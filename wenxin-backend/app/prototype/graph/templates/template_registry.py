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

# ── M8: Quick Evaluate + Scenario Templates ──────────────────────────

QUICK_EVALUATE = GraphTemplate(
    name="quick_evaluate",
    display_name="Quick Evaluate",
    description="2-node evaluation — the fastest path to L1-L5 scores",
    entry_point="critic",
    nodes=["critic", "report"],
    edges=[
        ("critic", "report"),
        ("report", "__end__"),
    ],
    conditional_edges=[],
    enable_loop=False,
    parallel_critic=False,
)

SCENARIO_A_BRAND_CHECK = GraphTemplate(
    name="scenario_a_brand_check",
    display_name="Brand Safety Scan",
    description="Quick cultural compliance check for brand assets",
    entry_point="scout",
    nodes=["scout", "router", "critic", "report"],
    edges=[
        ("scout", "router"),
        ("router", "critic"),
        ("critic", "report"),
        ("report", "__end__"),
    ],
    conditional_edges=[],
    enable_loop=False,
    parallel_critic=False,
)

SCENARIO_B_DIAGNOSIS = GraphTemplate(
    name="scenario_b_diagnosis",
    display_name="Full Diagnosis",
    description="Complete L1-L5 diagnosis with evidence gathering",
    entry_point="scout",
    nodes=["scout", "router", "critic", "report"],
    edges=[
        ("scout", "router"),
        ("router", "critic"),
        ("critic", "report"),
        ("report", "__end__"),
    ],
    conditional_edges=[],
    enable_loop=False,
    parallel_critic=True,
    node_specs={
        "critic": NodeSpec(config={"enable_agent_critic": True}),
    },
)

SCENARIO_C_COMPARE = GraphTemplate(
    name="scenario_c_compare",
    display_name="Before/After Compare",
    description="Evaluate and compare two images side by side",
    entry_point="critic",
    nodes=["critic", "report"],
    edges=[
        ("critic", "report"),
        ("report", "__end__"),
    ],
    conditional_edges=[],
    enable_loop=False,
    parallel_critic=False,
)

SCENARIO_D_LEARNING = GraphTemplate(
    name="scenario_d_learning",
    display_name="Learning Pipeline",
    description="Full chain with generation — see how evaluation drives improvement",
    entry_point="scout",
    nodes=["scout", "router", "draft", "critic", "report"],
    edges=[
        ("scout", "router"),
        ("router", "draft"),
        ("draft", "critic"),
        ("critic", "report"),
        ("report", "__end__"),
    ],
    conditional_edges=[],
    enable_loop=False,
    parallel_critic=False,
)

SCENARIO_E_BATCH = GraphTemplate(
    name="scenario_e_batch",
    display_name="Batch + Report",
    description="Single-pass batch evaluation with in-canvas report",
    entry_point="scout",
    nodes=["scout", "router", "draft", "critic", "report"],
    edges=[
        ("scout", "router"),
        ("router", "draft"),
        ("draft", "critic"),
        ("critic", "report"),
        ("report", "__end__"),
    ],
    conditional_edges=[],
    enable_loop=False,
    parallel_critic=False,
)

# ── Registry ──────────────────────────────────────────────────────────

_TEMPLATES: dict[str, GraphTemplate] = {
    t.name: t
    for t in [
        DEFAULT,
        FAST_DRAFT,
        CRITIQUE_ONLY,
        INTERACTIVE_FULL,
        BATCH_EVAL,
        QUICK_EVALUATE,
        SCENARIO_A_BRAND_CHECK,
        SCENARIO_B_DIAGNOSIS,
        SCENARIO_C_COMPARE,
        SCENARIO_D_LEARNING,
        SCENARIO_E_BATCH,
    ]
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
