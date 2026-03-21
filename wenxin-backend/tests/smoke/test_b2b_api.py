"""Unit 2: B2B API smoke test.

Tests all 3 B2B API endpoints using FastAPI TestClient (in-process,
no real server needed). VLM/LLM calls are mocked to avoid Gemini costs.
"""

from __future__ import annotations

import base64
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Set API key env BEFORE importing modules that read it at load time
os.environ["VULCA_API_KEYS"] = "demo-key"
# Evaluate routes check GEMINI_API_KEY before calling score_image —
# set a dummy value so the env check passes and the @patch mock can intercept.
os.environ.setdefault("GEMINI_API_KEY", "test-fake-key-for-mock")

from app.prototype.api.evaluate_routes import evaluate_router

# Reset cached keys so our env var takes effect when running with other tests
import app.prototype.api.auth as _auth_mod
_auth_mod._KEYS = None

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Minimal 1x1 red PNG (67 bytes)
_1x1_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
    b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
    b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
_1x1_PNG_B64 = base64.b64encode(_1x1_PNG_BYTES).decode()

AUTH_HEADER = {"Authorization": "Bearer demo-key"}


@pytest.fixture(scope="module")
def client():
    """Create an in-process test client with the evaluate_router mounted."""
    # Force reload API keys from env to avoid stale cache from other test modules
    os.environ["VULCA_API_KEYS"] = "demo-key"
    _auth_mod._KEYS = None

    app = FastAPI()
    app.include_router(evaluate_router)
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ---------------------------------------------------------------------------
# Mocked VLM return values
# ---------------------------------------------------------------------------

def _mock_vlm_scores(*args, **kwargs):
    """Deterministic VLMCritic.score_image return value."""
    return {
        "L1": 0.85, "L2": 0.80, "L3": 0.75, "L4": 0.90, "L5": 0.70,
        "L1_rationale": "Good composition",
        "L2_rationale": "Solid technique",
        "L3_rationale": "Cultural elements present",
        "L4_rationale": "Respectful representation",
        "L5_rationale": "Moderate philosophical depth",
    }


def _make_mock_vlm():
    """Return a mock VLMCritic instance with .available=True and .score_image."""
    vlm = MagicMock()
    vlm.available = True
    vlm.score_image = MagicMock(side_effect=_mock_vlm_scores)
    return vlm


# ---------------------------------------------------------------------------
# GET /api/v1/knowledge-base
# ---------------------------------------------------------------------------

class TestKnowledgeBase:
    """GET /api/v1/knowledge-base — public, no auth required."""

    def test_returns_200(self, client: TestClient):
        resp = client.get("/api/v1/knowledge-base")
        assert resp.status_code == 200

    def test_has_9_traditions(self, client: TestClient):
        data = client.get("/api/v1/knowledge-base").json()
        assert len(data["traditions"]) == 9

    def test_each_tradition_has_required_fields(self, client: TestClient):
        data = client.get("/api/v1/knowledge-base").json()
        for entry in data["traditions"]:
            assert "tradition" in entry
            assert "weights" in entry
            assert "terms" in entry
            assert "taboo_rules" in entry
            assert "pipeline_variant" in entry

    def test_weights_sum_to_one(self, client: TestClient):
        data = client.get("/api/v1/knowledge-base").json()
        for entry in data["traditions"]:
            w = entry["weights"]
            total = sum(w.values())
            assert abs(total - 1.0) < 0.02, (
                f"Tradition {entry['tradition']} weights sum to {total}"
            )

    def test_summary_stats(self, client: TestClient):
        data = client.get("/api/v1/knowledge-base").json()
        summary = data["summary"]
        assert summary["total_traditions"] == 9
        assert summary["total_terms"] > 0
        assert summary["total_taboo_rules"] > 0

    def test_no_auth_required(self, client: TestClient):
        """Knowledge-base is public — no Authorization header needed."""
        resp = client.get("/api/v1/knowledge-base")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/v1/evaluate (mocked VLM)
# ---------------------------------------------------------------------------

