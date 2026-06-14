from __future__ import annotations

import os
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.apps.config import AppConfig, ResourceCSP
from fastmcp.tools import ToolResult
from fastmcp.utilities.mime import UI_MIME_TYPE

from vulca.chatgpt_prompt_studio import (
    PROMPT_STUDIO_WIDGET_URI,
    build_prompt_studio_package,
)
from vulca.chatgpt_prompt_studio_widget import PROMPT_STUDIO_WIDGET_HTML
from vulca.mcp_profiles import get_remote_tool_policy, list_remote_safe_tools


class RemoteMCPAccessError(ValueError):
    """Raised when a remote-safe MCP tool would read outside its workspace."""


def _policy_to_dict(tool_name: str) -> dict[str, object]:
    policy = get_remote_tool_policy(tool_name)
    return {
        "allowed": policy.allowed,
        "access": policy.access,
        "cost": policy.cost,
        "image_exposure": policy.image_exposure,
        "requires_approval": policy.requires_approval,
        "default_kwargs": dict(policy.default_kwargs),
    }


def is_prompt_studio_preview_enabled() -> bool:
    return os.environ.get(
        "VULCA_REMOTE_ENABLE_PROMPT_STUDIO",
        "",
    ).lower() in {"1", "true", "yes", "on"}


def _remote_tool_annotations(tool_names: list[str]) -> dict[str, dict[str, bool]]:
    return {
        tool_name: {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False,
            "idempotentHint": True,
        }
        for tool_name in tool_names
    }


def build_remote_mcp_server_summary(
    *,
    enable_prompt_studio: bool | None = None,
) -> dict[str, object]:
    if enable_prompt_studio is None:
        enable_prompt_studio = is_prompt_studio_preview_enabled()
    allowed_tools = list_remote_safe_tools(
        include_prompt_studio=enable_prompt_studio
    )
    return {
        "profile": "chatgpt_remote_safe",
        "transport_status": "streamable_http_ready",
        "allowed_tools": allowed_tools,
        "policies": {
            tool_name: _policy_to_dict(tool_name)
            for tool_name in allowed_tools
        },
    }


def resolve_remote_workspace_path(
    requested_path: str,
    *,
    workspace_root: str | os.PathLike[str] | None,
) -> Path:
    if not workspace_root:
        raise RemoteMCPAccessError(
            "VULCA_REMOTE_WORKSPACE_ROOT is required before remote file reads."
        )

    root = Path(workspace_root).expanduser().resolve()
    requested = Path(requested_path).expanduser()
    candidate = requested if requested.is_absolute() else root / requested
    resolved = candidate.resolve()

    if not resolved.is_relative_to(root):
        raise RemoteMCPAccessError(
            f"Remote path {resolved} is outside workspace root {root}."
        )
    if not resolved.exists():
        raise RemoteMCPAccessError(f"Remote path {resolved} does not exist.")
    if not resolved.is_file():
        raise RemoteMCPAccessError(f"Remote path {resolved} is not a file.")
    return resolved


async def _remote_compose_prompt_from_design(design_path: str) -> dict:
    """Use this when composing a provider-ready prompt from an approved design.md path inside the remote workspace."""
    safe_path = resolve_remote_workspace_path(
        design_path,
        workspace_root=os.environ.get("VULCA_REMOTE_WORKSPACE_ROOT", ""),
    )
    from vulca.mcp_server import compose_prompt_from_design

    result = await compose_prompt_from_design(str(safe_path))
    # The local tool returns the source path for agent debugging. The public
    # remote profile should not echo local filesystem paths back to ChatGPT.
    result.pop("source_design_path", None)
    return result


async def _evaluate_artwork(**kwargs) -> dict:
    from vulca.mcp_server import evaluate_artwork

    return await evaluate_artwork(**kwargs)


async def _remote_evaluate_artwork(
    image_path: str,
    tradition: str = "",
    intent: str = "",
) -> dict:
    """Use this when returning Vulca's L1-L5 rubric without reading pixels or calling a VLM."""
    result = await _evaluate_artwork(
        image_path=image_path,
        tradition=tradition,
        intent=intent,
        mock=True,
        mode="rubric_only",
        vlm_model="",
    )
    # Keep remote responses purpose-bound: do not echo user file paths or
    # diagnostic timing metadata in the submitted ChatGPT app profile.
    result.pop("image_path", None)
    result.pop("latency_ms", None)
    return result


async def _remote_list_traditions() -> dict:
    """Use this when selecting from Vulca's traditions before prompt or evaluation work."""
    from vulca.mcp_server import list_traditions

    return await list_traditions()


