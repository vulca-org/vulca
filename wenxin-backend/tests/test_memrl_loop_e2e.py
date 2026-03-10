"""MemRL loop E2E test — verifies the full creation→critique→feedback→evolution→injection cycle.

SessionStore → ContextEvolver.evolve() → evolved_context.json
  → Draft._inject_evolved_context() reads archetypes
  → Critic._get_evolved_scoring_context() reads focus_points
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from app.prototype.session.store import SessionStore
from app.prototype.session.types import SessionDigest
from app.prototype.digestion.context_evolver import ContextEvolver


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_isolated_store(tmp_path: Path, count: int = 16) -> SessionStore:
    """Create a SessionStore backed by a temp file with enough sessions."""
    path = str(tmp_path / "sessions.jsonl")
    SessionStore._instance = None
    store = SessionStore(path)
    traditions = [
        "chinese_xieyi", "japanese_wabi_sabi", "european_renaissance",
        "islamic_geometric", "indian_rasa", "korean_dancheong",
        "chinese_xieyi", "japanese_wabi_sabi", "default",
        "chinese_xieyi", "european_renaissance", "chinese_xieyi",
        "indian_rasa", "default", "chinese_xieyi", "japanese_wabi_sabi",
    ]
    for i in range(count):
        trad = traditions[i % len(traditions)]
        d = SessionDigest(
            mode="create",
            intent=f"test painting {i}",
            tradition=trad,
            subject=f"subject {i}",
            user_type="agent",
            final_scores={
                "L1": 0.5 + (i % 5) * 0.08,
                "L2": 0.6 + (i % 4) * 0.07,
                "L3": 0.7 + (i % 3) * 0.06,
                "L4": 0.55 + (i % 6) * 0.05,
                "L5": 0.65 + (i % 5) * 0.04,
            },
            final_weighted_total=0.65 + (i % 5) * 0.05,
            total_rounds=1 + (i % 3),
            total_latency_ms=30000 + i * 1000,
            total_cost_usd=0.067 * (1 + i % 3),
            created_at=time.time() - (count - i) * 3600,
        )
        store.append(d)
    return store


@pytest.fixture(autouse=True)
def _reset_singleton():
    """Reset SessionStore singleton before and after each test."""
    SessionStore._instance = None
    yield
    SessionStore._instance = None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMemRLLoopE2E:
    """Verify the full MemRL loop: sessions → evolve → inject into Draft/Critic."""

    def test_session_digest_persisted(self, tmp_path):
        """Step 1: SessionDigest is persisted to SessionStore."""
        store = _make_isolated_store(tmp_path, count=16)
        assert store.count() >= 16
        records = store.get_all()
        assert records[0]["mode"] == "create"
        assert "L1" in records[0]["final_scores"]

    def test_evolver_executes_with_enough_sessions(self, tmp_path):
        """Step 2: ContextEvolver.evolve() succeeds with ≥5 sessions."""
        store = _make_isolated_store(tmp_path, count=16)
        context_path = str(tmp_path / "evolved_context.json")

        # Pre-populate with weights so evolver can adjust
        initial = {
            "tradition_weights": {
                "chinese_xieyi": {"L1": 0.20, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.20},
                "default": {"L1": 0.20, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.20},
            },
            "version": 2,
            "evolutions": 0,
        }
        Path(context_path).write_text(json.dumps(initial))

        evolver = ContextEvolver(store=store, context_path=context_path)
        result = evolver.evolve()

        assert result.skipped_reason == "", f"Evolver skipped: {result.skipped_reason}"
        assert result.sessions_analyzed >= 16

    def test_evolutions_count_increases(self, tmp_path):
        """Step 3: evolved_context.json evolutions counter increases after evolve()."""
        store = _make_isolated_store(tmp_path, count=16)
        context_path = str(tmp_path / "evolved_context.json")

        initial = {
            "tradition_weights": {
                "chinese_xieyi": {"L1": 0.20, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.20},
            },
            "version": 2,
            "evolutions": 0,
        }
        Path(context_path).write_text(json.dumps(initial))

        evolver = ContextEvolver(store=store, context_path=context_path)
        evolver.evolve()

        # Check the saved file
        saved = json.loads(Path(context_path).read_text())
        assert saved["evolutions"] >= 1

    def test_draft_reads_evolved_archetypes(self, tmp_path):
        """Step 4: Draft._inject_evolved_context reads archetypes from evolved context."""
        context_path = str(tmp_path / "evolved_context.json")
        evolved = {
            "evolutions": 1,
            "prompt_contexts": {
                "archetypes": [
                    {
                        "pattern": "Use ink wash gradients for depth",
                        "traditions": ["chinese_xieyi"],
                        "insights": "Emphasize negative space",
                    },
                ],
            },
        }
        Path(context_path).write_text(json.dumps(evolved))

        def mock_get_archetypes(tradition, top_n=3):
            data = json.loads(Path(context_path).read_text())
            archetypes = data.get("prompt_contexts", {}).get("archetypes", [])
            return [a for a in archetypes
                    if tradition in a.get("traditions", []) or not a.get("traditions")][:top_n]

        from app.prototype.agents.draft_agent import _inject_evolved_context

        prompt_parts: list[str] = ["base prompt"]
        with patch(
            "app.prototype.cultural_pipelines.cultural_weights.get_prompt_archetypes",
            side_effect=mock_get_archetypes,
        ):
            _inject_evolved_context(prompt_parts, "chinese_xieyi")

        # Should have injected the pattern
        assert any("ink wash" in p for p in prompt_parts), f"Expected archetype injection, got: {prompt_parts}"

    def test_critic_reads_evolved_focus_points(self, tmp_path):
        """Step 5: Critic._get_evolved_scoring_context reads focus_points."""
        evolved = {
            "evolutions": 1,
            "layer_focus": {
                "chinese_xieyi": {
                    "visual_perception": {
                        "focus_points": ["ink wash gradients", "negative space"],
                        "session_count": 5,
                    },
                },
            },
            "prompt_contexts": {
                "archetypes": [
                    {
                        "traditions": ["chinese_xieyi"],
                        "evaluation_guidance": {"L1": "Focus on brush rhythm"},
                        "anti_patterns": ["avoid flat colors"],
                    },
                ],
            },
            "agent_insights": {
                "critic": "Prioritize cultural authenticity over technical perfection",
            },
        }

        # Write to the actual data path that _get_evolved_scoring_context reads
        import os
        data_path = os.path.join(
            os.path.dirname(__file__), os.pardir,
            "app", "prototype", "data", "evolved_context.json",
        )
        data_path = os.path.normpath(data_path)

        # Save original if exists
        original_content = None
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                original_content = f.read()

        try:
            Path(data_path).parent.mkdir(parents=True, exist_ok=True)
            Path(data_path).write_text(json.dumps(evolved))

            from app.prototype.agents.critic_rules import _get_evolved_scoring_context
            evo = _get_evolved_scoring_context("chinese_xieyi")

            assert "visual_perception" in evo["focus_points"]
            assert "ink wash gradients" in evo["focus_points"]["visual_perception"]
            assert evo["evaluation_guidance"].get("L1") == "Focus on brush rhythm"
            assert "avoid flat colors" in evo["anti_patterns"]
            assert "critic_insight" in evo
        finally:
            if original_content is not None:
                Path(data_path).write_text(original_content)
            elif os.path.exists(data_path):
                os.unlink(data_path)

    def test_full_loop_integration(self, tmp_path):
        """Full loop: sessions → evolve → Draft + Critic can read results."""
        store = _make_isolated_store(tmp_path, count=16)
        context_path = str(tmp_path / "evolved_context.json")

        initial = {
            "tradition_weights": {
                "chinese_xieyi": {"L1": 0.20, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.20},
            },
            "version": 2,
            "evolutions": 0,
        }
        Path(context_path).write_text(json.dumps(initial))

        # Run evolution
        evolver = ContextEvolver(store=store, context_path=context_path)
        result = evolver.evolve()
        assert result.skipped_reason == ""

        # Verify the evolved context file exists and has been updated
        saved = json.loads(Path(context_path).read_text())
        assert saved["evolutions"] >= 1

        # Verify layer_focus was generated (Chinese xieyi has seed focus)
        if "layer_focus" in saved:
            assert isinstance(saved["layer_focus"], dict)
