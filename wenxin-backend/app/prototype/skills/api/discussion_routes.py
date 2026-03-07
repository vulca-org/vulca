"""Skill discussion / comment thread endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.prototype.api.auth import verify_api_key
from app.prototype.skills.jsonl_store import read_jsonl, write_jsonl, append_jsonl

discussion_router = APIRouter(prefix="/api/v1/skills", tags=["skill-discussions"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
SKILLS_JSONL = DATA_DIR / "skills_marketplace.jsonl"
DISCUSSIONS_JSONL = DATA_DIR / "skills_discussions.jsonl"
DISCUSSION_VOTES_JSONL = DATA_DIR / "skills_discussion_votes.jsonl"


# --------------- Schemas ---------------

class CommentCreate(BaseModel):
    content: str
    comment_type: str = Field(
        default="comment",
        pattern="^(comment|review|upgrade_proposal)$",
        description="Type: comment, review, or upgrade_proposal",
    )
    author: str = "anonymous"


class CommentItem(BaseModel):
    id: str
    skill_id: str
    content: str
    comment_type: str
    author: str
    created_at: str
    upvotes: int = 0


# --------------- Helpers ---------------

def _comment_upvotes(comment_id: str) -> int:
    """Return upvote count for a comment."""
    votes = read_jsonl(DISCUSSION_VOTES_JSONL)
    return sum(1 for v in votes if v.get("comment_id") == comment_id and v.get("direction") == "up")


def _enrich_comment(c: dict) -> dict:
    """Add computed upvote count to a raw comment record."""
    return {
        "id": c["id"],
        "skill_id": c["skill_id"],
        "content": c["content"],
        "comment_type": c.get("comment_type", "comment"),
        "author": c.get("author", "anonymous"),
        "created_at": c["created_at"],
        "upvotes": _comment_upvotes(c["id"]),
    }


def _skill_exists(skill_id: str) -> bool:
    skills = read_jsonl(SKILLS_JSONL)
    return any(s["id"] == skill_id for s in skills)


# --------------- Endpoints ---------------

@discussion_router.get("/{skill_id}/discussions", response_model=list[CommentItem])
async def list_discussions(skill_id: str):
    """List all comments for a skill (public)."""
    if not _skill_exists(skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")
    comments = read_jsonl(DISCUSSIONS_JSONL)
    filtered = [c for c in comments if c.get("skill_id") == skill_id]
    return [_enrich_comment(c) for c in filtered]


@discussion_router.post("/{skill_id}/discussions", response_model=CommentItem, status_code=201)
async def add_comment(skill_id: str, body: CommentCreate, _key: str = Depends(verify_api_key)):
    """Add a comment to a skill discussion (auth required)."""
    if not _skill_exists(skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")
    record = {
        "id": uuid.uuid4().hex[:12],
        "skill_id": skill_id,
        "content": body.content,
        "comment_type": body.comment_type,
        "author": body.author,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    append_jsonl(DISCUSSIONS_JSONL, record)
    return _enrich_comment(record)


@discussion_router.post("/{skill_id}/discussions/{comment_id}/vote", status_code=201)
async def vote_comment(skill_id: str, comment_id: str, _key: str = Depends(verify_api_key)):
    """Upvote a comment (auth required)."""
    if not _skill_exists(skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")
    comments = read_jsonl(DISCUSSIONS_JSONL)
    if not any(c["id"] == comment_id and c.get("skill_id") == skill_id for c in comments):
        raise HTTPException(status_code=404, detail="Comment not found")
    vote_record = {
        "id": uuid.uuid4().hex[:12],
        "comment_id": comment_id,
        "skill_id": skill_id,
        "direction": "up",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    append_jsonl(DISCUSSION_VOTES_JSONL, vote_record)
    return {"comment_id": comment_id, "upvotes": _comment_upvotes(comment_id)}
