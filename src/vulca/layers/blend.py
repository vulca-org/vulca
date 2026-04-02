"""Blend mode engine for VULCA layered artwork compositing."""
from __future__ import annotations

import numpy as np
from PIL import Image

from vulca.layers.types import LayerResult


def blend_normal(bottom: Image.Image, top: Image.Image) -> Image.Image:
    """Normal blend: alpha composite top over bottom."""
    bottom = bottom.convert("RGBA")
    top = top.convert("RGBA")
    result = bottom.copy()
    result.alpha_composite(top)
    return result


def blend_screen(bottom: Image.Image, top: Image.Image) -> Image.Image:
    """Screen blend: 1 - (1-a)(1-b). Respects top alpha."""
    bottom = bottom.convert("RGBA")
    top = top.convert("RGBA")

    bot = np.array(bottom, dtype=np.float32) / 255.0
    top_arr = np.array(top, dtype=np.float32) / 255.0

    bot_rgb = bot[..., :3]
    top_rgb = top_arr[..., :3]
    bot_alpha = bot[..., 3:4]
    top_alpha = top_arr[..., 3:4]

    # Screen formula per channel: 1 - (1-a)(1-b)
    screened = 1.0 - (1.0 - bot_rgb) * (1.0 - top_rgb)

    # Lerp between bottom and screened by top_alpha
    out_rgb = bot_rgb * (1.0 - top_alpha) + screened * top_alpha

    # Output alpha: out_alpha = bot_alpha + top_alpha * (1 - bot_alpha)
    out_alpha = bot_alpha + top_alpha * (1.0 - bot_alpha)

    out = np.concatenate([out_rgb, out_alpha], axis=-1)
    out = np.clip(out * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def blend_multiply(bottom: Image.Image, top: Image.Image) -> Image.Image:
    """Multiply blend: a*b/255. Respects top alpha."""
    bottom = bottom.convert("RGBA")
    top = top.convert("RGBA")

    bot = np.array(bottom, dtype=np.float32) / 255.0
    top_arr = np.array(top, dtype=np.float32) / 255.0

    bot_rgb = bot[..., :3]
    top_rgb = top_arr[..., :3]
    bot_alpha = bot[..., 3:4]
    top_alpha = top_arr[..., 3:4]

    # Multiply formula: a * b (in 0-1 range, equivalent to a*b/255 in 0-255 range)
    multiplied = bot_rgb * top_rgb

    # Lerp between bottom and multiplied by top_alpha
    out_rgb = bot_rgb * (1.0 - top_alpha) + multiplied * top_alpha

    # Output alpha: out_alpha = bot_alpha + top_alpha * (1 - bot_alpha)
    out_alpha = bot_alpha + top_alpha * (1.0 - bot_alpha)

    out = np.concatenate([out_rgb, out_alpha], axis=-1)
    out = np.clip(out * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def blend_layers(
    layers: list[LayerResult],
    *,
    width: int = 1024,
    height: int = 1024,
) -> Image.Image:
    """Composite layers with proper blend modes, sorted by z_index. Skips invisible layers."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    _BLEND_FNS = {
        "normal": blend_normal,
        "screen": blend_screen,
        "multiply": blend_multiply,
    }

    sorted_layers = sorted(layers, key=lambda l: l.info.z_index)
    for layer in sorted_layers:
        if not layer.info.visible:
            continue
        try:
            layer_img = Image.open(layer.image_path).convert("RGBA")
        except Exception:
            continue

        if layer_img.size != (width, height):
            layer_img = layer_img.resize((width, height), Image.LANCZOS)

        # For non-background layers with fully opaque alpha (RGB source),
        # convert near-white pixels to transparent so layers composite correctly.
        # This handles LAYERED pipeline output where each layer has white bg.
        if layer.info.content_type != "background":
            arr = np.array(layer_img)
            if arr[:, :, 3].min() > 250:  # fully opaque = was RGB
                white = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
                arr[:, :, 3][white] = 0
                layer_img = Image.fromarray(arr, "RGBA")

        blend_fn = _BLEND_FNS.get(layer.info.blend_mode, blend_normal)
        canvas = blend_fn(canvas, layer_img)

    return canvas
