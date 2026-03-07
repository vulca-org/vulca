"""Skill Registry — singleton registry for all loaded Skills.

Follows the same patterns as:
- ToolRegistry (app/prototype/agents/tool_registry.py) for registry API
- tradition_loader.py for YAML auto-discovery and lazy loading
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.prototype.skills.loader import load_skill_yaml
from app.prototype.skills.types import SkillDef

logger = logging.getLogger(__name__)

__all__ = [
    "SkillRegistry",
]

# Default skills directory (mirrors traditions dir layout)
_SKILLS_DIR = Path(__file__).resolve().parent.parent / "data" / "skills"


class SkillRegistry:
    """Registry of available Skill definitions.

    Singleton pattern — use ``SkillRegistry.get_instance()`` for the
    shared global registry. Auto-discovers YAML skills from
    ``app/prototype/data/skills/`` on first access.
    """

    _instance: SkillRegistry | None = None

    def __init__(self) -> None:
        self._skills: dict[str, SkillDef] = {}
        self._loaded: bool = False

    # ------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------

    @classmethod
    def get_instance(cls) -> SkillRegistry:
        """Return the singleton SkillRegistry, creating it if needed.

        Auto-discovers skills from the default directory on first call.
        """
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.auto_discover(_SKILLS_DIR)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton (for testing)."""
        cls._instance = None

    # ------------------------------------------------------------------
    # Registration API
    # ------------------------------------------------------------------

    def register(self, skill: SkillDef) -> None:
        """Register a skill definition (overwrites if same name exists)."""
        self._skills[skill.name] = skill
        logger.debug("Registered skill: %s", skill.name)

    def get(self, name: str) -> SkillDef | None:
        """Look up a skill by name, or None if not found."""
        return self._skills.get(name)

    def list_all(self) -> list[SkillDef]:
        """Return all registered skills."""
        return list(self._skills.values())

    def list_by_tag(self, tag: str) -> list[SkillDef]:
        """Return all skills that have the given tag."""
        return [s for s in self._skills.values() if tag in s.tags]

    # ------------------------------------------------------------------
    # YAML loading
    # ------------------------------------------------------------------

    def load_from_yaml(self, path: Path) -> SkillDef | None:
        """Load a single YAML skill definition and register it.

        Returns the SkillDef on success, None on failure.
        """
        try:
            skill = load_skill_yaml(path)
            self.register(skill)
            return skill
        except Exception as e:
            logger.error("Failed to load skill from %s: %s", path, e)
            return None

    def auto_discover(self, directory: Path | None = None) -> int:
        """Find all \\*.yaml files in a directory and load them.

        Parameters
        ----------
        directory : Path, optional
            Directory to scan. Defaults to ``data/skills/``.

        Returns
        -------
        int
            Number of skills successfully loaded.
        """
        target = directory or _SKILLS_DIR
        if not target.is_dir():
            logger.warning("Skills directory not found: %s", target)
            return 0

        count = 0
        for path in sorted(target.glob("*.yaml")):
            if path.name.startswith("_"):
                continue  # skip templates
            if self.load_from_yaml(path) is not None:
                count += 1

        self._loaded = True
        logger.info("Auto-discovered %d skills from %s", count, target)
        return count
