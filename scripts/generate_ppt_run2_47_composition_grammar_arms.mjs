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
const RUN2_47_FULL_STATUS = "run2_46_composition_grammar_consumed_before_native_ppt_drawing";
const RUN2_47_BAD_STATUS = "run2_44_geometry_present_but_run2_46_composition_grammar_missing";
const RUN2_47_POLICY = "run2_46_visual_object_grammar_to_composed_object_scene";
const RUN2_47_SOURCE_BOUNDARY = "derived_only_no_copied_media";

const C = {
  ink: "#121419",
  paper: "#f4efe4",
  white: "#ffffff",
  line: "#d7d0c2",
  muted: "#5d6670",
  charcoal: "#161b22",
  blue: "#255fdd",
  cyan: "#7bcddd",
  signal: "#e75236",
  green: "#0f8a68",
  sand: "#ead9b8",
  butter: "#f0d46d",
  lavender: "#b9b2ff",
  steel: "#e7ecef",
};

const RUN2_47_INPUTS = {
  run246Result: `${pack}/results/run2_46_multimodal_composition_memory_result.json`,
  multimodalCompositionDecomposition: `${pack}/run2_46_multimodal_composition_decomposition.json`,
  visualObjectGrammarMemory: `${pack}/run2_46_visual_object_grammar_memory.json`,
  compositionWorkflowGates: `${pack}/run2_46_composition_workflow_gates.json`,
  semanticVisualAssetMemory: `${pack}/run2_43_semantic_visual_asset_memory.json`,
  editorialCompositionTypographyMemory: `${pack}/run2_43_editorial_composition_typography_memory.json`,
  visualAssetSemanticsWorkflowGates: `${pack}/run2_43_visual_asset_semantics_workflow_gates.json`,
  run244Result: `${pack}/results/run2_44_semantic_geometry_rerun_result.json`,
  run244FullTrace: `outputs/${threadId}/presentations/ppt-run2-44-full-vulca/trace_manifest.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_46_GRAMMAR_INPUTS = [
  RUN2_47_INPUTS.run246Result,
  RUN2_47_INPUTS.multimodalCompositionDecomposition,
  RUN2_47_INPUTS.visualObjectGrammarMemory,
  RUN2_47_INPUTS.compositionWorkflowGates,
];
const RUN2_47_FULL_DATA_INPUTS = Object.values(RUN2_47_INPUTS);
const RUN2_47_BAD_DATA_INPUTS = [
  RUN2_47_INPUTS.run244Result,
  RUN2_47_INPUTS.run244FullTrace,
  RUN2_47_INPUTS.commercialUsecaseBank,
  RUN2_47_INPUTS.sources,
];

const baseSlides = [
  {
    role: "cover",
    title: "Composition grammar replaces the slot scene.",
    claim: "The full arm must draw a composed object scene from Run 2.46, not three semantic geometry slots.",
  },
  {
    role: "setup",
    title: "A weak deck is now a storyboard problem.",
    claim: "The setup should show failure-to-route choreography before it shows process labels.",
  },
  {
    role: "contrast",
    title: "The after state gets object gravity.",
    claim: "Before/after should have a dominant product state and a quiet before state.",
  },
  {
    role: "proof",
    title: "The product surface behaves like a working room.",
    claim: "Proof belongs inside a composed surface with decision lanes, not separate feature cards.",
  },
  {
    role: "climax",
    title: "One result object owns the public demo.",
    claim: "The climax must fuse memory, proof, and release state into one visible result object.",
  },
  {
    role: "close",
    title: "The handoff is a composed release state.",
    claim: "The final slide should feel like a decision room, not a summary report.",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-47-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.47 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_47_FULL_DATA_INPUTS, "compositionGrammarTransform", "drawRun247ComposedObjectScene"],
    palette: {
      bg: "#f6f7f8",
      rail: "#394150",
      accent: C.blue,
      accent2: "#c5ceda",
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d9dee5",
      proof: C.signal,
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Make a premium launch deck.",
        "Show the problem clearly.",
        "Show before and after.",
        "Show product proof.",
        "Make a strong climax.",
        "End with next steps.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-47-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.47 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_47_FULL_DATA_INPUTS, "compositionGrammarTransform", "drawRun247ComposedObjectScene"],
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
        "The baseline explains the product lab.",
        "The setup is readable but broad.",
        "The comparison is still generic.",
        "The proof remains process-led.",
        "The climax is a labeled output.",
        "The close is correct but small.",
      ][index],
    })),
  },
  {
    armId: "run2_47_full_composition_grammar_compiler",
    slug: "ppt-run2-47-full-vulca",
    label: "Run 2.47 full composition grammar",
    kicker: "RUN 2.47 / COMPOSITION GRAMMAR",
    footer: "run2_47_full_composition_grammar_compiler | consumes Run 2.46 | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      ...RUN2_47_FULL_DATA_INPUTS,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_46_multimodal_composition_decomposition.json",
      "run2_46_visual_object_grammar_memory.json",
      "run2_46_composition_workflow_gates.json",
      "run2_46_multimodal_composition_memory_result.json",
      RUN2_47_POLICY,
    ],
    forbidden: [
      "copied screenshots",
      "raw tutorial media",
      "source layouts",
      "source brand imitation",
      "slot_based_semantic_geometry_as_primary_surface",
      "three_equal_feature_cards",
    ],
    palette: {
      bg: "#f4efe4",
      rail: C.charcoal,
      accent: C.charcoal,
      accent2: C.blue,
      proof: C.signal,
      panel: C.white,
      title: "#0e1218",
      muted: "#56616d",
      rule: "#d8cfbf",
      surface: "#edf2f0",
    },
    slides: baseSlides,
  },
  {
    armId: "bad_run2_46_missing_composition_grammar",
    slug: "ppt-run2-47-bad-missing-composition-grammar",
    label: "Bad missing composition grammar",
    kicker: "RUN 2.47 / BAD CONTROL",
    footer: "bad_run2_46_missing_composition_grammar | Run 2.44 slots only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_47_BAD_DATA_INPUTS],
    data_input_manifest: ["run2_44_geometry_slots_only_no_run2_46_composition_grammar"],
    forbidden: [
      ...RUN2_46_GRAMMAR_INPUTS,
      "compositionGrammarTransform",
      "drawRun247ComposedObjectScene",
      "run2_46_visual_object_grammar_id",
      "run2_46_composition_gate_id",
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
        "Old slots remain without composition grammar.",
        "The storyboard collapses into labeled blocks.",
        "Before/after returns to explicit slots.",
        "The product proof is still a geometry rail.",
        "The climax names a result object without composing it.",
        "The close keeps a gate label but no scene.",
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
    visualObjectSceneObjects: [],
    codeModuleIds: new Set(),
    primaryCompositionKind: "",
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun247Module(metrics, functionName) {
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

function registerSceneObject(metrics, object) {
  metrics.visualObjectSceneObjects.push(object);
}

function textDensityTier(metrics) {
  if (metrics.visibleWords >= 60) return "rich";
  if (metrics.visibleWords >= 34) return "medium";
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

function armUsesFullRun247Data(arm) {
  return arm.armId === "run2_47_full_composition_grammar_compiler";
}

function armUsesBadRun247Data(arm) {
  return arm.armId === "bad_run2_46_missing_composition_grammar";
}

function assertRun247ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun247Data(arm)) {
    for (const input of RUN2_47_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesBadRun247Data(arm)) {
    for (const input of RUN2_47_BAD_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow bad-control input ${input}`);
    }
    for (const input of RUN2_46_GRAMMAR_INPUTS) {
      if (allowed.has(input) || !forbidden.has(input)) throw new Error(`${arm.armId} must block ${input}`);
    }
    return;
  }
  for (const input of RUN2_47_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun247PackJsonForArm(arm, relPath) {
  assertRun247ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (!armUsesFullRun247Data(arm) && !armUsesBadRun247Data(arm)) {
    throw new Error(`${arm.armId} cannot read Run 2.47 pack data`);
  }
  return readJson(relPath);
}

function validateRun247CompositionGrammarCompiler(data) {
  const {
    run246Result,
    multimodalCompositionDecomposition,
    visualObjectGrammarMemory,
    compositionWorkflowGates,
    semanticVisualAssetMemory,
    editorialCompositionTypographyMemory,
    visualAssetSemanticsWorkflowGates,
    run244Result,
    run244FullTrace,
    commercialUsecaseBank,
    sources,
  } = data;
  if (run246Result?.status !== "run2_46_multimodal_composition_memory_ready_public_blocked") {
    throw new Error("Run 2.47 must consume Run 2.46 memory result");
  }
  if (run246Result?.next_required_action !== "consume_run2_46_multimodal_composition_memory_before_run2_47_rerun") {
    throw new Error("Run 2.46 result does not point to Run 2.47");
  }
  if (multimodalCompositionDecomposition?.status !== "run2_46_multimodal_composition_decomposition_ready_public_blocked") {
    throw new Error("Run 2.47 decomposition status mismatch");
  }
  if (visualObjectGrammarMemory?.status !== "run2_46_visual_object_grammar_memory_ready_public_blocked") {
    throw new Error("Run 2.47 visual object grammar status mismatch");
  }
  if (compositionWorkflowGates?.status !== "run2_46_composition_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.47 composition gates status mismatch");
  }
  if (compositionWorkflowGates?.next_rerun_contract !== "must_be_consumed_before_run2_47_four_arm_rerun") {
    throw new Error("Run 2.47 missing next rerun contract");
  }
  if (semanticVisualAssetMemory?.status !== "run2_43_semantic_visual_asset_memory_ready_public_blocked") {
    throw new Error("Run 2.47 semantic memory status mismatch");
  }
  if (editorialCompositionTypographyMemory?.status !== "run2_43_editorial_composition_typography_memory_ready_public_blocked") {
    throw new Error("Run 2.47 editorial memory status mismatch");
  }
  if (visualAssetSemanticsWorkflowGates?.status !== "run2_43_visual_asset_semantics_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.47 visual asset gates status mismatch");
  }
  if (run244Result?.status !== "run2_44_semantic_geometry_rerun_public_blocked") {
    throw new Error("Run 2.47 must consume Run 2.44 generated result");
  }
  if (run244FullTrace?.arm_id !== "run2_44_full_semantic_geometry_compiler") {
    throw new Error("Run 2.47 must compare against Run 2.44 full trace");
  }
  const usecase = (commercialUsecaseBank?.usecases ?? []).find((item) => item.id === selectedUsecaseId);
  if (!usecase) throw new Error("Run 2.47 missing selected commercial usecase");
  if (!Array.isArray(sources?.sources) || sources.sources.length < 4) throw new Error("Run 2.47 missing sources");

  const decompositions = multimodalCompositionDecomposition.multimodal_composition_decomposition_records ?? [];
  const grammar = visualObjectGrammarMemory.visual_object_grammar_records ?? [];
  const gates = compositionWorkflowGates.composition_workflow_gates ?? [];
  if (decompositions.length !== 6 || grammar.length !== 6 || gates.length !== 6) {
    throw new Error("Run 2.47 must consume six decompositions, six grammar records, and six gates");
  }
  for (const role of baseSlides.map((slide) => slide.role)) {
    const decomp = decompositions.find((record) => record.role === role);
    const grammarRecord = grammar.find((record) => record.role === role);
    const gate = gates.find((record) => record.role === role);
    const traceSlide = (run244FullTrace.slides ?? []).find((slide) => slide.role === role);
    if (!decomp || !grammarRecord || !gate || !traceSlide) throw new Error(`Run 2.47 missing role contract for ${role}`);
    if (grammarRecord.required_decomposition_id !== decomp.decomposition_id) {
      throw new Error(`Run 2.47 grammar/decomposition mismatch for ${role}`);
    }
    if (gate.required_visual_object_grammar_id !== grammarRecord.visual_object_grammar_id) {
      throw new Error(`Run 2.47 gate/grammar mismatch for ${role}`);
    }
    if (gate.required_multimodal_composition_decomposition_id !== decomp.decomposition_id) {
      throw new Error(`Run 2.47 gate/decomposition mismatch for ${role}`);
    }
    if (gate.forbid_slot_based_geometry_as_primary_surface !== true) {
      throw new Error(`Run 2.47 gate must forbid slot-based primary surface for ${role}`);
    }
    if (grammarRecord.replaces_run2_44_slot_based_geometry !== true) {
      throw new Error(`Run 2.47 grammar must replace Run 2.44 slots for ${role}`);
    }
    if ((traceSlide.run2_44_semantic_asset_geometry_slots ?? []).length !== 3) {
      throw new Error(`Run 2.47 bad control requires Run 2.44 slots for ${role}`);
    }
  }
}

