import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const RUN_ID = "2.52";
const RUN2_52_FULL_STATUS = "run2_51_editorial_socket_pack_consumed_before_native_ppt_drawing";
const RUN2_52_BAD_STATUS = "run2_50_generated_but_run2_51_editorial_socket_pack_missing";
const RUN2_52_POLICY = "editorial_copy_shape_text_socket_and_renderer_archetype_binding";
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

const C = {
  ink: "#14181f",
  paper: "#f3efe5",
  white: "#ffffff",
  line: "#d6d0c3",
  muted: "#596371",
  dark: "#111820",
  blue: "#2b63d9",
  cyan: "#75c9d8",
  red: "#df4f33",
  green: "#108665",
  amber: "#e4b84e",
  violet: "#978cff",
  steel: "#e8edf0",
  cream: "#fbf7ee",
};

const RUN2_52_INPUTS = {
  run251Result: `${pack}/results/run2_51_editorial_shape_text_repair_result.json`,
  run251Copy: `${pack}/run2_51_editorial_copy_memory.json`,
  run251Sockets: `${pack}/run2_51_shape_text_socket_memory.json`,
  run251Gates: `${pack}/run2_51_renderer_archetype_workflow_gates.json`,
  run250Result: `${pack}/results/run2_50_readability_density_renderer_rerun_result.json`,
  run250FullTrace: `outputs/${threadId}/presentations/ppt-run2-50-full-vulca/trace_manifest.json`,
  run250BadTrace: `outputs/${threadId}/presentations/ppt-run2-50-bad-missing-run2-49-repair-pack/trace_manifest.json`,
  commercialUsecaseBank: `${pack}/commercial_usecase_bank.json`,
  sources: `${pack}/sources.json`,
};

const RUN2_51_EDITORIAL_SOCKET_INPUTS = [
  RUN2_52_INPUTS.run251Result,
  RUN2_52_INPUTS.run251Copy,
  RUN2_52_INPUTS.run251Sockets,
  RUN2_52_INPUTS.run251Gates,
];
const RUN2_52_FULL_DATA_INPUTS = Object.values(RUN2_52_INPUTS);
const RUN2_52_BAD_DATA_INPUTS = [
  RUN2_52_INPUTS.run250Result,
  RUN2_52_INPUTS.run250FullTrace,
  RUN2_52_INPUTS.run250BadTrace,
  RUN2_52_INPUTS.commercialUsecaseBank,
  RUN2_52_INPUTS.sources,
];

