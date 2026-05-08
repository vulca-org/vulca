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
SCRIPT = ROOT / "scripts" / "visual_ownership_runtime_adapter.py"


def _gate(
    case_id: str,
    *,
    source_case_type: str,
    visual_ownership_kind: str,
    recommended_workflow: str,
    gate_status: str = "ready_for_agent_execution",
) -> dict:
    return {
        "schema_version": 1,
        "case_type": "learning_visual_ownership_execution_gate",
        "example_id": f"tiny_{case_id}",
        "case_id": case_id,
        "source_case_type": source_case_type,
        "visual_ownership_kind": visual_ownership_kind,
        "recommended_workflow": recommended_workflow,
        "gate_status": gate_status,
        "gate_reasons": [] if gate_status == "ready_for_agent_execution" else ["fixture_blocked"],
        "readiness": {
            "agent_execution_ready": gate_status == "ready_for_agent_execution",
            "production_runtime_ready": False,
            "required_input_count": 3,
            "planner_step_count": 3,
            "source_context_available": True,
        },
        "routing": {
            "next_owner": "visual_ownership_agent",
            "requires_runtime_adapter": True,
        },
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def _fixture_gates() -> list[dict]:
    return [
        _gate(
            "taxonomy_v1_decompose_occlusion_holdout",
            source_case_type="decompose_case",
            visual_ownership_kind="occlusion",
            recommended_workflow="decompose_occlusion_replan",
        ),
        _gate(
            "taxonomy_v1_redraw_under_split_holdout",
            source_case_type="redraw_case",
            visual_ownership_kind="under_split",
            recommended_workflow="redraw_under_split_boundary_replan",
        ),
        _gate(
            "blocked_missing_source_context",
            source_case_type="redraw_case",
            visual_ownership_kind="under_split",
            recommended_workflow="redraw_under_split_boundary_replan",
            gate_status="blocked_missing_source_context",
        ),
    ]


def test_visual_ownership_runtime_adapter_builds_runtime_requests(tmp_path):
    from vulca.learning.visual_ownership_runtime_adapter import (
        run_visual_ownership_runtime_adapter,
    )

    gate_path = tmp_path / "visual_ownership_execution_gate.jsonl"
    request_path = tmp_path / "visual_ownership_runtime_requests.jsonl"
    report_path = tmp_path / "visual_ownership_runtime_adapter_report.json"
    _write_jsonl(gate_path, _fixture_gates())

    report = run_visual_ownership_runtime_adapter(
        gate_path=gate_path,
        request_path=request_path,
        report_path=report_path,
    )

    assert report["case_type"] == "learning_visual_ownership_runtime_adapter_report"
    assert report["status"] == "runtime_requests_ready_for_adapter_review"
    assert report["summary"] == {
        "gate_record_count": 3,
        "adapter_request_count": 2,
        "blocked_gate_count": 1,
        "production_runtime_candidate_count": 2,
        "provider_call_count": 0,
    }
    assert report["counts_by_runtime_target"] == {
        "layers_decompose": 1,
        "layers_redraw": 1,
    }
    assert report["safe_handling"] == {
        "copies_local_paths": False,
        "copies_private_refs": False,
        "copies_raw_source_text": False,
        "calls_model_provider": False,
    }

    requests = [
        json.loads(line)
        for line in request_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert [request["case_id"] for request in requests] == [
        "taxonomy_v1_decompose_occlusion_holdout",
        "taxonomy_v1_redraw_under_split_holdout",
    ]
    by_case = {request["case_id"]: request for request in requests}

    decompose = by_case["taxonomy_v1_decompose_occlusion_holdout"]
    assert decompose["case_type"] == "learning_visual_ownership_runtime_request"
    assert decompose["runtime_target"] == "layers_decompose"
    assert decompose["runtime_action"] == "replan_decompose_layers"
    assert decompose["required_runtime_inputs"] == [
        "source_image",
        "current_layer_manifest",
        "layer_order_or_occlusion_notes",
    ]
    assert decompose["execution_policy"] == {
        "provider_calls_enabled": False,
        "requires_visual_agent_judgement": True,
        "requires_runtime_adapter_review": True,
    }

    redraw = by_case["taxonomy_v1_redraw_under_split_holdout"]
    assert redraw["runtime_target"] == "layers_redraw"
    assert redraw["runtime_action"] == "replan_redraw_boundary"
    assert redraw["required_runtime_inputs"] == [
        "source_image",
        "current_mask_or_layer_bounds",
        "target_region_description",
    ]
    assert report_path.exists()


def test_visual_ownership_runtime_adapter_cli_writes_summary(tmp_path):
    gate_path = tmp_path / "visual_ownership_execution_gate.jsonl"
    request_path = tmp_path / "visual_ownership_runtime_requests.jsonl"
    report_path = tmp_path / "visual_ownership_runtime_adapter_report.json"
    _write_jsonl(gate_path, _fixture_gates())

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--gates",
            str(gate_path),
            "--requests",
            str(request_path),
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
    assert "Visual ownership runtime adapter report:" in result.stdout
    assert "Gate records: 3" in result.stdout
    assert "Adapter requests: 2" in result.stdout
    assert "Blocked gates: 1" in result.stdout
    assert "Provider calls: 0" in result.stdout
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["adapter_request_count"] == 2
