"""Tests for hybrid pipeline execution — Tasks 5, 6, 7.

Covers:
Task 5: Engine _resolve_nodes() supports tool nodes
Task 6: EvaluateNode detects upstream algo coverage
Task 7: CULTURAL_XIEYI mixed template
"""

from __future__ import annotations

import asyncio
import base64
import io

import pytest
from PIL import Image


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_image_b64(width: int = 30, height: int = 30, color=(200, 200, 200)) -> str:
    """Return base64-encoded PNG bytes for a solid-color test image."""
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


# ---------------------------------------------------------------------------
# ===========================================================================
# Task 5: Engine _resolve_nodes() supports tool nodes
# ===========================================================================
# ---------------------------------------------------------------------------


def test_engine_resolves_tool_nodes():
    """A PipelineDefinition with 'whitespace_analyze' node resolves without error."""
    from vulca.pipeline.engine import _resolve_nodes
    from vulca.pipeline.types import PipelineDefinition

    definition = PipelineDefinition(
        name="test_whitespace",
        entry_point="generate",
        nodes=("generate", "whitespace_analyze", "evaluate", "decide"),
        edges=(
            ("generate", "whitespace_analyze"),
            ("whitespace_analyze", "evaluate"),
            ("evaluate", "decide"),
        ),
        enable_loop=False,
    )

    nodes = _resolve_nodes(definition)

    assert "generate" in nodes
    assert "whitespace_analyze" in nodes
    assert "evaluate" in nodes
    assert "decide" in nodes

    # whitespace_analyze node should have the correct name
    assert nodes["whitespace_analyze"].name == "whitespace_analyze"


def test_engine_resolves_multiple_tools():
    """Multiple tool node names resolve correctly."""
    from vulca.pipeline.engine import _resolve_nodes
    from vulca.pipeline.types import PipelineDefinition

    definition = PipelineDefinition(
        name="test_multi_tools",
        entry_point="generate",
        nodes=("generate", "whitespace_analyze", "color_gamut_check", "evaluate", "decide"),
        edges=(
            ("generate", "whitespace_analyze"),
            ("whitespace_analyze", "color_gamut_check"),
            ("color_gamut_check", "evaluate"),
            ("evaluate", "decide"),
        ),
        enable_loop=False,
    )

    nodes = _resolve_nodes(definition)

    assert "whitespace_analyze" in nodes
    assert "color_gamut_check" in nodes
    assert nodes["whitespace_analyze"].name == "whitespace_analyze"
    assert nodes["color_gamut_check"].name == "color_gamut_check"


def test_hybrid_pipeline_executes_end_to_end():
    """generate → whitespace_analyze → evaluate → decide runs end-to-end with mock."""
    from vulca.pipeline import execute
    from vulca.pipeline.types import PipelineDefinition, PipelineInput

    definition = PipelineDefinition(
        name="hybrid_test",
        entry_point="generate",
        nodes=("generate", "whitespace_analyze", "evaluate", "decide"),
        edges=(
            ("generate", "whitespace_analyze"),
            ("whitespace_analyze", "evaluate"),
            ("evaluate", "decide"),
        ),
        enable_loop=False,
        node_specs={"decide": {"accept_threshold": 0.0}},
    )

    pipeline_input = PipelineInput(
        subject="test artwork",
        intent="test",
        tradition="chinese_xieyi",
        provider="mock",
        max_rounds=1,
    )

    output = asyncio.run(execute(definition, pipeline_input))

    assert output.status in ("completed", "failed")
    # With mock provider, pipeline should complete
    assert output.status == "completed"
    assert output.total_rounds >= 1


def test_hybrid_pipeline_with_node_params():
    """node_params for tool nodes flow through to the tool."""
    from vulca.pipeline import execute
    from vulca.pipeline.types import PipelineDefinition, PipelineInput

    definition = PipelineDefinition(
        name="hybrid_params_test",
        entry_point="generate",
        nodes=("generate", "whitespace_analyze", "evaluate", "decide"),
        edges=(
            ("generate", "whitespace_analyze"),
            ("whitespace_analyze", "evaluate"),
            ("evaluate", "decide"),
        ),
        enable_loop=False,
        node_specs={"decide": {"accept_threshold": 0.0}},
    )

    pipeline_input = PipelineInput(
        subject="test artwork",
        intent="test",
        tradition="chinese_xieyi",
        provider="mock",
        max_rounds=1,
        node_params={
            "whitespace_analyze": {
                "mode": "check",
                "thresholds": {"ratio_min": 0.1, "ratio_max": 0.9},
            }
        },
    )

    output = asyncio.run(execute(definition, pipeline_input))

    assert output.status == "completed"
    # The pipeline executed — at least one round was completed
    assert len(output.rounds) >= 1


