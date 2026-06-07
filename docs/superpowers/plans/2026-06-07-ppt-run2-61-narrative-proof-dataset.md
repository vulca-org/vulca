# PPT Run 2.61 Narrative Proof Dataset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Run 2.61 data/workflow-only narrative proof dataset that fuses text, proof payloads, visual carriers, source references, and shape text sockets before any Run 2.62 PPT rerun.

**Architecture:** Run 2.61 is a compiler/data layer, not a PPT generator. A Python builder script reads the existing Run 2.8, 2.12, 2.18, 2.15, 2.51, 2.57, and 2.59 artifacts, emits five Run 2.61 JSON artifacts plus result docs, and exposes them in the existing static HTML viewer. CI-visible tests verify the contract without requiring local PPT rendering; local case-pack tests verify deeper artifact consistency and viewer surface.

**Tech Stack:** Python 3.11/3.12, pytest, static JSON case-pack artifacts, existing Python HTML viewer builder, generated static HTML output.

---

## File Structure

- Create: `tests/test_ppt_run2_61_ci_contract.py`
  - CI-visible static contract test for script, artifacts, result docs, and viewer references.
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
  - Local deep validation for artifact schemas, cross-run references, source refs, socket bindings, public proof replacement, and viewer content.
- Create: `scripts/build_ppt_run2_61_narrative_proof_dataset.py`
  - Deterministic builder for Run 2.61 artifacts. It must not generate PPT decks.
- Create: `docs/product/ppt-run2-data-skill-quality/run2_61_narrative_proof_dataset.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_61_story_to_visual_carrier_selector.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_61_text_socket_fusion_contracts.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_61_source_to_public_proof_policy.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_61_narrative_workflow_gates.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_61_narrative_proof_dataset_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_61_narrative_proof_dataset_result.md`
- Modify: `scripts/build_ppt_run_html_viewer.py`
  - Add Run 2.61 references and render a Data / Skill plus Data/Workflow Audit section.
- Generated: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html`
  - Rebuilt viewer. Latest generated run remains 2.60.

---

### Task 1: Add Run 2.61 Tests

**Files:**
- Create: `tests/test_ppt_run2_61_ci_contract.py`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Create the CI-visible static contract test**

Create `tests/test_ppt_run2_61_ci_contract.py`:

```python
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_contains(body: str, terms: list[str]) -> None:
    for term in terms:
        assert term in body, f"missing term: {term!r}"


def test_run2_61_static_contract_is_ci_visible() -> None:
    script = (ROOT / "scripts" / "build_ppt_run2_61_narrative_proof_dataset.py").read_text(
        encoding="utf-8"
    )
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_61_narrative_proof_dataset_result.json")
    result_md = (PACK / "results" / "run2_61_narrative_proof_dataset_result.md").read_text(
        encoding="utf-8"
    )

    assert result["run_id"] == "2.61"
    assert result["source_generated_run_id"] == "2.60"
    assert result["generation_boundary"]["creates_new_ppt_deck"] is False
    assert result["next_required_action"] == "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset"
    assert result["quality_delta"]["target_layer"] == "narrative_proof_dataset_and_socket_fusion"
    assert result["quality_delta"]["roles_with_narrative_proof_records"] == 6
    assert result["quality_delta"]["roles_with_visual_carrier_selection"] == 6
    assert result["quality_delta"]["roles_with_socket_fusion_contracts"] == 6

    assert_contains(
        script,
        [
            "run2_8_tutorial_decomposition.json",
            "run2_12_thick_multimodal_evidence.json",
            "run2_18_multimodal_evidence_expansion.json",
            "run2_15_layout_module_memory.json",
            "run2_51_shape_text_socket_memory.json",
            "run2_57_slide_message_contracts.json",
            "run2_59_content_composition_contracts.json",
            "run2_59_content_to_layout_selector.json",
            "run2_61_narrative_proof_dataset.json",
            "run2_61_story_to_visual_carrier_selector.json",
            "run2_61_text_socket_fusion_contracts.json",
            "run2_61_source_to_public_proof_policy.json",
            "run2_61_narrative_workflow_gates.json",
            "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset",
        ],
    )
    assert_contains(
        viewer,
        [
            'LATEST_RUN_PAYLOAD_HINT = \'"latestRunId": "2.60"\'',
            "Run 2.61 narrative proof dataset",
            "run2_61_narrative_proof_dataset.json",
            "run2_61_story_to_visual_carrier_selector.json",
            "run2_61_text_socket_fusion_contracts.json",
            "run2_61_source_to_public_proof_policy.json",
            "run2_61_narrative_workflow_gates.json",
            "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset",
        ],
    )
    assert_contains(
        result_md,
        [
            "Run 2.61 Narrative Proof Dataset",
            "does not generate a new PPT deck",
            "reader question",
            "visual carrier",
            "text socket fusion",
            "public proof replacement",
            "Do not advance to Run 3.0",
        ],
    )
