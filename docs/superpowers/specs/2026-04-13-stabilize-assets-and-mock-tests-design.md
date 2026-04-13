# Stabilize v3 Assets + E2E Mock Tests

**Date:** 2026-04-13
**Status:** Approved (post codex + superpowers scope review)
**Type:** Stabilization + Testing

## Background

v0.15.1 shipped with a rewritten README using mixed v2+v3 assets. Several v3 assets are incomplete due to MPS intermittent failures (black images under GPU pressure). Additionally, the E2E runner has zero automated test coverage — all verification is manual.

## Goals

1. **Phase A:** Produce clean v3 assets for layered (Phase 2), defense3 (Phase 4), and studio (Phase 7) by running on a freshly restarted ComfyUI. Update README display images.
2. **Phase D:** Add pytest E2E mock tests for all 8 phases so CI can verify pipeline logic without GPU.

## Non-Goals

- Not replacing v2 GIFs, master painting decompositions, or scenario comparison images (no v3 equivalent exists).
- Not adding GPU-based integration tests (requires ComfyUI running).
- Not fixing the underlying MPS bugs (upstream PyTorch issue).

---

## Phase A: Stabilize v3 Display Assets

### Strategy

Run phases sequentially on a freshly restarted ComfyUI, validating between each. If a phase produces black/corrupt images, restart ComfyUI and retry once.

### Steps

1. Restart ComfyUI: `pkill -9 -f ComfyUI; cd ~/dev/ComfyUI && ./venv/bin/python main.py --port 8188 --disable-auto-launch`
2. Run Phase 2 (layered): `--phases 2 --provider comfyui`
3. Validate: all layer PNGs > 10KB, composite exists and > 10KB
4. Run Phase 4 (defense3): `--phases 4 --provider comfyui`
5. Validate: both variant composites > 10KB
6. Run Phase 7 (studio): `--phases 7 --provider comfyui`
7. Validate: at least 1 concept PNG, final.png exists
8. Run `make-readme-assets.py` to regenerate display composites
9. Update any README image references if new assets are better than current

### Validation criteria

A PNG is "good" if:
- File size > 10KB (black images are ~4KB)
- PNG magic header present (`\x89PNG`)
- Visual spot-check: no noise, no anchors, recognizable subject matter

### Fallback

If a phase still produces black images after 1 ComfyUI restart + retry:
- Keep existing v2 asset for that README section
- Log the failure in the e2e-report.json
- Do not block on it

### v2 assets that stay permanently

| Asset | Reason |
|-------|--------|
| `vhs-create.gif`, `vhs-layers.gif`, `vhs-studio.gif`, `vhs-tools.gif` | Animated GIFs, can't regenerate from E2E script |
| `masters/qi_baishi_*`, `masters/mona_lisa_*` | Real artwork decomposition, not generated |
| `scenario1-comparison.png`, `scenario2-poster.png` | Hand-composed comparison images |
| `tools-viz.png` | Algorithmic visualization, not generated |

---

## Phase D: E2E Mock Tests

### Prerequisite: Upgrade MockImageProvider to PNG

**File:** `src/vulca/providers/mock.py`

**Problem:** `MockImageProvider.generate()` returns SVG (`image/svg+xml`). The E2E runner's `_validate_png_bytes()` requires PNG magic header. All phases except 8 will crash with mock.

**Fix:** Replace SVG generation with a solid-color PNG via Pillow:
```python
from PIL import Image
import io, base64

img = Image.new("RGBA", (width, height), (128, 128, 200, 255))
buf = io.BytesIO()
img.save(buf, format="PNG")
image_b64 = base64.b64encode(buf.getvalue()).decode()
return ImageResult(image_b64=image_b64, mime="image/png", metadata={})
```

This makes mock output consumable by all downstream pipeline operations (composite, keying, redraw, inpaint blend).

### Test file structure

```
tests/
  test_e2e_mock.py          # All 8 phase mock tests in one file
```

Single file because:
- All tests share the same fixtures (temp output dir, mock provider env vars)
- Tests run fast with mock (~1-2s each, no GPU)
- Easier to maintain than 8 separate files

### Test fixtures

