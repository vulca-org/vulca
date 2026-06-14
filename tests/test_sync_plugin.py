from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_sync_plugin():
    spec = importlib.util.spec_from_file_location(
        "sync_plugin", ROOT / "scripts" / "sync_plugin.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_fixture_repo(root: Path) -> None:
    (root / "src" / "vulca").mkdir(parents=True)
    (root / ".agents" / "skills" / "decompose").mkdir(parents=True)
    (root / ".agents" / "skills" / "evaluate").mkdir(parents=True)
    (root / "plugins" / "vulca" / ".codex-plugin").mkdir(parents=True)
    (root / "plugins" / "vulca" / "skills" / "stale").mkdir(parents=True)

    (root / "pyproject.toml").write_text(
        '[project]\nname = "vulca"\nversion = "9.8.7"\n',
        encoding="utf-8",
    )
    (root / "src" / "vulca" / "mcp_server.py").write_text(
        """
from fastmcp import FastMCP

mcp = FastMCP("VULCA")

@mcp.tool()
async def create_artwork(intent: str) -> dict:
    return {}

@mcp.tool()
def evaluate_artwork(image_path: str) -> dict:
    return {}
""".lstrip(),
        encoding="utf-8",
    )
    (root / ".agents" / "skills" / "decompose" / "SKILL.md").write_text(
        "---\nname: decompose\ndescription: Split images.\n---\n",
        encoding="utf-8",
    )
    (root / ".agents" / "skills" / "evaluate" / "SKILL.md").write_text(
        "---\nname: evaluate\ndescription: Score images.\n---\n",
        encoding="utf-8",
    )
    (root / "plugins" / "vulca" / ".codex-plugin" / "plugin.json").write_text(
        json.dumps({"name": "vulca", "version": "0.0.1", "skills": "./skills/"}),
        encoding="utf-8",
    )
    (root / "plugins" / "vulca" / "skills" / "stale" / "SKILL.md").write_text(
        "stale",
        encoding="utf-8",
    )


def test_extracts_mcp_tool_names_without_importing_fastmcp():
    sync_plugin = _load_sync_plugin()

    tools = sync_plugin.extract_mcp_tool_names(ROOT / "src" / "vulca" / "mcp_server.py")

    assert "create_artwork" in tools
    assert "evaluate_artwork" in tools
    assert tools == sorted(tools)


def test_sync_plugin_updates_manifest_skills_and_readme(tmp_path):
    sync_plugin = _load_sync_plugin()
    _write_fixture_repo(tmp_path)

    result = sync_plugin.sync_plugin_package(root=tmp_path)

    assert result.changed
    manifest = json.loads(
        (
            tmp_path
            / "plugins"
            / "vulca"
            / ".codex-plugin"
            / "plugin.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["version"] == "9.8.7"

    copied_skills = {
        path.parent.name
        for path in (tmp_path / "plugins" / "vulca" / "skills").glob("*/SKILL.md")
    }
    assert copied_skills == {"decompose", "evaluate"}

    readme = (tmp_path / "plugins" / "vulca" / "README.md").read_text(
        encoding="utf-8"
    )
    assert "| `create_artwork` |" in readme
    assert "| `evaluate_artwork` |" in readme
    assert "decompose" in readme
    assert "stale" not in readme


def test_sync_plugin_check_reports_drift_without_modifying(tmp_path):
    _write_fixture_repo(tmp_path)
    stale_manifest = (
        tmp_path / "plugins" / "vulca" / ".codex-plugin" / "plugin.json"
    ).read_text(encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "sync_plugin.py"),
            "--root",
            str(tmp_path),
            "--check",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "plugins/vulca/.codex-plugin/plugin.json is out of sync" in completed.stdout
    assert "plugins/vulca/skills is out of sync" in completed.stdout
    assert (
        tmp_path / "plugins" / "vulca" / ".codex-plugin" / "plugin.json"
    ).read_text(encoding="utf-8") == stale_manifest


def test_legacy_skill_sync_entrypoint_delegates_to_full_sync(tmp_path):
    _write_fixture_repo(tmp_path)

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "sync_plugin_skills.py"),
            "--root",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert (tmp_path / "plugins" / "vulca" / "README.md").exists()
    manifest = json.loads(
        (
            tmp_path
            / "plugins"
            / "vulca"
            / ".codex-plugin"
            / "plugin.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["version"] == "9.8.7"
