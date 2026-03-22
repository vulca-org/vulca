"""Tests for VULCA MCP server tools."""

from __future__ import annotations

import pytest

from vulca.mcp_server import _parse_weights_str


class TestParseWeightsStr:
    """Test the MCP weight string parser."""

    def test_valid_weights(self):
        result = _parse_weights_str("L1=0.3,L2=0.2,L3=0.2,L4=0.15,L5=0.15")
        assert result == {"L1": 0.3, "L2": 0.2, "L3": 0.2, "L4": 0.15, "L5": 0.15}

    def test_with_spaces(self):
        result = _parse_weights_str("L1=0.3, L2=0.2, L3=0.5")
        assert result == {"L1": 0.3, "L2": 0.2, "L3": 0.5}

    def test_empty_string(self):
        assert _parse_weights_str("") == {}

    def test_whitespace_only(self):
        assert _parse_weights_str("   ") == {}

    def test_partial_valid(self):
        result = _parse_weights_str("L1=0.3,bad,L2=0.7")
        assert result == {"L1": 0.3, "L2": 0.7}

    def test_invalid_dimension_ignored(self):
        result = _parse_weights_str("L1=0.3,L9=0.5")
        assert result == {"L1": 0.3}

    def test_invalid_value_ignored(self):
        result = _parse_weights_str("L1=abc,L2=0.5")
        assert result == {"L2": 0.5}

    def test_lowercase_normalized(self):
        result = _parse_weights_str("l1=0.3,l2=0.7")
        assert result == {"L1": 0.3, "L2": 0.7}


class TestCreateArtworkTool:
    """Test the create_artwork MCP tool."""

    @pytest.mark.asyncio
    async def test_basic_create(self):
        from vulca.mcp_server import create_artwork
        result = await create_artwork("test artwork", provider="mock")
        assert "session_id" in result
        assert result["status"] == "completed"
        assert result["interrupted_at"] == ""
        assert result["weighted_total"] > 0

    @pytest.mark.asyncio
    async def test_hitl_create(self):
        from vulca.mcp_server import create_artwork
        result = await create_artwork("test artwork", provider="mock", hitl=True)
        assert result["status"] == "waiting_human"
        assert result["interrupted_at"] == "decide"
        assert result["weighted_total"]  # evaluate ran

    @pytest.mark.asyncio
    async def test_weights_create(self):
        from vulca.mcp_server import create_artwork
        r_default = await create_artwork("test", provider="mock")
        r_custom = await create_artwork(
            "test", provider="mock",
            weights="L1=1.0,L2=0.0,L3=0.0,L4=0.0,L5=0.0",
        )
        assert r_default["weighted_total"] != r_custom["weighted_total"]
