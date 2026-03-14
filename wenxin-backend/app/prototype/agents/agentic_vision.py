"""Agentic Vision analyzer for deep cultural art inspection.

Implements a Think->Act->Observe loop inspired by Gemini's Agentic Vision,
where the model actively investigates artwork details relevant to L1/L3/L5
scoring across multiple rounds.

Round 1 (Global Scan):  Overall composition, cultural signals, aesthetic feel
Round 2 (Focused Inspection): Tradition-specific deep dive into key regions
Round 3 (Synthesis):    Cross-dimensional narrative + per-L-level insights

Max 3 rounds to keep API costs reasonable. Each round produces
VisionObservations that accumulate into final AgenticInsights.

Usage:
    analyzer = AgenticVisionAnalyzer()
    insights = await analyzer.analyze(image_path, tradition="chinese_xieyi")
    # Returns AgenticInsights with per-dimension findings
"""

from __future__ import annotations

import base64
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "AgenticInsights",
    "AgenticVisionAnalyzer",
    "VisionObservation",
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class VisionObservation:
    """Single observation from one inspection step."""

    region: str           # e.g. "upper-left quadrant", "brushwork detail"
    finding: str          # What was observed
    l_levels: list[str]   # Which L-levels this is relevant to ("L1", "L3", ...)
    confidence: float     # 0.0-1.0


@dataclass
class AgenticInsights:
    """Aggregated insights from agentic vision analysis."""

    observations: list[VisionObservation] = field(default_factory=list)
    l1_visual_details: list[str] = field(default_factory=list)
    l3_cultural_signals: list[str] = field(default_factory=list)
    l5_aesthetic_qualities: list[str] = field(default_factory=list)
    overall_narrative: str = ""
    analysis_steps: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize for inclusion in CritiqueOutput."""
        return {
            "observations": [
                {
                    "region": o.region,
                    "finding": o.finding,
                    "l_levels": o.l_levels,
                    "confidence": o.confidence,
                }
                for o in self.observations
            ],
            "l1_visual_details": self.l1_visual_details,
            "l3_cultural_signals": self.l3_cultural_signals,
            "l5_aesthetic_qualities": self.l5_aesthetic_qualities,
            "overall_narrative": self.overall_narrative,
            "analysis_steps": self.analysis_steps,
        }


# ---------------------------------------------------------------------------
# Tradition-specific inspection prompts
# ---------------------------------------------------------------------------

_TRADITION_INSPECTION_PROMPTS: dict[str, str] = {
    "chinese_xieyi": (
        "Focus on these tradition-specific elements:\n"
        "- Brushwork texture: Are strokes expressive and spontaneous (xieyi spirit)?\n"
        "- Ink gradation: Is there 'bone method' (骨法用笔) visible in stroke weight variation?\n"
        "- Negative space (留白): How is empty space used to create depth and breathing room?\n"
        "- Shanshui composition: Mountains-water spatial layering (远近法)\n"
        "- Ink wash transitions: Smooth gradient from dense (浓) to light (淡)\n"
        "- Spirit resonance (气韵生动): Does the artwork feel alive?"
    ),
    "chinese_gongbi": (
        "Focus on these tradition-specific elements:\n"
        "- Fine line work: Are outlines precise and controlled (工笔)?\n"
        "- Mineral pigment layers: Are colors rich and layered?\n"
        "- Detail fidelity: Meticulous rendering of subject matter\n"
        "- Compositional formality: Structured, deliberate arrangement\n"
        "- Gold/azurite/malachite palette accuracy"
    ),
    "islamic_geometric": (
        "Focus on these tradition-specific elements:\n"
        "- Pattern symmetry: Are geometric patterns mathematically precise?\n"
        "- Tessellation completeness: Do patterns tile without gaps?\n"
        "- Arabesque flow: Smooth, continuous interlacing curves\n"
        "- Color transitions: Harmony within the palette constraints\n"
        "- Girih tile accuracy: Correct angles (72/144 degree stars)\n"
        "- Aniconism respect: Absence of figurative representation"
    ),
    "western_academic": (
        "Focus on these tradition-specific elements:\n"
        "- Chiaroscuro: Light-shadow modeling for volume\n"
        "- Linear perspective: Correct vanishing point(s)\n"
        "- Anatomical proportion: If figures present, are proportions classical?\n"
        "- Oil painting texture: Visible brushwork, impasto, glazing layers\n"
        "- Color temperature: Warm/cool contrast for spatial depth"
    ),
    "african_traditional": (
        "Focus on these tradition-specific elements:\n"
        "- Bold geometric patterns: Strong, symbolic shapes\n"
        "- Carved/relief texture: Three-dimensional quality\n"
        "- Symbolic color use: Earth tones, primary colors with cultural meaning\n"
        "- Mask/figure stylization: Proportional distortion for spiritual emphasis\n"
        "- Storytelling composition: Narrative visual flow"
    ),
    "south_asian": (
        "Focus on these tradition-specific elements:\n"
        "- Miniature painting precision: Fine detail in small scale\n"
        "- Narrative composition: Sequential or layered storytelling\n"
        "- Decorative border work: Frame and margin ornamentation\n"
        "- Flat perspective: Characteristic lack of Western perspective\n"
        "- Jewel-tone palette: Rich, saturated colors"
    ),
}

_DEFAULT_INSPECTION_PROMPT = (
    "Focus on these general artistic elements:\n"
    "- Composition balance: Rule of thirds, golden ratio, visual weight\n"
    "- Color harmony: Complementary, analogous, or intentional discord\n"
    "- Technical execution: Detail quality, rendering consistency\n"
    "- Emotional tone: What feeling does the artwork convey?\n"
    "- Originality: Novel elements or creative interpretations"
)


# ---------------------------------------------------------------------------
# Round prompts
# ---------------------------------------------------------------------------

_ROUND_1_PROMPT = """\
You are an expert art critic performing a detailed visual investigation of this artwork.
This is Round 1: GLOBAL SCAN.

