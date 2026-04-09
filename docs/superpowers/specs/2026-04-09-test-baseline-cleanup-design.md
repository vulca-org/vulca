# Test Baseline Cleanup — Design

**Date:** 2026-04-09
**Status:** Approved
**Scope:** v0.13.3 backlog item 7 — clean up test baseline so `pytest tests/` gives a clean signal on Python 3.11.

## Background

Running `pytest tests/` on Python 3.11 produces 5 collection errors (missing optional deps), 7 test failures (missing deps + stale version assert + event loop flaky), masking real regressions. Goal: zero errors, zero flaky — every failure means a real bug.

## Changes

### 1. Install optional dependencies locally

```bash
/opt/homebrew/bin/pip3.11 install opencv-python-headless fastmcp
```

`torch` is NOT installed (2GB+, SAM3 tests skip via importorskip).

### 2. Add `pytest.importorskip` to tests with optional deps

| File | Missing module | Skip marker |
|---|---|---|
| `tests/test_tool_brushstroke.py` | cv2 | `pytest.importorskip("cv2")` |
| `tests/test_tool_color_gamut.py` | cv2 | `pytest.importorskip("cv2")` |
| `tests/test_tool_composition.py` | cv2 | `pytest.importorskip("cv2")` |
| `tests/test_tool_whitespace.py` | cv2 | `pytest.importorskip("cv2")` |
| `tests/test_mcp_server.py` | fastmcp | `pytest.importorskip("fastmcp")` |
| `tests/test_mcp_studio.py` | fastmcp | `pytest.importorskip("fastmcp")` |
| `tests/test_v012_split_sam3.py` | torch | `pytest.importorskip("torch")` |
| `tests/test_v012_split_vlm.py` | fastmcp | `pytest.importorskip("fastmcp")` |

### 3. Fix event loop flaky test

`tests/vulca/pipeline/nodes/test_layer_generate_capability_routing.py:73`: replace `asyncio.get_event_loop().run_until_complete(...)` with `asyncio.run(...)`.

### 4. Delete stale release test

Remove `tests/test_v060_release.py` — v0.6.0 one-time release checklist, hardcodes `assert __version__ == "0.12.0"`, no current value.

## Non-goals

- No changes to `pyproject.toml` extras groups (already correct).
- No Python 3.9 compatibility fixes (use 3.11 for testing).
- No `torch` installation (too heavy; SAM3 tests skip gracefully).

## Commit plan

Single commit: `fix(tests): clean up test baseline — importorskip + flaky fix + remove stale release test`
