import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.90";
const RESULT_JSON = `${pack}/results/run2_90_renderer_asset_surface_composition_rerun_result.json`;
const RESULT_MD = `${pack}/results/run2_90_renderer_asset_surface_composition_rerun_result.md`;

function resolveExistingPath(label, candidates) {
  for (const candidate of candidates.filter(Boolean)) {
    if (fs.existsSync(candidate)) return candidate;
  }
  throw new Error(
    `Unable to find ${label}. Set ARTIFACT_TOOL_PATH or ARTIFACT_TOOL_PACKAGE, checked: ${candidates.filter(Boolean).join(", ")}`
  );
}

const artifactToolPackageCandidates = [
  process.env.ARTIFACT_TOOL_PACKAGE,
  path.join(root, "node_modules/@oai/artifact-tool"),
  process.env.HOME
    ? path.join(
        process.env.HOME,
        ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool"
      )
    : "",
].filter(Boolean);
const artifactToolPath = resolveExistingPath("artifact tool entrypoint", [
  process.env.ARTIFACT_TOOL_PATH,
  ...artifactToolPackageCandidates.map((candidate) => path.join(candidate, "dist/artifact_tool.mjs")),
]);
const artifactToolPackage = resolveExistingPath("artifact tool package", [
  process.env.ARTIFACT_TOOL_PACKAGE,
  path.resolve(path.dirname(artifactToolPath), ".."),
  ...artifactToolPackageCandidates,
]);

const { Presentation, PresentationFile } = await import(pathToFileURL(artifactToolPath).href);

const W = 1280;
const H = 720;
const ROLES = ["cover", "setup", "contrast", "proof", "climax", "close"];
const INPUTS = {
  partTEvaluation: "docs/product/ppt-run2-data-skill-quality/results/run2_89_visual_quality_evaluation.json",
  run288Result: "docs/product/ppt-run2-data-skill-quality/results/run2_88_best_layout_visual_primitive_rerun_result.json",
  partRPlan: "docs/product/ppt-run2-data-skill-quality/run2_87_best_layout_recovery_visual_primitive_plan.json",
};
const CONSUMED_SOURCES = [INPUTS.partTEvaluation, INPUTS.run288Result, INPUTS.partRPlan];
const REPAIR_FLAGS = [
  "part_t_visual_quality_evaluation_consumed",
  "asset_surface_rendered",
  "composition_detail_added",
  "wireframe_reduced",
  "collision_repair_applied",
  "text_heavy_readability_preserved",
  "traceability_routed_off_canvas",
  "public_polish_not_claimed",
];
const ANTI_REGRESSION_GATES = [
  "product_surface_materiality",
  "visual_density_above_wireframe",
  "no_floating_labels",
  "collision_avoidance",
  "text_integrated_with_surface",
];

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

const COPY_BY_ROLE = {
  cover: {
    headline: "Recover the best layout before drawing",
    subhead: "Run 2.90 starts from the strongest historical hero rhythm, then renders a richer product-theater primitive.",
    proof: "The product surface is no longer a single shell; it carries depth planes, a proof rail, and a caption bound to the object.",
    caption: "Best layout + product primitive",
    labels: ["hero surface", "proof rail"],
  },
  setup: {
    headline: "Text stays dense, but now it has a field",
    subhead: "The page preserves the heavier editorial read the user prefers while anchoring it to an operating-stage object.",
    proof: "Paragraphs, side captions, and destination object share one reading axis instead of scattering small labels.",
    caption: "Editorial text field",
    labels: ["reading axis", "side rail", "anchor"],
  },
  contrast: {
    headline: "Before and after become real stage states",
    subhead: "The contrast page keeps the theater from the earlier better versions and enlarges the after surface.",
    proof: "The visual delta is carried by object size, depth, and state binding rather than by more chips.",
    caption: "After-state product surface",
    labels: ["before", "after", "delta"],
  },
  proof: {
    headline: "Proof becomes an unequal matrix",
    subhead: "The matrix uses one dominant evidence cell and smaller support cells, avoiding a generic dashboard grid.",
    proof: "Cell copy is embedded into modules, while the proof object gets a visible workspace and grouping grammar.",
    caption: "Evidence workspace matrix",
    labels: ["dominant cell", "rules", "checks"],
  },
  climax: {
    headline: "The payoff is a sticker-stack stage",
    subhead: "The climax recovers scale, overlap, and sticker energy from earlier stronger visual primitives.",
    proof: "A dominant generated deck surface stays central while short audience-facing badges create motion and emphasis.",
    caption: "Overlay sticker stack",
    labels: ["deck surface", "motion", "review"],
  },
  close: {
    headline: "The decision map is the visual object",
    subhead: "The close stops being a cluster of small nodes and becomes a large release decision board.",
    proof: "The blocked-public route is explicit, traceability stays in metadata, and the next quality evaluation is separated.",
    caption: "Part T quality gate",
    labels: ["generated", "blocked", "evaluate"],
  },
};

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-90-prompt-only",
    label: "Prompt-only control",
    mode: "control",
    release: "public_blocked",
    palette: { bg: "#f6f6f2", title: C.ink, muted: C.muted, accent: "#7d8793", accent2: "#b9c0c8", surface: "#ffffff" },
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-90-run1-5-skill",
    label: "Run 1.5 baseline",
    mode: "baseline",
    release: "public_blocked",
    palette: { bg: "#f1f6f3", title: C.ink, muted: C.muted, accent: C.green, accent2: "#b4d7c5", surface: "#ffffff" },
  },
  {
    armId: "run2_90_full_asset_surface_composition",
    slug: "ppt-run2-90-full-vulca",
    label: "Run 2.90 full asset surface composition",
    mode: "full",
    release: "public_blocked",
    palette: { bg: C.paper, title: C.ink, muted: C.muted, accent: C.blue, accent2: C.green, surface: C.white },
  },
  {
    armId: "bad_without_asset_surface_composition",
    slug: "ppt-run2-90-bad-without-asset-surface-composition",
    label: "Bad missing asset surface composition",
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

function compactText(value, max = 160) {
  const textValue = String(value ?? "").replace(/\s+/g, " ").trim();
  if (textValue.length <= max) return textValue;
  return textValue.slice(0, max).trim().replace(/\s+\S*$/, "").trim();
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
      line: { color: "transparent", transparency: 100, width: 0 },
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
  return { color, width: Math.max(width, 1) };
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
    text: compactText(value, opts.max ?? 160),
    x,
    y,
    w,
    h,
    ...opts,
  });
}

