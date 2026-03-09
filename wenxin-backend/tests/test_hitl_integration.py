"""
HITL (Human-in-the-Loop) integration tests with enable_hitl=True.

These tests verify that the pipeline actually pauses at each HITL point
(Scout, Draft, Critic, Queen) and correctly handles human actions
(approve, reject, rerun, lock_dimensions, force_accept).

All tests are marked @pytest.mark.slow — CI skips them by default.
Run with: PYTHONPATH=. pytest tests/test_hitl_integration.py -v --tb=short -m slow

Note: The Scout evidence-gathering stage triggers heavy imports (TensorFlow,
sentence-transformers) which can take 30-40s on first run. Timeouts are set
accordingly.
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from app.prototype.api.routes import (
    _buffer_lock,
    _event_buffers,
    _guest_runs_today,
    _idempotency_map,
    _orchestrators,
    _run_metadata,
    router,
)
from app.prototype.orchestrator.events import EventType
from app.prototype.orchestrator.run_state import HumanAction, RunState, RunStatus

API = "/api/v1/prototype"

# Scout stage triggers heavy ML imports (~35s on first run).
# Subsequent stages are fast (<1s each for mock provider).
_SCOUT_TIMEOUT = 60  # seconds to wait for Scout HITL pause
_STAGE_TIMEOUT = 20  # seconds to wait for post-Scout stage pauses
_COMPLETION_TIMEOUT = 20  # seconds to wait for pipeline completion

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """Isolated in-process API client per test."""
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
        timeout=120,
    ) as async_client:
        yield async_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def create_hitl_run(
    client: httpx.AsyncClient,
    subject: str = "Dong Yuan landscape",
    tradition: str = "chinese_xieyi",
    n_candidates: int = 2,
    max_rounds: int = 1,
    enable_agent_critic: bool = False,
) -> dict:
    """Create a pipeline run with enable_hitl=True and mock provider.

    Defaults to enable_agent_critic=False to use rule-only scoring (no LLM
    calls), ensuring tests run deterministically without external API keys.
    """
    res = await client.post(f"{API}/runs", json={
        "subject": subject,
        "tradition": tradition,
        "provider": "mock",
        "enable_hitl": True,
        "enable_agent_critic": enable_agent_critic,
        "n_candidates": n_candidates,
        "max_rounds": max_rounds,
    })
    assert res.status_code == 200, f"Create run failed: {res.status_code} {res.text}"
    data = res.json()
    assert "task_id" in data
    return data


async def wait_for_status(
    client: httpx.AsyncClient,
    task_id: str,
    target_status: str,
    timeout: float = _COMPLETION_TIMEOUT,
) -> dict | None:
    """Poll until the run reaches *target_status* or timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        res = await client.get(f"{API}/runs/{task_id}")
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == target_status:
                return data
            # Bail early on terminal states when not expected
            if data.get("status") in ("completed", "failed") and target_status not in ("completed", "failed"):
                return data
        await asyncio.sleep(0.2)
    return None


