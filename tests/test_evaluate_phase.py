"""Tests for EvaluatePhase -- Brief-based L1-L5 evaluation."""
from __future__ import annotations

import pytest


def test_evaluate_build_brief_prompt():
    """Eval criteria from Brief should be included in the VLM prompt."""
    from vulca.studio.phases.evaluate import EvaluatePhase
    from vulca.studio.brief import Brief

    b = Brief.new("水墨山水")
    b.eval_criteria = {
        "L1": "Mountain-water composition with 20%+ negative space",
        "L2": "Ink brush texture quality and variation",
        "L3": "Fidelity to xieyi tradition techniques",
        "L4": "No cultural misrepresentation",
        "L5": "Convey serene contemplative mood",
    }

    phase = EvaluatePhase()
    prompt = phase.build_eval_prompt(b)

    assert "Mountain-water composition" in prompt
    assert "Ink brush texture" in prompt
    assert "L1" in prompt
    assert "L5" in prompt


def test_evaluate_fallback_without_criteria():
    """Without eval_criteria, should use tradition-based evaluation."""
    from vulca.studio.phases.evaluate import EvaluatePhase
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight

    b = Brief.new("test", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    # No eval_criteria set

    phase = EvaluatePhase()
    prompt = phase.build_eval_prompt(b)

    # Should still produce a valid prompt using tradition
    assert "L1" in prompt
    assert len(prompt) > 50


def test_evaluate_auto_generates_criteria():
    """If Brief has no eval_criteria, EvaluatePhase should auto-generate them."""
    from vulca.studio.phases.evaluate import EvaluatePhase
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight

    b = Brief.new("水墨山水", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.must_have = ["ink texture"]
    assert b.eval_criteria == {}

    phase = EvaluatePhase()
    phase.ensure_eval_criteria(b)

    assert "L1" in b.eval_criteria
    assert len(b.eval_criteria) == 5


@pytest.mark.asyncio
async def test_evaluate_with_mock():
    """EvaluatePhase should return scores even with mock (fallback)."""
    from vulca.studio.phases.evaluate import EvaluatePhase
    from vulca.studio.brief import Brief

    b = Brief.new("test evaluation")
    b.eval_criteria = {f"L{i}": f"Test criterion {i}" for i in range(1, 6)}

    phase = EvaluatePhase()
    # Use a fake image (will trigger fallback/mock scores)
    result = await phase.evaluate(b, image_path="", mock=True)

    assert result is not None
    assert "L1" in result
    assert all(isinstance(result[f"L{i}"], float) for i in range(1, 6))
