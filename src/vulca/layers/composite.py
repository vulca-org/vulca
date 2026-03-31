"""Composite layers into a single flat image with proper blend modes (V2)."""
from __future__ import annotations

from vulca.layers.types import LayerResult
from vulca.layers.blend import blend_layers


def composite_layers(
    layers: list[LayerResult],
    *,
    width: int = 1024,
    height: int = 1024,
    output_path: str = "",
) -> str:
    """Composite full-canvas RGBA layers with blend mode support.
    Returns output_path."""
    canvas = blend_layers(layers, width=width, height=height)
    if output_path:
        canvas.save(output_path)
    return output_path
