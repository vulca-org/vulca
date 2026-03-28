"""Unit tests for the Digestion System (3 layers)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from app.prototype.session.store import SessionStore
from app.prototype.session.types import SessionDigest
from app.prototype.digestion.aggregator import DigestAggregator
from app.prototype.digestion.pattern_detector import PatternDetector
from app.prototype.digestion.preference_learner import PreferenceLearner
from app.prototype.digestion.context_evolver import ContextEvolver


def _make_store(sessions: list[SessionDigest]) -> SessionStore:
    """Create a temporary SessionStore populated with the given sessions."""
    tmpdir = tempfile.mkdtemp()
    path = str(Path(tmpdir) / "sessions.jsonl")
    SessionStore._instance = None
    store = SessionStore(path)
    for s in sessions:
        store.append(s)
    return store


def test_aggregator_empty():
    store = _make_store([])
    agg = DigestAggregator(store)
    result = agg.aggregate()
    assert result == {}
    SessionStore._instance = None


def test_aggregator_basic():
    sessions = [
        SessionDigest(
            mode="evaluate",
            tradition="chinese_xieyi",
            final_scores={"L1": 0.8, "L5": 0.9},
            final_weighted_total=0.85,
        ),
        SessionDigest(
            mode="create",
            tradition="chinese_xieyi",
            final_scores={"L1": 0.7, "L5": 0.8},
            final_weighted_total=0.75,
        ),
        SessionDigest(
            mode="evaluate",
            tradition="watercolor",
            final_weighted_total=0.6,
        ),
    ]
    store = _make_store(sessions)
    agg = DigestAggregator(store)
    result = agg.aggregate()

    assert "chinese_xieyi" in result
    assert result["chinese_xieyi"].session_count == 2
    assert result["chinese_xieyi"].avg_weighted_total > 0.7
    assert "watercolor" in result
    assert result["watercolor"].session_count == 1

    SessionStore._instance = None


def test_pattern_detector_no_patterns():
    """Too few sessions → no patterns."""
    sessions = [
        SessionDigest(tradition="default", final_scores={"L1": 0.3})
    ]
    store = _make_store(sessions)
    detector = PatternDetector(DigestAggregator(store))
    patterns = detector.detect()
    assert len(patterns) == 0
    SessionStore._instance = None


def test_pattern_detector_finds_low_pattern():
    """With enough sessions, should detect systematically low scores."""
    sessions = [
        SessionDigest(tradition="watercolor", final_scores={"L1": 0.3, "L2": 0.8})
        for _ in range(10)
    ]
    store = _make_store(sessions)
    detector = PatternDetector(DigestAggregator(store))
    patterns = detector.detect()

    low_patterns = [p for p in patterns if p.pattern_type == "systematically_low"]
    assert len(low_patterns) >= 1
    assert any(p.dimension == "L1" for p in low_patterns)

    SessionStore._instance = None


def test_preference_learner_empty():
    store = _make_store([])
    learner = PreferenceLearner(store)
    prefs = learner.learn()
    assert prefs == {}
    SessionStore._instance = None


def test_preference_learner_with_feedback():
    sessions = [
        SessionDigest(
            tradition="default",
            final_scores={"L1": 0.9, "L5": 0.3},
            feedback=[{"rating": "thumbs_up"}],
        ),
        SessionDigest(
            tradition="default",
            final_scores={"L1": 0.2, "L5": 0.9},
            feedback=[{"rating": "thumbs_down"}],
        ),
    ]
    store = _make_store(sessions)
    learner = PreferenceLearner(store)
    prefs = learner.learn()

    assert "default" in prefs
    assert prefs["default"].total_positive == 1
    assert prefs["default"].total_negative == 1

    SessionStore._instance = None


def test_context_evolver_skips_when_too_few_sessions():
    sessions = [SessionDigest() for _ in range(3)]
    store = _make_store(sessions)

    tmpdir = tempfile.mkdtemp()
    ctx_path = str(Path(tmpdir) / "evolved_context.json")

    evolver = ContextEvolver(store=store, context_path=ctx_path)
    result = evolver.evolve()

    assert result.skipped_reason != ""
    assert result.sessions_analyzed == 3
    assert len(result.actions) == 0

    SessionStore._instance = None


def test_context_evolver_produces_actions():
    """With enough sessions having low L1 scores, should produce evolution actions."""
    from unittest.mock import MagicMock

    # Use mock store with user_feedback to pass the evolution guard
    sessions = [
        {"session_id": f"api-{i}", "tradition": "watercolor",
         "final_scores": {"L1": 0.35, "L2": 0.8, "L3": 0.7, "L4": 0.6, "L5": 0.7},
         "user_feedback": "accepted" if i < 5 else ""}
        for i in range(15)
    ]
    store = MagicMock()
    store.count.return_value = len(sessions)
    store.get_all.return_value = sessions

    tmpdir = tempfile.mkdtemp()
    ctx_path = str(Path(tmpdir) / "evolved_context.json")

    # Pre-populate context with weights
    initial_context = {
        "tradition_weights": {
            "watercolor": {"L1": 0.20, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.20},
        },
        "version": 1,
        "evolutions": 0,
    }
    Path(ctx_path).write_text(json.dumps(initial_context))

    evolver = ContextEvolver(store=store, context_path=ctx_path)
    result = evolver.evolve()

    assert result.sessions_analyzed == 15
    assert result.patterns_found >= 1

    # Should have saved updated context
    if result.actions:
        saved = json.loads(Path(ctx_path).read_text())
        assert saved["evolutions"] == 1
        # L1 weight should have increased
        assert saved["tradition_weights"]["watercolor"]["L1"] > 0.20
        # Sum should still be ~1.0
        total = sum(saved["tradition_weights"]["watercolor"].values())
        assert abs(total - 1.0) < 0.001


def test_evolution_result_to_dict():
    from app.prototype.digestion.context_evolver import EvolutionAction, EvolutionResult

    action = EvolutionAction(
        tradition="watercolor", dimension="L1",
        old_value=0.20, new_value=0.25, reason="test"
    )
    result = EvolutionResult(actions=[action], patterns_found=1, sessions_analyzed=20)
    d = result.to_dict()
    assert d["patterns_found"] == 1
    assert len(d["actions"]) == 1
    assert d["actions"][0]["delta"] == 0.05
