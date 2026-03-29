"""Split a flat image into alpha-channel layers."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from vulca.layers.types import LayerInfo


def crop_layer(image_path: str, info: LayerInfo, *, output_dir: str = "") -> str:
    """Crop a region from image based on percentage bbox, apply chromakey. Returns path to RGBA PNG."""
    img = Image.open(image_path)
    x = int(img.width * info.bbox["x"] / 100)
    y = int(img.height * info.bbox["y"] / 100)
    w = int(img.width * info.bbox["w"] / 100)
    h = int(img.height * info.bbox["h"] / 100)
    cropped = img.crop((x, y, x + w, y + h))

    # Apply chromakey based on layer's generation background color
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
    """Write manifest.json for split layers. Stores bbox as percentages."""
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
