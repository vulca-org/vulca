"""Subprocess smoke: _import_cop() resolves correctly from fresh process.

Catches sys.path drift between pytest harness and runtime (MCP server starts
in a new process; pytest session may already have /scripts on sys.path).
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_import_cop_from_fresh_process():
    script = f"""
import sys
sys.path.insert(0, {str(REPO / 'src')!r})
from vulca.pipeline.segment.orchestrator import _import_cop
cop = _import_cop()
assert cop.__name__ == "claude_orchestrated_pipeline", cop.__name__
for name in ("load_grounding_dino", "load_yolo",
             "load_face_parser", "_load_sam_model"):
    assert callable(getattr(cop, name).cache_clear), name
print("OK")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, (
        f"subprocess failed:\\nstderr={result.stderr}\\nstdout={result.stdout}"
    )
    assert "OK" in result.stdout, f"stdout={result.stdout}"
