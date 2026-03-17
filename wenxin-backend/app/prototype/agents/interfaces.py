"""Canonical agent interfaces for extending the VULCA pipeline.

This module re-exports the core ``BaseAgent`` and ``AgentRegistry``
from the graph layer, making them the official developer-facing API.

Adding a custom agent
---------------------
1.  Subclass ``BaseAgent`` and implement ``execute(state) -> dict``.
2.  Register it with ``@AgentRegistry.register("my_agent")``.
3.  The agent becomes available in the graph pipeline and can be
    listed via ``AgentRegistry.list_agents()``.

Example::

    from app.prototype.agents.interfaces import BaseAgent, AgentRegistry

    @AgentRegistry.register("style_transfer")
    class StyleTransferAgent(BaseAgent):
        name = "style_transfer"
        description = "Transfer artistic style between traditions"

        def execute(self, state):
            # ... your logic here ...
            return {"style_result": {...}}

For image generation providers, subclass
``app.prototype.agents.draft_provider.AbstractProvider`` instead.

For LLM model routing, add entries to
``app.prototype.agents.model_router.MODELS``.
"""

try:
    from app.prototype.graph.base_agent import BaseAgent
    from app.prototype.graph.registry import AgentRegistry
except ImportError:
    # graph/ module removed in unified merge -- provide minimal stubs
    from abc import ABC, abstractmethod

    class BaseAgent(ABC):  # type: ignore[no-redef]
        name: str = ""
        description: str = ""

        @abstractmethod
        def execute(self, state: dict) -> dict: ...

    class AgentRegistry:  # type: ignore[no-redef]
        _agents: dict = {}

        @classmethod
        def register(cls, name: str):
            def decorator(agent_cls):
                cls._agents[name] = agent_cls
                return agent_cls
            return decorator

        @classmethod
        def list_agents(cls) -> list[str]:
            return list(cls._agents.keys())

__all__ = ["BaseAgent", "AgentRegistry"]
