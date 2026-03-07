"""IntentAgent — parses natural language intent into tradition + context.

Uses LiteLLM (Gemini) structured output to resolve user intent into
a cultural tradition identifier and evaluation context string.
Singleton pattern consistent with VLMCritic.
"""

from __future__ import annotations

import json
import logging
from typing import ClassVar

import litellm

from app.prototype.agents.model_router import MODELS
from app.prototype.intent.types import IntentResult

logger = logging.getLogger(__name__)

__all__ = ["IntentAgent"]

_KNOWN_TRADITIONS = [
    "default", "chinese_xieyi", "chinese_gongbi", "western_academic",
    "islamic_geometric", "japanese_traditional", "watercolor",
    "african_traditional", "south_asian",
]

_SYSTEM_PROMPT = (
    "You are a cultural art evaluation assistant. "
    "Parse the user's intent to determine which cultural tradition and context "
    "to use for evaluation.\n\n"
    "Known traditions: " + ", ".join(_KNOWN_TRADITIONS) + "\n\n"
    "Respond ONLY with valid JSON:\n"
    '{"tradition": "<tradition_id>", "context": "<brief context>", "confidence": 0.XX}'
)


class IntentAgent:
    """Resolves natural language intent into an IntentResult."""

    _instance: ClassVar[IntentAgent | None] = None

    @classmethod
    def get(cls) -> IntentAgent:
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def resolve(self, intent: str) -> IntentResult:
        """Parse a natural language intent string into an IntentResult.

        Falls back to tradition='default' if parsing fails.
        """
        try:
            spec = MODELS.get("gemini_direct")
            if spec is None:
                logger.warning("IntentAgent: gemini_direct model not configured, using default")
                return self._fallback(intent)

            extra: dict = {}
            api_base = spec.get_api_base()
            api_key = spec.get_api_key()
            if api_base:
                extra["api_base"] = api_base
            if api_key:
                extra["api_key"] = api_key

            response = await litellm.acompletion(
                model=spec.litellm_id,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": intent},
                ],
                max_tokens=256,
                temperature=0.1,
                timeout=30,
                **extra,
            )

            text = response.choices[0].message.content or ""
            parsed = self._parse_response(text)
            if parsed is None:
                return self._fallback(intent)

            tradition = parsed.get("tradition", "default")
            if tradition not in _KNOWN_TRADITIONS:
                tradition = "default"

            return IntentResult(
                tradition=tradition,
                context=parsed.get("context", ""),
                confidence=float(parsed.get("confidence", 0.5)),
                raw_intent=intent,
            )

        except Exception:
            logger.exception("IntentAgent.resolve failed")
            return self._fallback(intent)

    @staticmethod
    def _parse_response(text: str) -> dict | None:
        """Extract JSON from LLM response text."""
        if not text:
            return None
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            pass
        # Try extracting from markdown code block
        for marker in ["```json", "```"]:
            if marker in text:
                start = text.index(marker) + len(marker)
                end_pos = text.find("```", start)
                end = end_pos if end_pos != -1 else len(text)
                try:
                    return json.loads(text[start:end].strip())
                except (json.JSONDecodeError, ValueError):
                    pass
        # Try finding { ... } substring
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end > brace_start:
            try:
                return json.loads(text[brace_start : brace_end + 1])
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    @staticmethod
    def _fallback(intent: str) -> IntentResult:
        """Return a safe default when parsing fails."""
        return IntentResult(
            tradition="default",
            context="",
            confidence=0.0,
            raw_intent=intent,
        )