Cultural Tradition: {tradition}
Subject/Intent: {subject}
{terminology_section}

Perform a comprehensive initial scan. Identify:

1. **Dominant Visual Elements (L1)**: Composition, layout, color palette, spatial arrangement, dominant shapes and forms.

2. **Cultural Symbols or Motifs (L3)**: Any cultural references, traditional symbols, motifs, or visual vocabulary specific to the stated tradition. Note both present AND missing expected elements.

3. **Aesthetic Philosophy / Feeling (L5)**: The overall aesthetic quality, emotional resonance, philosophical depth. Does it achieve transcendence or remain surface-level?

4. **Areas Needing Closer Inspection**: Identify 2-3 specific regions or aspects that need deeper examination in the next round.

Output ONLY valid JSON:
{{"observations": [
    {{"region": "description of area/aspect",
      "finding": "what you observed",
      "l_levels": ["L1", "L3", "L5"],
      "confidence": 0.85}}
  ],
  "areas_to_inspect": ["area1", "area2"],
  "initial_l1_notes": ["note1", "note2"],
  "initial_l3_notes": ["note1", "note2"],
  "initial_l5_notes": ["note1", "note2"]
}}"""

_ROUND_2_PROMPT = """\
You are continuing a detailed visual investigation. This is Round 2: FOCUSED INSPECTION.

Cultural Tradition: {tradition}
Subject/Intent: {subject}

Previous round identified these areas for closer inspection:
{areas_to_inspect}

{tradition_specific_prompt}

Now examine each identified area closely. For each area:
- Describe what you see in detail
- Assess its quality and cultural authenticity
- Note any technical strengths or weaknesses

Output ONLY valid JSON:
{{"observations": [
    {{"region": "specific area examined",
      "finding": "detailed observation",
      "l_levels": ["L1"],
      "confidence": 0.9}}
  ],
  "l1_details": ["detailed visual finding 1", "finding 2"],
  "l3_signals": ["cultural signal 1", "signal 2"],
  "l5_qualities": ["aesthetic quality 1", "quality 2"]
}}"""

_ROUND_3_PROMPT = """\
You are completing a detailed visual investigation. This is Round 3: SYNTHESIS.

Cultural Tradition: {tradition}
Subject/Intent: {subject}

Here are ALL observations from the previous two rounds:
{all_observations}

Synthesize your findings into a coherent assessment. Provide:

1. **L1 Visual Summary**: Key visual strengths and weaknesses (composition, color, space)
2. **L3 Cultural Summary**: How well does this artwork embody the {tradition} tradition? What cultural elements are present, missing, or misrepresented?
3. **L5 Aesthetic Summary**: Does the artwork achieve aesthetic depth? Is there spiritual/philosophical resonance appropriate to the tradition?
4. **Overall Narrative**: A 2-3 sentence expert assessment tying everything together.

