"""DecideNode -- threshold-based accept/rerun/stop decision."""

from __future__ import annotations

from typing import Any

from vulca.pipeline.node import NodeContext, PipelineNode

_L_LABELS = {
    "L1": "Visual Perception",
    "L2": "Technical Execution",
    "L3": "Cultural Context",
    "L4": "Critical Interpretation",
    "L5": "Philosophical Aesthetics",
}


class DecideNode(PipelineNode):
    """Decide whether to accept, rerun, or stop the pipeline.

    Decision logic:
    - ``accept`` if ``weighted_total >= accept_threshold``
    - ``rerun``  if below threshold AND ``round_num < max_rounds``
    - ``stop``   if below threshold AND max rounds reached

    On ``rerun``, outputs ``weakest_dimensions`` and ``improvement_focus``
    so that GenerateNode can construct a targeted improvement prompt.
    """

    name = "decide"

    def __init__(self, accept_threshold: float = 0.7) -> None:
        self.accept_threshold = accept_threshold

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        weighted_total = ctx.get("weighted_total", 0.0)
        scores: dict[str, float] = ctx.get("scores", {})
        rationales: dict[str, str] = ctx.get("rationales", {})
        round_num = ctx.round_num
        max_rounds = ctx.max_rounds
        eval_mode = ctx.get("eval_mode", "strict")

        # In reference mode, always accept — don't "correct" the artist
        if eval_mode == "reference":
            decision = "accept"
        elif weighted_total >= self.accept_threshold:
            decision = "accept"
        elif round_num < max_rounds:
            decision = "rerun"
        else:
            decision = "stop"

        result: dict[str, Any] = {"decision": decision}

        # On rerun: identify weakest dimensions and provide improvement guidance
        if decision == "rerun" and scores:
            sorted_dims = sorted(scores.items(), key=lambda x: x[1])
            # Take bottom 2 dimensions (or fewer if all are close)
            weakest = [d for d, s in sorted_dims[:2]]
            focus_parts = []
            for dim in weakest:
                score = scores.get(dim, 0.0)
                label = _L_LABELS.get(dim, dim)
                rationale = rationales.get(f"{dim}_rationale", "")
                part = f"{dim} ({label}): {score:.2f}"
                if rationale:
                    part += f" — {rationale}"
                focus_parts.append(part)

            result["weakest_dimensions"] = weakest
            result["improvement_focus"] = "\n".join(focus_parts)

        return result
