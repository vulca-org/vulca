"""ConceptPhase -- generate concept designs (sketch + composition + palette merged)."""
from __future__ import annotations

import base64
import logging
from pathlib import Path

from vulca.studio.brief import Brief

logger = logging.getLogger("vulca.studio")


class ConceptPhase:
    def build_concept_prompt(self, brief: Brief, *, variation_strength: float = 0.0) -> str:
        parts = [f"Create a concept design artwork: {brief.intent}"]

        if variation_strength > 0:
            if variation_strength >= 0.6:
                parts.append(
                    "Create a SIGNIFICANT rework of the reference image. "
                    "Keep the core subject but substantially change composition, style, or mood."
                )
            elif variation_strength >= 0.35:
                parts.append(
                    "Create a variation of the reference image. "
                    "Preserve the overall composition but apply the requested changes."
                )
            else:
                parts.append(
                    "Create a subtle refinement of the reference image. "
                    "Keep composition and style very close, apply only minor adjustments."
                )
        elif brief.user_sketch:
            parts.append(
                "This should be a refined variation of the provided reference sketch, "
                "preserving its composition while improving detail and style."
            )

        if brief.style_mix:
            styles = ", ".join(s.tradition.replace("_", " ") or s.tag for s in brief.style_mix)
            parts.append(f"Style: {styles}")
        if brief.mood:
            parts.append(f"Mood/atmosphere: {brief.mood}")
        if brief.composition.layout:
            parts.append(f"Composition: {brief.composition.layout}")
        if brief.composition.focal_point:
            parts.append(f"Focal point: {brief.composition.focal_point}")
        if brief.palette.mood:
            parts.append(f"Color mood: {brief.palette.mood}")
        if brief.palette.primary:
            parts.append(f"Primary colors: {', '.join(brief.palette.primary)}")
        if brief.elements:
            parts.append(f"Key elements: {', '.join(e.name for e in brief.elements[:6])}")
        if brief.must_have:
            parts.append(f"Must include: {', '.join(brief.must_have)}")
        if brief.must_avoid:
            parts.append(f"Must avoid: {', '.join(brief.must_avoid)}")
        parts.append("Output: 1024x1024 image, no text or watermarks.")
        return "\n".join(parts)

    async def generate_concepts(
        self, brief: Brief, *, count: int = 4, provider: str = "mock",
        project_dir: str = "", api_key: str = "",
        reference_image: str = "",
        variation_strength: float = 0.0,
    ) -> list[str]:
        project = Path(project_dir) if project_dir else Path(".")
        concepts_dir = project / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)

        prompt = self.build_concept_prompt(brief, variation_strength=variation_strength)
        paths: list[str] = []

        # Determine reference image: explicit param > brief.user_sketch
        ref_b64 = ""
        if reference_image:
            ref_b64 = self._load_sketch_b64(reference_image)
        elif brief.user_sketch:
            ref_b64 = self._load_sketch_b64(brief.user_sketch)

        try:
            from vulca.providers import get_image_provider
            img_provider = get_image_provider(provider, api_key=api_key)
        except Exception:
            for i in range(count):
                p = concepts_dir / f"c{i + 1}.png"
                p.write_bytes(b"placeholder")
                paths.append(str(p))
            brief.concept_candidates = paths
            return paths

        for i in range(count):
            try:
                varied = f"{prompt}\n\nVariation {i + 1} of {count}."
                result = await img_provider.generate(
                    varied, tradition=brief.style_mix[0].tradition if brief.style_mix else "",
                    subject=brief.intent,
                    reference_image_b64=ref_b64,
                )
                ext = "png" if "png" in result.mime else "jpg"
                filepath = concepts_dir / f"c{i + 1}.{ext}"
                filepath.write_bytes(base64.b64decode(result.image_b64))
                paths.append(str(filepath))
            except Exception as exc:
                logger.debug("Concept %d failed: %s", i + 1, exc)
                filepath = concepts_dir / f"c{i + 1}.png"
                filepath.write_bytes(b"placeholder")
                paths.append(str(filepath))

        brief.concept_candidates = paths
        return paths

    def select(self, brief: Brief, index: int, notes: str = "") -> None:
        if 0 <= index < len(brief.concept_candidates):
            brief.selected_concept = brief.concept_candidates[index]
        elif brief.concept_candidates:
            brief.selected_concept = brief.concept_candidates[0]
        if notes:
            brief.concept_notes = notes

    @staticmethod
    def _load_sketch_b64(path: str) -> str:
        try:
            return base64.b64encode(Path(path).read_bytes()).decode()
        except Exception:
            return ""
