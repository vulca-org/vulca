"""Provider-free dry-run decision router for tiny learning cases."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from vulca.learning.seed_cases import DEFAULT_SEED_MANIFEST
from vulca.learning.source_dependency_eval import (
    DEFAULT_CASE_SOURCE_MANIFEST,
    DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
    POLICY_SOURCE_DEPENDENCY_RULE,
    predict_source_dependency_for_example,
)
from vulca.learning.tiny_action_model import (
    POLICY_TINY_ACTION_MODEL,
    TinyActionClassifier,
)
from vulca.learning.tiny_dataset import (
    DATASET_SPLITS,
    load_tiny_dataset_examples,
    write_tiny_dataset,
)


SCHEMA_VERSION = 1
DECISION_CASE_TYPE = "learning_dry_run_decision"
REPORT_CASE_TYPE = "learning_dry_run_decision_router_report"
DEFAULT_OUTPUT_DIR = Path("build/dry_run_decision_router")
DEFAULT_REPORT_NAME = "dry_run_decision_router_report.json"
DEFAULT_DECISION_NAME = "dry_run_decisions.jsonl"
DEFAULT_MIN_ACTION_CONFIDENCE = 0.5


def run_dry_run_decision_router(
    *,
    repo_root: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    manifest_path: str | Path | None = DEFAULT_SEED_MANIFEST,
    case_log_paths: Sequence[str | Path] = (),
    case_source_manifest_path: str | Path | None = DEFAULT_CASE_SOURCE_MANIFEST,
    source_dependency_manifest_path: str | Path | None = DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
    auxiliary_signal_manifest_path: str | Path | None = None,
    include_local_seeds: bool = True,
    eval_split: str = "test",
    train_split: str = "train",
    min_action_confidence: float = DEFAULT_MIN_ACTION_CONFIDENCE,
) -> dict[str, Any]:
    """Export the tiny dataset and write provider-free dry-run router decisions."""
    _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")
    root = Path(repo_root)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    dataset_path = output / "tiny_dataset.with_source_dependency.jsonl"
    decision_path = output / DEFAULT_DECISION_NAME
    resolved_report_path = (
        Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    )
    resolved_case_source_manifest = _resolve_optional_repo_path(
        root,
        case_source_manifest_path,
    )
    resolved_source_dependency_manifest = _resolve_optional_repo_path(
        root,
        source_dependency_manifest_path,
    )
    resolved_auxiliary_signal_manifest = _resolve_optional_repo_path(
        root,
        auxiliary_signal_manifest_path,
    )

    dataset_result = write_tiny_dataset(
        repo_root=root,
        output_path=dataset_path,
        manifest_path=manifest_path or DEFAULT_SEED_MANIFEST,
        case_log_paths=case_log_paths,
        case_source_manifest_path=resolved_case_source_manifest,
        source_dependency_manifest_path=resolved_source_dependency_manifest,
        auxiliary_signal_manifest_path=resolved_auxiliary_signal_manifest,
        include_local_seeds=include_local_seeds,
    )
    examples = load_tiny_dataset_examples(dataset_path)
    report = build_dry_run_router_report(
        examples,
        eval_split=eval_split,
        train_split=train_split,
        min_action_confidence=min_action_confidence,
    )
    decisions = report["decisions"]
    _write_jsonl(decision_path, decisions)

    report = {
        **{key: value for key, value in report.items() if key != "decisions"},
        "inputs": {
            "repo_root": str(root),
            "source_manifest": str(manifest_path or DEFAULT_SEED_MANIFEST),
            "case_log_paths": [str(path) for path in case_log_paths],
            "case_source_manifest_path": str(resolved_case_source_manifest or ""),
            "source_dependency_manifest_path": str(
                resolved_source_dependency_manifest or ""
            ),
            "auxiliary_signal_manifest_path": str(
                resolved_auxiliary_signal_manifest or ""
            ),
            "include_local_seeds": bool(include_local_seeds),
            "min_action_confidence": float(min_action_confidence),
        },
        "artifacts": {
            "dataset_path": str(dataset_path),
            "dataset_index_path": dataset_result.index_path,
            "decision_path": str(decision_path),
            "report_path": str(resolved_report_path),
        },
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def build_dry_run_router_report(
    examples: Iterable[Mapping[str, Any]],
    *,
    eval_split: str = "test",
    train_split: str = "train",
    min_action_confidence: float = DEFAULT_MIN_ACTION_CONFIDENCE,
) -> dict[str, Any]:
    """Build dry-run decisions and aggregate router metrics."""
    decisions = build_dry_run_decisions(
        examples,
        eval_split=eval_split,
        train_split=train_split,
        min_action_confidence=min_action_confidence,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "train_split": train_split,
        "eval_split": eval_split,
        "summary": _build_summary(decisions),
        "evaluation": _build_evaluation(decisions),
        "decisions": decisions,
    }


def build_dry_run_decisions(
    examples: Iterable[Mapping[str, Any]],
    *,
    eval_split: str = "test",
    train_split: str = "train",
    min_action_confidence: float = DEFAULT_MIN_ACTION_CONFIDENCE,
) -> list[dict[str, Any]]:
    """Combine tiny action and source-dependency decisions for a frozen split."""
    _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")
    items = list(examples)
    classifier = TinyActionClassifier.fit(items, train_split=train_split)
    decisions: list[dict[str, Any]] = []
    for example in items:
        if str(example.get("split") or "") != eval_split:
            continue
        action_prediction = classifier.predict(example)
        source_prediction = predict_source_dependency_for_example(example)
        decisions.append(
            _decision_record(
                example,
                action_prediction=action_prediction,
                source_prediction=source_prediction,
                min_action_confidence=min_action_confidence,
            )
        )
    return decisions


def _decision_record(
    example: Mapping[str, Any],
    *,
    action_prediction: Mapping[str, Any],
    source_prediction: Any,
    min_action_confidence: float,
) -> dict[str, Any]:
    source_case = _mapping(example.get("source_case"))
    targets = _mapping(example.get("targets"))
    confidence = _float(action_prediction.get("confidence"), default=0.0)
    recommended_action = str(action_prediction.get("recommended_action") or "")
    source_dependency = str(source_prediction.source_dependency or "")
    decision_basis = str(source_prediction.decision_basis or "")
    target_dependency = str(targets.get("source_dependency") or "")
    target_basis = str(targets.get("source_decision_basis") or "")
    source_context = _source_context_summary(example)
    dispatch = _dispatch_record(
        recommended_action=recommended_action,
        action_confidence=confidence,
        min_action_confidence=min_action_confidence,
        source_dependency=source_dependency,
        source_context_available=bool(source_context["available"]),
        target_dependency=target_dependency,
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": DECISION_CASE_TYPE,
        "example_id": str(example.get("example_id") or ""),
        "case_id": str(source_case.get("case_id") or ""),
        "source_case_type": str(source_case.get("case_type") or ""),
        "split": str(example.get("split") or ""),
        "action_router": {
            "policy_name": POLICY_TINY_ACTION_MODEL,
            "recommended_action": recommended_action,
            "confidence": confidence,
            "failure_hint": str(action_prediction.get("failure_hint") or ""),
            "rule_reason": _action_rule_reason(action_prediction),
            "target_action": str(targets.get("preferred_action") or ""),
        },
        "source_dependency_router": {
            "policy_name": POLICY_SOURCE_DEPENDENCY_RULE,
            "recommended_source_dependency": source_dependency,
            "recommended_decision_basis": decision_basis,
            "confidence": _float(source_prediction.confidence, default=0.0),
            "rule_reason": str(source_prediction.rule_reason or ""),
            "target_source_dependency": target_dependency,
            "target_decision_basis": target_basis,
        },
        "source_context": source_context,
        "dispatch": dispatch,
    }


def _dispatch_record(
    *,
    recommended_action: str,
    action_confidence: float,
    min_action_confidence: float,
    source_dependency: str,
    source_context_available: bool,
    target_dependency: str,
) -> dict[str, Any]:
    fallback_reasons: list[str] = []
    data_gap_tags: list[str] = []
    if recommended_action == "fallback_to_agent":
        fallback_reasons.append("action_fallback_to_agent")
    if action_confidence < min_action_confidence:
        fallback_reasons.append("low_action_confidence")
        data_gap_tags.append("low_action_confidence")
    if source_dependency == "required" and not source_context_available:
        fallback_reasons.append("source_required_but_unavailable")
        data_gap_tags.append("no_source_context_for_required_source")
    if not target_dependency:
        data_gap_tags.append("no_source_dependency_label")

    fallback_agent = bool(fallback_reasons)
    return {
        "decision_owner": (
            "fallback_agent"
            if action_confidence < min_action_confidence
            else "tiny_model"
        ),
        "execution_owner": "fallback_agent" if fallback_agent else "tiny_model",
        "fallback_agent": fallback_agent,
        "fallback_reasons": fallback_reasons,
        "data_gap_tags": data_gap_tags,
    }


def _build_summary(decisions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    data_gap_counts: Counter[str] = Counter()
    fallback_reason_counts: Counter[str] = Counter()
    for decision in decisions:
        dispatch = _mapping(decision.get("dispatch"))
        data_gap_counts.update(dispatch.get("data_gap_tags") or [])
        fallback_reason_counts.update(dispatch.get("fallback_reasons") or [])

    return {
        "decision_count": len(decisions),
        "fallback_agent_count": sum(
            1
            for decision in decisions
            if bool(_mapping(decision.get("dispatch")).get("fallback_agent"))
        ),
        "counts_by_recommended_action": _counter_by(
            decisions,
            lambda item: _mapping(item.get("action_router")).get(
                "recommended_action"
            ),
        ),
        "counts_by_source_dependency": _counter_by(
            decisions,
            lambda item: _mapping(item.get("source_dependency_router")).get(
                "recommended_source_dependency"
            ),
        ),
        "counts_by_decision_basis": _counter_by(
            decisions,
            lambda item: _mapping(item.get("source_dependency_router")).get(
                "recommended_decision_basis"
            ),
        ),
        "counts_by_execution_owner": _counter_by(
            decisions,
            lambda item: _mapping(item.get("dispatch")).get("execution_owner"),
        ),
        "fallback_reason_counts": dict(sorted(fallback_reason_counts.items())),
        "data_gap_counts": dict(sorted(data_gap_counts.items())),
    }


def _build_evaluation(decisions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    action_total = 0
    action_correct = 0
    dependency_total = 0
    dependency_correct = 0
    basis_total = 0
    basis_correct = 0
    for decision in decisions:
        action = _mapping(decision.get("action_router"))
        source = _mapping(decision.get("source_dependency_router"))
        target_action = str(action.get("target_action") or "")
        if target_action:
            action_total += 1
            if str(action.get("recommended_action") or "") == target_action:
                action_correct += 1
        target_dependency = str(source.get("target_source_dependency") or "")
        if target_dependency:
            dependency_total += 1
            if (
                str(source.get("recommended_source_dependency") or "")
                == target_dependency
            ):
                dependency_correct += 1
        target_basis = str(source.get("target_decision_basis") or "")
        if target_basis:
            basis_total += 1
            if str(source.get("recommended_decision_basis") or "") == target_basis:
                basis_correct += 1
    return {
        "action_labeled_count": action_total,
        "action_accuracy": _ratio(action_correct, action_total),
        "source_dependency_labeled_count": dependency_total,
        "source_dependency_accuracy": _ratio(dependency_correct, dependency_total),
        "decision_basis_labeled_count": basis_total,
        "decision_basis_accuracy": _ratio(basis_correct, basis_total),
    }


def _action_rule_reason(action_prediction: Mapping[str, Any]) -> str:
    explanation = _mapping(action_prediction.get("explanation"))
    fallback_reason = str(explanation.get("fallback_reason") or "")
    return fallback_reason or str(action_prediction.get("source_policy") or "")


def _source_context_summary(example: Mapping[str, Any]) -> dict[str, Any]:
    source_context = _mapping(example.get("source_context"))
    if isinstance(source_context.get("available"), bool):
        available = bool(source_context.get("available"))
        if available:
            return {
                "available": True,
                "source": "source_context",
                "signal_count": 0,
            }
    if int(source_context.get("source_artifact_available_count") or 0) > 0:
        return {
            "available": True,
            "source": "source_context",
            "signal_count": 0,
        }
    if bool(source_context.get("source_image_available")):
        return {
            "available": True,
            "source": "source_context",
            "signal_count": 0,
        }

    signal_count = _source_context_auxiliary_signal_count(example)
    if signal_count:
        return {
            "available": True,
            "source": "auxiliary_signal",
            "signal_count": signal_count,
        }
    return {
        "available": False,
        "source": "",
        "signal_count": 0,
    }


def _source_context_auxiliary_signal_count(example: Mapping[str, Any]) -> int:
    input_block = _mapping(example.get("input"))
    signals = input_block.get("auxiliary_signals")
    if not isinstance(signals, Sequence) or isinstance(signals, (str, bytes)):
        return 0
    count = 0
    for signal in signals:
        if not isinstance(signal, Mapping):
            continue
        if not _is_promoted_source_context_signal(signal):
            continue
        signal_payload = _mapping(signal.get("signals"))
        source_image = _mapping(signal_payload.get("source_image"))
        source_artifacts = _mapping(signal_payload.get("source_artifacts"))
        tags = signal_payload.get("source_context_tags")
        has_tags = isinstance(tags, Sequence) and not isinstance(tags, (str, bytes)) and bool(tags)
        if (
            bool(source_image.get("available"))
            or int(source_artifacts.get("available_count") or 0) > 0
            or bool(source_artifacts.get("artifact_kind_counts"))
            or has_tags
        ):
            count += 1
    return count


def _is_promoted_source_context_signal(signal: Mapping[str, Any]) -> bool:
    training_use = _mapping(signal.get("training_use"))
    if not bool(training_use.get("approved_for_auxiliary_training")):
        return False
    if str(training_use.get("review_status") or "") != "reviewed_promoted":
        return False
    signal_payload = _mapping(signal.get("signals"))
    if str(signal_payload.get("status") or "") != "completed":
        return False
    model_id = str(_mapping(signal.get("model")).get("id") or "")
    signal_source = str(signal_payload.get("signal_source") or "")
    return model_id == "source_context_static_v1" or signal_source == "source_context_static"


def _counter_by(
    decisions: Iterable[Mapping[str, Any]],
    getter: Any,
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for decision in decisions:
        value = str(getter(decision) or "unknown")
        counts[value] += 1
    return dict(sorted(counts.items()))


def _write_jsonl(path: str | Path, records: Sequence[Mapping[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
            fh.write("\n")


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(float(numerator) / float(denominator), 6)


def _resolve_optional_repo_path(root: Path, path: str | Path | None) -> Path | None:
    if not path:
        return None
    resolved = Path(path)
    if resolved.is_absolute():
        return resolved
    return root / resolved


def _validate_split(value: str, *, label: str) -> None:
    if value not in DATASET_SPLITS:
        raise ValueError(f"unsupported {label} {value!r}; expected one of {DATASET_SPLITS}")


def _float(value: Any, *, default: float) -> float:
    if value is None:
        return default
    return float(value)


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
