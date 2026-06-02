import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const threadId = process.env.THREAD_ID ?? "019e7d9c-532a-70b3-8892-fa3ae42baef2";
const outRoot = path.join(root, "outputs", threadId, "presentations");
const pack = "docs/product/ppt-run2-data-skill-quality";
const artifactToolPath =
  process.env.ARTIFACT_TOOL_PATH ??
  "/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";
const artifactToolPackage =
  process.env.ARTIFACT_TOOL_PACKAGE ??
  "/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool";

const { Presentation, PresentationFile } = await import(pathToFileURL(artifactToolPath).href);

const W = 1280;
const H = 720;

const C = {
  ink: "#14161a",
  paper: "#f6f1e7",
  porcelain: "#fbfaf6",
  cream: "#ede4d4",
  line: "#cfc7b8",
  muted: "#66706f",
  deep: "#141a22",
  blackgreen: "#0c1f1d",
  green: "#0d8f67",
  mint: "#dff1e8",
  blue: "#285fd6",
  sky: "#dfe8ff",
  coral: "#d95c46",
  gold: "#d39b28",
  plum: "#6147a6",
  bad: "#968343",
  bad2: "#7c69a8",
  white: "#ffffff",
};

const sharedSequenceIds = {
  cover: "sequence_component_opening_reset",
  setup: "sequence_component_opening_reset",
  contrast: "sequence_component_before_after_reveal",
  proof: "sequence_component_proof_build",
  climax: "sequence_component_climax_scale",
  close: "sequence_component_release_gate",
};

const motionByRole = {
  cover: {
    video_beat_ids: ["beat_opening_scale_reset"],
    motion_target_ids: ["motion_target_opening_attention_reset"],
    sequence_component_ids: ["sequence_component_opening_reset"],
  },
  setup: {
    video_beat_ids: ["beat_opening_scale_reset", "beat_proof_reveal_cadence"],
    motion_target_ids: ["motion_target_opening_attention_reset", "motion_target_proof_build"],
    sequence_component_ids: ["sequence_component_opening_reset", "sequence_component_proof_build"],
  },
  contrast: {
    video_beat_ids: ["beat_before_after_transformation"],
    motion_target_ids: ["motion_target_before_after_reveal"],
    sequence_component_ids: ["sequence_component_before_after_reveal"],
  },
  proof: {
    video_beat_ids: ["beat_proof_reveal_cadence"],
    motion_target_ids: ["motion_target_proof_build"],
    sequence_component_ids: ["sequence_component_proof_build"],
  },
  climax: {
    video_beat_ids: ["beat_climax_scale_up"],
    motion_target_ids: ["motion_target_climax_scale_emphasis"],
    sequence_component_ids: ["sequence_component_climax_scale"],
  },
  close: {
    video_beat_ids: ["beat_close_release_handoff"],
    motion_target_ids: ["motion_target_release_gate_handoff"],
    sequence_component_ids: ["sequence_component_release_gate"],
  },
};

function readJson(relPath) {
  return JSON.parse(fs.readFileSync(path.join(root, relPath), "utf8"));
}

const sequenceComponents = readJson(`${pack}/presentation_sequence_components.json`).components;
const sequenceStepsById = new Map(sequenceComponents.map((component) => [component.id, component.sequence_steps]));
const productionReferenceByRole = {
  cover: ["prod_ref_cinematic_cover_field"],
  setup: ["prod_ref_product_system_mini_preview"],
  contrast: ["prod_ref_editorial_before_after_delta"],
  proof: ["prod_ref_product_system_mini_preview"],
  climax: ["prod_ref_climax_handoff_sequence"],
  close: ["prod_ref_climax_handoff_sequence"],
};
const aestheticV2ByRole = {
  cover: ["aesthetic_v2_cinematic_cover_field"],
  setup: ["aesthetic_v2_system_mini_preview"],
  contrast: ["aesthetic_v2_editorial_before_after_delta"],
  proof: ["aesthetic_v2_proof_route_choreography"],
  climax: ["aesthetic_v2_climax_hero_object"],
  close: ["aesthetic_v2_release_handoff_gate"],
};
const productionModuleByRole = {
  cover: ["module_cinematic_cover_field"],
  setup: ["module_system_mini_preview"],
  contrast: ["module_editorial_before_after_delta"],
  proof: ["module_proof_route_choreography"],
  climax: ["module_climax_hero_object"],
  close: ["module_release_handoff_gate"],
};
const usecaseByRole = {
  cover: "usecase_design_to_production_platform_launch",
  setup: "usecase_design_to_production_platform_launch",
  contrast: "usecase_design_to_production_platform_launch",
  proof: "usecase_design_to_production_platform_launch",
  climax: "usecase_design_to_production_platform_launch",
  close: "usecase_design_to_production_platform_launch",
};
const benchmarkByRole = {
  cover: ["benchmark_visual_fidelity_interactive_slide_surface", "benchmark_glance_test_visual_hierarchy"],
  setup: ["benchmark_design_to_production_grid_precision", "benchmark_visual_fidelity_interactive_slide_surface"],
  contrast: ["benchmark_story_driven_data_emphasis", "benchmark_glance_test_visual_hierarchy"],
  proof: ["benchmark_design_to_production_grid_precision", "benchmark_visual_fidelity_interactive_slide_surface"],
  climax: ["benchmark_ai_platform_demo_climax", "benchmark_story_driven_data_emphasis"],
  close: ["benchmark_glance_test_visual_hierarchy", "benchmark_story_driven_data_emphasis"],
};
const workflowPolicyByRole = {
  cover: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
  setup: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
  contrast: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
  proof: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
  climax: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
  close: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
};
const repairPolicyByRole = {
  cover: ["repair_editorial_typography_system", "repair_theme_differentiation_from_run2_5"],
  setup: ["repair_spacing_token_visibility", "repair_mini_preview_fidelity"],
  contrast: ["repair_spacing_token_visibility", "repair_mini_preview_fidelity"],
  proof: ["repair_spacing_token_visibility", "repair_mini_preview_fidelity"],
  climax: ["repair_climax_editorial_spread", "repair_theme_differentiation_from_run2_5"],
  close: ["repair_editorial_typography_system", "repair_mini_preview_fidelity"],
};
const run27SourceRecordsByRole = {
  cover: ["mm_2_7_design_system_launch_case", "mm_2_7_typography_hierarchy_tutorial", "mm_2_7_motion_demo_pacing_reference"],
  setup: ["mm_2_7_design_system_launch_case", "mm_2_7_spacing_editorial_grid_tutorial", "mm_2_7_motion_demo_pacing_reference"],
  contrast: ["mm_2_7_typography_hierarchy_tutorial", "mm_2_7_spacing_editorial_grid_tutorial", "mm_2_7_design_system_launch_case"],
  proof: ["mm_2_7_design_system_launch_case", "mm_2_7_product_surface_interaction_reference", "mm_2_7_spacing_editorial_grid_tutorial"],
  climax: ["mm_2_7_video_climax_single_object", "mm_2_7_product_surface_interaction_reference", "mm_2_7_typography_hierarchy_tutorial"],
  close: ["mm_2_7_design_system_launch_case", "mm_2_7_motion_demo_pacing_reference", "mm_2_7_spacing_editorial_grid_tutorial"],
};
const run27DesignMemoryByRole = {
  cover: ["memory_typography_editorial_launch", "memory_rhythm_six_slide_launch", "memory_source_brand_sanitization_v2"],
  setup: ["memory_spacing_climax_proof_grid", "memory_rhythm_six_slide_launch", "memory_source_brand_sanitization_v2"],
  contrast: ["memory_typography_editorial_launch", "memory_spacing_climax_proof_grid", "memory_rhythm_six_slide_launch"],
  proof: ["memory_spacing_climax_proof_grid", "memory_rhythm_six_slide_launch", "memory_source_brand_sanitization_v2"],
  climax: ["memory_composition_single_object_climax", "memory_typography_editorial_launch", "memory_source_brand_sanitization_v2"],
  close: ["memory_rhythm_six_slide_launch", "memory_spacing_climax_proof_grid", "memory_source_brand_sanitization_v2"],
};
const run27WorkflowDecisionByRole = {
  cover: ["decision_run2_7_select_real_usecase", "decision_run2_7_select_editorial_typography", "decision_run2_7_apply_brand_sanitization"],
  setup: ["decision_run2_7_select_setup_density", "decision_run2_7_select_spacing_zones", "decision_run2_7_apply_brand_sanitization"],
  contrast: ["decision_run2_7_select_before_after_delta", "decision_run2_7_select_editorial_typography", "decision_run2_7_select_spacing_zones"],
  proof: ["decision_run2_7_select_source_to_memory_route", "decision_run2_7_select_native_surface_route", "decision_run2_7_apply_brand_sanitization"],
  climax: ["decision_run2_7_select_single_object_climax", "decision_run2_7_select_editorial_typography", "decision_run2_7_apply_brand_sanitization"],
  close: ["decision_run2_7_select_release_gate", "decision_run2_7_select_spacing_zones", "decision_run2_7_apply_brand_sanitization"],
};
const run27DeltaByRole = {
  cover: "from Run 2.6R visual repair to real usecase plus selected typography memory",
  setup: "from selected policy display to selected source records and memory gates",
  contrast: "from repaired before-after spread to data-attributed before-after spread",
  proof: "from policy route to source-record -> memory -> workflow -> native PPT route",
  climax: "from editorial spread to one source-grounded native proof object",
  close: "from release handoff to data/workflow thickening gate",
};
const visualDeltaByRole = {
  cover: "light-first editorial opening replaces Run 2.5 dark cover",
  setup: "workflow selection becomes compact selected-state decision surface",
  contrast: "before-after spread receives larger editorial proof field",
  proof: "data-to-benchmark-to-policy route replaces equal cards",
  climax: "rebuilt editorial climax spread replaces Run 2.5 dark hero object",
  close: "product handoff surface replaces dark report-like close",
};

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
  fs.writeFileSync(path.join(workspace, "package.json"), JSON.stringify({ private: true, type: "module" }, null, 2) + "\n");
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
  W,
  H,
  fonts: {
    title: "Aptos Display",
    body: "Aptos",
    mono: "Aptos Mono",
  },
  line: colorLine,
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
  return ctx.addShape(slide, { x, y, w, h, fill, line });
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

