"""Tests for stateless brief/concept/archive MCP tools."""
from __future__ import annotations

import asyncio

import pytest
pytest.importorskip("fastmcp", reason="fastmcp is an optional dependency (pip install vulca[mcp])")


def run(coro):
    return asyncio.run(coro)


def _get_tool_names():
    from vulca.mcp_server import mcp
    tools = run(mcp.list_tools())
    return {tool.name for tool in tools}


def test_new_tools_registered():
    """New stateless tools should be registered in the MCP server."""
    names = _get_tool_names()
    assert "brief_parse" in names
    assert "generate_concepts" in names
    assert "archive_session" in names


def test_old_studio_tools_removed():
    """Old studio tools should no longer exist."""
    names = _get_tool_names()
    assert "studio_create_brief" not in names
    assert "studio_generate_concepts" not in names
    assert "studio_accept" not in names


def test_existing_tools_preserved():
    """Core tools must still exist."""
    names = _get_tool_names()
    assert "create_artwork" in names
    assert "evaluate_artwork" in names
    assert "list_traditions" in names


class TestBriefParse:
    def test_returns_structured_brief(self):
        from vulca.mcp_server import brief_parse
        r = run(brief_parse("水墨山水 with mountains", mood="serene"))
        assert r["intent"] == "水墨山水 with mountains"
        assert r["mood"] == "serene"
        assert "tradition" in r
        assert "style_mix" in r
        assert "keywords" in r
        assert "composition" in r
        assert "palette" in r

    def test_detects_tradition(self):
        from vulca.mcp_server import brief_parse
        r = run(brief_parse("水墨山水"))
        assert r["tradition"] == "chinese_xieyi"

    def test_default_tradition_when_unknown(self):
        from vulca.mcp_server import brief_parse
        r = run(brief_parse("abstract colorful shapes"))
        # Should still return a tradition (may be default or detected)
        assert "tradition" in r


class TestGenerateConcepts:
    def test_mock_generates_multiple(self):
        from vulca.mcp_server import generate_concepts
        r = run(generate_concepts("a mountain", count=2, provider="mock"))
        assert len(r["concepts"]) == 2
        assert "total_cost_usd" in r
        for c in r["concepts"]:
            assert "image_path" in c

    def test_count_clamped(self):
        from vulca.mcp_server import generate_concepts
        r = run(generate_concepts("test", count=10, provider="mock"))
        assert len(r["concepts"]) == 6  # max 6


class TestArchiveSession:
    def test_archive_returns_session_id(self):
        from vulca.mcp_server import archive_session
        r = run(archive_session(
            intent="test artwork",
            tradition="default",
            feedback="looks good",
        ))
        assert "session_id" in r
        assert "archived" in r
