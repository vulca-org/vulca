import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const selectedUsecaseId = "usecase_design_to_production_platform_launch";
const artifactToolPath =
  process.env.ARTIFACT_TOOL_PATH ??
  "/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";
const artifactToolPackage =
  process.env.ARTIFACT_TOOL_PACKAGE ??
  "/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool";

const { Presentation, PresentationFile } = await import(pathToFileURL(artifactToolPath).href);

const W = 1280;
const H = 720;
const MAIN_CANVAS = { x: 54, y: 88, w: 1170, h: 542 };

const C = {
  ink: "#111318",
  paper: "#f4f1ea",
  white: "#ffffff",
  line: "#d1d5db",
  muted: "#5e6874",
  midnight: "#11161d",
  graphite: "#252b34",
  blue: "#245fdd",
  cyan: "#6cc5d8",
  signal: "#e85237",
  green: "#0f8a66",
  fog: "#eef2f5",
  cream: "#f8f4eb",
  wheat: "#e7dcc7",
  amber: "#c8962d",
  plum: "#6d4e8a",
};

const EXPECTED_RUN2_36_TRACE_FIELDS = [
  "run2_35_visual_evidence_asset_realism_ids",
  "run2_35_editorial_composition_memory_id",
  "run2_35_realism_gate_id",
  "run2_35_observable_product_state",
  "run2_35_hero_canvas_share_target",
  "run2_35_visual_evidence_realism_execution_status",
  "run2_36_code_module_ids",
];

const RUN2_36_INPUTS = {
  mainSurfaceVisualEvidenceAudit: `${pack}/results/run2_34_main_surface_visual_evidence_audit.json`,
  priorMainSurfaceVisualEvidenceRerun: `${pack}/results/run2_33_main_surface_visual_evidence_rerun_result.json`,
  visualEvidenceRealismWorkflowResult: `${pack}/results/run2_35_visual_evidence_realism_workflow_result.json`,
  visualEvidenceAssetRealismMemory: `${pack}/run2_35_visual_evidence_asset_realism_memory.json`,
  editorialCompositionMemory: `${pack}/run2_35_editorial_composition_memory.json`,
  visualEvidenceWorkflowGates: `${pack}/run2_35_visual_evidence_workflow_gates.json`,
};
const RUN2_36_DATA_INPUTS = [
  RUN2_36_INPUTS.mainSurfaceVisualEvidenceAudit,
  RUN2_36_INPUTS.priorMainSurfaceVisualEvidenceRerun,
  RUN2_36_INPUTS.visualEvidenceRealismWorkflowResult,
  RUN2_36_INPUTS.visualEvidenceAssetRealismMemory,
  RUN2_36_INPUTS.editorialCompositionMemory,
  RUN2_36_INPUTS.visualEvidenceWorkflowGates,
];

const baseSlides = [
  {
    role: "cover",
    title: "Design memory becomes a launch system.",
    claim: "Editable PPT output is controlled by selected design knowledge before code draws the deck.",
  },
  {
    role: "setup",
    title: "Prompt-only decks lose the product thread.",
    claim: "One-off prompting forgets the case, source boundaries, design memory, and release gates.",
  },
  {
    role: "contrast",
    title: "The same brief changes when evidence is selected first.",
    claim: "The selected usecase turns a generic AI claim into a source-bound product workflow.",
  },
  {
    role: "proof",
    title: "Content memory gives every slide a job.",
    claim: "Each role receives visible content obligations and native visual evidence slots before generation.",
  },
  {
    role: "climax",
    title: "One generated proof object owns the room.",
    claim: "The climax is a concrete editable result object, not another abstract selector diagram.",
  },
  {
    role: "close",
    title: "The handoff is blocked until the proof survives review.",
    claim: "The system can generate a stronger internal deck, but public release stays gated.",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-36-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.36 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [
      `${pack}/results/run2_34_main_surface_visual_evidence_audit.json`,
      `${pack}/results/run2_33_main_surface_visual_evidence_rerun_result.json`,
      `${pack}/results/run2_35_visual_evidence_realism_workflow_result.json`,
      `${pack}/run2_35_visual_evidence_asset_realism_memory.json`,
      `${pack}/run2_35_editorial_composition_memory.json`,
      `${pack}/run2_35_visual_evidence_workflow_gates.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "docs/product/ppt-run1-5-product-lab/",
    ],
    palette: {
      bg: "#f5f6f8",
      rail: "#374151",
      accent: C.blue,
      accent2: "#bfcbd8",
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d8dde4",
      gate: "#e9edf3",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Make this launch deck look designed.",
        "Explain why prompt-only slides are weak.",
        "Show a before and after.",
        "Add evidence that the system works.",
        "Make the big result feel important.",
        "Close with next steps.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-36-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.36 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [
      `${pack}/results/run2_34_main_surface_visual_evidence_audit.json`,
      `${pack}/results/run2_33_main_surface_visual_evidence_rerun_result.json`,
      `${pack}/results/run2_35_visual_evidence_realism_workflow_result.json`,
      `${pack}/run2_35_visual_evidence_asset_realism_memory.json`,
      `${pack}/run2_35_editorial_composition_memory.json`,
      `${pack}/run2_35_visual_evidence_workflow_gates.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
    ],
    palette: {
      bg: "#f3f6fb",
      rail: "#263247",
      accent: C.blue,
      accent2: C.green,
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d3dbe7",
      gate: "#e8edf5",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "The baseline names the product workflow.",
        "The setup is readable but still broad.",
        "The contrast remains evenly weighted.",
        "The proof surface is more process than product.",
        "The climax has a claim but not a stage.",
        "The close is correct, not decisive.",
      ][index],
    })),
  },
  {
    armId: "run2_36_full_visual_evidence_realism",
    slug: "ppt-run2-36-full-vulca",
    label: "Run 2.36 full visual-evidence realism",
    kicker: "RUN 2.36 / VISUAL EVIDENCE REALISM",
    footer: "run2_36_full_visual_evidence_realism | Run 2.35 realism + editorial composition + gates | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/sources.json`,
      `${pack}/results/run2_34_main_surface_visual_evidence_audit.json`,
      `${pack}/results/run2_33_main_surface_visual_evidence_rerun_result.json`,
      `${pack}/results/run2_35_visual_evidence_realism_workflow_result.json`,
      `${pack}/run2_35_visual_evidence_asset_realism_memory.json`,
      `${pack}/run2_35_editorial_composition_memory.json`,
      `${pack}/run2_35_visual_evidence_workflow_gates.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    forbidden: [
      "docs/product/ppt-run1-5-product-lab/",
      "copied source visuals",
      "raw tutorial media copied into slide surface",
      "source brand marks",
      "winner claims before scoring",
    ],
    palette: {
      bg: "#f6f1e8",
      rail: C.midnight,
      accent: C.midnight,
      accent2: C.cyan,
      proof: C.signal,
      panel: C.white,
      title: "#0e1218",
      muted: "#58636f",
      rule: "#d5cbb9",
      gate: C.midnight,
      surface: "#edf3f2",
    },
    slides: baseSlides,
  },
  {
    armId: "bad_visual_evidence_realism_memory",
    slug: "ppt-run2-36-bad-visual-evidence-realism-memory",
    label: "Bad visual-evidence realism memory control",
    kicker: "RUN 2.36 / NEGATIVE CONTROL",
    footer: "bad_visual_evidence_realism_memory | usecase label only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, `selected_usecase_label:${selectedUsecaseId}`],
    forbidden: [
      `${pack}/results/run2_34_main_surface_visual_evidence_audit.json`,
      `${pack}/results/run2_33_main_surface_visual_evidence_rerun_result.json`,
      `${pack}/results/run2_35_visual_evidence_realism_workflow_result.json`,
      `${pack}/run2_35_visual_evidence_asset_realism_memory.json`,
      `${pack}/run2_35_editorial_composition_memory.json`,
      `${pack}/run2_35_visual_evidence_workflow_gates.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "manual Run 2.36 pack repair before scoring",
    ],
    palette: {
      bg: "#f1eadb",
      rail: "#695d3a",
      accent: "#75683f",
      accent2: "#d3c28d",
      panel: "#faf4e8",
      title: "#2b271e",
      muted: "#675f4c",
      rule: "#dacfb8",
      gate: "#eadfbe",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "The usecase label appears, but the slide is generic.",
        "The setup cannot prove the selected content route.",
        "The contrast becomes labels without source-bound evidence.",
        "The proof panel has no memory-backed obligations.",
        "The climax is another diagram.",
        "The close lists gates it did not execute.",
      ][index],
    })),
  },
];

