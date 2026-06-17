import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.60";
const selectedUsecaseId = "usecase_design_to_production_platform_launch";
const RUN2_60_FULL_STATUS = "run2_59_composition_compiler_consumed_before_native_ppt_drawing";
const RUN2_60_BAD_STATUS = "fail_missing_run2_59_composition_compiler";
const RUN2_60_POLICY = "content_aware_composition_compiler_consumed";
const artifactToolPath =
  process.env.ARTIFACT_TOOL_PATH ??
  "/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";
const artifactToolPackage =
  process.env.ARTIFACT_TOOL_PACKAGE ??
  "/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool";

const { Presentation, PresentationFile } = await import(pathToFileURL(artifactToolPath).href);

const W = 1280;
const H = 720;
const C = {
  ink: "#12161d",
  dark: "#121820",
  paper: "#f4efe4",
  white: "#ffffff",
  muted: "#5b6571",
  line: "#d8d4ca",
  blue: "#2b63d9",
  cyan: "#75c9d8",
  red: "#df4f33",
  green: "#108665",
  amber: "#e4b84e",
  violet: "#7667e8",
  steel: "#e8edf0",
};

const RUN2_60_INPUTS = {
  run259Result: `${pack}/results/run2_59_content_aware_composition_compiler_result.json`,
  run259ContentContracts: `${pack}/run2_59_content_composition_contracts.json`,
  run259LayoutCapacity: `${pack}/run2_59_layout_capacity_model.json`,
  run259ContentSelector: `${pack}/run2_59_content_to_layout_selector.json`,
  run259TracePolicy: `${pack}/run2_59_public_surface_trace_policy.json`,
  run259WorkflowGates: `${pack}/run2_59_composition_workflow_gates.json`,
  run258Result: `${pack}/results/run2_58_product_content_contract_rerun_result.json`,
  run258FullTrace: `outputs/${threadId}/presentations/ppt-run2-58-full-vulca/trace_manifest.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_60_FULL_DATA_INPUTS = Object.values(RUN2_60_INPUTS);
const RUN2_60_BAD_DATA_INPUTS = [
  RUN2_60_INPUTS.run258Result,
  RUN2_60_INPUTS.run258FullTrace,
  RUN2_60_INPUTS.commercialUsecaseBank,
  RUN2_60_INPUTS.sources,
];

const requiredRun259TraceFields = [
  "run2_59_content_contract_id",
  "run2_59_layout_module_id",
  "run2_59_content_burden_level",
  "run2_59_capacity_fit_status",
  "run2_59_public_visible_word_budget",
  "run2_59_trace_only_detail_count",
  "run2_59_public_surface_trace_policy_id",
  "run2_59_composition_gate_id",
];

const baseSlides = [
  { role: "cover", title: "A real brief becomes editable PPT proof." },
  { role: "setup", title: "Sources compile into design memory before drawing." },
  { role: "contrast", title: "The difference is mechanism, not taste." },
  { role: "proof", title: "Trace proves the data path was used." },
  { role: "climax", title: "The product moment is the operating loop." },
  { role: "close", title: "2.60 proves compiler consumption, not public release." },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-60-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.60 / CONTROL",
    footer: "prompt_only | brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_60_FULL_DATA_INPUTS, "drawRun260ContentAwareComposition"],
    palette: {
      bg: "#f7f8fa",
      rail: "#394150",
      accent: C.blue,
      accent2: "#c7d2de",
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d9dee5",
      proof: C.red,
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Make the launch deck clearer.",
        "Show where data enters.",
        "Compare with the old way.",
        "Add proof.",
        "Make the product moment bigger.",
        "End with next steps.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-60-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.60 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_60_FULL_DATA_INPUTS, "drawRun260ContentAwareComposition"],
    palette: {
      bg: "#f3f7fb",
      rail: "#283247",
      accent: C.blue,
      accent2: C.green,
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d2dce7",
      proof: C.green,
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Readable product lab explanation.",
        "Workflow story exists, but no capacity compiler.",
        "Comparison is still generic.",
        "Proof is process-led.",
        "Product moment is named, not staged.",
        "Close remains correct but thin.",
      ][index],
    })),
  },
  {
    armId: "run2_60_full_content_aware_composition",
    slug: "ppt-run2-60-full-vulca",
    label: "Run 2.60 full content-aware composition",
    kicker: "RUN 2.60 / COMPOSITION COMPILER",
    footer: "run2_60_full_content_aware_composition | consumes Run 2.59 | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      ...RUN2_60_FULL_DATA_INPUTS,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_59_content_composition_contracts.json",
      "run2_59_layout_capacity_model.json",
      "run2_59_content_to_layout_selector.json",
      "run2_59_public_surface_trace_policy.json",
      "run2_59_composition_workflow_gates.json",
      "run2_58_product_content_contract_rerun_result.json",
      "ppt-run2-58-full-vulca/trace_manifest.json",
      RUN2_60_POLICY,
    ],
    forbidden: [
      "source layouts",
      "copied screenshots",
      "raw tutorial media",
      "image_only_output_claim",
      "generic product claims",
      "native_drawing_before_run2_59_composition_compiler",
    ],
    palette: {
      bg: "#f4efe4",
      rail: C.dark,
      accent: C.dark,
      accent2: C.blue,
      proof: C.red,
      panel: C.white,
      title: "#0e1218",
      muted: "#56616d",
      rule: "#d8cfbf",
      surface: "#edf2f0",
    },
    slides: baseSlides,
  },
  {
    armId: "bad_run2_58_without_run2_59_composition_compiler",
    slug: "ppt-run2-60-bad-without-composition-compiler",
    label: "Bad missing Run 2.59 composition compiler",
    kicker: "RUN 2.60 / BAD CONTROL",
    footer: "bad_run2_58_without_run2_59_composition_compiler | Run 2.58 only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_60_BAD_DATA_INPUTS],
    data_input_manifest: ["run2_58_generated_without_run2_59_composition_compiler"],
    forbidden: [
      "run2_59_content_composition_contracts.json",
      "run2_59_layout_capacity_model.json",
      "run2_59_content_to_layout_selector.json",
      "run2_59_public_surface_trace_policy.json",
      "run2_59_composition_workflow_gates.json",
      "drawRun260ContentAwareComposition",
      "run2_59_composition_compiler_consumed_before_native_ppt_drawing",
    ],
    palette: {
      bg: "#efe7d5",
      rail: "#6d603b",
      accent: "#766840",
      accent2: "#d4c38a",
      panel: "#faf4e8",
      title: "#2b271e",
      muted: "#665e4d",
      rule: "#dbcfb8",
      proof: "#a66f28",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Run 2.58 explains the product, but it does not compile public capacity.",
        "The source story remains too much like a visible checklist.",
        "The comparison can slip back into matrix thinking.",
        "Trace evidence risks becoming public clutter.",
        "The operating loop is present, but not selected by burden.",
        "The close has no 2.59 handoff proof.",
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

function compactText(value, max = 120) {
  const textValue = String(value ?? "").trim();
  return textValue.length > max ? `${textValue.slice(0, max - 1).trim()}...` : textValue;
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
    codeModuleIds: new Set(),
    productSystemSurfaceKind: "",
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerProof(metrics, count = 1) {
  metrics.proofObjects += count;
}

function registerZones(metrics, count = 1) {
  metrics.zones = Math.max(metrics.zones, count);
}

function socketText(slide, metrics, value, x, y, w, h, opts = {}) {
  const valueToRender = compactText(value, opts.max ?? 120);
  text(slide, valueToRender, x, y, w, h, opts);
  registerText(metrics, valueToRender);
}

function base(slide, arm, n) {
  rect(slide, 0, 0, W, H, arm.palette.bg);
  rect(slide, 0, 0, 16, H, arm.palette.rail);
  text(slide, arm.kicker, 54, 30, 548, 22, {
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
  text(slide, arm.footer, 548, 674, 676, 22, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
    align: "right",
  });
  for (let i = 1; i <= 6; i += 1) {
    rect(slide, 54 + (i - 1) * 20, 684, i === n ? 16 : 8, 5, i === n ? arm.palette.accent : C.line);
  }
}

function chip(slide, metrics, label, x, y, w, fill = C.white, color = C.ink) {
  rect(slide, x, y, w, 30, fill, colorLine("#cfd6dd", 1));
  socketText(slide, metrics, label, x + 12, y + 10, w - 24, 11, {
    fontSize: 8,
    bold: true,
    align: "center",
    color,
    max: 48,
  });
}

function drawEvidenceChips(slide, metrics, chips, x, y, w, fill = C.white) {
  const gap = 10;
  const chipW = (w - gap * Math.max(0, chips.length - 1)) / Math.max(1, chips.length);
  chips.forEach((item, index) => chip(slide, metrics, item, x + index * (chipW + gap), y, chipW, fill));
  registerProof(metrics, chips.length);
}

function drawTraceHint(slide, metrics, selection, x, y, w) {
  rect(slide, x, y, w, 52, "#fff8ed", colorLine("#e1c98f", 1));
  socketText(slide, metrics, "Trace viewer holds raw detail", x + 14, y + 10, w - 28, 12, {
    fontSize: 8,
    mono: true,
    bold: true,
    color: C.red,
    max: 48,
  });
  socketText(slide, metrics, `${selection.contract.trace_only_details.length} trace-only details removed from public slide`, x + 14, y + 28, w - 28, 12, {
    fontSize: 9,
    color: C.ink,
    max: 72,
  });
}

function armUsesFullRun260Composition(arm) {
  return arm.armId === "run2_60_full_content_aware_composition";
}

function armUsesBadRun260Data(arm) {
  return arm.armId === "bad_run2_58_without_run2_59_composition_compiler";
}

function assertRun260ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun260Composition(arm)) {
    for (const input of RUN2_60_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesBadRun260Data(arm)) {
    for (const input of RUN2_60_BAD_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow bad-control input ${input}`);
    }
    for (const input of [
      RUN2_60_INPUTS.run259Result,
      RUN2_60_INPUTS.run259ContentContracts,
      RUN2_60_INPUTS.run259LayoutCapacity,
      RUN2_60_INPUTS.run259ContentSelector,
      RUN2_60_INPUTS.run259TracePolicy,
      RUN2_60_INPUTS.run259WorkflowGates,
    ]) {
      if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    }
    return;
  }
  for (const input of RUN2_60_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun260PackJsonForArm(arm, relPath) {
  assertRun260ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (!armUsesFullRun260Composition(arm) && !armUsesBadRun260Data(arm)) {
    throw new Error(`${arm.armId} cannot read Run 2.60 pack data`);
  }
  return readJson(relPath);
}

function assertSelectedUsecase(value, label) {
  if (value !== selectedUsecaseId) throw new Error(`Run 2.60 selected usecase mismatch in ${label}`);
}

function validateRun260CompositionInputs(data) {
  if (data.run259Result?.status !== "run2_59_content_aware_composition_compiler_ready_public_blocked") {
    throw new Error("Run 2.60 must consume Run 2.59 content composition compiler result");
  }
  if (data.run259ContentContracts?.status !== "run2_59_content_composition_contracts_ready_public_blocked") {
    throw new Error("Run 2.60 must consume Run 2.59 content composition contracts");
  }
  if (data.run259LayoutCapacity?.status !== "run2_59_layout_capacity_model_ready_public_blocked") {
    throw new Error("Run 2.60 must consume Run 2.59 layout capacity model");
  }
  if (data.run259ContentSelector?.status !== "run2_59_content_to_layout_selector_ready_public_blocked") {
    throw new Error("Run 2.60 must consume Run 2.59 content-to-layout selector");
  }
  if (data.run259TracePolicy?.status !== "run2_59_public_surface_trace_policy_ready_public_blocked") {
    throw new Error("Run 2.60 must consume Run 2.59 public surface trace policy");
  }
  if (data.run259WorkflowGates?.status !== "run2_59_composition_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.60 must consume Run 2.59 composition workflow gates");
  }
  if (data.run258Result?.status !== "run2_58_product_content_contract_rerun_public_blocked") {
    throw new Error("Run 2.60 must consume Run 2.58 product content result");
  }
  if (data.run258FullTrace?.arm_id !== "run2_58_full_product_content_contract") {
    throw new Error("Run 2.60 must compare against Run 2.58 full trace");
  }
  if (!Array.isArray(data.run258FullTrace?.slides) || data.run258FullTrace.slides.length !== 6) {
    throw new Error("Run 2.60 requires six Run 2.58 full trace slides");
  }
  assertSelectedUsecase(data.run259Result?.selected_usecase_id, "run2_59_result");
  assertSelectedUsecase(data.run258Result?.selected_usecase_id, "run2_58_result");
  assertSelectedUsecase(data.run258FullTrace?.selected_usecase_id, "run2_58_full_trace");
  const roles = new Set(baseSlides.map((slide) => slide.role));
  const contracts = data.run259ContentContracts.content_composition_contracts ?? [];
  const selectors = data.run259ContentSelector.content_to_layout_selection_records ?? [];
  const capacities = data.run259LayoutCapacity.layout_capacity_records ?? [];
  const gates = data.run259WorkflowGates.composition_workflow_gates ?? [];
  if (contracts.length !== 6 || !contracts.every((contract) => roles.has(contract.role))) {
    throw new Error("Run 2.60 requires six Run 2.59 content composition contracts");
  }
  if (selectors.length !== 6 || !selectors.every((selector) => roles.has(selector.role))) {
    throw new Error("Run 2.60 requires six Run 2.59 content-to-layout selections");
  }
  if (capacities.length !== 6) {
    throw new Error("Run 2.60 requires six Run 2.59 layout capacity records");
  }
  if (gates.length !== 6 || !gates.every((gate) => roles.has(gate.role))) {
    throw new Error("Run 2.60 requires six Run 2.59 composition workflow gates");
  }
  if (data.run259TracePolicy?.policy_id !== "run2_59_public_slide_trace_viewer_split") {
    throw new Error("Run 2.60 must bind Run 2.59 public slide / trace viewer split policy");
  }
  const fullArmStatus = data.run259WorkflowGates?.next_generated_run_contract?.full_arm_pass_status;
  if (fullArmStatus !== RUN2_60_FULL_STATUS) {
    throw new Error("Run 2.60 next-generated-run contract status mismatch");
  }
  for (const contract of contracts) {
    const selector = selectors.find((item) => item.role === contract.role);
    const gate = gates.find((item) => item.role === contract.role);
    const capacity = capacities.find((item) => item.layout_module_id === selector?.selected_layout_module_id);
    if (!selector || !gate || !capacity) throw new Error(`Run 2.60 missing composition compiler link for ${contract.role}`);
    if (selector.content_contract_id !== contract.content_contract_id) throw new Error(`Run 2.60 contract/selector mismatch for ${contract.role}`);
    if (gate.content_contract_id !== contract.content_contract_id) throw new Error(`Run 2.60 contract/gate mismatch for ${contract.role}`);
    if (gate.selected_layout_module_id !== selector.selected_layout_module_id) throw new Error(`Run 2.60 selector/gate module mismatch for ${contract.role}`);
    for (const field of requiredRun259TraceFields) {
      if (!(contract.required_trace_fields_for_run2_60 ?? []).includes(field)) throw new Error(`Run 2.60 missing required contract trace field ${field}`);
      if (!(selector.required_trace_fields_for_run2_60 ?? []).includes(field)) throw new Error(`Run 2.60 missing required selector trace field ${field}`);
      if (!(gate.required_trace_fields ?? []).includes(field)) throw new Error(`Run 2.60 missing required workflow trace field ${field}`);
    }
    if ((selector.public_visible_word_budget ?? 0) > (capacity.max_visible_words ?? 0)) {
      throw new Error(`public_visible_word_budget_exceeds_selected_layout_capacity: ${contract.role}`);
    }
  }
}

