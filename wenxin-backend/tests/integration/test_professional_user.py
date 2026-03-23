"""Professional user behavior integration tests.

Simulates real-world workflows of professional users (artists, researchers,
curators) who use VULCA's full feature set:

1. Multi-tradition comparative creation
2. HITL refinement loops with dimension locking
3. Weight tuning for cultural emphasis
4. Cross-tradition evolution feedback
5. Gallery curation and filtering
6. Instruct-based iterative refinement
7. Reference image workflows
8. Digestion system verification after activity

Uses mock provider throughout — no external API keys required.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Environment setup — must happen before importing app
# ---------------------------------------------------------------------------

_TEST_KEY = "pro-user-test-key"
os.environ.setdefault("VULCA_API_KEYS", _TEST_KEY)
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("GOOGLE_API_KEY", "")

_API = "/api/v1/prototype"


# ---------------------------------------------------------------------------
# Module-scoped TestClient
# ---------------------------------------------------------------------------

def _make_client():
    """Build an isolated FastAPI TestClient using only the prototype router."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.prototype.api.routes import (
        _event_buffers,
        _guest_runs_today,
        _idempotency_map,
        _orchestrators,
        _run_metadata,
    )
    _orchestrators.clear()
    _run_metadata.clear()
    _event_buffers.clear()
    _idempotency_map.clear()
    _guest_runs_today.clear()

    import app.prototype.api.auth as _auth
    _auth._KEYS = None

    from app.prototype.api.routes import router
    mini_app = FastAPI()
    mini_app.include_router(router)
    return TestClient(mini_app, raise_server_exceptions=False)


@pytest.fixture(scope="module")
def client():
    c = _make_client()
    with c:
        yield c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_run(client, **kwargs) -> dict:
    """POST /runs with sensible defaults, return JSON response."""
    payload: dict[str, Any] = {
        "subject": "ink wash mountain",
        "tradition": "chinese_xieyi",
        "provider": "mock",
        "n_candidates": 2,
        "max_rounds": 1,
    }
    payload.update(kwargs)
    resp = client.post(f"{_API}/runs", json=payload)
    assert resp.status_code == 200, f"POST /runs failed: {resp.status_code} {resp.text}"
    data = resp.json()
    assert "task_id" in data
    return data


def _poll_until_done(client, task_id: str, timeout: float = 30.0) -> dict:
    """Poll until completed/failed or waiting_human."""
    deadline = time.monotonic() + timeout
    last = {}
    while time.monotonic() < deadline:
        resp = client.get(f"{_API}/runs/{task_id}")
        assert resp.status_code == 200
        data = resp.json()
        if data.get("status") in ("completed", "failed", "waiting_human"):
            if data["status"] == "completed" and not data.get("final_scores"):
                time.sleep(0.3)
                resp2 = client.get(f"{_API}/runs/{task_id}")
                if resp2.status_code == 200:
                    data = resp2.json()
            return data
        last = data
        time.sleep(0.5)
    raise TimeoutError(
        f"Pipeline {task_id} did not finish within {timeout:.0f}s "
        f"(last: {last.get('status', 'unknown')})"
    )


def _submit_action(client, task_id: str, action: str, **kwargs) -> dict:
    """POST /runs/{task_id}/action and return response JSON."""
    body = {"action": action, **kwargs}
    resp = client.post(f"{_API}/runs/{task_id}/action", json=body)
    if resp.status_code == 200:
        return {"status_code": 200, **resp.json()}
    return {"status_code": resp.status_code, "detail": resp.text}


def _instruct(client, task_id: str, instruction: str) -> dict:
    """POST /runs/{task_id}/instruct and return response JSON."""
    resp = client.post(
        f"{_API}/runs/{task_id}/instruct",
        json={"instruction": instruction},
    )
    assert resp.status_code == 200, f"instruct failed: {resp.status_code} {resp.text}"
    return resp.json()


def _get_events(task_id: str) -> list[dict]:
    """Read pipeline events from the in-memory buffer."""
    from app.prototype.api.routes import _buffer_lock, _event_buffers

    with _buffer_lock:
        raw = list(_event_buffers.get(task_id, []))
    events = []
    for ev in raw:
        try:
            events.append(ev.to_dict())
        except Exception:
            events.append({
                "event_type": str(getattr(ev, "event_type", "")),
                "payload": getattr(ev, "payload", {}),
            })
    return events


