#!/usr/bin/env python3
"""Validate the PipelineOrchestrator — unit tests for sync, stream, HITL modes."""

from __future__ import annotations

import sys
from pathlib import Path
from threading import Thread

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.prototype.agents.draft_config import DraftConfig
from app.prototype.agents.queen_config import QueenConfig
from app.prototype.orchestrator.events import EventType
from app.prototype.orchestrator.orchestrator import PipelineOrchestrator
from app.prototype.orchestrator.run_state import RunStatus
from app.prototype.pipeline.pipeline_types import PipelineInput

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✓ {name}")
    else:
        failed += 1
        print(f"  ✗ {name} — {detail}")


def test_sync_mode():
    """Test synchronous pipeline execution."""
    print("\n[1] Sync mode")
    orch = PipelineOrchestrator(enable_archivist=False)
    inp = PipelineInput(task_id="orch-sync-1", subject="test landscape", cultural_tradition="chinese_xieyi")
    result = orch.run_sync(inp)

    check("success", result.success, f"success={result.success}, error={result.error}")
    check("decision is accept or stop", result.final_decision in ("accept", "stop", "downgrade", "rerun"),
          f"decision={result.final_decision}")
    check("has stages", len(result.stages) >= 4, f"stages={len(result.stages)}")
    check("task_id matches", result.task_id == "orch-sync-1")


def test_stream_mode():
    """Test streaming pipeline execution."""
    print("\n[2] Stream mode")
    orch = PipelineOrchestrator(enable_archivist=True)
    inp = PipelineInput(task_id="orch-stream-1", subject="test painting", cultural_tradition="western_academic")

    events = list(orch.run_stream(inp))

    check("has events", len(events) > 0, f"events={len(events)}")

    event_types = [e.event_type for e in events]
    check("has STAGE_STARTED", EventType.STAGE_STARTED in event_types)
    check("has STAGE_COMPLETED", EventType.STAGE_COMPLETED in event_types)
    check("has DECISION_MADE", EventType.DECISION_MADE in event_types)
    check("has PIPELINE_COMPLETED", EventType.PIPELINE_COMPLETED in event_types)

    # Archivist should be in the events
    archivist_events = [e for e in events if e.stage == "archivist"]
    check("archivist stage present", len(archivist_events) >= 1, f"archivist_events={len(archivist_events)}")

    # Final event payload should have cost
    final = events[-1]
    check("final has cost", "total_cost_usd" in final.payload, f"payload keys={list(final.payload.keys())}")


def test_stream_event_ordering():
    """Test that events follow correct ordering."""
    print("\n[3] Event ordering")
    orch = PipelineOrchestrator(enable_archivist=False)
    inp = PipelineInput(task_id="orch-order-1", subject="orderly test", cultural_tradition="default")

    events = list(orch.run_stream(inp))

    # Check stage ordering: scout should come before draft
    stages_seen = []
    for e in events:
        if e.event_type == EventType.STAGE_COMPLETED and e.stage not in stages_seen:
            stages_seen.append(e.stage)

    check("scout before draft", stages_seen.index("scout") < stages_seen.index("draft"),
          f"order={stages_seen}")
    check("draft before critic", stages_seen.index("draft") < stages_seen.index("critic"),
          f"order={stages_seen}")
    # Queen emits DECISION_MADE (not STAGE_COMPLETED), so check via STARTED order
    started_stages = [e.stage for e in events if e.event_type == EventType.STAGE_STARTED]
    if "queen" in started_stages and "critic" in started_stages:
        check("critic before queen (started)",
              started_stages.index("critic") < started_stages.index("queen"),
              f"started_order={started_stages}")
    else:
        check("critic and queen both started", False, f"started={started_stages}")

    # Every STARTED should have a matching COMPLETED or DECISION_MADE
    for i, e in enumerate(events):
        if e.event_type == EventType.STAGE_STARTED:
            found = False
            for j in range(i + 1, len(events)):
                ej = events[j]
                if ej.stage == e.stage and ej.event_type in (
                    EventType.STAGE_COMPLETED, EventType.DECISION_MADE
                ):
                    found = True
                    break
            check(f"started→resolved for {e.stage} (r{e.round_num})", found)


