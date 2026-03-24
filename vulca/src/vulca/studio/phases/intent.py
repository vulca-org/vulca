"""IntentPhase -- parse user intent and generate clarifying questions."""
from __future__ import annotations

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


class IntentPhase:
    def parse_intent(self, brief: Brief) -> Brief:
        text = brief.intent.lower()
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
        return brief

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
