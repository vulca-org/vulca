# PPT Run 2.2 Multimodal Database Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a machine-checkable multimodal lesson database contract so PPT generation can learn from text tutorials, image references, video tutorials, audio commentary, transcript snippets, and interaction observations without storing copied copyrighted media.

**Architecture:** `multimodal_database.json` becomes the upstream database contract. The validator checks modality coverage, source references, storage boundaries, anchors, and QA gates. The Run 2 skill workflow compiles this database before evidence and aesthetic memory so later reruns can prove that data changed code-generated PPT behavior.

**Tech Stack:** JSON case-pack docs, Python validator, pytest regression tests, existing Run 2 case-pack validation CLI.

---

### Task 1: Add Multimodal Database Contract

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/multimodal_database.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/generation_protocol.md`

- [ ] **Step 1: Create the database file**

Add a JSON object with these top-level keys: `schema_version`, `status`, `storage_policy`, `required_modalities`, `records`, `cross_modal_design_tasks`, and `qa_gates`.

Each record must include:

```json
{
  "id": "mm_text_visual_hierarchy_tutorial",
  "source_id": "slidemodel_visual_hierarchy",
  "source_kind": "tutorial_page",
  "modalities": ["text", "image_reference"],
  "allowed_storage": "derived_observations_only",
  "ingestion_status": "metadata_and_derived_observations_recorded",
  "anchors": [
    {
      "anchor_id": "text_hierarchy_single_dominant_object",
      "modality": "text",
      "locator": "article-level design principle",
      "observation": "Presentation hierarchy should make the primary claim and focal object immediately dominant.",
      "extracted_design_signal": "A slide may carry one dominant claim and one dominant proof object; secondary labels must remain subordinate.",
      "allowed_use": "derived_rules_only"
    }
  ],
  "derived_outputs": ["extraction_units", "aesthetic_memory_candidates"],
  "do_not_store": ["full prose", "screenshots", "logos", "source layouts"],
  "qa_gates": ["source boundary recorded", "derived rule is executable", "no copied media stored"]
}
```

- [ ] **Step 2: Document database role**

Update `README.md` and `generation_protocol.md` to say Run 2.2 repeats the same five product layers, with `multimodal_database.json` thickening layer 2. Do not claim public readiness.

### Task 2: Validate Multimodal Database

**Files:**
- Modify: `scripts/validate_ppt_case_pack.py`
- Modify: `tests/test_ppt_case_pack_validator.py`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Extend Run 2 required files**

Add `multimodal_database.json` to `RUN2_REQUIRED_FILES`.

- [ ] **Step 2: Add validation constants**

Add modality and storage choices:

```python
RUN2_MULTIMODAL_MODALITIES = {"text", "image_reference", "video", "audio", "transcript", "interaction"}
RUN2_MULTIMODAL_ALLOWED_STORAGE = {
    "metadata_only",
    "derived_observations_only",
    "generated_assets_only",
    "local_untracked_cache_only",
}
```

- [ ] **Step 3: Add validation function**

Implement `validate_run2_multimodal_database(pack_dir, source_ids, errors)`. It must require all six modalities somewhere in the database, validate every `source_id`, validate every anchor, and reject copied-media storage language in `allowed_storage`.

- [ ] **Step 4: Add tests**

Add tests proving:

- missing `multimodal_database.json` fails Run 2 validation;
- missing audio/video/transcript coverage fails;
- valid Run 2 pack includes all modalities, copyright boundaries, executable anchors, and visual-taste tasks.

### Task 3: Wire Multimodal Database Into Skill Workflow

**Files:**
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/generation_briefs/run2_skill.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/source_cards/README.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/video_cards/README.md`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] **Step 1: Add compile_multimodal_database stage**

Insert a workflow stage before evidence memory:

```json
{
  "id": "compile_multimodal_database",
  "order": 2,
  "layer": "tutorial_case_video_audio_data",
  "inputs": ["multimodal_database.json", "sources.json"],
  "outputs": ["modal anchors", "cross-modal design tasks", "storage boundaries", "source-to-skill trace"],
  "gates": ["all required modalities covered", "no copied source media stored", "anchors become executable design signals"]
}
```

Renumber later stages and update tests to expect the new stage sequence.

- [ ] **Step 2: Update skill docs**

State that code generation must select design actions from multimodal anchors before writing slide code. Make audio/video/tutorial data usable only as derived observations, not copied assets.

- [ ] **Step 3: Update Run 2 skill allowed inputs**

Add `multimodal_database.json` to the full Run 2.1/2.2 arm allowed inputs.

### Task 4: Verify And Commit

**Files:**
- All files changed above.

- [ ] **Step 1: Run tests**

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py tests/test_ppt_run2_data_skill_quality.py tests/test_refresh_ppt_trace_qa.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Run validator**

```bash
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
```

Expected: `case pack ok`.

- [ ] **Step 3: Run lint and format checks**

```bash
ruff check scripts/validate_ppt_case_pack.py scripts/refresh_ppt_trace_qa.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py tests/test_refresh_ppt_trace_qa.py
ruff format --check scripts/validate_ppt_case_pack.py scripts/refresh_ppt_trace_qa.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py tests/test_refresh_ppt_trace_qa.py
git ls-files outputs | wc -l
```

Expected: ruff passes, format check passes, tracked outputs count is `0`.

- [ ] **Step 4: Commit**

```bash
git add docs/product/ppt-run2-data-skill-quality scripts/validate_ppt_case_pack.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py docs/superpowers/plans/2026-06-01-vulca-ppt-run2-2-multimodal-database.md
git commit -m "docs: add PPT Run 2.2 multimodal database"
```
