# Review Context Changelog

Vault status: append-only change log.

## 2026-06-15

### Added Website And PPT Claim Spine

- Added `13-website-ppt-claim-spine.md` as the protected M4 standard for
  website, README-facing copy, public decks, and PPT proof-lab summaries.
- Wired the claim spine into the README read order, manifest, source index,
  validator, and vault tests.
- Updated the integration spine so M4 points to the dedicated claim-spine
  document and M5 becomes the next release-readiness milestone.

Source basis:

- `docs/review-context/08-website-and-ppt-boundaries.md`.
- `docs/review-context/09-claim-boundaries.md`.
- `docs/review-context/12-complete-demo-path.md`.
- Platform website content and homepage plans at commit `5dc32cd`.
- PPT proof lab source index entry and Run 2.93 public-blocked gate.

### Added Complete Demo Path Standard

- Added `12-complete-demo-path.md` as the protected M3 standard for one
  complete VULCA preview scenario from brief to evidence pack and release gate.
- Wired the demo path into the README read order, manifest, source index,
  validator, and vault tests.
- Updated the integration spine and artifact bridge spec so M3 points to the
  dedicated demo-path standard.

Source basis:

- `docs/review-context/10-integration-spine.md`.
- `docs/review-context/11-artifact-bridge-spec.md`.
- `origin/master:docs/product/workspace-current-state-audit.md`.
- Workspace `workspaceDemo.ts` object model.

### Added Artifact Bridge Specification

- Added `11-artifact-bridge-spec.md` as the protected M2 specification for
  mapping SDK/MCP outputs into Workspace objects.
- Wired the bridge spec into the README read order, manifest, source index,
  validator, and vault tests.
- Updated `10-integration-spine.md` so M2 points to the dedicated bridge spec
  and M3 becomes the next demo-path milestone.

Source basis:

- `src/vulca/mcp_server.py` MCP payloads.
- Learning Loop, decompose case, and layer-generate case schema specs.
- Workspace `workspaceDemo.ts` object model.
- `origin/master:docs/product/workspace-current-state-audit.md`.

### Added Integration Spine

- Added `10-integration-spine.md` as the routing layer across Workspace,
  SDK/MCP, website, PPT proof lab, and protected vault context.
- Updated the vault manifest, README read order, source index, and validator
  tests so future sessions can find and gate the integration spine.
- Recorded the `master` README alignment merge commit
  `cb6d52fe docs: surface VULCA Workspace product direction`.
- Updated Workspace source memory to distinguish the user-cited baseline
  `6efef07` from the latest observed local preview `5f4a666`.

Source basis:

- `origin/master` commit `cb6d52fe`.
- `origin/master:docs/product/workspace-current-state-audit.md`.
- Platform Workspace baseline `6efef07` and observed preview `5f4a666`.

### Confirmed Branch-Only Protection

- Recorded the human decision to keep the vault only on
  `codex/vulca-context-vault`.
- Added `PROTECTION.md` as the local record for GitHub rulesets, branch
  boundary, request workflow, and emergency bypass requirements.
- Scoped `.github/workflows/review-context.yml` to
  `codex/vulca-context-vault` only.
- Fixed governance ownership text to use the valid GitHub owner `@yha9806`.

Source basis:

- Human decision in the current session: option B, keep the vault only on
  `codex/vulca-context-vault`.
- Live GitHub rulesets verified through the GitHub API on 2026-06-15.

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
