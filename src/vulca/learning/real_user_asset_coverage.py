"""Provider-free asset coverage reporting for reviewed real user cases."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from PIL import Image, UnidentifiedImageError

from vulca.learning.florence_signal_runner import resolve_case_source_image_path
from vulca.learning.private_asset_map import load_private_asset_maps
from vulca.learning.tiny_dataset import build_tiny_dataset_examples


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_real_user_asset_coverage_report"
DEFAULT_OUTPUT_PATH = Path("build/real_user_asset_coverage/coverage_report.json")


def run_real_user_asset_coverage_report(
    *,
    repo_root: str | Path,
    case_source_manifest_path: str | Path,
    private_asset_map_paths: Sequence[str | Path] = (),
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Write a safe coverage report for source images in real user cases."""
    root = Path(repo_root)
    private_asset_map = load_private_asset_maps(private_asset_map_paths)
    examples = build_tiny_dataset_examples(
        repo_root=root,
        case_source_manifest_path=case_source_manifest_path,
        include_local_seeds=False,
    )
    records = [
        _coverage_record(
            example,
            repo_root=root,
            private_asset_map=private_asset_map,
        )
        for example in examples
    ]
    summary = _summary(records)
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "inputs": {
            "repo_root": _safe_repo_root(root),
            "case_source_manifest_path": _safe_path(case_source_manifest_path),
            "private_asset_map_count": len(private_asset_map_paths),
        },
        "summary": summary,
        "counts_by_case_type": _counts_by(records, "case_type"),
        "counts_by_asset_status": _counts_by(records, "asset_status"),
        "records": records,
        "recommended_next_actions": _recommended_next_actions(summary),
    }

    output = Path(output_path) if output_path is not None else root / DEFAULT_OUTPUT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _coverage_record(
    example: Mapping[str, Any],
    *,
    repo_root: Path,
    private_asset_map: Mapping[str, str | Path],
) -> dict[str, Any]:
    source_case = _mapping(example.get("source_case"))
    source = _mapping(example.get("source"))
    case_record = _mapping(_mapping(example.get("input")).get("case_record"))
    source_ref = _source_image_ref(case_record)
    resolved = resolve_case_source_image_path(
        case_record,
        repo_root=repo_root,
        private_asset_map=private_asset_map,
    )
    image_probe = _image_probe(resolved.path) if resolved.path is not None else {}
    hint_stats = _path_hint_stats(case_record)
    asset_status = _asset_status(
        source_ref=source_ref,
        ref_kind=resolved.ref_kind,
        resolved_path=resolved.path,
        image_probe=image_probe,
        hint_stats=hint_stats,
    )

    record = {
        "case_id": str(source_case.get("case_id") or ""),
        "case_type": str(source_case.get("case_type") or ""),
        "source": {
            "source_id": str(source.get("source_id") or ""),
            "kind": str(source.get("kind") or ""),
            "privacy_scope": str(source.get("privacy_scope") or ""),
            "record_index": int(source.get("index") or 0),
        },
        "asset_status": asset_status,
        "open_model_runnable": asset_status == "available",
        "source_image": {
            "has_ref": bool(source_ref),
            "ref_kind": resolved.ref_kind,
            "available": asset_status == "available",
        },
        "path_hints": hint_stats,
        "next_action": _next_action_for_status(asset_status),
    }
    if source_ref.startswith("private://"):
        record["source_image"]["private_ref_digest"] = _digest(source_ref)
    if image_probe:
        record["image_probe"] = image_probe
    return record


def _asset_status(
    *,
    source_ref: str,
    ref_kind: str,
    resolved_path: Path | None,
    image_probe: Mapping[str, Any],
    hint_stats: Mapping[str, int],
) -> str:
    if resolved_path is not None:
        if image_probe.get("valid_image") is True:
            return "available"
        return "invalid_image"
    if ref_kind == "private_uri":
        return "needs_private_asset_map"
    if ref_kind == "remote_url":
        return "remote_url_unsupported"
    if ref_kind in {"repo_relative", "absolute_path"} and source_ref:
        return "path_missing"
    if int(hint_stats.get("source_path_hint_count") or 0) > 0:
        return "source_hint_only"
    return "missing_source_reference"


