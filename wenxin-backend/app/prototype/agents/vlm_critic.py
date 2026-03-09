"""VLM Critic — Vision-Language Model based image evaluation for L1-L5.

Replaces CLIP-based `ImageScorer` with Gemini 2.5 Flash VLM for:
1. Real visual understanding (not just text-image cosine similarity)
2. Cultural terminology awareness (multi-language)
3. Compositional and aesthetic judgement
4. Taboo/violation detection (L4 — impossible with CLIP)

API: Same dict format as ImageScorer so it's a drop-in replacement
in CriticRules._blend_image_scores().

Part of Line A in the VULCA upgrade roadmap.
"""

from __future__ import annotations

import base64
import json
import logging
import time
from pathlib import Path
from typing import Any

from app.prototype.agents.model_router import MODELS, ModelSpec
from app.prototype.utils.async_bridge import run_async_from_sync

logger = logging.getLogger(__name__)

__all__ = [
    "VLMCritic",
]

# ---------------------------------------------------------------------------
# VLM evaluation prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are an expert art critic evaluating AI-generated artwork across 5 cultural
dimensions. You will see an image and its context. Score each dimension 0.0-1.0.

Scoring guide:
- 0.0-0.2: Poor / major issues
- 0.2-0.4: Below average / noticeable problems
- 0.4-0.6: Average / acceptable
- 0.6-0.8: Good / well-executed
- 0.8-1.0: Excellent / masterful

Dimensions:
- L1 (Visual Perception): Composition, layout, spatial arrangement, visual clarity
- L2 (Technical Execution): Rendering quality, detail, technique fidelity, resolution
- L3 (Cultural Context): Fidelity to cultural tradition, correct terminology usage,
  traditional elements present (e.g., 留白 for xieyi, tessellation for Islamic)
- L4 (Critical Interpretation): No taboo violations, respectful representation,
  avoidance of cultural insensitivity or misrepresentation
- L5 (Philosophical/Aesthetic): Artistic depth, emotional resonance, aesthetic harmony,
  spiritual quality appropriate to the tradition

Output ONLY valid JSON (no markdown, no explanation):
{"L1": 0.XX, "L2": 0.XX, "L3": 0.XX, "L4": 0.XX, "L5": 0.XX,
 "L1_rationale": "brief reason",
 "L2_rationale": "brief reason",
 "L3_rationale": "brief reason",
 "L4_rationale": "brief reason",
 "L5_rationale": "brief reason"}"""

_USER_TEMPLATE = """\
Evaluate this AI-generated artwork.

Subject: {subject}
Cultural Tradition: {tradition}
Generation Prompt: {prompt}
{evidence_section}

