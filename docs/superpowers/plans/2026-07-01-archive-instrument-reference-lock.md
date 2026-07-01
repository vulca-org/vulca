# Archive Instrument Reference Lock Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static reference-lock review page that defines the visual quality gate for the existing Archive Instrument prototype before the next Three.js pass.

**Architecture:** Add one structured JSON artifact, one static HTML review page, and one focused pytest file. The JSON owns the reference and criteria contract; the HTML renders that contract into a visual review page; tests lock the page links, direction statement, criteria, source metadata, and current-prototype diagnosis.

**Tech Stack:** Static HTML/CSS/vanilla JavaScript, JSON, pytest, existing `docs/product/experiments/` review-page conventions.

---

## File Structure

- Create: `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock.json`
  - Responsibility: canonical structured data for the Archive Instrument reference lock.
- Create: `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html`
  - Responsibility: readable browser review page for the source matrix, current diagnosis, next-pass criteria, and action list.
- Create: `tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py`
  - Responsibility: source-level contract tests for the new page and JSON data.

No current prototype file is modified in this plan.

## Source Set Frozen For First Pass

Use these eight source cards in the first implementation:

1. `archive-instrument-current-prototype` — local current prototype baseline.
2. `natural-history-museum-spirit-collection` — wet-specimen and spirit-collection realism.
3. `apple-vision-pro-formed-glass` — premium formed glass and aluminum product language.
4. `zeiss-microscopy-instrument-system` — scientific instrument credibility.
5. `iyo-webgl-exploded-view` — central object component hierarchy and exploded inspection grammar.
6. `webgpu-scanning-depth-maps` — scan plane as real reveal, not neon decoration.
7. `spline-ai-single-object-rule` — object-first asset generation constraint.
8. `codrops-meshline-family` — route/line families for roots and trace systems.

## Task 1: Add Contract Tests

**Files:**
- Create: `tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py`

- [ ] **Step 1: Write the failing test file**

Create `tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py` with this complete content:

```python
from __future__ import annotations

import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_LOCK_JSON = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-archive-instrument-reference-lock.json"
)
REFERENCE_LOCK_HTML = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-archive-instrument-reference-lock"
    / "index.html"
)


EXPECTED_REFERENCE_IDS = [
    "archive-instrument-current-prototype",
    "natural-history-museum-spirit-collection",
    "apple-vision-pro-formed-glass",
    "zeiss-microscopy-instrument-system",
    "iyo-webgl-exploded-view",
    "webgpu-scanning-depth-maps",
    "spline-ai-single-object-rule",
    "codrops-meshline-family",
]


def test_archive_instrument_reference_lock_json_contract():
    payload = json.loads(REFERENCE_LOCK_JSON.read_text(encoding="utf-8"))

    assert payload["lock_id"] == "stage-02-archive-instrument-reference-lock"
    assert payload["status"] == "reference_lock_before_next_archive_instrument_pass"
    assert payload["selected_direction"] == "realistic specimen plus luxury scientific instrument"
    assert payload["direction_statement"].startswith("Archive Instrument = realistic preserved specimen")
    assert payload["prototype_path"].endswith(
        "3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html"
    )
    assert payload["reference_board_path"].endswith("3d-vector-aesthetic-stage-02-reference-board/index.html")
    assert payload["reference_discovery_path"].endswith("3d-vector-aesthetic-stage-02-reference-discovery.md")

    ids = [item["id"] for item in payload["references"]]
    assert ids == EXPECTED_REFERENCE_IDS
    for item in payload["references"]:
        assert item["label"]
        assert item["source_kind"] in {
            "local_prototype",
            "museum_science_reference",
            "product_material_reference",
            "scientific_instrument_reference",
            "external_inspiration",
            "shader_demo_reference",
            "tool_documentation",
            "creative_coding_family",
        }
        assert item["url"]
        assert item["borrow"]
        assert item["do_not_copy"].startswith("Do not")
        assert item["dimension"] in {
            "baseline",
            "specimen",
            "glass",
            "instrument",
            "sectioning",
            "scanning",
            "asset_pipeline",
            "root_routes",
        }
        assert item["confidence"] in {"high", "medium", "low"}


def test_archive_instrument_reference_lock_diagnosis_and_criteria_are_specific():
    payload = json.loads(REFERENCE_LOCK_JSON.read_text(encoding="utf-8"))

    assert payload["current_diagnosis"]["improved"] == [
        "central object",
        "warmer materiality",
        "four-state logic",
        "less abstract roots",
    ]
    assert "real-world specimen fidelity" in payload["current_diagnosis"]["still_weak"]
    assert "lack of high-quality model or texture assets" in payload["current_diagnosis"]["still_weak"]
    assert payload["current_diagnosis"]["risk"].startswith("continuing to polish procedural shapes")

    assert payload["visual_criteria"] == [
        "The specimen reads as a real object before reading as a diagram.",
        "The glass reads as a vitrine or wet-specimen container, not a transparent UI shell.",
        "The root and support geometry cannot be mistaken for legs or random lines.",
        "Each scroll state changes inspection logic, not just position or opacity.",
        "The palette has warm material contrast and does not collapse into gray-green technical UI.",
    ]
    assert payload["next_pass_moves"][0].startswith("replace or supplement procedural plant geometry")
    assert payload["next_pass_moves"][-1].startswith("add screenshot-based browser review checkpoints")


def test_archive_instrument_reference_lock_html_is_reviewable_and_linked():
    html_text = REFERENCE_LOCK_HTML.read_text(encoding="utf-8")

    assert REFERENCE_LOCK_HTML.is_file()
    assert 'data-vector-stage-product="2026-07-stage-02-archive-instrument-reference-lock"' in html_text
    assert "window.__ARCHIVE_INSTRUMENT_REFERENCE_LOCK__" in html_text
    assert "Archive Instrument = realistic preserved specimen" in html_text
    assert "Direction is locked; execution quality is not." in html_text
    assert "Current Prototype Diagnosis" in html_text
    assert "Visual Criteria For Next Pass" in html_text
    assert "Next-Pass Moves" in html_text
    assert "../3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html" in html_text
    assert "../3d-vector-aesthetic-stage-02-reference-board/index.html" in html_text
    assert "../3d-vector-aesthetic-stage-02-reference-discovery.md" in html_text


def test_archive_instrument_reference_lock_inline_reference_ids_match_json():
    html_text = REFERENCE_LOCK_HTML.read_text(encoding="utf-8")
    payload = json.loads(REFERENCE_LOCK_JSON.read_text(encoding="utf-8"))
    html_block = re.search(r"const REFERENCE_LOCK = (\\{.*?\\});", html_text, re.S)

    assert html_block, "inline reference lock payload missing"
    for item in payload["references"]:
        assert f'id: "{item["id"]}"' in html_block.group(1)
        assert item["label"] in html_text
        assert item["borrow"] in html_text
        assert item["do_not_copy"] in html_text
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py -q
```

Expected: fail with `FileNotFoundError` for `3d-vector-aesthetic-stage-02-archive-instrument-reference-lock.json`.

- [ ] **Step 3: Commit the failing test**

Run:

```bash
git add tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py
git commit -m "test: define archive instrument reference lock contract"
```

Expected: commit succeeds with one new test file.

## Task 2: Add Reference-Lock JSON Data

**Files:**
- Create: `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock.json`
- Test: `tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py`

- [ ] **Step 1: Create the JSON data file**

Create `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock.json` with this complete content:

```json
{
  "lock_id": "stage-02-archive-instrument-reference-lock",
  "status": "reference_lock_before_next_archive_instrument_pass",
  "created": "2026-07-01",
  "selected_direction": "realistic specimen plus luxury scientific instrument",
  "direction_statement": "Archive Instrument = realistic preserved specimen + luxury instrument object + restrained scientific inspection.",
  "prototype_path": "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html",
  "reference_board_path": "docs/product/experiments/3d-vector-aesthetic-stage-02-reference-board/index.html",
  "reference_discovery_path": "docs/product/experiments/3d-vector-aesthetic-stage-02-reference-discovery.md",
  "references": [
    {
      "id": "archive-instrument-current-prototype",
      "label": "Current Archive Instrument Prototype",
      "source_kind": "local_prototype",
      "url": "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html",
      "dimension": "baseline",
      "borrow": "Keep the central scroll object, four inspection states, warmer materiality, and preserved-root subject.",
      "do_not_copy": "Do not keep treating the current procedural geometry as the final visual standard.",
      "quality_line": "The current page is the baseline to beat, not the reference to imitate.",
      "confidence": "high"
    },
    {
      "id": "natural-history-museum-spirit-collection",
      "label": "Natural History Museum Spirit Collection",
      "source_kind": "museum_science_reference",
      "url": "https://www.nhm.ac.uk/discover/14-must-see-spirit-collection.html",
      "dimension": "specimen",
      "borrow": "Use real wet-collection logic: preserved biological material, container, fluid, age, and quiet scientific gravity.",
      "do_not_copy": "Do not copy museum imagery, specimen identities, or archival branding.",
      "quality_line": "The plant must read as a preserved specimen before it reads as a stylized diagram.",
      "confidence": "high"
    },
    {
      "id": "apple-vision-pro-formed-glass",
      "label": "Apple Vision Pro Formed Glass",
      "source_kind": "product_material_reference",
      "url": "https://www.apple.com/apple-vision-pro/",
      "dimension": "glass",
      "borrow": "Use premium formed-glass cues: clean edge highlights, controlled reflections, restrained surface detail, and warm material contrast.",
      "do_not_copy": "Do not copy Apple product identity, interface language, headset shape, or marketing composition.",
      "quality_line": "The glass should feel expensive and physical, not like a transparent UI ellipse.",
      "confidence": "medium"
    },
    {
      "id": "zeiss-microscopy-instrument-system",
      "label": "ZEISS Microscopy Instrument System",
      "source_kind": "scientific_instrument_reference",
      "url": "https://www.zeiss.com/microscopy/us/home.html",
      "dimension": "instrument",
      "borrow": "Use scientific-instrument restraint: optical credibility, precision, quiet technical hierarchy, and observation-first framing.",
      "do_not_copy": "Do not copy ZEISS brand, microscope forms, product photography, or industrial UI.",
      "quality_line": "The object should feel like an inspection instrument, not a sci-fi prop.",
      "confidence": "medium"
    },
    {
      "id": "iyo-webgl-exploded-view",
      "label": "iyO WebGL Exploded View",
      "source_kind": "external_inspiration",
      "url": "https://www.awwwards.com/inspiration/interactive-webgl-exploded-view-iyo",
      "dimension": "sectioning",
      "borrow": "Use central-object component hierarchy and closed-to-inspected separation logic.",
      "do_not_copy": "Do not turn the specimen into generic hardware advertising.",
      "quality_line": "Section state should clarify shell, fluid, specimen, roots, and signal layers.",
      "confidence": "medium"
    },
    {
      "id": "webgpu-scanning-depth-maps",
      "label": "WebGPU Scanning Depth Maps",
      "source_kind": "shader_demo_reference",
      "url": "https://tympanus.net/codrops/2025/03/31/webgpu-scanning-effect-with-depth-maps/",
      "dimension": "scanning",
      "borrow": "Make scan state reveal hidden structure through depth-aware inspection behavior.",
      "do_not_copy": "Do not use scan lines as decorative neon overlay.",
      "quality_line": "Scan must reveal or clarify something that Preserve does not show.",
      "confidence": "high"
    },
    {
      "id": "spline-ai-single-object-rule",
      "label": "Spline AI Single Object Rule",
      "source_kind": "tool_documentation",
      "url": "https://docs.spline.design/spline-ai/ai-3d-generation",
      "dimension": "asset_pipeline",
      "borrow": "Keep generated or modeled work object-first, with scan and archive states added in the web layer.",
      "do_not_copy": "Do not ask model generation for the full page, text, background, or complete interaction.",
      "quality_line": "Any future GLB or generated image should be a clean specimen asset, not a full scene.",
      "confidence": "high"
    },
    {
      "id": "codrops-meshline-family",
      "label": "Codrops MeshLine Family",
      "source_kind": "creative_coding_family",
      "url": "https://tympanus.net/codrops/hub/tag/three-js/",
      "dimension": "root_routes",
      "borrow": "Treat roots and trace lines as authored route families with hierarchy, rhythm, and line-weight differences.",
      "do_not_copy": "Do not drift into retro plotter/vector art or random tube spaghetti.",
      "quality_line": "Root routes must look designed and biological, never like support legs or debug lines.",
      "confidence": "medium"
    }
  ],
  "current_diagnosis": {
    "improved": [
      "central object",
      "warmer materiality",
      "four-state logic",
      "less abstract roots"
    ],
    "still_weak": [
      "real-world specimen fidelity",
      "glass thickness",
      "bottom support readability",
      "reference-level lighting",
      "lack of high-quality model or texture assets"
    ],
    "risk": "continuing to polish procedural shapes instead of introducing better model, texture, or reference-image workflows"
  },
  "visual_criteria": [
    "The specimen reads as a real object before reading as a diagram.",
    "The glass reads as a vitrine or wet-specimen container, not a transparent UI shell.",
    "The root and support geometry cannot be mistaken for legs or random lines.",
    "Each scroll state changes inspection logic, not just position or opacity.",
    "The palette has warm material contrast and does not collapse into gray-green technical UI."
  ],
  "next_pass_moves": [
    "replace or supplement procedural plant geometry with a better modeled or generated specimen asset",
    "rebuild glass as a believable thick container with edge highlights and refraction cues",
    "define one strong hero camera and only modest scroll-state camera changes",
    "reduce annotation density and make scan/section states behave like instrument modes",
    "add screenshot-based browser review checkpoints for mobile and desktop"
  ]
}
```

