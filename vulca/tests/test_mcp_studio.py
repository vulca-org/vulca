"""Tests for Studio MCP tools."""
from __future__ import annotations

import pytest


@pytest.fixture
async def mcp_tools():
    """Get the MCP server's tool functions."""
    import asyncio
    from vulca.mcp_server import mcp
    tools = await mcp.list_tools()
    return {tool.name: tool for tool in tools}


def test_mcp_studio_tools_registered(mcp_tools):
    """Studio tools should be registered in the MCP server."""
    assert "studio_create_brief" in mcp_tools
    assert "studio_update_brief" in mcp_tools
    assert "studio_generate_concepts" in mcp_tools
    assert "studio_select_concept" in mcp_tools


def test_mcp_existing_tools_preserved(mcp_tools):
    """Existing tools must still exist (backward compatibility)."""
    assert "create_artwork" in mcp_tools
    assert "evaluate_artwork" in mcp_tools
    assert "list_traditions" in mcp_tools


@pytest.mark.asyncio
async def test_mcp_studio_create_brief(tmp_path):
    from vulca.mcp_server import _studio_create_brief_impl
    result = await _studio_create_brief_impl(
        intent="水墨山水",
        mood="serene",
        project_dir=str(tmp_path),
    )
    assert "session_id" in result
    assert (tmp_path / "brief.yaml").exists()


@pytest.mark.asyncio
async def test_mcp_studio_update_brief(tmp_path):
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    b.save(tmp_path)

    from vulca.mcp_server import _studio_update_brief_impl
    result = await _studio_update_brief_impl(
        project_dir=str(tmp_path),
        instruction="加入霓虹效果",
    )
    assert "rollback_to" in result
