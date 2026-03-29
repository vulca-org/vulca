"""VLM-based layer analysis — identify semantic layers in an image."""
from __future__ import annotations

import json
import logging
import os
import re

import litellm

from vulca.layers.types import LayerInfo

logger = logging.getLogger("vulca.layers")

_BLEND_TO_BG = {"screen": "black", "multiply": "gray", "normal": "white"}

_ANALYZE_PROMPT = """\
Analyze this image and identify its semantic layers (3-6 layers).
For each layer, provide:
- name: short snake_case identifier
- description: what this layer contains (under 15 words)
- bbox: bounding box as percentages {"x": 0-100, "y": 0-100, "w": 1-100, "h": 1-100}
- z_index: stacking order (0 = bottom/background)
- blend_mode: "normal" for solid objects, "screen" for light/glow effects, "multiply" for shadows/mist

Keep descriptions concise. Return ONLY a JSON object (no markdown):
{"layers": [{"name": "...", "description": "...", "bbox": {...}, "z_index": 0, "blend_mode": "..."}]}
"""


def parse_layer_response(raw: dict) -> list[LayerInfo]:
    """Parse VLM JSON response into LayerInfo list."""
    layers_raw = raw.get("layers", [])
    result: list[LayerInfo] = []
    for item in layers_raw:
        blend = item.get("blend_mode", "normal")
        if blend not in ("normal", "screen", "multiply"):
            blend = "normal"
        bg_color = _BLEND_TO_BG.get(blend, "white")
        result.append(LayerInfo(
            name=item.get("name", f"layer_{len(result)}"),
            description=item.get("description", ""),
            bbox=item.get("bbox", {"x": 0, "y": 0, "w": 100, "h": 100}),
            z_index=item.get("z_index", len(result)),
            blend_mode=blend,
            bg_color=bg_color,
        ))
    result.sort(key=lambda l: l.z_index)
    return result


async def analyze_layers(image_path: str, *, api_key: str = "") -> list[LayerInfo]:
    """Use VLM to identify semantic layers in an image."""
    from vulca._image import load_image_base64

    img_b64, mime = await load_image_base64(image_path)
    model = os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash")

    resp = await litellm.acompletion(
        model=model,
        messages=[
            {"role": "system", "content": _ANALYZE_PROMPT},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                {"type": "text", "text": "Identify the semantic layers of this artwork."},
            ]},
        ],
        max_tokens=2048,
        temperature=0.1,
        api_key=api_key or os.environ.get("GOOGLE_API_KEY", ""),
        timeout=30,
    )

    text = resp.choices[0].message.content.strip()
    # Strip markdown code block
    if text.startswith("```"):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        text = text.strip()

    # Try parsing the full text as JSON first (most reliable)
    try:
        raw = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: find outermost JSON object
        start = text.find("{")
        if start == -1:
            raise ValueError(f"Could not parse layer analysis: {text[:200]}")
        # Find matching closing brace by counting
        depth = 0
        end = start
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        try:
            raw = json.loads(text[start:end])
        except json.JSONDecodeError:
            raise ValueError(f"Could not parse layer analysis: {text[:200]}")
    return parse_layer_response(raw)
