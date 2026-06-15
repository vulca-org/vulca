# Review Context Governance

Vault status: protected governance.

## Purpose

This governance file defines how the VULCA project memory is updated without
letting normal sessions overwrite hard-won context.

The vault exists because VULCA has multiple active surfaces:

- Python SDK / MCP execution engine.
- Claude / Codex / ChatGPT agent surfaces.
- VULCA Workspace product UI.
- `vulcaart.art` commercial website.
- PPT / deck proof lab.
- Learning-loop and case-record experiments.

Without a protected context branch, each surface can accidentally invent a new
story and lose the technical history behind layering, prompt control, redraw,
mask gates, and product boundaries.

## Roles

### Reader Session

Any future session may read the vault. Reader sessions use this folder to align
product decisions, claims, implementation plans, and copy.

Reader sessions must not directly edit protected files.

### Requesting Session

A requesting session creates a request packet in `requests/` or in its own
branch with the same template. It proposes a concrete change and cites evidence.

Requesting sessions do not merge their own request into the vault.

### Context-Curator Session

A context-curator session reviews request packets, checks source evidence,
updates vault files, runs gates, and commits the result.

The curator is responsible for preserving boundaries and rejecting weak claims.

## Request Packet Requirements

Every request must include:

- request id
- requester branch or session
- proposed files to change
- reason for change
- source evidence
- exact proposed text or precise patch description
- claim risk
- whether human confirmation is required
- rollback note

Use `requests/TEMPLATE.md`.

## Gate Requirements

Every curator change must pass four gates.

### 1. Source Gate

Claims must point to one of:

- repository file path
- commit hash
- test name or command
- branch state
- external source explicitly reviewed elsewhere
- human instruction from the current session

Unsupported synthesis must be labeled as synthesis.

### 2. Claim Boundary Gate

Do not upgrade a claim beyond its evidence. Internal proof stays internal.
Blocked assets stay blocked. AI-assisted review stays AI-assisted unless a human
confirmation field says otherwise.

### 3. Request Gate

Normal edits require a request packet. Emergency edits are allowed only when the
user explicitly instructs the curator to modify the vault directly; the curator
must still record the reason in `CHANGELOG.md`.

### 4. Validation Gate

Run:

```bash
python3 docs/review-context/gates/validate_review_context.py
```

The gate must pass before commit.

Pull requests that touch the vault also run `.github/workflows/review-context.yml`,
which executes the gate and its validator tests.

## Branch Boundary

The vault is branch-only by current human decision.

- `codex/vulca-context-vault` is the protected context branch.
- `master` is the protected product mainline.
- `master` does not carry the vault as a required context artifact.
- `master` does not require the `validate` review-context status check.
- Moving the vault into `master` requires a new explicit human instruction and
  a governance update in this folder.

## Repository Guardrails

The vault relies on both local and repository-level controls:

- `.github/CODEOWNERS` assigns `/docs/review-context/` to `@yha9806`.
- `.github/workflows/review-context.yml` runs the validator on
  `codex/vulca-context-vault` PRs and pushes.
- `tests/test_review_context_vault.py` checks the validator catches missing files,
  missing request-lock checklist items, and forbidden claim upgrades.
- GitHub rulesets protect `master` and `codex/vulca-context-vault` from direct
  branch mutation, deletion, and non-fast-forward updates.
- `protected-context-vault-required-checks` requires the `validate` status check
  on `codex/vulca-context-vault`.
- `protected-master-required-checks` requires only the existing CI checks on
  `master`: `test (3.11)` and `test (3.12)`.

These controls do not replace curator judgment. They make bypasses visible in
review and keep future sessions from silently weakening the context lock.

## Commit Policy

Context vault commits should be small and descriptive.

Good examples:

- `docs: initialize protected review context vault`
- `docs: add redraw history to review context vault`
- `docs: accept workspace product model context request`

Avoid mixed commits that also change SDK, website, product UI, or PPT code.

## What Requires Human Confirmation

Human confirmation is required before recording:

- a public release claim
- a final adjudication
- a claim that an artifact is production-quality
- a claim that a review or evaluation is human-approved
- a governance rule change that weakens this lock

## What Does Not Require Human Confirmation

The curator may record factual source-backed context such as:

- a commit exists
- a test passed or failed
- a branch is ahead/behind
- a file contains a stated design
- a feature is implemented in code
- an artifact is labeled `public_blocked`

The curator must still cite the source.
