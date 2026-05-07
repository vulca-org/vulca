"""Reviewed source-dependency labels for tiny training datasets."""
from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.layers.redraw_cases import utc_now_iso
from vulca.learning.case_review import load_cases, write_cases
from vulca.learning.real_source_dependency_review import (
    DECISION_BASIS_VALUES,
    ITEM_CASE_TYPE as REVIEW_ITEM_CASE_TYPE,
    SCHEMA_VERSION as REVIEW_SCHEMA_VERSION,
    SOURCE_DEPENDENCY_VALUES,
)


SCHEMA_VERSION = 1
LABEL_RECORD_CASE_TYPE = "learning_source_dependency_label_record"
LABEL_MANIFEST_CASE_TYPE = "learning_source_dependency_label_manifest"
SOURCE_DEPENDENCY_LABEL_LOG_KIND = "source_dependency_label_log"
REVIEWED_SOURCE_DEPENDENCY_STATUS = "reviewed_source_dependency_label"
APPROVED_LABEL_USE = "source_dependency_training_label"


@dataclass(frozen=True)
class SourceDependencyLabelPackResult:
    output_path: str
    manifest_path: str
    source_id: str
    record_count: int
    counts_by_source_dependency: dict[str, int]
    counts_by_decision_basis: dict[str, int]


def write_source_dependency_label_pack(
    *,
    input_path: str | Path,
    output_path: str | Path,
    manifest_path: str | Path,
    source_id: str,
    reviewer: str = "",
    reviewed_at: str | None = None,
    require_complete: bool = True,
) -> SourceDependencyLabelPackResult:
    """Write a sanitized label JSONL and manifest from completed review items."""
    resolved_source_id = str(source_id or "").strip()
    if not resolved_source_id:
        raise ValueError("source_id is required")

    review_time = str(reviewed_at or utc_now_iso())
    labels = [
        _label_record(
            item,
            record_index=index,
            source_id=resolved_source_id,
            reviewer=reviewer,
            reviewed_at=review_time,
            require_complete=require_complete,
        )
        for index, item in enumerate(load_cases(input_path))
    ]

    output = Path(output_path)
    manifest = Path(manifest_path)
    write_cases(output, labels)
    counts_by_source_dependency = _counts(labels, "source_dependency")
    counts_by_decision_basis = _counts(labels, "decision_basis")
    _write_manifest(
        manifest_path=manifest,
        output_path=output,
        source_id=resolved_source_id,
        record_count=len(labels),
        counts_by_source_dependency=counts_by_source_dependency,
        counts_by_decision_basis=counts_by_decision_basis,
    )
    return SourceDependencyLabelPackResult(
        output_path=str(output),
        manifest_path=str(manifest),
        source_id=resolved_source_id,
        record_count=len(labels),
        counts_by_source_dependency=counts_by_source_dependency,
        counts_by_decision_basis=counts_by_decision_basis,
    )


def load_source_dependency_labels(manifest_path: str | Path) -> list[dict[str, Any]]:
    """Load reviewed source-dependency labels from an explicit manifest."""
    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if not isinstance(manifest, Mapping):
        raise ValueError("source dependency label manifest must be an object")
    if manifest.get("case_type") != LABEL_MANIFEST_CASE_TYPE:
        raise ValueError(
            "source dependency label manifest case_type must be "
            f"{LABEL_MANIFEST_CASE_TYPE!r}"
        )

    sources = manifest.get("sources")
    if not isinstance(sources, list):
        raise ValueError("source dependency label manifest sources must be a list")

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for source_index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            errors.append(f"sources[{source_index}] must be an object")
            continue
        path = str(source.get("path") or "")
        if not path:
            errors.append(f"sources[{source_index}]: path is required")
            continue
        if str(source.get("kind") or "") != SOURCE_DEPENDENCY_LABEL_LOG_KIND:
            errors.append(
                f"sources[{source_index}]: unsupported kind "
                f"{str(source.get('kind') or '')!r}"
            )
        if str(source.get("curation_status") or "") != REVIEWED_SOURCE_DEPENDENCY_STATUS:
            errors.append(
                f"sources[{source_index}]: unsupported curation_status "
                f"{str(source.get('curation_status') or '')!r}"
            )
        source_path = Path(path)
        if not source_path.is_absolute():
            source_path = manifest_file.parent / source_path
        for record_index, record in enumerate(load_cases(source_path)):
            try:
                _validate_label_record(record, record_index=record_index)
            except ValueError as exc:
                errors.append(f"{source_path}:{record_index + 1}: {exc}")
                continue
            records.append(dict(record))

    if errors:
        raise ValueError("; ".join(errors))
    return records


