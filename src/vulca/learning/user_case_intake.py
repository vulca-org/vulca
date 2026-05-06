"""Provider-free intake for reviewed private user case logs."""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping

from vulca.learning.case_review import load_cases, write_cases
from vulca.learning.private_asset_map import write_private_asset_map as write_asset_map


USER_CASE_INTAKE_SCHEMA_VERSION = 1
CASE_SOURCE_MANIFEST_CASE_TYPE = "learning_tiny_case_source_manifest"
USER_CASE_LOG_KIND = "user_case_log"
PRIVATE_PRIVACY_SCOPE = "private"
REVIEWED_CURATION_STATUS = "reviewed"
SUPPORTED_USER_CASE_TYPES: frozenset[str] = frozenset(
    {"redraw_case", "decompose_case", "layer_generate_case"}
)

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
_SECRET_RE = re.compile(r"\b(?:sk|api|key|token)[-_][A-Za-z0-9]{12,}\b")
_POSIX_LOCAL_PATH_RE = re.compile(
    r"(?<![\w:])/(?:Users|home|private|var|tmp|Volumes)/[^\s,;\"')\]]+"
)
_WINDOWS_LOCAL_PATH_RE = re.compile(
    r"\b[A-Za-z]:\\(?:Users|Documents and Settings)\\[^\s,;\"')\]]+"
)
_SENSITIVE_KEY_RE = re.compile(
    r"(?:api[_-]?key|auth(?:orization)?|credential|password|secret|token)",
    re.IGNORECASE,
)
_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class UserCaseIntakeResult:
    source_id: str
    output_path: str
    manifest_path: str
    asset_map_path: str
    record_count: int


def write_user_case_intake(
    *,
    input_path: str | Path,
    source_id: str,
    output_dir: str | Path | None = None,
    output_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    asset_map_path: str | Path | None = None,
    write_private_asset_map: bool = False,
) -> UserCaseIntakeResult:
    """Normalize reviewed user case JSONL into a private user_case_log source."""
    resolved_source_id = str(source_id).strip()
    if not resolved_source_id:
        raise ValueError("source_id is required")

    input_records = load_cases(input_path)
    base_dir = Path(output_dir) if output_dir is not None else Path(input_path).parent
    path_token = _path_token(resolved_source_id)
    output = (
        Path(output_path)
        if output_path is not None
        else base_dir / f"{path_token}.private.user_cases.jsonl"
    )
    manifest = (
        Path(manifest_path)
        if manifest_path is not None
        else base_dir / f"{path_token}.case_source_manifest.json"
    )
    asset_map = (
        Path(asset_map_path)
        if asset_map_path is not None
        else base_dir / f"{path_token}.private.asset_map.json"
    )
    should_write_asset_map = bool(write_private_asset_map or asset_map_path)

    private_asset_entries: dict[str, str] = {}
    normalized_records = [
        normalize_user_case_record(
            record,
            source_id=resolved_source_id,
            record_index=index,
            private_asset_entries=private_asset_entries,
        )
        for index, record in enumerate(input_records)
    ]

    write_cases(output, normalized_records)
    _write_case_source_manifest(
        manifest_path=manifest,
        output_path=output,
        source_id=resolved_source_id,
    )
    if should_write_asset_map:
        write_asset_map(
            asset_map,
            source_id=resolved_source_id,
            entries=private_asset_entries,
        )
    return UserCaseIntakeResult(
        source_id=resolved_source_id,
        output_path=str(output),
        manifest_path=str(manifest),
        asset_map_path=str(asset_map) if should_write_asset_map else "",
        record_count=len(normalized_records),
    )


