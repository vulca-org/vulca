"""Tests for ColorGamutChecker — Tier 1 cultural tool for saturation analysis.

Task 2: ColorGamutChecker — tradition-specific color gamut checking.
"""

from __future__ import annotations

import io
import os
import sys

import cv2
import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vulca.tools.protocol import ImageData, ToolCategory, ToolConfig
from vulca.tools.cultural.color_gamut import ColorGamutChecker, ColorGamutInput


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_png(arr: np.ndarray) -> bytes:
    """Convert (H, W, C) uint8 RGB ndarray to PNG bytes."""
    pil = Image.fromarray(arr.astype(np.uint8), mode="RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ink_wash_image() -> bytes:
    """Gray gradient — low saturation, suitable for chinese_xieyi (max_sat=60)."""
    h, w = 100, 100
    # Create a grayscale gradient: all pixels have S≈0 in HSV
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for i in range(h):
        v = int(50 + (i / h) * 180)  # value 50..230
        arr[i, :, :] = v  # R=G=B → zero saturation
    return _make_png(arr)


@pytest.fixture
def neon_image() -> bytes:
    """Neon magenta/cyan — very high saturation, violates xieyi (max_sat=60)."""
    h, w = 100, 100
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Left half: pure magenta [255, 0, 255]
    arr[:, :50, 0] = 255
    arr[:, :50, 1] = 0
    arr[:, :50, 2] = 255
    # Right half: pure cyan [0, 255, 255]
    arr[:, 50:, 0] = 0
    arr[:, 50:, 1] = 255
    arr[:, 50:, 2] = 255
    return _make_png(arr)


@pytest.fixture
def warm_earth_image() -> bytes:
    """Ochre/sienna tones — moderate saturation (~120-150)."""
    h, w = 100, 100
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Ochre: R=204, G=153, B=51 (moderate saturation)
    arr[:50, :, 0] = 204
    arr[:50, :, 1] = 153
    arr[:50, :, 2] = 51
    # Sienna: R=160, G=82, B=45
    arr[50:, :, 0] = 160
    arr[50:, :, 1] = 82
    arr[50:, :, 2] = 45
    return _make_png(arr)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_gamut_ink_wash_in_xieyi(ink_wash_image):
    """Gray gradient (near-zero saturation) should have compliance > 0.7 for xieyi."""
    checker = ColorGamutChecker()
    inp = ColorGamutInput(image=ink_wash_image, tradition="chinese_xieyi")
    out = checker.safe_execute(inp)
    assert out.compliance > 0.7, (
        f"Expected compliance > 0.7 for low-saturation image with xieyi, got {out.compliance}"
    )


def test_gamut_neon_violates_xieyi(neon_image):
    """Neon image (very high saturation) should have compliance < 0.5 for xieyi and non-empty dominant_colors."""
    checker = ColorGamutChecker()
    inp = ColorGamutInput(image=neon_image, tradition="chinese_xieyi")
    out = checker.safe_execute(inp)
    assert out.compliance < 0.5, (
        f"Expected compliance < 0.5 for neon image with xieyi, got {out.compliance}"
    )
    assert len(out.dominant_colors) > 0, "dominant_colors should be non-empty"


def test_gamut_fix_mode(neon_image):
    """Fix mode should return fixed_image with reduced saturation compared to original."""
    checker = ColorGamutChecker()
    inp = ColorGamutInput(image=neon_image, tradition="chinese_xieyi")
    config = ToolConfig(mode="fix")
    out = checker.safe_execute(inp, config)

    assert out.fixed_image is not None, "fixed_image should not be None in fix mode"

    # Load original and fixed images, compare saturation
    original_arr = np.array(Image.open(io.BytesIO(neon_image)).convert("RGB"), dtype=np.uint8)
    fixed_arr = np.array(Image.open(io.BytesIO(out.fixed_image)).convert("RGB"), dtype=np.uint8)

    orig_hsv = cv2.cvtColor(original_arr, cv2.COLOR_RGB2HSV)
    fixed_hsv = cv2.cvtColor(fixed_arr, cv2.COLOR_RGB2HSV)

    orig_mean_sat = float(np.mean(orig_hsv[:, :, 1]))
    fixed_mean_sat = float(np.mean(fixed_hsv[:, :, 1]))

    assert fixed_mean_sat < orig_mean_sat, (
        f"Fixed image saturation ({fixed_mean_sat:.1f}) should be lower than "
        f"original ({orig_mean_sat:.1f})"
    )


def test_gamut_dominant_colors(warm_earth_image):
    """dominant_colors should be non-empty and each color should have 3 integer elements."""
    checker = ColorGamutChecker()
    inp = ColorGamutInput(image=warm_earth_image, tradition="ukiyo_e")
    out = checker.safe_execute(inp)

    assert len(out.dominant_colors) > 0, "dominant_colors should not be empty"
    for color in out.dominant_colors:
        assert len(color) == 3, f"Each dominant color must have 3 elements (RGB), got {color}"
        for channel in color:
            assert isinstance(channel, int), (
                f"Color channel must be int, got {type(channel).__name__}: {channel}"
            )
            assert 0 <= channel <= 255, f"Color channel must be in [0, 255], got {channel}"


def test_gamut_evidence_valid_png(ink_wash_image):
    """evidence.annotated_image must be valid PNG bytes (PNG magic header \\x89PNG)."""
    checker = ColorGamutChecker()
    inp = ColorGamutInput(image=ink_wash_image, tradition="chinese_xieyi")
    out = checker.safe_execute(inp)

    assert out.evidence is not None, "evidence should not be None"
    assert out.evidence.annotated_image is not None, "evidence.annotated_image should not be None"
    # PNG magic: \x89PNG\r\n\x1a\n
    assert out.evidence.annotated_image[:4] == b"\x89PNG", (
        "evidence.annotated_image should start with PNG magic bytes \\x89PNG"
    )


def test_gamut_replaces():
    """ColorGamutChecker.replaces must equal {'evaluate': ['L3']} and category must be 'cultural'."""
    assert ColorGamutChecker.replaces == {"evaluate": ["L3"]}, (
        f"Expected replaces == {{'evaluate': ['L3']}}, got {ColorGamutChecker.replaces}"
    )
    assert ColorGamutChecker.category == ToolCategory.CULTURAL_CHECK, (
        f"Expected category == ToolCategory.CULTURAL_CHECK, got {ColorGamutChecker.category}"
    )
    assert ColorGamutChecker.category == "cultural", (
        f"Expected category value == 'cultural', got {ColorGamutChecker.category!r}"
    )
