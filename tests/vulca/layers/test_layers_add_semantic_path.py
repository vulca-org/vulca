import os
import subprocess
import sys
from pathlib import Path


def _cli(*args) -> subprocess.CompletedProcess:
    repo_root = Path(__file__).resolve().parents[3]
    env = os.environ.copy()
    src = str(repo_root / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "vulca", *args],
        capture_output=True, text=True, env=env,
    )


def test_layers_add_help_lists_semantic_path():
    result = _cli("layers", "add", "--help")
    assert result.returncode == 0
    assert "--semantic-path" in result.stdout


def test_layers_add_semantic_path_roundtrips_to_manifest(tmp_path):
    import json
    from PIL import Image
    src_png = tmp_path / "src.png"
    Image.new("RGBA", (64, 64), (0, 0, 0, 0)).save(src_png)
    (tmp_path / "manifest.json").write_text(json.dumps({
        "version": 3, "width": 64, "height": 64, "layers": [],
        "source_image": str(src_png), "split_mode": "",
    }))
    r = _cli(
        "layers", "add", str(tmp_path),
        "--name", "eyes",
        "--semantic-path", "subject.face.eyes",
        "--content-type", "subject",
    )
    assert r.returncode == 0, f"stderr={r.stderr}"
    data = json.loads((tmp_path / "manifest.json").read_text())
    eyes = next(l for l in data["layers"] if l["name"] == "eyes")
    assert eyes.get("semantic_path") == "subject.face.eyes"