```

- [ ] **Step 2: Add local deep artifact tests**

Append these constants near the other Run 2 role constants in `tests/test_ppt_run2_data_skill_quality.py`:

```python
EXPECTED_RUN2_61_ROLES = {"cover", "setup", "contrast", "proof", "climax", "close"}
EXPECTED_RUN2_61_CARRIER_TYPES = {
    "product_surface",
    "operating_loop",
    "before_after_delta",
    "workspace_inspection",
    "climax_result_object",
    "release_handoff",
}
EXPECTED_RUN2_61_REQUIRED_COPY_UNITS = {
    "headline",
    "subhead",
    "proof_badges",
    "annotations",
    "state_labels",
    "speaker_note",
}
```

Append this test near the Run 2.59/2.60 tests:

```python
def test_run2_61_records_narrative_proof_dataset() -> None:
    narrative = load_json(PACK / "run2_61_narrative_proof_dataset.json")
    selector = load_json(PACK / "run2_61_story_to_visual_carrier_selector.json")
    fusion = load_json(PACK / "run2_61_text_socket_fusion_contracts.json")
    source_policy = load_json(PACK / "run2_61_source_to_public_proof_policy.json")
    gates = load_json(PACK / "run2_61_narrative_workflow_gates.json")
    result = load_json(PACK / "results" / "run2_61_narrative_proof_dataset_result.json")
    result_md = (PACK / "results" / "run2_61_narrative_proof_dataset_result.md").read_text(
        encoding="utf-8"
    )

    assert narrative["status"] == "run2_61_narrative_proof_dataset_ready_public_blocked"
    assert selector["status"] == "run2_61_story_to_visual_carrier_selector_ready_public_blocked"
    assert fusion["status"] == "run2_61_text_socket_fusion_contracts_ready_public_blocked"
    assert source_policy["status"] == "run2_61_source_to_public_proof_policy_ready_public_blocked"
    assert gates["status"] == "run2_61_narrative_workflow_gates_ready_public_blocked"
    assert result["run_id"] == "2.61"
    assert result["generation_boundary"]["creates_new_ppt_deck"] is False

    narrative_records = narrative["narrative_proof_records"]
    selector_records = selector["story_to_visual_carrier_records"]
    fusion_records = fusion["text_socket_fusion_contracts"]
    gate_records = gates["narrative_workflow_gates"]

    assert {record["role"] for record in narrative_records} == EXPECTED_RUN2_61_ROLES
    assert {record["role"] for record in selector_records} == EXPECTED_RUN2_61_ROLES
    assert {record["role"] for record in fusion_records} == EXPECTED_RUN2_61_ROLES
    assert {record["role"] for record in gate_records} == EXPECTED_RUN2_61_ROLES

    selector_by_role = {record["role"]: record for record in selector_records}
    fusion_by_role = {record["role"]: record for record in fusion_records}
    gate_by_role = {record["role"]: record for record in gate_records}

    for record in narrative_records:
        assert record["narrative_proof_id"].startswith("narrative_proof_2_61_")
        assert record["selected_usecase_id"] == "usecase_design_to_production_platform_launch"
        assert record["reader_question"]
        assert record["required_answer"]
        assert record["business_action"]
        assert record["public_takeaway"]
        assert set(record["copy_units"]) == EXPECTED_RUN2_61_REQUIRED_COPY_UNITS
        assert len(record["source_refs"]) >= 2
        assert len(record["proof_payload"]["secondary_evidence_objects"]) >= 2
        assert record["proof_payload"]["product_mechanism"]
        assert record["proof_payload"]["business_consequence"]
        assert record["public_proof_replacement"]["replacement_type"] in {
            "source_pack_object",
            "inspection_board",
            "before_after_route_break",
            "native_editable_proxy",
            "operating_loop_proxy",
            "release_gate_proxy",
        }
        assert record["density_budget"]["minimum_public_proof_objects"] >= 2
        assert record["density_budget"]["minimum_socket_bound_copy_units"] >= 4
        assert record["density_budget"]["maximum_free_floating_labels"] <= 2
        assert record["bad_control_probe"].startswith("fail_if_")
        assert record["next_rerun_obligation"] == "must_be_consumed_before_run2_62_four_arm_rerun"

        selected = selector_by_role[record["role"]]
        fused = fusion_by_role[record["role"]]
        gate = gate_by_role[record["role"]]
        assert selected["source_narrative_proof_id"] == record["narrative_proof_id"]
        assert selected["selected_layout_module_id"].startswith("module_2_15_")
        assert selected["selected_socket_memory_id"].startswith("shape_text_socket_2_51_")
        assert selected["visual_carrier_type"] in EXPECTED_RUN2_61_CARRIER_TYPES
        assert selected["visual_weight_requirement"]["minimum_primary_carrier_area_pct"] >= 30
        assert fused["source_narrative_proof_id"] == record["narrative_proof_id"]
        assert fused["source_socket_memory_id"] == selected["selected_socket_memory_id"]
        assert {binding["copy_unit_key"] for binding in fused["socket_bindings"]} >= {
            "headline",
            "subhead",
            "proof_badges",
            "annotations",
            "state_labels",
        }
        assert gate["source_narrative_proof_id"] == record["narrative_proof_id"]
        assert gate["next_run_required_trace_fields"] == [
            "run2_61_narrative_proof_id",
            "run2_61_visual_carrier_selector_id",
            "run2_61_text_socket_fusion_contract_id",
            "run2_61_public_proof_replacement_id",
            "run2_61_narrative_workflow_gate_id",
        ]

    assert source_policy["policy_id"] == "run2_61_source_to_public_proof_policy"
    assert "copy_source_slide_or_video_frame" in source_policy["forbidden_source_copying_behaviors"]
    assert "native_editable_proxy_object" in source_policy["allowed_source_abstraction_types"]
    assert result["next_required_action"] == "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset"
    assert "Run 2.61 Narrative Proof Dataset" in result_md
    assert "Do not advance to Run 3.0" in result_md
```

- [ ] **Step 3: Add viewer test terms**

Append this test near the existing viewer tests:

```python
def test_ppt_run_html_viewer_mentions_run2_61_narrative_proof_dataset() -> None:
    viewer_script = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    viewer_html = (
        ROOT
        / "outputs"
        / "019e7d9c-532a-70b3-8892-fa3ae42baef2"
        / "presentations"
        / "ppt-run-viewer.html"
    ).read_text(encoding="utf-8")
    for body in (viewer_script, viewer_html):
        assert_contains(
            body,
            [
                "Run 2.61 narrative proof dataset",
                "Why 2.60 felt thin",
                "Per-slide narrative proof table",
                "Visual carrier selector",
                "Text socket fusion",
                "Public proof replacement",
                "run2_61_narrative_proof_dataset.json",
                "run2_61_story_to_visual_carrier_selector.json",
                "run2_61_text_socket_fusion_contracts.json",
                "run2_61_source_to_public_proof_policy.json",
                "run2_61_narrative_workflow_gates.json",
                "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset",
                '"latestRunId": "2.60"',
            ],
        )
```

- [ ] **Step 4: Run RED**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_61_ci_contract.py tests/test_ppt_run2_data_skill_quality.py -q -k "run2_61"
```

Expected: failures because the Run 2.61 script, artifacts, result docs, and viewer section do not exist yet.

- [ ] **Step 5: Commit the red tests**

Run:

```bash
git add tests/test_ppt_run2_61_ci_contract.py tests/test_ppt_run2_data_skill_quality.py
git commit -m "test: add run2.61 narrative proof contracts"
```

