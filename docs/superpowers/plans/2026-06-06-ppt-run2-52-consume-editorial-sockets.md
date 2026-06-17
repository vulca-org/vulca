# PPT Run 2.52 Editorial Socket Rerun Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Run 2.52 as the generated four-arm proof that consumes Run 2.51 editorial copy, shape text sockets, and renderer archetype workflow gates before native PPT drawing.

**Architecture:** Follow the existing Run 2.50 generated-rerun pattern, but make Run 2.51 consumption the blocking contract. Add a new artifact-tool generator, record result JSON/Markdown, add one generated-proof workflow stage, and update the HTML viewer so Run 2.52 becomes the latest generated output while Run 2.51 remains the latest data/workflow repair input. The full arm must bind Run 2.51 ids in trace before drawing public text; the bad control must fail because it lacks those ids.

**Tech Stack:** Node.js ESM, `@oai/artifact-tool/presentation-jsx` through the existing bundled artifact-tool runtime, Python/pytest, existing case-pack JSON artifacts, HTML viewer builder.

---

## File Structure

- Create `scripts/generate_ppt_run2_52_editorial_socket_renderer_arms.mjs`
  - Responsibility: generate four editable native PPT arms, render PNG previews/contact sheets/layout JSON, write trace manifests, and record a Run 2.52 result.
- Modify `tests/test_ppt_run2_data_skill_quality.py`
  - Responsibility: add failing tests for Run 2.52 generator contracts, recorded result artifacts, trace fields, and viewer latest-run update.
- Create `docs/product/ppt-run2-data-skill-quality/results/run2_52_editorial_socket_renderer_rerun_result.json`
  - Responsibility: machine-readable Run 2.52 result summary.
- Create `docs/product/ppt-run2-data-skill-quality/results/run2_52_editorial_socket_renderer_rerun_result.md`
  - Responsibility: human-readable Run 2.52 boundary report.
- Modify `docs/product/ppt-run2-data-skill-quality/results/README.md`
  - Responsibility: list Run 2.52 as the generated proof consuming Run 2.51.
- Modify `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
  - Responsibility: add one generated-proof stage after Run 2.51 stages with sequential `order: 50`.
- Modify `scripts/build_ppt_run_html_viewer.py`
  - Responsibility: add Run 2.52 to `RUN_SPECS`, show its result in Data / Skill, keep Run 2.51 visible as the data/workflow repair layer that Run 2.52 consumes, and include Run 2.52 in the full-skill series sheet.

## Shared Constants

Use these exact values in generator, tests, and result artifacts:

```js
const RUN_ID = "2.52";
const RUN2_52_FULL_STATUS = "run2_51_editorial_socket_pack_consumed_before_native_ppt_drawing";
const RUN2_52_BAD_STATUS = "run2_50_generated_but_run2_51_editorial_socket_pack_missing";
const RUN2_52_POLICY = "editorial_copy_shape_text_socket_and_renderer_archetype_binding";
const selectedUsecaseId = "usecase_design_to_production_platform_launch";
```

Use these exact arm ids and slugs:

```js
prompt_only -> ppt-run2-52-prompt-only
run1_5_skill -> ppt-run2-52-run1-5-skill
run2_52_full_editorial_socket_renderer -> ppt-run2-52-full-vulca
bad_run2_51_missing_editorial_socket_pack -> ppt-run2-52-bad-missing-run2-51-editorial-socket-pack
```

The full arm must allow:

```js
[
  "docs/product/ppt-run2-data-skill-quality/commercial_case.md",
  "docs/product/ppt-run2-data-skill-quality/results/run2_51_editorial_shape_text_repair_result.json",
  "docs/product/ppt-run2-data-skill-quality/run2_51_editorial_copy_memory.json",
  "docs/product/ppt-run2-data-skill-quality/run2_51_shape_text_socket_memory.json",
  "docs/product/ppt-run2-data-skill-quality/run2_51_renderer_archetype_workflow_gates.json",
  "docs/product/ppt-run2-data-skill-quality/results/run2_50_readability_density_renderer_rerun_result.json",
  "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-50-full-vulca/trace_manifest.json",
  "docs/product/ppt-run2-data-skill-quality/skill_workflow.json",
  "docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md"
]
```

The bad control may read Run 2.50 generated traces and commercial sources, but must forbid every Run 2.51 artifact and every `run2_51_*` trace field.

---

### Task 1: Add Failing Tests For Run 2.52 Generator Contracts

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create in Task 2: `scripts/generate_ppt_run2_52_editorial_socket_renderer_arms.mjs`

- [ ] **Step 1: Add Run 2.52 expected trace field constant**

Add near `EXPECTED_RUN2_51_TRACE_FIELDS`:

```python
EXPECTED_RUN2_52_TRACE_FIELDS = {
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
    "run2_52_code_module_ids",
    "run2_52_primary_surface_kind",
    "run2_52_socket_bound_public_text_elements",
    "run2_52_shape_primitive_count",
}
```

- [ ] **Step 2: Add static generator contract test**

Append after the Run 2.51 tests:

```python
def test_run2_52_generator_consumes_run2_51_editorial_socket_pack() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_52_editorial_socket_renderer_arms.mjs"
    assert script_path.exists(), "missing Run 2.52 editorial socket renderer generator"
    body = script_path.read_text(encoding="utf-8")

    assert_contains(
        body,
        [
            "run2_51_editorial_shape_text_repair_result.json",
            "run2_51_editorial_copy_memory.json",
            "run2_51_shape_text_socket_memory.json",
            "run2_51_renderer_archetype_workflow_gates.json",
            "run2_51_editorial_copy_memory_id",
            "run2_51_shape_text_socket_memory_id",
            "run2_51_renderer_archetype_gate_id",
            "run2_51_primary_archetype",
            "run2_51_public_surface_copy_status",
            "run2_51_text_socket_placement_status",
            "bad_run2_51_missing_editorial_socket_pack",
            "drawRun252EditorialSocketScene",
            "run2_51_editorial_socket_pack_consumed_before_native_ppt_drawing",
        ],
    )
