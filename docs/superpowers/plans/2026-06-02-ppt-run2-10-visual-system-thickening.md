# PPT Run 2.10 Visual System Thickening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and record a Run 2.10 same-stage visual-system-thickening rerun that makes the generated full arm visually distinguishable from Runs 2.7-2.9 while preserving native PPT editability and trace truthfulness.

**Architecture:** Add Run 2.10 data, memory, and workflow artifacts before changing generation. Then add a new four-arm native PPT generator that reads those artifacts only in the full arm, updates the HTML viewer, records result docs, and validates the same two visual outputs: four-arm sheet and full-skill-series sheet.

**Gemini plan-critique guardrails:** Run 2.10 must not be a styling-only pass. The generator and gate matrix must force asymmetrical layout templates, organic whitespace, non-rectangular proof paths, and a shape-count/file-size budget so the result is structurally different from the rectangle-led Run 2.7-2.9 family.

**Tech Stack:** Python pytest for contract tests, JSON case-pack artifacts, Node ESM generator using bundled `@oai/artifact-tool`, Python contact-sheet/viewer helpers, Browser plugin for local viewer validation, gemini-agent for artifact review.

---

## File Structure

- `docs/product/ppt-run2-data-skill-quality/run2_10_visual_system_sources.json`: derived-only visual-system source pack.
- `docs/product/ppt-run2-data-skill-quality/run2_10_visual_system_memory.json`: executable visual-system memory families.
- `docs/product/ppt-run2-data-skill-quality/run2_10_visual_system_gate_matrix.json`: per-slide role gate matrix.
- `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`: add Run 2.10 stages before `generate_code_first_ppt`.
- `docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md`: document Run 2.10 usage and failure rules.
- `docs/product/ppt-run2-data-skill-quality/README.md`: update status and artifact summary.
- `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`: add Run 2.10 required trace fields.
- `scripts/generate_ppt_run2_10_visual_system_arms.mjs`: new four-arm generator.
- `scripts/build_ppt_run_html_viewer.py`: add Run 2.10 to `RUN_SPECS` and Data / Skill references.
- `docs/product/ppt-run2-data-skill-quality/results/run2_10_visual_system_rerun_result.json`: structured result record.
- `docs/product/ppt-run2-data-skill-quality/results/run2_10_visual_system_rerun_result.md`: human-readable result.
- `docs/product/ppt-run2-data-skill-quality/results/README.md`: latest-result summary.
- `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`: top-level comparison update.
- `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`: delivery artifacts and gate checklist.
- `tests/test_ppt_run2_data_skill_quality.py`: all Run 2.10 data, generator, viewer, and result contract tests.

### Task 1: Add Run 2.10 Data Contract Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add expected Run 2.10 constants**

Add constants near the existing Run 2.9 constants:

```python
EXPECTED_RUN2_10_SOURCE_IDS = {
    "vs_source_2_10_editorial_keynote_system",
    "vs_source_2_10_product_theater_demo",
    "vs_source_2_10_typographic_launch_field",
    "vs_source_2_10_kinetic_climax_sequence",
    "vs_source_2_10_non_rectangular_proof_path",
}

EXPECTED_RUN2_10_MEMORY_IDS = {
    "visual_system_editorial_cinema",
    "visual_system_product_theater",
    "visual_system_typographic_field",
    "visual_system_kinetic_demo",
    "visual_system_non_rectangular_proof",
}

EXPECTED_RUN2_10_TRACE_FIELDS = {
    "run2_10_visual_system_source_ids",
    "run2_10_visual_system_memory_ids",
    "run2_10_gate_matrix_ids",
    "run2_10_code_module_ids",
    "run2_10_visual_delta_from_run2_9",
    "run2_10_sameness_failure_probe",
    "run2_10_public_demo_first_read_probe",
    "run2_10_shape_count_budget",
    "run2_10_asymmetry_whitespace_rule",
}
```

- [ ] **Step 2: Add failing data test**

