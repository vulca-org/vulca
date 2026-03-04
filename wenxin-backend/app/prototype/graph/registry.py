"""AgentRegistry — plugin registry for graph nodes.

Allows dynamic registration and lookup of BaseAgent subclasses,
enabling future extensibility (custom agents, style transfer, etc.)
without modifying the core graph builder.

Usage::

    @AgentRegistry.register("my_custom_agent")
    class MyCustomAgent(BaseAgent):
        ...

    agent_cls = AgentRegistry.get("my_custom_agent")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.prototype.graph.base_agent import BaseAgent


class AgentRegistry:
    """Global registry of available agent node types."""

    _agents: dict[str, type[BaseAgent]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a BaseAgent subclass.

        Usage::

            @AgentRegistry.register("scout")
            class ScoutNode(BaseAgent):
                ...
        """
        def decorator(agent_cls: type[BaseAgent]):
            cls._agents[name] = agent_cls
            return agent_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> type[BaseAgent]:
        """Look up a registered agent class by name.

        Raises KeyError if not found.
        """
        if name not in cls._agents:
            raise KeyError(
                f"Agent '{name}' not registered. "
                f"Available: {sorted(cls._agents.keys())}"
            )
        return cls._agents[name]

    @classmethod
    def get_metadata(cls, name: str):
        """Get the AgentMetadata for a registered agent, or None."""
        agent_cls = cls.get(name)
        return getattr(agent_cls, "metadata_info", None)

    @classmethod
    def list_agents(cls) -> list[str]:
        """Return sorted list of all registered agent names."""
        return sorted(cls._agents.keys())

    @classmethod
    def list_agents_with_metadata(cls) -> list[dict]:
        """Return list of agent info dicts including metadata."""
        result = []
        for name in sorted(cls._agents.keys()):
            agent_cls = cls._agents[name]
            meta = getattr(agent_cls, "metadata_info", None)
            info: dict = {"name": name, "description": agent_cls.description}
            if meta is not None:
                from dataclasses import asdict
                info["metadata"] = asdict(meta)
            result.append(info)
        return result

    @classmethod
    def clear(cls) -> None:
        """Clear registry (useful for testing)."""
        cls._agents.clear()
