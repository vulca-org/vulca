"""JSONL-backed feedback storage with thread-safe append and singleton access."""

from __future__ import annotations

import json
import os
import threading
from collections import defaultdict
from pathlib import Path

from app.prototype.feedback.types import FeedbackRecord, FeedbackStats

_DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, "data", "feedback.jsonl"
)


class FeedbackStore:
    """Thread-safe, JSONL-backed feedback storage.

    Uses a singleton pattern so all callers share the same lock and path.
    """

    _instance: FeedbackStore | None = None
    _lock = threading.Lock()

    def __init__(self, path: str | None = None) -> None:
        self._path = Path(path or _DEFAULT_PATH).resolve()
        self._write_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Singleton access
    # ------------------------------------------------------------------

    @classmethod
    def get(cls, path: str | None = None) -> FeedbackStore:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(path)
        return cls._instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append(self, record: FeedbackRecord) -> None:
        """Append a single feedback record to the JSONL file (thread-safe)."""
        with self._write_lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.model_dump(), ensure_ascii=False) + "\n")

    def get_stats(self) -> FeedbackStats:
        """Read all records and compute aggregate statistics."""
        records = self._read_all()
        thumbs_up = sum(1 for r in records if r.rating == "thumbs_up")
        thumbs_down = sum(1 for r in records if r.rating == "thumbs_down")

        by_type: dict[str, int] = defaultdict(int)
        for r in records:
            by_type[r.feedback_type] += 1

        recent_comments = [
            r.comment for r in reversed(records) if r.comment
        ][:10]

        return FeedbackStats(
            total_feedback=len(records),
            thumbs_up=thumbs_up,
            thumbs_down=thumbs_down,
            by_type=dict(by_type),
            recent_comments=recent_comments,
        )

    def get_recent(self, limit: int = 50) -> list[FeedbackRecord]:
        """Return the last *limit* feedback records (newest last)."""
        records = self._read_all()
        return records[-limit:]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_all(self) -> list[FeedbackRecord]:
        if not self._path.exists():
            return []
        records: list[FeedbackRecord] = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(FeedbackRecord(**json.loads(line)))
                except (json.JSONDecodeError, ValueError):
                    # Skip malformed lines gracefully
                    continue
        return records
