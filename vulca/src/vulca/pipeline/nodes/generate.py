"""GenerateNode -- image generation via Gemini or mock."""

from __future__ import annotations

import base64
import hashlib
import logging
import os
import time
from typing import Any

from vulca.pipeline.node import NodeContext, PipelineNode

logger = logging.getLogger("vulca")

# L-label → full dimension name (for refinement strategies)
_L_TO_DIM = {
    "L1": "visual_perception",
    "L2": "technical_analysis",
    "L3": "cultural_context",
    "L4": "critical_interpretation",
    "L5": "philosophical_aesthetic",
}

# Per-dimension refinement strategies (ported from old DraftAgent)
_REFINEMENT_STRATEGIES: dict[str, str] = {
    "visual_perception": (
        "Focus on visual composition: improve spatial arrangement, color harmony, "
        "contrast, line quality, and overall visual balance. Enhance the image's "
        "immediate visual impact."
    ),
    "technical_analysis": (
        "Improve technical execution: refine brushwork/rendering technique, "
        "material handling, detail precision, and craftsmanship quality. "
        "Ensure technical mastery is evident."
    ),
    "cultural_context": (
        "Strengthen cultural authenticity: incorporate tradition-specific symbols, "
        "motifs, and compositional conventions. Ensure the work reflects deep "
        "understanding of its cultural tradition's visual language."
    ),
    "critical_interpretation": (
        "Deepen interpretive layers: add narrative depth, symbolic richness, "
        "and art-historical references. The work should invite critical reading "
        "beyond surface aesthetics."
    ),
    "philosophical_aesthetic": (
        "Elevate philosophical dimension: embed philosophical concepts through "
        "visual metaphor, explore beauty/sublimity, and create contemplative depth. "
        "The work should transcend technique to reach aesthetic meaning."
    ),
}


