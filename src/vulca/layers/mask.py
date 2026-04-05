"""Color-range mask generation for extract/split mode."""
from __future__ import annotations

import numpy as np
from PIL import Image

from vulca.layers.types import LayerInfo


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' or '#RGB' to (R, G, B)."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (r, g, b)


def build_color_mask(
    image: Image.Image,
    info: LayerInfo,
    *,
    tolerance: int = 30,
    assigned: np.ndarray | None = None,
) -> Image.Image:
    """Build a grayscale mask (L mode) for a layer based on dominant_colors and content_type.

    White (255) = pixel belongs to this layer. Black (0) = does not belong.

    Args:
        image: Source PIL image (any mode).
        info: LayerInfo with dominant_colors (hex strings) and content_type.
        tolerance: Distance tolerance in RGB space (default 30).
        assigned: Optional boolean array (H x W) of already-claimed pixels.
            Pixels set to True are zeroed out in the output mask, ensuring
            exclusive ownership (matches SAM mode's existing pattern).

    Returns:
        PIL Image in mode "L" (uint8, 0-255).
    """
    rgb = np.array(image.convert("RGB"), dtype=np.float32)  # H x W x 3

    h, w = rgb.shape[:2]

    # Start with all-zero match array
    color_match = np.zeros((h, w), dtype=np.float32)

    for hex_color in info.dominant_colors:
        try:
            target = np.array(_hex_to_rgb(hex_color), dtype=np.float32)  # shape (3,)
        except (ValueError, IndexError):
            continue
        # Euclidean distance per pixel
        diff = rgb - target  # H x W x 3
        dist = np.sqrt(np.sum(diff ** 2, axis=2))  # H x W
        match = np.clip(1.0 - dist / (tolerance * 3), 0.0, 1.0)
        color_match = np.maximum(color_match, match)

    if info.content_type == "effect":
        # Convert to HSV to get saturation channel
        hsv = np.array(image.convert("RGB").convert("HSV"), dtype=np.float32)
        saturation = hsv[:, :, 1]  # S channel, 0-255
        # Low saturation = likely an effect (mist, glow, overlay)
        low_sat_match = np.clip(1.0 - saturation / 80.0, 0.0, 1.0)
        color_match = np.maximum(color_match, low_sat_match)

    # Exclude already-assigned pixels (exclusive ownership)
    if assigned is not None:
        color_match[assigned] = 0.0

    # Convert 0-1 float mask to 0-255 uint8
    mask_array = (color_match * 255).astype(np.uint8)
    return Image.fromarray(mask_array, mode="L")


def apply_mask_to_image(image: Image.Image, mask: Image.Image) -> Image.Image:
    """Apply grayscale mask to image, producing full-canvas RGBA.

    Args:
        image: Source PIL image (any mode).
        mask: Grayscale (L mode) mask — white = opaque, black = transparent.

    Returns:
        PIL Image in mode "RGBA" with mask applied as alpha channel.
    """
    rgba = image.convert("RGBA")
    # Replace alpha channel with the mask
    r, g, b, _ = rgba.split()
    mask_l = mask.convert("L")
    return Image.merge("RGBA", (r, g, b, mask_l))
