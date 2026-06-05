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
const RUN2_44_POLICY = "run2_43_workflow_to_data_bound_visual_geometry";
const RUN2_44_GEOMETRY_SOURCE =
  "run2_43_semantic_visual_asset_memory+run2_43_editorial_composition_typography_memory+run2_43_visual_asset_semantics_workflow_gates";
const RUN2_44_FULL_STATUS = "run2_43_workflow_consumed_for_data_bound_geometry";
const RUN2_44_BAD_STATUS = "run2_43_names_only_geometry_control";

const C = {
  ink: "#111318",
  paper: "#f8f4eb",
  white: "#ffffff",
  line: "#d4cec2",
  muted: "#5f6872",
  midnight: "#11161d",
  blue: "#255fdd",
  cyan: "#79c8d8",
  signal: "#e85237",
  green: "#118a66",
  haze: "#eef2f5",
  warm: "#f2d46b",
  lilac: "#b8b0ff",
};

const RUN2_44_INPUTS = {
  run243WorkflowResult: `${pack}/results/run2_43_visual_asset_semantics_workflow_result.json`,
  semanticVisualAssetMemory: `${pack}/run2_43_semantic_visual_asset_memory.json`,
  editorialCompositionTypographyMemory: `${pack}/run2_43_editorial_composition_typography_memory.json`,
  visualAssetSemanticsWorkflowGates: `${pack}/run2_43_visual_asset_semantics_workflow_gates.json`,
  run244DataflowReadinessAudit: `${pack}/results/run2_44_dataflow_readiness_audit.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_44_FULL_DATA_INPUTS = Object.values(RUN2_44_INPUTS);
const RUN2_44_NAME_ONLY_INPUTS = [
  RUN2_44_INPUTS.semanticVisualAssetMemory,
  RUN2_44_INPUTS.commercialUsecaseBank,
  RUN2_44_INPUTS.sources,
];

const baseSlides = [
  {
    role: "cover",
    title: "Data-bound visual memory becomes the launch scene.",
    claim: "The full arm must bind semantic asset ids before drawing the hero geometry.",
  },
  {
    role: "setup",
    title: "The failure is visible when memory stays name-only.",
    claim: "The weak arm can repeat labels, but cannot place objects from gates and memory.",
  },
  {
    role: "contrast",
    title: "Before and after need asymmetric semantic weight.",
    claim: "Run 2.43 says which object owns the frame; Run 2.44 turns that into geometry.",
  },
  {
    role: "proof",
    title: "Proof should look like a working product surface.",
    claim: "The compiler binds role, object, typography target, and workflow gate before native PPT code.",
  },
  {
    role: "climax",
    title: "The result object must carry the slide.",
    claim: "The climax uses a higher primary weight target and pushes proof into support rails.",
  },
  {
    role: "close",
    title: "The release gate becomes an inspectable handoff.",
    claim: "Public release is still blocked, but the data path is no longer hidden from QA.",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-44-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.44 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_44_FULL_DATA_INPUTS, "semanticGeometryTransform", "layoutFromRun243Memory"],
    palette: {
      bg: "#f5f6f8",
      rail: "#374151",
      accent: C.blue,
      accent2: "#bfcbda",
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d8dde4",
      proof: C.signal,
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Make a premium launch deck.",
        "Explain why the current deck is weak.",
        "Show before and after.",
        "Show product proof.",
        "Make the climax impressive.",
        "End with a release gate.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-44-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.44 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_44_FULL_DATA_INPUTS, "semanticGeometryTransform", "layoutFromRun243Memory"],
    palette: {
      bg: "#f4f7fb",
      rail: "#263247",
      accent: C.blue,
      accent2: C.green,
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d3dbe7",
      proof: C.green,
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "The baseline knows the product lab.",
        "The setup is readable but broad.",
        "The comparison stays generic.",
        "The proof reads as process.",
        "The climax is still a labeled output.",
        "The close is correct but small.",
      ][index],
    })),
  },
  {
    armId: "run2_44_full_semantic_geometry_compiler",
    slug: "ppt-run2-44-full-vulca",
    label: "Run 2.44 full semantic geometry",
    kicker: "RUN 2.44 / SEMANTIC GEOMETRY",
    footer: "run2_44_full_semantic_geometry_compiler | consumes Run 2.43 | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      RUN2_44_INPUTS.run243WorkflowResult,
      RUN2_44_INPUTS.semanticVisualAssetMemory,
      RUN2_44_INPUTS.editorialCompositionTypographyMemory,
      RUN2_44_INPUTS.visualAssetSemanticsWorkflowGates,
      RUN2_44_INPUTS.run244DataflowReadinessAudit,
      RUN2_44_INPUTS.commercialUsecaseBank,
      RUN2_44_INPUTS.sources,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_43_semantic_visual_asset_memory.json",
      "run2_43_editorial_composition_typography_memory.json",
      "run2_43_visual_asset_semantics_workflow_gates.json",
      "run2_44_dataflow_readiness_audit.json",
      RUN2_44_POLICY,
    ],
    forbidden: [
      "copied screenshots",
      "raw tutorial media",
      "source layouts",
      "source brand imitation",
      "equal feature-card grid as primary composition",
      "generic placeholder geometry",
    ],
    palette: {
      bg: "#f8f4eb",
      rail: "#11161d",
      accent: "#11161d",
      accent2: "#255fdd",
      proof: "#e85237",
      panel: C.white,
      title: "#0e1218",
      muted: "#56616d",
      rule: "#d8cfbf",
      surface: "#eef3f2",
    },
    slides: baseSlides,
  },
  {
    armId: "bad_run2_43_name_only_geometry",
    slug: "ppt-run2-44-bad-run2-43-name-only-geometry",
    label: "Bad Run 2.43 name-only geometry",
    kicker: "RUN 2.44 / NAME-ONLY CONTROL",
    footer: "bad_run2_43_name_only_geometry | names only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_44_NAME_ONLY_INPUTS],
    data_input_manifest: ["run2_43_surface_names_only_no_gate_or_geometry_binding"],
    forbidden: [
      RUN2_44_INPUTS.run243WorkflowResult,
      RUN2_44_INPUTS.editorialCompositionTypographyMemory,
      RUN2_44_INPUTS.visualAssetSemanticsWorkflowGates,
      RUN2_44_INPUTS.run244DataflowReadinessAudit,
      "semanticGeometryTransform",
      "layoutFromRun243Memory",
      "run2_43_semantic_asset_id_binding",
      "run2_43_gate_id_binding",
    ],
    palette: {
      bg: "#f1eadb",
      rail: "#695d3a",
      accent: "#75683f",
      accent2: "#d3c28d",
      panel: "#faf4e8",
      title: "#2b271e",
      muted: "#665e4d",
      rule: "#dacfb8",
      proof: "#a66f28",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Same names, no semantic geometry.",
        "The failure path becomes a flat storyboard.",
        "Before/after returns to equal blocks.",
        "The product proof is only a label set.",
        "The climax does not know which object owns the frame.",
        "The close names the gate without binding it.",
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
    visibleSemanticAssetLabels: 0,
    visualModuleIds: new Set(),
    semanticGeometrySlots: [],
    layoutSignatureTarget: "",
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun244Module(metrics, functionName) {
  metrics.visualModuleIds.add(functionName);
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

function registerSemanticGeometry(metrics, slots, layoutSignatureTarget) {
  metrics.semanticGeometrySlots = slots.map((slot) => ({ ...slot }));
  metrics.visibleSemanticAssetLabels += slots.length;
  metrics.layoutSignatureTarget = layoutSignatureTarget;
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

function armUsesFullRun244Data(arm) {
  return arm.armId === "run2_44_full_semantic_geometry_compiler";
}

function armUsesNameOnlyRun243Data(arm) {
  return arm.armId === "bad_run2_43_name_only_geometry";
}

function assertRun244ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun244Data(arm)) {
    for (const input of RUN2_44_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesNameOnlyRun243Data(arm)) {
    for (const input of RUN2_44_NAME_ONLY_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow name-only input ${input}`);
    }
    for (const input of [
      RUN2_44_INPUTS.run243WorkflowResult,
      RUN2_44_INPUTS.editorialCompositionTypographyMemory,
      RUN2_44_INPUTS.visualAssetSemanticsWorkflowGates,
      RUN2_44_INPUTS.run244DataflowReadinessAudit,
    ]) {
      if (allowed.has(input) || !forbidden.has(input)) throw new Error(`${arm.armId} must block ${input}`);
    }
    return;
  }
  for (const input of RUN2_44_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun244PackJsonForArm(arm, relPath) {
  assertRun244ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (!armUsesFullRun244Data(arm) && !armUsesNameOnlyRun243Data(arm)) {
    throw new Error(`${arm.armId} cannot read Run 2.43/2.44 pack data`);
  }
  return readJson(relPath);
}

function validateRun244SemanticGeometryCompiler(data) {
  const {
    run243WorkflowResult,
    semanticVisualAssetMemory,
    editorialCompositionTypographyMemory,
    visualAssetSemanticsWorkflowGates,
    run244DataflowReadinessAudit,
    commercialUsecaseBank,
    sources,
  } = data;
  if (run243WorkflowResult?.status !== "run2_43_visual_asset_semantics_workflow_ready_public_blocked") {
    throw new Error("Run 2.44 must consume Run 2.43 workflow result");
  }
  if (semanticVisualAssetMemory?.status !== "run2_43_semantic_visual_asset_memory_ready_public_blocked") {
    throw new Error("Run 2.44 semantic visual asset memory status mismatch");
  }
  if (editorialCompositionTypographyMemory?.status !== "run2_43_editorial_composition_typography_memory_ready_public_blocked") {
    throw new Error("Run 2.44 editorial typography memory status mismatch");
  }
  if (visualAssetSemanticsWorkflowGates?.status !== "run2_43_visual_asset_semantics_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.44 workflow gates status mismatch");
  }
  if (
    run244DataflowReadinessAudit?.status !== "run2_44_dataflow_readiness_blocked" ||
    run244DataflowReadinessAudit?.bug_confirmed !== true
  ) {
    throw new Error("Run 2.44 preflight audit must confirm the dataflow bug before rerun");
  }
  if (run244DataflowReadinessAudit?.next_rerun_gate?.visual_geometry_must_be_data_bound !== true) {
    throw new Error("Run 2.44 preflight gate must require data-bound geometry");
  }
  const usecase = (commercialUsecaseBank?.usecases ?? []).find((item) => item.id === selectedUsecaseId);
  if (!usecase) throw new Error("Run 2.44 missing selected commercial usecase");
  if (!Array.isArray(sources?.sources) || sources.sources.length < 4) throw new Error("Run 2.44 missing sources");
  const semanticAssets = semanticVisualAssetMemory.semantic_visual_asset_records ?? [];
  const editorialRecords = editorialCompositionTypographyMemory.editorial_composition_typography_records ?? [];
  const gates = visualAssetSemanticsWorkflowGates.visual_asset_semantics_workflow_gates ?? [];
  if (semanticAssets.length !== 18 || editorialRecords.length !== 6 || gates.length !== 6) {
    throw new Error("Run 2.44 must consume eighteen semantic assets, six editorial records, and six workflow gates");
  }
  for (const role of baseSlides.map((slide) => slide.role)) {
    const roleAssets = semanticAssets.filter((asset) => asset.role === role);
    const editorial = editorialRecords.find((record) => record.role === role);
    const gate = gates.find((record) => record.role === role);
    if (roleAssets.length !== 3 || !editorial || !gate) throw new Error(`Run 2.44 missing role contract for ${role}`);
    const assetIds = roleAssets.map((asset) => asset.semantic_asset_id);
    if (JSON.stringify(assetIds) !== JSON.stringify(editorial.required_semantic_asset_ids)) {
      throw new Error(`Run 2.44 semantic/editorial id mismatch for ${role}`);
    }
    if (JSON.stringify(assetIds) !== JSON.stringify(gate.required_semantic_asset_ids)) {
      throw new Error(`Run 2.44 semantic/gate id mismatch for ${role}`);
    }
    if (gate.required_editorial_typography_memory_id !== editorial.editorial_typography_memory_id) {
      throw new Error(`Run 2.44 editorial/gate id mismatch for ${role}`);
    }
  }
}

