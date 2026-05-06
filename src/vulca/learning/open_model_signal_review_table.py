"""Review table export for completed open-model signal records."""
from __future__ import annotations

import csv
import json
import shlex
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.learning.case_review import load_cases
from vulca.learning.open_model_signals import SIGNAL_RECORD_CASE_TYPE


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_open_model_signal_review_table"
ROW_CASE_TYPE = "learning_open_model_signal_review_row"
DEFAULT_OUTPUT_DIR = Path("build/open_model_signal_review_table")
DEFAULT_REPORT_NAME = "open_model_signal_review_table_report.json"
DEFAULT_JSONL_NAME = "open_model_signal_review_table.jsonl"
DEFAULT_CSV_NAME = "open_model_signal_review_table.csv"
DEFAULT_MARKDOWN_NAME = "open_model_signal_review_table.md"
DEFAULT_REVIEWABLE_STATUSES: tuple[str, ...] = ("completed",)
CSV_COLUMNS: tuple[str, ...] = (
    "signal_id",
    "example_id",
    "model_id",
    "model_role",
    "source_case_type",
    "case_id",
    "signal_status",
    "signal_source",
    "source_image_ref_kind",
    "source_image_width",
    "source_image_height",
    "caption_preview",
    "ocr_preview",
    "mask_count",
    "total_mask_area_pct",
    "boundary_complexity",
    "suggested_review_decision",
    "review_priority",
    "review_reason",
    "review_command_promote",
    "review_command_reject",
    "review_command_hold",
)
MARKDOWN_COLUMNS: tuple[str, ...] = (
    "signal_id",
    "model_id",
    "source_case_type",
    "case_id",
    "caption_preview",
    "ocr_preview",
    "mask_count",
    "suggested_review_decision",
)


