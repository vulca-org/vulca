"""ScoutPhase -- generate reference images for creative inspiration."""
from __future__ import annotations

import base64
import logging
from pathlib import Path

from vulca.studio.brief import Brief
from vulca.studio.types import Reference

logger = logging.getLogger("vulca.studio")


class ScoutPhase:
    def extract_search_terms(self, brief: Brief) -> list[str]:
        terms = []
        if brief.intent:
            terms.append(brief.intent)
        for sw in brief.style_mix:
            if sw.tradition:
                terms.append(sw.tradition.replace("_", " "))
            if sw.tag:
                terms.append(sw.tag)
        if brief.mood:
            terms.append(f"{brief.mood} art style")
        return terms

    def build_reference_prompts(self, brief: Brief) -> list[str]:
        prompts = []
        base_desc = brief.intent or "artwork"
        mood = brief.mood or "artistic"

        prompts.append(
            f"Create a mood board / style reference for: {base_desc}. "
            f"Mood: {mood}. Show color palette, textures, and composition examples. "
            f"No text or labels."
        )

        if brief.palette.mood or brief.palette.primary:
            palette_desc = brief.palette.mood or f"colors: {', '.join(brief.palette.primary)}"
            prompts.append(
                f"Color palette study for {base_desc}. {palette_desc}. "
                f"Abstract color swatches and gradients. No text."
            )

        return prompts

    async def generate_references(
        self, brief: Brief, *, provider: str = "mock",
        project_dir: str = "", api_key: str = "",
    ) -> list[Reference]:
        refs: list[Reference] = []
        prompts = self.build_reference_prompts(brief)
        if not prompts:
            return refs

        project = Path(project_dir) if project_dir else Path(".")
        refs_dir = project / "refs"
        refs_dir.mkdir(parents=True, exist_ok=True)

        try:
            from vulca.providers import get_image_provider
            # TODO(v0.21): plumb model/quality from studio orchestrator —
            # currently defaults to OpenAIImageProvider's gpt-image-1 silently.
            # See v0.20 PR audit on layers_redraw model-plumbing fix.
            img_provider = get_image_provider(provider, api_key=api_key)
        except Exception:
            logger.debug("Could not load provider %s for scout", provider)
            return refs

        for i, prompt in enumerate(prompts):
            try:
                result = await img_provider.generate(
                    prompt, tradition=brief.style_mix[0].tradition if brief.style_mix else "",
                    subject=brief.intent,
                )
                ext = "png" if "png" in result.mime else "jpg"
                filename = f"ref-gen-{i:02d}.{ext}"
                filepath = refs_dir / filename
                filepath.write_bytes(base64.b64decode(result.image_b64))
                refs.append(Reference(
                    path=str(filepath), source="generate", prompt=prompt,
                    note=f"AI-generated reference {i + 1}",
                ))
            except Exception as exc:
                logger.debug("Scout reference generation failed: %s", exc)
        return refs
