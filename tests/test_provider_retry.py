"""Unit tests for vulca.providers.retry.with_retry."""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(coro):
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestWithRetry:
    def test_with_retry_succeeds_on_third_attempt(self):
        """Operation fails twice then succeeds — returns success, call_count == 3."""
        from vulca.providers.retry import with_retry

        call_count = 0

        async def flaky_op():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("temporary failure")
            return "success"

        result = run(with_retry(flaky_op, max_retries=3, base_delay_ms=10))
        assert result == "success"
        assert call_count == 3

    def test_with_retry_raises_after_max_retries(self):
        """Always-failing operation raises after max_retries+1 total attempts."""
        from vulca.providers.retry import with_retry

        call_count = 0

        async def always_fail():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("always down")

        with pytest.raises(RuntimeError, match="always down"):
            run(with_retry(always_fail, max_retries=3, base_delay_ms=10))

        # 1 original attempt + 3 retries = 4 total
        assert call_count == 4

    def test_with_retry_does_not_retry_non_retryable(self):
        """ValueError that fails retryable_check raises immediately, call_count == 1."""
        from vulca.providers.retry import with_retry

        call_count = 0

        async def bad_op():
            nonlocal call_count
            call_count += 1
            raise ValueError("auth error")

        # Only ConnectionError is retryable; ValueError should not be retried
        def check(exc: Exception) -> bool:
            return isinstance(exc, ConnectionError)

        with pytest.raises(ValueError, match="auth error"):
            run(with_retry(bad_op, max_retries=3, base_delay_ms=10, retryable_check=check))

        assert call_count == 1

    def test_with_retry_no_check_retries_everything(self):
        """When retryable_check=None, all exceptions are retried up to max_retries."""
        from vulca.providers.retry import with_retry

        call_count = 0

        async def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("any error")

        with pytest.raises(ValueError):
            run(with_retry(always_fail, max_retries=2, base_delay_ms=10, retryable_check=None))

        # retryable_check=None → retry all; 1 + 2 = 3 total attempts
        assert call_count == 3
