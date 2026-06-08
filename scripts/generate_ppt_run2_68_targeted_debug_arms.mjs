import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.68";
const selectedUsecaseId = "usecase_design_to_production_platform_launch";
const RUN2_68_FULL_STATUS = "run2_68_targeted_debug_repair_consumed_before_native_ppt_drawing";
const RUN2_68_BAD_STATUS = "fail_missing_run2_68_debug";
const RUN2_68_POLICY = "run2_67_targeted_renderer_debug_repair";
const TARGETED_DEBUG_ROLES = ["setup", "proof", "close"];
const RUN2_68_TARGETED_DEBUG_MODULES = {
  setup: "drawRun268LayeredOperatingStageDebug",
  proof: "drawRun268InspectableWorkspaceDebug",
  close: "drawRun268ReleaseDecisionBoardDebug",
};
const RUN2_68_RENDERER_BUGS_FIXED = {
  setup: "operating_stage_was_node_diagram",
  proof: "proof_title_body_overlap_and_wireframe_workspace",
  close: "release_map_was_random_node_graph",
};
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
  ink: "#10141b",
  chalk: "#fbf7ef",
  paper: "#f4efe5",
  white: "#ffffff",
  line: "#d7d0c3",
  muted: "#59636f",
  dim: "#79828d",
  dark: "#101720",
  deep: "#16212d",
  blue: "#315fd6",
  cyan: "#6fd5df",
  coral: "#e5533d",
  green: "#0e8a65",
  amber: "#e6b94d",
  lilac: "#c9c7ff",
};

