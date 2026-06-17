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
  ink: "#14171c",
  paper: "#f6f2e9",
  white: "#ffffff",
  line: "#d6d0c4",
  muted: "#657079",
  deep: "#101820",
  slate: "#2b3541",
  blue: "#2b64d8",
  sky: "#dce7ff",
  mint: "#dcefe7",
  green: "#0d8b68",
  coral: "#e34f37",
  amber: "#d79a2e",
  sand: "#efe5d5",
  khaki: "#d7c79f",
  olive: "#756a3f",
  fog: "#edf0f2",
  steel: "#cad1d8",
};

const EXPECTED_RUN2_10_TRACE_FIELDS = [
  "run2_10_visual_system_source_ids",
  "run2_10_visual_system_memory_ids",
  "run2_10_gate_matrix_ids",
  "run2_10_code_module_ids",
  "run2_10_visual_delta_from_run2_9",
  "run2_10_sameness_failure_probe",
  "run2_10_public_demo_first_read_probe",
  "run2_10_shape_count_budget",
  "run2_10_asymmetry_whitespace_rule",
];

const RUN2_10_INPUTS = {
  sources: `${pack}/run2_10_visual_system_sources.json`,
  memory: `${pack}/run2_10_visual_system_memory.json`,
  gateMatrix: `${pack}/run2_10_visual_system_gate_matrix.json`,
};
const RUN2_10_RESTRICTED_INPUTS = Object.values(RUN2_10_INPUTS);

