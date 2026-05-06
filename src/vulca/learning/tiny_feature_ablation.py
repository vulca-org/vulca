"""Feature ablation reports for provider-free tiny action evaluation."""
from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from vulca.learning.tiny_action_model import (
    FAILURE_HINT_ACTION_PRIORS,
    POLICY_TINY_ACTION_MODEL,
    build_tiny_action_model_predictions,
)
from vulca.learning.tiny_dataset import (
    DATASET_SPLITS,
    evaluate_tiny_prediction_records,
    load_tiny_dataset_examples,
)


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_tiny_feature_ablation_report"
DEFAULT_OUTPUT_PATH = Path("build/tiny_feature_ablation/tiny_feature_ablation.json")

AblationMutator = Callable[[dict[str, Any]], None]

_QUALITY_FAILURE_HINT_KEYS: frozenset[str] = frozenset(
    set(FAILURE_HINT_ACTION_PRIORS)
    | {
        "alpha_quality",
        "empty_layer",
        "residual_leakage",
        "semantic_mismatch",
    }
)


def run_tiny_feature_ablation_report(
    *,
    examples: Sequence[Mapping[str, Any]],
    output_path: str | Path | None = None,
    eval_split: str = "test",
    train_split: str = "train",
) -> dict[str, Any]:
    """Evaluate tiny_action_model_v1 under strong-feature ablations."""
    _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")
    source_examples = [copy.deepcopy(dict(example)) for example in examples]
    variant_specs = _variant_specs()
    variant_reports = [
        _evaluate_variant(
            source_examples,
            variant_id=variant_id,
            removed_feature_groups=removed_feature_groups,
            mutators=mutators,
            eval_split=eval_split,
            train_split=train_split,
        )
        for variant_id, removed_feature_groups, mutators in variant_specs
    ]
    full_accuracy = _accuracy_by_variant(variant_reports).get("full")
    for report in variant_reports:
        accuracy = report["policy_report"]["action_accuracy"]
        report["accuracy_delta_vs_full"] = _delta(accuracy, full_accuracy)

    output = Path(output_path) if output_path is not None else DEFAULT_OUTPUT_PATH
    result = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "policy_name": POLICY_TINY_ACTION_MODEL,
        "eval_split": eval_split,
        "train_split": train_split,
        "example_count": len(source_examples),
        "variant_reports": variant_reports,
        "summary": _summary(variant_reports),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def run_tiny_feature_ablation_report_for_dataset(
    *,
    dataset_path: str | Path,
    output_path: str | Path | None = None,
    eval_split: str = "test",
    train_split: str = "train",
) -> dict[str, Any]:
    """Load a tiny dataset JSONL and run the feature ablation report."""
    return run_tiny_feature_ablation_report(
        examples=load_tiny_dataset_examples(dataset_path),
        output_path=output_path,
        eval_split=eval_split,
        train_split=train_split,
    )


def _evaluate_variant(
    examples: Sequence[Mapping[str, Any]],
    *,
    variant_id: str,
    removed_feature_groups: Sequence[str],
    mutators: Sequence[AblationMutator],
    eval_split: str,
    train_split: str,
) -> dict[str, Any]:
    variant_examples = [copy.deepcopy(dict(example)) for example in examples]
    for example in variant_examples:
        for mutator in mutators:
            mutator(example)

    predictions = build_tiny_action_model_predictions(
        variant_examples,
        split=eval_split,
        train_split=train_split,
    )
    policy_report = evaluate_tiny_prediction_records(
        variant_examples,
        predictions,
        dataset_split=eval_split,
        policy_name=POLICY_TINY_ACTION_MODEL,
    )
    return {
        "variant_id": variant_id,
        "removed_feature_groups": list(removed_feature_groups),
        "policy_report": _compact_policy_report(policy_report),
        "fallback_reason_counts": _fallback_reason_counts(predictions),
        "auxiliary_feature_match_count": _auxiliary_feature_match_count(predictions),
    }


def _variant_specs() -> tuple[
    tuple[str, tuple[str, ...], tuple[AblationMutator, ...]],
    ...,
]:
    return (
        ("full", (), ()),
        (
            "without_failure_hints",
            ("quality.failure_hints",),
            (_remove_failure_hints,),
        ),
        (
            "without_action_hints",
            ("decisions.action_hints",),
            (_remove_action_hints,),
        ),
        (
            "without_failure_and_action_hints",
            ("quality.failure_hints", "decisions.action_hints"),
            (_remove_failure_hints, _remove_action_hints),
        ),
        (
            "without_auxiliary_signals",
            ("input.auxiliary_signals",),
            (_remove_auxiliary_signals,),
        ),
    )


