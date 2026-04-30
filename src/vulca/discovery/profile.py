"""Rule-based taste profile inference for visual discovery."""
from __future__ import annotations

from vulca.discovery.terms import extract_terms_from_intent
from vulca.discovery.types import TasteProfile


DOMAIN_HINTS = {
    "packaging": {"packaging", "label", "bottle", "box", "tea"},
    "poster": {"poster", "exhibition", "event"},
    "brand_visual": {"brand", "campaign", "launch"},
    "editorial_cover": {"cover", "magazine", "book"},
    "photography_brief": {"photo", "photography", "shoot"},
    "hero_visual_for_ui": {"hero", "splash"},
}

TRADITION_HINTS = {
    "chinese_xieyi": {
        "ink",
        "liubai",
        "liu bai",
        "xieyi",
        "negative space",
        "水墨",
        "留白",
    },
    "chinese_gongbi": {"gongbi", "fine line", "工笔"},
    "japanese_traditional": {"ukiyo", "wabi", "sabi", "japanese"},
    "brand_design": {"brand", "logo", "campaign"},
    "photography": {"photo", "camera", "shoot"},
}


def _pick_domain(intent: str) -> str:
    lowered = intent.lower()
    for domain, hints in DOMAIN_HINTS.items():
        if any(hint in lowered for hint in hints):
            return domain
    return "illustration"


def _pick_traditions(intent: str) -> list[str]:
    lowered = intent.lower()
    traditions = [
        tradition
        for tradition, hints in TRADITION_HINTS.items()
        if any(hint in lowered for hint in hints)
    ]
    return traditions or ["brand_design"]


def infer_taste_profile(slug: str, intent: str) -> TasteProfile:
    traditions = _pick_traditions(intent)
    terms: list[str] = []
    for tradition in traditions:
        for term in extract_terms_from_intent(intent, tradition):
            if term not in terms:
                terms.append(term)
    if not terms and "chinese_xieyi" in traditions:
        terms.append("reserved white space")

    mood = []
    lowered = intent.lower()
    if "premium" in lowered or "luxury" in lowered:
        mood.append("premium")
    if "quiet" in lowered or "restrained" in lowered:
        mood.append("quiet")

    return TasteProfile(
        slug=slug,
        initial_intent=intent,
        domain_primary=_pick_domain(intent),
        candidate_traditions=traditions,
        culture_terms=terms,
        mood=mood,
        confidence="med" if terms else "low",
    )
