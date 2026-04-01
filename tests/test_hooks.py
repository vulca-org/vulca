"""Tests for the event-driven hook system (vulca.hooks)."""

from __future__ import annotations

import pytest
import vulca.hooks as hooks


@pytest.fixture(autouse=True)
def clear_handlers():
    """Ensure a clean handler state for every test."""
    hooks.clear()
    yield
    hooks.clear()


# ── Registration ─────────────────────────────────────────────────────

class TestRegistration:
    def test_on_registers_handler(self):
        calls = []
        hooks.on(hooks.PIPELINE_START, lambda p: calls.append(p))
        assert len(hooks._handlers[hooks.PIPELINE_START]) == 1

    def test_off_removes_handler(self):
        def my_handler(p):
            pass

        hooks.on(hooks.PIPELINE_START, my_handler)
        assert len(hooks._handlers[hooks.PIPELINE_START]) == 1

        hooks.off(hooks.PIPELINE_START, my_handler)
        assert len(hooks._handlers[hooks.PIPELINE_START]) == 0

    def test_off_unknown_handler_is_noop(self):
        """off() should not raise if handler was never registered."""
        def phantom(p):
            pass

        hooks.off(hooks.PIPELINE_START, phantom)  # must not raise

    def test_on_returns_handler_for_decorator_use(self):
        """on() used as decorator returns the original function unchanged."""

        @hooks.on(hooks.NODE_START)
        def my_fn(payload):
            return payload

        assert callable(my_fn)
        # The decorated function should be callable normally
        assert my_fn({"x": 1}) == {"x": 1}
        # And it should be registered
        assert my_fn in hooks._handlers[hooks.NODE_START]

    def test_on_direct_call_returns_handler(self):
        """on(event, fn) returns fn so it can be stored for later off()."""
        def handler(p):
            pass

        returned = hooks.on(hooks.PIPELINE_COMPLETE, handler)
        assert returned is handler

    def test_clear_removes_all(self):
        hooks.on(hooks.PIPELINE_START, lambda p: None)
        hooks.on(hooks.NODE_START, lambda p: None)
        hooks.on(hooks.EVALUATE_SCORED, lambda p: None)

        hooks.clear()

        assert len(hooks._handlers[hooks.PIPELINE_START]) == 0
        assert len(hooks._handlers[hooks.NODE_START]) == 0
        assert len(hooks._handlers[hooks.EVALUATE_SCORED]) == 0


# ── Emit behaviour ───────────────────────────────────────────────────

class TestEmit:
    @pytest.mark.asyncio
    async def test_emit_calls_sync_handler(self):
        received = []

        def handler(payload):
            received.append(payload)

        hooks.on(hooks.PIPELINE_START, handler)
        await hooks.emit(hooks.PIPELINE_START, {"session_id": "abc"})

        assert len(received) == 1
        assert received[0]["session_id"] == "abc"

    @pytest.mark.asyncio
    async def test_emit_calls_async_handler(self):
        received = []

        async def async_handler(payload):
            received.append(payload["event"])

        hooks.on(hooks.NODE_COMPLETE, async_handler)
        await hooks.emit(hooks.NODE_COMPLETE, {"event": "done"})

        assert received == ["done"]

    @pytest.mark.asyncio
    async def test_emit_error_is_non_fatal(self):
        """A bad handler must not prevent subsequent good handlers from running."""
        good_results = []

        def bad_handler(payload):
            raise RuntimeError("boom")

        def good_handler(payload):
            good_results.append(payload)

        hooks.on(hooks.PIPELINE_ERROR, bad_handler)
        hooks.on(hooks.PIPELINE_ERROR, good_handler)

        # Should not raise despite bad_handler
        await hooks.emit(hooks.PIPELINE_ERROR, {"error": "test"})

        assert len(good_results) == 1
        assert good_results[0]["error"] == "test"

    @pytest.mark.asyncio
    async def test_emit_no_handlers_is_noop(self):
        """emit() on an event with no handlers completes without error."""
        await hooks.emit(hooks.EVOLUTION_TRIGGERED, {"tradition": "xieyi"})

    @pytest.mark.asyncio
    async def test_emit_default_payload_is_empty_dict(self):
        """emit() without explicit payload passes {} to handlers."""
        received = []

        def handler(payload):
            received.append(payload)

        hooks.on(hooks.PIPELINE_START, handler)
        await hooks.emit(hooks.PIPELINE_START)

        assert received == [{}]

    @pytest.mark.asyncio
    async def test_emit_calls_multiple_handlers_in_order(self):
        order = []

        hooks.on(hooks.NODE_START, lambda p: order.append(1))
        hooks.on(hooks.NODE_START, lambda p: order.append(2))
        hooks.on(hooks.NODE_START, lambda p: order.append(3))

        await hooks.emit(hooks.NODE_START, {})

        assert order == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_emit_async_error_is_non_fatal(self):
        """An async handler that raises must not block subsequent handlers."""
        good_results = []

        async def async_bad(payload):
            raise ValueError("async boom")

        async def async_good(payload):
            good_results.append("ok")

        hooks.on(hooks.EVALUATE_SCORED, async_bad)
        hooks.on(hooks.EVALUATE_SCORED, async_good)

        await hooks.emit(hooks.EVALUATE_SCORED, {"scores": {}})

        assert good_results == ["ok"]


# ── Event constants ──────────────────────────────────────────────────

class TestEventConstants:
    def test_all_constants_are_strings(self):
        constants = [
            hooks.PIPELINE_START,
            hooks.PIPELINE_COMPLETE,
            hooks.PIPELINE_ERROR,
            hooks.NODE_START,
            hooks.NODE_COMPLETE,
            hooks.EVALUATE_SCORED,
            hooks.EVOLUTION_TRIGGERED,
        ]
        for c in constants:
            assert isinstance(c, str)
            assert len(c) > 0

    def test_constants_are_unique(self):
        constants = [
            hooks.PIPELINE_START,
            hooks.PIPELINE_COMPLETE,
            hooks.PIPELINE_ERROR,
            hooks.NODE_START,
            hooks.NODE_COMPLETE,
            hooks.EVALUATE_SCORED,
            hooks.EVOLUTION_TRIGGERED,
        ]
        assert len(constants) == len(set(constants))
