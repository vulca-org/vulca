"""Tests for DecideNode evolution circuit breaker."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from vulca.pipeline.nodes.decide import _reset_circuit_breaker, _safe_load_evolved


@pytest.fixture(autouse=True)
def clean_circuit_breaker():
    """Reset circuit breaker before and after each test to prevent cross-test pollution."""
    _reset_circuit_breaker()
    yield
    _reset_circuit_breaker()


class TestCircuitBreakerTripsAfterThreeFailures:
    def test_circuit_breaker_trips_after_three_failures(self):
        with patch("vulca.pipeline.nodes.decide.LocalEvolver") as mock_cls:
            mock_cls.return_value.load_evolved.side_effect = RuntimeError("disk error")

            # First three calls fail but still attempt load
            result1 = _safe_load_evolved("chinese_xieyi")
            result2 = _safe_load_evolved("chinese_xieyi")
            result3 = _safe_load_evolved("chinese_xieyi")

            assert result1 is None
            assert result2 is None
            assert result3 is None
            assert mock_cls.return_value.load_evolved.call_count == 3

            # 4th call: circuit is open, load_evolved must NOT be called
            call_count_before = mock_cls.return_value.load_evolved.call_count
            result4 = _safe_load_evolved("chinese_xieyi")
            assert result4 is None
            assert mock_cls.return_value.load_evolved.call_count == call_count_before  # no new call


class TestCircuitBreakerPassesThroughOnSuccess:
    def test_circuit_breaker_passes_through_on_success(self):
        fake_evolved = {
            "session_count": 10,
            "overall_avg": 0.82,
            "strict_count": 7,
            "reference_count": 3,
        }

        with patch("vulca.pipeline.nodes.decide.LocalEvolver") as mock_cls:
            mock_cls.return_value.load_evolved.return_value = fake_evolved

            result = _safe_load_evolved("chinese_xieyi")

        assert result == fake_evolved


class TestCircuitBreakerResetsOnSuccess:
    def test_success_resets_failure_count(self):
        """After failures, a successful load should reset the counter so future
        transient failures don't immediately trip the breaker."""
        fake_evolved = {"session_count": 5, "overall_avg": 0.7}

        with patch("vulca.pipeline.nodes.decide.LocalEvolver") as mock_cls:
            inst = mock_cls.return_value

            # 2 failures (just below the 3-trip threshold)
            inst.load_evolved.side_effect = RuntimeError("transient")
            _safe_load_evolved("chinese_xieyi")
            _safe_load_evolved("chinese_xieyi")
            assert inst.load_evolved.call_count == 2

            # 1 success — should reset the counter
            inst.load_evolved.side_effect = None
            inst.load_evolved.return_value = fake_evolved
            result = _safe_load_evolved("chinese_xieyi")
            assert result == fake_evolved

            # Now 2 more failures should NOT trip the breaker (counter was reset)
            inst.load_evolved.side_effect = RuntimeError("transient again")
            _safe_load_evolved("chinese_xieyi")
            _safe_load_evolved("chinese_xieyi")

            # 6th call: if counter was NOT reset, this would be call #5 after
            # 4 total failures and the circuit would be open.
            # With reset, only 2 failures since last success — should still try.
            inst.load_evolved.reset_mock()
            inst.load_evolved.side_effect = RuntimeError("still failing")
            _safe_load_evolved("chinese_xieyi")
            assert inst.load_evolved.call_count == 1  # Circuit still closed, load was attempted