function loadRun244ContractData(arm) {
  const run243WorkflowResult = readRun244PackJsonForArm(arm, RUN2_44_INPUTS.run243WorkflowResult);
  const semanticVisualAssetMemory = readRun244PackJsonForArm(arm, RUN2_44_INPUTS.semanticVisualAssetMemory);
  const editorialCompositionTypographyMemory = readRun244PackJsonForArm(
    arm,
    RUN2_44_INPUTS.editorialCompositionTypographyMemory,
  );
  const visualAssetSemanticsWorkflowGates = readRun244PackJsonForArm(arm, RUN2_44_INPUTS.visualAssetSemanticsWorkflowGates);
  const run244DataflowReadinessAudit = readRun244PackJsonForArm(arm, RUN2_44_INPUTS.run244DataflowReadinessAudit);
  const commercialUsecaseBank = readRun244PackJsonForArm(arm, RUN2_44_INPUTS.commercialUsecaseBank);
  const sources = readRun244PackJsonForArm(arm, RUN2_44_INPUTS.sources);
  const data = {
    run243WorkflowResult,
    semanticVisualAssetMemory,
    editorialCompositionTypographyMemory,
    visualAssetSemanticsWorkflowGates,
    run244DataflowReadinessAudit,
    commercialUsecaseBank,
    sources,
  };
  validateRun244SemanticGeometryCompiler(data);
  return {
    ...data,
    usecase: commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_44_run2_43_workflow_consumed_for_semantic_geometry_contract_ready",
  };
}

function loadRun244NameOnlyData(arm) {
  const semanticVisualAssetMemory = readRun244PackJsonForArm(arm, RUN2_44_INPUTS.semanticVisualAssetMemory);
  const commercialUsecaseBank = readRun244PackJsonForArm(arm, RUN2_44_INPUTS.commercialUsecaseBank);
  const sources = readRun244PackJsonForArm(arm, RUN2_44_INPUTS.sources);
  return {
    semanticVisualAssetMemory,
    commercialUsecaseBank,
    sources,
    usecase: commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
  };
}

function selectRun244ForSlide(role, contractData) {
  const semanticAssets = (contractData.semanticVisualAssetMemory?.semantic_visual_asset_records ?? []).filter(
    (item) => item.role === role,
  );
  const editorial = (contractData.editorialCompositionTypographyMemory?.editorial_composition_typography_records ?? []).find(
    (item) => item.role === role,
  );
  const gate = (contractData.visualAssetSemanticsWorkflowGates?.visual_asset_semantics_workflow_gates ?? []).find(
    (item) => item.role === role,
  );
  if (semanticAssets.length !== 3 || !editorial || !gate) throw new Error(`Run 2.44 missing role ${role}`);
  return semanticGeometryTransform({
    semanticAssets,
    editorial,
    gate,
    usecase: contractData.usecase,
    sources: contractData.sources,
  });
}

function semanticGeometryTransform(selection) {
  const { semanticAssets, editorial, gate, usecase, sources } = selection;
  const sourceTitles = (sources?.sources ?? [])
    .filter((source) => (semanticAssets[0]?.source_ids ?? []).includes(source.id))
    .map((source) => source.title)
    .slice(0, 3);
  const semanticAssetIds = semanticAssets.map((asset) => asset.semantic_asset_id);
  const semanticSurfaceTypes = semanticAssets.map((asset) => asset.source_run2_41_surface_type);
  const businessDetails = [
    `audience: ${compactText(usecase?.audience, 58)}`,
    `decision: ${compactText(usecase?.business_decision, 58)}`,
    `mission: ${compactText(usecase?.deck_mission, 58)}`,
    `must show: ${(usecase?.must_show ?? []).slice(0, 2).join(" / ")}`,
    `layout: ${editorial.layout_signature_target}`,
    `first read: ${compactText(editorial.first_read_scene_object, 58)}`,
  ];
  const geometryPlan = layoutFromRun243Memory({
    semanticAssets,
    editorial,
    gate,
    usecase,
    sourceTitles,
  });
  return {
    semanticAssets,
    semanticAssetIds,
    semanticSurfaceTypes,
    editorial,
    gate,
    usecase,
    sourceTitles,
    businessDetails,
    geometryPlan,
    run2_44_geometry_source: RUN2_44_GEOMETRY_SOURCE,
    publicHeadline: editorial.first_read_scene_object,
    publicOutcome: usecase?.deck_mission ?? "data-bound code-generated presentation output",
    sourceBoundaryStatus: "derived_only_no_copied_media",
  };
}

