"""Tests for evolution guard: require real human feedback before evolving."""
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from app.prototype.digestion.context_evolver import ContextEvolver, EvolutionResult


def _make_store(sessions: list[dict]) -> MagicMock:
    """Create a mock SessionStore with given sessions."""
    store = MagicMock()
    store.count.return_value = len(sessions)
    store.get_all.return_value = sessions
    return store


def _make_context_file(tmp_path: Path) -> Path:
    ctx_path = tmp_path / "evolved_context.json"
    ctx_path.write_text(json.dumps({
        "evolutions": 0,
        "tradition_weights": {
            "chinese_xieyi": {
                "visual_perception": 0.2,
                "technical_analysis": 0.2,
                "cultural_context": 0.2,
                "critical_interpretation": 0.2,
                "philosophical_aesthetic": 0.2,
            }
        },
        "cultures": {},
        "few_shot_examples": {},
        "tradition_insights": {},
    }))
    return ctx_path


class TestEvolutionGuard:
    """Evolution should not run without real human feedback."""

    def test_skips_when_no_human_feedback(self, tmp_path):
        """10 sessions but 0 human feedback → skip evolution."""
        sessions = [
            {"session_id": f"api-{i}", "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.8, "L2": 0.7, "L3": 0.6, "L4": 0.5, "L5": 0.5}}
            for i in range(10)
        ]
        store = _make_store(sessions)
        ctx_path = _make_context_file(tmp_path)

        evolver = ContextEvolver(store=store, context_path=str(ctx_path))
        result = evolver.evolve()

        assert result.skipped_reason != ""
        assert "feedback" in result.skipped_reason.lower() or "human" in result.skipped_reason.lower()

    def test_runs_when_human_feedback_present(self, tmp_path):
        """10 sessions with 3 having explicit feedback → allow evolution."""
        sessions = [
            {"session_id": f"api-{i}", "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.8, "L2": 0.7, "L3": 0.6, "L4": 0.5, "L5": 0.5},
             "user_feedback": "accepted" if i < 3 else ""}
            for i in range(10)
        ]
        store = _make_store(sessions)
        ctx_path = _make_context_file(tmp_path)

        evolver = ContextEvolver(store=store, context_path=str(ctx_path))
        result = evolver.evolve()

        # Should not be skipped for feedback reasons
        assert "feedback" not in (result.skipped_reason or "").lower()

    def test_skips_when_only_seed_feedback(self, tmp_path):
        """Sessions from seed scripts (seed-*) should not count as real feedback."""
        sessions = [
            {"session_id": f"seed-{i}", "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.8, "L2": 0.7, "L3": 0.6, "L4": 0.5, "L5": 0.5},
             "user_feedback": "accepted"}
            for i in range(10)
        ]
        store = _make_store(sessions)
        ctx_path = _make_context_file(tmp_path)

        evolver = ContextEvolver(store=store, context_path=str(ctx_path))
        result = evolver.evolve()

        assert result.skipped_reason != ""

    def test_skips_with_2_feedback_below_threshold(self, tmp_path):
        """2 real feedback sessions (below threshold of 3) → skip."""
        sessions = [
            {"session_id": f"api-{i}", "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.8, "L2": 0.7, "L3": 0.6, "L4": 0.5, "L5": 0.5},
             "user_feedback": "accepted" if i < 2 else ""}
            for i in range(10)
        ]
        store = _make_store(sessions)
        ctx_path = _make_context_file(tmp_path)

        evolver = ContextEvolver(store=store, context_path=str(ctx_path))
        result = evolver.evolve()

        assert result.skipped_reason != ""
        assert "feedback" in result.skipped_reason.lower()

    def test_counts_rejected_as_human_feedback(self, tmp_path):
        """'rejected' feedback also counts as real human feedback."""
        sessions = [
            {"session_id": f"api-{i}", "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.8, "L2": 0.7, "L3": 0.6, "L4": 0.5, "L5": 0.5},
             "user_feedback": "rejected" if i < 3 else ""}
            for i in range(10)
        ]
        store = _make_store(sessions)
        ctx_path = _make_context_file(tmp_path)

        evolver = ContextEvolver(store=store, context_path=str(ctx_path))
        result = evolver.evolve()

        # 3 rejected = 3 real human feedback → should proceed
        assert "feedback" not in (result.skipped_reason or "").lower()

    def test_mixed_seed_and_real_only_counts_real(self, tmp_path):
        """Mix of seed + real: only non-seed feedback counts."""
        sessions = [
            # 5 seed sessions with feedback — should NOT count
            {"session_id": f"seed-{i}", "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.8, "L2": 0.7, "L3": 0.6, "L4": 0.5, "L5": 0.5},
             "user_feedback": "accepted"}
            for i in range(5)
        ] + [
            # 2 real sessions with feedback — below threshold
            {"session_id": f"api-{i}", "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.8, "L2": 0.7, "L3": 0.6, "L4": 0.5, "L5": 0.5},
             "user_feedback": "accepted"}
            for i in range(2)
        ] + [
            # 3 real sessions without feedback
            {"session_id": f"api-{i+10}", "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.7, "L2": 0.6, "L3": 0.5, "L4": 0.5, "L5": 0.5}}
            for i in range(3)
        ]
        store = _make_store(sessions)
        ctx_path = _make_context_file(tmp_path)

        evolver = ContextEvolver(store=store, context_path=str(ctx_path))
        result = evolver.evolve()

        # 5 seed (excluded) + 2 real feedback (below 3) → skip
        assert result.skipped_reason != ""
        assert "feedback" in result.skipped_reason.lower()

    def test_empty_feedback_string_not_counted(self, tmp_path):
        """Empty string feedback should not count as human feedback."""
        sessions = [
            {"session_id": f"api-{i}", "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.8, "L2": 0.7, "L3": 0.6, "L4": 0.5, "L5": 0.5},
             "user_feedback": ""}
            for i in range(10)
        ]
        store = _make_store(sessions)
        ctx_path = _make_context_file(tmp_path)

        evolver = ContextEvolver(store=store, context_path=str(ctx_path))
        result = evolver.evolve()

        assert result.skipped_reason != ""

    def test_weights_unchanged_when_guard_blocks(self, tmp_path):
        """When guard blocks evolution, weights in context file must not change."""
        sessions = [
            {"session_id": f"api-{i}", "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.9, "L2": 0.1, "L3": 0.1, "L4": 0.1, "L5": 0.1}}
            for i in range(10)
        ]
        store = _make_store(sessions)
        ctx_path = _make_context_file(tmp_path)

        # Read weights before
        before = json.loads(ctx_path.read_text())
        before_weights = before["tradition_weights"]["chinese_xieyi"].copy()

        evolver = ContextEvolver(store=store, context_path=str(ctx_path))
        result = evolver.evolve()

        # Read weights after
        after = json.loads(ctx_path.read_text())
        after_weights = after["tradition_weights"]["chinese_xieyi"]

        assert before_weights == after_weights
        assert after["evolutions"] == 0