---

### Task 2: Add Run 2.61 Builder And Data Artifacts

**Files:**
- Create: `scripts/build_ppt_run2_61_narrative_proof_dataset.py`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_61_narrative_proof_dataset.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_61_story_to_visual_carrier_selector.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_61_text_socket_fusion_contracts.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_61_source_to_public_proof_policy.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_61_narrative_workflow_gates.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_61_narrative_proof_dataset_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_61_narrative_proof_dataset_result.md`

- [ ] **Step 1: Create the builder script**

Create `scripts/build_ppt_run2_61_narrative_proof_dataset.py` with this structure:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
RESULTS = PACK / "results"
RUN_ID = "2.61"
SELECTED_USECASE_ID = "usecase_design_to_production_platform_launch"
NEXT_ACTION = "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset"
NEXT_OBLIGATION = "must_be_consumed_before_run2_62_four_arm_rerun"
NEXT_TRACE_FIELDS = [
    "run2_61_narrative_proof_id",
    "run2_61_visual_carrier_selector_id",
    "run2_61_text_socket_fusion_contract_id",
    "run2_61_public_proof_replacement_id",
    "run2_61_narrative_workflow_gate_id",
]
SOURCE_INPUTS = {
    "run2_8_tutorial_decomposition": "run2_8_tutorial_decomposition.json",
    "run2_12_thick_multimodal_evidence": "run2_12_thick_multimodal_evidence.json",
    "run2_18_multimodal_evidence_expansion": "run2_18_multimodal_evidence_expansion.json",
    "run2_15_layout_module_memory": "run2_15_layout_module_memory.json",
    "run2_51_shape_text_socket_memory": "run2_51_shape_text_socket_memory.json",
    "run2_57_slide_message_contracts": "run2_57_slide_message_contracts.json",
    "run2_59_content_composition_contracts": "run2_59_content_composition_contracts.json",
    "run2_59_content_to_layout_selector": "run2_59_content_to_layout_selector.json",
}


ROLE_SPECS: list[dict[str, Any]] = [
    {
        "role": "cover",
        "reader_question": "What does Vulca produce, and why is this not an image-generation demo?",
        "required_answer": "Vulca turns a real commercial brief plus selected source data into a code-generated editable PPT deck with traceable proof.",
        "business_action": "Position the product as an evidence-to-editable-PPT workflow.",
        "public_takeaway": "A real brief becomes editable PPT proof.",
        "primary_evidence_object": "input-to-output product surface",
        "secondary_evidence_objects": ["commercial brief card", "source pack object", "generated PPT preview"],
        "product_mechanism": "brief, source pack, memory, code, and PPT output are shown as one native product path",
        "business_consequence": "buyers can judge a repeatable workflow instead of a one-off pretty slide",
        "before_state": "prompt-only deck with weak provenance",
        "after_state": "editable PPT generated from selected case data",
        "visual_carrier_type": "product_surface",
        "selected_layout_module_id": "module_2_15_editorial_cover_field",
        "selected_socket_memory_id": "shape_text_socket_2_51_cover",
        "public_proof_replacement_type": "source_pack_object",
    },
    {
        "role": "setup",
        "reader_question": "How does raw tutorial and business material become design memory before drawing?",
        "required_answer": "The system selects allowed source records, extracts design rules, creates capability memory, and resolves slide contracts before native drawing.",
        "business_action": "Stage the data-to-memory compiler as the product's first operating step.",
        "public_takeaway": "Sources become design decisions before drawing.",
        "primary_evidence_object": "source-to-memory compiler stage",
        "secondary_evidence_objects": ["allowed source pack", "design rule extraction", "message contract"],
        "product_mechanism": "tutorial, case, and multimodal records are reduced into explicit memory and gate objects",
        "business_consequence": "the deck can explain why a visual decision was chosen",
        "before_state": "raw tutorials sit outside the product",
        "after_state": "source rules are compiled into selectable memory",
        "visual_carrier_type": "operating_loop",
        "selected_layout_module_id": "module_2_15_product_theater_stage",
        "selected_socket_memory_id": "shape_text_socket_2_51_setup",
        "public_proof_replacement_type": "native_editable_proxy",
    },
    {
        "role": "contrast",
        "reader_question": "What mechanism separates Vulca from prompt-only or template-style decks?",
        "required_answer": "Vulca binds usecase data, design memory, layout capacity, text sockets, and QA gates before generating editable PPT objects.",
        "business_action": "Show the competitor path breaking at the missing compiler turn.",
        "public_takeaway": "The difference is mechanism, not taste.",
        "primary_evidence_object": "before-after route break",
        "secondary_evidence_objects": ["prompt-only output", "missing compiler turn", "Vulca editable PPT route"],
        "product_mechanism": "the prompt-only path lacks source memory, carrier selection, and socket-bound copy",
        "business_consequence": "the buyer sees a system boundary rather than a subjective style comparison",
        "before_state": "generic deck from a prompt",
        "after_state": "source-bound generated PPT with visible decision route",
        "visual_carrier_type": "before_after_delta",
        "selected_layout_module_id": "module_2_15_before_after_route",
        "selected_socket_memory_id": "shape_text_socket_2_51_contrast",
        "public_proof_replacement_type": "before_after_route_break",
    },
    {
        "role": "proof",
        "reader_question": "How do we know the source data and workflow were actually used?",
        "required_answer": "The output carries narrative proof ids, visual carrier ids, socket fusion ids, proof replacements, and workflow gate ids in trace.",
        "business_action": "Expose a reviewable proof surface without dumping raw trace onto the public slide.",
        "public_takeaway": "Trace becomes inspectable product proof.",
        "primary_evidence_object": "inspection board with compact proof objects",
        "secondary_evidence_objects": ["narrative proof id", "socket fusion id", "public proof replacement"],
        "product_mechanism": "public proof objects point to trace-only records that remain inspectable in the viewer",
        "business_consequence": "reviewers can audit the pipeline without turning the slide into a compliance report",
        "before_state": "raw trace text competes with the main message",
        "after_state": "public proof object links to detailed trace",
        "visual_carrier_type": "workspace_inspection",
        "selected_layout_module_id": "module_2_15_dense_evidence_compression",
        "selected_socket_memory_id": "shape_text_socket_2_51_proof",
        "public_proof_replacement_type": "inspection_board",
    },
    {
        "role": "climax",
        "reader_question": "What is the strongest product moment the viewer should remember?",
        "required_answer": "A source-bound product loop creates an editable PPT preview, with code generation, design memory, and QA evidence orbiting one result object.",
        "business_action": "Make the generated PPT result object own the frame.",
        "public_takeaway": "One generated result owns the product moment.",
        "primary_evidence_object": "editable PPT preview hero object",
        "secondary_evidence_objects": ["design memory route", "code renderer tag", "QA gate tag"],
        "product_mechanism": "the source memory and code path converge into one editable native PPT preview",
        "business_consequence": "the product feels like an operating system for presentation generation",
        "before_state": "separate proof tags and disconnected diagrams",
        "after_state": "one generated result object with attached proof",
        "visual_carrier_type": "climax_result_object",
        "selected_layout_module_id": "module_2_15_metric_reveal_stage",
        "selected_socket_memory_id": "shape_text_socket_2_51_climax",
        "public_proof_replacement_type": "operating_loop_proxy",
    },
    {
        "role": "close",
        "reader_question": "What must happen before the product can claim public release quality?",
        "required_answer": "Run 2.61 prepares the next proof layer; Run 2.62 must consume it, generate a new four-arm comparison, and pass visual, trace, source-boundary, and human review.",
        "business_action": "Close with a release gate and the next concrete rerun.",
        "public_takeaway": "The next proof is generated, not claimed.",
        "primary_evidence_object": "release handoff gate",
        "secondary_evidence_objects": ["Run 2.61 data layer", "Run 2.62 rerun", "human review gate"],
        "product_mechanism": "the narrative proof dataset becomes a required consumer contract for the next PPT generator",
        "business_consequence": "the demo stays credible by showing the remaining gate instead of overclaiming",
        "before_state": "public release claimed from a thin proof",
        "after_state": "next proof waits for generated comparison and review",
        "visual_carrier_type": "release_handoff",
        "selected_layout_module_id": "module_2_15_quiet_release_handoff",
        "selected_socket_memory_id": "shape_text_socket_2_51_close",
        "public_proof_replacement_type": "release_gate_proxy",
    },
]
```

