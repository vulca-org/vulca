"""VLM Critic -- core L1-L5 image evaluation via Gemini Vision."""

from __future__ import annotations

import json
import logging
import os

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

Score each dimension 0.0-1.0. For each dimension provide:
1. **rationale**: What you observe (1-2 sentences).
2. **suggestion**: A specific, actionable improvement tip if the artist wants to \
align more closely with the tradition. Include concrete techniques, terms, or \
compositional advice (1 sentence). If the work already excels, suggest how to \
push it further.
3. **deviation_type**: Classify as one of:
   - "traditional": follows the tradition's conventions closely
   - "intentional_departure": appears to deliberately deviate (e.g., mixing \
modern elements with traditional forms)
   - "experimental": significantly outside the tradition's scope

Respond with ONLY a JSON object:
{{
    "L1": <float>, "L1_rationale": "<string>", "L1_suggestion": "<string>", "L1_deviation_type": "<string>",
    "L2": <float>, "L2_rationale": "<string>", "L2_suggestion": "<string>", "L2_deviation_type": "<string>",
    "L3": <float>, "L3_rationale": "<string>", "L3_suggestion": "<string>", "L3_deviation_type": "<string>",
    "L4": <float>, "L4_rationale": "<string>", "L4_suggestion": "<string>", "L4_deviation_type": "<string>",
    "L5": <float>, "L5_rationale": "<string>", "L5_suggestion": "<string>", "L5_deviation_type": "<string>"
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


def _load_evolved_context() -> dict | None:
    """Load evolved_context.json if available."""
    import os
    from pathlib import Path

    try:
        candidates = []
        env_path = os.environ.get("VULCA_EVOLVED_CONTEXT")
        if env_path:
            candidates.append(Path(env_path))
        vlm_path = Path(__file__).resolve()
        # Backend copy layout
        candidates.append(vlm_path.parent.parent / "app" / "prototype" / "data" / "evolved_context.json")
        # Monorepo layout
        candidates.append(vlm_path.parent.parent.parent.parent / "wenxin-backend" / "app" / "prototype" / "data" / "evolved_context.json")

        for path in candidates:
            if path.is_file():
                return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        logger.debug("Failed to load evolved context")
    return None


def _build_tradition_guidance(tradition: str) -> str:
    """Build rich tradition guidance from YAML data, evolved context, and few-shot examples."""
    base = _TRADITION_GUIDANCE.get(tradition, _TRADITION_GUIDANCE["default"])

    try:
        from vulca.cultural.loader import get_tradition
        tc = get_tradition(tradition)
        if tc is None:
            return base

        parts = [base]

        # Inject terminology
        if tc.terminology:
            terms_text = "\n".join(
                f"  - **{t.term}** ({t.term_zh}): {t.definition if isinstance(t.definition, str) else t.definition.get('en', '')}"
                for t in tc.terminology[:8]
            )
            parts.append(f"\n### Key Cultural Terminology\n{terms_text}")

        # Inject taboos
        if tc.taboos:
            taboos_text = "\n".join(
                f"  - ⚠️ {t.rule}" + (f" — {t.explanation}" if t.explanation else "")
                for t in tc.taboos
            )
            parts.append(f"\n### Evaluation Taboos (MUST respect)\n{taboos_text}")

        # Inject evolved weight guidance + few-shot examples
        evolved = _load_evolved_context()
        if evolved:
            _inject_evolved_guidance(parts, tradition, evolved)

        return "\n".join(parts)
    except Exception:
        logger.debug("Tradition guidance fallback for %s", tradition)
        return base


_L_LABELS = {
    "L1": "Visual Perception", "L2": "Technical Execution",
    "L3": "Cultural Context", "L4": "Critical Interpretation",
    "L5": "Philosophical Aesthetics",
}

_DIM_NAME_TO_L = {
    "visual_perception": "L1", "technical_analysis": "L2",
    "cultural_context": "L3", "critical_interpretation": "L4",
    "philosophical_aesthetic": "L5",
}


def _inject_evolved_guidance(parts: list[str], tradition: str, evolved: dict) -> None:
    """Inject evolved weights and few-shot examples into the prompt."""
    # 1. Evolved weight emphasis — tell the VLM which dimensions matter most
    tw = evolved.get("tradition_weights", {}).get(tradition)
    if tw and isinstance(tw, dict):
        weights_l = {_DIM_NAME_TO_L.get(k, k): v for k, v in tw.items() if _DIM_NAME_TO_L.get(k)}
        if weights_l:
            ranked = sorted(weights_l.items(), key=lambda x: x[1], reverse=True)
            emphasis = ", ".join(f"{k} ({_L_LABELS.get(k, k)}) {v:.0%}" for k, v in ranked)
            parts.append(f"\n### Dimension Weights (from system evolution)\nPrioritize by weight: {emphasis}")

    # 2. Few-shot reference examples — calibrate scoring
    fse = evolved.get("few_shot_examples", [])
    tradition_examples = [ex for ex in fse if ex.get("tradition") == tradition][:2]
    if tradition_examples:
        examples_text = "\n".join(
            f"  - \"{ex.get('subject', 'N/A')}\" — overall {ex.get('score', 0):.2f}"
            + (f" (strengths: {', '.join(ex['key_strengths'])})" if ex.get('key_strengths') else "")
            for ex in tradition_examples
        )
        parts.append(f"\n### Reference Benchmarks (high-scoring works in this tradition)\n{examples_text}")

    # 3. Tradition-specific insights from evolution
    ti = evolved.get("tradition_insights", {}).get(tradition)
    if ti and isinstance(ti, str) and len(ti) < 300:
        parts.append(f"\n### Evolved Insight\n{ti}")


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
    tradition_guidance = _build_tradition_guidance(tradition)
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
            model=os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash"),
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

        # Validate and clamp scores, ensure all fields present
        _VALID_DEVIATION_TYPES = {"traditional", "intentional_departure", "experimental"}
        for level in ("L1", "L2", "L3", "L4", "L5"):
            if level in data:
                data[level] = max(0.0, min(1.0, float(data[level])))
            else:
                data[level] = 0.0
            if f"{level}_rationale" not in data:
                data[f"{level}_rationale"] = ""
            if f"{level}_suggestion" not in data:
                data[f"{level}_suggestion"] = ""
            if f"{level}_deviation_type" not in data:
                data[f"{level}_deviation_type"] = "traditional"
            elif data[f"{level}_deviation_type"] not in _VALID_DEVIATION_TYPES:
                data[f"{level}_deviation_type"] = "traditional"

        return data

    except Exception as exc:
        logger.error("VLM scoring failed: %s", exc)
        fallback: dict = {"error": str(exc)}
        for level in ("L1", "L2", "L3", "L4", "L5"):
            fallback[level] = 0.0
            fallback[f"{level}_rationale"] = f"Scoring failed: {exc}" if level == "L1" else ""
            fallback[f"{level}_suggestion"] = ""
            fallback[f"{level}_deviation_type"] = "traditional"
        return fallback
