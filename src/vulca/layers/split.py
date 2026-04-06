"""Split a flat image into alpha-channel layers.

Supports two modes:
  - split_extract  : color-range masking → full-canvas RGBA layers
  - split_regenerate: img2img per layer → full-canvas RGBA layers (async)

V1 compat functions (crop_layer, chromakey_white, chromakey_black,
write_manifest) are kept at the bottom for backward compatibility with
test_layers.py and any other callers that import write_manifest from here.
The V1 write_manifest writes version=1 JSON with bbox/bg_color fields.
For V2, split_extract/split_regenerate use manifest.write_manifest internally.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

import numpy as np
from PIL import Image

from vulca.layers.types import LayerInfo, LayerResult
from vulca.layers.mask import build_color_mask, apply_mask_to_image, validate_dominant_colors
from vulca.layers.manifest import write_manifest as _write_manifest_v2
from vulca.layers.prompt import build_regeneration_prompt


# ---------------------------------------------------------------------------
# V2 API — Extract mode (synchronous, color-range masking)
# ---------------------------------------------------------------------------

def split_extract(
    image_path: str,
    layers: list[LayerInfo],
    *,
    output_dir: str,
    tolerance: int = 30,
) -> list[LayerResult]:
    """Extract mode: color-range masking → full-canvas RGBA layers.

    For each LayerInfo, builds a color-range mask based on dominant_colors and
    content_type, applies it to the source image, and saves a full-canvas RGBA
    PNG to output_dir.

    Args:
        image_path: Path to the source image.
        layers: LayerInfo list describing the semantic layers.
        output_dir: Directory to write layer PNGs and manifest.json.
        tolerance: Color-distance tolerance for mask generation (default 30).

    Returns:
        List of LayerResult sorted by z_index ascending.
    """
    img = Image.open(image_path)
    w, h = img.size

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Validate VLM-guessed colors against actual pixels.
    # Only validate non-empty lists: empty dominant_colors means the VLM could not
    # identify this layer's colors, so the layer should produce a transparent mask.
    for info in layers:
        if info.dominant_colors:
            info.dominant_colors = validate_dominant_colors(img, info.dominant_colors)

    assigned = np.zeros((h, w), dtype=bool)

    # Phase 1: Assign pixels foreground-first (high z_index = priority).
    # This matches SAM mode semantics: foreground layers have exclusive claim
    # over pixels before background layers are processed.
    layer_masks: dict[str, Image.Image] = {}
    for info in sorted(layers, key=lambda l: l.z_index, reverse=True):
        mask = build_color_mask(img, info, tolerance=tolerance, assigned=assigned)
        mask_arr = np.array(mask)
        assigned |= (mask_arr > 127)
        layer_masks[info.id] = mask

    # Phase 2: Save layers in z_index ascending order (bottom to top).
    results: list[LayerResult] = []
    for info in sorted(layers, key=lambda l: l.z_index):
        mask = layer_masks[info.id]
        layer_img = apply_mask_to_image(img, mask)
        out_path = out_dir / f"{info.name}.png"
        layer_img.save(str(out_path))
        results.append(LayerResult(info=info, image_path=str(out_path)))

    _write_manifest_v2(layers, output_dir=output_dir, width=w, height=h, split_mode="extract")
    return sorted(results, key=lambda r: r.info.z_index)


# ---------------------------------------------------------------------------
# V2 API — Regenerate mode (async, img2img per layer)
# ---------------------------------------------------------------------------

async def split_regenerate(
    image_path: str,
    layers: list[LayerInfo],
    *,
    output_dir: str,
    provider: str = "gemini",
    tradition: str = "default",
    api_key: str = "",
) -> list[LayerResult]:
    """Regenerate mode: img2img per layer → full-canvas RGBA layers.

    Uses an image provider to regenerate each layer independently,
    using the source image as a reference.  The provider is called once per
    layer with a per-layer prompt built from LayerInfo.

    Args:
        image_path: Path to the source image (used as img2img reference).
        layers: LayerInfo list describing the semantic layers.
        output_dir: Directory to write layer PNGs and manifest.json.
        provider: Provider name — "gemini", "mock", "openai", etc.
        tradition: Cultural tradition name injected into generation prompts.
        api_key: API key forwarded to the provider (empty = env-var fallback).

    Returns:
        List of LayerResult sorted by z_index ascending.
    """
    from vulca.providers import get_image_provider

    img = Image.open(image_path)
    w, h = img.size

    ref_b64 = base64.b64encode(Path(image_path).read_bytes()).decode()

    img_provider = get_image_provider(provider, api_key=api_key)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Validate VLM-guessed colors against actual pixels (same as extract mode).
    for info in layers:
        if info.dominant_colors:
            info.dominant_colors = validate_dominant_colors(img, info.dominant_colors)

    results: list[LayerResult] = []
    sorted_layers = sorted(layers, key=lambda l: l.z_index)

    for info in sorted_layers:
        other_names = [li.name for li in sorted_layers if li.name != info.name]
        prompt = build_regeneration_prompt(
            info,
            width=w,
            height=h,
            tradition=tradition,
            other_layer_names=other_names,
        )

        image_result = await img_provider.generate(
            prompt,
            tradition=tradition,
            reference_image_b64=ref_b64,
            width=w,
            height=h,
        )

        # Decode the generated image
        import io
        raw_bytes = base64.b64decode(image_result.image_b64)
        mime = getattr(image_result, "mime", "") or ""
        if "svg" in mime:
            # SVG output (e.g. mock provider): create a transparent placeholder
            gen_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        else:
            gen_img = Image.open(io.BytesIO(raw_bytes))

        # Ensure RGBA and full-canvas size
        gen_img = gen_img.convert("RGBA")
        if gen_img.size != (w, h):
            gen_img = gen_img.resize((w, h), Image.LANCZOS)

        # Two-pass VLM mask: ask the same VLM to generate a BW alpha mask.
        # This replaces the broken hybrid approach (color mask from original
        # image applied to generated RGB, causing alpha/content mismatch).
        if info.content_type != "background":
            from vulca.layers.vlm_mask import generate_vlm_mask, apply_vlm_mask
            buf = io.BytesIO()
            gen_img.convert("RGB").save(buf, format="PNG")
            gen_b64 = base64.b64encode(buf.getvalue()).decode()
            vlm_mask_img = await generate_vlm_mask(gen_b64, provider_name=provider, api_key=api_key)
            if vlm_mask_img is not None:
                gen_img = apply_vlm_mask(gen_img, vlm_mask_img)
            elif info.dominant_colors:
                # Fallback to color mask if VLM mask fails
                mask = build_color_mask(gen_img, info, tolerance=30)
                r, g, b, _ = gen_img.split()
                gen_img = Image.merge("RGBA", (r, g, b, mask))

        out_path = out_dir / f"{info.name}.png"
        gen_img.save(str(out_path))
        results.append(LayerResult(info=info, image_path=str(out_path)))

    _write_manifest_v2(layers, output_dir=output_dir, width=w, height=h, split_mode="regenerate")
    return results


# ---------------------------------------------------------------------------
# V2 API — VLM mode (async, per-layer BW masks from VLM)
# ---------------------------------------------------------------------------

async def split_vlm(
    image_path: str,
    layers: list[LayerInfo],
    *,
    output_dir: str,
    provider: str = "gemini",
    api_key: str = "",
) -> list[LayerResult]:
    """VLM semantic split: per-layer BW masks from VLM.

    For each non-background layer, asks VLM to generate a black/white
    segmentation mask. Background layer gets ~assigned (everything unclaimed).
    Original image pixels preserved, only alpha changes.

    Args:
        image_path: Path to the source image.
        layers: LayerInfo list describing the semantic layers.
        output_dir: Directory to write layer PNGs and manifest.json.
        provider: Provider name — "gemini", "mock", "openai", etc.
        api_key: API key forwarded to the provider (empty = env-var fallback).

    Returns:
        List of LayerResult sorted by z_index ascending.
    """
    from vulca.providers import get_image_provider
    import io as _io  # noqa: F401 (used in helper)

    img = Image.open(image_path)
    w, h = img.size

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ref_b64 = base64.b64encode(Path(image_path).read_bytes()).decode()
    img_provider = get_image_provider(provider, api_key=api_key)

    assigned = np.zeros((h, w), dtype=bool)

    # Phase 1: Generate VLM masks foreground-first (high z_index = priority).
    layer_masks: dict[str, Image.Image] = {}
    for info in sorted(layers, key=lambda l: l.z_index, reverse=True):
        if info.content_type == "background":
            continue

        prompt = (
            f"Create a black and white segmentation mask for this image.\n"
            f"White (#FFFFFF) = ONLY the region matching: {info.description}\n"
            f"Black (#000000) = everything else.\n"
            f"Sharp precise edges. No gray gradients except at content boundaries."
        )

        mask_l = await _vlm_mask_for_layer(
            ref_b64, prompt, img_provider, info, img, w, h,
        )
        mask_arr = np.array(mask_l)
        mask_bool = mask_arr > 127
        exclusive = mask_bool & ~assigned
        assigned |= exclusive
        exclusive_mask = Image.fromarray((exclusive * 255).astype(np.uint8), mode="L")
        layer_masks[info.id] = exclusive_mask

    # Phase 2: Background gets everything unclaimed.
    for info in layers:
        if info.content_type == "background":
            bg_mask = Image.fromarray(((~assigned) * 255).astype(np.uint8), mode="L")
            layer_masks[info.id] = bg_mask

    # Phase 3: Apply masks and save (z_index ascending).
    results: list[LayerResult] = []
    for info in sorted(layers, key=lambda l: l.z_index):
        mask = layer_masks.get(info.id)
        if mask is None:
            mask = Image.new("L", (w, h), 0)
        layer_img = apply_mask_to_image(img, mask)
        out_path = out_dir / f"{info.name}.png"
        layer_img.save(str(out_path))
        results.append(LayerResult(info=info, image_path=str(out_path)))

    _write_manifest_v2(layers, output_dir=output_dir, width=w, height=h, split_mode="vlm")
    return sorted(results, key=lambda r: r.info.z_index)


async def _vlm_mask_for_layer(
    ref_b64: str,
    prompt: str,
    provider,
    info: LayerInfo,
    img: Image.Image,
    w: int,
    h: int,
) -> Image.Image:
    """Generate a VLM mask for one layer, with fallback to color mask.

    Args:
        ref_b64: Base64-encoded reference image.
        prompt: Per-layer segmentation prompt.
        provider: Image provider instance with .generate() async method.
        info: LayerInfo for the layer being masked.
        img: Original PIL Image (used for color-mask fallback).
        w: Image width.
        h: Image height.

    Returns:
        Grayscale PIL Image (mode "L") — never None.
    """
    import io as _io
    import logging
    try:
        result = await provider.generate(
            prompt,
            reference_image_b64=ref_b64,
            raw_prompt=True,
        )
        mask_b64 = result.image_b64 if hasattr(result, "image_b64") else result
        mask_img = Image.open(_io.BytesIO(base64.b64decode(mask_b64)))
        mask_l = mask_img.convert("L")
        if mask_l.size != (w, h):
            mask_l = mask_l.resize((w, h), Image.LANCZOS)
        mask_arr = np.array(mask_l)
        if mask_arr.std() < 10:
            logging.getLogger("vulca").warning(
                "VLM mask degenerate for layer %s (std=%.1f), fallback to color mask",
                info.name, mask_arr.std(),
            )
            return build_color_mask(img, info, tolerance=30)
        return mask_l
    except Exception:
        logging.getLogger("vulca").warning(
            "VLM mask failed for layer %s, fallback to color mask", info.name,
            exc_info=True,
        )
        return build_color_mask(img, info, tolerance=30)


# ---------------------------------------------------------------------------
# V1 compat — kept for backward compatibility (test_layers.py)
# ---------------------------------------------------------------------------

def crop_layer(image_path: str, info: LayerInfo, *, output_dir: str = "") -> str:
    """Crop a region from image based on percentage bbox, apply chromakey.

    V1 compat function.  Returns path to RGBA PNG (minimal crop size).
    """
    img = Image.open(image_path)
    x = int(img.width * info.bbox["x"] / 100)
    y = int(img.height * info.bbox["y"] / 100)
    cw = int(img.width * info.bbox["w"] / 100)
    ch = int(img.height * info.bbox["h"] / 100)
    cropped = img.crop((x, y, x + cw, y + ch))

    if info.bg_color == "white":
        cropped = chromakey_white(cropped)
    elif info.bg_color == "black":
        cropped = chromakey_black(cropped)
    else:
        cropped = cropped.convert("RGBA")

    out_dir = Path(output_dir) if output_dir else Path(image_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{info.name}.png"
    cropped.save(str(out_path))
    return str(out_path)


def chromakey_white(img: Image.Image, *, threshold: int = 30) -> Image.Image:
    """Remove white background, returning RGBA image with transparency."""
    rgba = img.convert("RGBA")
    data = rgba.getdata()
    new_data = []
    for r, g, b, a in data:
        if r > (255 - threshold) and g > (255 - threshold) and b > (255 - threshold):
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, a))
    rgba.putdata(new_data)
    return rgba


def chromakey_black(img: Image.Image, *, threshold: int = 30) -> Image.Image:
    """Remove black background for screen-blend layers."""
    rgba = img.convert("RGBA")
    data = rgba.getdata()
    new_data = []
    for r, g, b, a in data:
        if r < threshold and g < threshold and b < threshold:
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, a))
    rgba.putdata(new_data)
    return rgba


def write_manifest(
    layers: list[LayerInfo],
    *,
    output_dir: str,
    width: int,
    height: int,
) -> str:
    """V1 compat: write manifest.json (version=1) with bbox and bg_color.

    This function preserves the original V1 format used by test_layers.py and
    any callers that import write_manifest from split.py.  For V2 format, use
    vulca.layers.manifest.write_manifest() directly.
    """
    manifest = {
        "version": 1,
        "width": width,
        "height": height,
        "layers": [
            {
                "name": info.name,
                "description": info.description,
                "file": f"{info.name}.png",
                "bbox": info.bbox,
                "z_index": info.z_index,
                "blend_mode": info.blend_mode,
                "bg_color": info.bg_color,
            }
            for info in sorted(layers, key=lambda l: l.z_index)
        ],
    }
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return str(manifest_path)