def attach_source_dependency_labels(
    examples: Sequence[dict[str, Any]],
    *,
    manifest_path: str | Path,
) -> int:
    """Mutate dataset examples by attaching reviewed source-dependency labels."""
    labels_by_key: dict[tuple[str, int, str, str], dict[str, Any]] = {}
    for label in load_source_dependency_labels(manifest_path):
        key = _label_match_key(label)
        if key in labels_by_key:
            raise ValueError(f"duplicate source dependency label for {key!r}")
        labels_by_key[key] = label

    attached = 0
    for example in examples:
        label = labels_by_key.get(_example_match_key(example))
        if not label:
            continue
        labels = _mapping(label.get("labels"))
        targets = example.setdefault("targets", {})
        if not isinstance(targets, dict):
            raise ValueError(
                f"dataset example {str(example.get('example_id') or '')!r} "
                "targets must be an object"
            )
        targets["source_dependency"] = str(labels.get("source_dependency") or "")
        targets["source_decision_basis"] = str(labels.get("decision_basis") or "")
        targets["source_preferred_action_confirmed"] = labels.get(
            "preferred_action_confirmed"
        )
        targets["source_corrected_preferred_action"] = str(
            labels.get("corrected_preferred_action") or ""
        )

        tasks = example.setdefault("tasks", {})
        if not isinstance(tasks, dict):
            raise ValueError(
                f"dataset example {str(example.get('example_id') or '')!r} "
                "tasks must be an object"
            )
        source_context = tasks.setdefault("source_context", {})
        if not isinstance(source_context, dict):
            raise ValueError(
                f"dataset example {str(example.get('example_id') or '')!r} "
                "tasks.source_context must be an object"
            )
        source_context["dependency_classification"] = targets["source_dependency"]
        source_context["decision_basis_classification"] = targets[
            "source_decision_basis"
        ]
        example["source_dependency_review"] = {
            "label_id": str(label.get("label_id") or ""),
            "review_status": REVIEWED_SOURCE_DEPENDENCY_STATUS,
            "approved_label_use": APPROVED_LABEL_USE,
        }
        attached += 1
    return attached


def _label_record(
    item: Mapping[str, Any],
    *,
    record_index: int,
    source_id: str,
    reviewer: str,
    reviewed_at: str,
    require_complete: bool,
) -> dict[str, Any]:
    _validate_review_item(item, record_index=record_index)
    human_review = _mapping(item.get("human_review"))
    source_dependency = _validate_source_dependency(
        human_review.get("source_dependency"),
        record_index=record_index,
        require_complete=require_complete,
    )
    decision_basis = _validate_decision_basis(
        human_review.get("decision_basis"),
        record_index=record_index,
        require_complete=require_complete,
    )
    confirmed = human_review.get("preferred_action_confirmed")
    if require_complete and not isinstance(confirmed, bool):
        raise ValueError(
            f"record {record_index}: incomplete source dependency review: "
            "human_review.preferred_action_confirmed must be true or false"
        )
    corrected_action = str(human_review.get("corrected_preferred_action") or "")
    if confirmed is False and not corrected_action:
        raise ValueError(
            f"record {record_index}: corrected_preferred_action is required when "
            "preferred_action_confirmed is false"
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": LABEL_RECORD_CASE_TYPE,
        "label_id": _label_id(source_id, item),
        "source_case": {
            "case_type": str(item.get("source_case_type") or ""),
            "case_id": str(item.get("case_id") or ""),
        },
        "source": _safe_source(_mapping(item.get("source"))),
        "current_labels": dict(_mapping(item.get("current_labels"))),
        "source_context": _safe_source_context(_mapping(item.get("source_context"))),
        "audit": _safe_audit(_mapping(item.get("audit"))),
        "labels": {
            "source_dependency": source_dependency,
            "decision_basis": decision_basis,
            "preferred_action_confirmed": confirmed if isinstance(confirmed, bool) else None,
            "corrected_preferred_action": corrected_action,
        },
        "review": {
            "schema_version": SCHEMA_VERSION,
            "reviewer": str(reviewer or ""),
            "reviewed_at": str(reviewed_at or ""),
            "review_notes_present": bool(str(human_review.get("review_notes") or "")),
        },
        "training_use": {
            "default_training_input": False,
            "approved_for_source_dependency_training": source_dependency != "unknown",
            "review_status": REVIEWED_SOURCE_DEPENDENCY_STATUS,
            "approved_label_use": APPROVED_LABEL_USE,
        },
    }