```

- [ ] **Step 3: Add recorded output test for result and traces**

Append after the static test:

```python
def test_run2_52_records_editorial_socket_renderer_rerun_result() -> None:
    result_md = (PACK / "results" / "run2_52_editorial_socket_renderer_rerun_result.md").read_text(
        encoding="utf-8"
    )
    result_json = load_json(PACK / "results" / "run2_52_editorial_socket_renderer_rerun_result.json")
    presentations = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"
    full_trace = load_json(presentations / "ppt-run2-52-full-vulca" / "trace_manifest.json")
    bad_trace = load_json(
        presentations / "ppt-run2-52-bad-missing-run2-51-editorial-socket-pack" / "trace_manifest.json"
    )

    assert result_json["run_id"] == "2.52"
    assert result_json["status"] == "run2_52_editorial_socket_renderer_rerun_public_blocked"
    assert result_json["source_repair_run_id"] == "2.51"
    assert result_json["source_generated_run_id"] == "2.50"
    assert result_json["rerun"]["best_internal_arm"] == "run2_52_full_editorial_socket_renderer"
    assert result_json["quality_delta"]["target_layer"] == (
        "editorial_copy_shape_text_socket_and_renderer_archetype_binding"
    )
    assert result_json["quality_delta"]["source_data_status"] == (
        "run2_51_editorial_socket_pack_consumed_before_native_ppt_drawing"
    )
    assert result_json["quality_delta"]["full_slides_with_run2_51_editorial_copy_memory_id"] == 6
    assert result_json["quality_delta"]["full_slides_with_run2_51_shape_text_socket_memory_id"] == 6
    assert result_json["quality_delta"]["full_slides_with_run2_51_renderer_archetype_gate_id"] == 6
    assert result_json["quality_delta"]["full_slides_with_socket_bound_public_text"] == 6
    assert result_json["quality_delta"]["bad_control_slides_without_run2_51_pack"] == 6
    assert result_json["rerun"]["combined_contact_sheet"].endswith("run2-52-four-arm-contact-sheet.png")

    assert full_trace["arm_id"] == "run2_52_full_editorial_socket_renderer"
    assert full_trace["run2_52_editorial_socket_renderer_status"] == (
        "run2_51_editorial_socket_pack_consumed_before_native_ppt_drawing"
    )
    assert len(full_trace["slides"]) == 6
    for slide in full_trace["slides"]:
        assert EXPECTED_RUN2_52_TRACE_FIELDS <= set(slide)
        assert slide["run2_51_editorial_copy_memory_id"].startswith("editorial_copy_2_51_")
        assert slide["run2_51_shape_text_socket_memory_id"].startswith("shape_text_socket_2_51_")
        assert slide["run2_51_renderer_archetype_gate_id"].startswith("gate_2_51_")
        assert slide["run2_51_public_surface_copy_status"] == "pass_internal"
        assert slide["run2_51_text_socket_placement_status"] == "pass_internal"
        assert slide["run2_51_shape_vocabulary_status"] == "pass_internal"
        assert slide["run2_51_character_fit_status"] == "pass_internal"
        assert slide["run2_51_forbidden_surface_terms_count"] == 0
        assert slide["run2_51_equal_card_cluster_count"] <= 1
        assert slide["run2_51_semantic_primitive_count"] >= 3
        assert slide["run2_52_socket_bound_public_text_elements"] >= 4
        assert slide["run2_52_shape_primitive_count"] >= 3
        assert slide["run2_52_primary_surface_kind"] != "square_block_grid"
        assert slide["layout_metrics"]["visible_words"] >= 48
        assert slide["layout_metrics"]["proof_objects"] >= 2
        assert slide["run2_52_code_module_ids"][0].startswith("drawRun252")

    assert bad_trace["arm_id"] == "bad_run2_51_missing_editorial_socket_pack"
    for slide in bad_trace["slides"]:
        assert slide["run2_51_editorial_copy_memory_id"] == ""
        assert slide["run2_51_shape_text_socket_memory_id"] == ""
        assert slide["run2_51_renderer_archetype_gate_id"] == ""
        assert slide["run2_51_public_surface_copy_status"] == "fail_missing_run2_51"

    assert_contains(
        result_md,
        [
            "Run 2.52 Editorial Socket Renderer Rerun",
            "consumes Run 2.51",
            "editorial copy",
            "shape text sockets",
            "renderer archetype",
            "bad_run2_51_missing_editorial_socket_pack",
            "public blocked",
        ],
    )