- [ ] **Step 2: Run the focused test and verify the JSON assertions pass while HTML assertions still fail**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py -q
```

Expected: JSON tests pass; HTML tests fail with `FileNotFoundError` for `index.html`.

- [ ] **Step 3: Commit the JSON data**

Run:

```bash
git add docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock.json
git commit -m "data: add archive instrument reference lock"
```

Expected: commit succeeds with the new JSON file.

## Task 3: Add Static Reference-Lock HTML Page

**Files:**
- Create: `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html`
- Test: `tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py`

- [ ] **Step 1: Create the HTML directory and page**

Create `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html` with this page structure:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Archive Instrument Reference Lock</title>
  <link rel="icon" href="data:," />
  <style>
    :root {
      --bg: #090d0a;
      --panel: rgba(244, 239, 229, 0.07);
      --panel-strong: rgba(244, 239, 229, 0.11);
      --ink: #f4efe5;
      --muted: rgba(244, 239, 229, 0.66);
      --dim: rgba(244, 239, 229, 0.42);
      --line: rgba(244, 239, 229, 0.15);
      --accent: #c4d58b;
      --warm: #e6b678;
      --scan: #b8dfd0;
      font-family: "Avenir Next", "SF Pro Display", "Helvetica Neue", ui-sans-serif, system-ui, sans-serif;
      color-scheme: dark;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(ellipse at 50% 10%, rgba(196, 213, 139, 0.18), transparent 42%),
        radial-gradient(ellipse at 85% 30%, rgba(184, 223, 208, 0.12), transparent 34%),
        linear-gradient(135deg, #060806 0%, #10170f 55%, #211507 100%);
    }

    a { color: inherit; }

    .page {
      width: min(1180px, calc(100vw - 36px));
      margin: 0 auto;
      padding: 48px 0 72px;
    }

    .eyebrow {
      margin: 0 0 12px;
      color: var(--accent);
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    h1, h2, h3, p { margin: 0; }

    h1 {
      max-width: 780px;
      font-size: clamp(34px, 6vw, 76px);
      line-height: 0.96;
      letter-spacing: 0;
      font-weight: 620;
    }

    .lead {
      max-width: 720px;
      margin-top: 22px;
      color: var(--muted);
      font-size: clamp(17px, 2vw, 22px);
      line-height: 1.45;
    }

    .links {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 28px;
    }

    .links a {
      border: 1px solid var(--line);
      padding: 10px 12px;
      color: var(--muted);
      text-decoration: none;
      font-size: 13px;
      background: rgba(0, 0, 0, 0.22);
    }

    section {
      margin-top: 48px;
      border-top: 1px solid var(--line);
      padding-top: 28px;
    }

    .section-head {
      display: grid;
      grid-template-columns: minmax(180px, 0.36fr) 1fr;
      gap: 24px;
      align-items: start;
      margin-bottom: 24px;
    }

    .section-head h2 {
      font-size: clamp(22px, 3vw, 36px);
      line-height: 1;
      font-weight: 600;
    }

    .section-head p {
      color: var(--muted);
      line-height: 1.55;
    }

    .matrix {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }

    .card, .diagnosis, .criteria li, .moves li {
      border: 1px solid var(--line);
      background: var(--panel);
      backdrop-filter: blur(18px);
    }

    .card {
      min-height: 300px;
      padding: 16px;
      display: grid;
      gap: 14px;
      align-content: start;
    }

    .card h3 {
      font-size: 17px;
      line-height: 1.16;
      font-weight: 610;
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .pill {
      border: 1px solid rgba(196, 213, 139, 0.26);
      color: rgba(244, 239, 229, 0.74);
      padding: 5px 7px;
      font-size: 11px;
      line-height: 1;
    }

    .label {
      color: var(--accent);
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .card p {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .card .avoid { color: rgba(230, 182, 120, 0.82); }

    .diagnosis-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }

    .diagnosis {
      padding: 18px;
    }

    .diagnosis ul, .criteria, .moves {
      margin: 14px 0 0;
      padding: 0;
      list-style: none;
    }

    .diagnosis li {
      color: var(--muted);
      margin-top: 9px;
      line-height: 1.4;
    }

    .criteria, .moves {
      display: grid;
      gap: 10px;
    }

    .criteria li, .moves li {
      display: grid;
      grid-template-columns: 44px 1fr;
      gap: 14px;
      align-items: start;
      padding: 16px;
      color: var(--muted);
      line-height: 1.45;
    }

    .num {
      color: var(--accent);
      font-variant-numeric: tabular-nums;
    }

    footer {
      margin-top: 56px;
      color: var(--dim);
      font-size: 12px;
      line-height: 1.5;
    }

    @media (max-width: 900px) {
      .section-head, .diagnosis-grid {
        grid-template-columns: 1fr;
      }

      .matrix {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 580px) {
      .page {
        width: min(100vw - 28px, 1180px);
        padding-top: 32px;
      }

      .matrix {
        grid-template-columns: 1fr;
      }

      .criteria li, .moves li {
        grid-template-columns: 34px 1fr;
      }
    }
  </style>
</head>
<body data-vector-stage-product="2026-07-stage-02-archive-instrument-reference-lock">
  <main class="page">
    <header>
      <p class="eyebrow">Stage 02 / Reference Lock</p>
      <h1>Direction is locked; execution quality is not.</h1>
      <p class="lead">Archive Instrument = realistic preserved specimen + luxury instrument object + restrained scientific inspection.</p>
      <nav class="links" aria-label="Related review pages">
        <a href="../3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html">Current prototype</a>
        <a href="../3d-vector-aesthetic-stage-02-reference-board/index.html">Reference board</a>
        <a href="../3d-vector-aesthetic-stage-02-reference-discovery.md">Reference discovery notes</a>
      </nav>
    </header>

    <section aria-labelledby="matrixTitle">
      <div class="section-head">
        <h2 id="matrixTitle">Reference Matrix</h2>
        <p>These sources define what the next pass should borrow and what it must not copy. The page is a quality gate, not a moodboard.</p>
      </div>
      <div class="matrix" id="referenceMatrix"></div>
    </section>

    <section aria-labelledby="diagnosisTitle">
      <div class="section-head">
        <h2 id="diagnosisTitle">Current Prototype Diagnosis</h2>
        <p>The current prototype is now a better baseline, but still not reference-level. This diagnosis is intentionally direct so the next pass has a measurable target.</p>
      </div>
      <div class="diagnosis-grid" id="diagnosisGrid"></div>
    </section>

    <section aria-labelledby="criteriaTitle">
      <div class="section-head">
        <h2 id="criteriaTitle">Visual Criteria For Next Pass</h2>
        <p>The next implementation should pass these criteria in browser screenshots before it is treated as an improvement.</p>
      </div>
      <ol class="criteria" id="criteriaList"></ol>
    </section>

    <section aria-labelledby="movesTitle">
      <div class="section-head">
        <h2 id="movesTitle">Next-Pass Moves</h2>
        <p>These moves deliberately focus on object credibility, glass, camera restraint, instrument logic, and screenshot-based review.</p>
      </div>
      <ol class="moves" id="movesList"></ol>
    </section>

    <footer>
      Sources are linked for review. This page does not copy third-party source assets, models, or brand language.
    </footer>
  </main>

  <script>
    const REFERENCE_LOCK = {
      lock_id: "stage-02-archive-instrument-reference-lock",
      references: [
        {
          id: "archive-instrument-current-prototype",
          label: "Current Archive Instrument Prototype",
          source_kind: "local_prototype",
          url: "../3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html",
          dimension: "baseline",
          confidence: "high",
          borrow: "Keep the central scroll object, four inspection states, warmer materiality, and preserved-root subject.",
          do_not_copy: "Do not keep treating the current procedural geometry as the final visual standard."
        },
        {
          id: "natural-history-museum-spirit-collection",
          label: "Natural History Museum Spirit Collection",
          source_kind: "museum_science_reference",
          url: "https://www.nhm.ac.uk/discover/14-must-see-spirit-collection.html",
          dimension: "specimen",
          confidence: "high",
          borrow: "Use real wet-collection logic: preserved biological material, container, fluid, age, and quiet scientific gravity.",
          do_not_copy: "Do not copy museum imagery, specimen identities, or archival branding."
        },
        {
          id: "apple-vision-pro-formed-glass",
          label: "Apple Vision Pro Formed Glass",
          source_kind: "product_material_reference",
          url: "https://www.apple.com/apple-vision-pro/",
          dimension: "glass",
          confidence: "medium",
          borrow: "Use premium formed-glass cues: clean edge highlights, controlled reflections, restrained surface detail, and warm material contrast.",
          do_not_copy: "Do not copy Apple product identity, interface language, headset shape, or marketing composition."
        },
        {
          id: "zeiss-microscopy-instrument-system",
          label: "ZEISS Microscopy Instrument System",
          source_kind: "scientific_instrument_reference",
          url: "https://www.zeiss.com/microscopy/us/home.html",
          dimension: "instrument",
          confidence: "medium",
          borrow: "Use scientific-instrument restraint: optical credibility, precision, quiet technical hierarchy, and observation-first framing.",
          do_not_copy: "Do not copy ZEISS brand, microscope forms, product photography, or industrial UI."
        },
        {
          id: "iyo-webgl-exploded-view",
          label: "iyO WebGL Exploded View",
          source_kind: "external_inspiration",
          url: "https://www.awwwards.com/inspiration/interactive-webgl-exploded-view-iyo",
          dimension: "sectioning",
          confidence: "medium",
          borrow: "Use central-object component hierarchy and closed-to-inspected separation logic.",
          do_not_copy: "Do not turn the specimen into generic hardware advertising."
        },
        {
          id: "webgpu-scanning-depth-maps",
          label: "WebGPU Scanning Depth Maps",
          source_kind: "shader_demo_reference",
          url: "https://tympanus.net/codrops/2025/03/31/webgpu-scanning-effect-with-depth-maps/",
          dimension: "scanning",
          confidence: "high",
          borrow: "Make scan state reveal hidden structure through depth-aware inspection behavior.",
          do_not_copy: "Do not use scan lines as decorative neon overlay."
        },
        {
          id: "spline-ai-single-object-rule",
          label: "Spline AI Single Object Rule",
          source_kind: "tool_documentation",
          url: "https://docs.spline.design/spline-ai/ai-3d-generation",
          dimension: "asset_pipeline",
          confidence: "high",
          borrow: "Keep generated or modeled work object-first, with scan and archive states added in the web layer.",
          do_not_copy: "Do not ask model generation for the full page, text, background, or complete interaction."
        },
        {
          id: "codrops-meshline-family",
          label: "Codrops MeshLine Family",
          source_kind: "creative_coding_family",
          url: "https://tympanus.net/codrops/hub/tag/three-js/",
          dimension: "root_routes",
          confidence: "medium",
          borrow: "Treat roots and trace lines as authored route families with hierarchy, rhythm, and line-weight differences.",
          do_not_copy: "Do not drift into retro plotter/vector art or random tube spaghetti."
        }
      ],
      current_diagnosis: {
        improved: ["central object", "warmer materiality", "four-state logic", "less abstract roots"],
        still_weak: ["real-world specimen fidelity", "glass thickness", "bottom support readability", "reference-level lighting", "lack of high-quality model or texture assets"],
        risk: "continuing to polish procedural shapes instead of introducing better model, texture, or reference-image workflows"
      },
      visual_criteria: [
        "The specimen reads as a real object before reading as a diagram.",
        "The glass reads as a vitrine or wet-specimen container, not a transparent UI shell.",
        "The root and support geometry cannot be mistaken for legs or random lines.",
        "Each scroll state changes inspection logic, not just position or opacity.",
        "The palette has warm material contrast and does not collapse into gray-green technical UI."
      ],
      next_pass_moves: [
        "replace or supplement procedural plant geometry with a better modeled or generated specimen asset",
        "rebuild glass as a believable thick container with edge highlights and refraction cues",
        "define one strong hero camera and only modest scroll-state camera changes",
        "reduce annotation density and make scan/section states behave like instrument modes",
        "add screenshot-based browser review checkpoints for mobile and desktop"
      ]
    };

    function renderReferenceCard(item) {
      return `
        <article class="card" data-reference-id="${item.id}">
          <div class="meta">
            <span class="pill">${item.dimension}</span>
            <span class="pill">${item.confidence}</span>
          </div>
          <h3><a href="${item.url}">${item.label}</a></h3>
          <div>
            <p class="label">Borrow</p>
            <p>${item.borrow}</p>
          </div>
          <div>
            <p class="label">Do Not Copy</p>
            <p class="avoid">${item.do_not_copy}</p>
          </div>
        </article>
      `;
    }

    function renderList(items) {
      return items.map((item) => `<li>${item}</li>`).join("");
    }

    document.getElementById("referenceMatrix").innerHTML = REFERENCE_LOCK.references.map(renderReferenceCard).join("");
    document.getElementById("diagnosisGrid").innerHTML = [
      ["Improved", renderList(REFERENCE_LOCK.current_diagnosis.improved)],
      ["Still Weak", renderList(REFERENCE_LOCK.current_diagnosis.still_weak)],
      ["Risk", `<li>${REFERENCE_LOCK.current_diagnosis.risk}</li>`]
    ].map(([title, body]) => `<article class="diagnosis"><p class="label">${title}</p><ul>${body}</ul></article>`).join("");
    document.getElementById("criteriaList").innerHTML = REFERENCE_LOCK.visual_criteria.map((item, index) => `<li><span class="num">${String(index + 1).padStart(2, "0")}</span><span>${item}</span></li>`).join("");
    document.getElementById("movesList").innerHTML = REFERENCE_LOCK.next_pass_moves.map((item, index) => `<li><span class="num">${String(index + 1).padStart(2, "0")}</span><span>${item}</span></li>`).join("");

    window.__ARCHIVE_INSTRUMENT_REFERENCE_LOCK__ = {
      referenceCount: REFERENCE_LOCK.references.length,
      criteriaCount: REFERENCE_LOCK.visual_criteria.length,
      direction: "archive-instrument"
    };
  </script>
</body>
</html>
```

