# PPT Run 2.11 Data Workflow Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Run 2.11 audit pass that proves the source-to-memory-to-gate-to-trace workflow chain for Runs 2.8, 2.9, and 2.10 without generating a new PPT deck.

**Architecture:** Add tests first for a machine-readable audit artifact, referential integrity, control-boundary evidence, and HTML viewer integration. Then create the audit JSON/Markdown reports, wire the existing viewer to render a `Data/Workflow Audit` tab, rebuild the viewer, and verify that existing run visuals still work.

**Tech Stack:** Python pytest, JSON case-pack artifacts, existing Python HTML viewer builder, existing static output directory, Browser plugin for local viewer validation, gemini-agent for plan/diff/artifact review.

**Gemini plan-critique guardrails:** Do not hardcode the output UUID in reusable audit logic; pass presentation paths through existing builder arguments. Add referential integrity checks so chain IDs cannot silently reference nonexistent source, memory, gate, or trace fields. Treat viewer tests as build/runtime smoke tests, not only string checks.

---

## File Structure

- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_11_data_workflow_audit.json`
  - Machine-readable audit board for Runs 2.7-2.10 source, memory, workflow, trace, and controls.
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_11_data_workflow_audit.md`
  - Human-readable outcome and next action.
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
  - Add Run 2.11 schema, chain, referential integrity, control-boundary, and viewer tests.
- Modify: `scripts/build_ppt_run_html_viewer.py`
  - Load the audit artifact through `build_reference_data()` and add a `Data/Workflow Audit` tab.
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
  - Add latest Run 2.11 audit summary.
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
  - Add Run 2.11 audit-first decision above Run 2.10.
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`
  - Add audit gate checklist and keep public blocked.

---

### Task 1: Add Failing Run 2.11 Audit Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add Run 2.11 constants**

Add near the existing Run 2.10 constants:

```python
EXPECTED_RUN2_11_AUDIT_FIELDS = {
    "schema_version",
    "status",
    "stage_policy",
    "audit_scope",
    "source_inventory",
    "workflow_inventory",
    "chain_records",
    "arm_trace_evidence",
    "negative_control_checks",
    "gate_summary",
    "next_required_action",
}

EXPECTED_RUN2_11_CHAIN_STATUSES = {"pass", "weak", "missing", "blocked"}

EXPECTED_RUN2_11_RUN_IDS = {"2.8", "2.9", "2.10"}