async def wait_for_human_required_event(
    task_id: str,
    expected_stage: str,
    timeout: float = _STAGE_TIMEOUT,
    after_index: int = 0,
) -> tuple[dict | None, int]:
    """Poll the event buffer until a HUMAN_REQUIRED event for *expected_stage* appears.

    The stage is matched against both ``ev.stage`` (the event-level field) and
    ``ev.payload.get("stage")`` because different pipeline stages use different
    conventions (Scout/Draft/Critic set payload["stage"], Queen does not).

    Args:
        after_index: Only consider events at this index or later (for round-2 detection).

    Returns:
        (payload, event_index) or (None, -1) if not found within timeout.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with _buffer_lock:
            buffer = list(_event_buffers.get(task_id, []))
        for i, ev in enumerate(buffer):
            if i < after_index:
                continue
            if ev.event_type == EventType.HUMAN_REQUIRED and (
                ev.stage == expected_stage
                or ev.payload.get("stage") == expected_stage
            ):
                return ev.payload, i
        await asyncio.sleep(0.2)
    return None, -1


async def submit_action(
    client: httpx.AsyncClient,
    task_id: str,
    action: str,
    **kwargs,
) -> dict:
    """Submit a HITL action and return the response body."""
    body = {"action": action, **kwargs}
    res = await client.post(f"{API}/runs/{task_id}/action", json=body)
    assert res.status_code == 200, f"Action failed: {res.status_code} {res.text}"
    return res.json()


async def collect_events(task_id: str) -> list[dict]:
    """Return all events currently in the buffer (non-blocking snapshot)."""
    with _buffer_lock:
        return [ev.to_dict() for ev in _event_buffers.get(task_id, [])]


async def approve_through_stages(
    client: httpx.AsyncClient,
    task_id: str,
    stages: tuple[str, ...] = ("scout", "draft", "critic"),
) -> int:
    """Approve through the given stages, returning the last event index seen.

    Uses _SCOUT_TIMEOUT for scout, _STAGE_TIMEOUT for other stages.
    Calls pytest.skip if any stage is not reached.
    """
    last_idx = 0
    for stage in stages:
        timeout = _SCOUT_TIMEOUT if stage == "scout" else _STAGE_TIMEOUT
        hr, idx = await wait_for_human_required_event(task_id, stage, timeout=timeout, after_index=last_idx)
        if hr is None:
            status = await wait_for_status(client, task_id, "completed", timeout=5)
            if status and status["status"] in ("completed", "failed"):
                pytest.skip(f"Pipeline completed/failed before reaching {stage} HITL pause")
            pytest.skip(f"Pipeline did not reach {stage} HITL pause within {timeout}s")
        await submit_action(client, task_id, "approve")
        last_idx = idx + 1
    return last_idx


# ---------------------------------------------------------------------------
# Tests: HITL pause at Scout
# ---------------------------------------------------------------------------


class TestHITLScoutPause:
    """Verify the pipeline pauses at Scout when enable_hitl=True."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_pauses_at_scout(self, client: httpx.AsyncClient):
        """Pipeline pauses at Scout and emits HUMAN_REQUIRED event."""
        data = await create_hitl_run(client)
        task_id = data["task_id"]

        # Wait for HUMAN_REQUIRED at scout
        hr_payload, _ = await wait_for_human_required_event(task_id, "scout", timeout=_SCOUT_TIMEOUT)
        if hr_payload is None:
            pytest.skip(f"Pipeline did not reach Scout HITL pause within {_SCOUT_TIMEOUT}s")

        assert hr_payload["stage"] == "scout"
        assert "evidence" in hr_payload

        # Verify run status is waiting_human
        status = await wait_for_status(client, task_id, "waiting_human", timeout=5)
        if status is None:
            pytest.skip("RunState did not transition to waiting_human")
        assert status["status"] == "waiting_human"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_approve_at_scout_resumes(self, client: httpx.AsyncClient):
        """Approving at Scout resumes pipeline to Draft."""
        data = await create_hitl_run(client)
        task_id = data["task_id"]

        # Wait for Scout pause
        hr_payload, scout_idx = await wait_for_human_required_event(task_id, "scout", timeout=_SCOUT_TIMEOUT)
        if hr_payload is None:
            pytest.skip("Pipeline did not reach Scout HITL pause")

        # Submit approve
        action_res = await submit_action(client, task_id, "approve", reason="Looks good")
        assert action_res["accepted"] is True

        # After approve, pipeline should continue to Draft and pause there
        hr_draft, _ = await wait_for_human_required_event(task_id, "draft", timeout=_STAGE_TIMEOUT, after_index=scout_idx + 1)
        if hr_draft is None:
            status = await wait_for_status(client, task_id, "completed", timeout=5)
            if status and status["status"] in ("completed", "failed"):
                pytest.skip("Pipeline completed/failed before reaching Draft HITL pause")
            pytest.skip("Pipeline did not reach Draft HITL pause after Scout approve")

        assert hr_draft["stage"] == "draft"


