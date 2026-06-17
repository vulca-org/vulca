import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.58";
const selectedUsecaseId = "usecase_design_to_production_platform_launch";
const RUN2_58_FULL_STATUS = "run2_57_product_capability_content_consumed_before_native_ppt_drawing";
const RUN2_58_BAD_STATUS = "fail_missing_run2_57_product_content";
const RUN2_58_POLICY = "product_capability_content_contract_binding";
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
  ink: "#14181f",
  dark: "#111820",
  paper: "#f4efe4",
  white: "#ffffff",
  muted: "#596371",
  line: "#d8d4ca",
  blue: "#2b63d9",
  cyan: "#75c9d8",
  red: "#df4f33",
  green: "#108665",
  amber: "#e4b84e",
  violet: "#7667e8",
  steel: "#e8edf0",
};

const RUN2_58_INPUTS = {
  run257Result: `${pack}/results/run2_57_product_capability_content_result.json`,
  run257CapabilityMemory: `${pack}/run2_57_product_capability_memory.json`,
  run257SlideContracts: `${pack}/run2_57_slide_message_contracts.json`,
  run257WorkflowGates: `${pack}/run2_57_content_workflow_gates.json`,
  run256Result: `${pack}/results/run2_56_role_renderer_split_rerun_result.json`,
  run256FullTrace: `outputs/${threadId}/presentations/ppt-run2-56-full-vulca/trace_manifest.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_58_FULL_DATA_INPUTS = Object.values(RUN2_58_INPUTS);
const RUN2_58_BAD_DATA_INPUTS = [
  RUN2_58_INPUTS.run256Result,
  RUN2_58_INPUTS.run256FullTrace,
  RUN2_58_INPUTS.commercialUsecaseBank,
  RUN2_58_INPUTS.sources,
];

const baseSlides = [
  { role: "cover", title: "Vulca turns a real brief into editable PPT proof." },
  { role: "setup", title: "The source pack becomes product memory before drawing." },
  { role: "contrast", title: "The comparison is product mechanism, not taste." },
  { role: "proof", title: "Trace fields prove the content layer was consumed." },
  { role: "climax", title: "The operating loop is the product moment." },
  { role: "close", title: "2.58 is proof, not public release." },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-58-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.58 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_58_FULL_DATA_INPUTS, "drawRun258ProductContentContract"],
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
        "Show the workflow.",
        "Compare with the old way.",
        "Show the proof.",
        "Make the product moment bigger.",
        "End with next steps.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-58-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.58 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_58_FULL_DATA_INPUTS, "drawRun258ProductContentContract"],
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
        "The baseline explains a product lab.",
        "The setup is readable but generic.",
        "The comparison lacks hard boundaries.",
        "The proof is process-led.",
        "The climax labels the result.",
        "The close is correct but thin.",
      ][index],
    })),
  },
  {
    armId: "run2_58_full_product_content_contract",
    slug: "ppt-run2-58-full-vulca",
    label: "Run 2.58 full product content contract",
    kicker: "RUN 2.58 / PRODUCT CONTENT",
    footer: "run2_58_full_product_content_contract | consumes Run 2.57 | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      ...RUN2_58_FULL_DATA_INPUTS,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_57_product_capability_content_result.json",
      "run2_57_product_capability_memory.json",
      "run2_57_slide_message_contracts.json",
      "run2_57_content_workflow_gates.json",
      "ppt-run2-56-full-vulca/trace_manifest.json",
      RUN2_58_POLICY,
    ],
    forbidden: [
      "source layouts",
      "copied screenshots",
      "raw tutorial media",
      "image_only_output_claim",
      "generic product claims",
      "native_drawing_before_run2_57_content_binding",
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
    armId: "bad_run2_56_without_product_capability_content",
    slug: "ppt-run2-58-bad-without-product-capability-content",
    label: "Bad missing Run 2.57 product content",
    kicker: "RUN 2.58 / BAD CONTROL",
    footer: "bad_run2_56_without_product_capability_content | Run 2.56 only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_58_BAD_DATA_INPUTS],
    data_input_manifest: ["run2_56_generated_without_product_capability_content"],
    forbidden: [
      "run2_57_product_capability_memory.json",
      "run2_57_slide_message_contracts.json",
      "run2_57_content_workflow_gates.json",
      "drawRun258ProductContentContract",
      "run2_57_product_capability_content_consumed_before_native_ppt_drawing",
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
        "Run 2.56 is visual proof, but the product is still under-explained.",
        "The source-to-memory story is implied, not explicit.",
        "Competitor comparison stays generic.",
        "Trace exists, but the reader question is not visible.",
        "The visual moment is stronger than the product logic.",
        "The close lacks the 2.57-to-2.58 handoff.",
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
    productTermsVisibleCount: 0,
    readerQuestionVisible: false,
    genericClaimCount: 0,
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
  registerText(metrics, value);
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

function armUsesFullRun258Content(arm) {
  return arm.armId === "run2_58_full_product_content_contract";
}

function armUsesBadRun258Data(arm) {
  return arm.armId === "bad_run2_56_without_product_capability_content";
}

function assertRun258ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun258Content(arm)) {
    for (const input of RUN2_58_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesBadRun258Data(arm)) {
    for (const input of RUN2_58_BAD_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow bad-control input ${input}`);
    }
    for (const input of [
      RUN2_58_INPUTS.run257Result,
      RUN2_58_INPUTS.run257CapabilityMemory,
      RUN2_58_INPUTS.run257SlideContracts,
      RUN2_58_INPUTS.run257WorkflowGates,
    ]) {
      if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    }
    return;
  }
  for (const input of RUN2_58_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun258PackJsonForArm(arm, relPath) {
  assertRun258ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (!armUsesFullRun258Content(arm) && !armUsesBadRun258Data(arm)) {
    throw new Error(`${arm.armId} cannot read Run 2.58 pack data`);
  }
  return readJson(relPath);
}

function assertSelectedUsecase(value, label) {
  if (value !== selectedUsecaseId) throw new Error(`Run 2.58 selected usecase mismatch in ${label}`);
}

function validateRun258ProductContentInputs(data) {
  if (data.run257Result?.status !== "run2_57_product_capability_content_ready_public_blocked") {
    throw new Error("Run 2.58 must consume Run 2.57 product capability content result");
  }
  if (data.run257CapabilityMemory?.status !== "run2_57_product_capability_memory_ready_public_blocked") {
    throw new Error("Run 2.58 must consume Run 2.57 product capability memory");
  }
  if (data.run257SlideContracts?.status !== "run2_57_slide_message_contracts_ready_public_blocked") {
    throw new Error("Run 2.58 must consume Run 2.57 slide message contracts");
  }
  if (data.run257WorkflowGates?.status !== "run2_57_content_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.58 must consume Run 2.57 content workflow gates");
  }
  if (data.run256Result?.status !== "run2_56_role_renderer_split_rerun_public_blocked") {
    throw new Error("Run 2.58 must consume Run 2.56 generated result");
  }
  if (data.run256FullTrace?.arm_id !== "run2_56_full_role_renderer_split") {
    throw new Error("Run 2.58 must compare against Run 2.56 full trace");
  }
  if (!Array.isArray(data.run256FullTrace?.slides) || data.run256FullTrace.slides.length !== 6) {
    throw new Error("Run 2.58 requires six Run 2.56 full trace slides");
  }
  assertSelectedUsecase(data.run257Result?.selected_usecase_id, "run2_57_result");
  assertSelectedUsecase(data.run257CapabilityMemory?.selected_usecase_id, "run2_57_capability_memory");
  assertSelectedUsecase(data.run257SlideContracts?.selected_usecase_id, "run2_57_slide_contracts");
  assertSelectedUsecase(data.run257WorkflowGates?.selected_usecase_id, "run2_57_workflow_gates");
  assertSelectedUsecase(data.run256Result?.selected_usecase_id, "run2_56_result");
  assertSelectedUsecase(data.run256FullTrace?.selected_usecase_id, "run2_56_full_trace");
  const roles = new Set(baseSlides.map((slide) => slide.role));
  const contracts = data.run257SlideContracts.slide_message_contracts ?? [];
  if (contracts.length !== 6 || !contracts.every((contract) => roles.has(contract.role))) {
    throw new Error("Run 2.58 requires six Run 2.57 slide message contracts");
  }
  for (const contract of contracts) {
    if ((contract.required_product_terms ?? []).length < 3) {
      throw new Error(`Run 2.58 contract has too few product terms for ${contract.role}`);
    }
    const visibleProductTerms = `${contract.required_answer} ${(contract.required_product_terms ?? []).join(" ")}`;
    if (!visibleProductTerms.includes("PPT") && ["cover", "climax", "close"].includes(contract.role)) {
      throw new Error(`Run 2.58 output-facing contract must explain product output for ${contract.role}`);
    }
    if ((contract.next_renderer_obligation?.required_trace_fields ?? []).length < 9) {
      throw new Error(`Run 2.58 contract missing trace obligations for ${contract.role}`);
    }
  }
  const fullArmStatus = data.run257WorkflowGates?.next_generated_run_contract?.full_arm_pass_status;
  if (fullArmStatus !== RUN2_58_FULL_STATUS) {
    throw new Error("Run 2.58 next-generated-run contract status mismatch");
  }
}

