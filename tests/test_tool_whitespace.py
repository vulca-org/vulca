"""Tests for WhitespaceAnalyzer — Tier 1 cultural analysis tool.

Task 4: WhitespaceAnalyzer — deterministic whitespace analysis for ink wash art.
"""

from __future__ import annotations

import io
import os
import sys

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vulca.tools.protocol import ImageData, ToolConfig
from vulca.tools.cultural.whitespace import WhitespaceAnalyzer, WhitespaceInput


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_png(arr: np.ndarray) -> bytes:
    """Convert (H, W, C) uint8 RGB ndarray to PNG bytes."""
    pil = Image.fromarray(arr.astype(np.uint8), mode="RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def white_heavy_image() -> bytes:
    """80% white image — bright background with a dark 20% strip at the bottom."""
    h, w = 100, 100
    arr = np.full((h, w, 3), 255, dtype=np.uint8)  # all white
    # bottom 20 rows are dark (20% of image)
    arr[80:, :, :] = 30
    return _make_png(arr)


@pytest.fixture
def dark_heavy_image() -> bytes:
    """80% dark image — dark background with a bright 20% strip at the top."""
    h, w = 100, 100
    arr = np.full((h, w, 3), 30, dtype=np.uint8)  # all dark
    # top 20 rows are white (20% of image)
    arr[:20, :, :] = 255
    return _make_png(arr)


@pytest.fixture
def balanced_image() -> bytes:
    """~50% white image — left half white, right half dark."""
    h, w = 100, 100
    arr = np.full((h, w, 3), 30, dtype=np.uint8)  # all dark
    arr[:, :50, :] = 255  # left half white
    return _make_png(arr)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_whitespace_high_ratio(white_heavy_image):
    """White-heavy image should produce ratio > 0.7."""
    analyzer = WhitespaceAnalyzer()
    inp = WhitespaceInput(image=white_heavy_image)
    out = analyzer.safe_execute(inp)
    assert out.ratio > 0.7, f"Expected ratio > 0.7, got {out.ratio}"


def test_whitespace_low_ratio(dark_heavy_image):
    """Dark-heavy image should produce ratio < 0.3."""
    analyzer = WhitespaceAnalyzer()
    inp = WhitespaceInput(image=dark_heavy_image)
    out = analyzer.safe_execute(inp)
    assert out.ratio < 0.3, f"Expected ratio < 0.3, got {out.ratio}"


def test_whitespace_balanced(balanced_image):
    """Balanced image should produce ratio in [0.35, 0.65]."""
    analyzer = WhitespaceAnalyzer()
    inp = WhitespaceInput(image=balanced_image)
    out = analyzer.safe_execute(inp)
    assert 0.35 <= out.ratio <= 0.65, f"Expected 0.35 <= ratio <= 0.65, got {out.ratio}"


def test_whitespace_cultural_verdict_xieyi(balanced_image):
    """cultural_verdict should be non-empty string for chinese_xieyi tradition."""
    analyzer = WhitespaceAnalyzer()
    inp = WhitespaceInput(image=balanced_image, tradition="chinese_xieyi")
    out = analyzer.safe_execute(inp)
    assert isinstance(out.cultural_verdict, str)
    assert len(out.cultural_verdict) > 0, "cultural_verdict should not be empty"


def test_whitespace_regions_are_bboxes(white_heavy_image):
    """regions list items must all have x, y, w, h integer keys."""
    analyzer = WhitespaceAnalyzer()
    inp = WhitespaceInput(image=white_heavy_image)
    out = analyzer.safe_execute(inp)
    assert isinstance(out.regions, list)
    for region in out.regions:
        assert isinstance(region, dict), f"Region should be dict, got {type(region)}"
        for key in ("x", "y", "w", "h"):
            assert key in region, f"Region missing key '{key}': {region}"
            assert isinstance(region[key], int), f"Region['{key}'] should be int, got {type(region[key])}"


def test_whitespace_with_thresholds(balanced_image):
    """Custom thresholds in ToolConfig override tradition defaults and affect verdict."""
    analyzer = WhitespaceAnalyzer()
    inp = WhitespaceInput(image=balanced_image, tradition="chinese_xieyi")

    # Default config — balanced image (≈0.5) is within xieyi range (0.30–0.55)
    config_default = ToolConfig()
    out_default = analyzer.safe_execute(inp, config_default)

    # Very strict thresholds — only [0.90, 0.99] passes; balanced image (~0.5) should fail
    config_strict = ToolConfig(thresholds={"ratio_min": 0.90, "ratio_max": 0.99})
    out_strict = analyzer.safe_execute(inp, config_strict)

    # Both verdicts are non-empty strings
    assert len(out_default.cultural_verdict) > 0
    assert len(out_strict.cultural_verdict) > 0
    # The verdicts should differ because thresholds changed
    assert out_default.cultural_verdict != out_strict.cultural_verdict, (
        "Strict thresholds should produce a different verdict than default thresholds"
    )


def test_whitespace_replaces_declaration():
    """WhitespaceAnalyzer.replaces must equal {'evaluate': ['L1']}."""
    assert WhitespaceAnalyzer.replaces == {"evaluate": ["L1"]}


def test_whitespace_evidence_is_valid_png(white_heavy_image):
    """evidence.annotated_image must be valid PNG bytes (PNG magic header)."""
    analyzer = WhitespaceAnalyzer()
    inp = WhitespaceInput(image=white_heavy_image)
    out = analyzer.safe_execute(inp)
    assert out.evidence is not None, "evidence should not be None"
    assert out.evidence.annotated_image is not None, "evidence.annotated_image should not be None"
    # PNG magic: \x89PNG\r\n\x1a\n
    assert out.evidence.annotated_image[:4] == b"\x89PNG", (
        "evidence.annotated_image should start with PNG magic bytes"
    )
