# Plugin Sync + README Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore a working agent-native install path (`vulca-plugin` v0.9.0 → v0.16.1 with the `/decompose` skill bundled) and ship the main-repo README refresh that converts MCP/Claude Code-curious cold visitors by naming agents as the protagonist.

**Architecture:** Two sequential phases across two git repositories. Phase 1 modifies `vulca-org/vulca-plugin` (external repo; clone to `~/dev/vulca-plugin` if absent). Phase 2 modifies `vulca-org/vulca` (CWD `/Users/yhryzy/dev/vulca`). A hard verification gate between them: Phase 2 does not start until Phase 1's clean-install test passes and saves `verification-tools-v0.16.1.txt`. Codex + superpowers parallel code review runs before merging each phase's PR.

**Tech Stack:** Git + gh CLI, Python 3.10+ venv, `pip` for vulca[mcp], `claude plugin install` via Claude Code, `uv/uvx` for MCP runner, `CronCreate` for rollback scheduling, `curl`/`jq` for verification.

**Spec:** `docs/superpowers/specs/2026-04-20-plugin-sync-and-readme-refresh-design.md` (commit `ba5a562`).

---

## Task index

### Pre-flight (can run in any order)
- **T0.1** Verify current working tree state (vulca main repo)
- **T0.2** [PARALLEL] File GitHub issue — `vulca[all]` extras mismatch
- **T0.3** [PARALLEL] File GitHub issue — plugin release cadence automation
- **T0.4** [PARALLEL] Resolve EMNLP URL redirect to canonical form

### Phase 1 — vulca-plugin sync to v0.16.1
- **T1.1** Clone or refresh local `vulca-plugin` checkout, create working branch
- **T1.2** [PARALLEL candidate A] Update `.claude-plugin/plugin.json`
- **T1.3** [PARALLEL candidate A] Update `.claude-plugin/marketplace.json`
- **T1.4** Delete 10 empty skill subdirectories + `agents/cultural-critic.md`
- **T1.5** Copy `/decompose` SKILL.md from main repo into plugin `skills/decompose/`
- **T1.6** Rewrite plugin's own `README.md`
- **T1.7** Commit, push, open Phase 1 PR
- **T1.8** [PARALLEL] Dispatch codex + superpowers parallel review on Phase 1 PR
- **T1.9** Address review feedback, merge, tag `v0.16.1`, push tag
- **T1.10** Create GitHub release `v0.16.1` on vulca-plugin

### Gate — Phase 1 clean-install verification
- **T1.G1** Rename aside existing `~/.claude/plugins/vulca*` + `~/.claude/skills/decompose/`
- **T1.G2** Fresh venv install + tag-pinned plugin install
- **T1.G3** Verify `/decompose` auto-discovery + reaches `layers_split` tool call
- **T1.G4** Capture exact 21-tool list to `verification-tools-v0.16.1.txt`
- **T1.G5** Restore aside directories; commit verification artifact to main repo

### Phase 2 — main README refresh
- **T2.1** Create Phase 2 branch `phase2-readme-refresh` from latest master
- **T2.2** Write the full new `README.md` (single pass, acceptance-criteria-driven)
- **T2.3** Run every Phase 2 grep/line-count acceptance check, fix violations inline
- **T2.4** Apply UTM tags to every non-github.com non-pypi.org link
- **T2.5** Update GitHub About description via `gh api`
- **T2.6** Update GitHub topics to the 14-topic final set
- **T2.7** Register `CronCreate` trigger for 2026-05-04 traffic review
- **T2.8** Commit, push, open Phase 2 PR
- **T2.9** [PARALLEL] Dispatch codex + superpowers parallel review on Phase 2 PR
- **T2.10** Address review feedback, merge PR
- **T2.11** Supersede `memory/project_readme_refresh_pending.md` as complete

### Post-merge
- **T3.1** Schedule a 2026-05-04 traffic review memory write when Cron fires

---

## Pre-flight tasks

### T0.1 — Verify current working tree state

**Files:** none (diagnostic)

**Acceptance criterion mapping:** safeguard — protects Phase 2 "Main-repo README.md replaced per Structure section" by ensuring a clean baseline.

- [ ] **Step 1: Capture current git state**

```bash
cd /Users/yhryzy/dev/vulca
git status --short | head -60
git log -1 --format='%h %s'
git branch --show-current
```

Expected: current branch is `master`; HEAD is `ba5a562` (the spec commit) or later.

- [ ] **Step 2: Stash or commit any unrelated in-flight work**

```bash
# If there are uncommitted changes unrelated to this plan, stash them:
git stash push -m "pre-plan-stash-2026-04-20" --include-untracked
```

Do NOT `git restore` or `git clean`; those are destructive. Stash preserves.

- [ ] **Step 3: Confirm no destructive state**

```bash
git diff --stat HEAD
```

Expected: clean or only the plan file itself untracked. If anything else modified, reconcile before proceeding.

- [ ] **Step 4: No commit — this is a read-only check**

---

### T0.2 — File issue: `vulca[all]` extras mismatch

**Files:** none (creates a GitHub issue)

**Acceptance criterion mapping:** Spec open question #2 — resolution per `feedback_release_checklist`.

- [ ] **Step 1: Read current `pyproject.toml` line 99**

```bash
sed -n '95,105p' /Users/yhryzy/dev/vulca/pyproject.toml
```

Confirm the reported mismatch (`vulca[all] = [vulca[layers,tools,mcp,scout]]` but `layers` and `scout` extras are not defined).

- [ ] **Step 2: File the issue via `gh`**

```bash
gh issue create \
  --repo vulca-org/vulca \
  --title "pyproject.toml: vulca[all] references undefined extras (layers, scout)" \
  --body "$(cat <<'EOF'
## Summary
`pyproject.toml` line 99 declares `all = [vulca[layers,tools,mcp,scout]]` but the `[project.optional-dependencies]` section only defines `tools`, `mcp`, `layers-full`. The `layers` and `scout` names do not exist, which will cause `pip install vulca[all]` to fail (or silently skip the unknown extras depending on the resolver).

## Impact
Users copy-pasting the current README's "Optional extras" block (`pip install vulca[layers-full]` is fine; `pip install vulca[all]` is the broken path) hit an install error.

## Proposed fix
Either:
1. Rename `layers-full` → `layers` (breaking change, requires README update) and drop `scout` from the list, OR
2. Update `all` to reference the actual defined extras: `all = [vulca[layers-full,tools,mcp]]`

Option 2 is the minimal fix.

## Context
Surfaced during the 2026-04-20 README refresh design spec (`docs/superpowers/specs/2026-04-20-plugin-sync-and-readme-refresh-design.md` open question #2). Deferred out of that spec's scope.

## Priority
Before next SDK release (v0.17.x).
EOF
)" \
  --label "bug"
```

Expected: `https://github.com/vulca-org/vulca/issues/N` printed.

- [ ] **Step 3: No commit — issue is filed in GitHub**

---

### T0.3 — File issue: plugin release cadence automation

**Files:** none (creates a GitHub issue)

**Acceptance criterion mapping:** Spec open question #3.

- [ ] **Step 1: File the issue via `gh`**

