# Layers Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace v0.12 layer-extraction-by-VLM-mask with generation-time per-layer alpha via canonical-canvas keying, gated by tradition `layerability`. Existing v0.12 split/SAM code is repositioned as the B-path fallback.

**Architecture:** A new pure-function library `layers/layered_generate.py` orchestrates per-layer concurrent provider calls with anchored prompts and per-tradition keying. The existing `pipeline/nodes/layer_generate.py` becomes a thin adapter calling the library. The `--layered` CLI flag (already shipped in v0.12) routes through the upgraded LAYERED pipeline template; tradition `layerability` field selects A-path vs B-path internally.

**Tech Stack:** Python 3.10+, asyncio, numpy, Pillow. No new mandatory dependencies (sRGB→LAB hand-rolled, OpenCV optional via existing `[tools]` extra).

**Spec:** `docs/superpowers/specs/2026-04-08-layers-redesign-design.md`

---

## Pre-flight context (read once before starting Phase A)

These are the real APIs the plan references; skim them so the early tasks make sense:

- `src/vulca/layers/types.py` — `LayerInfo`, `LayerResult`, `LayeredArtwork` dataclasses
- `src/vulca/layers/plan_prompt.py` — `build_plan_prompt`, `get_tradition_layer_order`, `_load_tradition_layers_from_yaml`
- `src/vulca/layers/manifest.py` — `write_manifest`, `load_manifest`, `MANIFEST_VERSION = 2`
- `src/vulca/layers/prompt.py` — existing `build_regeneration_prompt` (we are replacing its role with anchored variant, **not deleting it** — `redraw.py`/`split.py` still call it)
- `src/vulca/pipeline/nodes/layer_generate.py` — `LayerGenerateNode` v0.12 implementation. The `_apply_mask` method (lines 127–152) is the post-hoc VLM-mask step that produces bad ink-wash edges. The `_build_prompt` method (lines 154–224) is what we are replacing with anchored prompt builder.
- `src/vulca/pipeline/templates.py:73` — `LAYERED` template, `("plan_layers", "layer_generate", "composite")`
- `src/vulca/cli.py:98` — `--layered` flag is added here. Lines 609–649 handle the `layered=True` branch.
- `src/vulca/cultural/data/traditions/*.yaml` — 11 tradition files plus `_template.yaml`, `default.yaml`, `schema.json`. The 11 are: african_traditional, brand_design, chinese_gongbi, chinese_xieyi, contemporary_art, islamic_geometric, japanese_traditional, photography, south_asian, ui_ux_design, watercolor, western_academic. (Spec says "13 traditions" — that count includes synthetic defaults.)
- `src/vulca/providers/base.py` — provider `generate(...)` signature (engineer should grep for the abstract method to confirm reference_image_b64 kwarg name).
- `src/vulca/cultural/loader.py` — `get_tradition` function (used at `cli.py:599`).

**Spec correction folded in here, not in spec file:** the plan never re-asks the user about the existence of `--layered`. We treat it as augmented-not-new throughout.

---

## Phase A — Foundation (pure functions, fully unit-testable, no provider)

### Task 1: sRGB → LAB conversion (hand-rolled)

**Files:**
- Create: `src/vulca/layers/keying/__init__.py` (empty for now, just makes the package)
- Create: `src/vulca/layers/keying/_lab.py`
- Test: `tests/test_keying_lab.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_keying_lab.py
import numpy as np
from vulca.layers.keying._lab import srgb_to_lab

def test_pure_white_maps_to_L100():
    rgb = np.array([[[255, 255, 255]]], dtype=np.uint8)
    lab = srgb_to_lab(rgb)
    L, a, b = lab[0, 0]
    assert abs(L - 100.0) < 0.5
    assert abs(a) < 0.5
    assert abs(b) < 0.5

def test_pure_black_maps_to_L0():
    rgb = np.array([[[0, 0, 0]]], dtype=np.uint8)
    lab = srgb_to_lab(rgb)
    assert abs(lab[0, 0, 0]) < 0.5

def test_mid_gray_L_around_53():
    rgb = np.array([[[128, 128, 128]]], dtype=np.uint8)
    L = srgb_to_lab(rgb)[0, 0, 0]
    assert 52.0 < L < 55.0

def test_pure_red_chroma():
    rgb = np.array([[[255, 0, 0]]], dtype=np.uint8)
    L, a, b = srgb_to_lab(rgb)[0, 0]
    assert L > 50 and L < 60
    assert a > 50           # red has positive a
    assert b > 30           # and positive b

def test_shape_preserved():
    rgb = np.zeros((4, 5, 3), dtype=np.uint8)
    out = srgb_to_lab(rgb)
    assert out.shape == (4, 5, 3)
    assert out.dtype == np.float32
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_keying_lab.py -v
```
Expected: ImportError / module not found.

- [ ] **Step 3: Implement `_lab.py`**

```python
# src/vulca/layers/keying/_lab.py
"""Hand-rolled sRGB → CIE LAB. No scikit-image dependency.

Reference: https://en.wikipedia.org/wiki/SRGB and CIE LAB D65 white point.
"""
from __future__ import annotations

import numpy as np

# D65 reference white point
_XN, _YN, _ZN = 0.95047, 1.0, 1.08883


def _srgb_to_linear(c: np.ndarray) -> np.ndarray:
    out = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return out


def _xyz_to_lab_f(t: np.ndarray) -> np.ndarray:
    delta = 6.0 / 29.0
    return np.where(
        t > delta ** 3,
        np.cbrt(t),
        t / (3 * delta ** 2) + 4.0 / 29.0,
    )


def srgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Convert H×W×3 uint8 sRGB to H×W×3 float32 CIE LAB (D65).

    L in [0, 100], a/b roughly in [-128, 127].
    """
    if rgb.dtype != np.uint8:
        raise ValueError(f"expected uint8, got {rgb.dtype}")
    if rgb.ndim != 3 or rgb.shape[-1] != 3:
        raise ValueError(f"expected H×W×3, got {rgb.shape}")

    c = rgb.astype(np.float32) / 255.0
    lin = _srgb_to_linear(c)
    R, G, B = lin[..., 0], lin[..., 1], lin[..., 2]

    X = 0.4124564 * R + 0.3575761 * G + 0.1804375 * B
    Y = 0.2126729 * R + 0.7151522 * G + 0.0721750 * B
    Z = 0.0193339 * R + 0.1191920 * G + 0.9503041 * B

    fx = _xyz_to_lab_f(X / _XN)
    fy = _xyz_to_lab_f(Y / _YN)
    fz = _xyz_to_lab_f(Z / _ZN)

    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)

    return np.stack([L, a, b], axis=-1).astype(np.float32)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_keying_lab.py -v
```
Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/keying/__init__.py src/vulca/layers/keying/_lab.py tests/test_keying_lab.py
git commit -m "feat(layers): hand-rolled sRGB to CIE LAB for keying (no scikit-image dep)"
```

---

### Task 2: CanvasSpec + KeyingStrategy protocol

**Files:**
- Modify: `src/vulca/layers/keying/__init__.py`
- Test: `tests/test_keying_types.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_keying_types.py
from vulca.layers.keying import CanvasSpec

def test_canvasspec_from_hex():
    spec = CanvasSpec.from_hex("#ffffff")
    assert spec.color == (255, 255, 255)
    assert spec.tolerance == 0.05
    assert spec.invert is False

def test_canvasspec_from_hex_short():
    spec = CanvasSpec.from_hex("#000")
    assert spec.color == (0, 0, 0)

def test_canvasspec_explicit():
    spec = CanvasSpec(color=(245, 230, 200), tolerance=0.1, invert=False)
    assert spec.color == (245, 230, 200)
    assert spec.tolerance == 0.1
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_keying_types.py -v
```

- [ ] **Step 3: Implement types in `keying/__init__.py`**

```python
# src/vulca/layers/keying/__init__.py
"""Per-tradition alpha extraction from images on canonical canvases."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class CanvasSpec:
    """Canonical empty-canvas description for a tradition."""
    color: tuple[int, int, int]
    tolerance: float = 0.05
    invert: bool = False

    @classmethod
    def from_hex(cls, hex_color: str, *, tolerance: float = 0.05, invert: bool = False) -> "CanvasSpec":
        h = hex_color.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) != 6:
            raise ValueError(f"invalid hex color: {hex_color}")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return cls(color=(r, g, b), tolerance=tolerance, invert=invert)


class KeyingStrategy(Protocol):
    """Returns a float32 alpha map in [0, 1] given an RGB image and canvas."""
    def extract_alpha(self, rgb: np.ndarray, canvas: CanvasSpec) -> np.ndarray: ...
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_keying_types.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/keying/__init__.py tests/test_keying_types.py
git commit -m "feat(layers): CanvasSpec and KeyingStrategy protocol for keying subsystem"
```

---

### Task 3: Luminance keying (Tier 0, the WOW unlock for ink wash)

**Files:**
- Create: `src/vulca/layers/keying/luminance.py`
- Test: `tests/test_keying_luminance.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_keying_luminance.py
import numpy as np
from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.luminance import LuminanceKeying

def _make_image(rgb_tuple, h=4, w=4):
    img = np.full((h, w, 3), rgb_tuple, dtype=np.uint8)
    return img

def test_pure_white_canvas_pure_white_image_alpha_zero():
    canvas = CanvasSpec.from_hex("#ffffff")
    img = _make_image((255, 255, 255))
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert alpha.shape == (4, 4)
    assert alpha.dtype == np.float32
    assert (alpha < 0.01).all()

def test_dense_ink_on_white_alpha_high():
    """Dense ink (L≈30) on white paper → alpha ≈ 0.88."""
    canvas = CanvasSpec.from_hex("#ffffff")
    img = _make_image((30, 30, 30))
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert 0.85 < alpha.mean() < 0.92

def test_pale_ink_alpha_soft():
    """Pale wash (L≈180) → soft alpha ≈ 0.29."""
    canvas = CanvasSpec.from_hex("#ffffff")
    img = _make_image((180, 180, 180))
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert 0.25 < alpha.mean() < 0.33

def test_flying_white_alpha_very_low():
    """飞白 highlights (L≈240) → barely visible ≈ 0.06."""
    canvas = CanvasSpec.from_hex("#ffffff")
    img = _make_image((240, 240, 240))
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert 0.04 < alpha.mean() < 0.08

def test_alpha_clipped_to_unit_interval():
    canvas = CanvasSpec.from_hex("#ffffff")
    img = np.array([[[10, 10, 10], [255, 255, 255]]], dtype=np.uint8)
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert (alpha >= 0).all() and (alpha <= 1).all()

def test_invert_for_dark_canvas():
    """Light content on black canvas: invert=True flips the relation."""
    canvas = CanvasSpec(color=(0, 0, 0), invert=True)
    img = _make_image((255, 255, 255))
    alpha = LuminanceKeying().extract_alpha(img, canvas)
    assert (alpha > 0.95).all()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_keying_luminance.py -v
```

- [ ] **Step 3: Implement luminance strategy**

```python
# src/vulca/layers/keying/luminance.py
"""Tier 0 default: alpha = 1 - (L / L_canvas).

