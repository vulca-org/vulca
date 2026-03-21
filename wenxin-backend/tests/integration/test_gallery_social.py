"""Integration tests for Gallery and Social endpoints.

Tests:
- GET /api/v1/prototype/gallery — list gallery items, verify schema
- Gallery filtering by tradition
- Gallery sorting (newest, score, rounds, likes)
- POST /api/v1/prototype/gallery/{session_id}/like
- GET /api/v1/prototype/gallery/likes
- POST /api/v1/prototype/gallery/{session_id}/publish

All tests use mock/in-memory state via TestClient — no real Gemini calls.
Do NOT use @pytest.mark.integration here.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TEST_API_KEY = "gallery-test-key"


@pytest.fixture(scope="module")
def client():
    """TestClient with gallery + social routes mounted."""
    os.environ["VULCA_API_KEYS"] = _TEST_API_KEY

    # Reset cached auth keys
    import app.prototype.api.auth as _auth
    _auth._KEYS = None

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.main import app as main_app

    with TestClient(main_app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope="module")
def seeded_session_id(client):
    """Create a mock pipeline run so the Gallery has at least one item.

    Uses provider=mock so no real API key is needed.
    """
    resp = client.post(
        "/api/v1/prototype/runs",
        json={
            "subject": "Gallery test artwork — ink wash mountain",
            "tradition": "chinese_xieyi",
            "provider": "mock",
            "max_rounds": 1,
        },
    )
    assert resp.status_code == 200, f"Failed to create run: {resp.text}"
    task_id = resp.json()["task_id"]

    # Poll until completed (mock pipeline is fast)
    deadline = time.time() + 30
    while time.time() < deadline:
        status_resp = client.get(f"/api/v1/prototype/runs/{task_id}")
        assert status_resp.status_code == 200
        status = status_resp.json()["status"]
        if status in ("completed", "failed"):
            break
        time.sleep(0.3)

    return task_id


# ---------------------------------------------------------------------------
# 1. Gallery list — schema validation
# ---------------------------------------------------------------------------

class TestGalleryList:
    """GET /api/v1/prototype/gallery — basic list and schema."""

    def test_gallery_returns_200(self, client):
        resp = client.get("/api/v1/prototype/gallery")
        assert resp.status_code == 200, resp.text

    def test_gallery_schema_has_items_and_total(self, client):
        resp = client.get("/api/v1/prototype/gallery")
        body = resp.json()
        assert "items" in body, "Response must contain 'items' key"
        assert "total" in body, "Response must contain 'total' key"
        assert isinstance(body["items"], list)
        assert isinstance(body["total"], int)
        assert body["total"] >= 0

    def test_gallery_item_schema(self, client, seeded_session_id):
        """Each gallery item must have the required fields."""
        resp = client.get("/api/v1/prototype/gallery?limit=200")
        body = resp.json()
        items = body["items"]

        # The seeded run should eventually appear; check schema on any item
        if not items:
            pytest.skip("Gallery is empty — seeded session not yet digested")

        item = items[0]
        required_fields = {
            "id", "subject", "tradition", "scores", "overall",
            "best_image_url", "total_rounds", "created_at", "likes_count",
        }
        missing = required_fields - set(item.keys())
        assert not missing, f"Gallery item missing fields: {missing}"

    def test_gallery_scores_are_numeric(self, client):
        resp = client.get("/api/v1/prototype/gallery?limit=50")
        body = resp.json()
        for item in body["items"]:
            assert isinstance(item["overall"], (int, float)), (
                f"'overall' must be numeric, got {type(item['overall'])}"
            )
            for dim, score in item.get("scores", {}).items():
                assert isinstance(score, (int, float)), (
                    f"Score for {dim} must be numeric"
                )

    def test_gallery_pagination_limit(self, client):
        resp = client.get("/api/v1/prototype/gallery?limit=1")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["items"]) <= 1

    def test_gallery_pagination_offset(self, client):
        resp_all = client.get("/api/v1/prototype/gallery?limit=200")
        total = resp_all.json()["total"]
        if total < 2:
            pytest.skip("Need at least 2 items to test offset")

        resp_offset = client.get("/api/v1/prototype/gallery?limit=1&offset=1")
        assert resp_offset.status_code == 200
        # Item at offset=1 should differ from item at offset=0
        resp_first = client.get("/api/v1/prototype/gallery?limit=1&offset=0")
        id_first = resp_first.json()["items"][0]["id"]
        id_second = resp_offset.json()["items"][0]["id"]
        assert id_first != id_second

    def test_gallery_limit_validation_too_large(self, client):
        """limit > 200 should be rejected with 422."""
        resp = client.get("/api/v1/prototype/gallery?limit=201")
        assert resp.status_code == 422

    def test_gallery_limit_validation_zero(self, client):
        """limit=0 should be rejected with 422."""
        resp = client.get("/api/v1/prototype/gallery?limit=0")
        assert resp.status_code == 422

    def test_gallery_offset_negative_rejected(self, client):
        """Negative offset should be rejected with 422."""
        resp = client.get("/api/v1/prototype/gallery?offset=-1")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 2. Gallery filtering
# ---------------------------------------------------------------------------

class TestGalleryFiltering:
    """Gallery filter params: tradition, subject, min_score, max_score, published_only."""

    def test_filter_by_tradition(self, client):
        resp = client.get("/api/v1/prototype/gallery?tradition=chinese_xieyi&limit=100")
        assert resp.status_code == 200
        body = resp.json()
        for item in body["items"]:
            assert item["tradition"] == "chinese_xieyi", (
                f"Tradition filter violated: got {item['tradition']}"
            )

    def test_filter_by_nonexistent_tradition_returns_empty(self, client):
        resp = client.get("/api/v1/prototype/gallery?tradition=__no_such_tradition__")
        assert resp.status_code == 200
        body = resp.json()
        assert body["items"] == []
        assert body["total"] == 0

    def test_filter_by_subject(self, client):
        resp = client.get("/api/v1/prototype/gallery?subject=Gallery+test")
        assert resp.status_code == 200
        body = resp.json()
        for item in body["items"]:
            assert "gallery test" in item["subject"].lower(), (
                f"Subject filter violated: {item['subject']}"
            )

    def test_filter_min_score(self, client):
        resp = client.get("/api/v1/prototype/gallery?min_score=0.99&limit=100")
        assert resp.status_code == 200
        body = resp.json()
        for item in body["items"]:
            assert item["overall"] >= 0.99, (
                f"min_score filter violated: {item['overall']}"
            )

    def test_filter_max_score(self, client):
        resp = client.get("/api/v1/prototype/gallery?max_score=0.01&limit=100")
        assert resp.status_code == 200
        body = resp.json()
        for item in body["items"]:
            assert item["overall"] <= 0.01, (
                f"max_score filter violated: {item['overall']}"
            )

    def test_published_only_returns_subset(self, client):
        """published_only=true must return <= total items."""
        resp_all = client.get("/api/v1/prototype/gallery?limit=200")
        resp_pub = client.get("/api/v1/prototype/gallery?published_only=true&limit=200")
        assert resp_pub.status_code == 200
        assert resp_pub.json()["total"] <= resp_all.json()["total"]


# ---------------------------------------------------------------------------
# 3. Gallery sorting
# ---------------------------------------------------------------------------

class TestGallerySorting:
    """Gallery sort_by and sort_order params."""

    def _get_items(self, client, sort_by: str, sort_order: str = "desc") -> list[dict]:
        resp = client.get(
            f"/api/v1/prototype/gallery?sort_by={sort_by}&sort_order={sort_order}&limit=200"
        )
        assert resp.status_code == 200, resp.text
        return resp.json()["items"]

    def test_sort_by_newest_desc(self, client):
        items = self._get_items(client, "newest", "desc")
        if len(items) < 2:
            pytest.skip("Need at least 2 items to test sort order")
        timestamps = [item["created_at"] for item in items]
        assert timestamps == sorted(timestamps, reverse=True), (
            "sort_by=newest desc should yield descending created_at"
        )

    def test_sort_by_newest_asc(self, client):
        items = self._get_items(client, "newest", "asc")
        if len(items) < 2:
            pytest.skip("Need at least 2 items to test sort order")
        timestamps = [item["created_at"] for item in items]
        assert timestamps == sorted(timestamps), (
            "sort_by=newest asc should yield ascending created_at"
        )

    def test_sort_by_score_desc(self, client):
        items = self._get_items(client, "score", "desc")
        if len(items) < 2:
            pytest.skip("Need at least 2 items to test sort order")
        scores = [item["overall"] for item in items]
        assert scores == sorted(scores, reverse=True), (
            "sort_by=score desc should yield descending overall score"
        )

    def test_sort_by_score_asc(self, client):
        items = self._get_items(client, "score", "asc")
        if len(items) < 2:
            pytest.skip("Need at least 2 items to test sort order")
        scores = [item["overall"] for item in items]
        assert scores == sorted(scores), (
            "sort_by=score asc should yield ascending overall score"
        )

    def test_sort_by_rounds_desc(self, client):
        items = self._get_items(client, "rounds", "desc")
        if len(items) < 2:
            pytest.skip("Need at least 2 items to test sort order")
        rounds = [item["total_rounds"] for item in items]
        assert rounds == sorted(rounds, reverse=True), (
            "sort_by=rounds desc should yield descending total_rounds"
        )

    def test_sort_by_likes_desc(self, client):
        items = self._get_items(client, "likes", "desc")
        if len(items) < 2:
            pytest.skip("Need at least 2 items to test sort order")
        likes = [item["likes_count"] for item in items]
        assert likes == sorted(likes, reverse=True), (
            "sort_by=likes desc should yield descending likes_count"
        )

    def test_unknown_sort_by_falls_back_gracefully(self, client):
        """Unknown sort_by should not crash — fallback to created_at."""
        resp = client.get("/api/v1/prototype/gallery?sort_by=__garbage__")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 4. Social — Like endpoint
# ---------------------------------------------------------------------------

class TestGalleryLike:
    """POST /api/v1/prototype/gallery/{session_id}/like."""

    def test_like_existing_session_returns_200(self, client, seeded_session_id):
        resp = client.post(
            f"/api/v1/prototype/gallery/{seeded_session_id}/like"
        )
        # Like endpoint uses gallery_social_router which is always open
        assert resp.status_code == 200, resp.text

    def test_like_response_schema(self, client, seeded_session_id):
        resp = client.post(
            f"/api/v1/prototype/gallery/{seeded_session_id}/like"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "session_id" in body
        assert "likes" in body
        assert isinstance(body["likes"], int)
        assert body["likes"] >= 1

    def test_like_increments_count(self, client, seeded_session_id):
        resp1 = client.post(
            f"/api/v1/prototype/gallery/{seeded_session_id}/like"
        )
        resp2 = client.post(
            f"/api/v1/prototype/gallery/{seeded_session_id}/like"
        )
        assert resp2.json()["likes"] > resp1.json()["likes"]

    def test_like_with_client_id(self, client, seeded_session_id):
        resp = client.post(
            f"/api/v1/prototype/gallery/{seeded_session_id}/like?client_id=test-user-123"
        )
        assert resp.status_code == 200
        assert resp.json()["session_id"] == seeded_session_id

    def test_like_nonexistent_session_still_works(self, client):
        """Like endpoint does not require session to exist (optimistic social)."""
        resp = client.post(
            "/api/v1/prototype/gallery/nonexistent-session-xyz/like"
        )
        assert resp.status_code == 200

    def test_get_all_likes(self, client, seeded_session_id):
        # Ensure at least one like exists
        client.post(f"/api/v1/prototype/gallery/{seeded_session_id}/like")

        resp = client.get("/api/v1/prototype/gallery/likes")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict), "GET /gallery/likes must return a dict"
        # All values should be non-negative integers
        for session_id, count in body.items():
            assert isinstance(count, int) and count >= 0, (
                f"Like count for {session_id} must be a non-negative int"
            )


# ---------------------------------------------------------------------------
# 5. Social — Publish endpoint
# ---------------------------------------------------------------------------

class TestGalleryPublish:
    """POST /api/v1/prototype/gallery/{session_id}/publish."""

    def test_publish_existing_session(self, client, seeded_session_id):
        resp = client.post(
            f"/api/v1/prototype/gallery/{seeded_session_id}/publish"
        )
        # May be 200 (found) or 404 (not yet in store) depending on timing
        assert resp.status_code in (200, 404), (
            f"Publish returned unexpected status {resp.status_code}: {resp.text}"
        )

    def test_publish_response_schema(self, client, seeded_session_id):
        resp = client.post(
            f"/api/v1/prototype/gallery/{seeded_session_id}/publish"
        )
        if resp.status_code == 200:
            body = resp.json()
            assert "session_id" in body
            assert "published" in body
            assert "message" in body
            assert body["published"] is True
            assert body["session_id"] == seeded_session_id

    def test_publish_nonexistent_session_returns_404(self, client):
        resp = client.post(
            "/api/v1/prototype/gallery/definitely-not-a-real-session-id-abc123/publish"
        )
        assert resp.status_code == 404

    def test_published_items_appear_in_published_only_filter(self, client, seeded_session_id):
        """After publishing, item should appear when published_only=true."""
        pub_resp = client.post(
            f"/api/v1/prototype/gallery/{seeded_session_id}/publish"
        )
        if pub_resp.status_code != 200:
            pytest.skip("Session not yet in store — skip published_only filter check")

        gallery_resp = client.get(
            "/api/v1/prototype/gallery?published_only=true&limit=200"
        )
        assert gallery_resp.status_code == 200
        ids = [item["id"] for item in gallery_resp.json()["items"]]
        assert seeded_session_id in ids, (
            f"Published session {seeded_session_id} should appear in published_only=true results"
        )