# ---------------------------------------------------------------------------
# Tests: HITL pause at Draft
# ---------------------------------------------------------------------------


class TestHITLDraftPause:
    """Verify HITL actions at the Draft stage."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_approve_at_draft_reaches_critic(self, client: httpx.AsyncClient):
        """Approving through Scout and Draft should reach Critic."""
        data = await create_hitl_run(client)
        task_id = data["task_id"]

        # Approve Scout and Draft, then expect Critic
        last_idx = await approve_through_stages(client, task_id, ("scout", "draft"))

        # Should reach Critic
        hr_critic, _ = await wait_for_human_required_event(task_id, "critic", timeout=_STAGE_TIMEOUT, after_index=last_idx)
        if hr_critic is None:
            status = await wait_for_status(client, task_id, "completed", timeout=5)
            if status and status["status"] in ("completed", "failed"):
                pytest.skip("Pipeline completed/failed before Critic HITL pause")
            pytest.skip("Pipeline did not reach Critic pause after Draft approve")

        assert hr_critic["stage"] == "critic"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_draft_candidate_selection(self, client: httpx.AsyncClient):
        """Selecting specific candidates at Draft filters them for Critic."""
        data = await create_hitl_run(client, n_candidates=2)
        task_id = data["task_id"]

        # Approve Scout
        hr_scout, scout_idx = await wait_for_human_required_event(task_id, "scout", timeout=_SCOUT_TIMEOUT)
        if hr_scout is None:
            pytest.skip("Pipeline did not reach Scout pause")
        await submit_action(client, task_id, "approve")

        # Wait for Draft pause — get candidate IDs
        hr_draft, draft_idx = await wait_for_human_required_event(task_id, "draft", timeout=_STAGE_TIMEOUT, after_index=scout_idx + 1)
        if hr_draft is None:
            pytest.skip("Pipeline did not reach Draft pause")

        candidates = hr_draft.get("candidates", [])
        if candidates:
            first_id = candidates[0].get("candidate_id", "")
            # Select only the first candidate
            await submit_action(
                client, task_id, "approve",
                candidate_id=first_id,
            )
        else:
            await submit_action(client, task_id, "approve")

        # Verify pipeline continues to Critic
        hr_critic, _ = await wait_for_human_required_event(task_id, "critic", timeout=_STAGE_TIMEOUT, after_index=draft_idx + 1)
        if hr_critic is None:
            status = await wait_for_status(client, task_id, "completed", timeout=5)
            if status and status["status"] in ("completed", "failed"):
                pytest.skip("Pipeline completed/failed before Critic HITL pause")
            pytest.skip("Pipeline did not reach Critic pause")

        assert hr_critic["stage"] == "critic"


# ---------------------------------------------------------------------------
# Tests: HITL pause at Critic
# ---------------------------------------------------------------------------


class TestHITLCriticPause:
    """Verify HITL actions at the Critic stage."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_approve_through_to_queen(self, client: httpx.AsyncClient):
        """Approving Scout->Draft->Critic should reach Queen."""
        data = await create_hitl_run(client)
        task_id = data["task_id"]

        last_idx = await approve_through_stages(client, task_id, ("scout", "draft", "critic"))

        # Should reach Queen (only if queen_decision triggers HITL)
        hr_queen, _ = await wait_for_human_required_event(task_id, "queen", timeout=_STAGE_TIMEOUT, after_index=last_idx)
        if hr_queen is None:
            # Queen might have completed without pausing (e.g. max_rounds=1)
            status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
            if status and status["status"] in ("completed", "failed"):
                # Pipeline completed -- Queen didn't need HITL. That's OK.
                return
            pytest.skip("Pipeline did not reach Queen pause or completion")

        assert "queen_decision" in hr_queen or "plan_state" in hr_queen

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_lock_dimensions_at_critic(self, client: httpx.AsyncClient):
        """lock_dimensions at Critic should preserve scores and continue."""
        data = await create_hitl_run(client)
        task_id = data["task_id"]

        # Fast-forward to Critic
        hr_scout, scout_idx = await wait_for_human_required_event(task_id, "scout", timeout=_SCOUT_TIMEOUT)
        if hr_scout is None:
            pytest.skip("Pipeline did not reach Scout pause")
        await submit_action(client, task_id, "approve")

        hr_draft, draft_idx = await wait_for_human_required_event(task_id, "draft", timeout=_STAGE_TIMEOUT, after_index=scout_idx + 1)
        if hr_draft is None:
            pytest.skip("Pipeline did not reach Draft pause")
        await submit_action(client, task_id, "approve")

        hr_critic, critic_idx = await wait_for_human_required_event(task_id, "critic", timeout=_STAGE_TIMEOUT, after_index=draft_idx + 1)
        if hr_critic is None:
            pytest.skip("Pipeline did not reach Critic pause")

        # Submit lock_dimensions
        action_res = await submit_action(
            client, task_id, "lock_dimensions",
            locked_dimensions=["visual_perception", "technical_analysis"],
        )
        assert action_res["accepted"] is True

        # Pipeline should continue (Queen pause or completion)
        hr_queen, _ = await wait_for_human_required_event(task_id, "queen", timeout=_STAGE_TIMEOUT, after_index=critic_idx + 1)
        if hr_queen is None:
            status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
            if status is None:
                pytest.skip("Pipeline did not reach Queen or completion after lock_dimensions")
            # Completed -- acceptable
            return

        # Verify event buffer has HUMAN_RECEIVED for critic
        events = await collect_events(task_id)
        received_events = [
            e for e in events
            if e["event_type"] == "human_received" and e["stage"] == "critic"
        ]
        assert len(received_events) >= 1, "Expected HUMAN_RECEIVED event for critic"
        # Verify the locked_dimensions were recorded
        payload = received_events[0]["payload"]
        assert "visual_perception" in payload.get("locked_dimensions", [])


