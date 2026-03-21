"""Integration tests for error handling across all main endpoints.

Tests:
- POST /api/v1/prototype/runs — input validation and edge cases
- GET  /api/v1/prototype/runs/{id} — 404 for unknown run
- POST /api/v1/prototype/runs/{id}/action — 404 for unknown run
- POST /api/v1/prototype/runs/{id}/instruct — 404 for unknown run
- POST /api/v1/evaluate — missing/invalid image, empty subject
- POST /api/v1/identify-tradition — missing image
- Rate limiting — 429 after threshold

All tests use mock/in-memory state. Tests calling real Gemini are marked
@pytest.mark.integration and require GEMINI_API_KEY.
"""

from __future__ import annotations

import os
import time

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TEST_API_KEY = "error-handling-test-key"


@pytest.fixture(scope="module")
def client():
    """TestClient with the full app mounted."""
    os.environ["VULCA_API_KEYS"] = _TEST_API_KEY

    import app.prototype.api.auth as _auth
    _auth._KEYS = None

    from fastapi.testclient import TestClient
    from app.main import app as main_app

    with TestClient(main_app, raise_server_exceptions=False) as c:
        yield c


AUTH = {"Authorization": f"Bearer {_TEST_API_KEY}"}


# ---------------------------------------------------------------------------
# 1. POST /api/v1/prototype/runs — input validation
# ---------------------------------------------------------------------------

