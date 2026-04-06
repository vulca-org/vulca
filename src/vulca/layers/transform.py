"""Spatial transform engine for VULCA layers (v0.12).

Transforms layers from their stored size to canvas position using
percentage-based coordinates: x, y, width, height (0-100% of canvas),
rotation in degrees.

Transform order: resize -> rotate -> position on canvas.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from vulca.layers.types import LayerInfo


def needs_transform(info: LayerInfo) -> bool:
    """Check if a layer needs spatial transformation (non-default values)."""
    return (
        info.x != 0.0
        or info.y != 0.0
        or info.width != 100.0
        or info.height != 100.0
        or info.rotation != 0.0
    )


def apply_spatial_transform(
    image: Image.Image,
    info: LayerInfo,
    canvas_width: int,
    canvas_height: int,
) -> Image.Image:
    """Apply spatial transform: resize -> rotate -> position on canvas.

    Args:
        image: Source layer image (any size).
        info: LayerInfo with x/y/width/height (percentage) and rotation.
        canvas_width: Target canvas width in pixels.
        canvas_height: Target canvas height in pixels.

    Returns:
        Full-canvas RGBA image with the layer positioned/scaled/rotated.
    """
    if not needs_transform(info):
        if image.size != (canvas_width, canvas_height):
            return image.resize((canvas_width, canvas_height), Image.LANCZOS)
        return image

    img = image.convert("RGBA")

    # 1. Resize to target dimensions
    target_w = max(1, int(canvas_width * info.width / 100.0))
    target_h = max(1, int(canvas_height * info.height / 100.0))
    img = img.resize((target_w, target_h), Image.LANCZOS)

    # 2. Rotate (expand=True to avoid clipping)
    pre_rotate_w, pre_rotate_h = img.size
    if info.rotation != 0.0:
        img = img.rotate(
            -info.rotation,
            expand=True,
            resample=Image.BICUBIC,
            fillcolor=(0, 0, 0, 0),
        )

    # 3. Position on full canvas — compensate for rotation expansion
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    offset_x = (img.width - pre_rotate_w) // 2
    offset_y = (img.height - pre_rotate_h) // 2
    paste_x = int(canvas_width * info.x / 100.0) - offset_x
    paste_y = int(canvas_height * info.y / 100.0) - offset_y
    canvas.paste(img, (paste_x, paste_y), img)

    return canvas


def compute_content_bbox(image: Image.Image) -> dict | None:
    """Compute bounding box of non-transparent content.

    Args:
        image: RGBA image.

    Returns:
        {"x": int, "y": int, "w": int, "h": int} in pixels, or None if fully transparent.
    """
    alpha = np.array(image.convert("RGBA").split()[3])
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)

    if not rows.any():
        return None

    y_min, y_max = int(np.where(rows)[0][0]), int(np.where(rows)[0][-1])
    x_min, x_max = int(np.where(cols)[0][0]), int(np.where(cols)[0][-1])

    return {"x": x_min, "y": y_min, "w": x_max - x_min + 1, "h": y_max - y_min + 1}