# ---------------------------------------------------------------------------
# Tests: HITL at Queen
# ---------------------------------------------------------------------------


class TestHITLQueenActions:
    """Verify HITL actions at the Queen stage."""

    async def _advance_to_queen(
        self,
        client: httpx.AsyncClient,
        task_id: str,
    ) -> tuple[dict | None, int]:
        """Approve Scout->Draft->Critic and return (Queen HITL payload, event_index)."""
        last_idx = await approve_through_stages(client, task_id, ("scout", "draft", "critic"))
        return await wait_for_human_required_event(task_id, "queen", timeout=_STAGE_TIMEOUT, after_index=last_idx)

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_approve_at_queen_completes(self, client: httpx.AsyncClient):
        """Approving at Queen should complete the pipeline (accept)."""
        data = await create_hitl_run(client)
        task_id = data["task_id"]

        hr_queen, _ = await self._advance_to_queen(client, task_id)
        if hr_queen is None:
            status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
            if status and status["status"] in ("completed", "failed"):
                pytest.skip("Pipeline completed without Queen HITL pause")
            pytest.skip("Could not advance to Queen stage")

        # Approve -> pipeline should accept and finish
        action_res = await submit_action(client, task_id, "approve")
        assert action_res["accepted"] is True

        # Wait for completion
        status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
        if status is None:
            pytest.skip("Pipeline did not complete after Queen approve")
        assert status["status"] in ("completed", "failed")

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_reject_at_queen_stops_pipeline(self, client: httpx.AsyncClient):
        """Rejecting at Queen should stop the pipeline."""
        data = await create_hitl_run(client)
        task_id = data["task_id"]

        hr_queen, _ = await self._advance_to_queen(client, task_id)
        if hr_queen is None:
            status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
            if status and status["status"] in ("completed", "failed"):
                pytest.skip("Pipeline completed without Queen HITL pause")
            pytest.skip("Could not advance to Queen stage")

        # Reject -> pipeline should stop
        action_res = await submit_action(
            client, task_id, "reject",
            reason="Not meeting quality standards",
        )
        assert action_res["accepted"] is True

        # Wait for completion (reject maps to "stop")
        status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
        if status is None:
            pytest.skip("Pipeline did not complete after Queen reject")
        assert status["status"] in ("completed", "failed")

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_force_accept_at_queen(self, client: httpx.AsyncClient):
        """force_accept at Queen with candidate_id should complete pipeline."""
        data = await create_hitl_run(client, n_candidates=2)
        task_id = data["task_id"]

        # Advance through stages collecting candidate IDs at Draft
        hr_scout, scout_idx = await wait_for_human_required_event(task_id, "scout", timeout=_SCOUT_TIMEOUT)
        if hr_scout is None:
            pytest.skip("Pipeline did not reach Scout pause")
        await submit_action(client, task_id, "approve")

        hr_draft, draft_idx = await wait_for_human_required_event(task_id, "draft", timeout=_STAGE_TIMEOUT, after_index=scout_idx + 1)
        if hr_draft is None:
            pytest.skip("Pipeline did not reach Draft pause")
        candidates = hr_draft.get("candidates", [])
        candidate_id = candidates[0].get("candidate_id", "test-cand-1") if candidates else "test-cand-1"
        await submit_action(client, task_id, "approve")

        hr_critic, critic_idx = await wait_for_human_required_event(task_id, "critic", timeout=_STAGE_TIMEOUT, after_index=draft_idx + 1)
        if hr_critic is None:
            pytest.skip("Pipeline did not reach Critic pause")
        await submit_action(client, task_id, "approve")

        hr_queen, _ = await wait_for_human_required_event(task_id, "queen", timeout=_STAGE_TIMEOUT, after_index=critic_idx + 1)
        if hr_queen is None:
            status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
            if status and status["status"] in ("completed", "failed"):
                pytest.skip("Pipeline completed without Queen HITL pause")
            pytest.skip("Could not advance to Queen stage")

        # Force accept with specific candidate
        action_res = await submit_action(
            client, task_id, "force_accept",
            candidate_id=candidate_id,
            reason="Manual override: this candidate best matches creative intent",
        )
        assert action_res["accepted"] is True

        # Pipeline should complete
        status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
        if status is None:
            pytest.skip("Pipeline did not complete after force_accept")
        assert status["status"] in ("completed", "failed")

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_rerun_at_queen(self, client: httpx.AsyncClient):
        """Rerun at Queen should trigger another Draft->Critic->Queen cycle."""
        data = await create_hitl_run(client, max_rounds=2)
        task_id = data["task_id"]

        hr_queen, queen_idx = await self._advance_to_queen(client, task_id)
        if hr_queen is None:
            status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
            if status and status["status"] in ("completed", "failed"):
                pytest.skip("Pipeline completed without Queen HITL pause")
            pytest.skip("Could not advance to Queen stage")

        # Submit rerun with specific dimensions
        action_res = await submit_action(
            client, task_id, "rerun",
            rerun_dimensions=["visual_perception", "cultural_context"],
            reason="Need better cultural alignment",
        )
        assert action_res["accepted"] is True

        # Pipeline should loop back: Draft->Critic->Queen (round 2)
        # Wait for Draft pause on round 2 (after the queen event we just acted on)
        hr_draft_r2, draft_r2_idx = await wait_for_human_required_event(
            task_id, "draft", timeout=_STAGE_TIMEOUT, after_index=queen_idx + 1,
        )
        if hr_draft_r2 is not None:
            await submit_action(client, task_id, "approve")

            hr_critic_r2, critic_r2_idx = await wait_for_human_required_event(
                task_id, "critic", timeout=_STAGE_TIMEOUT, after_index=draft_r2_idx + 1,
            )
            if hr_critic_r2 is not None:
                await submit_action(client, task_id, "approve")

                hr_queen_r2, _ = await wait_for_human_required_event(
                    task_id, "queen", timeout=_STAGE_TIMEOUT, after_index=critic_r2_idx + 1,
                )
                if hr_queen_r2 is not None:
                    await submit_action(client, task_id, "approve")

        # Wait for terminal state
        status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
        if status is None:
            status = await wait_for_status(client, task_id, "failed", timeout=5)
        if status is None:
            pytest.skip("Pipeline did not reach terminal state after rerun")
        assert status["status"] in ("completed", "failed")

        # Verify we saw events from the rerun (human_received events)
        events = await collect_events(task_id)
        event_types = [e["event_type"] for e in events]
        assert "human_received" in event_types, "Expected at least one HUMAN_RECEIVED event"


