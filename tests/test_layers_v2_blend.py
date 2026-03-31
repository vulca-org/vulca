"""Tests for vulca.layers.blend — blend mode engine."""
from __future__ import annotations

import os
import tempfile

import numpy as np
import pytest
from PIL import Image

from vulca.layers.blend import blend_normal, blend_screen, blend_multiply, blend_layers
from vulca.layers.types import LayerInfo, LayerResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _solid(color: tuple[int, int, int, int], size: tuple[int, int] = (4, 4)) -> Image.Image:
    """Create a solid-color RGBA image."""
    img = Image.new("RGBA", size, color)
    return img


def _pixel(img: Image.Image, x: int = 0, y: int = 0) -> tuple[int, int, int, int]:
    """Return RGBA pixel at (x, y)."""
    return img.getpixel((x, y))


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
    size: tuple[int, int] = (4, 4),
) -> LayerResult:
    img = _solid(color, size)
    path = _save_tmp(img)
    info = LayerInfo(
        name=f"layer_{z_index}",
        description="test layer",
        z_index=z_index,
        visible=visible,
        blend_mode=blend_mode,
    )
    return LayerResult(info=info, image_path=path)


# ---------------------------------------------------------------------------
# TestBlendNormal
# ---------------------------------------------------------------------------

class TestBlendNormal:
    def test_opaque_top_replaces_bottom(self):
        """Opaque top should replace bottom — pixel is top color."""
        bottom = _solid((255, 0, 0, 255))   # red, fully opaque
        top = _solid((0, 0, 255, 255))       # blue, fully opaque
        result = blend_normal(bottom, top)
        r, g, b, a = _pixel(result)
        assert b > 200, f"Expected blue channel dominant, got {(r, g, b, a)}"
        assert r < 10, f"Expected red channel gone, got {(r, g, b, a)}"

    def test_transparent_top_shows_bottom(self):
        """Transparent top should leave bottom unchanged."""
        bottom = _solid((255, 0, 0, 255))   # red, fully opaque
        top = _solid((0, 0, 255, 0))         # blue, fully transparent
        result = blend_normal(bottom, top)
        r, g, b, a = _pixel(result)
        assert r > 200, f"Expected red channel dominant, got {(r, g, b, a)}"
        assert b < 10, f"Expected blue channel absent, got {(r, g, b, a)}"

    def test_half_alpha_blends(self):
        """Half-alpha top should produce a mid-range blend."""
        bottom = _solid((0, 0, 0, 255))     # black, fully opaque
        top = _solid((255, 255, 255, 128))  # white, half transparent
        result = blend_normal(bottom, top)
        r, g, b, a = _pixel(result)
        # Result should be mid-gray (not pure black nor pure white)
        assert 50 < r < 210, f"Expected mid-range blend, got {(r, g, b, a)}"


# ---------------------------------------------------------------------------
# TestBlendScreen
# ---------------------------------------------------------------------------

class TestBlendScreen:
    def test_screen_brightens(self):
        """Screen of two mid-range values should be brighter than either input."""
        val = 100
        bottom = _solid((val, val, val, 255))
        top = _solid((val, val, val, 255))
        result = blend_screen(bottom, top)
        r, g, b, a = _pixel(result)
        assert r > val, f"Screen should brighten: expected >{val}, got r={r}"

    def test_screen_black_is_identity(self):
        """Screen with black (0) overlay is identity — bottom unchanged."""
        bottom = _solid((150, 100, 80, 255))
        top = _solid((0, 0, 0, 255))
        result = blend_screen(bottom, top)
        r, g, b, a = _pixel(result)
        # With fully opaque black top, screen(x, 0) = 1 - (1-x)(1-0) = x
        assert abs(r - 150) <= 2, f"Expected r≈150, got {r}"
        assert abs(g - 100) <= 2, f"Expected g≈100, got {g}"
        assert abs(b - 80) <= 2, f"Expected b≈80, got {b}"

    def test_screen_transparent_top_leaves_bottom(self):
        """Transparent top should not alter bottom in screen mode."""
        bottom = _solid((120, 80, 60, 255))
        top = _solid((255, 255, 255, 0))   # fully transparent white
        result = blend_screen(bottom, top)
        r, g, b, a = _pixel(result)
        assert abs(r - 120) <= 2, f"Expected r≈120, got {r}"
        assert abs(g - 80) <= 2, f"Expected g≈80, got {g}"
        assert abs(b - 60) <= 2, f"Expected b≈60, got {b}"


