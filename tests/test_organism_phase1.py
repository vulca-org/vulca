"""Phase 1: Unified SessionStore tests.

Verifies that SDK and Studio sessions converge to a single JSONL file,
evolved_context resolves to a canonical path, and cultural/loader.py reads
from the unified path instead of wenxin-backend.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest


class TestUnifiedSessionStore:
    """UnifiedSessionStore — single data directory, single sessions file."""

    def test_sdk_and_studio_share_store(self, tmp_path: Path) -> None:
        """Both SDK-style and Studio-style appends land in the same JSONL."""
        from vulca.storage.unified import UnifiedSessionStore

        store = UnifiedSessionStore(data_dir=tmp_path / "data")

        # SDK session
        store.append({"session_id": "sdk-001", "source": "sdk", "tradition": "default"})
        # Studio session
        store.append({"session_id": "studio-001", "source": "studio", "tradition": "chinese_xieyi"})

        all_sessions = store.load_all()
        assert len(all_sessions) == 2
        ids = {s["session_id"] for s in all_sessions}
        assert ids == {"sdk-001", "studio-001"}

    def test_single_jsonl_file(self, tmp_path: Path) -> None:
        """Only one sessions.jsonl file exists, not two."""
        from vulca.storage.unified import UnifiedSessionStore

        store = UnifiedSessionStore(data_dir=tmp_path / "data")
        store.append({"session_id": "s1", "tradition": "default"})

        # Only one JSONL file in the data directory
        jsonl_files = list((tmp_path / "data").glob("*.jsonl"))
        assert len(jsonl_files) == 1
        assert jsonl_files[0].name == "sessions.jsonl"

    def test_evolved_context_single_path(self, tmp_path: Path) -> None:
        """evolved_context_path property returns a canonical path under data_dir."""
        from vulca.storage.unified import UnifiedSessionStore

        store = UnifiedSessionStore(data_dir=tmp_path / "data")
        epath = store.evolved_context_path
        assert epath == tmp_path / "data" / "evolved_context.json"
        assert epath.parent == tmp_path / "data"

    def test_backward_compat_reads_old_sessions(self, tmp_path: Path) -> None:
        """Existing sessions.jsonl is read by the new store."""
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True)

        # Pre-populate a JSONL file as if the old JsonlSessionBackend wrote it
        old_file = data_dir / "sessions.jsonl"
        records = [
            {"session_id": "old-001", "tradition": "chinese_xieyi", "score": 0.8},
            {"session_id": "old-002", "tradition": "default", "score": 0.6},
        ]
        with old_file.open("w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")

        from vulca.storage.unified import UnifiedSessionStore

        store = UnifiedSessionStore(data_dir=data_dir)
        all_sessions = store.load_all()
        assert len(all_sessions) == 2
        assert all_sessions[0]["session_id"] == "old-001"

    def test_load_by_tradition(self, tmp_path: Path) -> None:
        """load_by_tradition filters correctly."""
        from vulca.storage.unified import UnifiedSessionStore

        store = UnifiedSessionStore(data_dir=tmp_path / "data")
        store.append({"session_id": "s1", "tradition": "chinese_xieyi"})
        store.append({"session_id": "s2", "tradition": "default"})
        store.append({"session_id": "s3", "tradition": "chinese_xieyi"})

        filtered = store.load_by_tradition("chinese_xieyi")
        assert len(filtered) == 2
        assert all(s["tradition"] == "chinese_xieyi" for s in filtered)

    def test_load_since(self, tmp_path: Path) -> None:
        """load_since filters by timestamp."""
        from vulca.storage.unified import UnifiedSessionStore

        store = UnifiedSessionStore(data_dir=tmp_path / "data")
        store.append({"session_id": "s1", "tradition": "default", "timestamp": "2026-01-01T00:00:00Z"})
        store.append({"session_id": "s2", "tradition": "default", "timestamp": "2026-03-15T12:00:00Z"})
        store.append({"session_id": "s3", "tradition": "default", "timestamp": "2026-04-01T00:00:00Z"})

        # Everything since March 1
        recent = store.load_since("2026-03-01T00:00:00Z")
        assert len(recent) == 2
        assert {s["session_id"] for s in recent} == {"s2", "s3"}

    def test_env_var_override(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """VULCA_DATA_DIR env var overrides default data directory."""
        from vulca.storage.unified import UnifiedSessionStore

        custom_dir = tmp_path / "custom_data"
        monkeypatch.setenv("VULCA_DATA_DIR", str(custom_dir))

        store = UnifiedSessionStore()
        store.append({"session_id": "env-001", "tradition": "default"})

        assert store.evolved_context_path == custom_dir / "evolved_context.json"
        assert (custom_dir / "sessions.jsonl").exists()

    def test_loader_reads_unified_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """cultural/loader.py reads evolved_context from the unified path, not wenxin-backend."""
        import vulca.cultural.loader as loader

        # Set up evolved context in a temp dir
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True)
        ctx_file = data_dir / "evolved_context.json"
        ctx_file.write_text(json.dumps({
            "tradition_weights": {
                "chinese_xieyi": {
                    "visual_perception": 0.10,
                    "technical_analysis": 0.15,
                    "cultural_context": 0.35,
                    "critical_interpretation": 0.20,
                    "philosophical_aesthetic": 0.20,
                }
            },
            "total_sessions": 42,
        }))

        # Point loader to the unified path
        monkeypatch.setattr(loader, "_EVOLVED_CONTEXT_DIR", data_dir)

        weights = loader._load_evolved_weights("chinese_xieyi")
        assert weights is not None
        assert weights["L3"] == 0.35
        assert weights["L1"] == 0.10

    def test_loader_no_wenxin_backend_paths(self) -> None:
        """loader._load_evolved_weights should not reference wenxin-backend paths."""
        import inspect
        from vulca.cultural.loader import _load_evolved_weights

        source = inspect.getsource(_load_evolved_weights)
        assert "wenxin-backend" not in source, (
            "_load_evolved_weights still references wenxin-backend paths"
        )
        assert "prototype" not in source, (
            "_load_evolved_weights still references prototype paths"
        )

    def test_get_tradition_guide_no_wenxin_paths(self) -> None:
        """get_tradition_guide should not reference wenxin-backend paths."""
        import inspect
        from vulca.cultural.loader import get_tradition_guide

        source = inspect.getsource(get_tradition_guide)
        assert "wenxin-backend" not in source, (
            "get_tradition_guide still references wenxin-backend paths"
        )


class TestRealFeedback:
    """Real feedback signals — pipeline completion is neutral, explicit feedback is recorded."""

    def test_pipeline_completion_is_neutral(self, tmp_path: Path) -> None:
        """hooks.py default_on_complete writes user_feedback='completed', not 'accepted'."""
        import asyncio
        from unittest.mock import patch, MagicMock

        from vulca.pipeline.types import PipelineOutput

        output = PipelineOutput(
            session_id="neutral-001",
            tradition="chinese_xieyi",
            best_image_url="test.png",
            final_scores={"L1": 0.8, "L2": 0.7, "L3": 0.6, "L4": 0.5, "L5": 0.4},
            weighted_total=0.6,
        )

        captured: list[dict] = []

        class FakeStore:
            def __init__(self, **kwargs: Any) -> None:
                pass
            def append(self, data: dict) -> None:
                captured.append(data)

        fake_module = MagicMock()
        fake_module.UnifiedSessionStore = FakeStore

        with patch.dict("sys.modules", {"vulca.storage.unified": fake_module}):
            # Force reimport to pick up the patched module
            import importlib
            import vulca.pipeline.hooks as hooks_mod
            importlib.reload(hooks_mod)
            asyncio.run(hooks_mod.default_on_complete(output))

        assert len(captured) == 1
        assert captured[0]["user_feedback"] == "completed"

    def test_explicit_accept_writes_accepted(self, tmp_path: Path) -> None:
        """UnifiedSessionStore.record_feedback stores 'accepted' signal."""
        from vulca.storage.unified import UnifiedSessionStore

        store = UnifiedSessionStore(data_dir=tmp_path / "data")
        store.record_feedback("s1", "accepted")

        entries = store.load_feedback()
        assert len(entries) == 1
        assert entries[0]["session_id"] == "s1"
        assert entries[0]["signal"] == "accepted"
        assert "timestamp" in entries[0]

    def test_explicit_reject_writes_rejected(self, tmp_path: Path) -> None:
        """UnifiedSessionStore.record_feedback stores 'rejected' signal."""
        from vulca.storage.unified import UnifiedSessionStore

        store = UnifiedSessionStore(data_dir=tmp_path / "data")
        store.record_feedback("s2", "rejected")

        entries = store.load_feedback()
        assert len(entries) == 1
        assert entries[0]["session_id"] == "s2"
        assert entries[0]["signal"] == "rejected"

    def test_evolver_merges_feedback_signals(self, tmp_path: Path) -> None:
        """LocalEvolver._load_sessions merges feedback from UnifiedSessionStore."""
        from vulca.digestion.local_evolver import LocalEvolver
        from vulca.storage.unified import UnifiedSessionStore

        data_dir = tmp_path / "data"
        store = UnifiedSessionStore(data_dir=data_dir)

        # Write sessions without explicit feedback
        store.append({"session_id": "s1", "tradition": "chinese_xieyi", "user_feedback": "completed"})
        store.append({"session_id": "s2", "tradition": "chinese_xieyi", "user_feedback": "completed"})

        # Record explicit feedback for s1
        store.record_feedback("s1", "accepted")

        evolver = LocalEvolver(data_dir=str(data_dir))
        sessions = evolver._load_sessions()

        s1 = next(s for s in sessions if s["session_id"] == "s1")
        s2 = next(s for s in sessions if s["session_id"] == "s2")
        assert s1["user_feedback"] == "accepted"
        assert s2["user_feedback"] == "completed"  # unchanged, no explicit feedback


class TestFewShotPipeline:
    """Few-shot examples are extracted during evolve() and written to evolved_context.json."""

    @staticmethod
    def _seed_sessions(tmp_path: Path, *, extra_sessions: list[dict] | None = None) -> Path:
        """Seed a data_dir with enough sessions + feedback to trigger evolution.

        Returns the data_dir path.  By default, creates 6 sessions in 'chinese_xieyi'
        tradition: 4 accepted (high score), 1 rejected, 1 completed-only (neutral).
        """
        from vulca.storage.unified import UnifiedSessionStore

        data_dir = tmp_path / "data"
        store = UnifiedSessionStore(data_dir=data_dir)

        base_sessions = [
            {
                "session_id": "fs-001",
                "tradition": "chinese_xieyi",
                "subject": "Misty mountain landscape",
                "final_scores": {"L1": 0.90, "L2": 0.85, "L3": 0.80, "L4": 0.75, "L5": 0.70},
                "weighted_total": 0.80,
                "user_feedback": "completed",
                "eval_mode": "strict",
                "timestamp": 100.0,
            },
            {
                "session_id": "fs-002",
                "tradition": "chinese_xieyi",
                "subject": "Bamboo grove at dawn",
                "final_scores": {"L1": 0.95, "L2": 0.90, "L3": 0.85, "L4": 0.80, "L5": 0.78},
                "weighted_total": 0.86,
                "user_feedback": "completed",
                "eval_mode": "strict",
                "timestamp": 101.0,
            },
            {
                "session_id": "fs-003",
                "tradition": "chinese_xieyi",
                "subject": "Failed ink wash",
                "final_scores": {"L1": 0.30, "L2": 0.25, "L3": 0.20, "L4": 0.15, "L5": 0.10},
                "weighted_total": 0.20,
                "user_feedback": "completed",
                "eval_mode": "strict",
                "timestamp": 102.0,
            },
            {
                "session_id": "fs-004",
                "tradition": "chinese_xieyi",
                "subject": "Plum blossom winter",
                "final_scores": {"L1": 0.88, "L2": 0.82, "L3": 0.79, "L4": 0.76, "L5": 0.73},
                "weighted_total": 0.79,
                "user_feedback": "completed",
                "eval_mode": "strict",
                "timestamp": 103.0,
            },
            {
                "session_id": "fs-005",
                "tradition": "chinese_xieyi",
                "subject": "Lotus pond serenity",
                "final_scores": {"L1": 0.92, "L2": 0.87, "L3": 0.83, "L4": 0.79, "L5": 0.76},
                "weighted_total": 0.83,
                "user_feedback": "completed",
                "eval_mode": "strict",
                "timestamp": 104.0,
            },
            {
                "session_id": "fs-006",
                "tradition": "chinese_xieyi",
                "subject": "Crane in reeds",
                "final_scores": {"L1": 0.50, "L2": 0.45, "L3": 0.40, "L4": 0.35, "L5": 0.30},
                "weighted_total": 0.40,
                "user_feedback": "completed",
                "eval_mode": "strict",
                "timestamp": 105.0,
            },
        ]

        for s in base_sessions:
            store.append(s)

        if extra_sessions:
            for s in extra_sessions:
                store.append(s)

        # Record explicit feedback: accept high-scorers, reject one
        store.record_feedback("fs-001", "accepted")
        store.record_feedback("fs-002", "accepted")
        store.record_feedback("fs-003", "rejected")
        store.record_feedback("fs-004", "accepted")
        store.record_feedback("fs-005", "accepted")
        # fs-006 has no explicit feedback (neutral)

        return data_dir

    def test_few_shot_written_on_evolve(self, tmp_path: Path) -> None:
        """After evolve(), evolved_context.json has few_shot_examples with high-scoring accepted sessions."""
        from vulca.digestion.local_evolver import LocalEvolver

        data_dir = self._seed_sessions(tmp_path)
        evolver = LocalEvolver(data_dir=str(data_dir))
        result = evolver.evolve()

        assert result is not None, "evolve() should return data with sufficient sessions"
        assert "few_shot_examples" in result, "evolved data must contain few_shot_examples"

        examples = result["few_shot_examples"]
        assert isinstance(examples, list)
        assert len(examples) > 0, "Should have at least one few-shot example"

        # All examples should be from accepted sessions with weighted_total >= 0.75
        example_ids = {ex["session_id"] for ex in examples}
        assert "fs-001" in example_ids  # accepted, 0.80 >= 0.75
        assert "fs-002" in example_ids  # accepted, 0.86 >= 0.75
        assert "fs-004" in example_ids  # accepted, 0.79 >= 0.75
        assert "fs-005" in example_ids  # accepted, 0.83 >= 0.75

        # Verify each example has the required fields
        for ex in examples:
            assert "session_id" in ex
            assert "tradition" in ex
            assert "subject" in ex
            assert "score" in ex
            assert "key_strengths" in ex
            # Score should be rounded to 3 decimals
            score_str = str(ex["score"])
            if "." in score_str:
                assert len(score_str.split(".")[1]) <= 3
            # key_strengths should be top 2 dimensions
            assert isinstance(ex["key_strengths"], list)
            assert len(ex["key_strengths"]) == 2

        # Verify persisted to disk
        evolved_path = data_dir / "evolved_context.json"
        assert evolved_path.exists()
        disk_data = json.loads(evolved_path.read_text())
        assert "few_shot_examples" in disk_data
        assert len(disk_data["few_shot_examples"]) == len(examples)

        # Examples should be sorted by score descending within tradition
        xieyi_examples = [ex for ex in examples if ex["tradition"] == "chinese_xieyi"]
        scores = [ex["score"] for ex in xieyi_examples]
        assert scores == sorted(scores, reverse=True), "Examples should be sorted by score descending"

    def test_few_shot_excludes_rejected(self, tmp_path: Path) -> None:
        """Rejected sessions never appear in few_shot_examples."""
        from vulca.digestion.local_evolver import LocalEvolver

        data_dir = self._seed_sessions(tmp_path)
        evolver = LocalEvolver(data_dir=str(data_dir))
        result = evolver.evolve()

        assert result is not None
        examples = result.get("few_shot_examples", [])
        example_ids = {ex["session_id"] for ex in examples}

        # fs-003 was rejected -- must NOT appear
        assert "fs-003" not in example_ids, "Rejected session must not appear in few_shot_examples"

        # fs-006 has no explicit feedback (neutral) -- should also not appear
        # (only explicitly accepted sessions qualify)
        assert "fs-006" not in example_ids, (
            "Session without explicit accept should not appear in few_shot_examples"
        )


class TestModePromptDifferentiation:
    """Mode-specific VLM prompt framing — strict vs reference vs fusion produce different prompts."""

    def test_strict_prompt_contains_conformance_framing(self) -> None:
        """_build_dynamic_suffix with mode='strict' contains conformance/judge language."""
        from vulca._vlm import _build_dynamic_suffix

        result = _build_dynamic_suffix("chinese_xieyi", mode="strict")
        result_lower = result.lower()
        assert "conformance" in result_lower or "judge" in result_lower, (
            "Strict mode prompt must contain 'conformance' or 'judge'"
        )

    def test_reference_prompt_contains_mentor_framing(self) -> None:
        """_build_dynamic_suffix with mode='reference' contains mentor/advisor language."""
        from vulca._vlm import _build_dynamic_suffix

        result = _build_dynamic_suffix("chinese_xieyi", mode="reference")
        result_lower = result.lower()
        assert "mentor" in result_lower or "advisor" in result_lower, (
            "Reference mode prompt must contain 'mentor' or 'advisor'"
        )

    def test_strict_and_reference_prompts_differ(self) -> None:
        """Strict and reference mode prompts are not equal."""
        from vulca._vlm import _build_dynamic_suffix

        strict = _build_dynamic_suffix("chinese_xieyi", mode="strict")
        reference = _build_dynamic_suffix("chinese_xieyi", mode="reference")
        assert strict != reference, (
            "Strict and reference mode prompts must differ"
        )

    def test_default_mode_is_strict(self) -> None:
        """Calling without mode produces the same result as mode='strict'."""
        from vulca._vlm import _build_dynamic_suffix

        default = _build_dynamic_suffix("chinese_xieyi")
        explicit_strict = _build_dynamic_suffix("chinese_xieyi", mode="strict")
        assert default == explicit_strict, (
            "Default mode must produce the same prompt as explicit mode='strict'"
        )


class TestEvolutionRoundTrip:
    """Critical: evolve() output must be readable by loader and _vlm.py."""

    def test_evolve_weights_readable_by_loader(self, tmp_path: Path) -> None:
        """The most critical test: evolved_context.json round-trips correctly."""
        from vulca.digestion.local_evolver import LocalEvolver
        from vulca.storage.unified import UnifiedSessionStore
        import vulca.cultural.loader as loader

        data_dir = tmp_path / "data"
        store = UnifiedSessionStore(data_dir=data_dir)

        sessions = [
            {
                "session_id": f"s{i}",
                "tradition": "chinese_xieyi",
                "final_scores": {"L1": 0.85, "L2": 0.80, "L3": 0.90, "L4": 0.82, "L5": 0.88},
                "weighted_total": 0.85,
                "user_feedback": "completed",
                "eval_mode": "strict",
                "subject": f"landscape {i}",
            }
            for i in range(6)
        ]
        for s in sessions:
            store.append(s)
        for i in range(4):
            store.record_feedback(f"s{i}", "accepted")

        evolver = LocalEvolver(data_dir=str(data_dir))
        result = evolver.evolve()
        assert result is not None, "evolve() should return data"

        # THE CRITICAL CHECK: loader can read back what evolver wrote
        old_dir = loader._EVOLVED_CONTEXT_DIR
        try:
            loader._EVOLVED_CONTEXT_DIR = data_dir
            weights = loader._load_evolved_weights("chinese_xieyi")
            assert weights is not None, "evolved weights must be readable by loader"
            assert len(weights) == 5, f"expected 5 dimensions, got {len(weights)}"
            # Loader returns L1-L5 keyed dict
            for lk in ("L1", "L2", "L3", "L4", "L5"):
                assert lk in weights, f"missing {lk} in loader output"
        finally:
            loader._EVOLVED_CONTEXT_DIR = old_dir

    def test_tradition_weights_key_exists_in_evolved(self, tmp_path: Path) -> None:
        """evolved_context.json must contain 'tradition_weights' key."""
        from vulca.digestion.local_evolver import LocalEvolver
        from vulca.storage.unified import UnifiedSessionStore

        data_dir = tmp_path / "data"
        store = UnifiedSessionStore(data_dir=data_dir)

        for i in range(6):
            store.append({
                "session_id": f"s{i}",
                "tradition": "chinese_xieyi",
                "final_scores": {"L1": 0.85, "L2": 0.80, "L3": 0.90, "L4": 0.82, "L5": 0.88},
                "weighted_total": 0.85,
                "user_feedback": "completed",
                "eval_mode": "strict",
                "subject": f"landscape {i}",
            })
        for i in range(4):
            store.record_feedback(f"s{i}", "accepted")

        evolver = LocalEvolver(data_dir=str(data_dir))
        result = evolver.evolve()
        assert result is not None

        assert "tradition_weights" in result, (
            "evolved dict must contain 'tradition_weights' for _vlm.py and loader.py"
        )
        tw = result["tradition_weights"]
        assert "chinese_xieyi" in tw
        xieyi = tw["chinese_xieyi"]
        # Must use full dimension names as keys
        expected_keys = {
            "visual_perception", "technical_analysis",
            "cultural_context", "critical_interpretation",
            "philosophical_aesthetic",
        }
        assert set(xieyi.keys()) == expected_keys, (
            f"tradition_weights must use full dimension names, got {set(xieyi.keys())}"
        )

    def test_tradition_weights_persisted_to_disk(self, tmp_path: Path) -> None:
        """tradition_weights must be written to disk, not just in-memory."""
        from vulca.digestion.local_evolver import LocalEvolver
        from vulca.storage.unified import UnifiedSessionStore

        data_dir = tmp_path / "data"
        store = UnifiedSessionStore(data_dir=data_dir)

        for i in range(6):
            store.append({
                "session_id": f"s{i}",
                "tradition": "chinese_xieyi",
                "final_scores": {"L1": 0.85, "L2": 0.80, "L3": 0.90, "L4": 0.82, "L5": 0.88},
                "weighted_total": 0.85,
                "user_feedback": "completed",
                "eval_mode": "strict",
                "subject": f"landscape {i}",
            })
        for i in range(4):
            store.record_feedback(f"s{i}", "accepted")

        evolver = LocalEvolver(data_dir=str(data_dir))
        evolver.evolve()

        # Read from disk directly
        evolved_path = data_dir / "evolved_context.json"
        assert evolved_path.exists()
        disk_data = json.loads(evolved_path.read_text())
        assert "tradition_weights" in disk_data, (
            "tradition_weights must be persisted to disk"
        )


class TestRiskFlags:
    def test_risk_flags_in_prompt(self):
        from vulca._vlm import _STATIC_SCORING_PREFIX
        assert "risk_flags" in _STATIC_SCORING_PREFIX

    def test_risk_flags_parsed_from_response(self):
        from vulca._vlm import _parse_vlm_response
        raw = {
            "L1": 0.8, "L2": 0.7, "L3": 0.9, "L4": 0.8, "L5": 0.85,
            "L1_rationale": "good", "L2_rationale": "ok", "L3_rationale": "excellent",
            "L4_rationale": "fine", "L5_rationale": "deep",
            "risk_flags": ["cultural_appropriation", "anachronistic_elements"],
        }
        result = _parse_vlm_response(raw)
        assert "risk_flags" in result
        assert len(result["risk_flags"]) == 2

    def test_risk_flags_defaults_empty_list(self):
        from vulca._vlm import _parse_vlm_response
        raw = {"L1": 0.8, "L2": 0.7, "L3": 0.9, "L4": 0.8, "L5": 0.85,
               "L1_rationale": "a", "L2_rationale": "b", "L3_rationale": "c",
               "L4_rationale": "d", "L5_rationale": "e"}
        result = _parse_vlm_response(raw)
        assert result.get("risk_flags") == []

    def test_risk_flags_invalid_type_becomes_empty(self):
        from vulca._vlm import _parse_vlm_response
        raw = {"L1": 0.8, "L2": 0.7, "L3": 0.9, "L4": 0.8, "L5": 0.85,
               "L1_rationale": "a", "L2_rationale": "b", "L3_rationale": "c",
               "L4_rationale": "d", "L5_rationale": "e",
               "risk_flags": "not_a_list"}
        result = _parse_vlm_response(raw)
        assert result.get("risk_flags") == []