- [ ] **Step 2: Add builder helpers**

Add these helpers below `ROLE_SPECS`:

```python
def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(payload, indent=2, ensure_ascii=False)}\n", encoding="utf-8")


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def source_refs(role: str) -> list[dict[str, str]]:
    return [
        {"source_type": "prior_run", "source_id": "run2_8_tutorial_decomposition", "path": SOURCE_INPUTS["run2_8_tutorial_decomposition"], "role": role},
        {"source_type": "prior_run", "source_id": "run2_12_thick_multimodal_evidence", "path": SOURCE_INPUTS["run2_12_thick_multimodal_evidence"], "role": role},
        {"source_type": "prior_run", "source_id": "run2_18_multimodal_evidence_expansion", "path": SOURCE_INPUTS["run2_18_multimodal_evidence_expansion"], "role": role},
        {"source_type": "prior_run", "source_id": "run2_51_shape_text_socket_memory", "path": SOURCE_INPUTS["run2_51_shape_text_socket_memory"], "role": role},
        {"source_type": "prior_run", "source_id": "run2_57_slide_message_contracts", "path": SOURCE_INPUTS["run2_57_slide_message_contracts"], "role": role},
        {"source_type": "prior_run", "source_id": "run2_59_content_composition_contracts", "path": SOURCE_INPUTS["run2_59_content_composition_contracts"], "role": role},
    ]


def copy_units(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "headline": spec["public_takeaway"],
        "subhead": spec["required_answer"],
        "proof_badges": spec["secondary_evidence_objects"],
        "annotations": [
            spec["product_mechanism"],
            spec["business_consequence"],
        ],
        "state_labels": [
            "before: " + spec["before_state"],
            "after: " + spec["after_state"],
        ],
        "speaker_note": "Explain the business action first, then point to the visual proof object and the viewer trace.",
    }


def narrative_record(spec: dict[str, Any]) -> dict[str, Any]:
    role = spec["role"]
    return {
        "narrative_proof_id": f"narrative_proof_2_61_{role}",
        "role": role,
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_run_ids": ["2.8", "2.12", "2.18", "2.15", "2.51", "2.57", "2.59"],
        "reader_question": spec["reader_question"],
        "required_answer": spec["required_answer"],
        "business_action": spec["business_action"],
        "public_takeaway": spec["public_takeaway"],
        "proof_payload": {
            "primary_evidence_object": spec["primary_evidence_object"],
            "secondary_evidence_objects": spec["secondary_evidence_objects"],
            "product_mechanism": spec["product_mechanism"],
            "business_consequence": spec["business_consequence"],
            "before_state": spec["before_state"],
            "after_state": spec["after_state"],
            "what_the_viewer_should_notice": "the main visual object demonstrates the business action before small labels are read",
        },
        "copy_units": copy_units(spec),
        "source_refs": source_refs(role),
        "trace_only_payload": [
            "full source record inventory",
            "raw tutorial decomposition fields",
            "complete workflow gate details",
            "all prior-run trace ids",
        ],
        "public_proof_replacement": {
            "replacement_id": f"public_proof_replacement_2_61_{role}",
            "replacement_type": spec["public_proof_replacement_type"],
            "replacement_rule": "render a native editable proxy that shows the product action without copying source visuals or leaking raw trace",
        },
        "density_budget": {
            "maximum_public_visible_words": 86,
            "minimum_public_proof_objects": 2,
            "maximum_trace_placeholders": 1,
            "minimum_visual_carrier_area_pct": 30,
            "maximum_free_floating_labels": 2,
            "minimum_socket_bound_copy_units": 4,
        },
        "forbidden_surface_terms": ["run2", "trace manifest", "workflow gate", "schema id", "raw source inventory"],
        "bad_control_probe": f"fail_if_{role}_renders_claim_without_narrative_proof_and_socket_fusion",
        "next_rerun_obligation": NEXT_OBLIGATION,
    }
```

- [ ] **Step 3: Add artifact builders**