# ---------------------------------------------------------------------------
# TestBlendMultiply
# ---------------------------------------------------------------------------

class TestBlendMultiply:
    def test_multiply_darkens(self):
        """Multiply of two mid-high values should be darker than either input."""
        val = 200
        bottom = _solid((val, val, val, 255))
        top = _solid((val, val, val, 255))
        result = blend_multiply(bottom, top)
        r, g, b, a = _pixel(result)
        assert r < val, f"Multiply should darken: expected <{val}, got r={r}"

    def test_multiply_white_is_identity(self):
        """Multiply with white (255) is identity — bottom unchanged."""
        bottom = _solid((100, 150, 200, 255))
        top = _solid((255, 255, 255, 255))
        result = blend_multiply(bottom, top)
        r, g, b, a = _pixel(result)
        assert abs(r - 100) <= 2, f"Expected r≈100, got {r}"
        assert abs(g - 150) <= 2, f"Expected g≈150, got {g}"
        assert abs(b - 200) <= 2, f"Expected b≈200, got {b}"

    def test_multiply_transparent_top_leaves_bottom(self):
        """Transparent top should not alter bottom in multiply mode."""
        bottom = _solid((100, 150, 200, 255))
        top = _solid((0, 0, 0, 0))   # fully transparent black
        result = blend_multiply(bottom, top)
        r, g, b, a = _pixel(result)
        assert abs(r - 100) <= 2, f"Expected r≈100, got {r}"
        assert abs(g - 150) <= 2, f"Expected g≈150, got {g}"
        assert abs(b - 200) <= 2, f"Expected b≈200, got {b}"


# ---------------------------------------------------------------------------
# TestBlendLayers
# ---------------------------------------------------------------------------

class TestBlendLayers:
    def test_stack_normal_layers_last_opaque_wins(self):
        """Stack 3 normal layers: last opaque (highest z_index) wins — pixel is blue."""
        size = (4, 4)
        layers = [
            _make_layer((255, 0, 0, 255), z_index=0, blend_mode="normal", size=size),  # red
            _make_layer((0, 255, 0, 255), z_index=1, blend_mode="normal", size=size),  # green
            _make_layer((0, 0, 255, 255), z_index=2, blend_mode="normal", size=size),  # blue
        ]
        result = blend_layers(layers, width=size[0], height=size[1])
        r, g, b, a = _pixel(result)
        assert b > 200, f"Expected blue (z_index=2) to win, got {(r, g, b, a)}"
        assert r < 10, f"Expected red gone, got {(r, g, b, a)}"
        assert g < 10, f"Expected green gone, got {(r, g, b, a)}"

    def test_invisible_layer_skipped(self):
        """Invisible layer should not affect the result."""
        size = (4, 4)
        layers = [
            _make_layer((255, 0, 0, 255), z_index=0, blend_mode="normal", size=size),   # red base
            _make_layer((0, 0, 255, 255), z_index=1, blend_mode="normal", visible=False, size=size),  # blue hidden
        ]
        result = blend_layers(layers, width=size[0], height=size[1])
        r, g, b, a = _pixel(result)
        assert r > 200, f"Expected red (invisible blue skipped), got {(r, g, b, a)}"
        assert b < 10, f"Expected blue absent, got {(r, g, b, a)}"

    def test_screen_layer_brightens(self):
        """Screen layer over dark base should result in a brighter pixel."""
        size = (4, 4)
        base_val = 80
        layers = [
            _make_layer((base_val, base_val, base_val, 255), z_index=0, blend_mode="normal", size=size),
            _make_layer((200, 200, 200, 255), z_index=1, blend_mode="screen", size=size),
        ]
        result = blend_layers(layers, width=size[0], height=size[1])
        r, g, b, a = _pixel(result)
        assert r > base_val, f"Screen overlay should brighten: expected >{base_val}, got r={r}"
