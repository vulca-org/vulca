"""Tests for V2 analysis prompt engine (layers/prompt.py)."""
from __future__ import annotations

import pytest
from vulca.layers.prompt import (
    ANALYZE_PROMPT,
    build_analyze_prompt,
    parse_v2_response,
    build_regeneration_prompt,
)
from vulca.layers.types import LayerInfo


class TestAnalyzePrompt:
    """Tests for the ANALYZE_PROMPT constant and build_analyze_prompt()."""

    def test_prompt_contains_no_overlap_rule(self):
        """Prompt must warn that layers MUST NOT overlap in content."""
        assert "MUST NOT overlap" in ANALYZE_PROMPT

    def test_bbox_only_in_do_not_context(self):
        """The word 'bbox' must appear only in a 'DO NOT include bbox' instruction."""
        assert "bbox" in ANALYZE_PROMPT
        # Every occurrence of "bbox" should be in a "DO NOT" context
        lower = ANALYZE_PROMPT.lower()
        idx = lower.find("bbox")
        while idx != -1:
            # Look backwards up to 30 chars for "do not"
            context = lower[max(0, idx - 30): idx + len("bbox")]
            assert "do not" in context, (
                f"Found 'bbox' outside 'DO NOT' context at index {idx}: "
                f"...{ANALYZE_PROMPT[max(0, idx-30):idx+20]}..."
            )
            idx = lower.find("bbox", idx + 1)

    def test_prompt_requires_regeneration_prompt_field(self):
        """Prompt must require the 'regeneration_prompt' field in JSON schema."""
        assert "regeneration_prompt" in ANALYZE_PROMPT

    def test_prompt_requires_content_type_field(self):
        """Prompt must require the 'content_type' field in JSON schema."""
        assert "content_type" in ANALYZE_PROMPT

    def test_prompt_requires_dominant_colors_field(self):
        """Prompt must require the 'dominant_colors' field in JSON schema."""
        assert "dominant_colors" in ANALYZE_PROMPT

    def test_build_analyze_prompt_returns_same_as_constant(self):
        """build_analyze_prompt() must return the ANALYZE_PROMPT constant."""
        assert build_analyze_prompt() == ANALYZE_PROMPT


class TestParseV2Response:
    """Tests for parse_v2_response()."""

    def test_parse_valid_two_layer_response(self):
        """Parse a valid 2-layer response and check all fields."""
        raw = {
            "layers": [
                {
                    "name": "sky_background",
                    "description": "Gradient blue sky with soft clouds",
                    "z_index": 0,
                    "blend_mode": "normal",
                    "dominant_colors": ["#87CEEB", "#FFFFFF"],
                    "content_type": "background",
                    "regeneration_prompt": "A gradient blue sky on transparent background",
                },
                {
                    "name": "mountain_subject",
                    "description": "Snow-capped mountain peaks",
                    "z_index": 1,
                    "blend_mode": "multiply",
                    "dominant_colors": ["#FFFFFF", "#808080"],
                    "content_type": "subject",
                    "regeneration_prompt": "Snow-capped mountains on transparent background",
                },
            ]
        }
        layers = parse_v2_response(raw)
        assert len(layers) == 2

        bg = layers[0]
        assert bg.name == "sky_background"
        assert bg.z_index == 0
        assert bg.blend_mode == "normal"
        assert bg.content_type == "background"
        assert bg.dominant_colors == ["#87CEEB", "#FFFFFF"]
        assert bg.regeneration_prompt == "A gradient blue sky on transparent background"

        subj = layers[1]
        assert subj.name == "mountain_subject"
        assert subj.blend_mode == "multiply"
        assert subj.content_type == "subject"
        assert subj.dominant_colors == ["#FFFFFF", "#808080"]

    def test_parse_missing_optional_fields_uses_defaults(self):
        """Missing optional fields must fall back to defaults."""
        raw = {
            "layers": [
                {
                    "name": "minimal",
                    "description": "minimal layer",
                    "z_index": 0,
                    # blend_mode, content_type, dominant_colors, regeneration_prompt all missing
                },
            ]
        }
        layers = parse_v2_response(raw)
        assert len(layers) == 1
        layer = layers[0]
        assert layer.blend_mode == "normal"
        assert layer.content_type == "background"
        assert layer.dominant_colors == []
        assert layer.regeneration_prompt == ""

    def test_parse_three_layers_sorted_by_z_index(self):
        """Layers with out-of-order z_index values must be returned sorted ascending."""
        raw = {
            "layers": [
                {"name": "top", "description": "top layer", "z_index": 2, "blend_mode": "screen"},
                {"name": "mid", "description": "middle layer", "z_index": 1},
                {"name": "bottom", "description": "base layer", "z_index": 0},
            ]
        }
        layers = parse_v2_response(raw)
        assert len(layers) == 3
        assert layers[0].name == "bottom"
        assert layers[0].z_index == 0
        assert layers[1].name == "mid"
        assert layers[1].z_index == 1
        assert layers[2].name == "top"
        assert layers[2].z_index == 2


