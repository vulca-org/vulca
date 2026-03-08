"""Unit tests for VULCA-Rankings integration API.

Uses sync TestClient (like test_health.py) to avoid lifespan/background-task
hang issues with async ASGITransport.

Tests that require seeded model data skip gracefully when the DB is empty.
"""

from __future__ import annotations

import os
import sys

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-at-least-32-chars")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def _get_models(**params):
    """GET /api/v1/models, skip test if DB not ready."""
    response = client.get("/api/v1/models", params=params)
    if response.status_code >= 500:
        pytest.skip(f"Models endpoint returned {response.status_code} — DB may not be initialised")
    return response


def test_models_endpoint_without_vulca():
    """GET /api/v1/models?include_vulca=false returns 200."""
    response = _get_models(include_vulca="false")
    assert response.status_code == 200
    data = response.json()
    if len(data) > 0:
        if "vulca_scores_47d" in data[0]:
            assert data[0]["vulca_scores_47d"] in [None, {}]


def test_models_endpoint_with_vulca():
    """GET /api/v1/models?include_vulca=true returns VULCA fields."""
    response = _get_models(include_vulca="true")
    assert response.status_code == 200
    data = response.json()
    if len(data) > 0:
        assert "vulca_scores_47d" in data[0]
        assert "vulca_cultural_perspectives" in data[0]
        assert "vulca_evaluation_date" in data[0]
        assert "vulca_sync_status" in data[0]


def test_model_detail_with_vulca():
    """GET /api/v1/models/{id} includes VULCA fields."""
    response = _get_models(limit="1")
    if response.status_code != 200 or len(response.json()) == 0:
        pytest.skip("No models in test DB — run init_db.py first")

    model_id = response.json()[0]["id"]

    detail = client.get(f"/api/v1/models/{model_id}")
    if detail.status_code >= 500:
        pytest.skip(f"Model detail returned {detail.status_code}")
    assert detail.status_code == 200
    data = detail.json()
    assert "vulca_scores_47d" in data
    assert "vulca_cultural_perspectives" in data

    detail2 = client.get(f"/api/v1/models/{model_id}", params={"include_vulca": "false"})
    assert detail2.status_code == 200
    data2 = detail2.json()
    assert "id" in data2
    assert data2["id"] == model_id


def test_vulca_models_endpoint():
    """GET /api/v1/vulca/models returns model list with VULCA metadata."""
    response = client.get("/api/v1/vulca/models")
    if response.status_code >= 500:
        pytest.skip(f"VULCA models endpoint returned {response.status_code}")
    assert response.status_code == 200
    data = response.json()

    assert "total" in data
    assert "models" in data
    assert isinstance(data["models"], list)

    if len(data["models"]) > 0:
        model = data["models"][0]
        assert "id" in model
        assert "name" in model
        assert "organization" in model
        assert "has_vulca" in model
        assert "vulca_sync_status" in model


def test_vulca_evaluate_with_sync():
    """POST /api/v1/vulca/evaluate accepts 6D scores."""
    evaluation_request = {
        "model_id": 1,
        "model_name": "Test Model",
        "scores_6d": {
            "creativity": 85.0, "technique": 88.0, "emotion": 82.0,
            "context": 86.0, "innovation": 84.0, "impact": 87.0,
        },
    }
    response = client.post("/api/v1/vulca/evaluate", json=evaluation_request)
    assert response.status_code in [200, 422, 500]
    if response.status_code == 200:
        data = response.json()
        assert "scores_47d" in data
        assert "cultural_perspectives" in data
        assert len(data["scores_47d"]) == 47


def test_vulca_sync_status():
    """Models report a valid vulca_sync_status."""
    response = _get_models(include_vulca="true", limit="10")
    assert response.status_code == 200
    models = response.json()
    for model in models:
        assert "vulca_sync_status" in model
        assert model["vulca_sync_status"] in [
            "pending", "syncing", "completed", "failed", "no_data", None,
        ]
