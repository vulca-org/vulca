"""CuratorAgent -- curates a "featured" list of high-quality community skills.

Quality criteria evaluated per skill:
  1. Description longer than 20 characters
  2. At least 1 tag
  3. Positive vote ratio > 0.5
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.prototype.community.base_agent import BaseAgent
from app.prototype.community.api_client import VulcaAPIClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Quality thresholds
# ---------------------------------------------------------------------------
MIN_DESCRIPTION_LENGTH = 20
MIN_TAGS = 1
MIN_VOTE_RATIO = 0.5


def _vote_ratio(skill: dict) -> float:
    """Compute upvote ratio from a skill dict, defaulting to 0.0."""
    up = skill.get("upvotes", 0) or 0
    down = skill.get("downvotes", 0) or 0
    total = up + down
    if total == 0:
        return 0.0
    return up / total


def _passes_quality(skill: dict) -> bool:
    """Return True if a skill passes all curation quality checks."""
    description = skill.get("description", "") or ""
    if len(description) <= MIN_DESCRIPTION_LENGTH:
        return False

    tags = skill.get("tags") or []
    if len(tags) < MIN_TAGS:
        return False

    if _vote_ratio(skill) <= MIN_VOTE_RATIO:
        return False

    return True


@dataclass
class CuratorAgent(BaseAgent):
    """Periodically reviews community skills and selects featured ones."""

    name: str = field(default="curator")
    client: VulcaAPIClient = field(default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.client is None:
            self.client = VulcaAPIClient()

    async def run_cycle(self) -> dict:
        """Fetch all skills, evaluate quality, return featured list.

        Returns
        -------
        dict
            ``{"featured": [<skill_id>, ...], "reviewed": <int>}``
        """
        skills = await self.client.get_skills()
        reviewed = len(skills)

        featured: list[str] = []
        for skill in skills:
            if _passes_quality(skill):
                skill_id = skill.get("id", skill.get("name", "unknown"))
                featured.append(str(skill_id))

        # Sort by vote ratio descending so best skills come first
        featured_skills = [s for s in skills if str(s.get("id", s.get("name", "unknown"))) in featured]
        featured_skills.sort(key=_vote_ratio, reverse=True)
        featured = [str(s.get("id", s.get("name", "unknown"))) for s in featured_skills]

        self.log_action(
            "curate",
            {"reviewed": reviewed, "featured_count": len(featured), "featured_ids": featured},
        )

        logger.info("CuratorAgent: reviewed %d skills, featured %d", reviewed, len(featured))
        return {"featured": featured, "reviewed": reviewed}
