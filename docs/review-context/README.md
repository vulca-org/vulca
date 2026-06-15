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
6. If this vault needs a change, create a request packet instead of editing it.