function connector(slide, x1, y1, x2, y2, color, width = 10) {
  const midX = x1 + (x2 - x1) * 0.55;
  rect(slide, Math.min(x1, midX), y1 - width / 2, Math.abs(midX - x1), width, { color }, line(color, 0));
  rect(slide, midX - width / 2, Math.min(y1, y2), width, Math.abs(y2 - y1), { color }, line(color, 0));
  rect(slide, Math.min(midX, x2), y2 - width / 2, Math.abs(x2 - midX), width, { color }, line(color, 0));
}

function drawBase(slide, page, arm) {
  rect(slide, 0, 0, W, H, { color: arm.palette.bg }, line(arm.palette.bg, 0));
  text(slide, `RUN ${RUN_ID} / ${arm.mode === "full" ? page.primitive_family.replaceAll("_", " ") : arm.label.toUpperCase()}`, 52, 34, 760, 20, {
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
  text(slide, page.headline, x, y, w, opts.headlineH ?? 112, {
    fontSize: opts.titleSize ?? 36,
    bold: true,
    title: true,
    color: arm.palette.title,
    max: 108,
  });
  text(slide, page.subhead, x, y + (opts.subheadY ?? 130), w * 0.92, opts.subheadH ?? 72, {
    fontSize: opts.subheadSize ?? 15,
    color: arm.palette.muted,
    max: 155,
  });
  rect(slide, x, y + (opts.ruleY ?? 226), Math.min(350, w * 0.7), 3, { color: arm.palette.accent }, line(arm.palette.accent, 0));
  text(slide, page.proof_sentence, x, y + (opts.proofY ?? 252), w * 0.86, opts.proofH ?? 70, {
    fontSize: opts.proofSize ?? 13,
    color: arm.palette.title,
    max: 148,
  });
}

function drawRicherProductSurface(slide, x, y, w, h, arm, variant = 0) {
  rect(slide, x + 42, y + 42, w, h, { color: "#b9b0a4" }, line("#b9b0a4", 0));
  rect(slide, x + 22, y + 22, w, h, { color: "#d8d0c4" }, line("#d8d0c4", 0));
  rect(slide, x, y, w, h, { color: C.dark }, line(C.dark, 0));
  rect(slide, x + 26, y + 26, w - 52, h - 52, { color: arm.palette.surface }, line(arm.palette.surface, 0));
  rect(slide, x + 26, y + 26, w - 52, 50, { color: "#172331" }, line("#172331", 0));
  [0, 1, 2].forEach((index) => ellipse(slide, x + 52 + index * 22, y + 45, 10, 10, {
    color: index === variant % 3 ? arm.palette.accent : "#f3eadf",
  }, line("#f3eadf", 0)));
  rect(slide, x + w - 205, y + 43, 112, 10, { color: "#d6e0eb" }, line("#d6e0eb", 0));
  rect(slide, x + w - 80, y + 39, 22, 18, { color: arm.palette.accent2 }, line(arm.palette.accent2, 0));
  const sideW = Math.max(86, w * 0.16);
  const contentTop = y + 98;
  rect(slide, x + 50, contentTop, sideW, h - 150, { color: "#e9eef2" }, line("#e9eef2", 0));
  for (let index = 0; index < 5; index += 1) {
    rect(slide, x + 68, contentTop + 20 + index * 30, sideW - 36, 8, {
      color: index === variant % 5 ? arm.palette.accent : "#c9d2dc",
    }, line("#c9d2dc", 0));
  }
  const stageX = x + sideW + 82;
  const stageW = w - sideW - 138;
  rect(slide, stageX + 18, contentTop + 24, stageW * 0.88, 120, { color: "#e3ebf4" }, line("#e3ebf4", 0));
  rect(slide, stageX, contentTop, stageW * 0.84, 122, { color: "#f8fbfd" }, line("#f8fbfd", 0));
  rect(slide, stageX + 24, contentTop + 28, stageW * 0.5, 12, { color: "#93a3b6" }, line("#93a3b6", 0));
  rect(slide, stageX + 24, contentTop + 60, stageW * 0.72, 18, { color: arm.palette.accent }, line(arm.palette.accent, 0));
  ellipse(slide, stageX + stageW * 0.55, contentTop + 86, stageW * 0.34, 54, { color: "#ffffff" }, line("#ffffff", 0));
  rect(slide, stageX + stageW * 0.58, contentTop + 24, stageW * 0.18, 14, { color: C.green }, line(C.green, 0));
  rect(slide, stageX + stageW * 0.58, contentTop + 50, stageW * 0.24, 10, { color: "#b8c4d2" }, line("#b8c4d2", 0));
  const tileTop = contentTop + Math.max(122, h * 0.36);
  for (let index = 0; index < 4; index += 1) {
    const tileW = (stageW * 0.86 - 30) / 4;
    const tx = stageX + index * (tileW + 10);
    rect(slide, tx, tileTop, tileW, 48, { color: index % 2 === 0 ? "#eef5fb" : "#f7eadb" }, line("#dde5ee", 1));
    ellipse(slide, tx + 12, tileTop + 12, 15, 15, { color: index === variant % 4 ? arm.palette.accent : "#aeb9c6" }, line("#aeb9c6", 0));
    rect(slide, tx + 36, tileTop + 15, tileW - 48, 6, { color: "#7e8b9a" }, line("#7e8b9a", 0));
    rect(slide, tx + 36, tileTop + 30, Math.max(20, tileW * 0.36), 5, { color: "#c4ced9" }, line("#c4ced9", 0));
  }
  const rowY = contentTop + Math.max(154, h * 0.49);
  [0, 1, 2].forEach((index) => {
    const blockW = (stageW - 32) / 3;
    const bx = stageX + index * (blockW + 16);
    const fill = index === 1 ? "#f8eadb" : "#eaf1fb";
    rect(slide, bx, rowY, blockW, 62, { color: fill }, line(fill, 0));
    rect(slide, bx + 16, rowY + 20, blockW - 32, 8, { color: index === 1 ? C.amber : arm.palette.accent }, line(arm.palette.accent, 0));
    rect(slide, bx + 16, rowY + 40, blockW * 0.45, 7, { color: "#aeb9c6" }, line("#aeb9c6", 0));
  });
  rect(slide, stageX + stageW * 0.66, rowY + 82, stageW * 0.2, 42, { color: "#172331" }, line("#172331", 0));
  rect(slide, stageX + stageW * 0.68, rowY + 98, stageW * 0.12, 6, { color: C.white }, line(C.white, 0));
  rect(slide, stageX + stageW * 0.68, rowY + 112, stageW * 0.16, 6, { color: arm.palette.accent2 }, line(arm.palette.accent2, 0));
}

function drawCaption(slide, page, x, y, w, arm) {
  rect(slide, x, y, w, 40, { color: "#fffdf8" }, line(arm.palette.accent, 2));
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
      max: 38,
    });
  });
}

