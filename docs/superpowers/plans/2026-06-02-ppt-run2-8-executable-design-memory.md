# PPT Run 2.8 Executable Design Memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Run 2.8 as a same-loop thickening pass that turns tutorial/video decomposition and design memory into explicit code-generation bindings for native PPT.

**Architecture:** Keep the Run 2 case-pack structure and add Run 2.8 artifacts instead of starting Run 3.0. Run 2.8 adds three contracts above Run 2.7: tutorial/video decomposition units, executable design-memory schema bindings, and a workflow gate matrix. The four-arm experiment remains `prompt_only`, `run1_5_skill`, `run2_8_full_skill`, and `bad_memory_schema`.

**Tech Stack:** Python 3 tests with pytest; JSON/Markdown case-pack artifacts; Node ESM generator using bundled `@oai/artifact-tool`; existing PPT layout, trace, contact-sheet, delivery validators; gemini-agent for context compression and artifact review.

---

## Non-Negotiable Product Rule

Every change must deepen the same five-layer loop:

```text
real commercial usecase
-> multimodal tutorial/case database
-> design memory
-> skill workflow
-> code-generated native PPT
```

Run 2.8 is not Run 3.0. It must make data and workflow thicker, not merely restyle slides.

## Research Anchors

Use only derived rules, not copied media, screenshots, transcripts, slide layouts, or source prose:

- Duarte visual storytelling: prioritize the story, motivate action, visually enhance the most important data, and remove the rest.
- Type hierarchy guidance: use explicit type levels, line-length limits, readable line spacing, and no negative tracking.
- Slide makeover examples: split long blocks, replace text with visual structure where possible, shorten titles, remove distracting backgrounds, and keep styles consistent.
- DeepSlides / design-first slide generation: separate page design decisions from implementation code before native PPT generation.

## File Map

- Modify `tests/test_ppt_run2_data_skill_quality.py`: add Run 2.8 data, schema, workflow, generator, and result contract tests.
- Modify `tests/test_ppt_case_pack_validator.py`: add focused validator failures for Run 2.8 schema gaps.
- Modify `scripts/validate_ppt_case_pack.py`: require and validate Run 2.8 decomposition, executable memory schema, and workflow gate matrix.
- Create `docs/product/ppt-run2-data-skill-quality/run2_8_tutorial_decomposition.json`: derived tutorial/video/case decomposition units.
- Create `docs/product/ppt-run2-data-skill-quality/run2_8_executable_design_memory.json`: memory tokens with code bindings and native PPT constraints.
- Create `docs/product/ppt-run2-data-skill-quality/run2_8_workflow_gate_matrix.json`: per-slide workflow gates and pass/fail thresholds.
- Modify `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`: add Run 2.8 decomposition and executable-memory stages before native generation.
- Modify `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`: require Run 2.8 trace fields.
- Create `scripts/generate_ppt_run2_8_executable_memory_arms.mjs`: four-arm runner.
- Modify `docs/product/ppt-run2-data-skill-quality/results/README.md`: add Run 2.8 result links.
- Modify `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`: add Run 2.8 comparison and interpretation.
- Modify `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`: add Run 2.8 delivery records.
- Create `docs/product/ppt-run2-data-skill-quality/results/run2_8_executable_design_memory_result.json`.
- Create `docs/product/ppt-run2-data-skill-quality/results/run2_8_executable_design_memory_result.md`.
- Create `docs/product/ppt-run2-data-skill-quality/results/run2_8_visual_qa_gate.json`.

## Task 1: Add Run 2.8 Contract Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Modify: `tests/test_ppt_case_pack_validator.py`

- [ ] **Step 1: Add Run 2.8 constants**

Add constants near the existing Run 2.7 constants:

