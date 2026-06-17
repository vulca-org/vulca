# PPT Run 2.9 Generator Rerun Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate and record a new four-arm Run 2.9 PPT rerun that exercises the visual primitive repair modules instead of stopping at data repair.

**Architecture:** Fork the existing Run 2.8 executable-memory generator pattern, preserve arm isolation and native editable PPT generation, and add Run 2.9 visual primitive/module/gate data to the full arm only. The viewer must show Run 2.9 outputs in both four-arm and full-series views.

**Tech Stack:** Node ESM generator using artifact-tool presentation runtime, JSON case-pack inputs, Python pytest contract tests, Python HTML viewer builder, existing PPT validation and layout QA scripts.

---

### Task 1: Generator Contract Test

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [x] **Step 1: Write failing test**

Add `test_run2_9_generator_uses_visual_primitive_modules_and_preserves_boundaries`.

The test must require:
- `scripts/generate_ppt_run2_9_visual_primitive_arms.mjs` exists.
- Arms: `prompt_only`, `run1_5_skill`, `run2_9_full_skill`, `bad_visual_primitive_memory`.
- Full arm allows `run2_9_visual_primitive_repair.json`, `run2_9_executable_visual_modules.json`, `run2_9_visual_gate_matrix.json`.
- Control and baseline forbid all Run 2.9 inputs.
- Bad arm may read `run2_9_visual_primitive_repair.json` but must forbid executable modules and gate matrix.
- Script contains functions `drawRun29EditorialSpread`, `drawRun29LayeredProductSurface`, `drawRun29MotionStoryboard`, `drawRun29ClimaxStage`, `drawRun29TypographicField`.
- Trace fields use actual rendered code modules, not inferred module membership.

- [x] **Step 2: Verify failure**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_9_generator_uses_visual_primitive_modules_and_preserves_boundaries -q
```

Expected: fail because the generator script does not exist.

### Task 2: Generator Implementation

**Files:**
- Create: `scripts/generate_ppt_run2_9_visual_primitive_arms.mjs`

- [x] **Step 1: Fork Run 2.8 generator**

Copy the structure of `scripts/generate_ppt_run2_8_executable_memory_arms.mjs`.

- [x] **Step 2: Add Run 2.9 input boundaries**

Define:
- `RUN2_9_INPUTS`
- `RUN2_9_RESTRICTED_INPUTS`
- `assertArmInputBoundaries`
- readers that allow full arm to load all Run 2.9 data, bad arm to load only repair data, and controls to load none.

- [x] **Step 3: Add Run 2.9 visual modules**

Implement native editable drawing functions:
- `drawRun29EditorialSpread`
- `drawRun29LayeredProductSurface`
- `drawRun29MotionStoryboard`
- `drawRun29ClimaxStage`
- `drawRun29TypographicField`

Each function must call `registerVisualModule(metrics, functionName)` and add non-box-grid native PPT shapes/text.

- [x] **Step 4: Add full-arm slide rendering**

Map slide roles:
- cover: typographic field + editorial spread
- setup: editorial spread + layered product surface
- contrast: editorial spread
- proof: layered product surface + motion storyboard
- climax: climax stage + motion storyboard
- close: typographic field + product surface handoff

- [x] **Step 5: Add trace fields**

Every full-arm slide trace must include:
- `run2_9_visual_primitive_ids`
- `run2_9_visual_module_ids`
- `run2_9_gate_matrix_ids`
- `run2_9_code_module_ids`
- `run2_9_boxiness_failure_probe`
- `run2_9_visual_delta_from_run2_8`

`run2_9_code_module_ids` must be derived from actual registered drawing calls.

### Task 3: Viewer And Result Contracts

**Files:**
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_9_visual_primitive_rerun_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_9_visual_primitive_rerun_result.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`

- [x] **Step 1: Add Run 2.9 viewer specs**

Add four Run 2.9 arms to the HTML viewer:
- `ppt-run2-9-prompt-only`
- `ppt-run2-9-run1-5-skill`
- `ppt-run2-9-full-vulca`
- `ppt-run2-9-bad-visual-primitive-memory`

- [x] **Step 2: Add result tests**

Require result JSON/MD to record generated arms, best internal arm, Run 2.9 visual modules, public blocked release, and HTML viewer path.

### Task 4: Run, Verify, Review, Commit

**Files:**
- All files above

- [x] **Step 1: Run focused tests**

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_9_generator_uses_visual_primitive_modules_and_preserves_boundaries -q
```

- [x] **Step 2: Generate Run 2.9 arms**

```bash
node scripts/generate_ppt_run2_9_visual_primitive_arms.mjs
```

- [x] **Step 3: Regenerate viewer**

```bash
python3 scripts/build_ppt_run_html_viewer.py
```

- [x] **Step 4: Run full verification**

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py tests/test_ppt_case_pack_validator.py
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
git diff --check
```

- [x] **Step 5: Browser and Gemini review**

Open the HTML viewer, inspect Run 2.9 four-arm and full-series views, confirm no console errors, and ask Gemini for an artifact/diff review.

- [x] **Step 6: Commit**

```bash
git add scripts/generate_ppt_run2_9_visual_primitive_arms.mjs scripts/build_ppt_run_html_viewer.py tests/test_ppt_run2_data_skill_quality.py docs/product/ppt-run2-data-skill-quality/results docs/superpowers/plans/2026-06-02-ppt-run2-9-generator-rerun.md
git commit -m "feat: generate PPT run 2.9 visual primitive arms"
```
