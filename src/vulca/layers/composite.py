"""Composite layers into a single flat image with proper blend modes (V2)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from vulca.layers.types import LayerResult
from vulca.layers.alpha import ensure_alpha
from vulca.layers.blend import blend_layers


def composite_layers(
    layers: list[LayerResult],
    *,
    width: int = 1024,
    height: int = 1024,
    output_path: str = "",
) -> str:
    """Composite full-canvas RGBA layers with blend mode support.

    Applies alpha extraction (ensure_alpha) to each layer before blending.
    Alpha extraction is alpha.py's job; blend is blend.py's job.
    This function orchestrates both.

    Returns output_path.
    """
    processed: list[LayerResult] = []
    for lr in layers:
        try:
            img = Image.open(lr.image_path)
        except Exception:
            processed.append(lr)
            continue

        if img.size != (width, height):
            img = img.resize((width, height), Image.LANCZOS)

        rgba = ensure_alpha(img, lr.info)
        rgba.save(lr.image_path)
        processed.append(lr)

    canvas = blend_layers(processed, width=width, height=height)
    if not output_path:
        # Default: write next to first layer file
        first = layers[0].image_path if layers else "composite.png"
        output_path = str(Path(first).parent / "composite.png")
    canvas.save(output_path)
    return output_path
