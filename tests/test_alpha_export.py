"""Tests for export-time alpha processing."""
import pytest
from PIL import Image

from vulca.layers.alpha import chroma_key, select_alpha_strategy
from vulca.layers.types import LayerInfo
from vulca.layers.alpha import ensure_alpha


class TestChromaKey:
    def test_green_background_removed(self):
        img = Image.new("RGB", (64, 64), (0, 255, 0))
        for x in range(20, 44):
            for y in range(20, 44):
                img.putpixel((x, y), (255, 0, 0))
        rgba = chroma_key(img, key_color=(0, 255, 0), tolerance=30)
        assert rgba.mode == "RGBA"
        assert rgba.getpixel((32, 32))[3] > 200
        assert rgba.getpixel((0, 0))[3] < 50


class TestAlphaStrategy:
    def test_background_is_opaque(self):
        info = LayerInfo(name="bg", description="bg", z_index=0, content_type="background")
        assert select_alpha_strategy(info) == "opaque"

    def test_text_uses_chroma(self):
        info = LayerInfo(name="text", description="text", z_index=5, content_type="text")
        assert select_alpha_strategy(info) == "chroma_or_threshold"

    def test_subject_uses_rembg(self):
        info = LayerInfo(name="person", description="person", z_index=2, content_type="subject")
        assert select_alpha_strategy(info) == "rembg_cascade"

    def test_effect_uses_sam(self):
        info = LayerInfo(name="mist", description="mist", z_index=1, content_type="effect")
        assert select_alpha_strategy(info) == "sam2_soft"


class TestEnsureAlpha:
    def test_background_stays_opaque(self):
        img = Image.new("RGB", (64, 64), (230, 225, 215))
        info = LayerInfo(name="paper", description="paper", z_index=0, content_type="background")
        result = ensure_alpha(img, info)
        assert result.mode == "RGBA"
        import numpy as np
        assert np.array(result)[:, :, 3].min() == 255

    def test_subject_gets_alpha(self):
        img = Image.new("RGB", (64, 64), (255, 255, 255))
        for x in range(20, 44):
            for y in range(20, 44):
                img.putpixel((x, y), (50, 50, 50))
        info = LayerInfo(name="tree", description="tree", z_index=2, content_type="subject")
        result = ensure_alpha(img, info)
        import numpy as np
        arr = np.array(result)
        assert arr[32, 32, 3] > 200
        assert arr[5, 5, 3] < 50

    def test_chroma_key_uses_white_by_default(self):
        img = Image.new("RGB", (64, 64), (255, 255, 255))
        for x in range(20, 44):
            for y in range(20, 44):
                img.putpixel((x, y), (200, 0, 0))
        rgba = chroma_key(img, key_color=(255, 255, 255), tolerance=30)
        import numpy as np
        arr = np.array(rgba)
        assert arr[5, 5, 3] < 50
        assert arr[32, 32, 3] > 200

    def test_already_has_alpha_skipped(self):
        img = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
        info = LayerInfo(name="pre_alpha", description="already has alpha", z_index=1, content_type="subject")
        result = ensure_alpha(img, info)
        import numpy as np
        assert np.array(result)[:, :, 3].max() == 0
