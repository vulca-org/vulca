"""Palette-coded visual task masks.

This is the first Vision-Banana-style bridge in Vulca: ask an image provider
to render a flat RGB ownership image, then decode those colors into normal
Vulca RGBA layers.
"""
from __future__ import annotations

import base64
import colorsys
import io
from pathlib import Path

import numpy as np
from PIL import Image

from vulca.layers.coarse_bucket import is_background
from vulca.layers.manifest import write_manifest
from vulca.layers.mask import apply_mask_to_image
from vulca.layers.types import LayerInfo, LayerResult

DEFAULT_PALETTE: tuple[str, ...] = (
    "#ff0000",
    "#00ff00",
    "#0000ff",
    "#ffff00",
    "#ff00ff",
    "#00ffff",
    "#ff8000",
    "#8000ff",
    "#0080ff",
    "#80ff00",
    "#ff0080",
    "#00ff80",
)
BACKGROUND_COLOR = "#000000"


def build_palette_mask_prompt(
    layers: list[LayerInfo],
    *,
    palette: dict[str, str] | None = None,
) -> tuple[str, dict[str, str]]:
    """Build a provider prompt and resolved layer-name -> hex palette map."""
    resolved = _resolve_palette(layers, palette)
    entries = "\n".join(
        f"- {info.name}: {resolved[info.name]} = {info.description or info.name}"
        for info in sorted(layers, key=lambda item: item.z_index, reverse=True)
    )
    prompt = (
        "Create a pure flat RGB palette mask for the provided image.\n"
        "Do not generate a normal image, realistic image, shaded image, or textured image.\n"
        "Every output pixel must be one of the exact colors listed below.\n"
        "Use hard boundaries. Do not use gradients, shadows, labels, text, anti-aliased outlines, or extra colors.\n"
        "The output must match the input image dimensions and composition.\n\n"
        "Palette ownership map:\n"
        f"{entries}\n\n"
        "If a pixel does not belong to a listed foreground target, use the background color."
    )
    return prompt, resolved


def decode_palette_mask(
    mask_image: Image.Image,
    layers: list[LayerInfo],
    *,
    palette: dict[str, str] | None = None,
    tolerance: int = 48,
) -> dict[str, Image.Image]:
    """Decode an RGB palette mask into per-layer grayscale masks.

    Pixels are assigned to the nearest palette color when within `tolerance`.
    Out-of-tolerance pixels fall back to the background layer when present.
    """
    if not layers:
        return {}

    resolved = _resolve_palette(layers, palette)
    ordered = list(layers)
    colors = np.array([_hex_to_rgb(resolved[info.name]) for info in ordered], dtype=np.float32)
    rgb = np.array(mask_image.convert("RGB"), dtype=np.float32)

    diff = rgb[:, :, None, :] - colors[None, None, :, :]
    distances = np.sqrt(np.sum(diff * diff, axis=3))
    nearest = np.argmin(distances, axis=2)
    nearest_distance = np.min(distances, axis=2)
    within = nearest_distance <= float(tolerance)

    background_index = next(
        (idx for idx, info in enumerate(ordered) if is_background(info.content_type)),
        None,
    )

    masks: dict[str, Image.Image] = {}
    for idx, info in enumerate(ordered):
        mask = (nearest == idx) & within
        if background_index is not None and idx == background_index:
            mask = mask | ~within
        masks[info.id] = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    return masks


