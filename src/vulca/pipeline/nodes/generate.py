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

    # Tradition → background color for mock SVG placeholders
    _TRADITION_COLORS: dict[str, str] = {
        "chinese_xieyi": "#3a3a3a",
        "chinese_gongbi": "#c43f2f",
        "japanese_traditional": "#264653",
        "japanese_wabi_sabi": "#264653",
        "islamic_geometric": "#2a9d8f",
        "watercolor": "#89c2d9",
        "western_academic": "#8a5a44",
        "western_classical": "#8a5a44",
        "african_traditional": "#bc6c25",
        "african_ubuntu": "#bc6c25",
        "south_asian": "#e9c46a",
        "persian_miniature": "#2a9d8f",
        "korean_minhwa": "#5F8A50",
    }

    @staticmethod
    def _mock_generate(ctx: NodeContext) -> dict[str, Any]:
        """Return a deterministic SVG placeholder with tradition/subject info."""
        candidate_id = hashlib.sha256(
            f"{ctx.subject}:{ctx.round_num}".encode()
        ).hexdigest()[:12]
        tradition = ctx.tradition or "default"
        bg = GenerateNode._TRADITION_COLORS.get(tradition, "#5F8A50")
        tradition_display = tradition.replace("_", " ").title()
        subject_display = (ctx.subject or "Untitled")[:50]
        # Escape XML special characters
        for old, new in [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;")]:
            subject_display = subject_display.replace(old, new)
            tradition_display = tradition_display.replace(old, new)

        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512">'
            f'<rect width="512" height="512" fill="{bg}" rx="24"/>'
            f'<text x="256" y="200" text-anchor="middle" font-size="28" '
            f'fill="white" font-family="sans-serif">{tradition_display}</text>'
            f'<text x="256" y="256" text-anchor="middle" font-size="20" '
            f'fill="rgba(255,255,255,0.7)" font-family="sans-serif">Round {ctx.round_num}</text>'
            f'<text x="256" y="310" text-anchor="middle" font-size="16" '
            f'fill="rgba(255,255,255,0.5)" font-family="sans-serif">{subject_display}</text>'
            f'<text x="256" y="420" text-anchor="middle" font-size="14" '
            f'fill="rgba(255,255,255,0.3)" font-family="sans-serif">VULCA Preview</text>'
            f'</svg>'
        )
        img_b64 = base64.b64encode(svg.encode()).decode()
        return {
            "image_b64": img_b64,
            "image_mime": "image/svg+xml",
            "candidate_id": candidate_id,
            "image_url": f"mock://{candidate_id}.svg",
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

        # Also check node_params for improvement_focus (from HITL rerun)
        node_params = ctx.get("node_params") or {}
        gen_params = node_params.get("generate") or {}
        improvement_focus = gen_params.get("improvement_focus", [])
        if improvement_focus and not weakest:
            weakest = improvement_focus

        if not prev_scores:
            # Even without prev_scores, if we have improvement_focus, generate guidance
            if improvement_focus:
                dim_names = [_L_TO_DIM.get(d, d) for d in improvement_focus]
                strategies = [_REFINEMENT_STRATEGIES.get(dn, "") for dn in dim_names]
                parts = [f"IMPROVEMENT FOCUS (Round {ctx.round_num}):"]
                for dim, strategy in zip(improvement_focus, strategies):
                    parts.append(f"\n  Focus on {_L_TO_DIM.get(dim, dim)}:")
                    if strategy:
                        parts.append(f"    Strategy: {strategy}")
                return "\n".join(parts)
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

        # Reference image guidance (check both top-level and node_params)
        ref_b64 = ctx.get("reference_image_b64")
        if not ref_b64:
            node_params = ctx.get("node_params") or {}
            gen_params = node_params.get("generate") or {}
            ref_b64 = gen_params.get("reference_image_b64")
        if ref_b64:
            prompt_parts.append(
                "\nUse the provided reference image as style/composition guidance. "
                "Incorporate its aesthetic qualities while creating an original work."
            )

        prompt_parts.append(
            "\nOutput image aspect ratio: 1:1, resolution: 1024x1024"
        )
        full_prompt = "\n".join(prompt_parts)

        logger.info(
            "GenerateNode round %d prompt (%d chars%s)",
            ctx.round_num,
            len(full_prompt),
            ", +ref_image" if ref_b64 else "",
        )

        t0 = time.monotonic()
        try:
            client = genai.Client(
                api_key=api_key,
                http_options={"timeout": 120_000},
            )

            # Build contents: text prompt + optional reference image
            contents: list[Any] = [full_prompt]
            if ref_b64:
                try:
                    ref_bytes = base64.b64decode(ref_b64)
                    contents.insert(0, types.Part.from_bytes(
                        data=ref_bytes,
                        mime_type="image/png",
                    ))
                except Exception as ref_err:
                    logger.warning("Failed to decode reference image: %s", ref_err)

            response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=contents,
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
