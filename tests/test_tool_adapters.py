"""Tests for CLI, SDK, and MCP adapters — Tasks 6, 7, 8.

Covers 14 test cases across all three adapters.
"""

from __future__ import annotations

import base64
import io

import numpy as np
import pytest
from PIL import Image

from vulca.tools.protocol import ImageData


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def test_image_path(tmp_path):
    img = Image.new("RGB", (20, 20), (200, 200, 200))
    path = tmp_path / "test_img.png"
    img.save(path)
    return str(path)


# ===========================================================================
# CLI tests
# ===========================================================================


def test_cli_tools_list():
    """vulca tools list should contain both discovered tool names."""
    from vulca.tools.adapters.cli import build_tools_parser, run_tools_command
    from vulca.tools.registry import ToolRegistry

    reg = ToolRegistry()
    reg.discover()
    p = build_tools_parser(reg)
    args = p.parse_args(["list"])
    output = run_tools_command(args, reg)

    assert "whitespace_analyze" in output
    assert "color_correct" in output


def test_cli_tools_list_category():
    """--category cultural should filter to only cultural tools."""
    from vulca.tools.adapters.cli import build_tools_parser, run_tools_command
    from vulca.tools.registry import ToolRegistry

    reg = ToolRegistry()
    reg.discover()
    p = build_tools_parser(reg)
    args = p.parse_args(["list", "--category", "cultural"])
    output = run_tools_command(args, reg)

    assert "whitespace_analyze" in output
    # color_correct is a filter tool, should NOT appear when filtering for cultural
    assert "color_correct" not in output


def test_cli_tools_run_whitespace(test_image_path, tmp_path):
    """vulca tools run whitespace_analyze should succeed and save output."""
    from vulca.tools.adapters.cli import build_tools_parser, run_tools_command
    from vulca.tools.registry import ToolRegistry

    out_path = str(tmp_path / "result.png")
    reg = ToolRegistry()
    reg.discover()
    p = build_tools_parser(reg)
    args = p.parse_args(["run", "whitespace_analyze", "--image", test_image_path, "--output", out_path])
    output = run_tools_command(args, reg)

    # Output should mention the tool name or ratio
    assert output  # non-empty
    import os
    assert os.path.exists(out_path)


def test_cli_tools_run_with_tradition(test_image_path, tmp_path):
    """--tradition flag should be passed through to the tool."""
    from vulca.tools.adapters.cli import build_tools_parser, run_tools_command
    from vulca.tools.registry import ToolRegistry

    out_path = str(tmp_path / "result.png")
    reg = ToolRegistry()
    reg.discover()
    p = build_tools_parser(reg)
    args = p.parse_args([
        "run", "whitespace_analyze",
        "--image", test_image_path,
        "--tradition", "chinese_xieyi",
        "--output", out_path,
    ])
    output = run_tools_command(args, reg)

    assert output
    # Tradition-specific text in cultural_verdict
    assert "chinese_xieyi" in output or "xieyi" in output.lower() or "ideal" in output.lower()


def test_cli_tools_run_with_mode(test_image_path, tmp_path):
    """--mode fix should invoke color_correct in fix mode."""
    from vulca.tools.adapters.cli import build_tools_parser, run_tools_command
    from vulca.tools.registry import ToolRegistry

    out_path = str(tmp_path / "result.png")
    reg = ToolRegistry()
    reg.discover()
    p = build_tools_parser(reg)
    args = p.parse_args([
        "run", "color_correct",
        "--image", test_image_path,
        "--mode", "fix",
        "--output", out_path,
    ])
    output = run_tools_command(args, reg)

    assert output
    import os
    assert os.path.exists(out_path)


# ===========================================================================
# SDK tests
# ===========================================================================


def test_sdk_whitespace_analyze(test_image_path):
    """vulca.tools.whitespace_analyze(path) should return an Output with ratio field."""
    from vulca.tools import whitespace_analyze

    result = whitespace_analyze(test_image_path)
    assert hasattr(result, "ratio")
    assert 0.0 <= result.ratio <= 1.0
    assert hasattr(result, "distribution")
    assert hasattr(result, "evidence")


def test_sdk_whitespace_analyze_with_bytes():
    """whitespace_analyze accepts raw bytes as image input."""
    from vulca.tools import whitespace_analyze

    img = Image.new("RGB", (20, 20), (220, 220, 220))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    result = whitespace_analyze(raw_bytes)
    assert hasattr(result, "ratio")
    assert 0.0 <= result.ratio <= 1.0


def test_sdk_color_correct(test_image_path):
    """vulca.tools.color_correct(path) should return channel_bias dict."""
    from vulca.tools import color_correct

    result = color_correct(test_image_path)
    assert hasattr(result, "channel_bias")
    assert "red" in result.channel_bias
    assert "green" in result.channel_bias
    assert "blue" in result.channel_bias


def test_sdk_color_correct_fix_mode(test_image_path):
    """color_correct in fix mode should produce a fixed_image bytes field."""
    from vulca.tools import color_correct

    result = color_correct(test_image_path, mode="fix")
    assert hasattr(result, "fixed_image")
    assert result.fixed_image is not None
    assert isinstance(result.fixed_image, bytes)
    assert len(result.fixed_image) > 0


def test_sdk_list_tools():
    """list_tools() should return metadata dicts for all discovered tools."""
    from vulca.tools import list_tools

    tools = list_tools()
    assert isinstance(tools, list)
    assert len(tools) >= 2
    names = [t["name"] for t in tools]
    assert "whitespace_analyze" in names
    assert "color_correct" in names
    # Each entry should have at least name, display_name, description, category
    for t in tools:
        assert "name" in t
        assert "display_name" in t
        assert "description" in t
        assert "category" in t


# ===========================================================================
# MCP tests
# ===========================================================================


def test_mcp_adapter_generates_tool_schemas():
    """generate_mcp_schema for whitespace_analyze should return proper schema dict."""
    from vulca.tools.adapters.mcp import generate_mcp_schema
    from vulca.tools.cultural.whitespace import WhitespaceAnalyzer

    schema = generate_mcp_schema(WhitespaceAnalyzer)
    assert schema["name"] == "tool_whitespace_analyze"
    assert "description" in schema
    assert "parameters" in schema
    params = schema["parameters"]
    assert "image_b64" in params
    assert "tradition" in params
    assert "mode" in params


def test_mcp_adapter_generates_color_correct_schema():
    """generate_mcp_schema for color_correct should return proper schema dict."""
    from vulca.tools.adapters.mcp import generate_mcp_schema
    from vulca.tools.filters.color_correct import ColorCorrect

    schema = generate_mcp_schema(ColorCorrect)
    assert schema["name"] == "tool_color_correct"
    assert "description" in schema
    params = schema["parameters"]
    assert "image_b64" in params


def test_mcp_adapter_execute_tool():
    """execute_mcp_tool should run whitespace_analyze from base64 input."""
    from vulca.tools.adapters.mcp import execute_mcp_tool
    from vulca.tools.registry import ToolRegistry

    reg = ToolRegistry()
    reg.discover()

    # Create a test image in base64
    img = Image.new("RGB", (20, 20), (200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    result = execute_mcp_tool(reg, "whitespace_analyze", image_b64=b64, tradition="", mode="check")
    assert isinstance(result, dict)
    assert "ratio" in result
    assert "distribution" in result
    assert "cultural_verdict" in result


def test_mcp_adapter_execute_color_correct():
    """execute_mcp_tool should run color_correct from base64 and serialize bytes fields."""
    from vulca.tools.adapters.mcp import execute_mcp_tool
    from vulca.tools.registry import ToolRegistry

    reg = ToolRegistry()
    reg.discover()

    img = Image.new("RGB", (20, 20), (200, 180, 160))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    result = execute_mcp_tool(reg, "color_correct", image_b64=b64, tradition="", mode="check")
    assert isinstance(result, dict)
    assert "channel_bias" in result
    assert "brightness" in result
    # bytes fields should be serialized to base64 strings (not raw bytes)
    if result.get("fixed_image") is not None:
        assert isinstance(result["fixed_image"], str)
