"""Feedback → Evolution integration tests.

Verifies the chain: sessions.jsonl (with inline feedback) → FeedbackStore.sync_from_sessions()
→ ContextEvolver.evolve() → evolved_context.json update.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from app.prototype.feedback.feedback_store import FeedbackStore
from app.prototype.session.store import SessionStore
from app.prototype.session.types import SessionDigest
from app.prototype.digestion.context_evolver import ContextEvolver


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Reset both SessionStore and FeedbackStore singletons."""
    SessionStore._instance = None
    FeedbackStore._instance = None
    yield
    SessionStore._instance = None
    FeedbackStore._instance = None


def _write_sessions_with_feedback(tmp_path: Path, count: int = 10) -> Path:
    """Write sessions.jsonl with inline feedback into tmp_path.

    FeedbackStore.sync_from_sessions() reads from self._path.parent / "sessions.jsonl",
    so feedback.jsonl and sessions.jsonl MUST be in the same directory.
    """
    sessions_path = tmp_path / "sessions.jsonl"
    traditions = ["chinese_xieyi", "japanese_wabi_sabi", "european_renaissance", "default"]

    with open(sessions_path, "w", encoding="utf-8") as f:
        for i in range(count):
            trad = traditions[i % len(traditions)]
            # Alternate feedback: thumbs_up for even, thumbs_down for odd
            rating = "thumbs_up" if i % 2 == 0 else "thumbs_down"
            session = {
                "session_id": f"sess-fb-{i:04d}",
                "mode": "create",
                "intent": f"test intent {i}",
                "tradition": trad,
                "subject": f"subject {i}",
                "final_scores": {
                    "L1": 0.5 + (i % 5) * 0.1,
                    "L2": 0.6 + (i % 4) * 0.08,
                    "L3": 0.7 + (i % 3) * 0.06,
                    "L4": 0.55 + (i % 6) * 0.05,
                    "L5": 0.65 + (i % 5) * 0.04,
                },
                "final_weighted_total": 0.65 + (i % 5) * 0.05,
                "total_rounds": 1 + (i % 3),
                "total_latency_ms": 30000 + i * 1000,
                "total_cost_usd": 0.067,
                "created_at": time.time() - (count - i) * 3600,
                "feedback": [{"rating": rating, "comment": f"feedback {i}"}],
                "cultural_features": {},
                "rounds": [],
                "risk_flags": [],
                "recommendations": [],
                "best_image_url": "",
                "user_type": "agent",
                "user_id": "",
                "media_type": "image",
                "critic_insights": [],
                "candidate_choice_index": -1,
                "time_to_select_ms": 0,
                "downloaded": False,
            }
            f.write(json.dumps(session, ensure_ascii=False) + "\n")

    return sessions_path


class TestFeedbackSyncFromSessions:
    """sessions.jsonl with inline feedback → sync → feedback.jsonl."""

    def test_sync_populates_feedback(self, tmp_path):
        """sync_from_sessions() extracts inline feedback from sessions."""
        _write_sessions_with_feedback(tmp_path, count=10)

        # feedback.jsonl must be in the SAME directory as sessions.jsonl
        feedback_path = str(tmp_path / "feedback.jsonl")
        store = FeedbackStore(feedback_path)

        synced = store.sync_from_sessions()
        assert synced == 10  # All 10 sessions have feedback

        # Verify feedback records exist
        stats = store.get_stats()
        assert stats.total_feedback == 10
        assert stats.thumbs_up == 5  # Even indices
        assert stats.thumbs_down == 5  # Odd indices

    def test_sync_idempotent(self, tmp_path):
        """Running sync twice doesn't duplicate feedback."""
        _write_sessions_with_feedback(tmp_path, count=5)

        feedback_path = str(tmp_path / "feedback.jsonl")
        store = FeedbackStore(feedback_path)

        first = store.sync_from_sessions()
        second = store.sync_from_sessions()

        assert first == 5
        assert second == 0  # No new entries
        assert store.get_stats().total_feedback == 5

    def test_sync_handles_missing_sessions(self, tmp_path, monkeypatch):
        """sync_from_sessions() returns 0 when no local sessions exist."""
        feedback_path = str(tmp_path / "feedback.jsonl")
        store = FeedbackStore(feedback_path)

        # Block SessionStore DB fallback so only local JSONL is tested
        import app.prototype.session.store as _ss_mod
        monkeypatch.setattr(_ss_mod.SessionStore, "get", classmethod(lambda cls: (_ for _ in ()).throw(RuntimeError("no DB"))))

        synced = store.sync_from_sessions()
        assert synced == 0


