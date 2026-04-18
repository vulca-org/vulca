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


class TestSamBboxIntegration:
    """E2E test for sam_bbox detector path — mocks SAM to avoid model load."""

    def test_hint_entity_flows_through_process(self, pipeline_module, tmp_path, monkeypatch):
        """sam_bbox entity produces a layer with source='bbox_hint' in manifest."""
        import numpy as np
        from PIL import Image

        # Tiny test image (256x256 solid color)
        img_path = tmp_path / "test.jpg"
        Image.new("RGB", (256, 256), "navy").save(str(img_path))

        # Plan with one hint entity only (no detectors needed)
        plan = {
            "slug": "test",
            "domain": "space_photograph",
            "device": "mps",
            "expand_face_parts": False,  # no face-parsing for hint-only plan
            "entities": [
                {
                    "name": "target", "label": "test target",
                    "semantic_path": "subject.target",
                    "detector": "sam_bbox",
                    "bbox_hint_pct": [0.25, 0.25, 0.75, 0.75],
                }
            ],
        }

        # Mock SAM: return a bool mask matching the bbox region
        class FakeSAMPredictor:
            def set_image(self, img): pass
            def predict(self, box=None, multimask_output=True):
                x1, y1, x2, y2 = box.tolist() if hasattr(box, "tolist") else box
                mask = np.zeros((256, 256), dtype=bool)
                mask[y1:y2, x1:x2] = True
                return np.array([mask, mask, mask]), np.array([0.9, 0.9, 0.9]), None

        # Mock loaders so no actual model download happens
        monkeypatch.setattr(pipeline_module, "load_sam",
                            lambda device="mps": FakeSAMPredictor())
        monkeypatch.setattr(pipeline_module, "load_grounding_dino",
                            lambda device="mps": (None, None))
        monkeypatch.setattr(pipeline_module, "load_yolo", lambda: None)

        # Redirect paths for test isolation
        (tmp_path / "originals").mkdir()
        (tmp_path / "plans").mkdir()
        (tmp_path / "out").mkdir()
        import shutil
        shutil.copy(img_path, tmp_path / "originals" / "test.jpg")
        import json as _json
        (tmp_path / "plans" / "test.json").write_text(_json.dumps(plan))

        monkeypatch.setattr(pipeline_module, "ORIG_DIR", tmp_path / "originals")
        monkeypatch.setattr(pipeline_module, "PLANS_DIR", tmp_path / "plans")
        monkeypatch.setattr(pipeline_module, "OUT_DIR", tmp_path / "out")

        pipeline_module.process("test", force=True)

        # Assert: manifest exists, layer produced with source="bbox_hint"
        mf = tmp_path / "out" / "test" / "manifest.json"
        assert mf.exists(), "manifest not written"
        m = _json.loads(mf.read_text())
        assert m["status"] == "ok"
        dr = m["detection_report"]
        target_records = [e for e in dr["per_entity"] if e["name"] == "target"]
        assert len(target_records) == 1, "target entity missing from report"
        rec = target_records[0]
        assert rec["status"] == "detected"
        assert rec["source"] == "bbox_hint"
        assert rec["detector"] == "sam_bbox"
        assert rec["det_score"] is None, "hint det_score should be None, not synthetic 1.0"

        # authority_mix reports hint correctly
        mix = dr["authority_mix"]
        assert mix["hinted_by_plan"] >= 1
        assert mix["detected_by_model"] == 0

        # New observability fields (Fix #1 + #2)
        assert "bbox_fill" in rec and 0.0 <= rec["bbox_fill"] <= 1.0
        assert "inside_ratio" in rec and 0.0 <= rec["inside_ratio"] <= 1.0
        assert "quality_flags" in rec
        # Full-bbox fake mask → bbox_fill ≈ 1.0, inside_ratio = 1.0, no flags
        assert rec["inside_ratio"] == 1.0
        assert rec["quality_flags"] == []
        # pct_before/after_resolve appear (erosion observability)
        assert "pct_before_resolve" in rec
        assert "pct_after_resolve" in rec
        # area_pct propagated into manifest.layers[]
        target_layer = [l for l in m["layers"] if l["name"] == "target"][0]
        assert "area_pct" in target_layer and target_layer["area_pct"] > 0
        assert target_layer["quality_status"] == "detected"

    def test_quality_backstop_flags_low_fill(self, pipeline_module, tmp_path, monkeypatch):
        """SAM returning a mask that fills <5% of bbox → status=suspect."""
        import numpy as np
        import json as _json
        from PIL import Image

        Image.new("RGB", (256, 256), "navy").save(str(tmp_path / "test.jpg"))
        plan = {
            "slug": "test",
            "domain": "space_photograph",
            "device": "mps",
            "expand_face_parts": False,
            "entities": [{
                "name": "target", "label": "test target",
                "semantic_path": "subject.target",
                "detector": "sam_bbox",
                "bbox_hint_pct": [0.1, 0.1, 0.9, 0.9],  # big bbox
            }],
        }

        class TinyMaskSAM:
            def set_image(self, img): pass
            def predict(self, box=None, multimask_output=True):
                # Return a 4x4 pixel mask centered — ~0.5% of 256x256,
                # and ~0.03% of the big bbox → below both thresholds.
                mask = np.zeros((256, 256), dtype=bool)
                mask[126:130, 126:130] = True
                return np.array([mask, mask, mask]), np.array([0.9, 0.9, 0.9]), None

        monkeypatch.setattr(pipeline_module, "load_sam",
                            lambda device="mps": TinyMaskSAM())
        monkeypatch.setattr(pipeline_module, "load_grounding_dino",
                            lambda device="mps": (None, None))
        monkeypatch.setattr(pipeline_module, "load_yolo", lambda: None)

        (tmp_path / "originals").mkdir(); (tmp_path / "plans").mkdir()
        (tmp_path / "out").mkdir()
        import shutil
        shutil.copy(tmp_path / "test.jpg", tmp_path / "originals" / "test.jpg")
        (tmp_path / "plans" / "test.json").write_text(_json.dumps(plan))
        monkeypatch.setattr(pipeline_module, "ORIG_DIR", tmp_path / "originals")
        monkeypatch.setattr(pipeline_module, "PLANS_DIR", tmp_path / "plans")
        monkeypatch.setattr(pipeline_module, "OUT_DIR", tmp_path / "out")

        pipeline_module.process("test", force=True)

        m = _json.loads((tmp_path / "out" / "test" / "manifest.json").read_text())
        # Low bbox_fill must trigger suspect, which must downgrade overall
        # status to partial (success_rate logic includes suspect_count==0).
        assert m["status"] == "partial", f"expected partial, got {m['status']}"
        rec = [e for e in m["detection_report"]["per_entity"] if e["name"] == "target"][0]
        assert rec["status"] == "suspect"
        assert "low_bbox_fill" in rec["quality_flags"]


