import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), "..");
const pack = "docs/product/ppt-run2-data-skill-quality";

const EXPECTED_RUN2_8_TRACE_FIELDS = [
  "run2_8_decomposition_unit_ids",
  "run2_8_memory_binding_ids",
  "run2_8_gate_matrix_ids",
  "run2_8_code_binding_ids",
  "run2_8_layout_budget",
  "run2_8_visual_delta_from_run2_7",
];

const RUN2_8_INPUTS = {
  decomposition: `${pack}/run2_8_tutorial_decomposition.json`,
  memory: `${pack}/run2_8_executable_design_memory.json`,
  gateMatrix: `${pack}/run2_8_workflow_gate_matrix.json`,
};
const RUN2_8_RESTRICTED_INPUTS = Object.values(RUN2_8_INPUTS);

const baseSlides = [
  { role: "cover", title: "Executable memory keeps the opening sparse." },
  { role: "setup", title: "The setup binds rules before layout expands." },
  { role: "contrast", title: "Contrast is carried by a visible delta." },
  { role: "proof", title: "Proof stays native and traceable." },
  { role: "climax", title: "The climax holds one dominant object." },
  { role: "close", title: "The close keeps the release gate visible." },
];

const armSpecs = [
  {
    armId: "prompt_only",
    slug: "ppt-run2-8-prompt-only",
    label: "Prompt-only control",
    allowed: [`${pack}/commercial_case.md`],
    forbidden: [
      `${pack}/run2_8_tutorial_decomposition.json`,
      `${pack}/run2_8_executable_design_memory.json`,
      `${pack}/run2_8_workflow_gate_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "docs/product/ppt-run1-5-product-lab/",
    ],
    palette: { bg: "#f5f6f8", rail: "#394456", accent: "#285fd6", panel: "#ffffff" },
    slides: baseSlides,
  },
  {
    armId: "run1_5_skill",
    slug: "ppt-run2-8-run1-5-skill",
    label: "Run 1.5 baseline",
    allowed: [`${pack}/commercial_case.md`, "docs/product/ppt-run1-5-product-lab/"],
    forbidden: [
      `${pack}/run2_8_tutorial_decomposition.json`,
      `${pack}/run2_8_executable_design_memory.json`,
      `${pack}/run2_8_workflow_gate_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
    ],
    palette: { bg: "#f4f6fa", rail: "#2d3a55", accent: "#285fd6", panel: "#ffffff" },
    slides: baseSlides,
  },
  {
    armId: "run2_8_full_skill",
    slug: "ppt-run2-8-full-skill",
    label: "Run 2.8 full executable memory",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/sources.json`,
      `${pack}/run2_8_tutorial_decomposition.json`,
      `${pack}/run2_8_executable_design_memory.json`,
      `${pack}/run2_8_workflow_gate_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      `${pack}/vulca_ppt_skill.md`,
    ],
    forbidden: [
      "docs/product/ppt-run1-5-product-lab/",
      "copied source visuals",
      "winner claims before scoring",
    ],
    palette: { bg: "#f7f4ee", rail: "#1a2228", accent: "#27343c", panel: "#ffffff" },
    slides: baseSlides,
  },
  {
    armId: "bad_memory_schema",
    slug: "ppt-run2-8-bad-memory-schema",
    label: "Bad memory-schema boundary control",
    allowed: [
      `${pack}/commercial_case.md`,
      `${pack}/run2_8_tutorial_decomposition.json`,
      `${pack}/sources.json`,
    ],
    forbidden: [
      `${pack}/run2_8_executable_design_memory.json`,
      `${pack}/run2_8_workflow_gate_matrix.json`,
      `${pack}/skill_workflow.json`,
      `${pack}/results/trace_manifest_contract.json`,
      "manual Run 2.8 memory repair before scoring",
    ],
    palette: { bg: "#f2efe1", rail: "#6d633e", accent: "#968343", panel: "#f9f6e8" },
    slides: baseSlides,
  },
];

function readJson(relPath) {
  return JSON.parse(fs.readFileSync(path.join(root, relPath), "utf8"));
}

function assertArmInputBoundaries(arm) {
  const allowed = new Set(arm.allowed);
  const forbidden = new Set(arm.forbidden);
  const assertAllowed = (input) => {
    if (!allowed.has(input)) throw new Error(`${arm.armId} must allow ${input}`);
    if (forbidden.has(input)) throw new Error(`${arm.armId} cannot both allow and forbid ${input}`);
  };
  const assertForbidden = (input) => {
    if (allowed.has(input)) throw new Error(`${arm.armId} must not allow ${input}`);
    if (!forbidden.has(input)) throw new Error(`${arm.armId} must forbid ${input}`);
  };

  if (arm.armId === "run2_8_full_skill") {
    for (const input of RUN2_8_RESTRICTED_INPUTS) assertAllowed(input);
    return;
  }
  if (arm.armId === "bad_memory_schema") {
    assertAllowed(RUN2_8_INPUTS.decomposition);
    assertForbidden(RUN2_8_INPUTS.memory);
    assertForbidden(RUN2_8_INPUTS.gateMatrix);
    return;
  }
  for (const input of RUN2_8_RESTRICTED_INPUTS) assertForbidden(input);
}