Optimal for traditions where dark content sits on a light canvas
(ink wash, calligraphy, line art, sketch). Ink darkness physically
equals alpha, so flying-white and ink gradients become soft alpha
for free — no halos, no hard edges.
"""
from __future__ import annotations

import numpy as np

from vulca.layers.keying import CanvasSpec


def _luma(rgb: np.ndarray) -> np.ndarray:
    """Rec. 601 luma in [0, 255]."""
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


class LuminanceKeying:
    def extract_alpha(self, rgb: np.ndarray, canvas: CanvasSpec) -> np.ndarray:
        if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[-1] != 3:
            raise ValueError(f"expected H×W×3 uint8, got {rgb.shape} {rgb.dtype}")

        L = _luma(rgb.astype(np.float32))
        L_canvas = float(_luma(np.array(canvas.color, dtype=np.float32)[None, None, :])[0, 0])

        if L_canvas <= 1.0:
            # Black-canvas case: invert relation
            alpha = L / 255.0
        else:
            alpha = 1.0 - (L / L_canvas)

        if canvas.invert:
            alpha = 1.0 - alpha

        return np.clip(alpha, 0.0, 1.0).astype(np.float32)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_keying_luminance.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/keying/luminance.py tests/test_keying_luminance.py
git commit -m "feat(layers): Tier 0 luminance keying — dense ink → high alpha, flying-white → soft alpha"
```

---

### Task 4: Chroma + Delta-E keying (Tier 1)

**Files:**
- Create: `src/vulca/layers/keying/chroma.py`
- Test: `tests/test_keying_chroma.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_keying_chroma.py
import numpy as np
from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.chroma import ChromaKeying, DeltaEKeying

def _img(rgb):
    return np.full((4, 4, 3), rgb, dtype=np.uint8)

def test_chroma_pure_canvas_color_alpha_zero():
    canvas = CanvasSpec(color=(245, 230, 200))     # cooked silk
    alpha = ChromaKeying().extract_alpha(_img((245, 230, 200)), canvas)
    assert (alpha < 0.05).all()

def test_chroma_distant_color_alpha_high():
    canvas = CanvasSpec(color=(245, 230, 200))
    alpha = ChromaKeying().extract_alpha(_img((20, 20, 200)), canvas)   # blue
    assert (alpha > 0.5).all()

def test_chroma_near_color_alpha_partial():
    canvas = CanvasSpec(color=(245, 230, 200))
    alpha = ChromaKeying().extract_alpha(_img((230, 215, 185)), canvas)  # similar
    assert 0.0 < alpha.mean() < 0.4

def test_delta_e_uses_perceptual_distance():
    """Delta-E should differ from naive RGB chroma on perceptually-equal colors."""
    canvas = CanvasSpec(color=(128, 128, 128))
    a_chroma = ChromaKeying().extract_alpha(_img((128, 200, 128)), canvas)
    a_delta_e = DeltaEKeying().extract_alpha(_img((128, 200, 128)), canvas)
    # Both should detect difference, but values may differ
    assert a_chroma.mean() > 0.1
    assert a_delta_e.mean() > 0.1
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_keying_chroma.py -v
```

- [ ] **Step 3: Implement chroma + delta-e**

```python
# src/vulca/layers/keying/chroma.py
"""Tier 1 strategies for colored content on colored canvases.

ChromaKeying: Euclidean distance in linear RGB. Fast, OK for high-contrast.
DeltaEKeying: Perceptual ΔE76 in CIE LAB. ~3× slower, used for low-contrast
              cases (e.g. gongbi color washes on cooked silk).
"""
from __future__ import annotations

import numpy as np

from vulca.layers.keying import CanvasSpec
from vulca.layers.keying._lab import srgb_to_lab


def _smoothstep(lo: float, hi: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - lo) / max(hi - lo, 1e-6), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


class ChromaKeying:
    def extract_alpha(self, rgb: np.ndarray, canvas: CanvasSpec) -> np.ndarray:
        diff = rgb.astype(np.float32) - np.array(canvas.color, dtype=np.float32)
        dist = np.sqrt(np.sum(diff * diff, axis=-1))      # 0..~441
        # tolerance maps to ~5% of max distance
        lo = canvas.tolerance * 441.0
        hi = 441.0 * 0.5                                   # full alpha around mid-distance
        alpha = _smoothstep(lo, hi, dist)
        if canvas.invert:
            alpha = 1.0 - alpha
        return alpha.astype(np.float32)


class DeltaEKeying:
    def extract_alpha(self, rgb: np.ndarray, canvas: CanvasSpec) -> np.ndarray:
        lab = srgb_to_lab(rgb)
        canvas_arr = np.array(canvas.color, dtype=np.uint8).reshape(1, 1, 3)
        canvas_lab = srgb_to_lab(canvas_arr)[0, 0]
        diff = lab - canvas_lab
        delta_e = np.sqrt(np.sum(diff * diff, axis=-1))    # CIE76 ΔE
        lo = canvas.tolerance * 100.0                       # ΔE in roughly [0, 100]
        hi = 50.0
        alpha = _smoothstep(lo, hi, delta_e)
        if canvas.invert:
            alpha = 1.0 - alpha
        return alpha.astype(np.float32)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_keying_chroma.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/keying/chroma.py tests/test_keying_chroma.py
git commit -m "feat(layers): Tier 1 chroma + delta-E keying for colored traditions"
```

---

### Task 5: Strategy registry / dispatch

**Files:**
- Modify: `src/vulca/layers/keying/__init__.py`
- Test: `tests/test_keying_dispatch.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_keying_dispatch.py
import pytest
from vulca.layers.keying import get_keying_strategy
from vulca.layers.keying.luminance import LuminanceKeying
from vulca.layers.keying.chroma import ChromaKeying, DeltaEKeying

def test_get_luminance():
    assert isinstance(get_keying_strategy("luminance"), LuminanceKeying)

def test_get_chroma():
    assert isinstance(get_keying_strategy("chroma"), ChromaKeying)

def test_get_delta_e():
    assert isinstance(get_keying_strategy("delta_e"), DeltaEKeying)

def test_default_when_none():
    assert isinstance(get_keying_strategy(None), LuminanceKeying)
    assert isinstance(get_keying_strategy(""), LuminanceKeying)

def test_unknown_strategy_raises():
    with pytest.raises(ValueError, match="unknown keying strategy"):
        get_keying_strategy("nonsense")

def test_dotted_path_callable_loaded(monkeypatch):
    """Tier 2 escape hatch: 'module.path:fn' imports and uses fn."""
    import sys, types
    mod = types.ModuleType("test_keying_custom_mod")
    class Dummy:
        def extract_alpha(self, rgb, canvas):
            import numpy as np
            return np.zeros(rgb.shape[:2], dtype="float32")
    def factory():
        return Dummy()
    mod.factory = factory
    sys.modules["test_keying_custom_mod"] = mod
    try:
        strat = get_keying_strategy("test_keying_custom_mod:factory")
        assert isinstance(strat, Dummy)
    finally:
        del sys.modules["test_keying_custom_mod"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_keying_dispatch.py -v
```

- [ ] **Step 3: Add `get_keying_strategy` to `keying/__init__.py`**

Append to existing `src/vulca/layers/keying/__init__.py`:

```python
def get_keying_strategy(spec: str | None) -> KeyingStrategy:
    """Resolve a keying strategy by name or 'module.path:callable'."""
    if not spec:
        from vulca.layers.keying.luminance import LuminanceKeying
        return LuminanceKeying()

    if ":" in spec:
        # Tier 2 escape hatch
        module_path, fn_name = spec.split(":", 1)
        import importlib
        mod = importlib.import_module(module_path)
        fn = getattr(mod, fn_name)
        return fn()

    name = spec.lower().strip()
    if name == "luminance":
        from vulca.layers.keying.luminance import LuminanceKeying
        return LuminanceKeying()
    if name == "chroma":
        from vulca.layers.keying.chroma import ChromaKeying
        return ChromaKeying()
    if name in ("delta_e", "deltae"):
        from vulca.layers.keying.chroma import DeltaEKeying
        return DeltaEKeying()
    raise ValueError(f"unknown keying strategy: {spec!r}")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_keying_dispatch.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/keying/__init__.py tests/test_keying_dispatch.py
git commit -m "feat(layers): keying strategy dispatch with Tier 2 dotted-path escape hatch"
```

---

### Task 6: Validation (coverage / position / emptiness)

**Files:**
- Create: `src/vulca/layers/validate.py`
- Test: `tests/test_layered_validate.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_layered_validate.py
import numpy as np
import pytest
from vulca.layers.validate import (
    validate_layer_alpha, ValidationReport, parse_coverage, parse_position,
)

def _alpha_in_region(h, w, top_pct, bottom_pct, left_pct=0.0, right_pct=1.0):
    a = np.zeros((h, w), dtype=np.float32)
    t, b = int(h * top_pct), int(h * bottom_pct)
    l, r = int(w * left_pct), int(w * right_pct)
    a[t:b, l:r] = 0.9
    return a

def test_parse_coverage_range():
    assert parse_coverage("20-30%") == (0.20, 0.30)
    assert parse_coverage("5-10%") == (0.05, 0.10)
    assert parse_coverage("100%") == (1.0, 1.0)

def test_parse_position_upper_30():
    region = parse_position("upper 30%")
    assert region["top"] == 0.0 and region["bottom"] == 0.30

def test_parse_position_lower_30():
    region = parse_position("lower 30%")
    assert region["top"] == 0.70 and region["bottom"] == 1.0

def test_empty_layer_is_failure():
    alpha = np.zeros((100, 100), dtype=np.float32)
    rep = validate_layer_alpha(alpha, position="upper 30%", coverage="20-30%")
    assert not rep.ok
    assert "empty_layer" in [w.kind for w in rep.warnings]

def test_coverage_in_range_no_warning():
    alpha = _alpha_in_region(100, 100, 0.0, 0.25)   # 25% coverage
    rep = validate_layer_alpha(alpha, position="upper 30%", coverage="20-30%")
    assert rep.ok
    assert "coverage_drift" not in [w.kind for w in rep.warnings]

def test_coverage_too_large_warns():
    alpha = _alpha_in_region(100, 100, 0.0, 0.80)   # 80% coverage
    rep = validate_layer_alpha(alpha, position="upper 30%", coverage="20-30%")
    assert "coverage_drift" in [w.kind for w in rep.warnings]

def test_position_drift_warns():
    """Layer says upper 30% but pixels are in lower 30%."""
    alpha = _alpha_in_region(100, 100, 0.70, 1.0)
    rep = validate_layer_alpha(alpha, position="upper 30%", coverage="20-30%")
    assert "position_drift" in [w.kind for w in rep.warnings]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_layered_validate.py -v
```

- [ ] **Step 3: Implement validation**

```python
# src/vulca/layers/validate.py
"""Per-layer post-generation validation: spatial sanity checks.

Defense layer 2 of the plan/generation consistency strategy. Cheap, offline,
no provider calls. Reports drifts as warnings; only emptiness is hard-failure.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np


@dataclass
class ValidationWarning:
    kind: str                      # "empty_layer" | "coverage_drift" | "position_drift"
    message: str
    detail: dict = field(default_factory=dict)


@dataclass
class ValidationReport:
    ok: bool
    warnings: list[ValidationWarning] = field(default_factory=list)
    coverage_actual: float = 0.0
    position_iou: float = 0.0


def parse_coverage(text: str) -> tuple[float, float]:
    """'20-30%' → (0.20, 0.30); '100%' → (1.0, 1.0); fallback (0, 1)."""
    if not text:
        return (0.0, 1.0)
    m = re.match(r"\s*(\d+)\s*-\s*(\d+)\s*%", text)
    if m:
        return (int(m.group(1)) / 100.0, int(m.group(2)) / 100.0)
    m = re.match(r"\s*(\d+)\s*%", text)
    if m:
        v = int(m.group(1)) / 100.0
        return (v, v)
    return (0.0, 1.0)


