"""Reusable async retry wrapper with exponential backoff + jitter."""
from __future__ import annotations

import logging
import random
from typing import Awaitable, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    max_retries: int = 3,
    base_delay_ms: int = 500,
    max_delay_ms: int = 16_000,
    retryable_check: Callable[[Exception], bool] | None = None,
) -> T:
    """Execute *operation* with exponential backoff retry.

    Args:
        operation: Async callable to attempt. Called with no arguments.
        max_retries: Maximum number of *retry* attempts (total calls = max_retries + 1).
        base_delay_ms: Base delay in milliseconds before the first retry.
        max_delay_ms: Cap on the computed delay (before jitter).
        retryable_check: Optional predicate — if provided and returns False for an
            exception, the exception is re-raised immediately without retrying.

    Returns:
        The return value of *operation* on the first successful call.

    Raises:
        The last exception raised by *operation* once all retries are exhausted, or
        immediately if *retryable_check* returned False.
    """
    import asyncio

    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except Exception as exc:
            last_exc = exc

            # Non-retryable exception — raise immediately
            if retryable_check is not None and not retryable_check(exc):
                raise

            # No more retries left
            if attempt >= max_retries:
                raise

            # Exponential backoff: base * 2^attempt, capped at max_delay_ms
            delay_ms = min(base_delay_ms * (2 ** attempt), max_delay_ms)
            # Jitter: up to 25% of computed delay
            jitter_ms = random.random() * 0.25 * delay_ms
            total_delay_s = (delay_ms + jitter_ms) / 1000.0

            logger.warning(
                "Retry attempt %d/%d after %.3fs (reason: %s: %s)",
                attempt + 1,
                max_retries,
                total_delay_s,
                type(exc).__name__,
                exc,
            )

            await asyncio.sleep(total_delay_s)

    # Should be unreachable, but keep type checker happy
    raise RuntimeError("with_retry: unreachable") from last_exc
