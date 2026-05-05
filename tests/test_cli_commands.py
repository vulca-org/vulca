import os
from pathlib import Path
import subprocess
import sys

VULCA = [sys.executable, "-m", "vulca.cli"]
ROOT = Path(__file__).resolve().parent.parent
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=(
        str(ROOT / "src")
        + os.pathsep
        + os.environ.get("PYTHONPATH", "")
    ),
)


def run_vulca(args):
    return subprocess.run(
        VULCA + args,
        capture_output=True, text=True, timeout=10, env=CLI_ENV,
    )


class TestCLICommands:
    def test_studio_help(self):
        result = run_vulca(["studio", "--help"])
        assert result.returncode == 0
        assert "studio" in result.stdout.lower() or "interactive" in result.stdout.lower()

    def test_brief_help(self):
        result = run_vulca(["brief", "--help"])
        assert result.returncode == 0

    def test_brief_update_help(self):
        result = run_vulca(["brief-update", "--help"])
        assert result.returncode == 0

    def test_concept_help(self):
        result = run_vulca(["concept", "--help"])
        assert result.returncode == 0

    def test_no_click_import(self):
        from pathlib import Path
        cli_path = Path(__file__).resolve().parent.parent / "src" / "vulca" / "cli.py"
        content = cli_path.read_text()
        assert "import click" not in content

    def test_existing_evaluate_still_works(self):
        result = run_vulca(["evaluate", "--help"])
        assert result.returncode == 0
        assert "evaluate" in result.stdout.lower() or "artwork" in result.stdout.lower()

    def test_layers_redraw_help_mentions_case_log(self):
        result = run_vulca(["layers", "redraw", "--help"])
        assert result.returncode == 0
        assert "--case-log" in result.stdout

    def test_layers_split_help_mentions_case_log(self):
        result = run_vulca(["layers", "split", "--help"])
        assert result.returncode == 0
        assert "--case-log" in result.stdout
