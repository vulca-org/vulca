# Platform Release Readiness Status

**Status:** Working release gate summary
**Last updated:** 2026-05-01

## Current Claims We Can Make

- Vulca has a Claude plugin package shape at the repository root: `.claude-plugin/plugin.json`, `.mcp.json`, and `skills/`.
- Vulca has a repo-local Codex plugin package for validation: `plugins/vulca/.codex-plugin/plugin.json`, `plugins/vulca/.mcp.json`, and `plugins/vulca/skills/`.
- Codex can be documented as a plugin plus MCP target; official public Codex plugin publishing should remain future-facing until OpenAI opens that flow.
- ChatGPT can be documented as a remote MCP app/prototype target.
- Google/Gemini can be documented as a provider path now, with ADK / Vertex Agent Engine later.
- Redraw is an advanced workflow today. v0.22 target-aware mask refinement is merged, but polished `/inpaint` or `/redraw-layer` promotion remains gated on real-image dogfood evidence.

## Claims We Should Not Make Yet

- Do not claim the public Codex listing has already launched.
- Do not claim Google has a Vulca plugin marketplace path.
- Do not claim cultural terminology guarantees better generation.
- Do not lead marketplace copy with redraw quality until v0.22 is dogfooded on representative real images.
- Do not present transparent layer assets as final after-images.

## Verification Evidence

Run in `master` on 2026-05-01:

```bash
/opt/homebrew/bin/codex marketplace add .
```

Observed: added marketplace `vulca-plugins` from this worktree.

```bash
/Users/yhryzy/.local/bin/claude plugin validate .
```

Observed: validation passed.

Run in `/Users/yhryzy/dev/vulca-plugin` on 2026-05-01:

```bash
/Users/yhryzy/.local/bin/claude plugin validate .
/Users/yhryzy/.local/bin/claude plugin validate .claude-plugin/plugin.json
```

Observed: marketplace and plugin manifest validation passed. `vulca-plugin` PR #9 synced the standalone plugin repository to v0.19.0 and was merged at commit `55b6bb371544cd199e43f493b763d34e9cb85f5e`.

```bash
/Users/yhryzy/.local/bin/claude --plugin-dir . --print --max-budget-usd 0.20 --permission-mode dontAsk "Reply with only the Vulca plugin skill names you can see from loaded plugins; do not use tools."
```

Observed skills:

- `vulca:visual-discovery`
- `vulca:decompose`
- `vulca:evaluate`
- `vulca:visual-spec`
- `vulca:visual-brainstorm`
- `vulca:using-vulca-skills`
- `vulca:visual-plan`

```bash
/opt/homebrew/bin/python3 scripts/sync_plugin_skills.py
```

Observed: synced `.agents/skills` into `.claude/skills`, `skills`, and `plugins/vulca/skills`.

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_prompting.py tests/test_visual_discovery_docs_truth.py tests/test_visual_discovery_prompting.py tests/test_visual_discovery_benchmark.py tests/test_gemini_image_size.py tests/test_generate_image_extended_signature.py -q
```

Observed: 60 passed.

```bash
grep -RIn "culture term[s] guarantee\|cultural term[s] guarantee\|always improves generatio[n]\|proves cultural promptin[g]\|official Codex public listing is liv[e]\|official Codex public publishing is liv[e]\|OpenAI plugin marketplac[e]\|21 MCP tool[s]\|20 MCP tool[s]\|21 tool[s]\|\.Codex/skill[s]" README.md pyproject.toml .claude-plugin .agents/skills .claude/skills skills docs/product docs/platform plugins/vulca src/vulca/mcp_server.py
```

Observed: no matches.

Run after v0.22 merge:

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_mask_refine.py tests/test_layers_redraw_refinement.py tests/test_redraw_review_contract.py -q
```

Observed: 14 passed.

```bash
/opt/homebrew/bin/python3 -m pytest tests/test_mask_refine.py tests/test_layers_redraw_refinement.py tests/test_layers_redraw_crop_pipeline.py tests/test_layers_redraw_quality_gates.py tests/test_layers_redraw_strategy.py tests/test_layers_redraw.py tests/test_provider_edit_capabilities.py tests/vulca/providers/test_capabilities.py -q
```

Observed: 44 passed.

## Manual Gates Remaining

- Optional: run a full interactive `claude --plugin-dir .` session if you want UI-level confirmation beyond `plugin validate` and non-interactive skill discovery.
- Optional: open Codex UI and confirm the newly added `vulca-plugins` marketplace source appears as expected.
- Review marketplace copy and screenshots before submission.
- Dogfood v0.22 redraw on representative real images and confirm the user-facing after-image is `source_pasteback_path`.
- Decide what to do with main-worktree untracked generated artifacts before any broad cleanup.
