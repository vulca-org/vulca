from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent


def _read_public_tree(relative: str) -> list[str]:
    root = ROOT / relative
    if not root.exists():
        return []
    return [
        path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.suffix in {".md", ".toml", ".json", ".py"}
        and ".git" not in path.parts
    ]


def _skill_files(relative: str) -> dict[str, str]:
    root = ROOT / relative
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("SKILL.md"))
    }


def _frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    if end == -1:
        return ""
    return text[4:end]


def test_stale_tool_count_claims_removed_from_public_docs():
    public_text = "\n".join(
        [
            (ROOT / "README.md").read_text(encoding="utf-8"),
            (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
            (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"),
            (ROOT / "src" / "vulca" / "mcp_server.py").read_text(
                encoding="utf-8"
            ),
        ]
        + _read_public_tree("docs/product")
        + _read_public_tree("docs/platform")
        + _read_public_tree("skills")
        + _read_public_tree("plugins/vulca")
    )

    assert "20 MCP tools" not in public_text
    assert "21 MCP tools" not in public_text
    assert "21 tools" not in public_text


def test_readme_mentions_visual_discovery_and_mock_boundary():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "/visual-discovery" in readme
    assert "mock sketch" in readme.lower()
    assert "real provider sketch" in readme.lower()


def test_readme_and_roadmap_mark_evaluate_skill_current():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "product" / "roadmap.md").read_text(
        encoding="utf-8"
    )

    assert "✅ `/evaluate`" in readme
    assert "`/evaluate`: user-facing evaluation skill" in roadmap
    assert "/evaluate` skill packaging" not in roadmap
    assert "no separate skill needed" not in readme
    assert "no agent skill yet" not in readme.lower()


def test_roadmap_marks_provider_matrix_current():
    roadmap = (ROOT / "docs" / "product" / "roadmap.md").read_text(
        encoding="utf-8"
    )
    provider_matrix = (
        ROOT / "docs" / "product" / "provider-capabilities.md"
    ).read_text(encoding="utf-8")

    assert "Vulca Provider and Platform Capability Matrix" in provider_matrix
    assert (
        "`docs/product/provider-capabilities.md`: provider/platform capability matrix"
        in roadmap
    )
    assert "Provider capability matrix for public docs" not in roadmap


def test_readme_leads_with_full_visual_workflow():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    first_screen = readme[:2500].lower()

    assert "discover" in first_screen
    assert "generate" in first_screen
    assert "edit" in first_screen
    assert "evaluate" in first_screen
    assert "one-click" in first_screen or "one shot" in first_screen


def test_public_docs_do_not_overclaim_cultural_terms():
    public_text = "\n".join(
        [
            (ROOT / "README.md").read_text(encoding="utf-8"),
            (ROOT / "docs" / "product" / "roadmap.md").read_text(
                encoding="utf-8"
            ),
            (
                ROOT
                / "docs"
                / "product"
                / "experiments"
                / "cultural-term-efficacy.md"
            ).read_text(encoding="utf-8"),
        ]
        + _read_public_tree("docs/platform")
        + _read_public_tree("skills")
        + _read_public_tree("plugins/vulca")
    ).lower()

    forbidden = [
        "culture terms guarantee",
        "cultural terms guarantee",
        "always improves generation",
        "proves cultural prompting",
    ]
    for phrase in forbidden:
        assert phrase not in public_text


def test_public_docs_do_not_overclaim_codex_public_listing():
    public_text = "\n".join(
        [
            (ROOT / "README.md").read_text(encoding="utf-8"),
            (ROOT / "docs" / "product" / "provider-capabilities.md").read_text(
                encoding="utf-8"
            ),
            (ROOT / "docs" / "product" / "roadmap.md").read_text(
                encoding="utf-8"
            ),
        ]
        + _read_public_tree("docs/platform")
        + _read_public_tree("skills")
        + _read_public_tree("plugins/vulca")
    ).lower()

    forbidden = [
        "official codex public listing is live",
        "official codex public publishing is live",
        "official codex public plugin publishing is available now",
    ]
    for phrase in forbidden:
        assert phrase not in public_text


def test_codex_plugin_package_has_installable_metadata():
    manifest = json.loads(
        (ROOT / "plugins" / "vulca" / ".codex-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    marketplace = json.loads(
        (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(
            encoding="utf-8"
        )
    )
    mcp_config = json.loads(
        (ROOT / "plugins" / "vulca" / ".mcp.json").read_text(encoding="utf-8")
    )
    root_mcp_config = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))

    assert manifest["name"] == "vulca"
    assert manifest["version"] == "0.19.0"
    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert "[TODO:" not in json.dumps(manifest)

    skill_names = {
        path.parent.name
        for path in (ROOT / "plugins" / "vulca" / "skills").glob("*/SKILL.md")
    }
    assert {
        "decompose",
        "evaluate",
        "visual-discovery",
        "visual-brainstorm",
        "visual-spec",
        "visual-plan",
        "using-vulca-skills",
    } <= skill_names

    assert marketplace["name"] == "vulca-plugins"
    plugin_entry = marketplace["plugins"][0]
    assert plugin_entry["name"] == "vulca"
    assert plugin_entry["source"] == {
        "source": "local",
        "path": "./plugins/vulca",
    }

    assert mcp_config["mcpServers"]["vulca"]["command"] == "vulca-mcp"
    assert root_mcp_config["mcpServers"]["vulca"]["command"] == "vulca-mcp"


def test_platform_skill_packages_are_synced():
    canonical = _skill_files(".agents/skills")

    assert canonical
    assert _skill_files(".claude/skills") == canonical
    assert _skill_files("skills") == canonical
    assert _skill_files("plugins/vulca/skills") == canonical


def test_skill_frontmatter_is_yaml_parseable_for_plugin_hosts():
    for relative in [
        ".agents/skills",
        ".claude/skills",
        "skills",
        "plugins/vulca/skills",
    ]:
        for path in sorted((ROOT / relative).rglob("SKILL.md")):
            metadata = yaml.safe_load(_frontmatter(path.read_text(encoding="utf-8")))
            assert isinstance(metadata, dict), path
            assert metadata.get("name"), path
            assert metadata.get("description"), path


def test_real_provider_docs_do_not_contain_live_credentials():
    experiment_doc = (
        ROOT / "docs" / "product" / "experiments" / "cultural-term-efficacy.md"
    ).read_text(encoding="utf-8")
    public_text = "\n".join(
        [
            experiment_doc,
            (
                ROOT
                / "docs"
                / "superpowers"
                / "specs"
                / "2026-04-30-cultural-term-real-provider-opt-in-design.md"
            ).read_text(encoding="utf-8"),
        ]
    )

    assert "sk-" not in public_text
    assert "global" + "ai" not in public_text.lower()
    assert "example.openai-compatible-gateway.test" in experiment_doc
