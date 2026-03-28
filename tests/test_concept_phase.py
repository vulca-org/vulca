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


class TestConceptPhaseReference:
    def test_build_prompt_without_reference(self):
        from vulca.studio.phases.concept import ConceptPhase
        from vulca.studio.brief import Brief

        b = Brief.new("test artwork")
        phase = ConceptPhase()
        prompt = phase.build_concept_prompt(b)
        assert "variation of the reference" not in prompt.lower()
        assert "rework" not in prompt.lower()

    def test_build_prompt_with_medium_strength(self):
        from vulca.studio.phases.concept import ConceptPhase
        from vulca.studio.brief import Brief

        b = Brief.new("test artwork")
        phase = ConceptPhase()
        prompt = phase.build_concept_prompt(b, variation_strength=0.4)
        assert "variation" in prompt.lower()

    def test_build_prompt_high_strength(self):
        from vulca.studio.phases.concept import ConceptPhase
        from vulca.studio.brief import Brief

        b = Brief.new("test artwork")
        phase = ConceptPhase()
        prompt = phase.build_concept_prompt(b, variation_strength=0.7)
        assert "significant" in prompt.lower() or "rework" in prompt.lower()

    def test_build_prompt_low_strength(self):
        from vulca.studio.phases.concept import ConceptPhase
        from vulca.studio.brief import Brief

        b = Brief.new("test artwork")
        phase = ConceptPhase()
        prompt = phase.build_concept_prompt(b, variation_strength=0.2)
        assert "subtle" in prompt.lower() or "minor" in prompt.lower() or "refine" in prompt.lower()

    def test_generate_concepts_accepts_reference_image(self):
        import asyncio
        import tempfile
        from vulca.studio.phases.concept import ConceptPhase
        from vulca.studio.brief import Brief

        b = Brief.new("test")
        phase = ConceptPhase()
        with tempfile.TemporaryDirectory() as td:
            loop = asyncio.new_event_loop()
            try:
                paths = loop.run_until_complete(
                    phase.generate_concepts(
                        b, count=1, provider="mock", project_dir=td,
                        reference_image="/tmp/nonexistent.jpg",
                    )
                )
            finally:
                loop.close()
            assert len(paths) == 1
