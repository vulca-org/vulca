# Review Context Changelog

Vault status: append-only change log.

## 2026-06-15

### Initialized Context Vault

- Created protected `docs/review-context/` structure on branch
  `codex/vulca-context-vault`.
- Recorded the core VULCA historical workstreams:
  image layering, decomposition, prompt control, visual skills,
  layer redraw, mask-aware routing, target-aware refinement, learning loop,
  Workspace product model, website, and PPT proof lab.
- Added governance rules requiring request packets for future modifications.
- Added local validation gate:
  `docs/review-context/gates/validate_review_context.py`.
- Added repository guardrails: CODEOWNERS path ownership, review-context CI, and
  validator tests.

Source basis:

- Current SDK/MCP mainline at `origin/master` commit `d6b8b559`.
- Workspace product branch at platform commit `6efef07`.
- Website film-led homepage branch at platform commit `5dc32cd`.
- PPT case-pack branch `codex/vulca-ppt-case-pack`, especially Run 2.93
  visual quality evaluation.
