from __future__ import annotations

import asyncio

from vulca.chatgpt_prompt_studio import PROMPT_STUDIO_WIDGET_URI
from vulca.mcp_remote import build_remote_mcp_server
from vulca.mcp_profiles import REMOTE_DENIED_TOOLS, REMOTE_SAFE_TOOLS


def test_prompt_studio_preview_registers_tool_with_ui_metadata():
    server = build_remote_mcp_server(enable_prompt_studio=True)

    tools = asyncio.run(server.list_tools())
    by_name = {tool.name: tool for tool in tools}

    assert "open_prompt_studio" in by_name
    tool = by_name["open_prompt_studio"]
    assert tool.annotations is not None
    assert tool.annotations.readOnlyHint is True
    assert tool.annotations.destructiveHint is False
    assert tool.annotations.openWorldHint is False
    assert tool.meta == {
        "ui": {
            "resourceUri": PROMPT_STUDIO_WIDGET_URI,
            "visibility": ["model"],
            "prefersBorder": True,
        },
        "openai/toolInvocation/invoking": "Opening Vulca Prompt Studio",
        "openai/toolInvocation/invoked": "Vulca Prompt Studio ready",
    }


def test_prompt_studio_preview_registers_widget_resource():
    server = build_remote_mcp_server(enable_prompt_studio=True)

    resources = asyncio.run(server.list_resources())
    by_uri = {str(resource.uri): resource for resource in resources}

    assert PROMPT_STUDIO_WIDGET_URI in by_uri
    resource = by_uri[PROMPT_STUDIO_WIDGET_URI]
    assert resource.mime_type == "text/html;profile=mcp-app"
    assert resource.meta == {
        "ui": {
            "csp": {"connectDomains": [], "resourceDomains": []},
            "prefersBorder": True,
        }
    }

    result = asyncio.run(server.read_resource(PROMPT_STUDIO_WIDGET_URI))
    assert result.contents[0].mime_type == "text/html;profile=mcp-app"
    assert "Generate in ChatGPT" in result.contents[0].content


def test_prompt_studio_tool_returns_structured_content_and_output_template():
    server = build_remote_mcp_server(enable_prompt_studio=True)

    result = asyncio.run(
        server.call_tool(
            "open_prompt_studio",
            {
                "prompt_title": "Ink mountain",
                "tradition": "chinese_xieyi",
                "final_prompt": "misty mountain ink study",
                "negative_prompt": "photorealistic",
                "generation_notes": "square format",
                "rubric_summary": "L5 qi resonance",
            },
        )
    )

    assert result.structured_content["final_prompt"] == "misty mountain ink study"
    assert result.structured_content["negative_prompt"] == "photorealistic"
    assert result.structured_content["followup_message"].startswith(
        "Generate an image in ChatGPT using this Vulca prompt."
    )
    assert result.meta == {"openai/outputTemplate": PROMPT_STUDIO_WIDGET_URI}


def test_prompt_studio_tool_returns_structured_error_for_empty_prompt():
    server = build_remote_mcp_server(enable_prompt_studio=True)

    result = asyncio.run(
        server.call_tool(
            "open_prompt_studio",
            {
                "prompt_title": "Ink mountain",
                "tradition": "chinese_xieyi",
                "final_prompt": " ",
            },
        )
    )

    assert result.structured_content == {
        "error": "final_prompt is required for Prompt Studio",
        "widget_uri": PROMPT_STUDIO_WIDGET_URI,
    }
    assert result.meta == {"openai/outputTemplate": PROMPT_STUDIO_WIDGET_URI}


def test_prompt_studio_preview_does_not_enable_provider_tools():
    unsafe = {
        "generate_image",
        "create_artwork",
        "generate_concepts",
        "inpaint_artwork",
        "layers_redraw",
        "view_image",
    }

    assert unsafe <= REMOTE_DENIED_TOOLS
    assert "open_prompt_studio" not in REMOTE_SAFE_TOOLS

    server = build_remote_mcp_server(enable_prompt_studio=True)
    preview_tools = {tool.name for tool in asyncio.run(server.list_tools())}

    assert unsafe.isdisjoint(preview_tools)
    assert "open_prompt_studio" in preview_tools
