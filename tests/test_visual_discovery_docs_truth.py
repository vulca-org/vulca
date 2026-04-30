from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_stale_tool_count_claims_removed_from_public_docs():
    public_text = "\n".join(
        [
            (ROOT / "README.md").read_text(encoding="utf-8"),
            (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
            (ROOT / "src" / "vulca" / "mcp_server.py").read_text(
                encoding="utf-8"
            ),
        ]
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
    ).lower()

    forbidden = [
        "culture terms guarantee",
        "cultural terms guarantee",
        "always improves generation",
        "proves cultural prompting",
    ]
    for phrase in forbidden:
        assert phrase not in public_text