```python
EXPECTED_RUN2_8_DECOMPOSITION_IDS = {
    "decomp_2_8_duarte_remove_nonessential_data",
    "decomp_2_8_type_hierarchy_readability_stack",
    "decomp_2_8_makeover_split_text_into_visual_steps",
    "decomp_2_8_design_first_code_second_pipeline",
    "decomp_2_8_climax_object_scale_and_pause",
    "decomp_2_8_source_brand_sanitized_case_evidence",
}
EXPECTED_RUN2_8_MEMORY_BINDING_IDS = {
    "binding_type_scale_readability",
    "binding_spacing_zone_grid",
    "binding_climax_hero_object",
    "binding_before_after_delta",
    "binding_public_gate_legibility",
}
EXPECTED_RUN2_8_TRACE_FIELDS = {
    "run2_8_decomposition_unit_ids",
    "run2_8_memory_binding_ids",
    "run2_8_gate_matrix_ids",
    "run2_8_code_binding_ids",
    "run2_8_layout_budget",
    "run2_8_visual_delta_from_run2_7",
}
```

- [ ] **Step 2: Add decomposition contract test**

Add `test_run2_8_has_tutorial_video_decomposition_units` after the Run 2.7 workflow test. It must load `run2_8_tutorial_decomposition.json`, `run2_7_multimodal_source_records.json`, and `sources.json`, then assert:

```python
assert decomposition["status"] == "run2_8_tutorial_decomposition_public_blocked"
assert decomposition["stage_policy"] == "repeat_same_five_layers_not_run3"
assert decomposition["storage_policy"]["raw_media"] == "forbidden"
assert EXPECTED_RUN2_8_DECOMPOSITION_IDS <= {unit["id"] for unit in decomposition["units"]}
```

For each unit assert these keys exist:

```python
{
    "id",
    "source_record_ids",
    "source_ids",
    "modality_mix",
    "tutorial_anchor",
    "observed_design_move",
    "derived_rule",
    "code_generation_binding",
    "native_ppt_obligation",
    "layout_budget",
    "failure_probe",
    "anti_copy_boundary",
    "qa_probe",
    "release_boundary",
}
```

Also assert `source_record_ids` are drawn from Run 2.7 records, `source_ids` are valid, `modality_mix` includes at least one of `video`, `audio`, `transcript`, `image_reference`, `interaction`, `code_generation_binding` mentions `native`, and no field contains copied media markers such as `.png`, `.jpg`, `.mp4`, `http://`, `https://`, or `base64,`.

- [ ] **Step 3: Add executable design-memory test**

Add `test_run2_8_has_executable_design_memory_bindings`. It must load `run2_8_executable_design_memory.json` and assert:

```python
assert memory["status"] == "run2_8_executable_design_memory_public_blocked"
assert memory["stage_policy"] == "repeat_same_five_layers_not_run3"
assert memory["memory_type"] == "executable_schema_bindings"
assert EXPECTED_RUN2_8_MEMORY_BINDING_IDS <= {binding["id"] for binding in memory["bindings"]}
```

For each binding assert these keys exist:

```python
{
    "id",
    "decomposition_unit_ids",
    "applies_to_slide_roles",
    "design_token",
    "code_binding",
    "native_ppt_constraints",
    "typography_constraints",
    "spacing_constraints",
    "composition_constraints",
    "negative_control_failure",
    "qa_probe",
    "release_boundary",
}
```

Also assert bindings reference valid decomposition units, use known rhythm roles, include `function_name`, `params`, and `layout_budget` inside `code_binding`, and mention at least one of `fontSize`, `bbox`, `spacing`, `heroObject`, `beforeAfter`, or `workflowGate`.

- [ ] **Step 4: Add workflow gate matrix test**

Add `test_run2_8_workflow_gate_matrix_connects_schema_to_trace`. It must load `run2_8_workflow_gate_matrix.json`, `skill_workflow.json`, and `results/trace_manifest_contract.json`, then assert:

