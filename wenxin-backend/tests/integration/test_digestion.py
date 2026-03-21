"""Integration tests for Digestion and Evolution endpoints.

Tests:
- GET /api/v1/prototype/evolution — evolution stats
- GET /api/v1/prototype/evolution/timeline — cumulative curve data
- GET /api/v1/digestion/status — digestion system status
- GET /api/v1/digestion/report — evolved context report
- POST /api/v1/digestion/run — trigger full digestion cycle
- Verify evolved weights format (L1-L5 structure)
- Verify tradition insights structure

All tests use mock/in-memory state — no real Gemini calls.
Do NOT use @pytest.mark.integration here.
"""

from __future__ import annotations

import os

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TEST_API_KEY = "digestion-test-key"


@pytest.fixture(scope="module")
def client():
    """TestClient for the full app."""
    os.environ["VULCA_API_KEYS"] = _TEST_API_KEY

    import app.prototype.api.auth as _auth
    _auth._KEYS = None

    from fastapi.testclient import TestClient
    from app.main import app as main_app

    with TestClient(main_app, raise_server_exceptions=False) as c:
        yield c


AUTH = {"Authorization": f"Bearer {_TEST_API_KEY}"}


# ---------------------------------------------------------------------------
# 1. Evolution stats endpoint
# ---------------------------------------------------------------------------

class TestEvolutionStats:
    """GET /api/v1/prototype/evolution."""

    def test_evolution_returns_200(self, client):
        resp = client.get("/api/v1/prototype/evolution")
        assert resp.status_code == 200, resp.text

    def test_evolution_schema_has_required_keys(self, client):
        resp = client.get("/api/v1/prototype/evolution")
        body = resp.json()

        required = {
            "total_sessions",
            "traditions_active",
            "evolutions_count",
            "emerged_concepts",
            "archetypes",
            "last_evolved_at",
            "agent_insights",
            "weight_changes",
        }
        missing = required - set(body.keys())
        assert not missing, f"Evolution response missing keys: {missing}"

    def test_evolution_total_sessions_is_non_negative_int(self, client):
        body = client.get("/api/v1/prototype/evolution").json()
        assert isinstance(body["total_sessions"], int)
        assert body["total_sessions"] >= 0

    def test_evolution_traditions_active_is_list(self, client):
        body = client.get("/api/v1/prototype/evolution").json()
        assert isinstance(body["traditions_active"], list)
        for t in body["traditions_active"]:
            assert isinstance(t, str), f"tradition entry must be str, got {type(t)}"

    def test_evolution_evolutions_count_is_non_negative(self, client):
        body = client.get("/api/v1/prototype/evolution").json()
        assert isinstance(body["evolutions_count"], int)
        assert body["evolutions_count"] >= 0

    def test_evolution_emerged_concepts_structure(self, client):
        body = client.get("/api/v1/prototype/evolution").json()
        concepts = body["emerged_concepts"]
        assert isinstance(concepts, list)
        for concept in concepts:
            assert "name" in concept, "Each concept must have 'name'"
            assert "description" in concept, "Each concept must have 'description'"
            assert isinstance(concept["name"], str)
            assert isinstance(concept["description"], str)

    def test_evolution_archetypes_is_list_of_strings(self, client):
        body = client.get("/api/v1/prototype/evolution").json()
        archetypes = body["archetypes"]
        assert isinstance(archetypes, list)
        for a in archetypes:
            assert isinstance(a, str), f"Archetype must be str, got {type(a)}"

    def test_evolution_agent_insights_is_dict(self, client):
        body = client.get("/api/v1/prototype/evolution").json()
        assert isinstance(body["agent_insights"], dict)

    def test_evolution_last_evolved_at_is_null_or_string(self, client):
        body = client.get("/api/v1/prototype/evolution").json()
        val = body["last_evolved_at"]
        assert val is None or isinstance(val, str), (
            f"last_evolved_at must be null or string, got {type(val)}"
        )


# ---------------------------------------------------------------------------
# 2. Evolution timeline endpoint
# ---------------------------------------------------------------------------

