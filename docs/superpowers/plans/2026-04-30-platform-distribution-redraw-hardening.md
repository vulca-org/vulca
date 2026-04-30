# Platform Distribution + Redraw Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare Vulca for Claude marketplace distribution, Codex plugin plus MCP integration, ChatGPT remote MCP integration, Google/Gemini provider-facing guidance, and v0.22-gated redraw promotion.

**Architecture:** This is a release-readiness plan split into four independently testable tracks: platform research truth, Claude plugin packaging, Codex plugin plus MCP distribution, and redraw promotion gating. Runtime image/provider behavior is not changed in this plan except where a later task explicitly integrates the already-isolated v0.22 redraw branch after review.

**Tech Stack:** Claude Code plugins, MCP, FastMCP/Vulca MCP server, Markdown docs, pytest doc truth tests, existing Vulca Python package, existing v0.22 redraw worktree.

---

## Source Inputs

- Product brief: `docs/product/2026-04-30-product-positioning-brief.md`
- Platform research brief: `docs/product/platform-distribution-realtime-brief.md`
- Provider matrix: `docs/product/provider-capabilities.md`
- Roadmap: `docs/product/roadmap.md`
- Claude plugin manifest: `.claude-plugin/plugin.json`
- Claude skills: `.claude/skills/*/SKILL.md` and `.agents/skills/*/SKILL.md`
- MCP config: `.mcp.json`
- MCP server: `src/vulca/mcp_server.py`
- v0.22 redraw worktree: `.worktrees/v0-22-mask-refinement`

## File Structure

- Modify: `.claude-plugin/plugin.json`
  - Keep plugin metadata current and remove fixed MCP tool count claims.
- Create: `docs/product/platform-distribution-realtime-brief.md`
  - Source-backed platform facts and product implications.
- Modify: `docs/product/provider-capabilities.md`
  - Mark Claude marketplace, Codex plugin/MCP, ChatGPT remote MCP, and Google provider/ADK status accurately.
- Modify: `docs/product/roadmap.md`
  - Add distribution and v0.22 gate to near-term roadmap without overclaiming redraw.
- Modify: `tests/test_visual_discovery_docs_truth.py`
  - Lock public docs and plugin manifest against stale tool-count claims.
- Create later: `docs/platform/claude-plugin-marketplace-checklist.md`
  - Clean install and submission checklist for Claude marketplace.
- Create later: `docs/platform/manual-review-checklist.md`
  - Human review gate for Claude, Codex, and redraw promotion.
- Create later: `scripts/sync_plugin_skills.py`
  - Sync canonical `.agents/skills` into Claude and Codex plugin package locations.
- Create later: `docs/platform/openai-codex-mcp-guide.md`
  - Repo-local Codex plugin package, local Codex MCP, and remote MCP guidance.
- Create later: `docs/platform/google-gemini-provider-guide.md`
  - Gemini provider, ADK, and Vertex Agent Engine posture.

## Task 1: Platform Fact Brief And Truth Tests

**Files:**
- Create: `docs/product/platform-distribution-realtime-brief.md`
- Modify: `tests/test_visual_discovery_docs_truth.py`
- Modify: `.claude-plugin/plugin.json`

- [ ] **Step 1: Add the platform fact brief**

Create `docs/product/platform-distribution-realtime-brief.md` with the sections:

```markdown
# Vulca Platform Distribution Realtime Brief

**Status:** Working brief for platform distribution
**Last verified:** 2026-04-30

## Position

- Claude Code: plugin marketplace path first.
- OpenAI Codex / ChatGPT: Codex plugin plus MCP path first; ChatGPT remote MCP app path second.
- Google / Gemini: provider integration now, ADK / Vertex Agent Engine path later.

## Claude Code

Include links to:
- https://code.claude.com/docs/en/plugins
- https://code.claude.com/docs/en/discover-plugins
- https://code.claude.com/docs/en/plugin-marketplaces

State that Claude Code plugins can package skills, commands, agents, hooks, MCP servers, and related config. State that official marketplace submission is through Claude.ai or Console in-app forms.

## OpenAI / Codex / ChatGPT

Include links to:
- https://developers.openai.com/codex/plugins
- https://developers.openai.com/codex/plugins/build
- https://platform.openai.com/docs/docs-mcp
- https://platform.openai.com/docs/mcp/
- https://platform.openai.com/docs/guides/tools-remote-mcp
- https://platform.openai.com/docs/guides/developer-mode

State that Codex supports plugins and MCP configuration, ChatGPT developer mode supports remote MCP apps, and Responses API supports remote MCP tools. State that OpenAI's public Codex plugin publishing flow is documented as coming soon, so the near-term path is repo-local/personal marketplace validation.

## Google / Gemini

Include links to:
- https://ai.google.dev/gemini-api/docs/image-generation
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation
- https://ai.google.dev/gemini-api/docs/function-calling
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview
- https://google.github.io/adk-docs/mcp/

State that Gemini is a current provider path and Google agent distribution remains planned.
```