function layoutFromRun243Memory(selection) {
  const { semanticAssets, editorial, gate, sourceTitles } = selection;
  const weight = Number(editorial.primary_visual_weight_target ?? 0.6);
  const signature = String(editorial.layout_signature_target ?? "");
  const role = editorial.role;
  const slotFor = (asset, index, box, slotRole, emphasis) => ({
    asset_id: asset.semantic_asset_id,
    surface_type: asset.source_run2_41_surface_type,
    semantic_object: asset.usecase_specific_semantic_object,
    slot_role: slotRole,
    emphasis,
    x: Math.round(box.x),
    y: Math.round(box.y),
    w: Math.round(box.w),
    h: Math.round(box.h),
  });

  let boxes;
  if (signature.includes("small_before_large_after")) {
    boxes = [
      { x: 92, y: 216, w: 238, h: 164, slotRole: "small_before_state", emphasis: 0.34 },
      { x: 414, y: 130, w: 650, h: 390, slotRole: "large_after_state", emphasis: weight },
      { x: 138, y: 478, w: 912, h: 80, slotRole: "business_delta_strip", emphasis: 0.28 },
    ];
  } else if (signature.includes("failure_storyboard")) {
    boxes = [
      { x: 112, y: 222, w: 288, h: 172, slotRole: "collapsed_failure_path", emphasis: 0.35 },
      { x: 442, y: 180, w: 542, h: 228, slotRole: "selected_route_scene", emphasis: weight },
      { x: 226, y: 466, w: 720, h: 84, slotRole: "decision_risk_lane", emphasis: 0.3 },
    ];
  } else if (signature.includes("working_product_surface")) {
    boxes = [
      { x: 114, y: 194, w: 700, h: 302, slotRole: "working_product_surface", emphasis: weight },
      { x: 846, y: 208, w: 250, h: 116, slotRole: "deck_preview_support", emphasis: 0.3 },
      { x: 846, y: 358, w: 250, h: 116, slotRole: "review_state_support", emphasis: 0.28 },
    ];
  } else if (signature.includes("single_cinematic")) {
    boxes = [
      { x: 184, y: 150, w: 792, h: 344, slotRole: "cinematic_result_object", emphasis: weight },
      { x: 118, y: 522, w: 286, h: 68, slotRole: "before_state_chip", emphasis: 0.2 },
      { x: 456, y: 522, w: 522, h: 68, slotRole: "supporting_proof_rail", emphasis: 0.28 },
    ];
  } else if (signature.includes("decision_room")) {
    boxes = [
      { x: 118, y: 250, w: 280, h: 142, slotRole: "review_decision_surface", emphasis: weight },
      { x: 474, y: 218, w: 300, h: 172, slotRole: "release_readiness_wall", emphasis: 0.44 },
      { x: 850, y: 252, w: 262, h: 140, slotRole: "next_run_action_surface", emphasis: 0.32 },
    ];
  } else {
    const heroW = Math.round(360 + weight * 250);
    boxes = [
      { x: 570, y: 126, w: heroW, h: 392, slotRole: "generated_deck_hero", emphasis: weight },
      { x: 90, y: 294, w: 330, h: 132, slotRole: "memory_control_field", emphasis: 0.32 },
      { x: 444, y: 500, w: 522, h: 66, slotRole: "benchmark_cue", emphasis: 0.22 },
    ];
  }

  const slots = semanticAssets.map((asset, index) => slotFor(asset, index, boxes[index], boxes[index].slotRole, boxes[index].emphasis));
  return {
    role,
    layout_signature_target: signature,
    first_read_scene_object: editorial.first_read_scene_object,
    primary_visual_weight_target: weight,
    visual_rhythm_id: editorial.visual_rhythm_id,
    gate_id: gate.gate_id,
    source_titles: sourceTitles,
    slots,
  };
}

