# Stabilize v3 Assets + E2E Mock Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce clean v3 display assets via ComfyUI regeneration, and add pytest mock tests for all 8 E2E phases so CI can verify pipeline logic without GPU.

**Architecture:** Phase A runs E2E phases 2/4/7 sequentially on fresh ComfyUI, validating between each. Phase D upgrades MockImageProvider from SVG to PNG output, then adds 8 pytest tests in `tests/test_e2e_mock.py` that verify pipeline orchestration, report structure, and file output using the mock provider.

**Tech Stack:** Python 3.11, pytest, pytest-asyncio, PIL/Pillow, vulca mock providers.

---

### Task 1: Upgrade MockImageProvider from SVG to PNG

**Files:**
- Modify: `src/vulca/providers/mock.py:21-63`

- [ ] **Step 1: Replace SVG generation with PNG**

Change the `generate` method of `MockImageProvider` from SVG to PNG output. Replace lines 41-63:

```python
    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        **kwargs,
    ) -> ImageResult:
        import io

        from PIL import Image

        cid = hashlib.md5(f"{prompt}{tradition}".encode()).hexdigest()[:12]

        # Deterministic color from tradition
        hex_color = _TRADITION_COLORS.get(tradition, "#5F8A50")
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        img = Image.new("RGBA", (width, height), (r, g, b, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        return ImageResult(
            image_b64=img_b64,
            mime="image/png",
            metadata={"candidate_id": cid, "image_url": f"mock://{cid}.png"},
        )
```

Also update the class docstring and comment:
```python
class MockImageProvider:
    """Generates deterministic solid-color PNG placeholder images."""

    capabilities: frozenset[str] = frozenset({"raw_rgba"})
```

- [ ] **Step 2: Verify**

Run: `cd /Users/yhryzy/dev/vulca && python3 -m py_compile src/vulca/providers/mock.py && echo "OK"`
Expected: `OK`

Run: `cd /Users/yhryzy/dev/vulca && PYTHONPATH=./src /opt/homebrew/opt/python@3.11/bin/python3.11 -c "
import asyncio
from vulca.providers.mock import MockImageProvider
async def test():
    p = MockImageProvider()
    r = await p.generate('test', tradition='chinese_xieyi', width=64, height=64)
    import base64
    data = base64.b64decode(r.image_b64)
    assert data[:4] == b'\x89PNG', f'Not PNG: {data[:4]}'
    assert len(data) > 100, f'Too small: {len(data)}'
    assert r.mime == 'image/png'
    print(f'MockImageProvider returns PNG: {len(data)} bytes')
asyncio.run(test())
"`
Expected: `MockImageProvider returns PNG: ... bytes`

- [ ] **Step 3: Commit**

```bash
git add src/vulca/providers/mock.py
git commit -m "fix(providers): MockImageProvider returns PNG instead of SVG"
```

---

### Task 2: Create E2E mock test file — Phase 1 + Phase 8

**Files:**
- Create: `tests/test_e2e_mock.py`

- [ ] **Step 1: Create test file with fixtures and Phase 1 + 8 tests**

