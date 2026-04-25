"""Tests for standalone prompt composition helpers."""

from __future__ import annotations

import asyncio
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"
FIXTURE_DESIGN_PATH = str(FIXTURE_DIR / "design_minimal.md")
FIXTURE_NULL_TRADITION_PATH = str(FIXTURE_DIR / "design_null_tradition.md")
FIXTURE_ARTIFACT_TOKENS_PATH = str(FIXTURE_DIR / "design_with_artifact_tokens.md")


def test_compose_prompt_from_design_fixture():
    from vulca.prompting import compose_prompt_from_design

    result = compose_prompt_from_design(FIXTURE_DESIGN_PATH)

    normalized = " ".join(result["composed_prompt"].split())
    assert "PRESERVE every existing photographic element" in normalized
    assert len(result["tradition_tokens"]) == 6
    assert result["style_treatment"] == "additive"


def test_mcp_compose_prompt_from_design_tool():
    import pytest

    pytest.importorskip("fastmcp", reason="fastmcp is an optional dependency (pip install vulca[mcp])")
    from vulca.mcp_server import compose_prompt_from_design

    result = asyncio.run(compose_prompt_from_design(FIXTURE_DESIGN_PATH))

    assert result["source_design_path"].endswith("design_minimal.md")
    assert "cinnabar red 朱砂红" in result["color_tokens"]


def test_compose_prompt_handles_null_tradition():
    """tradition: null is a valid resolved-design state — must not crash."""
    from vulca.prompting import compose_prompt_from_design

    result = compose_prompt_from_design(FIXTURE_NULL_TRADITION_PATH)

    assert result["tradition_tokens"] == []
    assert "Crisp documentary photograph" in result["composed_prompt"]
    assert "warm sunset palette" in result["color_tokens"]


def test_compose_prompt_prefers_artifact_tokens_over_registry():
    """When C.tradition_tokens is present in design.md, use it verbatim — the
    artifact is the source of truth, not the live tradition registry."""
    from vulca.prompting import compose_prompt_from_design

    result = compose_prompt_from_design(FIXTURE_ARTIFACT_TOKENS_PATH)

    assert result["tradition_tokens"] == ["FROZEN_TOKEN_A", "FROZEN_TOKEN_B"]
    assert "FROZEN_TOKEN_A" in result["composed_prompt"]
