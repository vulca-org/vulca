"""Phase 1.7 — locked-layer respect in redraw + manifest round-trip of v5 fields.

Ensures that:
1. redraw_layer refuses to touch a locked layer (e.g. pipeline-synthesized
   `residual` layer from hierarchical overlap resolution).
2. Manifest round-trip (write → load) preserves the new v5 fields:
   parent_layer_id, quality_status, area_pct.
"""
from __future__ import annotations

import asyncio
import json
import pytest
from pathlib import Path

from vulca.layers.types import LayerInfo, LayerResult, LayeredArtwork
from vulca.layers.manifest import write_manifest, load_manifest


def _make_info(name: str, z: int = 50, **kw) -> LayerInfo:
    return LayerInfo(name=name, description=f"desc for {name}", z_index=z, **kw)


def _make_artwork(layers: list[LayerInfo], tmp_path: Path) -> LayeredArtwork:
    lrs = [LayerResult(info=info, image_path=str(tmp_path / f"{info.name}.png"))
           for info in layers]
    return LayeredArtwork(
        composite_path=str(tmp_path / "composite.png"),
        layers=lrs,
        manifest_path=str(tmp_path / "manifest.json"),
    )


class TestRedrawRespectsLocked:
    def test_redraw_locked_raises(self, tmp_path):
        """Redrawing a locked layer must raise BEFORE any provider call."""
        from vulca.layers.redraw import redraw_layer

        info = _make_info("residual", z=1, locked=True)
        artwork = _make_artwork([info], tmp_path)

        # Guard fires before provider is even imported; pytest.raises catches
        # the ValueError synchronously from the coroutine.
        with pytest.raises(ValueError, match=r"locked"):
            asyncio.run(redraw_layer(
                artwork,
                layer_name="residual",
                instruction="change me",
                artwork_dir=str(tmp_path),
            ))

    def test_redraw_not_found_still_raises(self, tmp_path):
        """Baseline: unknown layer still raises its original ValueError."""
        from vulca.layers.redraw import redraw_layer

        info = _make_info("existing", z=50, locked=False)
        artwork = _make_artwork([info], tmp_path)

        with pytest.raises(ValueError, match=r"not found"):
            asyncio.run(redraw_layer(
                artwork,
                layer_name="nonexistent",
                instruction="change me",
                artwork_dir=str(tmp_path),
            ))


class TestManifestV5Roundtrip:
    def test_parent_layer_id_and_quality_roundtrip(self, tmp_path):
        parent = _make_info("parent", z=50)
        child = _make_info(
            "child",
            z=62,
            parent_layer_id=parent.id,
            quality_status="detected",
            area_pct=4.5,
        )
        residual = _make_info(
            "residual",
            z=1,
            locked=True,
            quality_status="residual",
            area_pct=25.5,
        )
        write_manifest(
            layers=[parent, child, residual],
            output_dir=str(tmp_path),
            width=1000,
            height=1000,
            generation_path="orchestrated",
            layerability="0.9",
        )
        # Create empty PNGs so load_manifest's filesystem checks pass
        for n in ("parent", "child", "residual", "composite"):
            (tmp_path / f"{n}.png").write_bytes(b"")

        artwork = load_manifest(str(tmp_path))
        loaded = {lr.info.name: lr.info for lr in artwork.layers}

        assert loaded["parent"].parent_layer_id is None
        assert loaded["child"].parent_layer_id == parent.id

        assert loaded["residual"].parent_layer_id is None
        assert loaded["residual"].quality_status == "residual"
        assert loaded["residual"].area_pct == 25.5
        assert loaded["residual"].locked is True

        assert loaded["parent"].quality_status == "detected"  # default
        assert loaded["parent"].area_pct == 0.0               # default

        assert loaded["child"].quality_status == "detected"
        assert loaded["child"].area_pct == 4.5

    def test_legacy_manifest_loads_with_safe_defaults(self, tmp_path):
        """Manifests missing Phase 1.7 fields must still load cleanly."""
        legacy = {
            "version": 4,
            "width": 500,
            "height": 500,
            "generation_path": "layered",
            "layerability": "0.7",
            "layers": [
                {
                    "id": "layer_abc123",
                    "name": "bg",
                    "description": "a background",
                    "z_index": 0,
                    "blend_mode": "normal",
                    "content_type": "background",
                    "visible": True,
                    "locked": False,
                    "file": "bg.png",
                    "dominant_colors": [],
                    "regeneration_prompt": "",
                    "opacity": 1.0,
                    "x": 0.0, "y": 0.0, "width": 100.0, "height": 100.0,
                    "rotation": 0.0, "content_bbox": None,
                    "position": "", "coverage": "",
                    "semantic_path": "background",
                    # NO parent_layer_id / quality_status / area_pct
                },
            ],
        }
        (tmp_path / "manifest.json").write_text(json.dumps(legacy))
        (tmp_path / "bg.png").write_bytes(b"")

        artwork = load_manifest(str(tmp_path))
        info = artwork.layers[0].info
        assert info.parent_layer_id is None
        assert info.quality_status == "detected"
        assert info.area_pct == 0.0
