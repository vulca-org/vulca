"""Critic checkpoint persistence — save / load critique run metadata."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.prototype.agents.critic_types import CritiqueOutput
from app.prototype.checkpoints.utils import atomic_write as _atomic_write
from app.prototype.checkpoints.utils import safe_task_id as _safe_task_dirname

logger = logging.getLogger(__name__)

_CHECKPOINT_ROOT = Path(__file__).resolve().parent / "critique"


def save_critic_checkpoint(output: CritiqueOutput) -> str:
    """Persist a CritiqueOutput as ``run.json``.

    Directory layout::

        checkpoints/critique/{task_id}/
            run.json

    Returns the path to ``run.json``.
    """
    task_dir = _CHECKPOINT_ROOT / _safe_task_dirname(output.task_id)
    task_dir.mkdir(parents=True, exist_ok=True)

    run_path = task_dir / "run.json"
    _atomic_write(run_path, json.dumps(output.to_dict(), indent=2, ensure_ascii=False))
    return str(run_path)


def load_critic_checkpoint(task_id: str) -> dict | None:
    """Load an existing critique checkpoint for *task_id*, or return ``None``."""
    run_path = _CHECKPOINT_ROOT / _safe_task_dirname(task_id) / "run.json"
    if not run_path.exists():
        return None
    try:
        return json.loads(run_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Corrupted critic checkpoint %s: %s", run_path, exc)
        return None


