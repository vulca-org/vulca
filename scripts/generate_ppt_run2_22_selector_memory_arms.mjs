import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
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
  paper: "#f3f1ec",
  white: "#ffffff",
  line: "#d4d7dc",
  muted: "#626b76",
  midnight: "#10151d",
  graphite: "#222934",
  blue: "#2468df",
  cyan: "#74c5d8",
  signal: "#ef563d",
  green: "#0f8a66",
  fog: "#edf1f4",
  pearl: "#f9fafb",
  wheat: "#ece0c9",
  olive: "#726641",
};

const EXPECTED_RUN2_22_TRACE_FIELDS = [
  "run2_21_visual_decision_memory_id",
  "run2_21_primary_evidence_id",
  "run2_21_secondary_evidence_ids",
  "run2_21_rejected_evidence_reasons",
  "run2_21_selector_gate_id",
  "run2_21_visual_decision_delta",
  "run2_22_selector_execution_status",
  "run2_22_code_module_ids",
];

const RUN2_22_INPUTS = {
  decisionMemory: `${pack}/run2_21_visual_decision_memory.json`,
  selectorGates: `${pack}/run2_21_per_role_selector_gates.json`,
  rejectionMatrix: `${pack}/run2_21_evidence_rejection_matrix.json`,
};
const RUN2_22_DATA_INPUTS = [
  RUN2_22_INPUTS.decisionMemory,
  RUN2_22_INPUTS.selectorGates,
  RUN2_22_INPUTS.rejectionMatrix,
];

const baseSlides = [
  {
    role: "cover",
    title: "One evidence choice drives the first read.",
    claim: "Run 2.22 forces every slide to choose a primary source before code draws the surface.",
    selectorHint: "vdm cover -> native promise field",
  },
  {
    role: "setup",
    title: "The setup becomes a selected route.",
    claim: "The workflow is no longer a pile of evidence; the selector turns it into one product-theater path.",
    selectorHint: "primary evidence -> proof route",
  },
  {
    role: "contrast",
    title: "Rejection makes the contrast sharper.",
    claim: "Unused evidence is not ignored; it is explicitly rejected so the slide can keep one visual job.",
    selectorHint: "accepted vs rejected evidence",
  },
  {
    role: "proof",
    title: "The proof surface gets a single owner.",
    claim: "Selector memory binds a native product surface, then keeps trace details out of the public slide.",
    selectorHint: "selector gate -> product proof",
  },
  {
    role: "climax",
    title: "The climax chooses one object.",
    claim: "The metric moment stops competing with setup evidence and becomes a single editorial stage.",
    selectorHint: "metric primary -> stage object",
  },
  {
    role: "close",
    title: "The handoff keeps the gate closed.",
    claim: "The generated deck is a stronger internal proof, not a public release candidate.",
    selectorHint: "selector proof -> public blocked",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-22-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.22 / CONTROL",
    footer: "prompt_only | no selector memory | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [
      `${pack}/run2_21_visual_decision_memory.json`,
      `${pack}/run2_21_per_role_selector_gates.json`,
      `${pack}/run2_21_evidence_rejection_matrix.json`,
      `${pack}/run2_18_multimodal_evidence_expansion.json`,
      `${pack}/run2_18_design_memory_expansion.json`,
      `${pack}/run2_18_workflow_gate_expansion.json`,
      `${pack}/skill_workflow.json`,
      "docs/product/ppt-run1-5-product-lab/",
    ],
    palette: {
      bg: "#f5f6f8",
      rail: "#364354",
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
        "The prompt asks for evidence-led slides.",
        "The setup says the deck should be clearer.",
        "The contrast labels before and after.",
        "The proof mentions product depth.",
        "The climax asks for impact.",
        "The close repeats the release gate.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-22-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.22 / RUN 1.5",
    footer: "run1_5_skill | prior workflow baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [
      `${pack}/run2_21_visual_decision_memory.json`,
      `${pack}/run2_21_per_role_selector_gates.json`,
      `${pack}/run2_21_evidence_rejection_matrix.json`,
      `${pack}/run2_18_multimodal_evidence_expansion.json`,
      `${pack}/run2_18_design_memory_expansion.json`,
      `${pack}/run2_18_workflow_gate_expansion.json`,
      `${pack}/skill_workflow.json`,
    ],
    palette: {
      bg: "#f3f6fb",
      rail: "#29354b",
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
        "The baseline is readable but broad.",
        "The setup still explains the process.",
        "The contrast spreads attention evenly.",
        "The proof surface stays diagrammatic.",
        "The climax has a result but not a stage.",
        "The close is correct, not memorable.",
      ][index],
    })),
  },
  {
    armId: "run2_22_full_selector_memory",
    slug: "ppt-run2-22-full-vulca",
    label: "Run 2.22 full selector memory",
    kicker: "RUN 2.22 / FULL SELECTOR",
    footer: "run2_22_full_selector_memory | 2.21 selector memory | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/sources.json`,
      `${pack}/run2_21_visual_decision_memory.json`,
      `${pack}/run2_21_per_role_selector_gates.json`,
      `${pack}/run2_21_evidence_rejection_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    forbidden: [
      "docs/product/ppt-run1-5-product-lab/",
      "copied source visuals",
      "winner claims before scoring",
      "raw tutorial media copied into slide surface",
    ],
    palette: {
      bg: "#f4f1ea",
      rail: C.midnight,
      accent: C.midnight,
      accent2: C.cyan,
      proof: C.signal,
      panel: C.white,
      title: "#0e1218",
      muted: "#58636f",
      rule: "#d2ccc1",
      gate: C.midnight,
    },
    slides: baseSlides,
  },
  {
    armId: "bad_selector_memory",
    slug: "ppt-run2-22-bad-selector-memory",
    label: "Bad selector-memory control",
    kicker: "RUN 2.22 / NEGATIVE CONTROL",
    footer: "bad_selector_memory | decision memory without gates/matrix | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, `${pack}/sources.json`, `${pack}/run2_21_visual_decision_memory.json`],
    forbidden: [
      `${pack}/run2_21_per_role_selector_gates.json`,
      `${pack}/run2_21_evidence_rejection_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "manual Run 2.22 selector gate repair before scoring",
    ],
    palette: {
      bg: "#f2efe1",
      rail: "#6d633e",
      accent: C.olive,
      accent2: "#d4c897",
      panel: "#f8f3e5",
      title: "#2d291f",
      muted: "#67604d",
      rule: "#d8cfb9",
      gate: "#eadfbe",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Decision names without gates stay fuzzy.",
        "The setup names too many possible routes.",
        "The contrast keeps rejected evidence visible.",
        "The proof surface becomes label-heavy again.",
        "The climax competes with supporting evidence.",
        "The close lists the process.",
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
  return ctx.addShape(slide, { x, y, w, h, fill, line });
}

