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

const EXPECTED_RUN2_29_TRACE_FIELDS = [
  "run2_24_selected_usecase_id",
  "run2_24_content_memory_id",
  "run2_24_visual_evidence_slot_ids",
  "run2_24_content_density_gate_id",
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
  "run2_29_presentation_synthesis_execution_status",
  "run2_29_code_module_ids",
];

const RUN2_29_INPUTS = {
  presentationSynthesis: `${pack}/run2_29_presentation_synthesis_memory.json`,
  evidenceChain: `${pack}/run2_28_evidence_chain_view_model.json`,
  contentMemory: `${pack}/run2_24_single_usecase_content_memory.json`,
  visualAssets: `${pack}/run2_24_visual_evidence_asset_memory.json`,
  workflowGates: `${pack}/run2_24_content_visual_workflow_gates.json`,
  priorRerun: `${pack}/results/run2_28_evidence_chain_rerun_result.json`,
};
const RUN2_29_DATA_INPUTS = [
  RUN2_29_INPUTS.presentationSynthesis,
  RUN2_29_INPUTS.evidenceChain,
  RUN2_29_INPUTS.contentMemory,
  RUN2_29_INPUTS.visualAssets,
  RUN2_29_INPUTS.workflowGates,
  RUN2_29_INPUTS.priorRerun,
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
    slug: "ppt-run2-29-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.29 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [
      `${pack}/run2_24_single_usecase_content_memory.json`,
      `${pack}/run2_24_visual_evidence_asset_memory.json`,
      `${pack}/run2_24_content_visual_workflow_gates.json`,
      `${pack}/run2_29_presentation_synthesis_memory.json`,
      `${pack}/run2_28_evidence_chain_view_model.json`,
      `${pack}/results/run2_28_evidence_chain_rerun_result.json`,
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
    slug: "ppt-run2-29-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.29 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [
      `${pack}/run2_24_single_usecase_content_memory.json`,
      `${pack}/run2_24_visual_evidence_asset_memory.json`,
      `${pack}/run2_24_content_visual_workflow_gates.json`,
      `${pack}/run2_29_presentation_synthesis_memory.json`,
      `${pack}/run2_28_evidence_chain_view_model.json`,
      `${pack}/results/run2_28_evidence_chain_rerun_result.json`,
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
    armId: "run2_29_full_presentation_synthesis",
    slug: "ppt-run2-29-full-vulca",
    label: "Run 2.29 full presentation synthesis pack",
    kicker: "RUN 2.29 / FULL PRESENTATION SYNTHESIS",
    footer: "run2_29_full_presentation_synthesis | presentation-first surface + compressed evidence spine | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/sources.json`,
      `${pack}/run2_29_presentation_synthesis_memory.json`,
      `${pack}/run2_28_evidence_chain_view_model.json`,
      `${pack}/run2_24_single_usecase_content_memory.json`,
      `${pack}/run2_24_visual_evidence_asset_memory.json`,
      `${pack}/run2_24_content_visual_workflow_gates.json`,
      `${pack}/results/run2_28_evidence_chain_rerun_result.json`,
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
    armId: "bad_presentation_synthesis_memory",
    slug: "ppt-run2-29-bad-presentation-synthesis-memory",
    label: "Bad presentation-synthesis memory control",
    kicker: "RUN 2.29 / NEGATIVE CONTROL",
    footer: "bad_presentation_synthesis_memory | usecase label only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, `selected_usecase_label:${selectedUsecaseId}`],
    forbidden: [
      `${pack}/run2_29_presentation_synthesis_memory.json`,
      `${pack}/run2_28_evidence_chain_view_model.json`,
      `${pack}/run2_24_single_usecase_content_memory.json`,
      `${pack}/run2_24_visual_evidence_asset_memory.json`,
      `${pack}/run2_24_content_visual_workflow_gates.json`,
      `${pack}/results/run2_28_evidence_chain_rerun_result.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "manual Run 2.29 pack repair before scoring",
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

function registerRun229Module(metrics, functionName) {
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

function drawRun229LaunchField(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun229Module(metrics, "drawRun229LaunchField");
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

function drawRun229SelectedRouteMap(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun229Module(metrics, "drawRun229SelectedRouteMap");
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

function run229ContentEvidenceSurfaceGeometry({ x, y, w, h }) {
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

function drawRun229ContentEvidenceSurface(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun229Module(metrics, "drawRun229ContentEvidenceSurface");
  const x = opts.x ?? 96;
  const y = opts.y ?? 126;
  const w = opts.w ?? 870;
  const h = opts.h ?? 368;
  const geom = run229ContentEvidenceSurfaceGeometry({ x, y, w, h });
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

function run229EvidenceChainSurfaceGeometry({ x, y, w, h }) {
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

function drawRun229EvidenceChainSurface(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun229Module(metrics, "drawRun229EvidenceChainSurface");
  const x = opts.x ?? 70;
  const y = opts.y ?? 112;
  const w = opts.w ?? 1068;
  const h = opts.h ?? 424;
  const geom = run229EvidenceChainSurfaceGeometry({ x, y, w, h });
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

function drawRun229WorkflowTracePanel(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun229Module(metrics, "drawRun229WorkflowTracePanel");
  drawRun229EvidenceChainSurface(slide, arm, spec, selection, metrics, {
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

function drawRun229ClimaxEvidenceObject(slide, arm, spec, selection, metrics) {
  registerRun229Module(metrics, "drawRun229ClimaxEvidenceObject");
  drawRun229ClimaxProofObject(slide, arm, spec, selection, metrics);
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

function drawRun229ClimaxProofObject(slide, arm, spec, selection, metrics) {
  registerRun229Module(metrics, "drawRun229ClimaxProofObject");
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

function run229SpineDetail(selection, step) {
  if (step === "source evidence") return compactText(selection.chain.source_evidence_summary, 74);
  if (step === "extracted design rule") return compactText(selection.chain.extracted_design_rule, 74);
  if (step === "workflow decision") return compactText(selection.chain.workflow_decision, 74);
  return compactText(selection.chain.generated_slide_surface, 74);
}

function drawRun229CompressedEvidenceSpine(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun229Module(metrics, "drawRun229CompressedEvidenceSpine");
  const x = opts.x ?? 922;
  const y = opts.y ?? 124;
  const w = opts.w ?? 246;
  const h = opts.h ?? 394;
  rect(slide, x, y, w, h, opts.dark ? "#121922" : C.white, colorLine(opts.dark ? "#374654" : "#cfd8dc", 1));
  text(slide, "compressed evidence spine", x + 18, y + 18, w - 36, 16, {
    fontSize: 8.5,
    mono: true,
    bold: true,
    color: opts.dark ? arm.palette.accent2 : arm.palette.accent,
  });
  text(slide, "manifest_and_html_viewer_full_chain_visible", x + 18, y + 40, w - 36, 12, {
    fontSize: 6.6,
    mono: true,
    color: opts.dark ? "#b9c9d2" : arm.palette.muted,
  });
  const steps = selection.synthesis.visible_on_slide_evidence_spine_steps ?? [
    "source evidence",
    "extracted design rule",
    "workflow decision",
    "generated slide surface",
  ];
  const rowH = Math.max(54, (h - 82) / steps.length);
  steps.forEach((step, index) => {
    const rowY = y + 70 + index * rowH;
    const markerFill = index === 0 ? arm.palette.proof ?? C.signal : index === steps.length - 1 ? arm.palette.accent2 : opts.dark ? "#2a3642" : "#eef3f4";
    rect(slide, x + 18, rowY + 4, 18, 18, markerFill, colorLine(markerFill, 1));
    if (index < steps.length - 1) rect(slide, x + 26, rowY + 24, 2, rowH - 18, opts.dark ? "#596877" : "#d7e0e3");
    text(slide, step, x + 48, rowY, w - 66, 12, {
      fontSize: 7.6,
      mono: true,
      bold: true,
      color: opts.dark ? "#dce8ee" : arm.palette.title,
    });
    text(slide, run229SpineDetail(selection, step), x + 48, rowY + 20, w - 66, 25, {
      fontSize: 6.8,
      color: opts.dark ? "#bac8d0" : arm.palette.muted,
    });
    registerText(metrics, `${step} ${run229SpineDetail(selection, step)}`);
  });
  registerWorkflow(metrics, 4);
  registerVisualEvidence(metrics, 1);
}

function drawRun229EditorialLaunchFrame(slide, arm, spec, selection, metrics) {
  registerRun229Module(metrics, "drawRun229EditorialLaunchFrame");
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
  drawRun229CompressedEvidenceSpine(slide, arm, spec, selection, metrics, { x: 898, y: 118, w: 264, h: 438 });
  registerProof(metrics, 2);
  registerZones(metrics, 3);
  registerHero(metrics, stage.x, stage.y, stage.w, stage.h);
}

function drawRun229AsymmetricProblemFrame(slide, arm, spec, selection, metrics) {
  registerRun229Module(metrics, "drawRun229AsymmetricProblemFrame");
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
  drawRun229CompressedEvidenceSpine(slide, arm, spec, selection, metrics, { x: 900, y: 124, w: 262, h: 420 });
  registerText(metrics, "prompt-only path selected product route generic surface");
  registerProof(metrics, 3);
  registerContentCards(metrics, 3);
  registerHero(metrics, route.x, route.y, route.w, route.h);
}

function drawRun229BeforeAfterEditorialSpread(slide, arm, spec, selection, metrics) {
  registerRun229Module(metrics, "drawRun229BeforeAfterEditorialSpread");
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
  drawRun229CompressedEvidenceSpine(slide, arm, spec, selection, metrics, { x: 900, y: 124, w: 262, h: 420 });
  registerText(metrics, "before prompt-only after evidence-selected");
  registerProof(metrics, 2);
  registerZones(metrics, 3);
  registerHero(metrics, after.x, after.y, after.w, after.h);
}

function drawRun229ProductProofTheater(slide, arm, spec, selection, metrics) {
  registerRun229Module(metrics, "drawRun229ProductProofTheater");
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
  drawRun229CompressedEvidenceSpine(slide, arm, spec, selection, metrics, { x: 900, y: 124, w: 262, h: 420 });
  registerProof(metrics, 3);
  registerContentCards(metrics, 3);
  registerVisualEvidence(metrics, selection.assets.length);
  registerHero(metrics, stage.x, stage.y, stage.w, stage.h);
}

function drawRun229HeroProofScene(slide, arm, spec, selection, metrics) {
  registerRun229Module(metrics, "drawRun229HeroProofScene");
  drawRun229ClimaxProofObject(slide, arm, spec, selection, metrics);
  drawRun229CompressedEvidenceSpine(slide, arm, spec, selection, metrics, { x: 840, y: 154, w: 244, h: 246, dark: true });
}

function drawRun229DecisionHandoff(slide, arm, spec, selection, metrics) {
  registerRun229Module(metrics, "drawRun229DecisionHandoff");
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
  drawRun229CompressedEvidenceSpine(slide, arm, spec, selection, metrics, { x: 900, y: 124, w: 262, h: 420 });
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

function assertRun229ArmInputBoundaries(arm) {
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

  if (arm.armId === "run2_29_full_presentation_synthesis") {
    for (const input of RUN2_29_DATA_INPUTS) assertAllowed(input);
    return;
  }
  for (const input of RUN2_29_DATA_INPUTS) assertForbidden(input);
}

function readRun229PackJsonForArm(arm, relPath) {
  assertRun229ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (arm.armId !== "run2_29_full_presentation_synthesis") {
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

function validateRun228PriorRerunResult(result) {
  if (result?.status !== "run2_28_evidence_chain_rerun_public_blocked") {
    throw new Error("Run 2.29 prior rerun result must be Run 2.28 public-blocked evidence-chain rerun");
  }
  if (result.run_id !== "2.28" || result.rerun?.best_internal_arm !== "run2_28_full_evidence_chain") {
    throw new Error("Run 2.29 prior rerun result source mismatch");
  }
}

function validateRun229EvidenceChainViewModel(model, contentMemory, workflowGates) {
  if (model?.status !== "run2_28_evidence_chain_view_model_ready_public_blocked") {
    throw new Error("Run 2.29 source evidence chain must be the Run 2.28 evidence-chain view model");
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

function validateRun229PresentationSynthesisMemory(memory, evidenceChain) {
  if (memory?.status !== "run2_29_presentation_synthesis_memory_ready_public_blocked") {
    throw new Error("Run 2.29 presentation synthesis memory status mismatch");
  }
  if (memory.selected_usecase_id !== selectedUsecaseId || memory.stage_policy !== "repeat_same_five_layers_not_run3") {
    throw new Error("Run 2.29 presentation synthesis usecase/stage mismatch");
  }
  if (memory.source_evidence_chain_layer !== "run2_28_evidence_chain_view_model.json") {
    throw new Error("Run 2.29 presentation synthesis must bind Run 2.28 evidence chain");
  }
  if (memory.surface_policy?.primary_reader_experience !== "presentation_first_surface") {
    throw new Error("Run 2.29 must render a presentation-first surface");
  }
  if (memory.surface_policy?.secondary_reviewer_experience !== "compressed_evidence_spine") {
    throw new Error("Run 2.29 must keep a compressed evidence spine");
  }
  if (memory.surface_policy?.forbidden_primary_surface !== "four_column_audit_table") {
    throw new Error("Run 2.29 must forbid four-column audit table as primary surface");
  }
  const chainsByRole = new Map((evidenceChain.slide_evidence_chains ?? []).map((chain) => [chain.role, chain]));
  const roles = ["cover", "setup", "contrast", "proof", "climax", "close"];
  const records = memory.slide_synthesis_records ?? [];
  if (records.length !== roles.length || records.map((record) => record.role).join(",") !== roles.join(",")) {
    throw new Error("Run 2.29 presentation synthesis must contain the six canonical slide roles in order");
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
      throw new Error(`Run 2.29 synthesis/evidence-chain mismatch for ${record.role}`);
    }
    if (record.source_native_surface_module_id !== chain.native_surface_module_id) {
      throw new Error(`Run 2.29 synthesis source module mismatch for ${record.role}`);
    }
    if (!String(record.presentation_module_id ?? "").startsWith("drawRun229")) {
      throw new Error(`Run 2.29 synthesis missing presentation module for ${record.role}`);
    }
    if (record.trace_surface_mode !== "manifest_and_html_viewer_full_chain_visible") {
      throw new Error(`Run 2.29 synthesis trace surface mode mismatch for ${record.role}`);
    }
    if (JSON.stringify(record.visible_on_slide_evidence_spine_steps ?? []) !== JSON.stringify(chainOrder)) {
      throw new Error(`Run 2.29 synthesis chain order mismatch for ${record.role}`);
    }
    for (const policy of [
      "do_not_render_four_column_audit_table_as_primary_surface",
      "make_evidence_chain_secondary_to_editorial_claim_and_proof_object",
      "preserve_full_chain_in_trace_manifest_and_html_viewer",
    ]) {
      if (!(record.chain_compression_policy ?? []).includes(policy)) {
        throw new Error(`Run 2.29 synthesis missing policy ${policy} for ${record.role}`);
      }
    }
    for (const field of requiredTraceFields) {
      if (!(record.preserved_trace_fields ?? []).includes(field)) {
        throw new Error(`Run 2.29 synthesis missing preserved trace field ${field} for ${record.role}`);
      }
    }
  }
}

function run229RequiredModulesByRole(presentationSynthesis) {
  return new Map(
    (presentationSynthesis.slide_synthesis_records ?? []).map((record) => [
      record.role,
      [record.presentation_module_id, "drawRun229CompressedEvidenceSpine"],
    ]),
  );
}

function loadRun229ContractData(arm) {
  const presentationSynthesis = readRun229PackJsonForArm(arm, RUN2_29_INPUTS.presentationSynthesis);
  const evidenceChain = readRun229PackJsonForArm(arm, RUN2_29_INPUTS.evidenceChain);
  const contentMemory = readRun229PackJsonForArm(arm, RUN2_29_INPUTS.contentMemory);
  const visualAssets = readRun229PackJsonForArm(arm, RUN2_29_INPUTS.visualAssets);
  const workflowGates = readRun229PackJsonForArm(arm, RUN2_29_INPUTS.workflowGates);
  const priorRerun = readRun229PackJsonForArm(arm, RUN2_29_INPUTS.priorRerun);
  validateRun224SingleUsecaseSchemas(contentMemory, visualAssets, workflowGates);
  validateRun228PriorRerunResult(priorRerun);
  validateRun229EvidenceChainViewModel(evidenceChain, contentMemory, workflowGates);
  validateRun229PresentationSynthesisMemory(presentationSynthesis, evidenceChain);
  return {
    presentationSynthesis,
    evidenceChain,
    contentMemory,
    visualAssets,
    workflowGates,
    priorRerun,
    requiredModulesByRole: run229RequiredModulesByRole(presentationSynthesis),
    status: "run2_29_presentation_synthesis_contract_ready",
  };
}

function selectRun229ForSlide(role, contractData) {
  const content = (contractData.contentMemory?.slide_content_memory ?? []).find((item) => item.role === role);
  const gate = (contractData.workflowGates?.gates ?? []).find((item) => item.role === role);
  const chain = (contractData.evidenceChain?.slide_evidence_chains ?? []).find((item) => item.role === role);
  const synthesis = (contractData.presentationSynthesis?.slide_synthesis_records ?? []).find((item) => item.role === role);
  if (!content || !gate) throw new Error(`Run 2.24 pack missing role ${role}`);
  if (!chain) throw new Error(`Run 2.28 evidence chain missing role ${role}`);
  if (!synthesis) throw new Error(`Run 2.29 presentation synthesis missing role ${role}`);
  if (gate.required_content_memory_id !== content.content_memory_id) throw new Error(`Run 2.24 gate/content mismatch for ${role}`);
  if (chain.content_memory_id !== content.content_memory_id || chain.workflow_gate_id !== gate.gate_id) {
    throw new Error(`Run 2.28 chain/content/gate mismatch for ${role}`);
  }
  if (synthesis.evidence_chain_id !== chain.evidence_chain_id) {
    throw new Error(`Run 2.29 synthesis/evidence-chain mismatch for ${role}`);
  }
  const assets = (contractData.visualAssets?.visual_evidence_assets ?? []).filter((asset) =>
    content.visual_evidence_slot_ids.includes(asset.slot_id),
  );
  if (assets.length < 2) throw new Error(`Run 2.24 visual evidence missing role ${role}`);
  return { content, assets, gate, chain, synthesis };
}

function renderRun229FullSlide(presentation, spec, arm, n, fullData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const selection = selectRun229ForSlide(spec.role, fullData);

  const modules = {
    drawRun229EditorialLaunchFrame,
    drawRun229AsymmetricProblemFrame,
    drawRun229BeforeAfterEditorialSpread,
    drawRun229ProductProofTheater,
    drawRun229HeroProofScene,
    drawRun229DecisionHandoff,
  };
  const renderModule = modules[selection.synthesis.presentation_module_id];
  if (!renderModule) throw new Error(`Run 2.29 missing presentation module ${selection.synthesis.presentation_module_id}`);
  renderModule(slide, arm, spec, selection, metrics);

  proofFooter(slide, arm, selection);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function renderControlSlide(presentation, spec, arm, n, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const mode = arm.armId === "bad_presentation_synthesis_memory" ? "bad" : arm.armId === "run1_5_skill" ? "run1_5" : "prompt";
  drawControlSlideContent(slide, arm, spec, metrics, mode);
  drawControlGate(slide, arm, spec, metrics, {
    x: spec.role === "climax" ? 1022 : 904,
    y: spec.role === "close" ? 326 : spec.role === "climax" ? 492 : 438,
    w: spec.role === "close" ? 226 : spec.role === "climax" ? 178 : 210,
    h: spec.role === "climax" ? 92 : 118,
    headline: arm.armId === "bad_presentation_synthesis_memory" ? "pack missing" : "public blocked",
    line: arm.armId === "bad_presentation_synthesis_memory" ? "label only / no 2.29 synthesis" : "no Run 2.29 trace",
  });
  proofFooter(slide, arm, null);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertRun229ArmInputBoundaries(arm);
  const fullRun229 = arm.armId === "run2_29_full_presentation_synthesis";
  const fullData = fullRun229 ? context.fullData ?? loadRun229ContractData(arm) : null;
  const requiredModulesByRole = fullData?.requiredModulesByRole ?? new Map();
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = fullRun229 && arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun229 ? selectedUsecaseId : "",
    prior_rerun_run_id: fullRun229 ? fullData.priorRerun.run_id : "",
    prior_rerun_status: fullRun229 ? fullData.priorRerun.status : "",
    evidence_chain_status: fullRun229 ? fullData.evidenceChain.status : "",
    presentation_synthesis_status: fullRun229 ? fullData.presentationSynthesis.status : "",
    commercial_case: `${pack}/commercial_case.md`,
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.29 presentation-synthesis arm-specific generation from scripts/generate_ppt_run2_29_presentation_synthesis_arms.mjs",
      no_cross_arm_reuse: [
        "cached memory summaries",
        "generated slide code",
        "layout JSON",
        "screenshots",
        "contact sheets",
        "QA notes",
        "Run 2.24 trace carryover",
        "Run 2.28 evidence chain in control arms",
        "Run 2.29 presentation synthesis in control arms",
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
      const selection = fullRun229 ? selectRun229ForSlide(slide.role, fullData) : null;
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_29_contract_status: fullRun229
          ? hasRenderedMetrics
            ? "full_arm_native_generator_rendered"
            : "full_arm_contract_preview_not_rendered"
          : "boundary_control_not_run2_29_full",
        run2_24_selected_usecase_id: fullRun229 ? selection.content.selected_usecase_id : "",
        run2_24_content_memory_id: fullRun229 ? selection.content.content_memory_id : "",
        run2_24_visual_evidence_slot_ids: fullRun229 ? selection.content.visual_evidence_slot_ids : [],
        run2_24_content_density_gate_id: fullRun229 ? selection.gate.gate_id : "",
        run2_24_business_proof_points_visible: fullRun229 ? selection.content.business_proof_points.slice(0, 3) : [],
        run2_24_visual_evidence_asset_ids: fullRun229 ? selection.assets.map((asset) => asset.asset_id) : [],
        run2_24_public_surface_policy: fullRun229 ? selection.content.public_surface_policy : "",
        run2_28_evidence_chain_id: fullRun229 ? selection.chain.evidence_chain_id : "",
        run2_28_multimodal_source_record_ids: fullRun229 ? selection.chain.multimodal_source_record_ids : [],
        run2_28_extracted_design_rule: fullRun229 ? selection.chain.extracted_design_rule : "",
        run2_28_workflow_decision: fullRun229 ? selection.chain.workflow_decision : "",
        run2_28_native_surface_module_id: fullRun229 ? selection.chain.native_surface_module_id : "",
        run2_29_synthesis_record_id: fullRun229 ? selection.synthesis.synthesis_record_id : "",
        run2_29_public_surface_mode: fullRun229 ? selection.synthesis.public_surface_mode : "",
        run2_29_trace_surface_mode: fullRun229 ? selection.synthesis.trace_surface_mode : "",
        run2_29_presentation_module_id: fullRun229 ? selection.synthesis.presentation_module_id : "",
        run2_29_chain_compression_policy: fullRun229 ? selection.synthesis.chain_compression_policy : [],
        run2_29_presentation_synthesis_execution_status: fullRun229
          ? "presentation_first_surface_rendered_with_secondary_evidence_spine"
          : "",
        run2_29_required_code_module_ids: fullRun229 ? requiredModulesByRole.get(slide.role) ?? [] : [],
        run2_29_code_module_ids: fullRun229
          ? hasRenderedMetrics
            ? actualCodeModuleIds
            : requiredModulesByRole.get(slide.role) ?? []
          : [],
        run2_29_bad_control_probe: fullRun229
          ? "bad_presentation_synthesis_memory may receive the selected usecase label but forbids Run 2.29 presentation synthesis, Run 2.28 evidence chain, Run 2.24 content memory, visual evidence assets, workflow gates, and Run 2.28 prior rerun result"
          : "boundary_control",
        negative_control_usecase_id: arm.armId === "bad_presentation_synthesis_memory" ? selectedUsecaseId : "",
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

function assertRun229ContentVisualGateSelfCheck(trace) {
  if (trace.arm_id !== "run2_29_full_presentation_synthesis") return;
  if (trace.selected_usecase_id !== selectedUsecaseId) throw new Error("Run 2.29 full trace did not lock the selected usecase");
  for (const slide of trace.slides) {
    if (slide.run2_29_contract_status !== "full_arm_native_generator_rendered") {
      throw new Error(`Run 2.29 full slide ${slide.slide_id} was not rendered with native module metrics`);
    }
    for (const field of EXPECTED_RUN2_29_TRACE_FIELDS) {
      const value = slide[field];
      const empty =
        value == null ||
        (Array.isArray(value) && value.length === 0) ||
        (typeof value === "string" && value.trim() === "") ||
        (typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === 0);
      if (empty) throw new Error(`Run 2.29 full slide ${slide.slide_id} missing ${field}`);
    }
    if ((slide.run2_24_visual_evidence_slot_ids ?? []).length < 2) {
      throw new Error(`Run 2.29 full slide ${slide.slide_id} missing at least two visual evidence slots`);
    }
    const actualCodeModules = new Set(slide.run2_29_code_module_ids ?? []);
    for (const requiredCodeModule of slide.run2_29_required_code_module_ids ?? []) {
      if (!actualCodeModules.has(requiredCodeModule)) {
        throw new Error(`Run 2.29 full slide ${slide.slide_id} did not call required module ${requiredCodeModule}`);
      }
    }
    if (!actualCodeModules.has(slide.run2_29_presentation_module_id)) {
      throw new Error(`Run 2.29 full slide ${slide.slide_id} did not call presentation synthesis module ${slide.run2_29_presentation_module_id}`);
    }
    if (!actualCodeModules.has("drawRun229CompressedEvidenceSpine")) {
      throw new Error(`Run 2.29 full slide ${slide.slide_id} did not call compressed evidence spine`);
    }
    if (slide.run2_29_presentation_synthesis_execution_status !== "presentation_first_surface_rendered_with_secondary_evidence_spine") {
      throw new Error(`Run 2.29 full slide ${slide.slide_id} missing presentation-first execution status`);
    }
    if (!(slide.run2_29_chain_compression_policy ?? []).includes("do_not_render_four_column_audit_table_as_primary_surface")) {
      throw new Error(`Run 2.29 full slide ${slide.slide_id} missing audit-table compression policy`);
    }
    if ((slide.layout_metrics?.workflow_objects ?? 0) < 4) {
      throw new Error(`Run 2.29 full slide ${slide.slide_id} does not expose the four-step workflow chain`);
    }
    if (slide.run2_24_selected_usecase_id !== selectedUsecaseId) {
      throw new Error(`Run 2.29 full slide ${slide.slide_id} selected the wrong usecase`);
    }
    if (slide.role === "climax" && !(slide.layout_metrics?.hero_object_canvas_share > 0.5)) {
      throw new Error("Run 2.29 climax missing large proof object stage");
    }
  }
}

function buildArmContract() {
  return armSpecs.map((arm) => ({
    armId: arm.armId,
    label: arm.label,
    contract_status:
      arm.armId === "run2_29_full_presentation_synthesis"
        ? "run2_29_presentation_synthesis_contract_ready_requires_render_metrics"
        : "run2_29_boundary_control_contract_ready",
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

function buildRun229FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-29-four-arm-contact-sheet.png"),
    "Run 2.29 four-arm comparison",
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
    "ppt-run2-29-full-vulca",
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
      "required proof objects: presentation-first surface, compressed evidence spine, editable product proof object, release gate",
      "source requirements: commercial case always; full arm requires Run 2.29 presentation synthesis, Run 2.28 evidence chain, Run 2.24 content memory, visual assets, workflow gates, and Run 2.28 prior rerun result before native PPT generation; bad control receives usecase label only",
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
  if (arm.armId === "run2_29_full_presentation_synthesis") {
    fullData = loadRun229ContractData(arm);
  }

  const slides = arm.slides.map((slide, index) =>
    arm.armId === "run2_29_full_presentation_synthesis"
      ? renderRun229FullSlide(presentation, slide, arm, index + 1, fullData, metricsByRole)
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
  assertRun229ContentVisualGateSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_29_presentation_synthesis_arms.mjs",
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

function writeRun229Result(runSummary) {
  const result = {
    schema_version: 1,
    run_id: "2.29",
    status: "run2_29_presentation_synthesis_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      presentation_synthesis_memory: RUN2_29_INPUTS.presentationSynthesis,
      evidence_chain_view_model: RUN2_29_INPUTS.evidenceChain,
      content_memory: RUN2_29_INPUTS.contentMemory,
      visual_evidence_asset_memory: RUN2_29_INPUTS.visualAssets,
      content_visual_workflow_gates: RUN2_29_INPUTS.workflowGates,
      prior_rerun_result: RUN2_29_INPUTS.priorRerun,
      source_data_layer: RUN2_29_INPUTS.presentationSynthesis,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_29_presentation_synthesis_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_29_full_presentation_synthesis",
      best_internal_arm_verdict: "presentation_first_surface_rendered_with_secondary_evidence_spine",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    presentation_synthesis_delta: {
      source_model: RUN2_29_INPUTS.presentationSynthesis,
      source_evidence_chain: RUN2_29_INPUTS.evidenceChain,
      prior_rerun_result: RUN2_29_INPUTS.priorRerun,
      chain_order: ["source evidence", "extracted design rule", "workflow decision", "generated slide surface"],
      replacement_focus: "compress_the_run2_28_four_column_audit_table_into_a_secondary_evidence_spine",
      primary_surface_mode: "presentation-first surface",
      secondary_surface_mode: "compressed evidence spine",
      forbidden_primary_surface: "four-column audit table",
      required_visible_chain_steps_per_full_slide: 4,
    },
    visual_quality_boundary:
      "presentation_synthesis_proof_only_not_public_video_grade_aesthetic_or_human_release_approval",
    control_boundary: {
      bad_presentation_synthesis_memory: "selected_usecase_label_only_without_run2_29_presentation_synthesis_run2_28_evidence_chain_run2_24_content_memory_visual_assets_workflow_gates_or_run2_28_prior_rerun_result",
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
    trace_manifest_requirements: EXPECTED_RUN2_29_TRACE_FIELDS,
    native_module_status: "actual_run2_29_presentation_module_calls_recorded_in_trace_manifest",
    release_boundary: "public_blocked_until_visual_human_review_native_render_review_motion_review_source_boundary_review_and_human_approval",
    next_required_action: "review_run2_29_outputs_for_presentation_first_surface_and_secondary_evidence_spine_then_continue_thickening_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_29_presentation_synthesis_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_29_presentation_synthesis_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.29 Presentation Synthesis Rerun Result",
      "",
      "Status: rerun completed, public blocked.",
      "",
      "Run 2.29 is the generated four-arm rerun that consumes Run 2.29 presentation synthesis memory, Run 2.28 evidence-chain data, Run 2.24 single-usecase content memory, visual evidence asset memory, content/visual workflow gates, and the Run 2.28 rerun result before native PPT code generation. It repeats the same five layers and does not advance to Run 3.0.",
      "",
      "The generator is `scripts/generate_ppt_run2_29_presentation_synthesis_arms.mjs`.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_29_full_presentation_synthesis`",
      "- `bad_presentation_synthesis_memory`",
      "",
      "The negative control `bad_presentation_synthesis_memory` may receive the selected usecase label, but it is blocked from reading Run 2.29 presentation synthesis memory, Run 2.28 evidence chain data, Run 2.24 content memory, visual evidence assets, workflow gates, and the Run 2.28 rerun result.",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_29_full_presentation_synthesis`.",
      "",
      "Verdict: `presentation_first_surface_rendered_with_secondary_evidence_spine`.",
      "",
      "Presentation-synthesis delta: every full-arm slide now renders a presentation-first surface with a secondary compressed evidence spine, while the full `source evidence`, `extracted design rule`, `workflow decision`, and `generated slide surface` chain remains traceable in the manifest and HTML viewer.",
      "",
      "Public release remains blocked. This proves presentation-synthesis execution, not final public-video-grade visual quality or high-aesthetic human approval.",
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
  const fourArmSheet = buildRun229FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_29_presentation_synthesis_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_29_presentation_synthesis_rerun_summary.json"), runSummary);
  writeRun229Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  EXPECTED_RUN2_29_TRACE_FIELDS,
  RUN2_29_INPUTS,
  RUN2_29_DATA_INPUTS,
  armSpecs,
  assertRun229ArmInputBoundaries,
  assertRun229ContentVisualGateSelfCheck,
  buildArmContract,
  drawRun229LaunchField,
  drawRun229SelectedRouteMap,
  drawRun229ContentEvidenceSurface,
  drawRun229CompressedEvidenceSpine,
  drawRun229EditorialLaunchFrame,
  drawRun229AsymmetricProblemFrame,
  drawRun229BeforeAfterEditorialSpread,
  drawRun229ProductProofTheater,
  drawRun229HeroProofScene,
  drawRun229DecisionHandoff,
  drawRun229EvidenceChainSurface,
  drawRun229WorkflowTracePanel,
  drawRun229ClimaxEvidenceObject,
  drawRun229ClimaxProofObject,
  loadRun229ContractData,
  main,
  readRun229PackJsonForArm,
  registerRun229Module,
  run229RequiredModulesByRole,
  run229ContentEvidenceSurfaceGeometry,
  run229EvidenceChainSurfaceGeometry,
  selectRun229ForSlide,
  traceFor,
  validateRun224SingleUsecaseSchemas,
  validateRun228PriorRerunResult,
  validateRun229EvidenceChainViewModel,
  validateRun229PresentationSynthesisMemory,
};
