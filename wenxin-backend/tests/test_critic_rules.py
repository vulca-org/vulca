"""Test critic rules."""
from __future__ import annotations

import logging
from unittest.mock import patch

import pytest

from app.prototype.agents.critic_config import CriticConfig, DIMENSIONS
from app.prototype.agents.critic_rules import CriticRules, _CULTURE_KEYWORDS, _IMAGE_BLEND_WEIGHTS

logger = logging.getLogger("vulca")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_EMPTY_EVO = {"focus_points": {}, "evaluation_guidance": {}, "anti_patterns": []}


@pytest.fixture(autouse=True)
def _no_evolved_context():
    """Disable evolved context injection so tests verify rule-based logic only."""
    with patch(
        "app.prototype.agents.critic_rules._get_evolved_scoring_context",
        return_value=_EMPTY_EVO,
    ):
        yield


@pytest.fixture()
def scorer() -> CriticRules:
    return CriticRules()


def _make_candidate(
    prompt: str = "a simple art piece",
    steps: int = 10,
    sampler: str = "",
    model_ref: str = "",
    image_path: str = "",
) -> dict:
    return {
        "prompt": prompt,
        "steps": steps,
        "sampler": sampler,
        "model_ref": model_ref,
        "image_path": image_path,
    }


def _make_evidence(
    terminology_hits: list | None = None,
    sample_matches: list | None = None,
    taboo_violations: list | None = None,
) -> dict:
    return {
        "terminology_hits": terminology_hits or [],
        "sample_matches": sample_matches or [],
        "taboo_violations": taboo_violations or [],
    }


# ---------------------------------------------------------------------------
# L1-L5 base score validation
# ---------------------------------------------------------------------------

class TestBaseScores:
    """Each dimension's base score (minimal candidate, empty evidence) is in expected range."""

    _EXPECTED_BASES: dict[str, float] = {
        "visual_perception": 0.35,
        "technical_analysis": 0.35,
        "cultural_context": 0.3,
        "critical_interpretation": 0.6,
        "philosophical_aesthetic": 0.4,
    }

    @pytest.mark.parametrize("dim,expected_base", list(_EXPECTED_BASES.items()))
    def test_base_score(self, scorer: CriticRules, dim: str, expected_base: float) -> None:
        """Minimal candidate with empty evidence should yield the base score
        plus a no-taboo bonus for L3 and L5, but no other bonuses."""
        # Short prompt, 0 steps, no sampler/model_ref, empty evidence
        # Use a prompt that does NOT match any default keywords ("art", "fine art", "museum")
        candidate = _make_candidate(prompt="xyz", steps=0)
        evidence = _make_evidence()
        scores = scorer.score(candidate, evidence, cultural_tradition="default", use_vlm=False)
        score_map = {s.dimension: s.score for s in scores}

        if dim == "cultural_context":
            # L3 gets +0.2 for no_taboo
            assert score_map[dim] == pytest.approx(expected_base + 0.2, abs=1e-6)
        elif dim == "philosophical_aesthetic":
            # L5 gets +0.2 for no_taboo
            assert score_map[dim] == pytest.approx(expected_base + 0.2, abs=1e-6)
        else:
            assert score_map[dim] == pytest.approx(expected_base, abs=1e-6)

    def test_all_five_dimensions_returned(self, scorer: CriticRules) -> None:
        candidate = _make_candidate()
        evidence = _make_evidence()
        scores = scorer.score(candidate, evidence, "default", use_vlm=False)
        assert len(scores) == 5
        dims_returned = [s.dimension for s in scores]
        assert dims_returned == DIMENSIONS


# ---------------------------------------------------------------------------
# Cultural keyword matching bonuses
# ---------------------------------------------------------------------------

