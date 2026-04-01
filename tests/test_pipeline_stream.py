"""Tests for execute_stream() async generator."""

from __future__ import annotations

import pytest

from vulca.pipeline.engine import execute_stream
from vulca.pipeline.types import EventType, PipelineInput
from vulca.pipeline import FAST


# ── Basic streaming ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_execute_stream_yields_events():
    """execute_stream() must yield at least one PipelineEvent."""
    inp = PipelineInput(subject="test stream", tradition="default", provider="mock")
    events = []
    async for event in execute_stream(FAST, inp):
        events.append(event)

    assert len(events) > 0, "execute_stream should yield at least one event"


@pytest.mark.asyncio
async def test_execute_stream_contains_stage_events():
    """execute_stream() must include STAGE_STARTED and STAGE_COMPLETED events."""
    inp = PipelineInput(subject="stage events", tradition="default", provider="mock")
    event_types = []
    async for event in execute_stream(FAST, inp):
        event_types.append(event.event_type)

    assert EventType.STAGE_STARTED in event_types, "Missing STAGE_STARTED event"
    assert EventType.STAGE_COMPLETED in event_types, "Missing STAGE_COMPLETED event"


@pytest.mark.asyncio
async def test_execute_stream_ends_with_pipeline_completed():
    """Last event from execute_stream() must be PIPELINE_COMPLETED."""
    inp = PipelineInput(subject="terminal event", tradition="default", provider="mock")
    last_event = None
    async for event in execute_stream(FAST, inp):
        last_event = event

    assert last_event is not None
    assert last_event.event_type == EventType.PIPELINE_COMPLETED, (
        f"Expected PIPELINE_COMPLETED as last event, got {last_event.event_type}"
    )


# ── Payload correctness ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_execute_stream_final_event_has_output():
    """PIPELINE_COMPLETED payload must be non-empty and contain status."""
    inp = PipelineInput(subject="test output", tradition="default", provider="mock")
    last_event = None
    async for event in execute_stream(FAST, inp):
        last_event = event

    assert last_event is not None
    assert last_event.payload, "PIPELINE_COMPLETED payload must not be empty"
    assert "status" in last_event.payload, "Payload must include 'status' key"


@pytest.mark.asyncio
async def test_execute_stream_final_payload_has_session_id():
    """PIPELINE_COMPLETED payload must include session_id (from PipelineOutput.to_dict)."""
    inp = PipelineInput(subject="session id check", tradition="default", provider="mock")
    last_event = None
    async for event in execute_stream(FAST, inp):
        last_event = event

    assert last_event is not None
    payload = last_event.payload
    # session_id comes from PipelineOutput.to_dict()
    assert "session_id" in payload, (
        f"Expected session_id in final payload, got keys: {list(payload.keys())}"
    )


@pytest.mark.asyncio
async def test_execute_stream_event_ordering():
    """Events must be ordered: STAGE_STARTED before STAGE_COMPLETED."""
    inp = PipelineInput(subject="ordering check", tradition="default", provider="mock")
    events = []
    async for event in execute_stream(FAST, inp):
        events.append(event)

    types = [e.event_type for e in events]
    started_idx = next(
        (i for i, t in enumerate(types) if t == EventType.STAGE_STARTED), None
    )
    completed_idx = next(
        (i for i, t in enumerate(types) if t == EventType.STAGE_COMPLETED), None
    )
    assert started_idx is not None, "No STAGE_STARTED event found"
    assert completed_idx is not None, "No STAGE_COMPLETED event found"
    assert started_idx < completed_idx, (
        "STAGE_STARTED must appear before STAGE_COMPLETED"
    )


# ── Stage field correctness ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_execute_stream_events_have_stage():
    """All STAGE_STARTED/STAGE_COMPLETED events must have a non-empty stage field."""
    inp = PipelineInput(subject="stage field", tradition="default", provider="mock")
    async for event in execute_stream(FAST, inp):
        if event.event_type in (EventType.STAGE_STARTED, EventType.STAGE_COMPLETED):
            assert event.stage, (
                f"Event {event.event_type} has empty stage field"
            )


# ── Consistency with execute() ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_execute_stream_status_matches_execute():
    """Status in PIPELINE_COMPLETED payload must match execute() status."""
    from vulca.pipeline.engine import execute

    inp = PipelineInput(subject="consistency check", tradition="default", provider="mock")

    # Run execute() to get ground truth
    direct_output = await execute(FAST, inp)

    # Run execute_stream() and extract final event payload
    last_event = None
    async for event in execute_stream(FAST, inp):
        last_event = event

    assert last_event is not None
    stream_status = last_event.payload.get("status")
    assert stream_status == direct_output.status, (
        f"Status mismatch: stream={stream_status}, execute={direct_output.status}"
    )


# ── Import surface ───────────────────────────────────────────────────────────

def test_execute_stream_importable_from_pipeline():
    """execute_stream must be importable from the vulca.pipeline package."""
    from vulca.pipeline import execute_stream as es  # noqa: F401
    assert callable(es)