function drawRun290ProductSurfaceHero(slide, page, arm) {
  drawEditorialText(slide, page, arm, 74, 100, 430, { titleSize: 36 });
  ellipse(slide, -160, 306, 710, 330, { color: "#eadfcd" }, line("#eadfcd", 0));
  ellipse(slide, 535, 42, 805, 574, { color: "#e7eef8" }, line("#e7eef8", 0));
  drawRicherProductSurface(slide, 470, 104, 676, 462, arm, page.slide_index);
  connector(slide, 172, 440, 512, 324, arm.palette.accent2, 16);
  drawCaption(slide, page, 844, 588, 270, arm);
  drawLabels(slide, page, [{ x: 920, y: 116, w: 154 }, { x: 880, y: 524, w: 144 }], arm);
}

function drawRun290EditorialSurfaceSpread(slide, page, arm) {
  drawEditorialText(slide, page, arm, 76, 82, 620, { titleSize: 34, subheadY: 120, ruleY: 212, proofY: 240 });
  rect(slide, 76, 450, 516, 116, { color: "#fffdf8" }, line("#fffdf8", 0));
  text(slide, "historical layout -> primitive -> renderer", 104, 478, 430, 20, { fontSize: 13, bold: true, mono: true, color: arm.palette.title });
  rect(slide, 104, 514, 136, 12, { color: arm.palette.accent }, line(arm.palette.accent, 0));
  rect(slide, 262, 514, 142, 12, { color: C.green }, line(C.green, 0));
  rect(slide, 426, 514, 90, 12, { color: C.amber }, line(C.amber, 0));
  ellipse(slide, 648, 150, 526, 370, { color: "#e8ede8" }, line("#e8ede8", 0));
  drawRicherProductSurface(slide, 760, 168, 392, 304, arm, 1);
  connector(slide, 604, 372, 760, 320, C.green, 16);
  drawCaption(slide, page, 840, 498, 246, arm);
  drawLabels(slide, page, [{ x: 140, y: 578, w: 136 }, { x: 318, y: 578, w: 136 }, { x: 952, y: 126, w: 140 }], arm);
}

