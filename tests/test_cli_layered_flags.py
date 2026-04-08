import os
import subprocess
import sys


def _run_help():
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    return subprocess.run(
        [sys.executable, "-m", "vulca", "create", "--help"],
        capture_output=True, text=True, env=env,
    )


def test_layered_flags_present_in_help():
    out = _run_help()
    assert out.returncode == 0, out.stderr
    assert "--no-cache" in out.stdout
    assert "--strict" in out.stdout
    assert "--max-layers" in out.stdout
