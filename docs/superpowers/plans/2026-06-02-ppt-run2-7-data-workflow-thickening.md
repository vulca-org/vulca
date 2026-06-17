# PPT Run 2.7 Data Workflow Thickening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Run 2.7 as a same-loop thickening pass that makes a real commercial usecase, multimodal tutorial/case records, serialized design memory, strict workflow selection, and code-generated native PPT visibly connected.

**Architecture:** Keep the existing Run 2 case-pack structure and extend it with Run 2.7-specific contracts instead of starting a new product phase. Use tests and validator rules to force data-to-workflow traceability before generating slides, then clone the Run 2.6R arm runner and replace the repair-only logic with data workflow memory selection. Preserve the four-arm experiment and the two required comparison images: four-arm contact sheet and full-skill series sheet.

**Tech Stack:** Python 3 tests with pytest; JSON/Markdown case-pack artifacts; Node ESM generator using bundled `@oai/artifact-tool`; existing PPT layout, trace, contact-sheet, and delivery validators; gemini-agent for plan/artifact/diff review.

---

## Non-Negotiable Product Rule

Every change in this run must improve at least one of these five layers, and the full arm must connect all five:

```text
real commercial usecase
-> multimodal tutorial/case database
-> design memory
-> skill workflow
-> code-generated native PPT
```

Run 2.7 is not Run 3.0. It deepens the same five-layer loop. Changes that only restyle colors, rename runs, or add isolated visual polish fail this plan.

## File Map

- Modify `tests/test_ppt_run2_data_skill_quality.py`: add Run 2.7 data, memory, workflow, generator, and result contract tests.
- Modify `tests/test_ppt_case_pack_validator.py`: add focused validator regression tests for Run 2.7 schema failures.
- Modify `scripts/validate_ppt_case_pack.py`: require and validate Run 2.7 usecase, multimodal source records, design memory, and workflow policy.
- Create `docs/product/ppt-run2-data-skill-quality/run2_7_commercial_usecase.json`: one concrete commercial brief for `AI design-to-production platform launch deck`.
- Create `docs/product/ppt-run2-data-skill-quality/run2_7_multimodal_source_records.json`: derived tutorial/case/video records with modality anchors and anti-copy boundaries.
- Create `docs/product/ppt-run2-data-skill-quality/run2_7_design_memory.json`: serializable typography, spacing, composition, rhythm, anti-pattern, and brand-sanitization memories.
- Create `docs/product/ppt-run2-data-skill-quality/run2_7_workflow_policy.json`: explicit memory-selection and generation gates.
- Modify `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`: insert the Run 2.7 memory-selection stage before `select_visual_production_modules`.
- Modify `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`: require Run 2.7 trace fields.
- Create `scripts/generate_ppt_run2_7_data_workflow_arms.mjs`: four-arm runner for prompt-only, Run 1.5, Run 2.7 full, and bad workflow memory.
- Modify `docs/product/ppt-run2-data-skill-quality/results/README.md`: add Run 2.7 result links.
- Modify `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`: add Run 2.7 row and interpretation.
- Modify `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`: add Run 2.7 QA and public-blocked gate.
- Create `docs/product/ppt-run2-data-skill-quality/results/run2_7_data_workflow_thickening_result.json`: machine-readable outcome.
- Create `docs/product/ppt-run2-data-skill-quality/results/run2_7_data_workflow_thickening_result.md`: human-readable outcome.
- Create `docs/product/ppt-run2-data-skill-quality/results/run2_7_visual_qa_gate.json`: visual aesthetic gate created from Gemini artifact review scores and kept public-blocked unless thresholds pass.

## Task 1: Add Run 2.7 Contract Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add Run 2.7 constants after `EXPECTED_RUN2_6R_TRACE_FIELDS`**

```python
EXPECTED_RUN2_7_USECASE_IDS = {
    "usecase_ai_design_to_production_platform_launch",
}
EXPECTED_RUN2_7_SOURCE_RECORD_IDS = {
    "mm_2_7_design_system_launch_case",
    "mm_2_7_video_climax_single_object",
    "mm_2_7_typography_hierarchy_tutorial",
    "mm_2_7_spacing_editorial_grid_tutorial",
    "mm_2_7_motion_demo_pacing_reference",
    "mm_2_7_product_surface_interaction_reference",
}
EXPECTED_RUN2_7_MEMORY_IDS = {
    "memory_typography_editorial_launch",
    "memory_spacing_climax_proof_grid",
    "memory_composition_single_object_climax",
    "memory_rhythm_six_slide_launch",
    "memory_source_brand_sanitization_v2",
}
EXPECTED_RUN2_7_SOURCE_RECORD_FIELDS = {
    "id",
    "source_id",
    "source_type",
    "allowed_use",
    "anchor",
    "modalities",
    "visual_observation",
    "transcript_or_teaching_claim",
    "extracted_design_rule",
    "slide_roles",
    "native_ppt_implication",
    "anti_copy_boundary",
    "qa_probe",
    "release_boundary",
}
EXPECTED_RUN2_7_MEMORY_FIELDS = {
    "id",
    "source_record_ids",
    "applicable_usecases",
    "applicable_slide_roles",
    "typography_rules",
    "spacing_rules",
    "composition_rules",
    "rhythm_rules",
    "native_ppt_generation_requirements",
    "forbidden_patterns",
    "qa_probes",
    "release_boundary",
}
EXPECTED_RUN2_7_TRACE_FIELDS = {
    "run2_7_usecase_id",
    "run2_7_source_record_ids",
    "run2_7_design_memory_ids",
    "run2_7_workflow_decision_ids",
    "run2_7_delta_from_run2_6r",
    "run2_7_quality_gate",
}
```

- [ ] **Step 2: Add test for the commercial usecase and source records**

Append this test after `test_run2_6r_workflow_and_trace_contract_include_visual_repair`:

```python
def test_run2_7_has_real_usecase_and_multimodal_source_records() -> None:
    usecase = load_json(PACK / "run2_7_commercial_usecase.json")
    source_records = load_json(PACK / "run2_7_multimodal_source_records.json")
    sources = load_json(PACK / "sources.json")
    source_ids = {source["id"] for source in sources["sources"]}

    assert usecase["status"] == "run2_7_commercial_usecase_public_blocked"
    assert usecase["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert EXPECTED_RUN2_7_USECASE_IDS <= {usecase["id"]}
    assert usecase["primary_usecase"] == "AI design-to-production platform launch deck"
    assert len(usecase["six_slide_arc"]) == 6
    assert [slide["rhythm_role"] for slide in usecase["six_slide_arc"]] == [
        "cover",
        "setup",
        "contrast",
        "proof",
        "climax",
        "close",
    ]
    assert_contains(json.dumps(usecase), ["AI product builders", "design engineering leaders", "technical founders"])
    assert_contains(json.dumps(usecase["business_job"]), ["product-system learning", "not one-shot prompting"])
    assert_contains(" ".join(usecase["must_not_show"]), ["copy", "source brand", "full-slide raster"])
    assert_contains(" ".join(usecase["proof_questions"]), ["data", "memory", "workflow", "PPT"])
    assert_contains(usecase["release_boundary"], ["public_blocked"])

    assert source_records["status"] == "run2_7_multimodal_source_records_public_blocked"
    assert source_records["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert source_records["storage_policy"]["raw_media"] == "forbidden"
    assert EXPECTED_RUN2_7_SOURCE_RECORD_IDS <= {record["id"] for record in source_records["records"]}

    covered_modalities = {modality for record in source_records["records"] for modality in record["modalities"]}
    assert {"text", "image_reference", "video", "audio", "transcript", "interaction"} <= covered_modalities

    for record in source_records["records"]:
        assert EXPECTED_RUN2_7_SOURCE_RECORD_FIELDS <= set(record), record["id"]
        assert record["source_id"] in source_ids
        assert record["allowed_use"] == "derived_rules_only"
        assert set(record["slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert_contains(record["native_ppt_implication"], ["native", "editable"])
        assert_contains(record["anti_copy_boundary"], ["do not copy"])
        assert_contains(record["qa_probe"], ["contact sheet"])
        assert_contains(record["release_boundary"], ["public_blocked"])
```

- [ ] **Step 3: Add test for deterministic design memory**

Append this test after the source-record test:

```python
def test_run2_7_has_serializable_design_memory() -> None:
    usecase = load_json(PACK / "run2_7_commercial_usecase.json")
    source_records = load_json(PACK / "run2_7_multimodal_source_records.json")
    memory = load_json(PACK / "run2_7_design_memory.json")
    source_record_ids = {record["id"] for record in source_records["records"]}

    assert memory["status"] == "run2_7_design_memory_public_blocked"
    assert memory["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert memory["memory_type"] == "deterministic_serializable_rules"
    assert EXPECTED_RUN2_7_MEMORY_IDS <= {record["id"] for record in memory["memories"]}

    for record in memory["memories"]:
        assert EXPECTED_RUN2_7_MEMORY_FIELDS <= set(record), record["id"]
        assert set(record["source_record_ids"]) <= source_record_ids
        assert usecase["id"] in record["applicable_usecases"]
        assert set(record["applicable_slide_roles"]) <= EXPECTED_RHYTHM_ROLES
        assert record["typography_rules"]
        assert record["spacing_rules"]
        assert record["composition_rules"]
        assert record["rhythm_rules"]
        assert_contains(" ".join(record["native_ppt_generation_requirements"]), ["native", "editable", "trace"])
        assert_mentions_any(
            " ".join(record["forbidden_patterns"]),
            {"report", "dashboard", "equal card", "source brand", "full-slide raster"},
        )
        assert_contains(" ".join(record["qa_probes"]), ["contact sheet"])
        assert_contains(record["release_boundary"], ["public_blocked"])

    climax_memory = next(
        record for record in memory["memories"] if record["id"] == "memory_composition_single_object_climax"
    )
    assert "climax" in climax_memory["applicable_slide_roles"]
    assert_contains(" ".join(climax_memory["composition_rules"]), ["40-55%", "one native proof object"])
```

- [ ] **Step 4: Add test for workflow selection and trace fields**

Append this test after the memory test:

```python
def test_run2_7_workflow_and_trace_contract_include_memory_selection() -> None:
    usecase = load_json(PACK / "run2_7_commercial_usecase.json")
    source_records = load_json(PACK / "run2_7_multimodal_source_records.json")
    memory = load_json(PACK / "run2_7_design_memory.json")
    policy = load_json(PACK / "run2_7_workflow_policy.json")
    workflow = load_json(PACK / "skill_workflow.json")
    trace_contract = load_json(PACK / "results" / "trace_manifest_contract.json")

    source_record_ids = {record["id"] for record in source_records["records"]}
    memory_ids = {record["id"] for record in memory["memories"]}

    assert policy["status"] == "run2_7_workflow_policy_public_blocked"
    assert policy["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert policy["commercial_usecase_id"] == usecase["id"]
    assert set(policy["selection_chain"]) == {
        "commercial_usecase",
        "source_record_ids",
        "typography_memory_id",
        "spacing_memory_id",
        "composition_memory_id",
        "rhythm_memory_id",
        "brand_sanitization_memory_id",
        "visual_repair_policy_ids",
        "native_ppt_generation",
        "qa_gate",
    }

    for mapping in policy["slide_role_memory_map"]:
        assert mapping["commercial_usecase_id"] == usecase["id"]
        assert set(mapping["source_record_ids"]) <= source_record_ids
        assert set(mapping["design_memory_ids"]) <= memory_ids
        assert EXPECTED_RUN2_7_TRACE_FIELDS <= set(mapping["trace_fields"])
        assert_contains(" ".join(mapping["workflow_gates"]), ["public_blocked", "native", "source-brand"])

    workflow_stage_ids = [stage["id"] for stage in workflow["stages"]]
    assert "select_run2_7_design_memory" in workflow_stage_ids
    assert workflow_stage_ids.index("select_run2_7_design_memory") < workflow_stage_ids.index(
        "select_visual_production_modules"
    )
    workflow_text = json.dumps(workflow)
    assert_contains(
        workflow_text,
        [
            "run2_7_commercial_usecase.json",
            "run2_7_multimodal_source_records.json",
            "run2_7_design_memory.json",
            "run2_7_workflow_policy.json",
        ],
    )
    assert EXPECTED_RUN2_7_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])
```

- [ ] **Step 5: Run the new tests and verify they fail because artifacts do not exist**

Run:

```bash
python3 -m pytest \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_7_has_real_usecase_and_multimodal_source_records \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_7_has_serializable_design_memory \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_7_workflow_and_trace_contract_include_memory_selection \
  -q
```

Expected:

```text
FAILED ... FileNotFoundError: ... run2_7_commercial_usecase.json
```

The first failure may point at `run2_7_multimodal_source_records.json` if the test order changes. That is an acceptable red state.

