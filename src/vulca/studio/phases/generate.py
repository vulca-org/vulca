"""GeneratePhase -- Brief-driven precise image generation."""
from __future__ import annotations

import base64
import logging
from pathlib import Path

from vulca.studio.brief import Brief
from vulca.studio.types import GenerationRound

logger = logging.getLogger("vulca.studio")


class GeneratePhase:
    """Generate artwork from a locked Brief with structured prompt."""

    def build_prompt(self, brief: Brief) -> str:
        parts = [f"Create a high-quality artwork: {brief.intent}"]

        if brief.selected_concept:
            parts.append(
                "Use the provided reference image as a composition and style guide. "
                "Preserve its layout while rendering at full quality and detail."
            )

        if brief.reference_path:
            ref_prompts = {
                "style": (
                    "Apply the style, color palette, and brushwork of the reference image "
                    "to this artwork. Do not copy the composition."
                ),
                "composition": (
                    "Use the reference image as a composition and spatial layout guide. "
                    "Apply different style and colors."
                ),
                "full": (
                    "Use the reference image as both a style guide and composition blueprint. "
                    "Match its visual language and spatial arrangement."
                ),
            }
            ref_type = brief.reference_type if brief.reference_type in ref_prompts else "full"
            parts.append(ref_prompts[ref_type])

        # Style
        if brief.style_mix:
            styles = ", ".join(s.tradition.replace("_", " ") or s.tag for s in brief.style_mix)
            parts.append(f"\n## Style\n{styles}")

        # Composition directives
        if brief.composition.layout or brief.composition.focal_point:
            parts.append("\n## Composition")
            if brief.composition.layout:
                parts.append(f"Layout: {brief.composition.layout}")
            if brief.composition.focal_point:
                parts.append(f"Focal point: {brief.composition.focal_point}")
            if brief.composition.negative_space:
                parts.append(f"Negative space: {brief.composition.negative_space}")

        # Palette directives
        if brief.palette.primary or brief.palette.accent or brief.palette.mood:
            parts.append("\n## Color Palette")
            if brief.palette.primary:
                parts.append(f"Primary colors: {', '.join(brief.palette.primary)}")
            if brief.palette.accent:
                parts.append(f"Accent colors: {', '.join(brief.palette.accent)}")
            if brief.palette.mood:
                parts.append(f"Color mood: {brief.palette.mood}")

        # Elements
        if brief.elements:
            elems = "\n".join(f"  - {e.name} ({e.category})" for e in brief.elements)
            parts.append(f"\n## Elements to Include\n{elems}")

        # Constraints
        if brief.must_have:
            parts.append(f"\n## Must Include\n{', '.join(brief.must_have)}")
        if brief.must_avoid:
            parts.append(f"\n## Must Avoid\n{', '.join(brief.must_avoid)}")

        # Mood
        if brief.mood:
            parts.append(f"\n## Mood/Atmosphere\n{brief.mood}")

        parts.append("\nOutput: high-resolution artwork, no text or watermarks.")
        return "\n".join(parts)

    async def generate(
        self, brief: Brief, *, provider: str = "mock",
        project_dir: str = "", api_key: str = "",
    ) -> str:
        project = Path(project_dir) if project_dir else Path(".")
        output_dir = project / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        prompt = self.build_prompt(brief)
        round_num = len(brief.generations) + 1

        try:
            from vulca.providers import get_image_provider
            # TODO(v0.21): plumb model/quality from create_artwork MCP signature —
            # currently silently defaults to OpenAIImageProvider's gpt-image-1.
            # The user-facing fix is the same shape as redraw.py:524 (per-call
            # `provider.model = model` after instantiation). v0.20 PR audit.
            img_provider = get_image_provider(provider, api_key=api_key)
        except Exception:
            filepath = output_dir / f"r{round_num}.png"
            filepath.write_bytes(b"placeholder")
            brief.generations.append(GenerationRound(round_num=round_num, image_path=str(filepath)))
            return str(filepath)

        reference_b64 = ""
        if brief.selected_concept:
            try:
                reference_b64 = base64.b64encode(Path(brief.selected_concept).read_bytes()).decode()
            except Exception:
                pass

        result = await img_provider.generate(
            prompt,
            tradition=brief.style_mix[0].tradition if brief.style_mix else "",
            subject=brief.intent,
            reference_image_b64=reference_b64,
        )

        mime = result.mime
        if "svg" in mime:
            ext = "svg"
        elif "png" in mime:
            ext = "png"
        else:
            ext = "jpg"

        filepath = output_dir / f"r{round_num}.{ext}"
        filepath.write_bytes(base64.b64decode(result.image_b64))

        brief.generations.append(GenerationRound(
            round_num=round_num,
            image_path=str(filepath),
        ))

        return str(filepath)
