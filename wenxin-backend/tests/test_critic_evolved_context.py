"""Test Critic evolved context injection — SEPARATE from test_critic_rules.py.

test_critic_rules.py has autouse=True fixture that patches out evolved context.
This file tests the evolved context path specifically.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.prototype.agents.critic_config import DIMENSIONS
from app.prototype.agents.critic_rules import CriticRules, _get_evolved_scoring_context


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def scorer() -> CriticRules:
    return CriticRules()


def _make_candidate(prompt: str = "a simple art piece", steps: int = 10) -> dict:
    return {"prompt": prompt, "steps": steps, "sampler": "", "model_ref": ""}


def _empty_evidence() -> dict:
    return {"terminology_hits": [], "sample_matches": [], "taboo_violations": []}


def _make_evo_context(
    focus_dim: str | None = None,
    guidance: dict | None = None,
    anti_patterns: list | None = None,
    critic_insight: str = "",
) -> dict:
    result: dict = {
        "focus_points": {},
        "evaluation_guidance": guidance or {},
        "anti_patterns": anti_patterns or [],
    }
    if focus_dim:
        result["focus_points"] = {focus_dim: [f"Test focus for {focus_dim}"]}
    if critic_insight:
        result["critic_insight"] = critic_insight
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestEvolvedFocusBonusPerDimension:
    """Parameterized: L1/L2/L3/L5 each get +0.05 bonus from focus_points."""

    @pytest.mark.parametrize("dim_name,score_idx", [
        ("visual_perception", 0),     # L1
        ("technical_analysis", 1),    # L2
        ("cultural_context", 2),      # L3
        ("philosophical_aesthetic", 4),  # L5
    ])
    def test_focus_bonus(self, scorer, dim_name, score_idx):
        """Evolved focus_points for {dim_name} add +0.05 to that dimension."""
        evo = _make_evo_context(focus_dim=dim_name)
        no_evo = _make_evo_context()

        candidate = _make_candidate()
        evidence = _empty_evidence()

        with patch(
            "app.prototype.agents.critic_rules._get_evolved_scoring_context",
            return_value=evo,
        ):
            scores_with = scorer.score(candidate, evidence, "chinese_xieyi")

        with patch(
            "app.prototype.agents.critic_rules._get_evolved_scoring_context",
            return_value=no_evo,
        ):
            scores_without = scorer.score(candidate, evidence, "chinese_xieyi")

        delta = scores_with[score_idx].score - scores_without[score_idx].score
        assert abs(delta - 0.05) < 0.001, (
            f"{dim_name}: expected +0.05 delta, got {delta:.4f}"
        )

    def test_l4_no_focus_bonus(self, scorer):
        """L4 (critical_interpretation) does NOT get focus bonus."""
        evo = _make_evo_context(focus_dim="critical_interpretation")
        no_evo = _make_evo_context()

        candidate = _make_candidate()
        evidence = _empty_evidence()

        with patch(
            "app.prototype.agents.critic_rules._get_evolved_scoring_context",
            return_value=evo,
        ):
            scores_with = scorer.score(candidate, evidence, "chinese_xieyi")

        with patch(
            "app.prototype.agents.critic_rules._get_evolved_scoring_context",
            return_value=no_evo,
        ):
            scores_without = scorer.score(candidate, evidence, "chinese_xieyi")

        # L4 is index 3
        delta = scores_with[3].score - scores_without[3].score
        assert abs(delta) < 0.001, f"L4 should have no focus bonus, got delta={delta:.4f}"


class TestEvolvedEvaluationGuidance:
    """Verify [Evolved] guidance appears in rationale."""

    def test_evolved_guidance_in_rationale(self, scorer):
        """Evaluation guidance from archetypes shows as [Evolved] in rationale."""
        evo = _make_evo_context(guidance={
            "L1": "Focus on brush rhythm and negative space",
            "L2": "Check ink consistency and paper texture",
        })

        candidate = _make_candidate()
        evidence = _empty_evidence()

        with patch(
            "app.prototype.agents.critic_rules._get_evolved_scoring_context",
            return_value=evo,
        ):
            scores = scorer.score(candidate, evidence, "chinese_xieyi")

        assert "[Evolved]" in scores[0].rationale  # L1
        assert "[Evolved]" in scores[1].rationale  # L2


class TestEvolvedAntiPatterns:
    """Verify anti_patterns and critic_insight are loaded."""

    def test_anti_patterns_loaded(self):
        """_get_evolved_scoring_context returns anti_patterns from evolved data."""
        import json
        import os
        from pathlib import Path

        evolved_data = {
            "evolutions": 1,
            "layer_focus": {},
            "prompt_contexts": {
                "archetypes": [
                    {
                        "traditions": ["chinese_xieyi"],
                        "evaluation_guidance": {},
                        "anti_patterns": ["avoid flat washes", "no digital artifacts"],
                    },
                ],
            },
        }

        # Write to actual data path
        data_path = os.path.normpath(os.path.join(
            os.path.dirname(__file__), os.pardir,
            "app", "prototype", "data", "evolved_context.json",
        ))
        original = None
        if os.path.exists(data_path):
            original = Path(data_path).read_text()

        try:
            Path(data_path).write_text(json.dumps(evolved_data))
            evo = _get_evolved_scoring_context("chinese_xieyi")
            assert "avoid flat washes" in evo["anti_patterns"]
            assert "no digital artifacts" in evo["anti_patterns"]
        finally:
            if original is not None:
                Path(data_path).write_text(original)
            elif os.path.exists(data_path):
                os.unlink(data_path)

    def test_critic_insight_loaded(self):
        """agent_insights.critic is read into critic_insight."""
        import json
        import os
        from pathlib import Path

        evolved_data = {
            "evolutions": 1,
            "agent_insights": {
                "critic": "Prioritize cultural authenticity over technical perfection",
            },
            "prompt_contexts": {"archetypes": []},
        }

        data_path = os.path.normpath(os.path.join(
            os.path.dirname(__file__), os.pardir,
            "app", "prototype", "data", "evolved_context.json",
        ))
        original = None
        if os.path.exists(data_path):
            original = Path(data_path).read_text()

        try:
            Path(data_path).write_text(json.dumps(evolved_data))
            evo = _get_evolved_scoring_context("chinese_xieyi")
            assert evo.get("critic_insight") == "Prioritize cultural authenticity over technical perfection"
        finally:
            if original is not None:
                Path(data_path).write_text(original)
            elif os.path.exists(data_path):
                os.unlink(data_path)


class TestNoEvolvedDataNoBonus:
    """Empty evolved data → scores equal baseline."""

    def test_no_bonus_with_empty_evo(self, scorer):
        """Zero evolutions → no bonus applied (same as baseline)."""
        empty_evo = {"focus_points": {}, "evaluation_guidance": {}, "anti_patterns": []}

        # Use a prompt that doesn't match any culture keywords
        candidate = _make_candidate(prompt="xyz test")
        evidence = _empty_evidence()

        with patch(
            "app.prototype.agents.critic_rules._get_evolved_scoring_context",
            return_value=empty_evo,
        ):
            scores = scorer.score(candidate, evidence, "nonexistent_tradition")

        # L1 baseline with no bonuses: 0.35 (prompt len ≤ 50, no style match, no terms)
        assert abs(scores[0].score - 0.35) < 0.001
        # No [Evolved] in any rationale
        for s in scores:
            assert "[Evolved]" not in s.rationale
