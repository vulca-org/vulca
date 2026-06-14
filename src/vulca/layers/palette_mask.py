"""Palette-coded visual task masks.

This is the first Vision-Banana-style bridge in Vulca: ask an image provider
to render a flat RGB ownership image, then decode those colors into normal
Vulca RGBA layers.
"""
from __future__ import annotations

import base64
import colorsys
import io
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

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


@dataclass
class PaletteDecodeLayerReport:
    layer_id: str
    name: str
    palette_color: str
    pixel_count: int
    area_pct: float
    bbox: dict[str, int] | None
    quality_status: str
    unmatched_pct: float
    warnings: list[str]


@dataclass
class PaletteDecodeReport:
    width: int
    height: int
    tolerance: int
    unmatched_pixel_count: int
    unmatched_pct: float
    background_layer_id: str | None
    warnings: list[str]
    layers: list[PaletteDecodeLayerReport]


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
    masks, _quantized, _report = quantize_palette_mask(
        mask_image,
        layers,
        palette=palette,
        tolerance=tolerance,
    )
    return masks


def quantize_palette_mask(
    mask_image: Image.Image,
    layers: list[LayerInfo],
    *,
    palette: dict[str, str] | None = None,
    tolerance: int = 48,
) -> tuple[dict[str, Image.Image], Image.Image, PaletteDecodeReport]:
    """Decode and re-render a palette mask with exact resolved palette colors."""
    width, height = mask_image.size
    if not layers:
        report = PaletteDecodeReport(
            width=width,
            height=height,
            tolerance=tolerance,
            unmatched_pixel_count=0,
            unmatched_pct=0.0,
            background_layer_id=None,
            warnings=[],
            layers=[],
        )
        return {}, Image.new("RGB", (width, height), BACKGROUND_COLOR), report

    resolved = _resolve_palette(layers, palette)
    ordered = list(layers)
    colors_u8 = np.array([_hex_to_rgb(resolved[info.name]) for info in ordered], dtype=np.uint8)
    colors = colors_u8.astype(np.float32)
    rgb_u8 = np.array(mask_image.convert("RGB"), dtype=np.uint8)
    rgb = rgb_u8.astype(np.float32)

    nearest = np.zeros((height, width), dtype=np.intp)
    nearest_distance_sq = np.full((height, width), np.inf, dtype=np.float32)
    for idx, color in enumerate(colors):
        diff = rgb - color
        distance_sq = np.sum(diff * diff, axis=2)
        closer = distance_sq < nearest_distance_sq
        nearest[closer] = idx
        nearest_distance_sq[closer] = distance_sq[closer]
    within = nearest_distance_sq <= float(tolerance * tolerance)

    background_index = next(
        (idx for idx, info in enumerate(ordered) if is_background(info.content_type)),
        None,
    )
    background_layer_id = ordered[background_index].id if background_index is not None else None

    assigned = nearest.copy()
    unmatched = ~within
    if background_index is not None:
        assigned[unmatched] = background_index
        unmatched = np.zeros_like(within, dtype=bool)

    quantized_arr = np.zeros_like(rgb_u8)
    masks: dict[str, Image.Image] = {}
    canvas_px = float(width * height) if width and height else 1.0
    unmatched_count = int(unmatched.sum())
    unmatched_pct = round(100.0 * unmatched_count / canvas_px, 4)
    warnings: list[str] = []
    if unmatched_count:
        warnings.append(
            f"palette mask left {unmatched_count} unmatched pixels without a background layer"
        )

    layer_reports: list[PaletteDecodeLayerReport] = []
    for idx, info in enumerate(ordered):
        mask = (assigned == idx) & ~unmatched
        quantized_arr[mask] = colors_u8[idx]
        pixel_count = int(mask.sum())
        area_pct = round(100.0 * pixel_count / canvas_px, 4)
        bbox = compute_mask_bbox(mask)
        quality_status = "detected" if pixel_count else "missed"
        layer_warnings: list[str] = []
        if not pixel_count:
            layer_warnings.append(f"palette mask produced empty layer: {info.name}")
            warnings.extend(layer_warnings)
        masks[info.id] = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
        layer_reports.append(
            PaletteDecodeLayerReport(
                layer_id=info.id,
                name=info.name,
                palette_color=resolved[info.name],
                pixel_count=pixel_count,
                area_pct=area_pct,
                bbox=bbox,
                quality_status=quality_status,
                unmatched_pct=unmatched_pct,
                warnings=layer_warnings,
            )
        )

    report = PaletteDecodeReport(
        width=width,
        height=height,
        tolerance=tolerance,
        unmatched_pixel_count=unmatched_count,
        unmatched_pct=unmatched_pct,
        background_layer_id=background_layer_id,
        warnings=warnings,
        layers=layer_reports,
    )
    return masks, Image.fromarray(quantized_arr, mode="RGB"), report


