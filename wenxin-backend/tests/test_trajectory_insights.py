"""Tests for trajectory-based learning in ContextEvolver."""

from __future__ import annotations

import json
import os

import pytest


@pytest.fixture()
def trajectory_dir(tmp_path):
    """Create a temporary trajectory directory with test data."""
    traj_dir = tmp_path / "trajectories"
    traj_dir.mkdir()

    # Trajectory 1: accepted after 1 round, chinese_xieyi
    (traj_dir / "traj-001.json").write_text(json.dumps({
        "trajectory_id": "traj-001",
        "subject": "bamboo in mist",
        "tradition": "chinese_xieyi",
        "final_score": 0.82,
        "final_action": "accept",
        "rounds": [
            {
                "round_num": 1,
                "critic_findings": {
                    "layer_scores": {"L1": 0.8, "L2": 0.7, "L3": 0.9, "L4": 0.6, "L5": 0.85},
                    "weighted_score": 0.82,
                },
                "decision": {"action": "accept", "reason": "score above threshold", "round_num": 1, "threshold": 0.7},
            }
        ],
    }))

    # Trajectory 2: rerun then accept, weak L2
    (traj_dir / "traj-002.json").write_text(json.dumps({
        "trajectory_id": "traj-002",
        "subject": "sunset landscape",
        "tradition": "watercolor",
        "final_score": 0.75,
        "final_action": "accept",
        "rounds": [
            {
                "round_num": 1,
                "critic_findings": {
                    "layer_scores": {"L1": 0.6, "L2": 0.3, "L3": 0.7, "L4": 0.5, "L5": 0.6},
                    "weighted_score": 0.54,
                },
                "decision": {"action": "rerun", "reason": "L2 too low", "round_num": 1, "threshold": 0.7},
            },
            {
                "round_num": 2,
                "critic_findings": {
                    "layer_scores": {"L1": 0.7, "L2": 0.6, "L3": 0.8, "L4": 0.6, "L5": 0.75},
                    "weighted_score": 0.75,
                },
                "decision": {"action": "accept", "reason": "improved", "round_num": 2, "threshold": 0.7},
            },
        ],
    }))

    # Trajectory 3: stopped (failed)
    (traj_dir / "traj-003.json").write_text(json.dumps({
        "trajectory_id": "traj-003",
        "subject": "abstract art",
        "tradition": "western_academic",
        "final_score": 0.4,
        "final_action": "stop",
        "rounds": [
            {
                "round_num": 1,
                "critic_findings": {
                    "layer_scores": {"L1": 0.4, "L2": 0.3, "L3": 0.3, "L4": 0.4, "L5": 0.4},
                    "weighted_score": 0.36,
                },
                "decision": {"action": "rerun", "reason": "all low", "round_num": 1, "threshold": 0.7},
            },
            {
                "round_num": 2,
                "critic_findings": {
                    "layer_scores": {"L1": 0.45, "L2": 0.35, "L3": 0.35, "L4": 0.4, "L5": 0.45},
                    "weighted_score": 0.4,
                },
                "decision": {"action": "stop", "reason": "max rounds", "round_num": 2, "threshold": 0.7},
            },
        ],
    }))

    return traj_dir


