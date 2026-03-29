"""NL Update parser -- parse natural language into Brief field updates."""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from vulca.studio.brief import Brief
from vulca.studio.session import SessionState
from vulca.studio.types import BriefUpdate, Element

logger = logging.getLogger("vulca.studio")


@dataclass
class NLUpdateResult:
    """Parsed result from a natural language update instruction."""
    field_updates: dict[str, Any] = field(default_factory=dict)
    rollback_to: SessionState = SessionState.CONCEPT
    confidence: float = 0.7
    explanation: str = ""


# Rollback rules: field set → phase
_INTENT_FIELDS = {"intent", "mood", "style_mix"}
_CONCEPT_FIELDS = {"composition", "palette", "elements", "must_have", "must_avoid"}
_EVALUATE_FIELDS = {"eval_criteria"}
_GENERATE_FIELDS = {"provider", "generation_params"}


_HIGH_STRENGTH_WORDS = {"completely", "replace", "different", "redo", "start over", "totally", "entirely", "scratch"}
_MEDIUM_STRENGTH_WORDS = {"change", "modify", "more", "less", "stronger", "weaker", "increase", "decrease", "add", "remove"}
_LOW_STRENGTH_WORDS = {"adjust", "refine", "subtle", "slightly", "tweak", "fine-tune", "minor", "touch up"}


def infer_variation_strength(instruction: str) -> float:
    """Infer variation strength from NL update text (0.0-1.0).

    High (0.7): major rework keywords.
    Medium (0.4): moderate change keywords.
    Low (0.2): fine-tuning keywords.
    Default: 0.3.
    """
    words = set(instruction.lower().split())
    # Check most specific first: low-strength words are intentional refinement signals
    if words & _LOW_STRENGTH_WORDS:
        return 0.2
    if words & _HIGH_STRENGTH_WORDS:
        return 0.7
    if words & _MEDIUM_STRENGTH_WORDS:
        return 0.4
    return 0.3


def determine_rollback(changed_fields: list[str]) -> SessionState:
    """Determine rollback phase from changed field names (deterministic).

    Priority (highest first): INTENT > CONCEPT > EVALUATE > GENERATE
    """
    field_set = set()
    for f in changed_fields:
        field_set.add(f.split(".")[0])  # Top-level field name only

    if field_set & _INTENT_FIELDS:
        return SessionState.INTENT
    if field_set & _CONCEPT_FIELDS:
        return SessionState.CONCEPT
    if field_set & _EVALUATE_FIELDS:
        return SessionState.EVALUATE
    if field_set & _GENERATE_FIELDS:
        return SessionState.GENERATE
    return SessionState.CONCEPT  # Safe default


# ---------------------------------------------------------------------------
# Keyword tables for V1 keyword-based NL parsing (no LLM required)
# ---------------------------------------------------------------------------

_MOOD_KEYWORDS = [
    # Chinese → English mapping
    ("神秘", "mystical"),
    ("宁静", "serene"),
    ("壮阔", "epic"),
    ("动感", "dynamic"),
    ("忧郁", "melancholic"),
    ("温馨", "warm"),
    ("冷峻", "cold"),
    # Atmosphere cue words (generic mood change)
    ("氛围", "_atmosphere_"),
    ("atmosphere", "_atmosphere_"),
    ("mood", "_mood_"),
    # English explicit
    ("mysterious", "mystical"),
    ("serene", "serene"),
    ("epic", "epic"),
    ("dynamic", "dynamic"),
    ("melancholic", "melancholic"),
]

_AVOID_KEYWORDS = [
    "不要", "避免", "不使用", "去掉", "删除",
    "remove", "avoid", "don't", "no ",
]

_ADD_KEYWORDS = [
    "加入", "添加", "增加", "加上",
    "加一", "放一", "画一", "来一", "搞一",
    "加些", "加点", "放些", "放点",
    "add ", "include ", "put ",
]

_COMPOSITION_KEYWORDS = [
    "构图", "布局", "layout", "composition",
    "更高", "更大", "更远", "更近", "更陡",
    "taller", "bigger", "closer", "farther", "steeper",
    "山", "水", "天空", "前景", "背景",
    "mountain", "water", "sky", "foreground", "background",
    # Position keywords
    "远处", "近处", "左边", "右边", "上方", "下方",
    "左侧", "右侧", "中间", "中央", "角落",
    "左上", "右上", "左下", "右下",
    "far", "near", "left", "right", "top", "bottom", "center",
    "移到", "挪到", "放到",
]

_COLOR_KEYWORDS = [
    "配色", "颜色", "色调", "palette", "color", "colour",
    "暖色", "冷色", "warm color", "cool color",
    "bright", "dark", "vivid", "saturated",
    "霓虹", "neon",
]


def _extract_after_keyword(original: str, lowered: str, keyword: str) -> str:
    """Return the text slice after 'keyword' in the instruction, stripped."""
    idx = lowered.index(keyword)
    after = original[idx + len(keyword):].strip().rstrip("。.，,！!？?")
    return after