const baseSlides = [
  {
    role: "cover",
    title: "The deck stops looking like a report.",
    claim: "Run 2.10 converts tutorial learning into visual systems before native PPT code is written.",
    trace: "commercial_case -> visual systems -> native PPT",
  },
  {
    role: "setup",
    title: "Visual learning becomes a surface, not a checklist.",
    claim: "The workflow now selects editorial composition and product depth before drawing proof.",
    trace: "editorial_spread + layered_product_surface",
  },
  {
    role: "contrast",
    title: "Boxiness is the failure probe.",
    claim: "The full arm must visibly move away from equal panels, card grids, and dashboard rhythm.",
    trace: "boxiness_probe + visual_delta_from_run2_8",
  },
  {
    role: "proof",
    title: "Data, module, and sequence must show up together.",
    claim: "Layered product surface carries the proof; motion storyboard shows how the proof unfolds.",
    trace: "product_depth + motion_storyboard",
  },
  {
    role: "climax",
    title: "One stage owns the public-demo moment.",
    claim: "The climax becomes a keynote-style reveal instead of another grid of evidence boxes.",
    trace: "climax_stage + pause + perimeter_evidence",
  },
  {
    role: "close",
    title: "The next loop is a decision handoff.",
    claim: "Public release stays blocked, but the workflow now knows what visual quality must improve next.",
    trace: "typographic_field + handoff_surface + release_gate",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-10-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.10 / CONTROL",
    footer: "prompt_only | commercial case only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [
      `${pack}/run2_10_visual_system_sources.json`,
      `${pack}/run2_10_visual_system_memory.json`,
      `${pack}/run2_10_visual_system_gate_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "docs/product/ppt-run1-5-product-lab/",
    ],
    palette: {
      bg: "#f5f6f8",
      rail: "#394456",
      accent: C.blue,
      accent2: C.steel,
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d8dde4",
      gate: "#e9edf3",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "The prompt asks for better slides.",
        "The setup names visual quality.",
        "The contrast requests less boxiness.",
        "The proof says data should drive design.",
        "The climax reserves space for impact.",
        "The close keeps release blocked.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-10-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.10 / RUN 1.5",
    footer: "run1_5_skill | prior workflow baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [
      `${pack}/run2_10_visual_system_sources.json`,
      `${pack}/run2_10_visual_system_memory.json`,
      `${pack}/run2_10_visual_system_gate_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
    ],
    palette: {
      bg: "#f4f6fa",
      rail: "#2d3a55",
      accent: C.blue,
      accent2: C.green,
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d6dce6",
      gate: "#e9edf4",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "A useful baseline still stays report-like.",
        "The setup explains more than it composes.",
        "The contrast improves labels before structure.",
        "The proof routes steps into boxes.",
        "The climax remains smaller than the story.",
        "The close is clear but not cinematic.",
      ][index],
    })),
  },
  {
    armId: "run2_10_full_skill",
    slug: "ppt-run2-10-full-vulca",
    label: "Run 2.10 full Vulca skill",
    kicker: "RUN 2.10 / FULL VULCA",
    footer: "run2_10_full_skill | sources + visual-system memory + gate matrix | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/sources.json`,
      `${pack}/run2_8_tutorial_decomposition.json`,
      `${pack}/run2_8_executable_design_memory.json`,
      `${pack}/run2_8_workflow_gate_matrix.json`,
      `${pack}/run2_10_visual_system_sources.json`,
      `${pack}/run2_10_visual_system_memory.json`,
      `${pack}/run2_10_visual_system_gate_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    forbidden: [
      "docs/product/ppt-run1-5-product-lab/",
      "copied source visuals",
      "winner claims before scoring",
    ],
    palette: {
      bg: "#f7f2e8",
      rail: "#111820",
      accent: "#17242c",
      accent2: "#95a6ad",
      proof: C.coral,
      panel: C.white,
      title: "#10161b",
      muted: "#5e6b73",
      rule: "#d8d0c2",
      gate: "#17212a",
    },
    slides: baseSlides,
  },
  {
    armId: "bad_visual_system_memory",
    slug: "ppt-run2-10-bad-visual-system-memory",
    label: "Bad visual-system boundary control",
    kicker: "RUN 2.10 / NEGATIVE CONTROL",
    footer: "bad_visual_system_memory | sources only | internal comparison",
    release: "internal_only",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/run2_10_visual_system_sources.json`,
      `${pack}/sources.json`,
    ],
    forbidden: [
      `${pack}/run2_10_visual_system_memory.json`,
      `${pack}/run2_10_visual_system_gate_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "manual Run 2.10 visual module repair before scoring",
    ],
    palette: {
      bg: "#f2efe1",
      rail: "#6d633e",
      accent: C.olive,
      accent2: C.khaki,
      panel: "#f8f3e5",
      title: "#2f2b1e",
      muted: "#6a644f",
      rule: "#d8cfb9",
      gate: "#ede2c1",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Primitive names do not fix the canvas.",
        "The setup crowds the route instead of choosing.",
        "The delta weakens into equal panels.",
        "The proof names motion without showing it.",
        "The climax loses the stage.",
        "The close becomes a checklist again.",
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
  fs.writeFileSync(path.join(workspace, "package.json"), JSON.stringify({ private: true, type: "module" }, null, 2) + "\n");
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
    heroBindingId: "",
    visualModuleIds: new Set(),
    codeBindingIds: new Set(),
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerNativeModule(metrics, functionName) {
  metrics.codeBindingIds.add(functionName);
}

function registerVisualModule(metrics, functionName) {
  metrics.visualModuleIds.add(functionName);
  registerNativeModule(metrics, functionName);
}

function registerRun210VisualModule(metrics, functionName) {
  registerVisualModule(metrics, functionName);
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

function registerHero(metrics, bindingId, x, y, w, h) {
  metrics.heroBindingId = bindingId;
  const area = Math.max(1, MAIN_CANVAS.w * MAIN_CANVAS.h);
  metrics.heroShare = (w * h) / area;
}

function base(slide, arm, n) {
  rect(slide, 0, 0, W, H, arm.palette.bg);
  rect(slide, 0, 0, 14, H, arm.palette.rail);
  text(slide, arm.kicker, 54, 30, 420, 22, {
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
  text(slide, arm.footer, 650, 674, 574, 22, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
    align: "right",
  });
  for (let i = 1; i <= 6; i += 1) {
    rect(slide, 54 + (i - 1) * 20, 684, i === n ? 16 : 8, 5, i === n ? arm.palette.accent : C.line);
  }
}

function proofFooter(slide, spec, arm) {
  text(slide, `trace: ${spec.trace}`, 66, 628, 850, 28, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
    fill: arm.palette.panel,
    line: colorLine(C.line, 1),
    insets: { left: 18, right: 8, top: 8, bottom: 5 },
  });
  rect(slide, 76, 640, 7, 7, arm.palette.accent);
}

function moduleLabel(slide, x, y, label, arm) {
  chip(slide, label, x, y, Math.max(132, label.length * 7 + 28), arm.palette.panel, arm.palette.accent);
}

function firstModule(modules, functionName) {
  return modules.find((module) => module.code_binding?.function_name === functionName) ?? null;
}

function drawRun210EditorialTypeSystem(slide, arm, spec, module, metrics, opts = {}) {
  registerRun210VisualModule(metrics, "drawRun210EditorialTypeSystem");
  const params = module?.code_binding?.params ?? {};
  const fontSize = opts.fontSize ?? Math.max(58, params.headlineMinPt ?? 58);
  const x = opts.x ?? 76;
  const y = opts.y ?? 118;
  const w = opts.w ?? 700;
  const h = opts.h ?? 250;
  moduleLabel(slide, opts.labelX ?? x, opts.labelY ?? y - 38, "typographic field", arm);
  text(slide, spec.title, x, y, w, h, {
    fontSize,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  rect(slide, x + 8, y + h + 18, 114, 8, arm.palette.proof ?? arm.palette.accent);
  rect(slide, x + 142, y + h + 18, 38, 8, arm.palette.accent2);
  text(slide, spec.claim, x + 2, y + h + 46, opts.claimW ?? 520, 54, {
    fontSize: opts.claimSize ?? 17,
    color: arm.palette.muted,
  });
  registerText(metrics, spec.claim);
  rect(slide, opts.objectX ?? 860, opts.objectY ?? 148, opts.objectW ?? 210, opts.objectH ?? 170, arm.palette.accent, colorLine(arm.palette.accent, 1));
  rect(slide, (opts.objectX ?? 860) + 34, (opts.objectY ?? 148) + 38, 72, 72, arm.palette.proof ?? C.coral, colorLine(arm.palette.proof ?? C.coral, 1));
  rect(slide, (opts.objectX ?? 860) + 128, (opts.objectY ?? 148) + 48, 74, 10, C.white);
  rect(slide, (opts.objectX ?? 860) + 128, (opts.objectY ?? 148) + 82, 56, 8, "#cad2d7");
  registerProof(metrics, 1);
}

function drawRun210FullBleedVisualField(slide, arm, spec, module, metrics, opts = {}) {
  registerRun210VisualModule(metrics, "drawRun210FullBleedVisualField");
  const x = opts.x ?? 80;
  const y = opts.y ?? 118;
  const w = opts.w ?? 1040;
  const h = opts.h ?? 430;
  const dark = Boolean(opts.dark);
  const fieldW = Math.round(w * (opts.fieldRatio ?? 0.64));
  const railW = Math.round(w * 0.18);
  moduleLabel(slide, x, y - 38, "editorial spread", arm);
  rect(slide, x, y + 24, fieldW, h - 42, dark ? arm.palette.gate : "#fbfaf6", colorLine(dark ? arm.palette.gate : arm.palette.rule, 1));
  rect(slide, x + fieldW + 34, y + 8, railW, h - 10, arm.palette.panel, colorLine(arm.palette.rule, 1));
  rect(slide, x + fieldW + railW + 72, y + 96, Math.max(92, w - fieldW - railW - 100), 176, arm.palette.proof ?? arm.palette.accent, colorLine(arm.palette.proof ?? arm.palette.accent, 1));
  text(slide, opts.headline ?? spec.title, x + 34, y + 68, fieldW - 70, 138, {
    fontSize: opts.headlineSize ?? 46,
    bold: true,
    title: true,
    color: dark ? C.white : arm.palette.title,
  });
  registerText(metrics, opts.headline ?? spec.title);
  text(slide, opts.note ?? spec.claim, x + 38, y + 250, Math.max(320, fieldW - 112), 48, {
    fontSize: opts.noteSize ?? 15,
    color: dark ? "#d8e2e3" : arm.palette.muted,
  });
  registerText(metrics, opts.note ?? spec.claim);
  const labels = opts.railLabels ?? ["primitive", "module", "gate"];
  labels.slice(0, 3).forEach((label, index) => {
    const yy = y + 58 + index * 86;
    rect(slide, x + fieldW + 54, yy, railW - 40, 36, index === 2 ? arm.palette.accent : C.fog, colorLine(index === 2 ? arm.palette.accent : "#d4dbe0", 1));
    text(slide, label, x + fieldW + 68, yy + 11, railW - 68, 12, {
      fontSize: 9,
      bold: true,
      mono: true,
      color: index === 2 ? C.white : arm.palette.accent,
    });
    registerText(metrics, label);
    if (index < 2) rect(slide, x + fieldW + 92, yy + 44, 4, 34, arm.palette.proof ?? arm.palette.accent);
  });
  registerZones(metrics, 2);
  registerProof(metrics, 1);
  registerDeltaPanels(metrics, 1);
}

function drawRun210ProductTheater(slide, arm, spec, module, metrics, opts = {}) {
  registerRun210VisualModule(metrics, "drawRun210ProductTheater");
  const x = opts.x ?? 604;
  const y = opts.y ?? 134;
  const w = opts.w ?? 504;
  const h = opts.h ?? 352;
  moduleLabel(slide, x, y - 38, "layered product surface", arm);
  rect(slide, x + 58, y + 54, w - 58, h - 56, "#dfe7e9", colorLine("#dfe7e9", 1));
  rect(slide, x + 32, y + 30, w - 58, h - 50, "#edf1f2", colorLine("#d2d9dc", 1));
  rect(slide, x, y, w - 60, h - 56, C.white, colorLine(arm.palette.accent, 2));
  rect(slide, x + 26, y + 28, 152, 22, arm.palette.accent, colorLine(arm.palette.accent, 1));
  rect(slide, x + 26, y + 76, w - 130, 72, C.fog, colorLine("#d2d9dc", 1));
  rect(slide, x + 46, y + 96, 128, 18, arm.palette.proof ?? arm.palette.accent);
  rect(slide, x + 206, y + 100, 84, 10, "#bec8cd");
  rect(slide, x + 322, y + 100, 66, 10, "#bec8cd");
  const nodes = [
    [x + 54, y + 202, "learn"],
    [x + 202, y + 232, "bind"],
    [x + 350, y + 186, "render"],
  ];
  nodes.forEach(([nx, ny, label], index) => {
    rect(slide, nx, ny, 98, 42, index === 2 ? arm.palette.proof ?? arm.palette.accent : C.white, colorLine(index === 2 ? arm.palette.proof ?? arm.palette.accent : "#cad2d8", 1));
    text(slide, label, nx + 16, ny + 14, 70, 12, {
      fontSize: 10,
      bold: true,
      mono: true,
      color: index === 2 ? C.white : arm.palette.accent,
    });
    registerText(metrics, label);
    if (index < nodes.length - 1) {
      const [nextX, nextY] = nodes[index + 1];
      rect(slide, nx + 98, ny + 20, Math.max(24, nextX - nx - 98), 4, arm.palette.proof ?? arm.palette.accent);
      rect(slide, nextX - 8, nextY + 20, 8, 4, arm.palette.proof ?? arm.palette.accent);
    }
  });
  text(slide, opts.caption ?? "native layers create depth before labels", x + 26, y + h - 44, w - 110, 20, {
    fontSize: 12,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, opts.caption ?? "native layers create depth before labels");
  registerProof(metrics, 2);
  registerZones(metrics, 3);
  registerWorkflow(metrics, 3);
}

function drawRun210NonRectangularProofPath(slide, arm, spec, module, metrics, opts = {}) {
  registerRun210VisualModule(metrics, "drawRun210NonRectangularProofPath");
  const x = opts.x ?? 104;
  const y = opts.y ?? 352;
  const nodes = opts.nodes ?? [
    { label: "brief", x: x + 10, y: y + 66, r: 54, fill: C.white },
    { label: "learn", x: x + 228, y: y + 8, r: 74, fill: arm.palette.sky ?? C.sky },
    { label: "bind", x: x + 492, y: y + 104, r: 62, fill: arm.palette.proof ?? C.coral },
    { label: "ship", x: x + 760, y: y + 20, r: 92, fill: arm.palette.accent },
  ];
  moduleLabel(slide, x, y - 44, "non-rectangular proof path", arm);
  for (let index = 0; index < nodes.length - 1; index += 1) {
    const current = nodes[index];
    const next = nodes[index + 1];
    const sx = current.x + current.r;
    const sy = current.y + current.r / 2;
    const ex = next.x + 4;
    const ey = next.y + next.r / 2;
    rect(slide, sx, sy, Math.max(24, ex - sx), 6, arm.palette.proof ?? C.coral, colorLine(arm.palette.proof ?? C.coral, 1));
    rect(slide, ex - 8, ey - 14, 18, 18, arm.palette.proof ?? C.coral, colorLine(arm.palette.proof ?? C.coral, 1));
  }
  nodes.forEach((node, index) => {
    ellipse(slide, node.x, node.y, node.r, node.r, node.fill, colorLine(index === nodes.length - 1 ? arm.palette.accent : arm.palette.rule, index === nodes.length - 1 ? 3 : 1));
    text(slide, node.label, node.x + 10, node.y + node.r / 2 - 8, node.r - 20, 16, {
      fontSize: index === nodes.length - 1 ? 12 : 10,
      bold: true,
      mono: true,
      color: index === nodes.length - 1 ? C.white : arm.palette.accent,
      align: "center",
    });
    registerText(metrics, node.label);
  });
  text(slide, opts.caption ?? "evidence moves through a path, not a table", x + 62, y + 196, 430, 26, {
    fontSize: 15,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, opts.caption ?? "evidence moves through a path, not a table");
  registerProof(metrics, 4);
  registerWorkflow(metrics, 4);
}

function drawRun210KineticSequence(slide, arm, spec, module, metrics, opts = {}) {
  registerRun210VisualModule(metrics, "drawRun210KineticSequence");
  const x = opts.x ?? 100;
  const y = opts.y ?? 430;
  const w = opts.w ?? 880;
  const h = opts.h ?? 126;
  moduleLabel(slide, x, y - 38, "motion storyboard", arm);
  const beats = opts.beats ?? [
    ["orient", 0.26],
    ["transform", 0.34],
    ["handoff", 0.24],
  ];
  let cursor = x;
  beats.forEach(([label, ratio], index) => {
    const beatW = Math.round(w * ratio);
    const beatH = index === 1 ? h : Math.round(h * 0.76);
    const beatY = y + (index === 1 ? 0 : Math.round(h * 0.12));
    rect(slide, cursor, beatY, beatW, beatH, index === 1 ? arm.palette.accent : C.white, colorLine(index === 1 ? arm.palette.accent : "#cfd6dc", 1));
    rect(slide, cursor + 20, beatY + 24, Math.round(beatW * (index === 1 ? 0.42 : 0.28)), Math.round(beatH * (index === 1 ? 0.52 : 0.36)), index === 1 ? arm.palette.proof ?? C.coral : "#dfe6e8");
    text(slide, label, cursor + 22, beatY + beatH - 34, beatW - 44, 18, {
      fontSize: index === 1 ? 15 : 11,
      bold: true,
      mono: true,
      color: index === 1 ? C.white : arm.palette.accent,
    });
    registerText(metrics, label);
    if (index < beats.length - 1) rect(slide, cursor + beatW + 6, y + h / 2 - 2, 28, 4, arm.palette.proof ?? arm.palette.accent);
    cursor += beatW + 40;
  });
  rect(slide, x + Math.round(w * 0.47), y - 18, 70, 12, arm.palette.proof ?? C.coral);
  text(slide, "pause", x + Math.round(w * 0.47) + 82, y - 22, 80, 16, {
    fontSize: 10,
    bold: true,
    mono: true,
    color: arm.palette.proof ?? C.coral,
  });
  registerText(metrics, "pause");
  registerWorkflow(metrics, 3);
  registerProof(metrics, 1);
}

function drawRun210CinematicClimax(slide, arm, spec, module, metrics, opts = {}) {
  registerRun210VisualModule(metrics, "drawRun210CinematicClimax");
  const stage = { x: 126, y: 100, w: 1010, h: 484 };
  moduleLabel(slide, 84, 98, "climax stage", arm);
  rect(slide, stage.x, stage.y, stage.w, stage.h, arm.palette.gate, colorLine(arm.palette.gate, 1));
  text(slide, "one stage owns the proof", stage.x + 46, stage.y + 44, 360, 52, {
    fontSize: 28,
    bold: true,
    title: true,
    color: C.white,
  });
  registerText(metrics, "one stage owns the proof");
  const hero = { x: stage.x + 190, y: stage.y + 118, w: 650, h: 272 };
  rect(slide, hero.x - 66, hero.y - 60, hero.w + 132, hero.h + 120, "#202c35", colorLine("#202c35", 1));
  rect(slide, hero.x, hero.y, hero.w, hero.h, C.white, colorLine(arm.palette.proof ?? C.coral, 4));
  rect(slide, hero.x + 60, hero.y + 56, 232, 156, arm.palette.proof ?? C.coral, colorLine(arm.palette.proof ?? C.coral, 1));
  rect(slide, hero.x + 330, hero.y + 66, 178, 14, arm.palette.accent2);
  rect(slide, hero.x + 330, hero.y + 116, 218, 9, "#bfc9ce");
  rect(slide, hero.x + 330, hero.y + 152, 136, 9, "#bfc9ce");
  text(slide, "public-demo reveal", hero.x + 60, hero.y + hero.h - 54, 360, 26, {
    fontSize: 22,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, "public-demo reveal");
  const evidence = ["data learned", "native trace", "release blocked"];
  evidence.forEach((label, index) => {
    const ex = index === 0 ? stage.x + 46 : index === 1 ? stage.x + stage.w - 212 : stage.x + stage.w - 224;
    const ey = index === 0 ? stage.y + stage.h - 102 : index === 1 ? stage.y + 54 : stage.y + stage.h - 92;
    rect(slide, ex, ey, 164, 34, "#2f3d46", colorLine("#54636c", 1));
    text(slide, label, ex + 14, ey + 11, 132, 12, {
      fontSize: 9,
      bold: true,
      mono: true,
      color: "#d8e4e7",
    });
    registerText(metrics, label);
  });
  registerHero(metrics, "module_2_9_climax_stage", stage.x, stage.y, stage.w, stage.h);
  registerProof(metrics, 1);
  registerGate(metrics, 1);
}

function drawControlGate(slide, arm, spec, metrics, opts = {}) {
  const x = opts.x ?? 906;
  const y = opts.y ?? 438;
  const w = opts.w ?? 202;
  const h = opts.h ?? 116;
  rect(slide, x, y, w, h, arm.palette.gate, colorLine(arm.palette.rule, 1));
  text(slide, opts.headline ?? "public blocked", x + 16, y + 22, w - 32, 30, {
    fontSize: 16,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  text(slide, opts.line ?? "no visual module trace", x + 16, y + 66, w - 32, 18, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
  });
  registerText(metrics, `${opts.headline ?? "public blocked"} ${opts.line ?? "no visual module trace"}`);
  registerGate(metrics, 1);
}

function drawDenseControl(slide, arm, spec, metrics, mode = "prompt") {
  const titleSize = mode === "bad" ? 34 : 38;
  text(slide, spec.title, 76, 132, 560, 92, {
    fontSize: titleSize,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, spec.claim, 80, 242, 520, 62, { fontSize: 16, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  const panelFill = mode === "bad" ? "#efe4c8" : C.white;
  if (spec.role === "cover") {
    rect(slide, 700, 130, 414, 288, mode === "bad" ? "#eadfbe" : C.deep, colorLine(mode === "bad" ? arm.palette.rule : C.deep, 1));
    for (let row = 0; row < (mode === "bad" ? 4 : 2); row += 1) {
      for (let col = 0; col < (mode === "bad" ? 4 : 2); col += 1) {
        rect(slide, 736 + col * 86, 168 + row * 48, mode === "bad" ? 58 : 118, mode === "bad" ? 28 : 58, mode === "bad" ? "#dfd0a7" : arm.palette.accent, colorLine(mode === "bad" ? arm.palette.rule : arm.palette.accent, 1));
      }
    }
  } else if (spec.role === "proof") {
    ["brief", "workflow", "native", "gate", "review"].forEach((label, index) => {
      rect(slide, 84 + index * 188, 328 + (index % 2) * 74, 150, 58, panelFill, colorLine(arm.palette.rule, 1));
      text(slide, label, 102 + index * 188, 348 + (index % 2) * 74, 112, 18, { fontSize: 10, bold: true, mono: true, color: arm.palette.accent });
      registerText(metrics, label);
    });
  } else if (spec.role === "climax") {
    for (let col = 0; col < 3; col += 1) {
      rect(slide, 94 + col * 300, 324, 248, 150, panelFill, colorLine(arm.palette.rule, 1));
      text(slide, ["brief", "baseline", "result"][col], 116 + col * 300, 352, 190, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.accent });
      text(slide, mode === "bad" ? "equal panels stay equal" : "impact is reserved, not staged", 116 + col * 300, 390, 198, 42, { fontSize: 15, bold: true, title: true, color: arm.palette.title });
      registerText(metrics, ["brief", "baseline", "result"][col]);
    }
  } else {
    rect(slide, 84, 330, 472, 204, panelFill, colorLine(arm.palette.rule, 1));
    text(slide, mode === "bad" ? "Primitive labels are present but the layout still behaves like boxes." : "The control can be readable while still lacking bound visual modules.", 108, 366, 410, 82, {
      fontSize: mode === "bad" ? 18 : 20,
      bold: true,
      title: true,
      color: arm.palette.title,
    });
    registerText(metrics, mode === "bad" ? "Primitive labels are present but the layout still behaves like boxes." : "The control can be readable while still lacking bound visual modules.");
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

  if (arm.armId === "run2_10_full_skill") {
    for (const input of RUN2_10_RESTRICTED_INPUTS) assertAllowed(input);
    return;
  }
  if (arm.armId === "bad_visual_system_memory") {
    assertAllowed(RUN2_10_INPUTS.sources);
    assertForbidden(RUN2_10_INPUTS.memory);
    assertForbidden(RUN2_10_INPUTS.gateMatrix);
    return;
  }
  for (const input of RUN2_10_RESTRICTED_INPUTS) assertForbidden(input);
}

function readRun210JsonForArm(arm, relPath) {
  assertArmInputBoundaries(arm);
  if (arm.armId !== "run2_10_full_skill") {
    throw new Error(`${arm.armId} cannot read Run 2.10 visual-module input: ${relPath}`);
  }
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  return readJson(relPath);
}

function readRun210SourcesForArm(arm) {
  assertArmInputBoundaries(arm);
  if (!arm.allowed.includes(RUN2_10_INPUTS.sources) || arm.forbidden.includes(RUN2_10_INPUTS.sources)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${RUN2_10_INPUTS.sources}`);
  }
  return readJson(RUN2_10_INPUTS.sources);
}

