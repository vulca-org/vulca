"""Single-layer and multi-layer merge+redraw via img2img."""
from __future__ import annotations

import base64
import json
import logging
import os
import tempfile
from pathlib import Path

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork

logger = logging.getLogger("vulca.layers")


def _build_redraw_prompt(
    instruction: str,
    descriptions: list[str],
    *,
    tradition: str = "default",
    canvas_size: str = "",
) -> str:
    """Build img2img redraw prompt from instruction + layer descriptions."""
    parts = [instruction.strip()]
    if descriptions:
        parts.append("Layer context: " + "; ".join(d for d in descriptions if d))
    parts.append("Generate a complete image filling the entire canvas. Do NOT include any checkerboard pattern, grid, or transparency indicators — output a fully painted image.")
    if canvas_size:
        parts.append(f"Canvas size: {canvas_size}.")
    if tradition and tradition != "default":
        parts.append(f"Maintain the {tradition.replace('_', ' ')} cultural tradition and technique.")
    return "\n".join(parts)


async def redraw_layer(
    artwork: LayeredArtwork,
    *,
    layer_name: str,
    instruction: str,
    provider: str = "gemini",
    tradition: str = "default",
    api_key: str = "",
    artwork_dir: str,
) -> LayerResult:
    """Redraw a single layer via img2img.

    Finds the target layer by name, uses its existing image as the reference,
    generates a new image, saves it to {artwork_dir}/{layer_name}.png,
    and updates the LayerResult in place.
    """
    from vulca.providers import get_image_provider

    # 1. Find target layer
    target: LayerResult | None = None
    for lr in artwork.layers:
        if lr.info.name == layer_name:
            target = lr
            break
    if target is None:
        raise ValueError(f"Layer {layer_name!r} not found in artwork (available: {[l.info.name for l in artwork.layers]})")

    # 2. Build prompt
    prompt = _build_redraw_prompt(
        instruction,
        [target.info.description],
        tradition=tradition,
    )

    # 3. Encode reference image
    ref_path = Path(target.image_path)
    ref_b64 = base64.b64encode(ref_path.read_bytes()).decode()

    # 4. Call image provider
    img_provider = get_image_provider(
        provider,
        api_key=api_key or os.environ.get("GOOGLE_API_KEY", ""),
    )
    result = await img_provider.generate(
        prompt,
        tradition=tradition,
        reference_image_b64=ref_b64,
    )

    # 5. Save output as RGBA PNG (match canvas size from manifest)
    manifest_data = json.loads((Path(artwork_dir) / "manifest.json").read_text())
    canvas_w = manifest_data.get("width", 1024)
    canvas_h = manifest_data.get("height", 1024)
    out_path = Path(artwork_dir) / f"{layer_name}.png"
    _save_as_rgba(result.image_b64, result.mime, out_path, width=canvas_w, height=canvas_h)

    # 5b. Apply alpha mask from source image if available (hybrid: Gemini content + extract alpha)
    source_img_name = manifest_data.get("source_image", "")
    if source_img_name and target.info.dominant_colors:
        source_path = Path(artwork_dir) / source_img_name
        if not source_path.exists():
            source_path = Path(artwork_dir).parent / source_img_name
        if source_path.exists():
            from vulca.layers.mask import build_color_mask
            from PIL import Image as _PIL
            source_img = _PIL.open(str(source_path))
            gen_img = _PIL.open(str(out_path))
            mask = build_color_mask(source_img, target.info, tolerance=30)
            r, g, b, _ = gen_img.convert("RGBA").split()
            hybrid = _PIL.merge("RGBA", (r, g, b, mask))
            hybrid.save(str(out_path))

    # 6. Update target and return
    target.image_path = str(out_path)
    return target


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

    # 1. Find selected layers (preserve order by z_index)
    name_set = set(layer_names)
    selected: list[LayerResult] = [lr for lr in artwork.layers if lr.info.name in name_set]
    found_names = {lr.info.name for lr in selected}
    missing = name_set - found_names
    if missing:
        raise ValueError(
            f"Layers not found in artwork: {sorted(missing)} "
            f"(available: {[l.info.name for l in artwork.layers]})"
        )

    # 2. Read manifest for canvas dimensions
    manifest_path = Path(artwork_dir) / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    width = manifest.get("width", 1024)
    height = manifest.get("height", 1024)

    # 3. Composite selected layers into temp file
    merged_img = blend_layers(selected, width=width, height=height)
    tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    try:
        merged_img.save(tmp_file.name)
        tmp_file.close()
        ref_b64 = base64.b64encode(Path(tmp_file.name).read_bytes()).decode()

        # 4. Build prompt
        descriptions = [lr.info.description for lr in selected]
        prompt = _build_redraw_prompt(
            instruction,
            descriptions,
            tradition=tradition,
            canvas_size=f"{width}x{height}",
        )

        # 5. Call image provider
        img_provider = get_image_provider(
            provider,
            api_key=api_key or os.environ.get("GOOGLE_API_KEY", ""),
        )
        result = await img_provider.generate(
            prompt,
            tradition=tradition,
            reference_image_b64=ref_b64,
        )
    finally:
        # 6. Cleanup temp file
        try:
            Path(tmp_file.name).unlink(missing_ok=True)
        except Exception:
            pass

    # 7. Save output as RGBA PNG (match canvas size)
    out_path = Path(artwork_dir) / f"{merged_name}.png"
    _save_as_rgba(result.image_b64, result.mime, out_path, width=width, height=height)

    # 8. Create new LayerInfo with merged_name, min z_index, content_type="subject"
    min_z = min(lr.info.z_index for lr in selected)
    merged_info = LayerInfo(
        name=merged_name,
        description=f"Merged redraw of: {', '.join(layer_names)}",
        z_index=min_z,
        content_type="subject",
    )
    if not re_split:
        return LayerResult(info=merged_info, image_path=str(out_path))

    # Re-split: analyze the merged result and split into extract mode layers
    from vulca.layers.analyze import analyze_layers
    from vulca.layers.split import split_extract
    import shutil

    new_layers = await analyze_layers(str(out_path), api_key=api_key)
    resplit_dir = Path(artwork_dir) / f"_resplit_{merged_name}"
    results = split_extract(str(out_path), new_layers, output_dir=str(resplit_dir))

    # Move re-split layer files to artwork_dir
    final_results = []
    for r in results:
        dest = Path(artwork_dir) / Path(r.image_path).name
        if Path(r.image_path) != dest:
            shutil.move(str(r.image_path), str(dest))
        r.image_path = str(dest)
        final_results.append(r)

    # Cleanup temp dir and merged file
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
    """Decode image_b64, convert to RGBA, resize to canvas if needed, save as PNG."""
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
    # Ensure output matches canvas size (providers may return different sizes)
    if width and height and img.size != (width, height):
        img = img.resize((width, height), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), format="PNG")