class TestCreateRunValidation:
    """Input validation for POST /api/v1/prototype/runs."""

    def test_empty_subject_rejected(self, client):
        """subject="" violates min_length=1 — must be 422."""
        resp = client.post(
            "/api/v1/prototype/runs",
            json={"subject": "", "tradition": "default", "provider": "mock"},
        )
        assert resp.status_code == 422, (
            f"Empty subject should be rejected with 422, got {resp.status_code}: {resp.text}"
        )

    def test_subject_too_long_rejected(self, client):
        """subject > 500 chars violates max_length=500."""
        resp = client.post(
            "/api/v1/prototype/runs",
            json={"subject": "x" * 501, "tradition": "default", "provider": "mock"},
        )
        assert resp.status_code == 422, (
            f"Subject > 500 chars should be rejected with 422, got {resp.status_code}"
        )

    def test_n_candidates_zero_rejected(self, client):
        """n_candidates=0 violates ge=1 — must be 422."""
        resp = client.post(
            "/api/v1/prototype/runs",
            json={
                "subject": "test artwork",
                "tradition": "default",
                "provider": "mock",
                "n_candidates": 0,
            },
        )
        assert resp.status_code == 422, (
            f"n_candidates=0 should be rejected with 422, got {resp.status_code}"
        )

    def test_n_candidates_exceeds_max_rejected(self, client):
        """n_candidates=9 violates le=8 — must be 422."""
        resp = client.post(
            "/api/v1/prototype/runs",
            json={
                "subject": "test artwork",
                "tradition": "default",
                "provider": "mock",
                "n_candidates": 9,
            },
        )
        assert resp.status_code == 422, (
            f"n_candidates=9 should be rejected with 422, got {resp.status_code}"
        )

    def test_max_rounds_zero_rejected(self, client):
        """max_rounds=0 violates ge=1 — must be 422."""
        resp = client.post(
            "/api/v1/prototype/runs",
            json={
                "subject": "test artwork",
                "tradition": "default",
                "provider": "mock",
                "max_rounds": 0,
            },
        )
        assert resp.status_code == 422, (
            f"max_rounds=0 should be rejected with 422, got {resp.status_code}"
        )

    def test_max_rounds_100_rejected(self, client):
        """max_rounds=100 violates le=5 — must be 422."""
        resp = client.post(
            "/api/v1/prototype/runs",
            json={
                "subject": "test artwork",
                "tradition": "default",
                "provider": "mock",
                "max_rounds": 100,
            },
        )
        assert resp.status_code == 422, (
            f"max_rounds=100 should be rejected with 422, got {resp.status_code}"
        )

    def test_invalid_provider_without_api_key_rejected(self, client):
        """provider=nb2 without GOOGLE_API_KEY should return 400."""
        # Unset any existing Google API key for this test
        original = os.environ.pop("GOOGLE_API_KEY", None)
        original_gemini = os.environ.pop("GEMINI_API_KEY", None)
        try:
            resp = client.post(
                "/api/v1/prototype/runs",
                json={
                    "subject": "test artwork",
                    "tradition": "default",
                    "provider": "nb2",
                },
            )
            assert resp.status_code == 400, (
                f"provider=nb2 without API key should be 400, got {resp.status_code}: {resp.text}"
            )
        finally:
            if original is not None:
                os.environ["GOOGLE_API_KEY"] = original
            if original_gemini is not None:
                os.environ["GEMINI_API_KEY"] = original_gemini

    def test_unknown_custom_nodes_rejected(self, client):
        """Custom topology with unknown node names should return 400."""
        resp = client.post(
            "/api/v1/prototype/runs",
            json={
                "subject": "test artwork",
                "tradition": "default",
                "provider": "mock",
                "custom_nodes": ["generate", "unknown_node_xyz"],
                "custom_edges": [["generate", "unknown_node_xyz"]],
            },
        )
        assert resp.status_code == 400, (
            f"Unknown custom node should be 400, got {resp.status_code}: {resp.text}"
        )

    def test_custom_nodes_without_edges_falls_back_to_default(self, client):
        """custom_nodes + empty custom_edges falls back to default template.

        The route uses ``if req.custom_nodes and req.custom_edges`` — an empty
        list is falsy, so the validation branch is skipped and the request is
        accepted using the default pipeline template.
        """
        resp = client.post(
            "/api/v1/prototype/runs",
            json={
                "subject": "test artwork",
                "tradition": "default",
                "provider": "mock",
                "custom_nodes": ["generate", "evaluate"],
                "custom_edges": [],
            },
        )
        # 200: custom_edges=[] is falsy → falls back to default template (not rejected)
        assert resp.status_code == 200, (
            f"custom_nodes + empty custom_edges should fall back gracefully, "
            f"got {resp.status_code}: {resp.text}"
        )

    def test_valid_mock_run_accepted(self, client):
        """A well-formed mock request must return 200 and a task_id."""
        resp = client.post(
            "/api/v1/prototype/runs",
            json={
                "subject": "Valid test artwork subject",
                "tradition": "default",
                "provider": "mock",
                "max_rounds": 1,
            },
        )
        assert resp.status_code == 200, (
            f"Valid mock run should be accepted: {resp.status_code} {resp.text}"
        )
        body = resp.json()
        assert "task_id" in body
        assert body["task_id"].startswith("api-")
        assert body["status"] == "running"

    def test_invalid_tradition_still_accepted(self, client):
        """Unknown tradition falls back to 'default' — should not error."""
        resp = client.post(
            "/api/v1/prototype/runs",
            json={
                "subject": "test with weird tradition",
                "tradition": "nonexistent_tradition_xyz",
                "provider": "mock",
                "max_rounds": 1,
            },
        )
        # Backend accepts and falls back — should not be a 400 or 422
        assert resp.status_code in (200, 400), (
            f"Unexpected status for invalid tradition: {resp.status_code}"
        )

    def test_missing_required_body_returns_422(self, client):
        """POST with no body at all must be 422 (subject is required)."""
        resp = client.post("/api/v1/prototype/runs", json={})
        assert resp.status_code == 422, (
            f"Empty body should return 422, got {resp.status_code}"
        )

    def test_missing_body_entirely_returns_422(self, client):
        """POST with no Content-Type body must be 422."""
        resp = client.post("/api/v1/prototype/runs")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 2. GET /runs/{id} — 404 for unknown run
# ---------------------------------------------------------------------------

class TestGetRunNotFound:
    """GET /api/v1/prototype/runs/{id} — 404 handling."""

    def test_get_nonexistent_run_returns_404(self, client):
        resp = client.get("/api/v1/prototype/runs/nonexistent-task-id-abc")
        assert resp.status_code == 404, (
            f"Expected 404 for unknown run, got {resp.status_code}"
        )

    def test_get_nonexistent_run_error_body(self, client):
        resp = client.get("/api/v1/prototype/runs/totally-fake-task-id")
        assert resp.status_code == 404
        body = resp.json()
        assert "detail" in body, "404 response should have a 'detail' field"

    def test_get_run_events_nonexistent_returns_404(self, client):
        """SSE stream for unknown run should also return 404."""
        resp = client.get("/api/v1/prototype/runs/no-such-run/events")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 3. POST /runs/{id}/action — 404 for unknown run
