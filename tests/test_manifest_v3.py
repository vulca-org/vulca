import json
from pathlib import Path

from vulca.layers.manifest import MANIFEST_VERSION, load_manifest, write_manifest
from vulca.layers.types import LayerInfo


def _layers():
    return [LayerInfo(name="bg", description="paper", z_index=0,
                      content_type="background", tradition_role="纸")]


def test_manifest_version_is_3():
    assert MANIFEST_VERSION == 3


def test_manifest_writes_new_fields(tmp_path):
    p = write_manifest(
        _layers(), output_dir=str(tmp_path), width=1024, height=1024,
        generation_path="a", layerability="native", partial=False,
    )
    data = json.loads(Path(p).read_text())
    assert data["version"] == 3
    assert data["generation_path"] == "a"
    assert data["layerability"] == "native"
    assert data["partial"] is False
    assert data["warnings"] == []


def test_manifest_v2_still_loads(tmp_path):
    """A v2 file (no new fields) should load with defaults, not crash."""
    v2 = {
        "version": 2, "width": 256, "height": 256, "source_image": "", "split_mode": "",
        "created_at": "2025-01-01T00:00:00Z",
        "layers": [{"id": "x", "name": "bg", "description": "", "z_index": 0,
                    "blend_mode": "normal", "content_type": "background",
                    "visible": True, "locked": False, "file": "bg.png",
                    "dominant_colors": [], "regeneration_prompt": "",
                    "opacity": 1.0, "x": 0, "y": 0, "width": 100, "height": 100,
                    "rotation": 0, "content_bbox": None}],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(v2))
    artwork = load_manifest(str(tmp_path))
    assert len(artwork.layers) == 1


def test_layer_info_has_position_and_coverage_fields():
    """P0.2: position/coverage must be first-class dataclass fields on
    LayerInfo, not dunder-private attrs set via setattr. The VLM planner
    emits them and the anchored prompt builder + cache key both depend
    on them — if retry can't round-trip them through the manifest, it
    silently regenerates layers with the weaker default spatial block
    and gets a different cache key from the original run."""
    l = LayerInfo(name="x", description="", z_index=0,
                  position="upper third", coverage="20-30%")
    assert l.position == "upper third"
    assert l.coverage == "20-30%"


def test_manifest_round_trips_position_and_coverage(tmp_path):
    """P0.2: manifest must persist + reload position/coverage per layer
    so `layers retry` can reconstruct the original spatial anchoring."""
    layers = [LayerInfo(
        name="mist", description="distant mist", z_index=0,
        content_type="atmosphere", position="upper portion",
        coverage="15-25%",
    )]
    p = write_manifest(
        layers, output_dir=str(tmp_path), width=768, height=1024,
        generation_path="a", layerability="native",
    )
    data = json.loads(Path(p).read_text())
    assert data["layers"][0]["position"] == "upper portion"
    assert data["layers"][0]["coverage"] == "15-25%"

    artwork = load_manifest(str(tmp_path))
    loaded = artwork.layers[0].info
    assert loaded.position == "upper portion"
    assert loaded.coverage == "15-25%"


def test_manifest_layer_extras_propagated(tmp_path):
    layers = _layers()
    extras = {layers[0].id: {"source": "a", "cache_hit": True, "attempts": 1,
                              "canvas_color": "#ffffff", "key_strategy": "luminance"}}
    p = write_manifest(
        layers, output_dir=str(tmp_path), width=512, height=512,
        layer_extras=extras,
    )
    data = json.loads(Path(p).read_text())
    layer0 = data["layers"][0]
    assert layer0["source"] == "a"
    assert layer0["cache_hit"] is True
    assert layer0["key_strategy"] == "luminance"
    # Core fields still intact
    assert layer0["id"] == layers[0].id
    assert layer0["name"] == "bg"
