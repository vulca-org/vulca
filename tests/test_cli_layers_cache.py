import os
import subprocess
import sys
from pathlib import Path


def _run(*argv):
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    return subprocess.run([sys.executable, "-m", "vulca", *argv],
                          capture_output=True, text=True, env=env)


def test_cache_clear_removes_dir(tmp_path):
    cache_dir = tmp_path / ".layered_cache"
    cache_dir.mkdir()
    (cache_dir / "x.png").write_bytes(b"PNG")
    out = _run("layers", "cache", "clear", str(tmp_path))
    assert out.returncode == 0, out.stderr
    assert not cache_dir.exists()


def test_cache_clear_on_missing_dir_is_noop(tmp_path):
    out = _run("layers", "cache", "clear", str(tmp_path))
    assert out.returncode == 0, out.stderr
