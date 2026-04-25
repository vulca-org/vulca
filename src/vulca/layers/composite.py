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
    force_alpha_writeback: bool = False,
) -> str:
    """Composite full-canvas RGBA layers with blend mode support.

    blend_layers() already reads each layer's RGBA from disk and applies the
    correct blend mode, so for the modern flow this is enough. Alpha
    extraction (ensure_alpha) is only needed for legacy extract-mode layers
    that store dominant_colors and rely on chroma keying at composite time.

    v0.17.14: pre-patch behavior unconditionally ran ``ensure_alpha`` and
    wrote the result back to each ``lr.image_path``, mutating source layers
    as a side-effect of a nominally read-only preview call (codex finding,
    2026-04-25 review). Default behavior is now non-destructive — pass
    ``force_alpha_writeback=True`` to opt back into the legacy in-place
    rewrite when callers actually want to persist alpha-extracted layers.

    Returns output_path.
    """
    if force_alpha_writeback:
        for lr in layers:
            try:
                img = Image.open(lr.image_path)
            except Exception:
                continue
            if img.size != (width, height):
                img = img.resize((width, height), Image.LANCZOS)
            rgba = ensure_alpha(img, lr.info)
            rgba.save(lr.image_path)

    canvas = blend_layers(layers, width=width, height=height)
    if not output_path:
        # Default: write next to first layer file
        first = layers[0].image_path if layers else "composite.png"
        output_path = str(Path(first).parent / "composite.png")
    canvas.save(output_path)
    return output_path
