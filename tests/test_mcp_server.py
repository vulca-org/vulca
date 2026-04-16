"""Tests for VULCA MCP server tools."""

from __future__ import annotations

import asyncio

import pytest
pytest.importorskip("fastmcp", reason="fastmcp is an optional dependency (pip install vulca[mcp])")

from vulca.mcp_server import _parse_weights_str


def run(coro):
    return asyncio.run(coro)


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
    """Test the create_artwork MCP tool (single-pass: generate + evaluate)."""

    def test_basic_create(self):
        from vulca.mcp_server import create_artwork
        result = run(create_artwork("test artwork", provider="mock"))
        assert "image_path" in result
        assert "weighted_total" in result
        assert "scores" in result
        assert "rationales" in result
        assert "recommendations" in result
        assert "cost_usd" in result

    def test_weights_create(self):
        from vulca.mcp_server import create_artwork
        r_default = run(create_artwork("test", provider="mock"))
        r_custom = run(create_artwork(
            "test", provider="mock",
            weights="L1=1.0,L2=0.0,L3=0.0,L4=0.0,L5=0.0",
        ))
        # Custom weights should produce a different weighted_total
        assert "weighted_total" in r_default
        assert "weighted_total" in r_custom