Add this test after `test_run2_9_has_executable_visual_modules_and_gate_matrix`:

```python
def test_run2_10_has_visual_system_sources_memory_and_gate_matrix() -> None:
    sources_path = PACK / "run2_10_visual_system_sources.json"
    memory_path = PACK / "run2_10_visual_system_memory.json"
    matrix_path = PACK / "run2_10_visual_system_gate_matrix.json"
    trace_contract_path = PACK / "results" / "trace_manifest_contract.json"
    workflow_path = PACK / "skill_workflow.json"

    assert sources_path.exists(), "missing Run 2.10 visual-system sources"
    assert memory_path.exists(), "missing Run 2.10 visual-system memory"
    assert matrix_path.exists(), "missing Run 2.10 visual-system gate matrix"

    sources = load_json(sources_path)
    memory = load_json(memory_path)
    matrix = load_json(matrix_path)
    trace_contract = load_json(trace_contract_path)
    workflow = load_json(workflow_path)

    assert sources["status"] == "run2_10_visual_system_sources_public_blocked"
    assert memory["status"] == "run2_10_visual_system_memory_public_blocked"
    assert matrix["status"] == "run2_10_visual_system_gate_matrix_public_blocked"
    assert sources["storage_policy"]["raw_media"] == "forbidden"
    assert sources["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert memory["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert matrix["stage_policy"] == "repeat_same_five_layers_not_run3"

    source_ids = {item["id"] for item in sources["sources"]}
    memory_ids = {item["visual_system_id"] for item in memory["visual_systems"]}
    assert EXPECTED_RUN2_10_SOURCE_IDS <= source_ids
    assert EXPECTED_RUN2_10_MEMORY_IDS <= memory_ids
    assert EXPECTED_RUN2_10_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])

    required_source_fields = {
        "id",
        "source_ids",
        "reference_type",
        "allowed_use",
        "visual_system_direction",
        "typography_observation",
        "spatial_composition_observation",
        "asset_strategy_observation",
        "motion_or_sequence_observation",
        "climax_grammar_observation",
        "native_ppt_implication",
        "anti_copy_boundary",
        "public_demo_probe",
        "release_boundary",
    }
    for source in sources["sources"]:
        assert required_source_fields <= set(source), source["id"]
        assert source["allowed_use"] == "derived_observations_only"
        assert_contains(source["native_ppt_implication"], ["native", "editable"])
        for field_value in iter_string_values(source):
            lowered = field_value.lower()
            for marker in RUN2_8_FORBIDDEN_MEDIA_MARKERS:
                assert marker not in lowered, f"{source['id']} contains copied media marker {marker!r}"

    required_memory_fields = {
        "visual_system_id",
        "source_record_ids",
        "applicable_slide_roles",
        "typography_contract",
        "composition_contract",
        "asset_strategy_contract",
        "motion_sequence_contract",
        "native_ppt_module_implications",
        "forbidden_sameness_patterns",
        "public_demo_first_read_probe",
        "anti_copy_boundary",
        "release_boundary",
    }
    for entry in memory["visual_systems"]:
        assert required_memory_fields <= set(entry), entry["visual_system_id"]
        assert set(entry["source_record_ids"]) <= source_ids
        assert set(entry["applicable_slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert_mentions_any(" ".join(entry["forbidden_sameness_patterns"]), {"rectangle", "same visual family", "palette-only", "dashboard"})

    gate_required_fields = {
        "id",
        "slide_role",
        "visual_system_source_ids",
        "visual_system_memory_ids",
        "required_code_modules",
        "visual_delta_from_run2_9",
        "sameness_failure_probe",
        "public_demo_first_read_probe",
        "shape_count_budget",
        "asymmetry_whitespace_rule",
        "trace_fields",
        "public_release_gate",
    }
    covered_trace_fields = set()
    for gate in matrix["gates"]:
        assert gate_required_fields <= set(gate), gate["id"]
        assert gate["slide_role"] in EXPECTED_RHYTHM_ROLES
        assert set(gate["visual_system_source_ids"]) <= source_ids
        assert set(gate["visual_system_memory_ids"]) <= memory_ids
        assert set(gate["trace_fields"]) <= set(trace_contract["per_slide_required_fields"])
        assert_contains(gate["sameness_failure_probe"], ["Run 2.9"])
        assert_contains(gate["asymmetry_whitespace_rule"], ["asymmetry", "whitespace"])
        assert gate["shape_count_budget"]["max_native_shapes"] <= 72
        covered_trace_fields |= set(gate["trace_fields"])
    assert EXPECTED_RUN2_10_TRACE_FIELDS <= covered_trace_fields

    workflow_stage_ids = [stage["id"] for stage in workflow["stages"]]
    run2_10_stages = [
        "select_run2_10_visual_system_sources",
        "compile_run2_10_visual_system_memory",
        "apply_run2_10_visual_system_gate_matrix",
    ]
    for stage_id in run2_10_stages:
        assert stage_id in workflow_stage_ids
        assert workflow_stage_ids.index(stage_id) < workflow_stage_ids.index("generate_code_first_ppt")
```

