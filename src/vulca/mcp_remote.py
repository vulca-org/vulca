from __future__ import annotations

import os
from pathlib import Path

from fastmcp import FastMCP

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


def build_remote_mcp_server_summary() -> dict[str, object]:
    allowed_tools = list_remote_safe_tools()
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

    return await compose_prompt_from_design(str(safe_path))


async def _evaluate_artwork(**kwargs) -> dict:
    from vulca.mcp_server import evaluate_artwork

    return await evaluate_artwork(**kwargs)


async def _remote_evaluate_artwork(
    image_path: str,
    tradition: str = "",
    intent: str = "",
) -> dict:
    """Use this when returning Vulca's L1-L5 rubric without reading pixels or calling a VLM."""
    return await _evaluate_artwork(
        image_path=image_path,
        tradition=tradition,
        intent=intent,
        mock=True,
        mode="rubric_only",
        vlm_model="",
    )


remote_mcp = FastMCP(
    "VULCA Remote",
    instructions=(
        "Remote-safe Vulca profile for ChatGPT and OpenAI Responses MCP. "
        "Only discovery, tradition lookup, prompt composition, and mock "
        "rubric evaluation tools are exposed."
    ),
)


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


remote_mcp.tool(name="list_traditions")(_remote_list_traditions)
remote_mcp.tool(name="get_tradition_guide")(_remote_get_tradition_guide)
remote_mcp.tool(name="search_traditions")(_remote_search_traditions)
remote_mcp.tool(name="compose_prompt_from_design")(_remote_compose_prompt_from_design)
remote_mcp.tool(name="evaluate_artwork")(_remote_evaluate_artwork)


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
