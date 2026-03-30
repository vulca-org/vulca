"""MCP adapter for the VULCA Tool Protocol.

Auto-registers all discovered VulcaTool subclasses as FastMCP tools on an
existing ``FastMCP`` server instance.

Each tool is exposed as ``tool_{name}`` (e.g. ``tool_whitespace_analyze``).
Images are passed as base64-encoded strings (``image_b64``); bytes fields in
the output are serialised back to base64 strings.

Usage::

    from fastmcp import FastMCP
    from vulca.tools.registry import ToolRegistry
    from vulca.tools.adapters.mcp import register_tools_on_mcp

    mcp = FastMCP("VULCA")
    reg = ToolRegistry()
    reg.discover()
    register_tools_on_mcp(mcp, reg)
"""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any, Type

if TYPE_CHECKING:
    from vulca.tools.protocol import VulcaTool
    from vulca.tools.registry import ToolRegistry


# ---------------------------------------------------------------------------
# Schema generation
# ---------------------------------------------------------------------------


def generate_mcp_schema(tool_cls: "Type[VulcaTool]") -> dict[str, Any]:
    """Return an MCP-style tool schema dict for *tool_cls*.

    Parameters
    ----------
    tool_cls:
        A concrete VulcaTool subclass.

    Returns
    -------
    dict
        Schema with keys: ``name``, ``description``, ``parameters``.
        ``parameters`` always includes ``image_b64``, ``tradition``, ``mode``.
    """
    parameters: dict[str, dict[str, Any]] = {
        "image_b64": {
            "type": "string",
            "description": "Base64-encoded PNG/JPEG image bytes.",
        },
        "tradition": {
            "type": "string",
            "description": "Cultural tradition name (optional, e.g. chinese_xieyi).",
            "default": "",
        },
        "mode": {
            "type": "string",
            "description": "Tool execution mode: 'check' (default), 'fix', or 'suggest'.",
            "enum": ["check", "fix", "suggest"],
            "default": "check",
        },
    }

    return {
        "name": f"tool_{tool_cls.name}",
        "description": tool_cls.description,
        "parameters": parameters,
    }


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def execute_mcp_tool(
    registry: "ToolRegistry",
    tool_name: str,
    image_b64: str = "",
    tradition: str = "",
    mode: str = "check",
    **kwargs: Any,
) -> dict[str, Any]:
    """Execute a registered tool from base64 image input.

    Parameters
    ----------
    registry:
        A populated ToolRegistry.
    tool_name:
        The bare tool name (e.g. ``"whitespace_analyze"``), NOT the MCP name.
    image_b64:
        Base64-encoded image bytes.
    tradition:
        Cultural tradition name.
    mode:
        Tool mode: ``"check"``, ``"fix"``, or ``"suggest"``.
    **kwargs:
        Extra ToolConfig.params entries.

    Returns
    -------
    dict
        Serialised output with bytes fields converted to base64 strings.
    """
    from vulca.tools.protocol import ToolConfig

    tool = registry.get(tool_name)

    # Decode image
    image_bytes = base64.b64decode(image_b64)

    # Build config
    config = ToolConfig(
        mode=mode,  # type: ignore[arg-type]
        params=kwargs,
    )

    # Execute
    input_data = tool.Input(image=image_bytes, tradition=tradition)
    output = tool.safe_execute(input_data, config)

    # Serialize to dict, converting bytes → base64
    raw = output.model_dump()
    return _bytes_to_b64_recursive(raw)


# ---------------------------------------------------------------------------
# FastMCP registration
# ---------------------------------------------------------------------------


def register_tools_on_mcp(mcp_server: Any, registry: "ToolRegistry") -> None:
    """Register all tools in *registry* as FastMCP tools on *mcp_server*.

    Each tool is registered under the name ``tool_{tool.name}``.

    Parameters
    ----------
    mcp_server:
        A FastMCP server instance.
    registry:
        A populated ToolRegistry (after ``discover()``).
    """
    for tool in registry.list_all():
        _register_single_tool(mcp_server, registry, tool)


def _register_single_tool(
    mcp_server: Any,
    registry: "ToolRegistry",
    tool: "VulcaTool",
) -> None:
    """Register a single tool on the MCP server as an async function."""
    tool_name = tool.name
    mcp_tool_name = f"tool_{tool_name}"
    description = tool.description

    # Build the async handler.  We capture tool_name by closure.
    async def _handler(
        image_b64: str,
        tradition: str = "",
        mode: str = "check",
    ) -> dict:
        return execute_mcp_tool(
            registry,
            tool_name,
            image_b64=image_b64,
            tradition=tradition,
            mode=mode,
        )

    _handler.__name__ = mcp_tool_name
    _handler.__qualname__ = mcp_tool_name
    _handler.__doc__ = description

    # FastMCP's @mcp.tool() decorator registers by function name; we call the
    # decorator directly with an explicit name parameter if supported, otherwise
    # fall back to just decorating the function and relying on __name__.
    try:
        mcp_server.tool(name=mcp_tool_name)(_handler)
    except TypeError:
        # Older FastMCP versions don't support name= kwarg
        mcp_server.tool()(_handler)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _bytes_to_b64_recursive(obj: Any) -> Any:
    """Recursively convert bytes values in *obj* to base64 strings."""
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode("ascii")
    if isinstance(obj, dict):
        return {k: _bytes_to_b64_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_bytes_to_b64_recursive(v) for v in obj]
    return obj
