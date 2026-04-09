"""Tests for BrushstrokeAnalyzer — Tier 1 cultural analysis tool.

Task 3: BrushstrokeAnalyzer — deterministic brushstroke/texture analysis for ink-wash art.
"""

from __future__ import annotations

import pytest
pytest.importorskip("cv2", reason="cv2 is an optional dependency (pip install vulca[tools])")

import io
import os
import sys

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vulca.tools.protocol import ToolConfig
from vulca.tools.cultural.brushstroke import BrushstrokeAnalyzer, BrushstrokeInput


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
def smooth_gradient() -> bytes:
    """Smooth gray gradient — no texture, low energy."""
    h, w = 100, 100
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Create a smooth horizontal gradient from 50 to 200
    gradient = np.linspace(50, 200, w, dtype=np.uint8)
    arr[:, :, 0] = gradient  # R
    arr[:, :, 1] = gradient  # G
    arr[:, :, 2] = gradient  # B
    return _make_png(arr)


@pytest.fixture
def textured_image() -> bytes:
    """Random noise image in range 50-200 — high texture energy."""
    rng = np.random.default_rng(42)
    arr = rng.integers(50, 200, size=(100, 100, 3), dtype=np.uint8)
    return _make_png(arr)


@pytest.fixture
def striped_image() -> bytes:
    """Vertical stripes every 4px — strong directional signal."""
    h, w = 100, 100
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for col in range(w):
        val = 240 if (col // 4) % 2 == 0 else 20
        arr[:, col, :] = val
    return _make_png(arr)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_brushstroke_smooth_low_texture(smooth_gradient):
    """Smooth gradient should produce texture_energy < 0.5."""
    analyzer = BrushstrokeAnalyzer()
    inp = BrushstrokeInput(image=smooth_gradient)
    out = analyzer.safe_execute(inp)
    assert out.texture_energy < 0.5, (
        f"Expected texture_energy < 0.5 for smooth gradient, got {out.texture_energy}"
    )


def test_brushstroke_textured_high_energy(textured_image):
    """Random noise image should produce texture_energy > 0.3."""
    analyzer = BrushstrokeAnalyzer()
    inp = BrushstrokeInput(image=textured_image)
    out = analyzer.safe_execute(inp)
    assert out.texture_energy > 0.3, (
        f"Expected texture_energy > 0.3 for noisy image, got {out.texture_energy}"
    )


def test_brushstroke_directional(striped_image):
    """Vertical striped image should have a non-None dominant_direction that is a string."""
    analyzer = BrushstrokeAnalyzer()
    inp = BrushstrokeInput(image=striped_image)
    out = analyzer.safe_execute(inp)
    assert out.dominant_direction is not None, (
        "Striped image should produce a dominant_direction, got None"
    )
    assert isinstance(out.dominant_direction, str), (
        f"dominant_direction should be str, got {type(out.dominant_direction)}"
    )
    valid_directions = {"horizontal", "vertical", "diagonal_rising", "diagonal_falling"}
    assert out.dominant_direction in valid_directions, (
        f"dominant_direction '{out.dominant_direction}' not in {valid_directions}"
    )


def test_brushstroke_cultural_verdict(textured_image):
    """cultural_verdict should be a non-empty string when tradition is provided."""
    analyzer = BrushstrokeAnalyzer()
    inp = BrushstrokeInput(image=textured_image, tradition="chinese_xieyi")
    out = analyzer.safe_execute(inp)
    assert isinstance(out.cultural_verdict, str), (
        f"cultural_verdict should be str, got {type(out.cultural_verdict)}"
    )
    assert len(out.cultural_verdict) > 0, "cultural_verdict should not be empty"


def test_brushstroke_evidence_valid_png(textured_image):
    """evidence.annotated_image must be valid PNG bytes (PNG magic header)."""
    analyzer = BrushstrokeAnalyzer()
    inp = BrushstrokeInput(image=textured_image)
    out = analyzer.safe_execute(inp)
    assert out.evidence is not None, "evidence should not be None"
    assert out.evidence.annotated_image is not None, (
        "evidence.annotated_image should not be None"
    )
    # PNG magic: \x89PNG\r\n\x1a\n
    assert out.evidence.annotated_image[:4] == b"\x89PNG", (
        "evidence.annotated_image should start with PNG magic bytes"
    )


def test_brushstroke_replaces():
    """BrushstrokeAnalyzer.replaces must equal {'evaluate': ['L2']}."""
    assert BrushstrokeAnalyzer.replaces == {"evaluate": ["L2"]}
