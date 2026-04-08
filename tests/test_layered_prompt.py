from vulca.layers.types import LayerInfo
from vulca.layers.layered_prompt import build_anchored_layer_prompt, TraditionAnchor


def _xieyi_anchor():
    return TraditionAnchor(
        canvas_color_hex="#ffffff",
        canvas_description="pure white rice paper (生宣纸), no texture, no border",
        style_keywords="水墨写意, 淡墨为主, 飞白笔触",
    )


def _layer(name, role, position="upper 30%", coverage="20-30%"):
    return LayerInfo(
        name=name,
        description=f"{role} description",
        z_index=1,
        tradition_role=role,
        regeneration_prompt=f"painted {role}",
    )


def test_prompt_contains_canvas_anchor():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=["中景山石", "题款"],
    )
    assert "pure white rice paper" in p
    assert "#ffffff" in p


def test_prompt_contains_negative_list_from_siblings():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=["中景山石", "题款"],
    )
    assert "中景山石" in p
    assert "题款" in p
    assert ("Do NOT" in p) or ("do not" in p.lower())


def test_prompt_does_not_negate_self():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=["远景淡墨", "中景山石"],  # self should be filtered
    )
    # In the CONTENT ANCHOR block, own role appears only in the positive mention
    content_section = p.split("[CONTENT ANCHOR")[1] if "[CONTENT ANCHOR" in p else p
    assert content_section.count("远景淡墨") <= 1


def test_prompt_includes_style_keywords():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=[],
    )
    assert "飞白" in p or "水墨" in p


def test_prompt_has_spatial_anchor():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=[],
        position="upper 30%",
        coverage="20-30%",
    )
    assert "upper 30%" in p
    assert "20-30%" in p


def test_prompt_passthrough_user_intent():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=[],
    )
    assert "painted 远景淡墨" in p