function run210VisualSystemGateMatrixByRole(gateMatrix) {
  return new Map((gateMatrix?.gates ?? []).map((gate) => [gate.slide_role, gate]));
}

function run210VisualSystemSourcesById(sources) {
  return new Map((sources?.sources ?? []).map((source) => [source.id, source]));
}

function run210VisualSystemsById(memory) {
  return new Map((memory?.visual_systems ?? []).map((visualSystem) => [visualSystem.visual_system_id, visualSystem]));
}

function run210VisualSystemSourcesByRole(sources, gateMatrix) {
  const sourcesById = run210VisualSystemSourcesById(sources);
  const map = new Map();
  for (const gate of gateMatrix?.gates ?? []) {
    map.set(
      gate.slide_role,
      gate.visual_system_source_ids.map((id) => sourcesById.get(id)).filter(Boolean),
    );
  }
  return map;
}

function run210VisualSystemsByRole(memory) {
  const map = new Map();
  for (const visualSystem of memory?.visual_systems ?? []) {
    for (const role of visualSystem.applicable_slide_roles ?? []) {
      const bucket = map.get(role) ?? [];
      bucket.push(visualSystem);
      map.set(role, bucket);
    }
  }
  return map;
}

function run210CodeModulesByRole(gateMatrix) {
  const map = new Map();
  for (const gate of gateMatrix?.gates ?? []) {
    map.set(gate.slide_role, gate.required_code_modules ?? []);
  }
  return map;
}

