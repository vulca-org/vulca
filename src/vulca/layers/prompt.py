"""V2 analysis prompt engine for VULCA layered artwork."""
from __future__ import annotations

from vulca.layers.types import LayerInfo

ANALYZE_PROMPT = """Analyze this image and decompose it into independent semantic layers (3-20 layers depending on complexity; detail-heavy portraits or group scenes may use 12-20).

Adapt your decomposition to the image type:
- Artwork/illustration: separate by visual depth and semantic meaning (background, subjects, effects, text)
- UI/app design: separate by interface components (navigation, headers, cards, buttons, content sections)
- Photography: separate by depth plane (foreground, subject, midground, background, sky)
- Design/poster: separate by design elements (background, imagery, typography, decorative elements)

Rules:
- Layers should minimize content overlap
- Each layer should be independently meaningful
- Order z_index from back (0) to front

For each layer provide:
{
  "layers": [
    {
      "name": "snake_case_name",
      "description": "Detailed description sufficient to regenerate this layer independently (20-40 words)",
      "z_index": 0,
      "blend_mode": "normal|screen|multiply",
      "dominant_colors": ["#hex1", "#hex2"],
      "content_type": "free-form label (e.g. background, subject, effect, ui_header, ui_card, typography, decoration — any descriptive label)",
      "semantic_path": "optional dot-notation hierarchical label, e.g. 'subject.face.eyes' or 'person[0].hair' (empty string if not hierarchical)",
      "regeneration_prompt": "Prompt to regenerate ONLY this layer's content, preserving the original style"
    }
  ]
}

Return ONLY a JSON object (no markdown fences, no explanation)."""

_VALID_BLEND_MODES = {"normal", "screen", "multiply"}
# content_type is free-form — VLM decides the label based on image content


def build_analyze_prompt() -> str:
    """Return the V2 analysis system prompt."""
    return ANALYZE_PROMPT


def parse_v2_response(raw: dict) -> list[LayerInfo]:
    """Parse VLM V2 response into LayerInfo list.

    Args:
        raw: Dict with a "layers" key containing a list of layer dicts.

    Returns:
        List of LayerInfo sorted by z_index ascending.
    """
    layers_data = raw.get("layers", [])
    results: list[LayerInfo] = []

    for item in layers_data:
        name = item.get("name", "")
        description = item.get("description", "")
        z_index = int(item.get("z_index", 0))

        blend_mode = item.get("blend_mode", "normal")
        if blend_mode not in _VALID_BLEND_MODES:
            blend_mode = "normal"

        content_type = item.get("content_type", "background")
        # Free-form: VLM can assign any descriptive label

        dominant_colors = item.get("dominant_colors", [])
        if not isinstance(dominant_colors, list):
            dominant_colors = []

        regeneration_prompt = item.get("regeneration_prompt", "")

        layer = LayerInfo(
            name=name,
            description=description,
            z_index=z_index,
            blend_mode=blend_mode,
            content_type=content_type,
            dominant_colors=dominant_colors,
            regeneration_prompt=regeneration_prompt,
            position=item.get("position", "") or "",
            coverage=item.get("coverage", "") or "",
            semantic_path=item.get("semantic_path", "") or "",
        )
        results.append(layer)

    results.sort(key=lambda li: li.z_index)
    return results


def build_regeneration_prompt(
    info: LayerInfo,
    *,
    width: int = 1024,
    height: int = 1024,
    tradition: str = "",
    other_layer_names: list[str] | None = None,
) -> str:
    """Build prompt for regenerating a single layer via img2img.

    Args:
        info: The LayerInfo for the layer to regenerate.
        width: Canvas width in pixels.
        height: Canvas height in pixels.
        tradition: Cultural tradition name; included in prompt when non-empty.
        other_layer_names: Names of other layers to exclude from this layer.

    Returns:
        A complete regeneration prompt string.
    """
    base = info.regeneration_prompt if info.regeneration_prompt else info.description

    parts = [
        base,
        f"Paint ONLY this layer's content on a plain white background. Do NOT draw checkerboard patterns or transparency grids.",
        f"Canvas size: {width}x{height}.",
    ]

    if tradition:
        parts.append(f"Cultural tradition: {tradition}.")

    if other_layer_names:
        names_str = ", ".join(other_layer_names)
        parts.append(f"DO NOT include any elements from these other layers: {names_str}.")

    return " ".join(parts)