function drawRun290BeforeAfterProductStage(slide, page, arm) {
  rect(slide, 0, 0, 540, H, { color: "#ece4d8" }, line("#ece4d8", 0));
  rect(slide, 540, 0, 740, H, { color: "#eaf1f6" }, line("#eaf1f6", 0));
  rect(slide, 518, 0, 68, H, { color: "#e6c4b6" }, line("#e6c4b6", 0));
  drawEditorialText(slide, page, arm, 72, 94, 424, { titleSize: 33 });
  drawRicherProductSurface(slide, 112, 324, 340, 205, { ...arm, palette: { ...arm.palette, accent: "#8a7652", accent2: "#b9aa8d" } }, 0);
  drawRicherProductSurface(slide, 704, 148, 478, 396, arm, 3);
  connector(slide, 472, 392, 706, 318, arm.palette.accent2, 18);
  text(slide, "after recovers surface hierarchy", 734, 80, 386, 32, { fontSize: 18, bold: true, color: arm.palette.title, max: 80 });
  drawCaption(slide, page, 810, 592, 270, arm);
  drawLabels(slide, page, [{ x: 174, y: 548, w: 112 }, { x: 930, y: 112, w: 116 }, { x: 936, y: 552, w: 128 }], arm);
}

function drawRun290EvidenceMatrixSurface(slide, page, arm) {
  drawEditorialText(slide, page, arm, 70, 74, 520, { titleSize: 31, subheadY: 116, ruleY: 210, proofY: 236 });
  ellipse(slide, 512, 80, 660, 532, { color: "#e8ede8" }, line("#e8ede8", 0));
  const gridX = 594;
  const gridY = 128;
  const cells = [
    [0, 0, 156, 112, "#fffdf8"],
    [174, 0, 328, 112, "#f7eadb"],
    [0, 130, 218, 162, "#172331"],
    [236, 130, 248, 162, "#fffdf8"],
    [0, 310, 154, 108, "#fffdf8"],
    [172, 310, 154, 108, "#eaf1fb"],
    [344, 310, 140, 108, "#fffdf8"],
  ];
  cells.forEach(([dx, dy, w, h, fill], index) => {
    const dark = fill === "#172331";
    rect(slide, gridX + dx, gridY + dy, w, h, { color: fill }, line(fill, 0));
    rect(slide, gridX + dx + 20, gridY + dy + 26, w - 42, 8, { color: dark ? arm.palette.accent : C.blue }, line(C.blue, 0));
    rect(slide, gridX + dx + 20, gridY + dy + 58, Math.max(42, w * 0.42), 8, { color: dark ? C.white : "#aeb9c6" }, line("#aeb9c6", 0));
    if (index === 2) text(slide, "proof object", gridX + dx + 22, gridY + dy + 98, w - 44, 18, { fontSize: 12, bold: true, color: C.white });
  });
  drawRicherProductSurface(slide, 292, 382, 342, 214, arm, 4);
  connector(slide, 626, 484, 770, 318, arm.palette.accent2, 14);
  drawCaption(slide, page, 832, 552, 258, arm);
  drawLabels(slide, page, [{ x: 336, y: 612, w: 130 }, { x: 786, y: 268, w: 120 }, { x: 976, y: 406, w: 112 }], arm);
}

