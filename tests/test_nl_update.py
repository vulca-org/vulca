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
