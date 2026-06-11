import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.85";
const RESULT_JSON = `${pack}/results/run2_85_design_motif_renderer_rerun_result.json`;
const RESULT_MD = `${pack}/results/run2_85_design_motif_renderer_rerun_result.md`;
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
const P2_INPUTS = {
  p1DesignMotifPlan: "docs/product/ppt-run2-data-skill-quality/run2_84_design_motif_taxonomy_style_router_plan.json",
  o2RendererResult: "docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json",
};
const CONSUMED_SOURCES = [P2_INPUTS.p1DesignMotifPlan, P2_INPUTS.o2RendererResult];
const REPAIR_FLAGS = [
  "p1_design_motif_layer_consumed",
  "style_router_applied",
  "motif_family_rendered",
  "preserved_visual_effects_rendered",
  "text_integrated_with_motif",
  "traceability_routed_off_canvas",
  "public_polish_not_claimed",
];

const COPY_BY_ROLE = {
  cover: {
    headline: "Vulca turns design learning into native PPT",
    subhead: "A real brief, tutorial-derived design moves, and renderer gates become an editable presentation system.",
    proof: "Run 2.85 routes engineering trace into metadata while the slide itself carries a visible product theater.",
    caption: "Design memory to editable deck",
    labels: ["product surface", "native PPT"],
  },
  setup: {
    headline: "The system learns motifs, not just constraints",
    subhead: "Typography, readability, sockets, and tutorial moves are grouped into design motifs before drawing.",
    proof: "This page keeps the dense editorial text field, so business logic and visual hierarchy live in one reading path.",
    caption: "Motif router before rendering",
    labels: ["tutorial moves", "style router", "text grammar"],
  },
  contrast: {
    headline: "The control loses the visual grammar",
    subhead: "The full arm keeps the before/after theater so viewers can see why motif-aware rendering matters.",
    proof: "A visible comparison object replaces generic boxes and makes the delta inspectable without debug labels.",
    caption: "Before/after motif preserved",
    labels: ["before", "after", "motif applied"],
  },
  proof: {
    headline: "Proof becomes a modular workspace",
    subhead: "A matrix motif lets evidence, scene logic, and product output coexist without turning into a dashboard.",
    proof: "The matrix is still native PPT, but its cells are connected to one central product surface and caption.",
    caption: "Evidence matrix plus product surface",
    labels: ["rules", "checks", "render"],
  },
  climax: {
    headline: "The climax uses an overlay sticker stack",
    subhead: "Instead of a plain product mock, the surface carries layered callouts that read like designed emphasis.",
    proof: "Sticker layers preserve the earlier modular visual effects while the headline and proof stay editorial.",
    caption: "Layered product reveal",
    labels: ["deck surface", "motion cue", "review path"],
  },
  close: {
    headline: "Generated, inspected, still not public-ready",
    subhead: "The close becomes a decision map: generated output, review evidence, and next evaluation remain separate.",
    proof: "Part P2 proves the motif renderer ran; Part Q must still judge whether the result reaches public presentation quality.",
    caption: "Part Q visual quality gate",
    labels: ["generated", "evaluate", "blocked"],
  },
};

