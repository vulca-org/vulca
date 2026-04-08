import os
import subprocess
import sys


def _run(*argv):
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    return subprocess.run([sys.executable, "-m", "vulca", *argv],
                          capture_output=True, text=True, env=env)


def test_retry_subcommand_help():
    out = _run("layers", "retry", "--help")
    assert out.returncode == 0, out.stderr
    assert "--layer" in out.stdout
    assert "--all-failed" in out.stdout
    assert "artifact_dir" in out.stdout


def test_retry_helper_picks_targets(tmp_path):
    """pick_targets() returns files that are missing on disk when all_failed=True."""
    from vulca.layers.retry import pick_targets
    manifest = {
        "layers": [
            {"id": "a", "name": "bg", "file": "bg.png",
             "validation": {"ok": True, "warnings": []}},
            {"id": "b", "name": "far", "file": "far.png",
             "validation": {"ok": False, "warnings": [{"kind": "coverage"}]}},
        ]
    }
    (tmp_path / "bg.png").write_bytes(b"PNG")
    # far.png intentionally missing — should also be picked
    targets = pick_targets(manifest, tmp_path, all_failed=True)
    names = sorted(t["name"] for t in targets)
    assert names == ["far"]

    targets = pick_targets(manifest, tmp_path, layer_names=["bg"])
    assert [t["name"] for t in targets] == ["bg"]
