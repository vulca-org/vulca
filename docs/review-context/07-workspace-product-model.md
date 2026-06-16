# Workspace Product Model

Vault status: product memory.

## Product Center

The Workspace branch is the current product center. It turns VULCA from an
agent/MCP attachment into a reviewable product surface.

Current product sentence:

> VULCA Workspace organizes AI-native visual work around Creative Repos:
> briefs, motif branches, visual variants, review evidence, and release gates.

## Core Objects

- `CreativeRepo`: one project source of truth.
- `Brief`: business, visual, and cultural task.
- `MotifBranch`: creative direction under review.
- `VisualVariant`: generated/imported candidate or version.
- `ReviewRequest`: review workflow around a branch or asset.
- `EvidencePack`: proof bundle for a decision.
- `ReleaseGate`: public-readiness decision and blockers.
- `AgentRun`: execution trace inside the repo.

## Current Implemented Product Surface

In the `vulca-platform` Workspace branch:

- `/workspace`
- `/workspace/manual`
- Review Inbox
- Single Asset Review
- Visual Review Room
- Context Drawer
- Review Checks Panel
- Decision Panel
- Typed review modes
- Pin filters
- Context review controls
- `public_ready=false` boundaries
- RR3 durable review fixture:
  `workspace-durable/m3-durable-review-fixture.json`

Verified prior to vault creation:

- 29 focused tests passed.
- TypeScript type-check passed.

## Product Direction

VULCA should combine:

- GitHub-like review governance
- Figma / Frame.io-like visual comments and version review
- VULCA-specific cultural, visual, evidence, and release gates

It should not become a generic file review tool or an editor replacement.

## Production Persistence Layer

Production persistence is part of the Workspace product design, not a separate
backend-only concern. It defines durable Creative Repo state, reviewer and
release-owner permissions, conflict handling, multi-instance behavior, and
audit history.

Use `15-workspace-production-persistence-spec.md` before implementing or
reviewing database-backed Workspace persistence.

## Key Boundary

VULCA reviews and controls creative judgment. It does not replace Figma, Canva,
Adobe, Runway, FLORA, Krea, or other creative tools.

Agents can operate inside VULCA. Agents are not the product identity.

Sources:

- `source-index.md` Workspace section
- `15-workspace-production-persistence-spec.md`
