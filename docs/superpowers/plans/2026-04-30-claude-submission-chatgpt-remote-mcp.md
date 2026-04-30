# Claude Submission And ChatGPT Remote MCP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a human-reviewable Claude marketplace submission packet and implement a conservative ChatGPT remote MCP prototype profile.

**Architecture:** The Claude work is documentation-only and depends on the plugin package from PR #28. The ChatGPT work adds a small allowlist/policy module plus tests and docs, so the remote surface is built by positive inclusion rather than by exposing the full local Vulca MCP server.

**Tech Stack:** Markdown docs, pytest, Python 3.14, FastMCP/Vulca MCP server, existing `src/vulca/mcp_server.py` tools.

---

## Starting Conditions

Before implementing this plan:

- Rebase onto `master` after PR #28 is merged, or merge PR #28 into the work branch if it is still open.
- Verify `docs/platform/release-readiness-status.md` exists from PR #28.
- Run:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_visual_discovery_docs_truth.py tests/test_prompting.py -q
```

Expected: PASS.

## File Structure

- Create: `docs/platform/claude-submission-packet/README.md`
  - Submission overview and reviewer-facing checklist.
- Create: `docs/platform/claude-submission-packet/listing.md`
  - Marketplace listing copy with non-claims.
- Create: `docs/platform/claude-submission-packet/privacy.md`
  - Local files, provider keys, uploads, and approval boundaries.
- Create: `docs/platform/claude-submission-packet/validation.md`
  - Exact validation commands and results.
- Create: `docs/platform/claude-submission-packet/screenshots/README.md`
  - Screenshot capture checklist; image files are optional.
- Create: `src/vulca/mcp_profiles.py`
  - Remote-safe allowlist and per-tool policy metadata.
- Create: `src/vulca/mcp_remote.py`
  - Remote profile helper entry point for future HTTP transport wiring.
- Create: `tests/test_mcp_remote_profile.py`
  - Tests that prevent unsafe tools from entering the remote profile.
- Create: `docs/platform/chatgpt-remote-mcp-prototype.md`
  - ChatGPT/Responses API remote MCP guide.
- Modify: `docs/product/roadmap.md`
  - Mark Claude packet and remote MCP prototype status accurately.

## Task 1: Claude Submission Packet Docs

**Files:**
- Create: `docs/platform/claude-submission-packet/README.md`
- Create: `docs/platform/claude-submission-packet/listing.md`
- Create: `docs/platform/claude-submission-packet/privacy.md`
- Create: `docs/platform/claude-submission-packet/validation.md`
- Create: `docs/platform/claude-submission-packet/screenshots/README.md`

- [ ] **Step 1: Create packet directories**

Run:

```bash
mkdir -p docs/platform/claude-submission-packet/screenshots
```

Expected: directory exists.

- [ ] **Step 2: Write `README.md`**

Create `docs/platform/claude-submission-packet/README.md`:

```markdown
# Claude Submission Packet

**Status:** Human review packet
**Last verified:** 2026-04-30
**Depends on:** PR #28

## Submission Goal

Submit Vulca as a Claude Code plugin that adds agent-native visual discovery, decomposition, planning, and cultural evaluation workflows.

## Reviewer Summary

Vulca turns fuzzy visual intent into reviewable artifacts: discovery notes, direction cards, structured prompts, semantic layers, and L1-L5 evaluation. It is a workflow/control layer around configured image providers, not a hosted foundation model.

## Validated Skills

- `/vulca:visual-discovery`
- `/vulca:decompose`
- `/vulca:evaluate`
- `/vulca:visual-spec`
- `/vulca:visual-brainstorm`
- `/vulca:using-vulca-skills`
- `/vulca:visual-plan`

## Submission Form Guidance

- Product name: `Vulca`
- Category: developer tools, productivity, or creative workflow
- Repository: `https://github.com/vulca-org/vulca`
- Primary value: agent-native visual control for creative workflows
- Privacy note: local files stay local unless the user configures and approves a provider-backed operation.

## Packet Files

- `listing.md`: marketplace copy.
- `privacy.md`: data handling and user-approval language.
- `validation.md`: commands and observed validation results.
- `screenshots/README.md`: screenshot capture checklist.
```

- [ ] **Step 3: Write `listing.md`**

Create `docs/platform/claude-submission-packet/listing.md`:

```markdown
# Claude Marketplace Listing Draft

## One-Liner

Vulca is an agent-native visual control layer for discovery, structured prompts, semantic layers, and cultural evaluation.