- [ ] **Step 3: Run the data test and verify red**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_10_has_visual_system_sources_memory_and_gate_matrix -q
```

Expected: fail with `missing Run 2.10 visual-system sources`.

### Task 2: Add Run 2.10 Data, Memory, Workflow, And Skill Docs

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/run2_10_visual_system_sources.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_10_visual_system_memory.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_10_visual_system_gate_matrix.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/README.md`

- [ ] **Step 1: Create `run2_10_visual_system_sources.json`**

Create the file with schema version, public-blocked status, stage policy, storage policy, and five source records:

```json
{
  "schema_version": 1,
  "status": "run2_10_visual_system_sources_public_blocked",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "storage_policy": {
    "default": "derived_observations_only",
    "raw_media": "forbidden",
    "copyright_boundary": "Store derived observations, visual-system decisions, and native PPT implications only; do not store copied screenshots, source layouts, frames, audio, transcripts, logos, or brand marks."
  },
  "sources": [
    {
      "id": "vs_source_2_10_editorial_keynote_system",
      "source_ids": ["duarte_slide_design_course", "stripe_sessions_2025_product_keynote"],
      "reference_type": "commercial_keynote_plus_tutorial",
      "allowed_use": "derived_observations_only",
      "visual_system_direction": "editorial_cinema",
      "typography_observation": "Use one large decisive phrase and subordinate evidence labels rather than stacked explanatory cards.",
      "spatial_composition_observation": "Use full-bleed fields, off-grid proof rails, and one dominant object path to avoid uniform report panels.",
      "asset_strategy_observation": "Use generated or native abstract stage fields and original product objects; do not copy source UI or event graphics.",
      "motion_or_sequence_observation": "Reveal the field first, then the proof object, then the evidence rail.",
      "climax_grammar_observation": "The peak slide should break from the normal light-card system through stage scale, contrast, and pause.",
      "native_ppt_implication": "Implement as editable native headline text, stage fields, connector paths, and original proof objects.",
      "anti_copy_boundary": "No copied screenshot, source layout, brand mark, frame, transcript, or event graphic.",
      "public_demo_probe": "At thumbnail scale, the slide should read as a keynote moment before any label is readable.",
      "release_boundary": "public_blocked_until_native_render_trace_and_human_review"
    }
  ]
}
```

Add four more records with ids:

- `vs_source_2_10_product_theater_demo`
- `vs_source_2_10_typographic_launch_field`
- `vs_source_2_10_kinetic_climax_sequence`
- `vs_source_2_10_non_rectangular_proof_path`

Each record must use only existing source ids from `sources.json` and must include every field used by the test.

- [ ] **Step 2: Create `run2_10_visual_system_memory.json`**

