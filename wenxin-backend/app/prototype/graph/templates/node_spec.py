"""NodeSpec — per-node instance configuration for template-driven construction.

Captures constructor kwargs for each node so the template builder can
instantiate nodes without hardcoded if/elif chains.  The ``config`` dict
is forwarded as ``**kwargs`` to the agent class constructor.

Example::

    NodeSpec(config={"parallel_critic": True, "enable_agent_critic": True})
    # → CriticNode(parallel_critic=True, enable_agent_critic=True)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class NodeSpec:
    """Per-node instance configuration for template-driven construction.

    Attributes
    ----------
    config : dict[str, Any]
        Keys are forwarded as kwargs to the agent class ``__init__``.
    """

    config: dict[str, Any] = field(default_factory=dict)
