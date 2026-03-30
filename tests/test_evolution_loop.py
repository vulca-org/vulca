"""Tests for evolution loop closure — iterations 1-4."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


def _make_decide_ctx(*, tradition="default", weighted_total=0.8, scores=None,
                     round_num=1, max_rounds=3, eval_mode="strict", node_params=None):
    """Create a minimal mock NodeContext for DecideNode tests."""
    from unittest.mock import MagicMock
    ctx = MagicMock()
    ctx.tradition = tradition
    ctx.round_num = round_num
    ctx.max_rounds = max_rounds
    ctx.get = lambda key, default=None: {
        "weighted_total": weighted_total,
        "scores": scores or {},
        "rationales": {},
        "eval_mode": eval_mode,
        "node_params": node_params or {},
    }.get(key, default)
    return ctx


class TestLocalEvolverRelativeWeak:
    """Iteration 1: relative weak dimensions instead of absolute threshold."""

    def _write_sessions(self, data_dir: Path, sessions: list[dict]) -> None:
        jsonl_path = data_dir / "sessions.jsonl"
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(jsonl_path, "w") as f:
            for s in sessions:
                f.write(json.dumps(s) + "\n")

    def _make_sessions(self, tradition: str, scores: dict[str, float], count: int = 5) -> list[dict]:
        return [
            {"tradition": tradition, "final_scores": scores, "user_feedback": "accepted",
             "session_id": f"s{i}", "mode": "create", "eval_mode": "strict"}
            for i in range(count)
        ]

    def test_relative_weak_not_absolute(self):
        """Even with all scores > 0.7, bottom 2 should be identified as weak."""
        from vulca.digestion.local_evolver import LocalEvolver
        with tempfile.TemporaryDirectory() as td:
            sessions = self._make_sessions("t1", {"L1": 0.85, "L2": 0.76, "L3": 0.90, "L4": 0.79, "L5": 0.88})
            self._write_sessions(Path(td), sessions)
            evolver = LocalEvolver(data_dir=td)
            result = evolver.evolve()
            assert result is not None
            weak = result["traditions"]["t1"]["weak_dimensions"]
            assert len(weak) == 2
            assert "L2" in weak
            assert "L4" in weak

    def test_overall_avg_stored(self):
        from vulca.digestion.local_evolver import LocalEvolver
        with tempfile.TemporaryDirectory() as td:
            sessions = self._make_sessions("t1", {"L1": 0.80, "L2": 0.80, "L3": 0.80, "L4": 0.80, "L5": 0.80})
            self._write_sessions(Path(td), sessions)
            evolver = LocalEvolver(data_dir=td)
            result = evolver.evolve()
            assert "overall_avg" in result["traditions"]["t1"]
            assert abs(result["traditions"]["t1"]["overall_avg"] - 0.80) < 0.01

    def test_load_evolved_reads_tradition(self):
        from vulca.digestion.local_evolver import LocalEvolver
        with tempfile.TemporaryDirectory() as td:
            evolved = {"traditions": {"t1": {"weak_dimensions": ["L1", "L2"], "overall_avg": 0.82}}}
            (Path(td) / "evolved_context.json").write_text(json.dumps(evolved))
            evolver = LocalEvolver(data_dir=td)
            data = evolver.load_evolved("t1")
            assert data is not None
            assert data["weak_dimensions"] == ["L1", "L2"]

    def test_load_evolved_missing_file(self):
        from vulca.digestion.local_evolver import LocalEvolver
        with tempfile.TemporaryDirectory() as td:
            evolver = LocalEvolver(data_dir=td)
            assert evolver.load_evolved("t1") is None

    def test_load_evolved_missing_tradition(self):
        from vulca.digestion.local_evolver import LocalEvolver
        with tempfile.TemporaryDirectory() as td:
            evolved = {"traditions": {"t1": {"weak_dimensions": ["L1"]}}}
            (Path(td) / "evolved_context.json").write_text(json.dumps(evolved))
            evolver = LocalEvolver(data_dir=td)
            assert evolver.load_evolved("unknown") is None

    def test_load_evolved_corrupt_json(self):
        from vulca.digestion.local_evolver import LocalEvolver
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "evolved_context.json").write_text("{corrupt")
            evolver = LocalEvolver(data_dir=td)
            assert evolver.load_evolved("t1") is None


class TestGenerateNodeEvolution:
    """Iteration 1: GenerateNode includes evolution hint in guidance."""

    def test_guidance_includes_evolution_hint(self):
        from vulca.pipeline.nodes.generate import GenerateNode
        with tempfile.TemporaryDirectory() as td:
            evolved = {"traditions": {"chinese_xieyi": {
                "weak_dimensions": ["L1", "L2"], "overall_avg": 0.82
            }}}
            (Path(td) / "evolved_context.json").write_text(json.dumps(evolved))
            import os
            old = os.environ.get("VULCA_EVOLVED_DATA_DIR")
            os.environ["VULCA_EVOLVED_DATA_DIR"] = td
            try:
                guidance = GenerateNode._build_generation_guidance("chinese_xieyi")
                assert "Evolution hint" in guidance
                assert "L1" in guidance
                assert "L2" in guidance
            finally:
                if old is None:
                    os.environ.pop("VULCA_EVOLVED_DATA_DIR", None)
                else:
                    os.environ["VULCA_EVOLVED_DATA_DIR"] = old

    def test_guidance_without_evolution_still_works(self):
        from vulca.pipeline.nodes.generate import GenerateNode
        import os
        old = os.environ.get("VULCA_EVOLVED_DATA_DIR")
        os.environ["VULCA_EVOLVED_DATA_DIR"] = "/tmp/nonexistent_vulca_test_dir"
        try:
            guidance = GenerateNode._build_generation_guidance("chinese_xieyi")
            assert "Evolution hint" not in guidance
        finally:
            if old is None:
                os.environ.pop("VULCA_EVOLVED_DATA_DIR", None)
            else:
                os.environ["VULCA_EVOLVED_DATA_DIR"] = old
