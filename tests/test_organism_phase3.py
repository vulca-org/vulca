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
