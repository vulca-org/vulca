import asyncio

import pytest

pytest.importorskip("fastmcp")

from vulca.mcp_server import vulca_layered_create, vulca_layers_retry  # noqa: E402


def test_layered_create_runs_with_mock(tmp_path):
    out = asyncio.run(vulca_layered_create(
        intent="远山薄雾",
        tradition="chinese_xieyi",
        provider="mock",
        output_dir=str(tmp_path),
    ))
    # With mock provider every layer fails provider decoding, but the pipeline
    # still completes and CompositeNode writes manifest.json.
    assert isinstance(out, dict)
    assert (tmp_path / "manifest.json").exists()


def test_layers_retry_handles_missing_dir():
    out = asyncio.run(vulca_layers_retry(artifact_dir=""))
    assert out.get("error")

    out = asyncio.run(vulca_layers_retry(artifact_dir="/nonexistent/path/xyz"))
    assert out.get("error")


def test_layers_retry_unknown_layer_returns_structured_error(tmp_path):
    """P0.1 #2 MCP surface: bad layer name must return error + unknown/available."""
    import json as _json
    manifest = {
        "version": 3, "width": 256, "height": 256, "source_image": "",
        "split_mode": "", "generation_path": "a", "layerability": "native",
        "partial": False, "warnings": [], "created_at": "2026-04-08T00:00:00Z",
        "layers": [
            {"id": "layer_a", "name": "bg", "description": "", "z_index": 0,
             "blend_mode": "normal", "content_type": "background",
             "visible": True, "locked": False, "file": "bg.png",
             "dominant_colors": [], "regeneration_prompt": "", "opacity": 1.0,
             "x": 0, "y": 0, "width": 100, "height": 100, "rotation": 0,
             "content_bbox": None, "status": "ok", "source": "a"},
        ],
    }
    (tmp_path / "manifest.json").write_text(_json.dumps(manifest))
    (tmp_path / "bg.png").write_bytes(b"PNG")

    out = asyncio.run(vulca_layers_retry(
        artifact_dir=str(tmp_path),
        layer="nope",
        tradition="chinese_xieyi",
        provider="mock",
    ))
    assert out.get("error")
    assert "nope" in str(out.get("error", ""))
    assert out.get("unknown") == ["nope"]
    assert "bg" in out.get("available", [])
