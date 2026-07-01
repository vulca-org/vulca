import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const SLIDE = { width: 1280, height: 720 };

const COLORS = {
  bg: "#edf4f0",
  paper: "#fbfcfa",
  ink: "#16211d",
  muted: "#62716b",
  teal: "#007f73",
  tealDark: "#00695f",
  tealSoft: "#dff1ec",
  blue: "#0d6f91",
  blueSoft: "#e4f4f8",
  amber: "#9a6700",
  amberSoft: "#fff1d2",
  red: "#b63a31",
  redSoft: "#f8e0dc",
  panel: "#f7f6f1",
  line: "#c8d0cc",
  white: "#ffffff",
};

const SLIDE_PLAN = [
  {
    title: "VULCA Solution Pack v1",
    role: "Position the pack as release-evidence packets for AI-assisted visual assets.",
  },
  {
    title: "What VULCA Produces",
    role: "Map Lane A, Lane B, and Lane C without implying customer relationships.",
  },
  {
    title: "Before / After: AI Ad Workflow Handoff",
    role: "Make Lane C the hero proof with the Creatify source-safe card.",
  },
  {
    title: "Supporting Proof A: Product-Truth Evidence",
    role: "Show Lane A as structured product-truth evidence using the PROYA source-safe card.",
  },
  {
    title: "Supporting Proof B: AI Publishability Context",
    role: "Show Lane B as structured generated-asset publishability context using the Seedream source-safe card.",
  },
  {
    title: "A Bounded Pilot Shape",
    role: "Define intake, field read, evidence card, and readout.",
  },
  {
    title: "Review Ask And Boundaries",
    role: "Ask for workflow feedback while excluding legal, rights, platform, safety, and performance claims.",
  },
];

function assetPaths(root) {
  const base = path.join(root, "assets/research/vulca-evidence-packs/2026-06-20");
  return {
    creatifyCard: path.join(base, "creatify-deep-proof-v1/source-safe/creatify-source-safe-workflow-card-v1.png"),
    proyaCard: path.join(base, "proya-deep-proof-v1/vision-banana/proya-source-safe-distilled-card-v1.png"),
    seedreamCard: path.join(
      base,
      "seedream-byteplus-deep-proof-v1/source-safe/seedream-byteplus-source-safe-distilled-card-v1.png",
    ),
  };
}

async function readImageBlob(imagePath) {
  const bytes = await fs.readFile(imagePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function textBox(slide, name, text, position, style) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: 16,
    color: COLORS.ink,
    ...style,
  };
  return shape;
}

function rect(slide, name, position, fill, line = COLORS.line, radius = "rounded-lg") {
  return slide.shapes.add({
    geometry: "roundRect",
    name,
    position,
    fill,
    line: { style: "solid", fill: line, width: 1 },
    borderRadius: radius,
  });
}

function line(slide, name, left, top, width, fill = COLORS.teal) {
  slide.shapes.add({
    geometry: "rect",
    name,
    position: { left, top, width, height: 4 },
    fill,
    line: { style: "solid", fill, width: 0 },
  });
}

function addShell(slide, title, pageNumber, options = {}) {
  slide.background.fill = COLORS.bg;
  rect(slide, "paper", { left: 36, top: 30, width: 1208, height: 660 }, COLORS.paper, COLORS.paper, "rounded-lg");
  slide.shapes.add({
    geometry: "rect",
    name: "top-rule",
    position: { left: 36, top: 60, width: 1208, height: 10 },
    fill: COLORS.teal,
    line: { style: "solid", fill: COLORS.teal, width: 0 },
  });
  textBox(slide, "kicker", "VULCA SOLUTION PACK V1", { left: 72, top: 96, width: 420, height: 28 }, {
    fontSize: 16,
    color: COLORS.muted,
  });
  textBox(
    slide,
    "page-marker",
    `Public example sample / Page ${pageNumber}`,
    { left: 850, top: 96, width: 360, height: 28 },
    { fontSize: 16, color: COLORS.muted, alignment: "right" },
  );
  textBox(slide, "title", title, { left: 72, top: options.titleTop ?? 132, width: 1060, height: 68 }, {
    fontSize: options.titleSize ?? 40,
    bold: true,
    color: COLORS.ink,
  });
}

