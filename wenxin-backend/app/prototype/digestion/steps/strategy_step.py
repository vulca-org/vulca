"""Step adapter: queen strategy evolution via ContextEvolver._evolve_queen_strategy."""

from __future__ import annotations

import logging

from ..base import BaseDigester, DigestContext

logger = logging.getLogger(__name__)


class StrategyStep(BaseDigester):
    """Evolve Queen agent accept-threshold strategy from scoring patterns."""

    STEP_NAME = "queen_strategy"
    PRIORITY = 80

    def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
        """Delegate to ContextEvolver._evolve_queen_strategy."""
        try:
            evolver = ctx.evolver
            if evolver is None:
                logger.debug("StrategyStep skipped: no evolver reference")
                return ctx
            queen_strategy = evolver._evolve_queen_strategy(ctx.data, ctx.patterns)
            if queen_strategy:
                ctx.data["queen_strategy"] = queen_strategy
                ctx.changed = True
        except Exception as exc:
            logger.debug("StrategyStep skipped: %s", exc)
        return ctx
