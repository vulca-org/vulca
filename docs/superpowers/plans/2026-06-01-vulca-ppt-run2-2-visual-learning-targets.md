# PPT Run 2.2 Visual Learning Targets Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thicken the Run 2.2 multimodal database with real tutorial/video/audio/transcript references and add concrete visual learning targets that the next four-arm rerun must satisfy.

**Architecture:** `sources.json` records additional public source identities. `multimodal_database.json` stores derived-only anchors from those sources. `visual_learning_targets.json` converts anchors into expected generator behavior: before/after deltas, slide mini-previews, audio rhythm budgets, transcript headline compression, and interaction/state surfaces. The validator and tests make the targets enforceable without committing generated outputs or copied media.

**Tech Stack:** JSON case-pack docs, Python validator, pytest regression tests, existing Run 2 validation CLI.

---

### Task 1: Add Real Multimodal Source Identities

**Files:**
- Modify: `docs/product/ppt-run2-data-skill-quality/sources.json`

- [ ] Add `duarte_persuasive_visual_storytelling` for the Duarte webinar page.
- [ ] Add `duarte_slide_design_course` for the Duarte slide design course page.
- [ ] Add `udel_design_principles_video` for the University of Delaware design principles tutorial page.
- [ ] Keep `allowed_use` as `reference_analysis_only`.
- [ ] Explicitly forbid copied visuals, screenshots, full prose, full transcripts, audio, and video frames.

### Task 2: Thicken Multimodal Database Anchors

**Files:**
- Modify: `docs/product/ppt-run2-data-skill-quality/multimodal_database.json`

- [ ] Add a Duarte visual storytelling record with text/video/audio/transcript anchors.
- [ ] Add a Duarte slide design course record with text/image-reference/interaction anchors.
- [ ] Add a University of Delaware design principles record with video/audio/transcript/text anchors and CC BY-NC license boundary.
- [ ] Add derived outputs that feed `visual_learning_targets.json`.
- [ ] Keep every record `derived_observations_only`.

### Task 3: Add Visual Learning Targets

**Files:**
- Create: `docs/product/ppt-run2-data-skill-quality/visual_learning_targets.json`

- [ ] Add at least five targets:
  - `target_report_to_visual_delta`
  - `target_slide_mini_preview`
  - `target_audio_rhythm_budget`
  - `target_transcript_headline_compression`
  - `target_public_demo_climax`
- [ ] Each target must include `source_record_ids`, `anchor_ids`, `slide_roles`, `failure_pattern`, `desired_behavior`, `code_generation_requirements`, `qa_probe`, and `release_boundary`.
- [ ] Make targets require native/editable PPT implementation.

### Task 4: Validate Targets And Wire Workflow

**Files:**
- Modify: `scripts/validate_ppt_case_pack.py`
- Modify: `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`
- Modify: `docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/generation_briefs/run2_skill.md`
- Modify: `docs/product/ppt-run2-data-skill-quality/aesthetic_rubric.md`
- Modify: `tests/test_ppt_case_pack_validator.py`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`

- [ ] Add `visual_learning_targets.json` to Run 2 required files.
- [ ] Validate target references to multimodal records and anchors.
- [ ] Validate every target has native/editable code-generation requirements and public-blocked release boundary.
- [ ] Add workflow inputs so the full Run 2 arm must use the targets before generating code.
- [ ] Add tests for missing target file, unknown anchor reference, and real pack target coverage.

### Task 5: Verify And Commit

**Files:**
- All files changed above.

- [ ] Run:

```bash
python3 -m pytest tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_5_product_lab.py tests/test_ppt_run2_data_skill_quality.py tests/test_refresh_ppt_trace_qa.py -q
python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality
ruff check scripts/validate_ppt_case_pack.py scripts/refresh_ppt_trace_qa.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py tests/test_refresh_ppt_trace_qa.py
ruff format --check scripts/validate_ppt_case_pack.py scripts/refresh_ppt_trace_qa.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run2_data_skill_quality.py tests/test_refresh_ppt_trace_qa.py
git ls-files outputs | wc -l
```

- [ ] Ask Gemini for diff review.
- [ ] Commit docs, validator, tests, and plan only.
