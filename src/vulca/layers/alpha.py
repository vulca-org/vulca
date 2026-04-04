"""Alpha extraction for layer compositing — ML-based, not threshold-based."""
from __future__ import annotations

import numpy as np
from PIL import Image

from vulca.layers.types import LayerInfo

_BG_COLORS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "gray": (128, 128, 128),
    "green": (0, 255, 0),
}


def select_alpha_strategy(info: LayerInfo) -> str:
    """Select optimal alpha strategy based on layer content_type."""
    ct = info.content_type.lower()
    if ct == "background":
        return "opaque"
    elif ct in ("text", "line_art", "calligraphy", "seal"):
        return "chroma_or_threshold"
    elif ct in ("effect", "mist", "reflection", "glow", "atmosphere"):
        return "sam2_soft"
    else:
        return "rembg_cascade"


def chroma_key(
    image: Image.Image,
    key_color: tuple[int, int, int] = (255, 255, 255),
    tolerance: int = 30,
) -> Image.Image:
    """Remove solid-color background via chroma key.

    Default key_color is white (for LAYERED pipeline layers).
    """
    rgb = np.array(image.convert("RGB"), dtype=np.float32)
    target = np.array(key_color, dtype=np.float32)

    dist = np.sqrt(np.sum((rgb - target) ** 2, axis=2))
    alpha = np.clip((dist - tolerance) / tolerance, 0.0, 1.0)
    alpha = (alpha * 255).astype(np.uint8)

    r, g, b = image.convert("RGB").split()
    mask = Image.fromarray(alpha, mode="L")
    return Image.merge("RGBA", (r, g, b, mask))


def apply_alpha_to_layer(
    image: Image.Image,
    info: LayerInfo,
    method: str = "auto",
) -> Image.Image:
    """Apply alpha to a layer image based on strategy."""
    if method == "auto":
        method = select_alpha_strategy(info)

    if method == "opaque":
        return image.convert("RGBA")

    key = _BG_COLORS.get(info.bg_color, (255, 255, 255))

    if method == "chroma_or_threshold":
        return chroma_key(image, key_color=key)

    try:
        from rembg import remove
        rgba = remove(image)
        return rgba if rgba.mode == "RGBA" else rgba.convert("RGBA")
    except (ImportError, SystemExit, Exception):
        return chroma_key(image, key_color=key)


def ensure_alpha(image: Image.Image, info: LayerInfo) -> Image.Image:
    """Ensure a layer has correct alpha for compositing.

    Bridge between generation (RGB output) and blend (needs RGBA).
    - Background layers → fully opaque
    - Already has alpha → skip
    - Fully opaque RGB → ML-based alpha extraction
    """
    rgba = image.convert("RGBA")

    if info.content_type == "background":
        return rgba

    arr = np.array(rgba)
    if arr[:, :, 3].min() < 250:
        return rgba

    return apply_alpha_to_layer(image, info)