class TestRegenerationPrompt:
    """Tests for build_regeneration_prompt()."""

    def _make_layer(
        self,
        name: str = "test_layer",
        description: str = "A test layer",
        z_index: int = 0,
        regeneration_prompt: str = "",
    ) -> LayerInfo:
        return LayerInfo(
            name=name,
            description=description,
            z_index=z_index,
            regeneration_prompt=regeneration_prompt,
        )

    def test_includes_description_transparent_and_canvas_size(self):
        """Prompt must include layer content, 'transparent', and canvas dimensions."""
        layer = self._make_layer(
            description="Ink wash mountains",
            regeneration_prompt="Ink wash mountains on transparent background",
        )
        prompt = build_regeneration_prompt(layer, width=512, height=768)
        assert "Ink wash mountains" in prompt
        assert "white background" in prompt.lower() or "canvas" in prompt.lower()
        assert "512" in prompt
        assert "768" in prompt

    def test_includes_tradition_when_non_default(self):
        """Prompt must include the tradition name when provided."""
        layer = self._make_layer(
            description="Red dragon",
            regeneration_prompt="A red dragon on transparent background",
        )
        prompt = build_regeneration_prompt(
            layer, width=1024, height=1024, tradition="chinese_xieyi"
        )
        assert "chinese_xieyi" in prompt

    def test_tradition_absent_when_empty(self):
        """When tradition is empty string (default), it must not appear in prompt."""
        layer = self._make_layer(
            description="Simple background",
            regeneration_prompt="Simple gradient background",
        )
        prompt = build_regeneration_prompt(layer, width=1024, height=1024, tradition="")
        # "tradition" keyword should not appear
        assert "tradition" not in prompt.lower()

    def test_includes_do_not_exclusion_when_other_layers_provided(self):
        """Prompt must include 'DO NOT' exclusion clause when other_layer_names is given."""
        layer = self._make_layer(
            description="Bamboo stalks",
            regeneration_prompt="Bamboo stalks on transparent background",
        )
        prompt = build_regeneration_prompt(
            layer,
            width=1024,
            height=1024,
            other_layer_names=["sky_background", "mist_effect"],
        )
        assert "DO NOT" in prompt
        assert "sky_background" in prompt
        assert "mist_effect" in prompt

    def test_fallback_to_description_when_no_regeneration_prompt(self):
        """When regeneration_prompt is empty, description is used as the base."""
        layer = self._make_layer(
            description="Misty forest",
            regeneration_prompt="",
        )
        prompt = build_regeneration_prompt(layer, width=1024, height=1024)
        assert "Misty forest" in prompt
        assert "white background" in prompt.lower() or "canvas" in prompt.lower()


class TestAnalyzeV2Integration:
    def test_parse_layer_response_delegates_to_v2(self):
        from vulca.layers.analyze import parse_layer_response
        raw = {
            "layers": [{
                "name": "bg", "description": "sky", "z_index": 0,
                "content_type": "background",
                "dominant_colors": ["#87CEEB"],
                "regeneration_prompt": "Blue sky",
            }]
        }
        layers = parse_layer_response(raw)
        assert layers[0].content_type == "background"
        assert layers[0].dominant_colors == ["#87CEEB"]
        assert layers[0].regeneration_prompt == "Blue sky"
        assert layers[0].bbox is None