```

- [ ] **Step 4: Add malformed Run 2.51 input validation test**

Append after the recorded output test:

```python
def test_run2_52_generator_rejects_malformed_run2_51_source() -> None:
    script_path = ROOT / "scripts" / "generate_ppt_run2_52_editorial_socket_renderer_arms.mjs"
    body = script_path.read_text(encoding="utf-8")

    assert "validateRun252RepairPack" in body
    assert "Run 2.52 must consume Run 2.51 repair result" in body
    assert "Run 2.52 editorial copy status mismatch" in body
    assert "Run 2.52 socket status mismatch" in body
    assert "Run 2.52 renderer archetype gate status mismatch" in body
    assert "consumer_contract.next_generated_run" in body
    assert "must_bind_before_public_text" in body
    assert "missing role contract" in body
```

- [ ] **Step 5: Add bad-control leakage guard test**

Append after malformed source test:

```python
def test_run2_52_bad_control_trace_does_not_leak_run2_51_fields() -> None:
    presentations = ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"
    bad_trace = load_json(
        presentations / "ppt-run2-52-bad-missing-run2-51-editorial-socket-pack" / "trace_manifest.json"
    )

    for slide in bad_trace["slides"]:
        leaked_values = [
            value
            for key, value in slide.items()
            if key.startswith("run2_51_")
            and key not in {
                "run2_51_editorial_copy_memory_id",
                "run2_51_shape_text_socket_memory_id",
                "run2_51_renderer_archetype_gate_id",
                "run2_51_public_surface_copy_status",
            }
            and value not in ("", 0, [], False, None, "fail_missing_run2_51")
        ]
        assert leaked_values == []
```

- [ ] **Step 6: Run the new tests and verify they fail**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_52_generator_consumes_run2_51_editorial_socket_pack tests/test_ppt_run2_data_skill_quality.py::test_run2_52_records_editorial_socket_renderer_rerun_result tests/test_ppt_run2_data_skill_quality.py::test_run2_52_generator_rejects_malformed_run2_51_source tests/test_ppt_run2_data_skill_quality.py::test_run2_52_bad_control_trace_does_not_leak_run2_51_fields -q
```

