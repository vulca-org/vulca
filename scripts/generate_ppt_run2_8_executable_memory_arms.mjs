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
  ink: "#15171c",
  paper: "#f7f4ed",
  white: "#ffffff",
  line: "#d3cdc0",
  muted: "#64707a",
  deep: "#111a23",
  slate: "#23303f",
  blue: "#2a63da",
  sky: "#dce7ff",
  mint: "#ddefe8",
  green: "#0d8d68",
  coral: "#d95e49",
  amber: "#d79b2f",
  sand: "#efe6d8",
  khaki: "#d6c8a1",
  olive: "#7c6e3f",
  plum: "#725f97",
  fog: "#edf1f4",
  steel: "#c9d0d7",
};

const EXPECTED_RUN2_8_TRACE_FIELDS = [
  "run2_8_decomposition_unit_ids",
  "run2_8_memory_binding_ids",
  "run2_8_gate_matrix_ids",
  "run2_8_code_binding_ids",
  "run2_8_layout_budget",
  "run2_8_visual_delta_from_run2_7",
];

const RUN2_8_INPUTS = {
  decomposition: `${pack}/run2_8_tutorial_decomposition.json`,
  memory: `${pack}/run2_8_executable_design_memory.json`,
  gateMatrix: `${pack}/run2_8_workflow_gate_matrix.json`,
};
const RUN2_8_RESTRICTED_INPUTS = Object.values(RUN2_8_INPUTS);