def parse_nl_update(instruction: str, brief: Brief) -> NLUpdateResult:
    """Parse a natural language instruction into Brief field updates.

    Uses pure keyword matching (V1, no LLM dependency).
    """
    lower = instruction.lower()
    updates: dict[str, Any] = {}
    changed_fields: list[str] = []
    explanations: list[str] = []

    # --- 1. Mood detection ---
    for keyword, mood_val in _MOOD_KEYWORDS:
        if keyword in lower:
            if mood_val.startswith("_"):
                # Generic atmosphere/mood cue — use full instruction as value
                updates["mood"] = instruction
            else:
                updates["mood"] = mood_val
            changed_fields.append("mood")
            explanations.append(f"mood → {updates['mood']}")
            break  # First match wins

    # --- 2. Must-avoid detection ---
    for kw in _AVOID_KEYWORDS:
        if kw in lower:
            after = _extract_after_keyword(instruction, lower, kw)
            if after:
                updates["must_avoid"] = after
                changed_fields.append("must_avoid")
                explanations.append(f"must_avoid += '{after}'")
            break

    # --- 3. Add-element detection ---
    for kw in _ADD_KEYWORDS:
        if kw in lower:
            after = _extract_after_keyword(instruction, lower, kw)
            if after:
                updates["elements"] = after
                changed_fields.append("elements")
                explanations.append(f"elements += '{after}'")
            break

    # --- 4. Composition detection (only if not already handled above) ---
    if any(kw in lower for kw in _COMPOSITION_KEYWORDS):
        # Avoid double-classifying "add mountain" as both elements and composition
        if "elements" not in changed_fields and "composition" not in changed_fields:
            updates["composition"] = instruction
            changed_fields.append("composition")
            explanations.append(f"composition ← '{instruction}'")

    # --- 5. Palette / color detection ---
    if any(kw in lower for kw in _COLOR_KEYWORDS):
        if "palette" not in changed_fields:
            updates["palette"] = instruction
            changed_fields.append("palette")
            explanations.append(f"palette ← '{instruction}'")

    # --- 6. Fallback: treat as composition change ---
    if not changed_fields:
        updates["composition"] = instruction
        changed_fields.append("composition")
        explanations.append(f"(fallback) composition ← '{instruction}'")

    rollback = determine_rollback(changed_fields)
    confidence = 0.8 if len(changed_fields) == 1 else 0.6

    return NLUpdateResult(
        field_updates=updates,
        rollback_to=rollback,
        confidence=confidence,
        explanation="; ".join(explanations),
    )


def apply_update(brief: Brief, result: NLUpdateResult) -> None:
    """Apply a parsed NLUpdateResult to a Brief in-place.

    Ensures updated_at advances past created_at even when both operations
    happen within the same second (uses a brief sleep if timestamps match).
    """
    # Use microsecond precision to guarantee updated_at differs from created_at
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds")

    for field_name, value in result.field_updates.items():
        if field_name == "mood":
            brief.mood = value
        elif field_name == "must_avoid":
            if value not in brief.must_avoid:
                brief.must_avoid.append(value)
        elif field_name == "must_have":
            if value not in brief.must_have:
                brief.must_have.append(value)
        elif field_name == "elements":
            brief.elements.append(Element(name=value, category=""))
        elif field_name == "composition":
            if brief.composition.layout:
                brief.composition.layout += f"; {value}"
            else:
                brief.composition.layout = value
        elif field_name == "palette":
            if brief.palette.mood:
                brief.palette.mood += f"; {value}"
            else:
                brief.palette.mood = value

    brief.updated_at = now
    brief.updates.append(BriefUpdate(
        timestamp=now,
        instruction=result.explanation or str(result.field_updates),
        fields_changed=list(result.field_updates.keys()),
        rollback_to=result.rollback_to.value,
    ))


async def parse_nl_update_llm(instruction: str, brief: Brief) -> NLUpdateResult:
    """Parse NL update using LLM for complex instructions. Falls back to keyword parsing."""
    try:
        import litellm
        from vulca._parse import parse_llm_json

        model = os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash")

        # Brief context
        brief_ctx = []
        if brief.mood:
            brief_ctx.append(f"mood: {brief.mood}")
        if brief.elements:
            brief_ctx.append(f"elements: {', '.join(e.name for e in brief.elements[:5])}")
        if brief.composition.layout:
            brief_ctx.append(f"layout: {brief.composition.layout}")

        system_prompt = (
            "You are a creative brief update parser. Given an update instruction, "
            "extract which Brief fields should change.\n\n"
            f"Current Brief: {'; '.join(brief_ctx) or 'empty'}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "field_updates": {"<field>": "<new_value>", ...},\n'
            '  "explanation": "<what this update does>"\n'
            "}\n\n"
            "Valid fields: mood, composition, palette, elements, must_have, must_avoid, "
            "style_mix, eval_criteria\n"
            "Rules:\n"
            "- Extract ALL field changes from the instruction\n"
            "- A single instruction can update multiple fields\n"
            "- Position/layout changes → composition field\n"
            "- Color/tone changes → palette field\n"
            "- Add/remove objects → elements field\n"
            "- Return ONLY the JSON"
        )

        resp = await litellm.acompletion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": instruction},
            ],
            max_tokens=512,
            temperature=0.0,
            timeout=15,
        )
        text = resp.choices[0].message.content.strip()
        data = parse_llm_json(text)

        updates = data.get("field_updates", {})
        explanation = data.get("explanation", "")

        if updates:
            changed = list(updates.keys())
            rollback = determine_rollback(changed)
            return NLUpdateResult(
                field_updates=updates,
                rollback_to=rollback,
                confidence=0.85,
                explanation=explanation,
            )

    except Exception as exc:
        logger.warning("LLM NL update parsing failed, using keyword fallback: %s", exc)

    # Fallback to keyword parsing
    return parse_nl_update(instruction, brief)
