"""Tests for remaining audit findings — RED first."""
import json
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from vulca.layers.types import LayerInfo


class TestGeminiZeroDimensions:
    """I6: _dims_to_aspect_ratio(w, 0) should not crash."""

    def test_height_zero_no_crash(self):
        from vulca.providers.gemini import _dims_to_aspect_ratio
        # Should return some valid ratio, not ZeroDivisionError
        result = _dims_to_aspect_ratio(1024, 0)
        assert isinstance(result, str)
        assert ":" in result

    def test_width_zero_no_crash(self):
        from vulca.providers.gemini import _dims_to_aspect_ratio
        result = _dims_to_aspect_ratio(0, 1024)
        assert isinstance(result, str)
        assert ":" in result

    def test_both_zero_no_crash(self):
        from vulca.providers.gemini import _dims_to_aspect_ratio
        result = _dims_to_aspect_ratio(0, 0)
        assert result == "1:1"


class TestManifestV2MissingId:
    """I7: V2 manifest with missing 'id' field should not KeyError."""

    def test_v2_manifest_missing_id_loads(self):
        from vulca.layers.manifest import load_manifest
        with tempfile.TemporaryDirectory() as td:
            img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
            img.save(str(Path(td) / "bg.png"))
            # V2 manifest but layer has no "id" field
            manifest = {
                "version": 2, "width": 10, "height": 10,
                "layers": [{
                    "name": "bg", "description": "background",
                    "file": "bg.png", "z_index": 0,
                    "blend_mode": "normal", "content_type": "background",
                    "visible": True, "locked": False,
                    "dominant_colors": [], "regeneration_prompt": "",
                    # NOTE: no "id" field
                }],
            }
            (Path(td) / "manifest.json").write_text(json.dumps(manifest))
            artwork = load_manifest(td)
            assert len(artwork.layers) == 1
            # Should have auto-generated id
            assert artwork.layers[0].info.id.startswith("layer_")
