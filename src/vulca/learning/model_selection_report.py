"""Model and agent selection report for tiny learning policies."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.layers.decompose_cases import CASE_TYPE as DECOMPOSE_CASE_TYPE
from vulca.layers.layer_generate_cases import CASE_TYPE as LAYER_GENERATE_CASE_TYPE
from vulca.layers.redraw_cases import CASE_TYPE as REDRAW_CASE_TYPE
from vulca.learning.tiny_action_model import POLICY_TINY_ACTION_MODEL
from vulca.learning.tiny_baseline_model import POLICY_TINY_AGENT
from vulca.learning.tiny_dataset import DATASET_SPLITS
from vulca.learning.training_effectiveness import (
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    DEFAULT_OUTPUT_DIR as EFFECTIVENESS_OUTPUT_DIR,
    run_training_effectiveness_report,
)


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_model_selection_report"
DEFAULT_OUTPUT_DIR = Path("build/model_selection_report")
DEFAULT_REPORT_NAME = "model_selection_report.json"
POLICY_MAJORITY_ACTION = "majority_action"
POLICY_REDRAW_OBSERVABLE_SIGNAL = "redraw_observable_signal"
WORKLOAD_TRACKS: Mapping[str, str] = {
    REDRAW_CASE_TYPE: "redraw_router_specialist_v1",
    DECOMPOSE_CASE_TYPE: "decompose_action_specialist_v1",
    LAYER_GENERATE_CASE_TYPE: "layer_generate_action_specialist_v1",
}
POLICY_FAMILIES: Mapping[str, str] = {
    POLICY_TINY_ACTION_MODEL: "trained_sparse_action_model",
    POLICY_TINY_AGENT: "agent_baseline",
    POLICY_REDRAW_OBSERVABLE_SIGNAL: "observable_signal_router",
    POLICY_MAJORITY_ACTION: "train_split_majority_baseline",
}


def run_model_selection_report(
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
    """Build a stable selection report over current tiny policies and workloads."""
    _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")
    if min_workload_eval_examples < 0:
        raise ValueError("min_workload_eval_examples must be >= 0")

    root = Path(repo_root).resolve()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    effectiveness_output = output / "training_effectiveness"
    effectiveness_report = run_training_effectiveness_report(
        repo_root=root,
        output_dir=effectiveness_output,
        case_source_manifest_path=case_source_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
        min_eval_examples_per_bucket=min_eval_examples_per_bucket,
    )
    aggregated_report_path = Path(
        str(effectiveness_report["artifacts"]["aggregated_report_path"])
    )
    aggregated_report = json.loads(aggregated_report_path.read_text(encoding="utf-8"))

    selection = _build_selection(effectiveness_report)
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": _selection_status(effectiveness_report),
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
            "training_effectiveness_report_path": effectiveness_report["artifacts"][
                "report_path"
            ],
            "aggregated_report_path": str(aggregated_report_path),
            "dataset_path": effectiveness_report["artifacts"]["dataset_path"],
            "comparison_report_path": effectiveness_report["artifacts"][
                "comparison_report_path"
            ],
        },
        "dataset": {
            "example_count": int(effectiveness_report["dataset"]["example_count"]),
            "eval_example_count": int(
                effectiveness_report["dataset"]["eval_example_count"]
            ),
            "data_gap_count": len(effectiveness_report["data_gaps"]),
            "counts_by_source_kind": dict(
                _mapping(effectiveness_report["dataset"]["counts_by_source_kind"])
            ),
        },
        "selection": selection,
        "candidate_policies": _candidate_policies(aggregated_report, selection),
        "workload_recommendations": _workload_recommendations(
            aggregated_report,
            min_eval_examples=min_workload_eval_examples,
        ),
        "data_readiness": {
            "status": effectiveness_report["status"],
            "gate_passed": bool(effectiveness_report["effectiveness"]["gate_passed"]),
            "coverage_complete": not effectiveness_report["data_gaps"],
            "data_gaps": list(effectiveness_report["data_gaps"]),
        },
    }

    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _build_selection(effectiveness_report: Mapping[str, Any]) -> dict[str, Any]:
    effectiveness = _mapping(effectiveness_report.get("effectiveness"))
    gate_passed = bool(effectiveness.get("gate_passed"))
    data_gap_count = len(effectiveness_report.get("data_gaps", []) or [])
    action_accuracy = _float_or_none(effectiveness.get("action_accuracy"))
    baseline_accuracy = _float_or_none(effectiveness.get("baseline_action_accuracy"))
    delta = _float_or_none(effectiveness.get("accuracy_delta_vs_baseline"))
    primary = str(effectiveness.get("evaluated_policy") or POLICY_TINY_ACTION_MODEL)
    baseline = str(effectiveness.get("baseline_policy") or POLICY_TINY_AGENT)

    return {
        "recommended_primary_policy": primary if gate_passed else "",
        "recommended_baseline_policy": baseline,
        "primary_action_accuracy": action_accuracy,
        "baseline_action_accuracy": baseline_accuracy,
        "accuracy_delta_vs_baseline": delta,
        "requires_more_data_before_training": bool(data_gap_count),
        "reason": _selection_reason(
            gate_passed=gate_passed,
            data_gap_count=data_gap_count,
            primary=primary,
            action_accuracy=action_accuracy,
            baseline=baseline,
            baseline_accuracy=baseline_accuracy,
            delta=delta,
        ),
    }


def _candidate_policies(
    aggregated_report: Mapping[str, Any],
    selection: Mapping[str, Any],
) -> list[dict[str, Any]]:
    reports = _mapping(
        _mapping(aggregated_report.get("policy_comparison")).get("policy_reports")
    )
    rows: list[dict[str, Any]] = []
    for policy_name, report_value in sorted(reports.items()):
        report = _mapping(report_value)
        rows.append(
            {
                "policy_name": str(policy_name),
                "family": POLICY_FAMILIES.get(str(policy_name), "external_policy"),
                "decision": _policy_decision(str(policy_name), report, selection),
                "example_count": int(report.get("example_count") or 0),
                "evaluated_count": int(report.get("evaluated_count") or 0),
                "skipped_count": int(report.get("skipped_count") or 0),
                "action_accuracy": _float_or_none(report.get("action_accuracy")),
                "mismatch_count": int(report.get("mismatch_count") or 0),
                "missing_count": int(report.get("missing_count") or 0)
                if "missing_count" in report
                else None,
            }
        )
    return sorted(
        rows,
        key=lambda item: (
            _decision_rank(str(item["decision"])),
            -(item["action_accuracy"] or -1.0),
            int(item["mismatch_count"] or 0),
            str(item["policy_name"]),
        ),
    )


def _workload_recommendations(
    aggregated_report: Mapping[str, Any],
    *,
    min_eval_examples: int,
) -> list[dict[str, Any]]:
    bucket_metrics = _mapping(aggregated_report.get("bucket_metrics"))
    case_type_metrics = _mapping(bucket_metrics.get("source_case.case_type"))
    rows: list[dict[str, Any]] = []
    for case_type, metrics_value in sorted(case_type_metrics.items()):
        metrics = _mapping(metrics_value)
        policy_reports = _mapping(metrics.get("policy_reports"))
        ranked = _rank_policy_reports(policy_reports)
        best = ranked[0] if ranked else {}
        secondary = _secondary_policy(case_type=str(case_type), ranked=ranked)
        eval_count = int(metrics.get("eval_example_count") or 0)
        rows.append(
            {
                "case_type": str(case_type),
                "recommended_track": WORKLOAD_TRACKS.get(
                    str(case_type),
                    f"{case_type}_specialist_v1",
                ),
                "best_policy": str(best.get("policy_name") or ""),
                "secondary_policy": secondary,
                "eval_example_count": eval_count,
                "best_action_accuracy": _float_or_none(best.get("action_accuracy")),
                "decision": _workload_decision(
                    case_type=str(case_type),
                    eval_count=eval_count,
                    min_eval_examples=min_eval_examples,
                    secondary_policy=secondary,
                ),
                "policy_ranking": ranked,
            }
        )
    return rows


def _rank_policy_reports(policy_reports: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for policy_name, report_value in policy_reports.items():
        report = _mapping(report_value)
        accuracy = _float_or_none(report.get("action_accuracy"))
        evaluated_count = int(report.get("evaluated_count") or 0)
        if accuracy is None or evaluated_count <= 0:
            continue
        rows.append(
            {
                "policy_name": str(policy_name),
                "action_accuracy": accuracy,
                "mismatch_count": int(report.get("mismatch_count") or 0),
                "evaluated_count": evaluated_count,
                "missing_count": int(report.get("missing_count") or 0)
                if "missing_count" in report
                else None,
            }
        )
    return sorted(
        rows,
        key=lambda item: (
            -(item["action_accuracy"] or -1.0),
            int(item["mismatch_count"] or 0),
            -int(item["evaluated_count"] or 0),
            str(item["policy_name"]),
        ),
    )


def _selection_status(effectiveness_report: Mapping[str, Any]) -> str:
    effectiveness = _mapping(effectiveness_report.get("effectiveness"))
    if not effectiveness.get("gate_passed"):
        return "blocked_by_gate"
    if effectiveness_report.get("data_gaps"):
        return "blocked_by_data_gaps"
    return "ready_for_selection"


def _selection_reason(
    *,
    gate_passed: bool,
    data_gap_count: int,
    primary: str,
    action_accuracy: float | None,
    baseline: str,
    baseline_accuracy: float | None,
    delta: float | None,
) -> str:
    if not gate_passed:
        return "current primary policy failed the tiny training gate"
    if data_gap_count:
        return f"{data_gap_count} eval coverage gaps remain before selection"
    return (
        f"{primary} is selected because action_accuracy={action_accuracy} "
        f"beats {baseline} action_accuracy={baseline_accuracy} by {delta}"
    )


def _policy_decision(
    policy_name: str,
    report: Mapping[str, Any],
    selection: Mapping[str, Any],
) -> str:
    if policy_name == selection.get("recommended_primary_policy"):
        if report.get("action_accuracy") == 1.0 and int(report.get("mismatch_count") or 0) == 0:
            return "promote_primary"
        return "candidate_primary"
    if policy_name == POLICY_TINY_AGENT:
        return "keep_agent_baseline"
    if policy_name == POLICY_REDRAW_OBSERVABLE_SIGNAL:
        return "keep_redraw_guardrail"
    if policy_name == POLICY_MAJORITY_ACTION:
        return "reject_baseline"
    return "observe"


def _workload_decision(
    *,
    case_type: str,
    eval_count: int,
    min_eval_examples: int,
    secondary_policy: str,
) -> str:
    if case_type == REDRAW_CASE_TYPE and secondary_policy == POLICY_REDRAW_OBSERVABLE_SIGNAL:
        return "promote_with_guardrail"
    if eval_count < min_eval_examples:
        return "collect_more_real_cases"
    return "promote_current_policy"


def _secondary_policy(*, case_type: str, ranked: Sequence[Mapping[str, Any]]) -> str:
    if case_type == REDRAW_CASE_TYPE:
        for row in ranked:
            if row.get("policy_name") == POLICY_REDRAW_OBSERVABLE_SIGNAL:
                return POLICY_REDRAW_OBSERVABLE_SIGNAL
    for row in ranked:
        policy_name = str(row.get("policy_name") or "")
        if policy_name not in {POLICY_TINY_ACTION_MODEL, POLICY_MAJORITY_ACTION}:
            return policy_name
    return ""


def _decision_rank(decision: str) -> int:
    order = {
        "promote_primary": 0,
        "candidate_primary": 1,
        "keep_redraw_guardrail": 2,
        "keep_agent_baseline": 3,
        "observe": 4,
        "reject_baseline": 5,
    }
    return order.get(decision, 9)


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
