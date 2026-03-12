"""Tests for Critic evolved context injection.

This file is intentionally SEPARATE from test_critic_rules.py because that
file has an ``autouse=True`` ``_no_evolved_context`` fixture that patches
``_get_evolved_scoring_context`` to return empty data — which would override
the mocks we need here.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from app.prototype.agents.critic_config import DIMENSIONS
from app.prototype.agents.critic_rules import CriticRules, _get_evolved_scoring_context


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_candidate(
    prompt: str = "a simple art piece",
    steps: int = 10,
    sampler: str = "",
    model_ref: str = "",
    image_path: str = "",
) -> dict:
    return {
        "prompt": prompt,
        "steps": steps,
        "sampler": sampler,
        "model_ref": model_ref,
        "image_path": image_path,
    }


def _make_evidence(
    terminology_hits: list | None = None,
    sample_matches: list | None = None,
    taboo_violations: list | None = None,
) -> dict:
    return {
        "terminology_hits": terminology_hits or [],
        "sample_matches": sample_matches or [],
        "taboo_violations": taboo_violations or [],
    }


def _empty_evo() -> dict:
    """Evolved context with no data — no bonuses should apply."""
    return {"focus_points": {}, "evaluation_guidance": {}, "anti_patterns": []}


def _evo_with_focus(*dims: str) -> dict:
    """Evolved context with focus_points for the given dimension names."""
    focus = {d: [f"focus on {d}"] for d in dims}
    return {
        "focus_points": focus,
        "evaluation_guidance": {},
        "anti_patterns": [],
    }


def _evo_with_guidance(**mapping: str) -> dict:
    """Evolved context with evaluation_guidance for the given L-labels."""
    return {
        "focus_points": {},
        "evaluation_guidance": mapping,
        "anti_patterns": [],
    }


# Resolved path to the real evolved_context.json (used by file-level tests)
_DATA_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), os.pardir,
    "app", "prototype", "data", "evolved_context.json",
))


# Baseline candidate + evidence (minimal — triggers only baseline scores)
_BASELINE_CANDIDATE = _make_candidate()
_BASELINE_EVIDENCE = _make_evidence()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def scorer() -> CriticRules:
    return CriticRules()


# ---------------------------------------------------------------------------
# Test 1: Evolved focus bonus per dimension (parameterized L1/L2/L3/L5)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "dim_name, dim_index",
    [
        ("visual_perception", 0),       # L1
        ("technical_analysis", 1),      # L2
        ("cultural_context", 2),        # L3
        ("philosophical_aesthetic", 4), # L5
    ],
    ids=["L1", "L2", "L3", "L5"],
)
def test_evolved_focus_bonus_per_dimension(scorer, dim_name: str, dim_index: int):
    """When evolved focus_points exist for a dimension, a +0.05 bonus is applied.

    L4 (critical_interpretation) has no focus bonus — intentionally excluded.
    """
    # Score WITHOUT evolved focus
    with patch(
        "app.prototype.agents.critic_rules._get_evolved_scoring_context",
        return_value=_empty_evo(),
    ):
        baseline_scores = scorer.score(
            candidate=_BASELINE_CANDIDATE,
            evidence=_BASELINE_EVIDENCE,
            cultural_tradition="default",
            subject="test",
            use_vlm=False,
        )
    baseline_val = baseline_scores[dim_index].score

    # Score WITH evolved focus for this specific dimension only
    with patch(
        "app.prototype.agents.critic_rules._get_evolved_scoring_context",
        return_value=_evo_with_focus(dim_name),
    ):
        evolved_scores = scorer.score(
            candidate=_BASELINE_CANDIDATE,
            evidence=_BASELINE_EVIDENCE,
            cultural_tradition="default",
            subject="test",
            use_vlm=False,
        )
    evolved_val = evolved_scores[dim_index].score

    # The evolved score should be exactly 0.05 higher (focus bonus)
    assert evolved_val == pytest.approx(baseline_val + 0.05, abs=1e-4), (
        f"{dim_name}: expected {baseline_val + 0.05:.4f}, got {evolved_val:.4f}"
    )


# ---------------------------------------------------------------------------
# Test 2: [Evolved] tag appears in rationale when evaluation_guidance exists
# ---------------------------------------------------------------------------

def test_evolved_evaluation_guidance_in_rationale(scorer):
    """When evaluation_guidance is provided, '[Evolved]' appears in rationale text."""
    guidance = {
        "L1": "Look for visual clarity and harmony",
        "L2": "Examine technical execution of textures",
        "L3": "Verify cultural authenticity of elements",
        "L4": "Interpret narrative potential and depth",
        "L5": "Consider philosophical resonance and aesthetics",
    }
    with patch(
        "app.prototype.agents.critic_rules._get_evolved_scoring_context",
        return_value=_evo_with_guidance(**guidance),
    ):
        scores = scorer.score(
            candidate=_BASELINE_CANDIDATE,
            evidence=_BASELINE_EVIDENCE,
            cultural_tradition="default",
            subject="test",
            use_vlm=False,
        )

    # Every dimension should contain [Evolved] in its rationale
    for i, ds in enumerate(scores):
        assert "[Evolved]" in ds.rationale, (
            f"Dimension {ds.dimension} (index {i}) missing [Evolved] tag "
            f"in rationale: {ds.rationale!r}"
        )


# ---------------------------------------------------------------------------
# Test 3: anti_patterns loaded from _get_evolved_scoring_context
# ---------------------------------------------------------------------------

def test_evolved_anti_patterns_loaded():
    """_get_evolved_scoring_context returns anti_patterns from archetypes."""
    fake_ctx = {
        "evolutions": 5,
        "prompt_contexts": {
            "archetypes": [
                {
                    "pattern": "Test Pattern",
                    "traditions": ["chinese_xieyi"],
                    "evaluation_guidance": {},
                    "anti_patterns": [
                        "Over-cluttering the scene",
                        "Using culturally inappropriate colors",
                    ],
                }
            ],
        },
        "layer_focus": {},
        "agent_insights": {},
        "tradition_insights": {},
    }

    # Save and restore original file
    original = None
    if os.path.exists(_DATA_PATH):
        original = Path(_DATA_PATH).read_text(encoding="utf-8")

    try:
        Path(_DATA_PATH).write_text(json.dumps(fake_ctx), encoding="utf-8")
        result = _get_evolved_scoring_context("chinese_xieyi")

        assert "anti_patterns" in result
        assert len(result["anti_patterns"]) == 2
        assert "Over-cluttering the scene" in result["anti_patterns"]
        assert "Using culturally inappropriate colors" in result["anti_patterns"]
    finally:
        if original is not None:
            Path(_DATA_PATH).write_text(original, encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 4: critic insight loaded from agent_insights.critic
# ---------------------------------------------------------------------------

def test_evolved_critic_insight_loaded():
    """agent_insights.critic is read from evolved context and returned."""
    critic_text = "Prioritize evaluating outputs based on philosophical aesthetic"
    fake_ctx = {
        "evolutions": 10,
        "prompt_contexts": {"archetypes": []},
        "layer_focus": {},
        "agent_insights": {
            "critic": critic_text,
        },
        "tradition_insights": {},
    }

    # Save and restore original file
    original = None
    if os.path.exists(_DATA_PATH):
        original = Path(_DATA_PATH).read_text(encoding="utf-8")

    try:
        Path(_DATA_PATH).write_text(json.dumps(fake_ctx), encoding="utf-8")
        result = _get_evolved_scoring_context("default")

        assert "critic_insight" in result
        assert result["critic_insight"] == critic_text
    finally:
        if original is not None:
            Path(_DATA_PATH).write_text(original, encoding="utf-8")


# ---------------------------------------------------------------------------
# Test 5: no evolved data → score equals baseline (no bonus)
# ---------------------------------------------------------------------------

def test_no_evolved_data_no_bonus(scorer):
    """With empty evolution data, score equals baseline (no bonus applied)."""
    # Score with empty evolved context
    with patch(
        "app.prototype.agents.critic_rules._get_evolved_scoring_context",
        return_value=_empty_evo(),
    ):
        scores_empty = scorer.score(
            candidate=_BASELINE_CANDIDATE,
            evidence=_BASELINE_EVIDENCE,
            cultural_tradition="default",
            subject="test",
            use_vlm=False,
        )

    # Score with a FULL evolved context to prove they differ
    full_evo = {
        "focus_points": {
            "visual_perception": ["focus L1"],
            "technical_analysis": ["focus L2"],
            "cultural_context": ["focus L3"],
            "philosophical_aesthetic": ["focus L5"],
        },
        "evaluation_guidance": {
            "L1": "guidance L1",
            "L2": "guidance L2",
            "L3": "guidance L3",
            "L4": "guidance L4",
            "L5": "guidance L5",
        },
        "anti_patterns": ["bad pattern"],
        "critic_insight": "some insight",
    }
    with patch(
        "app.prototype.agents.critic_rules._get_evolved_scoring_context",
        return_value=full_evo,
    ):
        scores_full = scorer.score(
            candidate=_BASELINE_CANDIDATE,
            evidence=_BASELINE_EVIDENCE,
            cultural_tradition="default",
            subject="test",
            use_vlm=False,
        )

    # Empty evo scores should be strictly <= full evo scores for every dimension
    for empty_ds, full_ds in zip(scores_empty, scores_full):
        assert empty_ds.score <= full_ds.score, (
            f"{empty_ds.dimension}: empty={empty_ds.score:.4f} should be <= "
            f"full={full_ds.score:.4f}"
        )

    # No [Evolved] in any rationale when evolved context is empty
    for ds in scores_empty:
        assert "[Evolved]" not in ds.rationale, (
            f"{ds.dimension} should not have [Evolved] with empty evo data: "
            f"{ds.rationale!r}"
        )
