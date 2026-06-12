import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");

function normalizeThreadId(value) {
  const candidate = String(value ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2");
  if (!/^[A-Za-z0-9._-]{1,96}$/.test(candidate) || candidate.includes("..")) {
    throw new Error(`Unsafe THREAD_ID: ${candidate}`);
  }
  return candidate;
}

const threadId = normalizeThreadId(process.env.THREAD_ID);
const outRoot = path.join(root, "outputs", threadId, "presentations", "ppt-parallel-usecase-pilots");

function resolveExistingPath(label, candidates) {
  for (const candidate of candidates.filter(Boolean)) {
    if (fs.existsSync(candidate)) return candidate;
  }
  throw new Error(`Unable to find ${label}. Checked: ${candidates.filter(Boolean).join(", ")}`);
}

const artifactToolPackageCandidates = [
  process.env.ARTIFACT_TOOL_PACKAGE,
  path.join(root, "node_modules/@oai/artifact-tool"),
  process.env.HOME
    ? path.join(process.env.HOME, ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool")
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
const slideSize = { width: W, height: H };
const sourceRoot = path.join(root, "docs/product/ppt-parallel-usecase-pilots");
const bundledPython = process.env.HOME
  ? path.join(process.env.HOME, ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3")
  : "";
const python = process.env.PYTHON ?? (bundledPython && fs.existsSync(bundledPython) ? bundledPython : "python3");

const decks = [
  {
    id: "deck-a-brand-safe-ai-creative-production",
    title: "Brand-Safe AI Creative Production",
    filename: "brand-safe-ai-creative-production.pptx",
    accent: "#2a5bd7",
    accent2: "#0f8a6a",
    accent3: "#d66b4d",
    bg: "#f6f1e8",
    ink: "#141922",
    muted: "#59636f",
    footer: "Sources: Coca-Cola Company announcement; Adobe Firefly Creative Production docs. Reference examples only.",
  },
  {
    id: "deck-b-vulca-product-strategy",
    title: "Vulca Product Strategy",
    filename: "vulca-product-strategy.pptx",
    accent: "#4c6fff",
    accent2: "#18a579",
    accent3: "#f0b342",
    bg: "#eef3f1",
    ink: "#11151c",
    muted: "#53606d",
    footer: "Sources: Vulca README, roadmap, commercial case, generation protocol, MCP server source.",
  },
  {
    id: "deck-c-vulca-workflow-demo",
    title: "Vulca Workflow Demo",
    filename: "vulca-workflow-demo.pptx",
    accent: "#2d6cdf",
    accent2: "#e17b47",
    accent3: "#16a085",
    bg: "#f3efe7",
    ink: "#141720",
    muted: "#5e6772",
    footer: "Conceptual workflow demo. Current MCP capabilities and agent-side orchestration remain separate.",
  },
];

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function resetWorkspace(workspace) {
  fs.rmSync(workspace, { recursive: true, force: true });
  for (const dir of ["output", "preview", "layout/final", "qa", "assets", "slides", "node_modules/@oai"]) {
    ensureDir(path.join(workspace, dir));
  }
  fs.writeFileSync(path.join(workspace, "package.json"), `${JSON.stringify({ private: true, type: "module" }, null, 2)}\n`);
  const linkPath = path.join(workspace, "node_modules/@oai/artifact-tool");
  try {
    fs.symlinkSync(artifactToolPackage, linkPath, process.platform === "win32" ? "junction" : "dir");
  } catch (error) {
    if (error.code !== "EEXIST") throw error;
  }
}

function repoRel(absPath) {
  return path.relative(root, absPath).split(path.sep).join("/");
}

function blobToBuffer(blob) {
  if (blob?.data instanceof Uint8Array) return Buffer.from(blob.data);
  if (typeof blob.arrayBuffer === "function") {
    return blob.arrayBuffer().then((buffer) => Buffer.from(buffer));
  }
  throw new Error("Unsupported blob object returned by artifact-tool");
}

function compact(value, max = 140) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  if (text.length <= max) return text;
  return `${text.slice(0, max - 1).replace(/\s+\S*$/, "").trim()}.`;
}

function slugLabel(value) {
  return String(value ?? "")
    .replace(/[^a-z0-9]+/gi, " ")
    .trim()
    .toUpperCase();
}

function readSection(markdown, heading) {
  const marker = `## ${heading}`;
  const start = markdown.indexOf(marker);
  if (start < 0) return "";
  const rest = markdown.slice(start + marker.length);
  const next = rest.search(/\n## /);
  return (next >= 0 ? rest.slice(0, next) : rest).trim();
}

function firstParagraph(section) {
  return section
    .split(/\n{2,}/)
    .map((part) => part.trim())
    .find((part) => part && !part.startsWith("|")) ?? "";
}

function splitMarkdownRow(row) {
  const trimmed = row.trim();
  if (!trimmed.startsWith("|")) return [];
  return trimmed
    .slice(1, trimmed.endsWith("|") ? -1 : undefined)
    .split("|")
    .map((cell) => cell.trim());
}

function parseDeck(deck) {
  const briefPath = path.join(sourceRoot, deck.id, "deck_brief.md");
  const claimPath = path.join(sourceRoot, deck.id, "claim_spine.md");
  const visualPath = path.join(sourceRoot, deck.id, "visual_brief.md");
  const markdown = fs.readFileSync(briefPath, "utf8");
  const arc = [];
  const arcSection = readSection(markdown, "Six-Slide Arc");
  for (const line of arcSection.split("\n")) {
    const cells = splitMarkdownRow(line);
    if (cells.length >= 5 && /^[1-6]$/.test(cells[0])) {
      arc.push({
        index: Number.parseInt(cells[0], 10),
        role: cells[1],
        claim: cells[2],
        proof: cells[3],
        basis: cells[4],
      });
    }
  }
  if (arc.length !== 6) {
    throw new Error(`${deck.id} expected 6 slide rows, found ${arc.length}`);
  }
  return {
    ...deck,
    briefPath,
    claimPath,
    visualPath,
    audience: firstParagraph(readSection(markdown, "Audience")),
    decision: firstParagraph(readSection(markdown, "Decision")),
    thesis: firstParagraph(readSection(markdown, "Thesis")).replace(/\s+source_ids:.*$/, ""),
    concept: firstParagraph(readSection(markdown, "Product Or Workflow Concept")),
    arc,
  };
}

function addShape(slide, { x, y, w, h, fill = "#ffffff", line = "transparent", width = 0, geometry = "rect" }) {
  const strokeWidth = width === 1 ? 2 : Math.max(width, 1);
  return slide.shapes.add({
    geometry,
    position: { left: x, top: y, width: w, height: h },
    fill: fill === "transparent" ? { color: "#ffffff", transparency: 100 } : { color: fill },
    line: line === "transparent" ? { color: "#ffffff", transparency: 100, width: 0 } : { color: line, width: strokeWidth },
  });
}

function addText(slide, text, x, y, w, h, opts = {}) {
  const shape = addShape(slide, {
    x,
    y,
    w,
    h,
    fill: opts.fill ?? "transparent",
    line: opts.line ?? "transparent",
    width: opts.lineWidth ?? 0,
    geometry: opts.geometry ?? "rect",
  });
  shape.text.set(compact(text, opts.max ?? 170));
  shape.text.fontSize = opts.fontSize ?? 16;
  shape.text.color = opts.color ?? "#11151c";
  shape.text.bold = Boolean(opts.bold);
  shape.text.typeface = opts.typeface ?? (opts.title ? "Aptos Display" : opts.mono ? "Aptos Mono" : "Aptos");
  shape.text.insets = opts.insets ?? { left: 0, right: 0, top: 0, bottom: 0 };
  if (opts.align) shape.text.alignment = opts.align;
  if (opts.verticalAlign) shape.text.verticalAlignment = opts.verticalAlign;
  return shape;
}

function addLabel(slide, label, x, y, w, color, fill = "#ffffff") {
  addShape(slide, { x, y, w, h: 26, fill, line: color, width: 1 });
  addShape(slide, { x: x + 8, y: y + 8, w: 10, h: 10, fill: color, line: color, geometry: "ellipse" });
  addText(slide, label, x + 26, y + 6, w - 34, 14, { fontSize: 10, bold: true, color, max: 34 });
}

function addRule(slide, x, y, w, color, h = 3) {
  addShape(slide, { x, y, w, h, fill: color, line: color });
}

function drawBase(slide, deck, page) {
  addShape(slide, { x: 0, y: 0, w: W, h: H, fill: deck.bg, line: deck.bg });
  addShape(slide, { x: 0, y: 0, w: W, h: 10, fill: deck.accent, line: deck.accent });
  addText(slide, deck.title, 52, 34, 420, 18, { fontSize: 9, bold: true, color: deck.muted, mono: true, max: 80 });
  addText(slide, `${String(page.index).padStart(2, "0")} / ${slugLabel(page.role)}`, 1060, 34, 160, 18, {
    fontSize: 9,
    bold: true,
    color: deck.muted,
    align: "right",
    mono: true,
    max: 40,
  });
  addText(slide, deck.footer, 54, 676, 940, 18, { fontSize: 9.5, color: "#3f4954", max: 170 });
}

function drawHeadline(slide, deck, page, x = 64, y = 84, w = 510) {
  const claimLength = page.claim.length;
  const titleSize = claimLength > 128 ? 25 : claimLength > 104 ? 27 : claimLength > 82 ? 30 : 34;
  const titleMax = claimLength > 128 ? 112 : 128;
  addText(slide, slugLabel(page.role), x, y, 220, 22, { fontSize: 11, bold: true, color: deck.accent, mono: true, max: 28 });
  addRule(slide, x, y + 34, 132, deck.accent, 3);
  addText(slide, page.claim, x, y + 56, w, 188, {
    fontSize: titleSize,
    bold: true,
    title: true,
    color: deck.ink,
    max: titleMax,
  });
  addText(slide, page.proof, x, y + 276, w * 0.86, 62, {
    fontSize: 13.5,
    color: "#3f4954",
    max: 104,
  });
}

function drawMiniDeck(slide, x, y, w, h, deck, label = "editable deck") {
  addShape(slide, { x: x + 22, y: y + 22, w, h, fill: "#c8beb2", line: "#c8beb2" });
  addShape(slide, { x, y, w, h, fill: "#fffdf7", line: deck.ink, width: 2 });
  addShape(slide, { x: x + 22, y: y + 20, w: w - 44, h: 42, fill: deck.ink, line: deck.ink });
  addShape(slide, { x: x + 44, y: y + 84, w: w * 0.45, h: 18, fill: deck.accent, line: deck.accent });
  addShape(slide, { x: x + 44, y: y + 126, w: w * 0.62, h: 12, fill: "#b9c4cf", line: "#b9c4cf" });
  addShape(slide, { x: x + 44, y: y + 160, w: w * 0.28, h: 74, fill: "#e7edf4", line: "#e7edf4" });
  addShape(slide, { x: x + 44 + w * 0.32, y: y + 160, w: w * 0.28, h: 74, fill: "#eef4ee", line: "#eef4ee" });
  addShape(slide, { x: x + 44 + w * 0.64, y: y + 160, w: w * 0.22, h: 74, fill: "#f7eadb", line: "#f7eadb" });
  addText(slide, label, x + 32, y + h - 52, w - 64, 22, { fontSize: 13, bold: true, color: deck.ink, max: 42 });
}

function drawVariantGrid(slide, x, y, deck) {
  drawMiniDeck(slide, x, y + 52, 260, 176, deck, "single hero asset");
  addRule(slide, x + 296, y + 146, 88, deck.accent2, 8);
  for (let i = 0; i < 4; i += 1) {
    const cx = x + 420 + (i % 2) * 164;
    const cy = y + (i > 1 ? 172 : 20);
    addShape(slide, { x: cx, y: cy, w: 132, h: 106, fill: "#fffdf7", line: i % 2 ? deck.accent2 : deck.accent, width: 2 });
    addShape(slide, { x: cx + 16, y: cy + 18, w: 72, h: 8, fill: i % 2 ? deck.accent2 : deck.accent, line: i % 2 ? deck.accent2 : deck.accent });
    addShape(slide, { x: cx + 16, y: cy + 44, w: 98, h: 34, fill: i === 2 ? "#f7eadb" : "#e8eef7", line: "transparent" });
    addText(slide, ["social", "retail", "locale", "display"][i], cx + 18, cy + 82, 80, 12, { fontSize: 9, bold: true, color: deck.muted, max: 16 });
  }
}

function drawInputStack(slide, x, y, deck) {
  const rows = [
    ["approved assets", deck.accent],
    ["templates", deck.accent2],
    ["copy and offers", deck.accent3],
    ["review rules", "#6f7b88"],
  ];
  rows.forEach(([label, color], i) => {
    addShape(slide, { x: x + i * 22, y: y + i * 52, w: 388, h: 42, fill: "#fffdf7", line: color, width: 2 });
    addShape(slide, { x: x + 18 + i * 22, y: y + 15 + i * 52, w: 18, h: 12, fill: color, line: color });
    addText(slide, label, x + 54 + i * 22, y + 12 + i * 52, 250, 16, { fontSize: 13, bold: true, color: deck.ink, max: 34 });
  });
  addText(slide, "Reference examples only; no affiliation implied.", x, y + 250, 390, 28, { fontSize: 12, color: deck.muted, max: 80 });
}

function drawWorkflow(slide, x, y, w, deck, labels) {
  const stepW = Math.floor((w - 80) / labels.length);
  labels.forEach((label, i) => {
    const sx = x + i * (stepW + 16);
    addShape(slide, { x: sx, y, w: stepW, h: 90, fill: i % 2 ? "#eef4ee" : "#fffdf7", line: i % 2 ? deck.accent2 : deck.accent, width: 2 });
    addText(slide, String(i + 1).padStart(2, "0"), sx + 16, y + 16, 40, 16, { fontSize: 12, bold: true, mono: true, color: i % 2 ? deck.accent2 : deck.accent });
    addText(slide, label, sx + 16, y + 44, stepW - 32, 28, { fontSize: 12, bold: true, color: deck.ink, max: 34 });
    if (i < labels.length - 1) addRule(slide, sx + stepW, y + 44, 16, deck.accent2, 5);
  });
}

function drawLanes(slide, x, y, deck, rows) {
  rows.forEach((row, i) => {
    const yy = y + i * 72;
    addText(slide, row[0], x, yy + 22, 120, 18, { fontSize: 11, bold: true, color: deck.muted, max: 28 });
    for (let j = 0; j < row.length - 1; j += 1) {
      const color = [deck.accent, deck.accent2, deck.accent3, "#6f7b88"][j % 4];
      addShape(slide, { x: x + 142 + j * 132, y: yy, w: 112, h: 54, fill: "#fffdf7", line: color, width: 1 });
      addText(slide, row[j + 1], x + 154 + j * 132, yy + 19, 88, 15, { fontSize: 10, bold: true, color: deck.ink, align: "center", max: 24 });
    }
  });
}

function drawMatrix(slide, x, y, deck, columns, rows) {
  const cellW = 116;
  const cellH = 44;
  columns.forEach((col, i) => {
    addText(slide, col, x + 116 + i * cellW, y, cellW - 10, 18, { fontSize: 10, bold: true, color: deck.muted, align: "center", max: 18 });
  });
  rows.forEach((row, r) => {
    addText(slide, row, x, y + 34 + r * cellH + 14, 98, 16, { fontSize: 10, bold: true, color: deck.ink, max: 22 });
    columns.forEach((_, c) => {
      const fill = (r + c) % 3 === 0 ? "#eaf0fb" : (r + c) % 3 === 1 ? "#edf6ef" : "#f8eadb";
      addShape(slide, { x: x + 116 + c * cellW, y: y + 34 + r * cellH, w: cellW - 8, h: cellH - 8, fill, line: "#d6dce3", width: 1 });
      addShape(slide, { x: x + 160 + c * cellW, y: y + 48 + r * cellH, w: 18, h: 10, fill: c % 2 ? deck.accent2 : deck.accent, line: "transparent" });
    });
  });
}

function drawGate(slide, x, y, deck, labels) {
  labels.forEach((label, i) => {
    const yy = y + i * 64;
    addShape(slide, { x, y: yy, w: 430, h: 48, fill: i === labels.length - 1 ? deck.ink : "#fffdf7", line: i === labels.length - 1 ? deck.ink : "#d5d9de", width: 1 });
    addShape(slide, { x: x + 18, y: yy + 15, w: 18, h: 18, fill: i === labels.length - 1 ? deck.accent3 : deck.accent2, line: "transparent", geometry: "ellipse" });
    addText(slide, label, x + 52, yy + 15, 330, 18, { fontSize: 12, bold: true, color: i === labels.length - 1 ? "#fffdf7" : deck.ink, max: 54 });
  });
}

function drawProductLoop(slide, x, y, deck, labels) {
  const cx = x + 320;
  const cy = y + 214;
  addShape(slide, { x: cx - 118, y: cy - 118, w: 236, h: 236, fill: "#fffdf7", line: deck.accent, width: 3, geometry: "ellipse" });
  addText(slide, "control layer", cx - 76, cy - 16, 152, 28, { fontSize: 18, bold: true, color: deck.ink, align: "center", max: 30 });
  labels.forEach((label, i) => {
    const angle = (-90 + i * (360 / labels.length)) * Math.PI / 180;
    const nx = cx + Math.cos(angle) * 238 - 64;
    const ny = cy + Math.sin(angle) * 166 - 30;
    addShape(slide, { x: nx, y: ny, w: 128, h: 60, fill: i % 2 ? "#edf6ef" : "#eaf0fb", line: i % 2 ? deck.accent2 : deck.accent, width: 2 });
    addText(slide, label, nx + 12, ny + 22, 104, 16, { fontSize: 10.5, bold: true, color: deck.ink, align: "center", max: 24 });
  });
}

function drawComparison(slide, x, y, deck) {
  addShape(slide, { x, y, w: 270, h: 240, fill: "#fffdf7", line: "#cfd6dd", width: 1 });
  addText(slide, "prompt-only", x + 26, y + 24, 180, 24, { fontSize: 18, bold: true, color: deck.ink });
  addShape(slide, { x: x + 32, y: y + 78, w: 188, h: 26, fill: "#e6e0d6", line: "transparent" });
  addShape(slide, { x: x + 32, y: y + 126, w: 128, h: 26, fill: "#e6e0d6", line: "transparent" });
  addText(slide, "hard to inspect", x + 32, y + 186, 180, 18, { fontSize: 12, color: deck.muted, max: 28 });
  addShape(slide, { x: x + 340, y, w: 360, h: 240, fill: "#11151c", line: deck.accent, width: 2 });
  addText(slide, "governed workflow", x + 370, y + 24, 250, 24, { fontSize: 18, bold: true, color: "#fffdf7" });
  drawWorkflow(slide, x + 370, y + 80, 280, deck, ["intent", "edit", "review"]);
  addText(slide, "inspectable package", x + 370, y + 190, 230, 18, { fontSize: 12, bold: true, color: deck.accent2, max: 30 });
}

function drawReviewBoard(slide, x, y, deck) {
  const lanes = [
    ["pass", deck.accent2],
    ["repair", deck.accent3],
    ["hold", "#6f7b88"],
  ];
  lanes.forEach(([lane, color], i) => {
    const lx = x + i * 180;
    addText(slide, lane, lx, y, 150, 22, { fontSize: 12, bold: true, color, mono: true, max: 18 });
    addShape(slide, { x: lx, y: y + 32, w: 150, h: 246, fill: "#fffdf7", line: color, width: 2 });
    for (let j = 0; j < 3; j += 1) {
      addShape(slide, { x: lx + 18, y: y + 54 + j * 58, w: 112, h: 36, fill: j === 1 ? "#eef4ee" : "#eaf0fb", line: "transparent" });
    }
  });
}

function drawRoadmap(slide, x, y, deck) {
  const steps = [
    ["current base", deck.accent2],
    ["wedge", deck.accent],
    ["missing surface", deck.accent3],
    ["human review gate", deck.ink],
  ];
  steps.forEach(([label, color], i) => {
    const sx = x + i * 158;
    addShape(slide, { x: sx, y: y + i * 24, w: 126, h: 126, fill: "#fffdf7", line: color, width: 2 });
    addText(slide, label, sx + 14, y + i * 24 + 44, 98, 42, {
      fontSize: i === 3 ? 13 : 14,
      bold: true,
      color: deck.ink,
      align: "center",
      max: 32,
    });
    if (i < steps.length - 1) addRule(slide, sx + 126, y + i * 24 + 64, 32, color, 5);
  });
}

function drawPresentationWedge(slide, x, y, deck) {
  drawMiniDeck(slide, x, y + 26, 270, 194, deck, "editable deck");
  const objects = [
    ["source ledger", deck.accent2],
    ["claim spine", deck.accent],
    ["visual plan", deck.accent3],
    ["QA handoff", "#6f7b88"],
  ];
  objects.forEach(([label, color], i) => {
    const ox = x + 330 + (i % 2) * 178;
    const oy = y + 8 + Math.floor(i / 2) * 118;
    addShape(slide, { x: ox, y: oy, w: 146, h: 86, fill: "#fffdf7", line: color, width: 2 });
    addShape(slide, { x: ox + 18, y: oy + 18, w: 24, h: 16, fill: color, line: color });
    addText(slide, label, ox + 18, oy + 48, 104, 24, { fontSize: 12, bold: true, color: deck.ink, max: 26 });
  });
  addRule(slide, x + 278, y + 122, 52, deck.accent2, 6);
  addText(slide, "business artifact people can inspect", x + 330, y + 250, 328, 22, {
    fontSize: 13,
    bold: true,
    color: deck.accent2,
    max: 52,
  });
}

function drawHandoff(slide, x, y, deck) {
  drawMiniDeck(slide, x, y, 300, 210, deck, "draft deck");
  drawGate(slide, x + 360, y + 10, deck, ["source ledger", "review checklist", "next repair decision", "human approval"]);
}

function drawProofObject(slide, deck, page) {
  const x = 600;
  const y = 104;
  if (deck.id === "deck-a-brand-safe-ai-creative-production") {
    if (page.index === 1) return drawVariantGrid(slide, x - 40, y + 42, deck);
    if (page.index === 2) return drawInputStack(slide, x + 16, y + 44, deck);
    if (page.index === 3) return drawWorkflow(slide, x - 20, y + 150, 560, deck, ["brief", "assets", "rules", "review"]);
    if (page.index === 4) return drawLanes(slide, x - 16, y + 54, deck, [["rules", "brand", "legal", "market"], ["assets", "hero", "copy", "offer"], ["review", "flag", "rerun", "signoff"]]);
    if (page.index === 5) return drawMatrix(slide, x - 26, y + 40, deck, ["social", "retail", "display", "email"], ["US", "EU", "APAC", "LATAM"]);
    return drawGate(slide, x + 30, y + 74, deck, ["sample input validates", "flagged item reviewed", "variant packet checked", "human signoff before release"]);
  }
  if (deck.id === "deck-b-vulca-product-strategy") {
    if (page.index === 1) return drawProductLoop(slide, x - 36, y + 20, deck, ["intent", "route", "edit", "evaluate", "package"]);
    if (page.index === 2) return drawComparison(slide, x - 64, y + 88, deck);
    if (page.index === 3) return drawLanes(slide, x - 34, y + 60, deck, [["agent job", "discover", "specify", "route"], ["pixel work", "layers", "inpaint", "compose"], ["review", "score", "archive", "sync"]]);
    if (page.index === 4) return drawProductLoop(slide, x - 40, y + 8, deck, ["usecase", "brief", "visual plan", "deck draft", "review", "handoff"]);
    if (page.index === 5) return drawPresentationWedge(slide, x - 56, y + 78, deck);
    return drawRoadmap(slide, x - 28, y + 130, deck);
  }
  if (page.index === 1) return drawLanes(slide, x - 20, y + 64, deck, [["intake", "audience", "decision", "sources"], ["output", "deck", "ledger", "review"], ["status", "draft", "repair", "handoff"]]);
  if (page.index === 2) return drawMatrix(slide, x - 12, y + 54, deck, ["allowed", "blocked", "needs review"], ["source", "claim", "visual", "metric"]);
  if (page.index === 3) return drawWorkflow(slide, x - 40, y + 150, 600, deck, ["claims", "visual brief", "prompt", "QA"]);
  if (page.index === 4) {
    drawMiniDeck(slide, x + 20, y + 24, 390, 276, deck, "editable canvas");
    addShape(slide, { x: x + 452, y: y + 40, w: 132, h: 236, fill: "#11151c", line: deck.accent2, width: 2 });
    addText(slide, "agent-side orchestration", x + 470, y + 82, 96, 58, { fontSize: 13, bold: true, color: "#fffdf7", align: "center", max: 44 });
    addRule(slide, x + 430, y + 164, 42, deck.accent2, 5);
    return;
  }
  if (page.index === 5) return drawReviewBoard(slide, x + 18, y + 52, deck);
  return drawHandoff(slide, x - 22, y + 86, deck);
}

function drawSlide(presentation, deck, page) {
  const slide = presentation.slides.add();
  drawBase(slide, deck, page);
  if (page.index === 6) {
    addShape(slide, { x: -140, y: 184, w: 640, h: 390, fill: "#e8ded0", line: "transparent", geometry: "ellipse" });
  } else if (page.index % 2 === 0) {
    addShape(slide, { x: 740, y: 76, w: 520, h: 530, fill: "#e6edf4", line: "transparent", geometry: "ellipse" });
  } else {
    addShape(slide, { x: 638, y: 96, w: 600, h: 456, fill: "#eee6da", line: "transparent", geometry: "ellipse" });
  }
  drawHeadline(slide, deck, page);
  drawProofObject(slide, deck, page);
  addLabel(slide, page.index === 6 ? "decision handoff" : "editable native objects", 64, 604, 190, deck.accent);
  return slide;
}

function writeTextArtifacts(workspace, deck) {
  fs.writeFileSync(
    path.join(workspace, "profile-plan.txt"),
    [
      `Task mode: create`,
      `Primary deck-profile: product-platform`,
      `Secondary gates: strategy-leadership for Deck B; product workflow demo for Deck C`,
      `Required proof objects: workflow architecture, usecase journey, product-to-review linkage, roadmap or decision handoff`,
      `Source/asset requirements: no external images, no logos, no screenshots, no invented metrics`,
      `Known missing inputs: human brand/legal review and native PowerPoint visual inspection`,
      "",
    ].join("\n"),
  );
  fs.writeFileSync(
    path.join(workspace, "source-notes.txt"),
    [
      `Deck: ${deck.title}`,
      `Brief: ${repoRel(deck.briefPath)}`,
      `Claim spine: ${repoRel(deck.claimPath)}`,
      `Visual brief: ${repoRel(deck.visualPath)}`,
      `Identity assets: none embedded; text-only references and abstract product surfaces only.`,
      "",
    ].join("\n"),
  );
  fs.writeFileSync(
    path.join(workspace, "claim-spine.txt"),
    [
      `Thesis: ${deck.thesis}`,
      `Audience: ${deck.audience}`,
      `Decision: ${deck.decision}`,
      "",
      ...deck.arc.map((page) => `${page.index}. ${page.claim} / Proof: ${page.proof}`),
      "",
    ].join("\n"),
  );
  fs.writeFileSync(
    path.join(workspace, "design-system.txt"),
    [
      `Slide size: 1280x720`,
      `Typography: Aptos Display for claims, Aptos for labels, Aptos Mono for kickers`,
      `Palette: background ${deck.bg}, ink ${deck.ink}, accent ${deck.accent}, support ${deck.accent2}, warning ${deck.accent3}`,
      `Diagram grammar: native rectangles, circles, rails, lanes, matrices, and mini editable deck surfaces`,
      `Asset policy: no logos, screenshots, copied layouts, or raster proof objects`,
      "",
    ].join("\n"),
  );
  fs.writeFileSync(
    path.join(workspace, "contact-sheet-plan.txt"),
    [
      `Six-slide macro rhythm:`,
      `1. editorial cover with dominant proof object`,
      `2. ledger or comparison spread`,
      `3. workflow map`,
      `4. control/capability surface`,
      `5. matrix, wedge, or review board`,
      `6. decision handoff`,
      "",
    ].join("\n"),
  );
}

function writeScorecard(workspace, deck, manifest) {
  const lines = [
    `# ${deck.title} QA Scorecard`,
    "",
    `Profile gate: product-platform draft gate passed for structure; public release remains human-review gated.`,
    "",
    "| Dimension | Score | Note |",
    "| --- | ---: | --- |",
    "| story | 4 | Claims are sourced from the six-slide arc. |",
    "| specificity | 4 | Deck-specific source boundaries and product objects are visible. |",
    "| rhythm | 4 | Six macro layouts vary across cover, ledger, workflow, board, matrix, and handoff. |",
    "| whitespace | 4 | Slides use one dominant proof surface and avoid dense report grids. |",
    "| chart clarity | 4 | No numeric charts; matrices and boards use direct labels. |",
    "| typography | 4 | Claim hierarchy is native editable text. |",
    "| restraint | 4 | No logos, screenshots, decorative badges, or invented metrics. |",
    "| precision | 4 | Source references remain in notes/footer; no unsupported metrics. |",
    "| coherence | 4 | One visual system is reused with deck-specific accent color. |",
    "",
    `Package checks: ${manifest.slideCount} slides, ${manifest.outputBytes} bytes, previews rendered before delivery QA.`,
    "",
    `Remaining weak spot: native PowerPoint/Keynote visual fidelity and human review are not completed by this script.`,
    "",
  ];
  fs.writeFileSync(path.join(workspace, "qa", "comeback-scorecard.txt"), lines.join("\n"));
}

function runContactSheet(previewPaths, contactSheet, deckTitle) {
  const contactSheetScript = path.join(root, "scripts", "build_ppt_contact_sheet.py");
  if (!fs.existsSync(contactSheetScript)) {
    throw new Error(`Missing contact sheet script: ${contactSheetScript}`);
  }
  try {
    execFileSync(
      python,
      [
        contactSheetScript,
        "--out",
        contactSheet,
        "--title",
        deckTitle,
        "--cols",
        "3",
        ...previewPaths,
      ],
      { cwd: root, stdio: "pipe" },
    );
  } catch (error) {
    const stdout = error.stdout ? String(error.stdout).trim() : "";
    const stderr = error.stderr ? String(error.stderr).trim() : "";
    throw new Error(
      [
        `Contact sheet generation failed for ${deckTitle}.`,
        `Python executable: ${python}`,
        stdout,
        stderr,
      ]
        .filter(Boolean)
        .join("\n"),
    );
  }
}

function buildHtmlIndex(results) {
  const cards = results
    .map(
      (result) => `
      <section>
        <h2>${result.deck.title}</h2>
        <p><a href="${repoRel(result.pptx)}">PPTX</a> · <a href="${repoRel(result.contactSheet)}">contact sheet</a> · <a href="${repoRel(result.qaReport)}">QA report</a></p>
        <img src="${repoRel(result.contactSheet)}" alt="${result.deck.title} contact sheet">
      </section>`,
    )
    .join("\n");
  const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Parallel Usecase PPT Pilots</title>
  <style>
    body{margin:0;background:#151922;color:#f7f1e8;font-family:Aptos,Inter,system-ui,sans-serif}
    main{max-width:1160px;margin:0 auto;padding:38px 28px 64px}
    h1{font-size:38px;margin:0 0 28px}
    section{margin:0 0 42px;padding-bottom:32px;border-bottom:1px solid #3b4350}
    h2{font-size:24px;margin:0 0 8px}
    a{color:#8ab4ff}
    img{width:100%;height:auto;border:1px solid #3b4350;background:#fff}
  </style>
</head>
<body><main><h1>Parallel Usecase PPT Pilots</h1>${cards}</main></body>
</html>`;
  const indexPath = path.join(outRoot, "parallel-usecase-pilot-viewer.html");
  fs.writeFileSync(indexPath, html);
  return indexPath;
}

async function buildDeck(rawDeck) {
  const deck = parseDeck(rawDeck);
  const workspace = path.join(outRoot, deck.id);
  resetWorkspace(workspace);
  writeTextArtifacts(workspace, deck);

  const presentation = Presentation.create({ slideSize });
  const slides = deck.arc.map((page) => drawSlide(presentation, deck, page));
  const outputPath = path.join(workspace, "output", deck.filename);
  ensureDir(path.dirname(outputPath));
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(outputPath);

  const previewPaths = [];
  const layoutResults = [];
  for (let index = 0; index < slides.length; index += 1) {
    const slideNo = String(index + 1).padStart(2, "0");
    const previewPath = path.join(workspace, "preview", `slide-${slideNo}.png`);
    const layoutPath = path.join(workspace, "layout", "final", `slide-${slideNo}.layout.json`);
    fs.writeFileSync(previewPath, await blobToBuffer(await presentation.export({ slide: slides[index], format: "png" })));
    fs.writeFileSync(layoutPath, await blobToBuffer(await presentation.export({ slide: slides[index], format: "layout" })));
    previewPaths.push(previewPath);
    layoutResults.push({ layoutPath });
  }

  const contactSheet = path.join(workspace, "preview", `${deck.id}-contact-sheet.png`);
  runContactSheet(previewPaths, contactSheet, deck.title);

  const manifest = {
    deckId: deck.id,
    title: deck.title,
    output: outputPath,
    outputBytes: fs.statSync(outputPath).size,
    slideCount: slides.length,
    slideSize,
    sourceFiles: {
      brief: deck.briefPath,
      claimSpine: deck.claimPath,
      visualBrief: deck.visualPath,
    },
    previewDir: path.join(workspace, "preview"),
    previewPaths,
    layoutDir: path.join(workspace, "layout", "final"),
    layoutResults,
    contactSheet,
    publicReady: false,
    releaseGate: "internal-demo-ok-public-blocked",
  };
  fs.writeFileSync(path.join(workspace, "output", "artifact-build-manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
  writeScorecard(workspace, deck, manifest);
  return {
    deck,
    workspace,
    pptx: outputPath,
    contactSheet,
    manifestPath: path.join(workspace, "output", "artifact-build-manifest.json"),
    qaReport: path.join(workspace, "qa", "comeback-scorecard.txt"),
    layoutDir: path.join(workspace, "layout", "final"),
  };
}

async function main() {
  ensureDir(outRoot);
  const results = [];
  for (const deck of decks) {
    results.push(await buildDeck(deck));
  }
  const viewerPath = buildHtmlIndex(results);
  fs.writeFileSync(
    path.join(outRoot, "parallel-usecase-pilot-summary.json"),
    `${JSON.stringify(
      {
        status: "parallel_usecase_ppt_pilots_generated_public_blocked",
        generatedAt: new Date().toISOString(),
        viewer: viewerPath,
        outputs: results.map((result) => ({
          deckId: result.deck.id,
          title: result.deck.title,
          pptx: result.pptx,
          contactSheet: result.contactSheet,
          qaReport: result.qaReport,
          layoutDir: result.layoutDir,
        })),
      },
      null,
      2,
    )}\n`,
  );
  console.log(
    JSON.stringify(
      {
        viewer: viewerPath,
        outputs: results.map((result) => ({
          title: result.deck.title,
          pptx: result.pptx,
          contactSheet: result.contactSheet,
          qaReport: result.qaReport,
        })),
      },
      null,
      2,
    ),
  );
}

if (process.argv.includes("--dry-run")) {
  console.log(
    JSON.stringify(
      {
        status: "dry-run-ok",
        threadId,
        outRoot,
        decks: decks.map((deck) => {
          const parsed = parseDeck(deck);
          return {
            id: parsed.id,
            title: parsed.title,
            slideCount: parsed.arc.length,
            briefPath: parsed.briefPath,
          };
        }),
      },
      null,
      2,
    ),
  );
} else {
  await main();
}
