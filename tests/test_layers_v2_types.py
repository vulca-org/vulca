"""Tests for V2 LayerInfo / LayerResult / LayeredArtwork types."""
from __future__ import annotations

import pytest
from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork


class TestLayerInfoDefaults:
    def test_new_fields_have_correct_defaults(self):
        li = LayerInfo(name="bg", description="sky", z_index=0)
        # V2 new fields
        assert li.content_type == "background"
        assert li.dominant_colors == []
        assert li.regeneration_prompt == ""
        assert li.visible is True
        # V1 compat
        assert li.bbox is None
        # V1 unchanged fields
        assert li.blend_mode == "normal"
        assert li.bg_color == "white"
        assert li.locked is False

    def test_id_auto_generated(self):
        li = LayerInfo(name="bg", description="", z_index=0)
        assert li.id.startswith("layer_")
        assert len(li.id) == len("layer_") + 8  # "layer_" + 8 hex chars

    def test_id_unique_per_instance(self):
        a = LayerInfo(name="a", description="", z_index=0)
        b = LayerInfo(name="b", description="", z_index=1)
        assert a.id != b.id

    def test_bbox_none_by_default(self):
        li = LayerInfo(name="x", description="", z_index=0)
        assert li.bbox is None

    def test_bbox_accepts_dict_for_v1_compat(self):
        bbox = {"x": 10, "y": 20, "w": 50, "h": 60}
        li = LayerInfo(name="x", description="", z_index=0, bbox=bbox)
        assert li.bbox == bbox

    def test_explicit_field_setting(self):
        li = LayerInfo(
            name="subject",
            description="a dragon",
            z_index=2,
            content_type="subject",
            dominant_colors=["#FF0000", "#00FF00"],
            regeneration_prompt="Draw a red dragon",
            visible=False,
            blend_mode="screen",
            bg_color="black",
            locked=True,
            bbox={"x": 5, "y": 5, "w": 90, "h": 90},
        )
        assert li.name == "subject"
        assert li.description == "a dragon"
        assert li.z_index == 2
        assert li.content_type == "subject"
        assert li.dominant_colors == ["#FF0000", "#00FF00"]
        assert li.regeneration_prompt == "Draw a red dragon"
        assert li.visible is False
        assert li.blend_mode == "screen"
        assert li.bg_color == "black"
        assert li.locked is True
        assert li.bbox == {"x": 5, "y": 5, "w": 90, "h": 90}

    def test_explicit_id_overrides_default(self):
        li = LayerInfo(name="x", description="", z_index=0, id="layer_custom01")
        assert li.id == "layer_custom01"


class TestLayerResultV2:
    def test_basic(self):
        info = LayerInfo(name="fg", description="tree", z_index=1)
        lr = LayerResult(info=info, image_path="fg.png")
        assert lr.info is info
        assert lr.image_path == "fg.png"
        assert lr.scores == {}

    def test_with_scores(self):
        info = LayerInfo(name="bg", description="", z_index=0)
        lr = LayerResult(info=info, image_path="bg.png", scores={"L1": 0.8, "L2": 0.7})
        assert lr.scores["L1"] == 0.8


class TestLayeredArtworkV2:
    def test_defaults(self):
        la = LayeredArtwork(composite_path="comp.png", layers=[], manifest_path="manifest.json")
        assert la.brief is None
        assert la.source_image == ""
        assert la.split_mode == ""

    def test_source_image_and_split_mode(self):
        la = LayeredArtwork(
            composite_path="comp.png",
            layers=[],
            manifest_path="manifest.json",
            source_image="original.png",
            split_mode="vlm_semantic",
        )
        assert la.source_image == "original.png"
        assert la.split_mode == "vlm_semantic"

    def test_with_layers(self):
        info = LayerInfo(name="bg", description="", z_index=0)
        lr = LayerResult(info=info, image_path="bg.png")
        la = LayeredArtwork(
            composite_path="comp.png",
            layers=[lr],
            manifest_path="manifest.json",
        )
        assert len(la.layers) == 1
        assert la.layers[0].info.name == "bg"
