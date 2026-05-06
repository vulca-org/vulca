"""Private local asset map helpers for reviewed user cases.

The map intentionally lives outside training records. It may contain absolute
local paths, so callers should keep it local-only and never promote it into
shared benchmark artifacts.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Sequence


PRIVATE_ASSET_MAP_SCHEMA_VERSION = 1
PRIVATE_ASSET_MAP_CASE_TYPE = "learning_private_asset_map"
PRIVATE_LOCAL_PRIVACY_SCOPE = "private_local"


def write_private_asset_map(
    path: str | Path,
    *,
    source_id: str,
    entries: Mapping[str, str],
) -> None:
    """Write a deterministic private-ref to local-path sidecar map."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": PRIVATE_ASSET_MAP_SCHEMA_VERSION,
        "case_type": PRIVATE_ASSET_MAP_CASE_TYPE,
        "source_id": str(source_id),
        "privacy_scope": PRIVATE_LOCAL_PRIVACY_SCOPE,
        "entries": [
            {
                "private_ref": str(private_ref),
                "local_path": str(local_path),
            }
            for private_ref, local_path in sorted(entries.items())
        ],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def load_private_asset_maps(
    paths: Sequence[str | Path] | None,
) -> dict[str, Path]:
    """Load one or more private asset maps into an in-memory resolver."""
    resolver: dict[str, Path] = {}
    for raw_path in paths or ():
        path = Path(raw_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError("private asset map must be a JSON object")
        if payload.get("case_type") != PRIVATE_ASSET_MAP_CASE_TYPE:
            raise ValueError(
                f"private asset map case_type must be {PRIVATE_ASSET_MAP_CASE_TYPE!r}"
            )
        entries = payload.get("entries")
        if not isinstance(entries, list):
            raise ValueError("private asset map entries must be a list")
        for index, entry in enumerate(entries):
            if not isinstance(entry, Mapping):
                raise ValueError(f"private asset map entry {index}: expected object")
            private_ref = str(entry.get("private_ref") or "")
            local_path = str(entry.get("local_path") or "")
            if not private_ref.startswith("private://"):
                raise ValueError(
                    f"private asset map entry {index}: private_ref is required"
                )
            if not local_path:
                raise ValueError(
                    f"private asset map entry {index}: local_path is required"
                )
            resolver[private_ref] = Path(local_path)
    return resolver


def resolve_private_asset_ref(
    ref: str,
    *,
    private_asset_map: Mapping[str, str | Path] | None,
) -> Path | None:
    """Return the mapped local path for a private ref, if one exists."""
    if not ref.startswith("private://"):
        return None
    if not private_asset_map:
        return None
    mapped = private_asset_map.get(ref)
    if mapped is None:
        return None
    return Path(mapped)
