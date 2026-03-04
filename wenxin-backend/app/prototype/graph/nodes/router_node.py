"""RouterNode — LangGraph wrapper for CulturalPipelineRouter.

Routes the cultural tradition to a pipeline variant + critic config,
storing the result in state for downstream nodes to consume.
"""

from __future__ import annotations

import logging
from typing import Any

from app.prototype.graph.base_agent import BaseAgent
from app.prototype.graph.registry import AgentRegistry

logger = logging.getLogger(__name__)


@AgentRegistry.register("router")
class RouterNode(BaseAgent):
    name = "router"
    description = "Route cultural tradition to pipeline variant and critic configuration"

    try:
        from app.prototype.graph.agent_metadata import AgentMetadata
        metadata_info = AgentMetadata(
            display_name="Cultural Router",
            supports_hitl=False,
            estimated_latency_ms=50,
            input_keys=["cultural_tradition"],
            output_keys=["pipeline_route", "critic_config"],
            tags=["routing", "configuration"],
        )
    except ImportError:
        metadata_info = None

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        from app.prototype.cultural_pipelines.pipeline_router import CulturalPipelineRouter

        tradition = state["cultural_tradition"]

        router = CulturalPipelineRouter()
        route = router.route(tradition)

        return {
            "pipeline_route": route.to_dict(),
            # Store critic config from routing (will be used by CriticNode)
            "critic_config": route.critic_config.to_dict(),
        }
