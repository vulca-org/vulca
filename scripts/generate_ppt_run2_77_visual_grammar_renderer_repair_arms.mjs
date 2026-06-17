import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.77";
const RESULT_JSON = `${pack}/results/run2_77_visual_grammar_renderer_repair_rerun_result.json`;
const RESULT_MD = `${pack}/results/run2_77_visual_grammar_renderer_repair_rerun_result.md`;
const artifactToolPath =
  process.env.ARTIFACT_TOOL_PATH ??
  "/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";
const artifactToolPackage =
  process.env.ARTIFACT_TOOL_PACKAGE ??
  "/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool";

const { Presentation, PresentationFile } = await import(pathToFileURL(artifactToolPath).href);

const W = 1280;
const H = 720;
const ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"];
const MODULE_BY_ROLE = {
  cover: "product_reveal",
  setup: "hero_field",
  contrast: "before_after_theater",
  proof: "evidence_workspace",
  climax: "product_reveal",
  close: "decision_map",
};
const REQUIRED_SOCKET_KEYS = [
  "headline_socket",
  "proof_label_sockets",
  "supporting_copy_socket",
  "callout_sockets",
  "viewer_note_socket",
];
const BOUND_VISUAL_OBJECT_TYPES = new Set([
  "product edge",
  "field route",
  "comparison seam",
  "evidence rail",
  "decision node",
  "negative space pocket",
  "connector endpoint",
]);
const FORBIDDEN_TEXT_PATTERNS = [
  "empty text box",
  "generic rectangle label",
  "duplicated headline/supporting copy",
  "text floating without bound visual object",
  "all slides using the same text layout",
];
const RUN2_77_INPUTS = {
  sourceJVisualQualityEvaluation: "docs/product/ppt-run2-data-skill-quality/results/run2_76_visual_quality_evaluation.json",
  run275RendererRepair: "docs/product/ppt-run2-data-skill-quality/results/run2_75_renderer_repair_rerun_result.json",
  visualGrammarModules: "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
  rendererAdapterContracts: "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
  textBindingStrategy: "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
  scenePlanExpansion: "docs/product/ppt-run2-data-skill-quality/run2_73_scene_plan_expansion.json",
  rendererInputValidation: "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_input_validation.json",
  k1RepairPlan: "docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json",
};
const CONSUMED_SOURCES = [
  RUN2_77_INPUTS.sourceJVisualQualityEvaluation,
  RUN2_77_INPUTS.run275RendererRepair,
  RUN2_77_INPUTS.visualGrammarModules,
  RUN2_77_INPUTS.rendererAdapterContracts,
  RUN2_77_INPUTS.textBindingStrategy,
  RUN2_77_INPUTS.scenePlanExpansion,
  RUN2_77_INPUTS.rendererInputValidation,
  RUN2_77_INPUTS.k1RepairPlan,
];
const REPAIR_FLAGS = [
  "k1_repair_plan_consumed",
  "target_scene_direction_applied",
  "page_differentiation_repaired",
  "forbidden_fallbacks_removed",
  "public_polish_not_claimed",
];
const RENDERER_CAPABILITIES_BY_ROLE = {
  cover: ["hero crop", "editorial mask", "asymmetric foreground/background depth", "fewer but more meaningful labels"],
  setup: ["editorial mask", "scene-specific connectors", "asymmetric foreground/background depth"],
  contrast: ["asymmetric foreground/background depth", "scene-specific connectors", "fewer but more meaningful labels"],
  proof: ["larger proof object", "non-grid evidence arrangement", "fewer but more meaningful labels"],
  climax: ["hero crop", "asymmetric foreground/background depth", "larger proof object"],
  close: ["scene-specific connectors", "fewer but more meaningful labels", "editorial mask"],
};
const FORBIDDEN_RENDERER_FALLBACKS = [
  "debug-like outlines",
  "uniform small label wall",
  "same product window skeleton on every page",
  "schematic blueprint as final visual unless it is the actual proof object",
];

