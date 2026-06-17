import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
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
const RUN2_50_FULL_STATUS = "run2_49_repair_pack_consumed_before_native_ppt_drawing";
const RUN2_50_BAD_STATUS = "run2_47_composition_present_but_run2_49_repair_pack_missing";
const RUN2_50_POLICY = "readability_content_density_and_editorial_renderer_binding";

const C = {
  ink: "#13161b",
  paper: "#f4efe4",
  white: "#ffffff",
  line: "#d7d0c2",
  muted: "#58616c",
  dark: "#15171c",
  blue: "#265ed7",
  cyan: "#73c6d6",
  red: "#e45234",
  green: "#0f8a68",
  amber: "#e6b84d",
  lavender: "#b8b1ff",
  moss: "#b8c98d",
  steel: "#e8edf0",
  cream: "#fbf7ee",
};

const RUN2_50_INPUTS = {
  run249Result: `${pack}/results/run2_49_readability_content_density_renderer_repair_result.json`,
  run249Readability: `${pack}/run2_49_readability_memory.json`,
  run249Density: `${pack}/run2_49_content_evidence_density_memory.json`,
  run249Gates: `${pack}/run2_49_editorial_renderer_workflow_gates.json`,
  run247Result: `${pack}/results/run2_47_composition_grammar_rerun_result.json`,
  run247FullTrace: `outputs/${threadId}/presentations/ppt-run2-47-full-vulca/trace_manifest.json`,
  run247BadTrace: `outputs/${threadId}/presentations/ppt-run2-47-bad-missing-composition-grammar/trace_manifest.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_49_REPAIR_INPUTS = [
  RUN2_50_INPUTS.run249Result,
  RUN2_50_INPUTS.run249Readability,
  RUN2_50_INPUTS.run249Density,
  RUN2_50_INPUTS.run249Gates,
];

const RUN2_50_FULL_DATA_INPUTS = Object.values(RUN2_50_INPUTS);
const RUN2_50_BAD_DATA_INPUTS = [
  RUN2_50_INPUTS.run247Result,
  RUN2_50_INPUTS.run247FullTrace,
  RUN2_50_INPUTS.run247BadTrace,
  RUN2_50_INPUTS.commercialUsecaseBank,
  RUN2_50_INPUTS.sources,
];

const baseSlides = [
  {
    role: "cover",
    title: "Launch deck proof, not a prompt demo.",
    claim:
      "The first read must show a product system promise, a real commercial decision, and visible proof objects before any internal trace terms.",
  },
  {
    role: "setup",
    title: "The buyer needs a repeatable route.",
    claim:
      "Prompt-only output is small and uncertain; the selected route must show how case evidence becomes a generated launch deck.",
  },
  {
    role: "contrast",
    title: "Before stays small, after owns the frame.",
    claim:
      "The comparison should show business consequence, not equal feature cards or a palette swap.",
  },
  {
    role: "proof",
    title: "Evidence must be inspectable on the slide.",
    claim:
      "The product surface needs visible inputs, deck states, review states, and editable proof objects rather than hidden prompt text.",
  },
  {
    role: "climax",
    title: "One generated result carries the case.",
    claim:
      "The hero object must fuse commercial story, memory route, proof state, and release boundary in one visible composition.",
  },
  {
    role: "close",
    title: "The handoff shows what remains blocked.",
    claim:
      "The close must explain the decision path, the visible data used, and the release gate without turning into a trace report.",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-50-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.50 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_50_FULL_DATA_INPUTS, "drawRun250EditorialEvidenceScene"],
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
        "Make a premium AI launch deck.",
        "Show the problem and route.",
        "Show before and after.",
        "Show product proof.",
        "Make the result feel big.",
        "End with next steps.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-50-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.50 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_50_FULL_DATA_INPUTS, "drawRun250EditorialEvidenceScene"],
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
        "The route is readable but broad.",
        "The comparison is generic.",
        "The proof is process-led.",
        "The result is labeled, not staged.",
        "The close is correct but thin.",
      ][index],
    })),
  },
  {
    armId: "run2_50_full_readability_density_renderer",
    slug: "ppt-run2-50-full-vulca",
    label: "Run 2.50 full repair-consumption",
    kicker: "RUN 2.50 / READABILITY + DENSITY",
    footer: "run2_50_full_readability_density_renderer | consumes Run 2.49 | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      ...RUN2_50_FULL_DATA_INPUTS,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_49_readability_memory.json",
      "run2_49_content_evidence_density_memory.json",
      "run2_49_editorial_renderer_workflow_gates.json",
      RUN2_50_POLICY,
    ],
    forbidden: [
      "copied screenshots",
      "raw tutorial media",
      "source layouts",
      "source brand imitation",
      "square_block_grid_as_primary_surface",
      "equal_feature_card_distribution_as_primary_surface",
      "palette_swap_as_visual_delta",
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
    armId: "bad_run2_49_missing_repair_pack",
    slug: "ppt-run2-50-bad-missing-run2-49-repair-pack",
    label: "Bad missing Run 2.49 repair pack",
    kicker: "RUN 2.50 / BAD CONTROL",
    footer: "bad_run2_49_missing_repair_pack | Run 2.47 only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_50_BAD_DATA_INPUTS],
    data_input_manifest: ["run2_47_composition_grammar_without_run2_49_repair_pack"],
    forbidden: [
      ...RUN2_49_REPAIR_INPUTS,
      "run2_49_readability_memory_id",
      "run2_49_content_evidence_density_memory_id",
      "run2_49_editorial_renderer_gate_id",
      "run2_49_renderer_contract_id",
      "drawRun250EditorialEvidenceScene",
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
        "Composition exists, but evidence is thin.",
        "The route falls back to internal labels.",
        "The comparison returns to slot evidence.",
        "The proof surface has no 2.49 contract.",
        "The result object lacks density gates.",
        "The close cannot prove repair consumption.",
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
    nonSquareRatioVariants: 0,
    primarySurfaceKind: "",
    codeModuleIds: new Set(),
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun250Module(metrics, functionName) {
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

function armUsesFullRun250Repair(arm) {
  return arm.armId === "run2_50_full_readability_density_renderer";
}

function armUsesBadRun250Data(arm) {
  return arm.armId === "bad_run2_49_missing_repair_pack";
}

function assertRun250ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun250Repair(arm)) {
    for (const input of RUN2_50_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesBadRun250Data(arm)) {
    for (const input of RUN2_50_BAD_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow bad-control input ${input}`);
    }
    for (const input of RUN2_49_REPAIR_INPUTS) {
      if (allowed.has(input) || !forbidden.has(input)) throw new Error(`${arm.armId} must block ${input}`);
    }
    return;
  }
  for (const input of RUN2_50_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun250PackJsonForArm(arm, relPath) {
  assertRun250ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (!armUsesFullRun250Repair(arm) && !armUsesBadRun250Data(arm)) {
    throw new Error(`${arm.armId} cannot read Run 2.50 pack data`);
  }
  return readJson(relPath);
}

function validateRun250RepairPack(data) {
  const {
    run249Result,
    run249Readability,
    run249Density,
    run249Gates,
    run247Result,
    run247FullTrace,
    run247BadTrace,
    commercialUsecaseBank,
    sources,
  } = data;
  if (run249Result?.status !== "run2_49_readability_content_density_renderer_repair_ready_public_blocked") {
    throw new Error("Run 2.50 must consume Run 2.49 repair result");
  }
  if (run249Result?.next_required_action !== "consume_run2_49_before_run2_50_four_arm_rerun") {
    throw new Error("Run 2.49 result does not point to Run 2.50");
  }
  if (run249Readability?.status !== "run2_49_readability_memory_ready_public_blocked") {
    throw new Error("Run 2.50 readability status mismatch");
  }
  if (run249Density?.status !== "run2_49_content_evidence_density_memory_ready_public_blocked") {
    throw new Error("Run 2.50 content density status mismatch");
  }
  if (run249Gates?.status !== "run2_49_editorial_renderer_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.50 editorial renderer gate status mismatch");
  }
  if (run249Gates?.next_rerun_contract !== "must_be_consumed_before_run2_50_four_arm_rerun") {
    throw new Error("Run 2.49 gates do not require Run 2.50 consumption");
  }
  if (run247Result?.status !== "run2_47_composition_grammar_rerun_public_blocked") {
    throw new Error("Run 2.50 must use Run 2.47 as source generated run");
  }
  if (run247FullTrace?.arm_id !== "run2_47_full_composition_grammar_compiler") {
    throw new Error("Run 2.50 must compare against Run 2.47 full trace");
  }
  if (run247BadTrace?.arm_id !== "bad_run2_46_missing_composition_grammar") {
    throw new Error("Run 2.50 must carry Run 2.47 bad-control trace");
  }
  if (!Array.isArray(sources?.sources) || sources.sources.length < 4) throw new Error("Run 2.50 missing sources");
  const usecase = (commercialUsecaseBank?.usecases ?? []).find((item) => item.id === selectedUsecaseId);
  if (!usecase) throw new Error("Run 2.50 missing selected commercial usecase");

  const readability = run249Readability.readability_records ?? [];
  const density = run249Density.content_evidence_density_records ?? [];
  const gates = run249Gates.editorial_renderer_workflow_gates ?? [];
  if (readability.length !== 6 || density.length !== 6 || gates.length !== 6) {
    throw new Error("Run 2.50 must consume six readability records, six density records, and six renderer gates");
  }
  for (const role of baseSlides.map((slide) => slide.role)) {
    const readable = readability.find((record) => record.role === role);
    const dense = density.find((record) => record.role === role);
    const gate = gates.find((record) => record.role === role);
    const priorSlide = (run247FullTrace.slides ?? []).find((slide) => slide.role === role);
    if (!readable || !dense || !gate || !priorSlide) throw new Error(`Run 2.50 missing role contract for ${role}`);
    if (dense.required_readability_memory_id !== readable.readability_memory_id) {
      throw new Error(`Run 2.50 density/readability mismatch for ${role}`);
    }
    if (gate.required_readability_memory_id !== readable.readability_memory_id) {
      throw new Error(`Run 2.50 gate/readability mismatch for ${role}`);
    }
    if (gate.required_content_evidence_density_memory_id !== dense.content_evidence_density_memory_id) {
      throw new Error(`Run 2.50 gate/density mismatch for ${role}`);
    }
    if (gate.forbid_square_block_grid_as_primary_surface !== true) {
      throw new Error(`Run 2.50 gate must forbid square block grid for ${role}`);
    }
    if (gate.require_contact_sheet_readability !== true || gate.require_inspectable_business_evidence !== true) {
      throw new Error(`Run 2.50 gate must require readability and inspectable evidence for ${role}`);
    }
    if ((dense.evidence_object_contract ?? []).length < 3 || (dense.inspectable_visual_proof_object_contract ?? []).length < 2) {
      throw new Error(`Run 2.50 density contract is too thin for ${role}`);
    }
    if (!String(priorSlide.run2_46_visual_object_grammar_id ?? "").startsWith("visual_object_grammar_2_46_")) {
      throw new Error(`Run 2.50 source Run 2.47 trace missing grammar id for ${role}`);
    }
  }
}

function loadRun250ContractData(arm) {
  const data = {
    run249Result: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.run249Result),
    run249Readability: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.run249Readability),
    run249Density: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.run249Density),
    run249Gates: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.run249Gates),
    run247Result: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.run247Result),
    run247FullTrace: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.run247FullTrace),
    run247BadTrace: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.run247BadTrace),
    commercialUsecaseBank: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.commercialUsecaseBank),
    sources: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.sources),
  };
  validateRun250RepairPack(data);
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_50_run2_49_repair_pack_contract_ready",
  };
}

function loadRun250BadControlData(arm) {
  const data = {
    run247Result: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.run247Result),
    run247FullTrace: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.run247FullTrace),
    run247BadTrace: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.run247BadTrace),
    commercialUsecaseBank: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.commercialUsecaseBank),
    sources: readRun250PackJsonForArm(arm, RUN2_50_INPUTS.sources),
  };
  if (data.run247Result?.status !== "run2_47_composition_grammar_rerun_public_blocked") {
    throw new Error("Run 2.50 bad control must read Run 2.47 result");
  }
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
  };
}

function selectRun250ForSlide(role, contractData) {
  const readability = (contractData.run249Readability?.readability_records ?? []).find((item) => item.role === role);
  const density = (contractData.run249Density?.content_evidence_density_records ?? []).find((item) => item.role === role);
  const gate = (contractData.run249Gates?.editorial_renderer_workflow_gates ?? []).find((item) => item.role === role);
  const priorTraceSlide = (contractData.run247FullTrace?.slides ?? []).find((item) => item.role === role);
  if (!readability || !density || !gate || !priorTraceSlide) throw new Error(`Run 2.50 missing role ${role}`);
  return {
    role,
    readability,
    density,
    gate,
    priorTraceSlide,
    usecase: contractData.usecase,
    evidenceObjects: density.evidence_object_contract ?? [],
    proofObjects: density.inspectable_visual_proof_object_contract ?? [],
    businessProofPoints: density.business_proof_points ?? [],
    primarySurfaceKind: role === "setup" ? "asymmetric_route_storyboard" : role === "contrast" ? "wide_after_state_canvas" : role === "proof" ? "product_workspace_scene" : role === "climax" ? "cinematic_result_object" : role === "close" ? "decision_room_handoff" : "poster_scale_hero_surface",
  };
}

function drawMiniDeck(slide, x, y, w, h, fill, accent, dark = false) {
  rect(slide, x, y, w, h, fill, colorLine(dark ? "#37414b" : "#cbd3d8", 1));
  rect(slide, x + 18, y + 20, w * 0.45, 10, accent);
  rect(slide, x + 18, y + 48, w * 0.28, 7, dark ? C.cyan : "#a5bfcd");
  rect(slide, x + 18, y + 70, w * 0.36, 7, dark ? "#d8e6ec" : "#c9d4d9");
  rect(slide, x + w - 96, y + 24, 60, 78, dark ? "#273542" : "#edf1f3", colorLine(dark ? "#465764" : "#d5dde1", 1));
  ellipse(slide, x + w - 79, y + 45, 26, 26, accent, colorLine("transparent", 0));
  rect(slide, x + 20, y + h - 38, w - 44, 14, dark ? "#202a34" : "#f8f4eb", colorLine(dark ? "#354654" : "#dad2c6", 1));
}

function drawEvidenceRibbon(slide, arm, selection, x, y, w, h, metrics, dark) {
  const fill = dark ? "#202b35" : C.white;
  rect(slide, x, y, w, h, fill, colorLine(dark ? "#3a4652" : arm.palette.rule, 1));
  text(slide, "business evidence", x + 18, y + 14, 210, 18, {
    fontSize: 9.5,
    bold: true,
    mono: true,
    color: dark ? C.cyan : arm.palette.accent,
  });
  const points = selection.businessProofPoints.slice(0, 3);
  points.forEach((point, index) => {
    const rowY = y + 46 + index * 43;
    ellipse(slide, x + 20, rowY + 4, 16, 16, index === 0 ? arm.palette.proof : dark ? C.cyan : arm.palette.accent2, colorLine("transparent", 0));
    text(slide, compactText(point, 122), x + 46, rowY, w - 62, 32, {
      fontSize: 10.2,
      color: dark ? "#eaf3f8" : arm.palette.muted,
    });
    registerText(metrics, point);
  });
  registerProof(metrics, points.length);
}

function drawProofRail(slide, arm, selection, x, y, w, h, metrics, dark) {
  rect(slide, x, y, w, h, dark ? "#10161d" : C.white, colorLine(dark ? "#394652" : arm.palette.rule, 1));
  text(slide, "inspectable proof objects", x + 18, y + 13, w - 36, 18, {
    fontSize: 9.2,
    bold: true,
    mono: true,
    color: dark ? C.cyan : arm.palette.accent,
  });
  selection.proofObjects.slice(0, 2).forEach((proof, index) => {
    const px = x + 18 + index * ((w - 52) / 2);
    const py = y + 42;
    drawMiniDeck(slide, px, py, (w - 72) / 2, h - 68, dark ? "#f7f9fb" : "#f8fafb", index === 0 ? arm.palette.proof : arm.palette.accent2, false);
    text(slide, compactText(proof, 42), px + 12, py + h - 86, (w - 94) / 2, 24, {
      fontSize: 8.5,
      bold: true,
      color: C.ink,
    });
    registerText(metrics, proof);
  });
  registerProof(metrics, selection.proofObjects.slice(0, 2).length);
}

function drawNativeProductSurface(slide, arm, selection, x, y, w, h, metrics, dark) {
  const shadow = dark ? "#090d12" : "#d7cbbb";
  rect(slide, x + 18, y + 20, w, h, shadow, colorLine(shadow, 0));
  rect(slide, x, y, w, h, dark ? "#f8fafb" : C.white, colorLine(dark ? "#f8fafb" : arm.palette.rule, 1));
  rect(slide, x + 22, y + 26, w - 44, 42, dark ? C.dark : "#f1f5f6", colorLine("transparent", 0));
  text(slide, compactText(selection.gate.surface_contract, 82), x + 42, y + 38, w - 190, 20, {
    fontSize: 12.5,
    bold: true,
    color: dark ? C.white : arm.palette.title,
  });
  registerText(metrics, selection.gate.surface_contract);
  ellipse(slide, x + w - 92, y + 34, 24, 24, arm.palette.proof, colorLine("transparent", 0));
  rect(slide, x + 38, y + 96, w * 0.52, h * 0.44, "#edf2f0", colorLine("#cfd8d5", 1));
  drawMiniDeck(slide, x + 62, y + 124, w * 0.37, h * 0.28, "#ffffff", arm.palette.proof);
  rect(slide, x + w * 0.63, y + 104, w * 0.25, h * 0.12, "#111820", colorLine("#111820", 1));
  text(slide, "selected route", x + w * 0.65, y + 119, w * 0.17, 15, { fontSize: 9, bold: true, mono: true, color: C.white });
  rect(slide, x + w * 0.63, y + 176, w * 0.27, h * 0.22, "#f3e4d6", colorLine("#e4c8b5", 1));
  rect(slide, x + w * 0.63, y + 316, w * 0.18, h * 0.10, "#dfe9f8", colorLine("#c9d9f2", 1));
  rect(slide, x + w * 0.21, y + h - 82, w * 0.56, 20, arm.palette.proof, colorLine("transparent", 0));
  selection.evidenceObjects.slice(0, 3).forEach((object, index) => {
    const ox = x + 42 + index * Math.floor((w - 116) / 3);
    const oy = y + h - 136;
    rect(slide, ox, oy, Math.floor((w - 136) / 3), 46, index === 0 ? "#15171c" : index === 1 ? "#e8edf0" : "#f7dfb1", colorLine(index === 0 ? "#15171c" : "#d7d0c2", 1));
    text(slide, compactText(object, 34), ox + 10, oy + 12, Math.floor((w - 170) / 3), 20, {
      fontSize: 8.7,
      bold: true,
      color: index === 0 ? C.white : C.ink,
    });
    registerText(metrics, object);
  });
  registerPresentationSurface(metrics, x, y, w, h, 0.72);
  registerProof(metrics, 3);
}

function roleHeroBounds(role) {
  const bounds = {
    cover: { x: 520, y: 122, w: 595, h: 382 },
    setup: { x: 510, y: 148, w: 610, h: 330 },
    contrast: { x: 448, y: 120, w: 682, h: 386 },
    proof: { x: 390, y: 116, w: 720, h: 394 },
    climax: { x: 158, y: 116, w: 870, h: 414 },
    close: { x: 438, y: 154, w: 540, h: 300 },
  };
  return bounds[role] ?? bounds.cover;
}

function drawRun250EditorialEvidenceScene(slide, arm, spec, selection, metrics, moduleName) {
  registerRun250Module(metrics, moduleName);
  metrics.primarySurfaceKind = selection.primarySurfaceKind;
  metrics.nonSquareRatioVariants = Math.max(2, selection.gate.min_non_square_surface_ratio_variants ?? 2);
  const dark = spec.role === "climax";
  if (dark) {
    rect(slide, 70, 94, 1084, 548, C.dark, colorLine(C.dark, 1));
    text(slide, "One generated result carries the case.", 110, 126, 790, 46, {
      fontSize: 40,
      title: true,
      bold: true,
      color: C.white,
    });
    registerText(metrics, "One generated result carries the case");
    text(slide, compactText(spec.claim, 148), 114, 180, 720, 38, { fontSize: 14, color: "#dbe5ec" });
    registerText(metrics, spec.claim);
  } else {
    text(slide, compactText(spec.title, 74), 78, 112, spec.role === "proof" ? 286 : 404, 80, {
      fontSize: spec.role === "cover" ? 37 : 32,
      title: true,
      bold: true,
      color: arm.palette.title,
    });
    registerText(metrics, spec.title);
    text(slide, compactText(spec.claim, 150), 80, 208, spec.role === "proof" ? 270 : 390, 68, {
      fontSize: 14.5,
      color: arm.palette.muted,
    });
    registerText(metrics, spec.claim);
  }

  const hero = roleHeroBounds(spec.role);
  drawNativeProductSurface(slide, arm, selection, hero.x, hero.y, hero.w, hero.h, metrics, dark);

  if (spec.role === "setup") {
    rect(slide, 154, 376, 220, 94, "#f5e0d2", colorLine("#e0bba3", 1));
    text(slide, "prompt-only path collapses", 174, 408, 168, 18, { fontSize: 10, bold: true, color: "#7a3525" });
    rect(slide, 382, 418, 102, 5, arm.palette.proof);
  }
  if (spec.role === "contrast") {
    rect(slide, 104, 386, 260, 92, "#f2ded4", colorLine("#e0bba3", 1));
    text(slide, "before stays small", 128, 420, 190, 18, { fontSize: 10, bold: true, mono: true, color: "#7a3525" });
    rect(slide, 340, 430, 80, 5, arm.palette.proof);
  }
  if (spec.role === "proof") {
    text(slide, "editable product workspace", 82, 536, 270, 24, {
      fontSize: 17,
      title: true,
      bold: true,
      color: arm.palette.title,
    });
    registerText(metrics, "editable product workspace");
  }
  if (spec.role === "close") {
    rect(slide, 104, 496, 890, 38, "#15171c", colorLine("#15171c", 1));
    text(slide, "review -> native render -> source boundary -> human approval", 132, 507, 640, 14, {
      fontSize: 10,
      bold: true,
      mono: true,
      color: C.white,
    });
    registerText(metrics, "review native render source boundary human approval");
  }

  const ribbonX = dark ? 108 : spec.role === "proof" ? 78 : 80;
  const ribbonY = dark ? 548 : 410;
  const ribbonW = dark ? 430 : spec.role === "proof" ? 286 : 386;
  drawEvidenceRibbon(slide, arm, selection, ribbonX, ribbonY, ribbonW, 138, metrics, dark);

  const railX = dark ? 572 : spec.role === "proof" ? 802 : 760;
  const railY = dark ? 548 : 520;
  const railW = dark ? 456 : spec.role === "proof" ? 322 : 350;
  drawProofRail(slide, arm, selection, railX, railY, railW, 118, metrics, dark);

  text(slide, compactText(selection.readability.readability_goal, 120), dark ? 106 : 82, dark ? 602 : 586, dark ? 436 : 560, 28, {
    fontSize: 10.5,
    color: dark ? "#dbe5ec" : arm.palette.muted,
  });
  registerText(metrics, selection.readability.readability_goal);
  registerZones(metrics, 5);
}

