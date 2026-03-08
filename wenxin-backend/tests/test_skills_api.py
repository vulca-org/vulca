"""Integration tests for the skills marketplace API (/api/v1/skills).

Covers CRUD, voting, SKILL.md export, and authentication enforcement.

Usage:
    cd wenxin-backend
    PYTHONPATH=. python -m pytest tests/test_skills_api.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set required environment variables BEFORE any app import
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-at-least-32-chars")
os.environ["VULCA_API_KEYS"] = "demo-key"

# Reset cached API keys so our env var takes effect
import app.prototype.api.auth as _auth_mod
_auth_mod._KEYS = None

from fastapi.testclient import TestClient

from app.main import app
import app.prototype.skills.api.skill_routes as _skill_mod

# ---------------------------------------------------------------------------
# Fixtures — redirect JSONL storage to temp directory per test
# ---------------------------------------------------------------------------

AUTH_HEADER = {"Authorization": "Bearer demo-key"}


@pytest.fixture(autouse=True)
def _isolate_jsonl_storage(tmp_path: Path):
    """Redirect JSONL files to a temp dir so tests never touch real data.
    Also reset the rate limiter so tests don't hit the 30 req/min ceiling.
    """
    orig_skills = _skill_mod.SKILLS_JSONL
    orig_votes = _skill_mod.VOTES_JSONL

    _skill_mod.SKILLS_JSONL = tmp_path / "skills_marketplace.jsonl"
    _skill_mod.VOTES_JSONL = tmp_path / "skills_votes.jsonl"

    # Reset rate limiter windows between tests
    _auth_mod._RATE_WINDOWS.clear()

    yield

    _skill_mod.SKILLS_JSONL = orig_skills
    _skill_mod.VOTES_JSONL = orig_votes


@pytest.fixture()
def client():
    """Sync TestClient for the FastAPI app."""
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_skill(client: TestClient, **overrides) -> dict:
    """Helper: create a skill and return the response JSON."""
    payload = {
        "name": "Test Skill",
        "description": "A test skill for integration tests.",
        "tags": ["test", "integration"],
        "author": "pytest",
    }
    payload.update(overrides)
    resp = client.post("/api/v1/skills", json=payload, headers=AUTH_HEADER)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ===========================================================================
# Tests: GET /api/v1/skills — list
# ===========================================================================

class TestListSkills:
    def test_list_returns_array(self, client):
        resp = client.get("/api/v1/skills")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_empty_initially(self, client):
        resp = client.get("/api/v1/skills")
        assert resp.json() == []

    def test_list_contains_created_skill(self, client):
        _create_skill(client, name="Listed Skill")
        resp = client.get("/api/v1/skills")
        names = [s["name"] for s in resp.json()]
        assert "Listed Skill" in names

    def test_list_does_not_require_auth(self, client):
        """GET /skills is public — no Authorization header needed."""
        resp = client.get("/api/v1/skills")
        assert resp.status_code == 200


# ===========================================================================
# Tests: POST /api/v1/skills — create
# ===========================================================================

class TestCreateSkill:
    def test_create_returns_201(self, client):
        resp = client.post(
            "/api/v1/skills",
            json={
                "name": "Brand Check",
                "description": "Check brand consistency.",
                "tags": ["brand"],
                "author": "tester",
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_create_returns_full_object(self, client):
        data = _create_skill(client, name="Full Object Skill")
        assert "id" in data
        assert data["name"] == "Full Object Skill"
        assert data["version"] == "1.0.0"
        assert "created_at" in data

    def test_create_defaults_author(self, client):
        resp = client.post(
            "/api/v1/skills",
            json={"name": "No Author", "description": "Skill without explicit author."},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 201
        assert resp.json()["author"] == "anonymous"

    def test_create_without_auth_returns_401(self, client):
        resp = client.post(
            "/api/v1/skills",
            json={"name": "Unauthorized", "description": "Should fail."},
        )
        assert resp.status_code == 401

    def test_create_with_bad_token_returns_403(self, client):
        resp = client.post(
            "/api/v1/skills",
            json={"name": "Bad Token", "description": "Should fail."},
            headers={"Authorization": "Bearer wrong-key"},
        )
        assert resp.status_code == 403


# ===========================================================================
# Tests: GET /api/v1/skills/{id} — get single
# ===========================================================================

class TestGetSkill:
    def test_get_existing_skill(self, client):
        created = _create_skill(client)
        resp = client.get(f"/api/v1/skills/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]
        assert resp.json()["name"] == created["name"]

    def test_get_nonexistent_skill_returns_404(self, client):
        resp = client.get("/api/v1/skills/nonexistent-id-999")
        assert resp.status_code == 404

    def test_get_skill_includes_vote_counts(self, client):
        created = _create_skill(client)
        resp = client.get(f"/api/v1/skills/{created['id']}")
        data = resp.json()
        assert "upvotes" in data
        assert "downvotes" in data
        assert data["upvotes"] == 0
        assert data["downvotes"] == 0


# ===========================================================================
# Tests: PUT /api/v1/skills/{id} — update
# ===========================================================================

class TestUpdateSkill:
    def test_update_description(self, client):
        created = _create_skill(client)
        resp = client.put(
            f"/api/v1/skills/{created['id']}",
            json={"description": "Updated description."},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 200
        assert resp.json()["description"] == "Updated description."

    def test_update_tags(self, client):
        created = _create_skill(client)
        resp = client.put(
            f"/api/v1/skills/{created['id']}",
            json={"tags": ["new-tag", "updated"]},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 200
        assert resp.json()["tags"] == ["new-tag", "updated"]

    def test_update_preserves_unchanged_fields(self, client):
        created = _create_skill(client, name="Preserve Test", tags=["original"])
        resp = client.put(
            f"/api/v1/skills/{created['id']}",
            json={"description": "Only description changed."},
            headers=AUTH_HEADER,
        )
        data = resp.json()
        assert data["name"] == "Preserve Test"
        assert data["tags"] == ["original"]

    def test_update_nonexistent_returns_404(self, client):
        resp = client.put(
            "/api/v1/skills/does-not-exist",
            json={"description": "nope"},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 404

    def test_update_without_auth_returns_401(self, client):
        created = _create_skill(client)
        resp = client.put(
            f"/api/v1/skills/{created['id']}",
            json={"description": "No auth."},
        )
        assert resp.status_code == 401


# ===========================================================================
# Tests: DELETE /api/v1/skills/{id} — delete
# ===========================================================================

class TestDeleteSkill:
    def test_delete_returns_204(self, client):
        created = _create_skill(client)
        resp = client.delete(
            f"/api/v1/skills/{created['id']}",
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 204

    def test_delete_removes_from_list(self, client):
        created = _create_skill(client)
        client.delete(f"/api/v1/skills/{created['id']}", headers=AUTH_HEADER)
        resp = client.get("/api/v1/skills")
        ids = [s["id"] for s in resp.json()]
        assert created["id"] not in ids

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.delete(
            "/api/v1/skills/does-not-exist",
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 404

    def test_delete_without_auth_returns_401(self, client):
        created = _create_skill(client)
        resp = client.delete(f"/api/v1/skills/{created['id']}")
        assert resp.status_code == 401


# ===========================================================================
# Tests: POST /api/v1/skills/{id}/vote — vote
# ===========================================================================

class TestVoteSkill:
    def test_upvote_returns_201(self, client):
        created = _create_skill(client)
        resp = client.post(
            f"/api/v1/skills/{created['id']}/vote",
            json={"direction": "up"},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 201

    def test_upvote_increments_count(self, client):
        created = _create_skill(client)
        client.post(
            f"/api/v1/skills/{created['id']}/vote",
            json={"direction": "up"},
            headers=AUTH_HEADER,
        )
        resp = client.post(
            f"/api/v1/skills/{created['id']}/vote",
            json={"direction": "up"},
            headers=AUTH_HEADER,
        )
        data = resp.json()
        assert data["upvotes"] == 2
        assert data["downvotes"] == 0

    def test_downvote(self, client):
        created = _create_skill(client)
        resp = client.post(
            f"/api/v1/skills/{created['id']}/vote",
            json={"direction": "down"},
            headers=AUTH_HEADER,
        )
        data = resp.json()
        assert data["downvotes"] == 1

    def test_vote_reflected_in_get(self, client):
        created = _create_skill(client)
        client.post(
            f"/api/v1/skills/{created['id']}/vote",
            json={"direction": "up"},
            headers=AUTH_HEADER,
        )
        resp = client.get(f"/api/v1/skills/{created['id']}")
        assert resp.json()["upvotes"] == 1

    def test_vote_nonexistent_skill_returns_404(self, client):
        resp = client.post(
            "/api/v1/skills/no-such-skill/vote",
            json={"direction": "up"},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 404

    def test_vote_invalid_direction_returns_422(self, client):
        created = _create_skill(client)
        resp = client.post(
            f"/api/v1/skills/{created['id']}/vote",
            json={"direction": "sideways"},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 422

    def test_vote_without_auth_returns_401(self, client):
        created = _create_skill(client)
        resp = client.post(
            f"/api/v1/skills/{created['id']}/vote",
            json={"direction": "up"},
        )
        assert resp.status_code == 401


# ===========================================================================
# Tests: GET /api/v1/skills/{name}/skill-md — SKILL.md export
# ===========================================================================

class TestSkillMdExport:
    def test_builtin_skill_returns_markdown(self, client):
        """If a built-in skill is registered, export returns text/markdown."""
        # Register a built-in skill in the registry for this test
        from app.prototype.skills import SkillDef, SkillRegistry

        SkillRegistry.reset_instance()
        registry = SkillRegistry()
        registry.register(SkillDef(
            name="test_export",
            description="A test skill for SKILL.md export.",
            tags=["test"],
        ))
        SkillRegistry._instance = registry

        resp = client.get("/api/v1/skills/test_export/skill-md")
        assert resp.status_code == 200
        assert "text/markdown" in resp.headers.get("content-type", "")
        assert "test_export" in resp.text
        assert "A test skill for SKILL.md export." in resp.text

        # Clean up
        SkillRegistry.reset_instance()

    def test_nonexistent_builtin_returns_404(self, client):
        """Requesting SKILL.md for a non-registered built-in skill gives 404."""
        SkillRegistry_cls = __import__(
            "app.prototype.skills.skill_registry", fromlist=["SkillRegistry"]
        ).SkillRegistry
        SkillRegistry_cls.reset_instance()

        resp = client.get("/api/v1/skills/no_such_builtin/skill-md")
        assert resp.status_code == 404

        SkillRegistry_cls.reset_instance()


# ===========================================================================
# Tests: Authentication edge cases
# ===========================================================================

class TestAuthEdgeCases:
    def test_missing_bearer_prefix(self, client):
        """Authorization header without 'Bearer ' prefix."""
        resp = client.post(
            "/api/v1/skills",
            json={"name": "Bad Format", "description": "test"},
            headers={"Authorization": "demo-key"},
        )
        assert resp.status_code == 401

    def test_empty_bearer_token(self, client):
        """Authorization: Bearer (empty token)."""
        resp = client.post(
            "/api/v1/skills",
            json={"name": "Empty Token", "description": "test"},
            headers={"Authorization": "Bearer "},
        )
        assert resp.status_code == 403

    def test_read_endpoints_are_public(self, client):
        """GET list and GET single do not require auth."""
        resp_list = client.get("/api/v1/skills")
        assert resp_list.status_code == 200

        # GET single — 404 is expected (no skill exists), not 401
        resp_single = client.get("/api/v1/skills/nonexistent")
        assert resp_single.status_code == 404
