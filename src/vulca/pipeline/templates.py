"""Pre-built pipeline templates -- DEFAULT, FAST, CRITIQUE_ONLY."""

from vulca.pipeline.types import PipelineDefinition

DEFAULT = PipelineDefinition(
    name="default",
    display_name="Default Pipeline",
    description="Generate → Evaluate → Decide, with rerun loop.",
    entry_point="generate",
    nodes=("generate", "evaluate", "decide"),
    edges=(
        ("generate", "evaluate"),
        ("evaluate", "decide"),
    ),
    enable_loop=True,
)

FAST = PipelineDefinition(
    name="fast",
    display_name="Fast Pipeline",
    description="Single-round generate + evaluate, no loop.",
    entry_point="generate",
    nodes=("generate", "evaluate", "decide"),
    edges=(
        ("generate", "evaluate"),
        ("evaluate", "decide"),
    ),
    enable_loop=False,
    node_specs={"decide": {"accept_threshold": 0.0}},
)

CRITIQUE_ONLY = PipelineDefinition(
    name="critique_only",
    display_name="Critique Only",
    description="Evaluate an existing image without generation.",
    entry_point="evaluate",
    nodes=("evaluate", "decide"),
    edges=(("evaluate", "decide"),),
    enable_loop=False,
    node_specs={"decide": {"accept_threshold": 0.0}},
)

CULTURAL_XIEYI = PipelineDefinition(
    name="cultural_xieyi",
    display_name="Cultural Xieyi Pipeline",
    description=(
        "Hybrid pipeline for Chinese Xieyi ink-wash art: "
        "Generate → WhitespaceAnalyze → ColorGamutCheck → CompositionAnalyze "
        "→ Evaluate (algo-augmented) → Decide. "
        "Algorithmic tools cover L1 (whitespace), L3 (gamut), L3 (composition) "
        "before VLM evaluation, replacing Gemini calls for covered dimensions."
    ),
    entry_point="generate",
    nodes=(
        "generate",
        "whitespace_analyze",
        "color_gamut_check",
        "composition_analyze",
        "evaluate",
        "decide",
    ),
    edges=(
        ("generate", "whitespace_analyze"),
        ("whitespace_analyze", "color_gamut_check"),
        ("color_gamut_check", "composition_analyze"),
        ("composition_analyze", "evaluate"),
        ("evaluate", "decide"),
    ),
    enable_loop=False,
    node_specs={"decide": {"accept_threshold": 0.0}},
)

LAYERED = PipelineDefinition(
    name="layered",
    display_name="Layered Creation",
    description=(
        "Generate independent layers with cultural tradition knowledge. "
        "PlanLayers → LayerGenerate. Agent orchestrates composition, "
        "evaluation, and iteration using MCP tools."
    ),
    entry_point="plan_layers",
    nodes=("plan_layers", "layer_generate"),
    edges=(
        ("plan_layers", "layer_generate"),
    ),
    enable_loop=False,
)

TEMPLATES: dict[str, PipelineDefinition] = {
    "default": DEFAULT,
    "fast": FAST,
    "critique_only": CRITIQUE_ONLY,
    "cultural_xieyi": CULTURAL_XIEYI,
    "layered": LAYERED,
}