class TestEvolutionAfterFeedbackSync:
    """Full chain: sessions → sync → evolve → evolved_context.json update."""

    def test_full_feedback_evolution_chain(self, tmp_path):
        """Sessions with feedback → sync → evolve → context updated."""
        # Step 1: Write sessions with feedback
        _write_sessions_with_feedback(tmp_path, count=12)

        # Step 2: Set up SessionStore pointing to the same sessions
        session_store = SessionStore(str(tmp_path / "sessions.jsonl"))

        # Step 3: Sync feedback
        feedback_store = FeedbackStore(str(tmp_path / "feedback.jsonl"))
        synced = feedback_store.sync_from_sessions()
        assert synced == 12

        # Step 4: Run evolution
        context_path = str(tmp_path / "evolved_context.json")
        initial = {
            "tradition_weights": {
                "chinese_xieyi": {"L1": 0.20, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.20},
                "default": {"L1": 0.20, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.20},
            },
            "version": 2,
            "evolutions": 0,
        }
        Path(context_path).write_text(json.dumps(initial))

        evolver = ContextEvolver(store=session_store, context_path=context_path)
        result = evolver.evolve()

        assert result.skipped_reason == ""
        assert result.sessions_analyzed >= 12

        # Verify evolved context was saved
        saved = json.loads(Path(context_path).read_text())
        assert saved["evolutions"] >= 1


class TestEvolutionPicksUpFeedbackPreferences:
    """PreferenceLearner detects preference patterns from synced feedback."""

    def test_preference_learner_from_synced_feedback(self, tmp_path):
        """PreferenceLearner finds preferred dimensions from feedback-enriched sessions."""
        from app.prototype.digestion.preference_learner import PreferenceLearner

        # Create sessions with clear preference signal:
        # thumbs_up sessions have HIGH L1, thumbs_down sessions have LOW L1
        sessions_path = tmp_path / "sessions.jsonl"
        with open(sessions_path, "w", encoding="utf-8") as f:
            for i in range(12):
                is_positive = i < 6
                session = {
                    "session_id": f"sess-pref-{i:04d}",
                    "mode": "create",
                    "intent": f"test {i}",
                    "tradition": "chinese_xieyi",
                    "subject": f"subject {i}",
                    "final_scores": {
                        "L1": 0.9 if is_positive else 0.3,
                        "L2": 0.7,
                        "L3": 0.7,
                        "L4": 0.7,
                        "L5": 0.7,
                    },
                    "final_weighted_total": 0.8 if is_positive else 0.5,
                    "total_rounds": 1,
                    "created_at": time.time() - (12 - i) * 3600,
                    "feedback": [
                        {"rating": "thumbs_up" if is_positive else "thumbs_down"}
                    ],
                    "cultural_features": {},
                    "rounds": [],
                    "risk_flags": [],
                    "recommendations": [],
                    "best_image_url": "",
                    "user_type": "agent",
                    "user_id": "",
                    "media_type": "image",
                    "critic_insights": [],
                    "candidate_choice_index": -1,
                    "time_to_select_ms": 0,
                    "downloaded": False,
                    "total_latency_ms": 30000,
                    "total_cost_usd": 0.067,
                }
                f.write(json.dumps(session, ensure_ascii=False) + "\n")

        # Create store and learner
        session_store = SessionStore(str(sessions_path))
        learner = PreferenceLearner(session_store)
        preferences = learner.learn()

        # chinese_xieyi should show L1 as preferred (high in positive, low in negative)
        assert "chinese_xieyi" in preferences
        profile = preferences["chinese_xieyi"]
        assert "L1" in profile.preferred_dimensions, (
            f"Expected L1 in preferred_dimensions, got: {profile.preferred_dimensions}"
        )
        assert profile.total_positive >= 6
        assert profile.total_negative >= 6