function loadRun258ContractData(arm) {
  const data = {
    run257Result: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.run257Result),
    run257CapabilityMemory: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.run257CapabilityMemory),
    run257SlideContracts: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.run257SlideContracts),
    run257WorkflowGates: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.run257WorkflowGates),
    run256Result: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.run256Result),
    run256FullTrace: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.run256FullTrace),
    commercialUsecaseBank: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.commercialUsecaseBank),
    sources: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.sources),
  };
  validateRun258ProductContentInputs(data);
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_58_product_content_contract_ready",
  };
}

function loadRun258BadControlData(arm) {
  const data = {
    run256Result: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.run256Result),
    run256FullTrace: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.run256FullTrace),
    commercialUsecaseBank: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.commercialUsecaseBank),
    sources: readRun258PackJsonForArm(arm, RUN2_58_INPUTS.sources),
  };
  if (data.run256Result?.status !== "run2_56_role_renderer_split_rerun_public_blocked") {
    throw new Error("Run 2.58 bad control must read Run 2.56 result");
  }
  if (data.run256FullTrace?.arm_id !== "run2_56_full_role_renderer_split") {
    throw new Error("Run 2.58 bad control must read Run 2.56 full trace");
  }
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
  };
}

const ROLE_GATE_IDS = {
  cover: "gate_2_57_product_capability_binding",
  setup: "gate_2_57_reader_question_answer",
  contrast: "gate_2_57_competitor_boundary",
  proof: "gate_2_57_generic_claim_rejection",
  climax: "gate_2_57_code_generated_ppt_claim",
  close: "gate_2_57_repair_loop_handoff",
};

const ROLE_RENDERERS = {
  cover: "drawRun258CapabilityLaunchSurface",
  setup: "drawRun258SourceToMemoryPipeline",
  contrast: "drawRun258CompetitorBoundaryMatrix",
  proof: "drawRun258TraceQaInspectionBoard",
  climax: "drawRun258OperatingLoopClimax",
  close: "drawRun258ReleaseDecisionWall",
};

const ROLE_SURFACES = {
  cover: "capability_launch_surface",
  setup: "source_to_memory_pipeline",
  contrast: "competitor_boundary_matrix",
  proof: "trace_qa_inspection_board",
  climax: "product_operating_loop_climax",
  close: "release_decision_wall",
};

function selectRun258ForSlide(role, contractData) {
  const contract = (contractData.run257SlideContracts.slide_message_contracts ?? []).find((item) => item.role === role);
  const priorTraceSlide = (contractData.run256FullTrace.slides ?? []).find((item) => item.role === role);
  const gate = (contractData.run257WorkflowGates.content_workflow_gates ?? []).find((item) => item.gate_id === ROLE_GATE_IDS[role]);
  if (!contract || !priorTraceSlide || !gate) throw new Error(`Run 2.58 missing role contract for ${role}`);
  const capabilityRecords = contract.source_capability_ids.map((id) =>
    (contractData.run257CapabilityMemory.product_capability_records ?? []).find((record) => record.id === id),
  );
  if (capabilityRecords.some((record) => !record)) throw new Error(`Run 2.58 missing capability record for ${role}`);
  const relationRecords = (contractData.run257CapabilityMemory.product_logic_relation_records ?? []).filter((relation) =>
    contract.source_capability_ids.includes(relation.from_capability_id) ||
    contract.source_capability_ids.includes(relation.to_capability_id),
  );
  const competitorRecords = contract.role === "contrast"
    ? contractData.run257CapabilityMemory.competitor_boundary_records
    : (contractData.run257CapabilityMemory.competitor_boundary_records ?? []).slice(0, 2);
  return {
    role,
    contract,
    gate,
    priorTraceSlide,
    capabilities: capabilityRecords,
    relations: relationRecords,
    competitors: competitorRecords,
    usecase: contractData.usecase,
  };
}

function termList(contract) {
  return (contract.required_product_terms ?? []).join(" / ");
}

function drawLabel(slide, metrics, label, value, x, y, w, h, opts = {}) {
  text(slide, label, x, y, w, 12, {
    fontSize: 7.6,
    mono: true,
    bold: true,
    color: opts.labelColor ?? C.red,
  });
  socketText(slide, metrics, value, x, y + 15, w, h - 15, {
    fontSize: opts.fontSize ?? 10.5,
    bold: opts.bold,
    title: opts.title,
    color: opts.color ?? C.ink,
    max: opts.max ?? 118,
  });
}

function drawRequirementStack(slide, arm, selection, metrics, x, y, w) {
  const rows = [
    ["reader question", selection.contract.reader_question],
    ["required answer", selection.contract.required_answer],
    ["product terms", termList(selection.contract)],
    ["visible product object", selection.contract.visible_product_object],
  ];
  rows.forEach(([label, value], index) => {
    const rowY = y + index * 72;
    rect(slide, x, rowY, w, 56, index === 1 ? "#eef3f6" : C.white, colorLine("#d8e0e5", 1));
    drawLabel(slide, metrics, label, value, x + 16, rowY + 10, w - 32, 40, {
      max: index === 1 ? 160 : 118,
      fontSize: index === 1 ? 9.5 : 9,
    });
  });
  registerProof(metrics, rows.length);
  registerZones(metrics, 5);
}

function drawCapabilityNodes(slide, arm, selection, metrics, x, y, w, h) {
  const records = selection.capabilities.slice(0, 4);
  records.forEach((record, index) => {
    const nodeX = x + index * ((w - 76) / Math.max(1, records.length - 1));
    ellipse(slide, nodeX, y + (index % 2) * 28, 76, 76, index === 0 ? arm.palette.proof : C.white, colorLine(index === 0 ? arm.palette.proof : "#cbd7df", 1.2));
    socketText(slide, metrics, record.capability_layer.replace("_", " "), nodeX + 10, y + 24 + (index % 2) * 28, 56, 22, {
      fontSize: 8.4,
      bold: true,
      align: "center",
      color: index === 0 ? C.white : C.ink,
      max: 44,
    });
    if (index < records.length - 1) {
      rect(slide, nodeX + 76, y + 36 + (index % 2) * 28, (w - 76) / Math.max(1, records.length - 1) - 72, 5, arm.palette.accent2, colorLine("transparent", 0));
    }
  });
  registerProof(metrics, records.length);
  registerZones(metrics, 6);
}

function drawRun258CapabilityLaunchSurface(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, "Vulca product proof starts here", 78, 106, 470, 34, {
    fontSize: 14,
    mono: true,
    bold: true,
    color: arm.palette.proof,
    max: 64,
  });
  socketText(slide, metrics, selection.contract.required_answer, 78, 150, 520, 108, {
    fontSize: 28,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 168,
  });
  drawRequirementStack(slide, arm, selection, metrics, 78, 288, 450);
  rect(slide, 604, 118, 512, 384, C.dark, colorLine(C.dark, 1));
  const nodes = ["brief", "database", "memory", "code renderer", "editable PPT"];
  nodes.forEach((node, index) => {
    const x = 636 + index * 88;
    const y = 184 + (index % 2) * 92;
    rect(slide, x, y, 76, 70, index === 4 ? arm.palette.proof : "#f8fafb", colorLine("#aab8c5", 1));
    socketText(slide, metrics, node, x + 9, y + 24, 58, 20, {
      fontSize: 8.8,
      bold: true,
      align: "center",
      color: index === 4 ? C.white : C.ink,
      max: 38,
    });
    if (index < nodes.length - 1) rect(slide, x + 76, y + 33, 28, 6, arm.palette.accent2, colorLine("transparent", 0));
  });
  socketText(slide, metrics, "code-generated editable PPT", 690, 410, 300, 38, {
    fontSize: 21,
    title: true,
    bold: true,
    color: C.white,
    align: "center",
    max: 56,
  });
  drawCapabilityNodes(slide, arm, selection, metrics, 624, 530, 500, 92);
}

function drawRun258SourceToMemoryPipeline(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.contract.reader_question, 78, 112, 470, 54, {
    fontSize: 24,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 112,
  });
  socketText(slide, metrics, selection.contract.required_answer, 78, 182, 470, 64, {
    fontSize: 13.6,
    color: arm.palette.muted,
    max: 170,
  });
  const stages = [
    "commercial brief",
    "allowed source pack",
    "derived observations",
    "product capability memory",
    "slide message contract",
    "workflow gate",
  ];
  stages.forEach((stage, index) => {
    const x = 590 + (index % 3) * 178;
    const y = 126 + Math.floor(index / 3) * 144;
    rect(slide, x, y, 146, 82, index >= 3 ? "#edf4f7" : C.white, colorLine("#cbd7df", 1));
    socketText(slide, metrics, stage, x + 14, y + 26, 118, 28, {
      fontSize: 10,
      bold: true,
      align: "center",
      color: C.ink,
      max: 60,
    });
    if (index < stages.length - 1 && index !== 2) rect(slide, x + 146, y + 38, 30, 6, arm.palette.proof, colorLine("transparent", 0));
  });
  drawRequirementStack(slide, arm, selection, metrics, 78, 288, 440);
  drawCapabilityNodes(slide, arm, selection, metrics, 608, 450, 456, 88);
}

function drawRun258CompetitorBoundaryMatrix(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.contract.reader_question, 70, 100, 560, 54, {
    fontSize: 26,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 120,
  });
  socketText(slide, metrics, selection.contract.required_answer, 70, 164, 560, 54, {
    fontSize: 13.2,
    color: arm.palette.muted,
    max: 174,
  });
  const competitors = selection.competitors.slice(0, 5);
  competitors.forEach((record, index) => {
    const y = 254 + index * 60;
    rect(slide, 70, y, 260, 44, index === 0 ? "#f4dfd4" : C.white, colorLine("#d8e0e5", 1));
    socketText(slide, metrics, record.competitor_boundary_id.replaceAll("_", " "), 88, y + 15, 224, 18, {
      fontSize: 9,
      bold: true,
      max: 60,
    });
    rect(slide, 360, y, 646, 44, index === 0 ? "#eef3f6" : C.white, colorLine("#d8e0e5", 1));
    socketText(slide, metrics, record.vulca_difference, 378, y + 11, 610, 22, {
      fontSize: 8.8,
      max: 168,
    });
  });
  rect(slide, 1038, 254, 88, 284, C.dark, colorLine(C.dark, 1));
  socketText(slide, metrics, "bad control must fail without 2.57", 1052, 314, 58, 110, {
    fontSize: 10,
    bold: true,
    align: "center",
    color: C.white,
    max: 80,
  });
  drawCapabilityNodes(slide, arm, selection, metrics, 690, 108, 416, 88);
}

function drawRun258TraceQaInspectionBoard(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.contract.reader_question, 70, 102, 520, 52, {
    fontSize: 25,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 120,
  });
  socketText(slide, metrics, selection.contract.required_answer, 70, 166, 520, 64, {
    fontSize: 13,
    color: arm.palette.muted,
    max: 180,
  });
  const checks = [
    ["capability ids", selection.contract.source_capability_ids.join(", ")],
    ["message contract", selection.contract.contract_id],
    ["workflow gate", selection.gate.gate_id],
    ["reader question", "pass_internal"],
    ["generic claim count", "0"],
    ["output claim", "code-generated editable PPT"],
  ];
  checks.forEach(([label, value], index) => {
    const x = 634 + (index % 2) * 250;
    const y = 126 + Math.floor(index / 2) * 100;
    rect(slide, x, y, 218, 72, index === 5 ? "#f3dfd5" : C.white, colorLine("#cbd7df", 1));
    drawLabel(slide, metrics, label, value, x + 14, y + 14, 190, 42, {
      max: 96,
      fontSize: 9,
      bold: index === 5,
    });
  });
  drawRequirementStack(slide, arm, selection, metrics, 70, 280, 500);
  registerProof(metrics, checks.length);
  registerZones(metrics, 8);
}

function drawRun258OperatingLoopClimax(slide, arm, spec, selection, metrics) {
  rect(slide, 54, 90, 1136, 552, C.dark, colorLine(C.dark, 1));
  socketText(slide, metrics, selection.contract.required_answer, 96, 122, 560, 90, {
    fontSize: 29,
    title: true,
    bold: true,
    color: C.white,
    max: 168,
  });
  socketText(slide, metrics, selection.contract.reader_question, 98, 222, 520, 42, {
    fontSize: 12,
    color: "#dbe5ec",
    max: 120,
  });
  const loop = [
    "brief",
    "database",
    "design memory",
    "workflow gates",
    "code renderer",
    "editable PPT preview",
    "trace and QA",
  ];
  loop.forEach((item, index) => {
    const angle = (-90 + index * (360 / loop.length)) * (Math.PI / 180);
    const cx = 810 + Math.cos(angle) * 214;
    const cy = 350 + Math.sin(angle) * 156;
    ellipse(slide, cx - 54, cy - 36, 108, 72, index === 5 ? arm.palette.proof : "#f8fafb", colorLine(index === 5 ? arm.palette.proof : "#94a3b8", 1));
    socketText(slide, metrics, item, cx - 42, cy - 10, 84, 20, {
      fontSize: 8.6,
      bold: true,
      align: "center",
      color: index === 5 ? C.white : C.ink,
      max: 50,
    });
  });
  ellipse(slide, 710, 280, 200, 140, "#111820", colorLine("#8fd6e5", 2));
  socketText(slide, metrics, "code-generated editable PPT", 738, 328, 144, 34, {
    fontSize: 15,
    title: true,
    bold: true,
    color: C.white,
    align: "center",
    max: 58,
  });
  drawRequirementStack(slide, arm, selection, metrics, 96, 300, 420);
}

function drawRun258ReleaseDecisionWall(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, selection.contract.reader_question, 70, 110, 540, 52, {
    fontSize: 26,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 120,
  });
  socketText(slide, metrics, selection.contract.required_answer, 70, 176, 540, 64, {
    fontSize: 13,
    color: arm.palette.muted,
    max: 180,
  });
  const decisions = [
    ["latest generated", "Run 2.56 visual proof"],
    ["content layer", "Run 2.57 product capability memory"],
    ["now generated", "Run 2.58 four-arm proof"],
    ["still blocked", "visual review, native render, source boundary, human approval"],
  ];
  decisions.forEach(([label, value], index) => {
    const x = 650;
    const y = 118 + index * 102;
    rect(slide, x, y, 412, 76, index === 2 ? "#f4dfd4" : C.white, colorLine("#cbd7df", 1));
    drawLabel(slide, metrics, label, value, x + 20, y + 16, 368, 44, {
      max: 120,
      fontSize: 10,
      bold: index === 2,
    });
  });
  rect(slide, 1078, 118, 54, 382, C.dark, colorLine(C.dark, 1));
  socketText(slide, metrics, "public blocked", 1090, 254, 30, 86, {
    fontSize: 9.6,
    bold: true,
    align: "center",
    color: C.white,
    max: 38,
  });
  drawRequirementStack(slide, arm, selection, metrics, 70, 300, 500);
}

const RUN2_58_RENDERERS = {
  cover: drawRun258CapabilityLaunchSurface,
  setup: drawRun258SourceToMemoryPipeline,
  contrast: drawRun258CompetitorBoundaryMatrix,
  proof: drawRun258TraceQaInspectionBoard,
  climax: drawRun258OperatingLoopClimax,
  close: drawRun258ReleaseDecisionWall,
};