class GenerateNode(PipelineNode):
    """Generate an image from a text prompt.

    Supports two providers:
    - ``mock``: returns a deterministic 1x1 PNG (no external calls).
    - ``nb2``: calls Google Gemini image generation model.

    On round >= 2, incorporates previous round's critique feedback into the
    generation prompt for targeted improvement.
    """

    name = "generate"

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        provider = ctx.provider or "mock"

        if provider == "mock":
            return self._mock_generate(ctx)

        return await self._gemini_generate(ctx)

    # ------------------------------------------------------------------
    # Mock provider
    # ------------------------------------------------------------------

    @staticmethod
    def _mock_generate(ctx: NodeContext) -> dict[str, Any]:
        """Return a deterministic 1x1 white PNG."""
        png_bytes = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05"
            b"\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_b64 = base64.b64encode(png_bytes).decode()
        candidate_id = hashlib.sha256(
            f"{ctx.subject}:{ctx.round_num}".encode()
        ).hexdigest()[:12]
        return {
            "image_b64": img_b64,
            "image_mime": "image/png",
            "candidate_id": candidate_id,
            "image_url": f"mock://{candidate_id}.png",
        }

    # ------------------------------------------------------------------
    # Cultural guidance for generation
    # ------------------------------------------------------------------

    @staticmethod
    def _build_generation_guidance(tradition: str) -> str:
        """Build cultural guidance for the generation prompt.

        Separate from _vlm.py's evaluation guidance — this tells the model
        HOW to create, not how to judge.
        """
        parts: list[str] = []

        try:
            from vulca.cultural.loader import get_tradition
            tc = get_tradition(tradition)
            if tc is None:
                return ""

            if tc.terminology:
                terms = "\n".join(
                    f"  - Apply {t.term} ({t.term_zh}): "
                    f"{t.definition if isinstance(t.definition, str) else t.definition.get('en', '')}"
                    for t in tc.terminology[:6]
                )
                parts.append(f"Cultural techniques to incorporate:\n{terms}")

            if tc.taboos:
                taboos = "\n".join(
                    f"  - AVOID: {t.rule}"
                    + (f" ({t.explanation})" if t.explanation else "")
                    for t in tc.taboos
                )
                parts.append(f"Cultural constraints (must respect):\n{taboos}")

        except Exception:
            pass

        return "\n\n".join(parts)

    # ------------------------------------------------------------------
    # Critique-driven improvement prompt (round >= 2)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_improvement_prompt(ctx: NodeContext) -> str:
        """Build improvement instructions from previous round's critique."""
        prev_scores: dict[str, float] = ctx.get("scores", {})
        prev_rationales: dict[str, str] = ctx.get("rationales", {})
        weakest: list[str] = ctx.get("weakest_dimensions", [])

        if not prev_scores:
            return ""

        if not weakest:
            sorted_dims = sorted(prev_scores.items(), key=lambda x: x[1])
            weakest = [d for d, _ in sorted_dims[:2]]

        parts = [
            f"IMPROVEMENT REQUIRED (Round {ctx.round_num}):",
            f"Previous round scored {ctx.get('weighted_total', 0.0):.2f} overall.",
            "\nWeakest dimensions to improve:",
        ]

        for dim in weakest:
            score = prev_scores.get(dim, 0.0)
            rationale = prev_rationales.get(f"{dim}_rationale", "")
            dim_name = _L_TO_DIM.get(dim, dim)
            strategy = _REFINEMENT_STRATEGIES.get(dim_name, "")

            parts.append(f"\n  {dim} ({score:.2f}/1.0):")
            if rationale:
                parts.append(f"    Critique: {rationale}")
            if strategy:
                parts.append(f"    Strategy: {strategy}")

        parts.append(
            "\nCreate a SIGNIFICANTLY improved version addressing these specific weaknesses. "
            "Maintain the strengths from the previous version."
        )

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Gemini image generation (NB2)
    # ------------------------------------------------------------------

    @staticmethod
    async def _gemini_generate(ctx: NodeContext) -> dict[str, Any]:
        """Call Google Gemini image generation model.

        Falls back to mock on quota/rate-limit errors so the pipeline
        continues instead of crashing.
        """
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ImportError(
                "google-genai package required for image generation: "
                "pip install google-genai"
            ) from exc

        api_key = (
            ctx.api_key
            or os.environ.get("GOOGLE_API_KEY", "")
            or os.environ.get("GEMINI_API_KEY", "")
        )
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY or GEMINI_API_KEY required for image generation"
            )

        prompt = ctx.get("prompt") or ctx.subject or ctx.intent
        tradition_hint = ctx.tradition.replace("_", " ")

        # Build the full prompt with cultural guidance
        prompt_parts = [
            f"Generate a high-quality artwork: {prompt}",
            f"Style: {tradition_hint} tradition",
        ]

        # Inject cultural guidance (terminology + taboos)
        cultural_guidance = GenerateNode._build_generation_guidance(ctx.tradition)
        if cultural_guidance:
            prompt_parts.append(f"\n{cultural_guidance}")

        # On round >= 2: inject critique-driven improvement instructions
        if ctx.round_num >= 2:
            improvement = GenerateNode._build_improvement_prompt(ctx)
            if improvement:
                prompt_parts.append(f"\n{improvement}")

        prompt_parts.append(
            "\nOutput image aspect ratio: 1:1, resolution: 1024x1024"
        )
        full_prompt = "\n".join(prompt_parts)

        logger.info(
            "GenerateNode round %d prompt (%d chars)",
            ctx.round_num,
            len(full_prompt),
        )

        t0 = time.monotonic()
        try:
            client = genai.Client(
                api_key=api_key,
                http_options={"timeout": 120_000},
            )

            response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    temperature=1.0,
                ),
            )

            # Extract image from response parts
            img_bytes = None
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data is not None:
                    img_bytes = part.inline_data.data
                    break

            if not img_bytes:
                raise RuntimeError("Gemini returned no image in response")

            latency_ms = int((time.monotonic() - t0) * 1000)
            img_b64 = base64.b64encode(img_bytes).decode()
            candidate_id = hashlib.sha256(
                f"{ctx.subject}:{ctx.round_num}:gemini".encode()
            ).hexdigest()[:12]

            logger.info(
                "Gemini generated image (%dms, %d bytes)",
                latency_ms,
                len(img_bytes),
            )

            return {
                "image_b64": img_b64,
                "image_mime": "image/png",
                "candidate_id": candidate_id,
                "image_url": f"gemini://{candidate_id}.png",
            }

        except Exception as exc:
            err = str(exc).lower()
            recoverable = any(
                k in err
                for k in ("429", "quota", "rate", "503", "unavailable", "timeout")
            )
            if recoverable:
                logger.warning(
                    "Gemini API quota/rate limit — falling back to mock: %s", exc
                )
                return GenerateNode._mock_generate(ctx)
            raise
