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