Add functions that create each artifact:

```python
def build_narrative_dataset(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_narrative_proof_dataset.v1",
        "run_id": RUN_ID,
        "status": "run2_61_narrative_proof_dataset_ready_public_blocked",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "source_inputs": SOURCE_INPUTS,
        "narrative_proof_records": records,
        "next_required_action": NEXT_ACTION,
    }


def build_selector(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_story_to_visual_carrier_selector.v1",
        "run_id": RUN_ID,
        "status": "run2_61_story_to_visual_carrier_selector_ready_public_blocked",
        "story_to_visual_carrier_records": [
            {
                "selector_id": f"visual_carrier_selector_2_61_{record['role']}",
                "role": record["role"],
                "source_narrative_proof_id": record["narrative_proof_id"],
                "selected_layout_module_id": next(spec["selected_layout_module_id"] for spec in ROLE_SPECS if spec["role"] == record["role"]),
                "selected_socket_memory_id": next(spec["selected_socket_memory_id"] for spec in ROLE_SPECS if spec["role"] == record["role"]),
                "visual_carrier_type": next(spec["visual_carrier_type"] for spec in ROLE_SPECS if spec["role"] == record["role"]),
                "carrier_reason": "selected by business action, proof payload, existing Run 2.15 layout capacity, and Run 2.51 socket availability",
                "visual_weight_requirement": {
                    "minimum_primary_carrier_area_pct": 30,
                    "maximum_equal_card_clusters": 1,
                    "must_show_business_action": True,
                },
                "text_socket_requirement": "all public copy units must bind to Run 2.61 socket fusion contract",
                "fallback_if_over_capacity": "split proof payload to viewer and preserve the dominant visual carrier",
                "bad_control_probe": f"fail_if_{record['role']}_uses_generic_workflow_diagram_without_visual_carrier_selector",
            }
            for record in records
        ],
        "next_required_action": NEXT_ACTION,
    }


def build_fusion(records: list[dict[str, Any]], selectors: list[dict[str, Any]]) -> dict[str, Any]:
    selector_by_role = {selector["role"]: selector for selector in selectors}
    return {
        "schema_version": "ppt_run2_text_socket_fusion_contracts.v1",
        "run_id": RUN_ID,
        "status": "run2_61_text_socket_fusion_contracts_ready_public_blocked",
        "text_socket_fusion_contracts": [
            {
                "fusion_contract_id": f"text_socket_fusion_2_61_{record['role']}",
                "role": record["role"],
                "source_narrative_proof_id": record["narrative_proof_id"],
                "source_socket_memory_id": selector_by_role[record["role"]]["selected_socket_memory_id"],
                "source_copy_units": record["copy_units"],
                "socket_bindings": [
                    {"copy_unit_key": "headline", "socket_id": f"socket_2_61_{record['role']}_headline", "owning_shape_role": "primary_carrier", "character_budget": 64, "max_lines": 2, "minimum_font_size": 24, "placement_rule": "own the first read inside the dominant visual carrier", "failure_status": "fail_missing_headline_socket"},
                    {"copy_unit_key": "subhead", "socket_id": f"socket_2_61_{record['role']}_subhead", "owning_shape_role": "support_surface", "character_budget": 160, "max_lines": 3, "minimum_font_size": 13, "placement_rule": "sit near the carrier without becoming a paragraph block", "failure_status": "fail_missing_subhead_socket"},
                    {"copy_unit_key": "proof_badges", "socket_id": f"socket_2_61_{record['role']}_proof_badges", "owning_shape_role": "proof_object", "character_budget": 120, "max_lines": 3, "minimum_font_size": 10, "placement_rule": "attach proof badges to the evidence object", "failure_status": "fail_missing_proof_badge_socket"},
                    {"copy_unit_key": "annotations", "socket_id": f"socket_2_61_{record['role']}_annotations", "owning_shape_role": "annotation_callout", "character_budget": 180, "max_lines": 4, "minimum_font_size": 9, "placement_rule": "use callout or bracket geometry rather than floating labels", "failure_status": "fail_missing_annotation_socket"},
                    {"copy_unit_key": "state_labels", "socket_id": f"socket_2_61_{record['role']}_state_labels", "owning_shape_role": "state_marker", "character_budget": 96, "max_lines": 2, "minimum_font_size": 9, "placement_rule": "bind before and after labels to route, stage, or gate markers", "failure_status": "fail_missing_state_label_socket"},
                ],
                "fit_rules": {
                    "reject_if_any_required_copy_unit_is_unbound": True,
                    "reject_if_public_words_exceed_budget": True,
                    "reject_if_more_than_two_free_floating_labels": True,
                },
                "overflow_behavior": "move raw detail to viewer and preserve public proof replacement",
                "surface_terms_policy": "public copy must avoid run ids, raw trace names, schema ids, and source brand names",
                "trace_fields_for_next_rerun": NEXT_TRACE_FIELDS,
            }
            for record in records
        ],
        "next_required_action": NEXT_ACTION,
    }
```

Add source policy, gates, result, and markdown:

```python
def build_source_policy() -> dict[str, Any]:
    return {
        "schema_version": "ppt_run2_source_to_public_proof_policy.v1",
        "run_id": RUN_ID,
        "status": "run2_61_source_to_public_proof_policy_ready_public_blocked",
        "policy_id": "run2_61_source_to_public_proof_policy",
        "allowed_source_abstraction_types": [
            "native_editable_proxy_object",
            "source_pack_object",
            "inspection_board",
            "before_after_route_break",
            "operating_loop_proxy",
            "release_gate_proxy",
        ],
        "forbidden_source_copying_behaviors": [
            "copy_source_slide_or_video_frame",
            "copy_source_brand_visual_system",
            "copy_source_transcript_prose",
            "store_copyrighted_frame_as_reusable_asset",
        ],
        "public_replacement_rules": [
            "replace raw source inventory with a compact source pack object",
            "replace full workflow gate list with one pass/fail inspection board",
            "replace raw competitor prose with one before-after route break",
            "replace real screenshots with native editable proxy objects",
        ],
        "trace_only_retention_rules": [
            "keep raw source ids in trace manifests and viewer diagnostics",
            "keep workflow gate details outside public slide text",
            "keep source URLs in attribution fields",
        ],
    }


def build_gates(records: list[dict[str, Any]], selectors: list[dict[str, Any]], fusions: list[dict[str, Any]]) -> dict[str, Any]:
    selector_by_role = {selector["role"]: selector for selector in selectors}
    fusion_by_role = {fusion["role"]: fusion for fusion in fusions}
    return {
        "schema_version": "ppt_run2_narrative_workflow_gates.v1",
        "run_id": RUN_ID,
        "status": "run2_61_narrative_workflow_gates_ready_public_blocked",
        "narrative_workflow_gates": [
            {
                "gate_id": f"gate_2_61_{record['role']}_narrative_proof_fusion",
                "role": record["role"],
                "source_narrative_proof_id": record["narrative_proof_id"],
                "source_visual_carrier_selector_id": selector_by_role[record["role"]]["selector_id"],
                "source_text_socket_fusion_contract_id": fusion_by_role[record["role"]]["fusion_contract_id"],
                "required_checks": [
                    "reader_question_answered",
                    "business_action_present",
                    "proof_payload_specific",
                    "visual_carrier_selected",
                    "required_copy_units_socket_bound",
                    "public_proof_replacement_present",
                    "bad_control_probe_defined",
                ],
                "next_run_required_trace_fields": NEXT_TRACE_FIELDS,
                "bad_control_probe": record["bad_control_probe"],
            }
            for record in records
        ],
        "next_generated_run_contract": {
            "run_id": "2.62",
            "required_trace_fields": NEXT_TRACE_FIELDS,
            "bad_control_arm": "bad_run2_60_without_run2_61_narrative_proof_dataset",
            "full_arm_pass_status": "run2_61_narrative_proof_dataset_consumed_before_native_ppt_drawing",
        },
        "next_required_action": NEXT_ACTION,
    }
```

- [ ] **Step 4: Add `main()` and write files**

Add:

```python
def main() -> None:
    for rel_path in SOURCE_INPUTS.values():
        source_path = PACK / rel_path
        if not source_path.exists():
            raise FileNotFoundError(source_path)

    records = [narrative_record(spec) for spec in ROLE_SPECS]
    narrative = build_narrative_dataset(records)
    selector = build_selector(records)
    fusion = build_fusion(records, selector["story_to_visual_carrier_records"])
    source_policy = build_source_policy()
    gates = build_gates(
        records,
        selector["story_to_visual_carrier_records"],
        fusion["text_socket_fusion_contracts"],
    )
    result = {
        "schema_version": "ppt_run2_narrative_proof_dataset_result.v1",
        "run_id": RUN_ID,
        "status": "run2_61_narrative_proof_dataset_ready_public_blocked",
        "source_generated_run_id": "2.60",
        "selected_usecase_id": SELECTED_USECASE_ID,
        "input_chain": SOURCE_INPUTS,
        "generation_boundary": {
            "creates_new_ppt_deck": False,
            "latest_generated_run_id": "2.60",
            "public_ready": False,
        },
        "quality_delta": {
            "target_layer": "narrative_proof_dataset_and_socket_fusion",
            "fixes_failure_mode": "run2_60_compressed_summary_layer_loses_source_text_visual_thickness",
            "roles_with_narrative_proof_records": len(records),
            "roles_with_visual_carrier_selection": len(selector["story_to_visual_carrier_records"]),
            "roles_with_socket_fusion_contracts": len(fusion["text_socket_fusion_contracts"]),
            "roles_with_public_proof_replacement": len(records),
        },
        "next_required_action": NEXT_ACTION,
    }
    result_md = "\n".join(
        [
            "# Run 2.61 Narrative Proof Dataset",
            "",
            "Run 2.61 is a data/workflow repair layer. It does not generate a new PPT deck.",
            "",
            "It fixes the Run 2.60 failure where the renderer consumed compressed claims but lost source, tutorial, text socket, and visual carrier thickness.",
            "",
            "## Outputs",
            "",
            "- `run2_61_narrative_proof_dataset.json`",
            "- `run2_61_story_to_visual_carrier_selector.json`",
            "- `run2_61_text_socket_fusion_contracts.json`",
            "- `run2_61_source_to_public_proof_policy.json`",
            "- `run2_61_narrative_workflow_gates.json`",
            "",
            "## Required Next Action",
            "",
            f"`{NEXT_ACTION}`",
            "",
            "Do not advance to Run 3.0.",
            "",
        ]
    )

    write_json(PACK / "run2_61_narrative_proof_dataset.json", narrative)
    write_json(PACK / "run2_61_story_to_visual_carrier_selector.json", selector)
    write_json(PACK / "run2_61_text_socket_fusion_contracts.json", fusion)
    write_json(PACK / "run2_61_source_to_public_proof_policy.json", source_policy)
    write_json(PACK / "run2_61_narrative_workflow_gates.json", gates)
    write_json(RESULTS / "run2_61_narrative_proof_dataset_result.json", result)
    write_text(RESULTS / "run2_61_narrative_proof_dataset_result.md", result_md)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run builder and tests**

Run:

```bash
python3 scripts/build_ppt_run2_61_narrative_proof_dataset.py
python3 -m pytest tests/test_ppt_run2_61_ci_contract.py tests/test_ppt_run2_data_skill_quality.py -q -k "run2_61"
```

Expected: artifact tests pass; viewer test still fails until Task 3.

- [ ] **Step 6: Commit data layer**

Run:

```bash
git add scripts/build_ppt_run2_61_narrative_proof_dataset.py \
  docs/product/ppt-run2-data-skill-quality/run2_61_narrative_proof_dataset.json \
  docs/product/ppt-run2-data-skill-quality/run2_61_story_to_visual_carrier_selector.json \
  docs/product/ppt-run2-data-skill-quality/run2_61_text_socket_fusion_contracts.json \
  docs/product/ppt-run2-data-skill-quality/run2_61_source_to_public_proof_policy.json \
  docs/product/ppt-run2-data-skill-quality/run2_61_narrative_workflow_gates.json \
  docs/product/ppt-run2-data-skill-quality/results/run2_61_narrative_proof_dataset_result.json \
  docs/product/ppt-run2-data-skill-quality/results/run2_61_narrative_proof_dataset_result.md