function readJson(relPath) {
  return JSON.parse(fs.readFileSync(path.join(root, relPath), "utf8"));
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function writeJson(file, data) {
  fs.writeFileSync(file, `${JSON.stringify(data, null, 2)}\n`);
}

function resetWorkspace(workspace) {
  fs.rmSync(workspace, { recursive: true, force: true });
  for (const dir of ["output", "preview", "layout/final", "qa", "slides", "assets", "node_modules/@oai"]) {
    ensureDir(path.join(workspace, dir));
  }
  fs.writeFileSync(path.join(workspace, "package.json"), `${JSON.stringify({ private: true, type: "module" }, null, 2)}\n`);
  const linkPath = path.join(workspace, "node_modules/@oai/artifact-tool");
  try {
    fs.symlinkSync(artifactToolPackage, linkPath, "dir");
  } catch (error) {
    if (error.code !== "EEXIST") throw error;
  }
}

function colorLine(color = C.line, width = 1) {
  return { color, width };
}

const ctx = {
  fonts: {
    title: "Aptos Display",
    body: "Aptos",
    mono: "Aptos Mono",
  },
  addShape(slide, opts) {
    return slide.shapes.add({
      geometry: opts.geometry ?? "rect",
      position: { left: opts.x, top: opts.y, width: opts.w, height: opts.h },
      fill: opts.fill,
      line: opts.line,
    });
  },
  addText(slide, opts) {
    const shape = slide.shapes.add({
      geometry: "rect",
      position: { left: opts.x, top: opts.y, width: opts.w, height: opts.h },
      fill: opts.fill,
      line: opts.line,
    });
    shape.text.set(String(opts.text ?? ""));
    shape.text.fontSize = opts.fontSize ?? 14;
    shape.text.color = opts.color ?? C.ink;
    shape.text.bold = Boolean(opts.bold);
    shape.text.typeface = opts.typeface ?? (opts.title ? ctx.fonts.title : opts.mono ? ctx.fonts.mono : ctx.fonts.body);
    if (opts.align) shape.text.alignment = opts.align;
    if (opts.verticalAlign) shape.text.verticalAlignment = opts.verticalAlign;
    shape.text.insets = opts.insets ?? { left: 0, right: 0, top: 0, bottom: 0 };
    return shape;
  },
};

function rect(slide, x, y, w, h, fill, line) {
  if (w <= 0 || h <= 0) return null;
  return ctx.addShape(slide, { x, y, w, h, fill, line });
}

function ellipse(slide, x, y, w, h, fill, line) {
  if (w <= 0 || h <= 0) return null;
  return ctx.addShape(slide, { geometry: "ellipse", x, y, w, h, fill, line });
}

function text(slide, value, x, y, w, h, opts = {}) {
  return ctx.addText(slide, { text: value, x, y, w, h, ...opts });
}

function chip(slide, label, x, y, w, fill, color = C.ink) {
  text(slide, label, x, y, w, 28, {
    fontSize: 10,
    bold: true,
    mono: true,
    color,
    fill,
    line: colorLine(C.line, 1),
    insets: { left: 10, right: 8, top: 7, bottom: 5 },
  });
}

function wordsIn(value) {
  return String(value ?? "")
    .trim()
    .split(/\s+/)
    .filter(Boolean).length;
}

function createSlideMetrics(role) {
  return {
    role,
    textBoxCount: 0,
    visibleWords: 0,
    proofObjects: 0,
    zones: 0,
    workflowObjects: 0,
    gateObjects: 0,
    contentCards: 0,
    visualEvidenceObjects: 0,
    realisticVisualEvidenceObjects: 0,
    thickenedSurfaceProofPoints: 0,
    heroShare: 0,
    visualModuleIds: new Set(),
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun236Module(metrics, functionName) {
  metrics.visualModuleIds.add(functionName);
}

function registerProof(metrics, count = 1) {
  metrics.proofObjects += count;
}

function registerZones(metrics, count) {
  metrics.zones = Math.max(metrics.zones, count);
}

function registerWorkflow(metrics, count) {
  metrics.workflowObjects = Math.max(metrics.workflowObjects, count);
}

function registerGate(metrics, count = 1) {
  metrics.gateObjects = Math.max(metrics.gateObjects, count);
}

function registerContentCards(metrics, count = 1) {
  metrics.contentCards += count;
}

function registerVisualEvidence(metrics, count = 1) {
  metrics.visualEvidenceObjects += count;
}

function registerRealisticVisualEvidence(metrics, count = 1) {
  metrics.realisticVisualEvidenceObjects += count;
  registerVisualEvidence(metrics, count);
}

function registerThickenedSurfaceProofPoints(metrics, count = 1) {
  metrics.thickenedSurfaceProofPoints = Math.max(metrics.thickenedSurfaceProofPoints, count);
}

function registerHero(metrics, x, y, w, h) {
  const area = Math.max(1, MAIN_CANVAS.w * MAIN_CANVAS.h);
  metrics.heroShare = Math.max(metrics.heroShare, (w * h) / area);
}

function base(slide, arm, n) {
  rect(slide, 0, 0, W, H, arm.palette.bg);
  rect(slide, 0, 0, 16, H, arm.palette.rail);
  text(slide, arm.kicker, 54, 30, 500, 22, {
    fontSize: 10,
    bold: true,
    mono: true,
    color: arm.palette.accent,
  });
  text(slide, `${String(n).padStart(2, "0")} / 06`, 1110, 30, 114, 22, {
    fontSize: 10,
    mono: true,
    color: arm.palette.muted,
    align: "right",
  });
  rect(slide, 54, 70, 1170, 2, arm.palette.rule ?? C.line);
  text(slide, arm.footer, 612, 674, 612, 22, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
    align: "right",
  });
  for (let i = 1; i <= 6; i += 1) {
    rect(slide, 54 + (i - 1) * 20, 684, i === n ? 16 : 8, 5, i === n ? arm.palette.accent : C.line);
  }
}

function moduleLabel(slide, x, y, label, arm) {
  chip(slide, label, x, y, Math.max(132, label.length * 7 + 28), arm.palette.panel, arm.palette.accent);
}

function evidenceLabel(asset) {
  return String(asset?.asset_type ?? asset?.slot_id ?? "visual evidence").replaceAll("_", " ");
}

function compactText(value, max = 74) {
  const textValue = String(value ?? "").trim();
  return textValue.length > max ? `${textValue.slice(0, max - 1).trim()}...` : textValue;
}

function proofFooter(slide, arm, selection) {
  const hint = selection?.gate?.gate_id ?? "no Run 2.24 density gate";
  text(slide, `generation gate: ${hint}`, 66, 628, 830, 28, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
    fill: arm.palette.panel,
    line: colorLine(C.line, 1),
    insets: { left: 18, right: 8, top: 8, bottom: 5 },
  });
  rect(slide, 76, 640, 7, 7, arm.palette.proof ?? arm.palette.accent);
}

function drawRun236LaunchField(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun236Module(metrics, "drawRun236LaunchField");
  const content = selection.content;
  const assets = selection.assets;
  const x = opts.x ?? 82;
  const y = opts.y ?? 116;
  const w = opts.w ?? 730;
  moduleLabel(slide, x, y - 36, "single-usecase launch field", arm);
  text(slide, content.headline, x, y, w, opts.titleH ?? 154, {
    fontSize: opts.fontSize ?? 58,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, content.headline);
  rect(slide, x, y + (opts.ruleY ?? 184), 142, 10, arm.palette.proof ?? C.signal);
  rect(slide, x + 164, y + (opts.ruleY ?? 184), 72, 10, arm.palette.accent2);
  text(slide, content.support_line, x, y + (opts.claimY ?? 220), opts.claimW ?? 520, 58, {
    fontSize: opts.claimSize ?? 17,
    color: arm.palette.muted,
  });
  registerText(metrics, content.support_line);

  const motif = { x: opts.motifX ?? 904, y: opts.motifY ?? 132, w: opts.motifW ?? 236, h: opts.motifH ?? 238 };
  if (motif.w > 0 && motif.h > 0) {
    rect(slide, motif.x, motif.y, motif.w, motif.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
    rect(slide, motif.x + 34, motif.y + 40, 92, 92, arm.palette.proof ?? C.signal);
    rect(slide, motif.x + 146, motif.y + 50, 58, 10, C.white);
    rect(slide, motif.x + 146, motif.y + 84, 68, 8, "#cbd4d9");
    rect(slide, motif.x + 146, motif.y + 116, 42, 8, "#cbd4d9");
    chip(slide, selectedUsecaseId.replace("usecase_", ""), motif.x + 28, motif.y + motif.h - 54, motif.w - 56, "#252e38", C.white);
    assets.slice(0, 2).forEach((asset, index) => {
      text(slide, evidenceLabel(asset), motif.x + 28, motif.y + 154 + index * 22, motif.w - 56, 14, {
        fontSize: 8,
        mono: true,
        color: "#dfe8ec",
      });
      registerText(metrics, evidenceLabel(asset));
    });
    registerHero(metrics, motif.x, motif.y, motif.w, motif.h);
    registerProof(metrics, 1);
    registerVisualEvidence(metrics, assets.length);
  }
}

function drawRun236SelectedRouteMap(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun236Module(metrics, "drawRun236SelectedRouteMap");
  const x = opts.x ?? 82;
  const y = opts.y ?? 402;
  const w = opts.w ?? 1000;
  moduleLabel(slide, x, y - 38, "selected content/visual route", arm);
  const steps = [
    { label: "usecase", detail: "locked story", fill: arm.palette.accent, color: C.white },
    { label: "content", detail: selection.content.content_memory_id.replace("content_2_24_", ""), fill: C.white, color: arm.palette.accent },
    { label: "visual slots", detail: `${selection.assets.length} native assets`, fill: C.white, color: arm.palette.accent },
    { label: "gate", detail: "public blocked", fill: arm.palette.proof ?? C.signal, color: C.white },
  ];
  steps.forEach((step, index) => {
    const nodeW = index === 0 ? 150 : index === 2 ? 184 : 160;
    const nx = x + index * (w / 4);
    const ny = y + (index % 2 === 0 ? 44 : 12);
    rect(slide, nx, ny, nodeW, 78, step.fill, colorLine(index === 0 || index === 3 ? step.fill : arm.palette.accent2, 2));
    text(slide, step.label, nx + 16, ny + 18, nodeW - 32, 14, {
      fontSize: 10,
      bold: true,
      mono: true,
      color: step.color,
    });
    text(slide, step.detail, nx + 16, ny + 43, nodeW - 32, 18, {
      fontSize: 11,
      title: true,
      bold: true,
      color: step.color,
    });
    registerText(metrics, `${step.label} ${step.detail}`);
    if (index < steps.length - 1) {
      rect(slide, nx + nodeW, ny + 38, Math.max(42, x + (index + 1) * (w / 4) - nx - nodeW), 5, arm.palette.proof ?? C.signal);
    }
  });
  registerWorkflow(metrics, steps.length);
  registerGate(metrics, 1);
}

function run236ContentEvidenceSurfaceGeometry({ x, y, w, h }) {
  const mode = w < 620 ? "compact-thick" : w < 760 ? "medium-thick" : "wide-thick";
  const railW = mode === "compact-thick" ? 150 : Math.max(154, Math.min(190, w * 0.24));
  const railX = x + w - railW - 18;
  const proofMarkerX = x + 30;
  const proofTextX = proofMarkerX + 28;
  const proofW = Math.max(280, railX - proofTextX - 18);
  const rowH = mode === "compact-thick" ? 42 : 46;
  const stepY = mode === "compact-thick" ? 54 : 58;
  const headlineH = mode === "wide-thick" ? 62 : 54;
  const proofY = y + 28 + headlineH + 18;
  return {
    mode,
    shadow: { x: x + 54, y: y + 42, w: Math.max(1, w - 14), h: Math.max(1, h - 24) },
    backdrop: { x: x + 22, y: y + 20, w: Math.max(1, w - 10), h: Math.max(1, h - 18) },
    panel: { x, y, w: Math.max(1, w - 58), h: Math.max(1, h - 36) },
    headline: { x: x + 30, y: y + 26, w: proofW + 28, h: headlineH, fontSize: mode === "compact-thick" ? 18 : 22 },
    proofPoint: {
      x: proofTextX,
      y: proofY,
      w: proofW,
      h: rowH,
      fontSize: mode === "compact-thick" ? 8.5 : 9.5,
      stepY,
      count: 3,
      compress: false,
    },
    proofMarker: { x: proofMarkerX, y: proofY + 4, w: 18, h: 18, stepY },
    rail: { x: railX, y: y + 32, w: railW, h: Math.max(140, h - 116) },
    railTitle: { x: railX + 10, y: y + 52, w: Math.max(104, railW - 20), h: 18 },
    assetCard: { x: railX + 10, y: y + 92, w: Math.max(132, railW - 20), h: 48, stepY: 76 },
  };
}

function drawRun236ContentEvidenceSurface(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun236Module(metrics, "drawRun236ContentEvidenceSurface");
  const x = opts.x ?? 96;
  const y = opts.y ?? 126;
  const w = opts.w ?? 870;
  const h = opts.h ?? 368;
  const geom = run236ContentEvidenceSurfaceGeometry({ x, y, w, h });
  moduleLabel(slide, x, y - 38, "thickened content evidence surface", arm);
  rect(slide, geom.shadow.x, geom.shadow.y, geom.shadow.w, geom.shadow.h, "#dfe9ec", colorLine("#dfe9ec", 1));
  rect(slide, geom.backdrop.x, geom.backdrop.y, geom.backdrop.w, geom.backdrop.h, arm.palette.surface ?? C.fog, colorLine("#c9d3d7", 1));
  rect(slide, geom.panel.x, geom.panel.y, geom.panel.w, geom.panel.h, C.white, colorLine(arm.palette.accent, 2));
  text(slide, selection.content.headline, geom.headline.x, geom.headline.y, geom.headline.w, geom.headline.h, {
    fontSize: geom.headline.fontSize,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, selection.content.headline);
  const visibleProofPoints = selection.content.business_proof_points.slice(0, geom.proofPoint.count);
  visibleProofPoints.forEach((point, index) => {
    const py = geom.proofPoint.y + index * geom.proofPoint.stepY;
    const marker = geom.proofMarker ?? {
      x: geom.proofPoint.x,
      y: py + 1,
      w: 14,
      h: 14,
      stepY: geom.proofPoint.stepY,
    };
    rect(slide, marker.x, marker.y + index * (marker.stepY ?? 0), marker.w, marker.h, index === 0 ? arm.palette.proof ?? C.signal : arm.palette.accent2);
    text(slide, geom.proofPoint.compress ? compactText(point) : point, geom.proofPoint.x, py - 2, geom.proofPoint.w, geom.proofPoint.h, {
      fontSize: geom.proofPoint.fontSize,
      color: arm.palette.muted,
    });
    registerText(metrics, point);
  });
  rect(slide, geom.rail.x, geom.rail.y, geom.rail.w, geom.rail.h, "#f4f7f7", colorLine("#ccd6da", 1));
  text(slide, "native visual evidence", geom.railTitle.x, geom.railTitle.y, geom.railTitle.w, geom.railTitle.h, {
    fontSize: 10,
    mono: true,
    bold: true,
    color: arm.palette.accent,
  });
  selection.assets.slice(0, 2).forEach((asset, index) => {
    const ay = geom.assetCard.y + index * geom.assetCard.stepY;
    rect(slide, geom.assetCard.x, ay, geom.assetCard.w, geom.assetCard.h, index === 0 ? arm.palette.proof ?? C.signal : C.white, colorLine(index === 0 ? arm.palette.proof ?? C.signal : "#cad2d8", 1));
    text(slide, evidenceLabel(asset), geom.assetCard.x + 14, ay + (geom.mode === "compact-thick" ? 10 : 13), Math.max(104, geom.assetCard.w - 28), 22, {
      fontSize: 10,
      bold: true,
      title: true,
      color: index === 0 ? C.white : arm.palette.title,
    });
    registerText(metrics, evidenceLabel(asset));
  });
  registerProof(metrics, 3);
  registerZones(metrics, 3);
  registerContentCards(metrics, 3);
  registerVisualEvidence(metrics, selection.assets.length);
  registerThickenedSurfaceProofPoints(metrics, visibleProofPoints.length);
  registerHero(metrics, x, y, w - 64, h - 44);
}

function run236EvidenceChainSurfaceGeometry({ x, y, w, h }) {
  const compact = w < 760;
  const gap = compact ? 12 : 16;
  const colCount = 4;
  const colW = Math.max(116, (w - gap * (colCount + 1)) / colCount);
  const topH = compact ? 72 : 86;
  const cardY = y + topH + 20;
  const cardH = Math.max(118, h - topH - 54);
  return {
    compact,
    panel: { x, y, w, h },
    title: { x: x + 24, y: y + 20, w: Math.max(300, w * 0.52), h: compact ? 34 : 42 },
    gate: { x: x + w - 214, y: y + 20, w: 184, h: 44 },
    cardY,
    cardH,
    cards: Array.from({ length: colCount }, (_, index) => ({
      x: x + gap + index * (colW + gap),
      y: cardY,
      w: colW,
      h: cardH,
    })),
  };
}

function chainChunks(selection) {
  return [
    {
      label: "source evidence",
      value: selection.chain.source_evidence_summary,
      fill: "#101820",
      color: C.white,
    },
    {
      label: "extracted design rule",
      value: selection.chain.extracted_design_rule,
      fill: "#f2f6f7",
      color: armSafeInk(selection),
    },
    {
      label: "workflow decision",
      value: selection.chain.workflow_decision,
      fill: "#fff7ef",
      color: armSafeInk(selection),
    },
    {
      label: "generated slide surface",
      value: selection.chain.generated_slide_surface,
      fill: "#e9f6f2",
      color: armSafeInk(selection),
    },
  ];
}

function armSafeInk() {
  return "#12161d";
}

function drawRun236EvidenceChainSurface(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun236Module(metrics, "drawRun236EvidenceChainSurface");
  const x = opts.x ?? 70;
  const y = opts.y ?? 112;
  const w = opts.w ?? 1068;
  const h = opts.h ?? 424;
  const geom = run236EvidenceChainSurfaceGeometry({ x, y, w, h });
  moduleLabel(slide, x, y - 36, "source-rule-workflow-output chain", arm);
  rect(slide, geom.panel.x, geom.panel.y, geom.panel.w, geom.panel.h, C.white, colorLine(arm.palette.accent, 2));
  text(slide, selection.content.headline, geom.title.x, geom.title.y, geom.title.w, geom.title.h, {
    fontSize: geom.compact ? 22 : 28,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, selection.content.headline);
  rect(slide, geom.gate.x, geom.gate.y, geom.gate.w, geom.gate.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  text(slide, "public blocked", geom.gate.x + 18, geom.gate.y + 15, geom.gate.w - 36, 14, {
    fontSize: 10,
    mono: true,
    bold: true,
    color: C.white,
  });
  registerText(metrics, "public blocked");

  const chunks = chainChunks(selection);
  chunks.forEach((chunk, index) => {
    const card = geom.cards[index];
    rect(slide, card.x, card.y, card.w, card.h, chunk.fill, colorLine(index === 0 ? chunk.fill : "#cfd7dc", 1));
    text(slide, chunk.label, card.x + 14, card.y + 16, card.w - 28, 18, {
      fontSize: 8,
      mono: true,
      bold: true,
      color: index === 0 ? "#dce9ef" : arm.palette.accent,
    });
    text(slide, compactText(chunk.value, geom.compact ? 92 : 124), card.x + 14, card.y + 48, card.w - 28, card.h - 76, {
      fontSize: geom.compact ? 9 : 10,
      color: chunk.color,
    });
    registerText(metrics, `${chunk.label} ${chunk.value}`);
    if (index < chunks.length - 1) {
      const next = geom.cards[index + 1];
      rect(slide, card.x + card.w, card.y + card.h / 2, Math.max(8, next.x - card.x - card.w), 4, arm.palette.proof ?? C.signal);
    }
  });

  const assetY = y + h - 38;
  selection.assets.slice(0, 2).forEach((asset, index) => {
    const ax = x + 24 + index * 220;
    rect(slide, ax, assetY, 198, 24, index === 0 ? arm.palette.proof ?? C.signal : "#f4f7f7", colorLine(index === 0 ? arm.palette.proof ?? C.signal : "#cbd5da", 1));
    text(slide, evidenceLabel(asset), ax + 12, assetY + 8, 172, 10, {
      fontSize: 7.5,
      mono: true,
      bold: true,
      color: index === 0 ? C.white : arm.palette.title,
    });
    registerText(metrics, evidenceLabel(asset));
  });
  registerProof(metrics, 4);
  registerZones(metrics, 4);
  registerWorkflow(metrics, 4);
  registerGate(metrics, 1);
  registerContentCards(metrics, 4);
  registerVisualEvidence(metrics, selection.assets.length);
  registerThickenedSurfaceProofPoints(metrics, 4);
  registerHero(metrics, x, y, w, h);
}

function drawRun236WorkflowTracePanel(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun236Module(metrics, "drawRun236WorkflowTracePanel");
  drawRun236EvidenceChainSurface(slide, arm, spec, selection, metrics, {
    x: opts.x ?? 72,
    y: opts.y ?? 108,
    w: opts.w ?? 720,
    h: opts.h ?? 418,
  });
  const gate = { x: opts.gateX ?? 830, y: opts.gateY ?? 124, w: 304, h: 374 };
  rect(slide, gate.x, gate.y, gate.w, gate.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  text(slide, "release gate", gate.x + 28, gate.y + 28, gate.w - 56, 28, {
    fontSize: 22,
    title: true,
    bold: true,
    color: C.white,
  });
  text(slide, selection.chain.workflow_decision, gate.x + 28, gate.y + 82, gate.w - 56, 96, {
    fontSize: 13,
    color: "#dce5ea",
  });
  text(slide, "inspectable handoff path", gate.x + 28, gate.y + 220, gate.w - 56, 18, {
    fontSize: 9,
    mono: true,
    bold: true,
    color: arm.palette.accent2,
  });
  ["source", "rule", "workflow", "surface"].forEach((label, index) => {
    const bx = gate.x + 30 + index * 62;
    rect(slide, bx, gate.y + 262, 48, 48, index === 3 ? arm.palette.proof ?? C.signal : "#2c3844", colorLine("#53616d", 1));
    text(slide, label, bx + 6, gate.y + 280, 36, 10, { fontSize: 6.8, mono: true, color: C.white, align: "center" });
    registerText(metrics, label);
  });
  registerText(metrics, `release gate ${selection.chain.workflow_decision} inspectable handoff path`);
  registerGate(metrics, 2);
}

function drawRun236ClimaxEvidenceObject(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236ClimaxEvidenceObject");
  drawRun236ClimaxProofObject(slide, arm, spec, selection, metrics);
  const rail = { x: 826, y: 168, w: 250, h: 226 };
  rect(slide, rail.x, rail.y, rail.w, rail.h, "#151d25", colorLine("#46515c", 1));
  text(slide, "source evidence", rail.x + 18, rail.y + 18, rail.w - 36, 12, {
    fontSize: 8,
    mono: true,
    bold: true,
    color: arm.palette.accent2,
  });
  text(slide, compactText(selection.chain.source_evidence_summary, 86), rail.x + 18, rail.y + 44, rail.w - 36, 42, {
    fontSize: 8.5,
    color: "#dce5ea",
  });
  text(slide, "workflow decision", rail.x + 18, rail.y + 112, rail.w - 36, 12, {
    fontSize: 8,
    mono: true,
    bold: true,
    color: arm.palette.accent2,
  });
  text(slide, compactText(selection.chain.workflow_decision, 90), rail.x + 18, rail.y + 138, rail.w - 36, 48, {
    fontSize: 8.5,
    color: "#dce5ea",
  });
  registerText(metrics, `${selection.chain.source_evidence_summary} ${selection.chain.workflow_decision}`);
  registerWorkflow(metrics, 4);
}

function drawRun236ClimaxProofObject(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236ClimaxProofObject");
  const stage = { x: 96, y: 96, w: 1048, h: 500 };
  moduleLabel(slide, 84, 96, "single generated proof object", arm);
  rect(slide, stage.x, stage.y, stage.w, stage.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  text(slide, selection.content.headline, stage.x + 48, stage.y + 40, 522, 58, {
    fontSize: 32,
    bold: true,
    title: true,
    color: C.white,
  });
  registerText(metrics, selection.content.headline);
  const hero = { x: stage.x + 124, y: stage.y + 138, w: 780, h: 268 };
  rect(slide, hero.x - 74, hero.y - 54, hero.w + 148, hero.h + 112, "#222b35", colorLine("#222b35", 1));
  rect(slide, hero.x, hero.y, hero.w, hero.h, C.white, colorLine(arm.palette.proof ?? C.signal, 4));
  rect(slide, hero.x + 52, hero.y + 42, 258, 164, arm.palette.proof ?? C.signal);
  text(slide, "editable PPT result", hero.x + 70, hero.y + 72, 210, 32, {
    fontSize: 22,
    bold: true,
    title: true,
    color: C.white,
  });
  text(slide, selectedUsecaseId.replace("usecase_", ""), hero.x + 70, hero.y + 148, 220, 34, {
    fontSize: 10,
    mono: true,
    color: C.white,
  });
  rect(slide, hero.x + 358, hero.y + 58, 212, 14, arm.palette.accent2);
  rect(slide, hero.x + 358, hero.y + 108, 274, 9, "#bdc8cf");
  rect(slide, hero.x + 358, hero.y + 144, 188, 9, "#bdc8cf");
  text(slide, selection.content.business_proof_points[0], hero.x + 358, hero.y + 178, 316, 42, {
    fontSize: 12,
    color: arm.palette.muted,
  });
  registerText(metrics, selection.content.business_proof_points[0]);
  selection.assets.slice(0, 2).forEach((asset, index) => {
    const ex = index === 0 ? stage.x + 50 : stage.x + stage.w - 246;
    const ey = index === 0 ? stage.y + stage.h - 96 : stage.y + 70;
    rect(slide, ex, ey, 198, 34, "#303a45", colorLine("#596471", 1));
    text(slide, evidenceLabel(asset), ex + 14, ey + 11, 168, 12, {
      fontSize: 9,
      bold: true,
      mono: true,
      color: "#dae4e8",
    });
    registerText(metrics, evidenceLabel(asset));
  });
  rect(slide, stage.x + stage.w - 246, stage.y + stage.h - 92, 198, 34, arm.palette.proof ?? C.signal, colorLine(arm.palette.proof ?? C.signal, 1));
  text(slide, "public blocked", stage.x + stage.w - 226, stage.y + stage.h - 81, 150, 12, {
    fontSize: 9,
    bold: true,
    mono: true,
    color: C.white,
  });
  registerText(metrics, "public blocked");
  registerProof(metrics, 1);
  registerGate(metrics, 1);
  registerVisualEvidence(metrics, selection.assets.length);
  registerHero(metrics, stage.x, stage.y, stage.w, stage.h);
}

function run236SpineDetail(selection, step) {
  if (step === "source evidence") return compactText(selection.chain.source_evidence_summary, 54);
  if (step === "extracted design rule") return compactText(selection.chain.extracted_design_rule, 54);
  if (step === "workflow decision") return compactText(selection.chain.workflow_decision, 54);
  return compactText(selection.chain.generated_slide_surface, 54);
}

function drawRun236ReadableEvidenceSpine(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun236Module(metrics, "drawRun236ReadableEvidenceSpine");
  const x = opts.x ?? 922;
  const y = opts.y ?? 124;
  const w = opts.w ?? 246;
  const h = opts.h ?? 394;
  rect(slide, x, y, w, h, opts.dark ? "#121922" : C.white, colorLine(opts.dark ? "#374654" : "#cfd8dc", 1));
  text(slide, "readable evidence spine", x + 18, y + 18, w - 36, 16, {
    fontSize: 10,
    mono: true,
    bold: true,
    color: opts.dark ? arm.palette.accent2 : arm.palette.accent,
  });
  text(slide, "full chain visible in trace", x + 18, y + 42, w - 36, 14, {
    fontSize: 8,
    mono: true,
    color: opts.dark ? "#b9c9d2" : arm.palette.muted,
  });
  const steps = selection.synthesis.visible_on_slide_evidence_spine_steps ?? [
    "source evidence",
    "extracted design rule",
    "workflow decision",
    "generated slide surface",
  ];
  const rowH = Math.max(70, (h - 92) / steps.length);
  steps.forEach((step, index) => {
    const rowY = y + 78 + index * rowH;
    const markerFill = index === 0 ? arm.palette.proof ?? C.signal : index === steps.length - 1 ? arm.palette.accent2 : opts.dark ? "#2a3642" : "#eef3f4";
    rect(slide, x + 18, rowY + 4, 18, 18, markerFill, colorLine(markerFill, 1));
    if (index < steps.length - 1) rect(slide, x + 26, rowY + 24, 2, rowH - 18, opts.dark ? "#596877" : "#d7e0e3");
    text(slide, step, x + 48, rowY, w - 66, 12, {
      fontSize: 8.4,
      mono: true,
      bold: true,
      color: opts.dark ? "#dce8ee" : arm.palette.title,
    });
    text(slide, run236SpineDetail(selection, step), x + 48, rowY + 22, w - 66, 34, {
      fontSize: 8,
      color: opts.dark ? "#bac8d0" : arm.palette.muted,
    });
    registerText(metrics, `${step} ${run236SpineDetail(selection, step)}`);
  });
  registerWorkflow(metrics, 4);
  registerVisualEvidence(metrics, 1);
}

function run236EvidenceLayerSlot(role) {
  return {
    cover: { x: 464, y: 404, w: 334, h: 120, dark: true },
    setup: { x: 470, y: 438, w: 314, h: 86, dark: false },
    contrast: { x: 108, y: 492, w: 686, h: 72, dark: false },
    proof: { x: 410, y: 450, w: 360, h: 86, dark: false },
    climax: { x: 566, y: 158, w: 268, h: 72, dark: false },
    close: { x: 448, y: 452, w: 316, h: 76, dark: true },
  }[role] ?? { x: 420, y: 452, w: 340, h: 82, dark: false };
}

function drawRun236VisualEvidenceStoryboard(slide, arm, spec, selection, metrics, slot) {
  registerRun236Module(metrics, "drawRun236VisualEvidenceStoryboard");
  const assets = selection.assets.slice(0, 2);
  const cardGap = 12;
  const cardW = (slot.w - cardGap) / 2;
  assets.forEach((asset, index) => {
    const x = slot.x + index * (cardW + cardGap);
    const fill = index === 0 ? arm.palette.proof ?? C.signal : slot.dark ? "#22303a" : "#eef4f4";
    const line = index === 0 ? arm.palette.proof ?? C.signal : "#c8d5d8";
    rect(slide, x, slot.y, cardW, slot.h, fill, colorLine(line, 1));
    text(slide, index === 0 ? "primary evidence" : "supporting evidence", x + 12, slot.y + 12, cardW - 24, 10, {
      fontSize: 7.8,
      mono: true,
      bold: true,
      color: index === 0 || slot.dark ? C.white : arm.palette.accent,
    });
    text(slide, evidenceLabel(asset), x + 12, slot.y + 30, cardW - 24, 18, {
      fontSize: 9,
      bold: true,
      color: index === 0 || slot.dark ? C.white : arm.palette.title,
    });
    text(slide, compactText(asset.source_boundary ?? "Derived visual evidence", 46), x + 12, slot.y + 54, cardW - 24, 18, {
      fontSize: 7.4,
      color: index === 0 || slot.dark ? "#dce8ee" : arm.palette.muted,
    });
    registerText(metrics, `${evidenceLabel(asset)} ${asset.source_boundary ?? ""}`);
  });
  registerVisualEvidence(metrics, Math.max(2, assets.length));
  registerContentCards(metrics, Math.max(2, assets.length));
}

function drawRun236MainSurfaceEvidenceLayer(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236MainSurfaceEvidenceLayer");
  const slot = run236EvidenceLayerSlot(spec.role);
  rect(slide, slot.x - 8, slot.y - 8, slot.w + 16, slot.h + 16, slot.dark ? "#17212a" : "#f7fbfb", colorLine(slot.dark ? "#3b4954" : "#d7e3e5", 1));
  text(slide, "main-surface evidence", slot.x, slot.y - 24, Math.min(184, slot.w), 12, {
    fontSize: 8,
    mono: true,
    bold: true,
    color: slot.dark ? "#dbe8ee" : arm.palette.accent,
  });
  drawRun236VisualEvidenceStoryboard(slide, arm, spec, selection, metrics, slot);
  registerText(metrics, "main-surface evidence visual evidence realism");
  registerProof(metrics, 1);
}

function drawRun236EditorialLaunchFrame(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236EditorialLaunchFrame");
  moduleLabel(slide, 76, 98, "presentation-first surface", arm);
  text(slide, selection.content.headline, 76, 134, 658, 128, {
    fontSize: 52,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, selection.content.headline);
  text(slide, selection.content.support_line, 80, 282, 548, 58, {
    fontSize: 16,
    color: arm.palette.muted,
  });
  registerText(metrics, selection.content.support_line);
  const stage = { x: 112, y: 378, w: 688, h: 176 };
  rect(slide, stage.x, stage.y, stage.w, stage.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  rect(slide, stage.x + 34, stage.y + 34, 172, 92, arm.palette.proof ?? C.signal);
  text(slide, "editable launch system", stage.x + 58, stage.y + 62, 124, 32, {
    fontSize: 18,
    title: true,
    bold: true,
    color: C.white,
  });
  rect(slide, stage.x + 246, stage.y + 48, 240, 12, arm.palette.accent2);
  rect(slide, stage.x + 246, stage.y + 90, 324, 8, "#cad4da");
  rect(slide, stage.x + 246, stage.y + 124, 218, 8, "#cad4da");
  chip(slide, selectedUsecaseId.replace("usecase_", ""), stage.x + 510, stage.y + 34, 138, "#2b3642", C.white);
  drawRun236ReadableEvidenceSpine(slide, arm, spec, selection, metrics, { x: 898, y: 118, w: 264, h: 438 });
  registerProof(metrics, 2);
  registerZones(metrics, 3);
  registerHero(metrics, stage.x, stage.y, stage.w, stage.h);
}

function drawRun236AsymmetricProblemFrame(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236AsymmetricProblemFrame");
  moduleLabel(slide, 76, 98, "presentation-first surface", arm);
  text(slide, selection.content.headline, 76, 132, 620, 92, {
    fontSize: 42,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, selection.content.headline);
  const weak = { x: 86, y: 284, w: 250, h: 180 };
  const route = { x: 384, y: 238, w: 426, h: 280 };
  rect(slide, weak.x, weak.y, weak.w, weak.h, "#f7f7f8", colorLine("#cdd5dc", 1));
  text(slide, "prompt-only path", weak.x + 24, weak.y + 24, weak.w - 48, 16, {
    fontSize: 10,
    mono: true,
    bold: true,
    color: arm.palette.muted,
  });
  rect(slide, weak.x + 26, weak.y + 70, 92, 9, "#bec8cf");
  rect(slide, weak.x + 26, weak.y + 104, 134, 7, "#d2d9df");
  rect(slide, weak.x + 26, weak.y + 132, 72, 7, "#d2d9df");
  text(slide, "generic surface", weak.x + 26, weak.y + 148, weak.w - 52, 12, {
    fontSize: 8,
    mono: true,
    color: arm.palette.muted,
  });
  rect(slide, route.x, route.y, route.w, route.h, C.white, colorLine(arm.palette.accent, 2));
  text(slide, "selected product route", route.x + 34, route.y + 30, route.w - 68, 26, {
    fontSize: 22,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  selection.content.business_proof_points.slice(0, 3).forEach((point, index) => {
    const py = route.y + 88 + index * 54;
    rect(slide, route.x + 36, py + 4, 16, 16, index === 0 ? arm.palette.proof ?? C.signal : arm.palette.accent2);
    text(slide, point, route.x + 68, py, route.w - 112, 34, {
      fontSize: 10.5,
      color: arm.palette.muted,
    });
    registerText(metrics, point);
  });
  drawRun236ReadableEvidenceSpine(slide, arm, spec, selection, metrics, { x: 900, y: 124, w: 262, h: 420 });
  registerText(metrics, "prompt-only path selected product route generic surface");
  registerProof(metrics, 3);
  registerContentCards(metrics, 3);
  registerHero(metrics, route.x, route.y, route.w, route.h);
}

function drawRun236BeforeAfterEditorialSpread(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236BeforeAfterEditorialSpread");
  moduleLabel(slide, 76, 96, "presentation-first surface", arm);
  text(slide, selection.content.headline, 76, 130, 618, 72, {
    fontSize: 36,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, selection.content.headline);
  const before = { x: 80, y: 260, w: 260, h: 204 };
  const after = { x: 386, y: 218, w: 430, h: 308 };
  rect(slide, before.x, before.y, before.w, before.h, "#f5f6f7", colorLine("#ccd3da", 1));
  text(slide, "before / prompt-only", before.x + 22, before.y + 26, before.w - 44, 14, {
    fontSize: 9,
    mono: true,
    bold: true,
    color: arm.palette.muted,
  });
  rect(slide, before.x + 22, before.y + 72, 112, 10, "#c1cbd2");
  rect(slide, before.x + 22, before.y + 112, 166, 7, "#d3dae0");
  rect(slide, before.x + 22, before.y + 144, 88, 7, "#d3dae0");
  rect(slide, after.x, after.y, after.w, after.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  text(slide, "after / evidence-selected", after.x + 34, after.y + 30, after.w - 68, 22, {
    fontSize: 20,
    title: true,
    bold: true,
    color: C.white,
  });
  rect(slide, after.x + 36, after.y + 84, 154, 108, arm.palette.proof ?? C.signal);
  rect(slide, after.x + 220, after.y + 96, 146, 12, arm.palette.accent2);
  rect(slide, after.x + 220, after.y + 140, 112, 8, "#cbd6dc");
  rect(slide, after.x + 220, after.y + 172, 150, 8, "#cbd6dc");
  text(slide, selection.content.business_proof_points[0], after.x + 36, after.y + 226, after.w - 72, 40, {
    fontSize: 12,
    color: "#dfe9ee",
  });
  registerText(metrics, selection.content.business_proof_points[0]);
  drawRun236ReadableEvidenceSpine(slide, arm, spec, selection, metrics, { x: 900, y: 124, w: 262, h: 420 });
  registerText(metrics, "before prompt-only after evidence-selected");
  registerProof(metrics, 2);
  registerZones(metrics, 3);
  registerHero(metrics, after.x, after.y, after.w, after.h);
}

function drawRun236ProductProofTheater(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236ProductProofTheater");
  moduleLabel(slide, 76, 96, "presentation-first surface", arm);
  text(slide, selection.content.headline, 76, 126, 610, 70, {
    fontSize: 36,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, selection.content.headline);
  const stage = { x: 86, y: 228, w: 732, h: 322 };
  rect(slide, stage.x + 28, stage.y + 28, stage.w, stage.h, "#dce8eb", colorLine("#dce8eb", 1));
  rect(slide, stage.x, stage.y, stage.w, stage.h, C.white, colorLine(arm.palette.accent, 2));
  rect(slide, stage.x + 34, stage.y + 36, 214, 166, arm.palette.proof ?? C.signal);
  text(slide, "native PPT proof surface", stage.x + 58, stage.y + 70, 152, 46, {
    fontSize: 20,
    title: true,
    bold: true,
    color: C.white,
  });
  selection.content.business_proof_points.slice(0, 3).forEach((point, index) => {
    const px = stage.x + 296;
    const py = stage.y + 48 + index * 72;
    rect(slide, px, py + 5, 18, 18, index === 0 ? arm.palette.proof ?? C.signal : arm.palette.accent2);
    text(slide, point, px + 34, py, 344, 42, {
      fontSize: 11,
      color: arm.palette.muted,
    });
    registerText(metrics, point);
  });
  selection.assets.slice(0, 2).forEach((asset, index) => {
    const ax = stage.x + 36 + index * 180;
    const ay = stage.y + 238;
    rect(slide, ax, ay, 158, 34, index === 0 ? arm.palette.gate : "#f2f6f7", colorLine("#c8d2d7", 1));
    text(slide, evidenceLabel(asset), ax + 12, ay + 11, 134, 11, {
      fontSize: 7.6,
      mono: true,
      bold: true,
      color: index === 0 ? C.white : arm.palette.title,
    });
    registerText(metrics, evidenceLabel(asset));
  });
  drawRun236ReadableEvidenceSpine(slide, arm, spec, selection, metrics, { x: 900, y: 124, w: 262, h: 420 });
  registerProof(metrics, 3);
  registerContentCards(metrics, 3);
  registerVisualEvidence(metrics, selection.assets.length);
  registerHero(metrics, stage.x, stage.y, stage.w, stage.h);
}

function drawRun236HeroProofScene(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236HeroProofScene");
  moduleLabel(slide, 76, 96, "shared light editorial climax", arm);
  const stage = { x: 84, y: 118, w: 1086, h: 484 };
  rect(slide, stage.x + 22, stage.y + 22, stage.w - 4, stage.h - 4, "#dce7e7", colorLine("#dce7e7", 1));
  rect(slide, stage.x, stage.y, stage.w, stage.h, C.white, colorLine(arm.palette.accent, 2));
  text(slide, selection.content.headline, stage.x + 44, stage.y + 38, 574, 72, {
    fontSize: 38,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, selection.content.headline);
  text(slide, compactText(selection.content.support_line, 88), stage.x + 46, stage.y + 124, 480, 36, {
    fontSize: 13.5,
    color: arm.palette.muted,
  });
  registerText(metrics, selection.content.support_line);

  const hero = { x: stage.x + 56, y: stage.y + 196, w: 700, h: 246 };
  rect(slide, hero.x - 20, hero.y - 20, hero.w + 40, hero.h + 40, "#eef4f4", colorLine("#eef4f4", 1));
  rect(slide, hero.x, hero.y, hero.w, hero.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  rect(slide, hero.x + 42, hero.y + 42, 232, 140, arm.palette.proof ?? C.signal);
  text(slide, "editable PPT result", hero.x + 62, hero.y + 68, 178, 34, {
    fontSize: 23,
    bold: true,
    title: true,
    color: C.white,
  });
  text(slide, selectedUsecaseId.replace("usecase_", ""), hero.x + 62, hero.y + 136, 188, 28, {
    fontSize: 9.5,
    mono: true,
    color: C.white,
  });
  rect(slide, hero.x + 330, hero.y + 54, 220, 14, arm.palette.accent2);
  rect(slide, hero.x + 330, hero.y + 104, 278, 9, "#bdc8cf");
  rect(slide, hero.x + 330, hero.y + 140, 192, 9, "#bdc8cf");
  text(slide, selection.content.business_proof_points[0], hero.x + 330, hero.y + 174, 306, 42, {
    fontSize: 12,
    color: "#dce8ee",
  });
  registerText(metrics, selection.content.business_proof_points[0]);
  selection.assets.slice(0, 2).forEach((asset, index) => {
    const ax = stage.x + 596 + index * 152;
    rect(slide, ax, stage.y + 128, 132, 32, index === 0 ? arm.palette.proof ?? C.signal : "#edf3f2", colorLine("#c6d2d4", 1));
    text(slide, evidenceLabel(asset), ax + 10, stage.y + 139, 112, 10, {
      fontSize: 8,
      mono: true,
      bold: true,
      color: index === 0 ? C.white : arm.palette.title,
    });
    registerText(metrics, evidenceLabel(asset));
  });
  text(slide, "public blocked", hero.x + hero.w - 160, hero.y + hero.h - 48, 120, 14, {
    fontSize: 10,
    mono: true,
    bold: true,
    color: arm.palette.proof ?? C.signal,
  });
  registerText(metrics, "public blocked");
  drawRun236ReadableEvidenceSpine(slide, arm, spec, selection, metrics, { x: 872, y: 154, w: 270, h: 392 });
  registerProof(metrics, 3);
  registerGate(metrics, 1);
  registerVisualEvidence(metrics, selection.assets.length);
  registerZones(metrics, 3);
  registerHero(metrics, stage.x, stage.y, stage.w, stage.h);
}

function drawRun236DecisionHandoff(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236DecisionHandoff");
  moduleLabel(slide, 76, 96, "presentation-first surface", arm);
  text(slide, selection.content.headline, 76, 130, 594, 72, {
    fontSize: 36,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, selection.content.headline);
  const gate = { x: 94, y: 246, w: 690, h: 284 };
  rect(slide, gate.x, gate.y, gate.w, gate.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  text(slide, "release decision", gate.x + 38, gate.y + 34, gate.w - 76, 28, {
    fontSize: 24,
    title: true,
    bold: true,
    color: C.white,
  });
  text(slide, "public blocked", gate.x + 38, gate.y + 94, 220, 36, {
    fontSize: 30,
    title: true,
    bold: true,
    color: arm.palette.proof ?? C.signal,
  });
  text(slide, selection.chain.workflow_decision, gate.x + 38, gate.y + 154, 418, 58, {
    fontSize: 13,
    color: "#dce7ed",
  });
  ["source", "rule", "workflow", "surface"].forEach((label, index) => {
    const bx = gate.x + 430 + index * 52;
    rect(slide, bx, gate.y + 86, 40, 40, index === 3 ? arm.palette.proof ?? C.signal : "#2c3844", colorLine("#53616d", 1));
    text(slide, label, bx + 5, gate.y + 101, 30, 9, { fontSize: 5.8, mono: true, color: C.white, align: "center" });
    registerText(metrics, label);
  });
  drawRun236ReadableEvidenceSpine(slide, arm, spec, selection, metrics, { x: 900, y: 124, w: 262, h: 420 });
  registerText(metrics, `release decision public blocked ${selection.chain.workflow_decision}`);
  registerGate(metrics, 2);
  registerProof(metrics, 2);
  registerHero(metrics, gate.x, gate.y, gate.w, gate.h);
}

function drawControlGate(slide, arm, spec, metrics, opts = {}) {
  const x = opts.x ?? 910;
  const y = opts.y ?? 438;
  const w = opts.w ?? 210;
  const h = opts.h ?? 116;
  rect(slide, x, y, w, h, arm.palette.gate, colorLine(arm.palette.rule, 1));
  text(slide, opts.headline ?? "public blocked", x + 16, y + 22, w - 32, 30, {
    fontSize: 16,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  text(slide, opts.line ?? "no Run 2.24 pack trace", x + 16, y + 66, w - 32, 18, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
  });
  registerText(metrics, `${opts.headline ?? "public blocked"} ${opts.line ?? "no Run 2.24 pack trace"}`);
  registerGate(metrics, 1);
}

function drawControlSlideContent(slide, arm, spec, metrics, mode = "prompt") {
  text(slide, spec.title, 76, 132, 590, 104, {
    fontSize: mode === "bad" ? 34 : 38,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, spec.claim, 80, 250, 520, 64, { fontSize: 16, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  const panelFill = mode === "bad" ? "#efe4c8" : C.white;
  const cols = spec.role === "climax" ? 3 : mode === "bad" ? 4 : 3;
  for (let i = 0; i < cols; i += 1) {
    const px = spec.role === "climax" ? 94 + i * 300 : 674 + i * (mode === "bad" ? 116 : 150);
    const py = spec.role === "climax" ? 328 : 318;
    const pw = spec.role === "climax" ? 248 : mode === "bad" ? 100 : 132;
    const ph = spec.role === "climax" ? 150 : 148;
    rect(slide, px, py, pw, ph, panelFill, colorLine(arm.palette.rule, 1));
    rect(slide, px + 14, py + 26, pw - 40, 12, arm.palette.accent2);
    rect(slide, px + 14, py + 64, pw - 56, 9, "#c0c9d0");
    rect(slide, px + 14, py + 96, pw - 68, 9, "#c0c9d0");
  }
  const copy =
    mode === "bad"
      ? "Usecase label is present, but no Run 2.24 content memory, visual evidence, or density gate was executed."
      : "The control can be readable while still lacking content/visual evidence selected before generation.";
  rect(slide, 84, 346, mode === "bad" ? 456 : 480, 150, panelFill, colorLine(arm.palette.rule, 1));
  text(slide, copy, 108, 378, mode === "bad" ? 390 : 420, 72, {
    fontSize: mode === "bad" ? 17 : 19,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, copy);
  registerContentCards(metrics, 1);
}

function assertRun236ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  const assertAllowed = (input) => {
    if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
    if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
  };
  const assertForbidden = (input) => {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  };

  if (arm.armId === "run2_36_full_visual_evidence_realism") {
    for (const input of RUN2_36_DATA_INPUTS) assertAllowed(input);
    return;
  }
  for (const input of RUN2_36_DATA_INPUTS) assertForbidden(input);
}

function readRun236PackJsonForArm(arm, relPath) {
  assertRun236ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (arm.armId !== "run2_36_full_visual_evidence_realism") {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  return readJson(relPath);
}

function validateRun224SingleUsecaseSchemas(contentMemory, visualAssets, workflowGates) {
  if (contentMemory?.status !== "run2_24_single_usecase_content_memory_ready_public_blocked") {
    throw new Error("Run 2.24 content memory schema/status mismatch");
  }
  if (visualAssets?.status !== "run2_24_visual_evidence_asset_memory_ready_public_blocked") {
    throw new Error("Run 2.24 visual evidence asset memory schema/status mismatch");
  }
  if (workflowGates?.status !== "run2_24_content_visual_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.24 content/visual workflow gates schema/status mismatch");
  }
  if (contentMemory.selected_usecase?.id !== selectedUsecaseId || visualAssets.selected_usecase_id !== selectedUsecaseId) {
    throw new Error("Run 2.24 selected usecase mismatch");
  }
  const records = contentMemory.slide_content_memory ?? [];
  const assets = visualAssets.visual_evidence_assets ?? [];
  const gates = workflowGates.gates ?? [];
  if (records.length !== 6 || assets.length !== 12 || gates.length !== 6) {
    throw new Error("Run 2.24 pack must contain six content records, twelve visual assets, and six gates");
  }
  const assetsBySlot = new Map(assets.map((asset) => [asset.slot_id, asset]));
  const gateByRole = new Map(gates.map((gate) => [gate.role, gate]));
  for (const record of records) {
    const gate = gateByRole.get(record.role);
    if (record.selected_usecase_id !== selectedUsecaseId) throw new Error(`Run 2.24 content record usecase mismatch: ${record.role}`);
    if (!record.content_memory_id || !record.headline || !record.support_line) {
      throw new Error(`Run 2.24 content record is incomplete: ${record.role}`);
    }
    if ((record.business_proof_points ?? []).length < 2 || (record.visual_evidence_slot_ids ?? []).length < 2) {
      throw new Error(`Run 2.24 content record lacks density: ${record.role}`);
    }
    if (!gate || gate.required_content_memory_id !== record.content_memory_id) {
      throw new Error(`Run 2.24 workflow gate mismatch: ${record.role}`);
    }
    if (gate.public_release_gate !== "blocked" || gate.forbid_cross_case_primary_story !== true) {
      throw new Error(`Run 2.24 workflow gate policy mismatch: ${record.role}`);
    }
    for (const slotId of record.visual_evidence_slot_ids) {
      const asset = assetsBySlot.get(slotId);
      if (!asset || asset.role !== record.role || asset.selected_usecase_id !== selectedUsecaseId) {
        throw new Error(`Run 2.24 visual asset mismatch: ${slotId}`);
      }
      if (!asset.public_surface_allowed || !String(asset.source_boundary ?? "").startsWith("Derived")) {
        throw new Error(`Run 2.24 visual asset source boundary mismatch: ${slotId}`);
      }
    }
    for (const field of [
      "run2_24_selected_usecase_id",
      "run2_24_content_memory_id",
      "run2_24_visual_evidence_slot_ids",
      "run2_24_content_density_gate_id",
    ]) {
      if (!record.trace_fields_required?.includes(field) || !gate.required_trace_fields?.includes(field)) {
        throw new Error(`Run 2.24 role ${record.role} missing required trace field ${field}`);
      }
    }
  }
}

function validateRun230PresentationSynthesisAudit(audit) {
  if (audit?.status !== "run2_30_presentation_synthesis_audit_public_blocked") {
    throw new Error("Run 2.36 source audit must be Run 2.30 presentation synthesis audit");
  }
  if (audit.run_id !== "2.30" || audit.source_generated_run !== "2.29") {
    throw new Error("Run 2.30 audit source mismatch");
  }
  if (audit.creates_new_ppt_deck !== false || audit.public_ready !== false) {
    throw new Error("Run 2.30 audit boundary mismatch");
  }
  if (audit.quality_summary?.top_next_layer_to_thicken !== "spine_readability_and_climax_consistency") {
    throw new Error("Run 2.30 audit did not target spine_readability_and_climax_consistency");
  }
  if (audit.trace_closure?.full_arm?.presentation_synthesis_records_selected !== 6) {
    throw new Error("Run 2.30 audit did not prove 6/6 synthesis records selected");
  }
  if (audit.trace_closure?.bad_control?.presentation_synthesis_fields_leaked !== 0) {
    throw new Error("Run 2.30 audit bad-control boundary failed");
  }
}

function validateRun231SpineClimaxRepairRerun(result) {
  if (result?.status !== "run2_31_spine_climax_repair_rerun_public_blocked") {
    throw new Error("Run 2.36 prior rerun result must be Run 2.31 public-blocked spine/climax repair rerun");
  }
  if (
    result.run_id !== "2.31" ||
    result.rerun?.best_internal_arm !== "run2_31_full_spine_climax_repair" ||
    result.rerun?.best_internal_arm_verdict !==
      "spine_readability_and_climax_consistency_repaired_before_native_ppt_generation"
  ) {
    throw new Error("Run 2.36 prior rerun result source mismatch");
  }
}

function validateRun232SpineClimaxRepairAudit(audit) {
  if (audit?.status !== "run2_32_spine_climax_repair_audit_public_blocked") {
    throw new Error("Run 2.36 source audit must be Run 2.32 spine/climax repair audit");
  }
  if (audit.run_id !== "2.32" || audit.source_generated_run !== "2.31" || audit.source_audit_run !== "2.30") {
    throw new Error("Run 2.32 audit source mismatch");
  }
  if (audit.creates_new_ppt_deck !== false || audit.public_ready !== false) {
    throw new Error("Run 2.32 audit boundary mismatch");
  }
  if (audit.repair_verification?.repair_target_closed !== true) {
    throw new Error("Run 2.32 audit must close the Run 2.31 spine/climax repair target before Run 2.36");
  }
  if (audit.quality_summary?.top_next_layer_to_thicken !== "main_surface_information_density_and_visual_evidence_realism") {
    throw new Error("Run 2.32 audit did not target main_surface_information_density_and_visual_evidence_realism");
  }
  if (audit.trace_closure?.full_arm?.readable_evidence_spine_modules_called !== 6) {
    throw new Error("Run 2.32 audit did not prove 6/6 readable spine modules");
  }
  if (audit.trace_closure?.bad_control?.repair_fields_leaked !== 0) {
    throw new Error("Run 2.32 audit bad-control boundary failed");
  }
}

function validateRun236EvidenceChainViewModel(model, contentMemory, workflowGates) {
  if (model?.status !== "run2_28_evidence_chain_view_model_ready_public_blocked") {
    throw new Error("Run 2.36 source evidence chain must be the Run 2.28 evidence-chain view model");
  }
  if (model.selected_usecase_id !== selectedUsecaseId || model.stage_policy !== "repeat_same_five_layers_not_run3") {
    throw new Error("Run 2.28 evidence chain model usecase/stage mismatch");
  }
  const expectedChainOrder = ["source evidence", "extracted design rule", "workflow decision", "generated slide surface"];
  if (JSON.stringify(model.viewer_contract?.chain_order ?? []) !== JSON.stringify(expectedChainOrder)) {
    throw new Error("Run 2.28 viewer contract must expose source-rule-workflow-output order");
  }
  const chains = model.slide_evidence_chains ?? [];
  const roles = ["cover", "setup", "contrast", "proof", "climax", "close"];
  if (chains.length !== roles.length || chains.map((chain) => chain.role).join(",") !== roles.join(",")) {
    throw new Error("Run 2.28 evidence chain must contain the six canonical slide roles in order");
  }
  const contentByRole = new Map((contentMemory.slide_content_memory ?? []).map((record) => [record.role, record]));
  const gateByRole = new Map((workflowGates.gates ?? []).map((gate) => [gate.role, gate]));
  const expectedRun228Fields = [
    "run2_28_evidence_chain_id",
    "run2_28_multimodal_source_record_ids",
    "run2_28_extracted_design_rule",
    "run2_28_workflow_decision",
    "run2_28_native_surface_module_id",
  ];
  for (const chain of chains) {
    const content = contentByRole.get(chain.role);
    const gate = gateByRole.get(chain.role);
    if (!content || !gate) throw new Error(`Run 2.28 chain missing Run 2.24 binding for ${chain.role}`);
    if (chain.content_memory_id !== content.content_memory_id || chain.workflow_gate_id !== gate.gate_id) {
      throw new Error(`Run 2.28 chain/content/gate mismatch for ${chain.role}`);
    }
    for (const slotId of content.visual_evidence_slot_ids ?? []) {
      if (!(chain.visual_evidence_slot_ids ?? []).includes(slotId)) {
        throw new Error(`Run 2.28 chain ${chain.role} missing visual slot ${slotId}`);
      }
    }
    for (const field of expectedRun228Fields) {
      if (!(chain.required_trace_fields ?? []).includes(field)) {
        throw new Error(`Run 2.28 chain ${chain.role} missing trace field ${field}`);
      }
    }
    for (const key of [
      "source_evidence_summary",
      "extracted_design_rule",
      "workflow_decision",
      "native_ppt_surface_instruction",
      "native_surface_module_id",
      "generated_slide_surface",
      "viewer_inspection_prompt",
      "negative_control_failure_mode",
    ]) {
      if (!String(chain[key] ?? "").trim()) throw new Error(`Run 2.28 chain ${chain.role} missing ${key}`);
    }
  }
}

function validateRun236PresentationSynthesisMemory(memory, evidenceChain) {
  if (memory?.status !== "run2_29_presentation_synthesis_memory_ready_public_blocked") {
    throw new Error("Run 2.36 must consume Run 2.29 presentation synthesis memory");
  }
  if (memory.selected_usecase_id !== selectedUsecaseId || memory.stage_policy !== "repeat_same_five_layers_not_run3") {
    throw new Error("Run 2.36 presentation synthesis usecase/stage mismatch");
  }
  if (memory.source_evidence_chain_layer !== "run2_28_evidence_chain_view_model.json") {
    throw new Error("Run 2.36 presentation synthesis must bind Run 2.28 evidence chain");
  }
  if (memory.surface_policy?.primary_reader_experience !== "presentation_first_surface") {
    throw new Error("Run 2.36 must render a presentation-first surface");
  }
  if (memory.surface_policy?.secondary_reviewer_experience !== "compressed_evidence_spine") {
    throw new Error("Run 2.36 must keep a readable evidence spine");
  }
  if (memory.surface_policy?.forbidden_primary_surface !== "four_column_audit_table") {
    throw new Error("Run 2.36 must forbid four-column audit table as primary surface");
  }
  const chainsByRole = new Map((evidenceChain.slide_evidence_chains ?? []).map((chain) => [chain.role, chain]));
  const roles = ["cover", "setup", "contrast", "proof", "climax", "close"];
  const records = memory.slide_synthesis_records ?? [];
  if (records.length !== roles.length || records.map((record) => record.role).join(",") !== roles.join(",")) {
    throw new Error("Run 2.36 presentation synthesis must contain the six canonical slide roles in order");
  }
  const chainOrder = ["source evidence", "extracted design rule", "workflow decision", "generated slide surface"];
  const requiredTraceFields = [
    "run2_28_evidence_chain_id",
    "run2_28_multimodal_source_record_ids",
    "run2_28_extracted_design_rule",
    "run2_28_workflow_decision",
    "run2_28_native_surface_module_id",
    "run2_29_synthesis_record_id",
    "run2_29_public_surface_mode",
    "run2_29_trace_surface_mode",
    "run2_29_presentation_module_id",
    "run2_29_chain_compression_policy",
  ];
  for (const record of records) {
    const chain = chainsByRole.get(record.role);
    if (!chain || record.evidence_chain_id !== chain.evidence_chain_id) {
      throw new Error(`Run 2.36 synthesis/evidence-chain mismatch for ${record.role}`);
    }
    if (record.source_native_surface_module_id !== chain.native_surface_module_id) {
      throw new Error(`Run 2.36 synthesis source module mismatch for ${record.role}`);
    }
    if (!String(record.presentation_module_id ?? "").startsWith("drawRun229")) {
      throw new Error(`Run 2.36 synthesis missing presentation module for ${record.role}`);
    }
    if (record.trace_surface_mode !== "manifest_and_html_viewer_full_chain_visible") {
      throw new Error(`Run 2.36 synthesis trace surface mode mismatch for ${record.role}`);
    }
    if (JSON.stringify(record.visible_on_slide_evidence_spine_steps ?? []) !== JSON.stringify(chainOrder)) {
      throw new Error(`Run 2.36 synthesis chain order mismatch for ${record.role}`);
    }
    for (const policy of [
      "do_not_render_four_column_audit_table_as_primary_surface",
      "make_evidence_chain_secondary_to_editorial_claim_and_proof_object",
      "preserve_full_chain_in_trace_manifest_and_html_viewer",
    ]) {
      if (!(record.chain_compression_policy ?? []).includes(policy)) {
        throw new Error(`Run 2.36 synthesis missing policy ${policy} for ${record.role}`);
      }
    }
    for (const field of requiredTraceFields) {
      if (!(record.preserved_trace_fields ?? []).includes(field)) {
        throw new Error(`Run 2.36 synthesis missing preserved trace field ${field} for ${record.role}`);
      }
    }
  }
}

function validateRun235VisualEvidenceRealismWorkflow(data) {
  const { mainSurfaceAudit, priorRerun, workflowResult, realismMemory, compositionMemory, workflowGates } = data;
  if (mainSurfaceAudit?.status !== "run2_34_main_surface_visual_evidence_audit_public_blocked") {
    throw new Error("Run 2.36 must consume Run 2.34 main-surface visual-evidence audit");
  }
  if (mainSurfaceAudit.quality_summary?.top_next_layer_to_thicken !== "usecase_specific_visual_evidence_asset_realism_and_editorial_composition") {
    throw new Error("Run 2.34 audit did not point to Run 2.35 visual-evidence realism workflow");
  }
  if (priorRerun?.status !== "run2_33_main_surface_visual_evidence_rerun_public_blocked") {
    throw new Error("Run 2.36 prior generated run must be Run 2.33");
  }
  if (workflowResult?.status !== "run2_35_visual_evidence_realism_workflow_ready_public_blocked") {
    throw new Error("Run 2.36 must consume Run 2.35 workflow result");
  }
  if (workflowResult.creates_new_ppt_deck !== false || workflowResult.public_ready !== false) {
    throw new Error("Run 2.35 workflow boundary mismatch");
  }
  if (realismMemory?.status !== "run2_35_visual_evidence_asset_realism_memory_ready_public_blocked") {
    throw new Error("Run 2.35 realism memory status mismatch");
  }
  if (compositionMemory?.status !== "run2_35_editorial_composition_memory_ready_public_blocked") {
    throw new Error("Run 2.35 composition memory status mismatch");
  }
  if (workflowGates?.status !== "run2_35_visual_evidence_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.35 workflow gates status mismatch");
  }
  if (realismMemory.selected_usecase_id !== selectedUsecaseId || compositionMemory.selected_usecase_id !== selectedUsecaseId) {
    throw new Error("Run 2.35 selected usecase mismatch");
  }
  const roles = ["cover", "setup", "contrast", "proof", "climax", "close"];
  if ((realismMemory.visual_evidence_asset_realism_records ?? []).length !== 12) {
    throw new Error("Run 2.35 must provide twelve realism records");
  }
  if ((compositionMemory.editorial_composition_records ?? []).length !== 6 || (workflowGates.gates ?? []).length !== 6) {
    throw new Error("Run 2.35 must provide six composition records and six gates");
  }
  for (const role of roles) {
    const realismRecords = (realismMemory.visual_evidence_asset_realism_records ?? []).filter((record) => record.role === role);
    const composition = (compositionMemory.editorial_composition_records ?? []).find((record) => record.role === role);
    const gate = (workflowGates.gates ?? []).find((record) => record.role === role);
    if (realismRecords.length < 2 || !composition || !gate) throw new Error(`Run 2.35 missing role contract for ${role}`);
    if (gate.required_editorial_composition_memory_id !== composition.composition_memory_id) {
      throw new Error(`Run 2.35 gate/composition mismatch for ${role}`);
    }
    for (const id of gate.required_realism_memory_ids ?? []) {
      if (!realismRecords.some((record) => record.realism_memory_id === id)) {
        throw new Error(`Run 2.35 gate/realism mismatch for ${role}`);
      }
    }
    for (const field of [
      "run2_35_visual_evidence_asset_realism_ids",
      "run2_35_editorial_composition_memory_id",
      "run2_35_realism_gate_id",
      "run2_35_observable_product_state",
      "run2_35_hero_canvas_share_target",
      "run2_35_visual_evidence_realism_execution_status",
    ]) {
      if (!(gate.required_trace_fields ?? []).includes(field)) {
        throw new Error(`Run 2.35 gate ${role} missing trace field ${field}`);
      }
    }
  }
}

function run236RequiredModulesByRole(workflowGates) {
  return new Map(
    (workflowGates.gates ?? []).map((gate) => [
      gate.role,
      ["drawRun236EditorialAnchorObject", "drawRun236RealisticProductState", "drawRun236RealismGateRibbon"],
    ]),
  );
}

function loadRun236ContractData(arm) {
  const mainSurfaceAudit = readRun236PackJsonForArm(arm, RUN2_36_INPUTS.mainSurfaceVisualEvidenceAudit);
  const priorRerun = readRun236PackJsonForArm(arm, RUN2_36_INPUTS.priorMainSurfaceVisualEvidenceRerun);
  const workflowResult = readRun236PackJsonForArm(arm, RUN2_36_INPUTS.visualEvidenceRealismWorkflowResult);
  const realismMemory = readRun236PackJsonForArm(arm, RUN2_36_INPUTS.visualEvidenceAssetRealismMemory);
  const compositionMemory = readRun236PackJsonForArm(arm, RUN2_36_INPUTS.editorialCompositionMemory);
  const workflowGates = readRun236PackJsonForArm(arm, RUN2_36_INPUTS.visualEvidenceWorkflowGates);
  const data = { mainSurfaceAudit, priorRerun, workflowResult, realismMemory, compositionMemory, workflowGates };
  validateRun235VisualEvidenceRealismWorkflow(data);
  return {
    ...data,
    requiredModulesByRole: run236RequiredModulesByRole(workflowGates),
    status: "run2_36_visual_evidence_realism_contract_ready",
  };
}

function selectRun236ForSlide(role, contractData) {
  const realismRecords = (contractData.realismMemory?.visual_evidence_asset_realism_records ?? []).filter((item) => item.role === role);
  const composition = (contractData.compositionMemory?.editorial_composition_records ?? []).find((item) => item.role === role);
  const gate = (contractData.workflowGates?.gates ?? []).find((item) => item.role === role);
  if (realismRecords.length < 2) throw new Error(`Run 2.35 realism memory missing role ${role}`);
  if (!composition) throw new Error(`Run 2.35 composition memory missing role ${role}`);
  if (!gate) throw new Error(`Run 2.35 workflow gate missing role ${role}`);
  return { realismRecords, composition, gate };
}

function drawRun236EditorialAnchorObject(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236EditorialAnchorObject");
  const share = Math.max(selection.composition.hero_canvas_share_target, spec.role === "climax" ? 0.68 : 0.35);
  const widthShare = spec.role === "climax" ? 0.88 : spec.role === "proof" ? 0.76 : 0.72;
  const heightShare = Math.min(0.86, Math.max(0.52, share / widthShare + 0.02));
  const heroW = Math.round(MAIN_CANVAS.w * widthShare);
  const heroH = Math.round(MAIN_CANVAS.h * heightShare);
  const x = spec.role === "setup" || spec.role === "contrast" ? 338 : 82;
  const y = spec.role === "climax" ? 114 : 144;
  moduleLabel(slide, 76, 96, "Run 2.35 editorial anchor", arm);
  text(slide, spec.title, 76, 116, spec.role === "climax" ? 470 : 560, 70, {
    fontSize: spec.role === "climax" ? 34 : 32,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  rect(slide, x + 28, y + 28, heroW, heroH, "#dce8eb", colorLine("#dce8eb", 1));
  rect(slide, x, y, heroW, heroH, C.white, colorLine(arm.palette.accent, 2));
  text(slide, selection.composition.editorial_anchor_object, x + 34, y + 30, heroW - 68, 44, {
    fontSize: 20,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, selection.composition.editorial_anchor_object);
  registerHero(metrics, x, y, heroW, heroH);
  registerProof(metrics, 1);
  registerZones(metrics, 2);
}

function drawRun236RealisticProductState(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236RealisticProductState");
  const states = selection.realismRecords.slice(0, 2);
  const panel = spec.role === "climax" ? { x: 208, y: 286, w: 742, h: 236 } : { x: 128, y: 284, w: 670, h: 230 };
  rect(slide, panel.x, panel.y, panel.w, panel.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  text(slide, "observable product state", panel.x + 34, panel.y + 26, panel.w - 68, 22, {
    fontSize: 18,
    title: true,
    bold: true,
    color: C.white,
  });
  states.forEach((record, index) => {
    const cardX = panel.x + 34 + index * ((panel.w - 92) / 2);
    const cardW = (panel.w - 118) / 2;
    rect(slide, cardX, panel.y + 76, cardW, 112, index === 0 ? arm.palette.proof ?? C.signal : "#26313b", colorLine(index === 0 ? arm.palette.proof ?? C.signal : "#4b5964", 1));
    text(slide, record.observable_product_state, cardX + 18, panel.y + 96, cardW - 36, 40, {
      fontSize: 11,
      bold: true,
      color: C.white,
    });
    text(slide, record.business_context_caption, cardX + 18, panel.y + 148, cardW - 36, 26, {
      fontSize: 8.4,
      color: "#dbe6eb",
    });
    registerText(metrics, `${record.observable_product_state} ${record.business_context_caption}`);
  });
  registerRealisticVisualEvidence(metrics, states.length);
  registerContentCards(metrics, states.length);
  registerProof(metrics, states.length);
}

function drawRun236RealismGateRibbon(slide, arm, spec, selection, metrics) {
  registerRun236Module(metrics, "drawRun236RealismGateRibbon");
  const x = 884;
  const y = spec.role === "climax" ? 132 : 154;
  const h = spec.role === "climax" ? 408 : 352;
  rect(slide, x, y, 278, h, "#121922", colorLine("#34424f", 1));
  text(slide, "Run 2.35 gate", x + 22, y + 24, 230, 18, {
    fontSize: 11,
    mono: true,
    bold: true,
    color: arm.palette.accent2,
  });
  text(slide, selection.gate.gate_id, x + 22, y + 56, 230, 24, {
    fontSize: 9,
    mono: true,
    color: "#dce8ee",
  });
  [
    ["realism ids", selection.gate.required_realism_memory_ids.join(" / ")],
    ["composition", selection.composition.composition_memory_id],
    ["hero target", String(selection.composition.hero_canvas_share_target)],
    ["public gate", selection.gate.public_release_gate],
  ].forEach(([label, value], index) => {
    const rowY = y + 108 + index * 58;
    rect(slide, x + 22, rowY, 234, 42, index === 0 ? arm.palette.proof ?? C.signal : "#222d37", colorLine("#4b5964", 1));
    text(slide, label, x + 36, rowY + 8, 86, 10, {
      fontSize: 7.3,
      mono: true,
      bold: true,
      color: index === 0 ? C.white : arm.palette.accent2,
    });
    text(slide, compactText(value, 34), x + 124, rowY + 8, 118, 18, {
      fontSize: 8,
      mono: true,
      color: C.white,
    });
    registerText(metrics, `${label} ${value}`);
  });
  registerGate(metrics, 2);
  registerWorkflow(metrics, 4);
}

function renderRun236FullSlide(presentation, spec, arm, n, fullData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const selection = selectRun236ForSlide(spec.role, fullData);
  drawRun236EditorialAnchorObject(slide, arm, spec, selection, metrics);
  drawRun236RealisticProductState(slide, arm, spec, selection, metrics);
  drawRun236RealismGateRibbon(slide, arm, spec, selection, metrics);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function renderControlSlide(presentation, spec, arm, n, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const mode = arm.armId === "bad_visual_evidence_realism_memory" ? "bad" : arm.armId === "run1_5_skill" ? "run1_5" : "prompt";
  drawControlSlideContent(slide, arm, spec, metrics, mode);
  drawControlGate(slide, arm, spec, metrics, {
    x: spec.role === "climax" ? 1022 : 904,
    y: spec.role === "close" ? 326 : spec.role === "climax" ? 492 : 438,
    w: spec.role === "close" ? 226 : spec.role === "climax" ? 178 : 210,
    h: spec.role === "climax" ? 92 : 118,
    headline: arm.armId === "bad_visual_evidence_realism_memory" ? "pack missing" : "public blocked",
    line: arm.armId === "bad_visual_evidence_realism_memory" ? "label only / no 2.36 synthesis" : "no Run 2.36 trace",
  });
  proofFooter(slide, arm, null);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertRun236ArmInputBoundaries(arm);
  const fullRun236 = arm.armId === "run2_36_full_visual_evidence_realism";
  const fullData = fullRun236 ? context.fullData ?? loadRun236ContractData(arm) : null;
  const requiredModulesByRole = fullData?.requiredModulesByRole ?? new Map();
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = fullRun236 && arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun236 ? selectedUsecaseId : "",
    prior_rerun_run_id: fullRun236 ? fullData.priorRerun.run_id : "",
    prior_rerun_status: fullRun236 ? fullData.priorRerun.status : "",
    run2_34_audit_status: fullRun236 ? fullData.mainSurfaceAudit.status : "",
    run2_35_workflow_status: fullRun236 ? fullData.workflowResult.status : "",
    run2_35_realism_memory_status: fullRun236 ? fullData.realismMemory.status : "",
    run2_35_composition_memory_status: fullRun236 ? fullData.compositionMemory.status : "",
    run2_35_workflow_gate_status: fullRun236 ? fullData.workflowGates.status : "",
    commercial_case: `${pack}/commercial_case.md`,
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.36 visual-evidence realism arm-specific generation from scripts/generate_ppt_run2_36_visual_evidence_realism_arms.mjs",
      no_cross_arm_reuse: [
        "cached memory summaries",
        "generated slide code",
        "layout JSON",
        "screenshots",
        "contact sheets",
        "QA notes",
        "Run 2.35 realism memory in control arms",
        "Run 2.35 composition memory in control arms",
        "Run 2.35 workflow gate ids in control arms",
        "Run 2.36 visual-evidence realism in control arms",
      ],
    },
    model_provider: "Codex local code generation with artifact-tool native presentation primitives",
    tool_versions: {
      artifact_tool: "bundled @oai/artifact-tool via presentations skill",
      node: "codex primary runtime",
      python: "workspace runtime for contact sheet and layout QA",
    },
    release_decision: arm.release,
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const actualCodeModuleIds = Array.from(roleMetrics.visualModuleIds);
      const selection = fullRun236 ? selectRun236ForSlide(slide.role, fullData) : null;
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_36_contract_status: fullRun236
          ? hasRenderedMetrics
            ? "full_arm_native_generator_rendered"
            : "full_arm_contract_preview_not_rendered"
          : "boundary_control_not_run2_36_full",
        run2_34_source_audit_target: fullRun236 ? fullData.mainSurfaceAudit.quality_summary.top_next_layer_to_thicken : "",
        run2_35_visual_evidence_asset_realism_ids: fullRun236
          ? selection.realismRecords.map((record) => record.realism_memory_id)
          : [],
        run2_35_editorial_composition_memory_id: fullRun236 ? selection.composition.composition_memory_id : "",
        run2_35_realism_gate_id: fullRun236 ? selection.gate.gate_id : "",
        run2_35_observable_product_state: fullRun236
          ? selection.realismRecords.map((record) => record.observable_product_state).join(" | ")
          : "",
        run2_35_business_context_caption: fullRun236
          ? selection.realismRecords.map((record) => record.business_context_caption).join(" | ")
          : "",
        run2_35_editorial_anchor_object: fullRun236 ? selection.composition.editorial_anchor_object : "",
        run2_35_hero_canvas_share_target: fullRun236 ? selection.composition.hero_canvas_share_target : "",
        run2_35_visual_evidence_realism_execution_status: fullRun236
          ? "usecase_specific_visual_evidence_asset_realism_and_editorial_composition_consumed_before_native_ppt_generation"
          : "",
        run2_36_required_code_module_ids: fullRun236 ? requiredModulesByRole.get(slide.role) ?? [] : [],
        run2_36_code_module_ids: fullRun236
          ? hasRenderedMetrics
            ? actualCodeModuleIds
            : requiredModulesByRole.get(slide.role) ?? []
          : [],
        run2_36_bad_control_probe: fullRun236
          ? "bad_visual_evidence_realism_memory may receive the selected usecase label but forbids Run 2.35 realism memory, editorial composition memory, workflow gates, Run 2.34 audit, and Run 2.33 rerun result"
          : "boundary_control",
        negative_control_usecase_id: arm.armId === "bad_visual_evidence_realism_memory" ? selectedUsecaseId : "",
        layout_metrics: {
          text_box_count: roleMetrics.textBoxCount,
          visible_words: roleMetrics.visibleWords,
          proof_objects: roleMetrics.proofObjects,
          zones: roleMetrics.zones,
          workflow_objects: roleMetrics.workflowObjects,
          gate_objects: roleMetrics.gateObjects,
          content_cards: roleMetrics.contentCards,
          visual_evidence_objects: roleMetrics.visualEvidenceObjects,
          realistic_visual_evidence_objects: roleMetrics.realisticVisualEvidenceObjects,
          thickened_surface_proof_points: roleMetrics.thickenedSurfaceProofPoints,
          hero_object_canvas_share: Number(roleMetrics.heroShare.toFixed(3)),
        },
      };
    }),
  };
}

function assertRun236ContentVisualGateSelfCheck(trace) {
  if (trace.arm_id !== "run2_36_full_visual_evidence_realism") return;
  if (trace.selected_usecase_id !== selectedUsecaseId) throw new Error("Run 2.36 full trace did not lock the selected usecase");
  if (trace.run2_35_workflow_status !== "run2_35_visual_evidence_realism_workflow_ready_public_blocked") {
    throw new Error("Run 2.36 full trace did not consume Run 2.35 workflow result");
  }
  for (const slide of trace.slides) {
    if (slide.run2_36_contract_status !== "full_arm_native_generator_rendered") {
      throw new Error(`Run 2.36 full slide ${slide.slide_id} was not rendered with native module metrics`);
    }
    for (const field of EXPECTED_RUN2_36_TRACE_FIELDS) {
      const value = slide[field];
      const empty =
        value == null ||
        (Array.isArray(value) && value.length === 0) ||
        (typeof value === "string" && value.trim() === "") ||
        (typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === 0);
      if (empty) throw new Error(`Run 2.36 full slide ${slide.slide_id} missing ${field}`);
    }
    if ((slide.run2_35_visual_evidence_asset_realism_ids ?? []).length < 2) {
      throw new Error(`Run 2.36 full slide ${slide.slide_id} missing at least two Run 2.35 realism ids`);
    }
    if (!String(slide.run2_35_editorial_composition_memory_id ?? "").startsWith("composition_2_35_")) {
      throw new Error(`Run 2.36 full slide ${slide.slide_id} missing Run 2.35 composition memory`);
    }
    if (!String(slide.run2_35_realism_gate_id ?? "").startsWith("gate_2_35_")) {
      throw new Error(`Run 2.36 full slide ${slide.slide_id} missing Run 2.35 realism gate`);
    }
    if (slide.run2_35_visual_evidence_realism_execution_status !== "usecase_specific_visual_evidence_asset_realism_and_editorial_composition_consumed_before_native_ppt_generation") {
      throw new Error(`Run 2.36 full slide ${slide.slide_id} missing Run 2.35 consumption status`);
    }
    if (!(Number(slide.run2_35_hero_canvas_share_target) >= 0.35)) {
      throw new Error(`Run 2.36 full slide ${slide.slide_id} missing hero canvas share target`);
    }
    const actualCodeModules = new Set(slide.run2_36_code_module_ids ?? []);
    for (const requiredCodeModule of slide.run2_36_required_code_module_ids ?? []) {
      if (!actualCodeModules.has(requiredCodeModule)) {
        throw new Error(`Run 2.36 full slide ${slide.slide_id} did not call required module ${requiredCodeModule}`);
      }
    }
    for (const moduleId of ["drawRun236EditorialAnchorObject", "drawRun236RealisticProductState", "drawRun236RealismGateRibbon"]) {
      if (!actualCodeModules.has(moduleId)) throw new Error(`Run 2.36 full slide ${slide.slide_id} did not call ${moduleId}`);
    }
    if ((slide.layout_metrics?.realistic_visual_evidence_objects ?? 0) < 2) {
      throw new Error(`Run 2.36 full slide ${slide.slide_id} did not render enough realistic visual evidence objects`);
    }
    if ((slide.layout_metrics?.workflow_objects ?? 0) < 4) {
      throw new Error(`Run 2.36 full slide ${slide.slide_id} does not expose the Run 2.35 workflow gate`);
    }
    if ((slide.layout_metrics?.hero_object_canvas_share ?? 0) < Number(slide.run2_35_hero_canvas_share_target)) {
      throw new Error(`Run 2.36 full slide ${slide.slide_id} did not meet hero share target`);
    }
  }
}

function buildArmContract() {
  return armSpecs.map((arm) => ({
    armId: arm.armId,
    label: arm.label,
    contract_status:
      arm.armId === "run2_36_full_visual_evidence_realism"
        ? "run2_36_visual_evidence_realism_contract_ready_requires_render_metrics"
        : "run2_36_boundary_control_contract_ready",
    allowed: arm.allowed,
    forbidden: arm.forbidden,
    palette: arm.palette,
    trace: traceFor(arm),
  }));
}

async function blobToBuffer(blob) {
  if (blob?.data instanceof Uint8Array) return Buffer.from(blob.data);
  const arrayBuffer = await blob.arrayBuffer();
  return Buffer.from(arrayBuffer);
}

function buildNamedContactSheet(out, title, previewPaths, cols = 3, labels = null) {
  const args = [
    path.join(root, "scripts", "build_ppt_contact_sheet.py"),
    "--out",
    out,
    "--title",
    title,
    "--cols",
    String(cols),
  ];
  if (labels) args.push("--labels", ...labels, "--");
  args.push(...previewPaths);
  execFileSync(
    "python3",
    args,
    { cwd: root, stdio: "pipe" },
  );
  return out;
}

function buildContactSheet(workspace, arm, previewPaths) {
  return buildNamedContactSheet(path.join(workspace, "preview", "contact-sheet.png"), arm.label, previewPaths);
}

function buildRun236FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-36-four-arm-contact-sheet.png"),
    "Run 2.36 four-arm comparison",
    sheets,
    sheets.length,
    labels,
  );
}

function buildFullSkillSeriesSheet() {
  const fullSlugs = [
    "ppt-run2-full-vulca",
    "ppt-run2-1-full-vulca",
    "ppt-run2-2-full-vulca",
    "ppt-run2-3-full-vulca",
    "ppt-run2-4-full-vulca",
    "ppt-run2-5-full-vulca",
    "ppt-run2-6-full-vulca",
    "ppt-run2-6r-full-vulca",
    "ppt-run2-7-full-vulca",
    "ppt-run2-8-full-vulca",
    "ppt-run2-9-full-vulca",
    "ppt-run2-10-full-vulca",
    "ppt-run2-13-full-vulca",
    "ppt-run2-14-full-vulca",
    "ppt-run2-16-full-vulca",
    "ppt-run2-19-full-vulca",
    "ppt-run2-22-full-vulca",
    "ppt-run2-25-full-vulca",
    "ppt-run2-33-full-vulca",
    "ppt-run2-36-full-vulca",
  ];
  const sheets = fullSlugs
    .map((slug) => path.join(outRoot, slug, "preview", "contact-sheet.png"))
    .filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  return buildNamedContactSheet(path.join(outRoot, "run2-full-skill-series-horizontal.png"), "Run 2 full-skill series", sheets, sheets.length);
}

async function buildArm(arm) {
  const workspace = path.join(outRoot, arm.slug);
  resetWorkspace(workspace);
  fs.copyFileSync(__filename, path.join(workspace, "slides", "deck-source.mjs"));
  fs.writeFileSync(
    path.join(workspace, "profile-plan.txt"),
    [
      "task mode: create",
      "primary deck-profile: product-platform",
      "secondary deck-profile: design-keynote",
      `arm: ${arm.armId}`,
      `selected usecase: ${selectedUsecaseId}`,
      `allowed inputs: ${arm.allowed.join(", ")}`,
      `forbidden inputs: ${arm.forbidden.join(", ")}`,
      "required proof objects: usecase-specific product state, editorial anchor object, Run 2.35 realism gate ribbon, release gate",
      "source requirements: commercial case always; full arm requires Run 2.34 audit, Run 2.33 rerun result, Run 2.35 realism memory, Run 2.35 editorial composition memory, and Run 2.35 workflow gates before native PPT generation; bad control receives usecase label only",
      "brand authenticity constraints: no copied source visuals, no borrowed brand chrome, no screenshots, no raw tutorial media",
      "profile-specific QA gates: contact-sheet coherence, editable native text/shapes only, Run 2.35 trace preserved, product-platform proof object visible, release gate visibly blocked",
      "known missing inputs: public release approval remains unavailable",
      "",
    ].join("\n"),
  );
  fs.writeFileSync(
    path.join(workspace, "generation-notes.md"),
    [
      `# ${arm.label}`,
      "",
      "Status: generated-local-pending-delivery-qa.",
      "",
      `Allowed inputs: ${arm.allowed.join(", ")}`,
      "",
      `Forbidden inputs: ${arm.forbidden.join(", ")}`,
      "",
      "Visible slide structure is editable artifact-tool text and native shapes only. No images, screenshots, SVG assets, downloaded media, raw video, raw audio, or copied source layouts are used.",
      "",
    ].join("\n"),
  );

  const presentation = Presentation.create(undefined, { slideSize: { width: W, height: H } });
  const metricsByRole = new Map();
  let fullData = null;
  if (arm.armId === "run2_36_full_visual_evidence_realism") {
    fullData = loadRun236ContractData(arm);
  }

  const slides = arm.slides.map((slide, index) =>
    arm.armId === "run2_36_full_visual_evidence_realism"
      ? renderRun236FullSlide(presentation, slide, arm, index + 1, fullData, metricsByRole)
      : renderControlSlide(presentation, slide, arm, index + 1, metricsByRole),
  );

  const outputPath = path.join(workspace, "output", `${arm.slug}.pptx`);
  const pptxBlob = await PresentationFile.exportPptx(presentation);
  fs.writeFileSync(outputPath, await blobToBuffer(pptxBlob));

  const previewPaths = [];
  const layoutResults = [];
  for (let index = 0; index < slides.length; index += 1) {
    const slide = slides[index];
    const slideNo = String(index + 1).padStart(2, "0");
    const previewPath = path.join(workspace, "preview", `slide-${slideNo}.png`);
    const layoutPath = path.join(workspace, "layout", "final", `slide-${slideNo}.layout.json`);
    fs.writeFileSync(previewPath, await blobToBuffer(await slide.export({ format: "png" })));
    fs.writeFileSync(layoutPath, await blobToBuffer(await slide.export({ format: "layout" })));
    previewPaths.push(previewPath);
    layoutResults.push({ layoutPath });
  }

  const trace = traceFor(arm, { fullData, metricsByRole });
  assertRun236ContentVisualGateSelfCheck(trace);
  const contactSheet = buildContactSheet(workspace, arm, previewPaths);

  const manifest = {
    output: outputPath,
    outputBytes: fs.statSync(outputPath).size,
    slideCount: slides.length,
    slideSize: { width: W, height: H },
    previewDir: path.join(workspace, "preview"),
    previewPaths,
    layoutDir: path.join(workspace, "layout", "final"),
    layoutResults,
    contactSheet,
    slides: slides.map((_, index) => ({
      index: index + 1,
      requestedSlideNumber: index + 1,
      source: "scripts/generate_ppt_run2_36_visual_evidence_realism_arms.mjs",
      exportName: `slide${String(index + 1).padStart(2, "0")}`,
    })),
  };
  writeJson(path.join(workspace, "output", "artifact-build-manifest.json"), manifest);
  writeJson(path.join(workspace, "qa", "build_manifest_stdout.json"), manifest);
  writeJson(path.join(workspace, "trace_manifest.json"), trace);
  return { workspace, outputPath, contactSheet, previewPaths };
}

function repoRelative(absPath) {
  return path.relative(root, absPath).split(path.sep).join("/");
}

function writeRun236Result(runSummary) {
  const result = {
    schema_version: 1,
    run_id: "2.36",
    status: "run2_36_visual_evidence_realism_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_data_workflow_run_id: "2.35",
    source_audit_run_id: "2.34",
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      main_surface_visual_evidence_audit: RUN2_36_INPUTS.mainSurfaceVisualEvidenceAudit,
      prior_main_surface_visual_evidence_rerun: RUN2_36_INPUTS.priorMainSurfaceVisualEvidenceRerun,
      visual_evidence_realism_workflow_result: RUN2_36_INPUTS.visualEvidenceRealismWorkflowResult,
      visual_evidence_asset_realism_memory: RUN2_36_INPUTS.visualEvidenceAssetRealismMemory,
      editorial_composition_memory: RUN2_36_INPUTS.editorialCompositionMemory,
      visual_evidence_workflow_gates: RUN2_36_INPUTS.visualEvidenceWorkflowGates,
      source_data_layer: RUN2_36_INPUTS.visualEvidenceRealismWorkflowResult,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_36_visual_evidence_realism_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_36_full_visual_evidence_realism",
      best_internal_arm_verdict:
        "usecase_specific_visual_evidence_asset_realism_and_editorial_composition_consumed_before_native_ppt_generation",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: "usecase_specific_visual_evidence_asset_realism_and_editorial_composition",
      source_audit: RUN2_36_INPUTS.mainSurfaceVisualEvidenceAudit,
      source_workflow_result: RUN2_36_INPUTS.visualEvidenceRealismWorkflowResult,
      replacement_focus: "replace schematic visual evidence tokens with usecase-specific product states and stronger editorial anchors",
      repair_modules: ["drawRun236RealisticProductState", "drawRun236EditorialAnchorObject", "drawRun236RealismGateRibbon"],
      run2_35_realism_records_consumed: 12,
      run2_35_composition_records_consumed: 6,
      run2_35_workflow_gates_consumed: 6,
      required_realistic_visual_evidence_objects_per_full_slide: 2,
      source_run2_34_target_consumed: true,
    },
    visual_quality_boundary:
      "visual_evidence_realism_proof_only_not_public_video_grade_aesthetic_or_human_release_approval",
    control_boundary: {
      bad_visual_evidence_realism_memory: "selected_usecase_label_only_without_run2_35_realism_memory_editorial_composition_memory_workflow_gates_run2_34_audit_or_run2_33_rerun",
      prompt_only: "commercial_case_only_no_run2_35_visual_evidence_realism_workflow",
      run1_5_skill: "prior_baseline_no_run2_35_visual_evidence_realism_workflow",
    },
    remaining_public_release_gates: [
      "human_visual_review",
      "native_or_cross_platform_render_inspection",
      "motion_or_video_review",
      "source_boundary_review",
      "human_release_approval",
    ],
    trace_manifest_requirements: EXPECTED_RUN2_36_TRACE_FIELDS,
    native_module_status: "actual_run2_36_presentation_module_calls_recorded_in_trace_manifest",
    release_boundary: "public_blocked_until_visual_human_review_native_render_review_motion_review_source_boundary_review_and_human_approval",
    next_required_action: "audit_run2_36_outputs_for_visual_evidence_realism_and_editorial_composition_then_continue_thickening_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_36_visual_evidence_realism_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_36_visual_evidence_realism_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.36 Visual Evidence Realism Rerun Result",
      "",
      "Status: rerun completed, public blocked.",
      "",
      "Run 2.36 is the generated four-arm rerun that consumes the Run 2.35 visual evidence realism workflow before native PPT code generation. The full arm reads Run 2.35 realism memory, editorial composition memory, and workflow gates; the negative control receives only the usecase label. It repeats the same five layers and does not advance to Run 3.0.",
      "",
      "The generator is `scripts/generate_ppt_run2_36_visual_evidence_realism_arms.mjs`.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_36_full_visual_evidence_realism`",
      "- `bad_visual_evidence_realism_memory`",
      "",
      "The negative control `bad_visual_evidence_realism_memory` may receive the selected usecase label, but it is blocked from reading the Run 2.35 realism memory, editorial composition memory, workflow gates, Run 2.34 audit, and Run 2.33 rerun result.",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_36_full_visual_evidence_realism`.",
      "",
      "Verdict: `usecase_specific_visual_evidence_asset_realism_and_editorial_composition_consumed_before_native_ppt_generation`.",
      "",
      "Quality delta: `usecase_specific_visual_evidence_asset_realism_and_editorial_composition`. The full arm adds `drawRun236RealisticProductState`, `drawRun236EditorialAnchorObject`, and `drawRun236RealismGateRibbon` so each slide binds Run 2.35 realism ids, composition ids, and gate ids before native drawing.",
      "",
      "Public release remains blocked. This proves Run 2.35 workflow consumption, not final public-video-grade visual quality or high-aesthetic human approval.",
      "",
      "Remaining public release gates: human visual review, native or cross-platform render inspection, motion/video review, source-boundary review, and human release approval.",
      "",
      "## Required Images",
      "",
      `- \`${repoRelative(runSummary.combined_contact_sheet)}\``,
      `- \`${repoRelative(runSummary.full_skill_series_sheet)}\``,
      "",
      "Do not advance to Run 3.0.",
      "",
    ].join("\n"),
  );
  return result;
}

async function main() {
  ensureDir(outRoot);
  const built = [];
  for (const arm of armSpecs) {
    built.push(await buildArm(arm));
  }
  const fourArmSheet = buildRun236FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_36_visual_evidence_realism_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_36_visual_evidence_realism_rerun_summary.json"), runSummary);
  writeRun236Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  EXPECTED_RUN2_36_TRACE_FIELDS,
  RUN2_36_INPUTS,
  RUN2_36_DATA_INPUTS,
  armSpecs,
  assertRun236ArmInputBoundaries,
  assertRun236ContentVisualGateSelfCheck,
  buildArmContract,
  drawRun236LaunchField,
  drawRun236SelectedRouteMap,
  drawRun236ContentEvidenceSurface,
  drawRun236ReadableEvidenceSpine,
  drawRun236VisualEvidenceStoryboard,
  drawRun236MainSurfaceEvidenceLayer,
  drawRun236EditorialLaunchFrame,
  drawRun236AsymmetricProblemFrame,
  drawRun236BeforeAfterEditorialSpread,
  drawRun236ProductProofTheater,
  drawRun236HeroProofScene,
  drawRun236DecisionHandoff,
  drawRun236EvidenceChainSurface,
  drawRun236WorkflowTracePanel,
  drawRun236ClimaxEvidenceObject,
  drawRun236ClimaxProofObject,
  loadRun236ContractData,
  main,
  readRun236PackJsonForArm,
  registerRun236Module,
  run236RequiredModulesByRole,
  run236ContentEvidenceSurfaceGeometry,
  run236EvidenceChainSurfaceGeometry,
  selectRun236ForSlide,
  traceFor,
  validateRun235VisualEvidenceRealismWorkflow,
  validateRun224SingleUsecaseSchemas,
  validateRun230PresentationSynthesisAudit,
  validateRun231SpineClimaxRepairRerun,
  validateRun232SpineClimaxRepairAudit,
  validateRun236EvidenceChainViewModel,
  validateRun236PresentationSynthesisMemory,
};
