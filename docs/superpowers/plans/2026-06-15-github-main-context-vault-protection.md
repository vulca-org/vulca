# GitHub Main And Context Vault Protection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce GitHub repository-side protection for `master` and `codex/vulca-context-vault` so both branches require PR workflow and checks before updates.

**Architecture:** Use three GitHub repository rulesets: one shared base ruleset for PR-required/no-force-push/no-delete behavior, one master-only status-check ruleset, and one context-vault-only status-check ruleset. Keep master checks to existing CI; under the branch-only vault decision, only `codex/vulca-context-vault` is gated by the lightweight `validate` job.

**Tech Stack:** Git, GitHub CLI (`gh`), GitHub REST repository rulesets API, GitHub Actions, Python 3.

---

## File Structure

- Modify: `.github/workflows/review-context.yml`
  - Scope the workflow to `codex/vulca-context-vault` so the `validate` check appears on every context-vault PR/push without making it a `master` requirement.
- Read: `.github/workflows/ci.yml`
  - Confirm CI matrix job names before binding required checks for `master`.
- Read: `docs/superpowers/specs/2026-06-15-github-main-context-vault-protection-design.md`
  - Implementation source of truth.
- No committed script file is required.
  - Ruleset payloads are generated into `/tmp/vulca-rulesets/` during execution and are not repository artifacts.

## Task 1: Make Review Context Gate Always Runnable

**Files:**
- Modify: `.github/workflows/review-context.yml`
- Test: `python3 docs/review-context/gates/validate_review_context.py`
- Test: `python3 -m pytest tests/test_review_context_vault.py -q`
- Test: `git diff --check`

- [ ] **Step 1: Remove path filters from the workflow trigger**

Edit `.github/workflows/review-context.yml` to this exact content:

```yaml
name: Review Context Vault

on:
  pull_request:
    branches: [codex/vulca-context-vault]
  push:
    branches: [codex/vulca-context-vault]

concurrency:
  group: review-context-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: Install test runner
        run: |
          python -m pip install --upgrade pip
          python -m pip install pytest
      - name: Validate review context vault
        run: python docs/review-context/gates/validate_review_context.py
      - name: Test review context validator
        run: python -m pytest tests/test_review_context_vault.py -q
```

- [ ] **Step 2: Run the review-context validator**

Run:

```bash
python3 docs/review-context/gates/validate_review_context.py
```

Expected output:

```text
review-context gate passed
```

- [ ] **Step 3: Run the validator unit tests**

Run:

```bash
python3 -m pytest tests/test_review_context_vault.py -q
```

Expected output includes:

```text
4 passed
```

- [ ] **Step 4: Check whitespace**

Run:

```bash
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 5: Commit the workflow change**

Run:

```bash
git add .github/workflows/review-context.yml
git commit -m "ci: run review context gate on protected branches"
```

Expected: one commit modifying `.github/workflows/review-context.yml`.

## Task 2: Push Bootstrap Branch And Wait For Actions

**Files:**
- No local file changes.

- [ ] **Step 1: Confirm clean local state before push**

Run:

```bash
git status --short --branch
```

Expected output shape:

```text
## codex/vulca-context-vault...origin/master [ahead 4]
```

The ahead count may be higher if this plan has already been amended, but there
must be no uncommitted file entries below the branch line.

- [ ] **Step 2: Push the context-vault branch**

Run:

```bash
git push -u origin codex/vulca-context-vault
```

Expected: Git creates or updates `origin/codex/vulca-context-vault`.

- [ ] **Step 3: Confirm upstream tracking**

Run:

```bash
git status --short --branch
```

Expected output:

```text
## codex/vulca-context-vault...origin/codex/vulca-context-vault
```

- [ ] **Step 4: Wait for review-context workflow completion on the pushed branch**

Run:

```bash
gh run list \
  --repo vulca-org/vulca \
  --branch codex/vulca-context-vault \
  --workflow review-context.yml \
  --limit 5 \
  --json databaseId,status,conclusion,headSha,url
