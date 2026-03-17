"""Extra skill executors -- brand, audience, trend evaluation."""

from __future__ import annotations

import json
import logging

import litellm

from vulca.types import SkillResult

logger = logging.getLogger("vulca")

_SKILL_PROMPTS: dict[str, str] = {
    "brand": """\
Evaluate this image for brand consistency. Score four dimensions (0.0-1.0):
1. color_match -- How well colors align with typical brand palettes
2. typography -- Text/font quality and consistency
3. visual_identity -- Overall brand identity coherence
4. overall_coherence -- Unified brand message

Respond ONLY with JSON:
{{"color_match": <float>, "typography": <float>, "visual_identity": <float>,
  "overall_coherence": <float>, "summary": "<1-2 sentences>",
  "suggestions": ["<suggestion1>", "<suggestion2>"]}}""",
    "audience": """\
Evaluate this image for audience fit across demographics. Score each (0.0-1.0):
1. gen_z -- Appeal to Gen Z (18-25)
2. millennial -- Appeal to Millennials (26-40)
3. gen_x -- Appeal to Gen X (41-55)
4. boomer -- Appeal to Boomers (56+)

Respond ONLY with JSON:
{{"gen_z": <float>, "millennial": <float>, "gen_x": <float>, "boomer": <float>,
  "best_fit": "<demographic>", "summary": "<1-2 sentences>",
  "suggestions": ["<suggestion1>", "<suggestion2>"]}}""",
    "trend": """\
Evaluate this image for alignment with current design trends. Score each (0.0-1.0):
1. minimalism -- Clean, simple, less-is-more aesthetic
2. maximalism -- Bold, layered, more-is-more aesthetic
3. retro -- Nostalgic, vintage references
4. futuristic -- Forward-looking, tech-inspired
5. organic -- Natural, flowing, biomorphic forms

Respond ONLY with JSON:
{{"minimalism": <float>, "maximalism": <float>, "retro": <float>,
  "futuristic": <float>, "organic": <float>,
  "dominant_trend": "<trend_name>", "summary": "<1-2 sentences>",
  "suggestions": ["<suggestion1>", "<suggestion2>"]}}""",
}

_SKILL_WEIGHTS: dict[str, dict[str, float]] = {
    "brand": {"color_match": 0.25, "typography": 0.25, "visual_identity": 0.30, "overall_coherence": 0.20},
    "audience": {"gen_z": 0.25, "millennial": 0.25, "gen_x": 0.25, "boomer": 0.25},
    "trend": {"minimalism": 0.20, "maximalism": 0.20, "retro": 0.20, "futuristic": 0.20, "organic": 0.20},
}


async def run_skill(
    name: str,
    img_b64: str,
    mime: str,
    api_key: str,
) -> SkillResult:
    """Run a single skill evaluation and return a SkillResult."""
    prompt = _SKILL_PROMPTS.get(name)
    if not prompt:
        raise ValueError(f"Unknown skill: {name!r}. Available: {list(_SKILL_PROMPTS)}")

    resp = await litellm.acompletion(
        model="gemini/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                    {"type": "text", "text": "Evaluate this image."},
                ],
            },
        ],
        max_tokens=4096,
        temperature=0.1,
        api_key=api_key,
        timeout=30,
    )

    text = resp.choices[0].message.content.strip()
    from vulca._parse import parse_llm_json
    data = parse_llm_json(text)

    # Compute weighted score
    weights = _SKILL_WEIGHTS.get(name, {})
    score = 0.0
    for dim, w in weights.items():
        score += float(data.get(dim, 0.0)) * w

    return SkillResult(
        skill=name,
        score=round(score, 4),
        summary=data.get("summary", ""),
        details={k: v for k, v in data.items() if k not in ("summary", "suggestions")},
        suggestions=data.get("suggestions", []),
    )