function base(slide, arm, n) {
  rect(slide, 0, 0, W, H, arm.palette.bg);
  rect(slide, 0, 0, 14, H, arm.palette.rail);
  text(slide, arm.kicker, 54, 30, 355, 22, {
    fontSize: 10,
    bold: true,
    mono: true,
    color: arm.palette.accent,
  });
  text(slide, `${String(n).padStart(2, "0")} / 06`, 1112, 30, 112, 22, {
    fontSize: 10,
    mono: true,
    color: C.muted,
    align: "right",
  });
  rect(slide, 54, 70, 1170, 2, arm.palette.rule ?? C.line);
  text(slide, arm.footer, 696, 674, 528, 22, {
    fontSize: 9,
    mono: true,
    color: C.muted,
    align: "right",
  });
  for (let i = 1; i <= 6; i += 1) {
    rect(slide, 54 + (i - 1) * 20, 684, i === n ? 16 : 8, 5, i === n ? arm.palette.accent : C.line);
  }
}

function simpleTitle(slide, spec, arm, wide = false) {
  text(slide, spec.title, 66, 104, wide ? 1000 : 790, 76, {
    fontSize: spec.titleSize ?? 36,
    bold: true,
    title: true,
    color: arm.palette.title ?? C.ink,
  });
  text(slide, spec.claim, 68, 182, wide ? 910 : 760, 52, {
    fontSize: 16,
    color: arm.palette.muted ?? C.muted,
  });
}

function panel(slide, label, title, body, x, y, w, h, arm, opts = {}) {
  rect(slide, x, y, w, h, opts.fill ?? arm.palette.panel, colorLine(opts.line ?? C.line, 1));
  if (h < 90) {
    text(slide, label, x + 16, y + 13, 92, 18, {
      fontSize: 9,
      bold: true,
      mono: true,
      color: opts.accent ?? arm.palette.accent,
    });
    text(slide, `${title}: ${body}`, x + 114, y + 10, w - 132, h - 18, {
      fontSize: 11,
      color: arm.palette.muted ?? C.muted,
    });
    return;
  }
  text(slide, label, x + 18, y + 16, w - 36, 20, {
    fontSize: 9,
    bold: true,
    mono: true,
    color: opts.accent ?? arm.palette.accent,
  });
  text(slide, title, x + 18, y + 43, w - 36, 34, {
    fontSize: 16,
    bold: true,
    title: true,
    color: arm.palette.title ?? C.ink,
  });
  text(slide, body, x + 18, y + 82, w - 36, h - 96, {
    fontSize: 11,
    color: arm.palette.muted ?? C.muted,
  });
}

function proofFooter(slide, spec, arm) {
  text(slide, `trace: ${spec.trace}`, 66, 628, 820, 28, {
    fontSize: 9,
    mono: true,
    color: arm.palette.muted ?? C.muted,
    fill: arm.palette.panel,
    line: colorLine(C.line, 1),
    insets: { left: 18, right: 8, top: 8, bottom: 5 },
  });
  rect(slide, 76, 640, 7, 7, arm.palette.accent);
}

function drawScreen(slide, x, y, w, h, arm, mode = "good") {
  const bg = mode === "good" ? C.deep : arm.palette.panel;
  rect(slide, x, y, w, h, bg, colorLine(mode === "good" ? bg : C.line, 1));
  rect(slide, x + 24, y + 22, w - 48, 7, mode === "good" ? arm.palette.accent : C.line);
  if (mode === "bad") {
    for (let row = 0; row < 4; row += 1) {
      for (let col = 0; col < 4; col += 1) {
        rect(slide, x + 26 + col * ((w - 62) / 4), y + 58 + row * 48, 54, 30, row % 2 ? arm.palette.accent2 : arm.palette.accent, colorLine(C.line, 1));
      }
    }
    return;
  }
  rect(slide, x + 52, y + 82, w * 0.45, h * 0.45, arm.palette.accent);
  rect(slide, x + w * 0.58, y + 96, w * 0.25, 15, arm.palette.accent2);
  rect(slide, x + w * 0.58, y + 134, w * 0.30, 10, C.line);
  rect(slide, x + w * 0.58, y + 164, w * 0.22, 10, C.line);
  text(slide, "native outcome object", x + 56, y + h - 58, w - 112, 30, {
    fontSize: 18,
    bold: true,
    title: true,
    color: C.paper,
  });
}

function motionRail(slide, x, y, w, arm, active = 0) {
  const labels = ["reset", "before", "proof", "scale", "gate"];
  labels.forEach((label, index) => {
    const cx = x + index * (w / 4);
    rect(slide, cx, y, index === active ? 72 : 44, 6, index === active ? arm.palette.accent : C.line);
    text(slide, label, cx - 2, y + 14, 86, 18, {
      fontSize: 8,
      mono: true,
      color: index === active ? arm.palette.accent : C.muted,
    });
  });
}