```

Expected: at least one run for the pushed head SHA with `"status":"completed"` and `"conclusion":"success"`.

- [ ] **Step 5: Wait for the run if it is still in progress**

If Step 4 shows a queued or in-progress run, run:

```bash
RUN_DATABASE_ID="$(gh run list --repo vulca-org/vulca --branch codex/vulca-context-vault --workflow review-context.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
gh run watch "$RUN_DATABASE_ID" --repo vulca-org/vulca --exit-status
```

Expected: command exits 0.

## Task 3: Discover Exact Required Check Contexts

**Files:**
- No local file changes.

- [ ] **Step 1: Capture latest review-context check-run name**

Run:

```bash
CONTEXT_HEAD_SHA="$(git rev-parse HEAD)"
gh api "repos/vulca-org/vulca/commits/$CONTEXT_HEAD_SHA/check-runs" \
  --jq '.check_runs[].name'
```

Expected output contains a check-run name ending in:

```text
validate
```

Record the exact name:

```bash
REVIEW_CONTEXT_CHECK="$(gh api "repos/vulca-org/vulca/commits/$CONTEXT_HEAD_SHA/check-runs" --jq '.check_runs[].name' | grep -E '(^|/) ?validate$' | head -n 1)"
printf '%s\n' "$REVIEW_CONTEXT_CHECK"
```

Expected: one non-empty line containing the exact review-context check-run name.

- [ ] **Step 2: Capture existing CI matrix check-run names from master**

Run:

```bash
CI_RUN_ID="$(gh run list --repo vulca-org/vulca --branch master --workflow ci.yml --status success --limit 1 --json databaseId --jq '.[0].databaseId')"
MASTER_CI_SHA="$(gh run view "$CI_RUN_ID" --repo vulca-org/vulca --json headSha --jq '.headSha')"
gh api "repos/vulca-org/vulca/commits/$MASTER_CI_SHA/check-runs" \
  --jq '.check_runs[].name'
```

Expected output contains two matrix jobs equivalent to:

```text
test (3.11)
test (3.12)
```

Record the exact names:

```bash
MASTER_CHECK_311="$(gh api "repos/vulca-org/vulca/commits/$MASTER_CI_SHA/check-runs" --jq '.check_runs[].name' | grep -E '(^|/) ?test \(3\.11\)$' | head -n 1)"
MASTER_CHECK_312="$(gh api "repos/vulca-org/vulca/commits/$MASTER_CI_SHA/check-runs" --jq '.check_runs[].name' | grep -E '(^|/) ?test \(3\.12\)$' | head -n 1)"
printf '%s\n%s\n' "$MASTER_CHECK_311" "$MASTER_CHECK_312"
```

Expected: two non-empty lines containing the exact CI check-run names.

- [ ] **Step 3: Record contexts as shell variables**

Run:

```bash
test -n "$MASTER_CHECK_311"
test -n "$MASTER_CHECK_312"
test -n "$REVIEW_CONTEXT_CHECK"
export MASTER_CHECK_311
export MASTER_CHECK_312
export REVIEW_CONTEXT_CHECK
printf '%s\n%s\n%s\n' "$MASTER_CHECK_311" "$MASTER_CHECK_312" "$REVIEW_CONTEXT_CHECK"
```

Expected: three non-empty lines. The names are the exact contexts to write into
the required-status-check rulesets.

Keep this shell open for Task 4, or rerun Task 3 before generating payloads.

## Task 4: Create GitHub Ruleset Payloads

**Files:**
- Create local temporary files only: `/tmp/vulca-rulesets/base.json`
- Create local temporary files only: `/tmp/vulca-rulesets/master-checks.json`
- Create local temporary files only: `/tmp/vulca-rulesets/context-checks.json`

- [ ] **Step 1: Generate payload files**

Run:

```bash
mkdir -p /tmp/vulca-rulesets
python3 - <<'PY'
import os
import json
from pathlib import Path

out = Path("/tmp/vulca-rulesets")
master_check_311 = os.environ["MASTER_CHECK_311"]
master_check_312 = os.environ["MASTER_CHECK_312"]
review_context_check = os.environ["REVIEW_CONTEXT_CHECK"]