def run_open_model_signal_review_table(
    *,
    input_path: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    reviewed_output_path: str | Path | None = None,
    reviewable_statuses: Sequence[str] = DEFAULT_REVIEWABLE_STATUSES,
    max_preview_chars: int = 120,
) -> dict[str, Any]:
    """Write JSONL/CSV/Markdown rows for human reviewable signal records."""
    source_path = Path(input_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    resolved_reviewed_output = (
        Path(reviewed_output_path)
        if reviewed_output_path is not None
        else _default_reviewed_output_path(source_path)
    )
    reviewable = {str(item) for item in reviewable_statuses}
    records = load_cases(source_path)
    status_counts = _status_counts(records)

    rows = [
        _build_row(
            record,
            input_path=source_path,
            reviewed_output_path=resolved_reviewed_output,
            max_preview_chars=max_preview_chars,
        )
        for record in records
        if _signal_status(record) in reviewable
    ]
    rows = sorted(
        rows,
        key=lambda item: (
            -int(item["review_priority"]),
            str(item["source_case_type"]),
            str(item["case_id"]),
            str(item["signal_id"]),
        ),
    )

    jsonl_path = output / DEFAULT_JSONL_NAME
    csv_path = output / DEFAULT_CSV_NAME
    markdown_path = output / DEFAULT_MARKDOWN_NAME
    _write_jsonl(jsonl_path, rows)
    _write_csv(csv_path, rows)
    _write_markdown(markdown_path, rows)

    included_status_counts = Counter(str(row["signal_status"]) for row in rows)
    excluded_status_counts = Counter(status_counts)
    for status, count in included_status_counts.items():
        excluded_status_counts[status] -= count
        if excluded_status_counts[status] <= 0:
            del excluded_status_counts[status]

    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": "ready_for_human_review",
        "inputs": {
            "input_path": str(source_path),
            "reviewable_statuses": sorted(reviewable),
            "max_preview_chars": int(max_preview_chars),
            "reviewed_output_path": str(resolved_reviewed_output),
        },
        "artifacts": {
            "report_path": str(resolved_report_path),
            "review_table_jsonl_path": str(jsonl_path),
            "review_table_csv_path": str(csv_path),
            "review_table_markdown_path": str(markdown_path),
        },
        "summary": {
            "input_record_count": len(records),
            "row_count": len(rows),
            "status_counts": dict(sorted(status_counts.items())),
            "excluded_status_counts": dict(sorted(excluded_status_counts.items())),
            "counts_by_model": _counts_by_key(rows, "model_id"),
            "counts_by_source_case_type": _counts_by_key(rows, "source_case_type"),
        },
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _build_row(
    record: Mapping[str, Any],
    *,
    input_path: Path,
    reviewed_output_path: Path,
    max_preview_chars: int,
) -> dict[str, Any]:
    if record.get("case_type") != SIGNAL_RECORD_CASE_TYPE:
        raise ValueError(
            f"signal record case_type must be {SIGNAL_RECORD_CASE_TYPE!r}"
        )
    signals = _mapping(record.get("signals"))
    model = _mapping(record.get("model"))
    source_case = _mapping(record.get("source_case"))
    source_image = _mapping(signals.get("source_image"))
    signal_id = str(record.get("signal_id") or "")
    signal_status = str(signals.get("status") or "")
    model_id = str(model.get("id") or "")
    caption_preview = _preview_text(
        signals.get("caption_candidates"),
        max_chars=max_preview_chars,
    )
    ocr_preview = _preview_text(signals.get("ocr_text"), max_chars=max_preview_chars)
    mask_count = signals.get("mask_count")
    total_area = signals.get("total_mask_area_pct")
    boundary_complexity = str(signals.get("boundary_complexity") or "")

    review_priority, review_reason = _review_priority(
        model_id=model_id,
        caption_preview=caption_preview,
        ocr_preview=ocr_preview,
        mask_count=mask_count,
        signal_status=signal_status,
    )
    base = {
        "schema_version": SCHEMA_VERSION,
        "row_case_type": ROW_CASE_TYPE,
        "signal_id": signal_id,
        "example_id": str(record.get("example_id") or ""),
        "model_id": model_id,
        "model_role": str(model.get("model_role") or ""),
        "source_case_type": str(source_case.get("case_type") or ""),
        "case_id": str(source_case.get("case_id") or ""),
        "signal_status": signal_status,
        "signal_source": str(signals.get("signal_source") or ""),
        "source_image_ref_kind": str(source_image.get("ref_kind") or ""),
        "source_image_width": source_image.get("width"),
        "source_image_height": source_image.get("height"),
        "caption_preview": caption_preview,
        "ocr_preview": ocr_preview,
        "mask_count": mask_count,
        "total_mask_area_pct": total_area,
        "boundary_complexity": boundary_complexity,
        "suggested_review_decision": "hold",
        "review_priority": review_priority,
        "review_reason": review_reason,
    }
    base.update(
        {
            "review_command_promote": _review_command(
                input_path=input_path,
                reviewed_output_path=reviewed_output_path,
                signal_id=signal_id,
                decision="promote",
            ),
            "review_command_reject": _review_command(
                input_path=input_path,
                reviewed_output_path=reviewed_output_path,
                signal_id=signal_id,
                decision="reject",
            ),
            "review_command_hold": _review_command(
                input_path=input_path,
                reviewed_output_path=reviewed_output_path,
                signal_id=signal_id,
                decision="hold",
            ),
        }
    )
    return base


def _review_command(
    *,
    input_path: Path,
    reviewed_output_path: Path,
    signal_id: str,
    decision: str,
) -> str:
    parts = [
        "python",
        "scripts/open_model_signal_review.py",
        "review",
        "--input",
        str(input_path),
        "--output",
        str(reviewed_output_path),
        "--signal-id",
        signal_id,
        "--decision",
        decision,
        "--reviewer",
        "human",
    ]
    return " ".join(shlex.quote(part) for part in parts)


def _review_priority(
    *,
    model_id: str,
    caption_preview: str,
    ocr_preview: str,
    mask_count: Any,
    signal_status: str,
) -> tuple[int, str]:
    score = 40
    reasons = [f"signal_status:{signal_status}"]
    if model_id == "segment_anything_sam_vit":
        score += 30
        reasons.append("mask_signal")
    if mask_count not in (None, ""):
        score += 10
        reasons.append("has_mask_count")
    if caption_preview:
        score += 10
        reasons.append("has_caption")
    if ocr_preview:
        score += 5
        reasons.append("has_ocr")
    return min(score, 100), "; ".join(reasons)


def _status_counts(records: Sequence[Mapping[str, Any]]) -> Counter[str]:
    return Counter(_signal_status(record) for record in records)


def _signal_status(record: Mapping[str, Any]) -> str:
    return str(_mapping(record.get("signals")).get("status") or "unknown")


def _counts_by_key(rows: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts[str(row.get(key) or "unknown")] += 1
    return dict(sorted(counts.items()))


def _preview_text(value: Any, *, max_chars: int) -> str:
    text = " | ".join(_flatten_text(value))
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return f"{text[: max(0, max_chars - 1)].rstrip()}..."


def _flatten_text(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Mapping):
        texts: list[str] = []
        for child in value.values():
            texts.extend(_flatten_text(child))
        return texts
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        texts = []
        for item in value:
            texts.extend(_flatten_text(item))
        return texts
    return [str(value)]


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))


def _write_markdown(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    lines = [
        "# Open-Model Signal Review Table",
        "",
        "| " + " | ".join(MARKDOWN_COLUMNS) + " |",
        "| " + " | ".join("---" for _ in MARKDOWN_COLUMNS) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(_markdown_cell(row.get(column)) for column in MARKDOWN_COLUMNS)
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _markdown_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|")


def _default_reviewed_output_path(input_path: Path) -> Path:
    if input_path.suffix == ".jsonl":
        return input_path.with_name(f"{input_path.stem}.reviewed{input_path.suffix}")
    return input_path.with_name(f"{input_path.name}.reviewed.jsonl")


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
