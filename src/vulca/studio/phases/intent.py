"""IntentPhase -- parse user intent and generate clarifying questions."""
from __future__ import annotations

import re
from typing import Any
from vulca.studio.brief import Brief
from vulca.studio.types import StyleWeight, Element

_TRADITION_HINTS: dict[str, str] = {
    "水墨": "chinese_xieyi", "写意": "chinese_xieyi", "ink wash": "chinese_xieyi",
    "xieyi": "chinese_xieyi", "工笔": "chinese_gongbi", "gongbi": "chinese_gongbi",
    "浮世绘": "japanese_traditional", "ukiyo": "japanese_traditional",
    "油画": "western_academic", "oil painting": "western_academic",
    "watercolor": "watercolor", "水彩": "watercolor",
    "几何": "islamic_geometric", "geometric": "islamic_geometric",
}

_TAG_HINTS = ["cyberpunk", "赛博朋克", "steampunk", "蒸汽朋克", "pixel", "像素",
              "vaporwave", "synthwave", "minimalist", "极简"]

_MOOD_OPTIONS = [
    {"value": "epic-solitary", "label": "壮阔孤寂"},
    {"value": "serene", "label": "宁静平和"},
    {"value": "mystical", "label": "神秘玄幻"},
    {"value": "dynamic", "label": "动感张力"},
]

_BRUSH_OPTIONS = [
    {"value": "traditional", "label": "传统笔触"},
    {"value": "mixed-digital", "label": "数字混合"},
    {"value": "abstract", "label": "抽象表现"},
]


_ELEMENT_PATTERNS_ZH = [
    re.compile(r"需要(.+?)元素"),
    re.compile(r"要有(.+?)[，。,.]"),
    re.compile(r"包含(.+?)[，。,.]"),
    re.compile(r"画.{0,4}(.+?)(?:和|与|及)(.+?)(?:元素|$)"),
]

_ELEMENT_PATTERNS_EN = [
    re.compile(r"include\s+(.+?)(?:\s*[,.]|$)", re.I),
    re.compile(r"with\s+(.+?)(?:\s*[,.]|$)", re.I),
    re.compile(r"featuring\s+(.+?)(?:\s*[,.]|$)", re.I),
]

_PALETTE_MOOD_MAP: dict[str, str] = {
    "冷色调": "cold tones", "冷色": "cold tones", "冷调": "cold tones",
    "暖色调": "warm tones", "暖色": "warm tones", "暖调": "warm tones",
    "cold tone": "cold tones", "warm tone": "warm tones",
    "cool tone": "cold tones", "cool color": "cold tones",
}

_HEX_PATTERN = re.compile(r"#[0-9a-fA-F]{6}")

_COMPOSITION_LAYOUT_MAP: dict[str, str] = {
    "对角线": "diagonal", "对角": "diagonal", "diagonal": "diagonal",
    "三分法": "rule-of-thirds", "三分": "rule-of-thirds", "rule of thirds": "rule-of-thirds",
    "居中": "centered", "center": "centered", "centered": "centered",
    "对称": "symmetrical", "symmetr": "symmetrical",
    "黄金分割": "golden-ratio", "golden ratio": "golden-ratio",
}

_NEGATIVE_SPACE_HINTS = ["留白", "negative space", "empty space", "大量空白"]

_ASPECT_RATIO_PATTERN = re.compile(r"(\d{1,2}:\d{1,2})")