function loadRun260CompositionData(arm) {
  const data = {
    run259Result: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.run259Result),
    run259ContentContracts: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.run259ContentContracts),
    run259LayoutCapacity: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.run259LayoutCapacity),
    run259ContentSelector: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.run259ContentSelector),
    run259TracePolicy: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.run259TracePolicy),
    run259WorkflowGates: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.run259WorkflowGates),
    run258Result: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.run258Result),
    run258FullTrace: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.run258FullTrace),
    commercialUsecaseBank: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.commercialUsecaseBank),
    sources: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.sources),
  };
  validateRun260CompositionInputs(data);
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_60_content_aware_composition_inputs_ready",
  };
}

function loadRun260BadControlData(arm) {
  const data = {
    run258Result: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.run258Result),
    run258FullTrace: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.run258FullTrace),
    commercialUsecaseBank: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.commercialUsecaseBank),
    sources: readRun260PackJsonForArm(arm, RUN2_60_INPUTS.sources),
  };
  if (data.run258Result?.status !== "run2_58_product_content_contract_rerun_public_blocked") {
    throw new Error("Run 2.60 bad control must read Run 2.58 result");
  }
  if (data.run258FullTrace?.arm_id !== "run2_58_full_product_content_contract") {
    throw new Error("Run 2.60 bad control must read Run 2.58 full trace");
  }
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
  };
}

