"""Tests for generate_image, view_image, and layers_list MCP tools."""
import asyncio
import base64
import json
import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image


def run(coro):
    return asyncio.run(coro)


# ── generate_image ────────────────────────────────────────────────


class TestGenerateImage:
    def test_mock_returns_all_fields(self, tmp_path):
        from vulca.mcp_server import generate_image

        r = run(generate_image("a mountain", provider="mock", output_dir=str(tmp_path)))
        assert "image_path" in r
        assert "cost_usd" in r
        assert "latency_ms" in r
        assert r["provider"] == "mock"
        # File actually exists
        assert Path(r["image_path"]).exists()

    def test_saved_image_is_valid_png(self, tmp_path):
        from vulca.mcp_server import generate_image

        r = run(generate_image("cherry blossom", provider="mock", output_dir=str(tmp_path)))
        img = Image.open(r["image_path"])
        assert img.format == "PNG"
        assert img.size[0] > 0

    def test_tradition_passed_through(self, tmp_path):
        from vulca.mcp_server import generate_image

        r = run(generate_image(
            "ink wash mountains",
            provider="mock",
            tradition="chinese_xieyi",
            output_dir=str(tmp_path),
        ))
        assert Path(r["image_path"]).exists()

    def test_reference_path_missing_returns_error(self, tmp_path):
        from vulca.mcp_server import generate_image

        r = run(generate_image(
            "test",
            provider="mock",
            reference_path="/nonexistent/image.png",
            output_dir=str(tmp_path),
        ))
        assert "error" in r

    def test_reference_path_valid(self, tmp_path):
        from vulca.mcp_server import generate_image

        # Create a reference image
        ref = tmp_path / "ref.png"
        Image.new("RGB", (64, 64), "red").save(ref)

        r = run(generate_image(
            "test with ref",
            provider="mock",
            reference_path=str(ref),
            output_dir=str(tmp_path),
        ))
        assert "image_path" in r
        assert Path(r["image_path"]).exists()

    def test_unknown_provider_returns_error(self, tmp_path):
        from vulca.mcp_server import generate_image

        with pytest.raises(ValueError, match="Unknown image provider"):
            run(generate_image("test", provider="nonexistent", output_dir=str(tmp_path)))


# ── view_image ────────────────────────────────────────────────────


class TestViewImage:
    def test_returns_all_fields(self, tmp_path):
        from vulca.mcp_server import view_image

        img_path = tmp_path / "test.png"
        Image.new("RGBA", (200, 100), "blue").save(img_path)

        r = run(view_image(str(img_path)))
        assert "image_base64" in r
        assert r["original_width"] == 200
        assert r["original_height"] == 100
        assert r["width"] <= 200
        assert r["height"] <= 100
        assert r["file_size_bytes"] > 0

    def test_thumbnail_respects_max_dimension(self, tmp_path):
        from vulca.mcp_server import view_image

        img_path = tmp_path / "big.png"
        Image.new("RGB", (4000, 2000), "green").save(img_path)

        r = run(view_image(str(img_path), max_dimension=512))
        assert r["width"] <= 512
        assert r["height"] <= 512
        assert r["original_width"] == 4000
        assert r["original_height"] == 2000

    def test_small_image_not_upscaled(self, tmp_path):
        from vulca.mcp_server import view_image

        img_path = tmp_path / "small.png"
        Image.new("RGB", (50, 30), "red").save(img_path)

        r = run(view_image(str(img_path), max_dimension=1024))
        assert r["width"] == 50
        assert r["height"] == 30

    def test_base64_is_valid_png(self, tmp_path):
        from vulca.mcp_server import view_image

        img_path = tmp_path / "check.png"
        Image.new("RGB", (100, 100), "white").save(img_path)

        r = run(view_image(str(img_path)))
        decoded = base64.b64decode(r["image_base64"])
        # PNG magic bytes
        assert decoded[:4] == b"\x89PNG"

    def test_missing_file_returns_error(self):
        from vulca.mcp_server import view_image

        r = run(view_image("/nonexistent/image.png"))
        assert "error" in r

    def test_rgba_image(self, tmp_path):
        from vulca.mcp_server import view_image

        img_path = tmp_path / "rgba.png"
        Image.new("RGBA", (100, 100), (255, 0, 0, 128)).save(img_path)

        r = run(view_image(str(img_path)))
        assert "image_base64" in r
        assert r["original_width"] == 100


