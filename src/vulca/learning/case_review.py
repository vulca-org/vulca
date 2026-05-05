"""Lightweight review labeling for versioned case JSONL logs."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from vulca.layers.redraw_cases import (
    CASE_TYPE as REDRAW_CASE_TYPE,
    utc_now_iso,
    validate_failure_type as validate_redraw_failure_type,
    validate_preferred_action as validate_redraw_preferred_action,
)


_UNSET = object()


@dataclass(frozen=True)
class CaseReviewSpec:
    """Validation hooks for a reviewable case type."""

    case_type: str
    validate_failure_type: Callable[[str], str]
    validate_preferred_action: Callable[[str], str]


@dataclass(frozen=True)
class ReviewResult:
    """Result metadata for a case-log review update."""

    case_id: str
    output_path: str
    updated: bool
    sidecar_path: str = ""


CASE_REVIEW_SPECS: dict[str, CaseReviewSpec] = {
    REDRAW_CASE_TYPE: CaseReviewSpec(
        case_type=REDRAW_CASE_TYPE,
        validate_failure_type=validate_redraw_failure_type,
        validate_preferred_action=validate_redraw_preferred_action,
    )
}


def load_cases(path: str | Path) -> list[dict[str, Any]]:
    """Read newline-delimited JSON case records."""
    case_path = Path(path)
    records: list[dict[str, Any]] = []
    with case_path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            value = json.loads(stripped)
            if not isinstance(value, dict):
                raise ValueError(f"{case_path}:{line_no}: expected JSON object")
            records.append(value)
    return records


def write_cases(path: str | Path, cases: list[Mapping[str, Any]]) -> str:
    """Write newline-delimited JSON case records."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        for record in cases:
            fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
            fh.write("\n")
    return str(output_path)


def default_review_output_path(input_path: str | Path) -> str:
    """Return a non-destructive default output path for reviewed case logs."""
    path = Path(input_path)
    if path.suffix == ".jsonl":
        return str(path.with_name(f"{path.stem}.reviewed{path.suffix}"))
    return str(path.with_name(f"{path.name}.reviewed.jsonl"))


def parse_human_accept(value: str) -> bool:
    """Parse a CLI boolean for human_accept."""
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "accept", "accepted"}:
        return True
    if normalized in {"0", "false", "no", "n", "reject", "rejected"}:
        return False
    raise ValueError("human_accept must be true/false")


def review_case_log(
    input_path: str | Path,
    *,
    case_id: str,
    output_path: str | Path | None = None,
    human_accept: bool | object = _UNSET,
    failure_type: str | None = None,
    preferred_action: str | None = None,
    reviewer: str | None = None,
    reviewed_at: str | None = None,
    notes: str | None = None,
    sidecar_output_path: str | Path | None = None,
) -> ReviewResult:
    """Update one case review block and write reviewed JSONL.

    Original record fields are preserved. Only the nested ``review`` object on
    the matching ``case_id`` is merged with supplied labels.
    """
    if not case_id:
        raise ValueError("case_id is required")

    cases = load_cases(input_path)
    output = str(output_path or default_review_output_path(input_path))
    found = False
    sidecar_record: dict[str, Any] | None = None

    for record in cases:
        if str(record.get("case_id", "")) != case_id:
            continue

        found = True
        spec = _spec_for_record(record)
        review = dict(record.get("review", {}) or {})
        changed = False

        if human_accept is not _UNSET:
            review["human_accept"] = bool(human_accept)
            changed = True
        if failure_type is not None:
            review["failure_type"] = spec.validate_failure_type(str(failure_type))
            changed = True
        if preferred_action is not None:
            review["preferred_action"] = spec.validate_preferred_action(
                str(preferred_action)
            )
            changed = True
        if reviewer is not None:
            review["reviewer"] = str(reviewer)
            changed = True
        if notes is not None:
            review["notes"] = str(notes)
            changed = True
        if reviewed_at is not None:
            review["reviewed_at"] = str(reviewed_at)
            changed = True
        elif changed:
            review["reviewed_at"] = str(review.get("reviewed_at") or utc_now_iso())

        record["review"] = review
        sidecar_record = {
            "case_id": case_id,
            "case_type": str(record.get("case_type", "")),
            "review": review,
        }
        break

    if not found:
        raise ValueError(f"case_id {case_id!r} not found in {input_path}")

    write_cases(output, cases)
    sidecar_path = ""
    if sidecar_output_path:
        sidecar_path = _write_review_sidecar(sidecar_output_path, sidecar_record)
    return ReviewResult(
        case_id=case_id,
        output_path=output,
        updated=True,
        sidecar_path=sidecar_path,
    )


def _spec_for_record(record: Mapping[str, Any]) -> CaseReviewSpec:
    case_type = str(record.get("case_type", ""))
    spec = CASE_REVIEW_SPECS.get(case_type)
    if spec is None:
        supported = sorted(CASE_REVIEW_SPECS)
        raise ValueError(
            f"unsupported case_type {case_type!r}; expected one of {supported}"
        )
    return spec


def _write_review_sidecar(
    sidecar_output_path: str | Path,
    record: Mapping[str, Any] | None,
) -> str:
    if record is None:
        raise ValueError("cannot write sidecar without a reviewed case")
    path = Path(sidecar_output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
        fh.write("\n")
    return str(path)