Create five visual system entries with ids from `EXPECTED_RUN2_10_MEMORY_IDS`. Each entry must map to source ids from the new source file and include contracts for typography, composition, asset strategy, motion sequence, native module implications, forbidden sameness patterns, and first-read probes.

- [ ] **Step 3: Create `run2_10_visual_system_gate_matrix.json`**

Create six gates for slide roles `cover`, `setup`, `contrast`, `proof`, `climax`, and `close`. Each gate must map visual-system source ids and memory ids to required native code modules.

Use these required code modules:

```json
{
  "cover": ["drawRun210EditorialTypeSystem", "drawRun210FullBleedVisualField"],
  "setup": ["drawRun210ProductTheater", "drawRun210NonRectangularProofPath"],
  "contrast": ["drawRun210FullBleedVisualField", "drawRun210NonRectangularProofPath"],
  "proof": ["drawRun210ProductTheater", "drawRun210KineticSequence"],
  "climax": ["drawRun210CinematicClimax", "drawRun210KineticSequence"],
  "close": ["drawRun210EditorialTypeSystem", "drawRun210ProductTheater"]
}
```

- [ ] **Step 4: Update trace contract**

Append these fields to `results/trace_manifest_contract.json` `per_slide_required_fields`:

```json
[
  "run2_10_visual_system_source_ids",
  "run2_10_visual_system_memory_ids",
  "run2_10_gate_matrix_ids",
  "run2_10_code_module_ids",
  "run2_10_visual_delta_from_run2_9",
  "run2_10_sameness_failure_probe",
  "run2_10_public_demo_first_read_probe",
  "run2_10_shape_count_budget",
  "run2_10_asymmetry_whitespace_rule"
]
```

- [ ] **Step 5: Update workflow and skill docs**

Add workflow stages before `generate_code_first_ppt`:

- `select_run2_10_visual_system_sources`
- `compile_run2_10_visual_system_memory`
- `apply_run2_10_visual_system_gate_matrix`

Update `vulca_ppt_skill.md` and README to say Run 2.10 is a visual-system-thickening pass focused on being visibly different from Runs 2.7-2.9.

- [ ] **Step 6: Run the data test and full case-pack tests**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_10_has_visual_system_sources_memory_and_gate_matrix -q
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
```

Expected: both pass.

- [ ] **Step 7: Commit data layer**

Run:

```bash
git add docs/product/ppt-run2-data-skill-quality/run2_10_visual_system_sources.json docs/product/ppt-run2-data-skill-quality/run2_10_visual_system_memory.json docs/product/ppt-run2-data-skill-quality/run2_10_visual_system_gate_matrix.json docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json docs/product/ppt-run2-data-skill-quality/skill_workflow.json docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md docs/product/ppt-run2-data-skill-quality/README.md tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: add PPT run 2.10 visual system data"
```

### Task 3: Add Run 2.10 Generator Contract Test

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add failing generator test**

Add this test after the Run 2.9 generator test:

```python
def test_run2_10_generator_uses_visual_system_modules_and_preserves_boundaries() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_10_visual_system_arms.mjs"
    assert script_path.exists(), "missing Run 2.10 visual-system generator"
    body = script_path.read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_10_full_skill", "bad_visual_system_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else len(body)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    restricted_run2_10_inputs = [
        "run2_10_visual_system_sources.json",
        "run2_10_visual_system_memory.json",
        "run2_10_visual_system_gate_matrix.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_10_full_skill",
            "bad_visual_system_memory",
            "drawRun210FullBleedVisualField",
            "drawRun210ProductTheater",
            "drawRun210KineticSequence",
            "drawRun210EditorialTypeSystem",
            "drawRun210NonRectangularProofPath",
            "drawRun210CinematicClimax",
            "run210VisualSystemsByRole",
            "assertRun210VisualSystemGateSelfCheck",
            "registerRun210VisualModule",
            "run2_10_code_module_ids",
        ],
    )

    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_10_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_10_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_visual_system_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_visual_system_memory"), "forbidden:", "palette:")

    for term in restricted_run2_10_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden

    assert "run2_10_visual_system_sources.json" in bad_allowed
    assert "run2_10_visual_system_memory.json" not in bad_allowed
    assert "run2_10_visual_system_gate_matrix.json" not in bad_allowed
    assert "run2_10_visual_system_memory.json" in bad_forbidden
    assert "run2_10_visual_system_gate_matrix.json" in bad_forbidden
    assert 'const fullRun210 = arm.armId === "run2_10_full_skill";' in body
    for field in EXPECTED_RUN2_10_TRACE_FIELDS:
        assert re.search(fr"{field}:\s*fullRun210\s*\?", body), field
    assert "const actualCodeModuleIds = Array.from(roleMetrics.visualModuleIds);" in body