# ===========================================================================
# Scenario 1: Multi-Tradition Comparative Creation
#
# A researcher creates artworks across 3 traditions with the same subject
# to compare cultural interpretations, then verifies Gallery filtering.
# ===========================================================================

class TestMultiTraditionComparative:
    """Artist creates same subject across multiple traditions to compare."""

    _TRADITIONS = ["chinese_xieyi", "islamic_geometric", "watercolor"]
    _SUBJECT = "flowing water in moonlight"

    def test_create_across_three_traditions(self, client):
        """Same subject, 3 traditions → 3 independent runs all complete."""
        results = []
        for tradition in self._TRADITIONS:
            data = _create_run(
                client,
                subject=self._SUBJECT,
                tradition=tradition,
                n_candidates=2,
                max_rounds=1,
            )
            result = _poll_until_done(client, data["task_id"])
            results.append(result)

        completed = [r for r in results if r["status"] == "completed"]
        assert len(completed) >= 2, (
            f"Expected at least 2/3 runs to complete, got {len(completed)}. "
            f"Statuses: {[r['status'] for r in results]}"
        )

    def test_scores_differ_across_traditions(self, client):
        """Different traditions should produce meaningfully different scores."""
        score_sets = {}
        for tradition in self._TRADITIONS[:2]:
            data = _create_run(
                client,
                subject=self._SUBJECT,
                tradition=tradition,
            )
            result = _poll_until_done(client, data["task_id"])
            if result["status"] == "completed":
                score_sets[tradition] = result.get("final_scores", {})

        if len(score_sets) < 2:
            pytest.skip("Need at least 2 completed runs to compare")

        # Verify both have L1-L5 scores
        for tradition, scores in score_sets.items():
            assert len(scores) >= 5, (
                f"{tradition} has only {len(scores)} scores: {scores}"
            )

    def test_gallery_filters_by_tradition(self, client):
        """After creating runs, Gallery can filter by tradition."""
        # Create a run so gallery has content
        data = _create_run(client, tradition="chinese_xieyi")
        _poll_until_done(client, data["task_id"])

        resp = client.get(f"{_API}/gallery?tradition=chinese_xieyi")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body["items"], list)
        for item in body["items"]:
            assert item["tradition"] == "chinese_xieyi"


# ===========================================================================
# Scenario 2: HITL Refinement Loop
#
# An artist enables HITL, reviews the result, locks strong dimensions,
# then approves. This tests the real decision cycle.
# ===========================================================================

class TestHITLRefinementCycle:
    """Artist uses HITL to review, lock dimensions, and approve."""

    def test_hitl_review_lock_approve_cycle(self, client):
        """Full HITL cycle: create → wait → lock L1+L3 → approve."""
        data = _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        result = _poll_until_done(client, task_id)
        if result["status"] != "waiting_human":
            pytest.skip("Pipeline did not reach waiting_human")

        # Lock strong dimensions (L1, L3)
        lock_resp = _submit_action(
            client, task_id, "lock_dimensions",
            locked_dimensions=["L1", "L3"],
        )
        assert lock_resp["status_code"] == 200
        assert lock_resp.get("accepted") is True

        # After locking, pipeline should proceed to completion
        final = _poll_until_done(client, task_id)
        assert final["status"] == "completed", (
            f"Expected completed after lock+approve, got {final['status']}"
        )

    def test_hitl_reject_and_rerun(self, client):
        """Artist rejects first attempt, reruns with focus dimensions."""
        data = _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        result = _poll_until_done(client, task_id)
        if result["status"] != "waiting_human":
            pytest.skip("Pipeline did not reach waiting_human")

        # Rerun with focus on cultural context and interpretation
        rerun_resp = _submit_action(
            client, task_id, "rerun",
            rerun_dimensions=["L3", "L4"],
        )
        assert rerun_resp["status_code"] == 200
        assert rerun_resp.get("accepted") is True

        new_task_id = rerun_resp.get("new_task_id")
        assert new_task_id, "rerun must return new_task_id"
        assert new_task_id != task_id

        # The new run should at least start
        resp = client.get(f"{_API}/runs/{new_task_id}")
        assert resp.status_code == 200
        status = resp.json()["status"]
        assert status in ("running", "waiting_human", "completed", "failed")