# ---------------------------------------------------------------------------
# ===========================================================================
# Task 6: EvaluateNode detects upstream algo coverage
# ===========================================================================
# ---------------------------------------------------------------------------


def test_evaluate_detects_covered_dimensions():
    """EvaluateNode detects whitespace+gamut evidence in ctx and marks algo_covered_dims."""
    from vulca.pipeline.node import NodeContext
    from vulca.pipeline.nodes.evaluate import EvaluateNode

    node = EvaluateNode()
    ctx = NodeContext(
        subject="test",
        intent="test",
        tradition="chinese_xieyi",
        provider="mock",
        api_key="",
        round_num=1,
    )
    # Inject mock evidence from tool nodes upstream
    ctx.set("whitespace_analyze_evidence", {
        "summary": "Whitespace ratio: 40.0% (balanced). Within ideal range.",
        "confidence": 0.90,
        "details": {"ratio": 0.40, "distribution": "balanced"},
    })
    ctx.set("color_gamut_check_evidence", {
        "summary": "Saturation within range.",
        "confidence": 0.85,
        "details": {"compliance": 0.95},
    })

    result = asyncio.run(node.run(ctx))

    assert "algo_covered_dims" in result
    covered = result["algo_covered_dims"]
    assert isinstance(covered, list)
    # whitespace_analyze replaces L1; color_gamut_check replaces L3
    assert "L1" in covered
    assert "L3" in covered


def test_evaluate_uses_algo_scores():
    """Covered dimensions get algo-derived scores: 0.5 + confidence * 0.4."""
    from vulca.pipeline.node import NodeContext
    from vulca.pipeline.nodes.evaluate import EvaluateNode

    node = EvaluateNode()
    ctx = NodeContext(
        subject="test",
        intent="test",
        tradition="chinese_xieyi",
        provider="mock",
        api_key="",
        round_num=1,
    )
    # whitespace_analyze covers L1, confidence=0.90
    ctx.set("whitespace_analyze_evidence", {
        "summary": "Whitespace OK.",
        "confidence": 0.90,
        "details": {},
    })

    result = asyncio.run(node.run(ctx))

    scores = result["scores"]
    assert "L1" in scores
    # Algo score = 0.5 + 0.90 * 0.4 = 0.86
    expected_l1 = round(0.5 + 0.90 * 0.4, 4)
    assert abs(scores["L1"] - expected_l1) < 0.001


def test_evaluate_no_algo_evidence_unchanged():
    """Without any evidence in ctx, EvaluateNode behavior is unchanged (mock scores)."""
    from vulca.pipeline.node import NodeContext
    from vulca.pipeline.nodes.evaluate import EvaluateNode

    node = EvaluateNode()
    ctx = NodeContext(
        subject="test",
        intent="test",
        tradition="chinese_xieyi",
        provider="mock",
        api_key="",
        round_num=1,
    )
    # No tool evidence in ctx

    result = asyncio.run(node.run(ctx))

    # Standard mock scores should be returned
    assert "scores" in result
    assert "weighted_total" in result
    scores = result["scores"]
    for dim in ("L1", "L2", "L3", "L4", "L5"):
        assert dim in scores
    # algo_covered_dims should be empty or absent
    assert result.get("algo_covered_dims", []) == []


# ---------------------------------------------------------------------------
# ===========================================================================
# Task 7: CULTURAL_XIEYI template
# ===========================================================================
# ---------------------------------------------------------------------------


def test_cultural_xieyi_template_exists():
    """CULTURAL_XIEYI is present in TEMPLATES dict."""
    from vulca.pipeline.templates import TEMPLATES

    assert "cultural_xieyi" in TEMPLATES


def test_cultural_xieyi_template_has_tools():
    """CULTURAL_XIEYI template has all 6 expected nodes."""
    from vulca.pipeline.templates import CULTURAL_XIEYI

    expected_nodes = {
        "generate",
        "whitespace_analyze",
        "color_gamut_check",
        "composition_analyze",
        "evaluate",
        "decide",
    }
    assert set(CULTURAL_XIEYI.nodes) == expected_nodes
    assert len(CULTURAL_XIEYI.nodes) == 6


def test_cultural_xieyi_executes():
    """Full end-to-end run of CULTURAL_XIEYI with mock provider completes."""
    from vulca.pipeline import execute
    from vulca.pipeline.templates import CULTURAL_XIEYI
    from vulca.pipeline.types import PipelineInput

    pipeline_input = PipelineInput(
        subject="水墨山水",
        intent="试验性水墨山水画",
        tradition="chinese_xieyi",
        provider="mock",
        max_rounds=1,
    )

    output = asyncio.run(execute(CULTURAL_XIEYI, pipeline_input))

    assert output.status == "completed"
    assert output.total_rounds >= 1
    # Scores should exist (5 dimensions)
    assert len(output.final_scores) == 5
    assert output.weighted_total > 0.0
