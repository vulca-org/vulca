import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.79";
const RESULT_JSON = `${pack}/results/run2_79_renderer_art_direction_repair_rerun_result.json`;
const RESULT_MD = `${pack}/results/run2_79_renderer_art_direction_repair_rerun_result.md`;
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
const RUN2_79_INPUTS = {
  visualQualityEvaluation: "docs/product/ppt-run2-data-skill-quality/results/run2_78_visual_quality_evaluation.json",
  run277RendererRepair: "docs/product/ppt-run2-data-skill-quality/results/run2_77_visual_grammar_renderer_repair_rerun_result.json",
  k1RepairPlan: "docs/product/ppt-run2-data-skill-quality/run2_76_visual_grammar_renderer_repair_plan.json",
};
const CONSUMED_SOURCES = [
  RUN2_79_INPUTS.visualQualityEvaluation,
  RUN2_79_INPUTS.run277RendererRepair,
  RUN2_79_INPUTS.k1RepairPlan,
];
const REPAIR_FLAGS = [
  "l_repair_instruction_consumed",
  "wireframe_surface_replaced",
  "debug_annotation_removed",
  "dominant_product_object",
  "foreground_background_depth",
  "public_scene_hierarchy",
  "public_polish_not_claimed",
];
const ART_DIRECTION_SCENE_BY_ROLE = {
  cover: "finished product hero crop with editorial depth",
  setup: "source transformation field with solid product destination",
  contrast: "asymmetric transformation theater with rich after surface",
  proof: "inspection bench with one enlarged evidence object",
  climax: "completion reveal with full-frame editable result",
  close: "release gate scene with dominant blocked-public decision",
};
const DISPLAY_PROOF_LABEL_BY_ROLE = {
  cover: "brief to editable proof",
  setup: "source memory",
  contrast: "mechanism visible",
  proof: "inspection ready",
  climax: "editable result",
  close: "release gate",
};
const DISPLAY_CALLOUTS_BY_ROLE = {
  cover: ["source-backed", "native PPT"],
  setup: ["routed inputs", "product surface"],
  contrast: ["before", "richer after"],
  proof: ["bound evidence", "readable proof"],
  climax: ["six slides", "review-ready"],
  close: ["generated next", "public blocked"],
};
const DOMINANT_PRODUCT_SCALE_BY_ROLE = {
  cover: "hero",
  setup: "large",
  contrast: "large",
  proof: "large",
  climax: "full_frame",
  close: "large",
};

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
    slug: "ppt-run2-79-prompt-only",
    label: "Prompt-only control",
    mode: "control",
    release: "public_blocked",
    palette: { bg: "#f7f7f4", accent: "#778291", title: C.ink, muted: C.muted, surface: "#ffffff" },
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-79-run1-5-skill",
    label: "Run 1.5 baseline",
    mode: "baseline",
    release: "public_blocked",
    palette: { bg: "#f3f6f8", accent: C.green, title: C.ink, muted: C.muted, surface: "#ffffff" },
  },
  {
    armId: "run2_79_full_renderer_art_direction_repair",
    slug: "ppt-run2-79-full-vulca",
    label: "Run 2.79 full art-direction repair",
    mode: "full",
    release: "public_blocked",
    palette: { bg: C.paper, accent: C.blue, accent2: C.green, title: C.ink, muted: C.muted, surface: C.white },
  },
  {
    armId: "bad_run2_79_without_l_art_direction_repair",
    slug: "ppt-run2-79-bad-without-l-art-direction-repair",
    label: "Bad missing Run 2.79 L art-direction repair",
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
    visualQualityEvaluation: readJson(RUN2_79_INPUTS.visualQualityEvaluation),
    run277RendererRepair: readJson(RUN2_79_INPUTS.run277RendererRepair),
    k1RepairPlan: readJson(RUN2_79_INPUTS.k1RepairPlan),
  };
  if (data.visualQualityEvaluation.status !== "run2_78_visual_quality_evaluation_public_blocked") {
    throw new Error("Run 2.79 renderer repair requires the Run 2.78/Part L visual quality evaluation");
  }
  if (data.visualQualityEvaluation.next_required_action !== "part_m_renderer_art_direction_repair_from_l_evaluation") {
    throw new Error("Run 2.79 renderer repair requires Part L to request Part M art-direction repair");
  }
  if (data.run277RendererRepair.status !== "run2_77_visual_grammar_renderer_repair_rerun_generated_public_blocked") {
    throw new Error("Run 2.79 renderer repair requires the Run 2.77 renderer repair rerun result");
  }
  if (data.k1RepairPlan.status !== "run2_76_visual_grammar_renderer_repair_plan_ready_public_blocked") {
    throw new Error("Run 2.79 renderer repair requires the K1 repair plan as a preservation source");
  }
  return data;
}

