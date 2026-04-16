"""Phase 0 Task 4b follow-up: MCP layers_edit roundtrip semantic_path.

Closes the gap flagged by codex review — the subagent skipped this test
citing MCP harness invasiveness, but fastmcp's @mcp.tool() decorator
keeps the underlying async function importable and awaitable.
"""
import asyncio
import json
from pathlib import Path

import pytest
from PIL import Image


def _seed_artwork(tmp_path: Path) -> None:
    src_png = tmp_path / "src.png"
    Image.new("RGBA", (64, 64), (0, 0, 0, 0)).save(src_png)
    (tmp_path / "manifest.json").write_text(json.dumps({
        "version": 3, "width": 64, "height": 64, "layers": [],
        "source_image": str(src_png), "split_mode": "",
    }))


def _call_layers_edit(**kwargs):
    """Call the underlying async handler past the @mcp.tool() decorator."""
    from vulca.mcp_server import layers_edit
    # fastmcp wraps async functions as FunctionTool; the underlying callable
    # lives at `.fn` — fallback to direct invoke if older versions differ.
    fn = getattr(layers_edit, "fn", layers_edit)
    result = fn(**kwargs)
    if asyncio.iscoroutine(result):
        result = asyncio.run(result)
    return result


def test_layers_edit_add_returns_semantic_path(tmp_path):
    _seed_artwork(tmp_path)
    result = _call_layers_edit(
        artwork_dir=str(tmp_path),
        operation="add",
        name="eyes",
        description="eye detail",
        content_type="subject",
        semantic_path="subject.face.eyes",
    )
    assert result["operation"] == "add"
    assert result["name"] == "eyes"
    assert result.get("semantic_path") == "subject.face.eyes"


def test_layers_edit_add_persists_semantic_path(tmp_path):
    _seed_artwork(tmp_path)
    _call_layers_edit(
        artwork_dir=str(tmp_path),
        operation="add",
        name="hair",
        description="",
        content_type="subject",
        semantic_path="subject.hair",
    )
    data = json.loads((tmp_path / "manifest.json").read_text())
    hair = next(l for l in data["layers"] if l["name"] == "hair")
    assert hair["semantic_path"] == "subject.hair"


def test_layers_edit_add_default_semantic_path_empty(tmp_path):
    _seed_artwork(tmp_path)
    result = _call_layers_edit(
        artwork_dir=str(tmp_path),
        operation="add",
        name="sky",
        description="",
        content_type="background",
    )
    assert result.get("semantic_path") == ""