function addFooter(slide) {
  textBox(
    slide,
    "boundary-footer",
    "Named companies are public examples only. They do not imply a VULCA customer, partner, endorsement, authorization source, or finding.",
    { left: 72, top: 650, width: 1136, height: 30 },
    { fontSize: 11, color: COLORS.muted },
  );
}

function addPill(slide, name, text, left, top, width, fill, color) {
  rect(slide, `${name}-pill`, { left, top, width, height: 34 }, fill, color, "rounded-full");
  textBox(slide, `${name}-pill-text`, text, { left: left + 10, top: top + 7, width: width - 20, height: 22 }, {
    fontSize: 16,
    bold: true,
    color,
    alignment: "center",
  });
}

function addFieldCard(slide, name, title, body, position, fill, color, options = {}) {
  rect(slide, `${name}-card`, position, fill, color, options.radius ?? "rounded-lg");
  if (options.accent !== false) {
    slide.shapes.add({
      geometry: "rect",
      name: `${name}-accent`,
      position: { left: position.left, top: position.top, width: position.width, height: 8 },
      fill: color,
      line: { style: "solid", fill: color, width: 0 },
    });
  }
  textBox(slide, `${name}-title`, title, {
    left: position.left + 18,
    top: position.top + 20,
    width: position.width - 36,
    height: options.titleHeight ?? 28,
  }, { fontSize: options.titleSize ?? 17, bold: true, color });
  textBox(slide, `${name}-body`, body, {
    left: position.left + 18,
    top: position.top + (options.bodyTopOffset ?? 58),
    width: position.width - 36,
    height: position.height - (options.bodyTopOffset ?? 58) - 16,
  }, { fontSize: options.bodySize ?? 16, color: COLORS.ink });
}

function addMiniLabel(slide, name, text, position, color = COLORS.muted) {
  textBox(slide, name, text, position, {
    fontSize: 16,
    bold: true,
    color,
  });
}

async function addTitleSlide(presentation) {
  const slide = presentation.slides.add();
  addShell(slide, SLIDE_PLAN[0].title, 1, { titleSize: 52, titleTop: 130 });
  line(slide, "title-underline", 72, 206, 250);
  textBox(
    slide,
    "positioning-copy",
    "Release-evidence packets for AI-assisted visual assets.",
    { left: 72, top: 240, width: 820, height: 40 },
    { fontSize: 24, bold: true, color: COLORS.teal },
  );
  textBox(
    slide,
    "problem-copy",
    "AI-assisted visual production is scaling across commerce, campaign, generated media, and ad workflows. The bottleneck is no longer only making an asset. The bottleneck is explaining what it came from, what it represents, what still needs review, and who owns the release decision.",
    { left: 72, top: 318, width: 820, height: 156 },
    { fontSize: 20, color: COLORS.ink },
  );
  addPill(slide, "public", "public examples only", 72, 548, 190, COLORS.tealSoft, COLORS.tealDark);
  addPill(slide, "source", "source-backed", 282, 548, 168, COLORS.tealSoft, COLORS.tealDark);
  addPill(slide, "review", "human-reviewed", 470, 548, 172, COLORS.amberSoft, COLORS.amber);
  rect(slide, "right-proof-frame", { left: 950, top: 260, width: 190, height: 260 }, COLORS.panel, COLORS.line);
  addMiniLabel(slide, "right-proof-1", "source", { left: 985, top: 304, width: 120, height: 24 }, COLORS.teal);
  addMiniLabel(slide, "right-proof-2", "field read", { left: 985, top: 374, width: 120, height: 24 }, COLORS.amber);
  addMiniLabel(slide, "right-proof-3", "owner gate", { left: 985, top: 444, width: 120, height: 24 }, COLORS.red);
  addFooter(slide);
}

