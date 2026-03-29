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
    """Stack layers by z_index into a single image. Returns output path."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    sorted_layers = sorted(layers, key=lambda l: l.info.z_index)
    for layer in sorted_layers:
        try:
            layer_img = Image.open(layer.image_path).convert("RGBA")
            # Resize to canvas if needed
            if layer_img.size != (width, height):
                layer_img = layer_img.resize((width, height), Image.LANCZOS)
            canvas = Image.alpha_composite(canvas, layer_img)
        except Exception:
            continue

    if output_path:
        canvas.save(output_path)
    return output_path