def _remove_failure_hints(example: dict[str, Any]) -> None:
    quality = _case_record_child(example, "quality")
    if not isinstance(quality, dict):
        return
    quality.pop("failures", None)
    quality.pop("gate_passed", None)
    for key in _QUALITY_FAILURE_HINT_KEYS:
        quality.pop(key, None)


def _remove_action_hints(example: dict[str, Any]) -> None:
    decisions = _case_record_child(example, "decisions")
    if not isinstance(decisions, dict):
        return
    fallback_decisions = decisions.get("fallback_decisions")
    if not isinstance(fallback_decisions, list):
        return
    for item in fallback_decisions:
        if isinstance(item, dict):
            item.pop("suggested_action", None)


def _remove_auxiliary_signals(example: dict[str, Any]) -> None:
    input_block = example.get("input")
    if isinstance(input_block, dict):
        input_block.pop("auxiliary_signals", None)


def _case_record_child(example: Mapping[str, Any], key: str) -> Any:
    input_block = example.get("input")
    if not isinstance(input_block, Mapping):
        return None
    case_record = input_block.get("case_record")
    if not isinstance(case_record, Mapping):
        return None
    return case_record.get(key)


def _compact_policy_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "policy_name": str(report.get("policy_name") or ""),
        "split": str(report.get("split") or ""),
        "example_count": int(report.get("example_count") or 0),
        "prediction_count": int(report.get("prediction_count") or 0),
        "matched_count": int(report.get("matched_count") or 0),
        "missing_count": int(report.get("missing_count") or 0),
        "action_labeled_count": int(report.get("action_labeled_count") or 0),
        "action_accuracy": report.get("action_accuracy"),
        "mismatch_count": int(report.get("mismatch_count") or 0),
        "mismatches": list(report.get("mismatches") or []),
    }


def _fallback_reason_counts(predictions: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for prediction in predictions:
        explanation = prediction.get("explanation")
        if not isinstance(explanation, Mapping):
            counts["missing_explanation"] += 1
            continue
        reason = str(explanation.get("fallback_reason") or "scored_features")
        counts[reason] += 1
    return dict(sorted(counts.items()))


def _auxiliary_feature_match_count(predictions: Sequence[Mapping[str, Any]]) -> int:
    count = 0
    for prediction in predictions:
        explanation = prediction.get("explanation")
        if not isinstance(explanation, Mapping):
            continue
        matched = explanation.get("matched_features")
        if not isinstance(matched, Sequence) or isinstance(matched, (str, bytes)):
            continue
        if any(str(item).startswith("aux_signal.") for item in matched):
            count += 1
    return count


def _summary(variant_reports: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_variant = {
        str(report.get("variant_id") or ""): report for report in variant_reports
    }
    full = _mapping(by_variant.get("full"))
    full_policy = _mapping(full.get("policy_report"))
    return {
        "full_action_accuracy": full_policy.get("action_accuracy"),
        "full_mismatch_count": int(full_policy.get("mismatch_count") or 0),
        "largest_accuracy_drop": _largest_accuracy_drop(variant_reports),
    }


def _largest_accuracy_drop(
    variant_reports: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    rows = [
        {
            "variant_id": str(report.get("variant_id") or ""),
            "accuracy_delta_vs_full": report.get("accuracy_delta_vs_full"),
        }
        for report in variant_reports
        if report.get("variant_id") != "full"
        and report.get("accuracy_delta_vs_full") is not None
    ]
    if not rows:
        return {}
    return sorted(rows, key=lambda item: float(item["accuracy_delta_vs_full"]))[0]


def _accuracy_by_variant(
    variant_reports: Sequence[Mapping[str, Any]],
) -> dict[str, float | None]:
    return {
        str(report.get("variant_id") or ""): _mapping(
            report.get("policy_report")
        ).get("action_accuracy")
        for report in variant_reports
    }


def _delta(value: Any, baseline: Any) -> float | None:
    if value is None or baseline is None:
        return None
    return round(float(value) - float(baseline), 6)


def _validate_split(value: str, *, label: str) -> None:
    if value not in DATASET_SPLITS:
        raise ValueError(f"unsupported {label} {value!r}; expected one of {DATASET_SPLITS}")


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
