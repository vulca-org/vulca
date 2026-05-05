"""Tiny model/agent dataset export and offline baseline evaluation."""
from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from vulca.layers.decompose_cases import CASE_TYPE as DECOMPOSE_CASE_TYPE
from vulca.layers.layer_generate_cases import CASE_TYPE as LAYER_GENERATE_CASE_TYPE
from vulca.layers.redraw_cases import CASE_TYPE as REDRAW_CASE_TYPE
from vulca.layers.redraw_router_baseline import (
    POLICY_OBSERVABLE_SIGNAL,
    recommend_action,
)
from vulca.learning.case_review import load_cases
from vulca.learning.seed_cases import DEFAULT_SEED_MANIFEST, build_local_seed_cases


DATASET_SCHEMA_VERSION = 1
DATASET_CASE_TYPE = "learning_tiny_dataset_example"
DATASET_INDEX_CASE_TYPE = "learning_tiny_dataset_index"
EVAL_REPORT_CASE_TYPE = "learning_tiny_dataset_eval_report"

POLICY_REDRAW_OBSERVABLE_SIGNAL = "redraw_observable_signal"
TINY_DATASET_EVAL_POLICIES: frozenset[str] = frozenset(
    {POLICY_REDRAW_OBSERVABLE_SIGNAL}
)
SUPPORTED_SOURCE_CASE_TYPES: frozenset[str] = frozenset(
    {REDRAW_CASE_TYPE, DECOMPOSE_CASE_TYPE, LAYER_GENERATE_CASE_TYPE}
)


@dataclass(frozen=True)
class TinyDatasetWriteResult:
    output_path: str
    index_path: str
    example_count: int
    counts_by_case_type: dict[str, int]


def build_tiny_dataset_examples(
    *,
    repo_root: str | Path,
    manifest_path: str | Path = DEFAULT_SEED_MANIFEST,
    case_log_paths: Sequence[str | Path] = (),
    include_local_seeds: bool = True,
) -> list[dict[str, Any]]:
    """Build leak-resistant tiny dataset examples from seeds and case logs."""
    examples: list[dict[str, Any]] = []

    if include_local_seeds:
        bundle = build_local_seed_cases(repo_root, manifest_path)
        for case_type in (
            REDRAW_CASE_TYPE,
            DECOMPOSE_CASE_TYPE,
            LAYER_GENERATE_CASE_TYPE,
        ):
            for index, record in enumerate(bundle.get(case_type, [])):
                examples.append(
                    _build_example(
                        record,
                        source={
                            "kind": "local_seed",
                            "split": "seed",
                            "manifest": str(manifest_path),
                            "index": index,
                        },
                    )
                )

    for case_log_path in case_log_paths:
        records = load_cases(case_log_path)
        for index, record in enumerate(records):
            examples.append(
                _build_example(
                    record,
                    source={
                        "kind": "case_log",
                        "split": "log",
                        "path": str(case_log_path),
                        "index": index,
                    },
                )
            )

    return examples


