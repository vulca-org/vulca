"""Tests for per-action signal extraction."""
from __future__ import annotations

import pytest


def test_signal_from_concept_selection():
    """Selecting a concept should produce a signal with preference data."""
    from vulca.digestion.signals import extract_action_signal
    from vulca.studio.brief import Brief

    b = Brief.new("水墨山水")
    b.concept_candidates = ["concept_a.png", "concept_b.png", "concept_c.png", "concept_d.png"]
    b.selected_concept = "concept_c.png"
    b.concept_notes = "这个构图最好"

    signal = extract_action_signal(b, action="concept_select")

    assert signal["action"] == "concept_select"
    assert signal["session_id"] == b.session_id
    assert signal["concept_index"] == 2  # 0-indexed, concept_c is index 2
    assert signal["had_notes"] is True
    assert signal["total_candidates"] == 4


def test_signal_from_nl_update():
    """NL update should produce a signal with parsed field changes."""
    from vulca.digestion.signals import extract_action_signal
    from vulca.studio.brief import Brief
    from vulca.studio.nl_update import parse_nl_update, apply_update

    b = Brief.new("水墨山水")
    result = parse_nl_update("把山改得更高更陡", b)
    apply_update(b, result)

    signal = extract_action_signal(b, action="nl_update", instruction="把山改得更高更陡")

    assert signal["action"] == "nl_update"
    assert signal["instruction"] == "把山改得更高更陡"
    assert "fields_changed" in signal
    assert len(signal["fields_changed"]) >= 1


def test_signal_deterministic_no_llm():
    """Signal extraction must be deterministic — same input → same output, no LLM."""
    from vulca.digestion.signals import extract_action_signal
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    b.selected_concept = "c1.png"
    b.concept_candidates = ["c1.png", "c2.png"]

    s1 = extract_action_signal(b, action="concept_select")
    s2 = extract_action_signal(b, action="concept_select")

    assert s1 == s2


def test_signal_extracts_preferences():
    """Multiple actions should accumulate into a preference profile."""
    from vulca.digestion.signals import extract_action_signal, accumulate_preferences
    from vulca.studio.brief import Brief
    from vulca.studio.types import GenerationRound

    b = Brief.new("test")
    b.mood = "serene"
    b.concept_candidates = ["c1.png", "c2.png", "c3.png", "c4.png"]
    b.selected_concept = "c3.png"
    b.concept_notes = "more negative space"
    b.generations = [
        GenerationRound(round_num=1, image_path="r1.png", scores={"L1": 0.8, "L2": 0.4, "L3": 0.7, "L4": 0.6, "L5": 0.9}),
    ]

    signals = [
        extract_action_signal(b, action="concept_select"),
        extract_action_signal(b, action="evaluate"),
    ]

    prefs = accumulate_preferences(signals)

    assert "concept_position_preference" in prefs  # Prefers later concepts (index 2/3)
    assert "weak_dimension" in prefs  # L2 is weakest
    assert prefs["weak_dimension"] == "L2"
