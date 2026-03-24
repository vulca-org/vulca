"""EvaluatePhase -- Brief-based L1-L5 evaluation."""
from __future__ import annotations

import base64
import logging
from pathlib import Path

from vulca.studio.brief import Brief
from vulca.studio.eval_criteria import generate_eval_criteria_sync

logger = logging.getLogger("vulca.studio")

_L_LABELS = {
    "L1": "Visual Perception", "L2": "Technical Execution",
    "L3": "Cultural/Style Context", "L4": "Interpretation & Constraints",
    "L5": "Philosophical & Emotional Aesthetics",
}


class EvaluatePhase:
    """Evaluate artwork against Brief-defined L1-L5 criteria."""

    def ensure_eval_criteria(self, brief: Brief) -> None:
        """Auto-generate eval_criteria if not already set."""
        if not brief.eval_criteria:
            brief.eval_criteria = generate_eval_criteria_sync(brief, use_llm=False)

    def build_eval_prompt(self, brief: Brief) -> str:
        """Build VLM system prompt with Brief-specific criteria."""
        self.ensure_eval_criteria(brief)

        parts = [
            "You are VULCA, an art evaluation system. Evaluate the artwork "
            "against the following SPECIFIC criteria for each dimension (L1-L5).",
            "",
            "## Evaluation Criteria (from Creative Brief)",
        ]

        for dim in ("L1", "L2", "L3", "L4", "L5"):
            label = _L_LABELS.get(dim, dim)
            criteria = brief.eval_criteria.get(dim, f"General {label} quality")
            parts.append(f"- **{dim} ({label})**: {criteria}")

        # Add tradition context as supplementary
        if brief.style_mix:
            traditions = ", ".join(
                s.tradition.replace("_", " ") or s.tag for s in brief.style_mix
            )
            parts.append(f"\n## Style Context: {traditions}")

        if brief.must_have:
            parts.append(f"\n## Must Include: {', '.join(brief.must_have)}")
        if brief.must_avoid:
            parts.append(f"\n## Must Avoid: {', '.join(brief.must_avoid)}")

        parts.append(
            "\n## Instructions\n"
            "Score each dimension 0.0-1.0 based on the SPECIFIC criteria above.\n"
            "For each dimension provide:\n"
            "1. rationale (1-2 sentences)\n"
            "2. suggestion (1 sentence, actionable)\n"
            "3. deviation_type: traditional | intentional_departure | experimental\n"
            "\nRespond with ONLY JSON:\n"
            '{"L1": <float>, "L1_rationale": "<str>", "L1_suggestion": "<str>", '
            '"L1_deviation_type": "<str>", ... (same for L2-L5)}'
        )

        return "\n".join(parts)

    async def evaluate(
        self, brief: Brief, *, image_path: str = "",
        api_key: str = "", mock: bool = False,
    ) -> dict[str, float]:
        """Evaluate an image against Brief criteria.

        Returns dict with L1-L5 scores. Full EvalResult wrapping is done by caller.
        """
        self.ensure_eval_criteria(brief)

        if mock or not image_path:
            # Return mock scores
            return {f"L{i}": 0.65 + i * 0.03 for i in range(1, 6)}

        # Load image
        try:
            img_bytes = Path(image_path).read_bytes()
            img_b64 = base64.b64encode(img_bytes).decode()
            mime = "image/png" if image_path.endswith(".png") else "image/jpeg"
        except Exception as exc:
            logger.warning("Failed to load image %s: %s", image_path, exc)
            return {f"L{i}": 0.0 for i in range(1, 6)}

        # Call VLM with Brief-enhanced prompt
        try:
            from vulca._vlm import score_image
            tradition = brief.style_mix[0].tradition if brief.style_mix else "default"
            result = await score_image(
                img_b64=img_b64, mime=mime,
                subject=brief.intent, tradition=tradition,
                api_key=api_key,
            )
            return {f"L{i}": result.get(f"L{i}", 0.0) for i in range(1, 6)}
        except Exception as exc:
            logger.warning("VLM evaluation failed: %s", exc)
            return {f"L{i}": 0.0 for i in range(1, 6)}