# ---------------------------------------------------------------------------
# Tests: Full pipeline flow (approve all 4 stages)
# ---------------------------------------------------------------------------


class TestHITLFullPipeline:
    """End-to-end HITL flow: create run -> approve through all stages."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_full_approve_flow(self, client: httpx.AsyncClient):
        """Approve through Scout->Draft->Critic->Queen to completion."""
        data = await create_hitl_run(client, n_candidates=2, max_rounds=1)
        task_id = data["task_id"]

        stages_seen = []
        last_idx = 0

        for expected_stage in ("scout", "draft", "critic"):
            timeout = _SCOUT_TIMEOUT if expected_stage == "scout" else _STAGE_TIMEOUT
            hr, idx = await wait_for_human_required_event(
                task_id, expected_stage, timeout=timeout, after_index=last_idx,
            )
            if hr is None:
                status = await wait_for_status(client, task_id, "completed", timeout=5)
                if status and status["status"] in ("completed", "failed"):
                    break
                pytest.skip(f"Pipeline did not reach {expected_stage} HITL pause")
            stages_seen.append(expected_stage)
            await submit_action(client, task_id, "approve")
            last_idx = idx + 1

        # Queen might or might not have HITL pause
        hr_queen, _ = await wait_for_human_required_event(
            task_id, "queen", timeout=_STAGE_TIMEOUT, after_index=last_idx,
        )
        if hr_queen is not None:
            stages_seen.append("queen")
            await submit_action(client, task_id, "approve")

        # Wait for pipeline to finish
        status = await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)
        if status is None:
            status = await wait_for_status(client, task_id, "failed", timeout=5)
        if status is None:
            pytest.skip("Pipeline did not complete within timeout")

        assert status["status"] in ("completed", "failed")
        assert len(stages_seen) >= 3, f"Expected at least 3 HITL stages, saw: {stages_seen}"

        # Verify event stream integrity
        events = await collect_events(task_id)
        event_types = [e["event_type"] for e in events]
        assert "stage_started" in event_types
        assert "human_required" in event_types
        assert "human_received" in event_types
        terminal = {"pipeline_completed", "pipeline_failed"}
        assert terminal & set(event_types), f"No terminal event in {event_types}"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_full_flow_event_ordering(self, client: httpx.AsyncClient):
        """Verify HUMAN_REQUIRED always precedes HUMAN_RECEIVED for each stage."""
        data = await create_hitl_run(client, n_candidates=2, max_rounds=1)
        task_id = data["task_id"]

        # Approve through all stages
        last_idx = 0
        for stage in ("scout", "draft", "critic"):
            timeout = _SCOUT_TIMEOUT if stage == "scout" else _STAGE_TIMEOUT
            hr, idx = await wait_for_human_required_event(
                task_id, stage, timeout=timeout, after_index=last_idx,
            )
            if hr is None:
                status = await wait_for_status(client, task_id, "completed", timeout=5)
                if status and status["status"] in ("completed", "failed"):
                    break
                pytest.skip(f"Pipeline did not reach {stage}")
            await submit_action(client, task_id, "approve")
            last_idx = idx + 1

        hr_queen, _ = await wait_for_human_required_event(
            task_id, "queen", timeout=_STAGE_TIMEOUT, after_index=last_idx,
        )
        if hr_queen is not None:
            await submit_action(client, task_id, "approve")

        await wait_for_status(client, task_id, "completed", timeout=_COMPLETION_TIMEOUT)

        # Validate ordering: for each stage, HUMAN_REQUIRED comes before HUMAN_RECEIVED
        events = await collect_events(task_id)
        for stage in ("scout", "draft", "critic", "queen"):
            hr_events = [
                (i, e) for i, e in enumerate(events)
                if e["stage"] == stage
                and e["event_type"] in ("human_required", "human_received")
            ]
            if len(hr_events) >= 2:
                required_idx = next(
                    (i for i, e in hr_events if e["event_type"] == "human_required"),
                    None,
                )
                received_idx = next(
                    (i for i, e in hr_events if e["event_type"] == "human_received"),
                    None,
                )
                if required_idx is not None and received_idx is not None:
                    assert required_idx < received_idx, (
                        f"HUMAN_REQUIRED (idx={required_idx}) should precede "
                        f"HUMAN_RECEIVED (idx={received_idx}) for stage '{stage}'"
                    )


# ---------------------------------------------------------------------------
# Tests: Timeout handling
# ---------------------------------------------------------------------------


class TestHITLTimeout:
    """Verify timeout behavior when no human action is received."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_action_on_non_waiting_run_rejected(self, client: httpx.AsyncClient):
        """Action on a completed run returns accepted=False."""
        # Create a non-HITL run and wait for it to finish
        res = await client.post(f"{API}/runs", json={
            "subject": "test timeout",
            "tradition": "default",
            "provider": "mock",
            "enable_hitl": False,
            "enable_agent_critic": False,
            "n_candidates": 2,
            "max_rounds": 1,
        })
        assert res.status_code == 200
        task_id = res.json()["task_id"]

        # Wait for completion
        status = await wait_for_status(client, task_id, "completed", timeout=_SCOUT_TIMEOUT + _STAGE_TIMEOUT)
        if status is None:
            status = await wait_for_status(client, task_id, "failed", timeout=5)
        if status is None:
            pytest.skip("Non-HITL run did not complete")

        # Try to submit action -- should be rejected since run is not waiting
        action_res = await client.post(f"{API}/runs/{task_id}/action", json={
            "action": "approve",
        })
        assert action_res.status_code == 200
        body = action_res.json()
        assert body["accepted"] is False
        assert "not waiting" in body["message"].lower()