git commit -m "feat: add run2.61 narrative proof dataset"
```

---

### Task 3: Wire Run 2.61 Into The HTML Viewer

**Files:**
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Generated: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html`

- [ ] **Step 1: Read Run 2.61 artifacts in `build_data()`**

In `scripts/build_ppt_run_html_viewer.py`, near the Run 2.59 and Run 2.60 reads, add:

```python
    run261_narrative = read_json(pack / "run2_61_narrative_proof_dataset.json")
    run261_selector = read_json(pack / "run2_61_story_to_visual_carrier_selector.json")
    run261_fusion = read_json(pack / "run2_61_text_socket_fusion_contracts.json")
    run261_source_policy = read_json(pack / "run2_61_source_to_public_proof_policy.json")
    run261_gates = read_json(pack / "run2_61_narrative_workflow_gates.json")
    run261_result = read_json(pack / "results" / "run2_61_narrative_proof_dataset_result.json")
```

- [ ] **Step 2: Add Run 2.61 reference payload keys**

In the `reference_data` dictionary, add:

```python
        "run261ResultStatus": run261_result.get("status", ""),
        "run261Result": run261_result,
        "run261ResultPath": "run2_61_narrative_proof_dataset_result.json",
        "run261NarrativeStatus": run261_narrative.get("status", ""),
        "run261NarrativeRecords": run261_narrative.get("narrative_proof_records", []),
        "run261NarrativePath": "run2_61_narrative_proof_dataset.json",
        "run261SelectorStatus": run261_selector.get("status", ""),
        "run261SelectorRecords": run261_selector.get("story_to_visual_carrier_records", []),
        "run261SelectorPath": "run2_61_story_to_visual_carrier_selector.json",
        "run261FusionStatus": run261_fusion.get("status", ""),
        "run261FusionRecords": run261_fusion.get("text_socket_fusion_contracts", []),
        "run261FusionPath": "run2_61_text_socket_fusion_contracts.json",
        "run261SourcePolicyStatus": run261_source_policy.get("status", ""),
        "run261SourcePolicy": run261_source_policy,
        "run261SourcePolicyPath": "run2_61_source_to_public_proof_policy.json",
        "run261WorkflowGateStatus": run261_gates.get("status", ""),
        "run261WorkflowGates": run261_gates.get("narrative_workflow_gates", []),
        "run261WorkflowGatesPath": "run2_61_narrative_workflow_gates.json",
        "run261NextGeneratedRunContract": run261_gates.get("next_generated_run_contract", {}),
```

- [ ] **Step 3: Add Data / Skill cards**

In the JavaScript `renderData()` function, near the Run 2.60 and Run 2.59 cards, add variables:

```javascript
      const run261Result = refs.run261Result || {};
      const run261Quality = run261Result.quality_delta || {};
      const run261Boundary = run261Result.generation_boundary || {};
      const run261Policy = refs.run261SourcePolicy || {};
      const run261Next = refs.run261NextGeneratedRunContract || {};
      const run261NarrativeCards = (refs.run261NarrativeRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${escapeHtml(record.role || "")}</h4>
          ${detailBlock("Reader question", record.reader_question)}
          ${detailBlock("Required answer", record.required_answer)}
          ${detailBlock("Business action", record.business_action)}
          ${detailBlock("Primary proof", (record.proof_payload || {}).primary_evidence_object)}
          ${detailBlock("Public replacement", (record.public_proof_replacement || {}).replacement_type)}
        </article>
      `).join("");
      const run261SelectorCards = (refs.run261SelectorRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${escapeHtml(record.role || "")}</h4>
          ${detailBlock("Carrier", record.visual_carrier_type)}
          ${detailBlock("Layout module", record.selected_layout_module_id)}
          ${detailBlock("Socket memory", record.selected_socket_memory_id)}
          ${detailBlock("Reason", record.carrier_reason)}
        </article>
      `).join("");
      const run261FusionCards = (refs.run261FusionRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${escapeHtml(record.role || "")}</h4>
          ${detailBlock("Fusion contract", record.fusion_contract_id)}
          ${detailBlock("Source socket memory", record.source_socket_memory_id)}
          ${detailBlock("Socket count", (record.socket_bindings || []).length)}
          ${detailBlock("Overflow", record.overflow_behavior)}
        </article>
      `).join("");
```

Add this HTML section:

```javascript
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.61 narrative proof dataset</h3><p>Why 2.60 felt thin: the generated deck consumed compressed claims, but did not directly bind thick source data, text sockets, visual carriers, and public proof replacements. Run 2.61 repairs that data/workflow layer before any Run 2.62 deck generation.</p></div><span class="pill" title="${escapeHtml(refs.run261ResultStatus || "missing")}">${escapeHtml(refs.run261ResultStatus || "missing")}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Layer boundary</h4>
              ${detailBlock("Result", refs.run261ResultPath || "run2_61_narrative_proof_dataset_result.json")}
              ${detailBlock("Creates new PPT deck", run261Boundary.creates_new_ppt_deck)}
              ${detailBlock("Latest generated run", run261Boundary.latest_generated_run_id || "2.60")}
              ${detailBlock("Target layer", run261Quality.target_layer)}
              ${detailBlock("Next action", run261Result.next_required_action || "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset")}
            </article>
            <article class="dataCard">
              <h4>Artifacts</h4>
              ${detailBlock("Narrative proof", refs.run261NarrativePath || "run2_61_narrative_proof_dataset.json")}
              ${detailBlock("Visual carrier selector", refs.run261SelectorPath || "run2_61_story_to_visual_carrier_selector.json")}
              ${detailBlock("Text socket fusion", refs.run261FusionPath || "run2_61_text_socket_fusion_contracts.json")}
              ${detailBlock("Source policy", refs.run261SourcePolicyPath || "run2_61_source_to_public_proof_policy.json")}
              ${detailBlock("Workflow gates", refs.run261WorkflowGatesPath || "run2_61_narrative_workflow_gates.json")}
            </article>
            <article class="dataCard">
              <h4>Public proof replacement</h4>
              ${detailBlock("Policy id", run261Policy.policy_id)}
              ${detailBlock("Allowed abstractions", run261Policy.allowed_source_abstraction_types)}
              ${detailBlock("Forbidden copying", run261Policy.forbidden_source_copying_behaviors)}
            </article>
            <article class="dataCard">
              <h4>Next Run 2.62 contract</h4>
              ${detailBlock("Run", run261Next.run_id || "2.62")}
              ${detailBlock("Required trace fields", run261Next.required_trace_fields)}
              ${detailBlock("Bad control", run261Next.bad_control_arm || "bad_run2_60_without_run2_61_narrative_proof_dataset")}
              ${detailBlock("Full pass status", run261Next.full_arm_pass_status || "run2_61_narrative_proof_dataset_consumed_before_native_ppt_drawing")}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Per-slide narrative proof table</h4><p>${escapeHtml(refs.run261NarrativeStatus)}. Each role now carries reader question, required answer, business action, proof payload, copy units, source refs, and public proof replacement.</p></div>
          <div class="dataGrid">${run261NarrativeCards}</div>
          <div class="dataBandSubhead"><h4>Visual carrier selector</h4><p>${escapeHtml(refs.run261SelectorStatus)}. Each role selects a visual carrier from business action, proof payload, Run 2.15 layout memory, and Run 2.51 socket availability.</p></div>
          <div class="dataGrid">${run261SelectorCards}</div>
          <div class="dataBandSubhead"><h4>Text socket fusion</h4><p>${escapeHtml(refs.run261FusionStatus)}. Required copy units must bind to sockets before Run 2.62 native PPT drawing.</p></div>
          <div class="dataGrid">${run261FusionCards}</div>
        </section>
