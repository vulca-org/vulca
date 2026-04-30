from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AGENTS_SKILL = ROOT / ".agents" / "skills" / "evaluate" / "SKILL.md"
CLAUDE_SKILL = ROOT / ".claude" / "skills" / "evaluate" / "SKILL.md"
AGENTS_ROUTER = ROOT / ".agents" / "skills" / "using-vulca-skills" / "SKILL.md"
CLAUDE_ROUTER = ROOT / ".claude" / "skills" / "using-vulca-skills" / "SKILL.md"


def test_evaluate_skill_exists_and_wraps_existing_tool():
    body = AGENTS_SKILL.read_text(encoding="utf-8")

    assert "name: evaluate" in body
    assert "evaluate_artwork" in body
    assert "view_image" in body
    assert "get_tradition_guide" in body
    assert "L1-L5" in body
    assert "evaluation.md" in body
    assert "evaluation.json" in body


def test_evaluate_skill_bans_generation_and_layer_tools():
    body = AGENTS_SKILL.read_text(encoding="utf-8")

    assert "`generate_image`" in body
    assert "`create_artwork`" in body
    assert "`generate_concepts`" in body
    assert "`inpaint_artwork`" in body
    assert "`layers_*`" in body
    assert "must not execute pixel edits" in body.lower()


def test_router_invokes_evaluate_for_scoring_requests():
    body = AGENTS_ROUTER.read_text(encoding="utf-8")

    assert "evaluate an existing image" in body
    assert "`evaluate`" in body
    assert "L1-L5" in body
    assert "文化评分" in body


def test_claude_mirror_matches_evaluate_routing():
    skill = CLAUDE_SKILL.read_text(encoding="utf-8")
    router = CLAUDE_ROUTER.read_text(encoding="utf-8")

    assert "name: evaluate" in skill
    assert "evaluate_artwork" in skill
    assert "evaluation.md" in skill
    assert "evaluate an existing image" in router
