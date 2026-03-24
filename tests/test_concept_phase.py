"""Tests for ConceptPhase -- concept design generation."""
from __future__ import annotations

import pytest


def test_concept_build_prompt_from_brief():
    from vulca.studio.phases.concept import ConceptPhase
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, Composition

    b = Brief.new("水墨山水", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.mood = "serene"
    b.composition = Composition(layout="mountains top, water bottom")
    b.must_have = ["ink texture"]

    phase = ConceptPhase()
    prompt = phase.build_concept_prompt(b)

    assert "水墨山水" in prompt
    assert "serene" in prompt.lower() or "宁静" in prompt
    assert "mountains" in prompt.lower()
    assert "ink texture" in prompt.lower()


def test_concept_build_prompt_with_sketch():
    from vulca.studio.phases.concept import ConceptPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    b.user_sketch = "sketch.jpg"

    phase = ConceptPhase()
    prompt = phase.build_concept_prompt(b)

    assert "sketch" in prompt.lower() or "reference" in prompt.lower()


@pytest.mark.asyncio
async def test_concept_generate_mock():
    from vulca.studio.phases.concept import ConceptPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test concept")
    phase = ConceptPhase()
    paths = await phase.generate_concepts(b, count=4, provider="mock", project_dir="/tmp/vulca-test-concept")

    assert isinstance(paths, list)
    assert len(paths) == 4


def test_concept_select_updates_brief():
    from vulca.studio.phases.concept import ConceptPhase
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    b.concept_candidates = ["c1.png", "c2.png", "c3.png", "c4.png"]

    phase = ConceptPhase()
    phase.select(b, index=2, notes="mountain taller")

    assert b.selected_concept == "c3.png"
    assert b.concept_notes == "mountain taller"
