# PPT Run 2.53 Product Surface Scene Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Run 2.53 as a data/workflow-only repair layer that turns the Run 2.52 visual critique into product-surface scene memory, business visual evidence memory, and scene renderer workflow gates for a later Run 2.54 generated rerun.

**Architecture:** Run 2.53 must not create PPT output. It reads the Run 2.52 result/trace plus Run 2.51 copy/socket/gate artifacts, emits three role-level memory/gate JSON files, updates `skill_workflow.json`, writes result docs, and surfaces the layer in the HTML viewer. The repair target is the current root cause: Run 2.52 still uses abstract geometry and evidence cards instead of inspectable product/business objects.

**Tech Stack:** Python builder, JSON artifacts under `docs/product/ppt-run2-data-skill-quality/`, pytest contract tests, existing HTML viewer builder.

---

### Task 1: Run 2.53 Failing Contract Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add expected trace fields and artifact tests**

Add tests that require:
- `scripts/build_ppt_run2_53_product_surface_scene_repair.py`
- `run2_53_product_surface_scene_memory.json`
- `run2_53_business_visual_evidence_memory.json`
- `run2_53_scene_renderer_workflow_gates.json`
- `results/run2_53_product_surface_scene_repair_result.json`
- `results/run2_53_product_surface_scene_repair_result.md`

Each artifact must have six role records for `cover`, `setup`, `contrast`, `proof`, `climax`, and `close`; selected usecase must be `usecase_design_to_production_platform_launch`; public release must remain blocked; no PPT deck may be created.

- [ ] **Step 2: Add malformed source test**

Add a test importing the builder and mutating Run 2.52 result so `quality_delta.source_data_status` is wrong. `validate_inputs(...)` must raise `ValueError` mentioning `source_data_status`.

- [ ] **Step 3: Add workflow/viewer tests**

Add tests that require `skill_workflow.json` stages 50-52:
- `compile_run2_53_product_surface_scene_memory`
- `compile_run2_53_business_visual_evidence_memory`
- `apply_run2_53_scene_renderer_workflow_gates`

Add viewer script checks for Run 2.53 as data/workflow-only and assert `"Run 2.53" not in RUN_SPECS`.

- [ ] **Step 4: Verify red**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_53_builds_product_surface_scene_repair_pack tests/test_ppt_run2_data_skill_quality.py::test_run2_53_extends_skill_workflow_without_claiming_generated_deck tests/test_ppt_run2_data_skill_quality.py::test_run2_53_builder_rejects_malformed_run2_52_source tests/test_ppt_run_html_viewer_mentions_run2_53_product_surface_scene_repair -q
```

Expected: fail because builder/artifacts/viewer references do not exist.

- [ ] **Step 5: Commit red tests**

```bash
git add tests/test_ppt_run2_data_skill_quality.py
git commit -m "test: add run2.53 product surface repair contract"
```

### Task 2: Run 2.53 Builder And Artifacts

**Files:**
- Create: `scripts/build_ppt_run2_53_product_surface_scene_repair.py`
- Create by running builder: `docs/product/ppt-run2-data-skill-quality/run2_53_product_surface_scene_memory.json`
- Create by running builder: `docs/product/ppt-run2-data-skill-quality/run2_53_business_visual_evidence_memory.json`
- Create by running builder: `docs/product/ppt-run2-data-skill-quality/run2_53_scene_renderer_workflow_gates.json`
- Create by running builder: `docs/product/ppt-run2-data-skill-quality/results/run2_53_product_surface_scene_repair_result.json`
- Create by running builder: `docs/product/ppt-run2-data-skill-quality/results/run2_53_product_surface_scene_repair_result.md`
- Modify by running builder: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`

- [ ] **Step 1: Implement constants and input validation**

The builder must define:
- `RUN_ID = "2.53"`
- `TARGET_LAYER = "product_surface_scene_and_business_visual_evidence_repair"`
- `NEXT_ACTION = "consume_run2_53_before_run2_54_four_arm_rerun"`
- `NEXT_RERUN_CONTRACT = "must_be_consumed_before_run2_54_four_arm_rerun"`

`validate_inputs(...)` must require:
- Run 2.52 status `run2_52_editorial_socket_renderer_rerun_public_blocked`
- Run 2.52 `quality_delta.source_data_status == "run2_51_editorial_socket_pack_consumed_before_native_ppt_drawing"`
- Run 2.52 `quality_delta.full_slides_with_run2_51_editorial_copy_memory_id == 6`
- Six Run 2.51 copy/socket/gate records.

- [ ] **Step 2: Emit product surface scene memory**

For each role, create a record with:
- `product_surface_scene_id`
- `role`
- `selected_usecase_id`
- `source_run_ids: ["2.51", "2.52"]`
- `scene_object_kind`
- `primary_product_or_business_object`
- `surface_slots` with at least three slots
- `composition_contract`
- `native_ppt_object_strategy`
- `forbidden_visual_patterns` including `generic geometric diagram`, `evidence card only`, `floating annotation card`
- `next_rerun_obligation`