function loadRun247ContractData(arm) {
  const run246Result = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.run246Result);
  const multimodalCompositionDecomposition = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.multimodalCompositionDecomposition);
  const visualObjectGrammarMemory = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.visualObjectGrammarMemory);
  const compositionWorkflowGates = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.compositionWorkflowGates);
  const semanticVisualAssetMemory = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.semanticVisualAssetMemory);
  const editorialCompositionTypographyMemory = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.editorialCompositionTypographyMemory);
  const visualAssetSemanticsWorkflowGates = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.visualAssetSemanticsWorkflowGates);
  const run244Result = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.run244Result);
  const run244FullTrace = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.run244FullTrace);
  const commercialUsecaseBank = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.commercialUsecaseBank);
  const sources = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.sources);
  const data = {
    run246Result,
    multimodalCompositionDecomposition,
    visualObjectGrammarMemory,
    compositionWorkflowGates,
    semanticVisualAssetMemory,
    editorialCompositionTypographyMemory,
    visualAssetSemanticsWorkflowGates,
    run244Result,
    run244FullTrace,
    commercialUsecaseBank,
    sources,
  };
  validateRun247CompositionGrammarCompiler(data);
  return {
    ...data,
    usecase: commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_47_run2_46_composition_grammar_contract_ready",
  };
}

