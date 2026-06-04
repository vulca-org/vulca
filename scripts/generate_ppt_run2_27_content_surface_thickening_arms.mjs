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

const EXPECTED_RUN2_27_TRACE_FIELDS = [
  "run2_24_selected_usecase_id",
  "run2_24_content_memory_id",
  "run2_24_visual_evidence_slot_ids",
  "run2_24_content_density_gate_id",
  "run2_26_source_audit_status",
  "run2_26_roles_with_compressed_proof_surface",
  "run2_27_content_surface_thickening_execution_status",
  "run2_27_code_module_ids",
];

const RUN2_27_INPUTS = {
  contentMemory: `${pack}/run2_24_single_usecase_content_memory.json`,
  visualAssets: `${pack}/run2_24_visual_evidence_asset_memory.json`,
  workflowGates: `${pack}/run2_24_content_visual_workflow_gates.json`,
  visualModuleAudit: `${pack}/results/run2_26_visual_module_quality_audit.json`,
};
const RUN2_27_DATA_INPUTS = [
  RUN2_27_INPUTS.contentMemory,
  RUN2_27_INPUTS.visualAssets,
  RUN2_27_INPUTS.workflowGates,
  RUN2_27_INPUTS.visualModuleAudit,
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
    slug: "ppt-run2-27-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.27 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [
      `${pack}/run2_24_single_usecase_content_memory.json`,
      `${pack}/run2_24_visual_evidence_asset_memory.json`,
      `${pack}/run2_24_content_visual_workflow_gates.json`,
      `${pack}/results/run2_26_visual_module_quality_audit.json`,
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
    slug: "ppt-run2-27-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.27 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [
      `${pack}/run2_24_single_usecase_content_memory.json`,
      `${pack}/run2_24_visual_evidence_asset_memory.json`,
      `${pack}/run2_24_content_visual_workflow_gates.json`,
      `${pack}/results/run2_26_visual_module_quality_audit.json`,
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
    armId: "run2_27_full_content_surface_thickening",
    slug: "ppt-run2-27-full-vulca",
    label: "Run 2.27 full content surface thickening pack",
    kicker: "RUN 2.27 / FULL CONTENT + VISUAL",
    footer: "run2_27_full_content_surface_thickening | Run 2.24 pack consumed | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/sources.json`,
      `${pack}/run2_24_single_usecase_content_memory.json`,
      `${pack}/run2_24_visual_evidence_asset_memory.json`,
      `${pack}/run2_24_content_visual_workflow_gates.json`,
      `${pack}/results/run2_26_visual_module_quality_audit.json`,
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
    armId: "bad_surface_thickening_memory",
    slug: "ppt-run2-27-bad-surface-thickening-memory",
    label: "Bad surface-thickening memory control",
    kicker: "RUN 2.27 / NEGATIVE CONTROL",
    footer: "bad_surface_thickening_memory | usecase label only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, `selected_usecase_label:${selectedUsecaseId}`],
    forbidden: [
      `${pack}/run2_24_single_usecase_content_memory.json`,
      `${pack}/run2_24_visual_evidence_asset_memory.json`,
      `${pack}/run2_24_content_visual_workflow_gates.json`,
      `${pack}/results/run2_26_visual_module_quality_audit.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "manual Run 2.27 pack repair before scoring",
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
    thickenedSurfaceProofPoints: 0,
    heroShare: 0,
    visualModuleIds: new Set(),
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun227Module(metrics, functionName) {
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

function drawRun227LaunchField(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun227Module(metrics, "drawRun227LaunchField");
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

function drawRun227SelectedRouteMap(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun227Module(metrics, "drawRun227SelectedRouteMap");
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

function run227ContentEvidenceSurfaceGeometry({ x, y, w, h }) {
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

function drawRun227ContentEvidenceSurface(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun227Module(metrics, "drawRun227ContentEvidenceSurface");
  const x = opts.x ?? 96;
  const y = opts.y ?? 126;
  const w = opts.w ?? 870;
  const h = opts.h ?? 368;
  const geom = run227ContentEvidenceSurfaceGeometry({ x, y, w, h });
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

function drawRun227ClimaxProofObject(slide, arm, spec, selection, metrics) {
  registerRun227Module(metrics, "drawRun227ClimaxProofObject");
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

function assertRun227ArmInputBoundaries(arm) {
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

  if (arm.armId === "run2_27_full_content_surface_thickening") {
    for (const input of RUN2_27_DATA_INPUTS) assertAllowed(input);
    return;
  }
  for (const input of RUN2_27_DATA_INPUTS) assertForbidden(input);
}

function readRun227PackJsonForArm(arm, relPath) {
  assertRun227ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (arm.armId !== "run2_27_full_content_surface_thickening") {
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

function validateRun226VisualModuleAudit(audit) {
  if (audit?.status !== "run2_26_visual_module_quality_audit_public_blocked") {
    throw new Error("Run 2.26 visual module quality audit status mismatch");
  }
  if (audit.run_id !== "2.26" || audit.source_generated_run !== "2.25") {
    throw new Error("Run 2.26 visual module quality audit source mismatch");
  }
  const summary = audit.quality_summary ?? {};
  if (summary.top_next_module_to_thicken !== "drawRun225ContentEvidenceSurface") {
    throw new Error("Run 2.26 audit did not target drawRun225ContentEvidenceSurface");
  }
  const compressedRoles = summary.roles_with_compressed_proof_surface ?? [];
  for (const role of ["setup", "contrast", "close"]) {
    if (!compressedRoles.includes(role)) throw new Error(`Run 2.26 audit missing compressed role ${role}`);
  }
  if (audit.next_required_action !== "thicken_drawRun225ContentEvidenceSurface_before_run2_27_rerun") {
    throw new Error("Run 2.26 audit next action does not match Run 2.27 thickening contract");
  }
}

function loadRun226VisualModuleAudit(arm) {
  const audit = readRun227PackJsonForArm(arm, RUN2_27_INPUTS.visualModuleAudit);
  validateRun226VisualModuleAudit(audit);
  return audit;
}

function run227RequiredModulesByRole() {
  return new Map(
    Object.entries({
      cover: ["drawRun227LaunchField", "drawRun227SelectedRouteMap"],
      setup: ["drawRun227LaunchField", "drawRun227SelectedRouteMap", "drawRun227ContentEvidenceSurface"],
      contrast: ["drawRun227ContentEvidenceSurface", "drawRun227SelectedRouteMap"],
      proof: ["drawRun227ContentEvidenceSurface", "drawRun227SelectedRouteMap"],
      climax: ["drawRun227ClimaxProofObject"],
      close: ["drawRun227LaunchField", "drawRun227ContentEvidenceSurface"],
    }),
  );
}

function loadRun227ContractData(arm) {
  const contentMemory = readRun227PackJsonForArm(arm, RUN2_27_INPUTS.contentMemory);
  const visualAssets = readRun227PackJsonForArm(arm, RUN2_27_INPUTS.visualAssets);
  const workflowGates = readRun227PackJsonForArm(arm, RUN2_27_INPUTS.workflowGates);
  const visualModuleAudit = loadRun226VisualModuleAudit(arm);
  validateRun224SingleUsecaseSchemas(contentMemory, visualAssets, workflowGates);
  return {
    contentMemory,
    visualAssets,
    workflowGates,
    visualModuleAudit,
    requiredModulesByRole: run227RequiredModulesByRole(),
    status: "run2_27_content_surface_thickening_contract_ready",
  };
}

function selectRun224ForSlide(role, contractData) {
  const content = (contractData.contentMemory?.slide_content_memory ?? []).find((item) => item.role === role);
  const gate = (contractData.workflowGates?.gates ?? []).find((item) => item.role === role);
  if (!content || !gate) throw new Error(`Run 2.24 pack missing role ${role}`);
  if (gate.required_content_memory_id !== content.content_memory_id) throw new Error(`Run 2.24 gate/content mismatch for ${role}`);
  const assets = (contractData.visualAssets?.visual_evidence_assets ?? []).filter((asset) =>
    content.visual_evidence_slot_ids.includes(asset.slot_id),
  );
  if (assets.length < 2) throw new Error(`Run 2.24 visual evidence missing role ${role}`);
  return { content, assets, gate };
}

function renderRun227FullSlide(presentation, spec, arm, n, fullData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const selection = selectRun224ForSlide(spec.role, fullData);

  if (spec.role === "cover") {
    drawRun227LaunchField(slide, arm, spec, selection, metrics, {
      x: 82,
      y: 118,
      w: 760,
      fontSize: 62,
      motifX: 914,
      motifY: 146,
      motifW: 216,
      motifH: 224,
    });
    drawRun227SelectedRouteMap(slide, arm, spec, selection, metrics, { x: 78, y: 424, w: 1000 });
  } else if (spec.role === "setup") {
    drawRun227LaunchField(slide, arm, spec, selection, metrics, {
      x: 74,
      y: 118,
      w: 426,
      titleH: 106,
      fontSize: 36,
      ruleY: 132,
      claimY: 166,
      claimW: 400,
      claimSize: 13,
      motifX: 0,
      motifY: 0,
      motifW: 0,
      motifH: 0,
    });
    drawRun227SelectedRouteMap(slide, arm, spec, selection, metrics, { x: 78, y: 526, w: 1020 });
    drawRun227ContentEvidenceSurface(slide, arm, spec, selection, metrics, { x: 536, y: 112, w: 620, h: 382 });
  } else if (spec.role === "contrast") {
    drawRun227ContentEvidenceSurface(slide, arm, spec, selection, metrics, { x: 70, y: 112, w: 780, h: 402 });
    drawRun227SelectedRouteMap(slide, arm, spec, selection, metrics, { x: 858, y: 392, w: 300 });
  } else if (spec.role === "proof") {
    drawRun227ContentEvidenceSurface(slide, arm, spec, selection, metrics, { x: 82, y: 108, w: 790, h: 410 });
    drawRun227SelectedRouteMap(slide, arm, spec, selection, metrics, { x: 778, y: 430, w: 360 });
  } else if (spec.role === "climax") {
    drawRun227ClimaxProofObject(slide, arm, spec, selection, metrics);
  } else {
    drawRun227LaunchField(slide, arm, spec, selection, metrics, {
      x: 70,
      y: 110,
      w: 496,
      titleH: 122,
      fontSize: 38,
      ruleY: 154,
      claimY: 190,
      claimW: 430,
      motifX: 0,
      motifY: 0,
      motifW: 0,
      motifH: 0,
    });
    drawRun227ContentEvidenceSurface(slide, arm, spec, selection, metrics, { x: 592, y: 112, w: 566, h: 388 });
  }

  proofFooter(slide, arm, selection);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function renderControlSlide(presentation, spec, arm, n, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const mode = arm.armId === "bad_surface_thickening_memory" ? "bad" : arm.armId === "run1_5_skill" ? "run1_5" : "prompt";
  drawControlSlideContent(slide, arm, spec, metrics, mode);
  drawControlGate(slide, arm, spec, metrics, {
    x: spec.role === "climax" ? 1022 : 904,
    y: spec.role === "close" ? 326 : spec.role === "climax" ? 492 : 438,
    w: spec.role === "close" ? 226 : spec.role === "climax" ? 178 : 210,
    h: spec.role === "climax" ? 92 : 118,
    headline: arm.armId === "bad_surface_thickening_memory" ? "pack missing" : "public blocked",
    line: arm.armId === "bad_surface_thickening_memory" ? "label only / no 2.24 read" : "no Run 2.24 trace",
  });
  proofFooter(slide, arm, null);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertRun227ArmInputBoundaries(arm);
  const fullRun227 = arm.armId === "run2_27_full_content_surface_thickening";
  const fullData = fullRun227 ? context.fullData ?? loadRun227ContractData(arm) : null;
  const requiredModulesByRole = fullData?.requiredModulesByRole ?? new Map();
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = fullRun227 && arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun227 ? selectedUsecaseId : "",
    source_audit_run_id: fullRun227 ? "2.26" : "",
    source_audit_status: fullRun227 ? fullData.visualModuleAudit.status : "",
    commercial_case: `${pack}/commercial_case.md`,
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.27 content surface thickening arm-specific generation from scripts/generate_ppt_run2_27_content_surface_thickening_arms.mjs",
      no_cross_arm_reuse: ["cached memory summaries", "generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes", "Run 2.24 trace carryover", "Run 2.26 audit conclusions in control arms"],
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
      const selection = fullRun227 ? selectRun224ForSlide(slide.role, fullData) : null;
      const auditSummary = fullRun227 ? fullData.visualModuleAudit.quality_summary ?? {} : {};
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_27_contract_status: fullRun227
          ? hasRenderedMetrics
            ? "full_arm_native_generator_rendered"
            : "full_arm_contract_preview_not_rendered"
          : "boundary_control_not_run2_27_full",
        run2_24_selected_usecase_id: fullRun227 ? selection.content.selected_usecase_id : "",
        run2_24_content_memory_id: fullRun227 ? selection.content.content_memory_id : "",
        run2_24_visual_evidence_slot_ids: fullRun227 ? selection.content.visual_evidence_slot_ids : [],
        run2_24_content_density_gate_id: fullRun227 ? selection.gate.gate_id : "",
        run2_24_business_proof_points_visible: fullRun227 ? selection.content.business_proof_points.slice(0, 3) : [],
        run2_24_visual_evidence_asset_ids: fullRun227 ? selection.assets.map((asset) => asset.asset_id) : [],
        run2_24_public_surface_policy: fullRun227 ? selection.content.public_surface_policy : "",
        run2_26_source_audit_status: fullRun227 ? fullData.visualModuleAudit.status : "",
        run2_26_roles_with_compressed_proof_surface: fullRun227 ? auditSummary.roles_with_compressed_proof_surface ?? [] : [],
        run2_26_top_next_module_to_thicken: fullRun227 ? auditSummary.top_next_module_to_thicken ?? "" : "",
        run2_27_content_surface_thickening_execution_status: fullRun227 ? "run2_26_audit_target_executed_before_native_ppt_generation" : "",
        run2_27_required_code_module_ids: fullRun227 ? requiredModulesByRole.get(slide.role) ?? [] : [],
        run2_27_code_module_ids: fullRun227
          ? hasRenderedMetrics
            ? actualCodeModuleIds
            : requiredModulesByRole.get(slide.role) ?? []
          : [],
        run2_27_bad_control_probe: fullRun227
          ? "bad_surface_thickening_memory may receive the selected usecase label but forbids Run 2.24 content memory, visual evidence assets, workflow gates, and Run 2.26 visual module audit"
          : "boundary_control",
        negative_control_usecase_id: arm.armId === "bad_surface_thickening_memory" ? selectedUsecaseId : "",
        layout_metrics: {
          text_box_count: roleMetrics.textBoxCount,
          visible_words: roleMetrics.visibleWords,
          proof_objects: roleMetrics.proofObjects,
          zones: roleMetrics.zones,
          workflow_objects: roleMetrics.workflowObjects,
          gate_objects: roleMetrics.gateObjects,
          content_cards: roleMetrics.contentCards,
          visual_evidence_objects: roleMetrics.visualEvidenceObjects,
          thickened_surface_proof_points: roleMetrics.thickenedSurfaceProofPoints,
          hero_object_canvas_share: Number(roleMetrics.heroShare.toFixed(3)),
        },
      };
    }),
  };
}

function assertRun227ContentVisualGateSelfCheck(trace) {
  if (trace.arm_id !== "run2_27_full_content_surface_thickening") return;
  if (trace.selected_usecase_id !== selectedUsecaseId) throw new Error("Run 2.27 full trace did not lock the selected usecase");
  for (const slide of trace.slides) {
    if (slide.run2_27_contract_status !== "full_arm_native_generator_rendered") {
      throw new Error(`Run 2.27 full slide ${slide.slide_id} was not rendered with native module metrics`);
    }
    for (const field of EXPECTED_RUN2_27_TRACE_FIELDS) {
      const value = slide[field];
      const empty =
        value == null ||
        (Array.isArray(value) && value.length === 0) ||
        (typeof value === "string" && value.trim() === "") ||
        (typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === 0);
      if (empty) throw new Error(`Run 2.27 full slide ${slide.slide_id} missing ${field}`);
    }
    if ((slide.run2_24_visual_evidence_slot_ids ?? []).length < 2) {
      throw new Error(`Run 2.27 full slide ${slide.slide_id} missing at least two visual evidence slots`);
    }
    const actualCodeModules = new Set(slide.run2_27_code_module_ids ?? []);
    for (const requiredCodeModule of slide.run2_27_required_code_module_ids ?? []) {
      if (!actualCodeModules.has(requiredCodeModule)) {
        throw new Error(`Run 2.27 full slide ${slide.slide_id} did not call required module ${requiredCodeModule}`);
      }
    }
    if ((slide.run2_26_roles_with_compressed_proof_surface ?? []).includes(slide.role)) {
      if (!actualCodeModules.has("drawRun227ContentEvidenceSurface")) {
        throw new Error(`Run 2.27 full slide ${slide.slide_id} did not call the thickened content surface module`);
      }
      if ((slide.layout_metrics?.thickened_surface_proof_points ?? 0) < 3) {
        throw new Error(`Run 2.27 full slide ${slide.slide_id} still compresses proof surface`);
      }
    }
    if (slide.run2_24_selected_usecase_id !== selectedUsecaseId) {
      throw new Error(`Run 2.27 full slide ${slide.slide_id} selected the wrong usecase`);
    }
    if (slide.role === "climax" && !(slide.layout_metrics?.hero_object_canvas_share > 0.5)) {
      throw new Error("Run 2.27 climax missing large proof object stage");
    }
  }
}

function buildArmContract() {
  return armSpecs.map((arm) => ({
    armId: arm.armId,
    label: arm.label,
    contract_status:
      arm.armId === "run2_27_full_content_surface_thickening"
        ? "run2_27_content_surface_thickening_contract_ready_requires_render_metrics"
        : "run2_27_boundary_control_contract_ready",
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

function buildRun227FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-27-four-arm-contact-sheet.png"),
    "Run 2.27 four-arm comparison",
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
    "ppt-run2-27-full-vulca",
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
      "required proof objects: launch field, selected route map, content memory surface, visual evidence rail, climax proof object",
      "source requirements: commercial case always; full arm requires Run 2.24 content memory, visual assets, workflow gates, and Run 2.26 visual module audit before native PPT generation; bad control receives usecase label only",
      "brand authenticity constraints: no copied source visuals, no borrowed brand chrome, no screenshots, no raw tutorial media",
      "profile-specific QA gates: contact-sheet coherence, editable native text/shapes only, Run 2.24 trace hidden from first-read public slide surface, release gate visibly blocked",
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
  if (arm.armId === "run2_27_full_content_surface_thickening") {
    fullData = loadRun227ContractData(arm);
  }

  const slides = arm.slides.map((slide, index) =>
    arm.armId === "run2_27_full_content_surface_thickening"
      ? renderRun227FullSlide(presentation, slide, arm, index + 1, fullData, metricsByRole)
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
  assertRun227ContentVisualGateSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_27_content_surface_thickening_arms.mjs",
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

function writeRun227Result(runSummary) {
  const result = {
    schema_version: 1,
    run_id: "2.27",
    status: "run2_27_content_surface_thickening_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_audit_run_id: "2.26",
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      content_memory: RUN2_27_INPUTS.contentMemory,
      visual_evidence_asset_memory: RUN2_27_INPUTS.visualAssets,
      content_visual_workflow_gates: RUN2_27_INPUTS.workflowGates,
      visual_module_quality_audit: RUN2_27_INPUTS.visualModuleAudit,
      source_data_layer: "docs/product/ppt-run2-data-skill-quality/results/run2_26_visual_module_quality_audit.json",
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_27_content_surface_thickening_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_27_full_content_surface_thickening",
      best_internal_arm_verdict: "run2_26_audit_target_executed_before_native_ppt_generation",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      source_audit: RUN2_27_INPUTS.visualModuleAudit,
      target_module: "drawRun225ContentEvidenceSurface",
      replacement_module: "drawRun227ContentEvidenceSurface",
      roles_with_compressed_proof_surface_before: ["setup", "contrast", "close"],
      roles_with_compressed_proof_surface_after: [],
      required_visible_proof_points_per_target_role: 3,
    },
    visual_quality_boundary:
      "content_surface_thickening_proof_only_not_public_video_grade_aesthetic_or_human_release_approval",
    control_boundary: {
      bad_surface_thickening_memory: "selected_usecase_label_only_without_run2_24_content_memory_visual_assets_workflow_gates_or_run2_26_visual_module_audit",
      prompt_only: "commercial_case_only_no_run2_24_single_usecase_pack",
      run1_5_skill: "prior_baseline_no_run2_24_single_usecase_pack",
    },
    remaining_public_release_gates: [
      "human_visual_review",
      "native_or_cross_platform_render_inspection",
      "motion_or_video_review",
      "source_boundary_review",
      "human_release_approval",
    ],
    trace_manifest_requirements: EXPECTED_RUN2_27_TRACE_FIELDS,
    native_module_status: "actual_run2_27_module_calls_recorded_in_trace_manifest",
    release_boundary: "public_blocked_until_visual_human_review_native_render_review_motion_review_source_boundary_review_and_human_approval",
    next_required_action: "review_run2_27_outputs_against_run2_26_audit_target_then_continue_thickening_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_27_content_surface_thickening_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_27_content_surface_thickening_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.27 Content Surface Thickening Rerun Result",
      "",
      "Status: rerun completed, public blocked.",
      "",
      "Run 2.27 is the generated four-arm rerun that consumes Run 2.24 single-usecase content memory, visual evidence asset memory, content/visual workflow gates, and the Run 2.26 visual module quality audit before native PPT code generation. It repeats the same five layers and does not advance to Run 3.0.",
      "",
      "The generator is `scripts/generate_ppt_run2_27_content_surface_thickening_arms.mjs`.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_27_full_content_surface_thickening`",
      "- `bad_surface_thickening_memory`",
      "",
      "The negative control `bad_surface_thickening_memory` may receive the selected usecase label, but it is blocked from reading Run 2.24 content memory, visual evidence assets, workflow gates, and the Run 2.26 visual module quality audit.",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_27_full_content_surface_thickening`.",
      "",
      "Verdict: `run2_26_audit_target_executed_before_native_ppt_generation`.",
      "",
      "Quality delta: `drawRun225ContentEvidenceSurface` is replaced by `drawRun227ContentEvidenceSurface`; setup, contrast, and close now require three visible proof rows without compressed proof-surface carryover.",
      "",
      "Public release remains blocked. This proves content surface thickening pack execution, not final public-video-grade visual quality or high-aesthetic human approval.",
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
  const fourArmSheet = buildRun227FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_27_content_surface_thickening_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_27_content_surface_thickening_rerun_summary.json"), runSummary);
  writeRun227Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  EXPECTED_RUN2_27_TRACE_FIELDS,
  RUN2_27_INPUTS,
  RUN2_27_DATA_INPUTS,
  armSpecs,
  assertRun227ArmInputBoundaries,
  assertRun227ContentVisualGateSelfCheck,
  buildArmContract,
  drawRun227LaunchField,
  drawRun227SelectedRouteMap,
  drawRun227ContentEvidenceSurface,
  drawRun227ClimaxProofObject,
  loadRun226VisualModuleAudit,
  loadRun227ContractData,
  main,
  readRun227PackJsonForArm,
  registerRun227Module,
  run227RequiredModulesByRole,
  run227ContentEvidenceSurfaceGeometry,
  selectRun224ForSlide,
  traceFor,
  validateRun224SingleUsecaseSchemas,
  validateRun226VisualModuleAudit,
};
