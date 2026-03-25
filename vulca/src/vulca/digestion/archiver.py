"""Cold storage archiver — archive completed sessions for long-term retention.

Local implementation writes JSON files. Future: GCS bucket upload.
Designed to preserve ALL data including Brief version history,
rejected artifacts, and raw signals.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from vulca.studio.brief import Brief


class LocalArchiver:
    """Archive sessions to local filesystem (mock for GCS cold storage)."""

    def __init__(self, archive_dir: str | Path = ""):
        self.archive_dir = Path(archive_dir) if archive_dir else Path.home() / ".vulca" / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def archive_session(self, brief: Brief, user_feedback: str = "") -> Path:
        """Archive a completed session to a JSON file.

        Returns the path to the archive file.
        """
        record = {
            "archived_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_id": brief.session_id,
            "user_feedback": user_feedback,
            "brief": asdict(brief),
            "generation_count": len(brief.generations),
            "update_count": len(brief.updates),
        }

        if brief.generations:
            record["final_scores"] = brief.generations[-1].scores

        filepath = self.archive_dir / f"{brief.session_id}.json"
        filepath.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        return filepath