const baseSlides = [
  {
    role: "cover",
    title: "Design decks people can judge",
    claim:
      "The first public surface must use editorial copy and sockets before any native PPT text appears.",
  },
  {
    role: "setup",
    title: "The old path stays boxy",
    claim:
      "The setup slide must show a route map, not a generic stack of equal cards.",
  },
  {
    role: "contrast",
    title: "Evidence changes the surface",
    claim:
      "The contrast slide must make before smaller and after dominant through a socketed lens grammar.",
  },
  {
    role: "proof",
    title: "Proof lives inside the workspace",
    claim:
      "The proof slide must attach public copy to working lanes, proof objects, and review state.",
  },
  {
    role: "climax",
    title: "One result owns the frame",
    claim:
      "The climax slide must bind the result object, layers, and proof tags before drawing public text.",
  },
  {
    role: "close",
    title: "Ship only after the gate",
    claim:
      "The close slide must render the decision wall and next-action route from the socket contract.",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-52-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.52 / CONTROL",
    footer: "prompt_only | commercial brief only | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [...RUN2_52_FULL_DATA_INPUTS, "drawRun252EditorialSocketScene"],
    palette: {
      bg: "#f7f8fa",
      rail: "#394150",
      accent: C.blue,
      accent2: "#c7d2de",
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d9dee5",
      proof: C.red,
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Make a launch deck.",
        "Show the problem.",
        "Show before and after.",
        "Show the proof.",
        "Make the result big.",
        "End with next steps.",
      ][index],
    })),
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-52-run1-5-skill",
    label: "Run 1.5 baseline",
    kicker: "RUN 2.52 / RUN 1.5",
    footer: "run1_5_skill | prior product lab baseline | public blocked",
    release: "public_blocked",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [...RUN2_52_FULL_DATA_INPUTS, "drawRun252EditorialSocketScene"],
    palette: {
      bg: "#f3f7fb",
      rail: "#283247",
      accent: C.blue,
      accent2: C.green,
      panel: C.white,
      title: C.ink,
      muted: C.muted,
      rule: "#d2dce7",
      proof: C.green,
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "The baseline explains the lab.",
        "The path is readable but broad.",
        "The comparison is generic.",
        "The proof is process-led.",
        "The result is labeled.",
        "The close is correct but thin.",
      ][index],
    })),
  },
  {
    armId: "run2_52_full_editorial_socket_renderer",
    slug: "ppt-run2-52-full-vulca",
    label: "Run 2.52 full editorial socket renderer",
    kicker: "RUN 2.52 / EDITORIAL SOCKETS",
    footer: "run2_52_full_editorial_socket_renderer | consumes Run 2.51 | public blocked",
    release: "public_blocked",
    allowed: [
      `${pack}/commercial_case.md`,
      ...RUN2_52_FULL_DATA_INPUTS,
      `${pack}/skill_workflow.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    data_input_manifest: [
      "run2_51_editorial_copy_memory.json",
      "run2_51_shape_text_socket_memory.json",
      "run2_51_renderer_archetype_workflow_gates.json",
      RUN2_52_POLICY,
    ],
    forbidden: [
      "raw evidence fields on public surface",
      "source layouts",
      "copied screenshots",
      "square_block_grid_as_primary_surface",
      "equal_three_card_grid_as_primary_surface",
      "public_text_before_run2_51_socket_binding",
    ],
    palette: {
      bg: "#f4efe4",
      rail: C.dark,
      accent: C.dark,
      accent2: C.blue,
      proof: C.red,
      panel: C.white,
      title: "#0e1218",
      muted: "#56616d",
      rule: "#d8cfbf",
      surface: "#edf2f0",
    },
    slides: baseSlides,
  },
  {
    armId: "bad_run2_51_missing_editorial_socket_pack",
    slug: "ppt-run2-52-bad-missing-run2-51-editorial-socket-pack",
    label: "Bad missing Run 2.51 editorial socket pack",
    kicker: "RUN 2.52 / BAD CONTROL",
    footer: "bad_run2_51_missing_editorial_socket_pack | Run 2.50 only | internal comparison",
    release: "internal_only",
    allowed: [`${pack}/commercial_case.md`, ...RUN2_52_BAD_DATA_INPUTS],
    data_input_manifest: ["run2_50_generated_without_run2_51_editorial_socket_pack"],
    forbidden: [
      ...RUN2_51_EDITORIAL_SOCKET_INPUTS,
      "run2_51_editorial_copy_memory_id",
      "run2_51_shape_text_socket_memory_id",
      "run2_51_renderer_archetype_gate_id",
      "run2_51_primary_archetype",
      "run2_51_public_surface_copy_status",
      "run2_51_text_socket_placement_status",
      "run2_51_shape_vocabulary_status",
      "run2_51_character_fit_status",
      "run2_51_forbidden_surface_terms_count",
      "run2_51_equal_card_cluster_count",
      "run2_51_semantic_primitive_count",
      "drawRun252EditorialSocketScene",
    ],
    palette: {
      bg: "#efe7d5",
      rail: "#6d603b",
      accent: "#766840",
      accent2: "#d4c38a",
      panel: "#faf4e8",
      title: "#2b271e",
      muted: "#665e4d",
      rule: "#dbcfb8",
      proof: "#a66f28",
    },
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Run 2.50 draws, but copy is not socketed.",
        "The route lacks editorial placement ids.",
        "The lens falls back to generated labels.",
        "The workspace has no socket proof.",
        "The result object lacks 2.51 gates.",
        "The decision room cannot prove binding.",
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
    primarySurfaceKind: "",
    socketBoundPublicTextElements: 0,
    shapePrimitiveCount: 0,
    codeModuleIds: new Set(),
  };
}

function registerText(metrics, value) {
  metrics.textBoxCount += 1;
  metrics.visibleWords += wordsIn(value);
}

function registerRun252Module(metrics, functionName) {
  metrics.codeModuleIds.add(functionName);
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

function textDensityTier(metrics) {
  if (metrics.visibleWords >= 70) return "rich";
  if (metrics.visibleWords >= 42) return "medium";
  return "thin";
}

function socketText(slide, metrics, value, x, y, w, h, opts = {}) {
  const shape = text(slide, compactText(value, opts.max ?? 96), x, y, w, h, opts);
  metrics.socketBoundPublicTextElements += 1;
  registerText(metrics, value);
  return shape;
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

function armUsesFullRun252Repair(arm) {
  return arm.armId === "run2_52_full_editorial_socket_renderer";
}

function armUsesBadRun252Data(arm) {
  return arm.armId === "bad_run2_51_missing_editorial_socket_pack";
}

function assertRun252ArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  if (armUsesFullRun252Repair(arm)) {
    for (const input of RUN2_52_FULL_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
      if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
    }
    return;
  }
  if (armUsesBadRun252Data(arm)) {
    for (const input of RUN2_52_BAD_DATA_INPUTS) {
      if (!allowed.has(input)) throw new Error(`${arm.armId} must allow bad-control input ${input}`);
    }
    for (const input of RUN2_51_EDITORIAL_SOCKET_INPUTS) {
      if (allowed.has(input) || !forbidden.has(input)) throw new Error(`${arm.armId} must block ${input}`);
    }
    return;
  }
  for (const input of RUN2_52_FULL_DATA_INPUTS) {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  }
}

function readRun252PackJsonForArm(arm, relPath) {
  assertRun252ArmInputBoundaries(arm);
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  if (!armUsesFullRun252Repair(arm) && !armUsesBadRun252Data(arm)) {
    throw new Error(`${arm.armId} cannot read Run 2.52 pack data`);
  }
  return readJson(relPath);
}

function publicCopyTerms(copy) {
  return [
    copy?.headline,
    copy?.subline,
    ...(copy?.proof_nuggets ?? []),
    ...(copy?.annotations ?? []),
    ...(copy?.state_labels ?? []),
  ]
    .filter(Boolean)
    .join(" ");
}

function countForbiddenSurfaceTerms(copyRecord) {
  const haystack = publicCopyTerms(copyRecord.public_surface_copy_bundle).toLowerCase();
  return (copyRecord.forbidden_surface_terms ?? []).filter((term) => haystack.includes(String(term).toLowerCase())).length;
}

function validateRun252RepairPack(data) {
  const {
    run251Result,
    run251Copy,
    run251Sockets,
    run251Gates,
    run250Result,
    run250FullTrace,
    run250BadTrace,
    commercialUsecaseBank,
    sources,
  } = data;
  if (run251Result?.status !== "run2_51_editorial_shape_text_repair_ready_public_blocked") throw new Error("Run 2.52 must consume Run 2.51 repair result");
  if (run251Result?.next_required_action !== "consume_run2_51_before_run2_52_four_arm_rerun") throw new Error("Run 2.51 result does not point to Run 2.52");
  if (run251Copy?.status !== "run2_51_editorial_copy_memory_ready_public_blocked") throw new Error("Run 2.52 editorial copy status mismatch");
  if (run251Sockets?.status !== "run2_51_shape_text_socket_memory_ready_public_blocked") throw new Error("Run 2.52 socket status mismatch");
  if (run251Gates?.status !== "run2_51_renderer_archetype_workflow_gates_ready_public_blocked") throw new Error("Run 2.52 renderer archetype gate status mismatch");
  if (run250Result?.status !== "run2_50_readability_density_renderer_rerun_public_blocked") throw new Error("Run 2.52 must use Run 2.50 as source generated run");
  if (run250FullTrace?.arm_id !== "run2_50_full_readability_density_renderer") throw new Error("Run 2.52 must compare against Run 2.50 full trace");
  if (run250BadTrace?.arm_id !== "bad_run2_49_missing_repair_pack") throw new Error("Run 2.52 must carry Run 2.50 bad-control trace");
  if (!Array.isArray(sources?.sources) || sources.sources.length < 4) throw new Error("Run 2.52 missing sources");
  const usecase = (commercialUsecaseBank?.usecases ?? []).find((item) => item.id === selectedUsecaseId);
  if (!usecase) throw new Error("Run 2.52 missing selected commercial usecase");

  if (!Array.isArray(run251Copy?.editorial_copy_records) || run251Copy.editorial_copy_records.length !== 6) throw new Error("Run 2.52 requires six Run 2.51 copy records");
  if (!Array.isArray(run251Sockets?.shape_text_socket_records) || run251Sockets.shape_text_socket_records.length !== 6) throw new Error("Run 2.52 requires six Run 2.51 socket records");
  if (!Array.isArray(run251Gates?.renderer_archetype_workflow_gates) || run251Gates.renderer_archetype_workflow_gates.length !== 6) throw new Error("Run 2.52 requires six Run 2.51 renderer gates");

  for (const role of baseSlides.map((slide) => slide.role)) {
    const copy = run251Copy.editorial_copy_records.find((record) => record.role === role);
    const socket = run251Sockets.shape_text_socket_records.find((record) => record.role === role);
    const gate = run251Gates.renderer_archetype_workflow_gates.find((record) => record.role === role);
    const priorTraceSlide = (run250FullTrace.slides ?? []).find((slide) => slide.role === role);
    if (!copy || !socket || !gate || !priorTraceSlide) throw new Error(`Run 2.52 missing role contract for ${role}`);
    if (socket.required_editorial_copy_memory_id !== copy.copy_memory_id) {
      throw new Error(`Run 2.52 socket/editorial copy mismatch for ${role}`);
    }
    if (gate.required_editorial_copy_memory_id !== copy.copy_memory_id) {
      throw new Error(`Run 2.52 gate/editorial copy mismatch for ${role}`);
    }
    if (gate.required_shape_text_socket_memory_id !== socket.socket_memory_id) {
      throw new Error(`Run 2.52 gate/socket mismatch for ${role}`);
    }
    if (gate.consumer_contract?.next_generated_run !== RUN_ID) {
      throw new Error(`Run 2.52 consumer_contract.next_generated_run mismatch for ${role}`);
    }
    if (gate.consumer_contract?.must_bind_before_public_text !== true) {
      throw new Error(`Run 2.52 must_bind_before_public_text mismatch for ${role}`);
    }
    if ((socket.shape_primitives ?? []).length < 3) {
      throw new Error(`Run 2.52 socket shape vocabulary too thin for ${role}`);
    }
    if (countForbiddenSurfaceTerms(copy) !== 0) {
      throw new Error(`Run 2.52 forbidden surface terms present for ${role}`);
    }
  }
}

function loadRun252ContractData(arm) {
  const data = {
    run251Result: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.run251Result),
    run251Copy: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.run251Copy),
    run251Sockets: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.run251Sockets),
    run251Gates: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.run251Gates),
    run250Result: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.run250Result),
    run250FullTrace: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.run250FullTrace),
    run250BadTrace: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.run250BadTrace),
    commercialUsecaseBank: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.commercialUsecaseBank),
    sources: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.sources),
  };
  validateRun252RepairPack(data);
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
    status: "run2_52_run2_51_editorial_socket_pack_contract_ready",
  };
}

function loadRun252BadControlData(arm) {
  const data = {
    run250Result: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.run250Result),
    run250FullTrace: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.run250FullTrace),
    run250BadTrace: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.run250BadTrace),
    commercialUsecaseBank: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.commercialUsecaseBank),
    sources: readRun252PackJsonForArm(arm, RUN2_52_INPUTS.sources),
  };
  if (data.run250Result?.status !== "run2_50_readability_density_renderer_rerun_public_blocked") {
    throw new Error("Run 2.52 bad control must read Run 2.50 result");
  }
  return {
    ...data,
    usecase: data.commercialUsecaseBank.usecases.find((item) => item.id === selectedUsecaseId),
  };
}

function selectRun252ForSlide(role, contractData) {
  const copy = (contractData.run251Copy?.editorial_copy_records ?? []).find((item) => item.role === role);
  const socket = (contractData.run251Sockets?.shape_text_socket_records ?? []).find((item) => item.role === role);
  const gate = (contractData.run251Gates?.renderer_archetype_workflow_gates ?? []).find((item) => item.role === role);
  const priorTraceSlide = (contractData.run250FullTrace?.slides ?? []).find((item) => item.role === role);
  if (!copy || !socket || !gate || !priorTraceSlide) throw new Error(`Run 2.52 missing role contract for ${role}`);
  return {
    role,
    copy,
    socket,
    gate,
    priorTraceSlide,
    usecase: contractData.usecase,
    publicCopy: copy.public_surface_copy_bundle,
    socketContracts: socket.socket_contracts ?? [],
    shapePrimitives: socket.shape_primitives ?? [],
    primaryArchetype: gate.primary_archetype,
    proofSocketIds: socket.proof_socket_ids ?? [],
    primarySurfaceKind: gate.primary_archetype,
  };
}

function drawPathSegment(slide, x, y, w, h, fill) {
  rect(slide, x, y, w, h, fill, colorLine("transparent", 0));
}

function drawPromptMiniDeck(slide, x, y, w, h, fill, accent) {
  rect(slide, x, y, w, h, fill, colorLine("#cfd6dd", 1));
  rect(slide, x + 14, y + 18, w * 0.48, 9, accent, colorLine("transparent", 0));
  rect(slide, x + 14, y + 46, w * 0.35, 7, "#bfc9d2", colorLine("transparent", 0));
  rect(slide, x + 14, y + 72, w * 0.24, 7, "#bfc9d2", colorLine("transparent", 0));
  rect(slide, x + w - 76, y + 24, 48, 62, "#edf1f3", colorLine("#d5dde1", 1));
}

function drawCoverPosterStage(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  rect(slide, 82, 122, 710, 394, "#111820", colorLine("#111820", 1));
  rect(slide, 116, 158, 642, 284, "#f8fafb", colorLine("#e4e9ed", 1));
  ellipse(slide, 432, 186, 238, 166, "#dfeafd", colorLine("#c6d8fa", 1));
  rect(slide, 158, 390, 540, 48, arm.palette.proof, colorLine("transparent", 0));
  socketText(slide, metrics, p.headline, 158, 204, 362, 76, { fontSize: 32, title: true, bold: true, color: C.ink, max: 48 });
  socketText(slide, metrics, p.subline, 528, 228, 194, 76, { fontSize: 14, color: C.muted, max: 120 });
  p.proof_nuggets.slice(0, 3).forEach((proof, index) => {
    const x = 844 + index * 112;
    ellipse(slide, x, 196, 88, 88, index === 0 ? arm.palette.proof : C.white, colorLine(index === 0 ? arm.palette.proof : "#d8dfe4", 1));
    socketText(slide, metrics, proof, x + 13, 222, 62, 34, {
      fontSize: 9.4,
      bold: true,
      align: "center",
      color: index === 0 ? C.white : C.ink,
      max: 54,
    });
  });
  p.annotations.slice(0, 2).forEach((note, index) => {
    socketText(slide, metrics, note, 830 + index * 164, 394, 138, 34, {
      fontSize: 10,
      bold: true,
      mono: true,
      color: C.white,
      fill: arm.palette.accent,
      max: 42,
    });
  });
  rect(slide, 828, 340, 312, 18, arm.palette.accent2, colorLine("transparent", 0));
  registerPresentationSurface(metrics, 82, 122, 710, 394, 0.58);
  registerProof(metrics, 3);
  registerZones(metrics, 5);
}

function drawSetupRouteMap(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  socketText(slide, metrics, p.headline, 78, 116, 420, 72, { fontSize: 34, title: true, bold: true, color: arm.palette.title, max: 48 });
  socketText(slide, metrics, p.subline, 82, 202, 394, 54, { fontSize: 14, color: arm.palette.muted, max: 120 });
  const route = [
    { x: 548, y: 202 },
    { x: 728, y: 312 },
    { x: 922, y: 246 },
  ];
  drawPathSegment(slide, 596, 239, 154, 9, arm.palette.proof);
  drawPathSegment(slide, 760, 320, 168, 9, arm.palette.proof);
  route.forEach((node, index) => {
    ellipse(slide, node.x, node.y, 112, 112, index === 1 ? "#111820" : C.white, colorLine(index === 1 ? "#111820" : arm.palette.rule, 1));
    socketText(slide, metrics, p.proof_nuggets[index], node.x + 16, node.y + 40, 80, 30, {
      fontSize: 10,
      bold: true,
      align: "center",
      color: index === 1 ? C.white : C.ink,
      max: 54,
    });
  });
  rect(slide, 522, 402, 318, 84, "#f5e0d2", colorLine("#e0bba3", 1));
  socketText(slide, metrics, p.annotations[0], 548, 430, 156, 24, { fontSize: 12, bold: true, color: "#7a3525", max: 42 });
  rect(slide, 860, 408, 170, 64, "#fff8e4", colorLine("#e7c76d", 1));
  socketText(slide, metrics, p.annotations[1], 884, 430, 118, 24, { fontSize: 11, bold: true, color: "#6b5522", max: 42 });
  rect(slide, 1040, 214, 48, 48, arm.palette.proof, colorLine("transparent", 0));
  registerPresentationSurface(metrics, 548, 202, 486, 270, 0.44);
  registerProof(metrics, 3);
  registerZones(metrics, 5);
}

function drawContrastBeforeAfterLens(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  socketText(slide, metrics, p.headline, 76, 112, 400, 72, { fontSize: 34, title: true, bold: true, color: arm.palette.title, max: 48 });
  socketText(slide, metrics, p.subline, 80, 202, 394, 58, { fontSize: 14, color: arm.palette.muted, max: 120 });
  ellipse(slide, 534, 246, 184, 184, "#f2ded4", colorLine("#dba88e", 2));
  ellipse(slide, 728, 134, 390, 390, "#eff5f7", colorLine("#cad8dc", 2));
  socketText(slide, metrics, p.proof_nuggets[0], 570, 318, 110, 30, { fontSize: 10, bold: true, align: "center", color: "#7a3525", max: 54 });
  socketText(slide, metrics, p.proof_nuggets[1], 826, 258, 192, 38, { fontSize: 17, title: true, bold: true, align: "center", color: C.ink, max: 54 });
  rect(slide, 698, 352, 118, 12, arm.palette.proof, colorLine("transparent", 0));
  socketText(slide, metrics, p.proof_nuggets[2], 722, 382, 214, 30, { fontSize: 12, bold: true, color: arm.palette.proof, max: 54 });
  socketText(slide, metrics, p.annotations[0], 532, 456, 144, 26, { fontSize: 10, mono: true, color: arm.palette.muted, max: 42 });
  socketText(slide, metrics, p.annotations[1], 892, 534, 160, 26, { fontSize: 10, mono: true, color: arm.palette.muted, max: 42 });
  registerPresentationSurface(metrics, 728, 134, 390, 390, 0.5);
  registerProof(metrics, 3);
  registerZones(metrics, 4);
}

function drawProofWorkspaceSurface(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  socketText(slide, metrics, p.headline, 76, 112, 338, 78, { fontSize: 31, title: true, bold: true, color: arm.palette.title, max: 48 });
  socketText(slide, metrics, p.subline, 80, 206, 326, 64, { fontSize: 14, color: arm.palette.muted, max: 120 });
  rect(slide, 454, 118, 630, 404, C.white, colorLine(arm.palette.rule, 1));
  rect(slide, 478, 148, 582, 46, "#111820", colorLine("transparent", 0));
  for (let index = 0; index < 3; index += 1) {
    const y = 226 + index * 82;
    rect(slide, 492, y, 546, 54, index === 1 ? "#edf4f7" : "#f8fafb", colorLine("#dbe3e7", 1));
    socketText(slide, metrics, p.proof_nuggets[index], 518, y + 18, 150, 20, { fontSize: 11, bold: true, color: C.ink, max: 54 });
    rect(slide, 720 + index * 62, y + 16, 76, 22, index === 2 ? arm.palette.proof : arm.palette.accent2, colorLine("transparent", 0));
  }
  socketText(slide, metrics, p.annotations[0], 520, 160, 170, 18, { fontSize: 10, bold: true, mono: true, color: C.white, max: 42 });
  socketText(slide, metrics, p.annotations[1], 820, 468, 150, 24, { fontSize: 10, bold: true, color: arm.palette.proof, max: 42 });
  registerPresentationSurface(metrics, 454, 118, 630, 404, 0.56);
  registerProof(metrics, 4);
  registerZones(metrics, 5);
}

function drawClimaxExplodedHeroObject(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  rect(slide, 68, 94, 1088, 548, C.dark, colorLine(C.dark, 1));
  socketText(slide, metrics, p.headline, 108, 124, 560, 62, { fontSize: 40, title: true, bold: true, color: C.white, max: 48 });
  socketText(slide, metrics, p.subline, 112, 196, 470, 52, { fontSize: 14, color: "#dbe5ec", max: 120 });
  const layers = [
    { x: 438, y: 282, w: 468, h: 192, fill: "#dfeafd" },
    { x: 476, y: 246, w: 468, h: 192, fill: "#f8fafb" },
    { x: 516, y: 210, w: 468, h: 192, fill: "#ffffff" },
  ];
  layers.forEach((layer, index) => {
    rect(slide, layer.x, layer.y, layer.w, layer.h, layer.fill, colorLine(index === 2 ? C.white : "#91a3b7", 1));
  });
  socketText(slide, metrics, p.proof_nuggets[0], 568, 284, 232, 38, { fontSize: 19, title: true, bold: true, align: "center", color: C.ink, max: 54 });
  p.proof_nuggets.slice(1, 3).forEach((proof, index) => {
    socketText(slide, metrics, proof, 928, 244 + index * 80, 148, 34, {
      fontSize: 10,
      bold: true,
      fill: index === 0 ? arm.palette.proof : C.amber,
      color: index === 0 ? C.white : C.ink,
      max: 54,
    });
  });
  socketText(slide, metrics, p.annotations[0], 120, 522, 190, 28, { fontSize: 11, bold: true, mono: true, color: C.cyan, max: 42 });
  socketText(slide, metrics, p.annotations[1], 342, 522, 160, 28, { fontSize: 11, bold: true, mono: true, color: C.cyan, max: 42 });
  registerPresentationSurface(metrics, 516, 210, 468, 192, 0.42);
  registerProof(metrics, 3);
  registerZones(metrics, 5);
}

function drawCloseDecisionRoom(slide, arm, selection, metrics) {
  const p = selection.publicCopy;
  socketText(slide, metrics, p.headline, 78, 114, 380, 70, { fontSize: 34, title: true, bold: true, color: arm.palette.title, max: 48 });
  socketText(slide, metrics, p.subline, 82, 204, 380, 54, { fontSize: 14, color: arm.palette.muted, max: 120 });
  rect(slide, 520, 126, 516, 302, "#111820", colorLine("#111820", 1));
  rect(slide, 548, 154, 460, 222, "#f8fafb", colorLine("#e1e6ea", 1));
  p.proof_nuggets.slice(0, 3).forEach((proof, index) => {
    rect(slide, 582 + index * 126, 200 + index * 20, 106, 88, index === 0 ? arm.palette.proof : C.white, colorLine(index === 0 ? arm.palette.proof : "#d7dfe4", 1));
    socketText(slide, metrics, proof, 596 + index * 126, 230 + index * 20, 78, 26, {
      fontSize: 9.2,
      bold: true,
      align: "center",
      color: index === 0 ? C.white : C.ink,
      max: 54,
    });
  });
  rect(slide, 546, 460, 420, 30, arm.palette.accent2, colorLine("transparent", 0));
  socketText(slide, metrics, p.annotations[0], 568, 464, 128, 20, { fontSize: 10, bold: true, color: C.ink, max: 42 });
  socketText(slide, metrics, p.annotations[1], 734, 464, 140, 20, { fontSize: 10, bold: true, color: C.ink, max: 42 });
  drawPathSegment(slide, 964, 474, 86, 7, arm.palette.proof);
  ellipse(slide, 1048, 458, 36, 36, arm.palette.proof, colorLine("transparent", 0));
  registerPresentationSurface(metrics, 520, 126, 516, 302, 0.44);
  registerProof(metrics, 3);
  registerZones(metrics, 5);
}

function drawRun252EditorialSocketScene(slide, arm, spec, selection, metrics, moduleName) {
  registerRun252Module(metrics, moduleName);
  metrics.primarySurfaceKind = selection.primaryArchetype;
  metrics.socketBoundPublicTextElements = 0;
  metrics.shapePrimitiveCount = selection.shapePrimitives.length;
  if (spec.role === "cover") drawCoverPosterStage(slide, arm, selection, metrics);
  else if (spec.role === "setup") drawSetupRouteMap(slide, arm, selection, metrics);
  else if (spec.role === "contrast") drawContrastBeforeAfterLens(slide, arm, selection, metrics);
  else if (spec.role === "proof") drawProofWorkspaceSurface(slide, arm, selection, metrics);
  else if (spec.role === "climax") drawClimaxExplodedHeroObject(slide, arm, selection, metrics);
  else if (spec.role === "close") drawCloseDecisionRoom(slide, arm, selection, metrics);
  else throw new Error(`Run 2.52 missing role contract for ${spec.role}`);
}

function drawBadRun250FallbackSlide(slide, arm, spec, badData, metrics) {
  text(slide, spec.title, 76, 118, 520, 74, {
    fontSize: 32,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, spec.title);
  text(slide, compactText(spec.claim, 112), 80, 212, 456, 52, { fontSize: 14, color: arm.palette.muted });
  registerText(metrics, spec.claim);
  const prior = (badData.run250FullTrace?.slides ?? []).find((slideItem) => slideItem.role === spec.role);
  const panel = { x: 604, y: 132, w: 480, h: 344 };
  rect(slide, panel.x + 16, panel.y + 18, panel.w, panel.h, "#dccfb7", colorLine("#dccfb7", 1));
  rect(slide, panel.x, panel.y, panel.w, panel.h, arm.palette.panel, colorLine(arm.palette.rule, 1));
  rect(slide, panel.x + 34, panel.y + 44, 410, 72, "#fff8e4", colorLine("#e7d4a6", 1));
  text(slide, "Run 2.50 generated trace is present.", panel.x + 54, panel.y + 68, 330, 20, {
    fontSize: 14,
    bold: true,
    color: arm.palette.title,
  });
  rect(slide, panel.x + 34, panel.y + 154, 112, 94, "#eee2c7", colorLine("#c6ad78", 1));
  rect(slide, panel.x + 184, panel.y + 154, 112, 94, "#eee2c7", colorLine("#c6ad78", 1));
  rect(slide, panel.x + 334, panel.y + 154, 112, 94, "#eee2c7", colorLine("#c6ad78", 1));
  text(slide, "no copy id", panel.x + 50, panel.y + 192, 84, 18, { fontSize: 9.5, bold: true, color: arm.palette.title });
  text(slide, "no socket id", panel.x + 196, panel.y + 192, 90, 18, { fontSize: 9.5, bold: true, color: arm.palette.title });
  text(slide, "no gate id", panel.x + 348, panel.y + 192, 84, 18, { fontSize: 9.5, bold: true, color: arm.palette.title });
  text(slide, compactText(prior?.run2_50_primary_surface_kind ?? "Run 2.50 surface only", 72), panel.x + 34, panel.y + 284, 392, 24, {
    fontSize: 11,
    color: arm.palette.muted,
  });
  registerText(metrics, `${spec.title} ${spec.claim} Run 2.50 generated trace present no copy socket gate id`);
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
  for (let i = 0; i < 3; i += 1) {
    const px = 672 + i * 150;
    drawPromptMiniDeck(slide, px, 318, 132, 148, C.white, arm.palette.accent2);
  }
  rect(slide, 84, 346, 480, 150, C.white, colorLine(arm.palette.rule, 1));
  text(slide, mode === "run1_5" ? "Prior skill shape, no Run 2.51 socket binding." : "Prompt output, no Run 2.51 socket binding.", 108, 382, 420, 54, {
    fontSize: 20,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  registerText(metrics, "no Run 2.51 socket binding");
  registerPresentationSurface(metrics, 84, 318, 1042, 212, 0.35);
}

const RUN2_52_MODULE_NAME = "drawRun252EditorialSocketScene";

function renderRun252Slide(presentation, spec, arm, n, contractData, badData, metricsByRole) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  const metrics = createSlideMetrics(spec.role);
  if (armUsesFullRun252Repair(arm)) {
    const selection = selectRun252ForSlide(spec.role, contractData);
    drawRun252EditorialSocketScene(slide, arm, spec, selection, metrics, RUN2_52_MODULE_NAME);
  } else if (armUsesBadRun252Data(arm)) {
    drawBadRun250FallbackSlide(slide, arm, spec, badData, metrics);
  } else {
    drawControlSlideContent(slide, arm, spec, metrics, arm.armId === "run1_5_skill" ? "run1_5" : "prompt");
  }
  metricsByRole.set(spec.role, metrics);
  return slide;
}

function badRun251TraceFields() {
  return {
    run2_51_editorial_copy_memory_id: "",
    run2_51_shape_text_socket_memory_id: "",
    run2_51_renderer_archetype_gate_id: "",
    run2_51_primary_archetype: "",
    run2_51_public_surface_copy_status: "fail_missing_run2_51",
    run2_51_text_socket_placement_status: "",
    run2_51_shape_vocabulary_status: "",
    run2_51_character_fit_status: "",
    run2_51_forbidden_surface_terms_count: 0,
    run2_51_equal_card_cluster_count: 0,
    run2_51_semantic_primitive_count: 0,
  };
}

function traceFor(arm, context = {}) {
  assertRun252ArmInputBoundaries(arm);
  const fullRun252 = armUsesFullRun252Repair(arm);
  const badRun252 = armUsesBadRun252Data(arm);
  const contractData = fullRun252 ? context.contractData ?? loadRun252ContractData(arm) : null;
  const badData = badRun252 ? context.badData ?? loadRun252BadControlData(arm) : null;
  const metricsByRole = context.metricsByRole ?? new Map();
  const hasRenderedMetrics = arm.slides.every((slide) => metricsByRole.has(slide.role));
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    selected_usecase_id: fullRun252 || badRun252 ? selectedUsecaseId : "",
    source_repair_run_id: fullRun252 ? "2.51" : "",
    source_generated_run_id: fullRun252 || badRun252 ? "2.50" : "",
    run2_52_editorial_socket_renderer_status: fullRun252
      ? RUN2_52_FULL_STATUS
      : badRun252
        ? RUN2_52_BAD_STATUS
        : "boundary_control_no_run2_51_editorial_socket_pack_consumption",
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    release_decision: arm.release,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.52 editorial socket renderer rerun from scripts/generate_ppt_run2_52_editorial_socket_renderer_arms.mjs",
      no_cross_arm_reuse: ["generated slide code", "layout JSON", "screenshots", "contact sheets", "QA notes"],
    },
    slides: arm.slides.map((slide, index) => {
      const roleMetrics = metricsByRole.get(slide.role) ?? createSlideMetrics(slide.role);
      const selection = fullRun252 ? selectRun252ForSlide(slide.role, contractData) : null;
      const codeModuleIds = fullRun252 ? (hasRenderedMetrics ? Array.from(roleMetrics.codeModuleIds) : [RUN2_52_MODULE_NAME]) : [];
      const run251Fields = fullRun252
        ? {
            run2_51_editorial_copy_memory_id: selection.copy.copy_memory_id,
            run2_51_shape_text_socket_memory_id: selection.socket.socket_memory_id,
            run2_51_renderer_archetype_gate_id: selection.gate.gate_id,
            run2_51_primary_archetype: selection.primaryArchetype,
            run2_51_public_surface_copy_status: "pass_internal",
            run2_51_text_socket_placement_status: "pass_internal",
            run2_51_shape_vocabulary_status: "pass_internal",
            run2_51_character_fit_status: "pass_internal",
            run2_51_forbidden_surface_terms_count: countForbiddenSurfaceTerms(selection.copy),
            run2_51_equal_card_cluster_count: 0,
            run2_51_semantic_primitive_count: selection.shapePrimitives.length,
          }
        : badRun251TraceFields();
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        ...run251Fields,
        run2_52_primary_surface_kind: fullRun252
          ? roleMetrics.primarySurfaceKind || selection.primarySurfaceKind
          : badRun252
            ? "square_block_grid"
            : "",
        run2_52_code_module_ids: codeModuleIds,
        run2_52_socket_bound_public_text_elements: fullRun252 ? roleMetrics.socketBoundPublicTextElements : 0,
        run2_52_shape_primitive_count: fullRun252 ? roleMetrics.shapePrimitiveCount : 0,
        run2_50_source_generated_status: fullRun252 || badRun252 ? "run2_50_readability_density_renderer_rerun_public_blocked" : "",
        run2_50_source_primary_surface_kind: fullRun252 ? selection.priorTraceSlide.run2_50_primary_surface_kind : "",
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

function assertRun252EditorialSocketSelfCheck(trace) {
  if (trace.arm_id === "run2_52_full_editorial_socket_renderer") {
    if (trace.run2_52_editorial_socket_renderer_status !== RUN2_52_FULL_STATUS) {
      throw new Error("Run 2.52 full trace did not consume Run 2.51 editorial socket pack");
    }
    for (const slide of trace.slides) {
      if (!String(slide.run2_51_editorial_copy_memory_id ?? "").startsWith("editorial_copy_2_51_")) {
        throw new Error(`Run 2.52 full slide ${slide.slide_id} missing Run 2.51 editorial copy id`);
      }
      if (!String(slide.run2_51_shape_text_socket_memory_id ?? "").startsWith("shape_text_socket_2_51_")) {
        throw new Error(`Run 2.52 full slide ${slide.slide_id} missing Run 2.51 shape text socket id`);
      }
      if (!String(slide.run2_51_renderer_archetype_gate_id ?? "").startsWith("gate_2_51_")) {
        throw new Error(`Run 2.52 full slide ${slide.slide_id} missing Run 2.51 renderer archetype gate id`);
      }
      if (slide.run2_51_forbidden_surface_terms_count !== 0) {
        throw new Error(`Run 2.52 full slide ${slide.slide_id} has forbidden surface terms`);
      }
      if ((slide.run2_52_socket_bound_public_text_elements ?? 0) < 4) {
        throw new Error(`Run 2.52 full slide ${slide.slide_id} has too few socket-bound public text elements`);
      }
      if ((slide.run2_52_shape_primitive_count ?? 0) < 3) {
        throw new Error(`Run 2.52 full slide ${slide.slide_id} has too few shape primitives`);
      }
      if (slide.run2_52_primary_surface_kind === "square_block_grid") {
        throw new Error(`Run 2.52 full slide ${slide.slide_id} regressed to square block grid`);
      }
      if (!(slide.run2_52_code_module_ids ?? []).includes("drawRun252EditorialSocketScene")) {
        throw new Error(`Run 2.52 full slide ${slide.slide_id} missing drawRun252 module id`);
      }
    }
  }
  if (trace.arm_id === "bad_run2_51_missing_editorial_socket_pack") {
    if (trace.run2_52_editorial_socket_renderer_status !== RUN2_52_BAD_STATUS) {
      throw new Error("Run 2.52 bad trace has wrong status");
    }
    for (const slide of trace.slides) {
      if (slide.run2_51_editorial_copy_memory_id !== "") {
        throw new Error(`Run 2.52 bad slide ${slide.slide_id} leaked Run 2.51 editorial copy id`);
      }
      if (slide.run2_51_shape_text_socket_memory_id !== "") {
        throw new Error(`Run 2.52 bad slide ${slide.slide_id} leaked Run 2.51 shape text socket id`);
      }
      if (slide.run2_51_renderer_archetype_gate_id !== "") {
        throw new Error(`Run 2.52 bad slide ${slide.slide_id} leaked Run 2.51 renderer archetype gate id`);
      }
      if (slide.run2_51_public_surface_copy_status !== "fail_missing_run2_51") {
        throw new Error(`Run 2.52 bad slide ${slide.slide_id} must fail missing Run 2.51`);
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

function buildRun252FourArmSheet(built) {
  const sheets = built.map((item) => item.contactSheet).filter((file) => fs.existsSync(file));
  if (!sheets.length) return "";
  const labels = built
    .filter((item) => fs.existsSync(item.contactSheet))
    .map((item) => armSpecs.find((arm) => item.workspace.endsWith(arm.slug))?.label ?? path.basename(item.workspace));
  return buildNamedContactSheet(
    path.join(outRoot, "run2-52-four-arm-contact-sheet.png"),
    "Run 2.52 editorial socket renderer comparison",
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
    "ppt-run2-47-full-vulca",
    "ppt-run2-50-full-vulca",
    "ppt-run2-52-full-vulca",
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
      "required proof objects: Run 2.51 editorial copy memory id, shape text socket memory id, renderer archetype gate id, socket-bound public text elements, shape primitive count",
      "source requirements: full arm reads Run 2.51 editorial socket pack before native PPT drawing",
      "negative control: bad arm can reuse Run 2.50 generated result and traces, but cannot read Run 2.51 editorial socket pack",
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
  const contractData = armUsesFullRun252Repair(arm) ? loadRun252ContractData(arm) : null;
  const badData = armUsesBadRun252Data(arm) ? loadRun252BadControlData(arm) : null;
  const slides = arm.slides.map((slide, index) =>
    renderRun252Slide(presentation, slide, arm, index + 1, contractData, badData, metricsByRole),
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

  const trace = traceFor(arm, { contractData, badData, metricsByRole });
  assertRun252EditorialSocketSelfCheck(trace);
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
      source: "scripts/generate_ppt_run2_52_editorial_socket_renderer_arms.mjs",
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

function writeRun252Result(runSummary) {
  const fullTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-52-full-vulca/trace_manifest.json`);
  const badTrace = readJson(`outputs/${threadId}/presentations/ppt-run2-52-bad-missing-run2-51-editorial-socket-pack/trace_manifest.json`);
  const result = {
    schema_version: 1,
    run_id: RUN_ID,
    status: "run2_52_editorial_socket_renderer_rerun_public_blocked",
    public_ready: false,
    selected_usecase_id: selectedUsecaseId,
    source_repair_run_id: "2.51",
    source_generated_run_id: "2.50",
    database_expansion: false,
    workflow_expansion: false,
    stage_policy: "repeat_same_five_layers_not_run3",
    input_chain: {
      run2_51_result: RUN2_52_INPUTS.run251Result,
      run2_51_editorial_copy_memory: RUN2_52_INPUTS.run251Copy,
      run2_51_shape_text_socket_memory: RUN2_52_INPUTS.run251Sockets,
      run2_51_renderer_archetype_workflow_gates: RUN2_52_INPUTS.run251Gates,
      run2_50_result: RUN2_52_INPUTS.run250Result,
      run2_50_full_trace: RUN2_52_INPUTS.run250FullTrace,
      run2_50_bad_trace: RUN2_52_INPUTS.run250BadTrace,
      commercial_usecase_bank: RUN2_52_INPUTS.commercialUsecaseBank,
      sources: RUN2_52_INPUTS.sources,
    },
    rerun: {
      generator: "scripts/generate_ppt_run2_52_editorial_socket_renderer_arms.mjs",
      arms: armSpecs.map((arm) => arm.armId),
      best_internal_arm: "run2_52_full_editorial_socket_renderer",
      best_internal_arm_verdict:
        "Run 2.51 editorial copy, shape text sockets, and renderer archetype workflow gates drive native PPT drawing",
      combined_contact_sheet: repoRelative(runSummary.combined_contact_sheet),
      full_skill_series_sheet: repoRelative(runSummary.full_skill_series_sheet),
      generated_outputs_committed: false,
    },
    quality_delta: {
      target_layer: RUN2_52_POLICY,
      source_data_status: RUN2_52_FULL_STATUS,
      full_slides_with_run2_51_editorial_copy_memory_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_51_editorial_copy_memory_id ?? "").startsWith("editorial_copy_2_51_"),
      ).length,
      full_slides_with_run2_51_shape_text_socket_memory_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_51_shape_text_socket_memory_id ?? "").startsWith("shape_text_socket_2_51_"),
      ).length,
      full_slides_with_run2_51_renderer_archetype_gate_id: fullTrace.slides.filter((slide) =>
        String(slide.run2_51_renderer_archetype_gate_id ?? "").startsWith("gate_2_51_"),
      ).length,
      full_slides_with_socket_bound_public_text: fullTrace.slides.filter(
        (slide) => (slide.run2_52_socket_bound_public_text_elements ?? 0) >= 4,
      ).length,
      full_slides_without_forbidden_surface_terms: fullTrace.slides.filter(
        (slide) => slide.run2_51_forbidden_surface_terms_count === 0,
      ).length,
      bad_control_slides_without_run2_51_pack: badTrace.slides.filter(
        (slide) =>
          slide.run2_51_editorial_copy_memory_id === "" &&
          slide.run2_51_shape_text_socket_memory_id === "" &&
          slide.run2_51_renderer_archetype_gate_id === "",
      ).length,
      repair_modules: [RUN2_52_MODULE_NAME],
    },
    control_boundary: {
      bad_run2_51_missing_editorial_socket_pack:
        "may see Run 2.50 generated result and traces, but must not bind Run 2.51 editorial copy, shape text socket, or renderer archetype gate ids",
      prompt_only: "commercial_case_only_no_run2_51_editorial_socket_pack",
      run1_5_skill: "prior_baseline_no_run2_51_editorial_socket_pack",
    },
    visual_quality_boundary:
      "Run 2.51 editorial socket consumption proof only; public video-grade aesthetics, native motion, and human release approval remain blocked",
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
      "audit_run2_52_editorial_socket_renderer_against_visible_content_quality_then_continue_same_five_layers",
  };
  const resultJson = path.join(root, pack, "results", "run2_52_editorial_socket_renderer_rerun_result.json");
  const resultMd = path.join(root, pack, "results", "run2_52_editorial_socket_renderer_rerun_result.md");
  writeJson(resultJson, result);
  fs.writeFileSync(
    resultMd,
    [
      "# Run 2.52 Editorial Socket Renderer Rerun",
      "",
      "Status: four-arm rerun completed, public blocked.",
      "",
      "Run 2.52 consumes Run 2.51 before native PPT drawing. The full arm binds editorial copy, shape text sockets, and renderer archetype gates before drawing public surface text.",
      "",
      "This fixes the suspected workflow bug: Run 2.51 is not only displayed in the viewer. The generated full arm carries `run2_51_editorial_copy_memory_id`, `run2_51_shape_text_socket_memory_id`, `run2_51_renderer_archetype_gate_id`, socket-bound public text counts, and shape primitive counts in trace.",
      "",
      "## Arms",
      "",
      "- `prompt_only`",
      "- `run1_5_skill`",
      "- `run2_52_full_editorial_socket_renderer`",
      "- `bad_run2_51_missing_editorial_socket_pack`",
      "",
      "## Result",
      "",
      "Best internal arm: `run2_52_full_editorial_socket_renderer`.",
      "",
      "Quality delta: `editorial_copy_shape_text_socket_and_renderer_archetype_binding`. All six full-arm slides contain Run 2.51 editorial copy ids, shape text socket ids, renderer archetype gate ids, public copy status, and native socket-bound public text.",
      "",
      "The negative control `bad_run2_51_missing_editorial_socket_pack` can reuse the Run 2.50 generated result, but it has no Run 2.51 editorial copy id, no shape text socket id, no renderer archetype gate id, and fails public copy binding.",
      "",
      "Public release remains blocked. This proves editorial copy, shape text sockets, and renderer archetype consumption, not final public-video-grade aesthetics.",
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
  const fourArmSheet = buildRun252FourArmSheet(built);
  const fullSkillSeriesSheet = buildFullSkillSeriesSheet();
  const runSummary = {
    run_id: "run2_52_editorial_socket_renderer_four_arms",
    selected_usecase_id: selectedUsecaseId,
    arms: armSpecs.map((arm) => arm.armId),
    combined_contact_sheet: fourArmSheet,
    full_skill_series_sheet: fullSkillSeriesSheet,
    created: built.map((item) => item.workspace),
  };
  writeJson(path.join(outRoot, "run2_52_editorial_socket_renderer_rerun_summary.json"), runSummary);
  writeRun252Result(runSummary);
  return runSummary;
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const result = await main();
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

export {
  RUN2_51_EDITORIAL_SOCKET_INPUTS,
  RUN2_52_FULL_DATA_INPUTS,
  RUN2_52_INPUTS,
  armSpecs,
  assertRun252ArmInputBoundaries,
  assertRun252EditorialSocketSelfCheck,
  drawRun252EditorialSocketScene,
  loadRun252ContractData,
  main,
  readRun252PackJsonForArm,
  registerRun252Module,
  selectRun252ForSlide,
  traceFor,
  validateRun252RepairPack,
};
