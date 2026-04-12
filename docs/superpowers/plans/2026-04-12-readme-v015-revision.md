# README v0.15.0 Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 3 generation bugs, regenerate clean v3 assets, build a display image production script, and rewrite the README with a 12-section local-first structure.

**Architecture:** Phase 1 fixes 3 bugs (prompt anchor hallucination, background keying, provider validation). Phase 2 regenerates E2E phases 2/4/5/7 to produce clean artifacts. Phase 3 builds `scripts/make-readme-assets.py` to composite 7 display images from v3 artifacts. Phase 4 rewrites README.md.

**Tech Stack:** Python 3.11, PIL/Pillow, ComfyUI/SDXL, Ollama/Gemma4, vulca SDK.

---

### Task 1: Fix A — Remove "ANCHOR" from prompt section headers

**Files:**
- Modify: `src/vulca/layers/layered_prompt.py:81-95`

- [ ] **Step 1: Replace section header strings**

Change lines 81-95 from:
```python
    blocks = [
        "[CANVAS ANCHOR]",
        f"The image MUST be drawn on {canvas_description}.",
        f"The background MUST be the pure canvas color {anchor.canvas_color_hex},",
        "with absolutely no other elements, textures, shading, or borders on the background.",
        "",
        "[CONTENT ANCHOR — exclusivity]",
        "This image ONLY contains the element specified in USER INTENT.",
        f"Do NOT include any of: {others_text}.",
        "",
        "[SPATIAL ANCHOR]",
        f"MUST occupy {pos}, covering approximately {cov} of the canvas area.",
        "Do NOT extend beyond this region.",
        "",
        "[STYLE ANCHOR]",
        style_keywords,
```
to:
```python
    blocks = [
        "[CANVAS]",
        f"The image MUST be drawn on {canvas_description}.",
        f"The background MUST be the pure canvas color {anchor.canvas_color_hex},",
        "with absolutely no other elements, textures, shading, or borders on the background.",
        "",
        "[CONTENT — exclusivity]",
        "This image ONLY contains the element specified in USER INTENT.",
        f"Do NOT include any of: {others_text}.",
        "",
        "[SPATIAL]",
        f"MUST occupy {pos}, covering approximately {cov} of the canvas area.",
        "Do NOT extend beyond this region.",
        "",
        "[STYLE]",
        style_keywords,
```

- [ ] **Step 2: Verify**

Run: `cd /Users/yhryzy/dev/vulca && python3 -m py_compile src/vulca/layers/layered_prompt.py && echo "OK"`
Expected: `OK`

Run: `cd /Users/yhryzy/dev/vulca && python3 -c "
from vulca.layers.layered_prompt import build_anchored_layer_prompt, TraditionAnchor
from vulca.layers.types import LayerInfo
a = TraditionAnchor('#fff', 'white paper', 'ink wash')
l = LayerInfo(name='test', description='test', z_index=0)
p = build_anchored_layer_prompt(l, anchor=a, sibling_roles=[])
assert 'ANCHOR' not in p, f'ANCHOR still in prompt: {p}'
assert '[CANVAS]' in p
assert '[STYLE]' in p
print('No ANCHOR in prompt — OK')
"`
Expected: `No ANCHOR in prompt — OK`

- [ ] **Step 3: Commit**

```bash
git add src/vulca/layers/layered_prompt.py
git commit -m "fix(layers): remove ANCHOR from prompt headers — SDXL paints literal anchors"
```

---

### Task 2: Fix B — Skip keying for background layers

**Files:**
- Modify: `src/vulca/layers/layered_generate.py:300-301`

- [ ] **Step 1: Add content_type guard before keying**

Change lines 300-301 from:
```python
        rgb = np.array(_pil_rgb)
        alpha = keying.extract_alpha(rgb, canvas)
```
to:
```python
        rgb = np.array(_pil_rgb)
        if layer.content_type == "background":
            alpha = np.ones(rgb.shape[:2], dtype=np.float32)
        else:
            alpha = keying.extract_alpha(rgb, canvas)
```

- [ ] **Step 2: Verify**

Run: `cd /Users/yhryzy/dev/vulca && python3 -m py_compile src/vulca/layers/layered_generate.py && echo "OK"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/vulca/layers/layered_generate.py
git commit -m "fix(layers): skip keying for background layers — prevents transparent canvas"
```

