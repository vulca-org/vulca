"""Content-lock helpers for caption-faithful generation and evaluation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ContentLock:
    """Explicit user-requested content that should survive style optimization."""

    original_intent: str
    required_subjects: list[str] = field(default_factory=list)
    required_text_elements: list[str] = field(default_factory=list)
    required_surface: list[str] = field(default_factory=list)
    required_style_attributes: list[str] = field(default_factory=list)
    required_mood: list[str] = field(default_factory=list)

    @property
    def has_requirements(self) -> bool:
        return any(
            (
                self.required_subjects,
                self.required_text_elements,
                self.required_surface,
                self.required_style_attributes,
                self.required_mood,
            )
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "original_intent": self.original_intent,
            "required_subjects": list(self.required_subjects),
            "required_text_elements": list(self.required_text_elements),
            "required_surface": list(self.required_surface),
            "required_style_attributes": list(self.required_style_attributes),
            "required_mood": list(self.required_mood),
        }


def content_lock_from_dict(data: dict[str, Any] | ContentLock) -> ContentLock:
    if isinstance(data, ContentLock):
        return data
    allowed = {
        "original_intent",
        "required_subjects",
        "required_text_elements",
        "required_surface",
        "required_style_attributes",
        "required_mood",
    }
    cleaned = {key: value for key, value in data.items() if key in allowed}
    return ContentLock(
        original_intent=str(cleaned.get("original_intent") or ""),
        required_subjects=_as_string_list(cleaned.get("required_subjects")),
        required_text_elements=_as_string_list(cleaned.get("required_text_elements")),
        required_surface=_as_string_list(cleaned.get("required_surface")),
        required_style_attributes=_as_string_list(cleaned.get("required_style_attributes")),
        required_mood=_as_string_list(cleaned.get("required_mood")),
    )


def extract_content_lock(intent: str) -> ContentLock:
    """Extract explicit visual requirements from a short caption-like intent.

    This is intentionally conservative: it locks concrete, named objects and
    visible text/material requirements, but leaves broad style words to the
    tradition guidance unless they are clearly phrased as explicit attributes.
    """
    text = " ".join(intent.strip().split())
    lower = text.lower()

    subjects = _extract_subjects(text)
    subjects = _replace_known_subjects(subjects, lower)
    subjects.extend(_extract_keyword_subjects(lower))

    text_elements: list[str] = []
    if re.search(r"\bcircular calligraphy panel\b", lower):
        text_elements.append("circular calligraphy panel")
    elif re.search(r"\bvertical chinese calligraphy\b", lower):
        text_elements.append("vertical Chinese calligraphy")
    elif re.search(r"\bcalligraphy along the side\b", lower):
        text_elements.append("calligraphy along the side")
    elif re.search(r"\bcalligraphy\b", lower):
        text_elements.append("calligraphy")
    if re.search(r"\bred seals?\b", lower):
        text_elements.append("red seals")

    surface: list[str] = []
    if re.search(r"\baged paper\b", lower):
        surface.append("aged paper")
    if re.search(r"\bgraph paper\b", lower):
        surface.append("graph paper")
    if re.search(r"\bpale beige silk ground\b", lower):
        surface.append("pale beige silk ground")
    if re.search(r"\bornate pale patterned border\b", lower):
        surface.append("ornate pale patterned border")

    style_attributes: list[str] = []
    if re.search(r"\bgongbi vertical hanging scroll\b", lower):
        style_attributes.append("Gongbi vertical hanging scroll")
    elif re.search(r"\bvertical hanging scroll\b", lower):
        style_attributes.append("vertical hanging scroll")
    if re.search(r"\bgongbi album leaf\b", lower):
        style_attributes.append("Gongbi album leaf")
    if re.search(r"\brectangular frame\b", lower):
        style_attributes.append("rectangular frame")
    if re.search(r"\bmonochrome pencil style\b", lower):
        style_attributes.append("monochrome pencil style")
    if re.search(r"\bdelicate linework\b", lower):
        style_attributes.append("delicate linework")
    if re.search(r"\bmuted brown tones\b", lower):
        style_attributes.append("muted brown tones")
    if re.search(r"\bsparse brushwork\b", lower):
        style_attributes.append("sparse brushwork")

    mood: list[str] = []
    if re.search(r"\bcalm scholarly composition\b", lower):
        mood.append("calm scholarly composition")

    return ContentLock(
        original_intent=text,
        required_subjects=subjects,
        required_text_elements=_dedupe(text_elements),
        required_surface=_dedupe(surface),
        required_style_attributes=_dedupe(style_attributes),
        required_mood=_dedupe(mood),
    )


def build_content_lock_prompt(lock: ContentLock) -> str:
    """Build generation instructions that make explicit content non-negotiable."""
    if not lock.has_requirements:
        return ""

    lines = [
        "NON-NEGOTIABLE CONTENT REQUIREMENTS:",
        (
            "The following requirements come from the user's explicit request "
            "and must be satisfied before style optimization."
        ),
    ]
    if lock.required_subjects:
        lines.append(f"- Required subjects: {', '.join(lock.required_subjects)}.")
    if lock.required_text_elements:
        lines.append(
            f"- Required text/seal elements: {', '.join(lock.required_text_elements)}."
        )
    if lock.required_surface:
        lines.append(f"- Required surface/material: {', '.join(lock.required_surface)}.")
    if lock.required_style_attributes:
        lines.append(
            f"- Required style attributes: {', '.join(lock.required_style_attributes)}."
        )
    if lock.required_mood:
        lines.append(f"- Required mood/composition: {', '.join(lock.required_mood)}.")
    lines.append(
        "Do not replace these subjects with mountains, generic landscapes, "
        "or unrelated tradition prototypes."
    )
    lines.append(
        "Do not render sample IDs, filenames, watermarks, large labels, gallery "
        "walls, exhibition labels, framed museum installations, or photographed "
        "artwork mockups unless the user explicitly requested them."
    )
    lines.append(
        "If any required subject is absent, the image is a failed response even "
        "if the cultural style is strong."
    )
    return "\n".join(lines)


def build_content_fidelity_prompt(lock: ContentLock) -> str:
    """Build VLM scoring instructions for explicit content presence checks."""
    if not lock.has_requirements:
        return ""

    lines = [
        "CONTENT FIDELITY CHECK:",
        (
            "Before final scoring, verify whether the artwork visibly contains "
            "the user's non-negotiable content requirements."
        ),
    ]
    if lock.required_subjects:
        lines.append(f"- Required subjects: {', '.join(lock.required_subjects)}")
    if lock.required_text_elements:
        lines.append(
            f"- Required text/seal elements: {', '.join(lock.required_text_elements)}"
        )
    if lock.required_surface:
        lines.append(f"- Required surface/material: {', '.join(lock.required_surface)}")
    if lock.required_style_attributes:
        lines.append(
            f"- Required style attributes: {', '.join(lock.required_style_attributes)}"
        )
    lines.extend(
        [
            (
                "Also check for forbidden visual artifacts: visible sample IDs, "
                "filenames, watermarks, large labels, gallery walls, exhibition "
                "labels, framed museum installations, and photographed artwork mockups."
            ),
            "Add these exact fields to the JSON inside <scoring>:",
            '"missing_required_subjects": [strings copied exactly from the required subjects list],',
            '"missing_required_text_elements": [strings copied exactly from the required text/seal list],',
            '"missing_required_surface": [strings copied exactly from the required surface/material list].',
            '"missing_required_style_attributes": [strings copied exactly from the required style attributes list],',
            '"forbidden_visual_artifacts": [visible forbidden artifacts, or an empty list].',
            "Use an empty list when every item in a category is visible or no forbidden artifact is present.",
        ]
    )
    return "\n".join(lines)


def build_content_fidelity_gate(
    lock: ContentLock | dict[str, Any],
    scoring_data: dict[str, Any],
) -> dict[str, list[str]]:
    """Create deterministic gate data from VLM missing-item fields."""
    content_lock = content_lock_from_dict(lock) if isinstance(lock, dict) else lock
    return {
        "required_subjects": list(content_lock.required_subjects),
        "missing_required_subjects": _as_string_list(
            scoring_data.get("missing_required_subjects")
        ),
        "required_text_elements": list(content_lock.required_text_elements),
        "missing_required_text_elements": _as_string_list(
            scoring_data.get("missing_required_text_elements")
        ),
        "required_surface": list(content_lock.required_surface),
        "missing_required_surface": _as_string_list(
            scoring_data.get("missing_required_surface")
        ),
        "required_style_attributes": list(content_lock.required_style_attributes),
        "missing_required_style_attributes": _as_string_list(
            scoring_data.get("missing_required_style_attributes")
        ),
        "forbidden_visual_artifacts": _as_string_list(
            scoring_data.get("forbidden_visual_artifacts")
        ),
    }


def apply_content_fidelity_gate(result: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    """Cap high scores when required caption content is known missing."""
    missing_subjects = _as_string_list(gate.get("missing_required_subjects"))
    missing_text = _as_string_list(gate.get("missing_required_text_elements"))
    missing_surface = _as_string_list(gate.get("missing_required_surface"))
    missing_style = _as_string_list(gate.get("missing_required_style_attributes"))
    forbidden_artifacts = _as_string_list(gate.get("forbidden_visual_artifacts"))

    if not (
        missing_subjects
        or missing_text
        or missing_surface
        or missing_style
        or forbidden_artifacts
    ):
        return result

    updated = dict(result)
    scores = dict(updated.get("scores") or {})
    for key in ("L1", "L3", "L4", "L5"):
        scores[key] = min(float(scores.get(key, 0.0)), 0.25)
    updated["scores"] = scores
    updated["weighted_total"] = min(float(updated.get("weighted_total", 0.0)), 0.25)

    rationale_parts: list[str] = []
    if missing_subjects:
        rationale_parts.append(f"Missing required subjects: {', '.join(missing_subjects)}")
    if missing_text:
        rationale_parts.append(
            f"Missing required text elements: {', '.join(missing_text)}"
        )
    if missing_surface:
        rationale_parts.append(
            f"Missing required surface/material: {', '.join(missing_surface)}"
        )
    if missing_style:
        rationale_parts.append(
            f"Missing required style attributes: {', '.join(missing_style)}"
        )
    if forbidden_artifacts:
        rationale_parts.append(
            f"Forbidden visual artifacts: {', '.join(forbidden_artifacts)}"
        )
    rationales = dict(updated.get("rationales") or {})
    rationales["content_fidelity"] = "; ".join(rationale_parts)
    updated["rationales"] = rationales

    risk_flags = list(updated.get("risk_flags") or [])
    if "content_fidelity_failed" not in risk_flags:
        risk_flags.append("content_fidelity_failed")
    updated["risk_flags"] = risk_flags
    updated["content_fidelity_gate"] = dict(gate)
    return updated


def _extract_subjects(text: str) -> list[str]:
    match = re.search(
        r"\b(?:of|showing|featuring|depicting)\s+(.+?)(?:\s+"
        r"(?:beside|with|on|under|against|in|at|near|over|around)\b|,\s+with\b|$)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return []

    segment = match.group(1)
    pieces = re.split(r",\s*(?:and\s+)?|\s+and\s+", segment)
    subjects = []
    for piece in pieces:
        normalized = _clean_subject(piece)
        if normalized:
            subjects.append(normalized)
    return _dedupe(subjects)


def _replace_known_subjects(subjects: list[str], lower: str) -> list[str]:
    known: list[str] = []
    if re.search(r"\bbamboo\b", lower):
        known.append("bamboo")
    if re.search(r"\borchid grasses?\b", lower):
        known.append("orchid grasses")
    elif re.search(r"\borchids?\b", lower):
        known.append("orchids")
    if known:
        remaining = [
            subject
            for subject in subjects
            if "bamboo" not in subject and "orchid" not in subject
        ]
        return _dedupe([*known, *remaining])
    return subjects


def _extract_keyword_subjects(lower: str) -> list[str]:
    subjects: list[str] = []
    for pattern, label in (
        (r"\blotus blossoms?\b", "lotus blossoms"),
        (r"\bslender stems?\b", "slender stems"),
        (r"\bsmall leaves\b", "small leaves"),
        (r"\bdense tree-like network\b", "dense tree-like network"),
        (r"\bsmall heart\b", "small heart"),
        (r"\bgeometric marks\b", "geometric marks"),
        (r"\bsparse branches\b", "sparse branches"),
    ):
        if re.search(pattern, lower):
            subjects.append(label)
    if re.search(r"\bhand-drawn branching lines\b", lower):
        subjects.append("hand-drawn branching lines")
    elif re.search(r"\bbranching lines\b", lower):
        subjects.append("branching lines")
    if re.search(r"\bfinely detailed bird\b", lower):
        subjects.append("finely detailed bird")
    elif re.search(r"\bsmall bird\b", lower):
        subjects.append("small bird")
    elif re.search(r"\bbird\b", lower):
        subjects.append("bird")
    return _dedupe(subjects)


def _clean_subject(value: str) -> str:
    value = value.strip(" .,:;")
    value = re.sub(r"^(?:a|an|the)\s+", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\b(?:delicate|detailed|high-quality)\s+", "", value, flags=re.IGNORECASE)
    return " ".join(value.split())


def _as_string_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    return []


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result