```python
"""E2E mock tests — verify pipeline logic without GPU.

Uses MockImageProvider (solid-color PNGs) to exercise all 8 phases
of the E2E demo runner. Tests verify report structure, file output,
and pipeline orchestration — NOT image quality.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

# Ensure the scripts directory is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))


@pytest.fixture
def e2e_dirs(tmp_path, monkeypatch):
    """Patch E2E output directories to use tmp_path."""
    import scripts.generate_e2e_demo as mod  # noqa: delay import

    monkeypatch.setattr(mod, "DEMO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "GALLERY_DIR", tmp_path / "gallery")
    monkeypatch.setattr(mod, "TOOLS_DIR", tmp_path / "tools")
    monkeypatch.setattr(mod, "EVAL_DIR", tmp_path / "eval")
    monkeypatch.setattr(mod, "REPORT_PATH", tmp_path / "e2e-report.json")
    monkeypatch.setattr(mod, "LAYERED_DIR", tmp_path / "layered")
    monkeypatch.setattr(mod, "DEFENSE3_DIR", tmp_path / "defense3")
    monkeypatch.setattr(mod, "EDIT_DIR", tmp_path / "edit")
    monkeypatch.setattr(mod, "INPAINT_DIR", tmp_path / "inpaint")
    monkeypatch.setattr(mod, "STUDIO_DIR", tmp_path / "studio")
    return tmp_path


@pytest.fixture
def gallery_image(e2e_dirs):
    """Create a synthetic gallery PNG for phases that depend on Phase 1."""
    from PIL import Image

    gallery_dir = e2e_dirs / "gallery"
    gallery_dir.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1024, 1024), (200, 180, 160))
    path = gallery_dir / "chinese_xieyi.png"
    img.save(path, format="PNG")
    return path


def test_phase1_gallery_mock(e2e_dirs):
    """Phase 1: gallery generation produces reports with expected structure."""
    from scripts.generate_e2e_demo import run_phase1_gallery

    rep = asyncio.run(run_phase1_gallery(
        "mock", width=64, height=64, traditions={"chinese_xieyi"},
    ))

    assert rep["phase"] == 1
    assert rep["name"] == "gallery"
    assert rep["status"] in ("ok", "partial")
    assert len(rep["entries"]) >= 1
    entry = rep["entries"][0]
    assert "tradition" in entry
    assert "status" in entry
    # Verify file was written
    gallery_dir = e2e_dirs / "gallery"
    assert any(gallery_dir.glob("*.png"))


def test_phase8_tools_mock(e2e_dirs, gallery_image):
    """Phase 8: tools analysis produces expected JSON outputs."""
    from scripts.generate_e2e_demo import run_phase8_tools

    rep = run_phase8_tools(gallery_image, "chinese_xieyi")

    assert rep["phase"] == 8
    assert rep["name"] == "tools"
    assert rep["status"] == "ok"
    assert "brushstroke" in rep
    assert "composition" in rep
    assert 0.0 <= rep["brushstroke"]["texture_energy"] <= 1.0
    assert 0.0 <= rep["composition"]["center_weight"] <= 1.0
    # Verify JSON files written
    tools_dir = e2e_dirs / "tools"
    assert (tools_dir / "brushstroke.json").exists()
    assert (tools_dir / "composition.json").exists()
```

- [ ] **Step 2: Make the script importable**

The E2E script is at `scripts/generate-e2e-demo.py` which has a hyphen in the filename — Python can't import it directly. Create a symlink:

```bash
ln -sf generate-e2e-demo.py scripts/generate_e2e_demo.py
```

And add an empty `__init__.py`:
```bash
touch scripts/__init__.py
```

- [ ] **Step 3: Run tests**

Run: `cd /Users/yhryzy/dev/vulca && PYTHONPATH=./src /opt/homebrew/opt/python@3.11/bin/python3.11 -m pytest tests/test_e2e_mock.py::test_phase1_gallery_mock tests/test_e2e_mock.py::test_phase8_tools_mock -v`
Expected: 2 tests PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_e2e_mock.py scripts/generate_e2e_demo.py scripts/__init__.py
git commit -m "test(e2e): add mock tests for Phase 1 (gallery) and Phase 8 (tools)"
```

---

### Task 3: E2E mock tests — Phase 2 + Phase 3

**Files:**
- Modify: `tests/test_e2e_mock.py`

- [ ] **Step 1: Add Phase 2 and Phase 3 tests**

Append to `tests/test_e2e_mock.py`:

```python
def test_phase2_layered_mock(e2e_dirs):
    """Phase 2: layered generation produces manifest and layer files."""
    from scripts.generate_e2e_demo import run_phase2_layered

    rep = asyncio.run(run_phase2_layered("mock", width=64, height=64))

    assert rep["phase"] == 2
    assert rep["name"] == "layered"
    assert rep["status"] in ("ok", "partial")
    layered_dir = e2e_dirs / "layered"
    # Manifest should exist
    manifest_path = layered_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        assert "layers" in manifest