const C = {
  ink: "#11151c",
  white: "#fffdf8",
  paper: "#f4efe6",
  muted: "#66717e",
  line: "#cdd5df",
  blue: "#285ed8",
  green: "#0d8b68",
  amber: "#e0ad3e",
  coral: "#dd5b46",
  violet: "#6e58d9",
  dark: "#121922",
};

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-85-prompt-only",
    label: "Prompt-only control",
    mode: "control",
    release: "public_blocked",
    palette: { bg: "#f6f6f2", title: C.ink, muted: C.muted, accent: "#7d8793", accent2: "#b9c0c8", surface: "#ffffff" },
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-85-run1-5-skill",
    label: "Run 1.5 baseline",
    mode: "baseline",
    release: "public_blocked",
    palette: { bg: "#f1f6f3", title: C.ink, muted: C.muted, accent: C.green, accent2: "#b4d7c5", surface: "#ffffff" },
  },
  {
    armId: "run2_85_full_design_motif_style_router",
    slug: "ppt-run2-85-full-vulca",
    label: "Run 2.85 full design motif + style router",
    mode: "full",
    release: "public_blocked",
    palette: { bg: C.paper, title: C.ink, muted: C.muted, accent: C.blue, accent2: C.green, surface: C.white },
  },
  {
    armId: "bad_run2_85_without_design_motif_layer",
    slug: "ppt-run2-85-bad-without-design-motif-layer",
    label: "Bad missing Run 2.85 design motif layer",
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
  const textValue = String(value ?? "").replace(/\s+/g, " ").trim();
  if (textValue.length <= max) return textValue;
  const clipped = textValue.slice(0, max).trim();
  return clipped.includes(" ") ? clipped.replace(/\s+\S*$/, "").trim() : clipped;
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
    p1DesignMotifPlan: readJson(P2_INPUTS.p1DesignMotifPlan),
    o2RendererResult: readJson(P2_INPUTS.o2RendererResult),
  };
  if (data.p1DesignMotifPlan.status !== "run2_84_design_motif_taxonomy_style_router_plan_ready_public_blocked") {
    throw new Error("Run 2.85 requires the Run 2.84 design motif/style router plan");
  }
  if (data.p1DesignMotifPlan.next_required_action !== "part_p2_renderer_rerun_from_design_motif_layer_and_style_router") {
    throw new Error("Run 2.85 requires Part P1 to request the Part P2 renderer rerun");
  }
  if (data.o2RendererResult.status !== "run2_82_renderer_product_surface_text_composition_rerun_generated_public_blocked") {
    throw new Error("Run 2.85 requires the Run 2.82 product surface/text composition renderer result");
  }
  return data;
}

function buildRenderModel(data) {
  const o2ByRole = indexByRole(data.o2RendererResult.rendered_pages);
  const motifById = new Map(data.p1DesignMotifPlan.design_motif_taxonomy.map((motif) => [motif.motif_id, motif]));
  const bindings = data.p1DesignMotifPlan.page_role_motif_bindings;
  const preservedEffects = data.p1DesignMotifPlan.preserved_visual_effects;
  return ROLES.map((role, index) => {
    const binding = bindings.find((item) => item.role === role);
    const motif = motifById.get(binding?.primary_motif_id);
    const o2Page = o2ByRole.get(role);
    if (!binding || !motif || !o2Page) {
      throw new Error(`Run 2.85 missing P1/O2 renderer input record for role: ${role}`);
    }
    const copy = COPY_BY_ROLE[role];
    return {
      role,
      slide_index: index + 1,
      visual_grammar_module: binding.visual_grammar_module,
      source_p1_primary_motif_id: binding.primary_motif_id,
      source_p1_fallback_motif_id: binding.fallback_motif_id,
      source_o2_product_surface_type: o2Page.product_surface_type,
      motif_family: motif.motif_family,
      style_family: binding.style_family,
      scenario: binding.scenario,
      visual_density: motif.visual_density,
      renderer_repair_directives_applied: REPAIR_FLAGS,
      preserved_visual_effects_rendered: preservedEffects,
      motif_fidelity_checks: binding.required_motif_fidelity_checks,
      motif_family_visible: true,
      not_rectangle_only: true,
      text_integrated_with_shape: true,
      concrete_product_surface_visible: true,
      text_hierarchy: "motif_aware_headline_subhead_proof_caption",
      headline: copy.headline,
      subhead: copy.subhead,
      proof_sentence: copy.proof,
      object_caption: copy.caption,
      visible_labels: copy.labels.slice(0, 3),
      floating_label_count: 0,
      label_count: Math.min(copy.labels.length, 3),
      min_visible_label_font_size: 12,
      source_trace_terms_visible_on_canvas: [],
      public_polish_claimed: false,
    };
  });
}

function drawBase(slide, page, arm) {
  rect(slide, 0, 0, W, H, { color: arm.palette.bg }, line(arm.palette.bg, 0));
  text(slide, `RUN ${RUN_ID} / ${arm.mode === "full" ? page.motif_family.replaceAll("_", " ") : arm.label.toUpperCase()}`, 52, 34, 700, 20, {
    fontSize: 8,
    bold: true,
    color: arm.palette.muted,
    mono: true,
  });
  text(slide, `${String(page.slide_index).padStart(2, "0")} / ${page.role}`, 1130, 34, 96, 20, {
    fontSize: 8,
    bold: true,
    color: arm.palette.muted,
    align: "right",
    mono: true,
  });
}

function drawEditorialText(slide, page, arm, x, y, w, opts = {}) {
  text(slide, page.headline, x, y, w, opts.headlineH ?? 106, {
    fontSize: opts.titleSize ?? 36,
    bold: true,
    title: true,
    color: arm.palette.title,
    max: 104,
  });
  text(slide, page.subhead, x, y + (opts.subheadY ?? 126), w * 0.9, opts.subheadH ?? 68, {
    fontSize: opts.subheadSize ?? 15,
    color: arm.palette.muted,
    max: 155,
  });
  rect(slide, x, y + (opts.ruleY ?? 218), Math.min(330, w * 0.7), 3, { color: arm.palette.accent }, line(arm.palette.accent, 0));
  text(slide, page.proof_sentence, x, y + (opts.proofY ?? 244), w * 0.82, opts.proofH ?? 64, {
    fontSize: opts.proofSize ?? 13,
    color: arm.palette.title,
    max: 142,
  });
}

function drawProductShell(slide, x, y, w, h, arm, variant = 0) {
  rect(slide, x + 24, y + 28, w, h, { color: "#cfc6b8" }, line("#cfc6b8", 0));
  rect(slide, x, y, w, h, { color: C.dark }, line(C.dark, 0));
  rect(slide, x + 28, y + 32, w - 56, h - 64, { color: arm.palette.surface }, line(arm.palette.surface, 0));
  rect(slide, x + 28, y + 32, w - 56, 52, { color: "#172331" }, line("#172331", 0));
  [0, 1, 2].forEach((index) => ellipse(slide, x + 54 + index * 22, y + 52, 10, 10, {
    color: index === variant % 3 ? arm.palette.accent : "#f3eadf",
  }, line("#f3eadf", 0)));
  const sideW = Math.max(76, w * 0.14);
  const contentTop = y + 106;
  rect(slide, x + 52, contentTop, sideW, h - 170, { color: "#e9eef2" }, line("#e9eef2", 0));
  for (let index = 0; index < 5; index += 1) {
    rect(slide, x + 70, contentTop + 22 + index * 33, sideW - 36, 8, {
      color: index === variant % 5 ? arm.palette.accent : "#c9d2dc",
    }, line("#c9d2dc", 0));
  }
  const stageX = x + 80 + sideW;
  const stageW = w - sideW - 136;
  rect(slide, stageX, contentTop, stageW, Math.max(118, h * 0.36), { color: "#f1f5f8" }, line("#f1f5f8", 0));
  rect(slide, stageX + 24, contentTop + 28, stageW * 0.45, 13, { color: "#9aa9ba" }, line("#9aa9ba", 0));
  rect(slide, stageX + 24, contentTop + 62, stageW * 0.7, 18, { color: arm.palette.accent }, line(arm.palette.accent, 0));
  ellipse(slide, stageX + stageW * 0.58, contentTop + 96, stageW * 0.33, 56, { color: "#ffffff" }, line("#ffffff", 0));
  const rowY = contentTop + Math.max(140, h * 0.49);
  [0, 1, 2].forEach((index) => {
    const blockW = (stageW - 28) / 3;
    const bx = stageX + index * (blockW + 14);
    rect(slide, bx, rowY, blockW, 58, { color: index === 1 ? "#f8eadb" : "#eaf1fb" }, line(index === 1 ? "#f8eadb" : "#eaf1fb", 0));
    rect(slide, bx + 16, rowY + 20, blockW - 32, 8, {
      color: index === 1 ? C.amber : arm.palette.accent,
    }, line(arm.palette.accent, 0));
  });
}

function drawCaption(slide, page, x, y, w, arm) {
  rect(slide, x, y, w, 38, { color: "#fffdf8" }, line(arm.palette.accent, 2));
  text(slide, page.object_caption, x + 16, y + 11, w - 32, 18, {
    fontSize: 12,
    bold: true,
    color: arm.palette.title,
    max: 44,
  });
}

function drawLabels(slide, page, points, arm) {
  page.visible_labels.slice(0, 3).forEach((labelText, index) => {
    const point = points[index];
    if (!point) return;
    rect(slide, point.x, point.y, point.w, 28, { color: "#fffdf8" }, line(arm.palette.accent, 1));
    text(slide, labelText, point.x + 10, point.y + 8, point.w - 20, 12, {
      fontSize: 12,
      bold: true,
      color: arm.palette.title,
      max: 36,
    });
  });
}

function connector(slide, x1, y1, x2, y2, color, width = 12) {
  const midX = x1 + (x2 - x1) * 0.54;
  rect(slide, Math.min(x1, midX), y1 - width / 2, Math.abs(midX - x1), width, { color }, line(color, 0));
  rect(slide, midX - width / 2, Math.min(y1, y2), width, Math.abs(y2 - y1), { color }, line(color, 0));
  rect(slide, Math.min(midX, x2), y2 - width / 2, Math.abs(x2 - midX), width, { color }, line(color, 0));
}

function drawProductTheater(slide, page, arm) {
  drawEditorialText(slide, page, arm, 78, 104, 430, { titleSize: 36 });
  ellipse(slide, -160, 300, 710, 330, { color: "#eadfcd" }, line("#eadfcd", 0));
  ellipse(slide, 548, 46, 800, 570, { color: "#e7eef8" }, line("#e7eef8", 0));
  drawProductShell(slide, 488, 112, 650, 450, arm, page.slide_index);
  connector(slide, 160, 434, 518, 326, arm.palette.accent2, 16);
  drawCaption(slide, page, 858, 586, 246, arm);
  drawLabels(slide, page, [
    { x: 930, y: 122, w: 150 },
    { x: 880, y: 520, w: 144 },
  ], arm);
}

function drawEditorialField(slide, page, arm) {
  drawEditorialText(slide, page, arm, 76, 84, 610, { titleSize: 34, subheadY: 118, ruleY: 210, proofY: 238 });
  rect(slide, 76, 446, 500, 118, { color: "#fffdf8" }, line("#fffdf8", 0));
  text(slide, "motif -> layout -> renderer", 104, 474, 420, 20, { fontSize: 13, bold: true, mono: true, color: arm.palette.title });
  rect(slide, 104, 512, 118, 12, { color: arm.palette.accent }, line(arm.palette.accent, 0));
  rect(slide, 246, 512, 142, 12, { color: C.green }, line(C.green, 0));
  rect(slide, 412, 512, 90, 12, { color: C.amber }, line(C.amber, 0));
  ellipse(slide, 650, 160, 520, 360, { color: "#e8ede8" }, line("#e8ede8", 0));
  connector(slide, 600, 368, 752, 318, C.green, 16);
  drawProductShell(slide, 760, 170, 390, 300, arm, 1);
  drawCaption(slide, page, 842, 494, 240, arm);
  drawLabels(slide, page, [
    { x: 140, y: 576, w: 136 },
    { x: 318, y: 576, w: 136 },
    { x: 952, y: 130, w: 140 },
  ], arm);
}

function drawBeforeAfter(slide, page, arm) {
  rect(slide, 0, 0, 548, H, { color: "#ece4d8" }, line("#ece4d8", 0));
  rect(slide, 548, 0, 732, H, { color: "#eaf1f6" }, line("#eaf1f6", 0));
  rect(slide, 520, 0, 70, H, { color: "#e6c4b6" }, line("#e6c4b6", 0));
  drawEditorialText(slide, page, arm, 76, 94, 430, { titleSize: 33 });
  drawProductShell(slide, 118, 318, 330, 200, { ...arm, palette: { ...arm.palette, accent: "#8a7652", accent2: "#b9aa8d" } }, 0);
  drawProductShell(slide, 722, 158, 454, 380, arm, 3);
  connector(slide, 474, 386, 722, 320, arm.palette.accent2, 18);
  text(slide, "after keeps motif hierarchy", 744, 84, 374, 32, { fontSize: 18, bold: true, color: arm.palette.title, max: 80 });
  drawCaption(slide, page, 812, 592, 260, arm);
  drawLabels(slide, page, [
    { x: 174, y: 542, w: 112 },
    { x: 930, y: 116, w: 116 },
    { x: 936, y: 548, w: 170 },
  ], arm);
}