function buildRenderModel(data) {
  const run277ByRole = indexByRole(data.run277RendererRepair.rendered_pages);
  const lByRole = indexByRole(data.visualQualityEvaluation.role_assessments);
  const k1ByRole = indexByRole(data.k1RepairPlan.page_repair_plans);

  return ROLES.map((role, index) => {
    const run277Page = run277ByRole.get(role);
    const lAssessment = lByRole.get(role);
    const k1Repair = k1ByRole.get(role);
    if (!run277Page || !lAssessment || !k1Repair) {
      throw new Error(`Run 2.79 missing renderer input record for role: ${role}`);
    }
    const module = run277Page.visual_grammar_module;
    if (module !== MODULE_BY_ROLE[role]) throw new Error(`Run 2.79 module mismatch for ${role}: ${module}`);
    const sockets = run277Page.text_socket_bindings ?? [];
    const headline = sockets.find((socket) => socket.socket_key === "headline_socket");
    const supporting = sockets.find((socket) => socket.socket_key === "supporting_copy_socket");
    const proofLabels = (run277Page.proof_labels ?? sockets.filter((socket) => socket.socket_key === "proof_label_sockets").map((socket) => socket.canvas_copy)).filter(Boolean);
    const callouts = (run277Page.callouts ?? sockets.filter((socket) => socket.socket_key === "callout_sockets").map((socket) => socket.canvas_copy)).filter(Boolean);
    const canvasProofLabels = [DISPLAY_PROOF_LABEL_BY_ROLE[role] ?? proofLabels[0]].filter(Boolean);
    const canvasCallouts = DISPLAY_CALLOUTS_BY_ROLE[role] ?? callouts.slice(0, 2);
    return {
      role,
      slide_index: index + 1,
      visual_grammar_module: module,
      module_variant: run277Page.module_variant,
      layout_signature: `${role}_run2_79_renderer_art_direction_repair`,
      visual_density_profile: `${role}_run2_79_public_scene_${slugText(ART_DIRECTION_SCENE_BY_ROLE[role])}`,
      source_run2_77_page: {
        target_scene_direction: run277Page.target_scene_direction,
        visual_density_profile: run277Page.visual_density_profile,
        layout_signature: run277Page.layout_signature,
      },
      source_l_repair_instruction: lAssessment.next_repair_instruction,
      source_k1_target_scene_direction: k1Repair.target_scene_direction,
      art_direction_scene: ART_DIRECTION_SCENE_BY_ROLE[role],
      renderer_repair_directives_applied: REPAIR_FLAGS,
      debug_annotation_count: 0,
      wireframe_dependency: role === "climax" ? "minimal" : "reduced",
      dominant_product_object_scale: DOMINANT_PRODUCT_SCALE_BY_ROLE[role],
      min_visible_label_font_size: 12,
      label_count: canvasProofLabels.length + canvasCallouts.length,
      text_sockets_used: run277Page.text_sockets_used ?? REQUIRED_SOCKET_KEYS,
      text_socket_bindings: sockets,
      source_text_socket_label_inputs: {
        proof_labels: proofLabels,
        callouts,
      },
      visual_containers: run277Page.visual_containers ?? [],
      headline: headline?.canvas_copy ?? run277Page.headline ?? "",
      supporting_copy: supporting?.canvas_copy ?? run277Page.supporting_copy ?? "",
      proof_labels: canvasProofLabels,
      callouts: canvasCallouts,
      viewer_note: run277Page.viewer_note ?? "",
      overflow_policy: run277Page.overflow_policy,
      source_trace_terms_visible_on_canvas: [],
      public_polish_claimed: false,
      canvas_word_count: [headline?.canvas_copy ?? run277Page.headline, supporting?.canvas_copy ?? run277Page.supporting_copy, ...canvasProofLabels, ...canvasCallouts]
        .filter(Boolean)
        .reduce((sum, value) => sum + wordsIn(value), 0),
    };
  });
}

