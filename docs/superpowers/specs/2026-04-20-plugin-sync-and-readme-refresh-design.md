# Plugin Sync + README Refresh Design

**Date:** 2026-04-20
**Owner:** yhryzy (solo)
**Status:** Draft (brainstorm complete, pre-plan)

## Context

As of 2026-04-20 the `vulca-org/vulca` landing page does not reflect 11 days of work: the agent-native pivot (2026-04-16), v0.16.0 + v0.16.1 (Phase 1 MCP surface refactor 29→20+1 tools), and the 2026-04-19 ship of `.claude/skills/decompose/SKILL.md` (the first agent-facing skill).

Traffic data collected 2026-04-20 confirms conversion is broken: 14-day views **82 / 31 unique (↓61% vs 211 baseline)**, **zero social referrals** despite two Xiaohongshu carousels on 2026-04-18, PyPI downloads **~72/day (↓50% vs 140 baseline)**. Prior parallel reviews (2026-04-18) flagged "attribution collapse" — visitors land but don't convert.

Pre-spec verification surfaced a blocker: **`vulca-org/vulca-plugin` is 13 days stale (v0.9.0)**. Its README advertises 21 MCP tools but lists tools Phase 1 removed (`resume_artwork`, `studio_*`, `analyze_layers`, `layers_regenerate`, `tool_*`). Its 10 `skills/` subdirectories are empty. The `/decompose` skill does not ship inside it. Advertising `claude plugin install vulca-org/vulca-plugin` in the refreshed README would break the hero's "hands for Claude Code" promise at the first copy-paste.

Therefore this work is one design spanning two sequential phases: **Phase 1 fixes the plugin. Phase 2 refreshes the main README.** Phase 2 merges only after Phase 1 ships.

## Goals

1. Restore a working `claude plugin install vulca-org/vulca-plugin` path that matches the v0.16.1 MCP surface and bundles the `/decompose` skill.
2. Replace the stale main README with an agent-native-first landing page that converts MCP/Claude Code-curious cold visitors, documented honestly against the 6-cluster capability map.
3. Align the GitHub "About" description and topics with the new positioning in the same PR as the README change.
4. Instrument CTA links with UTM so the next traffic review (2026-05-04) can attribute README-origin visits.

## Non-goals

- No SDK behavior changes. No new MCP tools. No new skills beyond bundling the existing `/decompose`.
- No XHS post strategy changes (tracked separately in `memory/project_xhs_style_experiments.md`).
- No `.claude-plugin/marketplace.json` multi-plugin support. Keep single-plugin marketplace.
- No blog post / dev.to / GitHub Discussion update. README-first; other channels follow if traffic recovers.
- No demo GIF re-recording in this cycle. The 4 v2 GIFs currently referenced in the README (`vhs-create/layers/studio/tools.gif`) are CLI recordings that contradict the agent-native hero; drop their README references, keep the files.
- No asciinema production. Agent-loop proof uses a zero-cost transcript code block in v1.

---

## Phase 1 — vulca-plugin sync to v0.16.1

### Source of truth

- Current `@mcp.tool()` count in `src/vulca/mcp_server.py` = **21** (grep-verified 2026-04-20)
- Authoritative tool list (memory `project_phase1_complete`): `generate_image, create_artwork, inpaint_artwork, view_image, evaluate_artwork, list_traditions, get_tradition_guide, search_traditions, layers_split, layers_list, layers_edit, layers_redraw, layers_transform, layers_composite, layers_export, layers_evaluate, brief_parse, generate_concepts, archive_session, sync_data, unload_models`
- Skill source: `.claude/skills/decompose/SKILL.md` in the main repo

### Changes in `vulca-org/vulca-plugin`

1. **`.claude-plugin/plugin.json`**
   - `version: "0.9.0"` → `"0.16.1"` (track SDK version exactly so drift is visible)
   - `description`: rewrite to "Agent-native image-editing MCP surface for Claude Code & Cursor. 21 MCP tools + /decompose skill. Powered by vulca SDK."
   - `keywords`: add `agent-native`, `claude-code`, `anthropic`, `decompose`; keep `mcp`, `image-generation`, `l1-l5`