```python
@pytest.fixture
def e2e_env(tmp_path):
    """Set up environment for mock E2E runs."""
    # Create gallery dir with a synthetic PNG (Phase 5/6 dependency)
    gallery_dir = tmp_path / "gallery"
    gallery_dir.mkdir()
    img = Image.new("RGB", (1024, 1024), (200, 180, 160))
    img.save(gallery_dir / "chinese_xieyi.png")
    
    # Patch output paths to use tmp_path
    monkeypatch env vars and module-level constants
    
    return tmp_path
```

### Per-phase test assertions

| Phase | Test Name | Key Assertions |
|-------|-----------|---------------|
| 1 | `test_phase1_gallery_mock` | Returns dict with `phase=1, status`, `entries` list non-empty, all entries have `tradition` key |
| 2 | `test_phase2_layered_mock` | Returns dict with `phase=2`, `manifest.json` created with `layers` array, composite.png exists |
| 3 | `test_phase3_evaluate_mock` | Returns dict with `phase=3`, `images_ok` > 0, each entry has `scores` dict with L1-L5 keys |
| 4 | `test_phase4_defense3_mock` | Returns dict with `phase=4`, `entries` has 2 items (no_ref + with_ref), both have `status` |
| 5 | `test_phase5_edit_mock` | Returns dict with `phase=5`, `layer_redrawn` key present, `before.png` and `after.png` exist |
| 6 | `test_phase6_inpaint_mock` | Returns dict with `phase=6`, `before.png` exists, `after.png` exists |
| 7 | `test_phase7_studio_mock` | Returns dict with `phase=7`, does not crash (studio with mock may produce minimal output) |
| 8 | `test_phase8_tools_mock` | Returns dict with `phase=8, status="ok"`, `brushstroke` and `composition` keys present |

### What tests do NOT verify

- Image visual quality (mock produces solid-color rectangles)
- RGBA mode correctness (mock doesn't go through keying)
- Style-ref anchoring effectiveness (needs real diffusion)
- VLM score accuracy (mock returns fixed scores)

### Dependency handling

- Phase 5 needs Phase 2 artifacts → test creates synthetic layered dir with manifest.json + fake layer PNGs
- Phase 6 needs Phase 1 gallery → test creates synthetic gallery PNG
- Phase 3 needs Phase 1 gallery → same synthetic gallery
- Phase 8 needs an input image → same synthetic PNG

Each test is self-contained with its own fixtures. No test depends on another test's output.

### Mock VLM for Phase 3

Phase 3 calls `aevaluate()` which uses the VLM provider. Set `VULCA_VLM_MODEL=mock` or use the existing `mock=True` parameter on `aevaluate()`. Check which mechanism the E2E runner supports and use it.

---

## Success Criteria

### Phase A
1. `assets/demo/v3/layered/composite.png` is a clean Chinese ink wash landscape (> 10KB, no anchors)
2. `assets/demo/v3/defense3/no_ref/composite.png` and `with_ref/composite.png` are real images
3. `assets/demo/v3/studio/` has concept PNGs and final output
4. `make-readme-assets.py` produces updated display images
5. e2e-report.json shows all regenerated phases as `ok`

### Phase D
6. `pytest tests/test_e2e_mock.py -v` passes all 8 tests
7. No test requires ComfyUI, Ollama, or any external service
8. Tests run in < 30 seconds total
9. MockImageProvider returns valid PNG (not SVG)

---

## Files Changed

### Phase A (runtime only)
- `assets/demo/v3/layered/` — regenerated
- `assets/demo/v3/defense3/` — regenerated
- `assets/demo/v3/studio/` — regenerated
- `assets/demo/v3/readme/` — updated display composites

### Phase D (~200 lines new code)
- `src/vulca/providers/mock.py` — upgrade to PNG output (~15 lines changed)
- `tests/test_e2e_mock.py` — new file (~180 lines)

---

## Estimated Time

| Task | Time |
|------|------|
| Phase A: restart + 3 phases + validation | ~2h (wall time dominated by ComfyUI generation) |
| Phase D prerequisite: mock PNG upgrade | ~30min |
| Phase D: 8 mock tests | ~3h |
| Review + polish | ~30min |
| **Total** | ~6h |

## Risk

**Risk: MPS produces black images even after restart.**
Mitigated: one retry with ComfyUI restart. If still fails, keep v2 assets.

**Risk: Mock tests pass but real pipeline has different behavior.**
Accepted: mock tests verify structure and orchestration, not generation quality. Real E2E validation remains manual.
