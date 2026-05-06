"""Human review and explicit promotion for open-model signal records."""
from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.layers.redraw_cases import utc_now_iso
from vulca.learning.case_review import load_cases, write_cases
from vulca.learning.open_model_signals import (
    SCHEMA_VERSION as SIGNAL_SCHEMA_VERSION,
    SIGNAL_RECORD_CASE_TYPE,
)


SCHEMA_VERSION = 1
PROMOTION_MANIFEST_CASE_TYPE = "learning_open_model_signal_promotion_manifest"
OPEN_MODEL_SIGNAL_LOG_KIND = "open_model_signal_log"
REVIEWED_AUXILIARY_SIGNAL_STATUS = "reviewed_auxiliary_signal"
PROJECT_PRIVACY_SCOPE = "project"
DECISION_PROMOTE = "promote"
DECISION_REJECT = "reject"
DECISION_HOLD = "hold"
REVIEW_DECISIONS: frozenset[str] = frozenset(
    {DECISION_PROMOTE, DECISION_REJECT, DECISION_HOLD}
)
REVIEW_STATUS_BY_DECISION: Mapping[str, str] = {
    DECISION_PROMOTE: "reviewed_promoted",
    DECISION_REJECT: "reviewed_rejected",
    DECISION_HOLD: "needs_more_context",
}


@dataclass(frozen=True)
class OpenModelSignalReviewResult:
    signal_id: str
    output_path: str
    updated: bool
    decision: str
    review_status: str


@dataclass(frozen=True)
class PromotedOpenModelSignalPackResult:
    output_path: str
    manifest_path: str
    source_id: str
    promoted_count: int
    counts_by_model: dict[str, int]


def review_open_model_signal_log(
    input_path: str | Path,
    *,
    signal_id: str,
    decision: str,
    output_path: str | Path | None = None,
    reviewer: str = "",
    reviewed_at: str | None = None,
    notes: str = "",
) -> OpenModelSignalReviewResult:
    """Review one open-model signal record and write a non-destructive JSONL copy."""
    resolved_signal_id = str(signal_id or "")
    if not resolved_signal_id:
        raise ValueError("signal_id is required")
    resolved_decision = _validate_decision(decision)

    records = load_cases(input_path)
    output = Path(output_path) if output_path is not None else _default_review_output_path(input_path)
    found = False
    review_status = REVIEW_STATUS_BY_DECISION[resolved_decision]

    for index, record in enumerate(records):
        if str(record.get("signal_id") or "") != resolved_signal_id:
            continue
        _validate_signal_record(record, record_index=index)
        if resolved_decision == DECISION_PROMOTE:
            _validate_promotable_signal(record)
        found = True
        record["signal_review"] = {
            "schema_version": SCHEMA_VERSION,
            "decision": resolved_decision,
            "reviewer": str(reviewer or ""),
            "reviewed_at": str(reviewed_at or utc_now_iso()),
            "notes": str(notes or ""),
        }
        training_use = dict(_mapping(record.get("training_use")))
        training_use["default_training_input"] = False
        training_use["approved_for_auxiliary_training"] = (
            resolved_decision == DECISION_PROMOTE
        )
        training_use["review_status"] = review_status
        training_use["approved_signal_use"] = (
            "auxiliary_training_feature"
            if resolved_decision == DECISION_PROMOTE
            else "none"
        )
        record["training_use"] = training_use
        break

    if not found:
        raise ValueError(f"signal_id {resolved_signal_id!r} not found in {input_path}")

    write_cases(output, records)
    return OpenModelSignalReviewResult(
        signal_id=resolved_signal_id,
        output_path=str(output),
        updated=True,
        decision=resolved_decision,
        review_status=review_status,
    )


