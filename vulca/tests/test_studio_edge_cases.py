"""Edge case tests for Studio V2 — written RED first, then GREEN.

These tests cover gaps found during code review:
1. Brief.update_field with invalid field paths
2. Brief.load with corrupted/incomplete YAML
3. NL Update with empty/edge-case strings
4. StudioSession.load with missing session.yaml
5. EvaluatePhase eval_criteria auto-gen in async context
"""
from __future__ import annotations

import pytest


# ── 1. Brief.update_field validation ──

def test_brief_update_invalid_field_raises():
    """Updating a non-existent top-level field should raise ValueError."""
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    with pytest.raises(ValueError, match="Unknown Brief field"):
        b.update_field("nonexistent_field", "value")


def test_brief_update_invalid_nested_field_raises():
    """Updating a non-existent nested field should raise ValueError."""
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    with pytest.raises(ValueError, match="Unknown nested field"):
        b.update_field("composition.nonexistent", "value")


def test_brief_update_valid_field_works():
    """Valid field updates should still work after validation was added."""
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    b.update_field("mood", "dark")
    assert b.mood == "dark"
    b.update_field("composition.layout", "horizontal")
    assert b.composition.layout == "horizontal"


# ── 2. Brief.load with corrupted YAML ──

def test_brief_load_missing_file(tmp_path):
    """Loading from directory without brief.yaml should raise."""
    from vulca.studio.brief import Brief
    with pytest.raises(FileNotFoundError):
        Brief.load(tmp_path)


def test_brief_load_empty_yaml(tmp_path):
    """Loading empty YAML should not crash."""
    (tmp_path / "brief.yaml").write_text("", encoding="utf-8")
    from vulca.studio.brief import Brief
    # Should either raise or return default Brief (not crash with TypeError)
    try:
        b = Brief.load(tmp_path)
        # If it loads, it should be a valid Brief with defaults
        assert b.version == 1
    except (TypeError, AttributeError):
        pytest.fail("Brief.load crashed on empty YAML instead of handling gracefully")


def test_brief_load_partial_yaml(tmp_path):
    """Loading YAML with only some fields should fill defaults."""
    (tmp_path / "brief.yaml").write_text(
        "session_id: abc\nintent: test\n", encoding="utf-8"
    )
    from vulca.studio.brief import Brief
    b = Brief.load(tmp_path)
    assert b.session_id == "abc"
    assert b.intent == "test"
    assert b.mood == ""  # Default
    assert b.eval_criteria == {}  # Default


# ── 3. NL Update edge cases ──

def test_nl_update_empty_string():
    """Empty instruction should still return a valid result."""
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    result = parse_nl_update("", b)
    assert result.rollback_to is not None
    assert isinstance(result.field_updates, dict)


def test_nl_update_very_long_string():
    """Very long instruction should not crash."""
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    long_text = "加入更多元素 " * 1000
    result = parse_nl_update(long_text, b)
    assert result.rollback_to is not None


def test_nl_update_unicode_characters():
    """Unicode-heavy instructions should work."""
    from vulca.studio.nl_update import parse_nl_update
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    result = parse_nl_update("把背景改成🌸花瓣飘落的效果", b)
    assert result.rollback_to is not None


# ── 4. Session load edge cases ──

def test_session_load_missing_session_yaml(tmp_path):
    """Load session when only brief.yaml exists (no session.yaml)."""
    from vulca.studio.brief import Brief
    from vulca.studio.session import StudioSession, SessionState

    b = Brief.new("test recovery")
    b.save(tmp_path)
    # No session.yaml — should still load, defaulting to INTENT state

    loaded = StudioSession.load(tmp_path)
    assert loaded.state == SessionState.INTENT
    assert loaded.brief.intent == "test recovery"


# ── 5. Digestion signal extraction edge cases ──

def test_signals_with_empty_scores():
    """Signal extraction when generation has empty scores dict."""
    from vulca.digestion.signals import extract_signals
    from vulca.studio.brief import Brief
    from vulca.studio.types import GenerationRound

    b = Brief.new("test")
    b.generations = [GenerationRound(round_num=1, image_path="r1.png", scores={})]
    signals = extract_signals(b, user_feedback="accept")
    assert signals["dimension_difficulty"]["weakest"] is None


def test_signals_with_single_generation():
    """Signal extraction with exactly one generation."""
    from vulca.digestion.signals import extract_signals
    from vulca.studio.brief import Brief
    from vulca.studio.types import GenerationRound

    b = Brief.new("test")
    b.generations = [GenerationRound(
        round_num=1, image_path="r1.png",
        scores={"L1": 1.0, "L2": 0.5, "L3": 0.7, "L4": 0.8, "L5": 0.9}
    )]
    signals = extract_signals(b, user_feedback="accept")
    assert signals["dimension_difficulty"]["weakest"] == "L2"
    assert signals["dimension_difficulty"]["strongest"] == "L1"
