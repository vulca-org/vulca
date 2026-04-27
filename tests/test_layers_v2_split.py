"""Tests for vulca.layers.split — V2 split modes (extract + regenerate)."""
from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

from vulca.layers.split import split_extract, split_regenerate
from vulca.layers.types import LayerInfo, LayerResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_red_blue_image(size: int = 100) -> Image.Image:
    """Create a 100×100 RGB image: left half red, right half blue."""
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    arr[:, : size // 2] = (220, 30, 30)   # red
    arr[:, size // 2 :] = (30, 30, 220)   # blue
    return Image.fromarray(arr, mode="RGB")


def _save_temp(img: Image.Image, path: Path) -> str:
    img.save(str(path))
    return str(path)


# ---------------------------------------------------------------------------
# TestSplitExtract
# ---------------------------------------------------------------------------

class TestSplitExtract:

    def test_produces_full_canvas_rgba(self):
        """split_extract → both layers are full-canvas RGBA images."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="red_layer",
                    description="red subject",
                    z_index=0,
                    content_type="subject",
                    dominant_colors=["#DC1E1E"],
                ),
                LayerInfo(
                    name="blue_layer",
                    description="blue subject",
                    z_index=1,
                    content_type="subject",
                    dominant_colors=["#1E1EDC"],
                ),
            ]

            results = split_extract(str(src), layers, output_dir=td, tolerance=30)

            assert len(results) == 2

            for result in results:
                assert isinstance(result, LayerResult), "Each result must be a LayerResult"
                layer_img = Image.open(result.image_path)
                # Full-canvas: same size as original
                assert layer_img.size == (100, 100), (
                    f"Layer {result.info.name} must be full-canvas 100×100, got {layer_img.size}"
                )
                # Must be RGBA
                assert layer_img.mode == "RGBA", (
                    f"Layer {result.info.name} must be RGBA, got {layer_img.mode}"
                )

    def test_extract_red_layer_has_red_opaque(self):
        """Red-dominant layer: red pixels should be opaque, blue pixels transparent."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="red_layer",
                    description="red subject",
                    z_index=0,
                    content_type="subject",
                    dominant_colors=["#DC1E1E"],  # close to (220, 30, 30)
                ),
            ]

            results = split_extract(str(src), layers, output_dir=td, tolerance=30)
            assert len(results) == 1

            layer_img = Image.open(results[0].image_path)
            arr = np.array(layer_img)  # H × W × 4 (RGBA)

            # Left half (red region) — alpha should be substantially opaque
            left_alpha = arr[:, :50, 3].astype(float)
            # Right half (blue region) — alpha should be substantially transparent
            right_alpha = arr[:, 50:, 3].astype(float)

            assert left_alpha.mean() > right_alpha.mean() + 30, (
                f"Red region (mean alpha={left_alpha.mean():.1f}) should be more opaque "
                f"than blue region (mean alpha={right_alpha.mean():.1f})"
            )

    def test_writes_manifest(self):
        """split_extract must create manifest.json in output_dir."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="bg",
                    description="background",
                    z_index=0,
                    content_type="background",
                    dominant_colors=["#DC1E1E"],
                ),
            ]

            split_extract(str(src), layers, output_dir=td)

            manifest_path = Path(td) / "manifest.json"
            assert manifest_path.exists(), "manifest.json must be created in output_dir"

            manifest = json.loads(manifest_path.read_text())
            # V2 manifest
            assert manifest.get("version") == 3
            assert manifest.get("width") == 100
            assert manifest.get("height") == 100
            assert len(manifest.get("layers", [])) == 1
            assert manifest["layers"][0]["name"] == "bg"

    def test_sorted_by_z_index(self):
        """Results must be sorted by z_index ascending."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="top",
                    description="top layer",
                    z_index=2,
                    content_type="subject",
                    dominant_colors=["#DC1E1E"],
                ),
                LayerInfo(
                    name="bottom",
                    description="bottom layer",
                    z_index=0,
                    content_type="background",
                    dominant_colors=["#1E1EDC"],
                ),
            ]

            results = split_extract(str(src), layers, output_dir=td)
            z_indices = [r.info.z_index for r in results]
            assert z_indices == sorted(z_indices), "Results must be sorted by z_index"


# ---------------------------------------------------------------------------
# TestSplitRegenerate
# ---------------------------------------------------------------------------

class TestSplitRegenerate:

    def test_split_regenerate_mock(self):
        """Mock provider: 1 layer file created + LayerResult returned."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="background",
                    description="background layer",
                    z_index=0,
                    content_type="background",
                    dominant_colors=["#DC1E1E"],
                    regeneration_prompt="background layer on transparent canvas",
                ),
            ]

            results = asyncio.run(
                split_regenerate(
                    str(src),
                    layers,
                    output_dir=td,
                    provider="mock",
                    tradition="chinese_xieyi",
                )
            )

            # At least 1 result returned
            assert len(results) == 1, f"Expected 1 LayerResult, got {len(results)}"

            result = results[0]
            assert isinstance(result, LayerResult), "Result must be LayerResult"

            # File must exist on disk
            assert Path(result.image_path).exists(), (
                f"Layer file {result.image_path} must exist"
            )

            # Saved image must be RGBA and full-canvas
            layer_img = Image.open(result.image_path)
            assert layer_img.mode == "RGBA", f"Layer must be RGBA, got {layer_img.mode}"
            assert layer_img.size == (100, 100), (
                f"Layer must be full-canvas 100×100, got {layer_img.size}"
            )

    def test_split_regenerate_writes_manifest(self):
        """Mock provider: manifest.json is written after regeneration."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src.png"
            img = _make_red_blue_image(100)
            img.save(str(src))

            layers = [
                LayerInfo(
                    name="sky",
                    description="sky layer",
                    z_index=0,
                    content_type="background",
                    dominant_colors=["#1E1EDC"],
                ),
            ]

            asyncio.run(
                split_regenerate(
                    str(src),
                    layers,
                    output_dir=td,
                    provider="mock",
                )
            )

            manifest_path = Path(td) / "manifest.json"
            assert manifest_path.exists(), "manifest.json must be written by split_regenerate"

            manifest = json.loads(manifest_path.read_text())
            assert manifest.get("split_mode") == "regenerate"
            assert manifest.get("version") == 3


# ---------------------------------------------------------------------------
# TestMultiInstanceDetection — v0.18.0 detection-layer multi_instance opt-in
# ---------------------------------------------------------------------------

class _FakeTensor:
    """Minimal stand-in for the torch tensors returned by Grounding DINO post-
    processing. Only `.cpu().numpy()` is exercised by `detect_all_bboxes`."""

    def __init__(self, vals):
        self._vals = vals

    def cpu(self):
        return self

    def numpy(self):
        return np.array(self._vals)


class _FakeInputs(dict):
    """Behaves like HuggingFace BatchEncoding: supports both `**inputs` unpack
    (dict.__iter__/keys) AND attribute access (`inputs.input_ids`). The real
    `detect_all_bboxes` calls both `dino_model(**inputs)` and `inputs.input_ids`."""

    def __init__(self):
        super().__init__()
        self.input_ids = None  # post_process accepts None for our fake processor

    def to(self, device):  # noqa: ARG002 — device unused in fake
        return self


class _FakeProcessor:
    """Stand-in for `AutoProcessor.from_pretrained('IDEA-Research/grounding-dino-tiny')`.

    `__call__` builds the inputs payload; `post_process_grounded_object_detection`
    returns three "lanterns" bboxes with scores 0.9 / 0.85 / 0.8. Threshold
    filtering is honoured so threshold-driven tests behave like the real model.
    """

    def __init__(self):
        # Three non-overlapping bboxes labelled "lanterns" with descending scores.
        # NB: the test fixture intent is asserted at the top of every test that
        # consumes mock_dino (per v0.18 Task 3 lesson on fixture-intent drift).
        self._raw = [
            ([100, 200, 200, 400], 0.90, "lanterns"),
            ([300, 200, 400, 400], 0.85, "lanterns"),
            ([500, 200, 600, 400], 0.80, "lanterns"),
        ]

    def __call__(self, images=None, text=None, return_tensors=None):  # noqa: ARG002
        return _FakeInputs()

    def post_process_grounded_object_detection(
        self, outputs, input_ids, threshold=0.0, text_threshold=0.0,  # noqa: ARG002
        target_sizes=None,  # noqa: ARG002
    ):
        # Filter by score threshold like the real model would.
        kept = [d for d in self._raw if d[1] >= threshold]
        return [{
            "scores": _FakeTensor([d[1] for d in kept]),
            "boxes": _FakeTensor([d[0] for d in kept]),
            "text_labels": [d[2] for d in kept],
        }]


class _FakeDinoModel:
    """`detect_all_bboxes` only uses `dino_model(**inputs)` for its return value
    via `outputs`, which our fake processor's post-process ignores."""

    def __call__(self, **kw):  # noqa: ARG002
        return None


@pytest.fixture
def mock_dino():
    """Mock Grounding DINO returning 3 non-overlapping lantern bboxes.

    Fixture intent (assert at top of any consuming test, per v0.18 Task 3
    lesson `feedback_test_fixtures_assert_intent.md`):
      - 3 bboxes total
      - all labelled "lanterns"
      - scores 0.9, 0.85, 0.8 (strictly descending)
      - bboxes are non-overlapping (x-spans 100-200, 300-400, 500-600)
    """
    return (
        _FakeProcessor(),
        _FakeDinoModel(),
        "cpu",
        Image.new("RGB", (800, 600)),
    )


def _assert_mock_dino_intent(mock_dino):
    """Re-verify mock_dino fixture intent inside each test using it.

    Future-proofs against silent fixture drift: if someone changes scores,
    bbox count, or labels, every dependent test fails loudly with this
    explicit assertion rather than producing misleading green/red signals.
    """
    proc = mock_dino[0]
    assert len(proc._raw) == 3, "mock_dino must produce exactly 3 detections"
    assert all(d[2] == "lanterns" for d in proc._raw), \
        "mock_dino must label all detections 'lanterns'"
    scores = [d[1] for d in proc._raw]
    assert scores == [0.90, 0.85, 0.80], \
        f"mock_dino scores must be [0.9, 0.85, 0.8], got {scores}"
    # Non-overlapping check (IoU = 0 for all pairs)
    from vulca._segment import _iou
    boxes = [d[0] for d in proc._raw]
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            assert _iou(a, b) == 0.0, \
                f"mock_dino bboxes must be non-overlapping, got overlap {a} vs {b}"