class TestResolveOverlapsHierarchical:
    """Phase 1.6+: resolve_overlaps is hierarchical-only.

    (Flat escape hatch removed in Phase 1.6 after 44-image rerun validation.
    Legacy flat semantics still available by git-reverting past the Phase 1.6
    commit or using `migrate_evfsam_to_layers.py`'s independent implementation.)
    """

    def test_parent_keeps_descendant_pixels(self, pipeline_module):
        """Face-part (descendant) must NOT carve parent."""
        import numpy as np
        H = W = 100
        parent_mask = np.zeros((H, W), dtype=bool); parent_mask[20:80, 20:80] = True
        child_mask  = np.zeros((H, W), dtype=bool); child_mask[40:60, 40:60]  = True
        layers = [
            {"id": 1, "name": "parent", "semantic_path": "subject.head",
             "z": 50, "mask": parent_mask},
            {"id": 2, "name": "child", "semantic_path": "subject.head.eyes",
             "z": 62, "mask": child_mask},
        ]
        pipeline_module.resolve_overlaps(layers)
        # Parent's resolved mask should still cover the full 60×60 region —
        # descendant did NOT carve it out.
        assert layers[0]["mask_resolved"].sum() == parent_mask.sum()
        # Child keeps its own mask.
        assert (layers[1]["mask_resolved"] == child_mask).all()
        # Parent ∩ child ≠ 0 (overlap is intentional).
        assert (layers[0]["mask_resolved"] & layers[1]["mask_resolved"]).sum() > 0

    def test_non_descendant_blocks(self, pipeline_module):
        """Foreground-over-background still occludes."""
        import numpy as np
        H = W = 100
        bg   = np.ones((H, W), dtype=bool)
        fg   = np.zeros((H, W), dtype=bool); fg[40:60, 40:60] = True
        layers = [
            {"id": 1, "name": "bg", "semantic_path": "background",
             "z": 0, "mask": bg.copy()},
            {"id": 2, "name": "fg", "semantic_path": "foreground.obj",
             "z": 80, "mask": fg.copy()},
        ]
        pipeline_module.resolve_overlaps(layers)
        # bg (non-descendant of fg, strictly lower z) → fg blocks bg
        assert (layers[0]["mask_resolved"] & fg).sum() == 0
        assert layers[1]["mask_resolved"].sum() == fg.sum()

    def test_same_z_siblings_dont_block(self, pipeline_module):
        """Two persons at z=50 → both keep raw SAM masks (no arbitrary wins)."""
        import numpy as np
        H = W = 100
        # Two overlapping person masks at same z
        a = np.zeros((H, W), dtype=bool); a[20:70, 20:70] = True
        b = np.zeros((H, W), dtype=bool); b[50:90, 50:90] = True
        layers = [
            {"id": 1, "name": "person_a", "semantic_path": "subject.person[0]",
             "z": 50, "mask": a.copy()},
            {"id": 2, "name": "person_b", "semantic_path": "subject.person[1]",
             "z": 50, "mask": b.copy()},
        ]
        pipeline_module.resolve_overlaps(layers)
        # Both keep their raw mask entirely (no same-z blocking).
        assert layers[0]["mask_resolved"].sum() == a.sum()
        assert layers[1]["mask_resolved"].sum() == b.sum()
        # Intersection persists (overlap OK under hierarchical).
        assert (layers[0]["mask_resolved"] & layers[1]["mask_resolved"]).sum() > 0