## Short Description

Add visual discovery, decomposition, planning, and L1-L5 cultural evaluation workflows to Claude Code.

## Long Description

Vulca helps Claude Code users work with images through reviewable creative artifacts instead of one-shot prompting. It can explore fuzzy visual intent, produce direction cards, compose provider-aware prompts, decompose images into semantic layers, and evaluate visual results against cultural and quality criteria.

Vulca works with local files and configured image providers. Provider-backed generation, editing, and evaluation are explicit opt-in workflows.

## First-Release Emphasis

- Visual discovery and direction cards.
- Brainstorm/spec/plan artifacts.
- Semantic decomposition.
- L1-L5 evaluation.

## Do Not Claim

- Vulca hosts a foundation image model.
- Provider output quality is guaranteed.
- Cultural terminology guarantees better image generation.
- Redraw is polished for every image.
```

- [ ] **Step 4: Write `privacy.md`**

Create `docs/platform/claude-submission-packet/privacy.md`:

```markdown
# Claude Submission Privacy Notes

Vulca is local-first by default. It reads local project files and image paths when the user asks it to inspect, decompose, or evaluate local artifacts.

Provider-backed actions can send prompts, images, masks, or metadata to the configured provider. These actions must remain explicit opt-in and should show provider/model/cost metadata when available.

The first public submission should not enable remote upload, generation, redraw, inpaint, or VLM evaluation without user approval.
```

- [ ] **Step 5: Write `validation.md`**

Create `docs/platform/claude-submission-packet/validation.md`:

```markdown
# Claude Submission Validation

Run from the plugin package root after PR #28 is present:

```bash
/Users/yhryzy/.local/bin/claude plugin validate .
```

Expected: validation passed.

```bash
/Users/yhryzy/.local/bin/claude --plugin-dir . --print --max-budget-usd 0.20 --permission-mode dontAsk "Reply with only the Vulca plugin skill names you can see from loaded plugins; do not use tools."
```

Expected output includes:

- `vulca:visual-discovery`
- `vulca:decompose`
- `vulca:evaluate`
- `vulca:visual-spec`
- `vulca:visual-brainstorm`
- `vulca:using-vulca-skills`
- `vulca:visual-plan`
```

- [ ] **Step 6: Write screenshots checklist**

Create `docs/platform/claude-submission-packet/screenshots/README.md`:

```markdown
# Screenshot Checklist

Capture these before official submission:

- Plugin visible in Claude Code plugin UI.
- `/help` or skill list showing `vulca:*` skills.
- A no-cost `/vulca:visual-discovery` run producing direction cards.
- A no-cost `/vulca:evaluate` or rubric-only evaluation artifact.
- A terminal capture of `claude plugin validate .`.

Do not include private user images or provider API keys in screenshots.
```

- [ ] **Step 7: Validate docs exist**

Run:

```bash
test -f docs/platform/claude-submission-packet/README.md
test -f docs/platform/claude-submission-packet/listing.md
test -f docs/platform/claude-submission-packet/privacy.md
test -f docs/platform/claude-submission-packet/validation.md
test -f docs/platform/claude-submission-packet/screenshots/README.md
```

Expected: all commands exit 0.

## Task 2: Remote MCP Profile Tests

**Files:**
- Create: `tests/test_mcp_remote_profile.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_mcp_remote_profile.py`:

```python
from __future__ import annotations

from vulca.mcp_profiles import (
    REMOTE_DENIED_TOOLS,
    REMOTE_SAFE_TOOLS,
    get_remote_tool_policy,
    list_remote_safe_tools,
)


def test_remote_profile_exposes_only_safe_tools():
    assert list_remote_safe_tools() == [
        "compose_prompt_from_design",
        "evaluate_artwork",
        "get_tradition_guide",
        "list_traditions",
        "search_traditions",
    ]


def test_remote_profile_denies_generation_and_mutation_tools():
    unsafe = {
        "generate_image",
        "create_artwork",
        "generate_concepts",
        "inpaint_artwork",
        "layers_split",
        "layers_edit",
        "layers_redraw",
        "layers_composite",
        "layers_export",
        "layers_paste_back",
        "sync_data",
        "archive_session",
        "unload_models",
    }
    assert unsafe <= REMOTE_DENIED_TOOLS
    assert REMOTE_SAFE_TOOLS.isdisjoint(unsafe)


