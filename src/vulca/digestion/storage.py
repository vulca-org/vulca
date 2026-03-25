"""Digestion V2 storage — session, artifact, and signal persistence.

JSONL backend for local dev. Designed for drop-in Supabase replacement.
"""
from __future__ import annotations

import json
import threading
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from vulca.studio.brief import Brief


class JsonlStudioStorage:
    """JSONL-based storage for Studio digestion data.

    Three files:
    - studio_sessions.jsonl — completed session records (Brief + metadata)
    - artifacts.jsonl — per-artifact L1-L5 analysis records
    - signals.jsonl — per-action user signals
    """

    def __init__(self, data_dir: str | Path = ""):
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".vulca" / "digestion"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._sessions_file = self.data_dir / "studio_sessions.jsonl"
        self._artifacts_file = self.data_dir / "artifacts.jsonl"
        self._signals_file = self.data_dir / "signals.jsonl"
        self._lock = threading.Lock()

    # ── Sessions ──

    def save_session(self, brief: Brief, *, user_feedback: str = "") -> None:
        """Persist a studio session."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_id": brief.session_id,
            "brief": asdict(brief),
            "user_feedback": user_feedback,
            "generation_count": len(brief.generations),
            "update_count": len(brief.updates),
            "traditions": [s.tradition for s in brief.style_mix if s.tradition],
        }
        if brief.generations:
            record["final_scores"] = brief.generations[-1].scores
        self._append(self._sessions_file, record)

    def get_sessions(self, *, tradition: str = "", limit: int = 0) -> list[dict[str, Any]]:
        """Retrieve sessions, optionally filtered by tradition."""
        records = self._read_all(self._sessions_file)
        if tradition:
            records = [r for r in records if tradition in r.get("traditions", [])]
        if limit > 0:
            records = records[-limit:]
        return records

    # ── Artifacts ──

    def save_artifact(
        self, *, session_id: str, artifact_type: str,
        file_path: str = "", analysis: dict[str, Any] | None = None,
    ) -> None:
        """Persist an artifact analysis record."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_id": session_id,
            "artifact_type": artifact_type,
            "file_path": file_path,
            "analysis": analysis or {},
        }
        self._append(self._artifacts_file, record)

    def get_artifacts(self, *, session_id: str = "") -> list[dict[str, Any]]:
        """Retrieve artifacts, optionally filtered by session."""
        records = self._read_all(self._artifacts_file)
        if session_id:
            records = [r for r in records if r.get("session_id") == session_id]
        return records

    # ── Signals ──

    def append_signal(
        self, *, session_id: str, action: str, phase: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Append a per-action signal."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_id": session_id,
            "action": action,
            "phase": phase,
            "data": data or {},
        }
        self._append(self._signals_file, record)

    def get_signals(self, *, session_id: str = "") -> list[dict[str, Any]]:
        """Retrieve signals, optionally filtered by session."""
        records = self._read_all(self._signals_file)
        if session_id:
            records = [r for r in records if r.get("session_id") == session_id]
        return records

    # ── Internal ──

    def _append(self, path: Path, record: dict) -> None:
        with self._lock:
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def _read_all(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        with self._lock:
            records = []
            for line in path.read_text(encoding="utf-8").strip().splitlines():
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return records
