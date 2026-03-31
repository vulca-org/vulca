"""Tests for vulca.layers.composite V2 — delegates to blend_layers."""
from __future__ import annotations

import os
import tempfile

import pytest
from PIL import Image

from vulca.layers.composite import composite_layers  # direct import, bypasses __init__
from vulca.layers.types import LayerInfo, LayerResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save_tmp(img: Image.Image) -> str:
    """Save image to a temp file and return the path."""
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img.save(path)
    return path


def _make_layer(
    color: tuple[int, int, int, int],
    z_index: int,
    blend_mode: str = "normal",
    visible: bool = True,
    size: tuple[int, int] = (100, 100),
) -> LayerResult:
    img = Image.new("RGBA", size, color)
    path = _save_tmp(img)
    info = LayerInfo(
        name=f"layer_{z_index}",
        description="test layer",
        z_index=z_index,
        visible=visible,
        blend_mode=blend_mode,
    )
    return LayerResult(info=info, image_path=path)


def _make_layer_with_red_square(
    bg_color: tuple[int, int, int, int],
    z_index: int,
    size: tuple[int, int] = (100, 100),
) -> LayerResult:
    """Create a layer with a red square in the center (25-75) on a given background."""
    img = Image.new("RGBA", size, bg_color)
    # Draw a red square from 25-75 in both axes
    for y in range(25, 75):
        for x in range(25, 75):
            img.putpixel((x, y), (255, 0, 0, 255))
    path = _save_tmp(img)
    info = LayerInfo(
        name=f"layer_{z_index}",
        description="test layer with red square",
        z_index=z_index,
        visible=True,
        blend_mode="normal",
    )
    return LayerResult(info=info, image_path=path)


# ---------------------------------------------------------------------------
# TestCompositeV2
# ---------------------------------------------------------------------------

class TestCompositeV2:
    def test_normal_blend(self):
        """Full-canvas layers, blue bg + red square fg → red center, blue corner."""
        size = (100, 100)
        # BG layer: solid blue, fully opaque
        bg = _make_layer((0, 0, 255, 255), z_index=0, blend_mode="normal", size=size)
        # FG layer: transparent background with red square in center (25-75)
        fg = _make_layer_with_red_square((0, 0, 0, 0), z_index=1, size=size)

        layers = [bg, fg]
        result_path = ""
        # composite_layers returns path — pass no output_path, use blend_layers result indirectly
        # We need to check the composited result: save to a temp file
        fd, out_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        returned = composite_layers(layers, width=size[0], height=size[1], output_path=out_path)

        result = Image.open(out_path).convert("RGBA")

        # Center pixel (50, 50) should be red
        center = result.getpixel((50, 50))
        assert center[0] > 200, f"Center should be red (R>200), got {center}"
        assert center[2] < 50, f"Center should have low blue, got {center}"

        # Corner pixel (0, 0) should be blue (background showing through)
        corner = result.getpixel((0, 0))
        assert corner[2] > 200, f"Corner should be blue (B>200), got {corner}"
        assert corner[0] < 50, f"Corner should have low red, got {corner}"

    def test_screen_blend_brightens(self):
        """Screen layer brightens base (r > 50 when base=50, overlay=200)."""
        size = (4, 4)
        base_val = 50
        overlay_val = 200
        layers = [
            _make_layer((base_val, base_val, base_val, 255), z_index=0, blend_mode="normal", size=size),
            _make_layer((overlay_val, overlay_val, overlay_val, 255), z_index=1, blend_mode="screen", size=size),
        ]

        fd, out_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        composite_layers(layers, width=size[0], height=size[1], output_path=out_path)

        result = Image.open(out_path).convert("RGBA")
        r, g, b, a = result.getpixel((0, 0))
        assert r > base_val, f"Screen should brighten: expected r>{base_val}, got r={r}"

    def test_multiply_blend_darkens(self):
        """Multiply layer darkens base (r < 200 when base=200, shadow=100)."""
        size = (4, 4)
        base_val = 200
        shadow_val = 100
        layers = [
            _make_layer((base_val, base_val, base_val, 255), z_index=0, blend_mode="normal", size=size),
            _make_layer((shadow_val, shadow_val, shadow_val, 255), z_index=1, blend_mode="multiply", size=size),
        ]

        fd, out_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        composite_layers(layers, width=size[0], height=size[1], output_path=out_path)

        result = Image.open(out_path).convert("RGBA")
        r, g, b, a = result.getpixel((0, 0))
        assert r < base_val, f"Multiply should darken: expected r<{base_val}, got r={r}"

    def test_invisible_layer_skipped(self):
        """visible=False layer not composited → background shows through."""
        size = (4, 4)
        layers = [
            _make_layer((255, 0, 0, 255), z_index=0, blend_mode="normal", size=size),   # red base
            _make_layer((0, 0, 255, 255), z_index=1, blend_mode="normal", visible=False, size=size),  # blue hidden
        ]

        fd, out_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        composite_layers(layers, width=size[0], height=size[1], output_path=out_path)

        result = Image.open(out_path).convert("RGBA")
        r, g, b, a = result.getpixel((0, 0))
        assert r > 200, f"Invisible blue skipped — expected red background, got {(r, g, b, a)}"
        assert b < 10, f"Blue layer should be skipped, got {(r, g, b, a)}"

    def test_returns_output_path(self):
        """composite_layers returns the output_path string."""
        size = (4, 4)
        layers = [
            _make_layer((128, 128, 128, 255), z_index=0, size=size),
        ]

        fd, out_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        returned = composite_layers(layers, width=size[0], height=size[1], output_path=out_path)

        assert returned == out_path, f"Expected output_path returned, got {returned!r}"

    def test_empty_output_path_returns_empty_string(self):
        """When output_path is empty, returns empty string and does not crash."""
        size = (4, 4)
        layers = [
            _make_layer((128, 128, 128, 255), z_index=0, size=size),
        ]
        returned = composite_layers(layers, width=size[0], height=size[1])
        assert returned == "", f"Expected empty string, got {returned!r}"