def test_remote_tool_policy_requires_approval_for_image_evaluation():
    policy = get_remote_tool_policy("evaluate_artwork")

    assert policy.name == "evaluate_artwork"
    assert policy.access == "read"
    assert policy.cost == "none_by_default"
    assert policy.image_exposure == "local_or_user_supplied"
    assert policy.requires_approval is True
    assert policy.default_kwargs == {"mock": True, "mode": "rubric_only"}


def test_unknown_remote_tool_policy_fails_closed():
    policy = get_remote_tool_policy("generate_image")

    assert policy.name == "generate_image"
    assert policy.allowed is False
    assert policy.requires_approval is True
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_mcp_remote_profile.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.mcp_profiles'`.

## Task 3: Remote MCP Profile Implementation

**Files:**
- Create: `src/vulca/mcp_profiles.py`

- [ ] **Step 1: Implement profile module**

Create `src/vulca/mcp_profiles.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


REMOTE_SAFE_TOOLS = frozenset(
    {
        "list_traditions",
        "get_tradition_guide",
        "search_traditions",
        "compose_prompt_from_design",
        "evaluate_artwork",
    }
)

REMOTE_DENIED_TOOLS = frozenset(
    {
        "generate_image",
        "create_artwork",
        "generate_concepts",
        "inpaint_artwork",
        "layers_split",
        "layers_edit",
        "layers_redraw",
        "layers_composite",
        "layers_export",
        "layers_paste_back",
        "sync_data",
        "archive_session",
        "unload_models",
    }
)


@dataclass(frozen=True)
class RemoteToolPolicy:
    name: str
    allowed: bool
    access: str = "read"
    cost: str = "none"
    image_exposure: str = "none"
    requires_approval: bool = False
    default_kwargs: Mapping[str, object] = field(default_factory=dict)


_POLICIES = {
    "list_traditions": RemoteToolPolicy(
        name="list_traditions",
        allowed=True,
    ),
    "get_tradition_guide": RemoteToolPolicy(
        name="get_tradition_guide",
        allowed=True,
    ),
    "search_traditions": RemoteToolPolicy(
        name="search_traditions",
        allowed=True,
    ),
    "compose_prompt_from_design": RemoteToolPolicy(
        name="compose_prompt_from_design",
        allowed=True,
    ),
    "evaluate_artwork": RemoteToolPolicy(
        name="evaluate_artwork",
        allowed=True,
        cost="none_by_default",
        image_exposure="local_or_user_supplied",
        requires_approval=True,
        default_kwargs=MappingProxyType({"mock": True, "mode": "rubric_only"}),
    ),
}


def list_remote_safe_tools() -> list[str]:
    return sorted(REMOTE_SAFE_TOOLS)


def get_remote_tool_policy(tool_name: str) -> RemoteToolPolicy:
    policy = _POLICIES.get(tool_name)
    if policy is not None:
        return policy
    return RemoteToolPolicy(
        name=tool_name,
        allowed=False,
        requires_approval=True,
    )
```

- [ ] **Step 2: Run profile tests**

Run:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_mcp_remote_profile.py -q
```

Expected: PASS.

## Task 4: Remote MCP Helper Module

**Files:**
- Create: `src/vulca/mcp_remote.py`
- Modify: `tests/test_mcp_remote_profile.py`

- [ ] **Step 1: Extend tests for helper module**

Append to `tests/test_mcp_remote_profile.py`:

```python
from vulca.mcp_remote import build_remote_mcp_server_summary


def test_remote_mcp_summary_uses_allowlist_and_policy():
    summary = build_remote_mcp_server_summary()

    assert summary["profile"] == "chatgpt_remote_safe"
    assert summary["allowed_tools"] == list_remote_safe_tools()
    assert summary["transport_status"] == "profile_only"
    assert summary["policies"]["evaluate_artwork"]["default_kwargs"] == {
        "mock": True,
        "mode": "rubric_only",
    }
```

- [ ] **Step 2: Implement helper module**

Create `src/vulca/mcp_remote.py`:

```python
from __future__ import annotations

from vulca.mcp_profiles import get_remote_tool_policy, list_remote_safe_tools


def _policy_to_dict(tool_name: str) -> dict[str, object]:
    policy = get_remote_tool_policy(tool_name)
    return {
        "allowed": policy.allowed,
        "access": policy.access,
        "cost": policy.cost,
        "image_exposure": policy.image_exposure,
        "requires_approval": policy.requires_approval,
        "default_kwargs": dict(policy.default_kwargs),
    }


