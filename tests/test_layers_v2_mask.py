"""Tests for vulca.layers.mask — Color-Range Mask for extract mode."""
from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from vulca.layers.mask import hex_to_rgb, apply_mask_to_image, build_color_mask
from vulca.layers.types import LayerInfo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_half_image(left_rgb: tuple, right_rgb: tuple, size: int = 100) -> Image.Image:
    """Create an RGB image with a solid left half and solid right half."""
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    arr[:, : size // 2] = left_rgb
    arr[:, size // 2 :] = right_rgb
    return Image.fromarray(arr, mode="RGB")


def _make_ring_image(
    outer_rgb: tuple, center_rgb: tuple, size: int = 100, ring_frac: float = 0.2
) -> Image.Image:
    """Create an RGB image with a center square and outer border."""
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    arr[:, :] = outer_rgb
    margin = int(size * ring_frac)
    arr[margin : size - margin, margin : size - margin] = center_rgb
    return Image.fromarray(arr, mode="RGB")


def _mean_region(mask: Image.Image, region: str) -> float:
    """Return the mean mask value (0-255) for left or right half."""
    arr = np.array(mask)
    w = arr.shape[1]
    if region == "left":
        return float(arr[:, : w // 2].mean())
    elif region == "right":
        return float(arr[:, w // 2 :].mean())
    raise ValueError(f"Unknown region: {region}")


def _mean_center(mask: Image.Image, margin_frac: float = 0.2) -> float:
    """Return the mean mask value in the center region."""
    arr = np.array(mask)
    h, w = arr.shape
    m_h = int(h * margin_frac)
    m_w = int(w * margin_frac)
    return float(arr[m_h : h - m_h, m_w : w - m_w].mean())


def _mean_border(mask: Image.Image, margin_frac: float = 0.2) -> float:
    """Return the mean mask value in the border region (excluding center)."""
    arr = np.array(mask)
    h, w = arr.shape
    m_h = int(h * margin_frac)
    m_w = int(w * margin_frac)
    # Create border mask
    border_mask = np.ones((h, w), dtype=bool)
    border_mask[m_h : h - m_h, m_w : w - m_w] = False
    return float(arr[border_mask].mean())


# ---------------------------------------------------------------------------
# TestBuildColorMask
# ---------------------------------------------------------------------------

class TestBuildColorMask:

    def test_red_dominant_color_bright_on_red_half_dark_on_blue_half(self):
        """Red/blue image + red dominant color -> red half bright, blue half dark."""
        img = _make_half_image(left_rgb=(220, 30, 30), right_rgb=(30, 30, 220))
        info = LayerInfo(
            name="red_layer",
            description="red subject",
            z_index=1,
            content_type="subject",
            dominant_colors=["#DC1E1E"],  # close to (220, 30, 30)
        )
        mask = build_color_mask(img, info, tolerance=30)

        assert mask.mode == "L", "Mask must be mode L"
        assert mask.size == img.size, "Mask must match image dimensions"

        left_mean = _mean_region(mask, "left")
        right_mean = _mean_region(mask, "right")

        # Red half should be significantly brighter than blue half
        assert left_mean > 100, f"Red half too dark: {left_mean:.1f}"
        assert right_mean < 60, f"Blue half too bright: {right_mean:.1f}"
        assert left_mean > right_mean + 60, (
            f"Red half ({left_mean:.1f}) should be much brighter than blue half ({right_mean:.1f})"
        )

    def test_white_dominant_color_bright_on_white_corners_dark_on_red_center(self):
        """background content_type with white dominant color -> white corners bright, red center dark."""
        img = _make_ring_image(outer_rgb=(245, 245, 245), center_rgb=(200, 30, 30))
        info = LayerInfo(
            name="background",
            description="white background",
            z_index=0,
            content_type="background",
            dominant_colors=["#F5F5F5"],  # close to (245, 245, 245)
        )
        mask = build_color_mask(img, info, tolerance=30)

        assert mask.mode == "L"
        assert mask.size == img.size

        border_mean = _mean_border(mask, margin_frac=0.25)
        center_mean = _mean_center(mask, margin_frac=0.25)

        # White corners should be brighter than red center
        assert border_mean > 100, f"White border too dark: {border_mean:.1f}"
        assert center_mean < 80, f"Red center too bright: {center_mean:.1f}"
        assert border_mean > center_mean + 30, (
            f"White border ({border_mean:.1f}) should be brighter than red center ({center_mean:.1f})"
        )

    def test_effect_content_type_includes_low_saturation_edges(self):
        """effect content_type -> low-saturation edges included, high-saturation center excluded."""
        # Outer border: nearly-gray (low saturation), center: vivid green (high saturation)
        img = _make_ring_image(
            outer_rgb=(180, 185, 182),   # near-gray, low saturation
            center_rgb=(20, 200, 50),    # vivid green, high saturation
            size=100,
            ring_frac=0.25,
        )
        info = LayerInfo(
            name="effect_layer",
            description="mist overlay",
            z_index=3,
            content_type="effect",
            dominant_colors=[],  # no specific color — rely on low-sat detection
        )
        mask = build_color_mask(img, info, tolerance=30)

        assert mask.mode == "L"
        assert mask.size == img.size

        border_mean = _mean_border(mask, margin_frac=0.3)
        center_mean = _mean_center(mask, margin_frac=0.3)

        # Low-saturation edges should be included (bright), high-saturation center excluded (dark)
        assert border_mean > center_mean, (
            f"Effect border ({border_mean:.1f}) should be brighter than saturated center ({center_mean:.1f})"
        )
        assert border_mean > 80, f"Low-sat border should be reasonably bright, got {border_mean:.1f}"
        assert center_mean < 100, f"High-sat center should be darker, got {center_mean:.1f}"


# ---------------------------------------------------------------------------
# TestApplyMask
# ---------------------------------------------------------------------------

class TestApplyMask:

    def test_half_mask_left_opaque_right_transparent(self):
        """RGB image + half-white/half-black mask -> RGBA with left opaque, right transparent."""
        size = 60
        # Solid blue RGB image
        img_arr = np.full((size, size, 3), (0, 100, 200), dtype=np.uint8)
        img = Image.fromarray(img_arr, mode="RGB")

        # Mask: left half white (255), right half black (0)
        mask_arr = np.zeros((size, size), dtype=np.uint8)
        mask_arr[:, : size // 2] = 255
        mask = Image.fromarray(mask_arr, mode="L")

        result = apply_mask_to_image(img, mask)

        assert result.mode == "RGBA", "Result must be RGBA"
        assert result.size == img.size, "Result size must match input"

        result_arr = np.array(result)
        # Left half: alpha == 255 (opaque)
        left_alpha = result_arr[:, : size // 2, 3]
        assert left_alpha.min() == 255, f"Left alpha min={left_alpha.min()}, expected 255"

        # Right half: alpha == 0 (transparent)
        right_alpha = result_arr[:, size // 2 :, 3]
        assert right_alpha.max() == 0, f"Right alpha max={right_alpha.max()}, expected 0"

        # RGB channels of left half must be preserved
        left_rgb = result_arr[:, : size // 2, :3]
        assert left_rgb[:, :, 0].mean() == pytest.approx(0, abs=1)
        assert left_rgb[:, :, 1].mean() == pytest.approx(100, abs=1)
        assert left_rgb[:, :, 2].mean() == pytest.approx(200, abs=1)


# ---------------------------------------------------------------------------
# TestHexToRgb (helper function)
# ---------------------------------------------------------------------------

class TestHexToRgb:

    def test_rrggbb_format(self):
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("#00FF00") == (0, 255, 0)
        assert hex_to_rgb("#0000FF") == (0, 0, 255)
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_rgb_shorthand_format(self):
        # "#RGB" -> "#RRGGBB"
        assert hex_to_rgb("#F00") == (255, 0, 0)
        assert hex_to_rgb("#0F0") == (0, 255, 0)
        assert hex_to_rgb("#00F") == (0, 0, 255)
        assert hex_to_rgb("#FFF") == (255, 255, 255)

    def test_no_hash_prefix(self):
        # Should work with or without '#'
        assert hex_to_rgb("FF0000") == (255, 0, 0)

    def test_lowercase_hex(self):
        assert hex_to_rgb("#ff0000") == (255, 0, 0)
        assert hex_to_rgb("#dc1e1e") == (220, 30, 30)
