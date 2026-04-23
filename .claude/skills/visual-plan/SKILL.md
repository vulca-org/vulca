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

## Source-gating decisions (consumed by Phase 2 + 3)

For each design.md numeric threshold `{value, source, confidence}`, Phase 1 derivation maps to `gate_class`:

| design.md field | source value | plan.md `gate_class` | Phase 3 behavior |
|---|---|---|---|
| `D2.L_N_threshold` | `measured` | **hard** | score < value → `reject` verdict, fail_fast_counter++ |
| `D2.L_N_threshold` | `derived` | **hard** | same as measured (calibration-anchored, trusted) |
| `D2.L_N_threshold` | `assumed` | **soft** | score < value → `accept-with-warning`, log `[review-required]` to Notes, soft_gate_warn_count++, counter unchanged |
| `D2.L_N_threshold` | `user-confirmed` (post-elevation via Phase 2 change) | **hard** | same as measured; only possible after Phase 2 `change D.L_N` subcommand |
| `F.per_gen_sec` | `measured` / `derived` | **hard-budget** | enforced by Err #7 fail_fast counter |
| `F.per_gen_sec` | `assumed` | **Phase 2 F-summary prompt decides** | reply (a) → hard-budget continues + `user_ack_assumed_budget: true`; (b) → updates value, source=user-confirmed, hard-budget; (c) → disables Err #7 via `fail_fast_consecutive = None` |
| `F.fail_fast_consecutive` | any source | **hard-counter** | value applies regardless of source once F-summary resolved |
| `D1.L_N` weight | (no source triple) | **registry-authority** | weighted_total multiplier only; not itself a gate |

**Critical invariant**: when Phase 2 `change D.L_N` elevates a threshold from assumed → user-confirmed, `user_elevated` list in plan.md tracks the change + `gate_class: soft → hard` + `[override]` Notes line logged. **`user_elevated` persists ONLY in plan.md — never back-written to design.md. design.md is immutable post-resolved per /visual-spec S4 contract.**

### Phase 3 verdict tree

```python
# Sentinel: all-zero scores indicate evaluator failure masquerading as pass.
# Without this guard, a broken evaluate_artwork silently greenlights every iter.
# Threshold is <0.01 (not ==0.0) to catch float-representation noise from evaluators
# that emit 1e-7 rather than exact zero. Legitimate single-L outliers at 0.008 do NOT
# trigger — sentinel requires ALL FIVE dims simultaneously below 0.01.
if all(l_scores[k] < 0.01 for k in ("L1", "L2", "L3", "L4", "L5")):
    _append_notes(f"[evaluate-suspect] iter {iter}: all L_N scores < 0.01; flagged for review")
    return "accept-with-warning"

hard_fails = [L_N for L_N in L1..L5 if gate_class=hard AND score < value]
soft_fails = [L_N for L_N in L1..L5 if gate_class=soft AND score < value]
budget_overage = (F.fail_fast_consecutive is not None AND wall_time > F.per_gen_sec.value * 2)

if hard_fails: return "reject"
if soft_fails or budget_overage: return "accept-with-warning"   # NOT reject, counter unchanged
return "accept"                                                   # fail_fast_counter → 0
```

### Phase 2 F-summary prompt (fires before main draft prompt; NOT charged toward 5-turn cap)

triggered when any of `F.per_gen_sec / F.total_session_sec` has `source == "assumed"`. Print exactly:

```
F budget is assumed: per_gen_sec ~<X>s × <N> iters × 1.5 margin = ~<Y>s total.
This is derived from mock calibration + provider multiplier; not measured on your hardware.
Reply:
  (a) accept this budget as-is
  (b) override <per_gen_sec_seconds>
  (c) skip-budget-check (disables Err #7 cost enforcement)
```

Reply handling:
- `(a)` / `a` / `accept` → set `F.user_ack_assumed_budget: true`; F stays assumed; fail_fast still active.
- `(b) <N>` / `override <N>` → `F.per_gen_sec = {value: N, source: user-confirmed, confidence: high}`; recompute `F.total_session_sec`; fail_fast active with new baseline.
- `(c)` / `skip` / `skip-budget-check` → `F.fail_fast_consecutive = None`; Err #7 disabled; log Notes `[budget-skipped] user opted out of per-gen latency enforcement`.
- Invalid first time → re-prompt once.
- Invalid second time → default to `(a)` + log `[budget-assumed-default] invalid reply treated as accept`.

## Phase 2 — Plan-review loop

(filled in Task 6)

## Phase 3 — Execution loop