def build_remote_mcp_server_summary() -> dict[str, object]:
    allowed_tools = list_remote_safe_tools()
    return {
        "profile": "chatgpt_remote_safe",
        "transport_status": "profile_only",
        "allowed_tools": allowed_tools,
        "policies": {
            tool_name: _policy_to_dict(tool_name)
            for tool_name in allowed_tools
        },
    }
```

- [ ] **Step 3: Run helper tests**

Run:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_mcp_remote_profile.py -q
```

Expected: PASS.

## Task 5: ChatGPT Remote MCP Prototype Docs

**Files:**
- Create: `docs/platform/chatgpt-remote-mcp-prototype.md`

- [ ] **Step 1: Write prototype guide**

Create `docs/platform/chatgpt-remote-mcp-prototype.md`:

```markdown
# ChatGPT Remote MCP Prototype

**Status:** Prototype profile
**Last verified:** 2026-04-30

## Purpose

Expose a conservative Vulca MCP profile for ChatGPT developer mode and OpenAI API remote MCP experiments.

## Allowed Tools

- `list_traditions`
- `get_tradition_guide`
- `search_traditions`
- `compose_prompt_from_design`
- `evaluate_artwork`

`evaluate_artwork` defaults to `mock=True` and `mode="rubric_only"` for the remote profile.

## Not Exposed By Default

Generation, inpaint, redraw, layer mutation, archive/sync/admin tools, and auto-registered pixel analysis tools are not exposed by the first remote profile.

## Responses API Pattern

```python
tools = [
    {
        "type": "mcp",
        "server_label": "vulca",
        "server_url": "https://example.com/mcp",
        "allowed_tools": [
            "list_traditions",
            "get_tradition_guide",
            "search_traditions",
            "compose_prompt_from_design",
            "evaluate_artwork",
        ],
        "require_approval": "always",
    }
]
```

## Privacy Rules

- Do not pass private images to a remote server without explicit user approval.
- Do not enable provider-backed VLM evaluation by default.
- Do not expose filesystem-writing tools in the first prototype.
- Keep all cost-incurring tools behind explicit opt-in.
```

- [ ] **Step 2: Scan docs for overclaims**

Run:

```bash
grep -RIn "always improves generatio[n]\|proves cultural promptin[g]\|official Codex public listing is liv[e]\|OpenAI plugin marketplac[e]\|Google plugin marketplac[e]" docs/platform docs/product README.md
```

Expected: no matches.

## Task 6: Roadmap Update

**Files:**
- Modify: `docs/product/roadmap.md`

- [ ] **Step 1: Update roadmap Next section**

In `docs/product/roadmap.md`, ensure `## Next` includes:

```markdown
- Claude marketplace submission packet review.
- ChatGPT remote MCP safe-profile prototype.
```

Do not remove the existing v0.22 redraw gate item.

- [ ] **Step 2: Run roadmap/docs tests**

Run:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: PASS.

## Task 7: Final Verification

**Files:**
- All files touched by Tasks 1-6.

- [ ] **Step 1: Run focused tests**

Run:

```bash
/opt/homebrew/bin/python3 -m pytest \
  tests/test_mcp_remote_profile.py \
  tests/test_visual_discovery_docs_truth.py \
  tests/test_prompting.py \
  -q
```

Expected: PASS.

- [ ] **Step 2: Run Claude validation if PR #28 package files are present**

Run:

```bash
if [ -f .claude-plugin/plugin.json ] && [ -d skills ]; then
  /Users/yhryzy/.local/bin/claude plugin validate .
fi
```

Expected: PASS when plugin package files exist; skipped otherwise.

- [ ] **Step 3: Review diff**

Run:

```bash
git diff -- docs/platform docs/product/roadmap.md docs/superpowers/specs docs/superpowers/plans src/vulca tests/test_mcp_remote_profile.py
```

Expected: only Claude submission packet docs, remote MCP profile code/tests/docs, roadmap status, and planning docs.

- [ ] **Step 4: Commit**

Run:

```bash
git add docs/platform docs/product/roadmap.md docs/superpowers/specs/2026-04-30-claude-submission-chatgpt-remote-mcp-design.md docs/superpowers/plans/2026-04-30-claude-submission-chatgpt-remote-mcp.md src/vulca/mcp_profiles.py src/vulca/mcp_remote.py tests/test_mcp_remote_profile.py
git commit -m "feat: add Claude submission and ChatGPT remote MCP plan"
```

Expected: commit succeeds.
