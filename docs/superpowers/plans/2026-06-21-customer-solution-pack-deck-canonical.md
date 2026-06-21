# Customer Solution Pack Deck Canonical Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the formal customer-facing VULCA Solution Pack from a checked-in PPTX/deck source, then export the customer PDF from that deck.

**Architecture:** Keep the existing HTML preview as the internal proof lab, move the customer-facing source of truth to a real PPTX generated with the OpenAI Presentations `@oai/artifact-tool` route, and keep the PDF as a generated delivery artifact. The builder must use source-safe Lane A/B/C assets, run preflight against both PPTX and PDF, and replace the current ReportLab PDF output path instead of creating competing customer PDFs.

**Tech Stack:** JavaScript ES modules, `@oai/artifact-tool`, macOS Keynote export through `osascript`, Python preflight, pytest, Poppler `pdfinfo`/`pdftoppm`.

---

## Source Roles

- `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/index.html` remains internal review only.
- `output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx` becomes the canonical customer deck source.
- `output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf` becomes the PDF exported from the PPTX route.
- `scripts/build_customer_solution_pack_pdf.py` remains a transition reference until the PPTX route has replaced the PDF output.

## File Structure

- Create: `scripts/build_customer_solution_pack_deck.mjs`
  - Approval-gated orchestration script.
  - Creates the external scratch workspace.
  - Runs `setup_artifact_tool_workspace.mjs`.
  - Copies the deck builder module into scratch.
  - Builds PPTX, renders slide PNGs/layout JSON/contact sheet, exports PDF through Keynote, and runs customer preflight.
- Create: `scripts/customer_solution_pack_deck_builder.mjs`
  - Pure deck authoring module that imports `@oai/artifact-tool`.
  - Reads a JSON config written by the orchestration script.
  - Builds the seven-slide customer sample deck with source-safe Lane A/B/C cards.
- Modify: `src/vulca/solution_pack_preflight.py`
  - Add `.pptx` text extraction from `ppt/slides/slide*.xml`.
- Modify: `tests/test_solution_pack_preflight.py`
  - Cover `.pptx` text extraction and PPTX customer-safety scanning.
- Create: `tests/test_customer_solution_pack_deck_script.py`
  - Cover the approval gate and output path policy without requiring `@oai/artifact-tool`.
- Modify: `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/README.md`
  - State that PPTX is the formal customer source and PDF is exported from PPTX.
- Outputs after approved generation:
  - `output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx`
  - `output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf`
  - `tmp/pdfs/customer-sample-rendered/page-*.png`

## Task 1: Add PPTX Text Extraction To Customer Preflight

**Files:**
- Modify: `src/vulca/solution_pack_preflight.py`
- Modify: `tests/test_solution_pack_preflight.py`

- [ ] **Step 1: Write the failing PPTX extraction test**

Append this test to `tests/test_solution_pack_preflight.py`:

```python
def test_read_artifact_text_extracts_pptx_slide_text(tmp_path: Path) -> None:
    pptx = tmp_path / "candidate.pptx"
    slide_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:sp>
        <p:txBody>
          <a:p><a:r><a:t>Named companies are public examples only.</a:t></a:r></a:p>
          <a:p><a:r><a:t>No VULCA customer or partner claim.</a:t></a:r></a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>
"""
    with zipfile.ZipFile(pptx, "w") as archive:
        archive.writestr("ppt/slides/slide1.xml", slide_xml)

    text = read_artifact_text(pptx)

    assert "Named companies are public examples only." in text
    assert "No VULCA customer or partner claim." in text
```

Also add this import at the top of the file:

```python
import zipfile
```

- [ ] **Step 2: Run the new test and verify the current code fails**

Run:

```bash
python3 -m pytest tests/test_solution_pack_preflight.py::test_read_artifact_text_extracts_pptx_slide_text -q
```

Expected result:

```text
FAILED tests/test_solution_pack_preflight.py::test_read_artifact_text_extracts_pptx_slide_text
```

The failure should come from trying to read the binary PPTX as UTF-8 text.

- [ ] **Step 3: Implement PPTX text extraction**

Modify `src/vulca/solution_pack_preflight.py` with these imports:

```python
import zipfile
from xml.etree import ElementTree
```

Add this function below `_read_pdf_text`:

