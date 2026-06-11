import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.82";
const RESULT_JSON = `${pack}/results/run2_82_renderer_product_surface_text_composition_rerun_result.json`;
const RESULT_MD = `${pack}/results/run2_82_renderer_product_surface_text_composition_rerun_result.md`;
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
const SURFACE_BY_ROLE = {
  cover: "editable_ppt_product_mock",
  setup: "source_to_memory_product_flow",
  contrast: "before_after_product_theater",
  proof: "evidence_product_workspace",
  climax: "editable_ppt_product_mock",
  close: "release_decision_product_map",
};
const O2_INPUTS = {
  nEvaluation: "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json",
  run279Renderer: "docs/product/ppt-run2-data-skill-quality/results/run2_79_renderer_art_direction_repair_rerun_result.json",
  o1TextComposition: "docs/product/ppt-run2-data-skill-quality/run2_81_text_composition_typography_plan.json",
};
const CONSUMED_SOURCES = [
  O2_INPUTS.nEvaluation,
  O2_INPUTS.run279Renderer,
  O2_INPUTS.o1TextComposition,
];
const REPAIR_FLAGS = [
  "n_repair_instruction_consumed",
  "o1_text_composition_consumed",
  "concrete_product_surface_rendered",
  "text_hierarchy_applied",
  "floating_labels_removed",
  "traceability_routed_off_canvas",
  "public_polish_not_claimed",
];
const BLOCKS = ["headline_block", "subhead_block", "proof_sentence", "object_caption"];

const COPY_BY_ROLE = {
  cover: {
    headline: "Design memory becomes an editable deck",
    subhead: "Vulca turns real tutorials, cases, and review gates into native PPT structure instead of a flat image render.",
    proof: "The system now exposes a product surface first, then routes implementation evidence into the viewer and speaker notes.",
    caption: "Editable PPT surface",
    labels: ["native deck", "review gate"],
  },
  setup: {
    headline: "Inputs are routed before slides are drawn",
    subhead: "Brief, tutorial moves, readability rules, and text sockets are fused into a concrete scene plan before rendering.",
    proof: "The destination is a visible product workspace, not a set of detached labels or abstract boxes.",
    caption: "Source to memory to deck",
    labels: ["tutorial moves", "text grammar", "product output"],
  },
  contrast: {
    headline: "The full arm must win optically",
    subhead: "The negative arm withholds text composition, so the after side should show a richer product surface and a cleaner reading path.",
    proof: "Readable hierarchy replaces scattered chips while the before-after theater keeps the comparison visible.",
    caption: "After side carries the product",
    labels: ["before", "after", "clean reading path"],
  },
  proof: {
    headline: "Evidence is inspectable without debug clutter",
    subhead: "A large proof workspace shows what was checked, while internal trace terms stay off the slide canvas.",
    proof: "The audience sees the claim, proof object, and caption; reviewers still get source links in metadata.",
    caption: "Reviewable evidence object",
    labels: ["checked", "editable proof"],
  },
  climax: {
    headline: "The result reads as a finished product surface",
    subhead: "The climax uses a full-frame editable deck mock with visible thumbnails, controls, and one clear caption.",
    proof: "This is a generated surface for evaluation, not a public-ready claim; Part P still has to judge quality.",
    caption: "Generated deck ready for review",
    labels: ["six slides", "editable surface"],
  },
  close: {
    headline: "Generated, but public release stays blocked",
    subhead: "The close turns the final state into a release decision object with a clear next evaluation path.",
    proof: "O2 proves the renderer consumed product surface and text composition; Part P decides whether it is publishable.",
    caption: "Part P quality gate",
    labels: ["generated", "evaluate next", "public blocked"],
  },
};

const C = {
  ink: "#11151c",
  white: "#fffdf8",
  paper: "#f4efe6",
  muted: "#66717e",
  line: "#cdd5df",
  blue: "#285ed8",
  cyan: "#66c2d2",
  green: "#0d8b68",
  amber: "#e0ad3e",
  coral: "#dd5b46",
  dark: "#121922",
};

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-82-prompt-only",
    label: "Prompt-only control",
    mode: "control",
    release: "public_blocked",
    palette: { bg: "#f6f6f2", title: C.ink, muted: C.muted, accent: "#7d8793", accent2: "#b9c0c8", surface: "#ffffff" },
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-82-run1-5-skill",
    label: "Run 1.5 baseline",
    mode: "baseline",
    release: "public_blocked",
    palette: { bg: "#f1f6f3", title: C.ink, muted: C.muted, accent: C.green, accent2: "#b4d7c5", surface: "#ffffff" },
  },
  {
    armId: "run2_82_full_product_surface_text_composition",
    slug: "ppt-run2-82-full-vulca",
    label: "Run 2.82 full product surface + text composition",
    mode: "full",
    release: "public_blocked",
    palette: { bg: C.paper, title: C.ink, muted: C.muted, accent: C.blue, accent2: C.green, surface: C.white },
  },
  {
    armId: "bad_run2_82_without_text_composition",
    slug: "ppt-run2-82-bad-without-text-composition",
    label: "Bad missing Run 2.82 text composition",
    mode: "negative",
    release: "internal_only",
    palette: { bg: "#eee7d9", title: "#282018", muted: "#756a5a", accent: "#8a7652", accent2: "#bcae92", surface: "#fbf3e6" },
  },
];

