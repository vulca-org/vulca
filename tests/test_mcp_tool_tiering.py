def test_tool_tiers_defined():
    from vulca.mcp_server import _TOOL_TIERS, _DESC_LIMITS
    assert "create_artwork" in _TOOL_TIERS
    assert _TOOL_TIERS["create_artwork"] == "core"
    assert "brief_parse" in _TOOL_TIERS
    assert _TOOL_TIERS["brief_parse"] == "core"
    assert "layers_evaluate" in _TOOL_TIERS
    assert _TOOL_TIERS["layers_evaluate"] == "advanced"
    assert all(t in ("core", "standard", "advanced") for t in _TOOL_TIERS.values())
    assert _DESC_LIMITS["core"] > _DESC_LIMITS["advanced"]


def test_tier_description_truncates():
    from vulca.mcp_server import _tier_description
    long_desc = "x" * 500
    result_core = _tier_description("create_artwork", long_desc)
    assert len(result_core) <= 300
    assert result_core.endswith("...")

    result_adv = _tier_description("layers_evaluate", long_desc)
    assert len(result_adv) <= 50
    assert result_adv.endswith("...")

    short_desc = "Short"
    assert _tier_description("create_artwork", short_desc) == short_desc


def test_unknown_tool_defaults_to_advanced():
    from vulca.mcp_server import _tier_description
    long_desc = "x" * 500
    result = _tier_description("unknown_tool", long_desc)
    assert len(result) <= 50


def test_tier_description_applied_to_adapter_registration():
    """Tool descriptions in MCP adapter must be truncated per tier limits."""
    from vulca.tools.adapters.mcp import generate_mcp_schema
    from vulca.mcp_server import _DESC_LIMITS

    # Create a fake tool class with a very long description
    from vulca.tools.protocol import VulcaTool

    class FakeTool(VulcaTool):
        name = "layers_evaluate"  # This is an "advanced" tier tool
        display_name = "Fake"
        description = "x" * 500  # Very long description
        category = "cultural"
        max_seconds = 30.0
        replaces = {}

        class Input:
            pass

        class Output:
            pass

        def execute(self, input_data, config=None):
            pass

    schema = generate_mcp_schema(FakeTool)
    desc = schema["description"]
    # After tiering, advanced tool description should be truncated to 50 chars
    assert len(desc) <= 50, (
        f"Advanced-tier tool description should be ≤50 chars but got {len(desc)}: {desc!r}"
    )


def test_auto_registered_tool_protocol_descriptions_are_tiered():
    """Tool Protocol descriptions must already be tiered during mcp_server import."""
    import asyncio

    from vulca.mcp_server import _DESC_LIMITS, mcp

    tools = asyncio.run(mcp.list_tools())
    tool_protocol_descs = [
        tool.description or "" for tool in tools if tool.name.startswith("tool_")
    ]

    assert tool_protocol_descs
    assert all(len(desc) <= _DESC_LIMITS["advanced"] for desc in tool_protocol_descs)