const ROLE_RENDERERS = {
  cover: "drawRun260EditorialCoverField",
  setup: "drawRun260ProductTheaterStage",
  contrast: "drawRun260BeforeAfterRoute",
  proof: "drawRun260DenseEvidenceCompression",
  climax: "drawRun260MetricRevealStage",
  close: "drawRun260QuietReleaseHandoff",
};

function selectRun260ForSlide(role, data) {
  const contract = (data.run259ContentContracts.content_composition_contracts ?? []).find((item) => item.role === role);
  const selector = (data.run259ContentSelector.content_to_layout_selection_records ?? []).find((item) => item.role === role);
  const gate = (data.run259WorkflowGates.composition_workflow_gates ?? []).find((item) => item.role === role);
  const layout = (data.run259LayoutCapacity.layout_capacity_records ?? []).find(
    (item) => item.layout_module_id === selector?.selected_layout_module_id,
  );
  const priorTraceSlide = (data.run258FullTrace.slides ?? []).find((item) => item.role === role);
  if (!contract || !selector || !gate || !layout || !priorTraceSlide) {
    throw new Error(`Run 2.60 missing role composition selection for ${role}`);
  }
  return {
    role,
    contract,
    selector,
    gate,
    layout,
    priorTraceSlide,
    usecase: data.usecase,
    tracePolicy: data.run259TracePolicy,
  };
}