def _validate_review_item(item: Mapping[str, Any], *, record_index: int) -> None:
    if item.get("case_type") != REVIEW_ITEM_CASE_TYPE:
        raise ValueError(
            f"record {record_index}: case_type must be {REVIEW_ITEM_CASE_TYPE!r}"
        )
    if int(item.get("schema_version") or 0) != REVIEW_SCHEMA_VERSION:
        raise ValueError(
            f"record {record_index}: schema_version must be {REVIEW_SCHEMA_VERSION}"
        )
    if not str(item.get("case_id") or ""):
        raise ValueError(f"record {record_index}: case_id is required")
    if not str(item.get("source_case_type") or ""):
        raise ValueError(f"record {record_index}: source_case_type is required")
    source = _mapping(item.get("source"))
    if not str(source.get("source_id") or ""):
        raise ValueError(f"record {record_index}: source.source_id is required")


def _validate_label_record(record: Mapping[str, Any], *, record_index: int) -> None:
    if record.get("case_type") != LABEL_RECORD_CASE_TYPE:
        raise ValueError(
            f"record {record_index}: case_type must be {LABEL_RECORD_CASE_TYPE!r}"
        )
    if int(record.get("schema_version") or 0) != SCHEMA_VERSION:
        raise ValueError(f"record {record_index}: schema_version must be {SCHEMA_VERSION}")
    labels = _mapping(record.get("labels"))
    _validate_source_dependency(
        labels.get("source_dependency"),
        record_index=record_index,
        require_complete=True,
    )
    _validate_decision_basis(
        labels.get("decision_basis"),
        record_index=record_index,
        require_complete=True,
    )
    training_use = _mapping(record.get("training_use"))
    if not bool(training_use.get("approved_for_source_dependency_training")):
        raise ValueError(
            f"record {record_index}: label is not approved for source dependency training"
        )


def _validate_source_dependency(
    value: Any,
    *,
    record_index: int,
    require_complete: bool,
) -> str:
    normalized = str(value or "").strip()
    if normalized not in SOURCE_DEPENDENCY_VALUES:
        raise ValueError(
            f"record {record_index}: unsupported source_dependency {normalized!r}; "
            f"expected one of {list(SOURCE_DEPENDENCY_VALUES)}"
        )
    if require_complete and normalized == "unknown":
        raise ValueError(
            f"record {record_index}: incomplete source dependency review: "
            "human_review.source_dependency must not be unknown"
        )
    return normalized


def _validate_decision_basis(
    value: Any,
    *,
    record_index: int,
    require_complete: bool,
) -> str:
    normalized = str(value or "").strip()
    if normalized not in DECISION_BASIS_VALUES:
        raise ValueError(
            f"record {record_index}: unsupported decision_basis {normalized!r}; "
            f"expected one of {list(DECISION_BASIS_VALUES)}"
        )
    if require_complete and normalized == "unknown":
        raise ValueError(
            f"record {record_index}: incomplete source dependency review: "
            "human_review.decision_basis must not be unknown"
        )
    return normalized