## Task 2: Create Run 2.7 Data, Memory, Workflow, And Validator Contracts

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/run2_7_commercial_usecase.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_7_multimodal_source_records.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_7_design_memory.json`
- Create: `docs/product/ppt-run2-data-skill-quality/run2_7_workflow_policy.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`
- Modify: `scripts/validate_ppt_case_pack.py`
- Modify: `tests/test_ppt_case_pack_validator.py`

- [ ] **Step 1: Create `run2_7_commercial_usecase.json`**

Use this JSON body:

```json
{
  "schema_version": 1,
  "status": "run2_7_commercial_usecase_public_blocked",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "id": "usecase_ai_design_to_production_platform_launch",
  "primary_usecase": "AI design-to-production platform launch deck",
  "audience": [
    "AI product builders",
    "design engineering leaders",
    "technical founders",
    "public-demo viewers evaluating whether Vulca is more than a normal slide generator"
  ],
  "business_job": [
    "show product-system learning from tutorial and case data",
    "prove the deck is not one-shot prompting",
    "make the selected design memory visible in editable PPT output",
    "preserve public_blocked status until render, trace, source-brand, and human review gates pass"
  ],
  "business_decision": "Should a product team trust Vulca to turn design tutorials and commercial references into reusable presentation-generation workflow?",
  "deck_mission": "Explain Vulca as a code-generated presentation system whose taste improves because usecase, source records, memory, and workflow are selected before generation.",
  "six_slide_arc": [
    {
      "slide_id": "slide_01",
      "rhythm_role": "cover",
      "job": "Name the product category and make code-generated design memory visible immediately.",
      "must_show": "Vulca turns design learning into editable presentation code.",
      "must_not_show": "Do not open with a generic AI deck slogan."
    },
    {
      "slide_id": "slide_02",
      "rhythm_role": "setup",
      "job": "Show why one-shot PPT generation fails commercial teams.",
      "must_show": "Prompt-only generation lacks usecase-to-memory selection.",
      "must_not_show": "Do not use dense diagnostic panels."
    },
    {
      "slide_id": "slide_03",
      "rhythm_role": "contrast",
      "job": "Show before/after difference between direct generation and selected memory.",
      "must_show": "The full arm changes composition, typography, and spacing from the same brief.",
      "must_not_show": "Do not create a dashboard comparison."
    },
    {
      "slide_id": "slide_04",
      "rhythm_role": "proof",
      "job": "Expose the route from source records to memory to workflow to native slide objects.",
      "must_show": "Every visible design move has source record ids and memory ids.",
      "must_not_show": "Do not hide provenance in tiny footer text only."
    },
    {
      "slide_id": "slide_05",
      "rhythm_role": "climax",
      "job": "Deliver one large native transformation object that proves the product claim.",
      "must_show": "One native proof object occupies 40-55% of the canvas.",
      "must_not_show": "Do not use equal cards, full-slide raster, or copied screenshots."
    },
    {
      "slide_id": "slide_06",
      "rhythm_role": "close",
      "job": "End with release gate and product workflow handoff.",
      "must_show": "Internal-demo pass, public-blocked gate, next data/workflow thickening step.",
      "must_not_show": "Do not claim public readiness without human review."
    }
  ],
  "must_show": [
    "real commercial usecase selection",
    "multimodal tutorial and case source records",
    "serialized design memory ids",
    "strict workflow gates",
    "editable native PPT objects"
  ],
  "must_not_show": [
    "copy source brand",
    "copy source deck composition",
    "use full-slide raster as main proof",
    "claim public-ready status",
    "hide data influence from trace"
  ],
  "proof_questions": [
    "Can the contact sheet show that data changed the slide, not only the trace?",
    "Can each full-arm slide name source record ids and memory ids?",
    "Can the workflow explain why the control arms cannot use the same repair?",
    "Can the PPT remain editable native output without source-brand copying?"
  ],
  "release_boundary": "public_blocked until render QA, trace QA, source-brand review, and human approval pass"
}
```

- [ ] **Step 2: Add source ids to `sources.json`**

Append these source records inside the `sources` array. Use `accessed_on` equal to `2026-06-02`.

```json
{
  "id": "run2_7_figma_design_system_launch_reference",
  "title": "Figma design-to-production launch reference",
  "url": "https://www.figma.com/blog/",
  "role": "run2_7_design_to_production_commercial_reference",
  "accessed_on": "2026-06-02",
  "allowed_use": "reference_analysis_only",
  "copyright_note": "Use for public-source structural analysis only; do not copy visuals, screenshots, names, layout, or brand identity."
}
```

```json
{
  "id": "run2_7_slide_design_tutorial_reference",
  "title": "Public slide design tutorial reference",
  "url": "https://www.duarte.com/resources/",
  "role": "run2_7_typography_spacing_tutorial_reference",
  "accessed_on": "2026-06-02",
  "allowed_use": "reference_analysis_only",
  "copyright_note": "Use derived presentation rules only; do not store raw media, full transcript, or copied examples."
}
```

```json
{
  "id": "run2_7_product_demo_video_reference",
  "title": "Public product demo video pacing reference",
  "url": "https://www.youtube.com/",
  "role": "run2_7_video_demo_pacing_reference",
  "accessed_on": "2026-06-02",
  "allowed_use": "reference_analysis_only",
  "copyright_note": "Use timestamp-level derived observations only; do not store video, audio, frames, or full transcript."
}
```

```json
{
  "id": "run2_7_presentation_hierarchy_reference",
  "title": "Public visual hierarchy teaching reference",
  "url": "https://www.presentationzen.com/",
  "role": "run2_7_visual_hierarchy_reference",
  "accessed_on": "2026-06-02",
  "allowed_use": "reference_analysis_only",
  "copyright_note": "Use for derived hierarchy rules only; do not copy layouts, images, text, or brand identity."
}
```

- [ ] **Step 3: Create `run2_7_multimodal_source_records.json`**

Use this JSON body:

```json
{
  "schema_version": 1,
  "status": "run2_7_multimodal_source_records_public_blocked",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "storage_policy": {
    "default": "derived_observations_only",
    "raw_media": "forbidden",
    "copyright_boundary": "Store source metadata, anchors, derived observations, and design rules only; do not store copied media, full transcripts, screenshots, or source layouts."
  },
  "records": [
    {
      "id": "mm_2_7_design_system_launch_case",
      "source_id": "run2_7_figma_design_system_launch_reference",
      "source_type": "visual case article",
      "allowed_use": "derived_rules_only",
      "anchor": "public article section: design-to-production narrative",
      "modalities": ["text", "image_reference", "interaction"],
      "visual_observation": "A product launch story becomes clearer when the product surface is treated as the proof object rather than as a decorative screenshot.",
      "transcript_or_teaching_claim": "Launch material should connect audience job, product system, and decision handoff.",
      "extracted_design_rule": "For a design-to-production launch deck, connect brief, memory, workflow, and native output as one visible system route.",
      "slide_roles": ["cover", "setup", "proof", "close"],
      "native_ppt_implication": "Generate editable native route objects and product-surface diagrams; do not paste screenshots.",
      "anti_copy_boundary": "Do not copy source brand, color, UI, screenshots, or exact launch structure.",
      "qa_probe": "Contact sheet should show a product-system route, not a generic report sequence.",
      "release_boundary": "public_blocked; derived rules only"
    },
    {
      "id": "mm_2_7_video_climax_single_object",
      "source_id": "run2_7_product_demo_video_reference",
      "source_type": "video tutorial or talk segment",
      "allowed_use": "derived_rules_only",
      "anchor": "demo climax segment with one transformation moment",
      "modalities": ["video", "audio", "transcript"],
      "visual_observation": "A climax works when one transformation object gets the largest visual field and the narration pauses around it.",
      "transcript_or_teaching_claim": "The audience should remember one proof moment, not a grid of supporting facts.",
      "extracted_design_rule": "The climax slide should allocate 40-55% of canvas to one native proof object and move secondary explanation to a side rail.",
      "slide_roles": ["climax"],
      "native_ppt_implication": "Build the climax as grouped editable shapes with trace labels outside the main object.",
      "anti_copy_boundary": "Do not store video, frames, audio, transcript, or the original demo composition.",
      "qa_probe": "Full-arm contact sheet should reveal one dominant climax object from thumbnail scale.",
      "release_boundary": "public_blocked; timestamp observation only"
    },
    {
      "id": "mm_2_7_typography_hierarchy_tutorial",
      "source_id": "run2_7_slide_design_tutorial_reference",
      "source_type": "transcript excerpt",
      "allowed_use": "derived_rules_only",
      "anchor": "tutorial section: visual hierarchy and headline compression",
      "modalities": ["text", "transcript"],
      "visual_observation": "Hierarchy improves when the headline is short, the proof label is smaller, and trace text is demoted.",
      "transcript_or_teaching_claim": "A slide needs one dominant message before supporting detail.",
      "extracted_design_rule": "Use at most nine words for climax headline, 44-58 px hero scale, 14-18 px support text, and 8-10 px trace labels.",
      "slide_roles": ["cover", "contrast", "proof", "climax"],
      "native_ppt_implication": "Set text boxes with explicit font sizes and fixed bboxes; never rely on auto-fit to hide density.",
      "anti_copy_boundary": "Do not copy tutorial examples, screenshots, or exact wording.",
      "qa_probe": "Layout QA and contact sheet should show headline hierarchy without overlapping trace labels.",
      "release_boundary": "public_blocked; short derived teaching claim only"
    },
    {
      "id": "mm_2_7_spacing_editorial_grid_tutorial",
      "source_id": "run2_7_presentation_hierarchy_reference",
      "source_type": "visual case article",
      "allowed_use": "derived_rules_only",
      "anchor": "article section: whitespace, focal zones, and contrast",
      "modalities": ["text", "image_reference"],
      "visual_observation": "Whitespace reads as intentional when focal, support, and provenance zones have stable margins.",
      "transcript_or_teaching_claim": "Good spacing clarifies what the audience should inspect first.",
      "extracted_design_rule": "Use 64-88 px outer margins, 28-40 px gutters, and separate focal/support/provenance zones.",
      "slide_roles": ["setup", "contrast", "proof", "climax", "close"],
      "native_ppt_implication": "Use deterministic coordinates for focal object, side rail, trace rail, and QA gate; avoid equal-card grids.",
      "anti_copy_boundary": "Do not copy article layouts, images, or visual examples.",
      "qa_probe": "Contact sheet should show deliberate whitespace around the main proof object.",
      "release_boundary": "public_blocked; derived spacing rules only"
    },
    {
      "id": "mm_2_7_motion_demo_pacing_reference",
      "source_id": "run2_7_product_demo_video_reference",
      "source_type": "video tutorial or talk segment",
      "allowed_use": "derived_rules_only",
      "anchor": "demo pacing segment: setup, reveal, proof, pause, gate",
      "modalities": ["video", "audio"],
      "visual_observation": "Even in a static deck, pacing can be expressed by scale changes, route order, and pause slides.",
      "transcript_or_teaching_claim": "The demo should slow down around the proof moment.",
      "extracted_design_rule": "Six-slide rhythm should compress setup, enlarge contrast, route proof, pause at climax, and simplify close.",
      "slide_roles": ["setup", "contrast", "proof", "climax", "close"],
      "native_ppt_implication": "Encode pacing as rhythm strip, slide-role scale, and ordered reveal metadata in trace.",
      "anti_copy_boundary": "Do not copy video frames, audio, transcript, or presenter sequence.",
      "qa_probe": "Full skill series image should show visible rhythm changes across runs.",
      "release_boundary": "public_blocked; derived pacing only"
    },
    {
      "id": "mm_2_7_product_surface_interaction_reference",
      "source_id": "run2_7_figma_design_system_launch_reference",
      "source_type": "interaction or product-surface reference",
      "allowed_use": "derived_rules_only",
      "anchor": "public product surface section: editable system object",
      "modalities": ["image_reference", "interaction"],
      "visual_observation": "The product surface should behave like an editable system diagram instead of a pasted UI screenshot.",
      "transcript_or_teaching_claim": "A product workflow is credible when the object shows inputs, decisions, and output state.",
      "extracted_design_rule": "Represent Vulca as a native PPT system object with input memory lane, workflow decision lane, and generated slide surface.",
      "slide_roles": ["proof", "climax"],
      "native_ppt_implication": "Use grouped native shapes for the system object, with clear input, decision, and output zones.",
      "anti_copy_boundary": "Do not copy product UI, product marks, screenshots, or source layout.",
      "qa_probe": "The climax should remain inspectable as a native object in PPTX package checks.",
      "release_boundary": "public_blocked; derived interaction model only"
    }
  ],
  "qa_gates": [
    "all records store derived observations only",
    "all records include anti-copy boundary",
    "all records produce native PPT implications",
    "all records map to at least one slide role"
  ]
}
```

- [ ] **Step 4: Create `run2_7_design_memory.json`**

Use this JSON body:

```json
{
  "schema_version": 1,
  "status": "run2_7_design_memory_public_blocked",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "memory_type": "deterministic_serializable_rules",
  "memories": [
    {
      "id": "memory_typography_editorial_launch",
      "source_record_ids": ["mm_2_7_typography_hierarchy_tutorial", "mm_2_7_design_system_launch_case"],
      "applicable_usecases": ["usecase_ai_design_to_production_platform_launch"],
      "applicable_slide_roles": ["cover", "contrast", "proof", "climax"],
      "typography_rules": [
        "cover headline 46-62 px with at most 10 words",
        "climax headline 44-58 px with at most 9 words",
        "support text 14-18 px and no more than 2 lines",
        "trace labels 8-10 px and visually separated from hero text"
      ],
      "spacing_rules": [
        "hero headline starts inside a 72-88 px left margin",
        "trace rail stays below or beside proof object and never touches headline"
      ],
      "composition_rules": [
        "title hierarchy must visibly dominate metadata",
        "proof captions must support the main object instead of becoming report paragraphs"
      ],
      "rhythm_rules": [
        "cover is a slow opening with fewer than 38 visible words",
        "proof slide can expose route labels but not long prose"
      ],
      "native_ppt_generation_requirements": [
        "create native editable text boxes with fixed bboxes",
        "write run2_7_design_memory_ids into trace",
        "record typography choices in layout JSON"
      ],
      "forbidden_patterns": [
        "dense report paragraph",
        "dashboard label field",
        "equal card headline stack",
        "source brand typography copy"
      ],
      "qa_probes": [
        "contact sheet shows clear headline hierarchy",
        "layout QA reports zero tight-text warnings"
      ],
      "release_boundary": "public_blocked until typography and trace review pass"
    },
    {
      "id": "memory_spacing_climax_proof_grid",
      "source_record_ids": ["mm_2_7_spacing_editorial_grid_tutorial", "mm_2_7_video_climax_single_object"],
      "applicable_usecases": ["usecase_ai_design_to_production_platform_launch"],
      "applicable_slide_roles": ["setup", "contrast", "proof", "climax", "close"],
      "typography_rules": [
        "spacing labels use 9-11 px mono text",
        "side rail text stays below 15 words per block"
      ],
      "spacing_rules": [
        "use 64-88 px outer margins",
        "use 28-40 px gutters between focal, support, and provenance zones",
        "reserve a bottom trace rail between 34 and 52 px high",
        "no proof object may touch slide chrome"
      ],
      "composition_rules": [
        "separate focal zone, support zone, provenance zone, and gate zone",
        "avoid equal-width card rows on contrast, proof, and climax"
      ],
      "rhythm_rules": [
        "setup has three selected states and one surface",
        "climax has one pause field and one side rail"
      ],
      "native_ppt_generation_requirements": [
        "draw focal/support/provenance zones as native shapes",
        "write spacing token decision into run2_7_workflow_decision_ids",
        "export layout JSON with stable element ids"
      ],
      "forbidden_patterns": [
        "equal card grid",
        "floating nested cards",
        "report dashboard",
        "microtype provenance"
      ],
      "qa_probes": [
        "contact sheet shows whitespace around proof object",
        "layout QA reports zero overlap errors"
      ],
      "release_boundary": "public_blocked until spacing review and layout QA pass"
    },
    {
      "id": "memory_composition_single_object_climax",
      "source_record_ids": [
        "mm_2_7_video_climax_single_object",
        "mm_2_7_product_surface_interaction_reference",
        "mm_2_7_design_system_launch_case"
      ],
      "applicable_usecases": ["usecase_ai_design_to_production_platform_launch"],
      "applicable_slide_roles": ["climax"],
      "typography_rules": [
        "climax headline at most 9 words",
        "side rail has 3 short labels and no paragraph blocks"
      ],
      "spacing_rules": [
        "one native proof object occupies 40-55% of the canvas",
        "secondary proof detail stays in a right side rail",
        "trace/provenance remains below the main visual field"
      ],
      "composition_rules": [
        "one native proof object occupies 40-55% of the canvas",
        "proof object shows input memory lane, workflow decision lane, and generated PPT surface",
        "the main object must be visibly larger than all support objects combined"
      ],
      "rhythm_rules": [
        "climax is a pause slide",
        "climax contains fewer visual regions than proof slide"
      ],
      "native_ppt_generation_requirements": [
        "build grouped editable shapes for memory lane, workflow lane, and generated slide surface",
        "do not use screenshots or full-slide raster",
        "write run2_7_quality_gate as native_climax_object_present"
      ],
      "forbidden_patterns": [
        "equal cards",
        "multi-panel dashboard",
        "copied source UI",
        "full-slide raster",
        "tiny report labels"
      ],
      "qa_probes": [
        "contact sheet should show a clear single-object climax",
        "PPTX native guard should find no picture shapes in the full arm"
      ],
      "release_boundary": "public_blocked until climax object, native guard, and human review pass"
    },
    {
      "id": "memory_rhythm_six_slide_launch",
      "source_record_ids": ["mm_2_7_motion_demo_pacing_reference", "mm_2_7_design_system_launch_case"],
      "applicable_usecases": ["usecase_ai_design_to_production_platform_launch"],
      "applicable_slide_roles": ["cover", "setup", "contrast", "proof", "climax", "close"],
      "typography_rules": [
        "visible word count decreases on cover and climax",
        "proof slide may include route labels but not long explanatory copy"
      ],
      "spacing_rules": [
        "rhythm strip remains constant across all six slides",
        "slide role scale changes by changing object size, not by shrinking all text"
      ],
      "composition_rules": [
        "cover names product category",
        "setup selects the problem",
        "contrast shows before/after",
        "proof routes source-to-memory-to-workflow",
        "climax pauses on one object",
        "close returns to release gate"
      ],
      "rhythm_rules": [
        "compress setup",
        "enlarge contrast",
        "route proof",
        "pause at climax",
        "simplify close"
      ],
      "native_ppt_generation_requirements": [
        "draw native rhythm strip with active slide marker",
        "write ordered rhythm role and selected memory ids into trace",
        "make full-skill series sheet show Run 2.7 after Run 2.6R"
      ],
      "forbidden_patterns": [
        "same-density slides",
        "same-size proof objects",
        "engineering report rhythm",
        "unexplained visual climax"
      ],
      "qa_probes": [
        "full skill series image shows visible rhythm change",
        "four-arm contact sheet shows stronger full-arm climax than controls"
      ],
      "release_boundary": "public_blocked until rhythm comparison and review pass"
    },
    {
      "id": "memory_source_brand_sanitization_v2",
      "source_record_ids": [
        "mm_2_7_design_system_launch_case",
        "mm_2_7_product_surface_interaction_reference",
        "mm_2_7_spacing_editorial_grid_tutorial"
      ],
      "applicable_usecases": ["usecase_ai_design_to_production_platform_launch"],
      "applicable_slide_roles": ["cover", "setup", "contrast", "proof", "climax", "close"],
      "typography_rules": [
        "use Vulca-specific labels and neutral product language",
        "do not reproduce source headline wording"
      ],
      "spacing_rules": [
        "do not reproduce source layout proportions",
        "use original Vulca grid zones from workflow policy"
      ],
      "composition_rules": [
        "learn structure without copying visible identity",
        "translate source patterns into original native PPT primitives"
      ],
      "rhythm_rules": [
        "source rhythm can inform pacing only as derived rules",
        "do not copy source demo sequence"
      ],
      "native_ppt_generation_requirements": [
        "write source_brand_sanitization as learned_structure_no_visual_copy",
        "block copied logos, screenshots, exact palettes, and full-slide images",
        "keep public_blocked gate until human review confirms boundary"
      ],
      "forbidden_patterns": [
        "source brand copy",
        "source screenshot",
        "source exact palette",
        "source deck layout copy",
        "source UI copy"
      ],
      "qa_probes": [
        "source-brand QA confirms no copied identity",
        "contact sheet reads as Vulca-specific"
      ],
      "release_boundary": "public_blocked until source-brand review passes"
    }
  ],
  "qa_gates": [
    "all memories reference valid Run 2.7 source records",
    "all memories map to the selected commercial usecase",
    "all memories include native PPT generation requirements",
    "all memories include forbidden patterns and public_blocked boundary"
  ]
}
```

- [ ] **Step 5: Create `run2_7_workflow_policy.json`**

Use this JSON body:

```json
{
  "schema_version": 1,
  "status": "run2_7_workflow_policy_public_blocked",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
  "selection_chain": [
    "commercial_usecase",
    "source_record_ids",
    "typography_memory_id",
    "spacing_memory_id",
    "composition_memory_id",
    "rhythm_memory_id",
    "brand_sanitization_memory_id",
    "visual_repair_policy_ids",
    "native_ppt_generation",
    "qa_gate"
  ],
  "slide_role_memory_map": [
    {
      "rhythm_role": "cover",
      "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
      "source_record_ids": [
        "mm_2_7_design_system_launch_case",
        "mm_2_7_typography_hierarchy_tutorial",
        "mm_2_7_motion_demo_pacing_reference"
      ],
      "design_memory_ids": [
        "memory_typography_editorial_launch",
        "memory_rhythm_six_slide_launch",
        "memory_source_brand_sanitization_v2"
      ],
      "workflow_decision_ids": [
        "decision_run2_7_select_real_usecase",
        "decision_run2_7_select_editorial_typography",
        "decision_run2_7_apply_brand_sanitization"
      ],
      "visual_repair_policy_ids": ["repair_editorial_typography_system"],
      "native_ppt_generation": "draw native cover with product-category headline, memory rail, and generated output signal",
      "workflow_gates": [
        "public_blocked boundary recorded",
        "native editable text boxes required",
        "source-brand copy blocked"
      ],
      "trace_fields": [
        "run2_7_usecase_id",
        "run2_7_source_record_ids",
        "run2_7_design_memory_ids",
        "run2_7_workflow_decision_ids",
        "run2_7_delta_from_run2_6r",
        "run2_7_quality_gate"
      ]
    },
    {
      "rhythm_role": "setup",
      "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
      "source_record_ids": [
        "mm_2_7_design_system_launch_case",
        "mm_2_7_spacing_editorial_grid_tutorial",
        "mm_2_7_motion_demo_pacing_reference"
      ],
      "design_memory_ids": [
        "memory_spacing_climax_proof_grid",
        "memory_rhythm_six_slide_launch",
        "memory_source_brand_sanitization_v2"
      ],
      "workflow_decision_ids": [
        "decision_run2_7_select_setup_density",
        "decision_run2_7_select_spacing_zones",
        "decision_run2_7_apply_brand_sanitization"
      ],
      "visual_repair_policy_ids": ["repair_spacing_token_visibility"],
      "native_ppt_generation": "draw selected usecase, source records, and memory choices as editable native decision states",
      "workflow_gates": [
        "public_blocked boundary recorded",
        "native selected states required",
        "source-brand copy blocked"
      ],
      "trace_fields": [
        "run2_7_usecase_id",
        "run2_7_source_record_ids",
        "run2_7_design_memory_ids",
        "run2_7_workflow_decision_ids",
        "run2_7_delta_from_run2_6r",
        "run2_7_quality_gate"
      ]
    },
    {
      "rhythm_role": "contrast",
      "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
      "source_record_ids": [
        "mm_2_7_typography_hierarchy_tutorial",
        "mm_2_7_spacing_editorial_grid_tutorial",
        "mm_2_7_design_system_launch_case"
      ],
      "design_memory_ids": [
        "memory_typography_editorial_launch",
        "memory_spacing_climax_proof_grid",
        "memory_rhythm_six_slide_launch"
      ],
      "workflow_decision_ids": [
        "decision_run2_7_select_before_after_delta",
        "decision_run2_7_select_editorial_typography",
        "decision_run2_7_select_spacing_zones"
      ],
      "visual_repair_policy_ids": ["repair_mini_preview_fidelity", "repair_spacing_token_visibility"],
      "native_ppt_generation": "draw prompt-only before state and full-memory after state as editable native panels with one larger after object",
      "workflow_gates": [
        "public_blocked boundary recorded",
        "native before-after objects required",
        "source-brand copy blocked"
      ],
      "trace_fields": [
        "run2_7_usecase_id",
        "run2_7_source_record_ids",
        "run2_7_design_memory_ids",
        "run2_7_workflow_decision_ids",
        "run2_7_delta_from_run2_6r",
        "run2_7_quality_gate"
      ]
    },
    {
      "rhythm_role": "proof",
      "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
      "source_record_ids": [
        "mm_2_7_design_system_launch_case",
        "mm_2_7_product_surface_interaction_reference",
        "mm_2_7_spacing_editorial_grid_tutorial"
      ],
      "design_memory_ids": [
        "memory_spacing_climax_proof_grid",
        "memory_rhythm_six_slide_launch",
        "memory_source_brand_sanitization_v2"
      ],
      "workflow_decision_ids": [
        "decision_run2_7_select_source_to_memory_route",
        "decision_run2_7_select_native_surface_route",
        "decision_run2_7_apply_brand_sanitization"
      ],
      "visual_repair_policy_ids": ["repair_mini_preview_fidelity"],
      "native_ppt_generation": "draw source records, memory ids, workflow gate, and generated slide surface as a native route",
      "workflow_gates": [
        "public_blocked boundary recorded",
        "native route object required",
        "source-brand copy blocked"
      ],
      "trace_fields": [
        "run2_7_usecase_id",
        "run2_7_source_record_ids",
        "run2_7_design_memory_ids",
        "run2_7_workflow_decision_ids",
        "run2_7_delta_from_run2_6r",
        "run2_7_quality_gate"
      ]
    },
    {
      "rhythm_role": "climax",
      "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
      "source_record_ids": [
        "mm_2_7_video_climax_single_object",
        "mm_2_7_product_surface_interaction_reference",
        "mm_2_7_typography_hierarchy_tutorial"
      ],
      "design_memory_ids": [
        "memory_composition_single_object_climax",
        "memory_typography_editorial_launch",
        "memory_source_brand_sanitization_v2"
      ],
      "workflow_decision_ids": [
        "decision_run2_7_select_single_object_climax",
        "decision_run2_7_select_editorial_typography",
        "decision_run2_7_apply_brand_sanitization"
      ],
      "visual_repair_policy_ids": [
        "repair_climax_editorial_spread",
        "repair_theme_differentiation_from_run2_5"
      ],
      "native_ppt_generation": "draw one grouped native proof object occupying 40-55% of canvas with memory/workflow lanes and generated slide surface",
      "workflow_gates": [
        "public_blocked boundary recorded",
        "native climax object required",
        "source-brand copy blocked"
      ],
      "trace_fields": [
        "run2_7_usecase_id",
        "run2_7_source_record_ids",
        "run2_7_design_memory_ids",
        "run2_7_workflow_decision_ids",
        "run2_7_delta_from_run2_6r",
        "run2_7_quality_gate"
      ]
    },
    {
      "rhythm_role": "close",
      "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
      "source_record_ids": [
        "mm_2_7_design_system_launch_case",
        "mm_2_7_motion_demo_pacing_reference",
        "mm_2_7_spacing_editorial_grid_tutorial"
      ],
      "design_memory_ids": [
        "memory_rhythm_six_slide_launch",
        "memory_spacing_climax_proof_grid",
        "memory_source_brand_sanitization_v2"
      ],
      "workflow_decision_ids": [
        "decision_run2_7_select_release_gate",
        "decision_run2_7_select_spacing_zones",
        "decision_run2_7_apply_brand_sanitization"
      ],
      "visual_repair_policy_ids": ["repair_editorial_typography_system", "repair_mini_preview_fidelity"],
      "native_ppt_generation": "draw internal-demo result, public-blocked gate, and next data/workflow thickening handoff as native objects",
      "workflow_gates": [
        "public_blocked boundary recorded",
        "native release gate required",
        "source-brand copy blocked"
      ],
      "trace_fields": [
        "run2_7_usecase_id",
        "run2_7_source_record_ids",
        "run2_7_design_memory_ids",
        "run2_7_workflow_decision_ids",
        "run2_7_delta_from_run2_6r",
        "run2_7_quality_gate"
      ]
    }
  ],
  "qa_gates": [
    "selected usecase exists",
    "selected source records exist",
    "selected design memory ids exist",
    "all generated slides include Run 2.7 trace fields",
    "full arm uses native editable PPT primitives",
    "public_blocked remains active before human approval"
  ]
}
```

- [ ] **Step 6: Modify `skill_workflow.json` to insert the Run 2.7 stage**

Insert this stage after `select_visual_repair_policy` and before `select_visual_production_modules`, then renumber subsequent stage `order` values so they remain sequential:

```json
{
  "id": "select_run2_7_design_memory",
  "order": 12,
  "layer": "skill_workflow",
  "inputs": [
    "run2_7_commercial_usecase.json",
    "run2_7_multimodal_source_records.json",
    "run2_7_design_memory.json",
    "run2_7_workflow_policy.json",
    "visual_repair_policy.json"
  ],
  "outputs": [
    "selected Run 2.7 usecase id",
    "selected Run 2.7 source record ids",
    "selected Run 2.7 design memory ids",
    "selected Run 2.7 workflow decision ids"
  ],
  "gates": [
    "commercial usecase is real and public_blocked",
    "source records are derived observations only",
    "design memory is deterministic and serializable",
    "native generation can trace memory ids",
    "source-brand copying is blocked"
  ]
}
```

The final `stage_ids` order in `tests/test_ppt_run2_data_skill_quality.py::test_run2_skill_workflow_is_declarative_and_gated` must become:

```python
[
    "read_commercial_case",
    "compile_multimodal_database",
    "compile_evidence_memory",
    "compile_aesthetic_memory",
    "compile_production_reference_decompositions",
    "compile_aesthetic_memory_v2",
    "select_slide_archetypes",
    "select_commercial_usecase",
    "select_aesthetic_benchmarks",
    "select_theme_typography_spacing_policy",
    "select_visual_repair_policy",
    "select_run2_7_design_memory",
    "select_visual_production_modules",
    "generate_code_first_ppt",
    "run_structural_and_aesthetic_qa",
    "recommend_repairs",
    "refresh_trace_qa_outcomes",
    "emit_release_decision",
]
```

Update the assertion immediately below it to:

```python
assert [stage["order"] for stage in workflow["stages"]] == list(range(1, 19))
```

- [ ] **Step 7: Modify `trace_manifest_contract.json`**

Add the following values to `per_slide_required_fields`:

```json
"run2_7_usecase_id",
"run2_7_source_record_ids",
"run2_7_design_memory_ids",
"run2_7_workflow_decision_ids",
"run2_7_delta_from_run2_6r",
"run2_7_quality_gate"
```

- [ ] **Step 8: Modify `RUN2_REQUIRED_FILES` in `scripts/validate_ppt_case_pack.py`**

Add these entries after `visual_repair_policy.json`:

```python
"run2_7_commercial_usecase.json",
"run2_7_multimodal_source_records.json",
"run2_7_design_memory.json",
"run2_7_workflow_policy.json",
```

- [ ] **Step 9: Add validator constants and functions**

Add these constants after `RUN2_6R_REPAIR_ROLES`:

```python
RUN2_7_MEMORY_FIELDS = [
    "id",
    "source_record_ids",
    "applicable_usecases",
    "applicable_slide_roles",
    "typography_rules",
    "spacing_rules",
    "composition_rules",
    "rhythm_rules",
    "native_ppt_generation_requirements",
    "forbidden_patterns",
    "qa_probes",
    "release_boundary",
]
RUN2_7_TRACE_FIELDS = {
    "run2_7_usecase_id",
    "run2_7_source_record_ids",
    "run2_7_design_memory_ids",
    "run2_7_workflow_decision_ids",
    "run2_7_delta_from_run2_6r",
    "run2_7_quality_gate",
}
```

Add these functions before `validate_sources`:

```python
def validate_run2_7_commercial_usecase(pack_dir: Path, errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "run2_7_commercial_usecase.json", errors)
    require_keys(
        "run2_7_commercial_usecase.json",
        data,
        [
            "schema_version",
            "status",
            "stage_policy",
            "id",
            "primary_usecase",
            "audience",
            "business_job",
            "business_decision",
            "deck_mission",
            "six_slide_arc",
            "must_show",
            "must_not_show",
            "proof_questions",
            "release_boundary",
        ],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_7_commercial_usecase.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("run2_7_commercial_usecase.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_7_commercial_usecase.stage_policy must be repeat_same_five_layers_not_run3")
    usecase_id = data.get("id")
    seen_usecase_ids: set[str] = set()
    if "id" in data and require_non_empty_string("run2_7_commercial_usecase.id", usecase_id, errors):
        seen_usecase_ids.add(usecase_id)
    for key in ["primary_usecase", "business_decision", "deck_mission"]:
        if key in data:
            require_non_empty_string(f"run2_7_commercial_usecase.{key}", data[key], errors)
    for key in ["audience", "business_job", "must_show", "must_not_show", "proof_questions"]:
        if key in data:
            validate_string_list(f"run2_7_commercial_usecase.{key}", data[key], errors)
    arc = data.get("six_slide_arc", [])
    if require_non_empty_list("run2_7_commercial_usecase.six_slide_arc", arc, errors):
        roles: list[str] = []
        for index, slide in enumerate(arc):
            label = f"run2_7_commercial_usecase.six_slide_arc[{index}]"
            if not isinstance(slide, dict):
                errors.append(f"{label} must be an object")
                continue
            require_keys(label, slide, ["slide_id", "rhythm_role", "job", "must_show", "must_not_show"], errors)
            if "rhythm_role" in slide:
                role = slide["rhythm_role"]
                if validate_choice(f"{label}.rhythm_role", role, RUN2_RHYTHM_ROLES, errors):
                    roles.append(role)
            for key in ["slide_id", "job", "must_show", "must_not_show"]:
                if key in slide:
                    require_non_empty_string(f"{label}.{key}", slide[key], errors)
        if roles != ["cover", "setup", "contrast", "proof", "climax", "close"]:
            errors.append("run2_7_commercial_usecase.six_slide_arc must use cover/setup/contrast/proof/climax/close order")
    if "release_boundary" in data:
        validate_public_blocked_boundary("run2_7_commercial_usecase.release_boundary", data["release_boundary"], errors)
    validate_no_external_media_reference("run2_7_commercial_usecase", data, errors)
    return seen_usecase_ids


def validate_run2_7_source_records(pack_dir: Path, source_ids: set[str], errors: list[str]) -> set[str]:
    data = load_json(pack_dir / "run2_7_multimodal_source_records.json", errors)
    require_keys(
        "run2_7_multimodal_source_records.json",
        data,
        ["schema_version", "status", "stage_policy", "storage_policy", "records", "qa_gates"],
        errors,
    )
    if "schema_version" in data:
        require_integer("run2_7_multimodal_source_records.schema_version", data["schema_version"], errors)
    if "status" in data:
        require_non_empty_string("run2_7_multimodal_source_records.status", data["status"], errors)
    if "stage_policy" in data and data["stage_policy"] != "repeat_same_five_layers_not_run3":
        errors.append("run2_7_multimodal_source_records.stage_policy must be repeat_same_five_layers_not_run3")
    storage_policy = data.get("storage_policy", {})
    if require_non_empty_dict("run2_7_multimodal_source_records.storage_policy", storage_policy, errors):
        if storage_policy.get("raw_media") != "forbidden":
            errors.append("run2_7_multimodal_source_records.storage_policy.raw_media must be forbidden")
    records = data.get("records", [])
    seen_record_ids: set[str] = set()
    if require_non_empty_list("run2_7_multimodal_source_records.records", records, errors):
        for index, record in enumerate(records):
            label = f"run2_7_multimodal_source_records.records[{index}]"
            if not isinstance(record, dict):
                errors.append(f"{label} must be an object")
                continue
            require_keys(
                label,
                record,
                [
                    "id",
                    "source_id",
                    "source_type",
                    "allowed_use",
                    "anchor",
                    "modalities",
                    "visual_observation",
                    "transcript_or_teaching_claim",
                    "extracted_design_rule",
                    "slide_roles",
                    "native_ppt_implication",
                    "anti_copy_boundary",
                    "qa_probe",
                    "release_boundary",
                ],
                errors,
            )
            record_id = record.get("id")
            if "id" in record and require_non_empty_string(f"{label}.id", record_id, errors):
                if record_id in seen_record_ids:
                    errors.append(f"{label}.id duplicates {record_id}")
                seen_record_ids.add(record_id)
            if "source_id" in record:
                source_id = record["source_id"]
                if require_non_empty_string(f"{label}.source_id", source_id, errors) and source_id not in source_ids:
                    errors.append(f"{label}.source_id {source_id} is not defined in sources.json")
            if "allowed_use" in record and record["allowed_use"] != "derived_rules_only":
                errors.append(f"{label}.allowed_use must be derived_rules_only")
            for key in [
                "source_type",
                "anchor",
                "visual_observation",
                "transcript_or_teaching_claim",
                "extracted_design_rule",
                "native_ppt_implication",
                "anti_copy_boundary",
                "qa_probe",
            ]:
                if key in record:
                    require_non_empty_string(f"{label}.{key}", record[key], errors)
            if "modalities" in record and validate_string_list(f"{label}.modalities", record["modalities"], errors):
                for modality in record["modalities"]:
                    if modality not in RUN2_MULTIMODAL_MODALITIES:
                        errors.append(f"{label}.modalities has unexpected value: {modality}")
            if "slide_roles" in record and validate_string_list(f"{label}.slide_roles", record["slide_roles"], errors):
                for role in record["slide_roles"]:
                    if role not in RUN2_RHYTHM_ROLES:
                        errors.append(f"{label}.slide_roles has unexpected value: {role}")
            if "native_ppt_implication" in record:
                validate_string_mentions(f"{label}.native_ppt_implication", record["native_ppt_implication"], ["native", "editable"], errors)
            if "anti_copy_boundary" in record:
                validate_string_mentions(f"{label}.anti_copy_boundary", record["anti_copy_boundary"], ["do not copy"], errors)
            if "release_boundary" in record:
                validate_public_blocked_boundary(f"{label}.release_boundary", record["release_boundary"], errors)
            validate_no_external_media_reference(label, record, errors)
    if "qa_gates" in data:
        validate_string_list("run2_7_multimodal_source_records.qa_gates", data["qa_gates"], errors)
    return seen_record_ids


def validate_run2_7_design_memory(
    pack_dir: Path,
    source_record_ids: set[str],
    usecase_ids: set[str],
    errors: list[str],
) -> set[str]:
    data = load_json(pack_dir / "run2_7_design_memory.json", errors)
    require_keys(
        "run2_7_design_memory.json",
        data,
        ["schema_version", "status", "stage_policy", "memory_type", "memories", "qa_gates"],
        errors,
    )
    if "memory_type" in data and data["memory_type"] != "deterministic_serializable_rules":
        errors.append("run2_7_design_memory.memory_type must be deterministic_serializable_rules")
    memories = data.get("memories", [])
    seen_memory_ids: set[str] = set()
    if require_non_empty_list("run2_7_design_memory.memories", memories, errors):
        for index, memory in enumerate(memories):
            label = f"run2_7_design_memory.memories[{index}]"
            if not isinstance(memory, dict):
                errors.append(f"{label} must be an object")
                continue
            require_keys(label, memory, RUN2_7_MEMORY_FIELDS, errors)
            memory_id = memory.get("id")
            if "id" in memory and require_non_empty_string(f"{label}.id", memory_id, errors):
                if memory_id in seen_memory_ids:
                    errors.append(f"{label}.id duplicates {memory_id}")
                seen_memory_ids.add(memory_id)
            if "source_record_ids" in memory:
                validate_known_string_references(
                    f"{label}.source_record_ids",
                    memory["source_record_ids"],
                    source_record_ids,
                    "Run 2.7 source record",
                    errors,
                )
            if "applicable_usecases" in memory:
                validate_known_string_references(
                    f"{label}.applicable_usecases",
                    memory["applicable_usecases"],
                    usecase_ids,
                    "Run 2.7 commercial usecase",
                    errors,
                )
            if "applicable_slide_roles" in memory and validate_string_list(f"{label}.applicable_slide_roles", memory["applicable_slide_roles"], errors):
                for role in memory["applicable_slide_roles"]:
                    if role not in RUN2_RHYTHM_ROLES:
                        errors.append(f"{label}.applicable_slide_roles has unexpected value: {role}")
            for key in [
                "typography_rules",
                "spacing_rules",
                "composition_rules",
                "rhythm_rules",
                "native_ppt_generation_requirements",
                "forbidden_patterns",
                "qa_probes",
            ]:
                if key in memory:
                    validate_string_list(f"{label}.{key}", memory[key], errors)
            if "native_ppt_generation_requirements" in memory:
                validate_combined_terms(
                    f"{label}.native_ppt_generation_requirements",
                    memory["native_ppt_generation_requirements"],
                    ["native", "editable", "trace"],
                    errors,
                )
            if "release_boundary" in memory:
                validate_public_blocked_boundary(f"{label}.release_boundary", memory["release_boundary"], errors)
            validate_no_external_media_reference(label, memory, errors)
    if "qa_gates" in data:
        validate_string_list("run2_7_design_memory.qa_gates", data["qa_gates"], errors)
    return seen_memory_ids


def validate_run2_7_workflow_policy(
    pack_dir: Path,
    source_record_ids: set[str],
    usecase_ids: set[str],
    memory_ids: set[str],
    errors: list[str],
) -> None:
    data = load_json(pack_dir / "run2_7_workflow_policy.json", errors)
    require_keys(
        "run2_7_workflow_policy.json",
        data,
        [
            "schema_version",
            "status",
            "stage_policy",
            "commercial_usecase_id",
            "selection_chain",
            "slide_role_memory_map",
            "qa_gates",
        ],
        errors,
    )
    usecase_id = data.get("commercial_usecase_id")
    if "commercial_usecase_id" in data and require_non_empty_string("run2_7_workflow_policy.commercial_usecase_id", usecase_id, errors):
        if usecase_id not in usecase_ids:
            errors.append(f"run2_7_workflow_policy.commercial_usecase_id references unknown usecase: {usecase_id}")
    if "selection_chain" in data:
        validate_exact_string_set(
            "run2_7_workflow_policy.selection_chain",
            data["selection_chain"],
            {
                "commercial_usecase",
                "source_record_ids",
                "typography_memory_id",
                "spacing_memory_id",
                "composition_memory_id",
                "rhythm_memory_id",
                "brand_sanitization_memory_id",
                "visual_repair_policy_ids",
                "native_ppt_generation",
                "qa_gate",
            },
            errors,
        )
    mappings = data.get("slide_role_memory_map", [])
    if require_non_empty_list("run2_7_workflow_policy.slide_role_memory_map", mappings, errors):
        for index, mapping in enumerate(mappings):
            label = f"run2_7_workflow_policy.slide_role_memory_map[{index}]"
            if not isinstance(mapping, dict):
                errors.append(f"{label} must be an object")
                continue
            require_keys(
                label,
                mapping,
                [
                    "rhythm_role",
                    "commercial_usecase_id",
                    "source_record_ids",
                    "design_memory_ids",
                    "workflow_decision_ids",
                    "visual_repair_policy_ids",
                    "native_ppt_generation",
                    "workflow_gates",
                    "trace_fields",
                ],
                errors,
            )
            if "rhythm_role" in mapping:
                validate_choice(f"{label}.rhythm_role", mapping["rhythm_role"], RUN2_RHYTHM_ROLES, errors)
            if "commercial_usecase_id" in mapping:
                mapped_usecase = mapping["commercial_usecase_id"]
                if require_non_empty_string(f"{label}.commercial_usecase_id", mapped_usecase, errors) and mapped_usecase not in usecase_ids:
                    errors.append(f"{label}.commercial_usecase_id references unknown usecase: {mapped_usecase}")
            if "source_record_ids" in mapping:
                validate_known_string_references(
                    f"{label}.source_record_ids",
                    mapping["source_record_ids"],
                    source_record_ids,
                    "Run 2.7 source record",
                    errors,
                )
            if "design_memory_ids" in mapping:
                validate_known_string_references(
                    f"{label}.design_memory_ids",
                    mapping["design_memory_ids"],
                    memory_ids,
                    "Run 2.7 design memory",
                    errors,
                )
            for key in ["workflow_decision_ids", "visual_repair_policy_ids", "workflow_gates"]:
                if key in mapping:
                    validate_string_list(f"{label}.{key}", mapping[key], errors)
            if "native_ppt_generation" in mapping:
                validate_string_mentions(f"{label}.native_ppt_generation", mapping["native_ppt_generation"], ["native"], errors)
            if "trace_fields" in mapping:
                validate_exact_string_set(f"{label}.trace_fields", mapping["trace_fields"], RUN2_7_TRACE_FIELDS, errors)
            validate_no_external_media_reference(label, mapping, errors)
    if "qa_gates" in data:
        validate_string_list("run2_7_workflow_policy.qa_gates", data["qa_gates"], errors)
```

- [ ] **Step 10: Call the new validators from `validate_case_pack`**

In `validate_case_pack`, after existing Run 2 validators and after `source_ids = validate_sources(...)`, wire the Run 2.7 validators like this:

```python
run2_7_usecase_ids: set[str] = set()
run2_7_source_record_ids: set[str] = set()
run2_7_memory_ids: set[str] = set()
if profile == "run2":
    run2_7_usecase_ids = validate_run2_7_commercial_usecase(pack_dir, errors)
    run2_7_source_record_ids = validate_run2_7_source_records(pack_dir, source_ids, errors)
    run2_7_memory_ids = validate_run2_7_design_memory(
        pack_dir,
        run2_7_source_record_ids,
        run2_7_usecase_ids,
        errors,
    )
    validate_run2_7_workflow_policy(
        pack_dir,
        run2_7_source_record_ids,
        run2_7_usecase_ids,
        run2_7_memory_ids,
        errors,
    )
```

Keep existing Run 2 validators intact. If `validate_case_pack` already has a Run 2 block, insert these calls inside that block after `source_ids` is available.

- [ ] **Step 11: Add validator regression fixture helpers**

In `tests/test_ppt_case_pack_validator.py`, extend `write_run2_required_files` so it writes the four Run 2.7 JSON files. Use the same JSON bodies from Steps 1, 3, 4, and 5 with fewer source records only if every referenced id is internally consistent. The fixture must include:

```python
(pack / "run2_7_commercial_usecase.json").write_text(
    json.dumps(valid_run2_7_commercial_usecase(), indent=2),
    encoding="utf-8",
)
(pack / "run2_7_multimodal_source_records.json").write_text(
    json.dumps(valid_run2_7_multimodal_source_records(), indent=2),
    encoding="utf-8",
)
(pack / "run2_7_design_memory.json").write_text(
    json.dumps(valid_run2_7_design_memory(), indent=2),
    encoding="utf-8",
)
(pack / "run2_7_workflow_policy.json").write_text(
    json.dumps(valid_run2_7_workflow_policy(), indent=2),
    encoding="utf-8",
)
```

Add four helper functions below existing valid Run 2 helper functions:

```python
def valid_run2_7_commercial_usecase() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_7_commercial_usecase_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "id": "usecase_ai_design_to_production_platform_launch",
        "primary_usecase": "AI design-to-production platform launch deck",
        "audience": ["AI product builders", "design engineering leaders"],
        "business_job": ["prove product-system learning", "not one-shot prompting"],
        "business_decision": "Should a team trust Vulca for learned PPT generation?",
        "deck_mission": "Connect usecase, source records, memory, workflow, and native PPT output.",
        "six_slide_arc": [
            {"slide_id": "slide_01", "rhythm_role": "cover", "job": "name category", "must_show": "Vulca", "must_not_show": "generic slogan"},
            {"slide_id": "slide_02", "rhythm_role": "setup", "job": "show problem", "must_show": "selection", "must_not_show": "dense panels"},
            {"slide_id": "slide_03", "rhythm_role": "contrast", "job": "show before after", "must_show": "delta", "must_not_show": "dashboard"},
            {"slide_id": "slide_04", "rhythm_role": "proof", "job": "show route", "must_show": "trace", "must_not_show": "hidden provenance"},
            {"slide_id": "slide_05", "rhythm_role": "climax", "job": "show object", "must_show": "native object", "must_not_show": "raster"},
            {"slide_id": "slide_06", "rhythm_role": "close", "job": "show gate", "must_show": "public blocked", "must_not_show": "public ready"},
        ],
        "must_show": ["real usecase", "design memory", "native PPT"],
        "must_not_show": ["copy source brand", "full-slide raster"],
        "proof_questions": ["Does data affect PPT output?", "Are memory ids traced?"],
        "release_boundary": "public_blocked until review passes",
    }