```python
def _read_pptx_text(path: Path) -> str:
    slide_pattern = re.compile(r"ppt/slides/slide(\d+)\.xml$")
    pieces: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            slide_names = sorted(
                (
                    name
                    for name in archive.namelist()
                    if slide_pattern.match(name)
                ),
                key=lambda name: int(slide_pattern.match(name).group(1)),  # type: ignore[union-attr]
            )
            for slide_name in slide_names:
                root = ElementTree.fromstring(archive.read(slide_name))
                runs = [
                    node.text or ""
                    for node in root.iter()
                    if node.tag.endswith("}t") and (node.text or "").strip()
                ]
                if runs:
                    pieces.append(" ".join(runs))
    except zipfile.BadZipFile as exc:
        raise RuntimeError(f"Could not open PPTX archive {path}: {exc}") from exc
    except ElementTree.ParseError as exc:
        raise RuntimeError(f"Could not parse PPTX slide XML in {path}: {exc}") from exc
    return "\n".join(pieces)
```

Update `read_artifact_text`:

```python
def read_artifact_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf_text(path)
    if suffix == ".pptx":
        return _read_pptx_text(path)
    return path.read_text(encoding="utf-8", errors="replace")
```

- [ ] **Step 4: Run the PPTX extraction test**

Run:

```bash
python3 -m pytest tests/test_solution_pack_preflight.py::test_read_artifact_text_extracts_pptx_slide_text -q
```

Expected result:

```text
1 passed
```

- [ ] **Step 5: Add a PPTX scan test for forbidden internal material**

Append this test to `tests/test_solution_pack_preflight.py`:

```python
def test_scan_paths_flags_forbidden_text_inside_pptx(tmp_path: Path) -> None:
    pptx = tmp_path / "unsafe.pptx"
    slide_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:sp>
        <p:txBody>
          <a:p><a:r><a:t>Keep /Users/example/raw.png out of the deck.</a:t></a:r></a:p>
          <a:p><a:r><a:t>This still says debug overlay.</a:t></a:r></a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>
"""
    with zipfile.ZipFile(pptx, "w") as archive:
        archive.writestr("ppt/slides/slide1.xml", slide_xml)

    report = scan_paths([pptx])[0]

    assert report.ok is False
    assert {issue.rule_id for issue in report.issues} == {"local_path", "debug_overlay"}
```

- [ ] **Step 6: Run the full preflight test module**

Run:

```bash
python3 -m pytest tests/test_solution_pack_preflight.py -q
```

Expected result:

```text
8 passed
```

- [ ] **Step 7: Commit Task 1**

Run:

```bash
git add src/vulca/solution_pack_preflight.py tests/test_solution_pack_preflight.py
git commit -m "tools: scan customer solution pack pptx files"
```

## Task 2: Add The Approval-Gated Deck Build Orchestrator

**Files:**
- Create: `scripts/build_customer_solution_pack_deck.mjs`
- Create: `tests/test_customer_solution_pack_deck_script.py`

- [ ] **Step 1: Write the approval-gate test**

Create `tests/test_customer_solution_pack_deck_script.py`:

```python
from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_deck_builder_requires_explicit_approval() -> None:
    result = subprocess.run(
        ["node", "scripts/build_customer_solution_pack_deck.mjs"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "--approval-recorded" in result.stderr
    assert "output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx" in result.stderr
    assert "output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf" in result.stderr
```

- [ ] **Step 2: Run the test and verify the script is missing**

Run:

```bash
python3 -m pytest tests/test_customer_solution_pack_deck_script.py -q
```

Expected result:

```text
FAILED tests/test_customer_solution_pack_deck_script.py::test_deck_builder_requires_explicit_approval
```

The failure should mention that `scripts/build_customer_solution_pack_deck.mjs` does not exist.

- [ ] **Step 3: Create the orchestrator with approval gate and path policy**

Create `scripts/build_customer_solution_pack_deck.mjs`:

```javascript
#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import fsp from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const ROOT = path.resolve(path.dirname(__filename), "..");
const OUTPUT_PPTX = path.join(ROOT, "output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx");
const OUTPUT_PDF = path.join(ROOT, "output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf");
const SKILL_DIR =
  process.env.PRESENTATIONS_SKILL_DIR ||
  "/Users/yhryzy/.codex/plugins/cache/openai-primary-runtime/presentations/26.619.11828/skills/presentations";
const THREAD_ID = process.env.CODEX_THREAD_ID || `manual-${Date.now()}`;
const TASK_SLUG = "vulca-customer-solution-pack-deck";
const SCRATCH_ROOT = process.env.SCRATCH_ROOT || os.tmpdir();
const WORKSPACE = path.join(SCRATCH_ROOT, "codex-presentations", THREAD_ID, TASK_SLUG);
const TMP_DIR = path.join(WORKSPACE, "tmp");
const PREVIEW_DIR = path.join(TMP_DIR, "preview");
const LAYOUT_DIR = path.join(TMP_DIR, "layout");
const QA_DIR = path.join(TMP_DIR, "qa");

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd || ROOT,
    env: { ...process.env, ...(options.env || {}) },
    encoding: "utf8",
    stdio: options.stdio || "pipe",
  });
  if (result.status !== 0) {
    if (result.stdout) process.stdout.write(result.stdout);
    if (result.stderr) process.stderr.write(result.stderr);
    throw new Error(`${command} ${args.join(" ")} exited with ${result.status}`);
  }
  return result;
}

function requireApproval(args) {
  if (!args.includes("--approval-recorded")) {
    process.stderr.write(
      [
        "Refusing to generate formal customer deck without --approval-recorded.",
        `PPTX path: ${path.relative(ROOT, OUTPUT_PPTX)}`,
        `PDF path: ${path.relative(ROOT, OUTPUT_PDF)}`,
        "This command replaces the canonical customer sample outputs after main-review approval.",
        "",
      ].join("\n"),
    );
    process.exit(2);
  }
}

async function main() {
  requireApproval(process.argv.slice(2));
  await fsp.mkdir(TMP_DIR, { recursive: true });
  await fsp.mkdir(PREVIEW_DIR, { recursive: true });
  await fsp.mkdir(LAYOUT_DIR, { recursive: true });
  await fsp.mkdir(QA_DIR, { recursive: true });
  await fsp.mkdir(path.dirname(OUTPUT_PPTX), { recursive: true });
  await fsp.mkdir(path.dirname(OUTPUT_PDF), { recursive: true });

  const setupScript = path.join(SKILL_DIR, "container_tools/setup_artifact_tool_workspace.mjs");
  if (!fs.existsSync(setupScript)) {
    throw new Error(`Missing artifact-tool setup script: ${setupScript}`);
  }

  run("node", [setupScript, "--workspace", TMP_DIR], { stdio: "inherit" });

  const configPath = path.join(TMP_DIR, "deck-config.json");
  const scratchBuilderPath = path.join(TMP_DIR, "customer_solution_pack_deck_builder.mjs");
  const repoBuilderPath = path.join(ROOT, "scripts/customer_solution_pack_deck_builder.mjs");
  await fsp.copyFile(repoBuilderPath, scratchBuilderPath);
  await fsp.writeFile(
    configPath,
    JSON.stringify(
      {
        root: ROOT,
        outputPptx: OUTPUT_PPTX,
        outputPdf: OUTPUT_PDF,
        previewDir: PREVIEW_DIR,
        layoutDir: LAYOUT_DIR,
        qaDir: QA_DIR,
      },
      null,
      2,
    ),
  );

  run("node", [scratchBuilderPath, configPath], { cwd: TMP_DIR, stdio: "inherit" });
  run(
    "osascript",
    [
      "-e",
      `tell application "Keynote"
  activate
  set inputFile to POSIX file "${OUTPUT_PPTX}"
  set outputFile to POSIX file "${OUTPUT_PDF}"
  open inputFile
  set deckDocument to front document
  export deckDocument to outputFile as PDF
  close deckDocument saving no
end tell`,
    ],
    { stdio: "inherit" },
  );
  run("python3", ["scripts/customer_pdf_preflight.py", "--json", OUTPUT_PPTX, OUTPUT_PDF], { stdio: "inherit" });
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
```

- [ ] **Step 4: Make the script executable**

Run:

```bash
chmod +x scripts/build_customer_solution_pack_deck.mjs
```

- [ ] **Step 5: Run the approval-gate test**

Run:

```bash
python3 -m pytest tests/test_customer_solution_pack_deck_script.py -q
```

Expected result:

```text
1 passed
```

- [ ] **Step 6: Commit Task 2**

Run:

```bash
git add scripts/build_customer_solution_pack_deck.mjs tests/test_customer_solution_pack_deck_script.py
git commit -m "tools: add customer solution pack deck gate"
```

## Task 3: Build The Seven-Slide PPTX With Source-Safe Assets

**Files:**
- Create: `scripts/customer_solution_pack_deck_builder.mjs`

- [ ] **Step 1: Create the deck builder module**

Create `scripts/customer_solution_pack_deck_builder.mjs` with these top-level imports and constants:

```javascript
import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const SLIDE = { width: 1280, height: 720 };
const FRAME = { left: 72, top: 58, width: 1136, height: 604 };
const COLORS = {
  bg: "#edf4f0",
  paper: "#fbfcfa",
  ink: "#16211d",
  muted: "#62716b",
  teal: "#007f73",
  tealDark: "#00695f",
  tealSoft: "#dff1ec",
  blueSoft: "#e4f4f8",
  amber: "#9a6700",
  amberSoft: "#fff1d2",
  red: "#b63a31",
  redSoft: "#f8e0dc",
  panel: "#f7f6f1",
  line: "#c8d0cc",
};
```