```bash
gh issue create \
  --repo vulca-org/vulca \
  --title "Propose scripts/sync_plugin.py to prevent vulca-plugin drift" \
  --body "$(cat <<'EOF'
## Summary
The 2026-04-20 README refresh cycle discovered that `vulca-org/vulca-plugin` was 13 days stale (v0.9.0 vs. SDK v0.16.1) with a tool table referring to Phase-1-removed tools and 10 empty skill directories. This drift was invisible from the SDK side and caused the plugin install path in the main README to silently break.

## Proposed solution
Add `scripts/sync_plugin.py` that, on each SDK release:
1. Reads the MCP tool list from `src/vulca/mcp_server.py` (grep `@mcp.tool()` + extract function names)
2. Reads the currently-shipped agent skill files from `.claude/skills/*/SKILL.md`
3. Regenerates `vulca-plugin/.claude-plugin/plugin.json`, `marketplace.json`, and `README.md` tool table
4. Copies skill files from main repo to plugin repo
5. Opens a sync PR on vulca-plugin with the canonical diff

Gate behind the `memory/feedback_release_checklist.md` — add "Run `scripts/sync_plugin.py` before tagging" to the checklist.

## Out of scope for this issue
Actual implementation. This issue tracks the proposal + design; implementation happens when the next SDK release (v0.17.x) is staged.

## Context
Surfaced during the 2026-04-20 README refresh design spec. Deferred out of that spec's scope.
EOF
)" \
  --label "enhancement"
```

Expected: issue URL printed.

- [ ] **Step 2: No commit**

---

### T0.4 — Resolve EMNLP URL redirect

**Files:** Modify (later, in T2.2): `README.md`

**Acceptance criterion mapping:** Spec open question #1.

- [ ] **Step 1: Resolve the 301 redirect**

```bash
curl -Ls -o /dev/null -w '%{url_effective}\n' https://aclanthology.org/2025.findings-emnlp/
```

Expected: an HTTP 200 URL, likely `https://aclanthology.org/events/findings-2025/` or `https://aclanthology.org/volumes/2025.findings-emnlp/`.

- [ ] **Step 2: If redirect lands on an unstable aggregator page (volumes, events), fall back to the arXiv version**

```bash
# The known-good arXiv URLs from the current README:
curl -s -o /dev/null -w '%{http_code}\n' https://arxiv.org/abs/2601.07986   # VULCA-Bench
curl -s -o /dev/null -w '%{http_code}\n' https://arxiv.org/abs/2601.07984   # Art Critique
```

Both are already known 200 per 2026-04-20 verification. For the VULCA Framework citation, pick:
- Preferred: the resolved ACL Anthology per-paper URL if stable
- Fallback: `https://arxiv.org/abs/2601.07986` (VULCA-Bench arXiv) or whatever the ACL paper maps to

- [ ] **Step 3: Record the chosen URL for T2.2**

```bash
echo "Chosen EMNLP URL: <paste from step 1 or 2>" > /tmp/emnlp-url-2026-04-20.txt
```

T2.2 reads this file when transcribing research-lineage citations.

- [ ] **Step 4: No commit** — the URL fix lands inside T2.2's README.md write.

---

## Phase 1 — vulca-plugin sync to v0.16.1

### T1.1 — Clone or refresh vulca-plugin, create working branch

**Files:**
- Clone to: `/Users/yhryzy/dev/vulca-plugin` (or existing location if already cloned)

**Acceptance criterion mapping:** precondition for Phase 1 AC #1 "Plugin repo tagged `v0.16.1`".

- [ ] **Step 1: Check if plugin repo is already cloned**

```bash
if [ -d /Users/yhryzy/dev/vulca-plugin/.git ]; then
  echo "EXISTING"
else
  echo "CLONE_NEEDED"
fi
```

- [ ] **Step 2a: If CLONE_NEEDED — clone it**

```bash
cd /Users/yhryzy/dev
git clone git@github.com:vulca-org/vulca-plugin.git
cd vulca-plugin
```

- [ ] **Step 2b: If EXISTING — fetch + fast-forward master**

```bash
cd /Users/yhryzy/dev/vulca-plugin
git fetch origin
git checkout master
git pull --ff-only origin master
```

If pull fails (non-ff), stop and investigate — do not force anything.

- [ ] **Step 3: Create working branch**

```bash
cd /Users/yhryzy/dev/vulca-plugin
git checkout -b phase1-sync-v0.16.1
```

- [ ] **Step 4: Confirm branch**

```bash
git branch --show-current
```

Expected: `phase1-sync-v0.16.1`.

- [ ] **Step 5: No commit yet — branch creation is local setup**

---

### T1.2 — Update `.claude-plugin/plugin.json`

**Files:**
- Modify: `/Users/yhryzy/dev/vulca-plugin/.claude-plugin/plugin.json`

**Acceptance criterion mapping:** Phase 1 AC — "plugin.json has `"version": "0.16.1"` and description contains the substring `"21 MCP tools"`".

- [ ] **Step 1: Read current content**

```bash
cat /Users/yhryzy/dev/vulca-plugin/.claude-plugin/plugin.json
```

Expected: shows `"version": "0.9.0"` and the stale description.

- [ ] **Step 2: Write new content**

Replace entire file contents with:

```json
{
  "name": "vulca",
  "description": "Agent-native image-editing MCP surface for Claude Code & Cursor. 21 MCP tools + /decompose skill. Powered by vulca SDK.",
  "version": "0.16.1",
  "author": {
    "name": "Yu Haorui",
    "email": "yuhaorui48@gmail.com"
  },
  "homepage": "https://pypi.org/project/vulca/",
  "repository": "https://github.com/vulca-org/vulca-plugin",
  "license": "Apache-2.0",
  "keywords": [
    "agent-native",
    "claude-code",
    "anthropic",
    "decompose",
    "mcp",
    "image-generation",
    "l1-l5",
    "layers"
  ]
}
```

- [ ] **Step 3: Validate JSON**

```bash
python3 -m json.tool /Users/yhryzy/dev/vulca-plugin/.claude-plugin/plugin.json > /dev/null && echo OK
```

Expected: `OK` printed.

- [ ] **Step 4: Verify acceptance criterion**

```bash
jq -r '.version' /Users/yhryzy/dev/vulca-plugin/.claude-plugin/plugin.json
jq -r '.description' /Users/yhryzy/dev/vulca-plugin/.claude-plugin/plugin.json | grep -F "21 MCP tools"
```

Expected: `0.16.1` then the description line grep-matches.

- [ ] **Step 5: Commit**

```bash
cd /Users/yhryzy/dev/vulca-plugin
git add .claude-plugin/plugin.json
git commit -m "chore(plugin): bump to v0.16.1 + rewrite description for agent-native positioning

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### T1.3 — Update `.claude-plugin/marketplace.json`

**Files:**
- Modify: `/Users/yhryzy/dev/vulca-plugin/.claude-plugin/marketplace.json`

**Acceptance criterion mapping:** Phase 1 AC — "marketplace.json `plugins[0].version` equals `"0.16.1"`".

- [ ] **Step 1: Read current content**

```bash
cat /Users/yhryzy/dev/vulca-plugin/.claude-plugin/marketplace.json
```

- [ ] **Step 2: Write new content**

Replace entire file contents with:

```json
{
  "name": "vulca-marketplace",
  "owner": {
    "name": "Yu Haorui",
    "email": "yuhaorui48@gmail.com"
  },
  "plugins": [
    {
      "name": "vulca",
      "source": "./",
      "description": "Agent-native image-editing MCP surface for Claude Code & Cursor. 21 MCP tools + /decompose skill.",
      "version": "0.16.1"
    }
  ]
}
```

- [ ] **Step 3: Validate + verify**

```bash
python3 -m json.tool /Users/yhryzy/dev/vulca-plugin/.claude-plugin/marketplace.json > /dev/null && echo OK
jq -r '.plugins[0].version' /Users/yhryzy/dev/vulca-plugin/.claude-plugin/marketplace.json
```

Expected: `OK`, then `0.16.1`.

- [ ] **Step 4: Commit**

```bash
cd /Users/yhryzy/dev/vulca-plugin
git add .claude-plugin/marketplace.json
git commit -m "chore(plugin): sync marketplace.json to v0.16.1

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### T1.4 — Delete 10 empty skill subdirs + cultural-critic agent

**Files:**
- Delete: `/Users/yhryzy/dev/vulca-plugin/skills/{create,evaluate,evolution,inpaint,layers,release,resume,studio,sync,tradition}/`
- Delete: `/Users/yhryzy/dev/vulca-plugin/agents/cultural-critic.md`

**Acceptance criterion mapping:** Phase 1 AC — "skills/ contains exactly one subdirectory named decompose" AND "agents/cultural-critic.md is deleted".

- [ ] **Step 1: Verify the 10 skill subdirs are actually empty**

```bash
cd /Users/yhryzy/dev/vulca-plugin
for d in create evaluate evolution inpaint layers release resume studio sync tradition; do
  echo "=== skills/$d ==="
  ls -la "skills/$d" 2>&1 | tail -n +4
done
```

Expected: each subdir either missing or showing only `.` and `..` entries.

- [ ] **Step 2: Delete the 10 empty subdirs**

```bash
cd /Users/yhryzy/dev/vulca-plugin
for d in create evaluate evolution inpaint layers release resume studio sync tradition; do
  if [ -d "skills/$d" ]; then
    git rm -rf --quiet "skills/$d" 2>/dev/null || rmdir "skills/$d"
  fi
done
```

- [ ] **Step 3: Delete `cultural-critic.md`**

```bash
cd /Users/yhryzy/dev/vulca-plugin
git rm agents/cultural-critic.md
# If agents/ is now empty, also remove it:
if [ -d agents ] && [ -z "$(ls -A agents)" ]; then rmdir agents; fi
```

- [ ] **Step 4: Verify final state**

```bash
ls /Users/yhryzy/dev/vulca-plugin/skills/
ls /Users/yhryzy/dev/vulca-plugin/agents/ 2>&1 || echo "agents dir removed"
```

Expected: `skills/` contains only `decompose` (to be populated in T1.5); `agents/` does not exist or is empty.

Note: `decompose/` itself may not yet exist. T1.5 creates it.

- [ ] **Step 5: Commit**

```bash
cd /Users/yhryzy/dev/vulca-plugin
git add -A skills/ agents/ 2>/dev/null
git commit -m "chore(plugin): remove 10 empty skill dirs + orphaned cultural-critic agent

The 10 skill dirs (create/evaluate/evolution/inpaint/layers/release/resume/
studio/sync/tradition) were declared in plugin README but never populated.
cultural-critic referenced Phase-1-removed tools (resume_artwork, studio_*,
analyze_layers) and has no current user-facing flow. Both removed to match
reality; reintroduce when real skills ship.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### T1.5 — Copy `/decompose` SKILL.md from main repo

**Files:**
- Create: `/Users/yhryzy/dev/vulca-plugin/skills/decompose/SKILL.md`
- Source: `/Users/yhryzy/dev/vulca/.claude/skills/decompose/SKILL.md`

**Acceptance criterion mapping:** Phase 1 AC — "skills/decompose/SKILL.md exists and its SHA matches vulca/.claude/skills/decompose/SKILL.md (byte-identical copy)".

- [ ] **Step 1: Compute source SHA**

```bash
sha256sum /Users/yhryzy/dev/vulca/.claude/skills/decompose/SKILL.md
```

Expected: a hex digest. Record it for Step 4.

- [ ] **Step 2: Copy the file**

```bash
mkdir -p /Users/yhryzy/dev/vulca-plugin/skills/decompose
cp /Users/yhryzy/dev/vulca/.claude/skills/decompose/SKILL.md \
   /Users/yhryzy/dev/vulca-plugin/skills/decompose/SKILL.md
```

- [ ] **Step 3: Verify byte-identical copy**

```bash
diff -q \
  /Users/yhryzy/dev/vulca/.claude/skills/decompose/SKILL.md \
  /Users/yhryzy/dev/vulca-plugin/skills/decompose/SKILL.md
```

Expected: no output (files identical).

- [ ] **Step 4: Verify SHA match**

```bash
sha256sum /Users/yhryzy/dev/vulca-plugin/skills/decompose/SKILL.md
```

Expected: matches Step 1 digest exactly.

- [ ] **Step 5: Commit**

```bash
cd /Users/yhryzy/dev/vulca-plugin
git add skills/decompose/SKILL.md
git commit -m "feat(plugin): bundle /decompose skill from vulca v0.16.1

Copied byte-identically from vulca/.claude/skills/decompose/SKILL.md.
This is the first skill the plugin actually ships. Keeps one source of
truth in the SDK repo; plugin tracks via copy-on-release.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### T1.6 — Rewrite plugin's own README.md

**Files:**
- Modify: `/Users/yhryzy/dev/vulca-plugin/README.md`

**Acceptance criterion mapping:** Phase 1 AC — "Plugin README tool table lists the same 21 tool names as Phase 1 source-of-truth (grep-verifiable)".

- [ ] **Step 1: Write new README.md**

Replace entire file contents with:

````markdown
# VULCA — Claude Code & Cursor Plugin

Agent-native image-editing MCP surface. **21 MCP tools + 1 skill (`/decompose`)** for Claude Code and Cursor. v0.16.1 (tracks vulca SDK v0.16.1; 1446 tests).

## Install

```bash
pip install vulca[mcp]==0.16.1
claude plugin install vulca-org/vulca-plugin
```

For real image generation: either run [ComfyUI](https://github.com/comfyanonymous/ComfyUI) locally (free) or set `GOOGLE_API_KEY` for Gemini. Mock mode works without either.

## What happens in Claude Code

**You:** `> /decompose /path/to/painting.jpg`

**Claude:** Reads the image with `view_image`, authors a decomposition plan, calls `layers_split(mode="orchestrated", plan=...)`, returns one transparent PNG per entity. Iterates per the skill's 10-branch decision tree if segmentation fails on a specific entity.

## MCP Tools (21)

| Tool | Description |
|------|-------------|
| `generate_image` | Pure image generation (no evaluation loop) |
| `create_artwork` | Single-pass cultural-guided creation + evaluate |
| `inpaint_artwork` | Region-based inpainting |
| `view_image` | Read image metadata + base64 for the agent |
| `evaluate_artwork` | L1–L5 cultural scoring against a tradition |
| `list_traditions` | List all 13 cultural traditions |
| `get_tradition_guide` | Detailed tradition reference |
| `search_traditions` | Keyword search across tradition knowledge |
| `layers_split` | Decompose an image into semantic layers (orchestrated mode for `/decompose`) |
| `layers_list` | List layers in a session directory |
| `layers_edit` | Structural edits (add/remove/reorder/toggle/lock/merge/duplicate) |
| `layers_redraw` | Redraw one layer with new instructions |
| `layers_transform` | Apply transform ops to a layer |
| `layers_composite` | Composite layers back into a flat image |
| `layers_export` | Export to PNG directory with manifest |
| `layers_evaluate` | Per-layer L1–L5 evaluation |
| `brief_parse` | Parse a creative brief into structured form |
| `generate_concepts` | Generate concept sketches from a brief |
| `archive_session` | Archive a session for later retrieval |
| `sync_data` | Sync sessions + evolved weights |
| `unload_models` | Admin: release model memory (MPS/CUDA) |

## Skills (1)

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `/decompose` | "decompose /path/img.jpg" | Loads SKILL.md, reads image, orchestrates `layers_split`, iterates per decision tree |

## Requirements

- Python 3.10+
- `uv` installed for the default MCP runner (`uvx --from vulca[mcp] vulca-mcp`)
- `pip install vulca[mcp]==0.16.1`

## License

Apache 2.0
````

- [ ] **Step 2: Verify the 21-tool table**

```bash
grep -E '^\| \`[a-z_]+\` \|' /Users/yhryzy/dev/vulca-plugin/README.md | wc -l
```

Expected: `21`.

- [ ] **Step 3: Verify tool names match source-of-truth**

```bash
grep -oE '^\| \`[a-z_]+\`' /Users/yhryzy/dev/vulca-plugin/README.md \
  | sed -E 's/^\| `([a-z_]+)`/\1/' | sort > /tmp/plugin-readme-tools.txt

cat <<'EOF' | sort > /tmp/source-of-truth-tools.txt
generate_image
create_artwork
inpaint_artwork
view_image
evaluate_artwork
list_traditions
get_tradition_guide
search_traditions
layers_split
layers_list
layers_edit
layers_redraw
layers_transform
layers_composite
layers_export
layers_evaluate
brief_parse
generate_concepts
archive_session
sync_data
unload_models
EOF

diff /tmp/plugin-readme-tools.txt /tmp/source-of-truth-tools.txt
```

Expected: no diff output (identical sets).

- [ ] **Step 4: Commit**

```bash
cd /Users/yhryzy/dev/vulca-plugin
git add README.md
git commit -m "docs(plugin): rewrite README for v0.16.1 agent-native positioning

- Replace stale 21-tool table with current SDK tool list
- Replace 'Skills (10)' (empty) with 'Skills (1)' naming /decompose
- Drop 'Agent' section (cultural-critic removed)
- Pin install command to ==0.16.1
- Add uv/uvx as explicit requirement

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### T1.7 — Push branch, open Phase 1 PR

**Files:** none (git push + PR creation)

- [ ] **Step 1: Push branch**

```bash
cd /Users/yhryzy/dev/vulca-plugin
git push -u origin phase1-sync-v0.16.1
```

- [ ] **Step 2: Open PR**

```bash
gh pr create \
  --repo vulca-org/vulca-plugin \
  --title "Phase 1: sync plugin to vulca v0.16.1 agent-native surface" \
  --body "$(cat <<'EOF'
## Summary
- Bump plugin version 0.9.0 → 0.16.1
- Rewrite `.claude-plugin/plugin.json` + `marketplace.json` for agent-native positioning
- Remove 10 empty skill dirs + orphaned `cultural-critic.md` agent
- Bundle `/decompose` SKILL.md from vulca repo (byte-identical copy)
- Rewrite plugin README tool table to current 21-tool surface

## Why
vulca v0.16.1 (Phase 1 agent-native refactor) changed the tool surface from 29 → 20+1 and shipped `/decompose` as the first agent skill. The plugin repo had not been updated since 2026-04-07; `claude plugin install vulca-org/vulca-plugin` was silently installing references to removed tools and an empty skill directory structure.

This PR is Phase 1 of the 2026-04-20 README refresh plan. Phase 2 (main repo README) merges only after this PR ships and the clean-install verification passes.

## Test plan
- [ ] JSON manifests validate
- [ ] 21-tool table diffs clean against source-of-truth
- [ ] `skills/` contains only `decompose`
- [ ] `agents/` removed
- [ ] SHA(plugin SKILL.md) == SHA(vulca main SKILL.md)

## Acceptance criteria
See `docs/superpowers/specs/2026-04-20-plugin-sync-and-readme-refresh-design.md` Phase 1 section in the vulca main repo.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Expected: PR URL printed.

- [ ] **Step 3: No commit on main repo — PR is on plugin repo**

---

### T1.8 — Parallel review of Phase 1 PR (codex + superpowers)

**Files:** none (review dispatch)

**Acceptance criterion mapping:** per `memory/feedback_parallel_review_discipline.md` — non-trivial PR gets both reviewers.

- [ ] **Step 1: Capture PR number from T1.7**

```bash
PR_NUM=$(gh pr list --repo vulca-org/vulca-plugin --head phase1-sync-v0.16.1 --json number --jq '.[0].number')
echo "Phase 1 PR #$PR_NUM"
```

- [ ] **Step 2: Dispatch codex:codex-rescue on the PR**

In Claude Code, dispatch (do NOT execute this as bash — this is an Agent tool call):

```
subagent_type: codex:codex-rescue
description: Codex review of Phase 1 plugin sync PR
prompt: Review the diff at `gh pr diff <PR_NUM> --repo vulca-org/vulca-plugin`
         against `docs/superpowers/specs/2026-04-20-plugin-sync-and-readme-refresh-design.md`
         Phase 1 source-of-truth section (lines 37-68 of the spec). Focus on:
         1. Tool list correctness (21 names must match character-for-character)
         2. JSON syntax / schema drift in plugin.json and marketplace.json
         3. Whether any Phase-1-removed tool still appears anywhere
         4. Whether the SKILL.md copy is byte-identical (flag any accidental re-wrap)
         BLOCK until complete; return verbatim findings. Cap at 300 words.
```

- [ ] **Step 3: Dispatch superpowers:code-reviewer on the PR**

In Claude Code, dispatch in the same message for parallelism:

```
subagent_type: superpowers:code-reviewer
description: Superpowers review of Phase 1 plugin sync PR
prompt: Review the diff on PR #<PR_NUM> in vulca-org/vulca-plugin against
         the Phase 1 section of `docs/superpowers/specs/2026-04-20-plugin-sync-and-readme-refresh-design.md`
         (in the main vulca repo at `/Users/yhryzy/dev/vulca`). Focus on:
         1. README tool descriptions — accurate against current SDK docstrings?
         2. plugin.json keywords — do any omissions hurt marketplace discoverability?
         3. Tone consistency between plugin README hero and main-repo README hero
         4. Any claim that couldn't be verified from the diff alone
         Cap at 300 words. Lead with biggest blocker.
```

- [ ] **Step 4: Wait for both agents to return, synthesize findings**

If either reviewer flags a blocker, proceed to T1.9. If both return LGTM, skip directly to T1.9's merge step.

- [ ] **Step 5: No commit — next task handles feedback**

---

### T1.9 — Address review feedback, merge, tag v0.16.1

**Files:** whatever the reviewers flagged

**Acceptance criterion mapping:** Phase 1 AC — "Plugin repo tagged `v0.16.1` with release notes mentioning sync to SDK v0.16.1 + `/decompose` bundling".

- [ ] **Step 1: Address every blocker from T1.8**

For each blocker the reviewers named, edit the corresponding file, commit with a targeted message, push. Do not batch multiple fixes into one commit — one fix per commit matches repo convention.

- [ ] **Step 2: If reviewers required re-review, dispatch again**

Repeat T1.8 step 2 + step 3 in parallel on the updated diff.

- [ ] **Step 3: Merge the PR via GitHub UI or `gh`**

```bash
gh pr merge $PR_NUM --repo vulca-org/vulca-plugin --merge
```

Use `--merge` (not squash) to preserve linear granular history per `memory/user_collaboration_style.md`.

- [ ] **Step 4: Pull merged master + tag v0.16.1**

```bash
cd /Users/yhryzy/dev/vulca-plugin
git checkout master
git pull --ff-only origin master
git tag -a v0.16.1 -m "v0.16.1 — sync plugin to vulca SDK v0.16.1

- Tool surface: 29 → 20 + 1 (unload_models) = 21 total
- Skills: now 1 (/decompose) — replaces the 10 empty dirs
- Agents: removed cultural-critic (referenced removed tools)
- plugin.json + marketplace.json bumped
- Plugin README tool table rewritten"
```

- [ ] **Step 5: Push tag**

```bash
git push origin v0.16.1
```

- [ ] **Step 6: No new commit — tag is the artifact**

---

### T1.10 — GitHub release for v0.16.1

**Files:** none (GitHub release)

**Acceptance criterion mapping:** Phase 1 AC release note; `memory/feedback_release_checklist.md`.

- [ ] **Step 1: Create release**

```bash
cd /Users/yhryzy/dev/vulca-plugin
gh release create v0.16.1 \
  --title "v0.16.1 — agent-native sync" \
  --notes "$(cat <<'EOF'
Syncs plugin to vulca SDK v0.16.1 (Phase 1 agent-native refactor).

## Changes
- **Tool surface:** 21 MCP tools (Phase 1 pruned 29 → 20 + added unload_models)
- **Skills:** bundles `/decompose` (the orchestrated layer-split skill shipped in vulca v0.16.1)
- **Removed:** 10 empty skill directories, `cultural-critic` agent
- **Manifests:** plugin.json + marketplace.json bumped and rewritten for agent-native positioning

## Install
```bash
pip install vulca[mcp]==0.16.1
claude plugin install vulca-org/vulca-plugin
```

Requires `uv` for the default MCP runner. See plugin README.

## Next
See `docs/superpowers/specs/2026-04-20-plugin-sync-and-readme-refresh-design.md` in the vulca main repo.
EOF
)"
```

Expected: release URL printed.

- [ ] **Step 2: Verify PyPI is NOT needed** — plugin is a git-installed plugin, not a Python package. No `twine upload`.

- [ ] **Step 3: No commit — release is the artifact**

---

## Gate — Phase 1 clean-install verification

**This gate MUST pass before any Phase 2 task starts. If any step fails, return to Phase 1 to fix.**

### T1.G1 — Rename aside existing user directories

**Files:**
- Rename: `~/.claude/plugins/vulca*` → `~/.claude/plugins/vulca-BAK-2026-04-20`
- Rename: `~/.claude/skills/decompose/` → `~/.claude/skills/decompose-BAK-2026-04-20/`

- [ ] **Step 1: Rename aside**

```bash
# Plugin dir
if ls ~/.claude/plugins/vulca* 2>/dev/null; then
  for d in ~/.claude/plugins/vulca*; do
    mv "$d" "${d}-BAK-2026-04-20"
  done
fi

# Skill dir
if [ -d ~/.claude/skills/decompose ]; then
  mv ~/.claude/skills/decompose ~/.claude/skills/decompose-BAK-2026-04-20
fi
```

- [ ] **Step 2: Verify aside**

```bash
ls ~/.claude/plugins/ 2>&1 | grep -v BAK | grep -i vulca || echo "CLEAN"
ls ~/.claude/skills/ 2>&1 | grep -v BAK | grep -i decompose || echo "CLEAN"
```

Expected: both `CLEAN`.

- [ ] **Step 3: No commit**

---

### T1.G2 — Fresh venv install + tag-pinned plugin install

- [ ] **Step 1: Fresh venv**

```bash
mkdir -p /tmp/vulca-phase1-verify
cd /tmp/vulca-phase1-verify
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

- [ ] **Step 2: Install pinned vulca[mcp]**

```bash
pip install 'vulca[mcp]==0.16.1'
```

Expected: success. If PyPI does not yet have v0.16.1, fall back to installing from git: `pip install 'vulca[mcp] @ git+https://github.com/vulca-org/vulca@v0.16.1'`.

- [ ] **Step 3: Install plugin at tagged release**

```bash
claude plugin install vulca-org/vulca-plugin@v0.16.1
```

Expected: success. If syntax is rejected, try `claude plugin install https://github.com/vulca-org/vulca-plugin/releases/tag/v0.16.1`.

- [ ] **Step 4: No commit**

---

### T1.G3 — Verify `/decompose` auto-discovery + tool call

- [ ] **Step 1: Open Claude Code in a fresh shell**

```bash
cd /tmp/vulca-phase1-verify
# Launch Claude Code interactively
```

- [ ] **Step 2: In Claude Code, check that `/decompose` is listed as an available slash command**

Type `/dec` in the prompt and verify `/decompose` appears in the autocomplete.

- [ ] **Step 3: Run against a test image**

Use any test image (e.g. `/Users/yhryzy/dev/vulca/assets/demo/v2/masters/mona_lisa.jpg`):

```
> /decompose /Users/yhryzy/dev/vulca/assets/demo/v2/masters/mona_lisa.jpg
```

Expected: Claude Code loads the skill, calls `view_image` and `layers_split(mode="orchestrated", ...)`. Mock provider may refuse actual generation — that is OK. The assertion is that `layers_split` tool call FIRES, not that it succeeds.

- [ ] **Step 4: Screenshot or save transcript**

Save the transcript as `/tmp/vulca-phase1-verify/decompose-smoketest.txt`.

- [ ] **Step 5: No commit**

---

### T1.G4 — Capture exact 21-tool list

- [ ] **Step 1: In Claude Code, ask it to list MCP tools**

```
> list every MCP tool currently exposed by the vulca plugin, one per line, no prose
```

Claude Code returns the tool list from the active MCP connection.

- [ ] **Step 2: Save verbatim output**

Copy the response into:

```bash
cat > /Users/yhryzy/dev/vulca/verification-tools-v0.16.1.txt <<'EOF'
<paste exact tool list here, one per line>
EOF
```

- [ ] **Step 3: Verify count**

```bash
wc -l /Users/yhryzy/dev/vulca/verification-tools-v0.16.1.txt
```

Expected: `21`.

- [ ] **Step 4: Verify set equality with source-of-truth**

```bash
sort /Users/yhryzy/dev/vulca/verification-tools-v0.16.1.txt > /tmp/verified-tools-sorted.txt
cat <<'EOF' | sort > /tmp/source-of-truth-sorted.txt
generate_image
create_artwork
inpaint_artwork
view_image
evaluate_artwork
list_traditions
get_tradition_guide
search_traditions
layers_split
layers_list
layers_edit
layers_redraw
layers_transform
layers_composite
layers_export
layers_evaluate
brief_parse
generate_concepts
archive_session
sync_data
unload_models
EOF
diff /tmp/verified-tools-sorted.txt /tmp/source-of-truth-sorted.txt
```

Expected: no diff output.

- [ ] **Step 5: No commit (yet — see T1.G5)**

---

### T1.G5 — Restore aside dirs; commit verification artifact

- [ ] **Step 1: Restore user dirs**

```bash
# Plugin
for d in ~/.claude/plugins/vulca*-BAK-2026-04-20; do
  if [ -d "$d" ]; then
    original="${d%-BAK-2026-04-20}"
    if [ ! -d "$original" ]; then
      mv "$d" "$original"
    else
      echo "Warning: $original already exists from the test install; keep test install or merge manually"
    fi
  fi
done

# Skill
if [ -d ~/.claude/skills/decompose-BAK-2026-04-20 ]; then
  if [ ! -d ~/.claude/skills/decompose ]; then
    mv ~/.claude/skills/decompose-BAK-2026-04-20 ~/.claude/skills/decompose
  fi
fi
```

- [ ] **Step 2: Commit `verification-tools-v0.16.1.txt` to main vulca repo**

```bash
cd /Users/yhryzy/dev/vulca
git add verification-tools-v0.16.1.txt
git commit -m "test(release): capture 21-tool verification artifact for v0.16.1

Output of Phase 1 clean-install verification per the 2026-04-20 plan.
Used as evidence in the Phase 2 PR description.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 3: If gate passed all steps, Phase 2 is now unblocked**

Explicit pass criterion: all of T1.G1 through T1.G4 green AND `diff` at T1.G4 step 4 empty.

---

## Phase 2 — main README refresh

### T2.1 — Create branch `phase2-readme-refresh`

- [ ] **Step 1: Sync local master**

```bash
cd /Users/yhryzy/dev/vulca
git checkout master
git pull --ff-only origin master
```

- [ ] **Step 2: Create branch**

```bash
git checkout -b phase2-readme-refresh
```

- [ ] **Step 3: Verify**

```bash
git branch --show-current
```

Expected: `phase2-readme-refresh`.

- [ ] **Step 4: No commit yet**

---

### T2.2 — Write the full new README.md

**Files:**
- Replace: `/Users/yhryzy/dev/vulca/README.md` (full rewrite)

**Acceptance criterion mapping:** Phase 2 AC #1-8 (line count, hero, transcript position, setup position, capability map, v2 GIF absence, social proof, MPS link).

- [ ] **Step 1: Read the EMNLP URL from T0.4**

```bash
cat /tmp/emnlp-url-2026-04-20.txt
```

Record the resolved URL for use below.

- [ ] **Step 2: Write the full README**

Write exact content to `/Users/yhryzy/dev/vulca/README.md`. Use the structure below verbatim. Every non-github.com non-pypi.org URL below already has UTM applied; if you add a new external link, apply `?utm_source=github-readme&utm_medium=oss&utm_campaign=refresh-2026-04-20` inline.

```markdown
# VULCA

[![PyPI](https://img.shields.io/pypi/v/vulca.svg)](https://pypi.org/project/vulca/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/vulca/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/vulca-org/vulca/blob/master/LICENSE)
[![MCP Tools](https://img.shields.io/badge/MCP_tools-21-blueviolet.svg)](https://github.com/vulca-org/vulca-plugin)

**Agents can plan image edits but can't cut pixels. Vulca is the hands — semantic layer splits, cultural scoring, inpainting — as 21 MCP tools for Claude Code.**

> *Below: Mona Lisa → `face_and_hair.png` + `body_and_dress.png`, decomposed locally on Apple Silicon (ComfyUI + Ollama) with zero cloud API calls. SDK total: 21 MCP tools · 1446 tests passing.*

## What happens when you run `/decompose`

```
> /decompose assets/mona_lisa.jpg

Claude: I'll first look at the image and plan a decomposition.
[tool_use: view_image(path="assets/mona_lisa.jpg")]
[tool_use: layers_split(
    path="assets/mona_lisa.jpg",
    mode="orchestrated",
    plan={"domain": "portrait", "entities": [
        {"name": "face_and_hair", "prompt": "the woman's face and hair"},
        {"name": "body_and_dress", "prompt": "the woman's body and dress"}]})]
[tool_result: {"layers": [
    {"name": "face_and_hair", "path": "./layers/face_and_hair.png", "coverage": 0.38},
    {"name": "body_and_dress", "path": "./layers/body_and_dress.png", "coverage": 0.54}]}]

Claude: Two layers extracted with 92% total coverage. Want to redraw one?
```

## Try it in 60 seconds

**Prerequisite:** `uv` installed (provides `uvx`) — `curl -LsSf https://astral.sh/uv/install.sh?utm_source=github-readme&utm_medium=oss&utm_campaign=refresh-2026-04-20 | sh` or see [astral.sh/uv](https://docs.astral.sh/uv/?utm_source=github-readme&utm_medium=oss&utm_campaign=refresh-2026-04-20). Without `uv`, substitute `uvx --from vulca[mcp] vulca-mcp` with `python -m vulca.mcp_server` in Path B.

### Path A — plugin install (recommended)

```bash
pip install vulca[mcp]==0.16.1
claude plugin install vulca-org/vulca-plugin
```

Then in Claude Code: `> /decompose /path/to/your_image.jpg`

### Path B — no plugin (power user)

```bash
pip install vulca[mcp]==0.16.1

# Register MCP server — add to ~/.claude/settings.json:
# {"mcpServers": {"vulca": {"command": "uvx", "args": ["--from", "vulca[mcp]==0.16.1", "vulca-mcp"]}}}

# Install the /decompose skill:
mkdir -p ~/.claude/skills/decompose
curl -o ~/.claude/skills/decompose/SKILL.md \
  https://raw.githubusercontent.com/vulca-org/vulca/v0.16.1/.claude/skills/decompose/SKILL.md
```

<p align="center">
  <img src="assets/demo/v2/masters/mona_lisa.jpg" alt="Mona Lisa original" height="220">
  →
  <img src="assets/demo/v2/masters/mona_lisa_layers/mona_lisa_face_and_hair.png" alt="Face and hair layer" height="220">
  <img src="assets/demo/v2/masters/mona_lisa_layers/mona_lisa_body_and_dress.png" alt="Body and dress layer" height="220">
</p>
<p align="center"><em>Mona Lisa → face & hair / body & dress — clean semantic separation, produced by the transcript above</em></p>

---

## What Vulca takes off your agent's hands

| Cluster | What your agent delegates to Vulca | Skill | Tools |
|---|---|:---:|---|
| **Decompose** | Extract 10–20 semantic layers from any image with real transparency. | ✅ `/decompose` | `layers_split` (orchestrated), `layers_list` |
| **Edit** | Redraw one region or one layer without touching the rest. Composite back. | Roadmap | `inpaint_artwork`, `layers_edit`, `layers_redraw`, `layers_transform`, `layers_composite`, `layers_export`, `layers_evaluate` |
| **Evaluate** | Judge a visual against L1–L5 cultural criteria over 13 traditions with citable rationale. | Roadmap | `evaluate_artwork`, `list_traditions`, `get_tradition_guide`, `search_traditions` |
| **Create** | Generate a new image from intent + tradition guidance, optionally in structured layers. | — | `create_artwork`, `generate_image` |
| **Brief / Studio** | Turn a creative brief into concept sketches and iterate. | — | `brief_parse`, `generate_concepts` |
| **Admin** | Let the agent see intermediate artifacts, unload models, archive sessions. | — | `view_image`, `unload_models`, `archive_session`, `sync_data` |

```
User intent ─▶ Claude Code (planning) ─▶ Vulca MCP tools ─▶ Image artifacts ─┐
       ▲                                                                    │
       └──────────── visible via view_image ◀───────────────────────────────┘
```

### Roadmap — no promises, just honest order

- **Next skill:** `/evaluate` — reactivates the EMNLP anchor for agent-driven cultural scoring
- **Then:** `/inpaint` (region-level edit), `/layered-create` (structured generation)
- **Beyond:** community-driven — file an issue with your workflow

See [docs/agent-native-workflow.md](docs/agent-native-workflow.md) for the deeper walkthrough.

---

## Research

| Paper | Venue | Contribution |
|-------|-------|--------------|
| [**VULCA Framework**](<EMNLP_URL_FROM_T0_4>) | EMNLP 2025 Findings | 5-dimension evaluation framework |
| [**VULCA-Bench**](https://arxiv.org/abs/2601.07986?utm_source=github-readme&utm_medium=oss&utm_campaign=refresh-2026-04-20) | arXiv | L1-L5 definitions, 7,410 samples, 9 traditions |
| [**Art Critique**](https://arxiv.org/abs/2601.07984?utm_source=github-readme&utm_medium=oss&utm_campaign=refresh-2026-04-20) | arXiv | Cross-cultural critique evaluation |

### Citation

```bibtex
@inproceedings{yu2025vulca,
  title     = {VULCA: A Framework for Culturally-Aware Visual Understanding},
  author    = {Yu, Haorui},
  booktitle = {Findings of EMNLP 2025},
  year      = {2025}
}

@article{yu2026vulcabench,
  title   = {VULCA-Bench: A Benchmark for Culturally-Aware Visual Understanding at Five Levels},
  author  = {Yu, Haorui},
  journal = {arXiv preprint arXiv:2601.07986},
  year    = {2026}
}
```

---

## 13 cultural traditions

`chinese_xieyi` `chinese_gongbi` `japanese_traditional` `western_academic` `islamic_geometric` `watercolor` `african_traditional` `south_asian` `contemporary_art` `photography` `brand_design` `ui_ux_design` `default`

Custom traditions via YAML — `vulca evaluate painting.jpg --tradition ./my_style.yaml`.

---

## Apple Silicon / MPS quickstart

```bash
pip install vulca[mcp,tools]==0.16.1
# Local stack: ComfyUI + Ollama, full MPS support
```

See [docs/apple-silicon-mps-comfyui-guide.md](docs/apple-silicon-mps-comfyui-guide.md) for the full ComfyUI + Ollama setup tested on MPS.

---

<details>
<summary>CLI / SDK cheat sheet</summary>

```bash
# CLI entry points (all still work post agent-native refactor)
vulca create "intent" -t tradition --provider comfyui -o art.png
vulca evaluate art.png -t tradition --mode reference
vulca layers split art.png -o ./layers/ --mode regenerate
vulca layers redraw ./layers/ --layer sky -i "add sunset"
vulca layers composite ./layers/ -o final.png
vulca inpaint art.png --region "sky" --instruction "storm"
vulca tools run brushstroke_analyze --image art.png
```

```python
import vulca
result = vulca.evaluate("artwork.png", tradition="chinese_xieyi")
print(result.score, result.L3)
```

</details>

<details>
<summary>Architecture</summary>

```
┌──────────────────────────────────────────────────────────────┐
│                         User Intent                          │
└──────┬───────────┬──────────────┬──────────────┬─────────────┘
       │           │              │              │
  ┌────▼──┐  ┌─────▼───┐  ┌──────▼─────┐  ┌─────▼─────┐
  │  CLI  │  │ Python  │  │    MCP     │  │  ComfyUI  │
  │       │  │   SDK   │  │  21 tools  │  │  11 nodes │
  └───┬───┘  └────┬────┘  └──────┬─────┘  └─────┬─────┘
      └───────────┴───────┬──────┴───────────────┘
                          │
                 vulca.pipeline.execute()
                          │
              ┌───────────▼───────────┐
              │    Image Providers    │
              │  ComfyUI │ Gemini     │
              │  OpenAI  │ Mock       │
              └───────────────────────┘
```

| Provider | Generate | Inpaint | Layered | Multilingual |
|----------|----------|---------|---------|--------------|
| ComfyUI  | ✓        | ✓       | ✓       | English-only |
| Gemini   | ✓        | ✓       | ✓       | CJK native   |
| OpenAI   | ✓        | —       | —       | English-only |
| Mock     | ✓        | ✓       | ✓       | —            |

</details>

---

## Showcase — agent-produced layer separations

<p align="center">
  <img src="assets/demo/v2/masters/qi_baishi_shrimp.jpg" alt="Qi Baishi shrimp original" height="220">
  →
  <img src="assets/demo/v2/masters/qi_baishi_layers/ink_shrimp.png" alt="Shrimp layer" height="220">
  <img src="assets/demo/v2/masters/qi_baishi_layers/ink_calligraphy.png" alt="Calligraphy layer" height="220">
  <img src="assets/demo/v2/masters/qi_baishi_layers/red_seals.png" alt="Seals layer" height="220">
</p>
<p align="center"><em>Qi Baishi's Shrimp → shrimp / calligraphy / seals — each on transparent canvas.<br/>These layer separations were produced by Claude Code driving Vulca MCP tools via <code>/decompose</code>.</em></p>

---

## License

Apache 2.0. See [LICENSE](LICENSE).

> Issues and PRs welcome. Development syncs from a private monorepo via `git subtree`.
```

**Important:** In Step 2's content above, replace `<EMNLP_URL_FROM_T0_4>` with the actual URL resolved in T0.4 Step 3 (append the UTM query string if it is a non-github.com URL).

- [ ] **Step 3: Verify file line count**

```bash
wc -l /Users/yhryzy/dev/vulca/README.md
```

Expected: between 400 and 520. If over 520, compress the `<details>` sections. If under 400, the rewrite lost content — recheck against the spec's bottom-zone items.

- [ ] **Step 4: Commit**

```bash
cd /Users/yhryzy/dev/vulca
git add README.md
git commit -m "docs(readme): full refresh for agent-native positioning

- New D+A hero: 'Agents can plan image edits but can't cut pixels...'
- Agent transcript block above install block (conversion order fix)
- What Vulca takes off your agent's hands — 6-cluster capability map
- Public-domain masterwork social proof (Mona Lisa, Qi Baishi)
- MPS quickstart preserved (SEO #2 referrer)
- 4 stale v2 GIF references removed
- UTM on external non-github non-pypi links
- Pinned install commands to ==0.16.1

Aligns with Phase 1 plugin v0.16.1 (shipped 2026-04-20).
Traffic baseline: 14d views 82/31u. Rollback review 2026-05-04.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### T2.3 — Run every Phase 2 acceptance check

**Files:** none (verification script run)

**Acceptance criterion mapping:** Phase 2 ACs #1-8.

- [ ] **Step 1: File length**

```bash
LINES=$(wc -l < /Users/yhryzy/dev/vulca/README.md)
echo "Lines: $LINES"
[ "$LINES" -ge 400 ] && [ "$LINES" -le 520 ] && echo "PASS" || echo "FAIL"
```

Expected: `PASS`.

- [ ] **Step 2: Hero byte-exact**

```bash
grep -F "**Agents can plan image edits but can't cut pixels. Vulca is the hands — semantic layer splits, cultural scoring, inpainting — as 21 MCP tools for Claude Code.**" \
  /Users/yhryzy/dev/vulca/README.md && echo "PASS" || echo "FAIL"
```

Expected: `PASS`.

- [ ] **Step 3: Transcript before line 150 AND before any image tag**

```bash
TRANSCRIPT_LINE=$(grep -n 'What happens when you run' /Users/yhryzy/dev/vulca/README.md | head -1 | cut -d: -f1)
FIRST_IMG_LINE=$(grep -nE '(<img|!\[)' /Users/yhryzy/dev/vulca/README.md | head -1 | cut -d: -f1)
echo "Transcript at line $TRANSCRIPT_LINE; first image at line $FIRST_IMG_LINE"
[ "$TRANSCRIPT_LINE" -lt 150 ] && [ "$TRANSCRIPT_LINE" -lt "$FIRST_IMG_LINE" ] && echo "PASS" || echo "FAIL"
```

Expected: `PASS`.

- [ ] **Step 4: Setup block AFTER transcript but still near top**

```bash
SETUP_LINE=$(grep -n 'Try it in 60 seconds' /Users/yhryzy/dev/vulca/README.md | head -1 | cut -d: -f1)
echo "Setup at line $SETUP_LINE (must be > $TRANSCRIPT_LINE)"
[ "$SETUP_LINE" -gt "$TRANSCRIPT_LINE" ] && [ "$SETUP_LINE" -lt 150 ] && echo "PASS" || echo "FAIL"
```

Expected: `PASS`.

- [ ] **Step 5: Capability map — "delegates" column has no tool names**

```bash
# Extract lines of the capability map between its header and the workflow ASCII
awk '/^## What Vulca takes off your agent/,/^```$/' /Users/yhryzy/dev/vulca/README.md \
  | grep -E '^\|' \
  | awk -F'|' '{print $3}' \
  | grep -E '[a-z_]+_[a-z_]+' && echo "FAIL (tool name in delegates column)" || echo "PASS"
```

Expected: `PASS` (no tool names in second column).

- [ ] **Step 6: v2 GIF absence**

```bash
for gif in vhs-create.gif vhs-layers.gif vhs-studio.gif vhs-tools.gif; do
  if grep -q "$gif" /Users/yhryzy/dev/vulca/README.md; then
    echo "FAIL: $gif still referenced"
  fi
done
echo "DONE"
```

Expected: only `DONE` printed, no `FAIL` lines.

- [ ] **Step 7: Social proof — ≥2 master pairs, no celebrities**

```bash
grep -oE 'assets/demo/v2/masters/[a-z_/.]+' /Users/yhryzy/dev/vulca/README.md | sort -u
```

Expected: includes at least `mona_lisa` and `qi_baishi` path fragments. Review manually: no `bieber`, `trump`, or any celebrity name.

- [ ] **Step 8: MPS link present**

```bash
grep -F 'docs/apple-silicon-mps-comfyui-guide.md' /Users/yhryzy/dev/vulca/README.md && echo "PASS" || echo "FAIL"
```

Expected: `PASS`.

- [ ] **Step 9: No commit — this task is verification. If any check FAILS, loop back to T2.2 and fix.**

---

### T2.4 — UTM on every non-github.com non-pypi.org link

**Files:**
- Modify: `/Users/yhryzy/dev/vulca/README.md` (if Step 1 finds missing UTM)

**Acceptance criterion mapping:** Phase 2 AC — UTM grep check.

- [ ] **Step 1: Find violating links**

```bash
cd /Users/yhryzy/dev/vulca
grep -oE 'https?://[^[:space:])"]+' README.md \
  | grep -vE '^https?://(github\.com/vulca-org|pypi\.org/project/vulca)' \
  | grep -vE 'utm_source=github-readme' \
  | sort -u
```

Expected: empty output (no violators).

- [ ] **Step 2: If violators found, append UTM**

For each violator, edit README.md to replace the raw URL with:

```
<original-URL>?utm_source=github-readme&utm_medium=oss&utm_campaign=refresh-2026-04-20
```

If the URL already has a `?query=`, use `&` instead of `?`.

- [ ] **Step 3: Re-run Step 1 check**

Expected: empty output.

- [ ] **Step 4: Commit (only if fixes were made)**

```bash
cd /Users/yhryzy/dev/vulca
git add README.md
git commit -m "docs(readme): apply UTM tags to external links

Ensures 2026-05-04 traffic review can attribute README-origin visits.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

If no changes were needed, skip the commit — the content was already compliant from T2.2.

---

### T2.5 — Update GitHub About description

**Files:** none (GitHub API)

**Acceptance criterion mapping:** Phase 2 AC — "GitHub About description is byte-exact match".

- [ ] **Step 1: Capture current description**

```bash
gh api repos/vulca-org/vulca --jq '.description'
```

- [ ] **Step 2: Update via `gh api`**

```bash
gh api --method PATCH repos/vulca-org/vulca \
  -f description="Agent-native image-editing SDK for Claude Code. 21 MCP tools + /decompose skill — semantic layer splits, L1–L5 cultural scoring, region inpaint. Powered by ComfyUI, Gemini, or mock."
```

Expected: JSON response with new description echoed.

- [ ] **Step 3: Verify byte-exact match**

```bash
CURRENT=$(gh api repos/vulca-org/vulca --jq '.description')
EXPECTED="Agent-native image-editing SDK for Claude Code. 21 MCP tools + /decompose skill — semantic layer splits, L1–L5 cultural scoring, region inpaint. Powered by ComfyUI, Gemini, or mock."
[ "$CURRENT" = "$EXPECTED" ] && echo "PASS" || echo "FAIL"
```

Expected: `PASS`.

- [ ] **Step 4: No commit (state lives on GitHub, not in repo files)**

---

### T2.6 — Update GitHub topics to the 14-topic final set

**Files:** none (GitHub API)

**Acceptance criterion mapping:** Phase 2 AC — "topics list equals the 14-topic final set".

- [ ] **Step 1: Capture current topics**

```bash
gh api repos/vulca-org/vulca/topics --jq '.names'
```

- [ ] **Step 2: Replace topics with final 14**

```bash
gh api --method PUT repos/vulca-org/vulca/topics \
  -f 'names[]=agent-native' \
  -f 'names[]=claude-code' \
  -f 'names[]=anthropic' \
  -f 'names[]=claude-mcp' \
  -f 'names[]=ai' \
  -f 'names[]=art' \
  -f 'names[]=comfyui' \
  -f 'names[]=cultural' \
  -f 'names[]=mcp' \
  -f 'names[]=python' \
  -f 'names[]=sdk' \
  -f 'names[]=evaluation' \
  -f 'names[]=vlm' \
  -f 'names[]=multi-agent'
```

- [ ] **Step 3: Verify exact equality**

```bash
gh api repos/vulca-org/vulca/topics --jq '.names | sort' > /tmp/current-topics.json

cat <<'EOF' | jq -s 'sort' > /tmp/expected-topics.json
"agent-native"
"ai"
"anthropic"
"art"
"claude-code"
"claude-mcp"
"comfyui"
"cultural"
"evaluation"
"mcp"
"multi-agent"
"python"
"sdk"
"vlm"
EOF

diff /tmp/current-topics.json /tmp/expected-topics.json
```

Expected: no diff output.

- [ ] **Step 4: No commit**

---

### T2.7 — Register CronCreate for 2026-05-04 traffic review

**Files:** none (CronCreate invocation)

**Acceptance criterion mapping:** Phase 2 AC — "CronCreate trigger is registered to fire on 2026-05-04".

- [ ] **Step 1: Load the CronCreate tool schema**

In Claude Code, call ToolSearch with `select:CronCreate` to load the tool.

- [ ] **Step 2: Create the cron**

Call `CronCreate` with the following parameters (exact field names come from the loaded schema; adjust if the tool's schema uses different keys):

- Fire date/time: `2026-05-04` at `09:00` local
- Prompt:

```
Traffic review for the 2026-04-20 README refresh. Compare against baseline:

Baseline 14d views (pre-refresh): 82 / 31 unique
Baseline PyPI daily: ~72/day (down from 140)

Check:
- `gh api repos/vulca-org/vulca/traffic/views --jq '{count, uniques}'`
- `gh api repos/vulca-org/vulca/traffic/popular/referrers`
- PyPI recent: `curl -s https://pypistats.org/api/packages/vulca/recent`
- UTM-attributed traffic via GitHub referrer paths

Apply rollback thresholds:
- ≥130 views → refresh successful, iterate forward
- 80-130 views → content audit, adjust non-hero sections
- <80 views → revert hero, retain cluster map + Claude Code setup sections

Report decision + log outcome to a new memory file.
```

- [ ] **Step 3: Verify cron was created**

List existing crons via `CronList` (load via ToolSearch if needed). Confirm one fires on 2026-05-04.

- [ ] **Step 4: No commit**

---

### T2.8 — Push, open Phase 2 PR

- [ ] **Step 1: Push branch**

```bash
cd /Users/yhryzy/dev/vulca
git push -u origin phase2-readme-refresh
```

- [ ] **Step 2: Open PR**

```bash
gh pr create \
  --repo vulca-org/vulca \
  --title "Phase 2: README refresh for agent-native positioning" \
  --body "$(cat <<'EOF'
## Summary
- New hero: "Agents can plan image edits but can't cut pixels. Vulca is the hands..."
- Agent transcript block above install block (conversion-order fix from review)
- 6-cluster capability map organized by agent-jobs, not tool names
- Public-domain masterwork social proof (Mona Lisa + Qi Baishi) — no celebrity imagery
- MPS / Apple Silicon quickstart preserved (SEO #2 referrer)
- 4 stale v2 GIF references removed; files retained on disk
- UTM instrumented on every non-github non-pypi external link
- Pinned install commands to v0.16.1
- GitHub About description + topics updated in same PR

## Requires
This PR is Phase 2. Phase 1 (vulca-org/vulca-plugin v0.9.0 → v0.16.1) shipped and was verified via clean-install test (artifact: `verification-tools-v0.16.1.txt` in this repo root).

## Traffic baseline
14d views: 82 / 31 unique (↓61% vs 211 baseline)
PyPI: ~72/day (↓50% vs 140 baseline)
Social referrals: 0

## Rollback
CronCreate trigger scheduled for 2026-05-04:
- ≥130 views → success
- 80-130 → content audit
- <80 → revert hero

## Test plan
- [x] README 400-520 lines ✓
- [x] Hero byte-exact ✓
- [x] Transcript before line 150 AND before any `<img>` tag ✓
- [x] Setup block after transcript ✓
- [x] Capability map "delegates" column has no tool names ✓
- [x] Zero `vhs-*.gif` references ✓
- [x] Social proof = masters (no public figures) ✓
- [x] MPS doc linked ✓
- [x] UTM grep returns zero violations ✓
- [x] GitHub About byte-exact ✓
- [x] Topics = 14-item final set ✓
- [x] CronCreate registered for 2026-05-04 ✓

## Spec
`docs/superpowers/specs/2026-04-20-plugin-sync-and-readme-refresh-design.md` (commit ba5a562)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Expected: PR URL printed.

- [ ] **Step 3: No new commit**

---

### T2.9 — Parallel review of Phase 2 PR

**Files:** none

- [ ] **Step 1: Capture PR number**

```bash
PR_NUM=$(gh pr list --repo vulca-org/vulca --head phase2-readme-refresh --json number --jq '.[0].number')
echo "Phase 2 PR #$PR_NUM"
```

- [ ] **Step 2: Dispatch codex:codex-rescue (Agent tool call)**

```
subagent_type: codex:codex-rescue
description: Codex review of Phase 2 README refresh PR
prompt: Review the diff at `gh pr diff <PR_NUM> --repo vulca-org/vulca` against
         docs/superpowers/specs/2026-04-20-plugin-sync-and-readme-refresh-design.md
         Phase 2 acceptance criteria. Focus on:
         1. Hero paragraph byte-exact (do not accept paraphrase)
         2. Transcript block is genuinely ABOVE the install block
         3. "Delegates" column of capability map has zero tool names
         4. All external non-github non-pypi links carry utm_source=github-readme
         5. Any newly-introduced claim about tool behavior that could drift
         BLOCK until complete. Cap at 300 words. Lead with blockers.
```

- [ ] **Step 3: Dispatch superpowers:code-reviewer in parallel**

```
subagent_type: superpowers:code-reviewer
description: Superpowers review of Phase 2 README refresh PR
prompt: Review PR #<PR_NUM> on vulca-org/vulca against the Phase 2 section of
         docs/superpowers/specs/2026-04-20-plugin-sync-and-readme-refresh-design.md.
         Focus on:
         1. Conversion fidelity — does the above-the-fold zone (first ~600px) sell the hero?
         2. Capability map truthfulness — does each cluster's description match actual tool behavior? Flag any cluster where the spec's "agent-jobs" framing is violated.
         3. Any Path B step that a cold visitor on zsh/bash could misread or mis-paste
         4. Social proof caption honesty — were those layer separations actually produced by /decompose, or is the caption overclaiming?
         5. Links vs UTM rule consistency
         Cap at 300 words. Lead with biggest conversion risk.
```

- [ ] **Step 4: Wait for both; synthesize findings**

- [ ] **Step 5: No commit**

---

### T2.10 — Address feedback, merge Phase 2 PR

- [ ] **Step 1: For each blocker from T2.9, edit and commit fix**

One fix per commit. Push each.

- [ ] **Step 2: Re-dispatch reviewers if either required it**

- [ ] **Step 3: Merge**

```bash
gh pr merge $PR_NUM --repo vulca-org/vulca --merge
```

- [ ] **Step 4: Pull merged master**

```bash
cd /Users/yhryzy/dev/vulca
git checkout master
git pull --ff-only origin master
```

No new tag — docs-only, no SDK version bump.

---

### T2.11 — Supersede `project_readme_refresh_pending.md` memory

**Files:**
- Modify: `/Users/yhryzy/.claude/projects/-Users-yhryzy-dev-vulca/memory/MEMORY.md`
- Modify: `/Users/yhryzy/.claude/projects/-Users-yhryzy-dev-vulca/memory/project_readme_refresh_pending.md`

- [ ] **Step 1: Rewrite the pending memory as "completed"**

Replace the frontmatter `name` to mark it complete and update body to one-line supersede note:

```markdown
---
name: README refresh SHIPPED 2026-04-20
description: Phase 1 (plugin sync v0.16.1) + Phase 2 (README refresh) both merged. Traffic review scheduled 2026-05-04 via CronCreate. Superseded by that review's outcome memory.
type: project
---
Phase 1 PR + Phase 2 PR merged 2026-04-20. See commits on master for both repos.
Rollback criteria live until 2026-05-04 cron fire. After that date this memory is stale — trust the review-outcome memory instead.
```

- [ ] **Step 2: Update MEMORY.md index entry**

Change the existing line

```
- [README refresh pending](project_readme_refresh_pending.md) — 10 days stale; doesn't pitch agent-native/decompose skill; next session must refresh + codex+superpowers review
```

to:

```
- [README refresh SHIPPED](project_readme_refresh_pending.md) — 2026-04-20; traffic review cron fires 2026-05-04
```

- [ ] **Step 3: No commit (memory dir is outside the git repo)**

---

## Post-merge

### T3.1 — 2026-05-04 Cron fires

The scheduled CronCreate fires. Follow the prompt it carries. Write a new memory with the outcome; supersede `project_readme_refresh_pending.md` again if the rollback criterion was tripped.

This task is not executed as part of THIS plan — it's the follow-up reminder.

---

## Parallel dispatch summary

For subagent-driven-development:

| Parallel batch | Tasks | Notes |
|---|---|---|
| Batch A (pre-flight) | T0.2, T0.3, T0.4 | All file-issue / curl operations, no shared state |
| Batch B (Phase 1 manifests) | T1.2, T1.3 | Different JSON files in same repo, different commits |
| Batch C (Phase 1 review) | T1.8 codex + superpowers | Parallel dispatch in ONE Agent message |
| Batch D (Phase 2 review) | T2.9 codex + superpowers | Parallel dispatch in ONE Agent message |

Everything else is sequential (file dependencies, git state, Phase 1→Phase 2 gate).

---

## Spec-to-plan acceptance cross-check

| Spec AC | Plan task(s) |
|---|---|
| Phase 1 tag v0.16.1 pushed | T1.9 |
| plugin.json v0.16.1 + "21 MCP tools" | T1.2 |
| marketplace.json v0.16.1 | T1.3 |
| SKILL.md SHA match | T1.5 |
| skills/ has only decompose | T1.4 |
| cultural-critic deleted | T1.4 |
| plugin README tool table matches 21 | T1.6 |
| Clean-install verification passes | T1.G1-T1.G4 |
| README 400-520 lines | T2.2, T2.3.1 |
| Hero byte-exact | T2.2, T2.3.2 |
| Transcript before line 150 + before any img | T2.2, T2.3.3 |
| Setup after transcript in top zone | T2.2, T2.3.4 |
| Delegates column has no tool names | T2.2, T2.3.5 |
| No vhs-*.gif references | T2.2, T2.3.6 |
| ≥2 master pairs, no public figures | T2.2, T2.3.7 |
| MPS doc linked | T2.2, T2.3.8 |
| UTM grep zero violations | T2.2, T2.4 |
| GitHub About byte-exact | T2.5 |
| Topics = 14 final set | T2.6 |
| CronCreate registered | T2.7 |
