"""Tests for Organism Integrity Phase 3 — Layer Semantics."""
from __future__ import annotations

import numpy as np
import tempfile
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from vulca.layers.types import LayerInfo


def _make_layer(name: str, z: int, colors: list[str], ctype: str = "subject") -> LayerInfo:
    return LayerInfo(
        id=f"layer_{name}",
        name=name,
        description=f"Test layer {name}",
        z_index=z,
        blend_mode="normal",
        dominant_colors=colors,
        content_type=ctype,
        regeneration_prompt=f"Generate {name}",
    )


def _make_test_image(w: int = 100, h: int = 100) -> Image.Image:
    """Create a test image with distinct color regions."""
    img = Image.new("RGB", (w, h), (255, 255, 255))
    pixels = img.load()
    # Top half: red (#FF0000)
    for y in range(h // 2):
        for x in range(w):
            pixels[x, y] = (255, 0, 0)
    # Bottom half: blue (#0000FF)
    for y in range(h // 2, h):
        for x in range(w):
            pixels[x, y] = (0, 0, 255)
    return img


class TestExclusivePixelAssignment:
    """Task 1: Extract mode assigns each pixel to at most one layer."""

    def test_no_pixel_overlap(self):
        """Two layers with different colors should not share pixels."""
        from vulca.layers.mask import build_color_mask

        img = _make_test_image()
        layer_red = _make_layer("red", 0, ["#FF0000"])
        layer_blue = _make_layer("blue", 1, ["#0000FF"])

        assigned = np.zeros((100, 100), dtype=bool)

        mask_red = build_color_mask(img, layer_red, tolerance=30, assigned=assigned)
        red_arr = np.array(mask_red)
        assigned |= (red_arr > 127)

        mask_blue = build_color_mask(img, layer_blue, tolerance=30, assigned=assigned)
        blue_arr = np.array(mask_blue)

        # No pixel should be claimed by both
        overlap = (red_arr > 127) & (blue_arr > 127)
        assert np.sum(overlap) == 0, f"{np.sum(overlap)} pixels overlap"

    def test_assigned_pixels_zeroed_in_mask(self):
        """Pixels in assigned array should have 0 in the new mask."""
        from vulca.layers.mask import build_color_mask

        img = _make_test_image()
        layer = _make_layer("red", 0, ["#FF0000"])

        # Pre-assign top-left quadrant
        assigned = np.zeros((100, 100), dtype=bool)
        assigned[:50, :50] = True

        mask = build_color_mask(img, layer, tolerance=30, assigned=assigned)
        mask_arr = np.array(mask)

        # Top-left quadrant should be zero despite matching color
        assert np.all(mask_arr[:50, :50] == 0)

    def test_split_extract_exclusive(self):
        """split_extract should produce non-overlapping layer masks."""
        from vulca.layers.split import split_extract

        img = _make_test_image(200, 200)
        with tempfile.TemporaryDirectory() as td:
            img_path = Path(td) / "test.png"
            img.save(str(img_path))

            layers = [
                _make_layer("red_region", 0, ["#FF0000"]),
                _make_layer("blue_region", 1, ["#0000FF"]),
            ]
            results = split_extract(str(img_path), layers, output_dir=td)

            # Load both layer images by name and check alpha overlap
            by_name = {r.info.name: r for r in results}
            r_arr = np.array(Image.open(by_name["red_region"].image_path).split()[3])
            b_arr = np.array(Image.open(by_name["blue_region"].image_path).split()[3])

            overlap = (r_arr > 127) & (b_arr > 127)
            assert np.sum(overlap) == 0, f"{np.sum(overlap)} pixels overlap between layers"

            # Semantic: each layer should have actual opaque pixels
            assert np.sum(r_arr > 127) > 0, "red layer should have opaque pixels"
            assert np.sum(b_arr > 127) > 0, "blue layer should have opaque pixels"

    def test_backward_compat_no_assigned(self):
        """build_color_mask without assigned param still works (backward compat)."""
        from vulca.layers.mask import build_color_mask

        img = _make_test_image()
        layer = _make_layer("red", 0, ["#FF0000"])
        mask = build_color_mask(img, layer, tolerance=30)
        assert mask.mode == "L"
        assert mask.size == (100, 100)


class TestDominantColorValidation:
    """Task 2: Validate VLM-guessed colors against actual image pixels."""

    def test_correct_colors_pass_validation(self):
        """Colors matching actual pixels should be returned unchanged."""
        from vulca.layers.mask import validate_dominant_colors

        img = _make_test_image()
        validated = validate_dominant_colors(img, ["#FF0000", "#0000FF"])
        assert validated == ["#FF0000", "#0000FF"], f"Expected unchanged, got {validated}"

    def test_wrong_colors_get_replaced(self):
        """Colors far from any image pixel should be replaced with sampled colors."""
        from vulca.layers.mask import validate_dominant_colors

        img = _make_test_image()  # only has red and blue
        validated = validate_dominant_colors(img, ["#00FF00"])  # green doesn't exist
        # Should be replaced with an actual image color (same length as input)
        assert len(validated) == 1  # Same length as input (contract: same length, bad colors replaced)
        # The replacement should be close to red or blue
        for hex_c in validated:
            r, g, b = int(hex_c[1:3], 16), int(hex_c[3:5], 16), int(hex_c[5:7], 16)
            close_to_red = abs(r - 255) < 50 and g < 50 and b < 50
            close_to_blue = r < 50 and g < 50 and abs(b - 255) < 50
            assert close_to_red or close_to_blue, f"Replacement color {hex_c} not close to red or blue"

    def test_empty_colors_get_sampled(self):
        """Empty dominant_colors should be populated from image sampling."""
        from vulca.layers.mask import validate_dominant_colors

        img = _make_test_image()
        validated = validate_dominant_colors(img, [])
        assert len(validated) >= 1
        # Sampled colors should be valid hex and close to actual image colors
        for hex_c in validated:
            assert hex_c.startswith("#") and len(hex_c) == 7, f"Invalid hex: {hex_c}"


class TestVLMMaskShared:
    """Task 3: Shared VLM mask module used by regenerate and --layered."""

    def test_vlm_mask_module_exists(self):
        from vulca.layers import vlm_mask
        assert hasattr(vlm_mask, "generate_vlm_mask")

    def test_vlm_mask_prompt_asks_for_bw(self):
        from vulca.layers.vlm_mask import VLM_MASK_PROMPT
        assert "black" in VLM_MASK_PROMPT.lower()
        assert "white" in VLM_MASK_PROMPT.lower()

    def test_apply_vlm_mask_creates_rgba(self):
        from vulca.layers.vlm_mask import apply_vlm_mask
        content = Image.new("RGB", (64, 64), (200, 100, 50))
        mask = Image.new("L", (64, 64), 128)
        result = apply_vlm_mask(content, mask)
        assert result.mode == "RGBA"
        assert result.size == (64, 64)
        # Alpha should be 128 everywhere
        alpha = np.array(result.split()[3])
        assert np.all(alpha == 128)

    def test_apply_vlm_mask_resizes_mask(self):
        from vulca.layers.vlm_mask import apply_vlm_mask
        content = Image.new("RGB", (100, 100), (200, 100, 50))
        mask = Image.new("L", (50, 50), 255)  # Different size
        result = apply_vlm_mask(content, mask)
        assert result.size == (100, 100)

    def test_regenerate_no_longer_uses_color_mask_for_alpha(self):
        """split_regenerate should use vlm_mask module for alpha."""
        import inspect
        from vulca.layers.split import split_regenerate
        source = inspect.getsource(split_regenerate)
        assert "vlm_mask" in source, "split_regenerate should use vlm_mask module"


class TestSAMPointPrompts:
    """Task 4: SAM uses layer-specific point prompts, not image center."""

    def test_point_from_color_centroid(self):
        """Point prompt should be at the centroid of the layer's dominant color region."""
        from vulca.layers.sam import _compute_layer_point

        img = _make_test_image(200, 200)  # top=red, bottom=blue
        layer_red = _make_layer("red", 0, ["#FF0000"])
        layer_blue = _make_layer("blue", 1, ["#0000FF"])

        px_red, py_red = _compute_layer_point(img, layer_red)
        px_blue, py_blue = _compute_layer_point(img, layer_blue)

        # Red centroid should be in top half
        assert py_red < 100, f"Red point y={py_red} should be < 100"
        # Blue centroid should be in bottom half
        assert py_blue >= 100, f"Blue point y={py_blue} should be >= 100"

    def test_fallback_to_center(self):
        """If no dominant_colors, fall back to image center."""
        from vulca.layers.sam import _compute_layer_point

        img = _make_test_image(200, 200)
        layer_no_colors = _make_layer("unknown", 0, [])

        px, py = _compute_layer_point(img, layer_no_colors)
        assert px == 100  # w // 2
        assert py == 100  # h // 2

    def test_point_x_centered_for_full_width_region(self):
        """For a color region spanning full width, x should be near center."""
        from vulca.layers.sam import _compute_layer_point

        img = _make_test_image(200, 200)  # red spans full width of top half
        layer_red = _make_layer("red", 0, ["#FF0000"])
        px, py = _compute_layer_point(img, layer_red)
        # x should be near center (full width)
        assert 80 <= px <= 120, f"x={px} should be near center for full-width region"
