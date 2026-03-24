"""Tests for Brief dataclass and YAML serialization."""
from __future__ import annotations

import pytest
import yaml


def test_brief_create_minimal():
    from vulca.studio.brief import Brief
    b = Brief.new("水墨山水")
    assert b.intent == "水墨山水"
    assert b.session_id
    assert b.version == 1
    assert b.created_at


def test_brief_create_full():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, Element
    b = Brief.new(
        "赛博水墨",
        mood="epic",
        style_mix=[StyleWeight(tradition="chinese_xieyi", weight=0.6)],
        elements=[Element(name="neon", category="effect")],
        must_have=["ink texture"],
        must_avoid=["vector style"],
    )
    assert b.mood == "epic"
    assert len(b.style_mix) == 1
    assert b.style_mix[0].tradition == "chinese_xieyi"
    assert b.must_have == ["ink texture"]


def test_brief_to_yaml_roundtrip():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, Composition, Palette
    b = Brief.new("test intent", mood="serene")
    b.composition = Composition(layout="top mountains", focal_point="pavilion")
    b.palette = Palette(primary=["#000"], accent=["#0ff"], mood="cold")
    b.style_mix = [StyleWeight(tradition="chinese_xieyi", weight=0.7)]

    yaml_str = b.to_yaml()
    loaded = Brief.from_yaml(yaml_str)

    assert loaded.intent == "test intent"
    assert loaded.mood == "serene"
    assert loaded.composition.layout == "top mountains"
    assert loaded.palette.primary == ["#000"]
    assert loaded.style_mix[0].tradition == "chinese_xieyi"
    assert loaded.session_id == b.session_id


def test_brief_save_load_file(tmp_path):
    from vulca.studio.brief import Brief
    b = Brief.new("file test")
    filepath = b.save(tmp_path)
    assert filepath.exists()
    assert filepath.name == "brief.yaml"

    loaded = Brief.load(tmp_path)
    assert loaded.intent == "file test"
    assert loaded.session_id == b.session_id


def test_brief_update_field():
    from vulca.studio.brief import Brief
    b = Brief.new("original intent")
    b.update_field("mood", "mysterious")
    assert b.mood == "mysterious"
    assert b.updated_at
    assert len(b.updates) == 1
    assert b.updates[0].fields_changed == ["mood"]


def test_brief_update_nested():
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    b.update_field("composition.layout", "vertical split")
    assert b.composition.layout == "vertical split"


def test_brief_eval_criteria_empty_by_default():
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    assert b.eval_criteria == {}


def test_brief_version_preserved():
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    b.version = 2
    yaml_str = b.to_yaml()
    loaded = Brief.from_yaml(yaml_str)
    assert loaded.version == 2
