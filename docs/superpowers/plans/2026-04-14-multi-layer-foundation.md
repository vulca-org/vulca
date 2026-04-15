# Multi-Layer Decomposition Foundation (Phase 0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade Vulca's layer infrastructure to support 10–20 semantic layers per image (portraits with face parts, group portraits with per-person layers) while keeping full backward compatibility with existing 3-layer manifests.

**Architecture:** Dual-field manifest (coarse `content_type` + hierarchical `semantic_path`). All call sites use the coarse bucket for logic; `semantic_path` is free-form dot-notation (`subject.face.eyes`, `person[0].hair`). Overlap resolution is z-index driven, not name-based. Large images are pre-resized before decode. A post-decomposition validator guarantees `coverage == 1.0` and `overlap == 0` invariants.

**Tech Stack:** Python 3.11+, NumPy, Pillow, OpenCV, pytest. No new runtime deps — uses existing Vulca layer stack.

---

## Context You Need to Know

**Problem being solved:** EVF-SAM multi-layer experiments produced manifests with dotted names like `subject.face.eyes` and 12–20 layers per image. Nine call sites across the Vulca codebase hardcode `info.content_type == "background"` to identify the catch-all layer. Dotted names break this check, routing "background.catch_all" through the same path as "subject.face" and destroying coverage invariants.

**Affected files (9 primary + 8 additional call sites = 17 total, verified 2026-04-14):**

Primary (positive check `== "background"`):
- `src/vulca/layers/sam.py:126`
- `src/vulca/layers/sam3.py:88` and `:130`
- `src/vulca/layers/split.py:245` and `:267`
- `src/vulca/layers/alpha.py:86`
- `src/vulca/layers/layered_generate.py:319`
- `src/vulca/pipeline/nodes/layer_generate.py:348`
- `src/vulca/pipeline/nodes/plan_layers.py:112`

Additional (negated / non-background bucket checks — SAME BUG CLASS, must be updated together):
- `src/vulca/layers/split.py:179` — `!= "background"` form
- `src/vulca/layers/alpha.py:20` — `if ct == "background":` in `select_alpha_strategy`
- `src/vulca/pipeline/nodes/layer_generate.py:299` and `:394` — `!= "background"` form
- `src/vulca/pipeline/nodes/decide.py:171` — `!= "background"` form
- `src/vulca/layers/mask.py:63` and `:80` — hardcoded non-background bucket literals (tuples)
- `src/vulca/layers/layered_generate.py:72` — hardcoded non-background bucket literal (tuple; previously cited as `:71`, verify before editing)

**NOT in scope for Task 4 (explicitly excluded — flag if a reviewer suggests adding):**
- `src/vulca/pipeline/nodes/layer_generate.py:411` — palette dict keyed by literal `"background"` color lookup, NOT a role branch. Dotted `semantic_path` won't affect it.
- `src/vulca/layers/manifest.py:129, :154`, `src/vulca/layers/artifact.py:108`, `src/vulca/layers/prompt.py:66` — these write `"background"` as a `.get(..., "background")` default. Safe as defaults; auditing is optional.

Task 4 Step 10 verification grep must cover both `==` and `!=` forms, not just `==`.

**Out-of-scope surfaces that also need updating before Phase 0 is truly complete** (add as follow-up sub-tasks in Task 4 or new Task 4b):
- `src/vulca/cli.py:226` — `layers add` CLI has no `--semantic-path` input.
- `src/vulca/layers/ops.py:57` — layer-ops path doesn't propagate `semantic_path`.
- `src/vulca/mcp_server.py:1115` — MCP `layers.add` tool signature omits `semantic_path`.
- `src/vulca/layers/artifact.py:103` — V3 loader ignores future `semantic_path` field.
- `src/vulca/layers/prompt.py:6, :28` and `src/vulca/layers/plan_prompt.py:114, :133` — analyze/plan prompt schemas still emit only 3 layers and omit `semantic_path`.
- `scripts/run-full-showcase.py` + `scripts/generate-showcase-html.py:235` — showcase still describes 3 layers.
- Existing tests `tests/test_layers_v2_types.py:9`, `tests/test_layers_v2_manifest.py:42` need updating (not just new tests).

**Existing LayerInfo schema** (`src/vulca/layers/types.py`):
```python
@dataclass
class LayerInfo:
    name: str
    description: str
    z_index: int
    content_type: str = "background"   # ← currently the branching field
    # ... 20+ other fields
```

**Manifest format** is V3 (`src/vulca/layers/manifest.py`). Existing writer doesn't write `semantic_path`. Loader is tolerant of missing fields via `.get()`.

**Key invariants to preserve:**
1. Every layer's alpha mask has values 0 or 255 only (binary).
2. Union of all layer masks == 100% of canvas (no holes).
3. Intersection of any two layer masks == 0 (no overlap).
4. Existing 3-layer manifests without `semantic_path` continue to load and render.

**Testing convention:** Tests live under `tests/vulca/`. Run with `pytest tests/vulca/layers/ -v`. Mock tests (no cv2/litellm) live in `tests/vulca/layers/mocks/`. Project has `pyproject.toml` with `ruff` + `pytest` configured.

---

## Pre-Execution Amendments (2026-04-14 review round)

This plan was reviewed by superpowers+codex+simplifier before execution. The following binding amendments apply:

**1. Execution mode: INLINE ONLY, not Subagent-Driven.**
Independent review found that most tasks have direct dependencies or shared-file edits. Only Tasks 5 and 6 are safely parallel. Attempting Subagent-Driven dispatch would collide on shared files (`migrate_evfsam_to_layers.py` across Tasks 7+10+11; `evfsam_showcase.py` across Tasks 8+9). Execute inline with checkpoints between tasks.

**2. Dependency DAG (explicit):**
```
Task 0  ──► Task 1  ──► Task 2
                         │
                         ▼
Task 3  ──► Task 4  ──► Task 4b
Task 5  ──► Task 8
Task 6  ──► Task 7  ──► Task 10 ──► Task 11
                                    ▲
            Task 9  ─────────────────┘
                                    ▼
                                  Task 12
```
Safe parallelizable group: `{1, 3, 5, 6}`. Task 4b depends on both Tasks 2 (LayerInfo+manifest round-trip) and 4 (coarse bucket substitution must not regress when new schema field is added). Everything else sequential.

**3. New Task 0 (pre-requisite): Lift the 8-layer cap.**
`src/vulca/cli.py:101` clamps `--layers` to a max of 8, and `src/vulca/pipeline/types.py:102` defaults `max_layers=8`. These directly block the 10-20 layer goal. Must be lifted before any Phase 0 task is executed. See Task 0 spec below (inserted before Task 1).

**4. Task 4 broadening.**
The 9 `== "background"` sites enumerated above miss 8 more (`!= "background"` + hardcoded non-background literals). Task 4 must cover all **17** sites. Task 4 Step 10 verification regex must be `content_type\s*(==|!=)\s*"background"` — not just `==`.

**5. Task 7 `_z_index_for` already exists — extend, don't create.**
`_z_index_for(layer_name)` is already defined at `scripts/migrate_evfsam_to_layers.py:27-29` as `return Z_INDEX.get(layer_name, 99)`. Task 7 must extend this helper to fall back to the coarse bucket (via `coarse_bucket_of` from Task 3) when an exact-name miss occurs, so dotted names like `subject.face.eyes` resolve via the `subject` bucket rather than defaulting to `99`. See Task 7's inline plan-rot note for full semantics.

**6. Task 11 field hygiene.**
Task 11 test sets `content_type=sp` where `sp` is the full path (`subject.face.eyes`). This violates the dual-field design (content_type is the coarse bucket; semantic_path holds the path). Fix: set `content_type="subject"` + `semantic_path="subject.face.eyes"`.

**7. Task 12 acceptance tightening.**
"100% opaque composite" does not prove semantic correctness. Add a sub-step comparing per-layer bbox pixel hashes against the pre-refactor baseline (or a visual diff against the pre-refactor composite) to catch regressions where coverage=1.0 but pixels mis-assigned.

**8. Performance baseline (Task 12 sub-step).**
Record wall-clock for a 12-layer run as a baseline for Phase 1 (which will add VLM-driven prompt generation). Note: 10–20 layers × existing VLM re-prompts in `layered_generate.py` could be ~7× the API cost/latency of the 3-layer baseline.

**9. Data migration note.**
Existing showcase manifests under `assets/showcase/layers/` all have `content_type ∈ {background, subject, foreground}` and no `semantic_path`. The migrate script regenerates masks from scratch — destructive for showcase only. External user-edited manifests auto-gain empty `semantic_path` on load via Task 2's `.get("semantic_path", "")` contract.

**10. Deferred refinements (Simplifier signals noted; keep in scope).**
`_KNOWN_BUCKETS` frozenset, `_PREFIX_ALIASES`, `decomp_validator` as a separate module, `image_loader` as a separate module — Simplifier argued these are YAGNI. Decision: KEEP as specified; they are load-bearing for downstream Phase 1 (VLM prompt generation reads the bucket taxonomy; validator is reused across the pipeline). Revisit if Phase 1 doesn't materialize.

---

## File Structure

```
Creates:
  src/vulca/layers/coarse_bucket.py       # Extract coarse bucket from content_type
  src/vulca/layers/decomp_validator.py    # Post-decomposition invariant checks
  src/vulca/layers/image_loader.py        # Pre-resize + safe imread for giant images
  tests/vulca/layers/test_coarse_bucket.py
  tests/vulca/layers/test_decomp_validator.py
  tests/vulca/layers/test_image_loader.py
  tests/vulca/layers/test_manifest_semantic_path.py
  tests/vulca/layers/test_catch_all_callsites.py

Modifies:
  src/vulca/layers/types.py               # Add semantic_path field
  src/vulca/layers/manifest.py            # Write/read semantic_path
  src/vulca/layers/sam.py                 # Use coarse_bucket
  src/vulca/layers/sam3.py                # Use coarse_bucket (2 sites)
  src/vulca/layers/split.py               # Use coarse_bucket (2 sites)
  src/vulca/layers/alpha.py               # Use coarse_bucket
  src/vulca/layers/layered_generate.py    # Use coarse_bucket
  src/vulca/pipeline/nodes/layer_generate.py    # Use coarse_bucket
  src/vulca/pipeline/nodes/plan_layers.py       # Use coarse_bucket
  scripts/migrate_evfsam_to_layers.py     # Z-index driven overlap + use validator
  scripts/_evfsam_common.py               # Use image_loader for pre-resize
```

Each file has one clear responsibility. `coarse_bucket.py` is the single source of truth for the `content_type` → `{background, subject, foreground, detail, ...}` mapping. `decomp_validator.py` is a pure function that fails loudly on bad decompositions. `image_loader.py` is the single entry point for reading source images across all scripts.

---

### Task 0: Lift the 8-layer cap (pre-requisite)

**Motivation:** Two hard ceilings in the CLI/types layer clamp layered generation at 8 layers, directly blocking the 10–20 layer goal of Phase 0. They must be lifted before any other task runs, otherwise Task 12's 12-layer smoke test cannot exist.

**Files:**
- Modify: `src/vulca/cli.py:~101` (the `--layers` argparse definition inside `create` subcommand)
- Modify: `src/vulca/pipeline/types.py:~102` (the `max_layers` default on PipelineInput)
- Test: `tests/vulca/pipeline/test_layer_cap.py` (create)

- [ ] **Step 1: Confirm current ceilings**

```bash
grep -n "layers" src/vulca/cli.py | grep -iE "max|limit|choices|range|<=|>="
grep -n "max_layers" src/vulca/pipeline/types.py
grep -rn "max_layers" src/vulca/ tests/
```

Document the exact lines and any guard logic (e.g. `if args.layers > 8: ...`) in a scratch note before changing anything.

- [ ] **Step 2: Write the failing test**

