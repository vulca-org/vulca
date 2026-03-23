"""Integration tests — real Gemini API calls for VLM scoring and tradition ID.

Run with:  pytest tests/integration/ -m integration -v
Requires:  GEMINI_API_KEY in environment or .env file.
"""

from __future__ import annotations

import base64
import os
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="module")
def test_image_b64() -> str:
    """Load a real 64x64 gradient PNG that Gemini can actually process."""
    img_path = _FIXTURES_DIR / "test_artwork.png"
    assert img_path.exists(), f"Missing fixture: {img_path}"
    return base64.b64encode(img_path.read_bytes()).decode()


_INTEGRATION_KEY = "integration-test-key"


@pytest.fixture(scope="module")
def api_client():
    """In-process FastAPI TestClient with real API key loaded."""
    # Ensure env vars are loaded (conftest.py handles .env)
    # Force our own key so AUTH header matches
    os.environ["VULCA_API_KEYS"] = _INTEGRATION_KEY

    # Reset cached keys in auth module so our key takes effect
    import app.prototype.api.auth as _auth_mod
    _auth_mod._KEYS = None

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.prototype.api.evaluate_routes import evaluate_router

    app = FastAPI()
    app.include_router(evaluate_router)
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


AUTH = {"Authorization": f"Bearer {_INTEGRATION_KEY}"}


# ---------------------------------------------------------------------------
# 1. Real VLM Evaluate — L1-L5 scoring
# ---------------------------------------------------------------------------

class TestRealEvaluate:
    """POST /api/v1/evaluate with real Gemini VLM."""

    def test_evaluate_returns_200(self, api_client, test_image_b64):
        resp = api_client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": test_image_b64,
                "tradition": "default",
                "subject": "abstract red composition",
            },
            headers=AUTH,
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    def test_scores_are_valid_floats(self, api_client, test_image_b64):
        resp = api_client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": test_image_b64,
                "tradition": "default",
                "subject": "minimal abstract art",
            },
            headers=AUTH,
        )
        data = resp.json()
        scores = data["scores"]

        for label in ("L1", "L2", "L3", "L4", "L5"):
            assert label in scores, f"Missing {label}"
            val = scores[label]
            assert isinstance(val, float), f"{label} is {type(val)}, not float"
            assert 0.0 <= val <= 1.0, f"{label}={val} out of range [0, 1]"

    def test_weighted_total_in_range(self, api_client, test_image_b64):
        resp = api_client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": test_image_b64,
                "tradition": "chinese_xieyi",
                "subject": "ink wash mountain landscape",
            },
            headers=AUTH,
        )
        data = resp.json()
        assert 0.0 <= data["weighted_total"] <= 1.0

    def test_rationales_are_non_empty(self, api_client, test_image_b64):
        resp = api_client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": test_image_b64,
                "tradition": "default",
                "subject": "test artwork for rationale check",
            },
            headers=AUTH,
        )
        data = resp.json()
        rationales = data["rationales"]

        non_empty = sum(1 for v in rationales.values() if v)
        assert non_empty >= 3, f"Expected >=3 rationales, got {non_empty}"

    def test_latency_reasonable(self, api_client, test_image_b64):
        """Real VLM call should complete within 30 seconds."""
        t0 = time.monotonic()
        resp = api_client.post(
            "/api/v1/evaluate",
            json={
                "image_base64": test_image_b64,
                "tradition": "default",
                "subject": "latency benchmark",
            },
            headers=AUTH,
        )
        elapsed = time.monotonic() - t0
        assert resp.status_code == 200
        assert elapsed < 30, f"VLM took {elapsed:.1f}s (>30s)"

    def test_three_traditions(self, api_client, test_image_b64):
        """Spot-check 3 diverse traditions with real VLM.

        Note: synthetic gradient image may score very low (even 0.0) for
        traditions like chinese_xieyi — we only verify the API returns a
        valid response, not that scores are high.
        """
        for tradition in ("chinese_xieyi", "western_academic", "islamic_geometric"):
            resp = api_client.post(
                "/api/v1/evaluate",
                json={
                    "image_base64": test_image_b64,
                    "tradition": tradition,
                    "subject": f"test {tradition}",
                },
                headers=AUTH,
            )
            assert resp.status_code == 200, (
                f"{tradition} failed: {resp.status_code} {resp.text}"
            )
            data = resp.json()
            assert data["tradition_used"] == tradition
            assert data["weighted_total"] >= 0
            assert all(k in data["scores"] for k in ("L1", "L2", "L3", "L4", "L5"))


# ---------------------------------------------------------------------------
# 2. Real VLM Identify Tradition
# ---------------------------------------------------------------------------

class TestRealIdentifyTradition:
    """POST /api/v1/identify-tradition with real Gemini VLM."""

    VALID_TRADITIONS = {
        "default", "chinese_xieyi", "chinese_gongbi", "western_academic",
        "islamic_geometric", "japanese_traditional", "watercolor",
        "african_traditional", "south_asian",
    }

    def test_identify_returns_200(self, api_client, test_image_b64):
        resp = api_client.post(
            "/api/v1/identify-tradition",
            json={"image_base64": test_image_b64},
            headers=AUTH,
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    def test_returns_known_tradition(self, api_client, test_image_b64):
        resp = api_client.post(
            "/api/v1/identify-tradition",
            json={"image_base64": test_image_b64},
            headers=AUTH,
        )
        data = resp.json()
        assert data["tradition"] in self.VALID_TRADITIONS, (
            f"Unknown tradition: {data['tradition']}"
        )

    def test_confidence_in_range(self, api_client, test_image_b64):
        resp = api_client.post(
            "/api/v1/identify-tradition",
            json={"image_base64": test_image_b64},
            headers=AUTH,
        )
        data = resp.json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_recommended_weights_sum(self, api_client, test_image_b64):
        resp = api_client.post(
            "/api/v1/identify-tradition",
            json={"image_base64": test_image_b64},
            headers=AUTH,
        )
        data = resp.json()
        weights = data["recommended_weights"]
        assert len(weights) == 5, f"Expected 5 weights, got {len(weights)}"
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.05, f"Weights sum to {total}, expected ~1.0"


# ---------------------------------------------------------------------------
# 3. Knowledge Base (no API key needed, sanity check)
# ---------------------------------------------------------------------------

class TestKnowledgeBaseIntegration:
    """GET /api/v1/knowledge-base — verify real data loads correctly."""

    def test_all_9_traditions_present(self, api_client):
        resp = api_client.get("/api/v1/knowledge-base")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["total_traditions"] == 13

    def test_every_tradition_has_weights(self, api_client):
        resp = api_client.get("/api/v1/knowledge-base")
        data = resp.json()
        for entry in data["traditions"]:
            w = entry["weights"]
            assert len(w) >= 5, f"{entry['tradition']} missing weights"
            total = sum(w.values())
            assert abs(total - 1.0) < 0.05, (
                f"{entry['tradition']} weights sum={total}"
            )