def write_tiny_dataset(
    *,
    repo_root: str | Path,
    output_path: str | Path,
    manifest_path: str | Path = DEFAULT_SEED_MANIFEST,
    case_log_paths: Sequence[str | Path] = (),
    include_local_seeds: bool = True,
    index_path: str | Path | None = None,
) -> TinyDatasetWriteResult:
    examples = build_tiny_dataset_examples(
        repo_root=repo_root,
        manifest_path=manifest_path,
        case_log_paths=case_log_paths,
        include_local_seeds=include_local_seeds,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output, examples)

    counts = _counts_by_case_type(examples)
    index = Path(index_path) if index_path is not None else _default_index_path(output)
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(
        json.dumps(
            {
                "schema_version": DATASET_SCHEMA_VERSION,
                "case_type": DATASET_INDEX_CASE_TYPE,
                "output_path": str(output),
                "source_manifest": str(manifest_path),
                "case_log_paths": [str(path) for path in case_log_paths],
                "include_local_seeds": bool(include_local_seeds),
                "example_count": len(examples),
                "counts_by_case_type": counts,
                "counts_by_source": _counts_by_source(examples),
                "target_counts": _target_counts(examples),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return TinyDatasetWriteResult(
        output_path=str(output),
        index_path=str(index),
        example_count=len(examples),
        counts_by_case_type=counts,
    )


def load_tiny_dataset_examples(path: str | Path) -> list[dict[str, Any]]:
    return load_cases(path)


def evaluate_tiny_dataset_examples(
    examples: Iterable[Mapping[str, Any]],
    *,
    policy_name: str = POLICY_REDRAW_OBSERVABLE_SIGNAL,
) -> dict[str, Any]:
    """Evaluate provider-free policies on exported tiny dataset examples."""
    if policy_name not in TINY_DATASET_EVAL_POLICIES:
        raise ValueError(
            f"unsupported tiny dataset eval policy {policy_name!r}; "
            f"expected one of {sorted(TINY_DATASET_EVAL_POLICIES)}"
        )

    items = list(examples)
    action_total = 0
    action_correct = 0
    evaluated_count = 0
    skipped_by_case_type: Counter[str] = Counter()
    mismatches: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []

    for example in items:
        source_case = _mapping(example.get("source_case"))
        source_case_type = str(source_case.get("case_type") or "")
        if (
            policy_name == POLICY_REDRAW_OBSERVABLE_SIGNAL
            and source_case_type != REDRAW_CASE_TYPE
        ):
            skipped_by_case_type[source_case_type or "unknown"] += 1
            continue

        case_record = _mapping(_mapping(example.get("input")).get("case_record"))
        recommendation = recommend_action(
            case_record,
            policy_name=POLICY_OBSERVABLE_SIGNAL,
        )
        evaluated_count += 1
        target_action = str(
            _mapping(example.get("targets")).get("preferred_action") or ""
        )
        recommendation_record = {
            "example_id": str(example.get("example_id") or ""),
            "case_id": str(source_case.get("case_id") or ""),
            "source_case_type": source_case_type,
            "target_action": target_action,
            "recommended_action": recommendation.recommended_action,
            "failure_hint": recommendation.failure_hint,
            "rule_reason": recommendation.rule_reason,
        }
        recommendations.append(recommendation_record)

        if target_action:
            action_total += 1
            if recommendation.recommended_action == target_action:
                action_correct += 1
            else:
                mismatches.append(recommendation_record)

    skipped_count = sum(skipped_by_case_type.values())
    return {
        "schema_version": DATASET_SCHEMA_VERSION,
        "case_type": EVAL_REPORT_CASE_TYPE,
        "policy_name": policy_name,
        "example_count": len(items),
        "evaluated_count": evaluated_count,
        "skipped_count": skipped_count,
        "skipped_by_case_type": dict(sorted(skipped_by_case_type.items())),
        "action_labeled_count": action_total,
        "action_accuracy": _ratio(action_correct, action_total),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "recommendations": recommendations,
    }


def write_tiny_dataset_eval_report(
    *,
    dataset_path: str | Path,
    output_path: str | Path,
    policy_name: str = POLICY_REDRAW_OBSERVABLE_SIGNAL,
) -> str:
    report = evaluate_tiny_dataset_examples(
        load_tiny_dataset_examples(dataset_path),
        policy_name=policy_name,
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return str(path)


def _build_example(
    record: Mapping[str, Any],
    *,
    source: Mapping[str, Any],
) -> dict[str, Any]:
    case_type = str(record.get("case_type") or "")
    if case_type not in SUPPORTED_SOURCE_CASE_TYPES:
        raise ValueError(
            f"unsupported source case_type {case_type!r}; "
            f"expected one of {sorted(SUPPORTED_SOURCE_CASE_TYPES)}"
        )
    case_id = str(record.get("case_id") or "")
    review = _mapping(record.get("review"))
    human_accept = review.get("human_accept")
    failure_type = str(review.get("failure_type") or "")
    preferred_action = str(review.get("preferred_action") or "")
    source_data = dict(source)

    return {
        "schema_version": DATASET_SCHEMA_VERSION,
        "case_type": DATASET_CASE_TYPE,
        "example_id": _make_example_id(source_data, case_type, case_id),
        "created_at": str(record.get("created_at") or ""),
        "source": source_data,
        "source_case": {
            "case_type": case_type,
            "case_id": case_id,
            "schema_version": int(record.get("schema_version", 0) or 0),
        },
        "input": {
            "case_record": _sanitize_case_for_input(record),
        },
        "targets": {
            "human_accept": human_accept if isinstance(human_accept, bool) else None,
            "failure_type": failure_type,
            "preferred_action": preferred_action,
        },
        "tasks": {
            "tiny_model": {
                "accept_reject": _accept_reject_label(human_accept),
                "failure_classification": failure_type,
            },
            "tiny_agent": {
                "next_action_policy": preferred_action,
            },
        },
    }


def _sanitize_case_for_input(record: Mapping[str, Any]) -> dict[str, Any]:
    sanitized = copy.deepcopy(dict(record))
    _drop_label_fields(sanitized)
    if sanitized.get("case_type") == LAYER_GENERATE_CASE_TYPE:
        decisions = sanitized.get("decisions")
        if isinstance(decisions, dict):
            layer_count = decisions.get("layer_count")
            if isinstance(layer_count, dict):
                layer_count.pop("accepted", None)
        outputs = _mapping(sanitized.get("outputs"))
        for layer in outputs.get("layers", []) or []:
            if not isinstance(layer, dict):
                continue
            if str(layer.get("status") or "") in {"accepted", "rejected"}:
                layer["status"] = "generated"
    return sanitized


def _drop_label_fields(value: Any) -> None:
    if isinstance(value, dict):
        value.pop("review", None)
        value.pop("learning_targets", None)
        for child in value.values():
            _drop_label_fields(child)
    elif isinstance(value, list):
        for child in value:
            _drop_label_fields(child)


def _make_example_id(source: Mapping[str, Any], case_type: str, case_id: str) -> str:
    seed = json.dumps(
        {
            "schema_version": DATASET_SCHEMA_VERSION,
            "source": dict(source),
            "case_type": case_type,
            "case_id": case_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"tiny_{digest}"


def _accept_reject_label(value: Any) -> str:
    if value is True:
        return "accept"
    if value is False:
        return "reject"
    return ""


def _write_jsonl(path: Path, records: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
            fh.write("\n")


def _default_index_path(output_path: Path) -> Path:
    if output_path.suffix == ".jsonl":
        return output_path.with_suffix(".index.json")
    return output_path.with_name(f"{output_path.name}.index.json")


def _counts_by_case_type(examples: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for example in examples:
        key = str(_mapping(example.get("source_case")).get("case_type") or "unknown")
        counts[key] += 1
    return dict(sorted(counts.items()))


def _counts_by_source(examples: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for example in examples:
        counts[str(_mapping(example.get("source")).get("kind") or "unknown")] += 1
    return dict(sorted(counts.items()))


def _target_counts(examples: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    human_accept_counts: Counter[str] = Counter()
    failure_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    for example in examples:
        targets = _mapping(example.get("targets"))
        human_accept = targets.get("human_accept")
        if human_accept is True:
            human_accept_counts["true"] += 1
        elif human_accept is False:
            human_accept_counts["false"] += 1
        else:
            human_accept_counts["unlabeled"] += 1

        failure_type = str(targets.get("failure_type") or "")
        preferred_action = str(targets.get("preferred_action") or "")
        if failure_type:
            failure_counts[failure_type] += 1
        if preferred_action:
            action_counts[preferred_action] += 1

    return {
        "human_accept": dict(sorted(human_accept_counts.items())),
        "failure_type": dict(sorted(failure_counts.items())),
        "preferred_action": dict(sorted(action_counts.items())),
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator
