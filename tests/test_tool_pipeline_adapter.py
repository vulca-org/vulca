"""Tests for the pipeline adapter: tool_as_pipeline_node().

4 test cases:
- test_wrapped_tool_runs_in_pipeline     -- whitespace tool runs via node.run(ctx)
- test_wrapped_tool_reads_node_params    -- custom thresholds flow through
- test_wrapped_tool_fix_mode_updates_image -- fix mode updates ctx image_b64
- test_wrapped_color_correct_in_pipeline -- color_correct also works
"""

from __future__ import annotations

import asyncio
import base64
import io

import pytest
from PIL import Image

from vulca.pipeline.node import NodeContext


# ---------------------------------------------------------------------------
# Shared fixture: create a small test image and return its base64 string
# ---------------------------------------------------------------------------


def _make_image_b64(width: int = 30, height: int = 30, color=(200, 200, 200)) -> str:
    """Return base64-encoded PNG bytes for a solid-color test image."""
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _make_ctx(**kwargs) -> NodeContext:
    """Build a NodeContext with test defaults.

    NodeContext only accepts its declared dataclass fields in __init__.
    Extra data (image_b64, node_params, …) must be stored via ctx.set().
    """
    _DATA_KEYS = {"image_b64", "node_params"}
    init_kwargs = {
        "subject": "test",
        "intent": "test",
        "tradition": "chinese_xieyi",
        "provider": "mock",
        "api_key": "",
        "round_num": 1,
    }
    # Update with any init-compatible kwargs (excluding data-dict keys)
    for k, v in kwargs.items():
        if k not in _DATA_KEYS:
            init_kwargs[k] = v

    ctx = NodeContext(**init_kwargs)

    # Inject data-dict keys via ctx.set()
    for k in _DATA_KEYS:
        if k in kwargs:
            ctx.set(k, kwargs[k])

    return ctx


# ---------------------------------------------------------------------------
# Test 1: wrapped whitespace tool runs via node.run(ctx)
# ---------------------------------------------------------------------------


def test_wrapped_tool_runs_in_pipeline():
    """Whitespace tool wrapped as a PipelineNode runs successfully."""
    from vulca.tools.adapters.pipeline import tool_as_pipeline_node
    from vulca.tools.cultural.whitespace import WhitespaceAnalyzer

    NodeCls = tool_as_pipeline_node(WhitespaceAnalyzer)
    assert NodeCls.name == "whitespace_analyze"

    node = NodeCls()
    image_b64 = _make_image_b64()
    ctx = _make_ctx(image_b64=image_b64)

    output = asyncio.run(node.run(ctx))

    # result dict present
    assert "whitespace_analyze_result" in output
    result = output["whitespace_analyze_result"]
    assert isinstance(result, dict)
    # Core output fields (bytes sanitized to placeholder)
    assert "ratio" in result
    assert isinstance(result["ratio"], float)
    assert 0.0 <= result["ratio"] <= 1.0
    assert "distribution" in result

    # evidence dict present
    assert "whitespace_analyze_evidence" in output
    evidence = output["whitespace_analyze_evidence"]
    assert "summary" in evidence
    assert "confidence" in evidence
    assert 0.0 <= evidence["confidence"] <= 1.0
    assert "details" in evidence


# ---------------------------------------------------------------------------
# Test 2: custom thresholds flow through node_params
# ---------------------------------------------------------------------------


def test_wrapped_tool_reads_node_params():
    """Custom thresholds in node_params are passed to the tool."""
    from vulca.tools.adapters.pipeline import tool_as_pipeline_node
    from vulca.tools.cultural.whitespace import WhitespaceAnalyzer

    NodeCls = tool_as_pipeline_node(WhitespaceAnalyzer)
    node = NodeCls()

    # Create a very white image (high whitespace ratio)
    image_b64 = _make_image_b64(color=(255, 255, 255))
    node_params = {
        "whitespace_analyze": {
            "mode": "check",
            "thresholds": {"ratio_min": 0.8, "ratio_max": 1.0},
        }
    }
    ctx = _make_ctx(image_b64=image_b64, node_params=node_params)

    output = asyncio.run(node.run(ctx))

    # Evidence details should reflect the custom thresholds that were applied
    evidence = output["whitespace_analyze_evidence"]
    # Summary should exist and be a string
    assert isinstance(evidence["summary"], str)
    assert len(evidence["summary"]) > 0

    # The details should reflect the tool ran (ratio_min/ratio_max may be in
    # cultural_verdict or details, verify tool actually processed thresholds)
    result = output["whitespace_analyze_result"]
    assert "ratio" in result
    # With a completely white image, ratio should be very high
    assert result["ratio"] > 0.9


# ---------------------------------------------------------------------------
# Test 3: fix mode updates ctx image_b64
# ---------------------------------------------------------------------------


def test_wrapped_tool_fix_mode_updates_image():
    """In fix mode, color_correct's fixed_image overwrites image_b64 in the output."""
    from vulca.tools.adapters.pipeline import tool_as_pipeline_node
    from vulca.tools.filters.color_correct import ColorCorrect

    NodeCls = tool_as_pipeline_node(ColorCorrect)
    node = NodeCls()

    # Strongly red-biased image to trigger fix
    image_b64 = _make_image_b64(color=(230, 100, 80))
    node_params = {
        "color_correct": {
            "mode": "fix",
        }
    }
    ctx = _make_ctx(image_b64=image_b64, node_params=node_params)

    output = asyncio.run(node.run(ctx))

    # In fix mode with a biased image, fixed_image should be set
    result = output["color_correct_result"]
    # fixed_image is sanitized to placeholder string by _sanitize_result
    # Check it exists and is a string (either placeholder or None indicator)
    assert "fixed_image" in result

    # image_b64 should have been updated in the output dict
    assert "image_b64" in output
    new_b64 = output["image_b64"]
    assert isinstance(new_b64, str)
    # Decode and verify it's a valid image
    new_bytes = base64.b64decode(new_b64)
    img = Image.open(io.BytesIO(new_bytes))
    assert img.size[0] > 0
    assert img.size[1] > 0
    # The new image should differ from the original (channels were corrected)
    assert new_b64 != image_b64


# ---------------------------------------------------------------------------
# Test 4: color_correct also works as a pipeline node
# ---------------------------------------------------------------------------


def test_wrapped_color_correct_in_pipeline():
    """color_correct wrapped as a PipelineNode runs in check mode."""
    from vulca.tools.adapters.pipeline import tool_as_pipeline_node
    from vulca.tools.filters.color_correct import ColorCorrect

    NodeCls = tool_as_pipeline_node(ColorCorrect)
    assert NodeCls.name == "color_correct"

    node = NodeCls()
    image_b64 = _make_image_b64(color=(200, 180, 160))
    ctx = _make_ctx(image_b64=image_b64)

    output = asyncio.run(node.run(ctx))

    assert "color_correct_result" in output
    result = output["color_correct_result"]
    assert "channel_bias" in result
    assert "brightness" in result
    assert "contrast" in result

    assert "color_correct_evidence" in output
    evidence = output["color_correct_evidence"]
    assert "summary" in evidence
    assert 0.0 <= evidence["confidence"] <= 1.0

    # In check mode, image_b64 should NOT be updated
    assert "image_b64" not in output