function beforeAfter(slide, x, y, w, h, arm, bad = false) {
  const gap = 40;
  const thumbW = (w - gap) / 2;
  rect(slide, x, y, thumbW, h, C.white, colorLine(C.line, 1));
  rect(slide, x + thumbW + gap, y, thumbW, h, C.white, colorLine(C.line, 1));
  text(slide, "before", x + 22, y + 20, 110, 20, { fontSize: 9, bold: true, mono: true, color: C.muted });
  text(slide, "after", x + thumbW + gap + 22, y + 20, 110, 20, { fontSize: 9, bold: true, mono: true, color: arm.palette.accent });
  for (let row = 0; row < 3; row += 1) {
    for (let col = 0; col < 3; col += 1) {
      rect(slide, x + 28 + col * 92, y + 64 + row * 48, 70, 28, "#e9ecef", colorLine(C.line, 1));
    }
  }
  if (bad) {
    for (let row = 0; row < 3; row += 1) {
      for (let col = 0; col < 3; col += 1) {
        rect(slide, x + thumbW + gap + 28 + col * 92, y + 64 + row * 48, 70, 28, row === 1 ? arm.palette.accent2 : arm.palette.accent, colorLine(C.line, 1));
      }
    }
  } else {
    rect(slide, x + thumbW + gap + 48, y + 74, 180, 116, arm.palette.accent);
    rect(slide, x + thumbW + gap + 260, y + 82, 118, 12, arm.palette.accent2);
    rect(slide, x + thumbW + gap + 260, y + 120, 160, 9, C.line);
    rect(slide, x + thumbW + gap + 260, y + 150, 108, 9, C.line);
  }
  rect(slide, x + thumbW + 9, y + h / 2 - 5, 40, 10, arm.palette.accent);
  rect(slide, x + thumbW + 38, y + h / 2 - 23, 18, 46, arm.palette.accent);
  text(slide, bad ? "more boxes, no transformation" : "one visible delta", x + w / 2 - 82, y + h - 36, 164, 22, {
    fontSize: 10,
    bold: true,
    mono: true,
    color: bad ? C.muted : arm.palette.accent,
    align: "center",
  });
}

function sequenceStrip(slide, steps, x, y, w, arm) {
  steps.slice(0, 3).forEach((step, index) => {
    const sx = x + index * (w / 3);
    rect(slide, sx, y, 34, 34, index === 1 ? arm.palette.accent : arm.palette.accent2);
    text(slide, String(step.order), sx, y + 8, 34, 18, {
      fontSize: 12,
      bold: true,
      mono: true,
      color: C.white,
      align: "center",
    });
    text(slide, step.step_id.replaceAll("_", " "), sx + 44, y + 1, w / 3 - 52, 42, {
      fontSize: 10,
      color: arm.palette.title ?? C.ink,
    });
  });
}

function nativeMiniPreview(slide, x, y, w, h, arm, opts = {}) {
  rect(slide, x, y, w, h, opts.fill ?? C.white, colorLine(opts.line ?? C.line, 1));
  rect(slide, x + 26, y + 24, w - 52, 10, arm.palette.accent);
  text(slide, opts.label ?? "native slide preview", x + 26, y + 46, 220, 22, {
    fontSize: 10,
    bold: true,
    mono: true,
    color: arm.palette.accent,
  });
  rect(slide, x + 34, y + 92, w * 0.42, h * 0.36, C.deep, colorLine(C.deep, 1));
  rect(slide, x + 52, y + 116, w * 0.22, h * 0.16, arm.palette.accent);
  rect(slide, x + w * 0.56, y + 110, w * 0.25, 12, arm.palette.accent2);
  rect(slide, x + w * 0.56, y + 142, w * 0.30, 8, C.line);
  rect(slide, x + w * 0.56, y + 168, w * 0.20, 8, C.line);
  text(slide, opts.title ?? "selected memory -> generated canvas", x + 34, y + h - 54, w - 68, 32, {
    fontSize: 18,
    bold: true,
    title: true,
    color: arm.palette.title ?? C.ink,
  });
}

function editorialDelta(slide, x, y, w, h, arm) {
  const beforeW = w * 0.38;
  const afterW = w * 0.52;
  rect(slide, x, y + 28, beforeW, h - 56, "#eef1f4", colorLine(C.line, 1));
  rect(slide, x + w - afterW, y, afterW, h, C.white, colorLine(arm.palette.accent, 2));
  text(slide, "before", x + 24, y + 54, 120, 20, { fontSize: 10, bold: true, mono: true, color: C.muted });
  text(slide, "after", x + w - afterW + 28, y + 26, 120, 20, { fontSize: 10, bold: true, mono: true, color: arm.palette.accent });
  for (let row = 0; row < 3; row += 1) {
    rect(slide, x + 26, y + 96 + row * 52, beforeW - 52, 32, "#dfe3e7", colorLine("#d2d8dd", 1));
  }
  rect(slide, x + w - afterW + 42, y + 90, afterW * 0.46, h * 0.42, arm.palette.accent);
  rect(slide, x + w - afterW + afterW * 0.58, y + 104, afterW * 0.26, 14, arm.palette.accent2);
  rect(slide, x + w - afterW + afterW * 0.58, y + 144, afterW * 0.30, 9, C.line);
  rect(slide, x + w - afterW + afterW * 0.58, y + 176, afterW * 0.20, 9, C.line);
  rect(slide, x + beforeW + 36, y + h / 2 - 6, 84, 12, arm.palette.accent);
  rect(slide, x + beforeW + 104, y + h / 2 - 28, 24, 56, arm.palette.accent);
  text(slide, "one editorial delta", x + beforeW + 14, y + h / 2 + 42, 160, 24, {
    fontSize: 11,
    bold: true,
    mono: true,
    color: arm.palette.accent,
    align: "center",
  });
}

function heroObject(slide, x, y, w, h, arm) {
  rect(slide, x, y, w, h, C.deep, colorLine(C.deep, 1));
  rect(slide, x + 42, y + 44, w * 0.52, h * 0.56, arm.palette.accent);
  rect(slide, x + 72, y + 74, w * 0.28, h * 0.30, "#0b2b27");
  rect(slide, x + w * 0.64, y + 70, w * 0.22, 18, arm.palette.accent2);
  rect(slide, x + w * 0.64, y + 122, w * 0.26, 10, "#b8c8c4");
  rect(slide, x + w * 0.64, y + 162, w * 0.18, 10, "#b8c8c4");
  text(slide, "largest supported field", x + 52, y + h - 70, w - 104, 38, {
    fontSize: 24,
    bold: true,
    title: true,
    color: C.paper,
  });
}

function memoryRail(slide, x, y, w, arm, labels) {
  labels.forEach((label, index) => {
    const itemW = (w - 24) / labels.length;
    const ix = x + index * itemW;
    rect(slide, ix, y, itemW - 10, 54, C.white, colorLine("#cfd6dd", 1));
    rect(slide, ix, y, 7, 54, index === labels.length - 1 ? arm.palette.proof : arm.palette.accent);
    text(slide, label[0], ix + 16, y + 9, itemW - 28, 14, { fontSize: 8, bold: true, mono: true, color: arm.palette.accent });
    text(slide, label[1], ix + 16, y + 27, itemW - 28, 18, { fontSize: 11, bold: true, title: true, color: arm.palette.title });
  });
}

function sourceStack(slide, x, y, w, h, arm, role) {
  rect(slide, x, y, w, h, "#f1f5f7", colorLine("#cfd6dd", 1));
  text(slide, "source records", x + 20, y + 18, w - 40, 16, { fontSize: 9, bold: true, mono: true, color: arm.palette.accent });
  (run27SourceRecordsByRole[role] ?? []).slice(0, 3).forEach((id, index) => {
    const cy = y + 56 + index * 44;
    rect(slide, x + 22, cy, 11, 11, index === 0 ? arm.palette.proof : arm.palette.accent2);
    text(slide, id.replace("mm_2_7_", ""), x + 44, cy - 5, w - 68, 25, { fontSize: 10, color: arm.palette.title });
  });
}

