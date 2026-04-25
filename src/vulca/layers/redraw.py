"""Single-layer and multi-layer merge+redraw via img2img.

v0.17.14 recontract (conservative — defaults unchanged for backward-compat):

- ``output_layer_name``: opt-in non-destructive write to a new layer file +
  manifest entry. Default empty → legacy in-place overwrite (will flip to
  ``"<layer>_redrawn"`` default in v0.18 after one release cycle).
- ``background_strategy``: how to flatten the alpha-sparse layer before
  sending to the provider. ``"transparent"`` (default, legacy) passes the
  RGBA layer through; ``"cream"`` / ``"white"`` / ``"sample_median"`` paste
  onto a flat RGB canvas to stop providers hallucinating new content where
  the layer is empty.
- ``preserve_alpha``: re-apply the source layer's alpha to the provider
  output. Default False (legacy).
- ``provider``-aware api_key: legacy code injected ``GOOGLE_API_KEY`` into
  every provider; v0.17.14 hands ``api_key=""`` to the provider when the
  caller did not specify one, letting each provider self-resolve its env
  var (OPENAI_API_KEY for openai, GOOGLE_API_KEY for gemini, …).
- Aspect-preserving fit replaces blanket LANCZOS warp on non-square canvases.
"""
from __future__ import annotations

import base64
import json
import logging
import tempfile
from pathlib import Path

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork

logger = logging.getLogger("vulca.layers")

CREAM_BG_RGB = (252, 248, 240)
WHITE_BG_RGB = (255, 255, 255)


def _build_redraw_prompt(
    instruction: str,
    descriptions: list[str],
    *,
    tradition: str = "default",
    canvas_size: str = "",
    background_strategy: str = "transparent",
) -> str:
    """Build img2img redraw prompt from instruction + layer descriptions.

    For non-transparent background_strategy we add a canvas-guard line that
    explicitly tells the provider the flat color is canvas, not subject —
    this stops gpt-image-2 from hallucinating buildings into empty regions
    of an alpha-sparse layer (γ Scottish iter 0 spire bug).
    """
    parts = [instruction.strip()]
    if descriptions:
        parts.append("Layer context: " + "; ".join(d for d in descriptions if d))
    if background_strategy != "transparent":
        parts.append(
            "The flat background is canvas — do NOT introduce new objects, "
            "scenes, or elements where the canvas is empty. Preserve the "
            "original spatial position and bounding box of the visible subject."
        )
    parts.append(
        "Generate a complete image filling the entire canvas. Do NOT include "
        "any checkerboard pattern, grid, or transparency indicators — output "
        "a fully painted image."
    )
    if canvas_size:
        parts.append(f"Canvas size: {canvas_size}.")
    if tradition and tradition != "default":
        parts.append(
            f"Maintain the {tradition.replace('_', ' ')} cultural tradition "
            "and technique."
        )
    return "\n".join(parts)


