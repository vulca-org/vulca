"""Prompt for planning layer structure from text intent (no image needed)."""
from __future__ import annotations

_TRADITION_LAYER_ORDERS: dict[str, list[dict[str, str]]] = {
    "chinese_xieyi": [
        {"role": "底纸/绢底", "content_type": "background", "blend": "normal"},
        {"role": "远景淡墨", "content_type": "atmosphere", "blend": "multiply"},
        {"role": "中景山石树木", "content_type": "subject", "blend": "normal"},
        {"role": "近景人物建筑", "content_type": "subject", "blend": "normal"},
        {"role": "题款印章", "content_type": "text", "blend": "multiply"},
    ],
    "chinese_gongbi": [
        {"role": "熟宣底", "content_type": "background", "blend": "normal"},
        {"role": "白描勾线", "content_type": "line_art", "blend": "multiply"},
        {"role": "分染罩染", "content_type": "color_wash", "blend": "normal"},
        {"role": "细节点染", "content_type": "detail", "blend": "normal"},
        {"role": "题款印章", "content_type": "text", "blend": "multiply"},
    ],
    "japanese_traditional": [
        {"role": "背景地", "content_type": "background", "blend": "normal"},
        {"role": "主線版", "content_type": "line_art", "blend": "multiply"},
        {"role": "色版", "content_type": "color_block", "blend": "normal"},
        {"role": "金箔装飾", "content_type": "decoration", "blend": "screen"},
    ],
    "photography": [
        {"role": "sky/background", "content_type": "background", "blend": "normal"},
        {"role": "far distance", "content_type": "atmosphere", "blend": "normal"},
        {"role": "mid-ground", "content_type": "subject", "blend": "normal"},
        {"role": "foreground", "content_type": "subject", "blend": "normal"},
        {"role": "effects (reflections/bokeh)", "content_type": "effect", "blend": "screen"},
    ],
}

_DEFAULT_ORDER = [
    {"role": "background", "content_type": "background", "blend": "normal"},
    {"role": "main subject", "content_type": "subject", "blend": "normal"},
    {"role": "foreground/details", "content_type": "detail", "blend": "normal"},
    {"role": "text/overlay", "content_type": "text", "blend": "multiply"},
]


def get_tradition_layer_order(tradition: str) -> list[dict[str, str]]:
    """Return the canonical layer order for a tradition."""
    return _TRADITION_LAYER_ORDERS.get(tradition, _DEFAULT_ORDER)


def build_plan_prompt(intent: str, tradition: str = "default") -> str:
    """Build a VLM prompt to plan layer structure from text intent."""
    order = get_tradition_layer_order(tradition)
    order_text = "\n".join(
        f"  {i}. {o['role']} (typical content_type: {o['content_type']}, blend: {o['blend']})"
        for i, o in enumerate(order)
    )

    return f"""Plan the layer structure for creating this artwork:

Intent: "{intent}"
Tradition: {tradition}

Tradition-specific layer order (use as guidance, adapt to the specific intent):
{order_text}

Rules:
- Plan 3-8 layers depending on scene complexity
- Each layer should be independently meaningful
- Order z_index from back (0) to front
- Assign blend_mode based on tradition conventions
- Include dominant_colors that would characterize each layer
- Write a detailed regeneration_prompt for each layer (20-40 words) sufficient to generate that layer's content independently, while maintaining the overall scene context

Return a JSON object with this exact structure:
{{
  "layers": [
    {{
      "name": "snake_case_name",
      "description": "Detailed description (20-40 words)",
      "z_index": 0,
      "blend_mode": "normal|screen|multiply",
      "dominant_colors": ["#hex1", "#hex2"],
      "content_type": "free-form label",
      "regeneration_prompt": "Prompt to generate this layer in the context of the full scene"
    }}
  ]
}}

Return ONLY a JSON object (no markdown fences, no explanation)."""
