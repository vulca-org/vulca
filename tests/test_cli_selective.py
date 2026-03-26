"""Tests for CLI --residuals and --sparse-eval flags."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from vulca.cli import main


class TestCLISelectiveFlags:
    """CLI accepts --residuals and --sparse-eval flags."""

    def test_create_accepts_residuals_flag(self, capsys):
        """vulca create --residuals should not error on flag parsing."""
        # Use mock provider to avoid API calls
        with pytest.raises(SystemExit) as exc:
            main(["create", "test intent", "--provider", "mock", "--residuals"])
        # Should NOT exit with code 2 (argparse error)
        # Code 0 = success, Code 1 = runtime error (acceptable)
        assert exc.value.code != 2

    def test_create_accepts_sparse_eval_flag(self, capsys):
        """vulca create --sparse-eval should not error on flag parsing."""
        with pytest.raises(SystemExit) as exc:
            main(["create", "test intent", "--provider", "mock", "--sparse-eval"])
        assert exc.value.code != 2

    def test_create_accepts_both_flags(self, capsys):
        """vulca create --residuals --sparse-eval should not error."""
        with pytest.raises(SystemExit) as exc:
            main(["create", "test intent", "--provider", "mock",
                  "--residuals", "--sparse-eval"])
        assert exc.value.code != 2

    def test_evaluate_accepts_sparse_eval_flag(self, capsys):
        """vulca evaluate --sparse-eval should not error on flag parsing."""
        # evaluate needs an image file — use a non-existent path, will fail at runtime not argparse
        with pytest.raises(SystemExit) as exc:
            main(["evaluate", "nonexistent.png", "--mock", "--sparse-eval"])
        assert exc.value.code != 2

    def test_create_without_flags_still_works(self, capsys):
        """Backward compat: vulca create without new flags works."""
        with pytest.raises(SystemExit) as exc:
            main(["create", "test intent", "--provider", "mock"])
        assert exc.value.code != 2