class TestEvolutionTimeline:
    """GET /api/v1/prototype/evolution/timeline."""

    def test_timeline_returns_200(self, client):
        resp = client.get("/api/v1/prototype/evolution/timeline")
        assert resp.status_code == 200, resp.text

    def test_timeline_schema(self, client):
        body = client.get("/api/v1/prototype/evolution/timeline").json()
        assert "points" in body, "Timeline must have 'points'"
        assert "total_evolutions" in body, "Timeline must have 'total_evolutions'"
        assert "total_cultures" in body, "Timeline must have 'total_cultures'"

    def test_timeline_points_is_list(self, client):
        body = client.get("/api/v1/prototype/evolution/timeline").json()
        assert isinstance(body["points"], list)

    def test_timeline_points_structure(self, client):
        body = client.get("/api/v1/prototype/evolution/timeline").json()
        for point in body["points"]:
            assert "date" in point, "Timeline point must have 'date'"
            assert "cultures" in point, "Timeline point must have 'cultures'"
            assert "evolutions" in point, "Timeline point must have 'evolutions'"
            assert isinstance(point["cultures"], int)
            assert isinstance(point["evolutions"], int)

    def test_timeline_cultures_monotonically_increases(self, client):
        points = client.get("/api/v1/prototype/evolution/timeline").json()["points"]
        if len(points) < 2:
            pytest.skip("Need at least 2 timeline points to verify monotonicity")
        cultures = [p["cultures"] for p in points]
        for i in range(1, len(cultures)):
            assert cultures[i] >= cultures[i - 1], (
                f"Cultures should not decrease: {cultures[i-1]} -> {cultures[i]}"
            )

    def test_timeline_total_evolutions_non_negative(self, client):
        body = client.get("/api/v1/prototype/evolution/timeline").json()
        assert body["total_evolutions"] >= 0

    def test_timeline_total_cultures_non_negative(self, client):
        body = client.get("/api/v1/prototype/evolution/timeline").json()
        assert body["total_cultures"] >= 0


# ---------------------------------------------------------------------------
# 3. Digestion status endpoint
# ---------------------------------------------------------------------------

class TestDigestionStatus:
    """GET /api/v1/digestion/status."""

    def test_digestion_status_returns_200(self, client):
        resp = client.get("/api/v1/digestion/status")
        assert resp.status_code == 200, resp.text

    def test_digestion_status_schema(self, client):
        body = client.get("/api/v1/digestion/status").json()
        required = {
            "total_sessions",
            "traditions",
            "cultures",
            "prompt_contexts",
            "feature_space",
            "agent_insights",
            "tradition_insights",
            "evolutions",
            "last_evolved_at",
        }
        missing = required - set(body.keys())
        assert not missing, f"Digestion status missing keys: {missing}"

    def test_digestion_total_sessions_non_negative(self, client):
        body = client.get("/api/v1/digestion/status").json()
        assert isinstance(body["total_sessions"], int)
        assert body["total_sessions"] >= 0

    def test_digestion_traditions_is_dict(self, client):
        body = client.get("/api/v1/digestion/status").json()
        assert isinstance(body["traditions"], dict)

    def test_digestion_evolutions_is_int(self, client):
        body = client.get("/api/v1/digestion/status").json()
        assert isinstance(body["evolutions"], int)
        assert body["evolutions"] >= 0

    def test_digestion_tradition_insights_is_dict(self, client):
        body = client.get("/api/v1/digestion/status").json()
        assert isinstance(body["tradition_insights"], dict)

    def test_digestion_agent_insights_is_dict(self, client):
        body = client.get("/api/v1/digestion/status").json()
        assert isinstance(body["agent_insights"], dict)


# ---------------------------------------------------------------------------
# 4. Digestion report endpoint
# ---------------------------------------------------------------------------

class TestDigestionReport:
    """GET /api/v1/digestion/report."""

    def test_digestion_report_returns_200(self, client):
        resp = client.get("/api/v1/digestion/report")
        assert resp.status_code == 200, resp.text

    def test_digestion_report_is_dict(self, client):
        body = client.get("/api/v1/digestion/report").json()
        assert isinstance(body, dict), f"Report must be a dict, got {type(body)}"

    def test_digestion_report_has_insights_if_evolved(self, client):
        """If evolutions > 0, the report should contain insight keys."""
        status = client.get("/api/v1/digestion/status").json()
        if status["evolutions"] == 0:
            pytest.skip("No evolutions yet — skipping report enrichment check")

        body = client.get("/api/v1/digestion/report").json()
        # Report should at minimum have been augmented with agent_insights
        assert "agent_insights" in body or "tradition_insights" in body, (
            "Evolved report should contain agent_insights or tradition_insights"
        )


