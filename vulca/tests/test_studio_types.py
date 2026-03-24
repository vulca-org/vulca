"""Tests for studio supporting data types."""
from __future__ import annotations

import pytest


def test_style_weight_defaults():
    from vulca.studio.types import StyleWeight
    sw = StyleWeight(tradition="chinese_xieyi")
    assert sw.tradition == "chinese_xieyi"
    assert sw.tag == ""
    assert sw.weight == 0.5


def test_style_weight_tag():
    from vulca.studio.types import StyleWeight
    sw = StyleWeight(tag="cyberpunk", weight=0.4)
    assert sw.tradition == ""
    assert sw.tag == "cyberpunk"
    assert sw.weight == 0.4


def test_reference_upload():
    from vulca.studio.types import Reference
    ref = Reference(path="refs/my.jpg", source="upload", note="ink ref")
    assert ref.source == "upload"
    assert ref.query == ""
    assert ref.note == "ink ref"


def test_reference_generate():
    from vulca.studio.types import Reference
    ref = Reference(path="refs/gen.png", source="generate", prompt="ink palette")
    assert ref.source == "generate"
    assert ref.prompt == "ink palette"


def test_composition_defaults():
    from vulca.studio.types import Composition
    c = Composition()
    assert c.layout == ""
    assert c.aspect_ratio == "1:1"


def test_palette_fields():
    from vulca.studio.types import Palette
    p = Palette(primary=["#1a1a2e"], accent=["#00f5d4"], mood="dark cold")
    assert len(p.primary) == 1
    assert p.mood == "dark cold"


def test_element_fields():
    from vulca.studio.types import Element
    e = Element(name="hemp-fiber stroke", category="technique")
    assert e.name == "hemp-fiber stroke"
    assert e.category == "technique"


def test_generation_round():
    from vulca.studio.types import GenerationRound
    gr = GenerationRound(round_num=1, image_path="out/r1.png", scores={"L1": 0.8})
    assert gr.round_num == 1
    assert gr.scores["L1"] == 0.8
    assert gr.feedback == ""


def test_brief_update():
    from vulca.studio.types import BriefUpdate
    bu = BriefUpdate(timestamp="2026-03-24T10:00:00", instruction="make mountain taller")
    assert bu.instruction == "make mountain taller"
    assert bu.fields_changed == []
    assert bu.rollback_to == ""


def test_all_types_serializable():
    from dataclasses import asdict
    from vulca.studio.types import (
        StyleWeight, Reference, Composition, Palette,
        Element, GenerationRound, BriefUpdate,
    )
    for cls, kwargs in [
        (StyleWeight, {"tradition": "test"}),
        (Reference, {"path": "x", "source": "upload"}),
        (Composition, {}),
        (Palette, {}),
        (Element, {"name": "test"}),
        (GenerationRound, {"round_num": 1, "image_path": "x"}),
        (BriefUpdate, {"timestamp": "t", "instruction": "i"}),
    ]:
        obj = cls(**kwargs)
        d = asdict(obj)
        assert isinstance(d, dict)