function run210ShapeBudgetByRole(gateMatrix) {
  const map = new Map();
  for (const gate of gateMatrix?.gates ?? []) {
    map.set(gate.slide_role, gate.shape_count_budget ?? {});
  }
  return map;
}

function run210VisualDeltaByRole() {
  return new Map(
    Object.entries({
      cover: "full-bleed launch field replaces the Run 2.9 title-object and lower card rhythm",
      setup: "product theater with proof path replaces Run 2.9 layered product rectangle",
      contrast: "one field with diagonal proof path replaces Run 2.9 boxed comparison",
      proof: "product theater plus kinetic arc replaces Run 2.9 product beside storyboard strip",
      climax: "cinematic reveal field replaces Run 2.9 dark framed hero card",
      close: "decision theater replaces Run 2.9 typographic field plus product card",
    }),
  );
}

function buildBadVisualSystemSourcesByRole(sourcesData) {
  const sources = sourcesData?.sources ?? [];
  return new Map([
    ["cover", sources.filter((source) => source.visual_system_direction?.includes("editorial")).slice(0, 1)],
    ["setup", sources.filter((source) => source.visual_system_direction?.includes("product")).slice(0, 1)],
    ["contrast", sources.filter((source) => source.visual_system_direction?.includes("proof")).slice(0, 1)],
    ["proof", sources.filter((source) => source.visual_system_direction?.includes("product")).slice(0, 1)],
    ["climax", sources.filter((source) => source.visual_system_direction?.includes("kinetic")).slice(0, 1)],
    ["close", sources.filter((source) => source.visual_system_direction?.includes("typographic")).slice(0, 1)],
  ]);
}

