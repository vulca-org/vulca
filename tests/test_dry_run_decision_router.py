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


def _example(
    case_id: str,
    *,
    split: str,
    case_type: str = "layer_generate_case",
    failure_type: str = "style_drift",
    preferred_action: str = "adjust_prompt",
    source_dependency: str = "required",
    source_decision_basis: str = "artifact_source",
    source_context_available: bool = False,
    action_hint: str = "",
) -> dict:
    quality = {
        "gate_passed": not bool(failure_type),
        "failures": [failure_type] if failure_type else [],
    }
    case_record = {
        "case_type": case_type,
        "case_id": case_id,
        "quality": quality,
    }
    if action_hint:
        case_record["decisions"] = {
            "fallback_decisions": [{"suggested_action": action_hint}]
        }
    return {
        "schema_version": 1,
        "case_type": "learning_tiny_dataset_example",
        "example_id": f"example_{case_id}",
        "split": split,
        "source": {
            "kind": "user_case_log",
            "source_id": "unit_cases",
            "privacy_scope": "private",
            "curation_status": "reviewed",
        },
        "source_case": {
            "case_id": case_id,
            "case_type": case_type,
        },
        "input": {"case_record": case_record},
        "targets": {
            "failure_type": failure_type,
            "preferred_action": preferred_action,
            "source_dependency": source_dependency,
            "source_decision_basis": source_decision_basis,
        },
        "source_context": {
            "available": source_context_available,
            "source_artifact_available_count": 1 if source_context_available else 0,
            "source_image_available": source_context_available,
        },
    }


def _source_context_signal(example_id: str) -> dict:
    return {
        "signal_id": f"source_context_{example_id}",
        "model": {"id": "source_context_static_v1"},
        "signals": {
            "status": "completed",
            "signal_source": "source_context_static",
            "source_context_tags": ["source_artifact:present"],
            "source_image": {"available": False},
            "source_artifacts": {
                "available_count": 1,
                "artifact_kind_counts": {"file": 1},
            },
        },
        "training_use": {
            "approved_for_auxiliary_training": True,
            "review_status": "reviewed_promoted",
        },
    }


def test_dry_run_decisions_combine_action_source_dependency_and_dispatch():
    from vulca.learning.dry_run_decision_router import build_dry_run_decisions

    examples = [
        _example("train_style", split="train"),
        _example(
            "train_provider",
            split="train",
            failure_type="provider_failure",
            preferred_action="fallback_to_agent",
            source_dependency="not_needed",
            source_decision_basis="metadata_only",
            action_hint="fallback_to_agent",
        ),
        _example("test_style_missing_source", split="test"),
        _example(
            "test_provider_failure",
            split="test",
            failure_type="provider_failure",
            preferred_action="fallback_to_agent",
            source_dependency="not_needed",
            source_decision_basis="metadata_only",
            action_hint="fallback_to_agent",
        ),
        _example(
            "test_decompose_source_available",
            split="test",
            case_type="decompose_case",
            failure_type="under_segmentation",
            preferred_action="split_layer_further",
            source_dependency="required",
            source_decision_basis="image_source",
            source_context_available=True,
        ),
    ]

    decisions = build_dry_run_decisions(
        examples,
        eval_split="test",
        train_split="train",
    )

    by_case = {item["case_id"]: item for item in decisions}
    assert set(by_case) == {
        "test_style_missing_source",
        "test_provider_failure",
        "test_decompose_source_available",
    }

    style = by_case["test_style_missing_source"]
    assert style["action_router"]["policy_name"] == "tiny_action_model_v1"
    assert style["action_router"]["recommended_action"] == "adjust_prompt"
    assert style["source_dependency_router"] == {
        "policy_name": "source_dependency_rule_v1",
        "recommended_source_dependency": "required",
        "recommended_decision_basis": "artifact_source",
        "confidence": 0.8,
        "rule_reason": "layer_generate_source_artifact_judgement",
        "target_source_dependency": "required",
        "target_decision_basis": "artifact_source",
    }
    assert style["dispatch"]["decision_owner"] == "tiny_model"
    assert style["dispatch"]["execution_owner"] == "fallback_agent"
    assert style["dispatch"]["fallback_agent"] is True
    assert style["dispatch"]["fallback_reasons"] == [
        "source_required_but_unavailable"
    ]
    assert style["dispatch"]["data_gap_tags"] == [
        "no_source_context_for_required_source"
    ]

    provider = by_case["test_provider_failure"]
    assert provider["action_router"]["recommended_action"] == "fallback_to_agent"
    assert provider["source_dependency_router"]["recommended_source_dependency"] == (
        "not_needed"
    )
    assert provider["source_dependency_router"]["recommended_decision_basis"] == (
        "metadata_only"
    )
    assert provider["dispatch"]["fallback_reasons"] == ["action_fallback_to_agent"]
    assert provider["dispatch"]["data_gap_tags"] == []

    decompose = by_case["test_decompose_source_available"]
    assert decompose["action_router"]["recommended_action"] == "split_layer_further"
    assert decompose["source_dependency_router"]["recommended_decision_basis"] == (
        "image_source"
    )
    assert decompose["dispatch"]["fallback_agent"] is False
    assert decompose["dispatch"]["execution_owner"] == "tiny_model"