class TestMultiInstanceDetection:
    """v0.18.0: verify multi-instance bbox return at the detection layer.

    Helpers (`_iou`, `_nms_bboxes`) are imported from `vulca._segment` so the
    tests collect under CI without torch (cop.py imports torch at module
    level — see src/vulca/_segment.py docstring). `detect_all_bboxes` itself
    DOES need torch (it calls `torch.no_grad()`), so the two
    `detect_all_bboxes` tests will be skipped on CI but execute in dev.
    """

    def test_nms_keep_n_unlimited_default(self):
        """keep_n=None preserves current behavior (returns all dedup'd)."""
        from vulca._segment import _nms_bboxes
        dets = [
            ([0, 0, 100, 100], 0.9, "a"),
            ([200, 0, 300, 100], 0.8, "a"),  # no overlap
            ([0, 0, 90, 90], 0.7, "a"),       # overlaps first
        ]
        kept = _nms_bboxes(dets, iou_threshold=0.5)
        assert len(kept) == 2  # third one dropped (overlaps first)

    def test_nms_keep_n_caps_to_n(self):
        """keep_n=2 returns top-2 by score after NMS."""
        from vulca._segment import _nms_bboxes
        dets = [
            ([0, 0, 100, 100], 0.9, "a"),
            ([200, 0, 300, 100], 0.8, "a"),
            ([400, 0, 500, 100], 0.7, "a"),
            ([600, 0, 700, 100], 0.6, "a"),
        ]
        kept = _nms_bboxes(dets, iou_threshold=0.5, keep_n=2)
        assert len(kept) == 2
        assert kept[0][1] >= kept[1][1]  # score-sorted desc

    def test_nms_keep_n_zero_clamps_to_one(self):
        """keep_n=0 is clamped to 1 (not interpreted as 'return empty list')."""
        from vulca._segment import _nms_bboxes
        dets = [
            ([0, 0, 100, 100], 0.9, "a"),
            ([200, 0, 300, 100], 0.8, "a"),
        ]
        kept = _nms_bboxes(dets, iou_threshold=0.5, keep_n=0)
        assert len(kept) == 1, "keep_n=0 should clamp to 1, not return []"
        assert kept[0][1] == pytest.approx(0.9), "kept item should be highest-score"

    def test_nms_keep_n_negative_clamps_to_one(self):
        """keep_n=-1 (or other negative) is also clamped to 1."""
        from vulca._segment import _nms_bboxes
        dets = [
            ([0, 0, 100, 100], 0.9, "a"),
            ([200, 0, 300, 100], 0.8, "a"),
        ]
        kept = _nms_bboxes(dets, iou_threshold=0.5, keep_n=-5)
        assert len(kept) == 1, "negative keep_n should clamp to 1"

    def test_detect_all_bboxes_single_label_backward_compat(self, mock_dino):
        """Without multi_instance kwarg, returns dict[label, tuple] as before."""
        _assert_mock_dino_intent(mock_dino)
        pytest.importorskip("torch")  # cop import requires torch; CI skips
        from scripts.claude_orchestrated_pipeline import detect_all_bboxes
        result = detect_all_bboxes(*mock_dino, labels=["lanterns"], threshold=0.15)
        assert "lanterns" in result
        assert isinstance(result["lanterns"], tuple)
        assert len(result["lanterns"]) == 3  # (bbox, score, phrase)
        # Highest-score detection wins under backward-compat tuple form
        assert result["lanterns"][1] == pytest.approx(0.9)

    def test_detect_all_bboxes_multi_instance_returns_list(self, mock_dino):
        """With multi_instance={lanterns: 8}, returns dict[label, list[tuple]]."""
        _assert_mock_dino_intent(mock_dino)
        pytest.importorskip("torch")  # cop import requires torch; CI skips
        from scripts.claude_orchestrated_pipeline import detect_all_bboxes
        result = detect_all_bboxes(
            *mock_dino, labels=["lanterns"], threshold=0.15,
            multi_instance={"lanterns": 8},
            multi_instance_box_threshold=0.25,
        )
        assert isinstance(result["lanterns"], list)
        assert len(result["lanterns"]) >= 2
        # All 3 mock detections survive (non-overlapping, all >= 0.25 threshold)
        assert len(result["lanterns"]) == 3
        assert all(isinstance(d, tuple) and len(d) == 3 for d in result["lanterns"])
        # Score-descending order (per _nms_bboxes contract)
        scores = [d[1] for d in result["lanterns"]]
        assert scores == sorted(scores, reverse=True)

    def test_multi_instance_raises_on_tiled_path(self, monkeypatch, tmp_path):
        """v0.18.0: multi_instance + tiled-image-trigger raises NotImplementedError.

        Tracks Task 4 code-review I-1: tiled/upscaled paths don't yet forward
        multi_instance kwargs. Defensive raise prevents silent degradation to
        top-1 detection on extreme-aspect inputs.

        Test setup pre-conditions (asserted inline so future fixture drift
        fails loudly per v0.18 Task 3 lesson):
          - test image is extreme-aspect (200x4000) so needs_tile(W,H) is True
          - multi_instance_labels is non-empty {"lanterns": 8}
          - heavy detector loaders are stubbed so no model download / no MPS
        """
        pytest.importorskip("torch")  # cop import requires torch; CI skips
        from scripts import claude_orchestrated_pipeline as cop

        # Pre-condition assertions: extreme aspect MUST route to the tiled path.
        W, H = 200, 4000
        assert cop.needs_tile(W, H), \
            f"test fixture intent: ({W},{H}) must trigger needs_tile; " \
            f"adjust dims if TILE_ASPECT_RATIO ({cop.TILE_ASPECT_RATIO}) changed"
        assert not cop.needs_upscale(W, H), \
            f"test fixture intent: ({W},{H}) should NOT trigger needs_upscale " \
            f"(would mask the tiled-path branch we want to exercise)"

        # Stage a temp ORIG_DIR + PLANS_DIR with the extreme-aspect image and
        # a plan that opts a single label into multi_instance.
        slug = "extreme_aspect_multi"
        orig_dir = tmp_path / "originals"
        plans_dir = tmp_path / "plans"
        out_dir = tmp_path / "out"
        orig_dir.mkdir()
        plans_dir.mkdir()
        out_dir.mkdir()
        Image.new("RGB", (W, H), (128, 128, 128)).save(
            str(orig_dir / f"{slug}.jpg"), "JPEG"
        )
        plan_payload = {
            "entities": [
                {"name": "lanterns", "label": "lantern", "multi_instance": True}
            ],
        }
        (plans_dir / f"{slug}.json").write_text(json.dumps(plan_payload))

        # Stub heavy loaders so test never touches the model hub / MPS device.
        # The raise fires before detect_all_bboxes_tiled is invoked, so the
        # DINO/SAM stubs never get exercised — but loaders themselves run
        # earlier (load_sam + load_grounding_dino) and need to no-op cleanly.
        class _StubSam:
            def set_image(self, *_a, **_k):
                return None

        monkeypatch.setattr(cop, "load_sam", lambda *_a, **_k: _StubSam())
        monkeypatch.setattr(
            cop, "load_grounding_dino", lambda *_a, **_k: (object(), object())
        )
        # Redirect module-level dirs to our temp staging.
        monkeypatch.setattr(cop, "ORIG_DIR", orig_dir)
        monkeypatch.setattr(cop, "PLANS_DIR", plans_dir)
        monkeypatch.setattr(cop, "OUT_DIR", out_dir)

        with pytest.raises(NotImplementedError, match=r"multi_instance.*tiled"):
            cop.process(
                slug, force=True, multi_instance_labels={"lantern": 8}
            )