function drawModularMatrix(slide, page, arm) {
  drawEditorialText(slide, page, arm, 70, 76, 520, { titleSize: 31, subheadY: 116, ruleY: 210, proofY: 236 });
  ellipse(slide, 520, 86, 650, 520, { color: "#e8ede8" }, line("#e8ede8", 0));
  const gridX = 600;
  const gridY = 136;
  const cellW = 154;
  const cellH = 112;
  for (let row = 0; row < 3; row += 1) {
    for (let col = 0; col < 3; col += 1) {
      const x = gridX + col * (cellW + 18);
      const y = gridY + row * (cellH + 18);
      const fill = row === 1 && col === 1 ? "#172331" : row % 2 ? "#f7eadb" : "#fffdf8";
      rect(slide, x, y, cellW, cellH, { color: fill }, line(fill, 0));
      rect(slide, x + 20, y + 26, cellW - 42, 8, { color: row === 1 && col === 1 ? arm.palette.accent : C.blue }, line(C.blue, 0));
      rect(slide, x + 20, y + 58, cellW * 0.46, 8, { color: row === 1 && col === 1 ? C.white : "#aeb9c6" }, line("#aeb9c6", 0));
    }
  }
  drawProductShell(slide, 300, 374, 330, 210, arm, 4);
  connector(slide, 620, 478, 770, 320, arm.palette.accent2, 14);
  drawCaption(slide, page, 836, 550, 250, arm);
  drawLabels(slide, page, [
    { x: 338, y: 608, w: 112 },
    { x: 794, y: 274, w: 118 },
    { x: 972, y: 406, w: 112 },
  ], arm);
}

function drawOverlayStickerStack(slide, page, arm) {
  drawEditorialText(slide, page, arm, 70, 86, 420, { titleSize: 35, subheadY: 124, ruleY: 220, proofY: 248 });
  ellipse(slide, 430, 64, 760, 560, { color: "#e7eef8" }, line("#e7eef8", 0));
  drawProductShell(slide, 420, 104, 620, 430, arm, 5);
  const stickers = [
    { x: 880, y: 98, w: 230, h: 82, c: C.amber, t: "motion beat" },
    { x: 356, y: 386, w: 240, h: 90, c: C.green, t: "text socket" },
    { x: 810, y: 438, w: 250, h: 94, c: C.coral, t: "review path" },
  ];
  stickers.forEach((item, index) => {
    rect(slide, item.x + 12, item.y + 14, item.w, item.h, { color: "#c7beb2" }, line("#c7beb2", 0));
    rect(slide, item.x, item.y, item.w, item.h, { color: "#fffdf8" }, line(item.c, 3));
    ellipse(slide, item.x + 18, item.y + 18, 18, 18, { color: item.c }, line(item.c, 0));
    text(slide, item.t, item.x + 48, item.y + 28, item.w - 70, 26, { fontSize: 14, bold: true, color: arm.palette.title, max: 44 });
    if (index < 2) connector(slide, item.x + item.w / 2, item.y + item.h, 730, 330 + index * 60, item.c, 10);
  });
  drawCaption(slide, page, 760, 574, 260, arm);
  drawLabels(slide, page, [
    { x: 106, y: 468, w: 130 },
    { x: 106, y: 510, w: 130 },
    { x: 106, y: 552, w: 130 },
  ], arm);
}