def parse_position(text: str) -> dict[str, float]:
    """'upper 30%' → {top:0, bottom:0.3}; 'lower 30%' → {top:0.7, bottom:1};
    'center' → {top:0.25, bottom:0.75}; default → full canvas."""
    if not text:
        return {"top": 0.0, "bottom": 1.0, "left": 0.0, "right": 1.0}
    t = text.lower()
    m = re.search(r"upper\s+(\d+)\s*%", t)
    if m:
        return {"top": 0.0, "bottom": int(m.group(1)) / 100.0, "left": 0.0, "right": 1.0}
    m = re.search(r"lower\s+(\d+)\s*%", t)
    if m:
        return {"top": 1.0 - int(m.group(1)) / 100.0, "bottom": 1.0, "left": 0.0, "right": 1.0}
    if "center" in t:
        return {"top": 0.25, "bottom": 0.75, "left": 0.25, "right": 0.75}
    if "corner" in t:
        return {"top": 0.0, "bottom": 0.30, "left": 0.0, "right": 0.30}
    return {"top": 0.0, "bottom": 1.0, "left": 0.0, "right": 1.0}


def _alpha_bbox_iou(alpha: np.ndarray, region: dict[str, float], threshold: float = 0.05) -> float:
    h, w = alpha.shape
    mask = alpha > threshold
    if not mask.any():
        return 0.0

    rows = mask.any(axis=1)
    cols = mask.any(axis=0)
    y0, y1 = int(np.argmax(rows)), int(len(rows) - np.argmax(rows[::-1]))
    x0, x1 = int(np.argmax(cols)), int(len(cols) - np.argmax(cols[::-1]))

    rt, rb = int(region["top"] * h), int(region["bottom"] * h)
    rl, rr = int(region["left"] * w), int(region["right"] * w)

    ix0, iy0 = max(x0, rl), max(y0, rt)
    ix1, iy1 = min(x1, rr), min(y1, rb)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    a1 = (x1 - x0) * (y1 - y0)
    a2 = (rr - rl) * (rb - rt)
    return inter / max(a1 + a2 - inter, 1)


def validate_layer_alpha(
    alpha: np.ndarray,
    *,
    position: str = "",
    coverage: str = "",
    alpha_threshold: float = 0.05,
    position_iou_threshold: float = 0.30,
    coverage_factor: float = 2.0,
) -> ValidationReport:
    rep = ValidationReport(ok=True)
    h, w = alpha.shape
    canvas_area = h * w

    nonzero = (alpha > alpha_threshold).sum()
    rep.coverage_actual = float(nonzero) / canvas_area

    # Emptiness — hard failure
    if nonzero < canvas_area * 0.001:
        rep.ok = False
        rep.warnings.append(ValidationWarning(
            "empty_layer",
            "alpha is essentially empty (< 0.1% of canvas)",
            {"nonzero": int(nonzero), "canvas_area": canvas_area},
        ))
        return rep

    # Coverage check
    lo, hi = parse_coverage(coverage)
    lo_tol, hi_tol = lo / coverage_factor, hi * coverage_factor
    if rep.coverage_actual < lo_tol or rep.coverage_actual > hi_tol:
        rep.warnings.append(ValidationWarning(
            "coverage_drift",
            f"coverage {rep.coverage_actual:.0%} outside tolerated [{lo_tol:.0%}, {hi_tol:.0%}]",
            {"actual": rep.coverage_actual, "expected": coverage},
        ))

    # Position check
    region = parse_position(position)
    rep.position_iou = _alpha_bbox_iou(alpha, region, alpha_threshold)
    if rep.position_iou < position_iou_threshold:
        rep.warnings.append(ValidationWarning(
            "position_drift",
            f"alpha bbox IoU with expected region = {rep.position_iou:.2f}",
            {"iou": rep.position_iou, "expected": position},
        ))

    return rep
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_layered_validate.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/validate.py tests/test_layered_validate.py
git commit -m "feat(layers): per-layer alpha validation (coverage / position / emptiness)"
```

---

## Phase B — Tradition config

### Task 7: Add new YAML fields to chinese_xieyi (the hero case)

**Files:**
- Modify: `src/vulca/cultural/data/traditions/chinese_xieyi.yaml`
- Test: `tests/test_tradition_layerability.py`

- [ ] **Step 1: Read the existing file** to find the right insertion point.

```bash
cat src/vulca/cultural/data/traditions/chinese_xieyi.yaml | head -40
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_tradition_layerability.py
from vulca.cultural.loader import get_tradition

def test_chinese_xieyi_has_layerability_fields():
    t = get_tradition("chinese_xieyi")
    raw = t.raw_data if hasattr(t, "raw_data") else t  # adapt to loader return type
    # The loader may expose YAML as dict or attrs — engineer should adapt this assertion
    # to whatever the loader actually returns. The test should fail clearly if missing.
    assert "layerability" in str(raw) or hasattr(t, "layerability")
```

> Engineer note: read `src/vulca/cultural/loader.py` first to see how `get_tradition` returns data; this test asserts the field round-trips through the loader. If the loader currently strips unknown YAML keys, Task 8 must add explicit field handling.

- [ ] **Step 3: Run test to verify it fails**

- [ ] **Step 4: Append the 5 fields to `chinese_xieyi.yaml`**

```yaml
# Layered generation configuration (v0.13)
layerability: native
canvas_color: "#ffffff"
canvas_description: "pure white rice paper (生宣纸), no texture, no border"
key_strategy: luminance
style_keywords: "水墨写意, 淡墨为主, 飞白笔触, 大量留白, 宣纸质感, 不画任何彩色, ink wash, monochrome, traditional Chinese painting"
```

- [ ] **Step 5: Run test, expect it to still fail if loader strips the fields. Continue to Task 8.**

- [ ] **Step 6: Commit (intermediate, fields added but not yet loaded)**

```bash
git add src/vulca/cultural/data/traditions/chinese_xieyi.yaml tests/test_tradition_layerability.py
git commit -m "feat(traditions): add layerability fields to chinese_xieyi (loader wiring next)"
```

---

### Task 8: Tradition loader exposes new fields

**Files:**
- Read: `src/vulca/cultural/loader.py`
- Modify: `src/vulca/cultural/loader.py`
- Modify: `tests/test_tradition_layerability.py` (tighten assertions)

- [ ] **Step 1: Read the loader to understand its data shape**

```bash
wc -l src/vulca/cultural/loader.py
```

Read the file. Identify the dataclass / dict that `get_tradition` returns. The plan calls it `Tradition`; whatever it actually is, add five public attributes (or dict keys) for the new fields with sensible defaults.

- [ ] **Step 2: Strengthen the failing test**

```python
# tests/test_tradition_layerability.py (replace contents)
from vulca.cultural.loader import get_tradition

def test_chinese_xieyi_layerability_native():
    t = get_tradition("chinese_xieyi")
    assert getattr(t, "layerability", None) == "native"
    assert getattr(t, "canvas_color", None) == "#ffffff"
    assert getattr(t, "key_strategy", None) == "luminance"
    assert "宣纸" in (getattr(t, "canvas_description", "") or "")
    assert "水墨" in (getattr(t, "style_keywords", "") or "")

def test_unknown_tradition_defaults_to_split():
    t = get_tradition("default")
    # Default tradition may or may not be set up; either it's split or absent.
    if t is not None:
        assert getattr(t, "layerability", "split") in ("split", "native", "discouraged")
```

- [ ] **Step 3: Run test, verify it fails on the new attribute checks**

- [ ] **Step 4: Modify the loader**

Add the five fields (with defaults: `layerability="split"`, `canvas_color="#ffffff"`, `canvas_description=""`, `key_strategy="luminance"`, `style_keywords=""`) to whatever data structure `get_tradition` returns. If it's a dataclass, add fields. If it's a dict, ensure the YAML keys flow through unchanged.

> Engineer note: keep edits minimal — add the five fields, do not refactor the loader.

- [ ] **Step 5: Run test and confirm pass**

```bash
pytest tests/test_tradition_layerability.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/vulca/cultural/loader.py tests/test_tradition_layerability.py
git commit -m "feat(cultural): tradition loader exposes layerability, canvas_color, key_strategy, canvas_description, style_keywords"
```

---

### Task 9: Roll out fields to remaining 10 traditions

**Files:**
- Modify (10 files): `src/vulca/cultural/data/traditions/{african_traditional,brand_design,chinese_gongbi,contemporary_art,islamic_geometric,japanese_traditional,photography,south_asian,ui_ux_design,watercolor,western_academic}.yaml`

Use this assignment table:

| Tradition | layerability | canvas_color | key_strategy | canvas_description (EN) | style_keywords seed |
|---|---|---|---|---|---|
| chinese_gongbi | native | #f5e6c8 | delta_e | cooked silk with subtle warm tone (熟绢) | 工笔, 白描勾线, 分染罩染, 细致, gongbi style, fine outline, refined |
| japanese_traditional | native | #f5ecd8 | delta_e | washi paper, slight warm tone | ukiyo-e, woodblock print style, flat color blocks, line art |
| watercolor | native | #ffffff | luminance | cold-press white watercolor paper | watercolor wash, transparent pigments, soft edges, paper texture |
| islamic_geometric | native | #ffffff | luminance | flat white background, no texture | geometric pattern, symmetry, intricate ornament, no shading |
| brand_design | native | #ffffff | luminance | flat white digital canvas | clean vector style, brand design, flat illustration, minimal |
| ui_ux_design | native | #ffffff | luminance | flat white digital canvas | UI design, flat material, clean interface, vector |
| contemporary_art | split | #ffffff | luminance | white canvas | contemporary art (best-effort layering) |
| south_asian | native | #f5e6c8 | delta_e | warm beige canvas | Indian miniature style, refined detail, mineral pigments |
| african_traditional | split | #ffffff | luminance | white canvas | African traditional art (best-effort) |
| western_academic | discouraged | null | null |  |  |
| photography | discouraged | null | null |  |  |

- [ ] **Step 1: Add the 5-field block to each YAML file** (template):

```yaml
# Layered generation configuration (v0.13)
layerability: <native|split|discouraged>
canvas_color: "<#hex or null>"
canvas_description: "<short EN sentence>"
key_strategy: <luminance|delta_e|null>
style_keywords: "<comma-separated, trad-specific>"
```

For `discouraged` traditions write `null` for `canvas_color` / `key_strategy` and leave `style_keywords: ""`.

- [ ] **Step 2: Add a parameterised test**

```python
# tests/test_tradition_layerability.py — append
import pytest

@pytest.mark.parametrize("name,expected_layerability", [
    ("chinese_xieyi", "native"),
    ("chinese_gongbi", "native"),
    ("japanese_traditional", "native"),
    ("watercolor", "native"),
    ("islamic_geometric", "native"),
    ("brand_design", "native"),
    ("ui_ux_design", "native"),
    ("contemporary_art", "split"),
    ("south_asian", "native"),
    ("african_traditional", "split"),
    ("photography", "discouraged"),
    ("western_academic", "discouraged"),
])
def test_all_traditions_have_layerability(name, expected_layerability):
    from vulca.cultural.loader import get_tradition
    t = get_tradition(name)
    assert t is not None, f"tradition {name} missing"
    assert getattr(t, "layerability", None) == expected_layerability