# ---------------------------------------------------------------------------
# TestMultiInstance — v0.18.0 entity-loop multi_instance behavior
# ---------------------------------------------------------------------------
#
# Helpers below are kept module-local (not in conftest.py) so they don't get
# auto-loaded for unrelated test modules. They mock at the `detect_all_bboxes`
# / `segment_bbox` function-call seam (per Task 4 Approach E) — no real model
# weights, no torch model inference.
#
# The 8 tests in `class TestMultiInstance` exercise the entity loop from
# `process()` end-to-end at unit level, verifying:
#   - legacy single-instance preservation (test_flag_off_legacy_behavior)
#   - multi-instance N-bbox expansion + naming (test_flag_on_returns_n_layers)
#   - z_index push across subsequent entities (test_z_index_pushes_…)
#   - degraded fallback when DINO returns 1 bbox (test_degraded_when_dino_…)
#   - no-detection flag on 0 bboxes (test_no_detection)
#   - cap consumption (test_caps_at_8 — cap itself is Task 4's territory)
#   - score-desc sibling naming (test_naming_sorted_by_sam_score_desc)
#   - mixed single+multi entities in one plan (test_mixed_single_and_multi…)


class _StubSamPredictor:
    """Minimal stand-in for SAM2ImagePredictor consumed by `process()`.

    Real cop.process() calls:
      - `load_sam(device)` → SAM2ImagePredictor instance
      - `predictor.set_image(np.ndarray)` once after load
      - `segment_bbox(predictor, bbox)` per detection (this is the seam we mock
        externally — predictor is never actually consulted)
    """

    def set_image(self, *_a, **_k):
        return None

    # Defensive: if mock_segment ever forgets to patch and calls .predict(),
    # fail loud rather than crash with AttributeError mid-pipeline.
    def predict(self, *_a, **_k):  # pragma: no cover — should never run
        raise AssertionError(
            "_StubSamPredictor.predict was called — segment_bbox mock missing?"
        )


def _make_segment_bbox_mock(canvas_hw: tuple[int, int] = (600, 800),
                             sam_score: float = 0.85):
    """Build a `segment_bbox` replacement that fabricates a plausible mask.

    The mask is the bbox rectangle (clamped to canvas), giving sam_score and
    bbox_fill / inside_ratio = 1.0. That's enough for the entity loop's quality-
    flag gate to register the layer as `status="detected"` (no transparency
    flags) so we cleanly observe multi_instance-specific flags downstream.

    Args:
        canvas_hw: (H, W) of the test image. Mask is cropped to these dims.
        sam_score: returned SAM confidence; 0.85 is comfortably above the
            transparency gate's 0.65 floor (see compute_quality_flags).
    """
    H, W = canvas_hw

    def _seg(_sam_pred, bbox):
        x1, y1, x2, y2 = bbox
        mask = np.zeros((H, W), dtype=bool)
        # Clamp into canvas — defensive against bbox coords from a mocked DINO
        # that don't know the test image dims.
        x1c = max(0, min(W, int(x1)))
        y1c = max(0, min(H, int(y1)))
        x2c = max(0, min(W, int(x2)))
        y2c = max(0, min(H, int(y2)))
        mask[y1c:y2c, x1c:x2c] = True
        return mask, sam_score, 1.0, 1.0

    return _seg


def _stage_artwork(tmp_path, slug: str, plan_payload: dict,
                    canvas_wh: tuple[int, int] = (800, 600),
                    monkeypatch=None, cop=None):
    """Build minimal `process()` artwork dir staging.

    Creates ORIG_DIR / PLANS_DIR / OUT_DIR under `tmp_path`, writes a uniform-
    color JPG at the requested size, writes the plan JSON, and (if
    `monkeypatch` + `cop` provided) rebinds the three module-level dirs.

    Returns the staged paths (orig_dir, plans_dir, out_dir) for tests that
    need to inspect the post-run manifest.
    """
    W, H = canvas_wh
    orig_dir = tmp_path / "originals"
    plans_dir = tmp_path / "plans"
    out_dir = tmp_path / "out"
    orig_dir.mkdir()
    plans_dir.mkdir()
    out_dir.mkdir()
    Image.new("RGB", (W, H), (128, 128, 128)).save(
        str(orig_dir / f"{slug}.jpg"), "JPEG"
    )
    (plans_dir / f"{slug}.json").write_text(json.dumps(plan_payload))
    if monkeypatch is not None and cop is not None:
        monkeypatch.setattr(cop, "ORIG_DIR", orig_dir)
        monkeypatch.setattr(cop, "PLANS_DIR", plans_dir)
        monkeypatch.setattr(cop, "OUT_DIR", out_dir)
    return orig_dir, plans_dir, out_dir


