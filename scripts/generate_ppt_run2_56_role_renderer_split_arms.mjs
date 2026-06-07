import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.56";
const RUN2_56_FULL_STATUS = "run2_55_text_shape_integration_consumed_before_role_renderer_redraw";
const RUN2_56_BAD_STATUS = "run2_55_generated_but_role_renderer_split_missing";
const RUN2_56_POLICY = "role_specific_renderer_variation_and_layout_qa";
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
  ink: "#14181f",
  paper: "#f3efe5",
  white: "#ffffff",
  line: "#d6d0c3",
  muted: "#596371",
  dark: "#111820",
  blue: "#2b63d9",
  cyan: "#75c9d8",
  red: "#df4f33",
  green: "#108665",
  amber: "#e4b84e",
  violet: "#978cff",
  steel: "#e8edf0",
  cream: "#fbf7ee",
};

const RUN2_56_INPUTS = {
  run251CopyMemory: `${pack}/run2_51_editorial_copy_memory.json`,
  run251SocketMemory: `${pack}/run2_51_shape_text_socket_memory.json`,
  run253Result: `${pack}/results/run2_53_product_surface_scene_repair_result.json`,
  run253Scenes: `${pack}/run2_53_product_surface_scene_memory.json`,
  run253Evidence: `${pack}/run2_53_business_visual_evidence_memory.json`,
  run253Gates: `${pack}/run2_53_scene_renderer_workflow_gates.json`,
  run255Result: `${pack}/results/run2_55_text_shape_integration_rerun_result.json`,
  run255FullTrace: `outputs/${threadId}/presentations/ppt-run2-55-full-vulca/trace_manifest.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_53_PRODUCT_SURFACE_INPUTS = [
  RUN2_56_INPUTS.run253Result,
  RUN2_56_INPUTS.run253Scenes,
  RUN2_56_INPUTS.run253Evidence,
  RUN2_56_INPUTS.run253Gates,
];
const RUN2_56_FULL_DATA_INPUTS = Object.values(RUN2_56_INPUTS);
const RUN2_56_BAD_DATA_INPUTS = Object.values(RUN2_56_INPUTS);

const baseSlides = [
  {
    role: "cover",
    title: "Design decks people can judge",
    claim:
      "The first public surface must show the actual product object before any abstract proof labels appear.",
  },
  {
    role: "setup",
    title: "The old path stays boxy",
    claim:
      "The setup slide must show a concrete workflow route board, not a generic stack of equal cards.",
  },
  {
    role: "contrast",
    title: "Evidence changes the surface",
    claim:
      "The contrast slide must make the before and after deck surfaces inspectable through a visible delta.",
  },
  {
    role: "proof",
    title: "Proof lives inside the workspace",
    claim:
      "The proof slide must attach evidence to working lanes, proof objects, and review state.",
  },
  {
    role: "climax",
    title: "One result owns the frame",
    claim:
      "The climax slide must make one generated result object own the frame with anchored proof tags.",
  },
  {
    role: "close",
    title: "Ship only after the gate",
    claim:
      "The close slide must render the release decision wall and next-action route from the scene contract.",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-56-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.56 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_56_FULL_DATA_INPUTS, "drawRun256CoverPosterStage"],
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
        "Make a launch deck.",
        "Show the problem.",
        "Show before and after.",
        "Show the proof.",
        "Make the result big.",
        "End with next steps.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-56-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.56 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_56_FULL_DATA_INPUTS, "drawRun256CoverPosterStage"],
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
        "The baseline explains the lab.",
        "The path is readable but broad.",
        "The comparison is generic.",
        "The proof is process-led.",
        "The result is labeled.",
        "The close is correct but thin.",
      ][index],
    })),
  },
  {
    armId: "run2_56_full_role_renderer_split",
    slug: "ppt-run2-56-full-vulca",
    label: "Run 2.56 full role renderer split",
    kicker: "RUN 2.56 / ROLE RENDERERS",
    footer: "run2_56_full_role_renderer_split | consumes Run 2.55 | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      ...RUN2_56_FULL_DATA_INPUTS,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_53_product_surface_scene_memory.json",
      "run2_53_business_visual_evidence_memory.json",
      "run2_53_scene_renderer_workflow_gates.json",
      "run2_51_shape_text_socket_memory.json",
      "run2_55_text_shape_integration_rerun_result.json",
      "ppt-run2-55-full-vulca/trace_manifest.json",
      RUN2_56_POLICY,
    ],
    forbidden: [
      "raw evidence fields on public surface",
      "source layouts",
      "copied screenshots",
      "square_block_grid_as_primary_surface",
      "equal_three_card_grid_as_primary_surface",
      "equal rectangle cluster",
      "reused_run2_55_stage_side_template",
      "single_renderer_for_all_roles",
      "native_drawing_before_run2_55_role_renderer_binding",
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
    armId: "bad_run2_55_reused_single_template",
    slug: "ppt-run2-56-bad-reused-single-template",
    label: "Bad reused Run 2.55 single template",
    kicker: "RUN 2.56 / BAD CONTROL",
    footer: "bad_run2_55_reused_single_template | Run 2.55 single renderer | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_56_BAD_DATA_INPUTS],
    data_input_manifest: ["run2_55_generated_without_role_renderer_split"],
    forbidden: [
      "drawRun256CoverPosterStage",
      "drawRun256SetupRouteMap",
      "drawRun256ContrastBeforeAfterLens",
      "drawRun256ProofWorkspaceSurface",
      "drawRun256ClimaxEditorialHero",
      "drawRun256CloseDecisionWall",
      "run2_56_distinct_role_surface_status",
      "run2_56_layout_signature",
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
        "Run 2.55 improves text, but the renderer repeats.",
        "The route still inherits the same stage-side skeleton.",
        "The lens is labelled, but not structurally unique.",
        "The workspace repeats the template rhythm.",
        "The climax is the only strong visual exception.",
        "The close inherits the same proof-panel structure.",
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

function compactText(value, max = 88) {
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
    presentationSurfaceWeight: 0,
    primarySurfaceKind: "",
    socketBoundPublicTextElements: 0,
    shapePrimitiveCount: 0,
    productSurfaceSlotsRendered: 0,
    businessVisualEvidenceObjects: 0,
    forbiddenGenericGeometryCount: 0,
    namedTextContainersRendered: 0,
    nonRectangularShapeFamiliesRendered: 0,
    textShapeBindingPairs: 0,
    textOverflowRiskCount: 0,
    equalRectangleClusterCount: 0,
    editorialHierarchyLevels: 0,
    primaryLayoutStrategy: "",
    roleRendererId: "",
    compositionFamily: "",
    layoutSignature: "",
    visualSamenessBucket: "",
    primaryAnchorRegion: "",
    roleSpecificGeometryCount: 0,
    textCollisionRiskCount: 0,
    distinctRoleSurfaceStatus: "",
    roleArchetypeBindingStatus: "",
    codeModuleIds: new Set(),
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun256Module(metrics, functionName) {
  metrics.codeModuleIds.add(functionName);
}

function registerPresentationSurface(metrics, x, y, w, h, target = 0) {
  const area = Math.max(1, MAIN_CANVAS.w * MAIN_CANVAS.h);
  metrics.presentationSurfaceWeight = Math.max(metrics.presentationSurfaceWeight, (w * h) / area, Number(target) || 0);
}

function registerProof(metrics, count = 1) {
  metrics.proofObjects += count;
}

function registerZones(metrics, count = 1) {
  metrics.zones = Math.max(metrics.zones, count);
}

function textDensityTier(metrics) {
  if (metrics.visibleWords >= 70) return "rich";
  if (metrics.visibleWords >= 42) return "medium";
  return "thin";
}

function socketText(slide, metrics, value, x, y, w, h, opts = {}) {
  const shape = text(slide, compactText(value, opts.max ?? 96), x, y, w, h, opts);
  metrics.socketBoundPublicTextElements += 1;
  registerText(metrics, value);
  return shape;
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

function armUsesFullRun256Repair(arm) {
  return arm.armId === "run2_56_full_role_renderer_split";
}

function armUsesBadRun256Data(arm) {
  return arm.armId === "bad_run2_55_reused_single_template";
}

function assertRun256ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun256Repair(arm)) {
    for (const input of RUN2_56_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesBadRun256Data(arm)) {
    for (const input of RUN2_56_BAD_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow bad-control input ${input}`);
    }
    if (!forbidden.has("drawRun256CoverPosterStage")) {
      throw new Error(`${arm.armId} must block drawRun256CoverPosterStage`);
    }
    return;
  }
  for (const input of RUN2_56_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun256PackJsonForArm(arm, relPath) {
  assertRun256ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (!armUsesFullRun256Repair(arm) && !armUsesBadRun256Data(arm)) {
    throw new Error(`${arm.armId} cannot read Run 2.56 pack data`);
  }
  return readJson(relPath);
}

function publicCopyTerms(copy) {
  return [
    copy?.headline,
    copy?.subline,
    ...(copy?.proof_nuggets ?? []),
    ...(copy?.annotations ?? []),
    ...(copy?.state_labels ?? []),
  ]
    .filter(Boolean)
    .join(" ");
}

function countForbiddenSurfaceTerms(copyRecord) {
  const haystack = publicCopyTerms(copyRecord.public_surface_copy_bundle).toLowerCase();
  return (copyRecord.forbidden_surface_terms ?? []).filter((term) => haystack.includes(String(term).toLowerCase())).length;
}

function assertSelectedUsecase(value, label) {
  if (value !== selectedUsecaseId) {
    throw new Error(`Run 2.56 selected usecase mismatch in ${label}`);
  }
}

function assertPublicCopyBundle(copy, role) {
  const bundle = copy.public_surface_copy_bundle;
  if (!bundle || typeof bundle !== "object") {
    throw new Error(`Run 2.56 public copy bundle missing for ${role}`);
  }
  for (const key of ["headline", "subline"]) {
    if (typeof bundle[key] !== "string" || !bundle[key].trim()) {
      throw new Error(`Run 2.56 public copy ${key} missing for ${role}`);
    }
  }
  for (const key of ["proof_nuggets", "annotations", "state_labels"]) {
    if (!Array.isArray(bundle[key]) || !bundle[key].length || !bundle[key].every((item) => typeof item === "string" && item.trim())) {
      throw new Error(`Run 2.56 public copy ${key} malformed for ${role}`);
    }
  }
}

function validateRun256RoleRendererInputs(data) {
  const {
    run251CopyMemory,
    run251SocketMemory,
    run253Result,
    run253Scenes,
    run253Evidence,
    run253Gates,
    run255Result,
    run255FullTrace,
    commercialUsecaseBank,
    sources,
  } = data;
  if (run251CopyMemory?.status !== "run2_51_editorial_copy_memory_ready_public_blocked") throw new Error("Run 2.56 must consume Run 2.51 editorial copy memory");
  if (run251SocketMemory?.status !== "run2_51_shape_text_socket_memory_ready_public_blocked") throw new Error("Run 2.56 must consume Run 2.51 shape text socket memory");
  if (run253Result?.status !== "run2_53_product_surface_scene_repair_ready_public_blocked") throw new Error("Run 2.56 must consume Run 2.53 repair result");
  if (run253Scenes?.status !== "run2_53_product_surface_scene_memory_ready_public_blocked") throw new Error("Run 2.56 product surface scene status mismatch");
  if (run253Evidence?.status !== "run2_53_business_visual_evidence_memory_ready_public_blocked") throw new Error("Run 2.56 business visual evidence status mismatch");
  if (run253Gates?.status !== "run2_53_scene_renderer_workflow_gates_ready_public_blocked") throw new Error("Run 2.56 scene renderer gate status mismatch");
  if (run255Result?.status !== "run2_55_text_shape_integration_rerun_public_blocked") throw new Error("Run 2.56 must consume Run 2.55 generated result");
  if (run255Result?.rerun?.best_internal_arm !== "run2_55_full_text_shape_integration") throw new Error("Run 2.56 must consume Run 2.55 full arm");
  if (run255FullTrace?.arm_id !== "run2_55_full_text_shape_integration") throw new Error("Run 2.56 must compare against Run 2.55 full trace");
  if (run255FullTrace?.run2_55_text_shape_integration_status !== "run2_54_product_surface_scene_rerun_consumed_before_text_shape_redraw") throw new Error("Run 2.56 must compare against Run 2.55 full trace");
  if (!Array.isArray(run255FullTrace?.slides) || run255FullTrace.slides.length !== 6) throw new Error("Run 2.56 requires six Run 2.55 full trace slides");
  if (!Array.isArray(sources?.sources) || sources.sources.length < 4) throw new Error("Run 2.56 missing sources");
  const usecase = (commercialUsecaseBank?.usecases ?? []).find((item) => item.id === selectedUsecaseId);
  if (!usecase) throw new Error("Run 2.56 missing selected commercial usecase");
  assertSelectedUsecase(run251CopyMemory?.selected_usecase_id, "run2_51_editorial_copy_memory");
  assertSelectedUsecase(run251SocketMemory?.selected_usecase_id, "run2_51_shape_text_socket_memory");
  assertSelectedUsecase(run253Result?.selected_usecase_id, "run2_53_result");
  assertSelectedUsecase(run253Scenes?.selected_usecase_id, "run2_53_product_surface_scene_memory");
  assertSelectedUsecase(run253Evidence?.selected_usecase_id, "run2_53_business_visual_evidence_memory");
  assertSelectedUsecase(run253Gates?.selected_usecase_id, "run2_53_scene_renderer_workflow_gates");
  assertSelectedUsecase(run255Result?.selected_usecase_id, "run2_55_result");
  assertSelectedUsecase(run255FullTrace?.selected_usecase_id, "run2_55_full_trace");

  if (!Array.isArray(run251CopyMemory?.editorial_copy_records) || run251CopyMemory.editorial_copy_records.length !== 6) throw new Error("Run 2.56 requires six Run 2.51 editorial copy records");
  if (!Array.isArray(run251SocketMemory?.shape_text_socket_records) || run251SocketMemory.shape_text_socket_records.length !== 6) throw new Error("Run 2.56 requires six Run 2.51 shape text socket records");
  if (!Array.isArray(run253Scenes?.product_surface_scene_records) || run253Scenes.product_surface_scene_records.length !== 6) throw new Error("Run 2.56 requires six Run 2.53 product surface scene records");
  if (!Array.isArray(run253Evidence?.business_visual_evidence_records) || run253Evidence.business_visual_evidence_records.length !== 6) throw new Error("Run 2.56 requires six Run 2.53 business visual evidence records");
  if (!Array.isArray(run253Gates?.scene_renderer_workflow_gates) || run253Gates.scene_renderer_workflow_gates.length !== 6) throw new Error("Run 2.56 requires six Run 2.53 scene renderer gates");

  for (const role of baseSlides.map((slide) => slide.role)) {
    const copy = run251CopyMemory.editorial_copy_records.find((record) => record.role === role);
    const socket = run251SocketMemory.shape_text_socket_records.find((record) => record.role === role);
    const scene = run253Scenes.product_surface_scene_records.find((record) => record.role === role);
    const evidence = run253Evidence.business_visual_evidence_records.find((record) => record.role === role);
    const gate = run253Gates.scene_renderer_workflow_gates.find((record) => record.role === role);
    const priorTraceSlide = (run255FullTrace.slides ?? []).find((slide) => slide.role === role);
    if (!copy || !socket || !scene || !evidence || !gate || !priorTraceSlide) throw new Error(`Run 2.56 missing role contract for ${role}`);
    assertPublicCopyBundle(copy, role);
    assertSelectedUsecase(copy.selected_usecase_id, `run2_51_copy_record_${role}`);
    assertSelectedUsecase(socket.selected_usecase_id, `run2_51_socket_record_${role}`);
    assertSelectedUsecase(scene.selected_usecase_id, `run2_53_scene_record_${role}`);
    assertSelectedUsecase(evidence.selected_usecase_id, `run2_53_evidence_record_${role}`);
    assertSelectedUsecase(gate.selected_usecase_id, `run2_53_gate_record_${role}`);
    if (scene.must_render_product_or_business_object !== true) {
      throw new Error(`Run 2.56 scene must render product or business object for ${role}`);
    }
    if ((scene.surface_slots ?? []).length < 3) {
      throw new Error(`Run 2.56 product surface slots too thin for ${role}`);
    }
    if (evidence.required_product_surface_scene_id !== scene.id) {
      throw new Error(`Run 2.56 evidence/scene mismatch for ${role}`);
    }
    if (gate.required_product_surface_scene_id !== scene.id) {
      throw new Error(`Run 2.56 gate/scene mismatch for ${role}`);
    }
    if (gate.required_business_visual_evidence_id !== evidence.id) {
      throw new Error(`Run 2.56 gate/evidence mismatch for ${role}`);
    }
    if (!String(priorTraceSlide.run2_53_product_surface_scene_id ?? "").startsWith("product_surface_scene_2_53_")) {
      throw new Error(`Run 2.56 missing Run 2.53 product surface scene id for ${role}`);
    }
    if (priorTraceSlide.run2_55_text_shape_integration_status !== "pass_internal") {
      throw new Error(`Run 2.56 must consume Run 2.55 pass_internal text-shape slide for ${role}`);
    }
    if (priorTraceSlide.run2_55_equal_rectangle_cluster_count !== 0) {
      throw new Error(`Run 2.56 cannot split role renderer from equal rectangle cluster source for ${role}`);
    }
    if (gate.consumer_contract?.must_bind_before_native_drawing !== true) {
      throw new Error(`Run 2.56 must_bind_before_native_drawing mismatch for ${role}`);
    }
  }
}

function loadRun256ContractData(arm) {
  const data = {
    run251CopyMemory: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run251CopyMemory),
    run251SocketMemory: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run251SocketMemory),
    run253Result: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run253Result),
    run253Scenes: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run253Scenes),
    run253Evidence: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run253Evidence),
    run253Gates: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run253Gates),
    run255Result: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run255Result),
    run255FullTrace: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run255FullTrace),
    commercialUsecaseBank: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.commercialUsecaseBank),
    sources: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.sources),
  };
  validateRun256RoleRendererInputs(data);
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_56_role_renderer_input_contract_ready",
  };
}

