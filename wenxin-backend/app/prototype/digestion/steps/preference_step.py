"""Step adapter: learn user preferences via PreferenceLearner."""

from __future__ import annotations

import logging

from ..base import BaseDigester, DigestContext

logger = logging.getLogger(__name__)


class PreferenceStep(BaseDigester):
    """Learn user preferences from feedback signals."""

    STEP_NAME = "learn_preferences"
    PRIORITY = 20

    def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
        """Learn preference profiles from session feedback."""
        try:
            from ..preference_learner import PreferenceLearner

            learner = PreferenceLearner(
                ctx.evolver._store if ctx.evolver else None,
            )
            preferences = learner.learn()
            if preferences:
                ctx.data["_preferences"] = preferences
                ctx.changed = True
        except Exception as exc:
            logger.debug("PreferenceStep skipped: %s", exc)
        return ctx