const baseSlides = [
  {
    role: "cover",
    title: "Executable memory makes the opening sparse.",
    claim: "The generator selects memory before code and keeps one native product surface in view.",
    trace: "commercial_case + run2_8_decomposition + memory + gate",
  },
  {
    role: "setup",
    title: "Type, spacing, and memory are chosen before drawing.",
    claim: "The route exposes selected rules before any native PPT module is called.",
    trace: "selected bindings before native module execution",
  },
  {
    role: "contrast",
    title: "The delta is visible, not described.",
    claim: "A dense before state is routed into one cleaner native after state.",
    trace: "before-after delta bound to executable memory",
  },
  {
    role: "proof",
    title: "Data flows into memory, gate, and native PPT.",
    claim: "The proof slide shows the explicit generator chain with editable diagram primitives.",
    trace: "data -> memory -> gate -> native PPT",
  },
  {
    role: "climax",
    title: "One hero object carries the proof.",
    claim: "The climax binds to a dominant native object before secondary explanation appears.",
    trace: "binding_climax_hero_object + gate_2_8_climax",
  },
  {
    role: "close",
    title: "Release stays blocked until the next workflow loop.",
    claim: "The final slide keeps the public gate explicit and points back into the memory-selection loop.",
    trace: "public_blocked workflow gate remains visible",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-8-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.8 / CONTROL",
    footer: "prompt_only | commercial_case only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [
      `${pack}/run2_8_tutorial_decomposition.json`,
      `${pack}/run2_8_executable_design_memory.json`,
      `${pack}/run2_8_workflow_gate_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "docs/product/ppt-run1-5-product-lab/",
    ],
    palette: {
      bg: "#f5f6f8",
      rail: "#394456",
      accent: C.blue,
      accent2: C.plum,
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: C.line,
      gate: "#e9edf3",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "The prompt can ask for clarity.",
        "The setup can name good behavior.",
        "The contrast can request a delta.",
        "The proof can describe a route.",
        "The climax can reserve a slot.",
        "The close can keep release blocked.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-8-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.8 / RUN 1.5",
    footer: "run1_5_skill | prior workflow baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [
      `${pack}/run2_8_tutorial_decomposition.json`,
      `${pack}/run2_8_executable_design_memory.json`,
      `${pack}/run2_8_workflow_gate_matrix.json`,
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
        "A stronger baseline still lacks Run 2.8 memory.",
        "The setup remains evidence-heavy.",
        "The contrast improves words before structure.",
        "The proof shows workflow, not executable binding.",
        "The climax stays smaller than the system needs.",
        "The close is useful but not contract-complete.",
      ][index],
    })),
  },
  {
    armId: "run2_8_full_skill",
    slug: "ppt-run2-8-full-vulca",
    label: "Run 2.8 full Vulca skill",
    kicker: "RUN 2.8 / FULL VULCA",
    footer: "run2_8_full_skill | decomposition + executable memory + gate matrix | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/sources.json`,
      `${pack}/run2_8_tutorial_decomposition.json`,
      `${pack}/run2_8_executable_design_memory.json`,
      `${pack}/run2_8_workflow_gate_matrix.json`,
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
      bg: "#f7f4ee",
      rail: "#131b23",
      accent: "#1f2f3d",
      accent2: "#92a5ad",
      proof: "#e24d30",
      panel: C.white,
      title: "#10161b",
      muted: "#5e6b73",
      rule: "#d7d1c6",
      gate: "#182129",
    },
    slides: baseSlides,
  },
  {
    armId: "bad_memory_schema",
    slug: "ppt-run2-8-bad-memory-schema",
    label: "Bad memory-schema boundary control",
    kicker: "RUN 2.8 / NEGATIVE CONTROL",
    footer: "bad_memory_schema | decomposition only | internal comparison",
    release: "internal_only",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/run2_8_tutorial_decomposition.json`,
      `${pack}/sources.json`,
    ],
    forbidden: [
      `${pack}/run2_8_executable_design_memory.json`,
      `${pack}/run2_8_workflow_gate_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "manual Run 2.8 memory repair before scoring",
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
        "Decomposition alone does not bind the layout.",
        "The setup crowds the route instead of choosing.",
        "The delta weakens into equal panels.",
        "The proof names steps without executable gate control.",
        "The climax loses the hero field.",
        "The close lists checks without a credible gate.",
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
  text(slide, arm.footer, 660, 674, 564, 22, {
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
  text(slide, `trace: ${spec.trace}`, 66, 628, 860, 28, {
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

function drawRun28TypeScale(slide, arm, spec, binding, metrics, opts = {}) {
  registerNativeModule(metrics, "drawRun28TypeScale");
  const params = binding?.code_binding?.params ?? {};
  const titleSize = opts.titleSize ?? Math.max(40, params.title_min_pt ?? params.fontSize ?? 40);
  const bodySize = opts.bodySize ?? Math.max(18, params.body_min_pt ?? 18);
  moduleLabel(slide, opts.labelX ?? 76, opts.labelY ?? 102, `type ${binding?.design_token ?? "manual"}`, arm);
  text(slide, spec.title, opts.titleX ?? 76, opts.titleY ?? 144, opts.titleW ?? 560, opts.titleH ?? 136, {
    fontSize: titleSize,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, spec.claim, opts.claimX ?? 80, opts.claimY ?? 308, opts.claimW ?? 500, opts.claimH ?? 66, {
    fontSize: bodySize,
    color: arm.palette.muted,
  });
  registerText(metrics, spec.claim);
}

function drawRun28SpacingZones(slide, arm, role, binding, metrics, opts = {}) {
  registerNativeModule(metrics, "drawRun28SpacingZones");
  const dense = Boolean(opts.dense);
  const fill = opts.fill ?? arm.palette.panel;
  const x = opts.x ?? 664;
  const y = opts.y ?? 130;
  const w = opts.w ?? 486;
  const h = opts.h ?? 364;
  const gutter = dense ? 16 : 22;
  const zones = dense ? 4 : Math.min(4, opts.zones ?? 3);
  const widths = dense ? [0.24, 0.24, 0.24, 0.24] : zones === 3 ? [0.42, 0.24, 0.22] : [0.46, 0.46];
  moduleLabel(slide, x, y - 36, `space ${binding?.design_token ?? role}`, arm);
  rect(slide, x, y, w, h, fill, colorLine(arm.palette.rule ?? C.line, 1));
  let cursor = x + 22;
  const zoneTop = y + Math.max(18, Math.round(h * 0.12));
  const zoneH = Math.max(26, h - (dense ? 54 : 70));
  widths.slice(0, zones).forEach((ratio, index) => {
    const zoneW = Math.round((w - 44 - gutter * (zones - 1)) * ratio);
    const zoneY = zoneTop + (index % 2 === 1 && !dense ? Math.min(16, Math.round(zoneH * 0.1)) : 0);
    rect(slide, cursor, zoneY, zoneW, zoneH, dense ? "#f1ead7" : index === 0 ? C.deep : "#eef2f5", colorLine(dense ? arm.palette.rule : index === 0 ? C.deep : "#cad1d8", 1));
    if (dense) {
      const rowCount = h < 170 ? 2 : 4;
      const rowStep = Math.max(22, Math.floor((zoneH - 18) / rowCount));
      for (let row = 0; row < rowCount; row += 1) {
        rect(slide, cursor + 12, zoneY + 14 + row * rowStep, Math.max(18, zoneW - 24), Math.min(28, rowStep - 7), row % 2 ? arm.palette.accent2 : "#e5dcc2", colorLine(arm.palette.rule, 1));
      }
    } else if (index === 0) {
      const heroH = Math.max(24, Math.round(zoneH * 0.52));
      rect(slide, cursor + 20, zoneY + 22, Math.max(24, zoneW - 40), heroH, arm.palette.accent, colorLine(arm.palette.accent, 1));
      rect(slide, cursor + 20, zoneY + 34 + heroH, Math.max(24, zoneW - 96), Math.min(12, Math.max(6, Math.round(zoneH * 0.05))), arm.palette.accent2);
      rect(slide, cursor + 20, zoneY + 58 + heroH, Math.max(20, zoneW - 128), Math.min(8, Math.max(5, Math.round(zoneH * 0.04))), "#b9c4cb");
    } else {
      rect(slide, cursor + 18, zoneY + 24, Math.max(24, zoneW - 36), Math.min(14, Math.max(7, Math.round(zoneH * 0.08))), arm.palette.accent2);
      rect(slide, cursor + 18, zoneY + Math.round(zoneH * 0.32), Math.max(24, zoneW - 50), 9, "#b9c4cb");
      rect(slide, cursor + 18, zoneY + Math.round(zoneH * 0.46), Math.max(24, zoneW - 74), 9, "#b9c4cb");
      rect(slide, cursor + 18, zoneY + Math.round(zoneH * 0.62), Math.max(24, zoneW - 36), Math.max(22, Math.round(zoneH * 0.24)), C.white, colorLine("#d4dbe0", 1));
    }
    cursor += zoneW + gutter;
  });
  registerZones(metrics, zones);
  registerProof(metrics, dense ? 0 : 1);
}

function drawRun28BeforeAfterDelta(slide, arm, role, binding, metrics, opts = {}) {
  registerNativeModule(metrics, "drawRun28BeforeAfterDelta");
  const bad = Boolean(opts.bad);
  const x = opts.x ?? 84;
  const y = opts.y ?? 286;
  const w = opts.w ?? 988;
  const h = opts.h ?? 258;
  const gap = 34;
  const panelW = Math.floor((w - gap) / 2);
  const rightX = x + panelW + gap;
  moduleLabel(slide, x, y - 40, `delta ${binding?.design_token ?? role}`, arm);
  rect(slide, x, y, panelW, h, bad ? "#efe6cf" : "#eef2f4", colorLine("#cfd6dc", 1));
  rect(slide, rightX, y, panelW, h, C.white, colorLine(bad ? arm.palette.rule : arm.palette.accent, bad ? 1 : 2));
  text(slide, "before", x + 22, y + 18, 120, 18, { fontSize: 10, bold: true, mono: true, color: arm.palette.muted });
  text(slide, "after", rightX + 22, y + 18, 120, 18, { fontSize: 10, bold: true, mono: true, color: bad ? arm.palette.muted : arm.palette.accent });
  registerText(metrics, "before");
  registerText(metrics, "after");
  const cellW = Math.max(20, Math.min(72, (panelW - 54) / 3));
  const cellH = Math.max(12, Math.min(30, (h - 92) / 3));
  const cellStepX = Math.max(cellW + 10, (panelW - 52) / 3);
  const cellStepY = Math.max(cellH + 8, (h - 80) / 3);
  for (let row = 0; row < 3; row += 1) {
    for (let col = 0; col < 3; col += 1) {
      rect(slide, x + 24 + col * cellStepX, y + 56 + row * cellStepY, cellW, cellH, "#dde2e6", colorLine("#ccd3d8", 1));
    }
  }
  if (bad) {
    for (let row = 0; row < 3; row += 1) {
      for (let col = 0; col < 3; col += 1) {
        rect(slide, rightX + 24 + col * cellStepX, y + 56 + row * cellStepY, cellW, cellH, row === 1 ? arm.palette.accent2 : "#e5dcc2", colorLine(arm.palette.rule, 1));
      }
    }
  } else {
    const heroW = Math.max(34, Math.min(206, Math.round(panelW * 0.45)));
    const heroH = Math.max(34, Math.min(126, h - 86));
    const heroX = rightX + Math.max(20, Math.round(panelW * 0.1));
    const heroY = y + 58;
    const barX = rightX + Math.min(panelW - 86, Math.round(panelW * 0.62));
    rect(slide, heroX, heroY, heroW, heroH, arm.palette.accent, colorLine(arm.palette.accent, 1));
    rect(slide, barX, y + 68, Math.max(34, Math.min(128, panelW - (barX - rightX) - 24)), 14, arm.palette.accent2);
    rect(slide, barX, y + 102, Math.max(34, Math.min(174, panelW - (barX - rightX) - 24)), 9, "#c1ccd1");
    rect(slide, barX, y + 132, Math.max(30, Math.min(112, panelW - (barX - rightX) - 24)), 9, "#c1ccd1");
    registerProof(metrics, 1);
  }
  rect(slide, x + panelW - 8, y + h / 2 - 6, 46, 12, arm.palette.accent);
  rect(slide, x + panelW + 22, y + h / 2 - 26, 18, 52, arm.palette.accent);
  text(slide, bad ? "weak delta" : "visible delta", x + panelW - 60, y + h - 34, 156, 18, {
    fontSize: 10,
    bold: true,
    mono: true,
    color: bad ? arm.palette.muted : arm.palette.accent,
    align: "center",
  });
  registerText(metrics, bad ? "weak delta" : "visible delta");
  registerDeltaPanels(metrics, 2);
}

function drawRun28WorkflowGate(slide, arm, role, binding, metrics, opts = {}) {
  registerNativeModule(metrics, "drawRun28WorkflowGate");
  const x = opts.x ?? 974;
  const y = opts.y ?? 286;
  const w = opts.w ?? 194;
  const h = opts.h ?? 182;
  const dark = opts.dark ?? arm.armId === "run2_8_full_skill";
  const bg = dark ? arm.palette.gate : arm.palette.gate;
  const fg = dark ? C.white : arm.palette.title;
  moduleLabel(slide, x, y - 36, `gate ${binding?.design_token ?? role}`, arm);
  rect(slide, x, y, w, h, bg, colorLine(dark ? bg : arm.palette.rule, 1));
  text(slide, "public gate", x + 18, y + 18, w - 36, 18, { fontSize: 9, bold: true, mono: true, color: dark ? "#d6ecec" : arm.palette.accent });
  text(slide, opts.headline ?? "release blocked", x + 18, y + 44, w - 36, 40, { fontSize: 17, bold: true, title: true, color: fg });
  text(slide, opts.line1 ?? "native trace required", x + 18, y + 98, w - 36, 20, { fontSize: 10, mono: true, color: dark ? "#d6ecec" : arm.palette.muted });
  text(slide, opts.line2 ?? "human review required", x + 18, y + 126, w - 36, 20, { fontSize: 10, mono: true, color: dark ? "#d6ecec" : arm.palette.muted });
  registerText(metrics, `public gate ${opts.headline ?? "release blocked"}`);
  registerText(metrics, `${opts.line1 ?? "native trace required"} ${opts.line2 ?? "human review required"}`);
  registerGate(metrics, opts.gateObjects ?? 1);
}

function drawRun28Climax(slide, binding, arm, spec, metrics, opts = {}) {
  registerNativeModule(metrics, "drawRun28Climax");
  if (!binding?.id || !binding?.code_binding?.function_name) {
    throw new Error("Run 2.8 climax requires binding_climax_hero_object with code_binding.function_name");
  }
  rect(slide, MAIN_CANVAS.x, MAIN_CANVAS.y, MAIN_CANVAS.w, MAIN_CANVAS.h, arm.palette.bg, colorLine(arm.palette.rule, 1));
  drawRun28TypeScale(
    slide,
    arm,
    {
      ...spec,
      claim: opts.claim ?? "The hero field is selected before labels, workflow notes, and release status.",
    },
    opts.typeBinding,
    metrics,
    {
      labelX: 84,
      labelY: 100,
      titleX: 84,
      titleY: 140,
      titleW: 342,
      titleH: 154,
      titleSize: 44,
      claimX: 88,
      claimY: 318,
      claimW: 324,
      claimH: 58,
      bodySize: 15,
    },
  );
  const heroX = 474;
  const heroY = 120;
  const heroW = 600;
  const heroH = 470;
  rect(slide, heroX, heroY, heroW, heroH, C.white, colorLine(arm.palette.proof ?? arm.palette.accent, 3));
  rect(slide, heroX + 44, heroY + 54, 334, 312, arm.palette.proof ?? arm.palette.accent, colorLine(arm.palette.proof ?? arm.palette.accent, 1));
  rect(slide, heroX + 84, heroY + 94, 178, 170, "#122b25", colorLine("#122b25", 1));
  rect(slide, heroX + 406, heroY + 78, 124, 16, arm.palette.accent2);
  rect(slide, heroX + 406, heroY + 124, 144, 10, "#c4ced2");
  rect(slide, heroX + 406, heroY + 156, 96, 10, "#c4ced2");
  text(slide, "hero object", heroX + 42, heroY + 24, 136, 18, {
    fontSize: 9,
    bold: true,
    mono: true,
    color: arm.palette.proof ?? arm.palette.accent,
  });
  text(slide, "one bound native proof object", heroX + 44, heroY + heroH - 70, heroW - 88, 32, {
    fontSize: 24,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, "one bound native proof object");
  rect(slide, 88, 398, 312, 128, "#eef2f5", colorLine("#cfd6dc", 1));
  text(slide, binding.id, 108, 420, 272, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.accent });
  text(slide, "pause first, support second", 108, 458, 220, 24, { fontSize: 13, bold: true, title: true, color: arm.palette.title });
  registerProof(metrics, 1);
  registerHero(metrics, binding.id, heroX, heroY, heroW, heroH);
  return {
    role: "climax",
    hero_binding_id: binding.id,
    function_name: binding.code_binding.function_name,
    hero_share: metrics.heroShare,
  };
}

function drawDenseControl(slide, arm, spec, metrics, mode = "prompt") {
  const titleSize = mode === "bad" ? 34 : 38;
  text(slide, spec.title, 76, 132, 520, 92, {
    fontSize: titleSize,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, spec.claim, 80, 240, 500, 62, { fontSize: 16, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  if (spec.role === "cover") {
    rect(slide, 720, 130, 400, 280, mode === "bad" ? "#eadfbe" : C.deep, colorLine(mode === "bad" ? arm.palette.rule : C.deep, 1));
    if (mode === "bad") {
      for (let row = 0; row < 4; row += 1) {
        for (let col = 0; col < 4; col += 1) {
          rect(slide, 744 + col * 88, 164 + row * 46, 60, 28, row % 2 ? arm.palette.accent2 : "#dfd0a7", colorLine(arm.palette.rule, 1));
        }
      }
    } else {
      rect(slide, 756, 180, 180, 118, arm.palette.accent);
      rect(slide, 970, 190, 104, 12, arm.palette.accent2);
      rect(slide, 970, 228, 130, 8, "#bbc5cc");
      rect(slide, 970, 256, 84, 8, "#bbc5cc");
    }
  } else if (spec.role === "contrast") {
    drawRun28BeforeAfterDelta(slide, arm, spec.role, null, metrics, { x: 86, y: 342, w: 1000, h: 206, bad: mode === "bad" });
  } else if (spec.role === "climax") {
    rect(slide, 84, 302, 988, 228, arm.palette.panel, colorLine(arm.palette.rule, 1));
    for (let col = 0; col < 3; col += 1) {
      rect(slide, 110 + col * 308, 336, 250, 136, mode === "bad" ? "#efe4c8" : C.white, colorLine(arm.palette.rule, 1));
      text(slide, ["brief", "baseline", "result"][col], 128 + col * 308, 356, 210, 20, { fontSize: 9, bold: true, mono: true, color: arm.palette.accent });
      registerText(metrics, ["brief", "baseline", "result"][col]);
      text(slide, mode === "bad" ? "equal panels stay equal" : "reserved slot, not a hero field", 128 + col * 308, 396, 210, 42, { fontSize: 14, bold: true, title: true, color: arm.palette.title });
      registerText(metrics, mode === "bad" ? "equal panels stay equal" : "reserved slot, not a hero field");
    }
  } else if (spec.role === "proof") {
    const labels = mode === "bad" ? ["data", "notes", "route", "checks", "more"] : ["brief", "workflow", "native", "gate", "review"];
    labels.forEach((label, index) => {
      rect(slide, 84 + index * 194, 330 + (index % 2) * 74, 154, 58, mode === "bad" ? "#efe4c8" : C.white, colorLine(arm.palette.rule, 1));
      text(slide, label, 102 + index * 194, 348 + (index % 2) * 74, 118, 18, { fontSize: 10, bold: true, mono: true, color: arm.palette.accent });
      registerText(metrics, label);
    });
  } else {
    const cards = mode === "bad" ? 4 : 3;
    for (let i = 0; i < cards; i += 1) {
      rect(slide, 680 + i * (mode === "bad" ? 120 : 150), 314, mode === "bad" ? 104 : 132, 144, mode === "bad" ? "#efe4c8" : C.white, colorLine(arm.palette.rule, 1));
      rect(slide, 690 + i * (mode === "bad" ? 120 : 150), 332, mode === "bad" ? 84 : 108, 12, arm.palette.accent2);
      rect(slide, 690 + i * (mode === "bad" ? 120 : 150), 368, mode === "bad" ? 72 : 88, 9, "#c0c9d0");
      rect(slide, 690 + i * (mode === "bad" ? 120 : 150), 396, mode === "bad" ? 64 : 74, 9, "#c0c9d0");
    }
    rect(slide, 84, 328, 484, 202, mode === "bad" ? "#efe4c8" : C.white, colorLine(arm.palette.rule, 1));
    text(slide, mode === "bad" ? "dense explanation replaces strong selection." : "A valid control can stay readable and still lack bound memory.", 108, 364, 424, 84, {
      fontSize: mode === "bad" ? 18 : 20,
      bold: true,
      title: true,
      color: arm.palette.title,
    });
    registerText(metrics, mode === "bad" ? "dense explanation replaces strong selection." : "A valid control can stay readable and still lack bound memory.");
  }
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

  if (arm.armId === "run2_8_full_skill") {
    for (const input of RUN2_8_RESTRICTED_INPUTS) assertAllowed(input);
    return;
  }
  if (arm.armId === "bad_memory_schema") {
    assertAllowed(RUN2_8_INPUTS.decomposition);
    assertForbidden(RUN2_8_INPUTS.memory);
    assertForbidden(RUN2_8_INPUTS.gateMatrix);
    return;
  }
  for (const input of RUN2_8_RESTRICTED_INPUTS) assertForbidden(input);
}

function readRun28JsonForArm(arm, relPath) {
  assertArmInputBoundaries(arm);
  if (arm.armId !== "run2_8_full_skill") {
    throw new Error(`${arm.armId} cannot read Run 2.8 executable-memory input: ${relPath}`);
  }
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  return readJson(relPath);
}

function readRun28DecompositionForArm(arm) {
  assertArmInputBoundaries(arm);
  if (!arm.allowed.includes(RUN2_8_INPUTS.decomposition) || arm.forbidden.includes(RUN2_8_INPUTS.decomposition)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${RUN2_8_INPUTS.decomposition}`);
  }
  return readJson(RUN2_8_INPUTS.decomposition);
}

function run28GateMatrixByRole(gateMatrix) {
  return new Map((gateMatrix?.gates ?? []).map((gate) => [gate.slide_role, gate]));
}

function run28DecompositionByRole(decomposition, gateMatrix) {
  const unitsById = new Map((decomposition?.units ?? []).map((unit) => [unit.id, unit]));
  const map = new Map();
  for (const gate of gateMatrix?.gates ?? []) {
    map.set(
      gate.slide_role,
      gate.decomposition_unit_ids.map((id) => unitsById.get(id)).filter(Boolean),
    );
  }
  return map;
}

function run28MemoryBindingsByRole(memory) {
  const bindingsByRole = new Map();
  for (const binding of memory.bindings) {
    for (const role of binding.applies_to_slide_roles) {
      const bucket = bindingsByRole.get(role) ?? [];
      bucket.push(binding);
      bindingsByRole.set(role, bucket);
    }
  }
  return bindingsByRole;
}

function run28CodeBindingsByRole(memoryBindingsByRole) {
  const map = new Map();
  for (const [role, bindings] of memoryBindingsByRole.entries()) {
    map.set(
      role,
      bindings.map((binding) => binding.code_binding?.function_name).filter(Boolean),
    );
  }
  return map;
}

function run28LayoutBudgetByRole(gateMatrix) {
  const map = new Map();
  for (const gate of gateMatrix?.gates ?? []) {
    map.set(gate.slide_role, gate.layout_budget ?? {});
  }
  return map;
}

function run28VisualDeltaByRole() {
  return new Map(
    Object.entries({
      cover: "sparse editorial cover plus native surface preview replaces a generic opener",
      setup: "selected type and spacing become explicit before native code execution",
      contrast: "a clear before-after delta replaces equal-density explanation",
      proof: "the chain becomes data -> memory -> gate -> native PPT instead of report cards",
      climax: "one dominant hero object replaces multi-panel climax drift",
      close: "the public-blocked release gate remains visible inside the next workflow loop",
    }),
  );
}

function buildBadMemoryDecompositionByRole(decomposition) {
  const units = decomposition?.units ?? [];
  return new Map([
    ["cover", units.slice(0, 2)],
    ["setup", units.slice(1, 4)],
    ["contrast", units.slice(2, 4)],
    ["proof", units.slice(3, 6)],
    ["climax", units.filter((unit) => unit.id.includes("climax")).slice(0, 1)],
    ["close", units.slice(3, 6)],
  ]);
}

function loadRun28ContractData(arm) {
  const decomposition = readRun28JsonForArm(arm, RUN2_8_INPUTS.decomposition);
  const memory = readRun28JsonForArm(arm, RUN2_8_INPUTS.memory);
  const gateMatrix = readRun28JsonForArm(arm, RUN2_8_INPUTS.gateMatrix);
  const gateMatrixByRole = run28GateMatrixByRole(gateMatrix);
  const decompositionByRole = run28DecompositionByRole(decomposition, gateMatrix);
  const memoryBindingsByRole = run28MemoryBindingsByRole(memory);
  const codeBindingsByRole = run28CodeBindingsByRole(memoryBindingsByRole);
  const layoutBudgetByRole = run28LayoutBudgetByRole(gateMatrix);
  const visualDeltaByRole = run28VisualDeltaByRole();
  return {
    decomposition,
    memory,
    gateMatrix,
    gateMatrixByRole,
    decompositionByRole,
    memoryBindingsByRole,
    codeBindingsByRole,
    layoutBudgetByRole,
    visualDeltaByRole,
  };
}

function renderRun28Full(arm) {
  const contract = loadRun28ContractData(arm);
  const climaxBinding = (contract.memoryBindingsByRole.get("climax") ?? []).find((binding) => binding.id === "binding_climax_hero_object");
  return {
    ...contract,
    climaxPreview: {
      role: "climax",
      hero_binding_id: climaxBinding?.id ?? "",
      function_name: climaxBinding?.code_binding?.function_name ?? "",
      status: "contract_preview_not_rendered",
    },
  };
}

function renderRun28FullSlide(presentation, spec, arm, n, fullData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const bindings = fullData.memoryBindingsByRole.get(spec.role) ?? [];
  const gate = fullData.gateMatrixByRole.get(spec.role);
  const bindingById = new Map(bindings.map((binding) => [binding.id, binding]));
  const typeBinding = bindingById.get("binding_type_scale_readability");
  const spacingBinding = bindingById.get("binding_spacing_zone_grid");
  const deltaBinding = bindingById.get("binding_before_after_delta");
  const gateBinding = bindingById.get("binding_public_gate_legibility");
  const heroBinding = bindingById.get("binding_climax_hero_object");

  if (spec.role === "cover") {
    drawRun28TypeScale(slide, arm, spec, typeBinding, metrics, {
      titleW: 528,
      titleH: 146,
      claimY: 314,
      claimW: 480,
    });
    rect(slide, 696, 132, 444, 290, C.white, colorLine(arm.palette.rule, 1));
    moduleLabel(slide, 720, 154, "native surface preview", arm);
    rect(slide, 736, 196, 206, 150, C.deep, colorLine(C.deep, 1));
    rect(slide, 762, 224, 142, 88, arm.palette.proof, colorLine(arm.palette.proof, 1));
    rect(slide, 974, 222, 104, 12, arm.palette.accent2);
    rect(slide, 974, 258, 126, 8, "#c0cad0");
    rect(slide, 974, 286, 82, 8, "#c0cad0");
    registerProof(metrics, 1);
    drawRun28WorkflowGate(slide, arm, spec.role, gateBinding, metrics, {
      x: 770,
      y: 438,
      w: 292,
      h: 118,
      headline: "public blocked",
      line1: "trace before delivery",
      line2: "human review before release",
      dark: true,
    });
  } else if (spec.role === "setup") {
    drawRun28TypeScale(slide, arm, spec, typeBinding, metrics, {
      titleW: 604,
      titleH: 108,
      claimY: 260,
      claimW: 520,
    });
    drawRun28SpacingZones(slide, arm, spec.role, spacingBinding, metrics, {
      x: 714,
      y: 126,
      w: 416,
      h: 310,
      zones: 3,
    });
    rect(slide, 86, 432, 1028, 98, C.white, colorLine("#cfd6dc", 1));
    moduleLabel(slide, 110, 452, "memory selection", arm);
    const labels = [
      ["type", "readability stack"],
      ["space", "zone grid"],
      ["memory", "before code"],
      ["code", "native PPT"],
    ];
    labels.forEach((item, index) => {
      const x = 110 + index * 244;
      rect(slide, x, 486, 184, 26, index === 3 ? arm.palette.accent : "#eef2f5", colorLine(index === 3 ? arm.palette.accent : "#cfd6dc", 1));
      text(slide, `${item[0]}  ${item[1]}`, x + 12, 492, 160, 12, {
        fontSize: 9,
        bold: true,
        mono: true,
        color: index === 3 ? C.white : arm.palette.title,
      });
      registerText(metrics, `${item[0]} ${item[1]}`);
      if (index < labels.length - 1) rect(slide, x + 188, 497, 36, 4, arm.palette.proof);
    });
    registerWorkflow(metrics, 4);
  } else if (spec.role === "contrast") {
    drawRun28TypeScale(slide, arm, spec, typeBinding, metrics, {
      titleW: 860,
      titleH: 76,
      titleSize: 38,
      claimY: 206,
      claimW: 760,
      claimH: 40,
    });
    drawRun28SpacingZones(slide, arm, spec.role, spacingBinding, metrics, {
      x: 948,
      y: 126,
      w: 188,
      h: 114,
      dense: true,
    });
    drawRun28BeforeAfterDelta(slide, arm, spec.role, deltaBinding, metrics, {
      x: 90,
      y: 282,
      w: 1050,
      h: 246,
    });
  } else if (spec.role === "proof") {
    drawRun28TypeScale(slide, arm, spec, typeBinding, metrics, {
      titleW: 840,
      titleH: 112,
      titleSize: 36,
      claimY: 252,
      claimW: 800,
      claimH: 44,
    });
    rect(slide, 88, 318, 1030, 40, C.white, colorLine("#cfd6dc", 1));
    text(slide, "data -> memory -> gate -> native PPT", 112, 329, 424, 14, {
      fontSize: 10,
      bold: true,
      mono: true,
      color: arm.palette.accent,
    });
    registerText(metrics, "data memory gate native PPT");
    registerWorkflow(metrics, 5);
    drawRun28BeforeAfterDelta(slide, arm, spec.role, deltaBinding, metrics, {
      x: 90,
      y: 412,
      w: 444,
      h: 126,
    });
    drawRun28SpacingZones(slide, arm, spec.role, spacingBinding, metrics, {
      x: 558,
      y: 412,
      w: 236,
      h: 126,
      zones: 2,
    });
    drawRun28WorkflowGate(slide, arm, spec.role, gateBinding, metrics, {
      x: 832,
      y: 394,
      w: 246,
      h: 142,
      headline: "trace + release gate",
      line1: "public blocked",
      line2: "handoff into QA",
      dark: true,
    });
    registerProof(metrics, 1);
  } else if (spec.role === "climax") {
    const climaxPreview = drawRun28Climax(slide, heroBinding, arm, spec, metrics, { typeBinding });
    rect(slide, 88, 540, 986, 44, C.white, colorLine("#cfd6dc", 1));
    text(slide, `${climaxPreview.hero_binding_id} -> ${climaxPreview.function_name}`, 108, 552, 420, 16, {
      fontSize: 9,
      bold: true,
      mono: true,
      color: arm.palette.accent,
    });
    drawRun28WorkflowGate(slide, arm, spec.role, gateBinding, metrics, {
      x: 1070,
      y: 246,
      w: 120,
      h: 180,
      headline: "pause",
      line1: "hero first",
      line2: "support later",
      dark: true,
    });
  } else {
    drawRun28TypeScale(slide, arm, spec, typeBinding, metrics, {
      titleW: 720,
      titleH: 112,
      titleSize: 38,
      claimY: 244,
      claimW: 780,
      claimH: 44,
    });
    drawRun28SpacingZones(slide, arm, spec.role, spacingBinding, metrics, {
      x: 90,
      y: 330,
      w: 392,
      h: 246,
      zones: 2,
    });
    drawRun28WorkflowGate(slide, arm, spec.role, gateBinding, metrics, {
      x: 540,
      y: 348,
      w: 244,
      h: 174,
      headline: "public blocked",
      line1: "native trace done",
      line2: "next loop: more data",
      dark: true,
    });
    rect(slide, 826, 330, 286, 246, C.white, colorLine("#cfd6dc", 1));
    moduleLabel(slide, 846, 352, "next workflow loop", arm);
    const loop = [
      ["select", "new case data"],
      ["bind", "memory updates"],
      ["gate", "layout + release"],
    ];
    loop.forEach((item, index) => {
      rect(slide, 850, 394 + index * 58, 236, 40, index === 2 ? arm.palette.accent : "#eef2f5", colorLine(index === 2 ? arm.palette.accent : "#cfd6dc", 1));
      text(slide, `${item[0]}  ${item[1]}`, 866, 406 + index * 58, 210, 14, {
        fontSize: 9,
        bold: true,
        mono: true,
        color: index === 2 ? C.white : arm.palette.title,
      });
      if (index !== 1) registerText(metrics, `${item[0]} ${item[1]}`);
      if (index < loop.length - 1) rect(slide, 966, 440 + index * 58, 4, 18, arm.palette.proof);
    });
    registerWorkflow(metrics, 3);
    registerProof(metrics, 1);
  }

  proofFooter(slide, spec, arm);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function renderControlSlide(presentation, spec, arm, n, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const mode = arm.armId === "bad_memory_schema" ? "bad" : arm.armId === "run1_5_skill" ? "run1_5" : "prompt";
  drawDenseControl(slide, arm, spec, metrics, mode);
  if (spec.role !== "contrast") {
    drawRun28WorkflowGate(slide, arm, spec.role, null, metrics, {
      x: spec.role === "climax" ? 1038 : 904,
      y: spec.role === "close" ? 330 : spec.role === "climax" ? 324 : 438,
      w: spec.role === "close" ? 226 : spec.role === "climax" ? 164 : 202,
      h: spec.role === "close" ? 168 : 112,
      headline: arm.armId === "bad_memory_schema" ? "boundary only" : "public blocked",
      line1: arm.armId === "run1_5_skill" ? "baseline trace only" : arm.armId === "bad_memory_schema" ? "no memory binding" : "no executable memory",
      line2: arm.armId === "bad_memory_schema" ? "weak layout binding" : "human review required",
      dark: false,
    });
  }
  proofFooter(slide, spec, arm);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertArmInputBoundaries(arm);
  const fullRun28 = arm.armId === "run2_8_full_skill";
  const fullData = fullRun28 ? context.fullData ?? renderRun28Full(arm) : null;
  const gateByRole = fullData?.gateMatrixByRole ?? new Map();
  const decompositionByRole = fullData?.decompositionByRole ?? new Map();
  const memoryByRole = fullData?.memoryBindingsByRole ?? new Map();
  const codeBindingsByRole = fullData?.codeBindingsByRole ?? new Map();
  const budgetByRole = fullData?.layoutBudgetByRole ?? new Map();
  const visualDeltaByRole = fullData?.visualDeltaByRole ?? new Map();
  const badDecompositionByRole = context.badDecompositionByRole ?? new Map();
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics =
    fullRun28 && arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    commercial_case: `${pack}/commercial_case.md`,
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.8 executable-memory arm-specific generation from scripts/generate_ppt_run2_8_executable_memory_arms.mjs",
      no_cross_arm_reuse: ["cached memory summaries", "generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes", "memory binding carryover"],
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
      const roleDecomposition = decompositionByRole.get(slide.role) ?? [];
      const roleBindings = memoryByRole.get(slide.role) ?? [];
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const climaxBindingIds = slide.role === "climax" ? roleBindings.map((binding) => binding.id) : [];
      const actualCodeBindingIds = Array.from(roleMetrics.codeBindingIds);
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_8_contract_status: fullRun28
          ? hasRenderedMetrics
            ? "full_arm_native_generator_rendered"
            : "full_arm_contract_preview_not_rendered"
          : "boundary_control_not_run2_8_full",
        run2_8_decomposition_unit_ids: fullRun28 ? roleDecomposition.map((unit) => unit.id) : [],
        run2_8_memory_binding_ids: fullRun28 ? roleBindings.map((binding) => binding.id) : [],
        run2_8_gate_matrix_ids: fullRun28 ? (gate ? [gate.id] : []) : [],
        run2_8_required_code_binding_ids: fullRun28 ? gate?.required_code_bindings ?? [] : [],
        run2_8_code_binding_ids: fullRun28
          ? hasRenderedMetrics
            ? actualCodeBindingIds
            : gate?.required_code_bindings ?? codeBindingsByRole.get(slide.role) ?? []
          : [],
        run2_8_layout_budget: fullRun28 ? budgetByRole.get(slide.role) ?? {} : {},
        run2_8_visual_delta_from_run2_7: fullRun28 ? visualDeltaByRole.get(slide.role) ?? "" : "",
        run2_8_trace_origin: hasRenderedMetrics ? "actual_native_module_calls" : fullRun28 ? "contract_preview_required_bindings" : "boundary_control",
        climax_binding_ids: fullRun28 ? climaxBindingIds : [],
        negative_control_decomposition_unit_ids:
          arm.armId === "bad_memory_schema" ? (badDecompositionByRole.get(slide.role) ?? []).map((unit) => unit.id) : [],
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
          fullRun28 && gate && hasRenderedMetrics
            ? evaluateBudget(gate.layout_budget ?? {}, roleMetrics)
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

function assertRun28GateMatrixSelfCheck(trace) {
  if (trace.arm_id !== "run2_8_full_skill") return;
  for (const slide of trace.slides) {
    if (slide.run2_8_contract_status !== "full_arm_native_generator_rendered") {
      throw new Error(`Run 2.8 full slide ${slide.slide_id} was not rendered with native module metrics`);
    }
    for (const field of EXPECTED_RUN2_8_TRACE_FIELDS) {
      const value = slide[field];
      const empty =
        value == null ||
        (Array.isArray(value) && value.length === 0) ||
        (typeof value === "string" && value.trim() === "") ||
        (typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === 0);
      if (empty) throw new Error(`Run 2.8 full slide ${slide.slide_id} missing ${field}`);
    }
    if (!slide.layout_budget_status?.within_budget) {
      throw new Error(`Run 2.8 full slide ${slide.slide_id} exceeded layout budget: ${slide.layout_budget_status.violations.join("; ")}`);
    }
    const actualCodeBindings = new Set(slide.run2_8_code_binding_ids ?? []);
    for (const requiredCodeBinding of slide.run2_8_required_code_binding_ids ?? []) {
      if (!actualCodeBindings.has(requiredCodeBinding)) {
        throw new Error(`Run 2.8 full slide ${slide.slide_id} did not call required module ${requiredCodeBinding}`);
      }
    }
    if (slide.role === "climax") {
      if (!slide.climax_binding_ids?.includes("binding_climax_hero_object")) {
        throw new Error("Run 2.8 climax lacks hero binding");
      }
      const share = slide.layout_metrics?.hero_object_canvas_share ?? 0;
      if (!share) throw new Error("Run 2.8 climax missing hero object share");
    }
  }
}

function buildArmContract() {
  return armSpecs.map((arm) => ({
    armId: arm.armId,
    label: arm.label,
    contract_status:
      arm.armId === "run2_8_full_skill"
        ? "run2_8_contract_ready_requires_render_metrics"
        : "run2_8_boundary_control_contract_ready",
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

function buildContactSheet(workspace, arm, previewPaths) {
  const out = path.join(workspace, "preview", "contact-sheet.png");
  execFileSync(
    "python3",
    [
      path.join(root, "scripts", "build_ppt_contact_sheet.py"),
      "--out",
      out,
      "--title",
      arm.label,
      ...previewPaths,
    ],
    { cwd: root, stdio: "pipe" },
  );
  return out;
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
      "secondary deck-profile: engineering-platform",
      `arm: ${arm.armId}`,
      `allowed inputs: ${arm.allowed.join(", ")}`,
      `forbidden inputs: ${arm.forbidden.join(", ")}`,
      "required proof objects: native cover surface, selected-state setup, before-after delta, workflow route, climax hero object, release gate loop",
      "source requirements: commercial case always; decomposition only for negative control; full arm additionally requires executable memory and gate matrix",
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
  let badDecompositionByRole = new Map();
  if (arm.armId === "run2_8_full_skill") {
    fullData = loadRun28ContractData(arm);
  } else if (arm.armId === "bad_memory_schema") {
    badDecompositionByRole = buildBadMemoryDecompositionByRole(readRun28DecompositionForArm(arm));
  }

  const slides = arm.slides.map((slide, index) =>
    arm.armId === "run2_8_full_skill"
      ? renderRun28FullSlide(presentation, slide, arm, index + 1, fullData, metricsByRole)
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

  const trace = traceFor(arm, { fullData, badDecompositionByRole, metricsByRole });
  assertRun28GateMatrixSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_8_executable_memory_arms.mjs",
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
  const runSummary = {
    run_id: "run2_8_executable_memory_four_arms",
    arms: armSpecs.map((arm) => arm.armId),
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_8_executable_memory_summary.json"), runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  EXPECTED_RUN2_8_TRACE_FIELDS,
  RUN2_8_INPUTS,
  RUN2_8_RESTRICTED_INPUTS,
  armSpecs,
  assertRun28GateMatrixSelfCheck,
  buildArmContract,
  drawRun28BeforeAfterDelta,
  drawRun28Climax,
  drawRun28SpacingZones,
  drawRun28TypeScale,
  drawRun28WorkflowGate,
  main,
  renderRun28Full,
  run28CodeBindingsByRole,
  run28DecompositionByRole,
  run28GateMatrixByRole,
  run28LayoutBudgetByRole,
  run28MemoryBindingsByRole,
  run28VisualDeltaByRole,
  traceFor,
};