def _image_probe(path: Path) -> dict[str, Any]:
    try:
        with Image.open(path) as image:
            return {
                "valid_image": True,
                "width": int(image.width),
                "height": int(image.height),
                "format": str(image.format or "").lower(),
            }
    except (OSError, UnidentifiedImageError):
        return {"valid_image": False}


def _source_image_ref(case_record: Mapping[str, Any]) -> str:
    direct = str(case_record.get("source_image") or "")
    if direct:
        return direct
    for key in ("input", "inputs"):
        nested = case_record.get(key)
        if isinstance(nested, Mapping):
            value = str(nested.get("source_image") or "")
            if value:
                return value
    return ""


def _path_hint_stats(case_record: Mapping[str, Any]) -> dict[str, int]:
    stats = Counter()

    def walk(value: Any, *, key: str = "") -> None:
        if isinstance(value, Mapping):
            for child_key, child in value.items():
                walk(child, key=str(child_key))
            return
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            for child in value:
                walk(child, key=key)
            return
        if not isinstance(value, str):
            return
        if key.endswith("source_path_hint") and value:
            stats["source_path_hint_count"] += 1
        if value.startswith("private://"):
            stats["private_ref_count"] += 1
        elif value.startswith("http://") or value.startswith("https://"):
            stats["remote_ref_count"] += 1

    walk(case_record)
    return {
        "source_path_hint_count": stats["source_path_hint_count"],
        "private_ref_count": stats["private_ref_count"],
        "remote_ref_count": stats["remote_ref_count"],
    }


def _summary(records: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    status_counts = Counter(str(record.get("asset_status") or "") for record in records)
    available = status_counts["available"]
    return {
        "example_count": len(records),
        "available_source_image_count": available,
        "open_model_runnable_count": available,
        "needs_private_asset_map_count": status_counts["needs_private_asset_map"],
        "source_hint_only_count": status_counts["source_hint_only"],
        "missing_source_reference_count": status_counts["missing_source_reference"],
        "invalid_image_count": status_counts["invalid_image"],
    }


def _recommended_next_actions(summary: Mapping[str, int]) -> list[str]:
    actions: list[str] = []
    if int(summary.get("needs_private_asset_map_count") or 0) > 0:
        actions.append("provide_private_asset_map_for_unmapped_private_refs")
    if int(summary.get("source_hint_only_count") or 0) > 0:
        actions.append("re_intake_brief_cases_with_source_image_or_artifact_path")
    if int(summary.get("missing_source_reference_count") or 0) > 0:
        actions.append("add_source_image_refs_for_visual_cases")
    if not actions:
        actions.append("ready_for_open_model_signal_run")
    return actions


def _next_action_for_status(asset_status: str) -> str:
    return {
        "available": "ready_for_open_model_signal_run",
        "needs_private_asset_map": "provide_private_asset_map",
        "source_hint_only": "re_intake_with_source_image",
        "missing_source_reference": "add_source_image_ref",
        "path_missing": "fix_or_map_source_path",
        "invalid_image": "replace_invalid_image_asset",
        "remote_url_unsupported": "download_or_cache_source_asset",
    }.get(asset_status, "manual_review")


def _counts_by(records: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(str(record.get(key) or "unknown") for record in records)
    return dict(sorted(counts.items()))


def _safe_path(path: str | Path) -> str:
    value = Path(path)
    parts = value.parts
    if "docs" in parts:
        docs_index = parts.index("docs")
        return str(Path(*parts[docs_index:]))
    if "build" in parts:
        build_index = parts.index("build")
        return str(Path(*parts[build_index:]))
    return value.name


def _safe_repo_root(path: str | Path) -> str:
    return Path(path).name


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
