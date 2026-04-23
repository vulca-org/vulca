# `/visual-plan` Skill — Design Spec

**Date:** 2026-04-23
**Status:** Design locked after brainstorm session (5 clarifying Q's Q1-Q5 + 5 design-section acks S1-S5 + mid-checkpoint parallel review round → 6 mandatory revisions) + post-write parallel review round (codex + superpowers → 5 BLOCKER + 7 SHOULD-FIX + 2 MS folded into this v2 spec).
**Parent siblings:** [`2026-04-21-visual-brainstorm-skill-design.md`](./2026-04-21-visual-brainstorm-skill-design.md) (shipped v0.17.4) + [`2026-04-21-visual-spec-skill-design.md`](./2026-04-21-visual-spec-skill-design.md) (shipped v0.17.5).
**Follow-up:** implementation plan at `docs/superpowers/plans/2026-04-23-visual-plan-skill.md` (next, via `superpowers:writing-plans`).

This spec is for the **shipped skill artifact** (`.claude/skills/visual-plan/SKILL.md`). Per sibling discipline, the skill file itself will contain zero "future / later / expand" phrasing — deployed artifact is not a roadmap. Y-future thinking lives only in this spec and the follow-up plan doc.

---

## 1. Purpose, scope, positioning

### 1.1 Purpose

`/visual-plan` is the **third and final member** of the 3-layer meta-skill architecture `brainstorm → spec → plan → execute`. It reads a resolved `design.md` (produced by `/visual-spec`) and drives a plan-then-execute loop: derive an auditable `plan.md`, review-gate it with the user, execute the generate+evaluate loop against real provider(s), and finalize with status + audit.

```
/visual-brainstorm  →  /visual-spec  →  /visual-plan  →  (terminal)
  (intent,               (technical       (execution:
   proposal.md)          decisions,        plan.md +
                         design.md)        real pixels)
```

Unlike its two siblings, `/visual-plan` is the **only member that burns real provider budget**. Every architectural choice (review gate before execution, append-only jsonl recovery authority, lockfile concurrency control, soft-gate downgrade on assumed thresholds) serves that single operational reality.

### 1.2 Scope

**In-scope**: any `design.md` at `docs/visual-specs/<slug>/` with `frontmatter.status == resolved` produced by `/visual-spec` at v0.17.5 or later. The skill:
- Parses 7 fenced-YAML dimension blocks (A/B/C/D1/D2/E/F) with tolerant-read discipline.
- Derives a `plan.md` draft (seed allocation, gating classifications, iteration order, fail-fast budget, rollback plan).
- Review-gates with the user (5-turn cap, vocabulary inherited from /visual-spec Phase 4).
- Executes the generate+evaluate loop against the provider specified by `design.A.provider`.
- Appends per-iter results to a crash-safe jsonl sidecar; renders to plan.md at finalize.
- Terminates with one of: `completed` / `partial` / `aborted`.

**Out-of-scope** (hard reject):
- Any `design.md` with `status != resolved` — run `/visual-spec <slug>` first (Err #1).
- `design.md` with `tradition` not in `list_traditions()` registry AND not literal YAML `null` (Err #4).
- `design.md` with `domain` not in 7-enum (Err #4).
- Same-slug `plan.md` already in terminal state (`completed` / `partial` / `aborted`) — Err #2 refuse-overwrite; branch with `-v2` or new slug.
- Concurrent same-slug /visual-plan invocations (Err #11 lockfile collision).
- Not inside a Vulca checkout (Err #14 sentinel).
- Multi-slug batch runs — one invocation, one slug.

### 1.3 Positioning vs sibling skills

| Skill | Input | Output | Side effects | Phase count |
|---|---|---|---|---|
| `/visual-brainstorm` | user intent | `proposal.md status:ready` | file write only | 5 |
| `/visual-spec` | `proposal.md status:ready` | `design.md status:resolved` | file write + 1 mock + optional spike (real) | 6 |
| `/visual-plan` | `design.md status:resolved` | `plan.md status:{completed\|partial\|aborted}` + `iters/<seed>/*.png` on disk | **full execution: N real `generate_image` + N `evaluate_artwork` + optional `unload_models`** | 4 |

`/visual-plan` has **fewer phases** (4 vs sibling 6) for a specific architectural reason:

- `/visual-spec` Phase 2 (F calibration) burns a real `generate_image(provider="mock")` measurement + a user confirmation — it's a *judgment* phase doing live measurement, so it earns its own slot. `/visual-plan`'s equivalent (F-summary prompt) is a *read+prompt on pre-computed F values from `design.md`*, not a new measurement — it folds naturally into Phase 2's review rather than owning a phase.
- `/visual-spec` Phase 3 (dimension derivation) is live judgment across 7 dimensions — seed-vs-steps-vs-cfg tradeoffs, prompt composition from intent + terminology, tradition-specific threshold derivation. It earns a phase. `/visual-plan`'s derivation is *deterministic copy+compose from `design.md`* (seed_list = `A.seed` +1 walk, composed_prompts = concat of C fields) — no judgment, no user turn, so it folds into Phase 1's precondition gate rather than owning a phase.
- Phase 4 collapses finalize + optional `unload_models` hygiene because both are terminal, both non-interactive, and `unload_models` is optional (MAY not SHOULD). `/visual-spec`'s Phase 6 is pure finalize with no hygiene equivalent.

Phases earn their number by having distinct I/O signatures + live-judgment content. This is an honest phase count per mid-checkpoint review, not cargo-culted parity with /visual-spec.

---

## 2. Input / output contracts

**Input** (required):
- `docs/visual-specs/<slug>/design.md` with `frontmatter.status == resolved`.
- Working directory = Vulca repo (assertion `Path("src/vulca").is_dir()` — Err #14 otherwise).

**Input** (optional — per-invocation flags; none carries over between sessions):
- `--dry-run` — run Phase 1-2 only; render draft plan.md to stdout; do NOT write to disk; never flips status. Review-only mode.
- `--resume` — explicit opt-in for Err #3 resume path when same-slug `plan.md status: draft` exists. Default behavior already resumes automatically; flag exists for clarity when the user wants to assert intent.
- `--max-iters <N>` — truncate the Phase 3 seed_list to at most N iterations. Soft cap for experimentation; does NOT modify design.md.

**Output** (per finalize):
- `docs/visual-specs/<slug>/plan.md` with `frontmatter.status ∈ {completed, partial, aborted}`.
- `docs/visual-specs/<slug>/plan.md.results.jsonl.archive` — archived append-only ledger from Phase 3 (renamed from `.jsonl` after finalize render). Machine-only; humans read `plan.md ## Results`.
- `docs/visual-specs/<slug>/iters/<seed>/gen_<hash>.png` — per-iter generated images, one directory per seed.

**Handoff** (byte-identical grep contract — variants selected by final status and trigger source):

| Terminal status + conditions | Handoff string |
|---|---|
| `completed`, zero soft warnings | `Plan /visual-plan/<slug> completed. <N> images at docs/visual-specs/<slug>/iters/.` |
| `completed`, ≥1 soft warning (review-required variant) | `Plan /visual-plan/<slug> completed. <N> images; <K> iters with soft-gate warnings — review ## Results.` |
| `partial` via fail_fast (Err #7) | `Plan /visual-plan/<slug> partial (<N>/<M>). fail_fast triggered at iter <K>. <err excerpt>.` |
| `partial` via Err #7 `accept-remaining` | `Plan /visual-plan/<slug> partial (<N>/<M>). cost budget exceeded; user accepted remaining.` |
| `partial` via Err #13(c) cross-class skip | `Plan /visual-plan/<slug> partial (<N>/<M>). <provider> unreachable; user skipped remaining.` |
| `partial` via all-`failed` verdicts (Err #6) | `Plan /visual-plan/<slug> partial (<N>/<M>). all generate_image calls failed (<err excerpt>).` |
| `aborted` via user interrupt OR Err #13(b) | `Plan /visual-plan/<slug> aborted by user at iter <K>. resume with /visual-plan <slug>.` |
| `aborted` via Err #7 `abort` | `Plan /visual-plan/<slug> aborted at iter <K>. cost budget exceeded.` |

**Error-excerpt convention** (applies to `<err excerpt>` token in any variant): first 80 chars of error message, with `\n` and `` ` `` characters replaced by single spaces. Preserves grep-compat across variants.

**Stale-lock suffix**: any recovery-from-stale-lock session appends ` (recovered from stale lock at iter <K>)` to the chosen variant **before the final period**. Example of completed + stale-recovery:

```
Plan /visual-plan/2026-04-23-gongbi-poster completed. 12 images at docs/visual-specs/2026-04-23-gongbi-poster/iters/ (recovered from stale lock at iter 7).
```

**`--dry-run` mode**: prints no terminal handoff string; stdout is the draft `plan.md` body only. `--dry-run` never reaches Phase 3 or 4, so no terminal status applies.

---

## 3. Architecture

```
USER: /visual-plan <slug> [--dry-run | --resume | --max-iters <N>]
  │
  ▼
Phase 1: Precondition gate + derivation + plan.md draft write
  ├─ Err #14: cwd not inside Vulca checkout → terminate
  ├─ Read design.md; assert status == resolved, tradition ∈ registry ∨ null,
  │    domain ∈ 7-enum, schema_version ∈ supported set, required sections present
  │    (Err #1, #4, #10, #15)
  ├─ Check same-slug plan.md collision:
  │    - terminal status → Err #2 refuse-overwrite
  │    - status: draft → Err #3 resume path (accumulate turns_used; replay jsonl).
  │      If a stale lockfile ALSO exists, fold Err #12 recovery into this path
  │      (unlink lockfile + [stale-lock-recovery] Notes line + handoff suffix).
  ├─ Check lockfile (skipped if Err #3 folded it):
  │    - fresh lockfile + fresh jsonl → Err #11 concurrent, refuse
  │    - stale lockfile → Err #12 auto-recover (delete, log to Notes, continue)
  ├─ Parse 7 fenced-YAML dim blocks tolerant-read (§4.1)
  ├─ Derive seed_list, gating classifications, composed prompts, F values
  ├─ Capture design.md SHA-256 into session-internal design_hash (S4 content guard)
  ├─ Create lockfile `plan.md.lock` via O_CREAT|O_EXCL with {pid, started_at, design_ref}
  ├─ Write plan.md status: draft
  ↓
Phase 2: Plan-review loop (5-turn cap; inherits /visual-spec Phase 4 vocabulary)
  ├─ If any F field source=="assumed": print F-summary prompt (a/b/c reply), NOT capped
  ├─ Print draft + prompt: "Type 'accept all' / 'change <section>' / 'deep review'"
  ├─ Each user reply = 1 turn. At cap: force-show + prompt finalize-or-deep-review.
  ├─ Err #8: user pixel request outside Phase 3 → decline, turn not charged
  ├─ On "accept all" → flip status: draft → running, enter Phase 3
  ↓
Phase 3: Execution loop (no review cap; seed_list-indexed sequential iteration)
  ├─ Per iter:
  │    - Re-assert design.md SHA-256 equals captured design_hash (S4 content guard).
  │      Drift → Err #16 (see §6).
  │    - Compose prompt from C (base + tradition_tokens + color_constraint_tokens)
  │    - Call generate_image(prompt, provider, tradition, seed, steps, cfg_scale,
  │      negative_prompt, output_dir) — MCP-extended signature (§7)
  │    - Err #5 (provider unreachable) → hands directly to Err #13 user prompt
  │    - Err #6 (generate_image error dict) → jsonl row verdict=failed, continue
  │    - Err #13 (cross-class failover) → user 3-option prompt
  │    - Call evaluate_artwork(image_path, tradition); parse L1-L5 from dimensions
  │    - Compute weighted_total = sum(L_N × D1.L_N)
  │    - Apply gating: measured/derived/user_elevated → hard; assumed → soft
  │    - All-zero-scores sentinel: if all L_N < 0.01 → accept-with-warning + log
  │      [evaluate-suspect] to Notes (§8 verdict tree)
  │    - Determine verdict: accept / accept-with-warning / reject
  │    - Append 1 row to plan.md.results.jsonl (14 fields)
  │    - Update fail_fast_counter (reject ++; accept 0; accept-with-warning unchanged)
  │    - Err #7: fail_fast_counter ≥ threshold → 3-option user prompt (unified form)
  │    - Lockfile heartbeat via jsonl mtime (implicit)
  ↓
Phase 4: Finalize + optional hygiene
  ├─ Read jsonl; render ## Results markdown table in plan.md
  ├─ Determine terminal status: completed / partial / aborted
  │    - all iters accepted, zero soft-warnings → completed
  │    - all iters accepted, ≥1 soft-warnings → completed (with handoff variant)
  │    - fail_fast triggered OR Err #13(c) user chose "skip remaining" → partial
  │    - user abort OR Err #13(b) → aborted
  ├─ Rename plan.md.results.jsonl → plan.md.results.jsonl.archive
  ├─ Delete plan.md.lock
  ├─ MAY call unload_models() and log to Notes
  ├─ Write plan.md final (status + updated bumped + Results rendered)
  └─ Print handoff string (1 of 8 verbatim variants, optionally with stale-lock suffix)
```

**Design invariants the architecture serves**: review before execution (B-i gate), append-only recovery (jsonl), concurrency safety (lockfile O_CREAT|O_EXCL), fail-fast with user choice (Err #7 three options), explicit operator oversight on cross-class failover (Err #13).

---

## 4. Parser contract — `design.md` fenced-YAML schema consumption

### 4.1 Tolerant-read rules

Extract fenced ```` ```yaml ... ``` ```` blocks beneath ```## A. ... ## F. ``` headings; parse via `yaml.safe_load` with `allow_duplicate_keys=False` (PyYAML strict default).

**Accept-with-normalization**:
1. Unknown top-level keys inside a dim block → ignore + log to `plan.md ## Notes`: `[parser-warn] <section>.<key>: unknown key dropped`.
2. Missing required key → fill from schema default + log: `[parser-default] <section>.<key> missed; filled with <default>`.
3. Inline `# comments` inside fences → allowed on read; stripped on write.
4. Unknown `##` section headings outside A/B/C/D1/D2/E/F/Open questions/Notes → ignore silently.
5. `C.tradition_tokens` as **flat string list** OR **list[dict]** with `{term, translation, definition?}` → normalize to flat strings `f"{term} {translation}"`.
6. `A.provider` as bare `sdxl` → on darwin normalize to `sdxl-mps`, elsewhere `sdxl-cuda`, log: `[parser-normalize] A.provider: sdxl → sdxl-mps`.
7. `D2.L_N_threshold` / `F.*` as bare number `0.7` → wrap to `{value: 0.7, source: assumed, confidence: low}`.

**Hard-reject (Err #1, #4, #10 per §6)**:
- `frontmatter.status != "resolved"` → Err #1.
- `frontmatter.tradition` not in registry AND not literal YAML null → Err #4.
- `frontmatter.domain` not in 7-enum → Err #4.
- Any of sections A/B/C/D2/F missing → Err #10.
- Duplicate keys within a block (PyYAML raises) → Err #10.
- Fence syntax error → Err #10.
- D1 missing AND `tradition != null` → Err #10.

### 4.2 Strict-write rules — plan.md canonical shape

**Frontmatter: exactly 9 fields, no comments inside `---` fence, deterministic field order**:
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

**schema_version back-compat rule**: Phase 1 reads `design.frontmatter.schema_version`; if the field is absent, treat as `"0.1"` (v0.17.5-era designs lack the field). If present and in the supported set (currently `{"0.1"}`), proceed. If present and unrecognized → Err #15 (version skew, not user-fixable).

**Body: exactly 10 sections, fixed order, every section present (empty uses markdown `none`)**:
```
# <human-readable title, mirror design.md's>
## A. Execution parameters         — fenced YAML from design.A (MCP-extended)
## B. Iteration plan               — fenced YAML: strategy, variation_axis, seed_list, variant_count, batch_size
## C. Prompt composition           — fenced YAML: composed prompts per variant
## D. Gating decisions             — fenced YAML: per L_N {value, source, gate_class}, user_elevated, soft_gate_warn_count
## E. Fail-fast budget + rollback  — fenced YAML: fail_fast_consecutive, rollback_trigger, rollback_action
## F. Cost ledger                  — fenced YAML: initial_budget, actual (from jsonl), overage_pct
## Results                         — markdown table rendered from jsonl at Phase 4
## Notes                           — free-form audit lines
```

Notes required convention lines (when relevant):
- `[parser-default] / [parser-warn] / [parser-normalize]` from Phase 1
- `[override] <section>.<field>: <old> → <new>. Reason: <user rationale>` from Phase 2
- `[resume-state] turns_used: <N>` for Err #3 resume
- `[fail-fast] triggered at iter <K>. consecutive_rejects: <N>.`
- `[stale-lock-recovery] previous pid <N> abandoned at <iso>; reclaimed at <now>. Resuming from iter <K>.` for Err #12
- `[review-required] iter_<N>: L<X>=<score> below threshold <T>` for each soft-gate miss
- `[unload-models] freeing <provider> weights` (Phase 4 optional)

### 4.3 Three-file system per `<slug>`

| File | Role | Lifetime |
|---|---|---|
| `plan.md` | Render artifact; source of truth for agent + human review | entire session + post-finalize |
| `plan.md.results.jsonl` | Append-only recovery authority during Phase 3 | created on first iter; renamed `.archive` at Phase 4 |
| `plan.md.lock` | `O_CREAT\|O_EXCL` concurrency primitive with `{pid, started_at, design_ref}` JSON | created at Phase 1 end; deleted at Phase 4 |

jsonl mtime acts as implicit heartbeat (no separate heartbeat file). Lockfile is not rewritten mid-session — its existence + jsonl mtime freshness are the two liveness signals (see §6 Err #11/#12).

---

## 5. Phase details

### Phase 1 — Precondition + derivation + draft write

Steps (strict order, early-exit on any Err):

0. Assert cwd is Vulca checkout (`Path("src/vulca").is_dir()`) — Err #14 otherwise.
1. Resolve `slug` from positional arg. Compute paths `docs/visual-specs/<slug>/{design.md,plan.md,plan.md.results.jsonl,plan.md.lock,iters/}`.
2. `Read(design.md)`. Missing file or `status != resolved` → Err #1.
3. Check same-slug `plan.md` collision:
   - `status ∈ {completed, partial, aborted}` → Err #2.
   - `status == draft` → Err #3 resume path (continue below, but flag for Phase 2 entry with `turns_used` state).
4. Check `plan.md.lock` (skip if step 3's Err #3 resume path already folded Err #12 recovery):
   - Exists + jsonl fresh (< 300s mtime) OR lockfile `started_at` < 300s + no jsonl → Err #11 concurrent.
   - Exists + stale (jsonl > 300s OR lockfile.started_at > 300s + no jsonl) → Err #12 auto-recover: `os.unlink(lockfile)`, append Notes `[stale-lock-recovery]` line, continue.

   **Err #3 + Err #12 collision rule**: if step 3 detected `status: draft` AND step 4 would have triggered Err #12, the Err #3 resume path executes the Err #12 side-effects (unlink + Notes line + Phase 4 handoff suffix) before entering Phase 2 review loop. Only one recovery Notes line is written. Both tests in §12 assert this ordering.
5. Validate `design.frontmatter.schema_version` per §4.2 back-compat rule. Unrecognized → Err #15.
6. Call `list_traditions()`. Validate `design.tradition` ∈ `traditions.keys()` or literal YAML null → Err #4 otherwise.
7. Validate `design.domain` ∈ 7-enum → Err #4 otherwise.
7.5. Parse 7 fenced-YAML dim blocks per §4.1. Required section missing → Err #10.
8. Sketch readability probe (if `design.C.sketch_integration != "ignore"` and sketch path in `design.## References`): `Read(sketch_path)`. On failure → Err #9 (set internal `sketch_available: false`; override plan.C.sketch_integration to "ignore"; queue Notes entry).
9. Freeze `{tradition, domain, slug}` as session constants (S4). Capture `design_hash = sha256(design.md bytes)` as session constant for Phase 3 content-guard.
10. Derive plan:
    - `seed_list`: start from `design.A.seed`, step +1 for `design.B.variant_count` items. If `design.## Open questions` has explicit `- seeds: [1337, 42, 7]` list → prefer it.
    - `gating_decisions`: per D2 L_N: `gate_class = hard` if source ∈ {measured, derived}, else `soft`. Initial `user_elevated: []`.
    - `composed_prompts`: per variant, assemble `{base_prompt, tradition_tokens, color_constraint_tokens}` + `negative_prompt` → 1 composed string per iter.
    - `fail_fast_budget`: copy `F.fail_fast_consecutive`; if `None`, fail-fast disabled globally.
    - `rollback_plan`: copy `D2.rollback_trigger` + derive `rollback_action` default = `partial` (user overrideable in Phase 2).
    - `F.initial_budget`: copy `design.F` fields verbatim.
11. Create lockfile `plan.md.lock` via `open(path, O_CREAT | O_EXCL | O_WRONLY)` with `{pid: os.getpid(), started_at_iso: now(), design_ref: <path>}`.
12. `Write(plan.md)` with `status: draft` + computed body.

**Turn cost**: zero (Phase 1 does not charge toward cap).

### Phase 2 — Plan-review loop

Cap: 5 turns (hard). `deep review` soft extension: +3 → cap 8. Inherits /visual-spec Phase 4 vocabulary byte-for-byte where possible.

**F-summary prompt** (triggered when any of `F.per_gen_sec / F.total_session_sec` has `source == "assumed"`; fired before the main draft prompt; NOT charged toward cap):

```
F budget is assumed: per_gen_sec ~<X>s × <N> iters × 1.5 margin = ~<Y>s total.
This is derived from mock calibration + provider multiplier; not measured on your hardware.
Reply:
  (a) accept this budget as-is
  (b) override <per_gen_sec_seconds>
  (c) skip-budget-check (disables Err #7 cost enforcement)
```

Reply handling per §3.3 of design:
- `(a)` or `a` or `accept` → `F.user_ack_assumed_budget: true`.
- `(b) <N>` → `F.per_gen_sec = {value: N, source: user-confirmed, confidence: high}`; recompute `F.total_session_sec`.
- `(c)` or `skip` → `F.fail_fast_consecutive = None`; log Notes `[budget-skipped]`.
- Invalid first time → re-prompt once.
- Invalid second time → default to `(a)` + log `[budget-assumed-default]`.

**Main draft prompt** (after F-summary if applicable):

```
Draft plan.md below. Type 'accept all' to finalize, 'change <section>' to revise one, or 'deep review' to extend your review budget +3 turns.
```

**Reply handling**:
- `accept all` (case-insensitive exact match) → flip every dim's internal `reviewed: true`, flip frontmatter `status: draft → running`, `Write` plan.md, enter Phase 3.
- `change <section>` (A / B / C / D / D.L1 / D.L3 / E / F / etc.) → sub-dialog scoped to that section. One targeted question per turn. On user-supplied valid value, apply; on invalid, re-prompt once; second invalid = 1 turn cost + return to main prompt.
  - If the user-edit changes `D.L_N.source` from `assumed` to `user-confirmed` → add `L_N` to `user_elevated`, flip `gate_class: soft → hard`, log Notes `[override] D.L_N.source: assumed → user-confirmed. Reason: <user>.`
  - **Critical**: `user_elevated` persists only in plan.md — **never back-written to design.md** (design.md immutable post-resolved).
- `deep review` → cap += 3 (max 8). One-time per session. Second invocation treated as invalid.
- Ambiguous reply (`looks good but`, etc.) → re-prompt main; count as 1 turn.
- Pixel action request (`just generate now`) → Err #8 decline, turn NOT charged.
- Cap-hit without `accept all` → force-show full draft + prompt `Turn cap reached. finalize or deep review?` No auto-advance (S2).

Per-turn housekeeping: re-`Write(plan.md)` with `status: draft`, bumped `updated`, updated `[resume-state] turns_used: <N>` line in Notes (pairs with EVERY turn that mutated state OR the counter, per brainstorm/spec discipline).

### Phase 3 — Execution loop

No turn cap. Sequential iteration over `seed_list`. Lockfile heartbeat = jsonl mtime.

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
        return  # Err #16 fires; see §6

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
            seed=plan.A.seed + iter_idx,          # MCP-extended
            steps=plan.A.steps,                    # MCP-extended
            cfg_scale=plan.A.cfg_scale,            # MCP-extended
            negative_prompt=plan.A.negative_prompt, # MCP-extended
        )
    except ProviderUnreachable as e:
        # Err #13: cross-class failover user prompt (no auto-failover per §1 S8-removal)
        user_choice = prompt_err13(e, plan.A.provider)
        if user_choice == "a":   # approve cross-class switch
            plan.A.provider = _alt_class_provider(plan.A.provider)
            _log_failover_notes(plan.A.provider)
            continue  # retry this iter with new provider
        elif user_choice == "b":  # abort
            _terminate_phase3(status="aborted", at_iter=iter_idx)
            return
        elif user_choice == "c":  # skip remaining as partial
            _terminate_phase3(status="partial", at_iter=iter_idx)
            return

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
    l_scores = _extract_l_scores(eval_result)  # raises on malformed → caller logs failed
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
        fail_fast_counter = 0
    elif verdict == "accept-with-warning":
        soft_gate_warn_count += 1
        # fail_fast_counter unchanged

    # Err #7: unified 3-option prompt (no F.source branching per review revision)
    if (plan.F.fail_fast_consecutive is not None
        and fail_fast_counter >= plan.F.fail_fast_consecutive.value):
        user_choice = prompt_err7()
        if user_choice == "abort":
            _terminate_phase3(status="aborted", at_iter=iter_idx); return
        elif user_choice.startswith("extend"):
            plan.F.fail_fast_consecutive.value = _parse_extend(user_choice)
            fail_fast_counter = 0  # reset on extend
        elif user_choice == "accept-remaining":
            _terminate_phase3(status="partial", at_iter=iter_idx); return
```

**Phase 3 tool whitelist**: `generate_image`, `evaluate_artwork`, MAY `unload_models` at loop end; jsonl `append` via Write equivalent; lockfile `read` for heartbeat check (no rewrite).

**S1 ban enforced**: no `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*` in any phase.

### Phase 4 — Finalize

1. Read `plan.md.results.jsonl` → all completed rows.
2. Determine terminal status (priority order: `aborted` > `partial` > `completed`):
   - **`aborted`** triggers: user-triggered abort, Err #13(b) user picked "no, abort", Err #7 user picked "abort", Err #16 design.md drift detected mid-Phase-3.
   - **`partial`** triggers: Err #7 user picked "accept-remaining", Err #13(c) user picked "skip as partial", all iters completed but zero had verdict ∈ {accept, accept-with-warning} (i.e., every row was `verdict: failed` via Err #6). Note: mixed rows where at least one is `accept`/`accept-with-warning` do NOT become `partial` — they fall through to `completed` with an `[iter-failures]` Notes line.
   - **`completed`** trigger: all iters in seed_list completed AND at least one verdict ∈ {accept, accept-with-warning}. Soft warnings affect handoff string variant selection (§2) but do NOT demote to partial.
   - **Zero-rows corner case**: if Err #16 (or user abort) fires at iter 0 before any jsonl row is appended, fall-through to `aborted` (no rows → none of "completed" or "partial" conditions can apply).
3. Render `## Results` markdown table from jsonl rows (column order: `iter | seed | variant | image | L1-L5 | weighted | verdict | wall_time | provider | notes`).
4. Populate `## F. Cost ledger` actual: `total_wall_time` sum from jsonl, `overage_pct = actual / initial_budget - 1`.
5. Append any terminal-state Notes lines (`[fail-fast]`, `[aborted-at-iter]`, etc.).
6. Rename `plan.md.results.jsonl` → `plan.md.results.jsonl.archive` (atomic on same filesystem).
7. Delete `plan.md.lock` via `os.unlink`.
8. MAY call `unload_models()` on `plan.A.provider`'s weight family if post-session cleanup desired. Log to Notes if called.
9. Write final `plan.md` with `status: <terminal>`, `updated: <today>`.
10. Assert S4: `plan.frontmatter.tradition == captured_tradition`, same for `domain`, `slug`. Violation → raise (code bug; should never fire).
11. Determine handoff string variant (§2 table — 8 variants across {completed, completed-with-soft-warnings, partial×4 by trigger source, aborted×2 by trigger source}); append ` (recovered from stale lock at iter <K>)` suffix if Phase 1 fired Err #12 or folded it via Err #3.
12. Print handoff string byte-identical.

**Do NOT auto-invoke anything downstream.** /visual-plan is terminal.

---

## 6. Error matrix (16 rows — grep-contract verbatim)

All `Print exactly:` strings are backtick-wrapped for downstream grep compatibility.

| # | Signal | Response | Enforce class |
|---|---|---|---|
| 1 | `design.md` not found OR `status != resolved` | Print exactly: `design.md not found or status != resolved at <path>. Run /visual-spec <slug> first.` Terminate. | helper |
| 2 | Same-slug `plan.md` exists with terminal status (`completed` / `partial` / `aborted`) | Print exactly: `already <status> at <path>; branch with -v2 or pick new slug`. Terminate. **Do not overwrite.** | helper + prescription |
| 3 | Same-slug `plan.md` status: draft (with or without jsonl) | Resume Phase 2: re-enter review loop, skip sections with `reviewed: true`, accumulate turns_used from Notes `[resume-state]` line. If jsonl present → Phase 3 entry replays completed iters. **If a stale lockfile also exists, fold Err #12 side-effects (unlink + `[stale-lock-recovery]` Notes line + Phase 4 handoff suffix) into this resume path; only one recovery Notes line total.** | helper + prescription |
| 4 | design.md frontmatter violation (`tradition` not in registry and not YAML null; OR `domain` not in 7-enum) | Print exactly: `design.md frontmatter violation: <field> <value> invalid. Re-run /visual-spec <slug> to fix.` Terminate. **Do not auto-retry.** | helper |
| 5 | Phase 3 provider unreachable (connection refused / missing key / timeout) | **No auto-failover.** Append `[failover-needed] <provider> unreachable: <err>` to Notes. Advance directly to Err #13 user prompt. | helper (hands off to #13) |
| 6 | `generate_image` returns error dict (validation / OOM / malformed param) | jsonl row: `verdict: failed, error: <excerpt>`. Continue next iter. All-fail → terminal `partial` (distinct from all-skipped). | helper |
| 7 | Phase 3 `fail_fast_counter >= F.fail_fast_consecutive.value` (applies only when `F.fail_fast_consecutive is not None`) | Force-show current draft + print exactly: `cost budget exceeded (<consecutive>×over). Abort, extend budget, or accept remaining?` User picks `(a)` abort → status `aborted`; `(b) extend <N>` → fail_fast_consecutive reset to N, counter reset 0, continue; `(c) accept-remaining` → status `partial`. **Never auto-extend.** | prescription |
| 8 | User requests pixel action in Phase 1/2/4 (`generate now`, `skip review`) | Print exactly: `plan layer executes pixels in Phase 3 only. Complete review (accept all) first, or change spec via /visual-spec <slug>.` Do NOT invoke tool. **Turn NOT charged.** | prescription (S1 parallel) |
| 9 | design.md `## References` sketch unreadable at Phase 1 probe | Set state `sketch_available: false`; override `plan.C.sketch_integration: ignore`. Notes: `sketch at <path> unreadable at plan time: <err>. Proceeding text-only; C.sketch_integration forced to "ignore".` **Do not abort.** | helper |
| 10 | design.md YAML parse-fail (required section missing / dup keys / fence syntax) | Print exactly: `design.md parse-fail at <slug>: <issue>. Re-run /visual-spec <slug> to regenerate.` Terminate. **Do not auto-retry.** | helper |
| 11 | Same-slug concurrent /visual-plan (lockfile exists + jsonl mtime < 300s OR lockfile.started_at < 300s + no jsonl) | Print exactly: `<slug> currently running (pid: <pid>, started: <iso>). Abort the other session first, or wait and retry.` Terminate. **Do not kill other pid.** | helper |
| 12 | Stale lockfile (lockfile exists + jsonl mtime > 300s OR lockfile.started_at > 300s + no jsonl) | Auto-recover silently to terminal: `os.unlink(lockfile)`. Append to Notes: `[stale-lock-recovery] previous pid <N> abandoned at <iso>; reclaimed at <now>. Resuming from iter <K>.` Handoff string at Phase 4 finalize appends ` (recovered from stale lock at iter <K>)` suffix. **No user prompt; no stderr print** (Claude Code does not surface stderr from skills). | helper |
| 13 | Phase 3 provider unreachable AND failover requires cross-class switch (local ↔ cloud) | Print exactly: `<current> unreachable, failover to <alt> requires cross-class switch (local→cloud or reverse). Approve? (a) yes / (b) no, abort / (c) no, skip remaining iters as partial`. **Prompt user. Turn NOT charged.** `(a)` → execute failover + Notes `[failover-cross-class]`; `(b)` → terminal `aborted`; `(c)` → terminal `partial`. | prescription |
| 14 | `Path("src/vulca").is_dir()` false (not inside Vulca checkout) | Print exactly: `not inside a Vulca checkout; /visual-plan requires repo presence at cwd. cd into your vulca repo and retry.` Terminate. Do not probe further paths. | helper |
| **15** | `design.frontmatter.schema_version` present AND not in supported set `{"0.1"}` | Print exactly: `design.md schema_version <got> not recognized; upgrade /visual-spec (pip install --upgrade vulca) or pin vulca@<compatible>.` Terminate. **Do not auto-retry; do not suggest /visual-spec re-run** (it would produce the same unsupported version). | helper |
| **16** | Phase 3 per-iter hash guard detects `design.md` bytes changed since Phase 1 capture | Print exactly: `design.md mutated mid-session at iter <K>; aborting. Re-run /visual-plan <slug> to restart with new design.` Abort immediately. Status → `aborted`. jsonl up through iter `<K-1>` preserved. Append to Notes: `[design-drift] design.md sha256 changed between Phase 1 and iter <K>; aborting.` | helper (content-guard) |

**Classification footer**:
- **Do NOT auto-retry**: Err 1, 4, 7, 10, 14, 15, 16.
- **Do NOT overwrite**: Err 2.
- **Degrade, continue**: Err 6, 9.
- **Resume / recover (special)**: Err 3 (draft resume), 12 (stale-lock auto-recover). Collision rule (§5 Phase 1 step 4): Err #3 path absorbs Err #12 side-effects when both fire.
- **Decline without charge**: Err 8, 13 (cross-class prompt).
- **Refuse-to-start**: Err 11, 14, 15.
- **User prompt**: Err 7, 13 (both 3-option).
- **Hands-off**: Err 5 → #13.
- **Content-guard abort**: Err 16 (rare; only fires when design.md bytes change mid-session).

---

## 7. Invariants (S1-S7, 7 total — reduced from initial 9 post-review)

| # | Rule | Enforce class | Notes |
|---|---|---|---|
| **S1** | Pixel-tool ban baseline. Exemptions: (a) Phase 3 execution authorizes ONLY `generate_image`, `evaluate_artwork`, MAY `unload_models`; (b) no other phase uses pixel tools. Forbidden across EVERY phase (no exemption): `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*`. | prescription | Agent self-discipline; Err #8 fires on user-driven request. |
| **S2** | Do not flip `frontmatter.status` without explicit user trigger: `draft → running` requires `accept all`; `running → terminal` requires a terminal condition (all iters done, fail_fast, user-abort, Err #13). Cap-hit alone is NOT a trigger. | prescription | Vibe-plan anti-pattern; downstream misaligned. |
| **S3** | Only consume `design.md` with `status: resolved`. Reject anything else via Err #1. | helper | Enforceable at Phase 1 gate. |
| **S4** | `frontmatter.{tradition, domain, slug}` are **immutable** across the session (captured at Phase 1, asserted at Phase 4). `A.provider` is **EXPLICITLY MUTABLE** via user-approved Err #13 cross-class failover only — any mutation outside Err #13 is an S4 violation. Additionally, `design.md` file bytes are content-hash-guarded: Phase 1 captures `sha256(design.md)` into session `design_hash`; Phase 3 re-hashes per iter; drift → Err #16 abort. | helper (Phase 4 write-time check + Phase 3 per-iter content guard) | Violation is a code bug or external-edit-during-execution; not an agent choice. |
| **S5** | Concurrency control via `plan.md.lock` (`O_CREAT\|O_EXCL` with `{pid, started_at_iso, design_ref}` JSON). Staleness judged by jsonl mtime (when present) OR lockfile `started_at` (when no jsonl), both compared to 300s threshold. Stale → auto-recover per Err #12. Fresh → refuse per Err #11. | helper (POSIX atomicity) | Precedent: `src/vulca/digestion/dream.py:46-80`. |
| **S6** | `plan.md.results.jsonl` is append-only during Phase 3. One row per completed iter (success OR failed OR skipped-via-failover). No rewrites; sequential append in `iter_idx` order (natural from sequential Phase 3). | helper (write discipline) | Recovery authority for Err #3 + #12. |
| **S7** | `plan.md` is a render artifact only. Phase 3 does NOT rewrite `plan.md` mid-loop (all per-iter progress goes to jsonl). Phase 4 finalize reads jsonl → renders `## Results` → atomic `os.rename(.jsonl → .jsonl.archive)` → Write terminal plan.md. | prescription + helper (separation of concerns) | Crash window for plan.md is only Phase 1 initial write + Phase 4 finalize write. |

**Deleted from earlier draft** (post parallel review):
- ~~S8 quality-class failover~~ — /visual-spec design explicitly deferred automatic fallback (`2026-04-21-visual-spec-skill-design.md:401`); only 4 providers exist (mock/gemini/openai/comfyui). Cut. Err #5 now hands directly to Err #13.
- ~~S9 seed-monotonic append order~~ — tautological with sequential Phase 3. Add back if parallelization lands.

---

## 8. Source-gating decisions (Phase 2 matrix)

| design.md field | source value | plan.md `gate_class` | Phase 3 behavior |
|---|---|---|---|
| `D2.L_N_threshold` | `measured` | **hard** | score < value → `reject` verdict, `fail_fast_counter++` |
| `D2.L_N_threshold` | `derived` | **hard** | same as measured (calibration-anchored, trusted) |
| `D2.L_N_threshold` | `assumed` | **soft** | score < value → `accept-with-warning`, log `[review-required]` to Notes, `soft_gate_warn_count++`, counter unchanged |
| `D2.L_N_threshold` | `user-confirmed` (post-elevation) | **hard** | same as measured; only possible after Phase 2 `change D.L_N` subcommand |
| `F.per_gen_sec` | `measured` / `derived` | **hard-budget** | enforced by Err #7 fail_fast counter |
| `F.per_gen_sec` | `assumed` | **Phase 2 F-summary prompt decides** | reply (a) → hard-budget continues + `user_ack_assumed_budget: true`; (b) → updates value, source=user-confirmed, hard-budget; (c) → disables Err #7 entirely via `fail_fast_consecutive = None` |
| `F.fail_fast_consecutive` | any source | **hard-counter** | value applies regardless of source once the F-summary path resolved |
| `D1.L_N` | (no triple) | **registry-authority** | weighted_total multiplier only; not itself a gate |

**Phase 2 `change D.L_N` semantics**: user explicitly typing a value → `D.L_N.source: assumed → user-confirmed`, `gate_class: soft → hard`, append `L_N` to `user_elevated: []`, log Notes `[override]`. **`user_elevated` persists only in plan.md — never back-written to design.md.**

**Phase 3 verdict tree**:
```
# Sentinel: all-zero scores indicate evaluator failure masquerading as pass.
# Without this guard, a broken evaluate_artwork silently greenlights every iter.
# Threshold is <0.01 (not ==0.0) to catch float-representation noise from evaluators
# that emit 1e-7 floats rather than exact zero. Legitimate single-L outliers at 0.008
# do NOT trigger — sentinel requires ALL FIVE dims simultaneously below 0.01.
if all(l_scores[k] < 0.01 for k in ("L1", "L2", "L3", "L4", "L5")):
    _append_notes(f"[evaluate-suspect] iter {iter}: all L_N scores < 0.01; flagged for review")
    return "accept-with-warning"

hard_fails = [L_N for L_N in L1..L5 if gate_class=hard AND score < value]
soft_fails = [L_N for L_N in L1..L5 if gate_class=soft AND score < value]
budget_overage = (F.fail_fast_consecutive is not None AND wall_time > F.per_gen_sec.value * 2)

if hard_fails: return "reject"
if soft_fails or budget_overage: return "accept-with-warning"   # NOT reject, counter unchanged
return "accept"                                                  # fail_fast_counter → 0
```

---

## 9. jsonl row schema (Phase 3 append-only)

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
  "gate_decisions": {
    "hard_fails": [],
    "soft_fails": [["L3", 0.58, 0.6], ["L5", 0.49, 0.5]],
    "budget_overage": false
  },
  "prompt_used": "..."
}
```

**Schema rules**:
- UTF-8, NDJSON (newline-delimited JSON), one row per line.
- Serialize with `json.dumps(..., ensure_ascii=True, separators=(",", ":"))` (grep-safe; CJK escapes to `\uXXXX`).
- Always terminate with `"\n"`; read via `[json.loads(l) for l in content.splitlines() if l.strip()]` (tolerant of torn last line from crash).
- 14 required fields listed above; 1 optional `error` field (present on `verdict: failed` rows only); 1 optional `evaluate_artwork_raw` field (full tool return; off by default).
- `iter` is strictly monotonic increasing by 1 per append (natural from sequential Phase 3).

---

## 10. MCP extension (cross-cutting, v0.17.6 pre-requisite)

Before /visual-plan can ship, `generate_image` MCP tool must accept 4 new kwargs. This ships in **vulca v0.17.6 bundled with Task C clarity patch** (prereq for v0.17.7 /visual-plan ship).

**Signature (v0.17.6)**:
```python
async def generate_image(
    prompt: str,
    provider: str = "gemini",
    tradition: str = "default",
    reference_path: str = "",
    output_dir: str = "",
    seed: int | None = None,              # NEW
    steps: int | None = None,              # NEW
    cfg_scale: float | None = None,        # NEW
    negative_prompt: str = "",             # NEW
) -> dict:
```

Fully backward-compatible (all new params default to `None` or empty string = identical to pre-v0.17.6 behavior).

**Per-provider plumbing** (`src/vulca/providers/*.py`):

| Provider | File | Change |
|---|---|---|
| `mock` | `providers/mock.py` | Echo all new kwargs in result metadata; used by pytest. |
| `comfyui` | `providers/comfyui.py:98` | Parameterize KSampler node: read `seed / steps / cfg_scale / negative_prompt` from kwargs; None → keep current hardcoded defaults. |
| `openai` | `providers/openai_provider.py:21` | Prepend `negative_prompt` to user prompt as `"avoid: <negative>. <prompt>"`. Silently ignore `seed / steps / cfg_scale` (OpenAI doesn't support). |
| `gemini` | `providers/gemini.py:79` | Prepend `negative_prompt` to user prompt. Wire `seed` to `generationConfig.seed` when non-None. Ignore `steps / cfg_scale`. |

**Additional schema_version field** (bundled in v0.17.6 Task C, per review Ruling G):
- `design.md` frontmatter gains `schema_version: "0.1"` field (/visual-spec writes it on new finalize).
- `plan.md` frontmatter gains same.
- /visual-plan Phase 1 refuses `design.md` with unrecognized `schema_version` (Err #15, not Err #4 — see §6).
- v0.17.6 does NOT retro-write `schema_version` into pre-existing `design.md` files on disk; the back-compat rule (absent → "0.1") covers v0.17.5-era files without touching them.

---

## 11. Ship-gate protocol (3 layers)

Mirror /visual-spec v0.17.5 three-layer model:

### Layer A — pytest tripwires (blocking)

~65 test cases across 5 files (see §12 for full enumeration). Must all pass before advancing to Layer B.

### Layer B — simulated mechanical ship-gate (blocking)

3 parallel subagents × ~4 cases each = ~12 cases covering:
- P1 full positive flow (design.md → plan.md draft → accept all → Phase 3 with mock provider → completed handoff)
- P2 Err #3 resume path (plan.md draft + partial jsonl → Phase 2 continues + Phase 3 replays)
- P3 Err #11 concurrent lockfile
- N1-N9 error matrix single-fire (Err 1/2/4/6/8/9/10/13/14 each triggered with verbatim string check)
- N10 stale-lock Notes-append verification
- N11 user_elevated doesn't touch design.md

Tool calls noted but not executed (sticks with v1 mechanical pattern).

### Layer C — live ship-gate v2 (non-blocking but ship-ready signal)

2 parallel subagents × 3 cases each = ~6 cases:
- α: P1-live full Phase 3 with real `generate_image(mock)` × 3 iters + real `evaluate_artwork` × 3; verify jsonl atomicity, MCP-ext backward compat, handoff byte-identical.
- β: Err-matrix real-filesystem (Err #11 lockfile collision, Err #12 stale-recovery, Err #2 refuse-overwrite, Err #8 decline).

Subagent-dispatch caveat (learned from /visual-spec v2 2026-04-22): MCP tools do NOT auto-expose in dispatched subagents; brief must include `PYTHONPATH=src python3.11 -c "import asyncio; from vulca.mcp_server import ...; asyncio.run(...)"` pattern.

### Release chain (per memory `feedback_release_checklist`)

1. **v0.17.6 ships first**: 4 bundled scope items:
   - MCP extension (seed/steps/cfg_scale/negative_prompt kwargs on `generate_image` + 4-provider plumbing per §10)
   - `schema_version: "0.1"` field added to `design.md` + `plan.md` frontmatter (back-compat: absent → treated as "0.1" for v0.17.5-era files; no break for in-flight proposals)
   - 10 clarity-gap items from `project_visual_spec_clarity_gaps.md` (wording fixes in /visual-spec SKILL.md)
   - pytest for MCP extension (§10) + schema_version round-trip (/visual-spec side)
2. **v0.17.7 ships second**: /visual-plan SKILL.md + 5 pytest files (~58 cases) + ship-gate docs. Requires v0.17.6 MCP surface + schema_version landed.
3. Each: tag + push + GitHub release + PyPI publish + plugin sync PR.

---

## 12. Pytest contract surface (~65 cases across 5 files)

### `tests/test_visual_plan_parser_invariants.py` (~15 cases)
- `test_parser_roundtrip_minimal_design`
- `test_parser_roundtrip_full_design_with_spike`
- `test_parser_roundtrip_null_tradition_no_spike`
- `test_tolerant_read_flat_tradition_tokens`
- `test_tolerant_read_dict_tradition_tokens` (v2-delta #7 fix)
- `test_tolerant_read_bare_numeric_d2_threshold`
- `test_tolerant_read_bare_sdxl_provider` (v2-delta #3 fix)
- `test_tolerant_read_inline_comments_stripped_on_write`
- `test_tolerant_read_unknown_top_level_key_warning`
- `test_tolerant_read_missing_optional_section_E`
- `test_tolerant_read_missing_required_section_raises_err10`
- `test_tolerant_read_unknown_section_heading_ignored_silently`
- `test_tolerant_read_missing_defaultable_required_field_fills_and_logs`
- `test_strict_write_frontmatter_exactly_9_fields_includes_schema_version`
- `test_skill_body_matches_spec_phase_invariant_err_counts` (drift-audit guard)

### `tests/test_visual_plan_source_gating.py` (~11 cases)
- `test_gating_assumed_d2_becomes_soft`
- `test_gating_measured_d2_becomes_hard`
- `test_gating_user_elevated_hard_no_design_mutation`  (key: design.md untouched)
- `test_f_summary_prompt_triggered_on_assumed`
- `test_f_summary_prompt_skipped_on_measured`
- `test_f_summary_reply_accept_keeps_assumed_flag`
- `test_f_summary_reply_override_updates_value`
- `test_f_summary_reply_skip_nulls_fail_fast`
- `test_verdict_hard_fail_reject`
- `test_verdict_soft_fail_accept_with_warning_counter_unchanged`
- `test_verdict_all_zero_flags_evaluate_suspect`  (sentinel guard per §8)

### `tests/test_visual_plan_execution_loop.py` (~14 cases)
- `test_phase3_verdict_accept_counter_resets`
- `test_phase3_verdict_accept_with_warning_counter_unchanged`
- `test_phase3_verdict_reject_increments_counter`
- `test_phase3_fail_fast_err7_unified_prompt_verbatim`  (verbatim string + no F.source branching)
- `test_phase3_fail_fast_null_never_breaks`
- `test_jsonl_row_schema_14_required_fields`
- `test_jsonl_utf8_ensure_ascii_true`
- `test_jsonl_append_only_crash_leaves_n_rows_not_n_plus_partial`  (S6 atomicity)
- `test_resume_from_jsonl_skips_completed_iters`
- `test_resume_fail_fast_counter_rebuilt`
- `test_unload_models_optional_in_phase4`
- `test_s2_cap_hit_without_accept_stays_draft`  (S2 enforcement)
- `test_s5_lockfile_exclusive_create_atomicity`  (S5 O_CREAT|O_EXCL)
- `test_phase4_terminal_status_priority_aborted_over_partial_over_completed`

### `tests/test_visual_plan_error_matrix.py` (~14 cases)
- `test_err1_verbatim_string`
- `test_err2_refuse_overwrite_terminal_states`
- `test_err3_resume_replays_jsonl`
- `test_err3_plus_err12_collision_folds_recovery_into_resume`  (Blocker B5 fix)
- `test_err4_verbatim_string_frontmatter_violation`
- `test_err5_hands_off_to_err13_no_auto_failover`
- `test_err6_per_iter_failed_continues_and_all_fail_becomes_partial`
- `test_err7_verbatim_string_and_three_option_branch`  (abort→aborted, extend→continue, accept-remaining→partial)
- `test_err8_pixel_request_decline_turn_not_charged`
- `test_err9_sketch_unreadable_degrades_sketch_integration`
- `test_err10_parse_fail_verbatim_string`
- `test_err11_concurrent_lockfile_refuses`
- `test_err12_stale_lock_writes_notes_not_stderr`  (key: Ruling D fix)
- `test_err13_cross_class_prompt_three_option_outcomes`  (a→failover+notes, b→aborted, c→partial)
- `test_err14_sentinel_cwd_check`
- `test_err15_schema_version_unrecognized_refuses`
- `test_err16_design_hash_drift_aborts_at_iter`

### `tests/test_generate_image_extended_signature.py` (~8 cases)
- `test_generate_image_accepts_seed_kwarg`
- `test_generate_image_seed_mock_echo`
- `test_generate_image_seed_comfyui_ksampler_param`
- `test_generate_image_negative_prompt_openai_prepended`
- `test_generate_image_negative_prompt_gemini_prepended`
- `test_generate_image_steps_ignored_by_cloud_providers`
- `test_generate_image_backward_compat_no_new_kwargs`
- `test_generate_image_none_defaults_equivalent_to_omitted`

---

## 13. Open questions (legitimately deferred to implementation)

1. **`--max-iters` flag semantics** (§2): does it truncate `seed_list` before Phase 2 review (so user sees N iters in draft), or only at Phase 3 entry? Leaning toward former for transparency; verify during implementation.
2. **Unload-models heuristic** (§Phase 4.8): when MAY skill call `unload_models`? Currently unspecified; proposed rule: call iff `plan.A.provider` is local (`comfyui` / `sdxl-*`) AND terminal status ∈ {completed, partial}. Defer exact rule to first real-user feedback.

**Resolved during spec self-review + parallel mid-review (no longer open)**:
- ~~evaluate_artwork all-zero detection~~ → folded into §8 verdict tree as sentinel + `[evaluate-suspect]` Notes line; pytest `test_verdict_all_zero_flags_evaluate_suspect` in §12.
- ~~SKILL.md drift audit pytest~~ → promoted to §12 as `test_skill_body_matches_spec_phase_invariant_err_counts`.

---

## 14. Invariant summary (quick reference)

- **7 invariants**: S1 pixel ban + Phase 3 whitelist / S2 no auto-status / S3 consume resolved only / S4 immutable {tradition, domain, slug} + A.provider mutable only via Err #13 + design.md content-hash guard / S5 lockfile O_CREAT|O_EXCL + 300s staleness / S6 jsonl append-only / S7 plan.md render-artifact-only.
- **4 phases**: precondition+derive+draft-write / plan-review-loop / execute / finalize.
- **3 terminal states**: completed / partial / aborted (completed-with-soft-warnings is a handoff string variant, not a separate status).
- **16 error matrix rows**: 1-4 preconditions / 5-7 execution runtime / 8 pixel-decline / 9 sketch-degrade / 10 parse-fail / 11-12 concurrency / 13 cross-class / 14 sentinel / 15 schema-version skew / 16 design-drift content-guard.
- **~65 pytest cases** across 5 test files (15 parser + 11 source-gating + 14 execution + 17 error-matrix + 8 MCP-extension).
- **plan.md frontmatter: 9 fields** (schema_version added v0.17.6; back-compat rule: absent → "0.1").
- **Cross-skill dependency**: v0.17.6 MCP extension + schema_version must land before v0.17.7 /visual-plan ship. `schema_version` is back-compat additive (absent → "0.1"); no break for in-flight v0.17.5-era `design.md`.

---

## References

- Parent siblings: `docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md`, `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md`
- Ship-gate precedents: `docs/superpowers/plans/visual-spec-ship-gate-log.md` (v1), `docs/superpowers/plans/visual-spec-live-ship-gate-log.md` (v2 live 2026-04-22)
- Memory context: `project_vulca_0_17_5_shipped.md`, `project_visual_spec_clarity_gaps.md`, `project_visual_spec_layerC_v2_green.md`, `feedback_parallel_review_discipline.md`, `feedback_release_checklist.md`, `user_collaboration_style.md`
- Lockfile precedent: `src/vulca/digestion/dream.py:46-80` (O_CREAT|O_EXCL + stale-lock handling)
- Append-only jsonl precedent: `src/vulca/storage/unified.py:52-99`
- Real MCP surface: `src/vulca/mcp_server.py:1131-1201` (pre-v0.17.6 `generate_image`)
- Providers: `src/vulca/providers/{mock,comfyui,openai_provider,gemini}.py`
