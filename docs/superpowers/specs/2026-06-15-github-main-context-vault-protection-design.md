# GitHub Main And Context Vault Protection Design

## Status

Approved design for implementation planning.

## Context

The repository is `vulca-org/vulca`. The default branch is `master`.

Current remote protection state checked on 2026-06-15:

- `master` has no branch protection rule.
- repository rulesets are empty.
- local branch `codex/vulca-context-vault` contains the protected review-context
  vault initialization commit and is ahead of `origin/master` by one commit.
- `.github/CODEOWNERS` now assigns `/docs/review-context/` to `@yha9806`.
- `.github/workflows/review-context.yml` now validates review-context vault
  changes.

GitHub CODEOWNERS only becomes an enforcement mechanism when branch protection
or rulesets require code owner review. Without repository-side rules, the local
vault lock is advisory rather than enforced at merge time.

## Goal

Protect both long-lived branches:

- `master`
- `codex/vulca-context-vault`

The practical rule is: no ordinary direct push to either branch. Changes must go
through pull requests, review, and required checks.

## Non-Goals

- Do not protect all `codex/*` branches. Normal Codex feature branches should
  remain cheap to create, update, and discard.
- Do not make PPT, website, or SDK experiment branches immutable.
- Do not add signed-commit enforcement in this pass.
- Do not require approval while the repository is operated by a solo maintainer.
  The first protection layer blocks direct branch mutation through PR-required,
  no-delete, no-force-push, and required-check rules. Approval and code-owner
  review can be re-enabled after a second valid reviewer or team exists.

## Recommended Mechanism

Use repository rulesets instead of classic branch protection rules.

Use one shared base ruleset for both protected branches, then add status-check
rulesets where the required checks differ by branch. This avoids requiring the
full `ci.yml` matrix on `codex/vulca-context-vault`, where CI is not currently
triggered and where full SDK CI would be unnecessary for context-only updates.

Shared base ruleset name:

`protected-main-and-context-vault-base`

Base ruleset target:

branch refs only.

Included refs:

- `refs/heads/master`
- `refs/heads/codex/vulca-context-vault`

Excluded refs:

- none.

Bypass actors:

- none by default.

Emergency bypass should be added only after explicit human instruction. The
default should keep administrators subject to the same merge discipline as other
actors.

## Required Rules

The base ruleset should enforce:

- Require pull request before merging.
- Require zero approving reviews while the repository has only one collaborator.
- Do not require Code Owner review while the repository has only one collaborator.
- Dismiss stale approvals when new commits are pushed.
- Require conversation resolution before merge.
- Block force pushes.
- Block branch deletion.

The ruleset should not require linear history in this pass. The current repo has
merge commits on `master`, and changing history policy is a separate workflow
decision.

## Required Status Check Rulesets

Status checks should be enforced with branch-specific rulesets.

Ruleset name:

`protected-master-required-checks`

Target:

- `refs/heads/master`

Required checks:

- CI Python 3.11 job.
- CI Python 3.12 job.

Do not require the review-context validation job on `master` until
`.github/workflows/review-context.yml` has landed on `master` and a successful
`validate` check has been observed on that branch.

Ruleset name:

`protected-context-vault-required-checks`

Target:

- `refs/heads/codex/vulca-context-vault`

Required checks:

- Review Context Vault validation job.

The `validate` check from `Review Context Vault` must run on every
context-vault PR and push, and can later be required on `master` after the
workflow exists there.
The implementation should remove path filters from `.github/workflows/review-context.yml`
before the rulesets require that check. The validator is lightweight and safe to
run on all protected branch changes.

The exact GitHub check context names must be bound after the workflows have run
at least once on GitHub. Implementation must read the names from GitHub's
commit check-runs API, not from local workflow filenames or UI guesses. Candidate
names are derived from:

- `.github/workflows/ci.yml`, matrix job `test` for Python 3.11 and 3.12.
- `.github/workflows/review-context.yml`, job `validate`.

Implementation must inspect recent check runs and use the exact context names
reported by GitHub.

## Current Applied State

Applied on 2026-06-15:

- `protected-main-and-context-vault-base` id `17697353`
  - active branch ruleset
  - targets `refs/heads/master` and `refs/heads/codex/vulca-context-vault`
  - requires pull requests but currently uses `required_approving_review_count: 0`
  - uses `require_code_owner_review: false`
  - blocks deletion and non-fast-forward updates
  - has no bypass actors
