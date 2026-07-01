# Archive Instrument Specimen Asset Pass 01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a separate Three.js candidate page that tests whether an upgraded preserved-root specimen asset reads as a real object before it reads as a diagram.

**Architecture:** Add one JSON contract, one static Three.js candidate page, and one focused pytest contract. The JSON owns the anatomy and acceptance criteria; the HTML renders a deterministic procedural specimen candidate with a compact review panel; tests lock the candidate links, anatomy strings, criteria, and implementation guardrails without modifying the current Archive Instrument prototype.

**Tech Stack:** Static HTML/CSS/vanilla JavaScript, Three.js via CDN, JSON, pytest, existing `docs/product/experiments/` review-page conventions.

---

## Scope And File Structure

This plan must not modify:

```text
docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html
```

Create exactly these files:

- `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01.json`
  - Canonical contract for candidate anatomy, criteria, links, and handoff notes.
- `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01/index.html`
  - Static Three.js candidate page for visual review.
- `tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py`
  - Source-level contract tests for the candidate page and JSON.

## Commit Discipline

The steps below use TDD, but do not commit a deliberately failing intermediate state. Commit only after the focused tests for that task pass.

## Task 1: Add JSON Contract And Source Tests

**Files:**
- Create: `tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py`
- Create: `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01.json`

- [ ] **Step 1: Create the failing test file**

Create `tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py` with this full content:

```python
from __future__ import annotations

import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_JSON = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01.json"
)
CANDIDATE_HTML = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01"
    / "index.html"
)
CURRENT_PROTOTYPE = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-archive-instrument-prototype"
    / "index.html"
)

EXPECTED_ANATOMY_PARTS = [
    "woody stem",
    "leaf cluster",
    "petiole",
    "root crown",
    "fine roots",
    "mounting wire",
]
EXPECTED_CRITERIA = [
    "The specimen reads as a real object before reading as a diagram.",
    "The glass reads as a vitrine or wet-specimen container, not a transparent UI shell.",
    "The root and support geometry cannot be mistaken for legs or random lines.",
    "Each scroll state changes inspection logic, not just position or opacity.",
    "The palette has warm material contrast and does not collapse into gray-green technical UI.",
]
EXPECTED_SECONDARY_SUCCESS = [
    "roots no longer read as legs",
    "leaves have credible attachment and orientation",
    "root crown feels physically connected to the stem",
    "material palette is warmer and less gray-green",
    "the candidate can be moved into the current prototype without changing the direction",
]


def _payload() -> dict:
    assert CANDIDATE_JSON.is_file()
    return json.loads(CANDIDATE_JSON.read_text(encoding="utf-8"))


def test_specimen_asset_pass01_json_contract():
    payload = _payload()

    assert payload["candidate_id"] == "stage-02-archive-instrument-specimen-asset-pass-01"
    assert payload["status"] == "specimen_asset_candidate_before_prototype_merge"
    assert payload["created"] == "2026-07-01"
    assert payload["direction"] == "realistic preserved specimen plus luxury scientific instrument"
    assert payload["goal"] == "Does the central specimen read as a preserved real object before it reads as a diagram?"
    assert payload["current_prototype_path"] == (
        "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html"
    )
    assert payload["reference_lock_path"] == (
        "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html"
    )
    assert payload["recommended_approach"] == "separate procedural specimen candidate"
    assert payload["explicit_non_goal"] == "do not modify the current Archive Instrument prototype in this pass"


def test_specimen_asset_pass01_anatomy_and_criteria_contract():
    payload = _payload()

    assert payload["required_anatomy_parts"] == EXPECTED_ANATOMY_PARTS
    assert payload["visual_criteria"] == EXPECTED_CRITERIA
    assert payload["secondary_success_criteria"] == EXPECTED_SECONDARY_SUCCESS
    assert payload["candidate_traits"] == [
        "asymmetric woody stem with taper, knots, scars, and bark rings",
        "5 to 7 leaves with varied size, age, bend, pitch, and yaw",
        "petioles visibly attach leaves to the stem",
        "root crown or soil plug with roots emerging from believable sockets",
        "short branching fine roots and root hairs",
        "mounting wires read as specimen support, not legs",
        "warm brown, olive, pale vein, and amber material accents",
    ]
    assert payload["first_read"] == "preserved organic sample"
    assert payload["not_read_as"] == [
        "plant icon",
        "wireframe diagram",
        "random tubes",
        "technical toy",
    ]


def test_specimen_asset_pass01_html_is_reviewable_and_isolated():
    assert CANDIDATE_HTML.is_file()
    html_text = CANDIDATE_HTML.read_text(encoding="utf-8")

    assert CURRENT_PROTOTYPE.is_file()
    assert 'data-vector-stage-product="2026-07-stage-02-archive-instrument-specimen-asset-pass-01"' in html_text
    assert "<title>Archive Instrument Specimen Asset Pass 01</title>" in html_text
    assert "window.__ARCHIVE_SPECIMEN_ASSET_PASS_01__" in html_text
    assert "Specimen Asset Pass 01" in html_text
    assert "Does the central specimen read as a preserved real object before it reads as a diagram?" in html_text
    assert "../3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html" in html_text
    assert "../3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html" in html_text
    assert "import * as THREE from \"https://unpkg.com/three@0.165.0/build/three.module.js\"" in html_text
    assert "new THREE.WebGLRenderer" in html_text
    assert "preserveDrawingBuffer: true" in html_text
    assert "createSpecimenCandidate" in html_text
    assert "createLeafBlade" in html_text
    assert "createFineRoots" in html_text
    assert "createMountingWires" in html_text


def test_specimen_asset_pass01_html_contains_required_anatomy_and_criteria():
    payload = _payload()
    html_text = CANDIDATE_HTML.read_text(encoding="utf-8")

    for part in payload["required_anatomy_parts"]:
        assert part in html_text
    for criterion in payload["visual_criteria"]:
        assert criterion in html_text
    for success in payload["secondary_success_criteria"]:
        assert success in html_text
    for phrase in payload["not_read_as"]:
        assert phrase in html_text
    assert "accepted: merge candidate anatomy into the main Archive Instrument prototype" in html_text
    assert "still weak: move to generated GLB or modeled-asset exploration" in html_text
    assert "glass/instrument/scroll-state changes remain later passes" in html_text


def test_specimen_asset_pass01_inline_payload_matches_json():
    payload = _payload()
    html_text = CANDIDATE_HTML.read_text(encoding="utf-8")
    html_block = re.search(r"const SPECIMEN_PASS = (\\{.*?\\});", html_text, re.S)

    assert html_block, "inline specimen pass payload missing"
    inline_payload = json.loads(html_block.group(1))
    assert inline_payload == payload
    assert "referenceCount" not in html_text
    assert "candidateId: SPECIMEN_PASS.candidate_id" in html_text
    assert "anatomyCount: SPECIMEN_PASS.required_anatomy_parts.length" in html_text
    assert "criteriaCount: SPECIMEN_PASS.visual_criteria.length" in html_text
```