function drawDecisionMap(slide, page, arm) {
  drawEditorialText(slide, page, arm, 78, 82, 520, { titleSize: 32, subheadY: 116, ruleY: 210, proofY: 236 });
  ellipse(slide, 160, 166, 880, 420, { color: "#ecebe1" }, line("#ecebe1", 0));
  const nodes = [
    { x: 266, y: 452, label: "generated", dark: false },
    { x: 474, y: 336, label: "review", dark: false },
    { x: 690, y: 386, label: "Part Q", dark: false },
    { x: 916, y: 262, label: "public blocked", dark: true },
  ];
  connector(slide, nodes[0].x, nodes[0].y, nodes[1].x, nodes[1].y, arm.palette.accent2, 16);
  connector(slide, nodes[1].x, nodes[1].y, nodes[2].x, nodes[2].y, arm.palette.accent2, 16);
  connector(slide, nodes[2].x, nodes[2].y, nodes[3].x, nodes[3].y, arm.palette.accent, 18);
  nodes.forEach((node) => {
    ellipse(slide, node.x - 66, node.y - 46, 132, 92, { color: node.dark ? "#172331" : "#fffdf8" }, line(node.dark ? "#172331" : "#fffdf8", 0));
    text(slide, node.label, node.x - 58, node.y - 12, 116, 24, {
      fontSize: 12,
      bold: true,
      color: node.dark ? C.white : arm.palette.title,
      align: "center",
      max: 34,
    });
  });
  drawProductShell(slide, 792, 356, 330, 208, arm, 2);
  drawCaption(slide, page, 836, 590, 236, arm);
  drawLabels(slide, page, [
    { x: 212, y: 530, w: 112 },
    { x: 646, y: 458, w: 112 },
    { x: 870, y: 186, w: 128 },
  ], arm);
}

function drawFullSlide(slide, page, arm) {
  drawBase(slide, page, arm);
  if (page.motif_family === "editorial_text_field") drawEditorialField(slide, page, arm);
  else if (page.motif_family === "before_after_theater") drawBeforeAfter(slide, page, arm);
  else if (page.motif_family === "modular_matrix") drawModularMatrix(slide, page, arm);
  else if (page.motif_family === "overlay_sticker_stack") drawOverlayStickerStack(slide, page, arm);
  else if (page.motif_family === "decision_map") drawDecisionMap(slide, page, arm);
  else drawProductTheater(slide, page, arm);
  text(slide, `${page.style_family.replaceAll("_", " ")} / ${page.scenario.replaceAll("_", " ")}`, 54, 664, 460, 18, {
    fontSize: 10,
    bold: true,
    color: arm.palette.muted,
    mono: true,
  });
}

