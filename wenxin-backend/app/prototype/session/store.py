"""Session digest storage — DB-backed (production) with JSONL fallback (dev).

Production: reads/writes PrototypeSession rows via sync SQLAlchemy.
Development: falls back to JSONL file if DB is SQLite or unavailable.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from app.prototype.session.types import SessionDigest

_DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, "data", "sessions.jsonl"
)


def _use_db() -> bool:
    """Return True if we should use the database backend."""
    try:
        from app.core.config import settings
        return not settings.DATABASE_URL.startswith("sqlite")
    except Exception:
        return False


class SessionStore:
    """Thread-safe session digest storage.

    Uses database in production (PostgreSQL/Supabase), JSONL file in dev.
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

    # ── Write ──────────────────────────────────────────────────────

    def append(self, digest: SessionDigest) -> None:
        """Append a session digest."""
        if _use_db():
            self._db_append(digest)
        else:
            self._jsonl_append(digest)

    def _db_append(self, digest: SessionDigest) -> None:
        from app.core.database import SyncSessionLocal
        from app.models.prototype_session import PrototypeSession
        d = digest.to_dict()
        row = PrototypeSession(
            session_id=d["session_id"],
            mode=d.get("mode", "create"),
            intent=d.get("intent", ""),
            tradition=d.get("tradition", "default"),
            subject=d.get("subject", ""),
            user_type=d.get("user_type", "human"),
            user_id=d.get("user_id", ""),
            media_type=d.get("media_type", "image"),
            rounds=d.get("rounds", []),
            final_scores=d.get("final_scores", {}),
            final_weighted_total=d.get("final_weighted_total", 0.0),
            best_image_url=d.get("best_image_url", ""),
            risk_flags=d.get("risk_flags", []),
            recommendations=d.get("recommendations", []),
            feedback=d.get("feedback", []),
            cultural_features=d.get("cultural_features", {}),
            critic_insights=d.get("critic_insights", []),
            candidate_choice_index=d.get("candidate_choice_index", -1),
            time_to_select_ms=d.get("time_to_select_ms", 0),
            downloaded=d.get("downloaded", False),
            published=d.get("published", False),
            likes_count=d.get("likes_count", 0),
            total_rounds=d.get("total_rounds", 0),
            total_latency_ms=d.get("total_latency_ms", 0),
            total_cost_usd=d.get("total_cost_usd", 0.0),
            created_at=d.get("created_at", 0.0),
        )
        with SyncSessionLocal() as session:
            session.merge(row)  # upsert
            session.commit()

    def _jsonl_append(self, digest: SessionDigest) -> None:
        with self._write_lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(digest.to_dict(), ensure_ascii=False) + "\n")

    # ── Read ───────────────────────────────────────────────────────

    def get_all(self) -> list[dict]:
        if _use_db():
            return self._db_get_all()
        return self._jsonl_get_all()

    def _db_get_all(self) -> list[dict]:
        from app.core.database import SyncSessionLocal
        from app.models.prototype_session import PrototypeSession
        with SyncSessionLocal() as session:
            rows = session.query(PrototypeSession).order_by(PrototypeSession.created_at).all()
            return [r.to_dict() for r in rows]

    def _jsonl_get_all(self) -> list[dict]:
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
        if _use_db():
            from app.core.database import SyncSessionLocal
            from app.models.prototype_session import PrototypeSession
            with SyncSessionLocal() as session:
                rows = (session.query(PrototypeSession)
                        .order_by(PrototypeSession.created_at.desc())
                        .limit(limit).all())
                return [r.to_dict() for r in reversed(rows)]
        records = self.get_all()
        return records[-limit:]

    def get_by_tradition(self, tradition: str) -> list[dict]:
        if _use_db():
            from app.core.database import SyncSessionLocal
            from app.models.prototype_session import PrototypeSession
            with SyncSessionLocal() as session:
                rows = (session.query(PrototypeSession)
                        .filter(PrototypeSession.tradition == tradition)
                        .order_by(PrototypeSession.created_at).all())
                return [r.to_dict() for r in rows]
        return [r for r in self.get_all() if r.get("tradition") == tradition]

    def count(self) -> int:
        if _use_db():
            from app.core.database import SyncSessionLocal
            from app.models.prototype_session import PrototypeSession
            from sqlalchemy import func
            with SyncSessionLocal() as session:
                return session.query(func.count(PrototypeSession.session_id)).scalar() or 0
        if not self._path.exists():
            return 0
        count = 0
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    # ── Update ─────────────────────────────────────────────────────

    def update_field(self, session_id: str, field: str, value: object) -> bool:
        if _use_db():
            return self._db_update_field(session_id, field, value)
        return self._jsonl_update_field(session_id, field, value)

    def _db_update_field(self, session_id: str, field: str, value: object) -> bool:
        from app.core.database import SyncSessionLocal
        from app.models.prototype_session import PrototypeSession
        with SyncSessionLocal() as session:
            row = session.query(PrototypeSession).filter(
                PrototypeSession.session_id == session_id
            ).first()
            if not row:
                return False
            setattr(row, field, value)
            session.commit()
            return True

    def _jsonl_update_field(self, session_id: str, field: str, value: object) -> bool:
        with self._write_lock:
            records = self._jsonl_get_all()
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