class IntentPhase:
    def parse_intent(self, brief: Brief) -> Brief:
        text = brief.intent.lower()
        original_text = brief.intent  # preserve case for element names

        # --- Style detection (existing) ---
        detected = []
        for keyword, tradition in _TRADITION_HINTS.items():
            if keyword in text and not any(s.tradition == tradition for s in detected):
                detected.append(StyleWeight(tradition=tradition, weight=0.5))

        free_tags = []
        tag_map = {"赛博朋克": "cyberpunk", "蒸汽朋克": "steampunk", "像素": "pixel"}
        for tag in _TAG_HINTS:
            if tag in text:
                tag_name = tag_map.get(tag, tag)
                if not any(s.tag == tag_name for s in free_tags):
                    free_tags.append(StyleWeight(tag=tag_name, weight=0.5))

        all_styles = detected + free_tags
        if all_styles:
            for s in all_styles:
                s.weight = round(1.0 / len(all_styles), 2)
            brief.style_mix = all_styles

        # --- Element extraction ---
        self._extract_elements(brief, original_text)

        # --- Palette extraction ---
        self._extract_palette(brief, original_text)

        # --- Composition extraction ---
        self._extract_composition(brief, original_text)

        return brief

    @staticmethod
    def _extract_elements(brief: Brief, text: str) -> None:
        existing = {e.name for e in brief.elements}

        # Chinese patterns
        for pat in _ELEMENT_PATTERNS_ZH:
            for m in pat.finditer(text):
                for group_text in m.groups():
                    if not group_text:
                        continue
                    # Split on 和/与/及/、/,
                    parts = re.split(r"[和与及、,，]+", group_text.strip())
                    for part in parts:
                        name = part.strip().rstrip("元素的")
                        if name and name not in existing:
                            brief.elements.append(Element(name=name))
                            existing.add(name)

        # English patterns
        for pat in _ELEMENT_PATTERNS_EN:
            for m in pat.finditer(text):
                raw = m.group(1)
                parts = re.split(r"\s+and\s+|,\s*", raw)
                for part in parts:
                    name = part.strip()
                    if name and name.lower() not in {n.lower() for n in existing}:
                        brief.elements.append(Element(name=name))
                        existing.add(name)

    @staticmethod
    def _extract_palette(brief: Brief, text: str) -> None:
        text_lower = text.lower()

        # Palette mood
        for hint, mood in _PALETTE_MOOD_MAP.items():
            if hint in text_lower:
                brief.palette.mood = mood
                break

        # Hex colors
        for m in _HEX_PATTERN.finditer(text):
            color = m.group(0).upper()
            if color not in brief.palette.primary:
                brief.palette.primary.append(color)

    @staticmethod
    def _extract_composition(brief: Brief, text: str) -> None:
        text_lower = text.lower()

        # Layout
        for hint, layout in _COMPOSITION_LAYOUT_MAP.items():
            if hint in text_lower:
                brief.composition.layout = layout
                break

        # Negative space
        for hint in _NEGATIVE_SPACE_HINTS:
            if hint in text_lower:
                brief.composition.negative_space = "heavy"
                break

        # Aspect ratio
        m = _ASPECT_RATIO_PATTERN.search(text)
        if m:
            brief.composition.aspect_ratio = m.group(1)

    def generate_questions(self, brief: Brief) -> list[dict[str, Any]]:
        questions = []
        if not brief.mood:
            questions.append({
                "text": "What mood/atmosphere?",
                "field": "mood",
                "options": [o["value"] for o in _MOOD_OPTIONS],
                "labels": [o["label"] for o in _MOOD_OPTIONS],
            })
        if not any(e.category == "technique" for e in brief.elements):
            questions.append({
                "text": "Brush/rendering style?",
                "field": "brush_style",
                "options": [o["value"] for o in _BRUSH_OPTIONS],
                "labels": [o["label"] for o in _BRUSH_OPTIONS],
            })
        return questions

    def apply_answer(self, brief: Brief, question: dict, answer: str) -> None:
        field = question.get("field", "")
        if field == "mood":
            brief.update_field("mood", answer)
        elif field == "brush_style":
            brief.elements.append(Element(name=answer, category="technique"))
            from datetime import datetime, timezone
            brief.updated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def set_sketch(self, brief: Brief, sketch_path: str) -> None:
        brief.update_field("user_sketch", sketch_path)