---

### Task 3: Fix C — Validate ComfyUI response before returning

**Files:**
- Modify: `src/vulca/providers/comfyui.py:77-84`

- [ ] **Step 1: Add PNG validation after fetching image**

Change lines 77-84 from:
```python
                                img_resp = await client.get(
                                    f"{self.base_url}/view",
                                    params={"filename": img["filename"],
                                            "subfolder": img.get("subfolder", ""),
                                            "type": img.get("type", "output")},
                                )
                                img_b64 = base64.b64encode(img_resp.content).decode()
                                return ImageResult(image_b64=img_b64, mime="image/png",
                                                   metadata={"prompt_id": prompt_id})
```
to:
```python
                                img_resp = await client.get(
                                    f"{self.base_url}/view",
                                    params={"filename": img["filename"],
                                            "subfolder": img.get("subfolder", ""),
                                            "type": img.get("type", "output")},
                                )
                                raw_bytes = img_resp.content
                                if len(raw_bytes) < 1000 or raw_bytes[:4] != b'\x89PNG':
                                    raise ValueError(
                                        f"ComfyUI returned invalid image "
                                        f"({len(raw_bytes)} bytes, "
                                        f"header={raw_bytes[:4]!r})"
                                    )
                                img_b64 = base64.b64encode(raw_bytes).decode()
                                return ImageResult(image_b64=img_b64, mime="image/png",
                                                   metadata={"prompt_id": prompt_id})
```

- [ ] **Step 2: Verify**

Run: `cd /Users/yhryzy/dev/vulca && python3 -m py_compile src/vulca/providers/comfyui.py && echo "OK"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/vulca/providers/comfyui.py
git commit -m "fix(providers): validate ComfyUI PNG response — reject corrupt data"
```

---

### Task 4: Regenerate E2E Phases 2, 5, 4, 7

**Files:** None (runtime, not code changes)

**Prerequisites:** ComfyUI running at localhost:8188, Ollama running with gemma4 loaded.

- [ ] **Step 1: Clear old artifacts**

```bash
rm -rf assets/demo/v3/layered assets/demo/v3/defense3 assets/demo/v3/edit assets/demo/v3/studio
```

- [ ] **Step 2: Regenerate Phase 2 (layered)**

```bash
cd /Users/yhryzy/dev/vulca && \
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  /opt/homebrew/opt/python@3.11/bin/python3.11 scripts/generate-e2e-demo.py --phases 2 --provider comfyui
```
Expected: `→ ok` with 5+ layers in `assets/demo/v3/layered/`

- [ ] **Step 3: Visually inspect Phase 2 artifacts**

Open `assets/demo/v3/layered/composite.png` — should be a Chinese ink wash landscape with NO anchor artifacts. Individual layers should have proper alpha (background fully opaque, subject layers partially transparent).

If artifacts still show anchors, the ANCHOR fix didn't take effect — check that the commit from Task 1 is on the current branch.

- [ ] **Step 4: Regenerate Phase 5 (edit, depends on Phase 2)**

```bash
cd /Users/yhryzy/dev/vulca && \
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  /opt/homebrew/opt/python@3.11/bin/python3.11 scripts/generate-e2e-demo.py --phases 5 --provider comfyui
```
Expected: `→ ok`. `assets/demo/v3/edit/before.png` and `after.png` should differ visually.

- [ ] **Step 5: Regenerate Phase 4 (defense3)**

```bash
cd /Users/yhryzy/dev/vulca && \
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  /opt/homebrew/opt/python@3.11/bin/python3.11 scripts/generate-e2e-demo.py --phases 4 --provider comfyui
```
Expected: `→ ok`. Both `defense3/no_ref/composite.png` and `defense3/with_ref/composite.png` should be real images (not noise).

If layers are still noise, the PNG validation fix (Task 3) should have caused errors instead of silently saving garbage. Check the error output for `ValueError: ComfyUI returned invalid image`.

- [ ] **Step 6: Regenerate Phase 7 (studio)**

