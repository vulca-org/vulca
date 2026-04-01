"""Tests for Artifact V3 format and extended layer types."""
import json
import tempfile
from pathlib import Path

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


from vulca.layers.artifact import write_artifact_v3, load_artifact_v3


class TestArtifactV3WriteLoad:
    def _make_layers(self):
        return [
            LayerInfo(
                name="rice_paper", description="Rice paper base", z_index=0,
                content_type="background", tradition_role="底纸",
                dominant_colors=["#F5F0E8"], status="accepted", generation_round=1,
            ),
            LayerInfo(
                name="mountains", description="Distant mountains", z_index=1,
                content_type="atmosphere", tradition_role="远景淡墨",
                blend_mode="multiply", opacity=0.7,
                status="accepted", generation_round=2,
                weakness="L2: texture variation insufficient",
            ),
        ]

    def test_write_creates_artifact_json(self, tmp_path):
        layers = self._make_layers()
        path = write_artifact_v3(
            layers=layers,
            output_dir=str(tmp_path),
            width=1024, height=1024,
            intent="水墨山水",
            tradition="chinese_xieyi",
            composite_scores={"L1": 0.90, "weighted_total": 0.88},
        )
        assert Path(path).exists()
        data = json.loads(Path(path).read_text())
        assert data["artifact_version"] == "3.0"
        assert data["intent"] == "水墨山水"
        assert data["tradition"] == "chinese_xieyi"
        assert len(data["layers"]) == 2
        assert data["layers"][0]["tradition_role"] == "底纸"
        assert data["layers"][1]["opacity"] == 0.7
        assert data["composite"]["scores"]["weighted_total"] == 0.88

    def test_load_roundtrip(self, tmp_path):
        layers = self._make_layers()
        path = write_artifact_v3(
            layers=layers, output_dir=str(tmp_path),
            width=1024, height=1024,
            intent="test", tradition="default",
        )
        loaded = load_artifact_v3(str(tmp_path))
        assert len(loaded.layers) == 2
        assert loaded.layers[0].info.tradition_role == "底纸"
        assert loaded.layers[1].info.opacity == 0.7

    def test_load_v2_manifest_compat(self, tmp_path):
        """V2 manifest loads with V3 defaults."""
        v2 = {
            "version": 2, "width": 1024, "height": 1024,
            "source_image": "", "split_mode": "extract",
            "created_at": "2026-01-01T00:00:00Z",
            "layers": [{
                "id": "l1", "name": "bg", "description": "bg",
                "z_index": 0, "blend_mode": "normal",
                "content_type": "background", "visible": True,
                "locked": False, "file": "bg.png",
                "dominant_colors": ["#FFF"],
                "regeneration_prompt": "bg",
            }],
        }
        (tmp_path / "manifest.json").write_text(json.dumps(v2))
        loaded = load_artifact_v3(str(tmp_path))
        assert len(loaded.layers) == 1
        assert loaded.layers[0].info.tradition_role == ""
        assert loaded.layers[0].info.opacity == 1.0