```python
# tests/vulca/pipeline/test_layer_cap.py
from vulca.pipeline.types import PipelineInput


def test_pipeline_accepts_up_to_20_layers():
    inp = PipelineInput(subject="x", provider="mock", max_layers=20)
    assert inp.max_layers == 20


def test_cli_accepts_layers_12(monkeypatch, capsys):
    """`vulca create --layers 12` must not error at argparse level."""
    from vulca.cli import main
    # Parse-only: use --help or a dry-run flag if available; otherwise call
    # the argparse parser directly via the module's build_parser() helper.
    import argparse
    from vulca.cli import _build_parser  # adjust if symbol differs
    parser = _build_parser()
    args = parser.parse_args(["create", "test-subject", "--layers", "12"])
    assert args.layers == 12
```

If the project has no exposed `_build_parser`, the test can instead assert against `subprocess.run([sys.executable, "-m", "vulca", "create", "--help"])` looking for the new range, or bypass argparse by instantiating PipelineInput directly.

Run: `pytest tests/vulca/pipeline/test_layer_cap.py -x` — must fail.

- [ ] **Step 3: Lift the caps**

In `src/vulca/cli.py`, remove any `choices=[...]` / clamp logic that restricts `--layers` to ≤8. Raise the accepted range to `1..20` (inclusive); add a help string that documents the new range.

In `src/vulca/pipeline/types.py`, raise the `max_layers` default field constraint (if any) to 20. If the current default value is 3, keep it (default != ceiling); the point is to remove the ceiling, not change the default.

- [ ] **Step 4: Verify tests pass**

```bash
pytest tests/vulca/pipeline/test_layer_cap.py -x
pytest tests/ -q  # full suite — must have no new failures
```

- [ ] **Step 5: Commit**

```
git add src/vulca/cli.py src/vulca/pipeline/types.py tests/vulca/pipeline/test_layer_cap.py
git commit -m "feat(pipeline): lift 8-layer cap to 20 — Phase 0 prerequisite

Phase 0 multi-layer foundation targets 10–20 layers per image.
The previous cap of 8 in cli.py and pipeline/types.py blocked that
goal. Default max_layers unchanged; only the ceiling is lifted."
```

**Acceptance:**
- `PipelineInput(max_layers=20)` constructs without error.
- `vulca create --layers 12` parses successfully.
- Full test suite still green (no new failures; pre-existing failures unchanged).

---

### Task 1: Add `semantic_path` field to LayerInfo

**Files:**
- Modify: `src/vulca/layers/types.py:12-47`
- Test: `tests/vulca/layers/test_manifest_semantic_path.py` (create)

> **Exact insertion point (verified 2026-04-14):** Add the new field **immediately after `content_type: str = "background"` at line 19** (before `dominant_colors`). All subsequent fields already have defaults, so dataclass ordering is safe. Grep `LayerInfo\(` with no `name=` first argument before editing; none found as of review, so positional constructions won't break.
> Insertion shape: `semantic_path: str = ""   # dot-notation hierarchy, e.g. "subject.face.eyes"`.
>
> **Amendment 2026-04-15 (as-built):** Field was placed at the end of the dataclass (after `coverage`, commit 85a89bb) rather than immediately after `content_type`. Rationale: semantic-adjacency to `coverage` (both are free-form text emitted by the VLM planner) and avoidance of churn in the content_type block. Functionally equivalent — all LayerInfo fields have defaults and codebase AST scan confirms no positional-argument callers. Manifest ordering is driven by explicit key lists in `write_manifest` / `load_manifest`, so this position has no serialization impact.

- [ ] **Step 1: Write the failing test**

```python
# tests/vulca/layers/test_manifest_semantic_path.py
from vulca.layers.types import LayerInfo


def test_semantic_path_defaults_to_empty_string():
    info = LayerInfo(name="bg", description="", z_index=0)
    assert info.semantic_path == ""


def test_semantic_path_accepts_dotted_hierarchy():
    info = LayerInfo(
        name="bg",
        description="",
        z_index=0,
        semantic_path="subject.face.eyes",
    )
    assert info.semantic_path == "subject.face.eyes"


def test_semantic_path_preserves_existing_fields():
    info = LayerInfo(name="bg", description="d", z_index=5, semantic_path="x.y")
    assert info.name == "bg"
    assert info.z_index == 5
    assert info.content_type == "background"  # default unchanged
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/vulca/layers/test_manifest_semantic_path.py::test_semantic_path_defaults_to_empty_string -v`
Expected: FAIL with `AttributeError: 'LayerInfo' object has no attribute 'semantic_path'`

- [ ] **Step 3: Add field to dataclass**

Edit `src/vulca/layers/types.py`. After the `coverage: str = ""` line (~line 47), add:

```python
    # v0.16 multi-layer: dot-notation hierarchical path (e.g. "subject.face.eyes",
    # "person[0].hair"). Free-form, not enum. Empty string for legacy 3-layer manifests.
    # The coarse `content_type` field above remains authoritative for catch-all/branch
    # logic; `semantic_path` is for rendering, UI grouping, and prompt provenance.
    semantic_path: str = ""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/vulca/layers/test_manifest_semantic_path.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/types.py tests/vulca/layers/test_manifest_semantic_path.py
git commit -m "feat(layers): add semantic_path field to LayerInfo

Dot-notation hierarchical path for multi-layer decomposition
(e.g. subject.face.eyes, person[0].hair). Defaults empty for
backward compat."
```

**Acceptance:**
- `pytest tests/vulca/layers/test_manifest_semantic_path.py -v` shows the new tests PASS.
- `grep -n 'semantic_path' src/vulca/layers/types.py` returns exactly one line with default `""`.
- `LayerInfo(name="x", description="", z_index=0).semantic_path == ""` at a Python REPL.

---

### Task 2: Round-trip `semantic_path` through manifest

**Files:**
- Modify: `src/vulca/layers/manifest.py` — writer per-layer dict at `:84` (needs new `"semantic_path"` key alongside `content_type`); loader `LayerInfo(...)` construction at `:124-129` (needs `semantic_path=ld.get("semantic_path", "")` kwarg). The `:129,:154` `.get("content_type", "background")` default fallbacks are NOT touched by this task — they remain as-is.
- Test: `tests/vulca/layers/test_manifest_semantic_path.py` (add)

- [ ] **Step 1: Write the failing round-trip test**

Append to `tests/vulca/layers/test_manifest_semantic_path.py`:

```python
import tempfile
from pathlib import Path
from vulca.layers.manifest import write_manifest, load_manifest


def test_semantic_path_round_trips_through_manifest():
    with tempfile.TemporaryDirectory() as td:
        layers = [
            LayerInfo(name="bg", description="", z_index=0,
                      semantic_path="background.catch_all"),
            LayerInfo(name="face", description="", z_index=30,
                      semantic_path="subject.face.skin"),
        ]
        write_manifest(layers, output_dir=td, width=100, height=100)
        loaded = load_manifest(td)
        paths = {l.info.name: l.info.semantic_path for l in loaded.layers}
        assert paths["bg"] == "background.catch_all"
        assert paths["face"] == "subject.face.skin"


def test_legacy_manifest_without_semantic_path_loads_with_empty_string():
    import json
    with tempfile.TemporaryDirectory() as td:
        # Write a manifest that doesn't include semantic_path (simulates legacy)
        manifest = {
            "version": 3, "width": 100, "height": 100,
            "source_image": "", "split_mode": "extract",
            "tradition": "", "partial": False, "warnings": [],
            "created_at": "2026-04-14T00:00:00Z",
            "layers": [{
                "id": "layer_001", "name": "bg", "description": "",
                "z_index": 0, "blend_mode": "normal",
                "content_type": "background", "visible": True,
                "locked": False, "file": "bg.png",
                "dominant_colors": [], "regeneration_prompt": "",
                "opacity": 1.0, "x": 0, "y": 0,
                "width": 100, "height": 100, "rotation": 0,
                "content_bbox": None, "position": "", "coverage": "",
            }],
        }
        Path(td, "manifest.json").write_text(json.dumps(manifest))
        loaded = load_manifest(td)
        assert loaded.layers[0].info.semantic_path == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/vulca/layers/test_manifest_semantic_path.py::test_semantic_path_round_trips_through_manifest -v`
Expected: FAIL — the written manifest won't have `semantic_path`, loader returns default `""`.

- [ ] **Step 3: Update manifest writer**

Edit `src/vulca/layers/manifest.py`. In `write_manifest` around line 98–100, inside the layer dict comprehension, add `"semantic_path": info.semantic_path,` after the `"coverage": info.coverage,` line. The block becomes:

```python
                "position": info.position,
                "coverage": info.coverage,
                "semantic_path": info.semantic_path,
```

- [ ] **Step 4: Update manifest loader (V2+ branch)**

Edit `src/vulca/layers/manifest.py:122-144`. In the `if version >= 2:` branch, after the `coverage=item.get("coverage", "") or "",` line, add:

```python
                semantic_path=item.get("semantic_path", ""),
```

- [ ] **Step 5: Update manifest loader (V1 migration branch)**

Edit the V1 migration block (`else:` branch around line 146). The V1 `LayerInfo(...)` call won't include `semantic_path`; since it defaults to `""` the V1 branch needs no changes. Add a comment:

```python
            # V1: migrate — semantic_path defaults to "" (multi-layer schema
            # didn't exist in V1; legacy content_type remains authoritative).
```

Add this comment just above the `info = LayerInfo(` in the V1 branch.

- [ ] **Step 6: Run all manifest tests**

Run: `pytest tests/vulca/layers/test_manifest_semantic_path.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 7: Run full layers test suite to check regressions**

Run: `pytest tests/vulca/layers/ -v --tb=short -x`
Expected: No NEW failures (pre-existing cv2/litellm-related failures are OK; they come from unrelated missing deps).

- [ ] **Step 8: Commit**

```bash
git add src/vulca/layers/manifest.py tests/vulca/layers/test_manifest_semantic_path.py
git commit -m "feat(manifest): round-trip semantic_path for multi-layer schema

Writer emits semantic_path in V3 layer dicts; loader tolerates
missing field on legacy manifests (defaults to empty string)."
```

**Acceptance:**
- All round-trip tests in `test_manifest_semantic_path.py` PASS.
- `json.loads(manifest_text)["layers"][0]` contains a `"semantic_path"` key after write.
- Loading a legacy V3 manifest (no `semantic_path`) yields `LayerInfo.semantic_path == ""`.

---

### Task 3: Create `coarse_bucket` module

**Files:**
- Create: `src/vulca/layers/coarse_bucket.py`
- Test: `tests/vulca/layers/test_coarse_bucket.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/vulca/layers/test_coarse_bucket.py
from vulca.layers.coarse_bucket import coarse_bucket_of, is_background


def test_exact_background_is_background():
    assert coarse_bucket_of("background") == "background"


def test_dotted_background_is_background():
    assert coarse_bucket_of("background.catch_all") == "background"
    assert coarse_bucket_of("background.sky") == "background"


def test_exact_subject_is_subject():
    assert coarse_bucket_of("subject") == "subject"


def test_dotted_subject_is_subject():
    assert coarse_bucket_of("subject.face.eyes") == "subject"


def test_person_indexed_is_subject():
    assert coarse_bucket_of("person[0].face") == "subject"
    assert coarse_bucket_of("person[3].hair") == "subject"


def test_unknown_bucket_returns_as_is():
    # Unknown prefixes are returned verbatim so callers can decide;
    # this makes the function side-effect-free and predictable.
    assert coarse_bucket_of("detail") == "detail"
    assert coarse_bucket_of("atmosphere") == "atmosphere"


def test_empty_string_defaults_to_background():
    # Empty string commonly appears for legacy/V1 manifests; treat as background
    # so catch-all logic survives the migration.
    assert coarse_bucket_of("") == "background"


def test_false_positive_background_noise_is_subject():
    # "background_noise" (with underscore) must NOT match background bucket —
    # it's a subject-level detail, not a catch-all.
    assert coarse_bucket_of("background_noise") == "background_noise"


