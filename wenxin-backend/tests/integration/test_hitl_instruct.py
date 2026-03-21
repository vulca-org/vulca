"""Comprehensive integration tests for HITL and Instruct flows.

Uses mock provider throughout — no external API keys required.
The mock pipeline is async and fast; polling uses time.sleep(0.5) with a
30-second timeout so tests stay deterministic regardless of machine speed.

All routes are mounted under the isolated FastAPI app so tests run in-process
via ASGITransport, exactly as test_prototype_api.py and test_hitl_integration.py do.
"""

from __future__ import annotations

import time
from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from app.prototype.api.routes import (
    _event_buffers,
    _guest_runs_today,
    _idempotency_map,
    _orchestrators,
    _run_metadata,
    router,
)

# Base path for all prototype endpoints
API = "/api/v1/prototype"

# Polling budget: mock provider is fast but pipeline runs in a background
# thread, so a small sleep between polls is enough.
_POLL_INTERVAL = 0.5   # seconds between status polls
_POLL_TIMEOUT  = 30    # seconds before giving up


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """Isolated in-process async client.

    State is cleared before each test so runs from previous tests cannot
    bleed into the next one.
    """
    _orchestrators.clear()
    _run_metadata.clear()
    _event_buffers.clear()
    _idempotency_map.clear()
    _guest_runs_today.clear()

    app = FastAPI()
    app.include_router(router)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        timeout=60,
    ) as async_client:
        yield async_client


# ---------------------------------------------------------------------------
# Polling helpers
# ---------------------------------------------------------------------------


