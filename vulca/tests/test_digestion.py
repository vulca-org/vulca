"""Tests for Studio digestion system."""
from __future__ import annotations

import json
import pytest


def test_session_data_save(tmp_path):
    """Digestion should save session data to JSONL."""
    from vulca.digestion.store import StudioStore
    from vulca.studio.brief import Brief
    from vulca.studio.types import GenerationRound

    b = Brief.new("水墨山水")
    b.generations = [GenerationRound(round_num=1, image_path="r1.png",
                                      scores={"L1": 0.8, "L2": 0.7})]

    store = StudioStore(data_dir=tmp_path)
    store.save_session(b, user_feedback="accept")

    sessions = store.load_sessions()
    assert len(sessions) == 1
    assert sessions[0]["brief"]["intent"] == "水墨山水"
    assert sessions[0]["user_feedback"] == "accept"


def test_signal_extraction():
    """Extract learning signals from a completed session."""
    from vulca.digestion.signals import extract_signals
    from vulca.studio.brief import Brief
    from vulca.studio.types import GenerationRound, StyleWeight

    b = Brief.new("test", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.generations = [
        GenerationRound(round_num=1, image_path="r1.png",
                        scores={"L1": 0.9, "L2": 0.5, "L3": 0.8, "L4": 0.7, "L5": 0.6}),
    ]
    b.concept_candidates = ["c1.png", "c2.png", "c3.png", "c4.png"]
    b.selected_concept = "c3.png"

    signals = extract_signals(b, user_feedback="accept")

    assert "concept_preference" in signals
    assert signals["concept_preference"]["selected_index"] == 2  # 0-based
    assert "dimension_difficulty" in signals
    assert signals["dimension_difficulty"]["weakest"] == "L2"
    assert "style_mix" in signals


def test_digestion_multiple_sessions(tmp_path):
    """Store can hold multiple sessions."""
    from vulca.digestion.store import StudioStore
    from vulca.studio.brief import Brief

    store = StudioStore(data_dir=tmp_path)
    for i in range(3):
        b = Brief.new(f"test {i}")
        store.save_session(b, user_feedback="accept")

    sessions = store.load_sessions()
    assert len(sessions) == 3


def test_signal_extraction_no_generations():
    """Signal extraction handles empty generations gracefully."""
    from vulca.digestion.signals import extract_signals
    from vulca.studio.brief import Brief

    b = Brief.new("empty")
    signals = extract_signals(b, user_feedback="quit")

    assert signals["user_feedback"] == "quit"
    assert signals["dimension_difficulty"]["weakest"] is None
