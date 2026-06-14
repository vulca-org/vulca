#!/usr/bin/env python3
"""Synchronize generated Vulca plugin package files from SDK source truth."""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL_TARGETS = (".claude/skills", "skills")


class SyncResult:
    def __init__(self, *, changed: bool, messages: list[str]) -> None:
        self.changed = changed
        self.messages = messages


def _is_mcp_tool_decorator(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "tool"
        and isinstance(func.value, ast.Name)
        and func.value.id == "mcp"
    )


def extract_mcp_tool_names(path: Path) -> list[str]:
    """Return names of functions decorated with @mcp.tool() without importing MCP."""
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(module):
        if not isinstance(node, ast.AsyncFunctionDef | ast.FunctionDef):
            continue
        if any(_is_mcp_tool_decorator(decorator) for decorator in node.decorator_list):
            names.append(node.name)
    return sorted(names)


def _project_version(pyproject: Path) -> str:
    in_project = False
    for raw_line in pyproject.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "[project]":
            in_project = True
            continue
        if line.startswith("[") and line.endswith("]"):
            in_project = False
        if not in_project:
            continue
        match = re.match(r'version\s*=\s*"([^"]+)"', line)
        if match:
            return match.group(1)
    raise ValueError(f"could not find [project] version in {pyproject}")


def _skill_names(source: Path) -> list[str]:
    return sorted(path.parent.name for path in source.glob("*/SKILL.md"))


def _read_file_map(directory: Path) -> dict[str, bytes]:
    if not directory.exists():
        return {}
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _write_if_changed(path: Path, content: str, *, check: bool) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return True


def _sync_json_version(path: Path, version: str, *, check: bool) -> bool:
    if not path.exists():
        return False
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") == version:
        return False
    payload["version"] = version
    if not check:
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return True


def _plugin_readme(*, version: str, tools: list[str], skills: list[str]) -> str:
    tool_rows = "\n".join(f"| `{tool}` |" for tool in tools)
    skill_rows = "\n".join(f"- `{skill}`" for skill in skills)
    return f"""# Vulca Plugin Package

Generated package metadata for Vulca SDK `{version}`.

## MCP Tools

| Tool |
|---|
{tool_rows}

## Skills

{skill_rows}

## Release Check

Run this from the Vulca SDK repository before tagging a release:

```bash
python scripts/sync_plugin.py --check
```
"""


def _sync_skill_target(root: Path, source: Path, target: Path, *, check: bool) -> tuple[bool, str]:
    changed = _read_file_map(source) != _read_file_map(target)
    if changed and not check:
        _copy_tree(source, target)
    return changed, f"{_rel(root, target)} is out of sync"


def sync_plugin_package(
    *,
    root: Path = ROOT,
    plugin_root: Path | None = None,
    check: bool = False,
) -> SyncResult:
    root = Path(root).resolve()
    plugin_root = Path(plugin_root).resolve() if plugin_root else root / "plugins" / "vulca"
    skills_source = root / ".agents" / "skills"
    if not skills_source.is_dir():
        raise FileNotFoundError(f"missing canonical skills directory: {skills_source}")

    version = _project_version(root / "pyproject.toml")
    tools = extract_mcp_tool_names(root / "src" / "vulca" / "mcp_server.py")
    skills = _skill_names(skills_source)
    changed = False
    messages: list[str] = []

    for relative in SKILL_TARGETS:
        target = root / relative
        target_changed, message = _sync_skill_target(root, skills_source, target, check=check)
        if target_changed:
            changed = True
            messages.append(message)

    plugin_skill_changed, plugin_skill_message = _sync_skill_target(
        root, skills_source, plugin_root / "skills", check=check
    )
    if plugin_skill_changed:
        changed = True
        messages.append(plugin_skill_message)

    for manifest in (
        root / ".claude-plugin" / "plugin.json",
        plugin_root / ".claude-plugin" / "plugin.json",
        plugin_root / ".codex-plugin" / "plugin.json",
    ):
        if _sync_json_version(manifest, version, check=check):
            changed = True
            messages.append(f"{_rel(root, manifest)} is out of sync")

    readme = plugin_root / "README.md"
    if _write_if_changed(
        readme,
        _plugin_readme(version=version, tools=tools, skills=skills),
        check=check,
    ):
        changed = True
        messages.append(f"{_rel(root, readme)} is out of sync")

    if not messages:
        messages.append("plugin package is in sync")
    return SyncResult(changed=changed, messages=messages)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Vulca SDK repository root")
    parser.add_argument(
        "--plugin-root",
        type=Path,
        default=None,
        help="Plugin package root; defaults to <root>/plugins/vulca",
    )
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    args = parser.parse_args(argv)

    result = sync_plugin_package(
        root=args.root,
        plugin_root=args.plugin_root,
        check=args.check,
    )
    for message in result.messages:
        print(message)
    return 1 if args.check and result.changed else 0


if __name__ == "__main__":
    sys.exit(main())
