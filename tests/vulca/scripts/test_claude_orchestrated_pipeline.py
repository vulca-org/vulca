"""Regression tests for the Claude-orchestrated segmentation pipeline.

Unit tests for pure helpers (needs_upscale, needs_tile, _iou, _nms_bboxes,
_z_index_for, tile_image). Golden tests comparing manifest invariants
against the committed 24-image baseline.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))


# ─────────────────────────────────────────────────────────────────
# Unit tests — pure helpers
# ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def pipeline_module():
    """Import once; loaders are lazy so no models download."""
    import claude_orchestrated_pipeline as m
    return m


class TestShapeAdapters:
    def test_needs_upscale_small_square(self, pipeline_module):
        assert pipeline_module.needs_upscale(320, 320)

    def test_needs_upscale_tiny_rect(self, pipeline_module):
        assert pipeline_module.needs_upscale(200, 300)

    def test_needs_upscale_medium(self, pipeline_module):
        assert not pipeline_module.needs_upscale(800, 600)

    def test_needs_upscale_large_thin(self, pipeline_module):
        # Don't upscale a landscape scroll — it'll be tiled
        assert not pipeline_module.needs_upscale(2560, 120)

    def test_needs_tile_extreme_wide(self, pipeline_module):
        assert pipeline_module.needs_tile(2560, 120)

    def test_needs_tile_square(self, pipeline_module):
        assert not pipeline_module.needs_tile(1024, 1024)

    def test_needs_tile_mild_wide(self, pipeline_module):
        # 2:1 ratio is not extreme enough
        assert not pipeline_module.needs_tile(2000, 1000)


class TestIoU:
    def test_iou_identical(self, pipeline_module):
        a = [0, 0, 100, 100]
        assert pipeline_module._iou(a, a) == pytest.approx(1.0)

    def test_iou_disjoint(self, pipeline_module):
        assert pipeline_module._iou([0, 0, 50, 50], [100, 100, 150, 150]) == 0.0

    def test_iou_half_overlap(self, pipeline_module):
        # 100x100 boxes, 50% overlap in x
        a = [0, 0, 100, 100]
        b = [50, 0, 150, 100]
        # intersection 50*100=5000, union 15000, IoU = 1/3
        assert pipeline_module._iou(a, b) == pytest.approx(1 / 3)


class TestNMS:
    def test_nms_no_overlap(self, pipeline_module):
        dets = [
            ([0, 0, 50, 50], 0.9, "a"),
            ([100, 100, 150, 150], 0.8, "b"),
        ]
        kept = pipeline_module._nms_bboxes(dets, iou_threshold=0.5)
        assert len(kept) == 2

    def test_nms_drops_dup(self, pipeline_module):
        dets = [
            ([0, 0, 100, 100], 0.9, "high"),
            ([5, 5, 95, 95], 0.7, "low_dup"),
        ]
        kept = pipeline_module._nms_bboxes(dets, iou_threshold=0.5)
        assert len(kept) == 1
        assert kept[0][2] == "high"


class TestTileImage:
    def test_tile_horizontal_scroll(self, pipeline_module):
        from PIL import Image
        img = Image.new("RGB", (1000, 100), "black")
        tiles = list(pipeline_module.tile_image(img, tile_size=100))
        assert len(tiles) > 1
        # Each tile offset x is within bounds
        for tile, (ox, oy, ow, oh) in tiles:
            assert oy == 0
            assert ow > 0 and oh == 100
            assert ox >= 0 and ox + ow <= 1000

    def test_tile_single_pass_square(self, pipeline_module):
        from PIL import Image
        img = Image.new("RGB", (500, 500), "black")
        tiles = list(pipeline_module.tile_image(img, tile_size=500))
        # Square image with tile == image: 1 tile
        assert len(tiles) == 1


class TestZIndexFromSemanticPath:
    def test_background(self, pipeline_module):
        assert pipeline_module._z_index_for("background") == 0

    def test_background_sub(self, pipeline_module):
        assert pipeline_module._z_index_for("background.sky") == 10

    def test_subject(self, pipeline_module):
        z = pipeline_module._z_index_for("subject.person[0]")
        assert 40 <= z <= 55  # in subject range

    def test_foreground(self, pipeline_module):
        assert pipeline_module._z_index_for("foreground.chair") == 80

    def test_hands_higher_than_clothing(self, pipeline_module):
        z_hands = pipeline_module._z_index_for("subject.body.hands")
        z_cloth = pipeline_module._z_index_for("subject.body.clothing")
        assert z_hands > z_cloth


# ─────────────────────────────────────────────────────────────────
# Golden manifest tests — compare counts/names against baseline
# ─────────────────────────────────────────────────────────────────

LAYERS_DIR = REPO / "assets" / "showcase" / "layers_v2"

# Expected minimum layer counts per image (below which = regression).
# Updated after Tier 2 completion, 2026-04-17.
EXPECTED_MIN_LAYERS = {
    "mona-lisa": 8,
    "napalm-girl": 20,
    "creation-of-adam": 8,
    "migrant-mother": 20,
    "girl-pearl-earring": 9,
    "nighthawks": 10,
    "the-scream": 4,
    "birth-of-venus": 7,
    "american-gothic": 20,
    "afghan-girl": 8,
    "saigon-execution": 10,
    "trump-portrait": 10,
    "trump-mugshot": 7,
    "trump-shooting": 9,
    "the-kiss": 3,
    "vulture-and-girl": 3,
    "qingming-bridge": 3,
}


def manifest(slug: str) -> dict | None:
    p = LAYERS_DIR / slug / "manifest.json"
    return json.loads(p.read_text()) if p.exists() else None


@pytest.mark.parametrize("slug", sorted(EXPECTED_MIN_LAYERS.keys()))
def test_manifest_status_ok(slug):
    m = manifest(slug)
    if m is None:
        pytest.skip(f"no manifest for {slug} (run pipeline first)")
    assert m.get("status") == "ok", \
        f"{slug}: status={m.get('status')}, expected ok"


@pytest.mark.parametrize("slug,min_layers", sorted(EXPECTED_MIN_LAYERS.items()))
def test_manifest_layer_count(slug, min_layers):
    m = manifest(slug)
    if m is None:
        pytest.skip(f"no manifest for {slug}")
    actual = len(m["layers"])
    assert actual >= min_layers, \
        f"{slug}: got {actual} layers, expected >= {min_layers} (regression)"


@pytest.mark.parametrize("slug", sorted(EXPECTED_MIN_LAYERS.keys()))
def test_manifest_has_detection_report(slug):
    m = manifest(slug)
    if m is None:
        pytest.skip()
    dr = m.get("detection_report")
    assert dr is not None, f"{slug}: missing detection_report"
    assert "per_entity" in dr
    assert "success_rate" in dr
    assert "detected" in dr
    assert "requested" in dr


@pytest.mark.parametrize("slug", sorted(EXPECTED_MIN_LAYERS.keys()))
def test_every_layer_png_exists(slug):
    m = manifest(slug)
    if m is None:
        pytest.skip()
    slug_dir = LAYERS_DIR / slug
    for layer in m["layers"]:
        p = slug_dir / layer["file"]
        assert p.exists(), f"{slug}: missing layer file {layer['file']}"
        # Non-empty PNG
        assert p.stat().st_size > 100, f"{slug}: {layer['file']} is empty"


@pytest.mark.parametrize("slug", sorted(EXPECTED_MIN_LAYERS.keys()))
def test_no_missed_entities_in_report(slug):
    """For each detected entity in plan, there must be a corresponding layer."""
    m = manifest(slug)
    if m is None:
        pytest.skip()
    dr = m["detection_report"]
    detected_entities = [e for e in dr["per_entity"] if e.get("status") == "detected"]
    # Each detected entity's name should be present in some layer
    layer_names = {l["name"] for l in m["layers"]}
    for e in detected_entities:
        # Layer name may be exact match, or used as prefix for sub-layers
        name = e["name"]
        assert name in layer_names or any(ln.startswith(f"{name}__") for ln in layer_names), \
            f"{slug}: detected entity {name!r} has no corresponding layer"
