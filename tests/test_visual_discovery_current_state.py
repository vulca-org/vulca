from __future__ import annotations

import asyncio

import pytest


def run(coro):
    return asyncio.run(coro)


EXPECTED_CORE_TOOLS = {
    "archive_session",
    "brief_parse",
    "compose_prompt_from_design",
    "create_artwork",
    "evaluate_artwork",
    "generate_concepts",
    "generate_image",
    "get_tradition_guide",
    "inpaint_artwork",
    "layers_composite",
    "layers_edit",
    "layers_evaluate",
    "layers_export",
    "layers_list",
    "layers_paste_back",
    "layers_redraw",
    "layers_split",
    "layers_transform",
    "list_traditions",
    "search_traditions",
    "sync_data",
    "unload_models",
    "view_image",
}

EXPECTED_TOOL_PROTOCOL_TOOLS = {
    "tool_brushstroke_analyze",
    "tool_color_correct",
    "tool_color_gamut_check",
    "tool_composition_analyze",
    "tool_whitespace_analyze",
}

EXPECTED_IMAGE_PROVIDERS = {
    "mock",
    "gemini",
    "nb2",
    "gemini-tools",
    "nb2-tools",
    "openai",
    "openai-responses",
    "comfyui",
}
EXPECTED_VLM_PROVIDERS = {"mock", "litellm"}
EXPECTED_TRADITIONS = {
    "african_traditional",
    "brand_design",
    "chinese_gongbi",
    "chinese_xieyi",
    "contemporary_art",
    "default",
    "islamic_geometric",
    "japanese_traditional",
    "photography",
    "south_asian",
    "ui_ux_design",
    "watercolor",
    "western_academic",
}


def test_runtime_mcp_surface_contains_current_expected_tools():
    pytest.importorskip("fastmcp", reason="fastmcp is optional; install vulca[mcp]")

    from vulca.mcp_server import mcp

    names = {tool.name for tool in run(mcp.list_tools())}

    assert EXPECTED_CORE_TOOLS <= names
    assert EXPECTED_TOOL_PROTOCOL_TOOLS <= names
    assert len(names) == len(EXPECTED_CORE_TOOLS | EXPECTED_TOOL_PROTOCOL_TOOLS)


def test_current_image_and_vlm_provider_registries():
    import vulca.providers as providers

    providers._lazy_load_providers()

    assert set(providers._IMAGE_PROVIDERS) == EXPECTED_IMAGE_PROVIDERS
    assert set(providers._VLM_PROVIDERS) == EXPECTED_VLM_PROVIDERS


def test_current_tradition_registry():
    from vulca.cultural.loader import get_all_traditions

    traditions = get_all_traditions()

    assert set(traditions) == EXPECTED_TRADITIONS
