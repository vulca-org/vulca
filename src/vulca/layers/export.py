"""Export layered artwork to PSD and PNG directory."""
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
    """Export layers as PNG directory with full-canvas expanded layers + manifest.

    Each minimal crop is expanded to full canvas (width x height) with transparency,
    matching Photoshop's layer display behavior.

    PSD binary format is not yet supported. If output_path ends in .psd,
    creates a PNG directory alongside it.
    """
    out = Path(output_path)
    # Create PNG directory alongside .psd path (or use path directly)
    if out.suffix == ".psd":
        png_dir = out.with_suffix("")
    else:
        png_dir = out
    png_dir.mkdir(parents=True, exist_ok=True)

    sorted_layers = sorted(layers, key=lambda l: l.info.z_index)
    for layer in sorted_layers:
        try:
            img = Image.open(layer.image_path).convert("RGBA")
            # Approach B: expand minimal crop to full canvas for export
            full = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            x = int(width * layer.info.bbox["x"] / 100)
            y = int(height * layer.info.bbox["y"] / 100)
            full.paste(img, (x, y), img)
            dest = png_dir / f"{layer.info.z_index:02d}_{layer.info.name}.png"
            full.save(str(dest))
        except Exception:
            continue

    # Write manifest
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
                "bbox": l.info.bbox,
                "scores": l.scores,
            }
            for l in sorted_layers
        ],
    }
    manifest_path = png_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    return str(out)