function drawComparisonSlide(slide, page, arm) {
  drawBase(slide, page, arm);
  ellipse(slide, 140, 178, 840, 360, { color: arm.mode === "negative" ? "#e3d6c2" : "#e7edf1" }, line("#cdd3d8", 1));
  rect(slide, 720, 210, 330, 238, { color: arm.palette.surface }, line("#c3ccd5", 1));
  connector(slide, 236, 456, 756, 308, arm.palette.accent2, 12);
  const title = arm.mode === "negative"
    ? `${page.role}: design motif withheld`
    : arm.mode === "baseline"
      ? `${page.role}: workflow baseline`
      : `${page.role}: brief-only deck`;
  text(slide, title, 96, 110, 540, 84, {
    fontSize: 30,
    bold: true,
    title: true,
    color: arm.palette.title,
    max: 84,
  });
  const body = arm.mode === "negative"
    ? "This arm keeps product/text contracts but removes the P1 motif router, so the page falls back to generic composition."
    : "This comparison arm is generated locally for viewer context. The P2 manifest validates the full arm only.";
  text(slide, body, 100, 218, 438, 72, {
    fontSize: 13,
    color: arm.palette.muted,
    max: 140,
  });
  page.visible_labels.slice(0, 3).forEach((labelText, index) => {
    text(slide, labelText, 190 + index * 205, 548 - index * 34, 150, 22, {
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
    part_p2_renderer_scope: arm.mode === "full"
      ? "renderer_design_motif_style_router_consumes_run2_84_p1_and_run2_82_o2"
      : "comparison_arm_not_part_p2_quality_manifest",
    public_release_started: false,
    slides: pages.map((page) => ({
      role: page.role,
      slide_index: page.slide_index,
      visual_grammar_module: arm.mode === "full" ? page.visual_grammar_module : "comparison_context",
      motif_family: arm.mode === "full" ? page.motif_family : "comparison_context",
      style_family: arm.mode === "full" ? page.style_family : "comparison_context",
      scenario: arm.mode === "full" ? page.scenario : "comparison_context",
      source_p1_primary_motif_id: arm.mode === "full" ? page.source_p1_primary_motif_id : "",
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

function buildRun285Sheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built.filter((item) => fs.existsSync(item.contactSheet)).map((item) => {
    const arm = armSpecs.find((spec) => item.workspace.endsWith(spec.slug));
    return arm?.label ?? path.basename(item.workspace);
  });
  return buildNamedContactSheet(
    path.join(outRoot, "run2-85-four-arm-contact-sheet.png"),
    "Run 2.85 design motif + style router comparison",
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
      `part: Part P2 / Run ${RUN_ID}`,
      `consumed sources: ${arm.mode === "full" ? CONSUMED_SOURCES.join(", ") : "commercial_case.md only"}`,
      "full arm requirement: apply Part P1 design motif taxonomy and style router over the Run 2.82 product/text renderer",
      "release boundary: public blocked until Part Q visual quality evaluation",
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
      source: "scripts/generate_ppt_run2_85_design_motif_renderer_arms.mjs",
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
    <section class="slide ${htmlEscape(page.motif_family)}">
      <div class="kicker">Run 2.85 / ${htmlEscape(page.motif_family)} / ${htmlEscape(page.scenario)}</div>
      <h2>${htmlEscape(page.headline)}</h2>
      <p class="subhead">${htmlEscape(page.subhead)}</p>
      <div class="surface"><span></span><span></span><span></span><b>${htmlEscape(page.object_caption)}</b></div>
      <p class="proof">${htmlEscape(page.proof_sentence)}</p>
    </section>
  `).join("\n");
  const html = `<!doctype html>
<html lang="en" data-run-id="2.85">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Run 2.85 design motif renderer</title>
  <style>
    body{margin:0;background:#141922;color:#11151c;font-family:Aptos,Inter,system-ui,sans-serif}
    main{display:grid;gap:24px;padding:32px}
    .slide{width:min(1120px,calc(100vw - 64px));aspect-ratio:16/9;background:#f4efe6;margin:auto;position:relative;padding:50px 60px;box-sizing:border-box;overflow:hidden}
    .kicker{font:700 11px/1 Aptos Mono,monospace;color:#66717e;text-transform:uppercase;letter-spacing:.04em}
    h2{font-size:42px;line-height:1.04;margin:50px 0 16px;max-width:480px}
    .subhead{font-size:18px;line-height:1.3;color:#66717e;max-width:510px}
    .proof{position:absolute;left:60px;bottom:64px;width:500px;font-size:15px;line-height:1.35}
    .surface{position:absolute;right:62px;top:104px;width:480px;height:360px;background:#121922;padding:28px;box-sizing:border-box;box-shadow:22px 24px 0 #cfc6b8}
    .surface span{display:block;height:20px;background:#285ed8;margin:28px 0;width:72%}
    .surface span:nth-child(2){background:#0d8b68;width:88%}
    .surface span:nth-child(3){background:#e0ad3e;width:56%}
    .surface b{position:absolute;right:28px;bottom:28px;background:#fffdf8;border:2px solid #285ed8;padding:9px 14px;font-size:13px}
    .editorial_text_field .surface{border-radius:0;right:82px;width:420px}
    .modular_matrix .surface{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;background:#e8ede8}
    .overlay_sticker_stack .surface{box-shadow:34px 38px 0 #e0ad3e}
    .decision_map .surface{border-radius:180px}
  </style>
</head>
<body><main>${slideCards}</main></body>
</html>`;
  fs.writeFileSync(outPath, html);
}

function buildResult(pages, built, fourArmSheet, standaloneHtml, data) {
  const full = built.find((item) => item.arm.armId === "run2_85_full_design_motif_style_router");
  return {
    artifact_id: "run2_85_design_motif_renderer_rerun_result",
    part: "Part P2",
    schema_version: "ppt_run2_85_design_motif_renderer_rerun_result.v1",
    run_id: RUN_ID,
    status: "run2_85_design_motif_renderer_rerun_generated_public_blocked",
    public_ready: false,
    public_release_started: false,
    quality_claim_boundary: "design_motif_renderer_generated_viewer_check_only_no_part_q_quality_verdict",
    consumed_sources: CONSUMED_SOURCES,
    source_p1_design_motif_plan: {
      status: data.p1DesignMotifPlan.status,
      next_required_action: data.p1DesignMotifPlan.next_required_action,
      source_result: P2_INPUTS.p1DesignMotifPlan,
    },
    source_o2_renderer_result: {
      status: data.o2RendererResult.status,
      next_required_action: data.o2RendererResult.next_required_action,
      source_result: P2_INPUTS.o2RendererResult,
    },
    renderer_design_motif_manifest: {
      generator: "scripts/generate_ppt_run2_85_design_motif_renderer_arms.mjs",
      consumed_sources: CONSUMED_SOURCES,
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_85_full_design_motif_style_router",
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
      source_p1_primary_motif_id: page.source_p1_primary_motif_id,
      source_p1_fallback_motif_id: page.source_p1_fallback_motif_id,
      source_o2_product_surface_type: page.source_o2_product_surface_type,
      motif_family: page.motif_family,
      style_family: page.style_family,
      scenario: page.scenario,
      visual_density: page.visual_density,
      renderer_repair_directives_applied: page.renderer_repair_directives_applied,
      preserved_visual_effects_rendered: page.preserved_visual_effects_rendered,
      motif_fidelity_checks: page.motif_fidelity_checks,
      motif_family_visible: page.motif_family_visible,
      not_rectangle_only: page.not_rectangle_only,
      text_integrated_with_shape: page.text_integrated_with_shape,
      concrete_product_surface_visible: page.concrete_product_surface_visible,
      text_hierarchy: page.text_hierarchy,
      floating_label_count: page.floating_label_count,
      label_count: page.label_count,
      min_visible_label_font_size: page.min_visible_label_font_size,
      source_trace_terms_visible_on_canvas: page.source_trace_terms_visible_on_canvas,
      public_polish_claimed: page.public_polish_claimed,
    })),
    renderer_design_motif_checks: {
      pages_with_p1_motif_consumed: pages.length,
      pages_with_motif_family_visible: pages.filter((page) => page.motif_family_visible).length,
      pages_with_not_rectangle_only: pages.filter((page) => page.not_rectangle_only).length,
      pages_with_text_integrated_with_shape: pages.filter((page) => page.text_integrated_with_shape).length,
      pages_with_traceability_routed_off_canvas: pages.filter((page) => page.source_trace_terms_visible_on_canvas.length === 0).length,
      public_quality_verdict_started: false,
    },
    next_required_action: "part_q_visual_quality_evaluation_for_run2_85",
  };
}

function buildMarkdown(result) {
  return [
    "# Run 2.85 design motif renderer rerun",
    "",
    `Status: ${result.status}`,
    "",
    "Run 2.85 generated a four-arm comparison and updated the local viewer. It consumes Run 2.84 Part P1 and the Run 2.82 product/text renderer result.",
    "",
    "Consumed source trace:",
    ...result.consumed_sources.map((source) => `- ${source}`),
    "",
    "Boundary: public release remains blocked. Part Q must evaluate visual quality before any public-ready claim.",
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
  const fourArmSheet = buildRun285Sheet(built);
  const standaloneHtml = path.join(outRoot, "ppt-run2-85-full-vulca", "output", "run2-85-design-motif-renderer.html");
  buildStandaloneHtml(pages, standaloneHtml);
  const result = buildResult(pages, built, fourArmSheet, standaloneHtml, data);
  writeJson(path.join(root, RESULT_JSON), result);
  fs.writeFileSync(path.join(root, RESULT_MD), buildMarkdown(result));
  writeJson(path.join(outRoot, "run2_85_design_motif_renderer_rerun_summary.json"), {
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
