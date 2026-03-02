"""Pipeline-level checkpoint — persist and restore per-stage state."""

from __future__ import annotations

import fcntl
import json
import logging
import os
from pathlib import Path

from app.prototype.checkpoints.utils import atomic_write as _atomic_write
from app.prototype.checkpoints.utils import safe_task_id as _safe

logger = logging.getLogger(__name__)

_CHECKPOINT_ROOT = Path(__file__).resolve().parent / "pipeline"


def save_pipeline_stage(task_id: str, stage: str, data: dict) -> str:
    """Save checkpoint for a specific pipeline stage.

    Layout::

        checkpoints/pipeline/{task_id}/stage_{stage}.json

    Returns the path to the saved file.
    """
    task_dir = _CHECKPOINT_ROOT / _safe(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    path = task_dir / f"stage_{stage}.json"
    _atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False))
    return str(path)


def load_pipeline_stage(task_id: str, stage: str) -> dict | None:
    """Load checkpoint for a specific pipeline stage, or None if missing."""
    path = _CHECKPOINT_ROOT / _safe(task_id) / f"stage_{stage}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Corrupted checkpoint %s: %s", path, exc)
        return None


def save_pipeline_output(task_id: str, data: dict) -> str:
    """Save the final pipeline output."""
    task_dir = _CHECKPOINT_ROOT / _safe(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    path = task_dir / "pipeline_output.json"
    _atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False))
    return str(path)


def load_pipeline_output(task_id: str) -> dict | None:
    """Load the final pipeline output, or None."""
    path = _CHECKPOINT_ROOT / _safe(task_id) / "pipeline_output.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Corrupted pipeline output %s: %s", path, exc)
        return None


def update_runs_index(task_id: str, entry: dict) -> None:
    """Update the runs index with a new or updated entry.

    Maintains ``checkpoints/runs_index.json`` as a lightweight metadata
    store mapping task_id to status, decision, cost, latency, etc.
    Uses file locking to prevent read-modify-write races.
    """
    _CHECKPOINT_ROOT.mkdir(parents=True, exist_ok=True)
    index_path = _CHECKPOINT_ROOT / "runs_index.json"
    lock_path = _CHECKPOINT_ROOT / ".runs_index.lock"

    with open(lock_path, "w") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            index: dict = {}
            if index_path.exists():
                try:
                    index = json.loads(index_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    index = {}
            index[task_id] = entry
            _atomic_write(index_path, json.dumps(index, indent=2, ensure_ascii=False))
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def load_runs_index() -> dict:
    """Load the full runs index."""
    index_path = _CHECKPOINT_ROOT / "runs_index.json"
    if not index_path.exists():
        return {}
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