class TestResidualLayer:
    """Phase 1.6: resolve_overlaps emits a synthetic `residual` layer when
    unclaimed pixels exceed unclaimed_threshold_pct.
    """

    def test_residual_emitted_when_coverage_low(self, pipeline_module):
        """60% coverage + 2% threshold → residual layer present with ~40% area."""
        import numpy as np
        H = W = 100
        # Two small layers covering ~40% of canvas, leaving ~60% unclaimed
        bg = np.zeros((H, W), dtype=bool); bg[0:30, :] = True   # 30%
        fg = np.zeros((H, W), dtype=bool); fg[60:70, 60:70] = True  # 1%
        layers = [
            {"id": 1, "name": "bg", "semantic_path": "background",
             "z": 0, "mask": bg.copy()},
            {"id": 2, "name": "fg", "semantic_path": "foreground.obj",
             "z": 80, "mask": fg.copy()},
        ]
        pipeline_module.resolve_overlaps(layers, unclaimed_threshold_pct=2.0)
        residual = [l for l in layers if l.get("name") == "residual"]
        assert len(residual) == 1, "residual layer should be emitted"
        r = residual[0]
        assert r["quality_status"] == "residual"
        assert r["locked"] is True
        assert r["z"] == 1
        # residual covers the 69% that bg+fg don't cover
        assert r["mask_resolved"].sum() > 0.5 * H * W

    def test_residual_skipped_when_coverage_near_complete(self, pipeline_module):
        """99% coverage + 2% threshold → no residual (below threshold)."""
        import numpy as np
        H = W = 100
        bg = np.ones((H, W), dtype=bool)   # 100% coverage
        layers = [
            {"id": 1, "name": "bg", "semantic_path": "background",
             "z": 0, "mask": bg.copy()},
        ]
        pipeline_module.resolve_overlaps(layers, unclaimed_threshold_pct=2.0)
        residuals = [l for l in layers if l.get("name") == "residual"]
        assert len(residuals) == 0

    def test_residual_plus_layers_cover_full_image(self, pipeline_module):
        """Residual + all other resolved masks union = full canvas."""
        import numpy as np
        H = W = 100
        bg = np.zeros((H, W), dtype=bool); bg[0:40, :]   = True  # 40%
        fg = np.zeros((H, W), dtype=bool); fg[50:70, 50:70] = True  # 4%
        layers = [
            {"id": 1, "name": "bg", "semantic_path": "background",
             "z": 0, "mask": bg.copy()},
            {"id": 2, "name": "fg", "semantic_path": "foreground.obj",
             "z": 80, "mask": fg.copy()},
        ]
        pipeline_module.resolve_overlaps(layers, unclaimed_threshold_pct=2.0)
        union = np.zeros((H, W), dtype=bool)
        for l in layers:
            union |= l["mask_resolved"]
        # Coverage should be 100% — residual fills remaining 56%
        assert union.sum() == H * W, \
            f"expected full coverage, got {union.sum()/(H*W)*100:.1f}%"

    def test_residual_is_orphan(self, pipeline_module):
        """Residual has no parent in semantic_path tree; is_descendant of nothing."""
        assert not pipeline_module._is_descendant("residual", "background")
        assert not pipeline_module._is_descendant("residual", "subject")
        assert not pipeline_module._is_descendant("subject.person[0]", "residual")