```bash
cd /Users/yhryzy/dev/vulca && \
PYTHONPATH=./src VULCA_VLM_MODEL=ollama_chat/gemma4 OLLAMA_API_BASE=http://localhost:11434 \
  /opt/homebrew/opt/python@3.11/bin/python3.11 scripts/generate-e2e-demo.py --phases 7 --provider comfyui
```
Expected: `→ ok` or `→ partial`. Concepts in `studio/concepts/` should be real images. If VLM scoring times out (0% scores), that's acceptable — the images themselves are what matter for the README.

- [ ] **Step 7: Final visual inspection**

Open and verify each key file is a real image (not noise, not anchor):
- `assets/demo/v3/layered/composite.png`
- `assets/demo/v3/defense3/no_ref/composite.png`
- `assets/demo/v3/defense3/with_ref/composite.png`
- `assets/demo/v3/edit/before.png` and `after.png`
- `assets/demo/v3/studio/concepts/c1.png` (at least one concept)

If any are still broken, note which ones failed and fall back to v2 assets for those README sections.

---

### Task 5: Build `scripts/make-readme-assets.py`

**Files:**
- Create: `scripts/make-readme-assets.py`

- [ ] **Step 1: Create the script**

```python
#!/usr/bin/env python3
"""Produce display-quality composite images for README from v3 E2E artifacts."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
V3 = REPO_ROOT / "assets" / "demo" / "v3"
OUT = V3 / "readme"


def _label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, color: str = "#666") -> None:
    """Draw a small label. Uses default font (no external font file needed)."""
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except OSError:
        font = ImageFont.load_default()
    draw.text((x, y), text, fill=color, font=font)


def _arrow(draw: ImageDraw.ImageDraw, x: int, y: int, color: str = "#999") -> None:
    """Draw a right-pointing arrow at (x, y)."""
    draw.text((x, y), "\u2192", fill=color)


def make_gallery_strip() -> Path:
    """5 tradition gallery images in a row."""
    traditions = ["chinese_xieyi", "japanese_traditional", "watercolor",
                  "islamic_geometric", "african_traditional"]
    cell = 200
    gap = 8
    w = cell * len(traditions) + gap * (len(traditions) - 1)
    canvas = Image.new("RGB", (w, cell), (255, 255, 255))

    for i, t in enumerate(traditions):
        src = V3 / "gallery" / f"{t}.png"
        if not src.exists():
            print(f"  [skip] {src} not found")
            continue
        img = Image.open(src).resize((cell, cell), Image.LANCZOS)
        canvas.paste(img, (i * (cell + gap), 0))

    out = OUT / "gallery_strip.png"
    canvas.save(out)
    print(f"  -> {out.relative_to(REPO_ROOT)}")
    return out


def make_layered_exploded() -> Path:
    """5 layers + composite in an exploded horizontal view."""
    layer_names = [
        ("base_rice_paper_texture", "Paper"),
        ("distant_mist_atmosphere", "Mist"),
        ("middle_ground_mountains", "Mountains"),
        ("foreground_cottage_pines", "Cottage"),
        ("calligraphy_and_seal", "Calligraphy"),
    ]
    cell = 160
    gap = 30
    label_h = 25
    n = len(layer_names) + 1  # +1 for composite
    w = cell * n + gap * n
    h = cell + label_h + 20
    canvas = Image.new("RGB", (w, h), (45, 45, 45))
    draw = ImageDraw.Draw(canvas)

    # Checkerboard for transparency visualization
    def _checker(size: int = 160) -> Image.Image:
        c = Image.new("RGB", (size, size))
        for y in range(0, size, 16):
            for x in range(0, size, 16):
                color = (200, 200, 200) if (x // 16 + y // 16) % 2 == 0 else (240, 240, 240)
                for dy in range(16):
                    for dx in range(16):
                        if y + dy < size and x + dx < size:
                            c.putpixel((x + dx, y + dy), color)
        return c

    checker = _checker(cell)

    for i, (fname, label) in enumerate(layer_names):
        src = V3 / "layered" / f"{fname}.png"
        x = i * (cell + gap) + 15
        if src.exists():
            img = Image.open(src).convert("RGBA").resize((cell, cell), Image.LANCZOS)
            bg = checker.copy()
            bg.paste(img, mask=img)
            canvas.paste(bg, (x, 10))
        _label(draw, x + 10, cell + 15, label, color="#ccc")
        if i < len(layer_names) - 1:
            _arrow(draw, x + cell + 5, cell // 2, color="#888")

    # Composite (last slot)
    comp_src = V3 / "layered" / "composite.png"
    x = len(layer_names) * (cell + gap) + 15
    draw.text((x - gap + 5, cell // 2, ), "=", fill="#888")
    if comp_src.exists():
        comp = Image.open(comp_src).convert("RGB").resize((cell, cell), Image.LANCZOS)
        canvas.paste(comp, (x, 10))
    _label(draw, x + 10, cell + 15, "Composite", color="#ccc")

    out = OUT / "layered_exploded.png"
    canvas.save(out)
    print(f"  -> {out.relative_to(REPO_ROOT)}")
    return out


def _make_comparison(left_path: Path, right_path: Path,
                     left_label: str, right_label: str,
                     out_name: str) -> Path:
    """Side-by-side comparison with labels."""
    cell = 400
    gap = 40
    label_h = 30
    w = cell * 2 + gap + 40
    h = cell + label_h + 30
    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    for i, (src, label) in enumerate([(left_path, left_label), (right_path, right_label)]):
        x = 20 + i * (cell + gap)
        if src.exists():
            img = Image.open(src).convert("RGB").resize((cell, cell), Image.LANCZOS)
            canvas.paste(img, (x, label_h))
        _label(draw, x + 10, 5, label, color="#333")

    # Arrow between
    _arrow(draw, 20 + cell + 8, label_h + cell // 2, color="#999")

    out = OUT / out_name
    canvas.save(out)
    print(f"  -> {out.relative_to(REPO_ROOT)}")
    return out


def make_defense3_comparison() -> Path:
    """No-ref vs with-ref composite side by side."""
    return _make_comparison(
        V3 / "defense3" / "no_ref" / "composite.png",
        V3 / "defense3" / "with_ref" / "composite.png",
        "Without style-ref (all parallel)",
        "With style-ref (serial-first, v0.14)",
        "defense3_comparison.png",
    )


def make_edit_comparison() -> Path:
    """Edit before/after side by side."""
    return _make_comparison(
        V3 / "edit" / "before.png",
        V3 / "edit" / "after.png",
        "Before",
        "After (layer redrawn with autumn colors)",
        "edit_comparison.png",
    )


def make_inpaint_comparison() -> Path:
    """Inpaint before/after side by side."""
    return _make_comparison(
        V3 / "inpaint" / "before.png",
        V3 / "inpaint" / "after.png",
        "Original",
        "After (pavilion inpainted, center 30%)",
        "inpaint_comparison.png",
    )


def make_studio_grid() -> Path:
    """4 concepts + final in a row."""
    cell = 200
    gap = 8
    concepts = [V3 / "studio" / "concepts" / f"c{i}.png" for i in range(1, 5)]
    # Final: last round output or studio/final.png
    final = V3 / "studio" / "final.png"
    if not final.exists():
        outputs = sorted((V3 / "studio" / "output").glob("*.png"))
        final = outputs[-1] if outputs else final

    all_imgs = concepts + [final]
    w = cell * 5 + gap * 4 + 40
    h = cell + 40
    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    for i, src in enumerate(all_imgs):
        x = 10 + i * (cell + gap)
        if i == 4:
            # Arrow before final
            _arrow(draw, x - gap + 2, cell // 2 + 5, color="#999")
        if src.exists():
            img = Image.open(src).convert("RGB").resize((cell, cell), Image.LANCZOS)
            canvas.paste(img, (x, 10))
        label = f"Concept {i + 1}" if i < 4 else "Final"
        _label(draw, x + 10, cell + 15, label)

    out = OUT / "studio_grid.png"
    canvas.save(out)
    print(f"  -> {out.relative_to(REPO_ROOT)}")
    return out


def make_tradition_grid() -> Path:
    """13 traditions in a 5x3 grid with labels."""
    traditions = [
        "chinese_xieyi", "chinese_gongbi", "japanese_traditional",
        "western_academic", "islamic_geometric", "watercolor",
        "african_traditional", "south_asian", "contemporary_art",
        "photography", "brand_design", "ui_ux_design", "default",
    ]
    cell = 180
    gap = 10
    label_h = 20
    cols = 5
    rows = 3
    w = cols * (cell + gap) + gap
    h = rows * (cell + label_h + gap) + gap
    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    for i, t in enumerate(traditions):
        row, col = divmod(i, cols)
        x = gap + col * (cell + gap)
        y = gap + row * (cell + label_h + gap)
        src = V3 / "gallery" / f"{t}.png"
        if src.exists():
            img = Image.open(src).resize((cell, cell), Image.LANCZOS)
            canvas.paste(img, (x, y))
        _label(draw, x + 5, y + cell + 2, t.replace("_", " "), color="#666")

    out = OUT / "tradition_grid.png"
    canvas.save(out)
    print(f"  -> {out.relative_to(REPO_ROOT)}")
    return out


BUILDERS = {
    "gallery": make_gallery_strip,
    "layered": make_layered_exploded,
    "defense3": make_defense3_comparison,
    "edit": make_edit_comparison,
    "inpaint": make_inpaint_comparison,
    "studio": make_studio_grid,
    "traditions": make_tradition_grid,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default=None,
                        help="Comma-separated list of assets to build (default: all)")
    parser.add_argument("--check", action="store_true",
                        help="Only check if input files exist, don't build")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    targets = BUILDERS
    if args.only:
        names = [n.strip() for n in args.only.split(",")]
        targets = {k: v for k, v in BUILDERS.items() if k in names}

    if args.check:
        # Quick existence check for key inputs
        checks = [
            V3 / "gallery" / "chinese_xieyi.png",
            V3 / "layered" / "composite.png",
            V3 / "defense3" / "no_ref" / "composite.png",
            V3 / "edit" / "before.png",
            V3 / "inpaint" / "before.png",
        ]
        ok = True
        for p in checks:
            status = "OK" if p.exists() else "MISSING"
            if status == "MISSING":
                ok = False
            print(f"  [{status}] {p.relative_to(REPO_ROOT)}")
        return 0 if ok else 1

    for name, builder in targets.items():
        print(f"Building {name}...")
        try:
            builder()
        except Exception as exc:
            print(f"  [ERROR] {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify syntax**

Run: `cd /Users/yhryzy/dev/vulca && python3 -m py_compile scripts/make-readme-assets.py && echo "OK"`
Expected: `OK`

- [ ] **Step 3: Build the assets that don't depend on regeneration**

```bash
cd /Users/yhryzy/dev/vulca && python3 scripts/make-readme-assets.py --only gallery,inpaint,traditions
```
Expected: 3 images created in `assets/demo/v3/readme/`

- [ ] **Step 4: Build all assets (after Task 4 regeneration)**

```bash
cd /Users/yhryzy/dev/vulca && python3 scripts/make-readme-assets.py
```
Expected: 7 images in `assets/demo/v3/readme/`

- [ ] **Step 5: Commit**

```bash
git add scripts/make-readme-assets.py assets/demo/v3/readme/
git commit -m "feat(scripts): add make-readme-assets.py — 7 display images from v3 artifacts"
```

---

### Task 6: README Rewrite — Sections 1-3 (Hero + Install + What You Can Do)

**Files:**
- Modify: `README.md:1-100` (approximately)

- [ ] **Step 1: Rewrite hero, install, and overview sections**

Replace the top of the README (everything before the first `---` separator and through "What You Can Do") with the new 12-section structure. The exact content depends on what v3 images passed visual inspection in Task 4.

**Hero section:**
- Badge row: keep PyPI (dynamic), Python, License. Remove hardcoded test count.
- One-liner: update to mention "local-first"
- 3 hero images: use `assets/demo/v3/gallery/chinese_xieyi.png`, `japanese_traditional.png`, `brand_design.png`
- Caption: "Three traditions, one local stack — ComfyUI (SDXL) + Ollama (Gemma 4), zero cloud API"
- CLI eval demo: keep existing block

**Install + Quick Start (merged):**
- Local path first (3 lines: pip install, env vars note + link to setup doc, comfyui create command)
- Cloud path second (2 lines: export key, create command)
- Mock fallback (1 line)
- Optional extras in `<details>`

**What You Can Do:**
- 6 capabilities, each 2-3 lines + one CLI example
- Link to deep-dive section via anchor
- No images in this section (gallery_strip goes in Section 11)

- [ ] **Step 2: Verify**

Run: `cd /Users/yhryzy/dev/vulca && head -100 README.md` — check structure looks right.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(readme): rewrite sections 1-3 — hero, install (local-first), overview"
```

