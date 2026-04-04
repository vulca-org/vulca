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

        class FakeBackend:
            def append(self, data: dict) -> None:
                captured.append(data)

        fake_module = MagicMock()
        fake_module.JsonlSessionBackend = FakeBackend

        with patch.dict("sys.modules", {"vulca.storage.jsonl": fake_module}):
            from vulca.pipeline.hooks import default_on_complete

            asyncio.run(default_on_complete(output))

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