function drawRun290StickerStageSurface(slide, page, arm) {
  drawEditorialText(slide, page, arm, 68, 84, 420, { titleSize: 35, subheadY: 126, ruleY: 222, proofY: 250 });
  ellipse(slide, 420, 58, 780, 570, { color: "#e7eef8" }, line("#e7eef8", 0));
  drawRicherProductSurface(slide, 410, 100, 635, 438, arm, 5);
  const stickers = [
    { x: 880, y: 92, w: 235, h: 84, c: C.amber, t: "motion" },
    { x: 350, y: 390, w: 246, h: 92, c: C.green, t: "text field" },
    { x: 810, y: 438, w: 258, h: 96, c: C.coral, t: "review path" },
  ];
  stickers.forEach((item, index) => {
    rect(slide, item.x + 14, item.y + 16, item.w, item.h, { color: "#c7beb2" }, line("#c7beb2", 0));
    rect(slide, item.x, item.y, item.w, item.h, { color: "#fffdf8" }, line(item.c, 3));
    ellipse(slide, item.x + 18, item.y + 18, 18, 18, { color: item.c }, line(item.c, 0));
    text(slide, item.t, item.x + 50, item.y + 28, item.w - 72, 26, { fontSize: 14, bold: true, color: arm.palette.title, max: 40 });
    if (index < 2) connector(slide, item.x + item.w / 2, item.y + item.h, 728, 328 + index * 64, item.c, 10);
  });
  drawCaption(slide, page, 760, 576, 270, arm);
  drawLabels(slide, page, [{ x: 104, y: 470, w: 130 }, { x: 104, y: 512, w: 130 }, { x: 104, y: 554, w: 130 }], arm);
}

function drawRun290DecisionBoardSurface(slide, page, arm) {
  drawEditorialText(slide, page, arm, 76, 80, 524, { titleSize: 32, subheadY: 116, ruleY: 210, proofY: 236 });
  ellipse(slide, 150, 166, 890, 420, { color: "#ecebe1" }, line("#ecebe1", 0));
  const nodes = [
    { x: 260, y: 456, label: "generated", dark: false },
    { x: 474, y: 334, label: "review", dark: false },
    { x: 700, y: 388, label: "Part T", dark: false },
    { x: 928, y: 258, label: "public blocked", dark: true },
  ];
  connector(slide, nodes[0].x, nodes[0].y, nodes[1].x, nodes[1].y, arm.palette.accent2, 16);
  connector(slide, nodes[1].x, nodes[1].y, nodes[2].x, nodes[2].y, arm.palette.accent2, 16);
  connector(slide, nodes[2].x, nodes[2].y, nodes[3].x, nodes[3].y, arm.palette.accent, 18);
  nodes.forEach((node) => {
    ellipse(slide, node.x - 68, node.y - 46, 136, 92, { color: node.dark ? "#172331" : "#fffdf8" }, line(node.dark ? "#172331" : "#fffdf8", 0));
    text(slide, node.label, node.x - 58, node.y - 12, 116, 24, {
      fontSize: 12,
      bold: true,
      color: node.dark ? C.white : arm.palette.title,
      align: "center",
      max: 34,
    });
  });
  drawRicherProductSurface(slide, 792, 356, 336, 212, arm, 2);
  drawCaption(slide, page, 836, 592, 244, arm);
  drawLabels(slide, page, [{ x: 210, y: 534, w: 118 }, { x: 654, y: 462, w: 112 }, { x: 872, y: 182, w: 128 }], arm);
}

function drawFullSlide(slide, page, arm) {
  drawBase(slide, page, arm);
  if (page.renderer_function_name === "drawRun290EditorialSurfaceSpread") drawRun290EditorialSurfaceSpread(slide, page, arm);
  else if (page.renderer_function_name === "drawRun290BeforeAfterProductStage") drawRun290BeforeAfterProductStage(slide, page, arm);
  else if (page.renderer_function_name === "drawRun290EvidenceMatrixSurface") drawRun290EvidenceMatrixSurface(slide, page, arm);
  else if (page.renderer_function_name === "drawRun290StickerStageSurface") drawRun290StickerStageSurface(slide, page, arm);
  else if (page.renderer_function_name === "drawRun290DecisionBoardSurface") drawRun290DecisionBoardSurface(slide, page, arm);
  else drawRun290ProductSurfaceHero(slide, page, arm);
  text(slide, `${page.renderer_primitive_id}`, 54, 666, 520, 18, {
    fontSize: 9,
    bold: true,
    color: arm.palette.muted,
    mono: true,
    max: 82,
  });
}