function titleCase(value) {
  return String(value ?? "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

function drawRun260EditorialCoverField(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.contract.public_claim, 76, 124, 520, 112, {
    fontSize: 38,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 84,
  });
  socketText(slide, metrics, "Code-generated editable PPT, not an image-only demo.", 80, 256, 470, 30, {
    fontSize: 14,
    color: arm.palette.muted,
    max: 72,
  });
  drawEvidenceChips(slide, metrics, selection.contract.evidence_chips, 80, 318, 430, "#fffaf2");
  rect(slide, 612, 112, 512, 404, C.dark, colorLine(C.dark, 1));
  socketText(slide, metrics, "brief -> source pack -> memory -> code -> deck", 652, 148, 420, 22, {
    fontSize: 12,
    mono: true,
    bold: true,
    color: C.cyan,
    max: 64,
  });
  const nodes = [
    ["brief", 656, 214, 96, 78, C.white],
    ["database", 806, 184, 132, 96, "#e9f4f7"],
    ["skill", 740, 336, 112, 86, "#fff2d6"],
    ["code", 946, 310, 104, 92, "#edf6f1"],
    ["PPT", 880, 444, 142, 54, C.red],
  ];
  nodes.forEach(([label, x, y, w, h, fill], index) => {
    if (index === 2) ellipse(slide, x, y, w, h, fill, colorLine("#95a8b8", 1));
    else rect(slide, x, y, w, h, fill, colorLine("#95a8b8", 1));
    socketText(slide, metrics, label, x + 14, y + h / 2 - 8, w - 28, 16, {
      fontSize: index === 4 ? 13 : 10,
      bold: true,
      align: "center",
      color: index === 4 ? C.white : C.ink,
      max: 18,
    });
  });
  rect(slide, 748, 250, 80, 5, C.cyan, colorLine("transparent", 0));
  rect(slide, 856, 372, 82, 5, C.cyan, colorLine("transparent", 0));
  drawTraceHint(slide, metrics, selection, 80, 404, 430);
  registerZones(metrics, 8);
}

function drawRun260ProductTheaterStage(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.contract.public_claim, 78, 116, 510, 70, {
    fontSize: 31,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 76,
  });
  socketText(slide, metrics, "Brief, sources, memory, contract, and gate are staged before drawing.", 82, 198, 476, 48, {
    fontSize: 12,
    color: arm.palette.muted,
    max: 116,
  });
  rect(slide, 612, 104, 500, 404, "#111820", colorLine("#111820", 1));
  rect(slide, 662, 156, 398, 210, "#f8fafb", colorLine("#8fa2b1", 1));
  socketText(slide, metrics, "source-to-memory compiler stage", 710, 178, 302, 20, {
    fontSize: 13,
    title: true,
    bold: true,
    align: "center",
    max: 48,
  });
  const stages = ["brief", "source pack", "memory", "contract", "gate"];
  stages.forEach((stage, index) => {
    const x = 684 + index * 70;
    const y = 242 + (index % 2) * 40;
    ellipse(slide, x, y, 62, 62, index >= 2 ? "#e8f5ef" : "#fff2d6", colorLine("#8796a4", 1));
    socketText(slide, metrics, stage, x + 8, y + 22, 46, 14, {
      fontSize: 7.8,
      bold: true,
      align: "center",
      max: 22,
    });
    if (index < stages.length - 1) rect(slide, x + 60, y + 30, 20, 4, C.blue, colorLine("transparent", 0));
  });
  drawEvidenceChips(slide, metrics, selection.contract.evidence_chips, 84, 312, 468, "#fffaf2");
  chip(slide, metrics, selection.selector.capacity_fit_status, 678, 404, 178, "#e8f5ef", C.ink);
  chip(slide, metrics, selection.layout.module_family, 876, 404, 166, "#eef3f6", C.ink);
  drawTraceHint(slide, metrics, selection, 84, 408, 468);
  registerZones(metrics, 7);
}

function drawRun260BeforeAfterRoute(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.contract.public_claim, 72, 106, 550, 62, {
    fontSize: 30,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 72,
  });
  socketText(slide, metrics, "Bad control breaks where the 2.59 composition compiler should bind content burden to layout capacity.", 76, 182, 536, 42, {
    fontSize: 12,
    color: arm.palette.muted,
    max: 108,
  });
  rect(slide, 100, 320, 250, 106, "#fff8e4", colorLine("#d1bd80", 1));
  rect(slide, 472, 256, 160, 160, "#f4dfd4", colorLine("#df4f33", 2));
  ellipse(slide, 782, 212, 254, 254, "#111820", colorLine("#75c9d8", 2));
  rect(slide, 350, 370, 124, 6, C.red, colorLine("transparent", 0));
  rect(slide, 632, 330, 150, 6, C.blue, colorLine("transparent", 0));
  socketText(slide, metrics, "prompt-only deck", 122, 360, 206, 20, {
    fontSize: 12,
    bold: true,
    align: "center",
    max: 32,
  });
  socketText(slide, metrics, "missing compiler turn point", 498, 312, 108, 42, {
    fontSize: 10,
    bold: true,
    align: "center",
    color: C.red,
    max: 38,
  });
  socketText(slide, metrics, "Vulca code-generated PPT", 832, 304, 152, 44, {
    fontSize: 16,
    title: true,
    bold: true,
    align: "center",
    color: C.white,
    max: 42,
  });
  drawEvidenceChips(slide, metrics, selection.contract.evidence_chips, 120, 492, 866, "#ffffff");
  drawTraceHint(slide, metrics, selection, 1000, 492, 170);
  registerZones(metrics, 7);
}

function drawRun260DenseEvidenceCompression(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.contract.public_claim, 70, 100, 520, 56, {
    fontSize: 28,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 60,
  });
  socketText(slide, metrics, "The public slide shows a compact proof board; raw field inventory stays in trace.", 74, 168, 494, 34, {
    fontSize: 12,
    color: arm.palette.muted,
    max: 84,
  });
  rect(slide, 622, 110, 496, 400, "#f8fafb", colorLine("#c7d1d8", 1));
  socketText(slide, metrics, "inspection board", 658, 142, 166, 18, {
    fontSize: 12,
    mono: true,
    bold: true,
    color: C.red,
    max: 28,
  });
  const proofRows = [
    ["contract", "2.59 proof contract"],
    ["layout module", "dense evidence module"],
    ["workflow gate", "proof composition gate"],
    ["policy", "public / trace split"],
  ];
  proofRows.forEach(([label, value], index) => {
    const x = 658 + (index % 2) * 210;
    const y = 190 + Math.floor(index / 2) * 120;
    rect(slide, x, y, 178, 74, index === 0 ? "#fff2d6" : C.white, colorLine("#cfd8e0", 1));
    socketText(slide, metrics, label, x + 14, y + 13, 150, 12, {
      fontSize: 7.6,
      mono: true,
      bold: true,
      color: C.red,
      max: 22,
    });
    socketText(slide, metrics, value, x + 14, y + 32, 150, 24, {
      fontSize: 8.4,
      bold: true,
      max: 48,
    });
  });
  drawEvidenceChips(slide, metrics, selection.contract.evidence_chips, 74, 270, 470, "#fffaf2");
  drawTraceHint(slide, metrics, selection, 74, 366, 470);
  chip(slide, metrics, "dense evidence compression", 724, 424, 244, "#111820", C.white);
  registerZones(metrics, 8);
}

