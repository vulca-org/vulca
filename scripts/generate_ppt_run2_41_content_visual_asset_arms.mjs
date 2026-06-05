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
const RUN2_41_POLICY = "public_surface_machinery_hidden_visual_asset_surface_from_existing_sources_not_copied_media";
const RUN2_41_VERDICT = "content_visual_asset_compiler_thickens_public_surface_without_database_or_workflow_expansion";
const RUN2_41_DATA_STATUS = "same_database_no_workflow_expansion_content_visual_asset_compiler";

const C = {
  ink: "#111318",
  paper: "#f8f4eb",
  white: "#ffffff",
  line: "#d5d0c4",
  muted: "#65707c",
  midnight: "#11161d",
  blue: "#245fdd",
  cyan: "#6cc5d8",
  signal: "#e85237",
  green: "#0f8a66",
  haze: "#eef2f5",
  warm: "#f2d56b",
};

const RUN2_41_INPUTS = {
  run240RerunResult: `${pack}/results/run2_40_visual_compiler_rerun_result.json`,
  run239RerunResult: `${pack}/results/run2_39_public_video_visual_direction_rerun_result.json`,
  publicVideoSlideDirectionMemory: `${pack}/run2_38_public_video_slide_direction_memory.json`,
  perSlideVisualRecipeMemory: `${pack}/run2_38_per_slide_visual_recipe_memory.json`,
  publicVideoWorkflowGates: `${pack}/run2_38_public_video_workflow_gates.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};
const RUN2_41_DATA_INPUTS = Object.values(RUN2_41_INPUTS);

const baseSlides = [
  {
    role: "cover",
    title: "A launch deck should feel like a market scene.",
    claim: "The same database should become public-facing business context, visual surfaces, and one memorable product moment.",
  },
  {
    role: "setup",
    title: "The failure is thin context, not missing workflow.",
    claim: "The weak deck hides the real buyer, launch deadline, decision risk, and visual benchmark behind generic blocks.",
  },
  {
    role: "contrast",
    title: "Same data, thicker surface.",
    claim: "Holding Run 2.38, Run 2.39, and Run 2.40 constant isolates whether content and visual assets are being compiled.",
  },
  {
    role: "proof",
    title: "The proof should look like product evidence.",
    claim: "The slide needs UI state, launch asset, review state, and commercial payload, not a list of system parts.",
  },
  {
    role: "climax",
    title: "The climax is an output moment.",
    claim: "The public high point is a cinematic generated deck in a real launch scene, surrounded by business proof.",
  },
  {
    role: "close",
    title: "The review room judges launch usefulness.",
    claim: "Public release stays blocked, but the next decision should inspect usefulness, visuals, and delivery readiness.",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-41-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.41 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_41_DATA_INPUTS, "contentVisualAssetCompilerTransform", `${pack}/skill_workflow.json`],
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
        "Make the deck look premium.",
        "Explain why data-heavy slides feel bad.",
        "Show a better version.",
        "Show product proof.",
        "Make the result impressive.",
        "End with next steps.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-41-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.41 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_41_DATA_INPUTS, "contentVisualAssetCompilerTransform", `${pack}/skill_workflow.json`],
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
        "The comparison is readable.",
        "The proof reads as a workflow note.",
        "The climax lacks editorial force.",
        "The close is correct but small.",
      ][index],
    })),
  },
  {
    armId: "run2_41_full_content_visual_asset_compiler",
    slug: "ppt-run2-41-full-vulca",
    label: "Run 2.41 full content/visual asset compiler",
    kicker: "RUN 2.41 / CONTENT VISUAL ASSET",
    footer: "run2_41_full_content_visual_asset_compiler | same database | no workflow expansion | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      RUN2_41_INPUTS.run240RerunResult,
      RUN2_41_INPUTS.run239RerunResult,
      RUN2_41_INPUTS.publicVideoSlideDirectionMemory,
      RUN2_41_INPUTS.perSlideVisualRecipeMemory,
      RUN2_41_INPUTS.publicVideoWorkflowGates,
      RUN2_41_INPUTS.commercialUsecaseBank,
      RUN2_41_INPUTS.sources,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_40_visual_compiler_rerun_result.json",
      "run2_39_public_video_visual_direction_rerun_result.json",
      "run2_38_public_video_slide_direction_memory.json",
      "run2_38_per_slide_visual_recipe_memory.json",
      "run2_38_public_video_workflow_gates.json",
      "commercial_usecase_bank.json",
      "sources.json",
      RUN2_41_DATA_STATUS,
    ],
    forbidden: [
      "new database records",
      "visible trace panel",
      "visible workflow gate ribbon",
      "visible memory id field",
      "visible module id field",
      "engineering report surface",
    ],
    content_visual_asset_compiler_policy: RUN2_41_POLICY,
    palette: {
      bg: "#f8f4eb",
      rail: "#11161d",
      accent: "#11161d",
      accent2: "#245fdd",
      proof: "#e85237",
      panel: C.white,
      title: "#0e1218",
      muted: "#58636f",
      rule: "#d8cfbf",
      gate: "#11161d",
      surface: "#eef3f2",
    },
    slides: baseSlides,
  },
  {
    armId: "bad_thin_content_visual_asset_compiler",
    slug: "ppt-run2-41-bad-thin-content-visual-asset-compiler",
    label: "Bad thin content visual asset compiler",
    kicker: "RUN 2.41 / THIN SAME-DATA CONTROL",
    footer: "bad_thin_content_visual_asset_compiler | machinery hidden but content/assets thin | internal comparison",
    release: "internal_only",
    allowed: [
      `${pack}/commercial_case.md`,
      RUN2_41_INPUTS.run240RerunResult,
      RUN2_41_INPUTS.run239RerunResult,
      RUN2_41_INPUTS.publicVideoSlideDirectionMemory,
      RUN2_41_INPUTS.perSlideVisualRecipeMemory,
      RUN2_41_INPUTS.publicVideoWorkflowGates,
      RUN2_41_INPUTS.commercialUsecaseBank,
      RUN2_41_INPUTS.sources,
    ],
    data_input_manifest: [
      "run2_40_visual_compiler_rerun_result.json",
      "run2_39_public_video_visual_direction_rerun_result.json",
      "run2_38_public_video_slide_direction_memory.json",
      "run2_38_per_slide_visual_recipe_memory.json",
      "run2_38_public_video_workflow_gates.json",
      "commercial_usecase_bank.json",
      "sources.json",
      RUN2_41_DATA_STATUS,
    ],
    forbidden: ["new database records", "new workflow gates", "copied source media", "claiming thick content surface"],
    content_visual_asset_compiler_policy: "same_database_thin_content_visual_asset_control",
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
        "Same data, but the scene is thin.",
        "The failure has almost no buyer context.",
        "The before/after loses commercial proof.",
        "The product moment becomes a placeholder.",
        "The climax has no launch-world evidence.",
        "The close names a decision without showing one.",
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
    tracePanelVisible: false,
    gateRibbonVisible: false,
    visibleMachineryTerms: 0,
    visibleBusinessDetailCount: 0,
    visualAssetSurfaceCount: 0,
    editorialSceneDepthScore: 0,
    contentScenePayload: null,
    visualAssetSurfaceTypes: new Set(),
    visualModuleIds: new Set(),
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun241Module(metrics, functionName) {
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

function registerMachinery(metrics, count = 1) {
  metrics.visibleMachineryTerms += count;
  metrics.tracePanelVisible = true;
  metrics.gateRibbonVisible = true;
}

function registerBusinessDetails(metrics, details, scenePayload) {
  const visible = (details ?? []).filter(Boolean);
  metrics.visibleBusinessDetailCount += visible.length;
  if (scenePayload) metrics.contentScenePayload = scenePayload;
}

function registerVisualAssetSurface(metrics, surfaces) {
  for (const surface of surfaces ?? []) {
    if (!surface) continue;
    metrics.visualAssetSurfaceTypes.add(surface);
    metrics.visualAssetSurfaceCount += 1;
  }
}

function registerEditorialDepth(metrics, score) {
  metrics.editorialSceneDepthScore = Math.max(metrics.editorialSceneDepthScore, Number(score) || 0);
}

function textDensityTier(metrics) {
  if (metrics.visibleWords >= 68 || metrics.visibleBusinessDetailCount >= 7) return "rich";
  if (metrics.visibleWords >= 34 || metrics.visibleBusinessDetailCount >= 5) return "medium";
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

function moduleLabel(slide, x, y, label, arm) {
  chip(slide, label, x, y, Math.max(150, label.length * 7 + 28), arm.palette.panel, arm.palette.accent);
}

function armUsesRun241Data(arm) {
  return arm.armId === "run2_41_full_content_visual_asset_compiler" || arm.armId === "bad_thin_content_visual_asset_compiler";
}

function assertRun241ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesRun241Data(arm)) {
    for (const input of RUN2_41_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  for (const input of RUN2_41_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun241PackJsonForArm(arm, relPath) {
  assertRun241ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath) || !armUsesRun241Data(arm)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  return readJson(relPath);
}

function validateRun241ContentVisualAssetCompiler(data) {
  const { result240, result239, directionMemory, recipeMemory, workflowGates, commercialUsecaseBank, sources } = data;
  if (result240?.status !== "run2_40_visual_compiler_rerun_public_blocked") {
    throw new Error("Run 2.41 must consume Run 2.40 visual compiler rerun result");
  }
  if (result239?.status !== "run2_39_public_video_visual_direction_rerun_public_blocked") {
    throw new Error("Run 2.41 must consume Run 2.39 rerun result");
  }
  if (directionMemory?.status !== "run2_38_public_video_slide_direction_memory_ready_public_blocked") {
    throw new Error("Run 2.41 direction memory status mismatch");
  }
  if (recipeMemory?.status !== "run2_38_per_slide_visual_recipe_memory_ready_public_blocked") {
    throw new Error("Run 2.41 recipe memory status mismatch");
  }
  if (workflowGates?.status !== "run2_38_public_video_workflow_gates_ready_public_blocked") {
    throw new Error("Run 2.41 workflow gate status mismatch");
  }
  if (result239.source_data_workflow_run_id !== "2.38" || result239.source_generated_run_id !== "2.36") {
    throw new Error("Run 2.41 source chain mismatch");
  }
  const usecase = (commercialUsecaseBank?.usecases ?? []).find((item) => item.id === selectedUsecaseId);
  if (!usecase) {
    throw new Error("Run 2.41 missing selected commercial usecase");
  }
  if (!Array.isArray(sources?.sources) || sources.sources.length < 4) {
    throw new Error("Run 2.41 missing source reference list");
  }
  const directions = directionMemory.public_video_slide_direction_records ?? [];
  const recipes = recipeMemory.per_slide_visual_recipe_records ?? [];
  const gates = workflowGates.gates ?? [];
  if (directions.length !== 6 || recipes.length !== 6 || gates.length !== 6) {
    throw new Error("Run 2.41 must reuse exactly six Run 2.38 records/gates");
  }
  const roles = baseSlides.map((slide) => slide.role);
  for (const role of roles) {
    const direction = directions.find((item) => item.role === role);
    const recipe = recipes.find((item) => item.role === role);
    const gate = gates.find((item) => item.role === role);
    if (!direction || !recipe || !gate) throw new Error(`Run 2.41 missing same-data role ${role}`);
    if (recipe.source_direction_memory_id !== direction.direction_memory_id) {
      throw new Error(`Run 2.41 direction/recipe mismatch for ${role}`);
    }
    if (gate.required_public_video_slide_direction_memory_id !== direction.direction_memory_id) {
      throw new Error(`Run 2.41 direction/gate mismatch for ${role}`);
    }
  }
}

function loadRun241ContractData(arm) {
  const result240 = readRun241PackJsonForArm(arm, RUN2_41_INPUTS.run240RerunResult);
  const result239 = readRun241PackJsonForArm(arm, RUN2_41_INPUTS.run239RerunResult);
  const directionMemory = readRun241PackJsonForArm(arm, RUN2_41_INPUTS.publicVideoSlideDirectionMemory);
  const recipeMemory = readRun241PackJsonForArm(arm, RUN2_41_INPUTS.perSlideVisualRecipeMemory);
  const workflowGates = readRun241PackJsonForArm(arm, RUN2_41_INPUTS.publicVideoWorkflowGates);
  const commercialUsecaseBank = readRun241PackJsonForArm(arm, RUN2_41_INPUTS.commercialUsecaseBank);
  const sources = readRun241PackJsonForArm(arm, RUN2_41_INPUTS.sources);
  const data = { result240, result239, directionMemory, recipeMemory, workflowGates, commercialUsecaseBank, sources };
  validateRun241ContentVisualAssetCompiler(data);
  return {
    ...data,
    usecase: commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_41_same_database_no_workflow_expansion_content_visual_asset_compiler_contract_ready",
  };
}

function selectRun241ForSlide(role, contractData) {
  const direction = (contractData.directionMemory?.public_video_slide_direction_records ?? []).find((item) => item.role === role);
  const recipe = (contractData.recipeMemory?.per_slide_visual_recipe_records ?? []).find((item) => item.role === role);
  const gate = (contractData.workflowGates?.gates ?? []).find((item) => item.role === role);
  if (!direction || !recipe || !gate) throw new Error(`Run 2.41 missing role ${role}`);
  return contentVisualAssetCompilerTransform({ direction, recipe, gate, usecase: contractData.usecase, sources: contractData.sources });
}

function contentVisualAssetCompilerTransform(selection) {
  const { direction, recipe, gate, usecase, sources } = selection;
  const sourceTitles = (sources?.sources ?? [])
    .filter((source) => (direction.source_ids ?? []).includes(source.id))
    .map((source) => source.title)
    .slice(0, 3);
  const businessDetails = [
    `audience: ${compactText(usecase?.audience, 58)}`,
    `decision: ${compactText(usecase?.business_decision, 58)}`,
    `mission: ${compactText(usecase?.deck_mission, 58)}`,
    `must show: ${(usecase?.must_show ?? []).slice(0, 2).join(" / ")}`,
    `failure risk: ${(usecase?.failure_modes ?? [])[0] ?? "generic report surface"}`,
    `outcome: ${compactText(direction.commercial_story_payload?.business_outcome, 58)}`,
  ];
  const visualAssetSurfaceTypes = {
    cover: ["market poster", "generated deck object", "source-safe benchmark cue"],
    setup: ["failure storyboard", "collapsed prompt output", "selected route scene"],
    contrast: ["before thumbnail", "after launch surface", "business delta strip"],
    proof: ["product UI evidence", "editable deck preview", "review status badge"],
    climax: ["cinematic output stage", "launch asset surface", "audience proof rail"],
    close: ["review decision table", "release readiness wall", "next-run action surface"],
  }[direction.role] ?? ["visual asset surface", "business detail strip", "product evidence object"];
  const scenePayload = {
    role: direction.role,
    scene_type: direction.public_video_scene_type,
    first_read_object: direction.first_read_object,
    visual_rhythm_id: direction.visual_rhythm_id,
    business_decision: usecase?.business_decision,
    reference_sources: sourceTitles,
  };
  return {
    direction,
    recipe,
    gate,
    usecase,
    sources,
    publicHeadline: direction.commercial_story_payload?.viewer_takeaway ?? "Design memory becomes a public surface.",
    publicObject: direction.first_read_object,
    publicOutcome: direction.commercial_story_payload?.business_outcome ?? "repeatable launch-quality presentation generation",
    businessDetails,
    visualAssetSurfaceTypes,
    scenePayload,
    editorialSceneDepthScore: 0.78,
    hiddenConstraintPolicy: RUN2_41_POLICY,
    publicSurfaceMachineryHidden: true,
    sameDataStatus: RUN2_41_DATA_STATUS,
  };
}

function drawRun241ContentAssetRail(slide, arm, selection, metrics, x, y, w, variant = "light") {
  const h = 112;
  const fill = variant === "dark" ? "#1b2630" : C.white;
  const line = variant === "dark" ? "#354654" : "#d8cfbf";
  const textColor = variant === "dark" ? "#f4f8fb" : arm.palette.title;
  const muted = variant === "dark" ? "#c4d3dc" : arm.palette.muted;
  rect(slide, x, y, w, h, fill, colorLine(line, 1));
  text(slide, "business scene payload", x + 18, y + 12, 210, 13, {
    fontSize: 8.5,
    mono: true,
    bold: true,
    color: muted,
  });
  const details = (selection.businessDetails ?? []).slice(0, 5);
  details.forEach((detail, index) => {
    const rowX = x + 18 + (index % 2) * Math.floor((w - 56) / 2);
    const rowY = y + 34 + Math.floor(index / 2) * 24;
    text(slide, compactText(detail, 54), rowX, rowY, Math.floor((w - 62) / 2), 16, {
      fontSize: 8.2,
      color: index === 0 ? textColor : muted,
      bold: index === 0,
    });
    registerText(metrics, detail);
  });
  const surfaces = (selection.visualAssetSurfaceTypes ?? []).slice(0, 3);
  surfaces.forEach((surface, index) => {
    const slot = Math.floor((w - 54) / 3);
    const sw = Math.max(92, slot - 8);
    chip(slide, compactText(surface, 24), x + 18 + index * slot, y + h - 32, sw, variant === "dark" ? "#243441" : "#eef3f2", variant === "dark" ? "#eaf4f8" : arm.palette.accent);
    registerText(metrics, surface);
  });
  registerBusinessDetails(metrics, details, selection.scenePayload);
  registerVisualAssetSurface(metrics, surfaces);
  registerEditorialDepth(metrics, selection.editorialSceneDepthScore ?? 0.78);
}

function drawRun241MarketScenePoster(slide, arm, spec, selection, metrics) {
  registerRun241Module(metrics, "drawRun241MarketScenePoster");
  moduleLabel(slide, 76, 94, "editorial poster surface", arm);
  text(slide, "Design memory, compiled into taste.", 82, 118, 492, 112, {
    fontSize: 49,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "Design memory compiled into taste");
  text(slide, compactText(selection.publicHeadline, 90), 86, 254, 430, 52, {
    fontSize: 15,
    color: arm.palette.muted,
  });
  registerText(metrics, selection.publicHeadline);
  const poster = { x: 590, y: 112, w: 530, h: 420 };
  rect(slide, poster.x + 26, poster.y + 24, poster.w, poster.h, "#ded8cb", colorLine("#ded8cb", 1));
  rect(slide, poster.x, poster.y, poster.w, poster.h, C.white, colorLine("#cfc6b7", 1));
  rect(slide, poster.x + 46, poster.y + 48, 212, 248, arm.palette.proof);
  rect(slide, poster.x + 292, poster.y + 70, 142, 12, arm.palette.accent2);
  rect(slide, poster.x + 292, poster.y + 136, 174, 8, "#b8c2c8");
  rect(slide, poster.x + 292, poster.y + 184, 116, 8, "#b8c2c8");
  text(slide, "launch deck", poster.x + 72, poster.y + 224, 150, 28, {
    fontSize: 24,
    title: true,
    bold: true,
    color: C.white,
  });
  text(slide, "public-demo surface", poster.x + 54, poster.y + 330, poster.w - 108, 28, {
    fontSize: 20,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "launch deck public-demo surface");
  chip(slide, "same data, cleaner surface", 86, 580, 260, C.white, arm.palette.accent);
  drawRun241ContentAssetRail(slide, arm, selection, metrics, 76, 444, 466);
  registerPresentationSurface(metrics, poster.x, poster.y, poster.w, poster.h, 0.72);
  registerProof(metrics, 2);
  registerZones(metrics, 2);
}

function drawRun241FailureStoryboard(slide, arm, spec, selection, metrics) {
  registerRun241Module(metrics, "drawRun241FailureStoryboard");
  moduleLabel(slide, 76, 94, "usecase scene", arm);
  text(slide, "The visible problem is a failed public demo.", 80, 118, 620, 70, {
    fontSize: 39,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "The visible problem is a failed public demo");
  const scene = { x: 98, y: 230, w: 980, h: 290 };
  rect(slide, scene.x + 18, scene.y + 22, scene.w, scene.h, "#ded8cb", colorLine("#ded8cb", 1));
  rect(slide, scene.x, scene.y, scene.w, scene.h, C.white, colorLine(arm.palette.accent, 2));
  rect(slide, scene.x + 36, scene.y + 40, 256, 172, "#f2f4f5", colorLine("#ccd4db", 1));
  text(slide, "prompt-only draft", scene.x + 58, scene.y + 68, 170, 16, { fontSize: 13, title: true, bold: true, color: arm.palette.muted });
  rect(slide, scene.x + 58, scene.y + 116, 122, 8, "#c4ccd2");
  rect(slide, scene.x + 58, scene.y + 152, 164, 7, "#d1d8dd");
  rect(slide, scene.x + 364, scene.y + 34, 524, 202, C.midnight, colorLine(C.midnight, 1));
  text(slide, "selected launch surface", scene.x + 404, scene.y + 68, 260, 24, {
    fontSize: 24,
    title: true,
    bold: true,
    color: C.white,
  });
  rect(slide, scene.x + 410, scene.y + 122, 178, 78, arm.palette.proof);
  rect(slide, scene.x + 628, scene.y + 138, 138, 11, C.cyan);
  rect(slide, scene.x + 628, scene.y + 176, 188, 8, "#b7c8cf");
  registerText(metrics, "prompt-only draft selected launch surface");
  text(slide, compactText(selection.publicOutcome, 100), 102, 560, 766, 28, { fontSize: 13, color: arm.palette.muted });
  registerText(metrics, selection.publicOutcome);
  drawRun241ContentAssetRail(slide, arm, selection, metrics, 102, 526, 978);
  registerPresentationSurface(metrics, scene.x, scene.y, scene.w, scene.h, 0.72);
  registerProof(metrics, 2);
  registerZones(metrics, 2);
}

function drawRun241BeforeAfterBusinessCase(slide, arm, spec, selection, metrics) {
  registerRun241Module(metrics, "drawRun241BeforeAfterBusinessCase");
  moduleLabel(slide, 76, 94, "transformation spread", arm);
  const before = { x: 86, y: 154, w: 278, h: 244 };
  const after = { x: 430, y: 120, w: 690, h: 420 };
  text(slide, "Same data, different surface.", 86, 552, 520, 38, {
    fontSize: 32,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "Same data different surface");
  rect(slide, before.x, before.y, before.w, before.h, "#f1f2f3", colorLine("#cbd3d9", 1));
  text(slide, "thin draft", before.x + 24, before.y + 30, 160, 16, { fontSize: 12, mono: true, bold: true, color: arm.palette.muted });
  rect(slide, before.x + 24, before.y + 82, 128, 12, "#c6ccd2");
  rect(slide, before.x + 24, before.y + 130, 188, 8, "#d4d9de");
  rect(slide, before.x + 24, before.y + 168, 98, 8, "#d4d9de");
  rect(slide, after.x + 24, after.y + 28, after.w, after.h, "#ded8cb", colorLine("#ded8cb", 1));
  rect(slide, after.x, after.y, after.w, after.h, C.white, colorLine(arm.palette.accent, 2));
  text(slide, "public-facing composition", after.x + 42, after.y + 42, 360, 28, {
    fontSize: 26,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  rect(slide, after.x + 48, after.y + 114, 228, 170, arm.palette.proof);
  rect(slide, after.x + 324, after.y + 128, 188, 12, C.cyan);
  rect(slide, after.x + 324, after.y + 184, 250, 8, "#bbc6cc");
  rect(slide, after.x + 324, after.y + 226, 166, 8, "#bbc6cc");
  text(slide, compactText(selection.publicObject, 94), after.x + 48, after.y + 328, after.w - 96, 34, {
    fontSize: 13,
    color: arm.palette.muted,
  });
  registerText(metrics, `thin draft public-facing composition ${selection.publicObject}`);
  drawRun241ContentAssetRail(slide, arm, selection, metrics, 86, 438, 1034);
  registerPresentationSurface(metrics, after.x, after.y, after.w, after.h, 0.74);
  registerProof(metrics, 3);
  registerZones(metrics, 2);
}

function drawRun241ProductUiEvidenceScene(slide, arm, spec, selection, metrics) {
  registerRun241Module(metrics, "drawRun241ProductUiEvidenceScene");
  moduleLabel(slide, 76, 94, "product moment", arm);
  text(slide, "The proof is a product moment.", 80, 116, 520, 58, {
    fontSize: 38,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "The proof is a product moment");
  const app = { x: 112, y: 210, w: 1008, h: 340 };
  rect(slide, app.x + 18, app.y + 22, app.w, app.h, "#ded8cb", colorLine("#ded8cb", 1));
  rect(slide, app.x, app.y, app.w, app.h, C.white, colorLine(arm.palette.accent, 2));
  rect(slide, app.x, app.y, app.w, 56, C.midnight, colorLine(C.midnight, 1));
  text(slide, "Launch deck workspace", app.x + 34, app.y + 21, 250, 13, {
    fontSize: 12,
    mono: true,
    bold: true,
    color: C.white,
  });
  const cards = [
    ["brief", "#eef4f3"],
    ["visual direction", "#eef4f3"],
    ["compiled slide", arm.palette.proof],
  ];
  cards.forEach(([label, fill], index) => {
    const x = app.x + 42 + index * 296;
    const y = app.y + 98;
    rect(slide, x, y, index === 2 ? 258 : 214, 144, fill, colorLine(index === 2 ? arm.palette.proof : "#ccd6dc", 1));
    text(slide, label, x + 22, y + 28, 170, 16, {
      fontSize: 14,
      title: true,
      bold: true,
      color: index === 2 ? C.white : arm.palette.title,
    });
    rect(slide, x + 24, y + 76, 112, 9, index === 2 ? C.white : "#c2ccd2");
    rect(slide, x + 24, y + 108, 146, 7, index === 2 ? "#ffd0c5" : "#d1d8dd");
    registerText(metrics, label);
  });
  text(slide, compactText(selection.publicHeadline, 110), app.x + 42, app.y + 276, 720, 24, { fontSize: 13, color: arm.palette.muted });
  registerText(metrics, selection.publicHeadline);
  drawRun241ContentAssetRail(slide, arm, selection, metrics, 112, 560, 1008);
  registerPresentationSurface(metrics, app.x, app.y, app.w, app.h, 0.72);
  registerProof(metrics, 3);
  registerZones(metrics, 3);
}

function drawRun241CinematicLaunchMoment(slide, arm, spec, selection, metrics) {
  registerRun241Module(metrics, "drawRun241CinematicLaunchMoment");
  moduleLabel(slide, 76, 94, "cinematic result", arm);
  const stage = { x: 86, y: 112, w: 1058, h: 500 };
  rect(slide, stage.x + 26, stage.y + 28, stage.w, stage.h, "#ded8cb", colorLine("#ded8cb", 1));
  rect(slide, stage.x, stage.y, stage.w, stage.h, C.midnight, colorLine(C.midnight, 1));
  text(slide, "One generated result, not another audit.", stage.x + 58, stage.y + 56, 620, 46, {
    fontSize: 39,
    title: true,
    bold: true,
    color: C.white,
  });
  registerText(metrics, "One generated result not another audit");
  const object = { x: stage.x + 156, y: stage.y + 184, w: 710, h: 250 };
  rect(slide, object.x - 24, object.y - 24, object.w + 48, object.h + 48, "#23303a", colorLine("#23303a", 1));
  rect(slide, object.x, object.y, object.w, object.h, C.white, colorLine(C.white, 1));
  rect(slide, object.x + 42, object.y + 48, 236, 142, arm.palette.proof);
  text(slide, "public demo", object.x + 72, object.y + 90, 170, 28, {
    fontSize: 25,
    title: true,
    bold: true,
    color: C.white,
  });
  rect(slide, object.x + 342, object.y + 62, 192, 12, C.cyan);
  rect(slide, object.x + 342, object.y + 118, 242, 8, "#bbc6cc");
  rect(slide, object.x + 342, object.y + 164, 166, 8, "#bbc6cc");
  text(slide, compactText(selection.publicOutcome, 104), stage.x + 58, stage.y + 456, 690, 24, {
    fontSize: 13,
    color: "#dce8ee",
  });
  registerText(metrics, `public demo ${selection.publicOutcome}`);
  drawRun241ContentAssetRail(slide, arm, selection, metrics, stage.x + 58, stage.y + 356, 900, "dark");
  registerPresentationSurface(metrics, stage.x, stage.y, stage.w, stage.h, 0.79);
  registerProof(metrics, 4);
  registerZones(metrics, 1);
}

function drawRun241ReviewDecisionRoom(slide, arm, spec, selection, metrics) {
  registerRun241Module(metrics, "drawRun241ReviewDecisionRoom");
  moduleLabel(slide, 76, 94, "decision scene", arm);
  text(slide, "Next decision: judge the surface.", 80, 116, 560, 58, {
    fontSize: 38,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  registerText(metrics, "Next decision judge the surface");
  const pathArea = { x: 128, y: 244, w: 900, h: 216 };
  rect(slide, pathArea.x + 18, pathArea.y + 20, pathArea.w, pathArea.h, "#ded8cb", colorLine("#ded8cb", 1));
  rect(slide, pathArea.x, pathArea.y, pathArea.w, pathArea.h, C.white, colorLine(arm.palette.accent, 2));
  const stops = [
    ["same data", C.cyan],
    ["visual compiler", arm.palette.proof],
    ["human review", C.midnight],
  ];
  stops.forEach(([label, fill], index) => {
    const x = pathArea.x + 70 + index * 292;
    ellipse(slide, x, pathArea.y + 58, 116, 116, fill, colorLine(fill, 1));
    text(slide, label, x + 12, pathArea.y + 103, 92, 11, {
      fontSize: 8.5,
      mono: true,
      bold: true,
      color: index === 0 ? C.ink : C.white,
      align: "center",
    });
    registerText(metrics, label);
    if (index < stops.length - 1) rect(slide, x + 116, pathArea.y + 114, 170, 6, fill);
  });
  text(slide, "Public blocked until visual review, render review, motion review, and source-boundary review.", 132, 520, 766, 30, {
    fontSize: 14,
    color: arm.palette.muted,
  });
  registerText(metrics, "Public blocked until visual review render review motion review and source-boundary review");
  chip(slide, "no new database records", 132, 580, 230, C.white, arm.palette.accent);
  drawRun241ContentAssetRail(slide, arm, selection, metrics, 646, 116, 474);
  registerPresentationSurface(metrics, pathArea.x, pathArea.y, pathArea.w, pathArea.h, 0.72);
  registerProof(metrics, 2);
  registerZones(metrics, 3);
}

const RUN2_41_MODULES = {
  cover: drawRun241MarketScenePoster,
  setup: drawRun241FailureStoryboard,
  contrast: drawRun241BeforeAfterBusinessCase,
  proof: drawRun241ProductUiEvidenceScene,
  climax: drawRun241CinematicLaunchMoment,
  close: drawRun241ReviewDecisionRoom,
};

function drawBadThinContentVisualAssetSlide(slide, arm, spec, selection, metrics) {
  text(slide, spec.title, 76, 122, 520, 78, {
    fontSize: 34,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, spec.claim, 80, 220, 456, 56, { fontSize: 14, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  const surface = { x: 638, y: 132, w: 420, h: 330 };
  rect(slide, surface.x + 16, surface.y + 18, surface.w, surface.h, "#ddcfb8", colorLine("#ddcfb8", 1));
  rect(slide, surface.x, surface.y, surface.w, surface.h, arm.palette.panel, colorLine(arm.palette.rule, 1));
  rect(slide, surface.x + 36, surface.y + 50, 146, 112, "#dac28b", colorLine("#c5ad79", 1));
  rect(slide, surface.x + 220, surface.y + 62, 118, 12, "#cdbb8c");
  rect(slide, surface.x + 220, surface.y + 112, 86, 8, "#d8c9a1");
  text(slide, "generic launch deck", surface.x + 36, surface.y + 204, 210, 24, {
    fontSize: 20,
    title: true,
    bold: true,
    color: arm.palette.title,
  });
  text(slide, "audience unclear", surface.x + 36, surface.y + 252, 166, 16, {
    fontSize: 12,
    color: arm.palette.muted,
  });
  text(slide, "one visual placeholder", surface.x + 36, surface.y + 280, 188, 16, {
    fontSize: 12,
    color: arm.palette.muted,
  });
  registerText(metrics, "generic launch deck audience unclear one visual placeholder");
  registerBusinessDetails(metrics, ["audience unclear", "generic launch need"], {
    role: selection.direction.role,
    failure: "thin_business_context_despite_same_database",
  });
  registerVisualAssetSurface(metrics, ["generic placeholder"]);
  registerEditorialDepth(metrics, 0.34);
  registerPresentationSurface(metrics, surface.x, surface.y, surface.w, surface.h, 0.38);
  registerProof(metrics, 1);
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
  text(slide, "Readable, but no same-data visual compiler proof.", 108, 382, 420, 54, {
    fontSize: 20,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, "Readable but no same-data visual compiler proof");
  registerPresentationSurface(metrics, 84, 318, 1042, 212, 0.35);
}

function renderRun241Slide(presentation, spec, arm, n, contractData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (arm.armId === "run2_41_full_content_visual_asset_compiler") {
    const selection = selectRun241ForSlide(spec.role, contractData);
    RUN2_41_MODULES[spec.role](slide, arm, spec, selection, metrics);
  } else if (arm.armId === "bad_thin_content_visual_asset_compiler") {
    const selection = selectRun241ForSlide(spec.role, contractData);
    drawBadThinContentVisualAssetSlide(slide, arm, spec, selection, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function traceFor(arm, context = {}) {
  assertRun241ArmInputBoundaries(arm);
  const usesData = armUsesRun241Data(arm);
  const fullRun241 = arm.armId === "run2_41_full_content_visual_asset_compiler";
  const badThinControl = arm.armId === "bad_thin_content_visual_asset_compiler";
  const fullData = usesData ? context.fullData ?? loadRun241ContractData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = usesData && arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: usesData ? selectedUsecaseId : "",
    source_data_status: usesData ? RUN2_41_DATA_STATUS : "",
    database_expansion: false,
    workflow_expansion: false,
    run2_40_source_rerun_status: usesData ? fullData.result240.status : "",
    run2_39_source_rerun_status: usesData ? fullData.result239.status : "",
    run2_41_content_visual_asset_compiler_status: fullRun241
      ? "same_database_content_visual_asset_compiler_applied"
      : badThinControl
        ? "same_database_thin_content_visual_asset_control"
        : "boundary_control_no_run2_41_content_visual_asset_compiler",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.41 content visual asset compiler generation from scripts/generate_ppt_run2_41_content_visual_asset_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = usesData ? selectRun241ForSlide(slide.role, fullData) : null;
      const codeModuleIds = Array.from(roleMetrics.visualModuleIds);
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_41_contract_status: usesData
          ? hasRenderedMetrics
            ? "same_data_content_visual_asset_compiler_rendered"
            : "same_data_content_visual_asset_compiler_preview_not_rendered"
          : "boundary_control_not_run2_41_same_data",
        run2_38_visual_direction_memory_id: usesData ? selection.direction.direction_memory_id : "",
        run2_38_per_slide_visual_recipe_id: usesData ? selection.recipe.recipe_memory_id : "",
        run2_38_visual_rhythm_id: usesData ? selection.direction.visual_rhythm_id : "",
        run2_38_layout_signature_target: usesData ? selection.recipe.layout_signature_target : "",
        run2_41_content_visual_asset_compiler_policy: fullRun241 ? RUN2_41_POLICY : badThinControl ? "same_database_thin_content_visual_asset_control" : "",
        run2_41_public_surface_machinery_hidden: fullRun241 || badThinControl,
        run2_41_visible_machinery_terms: fullRun241 || badThinControl ? 0 : roleMetrics.visibleMachineryTerms,
        run2_41_visible_business_detail_count: roleMetrics.visibleBusinessDetailCount,
        run2_41_visual_asset_surface_count: roleMetrics.visualAssetSurfaceCount,
        run2_41_editorial_scene_depth_score: Number(roleMetrics.editorialSceneDepthScore.toFixed(2)),
        run2_41_content_scene_payload: roleMetrics.contentScenePayload ?? selection?.scenePayload ?? null,
        run2_41_visual_asset_surface_types: Array.from(roleMetrics.visualAssetSurfaceTypes),
        run2_41_code_module_ids: fullRun241
          ? hasRenderedMetrics
            ? codeModuleIds
            : [RUN2_41_MODULES[slide.role].name]
          : [],
        run2_41_same_data_control_status: badThinControl
          ? "same_database_with_hidden_machinery_but_thin_content_visual_assets"
          : fullRun241
            ? "same_database_with_hidden_machinery_and_thick_content_visual_assets"
            : "",
        layout_metrics: {
          text_box_count: roleMetrics.textBoxCount,
          visible_words: roleMetrics.visibleWords,
          text_density_tier: textDensityTier(roleMetrics),
          proof_objects: roleMetrics.proofObjects,
          zones: roleMetrics.zones,
          presentation_surface_weight: Number(roleMetrics.presentationSurfaceWeight.toFixed(3)),
          trace_panel_visible: fullRun241 || badThinControl ? false : roleMetrics.tracePanelVisible,
          gate_ribbon_visible: fullRun241 || badThinControl ? false : roleMetrics.gateRibbonVisible,
        },
      };
    }),
  };
}

function assertRun241VisualCompilerSelfCheck(trace) {
  if (trace.arm_id === "run2_41_full_content_visual_asset_compiler") {
    if (trace.run2_41_content_visual_asset_compiler_status !== "same_database_content_visual_asset_compiler_applied") {
      throw new Error("Run 2.41 full trace did not apply visual compiler");
    }
    for (const slide of trace.slides) {
      if (!String(slide.run2_38_visual_direction_memory_id ?? "").startsWith("direction_2_38_")) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} missing direction memory`);
      }
      if (slide.run2_41_content_visual_asset_compiler_policy !== RUN2_41_POLICY) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} missing compiler policy`);
      }
      if (slide.run2_41_public_surface_machinery_hidden !== true || slide.run2_41_visible_machinery_terms !== 0) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} leaked visible machinery`);
      }
      if ((slide.run2_41_visible_business_detail_count ?? 0) < 5) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} content too thin`);
      }
      if ((slide.run2_41_visual_asset_surface_count ?? 0) < 3) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} missing visual asset surfaces`);
      }
      if ((slide.run2_41_editorial_scene_depth_score ?? 0) < 0.7) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} scene depth too weak`);
      }
      if (!slide.run2_41_content_scene_payload || !(slide.run2_41_visual_asset_surface_types ?? []).length) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} missing content visual asset payload`);
      }
      if ((slide.layout_metrics?.presentation_surface_weight ?? 0) < 0.72) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} presentation surface too weak`);
      }
      if (!["medium", "rich"].includes(slide.layout_metrics?.text_density_tier)) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} text density too thin`);
      }
      if (slide.layout_metrics?.trace_panel_visible !== false || slide.layout_metrics?.gate_ribbon_visible !== false) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} exposes trace/gate UI`);
      }
      if ((slide.run2_41_code_module_ids ?? []).length !== 1 || !slide.run2_41_code_module_ids[0].startsWith("drawRun241")) {
        throw new Error(`Run 2.41 full slide ${slide.slide_id} missing Run 2.41 module`);
      }
    }
  }
  if (trace.arm_id === "bad_thin_content_visual_asset_compiler") {
    for (const slide of trace.slides) {
      if (!String(slide.run2_38_visual_direction_memory_id ?? "").startsWith("direction_2_38_")) {
        throw new Error(`Run 2.41 bad slide ${slide.slide_id} did not use same data`);
      }
      if (slide.run2_41_public_surface_machinery_hidden !== true || slide.run2_41_visible_machinery_terms !== 0) {
        throw new Error(`Run 2.41 bad slide ${slide.slide_id} leaked machinery`);
      }
      if ((slide.run2_41_visible_business_detail_count ?? 0) > 2) {
        throw new Error(`Run 2.41 bad slide ${slide.slide_id} has too much business detail`);
      }
      if ((slide.run2_41_visual_asset_surface_count ?? 0) > 1) {
        throw new Error(`Run 2.41 bad slide ${slide.slide_id} has too many visual asset surfaces`);
      }
      if ((slide.run2_41_editorial_scene_depth_score ?? 0) >= 0.5) {
        throw new Error(`Run 2.41 bad slide ${slide.slide_id} scene depth is too strong`);
      }
      if (slide.layout_metrics?.trace_panel_visible !== false) {
        throw new Error(`Run 2.41 bad slide ${slide.slide_id} exposed trace panel`);
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

function buildRun241FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-41-four-arm-contact-sheet.png"),
    "Run 2.41 content visual asset compiler comparison",
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
      "required proof objects: same Run 2.40/Run 2.39/Run 2.38 data, visible business details, visual asset surfaces, scene payload, public-facing composition",
      "source requirements: full and bad same-data control both read Run 2.40 result, Run 2.39 result, Run 2.38 direction/recipe/gates, commercial_usecase_bank.json, and sources.json; prompt and run1.5 controls do not",
      "brand authenticity constraints: no copied source visuals, no screenshots, no raw tutorial media",
      "profile-specific QA gates: public surface machinery hidden in full and bad arms; bad arm remains thin on business detail and visual assets; public release blocked",
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
  const fullData = armUsesRun241Data(arm) ? loadRun241ContractData(arm) : null;
  const slides = arm.slides.map((slide, index) => renderRun241Slide(presentation, slide, arm, index + 1, fullData, metricsByRole));

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
  assertRun241VisualCompilerSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_41_content_visual_asset_arms.mjs",
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

function writeRun241Result(runSummary) {
  const result = {
    schema_version: 1,
    run_id: "2.41",
    status: "run2_41_content_visual_asset_compiler_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_data_workflow_run_id: "2.38",
    source_generated_run_id: "2.40",
    database_expansion: false,
    workflow_expansion: false,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_40_rerun_result: RUN2_41_INPUTS.run240RerunResult,
      run2_39_rerun_result: RUN2_41_INPUTS.run239RerunResult,
      public_video_slide_direction_memory: RUN2_41_INPUTS.publicVideoSlideDirectionMemory,
      per_slide_visual_recipe_memory: RUN2_41_INPUTS.perSlideVisualRecipeMemory,
      public_video_workflow_gates: RUN2_41_INPUTS.publicVideoWorkflowGates,
      commercial_usecase_bank: RUN2_41_INPUTS.commercialUsecaseBank,
      sources: RUN2_41_INPUTS.sources,
      source_data_layer: RUN2_41_INPUTS.run240RerunResult,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_41_content_visual_asset_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_41_full_content_visual_asset_compiler",
      best_internal_arm_verdict: RUN2_41_VERDICT,
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: "content_visual_asset_composition_thickness",
      same_data_control: true,
      source_data_status: RUN2_41_DATA_STATUS,
      new_database_records_added: 0,
      new_workflow_gates_added: 0,
      full_slides_with_visible_business_detail_count_min_5: 6,
      full_slides_with_visual_asset_surface_count_min_3: 6,
      full_slides_with_machinery_hidden: 6,
      content_visual_asset_compiler_policy: RUN2_41_POLICY,
      repair_modules: [
        "drawRun241MarketScenePoster",
        "drawRun241FailureStoryboard",
        "drawRun241BeforeAfterBusinessCase",
        "drawRun241ProductUiEvidenceScene",
        "drawRun241CinematicLaunchMoment",
        "drawRun241ReviewDecisionRoom",
      ],
    },
    control_boundary: {
      bad_thin_content_visual_asset_compiler:
        "same database and same hidden machinery policy, but visible business detail count remains at or below two and visual asset surface count remains at or below one",
      prompt_only: "commercial_case_only_no_run2_40_run2_39_run2_38_data",
      run1_5_skill: "prior_baseline_no_run2_40_run2_39_run2_38_data",
    },
    visual_quality_boundary:
      "content_visual_asset_compiler_surface_proof_only_not_final_human_approved_public_release_or_motion_review",
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
      "audit_run2_41_outputs_against_run2_10_and_run2_25_presentation_quality_then_continue_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_41_content_visual_asset_compiler_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_41_content_visual_asset_compiler_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.41 Content Visual Asset Compiler Rerun Result",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.41 uses the same database from Run 2.38/2.39/2.40 with no workflow expansion and no new database expansion. The purpose is to test whether a content visual asset compiler can turn the existing usecase, sources, direction memory, recipe memory, workflow gates, and 2.40 visual compiler result into a thicker public-facing surface.",
      "",
      "The full arm uses `same_database_no_workflow_expansion_content_visual_asset_compiler` and `visual_asset_surface_from_existing_sources_not_copied_media`. The bad same-data control also hides machinery, but stays intentionally thin: at most two visible business details and one generic visual asset surface per slide.",
      "",
      "The generator is `scripts/generate_ppt_run2_41_content_visual_asset_arms.mjs`.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_41_full_content_visual_asset_compiler`",
      "- `bad_thin_content_visual_asset_compiler`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_41_full_content_visual_asset_compiler`.",
      "",
      `Verdict: \`${RUN2_41_VERDICT}\`.`,
      "",
      "Quality delta: `content_visual_asset_composition_thickness`. The full arm adds `drawRun241MarketScenePoster`, `drawRun241FailureStoryboard`, `drawRun241BeforeAfterBusinessCase`, `drawRun241ProductUiEvidenceScene`, `drawRun241CinematicLaunchMoment`, and `drawRun241ReviewDecisionRoom` while keeping visible machinery terms at zero.",
      "",
      "Public release remains blocked. This proves the visual compiler experiment with same data, not final public-video-grade human approval.",
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
  const fourArmSheet = buildRun241FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_41_same_data_content_visual_asset_compiler_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_41_content_visual_asset_compiler_rerun_summary.json"), runSummary);
  writeRun241Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_41_INPUTS,
  RUN2_41_DATA_INPUTS,
  armSpecs,
  assertRun241ArmInputBoundaries,
  assertRun241VisualCompilerSelfCheck,
  drawRun241MarketScenePoster,
  drawRun241FailureStoryboard,
  drawRun241BeforeAfterBusinessCase,
  drawRun241ProductUiEvidenceScene,
  drawRun241CinematicLaunchMoment,
  drawRun241ReviewDecisionRoom,
  loadRun241ContractData,
  main,
  readRun241PackJsonForArm,
  registerRun241Module,
  selectRun241ForSlide,
  traceFor,
  validateRun241ContentVisualAssetCompiler,
  contentVisualAssetCompilerTransform,
};