class TestCulturalKeywordBonuses:
    """Style keywords for a tradition should add a +0.2 bonus to L1."""

    @pytest.mark.parametrize(
        "tradition,keyword",
        [
            ("chinese_xieyi", "ink"),
            ("chinese_xieyi", "brush"),
            ("chinese_xieyi", "shanshui"),
            ("chinese_gongbi", "gongbi"),
            ("chinese_gongbi", "meticulous"),
            ("western_academic", "chiaroscuro"),
            ("western_academic", "perspective"),
            ("islamic_geometric", "tessellation"),
            ("islamic_geometric", "arabesque"),
            ("watercolor", "watercolor"),
            ("african_traditional", "carved"),
            ("south_asian", "miniature"),
        ],
    )
    def test_style_keyword_bonus_l1(
        self, scorer: CriticRules, tradition: str, keyword: str
    ) -> None:
        # Short prompt (<=50 chars) with just the keyword
        candidate = _make_candidate(prompt=keyword, steps=0)
        evidence = _make_evidence()
        scores = scorer.score(candidate, evidence, tradition, use_vlm=False)
        l1 = next(s for s in scores if s.dimension == "visual_perception")
        # base 0.35 + style_match 0.2 = 0.55
        assert l1.score == pytest.approx(0.55, abs=1e-6)
        assert "traditional style" in l1.rationale

    def test_no_bonus_for_wrong_tradition(self, scorer: CriticRules) -> None:
        """A chinese_xieyi keyword should NOT trigger bonus under western_academic."""
        candidate = _make_candidate(prompt="ink")
        evidence = _make_evidence()
        scores = scorer.score(candidate, evidence, "western_academic", use_vlm=False)
        l1 = next(s for s in scores if s.dimension == "visual_perception")
        # "ink" is not a western_academic keyword, so base only
        assert l1.score == pytest.approx(0.35, abs=1e-6)

    def test_chinese_xieyi_keyword_l3_bonus(self, scorer: CriticRules) -> None:
        """When terminology_hits are present (cultural), L3 gets a term bonus."""
        candidate = _make_candidate(prompt="ink wash shanshui")
        evidence = _make_evidence(terminology_hits=["xieyi", "shanshui"])
        scores = scorer.score(candidate, evidence, "chinese_xieyi", use_vlm=False)
        l3 = next(s for s in scores if s.dimension == "cultural_context")
        # base 0.3 + term_hits(2)*0.15=0.3 + no_taboo=0.2 = 0.8
        assert l3.score == pytest.approx(0.8, abs=1e-6)


# ---------------------------------------------------------------------------
# VLM blend weights
# ---------------------------------------------------------------------------

class TestVLMBlendWeights:
    """Verify the _IMAGE_BLEND_WEIGHTS constants match the specification."""

    @pytest.mark.parametrize(
        "dim_key,expected_weight",
        [
            ("L1", 0.5),
            ("L2", 0.2),
            ("L3", 0.4),
            ("L5", 0.4),
        ],
    )
    def test_blend_weight_value(self, dim_key: str, expected_weight: float) -> None:
        assert _IMAGE_BLEND_WEIGHTS[dim_key] == pytest.approx(expected_weight, abs=1e-6)

    def test_l4_not_in_blend_weights(self) -> None:
        """L4 (taboo detection) should NOT have an image blend weight."""
        assert "L4" not in _IMAGE_BLEND_WEIGHTS

    def test_all_blend_weights_in_0_1(self) -> None:
        for key, w in _IMAGE_BLEND_WEIGHTS.items():
            assert 0.0 <= w <= 1.0, f"{key} weight {w} out of [0,1]"


# ---------------------------------------------------------------------------
# Invalid input handling
# ---------------------------------------------------------------------------