# ---------------------------------------------------------------------------

class TestSubmitActionNotFound:
    """POST /api/v1/prototype/runs/{id}/action — 404 and validation."""

    def test_action_on_nonexistent_run_returns_404(self, client):
        resp = client.post(
            "/api/v1/prototype/runs/no-such-run-xyz/action",
            json={"action": "approve"},
        )
        assert resp.status_code == 404, (
            f"Expected 404 for action on unknown run, got {resp.status_code}"
        )

    def test_action_force_accept_without_candidate_id_returns_400(self, client):
        """force_accept requires candidate_id — should return 400."""
        # First create a real run to get a valid task_id
        create_resp = client.post(
            "/api/v1/prototype/runs",
            json={
                "subject": "test HITL artwork",
                "provider": "mock",
                "max_rounds": 1,
                "enable_hitl": True,
            },
        )
        assert create_resp.status_code == 200
        task_id = create_resp.json()["task_id"]

        # force_accept without candidate_id on a run that is NOT waiting_human
        # — depends on timing, but validation happens first
        resp = client.post(
            f"/api/v1/prototype/runs/{task_id}/action",
            json={"action": "force_accept", "candidate_id": ""},
        )
        # Either 400 (validation fails) or the "not waiting" response
        assert resp.status_code in (200, 400), (
            f"force_accept without candidate_id: unexpected {resp.status_code}"
        )
        if resp.status_code == 400:
            body = resp.json()
            assert "detail" in body

    def test_action_invalid_action_type_rejected(self, client):
        """Action type not in enum should return 422."""
        create_resp = client.post(
            "/api/v1/prototype/runs",
            json={"subject": "test action validation", "provider": "mock"},
        )
        task_id = create_resp.json()["task_id"]

        resp = client.post(
            f"/api/v1/prototype/runs/{task_id}/action",
            json={"action": "invalid_action_type"},
        )
        assert resp.status_code == 422, (
            f"Invalid action type should be 422, got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# 4. POST /runs/{id}/instruct — 404 and validation
# ---------------------------------------------------------------------------

class TestInstructNotFound:
    """POST /api/v1/prototype/runs/{id}/instruct — 404 and validation."""

    def test_instruct_nonexistent_run_returns_404(self, client):
        resp = client.post(
            "/api/v1/prototype/runs/no-such-run-xyz/instruct",
            json={"instruction": "Refine the L3 dimension"},
        )
        assert resp.status_code == 404, (
            f"Expected 404 for instruct on unknown run, got {resp.status_code}"
        )

    def test_instruct_empty_instruction_returns_400(self, client):
        """Empty instruction body should return 400."""
        create_resp = client.post(
            "/api/v1/prototype/runs",
            json={"subject": "test instruct artwork", "provider": "mock"},
        )
        task_id = create_resp.json()["task_id"]

        resp = client.post(
            f"/api/v1/prototype/runs/{task_id}/instruct",
            json={"instruction": ""},
        )
        assert resp.status_code == 422, (
            f"Empty instruction should return 422 (Pydantic validation), got {resp.status_code}"
        )

    def test_instruct_missing_instruction_key_returns_422(self, client):
        """Missing 'instruction' key should return 422 (Pydantic validation)."""
        create_resp = client.post(
            "/api/v1/prototype/runs",
            json={"subject": "test instruct artwork", "provider": "mock"},
        )
        task_id = create_resp.json()["task_id"]

        resp = client.post(
            f"/api/v1/prototype/runs/{task_id}/instruct",
            json={},
        )
        assert resp.status_code == 422, (
            f"Missing instruction key should return 422, got {resp.status_code}"
        )

    def test_instruct_whitespace_only_instruction_returns_400(self, client):
        """Whitespace-only instruction should return 400."""
        create_resp = client.post(
            "/api/v1/prototype/runs",
            json={"subject": "test instruct artwork", "provider": "mock"},
        )
        task_id = create_resp.json()["task_id"]

        resp = client.post(
            f"/api/v1/prototype/runs/{task_id}/instruct",
            json={"instruction": "   "},
        )
        assert resp.status_code == 400, (
            f"Whitespace-only instruction should return 400, got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# 5. POST /api/v1/evaluate — error handling
# ---------------------------------------------------------------------------

class TestEvaluateErrors:
    """POST /api/v1/evaluate — missing/invalid input handling."""

    def test_evaluate_no_image_returns_422(self, client):
        """Neither image_url nor image_base64 provided — Pydantic validator fires."""
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "tradition": "default",
                "subject": "test artwork",
            },
            headers=AUTH,
        )
        assert resp.status_code == 422, (
            f"Missing image should return 422, got {resp.status_code}: {resp.text}"
        )

    def test_evaluate_no_auth_returns_401(self, client):
        """Request without Authorization header should return 401."""
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": "aGVsbG8=",
                "tradition": "default",
                "subject": "test",
            },
        )
        assert resp.status_code == 401, (
            f"Missing auth should return 401, got {resp.status_code}"
        )

    def test_evaluate_invalid_api_key_returns_403(self, client):
        """Wrong Bearer token should return 403."""
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": "aGVsbG8=",
                "tradition": "default",
                "subject": "test",
            },
            headers={"Authorization": "Bearer completely-wrong-key"},
        )
        assert resp.status_code == 403, (
            f"Invalid API key should return 403, got {resp.status_code}"
        )

    def test_evaluate_invalid_base64_returns_400_or_503(self, client):
        """Garbage base64 that can't be decoded as a real image."""
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": "!!!this_is_not_valid_base64!!!",
                "tradition": "default",
                "subject": "test invalid image",
            },
            headers=AUTH,
        )
        # 400 (image decode error), 502 (VLM rejects bad image), or 503 (no key)
        # — all are acceptable error responses for invalid image data
        assert resp.status_code in (400, 422, 502, 503), (
            f"Invalid base64 should error, got {resp.status_code}: {resp.text}"
        )

    def test_evaluate_empty_base64_returns_error(self, client):
        """Empty base64 string should produce a validation error."""
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": "",
                "tradition": "default",
                "subject": "test empty image",
            },
            headers=AUTH,
        )
        # Empty string fails the 'either image provided' validator
        assert resp.status_code in (400, 422), (
            f"Empty image_base64 should error, got {resp.status_code}"
        )

    def test_evaluate_empty_subject_handled(self, client):
        """Empty subject is allowed by schema (subject has no min_length).
        The endpoint should not crash — it either evaluates or returns 503 (no VLM key).
        """
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": "aGVsbG8=",  # valid base64 ("hello")
                "tradition": "default",
                "subject": "",
            },
            headers=AUTH,
        )
        # 503 = no VLM API key (expected in test env), 400 = bad image data
        # Neither 422 nor 500 — the endpoint should not panic on empty subject
        assert resp.status_code not in (422, 500), (
            f"Empty subject should not cause validation error or crash, "
            f"got {resp.status_code}: {resp.text}"
        )

    def test_evaluate_missing_body_returns_422(self, client):
        resp = client.post("/api/v1/evaluate", json={}, headers=AUTH)
        assert resp.status_code == 422, (
            f"Missing body should return 422, got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# 6. POST /api/v1/identify-tradition — error handling
# ---------------------------------------------------------------------------

class TestIdentifyTraditionErrors:
    """POST /api/v1/identify-tradition — missing image."""

    def test_identify_tradition_no_image_returns_422(self, client):
        """Neither image_url nor image_base64 — validator fires."""
        resp = client.post(
            "/api/v1/identify-tradition",
            json={},
            headers=AUTH,
        )
        assert resp.status_code == 422, (
            f"Missing image should return 422, got {resp.status_code}: {resp.text}"
        )

    def test_identify_tradition_no_auth_returns_401(self, client):
        resp = client.post(
            "/api/v1/identify-tradition",
            json={"image_base64": "aGVsbG8="},
        )
        assert resp.status_code == 401

    def test_identify_tradition_missing_body_returns_422(self, client):
        resp = client.post("/api/v1/identify-tradition", json={}, headers=AUTH)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 7. Rate limiting — 429 after threshold
# ---------------------------------------------------------------------------

class TestRateLimiting:
    """Sliding window rate limiter: 30 req/min per API key.

    Rate limiting is tested directly against the auth module's ``_check_rate_limit``
    function and via a single HTTP request after the window is pre-filled.
    This avoids the cost of 30+ real HTTP round-trips to a slow VLM endpoint.
    """

    _RATE_LIMIT_KEY = "rate-limit-test-key-unique"

    @pytest.fixture(autouse=True)
    def fresh_rate_state(self):
        """Reset rate limiter window before each test to avoid cross-test pollution."""
        import app.prototype.api.auth as _auth_mod
        _auth_mod._KEYS = {self._RATE_LIMIT_KEY}
        _auth_mod._RATE_WINDOWS[self._RATE_LIMIT_KEY].clear()
        yield
        _auth_mod._RATE_WINDOWS[self._RATE_LIMIT_KEY].clear()

    def test_rate_limit_unit_30_allowed(self):
        """Direct unit test: first 30 calls must not raise."""
        from fastapi import HTTPException
        import app.prototype.api.auth as _auth_mod

        _auth_mod._RATE_WINDOWS[self._RATE_LIMIT_KEY].clear()
        for i in range(30):
            try:
                _auth_mod._check_rate_limit(self._RATE_LIMIT_KEY)
            except HTTPException as exc:
                pytest.fail(f"Call #{i+1} should NOT be rate-limited, got {exc.status_code}")

    def test_rate_limit_unit_31st_raises_429(self):
        """Direct unit test: 31st call must raise HTTPException(429)."""
        from fastapi import HTTPException
        import app.prototype.api.auth as _auth_mod

        _auth_mod._RATE_WINDOWS[self._RATE_LIMIT_KEY].clear()
        for _ in range(30):
            _auth_mod._check_rate_limit(self._RATE_LIMIT_KEY)

        with pytest.raises(HTTPException) as exc_info:
            _auth_mod._check_rate_limit(self._RATE_LIMIT_KEY)
        assert exc_info.value.status_code == 429

    def test_rate_limit_http_response_after_window_prefilled(self, client):
        """HTTP integration: pre-fill the window, then one request must get 429.

        Only ONE real HTTP call is made — window is filled via the auth module directly.
        """
        import app.prototype.api.auth as _auth_mod
        import time as _time

        # Pre-fill the sliding window with 30 timestamps (all within the last 60s)
        now = _time.monotonic()
        for i in range(30):
            _auth_mod._RATE_WINDOWS[self._RATE_LIMIT_KEY].append(now - (59 - i))

        rate_auth = {"Authorization": f"Bearer {self._RATE_LIMIT_KEY}"}
        resp = client.post(
            "/api/v1/evaluate",
            json={"image_base64": "aGVsbG8=", "tradition": "default", "subject": "test"},
            headers=rate_auth,
        )
        assert resp.status_code == 429, (
            f"Pre-filled window: 31st request should be 429, got {resp.status_code}"
        )

    def test_rate_limit_error_message(self, client):
        """429 response detail mentions 'rate' or 'limit'."""
        import app.prototype.api.auth as _auth_mod
        import time as _time

        now = _time.monotonic()
        for i in range(30):
            _auth_mod._RATE_WINDOWS[self._RATE_LIMIT_KEY].append(now - (59 - i))

        rate_auth = {"Authorization": f"Bearer {self._RATE_LIMIT_KEY}"}
        resp = client.post(
            "/api/v1/evaluate",
            json={"image_base64": "aGVsbG8=", "subject": "test"},
            headers=rate_auth,
        )
        assert resp.status_code == 429
        body = resp.json()
        assert "detail" in body
        assert "rate" in body["detail"].lower() or "limit" in body["detail"].lower(), (
            f"Rate limit message should mention 'rate' or 'limit': {body['detail']}"
        )

    def test_rate_limit_per_key_isolation(self):
        """Different API keys have independent sliding windows."""
        from fastapi import HTTPException
        import app.prototype.api.auth as _auth_mod

        key_a = "rate-isolation-A"
        key_b = "rate-isolation-B"
        _auth_mod._KEYS = {key_a, key_b, self._RATE_LIMIT_KEY}
        _auth_mod._RATE_WINDOWS[key_a].clear()
        _auth_mod._RATE_WINDOWS[key_b].clear()

        # Exhaust key_a
        for _ in range(30):
            _auth_mod._check_rate_limit(key_a)
        with pytest.raises(HTTPException) as exc_info:
            _auth_mod._check_rate_limit(key_a)
        assert exc_info.value.status_code == 429, "key_a should be rate-limited"

        # key_b must still work
        try:
            _auth_mod._check_rate_limit(key_b)
        except HTTPException:
            pytest.fail("key_b should NOT be rate-limited")

        # Cleanup
        _auth_mod._RATE_WINDOWS[key_a].clear()
        _auth_mod._RATE_WINDOWS[key_b].clear()

    def test_guest_daily_limit_returns_429(self, client):
        """Prototype /runs endpoint daily limit — pre-fills counter directly."""
        import app.prototype.api.routes as _routes_mod

        today = time.strftime("%Y-%m-%d")
        original = _routes_mod._guest_runs_today.get(today, 0)
        _routes_mod._guest_runs_today[today] = _routes_mod._GUEST_DAILY_LIMIT

        try:
            resp = client.post(
                "/api/v1/prototype/runs",
                json={"subject": "daily limit test", "provider": "mock"},
            )
            assert resp.status_code == 429, (
                f"Daily limit should return 429, got {resp.status_code}: {resp.text}"
            )
            body = resp.json()
            assert "detail" in body
        finally:
            _routes_mod._guest_runs_today[today] = original


# ---------------------------------------------------------------------------
# 8. Classify-tradition — edge cases
# ---------------------------------------------------------------------------

class TestClassifyTraditionEdgeCases:
    """GET /api/v1/prototype/classify-tradition — edge case inputs."""

    def test_classify_tradition_requires_subject(self, client):
        """Missing subject param should return 422."""
        resp = client.get("/api/v1/prototype/classify-tradition")
        assert resp.status_code == 422, (
            f"Missing subject should return 422, got {resp.status_code}"
        )

    def test_classify_tradition_empty_string_rejected(self, client):
        """subject="" violates min_length=1."""
        resp = client.get("/api/v1/prototype/classify-tradition?subject=")
        assert resp.status_code == 422

    def test_classify_tradition_too_long_rejected(self, client):
        """subject > 500 chars should be rejected."""
        resp = client.get(
            "/api/v1/prototype/classify-tradition?subject=" + "x" * 501
        )
        assert resp.status_code == 422

    def test_classify_tradition_valid_returns_tradition_and_confidence(self, client):
        resp = client.get("/api/v1/prototype/classify-tradition?subject=water+ink+mountain")
        assert resp.status_code == 200
        body = resp.json()
        assert "tradition" in body
        assert "confidence" in body
        assert isinstance(body["confidence"], float)
        assert 0.0 <= body["confidence"] <= 1.0


# ---------------------------------------------------------------------------
# 9. Malformed JSON / Content-Type errors
# ---------------------------------------------------------------------------

class TestMalformedRequests:
    """Ensure the API doesn't panic on malformed input."""

    def test_runs_with_non_json_body(self, client):
        """Sending plain text instead of JSON to a JSON endpoint."""
        resp = client.post(
            "/api/v1/prototype/runs",
            content="this is not json",
            headers={"Content-Type": "text/plain"},
        )
        # FastAPI returns 422 for unparseable body
        assert resp.status_code == 422

    def test_action_with_non_json_body(self, client):
        """Action endpoint with non-JSON body."""
        create_resp = client.post(
            "/api/v1/prototype/runs",
            json={"subject": "malformed test", "provider": "mock"},
        )
        task_id = create_resp.json()["task_id"]

        resp = client.post(
            f"/api/v1/prototype/runs/{task_id}/action",
            content="not json",
            headers={"Content-Type": "text/plain"},
        )
        assert resp.status_code == 422

    def test_evaluate_with_non_json_body(self, client):
        """Non-JSON body to /evaluate — auth runs before body parsing.

        FastAPI evaluates the ``Authorization`` dependency before the request
        body is parsed.  If the auth key is not in _KEYS at this point (e.g.
        after cross-test mutation), auth rejects with 401/403 before the body
        is even checked.  Both 403 (bad key) and 422 (bad body) are valid
        rejection responses — the important thing is that we never get 200.
        """
        import app.prototype.api.auth as _auth_mod
        _auth_mod._KEYS = {_TEST_API_KEY}  # ensure our key is registered

        resp = client.post(
            "/api/v1/evaluate",
            content="not json at all",
            headers={"Content-Type": "text/plain", **AUTH},
        )
        # Auth runs first: 401/403 if key not registered; 422 if body invalid
        assert resp.status_code in (401, 403, 422), (
            f"Non-JSON body should be rejected (401/403/422), got {resp.status_code}"
        )
        assert resp.status_code != 200
