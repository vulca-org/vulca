"""Step adapter: concept crystallization via ConceptCrystallizer."""

from __future__ import annotations

import logging

from ..base import BaseDigester, DigestContext

logger = logging.getLogger(__name__)


class CrystallizeStep(BaseDigester):
    """Crystallize cultural concepts from large-enough clusters."""

    STEP_NAME = "crystallize_concepts"
    PRIORITY = 60

    def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
        """Run concept crystallization using clusters from ClusterStep."""
        try:
            from ..concept_crystallizer import ConceptCrystallizer

            crystallizer = ConceptCrystallizer()
            concepts = crystallizer.crystallize(ctx.clusters, sessions)
            if concepts:
                for concept in concepts:
                    ctx.data.setdefault("cultures", {})[concept.name] = concept.to_dict()
                ctx.changed = True
        except Exception as exc:
            logger.debug("CrystallizeStep skipped: %s", exc)
        return ctx
