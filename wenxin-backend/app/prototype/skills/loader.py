"""YAML loader for Skill definitions.

Parses a single YAML file into a SkillDef instance, validating
required fields. Follows the same pattern as tradition_loader.py.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.prototype.skills.types import SkillDef

logger = logging.getLogger(__name__)

__all__ = [
    "load_skill_yaml",
]


def _parse_skill(data: dict[str, Any]) -> SkillDef:
    """Parse a raw YAML dict into a SkillDef."""
    return SkillDef(
        name=data["name"],
        description=data["description"],
        version=data.get("version", "1.0.0"),
        author=data.get("author", "vulca"),
        tags=data.get("tags", []),
        input_types=data.get("input_types", ["image"]),
        output_schema=data.get("output_schema", {}),
        config=data.get("config", {}),
    )


def load_skill_yaml(path: Path) -> SkillDef:
    """Load and validate a single Skill YAML file.

    Parameters
    ----------
    path : Path
        Absolute or relative path to a .yaml skill definition file.

    Returns
    -------
    SkillDef
        Parsed skill definition.

    Raises
    ------
    ValueError
        If required fields (name, description) are missing.
    FileNotFoundError
        If the YAML file does not exist.
    """
    import yaml  # noqa: F811

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Skill YAML not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Skill YAML root must be a mapping: {path}")

    # Validate required fields
    errors: list[str] = []
    if "name" not in data:
        errors.append("Missing required field: name")
    if "description" not in data:
        errors.append("Missing required field: description")
    if errors:
        raise ValueError(f"Invalid skill YAML {path.name}: {'; '.join(errors)}")

    skill = _parse_skill(data)
    logger.debug("Loaded skill: %s v%s (%d tags)", skill.name, skill.version, len(skill.tags))
    return skill
