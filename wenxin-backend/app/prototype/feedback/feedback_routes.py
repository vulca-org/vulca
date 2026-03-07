"""REST endpoints for the feedback system."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.prototype.api.auth import verify_api_key
from app.prototype.feedback.feedback_store import FeedbackStore
from app.prototype.feedback.types import FeedbackRecord, FeedbackStats, FeedbackSubmit

feedback_router = APIRouter(prefix="/api/v1", tags=["feedback"])


def _hash_key(api_key: str) -> str:
    """Return a truncated SHA-256 hash for privacy-safe storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]


@feedback_router.post("/feedback")
async def submit_feedback(
    req: FeedbackSubmit,
    api_key: str = Depends(verify_api_key),
) -> dict:
    """Submit evaluation feedback (requires API key)."""
    record = FeedbackRecord(
        id=uuid.uuid4().hex,
        evaluation_id=req.evaluation_id,
        rating=req.rating,
        comment=req.comment,
        feedback_type=req.feedback_type,
        timestamp=datetime.now(timezone.utc).isoformat(),
        api_key_hash=_hash_key(api_key),
    )
    store = FeedbackStore.get()
    store.append(record)
    return {"status": "ok", "id": record.id}


@feedback_router.get("/feedback/stats", response_model=FeedbackStats)
async def get_feedback_stats() -> FeedbackStats:
    """Public endpoint — return aggregate feedback statistics."""
    store = FeedbackStore.get()
    return store.get_stats()
