"""Provider-free source artifact coverage for reviewed real user cases."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from vulca.learning.private_asset_map import load_private_asset_maps
from vulca.learning.tiny_dataset import build_tiny_dataset_examples


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_real_user_source_artifact_coverage_report"
DEFAULT_OUTPUT_PATH = Path(
    "build/real_user_source_artifact_coverage/source_artifact_coverage_report.json"
)


def run_real_user_source_artifact_coverage_report(
    *,
    repo_root: str | Path,
    case_source_manifest_path: str | Path,
    private_artifact_map_paths: Sequence[str | Path] = (),
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Write a safe report for non-image source artifacts in real user cases."""
    root = Path(repo_root)
    private_artifact_map = load_private_asset_maps(private_artifact_map_paths)
    examples = build_tiny_dataset_examples(
        repo_root=root,
        case_source_manifest_path=case_source_manifest_path,
        include_local_seeds=False,
    )
    records = [
        _coverage_record(
            example,
            repo_root=root,
            private_artifact_map=private_artifact_map,
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
            "private_artifact_map_count": len(private_artifact_map_paths),
        },
        "summary": summary,
        "counts_by_case_type": _counts_by(records, "case_type"),
        "counts_by_artifact_status": _counts_by(records, "artifact_status"),
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
    private_artifact_map: Mapping[str, str | Path],
) -> dict[str, Any]:
    source_case = _mapping(example.get("source_case"))
    source = _mapping(example.get("source"))
    case_record = _mapping(_mapping(example.get("input")).get("case_record"))
    source_image_ref = _source_image_ref(case_record)
    raw_refs = _artifact_refs(case_record)
    artifacts = [
        _resolve_artifact_ref(
            ref,
            repo_root=repo_root,
            private_artifact_map=private_artifact_map,
        )
        for ref in raw_refs
    ]
    artifact_status = _artifact_status(
        source_image_ref=source_image_ref,
        artifact_records=artifacts,
    )
    return {
        "case_id": str(source_case.get("case_id") or ""),
        "case_type": str(source_case.get("case_type") or ""),
        "source": {
            "source_id": str(source.get("source_id") or ""),
            "kind": str(source.get("kind") or ""),
            "privacy_scope": str(source.get("privacy_scope") or ""),
            "record_index": int(source.get("index") or 0),
        },
        "artifact_status": artifact_status,
        "source_context_available": artifact_status in {
            "available",
            "source_image_present",
        },
        "source_image": {
            "has_ref": bool(source_image_ref),
            "private_ref_digest": _digest(source_image_ref)
            if source_image_ref.startswith("private://")
            else "",
        },
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "next_action": _next_action_for_status(artifact_status),
    }


