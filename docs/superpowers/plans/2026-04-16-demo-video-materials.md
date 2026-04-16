# Demo Video Materials Preparation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare 20-artwork multi-layer assets, 3-way VLM prompt comparison, and interactive HTML viewer with ABC effects for the Vulca demo video.

**Architecture:** Depth-first pipeline — 3 pilot images (mona-lisa, nighthawks, the-scream) through full EVF-SAM multi-layer decomposition first, then batch remaining 17. Interactive HTML viewer uses external file refs with parallax/breathing/3D-tilt JS effects.

**Tech Stack:** Python 3, EVF-SAM (vendored at /tmp/EVF-SAM), Pillow, numpy, Ollama gemma4, vanilla HTML/CSS/JS

---

## File Structure

### New files
- `scripts/download_showcase_originals.py` — download 12 new images by URL
- `scripts/generate_vlm_prompts.py` — Ollama gemma4 prompt generation for EVF-SAM layers
- `scripts/merge_prompts.py` — compare 3-way prompts, output merged evfsam_prompts.json
- `assets/showcase/html/index.html` — interactive 20-image viewer
- `assets/showcase/html/js/effects.js` — ABC interactive effects (parallax, breathing, 3D tilt)
- `assets/showcase/html/css/style.css` — dark theme styles
- `assets/showcase/experiments/prompts/ollama/` — gemma4-generated prompts per slug
- `assets/showcase/experiments/prompts/gpt/` — Codex GPT-generated prompts per slug
- `assets/showcase/experiments/prompts/manual/` — hand-written prompts per slug

### Modified files
- `assets/showcase/experiments/evfsam_prompts.json` — extend from 8 to 20 images
- `scripts/evfsam_showcase.py` — no code changes, just run with new prompts
- `scripts/migrate_evfsam_to_layers.py` — no code changes, just run with new prompts

---

## Task 1: Download 3 Pilot Originals

**Files:**
- Create: `scripts/download_showcase_originals.py`
- Output: `assets/showcase/originals/{mona-lisa,nighthawks,the-scream}.jpg`

- [ ] **Step 1: Write the download script**

```python
#!/usr/bin/env python3
"""Download showcase original images from public URLs."""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ORIG_DIR = REPO / "assets" / "showcase" / "originals"

# Public-domain / fair-use URLs for showcase images.
# New 12 (pilot 3 first, remaining 9 after validation).
URLS: dict[str, str] = {
    "mona-lisa": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/800px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
    "nighthawks": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Nighthawks_by_Edward_Hopper_1942.jpg/1280px-Nighthawks_by_Edward_Hopper_1942.jpg",
    "the-scream": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg/800px-Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
    "creation-of-adam": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg/1280px-Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg",
    "birth-of-venus": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg/1280px-Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg",
    "the-kiss": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg/800px-The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg",
    "american-gothic": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Grant_Wood_-_American_Gothic_-_Google_Art_Project.jpg/800px-Grant_Wood_-_American_Gothic_-_Google_Art_Project.jpg",
    "persistence-of-memory": "https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg",
    "afghan-girl": "https://upload.wikimedia.org/wikipedia/en/b/b4/Sharbat_Gula.jpg",
    "tank-man": "https://upload.wikimedia.org/wikipedia/en/d/d8/Tianasquare.jpg",
    "lunch-atop-skyscraper": "https://upload.wikimedia.org/wikipedia/en/6/69/Lunch_atop_a_Skyscraper_-_Charles_Clyde_Ebbets.jpg",
    "raising-flag-iwo-jima": "https://upload.wikimedia.org/wikipedia/en/a/a1/WW2_Iwo_Jima_flag_raising.jpg",
}


def download(slugs: list[str] | None = None) -> None:
    ORIG_DIR.mkdir(parents=True, exist_ok=True)
    targets = {k: v for k, v in URLS.items() if slugs is None or k in slugs}
    for slug, url in targets.items():
        dest = ORIG_DIR / f"{slug}.jpg"
        if dest.exists():
            print(f"SKIP {slug}: already exists ({dest.stat().st_size // 1024}K)")
            continue
        print(f"GET  {slug} ...")
        req = urllib.request.Request(url, headers={"User-Agent": "Vulca-Showcase/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            dest.write_bytes(resp.read())
        print(f"  OK {dest.stat().st_size // 1024}K -> {dest}")


if __name__ == "__main__":
    slugs = sys.argv[1:] if len(sys.argv) > 1 else None
    download(slugs)
```

- [ ] **Step 2: Run for pilot 3**

Run: `python scripts/download_showcase_originals.py mona-lisa nighthawks the-scream`
Expected: 3 JPEGs downloaded to `assets/showcase/originals/`, each 100K-2M.

- [ ] **Step 3: Verify images are valid**

```bash
python -c "
from PIL import Image
from pathlib import Path
for s in ['mona-lisa', 'nighthawks', 'the-scream']:
    p = Path('assets/showcase/originals') / f'{s}.jpg'
    im = Image.open(p)
    print(f'{s}: {im.size[0]}x{im.size[1]}, {p.stat().st_size//1024}K')
"
```
Expected: 3 lines with reasonable dimensions (600-2000px range).

- [ ] **Step 4: Commit**

```bash
git add scripts/download_showcase_originals.py assets/showcase/originals/mona-lisa.jpg assets/showcase/originals/nighthawks.jpg assets/showcase/originals/the-scream.jpg
git commit -m "feat: download script + 3 pilot originals (mona-lisa, nighthawks, the-scream)"
```