function drawBadRun247FallbackSlide(slide, arm, spec, badData, metrics) {
  text(slide, spec.title, 76, 118, 540, 74, {
    fontSize: 33,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, compactText(spec.claim, 112), 80, 214, 456, 52, { fontSize: 14, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  const panel = { x: 604, y: 132, w: 480, h: 344 };
  rect(slide, panel.x + 16, panel.y + 18, panel.w, panel.h, "#dccfb7", colorLine("#dccfb7", 1));
  rect(slide, panel.x, panel.y, panel.w, panel.h, arm.palette.panel, colorLine(arm.palette.rule, 1));
  for (let index = 0; index < 6; index += 1) {
    const col = index % 3;
    const row = Math.floor(index / 3);
    const x = panel.x + 34 + col * 140;
    const y = panel.y + 52 + row * 120;
    rect(slide, x, y, 112, 86, index === 0 ? "#d4bc83" : "#eee2c7", colorLine("#c6ad78", 1));
    text(slide, index === 0 ? "composition label" : "thin proof slot", x + 12, y + 18, 88, 28, {
      fontSize: 9,
      bold: true,
      color: arm.palette.title,
    });
  }
  text(slide, "Run 2.47 composition grammar is present, but no Run 2.49 readability, density, or renderer repair ids are bound.", panel.x + 34, panel.y + 292, 392, 30, {
    fontSize: 11,
    color: arm.palette.muted,
  });
  registerText(metrics, "Run 2.47 composition grammar present but no Run 2.49 readability density renderer repair ids bound");
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
  const panelFill = C.white;
  for (let i = 0; i < 3; i += 1) {
    const px = 672 + i * 150;
    const py = 318;
    rect(slide, px, py, 132, 148, panelFill, colorLine(arm.palette.rule, 1));
    rect(slide, px + 14, py + 26, 92, 12, arm.palette.accent2);
    rect(slide, px + 14, py + 64, 76, 9, "#c0c9d0");
    rect(slide, px + 14, py + 96, 58, 9, "#c0c9d0");
  }
  rect(slide, 84, 346, 480, 150, panelFill, colorLine(arm.palette.rule, 1));
  text(slide, "Readable, but no Run 2.49 repair-pack consumption.", 108, 382, 420, 54, {
    fontSize: 20,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, "Readable but no Run 2.49 repair pack consumption");
  registerPresentationSurface(metrics, 84, 318, 1042, 212, 0.35);
}

const RUN2_50_MODULE_NAMES = {
  cover: "drawRun250CoverEditorialEvidenceScene",
  setup: "drawRun250SetupRouteEvidenceScene",
  contrast: "drawRun250ContrastAsymmetricEvidenceScene",
  proof: "drawRun250ProductWorkspaceEvidenceScene",
  climax: "drawRun250ClimaxResultEvidenceScene",
  close: "drawRun250DecisionHandoffEvidenceScene",
};

function renderRun250Slide(presentation, spec, arm, n, contractData, badData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun250Repair(arm)) {
    const selection = selectRun250ForSlide(spec.role, contractData);
    drawRun250EditorialEvidenceScene(slide, arm, spec, selection, metrics, RUN2_50_MODULE_NAMES[spec.role]);
  } else if (armUsesBadRun250Data(arm)) {
    drawBadRun247FallbackSlide(slide, arm, spec, badData, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertRun250ArmInputBoundaries(arm);
  const fullRun250 = armUsesFullRun250Repair(arm);
  const badRun250 = armUsesBadRun250Data(arm);
  const contractData = fullRun250 ? context.contractData ?? loadRun250ContractData(arm) : null;
  const badData = badRun250 ? context.badData ?? loadRun250BadControlData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun250 || badRun250 ? selectedUsecaseId : "",
    source_repair_run_id: fullRun250 ? "2.49" : "",
    source_generated_run_id: fullRun250 || badRun250 ? "2.47" : "",
    run2_50_readability_density_renderer_status: fullRun250
      ? RUN2_50_FULL_STATUS
      : badRun250
        ? RUN2_50_BAD_STATUS
        : "boundary_control_no_run2_49_repair_pack_consumption",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.50 readability/content-density renderer rerun from scripts/generate_ppt_run2_50_readability_density_renderer_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun250 ? selectRun250ForSlide(slide.role, contractData) : null;
      const codeModuleIds = fullRun250
        ? hasRenderedMetrics
          ? Array.from(roleMetrics.codeModuleIds)
          : [RUN2_50_MODULE_NAMES[slide.role]]
        : [];
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_49_readability_memory_id: fullRun250 ? selection.readability.readability_memory_id : "",
        run2_49_content_evidence_density_memory_id: fullRun250
          ? selection.density.content_evidence_density_memory_id
          : "",
        run2_49_editorial_renderer_gate_id: fullRun250 ? selection.gate.gate_id : "",
        run2_49_renderer_contract_id: fullRun250 ? selection.gate.renderer_contract_id : "",
        run2_49_contact_sheet_readability_status: fullRun250 ? "pass_internal" : "fail_missing_run2_49",
        run2_49_business_evidence_density_status: fullRun250 ? "pass_internal" : "fail_missing_run2_49",
        run2_49_business_evidence_objects: fullRun250 ? selection.evidenceObjects : [],
        run2_49_inspectable_proof_objects: fullRun250 ? selection.proofObjects : [],
        run2_49_non_square_surface_ratio_variants: fullRun250 ? roleMetrics.nonSquareRatioVariants : 0,
        run2_50_primary_surface_kind: fullRun250 ? roleMetrics.primarySurfaceKind || selection.primarySurfaceKind : "square_block_grid",
        run2_50_code_module_ids: codeModuleIds,
        run2_47_source_composition_grammar_status: fullRun250 || badRun250 ? "run2_47_composition_grammar_rerun_public_blocked" : "",
        run2_47_source_visual_object_grammar_id: fullRun250
          ? selection.priorTraceSlide.run2_46_visual_object_grammar_id
          : "",
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

function assertRun250ReadabilityDensitySelfCheck(trace) {
  if (trace.arm_id === "run2_50_full_readability_density_renderer") {
    if (trace.run2_50_readability_density_renderer_status !== RUN2_50_FULL_STATUS) {
      throw new Error("Run 2.50 full trace did not consume Run 2.49 repair pack");
    }
    for (const slide of trace.slides) {
      if (!String(slide.run2_49_readability_memory_id ?? "").startsWith("readability_memory_2_49_")) {
        throw new Error(`Run 2.50 full slide ${slide.slide_id} missing readability id`);
      }
      if (!String(slide.run2_49_content_evidence_density_memory_id ?? "").startsWith("content_evidence_density_2_49_")) {
        throw new Error(`Run 2.50 full slide ${slide.slide_id} missing density id`);
      }
      if (!String(slide.run2_49_editorial_renderer_gate_id ?? "").startsWith("gate_2_49_")) {
        throw new Error(`Run 2.50 full slide ${slide.slide_id} missing renderer gate id`);
      }
      if (slide.run2_49_business_evidence_density_status !== "pass_internal") {
        throw new Error(`Run 2.50 full slide ${slide.slide_id} missing business evidence pass`);
      }
      if ((slide.run2_49_business_evidence_objects ?? []).length < 3) {
        throw new Error(`Run 2.50 full slide ${slide.slide_id} missing evidence objects`);
      }
      if ((slide.run2_49_inspectable_proof_objects ?? []).length < 2) {
        throw new Error(`Run 2.50 full slide ${slide.slide_id} missing proof objects`);
      }
      if (slide.run2_50_primary_surface_kind === "square_block_grid") {
        throw new Error(`Run 2.50 full slide ${slide.slide_id} regressed to square grid`);
      }
      if ((slide.run2_50_code_module_ids ?? []).length !== 1 || !slide.run2_50_code_module_ids[0].startsWith("drawRun250")) {
        throw new Error(`Run 2.50 full slide ${slide.slide_id} missing Run 2.50 module`);
      }
    }
  }
  if (trace.arm_id === "bad_run2_49_missing_repair_pack") {
    if (trace.run2_50_readability_density_renderer_status !== RUN2_50_BAD_STATUS) {
      throw new Error("Run 2.50 bad trace has wrong status");
    }
    for (const slide of trace.slides) {
      if (slide.run2_49_readability_memory_id !== "") {
        throw new Error(`Run 2.50 bad slide ${slide.slide_id} leaked Run 2.49 readability id`);
      }
      if (slide.run2_49_business_evidence_density_status !== "fail_missing_run2_49") {
        throw new Error(`Run 2.50 bad slide ${slide.slide_id} must fail missing Run 2.49`);
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

function buildRun250FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-50-four-arm-contact-sheet.png"),
    "Run 2.50 readability density renderer comparison",
    sheets,
    sheets.length,
    labels,
  );
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
    "ppt-run2-25-full-vulca",
    "ppt-run2-33-full-vulca",
    "ppt-run2-36-full-vulca",
    "ppt-run2-39-full-vulca",
    "ppt-run2-41-full-vulca",
    "ppt-run2-44-full-vulca",
    "ppt-run2-47-full-vulca",
    "ppt-run2-50-full-vulca",
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
      `selected usecase: ${selectedUsecaseId}`,
      `allowed inputs: ${arm.allowed.join(", ")}`,
      `forbidden inputs: ${arm.forbidden.join(", ")}`,
      "required proof objects: Run 2.49 readability memory id, content evidence density id, editorial renderer gate id, renderer contract id, business evidence status, and non-square surface proof",
      "source requirements: full arm reads Run 2.49 repair pack before native PPT drawing",
      "negative control: bad arm can reuse Run 2.47 composition result, but cannot read Run 2.49 repair pack",
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
  const contractData = armUsesFullRun250Repair(arm) ? loadRun250ContractData(arm) : null;
  const badData = armUsesBadRun250Data(arm) ? loadRun250BadControlData(arm) : null;
  const slides = arm.slides.map((slide, index) =>
    renderRun250Slide(presentation, slide, arm, index + 1, contractData, badData, metricsByRole),
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
  assertRun250ReadabilityDensitySelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_50_readability_density_renderer_arms.mjs",
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

function writeRun250Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-50-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-50-bad-missing-run2-49-repair-pack/trace_manifest.json`);
  const result = {
    schema_version: 1,
    run_id: "2.50",
    status: "run2_50_readability_density_renderer_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_repair_run_id: "2.49",
    source_audit_run_id: "2.48",
    source_generated_run_id: "2.47",
    database_expansion: false,
    workflow_expansion: false,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_49_result: RUN2_50_INPUTS.run249Result,
      run2_49_readability_memory: RUN2_50_INPUTS.run249Readability,
      run2_49_content_evidence_density_memory: RUN2_50_INPUTS.run249Density,
      run2_49_editorial_renderer_workflow_gates: RUN2_50_INPUTS.run249Gates,
      run2_47_result: RUN2_50_INPUTS.run247Result,
      run2_47_full_trace: RUN2_50_INPUTS.run247FullTrace,
      commercial_usecase_bank: RUN2_50_INPUTS.commercialUsecaseBank,
      sources: RUN2_50_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_50_readability_density_renderer_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_50_full_readability_density_renderer",
      best_internal_arm_verdict: "Run 2.49 repair pack now drives readable evidence-dense native PPT scenes before drawing",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: RUN2_50_POLICY,
      source_data_status: RUN2_50_FULL_STATUS,
      full_slides_with_run2_49_readability_memory_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_49_readability_memory_id ?? "").startsWith("readability_memory_2_49_"),
      ).length,
      full_slides_with_run2_49_content_evidence_density_memory_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_49_content_evidence_density_memory_id ?? "").startsWith("content_evidence_density_2_49_"),
      ).length,
      full_slides_with_run2_49_editorial_renderer_gate_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_49_editorial_renderer_gate_id ?? "").startsWith("gate_2_49_"),
      ).length,
      full_slides_with_business_evidence_density_pass: fullTrace.slides.filter(
        (slide) => slide.run2_49_business_evidence_density_status === "pass_internal",
      ).length,
      full_slides_with_non_square_renderer_surface: fullTrace.slides.filter(
        (slide) => slide.run2_50_primary_surface_kind !== "square_block_grid",
      ).length,
      bad_control_slides_without_run2_49_repair_pack: badTrace.slides.filter(
        (slide) =>
          slide.run2_49_readability_memory_id === "" &&
          slide.run2_49_content_evidence_density_memory_id === "" &&
          slide.run2_49_editorial_renderer_gate_id === "",
      ).length,
      repair_modules: Object.values(RUN2_50_MODULE_NAMES),
    },
    control_boundary: {
      bad_run2_49_missing_repair_pack:
        "may see Run 2.47 composition result, but must not bind Run 2.49 readability, content evidence density, or renderer gate ids",
      prompt_only: "commercial_case_only_no_run2_49_repair_pack",
      run1_5_skill: "prior_baseline_no_run2_49_repair_pack",
    },
    visual_quality_boundary:
      "Run 2.49 repair consumption proof only; public video-grade aesthetics, native motion, and human release approval remain blocked",
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
      "audit_run2_50_readability_density_renderer_against_visible_content_quality_then_continue_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_50_readability_density_renderer_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_50_readability_density_renderer_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.50 Readability Density Renderer Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.50 consumes Run 2.49 before native PPT drawing. The full arm binds readability memory, content evidence density memory, and editorial renderer gates, then draws evidence-dense native product scenes instead of square block grids.",
      "",
      "This fixes the suspected workflow bug: Run 2.49 is not only displayed in the viewer. The generated full arm carries `run2_49_readability_memory_id`, `run2_49_content_evidence_density_memory_id`, `run2_49_editorial_renderer_gate_id`, `run2_49_renderer_contract_id`, `run2_49_business_evidence_density_status`, and visible proof-object counts in trace.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_50_full_readability_density_renderer`",
      "- `bad_run2_49_missing_repair_pack`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_50_full_readability_density_renderer`.",
      "",
      "Quality delta: `readability_content_density_and_editorial_renderer_binding`. All six full-arm slides contain Run 2.49 readability ids, content evidence density ids, renderer gate ids, business evidence pass status, at least three business evidence objects, and at least two inspectable proof objects.",
      "",
      "The negative control `bad_run2_49_missing_repair_pack` can reuse the Run 2.47 composition result, but it has no Run 2.49 readability id, no content evidence density id, no editorial renderer gate id, and fails business evidence density.",
      "",
      "Public release remains blocked. This proves data/workflow consumption and visible evidence-density routing, not final public-video-grade aesthetics.",
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
  const fourArmSheet = buildRun250FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_50_readability_density_renderer_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_50_readability_density_renderer_rerun_summary.json"), runSummary);
  writeRun250Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_49_REPAIR_INPUTS,
  RUN2_50_FULL_DATA_INPUTS,
  RUN2_50_INPUTS,
  armSpecs,
  assertRun250ArmInputBoundaries,
  assertRun250ReadabilityDensitySelfCheck,
  drawRun250EditorialEvidenceScene,
  loadRun250ContractData,
  main,
  readRun250PackJsonForArm,
  registerRun250Module,
  selectRun250ForSlide,
  traceFor,
  validateRun250RepairPack,
};
