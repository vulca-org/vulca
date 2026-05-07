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
SCRIPT = ROOT / "scripts" / "visual_ownership_planner.py"


def _decision(
    case_id: str,
    *,
    case_type: str,
    failure_hint: str,
    visual_ownership_kind: str,
) -> dict:
    return {
        "schema_version": 1,
        "case_type": "learning_dry_run_decision",
        "example_id": f"tiny_{case_id}",
        "case_id": case_id,
        "source_case_type": case_type,
        "split": "test",
        "action_router": {
            "policy_name": "tiny_action_model_v1",
            "recommended_action": "fallback_to_agent",
            "confidence": 0.86,
            "failure_hint": failure_hint,
            "rule_reason": "fixture",
            "target_action": "fallback_to_agent",
        },
        "source_dependency_router": {
            "policy_name": "source_dependency_rule_v1",
            "recommended_source_dependency": "required",
            "recommended_decision_basis": "image_source",
            "confidence": 0.8,
            "rule_reason": "fixture",
            "target_source_dependency": "required",
            "target_decision_basis": "image_source",
        },
        "source_context": {
            "available": True,
            "source": "auxiliary_signal",
            "signal_count": 1,
        },
        "dispatch": {
            "decision_owner": "visual_ownership_planner",
            "execution_owner": "visual_ownership_planner",
            "fallback_agent": False,
            "runtime_recovery": False,
            "runtime_recovery_kind": "",
            "visual_ownership_planner": True,
            "visual_ownership_kind": visual_ownership_kind,
            "fallback_reasons": [],
            "data_gap_tags": [],
            "confidence_calibration": "",
        },
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def _fixture_decisions() -> list[dict]:
    return [
        _decision(
            "taxonomy_v1_decompose_occlusion_holdout",
            case_type="decompose_case",
            failure_hint="occlusion",
            visual_ownership_kind="occlusion",
        ),
        _decision(
            "taxonomy_v1_redraw_under_split_holdout",
            case_type="redraw_case",
            failure_hint="under_split",
            visual_ownership_kind="under_split",
        ),
        _decision(
            "resolved_mask_leak",
            case_type="redraw_case",
            failure_hint="mask_leak",
            visual_ownership_kind="",
        )
        | {
            "dispatch": {
                "decision_owner": "tiny_model",
                "execution_owner": "tiny_model",
                "fallback_agent": False,
                "visual_ownership_planner": False,
            }
        },
    ]


def test_visual_ownership_planner_builds_structured_plans(tmp_path):
    from vulca.learning.visual_ownership_planner import run_visual_ownership_planner

    decision_path = tmp_path / "dry_run_decisions.jsonl"
    plan_path = tmp_path / "visual_ownership_plans.jsonl"
    report_path = tmp_path / "visual_ownership_planner_report.json"
    _write_jsonl(decision_path, _fixture_decisions())

    report = run_visual_ownership_planner(
        decision_path=decision_path,
        plan_path=plan_path,
        report_path=report_path,
    )

    assert report["case_type"] == "learning_visual_ownership_planner_report"
    assert report["status"] == "planned_visual_ownership_work"
    assert report["summary"] == {
        "decision_count": 3,
        "visual_ownership_decision_count": 2,
        "plan_count": 2,
        "source_context_gap_count": 0,
    }
    assert report["counts_by_visual_ownership_kind"] == {
        "occlusion": 1,
        "under_split": 1,
    }
    assert report["counts_by_recommended_workflow"] == {
        "decompose_occlusion_replan": 1,
        "redraw_under_split_boundary_replan": 1,
    }
    assert report["safe_handling"] == {
        "copies_local_paths": False,
        "copies_private_refs": False,
        "copies_raw_source_text": False,
        "calls_model_provider": False,
    }

    plans = [
        json.loads(line)
        for line in plan_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert [plan["case_id"] for plan in plans] == [
        "taxonomy_v1_decompose_occlusion_holdout",
        "taxonomy_v1_redraw_under_split_holdout",
    ]
    by_case = {plan["case_id"]: plan for plan in plans}

    occlusion = by_case["taxonomy_v1_decompose_occlusion_holdout"]
    assert occlusion["case_type"] == "learning_visual_ownership_plan"
    assert occlusion["recommended_workflow"] == "decompose_occlusion_replan"
    assert occlusion["required_inputs"] == [
        "source_image",
        "current_layer_manifest",
        "layer_order_or_occlusion_notes",
    ]
    assert occlusion["planner_steps"] == [
        "inspect_source_occlusion_relationships",
        "separate_occluder_and_occluded_regions",
        "verify_layer_order_and_mask_edges",
    ]
    assert occlusion["routing"]["next_owner"] == "visual_ownership_agent"
    assert occlusion["routing"]["production_runtime_ready"] is False

    under_split = by_case["taxonomy_v1_redraw_under_split_holdout"]
    assert under_split["recommended_workflow"] == "redraw_under_split_boundary_replan"
    assert under_split["required_inputs"] == [
        "source_image",
        "current_mask_or_layer_bounds",
        "target_region_description",
    ]
    assert under_split["planner_steps"] == [
        "inspect_under_split_boundaries",
        "propose_additional_layer_or_mask_splits",
        "verify_target_region_isolation",
    ]
    assert under_split["routing"]["next_owner"] == "visual_ownership_agent"
    assert report_path.exists()


def test_visual_ownership_planner_cli_writes_plan_and_summary(tmp_path):
    decision_path = tmp_path / "dry_run_decisions.jsonl"
    plan_path = tmp_path / "visual_ownership_plans.jsonl"
    report_path = tmp_path / "visual_ownership_planner_report.json"
    _write_jsonl(decision_path, _fixture_decisions())

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--decision-path",
            str(decision_path),
            "--plans",
            str(plan_path),
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
    assert "Visual ownership planner report:" in result.stdout
    assert "Visual ownership decisions: 2" in result.stdout
    assert "Plans: 2" in result.stdout
    assert "Source-context gaps: 0" in result.stdout
    assert plan_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["plan_count"] == 2
