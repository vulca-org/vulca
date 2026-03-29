# vulca/tests/golden/test_mock_regression.py
"""L1 Golden Set: Deterministic mock regression for all 13 traditions.

Runs on every CI push. Zero API cost. Asserts exact scores from
vulca.evaluate(mock=True) to detect unintended changes to:
- _mock_scores() algorithm
- Weight computation formula
- EvalResult field structure
- Tradition YAML loading
"""

from __future__ import annotations

import dataclasses

import pytest

import vulca

# -- Golden baseline: verified 2026-03-29 from _mock_scores() MD5 seed --
# Format: (tradition, L1, L2, L3, L4, L5, weighted_total)
MOCK_GOLDEN = [
    ("default",              0.85, 0.80, 0.90, 0.83, 0.88, 0.8545),
    ("chinese_xieyi",        0.81, 0.76, 0.86, 0.79, 0.84, 0.8205),
    ("chinese_gongbi",       0.85, 0.80, 0.90, 0.83, 0.88, 0.849),
    ("japanese_traditional", 0.77, 0.72, 0.82, 0.75, 0.80, 0.7735),
    ("western_academic",     0.82, 0.77, 0.87, 0.80, 0.85, 0.8145),
    ("islamic_geometric",    0.75, 0.70, 0.80, 0.73, 0.78, 0.745),
    ("watercolor",           0.77, 0.72, 0.82, 0.75, 0.80, 0.767),
    ("african_traditional",  0.79, 0.74, 0.84, 0.77, 0.82, 0.7955),
    ("south_asian",          0.74, 0.69, 0.79, 0.72, 0.77, 0.747),
    ("contemporary_art",     0.84, 0.79, 0.89, 0.82, 0.87, 0.8485),
    ("photography",          0.82, 0.77, 0.87, 0.80, 0.85, 0.8165),
    ("brand_design",         0.78, 0.73, 0.83, 0.76, 0.81, 0.776),
    ("ui_ux_design",         0.81, 0.76, 0.86, 0.79, 0.84, 0.805),
]


class TestMockScoresExact:
    """Assert mock scores match known constants exactly."""

    @pytest.mark.parametrize(
        "tradition, L1, L2, L3, L4, L5, total",
        MOCK_GOLDEN,
        ids=[t[0] for t in MOCK_GOLDEN],
    )
    def test_dimension_scores(self, tradition, L1, L2, L3, L4, L5, total):
        result = vulca.evaluate("test.png", tradition=tradition, mock=True)

        assert result.dimensions["L1"] == L1
        assert result.dimensions["L2"] == L2
        assert result.dimensions["L3"] == L3
        assert result.dimensions["L4"] == L4
        assert result.dimensions["L5"] == L5
        assert result.score == pytest.approx(total, abs=0.001)

    @pytest.mark.parametrize(
        "tradition, L1, L2, L3, L4, L5, total",
        MOCK_GOLDEN,
        ids=[t[0] for t in MOCK_GOLDEN],
    )
    def test_convenience_properties(self, tradition, L1, L2, L3, L4, L5, total):
        result = vulca.evaluate("test.png", tradition=tradition, mock=True)

        assert result.L1 == L1
        assert result.L2 == L2
        assert result.L3 == L3
        assert result.L4 == L4
        assert result.L5 == L5


class TestMockFieldIntegrity:
    """Assert EvalResult structural invariants across all traditions."""

    @pytest.mark.parametrize("tradition", [t[0] for t in MOCK_GOLDEN])
    def test_rationales_nonempty(self, tradition):
        result = vulca.evaluate("test.png", tradition=tradition, mock=True)
        for dim in ["L1", "L2", "L3", "L4", "L5"]:
            assert isinstance(result.rationales.get(dim), str)
            assert len(result.rationales[dim]) > 0, f"{dim} rationale is empty"

    @pytest.mark.parametrize("tradition", [t[0] for t in MOCK_GOLDEN])
    def test_deviation_types_traditional(self, tradition):
        result = vulca.evaluate("test.png", tradition=tradition, mock=True)
        for dim in ["L1", "L2", "L3", "L4", "L5"]:
            assert result.deviation_types.get(dim) == "traditional"

    @pytest.mark.parametrize("tradition", [t[0] for t in MOCK_GOLDEN])
    def test_risk_level_valid(self, tradition):
        result = vulca.evaluate("test.png", tradition=tradition, mock=True)
        assert result.risk_level in ("low", "medium", "high")

    @pytest.mark.parametrize("tradition", [t[0] for t in MOCK_GOLDEN])
    def test_eval_mode_strict(self, tradition):
        result = vulca.evaluate("test.png", tradition=tradition, mock=True)
        assert result.eval_mode == "strict"

    @pytest.mark.parametrize("tradition", [t[0] for t in MOCK_GOLDEN])
    def test_suggestions_contain_tradition_name(self, tradition):
        result = vulca.evaluate("test.png", tradition=tradition, mock=True)
        label = tradition.replace("_", " ").title()
        has_match = any(label.lower() in s.lower() for s in result.suggestions.values())
        assert has_match, f"No suggestion contains '{label}'"

    def test_serializable(self):
        result = vulca.evaluate("test.png", tradition="chinese_xieyi", mock=True)
        d = dataclasses.asdict(result)
        assert isinstance(d, dict)
        assert "score" in d
        assert "dimensions" in d
        assert isinstance(d["dimensions"], dict)