```python
assert matrix["status"] == "run2_8_workflow_gate_matrix_public_blocked"
assert matrix["stage_policy"] == "repeat_same_five_layers_not_run3"
assert set(matrix["selection_chain"]) == {
    "commercial_usecase",
    "run2_8_decomposition_units",
    "run2_8_executable_memory_bindings",
    "run2_8_gate_matrix",
    "native_ppt_code_generation",
    "layout_quality_gate",
    "delivery_gate",
    "visual_qa_gate",
}
assert EXPECTED_RUN2_8_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])
```

For each gate assert it has `slide_role`, `decomposition_unit_ids`, `memory_binding_ids`, `required_code_bindings`, `layout_budget`, `pass_fail_checks`, `trace_fields`, and `public_release_gate`.

- [ ] **Step 5: Add generator contract test**

Add `test_run2_8_generator_uses_executable_memory_and_preserves_boundaries`. It must expect a new script `scripts/generate_ppt_run2_8_executable_memory_arms.mjs`, the four arm ids, Run 2.8 input files, `renderRun28Full`, `drawRun28Climax`, `run28MemoryBindingsByRole`, `assertRun28GateMatrixSelfCheck`, and `run2_8_memory_binding_ids`. It must verify:

- prompt-only and Run 1.5 forbid all Run 2.8 files.
- full arm allows all Run 2.8 files.
- bad-memory-schema allows decomposition units but forbids executable design memory and gate matrix.
- full arm trace fields use `fullRun28`.
- bad arm never claims Run 2.8 memory binding success.

- [ ] **Step 6: Add validator regression tests**

In `tests/test_ppt_case_pack_validator.py`, add tests that copy the Run 2 pack to a temp dir and assert validation fails when:

- a decomposition unit has empty `code_generation_binding`;
- a design-memory binding references an unknown decomposition unit;
- a gate matrix references an unknown memory binding;
- a Run 2.8 trace field is removed from `results/trace_manifest_contract.json`.

- [ ] **Step 7: Run tests and confirm red state**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py tests/test_ppt_case_pack_validator.py
```

Expected: failures for missing Run 2.8 files and generator.

## Task 2: Add Run 2.8 Data, Memory, Workflow, and Validator Support

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/run2_8_tutorial_decomposition.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_8_executable_design_memory.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_8_workflow_gate_matrix.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`
- Modify: `scripts/validate_ppt_case_pack.py`

- [ ] **Step 1: Create Run 2.8 decomposition data**

Create six units that correspond to the expected ids. Each unit must be derived from existing Run 2.7 source records and external research anchors. Do not store raw source text, screenshots, video frames, audio, transcripts, or source layouts.

- [ ] **Step 2: Create executable memory bindings**

Create five bindings with deterministic code-binding objects:

```json
{
  "function_name": "drawRun28TypeScale",
  "params": {
    "title_min_pt": 40,
    "body_min_pt": 18,
    "max_line_chars": 60,
    "letter_spacing": 0
  },
  "layout_budget": {
    "max_text_boxes": 9,
    "max_visible_words": 52
  }
}
```

Use equivalent binding objects for spacing zones, climax hero object, before/after delta, and public gate legibility.

- [ ] **Step 3: Create workflow gate matrix**

Create six gates, one for each slide role. Each gate must connect decomposition units, memory bindings, code bindings, layout budget, trace fields, and public release gate. The climax gate must require `binding_climax_hero_object` and a hero object occupying 44-58% of the main canvas.

- [ ] **Step 4: Update workflow and trace contract**

Add workflow stages `decompose_run2_8_tutorial_video_units`, `select_run2_8_executable_design_memory`, and `apply_run2_8_workflow_gate_matrix` before native generation. Add all `EXPECTED_RUN2_8_TRACE_FIELDS` to `results/trace_manifest_contract.json`.

- [ ] **Step 5: Update validator**

Require Run 2.8 files for profile `run2`. Add validation helpers for decomposition unit cross-references, executable memory binding cross-references, gate matrix cross-references, raw-media marker exclusion, and trace contract fields.

