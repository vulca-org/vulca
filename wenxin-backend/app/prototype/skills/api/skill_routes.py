"""Skill marketplace CRUD and voting endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.prototype.api.auth import verify_api_key
from app.prototype.skills.jsonl_store import read_jsonl, write_jsonl, append_jsonl

skill_api_router = APIRouter(prefix="/api/v1/skills", tags=["skills"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
SKILLS_JSONL = DATA_DIR / "skills_marketplace.jsonl"
VOTES_JSONL = DATA_DIR / "skills_votes.jsonl"


# --------------- Schemas ---------------

class SkillCreate(BaseModel):
    name: str
    description: str
    tags: list[str] = []
    config: dict = {}
    author: str = "anonymous"


class SkillUpdate(BaseModel):
    description: str | None = None
    tags: list[str] | None = None
    config: dict | None = None


class SkillListItem(BaseModel):
    id: str
    name: str
    description: str
    tags: list[str]
    author: str
    version: str
    created_at: str
    upvotes: int = 0
    downvotes: int = 0


class VoteRequest(BaseModel):
    direction: str = Field(..., pattern="^(up|down)$", description="Vote direction: 'up' or 'down'")


# --------------- Helpers ---------------

def _vote_counts(skill_id: str) -> tuple[int, int]:
    """Return (upvotes, downvotes) for a given skill."""
    votes = read_jsonl(VOTES_JSONL)
    up = sum(1 for v in votes if v.get("skill_id") == skill_id and v.get("direction") == "up")
    down = sum(1 for v in votes if v.get("skill_id") == skill_id and v.get("direction") == "down")
    return up, down


def _skill_to_list_item(skill: dict) -> dict:
    """Enrich a raw skill record with vote counts."""
    up, down = _vote_counts(skill["id"])
    return {
        "id": skill["id"],
        "name": skill["name"],
        "description": skill["description"],
        "tags": skill.get("tags", []),
        "author": skill.get("author", "anonymous"),
        "version": skill.get("version", "1.0.0"),
        "created_at": skill["created_at"],
        "upvotes": up,
        "downvotes": down,
    }


# --------------- Endpoints ---------------

@skill_api_router.get("", response_model=list[SkillListItem])
async def list_skills():
    """List all skills (public)."""
    skills = read_jsonl(SKILLS_JSONL)
    return [_skill_to_list_item(s) for s in skills]


@skill_api_router.get("/{skill_id}", response_model=SkillListItem)
async def get_skill(skill_id: str):
    """Get a single skill by ID (public)."""
    skills = read_jsonl(SKILLS_JSONL)
    for s in skills:
        if s["id"] == skill_id:
            return _skill_to_list_item(s)
    raise HTTPException(status_code=404, detail="Skill not found")


@skill_api_router.post("", response_model=SkillListItem, status_code=201)
async def create_skill(body: SkillCreate, _key: str = Depends(verify_api_key)):
    """Create a new skill (auth required)."""
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "id": uuid.uuid4().hex[:12],
        "name": body.name,
        "description": body.description,
        "tags": body.tags,
        "config": body.config,
        "author": body.author,
        "version": "1.0.0",
        "created_at": now,
        "updated_at": now,
    }
    append_jsonl(SKILLS_JSONL, record)
    return _skill_to_list_item(record)


@skill_api_router.put("/{skill_id}", response_model=SkillListItem)
async def update_skill(skill_id: str, body: SkillUpdate, _key: str = Depends(verify_api_key)):
    """Update an existing skill (auth required)."""
    skills = read_jsonl(SKILLS_JSONL)
    for s in skills:
        if s["id"] == skill_id:
            if body.description is not None:
                s["description"] = body.description
            if body.tags is not None:
                s["tags"] = body.tags
            if body.config is not None:
                s["config"] = body.config
            s["updated_at"] = datetime.now(timezone.utc).isoformat()
            write_jsonl(SKILLS_JSONL, skills)
            return _skill_to_list_item(s)
    raise HTTPException(status_code=404, detail="Skill not found")


@skill_api_router.delete("/{skill_id}", status_code=204)
async def delete_skill(skill_id: str, _key: str = Depends(verify_api_key)):
    """Delete a skill (auth required)."""
    skills = read_jsonl(SKILLS_JSONL)
    filtered = [s for s in skills if s["id"] != skill_id]
    if len(filtered) == len(skills):
        raise HTTPException(status_code=404, detail="Skill not found")
    write_jsonl(SKILLS_JSONL, filtered)
    return None


@skill_api_router.post("/{skill_id}/vote", status_code=201)
async def vote_skill(skill_id: str, body: VoteRequest, _key: str = Depends(verify_api_key)):
    """Upvote or downvote a skill (auth required)."""
    # Verify skill exists
    skills = read_jsonl(SKILLS_JSONL)
    if not any(s["id"] == skill_id for s in skills):
        raise HTTPException(status_code=404, detail="Skill not found")
    vote_record = {
        "id": uuid.uuid4().hex[:12],
        "skill_id": skill_id,
        "direction": body.direction,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    append_jsonl(VOTES_JSONL, vote_record)
    up, down = _vote_counts(skill_id)
    return {"skill_id": skill_id, "upvotes": up, "downvotes": down}


@skill_api_router.get("/{skill_name}/skill-md")
async def get_skill_md(skill_name: str):
    """Export a built-in skill as SKILL.md format (public)."""
    from fastapi.responses import PlainTextResponse

    from app.prototype.skills import SkillRegistry, export_skill_md

    registry = SkillRegistry.get_instance()
    skill = registry.get(skill_name)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Built-in skill '{skill_name}' not found")
    md = export_skill_md(skill)
    return PlainTextResponse(content=md, media_type="text/markdown")