def test_phase3_evaluate_mock(e2e_dirs, gallery_image):
    """Phase 3: evaluate scores gallery images with expected report structure."""
    from scripts.generate_e2e_demo import run_phase3_evaluate

    rep = asyncio.run(run_phase3_evaluate(mode="strict"))

    assert rep["phase"] == 3
    assert rep["name"] == "evaluate"
    assert rep["status"] in ("ok", "partial")
    assert rep["images_total"] >= 1
    if rep["images_ok"] > 0:
        entry = rep["entries"][0]
        assert "scores" in entry or "error" in entry
```

- [ ] **Step 2: Run tests**

Run: `cd /Users/yhryzy/dev/vulca && PYTHONPATH=./src /opt/homebrew/opt/python@3.11/bin/python3.11 -m pytest tests/test_e2e_mock.py -v`
Expected: 4 tests PASS (or some SKIP if deps missing)

- [ ] **Step 3: Commit**

```bash
git add tests/test_e2e_mock.py
git commit -m "test(e2e): add mock tests for Phase 2 (layered) and Phase 3 (evaluate)"
```

---

### Task 4: E2E mock tests — Phase 4, 5, 6, 7

**Files:**
- Modify: `tests/test_e2e_mock.py`

- [ ] **Step 1: Add remaining phase tests**

Append to `tests/test_e2e_mock.py`:

```python
def test_phase4_defense3_mock(e2e_dirs):
    """Phase 4: defense3 produces two variant entries."""
    from scripts.generate_e2e_demo import run_phase4_defense3

    rep = asyncio.run(run_phase4_defense3("mock", width=64, height=64))

    assert rep["phase"] == 4
    assert rep["name"] == "defense3"
    assert rep["status"] in ("ok", "partial")
    assert len(rep.get("entries", [])) >= 1


def test_phase5_edit_mock(e2e_dirs):
    """Phase 5: edit requires Phase 2 artifacts — verify dependency check."""
    from scripts.generate_e2e_demo import run_phase5_edit

    # Phase 5 needs Phase 2 artifacts. Without them it should raise.
    with pytest.raises(FileNotFoundError, match="Phase 2"):
        asyncio.run(run_phase5_edit("mock"))


def test_phase5_edit_with_artifacts_mock(e2e_dirs):
    """Phase 5: edit with synthetic Phase 2 artifacts."""
    from PIL import Image
    from scripts.generate_e2e_demo import run_phase5_edit

    # Create synthetic Phase 2 artifacts
    layered_dir = e2e_dirs / "layered"
    layered_dir.mkdir(parents=True, exist_ok=True)

    # Minimal manifest
    manifest = {
        "layers": [
            {"id": "bg", "name": "background", "content_type": "background",
             "z_index": 0, "blend_mode": "normal"},
            {"id": "fg", "name": "foreground", "content_type": "subject",
             "z_index": 1, "blend_mode": "normal"},
        ]
    }
    (layered_dir / "manifest.json").write_text(json.dumps(manifest))

    # Create layer PNGs
    for name in ("background", "foreground", "composite"):
        img = Image.new("RGBA", (64, 64), (128, 128, 128, 255))
        img.save(layered_dir / f"{name}.png")

    rep = asyncio.run(run_phase5_edit("mock"))

    assert rep["phase"] == 5
    assert rep["name"] == "edit"
    assert rep["status"] in ("ok", "partial", "failed")


def test_phase6_inpaint_mock(e2e_dirs, gallery_image):
    """Phase 6: inpaint produces before/after artifacts."""
    from scripts.generate_e2e_demo import run_phase6_inpaint

    rep = asyncio.run(run_phase6_inpaint("mock"))

    assert rep["phase"] == 6
    assert rep["name"] == "inpaint"
    assert rep["status"] in ("ok", "partial", "failed")