def test_dry_run_decisions_treat_auxiliary_source_context_signal_as_available():
    from vulca.learning.dry_run_decision_router import build_dry_run_decisions

    train = _example("train_style", split="train")
    test = _example("test_style_aux_source_context", split="test")
    test["source_context"] = {
        "available": False,
        "source_artifact_available_count": 0,
        "source_image_available": False,
    }
    test["input"]["auxiliary_signals"] = [
        _source_context_signal("example_test_style_aux_source_context")
    ]

    decisions = build_dry_run_decisions(
        [train, test],
        eval_split="test",
        train_split="train",
    )

    assert len(decisions) == 1
    dispatch = decisions[0]["dispatch"]
    assert dispatch["fallback_agent"] is False
    assert dispatch["fallback_reasons"] == []
    assert dispatch["data_gap_tags"] == []
    assert decisions[0]["source_context"] == {
        "available": True,
        "source": "auxiliary_signal",
        "signal_count": 1,
    }


def test_dry_run_router_report_summarizes_counts_and_evaluation():
    from vulca.learning.dry_run_decision_router import build_dry_run_router_report

    examples = [
        _example("train_style", split="train"),
        _example("test_style_missing_source", split="test"),
        _example(
            "test_decompose_source_available",
            split="test",
            case_type="decompose_case",
            failure_type="under_segmentation",
            preferred_action="split_layer_further",
            source_dependency="required",
            source_decision_basis="image_source",
            source_context_available=True,
        ),
    ]

    report = build_dry_run_router_report(
        examples,
        eval_split="test",
        train_split="train",
    )

    assert report["case_type"] == "learning_dry_run_decision_router_report"
    assert report["summary"]["decision_count"] == 2
    assert report["summary"]["fallback_agent_count"] == 1
    assert report["summary"]["counts_by_recommended_action"] == {
        "adjust_prompt": 1,
        "split_layer_further": 1,
    }
    assert report["summary"]["counts_by_source_dependency"] == {"required": 2}
    assert report["summary"]["data_gap_counts"] == {
        "no_source_context_for_required_source": 1
    }
    assert report["evaluation"]["action_accuracy"] == 1.0
    assert report["evaluation"]["source_dependency_accuracy"] == 1.0
    assert report["evaluation"]["decision_basis_accuracy"] == 1.0


def test_dry_run_decision_router_cli_writes_real_dataset_report(tmp_path):
    output_dir = tmp_path / "decision_router"
    report_path = tmp_path / "decision_router_report.json"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/dry_run_decision_router.py"),
            "--repo-root",
            str(ROOT),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report_path),
            "--case-source-manifest",
            str(ROOT / "docs/benchmarks/learning/combined_case_source_manifest_v1.json"),
            "--source-dependency-manifest",
            str(
                ROOT
                / "docs/benchmarks/learning/real_source_dependency_label_manifest_v1.json"
            ),
            "--auxiliary-signal-manifest",
            "",
            "--split",
            "test",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Dry-run decision router report:" in result.stdout
    assert "Decisions: 21" in result.stdout
    assert "tiny_action_model_v1 action_accuracy: 1.0" in result.stdout
    assert "source_dependency_rule_v1 source_dependency_accuracy:" in result.stdout
    assert (output_dir / "dry_run_decisions.jsonl").exists()
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["decision_count"] == 21
    assert report["summary"]["counts_by_source_dependency"]["required"] > 0
    assert report["evaluation"]["action_accuracy"] == 1.0
    assert report["artifacts"]["decision_path"] == str(
        output_dir / "dry_run_decisions.jsonl"
    )