- [ ] **Step 6: Run tests and validator**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py tests/test_ppt_case_pack_validator.py
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
```

Expected: all Run 2.8 data/validator tests pass. Generator test still fails until Task 3/4.

## Task 3: Add Run 2.8 Generator Contract

**Files:**
- Create: `scripts/generate_ppt_run2_8_executable_memory_arms.mjs`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add placeholder generator**

Create the script by copying the Run 2.7 generator and changing only names, arm ids, slugs, and required Run 2.8 trace field names. Leave the full visual implementation intentionally incomplete if needed.

- [ ] **Step 2: Run generator contract test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_8_generator_uses_executable_memory_and_preserves_boundaries -q
```

Expected: fail only on missing implementation-specific identifiers that Task 4 will add.

## Task 4: Implement Run 2.8 Generator

**Files:**
- Modify: `scripts/generate_ppt_run2_8_executable_memory_arms.mjs`

- [ ] **Step 1: Implement Run 2.8 role maps**

Add `run28DecompositionByRole`, `run28MemoryBindingsByRole`, `run28GateMatrixByRole`, `run28CodeBindingsByRole`, `run28LayoutBudgetByRole`, and `run28VisualDeltaByRole`.

- [ ] **Step 2: Implement full-arm native modules**

Add `renderRun28Full`, `drawRun28Climax`, `drawRun28TypeScale`, `drawRun28BeforeAfterDelta`, and `drawRun28WorkflowGate`. These must generate editable text and native shapes only.

- [ ] **Step 3: Implement negative control**

The bad-memory-schema arm must receive decomposition units but not executable memory or gate matrix. It should visibly regress into dense, weakly bound layouts without causing layout QA failures.

- [ ] **Step 4: Implement self-check**

Add `assertRun28GateMatrixSelfCheck(trace)` so full-arm slides fail generation if any Run 2.8 trace field is empty, the climax lacks the hero binding, or a slide exceeds its layout budget.

- [ ] **Step 5: Run generator and contract tests**

Run:

```bash
node --check scripts/generate_ppt_run2_8_executable_memory_arms.mjs
THREAD_ID=019e7d9c-532a-70b3-8892-fa3ae42baef2 node scripts/generate_ppt_run2_8_executable_memory_arms.mjs
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_8_generator_uses_executable_memory_and_preserves_boundaries -q
```

Expected: generator succeeds and contract test passes.

## Task 5: Rerun Four Arms, QA, Gemini, and Results

**Files:**
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_8_executable_design_memory_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_8_executable_design_memory_result.md`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_8_visual_qa_gate.json`

- [ ] **Step 1: Build four per-arm contact sheets**

Use `scripts/build_ppt_contact_sheet.py` for:

- `ppt-run2-8-prompt-only`
- `ppt-run2-8-run1-5-skill`
- `ppt-run2-8-full-vulca`
- `ppt-run2-8-bad-memory-schema`

- [ ] **Step 2: Build mandatory comparison images**

Create:

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-8-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

- [ ] **Step 3: Run QA**

For all four arms, run layout QA, delivery QA, trace refresh, and native/arm-boundary guard. Expected layout is `0 errors / 0 warnings`; delivery remains `internal-demo-ok-public-blocked`; media and picture counts remain zero.

- [ ] **Step 4: Run Gemini artifact review**

Review the four-arm image and full-skill-series image with `gemini_artifact_review`, `write_artifact=true`.

- [ ] **Step 5: Write result docs**

Record that generated outputs remain untracked, public is blocked, and Run 2.8 is an internal proof of executable design memory only. Do not claim public-video-ready quality.

- [ ] **Step 6: Final verification**

Run:

```bash
node --check scripts/generate_ppt_run2_8_executable_memory_arms.mjs
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py tests/test_ppt_case_pack_validator.py
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
git diff --check
git ls-files outputs | wc -l
```

Expected: tests pass, validator says case pack ok, diff check is clean, and tracked outputs count is `0`.