- [ ] **Step 2: Run the focused test and verify all tests pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py -q
```

Expected: all tests in the file pass.

- [ ] **Step 3: Run the related stage-02 reference tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_stage2_reference_board.py tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py -q
```

Expected: both reference-board and reference-lock tests pass.

- [ ] **Step 4: Commit the HTML page**

Run:

```bash
git add docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html
git commit -m "product: add archive instrument reference lock page"
```

Expected: commit succeeds with the new static HTML page.

## Task 4: Browser Review And Final Verification

**Files:**
- Inspect: `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html`
- Test: `tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py`

- [ ] **Step 1: Run the full related test group**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_*.py -q
```

Expected: all vector aesthetics tests pass. Existing pytest config warnings are acceptable only if the suite passes.

- [ ] **Step 2: Check diff hygiene**

Run:

```bash
git diff --check
git status --short
```

Expected: `git diff --check` prints nothing and exits 0. `git status --short` is empty after Task 3 commit.

- [ ] **Step 3: Open the page in the existing local server**

Use the running server URL:

```text
http://127.0.0.1:18747/docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html
```

Expected browser observations:

- desktop width shows a readable hero, four-column reference matrix, diagnosis, criteria, and moves
- narrow width collapses cards without text overlap
- the three local links navigate to current prototype, reference board, and discovery notes
- console warning/error log is empty

- [ ] **Step 4: Capture review notes in final response**

Final response should include:

- plan completion status
- implemented page URL
- test command results
- browser review result
- latest commit hashes from Tasks 1-3

No extra commit is required in this task if the working tree is clean.