2. **`.claude-plugin/marketplace.json`**
   - Bump `plugins[0].version` to `0.16.1`
   - Update `plugins[0].description` to match plugin.json

3. **`.mcp.json`** — no change. `uvx --from vulca[mcp] vulca-mcp` still correct.

4. **`skills/` directory — full replacement**
   - Delete all 10 empty subdirectories: `create`, `evaluate`, `evolution`, `inpaint`, `layers`, `release`, `resume`, `studio`, `sync`, `tradition`
   - Add `skills/decompose/SKILL.md` — copy from `vulca/.claude/skills/decompose/SKILL.md` verbatim
   - Result: plugin ships exactly 1 skill, matching reality

5. **`agents/cultural-critic.md`** — **delete** (resolved inline per Codex flag on hidden decisions). Rationale: Phase 1 ships exactly 1 skill (`/decompose`); an orphan agent file referencing Phase-1-removed tools is maintenance debt without a user-facing hook. Re-introduce later when there is an actual agent-level flow to support.

6. **`README.md`** (plugin's own README)
   - Rewrite to mirror the main README's hero: "Agent-native image-editing for Claude Code & Cursor. 21 MCP tools + /decompose skill."
   - Replace the stale 21-tool table with the correct v0.16.1 tool list
   - Delete the "Skills (10)" section; replace with "Skills (1)" naming only `/decompose`
   - Delete the "Agent" section entirely (cultural-critic is deleted per source-section item 5)
   - Install block stays `pip install vulca[mcp]` + `claude plugin install vulca-org/vulca-plugin`

### Verification (blocks release)

Run from a macOS account with **no prior `~/.claude/plugins/vulca*` directory and no prior `~/.claude/skills/decompose/` directory** (rename them aside if present; restore after). Do not require a second machine.

- [ ] `pip install vulca[mcp]==0.16.1` succeeds from a fresh venv
- [ ] `claude plugin install vulca-org/vulca-plugin@v0.16.1` (tagged release, not default branch) succeeds
- [ ] In Claude Code, typing `/decompose` shows the skill as an available slash command (auto-discovery check)
- [ ] Running `/decompose <any test image>` reaches `layers_split` tool call (mock provider OK; assertion is that the tool call fires, not that real generation succeeds)
- [ ] A Claude Code query that lists available MCP tools returns exactly **21** tool names, and the set matches the Phase 1 source-of-truth list character-for-character (save output to `verification-tools-v0.16.1.txt` for the PR description)
- [ ] After verification, restore the renamed-aside user directories

### Phase 1 acceptance criteria

- [ ] Plugin repo tagged `v0.16.1` with release notes mentioning sync to SDK v0.16.1 + `/decompose` bundling
- [ ] Main-repo `README.md` bytes unchanged — Phase 1 ships independently
- [ ] Plugin `.claude-plugin/plugin.json` has `"version": "0.16.1"` and description contains the substring `"21 MCP tools"`
- [ ] Plugin `.claude-plugin/marketplace.json` `plugins[0].version` equals `"0.16.1"`
- [ ] Plugin `skills/decompose/SKILL.md` exists and its SHA matches `vulca/.claude/skills/decompose/SKILL.md` (byte-identical copy)
- [ ] Plugin `skills/` contains exactly one subdirectory named `decompose` (the other 9 previously-empty dirs are deleted)
- [ ] Plugin `agents/cultural-critic.md` file is deleted
- [ ] Plugin `README.md` tool table lists the same 21 tool names as Phase 1 source-of-truth (grep-verifiable)
- [ ] All 6 items in the Verification checklist above pass

---

## Phase 2 — Main repo README refresh

### Hero (locked)

> **Agents can plan image edits but can't cut pixels. Vulca is the hands — semantic layer splits, cultural scoring, inpainting — as 21 MCP tools for Claude Code.**

Rationale: negative-frame opening matches the MCP-ecosystem cold visitor's mental model ("I want my agent to manipulate images"); the "hands" metaphor is shareable out-of-context on X / Discord; "21 MCP tools for Claude Code" is a concrete specificity anchor. Codex review picked this; Superpowers review flagged "subordinate plumbing" risk which we accept because the user explicitly chose D+A.

### Structure (single file, zoned, ~450 lines target)

#### Top zone (~40% of length, fold-critical)

1. **Badges** — PyPI version, Python 3.10+, Apache 2.0, MCP Tools: `21` (hardcoded; update on every release that changes the tool count; add to release-checklist memory)
2. **Hero paragraph** (locked above)
3. **Stats strip** (one line, scoped to the demo below, not the whole product):
   > *Below: Mona Lisa → `face_and_hair.png` + `body_and_dress.png`, decomposed locally on Apple Silicon (ComfyUI + Ollama) with zero cloud API calls. SDK total: 21 MCP tools · 1446 tests passing.*
4. **`## What happens when you run /decompose`** — agent transcript block (moved above setup per final review; the "what does this do" hook must precede the "how do I install it" follow-through):
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

5. **`## Try it in 60 seconds`** — dual-path install. **Prerequisite:** `uv` installed (provides `uvx`) — `curl -LsSf https://astral.sh/uv/install.sh | sh` or see https://docs.astral.sh/uv/. Without `uv`, substitute `uvx --from vulca[mcp] vulca-mcp` with `python -m vulca.mcp_server` in the Path B config.
   - Path A (recommended, requires Phase 1 plugin at v0.16.1+):
     ```bash
     pip install vulca[mcp]==0.16.1
     claude plugin install vulca-org/vulca-plugin
     ```
     Then in Claude Code: `> /decompose assets/your_image.jpg`
   - Path B (no plugin, power user):
     ```bash
     pip install vulca[mcp]==0.16.1

     # Register MCP server — add to ~/.claude/settings.json:
     {"mcpServers": {"vulca": {"command": "uvx", "args": ["--from", "vulca[mcp]==0.16.1", "vulca-mcp"]}}}

     # Install the /decompose skill (single file, ~7 KB):
     mkdir -p ~/.claude/skills/decompose
     curl -o ~/.claude/skills/decompose/SKILL.md \
       https://raw.githubusercontent.com/vulca-org/vulca/v0.16.1/.claude/skills/decompose/SKILL.md
     ```

6. **One static proof image**: Mona Lisa original → `face_and_hair.png` + `body_and_dress.png`, side-by-side. Use existing `assets/demo/v2/masters/mona_lisa_*` files.

#### Middle zone (~30% of length) — the capability map

1. **Section header:** `## What Vulca takes off your agent's hands`
2. **6-cluster map** (organized by "manual work the agent offloads", not by internal tool names — Codex review's framing):

   | Cluster | What your agent delegates to Vulca | Agent skill | Tools |
   |---|---|---|---|
   | **Decompose** | Extract 10–20 semantic layers from any image with real transparency. | ✅ `/decompose` | `layers_split` (orchestrated), `layers_list` |
   | **Edit** | Redraw one region or one layer without touching the rest. Composite back. | Roadmap | `inpaint_artwork`, `layers_edit`, `layers_redraw`, `layers_transform`, `layers_composite`, `layers_export`, `layers_evaluate` |
   | **Evaluate** | Judge a visual against L1–L5 cultural criteria over 13 traditions with citable rationale. | Roadmap | `evaluate_artwork`, `list_traditions`, `get_tradition_guide`, `search_traditions` |
   | **Create** | Generate a new image from intent + tradition guidance, optionally in structured layers. | — | `create_artwork`, `generate_image` |
   | **Brief / Studio** | Turn a creative brief into concept sketches and iterate. | — | `brief_parse`, `generate_concepts` |
   | **Admin** | Let the agent see intermediate artifacts, unload models, archive sessions. | — | `view_image`, `unload_models`, `archive_session`, `sync_data` |

3. **Workflow diagram** (simple ASCII or inline SVG):
   ```
   User intent ─▶ Claude Code (planning) ─▶ Vulca MCP tools ─▶ Image artifacts ─┐
          ▲                                                                    │
          └──────────── visible via view_image ◀───────────────────────────────┘
   ```

4. **Roadmap** — transparent, no-promise:
   - Next skill: `/evaluate` (reactivates the EMNLP anchor for agent-driven cultural scoring)
   - Then: `/inpaint` (region-level edit), `/layered-create` (structured generation)
   - Community-driven beyond that — file an issue with your workflow

#### Bottom zone (~30% of length) — receipts & deep links

1. **Research lineage** — EMNLP 2025 Findings, VULCA-Bench, citations (bibtex). Keep existing content, move here.
2. **CLI / SDK cheat sheet** in `<details>` — shortened from current, link full reference to `docs/cli-reference.md` if/when it exists
3. **Architecture** in `<details>` — keep the current ASCII diagram
4. **13 cultural traditions table** — one compact section
5. **MPS / Apple Silicon quickstart** — tight `pip install` + link to `docs/apple-silicon-mps-comfyui-guide.md` (protect the #2 SEO referrer)
6. **Social proof strip** — 2 before/after pairs from `assets/demo/v2/masters/`: (a) Mona Lisa → `face_and_hair.png` + `body_and_dress.png`, (b) Qi Baishi Shrimp → `ink_shrimp.png` + `ink_calligraphy.png` + `red_seals.png`. Caption: *These layer separations were produced by Claude Code driving Vulca MCP tools via `/decompose`.* Chosen over the 2026-04-18 XHS celebrity carousels to avoid attention-magnet distraction (Codex review flag) and to stay fully public-domain.
7. **License / Support / Versioning** — footer

### GitHub About + topics (same PR)

**Description (replaces current):**
> *Agent-native image-editing SDK for Claude Code. 21 MCP tools + /decompose skill — semantic layer splits, L1–L5 cultural scoring, region inpaint. Powered by ComfyUI, Gemini, or mock.*

**Topics — add:** `agent-native`, `claude-code`, `anthropic`, `claude-mcp`
**Topics — keep:** `ai`, `art`, `comfyui`, `cultural`, `mcp`, `python`, `sdk`, `evaluation`, `vlm`, `multi-agent`
**Topics — drop (rot candidates):** `creative-ai`, `cultural-evaluation`, `pipeline` (low-intent generic, not how visitors search)
**Net:** 13 current → 14 after (10 keep + 4 add; GitHub allows 20)

### CTA ladder (option y, locked)

1. Try `/decompose` (primary) — link jumps to the Claude Code 60-second upstart block
2. `pip install vulca` (secondary) — for non-agent SDK users
3. Star the repo (tertiary) — bottom-zone footer, no hero pressure
4. Read `docs/agent-native-workflow.md` (deep-dive) — linked from the capability map

### UTM tagging

Add `?utm_source=github-readme&utm_medium=oss&utm_campaign=refresh-2026-04-20` to **every non-github.com link** in the main README.md (research paper URLs, astral/uv docs, external dashboards, etc.).

Do NOT add UTM to:
- Repo-local links (relative paths like `docs/agent-native-workflow.md`)
- `https://github.com/vulca-org/...` URLs (GitHub traffic API attributes natively)
- `https://pypi.org/project/vulca/` (PyPI badge target)

Verification: `grep -E 'https?://(?!github.com/vulca-org|pypi.org/project/vulca)' README.md` — every match must contain `utm_source=github-readme`.

### Rollback criterion

Schedule traffic review for **2026-05-04** (14 days post-merge) via `CronCreate`. Criteria vs. pre-refresh 14d baseline of 82 views:
- **≥ 130 views** → refresh successful, keep iterating forward
- **80–130 views** → content audit, adjust non-hero sections
- **< 80 views** → revert hero, retain cluster map and Claude Code setup sections (those are pure improvements regardless of positioning)

Logging the result as a project memory file is **out of scope** for this spec (addresses Codex scope-creep flag) — handle in the follow-up review session.

---

## Implementation order

1. **Phase 1 PR** in `vulca-org/vulca-plugin` — plugin sync (see Phase 1 changes above). Tag `v0.16.1` and publish.
2. **Verify** clean-install test from the verification list.
3. **Phase 2 PR** in `vulca-org/vulca` — README + About + topics. UTM links added. Points at the now-working plugin.
4. **Schedule reminder** for 2026-05-04 traffic review (can be a simple calendar note or CronCreate).

Phase 2 must not merge before Phase 1's clean-install test passes.

---

## Acceptance criteria (whole project)

### Phase 1

See the **Phase 1 acceptance criteria** checklist in the Phase 1 section above (9 items, all grep- or SHA-verifiable).

### Phase 2 (each criterion falsifiable)

- [ ] Main-repo `README.md` file length between 400 and 520 lines (target ~450 ±10%)
- [ ] Hero paragraph is a byte-exact match to the locked hero string in the Hero section of this spec
- [ ] Agent transcript block appears before line 150 of `README.md` AND before any Markdown image tag (`<img>` or `![...](...)`)
- [ ] Setup dual-path block (Path A + Path B) appears AFTER the agent transcript block but still in the top zone
- [ ] Every cluster row in the capability map's "What your agent delegates to Vulca" column begins with a verb and contains zero MCP tool names (tool names live only in the Tools column)
- [ ] The four v2 GIF basenames `vhs-create.gif`, `vhs-layers.gif`, `vhs-studio.gif`, `vhs-tools.gif` do not appear in `README.md` (grep-verifiable; files remain on disk)
- [ ] Bottom-zone social proof strip contains ≥2 before/after image pairs from `assets/demo/v2/masters/` and zero images of living or recognizable public figures
- [ ] `docs/apple-silicon-mps-comfyui-guide.md` is linked from the main README (protects SEO #2 referrer)
- [ ] `grep -E 'https?://(?!github.com/vulca-org|pypi.org/project/vulca)' README.md` returns zero matches that lack `utm_source=github-readme`
- [ ] GitHub About description is byte-exact match to the "Description (replaces current)" string in the About section of this spec
- [ ] GitHub topics list equals the 14-topic final set (10 keep + 4 add) specified in this spec — no more, no less
- [ ] A `CronCreate` trigger is registered to fire on 2026-05-04 with a prompt to check traffic against the rollback thresholds

---

## Open questions / risks

Resolved inline during spec self-review and final parallel review:
- ~~cultural-critic audit~~ → delete (Phase 1 source section, item 6)
- ~~social proof licensing~~ → public-domain masters (Phase 2 bottom-zone section, item 6)
- ~~"one additional public-domain masterwork"~~ → reduced to 2 named pairs (Mona Lisa + Qi Baishi)
- ~~badge dynamic vs hardcoded~~ → hardcoded `21` + release checklist reminder
- ~~traffic review reminder form~~ → `CronCreate` trigger
- ~~Path B skill-copy handwave~~ → explicit `mkdir -p` + `curl -o` command

Still open at spec-to-plan handoff:

1. **EMNLP URL returns HTTP 301** on `https://aclanthology.org/2025.findings-emnlp/`. During Phase 2 implementation, resolve the redirect (via `curl -Ls -o /dev/null -w '%{url_effective}' ...`) to the stable per-paper URL; update all four occurrences in the main README. If redirect target is unstable, cite the arXiv version instead.

2. **`vulca[all]` extra mismatch** — `pyproject.toml` line 99 references `vulca[layers,tools,mcp,scout]` but the extras section defines only `tools`, `mcp`, `layers-full`. `layers` and `scout` may not exist. Out of scope for this spec; file a follow-up issue before the next SDK release to avoid `vulca[all]` install failures.

3. **Plugin release cadence automation** — after this sync, every SDK release needs a matching plugin sync to avoid recurrence of the 13-day drift. Out of scope; file a follow-up issue proposing `scripts/sync_plugin.py` (regenerates plugin tool table + version from SDK truth) gated behind the `release_checklist` memory.

---

## References

- Current README: `<vulca-repo-root>/README.md`
- Decompose skill: `<vulca-repo-root>/.claude/skills/decompose/SKILL.md`
- MCP server: `<vulca-repo-root>/src/vulca/mcp_server.py` (21 `@mcp.tool()` decorators)
- Plugin repo: https://github.com/vulca-org/vulca-plugin (v0.9.0, 13 days stale)
- Traffic baseline memory: `memory/project_traffic_baseline_20260413.md`
- README-refresh-pending memory: `memory/project_readme_refresh_pending.md` (supersede after Phase 2 merges)
- Phase 1 complete memory: `memory/project_phase1_complete.md`
- Agent-native pivot memory: `memory/project_agent_native_pivot.md`
- XHS style experiments memory: `memory/project_xhs_style_experiments.md`