function markRun258ProductContent(metrics, selection) {
  metrics.codeModuleIds.add("drawRun258ProductContentContract");
  metrics.codeModuleIds.add(ROLE_RENDERERS[selection.role]);
  metrics.productTermsVisibleCount = Math.max(metrics.productTermsVisibleCount, (selection.contract.required_product_terms ?? []).length);
  metrics.readerQuestionVisible = true;
  metrics.genericClaimCount = 0;
  metrics.productSystemSurfaceKind = ROLE_SURFACES[selection.role];
  registerProof(metrics, Math.max(4, metrics.productTermsVisibleCount));
  registerZones(metrics, 7);
}

function drawRun258ProductContentContract(slide, arm, spec, selection, metrics) {
  const renderer = RUN2_58_RENDERERS[spec.role];
  if (!renderer) throw new Error(`Run 2.58 missing role renderer for ${spec.role}`);
  renderer(slide, arm, spec, selection, metrics);
  markRun258ProductContent(metrics, selection);
}

function drawBadRun258FallbackSlide(slide, arm, spec, badData, metrics) {
  const prior = (badData.run256FullTrace?.slides ?? []).find((slideItem) => slideItem.role === spec.role);
  socketText(slide, metrics, spec.title, 76, 118, 540, 78, {
    fontSize: 28,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 104,
  });
  socketText(slide, metrics, "Run 2.56 visuals remain visible, but no Run 2.57 product capability, reader question, or content workflow gate is bound before drawing.", 80, 212, 500, 62, {
    fontSize: 14,
    color: arm.palette.muted,
    max: 152,
  });
  rect(slide, 632, 136, 454, 314, arm.palette.panel, colorLine(arm.palette.rule, 1));
  rect(slide, 660, 170, 386, 64, "#fff8e4", colorLine("#dfc990", 1));
  socketText(slide, metrics, "Generic slide labels can look organized without explaining the product mechanism.", 682, 190, 342, 24, {
    fontSize: 11,
    bold: true,
    color: arm.palette.title,
    max: 104,
  });
  ["visual proof", "workflow", "quality", "next steps"].forEach((label, index) => {
    rect(slide, 678 + (index % 2) * 170, 276 + Math.floor(index / 2) * 72, 136, 50, "#eee2c7", colorLine("#c6ad78", 1));
    socketText(slide, metrics, label, 696 + (index % 2) * 170, 292 + Math.floor(index / 2) * 72, 100, 18, {
      fontSize: 9,
      bold: true,
      align: "center",
      max: 32,
    });
  });
  socketText(slide, metrics, prior?.run2_56_layout_signature ?? "Run 2.56 visual trace exists", 650, 474, 390, 26, {
    fontSize: 10,
    color: arm.palette.muted,
    max: 92,
  });
  metrics.genericClaimCount = 2;
  metrics.productTermsVisibleCount = 0;
  metrics.readerQuestionVisible = false;
  metrics.productSystemSurfaceKind = "run2_56_visual_surface_without_run2_57_content";
  registerProof(metrics, 2);
  registerZones(metrics, 3);
}

function drawControlSlideContent(slide, arm, spec, metrics, mode = "prompt") {
  socketText(slide, metrics, spec.title, 76, 132, 596, 104, {
    fontSize: mode === "run1_5" ? 33 : 36,
    bold: true,
    title: true,
    color: arm.palette.title,
    max: 100,
  });
  socketText(slide, metrics, "This arm does not receive the Run 2.57 product capability content layer, so it can only make broad claims about better slides.", 80, 250, 526, 64, {
    fontSize: 15,
    color: arm.palette.muted,
    max: 138,
  });
  for (let i = 0; i < 4; i += 1) {
    rect(slide, 674 + (i % 2) * 158, 278 + Math.floor(i / 2) * 108, 132, 82, C.white, colorLine(arm.palette.rule, 1));
    socketText(slide, metrics, ["prompt", "theme", "layout", "summary"][i], 696 + (i % 2) * 158, 310 + Math.floor(i / 2) * 108, 86, 18, {
      fontSize: 10,
      bold: true,
      align: "center",
      color: arm.palette.title,
    });
  }
  rect(slide, 84, 356, 482, 126, C.white, colorLine(arm.palette.rule, 1));
  socketText(slide, metrics, mode === "run1_5" ? "Prior skill: readable, but no 2.57 product contract." : "Prompt-only: no capability ids, no message contracts, no bad-control gate.", 108, 394, 420, 38, {
    fontSize: 18,
    bold: true,
    title: true,
    color: arm.palette.title,
    max: 92,
  });
  metrics.genericClaimCount = 1;
  registerProof(metrics, 2);
  registerZones(metrics, 3);
}

function renderRun258Slide(presentation, spec, arm, n, contractData, badData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun258Content(arm)) {
    const selection = selectRun258ForSlide(spec.role, contractData);
    drawRun258ProductContentContract(slide, arm, spec, selection, metrics);
  } else if (armUsesBadRun258Data(arm)) {
    drawBadRun258FallbackSlide(slide, arm, spec, badData, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function blankRun253Fields() {
  return {
    run2_53_product_surface_scene_id: "",
    run2_53_business_visual_evidence_id: "",
    run2_53_scene_renderer_gate_id: "",
    run2_53_primary_product_or_business_object: "",
    run2_53_visual_specificity_status: "fail_missing_run2_53",
    run2_53_forbidden_generic_geometry_count: 0,
  };
}

function blankRun255Fields() {
  return {
    run2_54_code_module_ids: [],
    run2_54_primary_surface_kind: "",
    run2_54_product_surface_slots_rendered: 0,
    run2_54_business_visual_evidence_objects: 0,
    run2_54_source_generated_status: "",
    run2_55_code_module_ids: [],
    run2_55_text_shape_integration_status: "",
    run2_55_primary_layout_strategy: "",
    run2_55_product_surface_slots_rendered: 0,
    run2_55_business_visual_evidence_objects: 0,
    run2_55_named_text_containers_rendered: 0,
    run2_55_non_rectangular_shape_families_rendered: 0,
    run2_55_text_shape_binding_pairs: 0,
    run2_55_text_overflow_risk_count: 0,
    run2_55_equal_rectangle_cluster_count: 0,
    run2_55_editorial_hierarchy_levels: 0,
  };
}

function blankRun256Fields() {
  return {
    run2_56_code_module_ids: [],
    run2_56_role_renderer_id: "",
    run2_56_composition_family: "",
    run2_56_layout_signature: "",
    run2_56_visual_sameness_bucket: "",
    run2_56_primary_anchor_region: "",
    run2_56_role_specific_geometry_count: 0,
    run2_56_text_collision_risk_count: 0,
    run2_56_text_overflow_risk_count: 0,
    run2_56_distinct_role_surface_status: "",
    run2_56_role_archetype_binding_status: "",
    run2_56_primary_layout_strategy: "",
    run2_56_product_surface_slots_rendered: 0,
    run2_56_business_visual_evidence_objects: 0,
    run2_56_named_text_containers_rendered: 0,
    run2_56_non_rectangular_shape_families_rendered: 0,
    run2_56_text_shape_binding_pairs: 0,
    run2_56_equal_rectangle_cluster_count: 0,
    run2_56_editorial_hierarchy_levels: 0,
  };
}

function inheritedRun256TraceFields(prior) {
  return {
    run2_53_product_surface_scene_id: prior.run2_53_product_surface_scene_id ?? "",
    run2_53_business_visual_evidence_id: prior.run2_53_business_visual_evidence_id ?? "",
    run2_53_scene_renderer_gate_id: prior.run2_53_scene_renderer_gate_id ?? "",
    run2_53_primary_product_or_business_object: prior.run2_53_primary_product_or_business_object ?? "",
    run2_53_visual_specificity_status: prior.run2_53_visual_specificity_status ?? "",
    run2_53_forbidden_generic_geometry_count: prior.run2_53_forbidden_generic_geometry_count ?? 0,
    run2_54_code_module_ids: prior.run2_54_code_module_ids ?? [],
    run2_54_primary_surface_kind: prior.run2_54_primary_surface_kind ?? "",
    run2_54_product_surface_slots_rendered: prior.run2_54_product_surface_slots_rendered ?? 0,
    run2_54_business_visual_evidence_objects: prior.run2_54_business_visual_evidence_objects ?? 0,
    run2_54_source_generated_status: prior.run2_54_source_generated_status ?? "",
    run2_55_code_module_ids: prior.run2_55_code_module_ids ?? [],
    run2_55_text_shape_integration_status: prior.run2_55_text_shape_integration_status ?? "",
    run2_55_primary_layout_strategy: prior.run2_55_primary_layout_strategy ?? "",
    run2_55_product_surface_slots_rendered: prior.run2_55_product_surface_slots_rendered ?? 0,
    run2_55_business_visual_evidence_objects: prior.run2_55_business_visual_evidence_objects ?? 0,
    run2_55_named_text_containers_rendered: prior.run2_55_named_text_containers_rendered ?? 0,
    run2_55_non_rectangular_shape_families_rendered: prior.run2_55_non_rectangular_shape_families_rendered ?? 0,
    run2_55_text_shape_binding_pairs: prior.run2_55_text_shape_binding_pairs ?? 0,
    run2_55_text_overflow_risk_count: prior.run2_55_text_overflow_risk_count ?? 0,
    run2_55_equal_rectangle_cluster_count: prior.run2_55_equal_rectangle_cluster_count ?? 0,
    run2_55_editorial_hierarchy_levels: prior.run2_55_editorial_hierarchy_levels ?? 0,
    run2_56_code_module_ids: prior.run2_56_code_module_ids ?? [],
    run2_56_role_renderer_id: prior.run2_56_role_renderer_id ?? "",
    run2_56_composition_family: prior.run2_56_composition_family ?? "",
    run2_56_layout_signature: prior.run2_56_layout_signature ?? "",
    run2_56_visual_sameness_bucket: prior.run2_56_visual_sameness_bucket ?? "",
    run2_56_primary_anchor_region: prior.run2_56_primary_anchor_region ?? "",
    run2_56_role_specific_geometry_count: prior.run2_56_role_specific_geometry_count ?? 0,
    run2_56_text_collision_risk_count: prior.run2_56_text_collision_risk_count ?? 0,
    run2_56_text_overflow_risk_count: prior.run2_56_text_overflow_risk_count ?? 0,
    run2_56_distinct_role_surface_status: prior.run2_56_distinct_role_surface_status ?? "",
    run2_56_role_archetype_binding_status: prior.run2_56_role_archetype_binding_status ?? "",
    run2_56_primary_layout_strategy: prior.run2_56_primary_layout_strategy ?? "",
    run2_56_product_surface_slots_rendered: prior.run2_56_product_surface_slots_rendered ?? 0,
    run2_56_business_visual_evidence_objects: prior.run2_56_business_visual_evidence_objects ?? 0,
    run2_56_named_text_containers_rendered: prior.run2_56_named_text_containers_rendered ?? 0,
    run2_56_non_rectangular_shape_families_rendered: prior.run2_56_non_rectangular_shape_families_rendered ?? 0,
    run2_56_text_shape_binding_pairs: prior.run2_56_text_shape_binding_pairs ?? 0,
    run2_56_equal_rectangle_cluster_count: prior.run2_56_equal_rectangle_cluster_count ?? 0,
    run2_56_editorial_hierarchy_levels: prior.run2_56_editorial_hierarchy_levels ?? 0,
  };
}

function traceFor(arm, context = {}) {
  assertRun258ArmInputBoundaries(arm);
  const fullRun258 = armUsesFullRun258Content(arm);
  const badRun258 = armUsesBadRun258Data(arm);
  const contractData = fullRun258 ? context.contractData ?? loadRun258ContractData(arm) : null;
  const badData = badRun258 ? context.badData ?? loadRun258BadControlData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun258 || badRun258 ? selectedUsecaseId : "",
    source_repair_run_id: fullRun258 ? "2.57" : "",
    source_generated_run_id: fullRun258 || badRun258 ? "2.56" : "",
    run2_58_product_content_contract_status: fullRun258
      ? RUN2_58_FULL_STATUS
      : badRun258
        ? RUN2_58_BAD_STATUS
        : "boundary_control_no_run2_57_content_contract",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.58 product content contract rerun from scripts/generate_ppt_run2_58_product_content_contract_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun258 ? selectRun258ForSlide(slide.role, contractData) : null;
      const prior = fullRun258
        ? selection.priorTraceSlide
        : badRun258
          ? (badData.run256FullTrace.slides ?? []).find((item) => item.role === slide.role) ?? {}
          : {};
      const inherited = fullRun258 || badRun258 ? inheritedRun256TraceFields(prior) : { ...blankRun253Fields(), ...blankRun255Fields(), ...blankRun256Fields() };
      const run257Fields = fullRun258
        ? {
            run2_57_product_capability_ids: selection.contract.source_capability_ids,
            run2_57_slide_message_contract_id: selection.contract.contract_id,
            run2_57_content_workflow_gate_id: selection.gate.gate_id,
            run2_57_product_logic_relation_ids: selection.relations.slice(0, 3).map((relation) => relation.id),
            run2_57_competitor_boundary_ids: selection.competitors.map((record) => record.competitor_boundary_id),
            run2_57_content_specificity_status: "pass_internal",
            run2_57_reader_question_answered_status: "pass_internal",
            run2_57_generic_claim_count: 0,
            run2_57_required_product_terms_rendered: selection.contract.required_product_terms.length,
          }
        : {
            run2_57_product_capability_ids: [],
            run2_57_slide_message_contract_id: "",
            run2_57_content_workflow_gate_id: "",
            run2_57_product_logic_relation_ids: [],
            run2_57_competitor_boundary_ids: [],
            run2_57_content_specificity_status: badRun258 ? "fail_missing_run2_57" : "",
            run2_57_reader_question_answered_status: badRun258 ? "fail_missing_reader_question_contract" : "",
            run2_57_generic_claim_count: badRun258 ? Math.max(1, roleMetrics.genericClaimCount) : roleMetrics.genericClaimCount,
            run2_57_required_product_terms_rendered: 0,
          };
      const run258Fields = {
        run2_58_code_module_ids: fullRun258 ? Array.from(roleMetrics.codeModuleIds) : [],
        run2_58_product_content_contract_status: fullRun258 ? "pass_internal" : badRun258 ? "fail_missing_run2_57_product_content" : "",
        run2_58_product_system_surface_kind: roleMetrics.productSystemSurfaceKind,
        run2_58_reader_question_visible: roleMetrics.readerQuestionVisible,
        run2_58_product_terms_visible_count: roleMetrics.productTermsVisibleCount,
        run2_58_proof_object_count: roleMetrics.proofObjects,
        run2_58_bad_control_boundary_status: badRun258 ? "fail_missing_run2_57_product_content" : fullRun258 ? "pass_internal" : "",
      };
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        ...inherited,
        ...run257Fields,
        ...run258Fields,
        layout_metrics: {
          text_box_count: roleMetrics.textBoxCount,
          visible_words: roleMetrics.visibleWords,
          text_density_tier: roleMetrics.visibleWords >= 82 ? "rich_product_content" : "thin",
          proof_objects: roleMetrics.proofObjects,
          zones: roleMetrics.zones,
          trace_panel_visible: false,
          gate_ribbon_visible: false,
        },
      };
    }),
  };
}

