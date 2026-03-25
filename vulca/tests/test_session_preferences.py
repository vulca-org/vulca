"""Tests for Layer 1 SessionPreferences — real-time preference accumulation."""
from __future__ import annotations

import pytest


def test_preference_accumulation_from_signals():
    """Signals from actions should accumulate into a SessionPreferences object."""
    from vulca.digestion.preferences import SessionPreferences

    prefs = SessionPreferences()

    prefs.update_from_signal({
        "action": "concept_select",
        "concept_index": 2,
        "total_candidates": 4,
        "had_notes": True,
    })
    prefs.update_from_signal({
        "action": "evaluate",
        "weakest": "L2",
        "strongest": "L5",
        "scores": {"L1": 0.8, "L2": 0.4, "L3": 0.7, "L4": 0.6, "L5": 0.9},
    })

    assert prefs.get("weak_dimension") == "L2"
    assert prefs.get("strong_dimension") == "L5"
    assert prefs.get("concept_position_preference") is not None


def test_preference_applies_to_prompt_builder():
    """SessionPreferences should generate prompt hints for generation."""
    from vulca.digestion.preferences import SessionPreferences

    prefs = SessionPreferences()
    prefs.update_from_signal({
        "action": "evaluate",
        "weakest": "L2",
        "strongest": "L5",
    })
    prefs.update_from_signal({
        "action": "nl_update",
        "fields_changed": ["composition", "composition"],
    })

    hints = prefs.to_prompt_hints()

    assert isinstance(hints, list)
    assert len(hints) >= 1
    # Should mention the weak dimension
    hint_text = " ".join(hints)
    assert "L2" in hint_text or "technical" in hint_text.lower()


def test_preference_confidence_increases():
    """Repeated signals for the same preference should increase confidence."""
    from vulca.digestion.preferences import SessionPreferences

    prefs = SessionPreferences()

    prefs.update_from_signal({"action": "evaluate", "weakest": "L2", "strongest": "L5"})
    c1 = prefs.confidence.get("weak_dimension", 0)

    prefs.update_from_signal({"action": "evaluate", "weakest": "L2", "strongest": "L5"})
    c2 = prefs.confidence.get("weak_dimension", 0)

    assert c2 > c1, f"Confidence should increase: {c1} → {c2}"
