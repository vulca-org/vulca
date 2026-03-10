"""IMAGE sub-stage handlers — real LLM-powered implementations with stub fallbacks.

Each handler follows the StageHandler protocol:
    async (stage_def: SubStageDef, context: dict) -> SubStageArtifact

Handlers call ``litellm.acompletion`` via MODEL_FAST for text/JSON generation.
If the LLM call fails (timeout, missing API key, rate limit, etc.), each handler
falls back to a deterministic stub so the pipeline never crashes.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import litellm

from app.prototype.agents.model_router import MODEL_FAST, MODEL_VLM
from app.prototype.media.types import SubStageArtifact, SubStageDef

logger = logging.getLogger(__name__)

# Default timeout for LLM calls in sub-stage handlers (seconds)
_DEFAULT_TIMEOUT = 10


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict | None:
    """Best-effort JSON extraction from LLM response text.

    Handles common cases: bare JSON, markdown-fenced JSON, and partial JSON.
    Returns *None* if extraction fails entirely.
    """
    # Strip markdown fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove first line (```json or ```) and last line (```)
        lines = cleaned.split("\n")
        # Find start
        start = 1 if lines[0].startswith("```") else 0
        # Find end
        end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        cleaned = "\n".join(lines[start:end]).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to find a JSON object in the text
    brace_start = cleaned.find("{")
    brace_end = cleaned.rfind("}")
    if brace_start != -1 and brace_end > brace_start:
        try:
            return json.loads(cleaned[brace_start : brace_end + 1])
        except json.JSONDecodeError:
            pass

    return None


def _gather_previous_outputs(context: dict[str, Any]) -> str:
    """Summarize previous sub-stage artifacts for downstream prompts."""
    input_artifacts = context.get("input_artifacts", {})
    if not input_artifacts:
        return ""
    parts: list[str] = []
    for name, artifact in input_artifacts.items():
        data = artifact.data if artifact else None
        if data is not None:
            # Truncate long data for prompt inclusion
            data_str = str(data)[:800]
            parts.append(f"[{name}]: {data_str}")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# mood_palette — JSON output
# ---------------------------------------------------------------------------

async def handle_mood_palette(stage_def: SubStageDef, context: dict[str, Any]) -> SubStageArtifact:
    """Generate a mood palette (color palette + mood keywords + atmosphere) as JSON.

    Uses MODEL_FAST to generate a culturally-informed color palette.
    Falls back to a deterministic stub if the LLM call fails.
    """
    tradition = context.get("cultural_tradition", context.get("tradition", "default"))
    subject = context.get("subject", "abstract art")

    try:
        tradition_clause = f" in the '{tradition}' cultural/artistic tradition" if tradition and tradition != "default" else ""
        response = await litellm.acompletion(
            model=MODEL_FAST,
            messages=[{
                "role": "user",
                "content": (
                    f"Generate a mood palette for an artwork about '{subject}'{tradition_clause}.\n"
                    "Return a JSON object with exactly these keys:\n"
                    "- \"colors\": list of 5 hex color strings (e.g. [\"#2C3E50\", ...])\n"
                    "- \"mood_keywords\": list of 3-5 mood descriptor strings\n"
                    "- \"atmosphere\": a single sentence describing the overall atmosphere\n"
                    "- \"warmth\": a float between 0.0 (cool) and 1.0 (warm)\n"
                    "Return ONLY valid JSON, no explanation."
                ),
            }],
            timeout=_DEFAULT_TIMEOUT,
        )

        content = response.choices[0].message.content
        palette_data = _extract_json(content)

        if palette_data is None:
            # LLM returned non-JSON; wrap raw response
            palette_data = {
                "raw_response": content,
                "colors": [],
                "mood_keywords": [],
                "atmosphere": content[:200] if content else "",
                "warmth": 0.5,
            }

        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="json",
            data=json.dumps(palette_data),
            metadata={"source": "llm", "model": MODEL_FAST, "tradition": tradition},
        )

    except Exception as exc:
        logger.warning("mood_palette LLM call failed, using stub: %s", exc)
        # Stub fallback
        palette_data = {
            "tradition": tradition,
            "subject": subject,
            "colors": ["#2C3E50", "#E74C3C", "#ECF0F1", "#3498DB", "#F39C12"],
            "mood": "contemplative",
            "mood_keywords": ["contemplative", "serene"],
            "atmosphere": f"A contemplative atmosphere evoking {subject}",
            "warmth": 0.6,
        }
        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="json",
            data=json.dumps(palette_data),
            metadata={"source": "stub", "tradition": tradition, "error": str(exc)},
        )


# ---------------------------------------------------------------------------
# composition_sketch — text description
# ---------------------------------------------------------------------------

async def handle_composition_sketch(stage_def: SubStageDef, context: dict[str, Any]) -> SubStageArtifact:
    """Generate a composition layout description based on subject and mood palette.

    Uses MODEL_FAST to produce a textual composition plan.
    Falls back to a stub if the LLM call fails.
    """
    subject = context.get("subject", "abstract art")
    previous = _gather_previous_outputs(context)

    try:
        mood_info = ""
        if previous:
            mood_info = f"\n\nPrevious stage outputs:\n{previous}\n"

        response = await litellm.acompletion(
            model=MODEL_FAST,
            messages=[{
                "role": "user",
                "content": (
                    f"You are an art director planning a composition for an artwork about '{subject}'.{mood_info}\n"
                    "Describe the composition layout in detail:\n"
                    "1. Overall structure (rule of thirds, golden ratio, symmetry, etc.)\n"
                    "2. Foreground, middle ground, background arrangement\n"
                    "3. Focal point placement\n"
                    "4. Visual flow and eye movement\n"
                    "5. Negative space usage\n"
                    "Keep the response concise (150-300 words)."
                ),
            }],
            timeout=_DEFAULT_TIMEOUT,
        )

        content = response.choices[0].message.content

        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="text",
            data=content,
            metadata={"source": "llm", "model": MODEL_FAST},
        )

    except Exception as exc:
        logger.warning("composition_sketch LLM call failed, using stub: %s", exc)
        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="text",
            data=(
                f"Composition plan for '{subject}': "
                "Rule-of-thirds layout with the main subject placed at the left-third intersection. "
                "Foreground contains textural elements, middle ground holds the focal subject, "
                "background provides atmospheric depth. Visual flow moves from bottom-left to upper-right."
            ),
            metadata={"source": "stub", "error": str(exc)},
        )


# ---------------------------------------------------------------------------
# element_studies — text description of key elements
# ---------------------------------------------------------------------------

async def handle_element_studies(stage_def: SubStageDef, context: dict[str, Any]) -> SubStageArtifact:
    """Analyze key elements in the composition, providing detail studies.

    Uses MODEL_FAST. Depends on composition_sketch artifact.
    Falls back to a stub if the LLM call fails.
    """
    subject = context.get("subject", "abstract art")
    previous = _gather_previous_outputs(context)

    try:
        prompt_parts = [
            f"You are an art director doing element studies for an artwork about '{subject}'.\n",
        ]
        if previous:
            prompt_parts.append(f"\nPrevious stage outputs:\n{previous}\n")
        prompt_parts.append(
            "Identify and describe 3-5 key visual elements in detail:\n"
            "For each element, specify:\n"
            "- Element name and role in the composition\n"
            "- Shape, form, and proportion details\n"
            "- Suggested texture and material treatment\n"
            "- Color relationships with the palette\n"
            "- Symbolic or cultural significance (if any)\n"
            "Keep each element study to 50-80 words."
        )

        response = await litellm.acompletion(
            model=MODEL_FAST,
            messages=[{
                "role": "user",
                "content": "".join(prompt_parts),
            }],
            timeout=_DEFAULT_TIMEOUT,
        )

        content = response.choices[0].message.content

        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="text",
            data=content,
            metadata={"source": "llm", "model": MODEL_FAST},
        )

    except Exception as exc:
        logger.warning("element_studies LLM call failed, using stub: %s", exc)
        input_artifacts = context.get("input_artifacts", {})
        comp_artifact = input_artifacts.get("composition_sketch")
        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="text",
            data=(
                f"Element studies for '{subject}':\n"
                "1. Primary subject — central focal element with detailed form study\n"
                "2. Supporting elements — secondary shapes providing visual balance\n"
                "3. Atmospheric elements — textures and gradients for depth"
            ),
            metadata={
                "source": "stub",
                "based_on": comp_artifact.stage_name if comp_artifact else None,
                "error": str(exc),
            },
        )


# ---------------------------------------------------------------------------
# style_reference — text guidance
# ---------------------------------------------------------------------------

async def handle_style_reference(stage_def: SubStageDef, context: dict[str, Any]) -> SubStageArtifact:
    """Provide style reference guidance based on cultural tradition and mood palette.

    Uses MODEL_FAST. Depends on mood_palette artifact.
    Falls back to a stub if the LLM call fails.
    """
    tradition = context.get("cultural_tradition", context.get("tradition", "default"))
    subject = context.get("subject", "abstract art")
    previous = _gather_previous_outputs(context)

    try:
        tradition_clause = f" rooted in the '{tradition}' tradition" if tradition and tradition != "default" else ""
        prompt_parts = [
            f"You are an art historian and style consultant. Provide style reference guidance "
            f"for an artwork about '{subject}'{tradition_clause}.\n",
        ]
        if previous:
            prompt_parts.append(f"\nPrevious stage outputs:\n{previous}\n")
        prompt_parts.append(
            "Include:\n"
            "1. Historical references — specific artworks, movements, or masters that inform this style\n"
            "2. Technique recommendations — brushwork, medium, application methods\n"
            "3. Color treatment — how the palette should be applied (layering, transparency, saturation)\n"
            "4. Texture and surface quality — matte vs glossy, smooth vs impasto, etc.\n"
            "5. Cultural markers — specific visual motifs or conventions to incorporate\n"
            "Keep the response to 150-250 words."
        )

        response = await litellm.acompletion(
            model=MODEL_FAST,
            messages=[{
                "role": "user",
                "content": "".join(prompt_parts),
            }],
            timeout=_DEFAULT_TIMEOUT,
        )

        content = response.choices[0].message.content

        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="text",
            data=content,
            metadata={"source": "llm", "model": MODEL_FAST, "tradition": tradition},
        )

    except Exception as exc:
        logger.warning("style_reference LLM call failed, using stub: %s", exc)
        input_artifacts = context.get("input_artifacts", {})
        palette_artifact = input_artifacts.get("mood_palette")
        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="text",
            data=(
                f"Style reference for '{subject}' in {tradition} tradition:\n"
                "Drawing from traditional techniques with contemporary interpretation. "
                "Use fluid brushwork with emphasis on atmospheric perspective. "
                "Color application should favor layered transparency over opaque fills. "
                "Incorporate cultural motifs as structural rather than decorative elements."
            ),
            metadata={
                "source": "stub",
                "tradition": tradition,
                "palette_used": palette_artifact is not None,
                "error": str(exc),
            },
        )


# ---------------------------------------------------------------------------
# storyboard — comprehensive creation plan
# ---------------------------------------------------------------------------

async def handle_storyboard(stage_def: SubStageDef, context: dict[str, Any]) -> SubStageArtifact:
    """Synthesize all previous sub-stage outputs into a comprehensive creation plan.

    Uses MODEL_FAST. Depends on composition_sketch, element_studies, style_reference.
    Falls back to a stub if the LLM call fails.
    """
    subject = context.get("subject", "abstract art")
    tradition = context.get("cultural_tradition", context.get("tradition", "default"))
    previous = _gather_previous_outputs(context)

    try:
        tradition_clause = (
            f" in the '{tradition}' tradition"
            if tradition and tradition != "default" else ""
        )
        prompt_parts = [
            f"You are a senior art director creating a final storyboard / creation plan "
            f"for an artwork about '{subject}'{tradition_clause}.\n",
        ]
        if previous:
            prompt_parts.append(f"\nAll previous sub-stage outputs:\n{previous}\n")
        prompt_parts.append(
            "\nSynthesize everything into a detailed creation plan that covers:\n"
            "1. VISION STATEMENT — One paragraph capturing the artistic intent\n"
            "2. COMPOSITION — Final layout decisions (from composition sketch)\n"
            "3. KEY ELEMENTS — Treatment of each major element (from element studies)\n"
            "4. STYLE EXECUTION — Technical approach (from style reference)\n"
            "5. COLOR STRATEGY — How the mood palette maps to regions of the artwork\n"
            "6. FINAL NOTES — Any special considerations or creative decisions\n"
            "This plan will guide the final rendering. Be specific and actionable (200-400 words)."
        )

        response = await litellm.acompletion(
            model=MODEL_FAST,
            messages=[{
                "role": "user",
                "content": "".join(prompt_parts),
            }],
            timeout=_DEFAULT_TIMEOUT,
        )

        content = response.choices[0].message.content

        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="text",
            data=content,
            metadata={"source": "llm", "model": MODEL_FAST},
        )

    except Exception as exc:
        logger.warning("storyboard LLM call failed, using stub: %s", exc)
        input_artifacts = context.get("input_artifacts", {})
        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="text",
            data=(
                f"Creation plan for '{subject}':\n"
                "VISION: A contemplative artwork balancing tradition with contemporary expression.\n"
                "COMPOSITION: Rule-of-thirds layout with atmospheric depth.\n"
                "ELEMENTS: Primary subject with supporting environmental elements.\n"
                "STYLE: Layered technique with attention to cultural markers.\n"
                "COLOR: Palette applied with graduated intensity from focal point outward.\n"
                "NOTES: Maintain balance between detail and negative space."
            ),
            metadata={
                "source": "stub",
                "inputs_available": list(input_artifacts.keys()),
                "error": str(exc),
            },
        )


# ---------------------------------------------------------------------------
# final_render — enhanced prompt synthesis (NOT image generation)
# ---------------------------------------------------------------------------

async def handle_final_render(stage_def: SubStageDef, context: dict[str, Any]) -> SubStageArtifact:
    """Synthesize all sub-stage artifacts into an enhanced generation prompt.

    This handler does NOT generate an image directly. It produces a comprehensive,
    enriched prompt text that the Draft agent's provider will use for actual image
    generation. The output combines all upstream sub-stage insights into a single
    optimized prompt.

    Uses MODEL_FAST for prompt synthesis. Falls back to concatenating prior outputs.
    """
    subject = context.get("subject", "abstract art")
    tradition = context.get("cultural_tradition", context.get("tradition", "default"))
    previous = _gather_previous_outputs(context)

    try:
        prompt_parts = [
            "You are an expert prompt engineer for AI image generation.\n"
            f"Subject: '{subject}'\n",
        ]
        if tradition and tradition != "default":
            prompt_parts.append(f"Cultural tradition: '{tradition}'\n")
        if previous:
            prompt_parts.append(f"\nAll sub-stage research and planning:\n{previous}\n")
        prompt_parts.append(
            "\nSynthesize ALL the above research into a single, highly detailed image generation prompt.\n"
            "The prompt should:\n"
            "- Be 100-200 words, densely packed with visual description\n"
            "- Include specific colors (hex codes from the palette)\n"
            "- Describe composition, lighting, texture, and atmosphere\n"
            "- Reference artistic style and technique\n"
            "- Include cultural elements naturally\n"
            "Return ONLY the generation prompt text, nothing else."
        )

        response = await litellm.acompletion(
            model=MODEL_FAST,
            messages=[{
                "role": "user",
                "content": "".join(prompt_parts),
            }],
            timeout=_DEFAULT_TIMEOUT,
        )

        content = response.choices[0].message.content

        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="text",
            data=content,
            metadata={
                "source": "llm",
                "model": MODEL_FAST,
                "tradition": tradition,
                "usage": "enhanced_prompt_for_draft_provider",
            },
        )

    except Exception as exc:
        logger.warning("final_render LLM call failed, using stub: %s", exc)
        # Fallback: concatenate available upstream artifacts into a basic prompt
        input_artifacts = context.get("input_artifacts", {})
        storyboard_data = ""
        if "storyboard" in input_artifacts and input_artifacts["storyboard"]:
            storyboard_data = str(input_artifacts["storyboard"].data)[:500]

        fallback_prompt = (
            f"A high-quality artwork depicting {subject}"
            + (f" in the {tradition} tradition" if tradition and tradition != "default" else "")
            + ". "
            + (storyboard_data if storyboard_data else
               "Contemplative atmosphere, balanced composition, rich color palette, "
               "detailed textures, and cultural depth.")
        )

        return SubStageArtifact(
            stage_name=stage_def.name,
            artifact_type="text",
            data=fallback_prompt,
            metadata={
                "source": "stub",
                "tradition": tradition,
                "error": str(exc),
                "usage": "enhanced_prompt_for_draft_provider",
            },
        )


# ---------------------------------------------------------------------------
# Handler registry for IMAGE sub-stages
# ---------------------------------------------------------------------------

IMAGE_HANDLERS: dict[str, Any] = {
    "mood_palette": handle_mood_palette,
    "composition_sketch": handle_composition_sketch,
    "element_studies": handle_element_studies,
    "style_reference": handle_style_reference,
    "storyboard": handle_storyboard,
    "final_render": handle_final_render,
}


def get_image_handlers() -> dict[str, Any]:
    """Return a copy of the IMAGE sub-stage handler registry."""
    return dict(IMAGE_HANDLERS)