async def _remote_get_tradition_guide(tradition: str) -> dict:
    """Use this when loading detailed weights, terminology, taboos, and layer guidance for one tradition."""
    from vulca.mcp_server import get_tradition_guide

    return await get_tradition_guide(tradition=tradition)


async def _remote_search_traditions(tags: list[str], limit: int = 5) -> dict:
    """Use this when fuzzy visual or cultural keywords need to be matched to Vulca traditions."""
    from vulca.mcp_server import search_traditions

    return await search_traditions(tags=tags, limit=limit)


async def _remote_open_prompt_studio(
    final_prompt: str,
    prompt_title: str = "",
    tradition: str = "",
    negative_prompt: str = "",
    generation_notes: str = "",
    rubric_summary: str = "",
) -> ToolResult:
    """Use this when the user wants a ChatGPT-native image generation handoff from a Vulca prompt package."""
    try:
        package = build_prompt_studio_package(
            prompt_title=prompt_title,
            tradition=tradition,
            final_prompt=final_prompt,
            negative_prompt=negative_prompt,
            generation_notes=generation_notes,
            rubric_summary=rubric_summary,
        )
        content = "Opened Vulca Prompt Studio for ChatGPT-native image generation."
    except ValueError as exc:
        package = {
            "error": str(exc),
            "widget_uri": PROMPT_STUDIO_WIDGET_URI,
        }
        content = f"Vulca Prompt Studio could not open: {exc}"

    return ToolResult(
        content=content,
        structured_content=package,
        meta={"openai/outputTemplate": PROMPT_STUDIO_WIDGET_URI},
    )


def _register_prompt_studio(
    server: FastMCP,
    annotations: dict[str, dict[str, bool]],
) -> None:
    server.resource(
        PROMPT_STUDIO_WIDGET_URI,
        name="prompt_studio_widget",
        mime_type=UI_MIME_TYPE,
        app=AppConfig(
            prefersBorder=True,
            csp=ResourceCSP(connectDomains=[], resourceDomains=[]),
        ),
    )(lambda: PROMPT_STUDIO_WIDGET_HTML)

    server.tool(
        name="open_prompt_studio",
        annotations=annotations["open_prompt_studio"],
        app=AppConfig(
            resourceUri=PROMPT_STUDIO_WIDGET_URI,
            visibility=["model"],
            prefersBorder=True,
        ),
        meta={
            "openai/toolInvocation/invoking": "Opening Vulca Prompt Studio",
            "openai/toolInvocation/invoked": "Vulca Prompt Studio ready",
        },
    )(_remote_open_prompt_studio)


def build_remote_mcp_server(*, enable_prompt_studio: bool = False) -> FastMCP:
    server = FastMCP(
        "VULCA Remote",
        instructions=(
            "Remote-safe Vulca profile for ChatGPT and OpenAI Responses MCP. "
            "Only discovery, tradition lookup, prompt composition, and mock "
            "rubric evaluation tools are exposed."
        ),
    )
    tool_names = list_remote_safe_tools(
        include_prompt_studio=enable_prompt_studio
    )
    annotations = _remote_tool_annotations(tool_names)

    server.tool(
        name="list_traditions",
        annotations=annotations["list_traditions"],
    )(_remote_list_traditions)
    server.tool(
        name="get_tradition_guide",
        annotations=annotations["get_tradition_guide"],
    )(_remote_get_tradition_guide)
    server.tool(
        name="search_traditions",
        annotations=annotations["search_traditions"],
    )(_remote_search_traditions)
    server.tool(
        name="compose_prompt_from_design",
        annotations=annotations["compose_prompt_from_design"],
    )(_remote_compose_prompt_from_design)
    server.tool(
        name="evaluate_artwork",
        annotations=annotations["evaluate_artwork"],
    )(_remote_evaluate_artwork)

    if enable_prompt_studio:
        _register_prompt_studio(server, annotations)

    return server


REMOTE_APP_TOOL_ANNOTATIONS = _remote_tool_annotations(list_remote_safe_tools())
remote_mcp = build_remote_mcp_server(
    enable_prompt_studio=is_prompt_studio_preview_enabled()
)


def main() -> None:
    transport = os.environ.get("VULCA_REMOTE_MCP_TRANSPORT", "streamable-http")
    host = os.environ.get("VULCA_REMOTE_MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("VULCA_REMOTE_MCP_PORT", "8765"))
    path = os.environ.get("VULCA_REMOTE_MCP_PATH", "/mcp")

    if transport == "stdio":
        remote_mcp.run(transport="stdio")
        return

    remote_mcp.run(
        transport=transport,
        host=host,
        port=port,
        path=path,
    )


if __name__ == "__main__":
    main()