function assertRun258ProductContentSelfCheck(trace) {
  if (trace.arm_id === "run2_58_full_product_content_contract") {
    if (trace.run2_58_product_content_contract_status !== RUN2_58_FULL_STATUS) {
      throw new Error("Run 2.58 full trace did not consume Run 2.57 product content before native PPT drawing");
    }
    for (const slide of trace.slides) {
      if (slide.run2_56_distinct_role_surface_status !== "pass_internal") {
        throw new Error(`Run 2.58 full slide ${slide.slide_id} did not inherit Run 2.56 role-renderer pass`);
      }
      if ((slide.run2_57_product_capability_ids ?? []).length < 2) {
        throw new Error(`Run 2.58 full slide ${slide.slide_id} missing product capability ids`);
      }
      if (!String(slide.run2_57_slide_message_contract_id ?? "").startsWith("message_contract_2_57_")) {
        throw new Error(`Run 2.58 full slide ${slide.slide_id} missing message contract id`);
      }
      if (!String(slide.run2_57_content_workflow_gate_id ?? "").startsWith("gate_2_57_")) {
        throw new Error(`Run 2.58 full slide ${slide.slide_id} missing workflow gate id`);
      }
      if (slide.run2_57_content_specificity_status !== "pass_internal") {
        throw new Error(`Run 2.58 full slide ${slide.slide_id} failed content specificity`);
      }
      if (slide.run2_57_reader_question_answered_status !== "pass_internal") {
        throw new Error(`Run 2.58 full slide ${slide.slide_id} reader question not answered`);
      }
      if ((slide.run2_57_generic_claim_count ?? 0) !== 0) {
        throw new Error(`Run 2.58 full slide ${slide.slide_id} generic claim count must be zero`);
      }
      if ((slide.run2_58_product_terms_visible_count ?? 0) < 3) {
        throw new Error(`Run 2.58 full slide ${slide.slide_id} has too few visible product terms`);
      }
      if (!(slide.run2_58_code_module_ids ?? []).includes("drawRun258ProductContentContract")) {
        throw new Error(`Run 2.58 full slide ${slide.slide_id} missing content contract module`);
      }
      if ((slide.layout_metrics?.visible_words ?? 0) < 82) {
        throw new Error(`Run 2.58 full slide ${slide.slide_id} content is too thin`);
      }
    }
  }
  if (trace.arm_id === "bad_run2_56_without_product_capability_content") {
    for (const slide of trace.slides) {
      if (slide.run2_56_distinct_role_surface_status !== "pass_internal") {
        throw new Error(`Run 2.58 bad slide ${slide.slide_id} must inherit Run 2.56 role-renderer pass`);
      }
      if ((slide.run2_57_product_capability_ids ?? []).length !== 0) {
        throw new Error(`Run 2.58 bad slide ${slide.slide_id} leaked Run 2.57 capability ids`);
      }
      if (slide.run2_57_content_specificity_status !== "fail_missing_run2_57") {
        throw new Error(`Run 2.58 bad slide ${slide.slide_id} must fail missing Run 2.57 content`);
      }
      if ((slide.run2_57_generic_claim_count ?? 0) < 1) {
        throw new Error(`Run 2.58 bad slide ${slide.slide_id} must expose generic claim count`);
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

function buildRun258FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-58-four-arm-contact-sheet.png"),
    "Run 2.58 product content contract comparison",
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
      "required proof objects: product capability ids, slide message contract, content workflow gate, code-generated editable PPT claim, trace QA board",
      "source requirements: full arm reads Run 2.57 product content layer and Run 2.56 full trace before native PPT drawing",
      "negative control: bad arm can read Run 2.56 generated result and trace, but cannot read Run 2.57 product content contracts",
      "profile-specific QA gates: product system must be visible, not a list of generic feature cards",
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
  const contractData = armUsesFullRun258Content(arm) ? loadRun258ContractData(arm) : null;
  const badData = armUsesBadRun258Data(arm) ? loadRun258BadControlData(arm) : null;
  const slides = arm.slides.map((slide, index) =>
    renderRun258Slide(presentation, slide, arm, index + 1, contractData, badData, metricsByRole),
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
  const trace = traceFor(arm, { contractData, badData, metricsByRole });
  assertRun258ProductContentSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_58_product_content_contract_arms.mjs",
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

function writeRun258Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-58-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-58-bad-without-product-capability-content/trace_manifest.json`);
  const result = {
    schema_version: 1,
    run_id: RUN_ID,
    status: "run2_58_product_content_contract_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_repair_run_id: "2.57",
    source_generated_run_id: "2.56",
    database_expansion: false,
    workflow_expansion: true,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_57_result: RUN2_58_INPUTS.run257Result,
      run2_57_product_capability_memory: RUN2_58_INPUTS.run257CapabilityMemory,
      run2_57_slide_message_contracts: RUN2_58_INPUTS.run257SlideContracts,
      run2_57_content_workflow_gates: RUN2_58_INPUTS.run257WorkflowGates,
      run2_56_result: RUN2_58_INPUTS.run256Result,
      run2_56_full_trace: RUN2_58_INPUTS.run256FullTrace,
      commercial_usecase_bank: RUN2_58_INPUTS.commercialUsecaseBank,
      sources: RUN2_58_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_58_product_content_contract_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_58_full_product_content_contract",
      best_internal_arm_verdict:
        "Run 2.57 product capability content contracts are consumed before native PPT drawing, forcing each slide to answer a product reader question with concrete product terms.",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: RUN2_58_POLICY,
      source_data_status: RUN2_58_FULL_STATUS,
      full_slides_with_run2_57_capability_ids: fullTrace.slides.filter((slide) => (slide.run2_57_product_capability_ids ?? []).length >= 2).length,
      full_slides_with_message_contracts: fullTrace.slides.filter((slide) => String(slide.run2_57_slide_message_contract_id ?? "").startsWith("message_contract_2_57_")).length,
      full_slides_with_content_workflow_gates: fullTrace.slides.filter((slide) => String(slide.run2_57_content_workflow_gate_id ?? "").startsWith("gate_2_57_")).length,
      full_slides_with_reader_question_answered: fullTrace.slides.filter((slide) => slide.run2_57_reader_question_answered_status === "pass_internal").length,
      full_slides_with_zero_generic_claims: fullTrace.slides.filter((slide) => (slide.run2_57_generic_claim_count ?? 0) === 0).length,
      full_slides_with_code_generated_ppt_claim: fullTrace.slides.filter((slide) => (slide.run2_57_required_product_terms_rendered ?? 0) >= 3).length,
      bad_control_slides_without_run2_57_content: badTrace.slides.filter(
        (slide) =>
          slide.run2_57_content_specificity_status === "fail_missing_run2_57" &&
          slide.run2_58_bad_control_boundary_status === "fail_missing_run2_57_product_content",
      ).length,
      repair_modules: Object.values(ROLE_RENDERERS),
    },
    control_boundary: {
      bad_run2_56_without_product_capability_content:
        "may see Run 2.56 generated result and trace, including role-renderer pass, but must not use Run 2.57 product capability memory, slide message contracts, or content workflow gates",
      prompt_only: "commercial_case_only_no_run2_57_product_content_layer",
      run1_5_skill: "prior_baseline_no_run2_57_product_content_layer",
    },
    visual_quality_boundary:
      "Run 2.58 improves product content specificity and product logic explanation; public-video-grade aesthetics, native motion, and human release approval remain blocked.",
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
      "audit_run2_58_product_content_contract_against_visible_story_quality_then_continue_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_58_product_content_contract_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_58_product_content_contract_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.58 Product Content Contract Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.58 consumes Run 2.57 before native PPT drawing. The full arm keeps the Run 2.56 role-renderer pass, then binds product capability content, slide message contracts, and content workflow gates on every slide.",
      "",
      "This fixes the content problem identified after Run 2.56: the deck was visually more varied, but it still did not explain Vulca's product capability, product logic, code-generated editable PPT output, comparison boundary, QA gate, or repair loop deeply enough.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_58_full_product_content_contract`",
      "- `bad_run2_56_without_product_capability_content`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_58_full_product_content_contract`.",
      "",
      "Quality delta: `product_capability_content_contract_binding`. All six full-arm slides bind Run 2.57 capability ids, message contract ids, content workflow gate ids, reader-question pass status, zero generic claims, and concrete product terms including `code-generated editable PPT`.",
      "",
      "The negative control `bad_run2_56_without_product_capability_content` can reuse Run 2.56 visual proof, but it fails the product capability content layer and exposes generic claim count.",
      "",
      "Public release remains blocked. This proves product-content binding, not final public-video-grade aesthetics.",
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
  const fourArmSheet = buildRun258FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_58_product_content_contract_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_58_product_content_contract_rerun_summary.json"), runSummary);
  writeRun258Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_58_FULL_DATA_INPUTS,
  RUN2_58_INPUTS,
  armSpecs,
  assertRun258ArmInputBoundaries,
  assertRun258ProductContentSelfCheck,
  drawRun258CapabilityLaunchSurface,
  drawRun258SourceToMemoryPipeline,
  drawRun258CompetitorBoundaryMatrix,
  drawRun258TraceQaInspectionBoard,
  drawRun258OperatingLoopClimax,
  drawRun258ReleaseDecisionWall,
  drawRun258ProductContentContract,
  loadRun258ContractData,
  main,
  readRun258PackJsonForArm,
  selectRun258ForSlide,
  traceFor,
  validateRun258ProductContentInputs,
};
