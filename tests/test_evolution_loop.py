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


class TestDecideNodeEvolution:
    """Iteration 1: DecideNode micro-adjusts threshold from evolution data."""

    def test_high_avg_raises_threshold(self):
        from vulca.pipeline.nodes.decide import DecideNode
        with tempfile.TemporaryDirectory() as td:
            evolved = {"traditions": {"t1": {"overall_avg": 0.85, "weak_dimensions": ["L1"]}}}
            (Path(td) / "evolved_context.json").write_text(json.dumps(evolved))
            import os
            os.environ["VULCA_EVOLVED_DATA_DIR"] = td
            try:
                node = DecideNode(accept_threshold=0.7)
                ctx = _make_decide_ctx(tradition="t1", weighted_total=0.73, scores={"L1": 0.7, "L2": 0.76},
                                       round_num=1, max_rounds=3)
                import asyncio
                result = asyncio.run(node.run(ctx))
                # threshold 0.7 + 0.05 = 0.75. Score 0.73 < 0.75 → rerun
                assert result["decision"] == "rerun"
            finally:
                os.environ.pop("VULCA_EVOLVED_DATA_DIR", None)

    def test_without_evolution_uses_default(self):
        from vulca.pipeline.nodes.decide import DecideNode
        import os
        os.environ["VULCA_EVOLVED_DATA_DIR"] = "/tmp/nonexistent_vulca_test_dir"
        try:
            node = DecideNode(accept_threshold=0.7)
            ctx = _make_decide_ctx(tradition="t1", weighted_total=0.73, scores={"L1": 0.7, "L2": 0.76},
                                   round_num=1, max_rounds=3)
            import asyncio
            result = asyncio.run(node.run(ctx))
            # No evolution → threshold stays 0.7. Score 0.73 >= 0.7 → accept
            assert result["decision"] == "accept"
        finally:
            os.environ.pop("VULCA_EVOLVED_DATA_DIR", None)

    def test_user_threshold_overrides_evolution(self):
        from vulca.pipeline.nodes.decide import DecideNode
        with tempfile.TemporaryDirectory() as td:
            evolved = {"traditions": {"t1": {"overall_avg": 0.90}}}
            (Path(td) / "evolved_context.json").write_text(json.dumps(evolved))
            import os
            os.environ["VULCA_EVOLVED_DATA_DIR"] = td
            try:
                node = DecideNode(accept_threshold=0.7)
                ctx = _make_decide_ctx(tradition="t1", weighted_total=0.65, scores={"L1": 0.6, "L2": 0.7},
                                       round_num=1, max_rounds=3,
                                       node_params={"decide": {"accept_threshold": 0.5}})
                import asyncio
                result = asyncio.run(node.run(ctx))
                # User set threshold=0.5. Score 0.65 >= 0.5 → accept (evolution ignored)
                assert result["decision"] == "accept"
            finally:
                os.environ.pop("VULCA_EVOLVED_DATA_DIR", None)

    def test_reference_mode_always_accepts(self):
        from vulca.pipeline.nodes.decide import DecideNode
        with tempfile.TemporaryDirectory() as td:
            evolved = {"traditions": {"t1": {"overall_avg": 0.95}}}
            (Path(td) / "evolved_context.json").write_text(json.dumps(evolved))
            import os
            os.environ["VULCA_EVOLVED_DATA_DIR"] = td
            try:
                node = DecideNode(accept_threshold=0.7)
                ctx = _make_decide_ctx(tradition="t1", weighted_total=0.30, scores={"L1": 0.3},
                                       round_num=1, max_rounds=3, eval_mode="reference")
                import asyncio
                result = asyncio.run(node.run(ctx))
                assert result["decision"] == "accept"
            finally:
                os.environ.pop("VULCA_EVOLVED_DATA_DIR", None)