def write_promoted_open_model_signal_pack(
    *,
    input_path: str | Path,
    output_path: str | Path,
    manifest_path: str | Path,
    source_id: str,
) -> PromotedOpenModelSignalPackResult:
    """Write a promoted-only signal JSONL plus an explicit promotion manifest."""
    resolved_source_id = str(source_id or "").strip()
    if not resolved_source_id:
        raise ValueError("source_id is required")

    promoted = []
    for index, record in enumerate(load_cases(input_path)):
        _validate_signal_record(record, record_index=index)
        if not _is_promoted_signal(record):
            continue
        promoted.append(_sanitize_promoted_signal_record(record))

    output = Path(output_path)
    manifest = Path(manifest_path)
    write_cases(output, promoted)
    counts_by_model = _counts_by_model(promoted)
    _write_promotion_manifest(
        manifest_path=manifest,
        output_path=output,
        source_id=resolved_source_id,
        promoted_count=len(promoted),
        counts_by_model=counts_by_model,
    )
    return PromotedOpenModelSignalPackResult(
        output_path=str(output),
        manifest_path=str(manifest),
        source_id=resolved_source_id,
        promoted_count=len(promoted),
        counts_by_model=counts_by_model,
    )


def load_promoted_open_model_signals(
    manifest_path: str | Path,
) -> list[dict[str, Any]]:
    """Load promoted open-model signals from a promotion manifest."""
    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if not isinstance(manifest, Mapping):
        raise ValueError("open-model signal promotion manifest must be an object")
    if manifest.get("case_type") != PROMOTION_MANIFEST_CASE_TYPE:
        raise ValueError(
            "open-model signal promotion manifest case_type must be "
            f"{PROMOTION_MANIFEST_CASE_TYPE!r}"
        )

    sources = manifest.get("sources")
    if not isinstance(sources, list):
        raise ValueError("open-model signal promotion manifest sources must be a list")

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
        if str(source.get("kind") or "") != OPEN_MODEL_SIGNAL_LOG_KIND:
            errors.append(
                f"sources[{source_index}]: unsupported kind "
                f"{str(source.get('kind') or '')!r}"
            )
        if str(source.get("curation_status") or "") != REVIEWED_AUXILIARY_SIGNAL_STATUS:
            errors.append(
                f"sources[{source_index}]: unsupported curation_status "
                f"{str(source.get('curation_status') or '')!r}"
            )
        source_path = Path(path)
        if not source_path.is_absolute():
            source_path = manifest_file.parent / source_path
        for record_index, record in enumerate(load_cases(source_path)):
            _validate_signal_record(record, record_index=record_index)
            if not _is_promoted_signal(record):
                errors.append(
                    f"{source_path}:{record_index + 1}: promoted pack contains "
                    "a non-promoted signal"
                )
                continue
            records.append(_sanitize_promoted_signal_record(record))

    if errors:
        raise ValueError("; ".join(errors))
    return records


def attach_promoted_open_model_signals(
    examples: Sequence[dict[str, Any]],
    *,
    manifest_path: str | Path,
) -> None:
    """Mutate dataset examples by attaching reviewed auxiliary signals by example_id."""
    signals_by_example_id: dict[str, list[dict[str, Any]]] = {}
    for signal in load_promoted_open_model_signals(manifest_path):
        example_id = str(signal.get("example_id") or "")
        if not example_id:
            continue
        signals_by_example_id.setdefault(example_id, []).append(signal)

    for example in examples:
        example_id = str(example.get("example_id") or "")
        signals = signals_by_example_id.get(example_id)
        if not signals:
            continue
        input_block = example.setdefault("input", {})
        if not isinstance(input_block, dict):
            raise ValueError(f"dataset example {example_id!r} input must be an object")
        input_block["auxiliary_signals"] = sorted(
            signals,
            key=lambda item: str(item.get("signal_id") or ""),
        )


def _default_review_output_path(input_path: str | Path) -> Path:
    path = Path(input_path)
    if path.suffix == ".jsonl":
        return path.with_name(f"{path.stem}.reviewed{path.suffix}")
    return path.with_name(f"{path.name}.reviewed.jsonl")