class TestTrajectoryInsights:
    """Test _extract_trajectory_insights from ContextEvolver."""

    def test_extracts_total_trajectories(self, trajectory_dir, tmp_path):
        """Total trajectory count should match files."""
        from app.prototype.digestion.context_evolver import ContextEvolver
        from app.prototype.session.store import SessionStore

        # Create isolated store with enough sessions
        store = SessionStore(str(tmp_path / "sessions.jsonl"))
        evolver = ContextEvolver(store=store, context_path=str(tmp_path / "ctx.json"))

        # Monkey-patch the trajectory recorder's storage dir
        import app.prototype.trajectory.trajectory_recorder as tr_mod
        original_dir = tr_mod._DEFAULT_STORAGE_DIR
        tr_mod._DEFAULT_STORAGE_DIR = trajectory_dir
        try:
            result = evolver._extract_trajectory_insights()
        finally:
            tr_mod._DEFAULT_STORAGE_DIR = original_dir

        assert result is not None
        assert result["total_trajectories"] == 3

    def test_identifies_weak_dimensions(self, trajectory_dir, tmp_path):
        """Should identify L2 as the most commonly weak dimension."""
        from app.prototype.digestion.context_evolver import ContextEvolver
        from app.prototype.session.store import SessionStore

        store = SessionStore(str(tmp_path / "sessions.jsonl"))
        evolver = ContextEvolver(store=store, context_path=str(tmp_path / "ctx.json"))

        import app.prototype.trajectory.trajectory_recorder as tr_mod
        original_dir = tr_mod._DEFAULT_STORAGE_DIR
        tr_mod._DEFAULT_STORAGE_DIR = trajectory_dir
        try:
            result = evolver._extract_trajectory_insights()
        finally:
            tr_mod._DEFAULT_STORAGE_DIR = original_dir

        assert result is not None
        # L2 appears as weak (<0.5) in traj-002 round1, traj-003 round1, traj-003 round2
        assert "L2" in result["common_weak_dimensions"]

    def test_avg_rounds_to_accept(self, trajectory_dir, tmp_path):
        """Average rounds for accepted trajectories: traj-001=1, traj-002=2 → avg 1.5."""
        from app.prototype.digestion.context_evolver import ContextEvolver
        from app.prototype.session.store import SessionStore

        store = SessionStore(str(tmp_path / "sessions.jsonl"))
        evolver = ContextEvolver(store=store, context_path=str(tmp_path / "ctx.json"))

        import app.prototype.trajectory.trajectory_recorder as tr_mod
        original_dir = tr_mod._DEFAULT_STORAGE_DIR
        tr_mod._DEFAULT_STORAGE_DIR = trajectory_dir
        try:
            result = evolver._extract_trajectory_insights()
        finally:
            tr_mod._DEFAULT_STORAGE_DIR = original_dir

        assert result is not None
        assert result["avg_rounds_to_accept"] == 1.5

    def test_repair_success_rate(self, trajectory_dir, tmp_path):
        """Repair success = L2 improved in traj-002 (0.3→0.6). traj-003 has partial improvement."""
        from app.prototype.digestion.context_evolver import ContextEvolver
        from app.prototype.session.store import SessionStore

        store = SessionStore(str(tmp_path / "sessions.jsonl"))
        evolver = ContextEvolver(store=store, context_path=str(tmp_path / "ctx.json"))

        import app.prototype.trajectory.trajectory_recorder as tr_mod
        original_dir = tr_mod._DEFAULT_STORAGE_DIR
        tr_mod._DEFAULT_STORAGE_DIR = trajectory_dir
        try:
            result = evolver._extract_trajectory_insights()
        finally:
            tr_mod._DEFAULT_STORAGE_DIR = original_dir

        assert result is not None
        assert "repair_success_rate" in result
        assert 0.0 <= result["repair_success_rate"] <= 1.0

    def test_tradition_avg_rounds(self, trajectory_dir, tmp_path):
        """Should have per-tradition round averages."""
        from app.prototype.digestion.context_evolver import ContextEvolver
        from app.prototype.session.store import SessionStore

        store = SessionStore(str(tmp_path / "sessions.jsonl"))
        evolver = ContextEvolver(store=store, context_path=str(tmp_path / "ctx.json"))

        import app.prototype.trajectory.trajectory_recorder as tr_mod
        original_dir = tr_mod._DEFAULT_STORAGE_DIR
        tr_mod._DEFAULT_STORAGE_DIR = trajectory_dir
        try:
            result = evolver._extract_trajectory_insights()
        finally:
            tr_mod._DEFAULT_STORAGE_DIR = original_dir

        assert result is not None
        tradition_rounds = result.get("tradition_avg_rounds", {})
        assert "chinese_xieyi" in tradition_rounds
        assert tradition_rounds["chinese_xieyi"] == 1.0  # 1 round
        assert tradition_rounds["watercolor"] == 2.0  # 2 rounds

    def test_insufficient_trajectories_returns_none(self, tmp_path):
        """Less than 3 trajectories should return None."""
        from app.prototype.digestion.context_evolver import ContextEvolver
        from app.prototype.session.store import SessionStore

        # Create dir with only 1 trajectory
        traj_dir = tmp_path / "sparse_traj"
        traj_dir.mkdir()
        (traj_dir / "traj-solo.json").write_text(json.dumps({
            "trajectory_id": "traj-solo",
            "subject": "test",
            "tradition": "default",
            "final_score": 0.5,
            "final_action": "accept",
            "rounds": [],
        }))

        store = SessionStore(str(tmp_path / "sessions.jsonl"))
        evolver = ContextEvolver(store=store, context_path=str(tmp_path / "ctx.json"))

        import app.prototype.trajectory.trajectory_recorder as tr_mod
        original_dir = tr_mod._DEFAULT_STORAGE_DIR
        tr_mod._DEFAULT_STORAGE_DIR = traj_dir
        try:
            result = evolver._extract_trajectory_insights()
        finally:
            tr_mod._DEFAULT_STORAGE_DIR = original_dir

        assert result is None


class TestCriticSummary:
    """Test human-readable summary generation in CriticRules."""

    def test_dimension_summaries_added(self):
        """Each DimensionScore should have a non-empty summary after scoring."""
        from app.prototype.agents.critic_rules import CriticRules

        rules = CriticRules()
        candidate = {"prompt": "A bamboo painting in ink wash style", "steps": 20, "sampler": "euler", "model_ref": "test"}
        evidence = {"terminology_hits": [{"term": "ink wash"}], "sample_matches": [], "taboo_violations": []}

        scores = rules.score(candidate, evidence, "chinese_xieyi", subject="bamboo", use_vlm=False)

        assert len(scores) == 5
        for ds in scores:
            assert ds.summary, f"Missing summary for {ds.dimension}"
            assert "%" in ds.summary  # Contains score percentage

    def test_evaluation_summary_generated(self):
        """generate_evaluation_summary should produce a non-empty string."""
        from app.prototype.agents.critic_rules import CriticRules
        from app.prototype.agents.critic_types import DimensionScore

        scores = [
            DimensionScore("visual_perception", 0.8, "good visual"),
            DimensionScore("technical_analysis", 0.6, "adequate tech"),
            DimensionScore("cultural_context", 0.9, "strong culture"),
            DimensionScore("critical_interpretation", 0.5, "needs work"),
            DimensionScore("philosophical_aesthetic", 0.7, "decent"),
        ]

        summary = CriticRules.generate_evaluation_summary(scores, "chinese_xieyi")
        assert summary
        assert "chinese xieyi" in summary
        assert "%" in summary
        assert "Strongest" in summary

    def test_score_labels(self):
        """Score labels should map correctly."""
        from app.prototype.agents.critic_rules import CriticRules

        assert CriticRules._score_label(0.9) == "excellent"
        assert CriticRules._score_label(0.7) == "good"
        assert CriticRules._score_label(0.55) == "adequate"
        assert CriticRules._score_label(0.4) == "needs improvement"
        assert CriticRules._score_label(0.2) == "weak"

    def test_empty_scores_summary(self):
        """Empty scores should return empty summary."""
        from app.prototype.agents.critic_rules import CriticRules

        assert CriticRules.generate_evaluation_summary([]) == ""