class TestInvalidInputs:
    """Empty candidate / empty evidence should not raise and should return sensible defaults."""

    def test_empty_candidate(self, scorer: CriticRules) -> None:
        scores = scorer.score({}, {}, "default", use_vlm=False)
        assert len(scores) == 5
        for s in scores:
            assert 0.0 <= s.score <= 1.0

    def test_empty_evidence(self, scorer: CriticRules) -> None:
        candidate = _make_candidate(prompt="oil painting chiaroscuro perspective classical realism detailed", steps=20, sampler="euler", model_ref="sdxl")
        scores = scorer.score(candidate, {}, "western_academic", use_vlm=False)
        assert len(scores) == 5
        for s in scores:
            assert 0.0 <= s.score <= 1.0

    def test_empty_prompt_empty_evidence(self, scorer: CriticRules) -> None:
        candidate = _make_candidate(prompt="", steps=0)
        scores = scorer.score(candidate, {}, "default", use_vlm=False)
        assert len(scores) == 5
        # All scores should be at or near base
        score_map = {s.dimension: s.score for s in scores}
        # L1 base = 0.35 (no style, no terms, short prompt)
        assert score_map["visual_perception"] == pytest.approx(0.35, abs=1e-6)

    def test_missing_keys_in_candidate(self, scorer: CriticRules) -> None:
        """Candidate dict with no expected keys at all."""
        scores = scorer.score({"unexpected": True}, {"also_unexpected": 42}, "default", use_vlm=False)
        assert len(scores) == 5

    def test_none_taboo_violations_key(self, scorer: CriticRules) -> None:
        """Evidence with missing taboo_violations key should still work."""
        candidate = _make_candidate()
        evidence = {"terminology_hits": [], "sample_matches": []}
        scores = scorer.score(candidate, evidence, "default", use_vlm=False)
        assert len(scores) == 5


# ---------------------------------------------------------------------------
# Parametrized: 3 traditions x 5 dimensions = 15 cases
# ---------------------------------------------------------------------------

_TRADITIONS = ["chinese_xieyi", "western_academic", "islamic_geometric"]

# For each tradition, build a rich candidate that hits style keywords
_TRADITION_PROMPTS: dict[str, str] = {
    "chinese_xieyi": "ink brush xieyi shanshui wash painting with cultural philosophy and aesthetic meaning in traditional style",
    "western_academic": "oil chiaroscuro perspective classical academic realism with cultural philosophy and aesthetic meaning",
    "islamic_geometric": "geometric tessellation arabesque islamic pattern with cultural philosophy and aesthetic tradition heritage",
}


class TestTraditionDimensionMatrix:
    """3 traditions x 5 dimensions = 15 parametrized test cases."""

    @pytest.mark.parametrize("tradition", _TRADITIONS)
    @pytest.mark.parametrize("dim_idx,dim_name", list(enumerate(DIMENSIONS)))
    def test_score_in_valid_range(
        self,
        scorer: CriticRules,
        tradition: str,
        dim_idx: int,
        dim_name: str,
    ) -> None:
        candidate = _make_candidate(
            prompt=_TRADITION_PROMPTS[tradition],
            steps=20,
            sampler="euler_a",
            model_ref="sdxl-turbo",
        )
        evidence = _make_evidence(
            terminology_hits=["term_a", "term_b"],
            sample_matches=["sample_1"],
        )
        scores = scorer.score(candidate, evidence, tradition, use_vlm=False)
        score = scores[dim_idx]

        assert score.dimension == dim_name
        assert 0.0 <= score.score <= 1.0, (
            f"{tradition}/{dim_name}: score {score.score} out of [0,1]"
        )
        assert len(score.rationale) > 0, f"{tradition}/{dim_name}: empty rationale"

    @pytest.mark.parametrize("tradition", _TRADITIONS)
    def test_rich_candidate_l1_higher_than_base(
        self, scorer: CriticRules, tradition: str
    ) -> None:
        """A rich candidate with style keywords should score above L1 base (0.35)."""
        candidate = _make_candidate(
            prompt=_TRADITION_PROMPTS[tradition],
            steps=20,
        )
        evidence = _make_evidence(terminology_hits=["term"])
        scores = scorer.score(candidate, evidence, tradition, use_vlm=False)
        l1 = scores[0]
        assert l1.score > 0.35

    @pytest.mark.parametrize("tradition", _TRADITIONS)
    def test_rich_candidate_l3_higher_than_base(
        self, scorer: CriticRules, tradition: str
    ) -> None:
        """With term hits and no taboo, L3 should be well above base (0.3)."""
        candidate = _make_candidate(prompt=_TRADITION_PROMPTS[tradition])
        evidence = _make_evidence(terminology_hits=["t1", "t2"])
        scores = scorer.score(candidate, evidence, tradition, use_vlm=False)
        l3 = scores[2]
        # base 0.3 + term_bonus(2*0.15=0.3) + no_taboo(0.2) = 0.8
        assert l3.score == pytest.approx(0.8, abs=1e-6)