class TestEvalModeAwareness:
    """Iteration 2: evolution separates strict vs reference sessions."""

    def _write_sessions(self, data_dir: Path, sessions: list[dict]) -> None:
        jsonl_path = data_dir / "sessions.jsonl"
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(jsonl_path, "w") as f:
            for s in sessions:
                f.write(json.dumps(s) + "\n")

    def test_strict_and_reference_produce_different_signals(self):
        from vulca.digestion.local_evolver import LocalEvolver
        with tempfile.TemporaryDirectory() as td:
            strict = [
                {"tradition": "t1", "final_scores": {"L1": 0.70, "L2": 0.90, "L3": 0.85, "L4": 0.88, "L5": 0.92},
                 "user_feedback": "accepted", "eval_mode": "strict", "session_id": f"strict{i}"}
                for i in range(5)
            ]
            reference = [
                {"tradition": "t1", "final_scores": {"L1": 0.90, "L2": 0.85, "L3": 0.50, "L4": 0.88, "L5": 0.45},
                 "user_feedback": "accepted", "eval_mode": "reference", "session_id": f"ref{i}"}
                for i in range(5)
            ]
            self._write_sessions(Path(td), strict + reference)
            evolver = LocalEvolver(data_dir=td)
            result = evolver.evolve()
            t1 = result["traditions"]["t1"]
            # Strict: L1 is weakest (0.70)
            assert "L1" in t1["strict_weak"]
            # Reference: L3 and L5 are low (exploration trends)
            assert "L3" in t1["reference_trends"] or "L5" in t1["reference_trends"]
            # Counts
            assert t1["strict_count"] == 5
            assert t1["reference_count"] == 5

    def test_missing_eval_mode_defaults_to_strict(self):
        from vulca.digestion.local_evolver import LocalEvolver
        with tempfile.TemporaryDirectory() as td:
            sessions = [
                {"tradition": "t1", "final_scores": {"L1": 0.75, "L2": 0.80, "L3": 0.85, "L4": 0.90, "L5": 0.88},
                 "user_feedback": "accepted", "session_id": f"s{i}"}
                for i in range(5)
            ]
            self._write_sessions(Path(td), sessions)
            evolver = LocalEvolver(data_dir=td)
            result = evolver.evolve()
            t1 = result["traditions"]["t1"]
            assert len(t1["weak_dimensions"]) >= 1
            assert t1["strict_count"] >= 5


class TestDeviationTypeFiltering:
    """Iteration 3: intentional_departure excluded from weak dimensions."""

    def _write_sessions(self, data_dir: Path, sessions: list[dict]) -> None:
        jsonl_path = data_dir / "sessions.jsonl"
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(jsonl_path, "w") as f:
            for s in sessions:
                f.write(json.dumps(s) + "\n")

    def test_intentional_departure_excluded_from_weak(self):
        from vulca.digestion.local_evolver import LocalEvolver
        with tempfile.TemporaryDirectory() as td:
            sessions = []
            for i in range(10):
                dev_types = {"L1": "intentional_departure" if i < 5 else "traditional",
                             "L2": "traditional", "L3": "traditional", "L4": "traditional", "L5": "traditional"}
                sessions.append({
                    "tradition": "t1", "eval_mode": "strict", "user_feedback": "accepted",
                    "final_scores": {"L1": 0.65, "L2": 0.70, "L3": 0.90, "L4": 0.85, "L5": 0.88},
                    "deviation_types": dev_types, "session_id": f"s{i}",
                })
            self._write_sessions(Path(td), sessions)
            evolver = LocalEvolver(data_dir=td)
            result = evolver.evolve()
            weak = result["traditions"]["t1"]["weak_dimensions"]
            # L1 should be EXCLUDED (50% intentional_departure > 30% threshold)
            assert "L1" not in weak
            # L2 should be in weak (lowest after excluding L1)
            assert "L2" in weak
            # L1 should appear in innovation_signals
            assert "L1" in result["traditions"]["t1"]["innovation_signals"]

    def test_missing_deviation_types_still_works(self):
        from vulca.digestion.local_evolver import LocalEvolver
        with tempfile.TemporaryDirectory() as td:
            sessions = [
                {"tradition": "t1", "final_scores": {"L1": 0.75, "L2": 0.80, "L3": 0.85, "L4": 0.90, "L5": 0.88},
                 "user_feedback": "accepted", "eval_mode": "strict", "session_id": f"s{i}"}
                for i in range(5)
            ]
            self._write_sessions(Path(td), sessions)
            evolver = LocalEvolver(data_dir=td)
            result = evolver.evolve()
            assert len(result["traditions"]["t1"]["weak_dimensions"]) >= 1


