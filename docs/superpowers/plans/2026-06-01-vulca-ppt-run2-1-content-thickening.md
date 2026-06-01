# Vulca PPT Run 2.1 Content Thickening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thicken the existing Run 2.0 PPT case pack in place so the next rerun proves deeper data, executable skill behavior, and refreshed trace QA outcomes instead of adding a new product stage.

**Architecture:** Keep the five fixed Run 2 layers and add Run 2.1 depth inside those layers. The source/video cards gain executable extraction units, the skill workflow gains a declarative machine-checkable stage spec and human-gated repair triggers, and a trace-refresh utility writes post-QA outcomes back into generated trace manifests before any public-release claim.

**Tech Stack:** Python stdlib, pytest, ruff, Markdown/JSON case-pack files, local `outputs/` PPT artifacts, Gemini-agent for plan/diff/artifact review.

---

## Scope

Run 2.1 is not a new product milestone. It deepens:

- tutorial/case/video data quality;
- design-memory-to-skill executability;
- QA trace outcome integrity.

It does not publish a public deck, claim post-training, or commit generated PPTX/PNG artifacts.

## File Map

- Modify `scripts/validate_ppt_case_pack.py`: require extraction units on Run 2 source/video cards and validate the new skill workflow file.
- Modify `tests/test_ppt_case_pack_validator.py`: add failing validator tests for missing extraction units and workflow repair triggers.
- Modify `tests/test_ppt_run2_data_skill_quality.py`: assert committed Run 2 cards and workflow are thick enough.
- Create `tests/test_refresh_ppt_trace_qa.py`: regression tests for post-QA trace refresh.
- Create `scripts/refresh_ppt_trace_qa.py`: update local `trace_manifest.json` files from delivery/layout QA artifacts.
- Modify `docs/product/ppt-run2-data-skill-quality/source_cards/*.json`: add executable extraction units.
- Modify `docs/product/ppt-run2-data-skill-quality/video_cards/*.json`: add executable extraction units.
- Create `docs/product/ppt-run2-data-skill-quality/skill_workflow.json`: declarative staged workflow, inputs, outputs, human-gated repair triggers, and release gate behavior.
- Modify `docs/product/ppt-run2-data-skill-quality/generation_protocol.md`: require trace refresh after QA.
- Modify `docs/product/ppt-run2-data-skill-quality/results/audit_review.md`: record that Run 2.1's next blocker is rerun, not new-stage expansion.

## Tasks

### Task 1: Require Thick Extraction Units

- [ ] Write failing validator tests that reject source/video cards missing `extraction_units`.
- [ ] Update `scripts/validate_ppt_case_pack.py` with `validate_run2_extraction_units`.
- [ ] Update test fixtures so valid Run 2 packs include extraction units.
- [ ] Run `python3 -m pytest tests/test_ppt_case_pack_validator.py -q`.
- [ ] Commit validator/schema update.

### Task 2: Thicken The Existing Data Cards

- [ ] Write failing package tests requiring at least two extraction units per card and fields `source_anchor`, `derived_rule`, `slide_role`, `execution_guard`, and `qa_probe`.
- [ ] Add extraction units to the 8 source cards and 2 video cards.
- [ ] Run `python3 -m pytest tests/test_ppt_run2_data_skill_quality.py -q`.
- [ ] Run `python3 scripts/validate_ppt_case_pack.py --profile run2 docs/product/ppt-run2-data-skill-quality`.
- [ ] Commit data-card thickening.

### Task 3: Add Declarative Skill Workflow

- [ ] Write failing tests requiring `skill_workflow.json`, ordered stages, and repair triggers.
- [ ] Add the workflow JSON with declarative stages for case read, memory compile, archetype selection, generation, QA, repair recommendation, trace refresh, and release decision.
- [ ] Update `vulca_ppt_skill.md` and `generation_protocol.md` to reference the machine-checkable workflow.
- [ ] Run Run 2 package tests and validator.
- [ ] Commit workflow update.

### Task 4: Refresh Trace QA Outcomes

- [ ] Write failing tests for `scripts/refresh_ppt_trace_qa.py` using a temporary trace manifest plus delivery/layout QA files.
- [ ] Implement the script with no PPTX mutation: read QA files, update trace fields, preserve public-blocked gates, support `--dry-run`, write `.bak` backup files, and replace manifests atomically.
- [ ] Add a partial-failure test proving invalid QA input does not overwrite the original manifest.
- [ ] Run the script on local Run 2 outputs under `outputs/` and keep outputs untracked.
- [ ] Run pytest/ruff and commit the script/tests/docs.

### Task 5: Rerun Readiness Gate

- [ ] Use Gemini-agent to review the completed diff for overclaims.
- [ ] Run full relevant verification: Run 2 package tests, case-pack validator, trace-refresh tests, ruff check, ruff format check.
- [ ] Update results docs with Run 2.1 readiness: ready to rerun arms, still public-blocked.
- [ ] Commit the readiness record.
