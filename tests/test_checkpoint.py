"""Tests for pipeline round checkpointing."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from vulca.pipeline.checkpoint import CheckpointStore


class TestCheckpointStore:
    def test_save_and_load_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            store = CheckpointStore(data_dir=td)
            store.save_metadata("sess1", {
                "pipeline_name": "default",
                "subject": "tea",
                "intent": "chinese tea",
                "tradition": "chinese_xieyi",
                "provider": "mock",
                "max_rounds": 3,
            })
            cp = store.load_checkpoint("sess1")
            assert cp is not None
            assert cp["metadata"]["subject"] == "tea"
            assert cp["metadata"]["tradition"] == "chinese_xieyi"

    def test_save_and_load_round(self):
        with tempfile.TemporaryDirectory() as td:
            store = CheckpointStore(data_dir=td)
            store.save_metadata("sess1", {"pipeline_name": "default", "subject": "test", "tradition": "default", "provider": "mock", "max_rounds": 3, "intent": ""})
            store.save_round("sess1", 1, {
                "scores": {"L1": 0.81, "L2": 0.76},
                "weighted_total": 0.82,
                "candidate_id": "c1",
                "tradition": "chinese_xieyi",
                "eval_mode": "strict",
                "decision": "loop",
            })
            cp = store.load_checkpoint("sess1")
            assert len(cp["rounds"]) == 1
            assert cp["rounds"][0]["round_num"] == 1
            assert cp["rounds"][0]["weighted_total"] == 0.82

    def test_save_round_with_image(self):
        """Image b64 should be saved as PNG file, not stored in JSONL."""
        import base64
        from PIL import Image
        import io

        with tempfile.TemporaryDirectory() as td:
            store = CheckpointStore(data_dir=td)
            store.save_metadata("sess1", {"pipeline_name": "default", "subject": "test", "tradition": "default", "provider": "mock", "max_rounds": 3, "intent": ""})

            img = Image.new("RGB", (10, 10), (255, 0, 0))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            img_b64 = base64.b64encode(buf.getvalue()).decode()

            store.save_round("sess1", 1, {
                "scores": {"L1": 0.8},
                "weighted_total": 0.8,
                "candidate_id": "c1",
                "image_b64": img_b64,
                "decision": "loop",
            })

            img_path = Path(td) / "sess1" / "round1.png"
            assert img_path.exists()

            rounds_path = Path(td) / "sess1" / "rounds.jsonl"
            line = rounds_path.read_text().strip()
            data = json.loads(line)
            assert "image_b64" not in data
            assert data["image_ref"] == "round1.png"

    def test_load_round_restores_image(self):
        """Loading a checkpoint should re-encode PNG to b64."""
        import base64
        from PIL import Image
        import io

        with tempfile.TemporaryDirectory() as td:
            store = CheckpointStore(data_dir=td)
            store.save_metadata("sess1", {"pipeline_name": "default", "subject": "test", "tradition": "default", "provider": "mock", "max_rounds": 3, "intent": ""})

            img = Image.new("RGB", (10, 10), (0, 0, 255))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            original_b64 = base64.b64encode(buf.getvalue()).decode()

            store.save_round("sess1", 1, {
                "scores": {"L1": 0.8},
                "weighted_total": 0.8,
                "candidate_id": "c1",
                "image_b64": original_b64,
                "decision": "loop",
            })

            cp = store.load_checkpoint("sess1")
            restored_b64 = cp["rounds"][0].get("image_b64", "")
            assert restored_b64 != ""
            decoded = base64.b64decode(restored_b64)
            img_restored = Image.open(io.BytesIO(decoded))
            assert img_restored.size == (10, 10)

    def test_list_sessions(self):
        with tempfile.TemporaryDirectory() as td:
            store = CheckpointStore(data_dir=td)
            store.save_metadata("sess1", {"pipeline_name": "default", "subject": "a", "tradition": "default", "provider": "mock", "max_rounds": 3, "intent": ""})
            store.save_metadata("sess2", {"pipeline_name": "default", "subject": "b", "tradition": "default", "provider": "mock", "max_rounds": 3, "intent": ""})
            sessions = store.list_sessions()
            assert set(sessions) == {"sess1", "sess2"}

    def test_get_round(self):
        with tempfile.TemporaryDirectory() as td:
            store = CheckpointStore(data_dir=td)
            store.save_metadata("sess1", {"pipeline_name": "default", "subject": "test", "tradition": "default", "provider": "mock", "max_rounds": 3, "intent": ""})
            store.save_round("sess1", 1, {"scores": {}, "weighted_total": 0.7, "candidate_id": "c1", "decision": "loop"})
            store.save_round("sess1", 2, {"scores": {}, "weighted_total": 0.85, "candidate_id": "c2", "decision": "accept"})
            r2 = store.get_round("sess1", 2)
            assert r2 is not None
            assert r2["weighted_total"] == 0.85

    def test_nonexistent_session_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            store = CheckpointStore(data_dir=td)
            assert store.load_checkpoint("nonexistent") is None
            assert store.get_round("nonexistent", 1) is None