class TestFullTrendInjection:
    """Iteration 4: rich trend context in GenerateNode prompt."""

    def test_prompt_has_strengthen_and_creative(self):
        from vulca.pipeline.nodes.generate import GenerateNode
        with tempfile.TemporaryDirectory() as td:
            evolved = {"traditions": {"t1": {
                "weak_dimensions": ["L2"],
                "strict_weak": ["L2"],
                "reference_trends": ["L3", "L5"],
                "innovation_signals": ["L1"],
                "overall_avg": 0.82,
                "session_count": 20,
                "strict_count": 15,
                "reference_count": 5,
                "dimension_averages": {"L1": 0.80, "L2": 0.72, "L3": 0.88, "L4": 0.85, "L5": 0.83},
            }}}
            (Path(td) / "evolved_context.json").write_text(json.dumps(evolved))
            import os
            os.environ["VULCA_EVOLVED_DATA_DIR"] = td
            try:
                guidance = GenerateNode._build_generation_guidance("t1")
                assert "Strengthen" in guidance
                assert "Creative space" in guidance
                assert "L2" in guidance  # in Strengthen
                assert "L1" in guidance  # in Creative space (innovation_signal)
            finally:
                os.environ.pop("VULCA_EVOLVED_DATA_DIR", None)

    def test_few_sessions_uses_simple_hint(self):
        from vulca.pipeline.nodes.generate import GenerateNode
        with tempfile.TemporaryDirectory() as td:
            evolved = {"traditions": {"t1": {
                "weak_dimensions": ["L1", "L2"], "session_count": 3, "overall_avg": 0.75,
            }}}
            (Path(td) / "evolved_context.json").write_text(json.dumps(evolved))
            import os
            os.environ["VULCA_EVOLVED_DATA_DIR"] = td
            try:
                guidance = GenerateNode._build_generation_guidance("t1")
                assert "Evolution hint" in guidance
                assert "Strengthen" not in guidance  # not enough data
            finally:
                os.environ.pop("VULCA_EVOLVED_DATA_DIR", None)


class TestModeAwareThreshold:
    """Iteration 4: DecideNode adjusts threshold by strict/reference ratio."""

    def test_strict_heavy_raises_threshold(self):
        from vulca.pipeline.nodes.decide import DecideNode
        with tempfile.TemporaryDirectory() as td:
            evolved = {"traditions": {"t1": {
                "overall_avg": 0.85, "strict_count": 90, "reference_count": 10, "session_count": 100,
            }}}
            (Path(td) / "evolved_context.json").write_text(json.dumps(evolved))
            import os
            os.environ["VULCA_EVOLVED_DATA_DIR"] = td
            try:
                node = DecideNode(accept_threshold=0.7)
                ctx = _make_decide_ctx(tradition="t1", weighted_total=0.74, scores={"L1": 0.74},
                                       round_num=1, max_rounds=3)
                import asyncio
                result = asyncio.run(node.run(ctx))
                # strict_ratio=0.9, mode_adj=0.05*(0.9-0.5)=+0.02
                # evolution_adj=0.05, total=0.07, threshold=0.7+0.07=0.77
                # capped at min(0.77, 0.85*0.95=0.8075) = 0.77
                # 0.74 < 0.77 → rerun
                assert result["decision"] == "rerun"
            finally:
                os.environ.pop("VULCA_EVOLVED_DATA_DIR", None)

    def test_min_sessions_guard(self):
        from vulca.pipeline.nodes.decide import DecideNode
        with tempfile.TemporaryDirectory() as td:
            evolved = {"traditions": {"t1": {
                "overall_avg": 0.95, "strict_count": 2, "reference_count": 1, "session_count": 3,
            }}}
            (Path(td) / "evolved_context.json").write_text(json.dumps(evolved))
            import os
            os.environ["VULCA_EVOLVED_DATA_DIR"] = td
            try:
                node = DecideNode(accept_threshold=0.7)
                ctx = _make_decide_ctx(tradition="t1", weighted_total=0.71, scores={"L1": 0.71},
                                       round_num=1, max_rounds=3)
                import asyncio
                result = asyncio.run(node.run(ctx))
                # < 5 sessions but hist_avg > 0.5 → simple adjustment
                # adjusted = min(0.7 + 0.05, 0.95*0.95=0.9025) = 0.75
                # 0.71 < 0.75 → rerun
                assert result["decision"] == "rerun"
            finally:
                os.environ.pop("VULCA_EVOLVED_DATA_DIR", None)