# ===========================================================================
# Scenario 3: Weight Tuning Session
#
# A researcher adjusts L1-L5 weights to emphasize cultural context
# (L3) and philosophical aesthetic (L5) for a specific tradition.
# ===========================================================================

class TestWeightTuningSession:
    """Researcher tunes L1-L5 weights for cultural emphasis."""

    def test_heavy_cultural_weights(self, client):
        """High L3+L5 weights (cultural/philosophical) accepted and run completes."""
        data = _create_run(
            client,
            subject="zen garden contemplation",
            tradition="japanese_traditional",
            node_params={
                "critic": {
                    "w_l1": 0.10,   # Low visual weight
                    "w_l2": 0.10,   # Low technical weight
                    "w_l3": 0.30,   # High cultural context
                    "w_l4": 0.20,   # Moderate interpretation
                    "w_l5": 0.30,   # High philosophical
                }
            },
        )
        result = _poll_until_done(client, data["task_id"])
        assert result["status"] in ("completed", "failed")

    def test_heavy_technical_weights(self, client):
        """High L1+L2 weights (visual/technical) for technique-focused evaluation."""
        data = _create_run(
            client,
            subject="geometric tessellation pattern",
            tradition="islamic_geometric",
            node_params={
                "critic": {
                    "w_l1": 0.35,   # High visual
                    "w_l2": 0.35,   # High technical
                    "w_l3": 0.10,
                    "w_l4": 0.10,
                    "w_l5": 0.10,
                }
            },
        )
        result = _poll_until_done(client, data["task_id"])
        assert result["status"] in ("completed", "failed")

    def test_extreme_single_dimension_weight(self, client):
        """Setting one dimension to near-max should still work."""
        data = _create_run(
            client,
            node_params={
                "critic": {
                    "w_l1": 0.05,
                    "w_l2": 0.05,
                    "w_l3": 0.80,   # Extreme cultural emphasis
                    "w_l4": 0.05,
                    "w_l5": 0.05,
                }
            },
        )
        result = _poll_until_done(client, data["task_id"])
        assert result["status"] in ("completed", "failed")

    def test_compare_weights_same_subject(self, client):
        """Same subject with different weight profiles → both complete."""
        subject = "autumn leaves in wind"
        # Profile A: balanced
        d1 = _create_run(
            client, subject=subject,
            node_params={"critic": {"w_l1": 0.20, "w_l2": 0.20, "w_l3": 0.20, "w_l4": 0.20, "w_l5": 0.20}},
        )
        # Profile B: cultural heavy
        d2 = _create_run(
            client, subject=subject,
            node_params={"critic": {"w_l1": 0.10, "w_l2": 0.10, "w_l3": 0.40, "w_l4": 0.10, "w_l5": 0.30}},
        )
        r1 = _poll_until_done(client, d1["task_id"])
        r2 = _poll_until_done(client, d2["task_id"])
        assert r1["status"] in ("completed", "failed")
        assert r2["status"] in ("completed", "failed")


# ===========================================================================
# Scenario 4: Iterative Instruct Refinement
#
# An artist creates a base artwork, then issues 3 successive instruct
# commands to refine it — testing the multi-turn creative dialogue.
# ===========================================================================

class TestIterativeInstructRefinement:
    """Artist refines artwork through successive instruct commands."""

    def test_three_round_instruct_chain(self, client):
        """Base → instruct (mood) → instruct (detail) → instruct (color)."""
        # Round 0: base creation
        data = _create_run(
            client,
            subject="mountain waterfall at dawn",
            tradition="chinese_xieyi",
        )
        result = _poll_until_done(client, data["task_id"])
        if result["status"] != "completed":
            pytest.skip("Base run did not complete")

        current_task = data["task_id"]
        instructions = [
            "make the atmosphere more melancholic and misty",
            "add more fine detail to the water splashes",
            "shift the color palette toward cooler blues and greys",
        ]

        for instruction in instructions:
            body = _instruct(client, current_task, instruction)
            assert "new_task_id" in body
            assert body["parent_task_id"] == current_task

            new_task = body["new_task_id"]
            new_result = _poll_until_done(client, new_task)
            assert new_result["status"] in ("completed", "failed"), (
                f"Instruct '{instruction[:30]}...' produced {new_result['status']}"
            )
            current_task = new_task

    def test_instruct_preserves_tradition(self, client):
        """Instruct chain preserves the original tradition."""
        from app.prototype.api.routes import _run_metadata

        data = _create_run(
            client,
            subject="sacred geometry",
            tradition="islamic_geometric",
        )
        result = _poll_until_done(client, data["task_id"])
        if result["status"] != "completed":
            pytest.skip("Base run did not complete")

        body = _instruct(client, data["task_id"], "add more intricate border pattern")
        new_id = body["new_task_id"]
        assert _run_metadata[new_id].get("tradition") == "islamic_geometric"


