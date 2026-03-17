"""DecideNode -- threshold-based accept/rerun/stop decision."""

from __future__ import annotations

from typing import Any

from vulca.pipeline.node import NodeContext, PipelineNode


class DecideNode(PipelineNode):
    """Decide whether to accept, rerun, or stop the pipeline.

    Decision logic:
    - ``accept`` if ``weighted_total >= accept_threshold``
    - ``rerun``  if below threshold AND ``round_num < max_rounds``
    - ``stop``   if below threshold AND max rounds reached
    """

    name = "decide"

    def __init__(self, accept_threshold: float = 0.7) -> None:
        self.accept_threshold = accept_threshold

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        weighted_total = ctx.get("weighted_total", 0.0)
        round_num = ctx.round_num
        max_rounds = ctx.max_rounds

        if weighted_total >= self.accept_threshold:
            decision = "accept"
        elif round_num < max_rounds:
            decision = "rerun"
        else:
            decision = "stop"

        return {"decision": decision}