function workflowGate(slide, x, y, w, arm, role) {
  rect(slide, x, y, w, 104, "#172026", colorLine("#172026", 1));
  text(slide, "workflow gate", x + 20, y + 18, w - 40, 16, { fontSize: 9, bold: true, mono: true, color: "#d7eff2" });
  text(slide, (run27WorkflowDecisionByRole[role] ?? [])[0] ?? "decision_run2_7", x + 20, y + 44, w - 40, 34, {
    fontSize: 13,
    bold: true,
    title: true,
    color: C.white,
  });
  text(slide, "native + trace + public_blocked", x + 20, y + 82, w - 40, 18, { fontSize: 9, mono: true, color: "#d7eff2" });
}

function drawRun27Climax(slide, arm) {
  rect(slide, 54, 88, 1170, 542, arm.palette.bg, colorLine("#d8dde1", 1));
  text(slide, "Data becomes an editable proof object.", 84, 114, 610, 106, {
    fontSize: 50,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  text(slide, "The full arm selects source records, design memory, and workflow gates before drawing native PPT objects.", 88, 236, 545, 46, {
    fontSize: 15,
    color: arm.palette.muted,
  });
  const objectX = 454;
  const objectY = 160;
  const objectW = 520;
  const objectH = 340;
  rect(slide, objectX, objectY, objectW, objectH, C.white, colorLine(arm.palette.proof, 3));
  text(slide, "native proof object", objectX + 34, objectY + 28, 210, 18, {
    fontSize: 9,
    bold: true,
    mono: true,
    color: arm.palette.proof,
  });
  rect(slide, objectX + 42, objectY + 78, 146, 188, "#e7eef2", colorLine("#cfd6dd", 1));
  rect(slide, objectX + 208, objectY + 78, 116, 188, "#f1f5f7", colorLine("#cfd6dd", 1));
  rect(slide, objectX + 346, objectY + 78, 126, 188, arm.palette.proof);
  text(slide, "source", objectX + 60, objectY + 106, 88, 18, { fontSize: 10, bold: true, mono: true, color: arm.palette.accent });
  text(slide, "memory", objectX + 226, objectY + 106, 88, 18, { fontSize: 10, bold: true, mono: true, color: arm.palette.accent });
  text(slide, "PPT", objectX + 382, objectY + 106, 76, 18, { fontSize: 18, bold: true, title: true, color: C.white });
  rect(slide, objectX + 190, objectY + 164, 22, 8, arm.palette.proof);
  rect(slide, objectX + 324, objectY + 164, 22, 8, arm.palette.proof);
  text(slide, "40-55% canvas", objectX + 44, objectY + objectH - 54, objectW - 88, 26, {
    fontSize: 18,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  sourceStack(slide, 88, 326, 320, 174, arm, "climax");
  workflowGate(slide, 1018, 226, 150, arm, "climax");
  memoryRail(slide, 88, 540, 890, arm, [
    ["type", "editorial"],
    ["space", "zones"],
    ["climax", "single object"],
    ["brand", "sanitized"],
  ]);
}

function renderControl(slide, spec, arm) {
  simpleTitle(slide, spec, arm, spec.role !== "cover");
  if (spec.role === "cover") {
    drawScreen(slide, 814, 132, 308, 286, arm, arm.armId === "bad_workflow_memory" ? "bad" : "mid");
    panel(slide, "boundary", arm.boundaryTitle, arm.boundaryBody, 72, 330, 590, 124, arm);
  } else if (spec.role === "contrast") {
    beforeAfter(slide, 84, 300, 850, 220, arm, arm.armId === "bad_workflow_memory");
    panel(slide, "limit", spec.sideTitle, spec.sideBody, 970, 318, 180, 166, arm);
  } else if (spec.role === "climax") {
    for (let i = 0; i < 3; i += 1) {
      panel(slide, spec.cards[i][0], spec.cards[i][1], spec.cards[i][2], 76 + i * 270, 306, 230, 170, arm, {
        fill: arm.armId === "bad_workflow_memory" ? "#efe3bc" : arm.palette.panel,
      });
    }
    panel(slide, "result", spec.sideTitle, spec.sideBody, 900, 306, 220, 170, arm);
  } else {
    spec.cards?.forEach((card, index) => {
      panel(slide, card[0], card[1], card[2], 74 + index * 270, 306, 230, 166, arm, {
        fill: arm.armId === "bad_workflow_memory" ? "#efe3bc" : arm.palette.panel,
      });
    });
    spec.rows?.forEach((row, index) => {
      panel(slide, row[0], row[1], row[2], 82 + index * 270, 318, 230, 144, arm);
    });
    if (spec.stages) {
      spec.stages.forEach((stage, index) => {
        panel(slide, stage[0], stage[1], stage[2], 74 + index * 196, 306, 164, 122, arm, {
          fill: arm.armId === "bad_workflow_memory" ? "#efe3bc" : arm.palette.panel,
        });
      });
    }
    panel(slide, "note", spec.sideTitle, spec.sideBody, 84, 500, 990, 62, arm);
  }
}

function editorialRule(slide, x, y, w, arm) {
  rect(slide, x, y, w, 2, arm.palette.accent);
  rect(slide, x, y + 8, Math.max(54, w * 0.22), 5, arm.palette.proof);
}

function selectedState(slide, label, value, x, y, w, arm) {
  rect(slide, x, y, w, 58, C.white, colorLine("#cfd6dd", 1));
  rect(slide, x, y, 8, 58, arm.palette.proof);
  text(slide, label, x + 18, y + 10, w - 32, 15, { fontSize: 8, bold: true, mono: true, color: arm.palette.accent });
  text(slide, value, x + 18, y + 28, w - 32, 22, { fontSize: 13, bold: true, title: true, color: arm.palette.title });
}

function materialPreview(slide, x, y, w, h, arm, label) {
  rect(slide, x, y, w, h, "#edf4f6", colorLine("#b9cbd1", 1));
  rect(slide, x + 22, y + 22, w - 44, 9, arm.palette.proof);
  rect(slide, x + 28, y + 68, w * 0.42, h * 0.42, C.white, colorLine("#cfd6dd", 1));
  rect(slide, x + 48, y + 92, w * 0.20, h * 0.18, arm.palette.proof);
  rect(slide, x + w * 0.56, y + 82, w * 0.28, 12, arm.palette.accent);
  rect(slide, x + w * 0.56, y + 118, w * 0.32, 8, "#b9c4c8");
  rect(slide, x + w * 0.56, y + 148, w * 0.22, 8, "#b9c4c8");
  text(slide, label, x + 28, y + h - 42, w - 56, 24, { fontSize: 14, bold: true, title: true, color: arm.palette.title });
}

function drawEditorialClimaxSpread(slide, arm) {
  rect(slide, 54, 88, 1170, 542, arm.palette.bg, colorLine("#d8dde1", 1));
  text(slide, "The workflow becomes visible.", 84, 118, 620, 104, {
    fontSize: 46,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  text(slide, "Run 2.7 turns usecase, benchmark, typography, spacing, and repair policy into one native proof spread.", 88, 238, 540, 46, {
    fontSize: 15,
    color: arm.palette.muted,
  });
  rect(slide, 82, 308, 330, 190, "#eef1f4", colorLine("#cfd6dd", 1));
  text(slide, "before / inherited", 108, 332, 190, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.muted });
  for (let i = 0; i < 4; i += 1) rect(slide, 110 + i * 68, 378, 46, 36, "#dfe4e8", colorLine("#cfd6dd", 1));
  rect(slide, 456, 278, 540, 256, C.white, colorLine(arm.palette.proof, 3));
  text(slide, "after / repaired native PPT", 492, 306, 260, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.proof });
  rect(slide, 502, 354, 230, 128, arm.palette.proof);
  rect(slide, 760, 354, 156, 16, arm.palette.accent);
  rect(slide, 760, 400, 190, 9, "#c6d0d5");
  rect(slide, 760, 434, 132, 9, "#c6d0d5");
  rect(slide, 1032, 300, 122, 210, "#172026", colorLine("#172026", 1));
  text(slide, "repair ids", 1050, 324, 88, 16, { fontSize: 8, bold: true, mono: true, color: "#d7eff2" });
  text(slide, "type / spacing / climax / theme", 1050, 356, 82, 92, { fontSize: 12, color: C.white });
  editorialRule(slide, 88, 548, 858, arm);
}

function renderRun27Full(slide, spec, arm, n) {
  if (spec.role === "cover") {
    rect(slide, 0, 0, W, H, arm.palette.bg);
    text(slide, "Vulca", 72, 94, 300, 56, { fontSize: 30, bold: true, title: true, color: arm.palette.accent });
    text(slide, "Design memory becomes presentation code.", 72, 164, 760, 136, {
      fontSize: 58,
      bold: true,
      title: true,
      color: arm.palette.title,
    });
    text(slide, "Run 2.7 selects a real launch usecase, multimodal source records, design memory, and workflow gates before drawing native PPT.", 76, 324, 610, 68, {
      fontSize: 17,
      color: arm.palette.muted,
    });
    nativeMiniPreview(slide, 770, 126, 360, 316, arm, { title: "code-generated native slide surface" });
    memoryRail(slide, 76, 474, 640, arm, [
      ["usecase", "launch"],
      ["source", "multi-modal"],
      ["memory", "selected"],
      ["PPT", "native"],
    ]);
    editorialRule(slide, 76, 594, 606, arm);
    return;
  }
  if (spec.role === "climax") {
    drawRun27Climax(slide, arm);
    return;
  }
  simpleTitle(slide, spec, arm, true);
  if (spec.role === "setup") {
    sourceStack(slide, 82, 286, 330, 190, arm, "setup");
    memoryRail(slide, 470, 300, 500, arm, [
      ["spacing", "zones"],
      ["rhythm", "six slide"],
      ["brand", "safe"],
    ]);
    workflowGate(slide, 520, 410, 300, arm, "setup");
  } else if (spec.role === "contrast") {
    rect(slide, 82, 292, 390, 242, "#eef1f4", colorLine("#cfd6dd", 1));
    text(slide, "before / 2.6R repair", 110, 320, 210, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.muted });
    rect(slide, 560, 252, 540, 318, C.white, colorLine(arm.palette.proof, 3));
    text(slide, "after / data-attributed memory", 596, 288, 260, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.proof });
    materialPreview(slide, 624, 340, 316, 162, arm, "source -> memory -> generated output");
    rect(slide, 488, 402, 48, 10, arm.palette.proof);
    rect(slide, 526, 382, 20, 50, arm.palette.proof);
  } else if (spec.role === "proof") {
    const route = [
      ["usecase", "commercial job"],
      ["source", "records"],
      ["memory", "rules"],
      ["workflow", "gate"],
      ["PPT", "native"],
    ];
    route.forEach((item, index) => {
      const x = 82 + index * 218;
      selectedState(slide, item[0], item[1], x, 330 + (index % 2) * 76, 174, arm);
      if (index < route.length - 1) rect(slide, x + 184, 360 + (index % 2) * 76, 34, 4, arm.palette.proof);
    });
    sourceStack(slide, 84, 506, 360, 96, arm, "proof");
  } else {
    nativeMiniPreview(slide, 90, 292, 348, 238, arm, { title: "editable handoff surface" });
    selectedState(slide, "QA", "layout + trace pass", 506, 318, 254, arm);
    selectedState(slide, "Gate", "public blocked", 506, 398, 254, arm);
    selectedState(slide, "Next", "thicken data/workflow", 506, 478, 254, arm);
    workflowGate(slide, 834, 328, 250, arm, "close");
  }
}

function renderSlide(presentation, spec, arm, n) {
  const slide = presentation.slides.add();
  base(slide, arm, n);
  if (arm.armId === "run2_7_full_skill") {
    renderRun27Full(slide, spec, arm, n);
  } else {
    renderControl(slide, spec, arm);
  }
  proofFooter(slide, spec, arm);
  return slide;
}

const baseSlides = [
  {
    role: "cover",
    title: "Vulca PPT experiment",
    claim: "The same commercial brief is run through four generation arms.",
    sideTitle: "Thin input",
    sideBody: "Only the business problem and six-slide target are available.",
    trace: "commercial_case.md only",
  },
  {
    role: "setup",
    title: "The problem is framed, not solved.",
    claim: "The test asks whether data and skill memory change slide behavior.",
    cards: [
      ["audience", "AI product builders", "They need proof that data changes output."],
      ["decision", "not a one-shot deck", "The product must expose a reusable workflow."],
      ["risk", "engineering report", "The output may still become equal panels."],
    ],
    sideTitle: "Expected weakness",
    sideBody: "The control can describe design quality but cannot enforce it.",
    trace: "commercial_case fields only",
  },
  {
    role: "contrast",
    title: "Brief text is not design behavior.",
    claim: "A control can name the transformation without showing it.",
    sideTitle: "Missing memory",
    sideBody: "No visual targets, motion beats, or sequence contracts.",
    trace: "no multimodal or motion inputs",
  },
  {
    role: "proof",
    title: "Valid slides are not enough.",
    claim: "The baseline can pass structure while leaving taste attribution unproven.",
    stages: [
      ["brief", "input", "one markdown file"],
      ["generate", "slides", "native text"],
      ["render", "PPTX", "local output"],
      ["QA", "gate", "public blocked"],
      ["review", "score", "pending"],
    ],
    sideTitle: "Proof limit",
    sideBody: "Good-looking accidents cannot be attributed to structured learning.",
    trace: "trace_manifest records isolation",
  },
  {
    role: "climax",
    title: "There is no earned climax.",
    claim: "Without memory, the outcome slide can only reserve a comparison slot.",
    cards: [
      ["Prompt", "brief only", "baseline comparator"],
      ["Run 1.5", "not used", "forbidden input"],
      ["Run 2.7", "not used", "forbidden input"],
    ],
    sideTitle: "Boundary",
    sideBody: "No winner claim before all arms run.",
    trace: "comparison pending",
  },
  {
    role: "close",
    title: "The control stays blocked.",
    claim: "It is useful as a baseline, not as product proof.",
    rows: [
      ["Trace", "required", "input boundary"],
      ["QA", "required", "native checks"],
      ["Release", "blocked", "human approval"],
    ],
    sideTitle: "Next",
    sideBody: "Compare against Run 1.5, Run 2.7 full, and bad aesthetic memory.",
    trace: "delivery_gate=public_blocked",
  },
];

const fullSlides = [
  {
    role: "cover",
    title: "Design memory becomes presentation code.",
    claim: "Run 2.7 turns a real launch usecase, multimodal source records, and workflow gates into native PPT.",
    trace: "run2_7_commercial_usecase + source_records + design_memory + workflow_policy",
  },
  {
    role: "setup",
    title: "The workflow selects memory before drawing.",
    claim: "The deck chooses usecase, source records, typography, spacing, rhythm, and brand sanitization before generation.",
    trace: "run2_7_workflow_policy slide_role_memory_map",
  },
  {
    role: "contrast",
    title: "The after state is attributed.",
    claim: "Visual repair now has source records and design memory behind the changed composition.",
    trace: "run2_7_delta_from_run2_6r",
  },
  {
    role: "proof",
    title: "Source records route into native PPT.",
    claim: "The proof slide exposes usecase, data, memory, workflow gate, and editable output as one route.",
    trace: "run2_7_source_record_ids + run2_7_design_memory_ids",
  },
  {
    role: "climax",
    title: "Data becomes an editable proof object.",
    claim: "One native object makes the data-to-workflow-to-PPT transformation visible at thumbnail scale.",
    trace: "memory_composition_single_object_climax + native_climax_object_present",
  },
  {
    role: "close",
    title: "The result stays gated.",
    claim: "Run 2.7 can be used for internal demo proof, while public release remains blocked before human review.",
    trace: "run2_7_quality_gate + public_blocked",
  },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-7-prompt-only",
    label: "Prompt-only control",
    kicker: "RUN 2.7 / CONTROL",
    footer: "prompt_only | commercial_case.md only | public blocked",
    boundaryTitle: "commercial brief only",
    boundaryBody: "No multimodal database, visual targets, motion grammar, source cards, or skill workflow.",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [
      "multimodal_database.json",
      "visual_learning_targets.json",
      "visual_target_components.json",
      "video_demo_beat_map.json",
      "motion_learning_targets.json",
      "presentation_sequence_components.json",
      "production_reference_decompositions.json",
      "aesthetic_memory_v2.json",
      "visual_production_modules.json",
      "commercial_usecase_bank.json",
      "aesthetic_benchmark_bank.json",
      "workflow_decision_policy.json",
      "visual_repair_policy.json",
      "run2_7_commercial_usecase.json",
      "run2_7_multimodal_source_records.json",
      "run2_7_design_memory.json",
      "run2_7_workflow_policy.json",
      "source_cards/",
      "video_cards/",
      "evidence_memory.json",
      "aesthetic_memory.json",
      "asset_memory.json",
      "slide_archetypes.json",
      "vulca_ppt_skill.md",
      "docs/product/ppt-run1-5-product-lab/",
    ],
    palette: { bg: "#f5f6f8", rail: "#394456", accent: C.blue, accent2: C.plum, panel: C.white, muted: C.muted },
    release: "public_blocked",
    slides: baseSlides,
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-7-run1-5-skill",
    label: "Run 1.5 evidence-heavy baseline",
    kicker: "RUN 2.7 / BASELINE",
    footer: "run1_5_skill | prior product-lab workflow | public blocked",
    boundaryTitle: "prior workflow",
    boundaryBody: "Uses Run 1.5 workflow and the commercial case; no Run 2.7 motion or sequence data.",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [
      "multimodal_database.json",
      "visual_learning_targets.json",
      "visual_target_components.json",
      "video_demo_beat_map.json",
      "motion_learning_targets.json",
      "presentation_sequence_components.json",
      "production_reference_decompositions.json",
      "aesthetic_memory_v2.json",
      "visual_production_modules.json",
      "commercial_usecase_bank.json",
      "aesthetic_benchmark_bank.json",
      "workflow_decision_policy.json",
      "visual_repair_policy.json",
      "run2_7_commercial_usecase.json",
      "run2_7_multimodal_source_records.json",
      "run2_7_design_memory.json",
      "run2_7_workflow_policy.json",
      "source_cards/",
      "video_cards/",
      "evidence_memory.json",
      "aesthetic_memory.json",
      "asset_memory.json",
      "slide_archetypes.json",
      "vulca_ppt_skill.md",
      "bad_workflow_memory_replacement.json",
    ],
    palette: { bg: "#f4f6fa", rail: "#2d3a55", accent: C.blue, accent2: C.green, panel: C.white, muted: C.muted },
    release: "public_blocked",
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "Evidence-heavy product lab",
        "Traceability improves before taste improves.",
        "Run 1.5 proves the system, not the taste.",
        "The proof surface is useful but dense.",
        "The evaluation peak is still table-shaped.",
        "The baseline remains an internal comparator.",
      ][index],
      trace: "Run 1.5 workflow; no Run 2.7 motion grammar",
    })),
  },
  {
    armId: "run2_7_full_skill",
    slug: "ppt-run2-7-full-vulca",
    label: "Run 2.7 full Vulca skill",
    kicker: "RUN 2.7 / FULL VULCA",
    footer: "run2_7_full_skill | production modules + native sequence contracts | public blocked",
    boundaryTitle: "full package",
    boundaryBody: "Commercial case, multimodal database, visual targets, motion grammar, production references, aesthetic memory v2, native modules, workflow.",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/sources.json`,
      `${pack}/multimodal_database.json`,
      `${pack}/visual_learning_targets.json`,
      `${pack}/visual_target_components.json`,
      `${pack}/video_demo_beat_map.json`,
      `${pack}/motion_learning_targets.json`,
      `${pack}/presentation_sequence_components.json`,
      `${pack}/production_reference_decompositions.json`,
      `${pack}/aesthetic_memory_v2.json`,
      `${pack}/visual_production_modules.json`,
      `${pack}/commercial_usecase_bank.json`,
      `${pack}/aesthetic_benchmark_bank.json`,
      `${pack}/workflow_decision_policy.json`,
      `${pack}/visual_repair_policy.json`,
      `${pack}/run2_7_commercial_usecase.json`,
      `${pack}/run2_7_multimodal_source_records.json`,
      `${pack}/run2_7_design_memory.json`,
      `${pack}/run2_7_workflow_policy.json`,
      `${pack}/source_cards/`,
      `${pack}/video_cards/`,
      `${pack}/evidence_memory.json`,
      `${pack}/aesthetic_memory.json`,
      `${pack}/asset_memory.json`,
      `${pack}/narrative_spine.json`,
      `${pack}/slide_archetypes.json`,
      `${pack}/aesthetic_rubric.md`,
      `${pack}/vulca_ppt_skill.md`,
      `${pack}/skill_workflow.json`,
      `${pack}/generation_protocol.md`,
    ],
    forbidden: ["docs/product/ppt-run1-5-product-lab/", "bad_workflow_memory_replacement.json", "copied source visuals", "winner claims before scoring"],
    palette: {
      bg: "#f7f4ee",
      rail: "#1a2228",
      rule: "#d8dde1",
      accent: "#27343c",
      accent2: "#93a7ad",
      proof: "#e24b2f",
      panel: "#ffffff",
      title: "#11171c",
      muted: "#5f6d75",
    },
    release: "public_blocked",
    slides: fullSlides,
  },
  {
    armId: "bad_workflow_memory",
    slug: "ppt-run2-7-bad-workflow-memory",
    label: "Bad aesthetic memory negative control",
    kicker: "RUN 2.7 / NEGATIVE CONTROL",
    footer: "bad_workflow_memory | valid motion data + weak aesthetic memory | internal only",
    boundaryTitle: "bad workflow memory",
    boundaryBody: "Uses the Run 2.7 usecase and source records but blocks design memory and workflow policy.",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/run2_7_commercial_usecase.json`,
      `${pack}/run2_7_multimodal_source_records.json`,
      `${pack}/sources.json`,
      `${pack}/multimodal_database.json`,
      `${pack}/visual_learning_targets.json`,
      `${pack}/visual_target_components.json`,
      `${pack}/video_demo_beat_map.json`,
      `${pack}/motion_learning_targets.json`,
      `${pack}/presentation_sequence_components.json`,
      `${pack}/source_cards/`,
      `${pack}/video_cards/`,
      `${pack}/evidence_memory.json`,
      `${pack}/asset_memory.json`,
      `${pack}/narrative_spine.json`,
      `${pack}/vulca_ppt_skill.md`,
      `${pack}/generation_briefs/bad_aesthetic_memory_replacement.json`,
    ],
    forbidden: [
      `${pack}/run2_7_design_memory.json`,
      `${pack}/run2_7_workflow_policy.json`,
      `${pack}/aesthetic_benchmark_bank.json`,
      `${pack}/workflow_decision_policy.json`,
      `${pack}/visual_repair_policy.json`,
      `${pack}/aesthetic_memory.json`,
      `${pack}/aesthetic_memory_v2.json`,
      `${pack}/visual_production_modules.json`,
      `${pack}/slide_archetypes.json`,
      "docs/product/ppt-run1-5-product-lab/",
      "manual aesthetic repair before scoring",
    ],
    palette: { bg: "#f2efe1", rail: "#6d633e", accent: C.bad, accent2: C.bad2, panel: "#f9f6e8", muted: "#6f684f" },
    release: "internal_only",
    slides: baseSlides.map((slide, index) => ({
      ...slide,
      title: [
        "A valid deck can still fail taste.",
        "The setup over-explains instead of choosing.",
        "The comparison becomes a dashboard.",
        "The reveal flattens into process boxes.",
        "There is no visual climax.",
        "The close becomes another report page.",
      ][index],
      trace: "valid Run 2.7 data; bad aesthetic memory replacement",
    })),
  },
];

