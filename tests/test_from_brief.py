"""Tests for Brief → TraditionConfig conversion."""
from __future__ import annotations

import pytest


def test_brief_to_tradition_single_known():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.from_brief import brief_to_tradition

    b = Brief.new("水墨山水", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    tc = brief_to_tradition(b)

    assert tc.name == "chinese_xieyi"
    assert tc.weights_l["L1"] > 0
    assert len(tc.terminology) > 0


def test_brief_to_tradition_mixed():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.from_brief import brief_to_tradition

    b = Brief.new("fusion", style_mix=[
        StyleWeight(tradition="chinese_xieyi", weight=0.6),
        StyleWeight(tradition="western_academic", weight=0.4),
    ])
    tc = brief_to_tradition(b)

    assert tc.name == "brief_fusion"
    assert abs(sum(tc.weights_l.values()) - 1.0) < 0.01


def test_brief_to_tradition_freeform_tag():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.from_brief import brief_to_tradition

    b = Brief.new("cyberpunk art", style_mix=[StyleWeight(tag="cyberpunk", weight=1.0)])
    tc = brief_to_tradition(b)

    assert tc.name == "brief_custom"
    assert abs(sum(tc.weights_l.values()) - 1.0) < 0.01
    assert len(tc.terminology) == 0


def test_brief_to_tradition_empty():
    from vulca.studio.brief import Brief
    from vulca.studio.from_brief import brief_to_tradition

    b = Brief.new("something")
    tc = brief_to_tradition(b)

    assert tc.name == "default"


def test_brief_to_tradition_with_constraints():
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.from_brief import brief_to_tradition

    b = Brief.new("test", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.must_avoid = ["vector style", "3D rendering"]
    tc = brief_to_tradition(b)

    taboo_rules = [t.rule for t in tc.taboos]
    assert any("vector style" in r for r in taboo_rules)
    assert any("3D rendering" in r for r in taboo_rules)