def _sample_median_bg(rgba_img) -> tuple[int, int, int]:
    """Pick a median-ish RGB from non-transparent pixels.

    Used by background_strategy="sample_median" so the flat canvas matches
    the dominant tone of the layer's actual pixels (e.g. cream parchment for
    a Scottish landscape, dark for a Goya).

    Fallback: when fewer than 0.1% of pixels meet the alpha>=32 visibility
    threshold (essentially fully-transparent layer), we log a warning and
    return CREAM. Codex 2026-04-25 review flagged the silent fallback as a
    "silent lie"; the warning is the agent's signal to inspect.
    """
    from PIL import Image

    rgba = rgba_img.convert("RGBA")
    pixels = list(rgba.getdata())
    visible = [(r, g, b) for r, g, b, a in pixels if a >= 32]
    if not visible:
        logger.warning(
            "redraw: sample_median found no visible pixels (alpha>=32) — "
            "falling back to cream background. Layer may be effectively "
            "transparent; consider background_strategy='cream' explicitly."
        )
        return CREAM_BG_RGB
    visible.sort()
    return visible[len(visible) // 2]


def _flatten_layer(
    src_rgba,
    *,
    background_strategy: str,
):
    """Return (flat_image, bg_rgb_or_None) per strategy."""
    from PIL import Image

    if background_strategy == "transparent":
        return src_rgba, None

    if background_strategy == "cream":
        bg = CREAM_BG_RGB
    elif background_strategy == "white":
        bg = WHITE_BG_RGB
    elif background_strategy == "sample_median":
        bg = _sample_median_bg(src_rgba)
    else:
        raise ValueError(
            f"unknown background_strategy={background_strategy!r}; "
            "expected one of transparent, cream, white, sample_median"
        )

    flat = Image.new("RGB", src_rgba.size, bg)
    flat.paste(src_rgba, (0, 0), src_rgba)  # alpha mask = src alpha
    return flat, bg


def _fit_into_canvas(out_img, target_size: tuple[int, int], bg_rgb):
    """Aspect-preserving fit. Letterboxes with bg_rgb (or transparent)."""
    from PIL import Image

    if out_img.size == target_size:
        return out_img

    tw, th = target_size
    sw, sh = out_img.size
    scale = min(tw / sw, th / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    resized = out_img.resize((nw, nh), Image.LANCZOS)

    if bg_rgb is None:
        canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
        if resized.mode != "RGBA":
            resized = resized.convert("RGBA")
    else:
        canvas = Image.new("RGB", target_size, bg_rgb)
        if resized.mode == "RGBA":
            resized = resized.convert("RGB")
    canvas.paste(resized, ((tw - nw) // 2, (th - nh) // 2))
    return canvas


def _add_or_replace_layer_in_manifest(
    artwork_dir: str,
    *,
    new_name: str,
    template: LayerInfo,
    description: str = "",
) -> int:
    """Append a new layer entry mirroring template's metadata.

    Used when output_layer_name diverges from the source layer name. If a
    layer of the same name already exists, it is replaced (idempotent).

    Returns the z_index assigned to the new layer so the caller's
    in-memory ``LayerResult`` agrees with what was just written to disk
    (P1.1 from 2026-04-25 review — disagreement caused the layer to
    silently move on the next ``load_manifest``).
    """
    from vulca.layers.manifest import load_manifest, write_manifest

    artwork = load_manifest(artwork_dir)
    layers = [lr.info for lr in artwork.layers if lr.info.name != new_name]
    new_z = max((l.z_index for l in layers), default=template.z_index) + 1

    new_info = LayerInfo(
        name=new_name,
        description=description or template.description,
        z_index=new_z,
        content_type=template.content_type,
        semantic_path=template.semantic_path,
        blend_mode=template.blend_mode,
        visible=True,
    )
    layers.append(new_info)

    manifest_path = Path(artwork_dir) / "manifest.json"
    manifest_data = json.loads(manifest_path.read_text())
    write_manifest(
        layers,
        output_dir=artwork_dir,
        width=manifest_data.get("width", 1024),
        height=manifest_data.get("height", 1024),
        source_image=manifest_data.get("source_image", ""),
        split_mode=manifest_data.get("split_mode", ""),
        generation_path=manifest_data.get("generation_path", ""),
        layerability=manifest_data.get("layerability", ""),
        partial=manifest_data.get("partial", False),
        warnings=manifest_data.get("warnings", []),
        tradition=manifest_data.get("tradition", ""),
    )
    return new_z


async def redraw_layer(
    artwork: LayeredArtwork,
    *,
    layer_name: str,
    instruction: str,
    provider: str = "gemini",
    tradition: str = "default",
    api_key: str = "",
    artwork_dir: str,
    output_layer_name: str = "",
    background_strategy: str = "transparent",
    preserve_alpha: bool = False,
) -> LayerResult:
    """Redraw a single layer via img2img.

    Default behavior preserves the legacy contract: writes back to the
    layer's existing file, transparent background, no alpha re-application.
    Pass ``output_layer_name`` to opt into non-destructive writes; pass
    ``background_strategy`` and ``preserve_alpha`` to opt into the
    hallucination-free path documented for the γ Scottish lanterns flow.
    """
    import os

    from PIL import Image

    from vulca.providers import get_image_provider

    # 1. Find target layer
    target: LayerResult | None = None
    for lr in artwork.layers:
        if lr.info.name == layer_name:
            target = lr
            break
    if target is None:
        raise ValueError(
            f"Layer {layer_name!r} not found in artwork "
            f"(available: {[l.info.name for l in artwork.layers]})"
        )

    if target.info.locked:
        raise ValueError(
            f"Layer {layer_name!r} is locked and cannot be redrawn "
            f"(likely a pipeline-synthesized layer like 'residual'). "
            f"Unlock it explicitly via layers_edit if you really mean to."
        )

    # 2. Read source layer + flatten per strategy
    src_path = Path(target.image_path)
    src_rgba = Image.open(str(src_path)).convert("RGBA")
    src_alpha = src_rgba.split()[-1]
    flat, bg_rgb = _flatten_layer(src_rgba, background_strategy=background_strategy)

    # 3. Build prompt
    canvas_size_hint = ""
    manifest_path = Path(artwork_dir) / "manifest.json"
    manifest_data = json.loads(manifest_path.read_text())
    canvas_w = manifest_data.get("width", src_rgba.width)
    canvas_h = manifest_data.get("height", src_rgba.height)
    if canvas_w and canvas_h:
        canvas_size_hint = f"{canvas_w}x{canvas_h}"
    prompt = _build_redraw_prompt(
        instruction,
        [target.info.description],
        tradition=tradition,
        canvas_size=canvas_size_hint,
        background_strategy=background_strategy,
    )

    # 4. Encode reference (flat for non-transparent, src_rgba for legacy)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fh:
        flat.save(fh.name, "PNG")
        ref_b64 = base64.b64encode(Path(fh.name).read_bytes()).decode()
    try:
        Path(fh.name).unlink(missing_ok=True)
    except Exception:
        pass

    # 5. Provider-aware api_key resolution. Bug fix: legacy code passed
    # GOOGLE_API_KEY to every provider. Now: if caller didn't specify a
    # key, hand "" to the provider so it self-resolves OPENAI_API_KEY /
    # GOOGLE_API_KEY / etc from its own __init__.
    img_provider = get_image_provider(provider, api_key=api_key)
    result = await img_provider.generate(
        prompt,
        tradition=tradition,
        reference_image_b64=ref_b64,
    )

    # 6. Decode + aspect-preserving fit (replaces blanket LANCZOS warp)
    raw = base64.b64decode(result.image_b64)
    if result.mime and "svg" in result.mime:
        # SVG fallback only — preserved for unusual mock branches
        out_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    else:
        import io as _io

        out_img = Image.open(_io.BytesIO(raw))

    out_img = _fit_into_canvas(out_img, (canvas_w, canvas_h), bg_rgb)
    rgba = out_img.convert("RGBA")

    # 7. Optionally re-apply original alpha
    if preserve_alpha:
        # Resize alpha to match if canvas resized (rare; manifest dims drive both)
        if src_alpha.size != rgba.size:
            src_alpha = src_alpha.resize(rgba.size, Image.LANCZOS)
        rgba.putalpha(src_alpha)

    # 8. Write — default in-place (legacy), opt-in new file
    if output_layer_name:
        out_name = output_layer_name
        out_path = Path(artwork_dir) / f"{out_name}.png"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        rgba.save(str(out_path), "PNG")

        # 8b. Hybrid alpha mask still applies for legacy `extract`-mode layers
        # whose dominant_colors are stored — keep behavior parity.
        _maybe_apply_legacy_color_mask(
            artwork_dir, manifest_data, target, out_path
        )

        # 8c. Manifest update: append (idempotent on rewrite). Capture the
        # assigned z_index so the in-memory LayerResult agrees with disk —
        # otherwise next load_manifest silently moves the layer (P1 finding,
        # 2026-04-25 review).
        assigned_z = target.info.z_index
        try:
            assigned_z = _add_or_replace_layer_in_manifest(
                artwork_dir,
                new_name=out_name,
                template=target.info,
                description=f"Redraw of {layer_name}: {instruction[:60]}",
            )
        except Exception as exc:
            logger.warning("redraw: manifest update failed (non-fatal): %s", exc)

        new_info = LayerInfo(
            name=out_name,
            description=target.info.description,
            z_index=assigned_z,
            content_type=target.info.content_type,
            semantic_path=target.info.semantic_path,
            blend_mode=target.info.blend_mode,
        )
        return LayerResult(info=new_info, image_path=str(out_path))

    # Legacy in-place path
    out_path = Path(artwork_dir) / f"{layer_name}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(str(out_path), "PNG")
    _maybe_apply_legacy_color_mask(artwork_dir, manifest_data, target, out_path)

    target.image_path = str(out_path)
    return target


def _maybe_apply_legacy_color_mask(
    artwork_dir: str, manifest_data: dict, target: LayerResult, out_path: Path
) -> None:
    """Hybrid alpha mask for legacy `extract`-mode layers (dominant_colors).

    Lifted verbatim from the old redraw_layer body so the legacy path stays
    bit-identical for backwards compatibility.
    """
    source_img_name = manifest_data.get("source_image", "")
    if not (source_img_name and target.info.dominant_colors):
        return
    source_path = Path(artwork_dir) / source_img_name
    if not source_path.exists():
        source_path = Path(artwork_dir).parent / source_img_name
    if not source_path.exists():
        return
    from PIL import Image as _PIL

    from vulca.layers.mask import build_color_mask

    source_img = _PIL.open(str(source_path))
    gen_img = _PIL.open(str(out_path))
    mask = build_color_mask(source_img, target.info, tolerance=30)
    r, g, b, _ = gen_img.convert("RGBA").split()
    hybrid = _PIL.merge("RGBA", (r, g, b, mask))
    hybrid.save(str(out_path))


async def redraw_merged(
    artwork: LayeredArtwork,
    *,
    layer_names: list[str],
    instruction: str,
    merged_name: str = "merged",
    provider: str = "gemini",
    tradition: str = "default",
    api_key: str = "",
    artwork_dir: str,
    re_split: bool = False,
) -> LayerResult | list[LayerResult]:
    """Merge selected layers, redraw via img2img, return as single new layer.

    Composites the selected layers into a temporary file, uses that as the
    img2img reference, generates a new image, and returns it as a LayerResult
    with name=merged_name and z_index=min of selected layers.
    """
    from vulca.layers.blend import blend_layers
    from vulca.providers import get_image_provider

    name_set = set(layer_names)
    selected: list[LayerResult] = [lr for lr in artwork.layers if lr.info.name in name_set]
    found_names = {lr.info.name for lr in selected}
    missing = name_set - found_names
    if missing:
        raise ValueError(
            f"Layers not found in artwork: {sorted(missing)} "
            f"(available: {[l.info.name for l in artwork.layers]})"
        )

    manifest_path = Path(artwork_dir) / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    width = manifest.get("width", 1024)
    height = manifest.get("height", 1024)

    merged_img = blend_layers(selected, width=width, height=height)
    tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    try:
        merged_img.save(tmp_file.name)
        tmp_file.close()
        ref_b64 = base64.b64encode(Path(tmp_file.name).read_bytes()).decode()

        descriptions = [lr.info.description for lr in selected]
        prompt = _build_redraw_prompt(
            instruction,
            descriptions,
            tradition=tradition,
            canvas_size=f"{width}x{height}",
        )

        # Provider-aware api_key (Patch 6 from spec, folded in)
        img_provider = get_image_provider(provider, api_key=api_key)
        result = await img_provider.generate(
            prompt,
            tradition=tradition,
            reference_image_b64=ref_b64,
        )
    finally:
        try:
            Path(tmp_file.name).unlink(missing_ok=True)
        except Exception:
            pass

    out_path = Path(artwork_dir) / f"{merged_name}.png"
    # Aspect-preserving fit (codex 2026-04-25 P2 — redraw_merged was using
    # blanket LANCZOS warp via _save_as_rgba, asymmetric with the new
    # redraw_layer fit logic). Letterbox transparent so merged result keeps
    # alpha-stack semantics for downstream composite.
    _save_as_rgba_fit(
        result.image_b64, result.mime, out_path,
        width=width, height=height,
    )

    min_z = min(lr.info.z_index for lr in selected)
    merged_info = LayerInfo(
        name=merged_name,
        description=f"Merged redraw of: {', '.join(layer_names)}",
        z_index=min_z,
        content_type="subject",
    )
    if not re_split:
        return LayerResult(info=merged_info, image_path=str(out_path))

    from vulca.layers.analyze import analyze_layers
    from vulca.layers.split import split_extract
    import shutil

    new_layers = await analyze_layers(str(out_path), api_key=api_key)
    resplit_dir = Path(artwork_dir) / f"_resplit_{merged_name}"
    results = split_extract(str(out_path), new_layers, output_dir=str(resplit_dir))

    final_results = []
    for r in results:
        dest = Path(artwork_dir) / Path(r.image_path).name
        if Path(r.image_path) != dest:
            shutil.move(str(r.image_path), str(dest))
        r.image_path = str(dest)
        final_results.append(r)

    shutil.rmtree(str(resplit_dir), ignore_errors=True)
    out_path.unlink(missing_ok=True)

    return final_results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _save_as_rgba(
    image_b64: str, mime: str, out_path: Path,
    *, width: int = 0, height: int = 0,
) -> None:
    """Decode image_b64, convert to RGBA, resize to canvas if needed, save as PNG.

    Legacy helper — uses LANCZOS warp on size mismatch. Kept for any
    out-of-tree callers; new code should use _save_as_rgba_fit which is
    aspect-preserving.
    """
    from PIL import Image
    import io

    raw = base64.b64decode(image_b64)

    if mime and "svg" in mime:
        # SVG from mock provider — create transparent placeholder at target size
        w = width or 100
        h = height or 100
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    else:
        img = Image.open(io.BytesIO(raw))

    img = img.convert("RGBA")
    if width and height and img.size != (width, height):
        img = img.resize((width, height), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), format="PNG")


def _save_as_rgba_fit(
    image_b64: str, mime: str, out_path: Path,
    *, width: int = 0, height: int = 0,
) -> None:
    """Aspect-preserving variant of _save_as_rgba — letterboxes with alpha=0
    when provider output's aspect differs from the canvas. Symmetric with
    redraw_layer's flow."""
    from PIL import Image
    import io

    raw = base64.b64decode(image_b64)

    if mime and "svg" in mime:
        w = width or 100
        h = height or 100
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    else:
        img = Image.open(io.BytesIO(raw))

    img = img.convert("RGBA")
    if width and height and img.size != (width, height):
        img = _fit_into_canvas(img, (width, height), bg_rgb=None)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), format="PNG")
