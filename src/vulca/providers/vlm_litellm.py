"""LiteLLM-based VLM scoring provider."""
from __future__ import annotations

import json
import os
import re

from vulca.providers.base import L1L5Scores, VLMProvider
from vulca.providers.retry import with_retry


class LiteLLMVLMProvider:
    """VLM scoring via any LiteLLM-supported model."""

    def __init__(self, model: str = "", api_key: str = ""):
        self.model = model or os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash")
        self.api_key = api_key

    async def score(
        self,
        image_b64: str,
        *,
        tradition: str = "",
        subject: str = "",
        guidance: str = "",
        **kwargs,
    ) -> L1L5Scores:
        import litellm

        prompt = guidance or self._default_prompt(tradition, subject)

        messages = [
            {"role": "system", "content": "You are VULCA, an AI art critic. Score the image on L1-L5 dimensions. Return JSON only."},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                {"type": "text", "text": prompt},
            ]},
        ]

        call_kwargs = {"model": self.model, "messages": messages, "temperature": 0.3, "max_tokens": 2000}
        if self.api_key:
            call_kwargs["api_key"] = self.api_key

        def _is_retryable(exc: Exception) -> bool:
            # litellm surfaces HTTP status via status_code attribute or message
            status = getattr(exc, "status_code", None)
            if status in (429, 500, 503):
                return True
            # Timeout and connection errors are retryable
            exc_name = type(exc).__name__
            if "Timeout" in exc_name or "RateLimit" in exc_name or "ServiceUnavailable" in exc_name:
                return True
            return False

        async def _call() -> L1L5Scores:
            response = await litellm.acompletion(**call_kwargs)
            text = response.choices[0].message.content or ""
            return self._parse_response(text)

        return await with_retry(
            _call,
            max_retries=3,
            base_delay_ms=500,
            max_delay_ms=16_000,
            retryable_check=_is_retryable,
        )

    def _default_prompt(self, tradition: str, subject: str) -> str:
        parts = ["Score this image on five dimensions (0.0-1.0). Return JSON with keys L1-L5 and L1_rationale through L5_rationale."]
        if tradition:
            parts.append(f"Cultural tradition: {tradition}")
        if subject:
            parts.append(f"Subject: {subject}")
        return "\n".join(parts)

    def _parse_response(self, text: str) -> L1L5Scores:
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON found in VLM response: {text[:200]}")
        data = json.loads(json_match.group())

        scores = {}
        rationales = {}
        for level in ("L1", "L2", "L3", "L4", "L5"):
            scores[level] = float(data.get(level, 0.5))
            rationales[level] = data.get(f"{level}_rationale", "")

        return L1L5Scores(**scores, rationales=rationales)