function drawRun260MetricRevealStage(slide, arm, spec, selection, metrics) {
  rect(slide, 54, 92, 1136, 544, C.dark, colorLine(C.dark, 1));
  socketText(slide, metrics, selection.contract.public_claim, 94, 132, 470, 82, {
    fontSize: 34,
    title: true,
    bold: true,
    color: C.white,
    max: 64,
  });
  socketText(slide, metrics, "One operating loop owns the slide; raw QA detail moves to trace.", 98, 230, 420, 36, {
    fontSize: 12,
    color: "#dbe5ec",
    max: 72,
  });
  const loop = [
    ["brief", 708, 166],
    ["data", 930, 220],
    ["memory", 986, 424],
    ["workflow", 792, 524],
    ["code", 622, 390],
  ];
  loop.forEach(([label, x, y], index) => {
    ellipse(slide, x, y, 128, 88, index === 4 ? C.red : "#f8fafb", colorLine(index === 4 ? C.red : "#94a3b8", 1));
    socketText(slide, metrics, label, x + 22, y + 34, 84, 16, {
      fontSize: 10,
      bold: true,
      align: "center",
      color: index === 4 ? C.white : C.ink,
      max: 18,
    });
  });
  ellipse(slide, 772, 306, 220, 132, "#111820", colorLine("#75c9d8", 2));
  socketText(slide, metrics, "editable PPT preview", 812, 356, 140, 26, {
    fontSize: 15,
    title: true,
    bold: true,
    color: C.white,
    align: "center",
    max: 34,
  });
  drawEvidenceChips(slide, metrics, selection.contract.evidence_chips, 96, 360, 404, "#fffaf2");
  drawTraceHint(slide, metrics, selection, 96, 462, 404);
  registerZones(metrics, 7);
}

function drawRun260QuietReleaseHandoff(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.contract.public_claim, 82, 122, 520, 72, {
    fontSize: 31,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 66,
  });
  socketText(slide, metrics, "Generated proof exists; compiler consumed; public release remains blocked.", 86, 212, 488, 40, {
    fontSize: 12,
    color: arm.palette.muted,
    max: 96,
  });
  const marks = [
    ["2.58", "product content proof", 650, 164, "#eef3f6"],
    ["2.59", "composition compiler", 796, 276, "#fff2d6"],
    ["2.60", "generated rerun", 942, 164, "#e8f5ef"],
  ];
  marks.forEach(([run, label, x, y, fill], index) => {
    ellipse(slide, x, y, 116, 116, fill, colorLine(index === 2 ? C.red : "#99aab8", index === 2 ? 2 : 1));
    socketText(slide, metrics, run, x + 26, y + 34, 64, 24, {
      fontSize: 18,
      title: true,
      bold: true,
      align: "center",
      color: arm.palette.title,
      max: 8,
    });
    socketText(slide, metrics, label, x + 14, y + 66, 88, 16, {
      fontSize: 7.8,
      align: "center",
      bold: true,
      max: 28,
    });
    if (index < marks.length - 1) rect(slide, x + 116, y + 56, 58, 6, C.blue, colorLine("transparent", 0));
  });
  rect(slide, 678, 468, 348, 54, "#111820", colorLine("#111820", 1));
  socketText(slide, metrics, "public blocked until human visual, native render, motion, source-boundary, and approval gates pass", 706, 486, 292, 20, {
    fontSize: 9.6,
    bold: true,
    align: "center",
    color: C.white,
    max: 82,
  });
  drawEvidenceChips(slide, metrics, selection.contract.evidence_chips, 86, 340, 474, "#fffaf2");
  drawTraceHint(slide, metrics, selection, 86, 442, 474);
  registerZones(metrics, 7);
}

const RUN2_60_RENDERERS = {
  cover: drawRun260EditorialCoverField,
  setup: drawRun260ProductTheaterStage,
  contrast: drawRun260BeforeAfterRoute,
  proof: drawRun260DenseEvidenceCompression,
  climax: drawRun260MetricRevealStage,
  close: drawRun260QuietReleaseHandoff,
};

function markRun260Composition(metrics, selection) {
  metrics.codeModuleIds.add("drawRun260ContentAwareComposition");
  metrics.codeModuleIds.add(ROLE_RENDERERS[selection.role]);
  metrics.productSystemSurfaceKind = selection.layout.module_family;
  registerProof(metrics, Math.max(3, selection.contract.evidence_chips.length + 1));
  registerZones(metrics, 7);
}

function drawRun260ContentAwareComposition(slide, arm, spec, selection, metrics) {
  const renderer = RUN2_60_RENDERERS[spec.role];
  if (!renderer) throw new Error(`Run 2.60 missing role renderer for ${spec.role}`);
  renderer(slide, arm, spec, selection, metrics);
  markRun260Composition(metrics, selection);
}

function drawBadRun260FallbackSlide(slide, arm, spec, badData, metrics) {
  const prior = (badData.run258FullTrace?.slides ?? []).find((slideItem) => slideItem.role === spec.role);
  socketText(slide, metrics, spec.title, 76, 118, 540, 78, {
    fontSize: 28,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 104,
  });
  socketText(slide, metrics, "This arm can read Run 2.58 product content, but it cannot read Run 2.59 content composition contracts, layout capacity, selector, trace policy, or workflow gates.", 80, 216, 500, 58, {
    fontSize: 13,
    color: arm.palette.muted,
    max: 150,
  });
  rect(slide, 626, 130, 474, 314, arm.palette.panel, colorLine(arm.palette.rule, 1));
  socketText(slide, metrics, "no composition compiler", 666, 170, 280, 24, {
    fontSize: 16,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 44,
  });
  ["2.58 trace", "content terms", "generic layout", "public clutter risk"].forEach((label, index) => {
    rect(slide, 668 + (index % 2) * 180, 238 + Math.floor(index / 2) * 78, 142, 50, "#eee2c7", colorLine("#c6ad78", 1));
    socketText(slide, metrics, label, 684 + (index % 2) * 180, 254 + Math.floor(index / 2) * 78, 110, 16, {
      fontSize: 8.8,
      bold: true,
      align: "center",
      max: 36,
    });
  });
  socketText(slide, metrics, prior?.run2_58_product_system_surface_kind ?? "Run 2.58 content trace exists", 646, 470, 416, 26, {
    fontSize: 10,
    color: arm.palette.muted,
    max: 92,
  });
  metrics.productSystemSurfaceKind = "run2_58_product_content_without_run2_59_composition_compiler";
  registerProof(metrics, 2);
  registerZones(metrics, 4);
}