const C = {
  ink: "#11151c",
  white: "#fffdf8",
  paper: "#f5efe4",
  slate: "#28323f",
  line: "#d7cfc0",
  muted: "#69727e",
  blue: "#2d62d6",
  cyan: "#64c6d8",
  coral: "#df563f",
  green: "#0d8b68",
  amber: "#e4b34d",
  violet: "#8c7cff",
  dark: "#121922",
};

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-77-prompt-only",
    label: "Prompt-only control",
    mode: "control",
    release: "public_blocked",
    palette: { bg: "#f7f7f4", accent: "#778291", title: C.ink, muted: C.muted, surface: "#ffffff" },
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-77-run1-5-skill",
    label: "Run 1.5 baseline",
    mode: "baseline",
    release: "public_blocked",
    palette: { bg: "#f3f6f8", accent: C.green, title: C.ink, muted: C.muted, surface: "#ffffff" },
  },
  {
    armId: "run2_77_full_visual_grammar_renderer_repair",
    slug: "ppt-run2-77-full-vulca",
    label: "Run 2.77 full renderer repair",
    mode: "full",
    release: "public_blocked",
    palette: { bg: C.paper, accent: C.coral, accent2: C.blue, title: C.ink, muted: C.muted, surface: C.white },
  },
  {
    armId: "bad_run2_77_without_k1_repair_plan",
    slug: "ppt-run2-77-bad-without-k1-repair-plan",
    label: "Bad missing Run 2.77 K1 repair plan",
    mode: "negative",
    release: "internal_only",
    palette: { bg: "#efe8d9", accent: "#8a7652", title: "#262017", muted: "#6b604f", surface: "#fbf3e3" },
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

function repoRelative(absPath) {
  return path.relative(root, absPath).split(path.sep).join("/");
}

function compactText(value, max = 112) {
  const raw = Array.isArray(value) ? value.join(" / ") : value;
  const rendered = String(raw ?? "").replace(/\s+/g, " ").trim();
  if (rendered.length <= max) return rendered;
  const clipped = rendered.slice(0, max).trim();
  return clipped.includes(" ") ? clipped.replace(/\s+\S*$/, "").trim() : clipped;
}

function wordsIn(value) {
  return String(value ?? "").trim().split(/\s+/).filter(Boolean).length;
}

async function blobToBuffer(blob) {
  if (blob?.data instanceof Uint8Array) return Buffer.from(blob.data);
  const arrayBuffer = await blob.arrayBuffer();
  return Buffer.from(arrayBuffer);
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

function line(color = C.line, width = 1) {
  return { color, width };
}

function rect(slide, x, y, w, h, fill, lineSpec) {
  if (w <= 0 || h <= 0) return null;
  return ctx.addShape(slide, { x, y, w, h, fill, line: lineSpec });
}

function ellipse(slide, x, y, w, h, fill, lineSpec) {
  if (w <= 0 || h <= 0) return null;
  return ctx.addShape(slide, { geometry: "ellipse", x, y, w, h, fill, line: lineSpec });
}

function text(slide, value, x, y, w, h, opts = {}) {
  return ctx.addText(slide, {
    text: compactText(value, opts.max ?? 140),
    x,
    y,
    w,
    h,
    ...opts,
  });
}

function flattenSockets(record) {
  const strategy = record.text_socket_strategy;
  const sockets = [];
  sockets.push({ socket_key: "headline_socket", ...strategy.headline_socket });
  for (const socket of strategy.proof_label_sockets ?? []) sockets.push({ socket_key: "proof_label_sockets", ...socket });
  sockets.push({ socket_key: "supporting_copy_socket", ...strategy.supporting_copy_socket });
  for (const socket of strategy.callout_sockets ?? []) sockets.push({ socket_key: "callout_sockets", ...socket });
  sockets.push({ socket_key: "viewer_note_socket", ...strategy.viewer_note_socket });
  return sockets;
}

function socketCopy(socket, fallback = "") {
  return socket?.text_source?.copy_preview || fallback || socket?.socket_id || "";
}

function indexByRole(records) {
  return new Map((records ?? []).map((record) => [record.role ?? record.page_type, record]));
}

function componentIds(scene) {
  return Object.values(scene.semantic_components ?? {}).map((component) => component.component_id).filter(Boolean);
}

function knownBindingIds(scene, adapter) {
  const manifest = adapter.renderer_adapter_manifest ?? {};
  return new Set([
    scene.expansion_id,
    adapter.adapter_scene_id,
    ...componentIds(scene),
    ...(scene.visual_containers ?? []).flatMap((container) => [container.container_id, container.bound_component_id].filter(Boolean)),
    ...(scene.expanded_renderer_action_bindings ?? []).map((binding) => binding.binding_id).filter(Boolean),
    ...(manifest.semantic_component_ids ?? []),
    ...(manifest.visual_container_ids ?? []),
    ...(manifest.expanded_renderer_binding_ids ?? []),
  ]);
}

function slugText(value) {
  return String(value ?? "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 72);
}

function loadInputs() {
  const data = {
    sourceJVisualQualityEvaluation: readJson(RUN2_77_INPUTS.sourceJVisualQualityEvaluation),
    run275RendererRepair: readJson(RUN2_77_INPUTS.run275RendererRepair),
    scenePlanExpansion: readJson(RUN2_77_INPUTS.scenePlanExpansion),
    rendererInputValidation: readJson(RUN2_77_INPUTS.rendererInputValidation),
    visualGrammarModules: readJson(RUN2_77_INPUTS.visualGrammarModules),
    rendererAdapterContracts: readJson(RUN2_77_INPUTS.rendererAdapterContracts),
    textBindingStrategy: readJson(RUN2_77_INPUTS.textBindingStrategy),
    k1RepairPlan: readJson(RUN2_77_INPUTS.k1RepairPlan),
  };
  if (data.rendererInputValidation.status !== "run2_73_renderer_input_validation_passed_public_blocked") {
    throw new Error("Run 2.77 renderer repair requires the passed Run 2.73 renderer input validation");
  }
  if (data.textBindingStrategy.status !== "run2_73_text_binding_strategy_ready_public_blocked") {
    throw new Error("Run 2.77 renderer repair requires the Run 2.73 text binding strategy");
  }
  if (data.sourceJVisualQualityEvaluation.status !== "run2_76_visual_quality_evaluation_public_blocked") {
    throw new Error("Run 2.77 renderer repair requires the Run 2.76/Part J visual quality evaluation");
  }
  if (data.run275RendererRepair.status !== "run2_75_renderer_repair_rerun_generated_public_blocked") {
    throw new Error("Run 2.77 renderer repair requires the Run 2.75 renderer repair rerun result");
  }
  if (data.k1RepairPlan.status !== "run2_76_visual_grammar_renderer_repair_plan_ready_public_blocked") {
    throw new Error("Run 2.77 renderer repair requires the K1 visual grammar renderer repair plan");
  }
  if (data.k1RepairPlan.next_required_action !== "part_k2_renderer_rerun_from_visual_grammar_renderer_repair_plan") {
    throw new Error("Run 2.77 renderer repair requires K1 to request the K2 renderer rerun");
  }
  return data;
}

function buildRenderModel(data) {
  const sceneByRole = indexByRole(data.scenePlanExpansion.scene_structures);
  const validationByRole = indexByRole(data.rendererInputValidation.scene_validation_results);
  const grammarByRole = indexByRole(data.visualGrammarModules.page_type_to_visual_grammar);
  const adapterByRole = indexByRole(data.rendererAdapterContracts.adapter_scene_records);
  const textByRole = indexByRole(data.textBindingStrategy.page_text_binding_records);
  const jByRole = indexByRole(data.sourceJVisualQualityEvaluation.role_assessments);
  const run275ByRole = indexByRole(data.run275RendererRepair.rendered_pages);
  const k1ByRole = indexByRole(data.k1RepairPlan.page_repair_plans);

  return ROLES.map((role, index) => {
    const scene = sceneByRole.get(role);
    const validation = validationByRole.get(role);
    const grammar = grammarByRole.get(role);
    const adapter = adapterByRole.get(role);
    const textBinding = textByRole.get(role);
    const jAssessment = jByRole.get(role);
    const run275Page = run275ByRole.get(role);
    const k1Repair = k1ByRole.get(role);
    if (!scene || !validation || !grammar || !adapter || !textBinding || !jAssessment || !run275Page || !k1Repair) {
      throw new Error(`Run 2.77 missing renderer input record for role: ${role}`);
    }
    const module = adapter.visual_grammar_binding?.module_id ?? grammar.primary_visual_grammar_module;
    if (module !== MODULE_BY_ROLE[role]) throw new Error(`Run 2.77 module mismatch for ${role}: ${module}`);
    if (validation.status !== "pass") throw new Error(`Run 2.77 D3 validation not pass for ${role}`);

    const known = knownBindingIds(scene, adapter);
    const sockets = flattenSockets(textBinding).map((socket) => {
      if (!BOUND_VISUAL_OBJECT_TYPES.has(socket.bound_visual_object_type)) {
        throw new Error(`Run 2.77 socket has invalid visual object type: ${socket.bound_visual_object_type}`);
      }
      if (!known.has(socket.bound_source_id)) {
        throw new Error(`Run 2.77 socket ${socket.socket_id} references unknown D2/E2 id: ${socket.bound_source_id}`);
      }
      return {
        socket_id: socket.socket_id,
        socket_key: socket.socket_key,
        binding_role: socket.binding_role,
        bound_visual_object_type: socket.bound_visual_object_type,
        bound_source_id: socket.bound_source_id,
        bound_source_artifact: socket.bound_source_artifact,
        capacity: socket.capacity,
        canvas_copy: socketCopy(socket),
      };
    });
    const headline = sockets.find((socket) => socket.socket_key === "headline_socket");
    const supporting = sockets.find((socket) => socket.socket_key === "supporting_copy_socket");
    const viewerNote = sockets.find((socket) => socket.socket_key === "viewer_note_socket");
    const proofLabels = sockets.filter((socket) => socket.socket_key === "proof_label_sockets");
    const callouts = sockets.filter((socket) => socket.socket_key === "callout_sockets");
    const canvasProofLabels = proofLabels.slice(0, 2).map((socket) => socket.canvas_copy).filter(Boolean);
    const canvasCallouts = callouts.slice(0, 2).map((socket) => socket.canvas_copy).filter(Boolean);
    const visualContainers = sockets.slice(0, 5).map((socket, socketIndex) => ({
      container_id: `${role}_${socket.bound_visual_object_type.replaceAll(" ", "_")}_${socketIndex + 1}`,
      source_container_or_component_id: socket.bound_source_id,
      visual_object_type: socket.bound_visual_object_type,
      bound_text_socket_ids: [socket.socket_id],
      empty: false,
    }));
    const rendererCapabilities = RENDERER_CAPABILITIES_BY_ROLE[role] ?? [];
    return {
      role,
      slide_index: index + 1,
      visual_grammar_module: module,
      module_variant: adapter.visual_grammar_binding?.module_variant ?? grammar.module_variant ?? "",
      main_structure: adapter.visual_grammar_binding?.main_structure ?? grammar.main_structure ?? {},
      draw_order: adapter.visual_grammar_binding?.draw_order ?? grammar.draw_order ?? [],
      layout_signature: `${textBinding.layout_signature}_k2_${role}`,
      visual_density_profile: `${role}_k2_${slugText(k1Repair.target_scene_direction)}`,
      source_expansion_id: scene.expansion_id,
      source_adapter_scene_id: adapter.adapter_scene_id,
      source_text_binding_id: textBinding.text_binding_id,
      source_validation_id: validation.validation_id,
      target_scene_direction: k1Repair.target_scene_direction,
      source_k1_repair_plan: {
        current_failure: k1Repair.current_failure,
        target_scene_direction: k1Repair.target_scene_direction,
        visual_grammar_change: k1Repair.visual_grammar_change,
        renderer_change: k1Repair.renderer_change,
        text_binding_adjustment: k1Repair.text_binding_adjustment,
        must_preserve_from_2_75: k1Repair.must_preserve_from_2_75,
        must_remove_from_2_75: k1Repair.must_remove_from_2_75,
        source_j_assessment: {
          root_cause_layer: jAssessment.root_cause_layer,
          repair_instruction: jAssessment.repair_instruction,
          engineering_report_risk: jAssessment.engineering_report_risk,
          public_video_direction: jAssessment.public_video_direction,
        },
        source_run2_75_page: {
          visual_density_profile: run275Page.visual_density_profile,
          layout_signature: run275Page.layout_signature,
        },
      },
      renderer_repair_directives_applied: REPAIR_FLAGS,
      renderer_capabilities_applied: rendererCapabilities,
      forbidden_renderer_fallbacks_absent: FORBIDDEN_RENDERER_FALLBACKS,
      label_count: canvasProofLabels.length + canvasCallouts.length,
      text_sockets_used: REQUIRED_SOCKET_KEYS,
      text_socket_bindings: sockets,
      visual_containers: visualContainers,
      headline: headline?.canvas_copy ?? "",
      supporting_copy: supporting?.canvas_copy ?? "",
      proof_labels: canvasProofLabels,
      callouts: canvasCallouts,
      viewer_note: viewerNote?.canvas_copy ?? "",
      overflow_policy: textBinding.overflow_policy,
      source_trace_terms_visible_on_canvas: [],
      forbidden_text_patterns_absent: FORBIDDEN_TEXT_PATTERNS,
      k1_acceptance_checks: k1Repair.acceptance_checks,
      canvas_word_count: [headline?.canvas_copy, supporting?.canvas_copy, ...canvasProofLabels, ...canvasCallouts]
        .filter(Boolean)
        .reduce((sum, value) => sum + wordsIn(value), 0),
    };
  });
}

function drawBase(slide, page, arm) {
  rect(slide, 0, 0, W, H, { color: arm.palette.bg }, line(arm.palette.bg, 0));
  text(slide, `RUN ${RUN_ID} / ${arm.mode === "full" ? "RENDERER REPAIR" : arm.label.toUpperCase()}`, 54, 34, 560, 20, {
    fontSize: 8,
    bold: true,
    color: arm.palette.muted,
    mono: true,
  });
  text(slide, `${String(page.slide_index).padStart(2, "0")} / ${page.role}`, 1160, 34, 70, 20, {
    fontSize: 8,
    bold: true,
    color: arm.palette.muted,
    align: "right",
    mono: true,
  });
}

function textSocket(slide, value, box, opts = {}) {
  text(slide, value, box.x, box.y, box.w, box.h, {
    fontSize: opts.fontSize ?? 18,
    bold: opts.bold,
    title: opts.title,
    color: opts.color ?? C.ink,
    align: opts.align,
    verticalAlign: opts.verticalAlign,
    max: opts.max,
  });
}

function drawProductSurface(slide, x, y, w, h, accent, variant = 0) {
  rect(slide, x + 16, y + 18, w, h, { color: "#d6d0c4" }, line("#d6d0c4", 0));
  rect(slide, x, y, w, h, { color: C.white }, line("#aeb8c5", 2));
  rect(slide, x + 18, y + 18, w - 36, 38, { color: "#16202b" }, line("#16202b", 0));
  [0, 1, 2].forEach((index) => ellipse(slide, x + 38 + index * 20, y + 32, 8, 8, { color: index === variant % 3 ? accent : "#f8f1e8" }, line(accent, 0)));
  rect(slide, x + 24, y + 78, 70, h - 112, { color: "#eef2f5" }, line("#d5dce3", 1));
  [0, 1, 2, 3].forEach((index) => {
    rect(slide, x + 42, y + 104 + index * 44, 36, 8, { color: index === variant % 4 ? accent : "#c9d2dc" }, line("#c9d2dc", 0));
  });
  const cardW = (w - 150) / 2;
  [0, 1, 2, 3].forEach((index) => {
    const cx = x + 116 + (index % 2) * (cardW + 18);
    const cy = y + 82 + Math.floor(index / 2) * ((h - 130) / 2);
    rect(slide, cx, cy, cardW, 74, { color: index % 2 ? "#f8eee5" : "#eff5fb" }, line("#cad3dc", 1));
    rect(slide, cx + 16, cy + 18, cardW - 32, 8, { color: "#b7c0cb" }, line("#b7c0cb", 0));
    rect(slide, cx + 16, cy + 38, (cardW - 44) * (0.48 + index * 0.1), 10, { color: index % 2 ? C.amber : accent }, line(accent, 0));
  });
  rect(slide, x + 116, y + h - 72, w - 150, 34, { color: "#17202b" }, line("#17202b", 0));
  rect(slide, x + 132, y + h - 58, w - 250, 6, { color: accent }, line(accent, 0));
  return { detailCount: 10, connectorCount: 4 };
}

function drawSlideStrip(slide, x, y, count, accent, selected = 0) {
  for (let index = 0; index < count; index += 1) {
    const sx = x + index * 72;
    rect(slide, sx, y + (index % 2) * 10, 58, 42, { color: index === selected ? "#17202b" : C.white }, line(index === selected ? accent : "#c6ced8", 2));
    rect(slide, sx + 8, y + 10 + (index % 2) * 10, 32, 5, { color: index === selected ? accent : "#c6ced8" }, line("#c6ced8", 0));
    rect(slide, sx + 8, y + 22 + (index % 2) * 10, 42, 5, { color: index === selected ? "#ffffff" : "#d7dde4" }, line("#d7dde4", 0));
  }
}

function drawConnector(slide, x1, y1, x2, y2, color) {
  const midX = x1 + (x2 - x1) * 0.55;
  rect(slide, Math.min(x1, midX), y1 - 1, Math.abs(midX - x1), 2, { color }, line(color, 0));
  rect(slide, midX - 1, Math.min(y1, y2), 2, Math.abs(y2 - y1), { color }, line(color, 0));
  rect(slide, Math.min(midX, x2), y2 - 1, Math.abs(x2 - midX), 2, { color }, line(color, 0));
  ellipse(slide, x2 - 6, y2 - 6, 12, 12, { color: C.white }, line(color, 2));
}

function drawRouteDots(slide, points, color) {
  for (const [index, point] of points.entries()) {
    ellipse(slide, point.x - 8, point.y - 8, 16, 16, { color: index === points.length - 1 ? color : C.white }, line(color, 2));
    if (index < points.length - 1) {
      const next = points[index + 1];
      const x = Math.min(point.x, next.x);
      const y = Math.min(point.y, next.y);
      rect(slide, x, y + (next.y - point.y) / 2 - 1, Math.abs(next.x - point.x), 2, { color }, line(color, 0));
    }
  }
}

function drawProductReveal(slide, page, arm) {
  if (page.role === "climax") {
    ellipse(slide, -120, 410, 760, 330, { color: "#e7dfd2" }, line("#e7dfd2", 0));
    ellipse(slide, 640, 10, 760, 650, { color: "#e6edf7" }, line("#e6edf7", 0));
    rect(slide, 210, 112, 880, 494, { color: "#151d27" }, line("#151d27", 0));
    rect(slide, 246, 144, 808, 414, { color: arm.palette.surface }, line("#ffffff", 3));
    drawProductSurface(slide, 292, 180, 700, 332, arm.palette.accent, 5);
    drawSlideStrip(slide, 338, 540, 6, arm.palette.accent, 5);
    drawRouteDots(slide, [{ x: 112, y: 500 }, { x: 260, y: 438 }, { x: 420, y: 320 }, { x: 612, y: 244 }], arm.palette.accent);
    drawConnector(slide, 990, 282, 1116, 220, arm.palette.accent);
    drawConnector(slide, 920, 514, 1088, 560, arm.palette.accent);
    textSocket(slide, page.headline, { x: 76, y: 96, w: 470, h: 104 }, { fontSize: 36, bold: true, title: true, color: arm.palette.title, max: 92 });
    textSocket(slide, page.supporting_copy, { x: 80, y: 210, w: 390, h: 60 }, { fontSize: 14, color: arm.palette.muted, max: 128 });
    page.proof_labels.slice(0, 2).forEach((label, index) => {
      textSocket(slide, label, { x: 1112, y: 196 + index * 330, w: 120, h: 46 }, { fontSize: 11, bold: true, color: arm.palette.title, align: "center", max: 38 });
    });
    page.callouts.slice(0, 2).forEach((label, index) => {
      textSocket(slide, label, { x: 764 + index * 170, y: 616, w: 152, h: 32 }, { fontSize: 12, bold: true, color: arm.palette.title, align: "center", max: 44 });
    });
    return;
  }
  ellipse(slide, -210, 260, 740, 360, { color: "#ece0cc" }, line("#ece0cc", 0));
  ellipse(slide, 600, 70, 780, 520, { color: "#e9eef8" }, line("#e9eef8", 0));
  rect(slide, 332, 118, 650, 438, { color: arm.palette.surface }, line("#bfc6d2", 2));
  rect(slide, 354, 144, 606, 42, { color: "#15202c" }, line("#15202c", 0));
  rect(slide, 382, 218, 244, 230, { color: "#f1f5fa" }, line("#cfd7e0", 1));
  rect(slide, 656, 220, 260, 172, { color: "#f8eee5" }, line("#dfc9b8", 1));
  ellipse(slide, 810, 420, 138, 58, { color: "#ffffff" }, line(arm.palette.accent, 2));
  drawProductSurface(slide, 382, 206, 500, 274, arm.palette.accent, page.slide_index);
  drawSlideStrip(slide, 420, 504, 5, arm.palette.accent, page.slide_index % 5);
  drawConnector(slide, 936, 270, 986, 220, arm.palette.accent);
  drawConnector(slide, 906, 428, 992, 398, arm.palette.accent);
  drawRouteDots(slide, [{ x: 118, y: 408 }, { x: 238, y: 360 }, { x: 354, y: 304 }, { x: 505, y: 238 }], arm.palette.accent);
  textSocket(slide, page.headline, { x: 74, y: 114, w: 450, h: 98 }, { fontSize: 35, bold: true, title: true, color: arm.palette.title, max: 92 });
  textSocket(slide, page.supporting_copy, { x: 78, y: 224, w: 430, h: 58 }, { fontSize: 14, color: arm.palette.muted, max: 132 });
  page.proof_labels.slice(0, 4).forEach((label, index) => {
    const positions = [
      [336, 572, 150],
      [518, 572, 132],
      [678, 572, 126],
      [830, 572, 118],
    ][index];
    textSocket(slide, label, { x: positions[0], y: positions[1], w: positions[2], h: 22 }, { fontSize: 10, bold: true, color: arm.palette.title, align: "center", max: 34 });
  });
  page.callouts.slice(0, 2).forEach((label, index) => {
    textSocket(slide, label, { x: index ? 994 : 974, y: index ? 284 : 200, w: 190, h: 46 }, { fontSize: 12, bold: true, color: arm.palette.title, max: 58 });
  });
}

function drawHeroField(slide, page, arm) {
  ellipse(slide, 56, 376, 920, 230, { color: "#e4eef3" }, line("#d7e1e6", 1));
  ellipse(slide, 244, 284, 750, 184, { color: "#dbe9df" }, line("#c5dacd", 1));
  ellipse(slide, 468, 220, 600, 150, { color: "#f6e8db" }, line("#e2cdbb", 1));
  drawRouteDots(slide, [{ x: 135, y: 520 }, { x: 322, y: 450 }, { x: 526, y: 362 }, { x: 762, y: 290 }, { x: 994, y: 236 }], arm.palette.accent);
  rect(slide, 780, 180, 300, 216, { color: arm.palette.surface }, line("#bac3cf", 2));
  ellipse(slide, 828, 226, 76, 76, { color: "#eaf1fb" }, line(arm.palette.accent, 2));
  drawProductSurface(slide, 762, 168, 358, 252, arm.palette.accent, 2);
  drawSlideStrip(slide, 710, 464, 4, arm.palette.accent, 1);
  drawConnector(slide, 642, 360, 778, 280, arm.palette.accent);
  drawConnector(slide, 972, 420, 1088, 454, arm.palette.accent);
  textSocket(slide, page.headline, { x: 84, y: 112, w: 520, h: 90 }, { fontSize: 34, bold: true, title: true, color: arm.palette.title, max: 94 });
  textSocket(slide, page.supporting_copy, { x: 88, y: 214, w: 450, h: 58 }, { fontSize: 14, color: arm.palette.muted, max: 128 });
  page.proof_labels.slice(0, 3).forEach((label, index) => {
    textSocket(slide, label, { x: 160 + index * 220, y: 588 - index * 34, w: 170, h: 22 }, { fontSize: 10, bold: true, color: arm.palette.title, align: "center", max: 36 });
  });
  page.callouts.slice(0, 2).forEach((label, index) => {
    textSocket(slide, label, { x: 880, y: 422 + index * 56, w: 260, h: 34 }, { fontSize: 12, bold: true, color: arm.palette.title, max: 68 });
  });
}

function drawBeforeAfterTheater(slide, page, arm) {
  rect(slide, 0, 0, 620, H, { color: "#eee7dc" }, line("#eee7dc", 0));
  rect(slide, 620, 0, 660, H, { color: "#edf3f6" }, line("#edf3f6", 0));
  ellipse(slide, 510, -120, 240, 960, { color: "#ffffff" }, line("#ffffff", 0));
  ellipse(slide, 566, -80, 128, 860, { color: "#f4d9ce" }, line(arm.palette.accent, 2));
  rect(slide, 116, 292, 360, 210, { color: "#f8f1e7" }, line("#d9caba", 1));
  rect(slide, 792, 204, 330, 282, { color: "#ffffff" }, line("#b9c7d5", 2));
  ellipse(slide, 778, 450, 212, 72, { color: "#ffffff" }, line(arm.palette.accent, 2));
  drawProductSurface(slide, 128, 278, 360, 222, "#8a7652", 0);
  drawProductSurface(slide, 756, 192, 398, 304, arm.palette.accent, 3);
  drawSlideStrip(slide, 172, 524, 4, "#8a7652", 0);
  drawSlideStrip(slide, 792, 522, 4, arm.palette.accent, 3);
  drawConnector(slide, 548, 322, 742, 282, arm.palette.accent);
  drawConnector(slide, 548, 438, 760, 438, arm.palette.accent);
  textSocket(slide, page.headline, { x: 92, y: 106, w: 470, h: 90 }, { fontSize: 33, bold: true, title: true, color: arm.palette.title, max: 94 });
  textSocket(slide, page.supporting_copy, { x: 724, y: 102, w: 420, h: 62 }, { fontSize: 14, color: arm.palette.muted, max: 132 });
  page.proof_labels.slice(0, 3).forEach((label, index) => {
    textSocket(slide, label, { x: 548, y: 238 + index * 82, w: 158, h: 22 }, { fontSize: 10, bold: true, color: arm.palette.title, align: "center", max: 36 });
  });
  page.callouts.slice(0, 2).forEach((label, index) => {
    textSocket(slide, label, { x: 772, y: 520 + index * 40, w: 300, h: 30 }, { fontSize: 12, bold: true, color: arm.palette.title, max: 70 });
  });
}

function drawEvidenceWorkspace(slide, page, arm) {
  ellipse(slide, 78, 158, 1030, 420, { color: "#edf0ec" }, line("#d7ded8", 1));
  rect(slide, 154, 170, 74, 382, { color: "#17202b" }, line("#17202b", 0));
  [0, 1, 2, 3].forEach((index) => {
    ellipse(slide, 182, 208 + index * 82, 18, 18, { color: index === 3 ? arm.palette.accent : C.white }, line(arm.palette.accent, 2));
    rect(slide, 230, 214 + index * 82, 650 - index * 84, 2, { color: index % 2 ? C.green : C.blue }, line(C.blue, 0));
  });
  rect(slide, 336, 176, 610, 306, { color: arm.palette.surface }, line("#c3cbd3", 2));
  ellipse(slide, 874, 420, 222, 78, { color: "#fff9ee" }, line(arm.palette.accent, 2));
  drawProductSurface(slide, 356, 192, 520, 258, arm.palette.accent, 4);
  drawSlideStrip(slide, 410, 502, 5, arm.palette.accent, 4);
  [0, 1, 2].forEach((index) => {
    rect(slide, 946, 194 + index * 68, 132, 44, { color: index % 2 ? "#f8eee5" : "#eef5fb" }, line("#cad3dc", 1));
    rect(slide, 964, 212 + index * 68, 82, 6, { color: index % 2 ? C.amber : C.blue }, line(C.blue, 0));
  });
  drawConnector(slide, 228, 464, 356, 384, arm.palette.accent);
  drawConnector(slide, 874, 320, 1008, 282, arm.palette.accent);
  textSocket(slide, page.headline, { x: 82, y: 92, w: 610, h: 74 }, { fontSize: 31, bold: true, title: true, color: arm.palette.title, max: 98 });
  textSocket(slide, page.supporting_copy, { x: 782, y: 92, w: 360, h: 64 }, { fontSize: 13, color: arm.palette.muted, max: 128 });
  page.proof_labels.slice(0, 4).forEach((label, index) => {
    textSocket(slide, label, { x: 246, y: 194 + index * 82, w: 190, h: 24 }, { fontSize: 10, bold: true, color: arm.palette.title, max: 38 });
  });
  page.callouts.slice(0, 2).forEach((label, index) => {
    textSocket(slide, label, { x: 862, y: 516 + index * 38, w: 258, h: 28 }, { fontSize: 12, bold: true, color: arm.palette.title, align: "center", max: 60 });
  });
}

function drawDecisionMap(slide, page, arm) {
  ellipse(slide, 130, 118, 918, 460, { color: "#ecece2" }, line("#d9d7ca", 1));
  const nodes = [
    { x: 210, y: 412, label: page.proof_labels[0] || "input" },
    { x: 410, y: 292, label: page.proof_labels[1] || "proof" },
    { x: 654, y: 360, label: page.proof_labels[2] || "review" },
    { x: 906, y: 236, label: page.proof_labels[3] || "release" },
  ];
  drawProductSurface(slide, 700, 288, 330, 184, arm.palette.accent, 5);
  drawSlideStrip(slide, 190, 520, 5, arm.palette.accent, 4);
  drawRouteDots(slide, nodes.map((node) => ({ x: node.x, y: node.y })), arm.palette.accent);
  nodes.forEach((node, index) => {
    ellipse(slide, node.x - 44, node.y - 34, 88, 68, { color: index === nodes.length - 1 ? "#15202c" : C.white }, line(arm.palette.accent, 2));
    textSocket(slide, node.label, { x: node.x - 58, y: node.y - 9, w: 116, h: 18 }, { fontSize: 9, bold: true, color: index === nodes.length - 1 ? C.white : arm.palette.title, align: "center", max: 30 });
  });
  textSocket(slide, page.headline, { x: 84, y: 94, w: 560, h: 82 }, { fontSize: 32, bold: true, title: true, color: arm.palette.title, max: 96 });
  textSocket(slide, page.supporting_copy, { x: 710, y: 96, w: 372, h: 62 }, { fontSize: 14, color: arm.palette.muted, max: 128 });
  page.callouts.slice(0, 2).forEach((label, index) => {
    textSocket(slide, label, { x: 706, y: 500 + index * 42, w: 320, h: 30 }, { fontSize: 12, bold: true, color: arm.palette.title, max: 70 });
  });
}

function drawFullSlide(slide, page, arm) {
  drawBase(slide, page, arm);
  if (page.visual_grammar_module === "hero_field") drawHeroField(slide, page, arm);
  else if (page.visual_grammar_module === "before_after_theater") drawBeforeAfterTheater(slide, page, arm);
  else if (page.visual_grammar_module === "evidence_workspace") drawEvidenceWorkspace(slide, page, arm);
  else if (page.visual_grammar_module === "decision_map") drawDecisionMap(slide, page, arm);
  else drawProductReveal(slide, page, arm);
  textSocket(slide, page.visual_grammar_module.replaceAll("_", " "), { x: 54, y: 664, w: 240, h: 18 }, { fontSize: 8, bold: true, color: arm.palette.muted, mono: true });
}

function drawControlSlide(slide, page, arm) {
  drawBase(slide, page, arm);
  ellipse(slide, 150, 180, 820, 360, { color: arm.mode === "negative" ? "#e4d8c4" : "#e8edf0" }, line("#cdd3d8", 1));
  rect(slide, 730, 210, 320, 240, { color: arm.palette.surface }, line("#c6cbd0", 1));
  drawRouteDots(slide, [{ x: 230, y: 450 }, { x: 420, y: 368 }, { x: 690, y: 330 }, { x: 900, y: 292 }], arm.palette.accent);
  const title = arm.mode === "negative"
    ? `${page.role}: K1 repair plan withheld`
    : arm.mode === "baseline"
      ? `${page.role}: prior workflow baseline`
      : `${page.role}: brief-only prompt output`;
  textSocket(slide, title, { x: 96, y: 110, w: 520, h: 86 }, { fontSize: 30, bold: true, title: true, color: arm.palette.title, max: 86 });
  textSocket(slide, "This comparison arm is generated locally for viewer context. The Part K2 manifest validates the full arm only.", { x: 100, y: 218, w: 430, h: 58 }, { fontSize: 13, color: arm.palette.muted, max: 128 });
  page.proof_labels.slice(0, 3).forEach((label, index) => {
    textSocket(slide, label, { x: 190 + index * 210, y: 548 - index * 36, w: 154, h: 20 }, { fontSize: 10, bold: true, color: arm.palette.title, align: "center", max: 34 });
  });
}

function renderSlide(presentation, page, arm) {
  const slide = presentation.slides.add();
  if (arm.mode === "full") drawFullSlide(slide, page, arm);
  else drawControlSlide(slide, page, arm);
  return slide;
}

function traceForArm(arm, pages) {
  return {
    schema_version: 1,
    run_id: RUN_ID,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    release_decision: arm.release,
    consumed_sources: arm.mode === "full" ? CONSUMED_SOURCES : [`${pack}/commercial_case.md`],
    part_k2_renderer_scope: arm.mode === "full" ? "visual_grammar_renderer_repair_consumes_j_2_75_a_f_d3_and_k1_repair_plan" : "comparison_arm_not_part_k2_quality_manifest",
    public_release_started: false,
    slides: pages.map((page) => ({
      role: page.role,
      slide_index: page.slide_index,
      visual_grammar_module: arm.mode === "full" ? page.visual_grammar_module : "comparison_context",
      layout_signature: arm.mode === "full" ? page.layout_signature : `${page.role}_${arm.mode}_comparison_layout`,
      source_text_binding_id: arm.mode === "full" ? page.source_text_binding_id : "",
      text_socket_binding_count: arm.mode === "full" ? page.text_socket_bindings.length : 0,
      visual_container_count: arm.mode === "full" ? page.visual_containers.length : 0,
      empty_visual_container_count: 0,
      floating_text_without_bound_visual_object_count: 0,
      source_trace_terms_visible_on_canvas: [],
    })),
  };
}

function buildNamedContactSheet(out, title, previewPaths, cols = 3, labels = null) {
  const args = [path.join(root, "scripts", "build_ppt_contact_sheet.py"), "--out", out, "--title", title, "--cols", String(cols)];
  if (labels) args.push("--labels", ...labels, "--");
  args.push(...previewPaths);
  execFileSync("python3.11", args, { cwd: root, stdio: "pipe" });
  return out;
}

function buildContactSheet(workspace, arm, previewPaths) {
  return buildNamedContactSheet(path.join(workspace, "preview", "contact-sheet.png"), arm.label, previewPaths);
}

function buildRun273Sheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built.filter((item) => fs.existsSync(item.contactSheet)).map((item) => {
    const arm = armSpecs.find((spec) => item.workspace.endsWith(spec.slug));
    return arm?.label ?? path.basename(item.workspace);
  });
  return buildNamedContactSheet(path.join(outRoot, "run2-77-four-arm-contact-sheet.png"), "Run 2.77 visual grammar renderer repair comparison", sheets, sheets.length, labels);
}

async function buildArm(arm, pages) {
  const workspace = path.join(outRoot, arm.slug);
  resetWorkspace(workspace);
  fs.copyFileSync(__filename, path.join(workspace, "slides", "deck-source.mjs"));
  fs.writeFileSync(
    path.join(workspace, "profile-plan.txt"),
    [
      "task mode: create",
      "primary deck-profile: product-platform",
      `arm: ${arm.armId}`,
      `part: Part K2 / Run ${RUN_ID}`,
      `consumed sources: ${arm.mode === "full" ? CONSUMED_SOURCES.join(", ") : "commercial_case.md only"}`,
      "full arm requirement: apply K1 visual grammar and renderer repair plan while preserving A-F source bindings",
      "release boundary: public blocked until Part L visual evaluation",
      "",
    ].join("\n"),
  );
  const presentation = Presentation.create(undefined, { slideSize: { width: W, height: H } });
  const slides = pages.map((page) => renderSlide(presentation, page, arm));
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
  const trace = traceForArm(arm, pages);
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
      source: "scripts/generate_ppt_run2_77_visual_grammar_renderer_repair_arms.mjs",
      exportName: `slide${String(index + 1).padStart(2, "0")}`,
    })),
  };
  writeJson(path.join(workspace, "output", "artifact-build-manifest.json"), manifest);
  writeJson(path.join(workspace, "qa", "build_manifest_stdout.json"), manifest);
  writeJson(path.join(workspace, "trace_manifest.json"), trace);
  return { arm, workspace, outputPath, contactSheet, previewPaths };
}