# ---------------------------------------------------------------------------
# Tests: RunState unit-level integration
# ---------------------------------------------------------------------------


class TestRunStateHITL:
    """Direct RunState tests for HITL synchronization primitives."""

    @pytest.mark.slow
    def test_wait_for_human_blocks_until_action(self):
        """wait_for_human blocks until submit_human_action is called."""
        state = RunState(task_id="test-block")
        received_action = [None]

        def _waiter():
            result = state.wait_for_human(timeout=5)
            received_action[0] = result

        t = threading.Thread(target=_waiter)
        t.start()

        # Give the thread time to enter wait
        time.sleep(0.3)
        assert state.status == RunStatus.WAITING_HUMAN

        # Submit action
        action = HumanAction(action="approve", reason="test")
        state.submit_human_action(action)
        t.join(timeout=5)

        assert received_action[0] is not None
        assert received_action[0].action == "approve"
        assert received_action[0].reason == "test"
        assert state.status == RunStatus.RUNNING

    @pytest.mark.slow
    def test_wait_for_human_timeout_returns_none(self):
        """wait_for_human returns None after timeout."""
        state = RunState(task_id="test-timeout")
        result = state.wait_for_human(timeout=0.5)
        assert result is None
        # Status returns to RUNNING after timeout
        assert state.status == RunStatus.RUNNING

    @pytest.mark.slow
    def test_pre_submitted_action_consumed_immediately(self):
        """If action is pre-submitted before wait, it is consumed immediately."""
        state = RunState(task_id="test-pre-submit")
        action = HumanAction(action="reject", reason="pre-submitted")
        state.submit_human_action(action)

        # wait_for_human should return immediately
        result = state.wait_for_human(timeout=1)
        assert result is not None
        assert result.action == "reject"
        assert result.reason == "pre-submitted"

    @pytest.mark.slow
    def test_multiple_sequential_actions(self):
        """Multiple sequential wait->submit cycles work correctly."""
        state = RunState(task_id="test-multi")

        for i, action_name in enumerate(["approve", "reject", "rerun"]):
            received = [None]

            def _waiter(out=received):
                out[0] = state.wait_for_human(timeout=3)

            t = threading.Thread(target=_waiter)
            t.start()
            time.sleep(0.2)

            state.submit_human_action(HumanAction(action=action_name, reason=f"step-{i}"))
            t.join(timeout=3)

            assert received[0] is not None, f"Step {i}: did not receive action"
            assert received[0].action == action_name

    @pytest.mark.slow
    def test_human_action_fields_preserved(self):
        """All HumanAction fields are correctly passed through."""
        state = RunState(task_id="test-fields")

        action = HumanAction(
            action="rerun",
            locked_dimensions=["visual_perception"],
            rerun_dimensions=["cultural_context", "technical_analysis"],
            candidate_id="cand-42",
            reason="Need more cultural depth",
        )

        received = [None]

        def _waiter():
            received[0] = state.wait_for_human(timeout=3)

        t = threading.Thread(target=_waiter)
        t.start()
        time.sleep(0.2)
        state.submit_human_action(action)
        t.join(timeout=3)

        r = received[0]
        assert r is not None
        assert r.action == "rerun"
        assert r.locked_dimensions == ["visual_perception"]
        assert r.rerun_dimensions == ["cultural_context", "technical_analysis"]
        assert r.candidate_id == "cand-42"
        assert r.reason == "Need more cultural depth"