```

- [ ] **Step 2: Run generator test and verify red**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_10_generator_uses_visual_system_modules_and_preserves_boundaries -q
```

Expected: fail with `missing Run 2.10 visual-system generator`.

### Task 4: Implement Run 2.10 Generator

**Files:**
- Create: `scripts/generate_ppt_run2_10_visual_system_arms.mjs`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Fork Run 2.9 generator**

Copy `scripts/generate_ppt_run2_9_visual_primitive_arms.mjs` to `scripts/generate_ppt_run2_10_visual_system_arms.mjs`, then rename:

- `Run 2.9` to `Run 2.10`
- `run2_9` to `run2_10`
- `Run29` to `Run210`
- `run29` to `run210`
- `visual_primitive` terms to `visual_system` where the data layer is different.

- [ ] **Step 2: Define Run 2.10 inputs and arm boundaries**

Use:

```js
const RUN2_10_INPUTS = {
  sources: `${pack}/run2_10_visual_system_sources.json`,
  memory: `${pack}/run2_10_visual_system_memory.json`,
  gateMatrix: `${pack}/run2_10_visual_system_gate_matrix.json`,
};
```

Rules:

- `run2_10_full_skill` allows all Run 2.10 inputs.
- `bad_visual_system_memory` allows only `RUN2_10_INPUTS.sources`.
- `prompt_only` and `run1_5_skill` forbid all Run 2.10 inputs.

- [ ] **Step 3: Implement data mappers**

Add these functions:

```js
function run210VisualSystemGateMatrixByRole(gateMatrix) {
  return new Map((gateMatrix?.gates ?? []).map((gate) => [gate.slide_role, gate]));
}

function run210VisualSystemSourcesById(sources) {
  return new Map((sources?.sources ?? []).map((source) => [source.id, source]));
}

function run210VisualSystemsByRole(memory) {
  const map = new Map();
  for (const visualSystem of memory?.visual_systems ?? []) {
    for (const role of visualSystem.applicable_slide_roles ?? []) {
      const bucket = map.get(role) ?? [];
      bucket.push(visualSystem);
      map.set(role, bucket);
    }
  }
  return map;
}

function run210CodeModulesByRole(gateMatrix) {
  const map = new Map();
  for (const gate of gateMatrix?.gates ?? []) {
    map.set(gate.slide_role, gate.required_code_modules ?? []);
  }
  return map;
}
```

- [ ] **Step 4: Implement visual-system modules**

Implement native editable drawing functions:

- `drawRun210FullBleedVisualField`
- `drawRun210ProductTheater`
- `drawRun210KineticSequence`
- `drawRun210EditorialTypeSystem`
- `drawRun210NonRectangularProofPath`
- `drawRun210CinematicClimax`

Each function must call:

```js
registerRun210VisualModule(metrics, "drawRun210FunctionName");
```

Each function must render with editable native text and shapes. Do not use screenshots, source images, source UI, or full-slide raster output.

- [ ] **Step 5: Implement full-arm role mapping**

Map slide roles to modules:

