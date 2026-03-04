"""TemplateRegistry — pre-defined graph templates for VULCA pipeline.

Five templates covering the most common usage patterns:

| Template         | Nodes                                    | Loop | Parallel |
|------------------|------------------------------------------|------|----------|
| default          | scout→router→draft→critic→queen→archivist| yes  | no       |
| fast_draft       | draft→critic→queen→archivist             | yes  | no       |
| critique_only    | critic→archivist                         | no   | no       |
| interactive_full | all 6 + full HITL                        | yes  | yes      |
| batch_eval       | scout→router→draft→critic→archivist      | no   | no       |
"""

from __future__ import annotations

from app.prototype.graph.templates.node_spec import NodeSpec
from app.prototype.graph.templates.template_model import ConditionalEdge, GraphTemplate

# ── Template Definitions ──────────────────────────────────────────────

_QUEEN_CONDITIONAL = ConditionalEdge(
    source="queen",
    route_function="route_queen_decision",
    destinations={"draft": "draft", "archivist": "archivist"},
)

DEFAULT = GraphTemplate(
    name="default",
    display_name="Standard Pipeline",
    description="Full Scout→Draft→Critic→Queen cycle with loop support",
    entry_point="scout",
    nodes=["scout", "router", "draft", "critic", "queen", "archivist"],
    edges=[
        ("scout", "router"),
        ("router", "draft"),
        ("draft", "critic"),
        ("critic", "queen"),
        ("archivist", "__end__"),
    ],
    conditional_edges=[_QUEEN_CONDITIONAL],
    enable_loop=True,
    parallel_critic=False,
)

FAST_DRAFT = GraphTemplate(
    name="fast_draft",
    display_name="Fast Draft",
    description="Skip Scout evidence — jump straight to generation",
    entry_point="draft",
    nodes=["draft", "critic", "queen", "archivist"],
    edges=[
        ("draft", "critic"),
        ("critic", "queen"),
        ("archivist", "__end__"),
    ],
    conditional_edges=[_QUEEN_CONDITIONAL],
    enable_loop=True,
    parallel_critic=False,
)

CRITIQUE_ONLY = GraphTemplate(
    name="critique_only",
    display_name="Critique Only",
    description="Evaluate an existing image without generation",
    entry_point="critic",
    nodes=["critic", "archivist"],
    edges=[
        ("critic", "archivist"),
        ("archivist", "__end__"),
    ],
    conditional_edges=[],
    enable_loop=False,
    parallel_critic=False,
)

INTERACTIVE_FULL = GraphTemplate(
    name="interactive_full",
    display_name="Interactive (HITL)",
    description="Full pipeline with human review at every stage",
    entry_point="scout",
    nodes=["scout", "router", "draft", "critic", "queen", "archivist"],
    edges=[
        ("scout", "router"),
        ("router", "draft"),
        ("draft", "critic"),
        ("critic", "queen"),
        ("archivist", "__end__"),
    ],
    conditional_edges=[_QUEEN_CONDITIONAL],
    interrupt_before=["draft", "critic", "queen"],
    enable_loop=True,
    parallel_critic=True,
    node_specs={
        "critic": NodeSpec(config={"parallel_critic": True, "enable_agent_critic": False}),
    },
)

BATCH_EVAL = GraphTemplate(
    name="batch_eval",
    display_name="Batch Evaluation",
    description="Single-pass evaluation — no loop, automated scoring",
    entry_point="scout",
    nodes=["scout", "router", "draft", "critic", "archivist"],
    edges=[
        ("scout", "router"),
        ("router", "draft"),
        ("draft", "critic"),
        ("critic", "archivist"),
        ("archivist", "__end__"),
    ],
    conditional_edges=[],
    enable_loop=False,
    parallel_critic=False,
)

# ── Registry ──────────────────────────────────────────────────────────

_TEMPLATES: dict[str, GraphTemplate] = {
    t.name: t
    for t in [DEFAULT, FAST_DRAFT, CRITIQUE_ONLY, INTERACTIVE_FULL, BATCH_EVAL]
}


class TemplateRegistry:
    """Lookup and listing of pre-defined graph templates."""

    @staticmethod
    def get(name: str) -> GraphTemplate:
        """Get a template by name. Raises KeyError if not found."""
        if name not in _TEMPLATES:
            raise KeyError(
                f"Template '{name}' not found. "
                f"Available: {sorted(_TEMPLATES.keys())}"
            )
        return _TEMPLATES[name]

    @staticmethod
    def list_templates() -> list[GraphTemplate]:
        """Return all templates sorted by name."""
        return sorted(_TEMPLATES.values(), key=lambda t: t.name)

    @staticmethod
    def list_names() -> list[str]:
        """Return sorted list of template names."""
        return sorted(_TEMPLATES.keys())
