"""Step adapter: extract per-tradition layer focus via ContextEvolver._extract_layer_focus."""

from __future__ import annotations

import logging

from ..base import BaseDigester, DigestContext

logger = logging.getLogger(__name__)


class LayerFocusStep(BaseDigester):
    """Extract per-tradition, per-layer focus points from session scores."""

    STEP_NAME = "extract_layer_focus"
    PRIORITY = 30

    def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
        """Delegate to ContextEvolver._extract_layer_focus."""
        try:
            evolver = ctx.evolver
            if evolver is None:
                logger.debug("LayerFocusStep skipped: no evolver reference")
                return ctx
            layer_focus = evolver._extract_layer_focus(sessions)
            if layer_focus:
                ctx.data["layer_focus"] = layer_focus
                ctx.changed = True
        except Exception as exc:
            logger.debug("LayerFocusStep skipped: %s", exc)
        return ctx
