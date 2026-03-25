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


# --- Step 1.6: Dynamic Questions (E5) ---


def test_no_mood_question_if_mood_already_set():
    """If Brief already has mood, don't ask about mood."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test", mood="serene")
    phase = IntentPhase()
    questions = phase.generate_questions(b)

    fields = [q["field"] for q in questions]
    assert "mood" not in fields


def test_composition_question_when_layout_empty():
    """If composition.layout is empty, should ask composition question."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    # mood is empty → mood question will be asked
    # composition is empty → composition question should be asked
    phase = IntentPhase()
    questions = phase.generate_questions(b)

    fields = [q["field"] for q in questions]
    assert "composition" in fields, f"Expected composition question, got fields: {fields}"


def test_palette_question_when_no_colors():
    """If palette has no colors, should ask palette question."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    phase = IntentPhase()
    questions = phase.generate_questions(b)

    fields = [q["field"] for q in questions]
    assert "palette" in fields, f"Expected palette question, got fields: {fields}"


def test_elements_question_when_no_elements():
    """If no elements, should ask about elements."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    phase = IntentPhase()
    questions = phase.generate_questions(b)

    fields = [q["field"] for q in questions]
    assert "elements" in fields, f"Expected elements question, got fields: {fields}"


def test_max_5_questions():
    """Never generate more than 5 questions."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")  # All fields empty → max questions
    phase = IntentPhase()
    questions = phase.generate_questions(b)

    assert len(questions) <= 5, f"Too many questions: {len(questions)}"


def test_free_text_option_always_present():
    """Every question should include a free-text / custom option."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    phase = IntentPhase()
    questions = phase.generate_questions(b)

    assert len(questions) > 0
    for q in questions:
        labels = q.get("labels", [])
        has_custom = any("自定义" in l or "custom" in l.lower() for l in labels)
        assert has_custom, f"Question '{q['text']}' missing free-text option, labels: {labels}"


# --- Step 1.3: Tradition Keywords Expansion (E4) ---


def test_detect_jiangnan():
    """'江南水乡' should detect chinese_xieyi."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("春天桃花盛开的江南水乡")
    IntentPhase().parse_intent(b)

    traditions = [s.tradition for s in b.style_mix]
    assert "chinese_xieyi" in traditions


def test_detect_zhongguofeng():
    """'中国风' should detect a Chinese tradition."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("中国风的古建筑画")
    IntentPhase().parse_intent(b)

    traditions = [s.tradition for s in b.style_mix]
    assert "chinese_xieyi" in traditions or "chinese_gongbi" in traditions


def test_detect_abstract():
    """'抽象画' should detect contemporary_art."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("一幅抽象画，色彩丰富")
    IntentPhase().parse_intent(b)

    traditions = [s.tradition for s in b.style_mix]
    assert "contemporary_art" in traditions


def test_detect_commercial():
    """'商业设计' / 'brand' should detect brand_design."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("一个商业品牌设计海报")
    IntentPhase().parse_intent(b)

    traditions = [s.tradition for s in b.style_mix]
    assert "brand_design" in traditions