Expected: fail because the generator and result artifacts do not exist.

- [ ] **Step 7: Commit failing tests**

```bash
git add tests/test_ppt_run2_data_skill_quality.py
git commit -m "test: add run2.52 editorial socket rerun contract"
```

### Task 2: Implement Run 2.52 Generator And Trace Contracts

**Files:**
- Create: `scripts/generate_ppt_run2_52_editorial_socket_renderer_arms.mjs`

- [ ] **Step 1: Create generator by adapting Run 2.50 structure**

Start from `scripts/generate_ppt_run2_50_readability_density_renderer_arms.mjs`, but rename all Run 2.50-specific public contracts to Run 2.52 and add these inputs:

```js
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
```

Full arm data inputs are `Object.values(RUN2_52_INPUTS)`. Bad control inputs are Run 2.50 result/traces plus commercial sources, but not Run 2.51 result/copy/socket/gates.

- [ ] **Step 2: Add Run 2.52 validation**

Implement `validateRun252RepairPack(data)` with these exact failures:

```js
if (run251Result?.status !== "run2_51_editorial_shape_text_repair_ready_public_blocked") throw new Error("Run 2.52 must consume Run 2.51 repair result");
if (run251Result?.next_required_action !== "consume_run2_51_before_run2_52_four_arm_rerun") throw new Error("Run 2.51 result does not point to Run 2.52");
if (run251Copy?.status !== "run2_51_editorial_copy_memory_ready_public_blocked") throw new Error("Run 2.52 editorial copy status mismatch");
if (run251Sockets?.status !== "run2_51_shape_text_socket_memory_ready_public_blocked") throw new Error("Run 2.52 socket status mismatch");
if (run251Gates?.status !== "run2_51_renderer_archetype_workflow_gates_ready_public_blocked") throw new Error("Run 2.52 renderer archetype gate status mismatch");
if (run250Result?.status !== "run2_50_readability_density_renderer_rerun_public_blocked") throw new Error("Run 2.52 must use Run 2.50 as source generated run");
if (run250FullTrace?.arm_id !== "run2_50_full_readability_density_renderer") throw new Error("Run 2.52 must compare against Run 2.50 full trace");
```

Also validate six records per role and these cross-links:

```js
socket.required_editorial_copy_memory_id === copy.copy_memory_id
gate.required_editorial_copy_memory_id === copy.copy_memory_id
gate.required_shape_text_socket_memory_id === socket.socket_memory_id
gate.consumer_contract.next_generated_run === "2.52"
gate.consumer_contract.must_bind_before_public_text === true
```

- [ ] **Step 2a: Add explicit schema-shape guards**

Inside `validateRun252RepairPack(data)`, reject empty or malformed Run 2.51 artifacts before drawing:

```js
if (!Array.isArray(run251Copy?.editorial_copy_records) || run251Copy.editorial_copy_records.length !== 6) throw new Error("Run 2.52 requires six Run 2.51 copy records");
if (!Array.isArray(run251Sockets?.shape_text_socket_records) || run251Sockets.shape_text_socket_records.length !== 6) throw new Error("Run 2.52 requires six Run 2.51 socket records");
if (!Array.isArray(run251Gates?.renderer_archetype_workflow_gates) || run251Gates.renderer_archetype_workflow_gates.length !== 6) throw new Error("Run 2.52 requires six Run 2.51 renderer gates");
for (const role of baseSlides.map((slide) => slide.role)) {
  const copy = run251Copy.editorial_copy_records.find((record) => record.role === role);
  const socket = run251Sockets.shape_text_socket_records.find((record) => record.role === role);
  const gate = run251Gates.renderer_archetype_workflow_gates.find((record) => record.role === role);
  if (!copy || !socket || !gate) throw new Error(`Run 2.52 missing role contract for ${role}`);
}
```

- [ ] **Step 3: Add `selectRun252ForSlide(role, contractData)`**

Return one object with:

```js
{
  role,
  copy,
  socket,
  gate,
  priorTraceSlide,
  usecase,
  publicCopy: copy.public_surface_copy_bundle,
  socketContracts: socket.socket_contracts ?? [],
  shapePrimitives: socket.shape_primitives ?? [],
  primaryArchetype: gate.primary_archetype,
  proofSocketIds: socket.proof_socket_ids ?? [],
  primarySurfaceKind: gate.primary_archetype,
}
```

