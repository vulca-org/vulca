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
    case_type: str = "layer_generate_case",
    failure_type: str = "prompt_ambiguity",
    source_dependency: str = "required",
    decision_basis: str = "artifact_source",
    source_artifact_count: int = 1,
    source_image_available: bool = False,
    split: str = "test",
) -> dict:
    return {
        "schema_version": 1,
        "case_type": "learning_tiny_dataset_example",
        "example_id": f"example_{case_id}",
        "split": split,
        "source_case": {
            "case_id": case_id,
            "case_type": case_type,
        },
        "input": {
            "case_record": {
                "case_type": case_type,
                "case_id": case_id,
                "review": {
                    "failure_type": failure_type,
                    "preferred_action": "manual_review",
                },
            },
        },
        "targets": {
            "failure_type": failure_type,
            "preferred_action": "manual_review",
            "source_dependency": source_dependency,
            "source_decision_basis": decision_basis,
        },
        "tasks": {
            "source_context": {
                "dependency_classification": source_dependency,
                "decision_basis_classification": decision_basis,
            }
        },
        "source_dependency_review": {
            "label_id": f"label_{case_id}",
            "review_status": "reviewed_source_dependency_label",
        },
        "source_context": {
            "available": bool(source_artifact_count or source_image_available),
            "source_artifact_available_count": source_artifact_count,
            "source_image_available": source_image_available,
        },
    }


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_source_dependency_rule_scores_dependency_and_basis_without_labels():
    from vulca.learning.source_dependency_eval import (
        POLICY_SOURCE_DEPENDENCY_RULE,
        evaluate_source_dependency_policy,
    )

    examples = [
        _example(
            "provider_failure",
            failure_type="provider_failure",
            source_dependency="not_needed",
            decision_basis="metadata_only",
            source_artifact_count=3,
            source_image_available=True,
        ),
        _example(
            "layer_prompt",
            failure_type="prompt_ambiguity",
            source_dependency="required",
            decision_basis="artifact_source",
        ),
        _example(
            "decompose_under",
            case_type="decompose_case",
            failure_type="under_segmentation",
            source_dependency="required",
            decision_basis="image_source",
        ),
    ]

    report = evaluate_source_dependency_policy(
        examples,
        policy_name=POLICY_SOURCE_DEPENDENCY_RULE,
    )

    assert report["policy_name"] == "source_dependency_rule_v1"
    assert report["dependency_labeled_count"] == 3
    assert report["dependency_accuracy"] == 1.0
    assert report["decision_basis_accuracy"] == 1.0
    assert report["mismatch_count"] == 0
    assert [item["recommended_source_dependency"] for item in report["recommendations"]] == [
        "not_needed",
        "required",
        "required",
    ]


def test_source_dependency_majority_baseline_is_ranked_below_rule():
    from vulca.learning.source_dependency_eval import (
        POLICY_SOURCE_DEPENDENCY_MAJORITY,
        POLICY_SOURCE_DEPENDENCY_RULE,
        build_source_dependency_comparison_report,
    )

    examples = [
        _example(
            "train_required",
            source_dependency="required",
            decision_basis="artifact_source",
            split="train",
        ),
        _example(
            "train_not_needed",
            failure_type="provider_failure",
            source_dependency="not_needed",
            decision_basis="metadata_only",
            split="train",
        ),
        _example(
            "test_not_needed",
            failure_type="provider_failure",
            source_dependency="not_needed",
            decision_basis="metadata_only",
            source_artifact_count=3,
            source_image_available=True,
            split="test",
        ),
        _example(
            "test_decompose",
            case_type="decompose_case",
            failure_type="under_segmentation",
            source_dependency="required",
            decision_basis="image_source",
            split="test",
        ),
    ]

    comparison = build_source_dependency_comparison_report(
        examples,
        eval_split="test",
        train_split="train",
        policy_names=(POLICY_SOURCE_DEPENDENCY_MAJORITY, POLICY_SOURCE_DEPENDENCY_RULE),
    )

    assert comparison["case_type"] == "learning_source_dependency_comparison_report"
    assert comparison["example_count"] == 2
    assert comparison["policy_reports"][POLICY_SOURCE_DEPENDENCY_RULE][
        "dependency_accuracy"
    ] == 1.0
    assert comparison["policy_reports"][POLICY_SOURCE_DEPENDENCY_MAJORITY][
        "dependency_accuracy"
    ] == 0.5
    assert comparison["ranked_policies"][0]["policy_name"] == POLICY_SOURCE_DEPENDENCY_RULE


def test_source_dependency_eval_cli_exports_dataset_and_report(tmp_path):
    output_dir = tmp_path / "source_dependency_eval"
    report_path = tmp_path / "source_dependency_eval_report.json"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/source_dependency_eval.py"),
            "--repo-root",
            str(ROOT),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report_path),
            "--case-source-manifest",
            str(ROOT / "docs/benchmarks/learning/combined_case_source_manifest_v1.json"),
            "--source-dependency-manifest",
            str(ROOT / "docs/benchmarks/learning/real_source_dependency_label_manifest_v1.json"),
            "--no-local-seeds",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Source dependency eval report:" in result.stdout
    assert "source_dependency_rule_v1 dependency_accuracy: 1.0" in result.stdout
    assert (output_dir / "tiny_dataset.with_source_dependency.jsonl").exists()
    assert report_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["case_type"] == "learning_source_dependency_eval_run_report"
    assert report["dataset"]["source_dependency_labeled_count"] == 12
    policy_reports = report["comparison"]["policy_reports"]
    assert policy_reports["source_dependency_rule_v1"]["dependency_accuracy"] == 1.0
    assert policy_reports["source_dependency_rule_v1"]["decision_basis_accuracy"] == 1.0
    assert policy_reports["source_dependency_majority"]["dependency_accuracy"] < 1.0

    examples = _read_jsonl(output_dir / "tiny_dataset.with_source_dependency.jsonl")
    assert sum(1 for item in examples if item["targets"].get("source_dependency")) == 12


def test_source_dependency_eval_cli_fails_threshold(tmp_path):
    output_dir = tmp_path / "source_dependency_eval"
    report_path = tmp_path / "source_dependency_eval_report.json"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/source_dependency_eval.py"),
            "--repo-root",
            str(ROOT),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report_path),
            "--case-source-manifest",
            str(ROOT / "docs/benchmarks/learning/combined_case_source_manifest_v1.json"),
            "--source-dependency-manifest",
            str(ROOT / "docs/benchmarks/learning/real_source_dependency_label_manifest_v1.json"),
            "--no-local-seeds",
            "--min-dependency-accuracy",
            "source_dependency_rule_v1=1.01",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 1
    assert "Source dependency eval gate failed" in result.stderr
    assert "source_dependency_rule_v1 dependency_accuracy 1.0 < 1.01" in result.stderr
