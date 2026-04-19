"""Automated SKILL.md discovery test: file exists + valid frontmatter."""
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO / ".claude" / "skills" / "decompose"
SKILL_MD = SKILL_DIR / "SKILL.md"


def test_skill_file_exists():
    assert SKILL_MD.exists(), f"{SKILL_MD} not found"


def test_skill_frontmatter_parses():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert text.startswith("---\n"), \
        "SKILL.md must start with YAML frontmatter (---)"
    parts = text.split("---\n", 2)
    assert len(parts) >= 3, "SKILL.md frontmatter malformed (missing closing ---)"
    frontmatter = yaml.safe_load(parts[1])
    assert isinstance(frontmatter, dict), "frontmatter must parse to dict"
    assert frontmatter.get("name") == "decompose", \
        f"name must be 'decompose', got {frontmatter.get('name')}"
    desc = frontmatter.get("description", "")
    assert len(desc) >= 20, \
        f"description too short ({len(desc)} chars); needed for discoverability"


def test_skill_references_mcp_tool():
    """Skill body must explicitly reference layers_split(mode='orchestrated')."""
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "layers_split" in text, "skill must reference the MCP tool name"
    assert "orchestrated" in text, "skill must mention the orchestrated mode"


def test_skill_documents_phase_111_bans():
    """Skill must explicitly forbid the 3 agent-side plan errors (E1, E2, E3)."""
    text = SKILL_MD.read_text(encoding="utf-8")
    # E1: no per-person face entities
    assert "face_person" in text.lower() or "sibling-mask" in text.lower() or \
           "face-part" in text.lower(), \
        "skill must mention the per-person face-part ban (E1)"
    # E2: no foreground objects under background.*
    assert "background.*" in text or "foreground object" in text.lower(), \
        "skill must mention the foreground-under-background ban (E2)"
    # E3: no manual head/torso/limbs split
    assert "head/torso" in text or "body_remainder" in text, \
        "skill must mention the head/torso/limbs ban (E3)"


@pytest.mark.parametrize("label", [
    # Decision-tree branches — appear as table rows "| A | ...", etc.
    "| A |", "| B |", "| C |", "| D |", "| E |",
    "| F |", "| G |", "| H |", "| I |", "| J |",
])
def test_skill_branch_label_present(label):
    text = SKILL_MD.read_text(encoding="utf-8")
    assert label in text, (
        f"decision-tree branch {label.strip()} missing from SKILL.md — "
        "removing a branch silently is a regression"
    )


@pytest.mark.parametrize("ban", [
    "E1 —",
    "E2 —",
    "E3 —",
    "E4 —",
    "E5 —",
])
def test_skill_ban_label_present(ban):
    text = SKILL_MD.read_text(encoding="utf-8")
    assert ban in text, (
        f"ban {ban.strip()} missing from SKILL.md — each ban encodes a "
        "Phase 1.11 invariant and must not be silently removed"
    )