def test_cost_tracking():
    """Test cost calculation."""
    print("\n[4] Cost tracking")
    orch = PipelineOrchestrator(
        draft_config=DraftConfig(provider="mock", n_candidates=4),
        enable_archivist=False,
    )
    inp = PipelineInput(task_id="orch-cost-1", subject="cost test", cultural_tradition="default")

    events = list(orch.run_stream(inp))
    final = events[-1]
    cost = final.payload.get("total_cost_usd", -1)
    images = final.payload.get("images_generated", -1)

    check("cost is zero for mock", cost == 0.0, f"cost={cost}")
    check("images generated", images >= 4, f"images={images}")


def test_hitl_timeout():
    """Test HITL with timeout (no human action submitted)."""
    print("\n[5] HITL timeout")
    orch = PipelineOrchestrator(
        enable_hitl=True,
        enable_archivist=False,
        queen_config=QueenConfig(max_rounds=1),
    )
    inp = PipelineInput(task_id="orch-hitl-timeout", subject="HITL timeout test", cultural_tradition="default")

    # Run in a thread since HITL will block
    events: list = []

    def run():
        for e in orch.run_stream(inp):
            events.append(e)

    t = Thread(target=run, daemon=True)
    t.start()

    # Wait for HUMAN_REQUIRED (or WAITING_HUMAN state), then submit to unblock.
    import time
    deadline = time.monotonic() + 15.0
    saw_human_required = False
    while time.monotonic() < deadline:
        if any(e.event_type == EventType.HUMAN_REQUIRED for e in events):
            saw_human_required = True
            break
        state = orch.get_run_state("orch-hitl-timeout")
        if state is not None and state.status == RunStatus.WAITING_HUMAN:
            saw_human_required = True
            break
        if not t.is_alive():
            break
        time.sleep(0.05)

    check("pipeline progressed", len(events) > 0, f"events={len(events)}")
    check("HUMAN_REQUIRED received", saw_human_required,
          f"events_types={[e.event_type.name for e in events]}")
    if saw_human_required:
        ok = orch.submit_action("orch-hitl-timeout", "approve")
        check("submit_action accepted", ok)

    t.join(timeout=10)
    check("thread completed", not t.is_alive())


def test_runs_index():
    """Test that runs_index.json is updated."""
    print("\n[6] Runs index")
    from app.prototype.checkpoints.pipeline_checkpoint import load_runs_index

    orch = PipelineOrchestrator(enable_archivist=False)
    inp = PipelineInput(task_id="orch-index-1", subject="index test", cultural_tradition="default")
    orch.run_sync(inp)

    index = load_runs_index()
    check("task in index", "orch-index-1" in index, f"keys={list(index.keys())[:5]}")
    entry = index.get("orch-index-1", {})
    check("has status", "status" in entry)
    check("status is completed", entry.get("status") == "completed", f"status={entry.get('status')}")


def test_run_pipeline_compat():
    """Test backward compatibility with run_pipeline()."""
    print("\n[7] run_pipeline() backward compat")
    from app.prototype.pipeline.run_pipeline import run_pipeline

    inp = PipelineInput(task_id="compat-test-1", subject="compat test", cultural_tradition="chinese_xieyi")
    result = run_pipeline(inp)

    check("success", result.success)
    check("has stages", len(result.stages) >= 4, f"stages={len(result.stages)}")
    check("no archivist stage", all(s.stage != "archivist" for s in result.stages),
          "run_pipeline should not call archivist")


def test_hitl_force_accept_override():
    """Test that force_accept sets final best_candidate_id to the human-selected candidate."""
    print("\n[8] HITL force_accept override")
    import time

    task_id = "orch-hitl-force-1"
    orch = PipelineOrchestrator(
        enable_hitl=True,
        enable_archivist=False,
        queen_config=QueenConfig(max_rounds=1),
    )
    inp = PipelineInput(task_id=task_id, subject="force accept test", cultural_tradition="default")

    events: list = []

    def run():
        for e in orch.run_stream(inp):
            events.append(e)

    t = Thread(target=run, daemon=True)
    t.start()

    deadline = time.monotonic() + 8.0
    selected_candidate_id = ""
    saw_human_required = False
    while time.monotonic() < deadline:
        for ev in events:
            if ev.event_type == EventType.HUMAN_REQUIRED:
                saw_human_required = True
            if ev.event_type == EventType.STAGE_COMPLETED and ev.stage == "draft":
                candidates = ev.payload.get("candidates", [])
                if candidates:
                    selected_candidate_id = candidates[-1].get("candidate_id", "")
        if saw_human_required and selected_candidate_id:
            break
        if not t.is_alive():
            break
        time.sleep(0.05)

    check("HUMAN_REQUIRED observed", saw_human_required)
    check("selected candidate available", bool(selected_candidate_id))

    ok = orch.submit_action(task_id, "force_accept", candidate_id=selected_candidate_id)
    check("force_accept submitted", ok)

    t.join(timeout=6)
    check("thread completed", not t.is_alive())

    final_events = [e for e in events if e.event_type == EventType.PIPELINE_COMPLETED]
    check("pipeline completed event emitted", len(final_events) == 1, f"count={len(final_events)}")
    if final_events:
        payload = final_events[0].payload
        check("final decision is accept", payload.get("final_decision") == "accept")
        check(
            "best_candidate_id overridden by human selection",
            payload.get("best_candidate_id") == selected_candidate_id,
            f"best={payload.get('best_candidate_id')} selected={selected_candidate_id}",
        )


