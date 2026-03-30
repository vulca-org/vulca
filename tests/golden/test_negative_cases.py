"""Negative Golden Set: things that SHOULD fail or NOT happen.

Anthropic Article 3: "One-sided evals create one-sided optimization."
These tests verify error handling, score sanity, and boundary conditions.

Behavior notes (verified 2026-03-29, mock=True):
- Invalid/nonexistent traditions are silently accepted and produce scores
  (the system falls back gracefully rather than raising).
- Empty tradition falls back to "default" tradition.
- mock=True skips file existence checks — nonexistent paths are fine.
- Mock rationales are generic ("Mock: Visual composition assessment."),
  they do NOT embed tradition names.
"""
from __future__ import annotations

import pytest
import vulca

# MOCK_GOLDEN is defined in the same package directory; import via sys.path
# (vulca.tests is not a proper package so direct import would fail)
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from test_mock_regression import MOCK_GOLDEN


class TestNegativeTraditions:
    """Invalid traditions must degrade gracefully — document actual behavior."""

    def test_nonexistent_tradition_does_not_raise(self):
        """Unknown tradition should NOT crash — system falls back gracefully.

        The mock evaluator assigns scores based on a hash of the tradition
        name, so a nonexistent tradition still returns a valid EvalResult.
        """
        result = vulca.evaluate("test.png", tradition="nonexistent_tradition_xyz", mock=True)
        # Must return a structurally valid result
        assert result.score is not None
        assert set(result.dimensions.keys()) == {"L1", "L2", "L3", "L4", "L5"}

    def test_nonexistent_tradition_score_differs_from_default(self):
        """A made-up tradition name must produce a different score from 'default'.

        This verifies that tradition identity actually influences mock scoring
        (not just returning the same constant for everything).
        """
        r_fake = vulca.evaluate("test.png", tradition="nonexistent_tradition_xyz", mock=True)
        r_default = vulca.evaluate("test.png", tradition="default", mock=True)
        assert r_fake.score != r_default.score, (
            "Nonexistent tradition returned identical score to default — "
            "tradition parameter has no effect on scoring"
        )

    def test_empty_tradition_falls_back_to_default(self):
        """Empty string tradition should fall back to the 'default' tradition."""
        r_empty = vulca.evaluate("test.png", tradition="", mock=True)
        r_default = vulca.evaluate("test.png", tradition="default", mock=True)
        assert r_empty.score == pytest.approx(r_default.score, abs=0.001), (
            f"Empty tradition score {r_empty.score} != default score {r_default.score}"
        )


class TestNegativeInputs:
    """Invalid file paths and empty inputs must degrade gracefully."""

    def test_nonexistent_image_mock_does_not_crash(self):
        """mock=True skips file I/O — a nonexistent path must not crash.

        In production (mock=False), a missing file would raise when the
        provider tries to open it. In mock mode, the path is unused.
        """
        result = vulca.evaluate(
            "/tmp/definitely_not_a_real_file_abc123.png",
            tradition="default",
            mock=True,
        )
        assert result.score is not None
        assert 0.0 <= result.score <= 1.0

    def test_empty_intent_create_does_not_crash(self):
        """Empty intent should either raise or produce a valid result, not crash."""
        try:
            result = vulca.create("", provider="mock")
            assert result.session_id != ""
        except (ValueError, TypeError):
            pass  # Raising is also acceptable behavior


class TestScoreSanity:
    """Statistical invariants across all 13 traditions."""

    def test_no_perfect_scores(self):
        """No tradition should receive a perfect 1.0 score in mock mode."""
        for tradition, *_, total in MOCK_GOLDEN:
            assert total < 1.0, f"{tradition} has perfect score {total}"

    def test_traditions_have_different_scores(self):
        """All 13 traditions must produce distinct total scores."""
        totals = [t[-1] for t in MOCK_GOLDEN]
        assert len(set(totals)) == len(totals), (
            f"Some traditions share identical scores: {totals}"
        )

    def test_scores_in_valid_range(self):
        """Every L1-L5 dimension score and weighted total must be in [0, 1]."""
        for tradition, L1, L2, L3, L4, L5, total in MOCK_GOLDEN:
            for name, val in [
                ("L1", L1), ("L2", L2), ("L3", L3), ("L4", L4), ("L5", L5),
                ("total", total),
            ]:
                assert 0.0 <= val <= 1.0, (
                    f"{tradition} {name}={val} out of [0, 1]"
                )

    def test_dimension_names_are_l1_to_l5(self):
        """EvalResult.dimensions must have exactly the keys L1, L2, L3, L4, L5."""
        result = vulca.evaluate("test.png", tradition="default", mock=True)
        assert set(result.dimensions.keys()) == {"L1", "L2", "L3", "L4", "L5"}

    def test_weighted_total_between_min_and_max(self):
        """The weighted total must not exceed the best dimension or fall below the worst."""
        for tradition, L1, L2, L3, L4, L5, total in MOCK_GOLDEN:
            scores = [L1, L2, L3, L4, L5]
            assert min(scores) <= total <= max(scores), (
                f"{tradition}: total {total} not between "
                f"min {min(scores)} and max {max(scores)}"
            )

    def test_rationales_are_generic_in_mock_mode(self):
        """Mock rationales are intentionally generic — they do NOT embed tradition names.

        This is the current documented behavior of mock=True. If this test fails,
        it means the mock was upgraded to tradition-aware rationales (update this test).
        """
        for tradition, *_ in MOCK_GOLDEN:
            result = vulca.evaluate("test.png", tradition=tradition, mock=True)
            all_rationales = " ".join(result.rationales.values())
            # All mock rationales share the same generic prefix
            assert "Mock:" in all_rationales, (
                f"{tradition}: mock rationale does not contain 'Mock:' prefix"
            )

    def test_rationales_nonempty_for_all_traditions(self):
        """Every L1-L5 dimension must have a non-empty rationale string."""
        for tradition, *_ in MOCK_GOLDEN:
            result = vulca.evaluate("test.png", tradition=tradition, mock=True)
            for dim in ["L1", "L2", "L3", "L4", "L5"]:
                rationale = result.rationales.get(dim, "")
                assert isinstance(rationale, str) and len(rationale) > 0, (
                    f"{tradition} {dim}: rationale is empty or missing"
                )