def test_is_background_helper():
    assert is_background("background") is True
    assert is_background("background.catch_all") is True
    assert is_background("subject") is False
    assert is_background("person[0].face") is False
    assert is_background("background_noise") is False
    assert is_background("") is True  # legacy default
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/vulca/layers/test_coarse_bucket.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.layers.coarse_bucket'`

- [ ] **Step 3: Create module**

```python
# src/vulca/layers/coarse_bucket.py
"""Coarse bucket extraction for multi-layer content_type values.

Multi-layer schema uses dot-notation (subject.face.eyes) and indexed
namespaces (person[0].hair). Call sites that branch on bucket membership
must use coarse_bucket_of() so they don't break when the layer name
gains hierarchy.

Design note: buckets are identified by prefix match on the segment before
the first '.' or '['. Non-matching prefixes are returned verbatim so
callers can decide what to do (rather than hiding unknowns behind a
fallback bucket).
"""
from __future__ import annotations

import logging

_logger = logging.getLogger("vulca.layers.coarse_bucket")
_SEEN_UNKNOWN: set[str] = set()


def _warn_unknown_bucket(head: str) -> None:
    """Log once per unique unknown head so VLM drift stays visible without
    flooding logs in a hot loop. Gated on logger level (WARNING by default)."""
    if head in _SEEN_UNKNOWN:
        return
    _SEEN_UNKNOWN.add(head)
    _logger.warning("coarse_bucket: unknown head %r (not in _KNOWN_BUCKETS)", head)


# Known coarse buckets. Unknown values pass through unchanged.
_KNOWN_BUCKETS = frozenset({
    "background",
    "subject",
    "foreground",
    "midground",
    "detail",
    "atmosphere",
    "effect",
    "text",
    "line_art",
    "color_wash",
    "color_block",
    "decoration",
})

# Prefixes that normalize to a different bucket name. The person[i] namespace
# is the standard way to namespace group-portrait subjects: they are still
# subjects for branching purposes.
_PREFIX_ALIASES = {
    "person": "subject",
}


def coarse_bucket_of(content_type: str) -> str:
    """Extract the coarse bucket from a possibly-dotted content_type.

    >>> coarse_bucket_of("background.catch_all")
    'background'
    >>> coarse_bucket_of("subject.face.eyes")
    'subject'
    >>> coarse_bucket_of("person[0].hair")
    'subject'
    >>> coarse_bucket_of("background_noise")
    'background_noise'
    >>> coarse_bucket_of("")
    'background'
    """
    if not content_type:
        return "background"  # legacy/V1 default

    # Split on both '.' and '[' to extract the leading segment.
    first_dot = content_type.find(".")
    first_bracket = content_type.find("[")
    if first_dot == -1 and first_bracket == -1:
        head = content_type
    else:
        cut = min(p for p in (first_dot, first_bracket) if p != -1)
        head = content_type[:cut]

    if head in _PREFIX_ALIASES:
        return _PREFIX_ALIASES[head]
    if head not in _KNOWN_BUCKETS:
        # Unknown head — emit one debug log per unique value so the caller
        # can notice VLM drift, but still return verbatim so downstream
        # code can make its own decision (e.g. plan prompt may emit new
        # buckets that Phase 1 then elevates to _KNOWN_BUCKETS).
        _warn_unknown_bucket(head)
    return head


def is_background(content_type: str) -> bool:
    """True if the content_type belongs to the background bucket.

    Use this at every call site that currently checks
    `info.content_type == "background"`.
    """
    return coarse_bucket_of(content_type) == "background"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/vulca/layers/test_coarse_bucket.py -v`
Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/coarse_bucket.py tests/vulca/layers/test_coarse_bucket.py
git commit -m "feat(layers): add coarse_bucket_of for multi-layer content_type

Extracts coarse bucket (background/subject/foreground/...) from
dotted or indexed content_type values (subject.face.eyes,
person[0].hair). Used to replace 17 hardcoded content_type branches (see Task 4)
checks in downstream tasks."
```

**Acceptance:**
- `pytest tests/vulca/layers/test_coarse_bucket.py -v` all PASS.
- `coarse_bucket_of("subject.face.eyes") == "subject"`; `is_background("background.catch_all") is True`.
- Unknown heads log one WARNING on first occurrence; subsequent occurrences silent (dedup via `_SEEN_UNKNOWN`).

---

### Task 4: Replace 17 hardcoded `content_type` branching sites (9 `==` + 8 `!=`/literal)

**Files:**
- Modify: `src/vulca/layers/sam.py:126`
- Modify: `src/vulca/layers/sam3.py:88` and `:130`
- Modify: `src/vulca/layers/split.py:245` and `:267`
- Modify: `src/vulca/layers/alpha.py:86`
- Modify: `src/vulca/layers/layered_generate.py:319`
- Modify: `src/vulca/pipeline/nodes/layer_generate.py:348`
- Modify: `src/vulca/pipeline/nodes/plan_layers.py:112`
- Test: `tests/vulca/layers/test_catch_all_callsites.py`

- [ ] **Step 1: Write a failing integration test**

```python
# tests/vulca/layers/test_catch_all_callsites.py
"""Verify catch-all behavior for dotted content_type across all split modes.

Regression test for multi-layer schema: a layer named 'background.catch_all'
must be treated as background (fill unclaimed pixels) rather than as a
named foreground layer.
"""
from __future__ import annotations

import numpy as np
from PIL import Image
from vulca.layers.types import LayerInfo
from vulca.layers.coarse_bucket import is_background


def test_is_background_matches_dotted_content_type():
    info = LayerInfo(name="bg", description="", z_index=0,
                     content_type="background.catch_all")
    assert is_background(info.content_type) is True


def test_is_background_rejects_subject_face_eyes():
    info = LayerInfo(name="eyes", description="", z_index=45,
                     content_type="subject.face.eyes")
    assert is_background(info.content_type) is False


def test_is_background_rejects_person_indexed():
    info = LayerInfo(name="face", description="", z_index=30,
                     content_type="person[0].face")
    assert is_background(info.content_type) is False
```

- [ ] **Step 2: Verify test is green (it should be; `is_background` is already implemented)**

Run: `pytest tests/vulca/layers/test_catch_all_callsites.py -v`
Expected: All 3 tests PASS. This locks the contract.

- [ ] **Step 3: Update sam.py**

Edit `src/vulca/layers/sam.py`. At the top, after the existing imports, add:

```python
from vulca.layers.coarse_bucket import is_background
```

Then line 126 — change:

```python
        if info.content_type == "background":
```

to:

```python
        if is_background(info.content_type):
```

- [ ] **Step 4: Update sam3.py (2 sites)**

Edit `src/vulca/layers/sam3.py`. Add the import at the top:

```python
from vulca.layers.coarse_bucket import is_background
```

Replace both line 88 and line 130 the same way:

```python
        if info.content_type == "background":
```
becomes
```python
        if is_background(info.content_type):
```

- [ ] **Step 5: Update split.py (2 sites)**

Edit `src/vulca/layers/split.py`. Add import at top:

```python
from vulca.layers.coarse_bucket import is_background
```

Replace line 245 and line 267 the same way.

- [ ] **Step 6: Update alpha.py**

Edit `src/vulca/layers/alpha.py`. Add import at top:

```python
from vulca.layers.coarse_bucket import is_background
```

Replace line 86 the same way.

- [ ] **Step 7: Update layered_generate.py**

Edit `src/vulca/layers/layered_generate.py`. Add import at top:

```python
from vulca.layers.coarse_bucket import is_background
```

Replace line 319. Note: this file checks `layer.content_type` (not `info.content_type`), so the substitution is:

```python
        if layer.content_type == "background":
```
becomes
```python
        if is_background(layer.content_type):
```

- [ ] **Step 8: Update pipeline/nodes/layer_generate.py**

Edit `src/vulca/pipeline/nodes/layer_generate.py`. Add import at top:

```python
from vulca.layers.coarse_bucket import is_background
```

Replace line 348 the same way.

- [ ] **Step 9: Update pipeline/nodes/plan_layers.py**

Edit `src/vulca/pipeline/nodes/plan_layers.py`. Add import at top:

```python
from vulca.layers.coarse_bucket import is_background
```

Replace line 112. The original is inside a generator:

```python
            if not any(l.content_type == "background" for l in layers):
```
becomes
```python
            if not any(is_background(l.content_type) for l in layers):
```

- [ ] **Step 10: Verify all sites are updated**

Run: `grep -rn 'content_type == "background"' src/vulca/ || echo "NONE REMAINING"`
Expected output: `NONE REMAINING`

- [ ] **Step 11: Run full layers test suite**

Run: `pytest tests/vulca/layers/ -v --tb=short`
Expected: All NEW tests PASS. Pre-existing cv2/litellm import failures are unchanged.

- [ ] **Step 12: Commit**

```bash
git add src/vulca/layers/sam.py src/vulca/layers/sam3.py \
        src/vulca/layers/split.py src/vulca/layers/alpha.py \
        src/vulca/layers/layered_generate.py \
        src/vulca/pipeline/nodes/layer_generate.py \
        src/vulca/pipeline/nodes/plan_layers.py \
        tests/vulca/layers/test_catch_all_callsites.py
git commit -m "refactor(layers): use is_background helper at 9 call sites

Replace hardcoded content_type == 'background' checks with
is_background() from coarse_bucket. Dotted content_type values
like 'background.catch_all' now route correctly through all
split modes (sam/sam3/vlm/regenerate/extract) and alpha/pipeline
nodes."
```

**Acceptance:**
- All 17 sites listed in amendments now go through `is_background(...)` or `coarse_bucket_of(...)` — verify: `grep -nE '== *"background"|!= *"background"' src/vulca/layers/ src/vulca/pipeline/nodes/ | grep -v 'coarse_bucket.py'` returns 0 matches.
- `pytest tests/vulca/layers/test_catch_all_callsites.py -v` PASS; full layer test suite no new regressions.
- A layer named `background.catch_all` now correctly acts as the catch-all in every split mode.

---

### Task 4b: Propagate `semantic_path` through outer surfaces (CLI / MCP / ops / artifact / prompts / existing tests)

**Motivation:** Task 1–2 add `semantic_path` to `LayerInfo` and manifest JSON. Task 4 fixes 17 internal branching sites. But the field has to reach those places from the user in the first place. This task wires `semantic_path` through every API boundary so users can set it, round-trip it, and have it survive edits. Without Task 4b, the field exists but is unreachable from outside the migrate script.

**Files (Modify):**
- `src/vulca/cli.py` — `layers_add` parser (~line 220 region, identified by the `layers_sub.add_parser("add", ...)` call)
- `src/vulca/layers/ops.py:57` — `add_layer()` signature + body
- `src/vulca/mcp_server.py` — `layers_edit` tool signature + body (identified by the `@mcp.tool()` `async def layers_edit(...)` near line ~1110)
- `src/vulca/layers/artifact.py` — V3 loader (identified by the `for ld in data.get("layers", []):` loop)
- `src/vulca/layers/prompt.py` — `ANALYZE_PROMPT` schema + "3-10 layers" wording
- `src/vulca/layers/plan_prompt.py` — plan prompt schema + "3-8 layers" wording
- `tests/test_layers_v2_types.py` — update expectations
- `tests/test_layers_v2_manifest.py` — update expectations
- `tests/vulca/pipeline/nodes/test_plan_layers.py` — if present (grep to confirm)

**Files (Create):**
- `tests/vulca/layers/test_layers_add_semantic_path.py`
- `tests/vulca/layers/test_artifact_semantic_path_roundtrip.py`
- `tests/vulca/layers/test_prompt_schema_semantic_path.py`

**Dependencies:** Requires Tasks 1 and 2 (LayerInfo + manifest round-trip). Produces no new import for Task 5+; Task 4b is a leaf surface-only task.

- [ ] **Step 1: CLI — `layers add --semantic-path`**

> **Plan-rot notes (verified 2026-04-14):**
> - `src/vulca/cli.py` does **NOT** expose a `_build_parser` symbol; the parser is local to `main(argv)` at line 60 and parses at line 314. Tests must either (a) invoke `main([...])` with `SystemExit`-safe args, or (b) use `subprocess.run([sys.executable, "-m", "vulca", ...])` and assert against `--help` output.
> - There is **no `_cmd_layers_add`**. The dispatcher is `_cmd_layers(args)` at `src/vulca/cli.py:1276` with an inline `if args.layers_command == "add":` branch; it imports `add_layer` at line 1423 and calls it at line 1425. Task 4b must add `semantic_path=args.semantic_path` to **that call site** (~line 1425), not a fictional `_cmd_layers_add`.

Write failing test first (subprocess form, avoids the missing `_build_parser`):

```python
# tests/vulca/layers/test_layers_add_semantic_path.py
import subprocess, sys