function loadRun210ContractData(arm) {
  const sources = readRun210JsonForArm(arm, RUN2_10_INPUTS.sources);
  const memory = readRun210JsonForArm(arm, RUN2_10_INPUTS.memory);
  const gateMatrix = readRun210JsonForArm(arm, RUN2_10_INPUTS.gateMatrix);
  const gateMatrixByRole = run210VisualSystemGateMatrixByRole(gateMatrix);
  const visualSystemSourcesByRole = run210VisualSystemSourcesByRole(sources, gateMatrix);
  const visualSystemsByRole = run210VisualSystemsByRole(memory);
  const codeModulesByRole = run210CodeModulesByRole(gateMatrix);
  const shapeBudgetByRole = run210ShapeBudgetByRole(gateMatrix);
  const visualDeltaByRole = run210VisualDeltaByRole();
  return {
    sources,
    memory,
    gateMatrix,
    gateMatrixByRole,
    visualSystemSourcesByRole,
    visualSystemsByRole,
    codeModulesByRole,
    shapeBudgetByRole,
    visualDeltaByRole,
    status: "run2_10_visual_contract_ready",
  };
}

function renderRun210Full(arm) {
  const contract = loadRun210ContractData(arm);
  return {
    ...contract,
    status: "run2_10_visual_contract_ready",
  };
}

