"""EvaluateNode -- L1-L5 image scoring via VLM or mock."""

from __future__ import annotations

import logging
from typing import Any

from vulca.pipeline.node import NodeContext, PipelineNode

logger = logging.getLogger("vulca")


class EvaluateNode(PipelineNode):
    """Score a generated image on L1-L5 dimensions.

    Wraps :func:`vulca._vlm.score_image` and computes a weighted total
    using the tradition's L1-L5 weights.
    """

    name = "evaluate"

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        img_b64 = ctx.get("image_b64", "")
        img_mime = ctx.get("image_mime", "image/png")

        if not img_b64:
            logger.warning("EvaluateNode: no image_b64 in context, using mock scores")
            return self._mock_scores(ctx)

        if ctx.provider == "mock" or not ctx.api_key:
            return self._mock_scores(ctx)

        return await self._vlm_scores(ctx, img_b64, img_mime)

    @staticmethod
    def _mock_scores(ctx: NodeContext) -> dict[str, Any]:
        """Return deterministic mock scores for testing."""
        base = 0.65 + (ctx.round_num * 0.05)
        scores = {
            "L1": min(1.0, base + 0.05),
            "L2": min(1.0, base),
            "L3": min(1.0, base + 0.10),
            "L4": min(1.0, base + 0.03),
            "L5": min(1.0, base + 0.08),
        }
        rationales = {f"{k}_rationale": f"Mock score for {k}" for k in scores}

        from vulca.cultural import get_weights
        weights = get_weights(ctx.tradition)
        weighted_total = sum(scores[k] * weights.get(k, 0.2) for k in scores)

        return {
            "scores": scores,
            "rationales": rationales,
            "weighted_total": round(weighted_total, 4),
        }

    @staticmethod
    async def _vlm_scores(
        ctx: NodeContext, img_b64: str, img_mime: str
    ) -> dict[str, Any]:
        """Call VLM for real L1-L5 evaluation."""
        from vulca._vlm import score_image

        data = await score_image(
            img_b64=img_b64,
            mime=img_mime,
            subject=ctx.subject or ctx.intent,
            tradition=ctx.tradition,
            api_key=ctx.api_key,
        )

        scores = {f"L{i}": data.get(f"L{i}", 0.0) for i in range(1, 6)}
        rationales = {
            f"L{i}_rationale": data.get(f"L{i}_rationale", "") for i in range(1, 6)
        }

        from vulca.cultural import get_weights
        weights = get_weights(ctx.tradition)
        weighted_total = sum(scores[k] * weights.get(k, 0.2) for k in scores)

        return {
            "scores": scores,
            "rationales": rationales,
            "weighted_total": round(weighted_total, 4),
        }
