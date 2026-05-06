"""Canonical provider-free tiny training/eval gate."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.learning.seed_cases import DEFAULT_SEED_MANIFEST
from vulca.learning.tiny_action_model import (
    POLICY_TINY_ACTION_MODEL,
    write_tiny_action_model_predictions,
)
from vulca.learning.tiny_baseline_model import (
    POLICY_TINY_AGENT,
    write_tiny_baseline_predictions,
)
from vulca.learning.tiny_dataset import (
    DATASET_SPLITS,
    build_tiny_dataset_comparison_report,
    load_tiny_dataset_examples,
    write_tiny_dataset,
)
from vulca.learning.tiny_feature_ablation import run_tiny_feature_ablation_report_for_dataset


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_tiny_training_eval_gate_report"
DEFAULT_OUTPUT_DIR = Path("build/tiny_training_eval_gate")
DEFAULT_MANUAL_CURATED_CASE_SOURCE_MANIFEST = Path(
    "docs/benchmarks/learning/manual_curated_case_source_manifest_v1.json"
)
DEFAULT_MIN_ACTION_ACCURACY: Mapping[str, float] = {
    POLICY_TINY_ACTION_MODEL: 1.0,
}
DEFAULT_MAX_MISMATCHES: Mapping[str, int] = {
    POLICY_TINY_ACTION_MODEL: 0,
}


def run_tiny_training_eval_gate(
    *,
    repo_root: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    manifest_path: str | Path | None = DEFAULT_SEED_MANIFEST,
    case_log_paths: Sequence[str | Path] = (),
    case_source_manifest_path: str | Path | None = DEFAULT_MANUAL_CURATED_CASE_SOURCE_MANIFEST,
    auxiliary_signal_manifest_path: str | Path | None = None,
    include_local_seeds: bool = True,
    eval_split: str = "test",
    train_split: str = "train",
    min_action_accuracy: Mapping[str, float] | None = None,
    min_ablation_action_accuracy: Mapping[str, float] | None = None,
    max_mismatches: Mapping[str, int] | None = None,
    require_no_missing_predictions: bool = True,
) -> dict[str, Any]:
    """Export the tiny dataset, run fixed predictors, compare them, and gate."""
    _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")

    root = Path(repo_root)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    dataset_path = output / "tiny_dataset.jsonl"
    tiny_agent_path = output / "tiny_agent_v0.predictions.jsonl"
    tiny_action_model_path = output / "tiny_action_model_v1.predictions.jsonl"
    comparison_report_path = output / "tiny_dataset_comparison.json"
    ablation_report_path = output / "tiny_feature_ablation.json"
    resolved_report_path = Path(report_path) if report_path else output / "tiny_training_eval_report.json"
    resolved_manifest_path = manifest_path or DEFAULT_SEED_MANIFEST

    resolved_case_source_manifest = _resolve_optional_repo_path(
        root,
        case_source_manifest_path,
    )
    dataset_result = write_tiny_dataset(
        repo_root=root,
        output_path=dataset_path,
        manifest_path=resolved_manifest_path,
        case_log_paths=case_log_paths,
        case_source_manifest_path=resolved_case_source_manifest,
        auxiliary_signal_manifest_path=auxiliary_signal_manifest_path,
        include_local_seeds=include_local_seeds,
    )
    tiny_agent_result = write_tiny_baseline_predictions(
        dataset_path=dataset_path,
        output_path=tiny_agent_path,
        policy_name=POLICY_TINY_AGENT,
        split=eval_split,
        train_split=train_split,
    )
    tiny_action_model_result = write_tiny_action_model_predictions(
        dataset_path=dataset_path,
        output_path=tiny_action_model_path,
        split=eval_split,
        train_split=train_split,
    )
    comparison_report = build_tiny_dataset_comparison_report(
        load_tiny_dataset_examples(dataset_path),
        train_split=train_split,
        eval_split=eval_split,
        prediction_paths=(tiny_agent_path, tiny_action_model_path),
    )
    comparison_report_path.write_text(
        json.dumps(comparison_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    ablation_report = run_tiny_feature_ablation_report_for_dataset(
        dataset_path=dataset_path,
        output_path=ablation_report_path,
        eval_split=eval_split,
        train_split=train_split,
    )

    min_thresholds = dict(DEFAULT_MIN_ACTION_ACCURACY)
    min_thresholds.update(min_action_accuracy or {})
    max_thresholds = dict(DEFAULT_MAX_MISMATCHES)
    max_thresholds.update(max_mismatches or {})
    gate = build_tiny_training_eval_gate_result(
        comparison_report,
        ablation_report=ablation_report,
        min_action_accuracy=min_thresholds,
        min_ablation_action_accuracy=min_ablation_action_accuracy or {},
        max_mismatches=max_thresholds,
        require_no_missing_predictions=require_no_missing_predictions,
    )

    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "train_split": train_split,
        "eval_split": eval_split,
        "inputs": {
            "repo_root": str(root),
            "source_manifest": str(resolved_manifest_path),
            "case_log_paths": [str(path) for path in case_log_paths],
            "case_source_manifest_path": str(resolved_case_source_manifest or ""),
            "auxiliary_signal_manifest_path": str(auxiliary_signal_manifest_path or ""),
            "include_local_seeds": bool(include_local_seeds),
        },
        "artifacts": {
            "dataset_path": str(dataset_path),
            "dataset_index_path": dataset_result.index_path,
            "tiny_agent_v0_prediction_path": str(tiny_agent_path),
            "tiny_action_model_v1_prediction_path": str(tiny_action_model_path),
            "comparison_report_path": str(comparison_report_path),
            "tiny_feature_ablation_report_path": str(ablation_report_path),
            "report_path": str(resolved_report_path),
        },
        "dataset": asdict(dataset_result),
        "predictions": {
            POLICY_TINY_AGENT: asdict(tiny_agent_result),
            POLICY_TINY_ACTION_MODEL: asdict(tiny_action_model_result),
        },
        "comparison": comparison_report,
        "ablation": ablation_report,
        "gate": gate,
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def build_tiny_training_eval_gate_result(
    comparison_report: Mapping[str, Any],
    *,
    ablation_report: Mapping[str, Any] | None = None,
    min_action_accuracy: Mapping[str, float],
    min_ablation_action_accuracy: Mapping[str, float] | None = None,
    max_mismatches: Mapping[str, int],
    require_no_missing_predictions: bool = True,
) -> dict[str, Any]:
    policy_reports = _mapping(comparison_report.get("policy_reports"))
    ablation_by_variant = _ablation_variants_by_id(ablation_report or {})
    violations: list[dict[str, Any]] = []

    for policy, threshold in sorted(min_action_accuracy.items()):
        metrics = _mapping(policy_reports.get(policy))
        actual = metrics.get("action_accuracy")
        if actual is None or float(actual) < float(threshold):
            violations.append(
                {
                    "policy": str(policy),
                    "metric": "action_accuracy",
                    "actual": actual,
                    "expected": f">= {_format_number(float(threshold))}",
                }
            )

    for variant, threshold in sorted((min_ablation_action_accuracy or {}).items()):
        metrics = _mapping(_mapping(ablation_by_variant.get(variant)).get("policy_report"))
        actual = metrics.get("action_accuracy")
        if actual is None or float(actual) < float(threshold):
            violations.append(
                {
                    "policy": POLICY_TINY_ACTION_MODEL,
                    "variant": str(variant),
                    "metric": "ablation_action_accuracy",
                    "actual": actual,
                    "expected": f">= {_format_number(float(threshold))}",
                }
            )

    for policy, threshold in sorted(max_mismatches.items()):
        metrics = _mapping(policy_reports.get(policy))
        actual = metrics.get("mismatch_count")
        if actual is None or int(actual) > int(threshold):
            violations.append(
                {
                    "policy": str(policy),
                    "metric": "mismatch_count",
                    "actual": actual,
                    "expected": f"<= {int(threshold)}",
                }
            )

    if require_no_missing_predictions:
        for policy, metrics_value in sorted(policy_reports.items()):
            metrics = _mapping(metrics_value)
            if "missing_count" not in metrics:
                continue
            actual = int(metrics.get("missing_count") or 0)
            if actual > 0:
                violations.append(
                    {
                        "policy": str(policy),
                        "metric": "missing_count",
                        "actual": actual,
                        "expected": "== 0",
                    }
                )

    return {
        "passed": not violations,
        "thresholds": {
            "min_action_accuracy": {
                policy: float(value)
                for policy, value in sorted(min_action_accuracy.items())
            },
            "min_ablation_action_accuracy": {
                variant: float(value)
                for variant, value in sorted((min_ablation_action_accuracy or {}).items())
            },
            "max_mismatches": {
                policy: int(value) for policy, value in sorted(max_mismatches.items())
            },
            "require_no_missing_predictions": bool(require_no_missing_predictions),
        },
        "violations": violations,
    }


def parse_policy_float_thresholds(values: Sequence[str]) -> dict[str, float]:
    thresholds: dict[str, float] = {}
    for raw in values:
        policy, value = _split_policy_threshold(raw)
        try:
            thresholds[policy] = float(value)
        except ValueError as exc:
            raise ValueError(
                f"invalid threshold value {value!r} for policy {policy!r}"
            ) from exc
    return thresholds


def parse_policy_int_thresholds(values: Sequence[str]) -> dict[str, int]:
    thresholds: dict[str, int] = {}
    for raw in values:
        policy, value = _split_policy_threshold(raw)
        try:
            number = float(value)
        except ValueError as exc:
            raise ValueError(
                f"invalid threshold value {value!r} for policy {policy!r}"
            ) from exc
        count = int(number)
        if count != number:
            raise ValueError(
                f"integer threshold required for policy {policy!r}: {value!r}"
            )
        thresholds[policy] = count
    return thresholds


def format_gate_violation(violation: Mapping[str, Any]) -> str:
    policy = str(violation.get("policy") or "")
    metric = str(violation.get("metric") or "")
    actual = violation.get("actual")
    expected = str(violation.get("expected") or "")
    if metric == "action_accuracy":
        threshold = expected.replace(">= ", "")
        return f"{policy} action_accuracy {actual} < {threshold}"
    if metric == "mismatch_count":
        threshold = expected.replace("<= ", "")
        return f"{policy} mismatch_count {actual} > {threshold}"
    if metric == "missing_count":
        return f"{policy} missing_count {actual} > 0"
    if metric == "ablation_action_accuracy":
        variant = str(violation.get("variant") or "")
        threshold = expected.replace(">= ", "")
        return f"{policy} {variant} action_accuracy {actual} < {threshold}"
    return f"{policy} {metric} {actual} violates {expected}"


def parse_variant_float_thresholds(values: Sequence[str]) -> dict[str, float]:
    thresholds: dict[str, float] = {}
    for raw in values:
        variant, value = _split_policy_threshold(raw)
        try:
            thresholds[variant] = float(value)
        except ValueError as exc:
            raise ValueError(
                f"invalid threshold value {value!r} for variant {variant!r}"
            ) from exc
    return thresholds


def _split_policy_threshold(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise ValueError(f"invalid tiny gate threshold {raw!r}; expected POLICY=VALUE")
    policy, value = raw.split("=", 1)
    policy = policy.strip()
    value = value.strip()
    if not policy:
        raise ValueError(f"invalid tiny gate threshold {raw!r}; policy is required")
    if not value:
        raise ValueError(f"invalid tiny gate threshold {raw!r}; value is required")
    return policy, value


def _resolve_optional_repo_path(
    repo_root: Path,
    path: str | Path | None,
) -> Path | None:
    if not path:
        return None
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = repo_root / resolved
    return resolved


def _validate_split(value: str, *, label: str) -> None:
    if value not in DATASET_SPLITS:
        raise ValueError(f"unsupported {label} {value!r}; expected one of {DATASET_SPLITS}")


def _format_number(value: float) -> str:
    if value.is_integer():
        return f"{value:.1f}"
    return str(value)


def _ablation_variants_by_id(
    ablation_report: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    variants = ablation_report.get("variant_reports")
    if not isinstance(variants, Sequence) or isinstance(variants, (str, bytes)):
        return {}
    return {
        str(_mapping(item).get("variant_id") or ""): _mapping(item)
        for item in variants
        if isinstance(item, Mapping)
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
