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


# --- Step 1.2: Intent Element Extraction (E1-V1, keyword) ---


def test_extract_elements_chinese_needs():
    """'需要竹子和茶壶元素' should extract bamboo and teapot elements."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("画一幅水墨画，需要竹子和茶壶元素")
    phase = IntentPhase()
    phase.parse_intent(b)

    names = [e.name for e in b.elements]
    assert "竹子" in names
    assert "茶壶" in names


def test_extract_elements_english_include():
    """'include mountains and river' should extract those elements."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("an ink painting, include mountains and river")
    phase = IntentPhase()
    phase.parse_intent(b)

    names = [e.name.lower() for e in b.elements]
    assert "mountains" in names
    assert "river" in names


def test_extract_palette_cold_warm():
    """'冷色调' should set palette mood to cold tones."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("一幅冷色调的海洋主题抽象画")
    phase = IntentPhase()
    phase.parse_intent(b)

    assert b.palette.mood, "palette.mood should be set for '冷色调'"
    assert "cold" in b.palette.mood.lower() or "冷" in b.palette.mood


def test_extract_palette_hex_colors():
    """Hex colors like #003366 in intent should be extracted to palette.primary."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("用 #003366 和 #006B5A 配色的抽象画")
    phase = IntentPhase()
    phase.parse_intent(b)

    assert "#003366" in b.palette.primary
    assert "#006B5A" in b.palette.primary or "#006b5a" in b.palette.primary


def test_extract_composition_aspect_ratio():
    """'16:9 横幅' should extract aspect_ratio."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("画一幅 16:9 横幅的风景画")
    phase = IntentPhase()
    phase.parse_intent(b)

    assert b.composition.aspect_ratio == "16:9"


def test_extract_composition_negative_space():
    """'大量留白' should set negative_space."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("水墨山水，要大量留白")
    phase = IntentPhase()
    phase.parse_intent(b)

    assert b.composition.negative_space, "negative_space should be set for '大量留白'"


def test_extract_composition_layout_type():
    """'对角线构图' should set composition.layout."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("对角线构图的动感山水画")
    phase = IntentPhase()
    phase.parse_intent(b)

    assert b.composition.layout, "layout should be set for '对角线构图'"
    assert "diagonal" in b.composition.layout.lower() or "对角" in b.composition.layout