Throw `Run 2.52 missing role contract for ${role}` when any linked record is absent.

- [ ] **Step 4: Add native shape/socket drawing**

Implement `drawRun252EditorialSocketScene(slide, arm, spec, selection, metrics, moduleName)` and make it the only module used by the full arm.

Minimum required behavior:

```js
registerRun252Module(metrics, moduleName);
metrics.primarySurfaceKind = selection.primaryArchetype;
metrics.socketBoundPublicTextElements = 0;
metrics.shapePrimitiveCount = selection.shapePrimitives.length;
```

Draw all public text from `selection.publicCopy`, never from raw evidence fields:

```js
socketText(slide, selection.publicCopy.headline, ...);
socketText(slide, selection.publicCopy.subline, ...);
selection.publicCopy.proof_nuggets.slice(0, 3).forEach(...socketText...);
selection.publicCopy.annotations.slice(0, 2).forEach(...socketText...);
```

Every `socketText` call must increment `metrics.socketBoundPublicTextElements`, register visible words, and use native editable text.

Use different primary shape grammars by role:

```js
cover -> poster_stage: stage field + spotlight + proof badge + ribbon
setup -> route_map: connected route path + node labels + bracket callout + risk marker
contrast -> before_after_lens: small before lens + dominant after lens + delta marker
proof -> workspace_surface: working surface + lanes + proof objects + review state
climax -> exploded_hero_object: dominant result object + 3 offset layers + proof tags
close -> decision_room: decision wall + gate strips + next-action route
```

Do not use an equal three-card grid as the primary surface.

- [ ] **Step 5: Add Run 2.52 trace and self-check**

`traceFor()` must add these slide fields for the full arm:

```js
run2_51_editorial_copy_memory_id
run2_51_shape_text_socket_memory_id
run2_51_renderer_archetype_gate_id
run2_51_primary_archetype
run2_51_public_surface_copy_status
run2_51_text_socket_placement_status
run2_51_shape_vocabulary_status
run2_51_character_fit_status
run2_51_forbidden_surface_terms_count
run2_51_equal_card_cluster_count
run2_51_semantic_primitive_count
run2_52_primary_surface_kind
run2_52_code_module_ids
run2_52_socket_bound_public_text_elements
run2_52_shape_primitive_count
```

For bad control, those id fields must be empty strings and `run2_51_public_surface_copy_status` must be `fail_missing_run2_51`.

`assertRun252EditorialSocketSelfCheck(trace)` must reject:

```js
missing Run 2.51 ids
forbidden surface term count != 0
socket-bound public text elements < 4
shape primitive count < 3
primary surface kind === "square_block_grid"
missing drawRun252 module id
bad control leaking Run 2.51 ids
```

For bad-control trace leakage, keep `run2_51_*_id` fields as empty strings and status fields as explicit failures. Do not populate primary archetype, text socket placement, shape vocabulary, character fit, semantic primitive, or public-copy values from Run 2.51 on the bad arm.

- [ ] **Step 6: Run static test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_52_generator_consumes_run2_51_editorial_socket_pack -q
```

Expected: pass.

- [ ] **Step 7: Commit generator**

```bash
git add scripts/generate_ppt_run2_52_editorial_socket_renderer_arms.mjs tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: add run2.52 editorial socket generator"
```

### Task 3: Generate Run 2.52 Outputs And Record Result Artifacts

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_52_editorial_socket_renderer_rerun_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_52_editorial_socket_renderer_rerun_result.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Generated local outputs under `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/`

- [ ] **Step 1: Run the generator**

Run:

```bash
/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/generate_ppt_run2_52_editorial_socket_renderer_arms.mjs
```

Expected stdout includes:

```json
"run_id": "run2_52_editorial_socket_renderer_four_arms"
"combined_contact_sheet"
"full_skill_series_sheet"
```

- [ ] **Step 2: Verify output files exist**

Run:

```bash
test -f outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-52-four-arm-contact-sheet.png
test -f outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png
test -f outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-52-full-vulca/trace_manifest.json
test -f docs/product/ppt-run2-data-skill-quality/results/run2_52_editorial_socket_renderer_rerun_result.json
test -f docs/product/ppt-run2-data-skill-quality/results/run2_52_editorial_socket_renderer_rerun_result.md
```

- [ ] **Step 3: Update results README**

Add one line near the latest results:

```markdown
- `run2_52_editorial_socket_renderer_rerun_result.json` / `.md`: generated four-arm rerun that consumes Run 2.51 editorial copy, shape text sockets, and renderer archetype workflow gates before native PPT drawing.
```

- [ ] **Step 4: Run recorded output test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_52_records_editorial_socket_renderer_rerun_result -q
```