# ---------------------------------------------------------------------------
# Taboo violation handling (L4 specific)
# ---------------------------------------------------------------------------

class TestTabooViolations:
    """L4 critical_interpretation taboo enforcement."""

    def test_taboo_critical_zeroes_l4(self, scorer: CriticRules) -> None:
        candidate = _make_candidate()
        evidence = _make_evidence(
            taboo_violations=[{"severity": "critical", "term": "forbidden"}]
        )
        scores = scorer.score(candidate, evidence, "default", use_vlm=False)
        l4 = next(s for s in scores if s.dimension == "critical_interpretation")
        assert l4.score == pytest.approx(0.0, abs=1e-6)

    def test_taboo_high_caps_l4(self, scorer: CriticRules) -> None:
        candidate = _make_candidate()
        evidence = _make_evidence(
            taboo_violations=[{"severity": "high", "term": "sensitive"}]
        )
        scores = scorer.score(candidate, evidence, "default", use_vlm=False)
        l4 = next(s for s in scores if s.dimension == "critical_interpretation")
        assert l4.score == pytest.approx(0.3, abs=1e-6)

    def test_taboo_critical_overrides_high(self, scorer: CriticRules) -> None:
        """If both critical and high are present, critical wins (L4 = 0.0)."""
        candidate = _make_candidate()
        evidence = _make_evidence(
            taboo_violations=[
                {"severity": "critical", "term": "forbidden"},
                {"severity": "high", "term": "sensitive"},
            ]
        )
        scores = scorer.score(candidate, evidence, "default", use_vlm=False)
        l4 = next(s for s in scores if s.dimension == "critical_interpretation")
        assert l4.score == pytest.approx(0.0, abs=1e-6)

    def test_taboo_affects_l3_and_l5(self, scorer: CriticRules) -> None:
        """When taboo violations exist, L3 and L5 lose the no_taboo bonus."""
        candidate = _make_candidate(prompt="art")
        evidence = _make_evidence(
            taboo_violations=[{"severity": "low", "term": "minor"}]
        )
        scores = scorer.score(candidate, evidence, "default", use_vlm=False)
        l3 = next(s for s in scores if s.dimension == "cultural_context")
        l5 = next(s for s in scores if s.dimension == "philosophical_aesthetic")
        # L3: base 0.3 only (no no_taboo bonus)
        assert l3.score == pytest.approx(0.3, abs=1e-6)
        # L5: base 0.4 only (no no_taboo bonus)
        assert l5.score == pytest.approx(0.4, abs=1e-6)


# ---------------------------------------------------------------------------
# Bonus stacking / clamp
# ---------------------------------------------------------------------------

