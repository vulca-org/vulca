# PPT Run 2.15 Layout Selector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Run 2.15 data/workflow layer that turns Run 2.14 aesthetic recovery into a reusable layout module selector before the next PPT rerun.

**Architecture:** Add three selector artifacts under the Run 2 case pack, validate them with focused tests, expose them in result docs and the HTML viewer data model, and keep public release blocked. This pass does not generate a new PPT deck.

**Tech Stack:** Python pytest for validation, JSON case-pack artifacts, Markdown result docs, existing `scripts/build_ppt_run_html_viewer.py` for viewer metadata.

---

### Task 1: Add Failing Tests For Run 2.15 Selector Artifacts

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create later: `docs/product/ppt-run2-data-skill-quality/run2_15_layout_selector_sources.json`
- Create later: `docs/product/ppt-run2-data-skill-quality/run2_15_layout_module_memory.json`
- Create later: `docs/product/ppt-run2-data-skill-quality/run2_15_layout_selector_gate_matrix.json`

- [ ] **Step 1: Add the failing test**

Add this test near the other Run 2 data/workflow artifact tests:

```python
def test_run2_15_layout_selector_artifacts_define_reusable_workflow() -> None:
    sources = load_json(PACK / "run2_15_layout_selector_sources.json")
    memory = load_json(PACK / "run2_15_layout_module_memory.json")
    gates = load_json(PACK / "run2_15_layout_selector_gate_matrix.json")

    assert sources["status"] == "run2_15_layout_selector_sources_ready"
    assert memory["status"] == "run2_15_layout_module_memory_ready"
    assert gates["status"] == "run2_15_layout_selector_gate_matrix_ready"

    source_records = sources["records"]
    memory_records = memory["modules"]
    gate_records = gates["gates"]

    assert len(source_records) >= 6
    assert len(memory_records) >= 6
    assert len(gate_records) >= 5

    required_source_fields = {
        "record_id",
        "source_family",
        "derived_from_run_ids",
        "modality_mix",
        "commercial_need",
        "design_observation",
        "layout_selector_obligation",
        "typography_obligation",
        "spacing_obligation",
        "product_theater_obligation",
        "motion_beat_obligation",
        "trace_visibility_obligation",
        "anti_copy_boundary",
    }
    for record in source_records:
        assert required_source_fields <= record.keys()
        assert record["anti_copy_boundary"]
        assert record["layout_selector_obligation"]
        assert not record.get("raw_media_path")
        assert not record.get("copied_source_layout")

    source_ids = {record["record_id"] for record in source_records}
    required_module_families = {
        "editorial_cover_field",
        "product_theater_stage",
        "before_after_route",
        "metric_reveal_stage",
        "quiet_release_handoff",
        "dense_evidence_compression",
    }
    module_families = {module["module_family"] for module in memory_records}
    assert required_module_families <= module_families

    required_memory_fields = {
        "module_id",
        "module_family",
        "slide_roles",
        "source_record_ids",
        "selection_trigger",
        "composition_contract",
        "typography_contract",
        "spacing_contract",
        "asset_contract",
        "trace_visibility_contract",
        "fallback_contract",
        "native_ppt_obligations",
        "forbidden_patterns",
    }
    for module in memory_records:
        assert required_memory_fields <= module.keys()
        assert set(module["source_record_ids"]) <= source_ids
        assert module["slide_roles"]
        assert module["trace_visibility_contract"] == "manifest_viewer_qa_only_for_public_surface"
        assert module["native_ppt_obligations"]

    module_ids = {module["module_id"] for module in memory_records}
    required_gate_ids = {
        "gate_2_15_role_to_module_selection",
        "gate_2_15_text_resilience",
        "gate_2_15_trace_hidden_from_surface",
        "gate_2_15_product_theater_realism",
        "gate_2_15_bad_selector_control_boundary",
    }
    gate_ids = {gate["gate_id"] for gate in gate_records}
    assert required_gate_ids <= gate_ids

    for gate in gate_records:
        assert set(gate["candidate_module_ids"]) <= module_ids
        assert gate["required_selector_inputs"]
        assert gate["selection_rules"]
        assert gate["rejection_rules"]
        assert gate["trace_fields"]
        assert "run2_15_selected_layout_module_ids" in gate["trace_fields"]
        assert gate["text_resilience_probe"]
        assert gate["bad_control_probe"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_15_layout_selector_artifacts_define_reusable_workflow -q
```