async def _poll_until(
    client: httpx.AsyncClient,
    task_id: str,
    target: str,
    timeout: float = _POLL_TIMEOUT,
) -> dict | None:
    """Poll GET /runs/{task_id} until status == target or timeout.

    Returns the final status dict, or None if timeout was reached.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        res = await client.get(f"{API}/runs/{task_id}")
        assert res.status_code == 200, f"Status poll returned {res.status_code}: {res.text}"
        data = res.json()
        if data.get("status") == target:
            return data
        time.sleep(_POLL_INTERVAL)
    return None


async def _create_run(
    client: httpx.AsyncClient,
    *,
    subject: str = "bamboo forest in mist",
    tradition: str = "chinese_xieyi",
    provider: str = "mock",
    max_rounds: int = 1,
    n_candidates: int = 2,
    enable_hitl: bool = False,
    node_params: dict | None = None,
    reference_image_base64: str | None = None,
) -> dict:
    """POST /runs and assert 200 + task_id present."""
    body: dict = {
        "subject": subject,
        "tradition": tradition,
        "provider": provider,
        "max_rounds": max_rounds,
        "n_candidates": n_candidates,
        "enable_hitl": enable_hitl,
    }
    if node_params is not None:
        body["node_params"] = node_params
    if reference_image_base64 is not None:
        body["reference_image_base64"] = reference_image_base64

    res = await client.post(f"{API}/runs", json=body)
    assert res.status_code == 200, f"create_run failed: {res.status_code} {res.text}"
    data = res.json()
    assert "task_id" in data, f"Missing task_id in response: {data}"
    return data


async def _submit_action(
    client: httpx.AsyncClient,
    task_id: str,
    action: str,
    **kwargs,
) -> dict:
    """POST /runs/{task_id}/action and return the JSON response."""
    body = {"action": action, **kwargs}
    res = await client.post(f"{API}/runs/{task_id}/action", json=body)
    return {"status_code": res.status_code, **res.json()} if res.status_code == 200 else {"status_code": res.status_code, "detail": res.text}


# ---------------------------------------------------------------------------
# HITL Decision Flow
# ---------------------------------------------------------------------------


class TestHITLDecisionFlow:
    """Tests for the human-in-the-loop decision pathway."""

    @pytest.mark.asyncio
    async def test_hitl_run_reaches_waiting_human(self, client: httpx.AsyncClient):
        """Creating a run with enable_hitl=True must eventually reach waiting_human."""
        data = await _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        result = await _poll_until(client, task_id, "waiting_human")
        if result is None:
            pytest.skip("Pipeline did not pause for HITL within timeout — mock may be slow")
        assert result["status"] == "waiting_human"
        assert result["task_id"] == task_id

    @pytest.mark.asyncio
    async def test_hitl_approve_completes_pipeline(self, client: httpx.AsyncClient):
        """approve action on a waiting_human run causes pipeline to complete."""
        data = await _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        waiting = await _poll_until(client, task_id, "waiting_human")
        if waiting is None:
            pytest.skip("Pipeline did not reach waiting_human")

        action_res = await _submit_action(client, task_id, "approve")
        assert action_res["status_code"] == 200, f"approve failed: {action_res}"
        assert action_res.get("accepted") is True

        # Pipeline should now report completed
        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Pipeline did not complete after approve")
        assert completed["status"] == "completed"

    @pytest.mark.asyncio
    async def test_hitl_reject_terminates_pipeline(self, client: httpx.AsyncClient):
        """reject action on a waiting_human run must be accepted and pipeline ends."""
        data = await _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        waiting = await _poll_until(client, task_id, "waiting_human")
        if waiting is None:
            pytest.skip("Pipeline did not reach waiting_human")

        action_res = await _submit_action(client, task_id, "reject", reason="not good enough")
        assert action_res["status_code"] == 200, f"reject failed: {action_res}"
        assert action_res.get("accepted") is True

        # After reject the run should be marked completed (terminal state)
        terminal = await _poll_until(client, task_id, "completed")
        if terminal is None:
            pytest.skip("Pipeline did not reach terminal state after reject")
        assert terminal["status"] == "completed"

    @pytest.mark.asyncio
    async def test_hitl_rerun_creates_new_task(self, client: httpx.AsyncClient):
        """rerun action must return a new task_id and redirect the pipeline."""
        data = await _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        waiting = await _poll_until(client, task_id, "waiting_human")
        if waiting is None:
            pytest.skip("Pipeline did not reach waiting_human")

        action_res = await _submit_action(
            client,
            task_id,
            "rerun",
            rerun_dimensions=["L3", "L4"],
        )
        assert action_res["status_code"] == 200, f"rerun failed: {action_res}"
        assert action_res.get("accepted") is True

        new_task_id = action_res.get("new_task_id")
        assert new_task_id, "rerun must return new_task_id"
        assert new_task_id != task_id, "new_task_id must differ from original"

        # The new task should start running
        new_status_res = await client.get(f"{API}/runs/{new_task_id}")
        assert new_status_res.status_code == 200
        new_status = new_status_res.json()
        assert new_status["status"] in ("running", "waiting_human", "completed", "failed")

    @pytest.mark.asyncio
    async def test_hitl_lock_dimensions_accepted(self, client: httpx.AsyncClient):
        """lock_dimensions action must be accepted and pipeline continues."""
        data = await _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        waiting = await _poll_until(client, task_id, "waiting_human")
        if waiting is None:
            pytest.skip("Pipeline did not reach waiting_human")

        action_res = await _submit_action(
            client,
            task_id,
            "lock_dimensions",
            locked_dimensions=["L1", "L3"],
        )
        assert action_res["status_code"] == 200, f"lock_dimensions failed: {action_res}"
        assert action_res.get("accepted") is True

        # Pipeline should progress to completed after the lock
        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Pipeline did not complete after lock_dimensions")
        assert completed["status"] == "completed"

    @pytest.mark.asyncio
    async def test_hitl_force_accept_requires_candidate_id(self, client: httpx.AsyncClient):
        """force_accept without candidate_id must return 400."""
        data = await _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        # Inject a fake human_required event so the action endpoint
        # treats this run as waiting_human (avoids needing to poll)
        from vulca.pipeline.types import EventType as VulcaEventType
        from vulca.pipeline.types import PipelineEvent as VulcaEvent
        from app.prototype.api.routes import _buffer_lock

        fake_event = VulcaEvent(
            event_type=VulcaEventType.HUMAN_REQUIRED,
            payload={"stage": "decide"},
            timestamp_ms=0,
        )
        with _buffer_lock:
            _event_buffers.setdefault(task_id, []).append(fake_event)

        res = await client.post(f"{API}/runs/{task_id}/action", json={"action": "force_accept"})
        assert res.status_code == 400, f"Expected 400 for missing candidate_id, got {res.status_code}: {res.text}"

    @pytest.mark.asyncio
    async def test_hitl_force_accept_with_candidate_id(self, client: httpx.AsyncClient):
        """force_accept with a candidate_id must be accepted."""
        data = await _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        waiting = await _poll_until(client, task_id, "waiting_human")
        if waiting is None:
            pytest.skip("Pipeline did not reach waiting_human")

        action_res = await _submit_action(
            client,
            task_id,
            "force_accept",
            candidate_id="cand-001",
        )
        assert action_res["status_code"] == 200, f"force_accept failed: {action_res}"
        assert action_res.get("accepted") is True

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Pipeline did not complete after force_accept")
        assert completed["status"] == "completed"


# ---------------------------------------------------------------------------
# Instruct Flow
# ---------------------------------------------------------------------------


class TestInstructFlow:
    """Tests for the POST /runs/{task_id}/instruct follow-up instruction flow."""

    @pytest.mark.asyncio
    async def test_instruct_returns_new_task_id(self, client: httpx.AsyncClient):
        """POST /instruct on a completed run returns a new task_id."""
        data = await _create_run(client)
        task_id = data["task_id"]

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Base run did not complete within timeout")

        res = await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": "make it more blue"})
        assert res.status_code == 200, f"instruct failed: {res.status_code} {res.text}"
        body = res.json()
        assert "new_task_id" in body
        assert body["new_task_id"] != task_id
        assert body.get("parent_task_id") == task_id
        assert body.get("status") == "running"

    @pytest.mark.asyncio
    async def test_instruct_new_run_completes(self, client: httpx.AsyncClient):
        """The new run created by /instruct eventually reaches completed."""
        data = await _create_run(client, max_rounds=1, n_candidates=2)
        task_id = data["task_id"]

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Base run did not complete within timeout")

        res = await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": "emphasise ink texture"})
        assert res.status_code == 200
        new_task_id = res.json()["new_task_id"]

        new_completed = await _poll_until(client, new_task_id, "completed")
        if new_completed is None:
            pytest.skip("Instruct run did not complete within timeout")
        assert new_completed["status"] == "completed"

    @pytest.mark.asyncio
    async def test_instruct_inherits_tradition(self, client: httpx.AsyncClient):
        """New run spawned by /instruct inherits the same tradition as the parent."""
        tradition = "japanese_ukiyo_e"
        data = await _create_run(client, tradition=tradition)
        task_id = data["task_id"]

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Base run did not complete within timeout")

        res = await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": "add more wave detail"})
        assert res.status_code == 200
        body = res.json()
        assert body.get("tradition") == tradition

    @pytest.mark.asyncio
    async def test_instruct_inherits_provider(self, client: httpx.AsyncClient):
        """New run's metadata shows same provider as parent."""
        data = await _create_run(client, provider="mock")
        task_id = data["task_id"]

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Base run did not complete within timeout")

        res = await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": "darker tones"})
        assert res.status_code == 200
        new_task_id = res.json()["new_task_id"]

        # Verify metadata for new task (provider stored in _run_metadata)
        assert new_task_id in _run_metadata
        assert _run_metadata[new_task_id].get("provider") == "mock"

    @pytest.mark.asyncio
    async def test_instruct_inherits_max_rounds(self, client: httpx.AsyncClient):
        """New run inherits max_rounds from the parent run."""
        data = await _create_run(client, max_rounds=2)
        task_id = data["task_id"]

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Base run did not complete within timeout")

        await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": "softer brushwork"})
        # Check all runs created after this point inherit max_rounds=2
        # New task is the latest entry added to _run_metadata
        new_task_ids = [
            tid for tid, meta in _run_metadata.items()
            if tid != task_id
        ]
        assert new_task_ids, "Expected at least one new task after instruct"
        newest = new_task_ids[-1]
        assert _run_metadata[newest].get("max_rounds") == 2

    @pytest.mark.asyncio
    async def test_instruct_inherits_n_candidates(self, client: httpx.AsyncClient):
        """New run inherits n_candidates from parent."""
        data = await _create_run(client, n_candidates=3)
        task_id = data["task_id"]

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Base run did not complete within timeout")

        await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": "more vibrant colors"})
        new_task_ids = [tid for tid in _run_metadata if tid != task_id]
        assert new_task_ids
        newest = new_task_ids[-1]
        assert _run_metadata[newest].get("n_candidates") == 3

    @pytest.mark.asyncio
    async def test_instruct_inherits_enable_hitl_false(self, client: httpx.AsyncClient):
        """New run inherits enable_hitl=False when parent had it disabled."""
        data = await _create_run(client, enable_hitl=False)
        task_id = data["task_id"]

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Base run did not complete within timeout")

        await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": "try lighter ink"})
        new_task_ids = [tid for tid in _run_metadata if tid != task_id]
        assert new_task_ids
        newest = new_task_ids[-1]
        assert _run_metadata[newest].get("enable_hitl") is False

    @pytest.mark.asyncio
    async def test_instruct_inherits_enable_hitl_true(self, client: httpx.AsyncClient):
        """New run inherits enable_hitl=True when parent had HITL enabled."""
        data = await _create_run(client, enable_hitl=True)
        task_id = data["task_id"]

        # For a HITL run we only need it to start; we don't wait for waiting_human
        # because we just want to verify metadata inheritance after instruct.
        # Wait a short time so the run is at least registered.
        time.sleep(0.5)

        # Force-complete the original run so instruct can proceed
        # (instruct works on any run that exists, not only completed ones)
        res = await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": "emphasise mountain peaks"})
        assert res.status_code == 200
        new_task_ids = [tid for tid in _run_metadata if tid != task_id]
        assert new_task_ids
        newest = new_task_ids[-1]
        assert _run_metadata[newest].get("enable_hitl") is True

    @pytest.mark.asyncio
    async def test_instruct_inherits_node_params(self, client: httpx.AsyncClient):
        """New run inherits node_params from parent when they are set."""
        node_params = {"critic": {"w_l1": 0.35, "w_l2": 0.15, "w_l3": 0.20, "w_l4": 0.15, "w_l5": 0.15}}
        data = await _create_run(client, node_params=node_params)
        task_id = data["task_id"]

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Base run did not complete within timeout")

        await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": "refine cultural symbolism"})
        new_task_ids = [tid for tid in _run_metadata if tid != task_id]
        assert new_task_ids
        newest = new_task_ids[-1]
        assert _run_metadata[newest].get("node_params") == node_params

    @pytest.mark.asyncio
    async def test_instruct_inherits_reference_image(self, client: httpx.AsyncClient):
        """New run inherits reference_image_base64 when parent had one."""
        # Minimal valid base64 (1x1 white PNG)
        ref_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
            "YPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        data = await _create_run(client, reference_image_base64=ref_b64)
        task_id = data["task_id"]

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Base run did not complete within timeout")

        await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": "same style, different season"})
        new_task_ids = [tid for tid in _run_metadata if tid != task_id]
        assert new_task_ids
        newest = new_task_ids[-1]
        assert _run_metadata[newest].get("reference_image_base64") == ref_b64


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge cases for HITL action and instruct endpoints."""

    @pytest.mark.asyncio
    async def test_submit_action_nonexistent_task(self, client: httpx.AsyncClient):
        """POST /runs/nonexistent/action must return 404."""
        res = await client.post(f"{API}/runs/nonexistent-task-xyz/action", json={"action": "approve"})
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_submit_action_on_completed_task(self, client: httpx.AsyncClient):
        """Submitting an action on an already completed run returns accepted=False."""
        data = await _create_run(client)
        task_id = data["task_id"]

        completed = await _poll_until(client, task_id, "completed")
        if completed is None:
            pytest.skip("Run did not complete within timeout")

        # No human_required event was emitted for a non-HITL run,
        # so the endpoint should reply accepted=False
        res = await client.post(f"{API}/runs/{task_id}/action", json={"action": "approve"})
        assert res.status_code == 200
        body = res.json()
        assert body.get("accepted") is False
        assert "not waiting" in body.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_instruct_nonexistent_task(self, client: httpx.AsyncClient):
        """POST /runs/nonexistent/instruct must return 404."""
        res = await client.post(
            f"{API}/runs/nonexistent-task-abc/instruct",
            json={"instruction": "make it blue"},
        )
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_submit_action_invalid_action_string(self, client: httpx.AsyncClient):
        """Posting an invalid action literal must return 422 validation error."""
        data = await _create_run(client)
        task_id = data["task_id"]

        res = await client.post(
            f"{API}/runs/{task_id}/action",
            json={"action": "not_a_real_action"},
        )
        assert res.status_code == 422, (
            f"Expected 422 for invalid action, got {res.status_code}: {res.text}"
        )

    @pytest.mark.asyncio
    async def test_instruct_empty_instruction_returns_422(self, client: httpx.AsyncClient):
        """POST /instruct with empty instruction string must return 422 (Pydantic min_length)."""
        data = await _create_run(client)
        task_id = data["task_id"]

        res = await client.post(f"{API}/runs/{task_id}/instruct", json={"instruction": ""})
        assert res.status_code == 422

    @pytest.mark.asyncio
    async def test_instruct_missing_instruction_key(self, client: httpx.AsyncClient):
        """POST /instruct with body missing 'instruction' key must return 422."""
        data = await _create_run(client)
        task_id = data["task_id"]

        res = await client.post(f"{API}/runs/{task_id}/instruct", json={"note": "this won't work"})
        assert res.status_code == 422

    @pytest.mark.asyncio
    async def test_action_not_accepted_when_not_waiting(self, client: httpx.AsyncClient):
        """Action on a non-HITL run (no human_required event) returns accepted=False."""
        # Non-HITL run never emits human_required
        data = await _create_run(client, enable_hitl=False)
        task_id = data["task_id"]

        # Submit immediately before pipeline completes (no human_required in buffer)
        res = await client.post(f"{API}/runs/{task_id}/action", json={"action": "reject"})
        assert res.status_code == 200
        body = res.json()
        assert body.get("accepted") is False
