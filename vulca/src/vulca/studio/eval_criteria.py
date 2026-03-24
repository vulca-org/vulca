"""Generate L1-L5 evaluation criteria from a Brief."""
from __future__ import annotations

import logging
from vulca.studio.brief import Brief

logger = logging.getLogger("vulca.studio")

_DEFAULT_CRITERIA = {
    "L1": "Composition, layout, spatial arrangement, visual clarity, and color harmony.",
    "L2": "Rendering quality, detail precision, technique fidelity, and craftsmanship.",
    "L3": "Fidelity to intended style, proper use of motifs/elements/terminology.",
    "L4": "Respectful representation, absence of constraint violations, coherent interpretation.",
    "L5": "Artistic depth, emotional resonance, aesthetic harmony, and intended mood.",
}


def generate_eval_criteria_sync(brief: Brief, *, use_llm: bool = True) -> dict[str, str]:
    if use_llm:
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(generate_eval_criteria(brief))
            loop.close()
            return result
        except Exception:
            logger.debug("LLM eval criteria generation failed, using fallback")
    return _fallback_criteria(brief)


async def generate_eval_criteria(brief: Brief) -> dict[str, str]:
    import os
    import litellm
    from vulca._parse import parse_llm_json

    summary = _brief_to_summary(brief)
    prompt = f"""Based on this creative brief, generate specific evaluation criteria for 5 art dimensions (L1-L5). Each should be concrete and measurable.

{summary}

Respond with ONLY JSON:
{{"L1": "<Visual Perception>", "L2": "<Technical Execution>", "L3": "<Cultural/Style Context>", "L4": "<Interpretation/Constraint>", "L5": "<Aesthetic/Emotional>"}}"""

    resp = await litellm.acompletion(
        model=os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024, temperature=0.3, timeout=30)
    data = parse_llm_json(resp.choices[0].message.content.strip())
    return {f"L{i}": str(data.get(f"L{i}", _DEFAULT_CRITERIA[f"L{i}"])) for i in range(1, 6)}


def _fallback_criteria(brief: Brief) -> dict[str, str]:
    criteria = dict(_DEFAULT_CRITERIA)
    known = [s.tradition for s in brief.style_mix if s.tradition]
    if known:
        try:
            from vulca.cultural.loader import get_tradition
            for tname in known:
                tc = get_tradition(tname)
                if tc and tc.terminology:
                    terms = ", ".join(t.term for t in tc.terminology[:4])
                    criteria["L3"] = f"Fidelity to {tname} tradition. Key techniques: {terms}."
                if tc and tc.taboos:
                    rules = "; ".join(t.rule for t in tc.taboos[:3])
                    criteria["L4"] = f"Respect constraints: {rules}."
        except Exception:
            pass
    if brief.must_have:
        criteria["L1"] = f"Must include: {', '.join(brief.must_have[:5])}. {criteria['L1']}"
    if brief.must_avoid:
        criteria["L4"] = f"Must avoid: {', '.join(brief.must_avoid[:5])}. {criteria['L4']}"
    if brief.mood:
        criteria["L5"] = f"Convey mood: {brief.mood}. {criteria['L5']}"
    if brief.composition.layout:
        criteria["L1"] = f"Layout: {brief.composition.layout}. {criteria['L1']}"
    return criteria


def _brief_to_summary(brief: Brief) -> str:
    parts = [f"Intent: {brief.intent}"]
    if brief.mood: parts.append(f"Mood: {brief.mood}")
    if brief.style_mix:
        parts.append(f"Style: {', '.join(s.tradition or s.tag for s in brief.style_mix)}")
    if brief.composition.layout: parts.append(f"Composition: {brief.composition.layout}")
    if brief.elements: parts.append(f"Elements: {', '.join(e.name for e in brief.elements[:6])}")
    if brief.must_have: parts.append(f"Must include: {', '.join(brief.must_have)}")
    if brief.must_avoid: parts.append(f"Must avoid: {', '.join(brief.must_avoid)}")
    return "\n".join(parts)
