# PPT Run 2.9 Visual Primitive Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Run 2.9 data repair layer that turns the Run 2.8 boxiness diagnosis into executable visual primitive modules before the next PPT rerun.

**Architecture:** Keep the existing five-layer loop and add three pre-generation artifacts: visual primitive repairs, executable visual modules, and a visual gate matrix. The artifacts must remain derived-only, copyright-safe, native-PPT-oriented, and visible in the HTML viewer.

**Tech Stack:** JSON case-pack files, Python pytest contract tests, Python HTML viewer builder, existing case-pack validator.

---

### Task 1: Contract Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [x] **Step 1: Write failing tests**

Add tests requiring:
- `run2_9_visual_primitive_repair.json`
- `run2_9_executable_visual_modules.json`
- `run2_9_visual_gate_matrix.json`
- Run 2.9 trace fields in `results/trace_manifest_contract.json`
- Run 2.9 stages in `skill_workflow.json`

- [x] **Step 2: Verify failure**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_9_has_visual_primitive_repair_data tests/test_ppt_run2_data_skill_quality.py::test_run2_9_has_executable_visual_modules_and_gate_matrix -q
```

Expected: fails because the Run 2.9 files do not exist.

### Task 2: Run 2.9 Data Artifacts

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/run2_9_visual_primitive_repair.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_9_executable_visual_modules.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_9_visual_gate_matrix.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md`

- [ ] **Step 1: Add derived visual primitive repair data**

Create five repairs:
- editorial spread composition
- product surface depth
- motion storyboard sequence
- climax stage composition
- typographic field composition

Each repair must include source ids, Run 2.8 decomposition ids, visual problem, reference method, extracted primitive, native PPT translation, code module obligation, recipes, forbidden box patterns, boxiness probe, QA probe, anti-copy boundary, and public-blocked release boundary.

- [ ] **Step 2: Add executable visual modules**

Create five modules mapping repairs to code function contracts:
- `drawRun29EditorialSpread`
- `drawRun29LayeredProductSurface`
- `drawRun29MotionStoryboard`
- `drawRun29ClimaxStage`
- `drawRun29TypographicField`

Each module must expose params, layout budget, native editable primitives, composition contract, negative-control failure, QA probe, and release boundary.

- [ ] **Step 3: Add visual gate matrix and trace fields**

Map slide roles to visual primitives and required code modules. Add trace fields:
- `run2_9_visual_primitive_ids`
- `run2_9_visual_module_ids`
- `run2_9_gate_matrix_ids`
- `run2_9_code_module_ids`
- `run2_9_boxiness_failure_probe`
- `run2_9_visual_delta_from_run2_8`

- [ ] **Step 4: Update skill workflow and skill doc**

Insert Run 2.9 stages before `generate_code_first_ppt`:
- `repair_run2_9_visual_primitives`
- `select_run2_9_executable_visual_modules`
- `apply_run2_9_visual_gate_matrix`

### Task 3: HTML Viewer Data Surface

**Files:**
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Extend viewer payload**

Load the three Run 2.9 artifacts and include them under `DATA.references`.

- [ ] **Step 2: Render Run 2.9 in Data / Skill**

Add sections for visual primitive repair, executable visual modules, and visual gate matrix. Keep all dynamic text escaped and keep source URLs restricted to `http` or `https`.

- [ ] **Step 3: Extend viewer contract test**

Require the builder to mention the Run 2.9 files and `Run 2.9 visual primitive repair`.

### Task 4: Verification And Commit

**Files:**
- All modified files above

- [ ] **Step 1: Run focused tests**

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_9_has_visual_primitive_repair_data tests/test_ppt_run2_data_skill_quality.py::test_run2_9_has_executable_visual_modules_and_gate_matrix tests/test_ppt_run2_data_skill_quality.py::test_ppt_run_html_viewer_builder_tracks_run2_8_outputs -q
```

- [ ] **Step 2: Run full relevant tests and validator**

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py tests/test_ppt_case_pack_validator.py
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
python3 scripts/build_ppt_run_html_viewer.py
git diff --check
```

- [ ] **Step 3: Browser check**

Open the existing local viewer and confirm the `Data / Skill` tab shows Run 2.9 sections with no console errors.

- [ ] **Step 4: Commit**

```bash
git add docs/product/ppt-run2-data-skill-quality docs/superpowers/plans/2026-06-02-ppt-run2-9-visual-primitive-repair.md scripts/build_ppt_run_html_viewer.py tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: add PPT run 2.9 visual primitive repair data"
```
