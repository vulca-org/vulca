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
SCRIPT = ROOT / "scripts" / "visual_ownership_runtime_entrypoint_dry_run.py"


def _replay(
    case_id: str,
    *,
    runtime_target: str,
    runtime_action: str,
    runtime_entrypoint: str,
    replay_status: str = "dry_run_replayable",
    required_runtime_inputs: list[str] | None = None,
    provider_calls_enabled: bool = False,
) -> dict:
    inputs = required_runtime_inputs or ["source_image"]
    return {
        "schema_version": 1,
        "case_type": "learning_visual_ownership_runtime_replay",
        "replay_name": "visual_ownership_runtime_replay_v1",
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
        "runtime_entrypoint": runtime_entrypoint,
        "replay_status": replay_status,
        "replay_reasons": []
        if replay_status == "dry_run_replayable"
        else ["fixture_blocked"],
        "runtime_contract": {
            "runtime_target": runtime_target,
            "runtime_action": runtime_action,
            "required_runtime_inputs": inputs,
            "provider_calls_enabled": provider_calls_enabled,
        },
        "readiness": {
            "dry_run_replayable": replay_status == "dry_run_replayable",
            "required_runtime_input_count": len(inputs),
            "provider_call_count": 0,
        },
    }


def _fixture_replays() -> list[dict]:
    return [
        _replay(
            "taxonomy_v1_decompose_occlusion_holdout",
            runtime_target="layers_decompose",
            runtime_action="replan_decompose_layers",
            runtime_entrypoint="layers_split_dry_run",
            required_runtime_inputs=[
                "source_image",
                "current_layer_manifest",
                "layer_order_or_occlusion_notes",
            ],
        ),
        _replay(
            "taxonomy_v1_redraw_under_split_holdout",
            runtime_target="layers_redraw",
            runtime_action="replan_redraw_boundary",
            runtime_entrypoint="layers_redraw_dry_run",
            required_runtime_inputs=[
                "source_image",
                "current_mask_or_layer_bounds",
                "target_region_description",
            ],
        ),
        _replay(
            "blocked_previous_replay",
            runtime_target="layers_redraw",
            runtime_action="replan_redraw_boundary",
            runtime_entrypoint="layers_redraw_dry_run",
            replay_status="blocked_missing_runtime_inputs",
            required_runtime_inputs=[],
        ),
    ]


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def test_visual_ownership_runtime_entrypoint_dry_run_builds_invocations(tmp_path):
    from vulca.learning.visual_ownership_runtime_entrypoint_dry_run import (
        run_visual_ownership_runtime_entrypoint_dry_run,
    )

    replay_path = tmp_path / "visual_ownership_runtime_replay.jsonl"
    invocation_path = (
        tmp_path / "visual_ownership_runtime_entrypoint_dry_run.jsonl"
    )
    report_path = tmp_path / "visual_ownership_runtime_entrypoint_dry_run_report.json"
    _write_jsonl(replay_path, _fixture_replays())

    report = run_visual_ownership_runtime_entrypoint_dry_run(
        replay_path=replay_path,
        invocation_path=invocation_path,
        report_path=report_path,
    )

    assert (
        report["case_type"]
        == "learning_visual_ownership_runtime_entrypoint_dry_run_report"
    )
    assert report["status"] == "blocked_runtime_entrypoint_dry_run"
    assert report["summary"] == {
        "replay_record_count": 3,
        "dry_run_invocation_count": 3,
        "ready_count": 2,
        "blocked_count": 1,
        "provider_call_count": 0,
    }
    assert report["counts_by_runtime_tool"] == {
        "layers_redraw": 2,
        "layers_split": 1,
    }
    assert report["counts_by_dry_run_status"] == {
        "blocked_previous_replay_status": 1,
        "dry_run_invocation_ready": 2,
    }
    assert report["safe_handling"] == {
        "copies_local_paths": False,
        "copies_private_refs": False,
        "copies_raw_source_text": False,
        "calls_model_provider": False,
    }

    invocations = [
        json.loads(line)
        for line in invocation_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_case = {record["case_id"]: record for record in invocations}

    decompose = by_case["taxonomy_v1_decompose_occlusion_holdout"]
    assert (
        decompose["case_type"]
        == "learning_visual_ownership_runtime_entrypoint_dry_run"
    )
    assert decompose["runtime_tool"] == "layers_split"
    assert decompose["runtime_interface"] == "mcp"
    assert decompose["dry_run_status"] == "dry_run_invocation_ready"
    assert decompose["entrypoint_contract"]["argument_contract"] == {
        "case_log_path": "{optional_case_log_path}",
        "image_path": "{source_image}",
        "mode": "orchestrated",
        "output_dir": "{runtime_output_dir}",
        "plan": "{visual_ownership_replan_json}",
        "provider": "dry_run",
        "tradition": "{tradition}",
    }
    assert decompose["readiness"]["provider_call_count"] == 0

    redraw = by_case["taxonomy_v1_redraw_under_split_holdout"]
    assert redraw["runtime_tool"] == "layers_redraw"
    assert redraw["runtime_interface"] == "mcp"
    assert redraw["dry_run_status"] == "dry_run_invocation_ready"
    assert redraw["entrypoint_contract"]["argument_contract"] == {
        "artwork_dir": "{current_layer_manifest_dir}",
        "case_log_path": "{optional_case_log_path}",
        "instruction": "{visual_ownership_redraw_instruction}",
        "layer": "{target_layer_name}",
        "provider": "dry_run",
        "route": "auto",
        "tradition": "{tradition}",
    }

    blocked = by_case["blocked_previous_replay"]
    assert blocked["runtime_tool"] == "layers_redraw"
    assert blocked["dry_run_status"] == "blocked_previous_replay_status"
    assert blocked["dry_run_reasons"] == ["previous_replay_not_replayable"]
    assert report_path.exists()


def test_visual_ownership_runtime_entrypoint_dry_run_blocks_provider_contract(
    tmp_path,
):
    from vulca.learning.visual_ownership_runtime_entrypoint_dry_run import (
        run_visual_ownership_runtime_entrypoint_dry_run,
    )

    replay_path = tmp_path / "visual_ownership_runtime_replay.jsonl"
    _write_jsonl(
        replay_path,
        [
            _replay(
                "provider_enabled_contract",
                runtime_target="layers_redraw",
                runtime_action="replan_redraw_boundary",
                runtime_entrypoint="layers_redraw_dry_run",
                provider_calls_enabled=True,
            )
        ],
    )

    report = run_visual_ownership_runtime_entrypoint_dry_run(
        replay_path=replay_path,
    )

    record = report["runtime_entrypoint_dry_runs"][0]
    assert record["dry_run_status"] == "blocked_provider_call_policy"
    assert record["dry_run_reasons"] == ["provider_calls_enabled"]
    assert record["readiness"]["provider_call_count"] == 0
    assert report["summary"]["provider_call_count"] == 0


def test_visual_ownership_runtime_entrypoint_dry_run_cli_writes_summary(tmp_path):
    replay_path = tmp_path / "visual_ownership_runtime_replay.jsonl"
    invocation_path = (
        tmp_path / "visual_ownership_runtime_entrypoint_dry_run.jsonl"
    )
    report_path = tmp_path / "visual_ownership_runtime_entrypoint_dry_run_report.json"
    _write_jsonl(replay_path, _fixture_replays())

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--replay",
            str(replay_path),
            "--invocations",
            str(invocation_path),
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
    assert "Visual ownership runtime entrypoint dry-run report:" in result.stdout
    assert "Visual ownership runtime entrypoint dry-runs:" in result.stdout
    assert "Replay records: 3" in result.stdout
    assert "Ready: 2" in result.stdout
    assert "Blocked: 1" in result.stdout
    assert "Provider calls: 0" in result.stdout
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["ready_count"] == 2
