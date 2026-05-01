# Real Brief Brainstorm Seed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a draft `/visual-brainstorm` `proposal.md` from Phase 2 real-brief workflow seed artifacts.

**Architecture:** Add a small `vulca.real_brief.brainstorm_seed` module plus CLI wrapper. The module reads an adapted visual-spec project directory, validates its real-brief seed status, renders the existing proposal schema, and writes only `proposal.md`.

**Tech Stack:** Python standard library, pytest, existing Vulca real-brief artifact helpers.

---

### Task 1: Proposal Seeder Tests

**Files:**
- Create: `tests/test_real_brief_brainstorm_seed.py`

- [ ] **Step 1: Write tests for supported seed generation**

Use `write_real_brief_dry_run` and `adapt_real_brief_package` to create a seeded project in `tmp_path`, call `seed_real_brief_brainstorm_proposal`, and assert `proposal.md` exists with `status: draft`, `domain: poster`, `tradition: null`, `style_treatment: unified`, brief-specific content, and human gate open questions.

- [ ] **Step 2: Write tests for gates and CLI**

Cover ready proposal overwrite refusal, draft overwrite requiring force, unsupported seed refusal, dry-run no-write behavior, CLI write behavior, and secret leakage.

- [ ] **Step 3: Verify red**

Run `PYTHONPATH=src python3 -m pytest tests/test_real_brief_brainstorm_seed.py -q`. Expected: import failure for `vulca.real_brief.brainstorm_seed`.

### Task 2: Proposal Seeder Module

**Files:**
- Create: `src/vulca/real_brief/brainstorm_seed.py`
- Modify: `src/vulca/real_brief/__init__.py`

- [ ] **Step 1: Implement loader and validation**

Read `workflow_seed.md`, `real_brief/adapter_manifest.json`, `real_brief/structured_brief.json`, and `real_brief/workflow_handoff.json`. Require `workflow_status == ready_for_visual_brainstorm`, `human_gate_required is true`, and a supported visual domain.

- [ ] **Step 2: Implement proposal renderer**

Render exactly the `/visual-brainstorm` proposal template with eight frontmatter fields and non-empty sections. Use `tradition: null`, `status: draft`, and `style_treatment: unified`.

- [ ] **Step 3: Implement write gates**

Refuse finalized `proposal.md`, refuse draft overwrite without `force=True`, support `dry_run=True`, and return paths/status in a result dict.

- [ ] **Step 4: Export lazily**

Add `seed_real_brief_brainstorm_proposal` to `vulca.real_brief.__all__` and `_LAZY_EXPORTS` without importing provider-facing modules.

### Task 3: CLI and Skill Contract

**Files:**
- Create: `scripts/real_brief_brainstorm_seed.py`
- Modify: `skills/visual-brainstorm/SKILL.md`
- Modify: `.agents/skills/visual-brainstorm/SKILL.md`
- Modify: `.claude/skills/visual-brainstorm/SKILL.md`

- [ ] **Step 1: Add CLI**

Accept `--root`, `--slug`, `--date`, `--force`, and `--dry-run`; print JSON result.

- [ ] **Step 2: Update skill docs**

Document that when `workflow_seed.md` and `real_brief/adapter_manifest.json` exist with `ready_for_visual_brainstorm`, `/visual-brainstorm <slug>` should seed or resume `proposal.md` from the real brief package, then show the full draft and wait for explicit `ready` or equivalent.

### Task 4: Verification and Publish

**Files:**
- Test files and changed implementation files.

- [ ] **Step 1: Run focused tests**

Run `PYTHONPATH=src python3 -m pytest tests/test_real_brief_brainstorm_seed.py tests/test_real_brief_workflow_adapter.py -q`.

- [ ] **Step 2: Run adjacent workflow tests**

Run `PYTHONPATH=src python3 -m pytest tests/test_real_brief_benchmark.py tests/test_visual_brainstorm_discovery_integration.py tests/test_visual_discovery_artifacts.py tests/test_visual_discovery_cards.py tests/test_visual_discovery_types.py -q`.

- [ ] **Step 3: Commit and push**

Commit the isolated branch and open a PR against `master`.
