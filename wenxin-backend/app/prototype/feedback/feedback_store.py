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

    def sync_from_sessions(self) -> int:
        """Sync inline feedback from sessions to feedback.jsonl.

        Reads from SessionStore (supports Supabase DB + JSONL fallback).
        Returns count of new feedback entries synced.
        """
        try:
            from app.prototype.session.store import SessionStore
            all_sessions = SessionStore.get().get_all()
        except Exception:
            # Fallback: try JSONL directly
            sessions_path = self._path.parent / "sessions.jsonl"
            if not sessions_path.exists():
                return 0
            all_sessions = []
            for line in sessions_path.read_text().strip().split("\n"):
                if line.strip():
                    try:
                        all_sessions.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        if not all_sessions:
            return 0

        # Load existing feedback evaluation_ids to avoid duplicates
        existing_ids: set[str] = set()
        if self._path.exists():
            for line in self._path.read_text().strip().split("\n"):
                if line.strip():
                    try:
                        entry = json.loads(line)
                        existing_ids.add(entry.get("evaluation_id", ""))
                    except json.JSONDecodeError:
                        pass

        synced = 0
        for session in all_sessions:
            if isinstance(session, dict):
                pass  # already a dict
            elif hasattr(session, "to_dict"):
                session = session.to_dict()
            else:
                continue

            sid = session.get("session_id", "")
            if not sid or sid in existing_ids:
                continue

            # Check for inline feedback
            feedback = session.get("feedback")
            if not feedback:
                continue

            # Normalize: feedback may be a dict or a list of dicts
            if isinstance(feedback, list):
                feedback_items = [f for f in feedback if isinstance(f, dict)]
            elif isinstance(feedback, dict):
                feedback_items = [feedback]
            else:
                continue

            for fb in feedback_items:
                # Determine rating
                rating = fb.get("rating")
                if not rating:
                    if fb.get("liked") is True:
                        rating = "thumbs_up"
                    elif fb.get("liked") is False:
                        rating = "thumbs_down"
                    else:
                        continue

                ts = session.get("completed_at") or session.get("created_at", "")
                if not isinstance(ts, str):
                    ts = str(ts)

                record = FeedbackRecord(
                    id=f"sync-{sid}",
                    evaluation_id=sid,
                    rating=rating,
                    comment=fb.get("comment", ""),
                    feedback_type="implicit",
                    timestamp=ts,
                    tradition=session.get("tradition", ""),
                )
                self.append(record)
                synced += 1

        return synced

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
