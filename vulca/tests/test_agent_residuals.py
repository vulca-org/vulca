"""Tests for pipeline/residuals.py — AttnRes-inspired agent aggregation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import math
import pytest
from vulca.pipeline.residuals import AgentResiduals, NodeSnapshot, ResidualWeights


class TestNodeSnapshot:
    def test_fields(self):
        snap = NodeSnapshot(node_name="scout", round_num=1,
                            output={"cultural_guidance": "xieyi techniques"},
                            summary="xieyi techniques for ink wash")
        assert snap.node_name == "scout"
        assert snap.round_num == 1


class TestAgentResiduals:
    def setup_method(self):
        self.residuals = AgentResiduals()

    def test_record_snapshot(self):
        snap = self.residuals.record(node_name="scout", round_num=1,
                                     output={"cultural_guidance": "水墨技法：留白、皴法"})
        assert isinstance(snap, NodeSnapshot)
        assert snap.node_name == "scout"
        assert snap.round_num == 1
        assert len(snap.summary) > 0

    def test_record_auto_summary_scout(self):
        snap = self.residuals.record("scout", 1,
                                     {"cultural_guidance": "Xieyi emphasizes spontaneity and ink wash"})
        assert len(snap.summary) > 0

    def test_record_auto_summary_evaluate(self):
        snap = self.residuals.record("evaluate", 1,
                                     {"scores": {"L1": 0.8, "L3": 0.6}, "weighted_total": 0.72})
        assert len(snap.summary) > 0

    def test_compute_weights_uniform_on_empty_brief(self):
        snaps = [
            NodeSnapshot("scout", 1, {}, "scout output"),
            NodeSnapshot("generate", 1, {}, "generate output"),
            NodeSnapshot("evaluate", 1, {}, "evaluate output"),
        ]
        weights = self.residuals.compute_weights("", snaps)
        values = list(weights.weights.values())
        assert all(abs(v - values[0]) < 0.01 for v in values)

    def test_compute_weights_biased_toward_relevant_node(self):
        snaps = [
            NodeSnapshot("scout", 1, {}, "水墨技法 留白 皴法 ink wash"),
            NodeSnapshot("generate", 1, {}, "generated image candidate abc123"),
            NodeSnapshot("evaluate", 1, {}, "L1 0.8 L2 0.7 L3 0.6"),
        ]
        weights = self.residuals.compute_weights("水墨 留白", snaps)
        assert weights.weights["scout"] > weights.weights["generate"]

    def test_residual_weights_sum_to_one(self):
        snaps = [
            NodeSnapshot("scout", 1, {}, "a b c"),
            NodeSnapshot("generate", 1, {}, "d e f"),
            NodeSnapshot("evaluate", 1, {}, "g h i"),
        ]
        weights = self.residuals.compute_weights("test", snaps)
        total = sum(weights.weights.values())
        assert abs(total - 1.0) < 1e-6

    def test_aggregate_preserves_all_node_data(self):
        snaps = [
            NodeSnapshot("scout", 1, {"guidance": "xieyi"}, "scout"),
            NodeSnapshot("generate", 1, {"image": "abc"}, "generate"),
        ]
        weights = ResidualWeights(weights={"scout": 0.6, "generate": 0.4}, method="keyword")
        result = self.residuals.aggregate(weights, snaps)
        assert "node_contributions" in result
        assert result["node_contributions"]["scout"]["guidance"] == "xieyi"
        assert result["node_contributions"]["generate"]["image"] == "abc"

    def test_aggregate_attention_weights(self):
        snaps = [
            NodeSnapshot("scout", 1, {}, "scout"),
            NodeSnapshot("generate", 1, {}, "gen"),
        ]
        weights = ResidualWeights(weights={"scout": 0.7, "generate": 0.3}, method="keyword")
        result = self.residuals.aggregate(weights, snaps)
        assert result["attention_weights"] == {"scout": 0.7, "generate": 0.3}

    def test_aggregate_dominant_node(self):
        snaps = [
            NodeSnapshot("scout", 1, {}, "scout"),
            NodeSnapshot("evaluate", 1, {}, "eval"),
        ]
        weights = ResidualWeights(weights={"scout": 0.3, "evaluate": 0.7}, method="keyword")
        result = self.residuals.aggregate(weights, snaps)
        assert result["dominant_node"] == "evaluate"

    def test_multi_round_accumulates_snapshots(self):
        nodes = ["scout", "generate", "evaluate"]
        for rnd in (1, 2):
            for name in nodes:
                self.residuals.record(name, rnd, {f"{name}_data": rnd})
        snaps = self.residuals.get_history()
        assert len(snaps) == 6

    def test_compute_weights_method_field(self):
        snaps = [NodeSnapshot("scout", 1, {}, "test")]
        weights = self.residuals.compute_weights("test", snaps)
        assert weights.method == "keyword"

    def test_single_snapshot_gets_full_weight(self):
        snaps = [NodeSnapshot("scout", 1, {}, "only node")]
        weights = self.residuals.compute_weights("test", snaps)
        assert abs(weights.weights["scout"] - 1.0) < 1e-6
