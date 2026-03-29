"""Pipeline completion hooks -- default session storage + throttled evolution."""

from __future__ import annotations

import logging
import time

from vulca.pipeline.types import PipelineOutput

logger = logging.getLogger("vulca")

_last_evolution_time = 0.0
_EVOLUTION_INTERVAL = 300  # 5 minutes


async def default_on_complete(output: PipelineOutput) -> None:
    """Store session to JSONL and trigger throttled evolution.

    This is the default hook for SDK/CLI/MCP headless usage.
    Web App routes use their own on_complete with richer SessionDigest.
    """
    # 1. Persist to local JSONL
    try:
        from vulca.storage.jsonl import JsonlSessionBackend

        backend = JsonlSessionBackend()
        data = output.to_dict()
        # Pipeline-completed sessions count as accepted for evolution
        if "user_feedback" not in data:
            data["user_feedback"] = "accepted"
        backend.append(data)
    except Exception as exc:
        logger.debug("JSONL session storage failed (non-fatal): %s", exc)

    # 2. Throttled evolution
    await _maybe_evolve(output.session_id)


async def _maybe_evolve(session_id: str = "") -> None:
    """Trigger evolution at most once per _EVOLUTION_INTERVAL seconds.

    Tries local evolution first (works without backend), then backend
    ContextEvolver if available.  Both failures are non-fatal.
    """
    global _last_evolution_time
    now = time.monotonic()
    if now - _last_evolution_time < _EVOLUTION_INTERVAL:
        return
    _last_evolution_time = now

    # Try local evolution first (works without backend)
    try:
        from vulca.digestion.local_evolver import LocalEvolver

        LocalEvolver().evolve()
        logger.debug("Local evolution triggered (session=%s)", session_id)
    except Exception as exc:
        logger.debug("Local evolution failed (non-fatal): %s", exc)

    # Then try backend evolution if available
    try:
        from app.prototype.digestion.context_evolver import ContextEvolver

        ContextEvolver().evolve()
        logger.debug("Backend evolution triggered (session=%s)", session_id)
    except ImportError:
        pass  # Standalone mode -- no prototype backend
    except Exception as exc:
        logger.debug("Backend evolution failed (non-fatal): %s", exc)
