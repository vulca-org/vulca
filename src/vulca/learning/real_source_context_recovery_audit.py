"""Run private source recovery and real source-context audit as one workflow."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.learning.real_source_context_audit import (
    DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    run_real_source_context_audit_report,
)
from vulca.learning.real_user_asset_map_recovery import (
    DEFAULT_ASSET_MAP_NAME as SOURCE_IMAGE_ASSET_MAP_NAME,
)
from vulca.learning.real_user_asset_map_recovery import (
    recover_real_user_private_asset_map,
)
from vulca.learning.real_user_source_artifact_map_recovery import (
    DEFAULT_ASSET_MAP_NAME as SOURCE_ARTIFACT_ASSET_MAP_NAME,
)
from vulca.learning.real_user_source_artifact_map_recovery import (
    recover_real_user_private_source_artifact_map,
)


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_real_source_context_recovery_audit_report"
DEFAULT_OUTPUT_DIR = Path("build/real_source_context_recovery_audit")
DEFAULT_REPORT_NAME = "real_source_context_recovery_audit_report.json"
SOURCE_ARTIFACT_RECOVERY_DIR_NAME = "source_artifact_recovery"
SOURCE_IMAGE_RECOVERY_DIR_NAME = "source_image_recovery"
AUDIT_DIR_NAME = "audit"


def run_real_source_context_recovery_audit(
    *,
    repo_root: str | Path,
    case_source_manifest_path: str | Path = DEFAULT_COMBINED_CASE_SOURCE_MANIFEST,
    artifact_search_roots: Sequence[str | Path] = (),
    image_search_roots: Sequence[str | Path] = (),
    artifact_filename_aliases: Mapping[str, str] | None = None,
    image_filename_aliases: Mapping[str, str] | None = None,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    include_local_seeds: bool = True,
    train_split: str = "train",
) -> dict[str, Any]:
    """Recover local private source maps, run audit, and write one safe report."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = Path(report_path) if report_path else output / DEFAULT_REPORT_NAME

    source_artifact_output = output / SOURCE_ARTIFACT_RECOVERY_DIR_NAME
    source_image_output = output / SOURCE_IMAGE_RECOVERY_DIR_NAME
    source_artifact_report = recover_real_user_private_source_artifact_map(
        repo_root=repo_root,
        case_source_manifest_path=case_source_manifest_path,
        search_roots=artifact_search_roots,
        filename_aliases=artifact_filename_aliases,
        output_dir=source_artifact_output,
    )
    source_image_report = recover_real_user_private_asset_map(
        repo_root=repo_root,
        case_source_manifest_path=case_source_manifest_path,
        search_roots=image_search_roots,
        filename_aliases=image_filename_aliases,
        output_dir=source_image_output,
    )

    private_asset_maps = [
        source_artifact_output / SOURCE_ARTIFACT_ASSET_MAP_NAME,
        source_image_output / SOURCE_IMAGE_ASSET_MAP_NAME,
    ]
    audit_report = run_real_source_context_audit_report(
        repo_root=repo_root,
        case_source_manifest_path=case_source_manifest_path,
        private_asset_map_paths=private_asset_maps,
        output_dir=output / AUDIT_DIR_NAME,
        include_local_seeds=include_local_seeds,
        train_split=train_split,
    )

    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": _status(audit_report),
        "inputs": {
            "repo_root": Path(repo_root).name,
            "case_source_manifest_path": _safe_path(case_source_manifest_path),
            "artifact_search_root_count": len(artifact_search_roots),
            "image_search_root_count": len(image_search_roots),
            "artifact_filename_alias_count": len(artifact_filename_aliases or {}),
            "image_filename_alias_count": len(image_filename_aliases or {}),
            "include_local_seeds": bool(include_local_seeds),
            "train_split": train_split,
        },
        "artifacts": {
            "report_path": _artifact_name(resolved_report_path, output),
            "source_artifact_recovery_report_path": _artifact_name(
                source_artifact_output
                / "real_user_source_artifact_recovery_report.json",
                output,
            ),
            "source_artifact_private_asset_map_path": _artifact_name(
                source_artifact_output / SOURCE_ARTIFACT_ASSET_MAP_NAME,
                output,
            ),
            "source_image_recovery_report_path": _artifact_name(
                source_image_output / "real_user_private_asset_recovery_report.json",
                output,
            ),
            "source_image_private_asset_map_path": _artifact_name(
                source_image_output / SOURCE_IMAGE_ASSET_MAP_NAME,
                output,
            ),
            "audit_report_path": _artifact_name(
                output / AUDIT_DIR_NAME / "real_source_context_audit_report.json",
                output,
            ),
        },
        "summary": _summary(
            source_artifact_report=source_artifact_report,
            source_image_report=source_image_report,
            audit_report=audit_report,
        ),
        "source_artifact_recovery": _compact_recovery(source_artifact_report),
        "source_image_recovery": _compact_recovery(source_image_report),
        "audit": _compact_audit(audit_report),
        "safe_handling": {
            "private_asset_maps_contain_local_paths": True,
            "do_not_commit_private_asset_maps": True,
            "report_omits_local_paths": True,
            "report_omits_private_refs": True,
            "calls_model_provider": False,
        },
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _summary(
    *,
    source_artifact_report: Mapping[str, Any],
    source_image_report: Mapping[str, Any],
    audit_report: Mapping[str, Any],
) -> dict[str, int]:
    artifact_summary = _mapping(source_artifact_report.get("summary"))
    image_summary = _mapping(source_image_report.get("summary"))
    audit_summary = _mapping(audit_report.get("summary"))
    return {
        "private_source_artifact_ref_count": int(
            artifact_summary.get("private_source_artifact_ref_count") or 0
        ),
        "private_source_artifact_recovered_count": int(
            artifact_summary.get("recovered_count") or 0
        ),
        "private_source_image_ref_count": int(
            image_summary.get("private_source_ref_count") or 0
        ),
        "private_source_image_recovered_count": int(
            image_summary.get("recovered_count") or 0
        ),
        "real_user_case_count": int(audit_summary.get("real_user_case_count") or 0),
        "source_context_available_count": int(
            audit_summary.get("source_context_available_count") or 0
        ),
        "source_context_unavailable_count": int(
            audit_summary.get("source_context_unavailable_count") or 0
        ),
        "review_candidate_count": int(audit_summary.get("review_candidate_count") or 0),
    }