EXPECTED_RUN2_11_CONTROL_ARMS = {
    "prompt_only",
    "run1_5_skill",
    "negative_control",
}
```

- [ ] **Step 2: Add audit artifact schema and chain test**

Add this test near the Run 2.10 tests:

```python
def test_run2_11_data_workflow_audit_artifact_has_required_chains() -> None:
    audit_path = PACK / "results" / "run2_11_data_workflow_audit.json"
    assert audit_path.exists(), "missing Run 2.11 data/workflow audit"

    audit = load_json(audit_path)
    assert EXPECTED_RUN2_11_AUDIT_FIELDS <= set(audit)
    assert audit["status"] == "run2_11_data_workflow_audit_public_blocked"
    assert audit["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert audit["audit_scope"]["creates_new_ppt_deck"] is False
    assert audit["audit_scope"]["primary_quality_target"] == "data_workflow_evidence"

    chains = audit["chain_records"]
    assert chains, "audit must contain source-to-trace chains"
    assert EXPECTED_RUN2_11_RUN_IDS <= {chain["run_id"] for chain in chains}

    for chain in chains:
        assert {
            "chain_id",
            "run_id",
            "layer",
            "source_ids",
            "decomposition_ids",
            "memory_ids",
            "gate_ids",
            "required_code_module_ids",
            "actual_code_module_ids",
            "slide_roles",
            "trace_manifest_paths",
            "control_boundary",
            "status",
            "reason",
            "next_fix",
        } <= set(chain), chain.get("chain_id")
        assert chain["status"] in EXPECTED_RUN2_11_CHAIN_STATUSES
        assert chain["run_id"] in EXPECTED_RUN2_11_RUN_IDS
        if chain["status"] in {"weak", "missing", "blocked"}:
            assert chain["next_fix"], chain["chain_id"]
        if chain["status"] == "pass":
            assert chain["actual_code_module_ids"], chain["chain_id"]
            assert chain["trace_manifest_paths"], chain["chain_id"]

    assert any(chain["run_id"] == "2.8" and chain["status"] == "pass" for chain in chains)
    assert any(chain["run_id"] == "2.9" and chain["status"] == "pass" for chain in chains)
    assert any(chain["run_id"] == "2.10" and chain["status"] == "pass" for chain in chains)
```

- [ ] **Step 3: Add referential integrity test**

Add:

```python
def test_run2_11_audit_references_existing_data_memory_gate_and_trace_fields() -> None:
    audit = load_json(PACK / "results" / "run2_11_data_workflow_audit.json")
    run27_sources = load_json(PACK / "run2_7_multimodal_source_records.json")
    run28_decomp = load_json(PACK / "run2_8_tutorial_decomposition.json")
    run28_memory = load_json(PACK / "run2_8_executable_design_memory.json")
    run28_gate = load_json(PACK / "run2_8_workflow_gate_matrix.json")
    run29_primitives = load_json(PACK / "run2_9_visual_primitive_repair.json")
    run29_modules = load_json(PACK / "run2_9_executable_visual_modules.json")
    run29_gate = load_json(PACK / "run2_9_visual_gate_matrix.json")
    run210_sources = load_json(PACK / "run2_10_visual_system_sources.json")
    run210_memory = load_json(PACK / "run2_10_visual_system_memory.json")
    run210_gate = load_json(PACK / "run2_10_visual_system_gate_matrix.json")

    known_source_ids = {record["id"] for record in run27_sources["records"]}
    known_decomposition_ids = {unit["id"] for unit in run28_decomp["units"]}
    known_memory_ids = {binding["id"] for binding in run28_memory["bindings"]}
    known_gate_ids = {gate["id"] for gate in run28_gate["gates"]}
    known_run29_primitive_ids = {item["id"] for item in run29_primitives["primitive_repairs"]}
    known_run29_module_ids = {item["id"] for item in run29_modules["modules"]}
    known_run29_gate_ids = {gate["id"] for gate in run29_gate["gates"]}
    known_run210_source_ids = {item["id"] for item in run210_sources["sources"]}
    known_run210_memory_ids = {item["visual_system_id"] for item in run210_memory["visual_systems"]}
    known_run210_gate_ids = {gate["id"] for gate in run210_gate["gates"]}

    for chain in audit["chain_records"]:
        if chain["run_id"] == "2.8":
            assert set(chain["source_ids"]) <= known_source_ids
            assert set(chain["decomposition_ids"]) <= known_decomposition_ids
            assert set(chain["memory_ids"]) <= known_memory_ids
            assert set(chain["gate_ids"]) <= known_gate_ids
        elif chain["run_id"] == "2.9":
            assert set(chain["decomposition_ids"]) <= known_run29_primitive_ids
            assert set(chain["memory_ids"]) <= known_run29_module_ids
            assert set(chain["gate_ids"]) <= known_run29_gate_ids
        elif chain["run_id"] == "2.10":
            assert set(chain["source_ids"]) <= known_run210_source_ids
            assert set(chain["memory_ids"]) <= known_run210_memory_ids
            assert set(chain["gate_ids"]) <= known_run210_gate_ids
```

- [ ] **Step 4: Add trace/control-boundary test**

Add:

```python
def test_run2_11_audit_records_trace_evidence_and_control_boundaries() -> None:
    audit = load_json(PACK / "results" / "run2_11_data_workflow_audit.json")

    trace_evidence = audit["arm_trace_evidence"]
    assert {"run2_8_full_skill", "run2_9_full_skill", "run2_10_full_skill"} <= set(trace_evidence)

    assert trace_evidence["run2_8_full_skill"]["trace_origin"] == "actual_native_module_calls"
    assert trace_evidence["run2_9_full_skill"]["trace_origin"] == "actual_native_visual_module_calls"
    assert trace_evidence["run2_10_full_skill"]["trace_origin"] == "actual_native_visual_module_calls"

    controls = audit["negative_control_checks"]
    control_arms = {item["arm_role"] for item in controls}
    assert EXPECTED_RUN2_11_CONTROL_ARMS <= control_arms
    for check in controls:
        assert check["status"] in {"pass", "weak", "missing", "blocked"}
        assert check["forbidden_fields"]
        assert check["observed_boundary"]
```

- [ ] **Step 5: Add viewer integration smoke test**

Add:

```python
def test_run2_11_audit_is_embedded_in_html_viewer(tmp_path: Path) -> None:
    out = tmp_path / "ppt-run-viewer.html"
    completed = subprocess.run(
        [
            "python3",
            "scripts/build_ppt_run_html_viewer.py",
            "--presentations-dir",
            str(ROOT / "outputs" / "019e7d9c-532a-70b3-8892-fa3ae42baef2" / "presentations"),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    body = out.read_text(encoding="utf-8")
    assert "Data/Workflow Audit" in body
    assert "renderAudit" in body
    assert "run2_11_data_workflow_audit_public_blocked" in body
    assert "Source-to-slide chains" in body
```

- [ ] **Step 6: Run tests and verify red**

Run:

```bash
python3 -m pytest \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_11_data_workflow_audit_artifact_has_required_chains \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_11_audit_references_existing_data_memory_gate_and_trace_fields \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_11_audit_records_trace_evidence_and_control_boundaries \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_11_audit_is_embedded_in_html_viewer \
  -q
```

Expected: fail because `run2_11_data_workflow_audit.json` does not exist and the viewer has no audit tab.

---

### Task 2: Create Run 2.11 Audit Artifact

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_11_data_workflow_audit.json`

- [ ] **Step 1: Create the audit JSON**

Create the file with this shape and concrete chains. Use relative trace paths so the audit is not coupled to absolute local paths:

```json
{
  "schema_version": 1,
  "status": "run2_11_data_workflow_audit_public_blocked",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "audit_scope": {
    "creates_new_ppt_deck": false,
    "primary_quality_target": "data_workflow_evidence",
    "audited_runs": ["2.7", "2.8", "2.9", "2.10"],
    "public_release_state": "public_blocked"
  },
  "source_inventory": {
    "run2_7_source_records": 6,
    "run2_8_tutorial_decomposition_units": 6,
    "run2_9_visual_primitives": 5,
    "run2_10_visual_system_sources": 5,
    "run2_10_visual_system_memory_records": 5
  },
  "workflow_inventory": {
    "skill_workflow_stages": 26,
    "run2_8_workflow_gates": 6,
    "run2_9_visual_gates": 6,
    "run2_10_visual_system_gates": 7,
    "data_workflow_chain_gate": "present_in_run2_11_audit_only"
  },
  "chain_records": [
    {
      "chain_id": "chain_2_8_cover_tutorial_to_trace",
      "run_id": "2.8",
      "layer": "tutorial_decomposition_to_executable_memory",
      "source_ids": [
        "mm_2_7_typography_hierarchy_tutorial",
        "mm_2_7_spacing_editorial_grid_tutorial"
      ],
      "decomposition_ids": [
        "decomp_2_8_type_hierarchy_readability_stack",
        "decomp_2_8_source_brand_sanitized_case_evidence"
      ],
      "memory_ids": [
        "binding_type_scale_readability",
        "binding_public_gate_legibility"
      ],
      "gate_ids": ["gate_2_8_cover"],
      "required_code_module_ids": [
        "drawRun28TypeScale",
        "drawRun28WorkflowGate"
      ],
      "actual_code_module_ids": [
        "drawRun28TypeScale",
        "drawRun28WorkflowGate"
      ],
      "slide_roles": ["cover"],
      "trace_manifest_paths": [
        "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-8-full-vulca/trace_manifest.json"
      ],
      "control_boundary": "Run 2.8 fields are present in full arm trace and absent or boundary-empty in controls.",
      "status": "pass",
      "reason": "The cover chain has source records, decomposition units, memory bindings, gate matrix ids, required code bindings, and actual native module trace evidence.",
      "next_fix": "Make the source observations thicker before the next rerun; the chain proves execution more than learning depth."
    },
    {
      "chain_id": "chain_2_9_cover_visual_primitive_to_trace",
      "run_id": "2.9",
      "layer": "visual_primitive_to_executable_visual_module",
      "source_ids": [],
      "decomposition_ids": [
        "primitive_2_9_editorial_spread_composition",
        "primitive_2_9_typographic_field_composition"
      ],
      "memory_ids": [
        "module_2_9_editorial_spread",
        "module_2_9_typographic_field"
      ],
      "gate_ids": ["gate_2_9_cover"],
      "required_code_module_ids": [
        "drawRun29EditorialSpread",
        "drawRun29TypographicField"
      ],
      "actual_code_module_ids": [
        "drawRun29TypographicField",
        "drawRun29EditorialSpread"
      ],
      "slide_roles": ["cover"],
      "trace_manifest_paths": [
        "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-9-full-vulca/trace_manifest.json"
      ],
      "control_boundary": "Run 2.9 actual code modules are full-arm-only; the negative control lacks executable visual module closure.",
      "status": "pass",
      "reason": "The visual primitive repair chain reaches actual native visual module calls in the full arm trace.",
      "next_fix": "Keep this trace truthfulness but add stronger source-to-primitive density before the next rerun."
    },
    {
      "chain_id": "chain_2_10_cover_visual_system_to_trace",
      "run_id": "2.10",
      "layer": "visual_system_memory_to_gate_matrix",
      "source_ids": [
        "vs_source_2_10_editorial_keynote_system",
        "vs_source_2_10_typographic_launch_field"
      ],
      "decomposition_ids": [],
      "memory_ids": [
        "visual_system_editorial_cinema",
        "visual_system_typographic_field"
      ],
      "gate_ids": ["gate_2_10_cover_editorial_field"],
      "required_code_module_ids": [
        "drawRun210EditorialTypeSystem",
        "drawRun210FullBleedVisualField"
      ],
      "actual_code_module_ids": [
        "drawRun210EditorialTypeSystem",
        "drawRun210FullBleedVisualField"
      ],
      "slide_roles": ["cover"],
      "trace_manifest_paths": [
        "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-10-full-vulca/trace_manifest.json"
      ],
      "control_boundary": "Prompt-only, Run 1.5, and bad visual-system memory arms have empty Run 2.10 memory/gate/module fields.",
      "status": "pass",
      "reason": "The visual-system source and memory records connect to gate ids, required modules, and actual native module trace evidence.",
      "next_fix": "The chain proves workflow execution, but Gemini still flags full-series visual sameness; do not rerun until data/workflow weak links are thickened."
    },
    {
      "chain_id": "chain_2_11_multimodal_depth_gap",
      "run_id": "2.10",
      "layer": "multimodal_database_quality",
      "source_ids": [
        "vs_source_2_10_kinetic_climax_sequence",
        "vs_source_2_10_non_rectangular_proof_path"
      ],
      "decomposition_ids": [],
      "memory_ids": [
        "visual_system_kinetic_demo",
        "visual_system_non_rectangular_proof"
      ],
      "gate_ids": [
        "gate_2_10_climax_cinematic",
        "gate_2_10_contrast_non_rectangular_path"
      ],
      "required_code_module_ids": [
        "drawRun210KineticSequence",
        "drawRun210NonRectangularProofPath"
      ],
      "actual_code_module_ids": [
        "drawRun210KineticSequence",
        "drawRun210NonRectangularProofPath"
      ],
      "slide_roles": ["contrast", "climax"],
      "trace_manifest_paths": [
        "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-10-full-vulca/trace_manifest.json"
      ],
      "control_boundary": "Full-arm-only modules are not available to controls.",
      "status": "weak",
      "reason": "The workflow chain is traceable, but the source records are still compact derived observations rather than a thick multimodal tutorial/video case database.",
      "next_fix": "Before the next rerun, add richer tutorial/video decomposition records with timestamp anchors, frame descriptions, transcript-derived claims, and explicit native PPT obligations."
    }
  ],
  "arm_trace_evidence": {
    "run2_8_full_skill": {
      "trace_manifest_path": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-8-full-vulca/trace_manifest.json",
      "trace_origin": "actual_native_module_calls",
      "evidence_fields": [
        "run2_8_code_binding_ids",
        "run2_8_required_code_binding_ids",
        "run2_8_gate_matrix_ids"
      ]
    },
    "run2_9_full_skill": {
      "trace_manifest_path": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-9-full-vulca/trace_manifest.json",
      "trace_origin": "actual_native_visual_module_calls",
      "evidence_fields": [
        "run2_9_code_module_ids",
        "run2_9_required_code_module_ids",
        "run2_9_gate_matrix_ids"
      ]
    },
    "run2_10_full_skill": {
      "trace_manifest_path": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-10-full-vulca/trace_manifest.json",
      "trace_origin": "actual_native_visual_module_calls",
      "evidence_fields": [
        "run2_10_code_module_ids",
        "run2_10_required_code_module_ids",
        "run2_10_gate_matrix_ids"
      ]
    }
  },
  "negative_control_checks": [
    {
      "arm_role": "prompt_only",
      "forbidden_fields": [
        "run2_10_visual_system_memory_ids",
        "run2_10_gate_matrix_ids",
        "run2_10_code_module_ids"
      ],
      "observed_boundary": "Run 2.10 prompt-only trace has empty memory, gate, and code module fields.",
      "status": "pass"
    },
    {
      "arm_role": "run1_5_skill",
      "forbidden_fields": [
        "run2_10_visual_system_memory_ids",
        "run2_10_gate_matrix_ids",
        "run2_10_code_module_ids"
      ],
      "observed_boundary": "Run 1.5 baseline trace has boundary-control Run 2.10 fields.",
      "status": "pass"
    },
    {
      "arm_role": "negative_control",
      "forbidden_fields": [
        "run2_10_visual_system_memory_ids",
        "run2_10_gate_matrix_ids",
        "run2_10_code_module_ids"
      ],
      "observed_boundary": "Bad visual-system memory arm is allowed source awareness but not memory/gate/module closure.",
      "status": "pass"
    }
  ],
  "gate_summary": {
    "data_workflow_chain_gate": "weak_pass_internal_only",
    "proven": [
      "Runs 2.8, 2.9, and 2.10 have full-arm chains that reach actual trace evidence.",
      "Run 2.10 controls preserve boundary isolation for full-arm-only fields."
    ],
    "weak": [
      "Multimodal source records remain compact and should become thicker tutorial/video decompositions before the next rerun.",
      "Viewer evidence is readable but still relies on manually curated audit chain records."
    ],
    "blocked": [
      "public release remains blocked until native render inspection, source-brand sanitization review, finished motion/render support, and human approval."
    ]
  },
  "next_required_action": "Add richer tutorial/video decomposition records and convert them into stricter workflow gates before the next four-arm PPT rerun."
}
```

- [ ] **Step 2: Run audit tests**

Run:

```bash
python3 -m pytest \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_11_data_workflow_audit_artifact_has_required_chains \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_11_audit_references_existing_data_memory_gate_and_trace_fields \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_11_audit_records_trace_evidence_and_control_boundaries \
  -q
```

Expected: these audit tests pass. The viewer test still fails until Task 3.

- [ ] **Step 3: Commit audit artifact**

Run:

```bash
git add docs/product/ppt-run2-data-skill-quality/results/run2_11_data_workflow_audit.json tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: add PPT run 2.11 data workflow audit"
```

---

### Task 3: Add Data/Workflow Audit Viewer Tab

**Files:**
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Load audit JSON in `build_reference_data()`**

Add after the existing Run 2.10 gate matrix load:

```python
    run211_audit = read_json(pack / "results" / "run2_11_data_workflow_audit.json")
```

Add to the returned dict:

```python
        "run211Audit": run211_audit,
```

- [ ] **Step 2: Add tab button**

In the toolbar view rail, after `Data / Skill`, add:

```html
        <button class="seg" data-view="audit">Data/Workflow Audit</button>
```

- [ ] **Step 3: Add compact audit CSS**

Inside the existing `<style>` block near the data classes, add:

```css
    .auditGrid { display: grid; grid-template-columns: minmax(320px, 0.8fr) minmax(560px, 1.4fr); gap: 16px; max-width: 1480px; }
    .auditTable { width: 100%; border-collapse: collapse; font-size: 12px; }
    .auditTable th, .auditTable td { border-top: 1px solid #ddd8cf; padding: 8px; text-align: left; vertical-align: top; }
    .auditTable th { color: var(--muted); font-size: 10px; text-transform: uppercase; }
    .statusPass { color: var(--green); font-weight: 800; }
    .statusWeak { color: #a16600; font-weight: 800; }
    .statusMissing, .statusBlocked { color: var(--accent); font-weight: 800; }
```

Add this responsive rule inside the existing mobile media query:

```css
      .auditGrid { grid-template-columns: minmax(0, 1fr); }
```

- [ ] **Step 4: Add audit render helpers**

Add before `renderData()`:

```javascript
    function auditStatusClass(status) {
      const normalized = safe(status).toLowerCase();
      if (normalized === "pass") return "statusPass";
      if (normalized === "weak") return "statusWeak";
      if (normalized === "missing") return "statusMissing";
      if (normalized === "blocked") return "statusBlocked";
      return "";
    }

    function auditInventoryCard(title, value, note) {
      return `<article class="dataCard">
        <h4>${escapeHtml(title)}</h4>
        <p style="font-size:26px;line-height:1;font-weight:800;color:var(--ink)">${escapeHtml(value)}</p>
        <p>${escapeHtml(note || "")}</p>
      </article>`;
    }

    function renderAudit() {
      const audit = (DATA.references || {}).run211Audit || {};
      const chains = audit.chain_records || [];
      const controls = audit.negative_control_checks || [];
      const sourceInventory = audit.source_inventory || {};
      const workflowInventory = audit.workflow_inventory || {};
      const gate = audit.gate_summary || {};

      if (!audit.status) {
        content.innerHTML = `<div class="empty">No Run 2.11 data/workflow audit artifact found.</div>`;
        return;
      }

      const inventoryCards = [
        auditInventoryCard("Run 2.7 source records", sourceInventory.run2_7_source_records || 0, "Derived multimodal records"),
        auditInventoryCard("Run 2.8 decomposition units", sourceInventory.run2_8_tutorial_decomposition_units || 0, "Tutorial/video to native obligations"),
        auditInventoryCard("Run 2.9 visual primitives", sourceInventory.run2_9_visual_primitives || 0, "Boxiness repair primitives"),
        auditInventoryCard("Run 2.10 visual systems", sourceInventory.run2_10_visual_system_memory_records || 0, "Executable visual-system memory"),
        auditInventoryCard("Workflow stages", workflowInventory.skill_workflow_stages || 0, "Ordered skill workflow"),
        auditInventoryCard("2.10 gates", workflowInventory.run2_10_visual_system_gates || 0, "Visual-system gate matrix")
      ].join("");

      const chainRows = chains.map((chain) => `<tr>
        <td><strong>${escapeHtml(chain.chain_id)}</strong><br><span class="dataLabel">${escapeHtml(chain.layer)}</span></td>
        <td>${escapeHtml(chain.run_id)}</td>
        <td>${chipList(chain.slide_roles)}</td>
        <td>${chipList(chain.required_code_module_ids)}</td>
        <td>${chipList(chain.actual_code_module_ids)}</td>
        <td><span class="${auditStatusClass(chain.status)}">${escapeHtml(chain.status)}</span><br>${escapeHtml(chain.reason)}</td>
        <td>${escapeHtml(chain.next_fix)}</td>
      </tr>`).join("");

      const controlRows = controls.map((check) => `<tr>
        <td>${escapeHtml(check.arm_role)}</td>
        <td>${chipList(check.forbidden_fields)}</td>
        <td>${escapeHtml(check.observed_boundary)}</td>
        <td><span class="${auditStatusClass(check.status)}">${escapeHtml(check.status)}</span></td>
      </tr>`).join("");

      content.innerHTML = `<div class="sectionHeader">
        <div><h2>Data/Workflow Audit</h2><div class="summary">Run 2.11 audits whether data became memory, gates, modules, trace evidence, and control separation.</div></div>
        <span class="pill">${escapeHtml(audit.status)}</span>
      </div>
      <div class="dataStack">
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>2.7-2.10 Progress</h3><p>Inventory of source records, decomposition units, memory, and workflow gates before the next rerun.</p></div><span class="pill">${escapeHtml(audit.stage_policy)}</span></div>
          <div class="dataGrid">${inventoryCards}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Source-to-slide chains</h3><p>Each row shows whether source/decomposition/memory/gate obligations reached actual trace evidence.</p></div><span class="pill">${chains.length} chains</span></div>
          <div style="overflow:auto;padding:14px">
            <table class="auditTable">
              <thead><tr><th>Chain</th><th>Run</th><th>Roles</th><th>Required</th><th>Actual</th><th>Status</th><th>Next fix</th></tr></thead>
              <tbody>${chainRows}</tbody>
            </table>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Control boundaries</h3><p>Controls should not contain full-arm-only data, memory, gate, or module closure.</p></div><span class="pill">${controls.length} controls</span></div>
          <div style="overflow:auto;padding:14px">
            <table class="auditTable">
              <thead><tr><th>Arm</th><th>Forbidden fields</th><th>Observed boundary</th><th>Status</th></tr></thead>
              <tbody>${controlRows}</tbody>
            </table>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Gaps Before Next Rerun</h3><p>${escapeHtml(audit.next_required_action || "")}</p></div><span class="pill">${escapeHtml(gate.data_workflow_chain_gate || "gate unknown")}</span></div>
          <div class="auditGrid" style="padding:14px">
            <article class="dataCard"><h4>Proven</h4>${listBlock(gate.proven || [])}</article>
            <article class="dataCard"><h4>Weak / Blocked</h4>${listBlock([...(gate.weak || []), ...(gate.blocked || [])])}</article>
          </div>
        </section>
      </div>`;
    }
```

- [ ] **Step 5: Route the audit view**

In `render()`, add:

```javascript
      else if (selectedView === "audit") renderAudit();
```

The final routing block should keep existing behavior:

```javascript
      if (selectedView === "series") renderSeries();
      else if (selectedView === "sheet") renderSheets();
      else if (selectedView === "data") renderData();
      else if (selectedView === "audit") renderAudit();
      else renderFour();
```

- [ ] **Step 6: Run viewer test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_11_audit_is_embedded_in_html_viewer -q
```

Expected: pass.

- [ ] **Step 7: Commit viewer integration**

Run:

```bash
git add scripts/build_ppt_run_html_viewer.py tests/test_ppt_run2_data_skill_quality.py
git commit -m "feat: show PPT run 2.11 data workflow audit"
```

---

### Task 4: Add Run 2.11 Result Reports And Delivery Gate Updates

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_11_data_workflow_audit.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`

- [ ] **Step 1: Create result Markdown**

Create `run2_11_data_workflow_audit.md`:

```markdown
# Run 2.11 Data Workflow Audit

Status: data-workflow-audited-public-blocked.

Run 2.11 does not generate a new PPT deck. It audits the existing Run 2.7-2.10 data/workflow chain:

`source -> decomposition -> memory -> gate -> required module -> actual trace -> control boundary`

## What Is Proven

- Run 2.8 has executable tutorial decomposition chains that reach actual native module trace fields.
- Run 2.9 has visual primitive and visual module chains that reach actual native visual module trace fields.
- Run 2.10 has visual-system source, memory, and gate chains that reach actual native visual-system module trace fields.
- Prompt-only, Run 1.5, and negative-control arms preserve full-arm-only field boundaries.

## What Is Weak

- The source and tutorial database is structurally valid but still compact.
- Several records are derived observations rather than thick multimodal decompositions with timestamp, frame-description, transcript-claim, and native-obligation coverage.
- The viewer now makes the chain inspectable, but the audit chain records are still curated and should become more automatically derived in later runs.

## Gate Decision

`data_workflow_chain_gate = weak_pass_internal_only`

The system is ready to thicken data/workflow, not ready for a public release or visual victory claim.

## Next Required Action

Add richer tutorial/video decomposition records and convert them into stricter workflow gates before the next four-arm PPT rerun.
```

- [ ] **Step 2: Update results README**

Add a latest-result entry near the top:

```markdown
## Latest Result: Run 2.11

Run 2.11 is a data/workflow audit pass, not a new PPT rerun. It adds `run2_11_data_workflow_audit.json` and `run2_11_data_workflow_audit.md`, then shows the audit in the HTML viewer.

Current gate: `weak_pass_internal_only_public_blocked`.
```

- [ ] **Step 3: Update comparison report**

Prepend:

```markdown
Run 2.11 is the latest reviewed internal result. It does not generate a new deck. It audits whether Runs 2.7-2.10 actually closed the product loop from source observations to memory, workflow gates, required modules, actual trace evidence, and control boundaries.

The audit result is `weak_pass_internal_only`: the traceable workflow exists for Runs 2.8, 2.9, and 2.10, but the underlying multimodal tutorial/video database is still too compact to justify another visual rerun as a learning-quality claim.
```

- [ ] **Step 4: Update delivery gate**

Add a Run 2.11 audit section near the top:

```markdown
## Run 2.11 Data/Workflow Audit Artifacts

Run 2.11 is audit-only and does not create new PPTX artifacts.

| Artifact | Path | Gate |
| --- | --- | --- |
| Audit JSON | `docs/product/ppt-run2-data-skill-quality/results/run2_11_data_workflow_audit.json` | `weak_pass_internal_only_public_blocked` |
| Audit report | `docs/product/ppt-run2-data-skill-quality/results/run2_11_data_workflow_audit.md` | `weak_pass_internal_only_public_blocked` |
| HTML viewer tab | `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html` | `internal-demo-ok-public-blocked` |
```

Add to the gate checklist:

```markdown
| Run 2.11 data/workflow audit artifact exists | pass |
| Run 2.11 audit chains cover Runs 2.8, 2.9, and 2.10 | pass |
| Run 2.11 control-boundary checks represented | pass |
| Run 2.11 viewer audit tab renders | pass |
```

- [ ] **Step 5: Commit result docs**

Run:

```bash
git add docs/product/ppt-run2-data-skill-quality/results
git commit -m "docs: record PPT run 2.11 data workflow audit"
```

---

### Task 5: Rebuild Viewer And Verify End To End

**Files:**
- Generated local artifact: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html`

- [ ] **Step 1: Rebuild viewer**

Run:

```bash
python3 scripts/build_ppt_run_html_viewer.py \
  --presentations-dir outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations
```

Expected output includes:

```json
{
  "runs": 12,
  "latest": "2.10"
}
```

Run 2.11 is audit-only, so latest generated PPT run remains 2.10.

- [ ] **Step 2: Run full focused verification**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
python3 -m pytest tests/test_pptx_delivery_validator.py -q
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
python3 scripts/build_ppt_run_html_viewer.py \
  --presentations-dir outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations \
  --out /tmp/ppt-run2-11-viewer-smoke.html
git diff --check
```

Expected:

- all focused tests pass;
- validator reports case pack ok;
- viewer smoke build exits 0;
- `git diff --check` exits 0.

- [ ] **Step 3: Use Browser to inspect viewer**

Open:

```text
http://127.0.0.1:8787/outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html
```

Check:

- `Data/Workflow Audit` tab exists.
- It shows `run2_11_data_workflow_audit_public_blocked`.
- `2.7-2.10 Progress` cards render.
- `Source-to-slide chains` table renders.
- `Gaps Before Next Rerun` renders.
- Existing `Four arms`, `Full series`, `Sheets`, and `Data / Skill` tabs still render.
- Browser console has no errors.

- [ ] **Step 4: Run gemini-agent diff review**

Run gemini-agent diff review with this focus:

```text
Review the Run 2.11 audit implementation diff. Check whether it stays audit-only, preserves public-blocked release gates, avoids hardcoded absolute paths, validates source-to-trace chain integrity, and keeps the viewer usable without breaking existing tabs.
```

If Gemini flags actionable defects, fix them before committing.

- [ ] **Step 5: Final commit if needed**

If Task 5 changed tracked files, run:

```bash
git add scripts/build_ppt_run_html_viewer.py docs/product/ppt-run2-data-skill-quality/results tests/test_ppt_run2_data_skill_quality.py
git commit -m "test: verify PPT run 2.11 data workflow audit"
```

Do not commit generated `outputs/` files unless the repository already tracks that exact viewer artifact.

---

## Completion Criteria

Run 2.11 is complete when:

- `run2_11_data_workflow_audit.json` exists and passes schema/integrity tests.
- The audit includes pass chains for Runs 2.8, 2.9, and 2.10.
- The audit includes negative-control boundary checks.
- The HTML viewer includes a working `Data/Workflow Audit` tab.
- Result docs explain proven, weak, missing, blocked, and next required action.
- Public release remains blocked.
- Focused pytest, case-pack validator, viewer smoke build, Browser check, and `git diff --check` pass.