function htmlEscape(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function svgFor(page) {
  if (page.visual_grammar_module === "hero_field") {
    return `<svg viewBox="0 0 1280 720" aria-hidden="true"><path d="M35 548 C250 420 322 520 520 345 C706 180 902 260 1218 105 L1248 286 C990 352 840 345 666 500 C470 676 250 652 35 548Z" fill="#dfece8"/><path d="M92 540 C310 446 462 430 622 320 C770 220 936 220 1124 158" fill="none" stroke="#df563f" stroke-width="7" stroke-linecap="round"/><circle cx="302" cy="448" r="16" fill="#fff" stroke="#df563f" stroke-width="4"/><circle cx="622" cy="320" r="16" fill="#fff" stroke="#df563f" stroke-width="4"/><rect x="798" y="180" width="276" height="198" rx="0" fill="#fffdf8" stroke="#bac3cf" stroke-width="4"/></svg>`;
  }
  if (page.visual_grammar_module === "before_after_theater") {
    return `<svg viewBox="0 0 1280 720" aria-hidden="true"><rect width="610" height="720" fill="#eee7dc"/><rect x="610" width="670" height="720" fill="#edf3f6"/><path d="M592 -80 C548 120 690 245 616 420 C570 530 650 660 600 790" fill="none" stroke="#df563f" stroke-width="72" stroke-linecap="round" opacity=".55"/><rect x="116" y="286" width="360" height="214" fill="#f8f1e7" stroke="#d9caba"/><rect x="792" y="204" width="330" height="282" fill="#fff" stroke="#b9c7d5" stroke-width="4"/></svg>`;
  }
  if (page.visual_grammar_module === "evidence_workspace") {
    return `<svg viewBox="0 0 1280 720" aria-hidden="true"><ellipse cx="590" cy="366" rx="530" ry="220" fill="#edf0ec" stroke="#d7ded8"/><rect x="154" y="170" width="74" height="382" fill="#17202b"/><rect x="336" y="176" width="610" height="306" fill="#fffdf8" stroke="#c3cbd3" stroke-width="4"/><g stroke="#2d62d6" stroke-width="4"><path d="M195 218 H870"/><path d="M195 300 H780"/><path d="M195 382 H704"/><path d="M195 464 H628"/></g><g fill="#fff" stroke="#df563f" stroke-width="4"><circle cx="191" cy="218" r="13"/><circle cx="191" cy="300" r="13"/><circle cx="191" cy="382" r="13"/><circle cx="191" cy="464" r="13"/></g></svg>`;
  }
  if (page.visual_grammar_module === "decision_map") {
    return `<svg viewBox="0 0 1280 720" aria-hidden="true"><ellipse cx="590" cy="350" rx="468" ry="238" fill="#ecece2" stroke="#d9d7ca"/><path d="M210 412 C350 270 480 286 654 360 C760 404 798 268 906 236" fill="none" stroke="#df563f" stroke-width="7" stroke-linecap="round"/><g fill="#fff" stroke="#df563f" stroke-width="4"><circle cx="210" cy="412" r="42"/><circle cx="410" cy="292" r="42"/><circle cx="654" cy="360" r="42"/><circle cx="906" cy="236" r="42"/></g></svg>`;
  }
  if (page.role === "climax") {
    return `<svg viewBox="0 0 1280 720" aria-hidden="true"><ellipse cx="260" cy="575" rx="410" ry="180" fill="#e7dfd2"/><ellipse cx="990" cy="330" rx="440" ry="330" fill="#e6edf7"/><rect x="210" y="112" width="880" height="494" fill="#151d27"/><rect x="246" y="144" width="808" height="414" fill="#fffdf8" stroke="#fff" stroke-width="5"/><rect x="292" y="180" width="700" height="332" fill="#f1f5fa" stroke="#bfc6d2" stroke-width="4"/><path d="M112 500 C260 438 420 320 612 244" fill="none" stroke="#df563f" stroke-width="7" stroke-linecap="round"/><path d="M990 282 C1048 258 1072 232 1116 220" fill="none" stroke="#df563f" stroke-width="5" stroke-linecap="round"/></svg>`;
  }
  return `<svg viewBox="0 0 1280 720" aria-hidden="true"><ellipse cx="150" cy="438" rx="390" ry="190" fill="#ece0cc"/><ellipse cx="910" cy="330" rx="420" ry="270" fill="#e9eef8"/><path d="M335 120 L984 78 L946 556 L284 586 Z" fill="#fffdf8" stroke="#bfc6d2" stroke-width="5"/><rect x="360" y="148" width="586" height="42" fill="#15202c"/><path d="M118 408 C238 360 354 304 505 238" fill="none" stroke="#df563f" stroke-width="7" stroke-linecap="round"/><g fill="#fff" stroke="#df563f" stroke-width="4"><circle cx="118" cy="408" r="15"/><circle cx="238" cy="360" r="15"/><circle cx="354" cy="304" r="15"/><circle cx="505" cy="238" r="15"/></g></svg>`;
}

function buildStandaloneHtml(pages, outPath) {
  const sections = pages.map((page) => {
    const labels = page.proof_labels.slice(0, 4).map((label) => `<span>${htmlEscape(label)}</span>`).join("");
    const callouts = page.callouts.slice(0, 2).map((label) => `<b>${htmlEscape(label)}</b>`).join("");
    return `<section class="slide ${page.visual_grammar_module}" data-role="${htmlEscape(page.role)}">
      ${svgFor(page)}
      <div class="copy">
        <h2>${htmlEscape(page.headline)}</h2>
        <p>${htmlEscape(page.supporting_copy)}</p>
      </div>
      <div class="labels">${labels}</div>
      <div class="callouts">${callouts}</div>
      <footer>${htmlEscape(page.visual_grammar_module.replaceAll("_", " "))}</footer>
    </section>`;
  }).join("\n");
  const html = `<!doctype html>
<html lang="en" data-run-id="2.77">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Run 2.77 Visual Grammar Renderer Repair</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #161b22; color: #11151c; font-family: Inter, Aptos, system-ui, sans-serif; }
    .deck { display: grid; gap: 28px; padding: 28px; }
    .slide { position: relative; width: min(1280px, calc(100vw - 56px)); aspect-ratio: 16 / 9; overflow: hidden; background: #f5efe4; box-shadow: 0 18px 60px rgba(0,0,0,.35); }
    .slide svg { position: absolute; inset: 0; width: 100%; height: 100%; }
    .copy { position: absolute; left: 6.4%; top: 13%; width: 42%; }
    .copy h2 { margin: 0; font-size: clamp(28px, 3.1vw, 48px); line-height: 1.02; letter-spacing: 0; }
    .copy p { margin: 16px 0 0; color: #69727e; font-size: clamp(13px, 1.25vw, 18px); line-height: 1.35; }
    .labels { position: absolute; left: 24%; right: 16%; bottom: 15%; display: flex; gap: 14px; flex-wrap: wrap; align-items: center; }
    .labels span { display: inline-flex; align-items: center; min-height: 26px; padding: 0 12px; border: 1px solid #d7cfc0; background: #fffdf8; border-radius: 999px; font-size: 12px; font-weight: 700; }
    .callouts { position: absolute; right: 7%; bottom: 20%; width: 26%; display: grid; gap: 12px; }
    .callouts b { font-size: 13px; line-height: 1.2; color: #11151c; }
    footer { position: absolute; left: 54px; bottom: 30px; font-size: 11px; color: #69727e; text-transform: uppercase; font-weight: 800; letter-spacing: 0; }
    .hero_field .copy { top: 15%; width: 45%; }
    .before_after_theater .copy { width: 37%; }
    .before_after_theater .callouts { right: 13%; bottom: 17%; }
    .evidence_workspace .copy { width: 50%; top: 12%; }
    .evidence_workspace .labels { left: 19%; bottom: 22%; display: grid; }
    .decision_map .copy { width: 46%; top: 13%; }
    .decision_map .labels { left: 12%; bottom: 31%; width: 70%; justify-content: space-between; }
    @media (max-width: 760px) { .deck { padding: 12px; gap: 14px; } .slide { width: calc(100vw - 24px); } .copy h2 { font-size: 20px; } .copy p, .callouts b, .labels span { font-size: 9px; } }
  </style>
</head>
<body>
  <main class="deck">
    ${sections}
  </main>
</body>
</html>
`;
  fs.writeFileSync(outPath, html);
}

function writeResult(pages, built, fourArmSheet, standaloneHtml, k1RepairPlan) {
  const full = built.find((item) => item.arm.armId === "run2_77_full_visual_grammar_renderer_repair");
  const viewerPath = path.join(outRoot, "ppt-run-viewer.html");
  const renderedPages = pages.map((page) => ({
    role: page.role,
    slide_index: page.slide_index,
    visual_grammar_module: page.visual_grammar_module,
    module_variant: page.module_variant,
    layout_signature: page.layout_signature,
    visual_density_profile: page.visual_density_profile,
    source_expansion_id: page.source_expansion_id,
    source_adapter_scene_id: page.source_adapter_scene_id,
    source_text_binding_id: page.source_text_binding_id,
    source_validation_id: page.source_validation_id,
    target_scene_direction: page.target_scene_direction,
    source_k1_repair_plan: page.source_k1_repair_plan,
    renderer_repair_directives_applied: page.renderer_repair_directives_applied,
    renderer_capabilities_applied: page.renderer_capabilities_applied,
    forbidden_renderer_fallbacks_absent: page.forbidden_renderer_fallbacks_absent,
    label_count: page.label_count,
    text_sockets_used: page.text_sockets_used,
    text_socket_bindings: page.text_socket_bindings,
    visual_containers: page.visual_containers,
    overflow_policy: page.overflow_policy,
    source_trace_terms_visible_on_canvas: page.source_trace_terms_visible_on_canvas,
    forbidden_text_patterns_absent: page.forbidden_text_patterns_absent,
    canvas_word_count: page.canvas_word_count,
    k1_acceptance_checks: page.k1_acceptance_checks,
  }));
  const capabilityUnion = [...new Set(renderedPages.flatMap((page) => page.renderer_capabilities_applied))].sort();
  const result = {
    artifact_id: "run2_77_visual_grammar_renderer_repair_rerun_result",
    part: "Part K2",
    schema_version: "ppt_run2_77_visual_grammar_renderer_repair_rerun_result.v1",
    run_id: RUN_ID,
    status: "run2_77_visual_grammar_renderer_repair_rerun_generated_public_blocked",
    public_ready: false,
    public_release_started: false,
    quality_claim_boundary: "visual_grammar_renderer_repair_generated_viewer_check_only_no_part_l_quality_verdict",
    consumed_sources: CONSUMED_SOURCES,
    source_k1_repair_plan: {
      status: k1RepairPlan.status,
      top_blocker: k1RepairPlan.source_j_evaluation?.top_blocker,
      primary_layer: k1RepairPlan.source_j_evaluation?.primary_layer_to_fix,
      next_required_action: k1RepairPlan.next_required_action,
      source_result: RUN2_77_INPUTS.k1RepairPlan,
    },
    visual_grammar_renderer_repair_manifest: {
      generator: "scripts/generate_ppt_run2_77_visual_grammar_renderer_repair_arms.mjs",
      consumed_sources: CONSUMED_SOURCES,
      arms: built.map((item) => item.arm.armId),
      best_internal_arm: "run2_77_full_visual_grammar_renderer_repair",
      outputs: {
        html_viewer: repoRelative(standaloneHtml),
        pptx: repoRelative(full.outputPath),
        ppt_run_viewer: repoRelative(viewerPath),
        combined_contact_sheet: repoRelative(fourArmSheet),
        full_contact_sheet: repoRelative(full.contactSheet),
      },
      viewer_update: {
        latest_run_id: RUN_ID,
        viewer_can_reference_new_run: true,
      },
    },
    rendered_pages: renderedPages,
    visual_grammar_renderer_repair_checks: {
      pages_with_k1_repair_plan_consumed: renderedPages.filter((page) => page.renderer_repair_directives_applied.includes("k1_repair_plan_consumed")).length,
      pages_using_expected_visual_grammar: renderedPages.filter((page) => page.visual_grammar_module === MODULE_BY_ROLE[page.role]).length,
      distinct_target_scene_directions: new Set(renderedPages.map((page) => page.target_scene_direction)).size,
      pages_with_forbidden_fallbacks_absent: renderedPages.filter((page) => FORBIDDEN_RENDERER_FALLBACKS.every((fallback) => page.forbidden_renderer_fallbacks_absent.includes(fallback))).length,
      pages_with_reduced_label_count: renderedPages.filter((page) => page.label_count <= 5).length,
      required_renderer_capabilities_covered: capabilityUnion,
      public_quality_verdict_started: false,
    },
    preliminary_viewer_observations: [
      "Generated full arm applies the Part K1 visual grammar and renderer repair plan to the A-F scene model.",
      "Viewer is updated for local inspection, but Part L must still evaluate visual quality.",
    ],
    verification_limitations: [
      "source_trace_terms_visible_on_canvas is renderer-declared metadata in K2; Part L must inspect the viewer/PPT surface before making any visual quality verdict.",
    ],
    release_boundary: "public_blocked_until_part_l_visual_quality_evaluation_and_human_release_approval",
    next_required_action: "part_l_visual_quality_evaluation_for_run2_77",
  };
  writeJson(path.join(root, RESULT_JSON), result);
  fs.writeFileSync(
    path.join(root, RESULT_MD),
    [
      "# Run 2.77 Visual Grammar Renderer Repair Rerun",
      "",
      "Status: generated locally, public blocked.",
      "",
      "Run 2.77 consumes the 2.73 A-F inputs, Part J evaluation, Run 2.75 rerun result, and K1 repair plan before native PPT drawing.",
      "",
      "Best internal arm: `run2_77_full_visual_grammar_renderer_repair`.",
      "",
      "Viewer check: generated output is available for local browser inspection. Part L must still evaluate visual quality.",
      "",
      "Limit: source-trace visibility is renderer-declared metadata in K2; Part L must inspect the viewer/PPT surface before any quality verdict.",
      "",
      "Generated outputs:",
      "",
      `- \`${repoRelative(full.outputPath)}\``,
      `- \`${repoRelative(standaloneHtml)}\``,
      `- \`${repoRelative(viewerPath)}\``,
      `- \`${repoRelative(fourArmSheet)}\``,
      "",
    ].join("\n"),
  );
  return result;
}

async function main() {
  ensureDir(outRoot);
  const inputs = loadInputs();
  const pages = buildRenderModel(inputs);
  const built = [];
  for (const arm of armSpecs) built.push(await buildArm(arm, pages));
  const fourArmSheet = buildRun273Sheet(built);
  const full = built.find((item) => item.arm.armId === "run2_77_full_visual_grammar_renderer_repair");
  const standaloneHtml = path.join(full.workspace, "output", "run2-77-renderer-repair.html");
  buildStandaloneHtml(pages, standaloneHtml);
  writeJson(path.join(outRoot, "run2_77_visual_grammar_renderer_repair_rerun_summary.json"), {
    run_id: "run2_77_visual_grammar_renderer_repair_four_arms",
    arms: built.map((item) => item.arm.armId),
    consumed_sources: CONSUMED_SOURCES,
    combined_contact_sheet: repoRelative(fourArmSheet),
    created: built.map((item) => repoRelative(item.workspace)),
  });
  const result = writeResult(pages, built, fourArmSheet, standaloneHtml, inputs.k1RepairPlan);
  execFileSync("python3.11", [path.join(root, "scripts", "build_ppt_run_html_viewer.py")], { cwd: root, stdio: "pipe" });
  return result;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result.visual_grammar_renderer_repair_manifest, null, 2)}\n`);
}

export {
  CONSUMED_SOURCES,
  MODULE_BY_ROLE,
  RUN2_77_INPUTS,
  armSpecs,
  buildRenderModel,
  main,
};