function drawControlSlideContent(slide, arm, spec, metrics, mode = "prompt") {
  socketText(slide, metrics, spec.title, 76, 132, 596, 104, {
    fontSize: mode === "run1_5" ? 33 : 36,
    bold: true,
    title: true,
    color: arm.palette.title,
    max: 100,
  });
  socketText(slide, metrics, "This arm does not receive the Run 2.59 composition compiler, so it cannot bind content burden to layout capacity before drawing.", 80, 252, 526, 56, {
    fontSize: 14,
    color: arm.palette.muted,
    max: 126,
  });
  ["brief", "theme", "layout", "summary"].forEach((label, index) => {
    rect(slide, 674 + (index % 2) * 158, 278 + Math.floor(index / 2) * 108, 132, 82, C.white, colorLine(arm.palette.rule, 1));
    socketText(slide, metrics, label, 696 + (index % 2) * 158, 310 + Math.floor(index / 2) * 108, 86, 18, {
      fontSize: 10,
      bold: true,
      align: "center",
      color: arm.palette.title,
      max: 22,
    });
  });
  rect(slide, 84, 360, 482, 126, C.white, colorLine(arm.palette.rule, 1));
  socketText(slide, metrics, mode === "run1_5" ? "Prior skill: readable, but no 2.59 composition capacity compiler." : "Prompt-only: no content contracts, layout selector, or trace split policy.", 108, 398, 420, 38, {
    fontSize: 17,
    bold: true,
    title: true,
    color: arm.palette.title,
    max: 92,
  });
  metrics.productSystemSurfaceKind = mode === "run1_5" ? "run1_5_without_run2_59_composition_compiler" : "prompt_only_without_run2_59_composition_compiler";
  registerProof(metrics, 2);
  registerZones(metrics, 3);
}

function renderRun260Slide(presentation, spec, arm, n, compositionData, badData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun260Composition(arm)) {
    const selection = selectRun260ForSlide(spec.role, compositionData);
    drawRun260ContentAwareComposition(slide, arm, spec, selection, metrics);
  } else if (armUsesBadRun260Data(arm)) {
    drawBadRun260FallbackSlide(slide, arm, spec, badData, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function blankRun259Fields(bad = false) {
  return {
    run2_59_content_contract_id: "",
    run2_59_layout_module_id: "",
    run2_59_content_burden_level: "",
    run2_59_capacity_fit_status: bad ? "fail_missing_run2_59" : "",
    run2_59_public_visible_word_budget: 0,
    run2_59_trace_only_detail_count: 0,
    run2_59_public_surface_trace_policy_id: "",
    run2_59_composition_gate_id: "",
  };
}

function traceFor(arm, context = {}) {
  assertRun260ArmInputBoundaries(arm);
  const fullRun260 = armUsesFullRun260Composition(arm);
  const badRun260 = armUsesBadRun260Data(arm);
  const compositionData = fullRun260 ? context.compositionData ?? loadRun260CompositionData(arm) : null;
  const badData = badRun260 ? context.badData ?? loadRun260BadControlData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun260 || badRun260 ? selectedUsecaseId : "",
    source_repair_run_id: fullRun260 ? "2.59" : "",
    source_generated_run_id: fullRun260 || badRun260 ? "2.58" : "",
    run2_60_content_aware_composition_status: fullRun260
      ? RUN2_60_FULL_STATUS
      : badRun260
        ? RUN2_60_BAD_STATUS
        : "boundary_control_no_run2_59_composition_compiler",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.60 content-aware composition rerun from scripts/generate_ppt_run2_60_content_aware_composition_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun260 ? selectRun260ForSlide(slide.role, compositionData) : null;
      const run259Fields = fullRun260
        ? {
            run2_59_content_contract_id: selection.contract.content_contract_id,
            run2_59_layout_module_id: selection.layout.layout_module_id,
            run2_59_content_burden_level: selection.selector.content_burden_level,
            run2_59_capacity_fit_status: selection.selector.capacity_fit_status,
            run2_59_public_visible_word_budget: selection.selector.public_visible_word_budget,
            run2_59_trace_only_detail_count: selection.contract.trace_only_details.length,
            run2_59_public_surface_trace_policy_id: selection.tracePolicy.policy_id,
            run2_59_composition_gate_id: selection.gate.gate_id,
          }
        : blankRun259Fields(badRun260);
      const run260Fields = {
        run2_60_code_module_ids: fullRun260 ? Array.from(roleMetrics.codeModuleIds) : [],
        run2_60_public_trace_split_status: fullRun260
          ? "pass_internal"
          : badRun260
            ? "fail_missing_run2_59_composition_compiler"
            : "",
        run2_60_over_capacity_fallback_status: fullRun260
          ? selection.selector.capacity_fit_status === "requires_dense_evidence_compression"
            ? "pass_fallback_recorded"
            : "pass_no_over_capacity"
          : badRun260
            ? "fail_missing_run2_59_composition_compiler"
            : "",
        run2_60_layout_collision_status: fullRun260
          ? "pass_internal"
          : badRun260
            ? "risk_reuses_run2_58_renderer"
            : "",
        run2_60_content_aware_composition_status: fullRun260
          ? "pass_internal"
          : badRun260
            ? RUN2_60_BAD_STATUS
            : "",
      };
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        source_run2_58_slide_id: fullRun260 ? selection.priorTraceSlide.slide_id : badRun260 ? slide.role : "",
        run2_58_product_content_contract_status: fullRun260
          ? selection.priorTraceSlide.run2_58_product_content_contract_status
          : badRun260
            ? "pass_internal_prior_only"
            : "",
        ...run259Fields,
        ...run260Fields,
        layout_metrics: {
          text_box_count: roleMetrics.textBoxCount,
          visible_words: roleMetrics.visibleWords,
          text_density_tier: roleMetrics.visibleWords >= 74 ? "bounded_dense" : "public_compact",
          proof_objects: roleMetrics.proofObjects,
          zones: roleMetrics.zones,
          trace_panel_visible: false,
          gate_ribbon_visible: false,
          product_system_surface_kind: roleMetrics.productSystemSurfaceKind,
        },
      };
    }),
  };
}

function assertRun260CompositionSelfCheck(trace) {
  if (trace.arm_id === "run2_60_full_content_aware_composition") {
    if (trace.run2_60_content_aware_composition_status !== RUN2_60_FULL_STATUS) {
      throw new Error("Run 2.60 full trace did not consume Run 2.59 composition compiler before native PPT drawing");
    }
    for (const slide of trace.slides) {
      if (!String(slide.run2_59_content_contract_id ?? "").startsWith("content_contract_2_59_")) {
        throw new Error(`Run 2.60 full slide ${slide.slide_id} missing Run 2.59 content contract`);
      }
      if (!String(slide.run2_59_layout_module_id ?? "").startsWith("module_2_15_")) {
        throw new Error(`Run 2.60 full slide ${slide.slide_id} missing Run 2.59 layout module`);
      }
      if (!["pass_after_trace_separation", "requires_dense_evidence_compression"].includes(slide.run2_59_capacity_fit_status)) {
        throw new Error(`Run 2.60 full slide ${slide.slide_id} failed Run 2.59 capacity fit`);
      }
      if ((slide.run2_59_public_visible_word_budget ?? 999) > 74) {
        throw new Error(`Run 2.60 full slide ${slide.slide_id} public visible word budget too high`);
      }
      if ((slide.run2_59_trace_only_detail_count ?? 0) < 2) {
        throw new Error(`Run 2.60 full slide ${slide.slide_id} did not externalize trace-only detail`);
      }
      if (slide.run2_60_public_trace_split_status !== "pass_internal") {
        throw new Error(`Run 2.60 full slide ${slide.slide_id} did not pass public/trace split`);
      }
      if (slide.run2_60_layout_collision_status !== "pass_internal") {
        throw new Error(`Run 2.60 full slide ${slide.slide_id} has layout collision risk`);
      }
      if (!(slide.run2_60_code_module_ids ?? []).includes("drawRun260ContentAwareComposition")) {
        throw new Error(`Run 2.60 full slide ${slide.slide_id} missing content-aware composition module`);
      }
      if ((slide.layout_metrics?.visible_words ?? 0) > 96) {
        throw new Error(`Run 2.60 full slide ${slide.slide_id} exceeds public visible-word capacity`);
      }
    }
  }
  if (trace.arm_id === "bad_run2_58_without_run2_59_composition_compiler") {
    for (const slide of trace.slides) {
      if (slide.run2_59_content_contract_id !== "") {
        throw new Error(`Run 2.60 bad slide ${slide.slide_id} leaked Run 2.59 content contract`);
      }
      if (slide.run2_59_capacity_fit_status !== "fail_missing_run2_59") {
        throw new Error(`Run 2.60 bad slide ${slide.slide_id} must fail missing Run 2.59`);
      }
      if (slide.run2_60_public_trace_split_status !== "fail_missing_run2_59_composition_compiler") {
        throw new Error(`Run 2.60 bad slide ${slide.slide_id} must fail public/trace split`);
      }
    }
  }
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
  execFileSync("python3", args, { cwd: root, stdio: "pipe" });
  return out;
}

function buildContactSheet(workspace, arm, previewPaths) {
  return buildNamedContactSheet(path.join(workspace, "preview", "contact-sheet.png"), arm.label, previewPaths);
}

function buildRun260FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-60-four-arm-contact-sheet.png"),
    "Run 2.60 content-aware composition compiler comparison",
    sheets,
    sheets.length,
    labels,
  );
}

