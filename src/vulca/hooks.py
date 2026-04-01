"""Event-driven hook system for VULCA pipeline observability.

Usage::

    import vulca.hooks as hooks

    # Register handler (direct call)
    def my_handler(payload):
        print(payload)
    hooks.on(hooks.PIPELINE_START, my_handler)

    # Register handler (decorator)
    @hooks.on(hooks.NODE_COMPLETE)
    async def on_node_done(payload):
        await log_to_db(payload)

    # Remove handler
    hooks.off(hooks.PIPELINE_START, my_handler)

    # Clear all handlers for all events
    hooks.clear()
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger("vulca.hooks")

# ── Event constants ──────────────────────────────────────────────────

PIPELINE_START = "pipeline_start"
PIPELINE_COMPLETE = "pipeline_complete"
PIPELINE_ERROR = "pipeline_error"
NODE_START = "node_start"
NODE_COMPLETE = "node_complete"
EVALUATE_SCORED = "evaluate_scored"
EVOLUTION_TRIGGERED = "evolution_triggered"

# ── Internal state ───────────────────────────────────────────────────

_handlers: dict[str, list[Callable]] = defaultdict(list)


# ── Public API ───────────────────────────────────────────────────────

def on(event: str, handler: Callable | None = None):
    """Register a handler for an event.

    Supports both direct call and decorator patterns::

        hooks.on("pipeline_start", my_fn)

        @hooks.on("pipeline_start")
        def my_fn(payload): ...
    """
    if handler is not None:
        # Direct call: hooks.on(event, fn)
        _handlers[event].append(handler)
        return handler

    # Decorator: @hooks.on(event)
    def decorator(fn: Callable) -> Callable:
        _handlers[event].append(fn)
        return fn

    return decorator


def off(event: str, handler: Callable) -> None:
    """Remove a previously registered handler for an event."""
    try:
        _handlers[event].remove(handler)
    except ValueError:
        pass


async def emit(event: str, payload: dict[str, Any] | None = None) -> None:
    """Emit an event, invoking all registered handlers.

    Handlers are called in registration order. Both sync and async handlers
    are supported. Handler errors are non-fatal — they are logged and
    execution continues so that one bad handler cannot block others.
    """
    if payload is None:
        payload = {}

    for handler in list(_handlers[event]):
        try:
            result = handler(payload)
            if asyncio.iscoroutine(result):
                await result
        except Exception as exc:
            logger.warning(
                "Hook handler %r for event %r raised: %s",
                getattr(handler, "__name__", repr(handler)),
                event,
                exc,
            )


def clear() -> None:
    """Remove all registered handlers for all events."""
    _handlers.clear()
