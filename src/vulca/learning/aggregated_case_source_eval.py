"""Provider-free aggregated case-source evaluation report."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from vulca.learning.seed_cases import DEFAULT_SEED_MANIFEST
from vulca.learning.tiny_dataset import (
    CASE_SOURCE_MANIFEST_CASE_TYPE,
    DATASET_SPLITS,
    load_tiny_dataset_examples,
)
from vulca.learning.tiny_training_eval import (
    DEFAULT_MANUAL_CURATED_CASE_SOURCE_MANIFEST,
    format_gate_violation,
    run_tiny_training_eval_gate,
)


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_aggregated_case_source_eval_report"
DEFAULT_OUTPUT_DIR = Path("build/aggregated_case_source_eval")
DEFAULT_REPORT_NAME = "aggregated_case_source_eval_report.json"
COMBINED_CASE_SOURCE_MANIFEST_NAME = "aggregated_case_source_manifest.json"
TINY_TRAINING_EVAL_REPORT_NAME = "tiny_training_eval_report.json"
BUCKETS: tuple[str, ...] = (
    "source_id",
    "source.kind",
    "privacy_scope",
    "curation_status",
    "source_case.case_type",
    "targets.failure_type",
)


def run_aggregated_case_source_eval(
    *,
    repo_root: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    manifest_path: str | Path | None = DEFAULT_SEED_MANIFEST,
    case_log_paths: Sequence[str | Path] = (),
    case_source_manifest_paths: Sequence[str | Path] = (),
    include_default_case_source_manifest: bool = True,
    include_local_seeds: bool = True,
    eval_split: str = "test",
    train_split: str = "train",
) -> dict[str, Any]:
    """Run the tiny eval gate and aggregate source/bucket metrics."""
    _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")

    root = Path(repo_root).resolve()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    resolved_manifest_path = manifest_path or DEFAULT_SEED_MANIFEST
    resolved_case_logs = tuple(_resolve_repo_path(root, path) for path in case_log_paths)
    resolved_source_manifests = _resolve_case_source_manifest_inputs(
        root,
        case_source_manifest_paths,
        include_default_case_source_manifest=include_default_case_source_manifest,
    )
    combined_manifest_path = _write_combined_case_source_manifest(
        resolved_source_manifests,
        output / COMBINED_CASE_SOURCE_MANIFEST_NAME,
    )

    tiny_report_path = output / TINY_TRAINING_EVAL_REPORT_NAME
    tiny_report = run_tiny_training_eval_gate(
        repo_root=root,
        output_dir=output,
        report_path=tiny_report_path,
        manifest_path=resolved_manifest_path,
        case_log_paths=resolved_case_logs,
        case_source_manifest_path=combined_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
    )
    examples = load_tiny_dataset_examples(tiny_report["artifacts"]["dataset_path"])
    policy_comparison = _mapping(tiny_report.get("comparison"))
    bucket_metrics = _build_bucket_metrics(
        examples,
        policy_comparison=policy_comparison,
        eval_split=eval_split,
    )

    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "train_split": train_split,
        "eval_split": eval_split,
        "inputs": {
            "repo_root": str(root),
            "source_manifest": str(resolved_manifest_path),
            "case_log_paths": [str(path) for path in resolved_case_logs],
            "case_source_manifest_paths": [str(path) for path in resolved_source_manifests],
            "include_default_case_source_manifest": bool(include_default_case_source_manifest),
            "include_local_seeds": bool(include_local_seeds),
        },
        "artifacts": {
            "report_path": str(resolved_report_path),
            "tiny_training_eval_report_path": str(tiny_report_path),
            "dataset_path": tiny_report["artifacts"]["dataset_path"],
            "dataset_index_path": tiny_report["artifacts"]["dataset_index_path"],
            "combined_case_source_manifest_path": str(combined_manifest_path or ""),
            "tiny_agent_v0_prediction_path": tiny_report["artifacts"]["tiny_agent_v0_prediction_path"],
            "tiny_action_model_v1_prediction_path": tiny_report["artifacts"][
                "tiny_action_model_v1_prediction_path"
            ],
            "comparison_report_path": tiny_report["artifacts"]["comparison_report_path"],
        },
        "dataset_summary": _build_dataset_summary(examples),
        "source_summary": _build_source_summary(examples),
        "bucket_metrics": bucket_metrics,
        "policy_comparison": policy_comparison,
        "mismatches_by_bucket": _group_mismatches_by_bucket(
            examples,
            policy_comparison=policy_comparison,
        ),
        "tiny_training_eval": {
            "gate": tiny_report["gate"],
            "predictions": tiny_report["predictions"],
        },
    }

    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def format_aggregated_eval_gate_failure(report: Mapping[str, Any]) -> list[str]:
    """Format tiny gate failures as aggregated CLI stderr lines."""
    gate = _mapping(_mapping(report.get("tiny_training_eval")).get("gate"))
    return [
        format_gate_violation(_mapping(violation))
        for violation in gate.get("violations", []) or []
        if isinstance(violation, Mapping)
    ]


def _resolve_case_source_manifest_inputs(
    repo_root: Path,
    case_source_manifest_paths: Sequence[str | Path],
    *,
    include_default_case_source_manifest: bool,
) -> tuple[Path, ...]:
    paths: list[Path] = []
    if include_default_case_source_manifest:
        paths.append(_resolve_repo_path(repo_root, DEFAULT_MANUAL_CURATED_CASE_SOURCE_MANIFEST))
    paths.extend(_resolve_repo_path(repo_root, path) for path in case_source_manifest_paths)
    return tuple(paths)


def _write_combined_case_source_manifest(
    manifest_paths: Sequence[Path],
    output_path: Path,
) -> Path | None:
    if not manifest_paths:
        return None

    sources: list[dict[str, Any]] = []
    for manifest_path in manifest_paths:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, Mapping):
            raise ValueError(f"{manifest_path}: case source manifest must be a JSON object")
        if manifest.get("case_type") != CASE_SOURCE_MANIFEST_CASE_TYPE:
            raise ValueError(
                f"{manifest_path}: case_type must be {CASE_SOURCE_MANIFEST_CASE_TYPE!r}"
            )
        manifest_sources = manifest.get("sources")
        if not isinstance(manifest_sources, list):
            raise ValueError(f"{manifest_path}: sources must be a list")
        for index, source in enumerate(manifest_sources):
            if not isinstance(source, Mapping):
                raise ValueError(f"{manifest_path}: sources[{index}] must be an object")
            item = dict(source)
            raw_path = str(item.get("path") or "")
            if raw_path:
                case_log_path = Path(raw_path)
                if not case_log_path.is_absolute():
                    case_log_path = manifest_path.parent / case_log_path
                item["path"] = str(case_log_path)
            sources.append(item)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "case_type": CASE_SOURCE_MANIFEST_CASE_TYPE,
                "sources": sources,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return output_path


def _build_dataset_summary(examples: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "example_count": len(examples),
        "counts_by_split": _counter_by(examples, lambda item: str(item.get("split") or "unknown")),
        "counts_by_source_kind": _counter_by(
            examples,
            lambda item: _bucket_value(item, "source.kind"),
        ),
        "counts_by_source_case_type": _counter_by(
            examples,
            lambda item: _bucket_value(item, "source_case.case_type"),
        ),
        "target_counts": {
            "human_accept": _human_accept_counts(examples),
            "failure_type": _counter_by(
                examples,
                lambda item: _target_failure_type(item),
                skip_empty=True,
            ),
            "preferred_action": _counter_by(
                examples,
                lambda item: str(_mapping(item.get("targets")).get("preferred_action") or ""),
                skip_empty=True,
            ),
        },
    }


def _build_source_summary(examples: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    for source_id, items in _group_examples(examples, "source_id").items():
        sources.append(
            {
                "source_id": source_id,
                "example_count": len(items),
                "source_kind_counts": _counter_by(
                    items,
                    lambda item: _bucket_value(item, "source.kind"),
                ),
                "privacy_scope_counts": _counter_by(
                    items,
                    lambda item: _bucket_value(item, "privacy_scope"),
                ),
                "curation_status_counts": _counter_by(
                    items,
                    lambda item: _bucket_value(item, "curation_status"),
                ),
                "source_case_type_counts": _counter_by(
                    items,
                    lambda item: _bucket_value(item, "source_case.case_type"),
                ),
                "failure_type_counts": _counter_by(
                    items,
                    lambda item: _target_failure_type(item),
                    skip_empty=True,
                ),
            }
        )

    return {
        "source_count": len(sources),
        "sources": sorted(sources, key=lambda item: str(item["source_id"])),
        "by_source_kind": _counter_by(
            examples,
            lambda item: _bucket_value(item, "source.kind"),
        ),
        "by_privacy_scope": _counter_by(
            examples,
            lambda item: _bucket_value(item, "privacy_scope"),
        ),
        "by_curation_status": _counter_by(
            examples,
            lambda item: _bucket_value(item, "curation_status"),
        ),
    }


def _build_bucket_metrics(
    examples: Sequence[Mapping[str, Any]],
    *,
    policy_comparison: Mapping[str, Any],
    eval_split: str,
) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    eval_examples = [example for example in examples if example.get("split") == eval_split]
    for bucket in BUCKETS:
        grouped_all = _group_examples(examples, bucket)
        grouped_eval = _group_examples(eval_examples, bucket)
        bucket_rows: dict[str, Any] = {}
        for value, items in grouped_all.items():
            bucket_eval_items = grouped_eval.get(value, [])
            bucket_rows[value] = {
                "example_count": len(items),
                "eval_example_count": len(bucket_eval_items),
                "counts_by_split": _counter_by(
                    items,
                    lambda item: str(item.get("split") or "unknown"),
                ),
                "target_counts": {
                    "failure_type": _counter_by(
                        items,
                        lambda item: _target_failure_type(item),
                        skip_empty=True,
                    ),
                    "preferred_action": _counter_by(
                        items,
                        lambda item: str(
                            _mapping(item.get("targets")).get("preferred_action") or ""
                        ),
                        skip_empty=True,
                    ),
                },
                "policy_reports": _build_policy_bucket_reports(
                    bucket_eval_items,
                    policy_comparison=policy_comparison,
                ),
            }
        metrics[bucket] = bucket_rows
    return metrics


def _build_policy_bucket_reports(
    examples: Sequence[Mapping[str, Any]],
    *,
    policy_comparison: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    example_ids = {str(example.get("example_id") or "") for example in examples}
    reports = _mapping(policy_comparison.get("policy_reports"))
    rows: dict[str, dict[str, Any]] = {}
    for policy_name, report_value in sorted(reports.items()):
        report = _mapping(report_value)
        recommendations = [
            _mapping(item)
            for item in report.get("recommendations", []) or []
            if str(_mapping(item).get("example_id") or "") in example_ids
        ]
        mismatches = [
            _mapping(item)
            for item in report.get("mismatches", []) or []
            if str(_mapping(item).get("example_id") or "") in example_ids
        ]
        missing_predictions = [
            _mapping(item)
            for item in report.get("missing_predictions", []) or []
            if str(_mapping(item).get("example_id") or "") in example_ids
        ]
        action_labeled_count = sum(
            1 for item in recommendations if str(item.get("target_action") or "")
        )
        correct_count = action_labeled_count - len(mismatches)
        skipped_count = max(
            0,
            len(examples) - len(recommendations) - len(missing_predictions),
        )
        row = {
            "example_count": len(examples),
            "evaluated_count": len(recommendations),
            "skipped_count": skipped_count,
            "action_labeled_count": action_labeled_count,
            "action_accuracy": _ratio(correct_count, action_labeled_count),
            "mismatch_count": len(mismatches),
        }
        if "matched_count" in report or "missing_count" in report:
            row["matched_count"] = len(recommendations)
            row["missing_count"] = len(missing_predictions)
        rows[str(policy_name)] = row
    return rows


def _group_mismatches_by_bucket(
    examples: Sequence[Mapping[str, Any]],
    *,
    policy_comparison: Mapping[str, Any],
) -> dict[str, dict[str, dict[str, list[dict[str, Any]]]]]:
    example_by_id = {str(example.get("example_id") or ""): example for example in examples}
    reports = _mapping(policy_comparison.get("policy_reports"))
    grouped: dict[str, dict[str, dict[str, list[dict[str, Any]]]]] = {
        bucket: {str(policy): {} for policy in sorted(reports)} for bucket in BUCKETS
    }

    for policy_name, report_value in sorted(reports.items()):
        report = _mapping(report_value)
        for mismatch_value in report.get("mismatches", []) or []:
            mismatch = _mapping(mismatch_value)
            example = example_by_id.get(str(mismatch.get("example_id") or ""))
            if example is None:
                continue
            enriched = _enriched_mismatch(str(policy_name), mismatch, example)
            for bucket in BUCKETS:
                bucket_value = _bucket_value(example, bucket)
                grouped[bucket][str(policy_name)].setdefault(bucket_value, []).append(enriched)

    for bucket_rows in grouped.values():
        for policy_rows in bucket_rows.values():
            for bucket_value, mismatches in list(policy_rows.items()):
                policy_rows[bucket_value] = sorted(
                    mismatches,
                    key=lambda item: (
                        str(item.get("example_id") or ""),
                        str(item.get("target_action") or ""),
                        str(item.get("recommended_action") or ""),
                    ),
                )
    return grouped


def _enriched_mismatch(
    policy_name: str,
    mismatch: Mapping[str, Any],
    example: Mapping[str, Any],
) -> dict[str, Any]:
    source = _mapping(example.get("source"))
    source_case = _mapping(example.get("source_case"))
    targets = _mapping(example.get("targets"))
    return {
        "policy_name": policy_name,
        "example_id": str(example.get("example_id") or mismatch.get("example_id") or ""),
        "case_id": str(source_case.get("case_id") or mismatch.get("case_id") or ""),
        "source_id": _bucket_value(example, "source_id"),
        "source_kind": str(source.get("kind") or "unknown"),
        "privacy_scope": _bucket_value(example, "privacy_scope"),
        "curation_status": _bucket_value(example, "curation_status"),
        "source_case_type": _bucket_value(example, "source_case.case_type"),
        "failure_type": str(targets.get("failure_type") or ""),
        "target_action": str(mismatch.get("target_action") or ""),
        "recommended_action": str(mismatch.get("recommended_action") or ""),
        "failure_hint": str(mismatch.get("failure_hint") or ""),
        "rule_reason": str(mismatch.get("rule_reason") or ""),
    }


def _group_examples(
    examples: Iterable[Mapping[str, Any]],
    bucket: str,
) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for example in examples:
        grouped.setdefault(_bucket_value(example, bucket), []).append(example)
    return {key: grouped[key] for key in sorted(grouped)}


def _bucket_value(example: Mapping[str, Any], bucket: str) -> str:
    source = _mapping(example.get("source"))
    source_case = _mapping(example.get("source_case"))
    targets = _mapping(example.get("targets"))

    if bucket == "source_id":
        source_id = str(source.get("source_id") or "")
        if source_id:
            return source_id
        kind = str(source.get("kind") or "")
        if kind == "local_seed":
            return "local_seed"
        path = str(source.get("path") or source.get("manifest") or "")
        if kind and path:
            return f"{kind}:{path}"
        return kind or "unknown"
    if bucket == "source.kind":
        return str(source.get("kind") or "unknown")
    if bucket == "privacy_scope":
        return str(source.get("privacy_scope") or "unspecified")
    if bucket == "curation_status":
        return str(source.get("curation_status") or "unspecified")
    if bucket == "source_case.case_type":
        return str(source_case.get("case_type") or "unknown")
    if bucket == "targets.failure_type":
        return str(targets.get("failure_type") or "unlabeled")
    raise ValueError(f"unsupported aggregate bucket {bucket!r}")


def _counter_by(
    examples: Iterable[Mapping[str, Any]],
    key_fn: Any,
    *,
    skip_empty: bool = False,
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for example in examples:
        key = str(key_fn(example) or "")
        if skip_empty and not key:
            continue
        counts[key or "unknown"] += 1
    return dict(sorted(counts.items()))


def _human_accept_counts(examples: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for example in examples:
        value = _mapping(example.get("targets")).get("human_accept")
        if value is True:
            counts["true"] += 1
        elif value is False:
            counts["false"] += 1
        else:
            counts["unlabeled"] += 1
    return dict(sorted(counts.items()))


def _target_failure_type(example: Mapping[str, Any]) -> str:
    return str(_mapping(example.get("targets")).get("failure_type") or "")


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


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator
