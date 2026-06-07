import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.62";
const selectedUsecaseId = "usecase_design_to_production_platform_launch";
const RUN2_62_FULL_STATUS = "run2_61_narrative_proof_dataset_consumed_before_native_ppt_drawing";
const RUN2_62_BAD_STATUS = "fail_missing_run2_61";
const RUN2_62_POLICY = "run2_61_narrative_proof_dataset_consumed";
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
  ink: "#11161d",
  dark: "#111820",
  paper: "#f4efe4",
  white: "#ffffff",
  muted: "#56616d",
  line: "#d8d4ca",
  blue: "#2b63d9",
  cyan: "#74c6d7",
  red: "#df4f33",
  green: "#108665",
  amber: "#e4b84e",
  slate: "#e8edf0",
};

const RUN2_62_INPUTS = {
  run261Result: `${pack}/results/run2_61_narrative_proof_dataset_result.json`,
  run261Narrative: `${pack}/run2_61_narrative_proof_dataset.json`,
  run261Selector: `${pack}/run2_61_story_to_visual_carrier_selector.json`,
  run261Fusion: `${pack}/run2_61_text_socket_fusion_contracts.json`,
  run261SourcePolicy: `${pack}/run2_61_source_to_public_proof_policy.json`,
  run261WorkflowGates: `${pack}/run2_61_narrative_workflow_gates.json`,
  run260Result: `${pack}/results/run2_60_content_aware_composition_rerun_result.json`,
  run260FullTrace: `outputs/${threadId}/presentations/ppt-run2-60-full-vulca/trace_manifest.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_62_FULL_DATA_INPUTS = Object.values(RUN2_62_INPUTS);
const RUN2_62_BAD_DATA_INPUTS = [
  RUN2_62_INPUTS.run260Result,
  RUN2_62_INPUTS.run260FullTrace,
  RUN2_62_INPUTS.commercialUsecaseBank,
  RUN2_62_INPUTS.sources,
];

const requiredRun261TraceFields = [
  "run2_61_narrative_proof_id",
  "run2_61_visual_carrier_selector_id",
  "run2_61_text_socket_fusion_contract_id",
  "run2_61_public_proof_replacement_id",
  "run2_61_narrative_workflow_gate_id",
];

const baseSlides = [
  { role: "cover", title: "A real brief becomes editable PPT proof." },
  { role: "setup", title: "Sources compile into design memory before drawing." },
  { role: "contrast", title: "The difference is mechanism, not taste." },
  { role: "proof", title: "Trace proves the data path was used." },
  { role: "climax", title: "The product moment is the operating loop." },
  { role: "close", title: "Generated proof exists; release remains gated." },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-62-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.62 / CONTROL",
    footer: "prompt_only | brief only | no Run 2.61 contract",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_62_FULL_DATA_INPUTS, "drawRun262NarrativeProofComposition"],
    palette: {
      bg: "#f7f8fa",
      rail: "#394150",
      accent: C.blue,
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d9dee5",
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
    slug: "ppt-run2-62-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.62 / RUN 1.5",
    footer: "run1_5_skill | prior baseline | no Run 2.61 contract",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_62_FULL_DATA_INPUTS, "drawRun262NarrativeProofComposition"],
    palette: {
      bg: "#f3f7fb",
      rail: "#283247",
      accent: C.green,
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d2dce7",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Readable product lab explanation.",
        "Workflow story exists, but no narrative proof contract.",
        "Comparison remains generic.",
        "Proof is process-led.",
        "Product moment is named, not contracted.",
        "Close remains correct but thin.",
      ][index],
    })),
  },
  {
    armId: "run2_62_full_narrative_proof",
    slug: "ppt-run2-62-full-vulca",
    label: "Run 2.62 full narrative proof",
    kicker: "RUN 2.62 / NARRATIVE PROOF",
    footer: "run2_62_full_narrative_proof | consumes Run 2.61 | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      ...RUN2_62_FULL_DATA_INPUTS,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_61_narrative_proof_dataset.json",
      "run2_61_story_to_visual_carrier_selector.json",
      "run2_61_text_socket_fusion_contracts.json",
      "run2_61_source_to_public_proof_policy.json",
      "run2_61_narrative_workflow_gates.json",
      "run2_60_content_aware_composition_rerun_result.json",
      "ppt-run2-60-full-vulca/trace_manifest.json",
      RUN2_62_POLICY,
    ],
    forbidden: [
      "source layouts",
      "copied screenshots",
      "raw tutorial media",
      "image_only_output_claim",
      "generic product claims",
      "native_drawing_before_run2_61_narrative_proof_dataset",
    ],
    palette: {
      bg: "#f4efe4",
      rail: C.dark,
      accent: C.red,
      accent2: C.blue,
      panel: C.white,
      title: "#0e1218",
      muted: "#56616d",
      rule: "#d8cfbf",
      surface: "#edf2f0",
    },
    slides: baseSlides,
  },
  {
    armId: "bad_run2_60_without_run2_61_narrative_proof_dataset",
    slug: "ppt-run2-62-bad-without-narrative-proof",
    label: "Bad missing Run 2.61 narrative proof",
    kicker: "RUN 2.62 / BAD CONTROL",
    footer: "bad_run2_60_without_run2_61_narrative_proof_dataset | Run 2.60 only",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_62_BAD_DATA_INPUTS],
    data_input_manifest: ["run2_60_generated_without_run2_61_narrative_proof_dataset"],
    forbidden: [
      "run2_61_narrative_proof_dataset.json",
      "run2_61_story_to_visual_carrier_selector.json",
      "run2_61_text_socket_fusion_contracts.json",
      "run2_61_source_to_public_proof_policy.json",
      "run2_61_narrative_workflow_gates.json",
      "drawRun262NarrativeProofComposition",
      "run2_61_narrative_proof_dataset_consumed_before_native_ppt_drawing",
    ],
    palette: {
      bg: "#efe7d5",
      rail: "#6d603b",
      accent: "#8a7143",
      panel: "#faf4e8",
      title: "#2b271e",
      muted: "#665e4d",
      rule: "#dbcfb8",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Run 2.60 looks cleaner, but it still lacks the 2.61 narrative proof layer.",
        "The source story remains compressed before it becomes a slide.",
        "The contrast can still become a generic mechanism diagram.",
        "Trace exists, but public proof replacement is not contracted.",
        "The operating loop exists, but the required answer is not socketed.",
        "The close has no Run 2.61 consumer proof.",
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
    socketBindingCount: 0,
    requiredAnswerVisible: false,
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

function armUsesFullRun262NarrativeProof(arm) {
  return arm.armId === "run2_62_full_narrative_proof";
}

function armUsesBadRun262Data(arm) {
  return arm.armId === "bad_run2_60_without_run2_61_narrative_proof_dataset";
}

function assertRun262ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun262NarrativeProof(arm)) {
    for (const input of RUN2_62_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesBadRun262Data(arm)) {
    for (const input of RUN2_62_BAD_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow bad-control input ${input}`);
    }
    for (const input of [
      RUN2_62_INPUTS.run261Result,
      RUN2_62_INPUTS.run261Narrative,
      RUN2_62_INPUTS.run261Selector,
      RUN2_62_INPUTS.run261Fusion,
      RUN2_62_INPUTS.run261SourcePolicy,
      RUN2_62_INPUTS.run261WorkflowGates,
    ]) {
      if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    }
    return;
  }
  for (const input of RUN2_62_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun262PackJsonForArm(arm, relPath) {
  assertRun262ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (!armUsesFullRun262NarrativeProof(arm) && !armUsesBadRun262Data(arm)) {
    throw new Error(`${arm.armId} cannot read Run 2.62 pack data`);
  }
  return readJson(relPath);
}

function assertSelectedUsecase(value, label) {
  if (value !== selectedUsecaseId) throw new Error(`Run 2.62 selected usecase mismatch in ${label}`);
}

function validateRun262NarrativeInputs(data) {
  if (data.run261Result?.status !== "run2_61_narrative_proof_dataset_ready_public_blocked") {
    throw new Error("Run 2.62 must consume Run 2.61 narrative proof result");
  }
  if (data.run261Narrative?.status !== "run2_61_narrative_proof_dataset_ready_public_blocked") {
    throw new Error("Run 2.62 must consume Run 2.61 narrative proof dataset");
  }
  if (data.run261Selector?.status !== "run2_61_story_to_visual_carrier_selector_ready_public_blocked") {
    throw new Error("Run 2.62 must consume Run 2.61 visual carrier selector");
  }
  if (data.run261Fusion?.status !== "run2_61_text_socket_fusion_contracts_ready_public_blocked") {
    throw new Error("Run 2.62 must consume Run 2.61 text socket fusion contracts");
  }
  if (data.run261SourcePolicy?.status !== "run2_61_source_to_public_proof_policy_ready_public_blocked") {
    throw new Error("Run 2.62 must consume Run 2.61 source-to-public-proof policy");
  }
  if (data.run261WorkflowGates?.status !== "run2_61_narrative_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.62 must consume Run 2.61 narrative workflow gates");
  }
  if (data.run260Result?.status !== "run2_60_content_aware_composition_rerun_public_blocked") {
    throw new Error("Run 2.62 must compare against Run 2.60 result");
  }
  if (data.run260FullTrace?.arm_id !== "run2_60_full_content_aware_composition") {
    throw new Error("Run 2.62 must compare against Run 2.60 full trace");
  }
  assertSelectedUsecase(data.run261Result?.selected_usecase_id, "run2_61_result");
  assertSelectedUsecase(data.run260Result?.selected_usecase_id, "run2_60_result");
  assertSelectedUsecase(data.run260FullTrace?.selected_usecase_id, "run2_60_full_trace");
  const roles = new Set(baseSlides.map((slide) => slide.role));
  const narrative = data.run261Narrative.narrative_proof_records ?? [];
  const selectors = data.run261Selector.story_to_visual_carrier_records ?? [];
  const fusions = data.run261Fusion.text_socket_fusion_contracts ?? [];
  const gates = data.run261WorkflowGates.narrative_workflow_gates ?? [];
  if (narrative.length !== 6 || !narrative.every((record) => roles.has(record.role))) {
    throw new Error("Run 2.62 requires six Run 2.61 narrative proof records");
  }
  if (selectors.length !== 6 || !selectors.every((record) => roles.has(record.role))) {
    throw new Error("Run 2.62 requires six Run 2.61 visual carrier selections");
  }
  if (fusions.length !== 6 || !fusions.every((record) => roles.has(record.role))) {
    throw new Error("Run 2.62 requires six Run 2.61 text socket fusion contracts");
  }
  if (gates.length !== 6 || !gates.every((record) => roles.has(record.role))) {
    throw new Error("Run 2.62 requires six Run 2.61 narrative workflow gates");
  }
  for (const record of narrative) {
    const selector = selectors.find((item) => item.role === record.role);
    const fusion = fusions.find((item) => item.role === record.role);
    const gate = gates.find((item) => item.role === record.role);
    if (!selector || !fusion || !gate) throw new Error(`Run 2.62 missing Run 2.61 role links for ${record.role}`);
    if (selector.source_narrative_proof_id !== record.narrative_proof_id) throw new Error(`Run 2.62 selector mismatch for ${record.role}`);
    if (fusion.source_narrative_proof_id !== record.narrative_proof_id) throw new Error(`Run 2.62 fusion mismatch for ${record.role}`);
    if (fusion.source_visual_carrier_selector_id !== selector.selector_id) throw new Error(`Run 2.62 fusion/selector mismatch for ${record.role}`);
    if (gate.source_narrative_proof_id !== record.narrative_proof_id) throw new Error(`Run 2.62 gate mismatch for ${record.role}`);
    for (const field of requiredRun261TraceFields) {
      if (!(gate.next_run_required_trace_fields ?? []).includes(field)) throw new Error(`Run 2.62 missing required Run 2.61 trace field ${field}`);
    }
    if ((fusion.socket_bindings ?? []).length < 5) throw new Error(`Run 2.62 requires at least five socket bindings for ${record.role}`);
    if ((record.density_budget?.maximum_public_visible_words ?? 999) > 110) throw new Error(`Run 2.62 public density budget too high for ${record.role}`);
  }
}

function loadRun262NarrativeProofData(arm) {
  const data = {
    run261Result: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.run261Result),
    run261Narrative: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.run261Narrative),
    run261Selector: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.run261Selector),
    run261Fusion: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.run261Fusion),
    run261SourcePolicy: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.run261SourcePolicy),
    run261WorkflowGates: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.run261WorkflowGates),
    run260Result: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.run260Result),
    run260FullTrace: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.run260FullTrace),
    commercialUsecaseBank: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.commercialUsecaseBank),
    sources: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.sources),
  };
  validateRun262NarrativeInputs(data);
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_62_narrative_proof_inputs_ready",
  };
}

function loadRun262BadControlData(arm) {
  const data = {
    run260Result: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.run260Result),
    run260FullTrace: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.run260FullTrace),
    commercialUsecaseBank: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.commercialUsecaseBank),
    sources: readRun262PackJsonForArm(arm, RUN2_62_INPUTS.sources),
  };
  if (data.run260Result?.status !== "run2_60_content_aware_composition_rerun_public_blocked") {
    throw new Error("Run 2.62 bad control must read Run 2.60 result");
  }
  if (data.run260FullTrace?.arm_id !== "run2_60_full_content_aware_composition") {
    throw new Error("Run 2.62 bad control must read Run 2.60 full trace");
  }
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
  };
}

function selectRun262ForSlide(role, data) {
  const narrative = (data.run261Narrative.narrative_proof_records ?? []).find((item) => item.role === role);
  const selector = (data.run261Selector.story_to_visual_carrier_records ?? []).find((item) => item.role === role);
  const fusion = (data.run261Fusion.text_socket_fusion_contracts ?? []).find((item) => item.role === role);
  const gate = (data.run261WorkflowGates.narrative_workflow_gates ?? []).find((item) => item.role === role);
  const priorTraceSlide = (data.run260FullTrace.slides ?? []).find((item) => item.role === role);
  if (!narrative || !selector || !fusion || !gate || !priorTraceSlide) {
    throw new Error(`Run 2.62 missing role narrative proof selection for ${role}`);
  }
  return {
    role,
    narrative,
    selector,
    fusion,
    gate,
    priorTraceSlide,
    sourcePolicy: data.run261SourcePolicy,
    usecase: data.usecase,
  };
}

const ROLE_RENDERERS = {
  cover: "drawRun262ContractCover",
  setup: "drawRun262SourceToSocketStage",
  contrast: "drawRun262BeforeAfterProofRoute",
  proof: "drawRun262InspectionProofBoard",
  climax: "drawRun262ClimaxResultObject",
  close: "drawRun262ReleaseGateHandoff",
};

function drawProofBadges(slide, metrics, labels, x, y, w, fill = "#fffaf2") {
  const values = Array.isArray(labels) ? labels.slice(0, 3) : [];
  const gap = 10;
  const chipW = (w - gap * Math.max(0, values.length - 1)) / Math.max(1, values.length);
  values.forEach((label, index) => chip(slide, metrics, label, x + index * (chipW + gap), y, chipW, fill));
  registerProof(metrics, values.length);
}

function drawSocketRail(slide, metrics, selection, x, y, w) {
  rect(slide, x, y, w, 120, "#fffdf8", colorLine("#dbcda8", 1));
  socketText(slide, metrics, "socket plan", x + 14, y + 12, 110, 12, {
    fontSize: 8,
    mono: true,
    bold: true,
    color: C.red,
    max: 24,
  });
  const sockets = (selection.fusion.socket_bindings ?? []).slice(0, 5);
  sockets.forEach((socket, index) => {
    const itemY = y + 34 + index * 15;
    rect(slide, x + 14, itemY + 5, 8, 8, index === 0 ? C.red : C.blue, colorLine("transparent", 0));
    socketText(slide, metrics, `${socket.copy_unit_key} -> ${socket.owning_shape_role}`, x + 30, itemY, w - 44, 10, {
      fontSize: 7.2,
      mono: true,
      color: C.ink,
      max: 64,
    });
  });
  metrics.socketBindingCount = selection.fusion.socket_bindings.length;
}

function drawPublicProofProxy(slide, metrics, selection, x, y, w, h) {
  const replacement = selection.narrative.public_proof_replacement ?? {};
  rect(slide, x, y, w, h, C.dark, colorLine(C.dark, 1));
  socketText(slide, metrics, replacement.replacement_type ?? "public proof proxy", x + 24, y + 24, w - 48, 22, {
    fontSize: 12,
    mono: true,
    bold: true,
    color: C.cyan,
    max: 44,
  });
  socketText(slide, metrics, selection.narrative.proof_payload?.primary_evidence_object ?? "", x + 30, y + 72, w - 60, 54, {
    fontSize: 22,
    title: true,
    bold: true,
    color: C.white,
    align: "center",
    max: 64,
  });
  const secondary = selection.narrative.proof_payload?.secondary_evidence_objects ?? [];
  secondary.slice(0, 3).forEach((label, index) => {
    rect(slide, x + 42 + index * ((w - 120) / 3), y + h - 88, (w - 150) / 3, 42, index === 0 ? "#fff2d6" : "#edf6f1", colorLine("#9ca8b3", 1));
    socketText(slide, metrics, label, x + 52 + index * ((w - 120) / 3), y + h - 72, (w - 170) / 3, 12, {
      fontSize: 7.5,
      bold: true,
      align: "center",
      color: C.ink,
      max: 30,
    });
  });
  registerProof(metrics, Math.max(2, secondary.length + 1));
}

function drawRun262ContractCover(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.narrative.copy_units.headline, 76, 118, 506, 84, {
    fontSize: 34,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 74,
  });
  socketText(slide, metrics, selection.narrative.required_answer, 80, 214, 500, 50, {
    fontSize: 13,
    color: arm.palette.muted,
    max: 120,
  });
  metrics.requiredAnswerVisible = true;
  drawProofBadges(slide, metrics, selection.narrative.copy_units.proof_badges, 80, 306, 460);
  drawPublicProofProxy(slide, metrics, selection, 632, 108, 500, 340);
  drawSocketRail(slide, metrics, selection, 80, 402, 460);
  registerZones(metrics, 8);
}

function drawRun262SourceToSocketStage(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.narrative.copy_units.headline, 78, 110, 510, 66, {
    fontSize: 29,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 76,
  });
  socketText(slide, metrics, selection.narrative.required_answer, 82, 190, 500, 44, {
    fontSize: 12,
    color: arm.palette.muted,
    max: 116,
  });
  metrics.requiredAnswerVisible = true;
  rect(slide, 626, 118, 482, 318, "#111820", colorLine("#111820", 1));
  ["brief", "source pack", "proof payload", "visual carrier", "socket fusion", "PPT"].forEach((label, index) => {
    const x = 664 + (index % 3) * 140;
    const y = 166 + Math.floor(index / 3) * 124;
    const fill = index >= 3 ? "#e8f5ef" : "#fff2d6";
    if (index === 2 || index === 4) ellipse(slide, x, y, 112, 76, fill, colorLine("#95a8b8", 1));
    else rect(slide, x, y, 112, 76, fill, colorLine("#95a8b8", 1));
    socketText(slide, metrics, label, x + 16, y + 30, 80, 12, {
      fontSize: 8,
      bold: true,
      align: "center",
      max: 24,
    });
  });
  drawProofBadges(slide, metrics, selection.narrative.copy_units.proof_badges, 84, 294, 470);
  drawSocketRail(slide, metrics, selection, 84, 396, 470);
  registerZones(metrics, 8);
}

function drawRun262BeforeAfterProofRoute(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.narrative.copy_units.headline, 72, 104, 550, 58, {
    fontSize: 28,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 72,
  });
  socketText(slide, metrics, selection.narrative.required_answer, 76, 174, 536, 38, {
    fontSize: 12,
    color: arm.palette.muted,
    max: 108,
  });
  metrics.requiredAnswerVisible = true;
  const proof = selection.narrative.proof_payload;
  rect(slide, 90, 300, 260, 116, "#fff8e4", colorLine("#d1bd80", 1));
  socketText(slide, metrics, proof.before_state, 116, 342, 208, 24, {
    fontSize: 11,
    bold: true,
    align: "center",
    max: 48,
  });
  ellipse(slide, 474, 254, 168, 168, "#f4dfd4", colorLine(C.red, 2));
  socketText(slide, metrics, "contracted turn", 506, 322, 104, 18, {
    fontSize: 9.6,
    bold: true,
    align: "center",
    color: C.red,
    max: 28,
  });
  rect(slide, 792, 254, 286, 164, "#111820", colorLine(C.cyan, 2));
  socketText(slide, metrics, proof.after_state, 830, 312, 210, 28, {
    fontSize: 14,
    title: true,
    bold: true,
    align: "center",
    color: C.white,
    max: 48,
  });
  rect(slide, 350, 354, 124, 6, C.red, colorLine("transparent", 0));
  rect(slide, 642, 334, 150, 6, C.blue, colorLine("transparent", 0));
  drawProofBadges(slide, metrics, selection.narrative.copy_units.proof_badges, 96, 492, 842);
  drawSocketRail(slide, metrics, selection, 960, 462, 180);
  registerZones(metrics, 8);
}

function drawRun262InspectionProofBoard(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.narrative.copy_units.headline, 70, 96, 520, 54, {
    fontSize: 27,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 60,
  });
  socketText(slide, metrics, selection.narrative.required_answer, 74, 162, 494, 34, {
    fontSize: 12,
    color: arm.palette.muted,
    max: 98,
  });
  metrics.requiredAnswerVisible = true;
  rect(slide, 622, 108, 506, 408, "#f8fafb", colorLine("#c7d1d8", 1));
  socketText(slide, metrics, "inspection board", 658, 140, 166, 18, {
    fontSize: 12,
    mono: true,
    bold: true,
    color: C.red,
    max: 28,
  });
  const rows = [
    ["proof object", selection.narrative.proof_payload.primary_evidence_object],
    ["replacement", selection.narrative.public_proof_replacement.replacement_type],
    ["carrier", selection.selector.visual_carrier_type],
    ["gate", selection.gate.gate_id],
  ];
  rows.forEach(([label, value], index) => {
    const x = 658 + (index % 2) * 214;
    const y = 188 + Math.floor(index / 2) * 126;
    rect(slide, x, y, 184, 80, index === 0 ? "#fff2d6" : C.white, colorLine("#cfd8e0", 1));
    socketText(slide, metrics, label, x + 14, y + 13, 150, 12, {
      fontSize: 7.6,
      mono: true,
      bold: true,
      color: C.red,
      max: 22,
    });
    socketText(slide, metrics, value, x + 14, y + 32, 150, 26, {
      fontSize: 8.4,
      bold: true,
      max: 52,
    });
  });
  drawProofBadges(slide, metrics, selection.narrative.copy_units.proof_badges, 74, 262, 470);
  drawSocketRail(slide, metrics, selection, 74, 388, 470);
  registerZones(metrics, 8);
}

function drawRun262ClimaxResultObject(slide, arm, spec, selection, metrics) {
  rect(slide, 54, 92, 1136, 544, C.dark, colorLine(C.dark, 1));
  socketText(slide, metrics, selection.narrative.copy_units.headline, 94, 128, 470, 78, {
    fontSize: 32,
    title: true,
    bold: true,
    color: C.white,
    max: 64,
  });
  socketText(slide, metrics, selection.narrative.required_answer, 98, 222, 420, 48, {
    fontSize: 12,
    color: "#dbe5ec",
    max: 100,
  });
  metrics.requiredAnswerVisible = true;
  ellipse(slide, 734, 188, 330, 250, "#f8fafb", colorLine(C.cyan, 2));
  socketText(slide, metrics, selection.narrative.proof_payload.primary_evidence_object, 796, 280, 206, 38, {
    fontSize: 19,
    title: true,
    bold: true,
    color: C.ink,
    align: "center",
    max: 42,
  });
  ["brief", "memory", "code", "editable PPT"].forEach((label, index) => {
    const x = 612 + index * 132;
    const y = 474 - (index % 2) * 36;
    rect(slide, x, y, 104, 56, index === 3 ? C.red : "#edf6f1", colorLine(index === 3 ? C.red : "#94a3b8", 1));
    socketText(slide, metrics, label, x + 12, y + 22, 80, 12, {
      fontSize: 8.5,
      bold: true,
      align: "center",
      color: index === 3 ? C.white : C.ink,
      max: 22,
    });
  });
  drawProofBadges(slide, metrics, selection.narrative.copy_units.proof_badges, 96, 356, 404);
  drawSocketRail(slide, metrics, selection, 96, 462, 404);
  registerZones(metrics, 8);
}

function drawRun262ReleaseGateHandoff(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.narrative.copy_units.headline, 82, 120, 520, 68, {
    fontSize: 30,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 66,
  });
  socketText(slide, metrics, selection.narrative.required_answer, 86, 204, 488, 42, {
    fontSize: 12,
    color: arm.palette.muted,
    max: 98,
  });
  metrics.requiredAnswerVisible = true;
  const marks = [
    ["2.60", "generated proof", 642, 162, "#eef3f6"],
    ["2.61", "narrative contracts", 792, 282, "#fff2d6"],
    ["2.62", "consumer rerun", 958, 162, "#e8f5ef"],
  ];
  marks.forEach(([run, label, x, y, fill], index) => {
    ellipse(slide, x, y, 118, 118, fill, colorLine(index === 2 ? C.red : "#99aab8", index === 2 ? 2 : 1));
    socketText(slide, metrics, run, x + 28, y + 34, 62, 24, {
      fontSize: 18,
      title: true,
      bold: true,
      align: "center",
      color: arm.palette.title,
      max: 8,
    });
    socketText(slide, metrics, label, x + 14, y + 66, 90, 16, {
      fontSize: 7.6,
      align: "center",
      bold: true,
      max: 30,
    });
    if (index < marks.length - 1) rect(slide, x + 118, y + 56, 64, 6, C.blue, colorLine("transparent", 0));
  });
  rect(slide, 690, 470, 348, 54, "#111820", colorLine("#111820", 1));
  socketText(slide, metrics, selection.narrative.public_proof_replacement.replacement_rule, 714, 486, 300, 20, {
    fontSize: 8.8,
    bold: true,
    align: "center",
    color: C.white,
    max: 84,
  });
  drawProofBadges(slide, metrics, selection.narrative.copy_units.proof_badges, 86, 332, 474);
  drawSocketRail(slide, metrics, selection, 86, 434, 474);
  registerZones(metrics, 8);
}

const RUN2_62_RENDERERS = {
  cover: drawRun262ContractCover,
  setup: drawRun262SourceToSocketStage,
  contrast: drawRun262BeforeAfterProofRoute,
  proof: drawRun262InspectionProofBoard,
  climax: drawRun262ClimaxResultObject,
  close: drawRun262ReleaseGateHandoff,
};

function markRun262NarrativeProof(metrics, selection) {
  metrics.codeModuleIds.add("drawRun262NarrativeProofComposition");
  metrics.codeModuleIds.add(ROLE_RENDERERS[selection.role]);
  metrics.productSystemSurfaceKind = selection.selector.visual_carrier_type;
  metrics.socketBindingCount = selection.fusion.socket_bindings.length;
  registerProof(metrics, Math.max(2, selection.narrative.proof_payload.secondary_evidence_objects.length + 1));
  registerZones(metrics, 8);
}

function drawRun262NarrativeProofComposition(slide, arm, spec, selection, metrics) {
  const renderer = RUN2_62_RENDERERS[spec.role];
  if (!renderer) throw new Error(`Run 2.62 missing role renderer for ${spec.role}`);
  renderer(slide, arm, spec, selection, metrics);
  markRun262NarrativeProof(metrics, selection);
}

function drawBadRun262FallbackSlide(slide, arm, spec, badData, metrics) {
  const prior = (badData.run260FullTrace?.slides ?? []).find((slideItem) => slideItem.role === spec.role);
  socketText(slide, metrics, spec.title, 76, 118, 540, 78, {
    fontSize: 28,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 104,
  });
  socketText(slide, metrics, "This arm can read Run 2.60 generated proof, but it cannot read Run 2.61 narrative proof, visual carrier, socket fusion, source policy, or workflow gate artifacts.", 80, 216, 500, 60, {
    fontSize: 13,
    color: arm.palette.muted,
    max: 150,
  });
  rect(slide, 626, 130, 474, 314, arm.palette.panel, colorLine(arm.palette.rule, 1));
  socketText(slide, metrics, "no narrative proof contract", 666, 170, 280, 24, {
    fontSize: 16,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 44,
  });
  ["2.60 trace", "compressed claim", "generic carrier", "unsocketed answer"].forEach((label, index) => {
    rect(slide, 668 + (index % 2) * 180, 238 + Math.floor(index / 2) * 78, 142, 50, "#eee2c7", colorLine("#c6ad78", 1));
    socketText(slide, metrics, label, 684 + (index % 2) * 180, 254 + Math.floor(index / 2) * 78, 110, 16, {
      fontSize: 8.8,
      bold: true,
      align: "center",
      max: 36,
    });
  });
  socketText(slide, metrics, prior?.layout_metrics?.product_system_surface_kind ?? "Run 2.60 trace exists", 646, 470, 416, 26, {
    fontSize: 10,
    color: arm.palette.muted,
    max: 92,
  });
  metrics.productSystemSurfaceKind = "run2_60_without_run2_61_narrative_proof_dataset";
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
  socketText(slide, metrics, "This arm does not receive Run 2.61 narrative proof contracts, so it cannot bind reader answer, proof object, visual carrier, and text sockets before drawing.", 80, 252, 526, 56, {
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
  socketText(slide, metrics, mode === "run1_5" ? "Prior skill: readable, but no Run 2.61 narrative proof consumption." : "Prompt-only: no narrative proof, no visual carrier selector, no socket fusion.", 108, 398, 420, 38, {
    fontSize: 17,
    bold: true,
    title: true,
    color: arm.palette.title,
    max: 92,
  });
  metrics.productSystemSurfaceKind = mode === "run1_5" ? "run1_5_without_run2_61_narrative_proof" : "prompt_only_without_run2_61_narrative_proof";
  registerProof(metrics, 2);
  registerZones(metrics, 3);
}

function renderRun262Slide(presentation, spec, arm, n, narrativeData, badData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun262NarrativeProof(arm)) {
    const selection = selectRun262ForSlide(spec.role, narrativeData);
    drawRun262NarrativeProofComposition(slide, arm, spec, selection, metrics);
  } else if (armUsesBadRun262Data(arm)) {
    drawBadRun262FallbackSlide(slide, arm, spec, badData, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function blankRun261Fields() {
  return {
    run2_61_narrative_proof_id: "",
    run2_61_visual_carrier_selector_id: "",
    run2_61_text_socket_fusion_contract_id: "",
    run2_61_public_proof_replacement_id: "",
    run2_61_narrative_workflow_gate_id: "",
  };
}

function traceFor(arm, context = {}) {
  assertRun262ArmInputBoundaries(arm);
  const fullRun262 = armUsesFullRun262NarrativeProof(arm);
  const badRun262 = armUsesBadRun262Data(arm);
  const narrativeData = fullRun262 ? context.narrativeData ?? loadRun262NarrativeProofData(arm) : null;
  const badData = badRun262 ? context.badData ?? loadRun262BadControlData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun262 || badRun262 ? selectedUsecaseId : "",
    source_repair_run_id: fullRun262 ? "2.61" : "",
    source_generated_run_id: fullRun262 || badRun262 ? "2.60" : "",
    run2_62_narrative_proof_consumption_status: fullRun262
      ? RUN2_62_FULL_STATUS
      : badRun262
        ? RUN2_62_BAD_STATUS
        : "boundary_control_no_run2_61_narrative_proof_dataset",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.62 narrative proof rerun from scripts/generate_ppt_run2_62_narrative_proof_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun262 ? selectRun262ForSlide(slide.role, narrativeData) : null;
      const run261Fields = fullRun262
        ? {
            run2_61_narrative_proof_id: selection.narrative.narrative_proof_id,
            run2_61_visual_carrier_selector_id: selection.selector.selector_id,
            run2_61_text_socket_fusion_contract_id: selection.fusion.fusion_contract_id,
            run2_61_public_proof_replacement_id: selection.narrative.public_proof_replacement.replacement_id,
            run2_61_narrative_workflow_gate_id: selection.gate.gate_id,
          }
        : blankRun261Fields();
      const run262Fields = {
        run2_62_code_module_ids: fullRun262 ? Array.from(roleMetrics.codeModuleIds) : [],
        run2_62_narrative_proof_consumption_status: fullRun262 ? "pass_internal" : badRun262 ? RUN2_62_BAD_STATUS : "",
        run2_62_socket_binding_count: fullRun262 ? roleMetrics.socketBindingCount : 0,
        run2_62_public_proof_object_count: roleMetrics.proofObjects,
        run2_62_required_answer_visible: fullRun262 ? (roleMetrics.requiredAnswerVisible ? "pass_internal" : "fail_missing_required_answer") : badRun262 ? RUN2_62_BAD_STATUS : "",
      };
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        source_run2_60_slide_id: fullRun262 ? selection.priorTraceSlide.slide_id : badRun262 ? slide.role : "",
        ...run261Fields,
        ...run262Fields,
        layout_metrics: {
          text_box_count: roleMetrics.textBoxCount,
          visible_words: roleMetrics.visibleWords,
          text_density_tier: roleMetrics.visibleWords >= 86 ? "bounded_dense" : "public_compact",
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

function assertRun262NarrativeProofSelfCheck(trace) {
  if (trace.arm_id === "run2_62_full_narrative_proof") {
    if (trace.run2_62_narrative_proof_consumption_status !== RUN2_62_FULL_STATUS) {
      throw new Error("Run 2.62 full trace did not consume Run 2.61 narrative proof dataset before native PPT drawing");
    }
    for (const slide of trace.slides) {
      if (!String(slide.run2_61_narrative_proof_id ?? "").startsWith("narrative_proof_2_61_")) {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} missing Run 2.61 narrative proof`);
      }
      if (!String(slide.run2_61_visual_carrier_selector_id ?? "").startsWith("visual_carrier_selector_2_61_")) {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} missing Run 2.61 visual carrier selector`);
      }
      if (!String(slide.run2_61_text_socket_fusion_contract_id ?? "").startsWith("text_socket_fusion_2_61_")) {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} missing Run 2.61 text socket fusion`);
      }
      if (!String(slide.run2_61_public_proof_replacement_id ?? "").startsWith("public_proof_replacement_2_61_")) {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} missing Run 2.61 public proof replacement`);
      }
      if (!String(slide.run2_61_narrative_workflow_gate_id ?? "").startsWith("gate_2_61_")) {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} missing Run 2.61 narrative gate`);
      }
      if (slide.run2_62_narrative_proof_consumption_status !== "pass_internal") {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} did not pass narrative proof consumption`);
      }
      if ((slide.run2_62_socket_binding_count ?? 0) < 5) {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} missing socket bindings`);
      }
      if ((slide.run2_62_public_proof_object_count ?? 0) < 2) {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} missing public proof objects`);
      }
      if (slide.run2_62_required_answer_visible !== "pass_internal") {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} missing required answer`);
      }
      if (!(slide.run2_62_code_module_ids ?? []).includes("drawRun262NarrativeProofComposition")) {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} missing narrative proof composition module`);
      }
      if ((slide.layout_metrics?.visible_words ?? 0) > 120) {
        throw new Error(`Run 2.62 full slide ${slide.slide_id} exceeds public visible-word capacity`);
      }
    }
  }
  if (trace.arm_id === "bad_run2_60_without_run2_61_narrative_proof_dataset") {
    for (const slide of trace.slides) {
      for (const field of requiredRun261TraceFields) {
        if (slide[field] !== "") throw new Error(`Run 2.62 bad slide ${slide.slide_id} leaked ${field}`);
      }
      if (slide.run2_62_narrative_proof_consumption_status !== RUN2_62_BAD_STATUS) {
        throw new Error(`Run 2.62 bad slide ${slide.slide_id} must fail missing Run 2.61`);
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

function buildRun262FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-62-four-arm-contact-sheet.png"),
    "Run 2.62 narrative proof consumption comparison",
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
    ["Run 2.62", "ppt-run2-62-full-vulca"],
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
      "required proof objects: Run 2.61 narrative proof, visual carrier selector, text socket fusion, public proof replacement, workflow gate",
      "source requirements: full arm reads Run 2.61 artifacts and Run 2.60 full trace before native PPT drawing",
      "negative control: bad arm can read Run 2.60 generated result and trace, but cannot read Run 2.61 narrative proof artifacts",
      "profile-specific QA gates: public slide surface must remain bounded; raw source detail belongs in viewer trace",
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
  const narrativeData = armUsesFullRun262NarrativeProof(arm) ? loadRun262NarrativeProofData(arm) : null;
  const badData = armUsesBadRun262Data(arm) ? loadRun262BadControlData(arm) : null;
  const slides = arm.slides.map((slide, index) =>
    renderRun262Slide(presentation, slide, arm, index + 1, narrativeData, badData, metricsByRole),
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
  const trace = traceFor(arm, { narrativeData, badData, metricsByRole });
  assertRun262NarrativeProofSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_62_narrative_proof_arms.mjs",
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

function writeRun262Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-62-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-62-bad-without-narrative-proof/trace_manifest.json`);
  const result = {
    schema_version: 1,
    run_id: RUN_ID,
    status: "run2_62_narrative_proof_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_repair_run_id: "2.61",
    source_generated_run_id: "2.60",
    database_expansion: false,
    workflow_expansion: true,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_61_result: RUN2_62_INPUTS.run261Result,
      run2_61_narrative_proof_dataset: RUN2_62_INPUTS.run261Narrative,
      run2_61_visual_carrier_selector: RUN2_62_INPUTS.run261Selector,
      run2_61_text_socket_fusion: RUN2_62_INPUTS.run261Fusion,
      run2_61_source_policy: RUN2_62_INPUTS.run261SourcePolicy,
      run2_61_workflow_gates: RUN2_62_INPUTS.run261WorkflowGates,
      run2_60_result: RUN2_62_INPUTS.run260Result,
      run2_60_full_trace: RUN2_62_INPUTS.run260FullTrace,
      commercial_usecase_bank: RUN2_62_INPUTS.commercialUsecaseBank,
      sources: RUN2_62_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_62_narrative_proof_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_62_full_narrative_proof",
      best_internal_arm_verdict:
        "Run 2.61 narrative proof records, visual carrier selectors, text socket fusion contracts, public proof replacements, and workflow gates are consumed before native PPT drawing.",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: RUN2_62_POLICY,
      source_data_status: RUN2_62_FULL_STATUS,
      full_slides_with_run2_61_contracts: fullTrace.slides.filter((slide) =>
        String(slide.run2_61_narrative_proof_id ?? "").startsWith("narrative_proof_2_61_"),
      ).length,
      full_slides_with_socket_bindings: fullTrace.slides.filter((slide) => (slide.run2_62_socket_binding_count ?? 0) >= 5).length,
      full_slides_with_public_proof_replacements: fullTrace.slides.filter((slide) =>
        String(slide.run2_61_public_proof_replacement_id ?? "").startsWith("public_proof_replacement_2_61_"),
      ).length,
      full_slides_with_required_answers_visible: fullTrace.slides.filter((slide) => slide.run2_62_required_answer_visible === "pass_internal").length,
      bad_control_slides_without_run2_61_contracts: badTrace.slides.filter(
        (slide) =>
          slide.run2_61_narrative_proof_id === "" &&
          slide.run2_62_narrative_proof_consumption_status === RUN2_62_BAD_STATUS,
      ).length,
      repair_modules: Object.values(ROLE_RENDERERS),
    },
    control_boundary: {
      bad_run2_60_without_run2_61_narrative_proof_dataset:
        "may see Run 2.60 generated result and trace, but must not use Run 2.61 narrative proof, visual carrier, socket fusion, source policy, or workflow gate artifacts",
      prompt_only: "commercial_case_only_no_run2_61_narrative_proof_dataset",
      run1_5_skill: "prior_baseline_no_run2_61_narrative_proof_dataset",
    },
    visual_quality_boundary:
      "Run 2.62 proves narrative-proof contract consumption; final public-video-grade aesthetics, native motion, and human release approval remain blocked.",
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
      "audit_run2_62_narrative_proof_consumption_then_decide_renderer_or_data_thickening_do_not_advance_to_run3",
  };
  const resultJson = path.join(root, pack, "results", "run2_62_narrative_proof_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_62_narrative_proof_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.62 Narrative Proof Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.62 consumes Run 2.61 before native PPT drawing. The full arm binds the narrative proof dataset, visual carrier selector, text socket fusion, public proof replacement, and narrative workflow gate on every slide.",
      "",
      "This tests the question raised after Run 2.60: whether the thick narrative and proof data actually reaches the generated PPT, rather than only appearing in the viewer.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_62_full_narrative_proof`",
      "- `bad_run2_60_without_run2_61_narrative_proof_dataset`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_62_full_narrative_proof`.",
      "",
      "Quality delta: `run2_61_narrative_proof_dataset_consumed`. All six full-arm slides bind a Run 2.61 narrative proof id, visual carrier selector id, text socket fusion contract id, public proof replacement id, and narrative workflow gate id.",
      "",
      "The negative control `bad_run2_60_without_run2_61_narrative_proof_dataset` can reuse Run 2.60 generated proof, but it fails the Run 2.61 narrative proof layer.",
      "",
      "Public release remains blocked. This proves contract consumption, not final public-video-grade aesthetics.",
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
  const fourArmSheet = buildRun262FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_62_narrative_proof_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_62_narrative_proof_rerun_summary.json"), runSummary);
  writeRun262Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_62_FULL_DATA_INPUTS,
  RUN2_62_INPUTS,
  armSpecs,
  assertRun262ArmInputBoundaries,
  assertRun262NarrativeProofSelfCheck,
  drawRun262ContractCover,
  drawRun262SourceToSocketStage,
  drawRun262BeforeAfterProofRoute,
  drawRun262InspectionProofBoard,
  drawRun262ClimaxResultObject,
  drawRun262ReleaseGateHandoff,
  drawRun262NarrativeProofComposition,
  loadRun262NarrativeProofData,
  main,
};