```js
const run210ModulesByRole = {
  cover: ["drawRun210EditorialTypeSystem", "drawRun210FullBleedVisualField"],
  setup: ["drawRun210ProductTheater", "drawRun210NonRectangularProofPath"],
  contrast: ["drawRun210FullBleedVisualField", "drawRun210NonRectangularProofPath"],
  proof: ["drawRun210ProductTheater", "drawRun210KineticSequence"],
  climax: ["drawRun210CinematicClimax", "drawRun210KineticSequence"],
  close: ["drawRun210EditorialTypeSystem", "drawRun210ProductTheater"],
};
```

- [ ] **Step 6: Implement trace and self-check**

Trace fields must be populated from the loaded gate matrix and actual `roleMetrics.visualModuleIds`:

```js
const actualCodeModuleIds = Array.from(roleMetrics.visualModuleIds);
```

Self-check must fail when a required gate module is absent from `run2_10_code_module_ids`.

- [ ] **Step 7: Run generator contract test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_10_generator_uses_visual_system_modules_and_preserves_boundaries -q
node --check scripts/generate_ppt_run2_10_visual_system_arms.mjs
```

Expected: both pass.

- [ ] **Step 8: Commit generator**

Run:

```bash
git add scripts/generate_ppt_run2_10_visual_system_arms.mjs tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: add PPT run 2.10 visual system generator"
```

### Task 5: Generate Run 2.10 Outputs And Update Viewer

**Files:**
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Generated local outputs under: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/`

- [ ] **Step 1: Generate Run 2.10 arms**

Run:

```bash
node scripts/generate_ppt_run2_10_visual_system_arms.mjs
```

Expected output includes:

- `ppt-run2-10-prompt-only`
- `ppt-run2-10-run1-5-skill`
- `ppt-run2-10-full-vulca`
- `ppt-run2-10-bad-visual-system-memory`
- `run2-10-four-arm-contact-sheet.png`
- updated `run2-full-skill-series-horizontal.png`

- [ ] **Step 2: Add Run 2.10 viewer spec**

Add this `RunSpec` after Run 2.9:

```python
RunSpec(
    "2.10",
    "Run 2.10",
    "run2-10-four-arm-contact-sheet.png",
    (
        ArmSpec("prompt_only", "Prompt only", "ppt-run2-10-prompt-only", "control"),
        ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-10-run1-5-skill", "baseline"),
        ArmSpec("run2_10_full_skill", "Run 2.10 full", "ppt-run2-10-full-vulca", "full"),
        ArmSpec("bad_visual_system_memory", "Bad visual system", "ppt-run2-10-bad-visual-system-memory", "negative"),
    ),
),
```

- [ ] **Step 3: Update viewer reference data**

Load the three Run 2.10 files in `build_reference_data` and expose:

- `run210SourceStatus`
- `run210VisualSystemSources`
- `run210MemoryStatus`
- `run210VisualSystems`
- `run210GateStatus`
- `run210VisualGates`

Add `Data / Skill` sections for these arrays.

- [ ] **Step 4: Rebuild viewer**

Run:

```bash
python3 scripts/build_ppt_run_html_viewer.py --presentations-dir outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations --out outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html
```

Expected: output JSON reports `"latest": "2.10"`.

- [ ] **Step 5: Browser check**

Open:

```text
http://127.0.0.1:8787/outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html
```

Check that:

- Latest run is 2.10.
- Four arms tab shows Run 2.10.
- Full series tab shows updated horizontal sheet.
- Data / Skill tab shows Run 2.10 sources, memory, and gates.
- No console errors are reported.

- [ ] **Step 6: Commit viewer update**

Run:

```bash
git add scripts/build_ppt_run_html_viewer.py
git commit -m "feat: show PPT run 2.10 in viewer"
```

Do not commit `outputs/`.

### Task 6: Add Run 2.10 Result Docs And Tests

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_10_visual_system_rerun_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_10_visual_system_rerun_result.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add failing result test**

Add this test after the Run 2.9 result test:

