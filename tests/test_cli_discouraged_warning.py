import os
import subprocess
import sys


def _run(*argv, stdin_input: str = ""):
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    # Force non-tty behavior so the warning goes to stderr instead of prompting.
    return subprocess.run([sys.executable, "-m", "vulca", *argv],
                          capture_output=True, text=True, env=env, input=stdin_input)


def test_discouraged_tradition_warns_on_non_tty():
    out = _run("create", "远山薄雾", "-t", "photography", "--layered",
               "--provider", "mock")
    combined = out.stderr + out.stdout
    assert "does not support high-quality layering" in combined
