"""Pipeline node protocol -- the building block for VULCA pipelines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NodeContext:
    """Shared mutable context passed through pipeline nodes."""

    subject: str = ""
    intent: str = ""
    tradition: str = "default"
    provider: str = "mock"
    api_key: str = ""
    round_num: int = 0
    max_rounds: int = 3
    data: dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


class PipelineNode(ABC):
    """Abstract base class for pipeline nodes.

    Every node receives a :class:`NodeContext`, performs work, and returns
    an output dict that is merged into ``ctx.data`` by the engine.
    """

    name: str

    @abstractmethod
    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        """Execute the node.

        Parameters
        ----------
        ctx:
            Shared pipeline context.

        Returns
        -------
        dict
            Output keys to merge into ``ctx.data``.
        """
