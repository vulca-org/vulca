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
SCRIPT = ROOT / "scripts" / "visual_ownership_runtime_replay.py"


def _request(
    case_id: str,
    *,
    runtime_target: str,
    runtime_action: str,
    required_runtime_inputs: list[str],
    provider_calls_enabled: bool = False,
) -> dict:
    return {
        "schema_version": 1,
        "case_type": "learning_visual_ownership_runtime_request",
        "adapter_name": "visual_ownership_runtime_adapter_v1",
        "example_id": f"tiny_{case_id}",
        "case_id": case_id,
        "source_case_type": "decompose_case"
        if runtime_target == "layers_decompose"
        else "redraw_case",
        "visual_ownership_kind": "occlusion"
        if runtime_target == "layers_decompose"
        else "under_split",
        "recommended_workflow": "decompose_occlusion_replan"
        if runtime_target == "layers_decompose"
        else "redraw_under_split_boundary_replan",
        "runtime_target": runtime_target,
        "runtime_action": runtime_action,
        "required_runtime_inputs": required_runtime_inputs,
        "gate_status": "ready_for_agent_execution",
        "source_context_available": True,
        "handoff": {
            "from_owner": "visual_ownership_agent",
            "to_runtime_target": runtime_target,
            "requires_runtime_adapter": True,
        },
        "execution_policy": {
            "provider_calls_enabled": provider_calls_enabled,
            "requires_visual_agent_judgement": True,
            "requires_runtime_adapter_review": True,
        },
    }


def _fixture_requests() -> list[dict]:
    return [
        _request(
            "taxonomy_v1_decompose_occlusion_holdout",
            runtime_target="layers_decompose",
            runtime_action="replan_decompose_layers",
            required_runtime_inputs=[
                "source_image",
                "current_layer_manifest",
                "layer_order_or_occlusion_notes",
            ],
        ),
        _request(
            "taxonomy_v1_redraw_under_split_holdout",
            runtime_target="layers_redraw",
            runtime_action="replan_redraw_boundary",
            required_runtime_inputs=[
                "source_image",
                "current_mask_or_layer_bounds",
                "target_region_description",
            ],
        ),
        _request(
            "blocked_unknown_runtime",
            runtime_target="unsupported_runtime",
            runtime_action="manual_visual_review",
            required_runtime_inputs=["source_image"],
        ),
    ]


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def test_visual_ownership_runtime_replay_records_dry_run_readiness(tmp_path):
    from vulca.learning.visual_ownership_runtime_replay import (
        run_visual_ownership_runtime_replay,
    )

    request_path = tmp_path / "visual_ownership_runtime_requests.jsonl"
    replay_path = tmp_path / "visual_ownership_runtime_replay.jsonl"
    report_path = tmp_path / "visual_ownership_runtime_replay_report.json"
    _write_jsonl(request_path, _fixture_requests())

    report = run_visual_ownership_runtime_replay(
        request_path=request_path,
        replay_path=replay_path,
        report_path=report_path,
    )

    assert report["case_type"] == "learning_visual_ownership_runtime_replay_report"
    assert report["status"] == "blocked_runtime_replay"
    assert report["summary"] == {
        "request_count": 3,
        "replay_record_count": 3,
        "replayable_count": 2,
        "blocked_count": 1,
        "provider_call_count": 0,
    }
    assert report["counts_by_runtime_target"] == {
        "layers_decompose": 1,
        "layers_redraw": 1,
        "unsupported_runtime": 1,
    }
    assert report["counts_by_runtime_entrypoint"] == {
        "layers_redraw_dry_run": 1,
        "layers_split_dry_run": 1,
        "unknown": 1,
    }
    assert report["counts_by_replay_status"] == {
        "blocked_unknown_runtime_target": 1,
        "dry_run_replayable": 2,
    }
    assert report["safe_handling"] == {
        "copies_local_paths": False,
        "copies_private_refs": False,
        "copies_raw_source_text": False,
        "calls_model_provider": False,
    }

    records = [
        json.loads(line)
        for line in replay_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_case = {record["case_id"]: record for record in records}

    decompose = by_case["taxonomy_v1_decompose_occlusion_holdout"]
    assert decompose["case_type"] == "learning_visual_ownership_runtime_replay"
    assert decompose["runtime_target"] == "layers_decompose"
    assert decompose["runtime_action"] == "replan_decompose_layers"
    assert decompose["runtime_entrypoint"] == "layers_split_dry_run"
    assert decompose["replay_status"] == "dry_run_replayable"
    assert decompose["runtime_contract"] == {
        "runtime_target": "layers_decompose",
        "runtime_action": "replan_decompose_layers",
        "required_runtime_inputs": [
            "source_image",
            "current_layer_manifest",
            "layer_order_or_occlusion_notes",
        ],
        "provider_calls_enabled": False,
    }

    redraw = by_case["taxonomy_v1_redraw_under_split_holdout"]
    assert redraw["runtime_target"] == "layers_redraw"
    assert redraw["runtime_action"] == "replan_redraw_boundary"
    assert redraw["runtime_entrypoint"] == "layers_redraw_dry_run"
    assert redraw["replay_status"] == "dry_run_replayable"

    blocked = by_case["blocked_unknown_runtime"]
    assert blocked["runtime_entrypoint"] == "unknown"
    assert blocked["replay_status"] == "blocked_unknown_runtime_target"
    assert blocked["replay_reasons"] == ["unsupported_runtime_target"]
    assert report_path.exists()


def test_visual_ownership_runtime_replay_blocks_provider_enabled_requests(tmp_path):
    from vulca.learning.visual_ownership_runtime_replay import (
        run_visual_ownership_runtime_replay,
    )

    request_path = tmp_path / "visual_ownership_runtime_requests.jsonl"
    _write_jsonl(
        request_path,
        [
            _request(
                "provider_enabled_request",
                runtime_target="layers_redraw",
                runtime_action="replan_redraw_boundary",
                required_runtime_inputs=["source_image"],
                provider_calls_enabled=True,
            )
        ],
    )

    report = run_visual_ownership_runtime_replay(request_path=request_path)

    record = report["runtime_replays"][0]
    assert record["replay_status"] == "blocked_provider_call_policy"
    assert record["replay_reasons"] == ["provider_calls_enabled"]
    assert record["readiness"]["provider_call_count"] == 0
    assert report["summary"]["provider_call_count"] == 0


def test_visual_ownership_runtime_replay_cli_writes_summary(tmp_path):
    request_path = tmp_path / "visual_ownership_runtime_requests.jsonl"
    replay_path = tmp_path / "visual_ownership_runtime_replay.jsonl"
    report_path = tmp_path / "visual_ownership_runtime_replay_report.json"
    _write_jsonl(request_path, _fixture_requests())

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--requests",
            str(request_path),
            "--replay",
            str(replay_path),
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
    assert "Visual ownership runtime replay report:" in result.stdout
    assert "Visual ownership runtime replay:" in result.stdout
    assert "Requests: 3" in result.stdout
    assert "Replayable: 2" in result.stdout
    assert "Blocked: 1" in result.stdout
    assert "Provider calls: 0" in result.stdout
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["replayable_count"] == 2