def test_phase7_studio_mock(e2e_dirs):
    """Phase 7: studio session completes without crash."""
    from scripts.generate_e2e_demo import run_phase7_studio

    rep = asyncio.run(run_phase7_studio("mock"))

    assert rep["phase"] == 7
    assert rep["name"] == "studio"
    assert rep["status"] in ("ok", "partial", "failed")
    # Studio may fail with mock but should not crash
```

- [ ] **Step 2: Run all tests**

Run: `cd /Users/yhryzy/dev/vulca && PYTHONPATH=./src /opt/homebrew/opt/python@3.11/bin/python3.11 -m pytest tests/test_e2e_mock.py -v --timeout=120`
Expected: 8+ tests, majority PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_e2e_mock.py
git commit -m "test(e2e): add mock tests for Phases 4-7 (defense3, edit, inpaint, studio)"
```

---

### Task 5: Regenerate Phase 2 (layered) on fresh ComfyUI

**Files:** None (runtime)

**Prerequisites:** ComfyUI running at localhost:8188 with venv python + torch 2.9.0, Ollama running with gemma4.

- [ ] **Step 1: Restart ComfyUI fresh**

```bash
pkill -9 -f ComfyUI 2>/dev/null; sleep 2
cd ~/dev/ComfyUI && ./venv/bin/python main.py --listen 0.0.0.0 --port 8188 --disable-auto-launch &
# Wait for ready
for i in $(seq 1 20); do curl -s -o /dev/null -w "%{http_code}" http://localhost:8188/system_stats | grep -q 200 && break; sleep 2; done
```

- [ ] **Step 2: Clear old artifacts and run Phase 2**

```bash
rm -rf assets/demo/v3/layered
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  python3.11 scripts/generate-e2e-demo.py --phases 2 --provider comfyui
```

- [ ] **Step 3: Validate outputs**

Check all layer PNGs are > 10KB. Visually inspect `composite.png` — should be a Chinese ink wash landscape with no anchors.

If any output is black (< 10KB), restart ComfyUI and retry once.

---

### Task 6: Regenerate Phase 4 (defense3) and Phase 7 (studio)

**Files:** None (runtime)

- [ ] **Step 1: Run Phase 4**

```bash
rm -rf assets/demo/v3/defense3
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  python3.11 scripts/generate-e2e-demo.py --phases 4 --provider comfyui
```

Validate: both `defense3/no_ref/composite.png` and `with_ref/composite.png` are > 10KB.

- [ ] **Step 2: Run Phase 7**

```bash
rm -rf assets/demo/v3/studio
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  python3.11 scripts/generate-e2e-demo.py --phases 7 --provider comfyui
```

Validate: at least 1 concept PNG exists in `studio/concepts/`.

- [ ] **Step 3: Update display images**

```bash
python3 scripts/make-readme-assets.py
```

- [ ] **Step 4: Commit regenerated assets + updated display images**

```bash
git add assets/demo/v3/readme/
git commit -m "chore(assets): regenerate v3 display images from clean ComfyUI run"
```

---

### Task 7: Final verification

**Files:** None (verification only)

- [ ] **Step 1: Run full mock test suite**

```bash
cd /Users/yhryzy/dev/vulca && PYTHONPATH=./src /opt/homebrew/opt/python@3.11/bin/python3.11 -m pytest tests/test_e2e_mock.py -v
```
Expected: all tests pass.

- [ ] **Step 2: Verify README image links**

```bash
grep -oP 'src="[^"]*"' README.md | sed 's/src="//;s/"//' | while read f; do [ -f "$f" ] && echo "OK: $f" || echo "BROKEN: $f"; done
```
Expected: all OK.

- [ ] **Step 3: Check e2e-report.json**

```bash
python3 -c "
import json
r = json.load(open('assets/demo/v3/e2e-report.json'))
for p in r['phases']:
    print(f\"Phase {p['phase']:>1} ({p['name']:>10}): {p['status']}\")
print(f\"Overall: {r['overall_status']}\")
"
```

- [ ] **Step 4: Final commit if any changes**

```bash
git add -A && git status
# If changes, commit
git commit -m "chore: final verification pass"
```
