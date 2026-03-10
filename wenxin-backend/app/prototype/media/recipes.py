"""Creation recipes for each media type — IMAGE, VIDEO, 3D, SOUND.

Each recipe defines an ordered sequence of sub-stages that the SubStageExecutor
runs to produce a final artifact.  Only IMAGE is currently enabled; the others
are registered as "Coming Soon" placeholders.
"""

from __future__ import annotations

from app.prototype.media.types import CreationRecipe, MediaType, SubStageDef

# ---------------------------------------------------------------------------
# Availability map — which media types are production-ready
# ---------------------------------------------------------------------------

AVAILABLE_MEDIA_TYPES: dict[MediaType, bool] = {
    MediaType.IMAGE: True,
    MediaType.VIDEO: False,      # Coming Soon
    MediaType.MODEL_3D: False,   # Coming Soon
    MediaType.SOUND: False,      # Coming Soon
}

# ---------------------------------------------------------------------------
# IMAGE recipes
# ---------------------------------------------------------------------------

IMAGE_STANDARD_RECIPE = CreationRecipe(
    media_type=MediaType.IMAGE,
    name="image_standard",
    display_name="Standard Image Recipe",
    sub_stages=(
        SubStageDef(
            name="mood_palette",
            display_name="Mood Palette",
            description="Generate color palette and mood board",
            order=0,
            output_artifact_type="json",
            estimated_latency_ms=2000,
        ),
        SubStageDef(
            name="composition_sketch",
            display_name="Composition Sketch",
            description="Rough composition layout description",
            order=1,
            output_artifact_type="text",
            estimated_latency_ms=3000,
        ),
        SubStageDef(
            name="element_studies",
            display_name="Element Studies",
            description="Detail studies for key elements",
            order=2,
            input_artifact_names=("composition_sketch",),
            output_artifact_type="text",
            estimated_latency_ms=4000,
        ),
        SubStageDef(
            name="style_reference",
            display_name="Style Reference",
            description="Cultural style reference guidance",
            order=3,
            input_artifact_names=("mood_palette",),
            output_artifact_type="text",
            estimated_latency_ms=3000,
        ),
        SubStageDef(
            name="storyboard",
            display_name="Storyboard",
            description="Comprehensive creation plan synthesizing all stages",
            order=4,
            input_artifact_names=("composition_sketch", "element_studies", "style_reference"),
            output_artifact_type="text",
            estimated_latency_ms=5000,
        ),
        SubStageDef(
            name="final_render",
            display_name="Final Render",
            description="Enhanced generation prompt synthesizing all sub-stages",
            order=5,
            input_artifact_names=("storyboard",),
            output_artifact_type="text",
            estimated_latency_ms=8000,
        ),
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# VIDEO recipe (placeholder)
# ---------------------------------------------------------------------------

VIDEO_RECIPE = CreationRecipe(
    media_type=MediaType.VIDEO,
    name="video_standard",
    display_name="Standard Video Recipe",
    sub_stages=(
        SubStageDef(
            name="storyboard",
            display_name="Storyboard",
            description="Generate storyboard frames from narrative",
            order=0,
            output_artifact_type="json",
            estimated_latency_ms=3000,
        ),
        SubStageDef(
            name="keyframe_generation",
            display_name="Keyframe Generation",
            description="Generate key visual frames",
            order=1,
            input_artifact_names=("storyboard",),
            output_artifact_type="image",
            estimated_latency_ms=10000,
        ),
        SubStageDef(
            name="interpolation",
            display_name="Frame Interpolation",
            description="Interpolate between keyframes for smooth motion",
            order=2,
            input_artifact_names=("keyframe_generation",),
            output_artifact_type="image",
            estimated_latency_ms=15000,
        ),
        SubStageDef(
            name="final_compose",
            display_name="Final Composition",
            description="Compose final video with audio sync",
            order=3,
            input_artifact_names=("interpolation",),
            output_artifact_type="image",
            estimated_latency_ms=20000,
        ),
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# 3D Model recipe (placeholder)
# ---------------------------------------------------------------------------

MODEL_3D_RECIPE = CreationRecipe(
    media_type=MediaType.MODEL_3D,
    name="3d_model_standard",
    display_name="Standard 3D Model Recipe",
    sub_stages=(
        SubStageDef(
            name="concept_sketch",
            display_name="Concept Sketch",
            description="Generate multi-view concept sketches",
            order=0,
            output_artifact_type="image",
            estimated_latency_ms=4000,
        ),
        SubStageDef(
            name="base_mesh",
            display_name="Base Mesh",
            description="Generate base 3D mesh from concepts",
            order=1,
            input_artifact_names=("concept_sketch",),
            output_artifact_type="mesh",
            estimated_latency_ms=15000,
        ),
        SubStageDef(
            name="texture_mapping",
            display_name="Texture Mapping",
            description="Apply textures and materials to mesh",
            order=2,
            input_artifact_names=("base_mesh",),
            output_artifact_type="mesh",
            estimated_latency_ms=10000,
        ),
        SubStageDef(
            name="final_render_3d",
            display_name="Final 3D Render",
            description="Render final 3D model with lighting",
            order=3,
            input_artifact_names=("texture_mapping",),
            output_artifact_type="mesh",
            estimated_latency_ms=12000,
        ),
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Sound recipe (placeholder)
# ---------------------------------------------------------------------------

SOUND_RECIPE = CreationRecipe(
    media_type=MediaType.SOUND,
    name="sound_standard",
    display_name="Standard Sound Recipe",
    sub_stages=(
        SubStageDef(
            name="mood_analysis",
            display_name="Mood Analysis",
            description="Analyze visual/textual input for musical mood",
            order=0,
            output_artifact_type="json",
            estimated_latency_ms=2000,
        ),
        SubStageDef(
            name="melody_generation",
            display_name="Melody Generation",
            description="Generate core melody based on mood",
            order=1,
            input_artifact_names=("mood_analysis",),
            output_artifact_type="audio",
            estimated_latency_ms=8000,
        ),
        SubStageDef(
            name="arrangement",
            display_name="Arrangement",
            description="Add instruments and harmonies",
            order=2,
            input_artifact_names=("melody_generation",),
            output_artifact_type="audio",
            estimated_latency_ms=10000,
        ),
        SubStageDef(
            name="final_mix",
            display_name="Final Mix",
            description="Mix and master final audio",
            order=3,
            input_artifact_names=("arrangement",),
            output_artifact_type="audio",
            estimated_latency_ms=5000,
        ),
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Recipe Registry
# ---------------------------------------------------------------------------

RECIPE_REGISTRY: dict[str, CreationRecipe] = {
    "image_standard": IMAGE_STANDARD_RECIPE,
    "video_standard": VIDEO_RECIPE,
    "3d_model_standard": MODEL_3D_RECIPE,
    "sound_standard": SOUND_RECIPE,
}

# Default recipe per media type
_DEFAULT_RECIPES: dict[MediaType, str] = {
    MediaType.IMAGE: "image_standard",
    MediaType.VIDEO: "video_standard",
    MediaType.MODEL_3D: "3d_model_standard",
    MediaType.SOUND: "sound_standard",
}


def get_recipe(name: str) -> CreationRecipe | None:
    """Look up a recipe by name. Returns None if not found."""
    return RECIPE_REGISTRY.get(name)


def get_default_recipe(media_type: MediaType) -> CreationRecipe:
    """Return the default recipe for a given media type.

    Raises ValueError if no default recipe exists.
    """
    recipe_name = _DEFAULT_RECIPES.get(media_type)
    if recipe_name is None:
        raise ValueError(f"No default recipe for media type: {media_type}")
    recipe = RECIPE_REGISTRY.get(recipe_name)
    if recipe is None:
        raise ValueError(f"Default recipe '{recipe_name}' not found in registry")
    return recipe
