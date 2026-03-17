"""Tests for storage backends -- protocol compliance, JSONL read/write."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from vulca.storage.protocol import FeedbackBackend, SessionBackend
from vulca.storage.jsonl import JsonlFeedbackBackend, JsonlSessionBackend


# -- Protocol Tests --------------------------------------------------------


class TestProtocol:
    def test_session_backend_is_abstract(self):
        with pytest.raises(TypeError):
            SessionBackend()

    def test_feedback_backend_is_abstract(self):
        with pytest.raises(TypeError):
            FeedbackBackend()

    def test_jsonl_session_implements_protocol(self):
        with tempfile.TemporaryDirectory() as td:
            backend = JsonlSessionBackend(Path(td) / "sessions.jsonl")
            assert isinstance(backend, SessionBackend)

    def test_jsonl_feedback_implements_protocol(self):
        with tempfile.TemporaryDirectory() as td:
            backend = JsonlFeedbackBackend(Path(td) / "feedback.jsonl")
            assert isinstance(backend, FeedbackBackend)

    def test_imports_from_init(self):
        from vulca.storage import SessionBackend, FeedbackBackend
        assert SessionBackend is not None
        assert FeedbackBackend is not None


# -- JSONL Session Backend Tests -------------------------------------------


class TestJsonlSessionBackend:
    def _make_backend(self, tmp_path: Path) -> JsonlSessionBackend:
        return JsonlSessionBackend(tmp_path / "sessions.jsonl")

    def test_append_and_get_all(self, tmp_path):
        backend = self._make_backend(tmp_path)
        backend.append({"session_id": "s1", "tradition": "default", "score": 0.75})
        backend.append({"session_id": "s2", "tradition": "chinese_xieyi", "score": 0.82})

        records = backend.get_all()
        assert len(records) == 2
        assert records[0]["session_id"] == "s1"
        assert records[1]["session_id"] == "s2"

    def test_count(self, tmp_path):
        backend = self._make_backend(tmp_path)
        assert backend.count() == 0

        backend.append({"session_id": "s1"})
        backend.append({"session_id": "s2"})
        assert backend.count() == 2

    def test_get_all_with_limit(self, tmp_path):
        backend = self._make_backend(tmp_path)
        for i in range(10):
            backend.append({"session_id": f"s{i}"})

        records = backend.get_all(limit=3)
        assert len(records) == 3
        assert records[0]["session_id"] == "s7"  # last 3

    def test_get_by_tradition(self, tmp_path):
        backend = self._make_backend(tmp_path)
        backend.append({"session_id": "s1", "tradition": "default"})
        backend.append({"session_id": "s2", "tradition": "chinese_xieyi"})
        backend.append({"session_id": "s3", "tradition": "chinese_xieyi"})

        xieyi = backend.get_by_tradition("chinese_xieyi")
        assert len(xieyi) == 2
        assert all(r["tradition"] == "chinese_xieyi" for r in xieyi)

    def test_update_field(self, tmp_path):
        backend = self._make_backend(tmp_path)
        backend.append({"session_id": "s1", "score": 0.5})

        result = backend.update_field("s1", "score", 0.9)
        assert result is True

        records = backend.get_all()
        assert records[0]["score"] == 0.9

    def test_update_field_not_found(self, tmp_path):
        backend = self._make_backend(tmp_path)
        backend.append({"session_id": "s1"})

        result = backend.update_field("nonexistent", "score", 0.9)
        assert result is False

    def test_empty_file(self, tmp_path):
        backend = self._make_backend(tmp_path)
        assert backend.get_all() == []
        assert backend.count() == 0

    def test_corrupted_line_skipped(self, tmp_path):
        path = tmp_path / "sessions.jsonl"
        with open(path, "w") as f:
            f.write('{"session_id": "s1"}\n')
            f.write("this is not json\n")
            f.write('{"session_id": "s2"}\n')

        backend = JsonlSessionBackend(path)
        records = backend.get_all()
        assert len(records) == 2

    def test_unicode_content(self, tmp_path):
        backend = self._make_backend(tmp_path)
        backend.append({"session_id": "s1", "subject": "\u6c34\u58a8\u5c71\u6c34"})

        records = backend.get_all()
        assert records[0]["subject"] == "\u6c34\u58a8\u5c71\u6c34"


# -- JSONL Feedback Backend Tests ------------------------------------------


class TestJsonlFeedbackBackend:
    def _make_backend(self, tmp_path: Path) -> JsonlFeedbackBackend:
        return JsonlFeedbackBackend(tmp_path / "feedback.jsonl")

    def test_append_and_get_all(self, tmp_path):
        backend = self._make_backend(tmp_path)
        backend.append({"rating": "thumbs_up", "comment": "Great", "tradition": "default"})
        backend.append({"rating": "thumbs_down", "comment": "Bad", "tradition": "default"})

        records = backend.get_all()
        assert len(records) == 2

    def test_get_by_tradition(self, tmp_path):
        backend = self._make_backend(tmp_path)
        backend.append({"rating": "thumbs_up", "tradition": "default"})
        backend.append({"rating": "thumbs_up", "tradition": "chinese_xieyi"})

        result = backend.get_by_tradition("chinese_xieyi")
        assert len(result) == 1

    def test_get_stats_empty(self, tmp_path):
        backend = self._make_backend(tmp_path)
        stats = backend.get_stats()
        assert stats["total_feedback"] == 0
        assert stats["thumbs_up"] == 0
        assert stats["thumbs_down"] == 0

    def test_get_stats(self, tmp_path):
        backend = self._make_backend(tmp_path)
        backend.append({"rating": "thumbs_up", "feedback_type": "explicit", "comment": "Nice"})
        backend.append({"rating": "thumbs_up", "feedback_type": "explicit", "comment": "Good"})
        backend.append({"rating": "thumbs_down", "feedback_type": "implicit"})

        stats = backend.get_stats()
        assert stats["total_feedback"] == 3
        assert stats["thumbs_up"] == 2
        assert stats["thumbs_down"] == 1
        assert stats["by_type"]["explicit"] == 2
        assert stats["by_type"]["implicit"] == 1
        assert len(stats["recent_comments"]) == 2

    def test_get_all_with_limit(self, tmp_path):
        backend = self._make_backend(tmp_path)
        for i in range(10):
            backend.append({"id": i, "rating": "thumbs_up"})

        records = backend.get_all(limit=3)
        assert len(records) == 3
