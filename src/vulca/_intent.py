"""Intent resolution -- detect cultural tradition from natural language."""

from __future__ import annotations

import json
import logging

import litellm

from vulca.cultural import TRADITIONS

logger = logging.getLogger("vulca")

_SYSTEM_PROMPT = """\
You are a cultural art analysis router. Given a user's evaluation intent,
determine the most appropriate cultural tradition for evaluation.

Available traditions: {traditions}

Respond with ONLY a JSON object:
{{"tradition": "<tradition_name>", "confidence": <0.0-1.0>}}

If the intent is unclear or general, use "default" with low confidence.
"""


async def resolve_intent(
    intent: str,
    *,
    api_key: str,
) -> tuple[str, float]:
    """Resolve user intent to a cultural tradition.

    Returns
    -------
    tuple[str, float]
        ``(tradition_name, confidence)``
    """
    if not intent.strip():
        return "default", 0.0

    # Fast keyword matching first (covers ~90% of cases)
    tradition, conf = _keyword_match(intent)
    if conf >= 0.8:
        return tradition, conf

    # LLM fallback for ambiguous intents
    try:
        resp = await litellm.acompletion(
            model="gemini/gemini-2.5-flash",
            messages=[
                {
                    "role": "system",
                    "content": _SYSTEM_PROMPT.format(traditions=", ".join(TRADITIONS)),
                },
                {"role": "user", "content": intent},
            ],
            max_tokens=100,
            temperature=0.0,
            api_key=api_key,
            timeout=10,
        )
        text = resp.choices[0].message.content.strip()
        from vulca._parse import parse_llm_json
        data = parse_llm_json(text)
        tradition = data.get("tradition", "default")
        confidence = float(data.get("confidence", 0.5))
        if tradition not in TRADITIONS:
            tradition = "default"
        return tradition, confidence
    except Exception as exc:
        logger.warning("Intent resolution failed, using default: %s", exc)
        return "default", 0.0


_KEYWORD_MAP: dict[str, list[str]] = {
    "chinese_xieyi": ["xieyi", "\u5199\u610f", "ink wash", "\u6c34\u58a8", "chinese ink", "freehand"],
    "chinese_gongbi": ["gongbi", "\u5de5\u7b14", "meticulous", "fine brushwork"],
    "western_academic": ["western", "academic", "renaissance", "oil painting", "realism"],
    "islamic_geometric": ["islamic", "geometric", "arabesque", "tessellation", "mosque"],
    "japanese_traditional": ["japanese", "ukiyo-e", "nihonga", "wabi-sabi", "\u65e5\u672c"],
    "watercolor": ["watercolor", "watercolour", "aquarelle"],
    "african_traditional": ["african", "mask", "ndop", "adinkra", "kente"],
    "south_asian": ["south asian", "mughal", "miniature", "rangoli", "mandala"],
}


def _keyword_match(intent: str) -> tuple[str, float]:
    """Fast keyword-based tradition matching."""
    lower = intent.lower()
    for tradition, keywords in _KEYWORD_MAP.items():
        for kw in keywords:
            if kw in lower:
                return tradition, 0.9
    return "default", 0.0