def _cli(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "vulca", *args],
        capture_output=True, text=True,
    )


def test_layers_add_help_lists_semantic_path():
    """`vulca layers add --help` must expose --semantic-path."""
    result = _cli("layers", "add", "--help")
    assert result.returncode == 0
    assert "--semantic-path" in result.stdout


def test_layers_add_semantic_path_roundtrips_to_manifest(tmp_path):
    """End-to-end: adding a layer with --semantic-path persists it to manifest.json."""
    import json
    from pathlib import Path
    from PIL import Image

    # Seed a minimal artwork dir: blank source PNG + manifest referencing it.
    # NOTE: `source_image` must point to a real file on disk — the current
    # `load_manifest` path reads it to derive dimensions in some code paths.
    # Pre-verify by: grep "source_image" src/vulca/layers/manifest.py src/vulca/layers/ops.py
    src_png = tmp_path / "src.png"
    Image.new("RGBA", (64, 64), (0, 0, 0, 0)).save(src_png)
    (tmp_path / "manifest.json").write_text(json.dumps({
        "version": 3, "width": 64, "height": 64, "layers": [],
        "source_image": str(src_png), "split_mode": "",
    }))
    r = _cli(
        "layers", "add", str(tmp_path),
        "--name", "eyes",
        "--semantic-path", "subject.face.eyes",
        "--content-type", "subject",   # explicit to avoid parser default drift
    )
    assert r.returncode == 0, f"stderr={r.stderr}"
    data = json.loads((tmp_path / "manifest.json").read_text())
    eyes = next(l for l in data["layers"] if l["name"] == "eyes")
    assert eyes.get("semantic_path") == "subject.face.eyes"
```

Then in `src/vulca/cli.py`, on the `layers_add` parser block (near line 222), add:
```python
layers_add.add_argument(
    "--semantic-path",
    default="",
    help="Hierarchical dot-notation label, e.g. 'subject.face.eyes' or 'person[0].hair'",
)
```

And in `_cmd_layers` at `src/vulca/cli.py:~1425`, where the `add` branch calls `add_layer(...)`, add the kwarg:
```python
result = add_layer(
    artwork,
    artwork_dir=args.artwork_dir,
    name=args.name,
    description=args.description,
    z_index=args.z_index,
    content_type=args.content_type,
    semantic_path=args.semantic_path,   # NEW
)
```

- [ ] **Step 2: `ops.add_layer()` — accept and persist `semantic_path`**

Failing test:

> **Plan-rot note (verified):** `LayeredArtwork` at `src/vulca/layers/types.py:59–66` has fields `composite_path`, `layers`, `manifest_path` — there is no `width`/`height`. Dimensions live on `manifest.json`. The test must seed a manifest.json with width/height and construct `LayeredArtwork(composite_path="", layers=[], manifest_path=str(tmp_path/"manifest.json"))`.

```python
# tests/vulca/layers/test_artifact_semantic_path_roundtrip.py (partial)
import json
from vulca.layers.ops import add_layer
from vulca.layers.types import LayeredArtwork


def _seed_artwork(tmp_path):
    """Write a minimal manifest.json so ops.add_layer has dimensions to read."""
    (tmp_path / "manifest.json").write_text(json.dumps({
        "version": 3, "width": 512, "height": 512, "layers": [],
        "source_image": "", "split_mode": "",
    }))
    return LayeredArtwork(
        composite_path="",
        layers=[],
        manifest_path=str(tmp_path / "manifest.json"),
    )


def test_add_layer_accepts_semantic_path(tmp_path):
    """add_layer stores semantic_path on the new LayerInfo."""
    artwork = _seed_artwork(tmp_path)
    result = add_layer(
        artwork, artwork_dir=str(tmp_path),
        name="eyes", description="eye detail",
        content_type="subject",
        semantic_path="subject.face.eyes",
    )
    assert result.info.semantic_path == "subject.face.eyes"


def test_add_layer_semantic_path_defaults_empty(tmp_path):
    artwork = _seed_artwork(tmp_path)
    result = add_layer(
        artwork, artwork_dir=str(tmp_path),
        name="sky", description="sky",
    )
    assert result.info.semantic_path == ""
```

In `src/vulca/layers/ops.py:57` signature, add after `content_type`:
```python
semantic_path: str = "",
```
and pass it into the `LayerInfo(...)` construction ten lines below.

- [ ] **Step 3: MCP `layers_edit` — accept and forward `semantic_path`**

Failing test: mock an artwork_dir, call `layers_edit(operation="add", name="x", semantic_path="subject.face.eyes", ...)`, assert the persisted manifest has the field.

In `src/vulca/mcp_server.py`, update the `layers_edit` signature (line ~1107) to add:
```python
semantic_path: str = "",
```
and forward it when `operation == "add"` to the `add_layer(...)` call at line ~1144. Update the docstring Args to document the new parameter.

**Also update the MCP return payload** at `mcp_server.py:~1148`: add `"semantic_path": result.info.semantic_path` to the dict returned for `operation == "add"`. Without this, MCP clients cannot confirm the field round-tripped; add an assertion in the failing test that the returned dict contains the field.

- [ ] **Step 4: Artifact V3 loader — populate `semantic_path`**

Failing test (tight): write an artifact.json with a layer entry that has `"semantic_path": "subject.face.eyes"`, load via the V3 loader, assert `layer.info.semantic_path == "subject.face.eyes"`. Also test that a legacy entry without the field loads with `semantic_path=""`.

In `src/vulca/layers/artifact.py`, inside the `for ld in data.get("layers", []):` loop where `LayerInfo(...)` is constructed, add:
```python
semantic_path=ld.get("semantic_path", ""),
```
Place it next to the other `.get()` calls — keep alphabetical or grouping convention used in surrounding lines.

**Also update the WRITER side.** Task 1+2 already ensure `write_manifest` writes `semantic_path`. `artifact.py` has its own writer `write_artifact_v3` at `src/vulca/layers/artifact.py:13` (verified), which serializes per-layer dicts at the `json.dumps(artifact, ...)` site around line 80. Locate the per-layer dict construction inside `write_artifact_v3` and add:
```python
"semantic_path": layer.info.semantic_path,
```
next to the other per-layer fields. Add a failing test that round-trips a `LayerInfo(..., semantic_path="subject.face.eyes")` through `write_artifact_v3` → re-read via the V3 loader → asserts the field survived.

**Also fix `parse_v2_response` in `src/vulca/layers/prompt.py:75`.** This function constructs `LayerInfo(...)` from VLM-returned dicts and is the main path through which the analyze prompt's output becomes layer metadata. If it doesn't read `semantic_path` from the raw dict, the field advertised in Step 5's updated prompt will be silently dropped. Add:
```python
semantic_path=raw.get("semantic_path", ""),
```
to the `LayerInfo(...)` construction inside the loop. Add a unit test that feeds a dict with `semantic_path` and asserts the parsed `LayerInfo` carries it.

- [ ] **Step 5: Analyze prompt schema — advertise `semantic_path` and raise layer ceiling**

Failing test:

```python
# tests/vulca/layers/test_prompt_schema_semantic_path.py
from vulca.layers.prompt import build_analyze_prompt


def test_analyze_prompt_documents_semantic_path():
    p = build_analyze_prompt()
    assert "semantic_path" in p


def test_analyze_prompt_mentions_high_layer_ceiling():
    p = build_analyze_prompt()
    # Accept either "10-20" or "3-20" wording — just ensure ceiling >=12.
    import re
    m = re.search(r"(\d+)\s*-\s*(\d+)\s+layers", p, re.I)
    assert m is not None, f"layer range not found in prompt: {p[:200]}"
    assert int(m.group(2)) >= 12
```

Update `ANALYZE_PROMPT` in `src/vulca/layers/prompt.py`:
- Change "3-10 layers depending on complexity" to "3-20 layers depending on complexity (detail-heavy portraits or group scenes may use 12-20)".
- Add `"semantic_path": "optional dot-notation hierarchical label, e.g. 'subject.face.eyes' or 'person[0].hair' (empty string if not hierarchical)"` to the per-layer schema block.

Update `src/vulca/layers/plan_prompt.py` analogously: raise "3-8 layers" to "3-20 layers (use 12-20 for detail-heavy scenes)" and add `semantic_path` to the schema.

- [ ] **Step 6: Update existing tests if they break on the new field**

> **Plan-rot note (verified):**
> - `tests/test_layers_v2_types.py:9` asserts **default field values**, not constructor shape. `semantic_path=""` default will pass unchanged.
> - `tests/test_layers_v2_manifest.py:42` asserts **selected V2 fields are written**, not that unknown fields are rejected. Adding a new field shouldn't break it.
> Don't edit these tests preemptively. Only repair if they fail after Steps 1–5.

Run:
```bash
pytest tests/ -k "layer" -q
```
Repair any pre-existing test that actually breaks on the new field's presence. Each repair must preserve original intent; do not broaden an assertion that was narrowing a bug.

**Out-of-scope LayerInfo construction sites (note, don't fix here):** these construct `LayerInfo` without `semantic_path` but default-empty is acceptable for now — document in commit message:
- `src/vulca/pipeline/nodes/plan_layers.py:96` (`_mock_plan`) and `:113, :118` (`_validate`)
- `src/vulca/layers/redraw.py:191` (merge — semantic_path of merged layers is dropped; defer a merge-policy decision to a later phase)
- `scripts/experiment_layer_fixes.py:38`, `scripts/generate-e2e-demo.py:659` (experimental / demo scripts)

Commit boundary: one commit per step is fine, or bundle steps 1+2+3 (API propagation) / 4+5 (persistence + prompt) / 6 (test repair) into three commits.

- [ ] **Step 7: Verify — full suite + schema exposure**

```bash
pytest tests/vulca/layers/ -q           # new tests
pytest tests/ -q                        # no regressions
vulca layers add --help | grep -i semantic-path      # CLI exposure
```

**Acceptance:**
- CLI `layers add --semantic-path` round-trips into manifest.
- MCP `layers_edit` with `semantic_path` arg round-trips.
- V3 artifact load/save preserves `semantic_path` unchanged.
- Both analyze + plan prompts mention `semantic_path` and allow ≥12 layers.
- All pre-existing layer tests still pass (with assertions updated, not deleted).

---

### Task 5: Create image_loader with pre-resize for giant images

**Files:**
- Create: `src/vulca/layers/image_loader.py`
- Test: `tests/vulca/layers/test_image_loader.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/vulca/layers/test_image_loader.py
import numpy as np
from pathlib import Path
from PIL import Image
from vulca.layers.image_loader import imread_safe, resize_to_max


def test_imread_safe_returns_rgb_ndarray(tmp_path):
    p = tmp_path / "small.jpg"
    Image.new("RGB", (100, 200), "red").save(p, "JPEG")
    arr, scale = imread_safe(p, max_dim=1024)
    assert arr.shape == (200, 100, 3)
    assert arr.dtype == np.uint8
    assert scale == 1.0


