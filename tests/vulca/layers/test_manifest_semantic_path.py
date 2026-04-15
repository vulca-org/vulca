"""Phase 0 Task 1+2: LayerInfo.semantic_path dot-notation path and
manifest round-trip (writer emits key; loader tolerates missing field)."""
import json
import tempfile
from pathlib import Path

from vulca.layers.artifact import load_artifact_v3, write_artifact_v3
from vulca.layers.manifest import load_manifest, write_manifest
from vulca.layers.types import LayerInfo


def test_semantic_path_defaults_to_empty_string():
    info = LayerInfo(name="bg", description="", z_index=0)
    assert info.semantic_path == ""


def test_semantic_path_accepts_dotted_hierarchy():
    info = LayerInfo(
        name="bg",
        description="",
        z_index=0,
        semantic_path="subject.face.eyes",
    )
    assert info.semantic_path == "subject.face.eyes"


def test_semantic_path_preserves_existing_fields():
    info = LayerInfo(name="bg", description="d", z_index=5, semantic_path="x.y")
    assert info.name == "bg"
    assert info.z_index == 5
    assert info.content_type == "background"


def test_semantic_path_orthogonal_to_content_type():
    """content_type (coarse bucket) and semantic_path (free-form hierarchy)
    are independent fields — setting one must not shadow the other."""
    info = LayerInfo(
        name="eyes",
        description="",
        z_index=2,
        content_type="subject",
        semantic_path="subject.face.eyes",
    )
    assert info.content_type == "subject"
    assert info.semantic_path == "subject.face.eyes"


def test_semantic_path_round_trips_through_manifest():
    with tempfile.TemporaryDirectory() as td:
        layers = [
            LayerInfo(name="bg", description="", z_index=0,
                      semantic_path="background.catch_all"),
            LayerInfo(name="face", description="", z_index=30,
                      semantic_path="subject.face.skin"),
        ]
        write_manifest(layers, output_dir=td, width=100, height=100)
        loaded = load_manifest(td)
        paths = {lr.info.name: lr.info.semantic_path for lr in loaded.layers}
        assert paths["bg"] == "background.catch_all"
        assert paths["face"] == "subject.face.skin"


def test_manifest_writer_emits_semantic_path_key():
    with tempfile.TemporaryDirectory() as td:
        layers = [
            LayerInfo(name="a", description="", z_index=0,
                      semantic_path="subject.hair"),
        ]
        write_manifest(layers, output_dir=td, width=100, height=100)
        raw = json.loads((Path(td) / "manifest.json").read_text())
        assert "semantic_path" in raw["layers"][0]
        assert raw["layers"][0]["semantic_path"] == "subject.hair"


def test_legacy_manifest_without_semantic_path_loads_with_empty_string():
    with tempfile.TemporaryDirectory() as td:
        manifest = {
            "version": 3, "width": 100, "height": 100,
            "source_image": "", "split_mode": "extract",
            "tradition": "", "partial": False, "warnings": [],
            "created_at": "2026-04-14T00:00:00Z",
            "layers": [{
                "id": "layer_001", "name": "bg", "description": "",
                "z_index": 0, "blend_mode": "normal",
                "content_type": "background", "visible": True,
                "locked": False, "file": "bg.png",
                "dominant_colors": [], "regeneration_prompt": "",
                "opacity": 1.0, "x": 0, "y": 0,
                "width": 100, "height": 100, "rotation": 0,
                "content_bbox": None, "position": "", "coverage": "",
            }],
        }
        Path(td, "manifest.json").write_text(json.dumps(manifest))
        loaded = load_manifest(td)
        assert loaded.layers[0].info.semantic_path == ""


def test_semantic_path_round_trips_through_artifact_v3():
    """Artifact V3 path is preferred by load_artifact_v3 over manifest.json,
    so semantic_path must survive the artifact writer/loader pair too."""
    with tempfile.TemporaryDirectory() as td:
        layers = [
            LayerInfo(name="bg", description="", z_index=0,
                      semantic_path="background.catch_all"),
            LayerInfo(name="hair", description="", z_index=20,
                      semantic_path="subject.hair"),
        ]
        write_artifact_v3(layers, output_dir=td, width=100, height=100)
        loaded = load_artifact_v3(td)
        paths = {lr.info.name: lr.info.semantic_path for lr in loaded.layers}
        assert paths["bg"] == "background.catch_all"
        assert paths["hair"] == "subject.hair"


def test_artifact_writer_emits_semantic_path_key():
    with tempfile.TemporaryDirectory() as td:
        layers = [
            LayerInfo(name="a", description="", z_index=0,
                      semantic_path="subject.face.skin"),
        ]
        write_artifact_v3(layers, output_dir=td, width=100, height=100)
        raw = json.loads((Path(td) / "artifact.json").read_text())
        assert "semantic_path" in raw["layers"][0]
        assert raw["layers"][0]["semantic_path"] == "subject.face.skin"
