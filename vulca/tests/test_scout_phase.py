"""Tests for ScoutPhase -- reference image generation."""
from __future__ import annotations

import pytest


def test_scout_extract_search_terms():
    from vulca.studio.phases.scout import ScoutPhase
    from vulca.studio.brief import Brief

    b = Brief.new("赛博朋克风格的水墨山水画")
    phase = ScoutPhase()
    terms = phase.extract_search_terms(b)

    assert isinstance(terms, list)
    assert len(terms) >= 1


def test_scout_build_reference_prompts():
    from vulca.studio.phases.scout import ScoutPhase
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight

    b = Brief.new("ink mountain", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.mood = "serene"
    phase = ScoutPhase()
    prompts = phase.build_reference_prompts(b)

    assert isinstance(prompts, list)
    assert len(prompts) >= 1
    for p in prompts:
        assert len(p) > 10


@pytest.mark.asyncio
async def test_scout_generate_references_mock():
    from vulca.studio.phases.scout import ScoutPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test art")
    phase = ScoutPhase()
    refs = await phase.generate_references(b, provider="mock", project_dir="/tmp/vulca-test-scout")

    assert isinstance(refs, list)
    for ref in refs:
        assert ref.source == "generate"