- [ ] **Step 2: Extend the stale tool count test**

In `tests/test_visual_discovery_docs_truth.py`, update `test_stale_tool_count_claims_removed_from_public_docs()` so `public_text` includes `.claude-plugin/plugin.json`:

```python
public_text = "\n".join(
    [
        (ROOT / "README.md").read_text(encoding="utf-8"),
        (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
        (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"),
        (ROOT / "src" / "vulca" / "mcp_server.py").read_text(
            encoding="utf-8"
        ),
    ]
)
```

- [ ] **Step 3: Run the truth test and verify it fails before metadata fix**

Run:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_visual_discovery_docs_truth.py::test_stale_tool_count_claims_removed_from_public_docs -q
```

Expected: FAIL because `.claude-plugin/plugin.json` still contains the stale fixed MCP tool-count phrase.

- [ ] **Step 4: Fix plugin manifest metadata**

Replace `.claude-plugin/plugin.json` with:

```json
{
  "name": "vulca",
  "version": "0.19.0",
  "description": "Vulca visual-control plugin for Claude Code: discovery, brainstorm, spec, plan, evaluate, and decompose workflows backed by Vulca MCP tools.",
  "homepage": "https://github.com/vulca-org/vulca-plugin",
  "license": "Apache-2.0",
  "author": {
    "name": "Vulca maintainers",
    "url": "https://github.com/vulca-org"
  }
}
```

- [ ] **Step 5: Run the truth test and verify it passes**

Run:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_visual_discovery_docs_truth.py::test_stale_tool_count_claims_removed_from_public_docs -q
```

Expected: PASS.

## Task 2: Provider Matrix And Roadmap Accuracy

**Files:**
- Modify: `docs/product/provider-capabilities.md`
- Modify: `docs/product/roadmap.md`

- [ ] **Step 1: Update agent surface statuses**

In `docs/product/provider-capabilities.md`, replace the Agent Surfaces table with:

```markdown
| Surface | Role | Status |
|---|---|---|
| Claude Code | Primary agent surface for MCP tools, skills, and marketplace distribution | Current, marketplace packaging next |
| OpenAI Codex | Plugin marketplace surface plus local MCP consumer for developer workflows | Repo-local Codex plugin package current, official public listing later |
| ChatGPT developer mode | Remote MCP app surface for interactive workflows | Remote MCP prototype planned |
| Gemini API / Vertex AI | Image provider and future agent runtime target | Provider current, ADK/Agent Engine planned |
| Python SDK / CLI | Power-user and test harness path | Current |
| Vulca Studio UI | Review surface for cards, sketches, layers, and evaluations | Later |
```

- [ ] **Step 2: Add platform distribution to roadmap**

In `docs/product/roadmap.md`, set `## Next` to:

```markdown
## Next

- Claude plugin marketplace packaging and submission checklist.
- Codex plugin marketplace validation and MCP usage guide.
- ChatGPT remote MCP prototype scope.
- Cultural-term efficacy benchmark real-provider opt-in.
- v0.22 target-aware mask refinement review and merge gate.
```

- [ ] **Step 3: Run docs truth tests**

Run:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: PASS.

## Task 3: Claude Plugin Marketplace Readiness

**Files:**
- Create: `docs/platform/claude-plugin-marketplace-checklist.md`
- Modify if needed: `.claude-plugin/plugin.json`
- Modify if needed: `.mcp.json`

- [ ] **Step 1: Create the checklist directory**

Run:

```bash
mkdir -p docs/platform
```

- [ ] **Step 2: Write the Claude plugin submission checklist**

Create `docs/platform/claude-plugin-marketplace-checklist.md` with:

```markdown
# Claude Plugin Submission Checklist

**Status:** Draft checklist
**Last verified:** 2026-04-30

## Package Contents

- `.claude-plugin/plugin.json`
- `.mcp.json`
- `skills/decompose/SKILL.md`
- `skills/visual-discovery/SKILL.md`
- `skills/visual-brainstorm/SKILL.md`
- `skills/visual-spec/SKILL.md`
- `skills/visual-plan/SKILL.md`
- `skills/evaluate/SKILL.md`
- `skills/using-vulca-skills/SKILL.md`
- `README.md`

## Clean Install Test

1. Build or sync the standalone plugin repository.
2. Run `claude --plugin-dir <plugin-path>` from a clean test checkout.
3. Run `/help` and verify namespaced Vulca skills appear.
4. Run a no-cost `/evaluate` or prompt-composition path.
5. Run `/decompose` only with local image paths and no cloud provider keys.
6. Confirm MCP startup uses documented env variables and does not require secrets by default.

## Submission Gate

- No fixed MCP tool count claims.
- No promise that cultural terms improve output quality.
- No public promotion of `/inpaint` or `/redraw-layer` until v0.22 evidence lands.
- Real-provider generation is explicit opt-in.
- README includes security notes for local file access and provider uploads.

## Submission Path

Submit through one of:

- Claude.ai plugin submission form.
- Anthropic Console plugin submission form.

Keep a private marketplace fallback using `.claude-plugin/marketplace.json` if official review takes longer than launch timing.
```

- [ ] **Step 3: Verify no stale count claims**

Run:

```bash
grep -RIn "21 MCP tool[s]\|20 MCP tool[s]\|21 tool[s]" .claude-plugin docs/platform README.md pyproject.toml src/vulca/mcp_server.py
```

Expected: no matches.

## Task 4: Codex Plugin And MCP Distribution Guide

**Files:**
- Create: `plugins/vulca/.codex-plugin/plugin.json`
- Create: `plugins/vulca/.mcp.json`
- Copy: `.agents/skills/*` into `plugins/vulca/skills/`
- Create: `.agents/plugins/marketplace.json`
- Create: `docs/platform/openai-codex-mcp-guide.md`

- [ ] **Step 1: Create repo-local Codex plugin package**

Create `plugins/vulca/.codex-plugin/plugin.json` with concrete metadata, `skills: "./skills/"`, and `mcpServers: "./.mcp.json"`.

Create `plugins/vulca/.mcp.json` with a local `vulca-mcp` server entry.

Copy the current Vulca skills into `plugins/vulca/skills/` so the plugin is self-contained for Codex testing.

- [ ] **Step 2: Create repo marketplace entry**

Create `.agents/plugins/marketplace.json` with:

```json
{
  "name": "vulca-plugins",
  "interface": {
    "displayName": "Vulca Plugins"
  },
  "plugins": [
    {
      "name": "vulca",
      "source": {
        "source": "local",
        "path": "./plugins/vulca"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_USE"
      },
      "category": "Productivity"
    }
  ]
}
```

- [ ] **Step 3: Write local and remote MCP guide**

Create `docs/platform/openai-codex-mcp-guide.md` with:

```markdown
# OpenAI Codex and ChatGPT MCP Guide

**Status:** Draft guide
**Last verified:** 2026-04-30

## Codex Plugin Path

The repo contains `plugins/vulca/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` for local marketplace validation.

Observed local CLI:

```bash
codex marketplace add .
```

Official docs may show `codex plugin marketplace add`; verify against the installed CLI before release.

Official public plugin publishing is documented as coming soon, so do not promise immediate official listing until OpenAI opens that flow.

## Local Codex MCP

Codex can connect to MCP servers from CLI or IDE configuration. The local Vulca path should use the existing `vulca-mcp` command.

Example:

```bash
codex mcp add vulca -- /opt/homebrew/bin/vulca-mcp
codex mcp list
```

## Remote MCP Prototype

The remote MCP prototype must expose a conservative tool set first:

- `list_traditions`
- `get_tradition_guide`
- `search_traditions`
- `compose_prompt_from_design`
- `evaluate_artwork`

Do not expose generation, redraw, inpaint, paste-back, or filesystem-writing layer tools by default.

## Responses API Pattern

Use `tools=[{"type":"mcp", "server_label":"vulca", "server_url":"https://...", "allowed_tools":[...], "require_approval":"always"}]` for early tests.

## Safety Rules

- Require approval for sensitive or cost-incurring tools.
- Use `allowed_tools`.
- Do not pass private images to a remote server without user approval.
- Log provider/model/cost metadata.
```

- [ ] **Step 4: Verify no official-listing overclaim**

Run:

```bash
grep -RIn "official Codex public listing is liv[e]\|official Codex public publishing is liv[e]\|OpenAI plugin marketplac[e]" docs/product docs/platform README.md plugins/vulca
```

Expected: no matches.

## Task 5: Google/Gemini Provider Guide

**Files:**
- Create: `docs/platform/google-gemini-provider-guide.md`

- [ ] **Step 1: Write Google posture guide**

Create `docs/platform/google-gemini-provider-guide.md` with:

```markdown
# Google Gemini Provider Guide

**Status:** Draft guide
**Last verified:** 2026-04-30

## Current Role

Gemini is a Vulca image provider path. Use it for sketching, reference-heavy exploration, image editing experiments, and provider comparisons.

## Planned Agent Role

Google ADK and Vertex AI Agent Engine are future integration targets. Do not describe them as an existing Vulca plugin marketplace.

## Provider Notes

- Gemini image models can generate and edit images through Gemini API / Vertex AI.
- Gemini 2.5 Flash Image and Gemini 3 Pro Image preview are the relevant image-output model families in current docs.
- Gemini 2.5 Flash Image supports 1024px output; Gemini 3 Pro Image preview supports up to 4096px in Vertex AI docs.
- Google ADK supports MCP tool use for agents.

## Vulca Work Items

- Keep `gemini` / `nb2` provider capability gates current.
- Add provider benchmark results before making quality claims.
- Add ADK or Vertex Agent Engine sample only after local provider and MCP docs are stable.
```

- [ ] **Step 2: Verify provider docs truth**

Run:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_gemini_image_size.py tests/test_generate_image_extended_signature.py -q
```

Expected: PASS.

## Task 6: v0.22 Redraw Merge And Promotion Gate

**Files:**
- Read from: `.worktrees/v0-22-mask-refinement`
- Modify later: `docs/product/roadmap.md`
- Modify later: `README.md`

- [ ] **Step 1: Run v0.22 focused tests in the v0.22 worktree**

Run:

```bash
cd .worktrees/v0-22-mask-refinement
/opt/homebrew/bin/python3 -m pytest tests/test_mask_refine.py tests/test_layers_redraw_refinement.py tests/test_redraw_review_contract.py -q
```

Expected: PASS.

- [ ] **Step 2: Run v0.22 broader redraw suite**

Run:

```bash
cd .worktrees/v0-22-mask-refinement
/opt/homebrew/bin/python3 -m pytest \
  tests/test_mask_refine.py \
  tests/test_layers_redraw_refinement.py \
  tests/test_layers_redraw_crop_pipeline.py \
  tests/test_layers_redraw_quality_gates.py \
  tests/test_layers_redraw_strategy.py \
  tests/test_layers_redraw.py \
  tests/test_provider_edit_capabilities.py \
  tests/vulca/providers/test_capabilities.py \
  -q
```

Expected: PASS or a precise failure list before merge.

- [ ] **Step 3: Review v0.22 public contract**

Read:

```text
.worktrees/v0-22-mask-refinement/docs/superpowers/specs/2026-04-30-redraw-showcase-product-contract-design.md
.worktrees/v0-22-mask-refinement/docs/superpowers/specs/2026-04-30-v0.22-target-aware-mask-refinement-design.md
```

Acceptance:

- `source_pasteback_path` is the primary user-facing after image.
- `file` remains the editable layer asset.
- Sparse transparent layer assets are not presented as final outputs.
- `refinement_applied`, `refined_child_count`, and quality advisory fields are present.

- [ ] **Step 4: Keep public promotion conservative**

Until real-image dogfood passes, public docs must use this wording:

```markdown
Redraw and inpaint tools are available for advanced workflows. Polished user-facing `/inpaint` or `/redraw-layer` skills will be promoted after v0.22 target-aware mask refinement evidence lands.
```

## Task 7: Final Verification

**Files:**
- All files touched by Tasks 1-5.

- [ ] **Step 1: Run focused docs/platform tests**

Run:

```bash
/opt/homebrew/bin/python3 -m pytest \
  tests/test_visual_discovery_docs_truth.py \
  tests/test_prompting.py \
  tests/test_visual_discovery_prompting.py \
  tests/test_visual_discovery_benchmark.py \
  -q
```

Expected: PASS.

- [ ] **Step 2: Scan public docs for forbidden phrases**

Run:

```bash
grep -RIn "culture terms guarantee\|cultural terms guarantee\|always improves generatio[n]\|proves cultural promptin[g]\|official Codex public listing is liv[e]\|official Codex public publishing is liv[e]\|OpenAI plugin marketplac[e]\|21 MCP tool[s]\|20 MCP tool[s]" README.md pyproject.toml .claude-plugin docs/product docs/platform plugins/vulca src/vulca/mcp_server.py
```

Expected: no matches.

- [ ] **Step 3: Review diff**

Run:

```bash
git diff -- .claude-plugin docs/product docs/platform docs/superpowers/plans tests/test_visual_discovery_docs_truth.py
```

Expected: only platform distribution docs, plugin manifest metadata, roadmap/provider matrix accuracy, and truth-test changes.
