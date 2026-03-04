"""GraphTemplate — dataclass defining a composable pipeline topology.

Each template specifies which nodes to include, how they connect,
and what runtime behaviors (loop, parallel critic, HITL interrupts)
are enabled.  Templates are registered in TemplateRegistry and looked
up by name at graph-build time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ConditionalEdge:
    """A conditional edge in the graph that routes based on state."""

    source: str
    route_function: str  # Name of the routing function (e.g. "route_queen_decision")
    destinations: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphTemplate:
    """Immutable definition of a pipeline graph topology.

    Attributes
    ----------
    name : str
        Machine-readable identifier (e.g. "default", "fast_draft").
    display_name : str
        Human-readable label for the UI.
    description : str
        One-line explanation of the template's purpose.
    entry_point : str
        First node to execute.
    nodes : list[str]
        Ordered list of node names included in this template.
    edges : list[tuple[str, str]]
        Direct edges between nodes.
    conditional_edges : list[ConditionalEdge]
        Edges that branch based on state (e.g. Queen → Draft/Archivist).
    interrupt_before : list[str]
        Nodes to pause before for HITL input.
    enable_loop : bool
        Whether Queen can route back to Draft for re-generation.
    parallel_critic : bool
        Whether L1-L5 dimensions are scored in parallel.
    """

    name: str
    display_name: str
    description: str
    entry_point: str
    nodes: list[str] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)
    conditional_edges: list[ConditionalEdge] = field(default_factory=list)
    interrupt_before: list[str] = field(default_factory=list)
    enable_loop: bool = True
    parallel_critic: bool = False
    node_specs: dict[str, Any] | None = None  # str → NodeSpec; Any avoids circular import