```

- [ ] **Step 4: Rebuild viewer and run tests**

Run:

```bash
python3 scripts/build_ppt_run_html_viewer.py
python3 -m pytest tests/test_ppt_run2_61_ci_contract.py tests/test_ppt_run2_data_skill_quality.py -q -k "run2_61"
```

Expected: all Run 2.61 tests pass.

- [ ] **Step 5: Commit viewer wiring**

Run:

```bash
git add scripts/build_ppt_run_html_viewer.py \
  outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html
git commit -m "feat: surface run2.61 narrative proof layer"
```

---

### Task 4: Full Verification

**Files:**
- Test: `tests/test_ppt_run2_61_ci_contract.py`
- Test: `tests/test_ppt_run2_data_skill_quality.py`
- Test: `tests/test_ppt_run2_60_ci_contract.py`
- Generated viewer: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html`

- [ ] **Step 1: Run focused checks**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_61_ci_contract.py tests/test_ppt_run2_60_ci_contract.py -q
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q -k "run2_59 or run2_60 or run2_61"
ruff check scripts/build_ppt_run2_61_narrative_proof_dataset.py tests/test_ppt_run2_61_ci_contract.py
```

Expected: all selected checks pass.

- [ ] **Step 2: Run builder idempotence check**

Run:

```bash
python3 scripts/build_ppt_run2_61_narrative_proof_dataset.py
python3 scripts/build_ppt_run_html_viewer.py
git diff --check
git status --short
```

Expected: `git diff --check` passes. `git status --short` should show only intentional files if builder formatting changed regenerated outputs.

- [ ] **Step 3: Browser verify**

Open:

```text
http://127.0.0.1:8787/outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html?v=261
```

Verify:

- Header still says latest 2.60.
- Data / Skill includes `Run 2.61 narrative proof dataset`.
- Data / Skill includes `Why 2.60 felt thin`.
- Data / Skill includes `Per-slide narrative proof table`.
- Data / Skill includes `Visual carrier selector`.
- Data / Skill includes `Text socket fusion`.
- Data / Skill includes `Public proof replacement`.
- Data/Workflow Audit remains available.

- [ ] **Step 4: Final commit if needed**

If Task 4 changed regenerated files, commit them:

```bash
git add docs/product/ppt-run2-data-skill-quality/run2_61_narrative_proof_dataset.json \
  docs/product/ppt-run2-data-skill-quality/run2_61_story_to_visual_carrier_selector.json \
  docs/product/ppt-run2-data-skill-quality/run2_61_text_socket_fusion_contracts.json \
  docs/product/ppt-run2-data-skill-quality/run2_61_source_to_public_proof_policy.json \
  docs/product/ppt-run2-data-skill-quality/run2_61_narrative_workflow_gates.json \
  docs/product/ppt-run2-data-skill-quality/results/run2_61_narrative_proof_dataset_result.json \
  docs/product/ppt-run2-data-skill-quality/results/run2_61_narrative_proof_dataset_result.md \
  outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run-viewer.html
git commit -m "chore: refresh run2.61 narrative proof artifacts"
```

---

## Self-Review

Spec coverage:

- Narrative proof dataset: Task 2 creates `run2_61_narrative_proof_dataset.json`; Task 1 validates the required fields.
- Visual carrier selector: Task 2 creates `run2_61_story_to_visual_carrier_selector.json`; Task 1 validates Run 2.15 layout module and Run 2.51 socket memory bindings.
- Text socket fusion: Task 2 creates `run2_61_text_socket_fusion_contracts.json`; Task 1 validates required copy unit socket bindings.
- Source to public proof policy: Task 2 creates `run2_61_source_to_public_proof_policy.json`; Task 1 validates allowed abstractions and forbidden source copying.
- Workflow gates: Task 2 creates `run2_61_narrative_workflow_gates.json`; Task 1 validates next Run 2.62 trace fields.
- Viewer exposure: Task 3 wires Run 2.61 into `build_ppt_run_html_viewer.py` and rebuilds the HTML viewer.
- No new PPT deck: Task 1 and Task 2 assert `creates_new_ppt_deck` is false and latest generated run remains 2.60.

Placeholder scan:

- No banned placeholder tokens or incomplete file names.
- All task commands include exact paths.
- All required artifact names are explicit.

Type consistency:

- Artifact keys in tests match builder output keys.
- Viewer reference keys use the `run261` prefix consistently.
- Next-run trace fields match across narrative gates, fusion contracts, and tests.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-07-ppt-run2-61-narrative-proof-dataset.md`. Two execution options:

**1. Subagent-Driven (recommended)** - dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** - execute tasks in this session using executing-plans, batch execution with checkpoints.