function drawRun244SemanticGeometryRail(slide, arm, selection, metrics, x, y, w, variant = "light") {
  const h = 118;
  const fill = variant === "dark" ? "#1b2630" : C.white;
  const line = variant === "dark" ? "#354654" : "#d8cfbf";
  const textColor = variant === "dark" ? "#f4f8fb" : arm.palette.title;
  const muted = variant === "dark" ? "#c4d3dc" : arm.palette.muted;
  rect(slide, x, y, w, h, fill, colorLine(line, 1));
  text(slide, "scene contract", x + 18, y + 12, 170, 13, {
    fontSize: 8.5,
    mono: true,
    bold: true,
    color: muted,
  });
  const details = (selection.businessDetails ?? []).slice(0, 4);
  details.forEach((detail, index) => {
    const rowX = x + 18 + (index % 2) * Math.floor((w - 58) / 2);
    const rowY = y + 34 + Math.floor(index / 2) * 24;
    text(slide, compactText(detail, 52), rowX, rowY, Math.floor((w - 64) / 2), 16, {
      fontSize: 8.1,
      color: index === 0 ? textColor : muted,
      bold: index === 0,
    });
    registerText(metrics, detail);
  });
  selection.semanticSurfaceTypes.slice(0, 3).forEach((surface, index) => {
    const slot = Math.floor((w - 54) / 3);
    chip(
      slide,
      compactText(surface, 24),
      x + 18 + index * slot,
      y + h - 34,
      Math.max(92, slot - 8),
      variant === "dark" ? "#263642" : "#eef3f2",
      variant === "dark" ? "#eaf4f8" : arm.palette.accent,
    );
    registerText(metrics, surface);
  });
}

function drawSlotObject(slide, arm, slot, index, metrics, variant = "light") {
  const fills = variant === "dark" ? ["#f5f7fa", "#263846", "#33434f"] : [arm.palette.proof, "#eef3f2", C.midnight];
  const textColors = variant === "dark" ? [C.ink, C.white, C.white] : [C.white, arm.palette.title, C.white];
  const fill = fills[index] ?? fills[0];
  const textColor = textColors[index] ?? C.white;
  const line = index === 0 ? colorLine(fill, 2) : colorLine("#cbd5d9", 1);
  rect(slide, slot.x + 14, slot.y + 16, slot.w, slot.h, variant === "dark" ? "#0d1117" : "#ded8cb", colorLine("transparent", 0));
  rect(slide, slot.x, slot.y, slot.w, slot.h, fill, line);
  const label = slot.surface_type || slot.slot_role;
  text(slide, compactText(label, 30), slot.x + 22, slot.y + 24, Math.max(80, slot.w - 44), 18, {
    fontSize: index === 0 ? 15 : 11,
    mono: index !== 0,
    title: index === 0,
    bold: true,
    color: textColor,
  });
  text(slide, compactText(slot.semantic_object, index === 0 ? 96 : 64), slot.x + 22, slot.y + slot.h - 54, Math.max(80, slot.w - 44), 34, {
    fontSize: index === 0 ? 12.2 : 9.5,
    color: textColor,
  });
  if (index === 0) {
    rect(slide, slot.x + 28, slot.y + 64, Math.max(110, slot.w * 0.36), 9, variant === "dark" ? C.signal : C.white);
    rect(slide, slot.x + 28, slot.y + 98, Math.max(86, slot.w * 0.24), 7, variant === "dark" ? C.cyan : "#ffd1c9");
  } else {
    ellipse(slide, slot.x + slot.w - 44, slot.y + 18, 18, 18, variant === "dark" ? C.cyan : arm.palette.accent2, colorLine("transparent", 0));
  }
  registerText(metrics, `${label} ${slot.semantic_object}`);
  registerProof(metrics, index === 0 ? 2 : 1);
}

function drawRun244SemanticGeometryScene(slide, arm, spec, selection, metrics, moduleName) {
  registerRun244Module(metrics, moduleName);
  const plan = selection.geometryPlan;
  const dark = spec.role === "climax";
  if (dark) {
    rect(slide, 70, 98, 1080, 530, C.midnight, colorLine(C.midnight, 1));
    text(slide, "The result object owns the frame.", 104, 126, 650, 48, {
      fontSize: 41,
      title: true,
      bold: true,
      color: C.white,
    });
    registerText(metrics, "The result object owns the frame");
  } else {
    text(slide, compactText(spec.title, 74), 76, 112, spec.role === "cover" ? 470 : 590, 70, {
      fontSize: spec.role === "cover" ? 37 : 34,
      title: true,
      bold: true,
      color: arm.palette.title,
    });
    registerText(metrics, spec.title);
    text(slide, compactText(selection.publicHeadline, 110), 80, spec.role === "cover" ? 210 : 184, 470, 42, {
      fontSize: 13.5,
      color: arm.palette.muted,
    });
    registerText(metrics, selection.publicHeadline);
  }
  plan.slots.forEach((slot, index) => drawSlotObject(slide, arm, slot, index, metrics, dark ? "dark" : "light"));
  if (spec.role === "contrast") {
    rect(slide, 334, 292, 70, 5, C.signal);
    rect(slide, 364, 276, 22, 38, C.signal);
  }
  if (spec.role === "setup") {
    rect(slide, 400, 322, 42, 6, C.signal);
    rect(slide, 430, 304, 10, 42, C.signal);
  }
  if (spec.role === "proof") {
    rect(slide, 148, 244, 640, 42, C.midnight);
    text(slide, "active decision lane", 172, 258, 180, 12, { fontSize: 10, mono: true, bold: true, color: C.white });
    registerText(metrics, "active decision lane");
  }
  if (spec.role === "close") {
    rect(slide, 398, 316, 76, 6, C.signal);
    rect(slide, 774, 316, 76, 6, C.signal);
  }
  drawRun244SemanticGeometryRail(slide, arm, selection, metrics, dark ? 120 : 82, dark ? 494 : 546, dark ? 900 : 1038, dark ? "dark" : "light");
  registerSemanticGeometry(metrics, plan.slots, plan.layout_signature_target);
  const hero = plan.slots[0];
  registerPresentationSurface(metrics, hero.x, hero.y, hero.w, hero.h, plan.primary_visual_weight_target);
  registerZones(metrics, 3);
}

