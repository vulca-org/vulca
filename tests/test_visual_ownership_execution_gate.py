from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
)
SCRIPT = ROOT / "scripts" / "visual_ownership_execution_gate.py"


def _plan(
    case_id: str,
    *,
    source_context_available: bool = True,
    planner_steps: list[str] | None = None,
    required_inputs: list[str] | None = None,
) -> dict:
    return {
        "schema_version": 1,
        "case_type": "learning_visual_ownership_plan",
        "planner_name": "visual_ownership_planner_v1",
        "example_id": f"tiny_{case_id}",
        "case_id": case_id,
        "source_case_type": "redraw_case",
        "recommended_action": "fallback_to_agent",
        "failure_hint": "under_split",
        "visual_ownership_kind": "under_split",
        "recommended_workflow": "redraw_under_split_boundary_replan",
        "required_inputs": required_inputs
        if required_inputs is not None
        else [
            "source_image",
            "current_mask_or_layer_bounds",
            "target_region_description",
        ],
        "planner_steps": planner_steps
        if planner_steps is not None
        else [
            "inspect_under_split_boundaries",
            "propose_additional_layer_or_mask_splits",
            "verify_target_region_isolation",
        ],
        "source_context_available": source_context_available,
        "source_context_signal_count": 1 if source_context_available else 0,
        "source_dependency": "required",
        "decision_basis": "image_source",
        "routing": {
            "next_owner": "visual_ownership_agent",
            "production_runtime_ready": False,
            "requires_visual_agent_judgement": True,
        },
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def test_visual_ownership_execution_gate_marks_ready_and_blocked_plans(tmp_path):
    from vulca.learning.visual_ownership_execution_gate import (
        run_visual_ownership_execution_gate,
    )

    plan_path = tmp_path / "visual_ownership_plans.jsonl"
    gate_path = tmp_path / "visual_ownership_execution_gate.jsonl"
    report_path = tmp_path / "visual_ownership_execution_gate_report.json"
    _write_jsonl(
        plan_path,
        [
            _plan("ready_under_split"),
            _plan("missing_source_context", source_context_available=False),
            _plan("incomplete_steps", planner_steps=[]),
        ],
    )

    report = run_visual_ownership_execution_gate(
        plan_path=plan_path,
        gate_path=gate_path,
        report_path=report_path,
    )

    assert report["case_type"] == "learning_visual_ownership_execution_gate_report"
    assert report["status"] == "blocked_visual_ownership_execution"
    assert report["summary"] == {
        "plan_count": 3,
        "agent_execution_ready_count": 1,
        "blocked_count": 2,
        "production_runtime_ready_count": 0,
        "source_context_gap_count": 1,
        "incomplete_plan_count": 1,
    }
    assert report["counts_by_gate_status"] == {
        "blocked_incomplete_plan": 1,
        "blocked_missing_source_context": 1,
        "ready_for_agent_execution": 1,
    }
    assert report["safe_handling"] == {
        "copies_local_paths": False,
        "copies_private_refs": False,
        "copies_raw_source_text": False,
        "calls_model_provider": False,
    }

    gate_records = [
        json.loads(line)
        for line in gate_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_case = {record["case_id"]: record for record in gate_records}

    ready = by_case["ready_under_split"]
    assert ready["case_type"] == "learning_visual_ownership_execution_gate"
    assert ready["gate_status"] == "ready_for_agent_execution"
    assert ready["gate_reasons"] == []
    assert ready["readiness"] == {
        "agent_execution_ready": True,
        "production_runtime_ready": False,
        "required_input_count": 3,
        "planner_step_count": 3,
        "source_context_available": True,
    }
    assert ready["routing"] == {
        "next_owner": "visual_ownership_agent",
        "requires_runtime_adapter": True,
    }

    missing_source = by_case["missing_source_context"]
    assert missing_source["gate_status"] == "blocked_missing_source_context"
    assert missing_source["gate_reasons"] == ["source_context_unavailable"]
    assert missing_source["routing"]["next_owner"] == "source_context_recovery"

    incomplete = by_case["incomplete_steps"]
    assert incomplete["gate_status"] == "blocked_incomplete_plan"
    assert incomplete["gate_reasons"] == ["planner_steps_missing"]
    assert incomplete["routing"]["next_owner"] == "visual_ownership_planner"
    assert report_path.exists()


def test_visual_ownership_execution_gate_cli_writes_summary(tmp_path):
    plan_path = tmp_path / "visual_ownership_plans.jsonl"
    gate_path = tmp_path / "visual_ownership_execution_gate.jsonl"
    report_path = tmp_path / "visual_ownership_execution_gate_report.json"
    _write_jsonl(plan_path, [_plan("ready_under_split")])

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--plans",
            str(plan_path),
            "--gates",
            str(gate_path),
            "--report",
            str(report_path),
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Visual ownership execution gate report:" in result.stdout
    assert "Plans: 1" in result.stdout
    assert "Agent execution ready: 1" in result.stdout
    assert "Blocked: 0" in result.stdout
    assert "Production runtime ready: 0" in result.stdout
    assert gate_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["agent_execution_ready_count"] == 1