def test_imread_safe_resizes_giant_images(tmp_path):
    # Simulate a "giant" image by creating one bigger than max_dim
    p = tmp_path / "giant.jpg"
    Image.new("RGB", (5000, 3000), "blue").save(p, "JPEG")
    arr, scale = imread_safe(p, max_dim=1024)
    # Long side capped at 1024; short side scaled proportionally
    assert max(arr.shape[:2]) == 1024
    assert scale == 1024 / 5000


def test_imread_safe_raises_on_missing_file(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        imread_safe(tmp_path / "nonexistent.jpg")


def test_resize_to_max_keeps_aspect_ratio():
    arr = np.zeros((3000, 5000, 3), dtype=np.uint8)
    resized = resize_to_max(arr, max_dim=1000)
    assert resized.shape == (600, 1000, 3)


def test_resize_to_max_noop_when_smaller():
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    resized = resize_to_max(arr, max_dim=1000)
    assert resized.shape == (100, 100, 3)
    # Should be the same array (not a copy)
    assert resized is arr
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/vulca/layers/test_image_loader.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Create the module**

```python
# src/vulca/layers/image_loader.py
"""Safe image loading with pre-resize for giant source images.

Used by EVF-SAM scripts and any pipeline that handles arbitrary-resolution
inputs. Las Meninas at 26065x30000 decoded to float32 is ~9 GB.

IMPORTANT LIMITATION: cv2.imread fully decodes the BGR buffer to uint8
(~2.3 GB for 26k×30k) BEFORE this helper can resize. That's large but
usually survivable on a 16+ GB machine; the ~9 GB blow-up only occurs
when a downstream caller converts to float32. This helper prevents THAT
second blow-up by capping dimensions before any downstream float
conversion. It does NOT prevent OOM during raw cv2 decode — if that
becomes a real problem, switch to PIL.Image.open + thumbnail (which
can decode-and-resize lazily) in a follow-up.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def imread_safe(
    path: str | Path,
    *,
    max_dim: int = 4096,
) -> tuple[np.ndarray, float]:
    """Read an image and resize if longest side exceeds max_dim.

    Args:
        path: Image file path.
        max_dim: Maximum allowed longest side. Default 4096 keeps most
            modern TIFFs under control while still preserving enough
            pixels for SAM-class inference.

    Returns:
        (rgb_ndarray, scale) where scale is the factor applied (1.0 if no resize).

    Raises:
        FileNotFoundError: if the file doesn't exist or can't be read.

    Note:
        Resize happens AFTER cv2 decodes the full uint8 BGR buffer. OOM
        protection applies only to downstream float32 conversions, not
        to the initial decode. See module docstring.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {p}")

    bgr = cv2.imread(str(p))
    if bgr is None:
        raise FileNotFoundError(f"cv2 could not decode image: {p}")

    h, w = bgr.shape[:2]
    longest = max(h, w)
    scale = 1.0
    if longest > max_dim:
        scale = max_dim / longest
        new_w, new_h = int(w * scale), int(h * scale)
        bgr = cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return rgb, scale


def resize_to_max(arr: np.ndarray, *, max_dim: int) -> np.ndarray:
    """Resize a HxWxC ndarray so its longest side <= max_dim.

    Returns the same array if already small enough (no copy).
    """
    h, w = arr.shape[:2]
    longest = max(h, w)
    if longest <= max_dim:
        return arr
    scale = max_dim / longest
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(arr, (new_w, new_h), interpolation=cv2.INTER_AREA)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/vulca/layers/test_image_loader.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/image_loader.py tests/vulca/layers/test_image_loader.py
git commit -m "feat(layers): add imread_safe with pre-resize for giant images

Las Meninas 26065x30000 decoded to float32 ~9GB; capping long side
before decode prevents OOM. Returns (arr, scale) so callers can
map mask coordinates back to original resolution if needed."
```

**Acceptance:**
- `pytest tests/vulca/layers/test_image_loader.py -v` all PASS.
- `imread_safe(path)` on a 5000×3000 fixture returns `scale < 1.0` and `max(arr.shape[:2]) == max_dim`.
- `imread_safe(path)` on a 1024×1024 fixture returns `scale == 1.0` (pass-through).

---

### Task 6: Create decomp_validator

**Files:**
- Create: `src/vulca/layers/decomp_validator.py`
- Test: `tests/vulca/layers/test_decomp_validator.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/vulca/layers/test_decomp_validator.py
import numpy as np
import pytest
from vulca.layers.decomp_validator import (
    validate_decomposition,
    DecompositionValidationError,
)


def _binary(mask: np.ndarray) -> np.ndarray:
    """Helper: convert bool mask to uint8 0/255."""
    return (mask.astype(np.uint8)) * 255


def test_validator_passes_for_perfect_partition():
    # 4x4 canvas divided into 2 non-overlapping masks that together cover everything
    a = np.zeros((4, 4), dtype=bool)
    a[:, :2] = True
    b = np.zeros((4, 4), dtype=bool)
    b[:, 2:] = True
    report = validate_decomposition([_binary(a), _binary(b)])
    assert report.coverage == 1.0
    assert report.overlap == 0.0
    assert report.holes == 0
    assert report.overlaps == 0


def test_validator_fails_on_hole():
    # Leave one pixel uncovered
    a = np.zeros((4, 4), dtype=bool)
    a[:, :2] = True
    b = np.zeros((4, 4), dtype=bool)
    b[:, 2:] = True
    b[0, 2] = False  # hole
    with pytest.raises(DecompositionValidationError) as exc:
        validate_decomposition([_binary(a), _binary(b)], strict=True)
    assert "coverage" in str(exc.value).lower()


def test_validator_fails_on_overlap():
    # Two masks both claim the same pixel
    a = np.zeros((4, 4), dtype=bool)
    a[:, :3] = True
    b = np.zeros((4, 4), dtype=bool)
    b[:, 2:] = True  # column 2 is claimed by both
    with pytest.raises(DecompositionValidationError) as exc:
        validate_decomposition([_binary(a), _binary(b)], strict=True)
    assert "overlap" in str(exc.value).lower()


def test_validator_non_strict_returns_report_without_raising():
    a = np.zeros((4, 4), dtype=bool)
    a[:, :2] = True
    # b doesn't cover the right half — coverage will be 0.5
    b = np.zeros((4, 4), dtype=bool)
    report = validate_decomposition([_binary(a), _binary(b)], strict=False)
    assert report.coverage == pytest.approx(0.5)
    assert report.holes == 8  # 4x4 minus 8 covered


def test_validator_tolerates_small_coverage_epsilon():
    # 100x100 with a single uncovered pixel — coverage = 0.9999
    # Default epsilon is 1e-4, so 1 pixel out of 10000 should pass
    a = np.ones((100, 100), dtype=bool)
    a[0, 0] = False  # 1 hole
    report = validate_decomposition([_binary(a)], strict=True, epsilon=1e-3)
    assert report.coverage < 1.0
    # Does not raise because 0.0001 < 1e-3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/vulca/layers/test_decomp_validator.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Create the module**

```python
# src/vulca/layers/decomp_validator.py
"""Post-decomposition invariant checks.

Guarantees:
    coverage == 1.0 (every pixel belongs to exactly one layer)
    overlap == 0.0 (no two layers claim the same pixel)

Use this at the end of every decomposition pipeline (extract/vlm/evfsam/
tile) to fail loudly on broken masks rather than silently producing
invalid composites.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class DecompositionValidationError(ValueError):
    """Raised when a layer decomposition violates coverage or overlap invariant."""


@dataclass
class DecompositionReport:
    coverage: float    # fraction of canvas pixels claimed by at least one layer
    overlap: float     # fraction of canvas pixels claimed by 2+ layers
    holes: int         # absolute pixel count of unclaimed pixels
    overlaps: int      # absolute pixel count of multiply-claimed pixels
    canvas_size: int   # total pixels


def validate_decomposition(
    masks: list[np.ndarray],
    *,
    strict: bool = True,
    epsilon: float = 1e-4,
) -> DecompositionReport:
    """Validate that a set of binary masks partition the canvas perfectly.

    Args:
        masks: List of uint8 HxW arrays (values 0 or 255; threshold is > 127)
            OR bool HxW arrays. Must all have the same shape. Float arrays
            and 3D arrays are NOT supported and will produce incorrect counts
            silently — add an `isinstance` / `ndim==2` guard at the call site
            if your pipeline can emit those.
        strict: If True, raise DecompositionValidationError on violation.
            If False, return the report without raising.
        epsilon: Tolerance for both coverage AND overlap comparisons.
            Default 1e-4 allows ~1 pixel per 10000 to be uncovered or
            overlapped (useful for rounding artifacts at image boundaries).

    Returns:
        DecompositionReport with coverage, overlap, and counts.

    Strict semantics (unambiguous):
        Two independent checks are performed in this order; first violation
        raises. A decomposition is rejected when either
            coverage < 1 - epsilon
        OR  overlap  > epsilon
        ("equal to epsilon" passes in both cases — strict `<` and `>`).

    Raises:
        DecompositionValidationError: if strict=True and coverage or overlap
            violates the thresholds above.
        ValueError: if masks list is empty or shapes don't match.
    """
    if not masks:
        raise ValueError("masks list is empty")

    first_shape = masks[0].shape
    for i, m in enumerate(masks[1:], start=1):
        if m.shape != first_shape:
            raise ValueError(
                f"mask shape mismatch: masks[0]={first_shape}, masks[{i}]={m.shape}"
            )

    h, w = first_shape
    canvas_size = h * w

    # Vote counting: how many masks claim each pixel
    votes = np.zeros(first_shape, dtype=np.uint16)
    for m in masks:
        if m.dtype == bool:
            votes += m.astype(np.uint16)
        else:
            votes += (m > 127).astype(np.uint16)

    covered = votes >= 1
    multiply_claimed = votes >= 2
    coverage = float(covered.sum()) / canvas_size
    overlap = float(multiply_claimed.sum()) / canvas_size
    holes = int((~covered).sum())
    overlaps = int(multiply_claimed.sum())

    report = DecompositionReport(
        coverage=coverage,
        overlap=overlap,
        holes=holes,
        overlaps=overlaps,
        canvas_size=canvas_size,
    )

    if strict:
        if coverage < 1.0 - epsilon:
            raise DecompositionValidationError(
                f"coverage {coverage:.4f} below 1.0 - {epsilon} "
                f"({holes} unclaimed pixels out of {canvas_size})"
            )
        if overlap > epsilon:
            raise DecompositionValidationError(
                f"overlap {overlap:.4f} exceeds {epsilon} "
                f"({overlaps} multiply-claimed pixels out of {canvas_size})"
            )

    return report
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/vulca/layers/test_decomp_validator.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/vulca/layers/decomp_validator.py tests/vulca/layers/test_decomp_validator.py
git commit -m "feat(layers): add decomp_validator for coverage/overlap invariants

Post-decomposition validator guarantees coverage==1 and overlap==0.
Fails loudly via DecompositionValidationError rather than silently
producing broken composites."
```

**Acceptance:**
- `pytest tests/vulca/layers/test_decomp_validator.py -v` all PASS.
- `validate_decomposition([non_covering_masks], strict=True)` raises with substring `"coverage"`.
- `validate_decomposition([overlapping_masks], strict=True)` raises with substring `"overlap"`.
- `strict=False` returns a `DecompositionReport` without raising, even on violation.

---

### Task 7: Rewrite migrate_evfsam_to_layers with z-index driven resolution

> **Plan-rot note (verified 2026-04-14):** `_z_index_for(name)` **already exists** at `scripts/migrate_evfsam_to_layers.py:27-29` with body `return Z_INDEX.get(layer_name, 99)`. This task **extends** — it does not create — the helper.
> Current behavior: exact-name lookup only. Dotted names like `"subject.face.eyes"` fall through to the default `99`. The extension must:
> 1. First try exact-name lookup (preserves existing behavior for non-dotted names like `"sky"`).
> 2. On miss, extract the **coarse bucket** via `coarse_bucket_of(name)` from Task 3 and look up that bucket in `Z_INDEX`.
> 3. Still fall through to `99` only if both lookups miss.
> Add a unit test that asserts `_z_index_for("subject.face.eyes")` resolves to `Z_INDEX["subject"]` (or equivalent), not `99`.

**Files:**
- Modify: `scripts/migrate_evfsam_to_layers.py` — extend `_z_index_for` at `:27-29`; rewrite overlap-resolution block at `:107-138` to use the new `resolve_masks_zindex` helper.

- [ ] **Step 1: Write a failing test for the new behavior**

Create `tests/vulca/scripts/test_migrate_overlap_resolution.py`:

```python
"""Unit test for z-index driven overlap resolution in migrate script.

The migrate script's resolve_masks_zindex must:
 1. Clear higher-z masks from lower-z (foreground beats subject beats background).
 2. Fill unclaimed pixels into the layer whose content_type is_background.
 3. Work for arbitrary layer counts, not just 3.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pytest

# The helper lives in the migrate script; import via path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))
from migrate_evfsam_to_layers import resolve_masks_zindex  # noqa: E402


def _mask(h: int, w: int, *, y1: int = 0, y2: int | None = None) -> np.ndarray:
    m = np.zeros((h, w), dtype=bool)
    m[y1:y2, :] = True
    return m


def test_resolve_three_layers_higher_z_wins():
    """bg (z=0), subj (z=30), fg (z=80). fg wins over subj which wins over bg."""
    h, w = 10, 10
    bg = np.ones((h, w), dtype=bool)         # bg covers everything
    subj = _mask(h, w, y1=3, y2=8)          # middle rows
    fg = _mask(h, w, y1=5, y2=7)            # inside middle

    layers = [
        {"name": "bg", "z": 0, "content_type": "background", "mask": bg},
        {"name": "subj", "z": 30, "content_type": "subject", "mask": subj},
        {"name": "fg", "z": 80, "content_type": "foreground", "mask": fg},
    ]
    out = resolve_masks_zindex(layers)
    assert (out["fg"] == fg).all()
    # subj loses fg's pixels
    assert not (out["subj"] & out["fg"]).any()
    # bg loses both subj and fg
    assert not (out["bg"] & (out["subj"] | out["fg"])).any()
    # But bg still covers everything else
    assert (out["bg"] | out["subj"] | out["fg"]).sum() == h * w


def test_resolve_fills_unclaimed_into_background():
    """If EVF-SAM masks don't cover the whole canvas, bg must fill the gap."""
    h, w = 10, 10
    bg = np.zeros((h, w), dtype=bool)  # EVF-SAM missed the bg entirely
    subj = _mask(h, w, y1=3, y2=7)
    layers = [
        {"name": "bg", "z": 0, "content_type": "background", "mask": bg},
        {"name": "subj", "z": 50, "content_type": "subject", "mask": subj},
    ]
    out = resolve_masks_zindex(layers)
    # bg now covers everything subj doesn't
    assert (out["bg"] | out["subj"]).all()
    assert not (out["bg"] & out["subj"]).any()


def test_resolve_many_layers_portrait():
    """20-layer portrait: overlap resolution generalizes."""
    h, w = 20, 20
    rng = np.random.default_rng(42)
    layers = []
    for i in range(20):
        name = f"layer_{i}"
        mask = rng.random((h, w)) < 0.3  # each claims ~30% of canvas
        layers.append({
            "name": name, "z": i * 5,
            "content_type": "background" if i == 0 else f"subject.layer_{i}",
            "mask": mask,
        })
    out = resolve_masks_zindex(layers)
    # Invariants
    stack = np.zeros((h, w), dtype=np.uint16)
    for name in out:
        stack += out[name].astype(np.uint16)
    assert (stack == 1).all(), "some pixel is claimed by 0 or 2+ layers"


def test_dotted_background_is_catch_all():
    """A layer named background.catch_all must still fill unclaimed pixels."""
    h, w = 10, 10
    bg = np.zeros((h, w), dtype=bool)
    subj = _mask(h, w, y1=2, y2=8)
    layers = [
        {"name": "bg", "z": 0, "content_type": "background.catch_all", "mask": bg},
        {"name": "subj", "z": 30, "content_type": "subject.face", "mask": subj},
    ]
    out = resolve_masks_zindex(layers)
    assert (out["bg"] | out["subj"]).all()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/vulca/scripts/test_migrate_overlap_resolution.py -v`
Expected: FAIL with `ImportError: cannot import name 'resolve_masks_zindex'`.

- [ ] **Step 3: Open the script and locate the hardcoded block**

Read `scripts/migrate_evfsam_to_layers.py` lines 107–138. It currently has:

```python
        # Resolve layer priority: foreground > subject > background
        # (higher z_index claims pixels first)
        if "foreground" in masks:
            if "subject" in masks:
                masks["subject"] &= ~masks["foreground"]
            if "background" in masks:
                masks["background"] &= ~masks["foreground"]
        if "subject" in masks and "background" in masks:
            masks["background"] &= ~masks["subject"]

        # Fill unclaimed pixels into background (catch-all)
        if "background" in masks:
            ...
```

- [ ] **Step 4: Extract `resolve_masks_zindex` helper**

Replace the entire block at lines 107–138 with a call to a new module-level function. First, add the function (before `main()`, after `make_manifest`):

```python
def resolve_masks_zindex(layers: list[dict]) -> dict[str, np.ndarray]:
    """Resolve overlaps between layer masks by z-index.

    Higher z_index wins: each layer's mask is cleared of all pixels claimed
    by any higher-z layer. After overlap resolution, any unclaimed pixels
    are filled into the is_background layer (if one exists).

    Args:
        layers: list of dicts with REQUIRED keys ``name`` (str), ``z`` (int),
            ``content_type`` (str), ``mask`` (HxW bool ndarray). The optional
            key ``semantic_path`` (str) is tolerated and ignored by this
            helper — it flows through Task 1/2/10 separately. Extra keys
            are ignored.

    Returns:
        dict name -> bool mask with 100% coverage and 0% overlap.

    Tiebreaker:
        When two layers share the same ``z``, the one appearing **earlier
        in the input list** wins contested pixels. Sort is stable
        (Python's ``sorted``), but callers should not rely on dict/JSON
        ordering since iteration order there is not guaranteed across
        Python versions for dicts loaded from JSON on <3.7. For a
        deterministic tiebreaker independent of input order, pass layers
        pre-sorted by name or include the input index explicitly.

    Raises:
        ValueError: on empty input or mismatched mask shapes.
    """
    from vulca.layers.coarse_bucket import is_background

    if not layers:
        raise ValueError("layers list is empty")

    first_shape = layers[0]["mask"].shape
    for i, l in enumerate(layers):
        if l["mask"].shape != first_shape:
            raise ValueError(
                f"layer {i} ({l['name']!r}) mask shape "
                f"{l['mask'].shape} != first shape {first_shape}"
            )

    # Sort by z DESCENDING (highest first). Stable sort preserves input
    # order for same-z ties — see Tiebreaker in docstring.
    ordered = sorted(layers, key=lambda l: -l["z"])
    out: dict[str, np.ndarray] = {}

    # Track which pixels have been claimed by higher-z layers
    claimed = np.zeros(first_shape, dtype=bool)

    for layer in ordered:
        mask = layer["mask"] & ~claimed
        out[layer["name"]] = mask
        claimed |= mask

    # Find the catch-all background layer (lowest z_index that is_background)
    bg_candidates = [l for l in layers if is_background(l["content_type"])]
    if bg_candidates:
        bg_layer = min(bg_candidates, key=lambda l: l["z"])
        unclaimed = ~claimed
        out[bg_layer["name"]] = out[bg_layer["name"]] | unclaimed

    return out
```

> **Task 7 testing note:** add a unit test `test_resolve_tiebreaker_is_input_order` that constructs two layers at the same z with overlapping masks, and asserts the first-in-input-list wins. Also add `test_resolve_raises_on_shape_mismatch`.

- [ ] **Step 5: Replace the inline block with a call**

Replace lines 107–138 (the old hardcoded block) with:

```python
        from vulca.layers.mask import apply_mask_to_image
        import numpy as np
        from PIL import Image

        # Load alpha masks
        orig_img = Image.open(ORIG / f"{stem}.jpg")
        raw_masks: dict[str, np.ndarray] = {}
        layer_info: list[dict] = []
        for name, prompt in prompts:
            im = np.array(Image.open(src / f"{name}.png"))
            raw_masks[name] = im[:, :, 3] > 10
            layer_info.append({
                "name": name,
                "z": _z_index_for(name),
                "content_type": name,  # use name as coarse bucket for now
                "mask": raw_masks[name],
            })

        # Z-index driven overlap resolution + catch-all background
        resolved = resolve_masks_zindex(layer_info)

        # Validate
        from vulca.layers.decomp_validator import validate_decomposition
        mask_list = [resolved[n] for n, _ in prompts]
        report = validate_decomposition(mask_list, strict=True)
        print(f"  coverage={report.coverage:.4f} overlap={report.overlap:.4f}")

        # Save resolved masks
        for name, _ in prompts:
            mask_u8 = (resolved[name] * 255).astype(np.uint8)
            mask_pil = Image.fromarray(mask_u8, mode="L")
            layer = apply_mask_to_image(orig_img, mask_pil)
            layer.save(str(dst / f"{name}.png"))
```

- [ ] **Step 6: Run migrate test**

Run: `pytest tests/vulca/scripts/test_migrate_overlap_resolution.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 7: Smoke test the script end-to-end**

Run: `/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/MacOS/Python scripts/migrate_evfsam_to_layers.py`
Expected: 8 images migrated, no validation error.

- [ ] **Step 8: Commit**

```bash
git add scripts/migrate_evfsam_to_layers.py tests/vulca/scripts/test_migrate_overlap_resolution.py
git commit -m "refactor(migrate): z-index driven overlap resolution

Replace hardcoded fg>subj>bg chain with resolve_masks_zindex that
generalizes to 10-20 layers. Find catch-all via is_background
(not string match). Run validate_decomposition after migration."
```

**Acceptance:**
- `pytest tests/vulca/scripts/test_migrate_overlap_resolution.py -v` all PASS including the new tie-breaker and shape-mismatch tests.
- `_z_index_for("subject.face.eyes")` returns `Z_INDEX["subject"]` (not the default 99).
- Running the migrate script on the 8-image showcase prints `coverage=1.0000 overlap=0.0000` for every image; any validation failure halts the script.

---

### Task 8: Update `_evfsam_common.py` to use image_loader

> **Plan-rot note (verified 2026-04-14):** `imread_rgb(path) -> np.ndarray` at `scripts/_evfsam_common.py:73` must change signature to return `(arr, scale)` (tuple). This BREAKS two existing callers that unpack a bare ndarray:
> - `scripts/evfsam_showcase.py:66` — unpacks as ndarray.
> - `scripts/evfsam_tile_longscroll.py:67` — unpacks as ndarray.
> Both must be updated in the same commit as the signature change, or tests will fail with `TypeError: cannot unpack non-iterable numpy.ndarray object`. Alternative: keep `imread_rgb` returning only `arr` for backward compat, and add a new `imread_rgb_scaled(path) -> (arr, scale)` that `evfsam_showcase.py` migrates to in Task 9. Decide here before coding; the plan currently assumes the breaking change.

**Files:**
- Modify: `scripts/_evfsam_common.py` — replace `imread_rgb` with delegation to `image_loader.imread_safe`.
- Modify: `scripts/evfsam_showcase.py:66` — update call site.
- Modify: `scripts/evfsam_tile_longscroll.py:67` — update call site.

- [ ] **Step 1: Write a failing test**

```python
# tests/vulca/scripts/test_evfsam_common_uses_image_loader.py
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))
from _evfsam_common import imread_rgb  # noqa: E402


def test_imread_rgb_returns_rgb_and_scale(tmp_path):
    p = tmp_path / "small.jpg"
    Image.new("RGB", (100, 100), "red").save(p, "JPEG")
    result = imread_rgb(p)
    # After the refactor, imread_rgb returns the RGB array AND the scale factor
    assert isinstance(result, tuple) and len(result) == 2
    arr, scale = result
    assert arr.shape[2] == 3
    assert scale == 1.0


def test_imread_rgb_resizes_giant(tmp_path):
    p = tmp_path / "giant.jpg"
    Image.new("RGB", (5000, 4000), "blue").save(p, "JPEG")
    arr, scale = imread_rgb(p, max_dim=1024)
    assert max(arr.shape[:2]) == 1024
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/vulca/scripts/test_evfsam_common_uses_image_loader.py -v`
Expected: FAIL — current `imread_rgb` returns only the array, not a tuple.

- [ ] **Step 3: Rewrite imread_rgb**

Edit `scripts/_evfsam_common.py`. Replace the existing `imread_rgb` with:

```python
def imread_rgb(path: Path, *, max_dim: int = 4096) -> tuple[np.ndarray, float]:
    """Read BGR image, convert to RGB, resize if longer side exceeds max_dim.

    Delegates to vulca.layers.image_loader.imread_safe so all scripts share
    the same pre-resize policy. Returns (rgb_ndarray, scale_factor).

    Raises FileNotFoundError if missing or unreadable.
    """
    from vulca.layers.image_loader import imread_safe
    return imread_safe(path, max_dim=max_dim)
```

Remove the `cv2` import from `_evfsam_common.py` top-level if no other function uses it (a quick grep in the file will confirm).

- [ ] **Step 4: Update callers in scripts**

Two callers need the scale value now:

`scripts/evfsam_showcase.py` around line 60 currently does:
```python
    image_full = imread_rgb(img_path)
```
Change to:
```python
    image_full, _ = imread_rgb(img_path, max_dim=4096)
```

`scripts/evfsam_tile_longscroll.py` around line 51:
```python
    image_np = imread_rgb(img_path)
```
Change to:
```python
    image_np, _ = imread_rgb(img_path, max_dim=4096)
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/vulca/scripts/test_evfsam_common_uses_image_loader.py -v`
Expected: Both tests PASS.

- [ ] **Step 6: Smoke test both scripts**

Run: `/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/MacOS/Python -c "from _evfsam_common import imread_rgb; import sys; sys.path.insert(0, 'scripts'); arr, scale = imread_rgb('assets/showcase/originals/earthrise.jpg'); print(arr.shape, scale)"` (from the repo root)
Expected: prints `(H, W, 3) 1.0` for Earthrise (2400x2400 well under 4096).

- [ ] **Step 7: Commit**

```bash
git add scripts/_evfsam_common.py scripts/evfsam_showcase.py \
        scripts/evfsam_tile_longscroll.py \
        tests/vulca/scripts/test_evfsam_common_uses_image_loader.py
git commit -m "refactor(scripts): route imread through image_loader

Unified pre-resize policy across EVF-SAM scripts. imread_rgb now
returns (arr, scale) so downstream mask upsampling can be exact
when source > max_dim."
```

**Acceptance:**
- `imread_rgb(path)` returns a 2-tuple (verified by the new test).
- Both updated callers (`evfsam_showcase.py:66`, `evfsam_tile_longscroll.py:67`) unpack without `TypeError`.
- Smoke-running the script on `earthrise.jpg` prints `(H, W, 3) 1.0` (2400×2400 < 4096 default).

---

### Task 9: Add `--semantic-path` support in EVF-SAM scripts

> **Plan-rot notes (verified 2026-04-14):**
> - `parse_prompt_entry(entry)` **does not exist** in `scripts/evfsam_showcase.py`. This task CREATES it as a new helper returning `(name, prompt, semantic_path)`. **Backward-compat policy (binding):** legacy 2-tuple entries yield `semantic_path = name` (NOT empty string). Rationale: downstream `_z_index_for` performs exact-name lookup — if `semantic_path` is empty, no bucket inference is possible; setting it to `name` keeps the pre-refactor behavior identical. All three places (Step 1 prose, Step 2 tests, Step 4 implementation) must agree on this default.
> - Prompts iteration in the current file: **one** main loop at `evfsam_showcase.py:83` (`for name, prompt in prompts:`) + **one** list comprehension at `:149` (`[(n, p) for n, p in prompts_cfg[stem]]`). Both must be updated to 3-tuple destructuring (via `parse_prompt_entry`).
> - Current argparse at `:123` has only `--force` and `--images`. Plan adds `--semantic-path` as a new CLI-level opt-in flag (optional; default off — existing 2-tuple prompts still work).
> - `evfsam_prompts.json` remains on-disk with 2-tuple entries. Task 9 makes the **loader** tolerant of 3-tuples; the JSON file itself is NOT rewritten by this task. **Persistence of `semantic_path` happens in Task 10**, not here — this task only threads the value through `parse_prompt_entry` and the loops.

**Files:**
- Modify: `scripts/evfsam_showcase.py` — add `parse_prompt_entry` helper, add `--semantic-path` flag, thread the value through the two iteration sites (`:83` and `:149`).
- **NOT modified** by this task: `assets/showcase/experiments/evfsam_prompts.json`. Earlier drafts of this plan listed it in Files; that was phantom — the JSON stays as-is (backward compat).

- [ ] **Step 1: Understand current prompt schema**

Read `assets/showcase/experiments/evfsam_prompts.json`. It currently has:
```json
"earthrise": [
    ["background", "the black empty space around the planet"],
    ...
]
```

Goal: allow an optional third element per tuple for `semantic_path`:
```json
["background", "the black empty space around the planet", "background.catch_all"]
```

Backward compat: when the third element is missing, `semantic_path` defaults to the layer name (current behavior).

- [ ] **Step 2: Write failing test**

```python
# tests/vulca/scripts/test_evfsam_prompt_schema.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))
from evfsam_showcase import parse_prompt_entry  # noqa: E402


def test_parse_two_element_tuple_defaults_semantic_path_to_name():
    name, prompt, path = parse_prompt_entry(["bg", "the sky"])
    assert name == "bg"
    assert prompt == "the sky"
    assert path == "bg"


def test_parse_three_element_tuple_uses_explicit_path():
    name, prompt, path = parse_prompt_entry(["bg", "the sky", "background.sky"])
    assert name == "bg"
    assert prompt == "the sky"
    assert path == "background.sky"


def test_parse_rejects_short_tuple():
    import pytest
    with pytest.raises(ValueError):
        parse_prompt_entry(["bg"])
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/vulca/scripts/test_evfsam_prompt_schema.py -v`
Expected: FAIL with `ImportError: cannot import name 'parse_prompt_entry'`.

- [ ] **Step 4: Add the helper to evfsam_showcase.py**

In `scripts/evfsam_showcase.py`, after the imports, add:

```python
def parse_prompt_entry(entry: list) -> tuple[str, str, str]:
    """Parse a prompt config tuple into (name, prompt, semantic_path).

    Accepts 2-tuple (name, prompt) for legacy compat — semantic_path
    defaults to name. Accepts 3-tuple (name, prompt, semantic_path)
    for the multi-layer schema.
    """
    if len(entry) < 2:
        raise ValueError(f"prompt entry too short: {entry}")
    name = entry[0]
    prompt = entry[1]
    semantic_path = entry[2] if len(entry) >= 3 else name
    return name, prompt, semantic_path
```

- [ ] **Step 5: Use the helper at the two call sites**

Find the two places in `evfsam_showcase.py` that iterate over prompts (currently `for name, prompt in prompts`). Change them to:

```python
        for entry in prompts:
            name, prompt, semantic_path = parse_prompt_entry(entry)
            # ... existing inference body uses `name` and `prompt` as before
```

The `semantic_path` is not yet wired into any output (that's Task 10). For now, just capture it so the variable is available for logging:

```python
            print(f"  [{name}] ({semantic_path}) {prompt!r}")
```

- [ ] **Step 6: Run all tests**

Run: `pytest tests/vulca/scripts/ -v`
Expected: All tests PASS.

- [ ] **Step 7: Commit**

```bash
git add scripts/evfsam_showcase.py tests/vulca/scripts/test_evfsam_prompt_schema.py
git commit -m "feat(evfsam): accept optional semantic_path in prompt config

Prompt entries can now be (name, prompt) for legacy compat or
(name, prompt, semantic_path) for multi-layer schema. semantic_path
defaults to name when omitted."
```

**Acceptance:**
- `pytest tests/vulca/scripts/test_evfsam_prompt_schema.py -v` all PASS.
- `parse_prompt_entry(["bg", "sky"]) == ("bg", "sky", "bg")` (2-tuple fallback = name).
- `parse_prompt_entry(["bg", "sky", "background.sky"]) == ("bg", "sky", "background.sky")`.
- `evfsam_showcase.py` runs both iteration sites (line 83 + comprehension at 149) without KeyError or tuple-unpack errors on the unchanged `evfsam_prompts.json`.

---

### Task 10: Emit `semantic_path` in migrate manifest

> **Plan-rot note (verified 2026-04-14):** Current `make_manifest` at `scripts/migrate_evfsam_to_layers.py:32` takes `list[tuple[str, str]]` and destructures `for layer_name, prompt in prompts:` at `:38`. This task upgrades it to accept **either** 2-tuples (back-compat for unmigrated prompts JSON) **or** 3-tuples where the third element is `semantic_path`. Use a defensive unpack:
> ```python
> for entry in prompts:
>     layer_name, prompt = entry[0], entry[1]
>     semantic_path = entry[2] if len(entry) >= 3 else layer_name   # match Task 9 policy
>     ...
> ```
> The emitted per-layer dict (~line 46) gains `"semantic_path": semantic_path`. 2-tuple callers continue to work; `semantic_path` defaults to `layer_name` — **same policy as `parse_prompt_entry` in Task 9**, do not let them drift.

**Files:**
- Modify: `scripts/migrate_evfsam_to_layers.py:32-67` (`make_manifest` signature + loop + emitted dict)

- [ ] **Step 1: Write failing test**

Append to `tests/vulca/scripts/test_migrate_overlap_resolution.py`:

```python
def test_make_manifest_passes_semantic_path_through():
    from migrate_evfsam_to_layers import make_manifest

    prompts = [
        ("background", "the sky", "background.sky"),
        ("subject", "the person", "subject.body"),
    ]
    # Fake stem so make_manifest can open an image — use one we know exists
    import tempfile
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        from pathlib import Path as _P
        import migrate_evfsam_to_layers as m
        # Patch ORIG to our temp dir
        orig_orig = m.ORIG
        m.ORIG = _P(td)
        try:
            Image.new("RGB", (100, 100), "red").save(_P(td) / "test.jpg", "JPEG")
            manifest = make_manifest("test", prompts)
            paths = {l["name"]: l.get("semantic_path") for l in manifest["layers"]}
            assert paths["background"] == "background.sky"
            assert paths["subject"] == "subject.body"
        finally:
            m.ORIG = orig_orig
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/vulca/scripts/test_migrate_overlap_resolution.py::test_make_manifest_passes_semantic_path_through -v`
Expected: FAIL — `make_manifest` signature only accepts 2-tuples and doesn't emit `semantic_path`.

- [ ] **Step 3: Update `make_manifest`**

In `scripts/migrate_evfsam_to_layers.py`, find `make_manifest` (around line 39). Update:

```python
def make_manifest(stem: str, prompts: list[tuple]) -> dict:
    orig_path = ORIG / f"{stem}.jpg"
    im = Image.open(orig_path)
    w, h = im.size

    layers = []
    for entry in prompts:
        if len(entry) < 2:
            continue
        layer_name = entry[0]
        prompt = entry[1]
        semantic_path = entry[2] if len(entry) >= 3 else layer_name
        layer_id = "layer_" + hashlib.md5(f"{stem}-{layer_name}".encode()).hexdigest()[:8]
        layers.append({
            "id": layer_id,
            "name": layer_name,
            "description": prompt,
            "z_index": _z_index_for(layer_name),
            "blend_mode": "normal",
            "content_type": layer_name,  # coarse bucket derived from name
            "semantic_path": semantic_path,
            "visible": True,
            "locked": False,
            "file": f"{layer_name}.png",
            "dominant_colors": [],
            "regeneration_prompt": prompt,
            "opacity": 1.0,
            "x": 0.0, "y": 0.0,
            "width": 100.0, "height": 100.0,
            "rotation": 0.0,
            "content_bbox": None,
            "position": "",
            "coverage": "",
        })
    return {
        "version": 3,
        "width": w,
        "height": h,
        "source_image": str(orig_path.relative_to(REPO)),
        "split_mode": "evfsam",
        "generation_path": "",
        "layerability": "",
        "tradition": "",
        "partial": False,
        "warnings": [],
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "layers": layers,
    }
```

- [ ] **Step 4: Update main() to pass 3-tuples through**

In `main()`, find the loop that iterates `prompts_cfg.items()`. Change the prompt normalization:

```python
        prompts_raw = prompts_cfg[stem]
        prompts = []
        for entry in prompts_raw:
            if len(entry) < 2:
                continue
            name, prompt = entry[0], entry[1]
            semantic_path = entry[2] if len(entry) >= 3 else name
            prompts.append((name, prompt, semantic_path))
```

Replace subsequent `for name, _ in prompts:` loops with `for name, *_ in prompts:`.

- [ ] **Step 5: Run the test**

Run: `pytest tests/vulca/scripts/test_migrate_overlap_resolution.py -v`
Expected: All tests PASS (including new one).

- [ ] **Step 6: Commit**

```bash
git add scripts/migrate_evfsam_to_layers.py tests/vulca/scripts/test_migrate_overlap_resolution.py
git commit -m "feat(migrate): emit semantic_path in migrated manifests

Backward compat: 2-tuple prompt entries default semantic_path to
layer name. 3-tuple entries pass through explicit path."
```

**Acceptance:**
- `jq '.layers[].semantic_path' <any-migrated-manifest>.json` returns a non-empty string for every layer.
- 2-tuple prompt entries in `evfsam_prompts.json` still migrate cleanly (semantic_path = layer name).
- The emitted JSON schema is forward-compat: the Task 2 loader can round-trip it without modification.

---

### Task 11: End-to-end smoke test on one image

**Files:**
- Test: `tests/vulca/scripts/test_phase0_e2e.py` (create)

- [ ] **Step 1: Write failing integration test**

```python
# tests/vulca/scripts/test_phase0_e2e.py
"""End-to-end smoke test for Phase 0 foundation:
 - semantic_path and content_type are INDEPENDENT fields that both round-trip
 - is_background reads the coarse bucket (via content_type OR semantic_path prefix)
 - resolve_masks_zindex + validate_decomposition integrate cleanly
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))


def test_phase0_end_to_end_multilayer():
    """12-layer portrait decomposition survives migrate + validate + load."""
    from migrate_evfsam_to_layers import resolve_masks_zindex
    from vulca.layers.decomp_validator import validate_decomposition
    from vulca.layers.coarse_bucket import is_background

    h, w = 50, 50
    rng = np.random.default_rng(0)
    # Spec tuple: (name, z, coarse_content_type, semantic_path).
    # IMPORTANT: content_type holds the coarse bucket; semantic_path holds
    # the full dotted hierarchy. They are independent fields — the whole
    # point of Task 1/2/3 is to separate them. Do NOT conflate by setting
    # content_type = semantic_path.
    specs = [
        ("bg",            0,  "background", "background.catch_all"),
        ("body_clothing", 15, "subject",    "subject.body.clothing"),
        ("body_neck",     20, "subject",    "subject.body.neck"),
        ("accessory",     25, "subject",    "subject.accessories.jewelry"),
        ("face_skin",     30, "subject",    "subject.face.skin"),
        ("face_lips",     35, "subject",    "subject.face.lips"),
        ("face_nose",     40, "subject",    "subject.face.nose"),
        ("face_eyes",     45, "subject",    "subject.face.eyes"),
        ("face_brows",    50, "subject",    "subject.face.eyebrows"),
        ("hair",          55, "subject",    "subject.hair"),
        ("headwear",      60, "subject",    "subject.headwear"),
        ("fg_objects",    80, "foreground", "foreground.objects"),
    ]

    layers = []
    for name, z, ct, sp in specs:
        # bg claims nothing initially (EVF-SAM often misses bg); others claim ~10% each.
        if name == "bg":
            mask = np.zeros((h, w), dtype=bool)
        else:
            mask = rng.random((h, w)) < 0.1
        layers.append({
            "name": name, "z": z,
            "content_type": ct,
            "semantic_path": sp,
            "mask": mask,
        })

    resolved = resolve_masks_zindex(layers)
    mask_list = [resolved[s[0]] for s in specs]
    report = validate_decomposition(mask_list, strict=True)

    assert report.coverage == 1.0
    assert report.overlap == 0.0
    # Verify is_background recognizes both the coarse content_type AND
    # the dotted semantic_path — two orthogonal inputs, one bucket.
    assert is_background("background")
    assert is_background("background.catch_all")
    # bg claims all originally-unclaimed pixels
    other_union = np.zeros((h, w), dtype=bool)
    for s in specs[1:]:
        other_union |= resolved[s[0]]
    assert (resolved["bg"] | other_union).all()
```

> **Note for Task 7 implementers:** the `layers` list passed to `resolve_masks_zindex` now includes a `semantic_path` key in addition to `{name, z, content_type, mask}`. Task 7's helper should accept but not require it (use `layer.get("semantic_path", "")`). This keeps the helper forward-compatible without forcing all callers to supply the field.

- [ ] **Step 2: Run the test**

Run: `pytest tests/vulca/scripts/test_phase0_e2e.py -v`
Expected: PASS. If anything imports break, a regression in earlier tasks surfaces here.

- [ ] **Step 3: Commit**

```bash
git add tests/vulca/scripts/test_phase0_e2e.py
git commit -m "test: phase 0 end-to-end smoke for 12-layer portrait

Verifies resolve_masks_zindex + decomp_validator + is_background
compose cleanly for a realistic 12-layer portrait spec."
```

**Acceptance:**
- `pytest tests/vulca/scripts/test_phase0_e2e.py -v` PASSES.
- Test constructs a 12-layer spec with BOTH `content_type` (coarse) and `semantic_path` (full dotted), independently.
- Report reads `coverage == 1.0` and `overlap == 0.0`; `is_background` returns True for both `"background"` and `"background.catch_all"` inputs.

---

### Task 12: Run full suite + rebuild showcase

**Files:** none (verification + side-effect runs)

- [ ] **Step 1: Run entire layers test suite**

Run: `pytest tests/vulca/layers/ tests/vulca/scripts/ -v --tb=short`
Expected: All NEW tests PASS. No regressions vs pre-Phase-0 baseline (pre-existing cv2/litellm import errors are unchanged).

- [ ] **Step 2: Re-migrate existing 8-image showcase**

Run: `/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/MacOS/Python scripts/migrate_evfsam_to_layers.py`
Expected:
```
OK  earthrise: 3 layers + manifest (2400x2400) coverage=1.0000 overlap=0.0000
OK  migrant-mother: ...
...
Migrated 8, skipped 0
```

If any image fails validation, the migrate script should raise and halt. That's the correct behavior — surface the problem instead of silently writing a broken manifest. **This expectation depends on Task 7's insertion of `validate_decomposition(..., strict=True)` in the migrate script. If validation fails here, inspect the Task 7 resolver first before blaming the input data.**

- [ ] **Step 3: Regenerate composite + re-evaluate**

Run: `rm -f assets/showcase/composites/*.png && python3 scripts/run-full-showcase.py --caps 6 2>&1 | tail -10`
Expected: 8/8 composite OK, `DONE` line shows `OK: 8`.

- [ ] **Step 4: Verify composite opacity is 100%**

Use `glob()` instead of a hardcoded stem list — the showcase will grow to 20+ artworks (see `project_vulca_showcase_video`) and any hardcoded list rots immediately:

```python
python3 -c "
from pathlib import Path
from PIL import Image
import numpy as np
composites = sorted(Path('assets/showcase/composites').glob('*-composite.png'))
assert composites, 'No composites found — did Step 3 run?'
for p in composites:
    im = np.array(Image.open(p))
    if im.shape[-1] < 4:
        raise SystemExit(f'{p.stem}: no alpha channel')
    # Coverage: any pixel with alpha > 0 is claimed by some layer. This is
    # the actual bug this step catches — transparent holes in the composite.
    # Do NOT raise the threshold above 0; doing so double-counts the 99.99%
    # floor with anti-aliased edge softness and produces false positives on
    # soft-edged VLM masks.
    covered = (im[:,:,3] > 0).sum() / im[:,:,3].size * 100
    mean_alpha = im[:,:,3].mean()
    status = 'OK' if covered >= 99.99 else 'FAIL'
    print(f'{status} {p.stem}: covered={covered:.2f}%, mean_alpha={mean_alpha:.1f}')
    assert covered >= 99.99, (
        f'{p.stem} composite has transparent holes ({covered:.2f}% coverage). '
        f'Expected >=99.99%.'
    )
"
```
Expected: every composite ≥99.99% (allowing for blend-edge anti-aliasing rounding).

- [ ] **Step 5: Commit any updated showcase artifacts**

```bash
git add assets/showcase/composites/ assets/showcase/layers/
git commit -m "chore(showcase): rebuild composites after Phase 0 refactor

All 8 images pass decomposition validation (coverage=1.0,
overlap=0.0). Composites are 100% opaque."
```

**Acceptance:**
- Full test suite: no new regressions vs pre-Phase-0 baseline (pre-existing cv2/litellm import failures unchanged).
- Step 2 migrate output: `Migrated 8, skipped 0`, every image shows `coverage=1.0000 overlap=0.0000`.
- Step 4 opacity loop: every composite ≥99.99% coverage (by `alpha > 0`); mean_alpha logged per image for visibility.
- Phase-0 deliverable tagline: plan supports a 12-layer portrait end-to-end without any hardcoded `"background"` branching.

---

## Self-Review Checklist (done)

**Spec coverage:** Every item from the spec argument maps to a task:
- "manifest schema upgrade" → Tasks 1, 2
- "content_type prefix matching" → Tasks 3, 4
- "z-index driven overlap resolution" → Task 7
- "pre-resize large images" → Tasks 5, 8
- "VLM-driven prompt generation" → **NOT in Phase 0** — this is deferred to Phase 1 of the broader showcase plan. Phase 0 only prepares the foundation (schema + validator + resolver). Writing a VLM prompt generator is orthogonal and large; the spec argument lists it but Superpowers review flagged it as Phase 1 work.
- "validator" → Task 6

**Placeholder scan:** No `TBD`, `TODO`, or "similar to above" in the plan. Every step has concrete code.

**Type consistency:** `resolve_masks_zindex` takes `list[dict]` with keys `{name, z, content_type, mask}`; same keys in all tests (Task 7) and the end-to-end test (Task 11). `validate_decomposition` takes `list[np.ndarray]` and returns `DecompositionReport`; used consistently in Tasks 6, 7, 11, 12. `imread_rgb` / `imread_safe` returns `(arr, scale)` tuple; callers updated in Task 8. `parse_prompt_entry` returns `(name, prompt, semantic_path)`; used in Task 9 scripts.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-14-multi-layer-foundation.md`.

**Execution mode: INLINE ONLY** (per 2026-04-14 pre-execution review — see amendment #1).

Rationale: Independent review verified that most tasks have direct dependencies or shared-file edits. Only Tasks 5 and 6 are safely parallel. Subagent-Driven dispatch would collide on shared files. Use `superpowers:executing-plans` with checkpoints between tasks.

**Execution order (Inline):** Task 0 → 1 → 2 → 3 → 4 → **4b** → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12.

**Checkpoint gates:** commit after each task; run the full test suite after Tasks 4, **4b**, 7, 11, and 12.
