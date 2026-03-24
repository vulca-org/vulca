"""StudioStore -- persist studio session data to JSONL."""
from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from vulca.studio.brief import Brief

logger = logging.getLogger("vulca.digestion")


class StudioStore:
    """JSONL-based storage for Studio session data."""

    def __init__(self, data_dir: str | Path = ""):
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".vulca" / "sessions"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._file = self.data_dir / "studio_sessions.jsonl"

    def save_session(self, brief: Brief, *, user_feedback: str = "") -> None:
        """Append a completed session to the JSONL store."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_id": brief.session_id,
            "brief": asdict(brief),
            "user_feedback": user_feedback,
            "generation_count": len(brief.generations),
            "update_count": len(brief.updates),
        }

        # Extract final scores if available
        if brief.generations:
            record["final_scores"] = brief.generations[-1].scores

        with self._file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def load_sessions(self, limit: int = 100) -> list[dict]:
        """Load recent sessions from JSONL."""
        if not self._file.exists():
            return []

        sessions = []
        for line in self._file.read_text(encoding="utf-8").strip().splitlines():
            if line:
                sessions.append(json.loads(line))

        return sessions[-limit:]
