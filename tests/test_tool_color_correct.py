"""Tests for ColorCorrect — Tier 2 image processing tool.

Task 5: ColorCorrect — color balance analysis and correction.

Fixtures:
    red_tinted_image  — R=200, G=100, B=100 (strong red cast)
    normal_image      — R=120, G=130, B=125 (balanced)
"""

from __future__ import annotations

import io
import os
import sys

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vulca.tools.filters.color_correct import ColorCorrect, ColorCorrectInput, ColorCorrectOutput
from vulca.tools.protocol import ImageData, ToolCategory, ToolConfig


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_png_bytes(r: int, g: int, b: int, w: int = 32, h: int = 32) -> bytes:
    """Create a PNG-encoded solid-color image."""
    arr = np.full((h, w, 3), [r, g, b], dtype=np.uint8)
    pil = Image.fromarray(arr, mode="RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def red_tinted_image() -> bytes:
    """Strong red cast: R=200, G=100, B=100."""
    return _make_png_bytes(200, 100, 100)


@pytest.fixture
def normal_image() -> bytes:
    """Balanced image: R=120, G=130, B=125."""
    return _make_png_bytes(120, 130, 125)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_color_correct_check_mode(red_tinted_image):
    """Check mode detects red bias; evidence.details contains channel_bias info."""
    tool = ColorCorrect()
    inp = ColorCorrectInput(image=red_tinted_image)
    cfg = ToolConfig(mode="check")
    out = tool.safe_execute(inp, cfg)

    assert isinstance(out, ColorCorrectOutput)

    # Red channel should show strong positive bias
    assert out.channel_bias["red"] > 0.05
    # Green and blue should be negative
    assert out.channel_bias["green"] < 0.0
    assert out.channel_bias["blue"] < 0.0

    # Brightness should be near mean of (200+100+100)/3 * something
    assert 0 < out.brightness < 256

    # Contrast is std deviation, should be non-negative
    assert out.contrast >= 0.0

    # Evidence must be present
    assert out.evidence is not None
    assert "channel_bias" in out.evidence.details
    assert out.evidence.confidence > 0.0

    # fix mode not triggered — fixed_image should be None
    assert out.fixed_image is None


def test_color_correct_fix_mode(red_tinted_image):
    """Fix mode returns corrected image; red channel reduced after correction."""
    tool = ColorCorrect()
    inp = ColorCorrectInput(image=red_tinted_image)
    cfg = ToolConfig(mode="fix")
    out = tool.safe_execute(inp, cfg)

    assert isinstance(out, ColorCorrectOutput)

    # fixed_image must be returned in fix mode
    assert out.fixed_image is not None
    assert isinstance(out.fixed_image, bytes)

    # Decode fixed image and verify red channel has been reduced
    fixed_arr = np.array(Image.open(io.BytesIO(out.fixed_image)).convert("RGB"), dtype=np.float32)
    original_arr = np.array(Image.open(io.BytesIO(red_tinted_image)).convert("RGB"), dtype=np.float32)

    # After color correction, channels should be more balanced
    fixed_r_mean = float(np.mean(fixed_arr[:, :, 0]))
    fixed_g_mean = float(np.mean(fixed_arr[:, :, 1]))
    fixed_b_mean = float(np.mean(fixed_arr[:, :, 2]))

    orig_r_mean = float(np.mean(original_arr[:, :, 0]))

    # Red should be reduced after correction
    assert fixed_r_mean < orig_r_mean

    # Channels should be more balanced in fixed image
    fixed_max_bias = max(abs(fixed_r_mean - np.mean([fixed_r_mean, fixed_g_mean, fixed_b_mean])),
                         abs(fixed_g_mean - np.mean([fixed_r_mean, fixed_g_mean, fixed_b_mean])),
                         abs(fixed_b_mean - np.mean([fixed_r_mean, fixed_g_mean, fixed_b_mean])))
    orig_max_bias = abs(orig_r_mean - np.mean([np.mean(original_arr[:, :, 0]),
                                                np.mean(original_arr[:, :, 1]),
                                                np.mean(original_arr[:, :, 2])]))
    assert fixed_max_bias < orig_max_bias


def test_color_correct_suggest_mode(red_tinted_image):
    """Suggest mode returns non-empty suggestions and no fixed_image."""
    tool = ColorCorrect()
    inp = ColorCorrectInput(image=red_tinted_image)
    cfg = ToolConfig(mode="suggest")
    out = tool.safe_execute(inp, cfg)

    assert isinstance(out, ColorCorrectOutput)

    # Suggest mode: textual suggestions must be provided
    assert len(out.suggestions) > 0
    assert all(isinstance(s, str) for s in out.suggestions)

    # No image correction in suggest mode
    assert out.fixed_image is None


def test_color_correct_normal_image(normal_image):
    """Balanced image shows no strong channel bias."""
    tool = ColorCorrect()
    inp = ColorCorrectInput(image=normal_image)
    cfg = ToolConfig(mode="check")
    out = tool.safe_execute(inp, cfg)

    assert isinstance(out, ColorCorrectOutput)

    # All channel biases should be small (< 0.05 threshold)
    for ch, bias in out.channel_bias.items():
        assert abs(bias) < 0.05, f"Channel {ch} bias {bias:.3f} exceeds threshold"


def test_color_correct_with_brightness_params(normal_image):
    """brightness=1.3 param in fix mode results in a brighter output image."""
    tool = ColorCorrect()
    inp = ColorCorrectInput(image=normal_image)
    cfg = ToolConfig(mode="fix", params={"brightness": 1.3})
    out = tool.safe_execute(inp, cfg)

    assert out.fixed_image is not None

    # Fixed image should be brighter than original
    fixed_arr = np.array(Image.open(io.BytesIO(out.fixed_image)).convert("RGB"), dtype=np.float32)
    original_arr = np.array(Image.open(io.BytesIO(normal_image)).convert("RGB"), dtype=np.float32)

    fixed_mean = float(np.mean(fixed_arr))
    original_mean = float(np.mean(original_arr))

    assert fixed_mean > original_mean, (
        f"Expected brightness increase: fixed={fixed_mean:.1f} > original={original_mean:.1f}"
    )


def test_color_correct_category_and_name():
    """ColorCorrect has name='color_correct' and category=FILTER."""
    assert ColorCorrect.name == "color_correct"
    assert ColorCorrect.display_name == "Color Correct"
    assert ColorCorrect.category == ToolCategory.FILTER
    assert ColorCorrect.replaces == {}
    assert ColorCorrect.max_seconds <= 10


def test_color_correct_evidence_is_valid_png(red_tinted_image):
    """evidence.annotated_image is valid PNG (starts with PNG magic bytes)."""
    tool = ColorCorrect()
    inp = ColorCorrectInput(image=red_tinted_image)
    cfg = ToolConfig(mode="check")
    out = tool.safe_execute(inp, cfg)

    assert out.evidence is not None
    assert out.evidence.annotated_image is not None

    # PNG magic bytes: 0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A
    png_magic = b"\x89PNG\r\n\x1a\n"
    assert out.evidence.annotated_image[:8] == png_magic, (
        f"Expected PNG magic bytes, got {out.evidence.annotated_image[:8]!r}"
    )