function drawRun244CoverSemanticGeometry(slide, arm, spec, selection, metrics) {
  drawRun244SemanticGeometryScene(slide, arm, spec, selection, metrics, "drawRun244CoverSemanticGeometry");
}

function drawRun244SetupSemanticGeometry(slide, arm, spec, selection, metrics) {
  drawRun244SemanticGeometryScene(slide, arm, spec, selection, metrics, "drawRun244SetupSemanticGeometry");
}

function drawRun244ContrastSemanticGeometry(slide, arm, spec, selection, metrics) {
  drawRun244SemanticGeometryScene(slide, arm, spec, selection, metrics, "drawRun244ContrastSemanticGeometry");
}

function drawRun244ProofSemanticGeometry(slide, arm, spec, selection, metrics) {
  drawRun244SemanticGeometryScene(slide, arm, spec, selection, metrics, "drawRun244ProofSemanticGeometry");
}

function drawRun244ClimaxSemanticGeometry(slide, arm, spec, selection, metrics) {
  drawRun244SemanticGeometryScene(slide, arm, spec, selection, metrics, "drawRun244ClimaxSemanticGeometry");
}

function drawRun244CloseSemanticGeometry(slide, arm, spec, selection, metrics) {
  drawRun244SemanticGeometryScene(slide, arm, spec, selection, metrics, "drawRun244CloseSemanticGeometry");
}

const RUN2_44_MODULES = {
  cover: drawRun244CoverSemanticGeometry,
  setup: drawRun244SetupSemanticGeometry,
  contrast: drawRun244ContrastSemanticGeometry,
  proof: drawRun244ProofSemanticGeometry,
  climax: drawRun244ClimaxSemanticGeometry,
  close: drawRun244CloseSemanticGeometry,
};

function selectNameOnlySurfacesForSlide(role, nameOnlyData) {
  return (nameOnlyData.semanticVisualAssetMemory?.semantic_visual_asset_records ?? [])
    .filter((asset) => asset.role === role)
    .map((asset) => asset.source_run2_41_surface_type)
    .slice(0, 3);
}

