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
        backend.append(output.to_dict())
    except Exception as exc:
        logger.debug("JSONL session storage failed (non-fatal): %s", exc)

    # 2. Throttled evolution
    await _maybe_evolve(output.session_id)


async def _maybe_evolve(session_id: str = "") -> None:
    """Trigger ContextEvolver at most once per _EVOLUTION_INTERVAL seconds.

    Shared by both headless (default_on_complete) and Web App routes.
    Import of ContextEvolver is deferred -- standalone usage without
    the prototype backend simply skips evolution.
    """
    global _last_evolution_time
    now = time.monotonic()
    if now - _last_evolution_time < _EVOLUTION_INTERVAL:
        return
    _last_evolution_time = now
    try:
        from app.prototype.digestion.context_evolver import ContextEvolver

        ContextEvolver().evolve()
        logger.debug("Evolution triggered (session=%s)", session_id)
    except ImportError:
        pass  # Standalone mode -- no prototype backend
    except Exception as exc:
        logger.debug("Evolution failed (non-fatal): %s", exc)