def compute_mask_bbox(mask: Image.Image | np.ndarray) -> dict[str, int] | None:
    """Return inclusive-pixel content bounds as x/y/w/h for non-empty masks."""
    if isinstance(mask, Image.Image):
        arr = np.array(mask.convert("L")) > 127
    else:
        arr = np.asarray(mask).astype(bool)
    if not arr.any():
        return None
    ys, xs = np.where(arr)
    x0 = int(xs.min())
    y0 = int(ys.min())
    x1 = int(xs.max())
    y1 = int(ys.max())
    return {"x": x0, "y": y0, "w": x1 - x0 + 1, "h": y1 - y0 + 1}


def write_decode_report(report: PaletteDecodeReport, output_path: str | Path) -> str:
    path = Path(output_path)
    path.write_text(json.dumps(asdict(report), indent=2))
    return str(path)


def write_palette_contact_sheet(
    *,
    source_image: Image.Image,
    raw_palette: Image.Image,
    quantized_palette: Image.Image,
    decoded_layers: list[tuple[str, Image.Image]],
    output_path: str | Path,
    tile_size: tuple[int, int] = (180, 135),
) -> str:
    """Write a compact visual audit sheet for source, masks, and decoded layers."""
    items: list[tuple[str, Image.Image]] = [
        ("source", source_image.convert("RGB")),
        ("raw palette", raw_palette.convert("RGB")),
        ("quantized palette", quantized_palette.convert("RGB")),
        *decoded_layers,
    ]
    if not items:
        raise ValueError("contact sheet requires at least one image")

    cols = min(4, len(items))
    rows = (len(items) + cols - 1) // cols
    pad = 10
    label_h = 20
    tile_w, tile_h = tile_size
    sheet = Image.new(
        "RGB",
        (cols * tile_w + (cols + 1) * pad, rows * (tile_h + label_h) + (rows + 1) * pad),
        (245, 245, 242),
    )
    draw = ImageDraw.Draw(sheet)
    for idx, (label, image) in enumerate(items):
        row = idx // cols
        col = idx % cols
        x = pad + col * (tile_w + pad)
        y = pad + row * (tile_h + label_h + pad)
        preview = _contact_sheet_preview(image)
        thumb = ImageOps.contain(preview, tile_size)
        tile = Image.new("RGB", tile_size, (255, 255, 255))
        tile.paste(thumb, ((tile_w - thumb.width) // 2, (tile_h - thumb.height) // 2))
        sheet.paste(tile, (x, y))
        draw.text((x, y + tile_h + 4), label[:32], fill=(30, 30, 30))

    path = Path(output_path)
    sheet.save(path)
    return str(path)


async def split_palette(
    image_path: str,
    layers: list[LayerInfo],
    *,
    output_dir: str,
    provider: str = "nb2",
    api_key: str = "",
    palette: dict[str, str] | None = None,
    tolerance: int = 48,
    write_debug_artifacts: bool = True,
    contact_sheet: bool = True,
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
        palette_img = palette_img.resize((width, height), Image.Resampling.NEAREST)
    palette_img.save(out_dir / "palette_mask.png")

    masks, quantized_img, decode_report = quantize_palette_mask(
        palette_img,
        layers,
        palette=resolved_palette,
        tolerance=tolerance,
    )
    if write_debug_artifacts:
        quantized_img.save(out_dir / "palette_mask_quantized.png")
        write_decode_report(decode_report, out_dir / "decode_report.json")

    results: list[LayerResult] = []
    report_by_id = {item.layer_id: item for item in decode_report.layers}
    decoded_previews: list[tuple[str, Image.Image]] = []
    for info in sorted(layers, key=lambda item: item.z_index):
        mask = masks.get(info.id) or Image.new("L", (width, height), 0)
        layer_report = report_by_id.get(info.id)
        if layer_report is not None:
            info.area_pct = layer_report.area_pct
            info.quality_status = layer_report.quality_status
            info.content_bbox = layer_report.bbox
            info.dominant_colors = [layer_report.palette_color]
        layer_img = apply_mask_to_image(source, mask)
        out_path = out_dir / f"{info.name}.png"
        layer_img.save(out_path)
        decoded_previews.append((info.name, layer_img))
        results.append(LayerResult(info=info, image_path=str(out_path)))

    if write_debug_artifacts and contact_sheet:
        write_palette_contact_sheet(
            source_image=source,
            raw_palette=palette_img,
            quantized_palette=quantized_img,
            decoded_layers=decoded_previews,
            output_path=out_dir / "contact_sheet.png",
        )

    write_manifest(
        layers,
        output_dir=output_dir,
        width=width,
        height=height,
        source_image=image_path,
        split_mode="palette",
        generation_path="palette_mask.png",
        partial=bool(decode_report.warnings),
        warnings=decode_report.warnings,
    )
    return results


def _contact_sheet_preview(image: Image.Image) -> Image.Image:
    if image.mode != "RGBA":
        return image.convert("RGB")
    background = Image.new("RGB", image.size, (255, 255, 255))
    background.paste(image, mask=image.getchannel("A"))
    return background


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
