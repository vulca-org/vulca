# `/visual-plan` Ship-Gate Log (v1 — simulated)

**Date:** 2026-04-23
**Branch:** `master`
**Skill commit under test:** `d69eb7e1` (Phase 2 plan-review loop body)
**Spec reference:** `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md` §11.2
**Plan reference:** `docs/superpowers/plans/2026-04-23-visual-plan-skill.md` Task 8

## Protocol

Three parallel subagents act as "Claude Code sessions loading the skill" — each reads `.claude/skills/visual-plan/SKILL.md` verbatim and simulates both agent-following-skill and scripted user. Tool calls (list_traditions / generate_image / evaluate_artwork / Read / Write) noted but not executed. Pixel tools verified NOT called outside Phase 3 whitelist.

This is the mechanical-rule surface simulation. Layer C live ship-gate v2 deferred to Task 9 (v0.17.6 MCP extension already shipped 2026-04-23 so Task 9 is unblocked).

## Case matrix

| # | Case | Subagent | Verdict |
|---|---|---|---|
| P1 | Positive full flow (design.md status:resolved → plan.md draft → accept all → Phase 3 with mock provider → completed) | α | PASS |
| P2 | Err #3 resume (plan.md status:draft + 3-row jsonl → Phase 2 continues, Phase 3 from iter 3) | α | PASS |
| P3 | Err #11 concurrent lockfile (fresh lock + fresh jsonl → refuse) | α | PASS |
| N1 | Err #1 design.md not found → verbatim terminate | β | PASS |
| N2 | Err #2 same-slug completed → refuse-overwrite | β | PASS |
| N3 | Err #4 tradition not in registry → verbatim terminate | β | PASS |
| N4 | Err #8 pixel request in Phase 2 → decline + turn NOT charged | β | PASS |
| N5 | Err #9 sketch unreadable → degrade + continue | γ | PASS |
| N6 | Err #10 design.md YAML parse-fail → verbatim terminate | γ | PASS |
| N7 | Err #12 stale-lock auto-recover + Notes append (no stderr) | γ | PASS |
| N8 | Err #13 cross-class prompt option (c) → partial | γ | PASS |
| N9 | Err #14 not in Vulca checkout → sentinel terminate | γ | PASS |
| N10 | Err #15 schema_version unrecognized → refuse | γ | PASS |
| N11 | user_elevated persists plan.md only, design.md untouched (decision #10) | α | PASS |

**Aggregate: 14/14 PASS.**

## Results

### Subagent α report (4/4 PASS)

#### Case P1 — PASS
**Fixture**: `docs/visual-specs/demo-p1/design.md` exists, `status: resolved`, `tradition: null` (literal), `domain: poster`, `schema_version: "0.1"`, 7 fenced-YAML blocks present (D1 omitted allowed per step 8 since tradition is null), `A.provider: mock`, `A.seed: 1337`, `B.variant_count: 4`, all F fields `source: measured`. No prior `plan.md`, no lockfile, no jsonl. `src/vulca/` exists.

**Phase 1 walk**: Step 0 passes (Vulca sentinel). Steps 1-3 pass (no collision). Step 4: no lockfile → skip. Step 5: schema_version 0.1 ∈ supported. Step 6: tradition literal null → accept. Step 7: domain ∈ 7-enum. Step 8: 6 sections (A/B/C/D2/E/F) parse cleanly; D1 legitimately absent per "D1 optional iff tradition: null." Step 9: sketch_integration=ignore → skip probe. Step 10: capture `design_hash`. Step 11: derive `seed_list = [1337, 1338, 1339, 1340]`, gate_class=hard for all L_N (measured), fail_fast from F. Step 12: create lockfile via `O_CREAT | O_EXCL`. Step 13: Write plan.md `status: draft`. **No pixel tools touched — S1 OK.**

**Phase 2 walk**: F-summary prompt SKIPPED (all F sources=measured, not assumed). Render draft + persist via Write. Print main prompt verbatim. User replies `accept all` on turn 1. Agent flips all `reviewed: true`, flips `status: draft → running` (S2 OK — explicit trigger), Writes plan.md, enters Phase 3.

**Phase 3 walk**: 4 iters, seed_list[0..3]. Per iter: re-hash design.md (matches — S4 OK), compose prompt, call `generate_image(provider="mock", …)` **(S1 whitelist — ALLOWED)**, call `evaluate_artwork` **(S1 whitelist — ALLOWED)**, append jsonl row (monotonic iter 0→3, S6 OK). All 4 iters: mock returns valid → verdict=`accept` (measured gates hit); fail_fast_counter stays 0. No Err #7.

**Phase 4 walk**: read jsonl (4 rows, all accept, zero soft). Terminal = `completed`, zero soft warnings. Render Results table. Populate F ledger. Rename jsonl → .archive. Delete lockfile. Write final plan.md `status: completed`. Assert S4 passes. Handoff variant #1: byte-identical to §handoff row 1.

**Invariants**: S1 ✓ S2 ✓ S4 ✓ S6 ✓ S7 ✓.

#### Case P2 — PASS (with 1 minor ambiguity called out)
**Fixture**: `design.md` as P1. `plan.md` exists, `status: draft`, has Notes line `[resume-state] turns_used: 2`. `plan.md.results.jsonl` has 3 rows (iter 0/1/2, all `verdict: accept`), mtime = now (fresh). No lockfile.

**Phase 1 walk**: Steps 0-2 pass. Step 3: plan.md exists, `status: draft` → Err #3 resume path. No stale lockfile → Err #12 fold does not apply. Step 4 skipped per step 3 resolution. Steps 5-10 pass normally. Step 11 derivation runs (idempotent). Step 12: agent recreates lockfile. Step 13: agent rewrites plan.md status:draft preserving `reviewed: true` flags.

**Phase 2 walk**: enter with `turns_used = 2`. Render draft (skipping sections already `reviewed: true` per Err #3 text). User replies `accept all` on turn 3 (against effective remaining cap 5−2=3). Status flips draft→running.

**Phase 3 walk**: `completed_iters = _replay_jsonl_if_exists()` returns 3. Loop: iter_idx 0/1/2 → `continue` (already completed). iter_idx 3: re-hash (OK), generate_image(mock), evaluate_artwork, append jsonl row 4. fail_fast_counter rebuilt from prior 3 accepts = 0.

**Phase 4 walk**: 4 rows total, all accept → `completed`. Handoff variant #1. S4 assertions pass.

**Called ambiguity**: SKILL.md §Phase 1 step 3 + 4 interaction is clean when both Err #3 AND stale lockfile present, but **silent on Err #3 + fresh lockfile** (previous session crashed mid-run, lockfile still fresh). A strict reader could either (a) hit Err #11 and refuse, or (b) rescue-on-resume. Spec §6 Err #11 row doesn't exempt resume paths → agent SHOULD refuse with Err #11 — correct per letter of S5/§6, but surprising UX. Non-blocking clarity gap.

#### Case P3 — PASS
**Fixture**: `design.md` resolved. No plan.md. Lockfile exists with `started_at` 10s ago, jsonl mtime 15s ago (both fresh).

**Phase 1 walk**: Step 4: lockfile exists + jsonl fresh (15s < 300s) → **Err #11 fires.** Print exactly: `demo-p3 currently running (pid: 4242, started: <iso>). Abort the other session first, or wait and retry.` — byte-match §6 row 11. Terminate.

**Tool calls**: `Read(design.md)`, `Read(plan.md.lock)`, `os.stat(jsonl)`. **NO `os.unlink(lockfile)`** (S5 semantic). **NO `Write` to plan.md**. **NO pixel tools** (S1 ✓).

**Invariants**: S1 ✓ S2 ✓ S5 ✓ (O_CREAT|O_EXCL semantic honored).

#### Case N11 — PASS
**Fixture**: design.md with `D2.L3_threshold: {value: 0.6, source: assumed, confidence: low}` + 4 other L_N thresholds measured. plan.md fresh draft rendered. Lockfile fresh. No jsonl yet.

**Phase 2 walk**: F-summary skipped (F measured). Main prompt fires. User turn 1: `change D.L3`. Agent opens sub-dialog. User turn 2: `0.65 user-confirmed, reason: hand-tuned on calibration set`. Agent applies:
- Flip `D.L3.value = 0.65`, `source: user-confirmed`, `gate_class: soft → hard`.
- Append `L3` to `plan.D.user_elevated: [L3]`.
- Append Notes `[override] D.L3.source: assumed → user-confirmed. Reason: hand-tuned on calibration set.`
- Flip section reviewed flag true.
- Re-`Write` plan.md.

**CRITICAL S4 check**: during ENTIRE sub-dialog, agent ONLY Writes `plan.md`. design.md is NEVER touched. Skill body states this in 3 places (§Source-gating, §Phase 2 reply handler, §Invariants S4). Design_hash remains stable.

**Invariants**: S1 ✓ S2 ✓ S4 ✓ (design.md bytes untouched; `A.provider` unchanged), S6 user_elevated invariant ✓ (persists plan.md only), S7 ✓.

#### α summary
**4/4 PASS.**

Deltas:
1. **P2-adjacent ambiguity**: Err #3 + fresh-lockfile interaction undefined. Strict reader fires Err #11 — correct per letter but surprising UX. Non-blocking clarity gap.
2. **Minor wording drift**: skill body Phase 2 item 4 mentions `change D.L3` but §Phase 2 housekeeping refers to "compact form" which is undefined. Not surface-impacting.
3. **Positive**: verbatim error strings byte-match §6, handoff variant #1 byte-match, S1 whitelist unambiguous, S4 restated in 3 places (redundancy correct for load-bearing rule).

### Subagent β report (4/4 PASS)

#### Case N1 — PASS
**Fixture**: Slug = `2026-04-23-does-not-exist`. No `docs/visual-specs/2026-04-23-does-not-exist/` dir. cwd sentinel passes.

**Phase walk**: Step 0 pass. Step 1 paths. Step 2 `Read(design_path)` raises FileNotFoundError → Err #1. Terminate. No plan.md.lock created. No `Write`.

**Verbatim check**: `design.md not found or status != resolved at docs/visual-specs/2026-04-23-does-not-exist/design.md. Run /visual-spec 2026-04-23-does-not-exist first.` — matches §6 row 1 byte-for-byte.

**Invariants**: S1 ✓ S2 ✓ S3 ✓. **Minor ambiguity**: strict-reader could emit Python traceback before Err #1; add "on FileNotFoundError, catch and emit Err #1 verbatim before any traceback" note.

#### Case N2 — PASS
**Fixture**: design.md `status: resolved`. plan.md exists at same slug with `status: completed`.

**Phase walk**: Step 3 reads plan.md frontmatter: `status: completed` ∈ `{completed, partial, aborted}` → Err #2. Terminate. Steps 4-13 skipped. No mutation of plan.md, no lockfile.

**Verbatim check**: `already completed at docs/visual-specs/2026-04-20-gongbi-poster/plan.md; branch with -v2 or pick new slug` — matches §6 row 2 byte-for-byte.

**Invariants**: S1 ✓ S2 ✓ (plan.md's existing `completed` left untouched), S3 ✓ S7 ✓.

#### Case N3 — PASS
**Fixture**: design.md `status: resolved`, schema_version `"0.1"`, `domain: poster` (valid), `tradition: made_up_school` (NOT in registry, NOT null).

**Phase walk**: Step 6 `list_traditions()` → `made_up_school` ∉ keys AND ≠ YAML null → Err #4. Terminate. Steps 7-13 skipped.

**Tool calls**: `list_traditions()` fires (registry read, not pixel tool). No pixel tools.

**Verbatim check**: `design.md frontmatter violation: tradition made_up_school invalid. Re-run /visual-spec 2026-04-23-N3 to fix.` — matches §6 row 4 byte-for-byte. "Do not auto-retry" honored.

**Invariants**: S1 ✓ S2 ✓ S3 ✓. **Minor ambiguity**: §6 row 4 covers both `tradition` and `domain` violations; skill places them in separate steps. Strict reader hitting both at once: implicit precedence "step 6 first". Worth one-liner clarification.

#### Case N4 — PASS
**Fixture**: plan.md at `status: draft`, mid-Phase 2, turn counter = 2 of cap 5. User message: `just generate it now`.

**Phase walk**: Phase 2 step 4 pixel-action-request bucket → Err #8 decline. Counter STAYS at 2 (not 3). Re-prompt main menu.

**Tool calls**: Zero. No `generate_image`, no status flip, no jsonl append, no iters dir, no plan.md rewrite (housekeeping re-Writes only on state OR counter mutation).

**Verbatim check**: `plan layer executes pixels in Phase 3 only. Complete review (accept all) first, or change spec via /visual-spec <slug>.` — matches §6 row 8 byte-for-byte.

**Invariants**: S1 ✓ (Err #8 upholds S1 parallel), S2 ✓ (status stays `draft`). **Ambiguity**: §Phase 2 step 5 "after each round" — strict-reader may re-Write on Err #8 turns. Parenthetical clarifies but bolding would harden.

#### β summary
**4/4 PASS.**

Deltas:
- D1 (N1): suppress-traceback clarification needed at step 2.
- D2 (N3): FIRST-violation precedence at step 7 worth noting.
- D3 (N4): bolden "Err #8 + deep-review-denied mutate neither state nor counter; skip Write."
- No verbatim drift — all 4 error strings byte-match §6.

### Subagent γ report (6/6 PASS)

#### Case N5 — PASS
**Fixture**: design.md with `C.sketch_integration: control` + `## References` pointing at absent sketch path.

**Phase walk**: Step 9 `Read(sketch_path)` fails → Err #9. Agent sets internal `sketch_available: false`, overrides `plan.C.sketch_integration: ignore`, queues Notes line `sketch at assets/briefs/cat-n5/sketch.png unreadable at plan time: <err>. Proceeding text-only; C.sketch_integration forced to "ignore".`. Steps 10-13 CONTINUE.

**Invariants**: S1 ✓ S2 ✓ S4 ✓. Terminal: CONTINUES (correct — Err #9 is "degrade, continue").

#### Case N6 — PASS
**Fixture**: `## A.` fenced YAML block contains duplicate `seed` key.

**Phase walk**: Step 8 `yaml.safe_load(allow_duplicate_keys=False)` raises ConstructorError → Hard-reject rule → Err #10. Terminate.

**Verbatim check**: `design.md parse-fail at <slug>: <issue>. Re-run /visual-spec <slug> to regenerate.` — byte-match §6 row 10.

**Invariants**: S1 ✓ S2 ✓. Terminal: TERMINATE (Err #10 "do NOT auto-retry").

#### Case N7 — PASS
**Fixture**: No plan.md (first invocation). Lockfile `started_at_iso` = now-400s. jsonl mtime = now-350s. Both stale.

**Phase walk**: Step 3 no plan.md → Err #3 branch skipped. Step 4 lockfile + jsonl stale → Err #12 auto-recover. `os.unlink(lock_path)` silently, append Notes `[stale-lock-recovery] previous pid <N> abandoned at <iso>; reclaimed at <now>. Resuming from iter <K>.`. CONTINUE. Phase 4 handoff gets `(recovered from stale lock at iter <K>)` suffix.

**Invariants**: S1 ✓ S2 ✓ S5 ✓ (unlink + Notes append), S6 ✓ (Notes channel, NOT stderr per §6 row 12 `NOT stderr`). Terminal: CONTINUES.

#### Case N8 — PASS
**Fixture**: Phase 3 iter 2 dispatch fails — `generate_image` raises ProviderUnreachable. Err #5 hands off to Err #13 per §6 row 5.

**Phase walk**: Agent prints Err #13 verbatim 3-option prompt. Turn NOT charged. User picks `(c) accept partial`. `_terminate_phase3(status="partial", at_iter=2)`. Phase 4 renders partial results; handoff variant 5 fires.

**Verbatim check**: `<current> unreachable, failover to <alt> requires cross-class switch (local→cloud or reverse). Approve? (a) yes / (b) no, abort / (c) no, skip remaining iters as partial` — byte-match §6 row 13.

**Invariants**: S1 ✓ (Phase 3 whitelist), S2 ✓ (`running → partial` via explicit user `(c)` trigger is valid terminal).

**Delta**: brief described "soft gate threshold elevated to hard mid-session" as Err #13 trigger. That reading inconsistent with spec — Err #13 fires ONLY on provider-unreachable + provider cross-class (local↔cloud). Gate-class change is Phase 2 `change D.L_N` sub-dialog outcome, no Err fires. γ scored per provider-unreachable reading (what §6 enforces).

#### Case N9 — PASS
**Fixture**: cwd = `/tmp/random-dir`; no `src/vulca/`.

**Phase walk**: Step 0 `Path("src/vulca").is_dir()` → False → Err #14. Terminate.

**Verbatim check**: `not inside a Vulca checkout; /visual-plan requires repo presence at cwd. cd into your vulca repo and retry.` — byte-match §6 row 14.

**Tool calls**: None. No pixel tools.

**Invariants**: S1 ✓ S2 ✓.

#### Case N10 — PASS
**Fixture**: design.md frontmatter `schema_version: "0.3"`.

**Phase walk**: Step 5 `"0.3"` ∉ supported set `{"0.1"}` → Err #15. Terminate.

**Verbatim check**: `design.md schema_version 0.3 not recognized; upgrade /visual-spec (pip install --upgrade vulca) or pin vulca@<compatible>.` — byte-match §6 row 15.

**Invariants**: S1 ✓ S2 ✓. Terminal: TERMINATE + do-NOT-auto-retry + do NOT suggest /visual-spec re-run.

#### γ summary
**6/6 PASS.**

Deltas:
1. N8 brief mis-framing: task described Err #13 as gate-class transition; §6 row 13 strictly governs provider cross-class. Resolved per verbatim string. Worth tightening brief wording for future Layer B runs.
2. Err #9 Notes-string byte-match §6 row 9.
3. N7 silence rule well-specified; SKILL.md `NOT stderr` vs spec `no stderr print` — semantic match not byte-match on explanatory parenthetical, but `Print exactly:` contract only governs user-facing strings.

## Deltas (aggregated non-blockers for v0.17.8 clarity patch)

1. **Phase 1 step 2 / N1**: add "on `FileNotFoundError`, catch and emit Err #1 verbatim before any Python traceback" one-liner to harden against strict-reader trace-leak.
2. **Phase 1 step 7 / N3**: clarify "report the FIRST violation encountered (tradition → domain); do not concatenate" for the Err #4 dual-field case.
3. **Phase 1 step 3+4 / P2-adjacent**: specify behavior for Err #3 + fresh-lockfile (mid-run crash scenario) — current implicit rule is "fire Err #11 and block resume", which is correct per S5 letter but worth documenting explicitly.
4. **Phase 2 step 4 / N4**: bold the "Err #8 and deep-review-denied-second-call mutate neither state nor counter; skip Write" parenthetical to prevent strict-reader from re-Writing plan.md on no-op turns.
5. **§Phase 2 step 5 / α**: define "compact form" (skill refers to compact rendering when no section mutated, term is undefined).

None of these are structural defects. All are wording-tightenings that affect strict-reader edge cases; mechanical flow is sound.

## Conclusion

**Layer B simulated ship-gate v1: 14/14 PASS across 3 parallel subagents (α 4, β 4, γ 6).**

- All verbatim `Print exactly:` strings (Err #1, #2, #4, #8, #10, #11, #13, #14, #15) byte-match spec §6.
- S1 pixel-tool whitelist discipline holds across every phase in every case (no pixel tool fires in Phase 1/2/4 error paths; Phase 3 whitelist honored).
- S2 status-transition discipline holds (status flips only on explicit `accept all` for draft→running, explicit user `(c)` for running→partial, explicit finalize rule for running→completed).
- S4 design.md immutability holds (N11 confirmed no `Write` to design.md during user_elevated sub-dialog; P1/P2/P3 confirmed per-iter hash guard).
- S5 lockfile O_CREAT|O_EXCL semantic holds (P3 refuses concurrent; N7 stale auto-recovers via Notes channel, not stderr).

5 deltas logged as non-blocking clarity items for /visual-plan v0.17.8 follow-up patch; they do not affect mechanical flow correctness.

**Layer B v1 verdict: GREEN. Advance to Task 9 Layer C live ship-gate v2 (v0.17.6 MCP extension precondition satisfied — shipped 2026-04-23 at tag `v0.17.6`).**
