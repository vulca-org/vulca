"""IntentAgent -- parses natural language intent into tradition + context.

Uses LiteLLM (Gemini) structured output to resolve user intent into
a cultural tradition identifier and evaluation context string.
"""

from __future__ import annotations

import json
import logging
import os
from typing import ClassVar

import litellm

from vulca.intent.types import IntentResult

logger = logging.getLogger(__name__)

_INTENT_MODEL = "gemini/gemini-2.5-pro"


def _google_api_key() -> str:
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""

__all__ = ["IntentAgent"]

_LEGACY_KNOWN_TRADITIONS = [
    "default", "chinese_xieyi", "chinese_gongbi", "western_academic",
    "islamic_geometric", "japanese_traditional", "watercolor",
    "african_traditional", "south_asian",
]


def _get_known_traditions() -> list[str]:
    """Dynamic tradition list from YAML loader with legacy fallback."""
    try:
        from vulca.cultural.loader import get_known_traditions
        traditions = get_known_traditions()
        if traditions:
            return traditions
    except Exception:
        logging.getLogger("vulca").debug("YAML traditions not available, using legacy list")
    return _LEGACY_KNOWN_TRADITIONS


_SYSTEM_PROMPT_TEMPLATE = (
    "You are a cultural art evaluation assistant. "
    "Parse the user's intent to determine which cultural tradition and context "
    "to use for evaluation.\n\n"
    "Known traditions: {traditions}\n\n"
    "Respond ONLY with valid JSON:\n"
    '{{"tradition": "<tradition_id>", "context": "<brief context>", "confidence": 0.XX}}'
)


class IntentAgent:
    """Resolves natural language intent into an IntentResult."""

    _instance: ClassVar[IntentAgent | None] = None

    @classmethod
    def get(cls) -> IntentAgent:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def resolve(self, intent: str) -> IntentResult:
        """Parse a natural language intent string into an IntentResult."""
        try:
            traditions = _get_known_traditions()
            system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
                traditions=", ".join(traditions),
            )

            extra: dict = {}
            api_key = _google_api_key()
            if api_key:
                extra["api_key"] = api_key

            response = await litellm.acompletion(
                model=_INTENT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
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
            if tradition not in traditions:
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
        if not text:
            return None
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            pass
        for marker in ["```json", "```"]:
            if marker in text:
                start = text.index(marker) + len(marker)
                end_pos = text.find("```", start)
                end = end_pos if end_pos != -1 else len(text)
                try:
                    return json.loads(text[start:end].strip())
                except (json.JSONDecodeError, ValueError):
                    pass
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
        return IntentResult(
            tradition="default",
            context="",
            confidence=0.0,
            raw_intent=intent,
        )