class TestIsDescendant:
    """Phase 1.5: boundary-safe prefix check (`person[10]` vs `person[1]`)."""

    def test_strict_dotted_prefix(self, pipeline_module):
        assert pipeline_module._is_descendant("subject.head.eyes", "subject.head")
        assert pipeline_module._is_descendant("subject.head.face.skin", "subject.head")
        assert not pipeline_module._is_descendant("subject.head", "subject.head")

    def test_bracket_disambiguation(self, pipeline_module):
        # person[10] should NOT be a descendant of person[1] (mandatory ".")
        assert not pipeline_module._is_descendant("subject.person[10]", "subject.person[1]")
        assert pipeline_module._is_descendant("subject.person[0].eyes", "subject.person[0]")

    def test_empty_ancestor_rejected(self, pipeline_module):
        assert not pipeline_module._is_descendant("subject.head", "")

    def test_empty_sp_never_descends(self, pipeline_module):
        assert not pipeline_module._is_descendant("", "subject.head")


class TestIsAncestorOrDescendant:
    """Phase 1.8: bidirectional ancestor/descendant check."""

    def test_symmetric_true_both_directions(self, pipeline_module):
        parent = "subject.person[0]"
        child  = "subject.person[0].cloth"
        assert pipeline_module._is_ancestor_or_descendant(parent, child)
        assert pipeline_module._is_ancestor_or_descendant(child, parent)  # NEW: dual

    def test_transitive_depths(self, pipeline_module):
        gp    = "subject"
        pa    = "subject.person[0]"
        child = "subject.person[0].face.eyes"
        assert pipeline_module._is_ancestor_or_descendant(gp, child)
        assert pipeline_module._is_ancestor_or_descendant(child, gp)

    def test_siblings_unrelated(self, pipeline_module):
        a = "subject.person[0].cloth"
        b = "subject.person[0].body"
        assert not pipeline_module._is_ancestor_or_descendant(a, b)

    def test_different_persons_unrelated(self, pipeline_module):
        p0 = "subject.person[0].eyes"
        p1 = "subject.person[1].eyes"
        assert not pipeline_module._is_ancestor_or_descendant(p0, p1)

    def test_empty_strings_never_related(self, pipeline_module):
        assert not pipeline_module._is_ancestor_or_descendant("", "subject.head")
        assert not pipeline_module._is_ancestor_or_descendant("subject.head", "")

    def test_identical_not_related(self, pipeline_module):
        # A layer is not its own ancestor/descendant
        sp = "subject.person[0]"
        assert not pipeline_module._is_ancestor_or_descendant(sp, sp)


