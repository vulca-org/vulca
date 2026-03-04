"""pipeline_graph — Build the default LangGraph StateGraph for VULCA pipeline.

Graph topology::

    Scout → Router → Draft → Critic → Queen
                                         ↓
                                   [accept] → Archivist → END
                                   [rerun]  → Draft (loop)
                                   [stop]   → Archivist → END

The graph is compiled with an optional MemorySaver checkpointer
and configurable interrupt_before points for multi-stage HITL.
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from app.prototype.graph.state import PipelineState

# Import all nodes to trigger @AgentRegistry.register decorators
from app.prototype.graph.nodes.scout_node import ScoutNode     # noqa: F401
from app.prototype.graph.nodes.router_node import RouterNode    # noqa: F401
from app.prototype.graph.nodes.draft_node import DraftNode      # noqa: F401
from app.prototype.graph.nodes.critic_node import CriticNode    # noqa: F401
from app.prototype.graph.nodes.queen_node import QueenNode      # noqa: F401
from app.prototype.graph.nodes.archivist_node import ArchivistNode  # noqa: F401

logger = logging.getLogger(__name__)


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
        # "stop" or max rounds reached
        return "archivist"


def build_default_graph(
    draft_config: dict | None = None,
    queen_config: dict | None = None,
    enable_agent_critic: bool = False,
    enable_hitl: bool = False,
    interrupt_before: list[str] | None = None,
    use_checkpointer: bool = True,
) -> Any:
    """Build and compile the default VULCA pipeline graph.

    Parameters
    ----------
    draft_config : dict, optional
        DraftConfig as dict, passed to DraftNode.
    queen_config : dict, optional
        QueenConfig as dict, passed to QueenNode.
    enable_agent_critic : bool
        If True, use CriticLLM instead of rule-based CriticAgent.
    enable_hitl : bool
        If True, add interrupt_before points for HITL.
    interrupt_before : list[str], optional
        Explicit list of node names to pause before.
        Overrides enable_hitl default (["queen"]).
    use_checkpointer : bool
        If True, attach MemorySaver for state checkpointing.

    Returns
    -------
    CompiledGraph
        A LangGraph compiled graph ready for invoke/stream.
    """
    # Instantiate nodes with their configs
    scout_node = ScoutNode()
    router_node = RouterNode()
    draft_node = DraftNode(draft_config=draft_config)
    critic_node = CriticNode(enable_agent_critic=enable_agent_critic)
    queen_node = QueenNode(queen_config=queen_config)
    archivist_node = ArchivistNode()

    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("scout", scout_node.execute)
    graph.add_node("router", router_node.execute)
    graph.add_node("draft", draft_node.execute)
    graph.add_node("critic", critic_node.execute)
    graph.add_node("queen", queen_node.execute)
    graph.add_node("archivist", archivist_node.execute)

    # Define edges
    graph.set_entry_point("scout")
    graph.add_edge("scout", "router")
    graph.add_edge("router", "draft")
    graph.add_edge("draft", "critic")
    graph.add_edge("critic", "queen")

    # Conditional edge: Queen decides next step
    graph.add_conditional_edges(
        "queen",
        route_queen_decision,
        {
            "draft": "draft",
            "archivist": "archivist",
        },
    )
    graph.add_edge("archivist", END)

    # Compile with optional checkpointer and interrupts
    compile_kwargs: dict[str, Any] = {}

    if use_checkpointer:
        compile_kwargs["checkpointer"] = MemorySaver()

    # Determine interrupt points
    if interrupt_before is not None:
        compile_kwargs["interrupt_before"] = interrupt_before
    elif enable_hitl:
        # Default HITL: pause before Queen (matching old orchestrator behavior)
        compile_kwargs["interrupt_before"] = ["queen"]

    compiled = graph.compile(**compile_kwargs)
    logger.info(
        "Built default pipeline graph (hitl=%s, interrupt_before=%s)",
        enable_hitl,
        compile_kwargs.get("interrupt_before", []),
    )
    return compiled


# ── Template-based builder convenience wrapper ────────────────────────

def build_graph_from_template_name(
    template_name: str,
    draft_config: dict | None = None,
    queen_config: dict | None = None,
    enable_agent_critic: bool = False,
    enable_hitl: bool = False,
    use_checkpointer: bool = True,
):
    """Build a graph from a named template, falling back to build_default_graph.

    This provides a single entry point that gracefully degrades if the
    template system is not available.
    """
    try:
        from app.prototype.graph.templates.template_registry import TemplateRegistry
        from app.prototype.graph.template_builder import build_graph_from_template

        template = TemplateRegistry.get(template_name)
        return build_graph_from_template(
            template=template,
            draft_config=draft_config,
            queen_config=queen_config,
            enable_agent_critic=enable_agent_critic,
            enable_hitl=enable_hitl,
            use_checkpointer=use_checkpointer,
        )
    except (ImportError, KeyError) as exc:
        logger.warning(
            "Template '%s' unavailable (%s), falling back to default graph",
            template_name, exc,
        )
        return build_default_graph(
            draft_config=draft_config,
            queen_config=queen_config,
            enable_agent_critic=enable_agent_critic,
            enable_hitl=enable_hitl,
            use_checkpointer=use_checkpointer,
        )
