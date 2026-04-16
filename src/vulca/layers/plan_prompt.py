"""Prompt for planning layer structure from text intent (no image needed)."""
from __future__ import annotations

from pathlib import Path

import yaml

_TRADITION_LAYER_ORDERS: dict[str, list[dict[str, str]]] = {
    "chinese_xieyi": [
        {"role": "底纸/绢底", "content_type": "background", "blend": "normal",
         "position": "full canvas", "coverage": "100%"},
        {"role": "远景淡墨", "content_type": "atmosphere", "blend": "multiply",
         "position": "upper 25-35% of canvas", "coverage": "15-25%"},
        {"role": "中景山石树木", "content_type": "subject", "blend": "normal",
         "position": "center, slightly below middle", "coverage": "25-35%"},
        {"role": "近景人物建筑", "content_type": "subject", "blend": "normal",
         "position": "lower 30% of canvas", "coverage": "10-20%"},
        {"role": "题款印章", "content_type": "text", "blend": "multiply",
         "position": "upper-left or lower-right corner", "coverage": "5-10%"},
    ],
    "chinese_gongbi": [
        {"role": "熟宣底", "content_type": "background", "blend": "normal",
         "position": "full canvas", "coverage": "100%"},
        {"role": "白描勾线", "content_type": "line_art", "blend": "multiply",
         "position": "full canvas, defines all shapes", "coverage": "60-80%"},
        {"role": "分染罩染", "content_type": "color_wash", "blend": "normal",
         "position": "within line art outlines", "coverage": "40-60%"},
        {"role": "细节点染", "content_type": "detail", "blend": "normal",
         "position": "focal points only", "coverage": "5-15%"},
        {"role": "题款印章", "content_type": "text", "blend": "multiply",
         "position": "corner", "coverage": "5-10%"},
    ],
    "japanese_traditional": [
        {"role": "背景地", "content_type": "background", "blend": "normal",
         "position": "full canvas", "coverage": "100%"},
        {"role": "主線版", "content_type": "line_art", "blend": "multiply",
         "position": "full canvas, defines all shapes", "coverage": "50-70%"},
        {"role": "色版", "content_type": "color_block", "blend": "normal",
         "position": "within line art outlines", "coverage": "40-60%"},
        {"role": "金箔装飾", "content_type": "decoration", "blend": "screen",
         "position": "accent areas", "coverage": "5-15%"},
    ],
    "photography": [
        {"role": "sky/background", "content_type": "background", "blend": "normal",
         "position": "full canvas, emphasis on upper portion", "coverage": "100%"},
        {"role": "far distance", "content_type": "atmosphere", "blend": "normal",
         "position": "upper-middle horizon area", "coverage": "20-30%"},
        {"role": "mid-ground", "content_type": "subject", "blend": "normal",
         "position": "center of canvas", "coverage": "30-40%"},
        {"role": "foreground", "content_type": "subject", "blend": "normal",
         "position": "lower 30% of canvas", "coverage": "20-30%"},
        {"role": "effects (reflections/bokeh)", "content_type": "effect", "blend": "screen",
         "position": "overlay, matching subject positions", "coverage": "10-20%"},
    ],
}

_DEFAULT_ORDER = [
    {"role": "background", "content_type": "background", "blend": "normal",
     "position": "full canvas", "coverage": "100%"},
    {"role": "main subject", "content_type": "subject", "blend": "normal",
     "position": "center of canvas", "coverage": "30-50%"},
    {"role": "foreground/details", "content_type": "detail", "blend": "normal",
     "position": "lower portion", "coverage": "10-20%"},
    {"role": "text/overlay", "content_type": "text", "blend": "multiply",
     "position": "corner", "coverage": "5-10%"},
]


def _load_tradition_layers_from_yaml(tradition: str) -> list[dict[str, str]] | None:
    """Try to load tradition_layers from the tradition's YAML file."""
    yaml_dir = Path(__file__).parent.parent / "cultural" / "data" / "traditions"
    yaml_path = yaml_dir / f"{tradition}.yaml"
    if not yaml_path.exists():
        return None
    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        layers = data.get("tradition_layers")
        if layers and isinstance(layers, list):
            return layers
    except Exception:
        pass
    return None


def get_tradition_layer_order(tradition: str) -> list[dict[str, str]]:
    """Return the canonical layer order for a tradition.

    Tries YAML file first, falls back to hardcoded dict.
    """
    yaml_layers = _load_tradition_layers_from_yaml(tradition)
    if yaml_layers:
        return yaml_layers
    return _TRADITION_LAYER_ORDERS.get(tradition, _DEFAULT_ORDER)


def build_plan_prompt(intent: str, tradition: str = "default") -> str:
    """Build a VLM prompt to plan layer structure from text intent."""
    order = get_tradition_layer_order(tradition)
    order_text = "\n".join(
        f"  {i}. {o['role']} (content_type: {o['content_type']}, blend: {o['blend']}, "
        f"position: {o.get('position', 'flexible')}, coverage: {o.get('coverage', 'flexible')})"
        for i, o in enumerate(order)
    )

    return f"""Plan the layer structure for creating this artwork:

Intent: "{intent}"
Tradition: {tradition}

Tradition-specific layer order (use as guidance, adapt to the specific intent):
{order_text}

Rules:
- Plan 3-20 layers depending on scene complexity (use 12-20 for detail-heavy scenes)
- Each layer should be independently meaningful
- Order z_index from back (0) to front
- Assign blend_mode based on tradition conventions
- Include dominant_colors that would characterize each layer
- CRITICAL: Each layer's regeneration_prompt MUST include specific position and size constraints (e.g. "in the upper 30% of canvas", "covering about 20% of canvas area")
- CRITICAL: The background layer (content_type: background) must describe ONLY the base medium texture (paper, silk, canvas). Do NOT include ANY scene elements (mountains, water, trees, buildings, figures) in the background layer. Scene elements belong in atmosphere/subject layers.
- Respect the tradition's whitespace conventions (e.g. xieyi: 30-55% blank space)
- IMPORTANT: All "regeneration_prompt" values MUST be in English, regardless of the user's input language. Translate if necessary.

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
      "semantic_path": "optional dot-notation hierarchical label, e.g. 'subject.face.eyes' or 'person[0].hair' (empty string if not hierarchical)",
      "position": "where on canvas (e.g. 'upper 30%', 'lower-left corner', 'center')",
      "coverage": "approximate % of canvas area this element should cover",
      "regeneration_prompt": "MUST include position and size: e.g. 'Mountains in upper 30% of canvas, covering about 25%. Light ink wash...'"
    }}
  ]
}}

Return ONLY a JSON object (no markdown fences, no explanation)."""
