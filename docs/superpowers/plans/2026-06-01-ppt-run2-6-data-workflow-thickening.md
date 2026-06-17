# PPT Run 2.6 Data Workflow Thickening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Run 2.6 data/workflow artifacts that make commercial usecase, aesthetic benchmark, theme, typography, and spacing selection executable before the next PPT rerun.

**Architecture:** Implement Run 2.6 in two verified commits. The first commit adds data banks, workflow policy, workflow stages, trace contract fields, and tests. The second commit adds the Run 2.6 generator, reruns the four arms, refreshes QA, creates the two mandatory comparison images, and records public-blocked results.

**Tech Stack:** Python stdlib JSON tests, pytest, ruff, Node.js artifact-tool generator, existing PPT layout/delivery QA scripts, Gemini-agent review, local untracked `outputs/` artifacts.

---

## File Map

First commit, data/workflow:

- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Modify: `docs/product/ppt-run2-data-skill-quality/sources.json`
- Create: `docs/product/ppt-run2-data-skill-quality/commercial_usecase_bank.json`
- Create: `docs/product/ppt-run2-data-skill-quality/aesthetic_benchmark_bank.json`
- Create: `docs/product/ppt-run2-data-skill-quality/workflow_decision_policy.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`

Second commit, rerun:

- Create: `scripts/generate_ppt_run2_6_arms.mjs`
- Create: `scripts/build_ppt_full_skill_series_sheet.py` for the mandatory Run 2.0-2.6 full-skill-series comparison image.
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_6_rerun_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_6_rerun_result.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`

Generated artifacts remain untracked:

- `outputs/<thread-id>/presentations/ppt-run2-6-prompt-only/`
- `outputs/<thread-id>/presentations/ppt-run2-6-run1-5-skill/`
- `outputs/<thread-id>/presentations/ppt-run2-6-full-vulca/`
- `outputs/<thread-id>/presentations/ppt-run2-6-bad-aesthetic-memory/`
- `outputs/<thread-id>/presentations/run2-6-four-arm-contact-sheet.png`
- `outputs/<thread-id>/presentations/run2-full-skill-series-horizontal.png`

---

### Task 1: Add Failing Tests For Run 2.6 Data Banks

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add expected constants**

Add these constants near the existing Run 2.5 expected constants:

```python
EXPECTED_RUN2_6_SOURCE_IDS = {
    "figma_config_2025_platform_launch",
    "figma_config_2025_recap",
    "figma_slides_product",
    "figma_slides_help",
    "stripe_sessions_2025_product_keynote",
    "google_cloud_next_2025_wrap",
    "google_cloud_next_2025_sundar",
    "apple_liquid_glass_newsroom",
    "apple_liquid_glass_developer",
    "duarte_slide_design",
    "duarte_visual_storytelling",
    "slidemodel_visual_hierarchy",
}
EXPECTED_RUN2_6_USECASE_IDS = {
    "usecase_design_to_production_platform_launch",
    "usecase_fintech_product_keynote",
    "usecase_ai_cloud_keynote_demo",
    "usecase_design_language_public_reveal",
}
EXPECTED_RUN2_6_BENCHMARK_IDS = {
    "benchmark_design_to_production_grid_precision",
    "benchmark_visual_fidelity_interactive_slide_surface",
    "benchmark_fintech_keynote_breadth_without_grid",
    "benchmark_ai_platform_demo_climax",
    "benchmark_content_first_dynamic_material",
    "benchmark_glance_test_visual_hierarchy",
    "benchmark_story_driven_data_emphasis",
}
EXPECTED_RUN2_6_TRACE_FIELDS = {
    "commercial_usecase_id",
    "aesthetic_benchmark_ids",
    "theme_policy_id",
    "typography_system_id",
    "spacing_token_set_id",
    "workflow_decision_ids",
    "source_brand_sanitization",
    "benchmark_validation_probe",
    "theme_validation_probe",
}
EXPECTED_RUN2_6_USECASE_FIELDS = {
    "id",
    "source_ids",
    "audience",
    "business_decision",
    "deck_mission",
    "slide_arc",
    "must_show",
    "must_not_show",
    "failure_modes",
    "visual_risk",
    "workflow_implications",
    "qa_probe",
    "release_boundary",
}
EXPECTED_RUN2_6_BENCHMARK_FIELDS = {
    "id",
    "source_ids",
    "allowed_use",
    "composition_rules",
    "typography_rules",
    "spacing_rules",
    "theme_rules",
    "motion_or_interaction_rules",
    "native_ppt_implications",
    "anti_copy_rules",
    "qa_probe",
    "trace_fields",
    "release_boundary",
}
```

- [ ] **Step 2: Add failing source/usecase bank test**

Append this test after the existing Run 2.5 data tests:

```python
def test_run2_6_has_commercial_usecase_bank() -> None:
    sources = load_json(PACK / "sources.json")
    usecases = load_json(PACK / "commercial_usecase_bank.json")
    source_ids = {source["id"] for source in sources["sources"]}

    assert EXPECTED_RUN2_6_SOURCE_IDS <= source_ids
    assert usecases["status"] == "run2_6_commercial_usecase_bank_public_blocked"
    assert usecases["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert usecases["storage_policy"]["raw_media"] == "forbidden"
    assert EXPECTED_RUN2_6_USECASE_IDS <= {item["id"] for item in usecases["usecases"]}

    for item in usecases["usecases"]:
        assert EXPECTED_RUN2_6_USECASE_FIELDS <= set(item), item["id"]
        assert set(item["source_ids"]) <= source_ids
        assert_contains(" ".join(item["must_not_show"]), ["copy", "brand"])
        assert_contains(" ".join(item["workflow_implications"]), ["select", "benchmark"])
        assert_contains(item["qa_probe"], ["contact sheet"])
        assert_contains(item["release_boundary"], ["public_blocked"])
```

- [ ] **Step 3: Add failing aesthetic benchmark bank test**

Append:

```python
def test_run2_6_has_aesthetic_benchmark_bank() -> None:
    sources = load_json(PACK / "sources.json")
    benchmarks = load_json(PACK / "aesthetic_benchmark_bank.json")
    source_ids = {source["id"] for source in sources["sources"]}

    assert benchmarks["status"] == "run2_6_aesthetic_benchmark_bank_public_blocked"
    assert benchmarks["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert benchmarks["storage_policy"]["raw_media"] == "forbidden"
    assert EXPECTED_RUN2_6_BENCHMARK_IDS <= {item["id"] for item in benchmarks["benchmarks"]}

    for item in benchmarks["benchmarks"]:
        assert EXPECTED_RUN2_6_BENCHMARK_FIELDS <= set(item), item["id"]
        assert set(item["source_ids"]) <= source_ids
        assert item["allowed_use"] == "derived_rules_only"
        assert_contains(" ".join(item["composition_rules"]), ["native"])
        assert_contains(" ".join(item["typography_rules"]), ["hierarchy"])
        assert_contains(" ".join(item["spacing_rules"]), ["spacing"])
        assert_contains(" ".join(item["anti_copy_rules"]), ["do not copy"])
        assert EXPECTED_RUN2_6_TRACE_FIELDS & set(item["trace_fields"])
        assert_contains(item["release_boundary"], ["public_blocked"])
```

- [ ] **Step 4: Run tests and verify failure**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_6_has_commercial_usecase_bank tests/test_ppt_run2_data_skill_quality.py::test_run2_6_has_aesthetic_benchmark_bank -q
```

Expected: fail because `commercial_usecase_bank.json` and `aesthetic_benchmark_bank.json` do not exist yet.

---

### Task 2: Add Run 2.6 Sources And Data Banks

**Files:**
- Modify: `docs/product/ppt-run2-data-skill-quality/sources.json`
- Create: `docs/product/ppt-run2-data-skill-quality/commercial_usecase_bank.json`
- Create: `docs/product/ppt-run2-data-skill-quality/aesthetic_benchmark_bank.json`

- [ ] **Step 1: Extend `sources.json`**

Add source records with these ids, URLs, and roles:

```json
[
  {
    "id": "figma_config_2025_platform_launch",
    "title": "Config 2025 launches deepen Figma's design capabilities as its platform expands",
    "url": "https://www.figma.com/blog/config-2025-press-release/",
    "role": "design_to_production_platform_launch_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy visuals, layouts, screenshots, brand marks, source prose, template files, or proprietary assets."
  },
  {
    "id": "figma_config_2025_recap",
    "title": "Config 2025: Pushing Design Further",
    "url": "https://www.figma.com/blog/config-2025-recap/",
    "role": "craft_grid_design_to_production_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy visuals, layouts, screenshots, brand marks, source prose, template files, or proprietary assets."
  },
  {
    "id": "figma_slides_product",
    "title": "Figma Slides",
    "url": "https://www.figma.com/slides/",
    "role": "presentation_product_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy visuals, layouts, screenshots, brand marks, source prose, template files, or proprietary assets."
  },
  {
    "id": "figma_slides_help",
    "title": "Explore Figma Slides",
    "url": "https://help.figma.com/hc/en-us/articles/24170630629911-Explore-Figma-Slides",
    "role": "presentation_workflow_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy visuals, layouts, screenshots, brand marks, source prose, template files, or proprietary assets."
  },
  {
    "id": "stripe_sessions_2025_product_keynote",
    "title": "Stripe Sessions 2025 Product Keynote",
    "url": "https://stripe.com/gb/sessions/2025/product-keynote",
    "role": "fintech_product_keynote_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy visuals, layouts, screenshots, brand marks, transcript text, event graphics, or proprietary assets."
  },
  {
    "id": "google_cloud_next_2025_wrap",
    "title": "Google Cloud Next 2025 Wrap Up",
    "url": "https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2025-wrap-up/?hl=en",
    "role": "large_scale_ai_cloud_keynote_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy visuals, layouts, screenshots, brand marks, transcript text, event graphics, or proprietary assets."
  },
  {
    "id": "google_cloud_next_2025_sundar",
    "title": "Google Cloud Next 25: New AI capabilities to transform your business",
    "url": "https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/google-cloud-next-2025-sundar-pichai-keynote/",
    "role": "executive_ai_platform_keynote_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy visuals, layouts, screenshots, brand marks, transcript text, event graphics, or proprietary assets."
  },
  {
    "id": "apple_liquid_glass_newsroom",
    "title": "Apple introduces a delightful and elegant new software design",
    "url": "https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/",
    "role": "design_language_launch_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy visuals, layouts, screenshots, brand marks, source prose, video frames, or proprietary design assets."
  },
  {
    "id": "apple_liquid_glass_developer",
    "title": "Meet Liquid Glass",
    "url": "https://developer.apple.com/videos/play/wwdc2025/219/",
    "role": "design_language_principles_video_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy visuals, layouts, screenshots, brand marks, source prose, video frames, audio, or transcripts."
  },
  {
    "id": "duarte_slide_design",
    "title": "Presentation Design Training",
    "url": "https://www.duarte.com/training/slide-document-design/slide-design/",
    "role": "slide_design_training_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy course lessons, visuals, layouts, screenshots, brand marks, exercise files, full prose, transcripts, audio, or video frames."
  },
  {
    "id": "duarte_visual_storytelling",
    "title": "Persuasive Visual Storytelling",
    "url": "https://www.duarte.com/resources/webinars-videos/persuasive-visual-storytelling/",
    "role": "visual_storytelling_training_reference",
    "accessed_on": "2026-06-01",
    "allowed_use": "reference_analysis_only",
    "copyright_note": "Original analysis only; do not copy webinar materials, visuals, layouts, screenshots, brand marks, full prose, transcripts, audio, or video frames."
  }
]
```

Keep existing source ids; do not delete previous Run 2.0-2.5 references.

- [ ] **Step 2: Create `commercial_usecase_bank.json`**

Create a JSON object:

```json
{
  "schema_version": 1,
  "status": "run2_6_commercial_usecase_bank_public_blocked",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "storage_policy": {
    "raw_media": "forbidden",
    "allowed_storage": "derived_observations_only",
    "forbidden_storage": ["screenshots", "video frames", "audio", "full transcripts", "copied layouts", "brand marks", "template files", "long source prose"]
  },
  "usecases": [
    {
      "id": "usecase_design_to_production_platform_launch",
      "source_ids": ["figma_config_2025_platform_launch", "figma_config_2025_recap", "figma_slides_product", "figma_slides_help"],
      "audience": "AI product builders and design-led founders evaluating whether Vulca can turn design memory into production-grade code-generated PPT.",
      "business_decision": "Should the team position Vulca as a design-to-production presentation workflow rather than a prompt-only slide generator?",
      "deck_mission": "Show that the product selects data, memory, modules, and QA gates before writing slide code.",
      "slide_arc": ["designed opening", "workflow selection", "before/after delta", "proof route", "hero result", "release gate"],
      "must_show": ["usecase selection before generation", "visual benchmark selection", "native editable module output", "traceable release boundary"],
      "must_not_show": ["do not copy Figma brand visuals", "do not copy Figma product UI", "do not become a feature grid"],
      "failure_modes": ["looks like an engineering report", "lists capabilities without visual proof", "uses generic SaaS dashboard cards"],
      "visual_risk": "Can drift into Figma-like branding or generic product grid if source-brand sanitization is weak.",
      "workflow_implications": ["select benchmark_design_to_production_grid_precision", "select benchmark_visual_fidelity_interactive_slide_surface", "select theme and spacing policy before production modules"],
      "qa_probe": "From the contact sheet, the full arm should read as a designed workflow product, not a source-brand imitation or report.",
      "release_boundary": "public_blocked_until_native_render_human_approval_and_source_brand_sanitization"
    }
  ]
}
```

Add the remaining three usecases with the same required fields:

- `usecase_fintech_product_keynote`, sources `["stripe_sessions_2025_product_keynote"]`, must avoid feature-grid sprawl.
- `usecase_ai_cloud_keynote_demo`, sources `["google_cloud_next_2025_wrap", "google_cloud_next_2025_sundar"]`, must preserve demo/climax scale.
- `usecase_design_language_public_reveal`, sources `["apple_liquid_glass_newsroom", "apple_liquid_glass_developer"]`, must make design language the proof object while forbidding Apple-like output.

- [ ] **Step 3: Create `aesthetic_benchmark_bank.json`**

Create a JSON object:

```json
{
  "schema_version": 1,
  "status": "run2_6_aesthetic_benchmark_bank_public_blocked",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "storage_policy": {
    "raw_media": "forbidden",
    "allowed_storage": "derived_observations_only",
    "forbidden_storage": ["screenshots", "video frames", "audio", "full transcripts", "copied layouts", "brand marks", "template files", "long source prose"]
  },
  "benchmarks": [
    {
      "id": "benchmark_design_to_production_grid_precision",
      "source_ids": ["figma_config_2025_recap"],
      "allowed_use": "derived_rules_only",
      "composition_rules": ["Use native grid discipline as an invisible structure; the generated slide must not expose a generic equal-card grid.", "Place the focal object on a deliberate grid span and keep support objects subordinate."],
      "typography_rules": ["Use hierarchy to separate product promise, proof object, and support labels.", "Avoid tiny implementation labels unless routed to trace."],
      "spacing_rules": ["Use margin and gutter tokens before module generation.", "Whitespace must support focal scale instead of acting as decoration."],
      "theme_rules": ["Do not copy Figma colors or event identity.", "Generate an original theme policy with light and dark variants."],
      "motion_or_interaction_rules": ["If interaction is referenced, convert it into ordered native reveal steps, not copied UI behavior."],
      "native_ppt_implications": ["Require editable grid-aligned shape groups.", "Trace theme_policy_id, typography_system_id, and spacing_token_set_id."],
      "anti_copy_rules": ["Do not copy source layouts, screenshots, brand marks, product UI, event graphics, or exact color systems."],
      "qa_probe": "The contact sheet should show precise alignment and focal hierarchy without source-brand resemblance.",
      "trace_fields": ["aesthetic_benchmark_ids", "theme_policy_id", "typography_system_id", "spacing_token_set_id"],
      "release_boundary": "public_blocked_until_native_render_human_approval_and_source_brand_sanitization"
    }
  ]
}
```

Add the remaining six benchmark records with the same fields and ids from `EXPECTED_RUN2_6_BENCHMARK_IDS`. Every record must include at least one trace field from `EXPECTED_RUN2_6_TRACE_FIELDS`.

- [ ] **Step 4: Run tests and verify pass**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_6_has_commercial_usecase_bank tests/test_ppt_run2_data_skill_quality.py::test_run2_6_has_aesthetic_benchmark_bank -q
```

Expected: both tests pass.

---

### Task 3: Add Workflow Policy, Workflow Stages, And Trace Contract Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create: `docs/product/ppt-run2-data-skill-quality/workflow_decision_policy.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json`

- [ ] **Step 1: Add failing workflow policy test**

Append:

```python
def test_run2_6_has_workflow_decision_policy_and_trace_contract() -> None:
    usecases = load_json(PACK / "commercial_usecase_bank.json")
    benchmarks = load_json(PACK / "aesthetic_benchmark_bank.json")
    policy = load_json(PACK / "workflow_decision_policy.json")
    workflow = load_json(PACK / "skill_workflow.json")
    trace_contract = load_json(PACK / "results" / "trace_manifest_contract.json")

    usecase_ids = {item["id"] for item in usecases["usecases"]}
    benchmark_ids = {item["id"] for item in benchmarks["benchmarks"]}

    assert policy["status"] == "run2_6_workflow_decision_policy_public_blocked"
    assert policy["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert set(policy["selection_chain"]) == {
        "commercial_case",
        "usecase_id",
        "benchmark_ids",
        "theme_policy_id",
        "typography_system_id",
        "spacing_token_set_id",
        "visual_production_module_ids",
        "qa_probes",
    }
    for mapping in policy["usecase_benchmark_map"]:
        assert mapping["usecase_id"] in usecase_ids
        assert set(mapping["benchmark_ids"]) <= benchmark_ids
        assert mapping["theme_policy_id"]
        assert mapping["typography_system_id"]
        assert mapping["spacing_token_set_id"]
        assert_contains(" ".join(mapping["source_brand_sanitization"]), ["do not copy"])

    workflow_stage_ids = {stage["id"] for stage in workflow["stages"]}
    assert {
        "select_commercial_usecase",
        "select_aesthetic_benchmarks",
        "select_theme_typography_spacing_policy",
    } <= workflow_stage_ids
    assert EXPECTED_RUN2_6_TRACE_FIELDS <= set(trace_contract["per_slide_required_fields"])
```

- [ ] **Step 2: Run test and verify failure**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_6_has_workflow_decision_policy_and_trace_contract -q
```

Expected: fail because `workflow_decision_policy.json` and trace additions do not exist yet.

- [ ] **Step 3: Create `workflow_decision_policy.json`**

Create:

```json
{
  "schema_version": 1,
  "status": "run2_6_workflow_decision_policy_public_blocked",
  "stage_policy": "repeat_same_five_layers_not_run3",
  "selection_chain": ["commercial_case", "usecase_id", "benchmark_ids", "theme_policy_id", "typography_system_id", "spacing_token_set_id", "visual_production_module_ids", "qa_probes"],
  "usecase_benchmark_map": [
    {
      "usecase_id": "usecase_design_to_production_platform_launch",
      "benchmark_ids": ["benchmark_design_to_production_grid_precision", "benchmark_visual_fidelity_interactive_slide_surface", "benchmark_glance_test_visual_hierarchy"],
      "theme_policy_id": "theme_original_high_contrast_product_system",
      "typography_system_id": "type_system_editorial_product_sans",
      "spacing_token_set_id": "spacing_tokens_precision_grid_12",
      "visual_production_module_ids": ["module_cinematic_cover_field", "module_system_mini_preview", "module_editorial_before_after_delta", "module_proof_route_choreography", "module_climax_hero_object", "module_release_handoff_gate"],
      "source_brand_sanitization": ["do not copy Figma brand marks", "do not copy Figma UI", "do not use source event colors as identity"],
      "fallback_policy": "public_blocked_if_theme_or_spacing_policy_is_not_visible",
      "qa_probes": ["contact sheet shows product workflow before code", "full arm does not resemble source brand"]
    }
  ],
  "theme_policies": [
    {
      "id": "theme_original_high_contrast_product_system",
      "mode_support": ["dark", "light"],
      "rules": ["use original palette", "preserve text contrast", "forbid source-brand color cloning"],
      "qa_probe": "Theme should read as Vulca/product-system original, not a reference brand."
    }
  ],
  "typography_systems": [
    {
      "id": "type_system_editorial_product_sans",
      "rules": ["headline at least 2.6x support label size", "body lines stay short", "tiny trace labels stay out of main slide"],
      "qa_probe": "Contact sheet headline should be readable before support labels."
    }
  ],
  "spacing_token_sets": [
    {
      "id": "spacing_tokens_precision_grid_12",
      "rules": ["outer margin >= 54px", "module gutters >= 24px", "focal object has larger margin than support objects"],
      "qa_probe": "Focal object should not feel crowded or accidental."
    }
  ]
}
```

Add exactly three additional mappings for the other usecases. Keep every mapping source-brand sanitized and public-blocked:

- `usecase_fintech_product_keynote`: benchmarks `benchmark_fintech_product_keynote_breadth_without_grid`, `benchmark_story_driven_data_emphasis`, `benchmark_glance_test_visual_hierarchy`; theme `theme_original_fintech_keynote_contrast`; typography `type_system_keynote_product_sans`; spacing `spacing_tokens_keynote_asymmetric`.
- `usecase_ai_cloud_keynote_demo`: benchmarks `benchmark_ai_platform_demo_climax`, `benchmark_story_driven_data_emphasis`, `benchmark_glance_test_visual_hierarchy`; theme `theme_original_ai_demo_scale`; typography `type_system_demo_narrative_sans`; spacing `spacing_tokens_demo_stage_depth`.
- `usecase_design_language_public_reveal`: benchmarks `benchmark_content_first_dynamic_material`, `benchmark_visual_fidelity_interactive_slide_surface`, `benchmark_glance_test_visual_hierarchy`; theme `theme_original_material_language_neutral`; typography `type_system_design_language_editorial`; spacing `spacing_tokens_layered_material`.

Add matching records for all referenced `theme_policy_id`, `typography_system_id`, and `spacing_token_set_id` values under `theme_policies`, `typography_systems`, and `spacing_token_sets`.

- [ ] **Step 4: Update `skill_workflow.json`**

Insert three stages before `select_visual_production_modules`:

```json
{
  "id": "select_commercial_usecase",
  "order": 8,
  "layer": "skill_workflow",
  "inputs": ["commercial_case.md", "commercial_usecase_bank.json"],
  "outputs": ["commercial_usecase_id", "usecase slide arc", "usecase QA probe"],
  "gates": ["selected usecase references valid sources", "selected usecase is concrete", "source-brand imitation remains forbidden"]
}
```

Then add `select_aesthetic_benchmarks` and `select_theme_typography_spacing_policy` with the inputs/outputs/gates from the spec. Increment later stage `order` values so orders stay strictly increasing.

- [ ] **Step 5: Update trace manifest contract**

Append these values to `per_slide_required_fields` in `trace_manifest_contract.json`:

```json
"commercial_usecase_id",
"aesthetic_benchmark_ids",
"theme_policy_id",
"typography_system_id",
"spacing_token_set_id",
"workflow_decision_ids",
"source_brand_sanitization",
"benchmark_validation_probe",
"theme_validation_probe"
```

- [ ] **Step 6: Run workflow policy test and full data test**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
ruff check tests/test_ppt_run2_data_skill_quality.py
```

Expected: tests pass, case pack ok, ruff ok.

- [ ] **Step 7: Commit data/workflow**

Run:

```bash
git add tests/test_ppt_run2_data_skill_quality.py docs/product/ppt-run2-data-skill-quality/sources.json docs/product/ppt-run2-data-skill-quality/commercial_usecase_bank.json docs/product/ppt-run2-data-skill-quality/aesthetic_benchmark_bank.json docs/product/ppt-run2-data-skill-quality/workflow_decision_policy.json docs/product/ppt-run2-data-skill-quality/skill_workflow.json docs/product/ppt-run2-data-skill-quality/results/trace_manifest_contract.json
git commit -m "docs: add PPT run 2.6 data workflow"
```

---

### Task 4: Add Run 2.6 Generator Contract Tests

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create later: `scripts/generate_ppt_run2_6_arms.mjs`

- [ ] **Step 1: Add failing generator source test**

Append:

```python
def test_run2_6_generator_consumes_workflow_policy_and_preserves_control_boundaries() -> None:
    body = (ROOT / "scripts" / "generate_ppt_run2_6_arms.mjs").read_text(encoding="utf-8")

    assert_contains(
        body,
        [
            "prompt_only",
            "run1_5_skill",
            "run2_6_full_skill",
            "bad_aesthetic_memory",
            "commercial_usecase_bank.json",
            "aesthetic_benchmark_bank.json",
            "workflow_decision_policy.json",
            "source_brand_sanitization",
            "no_cross_arm_reuse",
        ],
    )
    assert 'const workflowEligible = ["run2_6_full_skill", "bad_aesthetic_memory"].includes(arm.armId);' in body
    assert 'const fullWorkflow = arm.armId === "run2_6_full_skill";' in body
    assert re.search(r"commercial_usecase_id:\s*workflowEligible\s*\\?", body)
    assert re.search(r"aesthetic_benchmark_ids:\s*fullWorkflow\s*\\?", body)
    assert re.search(r"theme_policy_id:\s*fullWorkflow\s*\\?", body)
    assert re.search(r"typography_system_id:\s*fullWorkflow\s*\\?", body)
    assert re.search(r"spacing_token_set_id:\s*fullWorkflow\s*\\?", body)
    assert re.search(r"workflow_decision_ids:\s*fullWorkflow\s*\\?", body)
    assert "source_brand_sanitization:" in body
```

- [ ] **Step 2: Run test and verify failure**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_6_generator_consumes_workflow_policy_and_preserves_control_boundaries -q
```

Expected: fail because `scripts/generate_ppt_run2_6_arms.mjs` does not exist yet.

---

### Task 5: Implement Run 2.6 Generator And Rerun Four Arms

**Files:**
- Create: `scripts/generate_ppt_run2_6_arms.mjs`

- [ ] **Step 1: Create generator from Run 2.5**

Copy `scripts/generate_ppt_run2_5_arms.mjs` to `scripts/generate_ppt_run2_6_arms.mjs`.

Required mechanical replacements:

- `run2_5_full_skill` -> `run2_6_full_skill`
- `ppt-run2-5-` -> `ppt-run2-6-`
- `RUN 2.5` -> `RUN 2.6`
- `scripts/generate_ppt_run2_5_arms.mjs` -> `scripts/generate_ppt_run2_6_arms.mjs`

- [ ] **Step 2: Add workflow policy maps**

Add maps near the Run 2.5 role maps:

```js
const usecaseByRole = {
  cover: "usecase_design_to_production_platform_launch",
  setup: "usecase_design_to_production_platform_launch",
  contrast: "usecase_design_to_production_platform_launch",
  proof: "usecase_design_to_production_platform_launch",
  climax: "usecase_design_to_production_platform_launch",
  close: "usecase_design_to_production_platform_launch",
};
const benchmarkByRole = {
  cover: ["benchmark_visual_fidelity_interactive_slide_surface", "benchmark_glance_test_visual_hierarchy"],
  setup: ["benchmark_design_to_production_grid_precision", "benchmark_visual_fidelity_interactive_slide_surface"],
  contrast: ["benchmark_story_driven_data_emphasis", "benchmark_glance_test_visual_hierarchy"],
  proof: ["benchmark_design_to_production_grid_precision", "benchmark_visual_fidelity_interactive_slide_surface"],
  climax: ["benchmark_ai_platform_demo_climax", "benchmark_story_driven_data_emphasis"],
  close: ["benchmark_glance_test_visual_hierarchy", "benchmark_story_driven_data_emphasis"],
};
const workflowPolicyByRole = {
  cover: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
  setup: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
  contrast: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
  proof: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
  climax: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
  close: { theme_policy_id: "theme_original_high_contrast_product_system", typography_system_id: "type_system_editorial_product_sans", spacing_token_set_id: "spacing_tokens_precision_grid_12" },
};
```

- [ ] **Step 3: Update arm input boundaries**

Full arm `allowed` must include:

```js
`${pack}/commercial_usecase_bank.json`,
`${pack}/aesthetic_benchmark_bank.json`,
`${pack}/workflow_decision_policy.json`,
```

Prompt-only and Run 1.5 `forbidden` must include all three files. Bad aesthetic memory `allowed` may include `commercial_usecase_bank.json`, but `forbidden` must include `aesthetic_benchmark_bank.json` and `workflow_decision_policy.json`.

- [ ] **Step 4: Update trace**

Inside `traceFor`, add:

```js
const workflowEligible = ["run2_6_full_skill", "bad_aesthetic_memory"].includes(arm.armId);
const fullWorkflow = arm.armId === "run2_6_full_skill";
```

Each slide trace must include:

```js
commercial_usecase_id: workflowEligible ? usecaseByRole[slide.role] ?? null : null,
aesthetic_benchmark_ids: fullWorkflow ? benchmarkByRole[slide.role] ?? [] : [],
theme_policy_id: fullWorkflow ? workflowPolicyByRole[slide.role]?.theme_policy_id ?? null : null,
typography_system_id: fullWorkflow ? workflowPolicyByRole[slide.role]?.typography_system_id ?? null : null,
spacing_token_set_id: fullWorkflow ? workflowPolicyByRole[slide.role]?.spacing_token_set_id ?? null : null,
workflow_decision_ids: fullWorkflow ? [`decision_${slide.role}_usecase_benchmark_policy`] : [],
source_brand_sanitization: fullWorkflow
  ? "source brands are research references only; final slide must not copy Apple, Stripe, Figma, Google, Duarte, or SlideModel identity"
  : arm.armId === "bad_aesthetic_memory"
    ? "commercial usecase visible, but good benchmark and policy artifacts are forbidden"
    : "not applicable; Run 2.6 data forbidden for this arm",
benchmark_validation_probe: fullWorkflow ? "contact sheet must show benchmark-driven hierarchy without source-brand imitation" : "control arm must not claim benchmark learning",
theme_validation_probe: fullWorkflow ? "theme, typography, and spacing policy must be visible and original" : "control arm must not claim theme-policy learning",
```

- [ ] **Step 5: Verify generator syntax and source contract**

Run:

```bash
/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check scripts/generate_ppt_run2_6_arms.mjs
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py::test_run2_6_generator_consumes_workflow_policy_and_preserves_control_boundaries -q
```

Expected: both pass.

- [ ] **Step 6: Run generator**

Run:

```bash
/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/generate_ppt_run2_6_arms.mjs
```

Expected: creates four Run 2.6 arm directories under `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/`.

---

### Task 6: Run QA, Gemini Review, And Generate Two Mandatory Images

**Files:**
- Generated only under `outputs/`
- Create: `scripts/build_ppt_full_skill_series_sheet.py`

- [ ] **Step 1: Run layout QA for all arms**

For each slug:

```bash
python3 scripts/check_ppt_layout_quality.py \
  outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/<slug>/layout/final \
  outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/<slug>/qa/layout_quality_report.txt
```

Expected: `Checked 6 layout file(s): 0 error(s), 0 warning(s).`

- [ ] **Step 2: Run delivery QA for all arms**

For each slug:

```bash
python3 scripts/validate_pptx_delivery.py \
  --pptx "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/<slug>/output/<slug>.pptx" \
  --layout-dir "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/<slug>/layout/final" \
  --contact-sheet "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/<slug>/preview/contact-sheet.png" \
  --label "<slug>" \
  --out "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/<slug>/qa/delivery_report.md"
```

Expected: `internal-demo-ok-public-blocked`.

- [ ] **Step 3: Refresh trace QA for all arms**

For each slug:

```bash
python3 scripts/refresh_ppt_trace_qa.py \
  --trace "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/<slug>/trace_manifest.json" \
  --delivery-report "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/<slug>/qa/delivery_report.md" \
  --layout-report "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/<slug>/qa/layout_quality_report.txt" \
  --aesthetic-status "contact_sheet_review_pending_gemini_and_human"
```

Expected: delivery gate remains `internal-demo-ok-public-blocked`.

- [ ] **Step 4: Build four-arm contact sheet**

Use the existing contact-sheet builder or current local composition pattern to create:

```text
outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-6-four-arm-contact-sheet.png
```

The image must show `prompt-only`, `run1.5`, `run2.6 full`, and `bad aesthetic memory`.

- [ ] **Step 5: Create reusable full-skill-series builder**

Create `scripts/build_ppt_full_skill_series_sheet.py`. It must accept a list of full-skill contact-sheet image paths and labels, compose them horizontally with stable column widths, and write a single PNG output.

The script must support this command shape:

```bash
python3 scripts/build_ppt_full_skill_series_sheet.py \
  --out outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png \
  --item "Run 2.0=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.1=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-1-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.2=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-2-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.3=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-3-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.4=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-4-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.5=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-5-full-vulca/preview/contact-sheet.png" \
  --item "Run 2.6=outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/ppt-run2-6-full-vulca/preview/contact-sheet.png"
```

Expected: missing historical items are reported as errors, not silently skipped.

- [ ] **Step 6: Build full-skill-series horizontal comparison**

Create or update:

```text
outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png
```

The image must include Run 2.0 through Run 2.6 full-skill columns.

- [ ] **Step 7: Run Gemini artifact review**

Call `mcp__gemini_agent.gemini_artifact_review` on `run2-6-four-arm-contact-sheet.png`.

Expected: review artifact written under `.gemini-agent/artifacts/`; verdict remains internal/public-blocked unless native render and human approval pass.

---

### Task 7: Record Run 2.6 Results And Commit Rerun

**Files:**
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_6_rerun_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_6_rerun_result.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`

- [ ] **Step 1: Add failing result contract test**

Append:

```python
def test_run2_6_records_data_workflow_rerun_result() -> None:
    result = (PACK / "results" / "run2_6_rerun_result.md").read_text(encoding="utf-8")
    result_json = load_json(PACK / "results" / "run2_6_rerun_result.json")

    assert result_json["status"] == "rerun_completed_public_blocked"
    assert result_json["public_ready"] is False
    assert result_json["stage_policy"] == "repeat_same_five_layers_not_run3"
    assert result_json["rerun"]["status"] == "completed"
    assert result_json["rerun"]["best_internal_arm"] == "run2_6_full_skill"
    assert result_json["rerun"]["generated_outputs_committed"] is False
    assert_contains(
        json.dumps(result_json["data_workflow_learning"]),
        [
            "commercial_usecase_id",
            "aesthetic_benchmark_ids",
            "theme_policy_id",
            "typography_system_id",
            "spacing_token_set_id",
            "source_brand_sanitization",
        ],
    )
    assert_contains(
        result,
        [
            "Run 2.6",
            "commercial_usecase_bank.json",
            "aesthetic_benchmark_bank.json",
            "workflow_decision_policy.json",
            "run2_6_full_skill",
            "public blocked",
            "Do not advance to Run 3.0",
        ],
    )
```

- [ ] **Step 2: Create result JSON/MD**

Create `run2_6_rerun_result.json` with:

```json
{
  "schema_version": 1,
  "status": "rerun_completed_public_blocked",
  "public_ready": false,
  "stage_policy": "repeat_same_five_layers_not_run3",
  "rerun": {
    "status": "completed",
    "generated_outputs_committed": false,
    "combined_contact_sheet": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-6-four-arm-contact-sheet.png",
    "full_skill_series_sheet": "outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png",
    "delivery_gate": "internal-demo-ok-public-blocked",
    "best_internal_arm": "run2_6_full_skill",
    "best_internal_arm_verdict": "data_workflow_policy_visible_but_not_public_release_ready"
  },
  "data_workflow_learning": {
    "commercial_usecase_id": "present_for_run2_6_full_skill_and_bad_aesthetic_memory_only",
    "aesthetic_benchmark_ids": "present_for_run2_6_full_skill_only",
    "theme_policy_id": "present_for_run2_6_full_skill_only",
    "typography_system_id": "present_for_run2_6_full_skill_only",
    "spacing_token_set_id": "present_for_run2_6_full_skill_only",
    "workflow_decision_ids": "present_for_run2_6_full_skill_only",
    "source_brand_sanitization": "recorded_per_slide",
    "visual_quality_boundary": "still_internal_demo_grade"
  },
  "release_gate": "public_blocked_until_native_render_human_approval_and_source_brand_sanitization"
}
```

Create the Markdown result with the same conclusions and public-blocked boundary.

- [ ] **Step 3: Update README, comparison report, and delivery gate**

Add Run 2.6 artifacts and summary to:

- `results/README.md`
- `results/comparison_report.md`
- `results/delivery_gate.md`

The latest result should say `run2_6_full_skill` is the best internal arm for data/workflow-policy evidence. Do not claim public-ready quality.

- [ ] **Step 4: Final verification**

Run:

```bash
python3 -m pytest tests/test_ppt_run2_data_skill_quality.py tests/test_ppt_case_pack_validator.py tests/test_refresh_ppt_trace_qa.py tests/test_pptx_delivery_validator.py -q
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
ruff check tests/test_ppt_run2_data_skill_quality.py scripts/check_ppt_layout_quality.py scripts/refresh_ppt_trace_qa.py scripts/validate_pptx_delivery.py
/Users/yhryzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check scripts/generate_ppt_run2_6_arms.mjs
git ls-files outputs | wc -l
```

Expected:

- pytest passes with only existing config warning if present;
- case pack ok;
- ruff ok;
- node check ok;
- tracked `outputs` count is `0`.

- [ ] **Step 5: Gemini diff review**

Call `mcp__gemini_agent.gemini_diff_review` on the staged diff. Focus on:

- control-arm boundary;
- source-brand sanitization;
- public-ready overclaims;
- result docs and tests consistency.

- [ ] **Step 6: Commit rerun**

Run:

```bash
git add scripts/generate_ppt_run2_6_arms.mjs tests/test_ppt_run2_data_skill_quality.py docs/product/ppt-run2-data-skill-quality/results/run2_6_rerun_result.json docs/product/ppt-run2-data-skill-quality/results/run2_6_rerun_result.md docs/product/ppt-run2-data-skill-quality/results/README.md docs/product/ppt-run2-data-skill-quality/results/comparison_report.md docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md
git commit -m "docs: record PPT run 2.6 rerun"
```

---

## Self-Review Checklist

- Every Run 2.6 data artifact has tests before implementation.
- The generator is not touched until data/workflow tests pass.
- Control arms forbid Run 2.6 data.
- Bad aesthetic memory receives commercial usecase only, not good benchmark/policy.
- Source-brand copying is explicitly forbidden in data, workflow, trace, and result docs.
- Results stay public-blocked until native render and human approval pass.
- Every rerun must produce two images: four-arm contact sheet and full-skill-series horizontal comparison.
