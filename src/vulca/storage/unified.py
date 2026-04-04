"""Unified session store -- single canonical data directory for all entry points.

Consolidates SDK (JsonlSessionBackend) and Studio (JsonlStudioStorage)
into one JSONL file at ``~/.vulca/data/sessions.jsonl`` (or VULCA_DATA_DIR).

This module does NOT replace jsonl.py or digestion/storage.py yet --
they will be updated later to delegate to this store.

Usage::

    from vulca.storage.unified import UnifiedSessionStore

    store = UnifiedSessionStore()            # default: ~/.vulca/data
    store.append({"session_id": "...", ...}) # write
    store.load_all()                         # read all
    store.load_by_tradition("chinese_xieyi") # filter
    store.load_since("2026-03-01T00:00:00Z") # filter by time
    store.evolved_context_path               # canonical path for evolved_context.json
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any


class UnifiedSessionStore:
    """Single canonical store for all VULCA session data.

    Parameters
    ----------
    data_dir : str | Path, optional
        Root data directory.  Resolved in order:
        1. Explicit ``data_dir`` argument
        2. ``VULCA_DATA_DIR`` environment variable
        3. ``~/.vulca/data`` (default)
    """

    def __init__(self, data_dir: str | Path | None = None) -> None:
        if data_dir is not None:
            self._data_dir = Path(data_dir)
        else:
            env = os.environ.get("VULCA_DATA_DIR")
            if env:
                self._data_dir = Path(env)
            else:
                self._data_dir = Path.home() / ".vulca" / "data"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._sessions_path = self._data_dir / "sessions.jsonl"
        self._lock = threading.Lock()

    # ── Properties ──

    @property
    def data_dir(self) -> Path:
        """Root data directory."""
        return self._data_dir

    @property
    def sessions_path(self) -> Path:
        """Canonical path to the unified sessions JSONL file."""
        return self._sessions_path

    @property
    def evolved_context_path(self) -> Path:
        """Canonical path for evolved_context.json."""
        return self._data_dir / "evolved_context.json"

    # ── Write ──

    def append(self, data: dict[str, Any]) -> None:
        """Append a session record to the unified JSONL file."""
        with self._lock:
            self._sessions_path.parent.mkdir(parents=True, exist_ok=True)
            with self._sessions_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False, default=str) + "\n")

    # ── Read ──

    def load_all(self) -> list[dict[str, Any]]:
        """Read all session records from the JSONL file."""
        if not self._sessions_path.exists():
            return []
        with self._lock:
            records: list[dict[str, Any]] = []
            with self._sessions_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            return records

    def load_by_tradition(self, tradition: str) -> list[dict[str, Any]]:
        """Read sessions filtered by tradition name."""
        return [r for r in self.load_all() if r.get("tradition") == tradition]

    # ── Feedback ──

    def record_feedback(self, session_id: str, signal: str) -> None:
        """Record explicit user feedback (accepted/rejected) for a session."""
        feedback_path = self._data_dir / "feedback.jsonl"
        entry = {"session_id": session_id, "signal": signal, "timestamp": __import__("time").time()}
        with self._lock:
            with feedback_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def load_feedback(self) -> list[dict[str, Any]]:
        """Load all explicit feedback entries."""
        feedback_path = self._data_dir / "feedback.jsonl"
        if not feedback_path.exists():
            return []
        entries: list[dict[str, Any]] = []
        with self._lock:
            with feedback_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return entries

    def load_since(self, timestamp: str) -> list[dict[str, Any]]:
        """Read sessions with timestamp >= the given ISO timestamp string.

        Records without a ``timestamp`` field are excluded.
        Comparison is lexicographic on ISO-8601 strings, which works correctly
        for UTC timestamps in the same format.
        """
        return [
            r for r in self.load_all()
            if r.get("timestamp", "") >= timestamp
        ]