def test_detect_taohua_spring():
    """'桃花' with spring context should detect chinese_xieyi."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    b = Brief.new("春天桃花落英缤纷的山水画")
    IntentPhase().parse_intent(b)

    traditions = [s.tradition for s in b.style_mix]
    assert "chinese_xieyi" in traditions


# --- Step 2.1: LLM Intent Parsing ---


def _make_mock_llm_response(json_content: dict):
    """Helper: create a mock litellm response object."""
    import json

    class _Choice:
        def __init__(self, text):
            self.message = type("Msg", (), {"content": text})()

    class _Response:
        def __init__(self, text):
            self.choices = [_Choice(text)]

    return _Response(json.dumps(json_content, ensure_ascii=False))


@pytest.mark.asyncio
async def test_intent_llm_extracts_all_fields(monkeypatch):
    """LLM intent parsing should extract mood, elements, palette, composition from free text."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    # Mock LLM returns structured JSON
    mock_response = _make_mock_llm_response({
        "mood": "serene-contemplative",
        "style_mix": [{"tradition": "chinese_xieyi", "weight": 1.0}],
        "elements": [
            {"name": "远山", "category": "subject"},
            {"name": "烟雾", "category": "atmosphere"},
            {"name": "石桥", "category": "subject"},
            {"name": "流水", "category": "subject"},
        ],
        "palette": {"primary": [], "accent": [], "mood": "ink-wash monochrome"},
        "composition": {"layout": "散点透视", "negative_space": "heavy"},
        "must_have": ["留白三成"],
        "must_avoid": [],
    })

    async def fake_acompletion(**kwargs):
        return mock_response

    monkeypatch.setattr("litellm.acompletion", fake_acompletion)

    b = Brief.new("一幅传统水墨山水画，远山含烟，近水有桥，留白三成，散点透视")
    phase = IntentPhase()
    await phase.parse_intent_llm(b)

    # Should extract elements that keyword parsing misses
    element_names = [e.name for e in b.elements]
    assert len(element_names) >= 3, f"Expected 3+ elements, got {element_names}"
    assert any("山" in n for n in element_names)
    assert any("桥" in n or "石桥" in n for n in element_names)

    # Should set mood
    assert b.mood, "mood should be set"

    # Should set composition
    assert b.composition.negative_space, "negative_space should be set"

    # Should set must_have
    assert len(b.must_have) >= 1


@pytest.mark.asyncio
async def test_intent_llm_fallback_to_keyword_on_failure(monkeypatch):
    """If LLM call fails, should fall back to keyword parsing without error."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    async def failing_acompletion(**kwargs):
        raise Exception("API quota exceeded")

    monkeypatch.setattr("litellm.acompletion", failing_acompletion)

    b = Brief.new("赛博朋克水墨山水")
    phase = IntentPhase()
    await phase.parse_intent_llm(b)

    # Should still work via keyword fallback
    traditions = [s.tradition for s in b.style_mix]
    assert "chinese_xieyi" in traditions, "keyword fallback should detect traditions"


@pytest.mark.asyncio
async def test_intent_llm_structured_json_output(monkeypatch):
    """LLM should be called with a system prompt requesting structured JSON."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    captured_kwargs = {}

    async def capture_acompletion(**kwargs):
        captured_kwargs.update(kwargs)
        return _make_mock_llm_response({
            "mood": "warm",
            "style_mix": [],
            "elements": [{"name": "sunset", "category": "subject"}],
            "palette": {"primary": ["#FF6B35"], "mood": "warm tones"},
            "composition": {},
            "must_have": [],
            "must_avoid": [],
        })

    monkeypatch.setattr("litellm.acompletion", capture_acompletion)

    b = Brief.new("a warm sunset painting")
    phase = IntentPhase()
    await phase.parse_intent_llm(b)

    # Should have called litellm with proper structure
    assert "messages" in captured_kwargs
    assert "model" in captured_kwargs
    # System prompt should request JSON output
    system_msg = captured_kwargs["messages"][0]["content"]
    assert "JSON" in system_msg or "json" in system_msg


@pytest.mark.asyncio
async def test_intent_llm_english_implicit_elements(monkeypatch):
    """LLM should extract implicit elements from English text that keyword parsing misses."""
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.brief import Brief

    mock_response = _make_mock_llm_response({
        "mood": "warm-romantic",
        "style_mix": [],
        "elements": [
            {"name": "sunset", "category": "subject"},
            {"name": "ocean", "category": "subject"},
        ],
        "palette": {"primary": ["#FF6B35", "#FF8C42"], "mood": "warm tones"},
        "composition": {},
        "must_have": [],
        "must_avoid": [],
    })

    async def fake_acompletion(**kwargs):
        return mock_response

    monkeypatch.setattr("litellm.acompletion", fake_acompletion)

    b = Brief.new("a beautiful sunset over the ocean with warm colors")
    phase = IntentPhase()
    await phase.parse_intent_llm(b)

    element_names = [e.name.lower() for e in b.elements]
    assert "sunset" in element_names
    assert "ocean" in element_names
