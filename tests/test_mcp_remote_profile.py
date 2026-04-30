from __future__ import annotations

from vulca.mcp_profiles import (
    REMOTE_DENIED_TOOLS,
    REMOTE_SAFE_TOOLS,
    get_remote_tool_policy,
    list_remote_safe_tools,
)


def test_remote_profile_exposes_only_safe_tools():
    assert list_remote_safe_tools() == [
        "compose_prompt_from_design",
        "evaluate_artwork",
        "get_tradition_guide",
        "list_traditions",
        "search_traditions",
    ]


def test_remote_profile_denies_generation_and_mutation_tools():
    unsafe = {
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
    assert unsafe <= REMOTE_DENIED_TOOLS
    assert REMOTE_SAFE_TOOLS.isdisjoint(unsafe)


def test_remote_tool_policy_requires_approval_for_image_evaluation():
    policy = get_remote_tool_policy("evaluate_artwork")

    assert policy.name == "evaluate_artwork"
    assert policy.access == "read"
    assert policy.cost == "none_by_default"
    assert policy.image_exposure == "local_or_user_supplied"
    assert policy.requires_approval is True
    assert policy.default_kwargs == {"mock": True, "mode": "rubric_only"}


def test_remote_tool_policy_requires_approval_for_design_file_reads():
    policy = get_remote_tool_policy("compose_prompt_from_design")

    assert policy.name == "compose_prompt_from_design"
    assert policy.access == "read"
    assert policy.cost == "none"
    assert policy.image_exposure == "user_supplied_design_path"
    assert policy.requires_approval is True


def test_unknown_remote_tool_policy_fails_closed():
    policy = get_remote_tool_policy("generate_image")

    assert policy.name == "generate_image"
    assert policy.allowed is False
    assert policy.requires_approval is True


from vulca.mcp_remote import build_remote_mcp_server_summary


def test_remote_mcp_summary_uses_allowlist_and_policy():
    summary = build_remote_mcp_server_summary()

    assert summary["profile"] == "chatgpt_remote_safe"
    assert summary["allowed_tools"] == list_remote_safe_tools()
    assert summary["transport_status"] == "profile_only"
    assert summary["policies"]["evaluate_artwork"]["default_kwargs"] == {
        "mock": True,
        "mode": "rubric_only",
    }
