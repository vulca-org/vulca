"""Test locked_dimensions behavior in EvaluateNode."""

from __future__ import annotations

import pytest
from vulca.pipeline.nodes.evaluate import EvaluateNode
from vulca.pipeline.node import NodeContext


def _make_ctx(**kwargs) -> NodeContext:
    """Create a NodeContext and optionally seed ctx.data fields.

    Extra keys that are not NodeContext constructor parameters are stored
    via ``ctx.set()`` so they land in ``ctx.data`` where nodes read them.
    """
    # Fields accepted by the NodeContext dataclass directly
    _direct_fields = {
        "subject", "intent", "tradition", "provider", "api_key",
        "round_num", "max_rounds", "cost_usd", "max_cost_usd",
    }
    direct = {k: v for k, v in kwargs.items() if k in _direct_fields}
    extra = {k: v for k, v in kwargs.items() if k not in _direct_fields}

    ctx = NodeContext(**direct)
    for k, v in extra.items():
        ctx.set(k, v)
    return ctx


# ---------------------------------------------------------------------------
# _apply_locked_dimensions (static helper)
# ---------------------------------------------------------------------------

class TestApplyLockedDimensions:
    def test_locked_dims_replaced_with_previous(self):
        new = {"L1": 0.80, "L2": 0.80, "L3": 0.80, "L4": 0.80, "L5": 0.80}
        previous = {"L1": 0.95, "L3": 0.88}
        result = EvaluateNode._apply_locked_dimensions(new, ["L1", "L3"], previous)
        assert result["L1"] == 0.95
        assert result["L3"] == 0.88

    def test_unlocked_dims_unchanged(self):
        new = {"L1": 0.80, "L2": 0.75, "L3": 0.80, "L4": 0.70, "L5": 0.72}
        previous = {"L1": 0.95, "L3": 0.88}
        result = EvaluateNode._apply_locked_dimensions(new, ["L1", "L3"], previous)
        assert result["L2"] == 0.75
        assert result["L4"] == 0.70
        assert result["L5"] == 0.72

    def test_empty_locked_list_is_noop(self):
        new = {"L1": 0.80, "L2": 0.75}
        previous = {"L1": 0.95}
        result = EvaluateNode._apply_locked_dimensions(new, [], previous)
        assert result == new

    def test_locked_dim_absent_in_previous_keeps_new(self):
        """If locked dim has no previous value, leave new score intact."""
        new = {"L1": 0.80, "L2": 0.75}
        previous = {}  # No previous scores at all
        result = EvaluateNode._apply_locked_dimensions(new, ["L1"], previous)
        assert result["L1"] == 0.80

    def test_does_not_mutate_input(self):
        new = {"L1": 0.80}
        previous = {"L1": 0.95}
        result = EvaluateNode._apply_locked_dimensions(new, ["L1"], previous)
        assert new["L1"] == 0.80  # Original unchanged
        assert result["L1"] == 0.95


# ---------------------------------------------------------------------------
# _mock_scores integrates locked_dimensions via ctx.data
# ---------------------------------------------------------------------------