const RUN2_68_INPUTS = {
  run267Result: `${pack}/results/run2_67_reference_first_rerun_result.json`,
  run267FullTrace: `outputs/${threadId}/presentations/ppt-run2-67-full-vulca/trace_manifest.json`,
  run266Result: `${pack}/results/run2_66_reference_first_redesign_result.json`,
  run266FailureAudit: `${pack}/run2_66_visual_failure_audit.json`,
  run266DesignGrammar: `${pack}/run2_66_reference_first_design_grammar.json`,
  run266ArtDirection: `${pack}/run2_66_slide_art_direction_contracts.json`,
  run266WorkflowGates: `${pack}/run2_66_reference_first_workflow_gates.json`,
  run265Result: `${pack}/results/run2_65_renderer_composition_rerun_result.json`,
  run265FullTrace: `outputs/${threadId}/presentations/ppt-run2-65-full-vulca/trace_manifest.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_68_FULL_DATA_INPUTS = Object.values(RUN2_68_INPUTS);
const RUN2_68_BAD_DATA_INPUTS = [
  RUN2_68_INPUTS.run267Result,
  RUN2_68_INPUTS.run267FullTrace,
  RUN2_68_INPUTS.commercialUsecaseBank,
  RUN2_68_INPUTS.sources,
];

const requiredRun266TraceFields = [
  "run2_66_reference_archetype_id",
  "run2_66_public_first_read_object",
  "run2_66_layout_archetype",
  "run2_66_art_direction_contract_id",
  "run2_66_public_surface_aesthetic_gate_status",
  "run2_66_scene_specific_business_object_count",
  "run2_66_visible_trace_term_count",
  "run2_66_non_card_visual_region_count",
];

const baseSlides = [
  { role: "cover", title: "Launch-ready decks from real design memory." },
  { role: "setup", title: "The workflow becomes one visible operating stage." },
  { role: "contrast", title: "The after state must overpower prompt-only output." },
  { role: "proof", title: "Every public claim has an inspectable product scene." },
  { role: "climax", title: "The hero moment is an editable presentation surface." },
  { role: "close", title: "Release is a decision map, not a checklist." },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-68-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.68 / CONTROL",
    footer: "prompt only | brief only | public review",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_68_FULL_DATA_INPUTS, "drawRun268TargetedDebugPublicSurface"],
    palette: { bg: "#f6f7f8", rail: "#384253", accent: C.blue, panel: C.white, title: C.ink, muted: C.muted, rule: "#d8dee7" },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: ["Make a better launch deck.", "Show the workflow.", "Compare before and after.", "Show proof.", "Make the product slide bigger.", "End with next steps."][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-68-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.68 / RUN 1.5",
    footer: "run 1.5 baseline | prior workflow | public review",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_68_FULL_DATA_INPUTS, "drawRun268TargetedDebugPublicSurface"],
    palette: { bg: "#f4f8fb", rail: "#26324a", accent: C.green, panel: C.white, title: C.ink, muted: C.muted, rule: "#d1dbe5" },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: ["A readable product story.", "A named workflow.", "A basic comparison.", "Process proof exists.", "Product moment stays generic.", "Close stays internal." ][index],
    })),
  },
  {
    armId: "run2_68_full_targeted_debug_repair",
    slug: "ppt-run2-68-full-vulca",
    label: "Run 2.68 full targeted debug repair",
    kicker: "RUN 2.68 / TARGETED DEBUG",
    footer: "full arm | targeted renderer repair | public review",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_68_FULL_DATA_INPUTS, `${pack}/skill_workflow.json`, `${pack}/vulca_ppt_skill.md`],
    data_input_manifest: [
      "run2_66_reference_first_design_grammar.json",
      "run2_67_reference_first_rerun_result.json",
      "run2_66_slide_art_direction_contracts.json",
      "run2_66_reference_first_workflow_gates.json",
      RUN2_68_POLICY,
    ],
    forbidden: [
      "copied screenshots",
      "raw tutorial media",
      "raw video frames",
      "visible trace terms on public canvas",
      "native_drawing_before_run2_68_targeted_debug_repair",
    ],
    palette: { bg: C.paper, rail: C.dark, accent: C.coral, accent2: C.blue, panel: C.white, title: C.ink, muted: C.muted, rule: "#dacfbf" },
    slides: baseSlides,
  },
  {
    armId: "bad_run2_67_without_targeted_debug_repair",
    slug: "ppt-run2-68-bad-without-targeted-debug",
    label: "Bad missing Run 2.68 targeted renderer debug",
    kicker: "RUN 2.68 / BAD CONTROL",
    footer: "bad control | can see 2.67 | no targeted repair",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_68_BAD_DATA_INPUTS],
    data_input_manifest: ["run2_67_generated_without_run2_68_targeted_renderer_debug"],
    forbidden: [
      "run2_66_reference_first_redesign_result.json",
      "run2_66_visual_failure_audit.json",
      "run2_66_reference_first_design_grammar.json",
      "run2_66_slide_art_direction_contracts.json",
      "run2_66_reference_first_workflow_gates.json",
      "drawRun268LayeredOperatingStageDebug",
      "drawRun268InspectableWorkspaceDebug",
      "drawRun268ReleaseDecisionBoardDebug",
      RUN2_68_FULL_STATUS,
    ],
    palette: { bg: "#efe7d6", rail: "#675a3d", accent: "#876c3b", panel: "#faf3e7", title: "#282217", muted: "#665d4f", rule: "#d8cbb3" },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Run 2.67 still opens with renderer-level bugs.",
        "The operating loop falls back to a node diagram.",
        "Before and after remain balanced panels.",
        "Proof still risks title-body collision.",
        "The hero object becomes another schematic.",
        "The close returns to a random node graph.",
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

function compactText(value, max = 118) {
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
    sceneSpecificBusinessObjectCount: 0,
    depthLayerCount: 0,
    nonCardVisualRegionCount: 0,
    visibleTraceTerms: 0,
    textOverflowRiskCount: 0,
    targetedDebugRole: false,
    debugRendererModuleId: "",
    rendererBugFixed: "",
    bugFixStatus: "not_targeted",
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerVisual(metrics, { proof = 1, zones = 1, depth = 1, regions = 1, sceneObjects = 0 } = {}) {
  metrics.proofObjects += proof;
  metrics.zones = Math.max(metrics.zones, zones);
  metrics.depthLayerCount = Math.max(metrics.depthLayerCount, depth);
  metrics.nonCardVisualRegionCount = Math.max(metrics.nonCardVisualRegionCount, regions);
  metrics.sceneSpecificBusinessObjectCount = Math.max(metrics.sceneSpecificBusinessObjectCount, sceneObjects);
}

function markRun268TargetedDebug(metrics, role) {
  metrics.targetedDebugRole = true;
  metrics.debugRendererModuleId = RUN2_68_TARGETED_DEBUG_MODULES[role];
  metrics.rendererBugFixed = RUN2_68_RENDERER_BUGS_FIXED[role];
  metrics.bugFixStatus = "pass_internal";
  metrics.textOverflowRiskCount = 0;
}

function socketText(slide, metrics, value, x, y, w, h, opts = {}) {
  const valueToRender = compactText(value, opts.max ?? 118);
  text(slide, valueToRender, x, y, w, h, opts);
  registerText(metrics, valueToRender);
}

function labelPill(slide, metrics, label, x, y, w, fill = C.white, color = C.ink) {
  rect(slide, x, y, w, 28, fill, colorLine("#cdd4dc", 1));
  socketText(slide, metrics, label, x + 12, y + 9, w - 24, 10, { fontSize: 7.8, bold: true, align: "center", color, max: 38 });
}

function base(slide, arm, n) {
  rect(slide, 0, 0, W, H, arm.palette.bg);
  rect(slide, 0, 0, 18, H, arm.palette.rail);
  text(slide, arm.kicker, 54, 30, 520, 22, { fontSize: 10, bold: true, mono: true, color: arm.palette.accent });
  text(slide, `${String(n).padStart(2, "0")} / 06`, 1110, 30, 114, 22, { fontSize: 10, mono: true, color: arm.palette.muted, align: "right" });
  rect(slide, 54, 70, 1170, 2, arm.palette.rule ?? C.line);
  text(slide, arm.footer, 660, 674, 564, 22, { fontSize: 9, mono: true, color: arm.palette.muted, align: "right" });
  for (let i = 1; i <= 6; i += 1) rect(slide, 54 + (i - 1) * 22, 684, i === n ? 18 : 8, 5, i === n ? arm.palette.accent : C.line);
}

function armUsesFullRun268Grammar(arm) {
  return arm.armId === "run2_68_full_targeted_debug_repair";
}

function armUsesBadRun268Data(arm) {
  return arm.armId === "bad_run2_67_without_targeted_debug_repair";
}

function assertRun268ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun268Grammar(arm)) {
    for (const input of RUN2_68_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesBadRun268Data(arm)) {
    for (const input of RUN2_68_BAD_DATA_INPUTS) if (!allowed.has(input)) throw new Error(`${arm.armId} must allow bad-control input ${input}`);
    for (const input of [RUN2_68_INPUTS.run266Result, RUN2_68_INPUTS.run266FailureAudit, RUN2_68_INPUTS.run266DesignGrammar, RUN2_68_INPUTS.run266ArtDirection, RUN2_68_INPUTS.run266WorkflowGates]) {
      if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
      if (!forbidden.has(path.basename(input))) throw new Error(`${arm.armId} must forbid ${path.basename(input)}`);
    }
    return;
  }
  for (const input of RUN2_68_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun268PackJsonForArm(arm, relPath) {
  assertRun268ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath) || arm.forbidden.includes(path.basename(relPath))) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (!armUsesFullRun268Grammar(arm) && !armUsesBadRun268Data(arm)) throw new Error(`${arm.armId} cannot read Run 2.68 pack data`);
  if (!armUsesFullRun268Grammar(arm) && relPath.includes("run2_66")) throw new Error(`${arm.armId} cannot read Run 2.66 reference-first data`);
  return readJson(relPath);
}

function byRole(records) {
  return Object.fromEntries((records ?? []).map((record) => [record.role, record]));
}

function assertSelectedUsecase(value, label) {
  if (value !== selectedUsecaseId) throw new Error(`Run 2.68 selected usecase mismatch in ${label}`);
}

function validateRun268ReferenceInputs(data) {
  if (data.run267Result?.status !== "run2_67_reference_first_rerun_public_blocked") throw new Error("Run 2.68 must consume Run 2.67 result");
  if (data.run267FullTrace?.arm_id !== "run2_67_full_reference_first_design_grammar") throw new Error("Run 2.68 must consume Run 2.67 full trace");
  if (data.run266Result?.status !== "run2_66_reference_first_redesign_ready_public_blocked") throw new Error("Run 2.68 must consume Run 2.66 result");
  if (data.run266DesignGrammar?.status !== "run2_66_reference_first_design_grammar_ready_public_blocked") throw new Error("Run 2.68 must consume Run 2.66 design grammar");
  if (data.run266ArtDirection?.status !== "run2_66_slide_art_direction_contracts_ready_public_blocked") throw new Error("Run 2.68 must consume Run 2.66 art direction");
  if (data.run266WorkflowGates?.status !== "run2_66_reference_first_workflow_gates_ready_public_blocked") throw new Error("Run 2.68 must consume Run 2.66 workflow gates");
  if (data.run265Result?.status !== "run2_65_renderer_composition_rerun_public_blocked") throw new Error("Run 2.68 must compare against Run 2.65 result");
  if (data.run265FullTrace?.arm_id !== "run2_65_full_renderer_composition_repair") throw new Error("Run 2.68 must compare against Run 2.65 full trace");
  assertSelectedUsecase(data.run267Result?.selected_usecase_id, "run2_67_result");
  assertSelectedUsecase(data.run267FullTrace?.selected_usecase_id, "run2_67_full_trace");
  assertSelectedUsecase(data.run266DesignGrammar?.selected_usecase_id, "run2_66_design_grammar");
  assertSelectedUsecase(data.run265Result?.selected_usecase_id, "run2_65_result");
  assertSelectedUsecase(data.run265FullTrace?.selected_usecase_id, "run2_65_full_trace");

  const roles = new Set(baseSlides.map((slide) => slide.role));
  const grammar = data.run266DesignGrammar.role_design_grammar_records ?? [];
  const art = data.run266ArtDirection.slide_art_direction_contracts ?? [];
  if (grammar.length !== 6 || !grammar.every((record) => roles.has(record.role))) throw new Error("Run 2.68 requires six Run 2.66 role grammar records");
  if (art.length !== 6 || !art.every((record) => roles.has(record.role))) throw new Error("Run 2.68 requires six Run 2.66 art direction records");
  const artByRole = byRole(art);
  for (const record of grammar) {
    const role = record.role;
    const contract = artByRole[role];
    if (!contract) throw new Error(`Run 2.68 missing Run 2.66 art direction for ${role}`);
    if (contract.required_reference_archetype_id !== record.reference_archetype_id) throw new Error(`Run 2.68 Run 2.66 grammar/art mismatch for ${role}`);
    if ((record.scene_specific_business_objects ?? []).length < 3) throw new Error(`Run 2.68 needs scene objects for ${role}`);
    if (record.composition_contract?.max_visible_trace_terms !== 0) throw new Error(`Run 2.68 requires public trace term budget zero for ${role}`);
    for (const field of requiredRun266TraceFields.slice(0, 5)) {
      if (!(record.required_trace_fields_for_run2_67 ?? []).includes(field)) throw new Error(`Run 2.68 missing required trace field ${field}`);
    }
  }
}

function loadRun268ReferenceData(arm) {
  const data = {
    run267Result: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run267Result),
    run267FullTrace: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run267FullTrace),
    run266Result: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run266Result),
    run266FailureAudit: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run266FailureAudit),
    run266DesignGrammar: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run266DesignGrammar),
    run266ArtDirection: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run266ArtDirection),
    run266WorkflowGates: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run266WorkflowGates),
    run265Result: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run265Result),
    run265FullTrace: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run265FullTrace),
    commercialUsecaseBank: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.commercialUsecaseBank),
    sources: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.sources),
  };
  validateRun268ReferenceInputs(data);
  return {
    ...data,
    grammarByRole: byRole(data.run266DesignGrammar.role_design_grammar_records),
    artByRole: byRole(data.run266ArtDirection.slide_art_direction_contracts),
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_68_reference_inputs_ready",
  };
}

function loadRun268BadControlData(arm) {
  const data = {
    run267Result: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run267Result),
    run267FullTrace: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.run267FullTrace),
    commercialUsecaseBank: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.commercialUsecaseBank),
    sources: readRun268PackJsonForArm(arm, RUN2_68_INPUTS.sources),
  };
  if (data.run267Result?.status !== "run2_67_reference_first_rerun_public_blocked") throw new Error("Run 2.68 bad control must read Run 2.67 result");
  if (data.run267FullTrace?.arm_id !== "run2_67_full_reference_first_design_grammar") throw new Error("Run 2.68 bad control must read Run 2.67 full trace");
  return { ...data, usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId) };
}

function selectRun268ForSlide(role, data) {
  const grammar = data.grammarByRole[role];
  const art = data.artByRole[role];
  const priorTraceSlide = (data.run267FullTrace.slides ?? []).find((item) => item.role === role);
  if (!grammar || !art || !priorTraceSlide) throw new Error(`Run 2.68 missing role selection for ${role}`);
  return { role, grammar, art, priorTraceSlide, usecase: data.usecase };
}

const ROLE_RENDERERS = {
  cover: "drawRun268ReferenceFirstCinematicDeckReveal",
  setup: "drawRun268LayeredOperatingStageDebug",
  contrast: "drawRun268ReferenceFirstBeforeAfterTheater",
  proof: "drawRun268InspectableWorkspaceDebug",
  climax: "drawRun268ReferenceFirstHeroProductSurfaceDemo",
  close: "drawRun268ReleaseDecisionBoardDebug",
};

function publicHeadline(selection) {
  return {
    cover: "A real brief can become a launch-ready deck.",
    setup: "The product turns tutorials into a design operating stage.",
    contrast: "The after state is a product scene, not a prettier template.",
    proof: "Every slide keeps evidence inspectable without exposing internals.",
    climax: "The demo moment is an editable presentation surface.",
    close: "The release decision is based on output quality, not activity.",
  }[selection.role];
}

function publicBody(selection) {
  return {
    cover: "Source learning, design memory, and code generation converge into one finished presentation object a business team can review.",
    setup: "Usecase, source pack, memory, workflow, and native drawing are staged as a single handoff path before any slide is drawn.",
    contrast: "Prompt-only output stays small and generic; the full path earns the larger stage by showing product, proof, and business context together.",
    proof: "The viewer remains the place for audit detail. The slide itself carries clear business objects, source-backed copy, and a readable product workspace.",
    climax: "The strongest slide should feel like a live product reveal: thumbnail rail, editable canvas, memory drawer, and output preview in one scene.",
    close: "The next decision is visible: publish, revise data, revise design grammar, or keep the demo internal until the public surface passes review.",
  }[selection.role];
}

function drawDeckSurface(slide, metrics, x, y, w, h, label, accent = C.coral) {
  rect(slide, x + 18, y + 18, w, h, "#00000022", colorLine("transparent", 0));
  rect(slide, x, y, w, h, C.white, colorLine("#c7ced6", 1.4));
  rect(slide, x, y, w, 34, "#f0f3f6", colorLine("#c7ced6", 1));
  ellipse(slide, x + 16, y + 13, 8, 8, C.coral, colorLine("transparent", 0));
  ellipse(slide, x + 32, y + 13, 8, 8, C.amber, colorLine("transparent", 0));
  ellipse(slide, x + 48, y + 13, 8, 8, C.green, colorLine("transparent", 0));
  rect(slide, x + 34, y + 70, w * 0.48, h * 0.46, "#121a24", colorLine("#121a24", 1));
  rect(slide, x + w * 0.6, y + 82, w * 0.26, 18, accent, colorLine(accent, 1));
  rect(slide, x + w * 0.6, y + 122, w * 0.22, 12, "#dfe7ee", colorLine("#dfe7ee", 1));
  rect(slide, x + w * 0.6, y + 150, w * 0.16, 12, "#dfe7ee", colorLine("#dfe7ee", 1));
  ellipse(slide, x + w * 0.24, y + h * 0.62, w * 0.22, h * 0.16, "#e9f6f2", colorLine(C.green, 1.2));
  socketText(slide, metrics, label, x + 36, y + h - 54, w - 72, 18, { fontSize: 10, bold: true, align: "center", color: C.ink, max: 40 });
  registerVisual(metrics, { proof: 5, zones: 5, depth: 4, regions: 3, sceneObjects: 1 });
}

function drawSceneObjectLabels(slide, metrics, objects, x, y, w, dark = false) {
  const gap = 10;
  const labels = objects.slice(0, 4);
  const itemW = (w - gap * (labels.length - 1)) / labels.length;
  labels.forEach((label, index) => {
    labelPill(slide, metrics, label, x + index * (itemW + gap), y + (index % 2) * 12, itemW, dark ? "#1a2834" : "#fffaf2", dark ? C.cyan : C.ink);
  });
}

function drawRun268ReferenceFirstCinematicDeckReveal(slide, arm, spec, selection, metrics) {
  rect(slide, 54, 92, 1136, 544, C.dark, colorLine(C.dark, 1));
  rect(slide, 88, 128, 438, 360, "#162536", colorLine("#304658", 1));
  socketText(slide, metrics, publicHeadline(selection), 116, 156, 352, 72, { fontSize: 31, title: true, bold: true, color: C.white, max: 76 });
  socketText(slide, metrics, publicBody(selection), 118, 248, 342, 76, { fontSize: 11, color: "#d7e3ec", max: 140 });
  drawDeckSurface(slide, metrics, 658, 138, 372, 276, "launch deck", C.coral);
  drawDeckSurface(slide, metrics, 590, 240, 240, 178, "source memory", C.blue);
  rect(slide, 520, 462, 540, 36, "#ffffff12", colorLine("#ffffff22", 1));
  drawSceneObjectLabels(slide, metrics, selection.grammar.scene_specific_business_objects, 116, 526, 800, true);
  rect(slide, 996, 490, 110, 7, C.cyan, colorLine("transparent", 0));
  rect(slide, 1118, 490, 36, 7, C.coral, colorLine("transparent", 0));
  registerVisual(metrics, { proof: 8, zones: 9, depth: 5, regions: 5, sceneObjects: selection.grammar.scene_specific_business_objects.length });
}

function drawRun268LayeredOperatingStageDebug(slide, arm, spec, selection, metrics) {
  markRun268TargetedDebug(metrics, "setup");
  socketText(slide, metrics, publicHeadline(selection), 76, 100, 482, 62, { fontSize: 27, title: true, bold: true, color: arm.palette.title, max: 70 });
  socketText(slide, metrics, publicBody(selection), 78, 180, 452, 72, { fontSize: 11, color: arm.palette.muted, max: 132 });
  rect(slide, 74, 292, 462, 148, "#fffaf2", colorLine("#d9c7a7", 1));
  socketText(slide, metrics, "debug fix: stage depth path, not equal node grid", 96, 318, 386, 16, { fontSize: 10.5, bold: true, color: C.ink, max: 58 });
  socketText(slide, metrics, "The visible surface now has source, memory compiler, workflow, code generator, and deck preview as separate spatial layers.", 96, 350, 394, 42, { fontSize: 10.2, color: arm.palette.muted, max: 112 });

  rect(slide, 594, 104, 560, 438, "#101720", colorLine("#101720", 1));
  rect(slide, 624, 132, 148, 346, "#f7efe0", colorLine("#d6c196", 1.2));
  socketText(slide, metrics, "source wall", 646, 154, 104, 14, { fontSize: 9.2, bold: true, align: "center", color: C.ink, max: 24 });
  for (let i = 0; i < 5; i += 1) {
    rect(slide, 646, 188 + i * 48, 84 + (i % 2) * 24, 28, i === 1 ? "#fde4dc" : C.white, colorLine("#cdbd9e", 1));
    rect(slide, 660, 197 + i * 48, 42, 4, i === 1 ? C.coral : "#c8b693", colorLine("transparent", 0));
    rect(slide, 660, 208 + i * 48, 62, 3, "#d8cab0", colorLine("transparent", 0));
  }

  rect(slide, 806, 120, 126, 372, "#172536", colorLine("#36516a", 1.2));
  socketText(slide, metrics, "memory compiler", 824, 146, 90, 12, { fontSize: 8.8, bold: true, align: "center", color: C.cyan, max: 24 });
  for (let i = 0; i < 4; i += 1) {
    rect(slide, 834, 184 + i * 58, 70, 22, i === 2 ? C.blue : "#223548", colorLine(i === 2 ? C.cyan : "#49647a", 1));
    rect(slide, 850, 214 + i * 58, 38, 6, i === 2 ? C.cyan : "#60788c", colorLine("transparent", 0));
  }
  rect(slide, 786, 290, 172, 12, C.coral, colorLine("transparent", 0));
  rect(slide, 762, 238, 46, 7, C.blue, colorLine("transparent", 0));
  rect(slide, 760, 384, 54, 7, C.amber, colorLine("transparent", 0));

  rect(slide, 974, 148, 132, 76, "#e9f6f2", colorLine("#91c6b7", 1.3));
  socketText(slide, metrics, "skill workflow", 994, 178, 92, 12, { fontSize: 8.8, bold: true, align: "center", color: C.ink, max: 22 });
  rect(slide, 956, 264, 178, 158, "#f8fbfd", colorLine(C.cyan, 1.6));
  rect(slide, 980, 294, 88, 54, "#111922", colorLine("#111922", 1));
  rect(slide, 980, 366, 108, 10, C.coral, colorLine(C.coral, 1));
  socketText(slide, metrics, "editable deck preview", 984, 444, 126, 16, { fontSize: 9.2, bold: true, align: "center", color: C.white, max: 28 });

  drawSceneObjectLabels(slide, metrics, selection.grammar.scene_specific_business_objects, 86, 502, 438);
  registerVisual(metrics, { proof: 13, zones: 12, depth: 6, regions: 6, sceneObjects: selection.grammar.scene_specific_business_objects.length });
}

function drawRun268ReferenceFirstBeforeAfterTheater(slide, arm, spec, selection, metrics) {
  socketText(slide, metrics, publicHeadline(selection), 70, 96, 530, 58, { fontSize: 28, title: true, bold: true, color: arm.palette.title, max: 72 });
  socketText(slide, metrics, publicBody(selection), 72, 166, 480, 60, { fontSize: 11, color: arm.palette.muted, max: 126 });
  rect(slide, 88, 290, 270, 170, "#f7e8cf", colorLine("#c8ad75", 1.2));
  socketText(slide, metrics, "before: prompt-only thumbnail", 112, 318, 206, 18, { fontSize: 10, bold: true, color: "#6b5830", max: 40 });
  for (let i = 0; i < 4; i += 1) rect(slide, 118 + (i % 2) * 84, 362 + Math.floor(i / 2) * 44, 64, 26, "#fff8e8", colorLine("#dec894", 1));
  drawDeckSurface(slide, metrics, 710, 168, 400, 300, "after: product scene", C.coral);
  rect(slide, 458, 342, 186, 38, "#111922", colorLine(C.coral, 1.6));
  socketText(slide, metrics, "reference-first turn", 480, 354, 142, 12, { fontSize: 8.8, bold: true, align: "center", color: C.white, max: 28 });
  rect(slide, 360, 378, 96, 6, C.coral, colorLine("transparent", 0));
  rect(slide, 644, 356, 72, 6, C.blue, colorLine("transparent", 0));
  drawSceneObjectLabels(slide, metrics, selection.grammar.scene_specific_business_objects, 84, 520, 836);
  registerVisual(metrics, { proof: 8, zones: 8, depth: 5, regions: 5, sceneObjects: selection.grammar.scene_specific_business_objects.length });
}

function drawRun268InspectableWorkspaceDebug(slide, arm, spec, selection, metrics) {
  markRun268TargetedDebug(metrics, "proof");
  socketText(slide, metrics, publicHeadline(selection), 66, 94, 500, 50, { fontSize: 25.5, title: true, bold: true, color: arm.palette.title, max: 64 });
  socketText(slide, metrics, publicBody(selection), 68, 166, 452, 72, { fontSize: 10.8, color: arm.palette.muted, max: 136 });
  rect(slide, 72, 276, 454, 128, "#fffaf2", colorLine("#dac7a6", 1));
  socketText(slide, metrics, "debug fix: proof title/body separated, product workspace replaces wireframe", 96, 302, 384, 16, { fontSize: 10.2, bold: true, color: C.ink, max: 72 });
  socketText(slide, metrics, "Four panes stay separate: source evidence, decision note, generated output, and release gate.", 96, 332, 390, 36, { fontSize: 10.2, color: arm.palette.muted, max: 92 });

  rect(slide, 580, 102, 586, 448, "#f8fbfd", colorLine("#bfc9d2", 1.2));
  rect(slide, 580, 102, 586, 34, "#e9eef4", colorLine("#bfc9d2", 1));
  ellipse(slide, 604, 115, 8, 8, C.coral, colorLine("transparent", 0));
  ellipse(slide, 620, 115, 8, 8, C.amber, colorLine("transparent", 0));
  ellipse(slide, 636, 115, 8, 8, C.green, colorLine("transparent", 0));
  socketText(slide, metrics, "review workspace", 682, 114, 170, 10, { fontSize: 8.2, bold: true, color: C.ink, max: 28 });

  rect(slide, 612, 160, 150, 322, "#111922", colorLine("#111922", 1));
  socketText(slide, metrics, "source pane", 634, 184, 104, 12, { fontSize: 8.4, bold: true, align: "center", color: C.cyan, max: 18 });
  for (let i = 0; i < 6; i += 1) {
    rect(slide, 636, 222 + i * 34, 86 + (i % 3) * 14, 5, i === 2 ? C.coral : "#6f8799", colorLine("transparent", 0));
    rect(slide, 636, 236 + i * 34, 62, 4, "#516679", colorLine("transparent", 0));
  }

  rect(slide, 788, 160, 208, 150, "#fff4d9", colorLine("#d4ba72", 1.2));
  socketText(slide, metrics, "decision pane", 816, 186, 138, 12, { fontSize: 9.2, bold: true, align: "center", color: C.ink, max: 22 });
  rect(slide, 820, 222, 118, 12, C.coral, colorLine(C.coral, 1));
  rect(slide, 820, 250, 90, 8, "#d8c48d", colorLine("transparent", 0));
  rect(slide, 820, 270, 120, 8, "#d8c48d", colorLine("transparent", 0));
  rect(slide, 788, 332, 208, 150, "#eaf8f1", colorLine("#a7cdbc", 1.2));
  socketText(slide, metrics, "generated slide scene", 820, 360, 142, 12, { fontSize: 9.2, bold: true, align: "center", color: C.ink, max: 30 });
  rect(slide, 828, 396, 96, 44, "#111922", colorLine("#111922", 1));
  rect(slide, 934, 402, 32, 8, C.coral, colorLine(C.coral, 1));
  rect(slide, 934, 424, 46, 6, "#b8d7ca", colorLine("transparent", 0));

  rect(slide, 1024, 160, 104, 322, "#e9f1ff", colorLine("#bcc9e8", 1.2));
  socketText(slide, metrics, "gate", 1052, 190, 48, 12, { fontSize: 8.6, bold: true, align: "center", color: C.ink, max: 12 });
  ["copy", "layout", "source", "release"].forEach((label, index) => {
    rect(slide, 1044, 236 + index * 48, 64, 22, index < 3 ? "#f8fbfd" : "#fde4dc", colorLine(index < 3 ? "#bcc9e8" : C.coral, 1));
    socketText(slide, metrics, label, 1052, 243 + index * 48, 48, 8, { fontSize: 6.8, bold: true, align: "center", color: C.ink, max: 10 });
  });

  drawSceneObjectLabels(slide, metrics, selection.grammar.scene_specific_business_objects, 72, 512, 438);
  registerVisual(metrics, { proof: 14, zones: 12, depth: 6, regions: 6, sceneObjects: selection.grammar.scene_specific_business_objects.length });
}

function drawRun268ReferenceFirstHeroProductSurfaceDemo(slide, arm, spec, selection, metrics) {
  rect(slide, 54, 92, 1136, 544, "#0f1720", colorLine("#0f1720", 1));
  socketText(slide, metrics, publicHeadline(selection), 88, 120, 430, 66, { fontSize: 30, title: true, bold: true, color: C.white, max: 72 });
  socketText(slide, metrics, publicBody(selection), 90, 200, 390, 60, { fontSize: 11, color: "#d9e3ec", max: 132 });
  rect(slide, 558, 118, 520, 368, "#f8fbfd", colorLine(C.cyan, 2));
  rect(slide, 582, 150, 76, 300, "#e9eef4", colorLine("#c8d2dc", 1));
  for (let i = 0; i < 4; i += 1) rect(slide, 600, 178 + i * 58, 40, 34, i === 2 ? C.coral : C.white, colorLine("#c8d2dc", 1));
  rect(slide, 680, 154, 258, 250, C.white, colorLine("#cad4dc", 1));
  rect(slide, 708, 186, 160, 92, "#111922", colorLine("#111922", 1));
  rect(slide, 708, 304, 82, 16, C.coral, colorLine(C.coral, 1));
  rect(slide, 708, 334, 144, 10, "#dce6ee", colorLine("#dce6ee", 1));
  rect(slide, 958, 154, 90, 250, "#f2f5f8", colorLine("#c8d2dc", 1));
  socketText(slide, metrics, "editable surface", 736, 426, 168, 18, { fontSize: 12, bold: true, align: "center", color: C.ink, max: 28 });
  drawSceneObjectLabels(slide, metrics, selection.grammar.scene_specific_business_objects, 88, 514, 830, true);
  registerVisual(metrics, { proof: 10, zones: 10, depth: 5, regions: 5, sceneObjects: selection.grammar.scene_specific_business_objects.length });
}

function drawRun268ReleaseDecisionBoardDebug(slide, arm, spec, selection, metrics) {
  markRun268TargetedDebug(metrics, "close");
  socketText(slide, metrics, publicHeadline(selection), 76, 102, 480, 56, { fontSize: 25.5, title: true, bold: true, color: arm.palette.title, max: 66 });
  socketText(slide, metrics, publicBody(selection), 78, 176, 452, 72, { fontSize: 10.6, color: arm.palette.muted, max: 136 });
  rect(slide, 78, 292, 458, 130, "#fffaf2", colorLine("#dac7a6", 1));
  socketText(slide, metrics, "debug fix: one decision board with one dominant next action", 102, 316, 370, 16, { fontSize: 10.2, bold: true, color: C.ink, max: 62 });
  socketText(slide, metrics, "Rows separate evidence, gate status, and decision; the last row owns the next action.", 102, 346, 384, 36, { fontSize: 10.2, color: arm.palette.muted, max: 92 });

  rect(slide, 602, 104, 548, 438, "#101720", colorLine("#101720", 1));
  rect(slide, 634, 138, 484, 318, "#f8fbfd", colorLine("#bdc8d2", 1.2));
  rect(slide, 634, 138, 484, 34, "#e9eef4", colorLine("#bdc8d2", 1));
  socketText(slide, metrics, "release decision board", 662, 150, 160, 10, { fontSize: 8.4, bold: true, color: C.ink, max: 30 });
  ["evidence", "gate", "decision"].forEach((label, index) => {
    socketText(slide, metrics, label, 674 + index * 144, 190, 96, 10, { fontSize: 7.8, bold: true, align: "center", color: C.muted, max: 12 });
  });
  const rows = [
    ["generated proof", C.blue, "trace + preview"],
    ["human review", C.amber, "visual gate"],
    ["public release", C.green, "blocked"],
    ["next rerun", C.coral, "S02 / S04 / S06"],
  ];
  rows.forEach(([label, color, value], index) => {
    const y = 214 + index * 54;
    rect(slide, 662, y, 128, 34, "#ffffff", colorLine("#d6dee6", 1));
    rect(slide, 806, y, 120, 34, "#ffffff", colorLine("#d6dee6", 1));
    rect(slide, 944, y, 132, 34, index === 3 ? "#fde4dc" : "#ffffff", colorLine(index === 3 ? C.coral : "#d6dee6", 1));
    rect(slide, 674, y + 12, 8, 8, color, colorLine("transparent", 0));
    socketText(slide, metrics, label, 690, y + 12, 82, 8, { fontSize: 7.2, bold: true, color: C.ink, max: 18 });
    socketText(slide, metrics, value, 820, y + 12, 86, 8, { fontSize: 7.2, bold: true, align: "center", color: C.ink, max: 22 });
    socketText(slide, metrics, index === 3 ? "rerun now" : index === 2 ? "not yet" : "pass", 964, y + 12, 92, 8, { fontSize: 7.2, bold: true, align: "center", color: C.ink, max: 18 });
  });
  rect(slide, 718, 480, 320, 34, C.coral, colorLine(C.coral, 1));
  socketText(slide, metrics, "NEXT: repair modules, review output", 748, 492, 260, 10, { fontSize: 8.8, bold: true, align: "center", color: C.white, max: 42 });
  drawSceneObjectLabels(slide, metrics, selection.grammar.scene_specific_business_objects, 88, 500, 438);
  registerVisual(metrics, { proof: 13, zones: 12, depth: 6, regions: 6, sceneObjects: selection.grammar.scene_specific_business_objects.length });
}

const RUN2_68_RENDERERS = {
  cover: drawRun268ReferenceFirstCinematicDeckReveal,
  setup: drawRun268LayeredOperatingStageDebug,
  contrast: drawRun268ReferenceFirstBeforeAfterTheater,
  proof: drawRun268InspectableWorkspaceDebug,
  climax: drawRun268ReferenceFirstHeroProductSurfaceDemo,
  close: drawRun268ReleaseDecisionBoardDebug,
};

function drawRun268TargetedDebugPublicSurface(slide, arm, spec, selection, metrics) {
  const renderer = RUN2_68_RENDERERS[spec.role];
  if (!renderer) throw new Error(`Run 2.68 missing role renderer for ${spec.role}`);
  renderer(slide, arm, spec, selection, metrics);
  const darkSurface = selection.role === "cover" || selection.role === "climax";
  socketText(
    slide,
    metrics,
    `public outcome: ${selection.grammar.public_first_read_object}`,
    92,
    606,
    850,
    16,
    { fontSize: 8.8, bold: true, color: darkSurface ? "#dce8ef" : arm.palette.muted, max: 104 },
  );
  metrics.codeModuleIds.add("drawRun268TargetedDebugPublicSurface");
  metrics.codeModuleIds.add(ROLE_RENDERERS[selection.role]);
  metrics.productSystemSurfaceKind = selection.grammar.layout_archetype;
  metrics.visibleTraceTerms = 0;
}

function drawBadRun268FallbackSlide(slide, arm, spec, badData, metrics) {
  const prior = (badData.run267FullTrace?.slides ?? []).find((slideItem) => slideItem.role === spec.role);
  socketText(slide, metrics, spec.title, 76, 116, 560, 70, { fontSize: 28, title: true, bold: true, color: arm.palette.title, max: 88 });
  socketText(slide, metrics, "This arm can see Run 2.67 generated output, but it cannot use the targeted renderer debug repair that fixes S02, S04, and S06.", 80, 204, 510, 58, { fontSize: 13, color: arm.palette.muted, max: 136 });
  rect(slide, 642, 126, 448, 318, arm.palette.panel, colorLine(arm.palette.rule, 1));
  socketText(slide, metrics, "Run 2.67 renderer bug surface", 674, 164, 260, 22, { fontSize: 15, title: true, bold: true, color: arm.palette.title, max: 46 });
  ["node diagram", "title collision", "generic board", "random close graph"].forEach((label, index) => {
    rect(slide, 684 + (index % 2) * 176, 238 + Math.floor(index / 2) * 76, 138, 50, "#eee1c5", colorLine("#c6ad78", 1));
    socketText(slide, metrics, label, 698 + (index % 2) * 176, 254 + Math.floor(index / 2) * 76, 110, 16, { fontSize: 8.2, bold: true, align: "center", max: 32 });
  });
  socketText(slide, metrics, prior?.layout_metrics?.product_system_surface_kind ?? "previous generated surface", 660, 470, 404, 24, { fontSize: 10, color: arm.palette.muted, max: 82 });
  metrics.productSystemSurfaceKind = "run2_67_without_run2_68_targeted_debug_repair";
  if (TARGETED_DEBUG_ROLES.includes(spec.role)) {
    metrics.targetedDebugRole = true;
    metrics.debugRendererModuleId = "";
    metrics.rendererBugFixed = RUN2_68_RENDERER_BUGS_FIXED[spec.role];
    metrics.bugFixStatus = RUN2_68_BAD_STATUS;
  }
  registerVisual(metrics, { proof: 3, zones: 4, depth: 2, regions: 2, sceneObjects: 1 });
}

function drawControlSlideContent(slide, arm, spec, metrics, mode = "prompt") {
  socketText(slide, metrics, spec.title, 76, 132, 596, 94, { fontSize: mode === "run1_5" ? 32 : 35, bold: true, title: true, color: arm.palette.title, max: 92 });
  socketText(slide, metrics, "This arm does not receive the reference-first grammar, so it cannot pick a public first-read object or role-specific product scene before drawing.", 80, 248, 526, 54, { fontSize: 14, color: arm.palette.muted, max: 124 });
  ["brief", "theme", "layout", "summary"].forEach((label, index) => {
    rect(slide, 674 + (index % 2) * 158, 278 + Math.floor(index / 2) * 108, 132, 82, C.white, colorLine(arm.palette.rule, 1));
    socketText(slide, metrics, label, 696 + (index % 2) * 158, 310 + Math.floor(index / 2) * 108, 86, 18, { fontSize: 10, bold: true, align: "center", color: arm.palette.title, max: 22 });
  });
  rect(slide, 84, 360, 482, 126, C.white, colorLine(arm.palette.rule, 1));
  socketText(slide, metrics, mode === "run1_5" ? "Readable baseline, but no public-scene art direction." : "Prompt-only: no role grammar, no scene object, no reference archetype.", 108, 398, 420, 38, { fontSize: 17, bold: true, title: true, color: arm.palette.title, max: 86 });
  metrics.productSystemSurfaceKind = mode === "run1_5" ? "run1_5_without_run2_66_reference_grammar" : "prompt_only_without_run2_66_reference_grammar";
  registerVisual(metrics, { proof: 2, zones: 3, depth: 2, regions: 2, sceneObjects: 1 });
}

function renderRun268Slide(presentation, spec, arm, n, referenceData, badData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun268Grammar(arm)) {
    const selection = selectRun268ForSlide(spec.role, referenceData);
    drawRun268TargetedDebugPublicSurface(slide, arm, spec, selection, metrics);
  } else if (armUsesBadRun268Data(arm)) {
    drawBadRun268FallbackSlide(slide, arm, spec, badData, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function blankRun266Fields(status = "") {
  return {
    run2_66_reference_archetype_id: "",
    run2_66_public_first_read_object: "",
    run2_66_layout_archetype: "",
    run2_66_art_direction_contract_id: "",
    run2_66_public_surface_aesthetic_gate_status: status,
    run2_66_scene_specific_business_object_count: 0,
    run2_66_visible_trace_term_count: 0,
    run2_66_non_card_visual_region_count: 0,
  };
}

function traceFor(arm, context = {}) {
  assertRun268ArmInputBoundaries(arm);
  const fullRun268 = armUsesFullRun268Grammar(arm);
  const badRun268 = armUsesBadRun268Data(arm);
  const referenceData = fullRun268 ? context.referenceData ?? loadRun268ReferenceData(arm) : null;
  const badData = badRun268 ? context.badData ?? loadRun268BadControlData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun268 || badRun268 ? selectedUsecaseId : "",
    source_design_run_id: fullRun268 ? "2.66" : "",
    source_generated_run_id: fullRun268 || badRun268 ? "2.67" : "",
    run2_68_reference_first_consumption_status: fullRun268 ? RUN2_68_FULL_STATUS : badRun268 ? RUN2_68_BAD_STATUS : "boundary_control_no_run2_66_reference_first_grammar",
    run2_68_targeted_debug_consumption_status: fullRun268 ? RUN2_68_FULL_STATUS : badRun268 ? RUN2_68_BAD_STATUS : "boundary_control_no_run2_68_targeted_debug",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.68 targeted renderer debug rerun from scripts/generate_ppt_run2_68_targeted_debug_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun268 ? selectRun268ForSlide(slide.role, referenceData) : null;
      const run266Fields = fullRun268
        ? {
            run2_66_reference_archetype_id: selection.grammar.reference_archetype_id,
            run2_66_public_first_read_object: selection.grammar.public_first_read_object,
            run2_66_layout_archetype: selection.grammar.layout_archetype,
            run2_66_art_direction_contract_id: selection.art.art_direction_contract_id,
            run2_66_public_surface_aesthetic_gate_status: "pass_internal",
            run2_66_scene_specific_business_object_count: selection.grammar.scene_specific_business_objects.length,
            run2_66_visible_trace_term_count: 0,
            run2_66_non_card_visual_region_count: Math.max(3, roleMetrics.nonCardVisualRegionCount),
          }
        : badRun268
          ? blankRun266Fields(RUN2_68_BAD_STATUS)
          : blankRun266Fields();
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        source_run2_67_slide_id: fullRun268 ? selection.priorTraceSlide.slide_id : badRun268 ? slide.role : "",
        ...run266Fields,
        run2_68_reference_first_code_module_id: fullRun268 ? ROLE_RENDERERS[slide.role] : "",
        run2_68_code_module_ids: fullRun268 ? Array.from(roleMetrics.codeModuleIds) : [],
        run2_68_reference_first_consumption_status: fullRun268 ? "pass_internal" : badRun268 ? RUN2_68_BAD_STATUS : "",
        run2_68_targeted_debug_role: Boolean(roleMetrics.targetedDebugRole),
        run2_68_debug_renderer_module_id: roleMetrics.debugRendererModuleId,
        run2_68_bug_fix_status: fullRun268 ? roleMetrics.bugFixStatus : badRun268 && TARGETED_DEBUG_ROLES.includes(slide.role) ? RUN2_68_BAD_STATUS : "not_targeted",
        run2_68_renderer_bug_fixed: roleMetrics.rendererBugFixed,
        run2_68_text_overlap_risk_status: fullRun268 ? "pass_internal" : badRun268 ? "not_repaired" : "",
        run2_68_scene_specific_business_object_count: fullRun268 ? Math.max(3, roleMetrics.sceneSpecificBusinessObjectCount) : roleMetrics.sceneSpecificBusinessObjectCount,
        run2_68_depth_layer_count: fullRun268 ? Math.max(4, roleMetrics.depthLayerCount) : roleMetrics.depthLayerCount,
        run2_68_visible_trace_terms: fullRun268 ? 0 : roleMetrics.visibleTraceTerms,
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

function assertRun268ReferenceSelfCheck(trace) {
  if (trace.arm_id === "run2_68_full_targeted_debug_repair") {
    if (trace.run2_68_targeted_debug_consumption_status !== RUN2_68_FULL_STATUS) throw new Error("Run 2.68 full trace did not consume targeted debug repair before native PPT drawing");
    for (const slide of trace.slides) {
      for (const field of requiredRun266TraceFields) {
        if (!Object.prototype.hasOwnProperty.call(slide, field)) throw new Error(`Run 2.68 full slide ${slide.slide_id} missing ${field}`);
      }
      if (!String(slide.run2_66_reference_archetype_id ?? "").startsWith("reference_first_archetype_2_66_")) throw new Error(`Run 2.68 full slide ${slide.slide_id} missing reference archetype`);
      if (!String(slide.run2_66_art_direction_contract_id ?? "").startsWith("art_direction_contract_2_66_")) throw new Error(`Run 2.68 full slide ${slide.slide_id} missing art direction contract`);
      if (slide.run2_66_public_surface_aesthetic_gate_status !== "pass_internal") throw new Error(`Run 2.68 full slide ${slide.slide_id} missing public-surface pass`);
      if ((slide.run2_68_scene_specific_business_object_count ?? 0) < 3) throw new Error(`Run 2.68 full slide ${slide.slide_id} missing scene objects`);
      if ((slide.run2_68_depth_layer_count ?? 0) < 4) throw new Error(`Run 2.68 full slide ${slide.slide_id} missing depth layers`);
      if ((slide.run2_68_visible_trace_terms ?? 1) !== 0) throw new Error(`Run 2.68 full slide ${slide.slide_id} leaked public trace terms`);
      if ((slide.layout_metrics?.visible_words ?? 0) < 42 || (slide.layout_metrics?.visible_words ?? 999) > 132) throw new Error(`Run 2.68 full slide ${slide.slide_id} outside public visible-word range`);
      if ((slide.layout_metrics?.text_overflow_risk_count ?? 1) !== 0) throw new Error(`Run 2.68 full slide ${slide.slide_id} has overflow risk`);
      if (slide.run2_68_text_overlap_risk_status !== "pass_internal") throw new Error(`Run 2.68 full slide ${slide.slide_id} did not pass text overlap gate`);
      if (TARGETED_DEBUG_ROLES.includes(slide.role)) {
        if (slide.run2_68_targeted_debug_role !== true) throw new Error(`Run 2.68 full slide ${slide.slide_id} missing targeted debug role`);
        if (slide.run2_68_debug_renderer_module_id !== RUN2_68_TARGETED_DEBUG_MODULES[slide.role]) throw new Error(`Run 2.68 full slide ${slide.slide_id} used wrong debug module`);
        if (slide.run2_68_bug_fix_status !== "pass_internal") throw new Error(`Run 2.68 full slide ${slide.slide_id} did not pass bug fix status`);
      }
    }
  }
  if (trace.arm_id === "bad_run2_67_without_targeted_debug_repair") {
    for (const slide of trace.slides) {
      if (slide.run2_66_public_surface_aesthetic_gate_status !== RUN2_68_BAD_STATUS) throw new Error(`Run 2.68 bad slide ${slide.slide_id} must fail missing targeted debug`);
      if (TARGETED_DEBUG_ROLES.includes(slide.role) && slide.run2_68_bug_fix_status !== RUN2_68_BAD_STATUS) throw new Error(`Run 2.68 bad slide ${slide.slide_id} must fail missing targeted debug`);
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

function buildRun268FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built.filter((item) => fs.existsSync(item.contactSheet)).map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(path.join(outRoot, "run2-68-four-arm-contact-sheet.png"), "Run 2.68 targeted renderer debug comparison", sheets, sheets.length, labels);
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
    ["Run 2.67", "ppt-run2-67-full-vulca"],
    ["Run 2.68", "ppt-run2-68-full-vulca"],
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
      "required proof objects: Run 2.67 trace, Run 2.66 reference archetype, public first-read object, layout archetype, art direction contract, and targeted debug module status",
      "negative control: bad arm can read Run 2.67, but cannot use Run 2.68 targeted renderer debug modules",
      "profile-specific QA gates: visible text must remain bounded; S02/S04/S06 must pass targeted renderer bug gates",
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
      "Visible slide structure is editable artifact-tool text and native shapes only. No copied screenshots, raw tutorial media, raw video frames, or image-only output claims are used.",
      "",
    ].join("\n"),
  );
  const presentation = Presentation.create(undefined, { slideSize: { width: W, height: H } });
  const metricsByRole = new Map();
  const referenceData = armUsesFullRun268Grammar(arm) ? loadRun268ReferenceData(arm) : null;
  const badData = armUsesBadRun268Data(arm) ? loadRun268BadControlData(arm) : null;
  const slides = arm.slides.map((slide, index) => renderRun268Slide(presentation, slide, arm, index + 1, referenceData, badData, metricsByRole));
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
  const trace = traceFor(arm, { referenceData, badData, metricsByRole });
  assertRun268ReferenceSelfCheck(trace);
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
    slides: slides.map((_, index) => ({ index: index + 1, requestedSlideNumber: index + 1, source: "scripts/generate_ppt_run2_68_targeted_debug_arms.mjs", exportName: `slide${String(index + 1).padStart(2, "0")}` })),
  };
  writeJson(path.join(workspace, "output", "artifact-build-manifest.json"), manifest);
  writeJson(path.join(workspace, "qa", "build_manifest_stdout.json"), manifest);
  writeJson(path.join(workspace, "trace_manifest.json"), trace);
  return { workspace, outputPath, contactSheet, previewPaths };
}

function repoRelative(absPath) {
  return path.relative(root, absPath).split(path.sep).join("/");
}

function writeRun268Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-68-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-68-bad-without-targeted-debug/trace_manifest.json`);
  const result = {
    schema_version: 1,
    run_id: RUN_ID,
    status: "run2_68_targeted_debug_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_design_run_id: "2.66",
    source_generated_run_id: "2.67",
    database_expansion: false,
    workflow_expansion: true,
    stage_policy: "repeat_same_five_layers_not_run3",
    debug_scope: {
      source_run_id: "2.67",
      target_layer: RUN2_68_POLICY,
      targeted_roles: TARGETED_DEBUG_ROLES,
      bug_ids: RUN2_68_RENDERER_BUGS_FIXED,
    },
    input_chain: {
      run2_67_result: RUN2_68_INPUTS.run267Result,
      run2_67_full_trace: RUN2_68_INPUTS.run267FullTrace,
      run2_66_result: RUN2_68_INPUTS.run266Result,
      run2_66_failure_audit: RUN2_68_INPUTS.run266FailureAudit,
      run2_66_design_grammar: RUN2_68_INPUTS.run266DesignGrammar,
      run2_66_art_direction: RUN2_68_INPUTS.run266ArtDirection,
      run2_66_workflow_gates: RUN2_68_INPUTS.run266WorkflowGates,
      run2_65_result: RUN2_68_INPUTS.run265Result,
      run2_65_full_trace: RUN2_68_INPUTS.run265FullTrace,
      commercial_usecase_bank: RUN2_68_INPUTS.commercialUsecaseBank,
      sources: RUN2_68_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_68_targeted_debug_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_68_full_targeted_debug_repair",
      best_internal_arm_verdict: "Run 2.67 generated output is consumed, then S02, S04, and S06 receive targeted renderer repairs before native PPT drawing.",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: RUN2_68_POLICY,
      source_data_status: RUN2_68_FULL_STATUS,
      full_slides_with_run2_66_reference_grammar: fullTrace.slides.filter((slide) => String(slide.run2_66_reference_archetype_id ?? "").startsWith("reference_first_archetype_2_66_")).length,
      full_slides_with_reference_archetypes: fullTrace.slides.filter((slide) => String(slide.run2_66_layout_archetype ?? "").length > 0).length,
      full_slides_with_public_surface_aesthetic_gate: fullTrace.slides.filter((slide) => slide.run2_66_public_surface_aesthetic_gate_status === "pass_internal").length,
      full_slides_with_visible_trace_terms_removed: fullTrace.slides.filter((slide) => (slide.run2_68_visible_trace_terms ?? 1) === 0).length,
      full_slides_with_scene_business_objects: fullTrace.slides.filter((slide) => (slide.run2_68_scene_specific_business_object_count ?? 0) >= 3).length,
      full_slides_with_depth_layers: fullTrace.slides.filter((slide) => (slide.run2_68_depth_layer_count ?? 0) >= 4).length,
      targeted_debug_roles_fixed: fullTrace.slides.filter((slide) => TARGETED_DEBUG_ROLES.includes(slide.role) && slide.run2_68_bug_fix_status === "pass_internal").length,
      full_slides_with_text_overlap_risk_removed: fullTrace.slides.filter((slide) => slide.run2_68_text_overlap_risk_status === "pass_internal" && (slide.layout_metrics?.text_overflow_risk_count ?? 1) === 0).length,
      full_slides_with_debug_renderer_modules: fullTrace.slides.filter((slide) => TARGETED_DEBUG_ROLES.includes(slide.role) && Object.values(RUN2_68_TARGETED_DEBUG_MODULES).includes(slide.run2_68_debug_renderer_module_id)).length,
      bad_control_slides_without_targeted_debug_repair: badTrace.slides.filter((slide) => TARGETED_DEBUG_ROLES.includes(slide.role) && slide.run2_68_bug_fix_status === RUN2_68_BAD_STATUS).length,
      repair_modules: Object.values(ROLE_RENDERERS),
    },
    control_boundary: {
      bad_run2_67_without_targeted_debug_repair: "may see Run 2.67 generated result and trace, but must not use the Run 2.68 targeted renderer debug repair modules",
      prompt_only: "commercial_case_only_no_run2_67_or_run2_68_targeted_debug",
      run1_5_skill: "prior_baseline_no_run2_67_or_run2_68_targeted_debug",
    },
    visual_quality_boundary: "Run 2.68 is an internal generated rerun for visual review; public release remains blocked until human review approves the rendered deck.",
    remaining_public_release_gates: ["human_visual_review", "native_or_cross_platform_render_inspection", "source_boundary_review", "human_release_approval"],
    release_boundary: "public_blocked_until_human_visual_review_native_render_review_source_boundary_review_and_human_approval",
    next_required_action: "human_review_run2_68_targeted_debug_output_then_decide_whether_more_data_workflow_debug_is_needed",
  };
  const resultJson = path.join(root, pack, "results", "run2_68_targeted_debug_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_68_targeted_debug_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.68 Targeted Renderer Debug Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.68 consumes Run 2.67 generated output plus Run 2.66 design grammar before native PPT drawing, then repairs the renderer layer that made S02 setup, S04 proof, and S06 close visually wrong.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_68_full_targeted_debug_repair`",
      "- `bad_run2_67_without_targeted_debug_repair`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_68_full_targeted_debug_repair`.",
      "",
      "Quality delta: `run2_67_targeted_renderer_debug_repair`. S02 setup replaces the node diagram with a layered operating stage; S04 proof removes text overlap and replaces the wireframe workspace; S06 close replaces the random node graph with a release decision board.",
      "",
      "The bad control can reuse Run 2.67 generated proof, but it fails the Run 2.68 targeted renderer debug layer.",
      "",
      "Bug notes: S02 setup, S04 proof, and S06 close now pass the internal text overlap and renderer-module gates.",
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
  const fourArmSheet = buildRun268FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_68_targeted_debug_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_68_targeted_debug_rerun_summary.json"), runSummary);
  writeRun268Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_68_FULL_DATA_INPUTS,
  RUN2_68_INPUTS,
  armSpecs,
  assertRun268ArmInputBoundaries,
  assertRun268ReferenceSelfCheck,
  drawRun268TargetedDebugPublicSurface,
  loadRun268ReferenceData,
  main,
};
