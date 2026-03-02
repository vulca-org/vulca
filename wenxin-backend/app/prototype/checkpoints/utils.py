"""Shared checkpoint utilities — atomic writes and task ID sanitisation."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

_SAFE_TASK_ID_RE = re.compile(r"[^A-Za-z0-9._-]+")


def atomic_write(path: Path, content: str) -> None:
    """Write *content* atomically via tempfile + rename.

    Guarantees that *path* is never left in a half-written state, even
    on crash or power loss (assuming the filesystem honours ``fsync``).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def safe_task_id(task_id: str) -> str:
    """Convert *task_id* into a filesystem-safe directory/file name."""
    cleaned = _SAFE_TASK_ID_RE.sub("_", task_id).strip("._")
    return cleaned or "task"