---

## Task 2: Manual Prompts for 3 Pilot Images (Path C)

**Files:**
- Create: `assets/showcase/experiments/prompts/manual/mona-lisa.json`
- Create: `assets/showcase/experiments/prompts/manual/nighthawks.json`
- Create: `assets/showcase/experiments/prompts/manual/the-scream.json`

- [ ] **Step 1: Write mona-lisa prompts (precision tier, 10-15 layers)**

```json
{
  "slug": "mona-lisa",
  "layers": [
    ["background", "the dark smoky landscape behind the figure with winding roads and rocky formations"],
    ["sky", "the hazy blue-green sky at the top of the painting above the horizon", "background.sky"],
    ["distant_landscape_left", "the winding road and rocky terrain on the left side behind the figure", "background.landscape_left"],
    ["distant_landscape_right", "the river valley and bridge on the right side behind the figure", "background.landscape_right"],
    ["hair", "the long dark brown wavy hair parted in the center falling over both shoulders", "subject.head.hair"],
    ["face_skin", "the smooth pale skin of the face including forehead cheeks and chin", "subject.head.face_skin"],
    ["eyes", "the two dark eyes with subtle lids looking slightly left", "subject.head.face.eyes"],
    ["nose", "the straight nose with soft shadow on the left side", "subject.head.face.nose"],
    ["lips", "the closed lips with a faint upward curve at the corners", "subject.head.face.lips"],
    ["neck_chest", "the bare neck and upper chest area below the chin", "subject.body.neck"],
    ["hands", "the two hands resting one over the other on the arm of the chair", "subject.body.hands"],
    ["clothing", "the dark greenish-brown dress with gathered folds across the torso", "subject.body.clothing"],
    ["veil", "the thin translucent dark veil draped over the hair and shoulders", "subject.head.veil"],
    ["chair_parapet", "the stone ledge and wooden chair armrest at the bottom edge", "foreground.chair"]
  ]
}
```

- [ ] **Step 2: Write nighthawks prompts (precision tier, 12-16 layers)**

```json
{
  "slug": "nighthawks",
  "layers": [
    ["background_buildings", "the dark brick buildings and empty storefronts across the street behind the diner", "background.buildings"],
    ["night_sky", "the dark empty upper area representing the night sky and building upper floors", "background.sky"],
    ["street", "the empty dark sidewalk and street surface in front of the diner", "background.street"],
    ["diner_exterior", "the curved glass window wall and green metal frame of the diner exterior", "subject.diner.exterior"],
    ["diner_interior_wall", "the back wall inside the diner with the coffee urns and equipment", "subject.diner.interior"],
    ["counter", "the long smooth wooden countertop running across the diner", "subject.diner.counter"],
    ["man_in_hat_left", "the man and woman sitting together on the left side of the counter", "subject.person[0]"],
    ["woman_red_dress", "the woman in red with auburn hair sitting next to the man on the left", "subject.person[1]"],
    ["man_alone", "the solitary man with his back to the viewer sitting on the right side of the counter", "subject.person[2]"],
    ["bartender", "the white-uniformed bartender bending forward behind the counter", "subject.person[3]"],
    ["stools", "the round stools along the counter inside the diner", "foreground.stools"],
    ["glasses_cups", "the coffee cups glasses and napkin holder items on the counter", "foreground.objects"],
    ["cash_register", "the metal triangular object near the counter edge", "foreground.register"],
    ["ceiling_light", "the bright fluorescent light fixtures on the diner ceiling", "subject.diner.lights"]
  ]
}
```

- [ ] **Step 3: Write the-scream prompts (precision tier, 10-12 layers)**

```json
{
  "slug": "the-scream",
  "layers": [
    ["sky", "the swirling orange and red sky with wavy horizontal bands", "background.sky"],
    ["fjord_water", "the dark blue water of the fjord below the sky on the right", "background.water"],
    ["distant_landscape", "the green and blue hilly landscape at the horizon", "background.hills"],
    ["bridge_railing", "the diagonal brown wooden railing running from lower left toward upper right", "subject.bridge.railing"],
    ["bridge_deck", "the brown wooden planked surface of the bridge or boardwalk", "subject.bridge.deck"],
    ["screaming_figure_body", "the dark flowing robe and elongated body of the central figure", "subject.figure.body"],
    ["screaming_figure_head", "the bald oval head with open mouth and wide eyes of the central figure", "subject.figure.head"],
    ["screaming_figure_hands", "the two hands pressed against the sides of the head", "subject.figure.hands"],
    ["background_figures", "the two dark silhouetted figures walking away in the upper left", "background.figures"],
    ["boats", "the small dark boats visible on the water below", "background.boats"]
  ]
}
```

- [ ] **Step 4: Commit**

```bash
git add assets/showcase/experiments/prompts/manual/
git commit -m "feat: manual EVF-SAM prompts for 3 pilot images (10-16 layers each)"
```

---

## Task 3: VLM Prompt Generation Script (Path A — Ollama gemma4)

**Files:**
- Create: `scripts/generate_vlm_prompts.py`

- [ ] **Step 1: Write the VLM prompt generation script**

