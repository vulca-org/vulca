"""Lazy-import agent factory with catalog registry.

Provides a single entry point for creating pipeline agents without
importing their modules at module load time.  This cuts orchestrator
import time and avoids circular-dependency issues when agent modules
grow heavier dependencies (GPU libs, LLM clients, etc.).

Usage::

    from app.prototype.orchestrator.agent_factory import create_agent, list_agents

    draft = create_agent("draft", config=my_draft_config)
    print(list_agents())
"""

from __future__ import annotations

import importlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Built-in agent catalog: name -> (module_path, class_name)
# ---------------------------------------------------------------------------
_AGENT_CATALOG: dict[str, tuple[str, str]] = {
    "draft": ("app.prototype.agents.draft_agent", "DraftAgent"),
    "critic": ("app.prototype.agents.critic_agent", "CriticAgent"),
    "queen": ("app.prototype.agents.queen_agent", "QueenAgent"),
    "archivist": ("app.prototype.agents.archivist_agent", "ArchivistAgent"),
    "critic_llm": ("app.prototype.agents.critic_llm", "CriticLLM"),
    "queen_llm": ("app.prototype.agents.queen_llm", "QueenLLMAgent"),
}

# Runtime-registered agents (plugins, community agents, etc.)
_RUNTIME_REGISTRY: dict[str, tuple[str, str]] = {}


def create_agent(name: str, **kwargs: Any) -> Any:
    """Instantiate an agent by catalog name with lazy imports.

    Parameters
    ----------
    name : str
        Registered agent name (e.g. ``"draft"``, ``"critic_llm"``).
    **kwargs
        Forwarded to the agent class constructor.

    Returns
    -------
    Any
        The instantiated agent object.

    Raises
    ------
    KeyError
        If *name* is not found in the catalog or runtime registry.
    """
    # Runtime registry takes precedence over built-in catalog
    if name in _RUNTIME_REGISTRY:
        module_path, class_name = _RUNTIME_REGISTRY[name]
    elif name in _AGENT_CATALOG:
        module_path, class_name = _AGENT_CATALOG[name]
    else:
        available = sorted(set(_AGENT_CATALOG) | set(_RUNTIME_REGISTRY))
        raise KeyError(
            f"Unknown agent '{name}'. Available agents: {available}"
        )

    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    logger.debug("Creating agent '%s' via %s.%s", name, module_path, class_name)
    return cls(**kwargs)


def register_agent(name: str, module_path: str, class_name: str) -> None:
    """Register a custom agent at runtime (for plugins / community agents).

    Parameters
    ----------
    name : str
        Unique agent name.  Overrides built-in catalog entries if same name.
    module_path : str
        Dotted Python module path (e.g. ``"my_plugin.agents.custom"``).
    class_name : str
        Class name inside the module (e.g. ``"CustomAgent"``).
    """
    _RUNTIME_REGISTRY[name] = (module_path, class_name)
    logger.info("Registered agent '%s' -> %s.%s", name, module_path, class_name)


def list_agents() -> list[str]:
    """Return all available agent names (built-in + runtime-registered)."""
    return sorted(set(_AGENT_CATALOG) | set(_RUNTIME_REGISTRY))
