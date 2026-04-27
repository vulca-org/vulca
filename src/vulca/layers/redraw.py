"""Single-layer and multi-layer merge+redraw via img2img.

v0.18.0 recontract (defaults flipped to safer values; ``in_place=True``
restores v0.17.x parity):

- ``output_layer_name``: explicit non-destructive output name. When empty
  (default) the result is auto-derived as ``f"{layer_name}_redrawn"``.
- ``background_strategy``: how to flatten the alpha-sparse layer before
  sending to the provider. ``"cream"`` (default) / ``"white"`` /
  ``"sample_median"`` paste onto a flat RGB canvas so providers don't
  hallucinate new content where the layer is empty. ``"transparent"``
  (legacy) passes the RGBA layer through.
- ``preserve_alpha``: re-apply the source layer's alpha to the provider
  output. Default ``True``.
- ``in_place``: legacy opt-out. When ``True`` the source layer's PNG is
  overwritten and no manifest entry is appended (v0.17.x parity).
- ``provider``-aware api_key: legacy code injected ``GOOGLE_API_KEY`` into
  every provider; we now hand ``api_key=""`` to the provider when the
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
from typing import Literal

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork

logger = logging.getLogger("vulca.layers")

CREAM_BG_RGB = (252, 248, 240)
WHITE_BG_RGB = (255, 255, 255)

# v0.20 mask-aware redraw routing
# spec: docs/superpowers/specs/2026-04-27-v0.20-mask-aware-redraw-routing-design.md
SPARSE_AREA_PCT_THRESHOLD = 5.0
SPARSE_BBOX_FILL_THRESHOLD = 0.5
INPAINT_PROMPT_PREFIX = (
    "Repaint the transparent region of the mask (where mask alpha=0) as: {instruction}. "
    "Leave the opaque region (mask alpha=255) bit-identical. "
    "Keep the same silhouette, placement, and scale as the underlying subject. "
    "Do not bleed color outside the mask boundary."
)


def _compute_sparsity(alpha) -> tuple[bool, float, float]:
    """Compute sparsity metrics from a layer's alpha channel.

    Returns ``(sparse, area_pct, bbox_fill)`` where ``sparse`` is true when
    either ``area_pct < 5%`` (single-region small subject like IMG_6847
    flower_cluster_c) or ``bbox_fill < 0.5`` (multi-instance fragmented
    alpha like Scottish row-of-6-lanterns at 8% area).

    See spec B1 — "live alpha, not manifest area_pct" — manifest's persisted
    area_pct can be wrong (Scottish NOTES.md:116-125 documents the case).
    """
    import numpy as np

    arr = np.array(alpha)
    if arr.ndim != 2:
        raise ValueError(
            f"_compute_sparsity expected 2D alpha band; got shape {arr.shape}"
        )
    visible_px = int((arr > 0).sum())
    total_px = int(arr.size)
    if total_px == 0:
        return False, 0.0, 0.0
    area_pct = 100.0 * visible_px / total_px

    # True bounding box (min/max indices) — NOT "populated rows × populated
    # cols" which under-estimates the bbox dramatically for multi-instance
    # spread layouts (e.g. blobs at corners). Empty rows/cols between
    # subjects must count toward the bbox so that bbox_fill reflects
    # spatial sparsity, not just density-within-populated-strip.
    rows_any = (arr > 0).any(axis=1)
    cols_any = (arr > 0).any(axis=0)
    if rows_any.any() and cols_any.any():
        row_idx = np.where(rows_any)[0]
        col_idx = np.where(cols_any)[0]
        bbox_h = int(row_idx[-1] - row_idx[0] + 1)
        bbox_w = int(col_idx[-1] - col_idx[0] + 1)
    else:
        bbox_h = bbox_w = 0
    bbox_area = bbox_h * bbox_w
    bbox_fill = visible_px / bbox_area if bbox_area else 0.0
    sparse = (
        area_pct < SPARSE_AREA_PCT_THRESHOLD
        or bbox_fill < SPARSE_BBOX_FILL_THRESHOLD
    )
    return sparse, area_pct, bbox_fill


def _build_inpaint_mask(alpha):
    """Build an OpenAI-convention RGBA mask from a layer alpha channel.

    OpenAI ``/v1/images/edits`` reads the mask alpha channel: alpha=0 is the
    EDIT zone, alpha=255 is PRESERVE. For ``layers_redraw`` we want the
    SUBJECT (where layer alpha > 0) to be EDITED, and the empty zone
    (where layer alpha == 0) to be PRESERVED.

    Polarity invariant: after construction, ``mask.split()[-1]`` has value 0
    over subject pixels and 255 over empty pixels. The unit test
    ``test_mask_polarity_invariant`` pins this.

    Hard binary {0, 255} only — no GaussianBlur (intermediate alpha values
    are undefined behavior under OpenAI's mask convention).
    """
    from PIL import Image, ImageOps

    if alpha.mode != "L":
        alpha = alpha.convert("L")
    subject = alpha.point(lambda v: 255 if v > 0 else 0)
    edit_mask_channel = ImageOps.invert(subject)  # 0 where subject (edit), 255 where empty (preserve)
    mask = Image.new("RGBA", alpha.size, (0, 0, 0, 0))
    mask.putalpha(edit_mask_channel)
    return mask


def _pick_inpaint_size(w: int, h: int) -> tuple[int, int]:
    """Pick an OpenAI-supported edit size matching the layer's aspect.

    OpenAI ``/v1/images/edits`` accepts {1024×1024, 1024×1536, 1536×1024}
    (verified at openai_provider.py:410-415). Rather than letting the
    provider silently fall back to 1024×1024 on a mismatch, we pre-fit
    aspect-preserving so the model's output canvas matches the source.
    """
    if h == 0:
        return (1024, 1024)
    aspect = w / h
    if aspect > 1.3:
        return (1536, 1024)
    if aspect < 1.0 / 1.3:
        return (1024, 1536)
    return (1024, 1024)


def _build_inpaint_prompt(
    instruction: str,
    descriptions: list[str],
    *,
    tradition: str = "default",
) -> str:
    """Build the inpaint-route prompt — explicit alpha-channel reference.

    Spec B5 (reviewer round 2 corrected wording): the canonical phrasing
    "the masked subject pixels" was ambiguous given OpenAI's convention
    treats alpha=0 as the inpaint zone. This wording references the mask
    alpha channel directly.
    """
    parts = [INPAINT_PROMPT_PREFIX.format(instruction=instruction.strip())]
    layer_ctx = "; ".join(d for d in descriptions if d)
    if layer_ctx:
        parts.append("Layer context: " + layer_ctx)
    if tradition and tradition != "default":
        parts.append(
            f"Maintain the {tradition.replace('_', ' ')} cultural tradition "
            "and technique."
        )
    return "\n".join(parts)


async def _redraw_via_inpaint_mask(
    *,
    flat_img,
    src_alpha,
    canvas_size: tuple[int, int],
    instruction: str,
    provider_inst,
    tradition: str,
    target_description: str,
):
    """Mask-aware inpaint path for ``redraw_layer`` (v0.20).

    Returns the model's output as an RGBA image at the original canvas
    size. Caller is responsible for ``preserve_alpha`` re-application.

    Image+mask are downsampled aspect-preserving to a 1024-class API size
    (B8 — flower_cluster_c.png is 4032×3024 but ``/v1/images/edits``
    accepts only {1024,1024×1536,1536×1024}). The model's response is
    upsampled back to the canvas size via ``_fit_into_canvas`` so the
    caller's ``preserve_alpha`` re-application against the ORIGINAL
    canvas alpha works without size mismatch.
    """
    import base64
    import io as _io
    import tempfile

    from PIL import Image

    canvas_w, canvas_h = canvas_size
    api_w, api_h = _pick_inpaint_size(canvas_w, canvas_h)

    # Aspect-preserving resize of both image and mask to API size.
    flat_for_api = _fit_into_canvas(
        flat_img.convert("RGB"), (api_w, api_h), bg_rgb=CREAM_BG_RGB
    )
    mask_full = _build_inpaint_mask(src_alpha)
    mask_for_api = _fit_into_canvas(mask_full, (api_w, api_h), bg_rgb=None)

    # Persist to temp files — the provider's inpaint_with_mask reads paths,
    # not bytes (openai_provider.py:403-405).
    image_tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    mask_tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    try:
        flat_for_api.save(image_tmp.name, "PNG")
        image_tmp.close()
        mask_for_api.save(mask_tmp.name, "PNG")
        mask_tmp.close()

        prompt = _build_inpaint_prompt(
            instruction, [target_description], tradition=tradition
        )
        result = await provider_inst.inpaint_with_mask(
            image_path=image_tmp.name,
            mask_path=mask_tmp.name,
            prompt=prompt,
            tradition=tradition,
        )

        raw = base64.b64decode(result.image_b64)
        if result.mime and "svg" in result.mime:
            out_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        else:
            out_img = Image.open(_io.BytesIO(raw))

        # bg_rgb=CREAM_BG_RGB letterboxes any aspect-mismatched return
        # onto cream; preserve_alpha re-crop downstream means PRESERVE-zone
        # pixels (where mask alpha=255) are discarded regardless of letterbox
        # color. If gpt-image-2 ever starts returning RGBA on the edits
        # endpoint, switch to bg_rgb=None to pass through alpha (v0.21).
        out_img = _fit_into_canvas(out_img, (canvas_w, canvas_h), bg_rgb=CREAM_BG_RGB)
        return out_img.convert("RGBA"), result
    finally:
        for tmp in (image_tmp.name, mask_tmp.name):
            try:
                Path(tmp).unlink(missing_ok=True)
            except Exception:
                pass


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
    background_strategy: str = "cream",
    preserve_alpha: bool = True,
    in_place: bool = False,
    route: Literal["auto", "img2img", "inpaint"] = "auto",
) -> LayerResult:
    """Redraw a single layer via img2img or mask-aware inpaint (v0.20).

    Output path resolution (v0.18.0):
      - if ``in_place=True`` → overwrite the source layer's PNG (legacy parity)
      - elif ``output_layer_name`` is non-empty → write to ``<output_layer_name>.png``
      - else → write to ``<layer_name>_redrawn.png`` (new safe default)

    ``in_place=True`` takes precedence; ``output_layer_name`` is silently
    ignored when ``in_place=True``.

    Defaults preserve alpha (``preserve_alpha=True``) and use a cream
    background (``background_strategy="cream"``) so providers don't
    hallucinate scenes into the alpha-empty regions of sparse layers.
    To restore v0.17.x legacy behavior verbatim, pass
    ``in_place=True, background_strategy="transparent", preserve_alpha=False``.

    v0.20 routing (``route``):
      - ``"auto"`` (default): when the layer alpha is sparse (area_pct<5%
        OR bbox_fill<0.5) AND the provider implements ``inpaint_with_mask``,
        route through OpenAI's mask-aware ``/v1/images/edits`` so the model
        receives explicit "edit here, preserve there" guidance instead of
        unmasked img2img. Dense layers and providers without mask support
        stay on the legacy img2img path bit-identically.
      - ``"img2img"``: force the legacy unmasked path (v0.18.x parity).
        The ``background_strategy="cream"`` workaround is most useful here.
      - ``"inpaint"``: force the mask-aware path. Falls back to img2img
        with a warning if the provider lacks ``inpaint_with_mask``.

    On the inpaint path, ``background_strategy`` is honored only in the
    sense that it controls how ``flat`` is built (which is used as the
    inpaint base image); its semantic effect is reduced because the model
    is told via mask which pixels to actually edit. ``cream`` remains the
    recommended setting on inpaint so the visible-but-preserved subject
    pixels read coherently if the API ever returns content outside the
    mask zone.

    Spec: ``docs/superpowers/specs/2026-04-27-v0.20-mask-aware-redraw-routing-design.md``.
    """
    import numpy as np

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

    # v0.20 — degenerate empty-layer guard (spec C7). A layer with no
    # opaque pixels can't be redrawn coherently regardless of route.
    if int((np.array(src_alpha) > 0).sum()) == 0:
        raise ValueError(
            f"Layer {layer_name!r} has no visible pixels (alpha == 0 everywhere); "
            "cannot redraw an empty layer."
        )

    flat, bg_rgb = _flatten_layer(src_rgba, background_strategy=background_strategy)

    # 3. Build prompt + read canvas size
    canvas_size_hint = ""
    manifest_path = Path(artwork_dir) / "manifest.json"
    manifest_data = json.loads(manifest_path.read_text())
    canvas_w = manifest_data.get("width", src_rgba.width)
    canvas_h = manifest_data.get("height", src_rgba.height)
    if canvas_w and canvas_h:
        canvas_size_hint = f"{canvas_w}x{canvas_h}"

    # v0.20 mask-aware routing decision (spec B1+B4+B6).
    sparse, area_pct, bbox_fill = _compute_sparsity(src_alpha)
    img_provider = get_image_provider(provider, api_key=api_key)
    has_inpaint = hasattr(img_provider, "inpaint_with_mask")

    if route == "auto":
        chosen_route = "inpaint" if (sparse and has_inpaint) else "img2img"
    elif route == "inpaint":
        if not has_inpaint:
            logger.warning(
                "Provider %s lacks inpaint_with_mask; falling back to img2img.",
                type(img_provider).__name__,
            )
            chosen_route = "img2img"
        else:
            chosen_route = "inpaint"
    elif route == "img2img":
        chosen_route = "img2img"
    else:
        raise ValueError(
            f"Unknown route={route!r}; expected one of 'auto', 'img2img', 'inpaint'."
        )

    # Spec E — log-channel advisory in v0.20 (typed return advisory deferred to v0.21).
    logger.info(
        "[layers_redraw] layer=%s sparse=%s area_pct=%.2f bbox_fill=%.3f "
        "route_requested=%s route_chosen=%s provider=%s",
        layer_name, sparse, area_pct, bbox_fill,
        route, chosen_route, type(img_provider).__name__,
    )

    if chosen_route == "inpaint":
        # 4-5. Mask-aware inpaint path (B2 + B3 + B5 + B8 in spec).
        rgba_with_alpha, _result = await _redraw_via_inpaint_mask(
            flat_img=flat,
            src_alpha=src_alpha,
            canvas_size=(canvas_w, canvas_h),
            instruction=instruction,
            provider_inst=img_provider,
            tradition=tradition,
            target_description=target.info.description,
        )
        # _redraw_via_inpaint_mask returns RGBA at canvas size with the
        # model's (cream-bg) painted output but WITHOUT the source alpha
        # re-applied. Step 7 below handles preserve_alpha re-application.
        rgba = rgba_with_alpha
    else:
        # 4-5. Legacy img2img path — unchanged from v0.18 behavior.
        prompt = _build_redraw_prompt(
            instruction,
            [target.info.description],
            tradition=tradition,
            canvas_size=canvas_size_hint,
            background_strategy=background_strategy,
        )

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fh:
            flat.save(fh.name, "PNG")
            ref_b64 = base64.b64encode(Path(fh.name).read_bytes()).decode()
        try:
            Path(fh.name).unlink(missing_ok=True)
        except Exception:
            pass

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

    # 8. Decide output path (v0.18.0 3-way resolution).
    if in_place:
        out_name = layer_name
        out_path = Path(artwork_dir) / f"{layer_name}.png"
    elif output_layer_name:
        out_name = output_layer_name
        out_path = Path(artwork_dir) / f"{output_layer_name}.png"
    else:
        out_name = f"{layer_name}_redrawn"
        out_path = Path(artwork_dir) / f"{out_name}.png"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(str(out_path), "PNG")

    # v0.18.0: manifest update happens whenever the caller is NOT in legacy
    # in-place mode. Both the auto-derived else branch and the explicit
    # output_layer_name branch append to the manifest.
    non_destructive = not in_place

    # Hybrid alpha mask still applies for legacy `extract`-mode layers whose
    # dominant_colors are stored — keep behavior parity across all branches.
    _maybe_apply_legacy_color_mask(artwork_dir, manifest_data, target, out_path)

    # 9. Manifest update branch.
    #
    # Legacy in-place (``in_place=True``) mutates the source layer in place
    # and skips manifest mutation. Both the auto-derived else branch and the
    # explicit ``output_layer_name`` branch take the non-destructive path:
    # write a new file + append a manifest entry.
    if not non_destructive:
        # Legacy in-place: mutate target, no manifest changes.
        target.image_path = str(out_path)
        return target

    # Non-destructive (auto-derived ``<layer>_redrawn`` or explicit
    # ``output_layer_name``): append manifest entry. Capture the assigned
    # z_index so the in-memory LayerResult agrees with disk — otherwise next
    # load_manifest silently moves the layer (P1 finding, 2026-04-25 review).
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
