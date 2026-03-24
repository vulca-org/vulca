"""Tests for IntentPhase -- intent parsing and question generation."""
from __future__ import annotations

import pytest


def test_intent_parse_text_only():
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("水墨山水画")
    phase = IntentPhase()
    result = phase.parse_intent(b)

    assert result.intent == "水墨山水画"
    assert len(result.style_mix) >= 0


def test_intent_generate_questions():
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("赛博朋克水墨")
    phase = IntentPhase()
    questions = phase.generate_questions(b)

    assert isinstance(questions, list)
    assert len(questions) >= 1
    for q in questions:
        assert "text" in q
        assert "options" in q


def test_intent_apply_answer():
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("水墨山水")
    phase = IntentPhase()
    questions = phase.generate_questions(b)

    if questions:
        phase.apply_answer(b, questions[0], questions[0]["options"][0])
        assert b.updated_at != b.created_at or b.mood or b.style_mix


def test_intent_with_sketch():
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    phase = IntentPhase()
    phase.set_sketch(b, "path/to/sketch.jpg")
    assert b.user_sketch == "path/to/sketch.jpg"