def _write_manifest(
    *,
    manifest_path: Path,
    output_path: Path,
    source_id: str,
    record_count: int,
    counts_by_source_dependency: Mapping[str, int],
    counts_by_decision_basis: Mapping[str, int],
) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "case_type": LABEL_MANIFEST_CASE_TYPE,
        "sources": [
            {
                "source_id": source_id,
                "kind": SOURCE_DEPENDENCY_LABEL_LOG_KIND,
                "path": _manifest_relative_path(output_path, manifest_path.parent),
                "privacy_scope": "project",
                "curation_status": REVIEWED_SOURCE_DEPENDENCY_STATUS,
                "approved_label_use": APPROVED_LABEL_USE,
                "record_count": int(record_count),
                "counts_by_source_dependency": dict(
                    sorted(counts_by_source_dependency.items())
                ),
                "counts_by_decision_basis": dict(sorted(counts_by_decision_basis.items())),
            }
        ],
        "record_count": int(record_count),
        "counts_by_source_dependency": dict(sorted(counts_by_source_dependency.items())),
        "counts_by_decision_basis": dict(sorted(counts_by_decision_basis.items())),
        "training_use": {
            "default_training_input": False,
            "requires_explicit_dataset_flag": True,
            "approved_label_use": APPROVED_LABEL_USE,
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _label_match_key(record: Mapping[str, Any]) -> tuple[str, int, str, str]:
    source = _mapping(record.get("source"))
    source_case = _mapping(record.get("source_case"))
    return (
        str(source.get("source_id") or ""),
        int(source.get("record_index") or 0),
        str(source_case.get("case_type") or ""),
        str(source_case.get("case_id") or ""),
    )


def _example_match_key(example: Mapping[str, Any]) -> tuple[str, int, str, str]:
    source = _mapping(example.get("source"))
    source_case = _mapping(example.get("source_case"))
    return (
        str(source.get("source_id") or ""),
        int(source.get("index") or 0),
        str(source_case.get("case_type") or ""),
        str(source_case.get("case_id") or ""),
    )


def _label_id(source_id: str, item: Mapping[str, Any]) -> str:
    seed = json.dumps(
        {
            "source_id": source_id,
            "case_id": str(item.get("case_id") or ""),
            "source_case_type": str(item.get("source_case_type") or ""),
            "source": _safe_source(_mapping(item.get("source"))),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"source_dependency_label_{digest}"


def _counts(records: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        labels = _mapping(record.get("labels"))
        counts[str(labels.get(key) or "unknown")] += 1
    return dict(sorted(counts.items()))


def _safe_source(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": str(source.get("source_id") or ""),
        "kind": str(source.get("kind") or ""),
        "privacy_scope": str(source.get("privacy_scope") or ""),
        "curation_status": str(source.get("curation_status") or ""),
        "record_index": int(source.get("record_index") or 0),
        "split": str(source.get("split") or ""),
    }


def _safe_source_context(source_context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "available": bool(source_context.get("available")),
        "tags": [str(item) for item in source_context.get("tags", []) or []],
        "source_image_available": bool(source_context.get("source_image_available")),
        "source_artifact_available_count": int(
            source_context.get("source_artifact_available_count") or 0
        ),
        "source_artifact_text_file_count": int(
            source_context.get("source_artifact_text_file_count") or 0
        ),
    }


def _safe_audit(audit: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "candidate_reason": str(audit.get("candidate_reason") or ""),
        "recommended_review_action": str(audit.get("recommended_review_action") or ""),
        "source_context_feature_match_count": int(
            audit.get("source_context_feature_match_count") or 0
        ),
    }


def _manifest_relative_path(output_path: Path, manifest_dir: Path) -> str:
    return Path(os.path.relpath(output_path, manifest_dir)).as_posix()


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
