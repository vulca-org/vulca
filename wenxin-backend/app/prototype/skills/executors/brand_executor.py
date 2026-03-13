"""Brand consistency skill executor."""

from app.prototype.skills.executors.base import BaseSkillExecutor
from app.prototype.skills.types import SkillResult

BRAND_PROMPT = (
    "Analyze this image for brand consistency. Evaluate each dimension on a "
    "0-1 scale:\n"
    "- color_match: Color palette coherence\n"
    "- typography: Typography consistency\n"
    "- visual_identity: Visual identity strength\n"
    "- overall_coherence: Overall brand coherence\n\n"
    "Respond ONLY with JSON (no markdown):\n"
    '{"score": <0-1>, "color_match": <0-1>, "typography": <0-1>, '
    '"visual_identity": <0-1>, "overall_coherence": <0-1>, '
    '"summary": "<brief assessment>", "suggestions": ["<suggestion>", ...]}'
)

# Weights for computing the composite score
_WEIGHTS = {
    "color_match": 0.25,
    "typography": 0.25,
    "visual_identity": 0.30,
    "overall_coherence": 0.20,
}


class BrandExecutor(BaseSkillExecutor):
    """Evaluates brand consistency of visual content."""

    SKILL_NAME = "brand_consistency"

    def __init__(self) -> None:
        super().__init__(skill_name="brand_consistency")

    async def execute(
        self, image_path: str, context: dict | None = None
    ) -> SkillResult:
        raw = await self._call_gemini(image_path, BRAND_PROMPT)
        data = self._parse_json(raw)

        # Extract sub-scores with fallback
        color = float(data.get("color_match", 0.5))
        typo = float(data.get("typography", 0.5))
        identity = float(data.get("visual_identity", 0.5))
        coherence = float(data.get("overall_coherence", 0.5))

        # Weighted composite score
        score = (
            _WEIGHTS["color_match"] * color
            + _WEIGHTS["typography"] * typo
            + _WEIGHTS["visual_identity"] * identity
            + _WEIGHTS["overall_coherence"] * coherence
        )

        summary = data.get("summary", "Brand consistency analysis complete.")
        suggestions = data.get("suggestions", [])
        if isinstance(suggestions, str):
            suggestions = [suggestions]

        return SkillResult(
            skill_name=self.skill_name,
            score=round(score, 3),
            summary=summary,
            details={
                "color_match": color,
                "typography": typo,
                "visual_identity": identity,
                "overall_coherence": coherence,
                "weights": _WEIGHTS,
            },
            suggestions=suggestions,
        )