function readRun28JsonForArm(arm, relPath) {
  assertArmInputBoundaries(arm);
  if (arm.armId !== "run2_8_full_skill") {
    throw new Error(`${arm.armId} cannot read Run 2.8 executable-memory input: ${relPath}`);
  }
  if (!arm.allowed.includes(relPath) || arm.forbidden.includes(relPath)) {
    throw new Error(`${arm.armId} input boundary does not permit reading ${relPath}`);
  }
  return readJson(relPath);
}

function drawRun28Climax(slide, binding) {
  if (!binding?.id || !binding?.code_binding?.function_name) {
    throw new Error("Run 2.8 climax requires binding_climax_hero_object with code_binding.function_name");
  }
  return {
    role: slide.role,
    hero_binding_id: binding.id,
    function_name: binding.code_binding.function_name,
  };
}

function run28MemoryBindingsByRole(memory) {
  const bindingsByRole = new Map();
  for (const binding of memory.bindings) {
    for (const role of binding.applies_to_slide_roles) {
      const bucket = bindingsByRole.get(role) ?? [];
      bucket.push(binding);
      bindingsByRole.set(role, bucket);
    }
  }
  return bindingsByRole;
}

function assertRun28GateMatrixSelfCheck(gateMatrix, memoryBindingsByRole) {
  for (const gate of gateMatrix.gates) {
    const known = new Set((memoryBindingsByRole.get(gate.slide_role) ?? []).map((binding) => binding.id));
    for (const bindingId of gate.memory_binding_ids) {
      if (!known.has(bindingId)) {
        throw new Error(`Run 2.8 gate references binding outside role scope: ${gate.slide_role} -> ${bindingId}`);
      }
    }
  }
}

function loadRun28ContractData(arm) {
  const decomposition = readRun28JsonForArm(arm, RUN2_8_INPUTS.decomposition);
  const memory = readRun28JsonForArm(arm, RUN2_8_INPUTS.memory);
  const gateMatrix = readRun28JsonForArm(arm, RUN2_8_INPUTS.gateMatrix);
  const memoryBindingsByRole = run28MemoryBindingsByRole(memory);
  assertRun28GateMatrixSelfCheck(gateMatrix, memoryBindingsByRole);
  return { decomposition, memory, gateMatrix, memoryBindingsByRole };
}

function renderRun28Full(arm) {
  const { decomposition, memory, gateMatrix, memoryBindingsByRole } = loadRun28ContractData(arm);
  const climaxGate = gateMatrix.gates.find((gate) => gate.slide_role === "climax");
  const climaxBinding = (memoryBindingsByRole.get("climax") ?? []).find((binding) => binding.id === "binding_climax_hero_object");
  const climaxPreview = drawRun28Climax({ role: "climax" }, climaxBinding);
  return {
    armId: arm.armId,
    decomposition,
    memory,
    gateMatrix,
    memoryBindingsByRole,
    climaxPreview,
    requiredCodeBindings: climaxGate?.required_code_bindings ?? [],
  };
}

function traceFor(arm) {
  assertArmInputBoundaries(arm);
  const fullRun28 = arm.armId === "run2_8_full_skill";
  const fullData = fullRun28 ? renderRun28Full(arm) : null;
  const gateByRole = new Map((fullData?.gateMatrix?.gates ?? []).map((gate) => [gate.slide_role, gate]));
  const memoryByRole = fullData?.memoryBindingsByRole ?? new Map();
  return {
    arm_id: arm.armId,
    inputs_allowed: arm.allowed,
    inputs_forbidden: arm.forbidden,
    slides: arm.slides.map((slide, index) => {
      const gate = gateByRole.get(slide.role);
      const roleBindings = memoryByRole.get(slide.role) ?? [];
      const climaxBindingIds = slide.role === "climax" ? roleBindings.map((binding) => binding.id) : [];
      return {
        slide_id: `slide_${String(index + 1).padStart(2, "0")}`,
        role: slide.role,
        title: slide.title,
        run2_8_contract_status: fullRun28 ? "full_arm_contract_loaded_not_rendered" : "boundary_stub_not_result",
        run2_8_decomposition_unit_ids: fullRun28 ? gate?.decomposition_unit_ids ?? [] : [],
        run2_8_memory_binding_ids: fullRun28 ? roleBindings.map((binding) => binding.id) : [],
        run2_8_gate_matrix_ids: fullRun28 ? (gate ? [gate.id] : []) : [],
        run2_8_code_binding_ids: fullRun28 ? gate?.required_code_bindings ?? [] : [],
        run2_8_layout_budget: fullRun28 ? gate?.layout_budget ?? {} : {},
        run2_8_visual_delta_from_run2_7: fullRun28 ? "executable memory selects native layout bindings before drawing" : "not available outside Run 2.8 full arm",
        climax_binding_ids: fullRun28 ? climaxBindingIds : [],
      };
    }),
  };
}

function buildArmContract() {
  return armSpecs.map((arm) => ({
    armId: arm.armId,
    label: arm.label,
    contract_status: "run2_8_generator_contract_skeleton_not_final_output",
    allowed: arm.allowed,
    forbidden: arm.forbidden,
    palette: arm.palette,
    trace: traceFor(arm),
  }));
}

function main() {
  return buildArmContract();
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const contract = main();
  process.stdout.write(`${JSON.stringify(contract, null, 2)}\n`);
}

export {
  EXPECTED_RUN2_8_TRACE_FIELDS,
  armSpecs,
  assertRun28GateMatrixSelfCheck,
  buildArmContract,
  drawRun28Climax,
  main,
  renderRun28Full,
  run28MemoryBindingsByRole,
};
