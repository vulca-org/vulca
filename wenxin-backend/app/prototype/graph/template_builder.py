"""template_builder — Build a LangGraph StateGraph from a GraphTemplate.

This module bridges the declarative GraphTemplate definitions with
the imperative LangGraph StateGraph API.  It resolves node classes
from the AgentRegistry, wires edges per the template spec, and
compiles with the appropriate checkpointer and interrupt settings.
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from app.prototype.graph.state import PipelineState
from app.prototype.graph.templates.template_model import GraphTemplate

# Import nodes to ensure @AgentRegistry.register decorators fire
from app.prototype.graph.nodes.scout_node import ScoutNode     # noqa: F401
from app.prototype.graph.nodes.router_node import RouterNode    # noqa: F401
from app.prototype.graph.nodes.draft_node import DraftNode      # noqa: F401
from app.prototype.graph.nodes.critic_node import CriticNode    # noqa: F401
from app.prototype.graph.nodes.queen_node import QueenNode      # noqa: F401
from app.prototype.graph.nodes.archivist_node import ArchivistNode  # noqa: F401

logger = logging.getLogger(__name__)

# ── Routing functions ─────────────────────────────────────────────────
# Named routing functions referenced by ConditionalEdge.route_function.
# Keep this dict in sync with any new routing strategies.

_ROUTE_FUNCTIONS: dict[str, Any] = {}


def _register_route(name: str):
    """Decorator to register a routing function by name."""
    def decorator(fn):
        _ROUTE_FUNCTIONS[name] = fn
        return fn
    return decorator


@_register_route("route_queen_decision")
def route_queen_decision(state: PipelineState) -> str:
    """Conditional edge after Queen: route to archivist or loop back to draft."""
    decision = (state.get("queen_decision") or {}).get("action", "stop")
    current_round = state.get("current_round", 1)
    max_rounds = state.get("max_rounds", 3)

    if decision == "accept":
        return "archivist"
    elif decision == "rerun" and current_round < max_rounds:
        return "draft"
    else:
        return "archivist"


# ── Builder ───────────────────────────────────────────────────────────

def build_graph_from_template(
    template: GraphTemplate,
    draft_config: dict | None = None,
    queen_config: dict | None = None,
    enable_agent_critic: bool = False,
    enable_hitl: bool = False,
    use_checkpointer: bool = True,
) -> Any:
    """Build and compile a LangGraph StateGraph from a GraphTemplate.

    Parameters
    ----------
    template : GraphTemplate
        Declarative topology definition.
    draft_config, queen_config : dict, optional
        Config dicts passed to DraftNode/QueenNode constructors.
    enable_agent_critic : bool
        Use CriticLLM instead of rule-based CriticAgent.
    enable_hitl : bool
        Add interrupt_before points from the template.
    use_checkpointer : bool
        Attach MemorySaver for state checkpointing.

    Returns
    -------
    CompiledGraph
    """
    from app.prototype.graph.registry import AgentRegistry
    from app.prototype.graph.templates.node_spec import NodeSpec

    _DEFAULT_SPEC = NodeSpec()  # reused across iterations

    graph = StateGraph(PipelineState)

    # Instantiate nodes using NodeSpec-driven config (data-driven factory).
    # NodeSpec provides template-level defaults; runtime params override.
    for node_name in template.nodes:
        agent_cls = AgentRegistry.get(node_name)
        spec = (template.node_specs or {}).get(node_name, _DEFAULT_SPEC)
        merged: dict[str, Any] = {**spec.config}

        # Runtime overrides for specific node types
        if node_name == "draft" and draft_config is not None:
            merged.setdefault("draft_config", draft_config)
        if node_name == "critic":
            merged.setdefault("enable_agent_critic", enable_agent_critic)
            merged.setdefault("parallel_critic", template.parallel_critic)
        if node_name == "queen" and queen_config is not None:
            merged.setdefault("queen_config", queen_config)

        node_instance = agent_cls(**merged)
        graph.add_node(node_name, node_instance.execute)

    # Set entry point
    graph.set_entry_point(template.entry_point)

    # Add direct edges
    for src, dst in template.edges:
        if dst == "__end__":
            graph.add_edge(src, END)
        else:
            graph.add_edge(src, dst)

    # Add conditional edges
    for cond_edge in template.conditional_edges:
        route_fn = _ROUTE_FUNCTIONS.get(cond_edge.route_function)
        if route_fn is None:
            raise ValueError(
                f"Unknown route function '{cond_edge.route_function}'. "
                f"Available: {sorted(_ROUTE_FUNCTIONS.keys())}"
            )
        graph.add_conditional_edges(
            cond_edge.source,
            route_fn,
            cond_edge.destinations,
        )

    # Compile
    compile_kwargs: dict[str, Any] = {}

    if use_checkpointer:
        compile_kwargs["checkpointer"] = MemorySaver()

    # Determine interrupt points
    if enable_hitl and template.interrupt_before:
        compile_kwargs["interrupt_before"] = template.interrupt_before
    elif enable_hitl:
        # Fallback: pause before queen (matches default behavior)
        compile_kwargs["interrupt_before"] = (
            ["queen"] if "queen" in template.nodes else []
        )

    compiled = graph.compile(**compile_kwargs)
    logger.info(
        "Built graph from template '%s' (nodes=%s, hitl=%s)",
        template.name,
        template.nodes,
        compile_kwargs.get("interrupt_before", []),
    )
    return compiled