# ── layers_list ───────────────────────────────────────────────────


class TestLayersList:
    def _make_artwork(self, tmp_path, layers=None, add_composite=False):
        """Helper to create a minimal artwork dir with manifest."""
        if layers is None:
            layers = [
                {"name": "background", "z_index": 0, "content_type": "background",
                 "visible": True, "blend_mode": "normal", "file": "background.png"},
                {"name": "subject", "z_index": 1, "content_type": "subject",
                 "visible": True, "blend_mode": "normal", "file": "subject.png"},
                {"name": "overlay", "z_index": 2, "content_type": "decoration",
                 "visible": False, "blend_mode": "multiply", "file": "overlay.png"},
            ]
        manifest = {
            "version": 3,
            "width": 1024,
            "height": 1024,
            "layers": layers,
        }
        (tmp_path / "manifest.json").write_text(json.dumps(manifest))
        # Create some layer PNGs
        Image.new("RGBA", (64, 64), "red").save(tmp_path / "background.png")
        Image.new("RGBA", (64, 64), "blue").save(tmp_path / "subject.png")
        # overlay.png deliberately missing
        if add_composite:
            Image.new("RGBA", (64, 64), "white").save(tmp_path / "composite.png")

    def test_returns_all_fields(self, tmp_path):
        from vulca.mcp_server import layers_list

        self._make_artwork(tmp_path)
        r = run(layers_list(str(tmp_path)))
        assert r["layer_count"] == 3
        assert r["visible_count"] == 2
        assert r["has_composite"] is False
        assert len(r["layers"]) == 3

    def test_layer_metadata(self, tmp_path):
        from vulca.mcp_server import layers_list

        self._make_artwork(tmp_path)
        r = run(layers_list(str(tmp_path)))
        bg = r["layers"][0]
        assert bg["name"] == "background"
        assert bg["z_index"] == 0
        assert bg["content_type"] == "background"
        assert bg["visible"] is True
        assert bg["blend_mode"] == "normal"

    def test_file_exists_check(self, tmp_path):
        from vulca.mcp_server import layers_list

        self._make_artwork(tmp_path)
        r = run(layers_list(str(tmp_path)))

        by_name = {l["name"]: l for l in r["layers"]}
        assert by_name["background"]["file_exists"] is True
        assert by_name["subject"]["file_exists"] is True
        assert by_name["overlay"]["file_exists"] is False  # deliberately not created

    def test_has_composite_true(self, tmp_path):
        from vulca.mcp_server import layers_list

        self._make_artwork(tmp_path, add_composite=True)
        r = run(layers_list(str(tmp_path)))
        assert r["has_composite"] is True

    def test_missing_manifest_returns_error(self, tmp_path):
        from vulca.mcp_server import layers_list

        r = run(layers_list(str(tmp_path)))
        assert "error" in r

    def test_empty_layers(self, tmp_path):
        from vulca.mcp_server import layers_list

        manifest = {"version": 3, "width": 512, "height": 512, "layers": []}
        (tmp_path / "manifest.json").write_text(json.dumps(manifest))

        r = run(layers_list(str(tmp_path)))
        assert r["layer_count"] == 0
        assert r["visible_count"] == 0
        assert r["layers"] == []

    def test_semantic_path_included(self, tmp_path):
        from vulca.mcp_server import layers_list

        layers = [{
            "name": "eyes",
            "z_index": 5,
            "content_type": "subject",
            "visible": True,
            "blend_mode": "normal",
            "file": "eyes.png",
            "semantic_path": "subject.face.eyes",
        }]
        manifest = {"version": 3, "width": 1024, "height": 1024, "layers": layers}
        (tmp_path / "manifest.json").write_text(json.dumps(manifest))
        Image.new("RGBA", (64, 64)).save(tmp_path / "eyes.png")

        r = run(layers_list(str(tmp_path)))
        assert r["layers"][0]["semantic_path"] == "subject.face.eyes"
