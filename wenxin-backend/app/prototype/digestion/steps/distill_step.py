"""Step adapter: prompt distillation via PromptDistiller."""

from __future__ import annotations

import logging

from ..base import BaseDigester, DigestContext

logger = logging.getLogger(__name__)


class DistillStep(BaseDigester):
    """Distill prompt archetypes from high-scoring sessions."""

    STEP_NAME = "distill_prompts"
    PRIORITY = 50

    def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
        """Run prompt distillation and store archetypes in context."""
        try:
            from ..prompt_distiller import PromptDistiller

            distiller = PromptDistiller()
            archetypes = distiller.distill(sessions)
            if archetypes:
                ctx.data.setdefault("prompt_contexts", {})["archetypes"] = [
                    a.to_dict() for a in archetypes
                ]
                ctx.changed = True
        except Exception as exc:
            logger.debug("DistillStep skipped: %s", exc)
        return ctx