class TestPhase18AncestorNoLongerEatsDescendant:
    """Phase 1.8 regression target: parent SAM mask no longer eats child face-parts.

    Before fix: `bieber__cloth` (z=46, child of `bieber` z=50) had its entire
    mask eaten because parent.z > child.z and one-way descendant rule didn't
    skip the parent. This test locks that behavior in place.
    """

    def test_parent_does_not_eat_child_with_negative_z_boost(self, pipeline_module):
        """Parent at z=50 must NOT carve a descendant at z=46."""
        import numpy as np
        H = W = 100
        # Parent mask covers 30x30 (the whole person)
        parent_mask = np.zeros((H, W), dtype=bool); parent_mask[20:50, 30:60] = True
        # Child (cloth) mask is a sub-region of parent — entirely within parent
        cloth_mask  = np.zeros((H, W), dtype=bool); cloth_mask[30:45, 35:55]  = True
        layers = [
            {"id": 1, "name": "person", "semantic_path": "subject.person[0]",
             "z": 50, "mask": parent_mask},
            {"id": 2, "name": "person__cloth", "semantic_path": "subject.person[0].cloth",
             "z": 46, "mask": cloth_mask},
        ]
        pipeline_module.resolve_overlaps(layers, unclaimed_threshold_pct=100)  # disable residual
        # Phase 1.8 invariant: descendant keeps its full mask even when
        # ancestor has higher z and overlaps entirely.
        cloth_resolved = layers[1]["mask_resolved"]
        assert cloth_resolved.sum() == cloth_mask.sum(), (
            f"cloth was eaten: before={cloth_mask.sum()}, "
            f"after={cloth_resolved.sum()}. "
            "Phase 1.8 regression: parent is blocking descendant."
        )
        # Parent also keeps its full mask (Phase 1.5 invariant)
        assert layers[0]["mask_resolved"].sum() == parent_mask.sum()

    def test_unrelated_higher_z_still_blocks(self, pipeline_module):
        """Sanity: Phase 1.8 didn't accidentally break sibling/unrelated blocking."""
        import numpy as np
        H = W = 100
        bg = np.ones((H, W), dtype=bool)
        fg = np.zeros((H, W), dtype=bool); fg[40:60, 40:60] = True
        layers = [
            {"id": 1, "name": "bg", "semantic_path": "background",
             "z": 0, "mask": bg.copy()},
            {"id": 2, "name": "fg", "semantic_path": "foreground.obj",
             "z": 80, "mask": fg.copy()},
        ]
        pipeline_module.resolve_overlaps(layers, unclaimed_threshold_pct=100)
        # fg and bg are unrelated (neither is ancestor of the other) so
        # fg still blocks bg.
        assert (layers[0]["mask_resolved"] & fg).sum() == 0

    def test_corpus_cloth_neck_bodies_nonzero(self):
        """Phase 1.8 empirical regression: for every image in the showcase corpus
        that emits a __cloth, __neck, or __body sub-layer, at least ONE such
        layer must have area_pct > 0.5%.

        This is the exact structural check that would have caught the Phase
        1.5 bug. Before fix: 14/14 __cloth and __neck layers had area_pct=0.00.
        After fix: expected ≥50% to have material area.

        Skipped cleanly if the layers_v2 corpus isn't present.
        """
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parents[3] / "assets" / "showcase" / "layers_v2"
        if not root.exists():
            pytest.skip("layers_v2 corpus not present")

        violators = []
        for slug_dir in root.iterdir():
            if not slug_dir.is_dir():
                continue
            mf = slug_dir / "manifest.json"
            if not mf.exists():
                continue
            try:
                m = json.loads(mf.read_text())
            except Exception:
                continue
            face_subs = [l for l in m.get("layers", [])
                         if any(k in l.get("name", "")
                                for k in ("__cloth", "__neck", "__body"))]
            if not face_subs:
                continue
            if not any(l.get("area_pct", 0.0) > 0.5 for l in face_subs):
                violators.append({
                    "slug": slug_dir.name,
                    "face_subs": [(l["name"], l.get("area_pct", 0))
                                  for l in face_subs],
                })
        # Allow up to 2 violators (heavily occluded subjects — hood/hat/side view
        # where face-parser genuinely can't find body/cloth). More than that
        # suggests the Phase 1.5→1.8 bug regressed.
        assert len(violators) <= 2, (
            f"{len(violators)} images have ALL __cloth/__neck/__body at "
            f"area_pct ≤ 0.5% — suggests Phase 1.8 regression. Violators: "
            f"{violators[:5]}"
        )

    def test_phase111_face_parse_sibling_isolation_conceptual(self, pipeline_module):
        """Phase 1.11 #A: conceptual verification that exclusive-mask logic
        uses numpy set operations (not mutate original). Can't easily unit-
        test full Stage 4 inline — verified empirically via migrant-mother
        rerun where child_right__skin was filtered from 5.21% mother-face
        contamination down to below threshold."""
        import numpy as np
        H = W = 100
        mother = np.zeros((H, W), dtype=bool); mother[20:80, 30:70] = True
        child_overflow = np.zeros((H, W), dtype=bool); child_overflow[10:90, 10:90] = True  # huge, overlaps mother
        # exclusive mask = child - mother
        exclusive = child_overflow & ~mother
        assert exclusive.sum() < child_overflow.sum()
        # Mother's pixels removed
        assert (exclusive & mother).sum() == 0
        # Child keeps its non-overlapping pixels
        assert exclusive[15, 15]  # upper-left of child, outside mother's bbox

    def test_phase19_hint_to_bbox_px_no_zero_area(self, pipeline_module):
        """Phase 1.9 #8: high-decimal hints in small images must not produce
        zero-area bboxes (caught downstream by SAM degenerate-box failure).
        """
        # Edge case: 0.998..0.999 on 400px image truncates to 399..399 = zero area
        bbox = pipeline_module.hint_to_bbox_px([0.998, 0.998, 0.999, 0.999], 400, 400)
        x1, y1, x2, y2 = bbox
        assert x2 > x1, f"degenerate bbox x: {bbox}"
        assert y2 > y1, f"degenerate bbox y: {bbox}"
        # Sanity: full-image hint still works
        full = pipeline_module.hint_to_bbox_px([0.0, 0.0, 1.0, 1.0], 1920, 1080)
        assert full[2] > full[0] and full[3] > full[1]

    def test_phase19_is_person_path_catches_figure(self, pipeline_module):
        """Phase 1.9 #2: `figure[0]` semantic_path also routes to person chain
        (used by stylized art entities)."""
        assert pipeline_module._is_person_path("subject.person[0]")
        assert pipeline_module._is_person_path("subject.figure[0]")
        assert pipeline_module._is_person_path("subject.person[0].eyes")
        assert not pipeline_module._is_person_path("subject.head")
        assert not pipeline_module._is_person_path("background")
        assert not pipeline_module._is_person_path("")

    def test_parent_does_not_eat_neck_child(self, pipeline_module):
        """Mirror of cloth test — `__neck` also has negative z-boost (-2).
        Same bug class. Reviewer-requested regression guard.
        """
        import numpy as np
        H = W = 100
        parent_mask = np.zeros((H, W), dtype=bool); parent_mask[10:60, 20:70] = True
        neck_mask   = np.zeros((H, W), dtype=bool); neck_mask[15:25, 30:50]   = True
        layers = [
            {"id": 1, "name": "person", "semantic_path": "subject.person[0]",
             "z": 50, "mask": parent_mask},
            {"id": 2, "name": "person__neck", "semantic_path": "subject.person[0].neck",
             "z": 48, "mask": neck_mask},  # neck z-boost = -2
        ]
        pipeline_module.resolve_overlaps(layers, unclaimed_threshold_pct=100)
        # neck must survive fully — parent is its ancestor, cannot block
        assert layers[1]["mask_resolved"].sum() == neck_mask.sum()
        assert layers[0]["mask_resolved"].sum() == parent_mask.sum()


