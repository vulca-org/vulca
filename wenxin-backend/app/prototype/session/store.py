"""JSONL-backed session digest storage with thread-safe append and singleton access."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from app.prototype.session.types import SessionDigest

_DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, "data", "sessions.jsonl"
)


class SessionStore:
    """Thread-safe, JSONL-backed session digest storage.

    Uses a singleton pattern so all callers share the same lock and path.
    """

    _instance: SessionStore | None = None
    _lock = threading.Lock()

    def __init__(self, path: str | None = None) -> None:
        self._path = Path(path or _DEFAULT_PATH).resolve()
        self._write_lock = threading.Lock()

    @classmethod
    def get(cls, path: str | None = None) -> SessionStore:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(path)
        return cls._instance

    def append(self, digest: SessionDigest) -> None:
        """Append a single session digest to the JSONL file (thread-safe)."""
        with self._write_lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(digest.to_dict(), ensure_ascii=False) + "\n")

    def get_all(self) -> list[dict]:
        """Read all session digests as dicts."""
        if not self._path.exists():
            return []
        records: list[dict] = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except (json.JSONDecodeError, ValueError):
                    continue
        return records

    def get_recent(self, limit: int = 50) -> list[dict]:
        """Return the last *limit* session digests (newest last)."""
        records = self.get_all()
        return records[-limit:]

    def get_by_tradition(self, tradition: str) -> list[dict]:
        """Return all sessions for a given tradition."""
        return [r for r in self.get_all() if r.get("tradition") == tradition]

    def count(self) -> int:
        """Return total number of stored sessions."""
        if not self._path.exists():
            return 0
        count = 0
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    def update_field(self, session_id: str, field: str, value: object) -> bool:
        """Update a single field on a session by rewriting the JSONL file.

        Returns True if the session was found and updated.
        """
        with self._write_lock:
            records = self.get_all()
            found = False
            for rec in records:
                if rec.get("session_id") == session_id:
                    rec[field] = value
                    found = True
                    break
            if not found:
                return False
            with open(self._path, "w", encoding="utf-8") as f:
                for rec in records:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            return True