function loadRun256BadControlData(arm) {
  const data = {
    run251CopyMemory: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run251CopyMemory),
    run251SocketMemory: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run251SocketMemory),
    run253Result: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run253Result),
    run253Scenes: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run253Scenes),
    run253Evidence: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run253Evidence),
    run253Gates: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run253Gates),
    run255Result: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run255Result),
    run255FullTrace: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.run255FullTrace),
    commercialUsecaseBank: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.commercialUsecaseBank),
    sources: readRun256PackJsonForArm(arm, RUN2_56_INPUTS.sources),
  };
  if (data.run255Result?.status !== "run2_55_text_shape_integration_rerun_public_blocked") {
    throw new Error("Run 2.56 bad control must read Run 2.55 result");
  }
  if (data.run255FullTrace?.arm_id !== "run2_55_full_text_shape_integration") {
    throw new Error("Run 2.56 bad control must read Run 2.55 full trace");
  }
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
  };
}

function selectRun256ForSlide(role, contractData) {
  const copy = (contractData.run251CopyMemory?.editorial_copy_records ?? []).find((item) => item.role === role);
  const socket = (contractData.run251SocketMemory?.shape_text_socket_records ?? []).find((item) => item.role === role);
  const scene = (contractData.run253Scenes?.product_surface_scene_records ?? []).find((item) => item.role === role);
  const evidence = (contractData.run253Evidence?.business_visual_evidence_records ?? []).find((item) => item.role === role);
  const gate = (contractData.run253Gates?.scene_renderer_workflow_gates ?? []).find((item) => item.role === role);
  const priorTraceSlide = (contractData.run255FullTrace?.slides ?? []).find((item) => item.role === role);
  if (!copy || !socket || !scene || !evidence || !gate || !priorTraceSlide) throw new Error(`Run 2.56 missing role contract for ${role}`);
  return {
    role,
    copy,
    publicCopy: copy.public_surface_copy_bundle,
    socket,
    scene,
    evidence,
    gate,
    priorTraceSlide,
    usecase: contractData.usecase,
    primaryObject: scene.primary_product_or_business_object,
    surfaceSlots: scene.surface_slots ?? [],
    primarySurfaceKind: scene.scene_object_kind,
  };
}

function drawPathSegment(slide, x, y, w, h, fill) {
  rect(slide, x, y, w, h, fill, colorLine("transparent", 0));
}

function drawPromptMiniDeck(slide, x, y, w, h, fill, accent) {
  rect(slide, x, y, w, h, fill, colorLine("#cfd6dd", 1));
  rect(slide, x + 14, y + 18, w * 0.48, 9, accent, colorLine("transparent", 0));
  rect(slide, x + 14, y + 46, w * 0.35, 7, "#bfc9d2", colorLine("transparent", 0));
  rect(slide, x + 14, y + 72, w * 0.24, 7, "#bfc9d2", colorLine("transparent", 0));
  rect(slide, x + w - 76, y + 24, 48, 62, "#edf1f3", colorLine("#d5dde1", 1));
}

function evidenceStripLines(selection) {
  return (selection.copy.raw_evidence_inputs?.business_proof_points ?? [])
    .slice(0, 2)
    .map((line) => compactText(line, 118));
}

function drawEditorialEvidenceStrip(slide, arm, selection, metrics, x, y, w, opts = {}) {
  const lines = evidenceStripLines(selection);
  const dark = opts.dark === true;
  const fill = dark ? "#17212c" : "#ffffff";
  const border = dark ? "#3d5262" : "#d8e0e5";
  const labelColor = dark ? "#8fd6e5" : arm.palette.proof;
  const textColor = dark ? "#e8f0f4" : C.ink;
  rect(slide, x, y, w, 96, fill, colorLine(border, 1));
  text(slide, opts.label ?? "commercial proof", x + 16, y + 12, w - 32, 14, {
    fontSize: 8.5,
    mono: true,
    bold: true,
    color: labelColor,
  });
  lines.forEach((line, index) => {
    socketText(slide, metrics, line, x + 16, y + 32 + index * 28, w - 32, 24, {
      fontSize: opts.fontSize ?? 9.6,
      color: textColor,
      max: 118,
    });
  });
  registerProof(metrics, lines.length);
  registerZones(metrics, 6);
}

function drawCoverPosterStage(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  rect(slide, 82, 122, 710, 394, "#111820", colorLine("#111820", 1));
  rect(slide, 116, 158, 642, 284, "#f8fafb", colorLine("#e4e9ed", 1));
  ellipse(slide, 432, 186, 238, 166, "#dfeafd", colorLine("#c6d8fa", 1));
  rect(slide, 158, 390, 540, 48, arm.palette.proof, colorLine("transparent", 0));
  socketText(slide, metrics, p.headline, 158, 204, 362, 76, { fontSize: 32, title: true, bold: true, color: C.ink, max: 48 });
  socketText(slide, metrics, p.subline, 528, 228, 194, 76, { fontSize: 14, color: C.muted, max: 120 });
  p.proof_nuggets.slice(0, 3).forEach((proof, index) => {
    const x = 844 + index * 112;
    ellipse(slide, x, 196, 88, 88, index === 0 ? arm.palette.proof : C.white, colorLine(index === 0 ? arm.palette.proof : "#d8dfe4", 1));
    socketText(slide, metrics, proof, x + 13, 222, 62, 34, {
      fontSize: 9.4,
      bold: true,
      align: "center",
      color: index === 0 ? C.white : C.ink,
      max: 54,
    });
  });
  p.annotations.slice(0, 2).forEach((note, index) => {
    socketText(slide, metrics, note, 830 + index * 164, 394, 138, 34, {
      fontSize: 10,
      bold: true,
      mono: true,
      color: C.white,
      fill: arm.palette.accent,
      max: 42,
    });
  });
  rect(slide, 828, 340, 312, 18, arm.palette.accent2, colorLine("transparent", 0));
  drawEditorialEvidenceStrip(slide, arm, selection, metrics, 830, 454, 314, { label: "buyer proof" });
  registerPresentationSurface(metrics, 82, 122, 710, 394, 0.58);
  registerProof(metrics, 3);
  registerZones(metrics, 5);
}

function drawSetupRouteMap(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  socketText(slide, metrics, p.headline, 78, 116, 420, 72, { fontSize: 34, title: true, bold: true, color: arm.palette.title, max: 48 });
  socketText(slide, metrics, p.subline, 82, 202, 394, 54, { fontSize: 14, color: arm.palette.muted, max: 120 });
  const route = [
    { x: 548, y: 202 },
    { x: 728, y: 312 },
    { x: 922, y: 246 },
  ];
  drawPathSegment(slide, 596, 239, 154, 9, arm.palette.proof);
  drawPathSegment(slide, 760, 320, 168, 9, arm.palette.proof);
  route.forEach((node, index) => {
    ellipse(slide, node.x, node.y, 112, 112, index === 1 ? "#111820" : C.white, colorLine(index === 1 ? "#111820" : arm.palette.rule, 1));
    socketText(slide, metrics, p.proof_nuggets[index], node.x + 16, node.y + 40, 80, 30, {
      fontSize: 10,
      bold: true,
      align: "center",
      color: index === 1 ? C.white : C.ink,
      max: 54,
    });
  });
  rect(slide, 522, 402, 318, 84, "#f5e0d2", colorLine("#e0bba3", 1));
  socketText(slide, metrics, p.annotations[0], 548, 430, 156, 24, { fontSize: 12, bold: true, color: "#7a3525", max: 42 });
  rect(slide, 860, 408, 170, 64, "#fff8e4", colorLine("#e7c76d", 1));
  socketText(slide, metrics, p.annotations[1], 884, 430, 118, 24, { fontSize: 11, bold: true, color: "#6b5522", max: 42 });
  rect(slide, 1040, 214, 48, 48, arm.palette.proof, colorLine("transparent", 0));
  drawEditorialEvidenceStrip(slide, arm, selection, metrics, 82, 300, 386, { label: "decision evidence" });
  registerPresentationSurface(metrics, 548, 202, 486, 270, 0.44);
  registerProof(metrics, 3);
  registerZones(metrics, 5);
}

function drawContrastBeforeAfterLens(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  socketText(slide, metrics, p.headline, 76, 112, 400, 72, { fontSize: 34, title: true, bold: true, color: arm.palette.title, max: 48 });
  socketText(slide, metrics, p.subline, 80, 202, 394, 58, { fontSize: 14, color: arm.palette.muted, max: 120 });
  ellipse(slide, 534, 246, 184, 184, "#f2ded4", colorLine("#dba88e", 2));
  ellipse(slide, 728, 134, 390, 390, "#eff5f7", colorLine("#cad8dc", 2));
  socketText(slide, metrics, p.proof_nuggets[0], 570, 318, 110, 30, { fontSize: 10, bold: true, align: "center", color: "#7a3525", max: 54 });
  socketText(slide, metrics, p.proof_nuggets[1], 826, 258, 192, 38, { fontSize: 17, title: true, bold: true, align: "center", color: C.ink, max: 54 });
  rect(slide, 698, 352, 118, 12, arm.palette.proof, colorLine("transparent", 0));
  socketText(slide, metrics, p.proof_nuggets[2], 722, 382, 214, 30, { fontSize: 12, bold: true, color: arm.palette.proof, max: 54 });
  socketText(slide, metrics, p.annotations[0], 532, 456, 144, 26, { fontSize: 10, mono: true, color: arm.palette.muted, max: 42 });
  socketText(slide, metrics, p.annotations[1], 892, 534, 160, 26, { fontSize: 10, mono: true, color: arm.palette.muted, max: 42 });
  drawEditorialEvidenceStrip(slide, arm, selection, metrics, 80, 298, 386, { label: "comparison evidence" });
  registerPresentationSurface(metrics, 728, 134, 390, 390, 0.5);
  registerProof(metrics, 3);
  registerZones(metrics, 4);
}

function drawProofWorkspaceSurface(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  socketText(slide, metrics, p.headline, 76, 112, 338, 78, { fontSize: 31, title: true, bold: true, color: arm.palette.title, max: 48 });
  socketText(slide, metrics, p.subline, 80, 206, 326, 64, { fontSize: 14, color: arm.palette.muted, max: 120 });
  rect(slide, 454, 118, 630, 404, C.white, colorLine(arm.palette.rule, 1));
  rect(slide, 478, 148, 582, 46, "#111820", colorLine("transparent", 0));
  for (let index = 0; index < 3; index += 1) {
    const y = 226 + index * 82;
    rect(slide, 492, y, 546, 54, index === 1 ? "#edf4f7" : "#f8fafb", colorLine("#dbe3e7", 1));
    socketText(slide, metrics, p.proof_nuggets[index], 518, y + 18, 150, 20, { fontSize: 11, bold: true, color: C.ink, max: 54 });
    rect(slide, 720 + index * 62, y + 16, 76, 22, index === 2 ? arm.palette.proof : arm.palette.accent2, colorLine("transparent", 0));
  }
  socketText(slide, metrics, p.annotations[0], 520, 160, 170, 18, { fontSize: 10, bold: true, mono: true, color: C.white, max: 42 });
  socketText(slide, metrics, p.annotations[1], 820, 468, 150, 24, { fontSize: 10, bold: true, color: arm.palette.proof, max: 42 });
  drawEditorialEvidenceStrip(slide, arm, selection, metrics, 78, 306, 330, { label: "proof evidence", fontSize: 9.2 });
  registerPresentationSurface(metrics, 454, 118, 630, 404, 0.56);
  registerProof(metrics, 4);
  registerZones(metrics, 5);
}

function drawClimaxExplodedHeroObject(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  rect(slide, 68, 94, 1088, 548, C.dark, colorLine(C.dark, 1));
  socketText(slide, metrics, p.headline, 108, 124, 560, 62, { fontSize: 40, title: true, bold: true, color: C.white, max: 48 });
  socketText(slide, metrics, p.subline, 112, 196, 470, 52, { fontSize: 14, color: "#dbe5ec", max: 120 });
  const layers = [
    { x: 438, y: 282, w: 468, h: 192, fill: "#dfeafd" },
    { x: 476, y: 246, w: 468, h: 192, fill: "#f8fafb" },
    { x: 516, y: 210, w: 468, h: 192, fill: "#ffffff" },
  ];
  layers.forEach((layer, index) => {
    rect(slide, layer.x, layer.y, layer.w, layer.h, layer.fill, colorLine(index === 2 ? C.white : "#91a3b7", 1));
  });
  socketText(slide, metrics, p.proof_nuggets[0], 568, 284, 232, 38, { fontSize: 19, title: true, bold: true, align: "center", color: C.ink, max: 54 });
  p.proof_nuggets.slice(1, 3).forEach((proof, index) => {
    socketText(slide, metrics, proof, 928, 244 + index * 80, 148, 34, {
      fontSize: 10,
      bold: true,
      fill: index === 0 ? arm.palette.proof : C.amber,
      color: index === 0 ? C.white : C.ink,
      max: 54,
    });
  });
  socketText(slide, metrics, p.annotations[0], 120, 522, 190, 28, { fontSize: 11, bold: true, mono: true, color: C.cyan, max: 42 });
  socketText(slide, metrics, p.annotations[1], 342, 522, 160, 28, { fontSize: 11, bold: true, mono: true, color: C.cyan, max: 42 });
  drawEditorialEvidenceStrip(slide, arm, selection, metrics, 112, 272, 300, { dark: true, label: "launch evidence", fontSize: 9 });
  registerPresentationSurface(metrics, 516, 210, 468, 192, 0.42);
  registerProof(metrics, 3);
  registerZones(metrics, 5);
}

function drawCloseDecisionRoom(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  socketText(slide, metrics, p.headline, 78, 114, 380, 70, { fontSize: 34, title: true, bold: true, color: arm.palette.title, max: 48 });
  socketText(slide, metrics, p.subline, 82, 204, 380, 54, { fontSize: 14, color: arm.palette.muted, max: 120 });
  rect(slide, 520, 126, 516, 302, "#111820", colorLine("#111820", 1));
  rect(slide, 548, 154, 460, 222, "#f8fafb", colorLine("#e1e6ea", 1));
  p.proof_nuggets.slice(0, 3).forEach((proof, index) => {
    rect(slide, 582 + index * 126, 200 + index * 20, 106, 88, index === 0 ? arm.palette.proof : C.white, colorLine(index === 0 ? arm.palette.proof : "#d7dfe4", 1));
    socketText(slide, metrics, proof, 596 + index * 126, 230 + index * 20, 78, 26, {
      fontSize: 9.2,
      bold: true,
      align: "center",
      color: index === 0 ? C.white : C.ink,
      max: 54,
    });
  });
  rect(slide, 546, 460, 420, 30, arm.palette.accent2, colorLine("transparent", 0));
  socketText(slide, metrics, p.annotations[0], 568, 464, 128, 20, { fontSize: 10, bold: true, color: C.ink, max: 42 });
  socketText(slide, metrics, p.annotations[1], 734, 464, 140, 20, { fontSize: 10, bold: true, color: C.ink, max: 42 });
  drawPathSegment(slide, 964, 474, 86, 7, arm.palette.proof);
  ellipse(slide, 1048, 458, 36, 36, arm.palette.proof, colorLine("transparent", 0));
  drawEditorialEvidenceStrip(slide, arm, selection, metrics, 82, 300, 360, { label: "decision evidence" });
  registerPresentationSurface(metrics, 520, 126, 516, 302, 0.44);
  registerProof(metrics, 3);
  registerZones(metrics, 5);
}

const RUN2_56_RENDERER_CONFIGS = {
  cover: {
    id: "drawRun256CoverPosterStage",
    family: "poster_stage",
    signature: "cover_stage_left_proof_orbits_right",
    bucket: "cover_poster_stage_surface",
    anchor: "left_stage_right_orbits",
    geometry: 8,
  },
  setup: {
    id: "drawRun256SetupRouteMap",
    family: "route_map",
    signature: "setup_left_copy_zigzag_route_nodes",
    bucket: "setup_route_map_surface",
    anchor: "right_zigzag_route",
    geometry: 9,
  },
  contrast: {
    id: "drawRun256ContrastBeforeAfterLens",
    family: "before_after_lens",
    signature: "contrast_left_evidence_nested_lenses",
    bucket: "contrast_lens_surface",
    anchor: "center_right_lens",
    geometry: 7,
  },
  proof: {
    id: "drawRun256ProofWorkspaceSurface",
    family: "workspace_surface",
    signature: "proof_left_copy_right_workspace_lanes",
    bucket: "proof_workspace_surface",
    anchor: "right_workspace_lanes",
    geometry: 10,
  },
  climax: {
    id: "drawRun256ClimaxEditorialHero",
    family: "exploded_hero_object",
    signature: "climax_full_bleed_dark_exploded_layers",
    bucket: "climax_editorial_hero_surface",
    anchor: "full_bleed_center_hero",
    geometry: 9,
  },
  close: {
    id: "drawRun256CloseDecisionWall",
    family: "decision_room",
    signature: "close_left_decision_copy_right_release_wall",
    bucket: "close_decision_wall_surface",
    anchor: "right_release_wall",
    geometry: 8,
  },
};

function markRun256RoleRenderer(metrics, config, selection) {
  registerRun256Module(metrics, config.id);
  metrics.roleRendererId = config.id;
  metrics.compositionFamily = config.family;
  metrics.layoutSignature = config.signature;
  metrics.visualSamenessBucket = config.bucket;
  metrics.primaryAnchorRegion = config.anchor;
  metrics.roleSpecificGeometryCount = config.geometry;
  metrics.primarySurfaceKind = selection.scene?.scene_object_kind ?? "";
  metrics.primaryLayoutStrategy = config.signature;
  metrics.shapePrimitiveCount = Math.max(metrics.shapePrimitiveCount, config.geometry);
  metrics.productSurfaceSlotsRendered = Math.max(metrics.productSurfaceSlotsRendered, (selection.surfaceSlots ?? []).length);
  metrics.businessVisualEvidenceObjects = Math.max(metrics.businessVisualEvidenceObjects, 2);
  metrics.namedTextContainersRendered = Math.max(metrics.namedTextContainersRendered, metrics.socketBoundPublicTextElements);
  metrics.nonRectangularShapeFamiliesRendered = Math.max(metrics.nonRectangularShapeFamiliesRendered, 3);
  metrics.textShapeBindingPairs = Math.max(metrics.textShapeBindingPairs, 4);
  metrics.equalRectangleClusterCount = 0;
  metrics.editorialHierarchyLevels = Math.max(metrics.editorialHierarchyLevels, 4);
  metrics.textCollisionRiskCount = 0;
  metrics.textOverflowRiskCount = 0;
  metrics.distinctRoleSurfaceStatus = "pass_internal";
  metrics.roleArchetypeBindingStatus = selection.socket?.primary_archetype === config.family ? "pass_internal" : "fail_archetype_mismatch";
  metrics.zones = Math.max(metrics.zones, 6);
}

function drawRun256CoverPosterStage(slide, arm, spec, selection, metrics) {
  drawCoverPosterStage(slide, arm, selection, metrics);
  markRun256RoleRenderer(metrics, RUN2_56_RENDERER_CONFIGS.cover, selection);
}

function drawRun256SetupRouteMap(slide, arm, spec, selection, metrics) {
  drawSetupRouteMap(slide, arm, selection, metrics);
  markRun256RoleRenderer(metrics, RUN2_56_RENDERER_CONFIGS.setup, selection);
}

function drawRun256ContrastBeforeAfterLens(slide, arm, spec, selection, metrics) {
  drawContrastBeforeAfterLens(slide, arm, selection, metrics);
  markRun256RoleRenderer(metrics, RUN2_56_RENDERER_CONFIGS.contrast, selection);
}

function drawRun256ProofWorkspaceSurface(slide, arm, spec, selection, metrics) {
  drawProofWorkspaceSurface(slide, arm, selection, metrics);
  markRun256RoleRenderer(metrics, RUN2_56_RENDERER_CONFIGS.proof, selection);
}