function renderRun210FullSlide(presentation, spec, arm, n, fullData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);

  if (spec.role === "cover") {
    drawRun210EditorialTypeSystem(slide, arm, spec, null, metrics, {
      x: 82,
      y: 120,
      w: 760,
      h: 240,
      fontSize: 68,
      objectX: 944,
      objectY: 172,
      objectW: 160,
      objectH: 154,
    });
    drawRun210FullBleedVisualField(slide, arm, spec, null, metrics, {
      x: 76,
      y: 382,
      w: 1020,
      h: 176,
      headline: "sources -> memory -> code",
      note: "The visual system must change structure, not only palette or box count.",
      headlineSize: 28,
      railLabels: ["source", "memory", "gate"],
    });
  } else if (spec.role === "setup") {
    drawRun210ProductTheater(slide, arm, spec, null, metrics, {
      x: 596,
      y: 128,
      w: 496,
      h: 330,
      caption: "product theater replaces report setup",
    });
    drawRun210NonRectangularProofPath(slide, arm, spec, null, metrics, {
      x: 88,
      y: 382,
      caption: "the setup is a route, not a checklist",
    });
    text(slide, spec.title, 86, 126, 430, 96, {
      fontSize: 42,
      bold: true,
      title: true,
      color: arm.palette.title,
    });
    registerText(metrics, spec.title);
  } else if (spec.role === "contrast") {
    drawRun210FullBleedVisualField(slide, arm, spec, null, metrics, {
      x: 86,
      y: 122,
      w: 990,
      h: 448,
      headline: "Before: equal boxes. After: one visual route.",
      note: "This fails if the result is just the Run 2.9 field with new colors.",
      headlineSize: 42,
      railLabels: ["Run 2.9", "failure", "Run 2.10"],
    });
    drawRun210NonRectangularProofPath(slide, arm, spec, null, metrics, {
      x: 168,
      y: 372,
      nodes: [
        { label: "Run 2.9", x: 188, y: 438, r: 58, fill: C.white },
        { label: "gap", x: 486, y: 382, r: 72, fill: C.sky },
        { label: "2.10", x: 814, y: 444, r: 86, fill: arm.palette.accent },
      ],
      caption: "proof crosses the field instead of sitting in panels",
    });
  } else if (spec.role === "proof") {
    drawRun210ProductTheater(slide, arm, spec, null, metrics, {
      x: 86,
      y: 120,
      w: 560,
      h: 360,
      caption: "data binds to visual system code",
    });
    drawRun210KineticSequence(slide, arm, spec, null, metrics, {
      x: 666,
      y: 372,
      w: 444,
      h: 126,
      beats: [
        ["learn", 0.25],
        ["bind", 0.34],
        ["ship", 0.24],
      ],
    });
    text(slide, spec.title, 688, 134, 410, 82, {
      fontSize: 34,
      bold: true,
      title: true,
      color: arm.palette.title,
    });
    registerText(metrics, spec.title);
  } else if (spec.role === "climax") {
    drawRun210CinematicClimax(slide, arm, spec, null, metrics);
    drawRun210KineticSequence(slide, arm, spec, null, metrics, {
      x: 236,
      y: 530,
      w: 720,
      h: 78,
      beats: [
        ["scale", 0.34],
        ["proof", 0.28],
      ],
    });
  } else {
    drawRun210EditorialTypeSystem(slide, arm, spec, null, metrics, {
      x: 76,
      y: 116,
      w: 650,
      h: 198,
      fontSize: 56,
      claimW: 470,
      objectX: 968,
      objectY: 128,
      objectW: 142,
      objectH: 130,
    });
    drawRun210ProductTheater(slide, arm, spec, null, metrics, {
      x: 560,
      y: 350,
      w: 460,
      h: 178,
      caption: "release stays gated",
    });
  }

  proofFooter(slide, spec, arm);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function renderControlSlide(presentation, spec, arm, n, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const mode = arm.armId === "bad_visual_system_memory" ? "bad" : arm.armId === "run1_5_skill" ? "run1_5" : "prompt";
  drawDenseControl(slide, arm, spec, metrics, mode);
  drawControlGate(slide, arm, spec, metrics, {
    x: spec.role === "climax" ? 1024 : 902,
    y: spec.role === "close" ? 326 : spec.role === "climax" ? 492 : 438,
    w: spec.role === "close" ? 226 : spec.role === "climax" ? 176 : 208,
    h: spec.role === "climax" ? 92 : 118,
    headline: arm.armId === "bad_visual_system_memory" ? "primitive only" : "public blocked",
    line: arm.armId === "bad_visual_system_memory" ? "no module/gate read" : "no Run 2.10 visual trace",
  });
  proofFooter(slide, spec, arm);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertArmInputBoundaries(arm);
  const fullRun210 = arm.armId === "run2_10_full_skill";
  const fullData = fullRun210 ? context.fullData ?? renderRun210Full(arm) : null;
  const gateByRole = fullData?.gateMatrixByRole ?? new Map();
  const visualSystemSourcesByRole = fullData?.visualSystemSourcesByRole ?? new Map();
  const visualSystemsByRole = fullData?.visualSystemsByRole ?? new Map();
  const codeModulesByRole = fullData?.codeModulesByRole ?? new Map();
  const budgetByRole = fullData?.shapeBudgetByRole ?? new Map();
  const visualDeltaByRole = fullData?.visualDeltaByRole ?? new Map();
  const badVisualSystemSourcesByRole = context.badVisualSystemSourcesByRole ?? new Map();
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics =
    fullRun210 && arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    commercial_case: `${pack}/commercial_case.md`,
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.10 visual-system arm-specific generation from scripts/generate_ppt_run2_10_visual_system_arms.mjs",
      no_cross_arm_reuse: ["cached memory summaries", "generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes", "visual module carryover"],
    },
    model_provider: "Codex local code generation with artifact-tool native presentation primitives",
    tool_versions: {
      artifact_tool: "bundled @oai/artifact-tool via presentations skill",
      node: "codex primary runtime",
      python: "workspace runtime for contact sheet and layout QA",
    },
    release_decision: arm.release,
    slides: arm.slides.map((slide, index) => {
      const gate = gateByRole.get(slide.role);
      const roleSources = visualSystemSourcesByRole.get(slide.role) ?? [];
      const roleSystems = visualSystemsByRole.get(slide.role) ?? [];
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const actualCodeModuleIds = Array.from(roleMetrics.visualModuleIds);
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_10_contract_status: fullRun210
          ? hasRenderedMetrics
            ? "full_arm_native_generator_rendered"
            : "full_arm_contract_preview_not_rendered"
          : "boundary_control_not_run2_10_full",
        run2_10_visual_system_source_ids: fullRun210
          ? gate?.visual_system_source_ids ?? roleSources.map((source) => source.id)
          : [],
        run2_10_visual_system_memory_ids: fullRun210
          ? gate?.visual_system_memory_ids ?? roleSystems.map((visualSystem) => visualSystem.visual_system_id)
          : [],
        run2_10_gate_matrix_ids: fullRun210 ? (gate ? [gate.id] : []) : [],
        run2_10_required_code_module_ids: fullRun210 ? gate?.required_code_modules ?? codeModulesByRole.get(slide.role) ?? [] : [],
        run2_10_code_module_ids: fullRun210
          ? hasRenderedMetrics
            ? actualCodeModuleIds
            : gate?.required_code_modules ?? codeModulesByRole.get(slide.role) ?? []
          : [],
        run2_10_visual_delta_from_run2_9: fullRun210 ? gate?.visual_delta_from_run2_9 ?? visualDeltaByRole.get(slide.role) ?? "" : "",
        run2_10_sameness_failure_probe: fullRun210 ? gate?.sameness_failure_probe ?? "" : "",
        run2_10_public_demo_first_read_probe: fullRun210 ? gate?.public_demo_first_read_probe ?? "" : "",
        run2_10_shape_count_budget: fullRun210 ? gate?.shape_count_budget ?? budgetByRole.get(slide.role) ?? {} : {},
        run2_10_asymmetry_whitespace_rule: fullRun210 ? gate?.asymmetry_whitespace_rule ?? "" : "",
        run2_10_trace_origin: hasRenderedMetrics ? "actual_native_visual_module_calls" : fullRun210 ? "contract_preview_required_visual_modules" : "boundary_control",
        negative_control_visual_system_source_ids:
          arm.armId === "bad_visual_system_memory" ? (badVisualSystemSourcesByRole.get(slide.role) ?? []).map((source) => source.id) : [],
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
        layout_budget_status:
          fullRun210 && hasRenderedMetrics
            ? evaluateBudget(budgetByRole.get(slide.role) ?? {}, roleMetrics)
            : {
                within_budget: true,
                violations: [],
              },
      };
    }),
  };
}

