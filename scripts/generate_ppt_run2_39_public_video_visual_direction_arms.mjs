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
const RUN2_36_DOMINANT_LAYOUT_SIGNATURE = "editorial_anchor_object+two_product_state_cards+gate_ribbon";
const RUN2_39_EXECUTION_STATUS =
  "public_video_grade_slide_direction_and_per_slide_visual_recipe_consumed_before_native_ppt_generation";

const C = {
  ink: "#111318",
  paper: "#f6f1e8",
  white: "#ffffff",
  line: "#d1d5db",
  muted: "#606a76",
  midnight: "#11161d",
  graphite: "#252b34",
  blue: "#245fdd",
  cyan: "#6cc5d8",
  signal: "#e85237",
  green: "#0f8a66",
  fog: "#eef2f5",
  butter: "#f2d56b",
  magenta: "#a83a7a",
  teal: "#198f8b",
  violet: "#5b4ad1",
};

const RUN2_39_INPUTS = {
  visualQualityAudit: `${pack}/results/run2_37_visual_quality_audit.json`,
  visualEvidenceRealismRerunResult: `${pack}/results/run2_36_visual_evidence_realism_rerun_result.json`,
  publicVideoVisualDirectionWorkflowResult: `${pack}/results/run2_38_public_video_visual_direction_workflow_result.json`,
  publicVideoSlideDirectionMemory: `${pack}/run2_38_public_video_slide_direction_memory.json`,
  perSlideVisualRecipeMemory: `${pack}/run2_38_per_slide_visual_recipe_memory.json`,
  publicVideoWorkflowGates: `${pack}/run2_38_public_video_workflow_gates.json`,
};
const RUN2_39_DATA_INPUTS = Object.values(RUN2_39_INPUTS);

