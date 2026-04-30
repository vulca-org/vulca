from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_stale_tool_count_claims_removed_from_public_docs():
    public_text = "\n".join(
        [
            (ROOT / "README.md").read_text(encoding="utf-8"),
            (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
            (ROOT / "src" / "vulca" / "mcp_server.py").read_text(
                encoding="utf-8"
            ),
        ]
    )

    assert "20 MCP tools" not in public_text
    assert "21 MCP tools" not in public_text


def test_readme_mentions_visual_discovery_and_mock_boundary():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "/visual-discovery" in readme
    assert "mock sketch" in readme.lower()
    assert "real provider sketch" in readme.lower()
