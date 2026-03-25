"""Tests for NL Update parser."""
from __future__ import annotations

import pytest


def test_nl_update_composition():
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    b = Brief.new("水墨山水")
    result = parse_nl_update("把山改得更高更陡", b)

    assert result.rollback_to.value == "concept"
    assert len(result.field_updates) > 0


def test_nl_update_mood():
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    result = parse_nl_update("改成更神秘的氛围", b)

    assert result.rollback_to.value == "intent"
    assert "mood" in result.field_updates


def test_nl_update_add_element():
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    result = parse_nl_update("加入霓虹灯光效果", b)

    assert result.rollback_to.value == "concept"
    assert "elements" in result.field_updates


def test_nl_update_must_avoid():
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    result = parse_nl_update("不要使用矢量风格", b)

    assert result.rollback_to.value == "concept"
    assert "must_avoid" in result.field_updates


def test_nl_update_apply_to_brief():
    from vulca.studio.nl_update import parse_nl_update, apply_update
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    result = parse_nl_update("配色改成暖色调", b)
    apply_update(b, result)

    assert b.updated_at != b.created_at
    assert len(b.updates) >= 1


def test_nl_rollback_deterministic():
    """Rollback phase should be determined by which fields change, not by LLM."""
    from vulca.studio.nl_update import determine_rollback
    from vulca.studio.session import SessionState

    assert determine_rollback(["mood"]) == SessionState.INTENT
    assert determine_rollback(["style_mix"]) == SessionState.INTENT
    assert determine_rollback(["composition"]) == SessionState.CONCEPT
    assert determine_rollback(["elements"]) == SessionState.CONCEPT
    assert determine_rollback(["must_avoid"]) == SessionState.CONCEPT
    assert determine_rollback(["palette"]) == SessionState.CONCEPT
    assert determine_rollback(["eval_criteria"]) == SessionState.EVALUATE


# --- Step 1.4: NL Update Keywords Expansion (E3) ---


def test_parse_add_with_chinese_variants():
    """Chinese add variants (加一, 放一, 画一) should parse as element additions."""
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    variants = ["加一些竹子", "放一棵松树在远处", "画一只鹤"]
    for instruction in variants:
        b = Brief.new("test")
        result = parse_nl_update(instruction, b)
        assert "elements" in result.field_updates, (
            f"'{instruction}' should be parsed as element addition, got {result.field_updates}"
        )


def test_parse_position_keywords():
    """Position words (远处/近处/左边/上方) should be composition, not fallback."""
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    instructions = [
        "在远处加一座山",
        "近处放一条小溪",
        "左边画一棵柳树",
        "上方留更多天空",
    ]
    for instruction in instructions:
        b = Brief.new("test")
        result = parse_nl_update(instruction, b)
        # Should detect composition (position change), not fall through to fallback
        assert "composition" in result.field_updates or "elements" in result.field_updates, (
            f"'{instruction}' not parsed correctly: {result.field_updates}"
        )
        # Should NOT be fallback (confidence should indicate real match)
        assert "(fallback)" not in result.explanation, (
            f"'{instruction}' fell back to default: {result.explanation}"
        )


def test_parse_multi_field_update():
    """A single instruction can update composition + elements simultaneously."""
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    result = parse_nl_update("在远处加一座雪山，配色改成冷色调", b)

    # Should capture multiple fields
    assert len(result.field_updates) >= 2, (
        f"Expected multi-field update, got {result.field_updates}"
    )


def test_no_fallback_for_position_instructions():
    """Instructions with clear position intent should not fall back."""
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    result = parse_nl_update("把前景的石头移到右边", b)

    assert "(fallback)" not in result.explanation, (
        f"Position instruction should not be fallback: {result.explanation}"
    )