Runs only after Phase 2 user types `accept all` and status flips `draft → running`. No review cap. Sequential iteration over `seed_list`. Lockfile heartbeat = jsonl mtime (no separate heartbeat file).

**S2 cross-phase reminder**: Phase 2 cap-hit without `accept all` force-shows the full draft and prompts `Turn cap reached. finalize or deep review?` — status STAYS `draft`; cap-hit alone never enters Phase 3 (see Phase 2 body).

**S1 enforcement**: Phase 3 tool whitelist = `generate_image` + `evaluate_artwork` + MAY `unload_models` at loop end. Forbidden across all phases: `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*`.

```python
fail_fast_counter = 0
completed_iters = _replay_jsonl_if_exists()   # Err #3 resume or Err #12 recovery
soft_gate_warn_count = 0

for iter_idx, seed in enumerate(seed_list):
    if iter_idx < len(completed_iters):
        # Resume: rebuild fail_fast_counter from last contiguous reject-run
        fail_fast_counter = _rebuild_counter(completed_iters)
        soft_gate_warn_count = _rebuild_soft_count(completed_iters)
        continue

    # S4 content-guard: re-hash design.md and compare to captured session constant
    current_hash = _sha256(Path(design_ref).read_bytes())
    if current_hash != design_hash:
        _terminate_phase3(status="aborted", at_iter=iter_idx, reason="err16")
        return  # Err #16 fires

    variant = _variant_for_iter(iter_idx, plan.B)
    composed_prompt = plan.C.composed_prompts[variant.idx]
    t0 = perf_counter()
    started_at = now_iso()

    try:
        gen_result = await generate_image(
            prompt=composed_prompt,
            provider=plan.A.provider,
            tradition=design.frontmatter.tradition,
            reference_path=plan.A.reference_path if plan.C.sketch_integration != "ignore" else "",
            output_dir=f"docs/visual-specs/{slug}/iters/{seed}/",
            seed=plan.A.seed + iter_idx,          # MCP-extended (v0.17.6 prereq)
            steps=plan.A.steps,                    # MCP-extended
            cfg_scale=plan.A.cfg_scale,            # MCP-extended
            negative_prompt=plan.A.negative_prompt, # MCP-extended
        )
    except ProviderUnreachable as e:
        # Err #5 hands off directly to Err #13 cross-class user prompt (no S8 auto-failover)
        user_choice = prompt_err13(e, plan.A.provider)
        if user_choice == "a":
            plan.A.provider = _alt_class_provider(plan.A.provider)
            _log_failover_notes(plan.A.provider)
            continue
        elif user_choice == "b":
            _terminate_phase3(status="aborted", at_iter=iter_idx); return
        elif user_choice == "c":
            _terminate_phase3(status="partial", at_iter=iter_idx); return

    wall_time = perf_counter() - t0

    if "error" in gen_result:
        # Err #6: per-iter failure, log + continue
        _append_jsonl_row(iter_idx, seed, verdict="failed",
                          error=gen_result["error"], ...)
        continue

    eval_result = await evaluate_artwork(
        image_path=gen_result["image_path"],
        tradition=design.frontmatter.tradition,
    )
    # evaluate_artwork returns {"score": float, "dimensions": {...}, "tradition": str}.
    # Map the 5 L scores out of the dimensions dict (keys are rubric names per tradition).
    # On missing / malformed dimensions → jsonl row verdict=failed with error=<excerpt>, continue.
    l_scores = _extract_l_scores(eval_result)
    weighted_total = sum(l_scores[k] * plan.D1[k] for k in ("L1", "L2", "L3", "L4", "L5"))

    verdict, gate_decisions = _compute_verdict(l_scores, plan.D.gating_decisions,
                                                plan.F, wall_time)

    _append_jsonl_row(iter_idx, seed, variant, gen_result["image_path"],
                     started_at, wall_time, plan.A.provider,
                     l_scores, weighted_total, verdict, gate_decisions,
                     composed_prompt)

    if verdict == "reject":
        fail_fast_counter += 1
    elif verdict == "accept":
        fail_fast_counter = 0   # accept resets counter to 0
    elif verdict == "accept-with-warning":
        soft_gate_warn_count += 1
        # fail_fast_counter unchanged — soft never contributes

    # Err #7: unified 3-option prompt (no F.source branching)
    if (plan.F.fail_fast_consecutive is not None
        and fail_fast_counter >= plan.F.fail_fast_consecutive.value):
        # force-show plan; print exactly: cost budget exceeded (<consecutive>×over). Abort, extend budget, or accept remaining?
        user_choice = prompt_err7()
        if user_choice == "abort":
            _terminate_phase3(status="aborted", at_iter=iter_idx); return
        elif user_choice.startswith("extend"):
            plan.F.fail_fast_consecutive.value = _parse_extend(user_choice)
            fail_fast_counter = 0  # reset on extend
        elif user_choice == "accept-remaining":
            _terminate_phase3(status="partial", at_iter=iter_idx); return
```

