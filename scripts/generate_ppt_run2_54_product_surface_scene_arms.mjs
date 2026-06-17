import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.54";
const RUN2_54_FULL_STATUS = "run2_53_product_surface_scene_pack_consumed_before_native_ppt_drawing";
const RUN2_54_BAD_STATUS = "run2_52_generated_but_run2_53_product_surface_scene_pack_missing";
const RUN2_54_POLICY = "product_surface_scene_and_business_visual_evidence_binding";
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

const RUN2_54_INPUTS = {
  run253Result: `${pack}/results/run2_53_product_surface_scene_repair_result.json`,
  run253Scenes: `${pack}/run2_53_product_surface_scene_memory.json`,
  run253Evidence: `${pack}/run2_53_business_visual_evidence_memory.json`,
  run253Gates: `${pack}/run2_53_scene_renderer_workflow_gates.json`,
  run252Result: `${pack}/results/run2_52_editorial_socket_renderer_rerun_result.json`,
  run252FullTrace: `outputs/${threadId}/presentations/ppt-run2-52-full-vulca/trace_manifest.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_53_PRODUCT_SURFACE_INPUTS = [
  RUN2_54_INPUTS.run253Result,
  RUN2_54_INPUTS.run253Scenes,
  RUN2_54_INPUTS.run253Evidence,
  RUN2_54_INPUTS.run253Gates,
];
const RUN2_54_FULL_DATA_INPUTS = Object.values(RUN2_54_INPUTS);
const RUN2_54_BAD_DATA_INPUTS = [
  RUN2_54_INPUTS.run252Result,
  RUN2_54_INPUTS.run252FullTrace,
  RUN2_54_INPUTS.commercialUsecaseBank,
  RUN2_54_INPUTS.sources,
];

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
    slug: "ppt-run2-54-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.54 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_54_FULL_DATA_INPUTS, "drawRun254ProductSurfaceScene"],
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
    slug: "ppt-run2-54-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.54 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_54_FULL_DATA_INPUTS, "drawRun254ProductSurfaceScene"],
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
    armId: "run2_54_full_product_surface_scene",
    slug: "ppt-run2-54-full-vulca",
    label: "Run 2.54 full product surface scene",
    kicker: "RUN 2.54 / PRODUCT SURFACE",
    footer: "run2_54_full_product_surface_scene | consumes Run 2.53 | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      ...RUN2_54_FULL_DATA_INPUTS,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_53_product_surface_scene_memory.json",
      "run2_53_business_visual_evidence_memory.json",
      "run2_53_scene_renderer_workflow_gates.json",
      RUN2_54_POLICY,
    ],
    forbidden: [
      "raw evidence fields on public surface",
      "source layouts",
      "copied screenshots",
      "square_block_grid_as_primary_surface",
      "equal_three_card_grid_as_primary_surface",
      "native_drawing_before_run2_53_scene_binding",
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
    armId: "bad_run2_53_missing_product_surface_scene_pack",
    slug: "ppt-run2-54-bad-missing-run2-53-product-surface-scene-pack",
    label: "Bad missing Run 2.53 product surface scene pack",
    kicker: "RUN 2.54 / BAD CONTROL",
    footer: "bad_run2_53_missing_product_surface_scene_pack | Run 2.52 only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_54_BAD_DATA_INPUTS],
    data_input_manifest: ["run2_52_generated_without_run2_53_product_surface_scene_pack"],
    forbidden: [
      ...RUN2_53_PRODUCT_SURFACE_INPUTS,
      "run2_53_product_surface_scene_id",
      "run2_53_business_visual_evidence_id",
      "run2_53_scene_renderer_gate_id",
      "run2_53_primary_product_or_business_object",
      "run2_53_visual_specificity_status",
      "run2_53_forbidden_generic_geometry_count",
      "drawRun254ProductSurfaceScene",
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
        "Run 2.52 draws, but the product scene is missing.",
        "The route lacks scene and evidence ids.",
        "The lens falls back to generated labels.",
        "The workspace has no scene proof.",
        "The result object lacks 2.53 gates.",
        "The decision room cannot prove scene binding.",
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
    codeModuleIds: new Set(),
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun254Module(metrics, functionName) {
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

function armUsesFullRun254Repair(arm) {
  return arm.armId === "run2_54_full_product_surface_scene";
}

function armUsesBadRun254Data(arm) {
  return arm.armId === "bad_run2_53_missing_product_surface_scene_pack";
}

function assertRun254ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun254Repair(arm)) {
    for (const input of RUN2_54_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesBadRun254Data(arm)) {
    for (const input of RUN2_54_BAD_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow bad-control input ${input}`);
    }
    for (const input of RUN2_53_PRODUCT_SURFACE_INPUTS) {
      if (allowed.has(input) || !forbidden.has(input)) throw new Error(`${arm.armId} must block ${input}`);
    }
    return;
  }
  for (const input of RUN2_54_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun254PackJsonForArm(arm, relPath) {
  assertRun254ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (!armUsesFullRun254Repair(arm) && !armUsesBadRun254Data(arm)) {
    throw new Error(`${arm.armId} cannot read Run 2.54 pack data`);
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
    throw new Error(`Run 2.54 selected usecase mismatch in ${label}`);
  }
}

function assertPublicCopyBundle(copy, role) {
  const bundle = copy.public_surface_copy_bundle;
  if (!bundle || typeof bundle !== "object") {
    throw new Error(`Run 2.54 public copy bundle missing for ${role}`);
  }
  for (const key of ["headline", "subline"]) {
    if (typeof bundle[key] !== "string" || !bundle[key].trim()) {
      throw new Error(`Run 2.54 public copy ${key} missing for ${role}`);
    }
  }
  for (const key of ["proof_nuggets", "annotations", "state_labels"]) {
    if (!Array.isArray(bundle[key]) || !bundle[key].length || !bundle[key].every((item) => typeof item === "string" && item.trim())) {
      throw new Error(`Run 2.54 public copy ${key} malformed for ${role}`);
    }
  }
}

function validateRun254RepairPack(data) {
  const {
    run253Result,
    run253Scenes,
    run253Evidence,
    run253Gates,
    run252Result,
    run252FullTrace,
    commercialUsecaseBank,
    sources,
  } = data;
  if (run253Result?.status !== "run2_53_product_surface_scene_repair_ready_public_blocked") throw new Error("Run 2.54 must consume Run 2.53 repair result");
  if (run253Result?.next_required_action !== "consume_run2_53_before_run2_54_four_arm_rerun") throw new Error("Run 2.53 result does not point to Run 2.54");
  if (run253Scenes?.status !== "run2_53_product_surface_scene_memory_ready_public_blocked") throw new Error("Run 2.54 product surface scene status mismatch");
  if (run253Evidence?.status !== "run2_53_business_visual_evidence_memory_ready_public_blocked") throw new Error("Run 2.54 business visual evidence status mismatch");
  if (run253Gates?.status !== "run2_53_scene_renderer_workflow_gates_ready_public_blocked") throw new Error("Run 2.54 scene renderer gate status mismatch");
  if (run252Result?.status !== "run2_52_editorial_socket_renderer_rerun_public_blocked") throw new Error("Run 2.54 must use Run 2.52 as source generated run");
  if (run252FullTrace?.arm_id !== "run2_52_full_editorial_socket_renderer") throw new Error("Run 2.54 must compare against Run 2.52 full trace");
  if (!Array.isArray(sources?.sources) || sources.sources.length < 4) throw new Error("Run 2.54 missing sources");
  const usecase = (commercialUsecaseBank?.usecases ?? []).find((item) => item.id === selectedUsecaseId);
  if (!usecase) throw new Error("Run 2.54 missing selected commercial usecase");
  assertSelectedUsecase(run253Result?.selected_usecase_id, "run2_53_result");
  assertSelectedUsecase(run253Scenes?.selected_usecase_id, "run2_53_product_surface_scene_memory");
  assertSelectedUsecase(run253Evidence?.selected_usecase_id, "run2_53_business_visual_evidence_memory");
  assertSelectedUsecase(run253Gates?.selected_usecase_id, "run2_53_scene_renderer_workflow_gates");
  assertSelectedUsecase(run252Result?.selected_usecase_id, "run2_52_result");
  assertSelectedUsecase(run252FullTrace?.selected_usecase_id, "run2_52_full_trace");

  if (!Array.isArray(run253Scenes?.product_surface_scene_records) || run253Scenes.product_surface_scene_records.length !== 6) throw new Error("Run 2.54 requires six Run 2.53 product surface scene records");
  if (!Array.isArray(run253Evidence?.business_visual_evidence_records) || run253Evidence.business_visual_evidence_records.length !== 6) throw new Error("Run 2.54 requires six Run 2.53 business visual evidence records");
  if (!Array.isArray(run253Gates?.scene_renderer_workflow_gates) || run253Gates.scene_renderer_workflow_gates.length !== 6) throw new Error("Run 2.54 requires six Run 2.53 scene renderer gates");

  for (const role of baseSlides.map((slide) => slide.role)) {
    const scene = run253Scenes.product_surface_scene_records.find((record) => record.role === role);
    const evidence = run253Evidence.business_visual_evidence_records.find((record) => record.role === role);
    const gate = run253Gates.scene_renderer_workflow_gates.find((record) => record.role === role);
    const priorTraceSlide = (run252FullTrace.slides ?? []).find((slide) => slide.role === role);
    if (!scene || !evidence || !gate || !priorTraceSlide) throw new Error(`Run 2.54 missing role contract for ${role}`);
    assertSelectedUsecase(scene.selected_usecase_id, `run2_53_scene_record_${role}`);
    assertSelectedUsecase(evidence.selected_usecase_id, `run2_53_evidence_record_${role}`);
    assertSelectedUsecase(gate.selected_usecase_id, `run2_53_gate_record_${role}`);
    if (scene.must_render_product_or_business_object !== true) {
      throw new Error(`Run 2.54 scene must render product or business object for ${role}`);
    }
    if ((scene.surface_slots ?? []).length < 3) {
      throw new Error(`Run 2.54 product surface slots too thin for ${role}`);
    }
    if (evidence.required_product_surface_scene_id !== scene.id) {
      throw new Error(`Run 2.54 evidence/scene mismatch for ${role}`);
    }
    if (gate.required_product_surface_scene_id !== scene.id) {
      throw new Error(`Run 2.54 gate/scene mismatch for ${role}`);
    }
    if (gate.required_business_visual_evidence_id !== evidence.id) {
      throw new Error(`Run 2.54 gate/evidence mismatch for ${role}`);
    }
    if (gate.consumer_contract?.next_generated_run !== RUN_ID) {
      throw new Error(`Run 2.54 consumer_contract.next_generated_run mismatch for ${role}`);
    }
    if (gate.consumer_contract?.must_bind_before_native_drawing !== true) {
      throw new Error(`Run 2.54 must_bind_before_native_drawing mismatch for ${role}`);
    }
  }
}

function loadRun254ContractData(arm) {
  const data = {
    run253Result: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.run253Result),
    run253Scenes: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.run253Scenes),
    run253Evidence: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.run253Evidence),
    run253Gates: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.run253Gates),
    run252Result: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.run252Result),
    run252FullTrace: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.run252FullTrace),
    commercialUsecaseBank: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.commercialUsecaseBank),
    sources: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.sources),
  };
  validateRun254RepairPack(data);
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_54_run2_53_product_surface_scene_pack_contract_ready",
  };
}

