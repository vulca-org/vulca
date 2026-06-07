# PPT Run 2.59 Content-Aware Composition Compiler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Run 2.59 data/workflow-only content-aware composition compiler and surface it in the existing PPT run viewer.

**Architecture:** Run 2.59 is a case-pack layer, not a PPT generator. It creates five JSON artifacts plus a result summary, then wires those artifacts into `scripts/build_ppt_run_html_viewer.py` so the Data / Skill tab shows the next compiler layer before any Run 2.60 rerun.

**Tech Stack:** Python tests with pytest, static JSON case-pack artifacts, existing Python HTML viewer builder, generated static HTML output.

---

### Task 1: Add Run 2.59 Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Write failing tests**

Add tests that load these files:

```python
run2_59_contracts = load_json(PACK / "run2_59_content_composition_contracts.json")
run2_59_capacity = load_json(PACK / "run2_59_layout_capacity_model.json")
run2_59_selector = load_json(PACK / "run2_59_content_to_layout_selector.json")
run2_59_policy = load_json(PACK / "run2_59_public_surface_trace_policy.json")
run2_59_gates = load_json(PACK / "run2_59_composition_workflow_gates.json")
run2_59_result = load_json(PACK / "results" / "run2_59_content_aware_composition_compiler_result.json")
```

Assert:

```python
assert run2_59_result["run_id"] == "2.59"
assert run2_59_result["generation_boundary"]["creates_new_ppt_deck"] is False
assert run2_59_result["next_required_action"] == "run2_60_generate_four_arm_ppt_consuming_run2_59_composition_compiler"
assert set(record["role"] for record in run2_59_contracts["content_composition_contracts"]) == EXPECTED_RUN2_51_ROLES
assert set(record["role"] for record in run2_59_selector["content_to_layout_selection_records"]) == EXPECTED_RUN2_51_ROLES
```

- [ ] **Step 2: Run tests and confirm RED**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q -k "run2_59"
```

Expected: failures because Run 2.59 files do not exist.

### Task 2: Add Run 2.59 Case-Pack Artifacts

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/run2_59_content_composition_contracts.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_59_layout_capacity_model.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_59_content_to_layout_selector.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_59_public_surface_trace_policy.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_59_composition_workflow_gates.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_59_content_aware_composition_compiler_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_59_content_aware_composition_compiler_result.md`

- [ ] **Step 1: Implement JSON artifacts**

Use one record per role: `cover`, `setup`, `contrast`, `proof`, `climax`, `close`.

Each content contract must include:

```json
{
  "role": "cover",
  "public_claim": "...",
  "primary_proof_object": "...",
  "evidence_chips": ["...", "..."],
  "trace_only_details": ["...", "..."],
  "speaker_note": "...",
  "max_public_visible_words": 58,
  "required_trace_fields_for_run2_60": ["run2_59_content_contract_id"]
}
```

Each layout capacity record must include:

```json
{
  "layout_module_id": "module_2_15_editorial_cover_field",
  "module_family": "editorial_cover_field",
  "max_title_lines": 2,
  "max_visible_words": 62,
  "max_evidence_chips": 2,
  "primary_object_area_min_pct": 32,
  "forbidden_patterns": ["equal_card_grid", "visible_workflow_gate_rail"]
}
```

- [ ] **Step 2: Run tests and confirm GREEN for artifact tests**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q -k "run2_59"
```

Expected: artifact tests pass, viewer tests still fail until Task 3.

### Task 3: Wire Run 2.59 Into Viewer

**Files:**
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Test: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add viewer test**

Assert both builder script and generated HTML contain:

```python
"Run 2.59 content-aware composition compiler"
"run2_59_content_composition_contracts.json"
"run2_59_layout_capacity_model.json"
"run2_59_content_to_layout_selector.json"
"run2_59_public_surface_trace_policy.json"
"run2_59_composition_workflow_gates.json"
"run2_60_generate_four_arm_ppt_consuming_run2_59_composition_compiler"
'"latestRunId": "2.58"'
```

- [ ] **Step 2: Run viewer test and confirm RED**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q -k "run2_59.*viewer|viewer.*run2_59"
```

Expected: missing viewer terms.

- [ ] **Step 3: Implement viewer references and section**

Read the new JSON artifacts inside `build_reference_data()` and expose:

```python
"run259ResultStatus"
"run259ContentContracts"
"run259LayoutCapacityRecords"
"run259SelectorRecords"
"run259PublicTracePolicy"
"run259WorkflowGates"
"run259NextGeneratedRunContract"
```

Add a `renderData()` section titled:

```text
Next data/workflow repair: Run 2.59 content-aware composition compiler
```

- [ ] **Step 4: Rebuild viewer and run tests**

Run:

```bash
python3 scripts/build_ppt_run_html_viewer.py
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
```

Expected: all tests pass.

### Task 4: Browser Verify and Commit

**Files:**
- Generated: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html`

- [ ] **Step 1: Verify with browser**

Open:

```text
http://127.0.0.1:8787/outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html?v=260
```

Click `Data / Skill` and verify:

```text
Run 2.59 content-aware composition compiler
content contracts
layout capacity model
public slide / trace separation
Run 2.60
latestRunId 2.58
```

- [ ] **Step 2: Commit**

Run:

```bash
git add docs/superpowers/specs/2026-06-07-ppt-run2-59-content-aware-composition-compiler-design.md \
  docs/superpowers/plans/2026-06-07-ppt-run2-59-content-aware-composition-compiler.md \
  docs/product/ppt-run2-data-skill-quality/run2_59_content_composition_contracts.json \
  docs/product/ppt-run2-data-skill-quality/run2_59_layout_capacity_model.json \
  docs/product/ppt-run2-data-skill-quality/run2_59_content_to_layout_selector.json \
  docs/product/ppt-run2-data-skill-quality/run2_59_public_surface_trace_policy.json \
  docs/product/ppt-run2-data-skill-quality/run2_59_composition_workflow_gates.json \
  docs/product/ppt-run2-data-skill-quality/results/run2_59_content_aware_composition_compiler_result.json \
  docs/product/ppt-run2-data-skill-quality/results/run2_59_content_aware_composition_compiler_result.md \
  scripts/build_ppt_run_html_viewer.py \
  tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: add run2.59 composition compiler layer"
git push
```
