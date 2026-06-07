# PPT Run 2.62 Narrative Proof Rerun Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate Run 2.62 as a four-arm PPT rerun that consumes Run 2.61 narrative proof contracts before native drawing.

**Architecture:** Add a Node generator that follows the Run 2.60 artifact-tool pattern but loads and validates Run 2.61 narrative, selector, fusion, policy, and gate artifacts. The full arm renders editable native PPT shapes/text from those contracts and records Run 2.61 IDs in every slide trace; the bad-control arm explicitly omits those IDs. Update tests and viewer registration so the local HTML page shows Run 2.62 as the latest generated proof.

**Tech Stack:** Node ESM, `@oai/artifact-tool`, Python pytest, ruff, static JSON/MD artifacts, existing HTML viewer builder.

---

## File Structure

- Create: `scripts/generate_ppt_run2_62_narrative_proof_arms.mjs`
- Create: `tests/test_ppt_run2_62_ci_contract.py`
- Modify: `tests/test_ppt_run2_data_skill_quality.py`
- Modify: `scripts/build_ppt_run_html_viewer.py`
- Create/update generated local outputs under `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_62_narrative_proof_rerun_result.json`
- Create: `docs/product/ppt-run2-data-skill-quality/results/run2_62_narrative_proof_rerun_result.md`

---

### Task 1: Add Failing Run 2.62 Contract Tests

- [ ] Add CI test that requires the new generator, result JSON/MD, Run 2.62 viewer registration, and latest run hint `2.62`.
- [ ] Add local trace/result test that requires full-arm Run 2.61 IDs on all six slides and bad-control omission on all six slides.
- [ ] Run the new tests and confirm they fail before implementation.

### Task 2: Implement Run 2.62 Generator

- [ ] Create `scripts/generate_ppt_run2_62_narrative_proof_arms.mjs`.
- [ ] Load and validate all Run 2.61 artifacts before drawing the full arm.
- [ ] Generate four arms, PPTX files, previews, per-arm contact sheets, four-arm sheet, full-skill series sheet, trace manifests, result JSON, and result MD.
- [ ] Run the generator and confirm outputs exist.

### Task 3: Register Run 2.62 In Viewer

- [ ] Add Run 2.62 to `RUN_SPECS`.
- [ ] Update `LATEST_RUN_PAYLOAD_HINT` to `2.62`.
- [ ] Load Run 2.62 result data and render a Data / Skill summary for the generated consumption proof.
- [ ] Rebuild the HTML viewer and verify latest is `2.62`.

### Task 4: Verify, Review, Commit, Push

- [ ] Run targeted Run 2.61/2.62 tests.
- [ ] Run `ruff` and `py_compile`.
- [ ] Use Browser to confirm the viewer shows Run 2.62 and the Data / Skill trace summary.
- [ ] Use gemini-agent diff review.
- [ ] Commit and push the verified changes.

