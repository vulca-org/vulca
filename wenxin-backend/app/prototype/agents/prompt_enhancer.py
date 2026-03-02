"""Prompt Enhancer — LLM-based expansion of short user prompts into
detailed image generation instructions.

Uses Gemini Flash-Lite (free tier) to:
1. Expand semantic intent into visual descriptions
2. Inject cultural terminology in original language + English
3. Add compositional principles specific to the tradition
4. Structure output for maximum CLIP token efficiency

Part of Line D in the VULCA upgrade roadmap.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.prototype.agents.model_router import MODELS, ModelSpec
from app.prototype.utils.async_bridge import run_async_from_sync

logger = logging.getLogger(__name__)

__all__ = [
    "PromptEnhancer",
]

# ---------------------------------------------------------------------------
# System prompt for the enhancer LLM
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are an expert art prompt engineer for AI image generation models.
Your task is to expand a short art description into a detailed, structured
prompt optimized for diffusion models (FLUX / Stable Diffusion).

Rules:
1. Keep the output under 200 words (CLIP has token limits).
2. Include cultural terminology in BOTH the original language AND English.
   Example: "留白 (negative space)", "气韵生动 (spirit resonance)".
3. Add specific visual details: composition, color palette, texture, lighting.
4. Add tradition-specific technical terms (brushwork, materials, techniques).
5. Maintain the original artistic intent — do NOT change the subject.
6. Output ONLY the enhanced prompt text, nothing else. No explanations.
7. If evidence keywords are provided, weave them naturally into the prompt.
8. End with quality modifiers: "masterpiece, museum quality, highly detailed".
"""

_USER_TEMPLATE = """\
Tradition: {tradition}
Original prompt: {subject}
{evidence_section}
Write an enhanced image generation prompt for this artwork."""

# ---------------------------------------------------------------------------
# PromptEnhancer
# ---------------------------------------------------------------------------


class PromptEnhancer:
    """Expand short prompts into detailed generation instructions via LLM.

    Parameters
    ----------
    model_key : str
        Key in MODELS dict. Default "gemini_flash_lite" (free tier).
    enabled : bool
        If False, enhance() returns the original prompt unchanged.
    """

    def __init__(
        self,
        model_key: str = "gemini_flash_lite",
        enabled: bool = True,
    ) -> None:
        self._model_key = model_key
        self._enabled = enabled
        self._model_spec: ModelSpec | None = MODELS.get(model_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enhance(
        self,
        subject: str,
        cultural_tradition: str,
        evidence: dict | None = None,
    ) -> str:
        """Enhance a short prompt into a detailed generation instruction.

        Parameters
        ----------
        subject : str
            The raw user prompt (e.g. "phoenix rising from ashes").
        cultural_tradition : str
            Art tradition key (e.g. "chinese_xieyi", "islamic_geometric").
        evidence : dict | None
            Scout evidence dict with terminology_hits, taboo_violations, etc.

        Returns
        -------
        str
            Enhanced prompt string, or original subject on failure.
        """
        if not self._enabled:
            return subject
        if not self._model_spec:
            logger.debug("PromptEnhancer: model %s not found, returning original", self._model_key)
            return subject
        if not self._model_spec.get_api_key():
            logger.debug("PromptEnhancer: no API key for %s, returning original", self._model_key)
            return subject

        try:
            result = self._run_async(
                self._enhance_async(subject, cultural_tradition, evidence)
            )
            if result and result.strip() != subject.strip():
                logger.info(
                    "Prompt enhanced: %d→%d chars",
                    len(subject), len(result),
                )
                return result
        except Exception as exc:  # noqa: BLE001
            logger.warning("Prompt enhancement failed, using original: %s", exc)

        return subject

    # ------------------------------------------------------------------
    # Async implementation
    # ------------------------------------------------------------------

    async def _enhance_async(
        self,
        subject: str,
        tradition: str,
        evidence: dict | None,
    ) -> str:
        """Call LLM to enhance the prompt."""
        import litellm

        spec = self._model_spec
        if spec is None:
            return subject

        # Build evidence section
        evidence_section = ""
        if evidence:
            parts = []
            for hit in evidence.get("terminology_hits", []):
                term = hit.get("term", "")
                if term:
                    parts.append(term)
            if parts:
                evidence_section = f"Cultural keywords: {', '.join(parts[:10])}"

        user_msg = _USER_TEMPLATE.format(
            tradition=tradition.replace("_", " "),
            subject=subject,
            evidence_section=evidence_section,
        )

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]

        extra_kwargs: dict = {}
        api_base = spec.get_api_base()
        api_key = spec.get_api_key()
        if api_base:
            extra_kwargs["api_base"] = api_base
        if api_key:
            extra_kwargs["api_key"] = api_key

        t0 = time.monotonic()
        response = await litellm.acompletion(
            model=spec.litellm_id,
            messages=messages,
            max_tokens=512,
            temperature=0.7,  # slightly creative for prompts
            timeout=25,  # must finish before ThreadPoolExecutor's 30s timeout
            **extra_kwargs,
        )
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        logger.debug("Prompt enhance LLM call: %dms", elapsed_ms)

        if response and response.choices:
            content = response.choices[0].message.content
            if content:
                # Clean up: remove quotes, leading/trailing whitespace
                enhanced = content.strip().strip('"').strip("'")
                if enhanced:
                    return enhanced
                logger.debug("Prompt enhancement returned empty after stripping; using original")

        return subject

    # ------------------------------------------------------------------
    # Sync→Async bridge (same pattern as CriticLLMAgent)
    # ------------------------------------------------------------------

    @staticmethod
    def _run_async(coro: Any) -> Any:
        """Run an async coroutine from sync context (delegates to shared pool)."""
        return run_async_from_sync(coro, timeout=30)
