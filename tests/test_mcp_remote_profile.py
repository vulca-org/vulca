from __future__ import annotations

import asyncio
import os
from pathlib import Path
import subprocess
import sys

import pytest

from vulca.mcp_profiles import (
    REMOTE_DENIED_TOOLS,
    REMOTE_SAFE_TOOLS,
    get_remote_tool_policy,
    list_remote_safe_tools,
)


ROOT = Path(__file__).resolve().parent.parent


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
    assert summary["transport_status"] == "streamable_http_ready"
    assert summary["policies"]["evaluate_artwork"]["default_kwargs"] == {
        "mock": True,
        "mode": "rubric_only",
    }


def test_remote_fastmcp_server_exposes_allowlist_only():
    from vulca.mcp_remote import remote_mcp

    tools = asyncio.run(remote_mcp.list_tools())
    tool_names = sorted(tool.name for tool in tools)

    assert tool_names == list_remote_safe_tools()


def test_remote_fastmcp_tools_have_descriptions():
    from vulca.mcp_remote import remote_mcp

    tools = asyncio.run(remote_mcp.list_tools())

    assert all(tool.description for tool in tools)
    assert {
        tool.name for tool in tools if "Use this when" in (tool.description or "")
    } == set(list_remote_safe_tools())


def test_remote_mcp_listing_does_not_import_full_local_mcp_server():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import asyncio, sys; "
                "from vulca.mcp_remote import remote_mcp; "
                "asyncio.run(remote_mcp.list_tools()); "
                "print('vulca.mcp_server' in sys.modules)"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )

    assert result.stdout.strip() == "False"


def test_remote_workspace_path_requires_configured_root(tmp_path):
    from vulca.mcp_remote import RemoteMCPAccessError, resolve_remote_workspace_path

    design_path = tmp_path / "design.md"
    design_path.write_text("# Design\n", encoding="utf-8")

    with pytest.raises(RemoteMCPAccessError, match="VULCA_REMOTE_WORKSPACE_ROOT"):
        resolve_remote_workspace_path(str(design_path), workspace_root="")


def test_remote_workspace_path_blocks_escape(tmp_path):
    from vulca.mcp_remote import RemoteMCPAccessError, resolve_remote_workspace_path

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    secret = tmp_path / "secret-design.md"
    secret.write_text("# Secret\n", encoding="utf-8")

    with pytest.raises(RemoteMCPAccessError, match="outside"):
        resolve_remote_workspace_path(str(secret), workspace_root=str(workspace))


def test_remote_workspace_path_allows_relative_file_inside_root(tmp_path):
    from vulca.mcp_remote import resolve_remote_workspace_path

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    design_path = workspace / "design.md"
    design_path.write_text("# Design\n", encoding="utf-8")

    assert resolve_remote_workspace_path(
        "design.md",
        workspace_root=str(workspace),
    ) == design_path.resolve()


def test_remote_evaluate_artwork_forces_mock_rubric_only(monkeypatch):
    from vulca import mcp_remote

    captured: dict[str, object] = {}

    async def fake_evaluate_artwork(**kwargs):
        captured.update(kwargs)
        return {"ok": True}

    monkeypatch.setattr(mcp_remote, "_evaluate_artwork", fake_evaluate_artwork)

    result = asyncio.run(
        mcp_remote._remote_evaluate_artwork(
            image_path="artwork.png",
            tradition="chinese_xieyi",
            intent="misty mountain",
        )
    )

    assert result == {"ok": True}
    assert captured == {
        "image_path": "artwork.png",
        "tradition": "chinese_xieyi",
        "intent": "misty mountain",
        "mock": True,
        "mode": "rubric_only",
        "vlm_model": "",
    }


def test_pyproject_exposes_remote_mcp_console_script():
    pyproject = (ROOT / "pyproject.toml").read_text(
        encoding="utf-8"
    )

    assert 'vulca-mcp-remote = "vulca.mcp_remote:main"' in pyproject