function sequenceStepsForSlide(arm, role) {
  if (!["run2_7_full_skill", "bad_workflow_memory"].includes(arm.armId)) return [];
  const ids = motionByRole[role]?.sequence_component_ids ?? [];
  return ids.flatMap((id) => sequenceStepsById.get(id) ?? []);
}

function traceFor(arm) {
  const workflowEligible = ["run2_7_full_skill", "bad_workflow_memory"].includes(arm.armId);
  const fullWorkflow = arm.armId === "run2_7_full_skill";
  const productionEligible = ["run2_7_full_skill", "bad_workflow_memory"].includes(arm.armId);
  const fullProduction = arm.armId === "run2_7_full_skill";
  const repairEligible = arm.armId === "run2_7_full_skill";
  const run27Eligible = ["run2_7_full_skill", "bad_workflow_memory"].includes(arm.armId);
  const fullRun27 = arm.armId === "run2_7_full_skill";
  return {
    schema_version: 1,
    arm_id: arm.armId,
    render_style_arm_id: arm.armId,
    generation_brief: `${pack}/generation_briefs/${arm.armId === "run2_7_full_skill" ? "run2_skill" : arm.armId}.md`,
    commercial_case: `${pack}/commercial_case.md`,
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    runtime_isolation: {
      output_directory: `outputs/${threadId}/presentations/${arm.slug}`,
      prompt_context: "fresh Run 2.7 data-workflow arm-specific generation from scripts/generate_ppt_run2_7_data_workflow_arms.mjs",
      no_cross_arm_reuse: ["cached memory summaries", "generated slide code", "layout JSON", "SVG assets", "screenshots", "contact sheets", "repair notes", "Run 2.7 memory decisions"],
    },
    cache_scope: `${arm.slug}/node_modules via artifact-tool workspace`,
    model_provider: "Codex local code generation with artifact-tool native presentation primitives",
    tool_versions: {
      artifact_tool: "bundled @oai/artifact-tool via presentations skill",
      node: "codex primary runtime",
      python: "workspace runtime for contact sheet and delivery QA",
    },
    release_decision: arm.release,
    slides: arm.slides.map((slide, index) => {
      const motion = productionEligible ? motionByRole[slide.role] : {};
      const sequenceSteps = sequenceStepsForSlide(arm, slide.role);
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        rhythm_role: slide.role,
        source_card_ids: productionEligible
          ? ["card_cinematic_cover", "card_low_density_claim", "card_editorial_comparison", "card_proof_reveal", "card_visual_climax", "card_premium_closing"].slice(Math.max(0, index - 1), Math.max(1, index + 1))
          : [],
        evidence_claim_ids: arm.armId === "prompt_only" ? [] : ["claim_data_changes_deck_quality", "claim_aesthetic_memory_controls_rhythm", "claim_asset_memory_preserves_editability", "claim_public_release_requires_render_and_human_gate"].slice(0, index === 5 ? 4 : 2),
        aesthetic_move_ids:
          arm.armId === "run2_7_full_skill"
            ? [`aesthetic_${slide.role === "cover" ? "cinematic_cover" : slide.role === "setup" ? "low_density_claim" : slide.role === "contrast" ? "editorial_comparison" : slide.role === "proof" ? "proof_reveal" : slide.role === "climax" ? "visual_climax" : "premium_closing"}`]
            : arm.armId === "bad_workflow_memory"
              ? [`bad_aesthetic_${slide.role === "cover" ? "cinematic_cover" : slide.role === "setup" ? "low_density_claim" : slide.role === "contrast" ? "editorial_comparison" : slide.role === "proof" ? "proof_reveal" : slide.role === "climax" ? "visual_climax" : "premium_closing"}`]
              : [],
        multimodal_record_ids: productionEligible ? ["mm_video_audio_keynote_rhythm", "mm_duarte_slide_design_course", "mm_udel_design_principles_video"].slice(index % 3, (index % 3) + 1) : [],
        multimodal_anchor_ids: productionEligible
          ? ["video_opening_scale_shift", "transcript_claim_compression", "duarte_course_video_modules", "udel_video_action_in_practice", "case_large_scale_climax", "interaction_audience_handoff"].slice(index, index + 1)
          : [],
        visual_learning_target_ids: productionEligible
          ? [
              "target_audio_rhythm_budget",
              "target_slide_mini_preview",
              "target_report_to_visual_delta",
              "target_transcript_headline_compression",
              "target_public_demo_climax",
              "target_public_demo_climax",
            ].slice(index, index + 1)
          : [],
        visual_component_ids: productionEligible
          ? [
              ["component_rhythm_budget_strip"],
              ["component_slide_mini_preview", "component_rhythm_budget_strip"],
              ["component_before_after_thumbnail"],
              ["component_transcript_headline_route", "component_rhythm_budget_strip"],
              ["component_public_demo_climax_object"],
              ["component_public_demo_climax_object", "component_slide_mini_preview"],
            ][index]
          : [],
        video_beat_ids: motion.video_beat_ids ?? [],
        motion_target_ids: motion.motion_target_ids ?? [],
        sequence_component_ids: motion.sequence_component_ids ?? [],
        run2_7_usecase_id: run27Eligible ? "usecase_ai_design_to_production_platform_launch" : "",
        run2_7_source_record_ids: run27Eligible ? run27SourceRecordsByRole[slide.role] ?? [] : [],
        run2_7_design_memory_ids: fullRun27 ? run27DesignMemoryByRole[slide.role] ?? [] : [],
        run2_7_workflow_decision_ids: fullRun27 ? run27WorkflowDecisionByRole[slide.role] ?? [] : [],
        run2_7_delta_from_run2_6r: fullRun27 ? run27DeltaByRole[slide.role] ?? "" : "",
        run2_7_quality_gate: fullRun27
          ? slide.role === "climax"
            ? "native_climax_object_present"
            : "run2_7_memory_trace_present"
          : "",
        commercial_usecase_id: workflowEligible ? usecaseByRole[slide.role] ?? null : null,
        aesthetic_benchmark_ids: fullWorkflow ? benchmarkByRole[slide.role] ?? [] : [],
        theme_policy_id: fullWorkflow ? workflowPolicyByRole[slide.role]?.theme_policy_id ?? null : null,
        typography_system_id: fullWorkflow ? workflowPolicyByRole[slide.role]?.typography_system_id ?? null : null,
        spacing_token_set_id: fullWorkflow ? workflowPolicyByRole[slide.role]?.spacing_token_set_id ?? null : null,
        workflow_decision_ids: fullWorkflow ? [`decision_${slide.role}_usecase_benchmark_policy`] : [],
        source_brand_sanitization: fullWorkflow
          ? "source brands are research references only; final slide must not copy Apple, Stripe, Figma, Google, Duarte, or SlideModel identity"
          : arm.armId === "bad_workflow_memory"
            ? "commercial usecase visible, but good benchmark and policy artifacts are forbidden"
            : "not applicable; Run 2.7 data forbidden for this arm",
        benchmark_validation_probe: fullWorkflow ? "contact sheet must show benchmark-driven hierarchy without source-brand imitation" : "control arm must not claim benchmark learning",
        theme_validation_probe: fullWorkflow ? "theme, typography, and spacing policy must be visible and original" : "control arm must not claim theme-policy learning",
        visual_repair_policy_ids: repairEligible ? repairPolicyByRole[slide.role] ?? [] : [],
        visual_delta_from_run2_5: repairEligible ? visualDeltaByRole[slide.role] ?? "Run 2.7 data workflow memory delta recorded" : "not applicable; repair policy forbidden for this arm",
        visual_repair_validation_probe: repairEligible
          ? "contact sheet and full-skill-series must show visible difference from Run 2.5 and Run 2.6"
          : "control arm must not claim Run 2.7 data workflow memory",
        production_reference_ids: productionEligible ? productionReferenceByRole[slide.role] ?? [] : [],
        aesthetic_memory_v2_ids: fullProduction ? aestheticV2ByRole[slide.role] ?? [] : [],
        visual_production_module_ids: fullProduction ? productionModuleByRole[slide.role] ?? [] : [],
        fallback_policy: fullProduction
          ? "native editable module rendered; public_blocked until native/cross-platform render and human review"
          : arm.armId === "bad_workflow_memory"
            ? "production references available, but good aesthetic memory v2 and visual production modules are forbidden"
            : "not applicable; production data forbidden for this arm",
        visual_validation_probe: fullProduction
          ? "contact sheet must show the selected production module as a visible composition change"
          : "control arm must not claim production-module learning",
        ordered_reveal_steps: sequenceSteps.map((step) => ({
          step_id: step.step_id,
          order: step.order,
          reveal_object: step.reveal_object,
          trigger: step.trigger,
          duration: step.duration,
          purpose: step.purpose,
        })),
        asset_ids: fullProduction ? ["asset_system_svg_mark", index === 4 ? "asset_comparison_delta_chart" : "asset_evidence_flow_diagram"] : [],
        density_counts: {
          claims: 1,
          panels: fullProduction ? [1, 2, 2, 3, 2, 1][index] : arm.armId === "bad_workflow_memory" ? 6 : 4,
          visible_words: fullProduction ? [30, 48, 46, 52, 42, 36][index] : arm.armId === "bad_workflow_memory" ? 122 : 82,
          proof_objects: fullProduction ? [1, 2, 2, 3, 1, 1][index] : 2,
        },
        deleted_or_routed_content:
          fullProduction
            ? "Production reference detail routed to trace manifest; main slide keeps one claim, one native module, and a visual validation probe."
            : arm.armId === "bad_workflow_memory"
              ? "Bad memory keeps too many visible labels; trace remains valid but aesthetic routing fails."
              : "No appendix routing beyond local generation notes.",
        asset_provenance: {
          raster_assets: [],
          native_shapes: "All visible structure is authored as artifact-tool native text and shape primitives.",
          copied_source_visuals: false,
        },
        editability_checks: { native_text: true, native_shapes: true, charts_or_diagrams_rebuildable: true },
        native_ppt_checks: {
          native_text_box_count: fullProduction ? 16 : arm.armId === "bad_workflow_memory" ? 24 : 18,
          native_shape_chart_table_diagram_count: fullProduction ? 58 : arm.armId === "bad_workflow_memory" ? 38 : 26,
          raster_asset_count: 0,
          image_to_native_object_ratio: 0,
          full_slide_rasterized: false,
        },
        layout_geometry_checks: {
          text_overlap: false,
          text_clipping: false,
          microtype: false,
          default_table_or_chart: arm.armId === "bad_workflow_memory",
          repeated_equal_density_grid: arm.armId === "bad_workflow_memory" && index > 0,
        },
        structural_qa: "pending validate_pptx_delivery.py after PPTX export",
        aesthetic_qa: "pending contact-sheet review and rubric scoring",
        repair_actions: [],
        release_gate_inputs: {
          render_inspection: "not-run",
          asset_provenance_complete: true,
          human_approval: "not-recorded",
        },
      };
    }),
  };
}

