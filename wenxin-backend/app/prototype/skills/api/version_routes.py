"""Skill version history endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.prototype.api.auth import verify_api_key
from app.prototype.skills.jsonl_store import read_jsonl, write_jsonl, append_jsonl

version_router = APIRouter(prefix="/api/v1/skills", tags=["skill-versions"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
SKILLS_JSONL = DATA_DIR / "skills_marketplace.jsonl"
VERSIONS_JSONL = DATA_DIR / "skills_versions.jsonl"


# --------------- Schemas ---------------

class VersionCreate(BaseModel):
    version: str
    changelog: str
    config: dict = {}


class VersionItem(BaseModel):
    id: str
    skill_id: str
    version: str
    changelog: str
    created_at: str


# --------------- Helpers ---------------

def _skill_exists(skill_id: str) -> bool:
    skills = read_jsonl(SKILLS_JSONL)
    return any(s["id"] == skill_id for s in skills)


# --------------- Endpoints ---------------

@version_router.get("/{skill_id}/versions", response_model=list[VersionItem])
async def list_versions(skill_id: str):
    """List all versions for a skill (public)."""
    if not _skill_exists(skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")
    versions = read_jsonl(VERSIONS_JSONL)
    filtered = [v for v in versions if v.get("skill_id") == skill_id]
    return filtered


@version_router.post("/{skill_id}/versions", response_model=VersionItem, status_code=201)
async def create_version(skill_id: str, body: VersionCreate, _key: str = Depends(verify_api_key)):
    """Create a new version for a skill (auth required).

    Also updates the skill's current version string.
    """
    if not _skill_exists(skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")

    now = datetime.now(timezone.utc).isoformat()
    record = {
        "id": uuid.uuid4().hex[:12],
        "skill_id": skill_id,
        "version": body.version,
        "changelog": body.changelog,
        "config": body.config,
        "created_at": now,
    }
    append_jsonl(VERSIONS_JSONL, record)

    # Update the skill's current version
    skills = read_jsonl(SKILLS_JSONL)
    for s in skills:
        if s["id"] == skill_id:
            s["version"] = body.version
            s["updated_at"] = now
            if body.config:
                s["config"] = body.config
            break
    write_jsonl(SKILLS_JSONL, skills)

    return {
        "id": record["id"],
        "skill_id": record["skill_id"],
        "version": record["version"],
        "changelog": record["changelog"],
        "created_at": record["created_at"],
    }