def _compact_recovery(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "case_type": str(report.get("case_type") or ""),
        "status": str(report.get("status") or ""),
        "summary": dict(_mapping(report.get("summary"))),
        "artifacts": dict(_mapping(report.get("artifacts"))),
    }


def _compact_audit(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "case_type": str(report.get("case_type") or ""),
        "status": str(report.get("status") or ""),
        "summary": dict(_mapping(report.get("summary"))),
        "counts_by_candidate_reason": dict(
            _mapping(report.get("counts_by_candidate_reason"))
        ),
        "counts_by_recommended_review_action": dict(
            _mapping(report.get("counts_by_recommended_review_action"))
        ),
        "artifacts": dict(_mapping(report.get("artifacts"))),
    }


def _status(audit_report: Mapping[str, Any]) -> str:
    summary = _mapping(audit_report.get("summary"))
    unavailable = int(summary.get("source_context_unavailable_count") or 0)
    if unavailable:
        return "needs_more_source_recovery"
    return "source_context_ready_for_review"


def _artifact_name(path: str | Path, output_dir: str | Path) -> str:
    value = Path(path)
    try:
        return str(value.relative_to(Path(output_dir)))
    except ValueError:
        return value.name


def _safe_path(path: str | Path) -> str:
    value = Path(path)
    parts = value.parts
    if "docs" in parts:
        return str(Path(*parts[parts.index("docs") :]))
    return value.name


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
