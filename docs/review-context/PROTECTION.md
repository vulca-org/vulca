# Review Context Protection

Vault status: protected branch and repository guardrail record.

## Branch-Only Decision

The review-context vault is intentionally kept on
`codex/vulca-context-vault`.

`master` is the protected product mainline. It must not become the working copy
of the vault unless a future human instruction explicitly reverses this
decision and records the reason in this vault.

Current rule:

- `codex/vulca-context-vault` owns `docs/review-context/` and its validation
  gate.
- `master` may link to or read from the vault, but it does not carry the vault
  as a required context artifact.
- The `validate` status check is required on `codex/vulca-context-vault`.
- The `validate` status check is not required on `master`.

## Live Repository Protection

As of 2026-06-15, GitHub repository rulesets protect both long-lived branches:

- `protected-main-and-context-vault-base` targets `master` and
  `codex/vulca-context-vault`.
- `protected-master-required-checks` targets `master`.
- `protected-context-vault-required-checks` targets
  `codex/vulca-context-vault`.

The shared base ruleset requires pull requests, blocks deletion, blocks
non-fast-forward updates, and has no bypass actors.

The master status-check ruleset requires:

- `test (3.11)`
- `test (3.12)`

The context-vault status-check ruleset requires:

- `validate`

While the repository has only one maintainer, the shared pull-request rule uses
`required_approving_review_count: 0` and
`require_code_owner_review: false` to avoid a solo-maintainer lockout. Code
owner review can be re-enabled only after a second valid reviewer or team exists.

## Related Platform Repository Protection

As of 2026-06-15, `yha9806/vulca-platform` is a private repository. GitHub's
branch-protection and ruleset APIs returned HTTP 403 with the message that the
feature requires GitHub Pro or a public repository. Therefore, the platform
repository cannot currently enforce the same hard no-direct-push rule through
GitHub branch protection.

Operational rule until the repository is upgraded or made public:

- do not push directly to `master`;
- push product work to `codex/*` branches;
- use PRs for `master` integration;
- treat `Run Tests` and `security` as required evidence even when GitHub cannot
  technically enforce them;
- record any exception in this vault before merging.

Once GitHub protection becomes available for `yha9806/vulca-platform`, mirror
the context-vault rule shape: require pull requests, block deletion, block
non-fast-forward updates, configure no bypass actors by default, and require
`Run Tests` plus `security` for `master`.

### Platform CI Hygiene

As of 2026-06-15, `yha9806/vulca-platform` PR #33,
`[codex] Update GitHub Actions for Node 24`, merged to `master` at
`0a7dd392de1eb24eacd245e91cb3c2d0234a5f81`.

That PR updated the platform workflows to current Node 24-compatible action
pins:

- `actions/checkout@v6.0.3`
- `actions/setup-node@v6.4.0`
- `actions/setup-python@v6.2.0`
- `gitleaks/gitleaks-action@v3.0.0`

Its PR gate passed `Run Tests` and `security`; the deploy job remained skipped
for the PR event.

## Modification Path

Reader sessions may:

- read this vault;
- cite this vault;
- create a request packet using `requests/TEMPLATE.md`;
- open a normal PR that proposes a request packet.

Reader sessions must not:

- directly edit protected vault files during unrelated SDK, website, PPT,
  Workspace, release, or copywriting work;
- merge their own context changes into `codex/vulca-context-vault`;
- move the vault into `master` as a side effect of another change.

Only a context-curator session may modify the vault. The curator must update the
relevant vault files, update `CHANGELOG.md` and `MANIFEST.json` when the
protected context inventory changes, run the local validation gate, and merge
through the protected branch workflow.

## Emergency Changes

Emergency bypass is not configured by default.

If a critical repair requires temporary bypass:

1. Record the human instruction authorizing the bypass.
2. Temporarily adjust only the failing ruleset requirement.
3. Make the smallest repair.
4. Restore the ruleset immediately.
5. Record the incident in this vault.

## Sources

- Repository rulesets verified through the GitHub API on 2026-06-15.
- `yha9806/vulca-platform` protection and ruleset API checks on 2026-06-15.
- `yha9806/vulca-platform` PR #33.
- Context-vault branch: `codex/vulca-context-vault`.
- GitHub user owner in `.github/CODEOWNERS`: `@yha9806`.
