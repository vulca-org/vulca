"""Build human review packs for real source-dependency labels."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_real_source_dependency_review_report"
ITEM_CASE_TYPE = "learning_real_source_dependency_review_item"
AUDIT_REPORT_CASE_TYPE = "learning_real_source_context_audit_report"
RECOVERY_AUDIT_REPORT_CASE_TYPE = "learning_real_source_context_recovery_audit_report"
DEFAULT_OUTPUT_DIR = Path("build/real_source_dependency_review")
DEFAULT_REPORT_NAME = "real_source_dependency_review_report.json"
DEFAULT_TEMPLATE_NAME = "real_source_dependency_review.template.jsonl"
DEFAULT_MARKDOWN_NAME = "real_source_dependency_review.md"

SOURCE_DEPENDENCY_VALUES: tuple[str, ...] = (
    "required",
    "helpful",
    "not_needed",
    "unknown",
)
DECISION_BASIS_VALUES: tuple[str, ...] = (
    "metadata_only",
    "source_context",
    "image_source",
    "artifact_source",
    "unknown",
)


def write_real_source_dependency_review_pack(
    *,
    audit_report_path: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    review_template_path: str | Path | None = None,
    markdown_path: str | Path | None = None,
) -> dict[str, Any]:
    """Write a safe human-review pack from a source-context audit report."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    resolved_template_path = (
        Path(review_template_path) if review_template_path else output / DEFAULT_TEMPLATE_NAME
    )
    resolved_markdown_path = (
        Path(markdown_path) if markdown_path else output / DEFAULT_MARKDOWN_NAME
    )
    source_report_path, source_report = _load_source_report(audit_report_path)
    audit_report = _load_detailed_audit_report(source_report_path, source_report)
    records = list(_records(audit_report))
    items = [_review_item(record) for record in records]
    items.sort(key=_item_sort_key)

    _write_jsonl(resolved_template_path, items)
    resolved_markdown_path.write_text(_markdown(items), encoding="utf-8")

    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": "needs_human_review" if items else "no_review_items",
        "inputs": {
            "audit_report_path": _safe_path(audit_report_path),
            "source_report_case_type": str(source_report.get("case_type") or ""),
            "audit_record_count": len(records),
        },
        "artifacts": {
            "report_path": _artifact_name(resolved_report_path, output),
            "review_template_jsonl_path": _artifact_name(resolved_template_path, output),
            "markdown_checklist_path": _artifact_name(resolved_markdown_path, output),
        },
        "summary": _summary(items, audit_record_count=len(records)),
        "allowed_values": {
            "source_dependency": list(SOURCE_DEPENDENCY_VALUES),
            "decision_basis": list(DECISION_BASIS_VALUES),
        },
        "safety": {
            "copies_raw_source_text": False,
            "copies_local_paths": False,
            "copies_private_refs": False,
            "calls_model_provider": False,
        },
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _load_source_report(path: str | Path) -> tuple[Path, Mapping[str, Any]]:
    report_path = Path(path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(report, Mapping):
        raise ValueError("source dependency review input must be a JSON object")
    case_type = str(report.get("case_type") or "")
    if case_type not in {AUDIT_REPORT_CASE_TYPE, RECOVERY_AUDIT_REPORT_CASE_TYPE}:
        raise ValueError(
            "source dependency review input case_type must be "
            f"{AUDIT_REPORT_CASE_TYPE!r} or {RECOVERY_AUDIT_REPORT_CASE_TYPE!r}"
        )
    return report_path, report


def _load_detailed_audit_report(
    source_report_path: Path,
    source_report: Mapping[str, Any],
) -> Mapping[str, Any]:
    case_type = str(source_report.get("case_type") or "")
    if case_type == AUDIT_REPORT_CASE_TYPE:
        return source_report

    artifacts = _mapping(source_report.get("artifacts"))
    audit_path = str(artifacts.get("audit_report_path") or "")
    if not audit_path:
        raise ValueError("recovery audit report requires artifacts.audit_report_path")
    resolved = Path(audit_path)
    if not resolved.is_absolute():
        resolved = source_report_path.parent / resolved
    audit_report = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(audit_report, Mapping):
        raise ValueError("resolved audit report must be a JSON object")
    if audit_report.get("case_type") != AUDIT_REPORT_CASE_TYPE:
        raise ValueError(
            f"resolved audit report case_type must be {AUDIT_REPORT_CASE_TYPE!r}"
        )
    return audit_report


def _records(audit_report: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    records = audit_report.get("records")
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
        raise ValueError("audit report records must be a list")
    return tuple(item for item in records if isinstance(item, Mapping))


def _review_item(record: Mapping[str, Any]) -> dict[str, Any]:
    source_context = _mapping(record.get("source_context"))
    predictions = _mapping(record.get("predictions"))
    targets = _mapping(record.get("targets"))
    suggested_source_dependency = _suggest_source_dependency(record)
    suggested_decision_basis = _suggest_decision_basis(record)
    review_priority = _review_priority(record)
    return {
        "schema_version": SCHEMA_VERSION,
        "case_type": ITEM_CASE_TYPE,
        "case_id": str(record.get("case_id") or ""),
        "source_case_type": str(record.get("case_type") or ""),
        "source": _safe_source(record),
        "current_labels": {
            "preferred_action": str(targets.get("preferred_action") or ""),
            "failure_type": str(targets.get("failure_type") or ""),
        },
        "source_context": {
            "available": bool(source_context.get("available")),
            "tags": list(source_context.get("tags") or []),
            "source_image_available": bool(source_context.get("source_image_available")),
            "source_artifact_available_count": int(
                source_context.get("source_artifact_available_count") or 0
            ),
            "source_artifact_text_file_count": int(
                source_context.get("source_artifact_text_file_count") or 0
            ),
        },
        "predictions": {
            "full_action": str(predictions.get("full_action") or ""),
            "without_auxiliary_signals_action": str(
                predictions.get("without_auxiliary_signals_action") or ""
            ),
            "action_changed_with_source_context": bool(
                predictions.get("action_changed_with_source_context")
            ),
            "full_matches_target": predictions.get("full_matches_target"),
            "without_auxiliary_signals_matches_target": predictions.get(
                "without_auxiliary_signals_matches_target"
            ),
        },
        "audit": {
            "candidate_reason": str(record.get("candidate_reason") or ""),
            "recommended_review_action": str(
                record.get("recommended_review_action") or ""
            ),
            "source_context_feature_match_count": int(
                _mapping(record.get("model_explanation")).get(
                    "source_context_feature_match_count"
                )
                or 0
            ),
        },
        "suggested_review": {
            "source_dependency": suggested_source_dependency,
            "decision_basis": suggested_decision_basis,
            "review_priority": review_priority,
        },
        "human_review": {
            "source_dependency": "unknown",
            "decision_basis": "unknown",
            "preferred_action_confirmed": None,
            "corrected_preferred_action": "",
            "review_notes": "",
        },
        "allowed_values": {
            "source_dependency": list(SOURCE_DEPENDENCY_VALUES),
            "decision_basis": list(DECISION_BASIS_VALUES),
        },
    }


def _safe_source(record: Mapping[str, Any]) -> dict[str, Any]:
    source = _mapping(record.get("source"))
    return {
        "source_id": str(source.get("source_id") or ""),
        "kind": str(source.get("kind") or ""),
        "privacy_scope": str(source.get("privacy_scope") or ""),
        "curation_status": str(source.get("curation_status") or ""),
        "record_index": int(source.get("record_index") or 0),
        "split": str(source.get("split") or ""),
    }


def _suggest_source_dependency(record: Mapping[str, Any]) -> str:
    reason = str(record.get("candidate_reason") or "")
    if reason == "prediction_changed_with_source_context":
        return "required"
    if reason == "source_context_used_no_action_change":
        return "helpful"
    if reason == "metadata_sufficient":
        return "not_needed"
    return "unknown"


def _suggest_decision_basis(record: Mapping[str, Any]) -> str:
    source_context = _mapping(record.get("source_context"))
    if not bool(source_context.get("available")):
        return "unknown"
    artifact_count = int(source_context.get("source_artifact_available_count") or 0)
    if artifact_count > 0:
        return "artifact_source"
    if bool(source_context.get("source_image_available")):
        return "image_source"
    tags = source_context.get("tags")
    if isinstance(tags, Sequence) and not isinstance(tags, (str, bytes)) and tags:
        return "source_context"
    return "metadata_only"


def _review_priority(record: Mapping[str, Any]) -> str:
    reason = str(record.get("candidate_reason") or "")
    if reason == "prediction_changed_with_source_context":
        return "high"
    if reason == "needs_source_context":
        return "recovery"
    if reason == "source_context_used_no_action_change":
        return "medium"
    return "low"


def _summary(items: Sequence[Mapping[str, Any]], *, audit_record_count: int) -> dict[str, Any]:
    return {
        "audit_record_count": audit_record_count,
        "review_item_count": len(items),
        "counts_by_suggested_source_dependency": _counts_suggested(
            items,
            "source_dependency",
        ),
        "counts_by_suggested_decision_basis": _counts_suggested(
            items,
            "decision_basis",
        ),
        "counts_by_review_priority": _counts_suggested(items, "review_priority"),
    }


def _counts_suggested(items: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        suggested = _mapping(item.get("suggested_review"))
        counts[str(suggested.get(key) or "unknown")] += 1
    return dict(sorted(counts.items()))


def _item_sort_key(item: Mapping[str, Any]) -> tuple[int, str]:
    priority = {
        "high": 0,
        "recovery": 1,
        "medium": 2,
        "low": 3,
    }.get(str(_mapping(item.get("suggested_review")).get("review_priority") or ""), 9)
    return (priority, str(item.get("case_id") or ""))


def _markdown(items: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "# Real Source Dependency Review",
        "",
        "| case_id | priority | suggested source_dependency | suggested decision_basis | current preferred_action | full/no-aux action | human source_dependency | human decision_basis | confirmed | notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        suggested = _mapping(item.get("suggested_review"))
        current_labels = _mapping(item.get("current_labels"))
        predictions = _mapping(item.get("predictions"))
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(str(item.get("case_id") or "")),
                    _md(str(suggested.get("review_priority") or "")),
                    _md(str(suggested.get("source_dependency") or "")),
                    _md(str(suggested.get("decision_basis") or "")),
                    _md(str(current_labels.get("preferred_action") or "")),
                    _md(
                        f"{str(predictions.get('full_action') or '')}/"
                        f"{str(predictions.get('without_auxiliary_signals_action') or '')}"
                    ),
                    "unknown",
                    "unknown",
                    "",
                    "",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Allowed `source_dependency`: required, helpful, not_needed, unknown.",
            "Allowed `decision_basis`: metadata_only, source_context, image_source, artifact_source, unknown.",
            "",
        ]
    )
    return "\n".join(lines)


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _write_jsonl(path: str | Path, records: Sequence[Mapping[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(dict(record), sort_keys=True, separators=(",", ":")))
            fh.write("\n")


def _artifact_name(path: str | Path, output_dir: str | Path) -> str:
    value = Path(path)
    try:
        return str(value.relative_to(Path(output_dir)))
    except ValueError:
        return value.name


def _safe_path(path: str | Path) -> str:
    value = Path(path)
    parts = value.parts
    if "build" in parts:
        return str(Path(*parts[parts.index("build") :]))
    if "docs" in parts:
        return str(Path(*parts[parts.index("docs") :]))
    return value.name


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