```python
#!/usr/bin/env python3
"""Generate EVF-SAM layer prompts via Ollama VLM (gemma4).

Sends each image to Ollama with a structured prompt asking for semantic
layer decomposition. Outputs per-slug JSON matching the manual prompt format.
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import httpx

REPO = Path(__file__).resolve().parent.parent
ORIG_DIR = REPO / "assets" / "showcase" / "originals"
OUT_DIR = REPO / "assets" / "showcase" / "experiments" / "prompts" / "ollama"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:27b"

SYSTEM_PROMPT = """You are an image segmentation planner. Given an artwork or photograph,
decompose it into 10-20 semantic layers for text-prompted segmentation (EVF-SAM).

Rules:
- Each layer has: name (snake_case), description (one sentence describing EXACTLY what pixels to segment), semantic_path (dot-notation hierarchy)
- The first layer MUST be "background" — it catches all unclaimed pixels
- For portraits: decompose face into eyes, nose, lips, hair, skin
- For groups: use person[0], person[1] etc. in semantic_path
- Descriptions must be unambiguous visual descriptions of pixel regions, NOT artistic interpretations
- Higher-z layers (foreground) take priority over lower-z (background) when overlapping

Output valid JSON array of [name, description, semantic_path] triples. No commentary."""

USER_PROMPT = """Analyze this image and output a JSON array of semantic layer definitions.
Each element: ["layer_name", "pixel-level description of what to segment", "semantic.path"]
Return ONLY the JSON array, no markdown fences or commentary."""


def encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def generate_prompts(slug: str, image_path: Path) -> list[list[str]]:
    b64 = encode_image(image_path)
    payload = {
        "model": MODEL,
        "prompt": USER_PROMPT,
        "system": SYSTEM_PROMPT,
        "images": [b64],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2048},
    }
    resp = httpx.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    text = resp.json()["response"]

    # Extract JSON from response (handle markdown fences if present)
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slugs = sys.argv[1:] if len(sys.argv) > 1 else None

    for img_path in sorted(ORIG_DIR.glob("*.jpg")):
        slug = img_path.stem
        if slug.endswith("-1024"):
            continue
        if slugs and slug not in slugs:
            continue
        out = OUT_DIR / f"{slug}.json"
        if out.exists():
            print(f"SKIP {slug}: {out} exists")
            continue
        print(f"GEN  {slug} via {MODEL} ...")
        try:
            layers = generate_prompts(slug, img_path)
            result = {"slug": slug, "layers": layers}
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False))
            print(f"  OK {len(layers)} layers -> {out}")
        except Exception as e:
            print(f"  FAIL {slug}: {e}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test with one image (requires Ollama running)**

Run: `python scripts/generate_vlm_prompts.py mona-lisa`
Expected: `assets/showcase/experiments/prompts/ollama/mona-lisa.json` with 10-20 layer entries.

- [ ] **Step 3: Run for all 3 pilots**

Run: `python scripts/generate_vlm_prompts.py mona-lisa nighthawks the-scream`
Expected: 3 JSON files in `prompts/ollama/`.

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_vlm_prompts.py assets/showcase/experiments/prompts/ollama/
git commit -m "feat: Ollama VLM prompt generation script + 3 pilot outputs"
```

---

## Task 4: Codex GPT Prompt Generation (Path B)

**Files:**
- Create: `assets/showcase/experiments/prompts/gpt/mona-lisa.json`
- Create: `assets/showcase/experiments/prompts/gpt/nighthawks.json`
- Create: `assets/showcase/experiments/prompts/gpt/the-scream.json`

- [ ] **Step 1: Dispatch Codex agent for prompt generation**

Use the `codex:codex-rescue` agent to generate prompts for each pilot image. Provide the same system prompt and format as Task 3, but send image descriptions instead of raw images. Have Codex produce 3 JSON files matching the manual format.

The Codex agent should research each artwork online and produce `[name, description, semantic_path]` triples based on art-historical knowledge plus visual analysis.