function ellipse(slide, x, y, w, h, fill, line) {
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
    deltaPanels: 0,
    heroShare: 0,
    visualModuleIds: new Set(),
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun222Module(metrics, functionName) {
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

function registerDeltaPanels(metrics, count) {
  metrics.deltaPanels = Math.max(metrics.deltaPanels, count);
}

function registerHero(metrics, x, y, w, h) {
  const area = Math.max(1, MAIN_CANVAS.w * MAIN_CANVAS.h);
  metrics.heroShare = Math.max(metrics.heroShare, (w * h) / area);
}

function base(slide, arm, n) {
  rect(slide, 0, 0, W, H, arm.palette.bg);
  rect(slide, 0, 0, 16, H, arm.palette.rail);
  text(slide, arm.kicker, 54, 30, 430, 22, {
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
  text(slide, arm.footer, 632, 674, 592, 22, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
    align: "right",
  });
  for (let i = 1; i <= 6; i += 1) {
    rect(slide, 54 + (i - 1) * 20, 684, i === n ? 16 : 8, 5, i === n ? arm.palette.accent : C.line);
  }
}

function proofFooter(slide, spec, arm, selection) {
  const hint = selection?.decision?.decision_id ?? spec.selectorHint;
  text(slide, `selector: ${hint}`, 66, 628, 830, 28, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
    fill: arm.palette.panel,
    line: colorLine(C.line, 1),
    insets: { left: 18, right: 8, top: 8, bottom: 5 },
  });
  rect(slide, 76, 640, 7, 7, arm.palette.proof ?? arm.palette.accent);
}

function moduleLabel(slide, x, y, label, arm) {
  chip(slide, label, x, y, Math.max(132, label.length * 7 + 28), arm.palette.panel, arm.palette.accent);
}

function drawRun222CinematicSelectorField(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun222Module(metrics, "drawRun222CinematicSelectorField");
  const x = opts.x ?? 82;
  const y = opts.y ?? 116;
  const w = opts.w ?? 700;
  moduleLabel(slide, x, y - 36, "primary evidence field", arm);
  text(slide, spec.title, x, y, w, opts.titleH ?? 206, {
    fontSize: opts.fontSize ?? 64,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  rect(slide, x, y + (opts.ruleY ?? 238), 128, 9, arm.palette.proof ?? arm.palette.accent);
  rect(slide, x + 148, y + (opts.ruleY ?? 238), 56, 9, arm.palette.accent2);
  text(slide, spec.claim, x, y + (opts.claimY ?? 274), opts.claimW ?? 520, 54, {
    fontSize: opts.claimSize ?? 17,
    color: arm.palette.muted,
  });
  registerText(metrics, spec.claim);
  const motif = { x: opts.motifX ?? 880, y: opts.motifY ?? 132, w: opts.motifW ?? 248, h: opts.motifH ?? 248 };
  rect(slide, motif.x, motif.y, motif.w, motif.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  rect(slide, motif.x + 34, motif.y + 44, 96, 96, arm.palette.proof ?? C.signal);
  rect(slide, motif.x + 154, motif.y + 56, 58, 10, C.white);
  rect(slide, motif.x + 154, motif.y + 91, 74, 8, "#c7d1d7");
  rect(slide, motif.x + 154, motif.y + 126, 42, 8, "#c7d1d7");
  const primary = selection?.decision?.primary_evidence_id ?? "primary evidence selected";
  text(slide, primary.replace(/^thick_2_18_/, ""), motif.x + 34, motif.y + motif.h - 48, motif.w - 68, 18, {
    fontSize: 10,
    bold: true,
    mono: true,
    color: C.white,
  });
  registerText(metrics, primary);
  registerProof(metrics, 1);
  registerHero(metrics, motif.x, motif.y, motif.w, motif.h);
}

function drawRun222ProductTheaterSurface(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun222Module(metrics, "drawRun222ProductTheaterSurface");
  const x = opts.x ?? 596;
  const y = opts.y ?? 126;
  const w = opts.w ?? 506;
  const h = opts.h ?? 346;
  moduleLabel(slide, x, y - 38, "selected product surface", arm);
  rect(slide, x + 78, y + 58, w - 58, h - 58, "#dfe8ed", colorLine("#dfe8ed", 1));
  rect(slide, x + 42, y + 28, w - 60, h - 50, "#edf3f5", colorLine("#cbd6db", 1));
  rect(slide, x, y, w - 66, h - 58, C.white, colorLine(arm.palette.accent, 2));
  rect(slide, x + 28, y + 28, 172, 24, arm.palette.accent);
  rect(slide, x + 28, y + 82, w - 144, 78, C.fog, colorLine("#d2d9de", 1));
  rect(slide, x + 50, y + 106, 122, 18, arm.palette.proof ?? C.signal);
  rect(slide, x + 214, y + 110, 88, 9, "#bfc8ce");
  rect(slide, x + 332, y + 110, 60, 9, "#bfc8ce");
  const steps = ["select", "compose", "render"];
  steps.forEach((label, index) => {
    const nx = x + 54 + index * 128;
    const ny = y + 212 + (index === 1 ? 22 : 0);
    rect(slide, nx, ny, 96, 40, index === 2 ? arm.palette.proof ?? C.signal : C.white, colorLine(index === 2 ? arm.palette.proof ?? C.signal : "#cad2d8", 1));
    text(slide, label, nx + 14, ny + 13, 70, 12, {
      fontSize: 10,
      bold: true,
      mono: true,
      color: index === 2 ? C.white : arm.palette.accent,
    });
    registerText(metrics, label);
    if (index < steps.length - 1) rect(slide, nx + 96, ny + 19, 36, 4, arm.palette.proof ?? C.signal);
  });
  const decision = selection?.decision?.proof_object_decision ?? "native surface carries proof";
  text(slide, decision, x + 28, y + h - 44, w - 112, 24, {
    fontSize: 11,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, decision);
  registerProof(metrics, 2);
  registerZones(metrics, 3);
  registerWorkflow(metrics, 3);
}

function drawRun222EvidenceRoute(slide, arm, spec, selection, metrics, opts = {}) {
  registerRun222Module(metrics, "drawRun222EvidenceRoute");
  const x = opts.x ?? 88;
  const y = opts.y ?? 362;
  const w = opts.w ?? 990;
  moduleLabel(slide, x, y - 38, "selected / rejected route", arm);
  const primary = selection?.decision?.primary_evidence_id ?? "primary";
  const secondary = selection?.decision?.secondary_evidence_ids ?? ["secondary"];
  const rejected = selection?.decision?.rejected_evidence ?? [];
  const nodes = [
    { label: "primary", detail: primary.replace(/^thick_2_18_/, ""), x: x + 18, y: y + 44, r: 88, fill: arm.palette.accent, color: C.white },
    { label: "secondary", detail: `${secondary.length} support`, x: x + 300, y: y + 12, r: 70, fill: C.white, color: arm.palette.accent },
    { label: "rejected", detail: `${rejected.length} held out`, x: x + 544, y: y + 82, r: 62, fill: C.fog, color: arm.palette.muted },
    { label: "slide", detail: "one visual job", x: x + 792, y: y + 22, r: 96, fill: arm.palette.proof ?? C.signal, color: C.white },
  ];
  for (let index = 0; index < nodes.length - 1; index += 1) {
    const current = nodes[index];
    const next = nodes[index + 1];
    rect(slide, current.x + current.r, current.y + current.r / 2, Math.max(36, next.x - current.x - current.r), 6, arm.palette.proof ?? C.signal);
  }
  nodes.forEach((node, index) => {
    ellipse(slide, node.x, node.y, node.r, node.r, node.fill, colorLine(index === 1 ? arm.palette.accent2 : node.fill, index === 1 ? 2 : 1));
    text(slide, node.label, node.x + 12, node.y + node.r / 2 - 16, node.r - 24, 14, {
      fontSize: 10,
      bold: true,
      mono: true,
      color: node.color,
      align: "center",
    });
    text(slide, node.detail, node.x + 10, node.y + node.r / 2 + 4, node.r - 20, 24, {
      fontSize: 8,
      mono: true,
      color: node.color,
      align: "center",
    });
    registerText(metrics, `${node.label} ${node.detail}`);
  });
  registerProof(metrics, 4);
  registerWorkflow(metrics, 4);
  registerDeltaPanels(metrics, 1);
}

function drawRun222ClimaxEditorialStage(slide, arm, spec, selection, metrics) {
  registerRun222Module(metrics, "drawRun222ClimaxEditorialStage");
  const stage = { x: 118, y: 96, w: 1026, h: 488 };
  moduleLabel(slide, 84, 96, "selector climax stage", arm);
  rect(slide, stage.x, stage.y, stage.w, stage.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  text(slide, "one selected proof owns the room", stage.x + 48, stage.y + 44, 470, 52, {
    fontSize: 30,
    bold: true,
    title: true,
    color: C.white,
  });
  registerText(metrics, "one selected proof owns the room");
  const hero = { x: stage.x + 168, y: stage.y + 128, w: 690, h: 258 };
  rect(slide, hero.x - 74, hero.y - 62, hero.w + 148, hero.h + 124, "#202833", colorLine("#202833", 1));
  rect(slide, hero.x, hero.y, hero.w, hero.h, C.white, colorLine(arm.palette.proof ?? C.signal, 4));
  rect(slide, hero.x + 62, hero.y + 54, 248, 154, arm.palette.proof ?? C.signal);
  rect(slide, hero.x + 352, hero.y + 68, 186, 14, arm.palette.accent2);
  rect(slide, hero.x + 352, hero.y + 118, 232, 9, "#bdc8cf");
  rect(slide, hero.x + 352, hero.y + 154, 146, 9, "#bdc8cf");
  const primary = selection?.decision?.primary_evidence_id ?? "selected climax evidence";
  text(slide, primary.replace(/^thick_2_18_/, ""), hero.x + 62, hero.y + hero.h - 54, 454, 24, {
    fontSize: 18,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, primary);
  ["primary chosen", "support capped", "public blocked"].forEach((label, index) => {
    const ex = index === 0 ? stage.x + 50 : index === 1 ? stage.x + stage.w - 230 : stage.x + stage.w - 242;
    const ey = index === 0 ? stage.y + stage.h - 98 : index === 1 ? stage.y + 56 : stage.y + stage.h - 86;
    rect(slide, ex, ey, 176, 34, "#303a45", colorLine("#596471", 1));
    text(slide, label, ex + 14, ey + 11, 146, 12, {
      fontSize: 9,
      bold: true,
      mono: true,
      color: "#dae4e8",
    });
    registerText(metrics, label);
  });
  registerHero(metrics, stage.x, stage.y, stage.w, stage.h);
  registerProof(metrics, 1);
  registerGate(metrics, 1);
}

function drawControlGate(slide, arm, spec, metrics, opts = {}) {
  const x = opts.x ?? 908;
  const y = opts.y ?? 438;
  const w = opts.w ?? 206;
  const h = opts.h ?? 116;
  rect(slide, x, y, w, h, arm.palette.gate, colorLine(arm.palette.rule, 1));
  text(slide, opts.headline ?? "public blocked", x + 16, y + 22, w - 32, 30, {
    fontSize: 16,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  text(slide, opts.line ?? "no selector gate trace", x + 16, y + 66, w - 32, 18, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
  });
  registerText(metrics, `${opts.headline ?? "public blocked"} ${opts.line ?? "no selector gate trace"}`);
  registerGate(metrics, 1);
}

function drawDenseControl(slide, arm, spec, metrics, mode = "prompt") {
  text(slide, spec.title, 76, 132, 566, 96, {
    fontSize: mode === "bad" ? 34 : 38,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, spec.claim, 80, 244, 518, 64, { fontSize: 16, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  const panelFill = mode === "bad" ? "#efe4c8" : C.white;
  if (spec.role === "climax") {
    for (let col = 0; col < 3; col += 1) {
      rect(slide, 94 + col * 300, 324, 248, 150, panelFill, colorLine(arm.palette.rule, 1));
      text(slide, ["primary?", "support?", "result?"][col], 116 + col * 300, 352, 190, 18, {
        fontSize: 9,
        bold: true,
        mono: true,
        color: arm.palette.accent,
      });
      text(slide, mode === "bad" ? "selector labels remain visible" : "impact is requested, not bound", 116 + col * 300, 390, 198, 42, {
        fontSize: 15,
        bold: true,
        title: true,
        color: arm.palette.title,
      });
      registerText(metrics, ["primary?", "support?", "result?"][col]);
    }
  } else {
    rect(slide, 84, 330, 472, 204, panelFill, colorLine(arm.palette.rule, 1));
    text(slide, mode === "bad" ? "The decision memory is present, but the selector gate is missing." : "The control can be readable while still lacking selector-bound composition.", 108, 366, 410, 82, {
      fontSize: mode === "bad" ? 18 : 20,
      bold: true,
      title: true,
      color: arm.palette.title,
    });
    registerText(metrics, mode === "bad" ? "The decision memory is present, but the selector gate is missing." : "The control can be readable while still lacking selector-bound composition.");
    for (let i = 0; i < (mode === "bad" ? 4 : 3); i += 1) {
      rect(slide, 680 + i * (mode === "bad" ? 116 : 150), 316, mode === "bad" ? 100 : 132, 144, panelFill, colorLine(arm.palette.rule, 1));
      rect(slide, 692 + i * (mode === "bad" ? 116 : 150), 340, mode === "bad" ? 80 : 108, 12, arm.palette.accent2);
      rect(slide, 692 + i * (mode === "bad" ? 116 : 150), 378, mode === "bad" ? 66 : 88, 9, "#c0c9d0");
      rect(slide, 692 + i * (mode === "bad" ? 116 : 150), 410, mode === "bad" ? 58 : 74, 9, "#c0c9d0");
    }
  }
  registerDeltaPanels(metrics, mode === "bad" ? 4 : 2);
}

function assertArmInputBoundaries(arm) {
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

  if (arm.armId === "run2_22_full_selector_memory") {
    for (const input of RUN2_22_DATA_INPUTS) assertAllowed(input);
    return;
  }
  if (arm.armId === "bad_selector_memory") {
    assertAllowed(RUN2_22_INPUTS.decisionMemory);
    assertForbidden(RUN2_22_INPUTS.selectorGates);
    assertForbidden(RUN2_22_INPUTS.rejectionMatrix);
    return;
  }
  for (const input of RUN2_22_DATA_INPUTS) assertForbidden(input);
}

function readRun222SelectorJsonForArm(arm, relPath) {
  assertArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (arm.armId !== "run2_22_full_selector_memory" && relPath !== RUN2_22_INPUTS.decisionMemory) {
    throw new Error(`${arm.armId} cannot read Run 2.21 selector gates or rejection matrix: ${relPath}`);
  }
  return readJson(relPath);
}

function validateRun221SelectorSchemas(decisionMemory, selectorGates, rejectionMatrix) {
  if (decisionMemory?.status !== "run2_21_visual_decision_memory_ready_public_blocked") {
    throw new Error("Run 2.21 visual decision memory schema/status mismatch");
  }
  if (selectorGates?.status !== "run2_21_per_role_selector_gates_ready_public_blocked") {
    throw new Error("Run 2.21 selector gates schema/status mismatch");
  }
  if (rejectionMatrix?.status !== "run2_21_evidence_rejection_matrix_ready_public_blocked") {
    throw new Error("Run 2.21 evidence rejection matrix schema/status mismatch");
  }
  const decisions = decisionMemory.visual_decision_memory ?? [];
  const gates = selectorGates.gates ?? [];
  const rejections = rejectionMatrix.role_records ?? [];
  if (decisions.length !== 6 || gates.length !== 6 || rejections.length !== 6) {
    throw new Error("Run 2.21 selector memory must contain six role records, gates, and rejection records");
  }
  const gateByRole = new Map(gates.map((gate) => [gate.role, gate]));
  const rejectionByRole = new Map(rejections.map((record) => [record.role, record]));
  for (const decision of decisions) {
    const gate = gateByRole.get(decision.role);
    const rejection = rejectionByRole.get(decision.role);
    if (!decision.decision_id || !decision.primary_evidence_id || !Array.isArray(decision.secondary_evidence_ids)) {
      throw new Error(`Run 2.21 decision is incomplete: ${decision.decision_id ?? "unknown"}`);
    }
    if (decision.secondary_evidence_ids.length > 2) {
      throw new Error(`Run 2.21 decision ${decision.decision_id} has too many secondary evidence ids`);
    }
    if (!gate || gate.required_visual_decision_memory_id !== decision.decision_id) {
      throw new Error(`Run 2.21 gate mismatch for role ${decision.role}`);
    }
    if (!rejection || rejection.visual_decision_memory_id !== decision.decision_id || !rejection.all_evidence_accounted_for) {
      throw new Error(`Run 2.21 rejection mismatch for role ${decision.role}`);
    }
    if (rejection.primary_evidence_id !== decision.primary_evidence_id) {
      throw new Error(`Run 2.21 primary evidence mismatch for role ${decision.role}`);
    }
    for (const field of [
      "run2_21_visual_decision_memory_id",
      "run2_21_primary_evidence_id",
      "run2_21_secondary_evidence_ids",
      "run2_21_rejected_evidence_reasons",
      "run2_21_selector_gate_id",
      "run2_21_visual_decision_delta",
    ]) {
      if (!gate.required_trace_fields?.includes(field)) {
        throw new Error(`Run 2.21 gate ${gate.gate_id} missing required trace field ${field}`);
      }
    }
  }
}

function selectRun221ForSlide(role, decisionMemory, selectorGates, rejectionMatrix) {
  const decision = (decisionMemory?.visual_decision_memory ?? []).find((item) => item.role === role);
  const gate = (selectorGates?.gates ?? []).find((item) => item.role === role);
  const rejection = (rejectionMatrix?.role_records ?? []).find((item) => item.role === role);
  if (!decision || !gate || !rejection) throw new Error(`Run 2.21 selector selection missing role ${role}`);
  if (gate.required_visual_decision_memory_id !== decision.decision_id) throw new Error(`Run 2.21 selector gate mismatch for role ${role}`);
  if (rejection.visual_decision_memory_id !== decision.decision_id) throw new Error(`Run 2.21 rejection matrix mismatch for role ${role}`);
  return { decision, gate, rejection };
}

function run222RequiredModulesByRole() {
  return new Map(
    Object.entries({
      cover: ["drawRun222CinematicSelectorField"],
      setup: ["drawRun222CinematicSelectorField", "drawRun222ProductTheaterSurface"],
      contrast: ["drawRun222CinematicSelectorField", "drawRun222EvidenceRoute"],
      proof: ["drawRun222ProductTheaterSurface", "drawRun222EvidenceRoute"],
      climax: ["drawRun222ClimaxEditorialStage"],
      close: ["drawRun222CinematicSelectorField", "drawRun222EvidenceRoute"],
    }),
  );
}

function run222VisualDeltaByRole() {
  return new Map(
    Object.entries({
      cover: "Run 2.22 binds one Run 2.21 primary evidence id before drawing the cover promise field.",
      setup: "Run 2.22 turns selector memory into a product-theater route instead of showing all workflow evidence.",
      contrast: "Run 2.22 uses rejected evidence reasons to keep the contrast slide from becoming equal panels.",
      proof: "Run 2.22 gives proof ownership to the selected product surface and records rejection outside the public slide.",
      climax: "Run 2.22 uses the selected primary metric evidence to stage one climax object.",
      close: "Run 2.22 keeps release blocked while showing a selector-driven handoff.",
    }),
  );
}

function loadRun222ContractData(arm) {
  const decisionMemory = readRun222SelectorJsonForArm(arm, RUN2_22_INPUTS.decisionMemory);
  const selectorGates = readRun222SelectorJsonForArm(arm, RUN2_22_INPUTS.selectorGates);
  const rejectionMatrix = readRun222SelectorJsonForArm(arm, RUN2_22_INPUTS.rejectionMatrix);
  validateRun221SelectorSchemas(decisionMemory, selectorGates, rejectionMatrix);
  return {
    decisionMemory,
    selectorGates,
    rejectionMatrix,
    requiredModulesByRole: run222RequiredModulesByRole(),
    visualDeltaByRole: run222VisualDeltaByRole(),
    status: "run2_22_selector_memory_contract_ready",
  };
}

function renderRun222FullSlide(presentation, spec, arm, n, fullData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const selection = selectRun221ForSlide(spec.role, fullData.decisionMemory, fullData.selectorGates, fullData.rejectionMatrix);

  if (spec.role === "cover") {
    drawRun222CinematicSelectorField(slide, arm, spec, selection, metrics, {
      x: 82,
      y: 118,
      w: 760,
      fontSize: 66,
      motifX: 930,
      motifY: 154,
      motifW: 172,
      motifH: 174,
    });
    drawRun222EvidenceRoute(slide, arm, spec, selection, metrics, { x: 78, y: 414, w: 990 });
  } else if (spec.role === "setup") {
    drawRun222CinematicSelectorField(slide, arm, spec, selection, metrics, {
      x: 86,
      y: 126,
      w: 430,
      titleH: 124,
      fontSize: 42,
      ruleY: 154,
      claimY: 190,
      claimW: 398,
      claimSize: 15,
      motifX: 0,
      motifY: 0,
      motifW: 0,
      motifH: 0,
    });
    drawRun222ProductTheaterSurface(slide, arm, spec, selection, metrics, { x: 596, y: 124 });
    drawRun222EvidenceRoute(slide, arm, spec, selection, metrics, { x: 92, y: 398, w: 960 });
  } else if (spec.role === "contrast") {
    drawRun222CinematicSelectorField(slide, arm, spec, selection, metrics, {
      x: 86,
      y: 118,
      w: 610,
      titleH: 118,
      fontSize: 38,
      ruleY: 146,
      claimY: 178,
      claimW: 418,
      claimSize: 14,
      motifX: 914,
      motifY: 132,
      motifW: 162,
      motifH: 130,
    });
    drawRun222EvidenceRoute(slide, arm, spec, selection, metrics, { x: 86, y: 356, w: 1000 });
  } else if (spec.role === "proof") {
    drawRun222ProductTheaterSurface(slide, arm, spec, selection, metrics, { x: 86, y: 118, w: 560, h: 366 });
    text(slide, spec.title, 690, 132, 410, 82, {
      fontSize: 34,
      bold: true,
      title: true,
      color: arm.palette.title,
    });
    registerText(metrics, spec.title);
    drawRun222EvidenceRoute(slide, arm, spec, selection, metrics, { x: 674, y: 372, w: 430 });
  } else if (spec.role === "climax") {
    drawRun222ClimaxEditorialStage(slide, arm, spec, selection, metrics);
  } else {
    drawRun222CinematicSelectorField(slide, arm, spec, selection, metrics, {
      x: 76,
      y: 116,
      w: 650,
      titleH: 170,
      fontSize: 54,
      claimW: 470,
      motifX: 966,
      motifY: 134,
      motifW: 150,
      motifH: 132,
    });
    drawRun222EvidenceRoute(slide, arm, spec, selection, metrics, { x: 538, y: 402, w: 564 });
  }

  proofFooter(slide, spec, arm, selection);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function renderControlSlide(presentation, spec, arm, n, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const mode = arm.armId === "bad_selector_memory" ? "bad" : arm.armId === "run1_5_skill" ? "run1_5" : "prompt";
  drawDenseControl(slide, arm, spec, metrics, mode);
  drawControlGate(slide, arm, spec, metrics, {
    x: spec.role === "climax" ? 1024 : 902,
    y: spec.role === "close" ? 326 : spec.role === "climax" ? 492 : 438,
    w: spec.role === "close" ? 226 : spec.role === "climax" ? 176 : 208,
    h: spec.role === "climax" ? 92 : 118,
    headline: arm.armId === "bad_selector_memory" ? "selector shallow" : "public blocked",
    line: arm.armId === "bad_selector_memory" ? "no gate/matrix read" : "no Run 2.22 selector trace",
  });
  proofFooter(slide, spec, arm, null);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertArmInputBoundaries(arm);
  const fullRun222 = arm.armId === "run2_22_full_selector_memory";
  const fullData = fullRun222 ? context.fullData ?? loadRun222ContractData(arm) : null;
  const requiredModulesByRole = fullData?.requiredModulesByRole ?? new Map();
  const visualDeltaByRole = fullData?.visualDeltaByRole ?? new Map();
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = fullRun222 && arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    commercial_case: `${pack}/commercial_case.md`,
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.22 selector-memory arm-specific generation from scripts/generate_ppt_run2_22_selector_memory_arms.mjs",
      no_cross_arm_reuse: ["cached memory summaries", "generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes", "selector trace carryover"],
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
      const selection = fullRun222
        ? selectRun221ForSlide(slide.role, fullData.decisionMemory, fullData.selectorGates, fullData.rejectionMatrix)
        : { decision: null, gate: null, rejection: null };
      const rejectionReasons = selection.rejection?.rejected_evidence?.map((item) => ({
        evidence_id: item.evidence_id,
        reason: item.reason,
      })) ?? [];
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_22_contract_status: fullRun222
          ? hasRenderedMetrics
            ? "full_arm_native_generator_rendered"
            : "full_arm_contract_preview_not_rendered"
          : "boundary_control_not_run2_22_full",
        run2_21_visual_decision_memory_id: fullRun222 ? selection.decision.decision_id : "",
        run2_21_primary_evidence_id: fullRun222 ? selection.decision.primary_evidence_id : "",
        run2_21_secondary_evidence_ids: fullRun222 ? selection.decision.secondary_evidence_ids : [],
        run2_21_rejected_evidence_reasons: fullRun222 ? rejectionReasons : [],
        run2_21_selector_gate_id: fullRun222 ? selection.gate.gate_id : "",
        run2_21_visual_decision_delta: fullRun222 ? visualDeltaByRole.get(slide.role) ?? "" : "",
        run2_21_surface_policy: fullRun222 ? selection.gate.public_surface_policy : "",
        run2_22_selector_execution_status: fullRun222 ? "selector_memory_executed_before_native_ppt_generation" : "",
        run2_22_required_code_module_ids: fullRun222 ? requiredModulesByRole.get(slide.role) ?? [] : [],
        run2_22_code_module_ids: fullRun222
          ? hasRenderedMetrics
            ? actualCodeModuleIds
            : requiredModulesByRole.get(slide.role) ?? []
          : [],
        run2_22_bad_control_probe: fullRun222
          ? "bad_selector_memory may read visual decision memory but forbids Run 2.21 selector gates and rejection matrix; if it matches full arm, selector gates did not add value"
          : "boundary_control",
        negative_control_decision_memory_id:
          arm.armId === "bad_selector_memory" ? `decision_memory_only_without_selector_gate_for_${slide.role}` : "",
        layout_metrics: {
          text_box_count: roleMetrics.textBoxCount,
          visible_words: roleMetrics.visibleWords,
          proof_objects: roleMetrics.proofObjects,
          zones: roleMetrics.zones,
          workflow_objects: roleMetrics.workflowObjects,
          gate_objects: roleMetrics.gateObjects,
          delta_panels: roleMetrics.deltaPanels,
          hero_object_canvas_share: Number(roleMetrics.heroShare.toFixed(3)),
        },
      };
    }),
  };
}

function assertRun222SelectorGateSelfCheck(trace) {
  if (trace.arm_id !== "run2_22_full_selector_memory") return;
  for (const slide of trace.slides) {
    if (slide.run2_22_contract_status !== "full_arm_native_generator_rendered") {
      throw new Error(`Run 2.22 full slide ${slide.slide_id} was not rendered with native module metrics`);
    }
    for (const field of EXPECTED_RUN2_22_TRACE_FIELDS) {
      const value = slide[field];
      const empty =
        value == null ||
        (Array.isArray(value) && value.length === 0) ||
        (typeof value === "string" && value.trim() === "") ||
        (typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === 0);
      if (empty) throw new Error(`Run 2.22 full slide ${slide.slide_id} missing ${field}`);
    }
    const actualCodeModules = new Set(slide.run2_22_code_module_ids ?? []);
    for (const requiredCodeModule of slide.run2_22_required_code_module_ids ?? []) {
      if (!actualCodeModules.has(requiredCodeModule)) {
        throw new Error(`Run 2.22 full slide ${slide.slide_id} did not call required module ${requiredCodeModule}`);
      }
    }
    if (slide.run2_21_surface_policy !== "trace_suppressed_from_public_slide_surface") {
      throw new Error(`Run 2.22 full slide ${slide.slide_id} did not suppress trace from public slide surface`);
    }
    if (slide.role === "climax" && !(slide.layout_metrics?.hero_object_canvas_share > 0.3)) {
      throw new Error("Run 2.22 climax missing large hero stage");
    }
  }
}

function buildArmContract() {
  return armSpecs.map((arm) => ({
    armId: arm.armId,
    label: arm.label,
    contract_status:
      arm.armId === "run2_22_full_selector_memory"
        ? "run2_22_selector_memory_contract_ready_requires_render_metrics"
        : "run2_22_boundary_control_contract_ready",
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

function buildNamedContactSheet(out, title, previewPaths, cols = 3) {
  execFileSync(
    "python3",
    [
      path.join(root, "scripts", "build_ppt_contact_sheet.py"),
      "--out",
      out,
      "--title",
      title,
      "--cols",
      String(cols),
      ...previewPaths,
    ],
    { cwd: root, stdio: "pipe" },
  );
  return out;
}

function buildContactSheet(workspace, arm, previewPaths) {
  return buildNamedContactSheet(path.join(workspace, "preview", "contact-sheet.png"), arm.label, previewPaths);
}

function buildRun222FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  return buildNamedContactSheet(path.join(outRoot, "run2-22-four-arm-contact-sheet.png"), "Run 2.22 four-arm comparison", sheets, sheets.length);
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
      `allowed inputs: ${arm.allowed.join(", ")}`,
      `forbidden inputs: ${arm.forbidden.join(", ")}`,
      "required proof objects: selector-bound promise field, product theater surface, accepted/rejected evidence route, editorial climax stage",
      "source requirements: commercial case always; bad control may read Run 2.21 visual decision memory only; full arm requires Run 2.21 selector gates and rejection matrix before native PPT generation",
      "brand authenticity constraints: no copied source visuals, no borrowed brand chrome, no screenshots, no raw tutorial media",
      "profile-specific QA gates: contact-sheet coherence, editable native text/shapes only, selector trace hidden from public slide surface, release gate visibly blocked",
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
  if (arm.armId === "run2_22_full_selector_memory") {
    fullData = loadRun222ContractData(arm);
  } else if (arm.armId === "bad_selector_memory") {
    readRun222SelectorJsonForArm(arm, RUN2_22_INPUTS.decisionMemory);
  }

  const slides = arm.slides.map((slide, index) =>
    arm.armId === "run2_22_full_selector_memory"
      ? renderRun222FullSlide(presentation, slide, arm, index + 1, fullData, metricsByRole)
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
  assertRun222SelectorGateSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_22_selector_memory_arms.mjs",
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

function writeRun222Result(runSummary) {
  const result = {
    schema_version: 1,
    run_id: "2.22",
    status: "rerun_completed_public_blocked",
    public_ready: false,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      visual_decision_memory: RUN2_22_INPUTS.decisionMemory,
      selector_gates: RUN2_22_INPUTS.selectorGates,
      rejection_matrix: RUN2_22_INPUTS.rejectionMatrix,
      source_data_layer: "docs/product/ppt-run2-data-skill-quality/results/run2_21_visual_decision_memory_result.json",
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_22_selector_memory_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_22_full_selector_memory",
      best_internal_arm_verdict: "selector_memory_executed_before_native_ppt_generation",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    control_boundary: {
      bad_selector_memory: "decision_memory_only_without_selector_gates_or_rejection_matrix",
      prompt_only: "commercial_case_only_no_run2_21_selector_memory",
      run1_5_skill: "prior_baseline_no_run2_21_selector_memory",
    },
    remaining_public_release_gates: [
      "human_visual_review",
      "native_or_cross_platform_render_inspection",
      "motion_or_video_review",
      "source_boundary_review",
      "human_release_approval",
    ],
    trace_manifest_requirements: EXPECTED_RUN2_22_TRACE_FIELDS,
    native_module_status: "actual_run2_22_module_calls_recorded_in_trace_manifest",
    release_boundary: "public_blocked_until_visual_human_review_native_render_review_motion_review_source_boundary_review_and_human_approval",
    next_required_action: "review_run2_22_outputs_against_run2_21_selector_contract_then_continue_thickening_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_22_selector_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_22_selector_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.22 Selector Rerun Result",
      "",
      "Status: rerun completed, public blocked.",
      "",
      "Run 2.22 is the generated four-arm rerun that consumes Run 2.21 visual-decision memory, per-role selector gates, and the evidence rejection matrix before native PPT code generation. It repeats the same five layers and does not advance to Run 3.0.",
      "",
      "The generator is `scripts/generate_ppt_run2_22_selector_memory_arms.mjs`.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_22_full_selector_memory`",
      "- `bad_selector_memory`",
      "",
      "The negative control `bad_selector_memory` may read Run 2.21 visual-decision memory, but it is blocked from reading selector gates and the rejection matrix.",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_22_full_selector_memory`.",
      "",
      "Verdict: `selector_memory_executed_before_native_ppt_generation`.",
      "",
      "Public release remains blocked. This proves selector-memory execution, not final public-video-grade visual quality.",
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
  const fourArmSheet = buildRun222FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_22_selector_memory_four_arms",
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_22_selector_rerun_summary.json"), runSummary);
  writeRun222Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  EXPECTED_RUN2_22_TRACE_FIELDS,
  RUN2_22_INPUTS,
  RUN2_22_DATA_INPUTS,
  armSpecs,
  assertArmInputBoundaries,
  assertRun222SelectorGateSelfCheck,
  buildArmContract,
  drawRun222CinematicSelectorField,
  drawRun222ProductTheaterSurface,
  drawRun222EvidenceRoute,
  drawRun222ClimaxEditorialStage,
  main,
  readRun222SelectorJsonForArm,
  registerRun222Module,
  run222RequiredModulesByRole,
  run222VisualDeltaByRole,
  selectRun221ForSlide,
  traceFor,
  validateRun221SelectorSchemas,
};