class TestBonusStacking:
    """Verify bonuses stack correctly and clamp to [0, 1]."""

    def test_max_l1_clamped_to_1(self, scorer: CriticRules) -> None:
        """Even with all bonuses, L1 should not exceed 1.0."""
        candidate = _make_candidate(
            prompt="ink brush xieyi wash shanshui with lots of cultural detail " * 3,
            steps=20,
        )
        evidence = _make_evidence(terminology_hits=["t1"])
        scores = scorer.score(candidate, evidence, "chinese_xieyi", use_vlm=False)
        l1 = scores[0]
        # base 0.35 + style 0.2 + terms 0.15 + prompt_length 0.15 = 0.85
        assert l1.score == pytest.approx(0.85, abs=1e-6)
        assert l1.score <= 1.0

    def test_max_l4_with_bonuses(self, scorer: CriticRules) -> None:
        """L4 with both term and sample bonuses."""
        candidate = _make_candidate()
        evidence = _make_evidence(
            terminology_hits=["t1"],
            sample_matches=["s1"],
        )
        scores = scorer.score(candidate, evidence, "default", use_vlm=False)
        l4 = next(s for s in scores if s.dimension == "critical_interpretation")
        # base 0.6 + terms 0.2 + samples 0.2 = 1.0
        assert l4.score == pytest.approx(1.0, abs=1e-6)

    def test_l3_term_bonus_capped(self, scorer: CriticRules) -> None:
        """Term bonus in L3 is capped at 0.3 even with many hits."""
        candidate = _make_candidate(prompt="art")
        evidence = _make_evidence(
            terminology_hits=["t1", "t2", "t3", "t4", "t5"],
        )
        scores = scorer.score(candidate, evidence, "default", use_vlm=False)
        l3 = next(s for s in scores if s.dimension == "cultural_context")
        # base 0.3 + term_cap 0.3 + no_taboo 0.2 = 0.8
        assert l3.score == pytest.approx(0.8, abs=1e-6)

    def test_l3_sample_bonus_capped(self, scorer: CriticRules) -> None:
        """Sample match bonus in L3 is capped at 0.2 even with many matches."""
        candidate = _make_candidate(prompt="art")
        evidence = _make_evidence(
            sample_matches=["s1", "s2", "s3", "s4", "s5"],
        )
        scores = scorer.score(candidate, evidence, "default", use_vlm=False)
        l3 = next(s for s in scores if s.dimension == "cultural_context")
        # base 0.3 + sample_cap 0.2 + no_taboo 0.2 = 0.7
        assert l3.score == pytest.approx(0.7, abs=1e-6)


# ---------------------------------------------------------------------------
# CriticConfig
# ---------------------------------------------------------------------------

class TestCriticConfig:
    """Basic CriticConfig validation."""

    def test_default_weights_sum_to_1(self) -> None:
        cfg = CriticConfig()
        total = sum(cfg.weights.values())
        assert abs(total - 1.0) < 1e-6

    def test_weights_auto_normalize(self) -> None:
        cfg = CriticConfig(weights={"visual_perception": 1.0, "technical_analysis": 1.0,
                                     "cultural_context": 1.0, "critical_interpretation": 1.0,
                                     "philosophical_aesthetic": 1.0})
        assert sum(cfg.weights.values()) == pytest.approx(1.0, abs=1e-6)
        assert cfg.weights["visual_perception"] == pytest.approx(0.2, abs=1e-6)

    def test_to_dict(self) -> None:
        cfg = CriticConfig()
        d = cfg.to_dict()
        assert "weights" in d
        assert "pass_threshold" in d
        assert d["pass_threshold"] == 0.4
        assert d["use_vlm"] is True


# ---------------------------------------------------------------------------
# Culture keywords coverage
# ---------------------------------------------------------------------------

class TestCultureKeywords:
    """Verify _CULTURE_KEYWORDS dict has expected traditions."""

    @pytest.mark.parametrize(
        "tradition",
        [
            "chinese_xieyi",
            "chinese_gongbi",
            "western_academic",
            "islamic_geometric",
            "watercolor",
            "african_traditional",
            "south_asian",
            "default",
        ],
    )
    def test_tradition_has_keywords(self, tradition: str) -> None:
        assert tradition in _CULTURE_KEYWORDS
        assert len(_CULTURE_KEYWORDS[tradition]) > 0

    def test_unknown_tradition_falls_back_to_default(self, scorer: CriticRules) -> None:
        """Unknown tradition uses 'default' keywords."""
        candidate = _make_candidate(prompt="fine art museum piece")
        evidence = _make_evidence()
        scores = scorer.score(candidate, evidence, "nonexistent_tradition", use_vlm=False)
        l1 = scores[0]
        # "fine art" and "art" and "museum" are all in default keywords
        assert "traditional style" in l1.rationale
