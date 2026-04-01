"""DecideNode -- threshold-based accept/rerun/stop decision."""

from __future__ import annotations

import logging
import os
from typing import Any

from vulca.digestion.local_evolver import LocalEvolver
from vulca.pipeline.node import NodeContext, PipelineNode

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Evolution circuit breaker
# ---------------------------------------------------------------------------

_MAX_EVOLUTION_FAILURES = 3
_evolution_failure_count = 0


def _reset_circuit_breaker() -> None:
    """Reset the circuit breaker failure counter (intended for testing)."""
    global _evolution_failure_count
    _evolution_failure_count = 0


def _safe_load_evolved(tradition: str) -> dict | None:
    """Load evolved context for *tradition*, with a circuit breaker.

    After 3 consecutive failures the circuit opens and further calls return
    ``None`` immediately without touching the file system.
    """
    global _evolution_failure_count

    if _evolution_failure_count >= _MAX_EVOLUTION_FAILURES:
        return None

    try:
        data_dir = os.environ.get("VULCA_EVOLVED_DATA_DIR", "")
        evolver = LocalEvolver(data_dir=data_dir) if data_dir else LocalEvolver()
        return evolver.load_evolved(tradition)
    except Exception as exc:  # noqa: BLE001
        _evolution_failure_count += 1
        logger.warning(
            "Evolution load failed (%d/%d): %s",
            _evolution_failure_count,
            _MAX_EVOLUTION_FAILURES,
            exc,
        )
        return None


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
            evolved = _safe_load_evolved(ctx.tradition)
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

        # Per-layer decisions for LAYERED pipeline
        layer_results = ctx.get("layer_results")
        if layer_results:
            layer_decisions = {}
            for lr in layer_results:
                if not lr.image_path:
                    # Failed layer → must rerun
                    layer_decisions[lr.info.name] = "rerun"
                elif decision == "accept":
                    layer_decisions[lr.info.name] = "accept"
                else:
                    # Default: accept this layer
                    layer_decisions[lr.info.name] = "accept"

            # If overall decision is rerun but no specific layer targeted, rerun last non-bg layer
            if decision == "rerun" and "rerun" not in layer_decisions.values():
                candidates = [lr for lr in layer_results if lr.info.content_type != "background" and lr.image_path]
                if candidates:
                    layer_decisions[candidates[-1].info.name] = "rerun"

            result["layer_decisions"] = layer_decisions

        return result
