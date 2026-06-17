# PPT Delivery QA V1

Status: structural QA primitive; native rendering still requires a later adapter.

## Purpose

PPT Delivery QA V1 turns a generated PowerPoint deck into an inspectable delivery gate before a demo or public claim. It does not generate slides and does not judge aesthetics. It checks whether the artifact package is structurally ready for internal review.

## Inputs

- Generated `.pptx`.
- Artifact-tool layout JSON directory.
- Contact sheet PNG.
- Optional product/case-pack evidence for human review.

## Checks

- PPTX is a readable ZIP package.
- Required PPTX package entries exist.
- Slide XML entries exist and are counted.
- Layout JSON files exist, parse as JSON, and expose artifact-tool layout schema plus element lists.
- Contact sheet exists and has a valid PNG header.
- Embedded `ppt/media/*` entries are counted as provenance/editability warnings.
- Local renderer availability is recorded for LibreOffice, PowerPoint, and Keynote.

## Gate Statuses

- `blocked`: a hard structural artifact is missing or unreadable.
- `internal-demo-ok-public-blocked`: structural checks allow internal demo review, but public publishing is blocked.

Tools should present `internal-demo-ok-public-blocked` as a caution state, not as a green pass.

## What V1 Does Not Prove

This primitive does not prove native PowerPoint, Keynote, or Google Slides visual fidelity. Renderer availability is a heuristic only. Public publishing still requires human review and at least one real native/cross-platform inspection pass.

## Run 1 Result

Both the Run 1 baseline deck and the Run 1 Vulca case-pack deck are `internal-demo-ok-public-blocked`: structurally ready for internal review, not public-ready.
