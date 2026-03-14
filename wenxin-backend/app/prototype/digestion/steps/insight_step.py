"""Step adapter: LLM-powered insights via ContextEvolver._generate_llm_insights."""

from __future__ import annotations

import logging

from ..base import BaseDigester, DigestContext

logger = logging.getLogger(__name__)


class InsightStep(BaseDigester):
    """Generate agent and tradition insights via LLM (MemRL evolving context)."""

    STEP_NAME = "llm_insights"
    PRIORITY = 90

    def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
        """Delegate to ContextEvolver._generate_llm_insights."""
        try:
            evolver = ctx.evolver
            if evolver is None:
                logger.debug("InsightStep skipped: no evolver reference")
                return ctx
            insights = evolver._generate_llm_insights(
                ctx.data, ctx.patterns, ctx.actions, sessions,
            )
            if insights:
                if insights.get("agent_insights"):
                    ctx.data["agent_insights"] = insights["agent_insights"]
                if insights.get("tradition_insights"):
                    ctx.data["tradition_insights"] = insights["tradition_insights"]
                ctx.changed = True
        except Exception as exc:
            logger.debug("InsightStep skipped: %s", exc)
        return ctx
