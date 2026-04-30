# Claude Submission Packet And ChatGPT Remote MCP Prototype Design

**Date:** 2026-04-30
**Status:** Draft approved direction
**Branch:** `codex/claude-chatgpt-platform-next`
**Depends on:** PR #28, `codex/platform-distribution-realtime-plan`

## Goal

Turn the platform packaging work from PR #28 into the next executable platform-integration step:

1. a Claude marketplace submission packet that a human can review and submit; and
2. a conservative ChatGPT remote MCP prototype spec that can be implemented without exposing high-risk image generation, redraw, inpaint, or filesystem mutation tools by default.

This is a design/spec step. It does not submit the Claude marketplace form, deploy a public MCP server, or expose user images remotely.

## Source-Verified Platform Facts

Current official docs verified on 2026-04-30:

- Claude Code plugins are shareable directories with `.claude-plugin/plugin.json`, root-level `skills/`, `.mcp.json`, and optional commands, agents, hooks, LSP servers, binaries, settings, and monitors.
- Claude plugin skills are namespaced as `/plugin-name:skill-name`.
- Claude official marketplace submission is through Claude.ai or Anthropic Console in-app forms.
- Codex has plugins and marketplace sources, but public plugin publishing remains a separate platform flow and should not be claimed as already available unless official docs change.
- ChatGPT developer mode and OpenAI API integrations can use remote MCP servers.
- OpenAI remote MCP guidance emphasizes limiting exposed tools and requiring approval for sensitive or write-capable operations.

Sources:

- [Claude Code create plugins](https://code.claude.com/docs/en/plugins)
- [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Codex plugins](https://developers.openai.com/codex/plugins)
- [Build Codex plugins](https://developers.openai.com/codex/plugins/build)
- [OpenAI MCP servers for ChatGPT Apps and API integrations](https://developers.openai.com/api/docs/mcp)
- [ChatGPT Developer mode](https://developers.openai.com/api/docs/guides/developer-mode)
- [MCP and Connectors](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)

## Product Position

The first public platform story should lead with workflow control, not raw image quality:

- discover visual direction;
- produce direction cards and structured prompts;
- decompose images into semantic layers;
- evaluate outputs with L1-L5 cultural/visual criteria;
- route provider-backed image operations only where the user explicitly opts in.

Redraw remains an advanced workflow until v0.22 target-aware mask refinement is merged and dogfooded on real images. Marketplace and remote MCP copy must not lead with redraw.

## Claude Submission Packet

The Claude packet is a human-reviewed folder of submission material, not an automatic form submission. It should live in:

```text
docs/platform/claude-submission-packet/
```

Required files:

- `README.md`: human submission brief with value proposition, install/test status, privacy notes, links to validation evidence, and form-fill guidance.
- `listing.md`: marketplace copy with one-liner, short description, long description, suggested categories, and explicit non-claims.
- `privacy.md`: local files, provider keys, optional external uploads, and user approval boundaries.
- `validation.md`: exact commands and observed results from PR #28 plus any fresh validation run.
- `screenshots/README.md`: checklist for screenshots or terminal captures. Actual image assets are optional and should not block the packet.

The packet should reference PR #28 as the package baseline and must not duplicate large docs already produced there.

### Claude Acceptance Criteria

- The packet tells a reviewer what Vulca does in one minute.
- It includes the seven validated skill names:
  - `vulca:visual-discovery`
  - `vulca:decompose`
  - `vulca:evaluate`
  - `vulca:visual-spec`
  - `vulca:visual-brainstorm`
  - `vulca:using-vulca-skills`
  - `vulca:visual-plan`
- It includes the validation evidence:
  - `claude plugin validate .`
  - `claude --plugin-dir . --print ...`
  - platform/provider/prompt test suite from PR #28.
- It explicitly says real-provider image work is opt-in.
- It explicitly says redraw/inpaint are advanced workflows, not polished first-release skills.

## ChatGPT Remote MCP Prototype

The ChatGPT remote MCP prototype should be designed as a separate profile around the existing Vulca MCP server. The first prototype is a remote-safe allowlist, not the full local Vulca MCP surface.

Initial allowlist:

- `list_traditions`
- `get_tradition_guide`
- `search_traditions`
- `compose_prompt_from_design`
- `evaluate_artwork` in `rubric_only` or `mock` mode only unless a human explicitly enables VLM/provider access.

Initial denylist:

- `generate_image`
- `create_artwork`
- `generate_concepts`
- `inpaint_artwork`
- `layers_split`
- `layers_edit`
- `layers_redraw`
- `layers_composite`
- `layers_export`
- `layers_paste_back`
- `sync_data`
- `archive_session`
- `unload_models`
- auto-registered pixel analysis tools until their data handling is reviewed.

### Remote MCP Configuration Shape

Implement the prototype as code that can produce an allowlisted FastMCP app or configuration profile, not by editing every existing tool manually.

Proposed files:

```text
src/vulca/mcp_profiles.py
src/vulca/mcp_remote.py
tests/test_mcp_remote_profile.py
docs/platform/chatgpt-remote-mcp-prototype.md
```

The profile module should define:

```python
REMOTE_SAFE_TOOLS = {
    "list_traditions",
    "get_tradition_guide",
    "search_traditions",
    "compose_prompt_from_design",
    "evaluate_artwork",
}
```

It should also define a policy for each tool:

- tool name;
- read/write classification;
- cost classification;
- image/file exposure classification;
- whether human approval is required.

The remote app module should expose a CLI/script entry point later, but the first implementation can stay behind tests and docs if the FastMCP HTTP transport details need a spike.

### ChatGPT Acceptance Criteria

- A test can assert the remote profile includes only the intended allowlist.
- A test can assert no generation, redraw, inpaint, layer mutation, filesystem-writing, or admin tools are exposed.
- `evaluate_artwork` defaults to a no-provider mode for remote use unless explicitly configured otherwise.
- Docs include an example Responses API `tools=[{"type": "mcp", ...}]` entry with `allowed_tools` and `require_approval`.
- Docs warn users not to pass private images to a remote server without explicit approval.

## Security And Privacy Rules

The remote MCP prototype must follow these defaults:

- no image generation by default;
- no remote image upload by default;
- no filesystem mutation by default;
- no local path browsing by default;
- no provider API calls by default;
- explicit approval for any tool that can incur cost, read images, write files, or call a provider.

The implementation should prefer allowlists over denylists. Denylists are useful for tests and documentation, but the actual remote surface should be built from positive inclusion.

## Rollout Order

1. Merge or review PR #28 so platform packaging is stable.
2. Add Claude submission packet docs.
3. Add ChatGPT remote MCP profile tests and docs.
4. Optionally add a remote MCP server entry point after confirming FastMCP HTTP transport behavior in this environment.
5. Dogfood with a local tunnel or staging host only after the allowlist tests pass.

## Non-Goals

- Submitting the Claude marketplace form from Codex.
- Deploying a public remote MCP server in this step.
- Exposing generation, redraw, inpaint, or layer mutation in the first ChatGPT MCP prototype.
- Claiming official Codex public listing has launched.
- Cleaning main-worktree generated assets.

## Open Questions For Implementation

- Whether FastMCP's installed version in the release environment supports the desired remote transport directly or needs a small ASGI wrapper.
- Whether `evaluate_artwork` needs a dedicated remote-safe wrapper, or whether passing `mode="rubric_only"` / `mock=True` is sufficient.
- Where a staging remote MCP server should be hosted once the prototype leaves local tests.