Add these exact customer-visible source-safe asset paths through the runtime config:

```javascript
function assetPaths(root) {
  const base = path.join(root, "assets/research/vulca-evidence-packs/2026-06-20");
  return {
    creatifyCard: path.join(base, "creatify-deep-proof-v1/source-safe/creatify-source-safe-workflow-card-v1.png"),
    proyaCard: path.join(base, "proya-deep-proof-v1/vision-banana/proya-source-safe-distilled-card-v1.png"),
    seedreamCard: path.join(
      base,
      "seedream-byteplus-deep-proof-v1/source-safe/seedream-byteplus-source-safe-distilled-card-v1.png",
    ),
  };
}
```

- [ ] **Step 2: Add reusable deck primitives**

Add these functions to the builder:

```javascript
async function readImageBlob(imagePath) {
  const bytes = await fs.readFile(imagePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function textBox(slide, name, text, position, style) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = style;
  return shape;
}

function rect(slide, name, position, fill, line = COLORS.line, radius = "rounded-lg") {
  return slide.shapes.add({
    geometry: "roundRect",
    name,
    position,
    fill,
    line: { style: "solid", fill: line, width: 1 },
    borderRadius: radius,
  });
}

function addShell(slide, title, pageNumber) {
  slide.background.fill = COLORS.bg;
  rect(slide, "paper", { left: 36, top: 30, width: 1208, height: 660 }, COLORS.paper, COLORS.paper, "rounded-lg");
  slide.shapes.add({
    geometry: "rect",
    name: "top-rule",
    position: { left: 36, top: 60, width: 1208, height: 10 },
    fill: COLORS.teal,
    line: { style: "solid", fill: COLORS.teal, width: 0 },
  });
  textBox(slide, "kicker", "VULCA SOLUTION PACK V1", { left: 72, top: 96, width: 420, height: 28 }, {
    fontSize: 16,
    color: COLORS.muted,
  });
  textBox(
    slide,
    "page-marker",
    `Public example sample / Page ${pageNumber}`,
    { left: 850, top: 96, width: 360, height: 28 },
    { fontSize: 16, color: COLORS.muted, alignment: "right" },
  );
  textBox(slide, "title", title, { left: 72, top: 132, width: 1040, height: 58 }, {
    fontSize: 40,
    bold: true,
    color: COLORS.ink,
  });
}

function addFooter(slide) {
  textBox(
    slide,
    "boundary-footer",
    "Named companies are public examples only. They do not imply a VULCA customer, partner, endorsement, authorization source, or finding.",
    { left: 72, top: 650, width: 1136, height: 30 },
    { fontSize: 11, color: COLORS.muted },
  );
}
```

- [ ] **Step 3: Add the seven slide authoring functions**

Use these slide titles and roles exactly:

```javascript
const SLIDE_PLAN = [
  {
    title: "VULCA Solution Pack v1",
    role: "Position the pack as release-evidence packets for AI-assisted visual assets.",
  },
  {
    title: "What VULCA Produces",
    role: "Map Lane A, Lane B, and Lane C without implying customer relationships.",
  },
  {
    title: "Before / After: AI Ad Workflow Handoff",
    role: "Make Lane C the hero proof with the Creatify source-safe card.",
  },
  {
    title: "Supporting Proof A: Product-Truth Evidence",
    role: "Show Lane A as structured product-truth evidence using the PROYA source-safe card.",
  },
  {
    title: "Supporting Proof B: AI Publishability Context",
    role: "Show Lane B as structured generated-asset publishability context using the Seedream source-safe card.",
  },
  {
    title: "A Bounded Pilot Shape",
    role: "Define intake, field read, evidence card, and readout.",
  },
  {
    title: "Review Ask And Boundaries",
    role: "Ask for workflow feedback while excluding legal, rights, platform, safety, and performance claims.",
  },
];
```

Implement each slide as an editable deck page, using the source-safe cards only on slides 3, 4, and 5:

