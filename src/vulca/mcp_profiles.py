from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


REMOTE_SAFE_TOOLS = frozenset(
    {
        "list_traditions",
        "get_tradition_guide",
        "search_traditions",
        "compose_prompt_from_design",
        "evaluate_artwork",
    }
)

REMOTE_DENIED_TOOLS = frozenset(
    {
        "generate_image",
        "create_artwork",
        "generate_concepts",
        "inpaint_artwork",
        "layers_split",
        "layers_list",
        "layers_edit",
        "layers_transform",
        "layers_redraw",
        "layers_composite",
        "layers_evaluate",
        "layers_export",
        "layers_paste_back",
        "view_image",
        "brief_parse",
        "tool_brushstroke_analyze",
        "tool_color_correct",
        "tool_color_gamut_check",
        "tool_composition_analyze",
        "tool_whitespace_analyze",
        "sync_data",
        "archive_session",
        "unload_models",
    }
)


@dataclass(frozen=True)
class RemoteToolPolicy:
    name: str
    allowed: bool
    access: str = "read"
    cost: str = "none"
    image_exposure: str = "none"
    requires_approval: bool = False
    default_kwargs: Mapping[str, object] = field(default_factory=dict)


_POLICIES = {
    "list_traditions": RemoteToolPolicy(
        name="list_traditions",
        allowed=True,
    ),
    "get_tradition_guide": RemoteToolPolicy(
        name="get_tradition_guide",
        allowed=True,
    ),
    "search_traditions": RemoteToolPolicy(
        name="search_traditions",
        allowed=True,
    ),
    "compose_prompt_from_design": RemoteToolPolicy(
        name="compose_prompt_from_design",
        allowed=True,
        image_exposure="user_supplied_design_path",
        requires_approval=True,
    ),
    "evaluate_artwork": RemoteToolPolicy(
        name="evaluate_artwork",
        allowed=True,
        cost="none_by_default",
        image_exposure="local_or_user_supplied",
        requires_approval=True,
        default_kwargs=MappingProxyType({"mock": True, "mode": "rubric_only"}),
    ),
}


def list_remote_safe_tools() -> list[str]:
    return sorted(REMOTE_SAFE_TOOLS)


def get_remote_tool_policy(tool_name: str) -> RemoteToolPolicy:
    policy = _POLICIES.get(tool_name)
    if policy is not None:
        return policy
    return RemoteToolPolicy(
        name=tool_name,
        allowed=False,
        requires_approval=True,
    )