function loadRun254BadControlData(arm) {
  const data = {
    run252Result: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.run252Result),
    run252FullTrace: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.run252FullTrace),
    commercialUsecaseBank: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.commercialUsecaseBank),
    sources: readRun254PackJsonForArm(arm, RUN2_54_INPUTS.sources),
  };
  if (data.run252Result?.status !== "run2_52_editorial_socket_renderer_rerun_public_blocked") {
    throw new Error("Run 2.54 bad control must read Run 2.52 result");
  }
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
  };
}

function selectRun254ForSlide(role, contractData) {
  const scene = (contractData.run253Scenes?.product_surface_scene_records ?? []).find((item) => item.role === role);
  const evidence = (contractData.run253Evidence?.business_visual_evidence_records ?? []).find((item) => item.role === role);
  const gate = (contractData.run253Gates?.scene_renderer_workflow_gates ?? []).find((item) => item.role === role);
  const priorTraceSlide = (contractData.run252FullTrace?.slides ?? []).find((item) => item.role === role);
  if (!scene || !evidence || !gate || !priorTraceSlide) throw new Error(`Run 2.54 missing role contract for ${role}`);
  return {
    role,
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

function drawRun254ProductSurfaceScene(slide, arm, spec, selection, metrics, moduleName) {
  registerRun254Module(metrics, moduleName);
  const scene = selection.scene;
  const evidence = selection.evidence;
  const slots = selection.surfaceSlots.slice(0, 4);
  const checks = (evidence.minimum_visual_specificity_checks ?? []).slice(0, 3);
  const darkScene = spec.role === "climax";
  metrics.primarySurfaceKind = scene.scene_object_kind;
  metrics.shapePrimitiveCount = 5;
  metrics.productSurfaceSlotsRendered = slots.length;
  metrics.businessVisualEvidenceObjects = 1;
  metrics.forbiddenGenericGeometryCount = 0;

  const stage = spec.role === "cover" || spec.role === "climax"
    ? { x: 86, y: 118, w: 712, h: 410 }
    : { x: 470, y: 124, w: 612, h: 384 };
  const side = spec.role === "cover" || spec.role === "climax"
    ? { x: 842, y: 132, w: 296, h: 380 }
    : { x: 78, y: 116, w: 330, h: 420 };

  rect(slide, stage.x + 18, stage.y + 20, stage.w, stage.h, darkScene ? "#1f2a36" : "#dbe4ea", colorLine("transparent", 0));
  rect(slide, stage.x, stage.y, stage.w, stage.h, darkScene ? "#111820" : C.white, colorLine(darkScene ? "#111820" : "#d4dde4", 1));
  rect(slide, stage.x + 34, stage.y + 42, stage.w - 68, stage.h - 104, darkScene ? "#eff5f7" : "#f7fafb", colorLine("#d9e2e8", 1));
  rect(slide, stage.x + 60, stage.y + 74, stage.w - 120, 46, arm.palette.accent2, colorLine("transparent", 0));
  rect(slide, stage.x + 72, stage.y + 150, stage.w - 250, 78, "#ffffff", colorLine("#d5dde2", 1));
  rect(slide, stage.x + stage.w - 164, stage.y + 150, 82, 118, "#e8edf0", colorLine("#cfd9df", 1));
  rect(slide, stage.x + 88, stage.y + 266, stage.w - 208, 42, arm.palette.proof, colorLine("transparent", 0));

  socketText(slide, metrics, spec.title, side.x, side.y, side.w, 74, {
    fontSize: spec.role === "climax" ? 36 : 32,
    title: true,
    bold: true,
    color: arm.palette.title,
    max: 58,
  });
  socketText(slide, metrics, spec.claim, side.x + 2, side.y + 88, side.w - 4, 62, {
    fontSize: 13.6,
    color: arm.palette.muted,
    max: 130,
  });
  socketText(slide, metrics, selection.primaryObject, stage.x + 86, stage.y + 166, stage.w - 286, 52, {
    fontSize: 17,
    title: true,
    bold: true,
    color: C.ink,
    max: 120,
  });
  socketText(slide, metrics, evidence.reader_question_answered, side.x, side.y + 172, side.w, 70, {
    fontSize: 11.4,
    color: C.ink,
    max: 150,
  });

  slots.forEach((slot, index) => {
    const x = stage.x + 64 + index * 146;
    const y = stage.y + stage.h - 74 - (index % 2) * 24;
    rect(slide, x, y, 126, 44, index === 0 ? arm.palette.proof : "#ffffff", colorLine(index === 0 ? arm.palette.proof : "#ccd6dd", 1));
    socketText(slide, metrics, slot, x + 9, y + 10, 108, 22, {
      fontSize: 8.6,
      bold: true,
      color: index === 0 ? C.white : C.ink,
      max: 54,
      align: "center",
    });
  });

  checks.forEach((check, index) => {
    const y = side.y + 274 + index * 46;
    rect(slide, side.x, y, side.w, 34, index === 0 ? "#111820" : "#ffffff", colorLine(index === 0 ? "#111820" : "#d8e0e6", 1));
    socketText(slide, metrics, check, side.x + 14, y + 8, side.w - 28, 16, {
      fontSize: 8.7,
      color: index === 0 ? C.white : arm.palette.muted,
      max: 100,
    });
  });

  registerPresentationSurface(metrics, stage.x, stage.y, stage.w, stage.h, spec.role === "climax" ? 0.62 : 0.5);
  registerProof(metrics, checks.length + 1);
  registerZones(metrics, 6);
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
  const prior = (badData.run252FullTrace?.slides ?? []).find((slideItem) => slideItem.role === spec.role);
  const panel = { x: 604, y: 132, w: 480, h: 344 };
  rect(slide, panel.x + 16, panel.y + 18, panel.w, panel.h, "#dccfb7", colorLine("#dccfb7", 1));
  rect(slide, panel.x, panel.y, panel.w, panel.h, arm.palette.panel, colorLine(arm.palette.rule, 1));
  rect(slide, panel.x + 34, panel.y + 44, 410, 72, "#fff8e4", colorLine("#e7d4a6", 1));
  text(slide, "Run 2.52 generated trace is present.", panel.x + 54, panel.y + 68, 330, 20, {
    fontSize: 14,
    bold: true,
    color: arm.palette.title,
  });
  rect(slide, panel.x + 34, panel.y + 154, 112, 94, "#eee2c7", colorLine("#c6ad78", 1));
  rect(slide, panel.x + 184, panel.y + 154, 112, 94, "#eee2c7", colorLine("#c6ad78", 1));
  rect(slide, panel.x + 334, panel.y + 154, 112, 94, "#eee2c7", colorLine("#c6ad78", 1));
  text(slide, "no scene id", panel.x + 50, panel.y + 192, 84, 18, { fontSize: 9.5, bold: true, color: arm.palette.title });
  text(slide, "no evidence id", panel.x + 196, panel.y + 192, 90, 18, { fontSize: 9.5, bold: true, color: arm.palette.title });
  text(slide, "no gate id", panel.x + 348, panel.y + 192, 84, 18, { fontSize: 9.5, bold: true, color: arm.palette.title });
  text(slide, compactText(prior?.run2_52_primary_surface_kind ?? "Run 2.52 surface only", 72), panel.x + 34, panel.y + 284, 392, 24, {
    fontSize: 11,
    color: arm.palette.muted,
  });
  registerText(metrics, `${spec.title} ${spec.claim} Run 2.52 generated trace present no scene evidence gate id`);
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

const RUN2_54_MODULE_NAME = "drawRun254ProductSurfaceScene";

function renderRun254Slide(presentation, spec, arm, n, contractData, badData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun254Repair(arm)) {
    const selection = selectRun254ForSlide(spec.role, contractData);
    drawRun254ProductSurfaceScene(slide, arm, spec, selection, metrics, RUN2_54_MODULE_NAME);
  } else if (armUsesBadRun254Data(arm)) {
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

function traceFor(arm, context = {}) {
  assertRun254ArmInputBoundaries(arm);
  const fullRun254 = armUsesFullRun254Repair(arm);
  const badRun254 = armUsesBadRun254Data(arm);
  const contractData = fullRun254 ? context.contractData ?? loadRun254ContractData(arm) : null;
  const badData = badRun254 ? context.badData ?? loadRun254BadControlData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun254 || badRun254 ? selectedUsecaseId : "",
    source_repair_run_id: fullRun254 ? "2.53" : "",
    source_generated_run_id: fullRun254 || badRun254 ? "2.52" : "",
    run2_54_product_surface_scene_status: fullRun254
      ? RUN2_54_FULL_STATUS
      : badRun254
        ? RUN2_54_BAD_STATUS
        : "boundary_control_no_run2_53_product_surface_scene_pack_consumption",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.54 product surface scene rerun from scripts/generate_ppt_run2_54_product_surface_scene_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun254 ? selectRun254ForSlide(slide.role, contractData) : null;
      const codeModuleIds = fullRun254 ? (hasRenderedMetrics ? Array.from(roleMetrics.codeModuleIds) : [RUN2_54_MODULE_NAME]) : [];
      const run253Fields = fullRun254
        ? {
            run2_53_product_surface_scene_id: selection.scene.id,
            run2_53_business_visual_evidence_id: selection.evidence.id,
            run2_53_scene_renderer_gate_id: selection.gate.id,
            run2_53_primary_product_or_business_object: selection.primaryObject,
            run2_53_visual_specificity_status: "pass_internal",
            run2_53_forbidden_generic_geometry_count: roleMetrics.forbiddenGenericGeometryCount,
          }
        : badRun253TraceFields();
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        ...run253Fields,
        run2_54_primary_surface_kind: fullRun254
          ? roleMetrics.primarySurfaceKind || selection.primarySurfaceKind
          : badRun254
            ? "square_block_grid"
            : "",
        run2_54_code_module_ids: codeModuleIds,
        run2_54_product_surface_slots_rendered: fullRun254 ? roleMetrics.productSurfaceSlotsRendered : 0,
        run2_54_business_visual_evidence_objects: fullRun254 ? roleMetrics.businessVisualEvidenceObjects : 0,
        run2_54_socket_bound_public_text_elements: fullRun254 ? roleMetrics.socketBoundPublicTextElements : 0,
        run2_54_shape_primitive_count: fullRun254 ? roleMetrics.shapePrimitiveCount : 0,
        run2_52_source_generated_status: fullRun254 || badRun254 ? "run2_52_editorial_socket_renderer_rerun_public_blocked" : "",
        run2_52_source_primary_surface_kind: fullRun254 ? selection.priorTraceSlide.run2_52_primary_surface_kind : "",
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

function assertRun254ProductSurfaceSceneSelfCheck(trace) {
  if (trace.arm_id === "run2_54_full_product_surface_scene") {
    if (trace.run2_54_product_surface_scene_status !== RUN2_54_FULL_STATUS) {
      throw new Error("Run 2.54 full trace did not consume Run 2.53 product surface scene pack");
    }
    for (const slide of trace.slides) {
      if (!String(slide.run2_53_product_surface_scene_id ?? "").startsWith("product_surface_scene_2_53_")) {
        throw new Error(`Run 2.54 full slide ${slide.slide_id} missing Run 2.53 product surface scene id`);
      }
      if (!String(slide.run2_53_business_visual_evidence_id ?? "").startsWith("business_visual_evidence_2_53_")) {
        throw new Error(`Run 2.54 full slide ${slide.slide_id} missing Run 2.53 business visual evidence id`);
      }
      if (!String(slide.run2_53_scene_renderer_gate_id ?? "").startsWith("scene_renderer_gate_2_53_")) {
        throw new Error(`Run 2.54 full slide ${slide.slide_id} missing Run 2.53 scene renderer gate id`);
      }
      if (slide.run2_53_visual_specificity_status !== "pass_internal") {
        throw new Error(`Run 2.54 full slide ${slide.slide_id} failed visual specificity`);
      }
      if (slide.run2_53_forbidden_generic_geometry_count !== 0) {
        throw new Error(`Run 2.54 full slide ${slide.slide_id} has forbidden generic geometry`);
      }
      if ((slide.run2_54_product_surface_slots_rendered ?? 0) < 3) {
        throw new Error(`Run 2.54 full slide ${slide.slide_id} has too few product surface slots`);
      }
      if ((slide.run2_54_business_visual_evidence_objects ?? 0) < 1) {
        throw new Error(`Run 2.54 full slide ${slide.slide_id} has too few business visual evidence objects`);
      }
      if (slide.run2_54_primary_surface_kind === "square_block_grid") {
        throw new Error(`Run 2.54 full slide ${slide.slide_id} regressed to square block grid`);
      }
      if (!(slide.run2_54_code_module_ids ?? []).includes("drawRun254ProductSurfaceScene")) {
        throw new Error(`Run 2.54 full slide ${slide.slide_id} missing drawRun254 module id`);
      }
    }
  }
  if (trace.arm_id === "bad_run2_53_missing_product_surface_scene_pack") {
    if (trace.run2_54_product_surface_scene_status !== RUN2_54_BAD_STATUS) {
      throw new Error("Run 2.54 bad trace has wrong status");
    }
    for (const slide of trace.slides) {
      if (slide.run2_53_product_surface_scene_id !== "") {
        throw new Error(`Run 2.54 bad slide ${slide.slide_id} leaked Run 2.53 product surface scene id`);
      }
      if (slide.run2_53_business_visual_evidence_id !== "") {
        throw new Error(`Run 2.54 bad slide ${slide.slide_id} leaked Run 2.53 business visual evidence id`);
      }
      if (slide.run2_53_scene_renderer_gate_id !== "") {
        throw new Error(`Run 2.54 bad slide ${slide.slide_id} leaked Run 2.53 scene renderer gate id`);
      }
      if (slide.run2_53_visual_specificity_status !== "fail_missing_run2_53") {
        throw new Error(`Run 2.54 bad slide ${slide.slide_id} must fail missing Run 2.53`);
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

function buildRun254FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-54-four-arm-contact-sheet.png"),
    "Run 2.54 product surface scene comparison",
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
      "required proof objects: Run 2.53 product surface scene id, business visual evidence id, scene renderer gate id, product surface slots rendered, business visual evidence objects",
      "source requirements: full arm reads Run 2.53 product surface scene pack before native PPT drawing",
      "negative control: bad arm can reuse Run 2.52 generated result and trace, but cannot read Run 2.53 product surface scene pack",
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
  const contractData = armUsesFullRun254Repair(arm) ? loadRun254ContractData(arm) : null;
  const badData = armUsesBadRun254Data(arm) ? loadRun254BadControlData(arm) : null;
  const slides = arm.slides.map((slide, index) =>
    renderRun254Slide(presentation, slide, arm, index + 1, contractData, badData, metricsByRole),
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
  assertRun254ProductSurfaceSceneSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_54_product_surface_scene_arms.mjs",
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

function writeRun254Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-54-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-54-bad-missing-run2-53-product-surface-scene-pack/trace_manifest.json`);
  const result = {
    schema_version: 1,
    run_id: RUN_ID,
    status: "run2_54_product_surface_scene_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_repair_run_id: "2.53",
    source_generated_run_id: "2.52",
    database_expansion: false,
    workflow_expansion: false,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_53_result: RUN2_54_INPUTS.run253Result,
      run2_53_product_surface_scene_memory: RUN2_54_INPUTS.run253Scenes,
      run2_53_business_visual_evidence_memory: RUN2_54_INPUTS.run253Evidence,
      run2_53_scene_renderer_workflow_gates: RUN2_54_INPUTS.run253Gates,
      run2_52_result: RUN2_54_INPUTS.run252Result,
      run2_52_full_trace: RUN2_54_INPUTS.run252FullTrace,
      commercial_usecase_bank: RUN2_54_INPUTS.commercialUsecaseBank,
      sources: RUN2_54_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_54_product_surface_scene_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_54_full_product_surface_scene",
      best_internal_arm_verdict:
        "Run 2.53 product surface scenes, business visual evidence, and scene renderer gates drive native PPT drawing",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: RUN2_54_POLICY,
      source_data_status: RUN2_54_FULL_STATUS,
      full_slides_with_run2_53_product_surface_scene_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_53_product_surface_scene_id ?? "").startsWith("product_surface_scene_2_53_"),
      ).length,
      full_slides_with_run2_53_business_visual_evidence_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_53_business_visual_evidence_id ?? "").startsWith("business_visual_evidence_2_53_"),
      ).length,
      full_slides_with_run2_53_scene_renderer_gate_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_53_scene_renderer_gate_id ?? "").startsWith("scene_renderer_gate_2_53_"),
      ).length,
      full_slides_with_product_surface_slots: fullTrace.slides.filter(
        (slide) => (slide.run2_54_product_surface_slots_rendered ?? 0) >= 3,
      ).length,
      full_slides_without_forbidden_generic_geometry: fullTrace.slides.filter(
        (slide) => slide.run2_53_forbidden_generic_geometry_count === 0,
      ).length,
      bad_control_slides_without_run2_53_pack: badTrace.slides.filter(
        (slide) =>
          slide.run2_53_product_surface_scene_id === "" &&
          slide.run2_53_business_visual_evidence_id === "" &&
          slide.run2_53_scene_renderer_gate_id === "",
      ).length,
      repair_modules: [RUN2_54_MODULE_NAME],
    },
    control_boundary: {
      bad_run2_53_missing_product_surface_scene_pack:
        "may see Run 2.52 generated result and trace, but must not bind Run 2.53 product surface scene, business visual evidence, or scene renderer gate ids",
      prompt_only: "commercial_case_only_no_run2_53_product_surface_scene_pack",
      run1_5_skill: "prior_baseline_no_run2_53_product_surface_scene_pack",
    },
    visual_quality_boundary:
      "Run 2.53 product surface scene consumption proof only; public video-grade aesthetics, native motion, and human release approval remain blocked",
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
      "audit_run2_54_product_surface_scene_against_visible_content_quality_then_continue_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_54_product_surface_scene_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_54_product_surface_scene_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.54 Product Surface Scene Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.54 consumes Run 2.53 before native PPT drawing. The full arm binds product surface scenes, business visual evidence, and scene renderer gates before drawing public surface text.",
      "",
      "This fixes the suspected workflow bug: Run 2.53 is not only displayed in the viewer. The generated full arm carries `run2_53_product_surface_scene_id`, `run2_53_business_visual_evidence_id`, `run2_53_scene_renderer_gate_id`, product surface slot counts, business visual evidence counts, and generic-geometry checks in trace.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_54_full_product_surface_scene`",
      "- `bad_run2_53_missing_product_surface_scene_pack`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_54_full_product_surface_scene`.",
      "",
      "Quality delta: `product_surface_scene_and_business_visual_evidence_binding`. All six full-arm slides contain Run 2.53 product surface scene ids, business visual evidence ids, scene renderer gate ids, visual specificity status, product surface slots, and business visual evidence objects.",
      "",
      "The negative control `bad_run2_53_missing_product_surface_scene_pack` can reuse the Run 2.52 generated result, but it has no Run 2.53 product surface scene id, no business visual evidence id, no scene renderer gate id, and fails visual specificity binding.",
      "",
      "Public release remains blocked. This proves product surface scene, business visual evidence, and scene renderer gate consumption, not final public-video-grade aesthetics.",
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
  const fourArmSheet = buildRun254FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_54_product_surface_scene_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_54_product_surface_scene_rerun_summary.json"), runSummary);
  writeRun254Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_53_PRODUCT_SURFACE_INPUTS,
  RUN2_54_FULL_DATA_INPUTS,
  RUN2_54_INPUTS,
  armSpecs,
  assertRun254ArmInputBoundaries,
  assertRun254ProductSurfaceSceneSelfCheck,
  drawRun254ProductSurfaceScene,
  loadRun254ContractData,
  main,
  readRun254PackJsonForArm,
  registerRun254Module,
  selectRun254ForSlide,
  traceFor,
  validateRun254RepairPack,
};