```javascript
async function addLaneCHero(presentation, assets) {
  const slide = presentation.slides.add();
  addShell(slide, "Before / After: AI Ad Workflow Handoff", 3);
  rect(slide, "before-panel", { left: 76, top: 236, width: 430, height: 150 }, COLORS.redSoft, COLORS.red);
  textBox(slide, "before-title", "Before VULCA", { left: 104, top: 260, width: 360, height: 34 }, {
    fontSize: 24,
    bold: true,
    color: COLORS.red,
  });
  textBox(
    slide,
    "before-copy",
    "A product URL, listing, image, or brief can quickly become campaign candidates while source input, review anatomy, export state, missing fields, and release owner sit in different places.",
    { left: 104, top: 305, width: 360, height: 64 },
    { fontSize: 17, color: COLORS.ink },
  );
  rect(slide, "after-panel", { left: 76, top: 424, width: 430, height: 150 }, COLORS.tealSoft, COLORS.teal);
  textBox(slide, "after-title", "After VULCA", { left: 104, top: 448, width: 360, height: 34 }, {
    fontSize: 24,
    bold: true,
    color: COLORS.teal,
  });
  textBox(
    slide,
    "after-copy",
    "The same flow becomes a release-evidence packet: source input, generated candidate, hook/body/CTA review, export state, missing-field list, owner route, and human review gate.",
    { left: 104, top: 492, width: 360, height: 68 },
    { fontSize: 17, color: COLORS.ink },
  );
  slide.images.add({
    blob: await readImageBlob(assets.creatifyCard),
    contentType: "image/png",
    alt: "Source-safe AI ad workflow evidence card",
    fit: "contain",
    position: { left: 598, top: 212, width: 616, height: 390 },
    geometry: "roundRect",
    borderRadius: "rounded-lg",
  });
  addFooter(slide);
}
```

Add these remaining authoring helpers and slide functions:

```javascript
function addPill(slide, name, text, left, top, width, fill, color) {
  rect(slide, `${name}-pill`, { left, top, width, height: 30 }, fill, color, "rounded-full");
  textBox(slide, `${name}-pill-text`, text, { left, top: top + 6, width, height: 18 }, {
    fontSize: 12,
    bold: true,
    color,
    alignment: "center",
  });
}

function addFieldCard(slide, name, title, body, position, fill, color) {
  rect(slide, `${name}-card`, position, fill, color, "rounded-lg");
  textBox(slide, `${name}-title`, title, {
    left: position.left + 18,
    top: position.top + 18,
    width: position.width - 36,
    height: 26,
  }, { fontSize: 17, bold: true, color });
  textBox(slide, `${name}-body`, body, {
    left: position.left + 18,
    top: position.top + 56,
    width: position.width - 36,
    height: position.height - 72,
  }, { fontSize: 16, color: COLORS.ink });
}

async function addTitleSlide(presentation) {
  const slide = presentation.slides.add();
  addShell(slide, "VULCA Solution Pack v1", 1);
  textBox(
    slide,
    "positioning-copy",
    "Release-evidence packets for AI-assisted visual assets.",
    { left: 72, top: 216, width: 850, height: 36 },
    { fontSize: 20, bold: true, color: COLORS.teal },
  );
  textBox(
    slide,
    "problem-copy",
    "AI-assisted visual production is scaling across commerce, campaign, generated media, and ad workflows. The bottleneck is no longer only making an asset. The bottleneck is explaining what it came from, what it represents, what still needs review, and who owns the release decision.",
    { left: 72, top: 286, width: 770, height: 150 },
    { fontSize: 19, color: COLORS.ink },
  );
  addPill(slide, "public", "public examples only", 72, 540, 160, COLORS.tealSoft, COLORS.tealDark);
  addPill(slide, "source", "source-backed", 252, 540, 142, COLORS.tealSoft, COLORS.tealDark);
  addPill(slide, "review", "human-reviewed", 414, 540, 158, COLORS.amberSoft, COLORS.amber);
  addFooter(slide);
}

async function addLaneMap(presentation) {
  const slide = presentation.slides.add();
  addShell(slide, "What VULCA Produces", 2);
  textBox(
    slide,
    "summary-copy",
    "A compact packet that connects source context, visual or generated-output fields, review questions, owner route, and a bounded human review gate.",
    { left: 72, top: 214, width: 1120, height: 46 },
    { fontSize: 17, color: COLORS.muted },
  );
  const laneTop = 306;
  const laneWidth = 342;
  addFieldCard(
    slide,
    "lane-a",
    "Lane A / Product-truth",
    "Existing commercial material and product claims become source-backed evidence cards: visible claim, product representation, source context, channel role, and release owner.",
    { left: 90, top: laneTop, width: laneWidth, height: 192 },
    COLORS.tealSoft,
    COLORS.tealDark,
  );
  addFieldCard(
    slide,
    "lane-b",
    "Lane B / AI publishability",
    "Generated assets are paired with input or reference context, model or workflow context, output state, label posture, unresolved fields, and owner route.",
    { left: 469, top: laneTop, width: laneWidth, height: 192 },
    COLORS.amberSoft,
    COLORS.amber,
  );
  addFieldCard(
    slide,
    "lane-c",
    "Lane C / AI ad workflow",
    "Product URL, listing, or brief-to-ad workflows become handoff packets: source input, generated candidate, review anatomy, export state, and campaign owner.",
    { left: 848, top: laneTop, width: laneWidth, height: 192 },
    COLORS.redSoft,
    COLORS.red,
  );
  textBox(
    slide,
    "reading-order",
    "Default reading order for this sample: Lane C is the main before/after workflow story. Lane A and Lane B show that the same source-backed method also works for product claims and generated assets.",
    { left: 90, top: 540, width: 1100, height: 58 },
    { fontSize: 17, color: COLORS.ink },
  );
  addFooter(slide);
}

async function addLaneAProof(presentation, assets) {
  const slide = presentation.slides.add();
  addShell(slide, "Supporting Proof A: Product-Truth Evidence", 4);
  textBox(
    slide,
    "lane-a-summary",
    "A public product or campaign surface can be translated into reviewable fields before reuse.",
    { left: 72, top: 214, width: 900, height: 34 },
    { fontSize: 17, color: COLORS.muted },
  );
  addFieldCard(slide, "a-source", "1. Public source surface", "Public commercial material, product representation, offer cue, and channel context are preserved.", { left: 82, top: 286, width: 262, height: 112 }, COLORS.blueSoft, "#0d6f91");
  addFieldCard(slide, "a-field", "2. VULCA field read", "Claim text, representation surface, reuse context, and owner route are separated into explicit fields.", { left: 370, top: 286, width: 262, height: 112 }, COLORS.tealSoft, COLORS.teal);
  addFieldCard(slide, "a-output", "3. Review output", "A product-truth packet shows what is known, what is missing, and who should decide release.", { left: 82, top: 424, width: 262, height: 112 }, COLORS.amberSoft, COLORS.amber);
  addFieldCard(slide, "a-boundary", "Boundary", "This is a public example for workflow discussion, not a legal, rights, platform, release-readiness, or relationship claim.", { left: 370, top: 424, width: 262, height: 112 }, COLORS.amberSoft, COLORS.amber);
  slide.images.add({
    blob: await readImageBlob(assets.proyaCard),
    contentType: "image/png",
    alt: "Source-safe product-truth evidence card",
    fit: "contain",
    position: { left: 700, top: 260, width: 474, height: 306 },
    geometry: "roundRect",
    borderRadius: "rounded-lg",
  });
  addFooter(slide);
}

async function addLaneBProof(presentation, assets) {
  const slide = presentation.slides.add();
  addShell(slide, "Supporting Proof B: AI Publishability Context", 5);
  textBox(
    slide,
    "lane-b-summary",
    "Generated media should not be reviewed as a file alone. The packet needs source or reference context, model or workflow context, output state, label posture, and owner route.",
    { left: 72, top: 210, width: 1040, height: 54 },
    { fontSize: 17, color: COLORS.muted },
  );
  addFieldCard(slide, "b-records", "1. Public records", "Official model or tool pages and tutorial context become source records.", { left: 82, top: 292, width: 262, height: 112 }, COLORS.blueSoft, "#0d6f91");
  addFieldCard(slide, "b-normalized", "2. Normalized fields", "Model context, input reference, output state, label posture, and reuse owner are split out.", { left: 370, top: 292, width: 262, height: 112 }, COLORS.tealSoft, COLORS.teal);
  addFieldCard(slide, "b-packet", "3. Review packet", "The output states what is reviewable, missing, source-backed, and not yet approved.", { left: 82, top: 430, width: 262, height: 112 }, COLORS.amberSoft, COLORS.amber);
  addFieldCard(slide, "b-boundary", "Boundary", "This is not model quality scoring, model-safety certification, copyright clearance, policy approval, or benchmark comparison.", { left: 370, top: 430, width: 262, height: 112 }, COLORS.amberSoft, COLORS.amber);
  slide.images.add({
    blob: await readImageBlob(assets.seedreamCard),
    contentType: "image/png",
    alt: "Source-safe AI publishability evidence card",
    fit: "contain",
    position: { left: 700, top: 260, width: 474, height: 306 },
    geometry: "roundRect",
    borderRadius: "rounded-lg",
  });
  addFooter(slide);
}

async function addPilotShape(presentation) {
  const slide = presentation.slides.add();
  addShell(slide, "A Bounded Pilot Shape", 6);
  textBox(
    slide,
    "pilot-summary",
    "The first useful step is small: public examples or sanitized assets, one review lane, a short readout, and a clear owner route.",
    { left: 72, top: 214, width: 1100, height: 42 },
    { fontSize: 17, color: COLORS.muted },
  );
  addFieldCard(slide, "pilot-intake", "1. Intake", "Public example, sanitized asset, product URL, listing, brief, or generated candidate.", { left: 90, top: 308, width: 518, height: 118 }, COLORS.tealSoft, COLORS.teal);
  addFieldCard(slide, "pilot-read", "2. Field Read", "Source context, visible claim or output context, review anatomy, output state, and missing fields.", { left: 672, top: 308, width: 518, height: 118 }, COLORS.tealSoft, COLORS.teal);
  addFieldCard(slide, "pilot-card", "3. Evidence Card", "A compact review object that a human owner can inspect and route.", { left: 90, top: 462, width: 518, height: 118 }, COLORS.amberSoft, COLORS.amber);
  addFieldCard(slide, "pilot-readout", "4. Readout", "What is ready to discuss, what is missing, who owns the next decision, and what should wait.", { left: 672, top: 462, width: 518, height: 118 }, COLORS.amberSoft, COLORS.amber);
  addFooter(slide);
}

async function addReviewAsk(presentation) {
  const slide = presentation.slides.add();
  addShell(slide, "Review Ask And Boundaries", 7);
  addFieldCard(
    slide,
    "ask",
    "Useful first response",
    "Which visual workflow should be turned into a source-backed review packet first: product-truth, AI publishability, or AI ad workflow handoff?",
    { left: 90, top: 270, width: 500, height: 150 },
    COLORS.tealSoft,
    COLORS.teal,
  );
  addFieldCard(
    slide,
    "what-we-show",
    "What the sample shows",
    "A repeatable packet shape: source context, representation or generated-output field read, unresolved questions, owner route, and human review gate.",
    { left: 90, top: 450, width: 500, height: 150 },
    COLORS.tealSoft,
    COLORS.teal,
  );
  addFieldCard(
    slide,
    "not-claims",
    "Not claiming",
    "No legal advice, rights clearance, platform approval, model-safety certification, release-readiness certification, performance measurement, ROI, CPA, CTR, ROAS, benchmark superiority, customer relationship, partnership, endorsement, authorization, or audit finding.",
    { left: 670, top: 270, width: 520, height: 330 },
    COLORS.redSoft,
    COLORS.red,
  );
  addFooter(slide);
}
```

