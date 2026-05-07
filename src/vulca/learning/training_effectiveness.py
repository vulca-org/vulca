"""Training effectiveness report for combined tiny learning sources."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.learning.aggregated_case_source_eval import run_aggregated_case_source_eval
from vulca.learning.dry_run_decision_router import run_dry_run_decision_router
from vulca.learning.source_dependency_eval import (
    DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
    POLICY_SOURCE_DEPENDENCY_MAJORITY,
    run_source_dependency_eval,
)
from vulca.learning.tiny_action_model import POLICY_TINY_ACTION_MODEL
from vulca.learning.tiny_baseline_model import POLICY_TINY_AGENT
from vulca.learning.tiny_dataset import DATASET_SPLITS


SCHEMA_VERSION = 3
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
    source_context_router = _build_source_context_router_summary(
        repo_root=root,
        output_dir=output,
        case_source_manifest_path=resolved_manifest_path,
        source_dependency_manifest_path=resolved_source_dependency_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
    )
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
            "source_context_signal_report_path": source_context_router["artifacts"][
                "source_context_signal_report_path"
            ],
            "source_context_signal_manifest_path": source_context_router["artifacts"][
                "source_context_signal_manifest_path"
            ],
            "source_context_signal_output_path": source_context_router["artifacts"][
                "source_context_signal_output_path"
            ],
            "dry_run_without_source_context_report_path": source_context_router[
                "artifacts"
            ]["dry_run_without_source_context_report_path"],
            "dry_run_with_source_context_report_path": source_context_router[
                "artifacts"
            ]["dry_run_with_source_context_report_path"],
            "dry_run_without_source_context_decision_path": source_context_router[
                "artifacts"
            ]["dry_run_without_source_context_decision_path"],
            "dry_run_with_source_context_decision_path": source_context_router[
                "artifacts"
            ]["dry_run_with_source_context_decision_path"],
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
        "source_context_router": source_context_router,
        "leaderboard": _build_task_leaderboard(
            effectiveness,
            source_dependency,
            source_context_router,
        ),
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


def _build_source_context_router_summary(
    *,
    repo_root: Path,
    output_dir: Path,
    case_source_manifest_path: Path,
    source_dependency_manifest_path: Path,
    include_local_seeds: bool,
    eval_split: str,
    train_split: str,
) -> dict[str, Any]:
    from vulca.learning.source_context_signals import write_source_context_signal_pack

    source_context_output = output_dir / "source_context"
    signal_output_path = source_context_output / "source_context_signals.promoted.jsonl"
    signal_manifest_path = (
        source_context_output / "source_context_signal_promotion_manifest.json"
    )
    signal_report_path = source_context_output / "source_context_signal_report.json"
    signal_report = write_source_context_signal_pack(
        repo_root=repo_root,
        case_source_manifest_path=case_source_manifest_path,
        output_path=signal_output_path,
        manifest_path=signal_manifest_path,
        report_path=signal_report_path,
        include_local_seeds=include_local_seeds,
    )

    baseline_report = run_dry_run_decision_router(
        repo_root=repo_root,
        output_dir=output_dir / "dry_run_without_source_context",
        report_path=output_dir / "dry_run_without_source_context" / "report.json",
        case_source_manifest_path=case_source_manifest_path,
        source_dependency_manifest_path=source_dependency_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
    )
    current_report = run_dry_run_decision_router(
        repo_root=repo_root,
        output_dir=output_dir / "dry_run_with_source_context",
        report_path=output_dir / "dry_run_with_source_context" / "report.json",
        case_source_manifest_path=case_source_manifest_path,
        source_dependency_manifest_path=source_dependency_manifest_path,
        auxiliary_signal_manifest_path=signal_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
    )

    baseline_decisions = _load_jsonl(
        _mapping(baseline_report["artifacts"])["decision_path"]
    )
    current_decisions = _load_jsonl(
        _mapping(current_report["artifacts"])["decision_path"]
    )
    improved_cases = _build_source_context_improved_cases(
        baseline_decisions,
        current_decisions,
    )
    remaining_gap_cases = _build_remaining_source_context_gap_cases(current_decisions)

    baseline_gap_count = _data_gap_count(
        baseline_report,
        "no_source_context_for_required_source",
    )
    current_gap_count = _data_gap_count(
        current_report,
        "no_source_context_for_required_source",
    )
    baseline_fallback_count = _fallback_agent_count(baseline_report)
    current_fallback_count = _fallback_agent_count(current_report)
    fallback_delta = current_fallback_count - baseline_fallback_count
    gap_delta = current_gap_count - baseline_gap_count
    fallback_reduction = baseline_fallback_count - current_fallback_count
    gap_reduction = baseline_gap_count - current_gap_count

    if fallback_reduction > 0 or gap_reduction > 0:
        status = "improved_with_source_context_signals"
    elif int(_mapping(signal_report.get("summary")).get("promoted_signal_count") or 0):
        status = "signals_available_no_dispatch_change"
    else:
        status = "no_source_context_signals"

    return {
        "status": status,
        "source_context_signal_summary": dict(_mapping(signal_report.get("summary"))),
        "baseline_without_source_context_signals": _compact_dry_run_report(
            baseline_report,
        ),
        "with_source_context_signals": _compact_dry_run_report(current_report),
        "delta": {
            "fallback_agent_count": fallback_delta,
            "fallback_agent_count_reduction": fallback_reduction,
            "no_source_context_for_required_source": gap_delta,
            "no_source_context_for_required_source_reduction": gap_reduction,
        },
        "improved_case_count": len(improved_cases),
        "improved_cases": improved_cases,
        "remaining_no_source_context_gap_count": len(remaining_gap_cases),
        "remaining_no_source_context_gap_cases": remaining_gap_cases,
        "artifacts": {
            "source_context_signal_report_path": str(signal_report_path),
            "source_context_signal_manifest_path": str(signal_manifest_path),
            "source_context_signal_output_path": str(signal_output_path),
            "dry_run_without_source_context_report_path": str(
                _mapping(baseline_report["artifacts"])["report_path"]
            ),
            "dry_run_with_source_context_report_path": str(
                _mapping(current_report["artifacts"])["report_path"]
            ),
            "dry_run_without_source_context_decision_path": str(
                _mapping(baseline_report["artifacts"])["decision_path"]
            ),
            "dry_run_with_source_context_decision_path": str(
                _mapping(current_report["artifacts"])["decision_path"]
            ),
        },
    }


def _compact_dry_run_report(report: Mapping[str, Any]) -> dict[str, Any]:
    summary = _mapping(report.get("summary"))
    evaluation = _mapping(report.get("evaluation"))
    return {
        "decision_count": int(summary.get("decision_count") or 0),
        "fallback_agent_count": int(summary.get("fallback_agent_count") or 0),
        "data_gap_counts": dict(_mapping(summary.get("data_gap_counts"))),
        "fallback_reason_counts": dict(_mapping(summary.get("fallback_reason_counts"))),
        "counts_by_execution_owner": dict(
            _mapping(summary.get("counts_by_execution_owner"))
        ),
        "action_accuracy": _float_or_none(evaluation.get("action_accuracy")),
        "source_dependency_accuracy": _float_or_none(
            evaluation.get("source_dependency_accuracy")
        ),
        "decision_basis_accuracy": _float_or_none(
            evaluation.get("decision_basis_accuracy")
        ),
    }


def _build_source_context_improved_cases(
    baseline_decisions: Sequence[Mapping[str, Any]],
    current_decisions: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    current_by_example_id = {
        str(item.get("example_id") or ""): item for item in current_decisions
    }
    cases: list[dict[str, Any]] = []
    for baseline in baseline_decisions:
        example_id = str(baseline.get("example_id") or "")
        current = current_by_example_id.get(example_id)
        if current is None:
            continue
        baseline_dispatch = _mapping(baseline.get("dispatch"))
        current_dispatch = _mapping(current.get("dispatch"))
        if not bool(baseline_dispatch.get("fallback_agent")):
            continue
        if bool(current_dispatch.get("fallback_agent")):
            continue
        cases.append(
            {
                "example_id": example_id,
                "case_id": str(baseline.get("case_id") or ""),
                "case_type": str(baseline.get("source_case_type") or ""),
                "recommended_action": str(
                    _mapping(current.get("action_router")).get(
                        "recommended_action",
                    )
                    or ""
                ),
                "source_dependency": str(
                    _mapping(current.get("source_dependency_router")).get(
                        "recommended_source_dependency",
                    )
                    or ""
                ),
                "removed_fallback_reasons": _list_difference(
                    baseline_dispatch.get("fallback_reasons"),
                    current_dispatch.get("fallback_reasons"),
                ),
                "removed_data_gap_tags": _list_difference(
                    baseline_dispatch.get("data_gap_tags"),
                    current_dispatch.get("data_gap_tags"),
                ),
                "source_context": dict(_mapping(current.get("source_context"))),
            }
        )
    return sorted(cases, key=lambda item: (item["case_type"], item["case_id"]))


def _build_remaining_source_context_gap_cases(
    decisions: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for decision in decisions:
        dispatch = _mapping(decision.get("dispatch"))
        data_gap_tags = dispatch.get("data_gap_tags")
        if "no_source_context_for_required_source" not in _string_list(data_gap_tags):
            continue
        cases.append(
            {
                "example_id": str(decision.get("example_id") or ""),
                "case_id": str(decision.get("case_id") or ""),
                "case_type": str(decision.get("source_case_type") or ""),
                "recommended_action": str(
                    _mapping(decision.get("action_router")).get(
                        "recommended_action",
                    )
                    or ""
                ),
                "source_dependency": str(
                    _mapping(decision.get("source_dependency_router")).get(
                        "recommended_source_dependency",
                    )
                    or ""
                ),
                "data_gap_tags": _string_list(data_gap_tags),
            }
        )
    return sorted(cases, key=lambda item: (item["case_type"], item["case_id"]))


def _data_gap_count(report: Mapping[str, Any], tag: str) -> int:
    return int(
        _mapping(_mapping(report.get("summary")).get("data_gap_counts")).get(tag)
        or 0
    )


def _fallback_agent_count(report: Mapping[str, Any]) -> int:
    return int(_mapping(report.get("summary")).get("fallback_agent_count") or 0)


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
    source_context_router: Mapping[str, Any],
) -> list[dict[str, Any]]:
    source_best = _mapping(source_dependency.get("best_policy"))
    source_context_delta = _mapping(source_context_router.get("delta"))
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
        {
            "task": "dry_run_dispatch",
            "best_policy": "tiny_model_with_source_context_signals",
            "baseline_policy": "tiny_model_without_source_context_signals",
            "primary_metric": "fallback_agent_count_reduction",
            "primary_accuracy": int(
                source_context_delta.get("fallback_agent_count_reduction") or 0
            ),
            "secondary_metric": "no_source_context_gap_reduction",
            "secondary_accuracy": int(
                source_context_delta.get(
                    "no_source_context_for_required_source_reduction",
                )
                or 0
            ),
            "mismatch_count": 0,
            "gate_passed": bool(
                source_context_router.get("status")
                != "no_source_context_signals"
            ),
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


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if isinstance(item, Mapping):
            records.append(dict(item))
    return records


def _list_difference(old_value: Any, new_value: Any) -> list[str]:
    new_items = set(_string_list(new_value))
    return [item for item in _string_list(old_value) if item not in new_items]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value]


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
