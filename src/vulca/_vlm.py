"""VLM Critic -- core L1-L5 image evaluation via Gemini Vision."""

from __future__ import annotations

import json
import logging

import litellm

logger = logging.getLogger("vulca")

_SYSTEM_PROMPT = """\
You are VULCA, a cultural-aware art evaluation system. Evaluate the given \
artwork image across five dimensions (L1-L5), each scored from 0.0 to 1.0.

## Dimension Definitions

- **L1 (Visual Perception)**: Composition, layout, spatial arrangement, visual \
clarity, color harmony, and overall visual impact.
- **L2 (Technical Execution)**: Rendering quality, detail precision, technique \
fidelity, medium-appropriate execution, and craftsmanship.
- **L3 (Cultural Context)**: Fidelity to cultural tradition, proper use of \
tradition-specific motifs/elements/terminology, adherence to canonical conventions.
- **L4 (Critical Interpretation)**: Respectful representation, absence of taboo \
violations, cultural sensitivity, appropriate contextual framing.
- **L5 (Philosophical Aesthetics)**: Artistic depth, emotional resonance, \
spiritual qualities, aesthetic harmony, and philosophical alignment with the tradition.

## Cultural Tradition: {tradition}

{tradition_guidance}

## Instructions

Score each dimension 0.0-1.0. Provide a brief rationale (1-2 sentences) for each.

Respond with ONLY a JSON object:
{{
    "L1": <float>, "L1_rationale": "<string>",
    "L2": <float>, "L2_rationale": "<string>",
    "L3": <float>, "L3_rationale": "<string>",
    "L4": <float>, "L4_rationale": "<string>",
    "L5": <float>, "L5_rationale": "<string>"
}}
"""

_TRADITION_GUIDANCE: dict[str, str] = {
    "default": "Apply general art evaluation principles. No specific cultural tradition.",
    "chinese_xieyi": (
        "Xieyi (\u5199\u610f) freehand ink wash painting. Prioritize: spontaneity of brushwork, "
        "use of blank space (\u7559\u767d), ink gradation (\u58a8\u5206\u4e94\u8272), qi-yun (\u6c14\u97f5) spiritual resonance, "
        "and harmony between poetry-calligraphy-painting-seal (\u8bd7\u4e66\u753b\u5370)."
    ),
    "chinese_gongbi": (
        "Gongbi (\u5de5\u7b14) meticulous painting. Prioritize: precision of line work, "
        "layered color application, fine detail rendering, and adherence to traditional subjects."
    ),
    "western_academic": (
        "Western academic tradition. Prioritize: anatomical accuracy, perspective, "
        "chiaroscuro, compositional balance, and narrative clarity."
    ),
    "islamic_geometric": (
        "Islamic geometric art. Prioritize: mathematical precision of patterns, "
        "symmetry, tessellation correctness, arabesque flow, and avoidance of figural representation."
    ),
    "japanese_traditional": (
        "Japanese traditional art (Nihonga/Ukiyo-e). Prioritize: flat color areas, "
        "bold outlines, seasonal motifs, wabi-sabi aesthetics, and mono no aware sentiment."
    ),
    "watercolor": (
        "Watercolor painting. Prioritize: transparency of washes, wet-in-wet technique, "
        "luminosity, paper-as-white usage, and freshness of application."
    ),
    "african_traditional": (
        "African traditional art. Prioritize: symbolic abstraction, mask conventions, "
        "community/ritual significance, material authenticity, and spiritual function."
    ),
    "south_asian": (
        "South Asian art traditions. Prioritize: miniature painting conventions, "
        "Mughal detail, color symbolism, narrative scenes, and decorative borders."
    ),
}


async def score_image(
    img_b64: str,
    mime: str,
    subject: str,
    tradition: str,
    api_key: str,
) -> dict:
    """Call Gemini Vision to score an image on L1-L5.

    Returns a dict with L1-L5 scores and rationales, or fallback zeros on error.
    """
    tradition_guidance = _TRADITION_GUIDANCE.get(tradition, _TRADITION_GUIDANCE["default"])
    system_msg = _SYSTEM_PROMPT.format(
        tradition=tradition.replace("_", " ").title(),
        tradition_guidance=tradition_guidance,
    )

    user_parts = [
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
    ]
    if subject:
        user_parts.append({"type": "text", "text": f"Subject/context: {subject}"})
    else:
        user_parts.append({"type": "text", "text": "Evaluate this artwork."})

    try:
        resp = await litellm.acompletion(
            model="gemini/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_parts},
            ],
            max_tokens=4096,
            temperature=0.1,
            api_key=api_key,
            timeout=55,
        )
        text = resp.choices[0].message.content.strip()
        from vulca._parse import parse_llm_json
        data = parse_llm_json(text)

        # Validate and clamp scores
        for level in ("L1", "L2", "L3", "L4", "L5"):
            if level in data:
                data[level] = max(0.0, min(1.0, float(data[level])))
            else:
                data[level] = 0.0
            if f"{level}_rationale" not in data:
                data[f"{level}_rationale"] = ""

        return data

    except Exception as exc:
        logger.error("VLM scoring failed: %s", exc)
        return {
            "L1": 0.0, "L1_rationale": f"Scoring failed: {exc}",
            "L2": 0.0, "L2_rationale": "",
            "L3": 0.0, "L3_rationale": "",
            "L4": 0.0, "L4_rationale": "",
            "L5": 0.0, "L5_rationale": "",
            "error": str(exc),
        }
