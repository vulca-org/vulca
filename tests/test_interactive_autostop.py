"""Tests for should_suggest_stop() — auto-stop heuristic for interactive loop."""
from vulca.studio.interactive import should_suggest_stop


class TestAutoStop:
    def test_suggest_stop_threshold(self):
        assert should_suggest_stop([0.60, 0.75, 0.86], target=0.85) is True

    def test_no_suggest_below_threshold(self):
        assert should_suggest_stop([0.60, 0.70], target=0.85) is False

    def test_suggest_stop_convergence(self):
        assert should_suggest_stop([0.60, 0.78, 0.79], target=0.95) is True

    def test_no_suggest_single_round(self):
        assert should_suggest_stop([0.60], target=0.85) is False

    def test_no_suggest_still_improving(self):
        assert should_suggest_stop([0.60, 0.70, 0.80], target=0.95) is False

    def test_convergence_needs_two_rounds(self):
        assert should_suggest_stop([0.60, 0.62], target=0.95) is True

    def test_empty_scores(self):
        assert should_suggest_stop([], target=0.85) is False