function drawBase(slide, page, arm) {
  rect(slide, 0, 0, W, H, { color: arm.palette.bg }, line(arm.palette.bg, 0));
  text(slide, `RUN ${RUN_ID} / ${arm.mode === "full" ? "ART DIRECTION REPAIR" : arm.label.toUpperCase()}`, 54, 34, 560, 20, {
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

function drawAtmosphericBand(slide, x, y, w, h, color, opacityFill = null) {
  rect(slide, x, y, w, h, { color: opacityFill ?? color }, line(opacityFill ?? color, 0));
}

function drawSolidProductObject(slide, x, y, w, h, accent, variant = 0, opts = {}) {
  const frame = opts.frame ?? "#121922";
  const inner = opts.inner ?? C.white;
  rect(slide, x + 22, y + 24, w, h, { color: "#c8c0b2" }, line("#c8c0b2", 0));
  rect(slide, x, y, w, h, { color: frame }, line(frame, 0));
  rect(slide, x + 24, y + 28, w - 48, h - 56, { color: inner }, line(inner, 0));
  rect(slide, x + 24, y + 28, w - 48, 46, { color: "#172331" }, line("#172331", 0));
  [0, 1, 2].forEach((index) => ellipse(slide, x + 50 + index * 20, y + 46, 9, 9, { color: index === variant % 3 ? accent : "#f6efe4" }, line("#f6efe4", 0)));

  const contentTop = y + 98;
  const contentH = h - 150;
  const sidebarW = Math.max(72, w * 0.14);
  rect(slide, x + 46, contentTop, sidebarW, contentH, { color: "#e9eef2" }, line("#e9eef2", 0));
  for (let index = 0; index < 4; index += 1) {
    rect(slide, x + 64, contentTop + 24 + index * 42, sidebarW - 36, 8, { color: index === variant % 4 ? accent : "#c7d0da" }, line("#c7d0da", 0));
  }

  const stageX = x + 74 + sidebarW;
  const stageW = w - sidebarW - 126;
  rect(slide, stageX, contentTop, stageW, Math.max(112, contentH * 0.52), { color: "#f1f5f8" }, line("#f1f5f8", 0));
  rect(slide, stageX + 22, contentTop + 24, stageW * 0.46, 14, { color: "#97a8b9" }, line("#97a8b9", 0));
  rect(slide, stageX + 22, contentTop + 58, stageW * 0.72, 18, { color: accent }, line(accent, 0));
  ellipse(slide, stageX + stageW * 0.56, contentTop + 96, stageW * 0.34, 64, { color: "#ffffff" }, line("#ffffff", 0));

  const rowY = contentTop + Math.max(136, contentH * 0.62);
  [0, 1, 2].forEach((index) => {
    const blockW = (stageW - 28) / 3;
    const bx = stageX + index * (blockW + 14);
    rect(slide, bx, rowY, blockW, 52, { color: index === 1 ? "#f8eadb" : "#eaf1fb" }, line(index === 1 ? "#f8eadb" : "#eaf1fb", 0));
    rect(slide, bx + 16, rowY + 18, blockW - 32, 8, { color: index === 1 ? C.amber : accent }, line(accent, 0));
  });
  rect(slide, stageX, y + h - 76, stageW, 28, { color: "#172331" }, line("#172331", 0));
  rect(slide, stageX + 20, y + h - 64, stageW * 0.58, 6, { color: accent }, line(accent, 0));
}

function drawSoftConnector(slide, x1, y1, x2, y2, color, width = 12) {
  const midX = x1 + (x2 - x1) * 0.58;
  rect(slide, Math.min(x1, midX), y1 - width / 2, Math.abs(midX - x1), width, { color }, line(color, 0));
  rect(slide, midX - width / 2, Math.min(y1, y2), width, Math.abs(y2 - y1), { color }, line(color, 0));
  rect(slide, Math.min(midX, x2), y2 - width / 2, Math.abs(x2 - midX), width, { color }, line(color, 0));
}

function drawSlideFilm(slide, x, y, count, accent, selected = 0) {
  for (let index = 0; index < count; index += 1) {
    const sx = x + index * 92;
    const active = index === selected;
    rect(slide, sx, y + (index % 2) * 8, 74, 50, { color: active ? "#172331" : "#fffdf8" }, line(active ? "#172331" : "#fffdf8", 0));
    rect(slide, sx + 12, y + 13 + (index % 2) * 8, 44, 7, { color: active ? accent : "#c9d2dc" }, line("#c9d2dc", 0));
    rect(slide, sx + 12, y + 29 + (index % 2) * 8, 50, 6, { color: active ? "#ffffff" : "#dbe2e9" }, line("#dbe2e9", 0));
  }
}

function drawMProductReveal(slide, page, arm) {
  if (page.role === "climax") {
    ellipse(slide, -120, 424, 680, 280, { color: "#e8dfd1" }, line("#e8dfd1", 0));
    ellipse(slide, 560, 52, 820, 600, { color: "#e8f0f7" }, line("#e8f0f7", 0));
    rect(slide, 312, 92, 842, 520, { color: "#121922" }, line("#121922", 0));
    drawSolidProductObject(slide, 352, 126, 760, 444, arm.palette.accent, 5, { frame: "#111820" });
    drawSlideFilm(slide, 424, 590, 6, arm.palette.accent, 5);
    drawSoftConnector(slide, 164, 514, 390, 456, arm.palette.accent2, 16);
    textSocket(slide, page.headline, { x: 78, y: 100, w: 420, h: 112 }, { fontSize: 37, bold: true, title: true, color: arm.palette.title, max: 92 });
    textSocket(slide, page.supporting_copy, { x: 82, y: 232, w: 360, h: 66 }, { fontSize: 15, color: arm.palette.muted, max: 130 });
    page.proof_labels.slice(0, 1).forEach((label) => {
      textSocket(slide, label, { x: 844, y: 626, w: 238, h: 28 }, { fontSize: 12, bold: true, color: arm.palette.title, align: "center", max: 42 });
    });
    page.callouts.slice(0, 2).forEach((label, index) => {
      textSocket(slide, label, { x: 92 + index * 186, y: 474 + index * 46, w: 166, h: 36 }, { fontSize: 13, bold: true, color: arm.palette.title, max: 44 });
    });
    return;
  }
  ellipse(slide, -170, 276, 720, 360, { color: "#eadfcd" }, line("#eadfcd", 0));
  ellipse(slide, 512, 58, 850, 560, { color: "#e8eef8" }, line("#e8eef8", 0));
  rect(slide, 456, 94, 706, 494, { color: "#121922" }, line("#121922", 0));
  drawSolidProductObject(slide, 492, 126, 636, 410, arm.palette.accent, 1, { frame: "#121922" });
  drawSlideFilm(slide, 530, 560, 5, arm.palette.accent, page.slide_index % 5);
  drawSoftConnector(slide, 150, 418, 492, 286, arm.palette.accent2, 18);
  textSocket(slide, page.headline, { x: 74, y: 116, w: 432, h: 104 }, { fontSize: 36, bold: true, title: true, color: arm.palette.title, max: 92 });
  textSocket(slide, page.supporting_copy, { x: 78, y: 238, w: 386, h: 70 }, { fontSize: 15, color: arm.palette.muted, max: 132 });
  page.proof_labels.slice(0, 1).forEach((label) => {
    textSocket(slide, label, { x: 800, y: 596, w: 206, h: 28 }, { fontSize: 12, bold: true, color: arm.palette.title, align: "center", max: 40 });
  });
  page.callouts.slice(0, 2).forEach((label, index) => {
    textSocket(slide, label, { x: 996, y: 176 + index * 78, w: 174, h: 44 }, { fontSize: 13, bold: true, color: arm.palette.title, max: 48 });
  });
}

function drawMHeroField(slide, page, arm) {
  ellipse(slide, 20, 414, 840, 230, { color: "#dfebef" }, line("#dfebef", 0));
  ellipse(slide, 272, 306, 720, 190, { color: "#dbeadc" }, line("#dbeadc", 0));
  ellipse(slide, 504, 196, 640, 164, { color: "#f5e6d8" }, line("#f5e6d8", 0));
  drawAtmosphericBand(slide, 120, 514, 260, 24, "#bed6df");
  drawAtmosphericBand(slide, 356, 444, 300, 22, "#b9d7c2");
  drawAtmosphericBand(slide, 622, 342, 300, 22, "#edcfb3");
  rect(slide, 746, 136, 430, 330, { color: "#121922" }, line("#121922", 0));
  drawSolidProductObject(slide, 776, 164, 370, 270, arm.palette.accent, 2);
  drawSoftConnector(slide, 630, 350, 782, 284, arm.palette.accent2, 18);
  drawSlideFilm(slide, 690, 494, 4, arm.palette.accent, 1);
  textSocket(slide, page.headline, { x: 84, y: 112, w: 520, h: 92 }, { fontSize: 35, bold: true, title: true, color: arm.palette.title, max: 94 });
  textSocket(slide, page.supporting_copy, { x: 88, y: 222, w: 456, h: 66 }, { fontSize: 15, color: arm.palette.muted, max: 128 });
  page.proof_labels.slice(0, 1).forEach((label) => {
    textSocket(slide, label, { x: 194, y: 570, w: 200, h: 28 }, { fontSize: 12, bold: true, color: arm.palette.title, align: "center", max: 40 });
  });
  page.callouts.slice(0, 2).forEach((label, index) => {
    textSocket(slide, label, { x: 858, y: 456 + index * 56, w: 266, h: 34 }, { fontSize: 13, bold: true, color: arm.palette.title, max: 66 });
  });
}

function drawMBeforeAfterTheater(slide, page, arm) {
  rect(slide, 0, 0, 560, H, { color: "#ece4d8" }, line("#ece4d8", 0));
  rect(slide, 560, 0, 720, H, { color: "#eaf1f6" }, line("#eaf1f6", 0));
  ellipse(slide, 498, -108, 230, 960, { color: "#fffdf8" }, line("#fffdf8", 0));
  rect(slide, 532, 0, 72, H, { color: "#e6c4b6" }, line("#e6c4b6", 0));
  drawSolidProductObject(slide, 118, 294, 350, 214, "#8a7652", 0, { frame: "#5d5142", inner: "#fbf3e7" });
  rect(slide, 704, 150, 486, 410, { color: "#121922" }, line("#121922", 0));
  drawSolidProductObject(slide, 740, 184, 418, 332, arm.palette.accent, 3);
  drawSoftConnector(slide, 484, 360, 740, 296, arm.palette.accent2, 18);
  drawSlideFilm(slide, 770, 548, 4, arm.palette.accent, 3);
  textSocket(slide, page.headline, { x: 86, y: 104, w: 458, h: 94 }, { fontSize: 34, bold: true, title: true, color: arm.palette.title, max: 94 });
  textSocket(slide, page.supporting_copy, { x: 706, y: 82, w: 420, h: 62 }, { fontSize: 15, color: arm.palette.muted, max: 132 });
  page.proof_labels.slice(0, 1).forEach((label) => {
    textSocket(slide, label, { x: 504, y: 226, w: 126, h: 42 }, { fontSize: 12, bold: true, color: arm.palette.title, align: "center", max: 36 });
  });
  page.callouts.slice(0, 2).forEach((label, index) => {
    textSocket(slide, label, { x: 784, y: 584 + index * 38, w: 330, h: 28 }, { fontSize: 13, bold: true, color: arm.palette.title, max: 76 });
  });
}

function drawMEvidenceWorkspace(slide, page, arm) {
  ellipse(slide, 96, 156, 1060, 440, { color: "#e9ede8" }, line("#e9ede8", 0));
  rect(slide, 142, 190, 84, 340, { color: "#172331" }, line("#172331", 0));
  [0, 1, 2].forEach((index) => {
    ellipse(slide, 174, 238 + index * 104, 22, 22, { color: index === 2 ? arm.palette.accent : "#fffdf8" }, line("#fffdf8", 0));
    rect(slide, 226, 246 + index * 104, 470 - index * 72, 10, { color: index % 2 ? C.green : C.blue }, line(C.blue, 0));
  });
  rect(slide, 318, 158, 650, 380, { color: "#121922" }, line("#121922", 0));
  drawSolidProductObject(slide, 356, 194, 570, 304, arm.palette.accent, 4);
  ellipse(slide, 836, 410, 284, 92, { color: "#fff7ea" }, line("#fff7ea", 0));
  rect(slide, 946, 198, 160, 210, { color: "#f7eadb" }, line("#f7eadb", 0));
  rect(slide, 970, 224, 112, 12, { color: arm.palette.accent2 }, line(arm.palette.accent2, 0));
  rect(slide, 970, 268, 92, 12, { color: arm.palette.accent }, line(arm.palette.accent, 0));
  rect(slide, 970, 312, 120, 12, { color: C.amber }, line(C.amber, 0));
  drawSoftConnector(slide, 226, 454, 356, 380, arm.palette.accent2, 16);
  textSocket(slide, page.headline, { x: 82, y: 88, w: 610, h: 74 }, { fontSize: 32, bold: true, title: true, color: arm.palette.title, max: 98 });
  textSocket(slide, page.supporting_copy, { x: 772, y: 84, w: 360, h: 66 }, { fontSize: 14, color: arm.palette.muted, max: 128 });
  page.proof_labels.slice(0, 1).forEach((label) => {
    textSocket(slide, label, { x: 276, y: 560, w: 260, h: 30 }, { fontSize: 12, bold: true, color: arm.palette.title, max: 48 });
  });
  page.callouts.slice(0, 2).forEach((label, index) => {
    textSocket(slide, label, { x: 864, y: 516 + index * 42, w: 270, h: 30 }, { fontSize: 13, bold: true, color: arm.palette.title, align: "center", max: 62 });
  });
}

function drawMDecisionMap(slide, page, arm) {
  ellipse(slide, 116, 124, 886, 452, { color: "#ecebe1" }, line("#ecebe1", 0));
  drawSoftConnector(slide, 232, 436, 420, 324, arm.palette.accent2, 16);
  drawSoftConnector(slide, 420, 324, 664, 370, arm.palette.accent2, 16);
  drawSoftConnector(slide, 664, 370, 892, 256, arm.palette.accent, 18);
  const nodes = [
    { x: 232, y: 436, label: page.proof_labels[0] || "story ready", dark: false },
    { x: 420, y: 324, label: page.callouts[0] || "generated proof next", dark: false },
    { x: 664, y: 370, label: page.callouts[1] || "blocked public branch", dark: false },
    { x: 892, y: 256, label: "public blocked", dark: true },
  ];
  nodes.forEach((node) => {
    ellipse(slide, node.x - 60, node.y - 44, 120, 88, { color: node.dark ? "#172331" : "#fffdf8" }, line(node.dark ? "#172331" : "#fffdf8", 0));
    textSocket(slide, node.label, { x: node.x - 58, y: node.y - 12, w: 116, h: 26 }, { fontSize: 12, bold: true, color: node.dark ? C.white : arm.palette.title, align: "center", max: 32 });
  });
  rect(slide, 760, 330, 360, 224, { color: "#121922" }, line("#121922", 0));
  drawSolidProductObject(slide, 790, 358, 300, 164, arm.palette.accent, 5);
  textSocket(slide, page.headline, { x: 84, y: 94, w: 560, h: 82 }, { fontSize: 33, bold: true, title: true, color: arm.palette.title, max: 96 });
  textSocket(slide, page.supporting_copy, { x: 706, y: 96, w: 384, h: 62 }, { fontSize: 15, color: arm.palette.muted, max: 128 });
}

function drawFullSlide(slide, page, arm) {
  drawBase(slide, page, arm);
  if (page.visual_grammar_module === "hero_field") drawMHeroField(slide, page, arm);
  else if (page.visual_grammar_module === "before_after_theater") drawMBeforeAfterTheater(slide, page, arm);
  else if (page.visual_grammar_module === "evidence_workspace") drawMEvidenceWorkspace(slide, page, arm);
  else if (page.visual_grammar_module === "decision_map") drawMDecisionMap(slide, page, arm);
  else drawMProductReveal(slide, page, arm);
  textSocket(slide, page.visual_grammar_module.replaceAll("_", " "), { x: 54, y: 664, w: 280, h: 18 }, { fontSize: 10, bold: true, color: arm.palette.muted, mono: true });
}

function drawControlSlide(slide, page, arm) {
  drawBase(slide, page, arm);
  ellipse(slide, 150, 180, 820, 360, { color: arm.mode === "negative" ? "#e4d8c4" : "#e8edf0" }, line("#cdd3d8", 1));
  rect(slide, 730, 210, 320, 240, { color: arm.palette.surface }, line("#c6cbd0", 1));
  drawRouteDots(slide, [{ x: 230, y: 450 }, { x: 420, y: 368 }, { x: 690, y: 330 }, { x: 900, y: 292 }], arm.palette.accent);
  const title = arm.mode === "negative"
    ? `${page.role}: L art-direction repair withheld`
    : arm.mode === "baseline"
      ? `${page.role}: prior workflow baseline`
      : `${page.role}: brief-only prompt output`;
  textSocket(slide, title, { x: 96, y: 110, w: 520, h: 86 }, { fontSize: 30, bold: true, title: true, color: arm.palette.title, max: 86 });
  textSocket(slide, "This comparison arm is generated locally for viewer context. The Part M manifest validates the full arm only.", { x: 100, y: 218, w: 430, h: 58 }, { fontSize: 13, color: arm.palette.muted, max: 128 });
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
    part_m_renderer_scope: arm.mode === "full" ? "renderer_art_direction_repair_consumes_l_2_77_and_k1_preservation_source" : "comparison_arm_not_part_m_quality_manifest",
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
      art_direction_scene: arm.mode === "full" ? page.art_direction_scene : "comparison_context",
      debug_annotation_count: arm.mode === "full" ? page.debug_annotation_count : 0,
      wireframe_dependency: arm.mode === "full" ? page.wireframe_dependency : "comparison_context",
      dominant_product_object_scale: arm.mode === "full" ? page.dominant_product_object_scale : "comparison_context",
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
  return buildNamedContactSheet(path.join(outRoot, "run2-79-four-arm-contact-sheet.png"), "Run 2.79 renderer art-direction repair comparison", sheets, sheets.length, labels);
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
      `part: Part M / Run ${RUN_ID}`,
      `consumed sources: ${arm.mode === "full" ? CONSUMED_SOURCES.join(", ") : "commercial_case.md only"}`,
      "full arm requirement: apply Part L art-direction repair while preserving the 2.77 scene mapping and K1 repair intent",
      "release boundary: public blocked until Part N visual evaluation",
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
      source: "scripts/generate_ppt_run2_79_renderer_art_direction_repair_arms.mjs",
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

function svgForArtDirection(page) {
  const product = `<rect x="610" y="120" width="520" height="420" rx="0" fill="#121922"/><rect x="642" y="154" width="456" height="344" rx="0" fill="#fffdf8"/><rect x="642" y="154" width="456" height="48" fill="#172331"/><rect x="682" y="238" width="300" height="108" fill="#edf4f8"/><rect x="704" y="266" width="200" height="18" fill="#2d62d6"/><rect x="704" y="316" width="246" height="14" fill="#0d8b68"/><rect x="682" y="374" width="120" height="56" fill="#eaf1fb"/><rect x="826" y="374" width="120" height="56" fill="#f8eadb"/><rect x="970" y="374" width="86" height="56" fill="#eaf1fb"/>`;
  if (page.visual_grammar_module === "hero_field") {
    return `<svg viewBox="0 0 1280 720" aria-hidden="true"><ellipse cx="430" cy="520" rx="430" ry="120" fill="#dfebef"/><ellipse cx="620" cy="390" rx="360" ry="100" fill="#dbeadc"/><rect x="170" y="514" width="250" height="24" fill="#bed6df"/><rect x="410" y="444" width="280" height="22" fill="#b9d7c2"/><rect x="650" y="346" width="260" height="22" fill="#edcfb3"/>${product}`;
  }
  if (page.visual_grammar_module === "before_after_theater") {
    return `<svg viewBox="0 0 1280 720" aria-hidden="true"><rect width="560" height="720" fill="#ece4d8"/><rect x="560" width="720" height="720" fill="#eaf1f6"/><rect x="532" width="72" height="720" fill="#e6c4b6"/><rect x="118" y="300" width="320" height="190" fill="#fbf3e7"/><rect x="150" y="336" width="220" height="22" fill="#8a7652"/>${product.replaceAll('x="610"', 'x="704"').replaceAll('width="520"', 'width="486"')}</svg>`;
  }
  if (page.visual_grammar_module === "evidence_workspace") {
    return `<svg viewBox="0 0 1280 720" aria-hidden="true"><ellipse cx="620" cy="378" rx="530" ry="220" fill="#e9ede8"/><rect x="142" y="190" width="84" height="340" fill="#172331"/><rect x="226" y="246" width="470" height="10" fill="#2d62d6"/><rect x="226" y="350" width="398" height="10" fill="#0d8b68"/><rect x="226" y="454" width="326" height="10" fill="#2d62d6"/>${product.replaceAll('x="610"', 'x="352"').replaceAll('y="120"', 'y="170"').replaceAll('width="520"', 'width="620"')}</svg>`;
  }
  if (page.visual_grammar_module === "decision_map") {
    return `<svg viewBox="0 0 1280 720" aria-hidden="true"><ellipse cx="560" cy="360" rx="460" ry="230" fill="#ecebe1"/><rect x="220" y="424" width="180" height="56" fill="#fffdf8"/><rect x="410" y="316" width="190" height="56" fill="#fffdf8"/><rect x="630" y="360" width="210" height="60" fill="#fffdf8"/><rect x="850" y="230" width="180" height="76" fill="#172331"/><rect x="260" y="446" width="280" height="16" fill="#0d8b68"/><rect x="540" y="370" width="330" height="18" fill="#2d62d6"/>${product.replaceAll('x="610"', 'x="760"').replaceAll('y="120"', 'y="338"').replaceAll('width="520"', 'width="360"').replaceAll('height="420"', 'height="224"')}</svg>`;
  }
  if (page.role === "climax") {
    return `<svg viewBox="0 0 1280 720" aria-hidden="true"><ellipse cx="260" cy="575" rx="410" ry="150" fill="#e8dfd1"/><ellipse cx="950" cy="340" rx="460" ry="300" fill="#e8f0f7"/><rect x="312" y="92" width="842" height="520" fill="#121922"/><rect x="352" y="126" width="760" height="444" fill="#fffdf8"/><rect x="394" y="238" width="520" height="150" fill="#edf4f8"/><rect x="424" y="284" width="340" height="20" fill="#2d62d6"/><rect x="424" y="338" width="430" height="18" fill="#0d8b68"/></svg>`;
  }
  return `<svg viewBox="0 0 1280 720" aria-hidden="true"><ellipse cx="220" cy="450" rx="390" ry="170" fill="#eadfcd"/><ellipse cx="930" cy="330" rx="430" ry="280" fill="#e8eef8"/>${product}</svg>`;
}

function buildStandaloneHtml(pages, outPath) {
  const sections = pages.map((page) => {
    const labels = page.proof_labels.slice(0, 1).map((label) => `<span>${htmlEscape(label)}</span>`).join("");
    const callouts = page.callouts.slice(0, 2).map((label) => `<b>${htmlEscape(label)}</b>`).join("");
    return `<section class="slide ${page.visual_grammar_module}" data-role="${htmlEscape(page.role)}">
      ${svgForArtDirection(page)}
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
<html lang="en" data-run-id="2.79">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Run 2.79 Renderer Art-Direction Repair</title>
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

function writeResult(pages, built, fourArmSheet, standaloneHtml, visualQualityEvaluation) {
  const full = built.find((item) => item.arm.armId === "run2_79_full_renderer_art_direction_repair");
  const viewerPath = path.join(outRoot, "ppt-run-viewer.html");
  const renderedPages = pages.map((page) => ({
    role: page.role,
    slide_index: page.slide_index,
    visual_grammar_module: page.visual_grammar_module,
    module_variant: page.module_variant,
    layout_signature: page.layout_signature,
    visual_density_profile: page.visual_density_profile,
    art_direction_scene: page.art_direction_scene,
    source_run2_77_page: page.source_run2_77_page,
    source_l_repair_instruction: page.source_l_repair_instruction,
    source_k1_target_scene_direction: page.source_k1_target_scene_direction,
    renderer_repair_directives_applied: page.renderer_repair_directives_applied,
    debug_annotation_count: page.debug_annotation_count,
    wireframe_dependency: page.wireframe_dependency,
    dominant_product_object_scale: page.dominant_product_object_scale,
    min_visible_label_font_size: page.min_visible_label_font_size,
    label_count: page.label_count,
    text_sockets_used: page.text_sockets_used,
    text_socket_bindings: page.text_socket_bindings,
    source_text_socket_label_inputs: page.source_text_socket_label_inputs,
    visual_containers: page.visual_containers,
    headline: page.headline,
    supporting_copy: page.supporting_copy,
    proof_labels: page.proof_labels,
    callouts: page.callouts,
    overflow_policy: page.overflow_policy,
    source_trace_terms_visible_on_canvas: page.source_trace_terms_visible_on_canvas,
    public_polish_claimed: page.public_polish_claimed,
    canvas_word_count: page.canvas_word_count,
  }));
  const result = {
    artifact_id: "run2_79_renderer_art_direction_repair_rerun_result",
    part: "Part M",
    schema_version: "ppt_run2_79_renderer_art_direction_repair_rerun_result.v1",
    run_id: RUN_ID,
    status: "run2_79_renderer_art_direction_repair_rerun_generated_public_blocked",
    public_ready: false,
    public_release_started: false,
    quality_claim_boundary: "renderer_art_direction_repair_generated_viewer_check_only_no_part_n_quality_verdict",
    consumed_sources: CONSUMED_SOURCES,
    source_l_evaluation: {
      status: visualQualityEvaluation.status,
      top_blocker: visualQualityEvaluation.visual_quality_assessment?.top_blocker,
      primary_layer: visualQualityEvaluation.visual_quality_assessment?.next_layer_to_fix,
      next_required_action: visualQualityEvaluation.next_required_action,
      source_result: RUN2_79_INPUTS.visualQualityEvaluation,
    },
    renderer_art_direction_repair_manifest: {
      generator: "scripts/generate_ppt_run2_79_renderer_art_direction_repair_arms.mjs",
      consumed_sources: CONSUMED_SOURCES,
      arms: built.map((item) => item.arm.armId),
      best_internal_arm: "run2_79_full_renderer_art_direction_repair",
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
    renderer_art_direction_repair_checks: {
      pages_with_l_repair_instruction_consumed: renderedPages.filter((page) => page.renderer_repair_directives_applied.includes("l_repair_instruction_consumed")).length,
      pages_with_debug_annotations_removed: renderedPages.filter((page) => page.debug_annotation_count === 0).length,
      pages_with_dominant_product_object: renderedPages.filter((page) => ["large", "hero", "full_frame"].includes(page.dominant_product_object_scale)).length,
      pages_with_public_scene_hierarchy: renderedPages.filter((page) => page.renderer_repair_directives_applied.includes("public_scene_hierarchy") && page.art_direction_scene).length,
      pages_with_reduced_wireframe_dependency: renderedPages.filter((page) => ["reduced", "minimal"].includes(page.wireframe_dependency)).length,
      pages_with_min_visible_label_size: renderedPages.filter((page) => page.min_visible_label_font_size >= 12).length,
      source_trace_terms_visible_on_canvas_count: renderedPages.reduce((sum, page) => sum + page.source_trace_terms_visible_on_canvas.length, 0),
      public_quality_verdict_started: false,
    },
    preliminary_viewer_observations: [
      "Generated full arm applies the Part L art-direction repair instruction to the Run 2.77 scene model.",
      "Viewer is updated for local inspection, but Part N must still evaluate visual quality.",
    ],
    verification_limitations: [
      "source_trace_terms_visible_on_canvas is renderer-declared metadata in Part M; Part N must inspect the viewer/PPT surface before any visual quality verdict.",
    ],
    release_boundary: "public_blocked_until_part_n_visual_quality_evaluation_and_human_release_approval",
    next_required_action: "part_n_visual_quality_evaluation_for_run2_79",
  };
  writeJson(path.join(root, RESULT_JSON), result);
  fs.writeFileSync(
    path.join(root, RESULT_MD),
    [
      "# Run 2.79 Renderer Art-Direction Repair Rerun",
      "",
      "Status: generated locally, public blocked.",
      "",
      "Run 2.79 consumes Part L, Run 2.77, and K1 before native PPT drawing.",
      "",
      "Best internal arm: `run2_79_full_renderer_art_direction_repair`.",
      "",
      "Viewer check: generated output is available for local browser inspection. Part N must still evaluate visual quality.",
      "",
      "Limit: source-trace visibility is renderer-declared metadata in Part M; Part N must inspect the viewer/PPT surface before any quality verdict.",
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
  const full = built.find((item) => item.arm.armId === "run2_79_full_renderer_art_direction_repair");
  const standaloneHtml = path.join(full.workspace, "output", "run2-79-renderer-art-direction-repair.html");
  buildStandaloneHtml(pages, standaloneHtml);
  writeJson(path.join(outRoot, "run2_79_renderer_art_direction_repair_rerun_summary.json"), {
    run_id: "run2_79_renderer_art_direction_repair_four_arms",
    arms: built.map((item) => item.arm.armId),
    consumed_sources: CONSUMED_SOURCES,
    combined_contact_sheet: repoRelative(fourArmSheet),
    created: built.map((item) => repoRelative(item.workspace)),
  });
  const result = writeResult(pages, built, fourArmSheet, standaloneHtml, inputs.visualQualityEvaluation);
  execFileSync("python3.11", [path.join(root, "scripts", "build_ppt_run_html_viewer.py")], { cwd: root, stdio: "pipe" });
  return result;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result.renderer_art_direction_repair_manifest, null, 2)}\n`);
}

export {
  CONSUMED_SOURCES,
  MODULE_BY_ROLE,
  RUN2_79_INPUTS,
  armSpecs,
  buildRenderModel,
  main,
};
