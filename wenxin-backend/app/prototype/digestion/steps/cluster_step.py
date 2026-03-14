"""Step adapter: cultural clustering via CulturalClusterer."""

from __future__ import annotations

import logging

from ..base import BaseDigester, DigestContext

logger = logging.getLogger(__name__)


class ClusterStep(BaseDigester):
    """Cluster sessions by cultural features (intra + cross tradition)."""

    STEP_NAME = "cluster_cultures"
    PRIORITY = 40

    def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
        """Run cultural clustering and store results in context."""
        try:
            from ..cultural_clusterer import CulturalClusterer

            clusterer = CulturalClusterer()
            clusters = clusterer.cluster(sessions)
            if clusters:
                ctx.clusters = clusters
                ctx.data.setdefault("feature_space", {})["clusters"] = [
                    c.to_dict() for c in clusters
                ]
                ctx.changed = True
        except Exception as exc:
            logger.debug("ClusterStep skipped: %s", exc)
        return ctx
