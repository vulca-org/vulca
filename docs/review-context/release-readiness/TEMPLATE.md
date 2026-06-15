# Release Readiness Report

Vault status: protected release-readiness report template.

Use this template for any request to upgrade VULCA work from draft, preview,
internal proof, or public-blocked status toward a stronger release level.

## Metadata

| Field | Value |
| --- | --- |
| Report id | TBD |
| Workstream | Workspace / SDK-MCP / website / PPT / provider-backed example / other |
| Current release level | R0 / R1 / R2 / R3 / R4 / R5 |
| Requested release level | R0 / R1 / R2 / R3 / R4 / R5 |
| Human release owner | TBD |
| Prepared by | TBD |
| Date | YYYY-MM-DD |
| Target branch or PR | TBD |
| Source vault commit | TBD |

## Default Boundary

- [ ] Public release remains blocked until every required gate below is passed and a human release owner records approval.
- [ ] Missing evidence is recorded as blocked, not silently ignored.
- [ ] Agent/system checks are evidence inputs only and do not make the final release decision.
- [ ] If evidence is mixed, the approved level uses the lowest applicable R-level.

## Evidence Index

| Evidence item | Required for gate | Path, URL, commit, or PR | Reviewer | Status |
| --- | --- | --- | --- | --- |
| TBD | Gate 1 | TBD | TBD | blocked / pass / not applicable |
| TBD | Gate 2 | TBD | TBD | blocked / pass / not applicable |
| TBD | Gate 3 | TBD | TBD | blocked / pass / not applicable |
| TBD | Gate 4 | TBD | TBD | blocked / pass / not applicable |
| TBD | Gate 5 | TBD | TBD | blocked / pass / not applicable |
| TBD | Gate 6 | TBD | TBD | blocked / pass / not applicable |

## Gate 1: Workspace Persistence

Gate result: blocked / pass / not applicable

Required evidence:

- [ ] Creative Repo or review data persists beyond a browser session.
- [ ] Review item state persists.
- [ ] Version history persists.
- [ ] Blockers and decisions persist.
- [ ] Release gate state persists.
- [ ] Reviewer and release-owner access boundaries are defined.

Verification links:

- TBD

Blocked notes:

- TBD

## Gate 2: Artifact Ingestion

Gate result: blocked / pass / not applicable

Required evidence:

- [ ] SDK/MCP outputs enter Workspace through the artifact bridge.
- [ ] Source operation, artifact paths, provider/model metadata, warnings,
  claim state, and review labels are preserved.
- [ ] Generated or imported assets become `VisualVariant` records.
- [ ] Tool executions become `AgentRun` records.
- [ ] Case records remain evidence substrate, not human labels.

Verification links:

- TBD

Blocked notes:

- TBD

## Gate 3: EvidencePack Rendering

Gate result: blocked / pass / not applicable

Required evidence:

- [ ] EvidencePack renders brief, motif, artifact, provider, prompt, layer,
  evaluation, warning, and source refs.
- [ ] Reviewers can inspect evidence on demand.
- [ ] Missing evidence is visible as a blocker.
- [ ] Evidence packs link back to bridge records or source artifacts.

Verification links:

- TBD

Blocked notes:

- TBD

## Gate 4: Human Release Workflow

Gate result: blocked / pass / not applicable

Required evidence:

- [ ] Release owner role exists.
- [ ] Human decision actions are explicit.
- [ ] Request-changes, block-release, and internal-approval paths are
  represented.
- [ ] Public-release state cannot be set by agent/system/external checks.
- [ ] Decision history records actor, action, summary, and timestamp.
- [ ] Release gate blockers remain visible.

Verification links:

- TBD

Blocked notes:

- TBD

## Gate 5: Public Example Quality

Gate result: blocked / pass / not applicable

Required evidence:

- [ ] Source artifacts are preserved.
- [ ] Final preview image or artifact is inspectable.
- [ ] Visual quality review passes for the specific example.
- [ ] Cultural/evidence review is qualified and source-backed.
- [ ] Release owner signs off for that example.
- [ ] Claims attached to the example match evidence.

Verification links:

- TBD

Blocked notes:

- TBD

## Gate 6: Website/PPT Claim Review

Gate result: blocked / pass / not applicable

Required evidence:

- [ ] Copy follows `13-website-ppt-claim-spine.md`.
- [ ] Website, README, and PPT use the same product spine.
- [ ] Preview/internal/public-blocked status is preserved.
- [ ] Public examples trace to the M3 demo path or an equivalent source-backed
  path.
- [ ] Translations preserve the same claim level.

Verification links:

- TBD

Blocked notes:

- TBD

## Release Decision

| Field | Value |
| --- | --- |
| Requested R-level | R0 / R1 / R2 / R3 / R4 / R5 |
| Approved R-level | R0 / R1 / R2 / R3 / R4 / R5 / blocked |
| Decision | blocked / internal_only / preview_gated / internal_pilot / public_example / product_release |
| Human release owner | TBD |
| Decision timestamp | YYYY-MM-DDTHH:MM:SSZ |
| Evidence packet path | TBD |
| Boundary notes | TBD |

## Required Downgrade If Blocked

If any required gate is blocked, the approved status must be downgraded to the
lowest applicable release level and public copy must preserve that boundary.

Record the downgrade here:

- Blocked gate(s): TBD
- Downgraded approved level: TBD
- Copy boundary to use: TBD
- Follow-up owner: TBD

## Sources

- `docs/review-context/14-release-readiness-evidence-gate.md`
- `docs/review-context/13-website-ppt-claim-spine.md`
- `docs/review-context/09-claim-boundaries.md`
