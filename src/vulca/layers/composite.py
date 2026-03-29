"""Composite layers into a single flat image."""
from __future__ import annotations

from PIL import Image

from vulca.layers.types import LayerResult


def composite_layers(
    layers: list[LayerResult],
    *,
    width: int = 1024,
    height: int = 1024,
    output_path: str = "",
) -> str:
    """Stack layers by z_index, pasting at bbox offset positions. Returns output path."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    sorted_layers = sorted(layers, key=lambda l: l.info.z_index)
    for layer in sorted_layers:
        try:
            layer_img = Image.open(layer.image_path).convert("RGBA")
            # Approach B: paste at bbox offset, no resize
            x = int(width * layer.info.bbox["x"] / 100)
            y = int(height * layer.info.bbox["y"] / 100)
            canvas.paste(layer_img, (x, y), layer_img)
        except Exception:
            continue

    if output_path:
        canvas.save(output_path)
    return output_path
