---
name: visual-plan
description: "Turn a resolved design.md (from /visual-spec) into reviewable plan.md + run generate+evaluate loop → status {completed, partial, aborted}. Triggers: /visual-plan, '视觉 plan', '设计 execute'. Requires design.md status: resolved + Vulca checkout."
---

You are running `/visual-plan` — the third meta-skill in the `brainstorm → spec → plan → execute` pipeline. Your job: read a `design.md` at `docs/visual-specs/<slug>/` (produced by `/visual-spec` with `status: resolved`), derive a reviewable `plan.md` draft, walk the user through plan review, execute the generate+evaluate loop against the provider specified by `design.A.provider`, and finalize with terminal status + handoff string.

**In scope:** any `design.md` with `status: resolved` and `tradition` in the registry (or literal `null`), inside a Vulca checkout (`src/vulca/` present at cwd).
**Out of scope:** producing pixels outside Phase 3 (Err #8); multi-slug batch runs; modifying `design.md` (`/visual-plan` NEVER writes to `design.md` — S4 invariant).

**Tone:** decisive plan derivation + collaborative review gate + disciplined execution with per-iter audit.

## Phase 1 — Precondition gate + derivation + plan.md draft write

Runs before anything else. No turn cap charged. Early-exit on any Err; SKILL.md §6 error matrix governs.

0. **Vulca-sentinel precondition.** Assert `Path("src/vulca").is_dir()` at cwd. Failure → Err #14.
1. **Resolve slug + paths.** From positional arg, compute:
   - `design_path = docs/visual-specs/<slug>/design.md`
   - `plan_path = docs/visual-specs/<slug>/plan.md`
   - `jsonl_path = docs/visual-specs/<slug>/plan.md.results.jsonl`
   - `lock_path = docs/visual-specs/<slug>/plan.md.lock`
   - `iters_dir = docs/visual-specs/<slug>/iters/`
2. **Read design.md.** Missing file → Err #1. Parse frontmatter. `status != resolved` → Err #1.
3. **Check same-slug plan.md collision.**
   - Terminal status (`completed` / `partial` / `aborted`) → Err #2 refuse-overwrite.
   - `status: draft` → Err #3 resume path. **If a stale lockfile also exists, fold Err #12 side-effects (unlink + `[stale-lock-recovery]` Notes line + Phase 4 handoff suffix) into the resume path.**
4. **Check lockfile** (skip if step 3 folded it):
   - Exists + jsonl fresh (< 300s mtime) OR lockfile `started_at` < 300s + no jsonl → Err #11 concurrent.
   - Exists + stale (jsonl > 300s OR lockfile.started_at > 300s + no jsonl) → Err #12 auto-recover: `os.unlink(lockfile)`, append Notes `[stale-lock-recovery]` line, continue.
5. **Validate schema_version.** `design.frontmatter.schema_version` in supported set `{"0.1"}`. Absent → treat as `"0.1"` (back-compat). Unrecognized → Err #15.
6. **Validate tradition.** `list_traditions()`. `frontmatter.tradition` ∈ `traditions.keys()` OR literal YAML null. Violation → Err #4.
7. **Validate domain.** `frontmatter.domain` ∈ `{poster, illustration, packaging, brand_visual, editorial_cover, photography_brief, hero_visual_for_ui}`. Violation → Err #4.
8. **Parse 7 fenced-YAML dim blocks** (A/B/C/D1/D2/E/F) per tolerant-read rules below. Required section missing → Err #10. **E section is optional** (fires only when `design.## Open questions` requested a spike); D1 is optional iff `tradition: null`; A/B/C/D2/F are always required.

### Fenced-YAML parser — tolerant read (Phase 1 step 8)

Extract fenced ```` ```yaml ... ``` ```` blocks under `## A.` / `## B.` / `## C.` / `## D1.` / `## D2.` / `## E.` / `## F.` headings. Parse via `yaml.safe_load` with `allow_duplicate_keys=False` (PyYAML strict default).

**Accept-with-normalization**:
1. **Unknown top-level keys** inside a dim block → ignore + log to plan.md Notes: `[parser-warn] <section>.<key>: unknown key dropped`.
2. **Missing required key** (e.g. `A.seed`) → fill from schema default + log: `[parser-default] <section>.<key> missed; filled with <default>`.
3. **Inline `# comments`** inside fences → allowed on read; stripped on write.
4. **Unknown `##` section headings** outside `A/B/C/D1/D2/E/F/Open questions/Notes` → ignore silently (no warning).
5. **`C.tradition_tokens` as flat string list** OR **list[dict]** with `{term, translation, definition?}` → normalize to flat strings `f"{term} {translation}"`.
6. **`A.provider` as bare `sdxl`** → on darwin normalize to `sdxl-mps`, elsewhere `sdxl-cuda`; log `[parser-normalize] A.provider: sdxl → sdxl-mps`.
7. **`D2.L_N_threshold` / `F.*` as bare number** `0.7` → wrap to `{value: 0.7, source: assumed, confidence: low}`.

**Hard-reject** → Err #1, #4, #10, #15 per §6. Any `design.md parse-fail` (dup keys / fence syntax / required section absent) → Err #10.

9. **Sketch readability probe.** If `design.C.sketch_integration != "ignore"` and sketch path in `design.## References`: `Read(sketch_path)`. Failure → Err #9 (internal `sketch_available: false`; override `plan.C.sketch_integration: ignore`; queue Notes entry).
10. **Freeze session constants.** Capture `{tradition, domain, slug}` + `design_hash = sha256(design.md bytes)` for S4 content-guard (Phase 3 per-iter re-asserts).
11. **Derive plan.**
    - `seed_list`: start from `design.A.seed`, step +1 for `design.B.variant_count` items. If `design.## Open questions` has `- seeds: [<list>]` explicit override → prefer.
    - `gating_decisions`: per D2 L_N: `gate_class = hard` if source ∈ `{measured, derived}`, else `soft`. Initial `user_elevated: []`.
    - `composed_prompts`: per variant, assemble `{base_prompt} + ", " + {tradition_tokens joined} + ", " + {color_constraint_tokens joined}` + `negative_prompt` as separate kwarg. One composed string per iter.
    - `fail_fast_budget`: copy `F.fail_fast_consecutive`; if `None`, fail-fast disabled.
    - `rollback_plan`: copy `D2.rollback_trigger`; derive `rollback_action` default `partial` (user overrideable in Phase 2).
    - `F.initial_budget`: copy `design.F` verbatim.
12. **Create lockfile** via `open(lock_path, O_CREAT | O_EXCL | O_WRONLY)` with JSON `{pid: os.getpid(), started_at_iso: now(), design_ref: <path>}`. Precedent: `src/vulca/digestion/dream.py:46-80`.
13. **Write plan.md** with `status: draft` + derived body (schema per §4.2 below). Turn cost: zero.

### plan.md canonical schema (strict write)

**Frontmatter — exactly 9 fields, no comments inside `---` fence, deterministic order:**
```yaml
---
slug: <copied from design.md>
status: draft | running | completed | partial | aborted
domain: <copied, S4 immutable>
tradition: <copied, S4 immutable>
schema_version: "0.1"              # back-compat: absent in source → treated as "0.1"
generated_by: visual-plan@0.1.0
design_ref: docs/visual-specs/<slug>/design.md
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Body — exactly 10 sections, fixed order, every section present (empty uses `none`):**

```
# <human-readable title, mirror design.md>
## A. Execution parameters         — fenced YAML from design.A (MCP-extended)
## B. Iteration plan               — fenced YAML: strategy, variation_axis, seed_list, variant_count, batch_size
## C. Prompt composition           — fenced YAML: composed prompts per variant
## D. Gating decisions             — fenced YAML: per L_N {value, source, gate_class}, user_elevated, soft_gate_warn_count
## E. Fail-fast budget + rollback  — fenced YAML: fail_fast_consecutive, rollback_trigger, rollback_action
## F. Cost ledger                  — fenced YAML: initial_budget, actual (from jsonl), overage_pct
## Results                         — markdown table rendered from jsonl at Phase 4
## Notes                           — free-form audit lines
```

Notes convention lines (when relevant): `[parser-default]` / `[parser-warn]` / `[parser-normalize]` / `[override]` / `[resume-state]` / `[fail-fast]` / `[stale-lock-recovery]` / `[review-required]` / `[unload-models]` / `[evaluate-suspect]` / `[design-drift]` / `[failover-cross-class]`.

## Phase 2 — Plan-review loop

(filled in Task 6)

## Phase 3 — Execution loop

(filled in Task 6)

## Phase 4 — Finalize + optional hygiene

(filled in Task 6)

## Invariants (S1-S7)

| # | Rule | Enforce class |
|---|---|---|
| **S1** | Pixel-tool ban baseline. Exemptions: (a) Phase 3 execution authorizes ONLY `generate_image`, `evaluate_artwork`, MAY `unload_models`; (b) no other phase uses pixel tools. Forbidden across EVERY phase (no exemption): `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*`. | prescription |
| **S2** | Do not flip `frontmatter.status` without explicit user trigger: `draft → running` requires `accept all`; `running → terminal` requires a terminal condition (all iters done, fail_fast, user-abort, Err #13). Cap-hit alone is NOT a trigger. | prescription |
| **S3** | Only consume `design.md` with `status: resolved`. Reject anything else via Err #1. | helper |
| **S4** | `frontmatter.{tradition, domain, slug}` are **immutable** across the session (captured at Phase 1, asserted at Phase 4). `A.provider` is **EXPLICITLY MUTABLE** via user-approved Err #13 cross-class failover only — any mutation outside Err #13 is an S4 violation. Additionally, `design.md` file bytes are content-hash-guarded: Phase 1 captures `sha256(design.md)` into session `design_hash`; Phase 3 re-hashes per iter; drift → Err #16 abort. | helper |
| **S5** | Concurrency control via `plan.md.lock` (`O_CREAT\|O_EXCL` with `{pid, started_at_iso, design_ref}` JSON). Staleness judged by jsonl mtime (when present) OR lockfile `started_at` (when no jsonl), both compared to 300s threshold. Stale → auto-recover per Err #12. Fresh → refuse per Err #11. | helper |
| **S6** | `plan.md.results.jsonl` is append-only during Phase 3. One row per completed iter (success OR failed OR skipped-via-failover). No rewrites; sequential append in `iter_idx` order. | helper |
| **S7** | `plan.md` is a render artifact only. Phase 3 does NOT rewrite `plan.md` mid-loop (all per-iter progress goes to jsonl). Phase 4 finalize reads jsonl → renders `## Results` → atomic `os.rename(.jsonl → .jsonl.archive)` → Write terminal plan.md. | prescription + helper |

## Error matrix (16 rows — grep contract)

All `Print exactly:` strings are backtick-wrapped for downstream grep compatibility. Full-prose version in `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md` §6.

| # | Signal | Response |
|---|---|---|
| Err #1 | `design.md` not found OR `status != resolved` | Print exactly: `design.md not found or status != resolved at <path>. Run /visual-spec <slug> first.` Terminate. |
| Err #2 | Same-slug `plan.md` exists with terminal status (`completed` / `partial` / `aborted`) | Print exactly: `already <status> at <path>; branch with -v2 or pick new slug`. Terminate. **Do not overwrite.** |
| Err #3 | Same-slug `plan.md` `status: draft` (with or without jsonl) | Resume Phase 2: re-enter review loop, skip sections with `reviewed: true`, accumulate turns_used from Notes `[resume-state]` line. If jsonl present → Phase 3 entry replays completed iters. **If a stale lockfile also exists, fold Err #12 side-effects into this resume path; only one recovery Notes line total.** |
| Err #4 | design.md frontmatter violation (`tradition` not in registry and not YAML null; OR `domain` not in 7-enum) | Print exactly: `design.md frontmatter violation: <field> <value> invalid. Re-run /visual-spec <slug> to fix.` Terminate. **Do not auto-retry.** |
| Err #5 | Phase 3 provider unreachable (connection refused / missing key / timeout) | **No auto-failover.** Append `[failover-needed] <provider> unreachable: <err>` to Notes. Advance directly to Err #13 user prompt. |
| Err #6 | `generate_image` returns error dict (validation / OOM / malformed param) | jsonl row: `verdict: failed, error: <excerpt>`. Continue next iter. All-fail → terminal `partial`. |
| Err #7 | Phase 3 `fail_fast_counter >= F.fail_fast_consecutive.value` (applies only when `F.fail_fast_consecutive is not None`) | Force-show current draft + print exactly: `cost budget exceeded (<consecutive>×over). Abort, extend budget, or accept remaining?` (a) abort → `aborted`; (b) extend → reset; (c) accept-remaining → `partial`. **Never auto-extend.** |
| Err #8 | User requests pixel action in Phase 1/2/4 (`generate now`, `skip review`) | Print exactly: `plan layer executes pixels in Phase 3 only. Complete review (accept all) first, or change spec via /visual-spec <slug>.` Do NOT invoke tool. **Turn NOT charged.** |
| Err #9 | design.md `## References` sketch unreadable at Phase 1 probe | Set `sketch_available: false`; override `plan.C.sketch_integration: ignore`. Notes: `sketch at <path> unreadable at plan time: <err>. Proceeding text-only; C.sketch_integration forced to "ignore".` **Do not abort.** |
| Err #10 | design.md YAML parse-fail (required section missing / dup keys / fence syntax) | Print exactly: `design.md parse-fail at <slug>: <issue>. Re-run /visual-spec <slug> to regenerate.` Terminate. **Do not auto-retry.** |
| Err #11 | Same-slug concurrent /visual-plan (lockfile exists + jsonl mtime < 300s OR lockfile.started_at < 300s + no jsonl) | Print exactly: `<slug> currently running (pid: <pid>, started: <iso>). Abort the other session first, or wait and retry.` Terminate. **Do not kill other pid.** |
| Err #12 | Stale lockfile (lockfile exists + jsonl mtime > 300s OR lockfile.started_at > 300s + no jsonl) | Auto-recover silently: `os.unlink(lockfile)`. Append to Notes: `[stale-lock-recovery] previous pid <N> abandoned at <iso>; reclaimed at <now>. Resuming from iter <K>.` Handoff string at Phase 4 appends ` (recovered from stale lock at iter <K>)`. **No user prompt; no stderr print.** |
| Err #13 | Phase 3 provider unreachable AND failover requires cross-class switch (local ↔ cloud) | Print exactly: `<current> unreachable, failover to <alt> requires cross-class switch (local→cloud or reverse). Approve? (a) yes / (b) no, abort / (c) no, skip remaining iters as partial`. **Prompt user. Turn NOT charged.** |
| Err #14 | `Path("src/vulca").is_dir()` false (not inside Vulca checkout) | Print exactly: `not inside a Vulca checkout; /visual-plan requires repo presence at cwd. cd into your vulca repo and retry.` Terminate. |
| Err #15 | `design.frontmatter.schema_version` present AND not in supported set `{"0.1"}` | Print exactly: `design.md schema_version <got> not recognized; upgrade /visual-spec (pip install --upgrade vulca) or pin vulca@<compatible>.` Terminate. **Do not auto-retry.** |
| Err #16 | Phase 3 per-iter hash guard detects `design.md` bytes changed since Phase 1 capture | Print exactly: `design.md mutated mid-session at iter <K>; aborting. Re-run /visual-plan <slug> to restart with new design.` Abort immediately. Status → `aborted`. jsonl through iter `<K-1>` preserved. Notes: `[design-drift] design.md sha256 changed between Phase 1 and iter <K>; aborting.` |

## References

- Design spec: `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md`
- Sibling skills: `.claude/skills/visual-brainstorm/SKILL.md` (v0.17.4), `.claude/skills/visual-spec/SKILL.md` (v0.17.5)
