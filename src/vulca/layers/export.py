"""Export layered artwork to PSD and PNG directory (V2)."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from vulca.layers.types import LayerResult


def export_psd(
    layers: list[LayerResult],
    *,
    width: int = 1024,
    height: int = 1024,
    output_path: str,
) -> str:
    """Export layers as PNG directory with full-canvas layers + manifest.

    V2: Layers are already full-canvas, so no bbox expansion needed.
    If output_path ends in .psd, creates a PNG directory alongside it.
    If output_path is a directory (or no suffix), uses it directly.
    """
    out = Path(output_path)
    if out.suffix == ".psd":
        png_dir = out.with_suffix("")
    else:
        png_dir = out
    png_dir.mkdir(parents=True, exist_ok=True)

    sorted_layers = sorted(layers, key=lambda l: l.info.z_index)
    for layer in sorted_layers:
        try:
            img = Image.open(layer.image_path).convert("RGBA")
            # V2: layers should already be full-canvas
            # V1 compat: if they're not, expand using bbox if available
            if img.size != (width, height):
                if layer.info.bbox:
                    full = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                    x = int(width * layer.info.bbox["x"] / 100)
                    y = int(height * layer.info.bbox["y"] / 100)
                    full.paste(img, (x, y), img)
                    img = full
                else:
                    img = img.resize((width, height), Image.LANCZOS)
            dest = png_dir / f"{layer.info.z_index:02d}_{layer.info.name}.png"
            img.save(str(dest))
        except Exception:
            continue

    manifest = {
        "width": width,
        "height": height,
        "layers": [
            {
                "name": l.info.name,
                "description": l.info.description,
                "file": f"{l.info.z_index:02d}_{l.info.name}.png",
                "z_index": l.info.z_index,
                "blend_mode": l.info.blend_mode,
                "scores": l.scores,
            }
            for l in sorted_layers
        ],
    }
    manifest_path = png_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return str(out)