def valid_run2_7_multimodal_source_records() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_7_multimodal_source_records_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "storage_policy": {
            "default": "derived_observations_only",
            "raw_media": "forbidden",
            "copyright_boundary": "derived observations only",
        },
        "records": [
            {
                "id": "mm_2_7_fixture_record",
                "source_id": "supervity_ai_keynote",
                "source_type": "visual case article",
                "allowed_use": "derived_rules_only",
                "anchor": "fixture section",
                "modalities": ["text", "image_reference", "interaction"],
                "visual_observation": "One proof object clarifies the workflow.",
                "transcript_or_teaching_claim": "Slides need one dominant message.",
                "extracted_design_rule": "Use one native editable proof object.",
                "slide_roles": ["climax"],
                "native_ppt_implication": "Generate native editable shapes.",
                "anti_copy_boundary": "do not copy source brand or layout",
                "qa_probe": "contact sheet shows one object",
                "release_boundary": "public_blocked until review",
            }
        ],
        "qa_gates": ["records are derived only"],
    }


def valid_run2_7_design_memory() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_7_design_memory_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "memory_type": "deterministic_serializable_rules",
        "memories": [
            {
                "id": "memory_fixture_climax",
                "source_record_ids": ["mm_2_7_fixture_record"],
                "applicable_usecases": ["usecase_ai_design_to_production_platform_launch"],
                "applicable_slide_roles": ["climax"],
                "typography_rules": ["headline at most 9 words"],
                "spacing_rules": ["use clear focal/support/provenance zones"],
                "composition_rules": ["one native proof object occupies 40-55% of canvas"],
                "rhythm_rules": ["pause at climax"],
                "native_ppt_generation_requirements": ["native editable shapes with trace"],
                "forbidden_patterns": ["report dashboard", "source brand copy"],
                "qa_probes": ["contact sheet shows one object"],
                "release_boundary": "public_blocked until review",
            }
        ],
        "qa_gates": ["memory references source records"],
    }


