"""Training effectiveness report for combined tiny learning sources."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.learning.aggregated_case_source_eval import run_aggregated_case_source_eval
from vulca.learning.source_dependency_eval import (
    DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
    POLICY_SOURCE_DEPENDENCY_MAJORITY,
    run_source_dependency_eval,
)
from vulca.learning.tiny_action_model import POLICY_TINY_ACTION_MODEL
from vulca.learning.tiny_baseline_model import POLICY_TINY_AGENT
from vulca.learning.tiny_dataset import DATASET_SPLITS


SCHEMA_VERSION = 2
REPORT_CASE_TYPE = "learning_training_effectiveness_report"
DEFAULT_OUTPUT_DIR = Path("build/training_effectiveness_report")
DEFAULT_REPORT_NAME = "training_effectiveness_report.json"
DEFAULT_COMBINED_CASE_SOURCE_MANIFEST = Path(
    "docs/benchmarks/learning/combined_case_source_manifest_v1.json"
)
DEFAULT_EVALUATED_POLICY = POLICY_TINY_ACTION_MODEL
DEFAULT_BASELINE_POLICY = POLICY_TINY_AGENT
DEFAULT_COVERAGE_BUCKETS: tuple[str, ...] = (
    "source.kind",
    "source_case.case_type",
    "targets.failure_type",
)


def run_training_effectiveness_report(
    *,
    repo_root: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    case_source_manifest_path: str | Path = DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    include_local_seeds: bool = True,
    eval_split: str = "test",
    train_split: str = "train",
    min_eval_examples_per_bucket: int = 1,
    source_dependency_manifest_path: str | Path = DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
    source_dependency_eval_split: str | None = None,
) -> dict[str, Any]:
    """Run combined tiny eval and summarize model effectiveness plus data gaps."""
    _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")
    if source_dependency_eval_split is not None:
        _validate_split(
            source_dependency_eval_split,
            label="source_dependency_eval_split",
        )
    if min_eval_examples_per_bucket < 0:
        raise ValueError("min_eval_examples_per_bucket must be >= 0")

    root = Path(repo_root).resolve()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    resolved_manifest_path = _resolve_repo_path(root, case_source_manifest_path)
    resolved_source_dependency_manifest_path = _resolve_repo_path(
        root,
        source_dependency_manifest_path,
    )
    aggregated_output_dir = output / "aggregated"
    aggregated_report = run_aggregated_case_source_eval(
        repo_root=root,
        output_dir=aggregated_output_dir,
        case_source_manifest_paths=[resolved_manifest_path],
        include_default_case_source_manifest=False,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
    )
    source_dependency_report = run_source_dependency_eval(
        repo_root=root,
        output_dir=output / "source_dependency",
        case_source_manifest_path=resolved_manifest_path,
        source_dependency_manifest_path=resolved_source_dependency_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=source_dependency_eval_split,
        train_split=train_split,
    )
    data_gaps = _build_data_gaps(
        aggregated_report,
        min_eval_examples=min_eval_examples_per_bucket,
    )
    effectiveness = _build_effectiveness_summary(aggregated_report)
    source_dependency = _build_source_dependency_summary(source_dependency_report)
    gate_passed = bool(effectiveness["gate_passed"]) and bool(
        source_dependency["gate_passed"]
    )
    if not gate_passed:
        status = "failed_gate"
    elif data_gaps:
        status = "passed_with_data_gaps"
    else:
        status = "passed"

    dataset_summary = _mapping(aggregated_report.get("dataset_summary"))
    counts_by_split = _mapping(dataset_summary.get("counts_by_split"))
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": status,
        "train_split": train_split,
        "eval_split": eval_split,
        "inputs": {
            "repo_root": str(root),
            "case_source_manifest_path": str(resolved_manifest_path),
            "source_dependency_manifest_path": str(
                resolved_source_dependency_manifest_path
            ),
            "include_local_seeds": bool(include_local_seeds),
            "min_eval_examples_per_bucket": int(min_eval_examples_per_bucket),
            "source_dependency_eval_split": source_dependency["eval_split"],
        },
        "artifacts": {
            "report_path": str(resolved_report_path),
            "aggregated_report_path": aggregated_report["artifacts"]["report_path"],
            "tiny_training_eval_report_path": aggregated_report["artifacts"][
                "tiny_training_eval_report_path"
            ],
            "dataset_path": aggregated_report["artifacts"]["dataset_path"],
            "dataset_index_path": aggregated_report["artifacts"]["dataset_index_path"],
            "comparison_report_path": aggregated_report["artifacts"][
                "comparison_report_path"
            ],
            "tiny_feature_ablation_report_path": aggregated_report["artifacts"][
                "tiny_feature_ablation_report_path"
            ],
            "source_dependency_eval_report_path": source_dependency_report["artifacts"][
                "report_path"
            ],
            "source_dependency_dataset_path": source_dependency_report["artifacts"][
                "dataset_path"
            ],
            "source_dependency_comparison_report_path": source_dependency_report[
                "artifacts"
            ]["comparison_report_path"],
        },
        "dataset": {
            "example_count": int(dataset_summary.get("example_count") or 0),
            "eval_example_count": int(counts_by_split.get(eval_split) or 0),
            "counts_by_split": dict(counts_by_split),
            "counts_by_source_kind": dict(
                _mapping(dataset_summary.get("counts_by_source_kind"))
            ),
            "counts_by_source_case_type": dict(
                _mapping(dataset_summary.get("counts_by_source_case_type"))
            ),
            "target_counts": dict(_mapping(dataset_summary.get("target_counts"))),
        },
        "coverage": _build_coverage_summary(aggregated_report),
        "effectiveness": effectiveness,
        "source_dependency": source_dependency,
        "leaderboard": _build_task_leaderboard(effectiveness, source_dependency),
        "data_gaps": data_gaps,
    }

    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def format_data_gap(gap: Mapping[str, Any]) -> str:
    bucket = str(gap.get("bucket") or "")
    value = str(gap.get("value") or "")
    eval_count = int(gap.get("eval_example_count") or 0)
    minimum = int(gap.get("min_eval_examples") or 0)
    return f"{bucket} {value} eval {eval_count} < {minimum}"


def _build_effectiveness_summary(aggregated_report: Mapping[str, Any]) -> dict[str, Any]:
    policy_reports = _mapping(
        _mapping(aggregated_report.get("policy_comparison")).get("policy_reports")
    )
    evaluated = _mapping(policy_reports.get(DEFAULT_EVALUATED_POLICY))
    baseline = _mapping(policy_reports.get(DEFAULT_BASELINE_POLICY))
    action_accuracy = _float_or_none(evaluated.get("action_accuracy"))
    baseline_accuracy = _float_or_none(baseline.get("action_accuracy"))
    accuracy_delta = None
    if action_accuracy is not None and baseline_accuracy is not None:
        accuracy_delta = action_accuracy - baseline_accuracy

    gate = _mapping(_mapping(aggregated_report.get("tiny_training_eval")).get("gate"))
    ablation = _mapping(
        _mapping(aggregated_report.get("tiny_training_eval")).get("ablation")
    )
    return {
        "gate_passed": bool(gate.get("passed")),
        "evaluated_policy": DEFAULT_EVALUATED_POLICY,
        "baseline_policy": DEFAULT_BASELINE_POLICY,
        "action_accuracy": action_accuracy,
        "baseline_action_accuracy": baseline_accuracy,
        "accuracy_delta_vs_baseline": accuracy_delta,
        "mismatch_count": int(evaluated.get("mismatch_count") or 0),
        "missing_count": int(evaluated.get("missing_count") or 0),
        "ablation_summary": dict(_mapping(ablation.get("summary"))),
        "ablation_variants": _compact_ablation_variants(ablation),
        "gate": dict(gate),
        "policy_ranking": _policy_ranking(policy_reports),
    }


def _build_source_dependency_summary(
    source_dependency_report: Mapping[str, Any],
) -> dict[str, Any]:
    comparison = _mapping(source_dependency_report.get("comparison"))
    policy_reports = _mapping(comparison.get("policy_reports"))
    ranking = [
        _compact_source_dependency_rank(item)
        for item in comparison.get("ranked_policies", []) or []
        if isinstance(item, Mapping)
    ]
    best_policy = ranking[0] if ranking else {}
    return {
        "gate_passed": bool(_mapping(source_dependency_report.get("gate")).get("passed")),
        "eval_split": str(source_dependency_report.get("eval_split") or "all"),
        "labeled_count": int(
            _mapping(source_dependency_report.get("dataset")).get(
                "source_dependency_labeled_count",
            )
            or 0
        ),
        "best_policy": best_policy,
        "policy_ranking": ranking,
        "policy_reports": {
            str(policy_name): _compact_source_dependency_policy_report(report_value)
            for policy_name, report_value in sorted(policy_reports.items())
        },
        "gate": dict(_mapping(source_dependency_report.get("gate"))),
    }


def _compact_source_dependency_rank(rank: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "policy_name": str(rank.get("policy_name") or ""),
        "dependency_accuracy": _float_or_none(rank.get("dependency_accuracy")),
        "decision_basis_accuracy": _float_or_none(rank.get("decision_basis_accuracy")),
        "evaluated_count": int(rank.get("evaluated_count") or 0),
        "mismatch_count": int(rank.get("mismatch_count") or 0),
    }


def _compact_source_dependency_policy_report(
    report_value: Any,
) -> dict[str, Any]:
    report = _mapping(report_value)
    return {
        "dependency_accuracy": _float_or_none(report.get("dependency_accuracy")),
        "decision_basis_accuracy": _float_or_none(
            report.get("decision_basis_accuracy")
        ),
        "dependency_labeled_count": int(
            report.get("dependency_labeled_count") or 0
        ),
        "decision_basis_labeled_count": int(
            report.get("decision_basis_labeled_count") or 0
        ),
        "evaluated_count": int(report.get("evaluated_count") or 0),
        "mismatch_count": int(report.get("mismatch_count") or 0),
    }


def _build_task_leaderboard(
    effectiveness: Mapping[str, Any],
    source_dependency: Mapping[str, Any],
) -> list[dict[str, Any]]:
    source_best = _mapping(source_dependency.get("best_policy"))
    return [
        {
            "task": "action_routing",
            "best_policy": str(effectiveness.get("evaluated_policy") or ""),
            "baseline_policy": str(effectiveness.get("baseline_policy") or ""),
            "primary_metric": "action_accuracy",
            "primary_accuracy": _float_or_none(effectiveness.get("action_accuracy")),
            "secondary_metric": None,
            "secondary_accuracy": None,
            "mismatch_count": int(effectiveness.get("mismatch_count") or 0),
            "gate_passed": bool(effectiveness.get("gate_passed")),
        },
        {
            "task": "source_dependency",
            "best_policy": str(source_best.get("policy_name") or ""),
            "baseline_policy": POLICY_SOURCE_DEPENDENCY_MAJORITY,
            "primary_metric": "dependency_accuracy",
            "primary_accuracy": _float_or_none(
                source_best.get("dependency_accuracy")
            ),
            "secondary_metric": "decision_basis_accuracy",
            "secondary_accuracy": _float_or_none(
                source_best.get("decision_basis_accuracy")
            ),
            "mismatch_count": int(source_best.get("mismatch_count") or 0),
            "gate_passed": bool(source_dependency.get("gate_passed")),
        },
    ]


def _policy_ranking(policy_reports: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for policy_name, report_value in policy_reports.items():
        report = _mapping(report_value)
        rows.append(
            {
                "policy_name": str(policy_name),
                "action_accuracy": _float_or_none(report.get("action_accuracy")),
                "mismatch_count": int(report.get("mismatch_count") or 0),
                "missing_count": int(report.get("missing_count") or 0),
            }
        )
    return sorted(
        rows,
        key=lambda item: (
            item["action_accuracy"] is None,
            -(item["action_accuracy"] or 0.0),
            item["mismatch_count"],
            item["policy_name"],
        ),
    )


def _compact_ablation_variants(
    ablation_report: Mapping[str, Any],
) -> list[dict[str, Any]]:
    variants = ablation_report.get("variant_reports")
    if not isinstance(variants, Sequence) or isinstance(variants, (str, bytes)):
        return []
    rows: list[dict[str, Any]] = []
    for variant_value in variants:
        variant = _mapping(variant_value)
        policy_report = _mapping(variant.get("policy_report"))
        rows.append(
            {
                "variant_id": str(variant.get("variant_id") or ""),
                "removed_feature_groups": list(
                    variant.get("removed_feature_groups") or []
                ),
                "action_accuracy": _float_or_none(
                    policy_report.get("action_accuracy")
                ),
                "mismatch_count": int(policy_report.get("mismatch_count") or 0),
                "accuracy_delta_vs_full": _float_or_none(
                    variant.get("accuracy_delta_vs_full")
                ),
                "fallback_reason_counts": dict(
                    _mapping(variant.get("fallback_reason_counts"))
                ),
                "auxiliary_feature_match_count": int(
                    variant.get("auxiliary_feature_match_count") or 0
                ),
            }
        )
    return rows


def _build_coverage_summary(aggregated_report: Mapping[str, Any]) -> dict[str, Any]:
    bucket_metrics = _mapping(aggregated_report.get("bucket_metrics"))
    return {
        "source_kind": _compact_bucket_counts(bucket_metrics, "source.kind"),
        "source_case_type": _compact_bucket_counts(bucket_metrics, "source_case.case_type"),
        "failure_type": _compact_bucket_counts(bucket_metrics, "targets.failure_type"),
    }


def _compact_bucket_counts(
    bucket_metrics: Mapping[str, Any],
    bucket: str,
) -> dict[str, dict[str, int]]:
    rows: dict[str, dict[str, int]] = {}
    for value, metrics_value in _mapping(bucket_metrics.get(bucket)).items():
        metrics = _mapping(metrics_value)
        rows[str(value)] = {
            "example_count": int(metrics.get("example_count") or 0),
            "eval_example_count": int(metrics.get("eval_example_count") or 0),
        }
    return dict(sorted(rows.items()))


def _build_data_gaps(
    aggregated_report: Mapping[str, Any],
    *,
    min_eval_examples: int,
) -> list[dict[str, Any]]:
    if min_eval_examples <= 0:
        return []

    gaps: list[dict[str, Any]] = []
    bucket_metrics = _mapping(aggregated_report.get("bucket_metrics"))
    for bucket in DEFAULT_COVERAGE_BUCKETS:
        for value, metrics_value in _mapping(bucket_metrics.get(bucket)).items():
            if bucket == "targets.failure_type" and value == "unlabeled":
                continue
            metrics = _mapping(metrics_value)
            example_count = int(metrics.get("example_count") or 0)
            eval_count = int(metrics.get("eval_example_count") or 0)
            if example_count <= 0 or eval_count >= min_eval_examples:
                continue
            gaps.append(
                {
                    "bucket": bucket,
                    "value": str(value),
                    "example_count": example_count,
                    "eval_example_count": eval_count,
                    "min_eval_examples": int(min_eval_examples),
                    "reason": "insufficient_eval_coverage",
                }
            )
    return sorted(
        gaps,
        key=lambda item: (
            item["bucket"],
            item["eval_example_count"],
            -item["example_count"],
            item["value"],
        ),
    )


def _resolve_repo_path(repo_root: Path, path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = repo_root / resolved
    return resolved


def _validate_split(value: str, *, label: str) -> None:
    if value not in DATASET_SPLITS:
        raise ValueError(f"unsupported {label} {value!r}; expected one of {DATASET_SPLITS}")


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