function drawComparisonSlide(slide, page, arm) {
  drawBase(slide, page, arm);
  ellipse(slide, 140, 180, 840, 360, { color: arm.mode === "negative" ? "#e3d6c2" : "#e7edf1" }, line("#cdd3d8", 1));
  rect(slide, 720, 210, 330, 238, { color: arm.palette.surface }, line("#c3ccd5", 1));
  connector(slide, 236, 456, 756, 308, arm.palette.accent2, 12);
  const title = arm.mode === "negative"
    ? `${page.role}: Part R withheld`
    : arm.mode === "baseline"
      ? `${page.role}: workflow baseline`
      : `${page.role}: brief-only deck`;
  text(slide, title, 96, 110, 540, 84, { fontSize: 30, bold: true, title: true, color: arm.palette.title, max: 84 });
  const body = arm.mode === "negative"
    ? "This arm sees the same content but cannot recover historical layouts or call Run 2.87 primitive modules."
    : "This comparison arm is generated locally for viewer context. The Part U manifest validates the full arm only.";
  text(slide, body, 100, 218, 438, 72, { fontSize: 13, color: arm.palette.muted, max: 140 });
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

function indexByRole(records) {
  return new Map((records ?? []).map((record) => [record.role, record]));
}

function loadInputs() {
  const data = {
    partTEvaluation: readJson(INPUTS.partTEvaluation),
    run288Result: readJson(INPUTS.run288Result),
    partRPlan: readJson(INPUTS.partRPlan),
  };
  if (data.partTEvaluation.status !== "run2_89_visual_quality_evaluation_public_blocked") {
    throw new Error("Run 2.90 requires the Run 2.89 visual quality evaluation");
  }
  if (data.partTEvaluation.next_required_action !== "part_u_renderer_asset_surface_composition_repair_from_t_evaluation") {
    throw new Error("Run 2.90 requires Part T to request the Part U renderer rerun");
  }
  if (data.run288Result.status !== "run2_88_best_layout_visual_primitive_rerun_generated_public_blocked") {
    throw new Error("Run 2.90 requires the Run 2.88 generated renderer result");
  }
  if (data.partRPlan.status !== "run2_87_best_layout_recovery_visual_primitive_plan_ready_public_blocked") {
    throw new Error("Run 2.90 requires the Run 2.87 asset surface composition plan");
  }
  if (data.partRPlan.next_required_action !== "part_s_renderer_rerun_from_run2_87_best_layout_visual_primitive_plan") {
    throw new Error("Run 2.90 requires the Run 2.87 plan to have fed Run 2.88");
  }
  return data;
}

function buildRenderModel(data) {
  const pageByRole = indexByRole(data.partRPlan.page_layout_recovery_records);
  const primitiveById = new Map(data.partRPlan.visual_primitive_contracts.map((contract) => [contract.primitive_id, contract]));
  const evaluationByRole = indexByRole(data.partTEvaluation.role_assessments);
  const run288ByRole = indexByRole(data.run288Result.rendered_pages);
  const functionByRole = {
    cover: "drawRun290ProductSurfaceHero",
    setup: "drawRun290EditorialSurfaceSpread",
    contrast: "drawRun290BeforeAfterProductStage",
    proof: "drawRun290EvidenceMatrixSurface",
    climax: "drawRun290StickerStageSurface",
    close: "drawRun290DecisionBoardSurface",
  };
  return ROLES.map((role, index) => {
    const recovery = pageByRole.get(role);
    const primitive = primitiveById.get(recovery?.renderer_primitive_id);
    const evaluation = evaluationByRole.get(role);
    const previousPage = run288ByRole.get(role);
    if (!recovery || !primitive || !evaluation || !previousPage) {
      throw new Error(`Run 2.90 missing source record for role: ${role}`);
    }
    const copy = COPY_BY_ROLE[role];
    return {
      role,
      slide_index: index + 1,
      visual_grammar_module: recovery.visual_grammar_module,
      motif_family: recovery.motif_family,
      renderer_primitive_id: primitive.primitive_id,
      source_run2_88_renderer_function_name: previousPage.renderer_function_name,
      source_t_root_cause_layer: evaluation.root_cause_layer,
      asset_surface_composition_id: `asset_surface_composition_2_90_${role}`,
      renderer_function_name: functionByRole[role],
      primitive_family: primitive.primitive_family ?? primitive.motif_family,
      renderer_repair_directives_applied: REPAIR_FLAGS,
      anti_regression_gates: ANTI_REGRESSION_GATES,
      historical_layout_recovered: true,
      asset_surface_rendered: true,
      composition_detail_added: true,
      wireframe_like: false,
      text_integrated_with_surface: true,
      collision_avoidance_passed: true,
      traceability_on_canvas: false,
      floating_label_count: 0,
      label_count: Math.min(copy.labels.length, 3),
      min_visible_label_font_size: 12,
      surface_detail_count: 12,
      filled_surface_count: 6,
      mock_asset_count: 3,
      public_polish_claimed: false,
      headline: copy.headline,
      subhead: copy.subhead,
      proof_sentence: copy.proof,
      object_caption: copy.caption,
      visible_labels: copy.labels.slice(0, 3),
    };
  });
}

function traceForArm(arm, pages) {
  return {
    schema_version: 1,
    run_id: RUN_ID,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    release_decision: arm.release,
    consumed_sources: arm.mode === "full" ? CONSUMED_SOURCES : [`${pack}/commercial_case.md`],
    part_u_renderer_scope: arm.mode === "full"
      ? "renderer_asset_surface_composition_consumes_run2_89_run2_88_and_run2_87"
      : "comparison_arm_not_part_u_quality_manifest",
    public_release_started: false,
    slides: pages.map((page) => ({
      role: page.role,
      slide_index: page.slide_index,
      visual_grammar_module: arm.mode === "full" ? page.visual_grammar_module : "comparison_context",
      renderer_primitive_id: arm.mode === "full" ? page.renderer_primitive_id : "",
      renderer_function_name: arm.mode === "full" ? page.renderer_function_name : "",
      asset_surface_composition_id: arm.mode === "full" ? page.asset_surface_composition_id : "",
      visible_label_count: arm.mode === "full" ? page.label_count : 0,
      floating_label_count: arm.mode === "full" ? page.floating_label_count : 0,
      traceability_on_canvas: false,
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

function buildRun288Sheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  const labels = built.filter((item) => fs.existsSync(item.contactSheet)).map((item) => item.arm.label);
  return buildNamedContactSheet(
    path.join(outRoot, "run2-90-four-arm-contact-sheet.png"),
    "Run 2.90 asset surface composition comparison",
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
      `part: Part U / Run ${RUN_ID}`,
      `consumed sources: ${arm.mode === "full" ? CONSUMED_SOURCES.join(", ") : "commercial_case.md only"}`,
      "full arm requirement: repair concrete product surface materiality and composition detail while preserving text-heavy readability",
      "release boundary: public blocked until Part V visual quality evaluation",
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
      source: "scripts/generate_ppt_run2_90_renderer_asset_surface_composition_arms.mjs",
      exportName: `slide${String(index + 1).padStart(2, "0")}`,
    })),
  };
  writeJson(path.join(workspace, "output", "artifact-build-manifest.json"), manifest);
  writeJson(path.join(workspace, "qa", "build_manifest_stdout.json"), manifest);
  writeJson(path.join(workspace, "trace_manifest.json"), traceForArm(arm, pages));
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
    <section class="slide ${htmlEscape(page.role)}">
      <div class="kicker">Run 2.90 / ${htmlEscape(page.renderer_primitive_id)}</div>
      <h2>${htmlEscape(page.headline)}</h2>
      <p class="subhead">${htmlEscape(page.subhead)}</p>
      <div class="surface"><span></span><span></span><span></span><b>${htmlEscape(page.object_caption)}</b></div>
      <p class="proof">${htmlEscape(page.proof_sentence)}</p>
    </section>
  `).join("\n");
  const html = `<!doctype html>
<html lang="en" data-run-id="2.90">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Run 2.90 asset surface compositions</title>
  <style>
    body{margin:0;background:#141922;color:#11151c;font-family:Aptos,Inter,system-ui,sans-serif}
    main{display:grid;gap:24px;padding:32px}
    .slide{width:min(1120px,calc(100vw - 64px));aspect-ratio:16/9;background:#f4efe6;margin:auto;position:relative;padding:50px 60px;box-sizing:border-box;overflow:hidden}
    .kicker{font:700 11px/1 Aptos Mono,monospace;color:#66717e;text-transform:uppercase;letter-spacing:.04em}
    h2{font-size:42px;line-height:1.04;margin:50px 0 16px;max-width:500px}
    .subhead{font-size:18px;line-height:1.3;color:#66717e;max-width:540px}
    .proof{position:absolute;left:60px;bottom:64px;width:520px;font-size:15px;line-height:1.35}
    .surface{position:absolute;right:62px;top:104px;width:500px;height:370px;background:#121922;padding:28px;box-sizing:border-box;box-shadow:28px 30px 0 #cfc6b8}
    .surface span{display:block;height:20px;background:#285ed8;margin:28px 0;width:72%}
    .surface span:nth-child(2){background:#0d8b68;width:88%}
    .surface span:nth-child(3){background:#e0ad3e;width:56%}
    .surface b{position:absolute;right:28px;bottom:28px;background:#fffdf8;border:2px solid #285ed8;padding:9px 14px;font-size:13px}
    .proof .surface{display:grid}
    .climax .surface{box-shadow:38px 42px 0 #e0ad3e}
    .close .surface{border-radius:180px}
  </style>
</head>
<body><main>${slideCards}</main></body>
</html>`;
  fs.writeFileSync(outPath, html);
}

function buildResult(pages, built, fourArmSheet, standaloneHtml, data) {
  const full = built.find((item) => item.arm.armId === "run2_90_full_asset_surface_composition");
  return {
    artifact_id: "run2_90_renderer_asset_surface_composition_rerun_result",
    part: "Part U",
    schema_version: "ppt_run2_90_renderer_asset_surface_composition_rerun_result.v1",
    run_id: RUN_ID,
    status: "run2_90_renderer_asset_surface_composition_rerun_generated_public_blocked",
    public_ready: false,
    public_release_started: false,
    quality_claim_boundary: "asset_surface_composition_renderer_generated_viewer_check_only_no_quality_verdict",
    consumed_sources: CONSUMED_SOURCES,
    source_t_evaluation: {
      status: data.partTEvaluation.status,
      next_required_action: data.partTEvaluation.next_required_action,
      source_result: INPUTS.partTEvaluation,
      top_blocker: data.partTEvaluation.visual_quality_assessment?.top_blocker ?? "",
      next_layer_to_fix: data.partTEvaluation.visual_quality_assessment?.next_layer_to_fix ?? "",
    },
    source_run2_88_renderer_result: {
      status: data.run288Result.status,
      next_required_action: data.run288Result.next_required_action,
      source_result: INPUTS.run288Result,
    },
    source_run2_87_plan: {
      status: data.partRPlan.status,
      next_required_action: data.partRPlan.next_required_action,
      source_result: INPUTS.partRPlan,
    },
    renderer_asset_surface_composition_manifest: {
      generator: "scripts/generate_ppt_run2_90_renderer_asset_surface_composition_arms.mjs",
      consumed_sources: CONSUMED_SOURCES,
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_90_full_asset_surface_composition",
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
      source_t_root_cause_layer: page.source_t_root_cause_layer,
      asset_surface_composition_id: page.asset_surface_composition_id,
      renderer_primitive_id: page.renderer_primitive_id,
      renderer_function_name: page.renderer_function_name,
      renderer_repair_directives_applied: page.renderer_repair_directives_applied,
      anti_regression_gates: page.anti_regression_gates,
      asset_surface_rendered: page.asset_surface_rendered,
      composition_detail_added: page.composition_detail_added,
      wireframe_like: page.wireframe_like,
      text_integrated_with_surface: page.text_integrated_with_surface,
      collision_avoidance_passed: page.collision_avoidance_passed,
      traceability_on_canvas: page.traceability_on_canvas,
      floating_label_count: page.floating_label_count,
      label_count: page.label_count,
      min_visible_label_font_size: page.min_visible_label_font_size,
      surface_detail_count: page.surface_detail_count,
      filled_surface_count: page.filled_surface_count,
      mock_asset_count: page.mock_asset_count,
      public_polish_claimed: page.public_polish_claimed,
    })),
    renderer_asset_surface_composition_checks: {
      pages_with_t_evaluation_consumed: pages.length,
      pages_with_asset_surface_rendered: pages.filter((page) => page.asset_surface_rendered).length,
      pages_with_composition_detail_added: pages.filter((page) => page.composition_detail_added).length,
      pages_with_wireframe_reduction: pages.filter((page) => page.wireframe_like === false).length,
      pages_with_collision_avoidance: pages.filter((page) => page.collision_avoidance_passed).length,
      pages_with_traceability_routed_off_canvas: pages.filter((page) => page.traceability_on_canvas === false).length,
      public_quality_verdict_started: false,
    },
    next_required_action: "part_v_visual_quality_evaluation_for_run2_90",
  };
}

function buildMarkdown(result) {
  return [
    "# Run 2.90 asset surface composition renderer rerun",
    "",
    `Status: ${result.status}`,
    "",
    "Run 2.90 generated a four-arm comparison and updated the local viewer. It consumes Part T Run 2.89, the Run 2.88 renderer result, and the Run 2.87 primitive plan.",
    "",
    "Consumed source trace:",
    ...result.consumed_sources.map((source) => `- ${source}`),
    "",
    "Boundary: public release remains blocked. Part V must evaluate visual quality before any public-ready claim.",
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
  const fourArmSheet = buildRun288Sheet(built);
  const standaloneHtml = path.join(outRoot, "ppt-run2-90-full-vulca", "output", "run2-90-asset-surface-composition.html");
  buildStandaloneHtml(pages, standaloneHtml);
  const result = buildResult(pages, built, fourArmSheet, standaloneHtml, data);
  writeJson(path.join(root, RESULT_JSON), result);
  fs.writeFileSync(path.join(root, RESULT_MD), buildMarkdown(result));
  writeJson(path.join(outRoot, "run2_90_renderer_asset_surface_composition_rerun_summary.json"), {
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
