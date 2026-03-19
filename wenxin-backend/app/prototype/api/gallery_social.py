"""Gallery social interactions — like + fork (JSONL-backed).

Follows the same JSONL storage pattern as FeedbackStore.
"""

from __future__ import annotations

import json
import threading
import time
from collections import defaultdict
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.prototype.api.auth import verify_api_key

gallery_social_router = APIRouter(
    prefix="/api/v1/prototype/gallery", tags=["gallery-social"]
)

_DATA_PATH = Path(__file__).parent.parent / "data" / "gallery_likes.jsonl"
_write_lock = threading.Lock()


class LikeRecord(BaseModel):
    session_id: str
    timestamp: float
    client_id: str = ""


class LikeResponse(BaseModel):
    session_id: str
    likes: int


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _read_all_likes() -> list[dict]:
    if not _DATA_PATH.exists():
        return []
    records: list[dict] = []
    for line in _DATA_PATH.read_text(encoding="utf-8").strip().split("\n"):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _count_likes() -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for rec in _read_all_likes():
        counts[rec.get("session_id", "")] += 1
    return dict(counts)


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@gallery_social_router.post("/{session_id}/like", response_model=LikeResponse)
async def like_artwork(session_id: str, client_id: str = ""):
    """Like a gallery artwork. Appends to JSONL store."""
    record = LikeRecord(
        session_id=session_id,
        timestamp=time.time(),
        client_id=client_id,
    )
    with _write_lock:
        _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_DATA_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.model_dump(), ensure_ascii=False) + "\n")

    counts = _count_likes()
    return LikeResponse(session_id=session_id, likes=counts.get(session_id, 1))


@gallery_social_router.get("/likes", response_model=dict[str, int])
async def get_all_likes():
    """Return like counts for all artworks: {session_id: count}."""
    return _count_likes()


class PublishResponse(BaseModel):
    session_id: str
    published: bool
    message: str


@gallery_social_router.post("/{session_id}/publish", response_model=PublishResponse)
async def publish_to_gallery(session_id: str, _key: str = Depends(verify_api_key)):
    """Publish a session to the public Gallery.

    Sets the ``published`` flag on the session digest so it appears
    in Gallery listings when ``published_only=true`` is used.
    """
    from app.prototype.session.store import SessionStore

    store = SessionStore.get()
    sessions = store.get_all()
    found = False
    for s in sessions:
        if s.get("session_id") == session_id:
            found = True
            break

    if not found:
        raise HTTPException(404, f"Session {session_id} not found")

    # Mark as published in the session store
    store.update_field(session_id, "published", True)

    return PublishResponse(
        session_id=session_id,
        published=True,
        message="Successfully published to Gallery",
    )