```python
def test_run2_10_records_visual_system_rerun_result() -> None:
    result = (PACK / "results" / "run2_10_visual_system_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_10_visual_system_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_10_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert "run2-10-four-arm-contact-sheet.png" in result_json["rerun"]["combined_contact_sheet"]
    assert "run2-full-skill-series-horizontal.png" in result_json["rerun"]["full_skill_series_sheet"]
    assert result_json["rerun"]["html_viewer"].endswith("/ppt-run-viewer.html")
    assert result_json["qa_summary"]["trace_truthfulness_guard"].startswith("passed")
    assert result_json["qa_summary"]["case_pack_validator"] == "passed with --profile run2"
    assert_contains(
        json.dumps(result_json["actual_full_arm_modules_by_role"]),
        [
            "drawRun210FullBleedVisualField",
            "drawRun210ProductTheater",
            "drawRun210KineticSequence",
            "drawRun210EditorialTypeSystem",
            "drawRun210NonRectangularProofPath",
            "drawRun210CinematicClimax",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.10",
            "visual system",
            "HTML viewer",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )
```

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_10_records_visual_system_rerun_result -q
```

Expected: fail because result files are missing.

- [ ] **Step 2: Create result JSON and MD**

The JSON must include:

- `status: "rerun_completed_public_blocked"`
- `public_ready: false`
- `rerun.best_internal_arm: "run2_10_full_skill"`
- paths to `run2-10-four-arm-contact-sheet.png`, `run2-full-skill-series-horizontal.png`, and `ppt-run-viewer.html`
- `actual_full_arm_modules_by_role`
- `visual_learning.useful_delta`
- `visual_learning.remaining_visual_gap`
- `release_gate`

The MD must say Run 2.10 is a same-stage visual-system-thickening rerun, not Run 3.0.

- [ ] **Step 3: Update summary docs**

Update:

- `results/README.md`
- `results/comparison_report.md`
- `results/delivery_gate.md`

Make Run 2.10 the latest generated internal result while preserving public blocked state.

- [ ] **Step 4: Run result tests**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_10_records_visual_system_rerun_result -q
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_ppt_run_html_viewer_builder_tracks_run2_8_outputs -q
```

Expected: both pass. Rename the viewer test to `test_ppt_run_html_viewer_builder_tracks_latest_outputs` if its name becomes misleading.

- [ ] **Step 5: Commit result docs**

Run:

```bash
git add docs/product/ppt-run2-data-skill-quality/results tests/test_ppt_run2_data_skill_quality.py
git commit -m "docs: record PPT run 2.10 visual system rerun"
```

### Task 7: Final Verification And Artifact Review

**Files:**
- All files changed in Tasks 1-6

- [ ] **Step 1: Run full test suite for this area**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
python3 -m pytest tests/test_pptx_delivery_validator.py -q
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
node --check scripts/generate_ppt_run2_10_visual_system_arms.mjs
git diff --check
```

Expected:

- Run 2 data/skill tests pass.
- Delivery validator tests pass.
- Case-pack validator reports `case pack ok`.
- Node syntax check exits 0.
- `git diff --check` exits 0.

- [ ] **Step 2: Ask Gemini to review two visual artifacts**

Review:

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-10-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Ask Gemini to judge:

- whether Run 2.10 full beats the three controls,
- whether Run 2.10 is visually distinguishable from Run 2.7/2.8/2.9,
- whether it is still rectangle-led,
- whether it uses structural asymmetry and whitespace, not only styling,
- whether public release should remain blocked.

- [ ] **Step 3: Update result docs if Gemini finds a material limitation**

If Gemini says Run 2.10 is not visually distinct enough, update `run2_10_visual_system_rerun_result.json`, `run2_10_visual_system_rerun_result.md`, and `comparison_report.md` to record that limitation. Keep `public_ready: false`.

- [ ] **Step 4: Final commit if docs changed after Gemini**

Run:

```bash
git add docs/product/ppt-run2-data-skill-quality/results
git commit -m "docs: update PPT run 2.10 review findings"
```

Skip this commit only if no tracked files changed.
