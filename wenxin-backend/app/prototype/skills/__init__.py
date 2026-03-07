"""VULCA Skill System — type definitions, YAML loader, and registry.

Usage::

    from app.prototype.skills import SkillDef, SkillResult, SkillRegistry

    # Singleton with auto-discovery
    registry = SkillRegistry.get_instance()
    print(registry.list_all())

    # Manual registration
    registry.register(SkillDef(name="my_skill", description="..."))
"""

from app.prototype.skills.skill_registry import SkillRegistry
from app.prototype.skills.types import SkillDef, SkillResult

__all__ = [
    "SkillDef",
    "SkillRegistry",
    "SkillResult",
]