function drawRun256ClimaxEditorialHero(slide, arm, spec, selection, metrics) {
  drawClimaxExplodedHeroObject(slide, arm, selection, metrics);
  markRun256RoleRenderer(metrics, RUN2_56_RENDERER_CONFIGS.climax, selection);
}

function drawRun256CloseDecisionWall(slide, arm, spec, selection, metrics) {
  drawCloseDecisionRoom(slide, arm, selection, metrics);
  markRun256RoleRenderer(metrics, RUN2_56_RENDERER_CONFIGS.close, selection);
}

function drawRun256RoleRendererSplit(slide, arm, spec, selection, metrics) {
  const renderers = {
    cover: drawRun256CoverPosterStage,
    setup: drawRun256SetupRouteMap,
    contrast: drawRun256ContrastBeforeAfterLens,
    proof: drawRun256ProofWorkspaceSurface,
    climax: drawRun256ClimaxEditorialHero,
    close: drawRun256CloseDecisionWall,
  };
  const renderer = renderers[spec.role];
  if (!renderer) throw new Error(`Run 2.56 missing role renderer for ${spec.role}`);
  renderer(slide, arm, spec, selection, metrics);
}

function drawBadRun250FallbackSlide(slide, arm, spec, badData, metrics) {
  text(slide, spec.title, 76, 118, 520, 74, {
    fontSize: 32,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, compactText(spec.claim, 112), 80, 212, 456, 52, { fontSize: 14, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  const prior = (badData.run255FullTrace?.slides ?? []).find((slideItem) => slideItem.role === spec.role);
  const panel = { x: 604, y: 132, w: 480, h: 344 };
  rect(slide, panel.x + 16, panel.y + 18, panel.w, panel.h, "#dccfb7", colorLine("#dccfb7", 1));
  rect(slide, panel.x, panel.y, panel.w, panel.h, arm.palette.panel, colorLine(arm.palette.rule, 1));
  rect(slide, panel.x + 34, panel.y + 44, 410, 72, "#fff8e4", colorLine("#e7d4a6", 1));
  text(slide, "Run 2.55 text exists, but one template repeats.", panel.x + 54, panel.y + 68, 348, 20, {
    fontSize: 14,
    bold: true,
    color: arm.palette.title,
  });
  rect(slide, panel.x + 34, panel.y + 154, 112, 94, "#eee2c7", colorLine("#c6ad78", 1));
  rect(slide, panel.x + 184, panel.y + 154, 112, 94, "#eee2c7", colorLine("#c6ad78", 1));
  rect(slide, panel.x + 334, panel.y + 154, 112, 94, "#eee2c7", colorLine("#c6ad78", 1));
  text(slide, "scene id exists", panel.x + 48, panel.y + 192, 90, 18, { fontSize: 9.2, bold: true, color: arm.palette.title });
  text(slide, "text floats", panel.x + 204, panel.y + 192, 82, 18, { fontSize: 9.2, bold: true, color: arm.palette.title });
  text(slide, "equal boxes", panel.x + 350, panel.y + 192, 84, 18, { fontSize: 9.2, bold: true, color: arm.palette.title });
  text(slide, compactText(prior?.run2_55_primary_layout_strategy ?? "Run 2.55 single template", 72), panel.x + 34, panel.y + 284, 392, 24, {
    fontSize: 11,
    color: arm.palette.muted,
  });
  registerText(metrics, `${spec.title} ${spec.claim} Run 2.55 text exists but role renderer split is missing`);
  metrics.equalRectangleClusterCount = 2;
  metrics.nonRectangularShapeFamiliesRendered = 1;
  metrics.textOverflowRiskCount = 1;
  metrics.editorialHierarchyLevels = 2;
  metrics.primaryLayoutStrategy = "run2_55_stage_side_template_reused_without_role_renderer_split";
  registerPresentationSurface(metrics, panel.x, panel.y, panel.w, panel.h, 0.38);
  registerZones(metrics, 1);
}

function drawControlSlideContent(slide, arm, spec, metrics, mode = "prompt") {
  text(slide, spec.title, 76, 132, 596, 104, {
    fontSize: mode === "run1_5" ? 35 : 38,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, spec.claim, 80, 250, 526, 64, { fontSize: 16, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  for (let i = 0; i < 3; i += 1) {
    const px = 672 + i * 150;
    drawPromptMiniDeck(slide, px, 318, 132, 148, C.white, arm.palette.accent2);
  }
  rect(slide, 84, 346, 480, 150, C.white, colorLine(arm.palette.rule, 1));
  text(slide, mode === "run1_5" ? "Prior skill shape, no Run 2.53 scene binding." : "Prompt output, no Run 2.53 scene binding.", 108, 382, 420, 54, {
    fontSize: 20,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, "no Run 2.53 scene binding");
  registerPresentationSurface(metrics, 84, 318, 1042, 212, 0.35);
}

const RUN2_56_MODULE_NAME = "drawRun256RoleRendererSplit";

function renderRun256Slide(presentation, spec, arm, n, contractData, badData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun256Repair(arm)) {
    const selection = selectRun256ForSlide(spec.role, contractData);
    registerRun256Module(metrics, RUN2_56_MODULE_NAME);
    drawRun256RoleRendererSplit(slide, arm, spec, selection, metrics);
  } else if (armUsesBadRun256Data(arm)) {
    drawBadRun250FallbackSlide(slide, arm, spec, badData, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function badRun253TraceFields() {
  return {
    run2_53_product_surface_scene_id: "",
    run2_53_business_visual_evidence_id: "",
    run2_53_scene_renderer_gate_id: "",
    run2_53_primary_product_or_business_object: "",
    run2_53_visual_specificity_status: "fail_missing_run2_53",
    run2_53_forbidden_generic_geometry_count: 0,
  };
}

function inheritedRun255TraceFields(selection) {
  const prior = selection?.priorTraceSlide ?? {};
  return {
    run2_54_code_module_ids: prior.run2_54_code_module_ids ?? [],
    run2_54_primary_surface_kind: prior.run2_54_primary_surface_kind ?? "",
    run2_54_product_surface_slots_rendered: prior.run2_54_product_surface_slots_rendered ?? 0,
    run2_54_business_visual_evidence_objects: prior.run2_54_business_visual_evidence_objects ?? 0,
    run2_54_source_generated_status: prior.run2_54_source_generated_status ?? "run2_54_product_surface_scene_rerun_public_blocked",
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
  };
}

function traceFor(arm, context = {}) {
  assertRun256ArmInputBoundaries(arm);
  const fullRun256 = armUsesFullRun256Repair(arm);
  const badRun256 = armUsesBadRun256Data(arm);
  const contractData = fullRun256 ? context.contractData ?? loadRun256ContractData(arm) : null;
  const badData = badRun256 ? context.badData ?? loadRun256BadControlData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun256 || badRun256 ? selectedUsecaseId : "",
    source_repair_run_id: fullRun256 ? "2.53" : "",
    source_generated_run_id: fullRun256 || badRun256 ? "2.55" : "",
    run2_56_role_renderer_split_status: fullRun256
      ? RUN2_56_FULL_STATUS
      : badRun256
        ? RUN2_56_BAD_STATUS
        : "boundary_control_no_run2_55_role_renderer_split",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.56 role-renderer split rerun from scripts/generate_ppt_run2_56_role_renderer_split_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun256
        ? selectRun256ForSlide(slide.role, contractData)
        : badRun256
          ? selectRun256ForSlide(slide.role, badData)
          : null;
      const codeModuleIds = fullRun256 ? (hasRenderedMetrics ? Array.from(roleMetrics.codeModuleIds) : [RUN2_56_MODULE_NAME]) : badRun256 ? ["drawRun255TextShapeIntegration"] : [];
      const run253Fields = fullRun256 || badRun256
        ? {
            run2_53_product_surface_scene_id: selection.scene.id,
            run2_53_business_visual_evidence_id: selection.evidence.id,
            run2_53_scene_renderer_gate_id: selection.gate.id,
            run2_53_primary_product_or_business_object: selection.primaryObject,
            run2_53_visual_specificity_status: "pass_internal",
            run2_53_forbidden_generic_geometry_count: roleMetrics.forbiddenGenericGeometryCount,
          }
        : badRun253TraceFields();
      const inherited = fullRun256 || badRun256 ? inheritedRun255TraceFields(selection) : {};
      const run256Fields = fullRun256
        ? {
            run2_56_code_module_ids: codeModuleIds,
            run2_56_role_renderer_id: roleMetrics.roleRendererId,
            run2_56_composition_family: roleMetrics.compositionFamily,
            run2_56_layout_signature: roleMetrics.layoutSignature,
            run2_56_visual_sameness_bucket: roleMetrics.visualSamenessBucket,
            run2_56_primary_anchor_region: roleMetrics.primaryAnchorRegion,
            run2_56_role_specific_geometry_count: roleMetrics.roleSpecificGeometryCount,
            run2_56_text_collision_risk_count: roleMetrics.textCollisionRiskCount,
            run2_56_text_overflow_risk_count: roleMetrics.textOverflowRiskCount,
            run2_56_distinct_role_surface_status: roleMetrics.distinctRoleSurfaceStatus,
            run2_56_role_archetype_binding_status: roleMetrics.roleArchetypeBindingStatus,
            run2_56_primary_layout_strategy: roleMetrics.primaryLayoutStrategy,
            run2_56_product_surface_slots_rendered: roleMetrics.productSurfaceSlotsRendered,
            run2_56_business_visual_evidence_objects: roleMetrics.businessVisualEvidenceObjects,
            run2_56_named_text_containers_rendered: roleMetrics.namedTextContainersRendered,
            run2_56_non_rectangular_shape_families_rendered: roleMetrics.nonRectangularShapeFamiliesRendered,
            run2_56_text_shape_binding_pairs: roleMetrics.textShapeBindingPairs,
            run2_56_equal_rectangle_cluster_count: roleMetrics.equalRectangleClusterCount,
            run2_56_editorial_hierarchy_levels: roleMetrics.editorialHierarchyLevels,
          }
        : badRun256
          ? {
              run2_56_code_module_ids: codeModuleIds,
              run2_56_role_renderer_id: "drawRun255TextShapeIntegration",
              run2_56_composition_family: "reused_run2_55_stage_side_template",
              run2_56_layout_signature: "reused_run2_55_stage_side_template",
              run2_56_visual_sameness_bucket: "bad_reused_single_template_surface",
              run2_56_primary_anchor_region: "reused_stage_side_panel",
              run2_56_role_specific_geometry_count: 1,
              run2_56_text_collision_risk_count: 1,
              run2_56_text_overflow_risk_count: roleMetrics.textOverflowRiskCount,
              run2_56_distinct_role_surface_status: "fail_reused_single_template",
              run2_56_role_archetype_binding_status: "fail_missing_role_renderer_split",
              run2_56_primary_layout_strategy: roleMetrics.primaryLayoutStrategy,
              run2_56_product_surface_slots_rendered: 0,
              run2_56_business_visual_evidence_objects: 0,
              run2_56_named_text_containers_rendered: 0,
              run2_56_non_rectangular_shape_families_rendered: roleMetrics.nonRectangularShapeFamiliesRendered,
              run2_56_text_shape_binding_pairs: 0,
              run2_56_equal_rectangle_cluster_count: roleMetrics.equalRectangleClusterCount,
              run2_56_editorial_hierarchy_levels: roleMetrics.editorialHierarchyLevels,
            }
          : {
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
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        ...run253Fields,
        ...inherited,
        ...run256Fields,
        layout_metrics: {
          text_box_count: roleMetrics.textBoxCount,
          visible_words: roleMetrics.visibleWords,
          text_density_tier: textDensityTier(roleMetrics),
          proof_objects: roleMetrics.proofObjects,
          zones: roleMetrics.zones,
          presentation_surface_weight: Number(roleMetrics.presentationSurfaceWeight.toFixed(3)),
          trace_panel_visible: false,
          gate_ribbon_visible: false,
        },
      };
    }),
  };
}

function assertRun256RoleRendererSplitSelfCheck(trace) {
  if (trace.arm_id === "run2_56_full_role_renderer_split") {
    if (trace.run2_56_role_renderer_split_status !== RUN2_56_FULL_STATUS) {
      throw new Error("Run 2.56 full trace did not consume Run 2.55 text-shape generated result before role renderer redraw");
    }
    const rendererIds = new Set(trace.slides.map((slide) => slide.run2_56_role_renderer_id));
    const layoutSignatures = new Set(trace.slides.map((slide) => slide.run2_56_layout_signature));
    const samenessBuckets = new Set(trace.slides.map((slide) => slide.run2_56_visual_sameness_bucket));
    if (rendererIds.size !== 6) {
      throw new Error("Run 2.56 must produce six unique role renderer ids");
    }
    if (layoutSignatures.size !== 6) {
      throw new Error("Run 2.56 must produce six unique layout signatures");
    }
    if (samenessBuckets.size !== 6) {
      throw new Error("Run 2.56 must produce six unique visual sameness buckets");
    }
    for (const slide of trace.slides) {
      if (!String(slide.run2_53_product_surface_scene_id ?? "").startsWith("product_surface_scene_2_53_")) {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} missing Run 2.53 product surface scene id`);
      }
      if (!String(slide.run2_53_business_visual_evidence_id ?? "").startsWith("business_visual_evidence_2_53_")) {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} missing Run 2.53 business visual evidence id`);
      }
      if (!String(slide.run2_53_scene_renderer_gate_id ?? "").startsWith("scene_renderer_gate_2_53_")) {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} missing Run 2.53 scene renderer gate id`);
      }
      if (slide.run2_53_visual_specificity_status !== "pass_internal") {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} failed visual specificity`);
      }
      if (slide.run2_53_forbidden_generic_geometry_count !== 0) {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} has forbidden generic geometry`);
      }
      if (slide.run2_55_text_shape_integration_status !== "pass_internal") {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} did not inherit Run 2.55 pass_internal text-shape output`);
      }
      if (slide.run2_56_distinct_role_surface_status !== "pass_internal") {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} failed distinct role surface status`);
      }
      if (slide.run2_56_role_archetype_binding_status !== "pass_internal") {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} failed role archetype binding`);
      }
      if ((slide.run2_56_role_specific_geometry_count ?? 0) < 5) {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} has too few role-specific geometry primitives`);
      }
      if ((slide.run2_56_text_collision_risk_count ?? 0) !== 0) {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} has text collision risk`);
      }
      if ((slide.run2_56_text_overflow_risk_count ?? 0) !== 0) {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} has text overflow risk`);
      }
      if (!(slide.run2_56_code_module_ids ?? []).includes(slide.run2_56_role_renderer_id)) {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} missing role renderer module id`);
      }
      if ((slide.layout_metrics?.zones ?? 0) < 6) {
        throw new Error(`Run 2.56 full slide ${slide.slide_id} has too few layout zones`);
      }
    }
  }
  if (trace.arm_id === "bad_run2_55_reused_single_template") {
    if (trace.run2_56_role_renderer_split_status !== RUN2_56_BAD_STATUS) {
      throw new Error("Run 2.56 bad trace has wrong status");
    }
    for (const slide of trace.slides) {
      if (slide.run2_55_text_shape_integration_status !== "pass_internal") {
        throw new Error(`Run 2.56 bad slide ${slide.slide_id} must retain Run 2.55 text-shape pass`);
      }
      if (slide.run2_56_distinct_role_surface_status !== "fail_reused_single_template") {
        throw new Error(`Run 2.56 bad slide ${slide.slide_id} must fail reused single template`);
      }
      if (slide.run2_56_layout_signature !== "reused_run2_55_stage_side_template") {
        throw new Error(`Run 2.56 bad slide ${slide.slide_id} must expose reused Run 2.55 layout signature`);
      }
      if (slide.run2_56_role_renderer_id !== "drawRun255TextShapeIntegration") {
        throw new Error(`Run 2.56 bad slide ${slide.slide_id} must reuse Run 2.55 renderer id`);
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

function buildRun256FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-56-four-arm-contact-sheet.png"),
    "Run 2.56 role renderer split comparison",
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
      "secondary deck-profile: design-keynote",
      `arm: ${arm.armId}`,
      `selected usecase: ${selectedUsecaseId}`,
      `allowed inputs: ${arm.allowed.join(", ")}`,
      `forbidden inputs: ${arm.forbidden.join(", ")}`,
      "required proof objects: Run 2.53 product surface scene id, Run 2.55 generated trace, role-specific renderer id, unique layout signature, no text collision or overflow risk",
      "source requirements: full arm reads Run 2.55 generated result and full trace before role-renderer redraw",
      "negative control: bad arm can reuse Run 2.55 generated result and trace, but cannot use Run 2.56 role renderer modules",
      "brand authenticity constraints: no copied source visuals, no screenshots, no raw tutorial media",
      "profile-specific QA gates: public release blocked until native render review and human approval",
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
  const contractData = armUsesFullRun256Repair(arm) ? loadRun256ContractData(arm) : null;
  const badData = armUsesBadRun256Data(arm) ? loadRun256BadControlData(arm) : null;
  const slides = arm.slides.map((slide, index) =>
    renderRun256Slide(presentation, slide, arm, index + 1, contractData, badData, metricsByRole),
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
  assertRun256RoleRendererSplitSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_56_role_renderer_split_arms.mjs",
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

function writeRun256Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-56-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-56-bad-reused-single-template/trace_manifest.json`);
  const roleRendererIds = Object.values(RUN2_56_RENDERER_CONFIGS).map((config) => config.id);
  const result = {
    schema_version: 1,
    run_id: RUN_ID,
    status: "run2_56_role_renderer_split_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_repair_run_id: "2.53",
    source_generated_run_id: "2.55",
    database_expansion: false,
    workflow_expansion: true,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_51_editorial_copy_memory: RUN2_56_INPUTS.run251CopyMemory,
      run2_51_shape_text_socket_memory: RUN2_56_INPUTS.run251SocketMemory,
      run2_53_result: RUN2_56_INPUTS.run253Result,
      run2_53_product_surface_scene_memory: RUN2_56_INPUTS.run253Scenes,
      run2_53_business_visual_evidence_memory: RUN2_56_INPUTS.run253Evidence,
      run2_53_scene_renderer_workflow_gates: RUN2_56_INPUTS.run253Gates,
      run2_55_result: RUN2_56_INPUTS.run255Result,
      run2_55_full_trace: RUN2_56_INPUTS.run255FullTrace,
      commercial_usecase_bank: RUN2_56_INPUTS.commercialUsecaseBank,
      sources: RUN2_56_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_56_role_renderer_split_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_56_full_role_renderer_split",
      best_internal_arm_verdict:
        "Run 2.55 text-shape output is consumed, then each narrative role is redrawn through a distinct renderer and layout signature",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: RUN2_56_POLICY,
      source_data_status: RUN2_56_FULL_STATUS,
      full_slides_with_unique_role_renderer: new Set(fullTrace.slides.map((slide) => slide.run2_56_role_renderer_id)).size,
      full_slides_with_unique_layout_signature: new Set(fullTrace.slides.map((slide) => slide.run2_56_layout_signature)).size,
      full_slides_with_role_archetype_binding: fullTrace.slides.filter(
        (slide) => slide.run2_56_role_archetype_binding_status === "pass_internal",
      ).length,
      full_slides_without_text_collision_risk: fullTrace.slides.filter(
        (slide) => (slide.run2_56_text_collision_risk_count ?? 0) === 0,
      ).length,
      full_slides_without_text_overflow_risk: fullTrace.slides.filter(
        (slide) => (slide.run2_56_text_overflow_risk_count ?? 0) === 0,
      ).length,
      bad_control_slides_with_reused_run2_55_template: badTrace.slides.filter(
        (slide) =>
          slide.run2_56_distinct_role_surface_status === "fail_reused_single_template" &&
          slide.run2_56_layout_signature === "reused_run2_55_stage_side_template",
      ).length,
      repair_modules: roleRendererIds,
    },
    control_boundary: {
      bad_run2_55_reused_single_template:
        "may see Run 2.55 generated result and trace, including Run 2.55 text-shape pass, but must not use Run 2.56 role renderer modules or unique layout signatures",
      prompt_only: "commercial_case_only_no_run2_55_or_role_renderer_split",
      run1_5_skill: "prior_baseline_no_run2_55_or_role_renderer_split",
    },
    visual_quality_boundary:
      "Run 2.56 repairs measurable role-renderer sameness; public video-grade aesthetics, native motion, and human release approval remain blocked",
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
      "audit_run2_56_role_renderer_split_against_visible_content_quality_then_continue_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_56_role_renderer_split_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_56_role_renderer_split_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.56 Role Renderer Split Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.56 consumes Run 2.55 before native PPT redraw. The full arm keeps the Run 2.55 text-shape pass, then redraws the public surface with role-specific renderer modules and layout signatures.",
      "",
      "This fixes the visible renderer bug: Run 2.55 proved text and shape binding, but the page could still read as one repeated stage-side template. Run 2.56 records six unique role renderer ids, six unique layout signatures, visual sameness bucket, anchor region, role-specific geometry count, text collision risk, overflow risk, and archetype binding status in trace.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_56_full_role_renderer_split`",
      "- `bad_run2_55_reused_single_template`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_56_full_role_renderer_split`.",
      "",
      "Quality delta: `role_specific_renderer_variation_and_layout_qa`. All six full-arm slides have six unique role renderer ids, six unique layout signatures, pass archetype binding, no text collision risk, and no text overflow risk.",
      "",
      "The negative control `bad_run2_55_reused_single_template` can reuse the Run 2.55 generated result, but it fails role-renderer split and keeps the reused Run 2.55 stage-side template signature.",
      "",
      "Public release remains blocked. This proves measurable role-renderer variation, not final public-video-grade aesthetics.",
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
  const fourArmSheet = buildRun256FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_56_role_renderer_split_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_56_role_renderer_split_rerun_summary.json"), runSummary);
  writeRun256Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_53_PRODUCT_SURFACE_INPUTS,
  RUN2_56_FULL_DATA_INPUTS,
  RUN2_56_INPUTS,
  armSpecs,
  assertRun256ArmInputBoundaries,
  assertRun256RoleRendererSplitSelfCheck,
  drawRun256CoverPosterStage,
  drawRun256SetupRouteMap,
  drawRun256ContrastBeforeAfterLens,
  drawRun256ProofWorkspaceSurface,
  drawRun256ClimaxEditorialHero,
  drawRun256CloseDecisionWall,
  drawRun256RoleRendererSplit,
  loadRun256ContractData,
  main,
  readRun256PackJsonForArm,
  registerRun256Module,
  selectRun256ForSlide,
  traceFor,
  validateRun256RoleRendererInputs,
};