async function addLaneMap(presentation) {
  const slide = presentation.slides.add();
  addShell(slide, SLIDE_PLAN[1].title, 2);
  textBox(
    slide,
    "summary-copy",
    "A compact packet that connects source context, visual or generated-output fields, review questions, owner route, and a bounded human review gate.",
    { left: 72, top: 214, width: 1120, height: 46 },
    { fontSize: 18, color: COLORS.muted },
  );
  const laneTop = 306;
  const laneWidth = 342;
  addFieldCard(
    slide,
    "lane-a",
    "Lane A / Product-truth",
    "Existing commercial material and product claims become source-backed evidence cards: visible claim, product representation, source context, channel role, and release owner.",
    { left: 90, top: laneTop, width: laneWidth, height: 192 },
    COLORS.tealSoft,
    COLORS.tealDark,
    { bodySize: 16 },
  );
  addFieldCard(
    slide,
    "lane-b",
    "Lane B / AI publishability",
    "Generated assets are paired with input or reference context, model or workflow context, output state, label posture, unresolved fields, and owner route.",
    { left: 469, top: laneTop, width: laneWidth, height: 192 },
    COLORS.amberSoft,
    COLORS.amber,
    { bodySize: 16 },
  );
  addFieldCard(
    slide,
    "lane-c",
    "Lane C / AI ad workflow",
    "Product URL, listing, or brief-to-ad workflows become handoff packets: source input, generated candidate, review anatomy, export state, and campaign owner.",
    { left: 848, top: laneTop, width: laneWidth, height: 192 },
    COLORS.redSoft,
    COLORS.red,
    { bodySize: 16 },
  );
  textBox(
    slide,
    "reading-order",
    "Default reading order for this sample: Lane C is the main before/after workflow story. Lane A and Lane B show that the same source-backed method also works for product claims and generated assets.",
    { left: 90, top: 540, width: 1100, height: 58 },
    { fontSize: 18, color: COLORS.ink },
  );
  addFooter(slide);
}

async function addLaneCHero(presentation, assets) {
  const slide = presentation.slides.add();
  addShell(slide, SLIDE_PLAN[2].title, 3);
  addFieldCard(
    slide,
    "before",
    "Before VULCA",
    "Campaign candidates move faster than review context: source input, export state, missing fields, and owner route sit apart.",
    { left: 76, top: 242, width: 420, height: 164 },
    COLORS.redSoft,
    COLORS.red,
    { titleSize: 24, bodySize: 17 },
  );
  addFieldCard(
    slide,
    "after",
    "After VULCA",
    "The same flow becomes one packet: source input, generated candidate, review anatomy, missing-field list, owner route, and human gate.",
    { left: 76, top: 430, width: 420, height: 164 },
    COLORS.tealSoft,
    COLORS.teal,
    { titleSize: 24, bodySize: 17 },
  );
  rect(slide, "creatify-card-frame", { left: 552, top: 206, width: 670, height: 392 }, COLORS.white, COLORS.line);
  slide.images.add({
    blob: await readImageBlob(assets.creatifyCard),
    contentType: "image/png",
    alt: "Source-safe AI ad workflow evidence card",
    fit: "contain",
    position: { left: 576, top: 224, width: 622, height: 356 },
    geometry: "roundRect",
    borderRadius: "rounded-lg",
  });
  textBox(
    slide,
    "lane-c-proof-label",
    "Source-safe example card; not vendor proof or performance prediction.",
    { left: 576, top: 608, width: 622, height: 22 },
    { fontSize: 16, color: COLORS.muted },
  );
  addFooter(slide);
}

async function addLaneAProof(presentation, assets) {
  const slide = presentation.slides.add();
  addShell(slide, SLIDE_PLAN[3].title, 4);
  textBox(
    slide,
    "lane-a-summary",
    "A public product or campaign surface can be translated into reviewable fields before reuse.",
    { left: 72, top: 214, width: 900, height: 34 },
    { fontSize: 18, color: COLORS.muted },
  );
  addFieldCard(
    slide,
    "a-source",
    "1. Public source surface",
    "Material, product view, offer cue, and channel context.",
    { left: 82, top: 286, width: 262, height: 124 },
    COLORS.blueSoft,
    COLORS.blue,
  );
  addFieldCard(
    slide,
    "a-field",
    "2. VULCA field read",
    "Claim, representation, context, and owner route split into fields.",
    { left: 370, top: 286, width: 262, height: 124 },
    COLORS.tealSoft,
    COLORS.teal,
  );
  addFieldCard(
    slide,
    "a-output",
    "3. Review output",
    "Known, missing, and decision-owner fields become inspectable.",
    { left: 82, top: 434, width: 262, height: 124 },
    COLORS.amberSoft,
    COLORS.amber,
  );
  addFieldCard(
    slide,
    "a-boundary",
    "Boundary",
    "Workflow discussion only. No rights, platform, release, or relationship claim.",
    { left: 370, top: 434, width: 262, height: 124 },
    COLORS.amberSoft,
    COLORS.amber,
  );
  rect(slide, "proya-card-frame", { left: 660, top: 252, width: 540, height: 346 }, COLORS.white, COLORS.line);
  slide.images.add({
    blob: await readImageBlob(assets.proyaCard),
    contentType: "image/png",
    alt: "Source-safe product-truth evidence card",
    fit: "contain",
    position: { left: 682, top: 274, width: 496, height: 298 },
    geometry: "roundRect",
    borderRadius: "rounded-lg",
  });
  addFooter(slide);
}

async function addLaneBProof(presentation, assets) {
  const slide = presentation.slides.add();
  addShell(slide, SLIDE_PLAN[4].title, 5);
  textBox(
    slide,
    "lane-b-summary",
    "Generated media should not be reviewed as a file alone. The packet needs source or reference context, model or workflow context, output state, label posture, and owner route.",
    { left: 72, top: 210, width: 1040, height: 54 },
    { fontSize: 18, color: COLORS.muted },
  );
  addFieldCard(
    slide,
    "b-records",
    "1. Public records",
    "Official model, tool, and tutorial context become source records.",
    { left: 82, top: 292, width: 262, height: 122 },
    COLORS.blueSoft,
    COLORS.blue,
  );
  addFieldCard(
    slide,
    "b-normalized",
    "2. Normalized fields",
    "Model context, input reference, output state, label posture, owner.",
    { left: 370, top: 292, width: 262, height: 122 },
    COLORS.tealSoft,
    COLORS.teal,
  );
  addFieldCard(
    slide,
    "b-packet",
    "3. Review packet",
    "Reviewable, missing, source-backed, and not-yet-approved fields.",
    { left: 82, top: 430, width: 262, height: 132 },
    COLORS.amberSoft,
    COLORS.amber,
  );
  addFieldCard(
    slide,
    "b-boundary",
    "Boundary",
    "No scoring, certification, clearance, approval, or benchmarks.",
    { left: 370, top: 430, width: 262, height: 132 },
    COLORS.amberSoft,
    COLORS.amber,
  );
  rect(slide, "seedream-card-frame", { left: 660, top: 252, width: 540, height: 346 }, COLORS.white, COLORS.line);
  slide.images.add({
    blob: await readImageBlob(assets.seedreamCard),
    contentType: "image/png",
    alt: "Source-safe AI publishability evidence card",
    fit: "contain",
    position: { left: 682, top: 274, width: 496, height: 298 },
    geometry: "roundRect",
    borderRadius: "rounded-lg",
  });
  addFooter(slide);
}

