from __future__ import annotations

from vulca.mcp_profiles import get_remote_tool_policy, list_remote_safe_tools


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
        "transport_status": "profile_only",
        "allowed_tools": allowed_tools,
        "policies": {
            tool_name: _policy_to_dict(tool_name)
            for tool_name in allowed_tools
        },
    }
