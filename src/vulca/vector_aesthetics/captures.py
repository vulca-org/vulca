from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import LOCAL_CAPTURE_TYPES, resolve_local_capture_path, validate_case_folder


def _metadata_path(case_dir: Path) -> Path:
    return case_dir / "metadata.json"


def _load(case_dir: Path) -> dict[str, Any]:
    return json.loads(_metadata_path(case_dir).read_text(encoding="utf-8"))


def _write(case_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    metadata_path = _metadata_path(case_dir)
    before = metadata_path.read_text(encoding="utf-8")
    try:
        metadata_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        validate_case_folder(case_dir)
    except Exception:
        metadata_path.write_text(before, encoding="utf-8")
        raise
    return payload


def _assert_local_file(case_dir: Path, capture: dict[str, str]) -> None:
    if capture["rights_status"] != "local_capture":
        return
    if capture["evidence_type"] not in LOCAL_CAPTURE_TYPES:
        return
    resolve_local_capture_path(case_dir, capture["path_or_url"])


def add_capture(case_dir: Path, capture: dict[str, str]) -> dict[str, Any]:
    _assert_local_file(case_dir, capture)
    payload = _load(case_dir)
    captures = [item for item in payload["captures"] if item["id"] != capture["id"]]
    captures.append(capture)
    payload["captures"] = sorted(captures, key=lambda item: item["id"])
    return _write(case_dir, payload)


def record_capture_failure(
    case_dir: Path,
    *,
    evidence_type: str,
    notes: str,
    source_url: str,
) -> dict[str, Any]:
    capture = {
        "id": f"{evidence_type}-capture-failure",
        "evidence_type": evidence_type,
        "path_or_url": source_url,
        "capture_method": "manual_browser",
        "viewport": "none",
        "interaction": "capture_failed",
        "captured_at": "2026-06-29",
        "source_url": source_url,
        "confidence": "medium",
        "rights_status": "source_link_only",
        "notes": notes,
    }
    return add_capture(case_dir, capture)