Output ONLY valid JSON:
{{"l1_visual_details": ["summary point 1", "point 2"],
  "l3_cultural_signals": ["cultural finding 1", "finding 2"],
  "l5_aesthetic_qualities": ["aesthetic quality 1", "quality 2"],
  "overall_narrative": "2-3 sentence synthesis",
  "final_observations": [
    {{"region": "synthesis",
      "finding": "key synthesis point",
      "l_levels": ["L1", "L3", "L5"],
      "confidence": 0.9}}
  ]
}}"""


# ---------------------------------------------------------------------------
# AgenticVisionAnalyzer
# ---------------------------------------------------------------------------

class AgenticVisionAnalyzer:
    """Think->Act->Observe loop for artwork analysis.

    Step 1 (Think): Given tradition + image, plan what to inspect
    Step 2 (Act):   Ask VLM to focus on specific regions/aspects
    Step 3 (Observe): Collect findings, decide if more inspection needed

    Max 3 rounds to keep costs reasonable.
    """

    MAX_ROUNDS = 3

    def __init__(self, model: str = "gemini/gemini-2.5-flash") -> None:
        self.model = model

    async def analyze(
        self,
        image_path: str,
        tradition: str = "default",
        subject: str = "",
        terminology_hints: list[str] | None = None,
    ) -> AgenticInsights:
        """Run agentic vision analysis on an artwork.

        Args:
            image_path: Path to the image file.
            tradition: Cultural tradition name for context.
            subject: Original creation subject/intent.
            terminology_hints: Scout-provided terminology to look for.

        Returns:
            AgenticInsights with per-dimension findings.
            On any failure, returns empty AgenticInsights (never crashes).
        """
        insights = AgenticInsights()

        # Load and encode image
        img_b64, mime_type = _load_image_b64(image_path)
        if not img_b64:
            logger.warning("Agentic vision: could not load image %s", image_path)
            return insights

        try:
            # Round 1: Global Scan
            r1_data = await self._round_1(
                img_b64, mime_type, tradition, subject, terminology_hints,
            )
            insights.analysis_steps += 1
            self._merge_observations(insights, r1_data.get("observations", []))
            insights.l1_visual_details.extend(r1_data.get("initial_l1_notes", []))
            insights.l3_cultural_signals.extend(r1_data.get("initial_l3_notes", []))
            insights.l5_aesthetic_qualities.extend(r1_data.get("initial_l5_notes", []))

            areas_to_inspect = r1_data.get("areas_to_inspect", [])

            # Round 2: Focused Inspection (only if Round 1 identified areas)
            if areas_to_inspect:
                r2_data = await self._round_2(
                    img_b64, mime_type, tradition, subject, areas_to_inspect,
                )
                insights.analysis_steps += 1
                self._merge_observations(insights, r2_data.get("observations", []))
                insights.l1_visual_details.extend(r2_data.get("l1_details", []))
                insights.l3_cultural_signals.extend(r2_data.get("l3_signals", []))
                insights.l5_aesthetic_qualities.extend(r2_data.get("l5_qualities", []))

            # Round 3: Synthesis (always run if we got this far)
            obs_summary = self._summarize_observations(insights.observations)
            r3_data = await self._round_3(
                img_b64, mime_type, tradition, subject, obs_summary,
            )
            insights.analysis_steps += 1
            self._merge_observations(insights, r3_data.get("final_observations", []))

            # Synthesis results replace (not append) the per-dimension lists
            if r3_data.get("l1_visual_details"):
                insights.l1_visual_details = r3_data["l1_visual_details"]
            if r3_data.get("l3_cultural_signals"):
                insights.l3_cultural_signals = r3_data["l3_cultural_signals"]
            if r3_data.get("l5_aesthetic_qualities"):
                insights.l5_aesthetic_qualities = r3_data["l5_aesthetic_qualities"]
            if r3_data.get("overall_narrative"):
                insights.overall_narrative = r3_data["overall_narrative"]

        except Exception:
            logger.exception("Agentic vision analysis failed for %s", image_path)
            # Return whatever partial insights we collected

        return insights

    # ------------------------------------------------------------------
    # Round implementations
    # ------------------------------------------------------------------

    async def _round_1(
        self,
        img_b64: str,
        mime_type: str,
        tradition: str,
        subject: str,
        terminology_hints: list[str] | None,
    ) -> dict[str, Any]:
        """Round 1: Global Scan."""
        terminology_section = ""
        if terminology_hints:
            terms_str = ", ".join(terminology_hints[:10])
            terminology_section = f"Cultural terminology to look for: {terms_str}"

        prompt = _ROUND_1_PROMPT.format(
            tradition=tradition.replace("_", " "),
            subject=subject or "(no specific subject)",
            terminology_section=terminology_section,
        )
        return await self._call_vlm(img_b64, mime_type, prompt)

    async def _round_2(
        self,
        img_b64: str,
        mime_type: str,
        tradition: str,
        subject: str,
        areas_to_inspect: list[str],
    ) -> dict[str, Any]:
        """Round 2: Focused Inspection with tradition-specific prompts."""
        tradition_prompt = _TRADITION_INSPECTION_PROMPTS.get(
            tradition, _DEFAULT_INSPECTION_PROMPT,
        )

        areas_str = "\n".join(f"- {area}" for area in areas_to_inspect[:5])

        prompt = _ROUND_2_PROMPT.format(
            tradition=tradition.replace("_", " "),
            subject=subject or "(no specific subject)",
            areas_to_inspect=areas_str,
            tradition_specific_prompt=tradition_prompt,
        )
        return await self._call_vlm(img_b64, mime_type, prompt)

    async def _round_3(
        self,
        img_b64: str,
        mime_type: str,
        tradition: str,
        subject: str,
        observations_summary: str,
    ) -> dict[str, Any]:
        """Round 3: Synthesis."""
        prompt = _ROUND_3_PROMPT.format(
            tradition=tradition.replace("_", " "),
            subject=subject or "(no specific subject)",
            all_observations=observations_summary,
        )
        return await self._call_vlm(img_b64, mime_type, prompt)

    # ------------------------------------------------------------------
    # VLM call helper
    # ------------------------------------------------------------------

    async def _call_vlm(
        self,
        img_b64: str,
        mime_type: str,
        prompt: str,
    ) -> dict[str, Any]:
        """Call the VLM with image + text prompt and parse JSON response.

        Returns parsed dict on success, empty dict on failure.
        """
        import litellm

        # Resolve API key from model_router if available
        extra_kwargs: dict[str, Any] = {}
        try:
            from app.prototype.agents.model_router import MODELS
            # Try to find a matching model spec for API key/base
            for _key, spec in MODELS.items():
                if spec.litellm_id == self.model:
                    api_key = spec.get_api_key()
                    api_base = spec.get_api_base()
                    if api_key:
                        extra_kwargs["api_key"] = api_key
                    if api_base:
                        extra_kwargs["api_base"] = api_base
                    break
        except Exception:
            pass  # litellm will use env vars as fallback

        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{img_b64}",
                            },
                        },
                    ],
                }],
                temperature=0.3,
                max_tokens=2048,
                timeout=45,
                **extra_kwargs,
            )
        except Exception:
            logger.exception("Agentic vision VLM call failed (model=%s)", self.model)
            return {}

        if not response or not response.choices:
            return {}

        content = response.choices[0].message.content
        if not content:
            return {}

        return _parse_vlm_json(content)

    # ------------------------------------------------------------------
    # Observation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _merge_observations(
        insights: AgenticInsights,
        raw_observations: list[dict[str, Any]],
    ) -> None:
        """Parse raw observation dicts into VisionObservation and append."""
        for obs in raw_observations:
            if not isinstance(obs, dict):
                continue
            try:
                insights.observations.append(VisionObservation(
                    region=str(obs.get("region", "unknown")),
                    finding=str(obs.get("finding", "")),
                    l_levels=obs.get("l_levels", []),
                    confidence=float(obs.get("confidence", 0.5)),
                ))
            except (TypeError, ValueError):
                continue

    @staticmethod
    def _summarize_observations(observations: list[VisionObservation]) -> str:
        """Create a text summary of all observations for Round 3 input."""
        if not observations:
            return "(No observations from previous rounds)"

        lines = []
        for i, obs in enumerate(observations, 1):
            levels = ", ".join(obs.l_levels) if obs.l_levels else "general"
            lines.append(
                f"{i}. [{levels}] Region: {obs.region} | "
                f"Finding: {obs.finding} (confidence: {obs.confidence:.2f})"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _load_image_b64(path: str) -> tuple[str, str]:
    """Load an image file and return (base64_string, mime_type).

    Returns ("", "") if the file doesn't exist or can't be read.
    """
    p = Path(path)
    if not p.exists():
        logger.debug("Image file not found: %s", path)
        return "", ""

    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    mime_type = mime_map.get(p.suffix.lower(), "image/png")

    try:
        data = p.read_bytes()
        # Auto-detect from magic bytes
        if data[:4] == b"\x89PNG":
            mime_type = "image/png"
        elif data[:2] == b"\xff\xd8":
            mime_type = "image/jpeg"
        elif data[:4] == b"RIFF" and len(data) > 12 and data[8:12] == b"WEBP":
            mime_type = "image/webp"

        return base64.b64encode(data).decode("ascii"), mime_type
    except Exception:
        logger.exception("Failed to read image %s", path)
        return "", ""


def _parse_vlm_json(content: str) -> dict[str, Any]:
    """Parse VLM response content as JSON, handling markdown wrappers.

    Returns empty dict on parse failure (never raises).
    """
    text = content.strip()

    # Strip markdown code block if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # Remove opening ```json line
        while lines and lines[-1].strip() in ("", "```"):
            lines.pop()
        text = "\n".join(lines).strip()

    # Try direct parse
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # Try extracting JSON from mixed content
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start:end])
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    logger.warning("Agentic vision: failed to parse VLM JSON: %s", text[:200])
    return {}
