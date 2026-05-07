"""Recover local-only private asset maps for real user source images."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from PIL import Image, UnidentifiedImageError

from vulca.learning.private_asset_map import write_private_asset_map
from vulca.learning.tiny_dataset import build_tiny_dataset_examples


SCHEMA_VERSION = 1
REPORT_CASE_TYPE = "learning_real_user_private_asset_recovery_report"
DEFAULT_OUTPUT_DIR = Path("build/real_user_asset_map_recovery")
DEFAULT_REPORT_NAME = "real_user_private_asset_recovery_report.json"
DEFAULT_ASSET_MAP_NAME = "real_user_recovered.private.asset_map.json"
DEFAULT_SOURCE_ID = "real_user_cases_local_recovered"


def recover_real_user_private_asset_map(
    *,
    repo_root: str | Path,
    case_source_manifest_path: str | Path,
    search_roots: Sequence[str | Path],
    filename_aliases: Mapping[str, str] | None = None,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    report_path: str | Path | None = None,
    asset_map_path: str | Path | None = None,
    source_id: str = DEFAULT_SOURCE_ID,
) -> dict[str, Any]:
    """Write a local private asset map by matching private source basenames."""
    roots = [Path(root) for root in search_roots]
    if not roots:
        raise ValueError("at least one search root is required")
    aliases = {
        str(source_name): str(local_name)
        for source_name, local_name in (filename_aliases or {}).items()
        if str(source_name) and str(local_name)
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resolved_report_path = (
        Path(report_path) if report_path else output / DEFAULT_REPORT_NAME
    )
    resolved_asset_map_path = (
        Path(asset_map_path) if asset_map_path else output / DEFAULT_ASSET_MAP_NAME
    )

    private_source_refs = _private_source_refs(
        repo_root=repo_root,
        case_source_manifest_path=case_source_manifest_path,
    )
    recovered: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    entries: dict[str, str] = {}

    for item in private_source_refs:
        basename = str(item["basename"])
        candidates = _find_valid_image_candidates(
            _candidate_basenames(basename, aliases),
            roots,
        )
        if len(candidates) == 1:
            candidate, matched_basename = candidates[0]
            private_ref = str(item["private_ref"])
            entries[private_ref] = str(candidate)
            recovered.append(
                _safe_record(
                    item,
                    candidate_count=1,
                    matched_basename=matched_basename,
                    selected_path_digest=_digest_path(candidate),
                    image_probe=_image_probe(candidate),
                )
            )
            continue
        if candidates:
            ambiguous.append(
                _safe_record(
                    item,
                    candidate_count=len(candidates),
                    candidate_path_digests=[
                        _digest_path(candidate) for candidate, _ in candidates
                    ],
                )
            )
            continue
        unresolved.append(_safe_record(item, candidate_count=0))

    write_private_asset_map(
        resolved_asset_map_path,
        source_id=source_id,
        entries=entries,
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "case_type": REPORT_CASE_TYPE,
        "status": "ready_to_rerun_coverage" if entries else "needs_user_assets",
        "inputs": {
            "case_source_manifest_path": _safe_path(case_source_manifest_path),
            "search_root_count": len(roots),
            "filename_alias_count": len(aliases),
        },
        "artifacts": {
            "report_path": _artifact_name(resolved_report_path, output),
            "private_asset_map_path": _artifact_name(resolved_asset_map_path, output),
        },
        "summary": {
            "private_source_ref_count": len(private_source_refs),
            "recovered_count": len(recovered),
            "ambiguous_count": len(ambiguous),
            "unresolved_count": len(unresolved),
        },
        "recovered": recovered,
        "ambiguous": ambiguous,
        "unresolved": unresolved,
        "safe_handling": {
            "private_asset_map_contains_local_paths": True,
            "do_not_commit_private_asset_map": True,
            "report_omits_local_paths": True,
        },
    }
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def _private_source_refs(
    *,
    repo_root: str | Path,
    case_source_manifest_path: str | Path,
) -> list[dict[str, Any]]:
    examples = build_tiny_dataset_examples(
        repo_root=repo_root,
        case_source_manifest_path=case_source_manifest_path,
        include_local_seeds=False,
    )
    items: list[dict[str, Any]] = []
    for example in examples:
        case_record = _mapping(_mapping(example.get("input")).get("case_record"))
        private_ref = _source_image_ref(case_record)
        if not private_ref.startswith("private://"):
            continue
        basename = private_ref.rstrip("/").rsplit("/", 1)[-1]
        if not basename:
            continue
        source_case = _mapping(example.get("source_case"))
        source = _mapping(example.get("source"))
        items.append(
            {
                "case_id": str(source_case.get("case_id") or ""),
                "case_type": str(source_case.get("case_type") or ""),
                "basename": basename,
                "private_ref": private_ref,
                "private_ref_digest": _digest_text(private_ref),
                "source": {
                    "source_id": str(source.get("source_id") or ""),
                    "kind": str(source.get("kind") or ""),
                    "privacy_scope": str(source.get("privacy_scope") or ""),
                    "record_index": int(source.get("index") or 0),
                },
            }
        )
    return items


def _candidate_basenames(
    basename: str,
    filename_aliases: Mapping[str, str],
) -> tuple[str, ...]:
    alias = filename_aliases.get(basename)
    if alias and alias != basename:
        return (basename, alias)
    return (basename,)


def _find_valid_image_candidates(
    basenames: Sequence[str],
    roots: Sequence[Path],
) -> list[tuple[Path, str]]:
    candidates: dict[str, tuple[Path, str]] = {}
    for root in roots:
        if not root.exists():
            continue
        for basename in basenames:
            for path in root.rglob(basename):
                if not path.is_file() or ".git" in path.parts:
                    continue
                if _image_probe(path).get("valid_image") is not True:
                    continue
                resolved = path.resolve()
                candidates[str(resolved)] = (resolved, basename)
    return [candidates[key] for key in sorted(candidates)]


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


def _safe_record(
    item: Mapping[str, Any],
    *,
    candidate_count: int,
    matched_basename: str = "",
    selected_path_digest: str = "",
    candidate_path_digests: Sequence[str] = (),
    image_probe: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    record = {
        "case_id": str(item.get("case_id") or ""),
        "case_type": str(item.get("case_type") or ""),
        "source": dict(_mapping(item.get("source"))),
        "basename": str(item.get("basename") or ""),
        "private_ref_digest": str(item.get("private_ref_digest") or ""),
        "candidate_count": candidate_count,
    }
    if selected_path_digest:
        record["selected_path_digest"] = selected_path_digest
    if matched_basename:
        record["matched_basename"] = matched_basename
    if candidate_path_digests:
        record["candidate_path_digests"] = list(candidate_path_digests)
    if image_probe:
        record["image_probe"] = dict(image_probe)
    return record


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


def _digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _digest_path(path: Path) -> str:
    return _digest_text(str(path.resolve()))


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}
