"""Integration tests for the feedback API endpoints.

Covers:
- POST /api/v1/feedback — normal submission → 200
- POST /api/v1/feedback — missing required fields → 422
- POST /api/v1/feedback — no auth → 401
- GET  /api/v1/feedback/stats — returns correct data structure
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import httpx
import pytest
import pytest_asyncio

# Environment must be set before importing the app so Settings picks them up.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-at-least-32-chars")

# Set a known API key for testing (must match other test files)
_TEST_API_KEY = "demo-key"
os.environ["VULCA_API_KEYS"] = _TEST_API_KEY


@pytest_asyncio.fixture
async def client():
    """Async httpx client wired to the FastAPI app via ASGITransport."""
    # Reset auth module's cached key set so it reloads from env
    import app.prototype.api.auth as _auth_mod
    _auth_mod._KEYS = None

    # Redirect FeedbackStore to a temporary file so tests are isolated
    from app.prototype.feedback.feedback_store import FeedbackStore
    _tmpdir = tempfile.mkdtemp()
    _tmp_feedback = str(Path(_tmpdir) / "feedback_test.jsonl")
    FeedbackStore._instance = None
    FeedbackStore._instance = FeedbackStore(path=_tmp_feedback)

    from app.main import app
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    # Cleanup singleton
    FeedbackStore._instance = None


# ---- Helper -----------------------------------------------------------

def _auth_header() -> dict[str, str]:
    return {"Authorization": f"Bearer {_TEST_API_KEY}"}


# ---- POST /api/v1/feedback -------------------------------------------

@pytest.mark.asyncio
async def test_submit_feedback_ok(client: httpx.AsyncClient):
    """Normal submission with valid auth → 200 and status ok."""
    resp = await client.post(
        "/api/v1/feedback",
        json={
            "evaluation_id": "eval-001",
            "rating": "thumbs_up",
            "comment": "good",
        },
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "id" in body


@pytest.mark.asyncio
async def test_submit_feedback_thumbs_down(client: httpx.AsyncClient):
    """Thumbs-down rating also succeeds."""
    resp = await client.post(
        "/api/v1/feedback",
        json={
            "evaluation_id": "eval-002",
            "rating": "thumbs_down",
            "comment": "needs improvement",
            "feedback_type": "explicit",
        },
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_submit_feedback_missing_required_fields(client: httpx.AsyncClient):
    """Missing evaluation_id and rating → 422 validation error."""
    resp = await client.post(
        "/api/v1/feedback",
        json={},
        headers=_auth_header(),
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_submit_feedback_missing_evaluation_id(client: httpx.AsyncClient):
    """Missing evaluation_id only → 422."""
    resp = await client.post(
        "/api/v1/feedback",
        json={"rating": "thumbs_up"},
        headers=_auth_header(),
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_submit_feedback_missing_rating(client: httpx.AsyncClient):
    """Missing rating only → 422."""
    resp = await client.post(
        "/api/v1/feedback",
        json={"evaluation_id": "eval-003"},
        headers=_auth_header(),
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_submit_feedback_no_auth(client: httpx.AsyncClient):
    """Feedback no longer requires auth — should accept without headers."""
    resp = await client.post(
        "/api/v1/feedback",
        json={
            "evaluation_id": "eval-004",
            "rating": "thumbs_up",
        },
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_submit_feedback_with_any_auth(client: httpx.AsyncClient):
    """Feedback ignores auth headers — should accept regardless."""
    resp = await client.post(
        "/api/v1/feedback",
        json={
            "evaluation_id": "eval-005",
            "rating": "thumbs_up",
        },
        headers={"Authorization": "Bearer any-token"},
    )
    assert resp.status_code == 200


# ---- GET /api/v1/feedback/stats --------------------------------------

@pytest.mark.asyncio
async def test_stats_empty(client: httpx.AsyncClient):
    """Stats on empty store → all zeros, correct structure."""
    resp = await client.get("/api/v1/feedback/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_feedback"] == 0
    assert body["thumbs_up"] == 0
    assert body["thumbs_down"] == 0
    assert isinstance(body["by_type"], dict)
    assert isinstance(body["recent_comments"], list)


@pytest.mark.asyncio
async def test_stats_after_submissions(client: httpx.AsyncClient):
    """Submit two feedbacks, then check stats reflect them."""
    # Submit thumbs_up
    await client.post(
        "/api/v1/feedback",
        json={"evaluation_id": "e1", "rating": "thumbs_up", "comment": "great"},
        headers=_auth_header(),
    )
    # Submit thumbs_down
    await client.post(
        "/api/v1/feedback",
        json={"evaluation_id": "e2", "rating": "thumbs_down", "comment": "bad"},
        headers=_auth_header(),
    )

    resp = await client.get("/api/v1/feedback/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_feedback"] == 2
    assert body["thumbs_up"] == 1
    assert body["thumbs_down"] == 1
    assert "explicit" in body["by_type"]
    assert body["by_type"]["explicit"] == 2
    assert len(body["recent_comments"]) == 2


@pytest.mark.asyncio
async def test_stats_no_auth_required(client: httpx.AsyncClient):
    """Stats endpoint is public — no Authorization header needed → 200."""
    resp = await client.get("/api/v1/feedback/stats")
    assert resp.status_code == 200