def _artifact_refs(case_record: Mapping[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    source_refs = case_record.get("source_refs")
    if isinstance(source_refs, Mapping):
        for key, value in source_refs.items():
            refs.extend(_refs_from_value(value, label=f"source_refs.{key}"))

    source_summary = case_record.get("source_summary")
    if isinstance(source_summary, Mapping):
        value = source_summary.get("source_path_hint")
        refs.extend(_refs_from_value(value, label="source_summary.source_path_hint"))

    inputs = case_record.get("inputs")
    if not isinstance(inputs, Mapping):
        inputs = case_record.get("input")
    if isinstance(inputs, Mapping):
        prompt_stack = inputs.get("prompt_stack")
        if isinstance(prompt_stack, Mapping):
            for key, value in prompt_stack.items():
                if _is_prompt_artifact_key(str(key)):
                    refs.extend(_refs_from_value(value, label=f"inputs.prompt_stack.{key}"))
    return refs


def _refs_from_value(value: Any, *, label: str) -> list[dict[str, str]]:
    if isinstance(value, str):
        if value:
            return [{"label": label, "ref": value}]
        return []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        refs: list[dict[str, str]] = []
        for index, item in enumerate(value):
            if isinstance(item, str) and item:
                refs.append({"label": f"{label}[{index}]", "ref": item})
        return refs
    return []


def _is_prompt_artifact_key(key: str) -> bool:
    return key.endswith("_path") or key.endswith("_paths") or key.endswith("_refs")


def _resolve_artifact_ref(
    item: Mapping[str, str],
    *,
    repo_root: Path,
    private_artifact_map: Mapping[str, str | Path],
) -> dict[str, Any]:
    raw_ref = str(item.get("ref") or "")
    label = str(item.get("label") or "")
    base = {
        "label": label,
        "ref_kind": _ref_kind(raw_ref),
        "available": False,
    }
    if raw_ref.startswith("private://"):
        resolved = private_artifact_map.get(raw_ref)
        record = {
            **base,
            "private_ref_digest": _digest(raw_ref),
        }
        if resolved is None:
            record["status"] = "needs_private_artifact_map"
            return record
        path = Path(resolved)
        record.update(_path_status(path, include_path_digest=True))
        return record

    if raw_ref.startswith("http://") or raw_ref.startswith("https://"):
        return {**base, "status": "remote_url_unsupported"}

    path = Path(raw_ref)
    if not path.is_absolute():
        path = repo_root / path
    return {
        **base,
        **_path_status(path, include_path_digest=path.is_absolute()),
        "safe_path": _safe_path(raw_ref),
    }


def _path_status(path: Path, *, include_path_digest: bool = False) -> dict[str, Any]:
    exists = path.exists()
    record: dict[str, Any] = {
        "available": exists,
        "status": "available" if exists else "missing_artifact_path",
        "artifact_kind": _artifact_kind(path) if exists else "",
        "basename": path.name,
    }
    if include_path_digest:
        record["path_digest"] = _digest(str(path.resolve()))
    return record


def _artifact_status(
    *,
    source_image_ref: str,
    artifact_records: Sequence[Mapping[str, Any]],
) -> str:
    if source_image_ref:
        return "source_image_present"
    if not artifact_records:
        return "missing_source_artifact"

    statuses = {str(record.get("status") or "") for record in artifact_records}
    if statuses == {"available"}:
        return "available"
    if "needs_private_artifact_map" in statuses:
        return "needs_private_artifact_map"
    if "missing_artifact_path" in statuses:
        return "missing_artifact_path"
    if "remote_url_unsupported" in statuses:
        return "remote_url_unsupported"
    return "manual_review"


def _summary(records: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    status_counts = Counter(str(record.get("artifact_status") or "") for record in records)
    context_available = sum(
        1 for record in records if bool(record.get("source_context_available"))
    )
    return {
        "example_count": len(records),
        "source_image_present_count": status_counts["source_image_present"],
        "available_source_artifact_count": status_counts["available"],
        "needs_private_artifact_map_count": status_counts["needs_private_artifact_map"],
        "missing_artifact_path_count": status_counts["missing_artifact_path"],
        "missing_source_artifact_count": status_counts["missing_source_artifact"],
        "source_context_available_count": context_available,
    }


def _recommended_next_actions(summary: Mapping[str, int]) -> list[str]:
    actions: list[str] = []
    if int(summary.get("needs_private_artifact_map_count") or 0) > 0:
        actions.append("provide_private_source_artifact_map_for_hint_only_cases")
    if int(summary.get("missing_artifact_path_count") or 0) > 0:
        actions.append("fix_or_remove_missing_source_artifact_paths")
    if int(summary.get("missing_source_artifact_count") or 0) > 0:
        actions.append("re_intake_cases_with_source_artifact_refs")
    if not actions:
        actions.append("ready_for_source_context_dependent_training")
    return actions


def _next_action_for_status(artifact_status: str) -> str:
    return {
        "available": "ready_for_source_context_dependent_training",
        "source_image_present": "handled_by_source_image_coverage",
        "needs_private_artifact_map": "provide_private_source_artifact_map",
        "missing_artifact_path": "fix_or_remove_source_artifact_path",
        "missing_source_artifact": "re_intake_with_source_artifact",
        "remote_url_unsupported": "download_or_cache_source_artifact",
    }.get(artifact_status, "manual_review")


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


def _ref_kind(ref: str) -> str:
    if ref.startswith("private://"):
        return "private_uri"
    if ref.startswith("http://") or ref.startswith("https://"):
        return "remote_url"
    if Path(ref).is_absolute():
        return "absolute_path"
    return "repo_relative"


def _artifact_kind(path: Path) -> str:
    if path.is_dir():
        return "directory"
    if path.is_file():
        return "file"
    return ""


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
