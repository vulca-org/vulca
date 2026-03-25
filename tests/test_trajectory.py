"""Tests for Layer 2 Trajectory Analysis — session completion digestion."""
from __future__ import annotations

import pytest


def test_mood_drift_detection():
    """Detect mood drift between initial intent and final artifact."""
    from vulca.digestion.trajectory import compute_mood_drift

    # Intent mood vs final artifact mood
    drift = compute_mood_drift(
        intent_mood="serene",
        generations_moods=["serene", "dynamic", "dynamic-serene"],
    )

    assert isinstance(drift, float)
    assert 0.0 <= drift <= 1.0
    assert drift > 0.0, "Mood changed from serene to dynamic — drift should be > 0"


def test_mood_drift_zero_when_consistent():
    """No drift when mood is consistent across generations."""
    from vulca.digestion.trajectory import compute_mood_drift

    drift = compute_mood_drift(
        intent_mood="serene",
        generations_moods=["serene", "serene"],
    )
    assert drift == 0.0


def test_cultural_fidelity_calculation():
    """Calculate how well cultural tradition was preserved through pipeline."""
    from vulca.digestion.trajectory import compute_cultural_fidelity

    fidelity = compute_cultural_fidelity(
        intended_traditions=["chinese_xieyi"],
        scores_trajectory=[
            {"L3": 0.8, "L1": 0.7},  # Round 1
            {"L3": 0.75, "L1": 0.8},  # Round 2
            {"L3": 0.7, "L1": 0.85},  # Round 3 — L3 slightly declining
        ],
    )

    assert isinstance(fidelity, float)
    assert 0.0 <= fidelity <= 1.0
    # L3 declined from 0.8 to 0.7, so fidelity should reflect some loss
    assert fidelity < 1.0


def test_composition_preservation_score():
    """Measure how well composition was preserved from concept to final."""
    from vulca.digestion.trajectory import compute_composition_preservation

    score = compute_composition_preservation(
        scores_trajectory=[
            {"L1": 0.9, "L2": 0.5},  # Round 1: strong L1
            {"L1": 0.85, "L2": 0.6},  # Round 2: L1 slightly drops
        ],
    )

    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_session_digest():
    """Produce a full SessionDigest from Brief and scores."""
    from vulca.digestion.trajectory import build_session_digest
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, GenerationRound

    b = Brief.new("水墨山水", mood="serene",
                   style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.generations = [
        GenerationRound(round_num=1, image_path="r1.png",
                       scores={"L1": 0.8, "L2": 0.5, "L3": 0.7, "L4": 0.6, "L5": 0.9}),
        GenerationRound(round_num=2, image_path="r2.png",
                       scores={"L1": 0.85, "L2": 0.6, "L3": 0.65, "L4": 0.7, "L5": 0.85}),
    ]

    digest = build_session_digest(b, user_feedback="accepted")

    assert digest["session_id"] == b.session_id
    assert digest["iteration_count"] == 2
    assert digest["user_feedback"] == "accepted"
    assert "mood_drift" in digest
    assert "cultural_fidelity" in digest
    assert "composition_preservation" in digest
    assert "dimension_difficulty" in digest
    assert digest["dimension_difficulty"]["weakest"] == "L2"
