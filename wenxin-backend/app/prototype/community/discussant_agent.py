"""DiscussantAgent -- generates template-based discussion comments on skills.

Rotates through three sub-personas:
  - reviewer  : constructive critique
  - suggester : feature / enhancement suggestions
  - debater   : challenges scoring or methodology assumptions
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field

from app.prototype.community.base_agent import BaseAgent
from app.prototype.community.api_client import VulcaAPIClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Comment templates per persona (no LLM required)
# ---------------------------------------------------------------------------
TEMPLATES: dict[str, list[str]] = {
    "reviewer": [
        "This skill would benefit from clearer rubric boundaries between adjacent score levels.",
        "This skill would benefit from additional example outputs to clarify expected quality.",
        "This skill would benefit from explicit handling of edge-case inputs.",
        "This skill would benefit from a more granular scoring rubric.",
        "This skill would benefit from cross-cultural validation examples.",
    ],
    "suggester": [
        "Consider adding support for multi-modal inputs to broaden applicability.",
        "Consider adding a confidence calibration step before final scoring.",
        "Consider adding support for batch evaluation to improve throughput.",
        "Consider adding automated regression tests for score stability.",
        "Consider adding a fallback strategy for low-confidence predictions.",
    ],
    "debater": [
        "The scoring rubric should weight cultural context more heavily because it significantly affects interpretation.",
        "The scoring rubric should weight technical execution differently because stylistic intent varies by tradition.",
        "The scoring rubric should weight creativity higher because novelty drives artistic discourse.",
        "The evaluation criteria may over-penalize unconventional compositions that defy Western norms.",
        "The scoring rubric should account for the observer's cultural background as a confounding variable.",
    ],
}

PERSONAS = list(TEMPLATES.keys())


@dataclass
class DiscussantAgent(BaseAgent):
    """Posts template-driven comments on under-discussed skills."""

    name: str = field(default="discussant")
    client: VulcaAPIClient = field(default=None)  # type: ignore[assignment]
    _persona_index: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.client is None:
            self.client = VulcaAPIClient()

    # ------------------------------------------------------------------
    # Persona rotation
    # ------------------------------------------------------------------

    @property
    def current_persona(self) -> str:
        return PERSONAS[self._persona_index % len(PERSONAS)]

    def _rotate_persona(self) -> None:
        self._persona_index = (self._persona_index + 1) % len(PERSONAS)

    # ------------------------------------------------------------------
    # Core cycle
    # ------------------------------------------------------------------

    async def run_cycle(self) -> dict:
        """Find a skill with few discussions, post a comment, rotate persona.

        Returns
        -------
        dict
            ``{"skill_id": <str|None>, "persona": <str>, "commented": <bool>}``
        """
        skills = await self.client.get_skills()

        if not skills:
            logger.info("DiscussantAgent: no skills available")
            return {"skill_id": None, "persona": self.current_persona, "commented": False}

        # Pick the skill with the fewest existing discussions
        target = min(
            skills,
            key=lambda s: len(s.get("discussions", []) or []),
        )

        skill_id = str(target.get("id", target.get("name", "unknown")))
        persona = self.current_persona
        comment = self._generate_comment(persona, target)

        await self.client.post_discussion(skill_id, comment)

        self.log_action(
            "discuss",
            {"skill_id": skill_id, "persona": persona, "comment": comment},
        )
        logger.info(
            "DiscussantAgent [%s]: commented on skill %s", persona, skill_id,
        )

        self._rotate_persona()

        return {"skill_id": skill_id, "persona": persona, "commented": True}

    # ------------------------------------------------------------------
    # Comment generation (template-based, no LLM)
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_comment(persona: str, skill: dict) -> str:
        """Select a template comment for the given persona.

        Uses the skill name as a seed so repeated runs on the same skill
        produce varied but deterministic-ish results.
        """
        templates = TEMPLATES.get(persona, TEMPLATES["reviewer"])
        skill_name = skill.get("name", "")
        # Use skill name hash to pick a semi-deterministic template
        idx = hash(skill_name) % len(templates)
        return templates[idx]