base = {
    "name": "protected-main-and-context-vault-base",
    "target": "branch",
    "enforcement": "active",
    "bypass_actors": [],
    "conditions": {
        "ref_name": {
            "include": [
                "refs/heads/master",
                "refs/heads/codex/vulca-context-vault",
            ],
            "exclude": [],
        },
    },
    "rules": [
        {
            "type": "pull_request",
            "parameters": {
                "allowed_merge_methods": ["merge", "squash", "rebase"],
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": False,
                "require_last_push_approval": False,
                "required_approving_review_count": 0,
                "required_review_thread_resolution": True,
            },
        },
        {"type": "deletion"},
        {"type": "non_fast_forward"},
    ],
}

master_checks = {
    "name": "protected-master-required-checks",
    "target": "branch",
    "enforcement": "active",
    "bypass_actors": [],
    "conditions": {
        "ref_name": {
            "include": ["refs/heads/master"],
            "exclude": [],
        },
    },
    "rules": [
        {
            "type": "required_status_checks",
            "parameters": {
                "strict_required_status_checks_policy": True,
                "required_status_checks": [
                    {"context": master_check_311},
                    {"context": master_check_312},
                ],
            },
        },
    ],
}

context_checks = {
    "name": "protected-context-vault-required-checks",
    "target": "branch",
    "enforcement": "active",
    "bypass_actors": [],
    "conditions": {
        "ref_name": {
            "include": ["refs/heads/codex/vulca-context-vault"],
            "exclude": [],
        },
    },
    "rules": [
        {
            "type": "required_status_checks",
            "parameters": {
                "strict_required_status_checks_policy": True,
                "required_status_checks": [
                    {"context": review_context_check},
                ],
            },
        },
    ],
}

