"""VLM-based layer analysis — identify semantic layers in an image."""
from __future__ import annotations

import json
import logging
import os
import re

import litellm

from vulca.layers.prompt import build_analyze_prompt, parse_v2_response
from vulca.layers.types import LayerInfo

logger = logging.getLogger("vulca.layers")

_MAX_RETRIES = 2


def _extract_json(text: str) -> dict:
    """Extract and parse JSON from VLM response text.

    Strips markdown code fences, then tries json.loads directly.
    Falls back to extracting content between first { and last }.
    Raises ValueError if no valid JSON can be extracted.
    """
    # Strip markdown code block fences
    if text.startswith("```"):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        text = text.strip()

    # Try parsing the full text as JSON first (most reliable)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract JSON between first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Could not parse layer analysis: {text[:200]}")
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        raise ValueError(f"Could not parse layer analysis: {text[:200]}")


def parse_layer_response(raw: dict) -> list[LayerInfo]:
    """Parse VLM JSON response into LayerInfo list.

    Delegates to parse_v2_response for V2 format (no bbox,
    includes content_type / dominant_colors / regeneration_prompt).
    Kept for backward compatibility.
    """
    return parse_v2_response(raw)


async def analyze_layers(image_path: str, *, api_key: str = "") -> list[LayerInfo]:
    """Use VLM to identify semantic layers in an image.

    Retries up to _MAX_RETRIES times on transient failures.
    Uses V2 prompt from build_analyze_prompt().
    """
    from vulca._image import load_image_base64

    img_b64, mime = await load_image_base64(image_path)
    model = os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash")
    prompt = build_analyze_prompt()

    last_err: Exception = ValueError("No attempts made")
    for attempt in range(_MAX_RETRIES + 1):
        try:
            resp = await litellm.acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                        {"type": "text", "text": "Identify the semantic layers of this artwork."},
                    ]},
                ],
                max_tokens=4096,
                temperature=0.1,
                api_key=api_key or os.environ.get("GOOGLE_API_KEY", ""),
                timeout=30,
            )
            text = resp.choices[0].message.content.strip()
            raw = _extract_json(text)
            return parse_layer_response(raw)
        except Exception as e:
            last_err = e
            if attempt < _MAX_RETRIES:
                logger.warning("Layer analysis attempt %d failed: %s", attempt + 1, e)
                continue

    raise ValueError(
        f"Layer analysis failed after {_MAX_RETRIES + 1} attempts: {last_err}"
    )
