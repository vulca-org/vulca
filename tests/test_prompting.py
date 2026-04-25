"""Tests for standalone prompt composition helpers."""

from __future__ import annotations

import asyncio
from pathlib import Path

FIXTURE_DESIGN_PATH = str(Path(__file__).parent / "fixtures" / "design_minimal.md")


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