### plan.md.results.jsonl — row schema (14 required fields + 2 optional)

```json
{
  "iter": 3,
  "seed": 1340,
  "variant_idx": 2,
  "variant_name": "season=summer",
  "image_path": "docs/visual-specs/<slug>/iters/1340/gen_abc12345.png",
  "started_at": "2026-04-23T14:05:12Z",
  "wall_time_sec": 82.34,
  "provider_used": "sdxl-mps",
  "l_scores": {"L1": 0.78, "L2": 0.72, "L3": 0.58, "L4": 0.61, "L5": 0.49},
  "weighted_total": 0.651,
  "verdict": "accept-with-warning",
  "gate_decisions": {"hard_fails": [], "soft_fails": [["L3", 0.58, 0.6]], "budget_overage": false},
  "prompt_used": "..."
}
```

Schema rules:
- UTF-8, NDJSON (newline-delimited JSON), one row per line.
- Serialize: `json.dumps(..., ensure_ascii=True, separators=(",", ":"))` — grep-safe (CJK escapes to `\uXXXX`).
- Always terminate with `"\n"`; read: `[json.loads(l) for l in content.splitlines() if l.strip()]` (tolerant of torn last line from crash).
- 14 required fields above; 2 optional: `error` (on `verdict: failed` rows) and `evaluate_artwork_raw` (full tool return; off by default).
- `iter` strictly monotonic increasing by 1 per append (natural from sequential Phase 3).
- **append-only** — a crash between row N-1 and row N leaves exactly N-1 rows on disk, not N+partial.

### Phase 3 tool whitelist reminder

- `generate_image` (MCP-extended v0.17.6 signature)
- `evaluate_artwork`
- MAY `unload_models` at loop end (optional memory hygiene; log Notes `[unload-models] freeing <provider> weights` when called).

**S1 absolute ban** (any phase): `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*`. User request for any of these → Err #8 decline, turn NOT charged.

## Phase 4 — Finalize + optional hygiene

1. Read `plan.md.results.jsonl` → all completed rows.
2. Determine terminal status (priority order: `aborted` > `partial` > `completed`):
   - **`aborted`** triggers: user-triggered abort, Err #13(b) user picked "no, abort", Err #7 user picked "abort", Err #16 design.md drift detected mid-Phase-3.
   - **`partial`** triggers: Err #7 user picked "accept-remaining", Err #13(c) user picked "skip as partial", all iters completed but zero had verdict ∈ {accept, accept-with-warning} (every row `verdict: failed` via Err #6). Mixed rows where at least one is `accept`/`accept-with-warning` fall through to `completed` with `[iter-failures]` Notes line.
   - **`completed`** trigger: all iters in seed_list completed AND at least one verdict ∈ {accept, accept-with-warning}. Soft warnings affect handoff variant selection but do NOT demote to partial.
   - **Zero-rows corner case**: if Err #16 / user abort fires at iter 0 before any jsonl row appended → fall-through to `aborted`.
3. Render `## Results` markdown table from jsonl rows (columns: `iter | seed | variant | image | L1-L5 | weighted | verdict | wall_time | provider | notes`).
4. Populate `## F. Cost ledger` actual: `total_wall_time` sum from jsonl, `overage_pct = actual / initial_budget - 1`.
5. Append terminal-state Notes lines (`[fail-fast]`, `[aborted-at-iter]`, etc.).
6. Rename `plan.md.results.jsonl` → `plan.md.results.jsonl.archive` (atomic on same filesystem).
7. Delete `plan.md.lock` via `os.unlink`.
8. MAY call `unload_models()` on `plan.A.provider`'s weight family for post-session cleanup. Log Notes if called.
9. Write final `plan.md` with `status: <terminal>`, `updated: <today>`.
10. Assert S4: `plan.frontmatter.{tradition, domain, slug}` == captured values. Violation → raise (code bug).
11. Determine handoff string variant (8 variants total — see §Handoff below); append ` (recovered from stale lock at iter <K>)` suffix if Phase 1 fired Err #12 or folded via Err #3.
12. Print handoff string byte-identical.

**Do NOT auto-invoke anything downstream.** /visual-plan is terminal.

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
