"""Tests for Layers V2 CLI flags: --mode on split, redraw subcommand."""
import subprocess
import sys

VULCA = [sys.executable, "-m", "vulca.cli"]


class TestLayersV2CLI:
    def test_layers_split_has_mode_flag(self):
        result = subprocess.run(
            VULCA + ["layers", "split", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--mode" in result.stdout

    def test_layers_split_has_provider_flag(self):
        result = subprocess.run(
            VULCA + ["layers", "split", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--provider" in result.stdout

    def test_layers_split_has_tradition_flag(self):
        result = subprocess.run(
            VULCA + ["layers", "split", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--tradition" in result.stdout

    def test_layers_redraw_in_help(self):
        result = subprocess.run(
            VULCA + ["layers", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "redraw" in result.stdout

    def test_layers_redraw_has_flags(self):
        result = subprocess.run(
            VULCA + ["layers", "redraw", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--layer" in result.stdout
        assert "--instruction" in result.stdout
        assert "--layers" in result.stdout
        assert "--merge" in result.stdout

    def test_layers_redraw_has_provider_flag(self):
        result = subprocess.run(
            VULCA + ["layers", "redraw", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--provider" in result.stdout

    def test_layers_redraw_has_tradition_flag(self):
        result = subprocess.run(
            VULCA + ["layers", "redraw", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--tradition" in result.stdout


class TestLayersEditCLI:
    def test_add_in_help(self):
        result = subprocess.run(VULCA + ["layers", "--help"], capture_output=True, text=True, timeout=10)
        assert "add" in result.stdout

    def test_remove_in_help(self):
        result = subprocess.run(VULCA + ["layers", "--help"], capture_output=True, text=True, timeout=10)
        assert "remove" in result.stdout

    def test_reorder_in_help(self):
        result = subprocess.run(VULCA + ["layers", "--help"], capture_output=True, text=True, timeout=10)
        assert "reorder" in result.stdout

    def test_toggle_in_help(self):
        result = subprocess.run(VULCA + ["layers", "--help"], capture_output=True, text=True, timeout=10)
        assert "toggle" in result.stdout

    def test_lock_in_help(self):
        result = subprocess.run(VULCA + ["layers", "--help"], capture_output=True, text=True, timeout=10)
        assert "lock" in result.stdout

    def test_merge_in_help(self):
        result = subprocess.run(VULCA + ["layers", "--help"], capture_output=True, text=True, timeout=10)
        assert "merge" in result.stdout

    def test_duplicate_in_help(self):
        result = subprocess.run(VULCA + ["layers", "--help"], capture_output=True, text=True, timeout=10)
        assert "duplicate" in result.stdout

    def test_add_has_flags(self):
        result = subprocess.run(VULCA + ["layers", "add", "--help"], capture_output=True, text=True, timeout=10)
        assert "--name" in result.stdout
        assert "--description" in result.stdout
        assert "--z-index" in result.stdout

    def test_redraw_has_resplit(self):
        result = subprocess.run(VULCA + ["layers", "redraw", "--help"], capture_output=True, text=True, timeout=10)
        assert "--re-split" in result.stdout

    def test_split_has_sam_mode(self):
        result = subprocess.run(VULCA + ["layers", "split", "--help"], capture_output=True, text=True, timeout=10)
        assert "sam" in result.stdout
