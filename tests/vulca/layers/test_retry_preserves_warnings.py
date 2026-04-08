"""v0.13.2 P2: retry_layers preserves non-validation warnings from prior manifest."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from PIL import Image


def _seed_artifact(tmp_path: Path) -> None:
    manifest = {
        "version": 3,
        "width": 512,
        "height": 512,
        "source_image": "",
        "split_mode": "",
        "generation_path": "a",
        "layerability": "discouraged",
        "tradition": "chinese_xieyi",
        "partial": True,
        "warnings": ["tradition-layerability discouraged: chinese_xieyi"],
        "created_at": "2026-04-08T00:00:00Z",
        "layers": [
            {
                "id": "layer_bg_000",
                "name": "bg",
                "description": "background",
                "z_index": 0,
                "blend_mode": "normal",
                "content_type": "background",
                "visible": True,
                "locked": False,
                "file": "bg.png",
                "dominant_colors": [],
                "regeneration_prompt": "",
                "opacity": 1.0,
                "x": 0.0,
                "y": 0.0,
                "width": 100.0,
                "height": 100.0,
                "rotation": 0.0,
                "content_bbox": None,
                "position": "",
                "coverage": "",
                "source": "a",
                "status": "failed",
                "reason": "validation_failed",
                "attempts": 1,
            }
        ],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    # Create a missing-file scenario isn't needed; we target by name directly.
    Image.new("RGBA", (4, 4), (0, 0, 0, 0)).save(tmp_path / "bg.png")


def test_retry_preserves_prior_non_validation_warnings(tmp_path: Path, monkeypatch):
    _seed_artifact(tmp_path)

    from vulca.layers import retry as retry_mod
    from vulca.layers.layered_generate import LayeredResult

    async def _noop_layered_generate(**kwargs):
        return LayeredResult(layers=[], failed=[])

    monkeypatch.setattr(retry_mod, "layered_generate", _noop_layered_generate)

    # Stub get_tradition so we don't need the real tradition loader.
    class _Trad:
        canvas_color = "#ffffff"
        canvas_description = "white canvas"
        style_keywords = ""
        key_strategy = "luminance"

    from vulca.cultural import loader as _loader
    monkeypatch.setattr(_loader, "get_tradition", lambda name: _Trad())

    asyncio.run(retry_mod.retry_layers(
        str(tmp_path),
        layer_names=["bg"],
        provider=None,
    ))

    rebuilt = json.loads((tmp_path / "manifest.json").read_text())
    assert "tradition-layerability discouraged: chinese_xieyi" in rebuilt["warnings"]