Expected: fail with missing `run2_15_layout_selector_sources.json`.

- [ ] **Step 3: Commit the failing test if working in strict TDD mode**

Do not commit if the team prefers red and green in one commit. Otherwise:

```bash
git add tests/test_ppt_run2_data_skill_quality.py
git commit -m "test: add Run 2.15 selector artifact contract"
```

### Task 2: Create Run 2.15 Selector Artifacts

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/run2_15_layout_selector_sources.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_15_layout_module_memory.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_15_layout_selector_gate_matrix.json`
- Test: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Create the source artifact**

Create `run2_15_layout_selector_sources.json` with this shape and at least six records:

```json
{
  "schema_version": 1,
  "status": "run2_15_layout_selector_sources_ready",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "records": [
    {
      "record_id": "selector_2_15_editorial_cover_from_210_214",
      "source_family": "editorial_cover_field",
      "derived_from_run_ids": ["2.10", "2.14"],
      "modality_mix": ["generated_deck_trace", "contact_sheet_review", "gemini_artifact_review"],
      "commercial_need": "make the first slide read as a public product narrative, not an internal workflow report",
      "design_observation": "Run 2.14 improves when the cover uses one dominant typographic field, one proof object, and hidden trace metadata.",
      "layout_selector_obligation": "select an editorial cover module when the slide role is cover and the claim can be compressed to one primary sentence",
      "typography_obligation": "one dominant headline, one short support line, no visible workflow checklist",
      "spacing_obligation": "reserve more than half the slide for headline/proof negative space",
      "product_theater_obligation": "show one native proof object or product-state object, not a dashboard grid",
      "motion_beat_obligation": "cover should imply entry state only; no multi-step visible process rail",
      "trace_visibility_obligation": "record evidence and workflow fields in manifest/viewer/QA only",
      "anti_copy_boundary": "derived from internal run review; no external screenshot, layout, logo, frame, or transcript is copied"
    }
  ]
}
```

Add five more records covering `product_theater_stage`, `before_after_route`, `metric_reveal_stage`, `quiet_release_handoff`, and `dense_evidence_compression`.

- [ ] **Step 2: Create the memory artifact**

Create `run2_15_layout_module_memory.json` with this shape and at least six modules:

```json
{
  "schema_version": 1,
  "status": "run2_15_layout_module_memory_ready",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "modules": [
    {
      "module_id": "module_2_15_editorial_cover_field",
      "module_family": "editorial_cover_field",
      "slide_roles": ["cover"],
      "source_record_ids": ["selector_2_15_editorial_cover_from_210_214"],
      "selection_trigger": "cover slide with one primary narrative claim and one product proof object",
      "composition_contract": "one large typographic field plus one asymmetric native proof object",
      "typography_contract": "headline first-read at thumbnail scale; support copy below 18 words",
      "spacing_contract": "headline/proof field must leave visible breathing room and avoid equal-card grids",
      "asset_contract": "native PPT shapes or sanitized/generated product object only",
      "trace_visibility_contract": "manifest_viewer_qa_only_for_public_surface",
      "fallback_contract": "if headline exceeds two lines, switch to dense_evidence_compression instead of shrinking below legible size",
      "native_ppt_obligations": ["dominant_headline", "single_proof_object", "manifest_trace_only"],
      "forbidden_patterns": ["visible_workflow_gate_rail", "equal_card_grid", "palette_only_change"]
    }
  ]
}
```

Add modules for the remaining five families.

- [ ] **Step 3: Create the gate matrix artifact**

Create `run2_15_layout_selector_gate_matrix.json` with this shape and at least five gates:

```json
{
  "schema_version": 1,
  "status": "run2_15_layout_selector_gate_matrix_ready",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "gates": [
    {
      "gate_id": "gate_2_15_role_to_module_selection",
      "slide_role": "all",
      "candidate_module_ids": [
        "module_2_15_editorial_cover_field",
        "module_2_15_product_theater_stage",
        "module_2_15_before_after_route",
        "module_2_15_metric_reveal_stage",
        "module_2_15_quiet_release_handoff",
        "module_2_15_dense_evidence_compression"
      ],
      "required_selector_inputs": ["slide_role", "content_burden", "commercial_need", "trace_visibility_policy"],
      "selection_rules": ["cover selects editorial_cover_field", "proof selects product_theater_stage", "climax selects metric_reveal_stage"],
      "rejection_rules": ["reject equal-card grid when an editorial module is available", "reject visible workflow machinery on public surface"],
      "trace_fields": ["run2_15_selected_layout_module_ids", "run2_15_selector_gate_ids", "run2_15_trace_visibility_policy"],
      "layout_budget": {"max_visible_workflow_objects": 0, "max_equal_cards": 3},
      "text_resilience_probe": "module declares fallback when headline or support copy exceeds budget",
      "product_surface_probe": "product/demo state must be native/sanitized/generated rather than copied source media",
      "bad_control_probe": "bad selector arm may read data but must not read selector gate matrix"
    }
  ]
}
```

Add the four remaining gates named in the design spec.

- [ ] **Step 4: Run the focused artifact test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_15_layout_selector_artifacts_define_reusable_workflow -q
```

