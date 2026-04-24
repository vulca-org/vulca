"""Tests for standalone prompt composition helpers."""

from __future__ import annotations

import asyncio


def test_compose_prompt_from_design_fixture():
    from vulca.prompting import compose_prompt_from_design

    result = compose_prompt_from_design(
        "docs/visual-specs/2026-04-23-scottish-chinese-fusion/design.md"
    )

    normalized = " ".join(result["composed_prompt"].split())
    assert "PRESERVE every existing photographic element" in normalized
    assert len(result["tradition_tokens"]) == 6
    assert result["style_treatment"] == "additive"


def test_mcp_compose_prompt_from_design_tool():
    import pytest

    pytest.importorskip("fastmcp", reason="fastmcp is an optional dependency (pip install vulca[mcp])")
    from vulca.mcp_server import compose_prompt_from_design

    result = asyncio.run(
        compose_prompt_from_design(
            "docs/visual-specs/2026-04-23-scottish-chinese-fusion/design.md"
        )
    )

    assert result["source_design_path"].endswith("design.md")
    assert "cinnabar red 朱砂红" in result["color_tokens"]