- [ ] **Step 2: Save outputs to prompts/gpt/**

Each file: `{"slug": "<slug>", "layers": [["name", "desc", "path"], ...]}`.

- [ ] **Step 3: Commit**

```bash
git add assets/showcase/experiments/prompts/gpt/
git commit -m "feat: Codex GPT-generated prompts for 3 pilot images"
```

---

## Task 5: Compare and Merge Prompts

**Files:**
- Create: `scripts/merge_prompts.py`
- Modify: `assets/showcase/experiments/evfsam_prompts.json`

- [ ] **Step 1: Write the comparison/merge script**

```python
#!/usr/bin/env python3
"""Compare 3-way prompts (ollama, gpt, manual) and produce merged evfsam_prompts.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO / "assets" / "showcase" / "experiments" / "prompts"
OUT = REPO / "assets" / "showcase" / "experiments" / "evfsam_prompts.json"


def load_source(source: str, slug: str) -> list[list[str]] | None:
    path = PROMPTS_DIR / source / f"{slug}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return data.get("layers", data) if isinstance(data, dict) else data


def compare(slug: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {slug}")
    print(f"{'='*60}")
    for src in ["manual", "ollama", "gpt"]:
        layers = load_source(src, slug)
        if layers is None:
            print(f"  {src:8s}: NOT FOUND")
            continue
        print(f"  {src:8s}: {len(layers)} layers")
        for layer in layers:
            name = layer[0]
            desc = layer[1][:60] + "..." if len(layer[1]) > 60 else layer[1]
            sp = layer[2] if len(layer) >= 3 else name
            print(f"    {name:30s} | {sp:30s} | {desc}")


def merge(slug: str, source: str) -> list[list[str]]:
    """Use a specific source as the winner for a slug."""
    layers = load_source(source, slug)
    if layers is None:
        raise FileNotFoundError(f"No {source} prompts for {slug}")
    return layers


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  merge_prompts.py compare <slug> [slug...]  — side-by-side comparison")
        print("  merge_prompts.py pick <slug> <source>       — pick winner, update evfsam_prompts.json")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "compare":
        for slug in sys.argv[2:]:
            compare(slug)
    elif cmd == "pick":
        slug, source = sys.argv[2], sys.argv[3]
        existing = json.loads(OUT.read_text()) if OUT.exists() else {}
        existing[slug] = merge(slug, source)
        OUT.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n")
        print(f"OK  {slug} <- {source} ({len(existing[slug])} layers)")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run comparison for all 3 pilots**

Run: `python scripts/merge_prompts.py compare mona-lisa nighthawks the-scream`
Expected: side-by-side listing of layers from each source.

- [ ] **Step 3: Pick best source per image**

Run (repeat per slug, choosing the best source after visual comparison):
```bash
python scripts/merge_prompts.py pick mona-lisa manual
python scripts/merge_prompts.py pick nighthawks manual
python scripts/merge_prompts.py pick the-scream manual
```

- [ ] **Step 4: Commit**

```bash
git add scripts/merge_prompts.py assets/showcase/experiments/evfsam_prompts.json
git commit -m "feat: prompt comparison tool + merged prompts for 3 pilots"
```

---

## Task 6: EVF-SAM Multi-Layer Decomposition (Pilot 3)

**Files:**
- Output: `assets/showcase/experiments/evfsam_all/{mona-lisa,nighthawks,the-scream}/`
- Output: `assets/showcase/layers/{mona-lisa,nighthawks,the-scream}/`

- [ ] **Step 1: Verify EVF-SAM is available**

```bash
test -d /tmp/EVF-SAM && echo "EVF-SAM ready" || echo "MISSING: clone EVF-SAM to /tmp/EVF-SAM"
```

- [ ] **Step 2: Run EVF-SAM segmentation on 3 pilots**

Run: `python scripts/evfsam_showcase.py --images mona-lisa,nighthawks,the-scream --force --show-semantic-path`
Expected: Layer PNGs + red-bg previews in `experiments/evfsam_all/{slug}/`. ~3s per prompt × 10-16 prompts × 3 images ≈ 2-3 minutes total.

- [ ] **Step 3: Run migration (z-index overlap resolution)**

Run: `python scripts/migrate_evfsam_to_layers.py`
Expected: For each pilot image:
- `coverage=1.0000 overlap=0.0000`
- Layers + manifest.json in `assets/showcase/layers/{slug}/`

- [ ] **Step 4: Visual spot-check**

```python
python -c "
from pathlib import Path
import json
for slug in ['mona-lisa', 'nighthawks', 'the-scream']:
    m = json.loads((Path('assets/showcase/layers') / slug / 'manifest.json').read_text())
    print(f\"{slug}: {len(m['layers'])} layers, {m['width']}x{m['height']}\")
    for l in m['layers']:
        print(f\"  z={l['z_index']:2d} {l['name']:30s} sp={l['semantic_path']}\")
"
```

- [ ] **Step 5: Commit**

```bash
git add assets/showcase/experiments/evfsam_all/ assets/showcase/layers/
git commit -m "feat: EVF-SAM multi-layer decomposition for 3 pilot images"
```

---

## Task 7: Quality Checkpoint — Pilot Review

**Files:** (no new files, review-only)

- [ ] **Step 1: Open layer PNGs in Finder for visual inspection**

```bash
open assets/showcase/layers/mona-lisa/
open assets/showcase/layers/nighthawks/
open assets/showcase/layers/the-scream/
```

Checklist per image:
- No large holes in any single layer
- Face parts (mona-lisa) cleanly separated
- Per-person layers (nighthawks) isolate individual figures
- Background catches all unclaimed pixels without leaking into foreground

- [ ] **Step 2: Dispatch Codex review of decomposition quality**

Use `codex:codex-rescue` agent to review the manifest.json files, check for z-index inconsistencies, and flag any semantic_path naming issues.

- [ ] **Step 3: If issues found — adjust prompts and re-run Tasks 5-6**

Document which prompts needed adjustment and why. Update the source prompt file, re-pick in merge_prompts.py, re-run EVF-SAM.

- [ ] **Step 4: Mark pilot phase complete**

If all 3 images pass inspection, proceed to batch phase.

---

## Task 8: Download Remaining 9 Originals

**Files:**
- Output: `assets/showcase/originals/{9 new slugs}.jpg`

- [ ] **Step 1: Run download script for remaining 9**

Run: `python scripts/download_showcase_originals.py creation-of-adam birth-of-venus the-kiss american-gothic persistence-of-memory afghan-girl tank-man lunch-atop-skyscraper raising-flag-iwo-jima`
Expected: 9 JPEGs downloaded.

- [ ] **Step 2: Verify all 20 originals present**

```bash
python -c "
from pathlib import Path
originals = sorted(Path('assets/showcase/originals').glob('*.jpg'))
originals = [p for p in originals if not p.stem.endswith('-1024')]
print(f'{len(originals)} originals:')
for p in originals:
    print(f'  {p.stem:30s} {p.stat().st_size // 1024:>6d}K')
"
```
Expected: 20 entries (8 existing + 12 new).

- [ ] **Step 3: Commit**

```bash
git add assets/showcase/originals/
git commit -m "feat: download remaining 9 showcase originals (20 total)"
```

---

## Task 9: Batch Prompts for Remaining 17 Images

**Files:**
- Create: `assets/showcase/experiments/prompts/manual/{12 new slugs}.json`
- Create: `assets/showcase/experiments/prompts/ollama/{remaining}.json`
- Modify: `assets/showcase/experiments/evfsam_prompts.json`

- [ ] **Step 1: Write manual prompts for 3 more precision-tier images**

Write `creation-of-adam.json`, `girl-pearl-earring.json` (upgrade from 3→15 layers), `lunch-atop-skyscraper.json` with 10-20 layers each, following the same format as Task 2.

- [ ] **Step 2: Write manual prompts for 9 standard-tier images**

Write 3-5 layer prompts for: birth-of-venus, the-kiss, american-gothic, nighthawks (already done), persistence-of-memory, afghan-girl, tank-man, raising-flag-iwo-jima. Each file: `{"slug": "...", "layers": [...]}`.

Standard tier template (3-5 layers):
```json
["background", "description of background pixels"],
["subject", "description of main subject pixels"],
["foreground", "description of foreground detail pixels"]
```

- [ ] **Step 3: Run Ollama VLM for all remaining images**

Run: `python scripts/generate_vlm_prompts.py`
(No args = process all originals missing from ollama output dir.)

- [ ] **Step 4: Dispatch Codex for remaining GPT prompts**

Use `codex:codex-rescue` to generate GPT prompts for all 12 new images.

- [ ] **Step 5: Compare and merge all 17 remaining**

Run: `python scripts/merge_prompts.py compare <all-remaining-slugs>`
Then pick winners per slug.

- [ ] **Step 6: Commit**

```bash
git add assets/showcase/experiments/prompts/ assets/showcase/experiments/evfsam_prompts.json
git commit -m "feat: prompts for all 20 images (3-way comparison complete)"
```

---

## Task 10: Batch EVF-SAM for Remaining 17

**Files:**
- Output: `assets/showcase/experiments/evfsam_all/{17 slugs}/`
- Output: `assets/showcase/layers/{17 slugs}/`

- [ ] **Step 1: Run EVF-SAM on all 20 (idempotent, skips existing)**

Run: `python scripts/evfsam_showcase.py --force --show-semantic-path`
Expected: ~200 prompts × 3s = ~10 minutes.

- [ ] **Step 2: Run migration for all**

Run: `python scripts/migrate_evfsam_to_layers.py`
Expected: All 20 images show `coverage=1.0000 overlap=0.0000`.

- [ ] **Step 3: Validate all manifests**

```python
python -c "
import json
from pathlib import Path
layers_dir = Path('assets/showcase/layers')
for d in sorted(layers_dir.iterdir()):
    if not d.is_dir():
        continue
    mf = d / 'manifest.json'
    if not mf.exists():
        print(f'MISSING manifest: {d.name}')
        continue
    m = json.loads(mf.read_text())
    n = len(m['layers'])
    print(f'{d.name:30s}: {n:2d} layers, {m[\"width\"]}x{m[\"height\"]}')
"
```
Expected: 20 entries, precision-tier with 10-20 layers, standard-tier with 3-5.

- [ ] **Step 4: Commit**

```bash
git add assets/showcase/experiments/evfsam_all/ assets/showcase/layers/
git commit -m "feat: EVF-SAM multi-layer decomposition for all 20 images"
```

---

## Task 11: Fix Phase 5 Edit Bug

**Files:**
- Investigate: `src/vulca/layers/edit.py`, `src/vulca/layers/redraw.py`
- Investigate: `scripts/generate_e2e_demo.py` (Phase 5 section)

- [ ] **Step 1: Read the e2e-report.json Phase 5 error**

```bash
python -c "
import json
r = json.loads(open('assets/demo/v3/e2e-report.json').read())
p5 = [p for p in r.get('phases', r.get('results', [])) if 'edit' in str(p).lower() or '5' in str(p.get('phase', ''))]
import pprint; pprint.pprint(p5)
"
```

- [ ] **Step 2: Reproduce the bug**

Compare before.png and after.png:
```python
python -c "
from PIL import Image
import numpy as np
b = np.array(Image.open('assets/demo/v3/edit/before.png'))
a = np.array(Image.open('assets/demo/v3/edit/after.png'))
diff = np.abs(b.astype(int) - a.astype(int))
print(f'Max pixel diff: {diff.max()}, Mean: {diff.mean():.4f}')
print(f'Identical: {np.array_equal(b, a)}')
"
```

- [ ] **Step 3: Diagnose root cause**

Read the Phase 5 section of `scripts/generate_e2e_demo.py` and trace through `layers_edit` or `redraw` to find why the output is identical to input.

- [ ] **Step 4: Fix the bug (TDD)**

Write a failing test that asserts edit output differs from input, then fix the implementation.

- [ ] **Step 5: Re-run Phase 5 and verify**

Re-run the e2e demo Phase 5 section. Verify before.png != after.png.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "fix: Phase 5 edit bug — output was identical to input"
```

---

## Task 12: Interactive HTML Viewer — Structure

**Files:**
- Create: `assets/showcase/html/index.html`
- Create: `assets/showcase/html/css/style.css`

- [ ] **Step 1: Write CSS (dark theme)**

```css
/* assets/showcase/html/css/style.css */
:root {
  --bg: #0d1117;
  --surface: #161b22;
  --border: #30363d;
  --text: #c9d1d9;
  --text-muted: #8b949e;
  --accent: #58a6ff;
  --green: #4caf50;
  --orange: #ff9800;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

header {
  text-align: center; padding: 2rem 1rem;
  border-bottom: 1px solid var(--border);
}
header h1 { font-size: 2rem; font-weight: 300; letter-spacing: 0.1em; }
header .subtitle { color: var(--text-muted); margin-top: 0.5rem; }

nav {
  display: flex; flex-wrap: wrap; gap: 0.5rem;
  justify-content: center; padding: 1rem;
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; background: var(--bg); z-index: 100;
}
nav a {
  color: var(--accent); text-decoration: none; padding: 0.25rem 0.75rem;
  border-radius: 4px; font-size: 0.85rem;
}
nav a:hover { background: var(--surface); }

.gallery { max-width: 1400px; margin: 0 auto; padding: 2rem 1rem; }

.artwork {
  margin-bottom: 4rem; border: 1px solid var(--border);
  border-radius: 8px; overflow: hidden; background: var(--surface);
}
.artwork-header {
  padding: 1.5rem; border-bottom: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
}
.artwork-header h2 { font-size: 1.3rem; font-weight: 500; }
.tradition-badge {
  background: var(--accent); color: var(--bg); padding: 0.2rem 0.6rem;
  border-radius: 12px; font-size: 0.75rem; font-weight: 600;
}

.artwork-body { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
.original-col { padding: 1.5rem; border-right: 1px solid var(--border); }
.layers-col { padding: 1.5rem; }

.original-col img {
  width: 100%; height: auto; border-radius: 4px;
  cursor: pointer; /* for ABC effects */
}

.layer-strip {
  display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1rem;
}
.layer-card {
  width: 120px; text-align: center; cursor: pointer;
  border: 2px solid transparent; border-radius: 6px; padding: 4px;
  transition: border-color 0.2s;
}
.layer-card:hover { border-color: var(--accent); }
.layer-card.active { border-color: var(--green); }
.layer-card img { width: 100%; height: auto; border-radius: 4px; }
.layer-card .name { font-size: 0.7rem; color: var(--text-muted); margin-top: 4px; }

.layer-viewport {
  position: relative; width: 100%; aspect-ratio: auto;
  overflow: hidden; border-radius: 4px; perspective: 800px;
}
.layer-viewport img {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  transition: transform 0.1s ease-out, opacity 0.3s;
}

.controls {
  display: flex; gap: 1rem; align-items: center;
  margin-top: 1rem; padding: 0.75rem;
  background: var(--bg); border-radius: 6px;
}
.controls label { font-size: 0.8rem; color: var(--text-muted); }
.controls input[type="range"] { flex: 1; }
.controls button {
  background: var(--surface); color: var(--text); border: 1px solid var(--border);
  padding: 0.3rem 0.8rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem;
}
.controls button.active { background: var(--accent); color: var(--bg); border-color: var(--accent); }

@media (max-width: 768px) {
  .artwork-body { grid-template-columns: 1fr; }
  .original-col { border-right: none; border-bottom: 1px solid var(--border); }
}
```

- [ ] **Step 2: Write HTML shell**

```html
<!-- assets/showcase/html/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VULCA — 20 Masterworks Multi-Layer Showcase</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <header>
    <h1>VULCA</h1>
    <p class="subtitle">20 Masterworks × Multi-Layer Semantic Decomposition</p>
  </header>
  <nav id="nav"></nav>
  <main class="gallery" id="gallery"></main>
  <script src="js/effects.js"></script>
</body>
</html>
```

- [ ] **Step 3: Commit**

```bash
git add assets/showcase/html/
git commit -m "feat: HTML viewer shell + dark theme CSS"
```

---

## Task 13: Interactive HTML Viewer — JS + ABC Effects

**Files:**
- Create: `assets/showcase/html/js/effects.js`

- [ ] **Step 1: Write effects.js — data loading + gallery rendering**

```javascript
// assets/showcase/html/js/effects.js
(function () {
  "use strict";

  // Artwork metadata — populated by build script or inline
  const ARTWORKS = [
    { slug: "earthrise", title: "Earthrise (NASA, 1968)", tradition: "photography" },
    { slug: "migrant-mother", title: "Migrant Mother (Lange, 1936)", tradition: "photography" },
    { slug: "starry-night", title: "The Starry Night (Van Gogh, 1889)", tradition: "western_academic" },
    { slug: "girl-pearl-earring", title: "Girl with a Pearl Earring (Vermeer, 1665)", tradition: "western_academic" },
    { slug: "water-lilies", title: "Water Lilies (Monet, 1906)", tradition: "western_academic" },
    { slug: "great-wave", title: "The Great Wave (Hokusai, 1831)", tradition: "japanese_traditional" },
    { slug: "qingming-bridge", title: "Along the River (Zhang Zeduan, 1100s)", tradition: "chinese_gongbi" },
    { slug: "padmapani", title: "Padmapani (Ajanta Cave 1, 5th c.)", tradition: "south_asian" },
    { slug: "mona-lisa", title: "Mona Lisa (Leonardo, 1503)", tradition: "western_academic" },
    { slug: "creation-of-adam", title: "Creation of Adam (Michelangelo, 1512)", tradition: "western_academic" },
    { slug: "birth-of-venus", title: "Birth of Venus (Botticelli, 1485)", tradition: "western_academic" },
    { slug: "the-scream", title: "The Scream (Munch, 1893)", tradition: "western_academic" },
    { slug: "the-kiss", title: "The Kiss (Klimt, 1908)", tradition: "western_academic" },
    { slug: "american-gothic", title: "American Gothic (Wood, 1930)", tradition: "western_academic" },
    { slug: "nighthawks", title: "Nighthawks (Hopper, 1942)", tradition: "western_academic" },
    { slug: "persistence-of-memory", title: "Persistence of Memory (Dalí, 1931)", tradition: "western_academic" },
    { slug: "afghan-girl", title: "Afghan Girl (McCurry, 1984)", tradition: "photography" },
    { slug: "tank-man", title: "Tank Man (1989)", tradition: "photography" },
    { slug: "lunch-atop-skyscraper", title: "Lunch atop a Skyscraper (1932)", tradition: "photography" },
    { slug: "raising-flag-iwo-jima", title: "Raising the Flag on Iwo Jima (1945)", tradition: "photography" },
  ];

  // Paths relative to html/ directory
  const LAYERS_BASE = "../../layers";
  const ORIGINALS_BASE = "../../originals";

  // State per artwork
  const state = {};

  // ── Gallery rendering ──
  async function loadManifest(slug) {
    const resp = await fetch(`${LAYERS_BASE}/${slug}/manifest.json`);
    if (!resp.ok) return null;
    return resp.json();
  }

  function renderNav() {
    const nav = document.getElementById("nav");
    nav.innerHTML = ARTWORKS.map(
      (a) => `<a href="#${a.slug}">${a.title.split("(")[0].trim()}</a>`
    ).join("");
  }

  function renderArtwork(art, manifest) {
    const layers = manifest ? manifest.layers : [];
    const section = document.createElement("section");
    section.className = "artwork";
    section.id = art.slug;

    section.innerHTML = `
      <div class="artwork-header">
        <h2>${art.title}</h2>
        <span class="tradition-badge">${art.tradition}</span>
      </div>
      <div class="artwork-body">
        <div class="original-col">
          <div class="layer-viewport" data-slug="${art.slug}">
            <img src="${ORIGINALS_BASE}/${art.slug}.jpg" alt="${art.title}" class="original-img" data-slug="${art.slug}">
            ${layers
              .map(
                (l, i) => `<img src="${LAYERS_BASE}/${art.slug}/${l.file}"
                  class="layer-img" data-slug="${art.slug}" data-index="${i}"
                  data-z="${l.z_index}" style="opacity:0; pointer-events:none;"
                  alt="${l.name}">`
              )
              .join("")}
          </div>
        </div>
        <div class="layers-col">
          <h3>${layers.length} Semantic Layers</h3>
          <div class="layer-strip">
            ${layers
              .map(
                (l, i) => `<div class="layer-card" data-slug="${art.slug}" data-index="${i}">
                  <img src="${LAYERS_BASE}/${art.slug}/${l.file}" alt="${l.name}">
                  <div class="name">${l.name}</div>
                </div>`
              )
              .join("")}
          </div>
          <div class="controls">
            <button class="btn-parallax" data-slug="${art.slug}">A: Parallax</button>
            <button class="btn-breathing" data-slug="${art.slug}">B: Breathe</button>
            <button class="btn-tilt" data-slug="${art.slug}">C: 3D Tilt</button>
          </div>
        </div>
      </div>
    `;
    return section;
  }

  // ── ABC Effects ──

  // A: Parallax — mouse move drives per-layer X/Y offset scaled by z-index
  function initParallax(slug) {
    const viewport = document.querySelector(`.layer-viewport[data-slug="${slug}"]`);
    if (!viewport) return;
    const layerImgs = viewport.querySelectorAll(".layer-img");
    const maxShift = 20; // px

    viewport.addEventListener("mousemove", (e) => {
      if (!state[slug]?.parallax) return;
      const rect = viewport.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5; // -0.5 to 0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      layerImgs.forEach((img) => {
        const z = parseInt(img.dataset.z) || 0;
        const factor = (z + 1) * 0.4; // higher z = more movement
        img.style.transform = `translate(${x * maxShift * factor}px, ${y * maxShift * factor}px)`;
      });
    });

    viewport.addEventListener("mouseleave", () => {
      layerImgs.forEach((img) => { img.style.transform = ""; });
    });
  }

  // B: Breathing — CSS keyframe pulse on layers
  function toggleBreathing(slug, on) {
    const viewport = document.querySelector(`.layer-viewport[data-slug="${slug}"]`);
    if (!viewport) return;
    viewport.querySelectorAll(".layer-img").forEach((img) => {
      if (on) {
        const z = parseInt(img.dataset.z) || 0;
        const duration = 3 + z * 0.5; // higher z = slightly slower
        img.style.animation = `breathe ${duration}s ease-in-out infinite`;
      } else {
        img.style.animation = "";
      }
    });
  }

  // C: 3D Tilt — hover rotateX/Y on viewport
  function initTilt(slug) {
    const viewport = document.querySelector(`.layer-viewport[data-slug="${slug}"]`);
    if (!viewport) return;

    viewport.addEventListener("mousemove", (e) => {
      if (!state[slug]?.tilt) return;
      const rect = viewport.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      viewport.style.transform = `rotateY(${x * 15}deg) rotateX(${-y * 15}deg)`;
    });

    viewport.addEventListener("mouseleave", () => {
      viewport.style.transform = "";
    });
  }

  // ── Layer toggle ──
  function initLayerToggle() {
    document.addEventListener("click", (e) => {
      const card = e.target.closest(".layer-card");
      if (!card) return;
      const slug = card.dataset.slug;
      const index = card.dataset.index;
      const layerImg = document.querySelector(
        `.layer-img[data-slug="${slug}"][data-index="${index}"]`
      );
      if (!layerImg) return;
      const visible = layerImg.style.opacity === "1";
      layerImg.style.opacity = visible ? "0" : "1";
      card.classList.toggle("active", !visible);
    });
  }

  // ── Effect buttons ──
  function initButtons() {
    document.addEventListener("click", (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      const slug = btn.dataset.slug;
      if (!slug) return;
      if (!state[slug]) state[slug] = {};

      if (btn.classList.contains("btn-parallax")) {
        state[slug].parallax = !state[slug].parallax;
        btn.classList.toggle("active", state[slug].parallax);
        // Show all layers when parallax active
        if (state[slug].parallax) showAllLayers(slug);
      }
      if (btn.classList.contains("btn-breathing")) {
        state[slug].breathing = !state[slug].breathing;
        btn.classList.toggle("active", state[slug].breathing);
        if (state[slug].breathing) showAllLayers(slug);
        toggleBreathing(slug, state[slug].breathing);
      }
      if (btn.classList.contains("btn-tilt")) {
        state[slug].tilt = !state[slug].tilt;
        btn.classList.toggle("active", state[slug].tilt);
        if (state[slug].tilt) showAllLayers(slug);
      }
    });
  }

  function showAllLayers(slug) {
    document.querySelectorAll(`.layer-img[data-slug="${slug}"]`).forEach((img) => {
      img.style.opacity = "1";
    });
    document.querySelectorAll(`.layer-card[data-slug="${slug}"]`).forEach((card) => {
      card.classList.add("active");
    });
  }

  // ── Inject breathing keyframes ──
  function injectKeyframes() {
    const style = document.createElement("style");
    style.textContent = `
      @keyframes breathe {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.015); }
      }
    `;
    document.head.appendChild(style);
  }

  // ── Init ──
  async function init() {
    injectKeyframes();
    renderNav();
    initLayerToggle();
    initButtons();

    const gallery = document.getElementById("gallery");
    for (const art of ARTWORKS) {
      const manifest = await loadManifest(art.slug);
      const section = renderArtwork(art, manifest);
      gallery.appendChild(section);
      initParallax(art.slug);
      initTilt(art.slug);
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
```

- [ ] **Step 2: Test in browser**

```bash
cd assets/showcase/html && python -m http.server 8080
```
Open `http://localhost:8080` — verify:
- Nav links scroll to each artwork
- Layer cards toggle layer visibility
- A/B/C buttons activate effects
- Images with manifests show layers; those without show graceful fallback

- [ ] **Step 3: Commit**

```bash
git add assets/showcase/html/js/effects.js
git commit -m "feat: interactive HTML viewer with ABC effects (parallax, breathing, 3D tilt)"
```

---

## Task 14: Upgrade Existing 8 Images to Multi-Layer

**Files:**
- Modify: `assets/showcase/experiments/evfsam_prompts.json` (already done in Task 9)
- Output: upgraded layers in `assets/showcase/layers/` for 5 remaining standard-tier images

Note: girl-pearl-earring already has 8 layers. The 5 standard-tier images (earthrise, migrant-mother, water-lilies, great-wave, qingming-bridge, padmapani) keep their 3-layer prompts. Only girl-pearl-earring is already multi-layer.

- [ ] **Step 1: Re-run EVF-SAM for any prompt-updated images**

Run: `python scripts/evfsam_showcase.py --force --show-semantic-path`

- [ ] **Step 2: Re-run migration**

Run: `python scripts/migrate_evfsam_to_layers.py`

- [ ] **Step 3: Verify all 20 pass validation**

Run the validation snippet from Task 10 Step 3. All 20 must have manifests.

- [ ] **Step 4: Commit**

```bash
git add assets/showcase/layers/ assets/showcase/experiments/evfsam_all/
git commit -m "feat: all 20 images fully decomposed and validated"
```

---

## Task 15: Final Integration Test

**Files:** (no new files)

- [ ] **Step 1: Launch HTML viewer and verify all 20 images**

```bash
cd assets/showcase/html && python -m http.server 8080
```

Checklist:
- All 20 images visible with originals loading
- Precision-tier images (6) show 10-20 layer cards
- Standard-tier images (14) show 3-5 layer cards
- Layer toggle works on all
- Parallax effect visible with mouse movement
- Breathing animation smooth
- 3D tilt responsive

- [ ] **Step 2: Dispatch Codex final review**

Use `codex:codex-rescue` for a final review of:
- All 20 manifests valid
- HTML viewer functional
- No broken image refs

- [ ] **Step 3: Dispatch code-reviewer for HTML/JS quality**

Use `superpowers:code-reviewer` to review the HTML/CSS/JS for quality, accessibility, and performance.

- [ ] **Step 4: Final commit if any fixes needed**

```bash
git add -A
git commit -m "chore: final integration fixes for 20-image showcase"
```
