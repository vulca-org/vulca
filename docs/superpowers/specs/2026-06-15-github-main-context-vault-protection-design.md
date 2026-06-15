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
- `.github/CODEOWNERS` now assigns `/docs/review-context/` to `@yhryzy`.
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
- Do not require two-person review while the repository is operated by a solo
  maintainer; one owner approval is enough for the first protection layer.

## Recommended Mechanism

Use one repository ruleset instead of separate branch protection rules.

Ruleset name:

`protected-main-and-context-vault`

Ruleset target:

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

The ruleset should enforce:

- Require pull request before merging.
- Require at least one approving review.
- Require review from Code Owners.
- Dismiss stale approvals when new commits are pushed.
- Require conversation resolution before merge.
- Require status checks before merge.
- Block force pushes.
- Block branch deletion.

The ruleset should not require linear history in this pass. The current repo has
merge commits on `master`, and changing history policy is a separate workflow
decision.

## Required Status Checks

Initial required checks:

- CI Python 3.11 job.
- CI Python 3.12 job.
- Review Context Vault validation job.

The exact GitHub check context names must be bound after the workflows have run
at least once on GitHub. Expected display names are derived from:

- `.github/workflows/ci.yml`, matrix job `test` for Python 3.11 and 3.12.
- `.github/workflows/review-context.yml`, job `validate`.

Implementation must inspect recent check runs and use the exact context names
reported by GitHub, rather than guessing strings locally.

## Bootstrap Sequence

The context-vault branch currently exists locally but not yet as a protected
remote branch. One bootstrap push is required before the ruleset can fully gate
future updates and before the review-context workflow can produce a check run.

Sequence:

1. Push `codex/vulca-context-vault` to `origin`.
2. Wait for GitHub Actions to run on the pushed branch.
3. Inspect exact check context names from the completed runs.
4. Create the active repository ruleset targeting `master` and
   `codex/vulca-context-vault`.
5. Verify the ruleset through the GitHub API.
6. Optionally attempt a harmless direct-push dry run only if GitHub provides a
   non-mutating way to inspect active rules; otherwise avoid test pushes.

After step 4, future changes to either protected branch must go through PRs.

## Review-Context Interaction

The GitHub ruleset complements, but does not replace, the vault rules:

- `docs/review-context/LOCK.md` defines who may modify vault context.
- `docs/review-context/GOVERNANCE.md` defines request and curator behavior.
- CODEOWNERS makes owner review visible and enforceable.
- the review-context workflow makes the local validator enforceable on PRs.

Other sessions may still read the vault and propose request packets. They should
not directly edit protected vault files or merge their own changes into the
vault branch.

## Failure Handling

If required checks are misnamed and block all merges:

1. Use admin access to edit the ruleset check list.
2. Replace guessed contexts with the exact contexts from recent check runs.
3. Keep PR review, code owner review, force-push block, and deletion block
   enabled while fixing check names.

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
  `protected-main-and-context-vault` with active enforcement.
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
