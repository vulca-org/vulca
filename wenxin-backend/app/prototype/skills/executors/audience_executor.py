"""Audience fit skill executor."""

from app.prototype.skills.executors.base import BaseSkillExecutor
from app.prototype.skills.types import SkillResult

AUDIENCE_PROMPT = (
    "Analyze this image for target audience appeal. Score how well the visual "
    "resonates with each demographic on a 0-1 scale:\n"
    "- gen_z: Generation Z (born ~1997-2012)\n"
    "- millennial: Millennials (born ~1981-1996)\n"
    "- gen_x: Generation X (born ~1965-1980)\n"
    "- boomer: Baby Boomers (born ~1946-1964)\n\n"
    "Respond ONLY with JSON (no markdown):\n"
    '{"score": <0-1 overall>, "demographics": {"gen_z": <0-1>, '
    '"millennial": <0-1>, "gen_x": <0-1>, "boomer": <0-1>}, '
    '"best_fit": "<demographic name>", '
    '"summary": "<brief assessment>", "suggestions": ["<suggestion>", ...]}'
)

_DEMOGRAPHICS = ("gen_z", "millennial", "gen_x", "boomer")


class AudienceExecutor(BaseSkillExecutor):
    """Evaluates target audience fit of visual content."""

    SKILL_NAME = "audience_fit"

    def __init__(self) -> None:
        super().__init__(skill_name="audience_fit")

    async def execute(
        self, image_path: str, context: dict | None = None
    ) -> SkillResult:
        raw = await self._call_gemini(image_path, AUDIENCE_PROMPT)
        data = self._parse_json(raw)

        # Extract demographic scores
        demo_data = data.get("demographics", {})
        demographics = {
            d: float(demo_data.get(d, 0.5)) for d in _DEMOGRAPHICS
        }

        # Overall score: use LLM-provided or average of demographics
        if "score" in data:
            score = float(data["score"])
        else:
            score = sum(demographics.values()) / len(demographics)

        best_fit = data.get("best_fit", max(demographics, key=demographics.get))  # type: ignore[arg-type]
        summary = data.get("summary", "Audience fit analysis complete.")
        suggestions = data.get("suggestions", [])
        if isinstance(suggestions, str):
            suggestions = [suggestions]

        return SkillResult(
            skill_name=self.skill_name,
            score=round(score, 3),
            summary=summary,
            details={
                "demographics": demographics,
                "best_fit": best_fit,
            },
            suggestions=suggestions,
        )