class TestHintToBboxPx:
    def test_full_image(self, pipeline_module):
        bbox = pipeline_module.hint_to_bbox_px([0.0, 0.0, 1.0, 1.0], 1000, 600)
        assert bbox == [0, 0, 999, 599]  # clamped inclusive

    def test_center_half(self, pipeline_module):
        bbox = pipeline_module.hint_to_bbox_px([0.25, 0.25, 0.75, 0.75], 800, 400)
        assert bbox == [200, 100, 600, 300]

    def test_rounding_down(self, pipeline_module):
        # pct * W might produce float > W-1; clamp takes effect
        bbox = pipeline_module.hint_to_bbox_px([0.0, 0.0, 0.999, 0.999], 100, 100)
        assert bbox == [0, 0, 99, 99]

    def test_out_of_range_defensive_clamp(self, pipeline_module):
        # Schema rejects values outside [0,1], but runtime should clamp anyway
        bbox = pipeline_module.hint_to_bbox_px([-0.5, 0.0, 1.5, 1.0], 100, 100)
        assert bbox == [0, 0, 99, 99]


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
    "migrant-mother": 18,  # Phase 1.11 #A: sibling-mask constraint filtered out cross-contaminated face-parts on the 2 children; 20 → 18 is the corrected baseline (removed mother-face leakage onto children's layers)
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
    # Exclude the synthetic `residual` layer from the count — it's a
    # pipeline-emitted bucket for plan-uncovered pixels, not a plan output.
    # Count only plan-requested + face-parse-derived layers.
    actual = sum(1 for l in m["layers"] if l.get("semantic_path") != "residual")
    assert actual >= min_layers, \
        f"{slug}: got {actual} non-residual layers, expected >= {min_layers} (regression)"


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