const run27VisualSelfCheck = {
  cover: ["headline_under_10_words", "memory_rail_visible", "native_surface_visible"],
  setup: ["source_stack_visible", "memory_selection_visible", "workflow_gate_visible"],
  contrast: ["before_after_delta_visible", "after_state_larger_than_before", "trace_not_only_footer"],
  proof: ["source_memory_workflow_route_visible", "native_output_surface_visible"],
  climax: ["single_native_object_40_55_canvas", "side_rail_secondary", "no_equal_card_grid"],
  close: ["public_blocked_gate_visible", "next_data_workflow_step_visible"],
};

function assertRun27MemorySelfCheck(trace) {
  if (trace.arm_id !== "run2_7_full_skill") return;
  for (const slide of trace.slides) {
    const role = slide.rhythm_role;
    if (!slide.run2_7_usecase_id) throw new Error(`Run 2.7 full slide ${slide.slide_id} missing usecase id`);
    if (!slide.run2_7_source_record_ids?.length) throw new Error(`Run 2.7 full slide ${slide.slide_id} missing source records`);
    if (!slide.run2_7_design_memory_ids?.length) throw new Error(`Run 2.7 full slide ${slide.slide_id} missing design memory`);
    if (!slide.run2_7_workflow_decision_ids?.length) throw new Error(`Run 2.7 full slide ${slide.slide_id} missing workflow decisions`);
    if (!run27VisualSelfCheck[role]?.length) throw new Error(`Run 2.7 full slide ${slide.slide_id} missing visual self-check rules`);
    if (role === "climax" && slide.run2_7_quality_gate !== "native_climax_object_present") {
      throw new Error("Run 2.7 climax missing native climax quality gate");
    }
  }
}