Expected: pass.

- [ ] **Step 5: Commit result artifacts**

```bash
git add docs/product/ppt-run2-data-skill-quality/results/run2_52_editorial_socket_renderer_rerun_result.json docs/product/ppt-run2-data-skill-quality/results/run2_52_editorial_socket_renderer_rerun_result.md docs/product/ppt-run2-data-skill-quality/results/README.md
git commit -m "feat: record run2.52 editorial socket rerun"
```

### Task 4: Add Run 2.52 To Workflow And HTML Viewer

**Files:**
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add workflow test**

Append:

```python
def test_run2_52_extends_workflow_as_generated_proof_layer() -> None:
    workflow = load_json(PACK / "skill_workflow.json")
    result = load_json(PACK / "results" / "run2_52_editorial_socket_renderer_rerun_result.json")
    workflow_stage_ids = [stage["id"] for stage in workflow["stages"]]
    stage_by_id = {stage["id"]: stage for stage in workflow["stages"]}

    assert result["source_repair_run_id"] == "2.51"
    assert result["source_generated_run_id"] == "2.50"
    assert "generate_run2_52_editorial_socket_renderer_four_arm_rerun" in workflow_stage_ids
    assert workflow_stage_ids.index("apply_run2_51_renderer_archetype_workflow_gates") < workflow_stage_ids.index(
        "generate_run2_52_editorial_socket_renderer_four_arm_rerun"
    )
    assert stage_by_id["generate_run2_52_editorial_socket_renderer_four_arm_rerun"]["order"] == 50
    assert [stage["order"] for stage in workflow["stages"]] == list(range(1, len(workflow["stages"]) + 1))
```

- [ ] **Step 2: Add viewer test**

Append:

```python
def test_ppt_run_html_viewer_generated_latest_run2_52() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    viewer = (
        ROOT
        / "outputs"
        / "019e7d9c-532a-70b3-8892-fa3ae42baef2"
        / "presentations"
        / "ppt-run-viewer.html"
    ).read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "Run 2.52",
            "ppt-run2-52-full-vulca",
            "run2-52-four-arm-contact-sheet.png",
            "run2_52_editorial_socket_renderer_rerun_result.json",
            "run2_51_editorial_shape_text_repair_result.json",
        ],
    )
    assert_contains(
        viewer,
        [
            '"latestRunId": "2.52"',
            "Run 2.52",
            "run2-52-four-arm-contact-sheet.png",
            "ppt-run2-52-prompt-only",
            "ppt-run2-52-run1-5-skill",
            "ppt-run2-52-full-vulca",
            "ppt-run2-52-bad-missing-run2-51-editorial-socket-pack",
            "Run 2.51 is the current data/workflow repair layer",
            "run2_52_editorial_socket_renderer_rerun_result.json",
        ],
    )
```

- [ ] **Step 3: Update `skill_workflow.json`**

Append this stage after `apply_run2_51_renderer_archetype_workflow_gates`:

```json
{
  "id": "generate_run2_52_editorial_socket_renderer_four_arm_rerun",
  "order": 50,
  "layer": "code_generated_ppt",
  "inputs": [
    "run2_51_editorial_copy_memory.json",
    "run2_51_shape_text_socket_memory.json",
    "run2_51_renderer_archetype_workflow_gates.json",
    "results/run2_51_editorial_shape_text_repair_result.json"
  ],
  "outputs": [
    "results/run2_52_editorial_socket_renderer_rerun_result.json",
    "run2-52-four-arm-contact-sheet.png",
    "ppt-run2-52-full-vulca/trace_manifest.json"
  ],
  "gates": [
    "full arm binds Run 2.51 editorial copy ids before public text is drawn",
    "full arm binds Run 2.51 shape text socket ids before semantic surfaces are drawn",
    "bad control fails without Run 2.51 copy/socket/archetype ids",
    "public release remains blocked until visual review, render review, and human approval"
  ]
}
```

