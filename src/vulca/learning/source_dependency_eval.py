"""Provider-free evaluation for source-dependency labels."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from vulca.learning.seed_cases import DEFAULT_SEED_MANIFEST
from vulca.learning.tiny_dataset import (
    DATASET_SPLITS,
    load_tiny_dataset_examples,
    write_tiny_dataset,
)


SCHEMA_VERSION = 1
EVAL_REPORT_CASE_TYPE = "learning_source_dependency_eval_report"
COMPARISON_REPORT_CASE_TYPE = "learning_source_dependency_comparison_report"
RUN_REPORT_CASE_TYPE = "learning_source_dependency_eval_run_report"
DEFAULT_OUTPUT_DIR = Path("build/source_dependency_eval")
DEFAULT_CASE_SOURCE_MANIFEST = Path(
    "docs/benchmarks/learning/combined_case_source_manifest_v1.json"
)
DEFAULT_SOURCE_DEPENDENCY_MANIFEST = Path(
    "docs/benchmarks/learning/real_source_dependency_label_manifest_v1.json"
)

POLICY_SOURCE_DEPENDENCY_MAJORITY = "source_dependency_majority"
POLICY_SOURCE_DEPENDENCY_RULE = "source_dependency_rule_v1"
POLICY_SOURCE_DEPENDENCY_ORACLE = "source_dependency_label_oracle"
SOURCE_DEPENDENCY_POLICIES: frozenset[str] = frozenset(
    {
        POLICY_SOURCE_DEPENDENCY_MAJORITY,
        POLICY_SOURCE_DEPENDENCY_RULE,
        POLICY_SOURCE_DEPENDENCY_ORACLE,
    }
)
DEFAULT_POLICY_NAMES: tuple[str, ...] = (
    POLICY_SOURCE_DEPENDENCY_MAJORITY,
    POLICY_SOURCE_DEPENDENCY_RULE,
)
DEFAULT_MIN_DEPENDENCY_ACCURACY: Mapping[str, float] = {
    POLICY_SOURCE_DEPENDENCY_RULE: 1.0,
}
DEFAULT_MAX_MISMATCHES: Mapping[str, int] = {
    POLICY_SOURCE_DEPENDENCY_RULE: 0,
}


@dataclass(frozen=True)
class SourceDependencyPrediction:
    source_dependency: str
    decision_basis: str
    rule_reason: str
    confidence: float


def run_source_dependency_eval(
    *,
    repo_root: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    manifest_path: str | Path | None = DEFAULT_SEED_MANIFEST,
    case_log_paths: Sequence[str | Path] = (),
    case_source_manifest_path: str | Path | None = DEFAULT_CASE_SOURCE_MANIFEST,
    source_dependency_manifest_path: str | Path | None = DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
    include_local_seeds: bool = True,
    eval_split: str | None = None,
    train_split: str = "train",
    policy_names: Sequence[str] = DEFAULT_POLICY_NAMES,
    min_dependency_accuracy: Mapping[str, float] | None = None,
    max_mismatches: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    """Export a source-dependency dataset and evaluate provider-free policies."""
    if eval_split is not None:
        _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")
    if source_dependency_manifest_path is None:
        raise ValueError("source_dependency_manifest_path is required")

    root = Path(repo_root)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    dataset_path = output / "tiny_dataset.with_source_dependency.jsonl"
    comparison_report_path = output / "source_dependency_comparison.json"
    resolved_report_path = (
        Path(report_path)
        if report_path
        else output / "source_dependency_eval_report.json"
    )
    resolved_case_source_manifest = _resolve_optional_repo_path(
        root,
        case_source_manifest_path,
    )
    resolved_source_dependency_manifest = _resolve_optional_repo_path(
        root,
        source_dependency_manifest_path,
    )
    dataset_result = write_tiny_dataset(
        repo_root=root,
        output_path=dataset_path,
        manifest_path=manifest_path or DEFAULT_SEED_MANIFEST,
        case_log_paths=case_log_paths,
        case_source_manifest_path=resolved_case_source_manifest,
        source_dependency_manifest_path=resolved_source_dependency_manifest,
        include_local_seeds=include_local_seeds,
    )
    examples = load_tiny_dataset_examples(dataset_path)
    comparison = build_source_dependency_comparison_report(
        examples,
        train_split=train_split,
        eval_split=eval_split,
        policy_names=policy_names,
    )
    comparison_report_path.write_text(
        json.dumps(comparison, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    min_thresholds = dict(DEFAULT_MIN_DEPENDENCY_ACCURACY)
    min_thresholds.update(min_dependency_accuracy or {})
    max_thresholds = dict(DEFAULT_MAX_MISMATCHES)
    max_thresholds.update(max_mismatches or {})
    gate = build_source_dependency_eval_gate_result(
        comparison,
        min_dependency_accuracy=min_thresholds,
        max_mismatches=max_thresholds,
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": RUN_REPORT_CASE_TYPE,
        "train_split": train_split,
        "eval_split": eval_split or "all",
        "inputs": {
            "repo_root": str(root),
            "source_manifest": str(manifest_path or DEFAULT_SEED_MANIFEST),
            "case_log_paths": [str(path) for path in case_log_paths],
            "case_source_manifest_path": str(resolved_case_source_manifest or ""),
            "source_dependency_manifest_path": str(
                resolved_source_dependency_manifest or ""
            ),
            "include_local_seeds": bool(include_local_seeds),
        },
        "artifacts": {
            "dataset_path": str(dataset_path),
            "dataset_index_path": dataset_result.index_path,
            "comparison_report_path": str(comparison_report_path),
            "report_path": str(resolved_report_path),
        },
        "dataset": {
            **asdict(dataset_result),
            "source_dependency_labeled_count": _source_dependency_labeled_count(
                examples,
                eval_split=eval_split,
            ),
        },
        "comparison": comparison,
        "gate": gate,
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def evaluate_source_dependency_policy(
    examples: Iterable[Mapping[str, Any]],
    *,
    policy_name: str = POLICY_SOURCE_DEPENDENCY_RULE,
    dataset_split: str | None = None,
    train_split: str = "train",
) -> dict[str, Any]:
    """Evaluate one source-dependency policy on exported tiny dataset examples."""
    if policy_name not in SOURCE_DEPENDENCY_POLICIES:
        raise ValueError(
            f"unsupported source dependency policy {policy_name!r}; "
            f"expected one of {sorted(SOURCE_DEPENDENCY_POLICIES)}"
        )
    all_items = list(examples)
    items = _filter_by_split(all_items, dataset_split)
    majority = _majority_prediction(all_items, train_split=train_split)

    dependency_total = 0
    dependency_correct = 0
    decision_basis_total = 0
    decision_basis_correct = 0
    skipped_count = 0
    mismatches: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []

    for example in items:
        targets = _mapping(example.get("targets"))
        target_dependency = str(targets.get("source_dependency") or "")
        target_basis = str(targets.get("source_decision_basis") or "")
        if not target_dependency:
            skipped_count += 1
            continue

        prediction = _predict_source_dependency(
            example,
            policy_name=policy_name,
            majority=majority,
        )
        recommendation = _recommendation_record(
            example,
            prediction=prediction,
            target_dependency=target_dependency,
            target_basis=target_basis,
        )
        recommendations.append(recommendation)

        has_mismatch = False
        dependency_total += 1
        if prediction.source_dependency == target_dependency:
            dependency_correct += 1
        else:
            has_mismatch = True

        if target_basis:
            decision_basis_total += 1
            if prediction.decision_basis == target_basis:
                decision_basis_correct += 1
            else:
                has_mismatch = True

        if has_mismatch:
            mismatches.append(recommendation)

    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": EVAL_REPORT_CASE_TYPE,
        "policy_name": policy_name,
        "split": dataset_split or "all",
        "example_count": len(items),
        "evaluated_count": dependency_total,
        "skipped_count": skipped_count,
        "dependency_labeled_count": dependency_total,
        "dependency_accuracy": _ratio(dependency_correct, dependency_total),
        "decision_basis_labeled_count": decision_basis_total,
        "decision_basis_accuracy": _ratio(
            decision_basis_correct,
            decision_basis_total,
        ),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "recommendations": recommendations,
        "counts_by_target_source_dependency": _target_counts(
            recommendations,
            "target_source_dependency",
        ),
        "counts_by_recommended_source_dependency": _target_counts(
            recommendations,
            "recommended_source_dependency",
        ),
    }


def build_source_dependency_comparison_report(
    examples: Iterable[Mapping[str, Any]],
    *,
    train_split: str = "train",
    eval_split: str | None = None,
    policy_names: Sequence[str] = DEFAULT_POLICY_NAMES,
) -> dict[str, Any]:
    """Compare source-dependency policies on a fixed dataset split."""
    items = list(examples)
    reports = {
        policy: evaluate_source_dependency_policy(
            items,
            policy_name=policy,
            dataset_split=eval_split,
            train_split=train_split,
        )
        for policy in policy_names
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": COMPARISON_REPORT_CASE_TYPE,
        "train_split": train_split,
        "eval_split": eval_split or "all",
        "example_count": len(_filter_by_split(items, eval_split)),
        "source_dependency_labeled_count": _source_dependency_labeled_count(
            items,
            eval_split=eval_split,
        ),
        "policy_reports": reports,
        "ranked_policies": _rank_policy_reports(reports),
    }


def build_source_dependency_eval_gate_result(
    comparison_report: Mapping[str, Any],
    *,
    min_dependency_accuracy: Mapping[str, float],
    max_mismatches: Mapping[str, int],
) -> dict[str, Any]:
    """Check source-dependency eval thresholds."""
    policy_reports = _mapping(comparison_report.get("policy_reports"))
    violations: list[dict[str, Any]] = []
    for policy, threshold in sorted(min_dependency_accuracy.items()):
        metrics = _mapping(policy_reports.get(policy))
        actual = metrics.get("dependency_accuracy")
        if actual is None or float(actual) < float(threshold):
            violations.append(
                {
                    "policy": str(policy),
                    "metric": "dependency_accuracy",
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
    return {
        "passed": not violations,
        "thresholds": {
            "min_dependency_accuracy": {
                policy: float(value)
                for policy, value in sorted(min_dependency_accuracy.items())
            },
            "max_mismatches": {
                policy: int(value) for policy, value in sorted(max_mismatches.items())
            },
        },
        "violations": violations,
    }


def format_source_dependency_gate_violation(violation: Mapping[str, Any]) -> str:
    policy = str(violation.get("policy") or "")
    metric = str(violation.get("metric") or "")
    actual = violation.get("actual")
    expected = str(violation.get("expected") or "")
    if metric == "dependency_accuracy":
        threshold = expected.replace(">= ", "")
        return f"{policy} dependency_accuracy {actual} < {threshold}"
    if metric == "mismatch_count":
        threshold = expected.replace("<= ", "")
        return f"{policy} mismatch_count {actual} > {threshold}"
    return f"{policy} {metric} {actual} violates {expected}"


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


def _predict_source_dependency(
    example: Mapping[str, Any],
    *,
    policy_name: str,
    majority: SourceDependencyPrediction,
) -> SourceDependencyPrediction:
    if policy_name == POLICY_SOURCE_DEPENDENCY_ORACLE:
        targets = _mapping(example.get("targets"))
        return SourceDependencyPrediction(
            source_dependency=str(targets.get("source_dependency") or ""),
            decision_basis=str(targets.get("source_decision_basis") or ""),
            rule_reason="label_oracle",
            confidence=1.0,
        )
    if policy_name == POLICY_SOURCE_DEPENDENCY_MAJORITY:
        return majority
    return _rule_prediction(example)


def _rule_prediction(example: Mapping[str, Any]) -> SourceDependencyPrediction:
    source_case = _mapping(example.get("source_case"))
    targets = _mapping(example.get("targets"))
    case_type = str(source_case.get("case_type") or "")
    failure_type = str(targets.get("failure_type") or "")

    if failure_type == "provider_failure":
        return SourceDependencyPrediction(
            source_dependency="not_needed",
            decision_basis="metadata_only",
            rule_reason="provider_failure_metadata",
            confidence=0.9,
        )

    if case_type in {"redraw_case", "decompose_case"}:
        return SourceDependencyPrediction(
            source_dependency="required",
            decision_basis="image_source",
            rule_reason=f"{case_type}_visual_judgement",
            confidence=0.85,
        )

    return SourceDependencyPrediction(
        source_dependency="required",
        decision_basis="artifact_source",
        rule_reason="layer_generate_source_artifact_judgement",
        confidence=0.8,
    )


def _majority_prediction(
    examples: Sequence[Mapping[str, Any]],
    *,
    train_split: str,
) -> SourceDependencyPrediction:
    train_items = _labeled_items(_filter_by_split(examples, train_split))
    if not train_items:
        train_items = _labeled_items(examples)
    return SourceDependencyPrediction(
        source_dependency=_majority_value(
            _mapping(item.get("targets")).get("source_dependency") for item in train_items
        )
        or "required",
        decision_basis=_majority_value(
            _mapping(item.get("targets")).get("source_decision_basis")
            for item in train_items
        )
        or "artifact_source",
        rule_reason=f"majority_from_{train_split}",
        confidence=0.5,
    )


def _recommendation_record(
    example: Mapping[str, Any],
    *,
    prediction: SourceDependencyPrediction,
    target_dependency: str,
    target_basis: str,
) -> dict[str, Any]:
    source_case = _mapping(example.get("source_case"))
    targets = _mapping(example.get("targets"))
    return {
        "example_id": str(example.get("example_id") or ""),
        "case_id": str(source_case.get("case_id") or ""),
        "source_case_type": str(source_case.get("case_type") or ""),
        "failure_type": str(targets.get("failure_type") or ""),
        "preferred_action": str(targets.get("preferred_action") or ""),
        "target_source_dependency": target_dependency,
        "recommended_source_dependency": prediction.source_dependency,
        "target_decision_basis": target_basis,
        "recommended_decision_basis": prediction.decision_basis,
        "rule_reason": prediction.rule_reason,
        "confidence": prediction.confidence,
    }


def _rank_policy_reports(reports: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for policy_name, report in sorted(reports.items()):
        rows.append(
            {
                "policy_name": policy_name,
                "dependency_accuracy": report.get("dependency_accuracy"),
                "decision_basis_accuracy": report.get("decision_basis_accuracy"),
                "evaluated_count": int(report.get("evaluated_count") or 0),
                "mismatch_count": int(report.get("mismatch_count") or 0),
            }
        )
    return sorted(
        rows,
        key=lambda item: (
            -_sortable_accuracy(item.get("dependency_accuracy")),
            -_sortable_accuracy(item.get("decision_basis_accuracy")),
            -int(item["evaluated_count"]),
            int(item["mismatch_count"]),
            str(item["policy_name"]),
        ),
    )


def _filter_by_split(
    examples: Sequence[Mapping[str, Any]],
    split: str | None,
) -> list[Mapping[str, Any]]:
    if not split:
        return list(examples)
    return [item for item in examples if str(item.get("split") or "") == split]


def _labeled_items(
    examples: Iterable[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    return [
        item
        for item in examples
        if str(_mapping(item.get("targets")).get("source_dependency") or "")
    ]


def _source_dependency_labeled_count(
    examples: Sequence[Mapping[str, Any]],
    *,
    eval_split: str | None,
) -> int:
    return len(_labeled_items(_filter_by_split(examples, eval_split)))


def _target_counts(
    recommendations: Sequence[Mapping[str, Any]],
    key: str,
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in recommendations:
        counts[str(item.get(key) or "unknown")] += 1
    return dict(sorted(counts.items()))


def _majority_value(values: Iterable[Any]) -> str:
    counts: Counter[str] = Counter(
        str(value or "") for value in values if str(value or "")
    )
    if not counts:
        return ""
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(float(numerator) / float(denominator), 6)


def _sortable_accuracy(value: Any) -> float:
    if value is None:
        return -1.0
    return float(value)


def _validate_split(value: str, *, label: str) -> None:
    if value not in DATASET_SPLITS:
        raise ValueError(f"unsupported {label} {value!r}; expected one of {DATASET_SPLITS}")


def _resolve_optional_repo_path(root: Path, path: str | Path | None) -> Path | None:
    if not path:
        return None
    resolved = Path(path)
    if resolved.is_absolute():
        return resolved
    return root / resolved


def _split_policy_threshold(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise ValueError(f"threshold must be POLICY=VALUE, got {raw!r}")
    policy, value = raw.split("=", 1)
    policy = policy.strip()
    value = value.strip()
    if not policy or not value:
        raise ValueError(f"threshold must be POLICY=VALUE, got {raw!r}")
    return policy, value


def _format_number(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