class TestEvaluate:
    """POST /api/v1/evaluate — requires Bearer auth, mocked VLM."""

    @patch("vulca._vlm.score_image", new_callable=AsyncMock, side_effect=lambda *a, **kw: _mock_vlm_scores())
    def test_evaluate_with_base64(self, mock_vlm, client: TestClient):
        # vulca._vlm.score_image already mocked by decorator
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": _1x1_PNG_B64,
                "tradition": "default",
                "subject": "test artwork",
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "scores" in data
        assert "L1" in data["scores"]
        assert "L5" in data["scores"]
        assert "weighted_total" in data
        assert "tradition_used" in data
        assert "rationales" in data
        assert "latency_ms" in data
        assert data["weighted_total"] > 0

    @patch("vulca._vlm.score_image", new_callable=AsyncMock, side_effect=lambda *a, **kw: _mock_vlm_scores())
    def test_evaluate_response_schema(self, mock_vlm, client: TestClient):
        # vulca._vlm.score_image already mocked by decorator
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": _1x1_PNG_B64,
                "tradition": "chinese_xieyi",
                "subject": "ink wash landscape",
            },
            headers=AUTH_HEADER,
        )
        data = resp.json()
        assert resp.status_code == 200
        # All 5 L-scores present
        for label in ("L1", "L2", "L3", "L4", "L5"):
            assert label in data["scores"]
            assert isinstance(data["scores"][label], float)
        # Rationales present
        for label in ("L1", "L2", "L3", "L4", "L5"):
            assert label in data["rationales"]
        assert isinstance(data["latency_ms"], int)
        assert data["tradition_used"] == "chinese_xieyi"

    @patch("vulca._vlm.score_image", new_callable=AsyncMock, side_effect=lambda *a, **kw: _mock_vlm_scores())
    def test_evaluate_all_traditions(self, mock_vlm, client: TestClient):
        """Evaluate endpoint works for all 9 known traditions."""
        # vulca._vlm.score_image already mocked by decorator
        traditions = [
            "default", "chinese_xieyi", "chinese_gongbi", "western_academic",
            "islamic_geometric", "japanese_traditional", "watercolor",
            "african_traditional", "south_asian",
        ]
        for tradition in traditions:
            resp = client.post(
                "/api/v1/evaluate",
                json={
                    "image_base64": _1x1_PNG_B64,
                    "tradition": tradition,
                    "subject": f"test {tradition}",
                },
                headers=AUTH_HEADER,
            )
            assert resp.status_code == 200, (
                f"Tradition {tradition} failed: {resp.status_code} {resp.text}"
            )
            data = resp.json()
            assert data["tradition_used"] == tradition


# ---------------------------------------------------------------------------
# POST /api/v1/identify-tradition (mocked VLM)
# ---------------------------------------------------------------------------

class TestIdentifyTradition:
    """POST /api/v1/identify-tradition — requires Bearer auth, mocked VLM."""

    @patch(
        "app.prototype.api.evaluate_routes._call_vlm_tradition",
        new_callable=AsyncMock,
        return_value='{"tradition": "chinese_xieyi", "confidence": 0.85, "alternatives": [{"tradition": "japanese_traditional", "confidence": 0.10}]}',
    )
    @patch("vulca._vlm.score_image", new_callable=AsyncMock, side_effect=lambda *a, **kw: _mock_vlm_scores())
    def test_identify_tradition(self, mock_vlm, mock_call, client: TestClient):
        # vulca._vlm.score_image already mocked by decorator
        resp = client.post(
            "/api/v1/identify-tradition",
            json={"image_base64": _1x1_PNG_B64},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "tradition" in data
        assert "confidence" in data
        assert "recommended_weights" in data
        assert "latency_ms" in data

    @patch(
        "app.prototype.api.evaluate_routes._call_vlm_tradition",
        new_callable=AsyncMock,
        return_value='{"tradition": "chinese_xieyi", "confidence": 0.85, "alternatives": []}',
    )
    @patch("vulca._vlm.score_image", new_callable=AsyncMock, side_effect=lambda *a, **kw: _mock_vlm_scores())
    def test_identify_returns_valid_tradition(self, mock_vlm, mock_call, client: TestClient):
        # vulca._vlm.score_image already mocked by decorator
        resp = client.post(
            "/api/v1/identify-tradition",
            json={"image_base64": _1x1_PNG_B64},
            headers=AUTH_HEADER,
        )
        data = resp.json()
        valid_traditions = {
            "default", "chinese_xieyi", "chinese_gongbi", "western_academic",
            "islamic_geometric", "japanese_traditional", "watercolor",
            "african_traditional", "south_asian",
        }
        assert data["tradition"] in valid_traditions
        assert 0 <= data["confidence"] <= 1.0
        # Recommended weights should have 5 entries
        assert len(data["recommended_weights"]) == 5


# ---------------------------------------------------------------------------
# Auth & Validation errors
# ---------------------------------------------------------------------------

class TestAuthErrors:
    """Verify auth enforcement on protected endpoints."""

    def test_no_auth_header_returns_401(self, client: TestClient):
        resp = client.post(
            "/api/v1/evaluate",
            json={"image_base64": _1x1_PNG_B64, "subject": "test"},
        )
        assert resp.status_code == 401

    def test_bad_key_returns_403(self, client: TestClient):
        resp = client.post(
            "/api/v1/evaluate",
            json={"image_base64": _1x1_PNG_B64, "subject": "test"},
            headers={"Authorization": "Bearer wrong-key-12345"},
        )
        assert resp.status_code == 403

    def test_invalid_format_returns_401(self, client: TestClient):
        resp = client.post(
            "/api/v1/evaluate",
            json={"image_base64": _1x1_PNG_B64, "subject": "test"},
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert resp.status_code == 401

    def test_identify_no_auth_returns_401(self, client: TestClient):
        resp = client.post(
            "/api/v1/identify-tradition",
            json={"image_base64": _1x1_PNG_B64},
        )
        assert resp.status_code == 401


class TestInputValidation:
    """Verify input validation (422 errors)."""

    def test_missing_image_returns_422(self, client: TestClient):
        resp = client.post(
            "/api/v1/evaluate",
            json={"subject": "test"},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 422

    def test_identify_missing_image_returns_422(self, client: TestClient):
        resp = client.post(
            "/api/v1/identify-tradition",
            json={},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 422
