"""BaseAgent — abstract base class for all graph nodes.

Every LangGraph node wraps an existing Agent via this interface.
The execute() method receives the full PipelineState and returns
a partial dict of state updates.  should_interrupt() controls
whether the graph pauses before this node for HITL input.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.prototype.graph.state import PipelineState


class BaseAgent(ABC):
    """Abstract base for all graph-aware agent nodes."""

    name: str = ""
    description: str = ""
    metadata_info: Any = None  # Optional AgentMetadata instance

    @abstractmethod
    def execute(self, state: PipelineState) -> dict[str, Any]:
        """Execute the agent and return a partial state update.

        The returned dict is merged into PipelineState by LangGraph.
        Only include keys that actually changed.
        """

    def should_interrupt(self, state: PipelineState) -> bool:
        """Whether to pause before this node for human input.

        Override in subclasses to enable per-node HITL.
        Default: no interruption.
        """
        return False
