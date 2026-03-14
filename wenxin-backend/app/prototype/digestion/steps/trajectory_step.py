"""Step adapter: trajectory-based learning via ContextEvolver._extract_trajectory_insights."""

from __future__ import annotations

import logging

from ..base import BaseDigester, DigestContext

logger = logging.getLogger(__name__)


class TrajectoryStep(BaseDigester):
    """Extract learning signals from recorded pipeline trajectories."""

    STEP_NAME = "trajectory_insights"
    PRIORITY = 70

    def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
        """Delegate to ContextEvolver._extract_trajectory_insights."""
        try:
            evolver = ctx.evolver
            if evolver is None:
                logger.debug("TrajectoryStep skipped: no evolver reference")
                return ctx
            insights = evolver._extract_trajectory_insights()
            if insights:
                ctx.data.setdefault("trajectory_insights", {}).update(insights)
                ctx.changed = True
        except Exception as exc:
            logger.debug("TrajectoryStep skipped: %s", exc)
        return ctx