def valid_run2_7_workflow_policy() -> dict:
    return {
        "schema_version": 1,
        "status": "run2_7_workflow_policy_public_blocked",
        "stage_policy": "repeat_same_five_layers_not_run3",
        "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
        "selection_chain": [
            "commercial_usecase",
            "source_record_ids",
            "typography_memory_id",
            "spacing_memory_id",
            "composition_memory_id",
            "rhythm_memory_id",
            "brand_sanitization_memory_id",
            "visual_repair_policy_ids",
            "native_ppt_generation",
            "qa_gate",
        ],
        "slide_role_memory_map": [
            {
                "rhythm_role": "climax",
                "commercial_usecase_id": "usecase_ai_design_to_production_platform_launch",
                "source_record_ids": ["mm_2_7_fixture_record"],
                "design_memory_ids": ["memory_fixture_climax"],
                "workflow_decision_ids": ["decision_fixture_climax"],
                "visual_repair_policy_ids": ["repair_climax_editorial_spread"],
                "native_ppt_generation": "draw one native climax object",
                "workflow_gates": ["public_blocked", "native", "source-brand"],
                "trace_fields": [
                    "run2_7_usecase_id",
                    "run2_7_source_record_ids",
                    "run2_7_design_memory_ids",
                    "run2_7_workflow_decision_ids",
                    "run2_7_delta_from_run2_6r",
                    "run2_7_quality_gate",
                ],
            }
        ],
        "qa_gates": ["trace fields present"],
    }
```

- [ ] **Step 12: Add validator negative tests**

Append these tests near the existing Run 2 validator tests:

```python
def test_run2_profile_rejects_run2_7_unknown_memory_source_record(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    memory_path = pack / "run2_7_design_memory.json"
    memory = json.loads(memory_path.read_text(encoding="utf-8"))
    memory["memories"][0]["source_record_ids"] = ["missing_source_record"]
    memory_path.write_text(json.dumps(memory, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_7_design_memory.memories[0].source_record_ids references unknown Run 2.7 source record: missing_source_record"
        in result.errors
    )


def test_run2_profile_rejects_run2_7_workflow_missing_trace_field(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    write_pack(pack)
    write_run2_required_files(pack)
    policy_path = pack / "run2_7_workflow_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["slide_role_memory_map"][0]["trace_fields"].remove("run2_7_quality_gate")
    policy_path.write_text(json.dumps(policy, indent=2), encoding="utf-8")

    result = validate_case_pack(pack, profile="run2")

    assert result.ok is False
    assert (
        "run2_7_workflow_policy.slide_role_memory_map[0].trace_fields missing value: run2_7_quality_gate"
        in result.errors
    )
```

- [ ] **Step 13: Run focused tests and validator**

Run:

```bash
python3 -m pytest \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_case_pack_is_valid \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_7_has_real_usecase_and_multimodal_source_records \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_7_has_serializable_design_memory \
  tests/test_ppt_run2_data_skill_quality.py::test_run2_7_workflow_and_trace_contract_include_memory_selection \
  tests/test_ppt_case_pack_validator.py::test_run2_profile_rejects_run2_7_unknown_memory_source_record \
  tests/test_ppt_case_pack_validator.py::test_run2_profile_rejects_run2_7_workflow_missing_trace_field \
  -q
```

Expected:

```text
6 passed
```

Then run:

```bash
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
```

Expected:

```text
OK
```

- [ ] **Step 14: Commit data and validator contracts**

Run:

```bash
git add \
  docs/product/ppt-run2-data-skill-quality/sources.json \
  docs/product/ppt-run2-data-skill-quality/run2_7_commercial_usecase.json \
  docs/product/ppt-run2-data-skill-quality/run2_7_multimodal_source_records.json \
  docs/product/ppt-run2-data-skill-quality/run2_7_design_memory.json \
  docs/product/ppt-run2-data-skill-quality/run2_7_workflow_policy.json \
  docs/product/ppt-run2-data-skill-quality/skill_workflow.json \
  docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json \
  scripts/validate_ppt_case_pack.py \
  tests/test_ppt_run2_data_skill_quality.py \
  tests/test_ppt_case_pack_validator.py
git diff --cached --check
git commit -m "docs: add PPT run 2.7 data workflow contracts"
```

Expected:

```text
[codex/vulca-ppt-case-pack ...] docs: add PPT run 2.7 data workflow contracts
```

## Task 3: Add Generator Contract Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create: `scripts/generate_ppt_run2_7_data_workflow_arms.mjs`

- [ ] **Step 1: Add generator test**

Append this test after `test_run2_6r_generator_consumes_visual_repair_policy_and_preserves_boundaries`:

```python
def test_run2_7_generator_consumes_design_memory_and_preserves_control_boundaries() -> None:
    body = (ROOT / "scripts" / "generate_ppt_run2_7_data_workflow_arms.mjs").read_text(encoding="utf-8")
    arm_order = ["prompt_only", "run1_5_skill", "run2_7_full_skill", "bad_workflow_memory"]

    def arm_block(arm_id: str) -> str:
        start = body.index(f'armId: "{arm_id}"')
        next_starts = [body.find(f'armId: "{next_arm}"', start + 1) for next_arm in arm_order]
        next_starts = [index for index in next_starts if index > start]
        end = min(next_starts) if next_starts else body.index("function sequenceStepsForSlide", start)
        return body[start:end]

    def section(block: str, start_marker: str, end_marker: str) -> str:
        start = block.index(start_marker)
        end = block.index(end_marker, start)
        return block[start:end]

    restricted_run2_7_inputs = [
        "run2_7_commercial_usecase.json",
        "run2_7_multimodal_source_records.json",
        "run2_7_design_memory.json",
        "run2_7_workflow_policy.json",
    ]

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_7_full_skill",
            "bad_workflow_memory",
            "run2_7_commercial_usecase.json",
            "run2_7_multimodal_source_records.json",
            "run2_7_design_memory.json",
            "run2_7_workflow_policy.json",
            "renderRun27Full",
            "drawRun27Climax",
            "assertRun27MemorySelfCheck",
            "run27VisualSelfCheck",
            "run27Eligible",
            "run2_7_design_memory_ids",
            "run2_7_delta_from_run2_6r",
            "no_cross_arm_reuse",
        ],
    )
    prompt_allowed = section(arm_block("prompt_only"), "allowed:", "forbidden:")
    prompt_forbidden = section(arm_block("prompt_only"), "forbidden:", "palette:")
    run1_allowed = section(arm_block("run1_5_skill"), "allowed:", "forbidden:")
    run1_forbidden = section(arm_block("run1_5_skill"), "forbidden:", "palette:")
    full_allowed = section(arm_block("run2_7_full_skill"), "allowed:", "forbidden:")
    full_forbidden = section(arm_block("run2_7_full_skill"), "forbidden:", "palette:")
    bad_allowed = section(arm_block("bad_workflow_memory"), "allowed:", "forbidden:")
    bad_forbidden = section(arm_block("bad_workflow_memory"), "forbidden:", "palette:")

    for term in restricted_run2_7_inputs:
        assert term not in prompt_allowed
        assert term in prompt_forbidden
        assert term not in run1_allowed
        assert term in run1_forbidden
        assert term in full_allowed
        assert term not in full_forbidden

    assert "run2_7_commercial_usecase.json" in bad_allowed
    assert "run2_7_multimodal_source_records.json" in bad_allowed
    assert "run2_7_design_memory.json" not in bad_allowed
    assert "run2_7_workflow_policy.json" not in bad_allowed
    assert "run2_7_design_memory.json" in bad_forbidden
    assert "run2_7_workflow_policy.json" in bad_forbidden
    assert re.search(r"run2_7_usecase_id:\s*run27Eligible\s*\?", body)
    assert re.search(r"run2_7_source_record_ids:\s*run27Eligible\s*\?", body)
    assert re.search(r"run2_7_design_memory_ids:\s*fullRun27\s*\?", body)
    assert re.search(r"run2_7_workflow_decision_ids:\s*fullRun27\s*\?", body)
    assert re.search(r"run2_7_delta_from_run2_6r:\s*fullRun27\s*\?", body)
    assert re.search(r"run2_7_quality_gate:\s*fullRun27\s*\?", body)
```

- [ ] **Step 2: Create a generator placeholder to verify red state narrows**

Create `scripts/generate_ppt_run2_7_data_workflow_arms.mjs` with this minimal content:

```javascript
// Run 2.7 generator placeholder. Full implementation lands in Task 4.
console.log("run2_7_generator_placeholder");
```

- [ ] **Step 3: Run the generator contract test and verify it fails on missing arm definitions**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_7_generator_consumes_design_memory_and_preserves_control_boundaries -q
```

Expected:

```text
FAILED ... missing term: 'prompt_only'
```

## Task 4: Implement Run 2.7 Four-Arm Generator

**Files:**
- Modify: `scripts/generate_ppt_run2_7_data_workflow_arms.mjs`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Copy the Run 2.6R generator as the implementation base**

Run:

```bash
cp scripts/generate_ppt_run2_6r_visual_repair_arms.mjs scripts/generate_ppt_run2_7_data_workflow_arms.mjs
```

Then edit only `scripts/generate_ppt_run2_7_data_workflow_arms.mjs`.

- [ ] **Step 2: Replace Run 2.6R arm ids and slugs**

Replace these identifiers:

```text
run2_6r_visual_repair_full_skill -> run2_7_full_skill
bad_aesthetic_memory -> bad_workflow_memory
ppt-run2-6r-prompt-only -> ppt-run2-7-prompt-only
ppt-run2-6r-run1-5-skill -> ppt-run2-7-run1-5-skill
ppt-run2-6r-full-vulca -> ppt-run2-7-full-vulca
ppt-run2-6r-bad-aesthetic-memory -> ppt-run2-7-bad-workflow-memory
RUN 2.6R -> RUN 2.7
visual repair -> data workflow memory
```

- [ ] **Step 3: Add Run 2.7 data maps after `repairPolicyByRole`**

Insert:

```javascript
const run27SourceRecordsByRole = {
  cover: ["mm_2_7_design_system_launch_case", "mm_2_7_typography_hierarchy_tutorial", "mm_2_7_motion_demo_pacing_reference"],
  setup: ["mm_2_7_design_system_launch_case", "mm_2_7_spacing_editorial_grid_tutorial", "mm_2_7_motion_demo_pacing_reference"],
  contrast: ["mm_2_7_typography_hierarchy_tutorial", "mm_2_7_spacing_editorial_grid_tutorial", "mm_2_7_design_system_launch_case"],
  proof: ["mm_2_7_design_system_launch_case", "mm_2_7_product_surface_interaction_reference", "mm_2_7_spacing_editorial_grid_tutorial"],
  climax: ["mm_2_7_video_climax_single_object", "mm_2_7_product_surface_interaction_reference", "mm_2_7_typography_hierarchy_tutorial"],
  close: ["mm_2_7_design_system_launch_case", "mm_2_7_motion_demo_pacing_reference", "mm_2_7_spacing_editorial_grid_tutorial"],
};

const run27DesignMemoryByRole = {
  cover: ["memory_typography_editorial_launch", "memory_rhythm_six_slide_launch", "memory_source_brand_sanitization_v2"],
  setup: ["memory_spacing_climax_proof_grid", "memory_rhythm_six_slide_launch", "memory_source_brand_sanitization_v2"],
  contrast: ["memory_typography_editorial_launch", "memory_spacing_climax_proof_grid", "memory_rhythm_six_slide_launch"],
  proof: ["memory_spacing_climax_proof_grid", "memory_rhythm_six_slide_launch", "memory_source_brand_sanitization_v2"],
  climax: ["memory_composition_single_object_climax", "memory_typography_editorial_launch", "memory_source_brand_sanitization_v2"],
  close: ["memory_rhythm_six_slide_launch", "memory_spacing_climax_proof_grid", "memory_source_brand_sanitization_v2"],
};

const run27WorkflowDecisionByRole = {
  cover: ["decision_run2_7_select_real_usecase", "decision_run2_7_select_editorial_typography", "decision_run2_7_apply_brand_sanitization"],
  setup: ["decision_run2_7_select_setup_density", "decision_run2_7_select_spacing_zones", "decision_run2_7_apply_brand_sanitization"],
  contrast: ["decision_run2_7_select_before_after_delta", "decision_run2_7_select_editorial_typography", "decision_run2_7_select_spacing_zones"],
  proof: ["decision_run2_7_select_source_to_memory_route", "decision_run2_7_select_native_surface_route", "decision_run2_7_apply_brand_sanitization"],
  climax: ["decision_run2_7_select_single_object_climax", "decision_run2_7_select_editorial_typography", "decision_run2_7_apply_brand_sanitization"],
  close: ["decision_run2_7_select_release_gate", "decision_run2_7_select_spacing_zones", "decision_run2_7_apply_brand_sanitization"],
};

const run27DeltaByRole = {
  cover: "from Run 2.6R visual repair to real usecase plus selected typography memory",
  setup: "from selected policy display to selected source records and memory gates",
  contrast: "from repaired before-after spread to data-attributed before-after spread",
  proof: "from policy route to source-record -> memory -> workflow -> native PPT route",
  climax: "from editorial spread to one source-grounded native proof object",
  close: "from release handoff to data/workflow thickening gate",
};
```

- [ ] **Step 4: Replace arm allowed/forbidden boundaries**

For `prompt_only` and `run1_5_skill`, add these four forbidden inputs:

```javascript
"run2_7_commercial_usecase.json",
"run2_7_multimodal_source_records.json",
"run2_7_design_memory.json",
"run2_7_workflow_policy.json",
```

For `run2_7_full_skill`, add these allowed inputs:

```javascript
`${pack}/run2_7_commercial_usecase.json`,
`${pack}/run2_7_multimodal_source_records.json`,
`${pack}/run2_7_design_memory.json`,
`${pack}/run2_7_workflow_policy.json`,
```

For `bad_workflow_memory`, set allowed and forbidden boundaries so it can use the usecase and source records, but cannot use design memory or workflow policy:

```javascript
allowed: [
  `${pack}/commercial_case.md`,
  `${pack}/run2_7_commercial_usecase.json`,
  `${pack}/run2_7_multimodal_source_records.json`,
  `${pack}/sources.json`,
  `${pack}/multimodal_database.json`,
  `${pack}/visual_learning_targets.json`,
  `${pack}/visual_target_components.json`,
  `${pack}/video_demo_beat_map.json`,
  `${pack}/motion_learning_targets.json`,
  `${pack}/presentation_sequence_components.json`,
  `${pack}/source_cards/`,
  `${pack}/video_cards/`,
  `${pack}/evidence_memory.json`,
  `${pack}/asset_memory.json`,
  `${pack}/narrative_spine.json`,
  `${pack}/vulca_ppt_skill.md`,
  `${pack}/generation_briefs/bad_aesthetic_memory_replacement.json`,
],
forbidden: [
  `${pack}/run2_7_design_memory.json`,
  `${pack}/run2_7_workflow_policy.json`,
  `${pack}/aesthetic_benchmark_bank.json`,
  `${pack}/workflow_decision_policy.json`,
  `${pack}/visual_repair_policy.json`,
  `${pack}/aesthetic_memory.json`,
  `${pack}/aesthetic_memory_v2.json`,
  `${pack}/visual_production_modules.json`,
  `${pack}/slide_archetypes.json`,
  "docs/product/ppt-run1-5-product-lab/",
  "manual aesthetic repair before scoring",
],
```

- [ ] **Step 5: Add Run 2.7 drawing helpers before `renderControl`**

Insert:

```javascript
function memoryRail(slide, x, y, w, arm, labels) {
  labels.forEach((label, index) => {
    const itemW = (w - 24) / labels.length;
    const ix = x + index * itemW;
    rect(slide, ix, y, itemW - 10, 54, C.white, colorLine("#cfd6dd", 1));
    rect(slide, ix, y, 7, 54, index === labels.length - 1 ? arm.palette.proof : arm.palette.accent);
    text(slide, label[0], ix + 16, y + 9, itemW - 28, 14, { fontSize: 8, bold: true, mono: true, color: arm.palette.accent });
    text(slide, label[1], ix + 16, y + 27, itemW - 28, 18, { fontSize: 11, bold: true, title: true, color: arm.palette.title });
  });
}

function sourceStack(slide, x, y, w, h, arm, role) {
  rect(slide, x, y, w, h, "#f1f5f7", colorLine("#cfd6dd", 1));
  text(slide, "source records", x + 20, y + 18, w - 40, 16, { fontSize: 9, bold: true, mono: true, color: arm.palette.accent });
  (run27SourceRecordsByRole[role] ?? []).slice(0, 3).forEach((id, index) => {
    const cy = y + 56 + index * 44;
    rect(slide, x + 22, cy, 11, 11, index === 0 ? arm.palette.proof : arm.palette.accent2);
    text(slide, id.replace("mm_2_7_", ""), x + 44, cy - 5, w - 68, 25, { fontSize: 10, color: arm.palette.title });
  });
}

function workflowGate(slide, x, y, w, arm, role) {
  rect(slide, x, y, w, 104, "#172026", colorLine("#172026", 1));
  text(slide, "workflow gate", x + 20, y + 18, w - 40, 16, { fontSize: 9, bold: true, mono: true, color: "#d7eff2" });
  text(slide, (run27WorkflowDecisionByRole[role] ?? [])[0] ?? "decision_run2_7", x + 20, y + 44, w - 40, 34, {
    fontSize: 13,
    bold: true,
    title: true,
    color: C.white,
  });
  text(slide, "native + trace + public_blocked", x + 20, y + 82, w - 40, 18, { fontSize: 9, mono: true, color: "#d7eff2" });
}

function drawRun27Climax(slide, arm) {
  rect(slide, 54, 88, 1170, 542, arm.palette.bg, colorLine("#d8dde1", 1));
  text(slide, "Data becomes an editable proof object.", 84, 114, 610, 106, {
    fontSize: 50,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  text(slide, "The full arm selects source records, design memory, and workflow gates before drawing native PPT objects.", 88, 236, 545, 46, {
    fontSize: 15,
    color: arm.palette.muted,
  });
  const objectX = 454;
  const objectY = 160;
  const objectW = 520;
  const objectH = 340;
  rect(slide, objectX, objectY, objectW, objectH, C.white, colorLine(arm.palette.proof, 3));
  text(slide, "native proof object", objectX + 34, objectY + 28, 210, 18, {
    fontSize: 9,
    bold: true,
    mono: true,
    color: arm.palette.proof,
  });
  rect(slide, objectX + 42, objectY + 78, 146, 188, "#e7eef2", colorLine("#cfd6dd", 1));
  rect(slide, objectX + 208, objectY + 78, 116, 188, "#f1f5f7", colorLine("#cfd6dd", 1));
  rect(slide, objectX + 346, objectY + 78, 126, 188, arm.palette.proof);
  text(slide, "source", objectX + 60, objectY + 106, 88, 18, { fontSize: 10, bold: true, mono: true, color: arm.palette.accent });
  text(slide, "memory", objectX + 226, objectY + 106, 88, 18, { fontSize: 10, bold: true, mono: true, color: arm.palette.accent });
  text(slide, "PPT", objectX + 382, objectY + 106, 76, 18, { fontSize: 18, bold: true, title: true, color: C.white });
  rect(slide, objectX + 190, objectY + 164, 22, 8, arm.palette.proof);
  rect(slide, objectX + 324, objectY + 164, 22, 8, arm.palette.proof);
  text(slide, "40-55% canvas", objectX + 44, objectY + objectH - 54, objectW - 88, 26, {
    fontSize: 18,
    bold: true,
    title: true,
    color: arm.palette.title,
  });
  sourceStack(slide, 88, 326, 320, 174, arm, "climax");
  workflowGate(slide, 1018, 226, 150, arm, "climax");
  memoryRail(slide, 88, 540, 890, arm, [
    ["type", "editorial"],
    ["space", "zones"],
    ["climax", "single object"],
    ["brand", "sanitized"],
  ]);
}
```

- [ ] **Step 6: Replace `renderFullRepair` with `renderRun27Full`**

Rename the function to `renderRun27Full` and replace the cover/setup/proof/close content with Run 2.7 content. Keep `drawRun27Climax` as the climax branch.

The function must have this skeleton:

```javascript
function renderRun27Full(slide, spec, arm, n) {
  if (spec.role === "cover") {
    rect(slide, 0, 0, W, H, arm.palette.bg);
    text(slide, "Vulca", 72, 94, 300, 56, { fontSize: 30, bold: true, title: true, color: arm.palette.accent });
    text(slide, "Design memory becomes presentation code.", 72, 164, 760, 136, {
      fontSize: 58,
      bold: true,
      title: true,
      color: arm.palette.title,
    });
    text(slide, "Run 2.7 selects a real launch usecase, multimodal source records, design memory, and workflow gates before drawing native PPT.", 76, 324, 610, 68, {
      fontSize: 17,
      color: arm.palette.muted,
    });
    nativeMiniPreview(slide, 770, 126, 360, 316, arm, { title: "code-generated native slide surface" });
    memoryRail(slide, 76, 474, 640, arm, [
      ["usecase", "launch"],
      ["source", "multi-modal"],
      ["memory", "selected"],
      ["PPT", "native"],
    ]);
    editorialRule(slide, 76, 594, 606, arm);
    return;
  }
  if (spec.role === "climax") {
    drawRun27Climax(slide, arm);
    return;
  }
  simpleTitle(slide, spec, arm, true);
  if (spec.role === "setup") {
    sourceStack(slide, 82, 286, 330, 190, arm, "setup");
    memoryRail(slide, 470, 300, 500, arm, [
      ["spacing", "zones"],
      ["rhythm", "six slide"],
      ["brand", "safe"],
    ]);
    workflowGate(slide, 520, 410, 300, arm, "setup");
  } else if (spec.role === "contrast") {
    rect(slide, 82, 292, 390, 242, "#eef1f4", colorLine("#cfd6dd", 1));
    text(slide, "before / 2.6R repair", 110, 320, 210, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.muted });
    rect(slide, 560, 252, 540, 318, C.white, colorLine(arm.palette.proof, 3));
    text(slide, "after / data-attributed memory", 596, 288, 260, 18, { fontSize: 9, bold: true, mono: true, color: arm.palette.proof });
    materialPreview(slide, 624, 340, 316, 162, arm, "source -> memory -> generated output");
    rect(slide, 488, 402, 48, 10, arm.palette.proof);
    rect(slide, 526, 382, 20, 50, arm.palette.proof);
  } else if (spec.role === "proof") {
    const route = [
      ["usecase", "commercial job"],
      ["source", "records"],
      ["memory", "rules"],
      ["workflow", "gate"],
      ["PPT", "native"],
    ];
    route.forEach((item, index) => {
      const x = 82 + index * 218;
      selectedState(slide, item[0], item[1], x, 330 + (index % 2) * 76, 174, arm);
      if (index < route.length - 1) rect(slide, x + 184, 360 + (index % 2) * 76, 34, 4, arm.palette.proof);
    });
    sourceStack(slide, 84, 506, 360, 96, arm, "proof");
  } else {
    nativeMiniPreview(slide, 90, 292, 348, 238, arm, { title: "editable handoff surface" });
    selectedState(slide, "QA", "layout + trace pass", 506, 318, 254, arm);
    selectedState(slide, "Gate", "public blocked", 506, 398, 254, arm);
    selectedState(slide, "Next", "thicken data/workflow", 506, 478, 254, arm);
    workflowGate(slide, 834, 328, 250, arm, "close");
  }
}
```

- [ ] **Step 7: Update `renderSlide` dispatch**

Replace the Run 2.6R dispatch with:

```javascript
if (arm.armId === "run2_7_full_skill") {
  renderRun27Full(slide, spec, arm, n);
} else {
  renderControl(slide, spec, arm);
}
```

- [ ] **Step 8: Update `fullSlides` text**

Set `fullSlides` to:

```javascript
const fullSlides = [
  {
    role: "cover",
    title: "Design memory becomes presentation code.",
    claim: "Run 2.7 turns a real launch usecase, multimodal source records, and workflow gates into native PPT.",
    trace: "run2_7_commercial_usecase + source_records + design_memory + workflow_policy",
  },
  {
    role: "setup",
    title: "The workflow selects memory before drawing.",
    claim: "The deck chooses usecase, source records, typography, spacing, rhythm, and brand sanitization before generation.",
    trace: "run2_7_workflow_policy slide_role_memory_map",
  },
  {
    role: "contrast",
    title: "The after state is attributed.",
    claim: "Visual repair now has source records and design memory behind the changed composition.",
    trace: "run2_7_delta_from_run2_6r",
  },
  {
    role: "proof",
    title: "Source records route into native PPT.",
    claim: "The proof slide exposes usecase, data, memory, workflow gate, and editable output as one route.",
    trace: "run2_7_source_record_ids + run2_7_design_memory_ids",
  },
  {
    role: "climax",
    title: "Data becomes an editable proof object.",
    claim: "One native object makes the data-to-workflow-to-PPT transformation visible at thumbnail scale.",
    trace: "memory_composition_single_object_climax + native_climax_object_present",
  },
  {
    role: "close",
    title: "The result stays gated.",
    claim: "Run 2.7 can be used for internal demo proof, while public release remains blocked before human review.",
    trace: "run2_7_quality_gate + public_blocked",
  },
];
```

- [ ] **Step 9: Update `traceFor`**

Add these booleans near existing trace booleans:

```javascript
const run27Eligible = ["run2_7_full_skill", "bad_workflow_memory"].includes(arm.armId);
const fullRun27 = arm.armId === "run2_7_full_skill";
```

Inside each slide trace object, add:

```javascript
run2_7_usecase_id: run27Eligible ? "usecase_ai_design_to_production_platform_launch" : "",
run2_7_source_record_ids: run27Eligible ? run27SourceRecordsByRole[slide.role] ?? [] : [],
run2_7_design_memory_ids: fullRun27 ? run27DesignMemoryByRole[slide.role] ?? [] : [],
run2_7_workflow_decision_ids: fullRun27 ? run27WorkflowDecisionByRole[slide.role] ?? [] : [],
run2_7_delta_from_run2_6r: fullRun27 ? run27DeltaByRole[slide.role] ?? "" : "",
run2_7_quality_gate: fullRun27
  ? slide.role === "climax"
    ? "native_climax_object_present"
    : "run2_7_memory_trace_present"
  : "",
```

For Run 2.7, keep existing fields such as `commercial_usecase_id`, `visual_repair_policy_ids`, `source_brand_sanitization`, `native_ppt_checks`, and `layout_geometry_checks` populated for full arm.

- [ ] **Step 10: Add deterministic memory and visual self-checks**

Add this self-check block after `traceFor` and call `assertRun27MemorySelfCheck(traceFor(arm))` before writing each trace manifest:

```javascript
const run27VisualSelfCheck = {
  cover: ["headline_under_10_words", "memory_rail_visible", "native_surface_visible"],
  setup: ["source_stack_visible", "memory_selection_visible", "workflow_gate_visible"],
  contrast: ["before_after_delta_visible", "after_state_larger_than_before", "trace_not_only_footer"],
  proof: ["source_memory_workflow_route_visible", "native_output_surface_visible"],
  climax: ["single_native_object_40_55_canvas", "side_rail_secondary", "no_equal_card_grid"],
  close: ["public_blocked_gate_visible", "next_data_workflow_step_visible"],
};

function assertRun27MemorySelfCheck(trace) {
  if (trace.arm_id !== "run2_7_full_skill") return;
  for (const slide of trace.slides) {
    const role = slide.rhythm_role;
    if (!slide.run2_7_usecase_id) throw new Error(`Run 2.7 full slide ${slide.slide_id} missing usecase id`);
    if (!slide.run2_7_source_record_ids?.length) throw new Error(`Run 2.7 full slide ${slide.slide_id} missing source records`);
    if (!slide.run2_7_design_memory_ids?.length) throw new Error(`Run 2.7 full slide ${slide.slide_id} missing design memory`);
    if (!slide.run2_7_workflow_decision_ids?.length) throw new Error(`Run 2.7 full slide ${slide.slide_id} missing workflow decisions`);
    if (!run27VisualSelfCheck[role]?.length) throw new Error(`Run 2.7 full slide ${slide.slide_id} missing visual self-check rules`);
    if (role === "climax" && slide.run2_7_quality_gate !== "native_climax_object_present") {
      throw new Error(`Run 2.7 climax missing native climax quality gate`);
    }
  }
}
```

The self-check is not a substitute for Gemini artifact review. It blocks obvious generator mistakes before compile: missing selected memory, missing selected workflow, and missing climax gate.

- [ ] **Step 11: Update the output run summary**

At the end of the script, make the summary write these expected filenames and arm ids:

```javascript
run_id: "run2_7_data_workflow_thickening",
arms: ["prompt_only", "run1_5_skill", "run2_7_full_skill", "bad_workflow_memory"],
contact_sheet: "run2-7-four-arm-contact-sheet.png",
```

- [ ] **Step 12: Run syntax and contract checks**

Run:

```bash
node --check scripts/generate_ppt_run2_7_data_workflow_arms.mjs
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_7_generator_consumes_design_memory_and_preserves_control_boundaries -q
```

Expected:

```text
1 passed
```

- [ ] **Step 13: Commit generator contract and implementation**

Run:

```bash
git add scripts/generate_ppt_run2_7_data_workflow_arms.mjs tests/test_ppt_run2_data_skill_quality.py
git diff --cached --check
git commit -m "docs: add PPT run 2.7 four-arm generator"
```

Expected:

```text
[codex/vulca-ppt-case-pack ...] docs: add PPT run 2.7 four-arm generator
```

## Task 5: Rerun Four Arms, QA, And Two Required Images

**Files:**
- Generated untracked outputs under `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/run2_7_data_workflow_thickening_result.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/run2_7_data_workflow_thickening_result.md`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_7_visual_qa_gate.json`

- [ ] **Step 1: Run the generator**

Run:

```bash
THREAD_ID=019e7d9c-532a-70b3-8892-fa3ae42baef2 node scripts/generate_ppt_run2_7_data_workflow_arms.mjs
```

Expected output includes:

```text
ppt-run2-7-prompt-only
ppt-run2-7-run1-5-skill
ppt-run2-7-full-vulca
ppt-run2-7-bad-workflow-memory
```

- [ ] **Step 2: Build the four-arm contact sheet**

Run:

```bash
python3 scripts/build_ppt_contact_sheet.py \
  --root outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations \
  --slug ppt-run2-7-prompt-only \
  --slug ppt-run2-7-run1-5-skill \
  --slug ppt-run2-7-full-vulca \
  --slug ppt-run2-7-bad-workflow-memory \
  --output outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-7-four-arm-contact-sheet.png
```

Expected:

```text
outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-7-four-arm-contact-sheet.png
```

- [ ] **Step 3: Build the full-skill series sheet**

Run:

```bash
python3 scripts/build_ppt_full_skill_series_sheet.py \
  --root outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations \
  --slug ppt-run2-1-full-vulca \
  --slug ppt-run2-2-full-vulca \
  --slug ppt-run2-3-full-vulca \
  --slug ppt-run2-4-full-vulca \
  --slug ppt-run2-5-full-vulca \
  --slug ppt-run2-6-full-vulca \
  --slug ppt-run2-6r-full-vulca \
  --slug ppt-run2-7-full-vulca \
  --output outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png
```

Expected:

```text
outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png
```

- [ ] **Step 4: Run layout QA on all four arms**

Run:

```bash
for slug in ppt-run2-7-prompt-only ppt-run2-7-run1-5-skill ppt-run2-7-full-vulca ppt-run2-7-bad-workflow-memory; do
  python3 scripts/check_ppt_layout_quality.py \
    "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/layout/final" \
    --report "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/qa/layout-quality.txt"
done
```

Expected for every arm:

```text
layout_errors=0
layout_warnings=0
```

- [ ] **Step 5: Run delivery QA on all four PPTX files**

Run:

```bash
for slug in ppt-run2-7-prompt-only ppt-run2-7-run1-5-skill ppt-run2-7-full-vulca ppt-run2-7-bad-workflow-memory; do
  python3 scripts/validate_pptx_delivery.py \
    "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/output/${slug}.pptx" \
    --trace "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/qa/trace_manifest.json" \
    --output "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/${slug}/qa/delivery-qa.json"
done
```

Expected for every arm:

```text
internal-demo-ok-public-blocked
```

- [ ] **Step 6: Run trace QA**

Run:

```bash
python3 scripts/refresh_ppt_trace_qa.py \
  --contract docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json \
  --trace outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-7-full-vulca/qa/trace_manifest.json
```

Expected:

```text
trace_qa_status=pass
```

If the script writes a JSON report instead of terminal text, record the report path in the result JSON.

- [ ] **Step 7: Run native and arm-boundary guard**

Run this inline Python check:

```bash
python3 - <<'PY'
import json
import zipfile
from pathlib import Path

root = Path("outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations")
arms = {
    "ppt-run2-7-prompt-only": {"memory": False, "workflow": False, "usecase": False},
    "ppt-run2-7-run1-5-skill": {"memory": False, "workflow": False, "usecase": False},
    "ppt-run2-7-full-vulca": {"memory": True, "workflow": True, "usecase": True},
    "ppt-run2-7-bad-workflow-memory": {"memory": False, "workflow": False, "usecase": True},
}
for slug, expected in arms.items():
    trace = json.loads((root / slug / "qa" / "trace_manifest.json").read_text())
    allowed = "\n".join(trace["inputs_allowed"])
    forbidden = "\n".join(trace["inputs_forbidden"])
    isolation = json.dumps(trace["runtime_isolation"])
    assert "no_cross_arm_reuse" in isolation, slug
    assert "cached memory summaries" in isolation, slug
    assert ("run2_7_commercial_usecase.json" in allowed) is expected["usecase"], (slug, "allowed usecase")
    assert ("run2_7_design_memory.json" in allowed) is expected["memory"], (slug, "allowed memory")
    assert ("run2_7_workflow_policy.json" in allowed) is expected["workflow"], (slug, "allowed workflow")
    if not expected["memory"]:
        assert "run2_7_design_memory.json" in forbidden, (slug, "forbidden memory")
    if not expected["workflow"]:
        assert "run2_7_workflow_policy.json" in forbidden, (slug, "forbidden workflow")
    for slide in trace["slides"]:
        has_usecase = bool(slide["run2_7_usecase_id"])
        has_memory = bool(slide["run2_7_design_memory_ids"])
        has_workflow = bool(slide["run2_7_workflow_decision_ids"])
        assert has_usecase is expected["usecase"], (slug, slide["slide_id"], "usecase")
        assert has_memory is expected["memory"], (slug, slide["slide_id"], "memory")
        assert has_workflow is expected["workflow"], (slug, slide["slide_id"], "workflow")

full_pptx = root / "ppt-run2-7-full-vulca" / "output" / "ppt-run2-7-full-vulca.pptx"
with zipfile.ZipFile(full_pptx) as archive:
    names = archive.namelist()
    media = [name for name in names if name.startswith("ppt/media/")]
    slide_xml = [archive.read(name).decode("utf-8", errors="ignore") for name in names if name.startswith("ppt/slides/slide")]
    picture_count = sum(xml.count("<p:pic") for xml in slide_xml)
    shape_count = sum(xml.count("<p:sp") for xml in slide_xml)
assert media == [], media
assert picture_count == 0, picture_count
assert shape_count >= 60, shape_count
print({"media": len(media), "picture_count": picture_count, "shape_count": shape_count})
PY
```

Expected:

```text
{'media': 0, 'picture_count': 0, 'shape_count': <number >= 60>}
```

- [ ] **Step 8: Ask gemini-agent to review the two images**

Run artifact review for:

```text
outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-7-four-arm-contact-sheet.png
outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png
```

Prompt for the four-arm image:

```text
Review this Run 2.7 PPT four-arm contact sheet. Focus on whether the full arm visibly benefits from real usecase, multimodal source records, design memory, and workflow policy; whether bad workflow memory is a meaningful negative control; whether the full arm still looks like an engineering report; and whether the climax object is strong enough for a public demo candidate. Return concise findings and a 0-5 score for visual quality, data/workflow attribution, and public-video readiness.
```

Prompt for the full-skill series image:

```text
Review this full-skill series image from Run 2.1 through Run 2.7. Focus on whether Run 2.7 is a meaningful visual and workflow improvement after Run 2.6R, whether typography/spacing/climax composition improved, and whether the output is still public-blocked. Return concise findings and a 0-5 score for progression clarity and public-video readiness.
```

Expected: gemini-agent writes artifact review JSON files under `.gemini-agent/artifacts/`. Record the returned paths in the Run 2.7 result JSON.

- [ ] **Step 9: Create visual aesthetic QA gate from artifact reviews**

Run:

```bash
python3 - <<'PY'
import json
import re
from pathlib import Path

artifact_dir = Path(".gemini-agent/artifacts")
reviews = sorted(artifact_dir.glob("*artifacts.json"), key=lambda path: path.stat().st_mtime)[-2:]
assert len(reviews) == 2, "expected two latest Gemini artifact review files"

def body_for(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(data, ensure_ascii=False)

def first_score(text: str, label_patterns: list[str]) -> float:
    lowered = text.lower()
    for label in label_patterns:
        index = lowered.find(label)
        if index >= 0:
            window = lowered[index:index + 260]
            match = re.search(r"([0-5](?:\\.\\d+)?)\\s*/\\s*5|score[^0-9]*([0-5](?:\\.\\d+)?)", window)
            if match:
                return float(match.group(1) or match.group(2))
    return 0.0

texts = {str(path): body_for(path) for path in reviews}
combined = "\n".join(texts.values())
scores = {
    "visual_quality": first_score(combined, ["visual quality", "typography", "spacing"]),
    "data_workflow_attribution": first_score(combined, ["data/workflow attribution", "data workflow", "attribution"]),
    "public_video_readiness": first_score(combined, ["public-video readiness", "public video readiness", "public readiness"]),
    "progression_clarity": first_score(combined, ["progression clarity", "series"]),
}
thresholds = {
    "internal_demo_minimum": 3.0,
    "public_video_minimum": 4.0,
}
decision = "internal_demo_ok_public_blocked"
blocking_reasons = []
if scores["visual_quality"] < thresholds["internal_demo_minimum"]:
    blocking_reasons.append("visual_quality_below_internal_demo_threshold")
if scores["data_workflow_attribution"] < thresholds["internal_demo_minimum"]:
    blocking_reasons.append("data_workflow_attribution_below_internal_demo_threshold")
if scores["public_video_readiness"] < thresholds["public_video_minimum"]:
    blocking_reasons.append("public_video_readiness_below_public_threshold")
if scores["progression_clarity"] < thresholds["internal_demo_minimum"]:
    blocking_reasons.append("progression_clarity_below_internal_demo_threshold")
if blocking_reasons:
    decision = "public_blocked_visual_repair_required"

gate = {
    "schema_version": 1,
    "status": "run2_7_visual_qa_gate_public_blocked",
    "stage_policy": "repeat_same_five_layers_not_run3",
    "review_artifacts": [str(path) for path in reviews],
    "scores": scores,
    "thresholds": thresholds,
    "decision": decision,
    "blocking_reasons": blocking_reasons,
    "engineering_report_risk": "blocked unless Gemini review says the full arm is visually stronger than controls and not only a trace/report artifact",
    "public_release": "blocked until visual_quality, data_workflow_attribution, progression_clarity are at least 3.0 and public_video_readiness is at least 4.0 with human approval",
}
out = Path("docs/product/ppt-run2-data-skill-quality/results/run2_7_visual_qa_gate.json")
out.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"visual_gate": str(out), "decision": decision, "scores": scores}, indent=2))
PY
```

Expected:

```text
"visual_gate": "docs/product/ppt-run2-data-skill-quality/results/run2_7_visual_qa_gate.json"
```

This gate intentionally keeps public release blocked when Gemini scores are missing or below threshold. Missing numeric scores become `0.0`, which forces the next action back into visual repair rather than allowing a weak deck to pass.

## Task 6: Record Results, Compare, Verify, And Commit

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_7_data_workflow_thickening_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_7_data_workflow_thickening_result.md`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_7_visual_qa_gate.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`

- [ ] **Step 1: Add Run 2.7 result test**

Append this test after `test_run2_6_records_data_workflow_rerun_result` and the Run 2.6R result test:

```python
def test_run2_7_records_data_workflow_thickening_result() -> None:
    result = (PACK / "results" / "run2_7_data_workflow_thickening_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_7_data_workflow_thickening_result.json")
    visual_gate = load_json(PACK / "results" / "run2_7_visual_qa_gate.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_7_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert (
        result_json["rerun"]["best_internal_arm_verdict"]
        == "data_workflow_memory_visible_but_not_public_video_grade"
    )
    assert result_json["next_required_action"] == "keep_deepening_real_usecase_data_memory_workflow_and_native_ppt_quality"
    assert result_json["qa_summary"]["visual_aesthetic_gate"] == visual_gate["decision"]
    assert visual_gate["status"] == "run2_7_visual_qa_gate_public_blocked"
    assert visual_gate["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert visual_gate["public_release"].startswith("blocked")
    assert {"visual_quality", "data_workflow_attribution", "public_video_readiness", "progression_clarity"} <= set(
        visual_gate["scores"]
    )
    assert_contains(
        json.dumps(result_json["data_workflow_learning"]),
        [
            "run2_7_usecase_id",
            "run2_7_source_record_ids",
            "run2_7_design_memory_ids",
            "run2_7_workflow_decision_ids",
            "native_climax_object_present",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.7",
            "run2_7_commercial_usecase.json",
            "run2_7_multimodal_source_records.json",
            "run2_7_design_memory.json",
            "run2_7_workflow_policy.json",
            "run2_7_full_skill",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )
```

- [ ] **Step 2: Run the result test and verify it fails**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_7_records_data_workflow_thickening_result -q
```

Expected:

```text
FAILED ... FileNotFoundError: ... run2_7_data_workflow_thickening_result.md
```

- [ ] **Step 3: Create result JSON**

Create `docs/product/ppt-run2-data-skill-quality/results/run2_7_data_workflow_thickening_result.json`:

```json
{
  "schema_version": 1,
  "status": "rerun_completed_public_blocked",
  "public_ready": false,
  "stage_policy": "repeat_same_five_layers_not_run3",
  "rerun": {
    "status": "completed",
    "arms": [
      "prompt_only",
      "run1_5_skill",
      "run2_7_full_skill",
      "bad_workflow_memory"
    ],
    "best_internal_arm": "run2_7_full_skill",
    "best_internal_arm_verdict": "data_workflow_memory_visible_but_not_public_video_grade",
    "generated_outputs_committed": false,
    "four_arm_contact_sheet": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-7-four-arm-contact-sheet.png",
    "full_skill_series_sheet": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png"
  },
  "data_workflow_learning": [
    "run2_7_usecase_id present in full and bad-workflow arms",
    "run2_7_source_record_ids present in full and bad-workflow arms",
    "run2_7_design_memory_ids present only in full arm",
    "run2_7_workflow_decision_ids present only in full arm",
    "native_climax_object_present quality gate present only in full arm",
    "bad_workflow_memory proves source records alone are insufficient without selected design memory and workflow policy"
  ],
    "qa_summary": {
    "layout_errors": 0,
    "layout_warnings": 0,
    "delivery_gate": "internal-demo-ok-public-blocked",
    "native_full_arm_media_count": 0,
    "native_full_arm_picture_count": 0,
    "trace_qa": "pass",
    "visual_aesthetic_gate": "public_blocked_visual_repair_required",
    "visual_gate_result": "docs/product/ppt-run2-data-skill-quality/results/run2_7_visual_qa_gate.json"
  },
  "gemini_artifact_reviews": [],
  "remaining_gaps": [
    "still not public-video-grade without stronger editorial composition and human visual review",
    "source records are derived public-source observations, not full raw tutorial media storage",
    "animation and narrated video workflow remains represented as rhythm metadata rather than rendered motion"
  ],
  "next_required_action": "keep_deepening_real_usecase_data_memory_workflow_and_native_ppt_quality"
}
```

After Task 5, replace the empty `gemini_artifact_reviews` array with returned artifact review paths.
After Task 5, set `qa_summary.visual_aesthetic_gate` to the exact `decision` value from `run2_7_visual_qa_gate.json`.

- [ ] **Step 4: Create result Markdown**

Create `docs/product/ppt-run2-data-skill-quality/results/run2_7_data_workflow_thickening_result.md`:

```markdown
# Run 2.7 Data Workflow Thickening Result

Status: rerun_completed_public_blocked

Run 2.7 deepened the same five-layer loop. Do not advance to Run 3.0.

## What Changed

- Real usecase: `run2_7_commercial_usecase.json`
- Multimodal tutorial/case records: `run2_7_multimodal_source_records.json`
- Design memory: `run2_7_design_memory.json`
- Workflow policy: `run2_7_workflow_policy.json`
- Code-generated native PPT: `run2_7_full_skill`

## Four Arms

- `prompt_only`: commercial case only; no Run 2.7 data, memory, or workflow.
- `run1_5_skill`: prior workflow baseline; no Run 2.7 data, memory, or workflow.
- `run2_7_full_skill`: usecase + source records + design memory + workflow policy + native PPT.
- `bad_workflow_memory`: usecase + source records, but no design memory or workflow policy.

## Result

The best internal arm is `run2_7_full_skill`.

Verdict: data workflow memory visible but not public video grade.

Run 2.7 improves over Run 2.6R by making the visual repair attributable to selected source records, selected design memory, and selected workflow decisions. It remains public blocked because the output still needs human visual review, stronger editorial composition, and a rendered video/demo workflow before any public release claim.

## QA

- Layout QA: 0 errors, 0 warnings.
- Delivery QA: internal-demo-ok-public-blocked.
- Native full-arm guard: no media and no picture shapes.
- Trace QA: Run 2.7 fields present.
- Visual aesthetic gate: public blocked unless Gemini scores and human review pass.

## Required Images

- Four-arm contact sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-7-four-arm-contact-sheet.png`
- Full skill series: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

## Next Required Action

Keep deepening the same five layers: real usecase, higher-quality multimodal records, more specific design memory, stricter workflow, and more advanced native PPT composition.
```

- [ ] **Step 5: Update results index and comparison docs**

In `docs/product/ppt-run2-data-skill-quality/results/README.md`, add:

```markdown
- `run2_7_data_workflow_thickening_result.md` / `.json`: Run 2.7 same-loop thickening with real usecase, multimodal source records, design memory, workflow policy, and four-arm rerun.
```

In `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`, add a Run 2.7 section containing:

```markdown
## Run 2.7

Status: rerun-reviewed-public-blocked.

Best internal arm: `run2_7_full_skill`.

Run 2.7 adds `run2_7_commercial_usecase.json`, `run2_7_multimodal_source_records.json`, `run2_7_design_memory.json`, and `run2_7_workflow_policy.json`. The improvement is not just visual repair; it is data/workflow attribution made visible in the generated PPT. The negative control is `bad_workflow_memory`, which keeps the usecase and source records but blocks design memory and workflow policy.
```

In `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`, add:

```markdown
## Run 2.7 Delivery Gate

Run 2.7 is internal-demo-ok-public-blocked.

- Four-arm contact sheet: `run2-7-four-arm-contact-sheet.png`
- Full-skill series sheet: `run2-full-skill-series-horizontal.png`
- Full arm: `run2_7_full_skill`
- Negative control: `bad_workflow_memory`
- Required gate: human visual review before public release
```

- [ ] **Step 6: Run full focused verification**

Run:

```bash
python3 -m pytest \
  tests/test_ppt_run2_data_skill_quality.py \
  tests/test_ppt_case_pack_validator.py \
  tests/test_refresh_ppt_trace_qa.py \
  tests/test_pptx_delivery_validator.py \
  -q
```

Expected:

```text
passed
```

Run:

```bash
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
node --check scripts/generate_ppt_run2_7_data_workflow_arms.mjs
git diff --check
git ls-files outputs | wc -l
```

Expected:

```text
OK
0
```

The `git ls-files outputs | wc -l` command should return `0` or the existing tracked-output count. Do not commit generated PPTX, screenshots, previews, layout files, or contact sheets unless the repository already tracks that output class and the user explicitly requests it.

- [ ] **Step 7: Ask gemini-agent for diff review**

Send this prompt to `gemini-agent` diff review:

```text
Review the Run 2.7 data workflow thickening diff before commit. Focus on schema consistency, validator/test gaps, whether Run 2.7 genuinely connects real usecase -> multimodal source records -> design memory -> workflow policy -> code-generated native PPT, and whether control arms are isolated from full-arm memory/workflow. Flag any issue that would make the result look like a prompt-only or engineering-report deck instead of product-system learning.
```

Expected: no blocking issues. If Gemini flags a blocking issue, fix it and rerun focused verification before committing.

- [ ] **Step 8: Commit final Run 2.7 result**

Run:

```bash
git add \
  docs/product/ppt-run2-data-skill-quality/results/README.md \
  docs/product/ppt-run2-data-skill-quality/results/comparison_report.md \
  docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md \
  docs/product/ppt-run2-data-skill-quality/results/run2_7_visual_qa_gate.json \
  docs/product/ppt-run2-data-skill-quality/results/run2_7_data_workflow_thickening_result.json \
  docs/product/ppt-run2-data-skill-quality/results/run2_7_data_workflow_thickening_result.md \
  tests/test_ppt_run2_data_skill_quality.py
git diff --cached --check
git commit -m "docs: record PPT run 2.7 data workflow thickening"
```

Expected:

```text
[codex/vulca-ppt-case-pack ...] docs: record PPT run 2.7 data workflow thickening
```

## Final Verification Checklist

- [ ] `python3 -m pytest tests/test_ppt_run2_data_skill_quality.py tests/test_ppt_case_pack_validator.py tests/test_refresh_ppt_trace_qa.py tests/test_pptx_delivery_validator.py -q` passes.
- [ ] `python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality` prints `OK`.
- [ ] `node --check scripts/generate_ppt_run2_7_data_workflow_arms.mjs` passes.
- [ ] Run 2.7 full arm trace includes non-empty `run2_7_design_memory_ids` and `run2_7_workflow_decision_ids`.
- [ ] Prompt-only and Run 1.5 arms have empty Run 2.7 fields.
- [ ] Bad workflow memory arm has usecase/source records but empty design memory/workflow decisions.
- [ ] Full arm PPTX has no `ppt/media/` entries and no `<p:pic>` shapes.
- [ ] Both required images exist:
  - `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-7-four-arm-contact-sheet.png`
  - `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`
- [ ] Gemini artifact review paths are recorded in `run2_7_data_workflow_thickening_result.json`.
- [ ] `docs/product/ppt-run2-data-skill-quality/results/run2_7_visual_qa_gate.json` exists and its `decision` is copied into the Run 2.7 result JSON.
- [ ] Generated outputs remain untracked unless the user explicitly requests output commits.

## Self-Review

Spec coverage:
- Real usecase is implemented in Task 2 via `run2_7_commercial_usecase.json`.
- Multimodal tutorial/case database is implemented in Task 2 via `run2_7_multimodal_source_records.json`.
- Design memory is implemented in Task 2 via `run2_7_design_memory.json`.
- Skill workflow is implemented in Task 2 via `run2_7_workflow_policy.json`, `skill_workflow.json`, and trace contract updates.
- Code-generated native PPT is implemented in Tasks 3-5 via the Run 2.7 four-arm generator, native guard, and visual contact sheets.
- Baseline and negative-control comparison is preserved through prompt-only, Run 1.5, Run 2.7 full, and bad workflow memory arms.
- Public release remains blocked through result docs, delivery gate, trace contract, validator rules, and QA steps.
- Gemini plan critique concerns are addressed by generator self-check, trace arm-leakage checks, and a visual aesthetic gate based on artifact-review scores.

Placeholder scan:
- This plan avoids placeholder terms and gives concrete file paths, ids, JSON bodies, test names, commands, expected outputs, and commit messages.

Type consistency:
- Run 2.7 field names are consistent across tests, JSON artifacts, validator functions, generator trace fields, and result docs:
  - `run2_7_usecase_id`
  - `run2_7_source_record_ids`
  - `run2_7_design_memory_ids`
  - `run2_7_workflow_decision_ids`
  - `run2_7_delta_from_run2_6r`
  - `run2_7_quality_gate`