class TestMockScoresLockedDimensions:
    def test_locked_dimensions_preserves_previous_scores(self):
        """Locked dimensions should keep previous round scores."""
        ctx = _make_ctx(
            round_num=2,
            node_params={"evaluate": {"locked_dimensions": ["L1", "L3"]}},
            scores={"L1": 0.95, "L2": 0.70, "L3": 0.88, "L4": 0.65, "L5": 0.72},
        )
        result = EvaluateNode._mock_scores(ctx)
        scores = result["scores"]
        assert scores["L1"] == 0.95, "L1 should be preserved from previous round"
        assert scores["L3"] == 0.88, "L3 should be preserved from previous round"

    def test_unlocked_dims_get_fresh_scores(self):
        """Unlocked dimensions should receive freshly computed scores."""
        ctx = _make_ctx(
            round_num=2,
            node_params={"evaluate": {"locked_dimensions": ["L1"]}},
            scores={"L1": 0.95, "L2": 0.10, "L3": 0.10, "L4": 0.10, "L5": 0.10},
        )
        result = EvaluateNode._mock_scores(ctx)
        scores = result["scores"]
        # Round 2: base = 0.65 + 2*0.05 = 0.75, L2 = 0.75, L3 = 0.85
        assert scores["L2"] > 0.50, "L2 should be fresh mock score, not 0.10"
        assert scores["L3"] > 0.50, "L3 should be fresh mock score, not 0.10"

    def test_no_locked_dimensions_uses_fresh_scores(self):
        """Without locked_dimensions, all scores should be fresh mock values."""
        ctx = _make_ctx(
            round_num=2,
            scores={"L1": 0.50, "L2": 0.50, "L3": 0.50, "L4": 0.50, "L5": 0.50},
        )
        result = EvaluateNode._mock_scores(ctx)
        scores = result["scores"]
        # Round 2: base = 0.75, all mock scores should be > 0.50
        assert all(v > 0.50 for v in scores.values()), (
            "Fresh scores at round 2 should all exceed 0.50"
        )

    def test_locked_dimensions_without_previous_scores(self):
        """If no previous scores exist, locked_dimensions should be a no-op."""
        ctx = _make_ctx(
            round_num=1,
            node_params={"evaluate": {"locked_dimensions": ["L1"]}},
            # No "scores" key in ctx.data
        )
        result = EvaluateNode._mock_scores(ctx)
        assert "scores" in result
        assert "weighted_total" in result
        # L1 should be the fresh mock value (no previous to preserve)
        base = 0.65 + 1 * 0.05
        expected_l1 = min(1.0, base + 0.05)
        assert result["scores"]["L1"] == pytest.approx(expected_l1)

    def test_returns_all_required_keys(self):
        """_mock_scores must always return scores, rationales, weighted_total."""
        ctx = _make_ctx(round_num=1)
        result = EvaluateNode._mock_scores(ctx)
        assert set(result.keys()) >= {"scores", "rationales", "weighted_total"}
        assert set(result["scores"].keys()) == {"L1", "L2", "L3", "L4", "L5"}


# ---------------------------------------------------------------------------
# custom_weights via node_params
# ---------------------------------------------------------------------------

class TestMockScoresCustomWeights:
    def test_custom_weights_applied(self):
        """Custom weights from node_params should be used for weighted_total."""
        ctx = _make_ctx(
            round_num=1,
            node_params={
                "evaluate": {
                    "custom_weights": {
                        "L1": 0.5, "L2": 0.1, "L3": 0.2, "L4": 0.1, "L5": 0.1
                    },
                },
            },
        )
        result = EvaluateNode._mock_scores(ctx)
        assert result["weighted_total"] > 0

        # Verify the weighted total is computed with custom weights, not uniform 0.2
        scores = result["scores"]
        expected = round(
            scores["L1"] * 0.5
            + scores["L2"] * 0.1
            + scores["L3"] * 0.2
            + scores["L4"] * 0.1
            + scores["L5"] * 0.1,
            4,
        )
        assert result["weighted_total"] == pytest.approx(expected)

    def test_uniform_weights_without_custom(self):
        """Without custom_weights, tradition default weights are used."""
        ctx = _make_ctx(round_num=1, tradition="default")
        result = EvaluateNode._mock_scores(ctx)
        scores = result["scores"]
        from vulca.cultural import get_weights
        weights = get_weights("default")
        expected = round(sum(scores[k] * weights.get(k, 0.2) for k in scores), 4)
        assert result["weighted_total"] == pytest.approx(expected)

    def test_round_num_increases_scores(self):
        """Higher round_num should produce higher base mock scores."""
        ctx_r1 = _make_ctx(round_num=1)
        ctx_r3 = _make_ctx(round_num=3)
        r1 = EvaluateNode._mock_scores(ctx_r1)
        r3 = EvaluateNode._mock_scores(ctx_r3)
        assert r3["weighted_total"] > r1["weighted_total"]
