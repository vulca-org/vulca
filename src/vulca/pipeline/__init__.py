"""VULCA pipeline subsystem -- slim execution engine with node protocol."""

from vulca.pipeline.engine import execute, execute_stream
from vulca.pipeline.hooks import default_on_complete
from vulca.pipeline.node import NodeContext, PipelineNode
from vulca.pipeline.parallel import explore_parallel, rank_results
from vulca.pipeline.residuals import AgentResiduals, NodeSnapshot, ResidualWeights
from vulca.pipeline.templates import CRITIQUE_ONLY, DEFAULT, FAST, TEMPLATES
from vulca.pipeline.types import (
    PipelineDefinition,
    PipelineEvent,
    PipelineInput,
    PipelineOutput,
    RoundSnapshot,
    RunStatus,
)

__all__ = [
    "execute",
    "execute_stream",
    "default_on_complete",
    "NodeContext",
    "PipelineNode",
    "explore_parallel",
    "rank_results",
    "AgentResiduals",
    "NodeSnapshot",
    "ResidualWeights",
    "DEFAULT",
    "FAST",
    "CRITIQUE_ONLY",
    "TEMPLATES",
    "PipelineDefinition",
    "PipelineEvent",
    "PipelineInput",
    "PipelineOutput",
    "RoundSnapshot",
    "RunStatus",
]