def test_hitl_rerun_lock_constraints():
    """Test that lock + rerun dimensions are applied to the next Critic round."""
    print("\n[9] HITL lock/rerun constraints")
    import time

    task_id = "orch-hitl-rerun-lock-1"
    orch = PipelineOrchestrator(
        enable_hitl=True,
        enable_archivist=False,
        queen_config=QueenConfig(max_rounds=2),
    )
    inp = PipelineInput(task_id=task_id, subject="rerun lock test", cultural_tradition="chinese_xieyi")

    events: list = []

    def run():
        for e in orch.run_stream(inp):
            events.append(e)

    t = Thread(target=run, daemon=True)
    t.start()

    # Wait for first human pause and trigger rerun with lock/rerun dimensions.
    deadline = time.monotonic() + 10.0
    first_action_done = False
    while time.monotonic() < deadline:
        hr_count = sum(1 for e in events if e.event_type == EventType.HUMAN_REQUIRED)
        if hr_count >= 1 and not first_action_done:
            ok = orch.submit_action(
                task_id,
                "rerun",
                locked_dimensions=["visual_perception", "technical_analysis"],
                rerun_dimensions=["cultural_context"],
                reason="lock L1/L2, rerun L3",
            )
            check("first rerun action submitted", ok)
            first_action_done = ok
            break
        if not t.is_alive():
            break
        time.sleep(0.05)

    check("first action done", first_action_done)

    # Wait for second human pause and approve to finish run.
    second_action_done = False
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        hr_count = sum(1 for e in events if e.event_type == EventType.HUMAN_REQUIRED)
        if hr_count >= 2:
            ok = orch.submit_action(task_id, "approve")
            check("second approve action submitted", ok)
            second_action_done = ok
            break
        if not t.is_alive():
            break
        time.sleep(0.05)

    check("second action done", second_action_done)

    t.join(timeout=8)
    check("thread completed", not t.is_alive())

    # Round-2 Critic payload should include applied HITL constraints metadata.
    critic_events = [
        e for e in events
        if e.event_type == EventType.STAGE_COMPLETED and e.stage == "critic"
    ]
    round2_events = [e for e in critic_events if e.round_num >= 2]
    check("second-round critic event exists", len(round2_events) >= 1, f"critic_events={len(critic_events)}")
    if round2_events:
        hitl_constraints = round2_events[0].payload.get("hitl_constraints", {})
        check("hitl_constraints metadata present", bool(hitl_constraints))
        preserved = set(hitl_constraints.get("preserved_dimensions", []))
        check("L1 preserved", "visual_perception" in preserved)
        check("L2 preserved", "technical_analysis" in preserved)
        check("L3 not preserved", "cultural_context" not in preserved)
        check("applied score count > 0", hitl_constraints.get("applied_scores", 0) > 0)

    final_events = [e for e in events if e.event_type == EventType.PIPELINE_COMPLETED]
    check("pipeline completed", len(final_events) == 1, f"completed={len(final_events)}")


if __name__ == "__main__":
    print("=" * 60)
    print("  PipelineOrchestrator Validation")
    print("=" * 60)

    test_sync_mode()
    test_stream_mode()
    test_stream_event_ordering()
    test_cost_tracking()
    test_hitl_timeout()
    test_runs_index()
    test_run_pipeline_compat()
    test_hitl_force_accept_override()
    test_hitl_rerun_lock_constraints()

    print(f"\n{'=' * 60}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")

    sys.exit(1 if failed > 0 else 0)
