"""Tests for ArtifactAnalysis L1-L5 data types."""
from __future__ import annotations

import pytest


def test_l1_analysis_dataclass():
    """L1Analysis should hold visual perception fields."""
    from vulca.digestion.artifact_analysis import L1Analysis

    l1 = L1Analysis(
        composition_type="diagonal",
        focal_points=[{"position": "upper_left", "element": "mountain peak"}],
        negative_space_ratio=0.35,
        depth_layers=["foreground: rocks", "midground: trees", "background: mountains"],
        color_dominance=[{"hex": "#1a1a2e", "area_ratio": 0.4}],
        contrast_level="high",
        balance="balanced",
        visual_flow="diagonal_ascending",
    )

    assert l1.composition_type == "diagonal"
    assert l1.negative_space_ratio == 0.35
    assert len(l1.focal_points) == 1
    assert l1.contrast_level == "high"


def test_l5_analysis_mood_fields():
    """L5Analysis should hold philosophical/emotional fields."""
    from vulca.digestion.artifact_analysis import L5Analysis

    l5 = L5Analysis(
        mood="contemplative-melancholy",
        atmosphere="misty, ethereal",
        emotional_resonance=["solitude", "awe"],
        aesthetic_philosophy="wabi-sabi",
        viewer_experience="draws eye upward",
        beauty_type="sublime",
        emotional_intensity=0.85,
    )

    assert l5.mood == "contemplative-melancholy"
    assert l5.beauty_type == "sublime"
    assert l5.emotional_intensity == 0.85
    assert "solitude" in l5.emotional_resonance


def test_analysis_to_dict_roundtrip():
    """ArtifactAnalysis should serialize to dict and back."""
    from vulca.digestion.artifact_analysis import (
        ArtifactAnalysis, L1Analysis, L2Analysis, L3Analysis, L4Analysis, L5Analysis,
    )

    original = ArtifactAnalysis(
        artifact_id="art-001",
        artifact_type="concept",
        session_id="sess-001",
        l1=L1Analysis(composition_type="centered", negative_space_ratio=0.2),
        l2=L2Analysis(stroke_style="ink_wash", detail_level="refined"),
        l3=L3Analysis(cultural_depth="integrated"),
        l4=L4Analysis(narrative_theme="solitary scholar"),
        l5=L5Analysis(mood="serene", beauty_type="harmonious"),
    )

    d = original.to_dict()
    assert isinstance(d, dict)
    assert d["artifact_id"] == "art-001"
    assert d["l1"]["composition_type"] == "centered"
    assert d["l5"]["mood"] == "serene"

    restored = ArtifactAnalysis.from_dict(d)
    assert restored.artifact_id == original.artifact_id
    assert restored.l1.composition_type == original.l1.composition_type
    assert restored.l5.mood == original.l5.mood


def test_analysis_vlm_prompt_generation():
    """ArtifactAnalysis should generate a VLM analysis prompt."""
    from vulca.digestion.artifact_analysis import ArtifactAnalysis

    prompt = ArtifactAnalysis.build_analysis_prompt(artifact_type="concept", intent="水墨山水")

    assert "L1" in prompt
    assert "L5" in prompt
    assert "JSON" in prompt or "json" in prompt
    assert len(prompt) > 100