- [ ] **Step 2: Run the test and verify it fails because the JSON/page do not exist**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py -q
```

Expected: fail with `AssertionError` or `FileNotFoundError` because `3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01.json` and `index.html` do not exist yet.

- [ ] **Step 3: Create the JSON contract**

Create `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01.json` with this exact content:

```json
{
  "candidate_id": "stage-02-archive-instrument-specimen-asset-pass-01",
  "status": "specimen_asset_candidate_before_prototype_merge",
  "created": "2026-07-01",
  "direction": "realistic preserved specimen plus luxury scientific instrument",
  "goal": "Does the central specimen read as a preserved real object before it reads as a diagram?",
  "current_prototype_path": "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html",
  "reference_lock_path": "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html",
  "recommended_approach": "separate procedural specimen candidate",
  "explicit_non_goal": "do not modify the current Archive Instrument prototype in this pass",
  "required_anatomy_parts": [
    "woody stem",
    "leaf cluster",
    "petiole",
    "root crown",
    "fine roots",
    "mounting wire"
  ],
  "candidate_traits": [
    "asymmetric woody stem with taper, knots, scars, and bark rings",
    "5 to 7 leaves with varied size, age, bend, pitch, and yaw",
    "petioles visibly attach leaves to the stem",
    "root crown or soil plug with roots emerging from believable sockets",
    "short branching fine roots and root hairs",
    "mounting wires read as specimen support, not legs",
    "warm brown, olive, pale vein, and amber material accents"
  ],
  "first_read": "preserved organic sample",
  "not_read_as": [
    "plant icon",
    "wireframe diagram",
    "random tubes",
    "technical toy"
  ],
  "visual_criteria": [
    "The specimen reads as a real object before reading as a diagram.",
    "The glass reads as a vitrine or wet-specimen container, not a transparent UI shell.",
    "The root and support geometry cannot be mistaken for legs or random lines.",
    "Each scroll state changes inspection logic, not just position or opacity.",
    "The palette has warm material contrast and does not collapse into gray-green technical UI."
  ],
  "secondary_success_criteria": [
    "roots no longer read as legs",
    "leaves have credible attachment and orientation",
    "root crown feels physically connected to the stem",
    "material palette is warmer and less gray-green",
    "the candidate can be moved into the current prototype without changing the direction"
  ],
  "handoff_notes": [
    "accepted: merge candidate anatomy into the main Archive Instrument prototype",
    "still weak: move to generated GLB or modeled-asset exploration",
    "glass/instrument/scroll-state changes remain later passes"
  ]
}
```

- [ ] **Step 4: Run the test again and verify only HTML-related assertions fail**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py -q
```