---

### Task 7: README Rewrite — Sections 4-6 (Create + Evaluate + Edit/Inpaint)

**Files:**
- Modify: `README.md` (Create, Evaluate, and Edit+Inpaint sections)

- [ ] **Step 1: Rewrite Create section**

- Add `layered_exploded.png` image (or v2 fallback)
- Add `defense3_comparison.png` image (or v2 fallback)
- Add CJK-aware callout
- Add style-ref anchoring explanation
- Show `--provider comfyui` in examples
- Remove duplicate layered explanation from old "What You Can Do"

- [ ] **Step 2: Keep Evaluate section mostly as-is**

- Minor: add `--provider comfyui` to any generation commands in examples
- Keep three-mode showcase (strict/reference/fusion)

- [ ] **Step 3: Merge Edit + Inpaint into one section**

- Subheading: "Layer-Based Editing" with `edit_comparison.png` (or v2 scenario1-comparison)
- Subheading: "Region-Based Inpainting" with `inpaint_comparison.png`
- Provider-agnostic callout for both
- Scenarios 2-4 in `<details>` block (cut Scenario 3 parallax if over budget)

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs(readme): rewrite sections 4-6 — create (layered+CJK), evaluate, edit+inpaint"
```

---

### Task 8: README Rewrite — Sections 7-9 (Decompose + Studio + Tools)

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Keep Decompose section as-is**

- v2 Qi Baishi + Mona Lisa demos stay
- Add `<!-- v2-asset -->` comments to v2 image references

- [ ] **Step 2: Update Studio section**

- Use `studio_grid.png` if v3 studio assets are good, else keep v2 images
- Add `--provider comfyui` example
- Add `<!-- v2-asset -->` comments if using v2

- [ ] **Step 3: Keep Tools section as-is**

- v2 tools-viz.png stays
- Add `<!-- v2-asset -->` comment

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs(readme): sections 7-9 — decompose (keep v2), studio, tools"
```