async def split_palette(
    image_path: str,
    layers: list[LayerInfo],
    *,
    output_dir: str,
    provider: str = "nb2",
    api_key: str = "",
    palette: dict[str, str] | None = None,
    tolerance: int = 48,
) -> list[LayerResult]:
    """Split an image into layers using a provider-generated palette mask."""
    from vulca.providers import get_image_provider

    source = Image.open(image_path).convert("RGB")
    width, height = source.size
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prompt, resolved_palette = build_palette_mask_prompt(layers, palette=palette)
    ref_b64 = base64.b64encode(Path(image_path).read_bytes()).decode()
    img_provider = get_image_provider(provider, api_key=api_key)
    result = await img_provider.generate(
        prompt,
        reference_image_b64=ref_b64,
        raw_prompt=True,
        width=width,
        height=height,
    )
    raw = base64.b64decode(result.image_b64)
    if getattr(result, "mime", "") and "svg" in result.mime:
        raise ValueError("palette mask provider returned SVG; expected raster image")

    palette_img = Image.open(io.BytesIO(raw)).convert("RGB")
    if palette_img.size != (width, height):
        palette_img = palette_img.resize((width, height), Image.NEAREST)
    palette_img.save(out_dir / "palette_mask.png")

    masks = decode_palette_mask(
        palette_img,
        layers,
        palette=resolved_palette,
        tolerance=tolerance,
    )

    results: list[LayerResult] = []
    warnings: list[str] = []
    canvas_px = float(width * height) if width and height else 1.0
    for info in sorted(layers, key=lambda item: item.z_index):
        mask = masks.get(info.id) or Image.new("L", (width, height), 0)
        mask_arr = np.array(mask)
        visible_px = int((mask_arr > 127).sum())
        info.area_pct = 100.0 * visible_px / canvas_px
        info.quality_status = "detected" if visible_px else "missed"
        info.dominant_colors = [resolved_palette[info.name]]
        if not visible_px:
            warnings.append(f"palette mask produced empty layer: {info.name}")
        layer_img = apply_mask_to_image(source, mask)
        out_path = out_dir / f"{info.name}.png"
        layer_img.save(out_path)
        results.append(LayerResult(info=info, image_path=str(out_path)))

    write_manifest(
        layers,
        output_dir=output_dir,
        width=width,
        height=height,
        source_image=image_path,
        split_mode="palette",
        generation_path="palette_mask.png",
        partial=bool(warnings),
        warnings=warnings,
    )
    return results


def _resolve_palette(
    layers: list[LayerInfo],
    palette: dict[str, str] | None,
) -> dict[str, str]:
    supplied = palette or {}
    resolved: dict[str, str] = {}
    foreground_idx = 0
    for info in sorted(layers, key=lambda item: item.z_index, reverse=True):
        if info.name in supplied:
            resolved[info.name] = _normalize_hex(supplied[info.name])
            continue
        if is_background(info.content_type):
            resolved[info.name] = BACKGROUND_COLOR
            continue
        if foreground_idx < len(DEFAULT_PALETTE):
            resolved[info.name] = DEFAULT_PALETTE[foreground_idx]
        else:
            resolved[info.name] = _generated_color(foreground_idx)
        foreground_idx += 1
    return resolved


def _normalize_hex(value: str) -> str:
    value = value.strip().lower()
    if not value.startswith("#"):
        value = "#" + value
    if len(value) == 4:
        value = "#" + "".join(ch * 2 for ch in value[1:])
    if len(value) != 7:
        raise ValueError(f"invalid palette color {value!r}; expected #RRGGBB")
    _hex_to_rgb(value)
    return value


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = _normalize_hex_no_validate(value)
    return (
        int(value[1:3], 16),
        int(value[3:5], 16),
        int(value[5:7], 16),
    )


def _normalize_hex_no_validate(value: str) -> str:
    value = value.strip().lower()
    if not value.startswith("#"):
        value = "#" + value
    if len(value) == 4:
        value = "#" + "".join(ch * 2 for ch in value[1:])
    if len(value) != 7:
        raise ValueError(f"invalid palette color {value!r}; expected #RRGGBB")
    int(value[1:], 16)
    return value


def _generated_color(index: int) -> str:
    hue = (index * 0.61803398875) % 1.0
    red, green, blue = colorsys.hsv_to_rgb(hue, 0.85, 1.0)
    return f"#{int(red * 255):02x}{int(green * 255):02x}{int(blue * 255):02x}"
