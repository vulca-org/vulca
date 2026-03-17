"""VULCA pipeline subsystem -- slim execution engine with node protocol."""

from vulca.pipeline.engine import execute
from vulca.pipeline.node import NodeContext, PipelineNode
from vulca.pipeline.templates import CRITIQUE_ONLY, DEFAULT, FAST, TEMPLATES
from vulca.pipeline.types import (
    ConditionalEdge,
    PipelineDefinition,
    PipelineEvent,
    PipelineInput,
    PipelineOutput,
    RoundSnapshot,
    RunStatus,
)

__all__ = [
    "execute",
    "NodeContext",
    "PipelineNode",
    "DEFAULT",
    "FAST",
    "CRITIQUE_ONLY",
    "TEMPLATES",
    "ConditionalEdge",
    "PipelineDefinition",
    "PipelineEvent",
    "PipelineInput",
    "PipelineOutput",
    "RoundSnapshot",
    "RunStatus",
]
