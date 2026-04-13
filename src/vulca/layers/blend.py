"""Blend mode engine for VULCA layered artwork compositing."""
from __future__ import annotations

import numpy as np
from PIL import Image

from vulca.layers.types import LayerResult
from vulca.layers.transform import needs_transform, apply_spatial_transform


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


def blend_overlay(bottom: Image.Image, top: Image.Image) -> Image.Image:
    """Overlay blend: combines multiply and screen based on base value."""
    bottom = bottom.convert("RGBA")
    top = top.convert("RGBA")
    bot = np.array(bottom, dtype=np.float32) / 255.0
    top_arr = np.array(top, dtype=np.float32) / 255.0
    bot_rgb, top_rgb = bot[..., :3], top_arr[..., :3]
    bot_alpha, top_alpha = bot[..., 3:4], top_arr[..., 3:4]
    low = 2.0 * bot_rgb * top_rgb
    high = 1.0 - 2.0 * (1.0 - bot_rgb) * (1.0 - top_rgb)
    overlaid = np.where(bot_rgb < 0.5, low, high)
    out_rgb = bot_rgb * (1.0 - top_alpha) + overlaid * top_alpha
    out_alpha = bot_alpha + top_alpha * (1.0 - bot_alpha)
    out = np.clip(np.concatenate([out_rgb, out_alpha], axis=-1) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def blend_soft_light(bottom: Image.Image, top: Image.Image) -> Image.Image:
    """Soft light blend: gentle contrast adjustment (Pegtop formula)."""
    bottom = bottom.convert("RGBA")
    top = top.convert("RGBA")
    bot = np.array(bottom, dtype=np.float32) / 255.0
    top_arr = np.array(top, dtype=np.float32) / 255.0
    bot_rgb, top_rgb = bot[..., :3], top_arr[..., :3]
    bot_alpha, top_alpha = bot[..., 3:4], top_arr[..., 3:4]
    soft = (1.0 - 2.0 * top_rgb) * bot_rgb * bot_rgb + 2.0 * top_rgb * bot_rgb
    out_rgb = bot_rgb * (1.0 - top_alpha) + soft * top_alpha
    out_alpha = bot_alpha + top_alpha * (1.0 - bot_alpha)
    out = np.clip(np.concatenate([out_rgb, out_alpha], axis=-1) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def blend_darken(bottom: Image.Image, top: Image.Image) -> Image.Image:
    """Darken blend: takes minimum of each channel."""
    bottom = bottom.convert("RGBA")
    top = top.convert("RGBA")
    bot = np.array(bottom, dtype=np.float32) / 255.0
    top_arr = np.array(top, dtype=np.float32) / 255.0
    bot_rgb, top_rgb = bot[..., :3], top_arr[..., :3]
    bot_alpha, top_alpha = bot[..., 3:4], top_arr[..., 3:4]
    darkened = np.minimum(bot_rgb, top_rgb)
    out_rgb = bot_rgb * (1.0 - top_alpha) + darkened * top_alpha
    out_alpha = bot_alpha + top_alpha * (1.0 - bot_alpha)
    out = np.clip(np.concatenate([out_rgb, out_alpha], axis=-1) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def blend_lighten(bottom: Image.Image, top: Image.Image) -> Image.Image:
    """Lighten blend: takes maximum of each channel."""
    bottom = bottom.convert("RGBA")
    top = top.convert("RGBA")
    bot = np.array(bottom, dtype=np.float32) / 255.0
    top_arr = np.array(top, dtype=np.float32) / 255.0
    bot_rgb, top_rgb = bot[..., :3], top_arr[..., :3]
    bot_alpha, top_alpha = bot[..., 3:4], top_arr[..., 3:4]
    lightened = np.maximum(bot_rgb, top_rgb)
    out_rgb = bot_rgb * (1.0 - top_alpha) + lightened * top_alpha
    out_alpha = bot_alpha + top_alpha * (1.0 - bot_alpha)
    out = np.clip(np.concatenate([out_rgb, out_alpha], axis=-1) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def blend_color_dodge(bottom: Image.Image, top: Image.Image) -> Image.Image:
    """Color dodge: brightens base by dividing by inverse of blend."""
    bottom = bottom.convert("RGBA")
    top = top.convert("RGBA")
    bot = np.array(bottom, dtype=np.float32) / 255.0
    top_arr = np.array(top, dtype=np.float32) / 255.0
    bot_rgb, top_rgb = bot[..., :3], top_arr[..., :3]
    bot_alpha, top_alpha = bot[..., 3:4], top_arr[..., 3:4]
    denom = np.maximum(1.0 - top_rgb, 1e-6)
    dodged = np.minimum(bot_rgb / denom, 1.0)
    out_rgb = bot_rgb * (1.0 - top_alpha) + dodged * top_alpha
    out_alpha = bot_alpha + top_alpha * (1.0 - bot_alpha)
    out = np.clip(np.concatenate([out_rgb, out_alpha], axis=-1) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def blend_color_burn(bottom: Image.Image, top: Image.Image) -> Image.Image:
    """Color burn: darkens base by dividing inverse by blend."""
    bottom = bottom.convert("RGBA")
    top = top.convert("RGBA")
    bot = np.array(bottom, dtype=np.float32) / 255.0
    top_arr = np.array(top, dtype=np.float32) / 255.0
    bot_rgb, top_rgb = bot[..., :3], top_arr[..., :3]
    bot_alpha, top_alpha = bot[..., 3:4], top_arr[..., 3:4]
    denom = np.maximum(top_rgb, 1e-6)
    burned = np.maximum(1.0 - (1.0 - bot_rgb) / denom, 0.0)
    out_rgb = bot_rgb * (1.0 - top_alpha) + burned * top_alpha
    out_alpha = bot_alpha + top_alpha * (1.0 - bot_alpha)
    out = np.clip(np.concatenate([out_rgb, out_alpha], axis=-1) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def blend_layers(
    layers: list[LayerResult],
    *,
    width: int = 1024,
    height: int = 1024,
) -> Image.Image:
    """Composite layers with proper blend modes, sorted by z_index. Skips invisible layers."""
    # Canvas starts as transparent white — identity for multiply (most common
    # non-normal blend). First visible layer forced to normal composite to avoid
    # white-out from screen/lighten/overlay on a white base.
    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    _first_visible = True

    _BLEND_FNS = {
        "normal": blend_normal,
        "screen": blend_screen,
        "multiply": blend_multiply,
        "overlay": blend_overlay,
        "soft_light": blend_soft_light,
        "darken": blend_darken,
        "lighten": blend_lighten,
        "color_dodge": blend_color_dodge,
        "color_burn": blend_color_burn,
    }

    sorted_layers = sorted(layers, key=lambda l: l.info.z_index)
    for layer in sorted_layers:
        if not layer.info.visible:
            continue
        try:
            layer_img = Image.open(layer.image_path).convert("RGBA")
        except Exception:
            continue

        # Apply spatial transform OR simple resize
        if needs_transform(layer.info):
            layer_img = apply_spatial_transform(
                layer_img, layer.info, canvas_width=width, canvas_height=height,
            )
        elif layer_img.size != (width, height):
            layer_img = layer_img.resize((width, height), Image.LANCZOS)

        # Apply layer opacity (v0.12)
        if layer.info.opacity < 1.0:
            alpha = layer_img.split()[3]
            alpha = alpha.point(lambda a: int(a * layer.info.opacity))
            layer_img.putalpha(alpha)

        if _first_visible:
            # Force normal composite for first layer — avoids white-out from
            # screen/lighten/overlay on the transparent white canvas.
            canvas = blend_normal(canvas, layer_img)
            _first_visible = False
        else:
            blend_fn = _BLEND_FNS.get(layer.info.blend_mode, blend_normal)
            canvas = blend_fn(canvas, layer_img)

    return canvas
