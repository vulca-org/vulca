"""Expand cultural and aesthetic terms into operational visual guidance."""
from __future__ import annotations

import re
from typing import Any

from vulca.cultural.loader import get_tradition, get_tradition_guide


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", value.lower())


TERM_VISUAL_OPS: dict[str, dict[str, Any]] = {
    "reserved white space": {
        "composition": (
            "large negative space, small off-center focal subject, "
            "clear figure-ground relationship"
        ),
        "color": "warm paper whites, restrained ink or muted accent colors",
        "texture": "subtle paper grain, quiet low-detail regions",
        "symbol_strategy": (
            "empty space should imply atmosphere or breath, not look unfinished"
        ),
        "avoid": [
            "empty background with no intentional balance",
            "generic minimalism unrelated to subject",
            "busy ornament",
        ],
        "evaluation_focus": {
            "L1": "negative space supports the focal hierarchy",
            "L2": "blank regions have controlled edges and stable balance",
            "L3": (
                "liubai connects to the chosen tradition rather than generic "
                "minimalism"
            ),
            "L4": "emptiness is a compositional argument",
            "L5": "emptiness contributes resonance, breath, and implied meaning",
        },
    },
    "spirit resonance and vitality": {
        "composition": "asymmetrical rhythm with clear visual flow",
        "color": "restrained tonal range with one living accent if needed",
        "texture": "brush or material energy should feel intentional",
        "symbol_strategy": "express living rhythm through movement and spacing",
        "avoid": [
            "static decorative imitation",
            "over-rendered realism with no expressive rhythm",
        ],
        "evaluation_focus": {
            "L1": "viewer can follow the image rhythm",
            "L2": "marks or materials carry energy without chaos",
            "L3": "the term is not reduced to surface ornament",
            "L4": "visual flow supports interpretation",
            "L5": "the image has living spirit beyond literal depiction",
        },
    },
}

GENERIC_VISUAL_OPS = {
    "composition": "clear focal hierarchy, intentional spacing, readable silhouette",
    "color": "limited palette aligned to the project mood",
    "texture": "material treatment supports the concept",
    "symbol_strategy": "prefer specific visual behavior over decorative labels",
    "avoid": [
        "generic ai aesthetic",
        "literal cliché symbolism",
        "unexplained culture mixing",
    ],
    "evaluation_focus": {
        "L1": "visual perception is clear",
        "L2": "execution supports the stated style",
        "L3": "cultural references are grounded",
        "L4": "interpretation matches the project intent",
        "L5": "the aesthetic idea has depth beyond styling",
    },
}


def _term_index(tradition: str) -> dict[str, dict[str, Any]]:
    config = get_tradition(tradition)
    index: dict[str, dict[str, Any]] = {}
    if config is not None:
        for term in config.terminology:
            entry = {
                "term": term.term,
                "term_zh": term.term_zh,
                "definition": term.definition,
                "category": term.category,
                "aliases": list(term.aliases),
            }
            labels = [
                entry["term"],
                entry["term_zh"],
                *entry["aliases"],
            ]
            for label in labels:
                if label:
                    index[_norm(label)] = entry
        return index

    guide = get_tradition_guide(tradition) or {}
    for entry in guide.get("terminology", []):
        if "term_zh" not in entry and "translation" in entry:
            entry = {**entry, "term_zh": entry["translation"]}
        labels = [
            str(entry.get("term", "")),
            str(entry.get("term_zh", "")),
            *[str(alias) for alias in entry.get("aliases", [])],
        ]
        for label in labels:
            if label:
                index[_norm(label)] = entry
    return index


def _entry_for_term(tradition: str, term: str) -> dict[str, Any] | None:
    return _term_index(tradition).get(_norm(term))


def _visual_ops_for_term(term: str) -> dict[str, Any]:
    return TERM_VISUAL_OPS.get(term, GENERIC_VISUAL_OPS)


def expand_terms(tradition: str, terms: list[str]) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for raw_term in terms:
        entry = _entry_for_term(tradition, raw_term)
        canonical = str(entry.get("term", raw_term)) if entry else raw_term
        ops = _visual_ops_for_term(canonical)
        expanded.append(
            {
                "term": canonical,
                "term_zh": str(entry.get("term_zh", "")) if entry else "",
                "definition": entry.get("definition", "") if entry else "",
                "category": (
                    str(entry.get("category", "aesthetic")) if entry else "aesthetic"
                ),
                "visual_ops": {
                    "composition": ops["composition"],
                    "color": ops["color"],
                    "texture": ops["texture"],
                    "symbol_strategy": ops["symbol_strategy"],
                    "avoid": list(ops["avoid"]),
                },
                "evaluation_focus": dict(ops["evaluation_focus"]),
            }
        )
    return expanded


def extract_terms_from_intent(intent: str, tradition: str) -> list[str]:
    intent_key = _norm(intent)
    terms: list[str] = []
    for entry in _term_index(tradition).values():
        labels = [str(entry.get("term", "")), str(entry.get("term_zh", ""))]
        labels.extend(str(alias) for alias in entry.get("aliases", []))
        if any(label and _norm(label) in intent_key for label in labels):
            term = str(entry.get("term", ""))
            if term and term not in terms:
                terms.append(term)
    return terms
