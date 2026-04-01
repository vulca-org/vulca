"""Tests for Artifact V3 format and extended layer types."""
import pytest
from vulca.layers.types import LayerInfo, LayerResult


class TestLayerInfoV3Fields:
    def test_default_new_fields(self):
        info = LayerInfo(name="bg", description="Background", z_index=0)
        assert info.tradition_role == ""
        assert info.opacity == 1.0
        assert info.status == ""
        assert info.weakness == ""
        assert info.generation_round == 0

    def test_explicit_new_fields(self):
        info = LayerInfo(
            name="mountains",
            description="Distant mountains",
            z_index=1,
            tradition_role="远景淡墨",
            opacity=0.7,
            status="rerun",
            weakness="L2: texture variation insufficient",
            generation_round=2,
        )
        assert info.tradition_role == "远景淡墨"
        assert info.opacity == 0.7
        assert info.status == "rerun"
        assert info.weakness == "L2: texture variation insufficient"
        assert info.generation_round == 2

    def test_backward_compat_no_new_fields(self):
        """V2-style construction without new fields still works."""
        info = LayerInfo(
            name="bg", description="bg", z_index=0,
            content_type="background", dominant_colors=["#FFF"],
        )
        assert info.tradition_role == ""
        assert info.opacity == 1.0
