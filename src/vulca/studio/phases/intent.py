"""IntentPhase -- parse user intent and generate clarifying questions."""
from __future__ import annotations

import logging
import os
import re
from typing import Any
from vulca.studio.brief import Brief
from vulca.studio.types import Composition, Palette, StyleWeight, Element

logger = logging.getLogger("vulca.studio")

_TRADITION_HINTS: dict[str, str] = {
    # Chinese Xieyi (freehand ink)
    "水墨": "chinese_xieyi", "写意": "chinese_xieyi", "ink wash": "chinese_xieyi",
    "xieyi": "chinese_xieyi", "泼墨": "chinese_xieyi", "山水": "chinese_xieyi",
    "江南": "chinese_xieyi", "桃花": "chinese_xieyi", "中国风": "chinese_xieyi",
    "国画": "chinese_xieyi", "chinese painting": "chinese_xieyi",
    "chinese ink": "chinese_xieyi", "shanshui": "chinese_xieyi",
    # Chinese Gongbi (meticulous)
    "工笔": "chinese_gongbi", "gongbi": "chinese_gongbi", "细笔": "chinese_gongbi",
    "meticulous": "chinese_gongbi",
    # Japanese
    "浮世绘": "japanese_traditional", "ukiyo": "japanese_traditional",
    "日本画": "japanese_traditional", "和风": "japanese_traditional",
    "japanese": "japanese_traditional",
    # Western Academic
    "油画": "western_academic", "oil painting": "western_academic",
    "古典": "western_academic", "renaissance": "western_academic",
    "classical": "western_academic", "academic": "western_academic",
    # Watercolor
    "watercolor": "watercolor", "水彩": "watercolor", "aquarelle": "watercolor",
    # Islamic Geometric
    "几何": "islamic_geometric", "geometric": "islamic_geometric",
    "tessellation": "islamic_geometric", "islamic": "islamic_geometric",
    # Contemporary Art
    "抽象": "contemporary_art", "abstract": "contemporary_art",
    "当代艺术": "contemporary_art", "contemporary": "contemporary_art",
    "modern art": "contemporary_art", "现代艺术": "contemporary_art",
    # Brand Design
    "商业": "brand_design", "品牌": "brand_design", "brand": "brand_design",
    "海报": "brand_design", "poster": "brand_design", "logo": "brand_design",
    "广告": "brand_design", "commercial": "brand_design",
    # Photography
    "摄影": "photography", "photo": "photography", "photography": "photography",
    # UI/UX
    "ui": "ui_ux_design", "ux": "ui_ux_design", "界面": "ui_ux_design",
    "app design": "ui_ux_design",
    # African Traditional
    "african": "african_traditional", "非洲": "african_traditional",
    # South Asian
    "印度": "south_asian", "indian": "south_asian", "south asian": "south_asian",
    "mughal": "south_asian", "mandala": "south_asian",
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
        questions: list[dict[str, Any]] = []

        if not brief.mood:
            questions.append({
                "text": "What mood/atmosphere?",
                "field": "mood",
                "options": [o["value"] for o in _MOOD_OPTIONS],
                "labels": [o["label"] for o in _MOOD_OPTIONS],
            })

        if not brief.composition.layout:
            questions.append({
                "text": "Composition/layout preference?",
                "field": "composition",
                "options": ["rule-of-thirds", "centered", "diagonal", "symmetrical", "golden-ratio"],
                "labels": ["三分法", "居中", "对角线", "对称", "黄金分割"],
            })

        if not brief.palette.primary and not brief.palette.mood:
            questions.append({
                "text": "Color palette?",
                "field": "palette",
                "options": ["warm", "cool", "monochrome", "earth-tones", "vibrant"],
                "labels": ["暖色调", "冷色调", "单色", "大地色系", "鲜艳明快"],
            })

        if not brief.elements:
            questions.append({
                "text": "Key elements to include?",
                "field": "elements",
                "options": ["nature", "architecture", "figures", "abstract-forms"],
                "labels": ["自然元素", "建筑元素", "人物", "抽象形态"],
            })

        if not any(e.category == "technique" for e in brief.elements):
            questions.append({
                "text": "Brush/rendering style?",
                "field": "brush_style",
                "options": [o["value"] for o in _BRUSH_OPTIONS],
                "labels": [o["label"] for o in _BRUSH_OPTIONS],
            })

        # Add 自定义 option to each question
        for q in questions:
            q["options"].append("custom")
            q["labels"].append("自定义 (custom)")

        return questions[:5]

    def apply_answer(self, brief: Brief, question: dict, answer: str) -> None:
        field = question.get("field", "")
        if field == "mood":
            brief.update_field("mood", answer)
        elif field == "brush_style":
            brief.elements.append(Element(name=answer, category="technique"))
            from datetime import datetime, timezone
            brief.updated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    async def parse_intent_llm(self, brief: Brief) -> Brief:
        """Parse intent using LLM for deep extraction. Falls back to keyword parsing."""
        try:
            import litellm
            from vulca._parse import parse_llm_json

            model = os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash")
            system_prompt = (
                "You are a creative brief analyst. Given the user's creative intent, "
                "extract structured information into JSON.\n\n"
                "Return ONLY valid JSON with these fields:\n"
                "{\n"
                '  "mood": "<string: emotional atmosphere, e.g. serene, dynamic, mystical>",\n'
                '  "style_mix": [{"tradition": "<yaml_key>", "tag": "<free_tag>", "weight": <0-1>}],\n'
                '  "elements": [{"name": "<string>", "category": "<subject|technique|atmosphere>"}],\n'
                '  "palette": {"primary": ["<hex>"], "accent": ["<hex>"], "mood": "<string>"},\n'
                '  "composition": {"layout": "<string>", "focal_point": "<string>", '
                '"aspect_ratio": "<W:H>", "negative_space": "<none|light|heavy>"},\n'
                '  "must_have": ["<string>"],\n'
                '  "must_avoid": ["<string>"]\n'
                "}\n\n"
                "Available traditions: chinese_xieyi, chinese_gongbi, japanese_traditional, "
                "western_academic, watercolor, islamic_geometric, contemporary_art, "
                "brand_design, photography, ui_ux_design, african_traditional, south_asian.\n\n"
                "Rules:\n"
                "- Extract ALL implicit subjects/objects as elements (mountains, bridges, flowers, etc.)\n"
                "- Detect color information even from adjectives (cold, warm, monochrome)\n"
                "- Set composition from spatial cues (perspective, negative space, aspect ratio)\n"
                "- Use empty string/list for unknown fields, never omit fields\n"
                "- Respond in the same language as the input for mood/element names\n"
                "- CRITICAL: elements MUST be [{\"name\": \"...\", \"category\": \"...\"}] format\n"
                "- CRITICAL: style_mix MUST be [{\"tradition\": \"...\", \"tag\": \"...\", \"weight\": N}] format\n"
                "- CRITICAL: Return ONLY the JSON object, no extra text or explanation"
            )

            resp = await litellm.acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": brief.intent},
                ],
                max_tokens=1024,
                temperature=0.1,
                timeout=30,
            )
            text = resp.choices[0].message.content.strip()
            data = parse_llm_json(text)
            self._apply_llm_result(brief, data)

        except Exception as exc:
            logger.warning("LLM intent parsing failed, falling back to keywords: %s", exc)

        # Always run keyword parsing as supplement (fills gaps LLM missed)
        self.parse_intent(brief)
        return brief

    @staticmethod
    def _apply_llm_result(brief: Brief, data: dict) -> None:
        """Apply parsed LLM JSON to Brief fields (additive, no overwrite of existing).

        Handles both strict schema (dicts) and loose schema (strings) from LLMs.
        """
        # Mood
        if data.get("mood") and not brief.mood:
            brief.mood = str(data["mood"])

        # Style mix — handle both dict list and string list
        if data.get("style_mix") and not brief.style_mix:
            styles = []
            for s in data["style_mix"]:
                if isinstance(s, dict):
                    styles.append(StyleWeight(
                        tradition=s.get("tradition", ""),
                        tag=s.get("tag", ""),
                        weight=float(s.get("weight", 0.5)),
                    ))
                elif isinstance(s, str) and s:
                    # Check if it matches a known tradition
                    s_lower = s.lower().replace(" ", "_")
                    known = {v for v in _TRADITION_HINTS.values()}
                    if s_lower in known:
                        styles.append(StyleWeight(tradition=s_lower, weight=0.5))
                    else:
                        styles.append(StyleWeight(tag=s, weight=0.5))
            if styles:
                for st in styles:
                    st.weight = round(1.0 / len(styles), 2)
                brief.style_mix = styles

        # Elements (additive) — handle both dict list and string list
        existing_names = {e.name.lower() for e in brief.elements}
        for e in data.get("elements", []):
            if isinstance(e, dict):
                name = e.get("name", "")
                cat = e.get("category", "")
            elif isinstance(e, str):
                name = e
                cat = ""
            else:
                continue
            if name and name.lower() not in existing_names:
                brief.elements.append(Element(name=name, category=cat))
                existing_names.add(name.lower())

        # Palette — handle non-standard keys (base/accents vs primary/accent/mood)
        pal = data.get("palette", {})
        if isinstance(pal, dict):
            primary = pal.get("primary") or pal.get("base_colors", [])
            accent = pal.get("accent") or pal.get("accents") or pal.get("accent_colors", [])
            mood = pal.get("mood") or pal.get("base") or pal.get("tone", "")

            if primary and not brief.palette.primary:
                if isinstance(primary, list):
                    brief.palette.primary = [c for c in primary if isinstance(c, str)]
                elif isinstance(primary, str):
                    brief.palette.primary = [primary]
            if accent and not brief.palette.accent:
                if isinstance(accent, list):
                    brief.palette.accent = [c for c in accent if isinstance(c, str)]
                elif isinstance(accent, str):
                    brief.palette.accent = [accent]
            if mood and not brief.palette.mood:
                brief.palette.mood = str(mood)

        # Composition — handle both dict and string
        comp = data.get("composition", {})
        if isinstance(comp, dict):
            if comp.get("layout") and not brief.composition.layout:
                brief.composition.layout = comp["layout"]
            if comp.get("focal_point") and not brief.composition.focal_point:
                brief.composition.focal_point = comp["focal_point"]
            if comp.get("aspect_ratio") and comp["aspect_ratio"] != "1:1":
                brief.composition.aspect_ratio = comp["aspect_ratio"]
            if comp.get("negative_space") and not brief.composition.negative_space:
                brief.composition.negative_space = comp["negative_space"]
        elif isinstance(comp, str) and comp and not brief.composition.layout:
            brief.composition.layout = comp

        # Must have / avoid (additive)
        for item in data.get("must_have", []):
            if isinstance(item, str) and item and item not in brief.must_have:
                brief.must_have.append(item)
        for item in data.get("must_avoid", []):
            if isinstance(item, str) and item and item not in brief.must_avoid:
                brief.must_avoid.append(item)

    def set_sketch(self, brief: Brief, sketch_path: str) -> None:
        brief.update_field("user_sketch", sketch_path)