# ---------------------------------------------------------------------------
# 5. Digestion run (trigger) endpoint
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDigestionRun:
    """POST /api/v1/digestion/run.

    Marked @pytest.mark.integration because ContextEvolver.evolve() may call
    LLM for insights generation (up to 60s timeout per call).  To avoid N×60s
    overhead, we cache the first POST response and reuse it for schema tests.
    Run with: pytest -m integration tests/integration/test_digestion.py
    """

    _cached_resp = None
    _cached_body = None

    @classmethod
    def _get_run_response(cls, client):
        """Cache the first digestion run to avoid repeated LLM calls."""
        if cls._cached_resp is None:
            cls._cached_resp = client.post("/api/v1/digestion/run")
            if cls._cached_resp.status_code == 200:
                cls._cached_body = cls._cached_resp.json()
            else:
                cls._cached_body = {}
        return cls._cached_resp, cls._cached_body

    def test_digestion_run_returns_200(self, client):
        resp, _ = self._get_run_response(client)
        assert resp.status_code == 200, resp.text

    def test_digestion_run_response_schema(self, client):
        _, body = self._get_run_response(client)
        required = {"evolution", "patterns", "preferences", "few_shot_examples_count"}
        missing = required - set(body.keys())
        assert not missing, f"Digestion run response missing keys: {missing}"

    def test_digestion_run_evolution_is_dict(self, client):
        _, body = self._get_run_response(client)
        assert isinstance(body["evolution"], dict), (
            f"'evolution' must be a dict, got {type(body['evolution'])}"
        )

    def test_digestion_run_patterns_is_list(self, client):
        _, body = self._get_run_response(client)
        assert isinstance(body["patterns"], list), (
            f"'patterns' must be a list, got {type(body['patterns'])}"
        )

    def test_digestion_run_preferences_is_dict(self, client):
        _, body = self._get_run_response(client)
        assert isinstance(body["preferences"], dict), (
            f"'preferences' must be a dict, got {type(body['preferences'])}"
        )

    def test_digestion_run_few_shot_count_is_non_negative(self, client):
        _, body = self._get_run_response(client)
        assert isinstance(body["few_shot_examples_count"], int)
        assert body["few_shot_examples_count"] >= 0

    def test_digestion_run_is_idempotent(self, client):
        """Running digestion twice should not crash — both calls succeed."""
        # First call is cached; second call is fresh
        resp1, _ = self._get_run_response(client)
        resp2 = client.post("/api/v1/digestion/run")
        assert resp1.status_code == 200
        assert resp2.status_code == 200


# ---------------------------------------------------------------------------
# 6. Evolved weights format verification
# ---------------------------------------------------------------------------

class TestEvolvedWeightsFormat:
    """Verify the format of evolved weights returned by the evolution system."""

    _L_LABELS = {"L1", "L2", "L3", "L4", "L5"}
    _DIM_KEYS = {
        "visual_perception",
        "technical_analysis",
        "cultural_context",
        "critical_interpretation",
        "philosophical_aesthetic",
    }

    def test_tradition_list_has_known_dimensions(self, client):
        """GET /api/v1/prototype/traditions — each tradition should list weights."""
        resp = client.get("/api/v1/prototype/traditions")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "traditions" in body

    def test_knowledge_base_weights_sum_to_one(self, client):
        """GET /api/v1/knowledge-base — weights per tradition must sum to ~1.0."""
        resp = client.get("/api/v1/knowledge-base")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        for entry in body.get("traditions", []):
            weights = entry.get("weights", {})
            if not weights:
                continue
            total = sum(weights.values())
            assert abs(total - 1.0) < 0.05, (
                f"Weights for {entry['tradition']} sum to {total:.4f}, expected ~1.0. "
                f"Weights: {weights}"
            )

    def test_knowledge_base_weights_keys_are_dimension_ids(self, client):
        """Weight dict keys should be known dimension IDs."""
        resp = client.get("/api/v1/knowledge-base")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        for entry in body.get("traditions", []):
            weights = entry.get("weights", {})
            for key in weights.keys():
                assert key in self._DIM_KEYS, (
                    f"Unknown weight key '{key}' in tradition {entry['tradition']}. "
                    f"Expected one of {self._DIM_KEYS}"
                )

    def test_knowledge_base_weights_all_non_negative(self, client):
        resp = client.get("/api/v1/knowledge-base")
        assert resp.status_code == 200
        body = resp.json()
        for entry in body.get("traditions", []):
            for dim, w in entry.get("weights", {}).items():
                assert w >= 0.0, (
                    f"Weight for {dim} in {entry['tradition']} is negative: {w}"
                )

    def test_digestion_status_traditions_weight_structure(self, client):
        """Digestion status traditions dict — each tradition's data is a dict."""
        body = client.get("/api/v1/digestion/status").json()
        for tradition_name, tradition_data in body["traditions"].items():
            assert isinstance(tradition_data, dict), (
                f"Tradition data for {tradition_name} must be a dict"
            )
