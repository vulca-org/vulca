# Release Readiness Reports

Vault status: protected release-readiness workflow.

This folder contains the fixed report template for applying
`14-release-readiness-evidence-gate.md`.

Use `TEMPLATE.md` whenever a session proposes to upgrade a feature, demo,
website/PPT claim, public example, or Workspace workflow from draft, preview,
internal, or public-blocked status toward a stronger release level.

Other sessions may copy the template into a feature branch or request packet.
They must not edit this folder directly outside a context-curator branch.

## Report Rules

- Default public release state is blocked until evidence is attached.
- Every gate must be marked pass, blocked, or not applicable with a reason.
- Evidence links must be concrete paths, commits, PRs, test runs, screenshots,
  or reviewed artifacts.
- Agent/system results may support review but cannot be recorded as human
  release approval.
- A human owner must be recorded before any release status upgrade.

## Sources

- `docs/review-context/14-release-readiness-evidence-gate.md`
- `docs/review-context/13-website-ppt-claim-spine.md`
- `docs/review-context/09-claim-boundaries.md`