def _stub_loaders(monkeypatch, cop):
    """No-op SAM + DINO loaders so `process()` never touches the model hub.

    The real entity loop downstream calls `detect_all_bboxes(dino_proc,
    dino_model, device, img_pil, …)` and `segment_bbox(sam_pred, bbox)` —
    both of which we replace with the function-level mocks. The loader
    return values are therefore opaque sentinels."""
    monkeypatch.setattr(cop, "load_sam", lambda *_a, **_k: _StubSamPredictor())
    monkeypatch.setattr(
        cop, "load_grounding_dino", lambda *_a, **_k: (object(), object())
    )


def _read_manifest(out_dir, slug: str) -> dict:
    """Helper: load the manifest.json `process()` wrote on success."""
    return json.loads((out_dir / slug / "manifest.json").read_text())


class TestMultiInstance:
    """v0.18.0: multi_instance entity-loop behavior.

    Mocks `detect_all_bboxes` + `segment_bbox` at the function-call seam.
    No real model weights, no torch model inference. Verifies the entity loop
    in `process()` produces the correct manifest shape, naming, z_index push,
    and `quality_flags` per spec § Edge cases (Task 6's contract).

    Each test asserts its own mock-setup intent at the top, per Task 3 lesson
    `feedback_test_fixtures_assert_intent.md`: future fixture edits that
    silently change a returned bbox count or score order will fail loudly with
    a fixture-intent assertion instead of silently producing the wrong test.
    """

    @staticmethod
    def _layer_by_name(manifest: dict, name: str) -> dict | None:
        for layer in manifest.get("layers", []):
            if layer["name"] == name:
                return layer
        return None

    @staticmethod
    def _entity_record(manifest: dict, name: str) -> dict | None:
        for rec in manifest.get("detection_report", {}).get("per_entity", []):
            if rec.get("name") == name:
                return rec
        return None

    def test_flag_off_legacy_behavior(self, monkeypatch, tmp_path):
        """multi_instance unset → top-1 tuple; 1 layer named <label> + no flag.

        Regression guard for v0.17.x callers who never set multi_instance.
        """
        pytest.importorskip("torch")
        from scripts import claude_orchestrated_pipeline as cop

        slug = "legacy_single"
        plan = {
            "domain": "renaissance_painting",
            "entities": [
                {"name": "lanterns", "label": "lantern",
                 "semantic_path": "subject.lanterns"},
            ],
        }
        _, _, out_dir = _stage_artwork(tmp_path, slug, plan,
                                        monkeypatch=monkeypatch, cop=cop)
        _stub_loaders(monkeypatch, cop)

        # Mock-intent assertion: tuple form is the legacy single-instance
        # contract — if detect_all_bboxes signature ever flips this default,
        # this test must be updated to match.
        mock_returns = {"lantern": ([100, 100, 300, 300], 0.9, "lantern")}
        assert isinstance(mock_returns["lantern"], tuple), \
            "test intent: legacy path uses tuple-form return"

        monkeypatch.setattr(cop, "detect_all_bboxes",
                            lambda *_a, **_k: mock_returns)
        monkeypatch.setattr(cop, "segment_bbox", _make_segment_bbox_mock())

        cop.process(slug, force=True)  # no multi_instance_labels

        manifest = _read_manifest(out_dir, slug)
        # Filter out synthetic background catch-all (added when no z<=10 layer).
        object_layers = [l for l in manifest["layers"]
                         if l["semantic_path"] == "subject.lanterns"]
        assert len(object_layers) == 1, \
            f"expected exactly 1 lantern layer (legacy), got {len(object_layers)}"
        assert object_layers[0]["name"] == "lanterns", \
            "legacy single-instance keeps base name with no _0 suffix"
        # No multi_instance_* flag should appear in the entity record.
        rec = self._entity_record(manifest, "lanterns")
        assert rec is not None
        flags = rec.get("quality_flags", [])
        assert not any(f.startswith("multi_instance") for f in flags), \
            f"legacy path must not emit multi_instance_* flags, got {flags}"

    def test_flag_on_returns_n_layers(self, monkeypatch, tmp_path):
        """6-bbox list → 6 sibling layers `lanterns_0..5`, sorted by score desc."""
        pytest.importorskip("torch")
        from scripts import claude_orchestrated_pipeline as cop

        slug = "multi_six"
        plan = {
            "domain": "renaissance_painting",
            "entities": [
                {"name": "lanterns", "label": "lantern",
                 "semantic_path": "subject.lanterns",
                 "multi_instance": True},
            ],
        }
        _, _, out_dir = _stage_artwork(tmp_path, slug, plan,
                                        monkeypatch=monkeypatch, cop=cop)
        _stub_loaders(monkeypatch, cop)

        # Mock-intent: 6 non-overlapping bboxes, scores strictly descending so
        # post-NMS order matches insertion order (kept under naming rule).
        bboxes = [
            ([50,  50, 150, 150], 0.95, "lantern"),
            ([200, 50, 300, 150], 0.90, "lantern"),
            ([350, 50, 450, 150], 0.85, "lantern"),
            ([500, 50, 600, 150], 0.80, "lantern"),
            ([50, 250, 150, 350], 0.75, "lantern"),
            ([200, 250, 300, 350], 0.70, "lantern"),
        ]
        assert len(bboxes) == 6, "test intent: 6-bbox fixture"
        assert [b[1] for b in bboxes] == sorted([b[1] for b in bboxes],
                                                  reverse=True), \
            "test intent: scores must be strictly descending pre-NMS"

        monkeypatch.setattr(cop, "detect_all_bboxes",
                            lambda *_a, **_k: {"lantern": bboxes})
        monkeypatch.setattr(cop, "segment_bbox", _make_segment_bbox_mock())

        cop.process(slug, force=True,
                    multi_instance_labels={"lantern": 8})

        manifest = _read_manifest(out_dir, slug)
        sibling_layers = [l for l in manifest["layers"]
                          if l["semantic_path"] == "subject.lanterns"]
        assert len(sibling_layers) == 6, \
            f"expected 6 expanded sibling layers, got {len(sibling_layers)}"
        names = sorted(l["name"] for l in sibling_layers)
        assert names == [f"lanterns_{i}" for i in range(6)], \
            f"sibling names must be lanterns_0..5, got {names}"

    def test_z_index_pushes_subsequent_entities(self, monkeypatch, tmp_path):
        """lanterns expands ×6 → subsequent person entity z bumps by N-1 = 5."""
        pytest.importorskip("torch")
        from scripts import claude_orchestrated_pipeline as cop

        slug = "z_push"
        plan = {
            # `space_photograph` profile = no person_chain, so the "person"
            # entity routes through DINO (object_entities). That's what the
            # spec's z_offset push covers; person-chain detections live in a
            # separate code path that's not part of this test's contract.
            "domain": "space_photograph",
            "entities": [
                {"name": "lanterns", "label": "lantern",
                 "semantic_path": "subject.lanterns",
                 "multi_instance": True},
                {"name": "robot", "label": "robot",
                 "semantic_path": "subject.robot"},
            ],
        }
        _, _, out_dir = _stage_artwork(tmp_path, slug, plan,
                                        monkeypatch=monkeypatch, cop=cop)
        _stub_loaders(monkeypatch, cop)

        # Six lanterns (multi-expand), one robot (single).
        lantern_bboxes = [
            ([50  + 60*i, 50, 100 + 60*i, 100], 0.95 - 0.05*i, "lantern")
            for i in range(6)
        ]
        robot_bbox = ([400, 400, 500, 500], 0.88, "robot")

        # Mock-intent assertions.
        assert len(lantern_bboxes) == 6, "test intent: lanterns expand to 6"
        assert isinstance(robot_bbox, tuple), \
            "test intent: robot is single-instance (tuple form)"

        # Z-index math: both `subject.lanterns` and `subject.robot` fall into
        # the catch-all `subject.` rule in `_z_index_for` → base z=45. After
        # 6 lanterns expand, `z_offset` = N-1 = 5. Robot's inst_idx = 0, so
        # robot.z = 45 + 5 + 0 = 50. (Lantern_5 also lands at 50 via
        # 45+0+inst_idx=5, but they have distinct semantic_paths so hierarchical
        # resolve tiebreaks deterministically — collision is by design and out
        # of scope for this test, which only verifies the push contract.)

        monkeypatch.setattr(cop, "detect_all_bboxes", lambda *_a, **_k: {
            "lantern": lantern_bboxes,
            "robot": robot_bbox,
        })
        monkeypatch.setattr(cop, "segment_bbox", _make_segment_bbox_mock())

        cop.process(slug, force=True,
                    multi_instance_labels={"lantern": 8})

        manifest = _read_manifest(out_dir, slug)
        robot_layer = self._layer_by_name(manifest, "robot")
        assert robot_layer is not None, "robot entity layer must be emitted"
        # Base z for `subject.robot` = 45 (catch-all `subject.` rule). With
        # 6 lanterns expanded ahead of it, z_offset should push by N-1 = 5.
        # Final z_index = 45 + 5 + 0 (robot's own inst_idx=0) = 50.
        assert robot_layer["z_index"] == 50, (
            f"robot.z_index must be 50 (45 base + 5 push from lanterns), "
            f"got {robot_layer['z_index']}"
        )

    def test_degraded_when_dino_returns_one(self, monkeypatch, tmp_path):
        """multi_instance opt-in but DINO returns 1 bbox → no _0 suffix + flag."""
        pytest.importorskip("torch")
        from scripts import claude_orchestrated_pipeline as cop

        slug = "degraded_one"
        plan = {
            "domain": "renaissance_painting",
            "entities": [
                {"name": "lanterns", "label": "lantern",
                 "semantic_path": "subject.lanterns",
                 "multi_instance": True},
            ],
        }
        _, _, out_dir = _stage_artwork(tmp_path, slug, plan,
                                        monkeypatch=monkeypatch, cop=cop)
        _stub_loaders(monkeypatch, cop)

        # Mock-intent: list with exactly 1 element. `is_multi_expanded` requires
        # len(detections) >= 2, so this triggers the degraded branch — the
        # keystone naming-contract case (no `_0` suffix).
        mock_returns = {"lantern": [([100, 100, 300, 300], 0.92, "lantern")]}
        assert isinstance(mock_returns["lantern"], list), \
            "test intent: must be list-form to trigger multi-instance branch"
        assert len(mock_returns["lantern"]) == 1, \
            "test intent: exactly 1 detection triggers degraded branch"

        monkeypatch.setattr(cop, "detect_all_bboxes",
                            lambda *_a, **_k: mock_returns)
        monkeypatch.setattr(cop, "segment_bbox", _make_segment_bbox_mock())

        cop.process(slug, force=True,
                    multi_instance_labels={"lantern": 8})

        manifest = _read_manifest(out_dir, slug)
        sibling_layers = [l for l in manifest["layers"]
                          if l["semantic_path"] == "subject.lanterns"]
        assert len(sibling_layers) == 1, \
            f"degraded path emits exactly 1 layer, got {len(sibling_layers)}"
        # Keystone contract: name is `<label>` with NO `_0` suffix.
        assert sibling_layers[0]["name"] == "lanterns", \
            f"degraded layer must be named 'lanterns' (no _0), got {sibling_layers[0]['name']!r}"
        # Quality flag must include multi_instance_degraded.
        rec = self._entity_record(manifest, "lanterns")
        assert rec is not None
        assert "multi_instance_degraded" in rec.get("quality_flags", []), (
            f"degraded path must flag multi_instance_degraded, "
            f"got flags={rec.get('quality_flags')}"
        )

    def test_no_detection(self, monkeypatch, tmp_path):
        """multi_instance opt-in but DINO returns no detection → 0 layers + flag.

        Spec: when label is missing from `dino_assigned`, emit a `missed`
        per_entity record with `multi_instance_no_detection` quality_flag.
        No layers.png are written for this entity.
        """
        pytest.importorskip("torch")
        from scripts import claude_orchestrated_pipeline as cop

        slug = "no_detection"
        plan = {
            "domain": "renaissance_painting",
            "entities": [
                {"name": "lanterns", "label": "lantern",
                 "semantic_path": "subject.lanterns",
                 "multi_instance": True},
            ],
        }
        _, _, out_dir = _stage_artwork(tmp_path, slug, plan,
                                        monkeypatch=monkeypatch, cop=cop)
        _stub_loaders(monkeypatch, cop)

        # Mock-intent: dino returns the dict but the label is absent — that's
        # how the real `detect_all_bboxes` signals "no detection survived
        # threshold filtering" for a label.
        mock_returns: dict = {}  # label absent
        assert "lantern" not in mock_returns, \
            "test intent: label absent triggers MISSED branch in entity loop"

        monkeypatch.setattr(cop, "detect_all_bboxes",
                            lambda *_a, **_k: mock_returns)
        monkeypatch.setattr(cop, "segment_bbox", _make_segment_bbox_mock())

        cop.process(slug, force=True,
                    multi_instance_labels={"lantern": 8})

        manifest = _read_manifest(out_dir, slug)
        # No layers under subject.lanterns.
        sibling_layers = [l for l in manifest["layers"]
                          if l["semantic_path"] == "subject.lanterns"]
        assert len(sibling_layers) == 0, (
            f"no-detection path must emit 0 layers, got {len(sibling_layers)}"
        )
        # detection_report carries the multi_instance_no_detection flag.
        rec = self._entity_record(manifest, "lanterns")
        assert rec is not None, \
            "detection_report must contain a record even on missed entities"
        assert rec.get("status") == "missed"
        assert "multi_instance_no_detection" in rec.get("quality_flags", []), (
            f"missed multi_instance entity must flag multi_instance_no_detection, "
            f"got flags={rec.get('quality_flags')}"
        )

    def test_caps_at_8(self, monkeypatch, tmp_path):
        """Entity loop consumes whatever it gets — 8 bboxes → 8 sibling layers.

        Cap enforcement itself lives in `_nms_bboxes(keep_n=8)` and is covered
        by Task 4. This test verifies the entity loop's loop-over behavior on
        a pre-capped 8-element list (does not re-test the cap itself).
        """
        pytest.importorskip("torch")
        from scripts import claude_orchestrated_pipeline as cop

        slug = "caps_eight"
        plan = {
            "domain": "renaissance_painting",
            "entities": [
                {"name": "lanterns", "label": "lantern",
                 "semantic_path": "subject.lanterns",
                 "multi_instance": True},
            ],
        }
        _, _, out_dir = _stage_artwork(tmp_path, slug, plan,
                                        monkeypatch=monkeypatch, cop=cop)
        _stub_loaders(monkeypatch, cop)

        # Mock-intent: exactly 8 bboxes, simulating Task 4's cap already
        # applied at the detection layer. Scores strictly descending so the
        # entity loop's score-desc traversal produces lanterns_0..7 in order.
        bboxes = [
            ([50 + 80*i, 50, 100 + 80*i, 100], 0.95 - 0.05*i, "lantern")
            for i in range(8)
        ]
        assert len(bboxes) == 8, \
            "test intent: exactly 8 bboxes (cap is Task 4's territory)"
        assert all(bboxes[i][1] > bboxes[i+1][1] for i in range(7)), \
            "test intent: scores strictly descending → naming order matches index"

        monkeypatch.setattr(cop, "detect_all_bboxes",
                            lambda *_a, **_k: {"lantern": bboxes})
        monkeypatch.setattr(cop, "segment_bbox", _make_segment_bbox_mock())

        cop.process(slug, force=True,
                    multi_instance_labels={"lantern": 8})

        manifest = _read_manifest(out_dir, slug)
        sibling_layers = [l for l in manifest["layers"]
                          if l["semantic_path"] == "subject.lanterns"]
        assert len(sibling_layers) == 8, \
            f"entity loop must emit 1 layer per bbox; got {len(sibling_layers)}"
        names = sorted(l["name"] for l in sibling_layers)
        assert names == [f"lanterns_{i}" for i in range(8)], \
            f"naming must produce lanterns_0..7, got {names}"

    def test_naming_sorted_by_sam_score_desc(self, monkeypatch, tmp_path):
        """3 bboxes with distinct DINO scores → lanterns_0 has highest det_score.

        Spec: ordering is preserved from `detect_all_bboxes` via _nms_bboxes
        (sorted by -score). The entity loop must NOT re-sort; lanterns_0 always
        carries the top-scoring detection.
        """
        pytest.importorskip("torch")
        from scripts import claude_orchestrated_pipeline as cop

        slug = "score_desc"
        plan = {
            "domain": "renaissance_painting",
            "entities": [
                {"name": "lanterns", "label": "lantern",
                 "semantic_path": "subject.lanterns",
                 "multi_instance": True},
            ],
        }
        _, _, out_dir = _stage_artwork(tmp_path, slug, plan,
                                        monkeypatch=monkeypatch, cop=cop)
        _stub_loaders(monkeypatch, cop)

        # Mock-intent: 3 bboxes, scores 0.92 / 0.78 / 0.65 (distinct + desc).
        bboxes = [
            ([100, 100, 200, 200], 0.92, "lantern"),
            ([300, 100, 400, 200], 0.78, "lantern"),
            ([500, 100, 600, 200], 0.65, "lantern"),
        ]
        scores = [b[1] for b in bboxes]
        assert scores == sorted(scores, reverse=True), \
            "test intent: scores pre-sorted descending (mimics _nms_bboxes)"
        assert len(set(scores)) == 3, \
            "test intent: scores must be distinct so ordering is unambiguous"

        monkeypatch.setattr(cop, "detect_all_bboxes",
                            lambda *_a, **_k: {"lantern": bboxes})
        monkeypatch.setattr(cop, "segment_bbox", _make_segment_bbox_mock())

        cop.process(slug, force=True,
                    multi_instance_labels={"lantern": 8})

        manifest = _read_manifest(out_dir, slug)
        # Pull det_score per sibling from manifest layers.
        sibling_layers = sorted(
            (l for l in manifest["layers"]
             if l["semantic_path"] == "subject.lanterns"),
            key=lambda l: l["name"],
        )
        assert len(sibling_layers) == 3, \
            f"expected 3 sibling layers, got {len(sibling_layers)}"
        det_scores = [l["det_score"] for l in sibling_layers]
        # lanterns_0 highest, lanterns_2 lowest.
        assert det_scores[0] > det_scores[1] > det_scores[2], (
            f"lanterns_0 must have highest det_score, lanterns_2 lowest; "
            f"got {dict(zip([l['name'] for l in sibling_layers], det_scores))}"
        )
        assert det_scores[0] == pytest.approx(0.92), \
            f"lanterns_0 must carry top score 0.92, got {det_scores[0]}"
        assert det_scores[2] == pytest.approx(0.65), \
            f"lanterns_2 must carry bottom score 0.65, got {det_scores[2]}"

    def test_mixed_single_and_multi_in_same_plan(self, monkeypatch, tmp_path):
        """Plan with both multi (lanterns ×N) + single (cathedral) → both work.

        Spec: cathedral path is unaffected — kept as `cathedral` (no _0 suffix),
        no z_offset push for ITSELF (it gets pushed by lanterns ahead, but its
        own loop iteration adds inst_idx=0 only). Lanterns expand to ≥2.
        """
        pytest.importorskip("torch")
        from scripts import claude_orchestrated_pipeline as cop

        slug = "mixed_plan"
        plan = {
            "domain": "renaissance_painting",
            "entities": [
                {"name": "lanterns", "label": "lantern",
                 "semantic_path": "subject.lanterns",
                 "multi_instance": True},
                {"name": "cathedral", "label": "cathedral",
                 "semantic_path": "subject.cathedral"},
            ],
        }
        _, _, out_dir = _stage_artwork(tmp_path, slug, plan,
                                        monkeypatch=monkeypatch, cop=cop)
        _stub_loaders(monkeypatch, cop)

        # Mock-intent: lanterns gets 3-bbox LIST (multi-expand); cathedral gets
        # legacy TUPLE form (single). Both forms must coexist in the same dict
        # — that's the type-discrimination contract.
        lantern_bboxes = [
            ([50, 50, 150, 150], 0.92, "lantern"),
            ([200, 50, 300, 150], 0.85, "lantern"),
            ([350, 50, 450, 150], 0.78, "lantern"),
        ]
        cathedral_bbox = ([100, 300, 700, 580], 0.88, "cathedral")
        assert isinstance(lantern_bboxes, list) and len(lantern_bboxes) >= 2, \
            "test intent: lanterns must be multi-expanding list"
        assert isinstance(cathedral_bbox, tuple), \
            "test intent: cathedral must be tuple (legacy single)"

        monkeypatch.setattr(cop, "detect_all_bboxes", lambda *_a, **_k: {
            "lantern": lantern_bboxes,
            "cathedral": cathedral_bbox,
        })
        monkeypatch.setattr(cop, "segment_bbox", _make_segment_bbox_mock())

        cop.process(slug, force=True,
                    multi_instance_labels={"lantern": 8})

        manifest = _read_manifest(out_dir, slug)
        # Lanterns: ≥2 expanded sibling layers.
        lantern_layers = [l for l in manifest["layers"]
                          if l["semantic_path"] == "subject.lanterns"]
        assert len(lantern_layers) >= 2, \
            f"lanterns must produce ≥2 layers in mixed plan, got {len(lantern_layers)}"
        assert all(l["name"].startswith("lanterns_") for l in lantern_layers), (
            f"lantern layers must be named lanterns_<n>, got "
            f"{[l['name'] for l in lantern_layers]}"
        )
        # Cathedral: exactly 1 layer named `cathedral` (no _0 suffix).
        cathedral_layer = self._layer_by_name(manifest, "cathedral")
        assert cathedral_layer is not None, \
            "cathedral path (single-instance) must be unaffected by multi-mix"
        assert cathedral_layer["semantic_path"] == "subject.cathedral"
        # Cathedral's record carries no multi_instance_* flag (it never opted in).
        cathedral_rec = self._entity_record(manifest, "cathedral")
        assert cathedral_rec is not None
        cathedral_flags = cathedral_rec.get("quality_flags", [])
        assert not any(f.startswith("multi_instance") for f in cathedral_flags), (
            f"single-instance cathedral must not carry multi_instance_* flags, "
            f"got {cathedral_flags}"
        )
