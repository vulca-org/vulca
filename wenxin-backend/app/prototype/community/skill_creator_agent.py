"""SkillCreatorAgent -- detects feedback patterns and creates new skills.

Reads feedback JSONL logs to find frequently mentioned keywords.  When a
keyword passes the occurrence threshold it generates a minimal skill YAML
definition and POSTs it to the Skill API.
"""

from __future__ import annotations

import json
import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.prototype.community.base_agent import BaseAgent
from app.prototype.community.api_client import VulcaAPIClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pattern detection configuration
# ---------------------------------------------------------------------------
# Keywords that signal a demand for a new evaluation skill
SEED_KEYWORDS: list[str] = [
    "accessibility",
    "sustainability",
    "inclusivity",
    "provenance",
    "materiality",
    "temporality",
    "interactivity",
    "narrative",
    "symbolism",
    "authenticity",
]

# Minimum keyword mentions before we consider creating a skill
CREATION_THRESHOLD = 3

# Default feedback log location (agent_logs written by BaseAgent)
_DEFAULT_FEEDBACK_DIR = Path(__file__).parent.parent / "data" / "agent_logs"


def _count_keyword_mentions(
    feedback_path: Path,
    keywords: list[str],
) -> Counter[str]:
    """Scan a JSONL file and count occurrences of each keyword in comments."""
    counts: Counter[str] = Counter()
    if not feedback_path.exists():
        return counts

    with open(feedback_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            comment = record.get("details", {}).get("comment", "")
            if not comment:
                # Also check top-level comment field
                comment = record.get("comment", "")
            if not comment:
                continue

            comment_lower = comment.lower()
            for kw in keywords:
                if kw in comment_lower:
                    counts[kw] += 1

    return counts


def _build_skill_payload(keyword: str) -> dict[str, Any]:
    """Generate a minimal skill definition dict from a keyword pattern."""
    # Normalise keyword to a clean name
    skill_name = re.sub(r"[^a-z0-9]+", "_", keyword.lower()).strip("_")
    display_name = keyword.capitalize()

    return {
        "name": f"auto_{skill_name}",
        "display_name": f"{display_name} Evaluation",
        "description": (
            f"Community-requested evaluation skill focusing on {keyword}. "
            f"Auto-generated from repeated user feedback mentioning '{keyword}'."
        ),
        "tags": ["auto-generated", "community", keyword],
        "rubric": {
            "dimensions": [
                {
                    "name": keyword,
                    "weight": 1.0,
                    "description": f"How well does the artwork address {keyword}?",
                    "levels": {
                        "1": "Not addressed",
                        "2": "Minimally addressed",
                        "3": "Adequately addressed",
                        "4": "Strongly addressed",
                        "5": "Exemplary treatment",
                    },
                }
            ]
        },
        "version": "0.1.0",
        "source": "skill_creator_agent",
    }


@dataclass
class SkillCreatorAgent(BaseAgent):
    """Monitors feedback logs and auto-creates skills when patterns emerge."""

    name: str = field(default="skill_creator")
    client: VulcaAPIClient = field(default=None)  # type: ignore[assignment]
    feedback_dir: Path = field(default=None)  # type: ignore[assignment]
    keywords: list[str] = field(default_factory=lambda: list(SEED_KEYWORDS))
    threshold: int = CREATION_THRESHOLD

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.client is None:
            self.client = VulcaAPIClient()
        if self.feedback_dir is None:
            self.feedback_dir = _DEFAULT_FEEDBACK_DIR

    async def run_cycle(self) -> dict:
        """Scan feedback, detect patterns, create a skill if warranted.

        Returns
        -------
        dict
            ``{"created": <skill_name|None>, "patterns_found": <int>}``
        """
        # Aggregate keyword counts across all feedback JSONL files
        total_counts: Counter[str] = Counter()
        if self.feedback_dir.is_dir():
            for jsonl_file in self.feedback_dir.glob("*.jsonl"):
                total_counts += _count_keyword_mentions(jsonl_file, self.keywords)

        patterns_found = sum(1 for c in total_counts.values() if c >= self.threshold)

        if patterns_found == 0:
            logger.info("SkillCreatorAgent: no patterns above threshold")
            self.log_action(
                "scan",
                {"patterns_found": 0, "counts": dict(total_counts)},
            )
            return {"created": None, "patterns_found": 0}

        # Pick the most mentioned keyword that passes threshold
        top_keyword, top_count = total_counts.most_common(1)[0]
        if top_count < self.threshold:
            self.log_action("scan", {"patterns_found": 0, "counts": dict(total_counts)})
            return {"created": None, "patterns_found": 0}

        payload = _build_skill_payload(top_keyword)
        skill_name = payload["name"]

        try:
            await self.client.create_skill(payload)
            logger.info(
                "SkillCreatorAgent: created skill '%s' from keyword '%s' (%d mentions)",
                skill_name,
                top_keyword,
                top_count,
            )
            self.log_action(
                "create_skill",
                {
                    "skill_name": skill_name,
                    "keyword": top_keyword,
                    "mentions": top_count,
                    "patterns_found": patterns_found,
                },
            )
            return {"created": skill_name, "patterns_found": patterns_found}
        except Exception as exc:
            logger.error("SkillCreatorAgent: failed to create skill: %s", exc)
            self.log_action(
                "create_skill_error",
                {"skill_name": skill_name, "error": str(exc)},
            )
            return {"created": None, "patterns_found": patterns_found}
