# PPT Run 2.60 Consume Composition Compiler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a Run 2.60 four-arm PPT rerun that consumes the Run 2.59 content-aware composition compiler before native PPT drawing.

**Architecture:** Reuse the established four-arm generator pattern from Run 2.58, but add Run 2.59 input artifacts and trace fields. The full arm must bind content contracts, layout capacity, content-to-layout selection, public/trace separation, and overflow fallback. The bad control must inherit Run 2.58 but fail without the 2.59 compiler. The HTML viewer becomes latest Run 2.60 while still showing 2.59 as a data/workflow layer.

**Tech Stack:** Node ESM generator using `@oai/artifact-tool`, static JSON result artifacts, Python pytest case-pack tests, existing static HTML viewer builder.

---

### Task 1: Tests First

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add tests for Run 2.60 generator**

Assert a new script exists:

```python
script_path = ROOT / "scripts" / "generate_ppt_run2_60_content_aware_composition_arms.mjs"
assert script_path.exists()
```

Assert it references:

```text
run2_59_content_composition_contracts.json
run2_59_layout_capacity_model.json
run2_59_content_to_layout_selector.json
run2_59_public_surface_trace_policy.json
run2_59_composition_workflow_gates.json
drawRun260ContentAwareComposition
bad_run2_58_without_run2_59_composition_compiler
run2_59_composition_compiler_consumed_before_native_ppt_drawing
```

- [ ] **Step 2: Add tests for Run 2.60 result and traces**

Assert result file exists:

```python
PACK / "results" / "run2_60_content_aware_composition_rerun_result.json"
```

Assert output traces exist:

```python
presentations / "ppt-run2-60-full-vulca" / "trace_manifest.json"
presentations / "ppt-run2-60-bad-without-composition-compiler" / "trace_manifest.json"
```

Assert every full-arm slide has:

```text
run2_59_content_contract_id
run2_59_layout_module_id
run2_59_content_burden_level
run2_59_capacity_fit_status
run2_59_public_visible_word_budget
run2_59_trace_only_detail_count
run2_59_public_surface_trace_policy_id
run2_59_composition_gate_id
run2_60_public_trace_split_status
run2_60_over_capacity_fallback_status
run2_60_layout_collision_status
```

- [ ] **Step 3: Add viewer tests**

Assert viewer includes Run 2.60 in `RUN_SPECS`, exposes the four-arm sheet, and has `"latestRunId": "2.60"`.

- [ ] **Step 4: Run RED**

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q -k "run2_60"
```

Expected: fails because script/results/traces/viewer entries are missing.

### Task 2: Generator and Output

**Files:**
- Create: `scripts/generate_ppt_run2_60_content_aware_composition_arms.mjs`
- Create generated outputs under `outputs/<thread>/presentations/ppt-run2-60-*`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_60_content_aware_composition_rerun_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_60_content_aware_composition_rerun_result.md`

- [ ] **Step 1: Implement the generator**

Start from the Run 2.58 generator structure, but change:

```text
RUN_ID = "2.60"
full slug = ppt-run2-60-full-vulca
bad slug = ppt-run2-60-bad-without-composition-compiler
full status = run2_59_composition_compiler_consumed_before_native_ppt_drawing
bad status = fail_missing_run2_59_composition_compiler
```

- [ ] **Step 2: Add full-arm renderers**

Each full-arm slide must consume the selected Run 2.59 module:

```text
cover -> editorial cover field
setup -> product theater stage
contrast -> before/after route
proof -> dense evidence compression
climax -> metric reveal stage
close -> quiet release handoff
```

- [ ] **Step 3: Run generator**

```bash
node --check scripts/generate_ppt_run2_60_content_aware_composition_arms.mjs
node scripts/generate_ppt_run2_60_content_aware_composition_arms.mjs
```

Expected: four PPT outputs, traces, previews, `run2-60-four-arm-contact-sheet.png`, and result JSON/MD.

### Task 3: Viewer

**Files:**
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Generated: `outputs/<thread>/presentations/ppt-run-viewer.html`

- [ ] **Step 1: Add Run 2.60 to `RUN_SPECS`**

Add arms:

```text
ppt-run2-60-prompt-only
ppt-run2-60-run1-5-skill
ppt-run2-60-full-vulca
ppt-run2-60-bad-without-composition-compiler
```

- [ ] **Step 2: Expose Run 2.60 in Data / Skill**

Read `run2_60_content_aware_composition_rerun_result.json` and display result path, full trace, bad trace, and Run 2.59 consumed status.

- [ ] **Step 3: Rebuild and verify**

```bash
python3 scripts/build_ppt_run_html_viewer.py
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
```

Expected: all tests pass.

### Task 4: Browser Review and Commit

**Files:**
- Same as above.

- [ ] **Step 1: Browser verify**

Open:

```text
http://127.0.0.1:8787/outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html?v=260
```

Verify latest Run 2.60 and Data / Skill references.

- [ ] **Step 2: Commit**

```bash
git add .
git commit -m "feat: generate run2.60 composition compiler rerun"
git push
```
