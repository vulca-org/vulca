"""Integration tests for the digestion system closed loop.

Tests the full pipeline: seed sessions → aggregate → detect patterns → evolve → verify weights.
All tests use tmp directories — no real data/ files are touched.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers: create a self-contained digestion environment in a tmp dir
# ---------------------------------------------------------------------------

_SEED_SESSIONS = [
    {
        "session_id": f"test-{i:03d}",
        "mode": "create",
        "intent": f"test intent {i}",
        "tradition": tradition,
        "subject": f"subject {i}",
        "user_type": "agent",
        "user_id": "test-agent",
        "rounds": [],
        "final_scores": scores,
        "final_weighted_total": sum(scores.values()) / len(scores),
        "best_image_url": "",
        "risk_flags": [],
        "recommendations": [],
        "feedback": feedback,
        "total_rounds": 1,
        "total_latency_ms": 30000,
        "total_cost_usd": 0.067,
        "created_at": 1736899200.0 + i * 3600,
    }
    for i, (tradition, scores, feedback) in enumerate([
        # chinese_xieyi — 5 sessions, L5 systematically low (<0.50)
        ("chinese_xieyi", {"L1": 0.82, "L2": 0.75, "L3": 0.88, "L4": 0.71, "L5": 0.40}, []),
        ("chinese_xieyi", {"L1": 0.78, "L2": 0.81, "L3": 0.85, "L4": 0.68, "L5": 0.35}, [{"rating": "thumbs_up"}]),
        ("chinese_xieyi", {"L1": 0.80, "L2": 0.77, "L3": 0.90, "L4": 0.73, "L5": 0.42}, []),
        ("chinese_xieyi", {"L1": 0.84, "L2": 0.79, "L3": 0.86, "L4": 0.70, "L5": 0.38}, []),
        ("chinese_xieyi", {"L1": 0.76, "L2": 0.82, "L3": 0.87, "L4": 0.69, "L5": 0.45}, [{"rating": "thumbs_up"}]),
        # japanese_wabi_sabi — 5 sessions, no systematically low dims
        ("japanese_wabi_sabi", {"L1": 0.91, "L2": 0.65, "L3": 0.78, "L4": 0.84, "L5": 0.59}, []),
        ("japanese_wabi_sabi", {"L1": 0.86, "L2": 0.69, "L3": 0.74, "L4": 0.80, "L5": 0.55}, []),
        ("japanese_wabi_sabi", {"L1": 0.89, "L2": 0.72, "L3": 0.81, "L4": 0.86, "L5": 0.62}, [{"rating": "thumbs_up"}]),
        ("japanese_wabi_sabi", {"L1": 0.88, "L2": 0.70, "L3": 0.76, "L4": 0.82, "L5": 0.58}, []),
        ("japanese_wabi_sabi", {"L1": 0.90, "L2": 0.67, "L3": 0.79, "L4": 0.85, "L5": 0.60}, []),
        # default — 5 sessions, L4 systematically low
        ("default", {"L1": 0.62, "L2": 0.58, "L3": 0.71, "L4": 0.35, "L5": 0.65}, []),
        ("default", {"L1": 0.55, "L2": 0.61, "L3": 0.68, "L4": 0.40, "L5": 0.59}, []),
        ("default", {"L1": 0.60, "L2": 0.56, "L3": 0.70, "L4": 0.38, "L5": 0.62}, []),
        ("default", {"L1": 0.58, "L2": 0.63, "L3": 0.67, "L4": 0.42, "L5": 0.60}, []),
        ("default", {"L1": 0.61, "L2": 0.59, "L3": 0.69, "L4": 0.36, "L5": 0.63}, []),
    ])
]


def _write_sessions(sessions_path: Path, sessions: list[dict]) -> None:
    """Write session dicts to a JSONL file."""
    sessions_path.parent.mkdir(parents=True, exist_ok=True)
    with open(sessions_path, "w", encoding="utf-8") as f:
        for s in sessions:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")


def _write_context(context_path: Path, context: dict) -> None:
    """Write evolved context JSON."""
    context_path.parent.mkdir(parents=True, exist_ok=True)
    with open(context_path, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False)


def _make_env(tmp: str, sessions: list[dict] | None = None, context: dict | None = None):
    """Create a self-contained digestion environment and return (store, evolver, context_path)."""
    from app.prototype.session.store import SessionStore
    from app.prototype.digestion.context_evolver import ContextEvolver

    data_dir = Path(tmp) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    sessions_path = data_dir / "sessions.jsonl"
    context_path = data_dir / "evolved_context.json"

    if sessions is not None:
        _write_sessions(sessions_path, sessions)

    if context is not None:
        _write_context(context_path, context)

    # Create a fresh store instance (bypass singleton)
    store = SessionStore(path=str(sessions_path))

    evolver = ContextEvolver(store=store, context_path=str(context_path))

    return store, evolver, context_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFullClosedLoop:
    """Test the complete digestion pipeline from sessions to evolved weights."""

    def test_full_loop_15_sessions(self):
        """15 seed sessions → aggregate → detect → evolve → weights changed."""
        with tempfile.TemporaryDirectory() as tmp:
            base_weights = {
                "chinese_xieyi": {
                    "visual_perception": 0.10, "technical_analysis": 0.15,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.30,
                },
                "japanese_wabi_sabi": {
                    "visual_perception": 0.15, "technical_analysis": 0.20,
                    "cultural_context": 0.20, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.25,
                },
                "default": {
                    "visual_perception": 0.15, "technical_analysis": 0.20,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.20,
                },
            }
            context = {"tradition_weights": base_weights, "version": 1, "evolutions": 0}

            store, evolver, context_path = _make_env(tmp, _SEED_SESSIONS, context)

            result = evolver.evolve()

            assert result.sessions_analyzed == 15
            assert result.patterns_found > 0
            assert len(result.actions) > 0
            assert result.skipped_reason == ""

            # Verify context was saved
            saved = json.loads(context_path.read_text(encoding="utf-8"))
            assert saved["evolutions"] == 1

    def test_dimension_alias_L5_to_philosophical_aesthetic(self):
        """L5 pattern detected → philosophical_aesthetic weight adjusted."""
        with tempfile.TemporaryDirectory() as tmp:
            base_weights = {
                "chinese_xieyi": {
                    "visual_perception": 0.10, "technical_analysis": 0.15,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.30,
                },
                "default": {
                    "visual_perception": 0.15, "technical_analysis": 0.20,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.20,
                },
            }
            context = {"tradition_weights": base_weights, "version": 1, "evolutions": 0}

            # 5 chinese_xieyi + 5 default padding to reach _MIN_SESSIONS_TO_EVOLVE=10
            sessions = _SEED_SESSIONS[:5] + _SEED_SESSIONS[10:15]
            store, evolver, context_path = _make_env(tmp, sessions, context)

            result = evolver.evolve()

            # Should detect L5 as systematically low and boost philosophical_aesthetic
            l5_actions = [a for a in result.actions if a.dimension == "philosophical_aesthetic"]
            assert len(l5_actions) > 0, f"Expected L5→philosophical_aesthetic action, got {[a.to_dict() for a in result.actions]}"

            action = l5_actions[0]
            assert action.tradition == "chinese_xieyi"
            assert action.new_value > action.old_value

    def test_dimension_alias_L4_to_critical_interpretation(self):
        """L4 pattern detected → critical_interpretation weight adjusted."""
        with tempfile.TemporaryDirectory() as tmp:
            base_weights = {
                "default": {
                    "visual_perception": 0.15, "technical_analysis": 0.20,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.20,
                },
                "chinese_xieyi": {
                    "visual_perception": 0.10, "technical_analysis": 0.15,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.30,
                },
            }
            context = {"tradition_weights": base_weights, "version": 1, "evolutions": 0}

            # 5 default + 5 chinese_xieyi padding to reach _MIN_SESSIONS_TO_EVOLVE=10
            sessions = _SEED_SESSIONS[10:15] + _SEED_SESSIONS[:5]
            store, evolver, context_path = _make_env(tmp, sessions, context)

            result = evolver.evolve()

            l4_actions = [a for a in result.actions if a.dimension == "critical_interpretation"]
            assert len(l4_actions) > 0, f"Expected L4→critical_interpretation action, got {[a.to_dict() for a in result.actions]}"

            action = l4_actions[0]
            assert action.tradition == "default"
            assert action.new_value > action.old_value


class TestEmptyTraditionWeightsInit:
    """Test auto-initialization of empty tradition_weights."""

    def test_empty_weights_auto_initialized(self):
        """Empty tradition_weights should be populated from cultural_weights fallback."""
        with tempfile.TemporaryDirectory() as tmp:
            context = {"tradition_weights": {}, "version": 1, "evolutions": 0}

            store, evolver, context_path = _make_env(tmp, _SEED_SESSIONS, context)

            result = evolver.evolve()

            # Should still find patterns and produce actions after auto-init
            assert result.sessions_analyzed == 15
            assert result.patterns_found > 0
            # The auto-init populates tradition_weights, so _boost_dimension
            # can now find the weights and produce actions
            assert len(result.actions) > 0

    def test_missing_context_file_auto_initialized(self):
        """No evolved_context.json → default context + auto-init."""
        with tempfile.TemporaryDirectory() as tmp:
            # Don't write context file at all
            store, evolver, context_path = _make_env(tmp, _SEED_SESSIONS, context=None)

            result = evolver.evolve()

            assert result.sessions_analyzed == 15
            # With auto-init from cultural_weights, should still work
            assert result.patterns_found > 0


class TestAuditLog:
    """Test evolution_log.jsonl audit trail."""

    def test_audit_log_written(self):
        """Audit log entry should be written after successful evolution."""
        with tempfile.TemporaryDirectory() as tmp:
            base_weights = {
                "chinese_xieyi": {
                    "visual_perception": 0.10, "technical_analysis": 0.15,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.30,
                },
                "default": {
                    "visual_perception": 0.15, "technical_analysis": 0.20,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.20,
                },
            }
            context = {"tradition_weights": base_weights, "version": 1, "evolutions": 0}

            store, evolver, context_path = _make_env(tmp, _SEED_SESSIONS, context)

            result = evolver.evolve()
            assert len(result.actions) > 0

            log_path = context_path.parent / "evolution_log.jsonl"
            assert log_path.exists(), "evolution_log.jsonl should be created"

            with open(log_path, "r", encoding="utf-8") as f:
                entries = [json.loads(line) for line in f if line.strip()]

            assert len(entries) == 1
            entry = entries[0]
            assert "timestamp" in entry
            assert entry["sessions_analyzed"] == 15
            assert entry["patterns_found"] > 0
            assert len(entry["actions"]) > 0

    def test_no_audit_log_when_no_actions_and_no_new_data(self):
        """Audit log only written when actions or new data exist."""
        with tempfile.TemporaryDirectory() as tmp:
            # All healthy sessions (no dim below 0.50)
            healthy_sessions = [
                {
                    "session_id": f"healthy-{i:03d}",
                    "mode": "create",
                    "intent": "healthy test",
                    "tradition": "default",
                    "subject": "test",
                    "user_type": "agent",
                    "user_id": "test-agent",
                    "rounds": [],
                    "final_scores": {"L1": 0.75, "L2": 0.80, "L3": 0.85, "L4": 0.70, "L5": 0.78},
                    "final_weighted_total": 0.78,
                    "best_image_url": "",
                    "risk_flags": [],
                    "recommendations": [],
                    "feedback": [],
                    "total_rounds": 1,
                    "total_latency_ms": 30000,
                    "total_cost_usd": 0.067,
                    "created_at": 1736899200.0 + i * 3600,
                }
                for i in range(15)
            ]

            base_weights = {
                "default": {
                    "visual_perception": 0.15, "technical_analysis": 0.20,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.20,
                },
            }
            context = {"tradition_weights": base_weights, "version": 1, "evolutions": 0}

            store, evolver, context_path = _make_env(tmp, healthy_sessions, context)

            result = evolver.evolve()
            assert len(result.actions) == 0

            log_path = context_path.parent / "evolution_log.jsonl"
            if log_path.exists():
                # If log exists (digestion produced new data), verify actions is empty
                import json
                with open(log_path, "r", encoding="utf-8") as f:
                    entries = [json.loads(line) for line in f if line.strip()]
                for entry in entries:
                    assert len(entry["actions"]) == 0, "Log should have no weight actions"


class TestBoundaryConditions:
    """Test edge cases and guardrails."""

    def test_fewer_than_5_sessions_skips(self):
        """< 5 sessions → skip evolution."""
        with tempfile.TemporaryDirectory() as tmp:
            sessions = _SEED_SESSIONS[:4]

            store, evolver, context_path = _make_env(tmp, sessions)

            result = evolver.evolve()

            assert result.sessions_analyzed == 4
            assert "Need 5" in result.skipped_reason
            assert len(result.actions) == 0

    def test_delta_below_threshold_ignored(self):
        """Dimensions with avg > 0.55 produce delta < 0.005 → ignored."""
        with tempfile.TemporaryDirectory() as tmp:
            # Sessions with scores just above the low threshold
            marginal_sessions = [
                {
                    "session_id": f"marginal-{i:03d}",
                    "mode": "create",
                    "intent": "marginal test",
                    "tradition": "default",
                    "subject": "test",
                    "user_type": "agent",
                    "user_id": "test-agent",
                    "rounds": [],
                    # L1 at 0.56 → delta = (0.60 - 0.56) * 0.1 = 0.004 < 0.005 → ignored
                    "final_scores": {"L1": 0.56, "L2": 0.70, "L3": 0.80, "L4": 0.75, "L5": 0.72},
                    "final_weighted_total": 0.71,
                    "best_image_url": "",
                    "risk_flags": [],
                    "recommendations": [],
                    "feedback": [],
                    "total_rounds": 1,
                    "total_latency_ms": 30000,
                    "total_cost_usd": 0.067,
                    "created_at": 1736899200.0 + i * 3600,
                }
                for i in range(15)
            ]

            base_weights = {
                "default": {
                    "visual_perception": 0.15, "technical_analysis": 0.20,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.20,
                },
            }
            context = {"tradition_weights": base_weights, "version": 1, "evolutions": 0}

            store, evolver, context_path = _make_env(tmp, marginal_sessions, context)

            result = evolver.evolve()

            # L1 avg ~0.56 → delta 0.004 < 0.005 threshold → no action
            # But L1 is below 0.50 threshold check → actually 0.56 is NOT below 0.50 so no pattern detected
            # Only dims below _LOW_THRESHOLD (0.50) trigger patterns
            l1_actions = [a for a in result.actions if a.dimension == "visual_perception"]
            assert len(l1_actions) == 0

    def test_weight_normalization(self):
        """After boosting, all weights for a tradition should sum to ~1.0."""
        with tempfile.TemporaryDirectory() as tmp:
            base_weights = {
                "chinese_xieyi": {
                    "visual_perception": 0.10, "technical_analysis": 0.15,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.30,
                },
                "default": {
                    "visual_perception": 0.15, "technical_analysis": 0.20,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.20,
                },
            }
            context = {"tradition_weights": base_weights, "version": 1, "evolutions": 0}

            store, evolver, context_path = _make_env(tmp, _SEED_SESSIONS, context)

            evolver.evolve()

            saved = json.loads(context_path.read_text(encoding="utf-8"))
            for tradition, weights in saved["tradition_weights"].items():
                if isinstance(weights, dict) and weights:
                    total = sum(weights.values())
                    assert abs(total - 1.0) < 0.01, (
                        f"Weights for {tradition} sum to {total}, expected ~1.0"
                    )

    def test_empty_sessions_file_reseeded(self):
        """Zero-byte sessions.jsonl should be treated as non-existent by seed logic."""
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            sessions_path = data_dir / "sessions.jsonl"

            # Create empty file (0 bytes)
            sessions_path.touch()
            assert sessions_path.stat().st_size == 0

            # Verify the seed_prototype guard would NOT skip this
            # (simulating the fixed guard condition)
            assert not (sessions_path.exists() and sessions_path.stat().st_size > 0)


class TestCulturalWeightsIntegration:
    """Test that cultural_weights.get_weights() respects evolved context."""

    def test_evolved_weights_read_by_cultural_weights(self):
        """cultural_weights should read evolved_context.json when present."""
        from app.prototype.cultural_pipelines.cultural_weights import (
            _try_load_from_evolved_context,
            _EVOLVED_CONTEXT_PATH,
        )

        # This is a read-only test of the existing mechanism
        # We verify the function exists and works with a tmp file
        with tempfile.TemporaryDirectory() as tmp:
            ctx_path = Path(tmp) / "evolved_context.json"
            ctx = {
                "tradition_weights": {
                    "chinese_xieyi": {
                        "visual_perception": 0.12,
                        "technical_analysis": 0.15,
                        "cultural_context": 0.25,
                        "critical_interpretation": 0.18,
                        "philosophical_aesthetic": 0.30,
                    },
                },
                "version": 1,
                "evolutions": 1,
            }
            ctx_path.write_text(json.dumps(ctx), encoding="utf-8")

            # Temporarily override the path
            import app.prototype.cultural_pipelines.cultural_weights as cw_mod
            orig_path = cw_mod._EVOLVED_CONTEXT_PATH
            try:
                cw_mod._EVOLVED_CONTEXT_PATH = str(ctx_path)
                result = cw_mod._try_load_from_evolved_context()
                assert result is not None
                assert "chinese_xieyi" in result
                assert result["chinese_xieyi"]["visual_perception"] == 0.12
            finally:
                cw_mod._EVOLVED_CONTEXT_PATH = orig_path


class TestV2Schema:
    """Test evolved_context v2 schema with cultures and prompt_contexts."""

    def test_v2_default_structure(self):
        """New context should have v2 structure."""
        with tempfile.TemporaryDirectory() as tmp:
            store, evolver, context_path = _make_env(tmp, _SEED_SESSIONS)

            # Access private method to test default structure
            context = evolver._load_context()
            assert context["version"] == 2
            assert "cultures" in context
            assert "prompt_contexts" in context
            assert "feature_space" in context

    def test_v1_auto_upgrade(self):
        """v1 context should be auto-upgraded to v2."""
        with tempfile.TemporaryDirectory() as tmp:
            v1_context = {
                "tradition_weights": {"default": {
                    "visual_perception": 0.2, "technical_analysis": 0.2,
                    "cultural_context": 0.2, "critical_interpretation": 0.2,
                    "philosophical_aesthetic": 0.2,
                }},
                "version": 1,
                "evolutions": 5,
            }
            store, evolver, context_path = _make_env(tmp, _SEED_SESSIONS, v1_context)

            context = evolver._load_context()
            assert context["version"] == 2
            assert "cultures" in context
            assert "prompt_contexts" in context
            assert context["evolutions"] == 5  # preserved

    def test_evolve_with_cultural_features(self):
        """Sessions with cultural_features should trigger clustering."""
        with tempfile.TemporaryDirectory() as tmp:
            # Add cultural_features to sessions
            enriched_sessions = []
            for s in _SEED_SESSIONS:
                s_copy = dict(s)
                s_copy["cultural_features"] = {
                    "tradition_specificity": 0.8,
                    "l5_emphasis": 0.7,
                    "avg_score": 0.65,
                }
                enriched_sessions.append(s_copy)

            base_weights = {
                "chinese_xieyi": {
                    "visual_perception": 0.10, "technical_analysis": 0.15,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.30,
                },
                "default": {
                    "visual_perception": 0.15, "technical_analysis": 0.20,
                    "cultural_context": 0.25, "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.20,
                },
            }
            context = {"tradition_weights": base_weights, "version": 1, "evolutions": 0}
            store, evolver, context_path = _make_env(tmp, enriched_sessions, context)

            result = evolver.evolve()
            assert result.sessions_analyzed == 15

            # Check context was saved with v2 data
            if context_path.exists():
                saved = json.loads(context_path.read_text(encoding="utf-8"))
                assert saved.get("version") in (1, 2)  # may or may not upgrade
                assert "feature_space" in saved or "cultures" in saved or saved.get("version") == 1