def normalize_user_case_record(
    record: Mapping[str, Any],
    *,
    source_id: str,
    record_index: int,
    private_asset_entries: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Return a sanitized reviewed case record with private intake metadata."""
    _validate_reviewed_case(record, record_index=record_index)
    normalized = _sanitize_value(
        dict(record),
        key="",
        private_asset_entries=private_asset_entries,
    )
    if not isinstance(normalized, dict):
        raise ValueError(f"record {record_index}: expected JSON object")
    normalized["user_case_intake"] = {
        "schema_version": USER_CASE_INTAKE_SCHEMA_VERSION,
        "source_id": source_id,
        "privacy_scope": PRIVATE_PRIVACY_SCOPE,
        "curation_status": REVIEWED_CURATION_STATUS,
        "record_index": record_index,
    }
    return normalized


def _validate_reviewed_case(record: Mapping[str, Any], *, record_index: int) -> None:
    case_type = str(record.get("case_type") or "")
    if case_type not in SUPPORTED_USER_CASE_TYPES:
        raise ValueError(
            f"record {record_index}: unsupported case_type {case_type!r}; "
            f"expected one of {sorted(SUPPORTED_USER_CASE_TYPES)}"
        )
    if not str(record.get("case_id") or ""):
        raise ValueError(f"record {record_index}: case_id is required")

    review = record.get("review")
    if not isinstance(review, Mapping):
        raise ValueError(f"record {record_index}: review object is required")
    if not str(review.get("reviewed_at") or ""):
        raise ValueError(f"record {record_index}: review.reviewed_at is required")
    human_accept = review.get("human_accept")
    failure_type = str(review.get("failure_type") or "")
    preferred_action = str(review.get("preferred_action") or "")
    if not isinstance(human_accept, bool) and not failure_type and not preferred_action:
        raise ValueError(f"record {record_index}: at least one review label is required")


def _write_case_source_manifest(
    *,
    manifest_path: Path,
    output_path: Path,
    source_id: str,
) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": USER_CASE_INTAKE_SCHEMA_VERSION,
        "case_type": CASE_SOURCE_MANIFEST_CASE_TYPE,
        "sources": [
            {
                "source_id": source_id,
                "kind": USER_CASE_LOG_KIND,
                "path": _manifest_relative_path(output_path, manifest_path.parent),
                "privacy_scope": PRIVATE_PRIVACY_SCOPE,
                "curation_status": REVIEWED_CURATION_STATUS,
            }
        ],
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def _sanitize_value(
    value: Any,
    *,
    key: str,
    private_asset_entries: dict[str, str] | None = None,
) -> Any:
    if _SENSITIVE_KEY_RE.search(key):
        return "<redacted>"
    if isinstance(value, dict):
        return {
            str(child_key): _sanitize_value(
                child_value,
                key=str(child_key),
                private_asset_entries=private_asset_entries,
            )
            for child_key, child_value in value.items()
        }
    if isinstance(value, list):
        return [
            _sanitize_value(
                child,
                key=key,
                private_asset_entries=private_asset_entries,
            )
            for child in value
        ]
    if isinstance(value, str):
        return _sanitize_text(value, private_asset_entries=private_asset_entries)
    return value


def _sanitize_text(
    value: str,
    *,
    private_asset_entries: dict[str, str] | None = None,
) -> str:
    sanitized = _POSIX_LOCAL_PATH_RE.sub(
        lambda match: _canonical_posix_path(
            match,
            private_asset_entries=private_asset_entries,
        ),
        value,
    )
    sanitized = _WINDOWS_LOCAL_PATH_RE.sub(
        lambda match: _canonical_windows_path(
            match,
            private_asset_entries=private_asset_entries,
        ),
        sanitized,
    )
    sanitized = _EMAIL_RE.sub("<email:redacted>", sanitized)
    sanitized = _PHONE_RE.sub("<phone:redacted>", sanitized)
    sanitized = _SECRET_RE.sub("<secret:redacted>", sanitized)
    return sanitized


def _canonical_posix_path(
    match: re.Match[str],
    *,
    private_asset_entries: dict[str, str] | None = None,
) -> str:
    raw, trailing = _strip_trailing_punctuation(match.group(0))
    token = _canonical_path_token(raw, Path(raw).name)
    if private_asset_entries is not None:
        private_asset_entries[token] = raw
    return f"{token}{trailing}"


def _canonical_windows_path(
    match: re.Match[str],
    *,
    private_asset_entries: dict[str, str] | None = None,
) -> str:
    raw, trailing = _strip_trailing_punctuation(match.group(0))
    token = _canonical_path_token(raw, PureWindowsPath(raw).name)
    if private_asset_entries is not None:
        private_asset_entries[token] = raw
    return f"{token}{trailing}"


def _canonical_path_token(raw_path: str, name: str) -> str:
    digest = hashlib.sha256(raw_path.encode("utf-8")).hexdigest()[:12]
    safe_name = _SAFE_FILENAME_RE.sub("_", name or "path").strip("._") or "path"
    return f"private://local_path/{digest}/{safe_name[:80]}"


def _strip_trailing_punctuation(value: str) -> tuple[str, str]:
    stripped = value.rstrip(".:")
    return stripped, value[len(stripped):]


def _manifest_relative_path(output_path: Path, manifest_dir: Path) -> str:
    rel = os.path.relpath(output_path, manifest_dir)
    return Path(rel).as_posix()


def _path_token(source_id: str) -> str:
    token = _SAFE_FILENAME_RE.sub("_", source_id).strip("._")
    if token:
        return token
    digest = hashlib.sha256(source_id.encode("utf-8")).hexdigest()[:12]
    return f"user_case_source_{digest}"
