"""Safe re-intake task packs for real user source asset gaps."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_real_user_asset_reintake_report"
COVERAGE_REPORT_CASE_TYPE = "learning_real_user_asset_coverage_report"
DEFAULT_OUTPUT_DIR = Path("build/real_user_asset_reintake")
DEFAULT_REPORT_NAME = "real_user_asset_reintake_report.json"
DEFAULT_MARKDOWN_NAME = "real_user_asset_reintake_tasks.md"
TASK_STATUSES: frozenset[str] = frozenset(
    {
        "invalid_image",
        "missing_source_reference",
        "needs_private_asset_map",
        "path_missing",
        "remote_url_unsupported",
        "source_hint_only",
    }
)


def write_real_user_asset_reintake_pack(
    *,
    coverage_report_path: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
) -> dict[str, Any]:
    """Write JSON/Markdown tasks for real user cases missing source assets."""
    coverage_path = Path(coverage_report_path)
    coverage_report = json.loads(coverage_path.read_text(encoding="utf-8"))
    _validate_coverage_report(coverage_report)
    records = [
        _mapping(record)
        for record in coverage_report.get("records", []) or []
        if isinstance(record, Mapping)
    ]
    tasks = sorted(
        (_build_task(record) for record in records if _needs_task(record)),
        key=lambda item: (
            -int(item["priority"]),
            str(item["asset_status"]),
            str(item["case_id"]),
        ),
    )

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    markdown_path = output / DEFAULT_MARKDOWN_NAME
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": "needs_user_assets" if tasks else "ready_for_open_model_signal_run",
        "inputs": {
            "coverage_report_path": _safe_path(coverage_report_path),
        },
        "artifacts": {
            "report_path": _artifact_name(resolved_report_path, output),
            "markdown_path": _artifact_name(markdown_path, output),
        },
        "summary": _summary(records, tasks),
        "tasks": tasks,
    }
    _write_markdown(markdown_path, report)
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _validate_coverage_report(report: Mapping[str, Any]) -> None:
    if report.get("case_type") != COVERAGE_REPORT_CASE_TYPE:
        raise ValueError(
            f"coverage report case_type must be {COVERAGE_REPORT_CASE_TYPE!r}"
        )
    records = report.get("records")
    if not isinstance(records, list):
        raise ValueError("coverage report records must be a list")


def _needs_task(record: Mapping[str, Any]) -> bool:
    if bool(record.get("open_model_runnable")):
        return False
    return str(record.get("asset_status") or "") in TASK_STATUSES


def _build_task(record: Mapping[str, Any]) -> dict[str, Any]:
    asset_status = str(record.get("asset_status") or "")
    source = _mapping(record.get("source"))
    return {
        "case_id": str(record.get("case_id") or ""),
        "case_type": str(record.get("case_type") or ""),
        "asset_status": asset_status,
        "priority": _priority(asset_status),
        "source": {
            "source_id": str(source.get("source_id") or ""),
            "kind": str(source.get("kind") or ""),
            "privacy_scope": str(source.get("privacy_scope") or ""),
            "record_index": int(source.get("record_index") or 0),
        },
        "required_action": _required_action(asset_status),
        "required_user_asset": _required_user_asset(asset_status),
        "path_hints": dict(_mapping(record.get("path_hints"))),
        "safe_handling": {
            "do_not_commit_local_paths": True,
            "use_private_asset_map_for_local_files": True,
            "case_record_should_use_private_uri": True,
        },
        "suggested_next_command": _suggested_next_command(asset_status),
    }


def _priority(asset_status: str) -> int:
    return {
        "needs_private_asset_map": 90,
        "invalid_image": 85,
        "path_missing": 80,
        "source_hint_only": 70,
        "remote_url_unsupported": 65,
        "missing_source_reference": 60,
    }.get(asset_status, 50)


def _required_action(asset_status: str) -> str:
    return {
        "invalid_image": "replace_invalid_image_asset",
        "missing_source_reference": "add_source_image_ref",
        "needs_private_asset_map": "provide_private_asset_map",
        "path_missing": "fix_or_map_source_path",
        "remote_url_unsupported": "download_or_cache_source_asset",
        "source_hint_only": "re_intake_with_source_image",
    }.get(asset_status, "manual_review")


def _required_user_asset(asset_status: str) -> str:
    return {
        "invalid_image": "replacement_source_image",
        "missing_source_reference": "source_image",
        "needs_private_asset_map": "private_asset_map_entry",
        "path_missing": "existing_source_image_path_or_private_map_entry",
        "remote_url_unsupported": "local_cached_source_image",
        "source_hint_only": "source_image_or_source_artifact",
    }.get(asset_status, "manual_review_context")


def _suggested_next_command(asset_status: str) -> str:
    if asset_status == "needs_private_asset_map":
        return "update local private asset map, then rerun real_user_asset_coverage.py"
    if asset_status == "source_hint_only":
        return "re-run user case intake with an explicit source_image or source artifact"
    if asset_status == "missing_source_reference":
        return "add a private source_image reference during re-intake"
    return "fix the asset locally, then rerun real_user_asset_coverage.py"


def _summary(
    records: Sequence[Mapping[str, Any]],
    tasks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "coverage_record_count": len(records),
        "task_count": len(tasks),
        "ready_count": sum(1 for record in records if bool(record.get("open_model_runnable"))),
        "counts_by_action": _counts_by(tasks, "required_action"),
        "counts_by_asset_status": _counts_by(tasks, "asset_status"),
    }


def _counts_by(records: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(str(record.get(key) or "unknown") for record in records)
    return dict(sorted(counts.items()))


def _write_markdown(path: Path, report: Mapping[str, Any]) -> None:
    tasks = [
        _mapping(task)
        for task in report.get("tasks", []) or []
        if isinstance(task, Mapping)
    ]
    lines = [
        "# Real User Asset Re-intake Tasks",
        "",
        f"Status: {report.get('status')}",
        f"Tasks: {_mapping(report.get('summary')).get('task_count', 0)}",
        "",
        "| priority | case_id | case_type | asset_status | required_user_asset | required_action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for task in tasks:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(task.get("priority") or ""),
                    str(task.get("case_id") or ""),
                    str(task.get("case_type") or ""),
                    str(task.get("asset_status") or ""),
                    str(task.get("required_user_asset") or ""),
                    str(task.get("required_action") or ""),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Local paths stay outside committed case records. Use private asset maps or private URI references for user-provided files.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _safe_path(path: str | Path) -> str:
    value = Path(path)
    parts = value.parts
    if "docs" in parts:
        index = parts.index("docs")
        return str(Path(*parts[index:]))
    if "build" in parts:
        index = parts.index("build")
        return str(Path(*parts[index:]))
    return value.name


def _artifact_name(path: Path, output_dir: Path) -> str:
    try:
        return str(path.relative_to(output_dir))
    except ValueError:
        return path.name


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