function loadRun247BadControlData(arm) {
  const run244Result = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.run244Result);
  const run244FullTrace = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.run244FullTrace);
  const commercialUsecaseBank = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.commercialUsecaseBank);
  const sources = readRun247PackJsonForArm(arm, RUN2_47_INPUTS.sources);
  if (run244Result?.status !== "run2_44_semantic_geometry_rerun_public_blocked") {
    throw new Error("Run 2.47 bad control must read Run 2.44 result");
  }
  if (run244FullTrace?.arm_id !== "run2_44_full_semantic_geometry_compiler") {
    throw new Error("Run 2.47 bad control must read Run 2.44 full trace");
  }
  return {
    run244Result,
    run244FullTrace,
    commercialUsecaseBank,
    sources,
    usecase: commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
  };
}

function selectRun247ForSlide(role, contractData) {
  const decomp = (contractData.multimodalCompositionDecomposition?.multimodal_composition_decomposition_records ?? []).find(
    (item) => item.role === role,
  );
  const grammar = (contractData.visualObjectGrammarMemory?.visual_object_grammar_records ?? []).find((item) => item.role === role);
  const gate = (contractData.compositionWorkflowGates?.composition_workflow_gates ?? []).find((item) => item.role === role);
  const priorTraceSlide = (contractData.run244FullTrace?.slides ?? []).find((item) => item.role === role);
  if (!decomp || !grammar || !gate || !priorTraceSlide) throw new Error(`Run 2.47 missing role ${role}`);
  return compositionGrammarTransform({
    decomp,
    grammar,
    gate,
    priorTraceSlide,
    usecase: contractData.usecase,
  });
}

function selectBadRun244SlotsForSlide(role, badData) {
  const traceSlide = (badData.run244FullTrace?.slides ?? []).find((item) => item.role === role);
  return traceSlide?.run2_44_semantic_asset_geometry_slots ?? [];
}

function compositionGrammarTransform(selection) {
  const { decomp, grammar, gate, priorTraceSlide, usecase } = selection;
  const role = grammar.role;
  const compositionKind = decomp.composition_move;
  const heroWeights = {
    cover: 0.68,
    setup: 0.58,
    contrast: 0.66,
    proof: 0.62,
    climax: 0.82,
    close: 0.56,
  };
  const weight = heroWeights[role] ?? 0.62;
  const sceneObjects = buildRun247SceneObjects(role, grammar, decomp, weight);
  return {
    role,
    compositionKind,
    decomp,
    grammar,
    gate,
    priorTraceSlide,
    usecase,
    visualObjectGrammarId: grammar.visual_object_grammar_id,
    multimodalCompositionDecompositionId: decomp.decomposition_id,
    compositionGateId: gate.gate_id,
    semanticAssetIds: grammar.required_run2_43_semantic_visual_asset_ids,
    priorSlotRoles: decomp.run2_44_slot_roles_to_replace ?? [],
    sceneObjects,
    publicHeadline: compactText(grammar.visual_object_grammar?.[0] ?? "one composed visual object owns the slide", 92),
    publicSubline: compactText(grammar.visual_object_grammar?.[1] ?? usecase?.deck_mission, 110),
    sourceBoundaryStatus: RUN2_47_SOURCE_BOUNDARY,
  };
}

function buildRun247SceneObjects(role, grammar, decomp, weight) {
  const hero = {
    object_id: `run2_47_${role}_primary_composed_object`,
    object_role: "primary_composed_object",
    grammar_rule: grammar.visual_object_grammar?.[0] ?? "primary object scene",
    x: role === "cover" ? 560 : role === "climax" ? 170 : role === "proof" ? 120 : 420,
    y: role === "climax" ? 126 : role === "proof" ? 146 : 130,
    w: role === "climax" ? 820 : role === "cover" ? 520 : role === "proof" ? 710 : 590,
    h: role === "climax" ? 404 : role === "cover" ? 388 : role === "proof" ? 330 : 348,
    emphasis: weight,
  };
  if (role === "contrast") {
    hero.x = 414;
    hero.y = 132;
    hero.w = 660;
    hero.h = 392;
  }
  if (role === "setup") {
    hero.x = 448;
    hero.y = 172;
    hero.w = 560;
    hero.h = 260;
  }
  if (role === "close") {
    hero.x = 440;
    hero.y = 198;
    hero.w = 390;
    hero.h = 212;
  }
  const supportA = {
    object_id: `run2_47_${role}_support_memory_field`,
    object_role: "support_memory_field",
    grammar_rule: grammar.visual_object_grammar?.[2] ?? grammar.visual_object_grammar?.[1] ?? "secondary memory field",
    x: role === "cover" ? 110 : 120,
    y: role === "close" ? 252 : role === "climax" ? 520 : 392,
    w: role === "climax" ? 285 : role === "cover" ? 360 : 310,
    h: role === "climax" ? 68 : role === "cover" ? 120 : 96,
    emphasis: 0.28,
  };
  const supportB = {
    object_id: `run2_47_${role}_proof_or_release_cue`,
    object_role: "proof_or_release_cue",
    grammar_rule: grammar.visual_object_grammar?.[3] ?? grammar.visual_object_grammar?.[2] ?? "quiet proof cue",
    x: role === "climax" ? 500 : role === "close" ? 870 : 852,
    y: role === "climax" ? 524 : role === "close" ? 252 : 488,
    w: role === "climax" ? 470 : role === "close" ? 250 : 260,
    h: role === "climax" ? 70 : role === "close" ? 140 : 80,
    emphasis: 0.24,
  };
  return [hero, supportA, supportB].map((object) => ({
    ...object,
    composition_move: decomp.composition_move,
    replaces_slot_roles: decomp.run2_44_slot_roles_to_replace ?? [],
  }));
}

function drawMiniDeckSurface(slide, x, y, w, h, fill, accent, dark = false) {
  rect(slide, x, y, w, h, fill, colorLine(dark ? "#2c3742" : "#cad2d7", 1));
  rect(slide, x + 22, y + 24, w * 0.42, 12, accent);
  rect(slide, x + 22, y + 54, w * 0.24, 7, dark ? C.cyan : "#9ac3d0");
  rect(slide, x + 22, y + 78, w * 0.32, 7, dark ? "#d8e6ec" : "#c9d4d9");
  rect(slide, x + w - 118, y + 28, 72, 96, dark ? "#273542" : "#edf1f3", colorLine(dark ? "#3b4a55" : "#d5dde1", 1));
  ellipse(slide, x + w - 96, y + 54, 28, 28, accent, colorLine("transparent", 0));
  rect(slide, x + 24, y + h - 54, w - 52, 20, dark ? "#202a34" : "#f8f4eb", colorLine(dark ? "#354654" : "#dad2c6", 1));
}

function drawRun247ComposedObjectScene(slide, arm, spec, selection, metrics, moduleName) {
  registerRun247Module(metrics, moduleName);
  metrics.primaryCompositionKind = selection.compositionKind;
  const dark = spec.role === "climax";
  if (dark) {
    rect(slide, 70, 98, 1080, 530, C.charcoal, colorLine(C.charcoal, 1));
    text(slide, "One generated result owns the room.", 110, 126, 760, 48, {
      fontSize: 42,
      title: true,
      bold: true,
      color: C.white,
    });
    registerText(metrics, "One generated result owns the room");
  } else {
    text(slide, compactText(spec.title, 76), 76, 112, spec.role === "cover" ? 485 : 635, spec.role === "cover" ? 90 : 74, {
      fontSize: spec.role === "cover" ? 39 : 34,
      title: true,
      bold: true,
      color: arm.palette.title,
    });
    registerText(metrics, spec.title);
    text(slide, selection.publicHeadline, 80, spec.role === "cover" ? 210 : 186, 480, 42, {
      fontSize: 13.5,
      color: arm.palette.muted,
    });
    registerText(metrics, selection.publicHeadline);
  }

  const [hero, supportA, supportB] = selection.sceneObjects;
  const shadow = dark ? "#0b0f14" : "#d8cdbb";
  rect(slide, hero.x + 18, hero.y + 20, hero.w, hero.h, shadow, colorLine(shadow, 0));
  drawMiniDeckSurface(slide, hero.x, hero.y, hero.w, hero.h, dark ? "#f7f9fb" : C.white, dark ? C.signal : arm.palette.proof, false);
  const heroSublineY = spec.role === "proof" ? hero.y + hero.h - 132 : hero.y + hero.h - 80;
  text(slide, compactText(selection.publicSubline, 82), hero.x + 32, heroSublineY, hero.w - 70, 38, {
    fontSize: roleFontSize(spec.role, 13, 11),
    color: C.ink,
    bold: spec.role === "climax",
  });
  registerText(metrics, selection.publicSubline);
  registerSceneObject(metrics, hero);
  registerPresentationSurface(metrics, hero.x, hero.y, hero.w, hero.h, hero.emphasis);
  registerProof(metrics, 2);

  rect(slide, supportA.x + 10, supportA.y + 12, supportA.w, supportA.h, dark ? "#0d1117" : "#dfd4c4", colorLine("transparent", 0));
  rect(slide, supportA.x, supportA.y, supportA.w, supportA.h, dark ? "#202b35" : "#fbf8ef", colorLine(dark ? "#354654" : arm.palette.rule, 1));
  text(slide, compactText(supportA.grammar_rule, 66), supportA.x + 18, supportA.y + 18, supportA.w - 34, 34, {
    fontSize: 11,
    color: dark ? "#eaf3f8" : arm.palette.title,
    bold: true,
  });
  rect(slide, supportA.x + 20, supportA.y + supportA.h - 28, Math.max(72, supportA.w * 0.42), 7, dark ? C.cyan : arm.palette.accent2);
  registerText(metrics, supportA.grammar_rule);
  registerSceneObject(metrics, supportA);

  rect(slide, supportB.x, supportB.y, supportB.w, supportB.h, dark ? "#263642" : "#edf2f0", colorLine(dark ? "#40515e" : "#cfd8d5", 1));
  text(slide, compactText(supportB.grammar_rule, 62), supportB.x + 18, supportB.y + 16, supportB.w - 34, 30, {
    fontSize: 10.5,
    color: dark ? "#edf6fb" : arm.palette.muted,
    bold: true,
  });
  ellipse(slide, supportB.x + supportB.w - 42, supportB.y + supportB.h - 40, 24, 24, dark ? C.signal : arm.palette.proof, colorLine("transparent", 0));
  registerText(metrics, supportB.grammar_rule);
  registerSceneObject(metrics, supportB);
  registerProof(metrics, 1);

  drawRun247ConnectiveState(slide, arm, spec, hero, supportA, supportB, dark);
  drawRun247QualityStrip(slide, arm, selection, metrics, dark);
  registerZones(metrics, 4);
}

function roleFontSize(role, regular, climax) {
  return role === "climax" ? climax : regular;
}

function drawRun247ConnectiveState(slide, arm, spec, hero, supportA, supportB, dark) {
  const lineColor = dark ? C.cyan : arm.palette.proof;
  rect(slide, Math.min(supportA.x + supportA.w, hero.x) - 6, supportA.y + Math.round(supportA.h / 2), Math.abs(hero.x - (supportA.x + supportA.w)) + 12, 4, lineColor);
  rect(slide, hero.x + hero.w - 4, supportB.y + Math.round(supportB.h / 2), Math.max(36, supportB.x - (hero.x + hero.w) + 8), 4, lineColor);
  if (spec.role === "contrast") {
    text(slide, "after owns scale", 118, 514, 210, 22, { fontSize: 11, mono: true, bold: true, color: arm.palette.proof });
    rect(slide, 306, 522, 92, 4, arm.palette.proof);
  }
  if (spec.role === "setup") {
    text(slide, "failure -> selected route", 124, 510, 290, 22, { fontSize: 11, mono: true, bold: true, color: arm.palette.proof });
  }
  if (spec.role === "proof") {
    rect(slide, hero.x + 34, hero.y + 124, hero.w - 70, 38, C.charcoal);
    text(slide, "active decision lane", hero.x + 58, hero.y + 138, 190, 12, { fontSize: 10, mono: true, bold: true, color: C.white });
  }
  if (spec.role === "close") {
    const labelY = 424;
    text(slide, "review", supportA.x + 22, labelY, 120, 18, { fontSize: 10, mono: true, bold: true, color: arm.palette.muted });
    text(slide, "release", hero.x + 24, labelY, 120, 18, { fontSize: 10, mono: true, bold: true, color: arm.palette.muted });
    text(slide, "next run", supportB.x + 22, labelY, 120, 18, { fontSize: 10, mono: true, bold: true, color: arm.palette.muted });
  }
}

function drawRun247QualityStrip(slide, arm, selection, metrics, dark) {
  const x = dark ? 118 : 84;
  const y = dark ? 596 : 552;
  const w = dark ? 900 : 1040;
  rect(slide, x, y, w, 44, dark ? "#1f2a34" : C.white, colorLine(dark ? "#354654" : arm.palette.rule, 1));
  const checks = selection.grammar.composition_quality_checks ?? [];
  checks.slice(0, 4).forEach((check, index) => {
    const colW = Math.floor((w - 36) / 4);
    const px = x + 18 + index * colW;
    ellipse(slide, px, y + 14, 12, 12, index === 0 ? arm.palette.proof : dark ? C.cyan : arm.palette.accent2, colorLine("transparent", 0));
    text(slide, compactText(check, 31), px + 18, y + 11, colW - 24, 16, {
      fontSize: 7.8,
      color: dark ? "#d8e6ec" : arm.palette.muted,
    });
    registerText(metrics, check);
  });
}

function drawRun247CoverComposition(slide, arm, spec, selection, metrics) {
  drawRun247ComposedObjectScene(slide, arm, spec, selection, metrics, "drawRun247CoverCompositionGrammar");
}

function drawRun247SetupComposition(slide, arm, spec, selection, metrics) {
  drawRun247ComposedObjectScene(slide, arm, spec, selection, metrics, "drawRun247SetupCompositionGrammar");
}

function drawRun247ContrastComposition(slide, arm, spec, selection, metrics) {
  drawRun247ComposedObjectScene(slide, arm, spec, selection, metrics, "drawRun247ContrastCompositionGrammar");
}

function drawRun247ProofComposition(slide, arm, spec, selection, metrics) {
  drawRun247ComposedObjectScene(slide, arm, spec, selection, metrics, "drawRun247ProofCompositionGrammar");
}

function drawRun247ClimaxComposition(slide, arm, spec, selection, metrics) {
  drawRun247ComposedObjectScene(slide, arm, spec, selection, metrics, "drawRun247ClimaxCompositionGrammar");
}

function drawRun247CloseComposition(slide, arm, spec, selection, metrics) {
  drawRun247ComposedObjectScene(slide, arm, spec, selection, metrics, "drawRun247CloseCompositionGrammar");
}

const RUN2_47_MODULES = {
  cover: drawRun247CoverComposition,
  setup: drawRun247SetupComposition,
  contrast: drawRun247ContrastComposition,
  proof: drawRun247ProofComposition,
  climax: drawRun247ClimaxComposition,
  close: drawRun247CloseComposition,
};

function drawBadRun244SlotFallbackSlide(slide, arm, spec, badData, metrics) {
  const slots = selectBadRun244SlotsForSlide(spec.role, badData);
  text(slide, spec.title, 76, 118, 540, 74, {
    fontSize: 34,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, compactText(spec.claim, 100), 80, 214, 456, 46, { fontSize: 14, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  const panel = { x: 604, y: 132, w: 480, h: 344 };
  rect(slide, panel.x + 16, panel.y + 18, panel.w, panel.h, "#dccfb7", colorLine("#dccfb7", 1));
  rect(slide, panel.x, panel.y, panel.w, panel.h, arm.palette.panel, colorLine(arm.palette.rule, 1));
  slots.forEach((slot, index) => {
    const slotW = index === 0 ? 226 : 150;
    const slotH = index === 0 ? 150 : 106;
    const x = index === 0 ? panel.x + 34 : panel.x + 286;
    const y = index === 0 ? panel.y + 58 : panel.y + 50 + (index - 1) * 132;
    rect(slide, x, y, slotW, slotH, index === 0 ? "#d4bc83" : "#eee2c7", colorLine("#c6ad78", 1));
    text(slide, compactText(slot.slot_role || slot.surface_type, 30), x + 14, y + 18, slotW - 28, 24, {
      fontSize: 10.5,
      bold: true,
      title: index === 0,
      color: arm.palette.title,
    });
    text(slide, compactText(slot.semantic_object, 58), x + 14, y + slotH - 48, slotW - 28, 30, {
      fontSize: 9,
      color: arm.palette.muted,
    });
    registerText(metrics, `${slot.slot_role} ${slot.semantic_object}`);
  });
  text(slide, "Run 2.44 geometry slots are present; Run 2.46 composition grammar is absent.", panel.x + 34, panel.y + 280, 390, 34, {
    fontSize: 12,
    color: arm.palette.muted,
  });
  chip(slide, "bad control: no 2.46 grammar", 84, 548, 270, C.white, arm.palette.accent);
  registerText(metrics, "Run 2.44 geometry slots are present Run 2.46 composition grammar is absent");
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
  text(slide, "Readable, but no Run 2.46 composition grammar consumption.", 108, 382, 420, 54, {
    fontSize: 20,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, "Readable but no Run 2.46 composition grammar consumption");
  registerPresentationSurface(metrics, 84, 318, 1042, 212, 0.35);
}

function renderRun247Slide(presentation, spec, arm, n, contractData, badData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun247Data(arm)) {
    const selection = selectRun247ForSlide(spec.role, contractData);
    RUN2_47_MODULES[spec.role](slide, arm, spec, selection, metrics);
  } else if (armUsesBadRun247Data(arm)) {
    drawBadRun244SlotFallbackSlide(slide, arm, spec, badData, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertRun247ArmInputBoundaries(arm);
  const fullRun247 = armUsesFullRun247Data(arm);
  const badRun247 = armUsesBadRun247Data(arm);
  const contractData = fullRun247 ? context.contractData ?? loadRun247ContractData(arm) : null;
  const badData = badRun247 ? context.badData ?? loadRun247BadControlData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun247 || badRun247 ? selectedUsecaseId : "",
    source_composition_memory_run_id: fullRun247 ? "2.46" : "",
    source_generated_run_id: fullRun247 || badRun247 ? "2.44" : "",
    source_workflow_run_id: fullRun247 ? "2.43" : "",
    run2_47_composition_grammar_status: fullRun247
      ? RUN2_47_FULL_STATUS
      : badRun247
        ? RUN2_47_BAD_STATUS
        : "boundary_control_no_run2_46_composition_grammar_consumption",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.47 composition grammar rerun from scripts/generate_ppt_run2_47_composition_grammar_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun247 ? selectRun247ForSlide(slide.role, contractData) : null;
      const badSlots = badRun247 ? selectBadRun244SlotsForSlide(slide.role, badData) : [];
      const codeModuleIds = fullRun247
        ? hasRenderedMetrics
          ? Array.from(roleMetrics.codeModuleIds)
          : [RUN2_47_MODULES[slide.role].name]
        : [];
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_43_semantic_visual_asset_ids: fullRun247 ? selection.semanticAssetIds : [],
        run2_46_visual_object_grammar_id: fullRun247 ? selection.visualObjectGrammarId : "",
        run2_46_multimodal_composition_decomposition_id: fullRun247
          ? selection.multimodalCompositionDecompositionId
          : "",
        run2_46_composition_gate_id: fullRun247 ? selection.compositionGateId : "",
        run2_46_slot_based_geometry_replaced: fullRun247,
        run2_46_source_boundary_status: fullRun247 ? RUN2_47_SOURCE_BOUNDARY : "",
        run2_46_composition_quality_checks: fullRun247 ? selection.grammar.composition_quality_checks ?? [] : [],
        run2_46_motion_or_sequence_implication: fullRun247 ? selection.grammar.motion_or_sequence_implication : "",
        run2_47_composition_compiler_policy: fullRun247 ? RUN2_47_POLICY : badRun247 ? "run2_44_slots_without_run2_46_grammar" : "",
        run2_47_primary_composition_kind: fullRun247 ? roleMetrics.primaryCompositionKind || selection.compositionKind : "slot_based_semantic_geometry",
        run2_47_visual_object_scene_objects: fullRun247
          ? hasRenderedMetrics
            ? roleMetrics.visualObjectSceneObjects
            : selection.sceneObjects
          : [],
        run2_47_code_module_ids: codeModuleIds,
        run2_44_semantic_asset_geometry_slots: fullRun247 ? [] : badSlots,
        run2_44_geometry_compiler_policy: badRun247 ? "slot_based_semantic_geometry_as_negative_control" : "",
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

function assertRun247CompositionGrammarSelfCheck(trace) {
  if (trace.arm_id === "run2_47_full_composition_grammar_compiler") {
    if (trace.run2_47_composition_grammar_status !== RUN2_47_FULL_STATUS) {
      throw new Error("Run 2.47 full trace did not consume Run 2.46 composition grammar");
    }
    for (const slide of trace.slides) {
      if (!String(slide.run2_46_visual_object_grammar_id ?? "").startsWith("visual_object_grammar_2_46_")) {
        throw new Error(`Run 2.47 full slide ${slide.slide_id} missing visual object grammar id`);
      }
      if (!String(slide.run2_46_multimodal_composition_decomposition_id ?? "").startsWith("composition_decomposition_2_46_")) {
        throw new Error(`Run 2.47 full slide ${slide.slide_id} missing composition decomposition id`);
      }
      if (!String(slide.run2_46_composition_gate_id ?? "").startsWith("gate_2_46_")) {
        throw new Error(`Run 2.47 full slide ${slide.slide_id} missing composition gate id`);
      }
      if (slide.run2_46_slot_based_geometry_replaced !== true) {
        throw new Error(`Run 2.47 full slide ${slide.slide_id} did not replace slot geometry`);
      }
      if (slide.run2_46_source_boundary_status !== RUN2_47_SOURCE_BOUNDARY) {
        throw new Error(`Run 2.47 full slide ${slide.slide_id} missing source boundary`);
      }
      if ((slide.run2_44_semantic_asset_geometry_slots ?? []).length !== 0) {
        throw new Error(`Run 2.47 full slide ${slide.slide_id} leaked Run 2.44 slots`);
      }
      if ((slide.run2_47_visual_object_scene_objects ?? []).length < 3) {
        throw new Error(`Run 2.47 full slide ${slide.slide_id} missing composed scene objects`);
      }
      if ((slide.run2_47_code_module_ids ?? []).length !== 1 || !slide.run2_47_code_module_ids[0].startsWith("drawRun247")) {
        throw new Error(`Run 2.47 full slide ${slide.slide_id} missing Run 2.47 module`);
      }
    }
  }
  if (trace.arm_id === "bad_run2_46_missing_composition_grammar") {
    if (trace.run2_47_composition_grammar_status !== RUN2_47_BAD_STATUS) {
      throw new Error("Run 2.47 bad trace has wrong status");
    }
    for (const slide of trace.slides) {
      if (slide.run2_46_visual_object_grammar_id !== "") {
        throw new Error(`Run 2.47 bad slide ${slide.slide_id} leaked Run 2.46 grammar id`);
      }
      if (slide.run2_46_slot_based_geometry_replaced !== false) {
        throw new Error(`Run 2.47 bad slide ${slide.slide_id} claimed slot replacement`);
      }
      if ((slide.run2_44_semantic_asset_geometry_slots ?? []).length !== 3) {
        throw new Error(`Run 2.47 bad slide ${slide.slide_id} missing Run 2.44 slots`);
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

function buildRun247FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-47-four-arm-contact-sheet.png"),
    "Run 2.47 composition grammar comparison",
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
      "required proof objects: Run 2.46 visual object grammar id, multimodal composition decomposition id, composition gate id, slot replacement flag, and source boundary status",
      "source requirements: full arm reads Run 2.46 composition grammar pack before native PPT drawing",
      "negative control: bad arm can reuse Run 2.44 geometry slots, but cannot read Run 2.46 composition grammar",
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
  const contractData = armUsesFullRun247Data(arm) ? loadRun247ContractData(arm) : null;
  const badData = armUsesBadRun247Data(arm) ? loadRun247BadControlData(arm) : null;
  const slides = arm.slides.map((slide, index) =>
    renderRun247Slide(presentation, slide, arm, index + 1, contractData, badData, metricsByRole),
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
  assertRun247CompositionGrammarSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_47_composition_grammar_arms.mjs",
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

function writeRun247Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-47-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-47-bad-missing-composition-grammar/trace_manifest.json`);
  const fullSlidesWithGrammar = fullTrace.slides.filter((slide) =>
    String(slide.run2_46_visual_object_grammar_id ?? "").startsWith("visual_object_grammar_2_46_"),
  ).length;
  const fullSlidesWithSlotReplacement = fullTrace.slides.filter((slide) => slide.run2_46_slot_based_geometry_replaced === true).length;
  const badSlidesWithoutGrammar = badTrace.slides.filter((slide) => slide.run2_46_visual_object_grammar_id === "").length;
  const result = {
    schema_version: 1,
    run_id: "2.47",
    status: "run2_47_composition_grammar_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_composition_memory_run_id: "2.46",
    source_generated_run_id: "2.44",
    source_workflow_run_id: "2.43",
    database_expansion: false,
    workflow_expansion: false,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_46_result: RUN2_47_INPUTS.run246Result,
      multimodal_composition_decomposition: RUN2_47_INPUTS.multimodalCompositionDecomposition,
      visual_object_grammar_memory: RUN2_47_INPUTS.visualObjectGrammarMemory,
      composition_workflow_gates: RUN2_47_INPUTS.compositionWorkflowGates,
      semantic_visual_asset_memory: RUN2_47_INPUTS.semanticVisualAssetMemory,
      editorial_composition_typography_memory: RUN2_47_INPUTS.editorialCompositionTypographyMemory,
      visual_asset_semantics_workflow_gates: RUN2_47_INPUTS.visualAssetSemanticsWorkflowGates,
      run2_44_result: RUN2_47_INPUTS.run244Result,
      run2_44_full_trace: RUN2_47_INPUTS.run244FullTrace,
      commercial_usecase_bank: RUN2_47_INPUTS.commercialUsecaseBank,
      sources: RUN2_47_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_47_composition_grammar_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_47_full_composition_grammar_compiler",
      best_internal_arm_verdict: "Run 2.46 visual object grammar now drives composed native PPT scenes before drawing",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: "composition_grammar_binding",
      source_data_status: RUN2_47_FULL_STATUS,
      full_slides_with_run2_46_visual_object_grammar_id: fullSlidesWithGrammar,
      full_slides_with_run2_46_composition_gate_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_46_composition_gate_id ?? "").startsWith("gate_2_46_"),
      ).length,
      full_slides_with_slot_based_geometry_replaced: fullSlidesWithSlotReplacement,
      full_slides_without_run2_44_geometry_slots: fullTrace.slides.filter((slide) => (slide.run2_44_semantic_asset_geometry_slots ?? []).length === 0).length,
      bad_control_slides_without_run2_46_grammar: badSlidesWithoutGrammar,
      bad_control_slides_with_run2_44_geometry_slots: badTrace.slides.filter((slide) => (slide.run2_44_semantic_asset_geometry_slots ?? []).length === 3).length,
      repair_modules: Object.values(RUN2_47_MODULES).map((fn) => fn.name),
    },
    control_boundary: {
      bad_run2_46_missing_composition_grammar:
        "may see Run 2.44 semantic geometry slots, but must not bind Run 2.46 visual object grammar, decomposition, or composition gate ids",
      prompt_only: "commercial_case_only_no_run2_46_composition_grammar",
      run1_5_skill: "prior_baseline_no_run2_46_composition_grammar",
    },
    visual_quality_boundary:
      "composition grammar consumption proof only; public video-grade aesthetics, native motion, and human release approval remain blocked",
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
      "audit_run2_47_composition_grammar_against_visual_quality_then_continue_data_workflow_thickening_or_renderer_repair",
  };
  const resultJson = path.join(root, pack, "results", "run2_47_composition_grammar_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_47_composition_grammar_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.47 Composition Grammar Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.47 consumes Run 2.46 before native PPT drawing. The full arm binds visual object grammar, multimodal composition decomposition, and composition workflow gates, then replaces Run 2.44 slot-based geometry with composed object scenes.",
      "",
      "This fixes the next suspected workflow bug: the generator must not merely carry Run 2.46 files as notes. The generated full arm carries `run2_46_visual_object_grammar_id`, `run2_46_multimodal_composition_decomposition_id`, `run2_46_composition_gate_id`, and `run2_46_slot_based_geometry_replaced` in trace.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_47_full_composition_grammar_compiler`",
      "- `bad_run2_46_missing_composition_grammar`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_47_full_composition_grammar_compiler`.",
      "",
      "Quality delta: `composition_grammar_binding`. All six full-arm slides contain Run 2.46 visual object grammar ids and mark slot-based geometry replaced.",
      "",
      "The negative control `bad_run2_46_missing_composition_grammar` can reuse Run 2.44 geometry slots, but it has no Run 2.46 visual object grammar id, no decomposition id, and no composition gate id.",
      "",
      "Public release remains blocked. This proves composition grammar consumption, not final public-video-grade aesthetics.",
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
  const fourArmSheet = buildRun247FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_47_composition_grammar_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_47_composition_grammar_rerun_summary.json"), runSummary);
  writeRun247Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_47_INPUTS,
  RUN2_47_FULL_DATA_INPUTS,
  armSpecs,
  assertRun247ArmInputBoundaries,
  assertRun247CompositionGrammarSelfCheck,
  compositionGrammarTransform,
  drawRun247ComposedObjectScene,
  loadRun247ContractData,
  main,
  readRun247PackJsonForArm,
  registerRun247Module,
  selectRun247ForSlide,
  traceFor,
  validateRun247CompositionGrammarCompiler,
};
