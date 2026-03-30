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

        # Allow per-request threshold override via node_params
        node_params = ctx.get("node_params") or {}
        decide_params = node_params.get("decide") or {}
        threshold = decide_params.get("accept_threshold", self.accept_threshold)

        # Evolution micro-adjustment (only if user didn't set explicit threshold)
        if not decide_params.get("accept_threshold"):
            try:
                import os
                from vulca.digestion.local_evolver import LocalEvolver
                data_dir = os.environ.get("VULCA_EVOLVED_DATA_DIR", "")
                evolver = LocalEvolver(data_dir=data_dir) if data_dir else LocalEvolver()
                evolved = evolver.load_evolved(ctx.tradition)
                if evolved:
                    session_count = evolved.get("session_count", 0)
                    hist_avg = evolved.get("overall_avg", 0.0)

                    if session_count >= 5 and hist_avg > 0.5:
                        # Base evolution adjustment
                        evolution_adj = 0.05

                        # Mode-aware adjustment (iteration 4)
                        strict_count = evolved.get("strict_count", session_count)
                        reference_count = evolved.get("reference_count", 0)
                        total = max(strict_count + reference_count, 1)
                        strict_ratio = strict_count / total
                        mode_adj = 0.05 * (strict_ratio - 0.5)  # [-0.025, +0.025]

                        # Total adjustment capped
                        total_adj = max(-0.05, min(evolution_adj + mode_adj, 0.10))
                        adjusted = min(threshold + total_adj, hist_avg * 0.95)
                        # Only raise threshold, never lower it
                        if adjusted > threshold:
                            threshold = adjusted
                    elif hist_avg > 0.5:
                        # Few sessions: simple adjustment only, no mode awareness
                        adjusted = min(threshold + 0.05, hist_avg * 0.95)
                        if adjusted > threshold:
                            threshold = adjusted
            except Exception:
                pass  # Evolution is advisory

        # In reference mode, always accept — don't "correct" the artist
        if eval_mode == "reference":
            decision = "accept"
        elif weighted_total >= threshold:
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
