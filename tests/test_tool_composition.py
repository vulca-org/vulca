"""Tests for CompositionAnalyzer — Tier 1 cultural composition tool.

Task 1 (Phase 2): CompositionAnalyzer — deterministic composition analysis.
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

from vulca.tools.protocol import ImageData, ToolCategory, ToolConfig
from vulca.tools.cultural.composition import CompositionAnalyzer, CompositionInput


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
def centered_subject() -> bytes:
    """300x300 white image with a dark block in the center third."""
    h, w = 300, 300
    arr = np.full((h, w, 3), 255, dtype=np.uint8)  # white background
    # Dark block occupying the center third: rows 100-200, cols 100-200
    arr[100:200, 100:200, :] = 30
    return _make_png(arr)


@pytest.fixture
def rule_of_thirds_image() -> bytes:
    """300x300 white image with a dark block near the (1/3, 1/3) intersection."""
    h, w = 300, 300
    arr = np.full((h, w, 3), 255, dtype=np.uint8)  # white background
    # Dark block centered near (col=100, row=100) — top-left thirds intersection
    arr[80:120, 80:120, :] = 30
    return _make_png(arr)


@pytest.fixture
def empty_image() -> bytes:
    """100x100 uniform gray image — no strong visual weight anywhere."""
    h, w = 100, 100
    arr = np.full((h, w, 3), 128, dtype=np.uint8)
    return _make_png(arr)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_composition_centered_subject(centered_subject):
    """Centered dark block should yield center_weight > 0.3 and evidence."""
    analyzer = CompositionAnalyzer()
    inp = CompositionInput(image=centered_subject)
    out = analyzer.safe_execute(inp)

    assert out.center_weight > 0.3, (
        f"Expected center_weight > 0.3 for centered subject, got {out.center_weight}"
    )
    assert out.evidence is not None, "evidence should not be None"
    assert isinstance(out.evidence.summary, str)
    assert len(out.evidence.summary) > 0


def test_composition_rule_of_thirds(rule_of_thirds_image):
    """Rule-of-thirds image should have thirds_alignment >= 0.0 and visual_center with x/y."""
    analyzer = CompositionAnalyzer()
    inp = CompositionInput(image=rule_of_thirds_image)
    out = analyzer.safe_execute(inp)

    assert out.thirds_alignment >= 0.0, (
        f"thirds_alignment must be non-negative, got {out.thirds_alignment}"
    )
    assert isinstance(out.visual_center, dict), (
        f"visual_center must be a dict, got {type(out.visual_center)}"
    )
    assert "x" in out.visual_center, "visual_center must have key 'x'"
    assert "y" in out.visual_center, "visual_center must have key 'y'"
    # Coordinates should be in [0, 1]
    assert 0.0 <= out.visual_center["x"] <= 1.0, (
        f"visual_center['x'] out of range: {out.visual_center['x']}"
    )
    assert 0.0 <= out.visual_center["y"] <= 1.0, (
        f"visual_center['y'] out of range: {out.visual_center['y']}"
    )


def test_composition_detects_guidelines(centered_subject, rule_of_thirds_image):
    """detected_rules must be a list; center image should contain 'center_composition'."""
    analyzer = CompositionAnalyzer()

    # Centered subject
    inp = CompositionInput(image=centered_subject)
    out = analyzer.safe_execute(inp)
    assert isinstance(out.detected_rules, list), (
        f"detected_rules must be a list, got {type(out.detected_rules)}"
    )
    assert "center_composition" in out.detected_rules, (
        f"Expected 'center_composition' in detected_rules for centered image, got {out.detected_rules}"
    )

    # Rule-of-thirds image — just verify it's a list (no hard constraint on contents)
    inp2 = CompositionInput(image=rule_of_thirds_image)
    out2 = analyzer.safe_execute(inp2)
    assert isinstance(out2.detected_rules, list)


def test_composition_cultural_verdict(centered_subject):
    """cultural_verdict must be a non-empty string when tradition is provided."""
    analyzer = CompositionAnalyzer()
    inp = CompositionInput(image=centered_subject, tradition="chinese_xieyi")
    out = analyzer.safe_execute(inp)

    assert isinstance(out.cultural_verdict, str), (
        f"cultural_verdict must be str, got {type(out.cultural_verdict)}"
    )
    assert len(out.cultural_verdict) > 0, "cultural_verdict should not be empty"


def test_composition_evidence_valid_png(centered_subject):
    """evidence.annotated_image must be valid PNG bytes (PNG magic header)."""
    analyzer = CompositionAnalyzer()
    inp = CompositionInput(image=centered_subject)
    out = analyzer.safe_execute(inp)

    assert out.evidence is not None, "evidence should not be None"
    assert out.evidence.annotated_image is not None, "evidence.annotated_image should not be None"
    # PNG magic bytes: \x89PNG\r\n\x1a\n
    assert out.evidence.annotated_image[:4] == b"\x89PNG", (
        "evidence.annotated_image must start with PNG magic bytes"
    )


def test_composition_replaces_declaration():
    """CompositionAnalyzer.replaces must equal {'evaluate': ['L1']} and category == COMPOSITION."""
    assert CompositionAnalyzer.replaces == {"evaluate": ["L1"]}, (
        f"Expected replaces == {{'evaluate': ['L1']}}, got {CompositionAnalyzer.replaces}"
    )
    assert CompositionAnalyzer.category == ToolCategory.COMPOSITION, (
        f"Expected category == COMPOSITION, got {CompositionAnalyzer.category}"
    )