- [ ] **Step 3: Emit business visual evidence memory**

For each role, create a record with:
- `business_visual_evidence_id`
- `required_product_surface_scene_id`
- `required_editorial_copy_memory_id`
- `observable_business_object`
- `reader_question_answered`
- `evidence_binding_contract`
- `minimum_visual_specificity_checks`
- `source_boundary`
- `bad_control_probe`

- [ ] **Step 4: Emit scene renderer workflow gates**

For each role, create a gate with:
- `scene_renderer_gate_id`
- `required_product_surface_scene_id`
- `required_business_visual_evidence_id`
- `required_run2_51_renderer_archetype_gate_id`
- `consumer_contract.next_generated_run == "2.54"`
- `consumer_contract.must_bind_before_native_drawing is True`
- required trace fields for Run 2.54:
  - `run2_53_product_surface_scene_id`
  - `run2_53_business_visual_evidence_id`
  - `run2_53_scene_renderer_gate_id`
  - `run2_53_primary_product_or_business_object`
  - `run2_53_visual_specificity_status`
  - `run2_53_forbidden_generic_geometry_count`

- [ ] **Step 5: Update workflow and result docs**

Append stages 50-52 only if missing. Write result JSON/MD stating Run 2.53 is data/workflow-only, public blocked, and no PPT deck is created.

- [ ] **Step 6: Run builder and tests**

```bash
python3 scripts/build_ppt_run2_53_product_surface_scene_repair.py
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_53_builds_product_surface_scene_repair_pack tests/test_ppt_run2_data_skill_quality.py::test_run2_53_extends_skill_workflow_without_claiming_generated_deck tests/test_ppt_run2_data_skill_quality.py::test_run2_53_builder_rejects_malformed_run2_52_source -q
python3 -m py_compile scripts/build_ppt_run2_53_product_surface_scene_repair.py
```

- [ ] **Step 7: Commit**

```bash
git add scripts/build_ppt_run2_53_product_surface_scene_repair.py docs/product/ppt-run2-data-skill-quality/run2_53_product_surface_scene_memory.json docs/product/ppt-run2-data-skill-quality/run2_53_business_visual_evidence_memory.json docs/product/ppt-run2-data-skill-quality/run2_53_scene_renderer_workflow_gates.json docs/product/ppt-run2-data-skill-quality/results/run2_53_product_surface_scene_repair_result.json docs/product/ppt-run2-data-skill-quality/results/run2_53_product_surface_scene_repair_result.md docs/product/ppt-run2-data-skill-quality/skill_workflow.json
git commit -m "feat: add run2.53 product surface scene repair"
```

### Task 3: Viewer And Results Index

**Files:**
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`

- [ ] **Step 1: Read Run 2.53 artifacts in viewer**

Read the three JSON artifacts and result JSON in `build_reference_data()`, expose them as `run253ProductSurfaceScenes`, `run253BusinessVisualEvidence`, `run253SceneRendererGates`, and `run253Result`.

- [ ] **Step 2: Render Run 2.53 in Data / Skill**

Add a data band near the top after Run 2.52:
- heading `Run 2.53 product-surface scene repair`
- text saying it is data/workflow-only, not a PPT run
- cards for result, output chain, six scene records, six evidence records, and six gates.

- [ ] **Step 3: Update results README**

Make Run 2.53 the latest data/workflow thickness layer. Keep Run 2.52 as latest generated result.

- [ ] **Step 4: Rebuild viewer and verify**

```bash
python3 scripts/build_ppt_run_html_viewer.py --presentations-dir outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations --out outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_ppt_run_html_viewer_mentions_run2_53_product_surface_scene_repair tests/test_ppt_run2_data_skill_quality.py::test_ppt_run_html_viewer_mentions_run2_51_to_run2_52_consumption_chain -q
```

- [ ] **Step 5: Commit**

```bash
git add scripts/build_ppt_run_html_viewer.py docs/product/ppt-run2-data-skill-quality/results/README.md tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: surface run2.53 repair in viewer"
```

### Task 4: Final Verification

**Files:**
- Verify only.

- [ ] **Step 1: Run full relevant tests**

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
python3 -m py_compile scripts/build_ppt_run2_53_product_surface_scene_repair.py scripts/build_ppt_run_html_viewer.py
git diff --check
```

- [ ] **Step 2: Browser check**

Open:

```text
http://127.0.0.1:8787/outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html?v=253
```

Confirm:
- latest generated remains 2.52
- Data / Skill includes Run 2.53
- Run 2.53 does not appear as a generated version button.

- [ ] **Step 3: Commit/push if needed**

If clean and all checks pass:

```bash
git push origin codex/vulca-ppt-case-pack
```
