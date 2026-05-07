"""Prioritized source-context gap pack from training effectiveness v3 reports."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.learning.source_dependency_eval import DEFAULT_SOURCE_DEPENDENCY_MANIFEST
from vulca.learning.tiny_dataset import load_tiny_dataset_examples
from vulca.learning.training_effectiveness import (
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    run_training_effectiveness_report,
)


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_source_context_gap_pack_report"
DEFAULT_OUTPUT_DIR = Path("build/source_context_gap_pack")
DEFAULT_REPORT_NAME = "source_context_gap_pack_report.json"
TRAINING_EFFECTIVENESS_DIR_NAME = "training_effectiveness"
ACTION_FALLBACK_REASON = "action_fallback_to_agent"
LOW_CONFIDENCE_REASON = "low_action_confidence"


def run_source_context_gap_pack(
    *,
    repo_root: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    case_source_manifest_path: str | Path = DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    source_dependency_manifest_path: str | Path = DEFAULT_SOURCE_DEPENDENCY_MANIFEST,
    include_local_seeds: bool = True,
    eval_split: str = "test",
    train_split: str = "train",
) -> dict[str, Any]:
    """Build an actionable data-pack plan for remaining source-context gaps."""
    root = Path(repo_root).resolve()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME

    training_effectiveness_report = run_training_effectiveness_report(
        repo_root=root,
        output_dir=output / TRAINING_EFFECTIVENESS_DIR_NAME,
        report_path=output
        / TRAINING_EFFECTIVENESS_DIR_NAME
        / "training_effectiveness_report.json",
        case_source_manifest_path=case_source_manifest_path,
        source_dependency_manifest_path=source_dependency_manifest_path,
        include_local_seeds=include_local_seeds,
        eval_split=eval_split,
        train_split=train_split,
    )
    dataset = load_tiny_dataset_examples(
        training_effectiveness_report["artifacts"]["dataset_path"],
    )
    examples_by_id = {str(item.get("example_id") or ""): item for item in dataset}
    decision_records = _load_jsonl(
        training_effectiveness_report["artifacts"][
            "dry_run_with_source_context_decision_path"
        ],
    )
    decisions_by_id = {
        str(item.get("example_id") or ""): item for item in decision_records
    }
    remaining = _mapping(
        training_effectiveness_report.get("source_context_router"),
    ).get("remaining_no_source_context_gap_cases")
    if not isinstance(remaining, Sequence) or isinstance(remaining, (str, bytes)):
        remaining = []

    gap_cases = [
        _gap_case(
            item,
            example=examples_by_id.get(str(_mapping(item).get("example_id") or ""), {}),
            decision=decisions_by_id.get(str(_mapping(item).get("example_id") or ""), {}),
        )
        for item in remaining
        if isinstance(item, Mapping)
    ]
    gap_cases = sorted(
        gap_cases,
        key=lambda item: (
            item["priority"],
            item["gap_task"],
            item["case_type"],
            item["case_id"],
        ),
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": "needs_source_context_gap_pack" if gap_cases else "source_context_ready",
        "inputs": {
            "repo_root": root.name,
            "case_source_manifest_path": _safe_repo_path(
                root,
                _resolve_repo_path(root, case_source_manifest_path),
            ),
            "source_dependency_manifest_path": _safe_repo_path(
                root,
                _resolve_repo_path(root, source_dependency_manifest_path),
            ),
            "include_local_seeds": bool(include_local_seeds),
            "eval_split": eval_split,
            "train_split": train_split,
        },
        "artifacts": {
            "report_path": str(resolved_report_path),
            "training_effectiveness_report_path": training_effectiveness_report[
                "artifacts"
            ]["report_path"],
            "dataset_path": training_effectiveness_report["artifacts"]["dataset_path"],
            "dry_run_with_source_context_decision_path": training_effectiveness_report[
                "artifacts"
            ]["dry_run_with_source_context_decision_path"],
        },
        "summary": _summary(gap_cases),
        "counts_by_case_type": _counter_by(gap_cases, "case_type"),
        "counts_by_source_kind": _counter_by(gap_cases, "source_kind"),
        "counts_by_gap_task": _counter_by(gap_cases, "gap_task"),
        "counts_by_secondary_blocker": _secondary_blocker_counts(gap_cases),
        "gap_groups": _gap_groups(gap_cases),
        "gap_cases": gap_cases,
        "safe_handling": {
            "copies_raw_source_text": False,
            "copies_local_paths": False,
            "copies_private_refs": False,
            "calls_model_provider": False,
            "downloads_weights": False,
        },
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _gap_case(
    gap: Mapping[str, Any],
    *,
    example: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    source = _mapping(example.get("source"))
    targets = _mapping(example.get("targets"))
    dispatch = _mapping(decision.get("dispatch"))
    fallback_reasons = _string_list(dispatch.get("fallback_reasons"))
    source_kind = str(source.get("kind") or "")
    gap_task = _gap_task_for_source_kind(source_kind)
    secondary_blocker = _secondary_blocker(fallback_reasons)
    return {
        "example_id": str(gap.get("example_id") or ""),
        "case_id": str(gap.get("case_id") or ""),
        "case_type": str(gap.get("case_type") or ""),
        "source_kind": source_kind,
        "source_id": str(source.get("source_id") or ""),
        "failure_type": str(targets.get("failure_type") or ""),
        "preferred_action": str(targets.get("preferred_action") or ""),
        "recommended_action": str(gap.get("recommended_action") or ""),
        "source_dependency": str(gap.get("source_dependency") or ""),
        "gap_task": gap_task,
        "priority": _priority_for_gap_task(gap_task),
        "secondary_blocker": secondary_blocker,
        "fallback_reasons": fallback_reasons,
        "expected_effect": (
            "remove_source_context_fallback"
            if secondary_blocker == "source_context_only"
            else "remove_source_context_gap_but_keep_agent_blocker"
        ),
    }


def _summary(gap_cases: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    remaining_count = len(gap_cases)
    still_agent_required = sum(
        1
        for item in gap_cases
        if str(item.get("secondary_blocker") or "") != "source_context_only"
    )
    return {
        "remaining_gap_count": remaining_count,
        "source_context_gap_closable_count": remaining_count,
        "tiny_model_dispatch_recoverable_count": remaining_count - still_agent_required,
        "still_agent_required_after_source_context_count": still_agent_required,
    }


def _gap_groups(gap_cases: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for item in gap_cases:
        grouped.setdefault(str(item.get("gap_task") or ""), []).append(item)

    rows: list[dict[str, Any]] = []
    for gap_task, items in grouped.items():
        rows.append(
            {
                "gap_task": gap_task,
                "priority": _priority_for_gap_task(gap_task),
                "case_count": len(items),
                "counts_by_case_type": _counter_by(items, "case_type"),
                "counts_by_source_kind": _counter_by(items, "source_kind"),
                "recommended_next_step": _recommended_next_step(gap_task),
            }
        )
    return sorted(rows, key=lambda item: (item["priority"], item["gap_task"]))


def _gap_task_for_source_kind(source_kind: str) -> str:
    if source_kind == "user_case_log":
        return "recover_real_user_source_context"
    if source_kind == "manual_case_log":
        return "attach_reviewed_source_artifact"
    if source_kind == "synthetic_case_log":
        return "author_synthetic_source_packet"
    if source_kind == "local_seed":
        return "review_seed_source_dependency"
    return "review_source_context_gap"


def _priority_for_gap_task(gap_task: str) -> str:
    if gap_task == "recover_real_user_source_context":
        return "p0"
    if gap_task in {"attach_reviewed_source_artifact", "author_synthetic_source_packet"}:
        return "p1"
    return "p2"


def _recommended_next_step(gap_task: str) -> str:
    if gap_task == "recover_real_user_source_context":
        return "recover or map the private source artifact/image, then rerun source-context signals"
    if gap_task == "attach_reviewed_source_artifact":
        return "add safe reviewed source_refs for the manual case and rerun source-context signals"
    if gap_task == "author_synthetic_source_packet":
        return "write safe synthetic source packets matching the holdout taxonomy case"
    if gap_task == "review_seed_source_dependency":
        return "decide whether the seed requires source context or should be metadata-only"
    return "review source context requirement and add the missing source evidence"


def _secondary_blocker(fallback_reasons: Sequence[str]) -> str:
    if ACTION_FALLBACK_REASON in fallback_reasons:
        return ACTION_FALLBACK_REASON
    if LOW_CONFIDENCE_REASON in fallback_reasons:
        return LOW_CONFIDENCE_REASON
    return "source_context_only"


def _secondary_blocker_counts(gap_cases: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return _counter_by(gap_cases, "secondary_blocker")


def _counter_by(items: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        value = str(item.get(field) or "unknown")
        counts[value] += 1
    return dict(sorted(counts.items()))


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if isinstance(item, Mapping):
            records.append(dict(item))
    return records


def _resolve_repo_path(repo_root: Path, path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = repo_root / resolved
    return resolved


def _safe_repo_path(repo_root: Path, path: str | Path) -> str:
    value = Path(path)
    try:
        return str(value.relative_to(repo_root))
    except ValueError:
        return value.name


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value]


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