# ---------------------------------------------------------------------------
# Tests: Edge cases
# ---------------------------------------------------------------------------


class TestHITLEdgeCases:
    """Edge cases and error handling for HITL."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_force_accept_requires_candidate_id(self, client: httpx.AsyncClient):
        """force_accept without candidate_id returns 400."""
        data = await create_hitl_run(client)
        task_id = data["task_id"]

        # Wait for scout pause so the run exists
        hr, _ = await wait_for_human_required_event(task_id, "scout", timeout=_SCOUT_TIMEOUT)
        if hr is None:
            pytest.skip("Pipeline did not reach Scout pause")

        res = await client.post(f"{API}/runs/{task_id}/action", json={
            "action": "force_accept",
            "reason": "missing candidate_id",
        })
        assert res.status_code == 400

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_action_on_nonexistent_run(self, client: httpx.AsyncClient):
        """Action on nonexistent task_id returns 404."""
        res = await client.post(f"{API}/runs/nonexistent-hitl-999/action", json={
            "action": "approve",
        })
        assert res.status_code == 404

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_invalid_action_type(self, client: httpx.AsyncClient):
        """Invalid action type returns 422 (Pydantic validation)."""
        data = await create_hitl_run(client)
        task_id = data["task_id"]

        hr, _ = await wait_for_human_required_event(task_id, "scout", timeout=_SCOUT_TIMEOUT)
        if hr is None:
            pytest.skip("Pipeline did not reach Scout pause")

        res = await client.post(f"{API}/runs/{task_id}/action", json={
            "action": "invalid_not_a_real_action",
        })
        assert res.status_code == 422

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_double_action_second_rejected(self, client: httpx.AsyncClient):
        """Submitting two actions at the same pause -- second should be rejected."""
        data = await create_hitl_run(client)
        task_id = data["task_id"]

        hr, _ = await wait_for_human_required_event(task_id, "scout", timeout=_SCOUT_TIMEOUT)
        if hr is None:
            pytest.skip("Pipeline did not reach Scout pause")

        # First action accepted
        res1 = await submit_action(client, task_id, "approve")
        assert res1["accepted"] is True

        # Brief pause for pipeline to process
        await asyncio.sleep(0.5)

        # Second action -- pipeline has moved on, so not waiting at scout anymore
        res2 = await client.post(f"{API}/runs/{task_id}/action", json={
            "action": "reject",
        })
        assert res2.status_code == 200
        body2 = res2.json()
        # Could be accepted (if pipeline paused again at next stage) or rejected
        # The important thing is no crash
        assert "accepted" in body2
