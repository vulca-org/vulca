# VULCA Review Context Vault

Vault status: protected context source.

This folder preserves the long-lived VULCA project memory: product intent,
technical history, capability boundaries, review gates, and source references.
It is designed for future sessions to read before planning product, website,
PPT, SDK, or MCP work.

This is not a normal documentation folder. It is the protected review context
for the project.

## Operating Rule

Other sessions may read this folder and cite it. They must not directly modify
it. Proposed edits go through `requests/` and are accepted only by a dedicated
context-curator session on the `codex/vulca-context-vault` branch.

The vault is intentionally branch-only. `master` remains the protected product
mainline and does not carry or require the vault validation gate.

## Current Vault Contents

- `LOCK.md`: non-negotiable access and modification boundary.
- `GOVERNANCE.md`: request, review, and curator workflow.
- `PROTECTION.md`: branch-only decision and live GitHub protection record.
- `MANIFEST.json`: machine-readable vault inventory and gate metadata.
- `source-index.md`: source references for historical claims.
- `00-project-overview.md`: current integrated VULCA picture.
- `01-development-history.md`: chronological technical/product history.
- `02-capability-map.md`: capability map by product layer.
- `03-layering-and-decompose.md`: image decomposition and layer stack memory.
- `04-prompt-control.md`: prompt and visual planning control history.
- `05-layer-redraw-and-mask-gates.md`: redraw, mask, pasteback, and quality gates.
- `06-learning-loop-and-case-records.md`: case record and future learning substrate.
- `07-workspace-product-model.md`: Workspace / Creative Repo product model.
- `08-website-and-ppt-boundaries.md`: website and PPT integration boundaries.
- `09-claim-boundaries.md`: public, internal, blocked, and human-confirmed claims.
- `10-integration-spine.md`: routing layer across Workspace, SDK/MCP, website,
  PPT, and vault context.
- `11-artifact-bridge-spec.md`: SDK/MCP artifact to Workspace object bridge.
- `12-complete-demo-path.md`: standard brief-to-evidence-to-release-gate demo
  path.
- `13-website-ppt-claim-spine.md`: shared website, README, PPT, and public
  story claim spine.
- `14-release-readiness-evidence-gate.md`: M5 release-readiness evidence gate.
- `artifact-bridge/`: RR2 reference fixture for projecting SDK/MCP artifacts
  into Workspace review objects.
- `workspace-durable/`: RR3 durable review fixture for reload-preserved
  review state, blockers, and human decision history.
- `public-examples/`: RR4 public example gate for one example-specific public
  artifact and copy scope.
- `copy-gates/`: RR5 website, README, PPT, and translation claim-level gate.
- `release-readiness/`: fixed report template for release-readiness reviews.
- `requests/`: proposed changes from other sessions.
- `gates/`: validation rules and local gate checks.

## Read Order

1. Read `LOCK.md`.
2. Read `00-project-overview.md`.
3. Read the focused history file for the workstream being changed.
4. Read `09-claim-boundaries.md` before writing public copy, decks, README text,
   or product claims.
5. Read `10-integration-spine.md` before connecting Workspace, SDK/MCP,
   website, PPT, or vault workstreams.
6. Read `11-artifact-bridge-spec.md` before designing artifact ingestion,
   Workspace imports, evidence packs, review checks, or demo paths.
7. Read `12-complete-demo-path.md` before building or describing the standard
   VULCA demo scenario.
8. Use `artifact-bridge/m3-demo-bridge-fixture.json` before implementing or
   reviewing the first M3 bridge adapter path.
9. Use `workspace-durable/m3-durable-review-fixture.json` before implementing
   or reviewing Workspace persistence, reload, blocker, or decision history.
10. Use `public-examples/m3-public-example-gate.json` before claiming that any
    specific visual example is cleared for public use.
11. Use `copy-gates/website-ppt-copy-gate.json` before aligning website,
    README, PPT, or translated public copy.
12. Read `13-website-ppt-claim-spine.md` before writing website copy, README
    positioning, public decks, or PPT proof-lab summaries.
13. Read `14-release-readiness-evidence-gate.md` before upgrading any preview,
    internal, public-blocked, or release-readiness status.
14. Use `release-readiness/TEMPLATE.md` before proposing a stronger release
    level, public example, website claim, or PPT claim.
15. If this vault needs a change, create a request packet instead of editing it.