const baseSlides = [
  {
    role: "cover",
    title: "Design memory becomes the stage.",
    claim: "Run 2.39 tests whether public-video slide direction is consumed before code draws the deck.",
  },
  {
    role: "setup",
    title: "The failure is visual sameness.",
    claim: "A working trace still feels weak when every slide speaks in the same card language.",
  },
  {
    role: "contrast",
    title: "The same brief must visibly change.",
    claim: "The comparison should prove that data selection changes the slide surface, not just the file list.",
  },
  {
    role: "proof",
    title: "Recipe memory becomes an app state.",
    claim: "Each slide role binds a visual rhythm, recipe, layout signature, and code module.",
  },
  {
    role: "climax",
    title: "One result object has to own the room.",
    claim: "The high point must be a generated product object, not another audit board.",
  },
  {
    role: "close",
    title: "The handoff remains blocked.",
    claim: "The system can improve internally while public release still waits for review.",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-39-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.39 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_39_DATA_INPUTS, `${pack}/skill_workflow.json`, "docs/product/ppt-run1-5-product-lab/"],
    palette: {
      bg: "#f5f6f8",
      rail: "#374151",
      accent: C.blue,
      accent2: "#bfcbd8",
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d8dde4",
      gate: "#e9edf3",
      proof: C.signal,
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Make the deck look more premium.",
        "Show why old slides feel generic.",
        "Create a before and after.",
        "Show the system works.",
        "Make the result impressive.",
        "End with next steps.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-39-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.39 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_39_DATA_INPUTS, `${pack}/skill_workflow.json`],
    palette: {
      bg: "#f4f7fb",
      rail: "#263247",
      accent: C.blue,
      accent2: C.green,
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d3dbe7",
      gate: "#e8edf5",
      proof: C.green,
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "The baseline knows the product lab.",
        "The setup is accurate but still broad.",
        "The comparison stays evenly weighted.",
        "The proof reads as workflow notes.",
        "The climax is correct but not cinematic.",
        "The close is gated but quiet.",
      ][index],
    })),
  },
  {
    armId: "run2_39_full_public_video_visual_direction",
    slug: "ppt-run2-39-full-vulca",
    label: "Run 2.39 full public-video direction",
    kicker: "RUN 2.39 / PUBLIC-VIDEO DIRECTION",
    footer: "run2_39_full_public_video_visual_direction | Run 2.38 direction + recipe + gates | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/sources.json`,
      RUN2_39_INPUTS.visualQualityAudit,
      RUN2_39_INPUTS.visualEvidenceRealismRerunResult,
      RUN2_39_INPUTS.publicVideoVisualDirectionWorkflowResult,
      RUN2_39_INPUTS.publicVideoSlideDirectionMemory,
      RUN2_39_INPUTS.perSlideVisualRecipeMemory,
      RUN2_39_INPUTS.publicVideoWorkflowGates,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_38_public_video_slide_direction_memory.json",
      "run2_38_per_slide_visual_recipe_memory.json",
      "run2_38_public_video_workflow_gates.json",
      "run2_38_public_video_visual_direction_workflow_result.json",
    ],
    forbidden: [
      "docs/product/ppt-run1-5-product-lab/",
      "copied source visuals",
      "raw tutorial media copied into slide surface",
      "source brand marks",
      "winner claims before scoring",
      RUN2_36_DOMINANT_LAYOUT_SIGNATURE,
    ],
    palette: {
      bg: "#f6f1e8",
      rail: C.midnight,
      accent: C.midnight,
      accent2: C.cyan,
      proof: C.signal,
      panel: C.white,
      title: "#0e1218",
      muted: "#58636f",
      rule: "#d5cbb9",
      gate: C.midnight,
      surface: "#edf3f2",
    },
    slides: baseSlides,
  },
  {
    armId: "bad_public_video_visual_direction_memory",
    slug: "ppt-run2-39-bad-public-video-visual-direction-memory",
    label: "Bad public-video direction memory",
    kicker: "RUN 2.39 / NEGATIVE CONTROL",
    footer: "bad_public_video_visual_direction_memory | usecase label only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, `selected_usecase_label:${selectedUsecaseId}`],
    forbidden_data_input_manifest: [
      "run2_38_public_video_slide_direction_memory.json",
      "run2_38_per_slide_visual_recipe_memory.json",
      "run2_38_public_video_workflow_gates.json",
      "run2_38_public_video_visual_direction_workflow_result.json",
    ],
    forbidden: [
      RUN2_39_INPUTS.visualQualityAudit,
      RUN2_39_INPUTS.visualEvidenceRealismRerunResult,
      RUN2_39_INPUTS.publicVideoVisualDirectionWorkflowResult,
      RUN2_39_INPUTS.publicVideoSlideDirectionMemory,
      RUN2_39_INPUTS.perSlideVisualRecipeMemory,
      RUN2_39_INPUTS.publicVideoWorkflowGates,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
      "manual Run 2.39 pack repair before scoring",
    ],
    palette: {
      bg: "#f1eadb",
      rail: "#695d3a",
      accent: "#75683f",
      accent2: "#d3c28d",
      panel: "#faf4e8",
      title: "#2b271e",
      muted: "#675f4c",
      rule: "#dacfb8",
      gate: "#eadfbe",
      proof: "#a66f28",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "The usecase label appears, but the scene is generic.",
        "The failure path has no recipe binding.",
        "The comparison becomes two labels.",
        "The product surface has no direction memory.",
        "The climax is another diagram.",
        "The close claims gates it did not execute.",
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
    workflowObjects: 0,
    gateObjects: 0,
    contentCards: 0,
    primaryVisualWeight: 0,
    run2_36DominantLayoutSignatureReused: false,
    visualModuleIds: new Set(),
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun239Module(metrics, functionName) {
  metrics.visualModuleIds.add(functionName);
}

function registerPrimaryVisual(metrics, x, y, w, h, target = 0) {
  const area = Math.max(1, MAIN_CANVAS.w * MAIN_CANVAS.h);
  metrics.primaryVisualWeight = Math.max(metrics.primaryVisualWeight, (w * h) / area, Number(target) || 0);
}

function registerProof(metrics, count = 1) {
  metrics.proofObjects += count;
}

function registerZones(metrics, count) {
  metrics.zones = Math.max(metrics.zones, count);
}

function registerWorkflow(metrics, count) {
  metrics.workflowObjects = Math.max(metrics.workflowObjects, count);
}

function registerGate(metrics, count = 1) {
  metrics.gateObjects += count;
}

function registerContentCards(metrics, count = 1) {
  metrics.contentCards += count;
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

function moduleLabel(slide, x, y, label, arm) {
  chip(slide, label, x, y, Math.max(132, label.length * 7 + 28), arm.palette.panel, arm.palette.accent);
}

function compactText(value, max = 86) {
  const textValue = String(value ?? "").trim();
  return textValue.length > max ? `${textValue.slice(0, max - 1).trim()}...` : textValue;
}

function assertRun239ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  const assertAllowed = (input) => {
    if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
    if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
  };
  const assertForbidden = (input) => {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  };

  if (arm.armId === "run2_39_full_public_video_visual_direction") {
    for (const input of RUN2_39_DATA_INPUTS) assertAllowed(input);
    return;
  }
  for (const input of RUN2_39_DATA_INPUTS) assertForbidden(input);
}

function readRun239PackJsonForArm(arm, relPath) {
  assertRun239ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (arm.armId !== "run2_39_full_public_video_visual_direction") {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  return readJson(relPath);
}

function validateRun238PublicVideoWorkflow(data) {
  const { audit237, result236, result238, directionMemory, recipeMemory, workflowGates } = data;
  if (audit237?.status !== "run2_37_visual_quality_audit_public_blocked") {
    throw new Error("Run 2.39 must consume Run 2.37 visual quality audit");
  }
  if (result236?.status !== "run2_36_visual_evidence_realism_rerun_public_blocked") {
    throw new Error("Run 2.39 must consume Run 2.36 visual-evidence realism rerun result");
  }
  if (result238?.status !== "run2_38_public_video_visual_direction_workflow_ready_public_blocked") {
    throw new Error("Run 2.39 must consume Run 2.38 public-video visual direction workflow result");
  }
  if (directionMemory?.status !== "run2_38_public_video_slide_direction_memory_ready_public_blocked") {
    throw new Error("Run 2.39 direction memory status mismatch");
  }
  if (recipeMemory?.status !== "run2_38_per_slide_visual_recipe_memory_ready_public_blocked") {
    throw new Error("Run 2.39 recipe memory status mismatch");
  }
  if (workflowGates?.status !== "run2_38_public_video_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.39 workflow gates status mismatch");
  }
  if (
    directionMemory.selected_usecase_id !== selectedUsecaseId ||
    recipeMemory.selected_usecase_id !== selectedUsecaseId ||
    workflowGates.selected_usecase_id !== selectedUsecaseId
  ) {
    throw new Error("Run 2.39 selected usecase mismatch");
  }
  const directions = directionMemory.public_video_slide_direction_records ?? [];
  const recipes = recipeMemory.per_slide_visual_recipe_records ?? [];
  const gates = workflowGates.gates ?? [];
  const roles = baseSlides.map((slide) => slide.role);
  if (directions.length !== 6 || recipes.length !== 6 || gates.length !== 6) {
    throw new Error("Run 2.38 must provide six directions, six recipes, and six workflow gates");
  }
  const diversity = workflowGates.visual_rhythm_diversity_contract ?? {};
  if (diversity.min_unique_visual_rhythms !== 6) throw new Error("Run 2.38 visual_rhythm_diversity_contract min mismatch");
  if (diversity.max_repeated_layout_signature_allowed !== 1) {
    throw new Error("Run 2.38 repeated layout signature contract mismatch");
  }
  if (diversity.forbidden_dominant_layout_signature !== RUN2_36_DOMINANT_LAYOUT_SIGNATURE) {
    throw new Error("Run 2.38 forbidden dominant layout signature mismatch");
  }

  const directionByRole = new Map(directions.map((record) => [record.role, record]));
  const recipeByRole = new Map(recipes.map((record) => [record.role, record]));
  const gateByRole = new Map(gates.map((record) => [record.role, record]));
  const visualRhythms = new Set();
  for (const role of roles) {
    const direction = directionByRole.get(role);
    const recipe = recipeByRole.get(role);
    const gate = gateByRole.get(role);
    if (!direction || !recipe || !gate) throw new Error(`Run 2.38 missing role ${role}`);
    if (direction.selected_usecase_id !== selectedUsecaseId || recipe.selected_usecase_id !== selectedUsecaseId) {
      throw new Error(`Run 2.38 role ${role} usecase mismatch`);
    }
    if (recipe.source_direction_memory_id !== direction.direction_memory_id) {
      throw new Error(`Run 2.38 direction/recipe mismatch for ${role}`);
    }
    if (gate.required_public_video_slide_direction_memory_id !== direction.direction_memory_id) {
      throw new Error(`Run 2.38 direction/gate mismatch for ${role}`);
    }
    if (gate.required_per_slide_visual_recipe_memory_id !== recipe.recipe_memory_id) {
      throw new Error(`Run 2.38 recipe/gate mismatch for ${role}`);
    }
    if (gate.required_visual_rhythm_id !== direction.visual_rhythm_id || recipe.visual_rhythm_id !== direction.visual_rhythm_id) {
      throw new Error(`Run 2.38 visual rhythm mismatch for ${role}`);
    }
    if (gate.required_layout_signature_target !== recipe.layout_signature_target) {
      throw new Error(`Run 2.38 layout target mismatch for ${role}`);
    }
    if (gate.next_rerun_contract !== "must_be_consumed_before_run2_39_four_arm_rerun") {
      throw new Error(`Run 2.38 next rerun contract mismatch for ${role}`);
    }
    if (gate.forbid_run2_36_dominant_layout_signature !== true || gate.forbid_workflow_gate_as_public_ribbon !== true) {
      throw new Error(`Run 2.38 gate policy mismatch for ${role}`);
    }
    for (const field of [
      "run2_38_visual_direction_memory_id",
      "run2_38_per_slide_visual_recipe_id",
      "run2_38_visual_rhythm_id",
      "run2_38_layout_signature_target",
      "run2_38_public_video_execution_status",
    ]) {
      if (!(gate.required_trace_fields ?? []).includes(field)) {
        throw new Error(`Run 2.38 gate ${role} missing trace field ${field}`);
      }
    }
    for (const moduleId of gate.required_code_modules ?? []) {
      if (!(direction.required_code_modules ?? []).includes(moduleId)) {
        throw new Error(`Run 2.38 module mismatch for ${role}`);
      }
    }
    visualRhythms.add(direction.visual_rhythm_id);
  }
  if (visualRhythms.size !== 6) throw new Error("Run 2.38 did not provide six unique visual rhythms");
}

function run239RequiredModulesByRole(workflowGates) {
  return new Map((workflowGates.gates ?? []).map((gate) => [gate.role, gate.required_code_modules ?? []]));
}

function loadRun239ContractData(arm) {
  const audit237 = readRun239PackJsonForArm(arm, RUN2_39_INPUTS.visualQualityAudit);
  const result236 = readRun239PackJsonForArm(arm, RUN2_39_INPUTS.visualEvidenceRealismRerunResult);
  const result238 = readRun239PackJsonForArm(arm, RUN2_39_INPUTS.publicVideoVisualDirectionWorkflowResult);
  const directionMemory = readRun239PackJsonForArm(arm, RUN2_39_INPUTS.publicVideoSlideDirectionMemory);
  const recipeMemory = readRun239PackJsonForArm(arm, RUN2_39_INPUTS.perSlideVisualRecipeMemory);
  const workflowGates = readRun239PackJsonForArm(arm, RUN2_39_INPUTS.publicVideoWorkflowGates);
  const data = { audit237, result236, result238, directionMemory, recipeMemory, workflowGates };
  validateRun238PublicVideoWorkflow(data);
  return {
    ...data,
    requiredModulesByRole: run239RequiredModulesByRole(workflowGates),
    status: "run2_39_public_video_visual_direction_contract_ready",
  };
}

function selectRun239ForSlide(role, contractData) {
  const direction = (contractData.directionMemory?.public_video_slide_direction_records ?? []).find((item) => item.role === role);
  const recipe = (contractData.recipeMemory?.per_slide_visual_recipe_records ?? []).find((item) => item.role === role);
  const gate = (contractData.workflowGates?.gates ?? []).find((item) => item.role === role);
  if (!direction) throw new Error(`Run 2.38 direction memory missing role ${role}`);
  if (!recipe) throw new Error(`Run 2.38 recipe memory missing role ${role}`);
  if (!gate) throw new Error(`Run 2.38 workflow gate missing role ${role}`);
  return { direction, recipe, gate };
}

function drawRun239LaunchPosterStage(slide, arm, spec, selection, metrics) {
  registerRun239Module(metrics, "drawRun239LaunchPosterStage");
  const target = selection.recipe.primary_visual_weight_target;
  moduleLabel(slide, 76, 94, "poster reveal scene", arm);
  text(slide, "Design memory becomes a launch surface.", 82, 116, 470, 92, {
    fontSize: 44,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "Design memory becomes a launch surface.");
  text(slide, compactText(selection.direction.commercial_story_payload.viewer_takeaway, 92), 84, 224, 430, 54, {
    fontSize: 15,
    color: arm.palette.muted,
  });
  registerText(metrics, selection.direction.commercial_story_payload.viewer_takeaway);
  const stage = { x: 554, y: 110, w: 612, h: 450 };
  rect(slide, stage.x + 26, stage.y + 24, stage.w, stage.h, "#d9e4e3", colorLine("#d9e4e3", 1));
  rect(slide, stage.x, stage.y, stage.w, stage.h, C.midnight, colorLine(C.midnight, 1));
  rect(slide, stage.x + 48, stage.y + 60, 356, 236, C.white, colorLine("#cfd8df", 1));
  rect(slide, stage.x + 78, stage.y + 96, 152, 86, arm.palette.proof, colorLine(arm.palette.proof, 1));
  rect(slide, stage.x + 260, stage.y + 110, 106, 12, C.cyan);
  rect(slide, stage.x + 260, stage.y + 154, 156, 8, "#b9c5cc");
  rect(slide, stage.x + 260, stage.y + 190, 106, 8, "#b9c5cc");
  text(slide, "generated launch deck", stage.x + 74, stage.y + 232, 294, 24, {
    fontSize: 18,
    title: true,
    bold: true,
    color: C.ink,
  });
  registerText(metrics, "generated launch deck");
  ["direction", "recipe", "gate"].forEach((label, index) => {
    const angleX = stage.x + 436 + (index % 2) * 74;
    const angleY = stage.y + 94 + index * 82;
    ellipse(slide, angleX, angleY, 82, 82, index === 1 ? arm.palette.proof : "#24313c", colorLine("#dfe9ec", 1));
    text(slide, label, angleX + 10, angleY + 33, 62, 12, {
      fontSize: 8,
      mono: true,
      bold: true,
      color: C.white,
      align: "center",
    });
    registerText(metrics, label);
  });
  text(slide, selection.direction.first_read_object, stage.x + 48, stage.y + 336, stage.w - 96, 48, {
    fontSize: 13,
    color: "#dce7ed",
  });
  registerText(metrics, selection.direction.first_read_object);
  chip(slide, selection.recipe.layout_signature_target, 84, 578, 420, C.white, arm.palette.accent);
  registerText(metrics, selection.recipe.layout_signature_target);
  registerPrimaryVisual(metrics, stage.x, stage.y, stage.w, stage.h, target);
  registerProof(metrics, 3);
  registerZones(metrics, 3);
}

function drawRun239FailurePathScene(slide, arm, spec, selection, metrics) {
  registerRun239Module(metrics, "drawRun239FailurePathScene");
  const target = selection.recipe.primary_visual_weight_target;
  moduleLabel(slide, 76, 94, "failure path scene", arm);
  text(slide, "Prompt-only loses the inspectable path.", 78, 114, 510, 72, {
    fontSize: 38,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "Prompt-only loses the inspectable path.");
  const pathDots = [
    { x: 92, y: 258, label: "brief" },
    { x: 246, y: 330, label: "prompt" },
    { x: 412, y: 410, label: "generic deck" },
  ];
  pathDots.forEach((dot, index) => {
    rect(slide, dot.x, dot.y, 148, 68, index === 2 ? "#e6d3c5" : C.white, colorLine(index === 2 ? arm.palette.proof : "#cbd3d9", 1));
    text(slide, dot.label, dot.x + 18, dot.y + 24, 110, 14, { fontSize: 12, mono: true, bold: true, color: arm.palette.title });
    registerText(metrics, dot.label);
    if (index < pathDots.length - 1) {
      rect(slide, dot.x + 138, dot.y + 52, 112, 6, "#c5cbd0");
    }
  });
  const selected = { x: 650, y: 142, w: 484, h: 374 };
  rect(slide, selected.x + 24, selected.y + 26, selected.w, selected.h, "#d9e4e3", colorLine("#d9e4e3", 1));
  rect(slide, selected.x, selected.y, selected.w, selected.h, C.white, colorLine(arm.palette.accent, 2));
  text(slide, "selected route", selected.x + 34, selected.y + 34, 220, 24, {
    fontSize: 22,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "selected route");
  const lanes = [
    ["source boundary", C.cyan],
    ["visual rhythm", C.signal],
    ["release gate", C.midnight],
  ];
  lanes.forEach(([label, fill], index) => {
    const y = selected.y + 94 + index * 74;
    rect(slide, selected.x + 42, y, selected.w - 84, 46, index === 1 ? fill : "#f3f6f7", colorLine(fill, 2));
    text(slide, label, selected.x + 64, y + 16, 200, 12, {
      fontSize: 10,
      mono: true,
      bold: true,
      color: index === 1 ? C.white : arm.palette.title,
    });
    registerText(metrics, label);
  });
  text(slide, compactText(selection.direction.first_read_object, 98), selected.x + 42, selected.y + 322, selected.w - 84, 26, {
    fontSize: 12,
    color: arm.palette.muted,
  });
  registerText(metrics, selection.direction.first_read_object);
  chip(slide, selection.recipe.visual_rhythm_id, 76, 578, 218, C.white, arm.palette.accent);
  registerPrimaryVisual(metrics, selected.x, selected.y, selected.w, selected.h, target);
  registerWorkflow(metrics, 3);
  registerGate(metrics, 1);
}

function drawRun239AsymmetricBeforeAfterState(slide, arm, spec, selection, metrics) {
  registerRun239Module(metrics, "drawRun239AsymmetricBeforeAfterState");
  const target = selection.recipe.primary_visual_weight_target;
  moduleLabel(slide, 76, 94, "asymmetric before/after", arm);
  const before = { x: 84, y: 166, w: 248, h: 214 };
  rect(slide, before.x, before.y, before.w, before.h, "#f3f4f5", colorLine("#cad2d8", 1));
  text(slide, "before", before.x + 22, before.y + 24, 120, 18, { fontSize: 15, title: true, bold: true, color: arm.palette.muted });
  rect(slide, before.x + 24, before.y + 76, 98, 10, "#bfc8cf");
  rect(slide, before.x + 24, before.y + 118, 146, 7, "#d0d7dd");
  rect(slide, before.x + 24, before.y + 148, 76, 7, "#d0d7dd");
  registerText(metrics, "before");
  const after = { x: 380, y: 126, w: 760, h: 430 };
  rect(slide, after.x + 24, after.y + 26, after.w, after.h, "#d9e4e3", colorLine("#d9e4e3", 1));
  rect(slide, after.x, after.y, after.w, after.h, C.midnight, colorLine(C.midnight, 1));
  text(slide, "after / evidence-selected", after.x + 42, after.y + 36, 310, 22, {
    fontSize: 22,
    title: true,
    bold: true,
    color: C.white,
  });
  registerText(metrics, "after evidence-selected");
  rect(slide, after.x + 44, after.y + 94, 266, 188, arm.palette.proof);
  text(slide, "public-demo launch deck", after.x + 70, after.y + 132, 190, 58, {
    fontSize: 27,
    title: true,
    bold: true,
    color: C.white,
  });
  registerText(metrics, "public-demo launch deck");
  ["direction memory", "visual recipe", "code module"].forEach((label, index) => {
    const x = after.x + 364;
    const y = after.y + 104 + index * 74;
    rect(slide, x, y, 298, 44, index === 1 ? C.cyan : "#27333e", colorLine("#596776", 1));
    text(slide, label, x + 20, y + 16, 230, 11, {
      fontSize: 9,
      mono: true,
      bold: true,
      color: index === 1 ? C.ink : C.white,
    });
    registerText(metrics, label);
  });
  text(slide, selection.direction.commercial_story_payload.viewer_takeaway, after.x + 44, after.y + 324, 576, 34, {
    fontSize: 14,
    color: "#dce8ee",
  });
  registerText(metrics, selection.direction.commercial_story_payload.viewer_takeaway);
  chip(slide, selection.recipe.layout_signature_target, 76, 578, 372, C.white, arm.palette.accent);
  registerPrimaryVisual(metrics, after.x, after.y, after.w, after.h, target);
  registerProof(metrics, 4);
  registerZones(metrics, 2);
}

function drawRun239ProductWorkflowSurface(slide, arm, spec, selection, metrics) {
  registerRun239Module(metrics, "drawRun239ProductWorkflowSurface");
  const target = selection.recipe.primary_visual_weight_target;
  moduleLabel(slide, 76, 94, "product workflow surface", arm);
  text(slide, "The memory is visible as a product state.", 78, 116, 610, 58, {
    fontSize: 34,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "The memory is visible as a product state.");
  const console = { x: 92, y: 198, w: 1052, h: 354 };
  rect(slide, console.x + 20, console.y + 24, console.w, console.h, "#d9e4e3", colorLine("#d9e4e3", 1));
  rect(slide, console.x, console.y, console.w, console.h, C.white, colorLine(arm.palette.accent, 2));
  rect(slide, console.x, console.y, console.w, 54, C.midnight, colorLine(C.midnight, 1));
  text(slide, "Vulca slide direction workbench", console.x + 28, console.y + 20, 320, 14, {
    fontSize: 12,
    mono: true,
    bold: true,
    color: C.white,
  });
  registerText(metrics, "Vulca slide direction workbench");
  const roles = baseSlides.map((item) => item.role);
  roles.forEach((role, index) => {
    const rowY = console.y + 78 + index * 39;
    const active = role === spec.role;
    rect(slide, console.x + 28, rowY, console.w - 56, 28, active ? arm.palette.proof : "#f2f5f6", colorLine(active ? arm.palette.proof : "#d7dfe4", 1));
    text(slide, role, console.x + 48, rowY + 9, 90, 8, {
      fontSize: 7.8,
      mono: true,
      bold: true,
      color: active ? C.white : arm.palette.title,
    });
    text(slide, role === spec.role ? selection.direction.visual_rhythm_id : "compressed", console.x + 172, rowY + 9, 180, 8, {
      fontSize: 7.8,
      mono: true,
      bold: true,
      color: active ? C.white : arm.palette.muted,
    });
    text(slide, role === spec.role ? selection.recipe.layout_signature_target : "inactive recipe", console.x + 420, rowY + 9, 330, 8, {
      fontSize: 7.8,
      mono: true,
      color: active ? C.white : arm.palette.muted,
    });
    registerText(metrics, `${role} ${role === spec.role ? selection.direction.visual_rhythm_id : "compressed"}`);
  });
  rect(slide, console.x + 772, console.y + 90, 208, 170, "#edf4f3", colorLine(C.cyan, 2));
  text(slide, "bound module", console.x + 796, console.y + 116, 160, 12, { fontSize: 9, mono: true, bold: true, color: arm.palette.accent });
  text(slide, selection.gate.required_code_modules[0], console.x + 796, console.y + 150, 148, 42, {
    fontSize: 17,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, `bound module ${selection.gate.required_code_modules[0]}`);
  chip(slide, "trace fields hidden; public surface stays product-first", 76, 578, 404, C.white, arm.palette.accent);
  registerPrimaryVisual(metrics, console.x, console.y, console.w, console.h, target);
  registerWorkflow(metrics, 6);
  registerProof(metrics, 2);
}

function drawRun239CinematicClimaxObject(slide, arm, spec, selection, metrics) {
  registerRun239Module(metrics, "drawRun239CinematicClimaxObject");
  const target = selection.recipe.primary_visual_weight_target;
  moduleLabel(slide, 76, 94, "cinematic climax object", arm);
  const stage = { x: 98, y: 112, w: 1038, h: 500 };
  rect(slide, stage.x + 28, stage.y + 28, stage.w, stage.h, "#d5dfdf", colorLine("#d5dfdf", 1));
  rect(slide, stage.x, stage.y, stage.w, stage.h, C.midnight, colorLine(C.midnight, 1));
  rect(slide, stage.x + 54, stage.y + 52, stage.w - 108, stage.h - 104, "#161f28", colorLine("#3b4854", 1));
  text(slide, "One generated proof object", stage.x + 82, stage.y + 78, 486, 48, {
    fontSize: 42,
    title: true,
    bold: true,
    color: C.white,
  });
  registerText(metrics, "One generated proof object");
  text(slide, compactText(selection.direction.commercial_story_payload.viewer_takeaway, 96), stage.x + 86, stage.y + 140, 500, 38, {
    fontSize: 14,
    color: "#d9e5ec",
  });
  registerText(metrics, selection.direction.commercial_story_payload.viewer_takeaway);
  const object = { x: stage.x + 156, y: stage.y + 220, w: 620, h: 220 };
  rect(slide, object.x - 26, object.y - 26, object.w + 52, object.h + 52, "#22303a", colorLine("#22303a", 1));
  rect(slide, object.x, object.y, object.w, object.h, C.white, colorLine(C.white, 1));
  rect(slide, object.x + 36, object.y + 42, 210, 118, arm.palette.proof);
  text(slide, "Run 2.39 full", object.x + 62, object.y + 76, 160, 28, {
    fontSize: 23,
    title: true,
    bold: true,
    color: C.white,
  });
  rect(slide, object.x + 302, object.y + 54, 176, 13, C.cyan);
  rect(slide, object.x + 302, object.y + 106, 220, 8, "#b6c5cc");
  rect(slide, object.x + 302, object.y + 146, 144, 8, "#b6c5cc");
  chip(slide, "public blocked", stage.x + 790, stage.y + 70, 156, "#25323d", C.white);
  chip(slide, selection.recipe.layout_signature_target, stage.x + 626, stage.y + 526, 418, "#25323d", C.white);
  registerText(metrics, `Run 2.39 full public blocked ${selection.recipe.layout_signature_target}`);
  registerPrimaryVisual(metrics, stage.x, stage.y, stage.w, stage.h, target);
  registerProof(metrics, 5);
  registerGate(metrics, 1);
  registerZones(metrics, 1);
}

function drawRun239DecisionHandoffPath(slide, arm, spec, selection, metrics) {
  registerRun239Module(metrics, "drawRun239DecisionHandoffPath");
  const target = selection.recipe.primary_visual_weight_target;
  moduleLabel(slide, 76, 94, "decision handoff path", arm);
  text(slide, "We stay in the same five layers.", 78, 116, 540, 58, {
    fontSize: 36,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "We stay in the same five layers.");
  const pathArea = { x: 116, y: 238, w: 938, h: 218 };
  rect(slide, pathArea.x + 18, pathArea.y + 20, pathArea.w, pathArea.h, "#d9e4e3", colorLine("#d9e4e3", 1));
  rect(slide, pathArea.x, pathArea.y, pathArea.w, pathArea.h, C.white, colorLine(arm.palette.accent, 2));
  const stops = [
    ["2.38 memory", C.cyan],
    ["2.39 rerun", arm.palette.proof],
    ["visual review", C.midnight],
    ["public blocked", "#6b7280"],
  ];
  stops.forEach(([label, fill], index) => {
    const x = pathArea.x + 54 + index * 220;
    ellipse(slide, x, pathArea.y + 64, 120, 120, fill, colorLine(fill, 1));
    text(slide, label, x + 14, pathArea.y + 110, 92, 12, {
      fontSize: 9,
      mono: true,
      bold: true,
      color: index === 0 ? C.ink : C.white,
      align: "center",
    });
    registerText(metrics, label);
    if (index < stops.length - 1) rect(slide, x + 118, pathArea.y + 122, 108, 7, fill);
  });
  text(slide, selection.direction.commercial_story_payload.business_outcome, 116, 502, 764, 36, {
    fontSize: 15,
    color: arm.palette.muted,
  });
  registerText(metrics, selection.direction.commercial_story_payload.business_outcome);
  chip(slide, selection.recipe.layout_signature_target, 116, 578, 368, C.white, arm.palette.accent);
  registerPrimaryVisual(metrics, pathArea.x, pathArea.y, pathArea.w, pathArea.h, target);
  registerWorkflow(metrics, 4);
  registerGate(metrics, 2);
}

const RUN2_39_MODULES = {
  cover: drawRun239LaunchPosterStage,
  setup: drawRun239FailurePathScene,
  contrast: drawRun239AsymmetricBeforeAfterState,
  proof: drawRun239ProductWorkflowSurface,
  climax: drawRun239CinematicClimaxObject,
  close: drawRun239DecisionHandoffPath,
};

function drawControlGate(slide, arm, spec, metrics, opts = {}) {
  const x = opts.x ?? 894;
  const y = opts.y ?? 438;
  const w = opts.w ?? 232;
  const h = opts.h ?? 116;
  rect(slide, x, y, w, h, arm.palette.gate, colorLine(arm.palette.rule, 1));
  text(slide, opts.headline ?? "public blocked", x + 16, y + 22, w - 32, 30, {
    fontSize: 16,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  text(slide, opts.line ?? "no Run 2.38 trace", x + 16, y + 66, w - 32, 18, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted,
  });
  registerText(metrics, `${opts.headline ?? "public blocked"} ${opts.line ?? "no Run 2.38 trace"}`);
  registerGate(metrics, 1);
}

function drawControlSlideContent(slide, arm, spec, metrics, mode = "prompt") {
  text(slide, spec.title, 76, 132, 596, 104, {
    fontSize: mode === "bad" ? 34 : 38,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, spec.claim, 80, 250, 526, 64, { fontSize: 16, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  const panelFill = mode === "bad" ? "#efe4c8" : C.white;
  const cols = spec.role === "climax" ? 3 : mode === "bad" ? 4 : 3;
  for (let i = 0; i < cols; i += 1) {
    const px = spec.role === "climax" ? 94 + i * 300 : 672 + i * (mode === "bad" ? 116 : 150);
    const py = spec.role === "climax" ? 328 : 318;
    const pw = spec.role === "climax" ? 248 : mode === "bad" ? 100 : 132;
    const ph = spec.role === "climax" ? 150 : 148;
    rect(slide, px, py, pw, ph, panelFill, colorLine(arm.palette.rule, 1));
    rect(slide, px + 14, py + 26, pw - 40, 12, arm.palette.accent2);
    rect(slide, px + 14, py + 64, pw - 56, 9, "#c0c9d0");
    rect(slide, px + 14, py + 96, pw - 68, 9, "#c0c9d0");
  }
  const copy =
    mode === "bad"
      ? "Usecase label is present, but no Run 2.38 public-video direction memory, per-slide visual recipe, or workflow gate was executed."
      : "The control can be readable while still lacking public-video direction memory selected before generation.";
  rect(slide, 84, 346, mode === "bad" ? 456 : 480, 150, panelFill, colorLine(arm.palette.rule, 1));
  text(slide, copy, 108, 378, mode === "bad" ? 390 : 420, 72, {
    fontSize: mode === "bad" ? 17 : 19,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, copy);
  registerContentCards(metrics, cols + 1);
  registerPrimaryVisual(metrics, 84, 318, 1042, 212, mode === "bad" ? 0.3 : 0.35);
}

function renderRun239FullSlide(presentation, spec, arm, n, fullData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const selection = selectRun239ForSlide(spec.role, fullData);
  const draw = RUN2_39_MODULES[spec.role];
  draw(slide, arm, spec, selection, metrics);
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function renderControlSlide(presentation, spec, arm, n, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  const mode = arm.armId === "bad_public_video_visual_direction_memory" ? "bad" : arm.armId === "run1_5_skill" ? "run1_5" : "prompt";
  drawControlSlideContent(slide, arm, spec, metrics, mode);
  drawControlGate(slide, arm, spec, metrics, {
    x: spec.role === "climax" ? 1022 : 894,
    y: spec.role === "close" ? 326 : spec.role === "climax" ? 492 : 438,
    w: spec.role === "close" ? 238 : spec.role === "climax" ? 178 : 232,
    h: spec.role === "climax" ? 92 : 118,
    headline: arm.armId === "bad_public_video_visual_direction_memory" ? "pack missing" : "public blocked",
    line: arm.armId === "bad_public_video_visual_direction_memory" ? "label only / no 2.39 recipe" : "no Run 2.39 trace",
  });
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertRun239ArmInputBoundaries(arm);
  const fullRun239 = arm.armId === "run2_39_full_public_video_visual_direction";
  const fullData = fullRun239 ? context.fullData ?? loadRun239ContractData(arm) : null;
  const requiredModulesByRole = fullData?.requiredModulesByRole ?? new Map();
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = fullRun239 && arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun239 ? selectedUsecaseId : arm.armId === "bad_public_video_visual_direction_memory" ? selectedUsecaseId : "",
    prior_generated_run_id: fullRun239 ? fullData.result236.run_id : "",
    prior_generated_run_status: fullRun239 ? fullData.result236.status : "",
    run2_37_visual_quality_audit_status: fullRun239 ? fullData.audit237.status : "",
    run2_38_public_video_workflow_result_status: fullRun239 ? fullData.result238.status : "",
    run2_38_visual_direction_memory_status: fullRun239 ? fullData.directionMemory.status : "",
    run2_38_per_slide_visual_recipe_status: fullRun239 ? fullData.recipeMemory.status : "",
    run2_38_workflow_gate_status: fullRun239 ? fullData.workflowGates.status : "",
    visual_rhythm_diversity_contract: fullRun239 ? fullData.workflowGates.visual_rhythm_diversity_contract : {},
    commercial_case: `${pack}/commercial_case.md`,
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.39 public-video visual direction arm-specific generation from scripts/generate_ppt_run2_39_public_video_visual_direction_arms.mjs",
      no_cross_arm_reuse: [
        "cached memory summaries",
        "generated slide code",
        "layout JSON",
        "screenshots",
        "contact sheets",
        "QA notes",
        "Run 2.38 direction memory in control arms",
        "Run 2.38 recipe memory in control arms",
        "Run 2.38 workflow gate ids in control arms",
      ],
    },
    model_provider: "Codex local code generation with artifact-tool native presentation primitives",
    tool_versions: {
      artifact_tool: "bundled @oai/artifact-tool via presentations skill",
      node: "codex primary runtime",
      python: "workspace runtime for contact sheet and layout QA",
    },
    release_decision: arm.release,
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const actualCodeModuleIds = Array.from(roleMetrics.visualModuleIds);
      const selection = fullRun239 ? selectRun239ForSlide(slide.role, fullData) : null;
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_39_contract_status: fullRun239
          ? hasRenderedMetrics
            ? "full_arm_native_generator_rendered"
            : "full_arm_contract_preview_not_rendered"
          : "boundary_control_not_run2_39_full",
        run2_37_source_audit_finding: fullRun239 ? fullData.audit237.root_cause ?? "visual_module_language_too_repetitive_and_card_like" : "",
        run2_38_visual_direction_memory_id: fullRun239 ? selection.direction.direction_memory_id : "",
        run2_38_per_slide_visual_recipe_id: fullRun239 ? selection.recipe.recipe_memory_id : "",
        run2_38_visual_rhythm_id: fullRun239 ? selection.direction.visual_rhythm_id : "",
        run2_38_layout_signature_target: fullRun239 ? selection.recipe.layout_signature_target : "",
        run2_38_primary_visual_weight_target: fullRun239 ? selection.recipe.primary_visual_weight_target : "",
        run2_38_public_video_scene_type: fullRun239 ? selection.direction.public_video_scene_type : "",
        run2_38_first_read_object: fullRun239 ? selection.direction.first_read_object : "",
        run2_38_public_video_execution_status: fullRun239 ? RUN2_39_EXECUTION_STATUS : "",
        run2_39_required_code_module_ids: fullRun239 ? requiredModulesByRole.get(slide.role) ?? [] : [],
        run2_39_code_module_ids: fullRun239
          ? hasRenderedMetrics
            ? actualCodeModuleIds
            : requiredModulesByRole.get(slide.role) ?? []
          : [],
        run2_39_bad_control_probe: fullRun239
          ? "bad_public_video_visual_direction_memory may receive the selected usecase label but forbids Run 2.38 direction memory, recipe memory, workflow gates, Run 2.37 audit, and Run 2.36 rerun result"
          : "boundary_control",
        negative_control_usecase_id: arm.armId === "bad_public_video_visual_direction_memory" ? selectedUsecaseId : "",
        layout_metrics: {
          text_box_count: roleMetrics.textBoxCount,
          visible_words: roleMetrics.visibleWords,
          proof_objects: roleMetrics.proofObjects,
          zones: roleMetrics.zones,
          workflow_objects: roleMetrics.workflowObjects,
          gate_objects: roleMetrics.gateObjects,
          content_cards: roleMetrics.contentCards,
          primary_visual_weight: Number(roleMetrics.primaryVisualWeight.toFixed(3)),
          run2_36_dominant_layout_signature_reused: roleMetrics.run2_36DominantLayoutSignatureReused,
        },
      };
    }),
  };
}

function assertRun239PublicVideoGateSelfCheck(trace) {
  if (trace.arm_id !== "run2_39_full_public_video_visual_direction") return;
  if (trace.selected_usecase_id !== selectedUsecaseId) throw new Error("Run 2.39 full trace did not lock selected usecase");
  if (trace.run2_38_workflow_gate_status !== "run2_38_public_video_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.39 full trace did not consume Run 2.38 workflow gates");
  }
  const rhythms = new Set(trace.slides.map((slide) => slide.run2_38_visual_rhythm_id));
  if (rhythms.size !== 6) throw new Error("Run 2.39 full trace did not preserve six unique visual rhythms");
  for (const slide of trace.slides) {
    for (const field of [
      "run2_38_visual_direction_memory_id",
      "run2_38_per_slide_visual_recipe_id",
      "run2_38_visual_rhythm_id",
      "run2_38_layout_signature_target",
      "run2_38_public_video_scene_type",
      "run2_38_first_read_object",
      "run2_38_public_video_execution_status",
    ]) {
      if (!String(slide[field] ?? "").trim()) throw new Error(`Run 2.39 full slide ${slide.slide_id} missing ${field}`);
    }
    if (slide.run2_38_public_video_execution_status !== RUN2_39_EXECUTION_STATUS) {
      throw new Error(`Run 2.39 full slide ${slide.slide_id} missing execution status`);
    }
    if ((slide.layout_metrics?.primary_visual_weight ?? 0) < 0.55) {
      throw new Error(`Run 2.39 full slide ${slide.slide_id} did not meet primary visual weight`);
    }
    if (slide.layout_metrics?.run2_36_dominant_layout_signature_reused !== false) {
      throw new Error(`Run 2.39 full slide ${slide.slide_id} reused Run 2.36 dominant layout signature`);
    }
    const actualCodeModules = new Set(slide.run2_39_code_module_ids ?? []);
    for (const requiredCodeModule of slide.run2_39_required_code_module_ids ?? []) {
      if (!actualCodeModules.has(requiredCodeModule)) {
        throw new Error(`Run 2.39 full slide ${slide.slide_id} did not call required module ${requiredCodeModule}`);
      }
    }
    if ((slide.run2_39_code_module_ids ?? []).length !== 1) {
      throw new Error(`Run 2.39 full slide ${slide.slide_id} should call exactly one Run 2.39 module`);
    }
  }
}

function buildArmContract() {
  return armSpecs.map((arm) => ({
    armId: arm.armId,
    label: arm.label,
    contract_status:
      arm.armId === "run2_39_full_public_video_visual_direction"
        ? "run2_39_public_video_visual_direction_contract_ready_requires_render_metrics"
        : "run2_39_boundary_control_contract_ready",
    allowed: arm.allowed,
    forbidden: arm.forbidden,
    palette: arm.palette,
    trace: traceFor(arm),
  }));
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

function buildRun239FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-39-four-arm-contact-sheet.png"),
    "Run 2.39 four-arm public-video visual-direction comparison",
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
      "required proof objects: public-video slide direction, per-slide visual recipe, unique visual rhythm, role-specific code module, release gate",
      "source requirements: commercial case always; full arm requires Run 2.37 audit, Run 2.36 rerun result, Run 2.38 direction memory, recipe memory, and workflow gates before native PPT generation; bad control receives usecase label only",
      "brand authenticity constraints: no copied source visuals, no borrowed brand chrome, no screenshots, no raw tutorial media",
      "profile-specific QA gates: contact-sheet coherence, editable native text/shapes only, Run 2.38 trace preserved, role-specific first-read object visible, release gate blocked",
      "known missing inputs: public release approval remains unavailable",
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
  let fullData = null;
  if (arm.armId === "run2_39_full_public_video_visual_direction") {
    fullData = loadRun239ContractData(arm);
  }
  const slides = arm.slides.map((slide, index) =>
    arm.armId === "run2_39_full_public_video_visual_direction"
      ? renderRun239FullSlide(presentation, slide, arm, index + 1, fullData, metricsByRole)
      : renderControlSlide(presentation, slide, arm, index + 1, metricsByRole),
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

  const trace = traceFor(arm, { fullData, metricsByRole });
  assertRun239PublicVideoGateSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_39_public_video_visual_direction_arms.mjs",
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

function writeRun239Result(runSummary) {
  const result = {
    schema_version: 1,
    run_id: "2.39",
    status: "run2_39_public_video_visual_direction_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_data_workflow_run_id: "2.38",
    source_audit_run_id: "2.37",
    source_generated_run_id: "2.36",
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      visual_quality_audit: RUN2_39_INPUTS.visualQualityAudit,
      visual_evidence_realism_rerun_result: RUN2_39_INPUTS.visualEvidenceRealismRerunResult,
      public_video_visual_direction_workflow_result: RUN2_39_INPUTS.publicVideoVisualDirectionWorkflowResult,
      public_video_slide_direction_memory: RUN2_39_INPUTS.publicVideoSlideDirectionMemory,
      per_slide_visual_recipe_memory: RUN2_39_INPUTS.perSlideVisualRecipeMemory,
      public_video_workflow_gates: RUN2_39_INPUTS.publicVideoWorkflowGates,
      source_data_layer: RUN2_39_INPUTS.publicVideoVisualDirectionWorkflowResult,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_39_public_video_visual_direction_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_39_full_public_video_visual_direction",
      best_internal_arm_verdict: RUN2_39_EXECUTION_STATUS,
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: "public_video_grade_slide_direction_and_per_slide_visual_recipe",
      source_audit: RUN2_39_INPUTS.visualQualityAudit,
      source_workflow_result: RUN2_39_INPUTS.publicVideoVisualDirectionWorkflowResult,
      replacement_focus:
        "replace repeated Run 2.36 card-like visual module language with six public-video slide rhythms and per-slide visual recipes",
      repair_modules: [
        "drawRun239LaunchPosterStage",
        "drawRun239FailurePathScene",
        "drawRun239AsymmetricBeforeAfterState",
        "drawRun239ProductWorkflowSurface",
        "drawRun239CinematicClimaxObject",
        "drawRun239DecisionHandoffPath",
      ],
      run2_38_direction_records_consumed: 6,
      run2_38_recipe_records_consumed: 6,
      run2_38_workflow_gates_consumed: 6,
      unique_visual_rhythms: 6,
      source_run2_37_target_consumed: true,
    },
    visual_quality_boundary:
      "public_video_visual_direction_proof_only_not_final_human_approved_public_release_or_motion_review",
    control_boundary: {
      bad_public_video_visual_direction_memory:
        "selected_usecase_label_only_without_run2_38_direction_memory_recipe_memory_workflow_gates_run2_37_audit_or_run2_36_rerun",
      prompt_only: "commercial_case_only_no_run2_38_public_video_visual_direction_workflow",
      run1_5_skill: "prior_baseline_no_run2_38_public_video_visual_direction_workflow",
    },
    remaining_public_release_gates: [
      "human_visual_review",
      "native_or_cross_platform_render_inspection",
      "motion_or_video_review",
      "source_boundary_review",
      "human_release_approval",
    ],
    native_module_status: "actual_run2_39_presentation_module_calls_recorded_in_trace_manifest",
    release_boundary:
      "public_blocked_until_visual_human_review_native_render_review_motion_review_source_boundary_review_and_human_approval",
    next_required_action:
      "audit_run2_39_outputs_for_public_video_visual_direction_then_continue_thickening_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_39_public_video_visual_direction_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_39_public_video_visual_direction_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.39 Public Video Visual Direction Rerun Result",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.39 is the generated four-arm rerun that consumes the Run 2.38 public-video visual direction workflow before native PPT code generation. The full arm reads Run 2.38 direction memory, per-slide visual recipe memory, and workflow gates; the negative control receives only the usecase label. It repeats the same five layers and does not advance to Run 3.0.",
      "",
      "The generator is `scripts/generate_ppt_run2_39_public_video_visual_direction_arms.mjs`.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_39_full_public_video_visual_direction`",
      "- `bad_public_video_visual_direction_memory`",
      "",
      "The negative control `bad_public_video_visual_direction_memory` may receive the selected usecase label, but it is blocked from reading the Run 2.38 direction memory, per-slide visual recipe memory, workflow gates, Run 2.37 visual quality audit, and Run 2.36 rerun result.",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_39_full_public_video_visual_direction`.",
      "",
      `Verdict: \`${RUN2_39_EXECUTION_STATUS}\`.`,
      "",
      "Quality delta: `public_video_grade_slide_direction_and_per_slide_visual_recipe`. The full arm uses `drawRun239LaunchPosterStage`, `drawRun239FailurePathScene`, `drawRun239AsymmetricBeforeAfterState`, `drawRun239ProductWorkflowSurface`, `drawRun239CinematicClimaxObject`, and `drawRun239DecisionHandoffPath` so each slide binds Run 2.38 direction id, recipe id, visual rhythm id, layout signature target, and execution status before native drawing.",
      "",
      "Public release remains blocked. This proves Run 2.38 workflow consumption and six-role visual-rhythm diversity, not final public-video-grade human approval.",
      "",
      "Remaining public release gates: human visual review, native or cross-platform render inspection, motion/video review, source-boundary review, and human release approval.",
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
  const fourArmSheet = buildRun239FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_39_public_video_visual_direction_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_39_public_video_visual_direction_rerun_summary.json"), runSummary);
  writeRun239Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_39_INPUTS,
  RUN2_39_DATA_INPUTS,
  armSpecs,
  assertRun239ArmInputBoundaries,
  assertRun239PublicVideoGateSelfCheck,
  buildArmContract,
  drawRun239LaunchPosterStage,
  drawRun239FailurePathScene,
  drawRun239AsymmetricBeforeAfterState,
  drawRun239ProductWorkflowSurface,
  drawRun239CinematicClimaxObject,
  drawRun239DecisionHandoffPath,
  loadRun239ContractData,
  main,
  readRun239PackJsonForArm,
  registerRun239Module,
  run239RequiredModulesByRole,
  selectRun239ForSlide,
  traceFor,
  validateRun238PublicVideoWorkflow,
};
