"""Tests for Brief → L1-L5 eval criteria generation."""
from __future__ import annotations

import pytest


def test_eval_criteria_fallback():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.eval_criteria import generate_eval_criteria_sync

    b = Brief.new("水墨山水", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    criteria = generate_eval_criteria_sync(b, use_llm=False)

    assert "L1" in criteria
    assert "L2" in criteria
    assert "L3" in criteria
    assert "L4" in criteria
    assert "L5" in criteria
    assert all(isinstance(v, str) and len(v) > 0 for v in criteria.values())


def test_eval_criteria_with_constraints():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.eval_criteria import generate_eval_criteria_sync

    b = Brief.new("test", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.must_have = ["ink texture", "negative space"]
    b.must_avoid = ["vector style"]
    criteria = generate_eval_criteria_sync(b, use_llm=False)

    all_text = " ".join(criteria.values()).lower()
    assert "ink texture" in all_text or "negative space" in all_text


def test_eval_criteria_empty_brief():
    from vulca.studio.brief import Brief
    from vulca.studio.eval_criteria import generate_eval_criteria_sync

    b = Brief.new("something abstract")
    criteria = generate_eval_criteria_sync(b, use_llm=False)

    assert len(criteria) == 5
    assert all(len(v) > 5 for v in criteria.values())


def test_eval_criteria_freeform_tag():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.eval_criteria import generate_eval_criteria_sync

    b = Brief.new("cyberpunk cityscape", style_mix=[StyleWeight(tag="cyberpunk", weight=1.0)])
    criteria = generate_eval_criteria_sync(b, use_llm=False)

    assert len(criteria) == 5
