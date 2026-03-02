"""Draft checkpoint persistence — save / load run metadata + images."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.prototype.agents.draft_types import DraftOutput
from app.prototype.checkpoints.utils import atomic_write as _atomic_write
from app.prototype.checkpoints.utils import safe_task_id as _safe_task_dirname

logger = logging.getLogger(__name__)

_CHECKPOINT_ROOT = Path(__file__).resolve().parent / "draft"


def save_draft_checkpoint(output: DraftOutput) -> str:
    """Persist a DraftOutput as ``run.json`` alongside its images.

    Directory layout::

        checkpoints/draft/{task_id}/
            run.json
            draft-{task_id}-0.{png|jpg|webp}
            draft-{task_id}-1.{png|jpg|webp}
            ...

    Returns the path to ``run.json``.
    """
    task_dir = _CHECKPOINT_ROOT / _safe_task_dirname(output.task_id)
    task_dir.mkdir(parents=True, exist_ok=True)

    run_path = task_dir / "run.json"
    run_data = {
        "task_id": output.task_id,
        "created_at": output.created_at,
        "config": _extract_config(output),
        "candidates": [c.to_dict() for c in output.candidates],
        "latency_ms": output.latency_ms,
        "success": output.success,
        "error": output.error,
    }
    _atomic_write(run_path, json.dumps(run_data, indent=2, ensure_ascii=False))
    return str(run_path)


def load_draft_checkpoint(task_id: str) -> dict | None:
    """Load an existing checkpoint for *task_id*, or return ``None``."""
    run_path = _CHECKPOINT_ROOT / _safe_task_dirname(task_id) / "run.json"
    if not run_path.exists():
        return None
    try:
        return json.loads(run_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Corrupted draft checkpoint %s: %s", run_path, exc)
        return None


def _extract_config(output: DraftOutput) -> dict:
    """Best-effort config extraction from the first candidate."""
    if not output.candidates:
        return {}
    c = output.candidates[0]
    return {
        "width": c.width,
        "height": c.height,
        "steps": c.steps,
        "sampler": c.sampler,
        "model_ref": c.model_ref,
    }


