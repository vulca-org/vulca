"""Tests for VULCA types."""

from vulca.types import EvalResult


class TestEvalResultObservations:
    def test_observations_default_empty(self):
        r = EvalResult(
            score=0.8, tradition="test", dimensions={}, rationales={},
            summary="", risk_level="low", risk_flags=[], recommendations=[],
        )
        assert r.observations == {}

    def test_reference_techniques_default_empty(self):
        r = EvalResult(
            score=0.8, tradition="test", dimensions={}, rationales={},
            summary="", risk_level="low", risk_flags=[], recommendations=[],
        )
        assert r.reference_techniques == {}

    def test_observations_set(self):
        r = EvalResult(
            score=0.8, tradition="test", dimensions={}, rationales={},
            summary="", risk_level="low", risk_flags=[], recommendations=[],
            observations={"L1": "diagonal flow, negative space"},
        )
        assert r.observations["L1"] == "diagonal flow, negative space"