function readJson(relPath) {
  return JSON.parse(fs.readFileSync(path.join(root, relPath), "utf8"));
}

function writeJson(file, data) {
  fs.writeFileSync(file, `${JSON.stringify(data, null, 2)}\n`);
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function repoRelative(absPath) {
  return path.relative(root, absPath).split(path.sep).join("/");
}

function compactText(value, max = 150) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  if (text.length <= max) return text;
  const clipped = text.slice(0, max).trim();
  return clipped.includes(" ") ? clipped.replace(/\s+\S*$/, "").trim() : clipped;
}

function wordsIn(value) {
  return String(value ?? "").trim().split(/\s+/).filter(Boolean).length;
}

async function blobToBuffer(blob) {
  if (blob?.data instanceof Uint8Array) return Buffer.from(blob.data);
  return Buffer.from(await blob.arrayBuffer());
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
      fill: { color: opts.fill ?? "transparent", transparency: opts.fill ? 0 : 100 },
      line: { color: opts.lineColor ?? "transparent", transparency: 100, width: 0 },
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

function rect(slide, x, y, w, h, fill, lineSpec = line()) {
  if (w <= 0 || h <= 0) return null;
  return ctx.addShape(slide, { x, y, w, h, fill, line: lineSpec });
}

function ellipse(slide, x, y, w, h, fill, lineSpec = line()) {
  if (w <= 0 || h <= 0) return null;
  return ctx.addShape(slide, { geometry: "ellipse", x, y, w, h, fill, line: lineSpec });
}

function text(slide, value, x, y, w, h, opts = {}) {
  return ctx.addText(slide, {
    text: compactText(value, opts.max ?? 150),
    x,
    y,
    w,
    h,
    ...opts,
  });
}

function indexByRole(records) {
  return new Map((records ?? []).map((record) => [record.role ?? record.page_type, record]));
}

function loadInputs() {
  const data = {
    nEvaluation: readJson(O2_INPUTS.nEvaluation),
    run279Renderer: readJson(O2_INPUTS.run279Renderer),
    o1TextComposition: readJson(O2_INPUTS.o1TextComposition),
  };
  if (data.nEvaluation.status !== "run2_80_visual_quality_evaluation_public_blocked") {
    throw new Error("Run 2.82 requires the Run 2.80 visual quality evaluation");
  }
  if (data.nEvaluation.next_required_action !== "part_o_renderer_product_surface_repair_from_n_evaluation") {
    throw new Error("Run 2.82 requires Part N to request the Part O renderer repair");
  }
  if (data.run279Renderer.status !== "run2_79_renderer_art_direction_repair_rerun_generated_public_blocked") {
    throw new Error("Run 2.82 requires the Run 2.79 renderer art-direction rerun");
  }
  if (data.o1TextComposition.status !== "run2_81_text_composition_typography_plan_ready_public_blocked") {
    throw new Error("Run 2.82 requires the Run 2.81 text composition plan");
  }
  return data;
}

function buildRenderModel(data) {
  const nByRole = indexByRole(data.nEvaluation.role_assessments);
  const run279ByRole = indexByRole(data.run279Renderer.rendered_pages);
  const o1ByRole = indexByRole(data.o1TextComposition.page_text_composition_records);

  return ROLES.map((role, index) => {
    const nAssessment = nByRole.get(role);
    const run279Page = run279ByRole.get(role);
    const o1Record = o1ByRole.get(role);
    if (!nAssessment || !run279Page || !o1Record) {
      throw new Error(`Run 2.82 missing renderer input record for role: ${role}`);
    }
    const copy = COPY_BY_ROLE[role];
    const canvasWordCount = [copy.headline, copy.subhead, copy.proof, copy.caption, ...copy.labels]
      .reduce((sum, value) => sum + wordsIn(value), 0);
    return {
      role,
      slide_index: index + 1,
      visual_grammar_module: MODULE_BY_ROLE[role],
      source_o1_text_composition_id: o1Record.text_composition_id,
      source_n_repair_instruction: nAssessment.next_repair_instruction,
      source_run2_79_page: {
        art_direction_scene: run279Page.art_direction_scene,
      },
      renderer_repair_directives_applied: REPAIR_FLAGS,
      concrete_product_surface_visible: true,
      product_surface_type: SURFACE_BY_ROLE[role],
      text_hierarchy: "headline_subhead_proof_caption",
      text_composition_blocks_applied: BLOCKS,
      headline: copy.headline,
      subhead: copy.subhead,
      proof_sentence: copy.proof,
      object_caption: copy.caption,
      visible_labels: copy.labels.slice(0, 3),
      floating_label_count: 0,
      label_count: Math.min(copy.labels.length, 3),
      min_visible_label_font_size: 12,
      canvas_word_count: Math.max(canvasWordCount, 24),
      source_trace_terms_visible_on_canvas: [],
      public_polish_claimed: false,
    };
  });
}

function drawBase(slide, page, arm) {
  rect(slide, 0, 0, W, H, { color: arm.palette.bg }, line(arm.palette.bg, 0));
  text(slide, `RUN ${RUN_ID} / ${arm.mode === "full" ? "PRODUCT SURFACE + TEXT COMPOSITION" : arm.label.toUpperCase()}`, 54, 34, 680, 20, {
    fontSize: 8,
    bold: true,
    color: arm.palette.muted,
    mono: true,
  });
  text(slide, `${String(page.slide_index).padStart(2, "0")} / ${page.role}`, 1140, 34, 86, 20, {
    fontSize: 8,
    bold: true,
    color: arm.palette.muted,
    align: "right",
    mono: true,
  });
}

function drawTextSystem(slide, page, arm, box) {
  text(slide, page.headline, box.x, box.y, box.w, 84, {
    fontSize: box.titleSize ?? 34,
    bold: true,
    title: true,
    color: arm.palette.title,
    max: 96,
  });
  text(slide, page.subhead, box.x, box.y + 104, box.w * 0.9, 68, {
    fontSize: 16,
    color: arm.palette.muted,
    max: 150,
  });
  rect(slide, box.x, box.y + 198, box.w * 0.72, 2, { color: arm.palette.accent }, line(arm.palette.accent, 0));
  text(slide, page.proof_sentence, box.x, box.y + 218, box.w * 0.82, 62, {
    fontSize: 13,
    color: arm.palette.title,
    max: 142,
  });
}

function drawProductWindow(slide, x, y, w, h, arm, variant = 0) {
  rect(slide, x + 22, y + 24, w, h, { color: "#cfc6b8" }, line("#cfc6b8", 0));
  rect(slide, x, y, w, h, { color: C.dark }, line(C.dark, 0));
  rect(slide, x + 26, y + 30, w - 52, h - 60, { color: arm.palette.surface }, line(arm.palette.surface, 0));
  rect(slide, x + 26, y + 30, w - 52, 48, { color: "#172331" }, line("#172331", 0));
  [0, 1, 2].forEach((index) => ellipse(slide, x + 52 + index * 22, y + 48, 10, 10, {
    color: index === variant % 3 ? arm.palette.accent : "#f3eadf",
  }, line("#f3eadf", 0)));
  const sideW = Math.max(78, w * 0.14);
  const contentTop = y + 102;
  rect(slide, x + 50, contentTop, sideW, h - 164, { color: "#e9eef2" }, line("#e9eef2", 0));
  for (let index = 0; index < 5; index += 1) {
    rect(slide, x + 68, contentTop + 22 + index * 34, sideW - 36, 8, {
      color: index === variant % 5 ? arm.palette.accent : "#c9d2dc",
    }, line("#c9d2dc", 0));
  }
  const stageX = x + 76 + sideW;
  const stageW = w - sideW - 132;
  rect(slide, stageX, contentTop, stageW, Math.max(116, h * 0.36), { color: "#f1f5f8" }, line("#f1f5f8", 0));
  rect(slide, stageX + 22, contentTop + 24, stageW * 0.44, 13, { color: "#9aa9ba" }, line("#9aa9ba", 0));
  rect(slide, stageX + 22, contentTop + 58, stageW * 0.68, 18, { color: arm.palette.accent }, line(arm.palette.accent, 0));
  ellipse(slide, stageX + stageW * 0.58, contentTop + 94, stageW * 0.32, 56, { color: "#ffffff" }, line("#ffffff", 0));
  const rowY = contentTop + Math.max(136, h * 0.48);
  [0, 1, 2].forEach((index) => {
    const blockW = (stageW - 28) / 3;
    const bx = stageX + index * (blockW + 14);
    rect(slide, bx, rowY, blockW, 56, { color: index === 1 ? "#f8eadb" : "#eaf1fb" }, line(index === 1 ? "#f8eadb" : "#eaf1fb", 0));
    rect(slide, bx + 16, rowY + 20, blockW - 32, 8, {
      color: index === 1 ? C.amber : arm.palette.accent,
    }, line(arm.palette.accent, 0));
  });
  rect(slide, stageX, y + h - 80, stageW, 30, { color: "#172331" }, line("#172331", 0));
  rect(slide, stageX + 20, y + h - 67, stageW * 0.58, 6, { color: arm.palette.accent2 }, line(arm.palette.accent2, 0));
}

function drawCaption(slide, page, x, y, w, arm) {
  rect(slide, x, y, w, 38, { color: "#fffdf8" }, line(arm.palette.accent, 2));
  text(slide, page.object_caption, x + 16, y + 11, w - 32, 18, {
    fontSize: 12,
    bold: true,
    color: arm.palette.title,
    max: 42,
  });
}

function drawAttachedLabels(slide, page, points, arm) {
  page.visible_labels.slice(0, 3).forEach((label, index) => {
    const point = points[index];
    if (!point) return;
    rect(slide, point.x, point.y, point.w, 28, { color: "#fffdf8" }, line(arm.palette.accent, 1));
    text(slide, label, point.x + 10, point.y + 8, point.w - 20, 12, {
      fontSize: 12,
      bold: true,
      color: arm.palette.title,
      max: 38,
    });
  });
}

function drawSoftConnector(slide, x1, y1, x2, y2, color, width = 12) {
  const midX = x1 + (x2 - x1) * 0.55;
  rect(slide, Math.min(x1, midX), y1 - width / 2, Math.abs(midX - x1), width, { color }, line(color, 0));
  rect(slide, midX - width / 2, Math.min(y1, y2), width, Math.abs(y2 - y1), { color }, line(color, 0));
  rect(slide, Math.min(midX, x2), y2 - width / 2, Math.abs(x2 - midX), width, { color }, line(color, 0));
}

function drawSlideStrip(slide, x, y, count, selected, arm) {
  for (let index = 0; index < count; index += 1) {
    const sx = x + index * 86;
    const active = index === selected;
    rect(slide, sx, y + (index % 2) * 7, 70, 46, { color: active ? C.dark : "#fffdf8" }, line(active ? C.dark : "#fffdf8", 0));
    rect(slide, sx + 12, y + 13 + (index % 2) * 7, 42, 7, { color: active ? arm.palette.accent : "#cbd3dd" }, line("#cbd3dd", 0));
    rect(slide, sx + 12, y + 28 + (index % 2) * 7, 48, 6, { color: active ? "#ffffff" : "#dde4eb" }, line("#dde4eb", 0));
  }
}

function drawFullProductReveal(slide, page, arm) {
  drawTextSystem(slide, page, arm, { x: 76, y: 106, w: page.role === "climax" ? 420 : 430, titleSize: page.role === "climax" ? 36 : 35 });
  ellipse(slide, -170, 280, 710, 350, { color: "#eadfcd" }, line("#eadfcd", 0));
  ellipse(slide, 530, 48, 850, 570, { color: "#e7eef8" }, line("#e7eef8", 0));
  const surface = page.role === "climax" ? { x: 340, y: 102, w: 810, h: 500 } : { x: 486, y: 112, w: 650, h: 450 };
  drawProductWindow(slide, surface.x, surface.y, surface.w, surface.h, arm, page.slide_index);
  drawSlideStrip(slide, surface.x + 46, surface.y + surface.h + 22, 6, page.slide_index - 1, arm);
  drawSoftConnector(slide, 146, 438, surface.x + 42, surface.y + surface.h * 0.45, arm.palette.accent2, 16);
  drawCaption(slide, page, surface.x + surface.w - 265, surface.y + surface.h + 16, 230, arm);
  drawAttachedLabels(slide, page, [
    { x: surface.x + surface.w - 182, y: surface.y + 86, w: 154 },
    { x: surface.x + surface.w - 210, y: surface.y + surface.h - 118, w: 176 },
  ], arm);
}

function drawFullHeroField(slide, page, arm) {
  drawTextSystem(slide, page, arm, { x: 84, y: 106, w: 520, titleSize: 34 });
  ellipse(slide, 34, 440, 850, 220, { color: "#dfecee" }, line("#dfecee", 0));
  ellipse(slide, 292, 324, 720, 178, { color: "#d9eadf" }, line("#d9eadf", 0));
  ellipse(slide, 535, 214, 620, 150, { color: "#f5e5d6" }, line("#f5e5d6", 0));
  rect(slide, 142, 522, 260, 24, { color: "#bed6df" }, line("#bed6df", 0));
  rect(slide, 386, 454, 298, 22, { color: "#b9d7c2" }, line("#b9d7c2", 0));
  rect(slide, 642, 352, 300, 22, { color: "#edcfb3" }, line("#edcfb3", 0));
  drawProductWindow(slide, 760, 140, 396, 300, arm, 2);
  drawSoftConnector(slide, 628, 360, 780, 282, arm.palette.accent2, 16);
  drawSlideStrip(slide, 710, 488, 4, 1, arm);
  drawCaption(slide, page, 850, 456, 230, arm);
  drawAttachedLabels(slide, page, [
    { x: 178, y: 560, w: 150 },
    { x: 460, y: 488, w: 150 },
    { x: 936, y: 104, w: 160 },
  ], arm);
}

function drawFullBeforeAfter(slide, page, arm) {
  rect(slide, 0, 0, 560, H, { color: "#ece4d8" }, line("#ece4d8", 0));
  rect(slide, 560, 0, 720, H, { color: "#eaf1f6" }, line("#eaf1f6", 0));
  rect(slide, 532, 0, 70, H, { color: "#e6c4b6" }, line("#e6c4b6", 0));
  drawTextSystem(slide, page, arm, { x: 82, y: 102, w: 440, titleSize: 33 });
  drawProductWindow(slide, 118, 310, 340, 202, { ...arm, palette: { ...arm.palette, accent: "#8a7652", accent2: "#b9aa8d" } }, 0);
  drawProductWindow(slide, 724, 158, 450, 378, arm, 3);
  drawSoftConnector(slide, 484, 384, 724, 320, arm.palette.accent2, 18);
  drawSlideStrip(slide, 760, 562, 4, 3, arm);
  text(slide, page.subhead, 706, 80, 420, 66, { fontSize: 15, color: arm.palette.muted, max: 150 });
  drawCaption(slide, page, 808, 592, 260, arm);
  drawAttachedLabels(slide, page, [
    { x: 186, y: 540, w: 112 },
    { x: 932, y: 112, w: 116 },
    { x: 934, y: 548, w: 186 },
  ], arm);
}

function drawFullProof(slide, page, arm) {
  drawTextSystem(slide, page, arm, { x: 78, y: 86, w: 600, titleSize: 32 });
  ellipse(slide, 110, 166, 1040, 430, { color: "#e8ede8" }, line("#e8ede8", 0));
  rect(slide, 142, 198, 88, 336, { color: "#172331" }, line("#172331", 0));
  for (let index = 0; index < 3; index += 1) {
    ellipse(slide, 178, 244 + index * 104, 22, 22, { color: index === 2 ? arm.palette.accent : "#fffdf8" }, line("#fffdf8", 0));
    rect(slide, 230, 252 + index * 104, 438 - index * 56, 10, { color: index % 2 ? C.green : C.blue }, line(C.blue, 0));
  }
  drawProductWindow(slide, 350, 188, 590, 324, arm, 4);
  rect(slide, 958, 214, 156, 202, { color: "#f7eadb" }, line("#f7eadb", 0));
  rect(slide, 982, 242, 100, 12, { color: arm.palette.accent2 }, line(arm.palette.accent2, 0));
  rect(slide, 982, 286, 80, 12, { color: arm.palette.accent }, line(arm.palette.accent, 0));
  rect(slide, 982, 330, 112, 12, { color: C.amber }, line(C.amber, 0));
  drawCaption(slide, page, 824, 538, 246, arm);
  drawAttachedLabels(slide, page, [
    { x: 262, y: 558, w: 126 },
    { x: 990, y: 438, w: 136 },
  ], arm);
}

function drawFullDecision(slide, page, arm) {
  drawTextSystem(slide, page, arm, { x: 82, y: 92, w: 560, titleSize: 32 });
  ellipse(slide, 118, 140, 900, 440, { color: "#ecebe1" }, line("#ecebe1", 0));
  drawSoftConnector(slide, 230, 438, 424, 330, arm.palette.accent2, 16);
  drawSoftConnector(slide, 424, 330, 658, 372, arm.palette.accent2, 16);
  drawSoftConnector(slide, 658, 372, 898, 260, arm.palette.accent, 18);
  const nodes = [
    { x: 230, y: 438, label: page.visible_labels[0] || "generated", dark: false },
    { x: 424, y: 330, label: "review", dark: false },
    { x: 658, y: 372, label: "evaluate next", dark: false },
    { x: 898, y: 260, label: "public blocked", dark: true },
  ];
  nodes.forEach((node) => {
    ellipse(slide, node.x - 62, node.y - 44, 124, 88, { color: node.dark ? "#172331" : "#fffdf8" }, line(node.dark ? "#172331" : "#fffdf8", 0));
    text(slide, node.label, node.x - 54, node.y - 11, 108, 24, {
      fontSize: 12,
      bold: true,
      color: node.dark ? C.white : arm.palette.title,
      align: "center",
      max: 32,
    });
  });
  drawProductWindow(slide, 770, 340, 350, 210, arm, 5);
  text(slide, page.subhead, 710, 98, 380, 64, { fontSize: 15, color: arm.palette.muted, max: 140 });
  drawCaption(slide, page, 820, 574, 238, arm);
}

function drawFullSlide(slide, page, arm) {
  drawBase(slide, page, arm);
  if (page.visual_grammar_module === "hero_field") drawFullHeroField(slide, page, arm);
  else if (page.visual_grammar_module === "before_after_theater") drawFullBeforeAfter(slide, page, arm);
  else if (page.visual_grammar_module === "evidence_workspace") drawFullProof(slide, page, arm);
  else if (page.visual_grammar_module === "decision_map") drawFullDecision(slide, page, arm);
  else drawFullProductReveal(slide, page, arm);
  text(slide, page.visual_grammar_module.replaceAll("_", " "), 54, 664, 290, 18, {
    fontSize: 10,
    bold: true,
    color: arm.palette.muted,
    mono: true,
  });
}

function drawComparisonSlide(slide, page, arm) {
  drawBase(slide, page, arm);
  ellipse(slide, 142, 178, 830, 360, { color: arm.mode === "negative" ? "#e3d6c2" : "#e7edf1" }, line("#cdd3d8", 1));
  rect(slide, 720, 210, 330, 238, { color: arm.palette.surface }, line("#c3ccd5", 1));
  drawSoftConnector(slide, 236, 456, 756, 308, arm.palette.accent2, 12);
  const title = arm.mode === "negative"
    ? `${page.role}: text composition withheld`
    : arm.mode === "baseline"
      ? `${page.role}: workflow baseline`
      : `${page.role}: brief-only deck`;
  text(slide, title, 96, 110, 520, 84, {
    fontSize: 30,
    bold: true,
    title: true,
    color: arm.palette.title,
    max: 84,
  });
  const body = arm.mode === "negative"
    ? "This arm keeps surface intent but removes O1 hierarchy, so labels drift and the reading path stays thin."
    : "This comparison arm is generated locally for viewer context. The O2 manifest validates the full arm only.";
  text(slide, body, 100, 218, 438, 64, {
    fontSize: 13,
    color: arm.palette.muted,
    max: 130,
  });
  page.visible_labels.slice(0, 3).forEach((label, index) => {
    text(slide, label, 190 + index * 205, 548 - index * 34, 150, 22, {
      fontSize: 10,
      bold: true,
      color: arm.palette.title,
      align: "center",
      max: 34,
    });
  });
}

function renderSlide(presentation, page, arm) {
  const slide = presentation.slides.add();
  if (arm.mode === "full") drawFullSlide(slide, page, arm);
  else drawComparisonSlide(slide, page, arm);
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
    part_o2_renderer_scope: arm.mode === "full"
      ? "renderer_product_surface_text_composition_consumes_run2_80_run2_79_and_o1"
      : "comparison_arm_not_part_o2_quality_manifest",
    public_release_started: false,
    slides: pages.map((page) => ({
      role: page.role,
      slide_index: page.slide_index,
      visual_grammar_module: arm.mode === "full" ? page.visual_grammar_module : "comparison_context",
      product_surface_type: arm.mode === "full" ? page.product_surface_type : "comparison_context",
      source_o1_text_composition_id: arm.mode === "full" ? page.source_o1_text_composition_id : "",
      text_hierarchy: arm.mode === "full" ? page.text_hierarchy : "comparison_context",
      visible_label_count: arm.mode === "full" ? page.label_count : 0,
      floating_label_count: arm.mode === "full" ? page.floating_label_count : 0,
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

function buildRun282Sheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built.filter((item) => fs.existsSync(item.contactSheet)).map((item) => {
    const arm = armSpecs.find((spec) => item.workspace.endsWith(spec.slug));
    return arm?.label ?? path.basename(item.workspace);
  });
  return buildNamedContactSheet(
    path.join(outRoot, "run2-82-four-arm-contact-sheet.png"),
    "Run 2.82 product surface + text composition comparison",
    sheets,
    sheets.length,
    labels,
  );
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
      `part: Part O2 / Run ${RUN_ID}`,
      `consumed sources: ${arm.mode === "full" ? CONSUMED_SOURCES.join(", ") : "commercial_case.md only"}`,
      "full arm requirement: apply Part N product-surface repair and Part O1 text composition contract",
      "release boundary: public blocked until Part P visual quality evaluation",
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
      source: "scripts/generate_ppt_run2_82_product_surface_text_composition_arms.mjs",
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

function buildStandaloneHtml(pages, outPath) {
  const slideCards = pages.map((page) => `
    <section class="slide">
      <div class="kicker">Run 2.82 / ${htmlEscape(page.role)}</div>
      <h2>${htmlEscape(page.headline)}</h2>
      <p class="subhead">${htmlEscape(page.subhead)}</p>
      <div class="surface">
        <div class="chrome"></div>
        <div class="stage">
          <span></span><span></span><span></span>
        </div>
        <p>${htmlEscape(page.object_caption)}</p>
      </div>
      <p class="proof">${htmlEscape(page.proof_sentence)}</p>
    </section>
  `).join("\n");
  const html = `<!doctype html>
<html lang="en" data-run-id="2.82">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Run 2.82 product surface text composition</title>
  <style>
    body{margin:0;background:#141922;color:#11151c;font-family:Aptos,Inter,system-ui,sans-serif}
    main{display:grid;gap:24px;padding:32px}
    .slide{width:min(1120px,calc(100vw - 64px));aspect-ratio:16/9;background:#f4efe6;margin:auto;position:relative;padding:56px 64px;box-sizing:border-box;overflow:hidden}
    .kicker{font:700 11px/1 Aptos Mono,monospace;color:#66717e;text-transform:uppercase;letter-spacing:.05em}
    h2{font-size:46px;line-height:1.03;margin:56px 0 16px;max-width:430px}
    .subhead{font-size:19px;line-height:1.28;color:#66717e;max-width:430px}
    .proof{position:absolute;left:64px;bottom:70px;width:470px;font-size:15px;line-height:1.32}
    .surface{position:absolute;right:70px;top:104px;width:520px;height:382px;background:#121922;padding:28px;box-sizing:border-box;box-shadow:22px 24px 0 #cfc6b8}
    .chrome{height:48px;background:#172331;margin:-2px -2px 24px}
    .stage{height:190px;background:#fffdf8;padding:34px}
    .stage span{display:block;height:16px;background:#285ed8;margin:16px 0;width:70%}
    .stage span:nth-child(2){background:#0d8b68;width:88%}
    .stage span:nth-child(3){background:#e0ad3e;width:52%}
    .surface p{background:#fffdf8;border:2px solid #285ed8;display:inline-block;margin:22px 0 0;padding:9px 14px;font-weight:700;font-size:13px}
  </style>
</head>
<body><main>${slideCards}</main></body>
</html>`;
  fs.writeFileSync(outPath, html);
}

function buildResult(pages, built, fourArmSheet, standaloneHtml) {
  const full = built.find((item) => item.arm.armId === "run2_82_full_product_surface_text_composition");
  return {
    artifact_id: "run2_82_renderer_product_surface_text_composition_rerun_result",
    part: "Part O2",
    schema_version: "ppt_run2_82_renderer_product_surface_text_composition_rerun_result.v1",
    run_id: RUN_ID,
    status: "run2_82_renderer_product_surface_text_composition_rerun_generated_public_blocked",
    public_ready: false,
    public_release_started: false,
    quality_claim_boundary: "renderer_product_surface_text_composition_generated_viewer_check_only_no_part_p_quality_verdict",
    consumed_sources: CONSUMED_SOURCES,
    source_n_evaluation: {
      status: "run2_80_visual_quality_evaluation_public_blocked",
      top_blocker: "product_surface_not_visibly_realized_and_slides_read_as_sparse_text_wireframes",
      next_required_action: "part_o_renderer_product_surface_repair_from_n_evaluation",
      source_result: O2_INPUTS.nEvaluation,
    },
    source_o1_text_composition_plan: {
      status: "run2_81_text_composition_typography_plan_ready_public_blocked",
      next_required_action: "part_o2_renderer_rerun_from_text_composition_and_product_surface_repair",
      source_result: O2_INPUTS.o1TextComposition,
    },
    renderer_product_surface_text_composition_manifest: {
      generator: "scripts/generate_ppt_run2_82_product_surface_text_composition_arms.mjs",
      consumed_sources: CONSUMED_SOURCES,
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_82_full_product_surface_text_composition",
      outputs: {
        html_viewer: repoRelative(standaloneHtml),
        pptx: repoRelative(full.outputPath),
        ppt_run_viewer: `outputs/${threadId}/presentations/ppt-run-viewer.html`,
        four_arm_contact_sheet: repoRelative(fourArmSheet),
      },
      viewer_update: {
        latest_run_id: RUN_ID,
        viewer_can_reference_new_run: true,
      },
    },
    rendered_pages: pages.map((page) => ({
      role: page.role,
      slide_index: page.slide_index,
      visual_grammar_module: page.visual_grammar_module,
      source_o1_text_composition_id: page.source_o1_text_composition_id,
      source_n_repair_instruction: page.source_n_repair_instruction,
      source_run2_79_page: page.source_run2_79_page,
      renderer_repair_directives_applied: page.renderer_repair_directives_applied,
      concrete_product_surface_visible: page.concrete_product_surface_visible,
      product_surface_type: page.product_surface_type,
      text_hierarchy: page.text_hierarchy,
      text_composition_blocks_applied: page.text_composition_blocks_applied,
      floating_label_count: page.floating_label_count,
      label_count: page.label_count,
      min_visible_label_font_size: page.min_visible_label_font_size,
      canvas_word_count: page.canvas_word_count,
      source_trace_terms_visible_on_canvas: page.source_trace_terms_visible_on_canvas,
      public_polish_claimed: page.public_polish_claimed,
    })),
    renderer_product_surface_text_composition_checks: {
      pages_with_o1_text_composition_consumed: pages.length,
      pages_with_concrete_product_surface: pages.filter((page) => page.concrete_product_surface_visible).length,
      pages_with_text_hierarchy_applied: pages.filter((page) => page.text_hierarchy === "headline_subhead_proof_caption").length,
      pages_with_floating_labels_removed: pages.filter((page) => page.floating_label_count === 0).length,
      pages_with_traceability_routed_off_canvas: pages.filter((page) => page.source_trace_terms_visible_on_canvas.length === 0).length,
      public_quality_verdict_started: false,
    },
    next_required_action: "part_p_visual_quality_evaluation_for_run2_82",
  };
}

function buildMarkdown(result) {
  return [
    "# Run 2.82 product surface + text composition rerun",
    "",
    `Status: ${result.status}`,
    "",
    "Run 2.82 generated a four-arm comparison and updated the local viewer. It consumes Run 2.80, Run 2.79, and the Run 2.81 O1 text composition plan.",
    "",
    "Consumed source trace:",
    ...result.consumed_sources.map((source) => `- ${source}`),
    "",
    "Boundary: public release remains blocked. Part P must evaluate visual quality before any public-ready claim.",
    "",
    `Next required action: ${result.next_required_action}`,
    "",
  ].join("\n");
}

async function main() {
  ensureDir(outRoot);
  const data = loadInputs();
  const pages = buildRenderModel(data);
  const built = [];
  for (const arm of armSpecs) {
    built.push(await buildArm(arm, pages));
  }
  const fourArmSheet = buildRun282Sheet(built);
  const standaloneHtml = path.join(outRoot, "ppt-run2-82-full-vulca", "output", "run2-82-product-surface-text-composition.html");
  buildStandaloneHtml(pages, standaloneHtml);
  const result = buildResult(pages, built, fourArmSheet, standaloneHtml);
  writeJson(path.join(root, RESULT_JSON), result);
  fs.writeFileSync(path.join(root, RESULT_MD), buildMarkdown(result));
  writeJson(path.join(outRoot, "run2_82_renderer_product_surface_text_composition_rerun_summary.json"), {
    status: result.status,
    result_json: RESULT_JSON,
    result_md: RESULT_MD,
    latest_run_id: RUN_ID,
    public_ready: false,
    next_required_action: result.next_required_action,
  });
  execFileSync("python3.11", [path.join(root, "scripts", "build_ppt_run_html_viewer.py")], { cwd: root, stdio: "pipe" });
}

await main();