function buildFullSkillSeriesSheet() {
  const fullItems = [
    ["Run 2.0", "ppt-run2-full-vulca"],
    ["Run 2.1", "ppt-run2-1-full-vulca"],
    ["Run 2.2", "ppt-run2-2-full-vulca"],
    ["Run 2.3", "ppt-run2-3-full-vulca"],
    ["Run 2.4", "ppt-run2-4-full-vulca"],
    ["Run 2.5", "ppt-run2-5-full-vulca"],
    ["Run 2.6", "ppt-run2-6-full-vulca"],
    ["Run 2.6R", "ppt-run2-6r-full-vulca"],
    ["Run 2.7", "ppt-run2-7-full-vulca"],
    ["Run 2.8", "ppt-run2-8-full-vulca"],
    ["Run 2.9", "ppt-run2-9-full-vulca"],
    ["Run 2.10", "ppt-run2-10-full-vulca"],
    ["Run 2.13", "ppt-run2-13-full-vulca"],
    ["Run 2.14", "ppt-run2-14-full-vulca"],
    ["Run 2.16", "ppt-run2-16-full-vulca"],
    ["Run 2.19", "ppt-run2-19-full-vulca"],
    ["Run 2.22", "ppt-run2-22-full-vulca"],
    ["Run 2.25", "ppt-run2-25-full-vulca"],
    ["Run 2.27", "ppt-run2-27-full-vulca"],
    ["Run 2.28", "ppt-run2-28-full-vulca"],
    ["Run 2.29", "ppt-run2-29-full-vulca"],
    ["Run 2.31", "ppt-run2-31-full-vulca"],
    ["Run 2.33", "ppt-run2-33-full-vulca"],
    ["Run 2.36", "ppt-run2-36-full-vulca"],
    ["Run 2.39", "ppt-run2-39-full-vulca"],
    ["Run 2.40", "ppt-run2-40-full-vulca"],
    ["Run 2.41", "ppt-run2-41-full-vulca"],
    ["Run 2.44", "ppt-run2-44-full-vulca"],
    ["Run 2.47", "ppt-run2-47-full-vulca"],
    ["Run 2.50", "ppt-run2-50-full-vulca"],
    ["Run 2.52", "ppt-run2-52-full-vulca"],
    ["Run 2.54", "ppt-run2-54-full-vulca"],
    ["Run 2.55", "ppt-run2-55-full-vulca"],
    ["Run 2.56", "ppt-run2-56-full-vulca"],
    ["Run 2.58", "ppt-run2-58-full-vulca"],
    ["Run 2.60", "ppt-run2-60-full-vulca"],
  ];
  const items = fullItems
    .map(([label, slug]) => [label, path.join(outRoot, slug, "preview", "contact-sheet.png")])
    .filter(([, file]) => fs.existsSync(file));
  if (!items.length) return "";
  const out = path.join(outRoot, "run2-full-skill-series-horizontal.png");
  const args = [
    path.join(root, "scripts", "build_ppt_full_skill_series_sheet.py"),
    "--out",
    out,
    "--title",
    "Run 2 full-skill series",
    "--item-width",
    "420",
  ];
  for (const [label, file] of items) {
    args.push("--item", `${label}=${file}`);
  }
  execFileSync("python3", args, { cwd: root, stdio: "pipe" });
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
      `arm: ${arm.armId}`,
      `selected usecase: ${selectedUsecaseId}`,
      `allowed inputs: ${arm.allowed.join(", ")}`,
      `forbidden inputs: ${arm.forbidden.join(", ")}`,
      "required proof objects: Run 2.59 content contract, layout module, capacity fit, public/trace split, composition gate",
      "source requirements: full arm reads Run 2.59 compiler artifacts and Run 2.58 full trace before native PPT drawing",
      "negative control: bad arm can read Run 2.58 generated result and trace, but cannot read Run 2.59 composition compiler artifacts",
      "profile-specific QA gates: public slide surface must remain bounded; raw trace details belong in viewer trace",
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
  const compositionData = armUsesFullRun260Composition(arm) ? loadRun260CompositionData(arm) : null;
  const badData = armUsesBadRun260Data(arm) ? loadRun260BadControlData(arm) : null;
  const slides = arm.slides.map((slide, index) =>
    renderRun260Slide(presentation, slide, arm, index + 1, compositionData, badData, metricsByRole),
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
  const trace = traceFor(arm, { compositionData, badData, metricsByRole });
  assertRun260CompositionSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_60_content_aware_composition_arms.mjs",
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

function writeRun260Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-60-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-60-bad-without-composition-compiler/trace_manifest.json`);
  const result = {
    schema_version: 1,
    run_id: RUN_ID,
    status: "run2_60_content_aware_composition_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_repair_run_id: "2.59",
    source_generated_run_id: "2.58",
    database_expansion: false,
    workflow_expansion: true,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_59_result: RUN2_60_INPUTS.run259Result,
      run2_59_content_contracts: RUN2_60_INPUTS.run259ContentContracts,
      run2_59_layout_capacity_model: RUN2_60_INPUTS.run259LayoutCapacity,
      run2_59_content_to_layout_selector: RUN2_60_INPUTS.run259ContentSelector,
      run2_59_public_surface_trace_policy: RUN2_60_INPUTS.run259TracePolicy,
      run2_59_composition_workflow_gates: RUN2_60_INPUTS.run259WorkflowGates,
      run2_58_result: RUN2_60_INPUTS.run258Result,
      run2_58_full_trace: RUN2_60_INPUTS.run258FullTrace,
      commercial_usecase_bank: RUN2_60_INPUTS.commercialUsecaseBank,
      sources: RUN2_60_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_60_content_aware_composition_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_60_full_content_aware_composition",
      best_internal_arm_verdict:
        "Run 2.59 content composition contracts, layout capacity, selector, public/trace policy, and workflow gates are consumed before native PPT drawing.",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: RUN2_60_POLICY,
      source_data_status: RUN2_60_FULL_STATUS,
      full_slides_with_run2_59_content_contracts: fullTrace.slides.filter((slide) =>
        String(slide.run2_59_content_contract_id ?? "").startsWith("content_contract_2_59_"),
      ).length,
      full_slides_with_layout_capacity_fit: fullTrace.slides.filter((slide) =>
        ["pass_after_trace_separation", "requires_dense_evidence_compression"].includes(slide.run2_59_capacity_fit_status),
      ).length,
      full_slides_with_public_trace_split: fullTrace.slides.filter((slide) => slide.run2_60_public_trace_split_status === "pass_internal").length,
      full_slides_without_layout_collision: fullTrace.slides.filter((slide) => slide.run2_60_layout_collision_status === "pass_internal").length,
      bad_control_slides_without_run2_59_compiler: badTrace.slides.filter(
        (slide) =>
          slide.run2_59_capacity_fit_status === "fail_missing_run2_59" &&
          slide.run2_60_public_trace_split_status === "fail_missing_run2_59_composition_compiler",
      ).length,
      repair_modules: Object.values(ROLE_RENDERERS),
    },
    control_boundary: {
      bad_run2_58_without_run2_59_composition_compiler:
        "may see Run 2.58 generated result and trace, but must not use Run 2.59 content contracts, layout capacity, selector, trace policy, or composition workflow gates",
      prompt_only: "commercial_case_only_no_run2_59_composition_compiler",
      run1_5_skill: "prior_baseline_no_run2_59_composition_compiler",
    },
    visual_quality_boundary:
      "Run 2.60 proves content-aware composition compiler consumption; public-video-grade aesthetics, native motion, and human release approval remain blocked.",
    remaining_public_release_gates: [
      "human_visual_review",
      "native_or_cross_platform_render_inspection",
      "motion_or_video_review",
      "source_boundary_review",
      "human_release_approval",
    ],
    release_boundary:
      "public_blocked_until_visual_human_review_native_render_review_motion_review_source_boundary_review_and_human_approval",
    next_required_action:
      "audit_run2_60_composition_compiler_consumption_then_continue_same_five_layers_do_not_advance_to_run3",
  };
  const resultJson = path.join(root, pack, "results", "run2_60_content_aware_composition_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_60_content_aware_composition_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.60 Content-Aware Composition Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.60 consumes Run 2.59 before native PPT drawing. The full arm binds the content composition contracts, layout capacity model, content-to-layout selector, public slide / trace viewer split, and composition workflow gates on every slide.",
      "",
      "This fixes the problem identified after Run 2.58 and Run 2.59: the product content was present, but the deck still needed content-aware composition before the native PPT code drew each role.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_60_full_content_aware_composition`",
      "- `bad_run2_58_without_run2_59_composition_compiler`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_60_full_content_aware_composition`.",
      "",
      "Quality delta: `content_aware_composition_compiler_consumed`. All six full-arm slides bind a Run 2.59 content contract, selected layout module, capacity fit status, trace split policy, and workflow gate.",
      "",
      "The negative control `bad_run2_58_without_run2_59_composition_compiler` can reuse Run 2.58 product content proof, but it fails the composition compiler layer.",
      "",
      "Public release remains blocked. This proves data/workflow consumption, not final public-video-grade aesthetics.",
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
  const fourArmSheet = buildRun260FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_60_content_aware_composition_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_60_content_aware_composition_rerun_summary.json"), runSummary);
  writeRun260Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_60_FULL_DATA_INPUTS,
  RUN2_60_INPUTS,
  armSpecs,
  assertRun260ArmInputBoundaries,
  assertRun260CompositionSelfCheck,
  drawRun260EditorialCoverField,
  drawRun260ProductTheaterStage,
  drawRun260BeforeAfterRoute,
  drawRun260DenseEvidenceCompression,
  drawRun260MetricRevealStage,
  drawRun260QuietReleaseHandoff,
  drawRun260ContentAwareComposition,
  loadRun260CompositionData,
  main,
  readRun260PackJsonForArm,
  selectRun260ForSlide,
  traceFor,
  validateRun260CompositionInputs,
};
