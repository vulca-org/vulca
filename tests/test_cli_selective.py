"""Tests for CLI --sparse-eval flag."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from vulca.cli import main


class TestCLISelectiveFlags:
    """CLI accepts --sparse-eval flag."""

    def test_create_accepts_sparse_eval_flag(self, capsys):
        """vulca create --sparse-eval should complete without argparse error."""
        main(["create", "test intent", "--provider", "mock", "--sparse-eval"])
        captured = capsys.readouterr()
        assert "VULCA Creation Result" in captured.out

    def test_evaluate_accepts_sparse_eval_flag(self, capsys):
        """vulca evaluate --sparse-eval should not be an argparse error."""
        # --mock scoring doesn't need a real file, just tests argparse accepts the flag
        main(["evaluate", "nonexistent.png", "--mock", "--sparse-eval"])
        captured = capsys.readouterr()
        # Should produce evaluation output, not argparse error
        assert "Error" not in captured.err or "unrecognized" not in captured.err

    def test_create_without_flags_still_works(self, capsys):
        """Backward compat: vulca create without new flags works."""
        main(["create", "test intent", "--provider", "mock"])
        captured = capsys.readouterr()
        assert "VULCA Creation Result" in captured.out
