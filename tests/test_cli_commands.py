import subprocess
import sys

VULCA = [sys.executable, "-m", "vulca.cli"]


class TestCLICommands:
    def test_studio_help(self):
        result = subprocess.run(
            VULCA + ["studio", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "studio" in result.stdout.lower() or "interactive" in result.stdout.lower()

    def test_brief_help(self):
        result = subprocess.run(
            VULCA + ["brief", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0

    def test_brief_update_help(self):
        result = subprocess.run(
            VULCA + ["brief-update", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0

    def test_concept_help(self):
        result = subprocess.run(
            VULCA + ["concept", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0

    def test_no_click_import(self):
        from pathlib import Path
        cli_path = Path(__file__).resolve().parent.parent / "src" / "vulca" / "cli.py"
        content = cli_path.read_text()
        assert "import click" not in content

    def test_existing_evaluate_still_works(self):
        result = subprocess.run(
            VULCA + ["evaluate", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "evaluate" in result.stdout.lower() or "artwork" in result.stdout.lower()