---

### Task 9: README Rewrite — Sections 10-12 (Architecture + Traditions + Entry Points)

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update Architecture section**

- Update ASCII diagram: emphasize ComfyUI as primary provider, add local VLM path
- Add provider capability matrix table
- Collapse Self-Evolution into `<details>` block inside Architecture
- Add E2E validation note: "8/8 phases validated on local stack"

- [ ] **Step 2: Update 13 Traditions section**

- Replace 5 v2 inline images with v3 gallery images
- Add `tradition_grid.png` in `<details>` block showing all 13
- Keep custom YAML example

- [ ] **Step 3: Merge Entry Points + Research into Section 12**

- Keep CLI/SDK/MCP/ComfyUI subsections
- Move full CLI reference to `<details>` or link to docs
- Keep Research table + Citation blocks
- Keep "Issues and PRs welcome" line

- [ ] **Step 4: Final line count check**

Run: `wc -l README.md`
Expected: under 800 lines. If over, trim Scenario 3 (parallax) and/or collapse more sections.

- [ ] **Step 5: Verify all image links**

Run: `cd /Users/yhryzy/dev/vulca && grep -oP 'src="[^"]*"' README.md | sed 's/src="//;s/"//' | while read f; do [ -f "$f" ] && echo "OK: $f" || echo "BROKEN: $f"; done`
Expected: all OK, no BROKEN.

- [ ] **Step 6: Commit**

```bash
git add README.md
git commit -m "docs(readme): sections 10-12 — architecture (provider matrix), traditions (v3), entry points"
```

---

### Task 10: Final verification + release commit

**Files:** None (verification only)

- [ ] **Step 1: Full README render check**

Open `README.md` in a markdown previewer or push to a branch and check GitHub rendering. Verify:
- All images render
- TOC links work
- Code blocks are properly formatted
- No orphaned sections or duplicate content

- [ ] **Step 2: Line count**

Run: `wc -l README.md`
Expected: under 800 lines.

- [ ] **Step 3: Commit any final tweaks**

```bash
git add README.md
git commit -m "docs(readme): final polish"
```
