#!/usr/bin/env python3
"""Synchronize Vulca skills into platform plugin package locations."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / ".agents" / "skills"
TARGETS = [
    ROOT / ".claude" / "skills",
    ROOT / "skills",
    ROOT / "plugins" / "vulca" / "skills",
]


def _sync_tree(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise SystemExit(f"missing source skills directory: {source}")
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)


def main() -> None:
    for target in TARGETS:
        _sync_tree(SOURCE, target)
        print(f"synced {SOURCE.relative_to(ROOT)} -> {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
