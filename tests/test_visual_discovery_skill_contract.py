from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".agents" / "skills" / "visual-discovery" / "SKILL.md"
ROUTER = ROOT / ".agents" / "skills" / "using-vulca-skills" / "SKILL.md"
CLAUDE_SKILL = ROOT / ".claude" / "skills" / "visual-discovery" / "SKILL.md"
CLAUDE_ROUTER = ROOT / ".claude" / "skills" / "using-vulca-skills" / "SKILL.md"


def test_visual_discovery_skill_declares_scope_and_bans():
    body = SKILL.read_text(encoding="utf-8")

    assert "name: visual-discovery" in body
    assert "direction cards" in body
    assert "taste_profile.json" in body
    assert "direction_cards.json" in body
    assert "generate_image(provider=\"mock\")" in body
    assert "generate_concepts(provider=\"mock\")" in body
    assert "real provider `generate_image` / `generate_concepts`" in body
    assert "`layers_*`" in body
    assert "`inpaint_artwork`" in body
    assert "Ready for /visual-brainstorm" in body


def test_router_mentions_visual_discovery_before_visual_brainstorm():
    body = ROUTER.read_text(encoding="utf-8")

    discovery_idx = body.index("visual-discovery")
    brainstorm_idx = body.index("visual-brainstorm")
    assert discovery_idx < brainstorm_idx
    assert "抽卡" in body
    assert "文化倾向分析" in body


def test_claude_skill_mirror_declares_visual_discovery_route():
    skill = CLAUDE_SKILL.read_text(encoding="utf-8")
    router = CLAUDE_ROUTER.read_text(encoding="utf-8")

    assert "name: visual-discovery" in skill
    assert "direction cards" in skill
    assert "real provider `generate_image` / `generate_concepts`" in skill
    assert router.index("visual-discovery") < router.index("visual-brainstorm")