Expected: pass.

- [ ] **Step 5: Commit the artifacts**

```bash
git add docs/product/ppt-run2-data-skill-quality/run2_15_layout_selector_sources.json docs/product/ppt-run2-data-skill-quality/run2_15_layout_module_memory.json docs/product/ppt-run2-data-skill-quality/run2_15_layout_selector_gate_matrix.json tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: add PPT run 2.15 layout selector artifacts"
```

### Task 3: Record Run 2.15 Result And Workflow Status

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_15_layout_selector_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_15_layout_selector_result.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`
- Test: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add the failing result-doc test**

Add this test near the Run 2.14 result test:

```python
def test_run2_15_records_layout_selector_data_workflow_result() -> None:
    result = (PACK / "results" / "run2_15_layout_selector_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_15_layout_selector_result.json")

    assert result_json["status"] == "selector_data_workflow_ready_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["run_id"] == "2.15"
    assert result_json["creates_new_ppt_outputs"] is False
    assert result_json["next_generation_gate"] == "run2_15_selector_gate_matrix_must_drive_next_four_arm_rerun"
    assert_contains(
        json.dumps(result_json["selector_artifacts"]),
        [
            "run2_15_layout_selector_sources.json",
            "run2_15_layout_module_memory.json",
            "run2_15_layout_selector_gate_matrix.json",
        ],
    )
    assert_contains(
        json.dumps(result_json["learning"]),
        [
            "layout module selector",
            "text resilience",
            "trace hidden from public slide surface",
            "product theater realism",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.15",
            "layout module selector",
            "data/workflow-only",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_15_records_layout_selector_data_workflow_result -q
```

Expected: fail with missing result files.

- [ ] **Step 3: Create the JSON result**

Create `run2_15_layout_selector_result.json` with:

```json
{
  "schema_version": 1,
  "status": "selector_data_workflow_ready_public_blocked",
  "public_ready": false,
  "stage_policy": "repeat_same_five_layers_not_run3",
  "run_id": "2.15",
  "creates_new_ppt_outputs": false,
  "selector_artifacts": {
    "sources": "docs/product/ppt-run2-data-skill-quality/run2_15_layout_selector_sources.json",
    "memory": "docs/product/ppt-run2-data-skill-quality/run2_15_layout_module_memory.json",
    "gate_matrix": "docs/product/ppt-run2-data-skill-quality/run2_15_layout_selector_gate_matrix.json"
  },
  "learning": [
    "layout module selector converts Run 2.14 aesthetic recovery into reusable generation policy",
    "text resilience is now a selector gate before native PPT generation",
    "trace hidden from public slide surface remains required",
    "product theater realism is now a gate rather than a hand-coded slide choice"
  ],
  "next_generation_gate": "run2_15_selector_gate_matrix_must_drive_next_four_arm_rerun",
  "not_public_ready_reasons": [
    "Run 2.15 creates no new PPT outputs.",
    "The selector has not yet driven a four-arm generated rerun.",
    "No human release approval has been recorded."
  ]
}
```

- [ ] **Step 4: Create the Markdown result**

Create `run2_15_layout_selector_result.md` with:

```markdown
# Run 2.15 Layout Selector Result

Status: selector data/workflow ready, internal only, public blocked.

Run 2.15 is data/workflow-only. It creates a layout module selector layer before the next PPT rerun.

What changed:

- Added selector source records.
- Added executable layout module memory.
- Added a selector gate matrix for role, text resilience, hidden trace, product theater realism, and bad-control boundaries.

Conclusion: Run 2.15 prepares the next generation pass but does not generate PPT. It remains public blocked. Do not advance to Run 3.0.
```

- [ ] **Step 5: Update summary docs**

Update:

- `docs/product/ppt-run2-data-skill-quality/results/README.md`
- `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`

Each file must state that Run 2.15 is the latest data/workflow layer, creates no new PPT, and gates the next four-arm rerun.

- [ ] **Step 6: Run the result test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_15_records_layout_selector_data_workflow_result -q
```

Expected: pass.

- [ ] **Step 7: Commit result docs**

```bash
git add docs/product/ppt-run2-data-skill-quality/results/run2_15_layout_selector_result.json docs/product/ppt-run2-data-skill-quality/results/run2_15_layout_selector_result.md docs/product/ppt-run2-data-skill-quality/results/README.md docs/product/ppt-run2-data-skill-quality/results/comparison_report.md docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md tests/test_ppt_run2_data_skill_quality.py
git commit -m "docs: record PPT run 2.15 selector result"
```

### Task 4: Expose Run 2.15 In The HTML Viewer Data Area

**Files:**
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Test: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add the failing viewer-data test**

Extend `test_ppt_run_html_viewer_builder_tracks_latest_outputs` or add a focused test:

```python
def test_ppt_run_html_viewer_mentions_run2_15_selector_artifacts() -> None:
    script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")

    assert_contains(
        script,
        [
            "run2_15_layout_selector_sources.json",
            "run2_15_layout_module_memory.json",
            "run2_15_layout_selector_gate_matrix.json",
            "Run 2.15 selector",
            "layout module selector",
        ],
    )
```

- [ ] **Step 2: Run the viewer-data test to verify it fails**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_ppt_run_html_viewer_mentions_run2_15_selector_artifacts -q
```

Expected: fail because the viewer builder does not yet read Run 2.15 artifacts.

- [ ] **Step 3: Update viewer builder reference data**

In `scripts/build_ppt_run_html_viewer.py`, update `build_reference_data()` to read:

```python
run215_sources = read_json(pack / "run2_15_layout_selector_sources.json")
run215_memory = read_json(pack / "run2_15_layout_module_memory.json")
run215_gate_matrix = read_json(pack / "run2_15_layout_selector_gate_matrix.json")
```

Add a compact `selectorLayer` object to the returned data:

```python
"selectorLayer": {
    "label": "Run 2.15 selector",
    "sources": run215_sources,
    "memory": run215_memory,
    "gateMatrix": run215_gate_matrix,
    "summary": "layout module selector before the next four-arm rerun",
},
```

- [ ] **Step 4: Rebuild the local viewer**

Run:

```bash
python3 scripts/build_ppt_run_html_viewer.py --presentations-dir outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations
```

Expected: JSON output with `"html"` and latest generated run still `2.14`, because Run 2.15 creates no PPT deck.

- [ ] **Step 5: Run the viewer-data test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_ppt_run_html_viewer_mentions_run2_15_selector_artifacts -q
```

Expected: pass.

- [ ] **Step 6: Commit viewer update**

```bash
git add scripts/build_ppt_run_html_viewer.py tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: expose PPT run 2.15 selector layer in viewer"
```

### Task 5: Full Verification

**Files:**
- Test: `tests/test_ppt_run2_data_skill_quality.py`
- Test: `tests/test_pptx_delivery_validator.py`
- Validate: `scripts/validate_ppt_case_pack.py`

- [ ] **Step 1: Run full Run 2 case-pack tests**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Run case-pack validator**

Run:

```bash
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
```

Expected:

```text
case pack ok: docs/product/ppt-run2-data-skill-quality
```

- [ ] **Step 3: Run delivery validator tests**

Run:

```bash
python3 -m pytest tests/test_pptx_delivery_validator.py -q
```

Expected: all tests pass.

- [ ] **Step 4: Run diff whitespace check**

Run:

```bash
git diff --check
```

Expected: no output.

- [ ] **Step 5: Final commit if anything remains uncommitted**

Run:

```bash
git status --short
```

If files remain modified:

```bash
git add docs/product/ppt-run2-data-skill-quality tests/test_ppt_run2_data_skill_quality.py scripts/build_ppt_run_html_viewer.py
git commit -m "feat: complete PPT run 2.15 selector data layer"
```

### Execution Notes

- Do not generate `ppt-run2-15-*` arms in this plan.
- Keep `outputs/` uncommitted.
- Keep latest generated deck in the HTML viewer as Run 2.14 unless a later generation plan explicitly creates a Run 2.15 rerun.
- Public release remains blocked.