- `protected-master-required-checks` id `17697361`
  - active branch ruleset
  - targets `refs/heads/master`
  - requires `test (3.11)` and `test (3.12)`
  - does not yet require `validate`
- `protected-context-vault-required-checks` id `17697367`
  - active branch ruleset
  - targets `refs/heads/codex/vulca-context-vault`
  - requires `validate`

Reason for staged review settings:

- The repository currently has one collaborator, `yha9806`.
- A one-approval plus code-owner review rule would lock out a solo maintainer.
- `review-context.yml` is not yet on `master`, so requiring `validate` on
  `master` would risk blocking the first PR that lands the workflow.

Follow-up after `review-context.yml` lands on `master` and a valid second
reviewer or team exists:

1. Add `validate` to `protected-master-required-checks`.
2. Re-enable `required_approving_review_count: 1`.
3. Re-enable `require_code_owner_review: true`.

## Bootstrap Sequence

The context-vault branch currently exists locally but not yet as a protected
remote branch. One bootstrap push is required before the ruleset can fully gate
future updates and before the review-context workflow can produce a check run.

Sequence:

1. Remove path filters from `.github/workflows/review-context.yml` and commit the
   workflow change if it has not already been done.
2. Push `codex/vulca-context-vault` to `origin`.
3. Wait for GitHub Actions to run on the pushed branch.
4. Inspect exact check context names from the completed runs.
5. Create the active repository rulesets:
   `protected-main-and-context-vault-base`,
   `protected-master-required-checks`, and
   `protected-context-vault-required-checks`.
6. Verify the rulesets through the GitHub API.
7. Optionally attempt a harmless direct-push dry run only if GitHub provides a
   non-mutating way to inspect active rules; otherwise avoid test pushes.

After step 5, future changes to either protected branch must go through PRs.

## Review-Context Interaction

The GitHub ruleset complements, but does not replace, the vault rules:

- `docs/review-context/LOCK.md` defines who may modify vault context.
- `docs/review-context/GOVERNANCE.md` defines request and curator behavior.
- CODEOWNERS makes ownership visible. Code-owner review becomes enforceable only
  after `require_code_owner_review` is re-enabled and a non-author reviewer or
  team exists.
- the review-context workflow makes the local validator enforceable on PRs and
  pushes to protected branches.

Other sessions may still read the vault and propose request packets. They should
not directly edit protected vault files or merge their own changes into the
vault branch.

## Failure Handling

If required checks are misnamed and block all merges:

1. Use admin access to edit the ruleset check list.
2. Replace guessed contexts with the exact contexts from recent check runs.
3. Keep PR workflow, force-push block, and deletion block enabled while fixing
   check names.

If the review-context workflow itself fails:

1. Treat failure as a blocked vault update.
2. Fix the workflow or validator on a normal branch.
3. Merge through PR after the checks pass.

If a critical emergency requires direct branch repair:

1. Record the human instruction authorizing bypass.
2. Add a temporary bypass actor or temporarily disable the specific failing
   ruleset requirement.
3. Make the smallest repair.
4. Restore the ruleset immediately.
5. Record the incident in the relevant project context or changelog.

## Verification Plan

Before creating the ruleset:

- confirm `gh auth status` has admin-capable credentials.
- confirm current repository metadata with `gh repo view`.
- confirm no existing branch protection/ruleset conflicts.
- confirm the context-vault branch has been pushed and workflows have completed.

After creating the ruleset:

- `gh api repos/vulca-org/vulca/rulesets` should list
  `protected-main-and-context-vault-base`,
  `protected-master-required-checks`, and
  `protected-context-vault-required-checks` with active enforcement.
- `gh api repos/vulca-org/vulca/rules/branches/master` should show active rules
  for `master`.
- `gh api repos/vulca-org/vulca/rules/branches/codex/vulca-context-vault`
  should show active rules for the context-vault branch.

## Source References

- GitHub Docs: About protected branches.
- GitHub Docs: About rulesets.
- GitHub Docs: Available rules for rulesets.
- GitHub Docs: About CODEOWNERS and branch protection.
- GitHub Docs: REST API endpoints for repository rulesets.
