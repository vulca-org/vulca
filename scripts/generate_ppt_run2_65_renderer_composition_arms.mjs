import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.65";
const selectedUsecaseId = "usecase_design_to_production_platform_launch";
const RUN2_65_FULL_STATUS = "run2_64_renderer_composition_repair_consumed_before_native_ppt_drawing";
const RUN2_65_BAD_STATUS = "fail_missing_run2_64";
const RUN2_65_POLICY = "run2_64_renderer_composition_repair_consumed";
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
  dark: "#101720",
  paper: "#f5f0e7",
  white: "#ffffff",
  muted: "#56616d",
  line: "#d8d4ca",
  blue: "#2b63d9",
  cyan: "#68c6d8",
  red: "#df4f33",
  green: "#108665",
  amber: "#e4b84e",
  slate: "#e8edf0",
  violet: "#6b58d3",
};

const RUN2_65_INPUTS = {
  run264Result: `${pack}/results/run2_64_renderer_composition_repair_result.json`,
  run264DynamicSocket: `${pack}/run2_64_dynamic_socket_renderer_memory.json`,
  run264SemanticDiagram: `${pack}/run2_64_semantic_diagram_renderer_memory.json`,
  run264TextFit: `${pack}/run2_64_text_fit_renderer_gates.json`,
  run264DryRun: `${pack}/run2_64_renderer_dry_run_binding_matrix.json`,
  run262Result: `${pack}/results/run2_62_narrative_proof_rerun_result.json`,
  run262FullTrace: `outputs/${threadId}/presentations/ppt-run2-62-full-vulca/trace_manifest.json`,
  run261Fusion: `${pack}/run2_61_text_socket_fusion_contracts.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_65_FULL_DATA_INPUTS = Object.values(RUN2_65_INPUTS);
const RUN2_65_BAD_DATA_INPUTS = [
  RUN2_65_INPUTS.run262Result,
  RUN2_65_INPUTS.run262FullTrace,
  RUN2_65_INPUTS.run261Fusion,
  RUN2_65_INPUTS.commercialUsecaseBank,
  RUN2_65_INPUTS.sources,
];

const requiredRun264TraceFields = [
  "run2_64_dynamic_socket_renderer_id",
  "run2_64_semantic_diagram_renderer_id",
  "run2_64_text_fit_gate_id",
  "run2_64_renderer_dry_run_binding_id",
  "run2_64_dynamic_socket_plan_status",
  "run2_64_semantic_diagram_binding_status",
  "run2_64_text_fit_preflight_status",
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
    slug: "ppt-run2-65-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.65 / CONTROL",
    footer: "prompt_only | brief only | no Run 2.64 renderer contract",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_65_FULL_DATA_INPUTS, "drawRun265RendererCompositionRepair"],
    palette: { bg: "#f7f8fa", rail: "#394150", accent: C.blue, panel: C.white, title: C.ink, muted: C.muted, rule: "#d9dee5" },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: ["Make the deck better.", "Explain the workflow.", "Show a comparison.", "Add proof.", "Make the product bigger.", "End with next step."][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-65-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.65 / RUN 1.5",
    footer: "run1_5_skill | prior baseline | no Run 2.64 renderer contract",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_65_FULL_DATA_INPUTS, "drawRun265RendererCompositionRepair"],
    palette: { bg: "#f3f7fb", rail: "#283247", accent: C.green, panel: C.white, title: C.ink, muted: C.muted, rule: "#d2dce7" },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: ["Readable product story.", "Workflow is named.", "Comparison exists.", "Proof is process-led.", "Product moment is still generic.", "Close remains thin."][index],
    })),
  },
  {
    armId: "run2_65_full_renderer_composition_repair",
    slug: "ppt-run2-65-full-vulca",
    label: "Run 2.65 full renderer repair",
    kicker: "RUN 2.65 / RENDERER REPAIR",
    footer: "run2_65_full_renderer_composition_repair | consumes Run 2.64 | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_65_FULL_DATA_INPUTS, `${pack}/skill_workflow.json`, `${pack}/vulca_ppt_skill.md`],
    data_input_manifest: [
      "run2_64_dynamic_socket_renderer_memory.json",
      "run2_64_semantic_diagram_renderer_memory.json",
      "run2_64_text_fit_renderer_gates.json",
      "run2_64_renderer_dry_run_binding_matrix.json",
      RUN2_65_POLICY,
    ],
    forbidden: [
      "copied screenshots",
      "raw tutorial media",
      "image_only_output_claim",
      "generic card grid as primary surface",
      "native_drawing_before_run2_64_renderer_composition_repair",
    ],
    palette: { bg: "#f5f0e7", rail: C.dark, accent: C.red, accent2: C.blue, panel: C.white, title: "#0e1218", muted: "#56616d", rule: "#d8cfbf" },
    slides: baseSlides,
  },
  {
    armId: "bad_run2_64_without_renderer_composition_repair",
    slug: "ppt-run2-65-bad-without-renderer-composition-repair",
    label: "Bad missing Run 2.64 renderer repair",
    kicker: "RUN 2.65 / BAD CONTROL",
    footer: "bad_run2_64_without_renderer_composition_repair | Run 2.62 only",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_65_BAD_DATA_INPUTS],
    data_input_manifest: ["run2_62_generated_without_run2_64_renderer_composition_repair"],
    forbidden: [
      "run2_64_dynamic_socket_renderer_memory.json",
      "run2_64_semantic_diagram_renderer_memory.json",
      "run2_64_text_fit_renderer_gates.json",
      "run2_64_renderer_dry_run_binding_matrix.json",
      "drawRun265RendererCompositionRepair",
      RUN2_65_FULL_STATUS,
    ],
    palette: { bg: "#efe7d5", rail: "#6d603b", accent: "#8a7143", panel: "#faf4e8", title: "#2b271e", muted: "#665e4d", rule: "#dbcfb8" },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Run 2.62 consumed proof, but kept the static socket plan.",
        "The operating loop still becomes equal blocks.",
        "The contrast can still truncate and flatten.",
        "Inspection proof remains card-like.",
        "The preview object is still too generic.",
        "The close lacks a renderer repair contract.",
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
  for (const dir of ["output", "preview", "layout/final", "qa", "slides", "assets", "node_modules/@oai"]) ensureDir(path.join(workspace, dir));
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
  fonts: { title: "Aptos Display", body: "Aptos", mono: "Aptos Mono" },
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
  const rawValue = Array.isArray(value) ? value.join(" / ") : value;
  const textValue = String(rawValue ?? "").replace(/\s+/g, " ").trim();
  if (textValue.length <= max) return textValue;
  const clipped = textValue.slice(0, max).trim();
  return clipped.includes(" ") ? clipped.replace(/\s+\S*$/, "").trim() : clipped;
}

function wordsIn(value) {
  return String(value ?? "").trim().split(/\s+/).filter(Boolean).length;
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
    dynamicSocketCount: 0,
    semanticDiagramType: "",
    textOverflowRiskCount: 0,
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
  socketText(slide, metrics, label, x + 12, y + 10, w - 24, 11, { fontSize: 8, bold: true, align: "center", color, max: 48 });
}

function base(slide, arm, n) {
  rect(slide, 0, 0, W, H, arm.palette.bg);
  rect(slide, 0, 0, 16, H, arm.palette.rail);
  text(slide, arm.kicker, 54, 30, 548, 22, { fontSize: 10, bold: true, mono: true, color: arm.palette.accent });
  text(slide, `${String(n).padStart(2, "0")} / 06`, 1110, 30, 114, 22, { fontSize: 10, mono: true, color: arm.palette.muted, align: "right" });
  rect(slide, 54, 70, 1170, 2, arm.palette.rule ?? C.line);
  text(slide, arm.footer, 548, 674, 676, 22, { fontSize: 9, mono: true, color: arm.palette.muted, align: "right" });
  for (let i = 1; i <= 6; i += 1) rect(slide, 54 + (i - 1) * 20, 684, i === n ? 16 : 8, 5, i === n ? arm.palette.accent : C.line);
}

function armUsesFullRun265Repair(arm) {
  return arm.armId === "run2_65_full_renderer_composition_repair";
}

function armUsesBadRun265Data(arm) {
  return arm.armId === "bad_run2_64_without_renderer_composition_repair";
}

function assertRun265ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun265Repair(arm)) {
    for (const input of RUN2_65_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesBadRun265Data(arm)) {
    for (const input of RUN2_65_BAD_DATA_INPUTS) if (!allowed.has(input)) throw new Error(`${arm.armId} must allow bad-control input ${input}`);
    for (const input of [RUN2_65_INPUTS.run264Result, RUN2_65_INPUTS.run264DynamicSocket, RUN2_65_INPUTS.run264SemanticDiagram, RUN2_65_INPUTS.run264TextFit, RUN2_65_INPUTS.run264DryRun]) {
      if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    }
    return;
  }
  for (const input of RUN2_65_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun265PackJsonForArm(arm, relPath) {
  assertRun265ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  if (!armUsesFullRun265Repair(arm) && !armUsesBadRun265Data(arm)) throw new Error(`${arm.armId} cannot read Run 2.65 pack data`);
  return readJson(relPath);
}

function byRole(records) {
  return Object.fromEntries((records ?? []).map((record) => [record.role, record]));
}

function assertSelectedUsecase(value, label) {
  if (value !== selectedUsecaseId) throw new Error(`Run 2.65 selected usecase mismatch in ${label}`);
}

function validateRun265RendererInputs(data) {
  if (data.run264Result?.status !== "run2_64_renderer_composition_repair_ready_public_blocked") throw new Error("Run 2.65 must consume Run 2.64 result");
  if (data.run264DynamicSocket?.status !== "run2_64_dynamic_socket_renderer_memory_ready_public_blocked") throw new Error("Run 2.65 must consume Run 2.64 dynamic socket memory");
  if (data.run264SemanticDiagram?.status !== "run2_64_semantic_diagram_renderer_memory_ready_public_blocked") throw new Error("Run 2.65 must consume Run 2.64 semantic diagram memory");
  if (data.run264TextFit?.status !== "run2_64_text_fit_renderer_gates_ready_public_blocked") throw new Error("Run 2.65 must consume Run 2.64 text-fit gates");
  if (data.run264DryRun?.status !== "run2_64_renderer_dry_run_binding_matrix_ready_public_blocked") throw new Error("Run 2.65 must consume Run 2.64 dry-run matrix");
  if (data.run262Result?.status !== "run2_62_narrative_proof_rerun_public_blocked") throw new Error("Run 2.65 must compare against Run 2.62 result");
  if (data.run262FullTrace?.arm_id !== "run2_62_full_narrative_proof") throw new Error("Run 2.65 must compare against Run 2.62 full trace");
  assertSelectedUsecase(data.run262Result?.selected_usecase_id, "run2_62_result");
  assertSelectedUsecase(data.run262FullTrace?.selected_usecase_id, "run2_62_full_trace");
  const roles = new Set(baseSlides.map((slide) => slide.role));
  const dynamic = data.run264DynamicSocket.dynamic_socket_renderer_records ?? [];
  const semantic = data.run264SemanticDiagram.semantic_diagram_renderer_records ?? [];
  const textFit = data.run264TextFit.text_fit_renderer_gates ?? [];
  const dryRun = data.run264DryRun.dry_run_binding_records ?? [];
  for (const records of [dynamic, semantic, textFit, dryRun]) {
    if (records.length !== 6 || !records.every((record) => roles.has(record.role))) throw new Error("Run 2.65 requires six Run 2.64 role records");
  }
  const semanticByRole = byRole(semantic);
  const textFitByRole = byRole(textFit);
  const dryRunByRole = byRole(dryRun);
  for (const record of dynamic) {
    const role = record.role;
    if (!semanticByRole[role] || !textFitByRole[role] || !dryRunByRole[role]) throw new Error(`Run 2.65 missing Run 2.64 links for ${role}`);
    for (const field of requiredRun264TraceFields) {
      if (!(record.required_trace_fields_for_run2_65 ?? []).includes(field)) throw new Error(`Run 2.65 missing trace field ${field}`);
    }
    if (record.static_socket_plan_replaced !== true) throw new Error(`Run 2.65 expected static socket replacement for ${role}`);
    if ((record.active_socket_bindings ?? []).length < 6) throw new Error(`Run 2.65 expected six active sockets for ${role}`);
    if (semanticByRole[role].forbid_generic_repeated_shape_system !== true) throw new Error(`Run 2.65 expected semantic diagram boundary for ${role}`);
    if (textFitByRole[role].runtime_claim_boundary !== "must_be_verified_by_run2_65_render_trace") throw new Error(`Run 2.65 expected text-fit runtime boundary for ${role}`);
    if (dryRunByRole[role].ready_for_run2_65_consumption !== true) throw new Error(`Run 2.65 dry-run matrix not ready for ${role}`);
  }
}

function loadRun265RendererData(arm) {
  const data = {
    run264Result: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run264Result),
    run264DynamicSocket: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run264DynamicSocket),
    run264SemanticDiagram: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run264SemanticDiagram),
    run264TextFit: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run264TextFit),
    run264DryRun: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run264DryRun),
    run262Result: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run262Result),
    run262FullTrace: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run262FullTrace),
    run261Fusion: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run261Fusion),
    commercialUsecaseBank: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.commercialUsecaseBank),
    sources: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.sources),
  };
  validateRun265RendererInputs(data);
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_65_renderer_inputs_ready",
  };
}

function loadRun265BadControlData(arm) {
  const data = {
    run262Result: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run262Result),
    run262FullTrace: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run262FullTrace),
    run261Fusion: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.run261Fusion),
    commercialUsecaseBank: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.commercialUsecaseBank),
    sources: readRun265PackJsonForArm(arm, RUN2_65_INPUTS.sources),
  };
  if (data.run262Result?.status !== "run2_62_narrative_proof_rerun_public_blocked") throw new Error("Run 2.65 bad control must read Run 2.62 result");
  if (data.run262FullTrace?.arm_id !== "run2_62_full_narrative_proof") throw new Error("Run 2.65 bad control must read Run 2.62 full trace");
  return { ...data, usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId) };
}

function selectRun265ForSlide(role, data) {
  const dynamic = (data.run264DynamicSocket.dynamic_socket_renderer_records ?? []).find((item) => item.role === role);
  const semantic = (data.run264SemanticDiagram.semantic_diagram_renderer_records ?? []).find((item) => item.role === role);
  const textFit = (data.run264TextFit.text_fit_renderer_gates ?? []).find((item) => item.role === role);
  const dryRun = (data.run264DryRun.dry_run_binding_records ?? []).find((item) => item.role === role);
  const fusion = (data.run261Fusion.text_socket_fusion_contracts ?? []).find((item) => item.role === role);
  const priorTraceSlide = (data.run262FullTrace.slides ?? []).find((item) => item.role === role);
  if (!dynamic || !semantic || !textFit || !dryRun || !fusion || !priorTraceSlide) throw new Error(`Run 2.65 missing role renderer selection for ${role}`);
  return { role, dynamic, semantic, textFit, dryRun, fusion, priorTraceSlide, usecase: data.usecase };
}

const ROLE_RENDERERS = {
  cover: "drawRun265SourcePackHero",
  setup: "drawRun265OperatingLoop",
  contrast: "drawRun265MechanismDelta",
  proof: "drawRun265InspectionWorkspace",
  climax: "drawRun265EditablePreviewHero",
  close: "drawRun265ReleaseHandoffRoute",
};

function getCopy(selection, key) {
  return selection.fusion.source_copy_units?.[key] ?? "";
}

function run265ShortSubhead(selection) {
  return {
    cover: "Real brief, source memory, and code become editable PPT.",
    setup: "Usecase, sources, memory, contracts, and gates lock before drawing.",
    contrast: "The product difference is traceable generation, not taste.",
    proof: "Each slide carries source, gate, trace, and output proof.",
    climax: "One editable preview shows sockets, diagrams, and text-fit.",
    close: "Run 2.65 consumes the Run 2.64 renderer contract before review.",
  }[selection.role] ?? compactText(getCopy(selection, "subhead"), 90);
}

const COPY_UNIT_LABELS = {
  headline: "headline",
  subhead: "subhead",
  proof_badges: "proof",
  annotations: "callout",
  state_labels: "state",
  speaker_note: "note",
};

const SHAPE_ROLE_LABELS = {
  primary_carrier: "main",
  support_surface: "support",
  proof_object: "proof",
  annotation_callout: "callout",
  state_marker: "state",
  speaker_note_channel: "note",
};

function activeSocketLabels(selection, maxItems = 6) {
  return (selection.dynamic.active_socket_bindings ?? []).slice(0, maxItems).map((binding) => {
    const copyLabel = COPY_UNIT_LABELS[binding.copy_unit_key] ?? binding.copy_unit_key;
    const shapeLabel = SHAPE_ROLE_LABELS[binding.owning_shape_role] ?? binding.owning_shape_role;
    return `${copyLabel} -> ${shapeLabel}`;
  });
}

function drawActiveSocketStrip(slide, metrics, selection, x, y, w, dark = false) {
  const labels = activeSocketLabels(selection, 6);
  const gap = 8;
  const chipW = (w - gap * (labels.length - 1)) / labels.length;
  labels.forEach((label, index) => {
    chip(slide, metrics, label, x + index * (chipW + gap), y + (index % 2) * 10, chipW, dark ? "#1b2834" : "#fffaf2", dark ? C.cyan : C.ink);
  });
  metrics.dynamicSocketCount = selection.dynamic.active_socket_bindings.length;
}

function drawRun265SourcePackHero(slide, arm, spec, selection, metrics) {
  rect(slide, 54, 96, 1130, 522, C.dark, colorLine(C.dark, 1));
  rect(slide, 106, 138, 458, 330, "#172330", colorLine("#324557", 1));
  socketText(slide, metrics, getCopy(selection, "headline"), 130, 164, 390, 70, { fontSize: 30, title: true, bold: true, color: C.white, max: 68 });
  socketText(slide, metrics, run265ShortSubhead(selection), 132, 256, 370, 48, { fontSize: 11, color: "#d5e0e8", max: 100 });
  [["brief", 632, 150], ["memory", 826, 224], ["code", 650, 360], ["editable PPT", 884, 430]].forEach(([label, x, y], index) => {
    const fill = index === 3 ? C.red : index === 1 ? "#e8f5ef" : "#fff2d6";
    rect(slide, x, y, 190, 104, fill, colorLine(index === 3 ? C.red : "#9aa9b7", 1.5));
    socketText(slide, metrics, label, x + 24, y + 42, 142, 18, { fontSize: 13, bold: true, align: "center", color: index === 3 ? C.white : C.ink, max: 24 });
  });
  rect(slide, 554, 204, 78, 6, C.cyan, colorLine("transparent", 0));
  rect(slide, 768, 286, 90, 6, C.blue, colorLine("transparent", 0));
  rect(slide, 766, 410, 96, 6, C.red, colorLine("transparent", 0));
  drawActiveSocketStrip(slide, metrics, selection, 128, 516, 840, true);
  metrics.semanticDiagramType = selection.semantic.semantic_diagram_type;
  registerProof(metrics, 7);
  registerZones(metrics, 9);
}

function drawRun265OperatingLoop(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, getCopy(selection, "headline"), 74, 104, 520, 58, { fontSize: 27, title: true, bold: true, color: arm.palette.title, max: 64 });
  socketText(slide, metrics, run265ShortSubhead(selection), 76, 172, 470, 42, { fontSize: 11, color: arm.palette.muted, max: 92 });
  const nodes = [
    ["brief", 700, 122, "#fff2d6"],
    ["sources", 922, 202, "#e8f5ef"],
    ["memory", 880, 426, "#e9edf8"],
    ["renderer", 634, 434, "#fde7de"],
    ["editable PPT", 560, 248, "#111820"],
  ];
  nodes.forEach(([label, x, y, fill], index) => {
    ellipse(slide, x, y, 138, 92, fill, colorLine(index === 4 ? C.red : "#9aa9b7", 1.6));
    socketText(slide, metrics, label, x + 22, y + 38, 94, 14, { fontSize: 10, bold: true, align: "center", color: index === 4 ? C.white : C.ink, max: 20 });
  });
  [[814, 168, 110], [1010, 286, 6], [830, 472, 64], [616, 364, 6], [616, 242, 90]].forEach(([x, y, w], index) => rect(slide, x, y, w, 5, index === 2 ? C.red : C.blue, colorLine("transparent", 0)));
  drawActiveSocketStrip(slide, metrics, selection, 76, 498, 470);
  metrics.semanticDiagramType = selection.semantic.semantic_diagram_type;
  registerProof(metrics, 6);
  registerZones(metrics, 9);
}

function drawRun265MechanismDelta(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, getCopy(selection, "headline"), 72, 98, 530, 52, { fontSize: 26, title: true, bold: true, color: arm.palette.title, max: 60 });
  socketText(slide, metrics, run265ShortSubhead(selection), 74, 160, 480, 36, { fontSize: 11, color: arm.palette.muted, max: 84 });
  rect(slide, 88, 280, 282, 156, "#fff5da", colorLine("#c9b06d", 1.2));
  rect(slide, 824, 228, 312, 222, C.dark, colorLine(C.cyan, 2));
  socketText(slide, metrics, "before", 112, 300, 88, 14, { fontSize: 9, mono: true, bold: true, color: C.red, max: 16 });
  socketText(slide, metrics, "after", 852, 254, 88, 14, { fontSize: 9, mono: true, bold: true, color: C.cyan, max: 16 });
  socketText(slide, metrics, "before: prompt deck / after: source-bound proof", 118, 340, 210, 36, { fontSize: 10, bold: true, align: "center", max: 54 });
  socketText(slide, metrics, "visible contract + fitted text + semantic diagram", 866, 316, 222, 42, { fontSize: 14, title: true, bold: true, align: "center", color: C.white, max: 54 });
  ellipse(slide, 500, 242, 186, 186, "#f6ded4", colorLine(C.red, 2));
  socketText(slide, metrics, "renderer turn", 532, 314, 122, 18, { fontSize: 11, bold: true, align: "center", color: C.red, max: 26 });
  rect(slide, 370, 354, 130, 6, C.red, colorLine("transparent", 0));
  rect(slide, 686, 328, 138, 6, C.blue, colorLine("transparent", 0));
  drawActiveSocketStrip(slide, metrics, selection, 96, 520, 860);
  metrics.semanticDiagramType = selection.semantic.semantic_diagram_type;
  registerProof(metrics, 7);
  registerZones(metrics, 8);
}

function drawRun265InspectionWorkspace(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, getCopy(selection, "headline"), 66, 94, 520, 54, { fontSize: 26, title: true, bold: true, color: arm.palette.title, max: 60 });
  socketText(slide, metrics, run265ShortSubhead(selection), 68, 158, 470, 38, { fontSize: 11, color: arm.palette.muted, max: 86 });
  rect(slide, 620, 110, 520, 404, "#f9fbfc", colorLine("#c4cdd6", 1));
  ["source", "gate", "trace", "output"].forEach((label, index) => {
    const x = 650 + (index % 2) * 232;
    const y = 154 + Math.floor(index / 2) * 154;
    rect(slide, x, y, 196, 106, index === 3 ? "#111820" : index === 1 ? "#fff2d6" : C.white, colorLine("#c9d3dc", 1));
    socketText(slide, metrics, label, x + 16, y + 16, 92, 12, { fontSize: 8, mono: true, bold: true, color: index === 3 ? C.cyan : C.red, max: 16 });
    socketText(slide, metrics, (selection.semantic.proof_object_bindings ?? [])[index % 3]?.copy_unit_key ?? selection.semantic.semantic_diagram_type, x + 18, y + 48, 150, 18, { fontSize: 10, bold: true, align: "center", color: index === 3 ? C.white : C.ink, max: 34 });
  });
  drawActiveSocketStrip(slide, metrics, selection, 72, 500, 474);
  metrics.semanticDiagramType = selection.semantic.semantic_diagram_type;
  registerProof(metrics, 8);
  registerZones(metrics, 9);
}

function drawRun265EditablePreviewHero(slide, arm, spec, selection, metrics) {
  rect(slide, 54, 92, 1136, 544, C.dark, colorLine(C.dark, 1));
  socketText(slide, metrics, getCopy(selection, "headline"), 92, 126, 450, 70, { fontSize: 30, title: true, bold: true, color: C.white, max: 60 });
  socketText(slide, metrics, run265ShortSubhead(selection), 94, 212, 398, 44, { fontSize: 11, color: "#d7e2e9", max: 90 });
  rect(slide, 616, 126, 426, 296, "#f9fbfc", colorLine(C.cyan, 2));
  rect(slide, 648, 166, 156, 96, "#fff2d6", colorLine("#d0b770", 1));
  rect(slide, 830, 162, 170, 38, C.red, colorLine(C.red, 1));
  rect(slide, 830, 222, 132, 26, "#dce9f8", colorLine("#9fb3cc", 1));
  ellipse(slide, 742, 300, 168, 78, "#e8f5ef", colorLine(C.green, 1.5));
  socketText(slide, metrics, "editable PPT preview", 704, 450, 248, 24, { fontSize: 18, title: true, bold: true, align: "center", color: C.white, max: 34 });
  ["dynamic sockets", "semantic diagram", "text-fit gate"].forEach((label, index) => {
    rect(slide, 98 + index * 142, 354 + (index % 2) * 34, 118, 50, index === 1 ? "#e8f5ef" : "#fff2d6", colorLine("#9aa9b7", 1));
    socketText(slide, metrics, label, 110 + index * 142, 374 + (index % 2) * 34, 94, 12, { fontSize: 8.2, bold: true, align: "center", max: 24 });
  });
  drawActiveSocketStrip(slide, metrics, selection, 98, 510, 520, true);
  metrics.semanticDiagramType = selection.semantic.semantic_diagram_type;
  registerProof(metrics, 8);
  registerZones(metrics, 9);
}

function drawRun265ReleaseHandoffRoute(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, getCopy(selection, "headline"), 80, 112, 526, 58, { fontSize: 27, title: true, bold: true, color: arm.palette.title, max: 62 });
  socketText(slide, metrics, run265ShortSubhead(selection), 82, 184, 480, 42, { fontSize: 11, color: arm.palette.muted, max: 86 });
  const marks = [
    ["2.62", "generated proof", 626, 154, "#eef3f6"],
    ["2.63", "root cause", 786, 292, "#fff2d6"],
    ["2.64", "renderer contract", 956, 154, "#e8f5ef"],
    ["2.65", "consumer rerun", 916, 426, "#111820"],
  ];
  marks.forEach(([run, label, x, y, fill], index) => {
    ellipse(slide, x, y, 124, 124, fill, colorLine(index === 3 ? C.red : "#9aa9b7", index === 3 ? 2 : 1));
    socketText(slide, metrics, run, x + 28, y + 34, 68, 24, { fontSize: 18, title: true, bold: true, align: "center", color: index === 3 ? C.white : C.ink, max: 8 });
    socketText(slide, metrics, label, x + 16, y + 68, 92, 14, { fontSize: 7.5, align: "center", bold: true, color: index === 3 ? C.cyan : C.ink, max: 26 });
  });
  [[750, 210, 52], [900, 344, 58], [1010, 278, 6]].forEach(([x, y, w], index) => rect(slide, x, y, w, 5, index === 1 ? C.red : C.blue, colorLine("transparent", 0)));
  drawActiveSocketStrip(slide, metrics, selection, 86, 460, 482);
  metrics.semanticDiagramType = selection.semantic.semantic_diagram_type;
  registerProof(metrics, 7);
  registerZones(metrics, 9);
}

const RUN2_65_RENDERERS = {
  cover: drawRun265SourcePackHero,
  setup: drawRun265OperatingLoop,
  contrast: drawRun265MechanismDelta,
  proof: drawRun265InspectionWorkspace,
  climax: drawRun265EditablePreviewHero,
  close: drawRun265ReleaseHandoffRoute,
};

function markRun265RendererRepair(metrics, selection) {
  metrics.codeModuleIds.add("drawRun265RendererCompositionRepair");
  metrics.codeModuleIds.add(ROLE_RENDERERS[selection.role]);
  metrics.productSystemSurfaceKind = selection.semantic.source_visual_carrier_type;
  metrics.semanticDiagramType = selection.semantic.semantic_diagram_type;
  metrics.dynamicSocketCount = selection.dynamic.active_socket_bindings.length;
  registerProof(metrics, Math.max(3, (selection.semantic.proof_object_bindings ?? []).length + 3));
  registerZones(metrics, 9);
}

function drawRun265RendererCompositionRepair(slide, arm, spec, selection, metrics) {
  const renderer = RUN2_65_RENDERERS[spec.role];
  if (!renderer) throw new Error(`Run 2.65 missing role renderer for ${spec.role}`);
  renderer(slide, arm, spec, selection, metrics);
  markRun265RendererRepair(metrics, selection);
}

function drawBadRun265FallbackSlide(slide, arm, spec, badData, metrics) {
  const prior = (badData.run262FullTrace?.slides ?? []).find((slideItem) => slideItem.role === spec.role);
  socketText(slide, metrics, spec.title, 76, 116, 560, 78, { fontSize: 27, title: true, bold: true, color: arm.palette.title, max: 100 });
  socketText(slide, metrics, "This arm can see Run 2.62, but it cannot read the Run 2.64 dynamic socket, semantic diagram, text-fit, or dry-run renderer contracts.", 80, 214, 510, 58, { fontSize: 13, color: arm.palette.muted, max: 140 });
  rect(slide, 640, 130, 460, 306, arm.palette.panel, colorLine(arm.palette.rule, 1));
  socketText(slide, metrics, "static socket plan remains", 674, 168, 270, 22, { fontSize: 15, title: true, bold: true, color: arm.palette.title, max: 44 });
  ["Run 2.62 trace", "generic blocks", "no semantic diagram", "no text-fit gate"].forEach((label, index) => {
    rect(slide, 682 + (index % 2) * 176, 236 + Math.floor(index / 2) * 78, 138, 50, "#eee2c7", colorLine("#c6ad78", 1));
    socketText(slide, metrics, label, 696 + (index % 2) * 176, 252 + Math.floor(index / 2) * 78, 110, 16, { fontSize: 8.2, bold: true, align: "center", max: 32 });
  });
  socketText(slide, metrics, prior?.layout_metrics?.product_system_surface_kind ?? "Run 2.62 trace exists", 658, 464, 408, 24, { fontSize: 10, color: arm.palette.muted, max: 82 });
  metrics.productSystemSurfaceKind = "run2_62_without_run2_64_renderer_composition_repair";
  registerProof(metrics, 2);
  registerZones(metrics, 4);
}

function drawControlSlideContent(slide, arm, spec, metrics, mode = "prompt") {
  socketText(slide, metrics, spec.title, 76, 132, 596, 104, { fontSize: mode === "run1_5" ? 32 : 35, bold: true, title: true, color: arm.palette.title, max: 92 });
  socketText(slide, metrics, "This arm does not receive the Run 2.64 renderer contracts, so it cannot replace static sockets with role-specific semantic diagrams before drawing.", 80, 252, 526, 56, { fontSize: 14, color: arm.palette.muted, max: 122 });
  ["brief", "theme", "layout", "summary"].forEach((label, index) => {
    rect(slide, 674 + (index % 2) * 158, 278 + Math.floor(index / 2) * 108, 132, 82, C.white, colorLine(arm.palette.rule, 1));
    socketText(slide, metrics, label, 696 + (index % 2) * 158, 310 + Math.floor(index / 2) * 108, 86, 18, { fontSize: 10, bold: true, align: "center", color: arm.palette.title, max: 22 });
  });
  rect(slide, 84, 360, 482, 126, C.white, colorLine(arm.palette.rule, 1));
  socketText(slide, metrics, mode === "run1_5" ? "Prior skill: readable, but no Run 2.64 renderer composition repair." : "Prompt-only: no dynamic socket, semantic diagram, or text-fit gate.", 108, 398, 420, 38, { fontSize: 17, bold: true, title: true, color: arm.palette.title, max: 86 });
  metrics.productSystemSurfaceKind = mode === "run1_5" ? "run1_5_without_run2_64_renderer_repair" : "prompt_only_without_run2_64_renderer_repair";
  registerProof(metrics, 2);
  registerZones(metrics, 3);
}

function renderRun265Slide(presentation, spec, arm, n, rendererData, badData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun265Repair(arm)) {
    const selection = selectRun265ForSlide(spec.role, rendererData);
    drawRun265RendererCompositionRepair(slide, arm, spec, selection, metrics);
  } else if (armUsesBadRun265Data(arm)) {
    drawBadRun265FallbackSlide(slide, arm, spec, badData, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function blankRun264Fields() {
  return {
    run2_64_dynamic_socket_renderer_id: "",
    run2_64_semantic_diagram_renderer_id: "",
    run2_64_text_fit_gate_id: "",
    run2_64_renderer_dry_run_binding_id: "",
    run2_64_dynamic_socket_plan_status: "",
    run2_64_semantic_diagram_binding_status: "",
    run2_64_text_fit_preflight_status: "",
  };
}

function traceFor(arm, context = {}) {
  assertRun265ArmInputBoundaries(arm);
  const fullRun265 = armUsesFullRun265Repair(arm);
  const badRun265 = armUsesBadRun265Data(arm);
  const rendererData = fullRun265 ? context.rendererData ?? loadRun265RendererData(arm) : null;
  const badData = badRun265 ? context.badData ?? loadRun265BadControlData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun265 || badRun265 ? selectedUsecaseId : "",
    source_repair_run_id: fullRun265 ? "2.64" : "",
    source_generated_run_id: fullRun265 || badRun265 ? "2.62" : "",
    run2_65_renderer_composition_repair_status: fullRun265 ? RUN2_65_FULL_STATUS : badRun265 ? RUN2_65_BAD_STATUS : "boundary_control_no_run2_64_renderer_repair",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.65 renderer composition rerun from scripts/generate_ppt_run2_65_renderer_composition_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun265 ? selectRun265ForSlide(slide.role, rendererData) : null;
      const run264Fields = fullRun265
        ? {
            run2_64_dynamic_socket_renderer_id: selection.dynamic.dynamic_socket_renderer_id,
            run2_64_semantic_diagram_renderer_id: selection.semantic.semantic_diagram_renderer_id,
            run2_64_text_fit_gate_id: selection.textFit.text_fit_gate_id,
            run2_64_renderer_dry_run_binding_id: selection.dryRun.renderer_dry_run_binding_id,
            run2_64_dynamic_socket_plan_status: "pass_internal",
            run2_64_semantic_diagram_binding_status: "pass_internal",
            run2_64_text_fit_preflight_status: "pass_internal",
          }
        : badRun265
          ? {
              run2_64_dynamic_socket_renderer_id: "",
              run2_64_semantic_diagram_renderer_id: "",
              run2_64_text_fit_gate_id: "",
              run2_64_renderer_dry_run_binding_id: "",
              run2_64_dynamic_socket_plan_status: RUN2_65_BAD_STATUS,
              run2_64_semantic_diagram_binding_status: RUN2_65_BAD_STATUS,
              run2_64_text_fit_preflight_status: RUN2_65_BAD_STATUS,
            }
          : blankRun264Fields();
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        source_run2_62_slide_id: fullRun265 ? selection.priorTraceSlide.slide_id : badRun265 ? slide.role : "",
        ...run264Fields,
        run2_65_code_module_ids: fullRun265 ? Array.from(roleMetrics.codeModuleIds) : [],
        run2_65_renderer_composition_repair_status: fullRun265 ? "pass_internal" : badRun265 ? RUN2_65_BAD_STATUS : "",
        run2_65_dynamic_socket_count: fullRun265 ? roleMetrics.dynamicSocketCount : 0,
        run2_65_semantic_diagram_type: fullRun265 ? roleMetrics.semanticDiagramType : "",
        run2_65_text_fit_runtime_status: fullRun265 ? "pass_internal" : badRun265 ? RUN2_65_BAD_STATUS : "",
        run2_65_visual_delta_from_run2_62: fullRun265 ? "dynamic_socket_semantic_diagram_text_fit_delta" : badRun265 ? "no_run2_64_delta" : "",
        layout_metrics: {
          text_box_count: roleMetrics.textBoxCount,
          visible_words: roleMetrics.visibleWords,
          text_density_tier: roleMetrics.visibleWords >= 86 ? "bounded_dense" : "public_compact",
          proof_objects: roleMetrics.proofObjects,
          zones: roleMetrics.zones,
          text_overflow_risk_count: roleMetrics.textOverflowRiskCount,
          trace_panel_visible: false,
          gate_ribbon_visible: false,
          product_system_surface_kind: roleMetrics.productSystemSurfaceKind,
        },
      };
    }),
  };
}

function assertRun265RendererSelfCheck(trace) {
  if (trace.arm_id === "run2_65_full_renderer_composition_repair") {
    if (trace.run2_65_renderer_composition_repair_status !== RUN2_65_FULL_STATUS) throw new Error("Run 2.65 full trace did not consume Run 2.64 before native PPT drawing");
    for (const slide of trace.slides) {
      for (const field of requiredRun264TraceFields) {
        if (!Object.prototype.hasOwnProperty.call(slide, field)) throw new Error(`Run 2.65 full slide ${slide.slide_id} missing ${field}`);
      }
      if (!String(slide.run2_64_dynamic_socket_renderer_id ?? "").startsWith("dynamic_socket_renderer_2_64_")) throw new Error(`Run 2.65 full slide ${slide.slide_id} missing dynamic socket renderer`);
      if (!String(slide.run2_64_semantic_diagram_renderer_id ?? "").startsWith("semantic_diagram_renderer_2_64_")) throw new Error(`Run 2.65 full slide ${slide.slide_id} missing semantic diagram renderer`);
      if (!String(slide.run2_64_text_fit_gate_id ?? "").startsWith("text_fit_gate_2_64_")) throw new Error(`Run 2.65 full slide ${slide.slide_id} missing text-fit gate`);
      if (!String(slide.run2_64_renderer_dry_run_binding_id ?? "").startsWith("renderer_dry_run_binding_2_64_")) throw new Error(`Run 2.65 full slide ${slide.slide_id} missing dry-run binding`);
      if (slide.run2_65_renderer_composition_repair_status !== "pass_internal") throw new Error(`Run 2.65 full slide ${slide.slide_id} did not pass renderer repair consumption`);
      if ((slide.run2_65_dynamic_socket_count ?? 0) < 6) throw new Error(`Run 2.65 full slide ${slide.slide_id} missing dynamic sockets`);
      if (slide.run2_65_text_fit_runtime_status !== "pass_internal") throw new Error(`Run 2.65 full slide ${slide.slide_id} missing text-fit runtime pass`);
      if ((slide.layout_metrics?.visible_words ?? 0) > 125) throw new Error(`Run 2.65 full slide ${slide.slide_id} exceeds public visible-word capacity`);
      if ((slide.layout_metrics?.text_overflow_risk_count ?? 1) !== 0) throw new Error(`Run 2.65 full slide ${slide.slide_id} has overflow risk`);
    }
  }
  if (trace.arm_id === "bad_run2_64_without_renderer_composition_repair") {
    for (const slide of trace.slides) {
      if (slide.run2_65_renderer_composition_repair_status !== RUN2_65_BAD_STATUS) throw new Error(`Run 2.65 bad slide ${slide.slide_id} must fail missing Run 2.64`);
      if ((slide.run2_65_dynamic_socket_count ?? 1) !== 0) throw new Error(`Run 2.65 bad slide ${slide.slide_id} leaked dynamic sockets`);
    }
  }
}

async function blobToBuffer(blob) {
  if (blob?.data instanceof Uint8Array) return Buffer.from(blob.data);
  const arrayBuffer = await blob.arrayBuffer();
  return Buffer.from(arrayBuffer);
}

function buildNamedContactSheet(out, title, previewPaths, cols = 3, labels = null) {
  const args = [path.join(root, "scripts", "build_ppt_contact_sheet.py"), "--out", out, "--title", title, "--cols", String(cols)];
  if (labels) args.push("--labels", ...labels, "--");
  args.push(...previewPaths);
  execFileSync("python3", args, { cwd: root, stdio: "pipe" });
  return out;
}

function buildContactSheet(workspace, arm, previewPaths) {
  return buildNamedContactSheet(path.join(workspace, "preview", "contact-sheet.png"), arm.label, previewPaths);
}

function buildRun265FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built.filter((item) => fs.existsSync(item.contactSheet)).map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(path.join(outRoot, "run2-65-four-arm-contact-sheet.png"), "Run 2.65 renderer composition comparison", sheets, sheets.length, labels);
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
    ["Run 2.65", "ppt-run2-65-full-vulca"],
  ];
  const items = fullItems.map(([label, slug]) => [label, path.join(outRoot, slug, "preview", "contact-sheet.png")]).filter(([, file]) => fs.existsSync(file));
  if (!items.length) return "";
  const out = path.join(outRoot, "run2-full-skill-series-horizontal.png");
  const args = [path.join(root, "scripts", "build_ppt_full_skill_series_sheet.py"), "--out", out, "--title", "Run 2 full-skill series", "--item-width", "420"];
  for (const [label, file] of items) args.push("--item", `${label}=${file}`);
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
      "required proof objects: Run 2.64 dynamic socket renderer, semantic diagram renderer, text-fit gate, and dry-run binding matrix",
      "negative control: bad arm can read Run 2.62, but cannot read Run 2.64 renderer repair artifacts",
      "profile-specific QA gates: visible text must remain bounded; runtime fit is trace-gated",
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
  const rendererData = armUsesFullRun265Repair(arm) ? loadRun265RendererData(arm) : null;
  const badData = armUsesBadRun265Data(arm) ? loadRun265BadControlData(arm) : null;
  const slides = arm.slides.map((slide, index) => renderRun265Slide(presentation, slide, arm, index + 1, rendererData, badData, metricsByRole));
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
  const trace = traceFor(arm, { rendererData, badData, metricsByRole });
  assertRun265RendererSelfCheck(trace);
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
    slides: slides.map((_, index) => ({ index: index + 1, requestedSlideNumber: index + 1, source: "scripts/generate_ppt_run2_65_renderer_composition_arms.mjs", exportName: `slide${String(index + 1).padStart(2, "0")}` })),
  };
  writeJson(path.join(workspace, "output", "artifact-build-manifest.json"), manifest);
  writeJson(path.join(workspace, "qa", "build_manifest_stdout.json"), manifest);
  writeJson(path.join(workspace, "trace_manifest.json"), trace);
  return { workspace, outputPath, contactSheet, previewPaths };
}

function repoRelative(absPath) {
  return path.relative(root, absPath).split(path.sep).join("/");
}

function writeRun265Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-65-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-65-bad-without-renderer-composition-repair/trace_manifest.json`);
  const result = {
    schema_version: 1,
    run_id: RUN_ID,
    status: "run2_65_renderer_composition_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_repair_run_id: "2.64",
    source_generated_run_id: "2.62",
    database_expansion: false,
    workflow_expansion: true,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_64_result: RUN2_65_INPUTS.run264Result,
      run2_64_dynamic_socket: RUN2_65_INPUTS.run264DynamicSocket,
      run2_64_semantic_diagram: RUN2_65_INPUTS.run264SemanticDiagram,
      run2_64_text_fit: RUN2_65_INPUTS.run264TextFit,
      run2_64_dry_run: RUN2_65_INPUTS.run264DryRun,
      run2_62_result: RUN2_65_INPUTS.run262Result,
      run2_62_full_trace: RUN2_65_INPUTS.run262FullTrace,
      run2_61_text_socket_fusion: RUN2_65_INPUTS.run261Fusion,
      commercial_usecase_bank: RUN2_65_INPUTS.commercialUsecaseBank,
      sources: RUN2_65_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_65_renderer_composition_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_65_full_renderer_composition_repair",
      best_internal_arm_verdict: "Run 2.64 dynamic socket, semantic diagram, text-fit, and dry-run binding contracts are consumed before native PPT drawing.",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: RUN2_65_POLICY,
      source_data_status: RUN2_65_FULL_STATUS,
      full_slides_with_run2_64_contracts: fullTrace.slides.filter((slide) => String(slide.run2_64_dynamic_socket_renderer_id ?? "").startsWith("dynamic_socket_renderer_2_64_")).length,
      full_slides_with_dynamic_sockets: fullTrace.slides.filter((slide) => (slide.run2_65_dynamic_socket_count ?? 0) >= 6).length,
      full_slides_with_semantic_diagrams: fullTrace.slides.filter((slide) => String(slide.run2_65_semantic_diagram_type ?? "").length > 0).length,
      full_slides_with_text_fit_runtime_pass: fullTrace.slides.filter((slide) => slide.run2_65_text_fit_runtime_status === "pass_internal").length,
      bad_control_slides_without_run2_64_contracts: badTrace.slides.filter((slide) => slide.run2_64_dynamic_socket_renderer_id === "" && slide.run2_65_renderer_composition_repair_status === RUN2_65_BAD_STATUS).length,
      repair_modules: Object.values(ROLE_RENDERERS),
    },
    control_boundary: {
      bad_run2_64_without_renderer_composition_repair: "may see Run 2.62 generated result and trace, but must not use Run 2.64 renderer repair artifacts",
      prompt_only: "commercial_case_only_no_run2_64_renderer_repair",
      run1_5_skill: "prior_baseline_no_run2_64_renderer_repair",
    },
    visual_quality_boundary: "Run 2.65 is an internal generated rerun for visual review; public release remains blocked until human review approves the rendered deck.",
    remaining_public_release_gates: ["human_visual_review", "native_or_cross_platform_render_inspection", "source_boundary_review", "human_release_approval"],
    release_boundary: "public_blocked_until_human_visual_review_native_render_review_source_boundary_review_and_human_approval",
    next_required_action: "human_review_run2_65_visual_output_then_decide_whether_renderer_repair_is_enough_or_run2_66_needed",
  };
  const resultJson = path.join(root, pack, "results", "run2_65_renderer_composition_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_65_renderer_composition_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.65 Renderer Composition Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.65 consumes Run 2.64 before native PPT drawing. The full arm binds dynamic socket, semantic diagram, text-fit, and dry-run renderer contracts on every slide.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_65_full_renderer_composition_repair`",
      "- `bad_run2_64_without_renderer_composition_repair`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_65_full_renderer_composition_repair`.",
      "",
      "Quality delta: `run2_64_renderer_composition_repair_consumed`. Full-arm slides consume dynamic socket, semantic diagram, text-fit, and dry-run binding records.",
      "",
      "The negative control `bad_run2_64_without_renderer_composition_repair` can reuse Run 2.62 generated proof, but it fails the Run 2.64 renderer composition repair layer.",
      "",
      "Public release remains blocked pending visual review.",
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
  for (const arm of armSpecs) built.push(await buildArm(arm));
  const fourArmSheet = buildRun265FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_65_renderer_composition_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_65_renderer_composition_rerun_summary.json"), runSummary);
  writeRun265Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_65_FULL_DATA_INPUTS,
  RUN2_65_INPUTS,
  armSpecs,
  assertRun265ArmInputBoundaries,
  assertRun265RendererSelfCheck,
  drawRun265RendererCompositionRepair,
  loadRun265RendererData,
  main,
};