- [ ] **Step 4: Update viewer builder**

In `RUN_SPECS`, add:

```python
RunSpec(
    "2.52",
    "Run 2.52",
    "run2-52-four-arm-contact-sheet.png",
    (
        ArmSpec("prompt_only", "Prompt only", "ppt-run2-52-prompt-only", "control"),
        ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-52-run1-5-skill", "baseline"),
        ArmSpec("run2_52_full_editorial_socket_renderer", "Run 2.52 full", "ppt-run2-52-full-vulca", "full"),
        ArmSpec(
            "bad_run2_51_missing_editorial_socket_pack",
            "Bad missing Run 2.51 socket pack",
            "ppt-run2-52-bad-missing-run2-51-editorial-socket-pack",
            "negative",
        ),
    ),
)
```

Also load `run2_52_editorial_socket_renderer_rerun_result.json` in `build_reference_data`, expose its status/path, and add a Data / Skill panel block:

```html
<h3>Run 2.52 generated proof</h3>
<p>Generated four-arm rerun over Run 2.51. The full arm binds editorial copy, shape text socket, and renderer archetype ids before native PPT drawing; the bad control intentionally lacks the Run 2.51 pack.</p>
```

- [ ] **Step 5: Rebuild viewer and run tests**

Run:

```bash
python3 scripts/build_ppt_run_html_viewer.py
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_52_extends_workflow_as_generated_proof_layer tests/test_ppt_run2_data_skill_quality.py::test_ppt_run_html_viewer_generated_latest_run2_52 -q
```

Expected: pass.

- [ ] **Step 6: Commit workflow/viewer**

```bash
git add docs/product/ppt-run2-data-skill-quality/skill_workflow.json scripts/build_ppt_run_html_viewer.py tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: surface run2.52 generated proof in workflow and viewer"
```

### Task 5: Final Verification And Browser Review

**Files:**
- No planned source edits unless verification finds defects.

- [ ] **Step 1: Run full data-quality test file**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
```

Expected: all tests pass. The known local warning about unknown `asyncio_mode` may remain.

- [ ] **Step 2: Run static checks**

Run:

```bash
ruff check scripts/generate_ppt_run2_52_editorial_socket_renderer_arms.mjs scripts/build_ppt_run_html_viewer.py tests/test_ppt_run2_data_skill_quality.py
python3 -m py_compile scripts/build_ppt_run_html_viewer.py
git diff --check
```

Expected: all pass.

- [ ] **Step 3: Rebuild viewer**

Run:

```bash
python3 scripts/build_ppt_run_html_viewer.py
```

Expected stdout includes:

```json
"latest": "2.52"
```

- [ ] **Step 4: Browser inspect**

Open:

```text
http://127.0.0.1:8787/outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html?v=252
```

Verify:

```text
header says latest 2.52 / generated native PPT outputs
Run 2.52 button exists
Four arms view includes Run 2.52 contact sheet
Full series view includes Run 2.52 full arm
Data / Skill includes Run 2.51 repair layer and Run 2.52 generated proof
```

- [ ] **Step 5: Final review and push**

Use a final code-review subagent over the Run 2.52 diff. If approved:

```bash
git status --short --branch
git push
```

Expected: branch pushed cleanly.

---

## Self-Review

Spec coverage:
- Real usecase/database/workflow rule is preserved: Run 2.52 consumes Run 2.51, which itself came from Run 2.49/2.50 and the locked commercial usecase.
- Four-arm experiment is preserved: prompt-only, Run 1.5 baseline, full skill, and bad missing-data control.
- Data-use proof is blocking: full arm trace must contain Run 2.51 ids; bad arm must lack them.
- Visual validation remains honest: public release stays blocked until rendered/browser/human review.

Placeholder scan:
- No `TBD`, `TODO`, or vague “add tests” placeholders remain.

Type consistency:
- The test field names match the Run 2.51 required trace fields plus Run 2.52-specific renderer metrics.
