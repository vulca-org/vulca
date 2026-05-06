"""Per-case review table for tiny model/agent selection."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from vulca.layers.redraw_cases import CASE_TYPE as REDRAW_CASE_TYPE
from vulca.learning.model_selection_report import (
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    DEFAULT_OUTPUT_DIR as MODEL_SELECTION_OUTPUT_DIR,
    POLICY_REDRAW_OBSERVABLE_SIGNAL,
    run_model_selection_report,
)
from vulca.learning.tiny_action_model import POLICY_TINY_ACTION_MODEL
from vulca.learning.tiny_baseline_model import POLICY_TINY_AGENT
from vulca.learning.tiny_dataset import DATASET_SPLITS, load_tiny_dataset_examples


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_model_selection_review_table"
ROW_CASE_TYPE = "learning_model_selection_review_row"
DEFAULT_OUTPUT_DIR = Path("build/model_selection_review_table")
DEFAULT_REPORT_NAME = "model_selection_review_table_report.json"
DEFAULT_JSONL_NAME = "model_selection_review_table.jsonl"
DEFAULT_CSV_NAME = "model_selection_review_table.csv"
CSV_COLUMNS: tuple[str, ...] = (
    "review_action",
    "priority_score",
    "case_type",
    "case_id",
    "example_id",
    "source_kind",
    "source_id",
    "failure_type",
    "target_action",
    "primary_action",
    "primary_correct",
    "baseline_action",
    "baseline_correct",
    "guardrail_action",
    "guardrail_correct",
    "policy_disagreement",
    "workload_decision",
    "review_reason",
)


def run_model_selection_review_table(
    *,
    repo_root: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    case_source_manifest_path: str | Path = DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    include_local_seeds: bool = True,
    eval_split: str = "test",
    train_split: str = "train",
    min_eval_examples_per_bucket: int = 1,
    min_workload_eval_examples: int = 8,
) -> dict[str, Any]:
    """Export eval cases with policy outcomes and manual-review priorities."""
    _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")

    root = Path(repo_root).resolve()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    model_selection_report = run_model_selection_report(
        repo_root=root,
        output_dir=output / "model_selection",
        case_source_manifest_path=case_source_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
        min_eval_examples_per_bucket=min_eval_examples_per_bucket,
        min_workload_eval_examples=min_workload_eval_examples,
    )

    dataset_path = Path(str(model_selection_report["artifacts"]["dataset_path"]))
    comparison_path = Path(
        str(model_selection_report["artifacts"]["comparison_report_path"])
    )
    examples = [
        item
        for item in load_tiny_dataset_examples(dataset_path)
        if item.get("split") == eval_split
    ]
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    policies = _recommendations_by_policy(comparison)
    workload_by_case_type = {
        str(item.get("case_type") or ""): item
        for item in model_selection_report["workload_recommendations"]
    }
    selection = _mapping(model_selection_report.get("selection"))
    primary_policy = str(
        selection.get("recommended_primary_policy") or POLICY_TINY_ACTION_MODEL
    )
    baseline_policy = str(
        selection.get("recommended_baseline_policy") or POLICY_TINY_AGENT
    )
    guardrail_policy = POLICY_REDRAW_OBSERVABLE_SIGNAL

    rows = [
        _build_review_row(
            example,
            policies=policies,
            workload_by_case_type=workload_by_case_type,
            primary_policy=primary_policy,
            baseline_policy=baseline_policy,
            guardrail_policy=guardrail_policy,
        )
        for example in examples
    ]
    rows = sorted(
        rows,
        key=lambda item: (
            -int(item["priority_score"]),
            str(item["case_type"]),
            str(item["failure_type"]),
            str(item["case_id"]),
        ),
    )

    jsonl_path = output / DEFAULT_JSONL_NAME
    csv_path = output / DEFAULT_CSV_NAME
    _write_jsonl(jsonl_path, rows)
    _write_csv(csv_path, rows)

    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": "ready_for_review",
        "train_split": train_split,
        "eval_split": eval_split,
        "inputs": {
            "repo_root": str(root),
            "case_source_manifest_path": str(_resolve_repo_path(root, case_source_manifest_path)),
            "include_local_seeds": bool(include_local_seeds),
            "min_eval_examples_per_bucket": int(min_eval_examples_per_bucket),
            "min_workload_eval_examples": int(min_workload_eval_examples),
        },
        "artifacts": {
            "report_path": str(resolved_report_path),
            "review_table_jsonl_path": str(jsonl_path),
            "review_table_csv_path": str(csv_path),
            "model_selection_report_path": model_selection_report["artifacts"][
                "report_path"
            ],
            "dataset_path": str(dataset_path),
            "comparison_report_path": str(comparison_path),
        },
        "selection": {
            "primary_policy": primary_policy,
            "baseline_policy": baseline_policy,
            "guardrail_policy": guardrail_policy,
        },
        "summary": _build_summary(rows),
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _build_review_row(
    example: Mapping[str, Any],
    *,
    policies: Mapping[str, Mapping[str, Mapping[str, Any]]],
    workload_by_case_type: Mapping[str, Mapping[str, Any]],
    primary_policy: str,
    baseline_policy: str,
    guardrail_policy: str,
) -> dict[str, Any]:
    source_case = _mapping(example.get("source_case"))
    source = _mapping(example.get("source"))
    targets = _mapping(example.get("targets"))
    example_id = str(example.get("example_id") or "")
    case_type = str(source_case.get("case_type") or "")
    target_action = str(targets.get("preferred_action") or "")
    policy_rows = {
        policy_name: _policy_projection(
            _mapping(recommendations.get(example_id)),
            target_action=target_action,
        )
        for policy_name, recommendations in sorted(policies.items())
        if example_id in recommendations
    }
    primary = policy_rows.get(primary_policy, {})
    baseline = policy_rows.get(baseline_policy, {})
    guardrail = policy_rows.get(guardrail_policy, {})
    actions = {
        str(row.get("recommended_action") or "")
        for row in policy_rows.values()
        if str(row.get("recommended_action") or "")
    }
    policy_disagreement = len(actions) > 1
    workload = _mapping(workload_by_case_type.get(case_type))
    workload_decision = str(workload.get("decision") or "")

    priority_score, review_action, review_reasons = _review_priority(
        source_kind=str(source.get("kind") or ""),
        primary_correct=primary.get("correct"),
        baseline_correct=baseline.get("correct"),
        guardrail_correct=guardrail.get("correct"),
        policy_disagreement=policy_disagreement,
        workload_decision=workload_decision,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": case_type,
        "row_case_type": ROW_CASE_TYPE,
        "example_id": example_id,
        "case_id": str(source_case.get("case_id") or ""),
        "split": str(example.get("split") or ""),
        "source_kind": str(source.get("kind") or ""),
        "source_id": str(source.get("source_id") or source.get("kind") or ""),
        "failure_type": str(targets.get("failure_type") or ""),
        "target_action": target_action,
        "primary_policy": primary_policy,
        "primary_action": str(primary.get("recommended_action") or ""),
        "primary_correct": primary.get("correct"),
        "baseline_policy": baseline_policy,
        "baseline_action": str(baseline.get("recommended_action") or ""),
        "baseline_correct": baseline.get("correct"),
        "guardrail_policy": guardrail_policy if case_type == REDRAW_CASE_TYPE else "",
        "guardrail_action": str(guardrail.get("recommended_action") or ""),
        "guardrail_correct": guardrail.get("correct"),
        "policy_disagreement": policy_disagreement,
        "workload_decision": workload_decision,
        "review_action": review_action,
        "priority_score": priority_score,
        "review_reason": "; ".join(review_reasons),
        "policies": policy_rows,
    }


def _policy_projection(
    recommendation: Mapping[str, Any],
    *,
    target_action: str,
) -> dict[str, Any]:
    action = str(recommendation.get("recommended_action") or "")
    correct = action == target_action if action and target_action else None
    return {
        "recommended_action": action,
        "correct": correct,
        "failure_hint": str(recommendation.get("failure_hint") or ""),
        "confidence": recommendation.get("confidence"),
        "rule_reason": str(recommendation.get("rule_reason") or ""),
    }


def _review_priority(
    *,
    source_kind: str,
    primary_correct: Any,
    baseline_correct: Any,
    guardrail_correct: Any,
    policy_disagreement: bool,
    workload_decision: str,
) -> tuple[int, str, list[str]]:
    score = 0
    reasons: list[str] = []
    review_action = "spot_check"
    if primary_correct is False:
        score += 100
        review_action = "inspect_primary_mismatch"
        reasons.append("primary policy missed the target action")
    if baseline_correct is False:
        score += 40
        if review_action == "spot_check":
            review_action = "verify_policy_disagreement"
        reasons.append("baseline disagrees with the label")
    if guardrail_correct is False:
        score += 35
        if review_action == "spot_check":
            review_action = "verify_policy_disagreement"
        reasons.append("redraw guardrail disagrees with the label")
    if policy_disagreement:
        score += 25
        reasons.append("policies recommend different actions")
    if workload_decision == "collect_more_real_cases":
        score += 20
        if review_action == "spot_check":
            review_action = "collect_more_real_case"
        reasons.append("workload needs more real cases before specialist training")
    if source_kind == "user_case_log":
        score += 15
        reasons.append("real user case")
    elif source_kind == "synthetic_case_log":
        score += 5
        reasons.append("taxonomy holdout case")
    if not reasons:
        reasons.append("primary policy currently agrees with the label")
    return score, review_action, reasons


def _recommendations_by_policy(
    comparison_report: Mapping[str, Any],
) -> dict[str, dict[str, Mapping[str, Any]]]:
    reports = _mapping(comparison_report.get("policy_reports"))
    by_policy: dict[str, dict[str, Mapping[str, Any]]] = {}
    for policy_name, report_value in reports.items():
        report = _mapping(report_value)
        rows: dict[str, Mapping[str, Any]] = {}
        for recommendation in report.get("recommendations", []) or []:
            if not isinstance(recommendation, Mapping):
                continue
            example_id = str(recommendation.get("example_id") or "")
            if example_id:
                rows[example_id] = recommendation
        by_policy[str(policy_name)] = rows
    return by_policy


def _build_summary(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "row_count": len(rows),
        "primary_mismatch_count": sum(
            1 for row in rows if row.get("primary_correct") is False
        ),
        "baseline_mismatch_count": sum(
            1 for row in rows if row.get("baseline_correct") is False
        ),
        "guardrail_mismatch_count": sum(
            1 for row in rows if row.get("guardrail_correct") is False
        ),
        "policy_disagreement_count": sum(
            1 for row in rows if bool(row.get("policy_disagreement"))
        ),
        "review_action_counts": dict(
            sorted(Counter(str(row.get("review_action") or "") for row in rows).items())
        ),
        "workload_decision_counts": dict(
            sorted(
                Counter(str(row.get("workload_decision") or "") for row in rows).items()
            )
        ),
        "counts_by_case_type": dict(
            sorted(Counter(str(row.get("case_type") or "") for row in rows).items())
        ),
    }


def _write_jsonl(path: Path, rows: list[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def _write_csv(path: Path, rows: list[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: _csv_value(row.get(column))
                    for column in CSV_COLUMNS
                }
            )


def _csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _resolve_repo_path(repo_root: Path, path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = repo_root / resolved
    return resolved


def _validate_split(value: str, *, label: str) -> None:
    if value not in DATASET_SPLITS:
        raise ValueError(f"unsupported {label} {value!r}; expected one of {DATASET_SPLITS}")


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
