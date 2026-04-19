"""Mocked pipeline smoke: decompose -> unload -> decompose round-trip.

Does NOT load real models. Monkeypatch pattern mirrors
tests/vulca/scripts/test_claude_orchestrated_pipeline.py:149-153.

Two tests:
  * test_decompose_unload_reload_roundtrip — run pipeline twice with
    mocked loaders, asserting manifest mtime advances (not a silent no-op)
    and second run is not wildly slower.
  * test_plan_validation_error_strings_verbatim — locks exact MCP
    error strings for plan+plan_path both/neither/malformed.
"""
import asyncio
import time
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "assets" / "showcase" / "originals" / "trump-shooting.jpg"


# Plan designed to exercise one code path only: sam_bbox hint entity.
# - No DINO detector (no object_entities).
# - No person semantic_path (no yolo_persons; has_any_person stays False).
# - expand_face_parts=False belt-and-braces disables face-parsing gate.
# The single entity uses a bbox_hint_pct so the pipeline calls SAM directly.
MINIMAL_PLAN = {
    "slug": "smoke-test",
    "domain": "news_photograph",
    "device": "mps",
    "threshold_hint": 0.2,
    "expand_face_parts": False,
    "entities": [
        {
            "name": "target",
            "label": "main subject",
            "semantic_path": "subject.target",  # NOT subject.person[...] — avoids face-parse
            "detector": "sam_bbox",
            "bbox_hint_pct": [0.20, 0.10, 0.80, 0.90],
        },
    ],
}


class _FakeSAMPredictor:
    """Mirrors scripts/claude_orchestrated_pipeline.segment_bbox expectations:
    predict(box=...) -> (masks[N,H,W], scores[N], low_res_logits|None).
    The real SamPredictor is instantiated per-run so set_image must no-op."""

    def set_image(self, img):
        pass

    def predict(self, box=None, multimask_output=True):
        # Box is an np.ndarray [x1, y1, x2, y2] in pixel coords.
        x1, y1, x2, y2 = box.tolist() if hasattr(box, "tolist") else box
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        # Fixture dims: 387 wide x 258 tall. Fill the bbox → bbox_fill≈1.0,
        # inside_ratio=1.0, no quality_flags, status=detected.
        mask = np.zeros((258, 387), dtype=bool)
        mask[y1:y2, x1:x2] = True
        masks = np.stack([mask, mask, mask], axis=0)  # shape (3, 258, 387)
        scores = np.array([0.95, 0.9, 0.85])
        return masks, scores, None


def _install_fake_loaders(monkeypatch):
    """Replace the 4 heavy loaders with stubs. Returns the cop module so the
    test can poke at loader cache_clear afterward."""
    from vulca.pipeline.segment.orchestrator import _import_cop
    cop = _import_cop()

    monkeypatch.setattr(cop, "load_sam", lambda device="mps": _FakeSAMPredictor())
    monkeypatch.setattr(cop, "load_grounding_dino",
                        lambda device="mps": (MagicMock(), MagicMock()))
    monkeypatch.setattr(cop, "load_yolo", lambda: MagicMock())
    monkeypatch.setattr(cop, "_load_sam_model", lambda device="mps": MagicMock())
    monkeypatch.setattr(cop, "load_face_parser",
                        lambda device="mps": (MagicMock(), MagicMock()))
    return cop


@pytest.mark.skipif(not FIXTURE.exists(), reason=f"fixture missing: {FIXTURE}")
def test_decompose_unload_reload_roundtrip(tmp_path, monkeypatch):
    """First decompose -> cache clear -> second decompose. Assert not silent no-op."""
    from vulca.pipeline.segment import run as pipeline_run, Plan

    cop = _install_fake_loaders(monkeypatch)
    plan = Plan.model_validate(MINIMAL_PLAN)

    out1 = tmp_path / "run1"
    t1 = time.perf_counter()
    r1 = pipeline_run(plan, FIXTURE, out1, force=True)
    first_s = time.perf_counter() - t1

    assert r1.status in ("ok", "partial"), \
        f"expected ok/partial, got {r1.status}: {r1.reason}"
    assert len(r1.layers) >= 1, "expected at least 1 layer from mocked pipeline"
    assert (out1 / "manifest.json").exists(), "manifest missing"
    manifest_mtime_1 = (out1 / "manifest.json").stat().st_mtime

    # Simulate unload_models behaviour — clear any lru caches on loaders.
    for name in ("load_grounding_dino", "load_yolo",
                 "load_face_parser", "_load_sam_model"):
        loader = getattr(cop, name, None)
        if loader is not None and hasattr(loader, "cache_clear"):
            loader.cache_clear()

    # Sleep a hair so mtime can tick on filesystems with 1s resolution.
    time.sleep(1.05)

    out2 = tmp_path / "run2"
    t2 = time.perf_counter()
    r2 = pipeline_run(plan, FIXTURE, out2, force=True)
    second_s = time.perf_counter() - t2

    assert r2.status == r1.status, f"status drift: {r1.status} -> {r2.status}"
    assert (out2 / "manifest.json").exists()
    manifest_mtime_2 = (out2 / "manifest.json").stat().st_mtime
    assert manifest_mtime_2 > manifest_mtime_1, \
        "run2 manifest mtime not advanced — run may have been silent no-op"

    # Second run shouldn't be pathologically slow (>3x) vs first, given
    # both are mocked. Floor at 5s to forgive CI jitter on tiny timings.
    assert second_s < max(first_s * 3.0, 5.0), \
        f"2nd run {second_s:.2f}s suspicious vs 1st {first_s:.2f}s"


def test_plan_validation_error_strings_verbatim():
    """Lock exact MCP error-string contract — plan arg validation paths."""
    from vulca.mcp_server import layers_split

    # The MCP tool is a FastMCP @mcp.tool() coroutine. Unwrap via .fn if needed.
    _call = getattr(layers_split, "fn", layers_split)

    # Case 1: both plan + plan_path -> "pass either plan..."
    r = asyncio.run(_call(
        image_path=str(FIXTURE),
        mode="orchestrated",
        plan="{}",
        plan_path="/tmp/nonexistent.json",
    ))
    assert "error" in r, r
    assert "pass either plan" in r["error"], r["error"]

    # Case 2: neither -> "requires 'plan'..."
    r = asyncio.run(_call(
        image_path=str(FIXTURE),
        mode="orchestrated",
    ))
    assert "error" in r, r
    assert "requires 'plan'" in r["error"], r["error"]

    # Case 3: malformed JSON -> "plan validation failed..."
    r = asyncio.run(_call(
        image_path=str(FIXTURE),
        mode="orchestrated",
        plan="not valid json",
    ))
    assert "error" in r, r
    assert "plan validation failed" in r["error"], r["error"]
