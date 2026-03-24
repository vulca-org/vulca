"""Tests for GeneratePhase -- Brief-driven image generation."""
from __future__ import annotations

import pytest


def test_generate_build_prompt():
    from vulca.studio.phases.generate import GeneratePhase
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, Composition, Palette, Element

    b = Brief.new("水墨山水", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.composition = Composition(layout="mountains top, water bottom", focal_point="pavilion")
    b.palette = Palette(primary=["#1a1a2e"], accent=["#00f5d4"], mood="cold dark")
    b.elements = [Element(name="hemp-fiber stroke", category="technique")]
    b.must_have = ["ink texture", "negative space"]
    b.must_avoid = ["vector style"]

    phase = GeneratePhase()
    prompt = phase.build_prompt(b)

    assert "水墨山水" in prompt
    assert "mountains" in prompt.lower()
    assert "#1a1a2e" in prompt
    assert "hemp-fiber stroke" in prompt.lower()
    assert "ink texture" in prompt.lower()
    assert "vector style" in prompt.lower()


def test_generate_prompt_uses_concept_reference():
    from vulca.studio.phases.generate import GeneratePhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    b.selected_concept = "concepts/c3.png"

    phase = GeneratePhase()
    prompt = phase.build_prompt(b)

    assert "concept" in prompt.lower() or "reference" in prompt.lower()


@pytest.mark.asyncio
async def test_generate_with_mock_provider():
    from vulca.studio.phases.generate import GeneratePhase
    from vulca.studio.brief import Brief

    b = Brief.new("test generation")
    phase = GeneratePhase()
    result_path = await phase.generate(b, provider="mock", project_dir="/tmp/vulca-test-gen")

    assert result_path
    from pathlib import Path
    assert Path(result_path).exists()


def test_generate_records_round_in_brief():
    """After generation, brief.generations should have a new entry."""
    import asyncio
    from vulca.studio.phases.generate import GeneratePhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    phase = GeneratePhase()

    loop = asyncio.new_event_loop()
    path = loop.run_until_complete(phase.generate(b, provider="mock", project_dir="/tmp/vulca-test-gen-round"))
    loop.close()

    assert len(b.generations) == 1
    assert b.generations[0].round_num == 1
    assert b.generations[0].image_path == path
