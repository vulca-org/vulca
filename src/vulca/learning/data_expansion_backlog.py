"""Data expansion backlog derived from model-selection review rows."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from vulca.learning.model_selection_report import DEFAULT_COMBINED_CASE_SOURCE_MANIFEST
from vulca.learning.model_selection_review_table import (
    DEFAULT_OUTPUT_DIR as REVIEW_TABLE_OUTPUT_DIR,
    run_model_selection_review_table,
)
from vulca.learning.tiny_dataset import DATASET_SPLITS, load_tiny_dataset_examples


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_data_expansion_backlog"
DEFAULT_OUTPUT_DIR = Path("build/data_expansion_backlog")
DEFAULT_REPORT_NAME = "data_expansion_backlog_report.json"
DEFAULT_BACKLOG_JSON_NAME = "data_expansion_backlog.json"
DEFAULT_BACKLOG_CSV_NAME = "data_expansion_backlog.csv"
CSV_COLUMNS: tuple[str, ...] = (
    "priority_tier",
    "priority_score",
    "backlog_id",
    "case_type",
    "failure_type",
    "requested_real_cases",
    "requested_manual_cases",
    "current_eval_count",
    "current_real_eval_count",
    "target_actions",
    "source_kind_counts",
    "priority_reason",
    "collection_prompt",
)


def run_data_expansion_backlog(
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
    requested_real_cases_per_item: int = 2,
    requested_manual_cases_per_item: int = 1,
) -> dict[str, Any]:
    """Build actionable case-collection tasks from model-selection review rows."""
    _validate_split(eval_split, label="eval_split")
    _validate_split(train_split, label="train_split")
    if requested_real_cases_per_item < 0:
        raise ValueError("requested_real_cases_per_item must be >= 0")
    if requested_manual_cases_per_item < 0:
        raise ValueError("requested_manual_cases_per_item must be >= 0")

    root = Path(repo_root).resolve()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    review_report = run_model_selection_review_table(
        repo_root=root,
        output_dir=output / "model_selection_review",
        case_source_manifest_path=case_source_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
        min_eval_examples_per_bucket=min_eval_examples_per_bucket,
        min_workload_eval_examples=min_workload_eval_examples,
    )
    review_rows = _load_review_rows(review_report)
    dataset_path = Path(str(review_report["artifacts"]["dataset_path"]))
    examples = load_tiny_dataset_examples(dataset_path)
    example_by_case_id = {
        str(_mapping(item.get("source_case")).get("case_id") or ""): item
        for item in examples
    }
    items = _build_backlog_items(
        review_rows,
        example_by_case_id=example_by_case_id,
        requested_real_cases=requested_real_cases_per_item,
        requested_manual_cases=requested_manual_cases_per_item,
    )

    backlog_json_path = output / DEFAULT_BACKLOG_JSON_NAME
    backlog_csv_path = output / DEFAULT_BACKLOG_CSV_NAME
    backlog_json_path.write_text(
        json.dumps(items, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_csv(backlog_csv_path, items)

    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": "ready_for_case_collection",
        "train_split": train_split,
        "eval_split": eval_split,
        "inputs": {
            "repo_root": str(root),
            "case_source_manifest_path": str(_resolve_repo_path(root, case_source_manifest_path)),
            "include_local_seeds": bool(include_local_seeds),
            "min_eval_examples_per_bucket": int(min_eval_examples_per_bucket),
            "min_workload_eval_examples": int(min_workload_eval_examples),
            "requested_real_cases_per_item": int(requested_real_cases_per_item),
            "requested_manual_cases_per_item": int(requested_manual_cases_per_item),
        },
        "artifacts": {
            "report_path": str(resolved_report_path),
            "backlog_json_path": str(backlog_json_path),
            "backlog_csv_path": str(backlog_csv_path),
            "review_table_report_path": review_report["artifacts"]["report_path"],
            "review_table_jsonl_path": review_report["artifacts"][
                "review_table_jsonl_path"
            ],
            "dataset_path": str(dataset_path),
        },
        "summary": _build_summary(
            items,
            source_review_row_count=int(review_report["summary"]["row_count"]),
        ),
        "backlog_items": items,
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _build_backlog_items(
    review_rows: list[Mapping[str, Any]],
    *,
    example_by_case_id: Mapping[str, Mapping[str, Any]],
    requested_real_cases: int,
    requested_manual_cases: int,
) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for row in review_rows:
        if row.get("workload_decision") != "collect_more_real_cases":
            continue
        failure_type = str(row.get("failure_type") or "")
        if not failure_type:
            continue
        case_type = str(row.get("case_type") or "")
        buckets.setdefault((case_type, failure_type), []).append(row)

    items = [
        _build_item(
            case_type=case_type,
            failure_type=failure_type,
            rows=rows,
            example_by_case_id=example_by_case_id,
            requested_real_cases=requested_real_cases,
            requested_manual_cases=requested_manual_cases,
        )
        for (case_type, failure_type), rows in buckets.items()
    ]
    return sorted(
        items,
        key=lambda item: (
            -int(item["priority_score"]),
            str(item["case_type"]),
            str(item["failure_type"]),
        ),
    )


def _build_item(
    *,
    case_type: str,
    failure_type: str,
    rows: list[Mapping[str, Any]],
    example_by_case_id: Mapping[str, Mapping[str, Any]],
    requested_real_cases: int,
    requested_manual_cases: int,
) -> dict[str, Any]:
    source_kind_counts: Counter[str] = Counter()
    target_actions: Counter[str] = Counter()
    examples: list[dict[str, str]] = []
    priority_score = 0
    real_count = 0
    synthetic_count = 0
    manual_count = 0
    for row in rows:
        source_kind = str(row.get("source_kind") or "")
        source_kind_counts[source_kind] += 1
        if source_kind == "user_case_log":
            real_count += 1
        elif source_kind == "synthetic_case_log":
            synthetic_count += 1
        elif source_kind == "manual_case_log":
            manual_count += 1
        action = str(row.get("target_action") or "")
        if action:
            target_actions[action] += 1
        priority_score += int(row.get("priority_score") or 0)
        examples.append(_example_summary(row, example_by_case_id=example_by_case_id))

    priority_tier = _priority_tier(priority_score, real_count=real_count)
    return {
        "schema_version": SCHEMA_VERSION,
        "backlog_id": f"{case_type}__{failure_type}",
        "case_type": case_type,
        "failure_type": failure_type,
        "workload_decision": "collect_more_real_cases",
        "priority_tier": priority_tier,
        "priority_score": priority_score,
        "priority_reason": _priority_reason(
            case_type=case_type,
            failure_type=failure_type,
            real_count=real_count,
            synthetic_count=synthetic_count,
            manual_count=manual_count,
            source_kind_counts=source_kind_counts,
        ),
        "requested_real_cases": int(requested_real_cases),
        "requested_manual_cases": int(requested_manual_cases),
        "current_eval_count": len(rows),
        "current_real_eval_count": real_count,
        "current_synthetic_eval_count": synthetic_count,
        "current_manual_eval_count": manual_count,
        "source_kind_counts": dict(sorted(source_kind_counts.items())),
        "target_actions": dict(sorted(target_actions.items())),
        "collection_prompt": _collection_prompt(
            case_type=case_type,
            failure_type=failure_type,
            target_actions=target_actions,
            requested_real_cases=requested_real_cases,
            requested_manual_cases=requested_manual_cases,
        ),
        "seed_examples": examples,
    }


def _example_summary(
    row: Mapping[str, Any],
    *,
    example_by_case_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, str]:
    case_id = str(row.get("case_id") or "")
    example = _mapping(example_by_case_id.get(case_id))
    source = _mapping(example.get("source"))
    source_case = _mapping(example.get("source_case"))
    return {
        "case_id": case_id,
        "example_id": str(row.get("example_id") or ""),
        "source_kind": str(row.get("source_kind") or ""),
        "source_id": str(row.get("source_id") or ""),
        "target_action": str(row.get("target_action") or ""),
        "source_case_type": str(source_case.get("case_type") or row.get("case_type") or ""),
        "source_index": str(source.get("index") if source.get("index") is not None else ""),
    }


def _priority_tier(priority_score: int, *, real_count: int) -> str:
    if real_count > 0 or priority_score >= 100:
        return "P0"
    if priority_score >= 75:
        return "P1"
    return "P2"


def _priority_reason(
    *,
    case_type: str,
    failure_type: str,
    real_count: int,
    synthetic_count: int,
    manual_count: int,
    source_kind_counts: Counter[str],
) -> str:
    fragments = [
        f"{case_type}/{failure_type} is marked collect_more_real_cases",
        f"eval sources={dict(sorted(source_kind_counts.items()))}",
    ]
    if real_count:
        fragments.append("real user case signal exists and should be expanded")
    else:
        fragments.append("no real user case coverage yet")
    if synthetic_count:
        fragments.append("synthetic holdout coverage exists")
    if manual_count:
        fragments.append("manual curated coverage exists")
    return "; ".join(fragments)


def _collection_prompt(
    *,
    case_type: str,
    failure_type: str,
    target_actions: Counter[str],
    requested_real_cases: int,
    requested_manual_cases: int,
) -> str:
    action_text = ", ".join(
        f"{action} x{count}" for action, count in sorted(target_actions.items())
    )
    return (
        f"Collect {requested_real_cases} real user cases and "
        f"{requested_manual_cases} manual curated case for {case_type} "
        f"failure_type={failure_type}. Preserve labels, artifacts, and privacy; "
        f"target preferred_action distribution: {action_text or 'unlabeled'}."
    )


def _load_review_rows(review_report: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    path = Path(str(review_report["artifacts"]["review_table_jsonl_path"]))
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _build_summary(
    items: list[Mapping[str, Any]],
    *,
    source_review_row_count: int,
) -> dict[str, Any]:
    return {
        "source_review_row_count": int(source_review_row_count),
        "backlog_item_count": len(items),
        "requested_real_case_count": sum(
            int(item.get("requested_real_cases") or 0) for item in items
        ),
        "requested_manual_case_count": sum(
            int(item.get("requested_manual_cases") or 0) for item in items
        ),
        "case_type_counts": dict(
            sorted(Counter(str(item.get("case_type") or "") for item in items).items())
        ),
    }


def _write_csv(path: Path, items: list[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for item in items:
            writer.writerow({column: _csv_value(item.get(column)) for column in CSV_COLUMNS})


def _csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
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
