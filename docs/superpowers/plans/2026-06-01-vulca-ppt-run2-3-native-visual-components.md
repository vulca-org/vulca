# PPT Run 2.3 Native Visual Components Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn Run 2.2 visual learning targets into concrete native-PPT component contracts and rerun the same four arms to test whether component-level learning improves the generated presentation.

**Architecture:** `visual_target_components.json` sits after `visual_learning_targets.json`. The validator checks that every component references known targets, requires native editable PPT primitives, avoids copied media references, and keeps public release blocked. The local Run 2.3 generation script renders the full arm with native component families while keeping prompt-only, Run 1.5, and bad aesthetic memory arms isolated.

**Tech Stack:** JSON case-pack docs, Python validator, pytest, artifact-tool presentation JSX, delivery/layout QA, Gemini artifact review.

---

### Task 1: Add Component Contract

- [x] Create `visual_target_components.json`.
- [x] Add five components: before/after thumbnail, slide mini-preview, rhythm budget strip, transcript headline route, public-demo climax object.
- [x] Keep component definitions derived-only and media-free.

### Task 2: Validate Component Contract

- [x] Add component file to Run 2 required files.
- [x] Validate target references.
- [x] Validate native/editable primitive requirements.
- [x] Reject external media/file references and public-ready release boundaries.
- [x] Add pytest coverage for failure modes and real pack coverage.

### Task 3: Wire Workflow And Briefs

- [x] Add `visual_target_components.json` to skill workflow inputs.
- [x] Update `vulca_ppt_skill.md`, generation briefs, generation protocol, and aesthetic rubric.
- [x] Update trace manifest contract with `visual_component_ids`.

### Task 4: Rerun Four Arms

- [x] Generate Run 2.3 local workspaces under `outputs/`.
- [x] Build four PPTX decks and contact sheets.
- [x] Run delivery QA, layout QA, trace refresh, and Gemini contact-sheet review.
- [x] Keep generated outputs untracked.

### Task 5: Record Results

- [x] Add Run 2.3 result markdown and JSON.
- [x] Update comparison report, results README, and delivery gate.
- [x] Verify tests, validator, lint, format, and no tracked outputs.