for name, payload in {
    "base.json": base,
    "master-checks.json": master_checks,
    "context-checks.json": context_checks,
}.items():
    (out / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
```

Expected: the three JSON files are created under `/tmp/vulca-rulesets/`.

- [ ] **Step 2: Review payload names and target refs**

Run:

```bash
python3 - <<'PY'
import json
from pathlib import Path

for path in sorted(Path("/tmp/vulca-rulesets").glob("*.json")):
    payload = json.loads(path.read_text())
    refs = payload["conditions"]["ref_name"]["include"]
    print(path.name, payload["name"], refs)
    for rule in payload["rules"]:
        if rule["type"] == "required_status_checks":
            contexts = [check["context"] for check in rule["parameters"]["required_status_checks"]]
            print("  checks:", contexts)
PY
```

Expected output contains the three ruleset files and their target refs:

```text
base.json protected-main-and-context-vault-base ['refs/heads/master', 'refs/heads/codex/vulca-context-vault']
context-checks.json protected-context-vault-required-checks ['refs/heads/codex/vulca-context-vault']
master-checks.json protected-master-required-checks ['refs/heads/master']
```

The printed check names must match the values from Task 3 exactly.

In the initial solo-maintainer rollout, expected checks are:

- `master-checks.json`: `test (3.11)`, `test (3.12)`
- `context-checks.json`: `validate`

Do not put `validate` in `master-checks.json` under the branch-only vault
decision. Any future change that makes `master` require `validate` must first
record an explicit governance decision to move or mirror the vault workflow onto
`master`.

## Task 5: Create Repository Rulesets

**Files:**
- No local file changes.

- [ ] **Step 1: Confirm no conflicting rulesets exist**

Run:

```bash
gh api repos/vulca-org/vulca/rulesets --jq '.[].name'
```

Expected before first creation: none of these names are present:

```text
protected-main-and-context-vault-base
protected-master-required-checks
protected-context-vault-required-checks
```

- [ ] **Step 2: Create the shared base ruleset**

Run:

```bash
gh api \
  --method POST \
  repos/vulca-org/vulca/rulesets \
  --input /tmp/vulca-rulesets/base.json \
  --jq '{id,name,enforcement,target}'
```

Expected output contains:

```json
{"name":"protected-main-and-context-vault-base","enforcement":"active","target":"branch"}
```

- [ ] **Step 3: Create the master status-check ruleset**

Run:

```bash
gh api \
  --method POST \
  repos/vulca-org/vulca/rulesets \
  --input /tmp/vulca-rulesets/master-checks.json \
  --jq '{id,name,enforcement,target}'
```

Expected output contains:

```json
{"name":"protected-master-required-checks","enforcement":"active","target":"branch"}
```

- [ ] **Step 4: Create the context-vault status-check ruleset**

Run:

```bash
gh api \
  --method POST \
  repos/vulca-org/vulca/rulesets \
  --input /tmp/vulca-rulesets/context-checks.json \
  --jq '{id,name,enforcement,target}'
```

Expected output contains:

```json
{"name":"protected-context-vault-required-checks","enforcement":"active","target":"branch"}
```

## Task 6: Verify Active Protection

**Files:**
- No local file changes.

- [ ] **Step 1: List repository rulesets**

Run:

```bash
gh api repos/vulca-org/vulca/rulesets --jq '.[] | {id,name,enforcement,target}'
```

Expected: all three rulesets appear with `"enforcement":"active"`.

- [ ] **Step 2: Verify active rules on master**

Run:

```bash
gh api repos/vulca-org/vulca/rules/branches/master --jq '.[] | .type'
```

Expected output includes:

```text
pull_request
deletion
non_fast_forward
required_status_checks
```

- [ ] **Step 3: Verify active rules on context-vault branch**

Run:

```bash
gh api repos/vulca-org/vulca/rules/branches/codex%2Fvulca-context-vault --jq '.[] | .type'
```

Expected output includes:

```text
pull_request
deletion
non_fast_forward
required_status_checks
```

- [ ] **Step 4: Verify required status check contexts on both branches**

Run:

```bash
MASTER_RULE_CHECKS="$(gh api repos/vulca-org/vulca/rules/branches/master --jq '.[] | select(.type == "required_status_checks") | .parameters.required_status_checks[].context')"
CONTEXT_RULE_CHECKS="$(gh api repos/vulca-org/vulca/rules/branches/codex%2Fvulca-context-vault --jq '.[] | select(.type == "required_status_checks") | .parameters.required_status_checks[].context')"
printf 'master:\n%s\ncontext vault:\n%s\n' "$MASTER_RULE_CHECKS" "$CONTEXT_RULE_CHECKS"
printf '%s\n' "$MASTER_RULE_CHECKS" | grep -Fx "$MASTER_CHECK_311"
printf '%s\n' "$MASTER_RULE_CHECKS" | grep -Fx "$MASTER_CHECK_312"
printf '%s\n' "$CONTEXT_RULE_CHECKS" | grep -Fx "$REVIEW_CONTEXT_CHECK"
```

Expected: all three `grep -Fx` commands echo the matching check name and exit 0.
`master` should not require `validate` in the initial rollout.

## Task 7: Final Local Verification And Handoff

**Files:**
- No local file changes.

- [ ] **Step 1: Confirm local worktree is clean after remote setup**

Run:

```bash
git status --short --branch
```

Expected: branch line only, with no uncommitted files.

- [ ] **Step 2: Record final ruleset ids**

Run:

```bash
gh api repos/vulca-org/vulca/rulesets \
  --jq '.[] | select(.name | startswith("protected-")) | {id,name,enforcement}'
```

Expected: three protected rulesets are listed with ids.

- [ ] **Step 3: Report completion with evidence**

Report:

- pushed branch name
- latest commit hash on `codex/vulca-context-vault`
- three ruleset names and ids
- active rules observed on `master`
- active rules observed on `codex/vulca-context-vault`
- workflow/check results used to bind required checks

## Rollback Plan

Use this only after explicit human instruction.

```bash
for id in $(gh api repos/vulca-org/vulca/rulesets --jq '.[] | select(.name == "protected-main-and-context-vault-base" or .name == "protected-master-required-checks" or .name == "protected-context-vault-required-checks") | .id'); do
  gh api --method DELETE "repos/vulca-org/vulca/rulesets/$id"
done
```

Expected after rollback:

```bash
gh api repos/vulca-org/vulca/rulesets --jq '.[].name'
```

does not print the three protected ruleset names.