def _write_promotion_manifest(
    *,
    manifest_path: Path,
    output_path: Path,
    source_id: str,
    promoted_count: int,
    counts_by_model: Mapping[str, int],
) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "case_type": PROMOTION_MANIFEST_CASE_TYPE,
        "sources": [
            {
                "source_id": source_id,
                "kind": OPEN_MODEL_SIGNAL_LOG_KIND,
                "path": _manifest_relative_path(output_path, manifest_path.parent),
                "privacy_scope": PROJECT_PRIVACY_SCOPE,
                "curation_status": REVIEWED_AUXILIARY_SIGNAL_STATUS,
                "approved_signal_use": "auxiliary_training_feature",
                "record_count": int(promoted_count),
                "counts_by_model": dict(sorted(counts_by_model.items())),
            }
        ],
        "record_count": int(promoted_count),
        "counts_by_model": dict(sorted(counts_by_model.items())),
        "training_use": {
            "default_training_input": False,
            "requires_explicit_dataset_flag": True,
            "approved_signal_use": "auxiliary_training_feature",
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _validate_decision(decision: str) -> str:
    normalized = str(decision or "").strip().lower()
    if normalized not in REVIEW_DECISIONS:
        raise ValueError(
            f"unsupported signal review decision {normalized!r}; "
            f"expected one of {sorted(REVIEW_DECISIONS)}"
        )
    return normalized


def _validate_signal_record(record: Mapping[str, Any], *, record_index: int) -> None:
    if record.get("case_type") != SIGNAL_RECORD_CASE_TYPE:
        raise ValueError(
            f"record {record_index}: case_type must be {SIGNAL_RECORD_CASE_TYPE!r}"
        )
    if int(record.get("schema_version") or 0) != SIGNAL_SCHEMA_VERSION:
        raise ValueError(
            f"record {record_index}: schema_version must be {SIGNAL_SCHEMA_VERSION}"
        )
    if not str(record.get("signal_id") or ""):
        raise ValueError(f"record {record_index}: signal_id is required")
    if not str(record.get("example_id") or ""):
        raise ValueError(f"record {record_index}: example_id is required")
    if not _mapping(record.get("model")).get("id"):
        raise ValueError(f"record {record_index}: model.id is required")
    if not isinstance(record.get("signals"), Mapping):
        raise ValueError(f"record {record_index}: signals object is required")


def _validate_promotable_signal(record: Mapping[str, Any]) -> None:
    signals = _mapping(record.get("signals"))
    source = str(signals.get("signal_source") or "")
    status = str(signals.get("status") or "")
    if source == "dry_run" or status.startswith("dry_run"):
        raise ValueError("cannot promote dry-run signal")
    if status != "completed":
        raise ValueError(f"cannot promote signal with status {status!r}")


def _is_promoted_signal(record: Mapping[str, Any]) -> bool:
    training_use = _mapping(record.get("training_use"))
    review = _mapping(record.get("signal_review"))
    return (
        bool(training_use.get("approved_for_auxiliary_training"))
        and str(training_use.get("review_status") or "") == "reviewed_promoted"
        and str(review.get("decision") or "") == DECISION_PROMOTE
    )


def _sanitize_promoted_signal_record(record: Mapping[str, Any]) -> dict[str, Any]:
    training_use = _mapping(record.get("training_use"))
    return {
        "schema_version": SIGNAL_SCHEMA_VERSION,
        "case_type": SIGNAL_RECORD_CASE_TYPE,
        "signal_id": str(record.get("signal_id") or ""),
        "example_id": str(record.get("example_id") or ""),
        "source_case": dict(_mapping(record.get("source_case"))),
        "model": dict(_mapping(record.get("model"))),
        "signals": dict(_mapping(record.get("signals"))),
        "signal_review": dict(_mapping(record.get("signal_review"))),
        "training_use": {
            "default_training_input": False,
            "approved_for_auxiliary_training": True,
            "review_status": str(training_use.get("review_status") or ""),
            "approved_signal_use": str(
                training_use.get("approved_signal_use")
                or "auxiliary_training_feature"
            ),
        },
    }


def _counts_by_model(records: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        counts[str(_mapping(record.get("model")).get("id") or "unknown")] += 1
    return dict(sorted(counts.items()))


def _manifest_relative_path(output_path: Path, manifest_dir: Path) -> str:
    rel = os.path.relpath(output_path, manifest_dir)
    return Path(rel).as_posix()


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
