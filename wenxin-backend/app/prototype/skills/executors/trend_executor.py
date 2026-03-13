"""Trend alignment skill executor."""

from app.prototype.skills.executors.base import BaseSkillExecutor
from app.prototype.skills.types import SkillResult

TREND_PROMPT = (
    "Analyze this image against current visual design trends. Score alignment "
    "with each trend on a 0-1 scale:\n"
    "- minimalism: Clean, minimal aesthetic\n"
    "- maximalism: Bold, layered, expressive aesthetic\n"
    "- retro: Vintage or nostalgic style references\n"
    "- futuristic: Forward-looking, tech-inspired visuals\n"
    "- organic: Natural, hand-crafted, textural feel\n\n"
    "Respond ONLY with JSON (no markdown):\n"
    '{"score": <0-1 overall trend relevance>, '
    '"trends": {"minimalism": <0-1>, "maximalism": <0-1>, "retro": <0-1>, '
    '"futuristic": <0-1>, "organic": <0-1>}, '
    '"dominant_trend": "<trend name>", '
    '"summary": "<brief assessment>", "suggestions": ["<suggestion>", ...]}'
)

_TRENDS = ("minimalism", "maximalism", "retro", "futuristic", "organic")


class TrendExecutor(BaseSkillExecutor):
    """Evaluates trend alignment of visual content."""

    SKILL_NAME = "trend_alignment"

    def __init__(self) -> None:
        super().__init__(skill_name="trend_alignment")

    async def execute(
        self, image_path: str, context: dict | None = None
    ) -> SkillResult:
        raw = await self._call_gemini(image_path, TREND_PROMPT)
        data = self._parse_json(raw)

        # Extract per-trend scores
        trend_data = data.get("trends", {})
        trends = {t: float(trend_data.get(t, 0.5)) for t in _TRENDS}

        # Overall score: use LLM-provided or max trend alignment
        if "score" in data:
            score = float(data["score"])
        else:
            score = max(trends.values()) if trends else 0.5

        dominant = data.get("dominant_trend", max(trends, key=trends.get))  # type: ignore[arg-type]
        summary = data.get("summary", "Trend alignment analysis complete.")
        suggestions = data.get("suggestions", [])
        if isinstance(suggestions, str):
            suggestions = [suggestions]

        return SkillResult(
            skill_name=self.skill_name,
            score=round(score, 3),
            summary=summary,
            details={
                "trends": trends,
                "dominant_trend": dominant,
            },
            suggestions=suggestions,
        )
