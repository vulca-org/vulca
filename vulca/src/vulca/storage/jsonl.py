"""JSONL file-based storage backends for local development.

These backends read/write newline-delimited JSON files.
Thread-safe via file-level locking.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

from vulca.storage.protocol import FeedbackBackend, SessionBackend


class JsonlSessionBackend(SessionBackend):
    """Session storage backed by a JSONL file."""

    def __init__(self, path: str | Path = "") -> None:
        if not path:
            data_dir = Path(os.environ.get("VULCA_DATA_DIR", "~/.vulca/data")).expanduser()
            data_dir.mkdir(parents=True, exist_ok=True)
            path = data_dir / "sessions.jsonl"
        self._path = Path(path)
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path

    def append(self, session: dict[str, Any]) -> None:
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(session, ensure_ascii=False, default=str) + "\n")

    def get_all(self, limit: int = 0) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        records = []
        with self._lock:
            with open(self._path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        if limit > 0:
            records = records[-limit:]
        return records

    def count(self) -> int:
        if not self._path.exists():
            return 0
        with self._lock:
            with open(self._path, "r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip())

    def get_by_tradition(self, tradition: str, limit: int = 50) -> list[dict[str, Any]]:
        all_records = self.get_all()
        filtered = [r for r in all_records if r.get("tradition") == tradition]
        if limit > 0:
            filtered = filtered[-limit:]
        return filtered

    def update_field(self, session_id: str, field: str, value: Any) -> bool:
        if not self._path.exists():
            return False
        with self._lock:
            records = []
            found = False
            with open(self._path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        records.append(line)
                        continue
                    if rec.get("session_id") == session_id:
                        rec[field] = value
                        found = True
                    records.append(json.dumps(rec, ensure_ascii=False, default=str))

            if found:
                with open(self._path, "w", encoding="utf-8") as f:
                    for line in records:
                        f.write(line + "\n")
            return found


class JsonlFeedbackBackend(FeedbackBackend):
    """Feedback storage backed by a JSONL file."""

    def __init__(self, path: str | Path = "") -> None:
        if not path:
            data_dir = Path(os.environ.get("VULCA_DATA_DIR", "~/.vulca/data")).expanduser()
            data_dir.mkdir(parents=True, exist_ok=True)
            path = data_dir / "feedback.jsonl"
        self._path = Path(path)
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path

    def append(self, record: dict[str, Any]) -> None:
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def get_all(self, limit: int = 0) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        records = []
        with self._lock:
            with open(self._path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        if limit > 0:
            records = records[-limit:]
        return records

    def get_by_tradition(self, tradition: str, limit: int = 50) -> list[dict[str, Any]]:
        all_records = self.get_all()
        filtered = [r for r in all_records if r.get("tradition") == tradition]
        if limit > 0:
            filtered = filtered[-limit:]
        return filtered

    def get_stats(self) -> dict[str, Any]:
        records = self.get_all()
        total = len(records)
        thumbs_up = sum(1 for r in records if r.get("rating") == "thumbs_up")
        thumbs_down = sum(1 for r in records if r.get("rating") == "thumbs_down")

        by_type: dict[str, int] = {}
        for r in records:
            ft = r.get("feedback_type", "unknown")
            by_type[ft] = by_type.get(ft, 0) + 1

        recent = [r.get("comment", "") for r in records[-5:] if r.get("comment")]

        return {
            "total_feedback": total,
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "by_type": by_type,
            "recent_comments": recent,
        }
