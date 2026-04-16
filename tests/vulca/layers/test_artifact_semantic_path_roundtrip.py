import json
from vulca.layers.ops import add_layer
from vulca.layers.types import LayeredArtwork


def _seed_artwork(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({
        "version": 3, "width": 512, "height": 512, "layers": [],
        "source_image": "", "split_mode": "",
    }))
    return LayeredArtwork(
        composite_path="",
        layers=[],
        manifest_path=str(tmp_path / "manifest.json"),
    )


def test_add_layer_accepts_semantic_path(tmp_path):
    artwork = _seed_artwork(tmp_path)
    result = add_layer(
        artwork, artwork_dir=str(tmp_path),
        name="eyes", description="eye detail",
        content_type="subject",
        semantic_path="subject.face.eyes",
    )
    assert result.info.semantic_path == "subject.face.eyes"


def test_add_layer_semantic_path_defaults_empty(tmp_path):
    artwork = _seed_artwork(tmp_path)
    result = add_layer(
        artwork, artwork_dir=str(tmp_path),
        name="sky", description="sky",
    )
    assert result.info.semantic_path == ""


def test_parse_v2_response_preserves_semantic_path():
    from vulca.layers.prompt import parse_v2_response
    raw = {
        "layers": [
            {"name": "eyes", "description": "eye detail", "z_index": 50,
             "content_type": "subject", "semantic_path": "subject.face.eyes"},
        ],
    }
    infos = parse_v2_response(raw)
    assert infos[0].semantic_path == "subject.face.eyes"


def test_parse_v2_response_defaults_semantic_path_empty():
    from vulca.layers.prompt import parse_v2_response
    raw = {"layers": [{"name": "sky", "description": "", "z_index": 0,
                       "content_type": "background"}]}
    infos = parse_v2_response(raw)
    assert infos[0].semantic_path == ""