function evaluateBudget(layoutBudget, metrics) {
  const violations = [];
  if (typeof layoutBudget.max_text_boxes === "number" && metrics.textBoxCount > layoutBudget.max_text_boxes) {
    violations.push(`text boxes ${metrics.textBoxCount} > ${layoutBudget.max_text_boxes}`);
  }
  if (typeof layoutBudget.max_visible_words === "number" && metrics.visibleWords > layoutBudget.max_visible_words) {
    violations.push(`visible words ${metrics.visibleWords} > ${layoutBudget.max_visible_words}`);
  }
  if (typeof layoutBudget.max_proof_objects === "number" && metrics.proofObjects > layoutBudget.max_proof_objects) {
    violations.push(`proof objects ${metrics.proofObjects} > ${layoutBudget.max_proof_objects}`);
  }
  if (typeof layoutBudget.max_zones === "number" && metrics.zones > layoutBudget.max_zones) {
    violations.push(`zones ${metrics.zones} > ${layoutBudget.max_zones}`);
  }
  if (typeof layoutBudget.max_workflow_objects === "number" && metrics.workflowObjects > layoutBudget.max_workflow_objects) {
    violations.push(`workflow objects ${metrics.workflowObjects} > ${layoutBudget.max_workflow_objects}`);
  }
  if (typeof layoutBudget.max_delta_panels === "number" && metrics.deltaPanels > layoutBudget.max_delta_panels) {
    violations.push(`delta panels ${metrics.deltaPanels} > ${layoutBudget.max_delta_panels}`);
  }
  if (typeof layoutBudget.max_gate_objects === "number" && metrics.gateObjects > layoutBudget.max_gate_objects) {
    violations.push(`gate objects ${metrics.gateObjects} > ${layoutBudget.max_gate_objects}`);
  }
  if (typeof layoutBudget.max_hero_objects === "number" && (metrics.heroBindingId ? 1 : 0) > layoutBudget.max_hero_objects) {
    violations.push(`hero objects 1 > ${layoutBudget.max_hero_objects}`);
  }
  if (typeof layoutBudget.hero_object_canvas_share_min === "number" && metrics.heroShare < layoutBudget.hero_object_canvas_share_min) {
    violations.push(`hero share ${metrics.heroShare.toFixed(3)} < ${layoutBudget.hero_object_canvas_share_min}`);
  }
  if (typeof layoutBudget.hero_object_canvas_share_max === "number" && metrics.heroShare > layoutBudget.hero_object_canvas_share_max) {
    violations.push(`hero share ${metrics.heroShare.toFixed(3)} > ${layoutBudget.hero_object_canvas_share_max}`);
  }
  return {
    within_budget: violations.length === 0,
    violations,
  };
}