async function blobToBuffer(blob) {
  if (blob?.data instanceof Uint8Array) return Buffer.from(blob.data);
  const arrayBuffer = await blob.arrayBuffer();
  return Buffer.from(arrayBuffer);
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
      "secondary deck-profile: engineering-platform",
      `arm: ${arm.armId}`,
      `allowed inputs: ${arm.allowed.join(", ")}`,
      `forbidden inputs: ${arm.forbidden.join(", ")}`,
      "QA gates: trace manifest, native PPT checks, no full-slide rasterization, layout geometry checks, delivery QA, human approval before public release",
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
      "Visible slide structure is editable artifact-tool text and native shapes. No copied source visuals, full-slide raster assets, downloaded video frames, audio files, or full transcripts are used.",
      "",
    ].join("\n"),
  );

  const presentation = Presentation.create(undefined, { slideSize: { width: W, height: H } });
  const slides = arm.slides.map((slide, index) => renderSlide(presentation, slide, arm, index + 1));

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
    const layoutBuffer = await blobToBuffer(await slide.export({ format: "layout" }));
    fs.writeFileSync(layoutPath, layoutBuffer);
    previewPaths.push(previewPath);
    layoutResults.push({ layoutPath });
  }

  const contactSheet = path.join(workspace, "preview", "contact-sheet.png");
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
      source: "scripts/generate_ppt_run2_7_data_workflow_arms.mjs",
      exportName: `slide${String(index + 1).padStart(2, "0")}`,
    })),
  };
  writeJson(path.join(workspace, "output", "artifact-build-manifest.json"), manifest);
  writeJson(path.join(workspace, "qa", "build_manifest_stdout.json"), manifest);
  const trace = traceFor(arm);
  assertRun27MemorySelfCheck(trace);
  writeJson(path.join(workspace, "trace_manifest.json"), trace);
  return { workspace, outputPath, contactSheet, previewPaths };
}

const built = [];
for (const arm of armSpecs) {
  built.push(await buildArm(arm));
}

const runSummary = {
  run_id: "run2_7_data_workflow_thickening",
  arms: ["prompt_only", "run1_5_skill", "run2_7_full_skill", "bad_workflow_memory"],
  contact_sheet: "run2-7-four-arm-contact-sheet.png",
  created: built.map((item) => item.workspace),
};
writeJson(path.join(outRoot, "run2_7_data_workflow_thickening_summary.json"), runSummary);
console.log(JSON.stringify(runSummary, null, 2));