Score all 5 dimensions (L1-L5) as JSON."""

# ---------------------------------------------------------------------------
# VLMCritic
# ---------------------------------------------------------------------------


class VLMCritic:
    """VLM-based image scorer for L1-L5 dimensions.

    Drop-in replacement for ImageScorer — same return dict format.
    Uses Gemini 2.5 Flash VLM via model_router.
    """

    _instance: VLMCritic | None = None

    @classmethod
    def get(cls) -> VLMCritic:
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(
        self,
        model_key: str = "gemini_direct",
    ) -> None:
        self._model_key = model_key
        self._model_spec: ModelSpec | None = MODELS.get(model_key)
        self._available: bool | None = None
        self._consecutive_failures: int = 0
        self._max_consecutive_failures: int = 3
        self._circuit_break_time: float = 0.0  # monotonic timestamp of last break
        self._circuit_break_cooldown_sec: float = 120.0  # retry after 2 minutes

    @property
    def available(self) -> bool:
        """Check if VLM model is configured and has API key."""
        if self._available is not None:
            # Circuit breaker recovery: retry after cooldown period
            if not self._available and self._circuit_break_time > 0:
                import time as _time
                if _time.monotonic() - self._circuit_break_time > self._circuit_break_cooldown_sec:
                    logger.info("VLM circuit breaker cooldown expired, retrying availability check")
                    self._available = None
                    self._consecutive_failures = 0
                    # Fall through to re-check below
                else:
                    return False
            else:
                return self._available
        if self._model_spec is None:
            self._available = False
            return False
        key = self._model_spec.get_api_key()
        self._available = bool(key)
        return self._available

    def score_image(
        self,
        image_path: str,
        subject: str,
        cultural_tradition: str,
        prompt: str = "",
        evidence: dict | None = None,
    ) -> dict[str, float] | None:
        """Score image on L1-L5 using VLM.

        Returns dict compatible with ImageScorer format:
        {"L1": float, "L2": float, "L3": float, "L5": float,
         "L4": float,  # NEW: VLM can do taboo detection
         "_L1_raw": float, ...}

        Returns None if VLM unavailable or image not found.
        """
        if not self.available:
            logger.debug("VLM critic unavailable (no API key)")
            return None

        path = Path(image_path)
        if not path.exists():
            logger.debug("Image not found for VLM scoring: %s", image_path)
            return None

        try:
            result = self._run_async(
                self._score_async(
                    image_path=str(path),
                    subject=subject,
                    tradition=cultural_tradition,
                    prompt=prompt,
                    evidence=evidence,
                )
            )
            self._consecutive_failures = 0  # Reset on success
            return result
        except Exception as exc:  # noqa: BLE001
            self._consecutive_failures += 1
            logger.warning(
                "VLM scoring failed for %s (%d/%d): %s",
                image_path, self._consecutive_failures,
                self._max_consecutive_failures, exc,
            )
            # Disable after N consecutive failures to avoid repeated timeouts.
            # Singleton is reset between ablation conditions by run_ablation.
            if self._consecutive_failures >= self._max_consecutive_failures:
                import time as _time
                logger.error("VLM disabled after %d consecutive failures (will retry in %.0fs)",
                             self._consecutive_failures, self._circuit_break_cooldown_sec)
                self._available = False
                self._circuit_break_time = _time.monotonic()
            return None

    # ------------------------------------------------------------------
    # Async implementation
    # ------------------------------------------------------------------

    async def _score_async(
        self,
        image_path: str,
        subject: str,
        tradition: str,
        prompt: str = "",
        evidence: dict | None = None,
    ) -> dict[str, float] | None:
        """Call VLM to score the image."""
        import litellm

        spec = self._model_spec
        if spec is None:
            return None

        # Encode image to base64
        image_b64, mime_type = self._encode_image(image_path)
        if not image_b64:
            return None

        # Build evidence section
        evidence_section = ""
        if evidence:
            parts = []
            for hit in evidence.get("terminology_hits", []):
                term = hit.get("term", "")
                if term:
                    parts.append(term)
            if parts:
                evidence_section = f"Cultural keywords: {', '.join(parts[:8])}"
            taboos = evidence.get("taboo_violations", [])
            if taboos:
                taboo_strs = [v.get("description", "") for v in taboos[:3]]
                evidence_section += f"\nKnown taboos: {'; '.join(taboo_strs)}"

        # Append prompt archetypes from PromptDistiller (WU-01)
        try:
            from app.prototype.cultural_pipelines.cultural_weights import get_prompt_archetypes
            archetypes = get_prompt_archetypes(tradition, top_n=5)
            if archetypes:
                pattern_strs = [
                    f"{a.get('pattern', '?')} (avg {a.get('avg_score', 0):.2f})"
                    for a in archetypes[:5]
                ]
                evidence_section += f"\nSuccessful patterns: {', '.join(pattern_strs)}"
        except Exception:
            pass  # Graceful degradation — archetypes are optional context

        user_text = _USER_TEMPLATE.format(
            subject=subject,
            tradition=tradition.replace("_", " "),
            prompt=prompt or subject,
            evidence_section=evidence_section,
        )

        # Inject evolved context into system prompt (before JSON format instructions)
        system_prompt = _SYSTEM_PROMPT
        try:
            from app.prototype.cultural_pipelines.cultural_weights import get_evolved_prompt_context
            evolved = get_evolved_prompt_context(tradition)
            if evolved:
                # Insert before the JSON output instruction line
                json_instruction = "\nOutput ONLY valid JSON"
                if json_instruction in system_prompt:
                    idx = system_prompt.index(json_instruction)
                    system_prompt = system_prompt[:idx] + evolved + system_prompt[idx:]
                else:
                    system_prompt += evolved
        except Exception:
            pass  # Zero regression — on any error, use original prompt

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_b64}",
                        },
                    },
                    {
                        "type": "text",
                        "text": user_text,
                    },
                ],
            },
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
            max_tokens=4096,  # Gemini 2.5 Flash thinking tokens count toward limit
            temperature=0.1,  # low temp for consistent scoring
            timeout=55,  # must finish before ThreadPoolExecutor's 60s timeout
            **extra_kwargs,
        )
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        logger.info("VLM critic call: %dms for %s", elapsed_ms, image_path)

        if not response or not response.choices:
            return None

        content = response.choices[0].message.content
        if not content:
            return None

        return self._parse_scores(content)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _encode_image(image_path: str) -> tuple[str, str]:
        """Encode image to base64 with MIME type detection."""
        path = Path(image_path)
        suffix = path.suffix.lower()

        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        mime_type = mime_map.get(suffix, "image/png")

        try:
            data = path.read_bytes()
            # Auto-detect from magic bytes
            if data[:4] == b"\x89PNG":
                mime_type = "image/png"
            elif data[:2] == b"\xff\xd8":
                mime_type = "image/jpeg"
            elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
                mime_type = "image/webp"

            return base64.b64encode(data).decode("ascii"), mime_type
        except Exception as exc:
            logger.warning("Failed to encode image %s: %s", image_path, exc)
            return "", ""

    @staticmethod
    def _parse_scores(content: str) -> dict[str, float] | None:
        """Parse VLM JSON response into scores dict.

        Handles both clean JSON and markdown-wrapped JSON.
        """
        # Strip markdown code block if present (handles trailing newlines)
        text = content.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove opening ``` line
            lines = lines[1:]
            # Remove closing ``` line (may have trailing whitespace/newlines)
            while lines and lines[-1].strip() in ("", "```"):
                lines.pop()
            text = "\n".join(lines).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from mixed content
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    data = json.loads(text[start:end])
                except json.JSONDecodeError:
                    logger.warning("Failed to parse VLM response as JSON: %s", text[:200])
                    return None
            else:
                logger.warning("No JSON found in VLM response: %s", text[:200])
                return None

        # Extract and validate scores
        result: dict[str, float] = {}
        for key in ("L1", "L2", "L3", "L4", "L5"):
            val = data.get(key)
            if val is not None:
                try:
                    score = float(val)
                    result[key] = max(0.0, min(1.0, score))
                    result[f"_{key}_raw"] = score
                except (TypeError, ValueError):
                    # Don't assign a sentinel 0.5 — leave the dimension
                    # missing so the completeness check below rejects the
                    # entire response (avoids phantom scores)
                    logger.warning("VLM returned unparseable value for %s: %r", key, val)

        # Extract rationales (for logging/debugging)
        for key in ("L1", "L2", "L3", "L4", "L5"):
            rationale_key = f"{key}_rationale"
            if rationale_key in data:
                result[rationale_key] = str(data[rationale_key])

        if len([k for k in result if not k.startswith("_") and "_rationale" not in k]) < 5:
            logger.warning("VLM returned fewer than 5 dimension scores (L1-L5)")
            return None

        return result

    # ------------------------------------------------------------------
    # Sync→Async bridge
    # ------------------------------------------------------------------

    @staticmethod
    def _run_async(coro: Any) -> Any:
        """Run an async coroutine from sync context (delegates to shared pool)."""
        return run_async_from_sync(coro, timeout=30)
