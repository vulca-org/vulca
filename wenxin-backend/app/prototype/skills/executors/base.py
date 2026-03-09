"""Base skill executor with shared Gemini calling infrastructure."""

import base64
import json
import re
from abc import ABC, abstractmethod
from pathlib import Path

import litellm

from app.prototype.agents.model_router import MODEL_FAST
from app.prototype.skills.types import SkillResult


class BaseSkillExecutor(ABC):
    """Abstract base class for all skill executors."""

    def __init__(self, skill_name: str):
        self.skill_name = skill_name

    @abstractmethod
    async def execute(
        self, image_path: str, context: dict | None = None
    ) -> SkillResult:
        """Execute the skill evaluation on the given image."""
        ...

    async def _call_gemini(self, image_path: str, prompt: str) -> str:
        """Shared Gemini call helper using LiteLLM."""
        img_bytes = Path(image_path).read_bytes()
        img_b64 = base64.b64encode(img_bytes).decode()
        suffix = Path(image_path).suffix.lower().lstrip(".")
        mime = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
        }.get(suffix, "image/png")

        response = await litellm.acompletion(
            model=MODEL_FAST,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{img_b64}",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            max_tokens=1024,
            temperature=0.2,
            timeout=30,
        )
        return response.choices[0].message.content or ""

    def _parse_score(self, text: str) -> float:
        """Extract a 0-1 score from LLM output."""
        match = re.search(r"\b(0\.\d+|1\.0|0|1)\b", text)
        return float(match.group()) if match else 0.5

    def _parse_json(self, text: str) -> dict:
        """Extract JSON object from LLM output, handling markdown fences."""
        # Strip markdown code fences if present
        cleaned = re.sub(r"```(?:json)?\s*", "", text)
        cleaned = cleaned.strip()
        # Find the first JSON object
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {}
