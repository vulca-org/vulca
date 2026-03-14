"""Step adapter: detect scoring patterns via PatternDetector."""

from __future__ import annotations

import logging

from ..base import BaseDigester, DigestContext

logger = logging.getLogger(__name__)


class PatternStep(BaseDigester):
    """Detect systematic scoring patterns from aggregated session data."""

    STEP_NAME = "detect_patterns"
    PRIORITY = 10

    def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
        """Detect patterns from session history."""
        try:
            from ..aggregator import DigestAggregator
            from ..pattern_detector import PatternDetector

            aggregator = DigestAggregator(
                ctx.evolver._store if ctx.evolver else None,
            )
            detector = PatternDetector(aggregator)
            ctx.patterns = detector.detect()
            ctx.changed = True
        except Exception as exc:
            logger.debug("PatternStep skipped: %s", exc)
        return ctx