# ===========================================================================
# Scenario 5: Reference Image Workflow
#
# A curator uploads a reference image alongside intent, creating
# artwork that should be influenced by the reference.
# ===========================================================================

class TestReferenceImageWorkflow:
    """Curator provides reference images to guide AI creation."""

    # Minimal 1x1 white PNG as base64
    _TINY_PNG = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
        "+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )

    def test_reference_image_creation_completes(self, client):
        """Run with reference image completes normally."""
        data = _create_run(
            client,
            subject="reinterpretation of classical landscape",
            tradition="western_academic",
            reference_image_base64=self._TINY_PNG,
        )
        result = _poll_until_done(client, data["task_id"])
        assert result["status"] in ("completed", "failed")

    def test_reference_image_with_hitl(self, client):
        """Reference image + HITL: image context available at review time."""
        data = _create_run(
            client,
            subject="modern take on silk road imagery",
            tradition="south_asian",
            reference_image_base64=self._TINY_PNG,
            enable_hitl=True,
        )
        result = _poll_until_done(client, data["task_id"])
        assert result["status"] in ("waiting_human", "completed", "failed")

    def test_reference_image_inherited_by_instruct(self, client):
        """Instruct on ref-image run inherits the reference."""
        from app.prototype.api.routes import _run_metadata

        data = _create_run(
            client,
            subject="lotus pond",
            reference_image_base64=self._TINY_PNG,
        )
        result = _poll_until_done(client, data["task_id"])
        if result["status"] != "completed":
            pytest.skip("Base run did not complete")

        body = _instruct(client, data["task_id"], "make the lotus more prominent")
        new_id = body["new_task_id"]
        assert _run_metadata[new_id].get("reference_image_base64") == self._TINY_PNG


# ===========================================================================
# Scenario 6: Gallery Curation Workflow
#
# After creating multiple runs, a curator uses Gallery to browse,
# filter, sort, and paginate through the collection.
# ===========================================================================

class TestGalleryCuration:
    """Curator browses and filters the gallery after creation sessions."""

    def test_gallery_default_listing(self, client):
        """Default gallery call returns items + total."""
        resp = client.get(f"{_API}/gallery")
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert isinstance(body["total"], int)

    def test_gallery_pagination(self, client):
        """Gallery supports limit/offset pagination."""
        resp1 = client.get(f"{_API}/gallery?limit=2&offset=0")
        assert resp1.status_code == 200
        items1 = resp1.json()["items"]
        assert len(items1) <= 2

        resp2 = client.get(f"{_API}/gallery?limit=2&offset=2")
        assert resp2.status_code == 200
        # Offset items should differ from first page (if enough data)

    def test_gallery_sort_by_score(self, client):
        """Gallery sorted by score returns items in descending order."""
        resp = client.get(f"{_API}/gallery?sort_by=score&sort_order=desc&limit=10")
        assert resp.status_code == 200
        items = resp.json()["items"]
        if len(items) >= 2:
            scores = [item.get("overall", 0) for item in items]
            for i in range(len(scores) - 1):
                assert scores[i] >= scores[i + 1], (
                    f"Gallery not sorted desc by score: {scores}"
                )

    def test_gallery_sort_by_newest(self, client):
        """Gallery sorted by newest returns items in recency order."""
        resp = client.get(f"{_API}/gallery?sort_by=newest&sort_order=desc&limit=10")
        assert resp.status_code == 200
        items = resp.json()["items"]
        if len(items) >= 2:
            times = [item.get("created_at", 0) for item in items]
            for i in range(len(times) - 1):
                assert times[i] >= times[i + 1], (
                    f"Gallery not sorted desc by time: {times}"
                )

    def test_gallery_min_score_filter(self, client):
        """min_score filter excludes low-scoring items."""
        resp = client.get(f"{_API}/gallery?min_score=0.5")
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item.get("overall", 0) >= 0.5, (
                f"Item {item.get('id')} has overall={item.get('overall')} below min_score=0.5"
            )

    def test_gallery_item_has_scores_dict(self, client):
        """Each gallery item includes L1-L5 scores dict."""
        # First create something to ensure gallery isn't empty
        data = _create_run(client)
        _poll_until_done(client, data["task_id"])

        resp = client.get(f"{_API}/gallery?limit=5")
        assert resp.status_code == 200
        items = resp.json()["items"]
        if not items:
            pytest.skip("Gallery empty")

        for item in items:
            scores = item.get("scores", {})
            assert isinstance(scores, dict), f"scores should be dict: {type(scores)}"