function drawBadRun243NameOnlyGeometrySlide(slide, arm, spec, nameOnlyData, metrics) {
  text(slide, spec.title, 76, 118, 540, 74, {
    fontSize: 34,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, compactText(spec.claim, 100), 80, 214, 456, 46, { fontSize: 14, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  const surfaces = selectNameOnlySurfacesForSlide(spec.role, nameOnlyData);
  const panel = { x: 614, y: 136, w: 444, h: 336 };
  rect(slide, panel.x + 16, panel.y + 18, panel.w, panel.h, "#ddcfb8", colorLine("#ddcfb8", 1));
  rect(slide, panel.x, panel.y, panel.w, panel.h, arm.palette.panel, colorLine(arm.palette.rule, 1));
  surfaces.forEach((surface, index) => {
    const x = panel.x + 34 + index * 132;
    rect(slide, x, panel.y + 62, 104, 126, "#dac28b", colorLine("#c5ad79", 1));
    text(slide, compactText(surface, 20), x + 12, panel.y + 210, 92, 28, {
      fontSize: 11,
      title: true,
      bold: true,
      color: arm.palette.title,
      align: "center",
    });
    registerText(metrics, surface);
  });
  text(slide, "names visible; no id, gate, or data-bound geometry", panel.x + 36, panel.y + 276, 334, 28, {
    fontSize: 12,
    color: arm.palette.muted,
  });
  registerText(metrics, "names visible no id gate or data-bound geometry");
  chip(slide, "name-only control", 84, 548, 214, C.white, arm.palette.accent);
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
  text(slide, "Readable, but no Run 2.43 workflow consumption.", 108, 382, 420, 54, {
    fontSize: 20,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, "Readable but no Run 2.43 workflow consumption");
  registerPresentationSurface(metrics, 84, 318, 1042, 212, 0.35);
}

function renderRun244Slide(presentation, spec, arm, n, contractData, nameOnlyData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun244Data(arm)) {
    const selection = selectRun244ForSlide(spec.role, contractData);
    RUN2_44_MODULES[spec.role](slide, arm, spec, selection, metrics);
  } else if (armUsesNameOnlyRun243Data(arm)) {
    drawBadRun243NameOnlyGeometrySlide(slide, arm, spec, nameOnlyData, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertRun244ArmInputBoundaries(arm);
  const fullRun244 = armUsesFullRun244Data(arm);
  const badNameOnly = armUsesNameOnlyRun243Data(arm);
  const fullData = fullRun244 ? context.fullData ?? loadRun244ContractData(arm) : null;
  const nameOnlyData = badNameOnly ? context.nameOnlyData ?? loadRun244NameOnlyData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun244 || badNameOnly ? selectedUsecaseId : "",
    source_data_workflow_run_id: fullRun244 ? "2.43" : "",
    source_dataflow_audit_run_id: fullRun244 ? "2.44-preflight" : "",
    run2_44_semantic_geometry_status: fullRun244
      ? RUN2_44_FULL_STATUS
      : badNameOnly
        ? RUN2_44_BAD_STATUS
        : "boundary_control_no_run2_43_workflow_consumption",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.44 semantic geometry rerun from scripts/generate_ppt_run2_44_semantic_geometry_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun244 ? selectRun244ForSlide(slide.role, fullData) : null;
      const semanticIds = fullRun244 ? selection.semanticAssetIds : [];
      const codeModuleIds = fullRun244
        ? hasRenderedMetrics
          ? Array.from(roleMetrics.visualModuleIds)
          : [RUN2_44_MODULES[slide.role].name]
        : [];
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_43_semantic_visual_asset_ids: semanticIds,
        run2_43_semantic_visual_asset_surface_types: fullRun244
          ? selection.semanticSurfaceTypes
          : badNameOnly
            ? selectNameOnlySurfacesForSlide(slide.role, nameOnlyData)
            : [],
        run2_43_editorial_typography_memory_id: fullRun244 ? selection.editorial.editorial_typography_memory_id : "",
        run2_43_visual_asset_semantics_gate_id: fullRun244 ? selection.gate.gate_id : "",
        run2_43_visual_asset_semantics_execution_status: fullRun244
          ? "consumed_before_native_ppt_drawing"
          : badNameOnly
            ? "not_consumed_name_only_control"
            : "not_consumed_boundary_control",
        run2_43_source_boundary_status: fullRun244 ? "derived_only_no_copied_media" : "",
        run2_43_layout_signature_target: fullRun244 ? selection.geometryPlan.layout_signature_target : "",
        run2_43_primary_visual_weight_target: fullRun244 ? selection.geometryPlan.primary_visual_weight_target : 0,
        run2_44_data_bound_geometry: fullRun244,
        run2_44_geometry_source: fullRun244 ? RUN2_44_GEOMETRY_SOURCE : "",
        run2_44_layout_signature_target: fullRun244 ? selection.geometryPlan.layout_signature_target : "",
        run2_44_semantic_asset_geometry_slots: fullRun244 ? roleMetrics.semanticGeometrySlots : [],
        run2_44_code_module_ids: codeModuleIds,
        run2_44_geometry_compiler_policy: fullRun244 ? RUN2_44_POLICY : badNameOnly ? "name_only_no_semantic_geometry_binding" : "",
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

function assertRun244SemanticGeometrySelfCheck(trace) {
  if (trace.arm_id === "run2_44_full_semantic_geometry_compiler") {
    if (trace.run2_44_semantic_geometry_status !== RUN2_44_FULL_STATUS) {
      throw new Error("Run 2.44 full trace did not consume Run 2.43 workflow");
    }
    for (const slide of trace.slides) {
      if ((slide.run2_43_semantic_visual_asset_ids ?? []).length !== 3) {
        throw new Error(`Run 2.44 full slide ${slide.slide_id} missing semantic asset ids`);
      }
      if (!String(slide.run2_43_editorial_typography_memory_id ?? "").startsWith("editorial_typography_2_43_")) {
        throw new Error(`Run 2.44 full slide ${slide.slide_id} missing editorial memory id`);
      }
      if (!String(slide.run2_43_visual_asset_semantics_gate_id ?? "").startsWith("gate_2_43_")) {
        throw new Error(`Run 2.44 full slide ${slide.slide_id} missing gate id`);
      }
      if (slide.run2_44_data_bound_geometry !== true || slide.run2_44_geometry_source !== RUN2_44_GEOMETRY_SOURCE) {
        throw new Error(`Run 2.44 full slide ${slide.slide_id} missing data-bound geometry`);
      }
      if ((slide.run2_44_semantic_asset_geometry_slots ?? []).length !== 3) {
        throw new Error(`Run 2.44 full slide ${slide.slide_id} missing semantic geometry slots`);
      }
      if ((slide.run2_44_code_module_ids ?? []).length !== 1 || !slide.run2_44_code_module_ids[0].startsWith("drawRun244")) {
        throw new Error(`Run 2.44 full slide ${slide.slide_id} missing Run 2.44 module`);
      }
    }
  }
  if (trace.arm_id === "bad_run2_43_name_only_geometry") {
    for (const slide of trace.slides) {
      if ((slide.run2_43_semantic_visual_asset_ids ?? []).length !== 0) {
        throw new Error(`Run 2.44 bad slide ${slide.slide_id} leaked semantic asset ids`);
      }
      if (slide.run2_44_data_bound_geometry !== false) {
        throw new Error(`Run 2.44 bad slide ${slide.slide_id} claimed data-bound geometry`);
      }
      if (slide.run2_43_visual_asset_semantics_execution_status !== "not_consumed_name_only_control") {
        throw new Error(`Run 2.44 bad slide ${slide.slide_id} has wrong name-only status`);
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

function buildRun244FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-44-four-arm-contact-sheet.png"),
    "Run 2.44 semantic geometry comparison",
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
      "required proof objects: Run 2.43 semantic visual asset ids, editorial typography memory id, workflow gate id, and data-bound geometry slots",
      "source requirements: full arm reads Run 2.43 workflow result, semantic memory, typography memory, workflow gates, Run 2.44 preflight audit, usecase bank, and sources before native PPT drawing",
      "negative control: bad arm can reuse surface names only, without semantic ids, typography memory, gate ids, or geometry compiler",
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
  const fullData = armUsesFullRun244Data(arm) ? loadRun244ContractData(arm) : null;
  const nameOnlyData = armUsesNameOnlyRun243Data(arm) ? loadRun244NameOnlyData(arm) : null;
  const slides = arm.slides.map((slide, index) =>
    renderRun244Slide(presentation, slide, arm, index + 1, fullData, nameOnlyData, metricsByRole),
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

  const trace = traceFor(arm, { fullData, nameOnlyData, metricsByRole });
  assertRun244SemanticGeometrySelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_44_semantic_geometry_arms.mjs",
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

function writeRun244Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-44-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-44-bad-run2-43-name-only-geometry/trace_manifest.json`);
  const fullSlidesWithIds = fullTrace.slides.filter((slide) => (slide.run2_43_semantic_visual_asset_ids ?? []).length === 3).length;
  const fullSlidesWithGeometry = fullTrace.slides.filter((slide) => slide.run2_44_data_bound_geometry === true).length;
  const result = {
    schema_version: 1,
    run_id: "2.44",
    status: "run2_44_semantic_geometry_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_data_workflow_run_id: "2.43",
    source_dataflow_audit_run_id: "2.44-preflight",
    database_expansion: false,
    workflow_expansion: false,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_43_workflow_result: RUN2_44_INPUTS.run243WorkflowResult,
      semantic_visual_asset_memory: RUN2_44_INPUTS.semanticVisualAssetMemory,
      editorial_composition_typography_memory: RUN2_44_INPUTS.editorialCompositionTypographyMemory,
      visual_asset_semantics_workflow_gates: RUN2_44_INPUTS.visualAssetSemanticsWorkflowGates,
      run2_44_dataflow_readiness_audit: RUN2_44_INPUTS.run244DataflowReadinessAudit,
      commercial_usecase_bank: RUN2_44_INPUTS.commercialUsecaseBank,
      sources: RUN2_44_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_44_semantic_geometry_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_44_full_semantic_geometry_compiler",
      best_internal_arm_verdict: "Run 2.43 semantic workflow now drives native PPT geometry before drawing",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: "semantic_visual_asset_geometry_binding",
      source_data_status: RUN2_44_FULL_STATUS,
      run2_44_geometry_source: RUN2_44_GEOMETRY_SOURCE,
      full_slides_with_run2_43_semantic_asset_ids: fullSlidesWithIds,
      full_slides_with_data_bound_geometry: fullSlidesWithGeometry,
      full_slides_with_editorial_typography_memory_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_43_editorial_typography_memory_id ?? "").startsWith("editorial_typography_2_43_"),
      ).length,
      full_slides_with_visual_asset_semantics_gate_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_43_visual_asset_semantics_gate_id ?? "").startsWith("gate_2_43_"),
      ).length,
      bad_control_slides_without_semantic_asset_ids: badTrace.slides.filter((slide) => (slide.run2_43_semantic_visual_asset_ids ?? []).length === 0).length,
      repair_modules: Object.values(RUN2_44_MODULES).map((fn) => fn.name),
    },
    control_boundary: {
      bad_run2_43_name_only_geometry:
        "may see surface names from Run 2.43 semantic memory, but must not bind semantic asset ids, editorial typography memory, workflow gate ids, or data-bound geometry slots",
      prompt_only: "commercial_case_only_no_run2_43_workflow",
      run1_5_skill: "prior_baseline_no_run2_43_workflow",
    },
    visual_quality_boundary:
      "semantic geometry dataflow proof only; public video-grade aesthetics, motion, typography, and human release approval remain blocked",
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
      "audit_run2_44_semantic_geometry_against_visual_quality_then_continue_same_five_layers_with_data_and_workflow_thickening",
  };
  const resultJson = path.join(root, pack, "results", "run2_44_semantic_geometry_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_44_semantic_geometry_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.44 Semantic Geometry Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.44 consumes Run 2.43 before native PPT drawing. The full arm binds semantic visual asset ids, editorial typography memory, and workflow gates, then turns those records into data-bound geometry slots.",
      "",
      "This fixes the suspected workflow bug from the preflight audit: the latest visible PPT is no longer only Run 2.41 with post-hoc data notes. The generated full arm now carries `run2_43_semantic_visual_asset_ids`, `run2_43_editorial_typography_memory_id`, `run2_43_visual_asset_semantics_gate_id`, and `run2_44_data_bound_geometry` in trace.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_44_full_semantic_geometry_compiler`",
      "- `bad_run2_43_name_only_geometry`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_44_full_semantic_geometry_compiler`.",
      "",
      "Quality delta: `semantic_visual_asset_geometry_binding`. All six full-arm slides contain three Run 2.43 semantic visual asset ids and data-bound geometry slots.",
      "",
      "The negative control `bad_run2_43_name_only_geometry` can repeat surface names, but it has no semantic visual asset ids, no gate id, and no data-bound geometry.",
      "",
      "Public release remains blocked. This proves dataflow and workflow consumption, not final public-video-grade aesthetics.",
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
  const fourArmSheet = buildRun244FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_44_semantic_geometry_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_44_semantic_geometry_rerun_summary.json"), runSummary);
  writeRun244Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_44_INPUTS,
  RUN2_44_FULL_DATA_INPUTS,
  armSpecs,
  assertRun244ArmInputBoundaries,
  assertRun244SemanticGeometrySelfCheck,
  drawRun244SemanticGeometryRail,
  layoutFromRun243Memory,
  loadRun244ContractData,
  main,
  readRun244PackJsonForArm,
  registerRun244Module,
  selectRun244ForSlide,
  semanticGeometryTransform,
  traceFor,
  validateRun244SemanticGeometryCompiler,
};