function assertRun210VisualSystemGateSelfCheck(trace) {
  if (trace.arm_id !== "run2_10_full_skill") return;
  for (const slide of trace.slides) {
    if (slide.run2_10_contract_status !== "full_arm_native_generator_rendered") {
      throw new Error(`Run 2.10 full slide ${slide.slide_id} was not rendered with native module metrics`);
    }
    for (const field of EXPECTED_RUN2_10_TRACE_FIELDS) {
      const value = slide[field];
      const empty =
        value == null ||
        (Array.isArray(value) && value.length === 0) ||
        (typeof value === "string" && value.trim() === "") ||
        (typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === 0);
      if (empty) throw new Error(`Run 2.10 full slide ${slide.slide_id} missing ${field}`);
    }
    if (!slide.layout_budget_status?.within_budget) {
      throw new Error(`Run 2.10 full slide ${slide.slide_id} exceeded layout budget: ${slide.layout_budget_status.violations.join("; ")}`);
    }
    const actualCodeModules = new Set(slide.run2_10_code_module_ids ?? []);
    for (const requiredCodeModule of slide.run2_10_required_code_module_ids ?? []) {
      if (!actualCodeModules.has(requiredCodeModule)) {
        throw new Error(`Run 2.10 full slide ${slide.slide_id} did not call required module ${requiredCodeModule}`);
      }
    }
    if (slide.role === "climax") {
      if (!actualCodeModules.has("drawRun210CinematicClimax")) {
        throw new Error("Run 2.10 climax did not call drawRun210CinematicClimax");
      }
      const share = slide.layout_metrics?.hero_object_canvas_share ?? 0;
      if (!share) throw new Error("Run 2.10 climax missing hero object share");
    }
  }
}

function buildArmContract() {
  return armSpecs.map((arm) => ({
    armId: arm.armId,
    label: arm.label,
    contract_status:
      arm.armId === "run2_10_full_skill"
        ? "run2_10_visual_contract_ready_requires_render_metrics"
        : "run2_10_boundary_control_contract_ready",
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

function buildRun210FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  return buildNamedContactSheet(path.join(outRoot, "run2-10-four-arm-contact-sheet.png"), "Run 2.10 four-arm comparison", sheets, sheets.length);
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
      "required proof objects: editorial type system, full-bleed visual field, product theater, non-rectangular proof path, kinetic sequence, cinematic climax",
      "source requirements: commercial case always; bad control may read Run 2.10 visual-system sources only; full arm additionally requires visual-system memory and gate matrix",
      "brand authenticity constraints: no copied source visuals, no borrowed brand chrome, no screenshots or media surfaces",
      "profile-specific QA gates: contact-sheet coherence, editable native text/shapes only, layout geometry pass, release gate visibly blocked",
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
  let badVisualSystemSourcesByRole = new Map();
  if (arm.armId === "run2_10_full_skill") {
    fullData = loadRun210ContractData(arm);
  } else if (arm.armId === "bad_visual_system_memory") {
    badVisualSystemSourcesByRole = buildBadVisualSystemSourcesByRole(readRun210SourcesForArm(arm));
  }

  const slides = arm.slides.map((slide, index) =>
    arm.armId === "run2_10_full_skill"
      ? renderRun210FullSlide(presentation, slide, arm, index + 1, fullData, metricsByRole)
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

  const trace = traceFor(arm, { fullData, badVisualSystemSourcesByRole, metricsByRole });
  assertRun210VisualSystemGateSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_10_visual_system_arms.mjs",
      exportName: `slide${String(index + 1).padStart(2, "0")}`,
    })),
  };
  writeJson(path.join(workspace, "output", "artifact-build-manifest.json"), manifest);
  writeJson(path.join(workspace, "qa", "build_manifest_stdout.json"), manifest);
  writeJson(path.join(workspace, "trace_manifest.json"), trace);
  return { workspace, outputPath, contactSheet, previewPaths };
}

async function main() {
  ensureDir(outRoot);
  const built = [];
  for (const arm of armSpecs) {
    built.push(await buildArm(arm));
  }
  const fourArmSheet = buildRun210FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_10_visual_system_four_arms",
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_10_visual_system_summary.json"), runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  EXPECTED_RUN2_10_TRACE_FIELDS,
  RUN2_10_INPUTS,
  RUN2_10_RESTRICTED_INPUTS,
  armSpecs,
  assertRun210VisualSystemGateSelfCheck,
  buildArmContract,
  drawRun210CinematicClimax,
  drawRun210FullBleedVisualField,
  drawRun210ProductTheater,
  drawRun210NonRectangularProofPath,
  drawRun210KineticSequence,
  drawRun210EditorialTypeSystem,
  main,
  registerRun210VisualModule,
  registerVisualModule,
  renderRun210Full,
  run210CodeModulesByRole,
  run210ShapeBudgetByRole,
  run210VisualSystemSourcesById,
  run210VisualSystemSourcesByRole,
  run210VisualDeltaByRole,
  run210VisualSystemGateMatrixByRole,
  run210VisualSystemsById,
  run210VisualSystemsByRole,
  traceFor,
};