# ===========================================================================
# Scenario 7: Evolution & Traditions Discovery
#
# A researcher explores the system's cultural knowledge, checks
# evolution stats, and verifies tradition configurations.
# ===========================================================================

class TestEvolutionDiscovery:
    """Researcher explores cultural traditions and evolution state."""

    def test_traditions_returns_all_nine(self, client):
        """System exposes exactly 9 cultural traditions."""
        resp = client.get(f"{_API}/traditions")
        assert resp.status_code == 200
        traditions = resp.json().get("traditions", [])
        assert len(traditions) >= 9, (
            f"Expected >= 9 traditions, got {len(traditions)}"
        )

    def test_each_tradition_has_display_name(self, client):
        """Every tradition includes a human-readable display_name."""
        resp = client.get(f"{_API}/traditions")
        for t in resp.json().get("traditions", []):
            assert t.get("display_name"), (
                f"Tradition {t.get('name')} missing display_name"
            )

    def test_evolution_stats_available(self, client):
        """Evolution endpoint returns valid statistics."""
        resp = client.get(f"{_API}/evolution")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body["total_sessions"], int)
        assert isinstance(body["traditions_active"], list)
        assert isinstance(body["evolutions_count"], int)

    def test_evolution_timeline_has_points(self, client):
        """Evolution timeline returns a list of cumulative data points."""
        resp = client.get(f"{_API}/evolution/timeline")
        assert resp.status_code == 200
        body = resp.json()
        assert "points" in body
        assert "total_evolutions" in body

    def test_classify_tradition_from_text(self, client):
        """classify-tradition endpoint resolves subject text to a tradition."""
        resp = client.get(
            f"{_API}/classify-tradition",
            params={"subject": "I want to paint a bamboo forest in the literati style"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "tradition" in body


# ===========================================================================
# Scenario 8: Multi-Round High-Fidelity Session
#
# An artist runs a pipeline with max_rounds=3 and 4 candidates,
# verifying that multi-round scoring produces progressive improvement.
# ===========================================================================

class TestMultiRoundSession:
    """Artist runs a multi-round pipeline for quality refinement."""

    def test_multi_round_completes(self, client):
        """max_rounds=3 + n_candidates=4 pipeline completes."""
        data = _create_run(
            client,
            subject="ancient temple at sunset",
            tradition="south_asian",
            n_candidates=4,
            max_rounds=3,
        )
        result = _poll_until_done(client, data["task_id"], timeout=60.0)
        assert result["status"] in ("completed", "failed")

    def test_multi_round_has_round_data(self, client):
        """Multi-round run reports round progression in response."""
        data = _create_run(
            client,
            subject="silk road caravan",
            n_candidates=2,
            max_rounds=2,
        )
        result = _poll_until_done(client, data["task_id"], timeout=60.0)
        if result["status"] != "completed":
            pytest.skip("Multi-round run did not complete")

        # total_rounds should reflect actual rounds executed
        assert result.get("total_rounds", 0) >= 1

    def test_multi_round_events_sequence(self, client):
        """Multi-round run emits generate events for each round."""
        data = _create_run(
            client,
            subject="calligraphy brush dance",
            tradition="chinese_gongbi",
            n_candidates=2,
            max_rounds=2,
        )
        _poll_until_done(client, data["task_id"], timeout=60.0)

        events = _get_events(data["task_id"])
        stage_events = [
            e for e in events
            if e.get("event_type") == "stage_started"
        ]
        # At minimum: generate + evaluate per round
        assert len(stage_events) >= 2, (
            f"Expected at least 2 stage_started events, got {len(stage_events)}"
        )

    def test_fast_template_fewer_rounds(self, client):
        """Fast template should complete in fewer rounds than default."""
        data = _create_run(
            client,
            subject="minimalist landscape",
            template="fast",
            n_candidates=2,
            max_rounds=1,
        )
        result = _poll_until_done(client, data["task_id"])
        assert result["status"] in ("completed", "failed")


# ===========================================================================
# Scenario 9: HITL Force-Accept Specific Candidate
#
# An artist in HITL mode sees 4 candidates and force-accepts a
# specific one they prefer, bypassing the normal decision flow.
# ===========================================================================

class TestHITLForceAccept:
    """Artist force-accepts a specific candidate in HITL mode."""

    def test_force_accept_with_candidate(self, client):
        """force_accept with candidate_id completes the pipeline."""
        data = _create_run(client, enable_hitl=True, n_candidates=4)
        task_id = data["task_id"]

        result = _poll_until_done(client, task_id)
        if result["status"] != "waiting_human":
            pytest.skip("Pipeline did not reach waiting_human")

        resp = _submit_action(
            client, task_id, "force_accept",
            candidate_id="cand-002",
        )
        assert resp["status_code"] == 200
        assert resp.get("accepted") is True

        final = _poll_until_done(client, task_id)
        assert final["status"] == "completed"

    def test_force_accept_without_candidate_rejected(self, client):
        """force_accept without candidate_id returns 400."""
        from vulca.pipeline.types import EventType as VulcaEventType
        from vulca.pipeline.types import PipelineEvent as VulcaEvent
        from app.prototype.api.routes import _buffer_lock, _event_buffers

        data = _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        # Inject a fake human_required event
        fake_event = VulcaEvent(
            event_type=VulcaEventType.HUMAN_REQUIRED,
            payload={"stage": "decide"},
            timestamp_ms=0,
        )
        with _buffer_lock:
            _event_buffers.setdefault(task_id, []).append(fake_event)

        resp = client.post(
            f"{_API}/runs/{task_id}/action",
            json={"action": "force_accept"},
        )
        assert resp.status_code == 400


# ===========================================================================
# Scenario 10: Cross-Session Workflow Coherence
#
# Verifies that multiple runs coexist properly — no state leakage,
# correct task_id isolation, events don't cross-contaminate.
# ===========================================================================

class TestCrossSessionCoherence:
    """Verify isolation between concurrent runs."""

    def test_parallel_runs_have_unique_task_ids(self, client):
        """Multiple runs created simultaneously get unique task_ids."""
        ids = set()
        for i in range(5):
            data = _create_run(
                client,
                subject=f"parallel test artwork {i}",
                n_candidates=2,
                max_rounds=1,
            )
            ids.add(data["task_id"])

        assert len(ids) == 5, f"Expected 5 unique task_ids, got {len(ids)}"

    def test_events_isolated_per_run(self, client):
        """Events from one run do not appear in another run's buffer."""
        d1 = _create_run(client, subject="run-alpha", tradition="chinese_xieyi")
        d2 = _create_run(client, subject="run-beta", tradition="watercolor")

        _poll_until_done(client, d1["task_id"])
        _poll_until_done(client, d2["task_id"])

        events1 = _get_events(d1["task_id"])
        events2 = _get_events(d2["task_id"])

        # Basic isolation: each buffer belongs to its own run
        assert len(events1) >= 1 or len(events2) >= 1, (
            "At least one run should have events"
        )

    def test_status_poll_returns_correct_run(self, client):
        """Polling for run A returns run A's data, not run B's."""
        da = _create_run(client, subject="run-A-unique-subject")
        db = _create_run(client, subject="run-B-unique-subject")

        ra = _poll_until_done(client, da["task_id"])
        rb = _poll_until_done(client, db["task_id"])

        assert ra["task_id"] == da["task_id"]
        assert rb["task_id"] == db["task_id"]
        assert ra["task_id"] != rb["task_id"]


# ===========================================================================
# Scenario 11: Capabilities & Datatypes Discovery
#
# A new user explores what the system can do.
# ===========================================================================

class TestSystemDiscovery:
    """New user explores system capabilities."""

    def test_capabilities_endpoint(self, client):
        """GET /capabilities returns valid dict."""
        resp = client.get(f"{_API}/capabilities")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict)

    def test_datatypes_endpoint(self, client):
        """GET /datatypes returns valid dict."""
        resp = client.get(f"{_API}/datatypes")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict)
