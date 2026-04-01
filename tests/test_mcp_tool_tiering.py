def test_tool_tiers_defined():
    from vulca.mcp_server import _TOOL_TIERS, _DESC_LIMITS
    assert "create_artwork" in _TOOL_TIERS
    assert _TOOL_TIERS["create_artwork"] == "core"
    assert "layers_regenerate" in _TOOL_TIERS
    assert _TOOL_TIERS["layers_regenerate"] == "advanced"
    assert all(t in ("core", "standard", "advanced") for t in _TOOL_TIERS.values())
    assert _DESC_LIMITS["core"] > _DESC_LIMITS["advanced"]


def test_tier_description_truncates():
    from vulca.mcp_server import _tier_description
    long_desc = "x" * 500
    result_core = _tier_description("create_artwork", long_desc)
    assert len(result_core) <= 300
    assert result_core.endswith("...")

    result_adv = _tier_description("layers_regenerate", long_desc)
    assert len(result_adv) <= 50
    assert result_adv.endswith("...")

    short_desc = "Short"
    assert _tier_description("create_artwork", short_desc) == short_desc


def test_unknown_tool_defaults_to_advanced():
    from vulca.mcp_server import _tier_description
    long_desc = "x" * 500
    result = _tier_description("unknown_tool", long_desc)
    assert len(result) <= 50