Use no font smaller than 16pt except the shared footer at 11pt. Keep slide titles at 40pt.

- [ ] **Step 4: Add the build/export main function**

Add this main function to `scripts/customer_solution_pack_deck_builder.mjs`:

```javascript
async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  const configPath = process.argv[2];
  if (!configPath) {
    throw new Error("Usage: node customer_solution_pack_deck_builder.mjs <deck-config.json>");
  }
  const config = JSON.parse(await fs.readFile(configPath, "utf8"));
  await fs.mkdir(config.previewDir, { recursive: true });
  await fs.mkdir(config.layoutDir, { recursive: true });

  const assets = assetPaths(config.root);
  const presentation = Presentation.create({ slideSize: SLIDE });

  await addTitleSlide(presentation);
  await addLaneMap(presentation);
  await addLaneCHero(presentation, assets);
  await addLaneAProof(presentation, assets);
  await addLaneBProof(presentation, assets);
  await addPilotShape(presentation);
  await addReviewAsk(presentation);

  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(config.previewDir, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 1 }));
    await fs.writeFile(path.join(config.layoutDir, `${stem}.layout.json`), await (await slide.export({ format: "layout" })).text());
  }

  await writeBlob(path.join(config.qaDir, "deck-contact-sheet.webp"), await presentation.export({
    format: "webp",
    montage: true,
    scale: 1,
  }));

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(config.outputPptx);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

- [ ] **Step 5: Run the approved deck build**

Run:

```bash
node scripts/build_customer_solution_pack_deck.mjs --approval-recorded
```

Expected result:

```text
The command creates output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx
The command creates output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf
The command prints preflight JSON with "ok": true
```

- [ ] **Step 6: Inspect the generated preview contact sheet**

Open the latest scratch contact sheet printed by the script, or locate it under:

```text
$SCRATCH_ROOT/codex-presentations/$THREAD_ID/vulca-customer-solution-pack-deck/tmp/qa/deck-contact-sheet.webp
```

Check these visible conditions:

- Every slide has the same title band and footer placement.
- Slides 3, 4, and 5 use source-safe card images, not raw screenshots.
- No title wraps.
- No image covers the footer.
- No dense page has unreadable field text.
- Slide 4 and Slide 5 have balanced text/image distribution.

- [ ] **Step 7: Fix any visual defects in the PPTX source**

Make all visual fixes inside `scripts/customer_solution_pack_deck_builder.mjs`, then rerun:

```bash
node scripts/build_customer_solution_pack_deck.mjs --approval-recorded
```

Expected result:

```text
The replacement PPTX and PDF are generated at the same canonical output paths.
```

## Task 4: Update Docs So PPTX Is Canonical

**Files:**
- Modify: `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/README.md`

- [ ] **Step 1: Replace the customer sample generation section**

In `assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/README.md`, replace the paragraph that says to regenerate the customer PDF with ReportLab:

````markdown
Formal customer sample source:

```text
output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx
```

Formal customer sample PDF:

```text
output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf
```

The PPTX is the canonical customer-facing source. The PDF is exported from that
PPTX after explicit approval. The HTML preview remains the internal proof lab;
the ReportLab PDF builder is retained only as a transition reference.

Regenerate the formal customer sample only after approval:

```bash
node scripts/build_customer_solution_pack_deck.mjs --approval-recorded
```
````

- [ ] **Step 2: Verify docs do not describe ReportLab as canonical**

Run:

```bash
rg -n "ReportLab|build_customer_solution_pack_pdf|canonical customer|customer-facing PDF" assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/README.md docs/superpowers/specs/2026-06-21-customer-solution-pack-deck-canonical-design.md
```

Expected result:

```text
ReportLab appears only as transition/reference language.
build_customer_solution_pack_pdf appears only as transition/reference language.
```

- [ ] **Step 3: Commit Task 4 with the deck builder if Task 3 is visually clean**

Run:

```bash
git add scripts/customer_solution_pack_deck_builder.mjs assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/README.md output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf
git commit -m "assets: make customer solution pack deck canonical"
```

## Task 5: Final Verification Gate

**Files:**
- Read: `output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx`
- Read: `output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf`

- [ ] **Step 1: Run customer preflight on both deliverables**

Run:

```bash
python3 scripts/customer_pdf_preflight.py --json output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf
```

Expected result:

```json
{
  "ok": true,
  "issue_count": 0
}
```

- [ ] **Step 2: Inspect PDF metadata**

Run:

```bash
/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pdfinfo output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf
```

Expected checks:

- `Pages: 7`
- `Encrypted: no`
- no JavaScript field is present

- [ ] **Step 3: Render the customer PDF**

Run:

```bash
rm -rf tmp/pdfs/customer-sample-rendered
mkdir -p tmp/pdfs/customer-sample-rendered
/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pdftoppm -png output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf tmp/pdfs/customer-sample-rendered/page
```

Expected result:

```text
tmp/pdfs/customer-sample-rendered/page-1.png
tmp/pdfs/customer-sample-rendered/page-2.png
tmp/pdfs/customer-sample-rendered/page-3.png
tmp/pdfs/customer-sample-rendered/page-4.png
tmp/pdfs/customer-sample-rendered/page-5.png
tmp/pdfs/customer-sample-rendered/page-6.png
tmp/pdfs/customer-sample-rendered/page-7.png
```

- [ ] **Step 4: Run the regression tests**

Run:

```bash
python3 -m pytest tests/test_solution_pack_preflight.py tests/test_customer_solution_pack_deck_script.py -q
```

Expected result:

```text
9 passed
```

- [ ] **Step 5: Run whitespace and path sanity checks**

Run:

```bash
git diff --check
rg -n "file://|/Users/|\\.codex/|debug overlay|raw crop|crop box|source-log|Alibaba case-study" output/pptx output/pdf assets/research/vulca-evidence-packs/2026-06-20/internal-page-preview-v1/README.md
```

Expected result:

```text
git diff --check exits 0.
rg exits 1 because no searched internal-source term appears in generated customer-visible output or the customer-material README.
```

- [ ] **Step 6: Final review with the user**

Show the user:

- PPTX path: `output/pptx/vulca-solution-pack-v1-customer-sample-public-examples.pptx`
- PDF path: `output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf`
- Rendered PDF preview directory: `tmp/pdfs/customer-sample-rendered/`
- Preflight result summary: `ok=true`, issue count `0`

Ask for inline review of the rendered pages before any outreach copy or email task resumes.

## Self-Review

- Spec coverage: The plan implements the PPTX canonical source, source-safe customer cards, approval gate, PDF export from PPTX, preflight for both artifacts, and README role clarity.
- No extra customer PDF path is introduced. The canonical output paths remain the existing customer sample paths.
- The plan keeps company names as public examples only and excludes customer, partner, endorsement, authorization, audit, legal, rights, platform, safety certification, and performance claims.
- The deck uses real source-safe assets already produced by the Lane A/B/C evidence folders.
- The verification gate checks PPTX text, exported PDF text, PDF metadata, PDF render output, and regression tests.
