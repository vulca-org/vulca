"""Tests for DecideNode evolution circuit breaker."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from vulca.pipeline.nodes.decide import _reset_circuit_breaker, _safe_load_evolved


class TestCircuitBreakerTripsAfterThreeFailures:
    def test_circuit_breaker_trips_after_three_failures(self):
        _reset_circuit_breaker()

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
        _reset_circuit_breaker()

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