async function addPilotShape(presentation) {
  const slide = presentation.slides.add();
  addShell(slide, SLIDE_PLAN[5].title, 6);
  textBox(
    slide,
    "pilot-summary",
    "The first useful step is small: public examples or sanitized assets, one review lane, a short readout, and a clear owner route.",
    { left: 72, top: 214, width: 1100, height: 42 },
    { fontSize: 18, color: COLORS.muted },
  );
  addFieldCard(
    slide,
    "pilot-intake",
    "1. Intake",
    "Public example, sanitized asset, product URL, listing, brief, or generated candidate.",
    { left: 90, top: 308, width: 518, height: 118 },
    COLORS.tealSoft,
    COLORS.teal,
    { titleSize: 21 },
  );
  addFieldCard(
    slide,
    "pilot-read",
    "2. Field Read",
    "Source context, visible claim or output context, review anatomy, output state, and missing fields.",
    { left: 672, top: 308, width: 518, height: 118 },
    COLORS.tealSoft,
    COLORS.teal,
    { titleSize: 21 },
  );
  addFieldCard(
    slide,
    "pilot-card",
    "3. Evidence Card",
    "A compact review object that a human owner can inspect and route.",
    { left: 90, top: 462, width: 518, height: 118 },
    COLORS.amberSoft,
    COLORS.amber,
    { titleSize: 21 },
  );
  addFieldCard(
    slide,
    "pilot-readout",
    "4. Readout",
    "What is ready to discuss, what is missing, who owns the next decision, and what should wait.",
    { left: 672, top: 462, width: 518, height: 118 },
    COLORS.amberSoft,
    COLORS.amber,
    { titleSize: 21 },
  );
  addFooter(slide);
}

async function addReviewAsk(presentation) {
  const slide = presentation.slides.add();
  addShell(slide, SLIDE_PLAN[6].title, 7);
  addFieldCard(
    slide,
    "ask",
    "Useful first response",
    "Which visual workflow should be turned into a source-backed review packet first: product-truth, AI publishability, or AI ad workflow handoff?",
    { left: 90, top: 270, width: 500, height: 150 },
    COLORS.tealSoft,
    COLORS.teal,
    { titleSize: 21 },
  );
  addFieldCard(
    slide,
    "what-we-show",
    "What the sample shows",
    "A repeatable packet shape: source context, representation or generated-output field read, unresolved questions, owner route, and human review gate.",
    { left: 90, top: 450, width: 500, height: 150 },
    COLORS.tealSoft,
    COLORS.teal,
    { titleSize: 21 },
  );
  addFieldCard(
    slide,
    "not-claims",
    "Not claiming",
    "No legal advice, rights clearance, platform approval, model-safety certification, release-readiness certification, performance measurement, ROI, CPA, CTR, ROAS, benchmark superiority, customer relationship, partnership, endorsement, authorization, or audit finding.",
    { left: 670, top: 270, width: 520, height: 330 },
    COLORS.redSoft,
    COLORS.red,
    { titleSize: 21, bodySize: 17 },
  );
  addFooter(slide);
}

async function main() {
  const configPath = process.argv[2];
  if (!configPath) {
    throw new Error("Usage: node customer_solution_pack_deck_builder.mjs <deck-config.json>");
  }
  const config = JSON.parse(await fs.readFile(configPath, "utf8"));
  await fs.mkdir(config.previewDir, { recursive: true });
  await fs.mkdir(config.layoutDir, { recursive: true });
  await fs.mkdir(config.qaDir, { recursive: true });

  const assets = assetPaths(config.root);
  const presentation = Presentation.create({ slideSize: SLIDE });

  await addTitleSlide(presentation);
  await addLaneMap(presentation);
  await addLaneCHero(presentation, assets);
  await addLaneAProof(presentation, assets);
  await addLaneBProof(presentation, assets);
  await addPilotShape(presentation);
  await addReviewAsk(presentation);

  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(
      path.join(config.previewDir, `${stem}.png`),
      await presentation.export({ slide, format: "png", scale: 1 }),
    );
    await fs.writeFile(path.join(config.layoutDir, `${stem}.layout.json`), await (await slide.export({ format: "layout" })).text());
  }

  await writeBlob(
    path.join(config.qaDir, "deck-contact-sheet.webp"),
    await presentation.export({
      format: "webp",
      montage: true,
      scale: 1,
    }),
  );

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(config.outputPptx);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