```

- [ ] **Step 3: Run test to verify it passes**

```bash
pytest tests/test_tradition_layerability.py -v
```

- [ ] **Step 4: Commit**

```bash
git add src/vulca/cultural/data/traditions/*.yaml tests/test_tradition_layerability.py
git commit -m "feat(traditions): roll layerability config to remaining 10 traditions"
```

---

## Phase C — Anchored prompt builder

### Task 10: Anchored layered prompt

**Files:**
- Create: `src/vulca/layers/layered_prompt.py`
- Test: `tests/test_layered_prompt.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_layered_prompt.py
from vulca.layers.types import LayerInfo
from vulca.layers.layered_prompt import build_anchored_layer_prompt, TraditionAnchor

def _xieyi_anchor():
    return TraditionAnchor(
        canvas_color_hex="#ffffff",
        canvas_description="pure white rice paper (生宣纸), no texture, no border",
        style_keywords="水墨写意, 淡墨为主, 飞白笔触",
    )

def _layer(name, role, position="upper 30%", coverage="20-30%"):
    return LayerInfo(
        name=name,
        description=f"{role} description",
        z_index=1,
        tradition_role=role,
        regeneration_prompt=f"painted {role}",
    )

def test_prompt_contains_canvas_anchor():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=["中景山石", "题款"],
    )
    assert "pure white rice paper" in p
    assert "#ffffff" in p

def test_prompt_contains_negative_list_from_siblings():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=["中景山石", "题款"],
    )
    assert "中景山石" in p
    assert "题款" in p
    assert ("Do NOT" in p) or ("do not" in p.lower())

def test_prompt_does_not_negate_self():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=["远景淡墨", "中景山石"],   # self should be filtered
    )
    # The "do not draw" line should not contain own role
    do_not_section = p.split("[CONTENT ANCHOR")[1] if "[CONTENT ANCHOR" in p else p
    assert do_not_section.count("远景淡墨") <= 1   # only the positive mention

def test_prompt_includes_style_keywords():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=[],
    )
    assert "飞白" in p or "水墨" in p

def test_prompt_has_spatial_anchor():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨", position="upper 30%", coverage="20-30%"),
        anchor=_xieyi_anchor(),
        sibling_roles=[],
        position="upper 30%",
        coverage="20-30%",
    )
    assert "upper 30%" in p
    assert "20-30%" in p

def test_prompt_passthrough_user_intent():
    p = build_anchored_layer_prompt(
        _layer("远山", "远景淡墨"),
        anchor=_xieyi_anchor(),
        sibling_roles=[],
    )
    assert "painted 远景淡墨" in p
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Implement the prompt builder**

```python
# src/vulca/layers/layered_prompt.py
"""Anchored layer prompt builder — Defense layer 1 of consistency strategy.

Wraps the plan's regeneration_prompt in four mandatory anchor blocks:
canvas, content (with negative list), spatial, style. Pure function.
"""
from __future__ import annotations

from dataclasses import dataclass

from vulca.layers.types import LayerInfo


@dataclass(frozen=True)
class TraditionAnchor:
    canvas_color_hex: str
    canvas_description: str
    style_keywords: str


def build_anchored_layer_prompt(
    layer: LayerInfo,
    *,
    anchor: TraditionAnchor,
    sibling_roles: list[str],
    position: str = "",
    coverage: str = "",
) -> str:
    """Build a fully anchored prompt for one layer of a layered artwork.

    sibling_roles is the full list of layer roles in the plan (this layer's
    role is filtered out automatically when building the negative list).
    """
    own_role = layer.tradition_role or layer.name
    others = [r for r in sibling_roles if r and r != own_role]
    others_text = ", ".join(others) if others else "(none)"

    pos = position or "wherever the user intent specifies"
    cov = coverage or "as the user intent specifies"

    user_intent = layer.regeneration_prompt or layer.description or own_role

    blocks = [
        "[CANVAS ANCHOR]",
        f"The image MUST be drawn on {anchor.canvas_description}.",
        f"The background MUST be the pure canvas color {anchor.canvas_color_hex},",
        "with absolutely no other elements, textures, shading, or borders on the background.",
        "",
        "[CONTENT ANCHOR — exclusivity]",
        f"The ONLY element in this image is: {own_role} — {layer.description}.",
        f"Do NOT draw any of: {others_text}. Draw ONLY the {own_role}.",
        "",
        "[SPATIAL ANCHOR]",
        f"The {own_role} MUST occupy {pos}, covering approximately {cov} of the canvas area.",
        "Do NOT extend beyond this region.",
        "",
        "[STYLE ANCHOR]",
        anchor.style_keywords,
        "",
        "[USER INTENT]",
        user_intent,
    ]
    return "\n".join(blocks)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_layered_prompt.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/layered_prompt.py tests/test_layered_prompt.py
git commit -m "feat(layers): anchored layer prompt builder (canvas/content/spatial/style)"
```

---

## Phase D — Layered generation library

### Task 11: Result dataclasses

**Files:**
- Create: `src/vulca/layers/layered_generate.py` (this file grows over Tasks 11–14)
- Test: `tests/test_layered_result.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_layered_result.py
from vulca.layers.types import LayerInfo
from vulca.layers.layered_generate import (
    LayerOutcome, LayerFailure, LayeredResult,
)

def _info(name, content_type="subject", role=""):
    return LayerInfo(name=name, description="", z_index=0, content_type=content_type, tradition_role=role)

def test_outcome_ok():
    o = LayerOutcome(ok=True, info=_info("远山", role="远景淡墨"), rgba_path="/tmp/x.png")
    assert o.ok and o.rgba_path.endswith(".png")

def test_failure_carries_reason():
    f = LayerFailure(layer_id="layer_x", role="远景淡墨", reason="provider_timeout", attempts=3)
    assert f.reason == "provider_timeout" and f.attempts == 3

def test_layered_result_is_complete():
    res = LayeredResult(
        layers=[LayerOutcome(ok=True, info=_info("a", role="bg"), rgba_path="/a.png"),
                LayerOutcome(ok=True, info=_info("b", content_type="subject", role="m"), rgba_path="/b.png")],
        failed=[],
    )
    assert res.is_complete and res.is_usable

def test_layered_result_partial_usable():
    res = LayeredResult(
        layers=[
            LayerOutcome(ok=True, info=_info("bg", content_type="background", role="bg"), rgba_path="/bg.png"),
            LayerOutcome(ok=True, info=_info("subj", content_type="subject", role="m"), rgba_path="/s.png"),
        ],
        failed=[LayerFailure(layer_id="x", role="题款", reason="r", attempts=1)],
    )
    assert not res.is_complete
    assert res.is_usable

def test_layered_result_unusable_no_subject():
    res = LayeredResult(
        layers=[LayerOutcome(ok=True, info=_info("bg", content_type="background", role="bg"), rgba_path="/bg.png")],
        failed=[LayerFailure("x", "subj", "r", 1)],
    )
    assert not res.is_usable
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Create `layered_generate.py` with the dataclasses**

```python
# src/vulca/layers/layered_generate.py
"""A-path layered generation library.

Pure orchestration: plan → concurrent provider calls → keying → validate.
Decoupled from the pipeline so it can be called from CLI, MCP, SDK, or tests.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from vulca.layers.types import LayerInfo
from vulca.layers.validate import ValidationReport


@dataclass
class LayerOutcome:
    ok: bool
    info: LayerInfo
    rgba_path: str = ""
    cache_hit: bool = False
    attempts: int = 1
    validation: ValidationReport | None = None


@dataclass
class LayerFailure:
    layer_id: str
    role: str
    reason: str
    attempts: int = 1


@dataclass
class LayeredResult:
    layers: list[LayerOutcome] = field(default_factory=list)
    failed: list[LayerFailure] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return not self.failed

    @property
    def is_usable(self) -> bool:
        if not self.layers:
            return False
        has_subject = any(
            l.info.content_type in ("subject", "line_art", "color_block", "color_wash", "detail")
            for l in self.layers
        )
        return has_subject
```

- [ ] **Step 4: Run test, confirm pass**

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/layered_generate.py tests/test_layered_result.py
git commit -m "feat(layers): LayerOutcome / LayerFailure / LayeredResult dataclasses"
```

---

### Task 12: Per-artifact sidecar cache

**Files:**
- Create: `src/vulca/layers/layered_cache.py`
- Test: `tests/test_layered_cache.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_layered_cache.py
import os
import tempfile
import numpy as np
from PIL import Image

from vulca.layers.layered_cache import LayerCache, build_cache_key

def _png_bytes():
    img = Image.new("RGBA", (8, 8), (10, 20, 30, 255))
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def test_cache_key_stable():
    a = build_cache_key(provider_id="gemini", model_id="m1", prompt="hi", canvas_color="#ffffff", canvas_tolerance=0.05, seed=0, schema_version="0.13")
    b = build_cache_key(provider_id="gemini", model_id="m1", prompt="hi", canvas_color="#ffffff", canvas_tolerance=0.05, seed=0, schema_version="0.13")
    assert a == b

def test_cache_key_changes_on_prompt():
    a = build_cache_key(provider_id="g", model_id="m", prompt="x", canvas_color="#fff", canvas_tolerance=0.05, seed=0, schema_version="0.13")
    b = build_cache_key(provider_id="g", model_id="m", prompt="y", canvas_color="#fff", canvas_tolerance=0.05, seed=0, schema_version="0.13")
    assert a != b

def test_cache_roundtrip(tmp_path):
    cache = LayerCache(tmp_path / "art")
    key = "k1"
    assert cache.get(key) is None
    cache.put(key, _png_bytes())
    data = cache.get(key)
    assert data is not None and data.startswith(b"\x89PNG")

def test_cache_disabled():
    cache = LayerCache(None, enabled=False)
    cache.put("k", _png_bytes())
    assert cache.get("k") is None
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Implement cache**

```python
# src/vulca/layers/layered_cache.py
"""Per-artifact sidecar cache for layered generation.

Cache lives at <artifact_dir>/.layered_cache/<key>.png. No global cache,
no LRU, no eviction. Deletes when the artifact directory is deleted.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional


def build_cache_key(
    *,
    provider_id: str,
    model_id: str,
    prompt: str,
    canvas_color: str,
    canvas_tolerance: float,
    seed: int = 0,
    schema_version: str = "0.13",
) -> str:
    h = hashlib.sha256()
    parts = [provider_id, model_id, prompt, canvas_color, f"{canvas_tolerance:.4f}", str(seed), schema_version]
    h.update("\x00".join(parts).encode("utf-8"))
    return h.hexdigest()


class LayerCache:
    def __init__(self, artifact_dir: Path | str | None, *, enabled: bool = True):
        self.enabled = enabled and artifact_dir is not None
        self.dir = Path(artifact_dir) / ".layered_cache" if artifact_dir else None
        if self.enabled:
            self.dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[bytes]:
        if not self.enabled:
            return None
        p = self.dir / f"{key}.png"
        if p.exists():
            return p.read_bytes()
        return None

    def put(self, key: str, data: bytes) -> None:
        if not self.enabled:
            return
        (self.dir / f"{key}.png").write_bytes(data)
```

- [ ] **Step 4: Run test, confirm pass**

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/layered_cache.py tests/test_layered_cache.py
git commit -m "feat(layers): per-artifact sidecar cache for layered generation"
```

---

### Task 13: Single-layer generation function (with mock provider)

**Files:**
- Modify: `src/vulca/layers/layered_generate.py`
- Test: `tests/test_layered_generate_one.py`

This task wires keying + validation + cache + prompt anchoring together for one layer using a fake provider, no real network.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_layered_generate_one.py
import asyncio
import io
import numpy as np
from PIL import Image
from pathlib import Path

from vulca.layers.types import LayerInfo
from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.luminance import LuminanceKeying
from vulca.layers.layered_prompt import TraditionAnchor
from vulca.layers.layered_generate import generate_one_layer, LayerOutcome
from vulca.layers.layered_cache import LayerCache


class _FakeProvider:
    def __init__(self):
        self.calls = 0
        self.id = "fake"
        self.model = "fake-1"

    async def generate(self, *, prompt, raw_prompt=False, reference_image_b64=None, **kw):
        self.calls += 1
        # Make a fake "ink wash" image: dark gray center on white
        img = Image.new("RGB", (32, 32), (255, 255, 255))
        for y in range(8, 24):
            for x in range(8, 24):
                img.putpixel((x, y), (40, 40, 40))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        import base64
        return type("R", (), {"image_b64": base64.b64encode(buf.getvalue()).decode()})()


def _layer():
    return LayerInfo(
        name="远山",
        description="distant ink mountains",
        z_index=1,
        content_type="subject",
        tradition_role="远景淡墨",
        regeneration_prompt="distant misty mountains in light ink",
    )

def _anchor():
    return TraditionAnchor(
        canvas_color_hex="#ffffff",
        canvas_description="pure white rice paper",
        style_keywords="水墨, 飞白",
    )

def test_generate_one_layer_produces_rgba(tmp_path):
    provider = _FakeProvider()
    cache = LayerCache(tmp_path, enabled=True)
    out = asyncio.run(generate_one_layer(
        layer=_layer(),
        anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        keying=LuminanceKeying(),
        provider=provider,
        sibling_roles=["中景", "题款"],
        output_dir=str(tmp_path),
        position="center",
        coverage="20-30%",
        cache=cache,
    ))
    assert isinstance(out, LayerOutcome)
    assert out.ok
    assert Path(out.rgba_path).exists()
    img = Image.open(out.rgba_path)
    assert img.mode == "RGBA"
    a = np.array(img)[:, :, 3]
    # Center should be opaque, edges transparent
    assert a[16, 16] > 200
    assert a[0, 0] < 30

def test_cache_hit_skips_provider(tmp_path):
    provider = _FakeProvider()
    cache = LayerCache(tmp_path, enabled=True)
    layer = _layer()
    # Run once to populate cache
    asyncio.run(generate_one_layer(
        layer=layer, anchor=_anchor(), canvas=CanvasSpec.from_hex("#ffffff"),
        keying=LuminanceKeying(), provider=provider, sibling_roles=[],
        output_dir=str(tmp_path), position="center", coverage="20-30%", cache=cache,
    ))
    assert provider.calls == 1
    # Run again, cache should hit
    out = asyncio.run(generate_one_layer(
        layer=layer, anchor=_anchor(), canvas=CanvasSpec.from_hex("#ffffff"),
        keying=LuminanceKeying(), provider=provider, sibling_roles=[],
        output_dir=str(tmp_path), position="center", coverage="20-30%", cache=cache,
    ))
    assert provider.calls == 1
    assert out.cache_hit
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Implement `generate_one_layer`** in `layered_generate.py`

Append to `src/vulca/layers/layered_generate.py`:

```python
import base64
import io
import logging
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from vulca.layers.keying import CanvasSpec, KeyingStrategy
from vulca.layers.layered_cache import LayerCache, build_cache_key
from vulca.layers.layered_prompt import TraditionAnchor, build_anchored_layer_prompt
from vulca.layers.validate import validate_layer_alpha

logger = logging.getLogger("vulca.layers.layered_generate")

SCHEMA_VERSION = "0.13"


def _provider_id_of(provider) -> str:
    return getattr(provider, "id", None) or provider.__class__.__name__


def _provider_model_of(provider) -> str:
    return getattr(provider, "model", None) or "unknown"


async def _call_provider(provider, prompt: str) -> bytes:
    """Call provider and return raw image bytes (PNG)."""
    result = await provider.generate(prompt=prompt, raw_prompt=True)
    b64 = result.image_b64 if hasattr(result, "image_b64") else result
    return base64.b64decode(b64)


def _apply_alpha(rgb_bytes: bytes, alpha: np.ndarray) -> Image.Image:
    img = Image.open(io.BytesIO(rgb_bytes)).convert("RGB")
    rgb = np.array(img)
    if rgb.shape[:2] != alpha.shape:
        # Resize alpha to match generated image
        a_img = Image.fromarray((alpha * 255).astype(np.uint8))
        a_img = a_img.resize((rgb.shape[1], rgb.shape[0]), Image.BILINEAR)
        alpha = np.array(a_img).astype(np.float32) / 255.0
    rgba = np.dstack([rgb, (alpha * 255).astype(np.uint8)])
    return Image.fromarray(rgba, mode="RGBA")


async def generate_one_layer(
    *,
    layer: LayerInfo,
    anchor: TraditionAnchor,
    canvas: CanvasSpec,
    keying: KeyingStrategy,
    provider,
    sibling_roles: list[str],
    output_dir: str,
    position: str = "",
    coverage: str = "",
    cache: LayerCache | None = None,
) -> LayerOutcome:
    prompt = build_anchored_layer_prompt(
        layer, anchor=anchor, sibling_roles=sibling_roles,
        position=position, coverage=coverage,
    )

    cache_key = build_cache_key(
        provider_id=_provider_id_of(provider),
        model_id=_provider_model_of(provider),
        prompt=prompt,
        canvas_color="#%02x%02x%02x" % canvas.color,
        canvas_tolerance=canvas.tolerance,
        schema_version=SCHEMA_VERSION,
    )

    out_path = str(Path(output_dir) / f"{layer.name}.png")
    cache_hit = False

    if cache is not None:
        cached = cache.get(cache_key)
        if cached:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            Path(out_path).write_bytes(cached)
            cache_hit = True

    if not cache_hit:
        try:
            rgb_bytes = await _call_provider(provider, prompt)
        except Exception as exc:
            logger.warning("provider failed for layer %s: %s", layer.name, exc)
            return LayerOutcome(ok=False, info=layer, rgba_path="", attempts=1)

        rgb = np.array(Image.open(io.BytesIO(rgb_bytes)).convert("RGB"))
        alpha = keying.extract_alpha(rgb, canvas)
        rgba_img = _apply_alpha(rgb_bytes, alpha)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        rgba_img.save(out_path)
        if cache is not None:
            buf = io.BytesIO()
            rgba_img.save(buf, format="PNG")
            cache.put(cache_key, buf.getvalue())

    # Validate from saved RGBA
    rgba = np.array(Image.open(out_path))
    alpha_only = rgba[:, :, 3].astype(np.float32) / 255.0
    report = validate_layer_alpha(alpha_only, position=position, coverage=coverage)

    if not report.ok:
        return LayerOutcome(
            ok=False, info=layer, rgba_path="", attempts=1,
            validation=report, cache_hit=cache_hit,
        )

    return LayerOutcome(
        ok=True, info=layer, rgba_path=out_path,
        attempts=1, validation=report, cache_hit=cache_hit,
    )
```

- [ ] **Step 4: Run test, confirm pass**

```bash
pytest tests/test_layered_generate_one.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/layered_generate.py tests/test_layered_generate_one.py
git commit -m "feat(layers): generate_one_layer wires anchored prompt + keying + cache + validate"
```

---

### Task 14: Concurrent orchestration

**Files:**
- Modify: `src/vulca/layers/layered_generate.py` (append `layered_generate`)
- Test: `tests/test_layered_generate_orchestration.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_layered_generate_orchestration.py
import asyncio
import io
import base64
from PIL import Image
from pathlib import Path

from vulca.layers.types import LayerInfo
from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.luminance import LuminanceKeying
from vulca.layers.layered_prompt import TraditionAnchor
from vulca.layers.layered_generate import layered_generate, LayeredResult
from vulca.layers.layered_cache import LayerCache


class _CountingProvider:
    def __init__(self, fail_for_role=None):
        self.calls = 0
        self.id = "fake"
        self.model = "fake-1"
        self.fail_for_role = fail_for_role

    async def generate(self, *, prompt, raw_prompt=False, **kw):
        self.calls += 1
        if self.fail_for_role and self.fail_for_role in prompt:
            raise RuntimeError("simulated failure")
        img = Image.new("RGB", (32, 32), (255, 255, 255))
        for y in range(8, 24):
            for x in range(8, 24):
                img.putpixel((x, y), (40, 40, 40))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return type("R", (), {"image_b64": base64.b64encode(buf.getvalue()).decode()})()


def _plan():
    return [
        LayerInfo(name="bg", description="paper", z_index=0, content_type="background", tradition_role="纸"),
        LayerInfo(name="far", description="far mountains", z_index=1, content_type="subject", tradition_role="远景淡墨", regeneration_prompt="distant mountains"),
        LayerInfo(name="mid", description="mid scenery", z_index=2, content_type="subject", tradition_role="中景", regeneration_prompt="mid scenery"),
    ]

def _anchor():
    return TraditionAnchor("#ffffff", "white rice paper", "水墨")

def test_layered_generate_all_succeed(tmp_path):
    provider = _CountingProvider()
    res = asyncio.run(layered_generate(
        plan=_plan(),
        tradition_anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        key_strategy_name="luminance",
        provider=provider,
        output_dir=str(tmp_path),
        positions={"bg": "full canvas", "far": "upper 30%", "mid": "center"},
        coverages={"bg": "100%", "far": "20-30%", "mid": "20-30%"},
        parallelism=2,
    ))
    assert isinstance(res, LayeredResult)
    assert res.is_complete
    assert len(res.layers) == 3
    assert provider.calls == 3

def test_layered_generate_partial_failure(tmp_path):
    provider = _CountingProvider(fail_for_role="中景")
    res = asyncio.run(layered_generate(
        plan=_plan(),
        tradition_anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        key_strategy_name="luminance",
        provider=provider,
        output_dir=str(tmp_path),
        positions={"bg": "full canvas", "far": "upper 30%", "mid": "center"},
        coverages={"bg": "100%", "far": "20-30%", "mid": "20-30%"},
        parallelism=2,
    ))
    assert not res.is_complete
    assert res.is_usable
    assert len(res.failed) == 1
    assert res.failed[0].role == "中景"

def test_cache_hit_on_second_run(tmp_path):
    provider = _CountingProvider()
    args = dict(
        plan=_plan(),
        tradition_anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        key_strategy_name="luminance",
        provider=provider,
        output_dir=str(tmp_path),
        positions={"bg": "full canvas", "far": "upper 30%", "mid": "center"},
        coverages={"bg": "100%", "far": "20-30%", "mid": "20-30%"},
        parallelism=2,
        cache_enabled=True,
    )
    asyncio.run(layered_generate(**args))
    assert provider.calls == 3
    asyncio.run(layered_generate(**args))
    assert provider.calls == 3   # all cached
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Implement `layered_generate` orchestration**

Append to `src/vulca/layers/layered_generate.py`:

```python
import asyncio

from vulca.layers.keying import get_keying_strategy


async def layered_generate(
    *,
    plan: list[LayerInfo],
    tradition_anchor: TraditionAnchor,
    canvas: CanvasSpec,
    key_strategy_name: str,
    provider,
    output_dir: str,
    positions: dict[str, str] | None = None,
    coverages: dict[str, str] | None = None,
    parallelism: int = 4,
    cache_enabled: bool = True,
) -> LayeredResult:
    """Concurrently generate every layer in the plan, key, validate, and assemble.

    `positions` / `coverages` are dicts keyed by layer.name. They come from
    the upstream LAYERED pipeline plan_layers node.
    """
    keying = get_keying_strategy(key_strategy_name)
    cache = LayerCache(output_dir, enabled=cache_enabled)
    sem = asyncio.Semaphore(parallelism)

    sibling_roles = [l.tradition_role or l.name for l in plan]
    positions = positions or {}
    coverages = coverages or {}

    async def _run(layer: LayerInfo) -> LayerOutcome:
        async with sem:
            try:
                return await generate_one_layer(
                    layer=layer,
                    anchor=tradition_anchor,
                    canvas=canvas,
                    keying=keying,
                    provider=provider,
                    sibling_roles=sibling_roles,
                    output_dir=output_dir,
                    position=positions.get(layer.name, ""),
                    coverage=coverages.get(layer.name, ""),
                    cache=cache,
                )
            except Exception as exc:
                logger.exception("unexpected failure for layer %s", layer.name)
                return LayerOutcome(ok=False, info=layer, rgba_path="", attempts=1)

    outcomes = await asyncio.gather(*(_run(l) for l in plan))

    layers_ok = [o for o in outcomes if o.ok]
    layers_failed = [
        LayerFailure(
            layer_id=o.info.id,
            role=o.info.tradition_role or o.info.name,
            reason=("validation_failed" if o.validation else "generation_failed"),
            attempts=o.attempts,
        )
        for o in outcomes if not o.ok
    ]
    return LayeredResult(layers=layers_ok, failed=layers_failed)
```

- [ ] **Step 4: Run test, confirm pass**

```bash
pytest tests/test_layered_generate_orchestration.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/layered_generate.py tests/test_layered_generate_orchestration.py
git commit -m "feat(layers): concurrent layered_generate orchestration with partial-failure semantics"
```

---

## Phase E — Pipeline integration

### Task 15: Refactor LayerGenerateNode to call the library

**Files:**
- Modify: `src/vulca/pipeline/nodes/layer_generate.py`
- Test: `tests/test_layer_generate_node_native.py`

This task **replaces the body of `_generate_layers`** in `LayerGenerateNode` so that, when the tradition's `layerability == "native"`, it routes through `layered_generate`. For non-native traditions it preserves the v0.12 behavior (the existing `_apply_mask` VLM-mask code path) so v0.12 tests continue to pass.

- [ ] **Step 1: Re-read the existing node**

```bash
sed -n '1,80p' src/vulca/pipeline/nodes/layer_generate.py
```

Confirm: `run` builds `layers`, `to_generate`, and `kept`, then calls `_generate_layers(to_generate, ctx)` and assembles the final list. **We modify only `_generate_layers`** to dispatch on `layerability`.

- [ ] **Step 2: Write the failing test**

```python
# tests/test_layer_generate_node_native.py
import asyncio
from vulca.pipeline.nodes.layer_generate import LayerGenerateNode
from vulca.pipeline.node import NodeContext
from vulca.layers.types import LayerInfo

def _ctx(tradition, output_dir):
    ctx = NodeContext()
    ctx.tradition = tradition
    ctx.provider = "mock"
    ctx.api_key = ""
    ctx.image_provider = None
    ctx.round_num = 1
    ctx._data = {
        "planned_layers": [
            LayerInfo(name="bg", description="paper", z_index=0, content_type="background", tradition_role="纸"),
            LayerInfo(name="far", description="far mtns", z_index=1, content_type="subject", tradition_role="远景淡墨", regeneration_prompt="distant mountains"),
        ],
        "layer_decisions": {},
        "layer_results": [],
        "output_dir": str(output_dir),
    }
    # NodeContext.get may use either attribute or _data dict — engineer should
    # adapt this to NodeContext's actual API.
    return ctx

def test_native_tradition_routes_through_library(tmp_path, monkeypatch):
    """When tradition has layerability=native, the node uses layered_generate."""
    called = {"used_library": False}
    from vulca.layers import layered_generate as lg_mod
    real_fn = lg_mod.layered_generate
    async def spy(**kw):
        called["used_library"] = True
        return await real_fn(**kw)
    monkeypatch.setattr(lg_mod, "layered_generate", spy)

    node = LayerGenerateNode()
    asyncio.run(node.run(_ctx("chinese_xieyi", tmp_path)))
    assert called["used_library"]
```

> Engineer note: `NodeContext` API needs to be inspected (`src/vulca/pipeline/node.py` or `pipeline/types.py`); the `_ctx` factory above is illustrative — wire it up to the real shape.

- [ ] **Step 3: Run test, expect failure**

- [ ] **Step 4: Modify `LayerGenerateNode`**

Inside `pipeline/nodes/layer_generate.py`, replace `_generate_layers` body with a dispatch:

```python
async def _generate_layers(self, layers, ctx):
    if not layers:
        return []

    from vulca.cultural.loader import get_tradition
    trad = get_tradition(ctx.tradition or "default")
    layerability = getattr(trad, "layerability", "split") if trad else "split"

    if layerability == "native":
        return await self._generate_layers_native(layers, ctx, trad)
    return await self._generate_layers_legacy(layers, ctx)
```

Move the existing implementation (the body that does `style_ref`, semaphore, `_generate_single`, `_apply_mask`) into `_generate_layers_legacy` unchanged.

Add the new path:

```python
async def _generate_layers_native(self, layers, ctx, trad):
    from vulca.layers.layered_generate import layered_generate
    from vulca.layers.layered_prompt import TraditionAnchor
    from vulca.layers.keying import CanvasSpec
    from vulca.layers.types import LayerResult

    output_dir = ctx.get("output_dir") or tempfile.mkdtemp(prefix="vulca_layered_")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    anchor = TraditionAnchor(
        canvas_color_hex=getattr(trad, "canvas_color", "#ffffff") or "#ffffff",
        canvas_description=getattr(trad, "canvas_description", "") or "white canvas",
        style_keywords=getattr(trad, "style_keywords", "") or "",
    )
    canvas = CanvasSpec.from_hex(getattr(trad, "canvas_color", "#ffffff") or "#ffffff")
    key_strategy_name = getattr(trad, "key_strategy", "luminance") or "luminance"

    # Pull positions/coverages from planned_layers metadata if present.
    # The plan_layers node stores them as attributes on LayerInfo if available;
    # otherwise default to empty dicts (no spatial constraint).
    positions: dict[str, str] = {l.name: getattr(l, "_position", "") for l in layers}
    coverages: dict[str, str] = {l.name: getattr(l, "_coverage", "") for l in layers}

    cache_enabled = not bool(getattr(ctx, "no_cache", False))

    from vulca.providers import get_image_provider
    provider_instance = ctx.image_provider or get_image_provider(ctx.provider, api_key=ctx.api_key)

    result = await layered_generate(
        plan=layers,
        tradition_anchor=anchor,
        canvas=canvas,
        key_strategy_name=key_strategy_name,
        provider=provider_instance,
        output_dir=output_dir,
        positions=positions,
        coverages=coverages,
        parallelism=int(os.environ.get("VULCA_LAYERED_PARALLELISM", "4")),
        cache_enabled=cache_enabled,
    )

    # Promote LayerOutcome → LayerResult for downstream compatibility
    out: list[LayerResult] = []
    for o in result.layers:
        o.info.status = "accepted"
        o.info.generation_round = ctx.round_num or 1
        out.append(LayerResult(info=o.info, image_path=o.rgba_path))
    for f in result.failed:
        # Synthesize a failed LayerResult so the pipeline downstream sees them
        for l in layers:
            if l.id == f.layer_id:
                l.status = "failed"
                l.weakness = f.reason
                out.append(LayerResult(info=l, image_path=""))
                break

    # Stash the result on ctx so manifest writer can pick it up later
    ctx.set("layered_result", result) if hasattr(ctx, "set") else None
    return sorted(out, key=lambda r: r.info.z_index)
```

- [ ] **Step 5: Run test and v0.12 regression suite**

```bash
pytest tests/test_layer_generate_node_native.py -v
pytest tests/test_v012_layer_primitives.py tests/test_layered_pipeline.py tests/test_layer_generate_node.py -v
```

All must pass. (If `_layered_pipeline` integration tests fail because they hit the legacy branch but expected modern behavior, adjust the test fixture's `tradition` to a non-native one to keep them on the legacy code path.)

- [ ] **Step 6: Commit**

```bash
git add src/vulca/pipeline/nodes/layer_generate.py tests/test_layer_generate_node_native.py
git commit -m "feat(pipeline): LayerGenerateNode dispatches native traditions through layered_generate library"
```

---

### Task 16: Wire spatial metadata from plan_layers into LayerInfo

**Files:**
- Read: `src/vulca/pipeline/nodes/plan_layers.py`
- Modify: `src/vulca/pipeline/nodes/plan_layers.py` (set `_position` / `_coverage` on each LayerInfo)
- Test: `tests/test_plan_layers_spatial_passthrough.py`

The plan VLM already returns `position` and `coverage`. Make sure they reach `LayerInfo` so Task 15's anchored prompt can use them.

- [ ] **Step 1: Read existing plan_layers node**

```bash
cat src/vulca/pipeline/nodes/plan_layers.py | sed -n '1,100p'
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_plan_layers_spatial_passthrough.py
import json
from vulca.pipeline.nodes.plan_layers import _parse_plan_response  # adapt to actual private name

def test_position_and_coverage_pass_through():
    raw = json.dumps({"layers": [
        {"name": "far", "description": "x", "z_index": 1,
         "blend_mode": "normal", "dominant_colors": [], "content_type": "subject",
         "position": "upper 30%", "coverage": "20-30%",
         "regeneration_prompt": "distant mountains"},
    ]})
    layers = _parse_plan_response(raw)
    assert len(layers) == 1
    li = layers[0]
    assert getattr(li, "_position", None) == "upper 30%"
    assert getattr(li, "_coverage", None) == "20-30%"
```

> Engineer note: `_parse_plan_response` is a placeholder name. Find the actual JSON-parsing function in `plan_layers.py` and use it.

- [ ] **Step 3: Run test, expect failure** (the parser likely drops position/coverage today)

- [ ] **Step 4: Modify the parser** to set `li._position = item.get("position", "")` and `li._coverage = item.get("coverage", "")` on each constructed LayerInfo. (Using underscore-prefixed attributes avoids polluting the dataclass schema.)

- [ ] **Step 5: Run test, confirm pass**

- [ ] **Step 6: Commit**

```bash
git add src/vulca/pipeline/nodes/plan_layers.py tests/test_plan_layers_spatial_passthrough.py
git commit -m "feat(pipeline): plan_layers passes position/coverage as private attrs on LayerInfo"
```

---

## Phase F — B-path matting

### Task 17: soften_mask

**Files:**
- Create: `src/vulca/layers/matting.py`
- Test: `tests/test_matting_soften.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_matting_soften.py
import numpy as np
from vulca.layers.matting import soften_mask

def _binary_disc(h=64, w=64, r=20):
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h // 2, w // 2
    return ((yy - cy) ** 2 + (xx - cx) ** 2 <= r * r).astype(np.uint8)

def _rgb_for_disc(h=64, w=64, r=20):
    img = np.full((h, w, 3), 255, dtype=np.uint8)
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h // 2, w // 2
    inside = (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
    img[inside] = (40, 40, 40)
    return img

def test_soften_returns_float_in_unit_range():
    mask = _binary_disc()
    rgb = _rgb_for_disc()
    out = soften_mask(mask, rgb)
    assert out.dtype == np.float32
    assert out.shape == mask.shape
    assert (out >= 0).all() and (out <= 1).all()

def test_soften_blurs_hard_edges():
    mask = _binary_disc()
    rgb = _rgb_for_disc()
    out = soften_mask(mask, rgb, feather_px=3, guided=False)
    # Some intermediate alpha values should exist (not pure 0/1)
    intermediates = ((out > 0.05) & (out < 0.95)).sum()
    assert intermediates > 0

def test_soften_disabled_returns_close_to_input():
    mask = _binary_disc()
    rgb = _rgb_for_disc()
    out = soften_mask(mask, rgb, feather_px=0, guided=False, despill=False)
    diff = np.abs(out - mask.astype(np.float32)).mean()
    assert diff < 0.05
```

- [ ] **Step 2: Run test, expect failure**

- [ ] **Step 3: Implement matting**

```python
# src/vulca/layers/matting.py
"""B-path mask softening: feather + (optional) guided filter + despill.

No new mandatory dependency. Uses cv2.ximgproc.guidedFilter when [tools]
extra is installed; otherwise falls back to a numpy box-filter feather.
"""
from __future__ import annotations

import numpy as np


def _box_blur(arr: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return arr.astype(np.float32)
    k = radius * 2 + 1
    pad = np.pad(arr.astype(np.float32), radius, mode="edge")
    out = np.zeros_like(arr, dtype=np.float32)
    s = pad.cumsum(axis=0).cumsum(axis=1)
    H, W = arr.shape
    for y in range(H):
        for x in range(W):
            y0, y1 = y, y + k
            x0, x1 = x, x + k
            total = s[y1, x1] - s[y0, x1] - s[y1, x0] + s[y0, x0]
            out[y, x] = total / (k * k)
    return out


def _try_guided_filter(mask: np.ndarray, rgb: np.ndarray, radius: int) -> np.ndarray | None:
    try:
        import cv2
        from cv2 import ximgproc
    except Exception:
        return None
    guide = rgb.astype(np.float32) / 255.0
    src = mask.astype(np.float32)
    return ximgproc.guidedFilter(guide=guide, src=src, radius=radius, eps=1e-3)


def _despill(rgba_alpha: np.ndarray, rgb: np.ndarray, bg_color=(255, 255, 255)) -> np.ndarray:
    """Reduce background color contamination at edges (cheap heuristic)."""
    bg = np.array(bg_color, dtype=np.float32)
    diff = np.linalg.norm(rgb.astype(np.float32) - bg, axis=-1) / 441.0
    return np.clip(rgba_alpha * (0.5 + 0.5 * diff), 0.0, 1.0)


def soften_mask(
    mask: np.ndarray,
    rgb: np.ndarray,
    *,
    feather_px: int = 2,
    guided: bool = True,
    despill: bool = True,
) -> np.ndarray:
    if mask.dtype == np.bool_:
        mask = mask.astype(np.uint8)

    soft: np.ndarray | None = None
    if guided:
        soft = _try_guided_filter(mask, rgb, radius=max(feather_px, 4))
    if soft is None:
        soft = _box_blur(mask, feather_px)

    soft = soft.astype(np.float32)
    soft = np.clip(soft, 0.0, 1.0)

    if despill:
        soft = _despill(soft, rgb)
    return soft.astype(np.float32)
```

- [ ] **Step 4: Run test, confirm pass**

```bash
pytest tests/test_matting_soften.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/matting.py tests/test_matting_soften.py
git commit -m "feat(layers): soften_mask for B-path (feather + guided filter optional + despill)"
```

---

### Task 18: Wire matting into split_vlm output

**Files:**
- Read: `src/vulca/layers/split.py` and `src/vulca/layers/vlm_mask.py`
- Modify: `src/vulca/layers/vlm_mask.py` (or wherever the binary mask is finalized for split_vlm)
- Test: `tests/test_split_vlm_softening.py`

> Engineer judgment call: find the smallest place where each split layer's binary mask is converted into its alpha channel, and apply `soften_mask` there. Do not touch SAM3's tensor pipeline (it has its own resize/OR logic). For v0.13 the goal is **softening only the VLM-mask path**; SAM3 stays as v0.12.

- [ ] **Step 1: Locate the conversion point**

```bash
grep -n "apply_vlm_mask\|alpha\|putalpha" src/vulca/layers/vlm_mask.py
```

- [ ] **Step 2: Write the failing test** that asserts VLM split output has soft (non-binary) alpha at edges. Use mock VLM mask (a binary disc) and assert the saved RGBA has at least N intermediate alpha pixels.

- [ ] **Step 3: Insert `soften_mask` call** at the conversion point. Default `feather_px=2`, `guided=True`, `despill=True`.

- [ ] **Step 4: Run test + the v0.12 split regression suite**

```bash
pytest tests/test_split_vlm_softening.py tests/test_v012_split_vlm.py tests/test_layers_v2_split.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/vlm_mask.py tests/test_split_vlm_softening.py
git commit -m "feat(layers): apply soften_mask to VLM-mask alpha for B-path edge quality"
```

---

## Phase G — Manifest schema bump

### Task 19: Manifest version 3 with new fields

**Files:**
- Modify: `src/vulca/layers/manifest.py`
- Test: `tests/test_manifest_v3.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_manifest_v3.py
import json
from pathlib import Path
from vulca.layers.manifest import write_manifest, load_manifest, MANIFEST_VERSION
from vulca.layers.types import LayerInfo

def _layers():
    return [LayerInfo(name="bg", description="paper", z_index=0, content_type="background", tradition_role="纸")]

def test_manifest_version_is_3():
    assert MANIFEST_VERSION == 3

def test_manifest_writes_new_fields(tmp_path):
    p = write_manifest(
        _layers(), output_dir=str(tmp_path), width=1024, height=1024,
        generation_path="a", layerability="native", partial=False,
    )
    data = json.loads(Path(p).read_text())
    assert data["version"] == 3
    assert data["generation_path"] == "a"
    assert data["layerability"] == "native"
    assert data["partial"] is False

def test_manifest_v2_still_loads(tmp_path):
    """A v2 file (no new fields) should load with defaults, not crash."""
    v2 = {
        "version": 2, "width": 256, "height": 256, "source_image": "", "split_mode": "",
        "created_at": "2025-01-01T00:00:00Z",
        "layers": [{"id": "x", "name": "bg", "description": "", "z_index": 0,
                    "blend_mode": "normal", "content_type": "background",
                    "visible": True, "locked": False, "file": "bg.png",
                    "dominant_colors": [], "regeneration_prompt": "",
                    "opacity": 1.0, "x": 0, "y": 0, "width": 100, "height": 100,
                    "rotation": 0, "content_bbox": None}],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(v2))
    artwork = load_manifest(str(tmp_path))
    assert len(artwork.layers) == 1
```

- [ ] **Step 2: Run test, expect failure**

- [ ] **Step 3: Bump version + add new fields to writer**

In `src/vulca/layers/manifest.py`:

1. Change `MANIFEST_VERSION = 2` → `MANIFEST_VERSION = 3`.
2. Add kwargs to `write_manifest`: `generation_path: str = ""`, `layerability: str = ""`, `partial: bool = False`, `warnings: list | None = None`. Write them at top-level. Also accept per-layer extras: `layer_extras: dict[str, dict] | None = None` mapping `layer.id` → dict (with keys `source`, `canvas_color`, `key_strategy`, `cache_hit`, `attempts`, `validation`).
3. In `load_manifest`, simply read these top-level keys with defaults — the existing `LayeredArtwork` doesn't need new fields for the engineer to read them externally; they're available via the raw dict if needed. (Out of scope to extend `LayeredArtwork` itself in v0.13.)

- [ ] **Step 4: Run test, confirm pass**

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/manifest.py tests/test_manifest_v3.py
git commit -m "feat(layers): bump manifest to v3 with generation_path/layerability/partial/warnings"
```

---

### Task 20: Wire layered metadata into manifest writes

**Files:**
- Modify: `src/vulca/pipeline/nodes/composite_node.py` or wherever the LAYERED template currently calls `write_manifest`
- Test: `tests/test_layered_manifest_metadata.py`

- [ ] **Step 1: Find the manifest write call**

```bash
grep -rn "write_manifest" src/vulca/pipeline/
```

- [ ] **Step 2: Write the failing test** asserting that when LAYERED runs on a native tradition (mock provider), the resulting `manifest.json` contains `generation_path: "a"` and `layerability: "native"`.

- [ ] **Step 3: Modify the composite/manifest-write site** to pass through:
  - `generation_path` from `ctx.get("layered_result")` presence (`"a"` if present, `"b"` otherwise)
  - `layerability` from the tradition lookup
  - `partial` from `result.is_complete`
  - `warnings` from each `LayerOutcome.validation.warnings`
  - `layer_extras` populated from each `LayerOutcome`

- [ ] **Step 4: Run test, confirm pass**

- [ ] **Step 5: Commit**

```bash
git add src/vulca/pipeline/nodes/composite_node.py tests/test_layered_manifest_metadata.py
git commit -m "feat(pipeline): write layered metadata into manifest.json"
```

---

## Phase H — CLI

### Task 21: New flags `--no-cache`, `--strict`, `--max-layers`

**Files:**
- Modify: `src/vulca/cli.py` (around line 98 where `--layered` is defined)
- Test: `tests/test_cli_layered_flags.py`

- [ ] **Step 1: Find the create-subcommand argparser block**

```bash
sed -n '85,120p' src/vulca/cli.py
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_cli_layered_flags.py
import subprocess, sys

def test_no_cache_flag_present():
    out = subprocess.run([sys.executable, "-m", "vulca", "create", "--help"],
                         capture_output=True, text=True)
    assert "--no-cache" in out.stdout
    assert "--strict" in out.stdout
    assert "--max-layers" in out.stdout
```

- [ ] **Step 3: Add the three flags**

```python
create_p.add_argument("--no-cache", action="store_true", help="Disable layered cache (forces re-generation)")
create_p.add_argument("--strict", action="store_true", help="Layered mode: any failed layer fails the run")
create_p.add_argument("--max-layers", type=int, default=8, help="Cap the number of layers (default 8)")
```

Plumb `args.no_cache`, `args.strict`, `args.max_layers` into the `PipelineInput` (add fields to `PipelineInput` if needed) and propagate to `LayerGenerateNode` via `ctx`.

- [ ] **Step 4: Run test, confirm pass**

- [ ] **Step 5: Commit**

```bash
git add src/vulca/cli.py src/vulca/pipeline/types.py tests/test_cli_layered_flags.py
git commit -m "feat(cli): --no-cache / --strict / --max-layers flags for layered create"
```

---

### Task 22: `vulca layers retry` subcommand

**Files:**
- Modify: `src/vulca/cli.py`
- Create: `src/vulca/layers/retry.py` (small helper)
- Test: `tests/test_cli_layers_retry.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli_layers_retry.py
import subprocess, sys, json
from pathlib import Path

def test_retry_subcommand_help():
    out = subprocess.run([sys.executable, "-m", "vulca", "layers", "retry", "--help"],
                         capture_output=True, text=True)
    assert out.returncode == 0
    assert "--layer" in out.stdout
    assert "--all-failed" in out.stdout
```

- [ ] **Step 2: Add the subparser**

In `cli.py`, add to the `layers` subcommand group:

```python
retry_p = layers_sub.add_parser("retry", help="Retry failed layers in a layered artifact")
retry_p.add_argument("artifact_dir", help="Path to the artifact directory")
retry_p.add_argument("--layer", help="Retry only this layer name")
retry_p.add_argument("--all-failed", action="store_true", help="Retry every failed layer")
retry_p.set_defaults(func=_cmd_layers_retry)
```

- [ ] **Step 3: Implement `_cmd_layers_retry`** — load `manifest.json`, find layers with status=failed (or the named one), call `layered_generate` for those layers only (cache hits keep the others free), rewrite manifest.

- [ ] **Step 4: Add `src/vulca/layers/retry.py`** with the small helper that reads the manifest, identifies targets, and re-invokes `layered_generate` on them.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/cli.py src/vulca/layers/retry.py tests/test_cli_layers_retry.py
git commit -m "feat(cli): layers retry subcommand for re-generating failed layers"
```

---

### Task 23: `vulca layers cache clear` subcommand + `discouraged` warning UX

**Files:**
- Modify: `src/vulca/cli.py`
- Test: `tests/test_cli_layers_cache.py`, `tests/test_cli_discouraged_warning.py`

- [ ] **Step 1: Add the cache subcommand** (deletes `<artifact>/.layered_cache/`).

```python
cache_p = layers_sub.add_parser("cache", help="Cache management")
cache_sub = cache_p.add_subparsers(dest="cache_cmd", required=True)
cache_clear = cache_sub.add_parser("clear")
cache_clear.add_argument("artifact_dir")
cache_clear.set_defaults(func=_cmd_layers_cache_clear)
```

Implementation: `shutil.rmtree(Path(args.artifact_dir) / ".layered_cache", ignore_errors=True)`.

- [ ] **Step 2: Add the discouraged-warning UX**

In the `--layered` branch of `_cmd_create` (around `cli.py:609`), before calling the LAYERED pipeline, look up the tradition's `layerability`:

```python
trad = get_tradition(args.tradition or "default")
layerability = getattr(trad, "layerability", "split") if trad else "split"
if layerability == "discouraged":
    msg = (f"Tradition '{args.tradition}' does not support high-quality layering.\n"
           "Result is best-effort and intended for analysis only.")
    if sys.stdin.isatty() and not getattr(args, "yes", False):
        print(f"⚠ {msg}\n  Continue? [y/N] ", end="")
        if input().strip().lower() != "y":
            print("Aborted.")
            return
    else:
        print(f"⚠ {msg}", file=sys.stderr)
```

- [ ] **Step 3: Tests** — for the cache subcommand, create a fake `.layered_cache` dir and assert it is deleted. For discouraged UX, run with `tradition=photography` and capture stderr.

- [ ] **Step 4: Commit**

```bash
git add src/vulca/cli.py tests/test_cli_layers_cache.py tests/test_cli_discouraged_warning.py
git commit -m "feat(cli): layers cache clear subcommand and discouraged tradition warning"
```

---

## Phase I — MCP

### Task 24: MCP `vulca_layered_create` and `vulca_layers_retry`

**Files:**
- Modify: `src/vulca/mcp_server.py`
- Test: `tests/test_mcp_layered.py`

- [ ] **Step 1: Find the existing `@mcp.tool()` pattern**

```bash
sed -n '982,1050p' src/vulca/mcp_server.py
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_mcp_layered.py
import asyncio
from vulca.mcp_server import vulca_layered_create, vulca_layers_retry

def test_layered_create_runs_with_mock(tmp_path):
    out = asyncio.run(vulca_layered_create(
        intent="远山薄雾",
        tradition="chinese_xieyi",
        provider="mock",
        output_dir=str(tmp_path),
    ))
    assert out["status"] in ("complete", "partial")
    assert (tmp_path / "manifest.json").exists()

def test_layers_retry_handles_missing_failed():
    out = asyncio.run(vulca_layers_retry(artifact_dir="/nonexistent"))
    assert out["error"]
```

- [ ] **Step 3: Add the two tools**

```python
@mcp.tool()
async def vulca_layered_create(
    intent: str,
    tradition: str = "default",
    provider: str = "gemini",
    output_dir: str = "",
    no_cache: bool = False,
    strict: bool = False,
    max_layers: int = 8,
) -> dict:
    """Generate a layered artwork using A-path layered generation."""
    from vulca.pipeline.engine import execute
    from vulca.pipeline.templates import LAYERED
    from vulca.pipeline.types import PipelineInput

    inp = PipelineInput(
        subject=intent, intent=intent, tradition=tradition, provider=provider,
        layered=True, no_cache=no_cache, strict=strict, max_layers=max_layers,
        output_dir=output_dir or None,
    )
    output = await execute(LAYERED, inp)
    return output.to_dict()


@mcp.tool()
async def vulca_layers_retry(
    artifact_dir: str,
    layer: str = "",
    all_failed: bool = False,
) -> dict:
    """Retry failed layers in a layered artifact."""
    from vulca.layers.retry import retry_layers
    if not artifact_dir:
        return {"error": "artifact_dir required"}
    try:
        return await retry_layers(artifact_dir, layer=layer or None, all_failed=all_failed)
    except FileNotFoundError as e:
        return {"error": str(e)}
```

- [ ] **Step 4: Run test, confirm pass**

- [ ] **Step 5: Commit**

```bash
git add src/vulca/mcp_server.py tests/test_mcp_layered.py
git commit -m "feat(mcp): vulca_layered_create and vulca_layers_retry tools"
```

---

## Phase J — Integration & golden tests

### Task 25: A-path end-to-end on chinese_xieyi (mock provider)

**Files:**
- Test: `tests/test_layered_e2e_xieyi.py`

- [ ] **Step 1: Write the failing-then-passing test**

```python
# tests/test_layered_e2e_xieyi.py
import asyncio, json
from pathlib import Path
from vulca.pipeline.engine import execute
from vulca.pipeline.templates import LAYERED
from vulca.pipeline.types import PipelineInput

def test_xieyi_layered_e2e_mock(tmp_path):
    inp = PipelineInput(
        subject="远山薄雾",
        intent="远山薄雾",
        tradition="chinese_xieyi",
        provider="mock",
        layered=True,
        output_dir=str(tmp_path),
    )
    output = asyncio.run(execute(LAYERED, inp))
    assert output.status in ("completed", "complete", "partial")

    manifest_path = tmp_path / "manifest.json"
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text())
    assert data.get("generation_path") == "a"
    assert data.get("layerability") == "native"
    assert len(data.get("layers", [])) > 0
```

- [ ] **Step 2: Iterate until pass.** This test exercises the full A-path through the pipeline; if it fails, the failure points to whichever earlier task is incomplete.

- [ ] **Step 3: Commit**

```bash
git add tests/test_layered_e2e_xieyi.py
git commit -m "test(layers): A-path e2e on chinese_xieyi with mock provider"
```

---

### Task 26: Partial-failure e2e

**Files:**
- Test: `tests/test_layered_partial_e2e.py`

- [ ] **Step 1: Write the test** that injects a failing layer (mock provider with a controllable failure list) and asserts:
  - Pipeline exits with status indicating partial success
  - `manifest.json` has `partial: true`
  - At least one layer present and at least one in the failed list

- [ ] **Step 2: Iterate until pass**

- [ ] **Step 3: Commit**

```bash
git add tests/test_layered_partial_e2e.py
git commit -m "test(layers): partial-failure non-blocking e2e"
```

---

### Task 27: Golden tests (real Gemini, gated)

**Files:**
- Create: `tests/test_layered_golden_xieyi.py`
- Create: `tests/golden/layered_xieyi_alpha_histogram.json` (initial baseline)

Per the spec, golden tests are gated behind a `--run-real-provider` flag and only run weekly. The test should:
1. Skip if `GOOGLE_API_KEY` not set or `--run-real-provider` not passed
2. Generate a layered xieyi artwork ("远山薄雾" intent)
3. For each layer, compute alpha histogram (16-bin) and compare against the JSON baseline within statistical tolerance

- [ ] **Step 1: Add a pytest marker / fixture** for `--run-real-provider`. Most repos do this in `conftest.py`. If one already exists, reuse it.

- [ ] **Step 2: Write the test** with the histogram-comparison function (use chi-square distance or simple per-bin tolerance like `abs(diff) < 0.05`).

- [ ] **Step 3: Run once with real Gemini to populate the baseline JSON**, commit the baseline.

- [ ] **Step 4: Commit**

```bash
git add tests/test_layered_golden_xieyi.py tests/golden/layered_xieyi_alpha_histogram.json tests/conftest.py
git commit -m "test(layers): golden test for A-path on xieyi (real provider, gated)"
```

---

## Phase K — Docs & release

### Task 28: README "Layered creation" section

**Files:**
- Modify: `README.md`

- [ ] **Step 1:** In the "What You Can Do" section, add ~30 lines:

```markdown
### Layered creation — generation-time alpha for cultural art

```bash
vulca create "远山薄雾" -t chinese_xieyi --layered -o art/
```

VULCA generates each layer (远山, 中景, 题款 ...) independently on the
canonical canvas of the tradition (生宣纸 for xieyi). Per-layer alpha is
extracted by tradition-specific keying, so flying-white and ink gradients
become true soft alpha — no halos, no hard edges. Layers can be re-rendered
individually with `vulca layers retry art/ --layer 远山`.

Cost: N provider calls per artwork (one per layer). Iterative editing
hits cache, so changing one layer is one provider call.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README section on layered creation"
```

---

### Task 29: CHANGELOG + version bump

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `src/vulca/_version.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Bump version** to `0.13.0` in both `_version.py` and `pyproject.toml`.

- [ ] **Step 2: Add CHANGELOG entry** summarizing acceptance criteria from the spec.

- [ ] **Step 3: Run the full test suite**

```bash
pytest -x
```

All passing (golden tests skipped without `--run-real-provider`).

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md src/vulca/_version.py pyproject.toml
git commit -m "release: v0.13.0 — Layered Generation A-path"
```

---

## Spec coverage check

| Spec section | Plan tasks |
|---|---|
| Architecture (dual path + dispatch) | 8, 15 |
| Module map (new files) | 1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 17 |
| Module map (modified files) | 8, 9, 15, 16, 18, 19, 20, 21, 22, 23, 24, 27 |
| Keying subsystem (Tier 0/1/2 + dispatch + LAB) | 1, 2, 3, 4, 5 |
| Tradition YAML +5 fields | 7, 8, 9 |
| Layered generation (orchestration + cache + partial) | 11, 12, 13, 14 |
| Defense 1 (prompt anchoring) | 10 |
| Defense 2 (validation) | 6 |
| Defense 3 (reference image) | **interface only — Task 13/14 leave a hook in `generate_one_layer` signature; full implementation deferred to v0.14 per spec** |
| B-path repositioning + matting | 17, 18 |
| `discouraged` UX | 23 |
| Manifest schema bump | 19, 20 |
| CLI new flags + retry + cache | 21, 22, 23 |
| MCP tools | 24 |
| Stats / observability | **explicitly dropped: spec said "telemetry into manifest"; the manifest writes already capture cache_hit, attempts, validation in tasks 19/20; no separate counter module** |
| Tests (unit/integration/golden) | 1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 25, 26, 27 |
| README + release | 28, 29 |

All acceptance criteria from the spec map to tasks. Defense 3 and the in-process counter module are explicitly deferred — both noted in the spec as v0.13 non-goals.

## v0.13.2 retry budget update

> **v0.13.2 update:** in-process retry budget=2 for `generation_failed`
> landed in commit `c22eaf9` (3 total attempts, full-jitter backoff).
> `validation_failed` is deterministic and not retried.
> `AssertionError`, `TypeError`, and `asyncio.CancelledError` propagate.
> External `vulca layers retry` CLI remains the operator-driven path
> for full manifest-level re-generation.