Expected: JSON contract tests pass; HTML tests fail because `index.html` does not exist yet.

- [ ] **Step 5: Defer commit until the candidate page exists**

Do not commit after this step. The focused test file still contains HTML assertions that must fail until Task 2 creates the candidate page. Repository policy requires verified commits only, so keep the test and JSON changes uncommitted until Task 2 makes the focused suite pass and then commit the JSON, HTML, and test together.

## Task 2: Add The Three.js Candidate Page

**Files:**
- Create: `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01/index.html`
- Test: `tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py`

- [ ] **Step 1: Create the candidate page**

Create `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01/index.html` with the structure below. The implementation may refine exact numeric coordinates during visual review, but it must keep the named functions and strings because tests assert them.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Archive Instrument Specimen Asset Pass 01</title>
  <link rel="icon" href="data:," />
  <style>
    :root {
      --bg: #090d0a;
      --ink: #f4efe5;
      --muted: rgba(244, 239, 229, 0.68);
      --dim: rgba(244, 239, 229, 0.42);
      --line: rgba(244, 239, 229, 0.14);
      --panel: rgba(244, 239, 229, 0.07);
      --accent: #c4d58b;
      --warm: #d7a261;
      --root: #b9946d;
      font-family: "Avenir Next", "SF Pro Display", "Helvetica Neue", ui-sans-serif, system-ui, sans-serif;
      color-scheme: dark;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(ellipse at 50% 34%, rgba(196, 213, 139, 0.15), transparent 42%),
        linear-gradient(135deg, #050706 0%, #10170f 54%, #211507 100%);
      overflow-x: hidden;
    }

    .stage {
      min-height: 100vh;
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(300px, 420px);
      gap: 28px;
      align-items: stretch;
      width: min(1280px, calc(100vw - 36px));
      margin: 0 auto;
      padding: 28px 0;
    }

    .viewport {
      position: relative;
      min-height: calc(100vh - 56px);
      border: 1px solid var(--line);
      background: rgba(0, 0, 0, 0.18);
      overflow: hidden;
    }

    #specimenCanvas {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      display: block;
    }

    .overlay-title {
      position: absolute;
      left: 22px;
      top: 20px;
      z-index: 2;
      max-width: min(360px, calc(100% - 44px));
    }

    .eyebrow {
      margin: 0 0 10px;
      color: var(--accent);
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    h1, h2, h3, p { margin: 0; }

    h1 {
      font-size: clamp(30px, 5.4vw, 72px);
      line-height: 0.94;
      letter-spacing: 0;
      font-weight: 620;
    }

    .side {
      display: grid;
      gap: 12px;
      align-content: start;
    }

    .panel {
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 18px;
      backdrop-filter: blur(18px);
    }

    .panel h2 {
      font-size: 20px;
      line-height: 1.1;
    }

    .panel p, .panel li {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .panel ul, .panel ol {
      margin: 12px 0 0;
      padding-left: 18px;
    }

    .links {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }

    .links a {
      border: 1px solid var(--line);
      padding: 8px 10px;
      color: var(--muted);
      text-decoration: none;
      font-size: 12px;
      background: rgba(0, 0, 0, 0.2);
    }

    .legend {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-top: 12px;
    }

    .tag {
      border: 1px solid rgba(196, 213, 139, 0.24);
      padding: 8px 9px;
      color: var(--muted);
      font-size: 12px;
    }

    .primary {
      border-color: rgba(196, 213, 139, 0.44);
      background: rgba(196, 213, 139, 0.08);
      color: var(--ink);
    }

    .note {
      color: var(--dim);
      font-size: 12px;
      line-height: 1.45;
    }

    @media (max-width: 920px) {
      .stage {
        grid-template-columns: 1fr;
      }

      .viewport {
        min-height: 64vh;
      }
    }

    @media (max-width: 560px) {
      .stage {
        width: min(100vw - 24px, 1280px);
        padding-top: 16px;
      }

      .legend {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body data-vector-stage-product="2026-07-stage-02-archive-instrument-specimen-asset-pass-01">
  <main class="stage">
    <section class="viewport" aria-label="Specimen candidate view">
      <canvas id="specimenCanvas"></canvas>
      <div class="overlay-title">
        <p class="eyebrow">Archive Instrument / Specimen Asset Pass 01</p>
        <h1>Specimen Asset Pass 01</h1>
      </div>
    </section>

    <aside class="side" aria-label="Specimen asset review notes">
      <section class="panel">
        <p class="eyebrow">Review Question</p>
        <h2>Does the central specimen read as a preserved real object before it reads as a diagram?</h2>
        <div class="links">
          <a href="../3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html">Current Prototype</a>
          <a href="../3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html">Reference Lock</a>
        </div>
      </section>

      <section class="panel">
        <p class="eyebrow">Anatomy Tags</p>
        <div class="legend" id="anatomyList"></div>
      </section>

      <section class="panel">
        <p class="eyebrow">Criteria Check</p>
        <ol id="criteriaList"></ol>
      </section>

      <section class="panel">
        <p class="eyebrow">Handoff Notes</p>
        <ul id="handoffList"></ul>
        <p class="note">This page improves only the specimen asset basis. Glass, instrument, and scroll-state passes stay separate.</p>
      </section>
    </aside>
  </main>

  <script type="module">
    import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.js";

    const SPECIMEN_PASS = {
      "candidate_id": "stage-02-archive-instrument-specimen-asset-pass-01",
      "status": "specimen_asset_candidate_before_prototype_merge",
      "created": "2026-07-01",
      "direction": "realistic preserved specimen plus luxury scientific instrument",
      "goal": "Does the central specimen read as a preserved real object before it reads as a diagram?",
      "current_prototype_path": "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html",
      "reference_lock_path": "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html",
      "recommended_approach": "separate procedural specimen candidate",
      "explicit_non_goal": "do not modify the current Archive Instrument prototype in this pass",
      "required_anatomy_parts": ["woody stem", "leaf cluster", "petiole", "root crown", "fine roots", "mounting wire"],
      "candidate_traits": [
        "asymmetric woody stem with taper, knots, scars, and bark rings",
        "5 to 7 leaves with varied size, age, bend, pitch, and yaw",
        "petioles visibly attach leaves to the stem",
        "root crown or soil plug with roots emerging from believable sockets",
        "short branching fine roots and root hairs",
        "mounting wires read as specimen support, not legs",
        "warm brown, olive, pale vein, and amber material accents"
      ],
      "first_read": "preserved organic sample",
      "not_read_as": ["plant icon", "wireframe diagram", "random tubes", "technical toy"],
      "visual_criteria": [
        "The specimen reads as a real object before reading as a diagram.",
        "The glass reads as a vitrine or wet-specimen container, not a transparent UI shell.",
        "The root and support geometry cannot be mistaken for legs or random lines.",
        "Each scroll state changes inspection logic, not just position or opacity.",
        "The palette has warm material contrast and does not collapse into gray-green technical UI."
      ],
      "secondary_success_criteria": [
        "roots no longer read as legs",
        "leaves have credible attachment and orientation",
        "root crown feels physically connected to the stem",
        "material palette is warmer and less gray-green",
        "the candidate can be moved into the current prototype without changing the direction"
      ],
      "handoff_notes": [
        "accepted: merge candidate anatomy into the main Archive Instrument prototype",
        "still weak: move to generated GLB or modeled-asset exploration",
        "glass/instrument/scroll-state changes remain later passes"
      ]
    };

    const canvas = document.getElementById("specimenCanvas");
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true });
    renderer.setClearColor(0x080b08, 1);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.18;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x080b08, 0.03);
    const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
    camera.position.set(0.1, 0.12, 5.4);

    const root = new THREE.Group();
    root.rotation.set(-0.05, -0.25, 0.01);
    scene.add(root);

    function tubeFromPoints(points, radius, material, segments = 72) {
      const curve = new THREE.CatmullRomCurve3(points.map((point) => new THREE.Vector3(...point)));
      return new THREE.Mesh(new THREE.TubeGeometry(curve, segments, radius, 10, false), material);
    }

    function createLeafBlade(width, height, material, veinMaterial) {
      const group = new THREE.Group();
      const shape = new THREE.Shape();
      shape.moveTo(0, height * 0.52);
      shape.bezierCurveTo(width * 0.62, height * 0.36, width * 0.58, height * -0.2, 0, height * -0.52);
      shape.bezierCurveTo(width * -0.55, height * -0.24, width * -0.64, height * 0.34, 0, height * 0.52);
      const blade = new THREE.Mesh(new THREE.ShapeGeometry(shape, 36), material);
      blade.userData.kind = "leaf cluster";
      group.add(blade);

      const center = tubeFromPoints([[0, height * -0.42, 0.012], [0.01, 0, 0.018], [0, height * 0.45, 0.012]], 0.0035, veinMaterial, 24);
      center.userData.kind = "leaf vein";
      group.add(center);
      [-1, 1].forEach((side) => {
        for (let i = 0; i < 4; i += 1) {
          const y = height * (-0.26 + i * 0.16);
          const vein = tubeFromPoints([[0, y, 0.014], [side * width * (0.16 + i * 0.035), y + height * 0.09, 0.014]], 0.0017, veinMaterial, 10);
          vein.userData.kind = "leaf vein";
          group.add(vein);
        }
      });
      return group;
    }

    function createFineRoots(rootMaterial, hairMaterial) {
      const group = new THREE.Group();
      const routes = [
        [[-0.02, -0.44, 0.05], [-0.06, -0.54, 0.08], [-0.13, -0.62, 0.06], [-0.22, -0.69, 0.02]],
        [[0.03, -0.44, -0.02], [0.08, -0.54, -0.05], [0.16, -0.62, -0.06], [0.25, -0.7, -0.02]],
        [[0, -0.45, 0.02], [-0.02, -0.56, -0.02], [-0.04, -0.65, -0.03], [-0.06, -0.73, 0.01]],
        [[0.04, -0.46, 0.04], [0.03, -0.56, 0.1], [0.07, -0.64, 0.11], [0.1, -0.72, 0.06]]
      ];
      routes.forEach((route, index) => {
        const rootTube = tubeFromPoints(route, index < 2 ? 0.009 : 0.0055, rootMaterial.clone(), 88);
        rootTube.userData.kind = index < 2 ? "fine roots primary" : "fine roots secondary";
        group.add(rootTube);
      });

      for (let i = 0; i < 38; i += 1) {
        const side = i % 2 === 0 ? -1 : 1;
        const y = -0.52 - (i % 14) * 0.014;
        const baseX = Math.sin(i * 1.7) * 0.11;
        const z = Math.cos(i * 1.37) * 0.08;
        const length = 0.026 + (i % 4) * 0.008;
        const hair = tubeFromPoints([
          [baseX, y, z],
          [baseX + side * length * 0.45, y - 0.016, z + Math.sin(i) * 0.014],
          [baseX + side * length, y - 0.033, z + Math.cos(i) * 0.018]
        ], 0.0012, hairMaterial.clone(), 24);
        hair.userData.kind = "fine roots hair";
        group.add(hair);
      }
      return group;
    }

    function createMountingWires(material) {
      const group = new THREE.Group();
      [
        [[-0.24, -0.5, 0.13], [-0.12, -0.26, 0.17], [0.02, -0.02, 0.13]],
        [[0.24, -0.5, 0.07], [0.13, -0.25, 0.13], [0.04, 0.08, 0.1]]
      ].forEach((route) => {
        const wire = tubeFromPoints(route, 0.003, material.clone(), 40);
        wire.userData.kind = "mounting wire";
        group.add(wire);
      });
      return group;
    }

    function createSpecimenCandidate() {
      const group = new THREE.Group();
      const stemMaterial = new THREE.MeshStandardMaterial({ color: 0x9a714a, roughness: 0.74, metalness: 0.02, emissive: 0x160b05, emissiveIntensity: 0.12 });
      const barkMaterial = new THREE.MeshBasicMaterial({ color: 0xd8a777, transparent: true, opacity: 0.28, depthWrite: false });
      const leafMaterial = new THREE.MeshStandardMaterial({ color: 0x91b966, roughness: 0.68, metalness: 0.02, emissive: 0x15210d, emissiveIntensity: 0.09, side: THREE.DoubleSide });
      const youngLeafMaterial = new THREE.MeshStandardMaterial({ color: 0xc0c979, roughness: 0.58, metalness: 0.02, emissive: 0x1c230d, emissiveIntensity: 0.1, side: THREE.DoubleSide });
      const veinMaterial = new THREE.MeshBasicMaterial({ color: 0xe0e9bb, transparent: true, opacity: 0.34, depthWrite: false });
      const crownMaterial = new THREE.MeshStandardMaterial({ color: 0x5b3a24, roughness: 0.88, metalness: 0.02, emissive: 0x120806, emissiveIntensity: 0.12 });
      const rootMaterial = new THREE.MeshStandardMaterial({ color: 0xb9946d, roughness: 0.88, metalness: 0.01, transparent: true, opacity: 0.5, depthWrite: false });
      const hairMaterial = new THREE.MeshBasicMaterial({ color: 0xcaa780, transparent: true, opacity: 0.12, depthWrite: false });
      const wireMaterial = new THREE.MeshBasicMaterial({ color: 0xc79b62, transparent: true, opacity: 0.18, depthWrite: false });

      const stem = tubeFromPoints([[0.02, -0.39, 0.06], [0.08, -0.1, 0.1], [0.02, 0.22, 0.08], [-0.05, 0.54, 0.04], [-0.03, 0.76, 0.03]], 0.045, stemMaterial, 96);
      stem.userData.kind = "woody stem";
      group.add(stem);

      [-0.26, -0.1, 0.08, 0.26, 0.48, 0.66].forEach((y, index) => {
        const scar = tubeFromPoints([[-0.035, y, 0.12], [0.02, y + 0.02, 0.15], [0.058, y + 0.038, 0.11]], 0.0025, barkMaterial.clone(), 18);
        scar.rotation.z = index * 0.23;
        scar.userData.kind = "bark ring";
        group.add(scar);
      });

      const crown = new THREE.Mesh(new THREE.SphereGeometry(0.27, 56, 28), crownMaterial);
      crown.scale.set(1.05, 0.5, 0.74);
      crown.position.set(0, -0.43, 0.04);
      crown.userData.kind = "root crown";
      group.add(crown);

      const leafSpecs = [
        [-0.34, 0.36, 0.04, -0.92, 0.45, -0.48, 0.22, 0.21, 0.44, 0],
        [0.34, 0.44, 0.12, 0.8, 0.34, 0.55, -0.08, 0.2, 0.42, 0],
        [-0.08, 0.68, -0.02, -0.24, 0.72, -0.12, 0.14, 0.14, 0.32, 1],
        [0.2, 0.2, 0.22, 0.42, 0.08, 0.72, -0.26, 0.12, 0.27, 1],
        [-0.2, 0.16, 0.02, -0.54, -0.08, -0.58, 0.08, 0.105, 0.25, 0],
        [0.1, 0.58, -0.12, 0.22, 0.62, 0.2, -0.1, 0.115, 0.28, 1]
      ];
      leafSpecs.forEach(([x, y, z, roll, pitch, yaw, openBias, width, height, young]) => {
        const leaf = createLeafBlade(width, height, young ? youngLeafMaterial.clone() : leafMaterial.clone(), veinMaterial.clone());
        leaf.position.set(x, y, z);
        leaf.rotation.set(pitch, yaw + openBias * 0.16, roll);
        leaf.userData.kind = "leaf cluster";
        const petiole = tubeFromPoints([[0.01, 0.2, 0.08], [x * 0.42, y * 0.62, z * 0.62], [x * 0.92, y * 0.94, z]], 0.005, stemMaterial, 30);
        petiole.userData.kind = "petiole";
        group.add(petiole);
        group.add(leaf);
      });

      group.add(createFineRoots(rootMaterial, hairMaterial));
      group.add(createMountingWires(wireMaterial));
      return group;
    }

    function addLights() {
      scene.add(new THREE.HemisphereLight(0xf8efdf, 0x070b08, 1.15));
      const key = new THREE.DirectionalLight(0xf7eedc, 3.1);
      key.position.set(-3, 4.5, 4);
      scene.add(key);
      const warm = new THREE.PointLight(0xe0a15f, 11, 7);
      warm.position.set(-2.2, -0.6, 2.5);
      scene.add(warm);
      const rim = new THREE.PointLight(0xc4d58b, 6, 6);
      rim.position.set(2.8, 1.6, 2.4);
      scene.add(rim);
    }

    const specimen = createSpecimenCandidate();
    root.add(specimen);
    addLights();

    const clock = new THREE.Clock();
    function resize() {
      const rect = canvas.getBoundingClientRect();
      const width = Math.max(1, Math.floor(rect.width));
      const height = Math.max(1, Math.floor(rect.height));
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      root.scale.setScalar(width < 700 ? 0.84 : 1);
    }

    function animate() {
      const time = clock.getElapsedTime();
      resize();
      root.rotation.y = -0.25 + Math.sin(time * 0.22) * 0.045;
      root.rotation.x = -0.05 + Math.sin(time * 0.17) * 0.012;
      camera.lookAt(0, 0.02, 0);
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }

    document.getElementById("anatomyList").innerHTML = SPECIMEN_PASS.required_anatomy_parts.map((part) => `<span class="tag">${part}</span>`).join("");
    document.getElementById("criteriaList").innerHTML = SPECIMEN_PASS.visual_criteria.map((criterion, index) => `<li class="${index === 0 ? "primary" : ""}">${criterion}</li>`).join("");
    document.getElementById("handoffList").innerHTML = SPECIMEN_PASS.handoff_notes.map((note) => `<li>${note}</li>`).join("");

    window.__ARCHIVE_SPECIMEN_ASSET_PASS_01__ = {
      candidateId: SPECIMEN_PASS.candidate_id,
      anatomyCount: SPECIMEN_PASS.required_anatomy_parts.length,
      criteriaCount: SPECIMEN_PASS.visual_criteria.length
    };

    animate();
  </script>
</body>
</html>
```

- [ ] **Step 2: Run the focused test and verify it passes**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py -q
```

Expected: `5 passed`.

- [ ] **Step 3: Run related stage-02 tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_stage2_archive_instrument_reference_lock.py tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py -q
```

Expected: reference-lock and specimen-pass tests pass together.

- [ ] **Step 4: Check diff hygiene**

Run:

```bash
git diff --check
```

Expected: no output, exit 0.

- [ ] **Step 5: Commit the candidate page**

If Task 1 was not committed because of the no-failing-commit rule, include its files here too:

```bash
git add docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01/index.html docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01.json tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py
git commit -m "product: add archive specimen asset candidate"
```

Expected: commit succeeds with the JSON, HTML, and test file, and focused tests pass.

## Task 3: Browser Review And Visual Gate

**Files:**
- Inspect: `docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01/index.html`
- Test: `tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py`

- [ ] **Step 1: Run full vector aesthetics tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_*.py -q
```

Expected: all vector aesthetics tests pass. Existing pytest config warnings are acceptable if the suite passes.

- [ ] **Step 2: Open the candidate page in the local server**

Use:

```text
http://127.0.0.1:18747/docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01/index.html
```

Expected desktop observations:

- candidate specimen is visible and not blank
- specimen is centered in the canvas
- first viewport contains the review question, anatomy tags, criteria, and handoff notes
- links to current prototype and reference-lock page are visible
- no horizontal overflow

- [ ] **Step 3: Check mobile/narrow viewport**

Use a 390px-wide viewport or equivalent browser tool.

Expected narrow observations:

- page becomes single-column
- canvas remains visible
- side review panels do not overlap the canvas
- text does not overflow buttons or panels
- no horizontal overflow

- [ ] **Step 4: Check browser console logs**

Use browser dev logs.

Expected: no warning or error entries.

- [ ] **Step 5: Record visual gate result**

In the final response, state one of:

```text
visual gate: candidate appears stronger than current specimen asset
visual gate: candidate is technically stable but still visually weak
visual gate: blocked by rendering/runtime issue
```

This is a review judgment, not a test assertion. If the candidate is still weak, do not merge it into the main prototype; recommend GLB/model exploration for Pass 02.

- [ ] **Step 6: Final commit only if browser review required code/test fixes**

If browser review required adjustments, run focused tests again and commit with:

```bash
git add docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01/index.html tests/test_vector_aesthetics_stage2_archive_instrument_specimen_asset_pass01.py
git commit -m "fix: refine archive specimen asset candidate review"
```

If no files changed, do not create an empty commit.
