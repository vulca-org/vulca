# `/visual-plan` Live Ship-Gate Log (v2)

**Date:** 2026-04-23
**Parent log:** `docs/superpowers/plans/visual-plan-ship-gate-log.md` (v1 simulated, 14/14 PASS)
**Scope:** Close integration-path gaps v1 simulated over — real `generate_image(mock)` timing, real `evaluate_artwork` return shape, real filesystem for lockfile + jsonl + plan.md I/O.

## Gap-to-case mapping

| # | Parent v1 simulated gap | v2 case | Subagent | Verdict |
|---|---|---|---|---|
| 1 | `generate_image(mock)` actually running → mock latency + real return | P1-live | α | PASS* |
| 2 | `evaluate_artwork` actually returning `dimensions` → L1-L5 extraction | P1-live | α | PASS |
| 3 | jsonl actual append-only write + read atomicity | P1-live | α | PASS |
| 4 | Real filesystem lockfile O_CREAT \| O_EXCL collision | β-lockfile | β | PASS |
| 5 | Real filesystem stale-lock auto-recovery + Notes append | β-stale-lock | β | PASS |
| 6 | Real Err #16 design-drift content-guard | β-drift | β | PASS |

**Aggregate: 6/6 gaps closed across 4/4 cases PASS.** (*Gap 1 surfaced a v0.17.6 integration gap logged below; skill-body flow correct, MCP-wrapper echo lossy.)

## Protocol

Mirrors /visual-spec v2 pattern. 2 parallel subagents. Subagent α runs in parent Claude Code session (has MCP tool access via `PYTHONPATH=src`). Subagent β dispatches MCP via shell `PYTHONPATH=src python3.11 -c ...` (subagent-dispatch caveat from v2 learning).

Tmp write paths: `tmp-shipgate-v2-plan/docs/visual-specs/<slug>/` (repo-relative; `/tmp/...` sandbox-denied per /visual-spec v2 precedent).

Tool whitelist: `list_traditions`, `get_tradition_guide`, `Read`, `Write`, `generate_image(provider="mock")` only, `evaluate_artwork`, MAY `unload_models`. Pixel-level tools banned.

## Results

### Subagent α report (live) — Case P1-live 3-iter full positive flow

#### Setup
- **tmp workspace:** `/Users/yhryzy/dev/vulca/tmp-shipgate-v2-plan/docs/visual-specs/live-p1/`
- **design.md:** 1588B, frontmatter {slug=live-p1, status=resolved, schema_version="0.1", domain=poster, tradition=chinese_gongbi}; body A/B/C/D1/D2/F (no E spike). D1 weights mirror real registry: L1=0.15, L2=0.30, L3=0.25, L4=0.15, L5=0.15. All D2/F thresholds `source: measured`.
- **cwd during Phase 1:** `/Users/yhryzy/dev/vulca` (the real repo root). Per brief option (a): running skill from repo root while referencing tmp-prefixed slug paths. Step 0 `Path("src/vulca").is_dir()` = TRUE at cwd.

#### Phase 1 live results
- Steps 0-13 all passed. `list_traditions()` returned 13 traditions incl. `chinese_gongbi`. Domain `poster` in 7-enum.
- Lockfile created at `.../live-p1/plan.md.lock` via `os.open(... O_CREAT|O_EXCL|O_WRONLY)`; body `{pid:45545, started_at_iso:2026-04-23T18:56:47Z, design_ref:<abs path>}`.
- plan.md draft at `.../live-p1/plan.md` (1593B, status=draft, all `reviewed: false`).

#### Phase 2 live results
- Simulated user reply `accept all` on turn 1. Handler flipped every `reviewed: false → true` and `status: draft → running`. Re-wrote plan.md (1589B). Turn cap unused (4 remaining).

#### Phase 3 live results (per iter)
All three iters identical due to mock determinism (mock evaluator returns static 0.85/0.80/0.90/0.83/0.88).

- **Iter 0:** seed=1337. `generate_image` → `image_path=.../iters/1337/gen_bad337d4.png` (2203B, real file), latency_ms=10, cost_usd=0.0, provider=mock. `evaluate_artwork` → dimensions {L1:0.85, L2:0.80, L3:0.90, L4:0.83, L5:0.88}. weighted_total=0.8490. verdict=**accept**. jsonl row appended.
- **Iter 1:** seed=1338. image_path=.../1338/gen_2011d92d.png, latency_ms=1. Same scores, verdict=accept.
- **Iter 2:** seed=1339. image_path=.../1339/gen_d632a151.png, latency_ms=1. Same scores, verdict=accept.
- **fail_fast_counter trace:** `0 → 0 → 0 → 0` (reset on every accept). soft_gate_warn_count=0 throughout. No Err #7 fired.

#### Phase 4 live results
- **Terminal status:** `completed` (all 3 verdict=accept, zero soft warnings).
- **Handoff string:** `Plan /visual-plan/live-p1 completed. 3 images at docs/visual-specs/live-p1/iters/.` — **byte-match PASS** against §Handoff row 1.
- **Archive rename:** `plan.md.results.jsonl → plan.md.results.jsonl.archive` succeeded (1841B, 3 canonical rows, CJK `\u`-escaped).
- **Lockfile unlink:** confirmed absent via `ls` exit-1.
- **Final plan.md:** 2084B at `.../live-p1/plan.md`, sha256 prefix `74041985d1ec`. S4 assertion passed.

#### Gap closures

- **Gap 1 (mock echo): PASS* (integration-gap flagged)**
  Evidence: `generate_image(provider="mock")` returned exactly `["image_path","cost_usd","latency_ms","provider"]` — no `metadata`, no `candidate_id`, no `seed`/`steps`/`cfg_scale` echo. The MCP tool (`src/vulca/mcp_server.py:1216-1221`) only surfaces those 4 fields; it drops `result.metadata` except for internal `cost_usd` extraction. The v0.17.6 mock-provider *internally* populates metadata (per `tests/test_generate_image_extended_signature.py::test_mock_provider_echoes_all_four_kwargs_in_metadata`), but the MCP wire contract discards it.
  **v0.17.8 candidate / v0.17.6 integration gap:** either `mcp_server.py` should surface `metadata`, OR the skill text should stop assuming echo is available. Currently the skill body doesn't *require* the echo for Phase 3 correctness (seed/steps/cfg_scale stored in plan.A locally), so this is cosmetic — but any future feature relying on MCP-echoed metadata will fail. The v0.17.6 direct-provider test PASSES because it tests the `MockImageProvider().generate()` layer, not the MCP wrapper; this v2 gate reveals the wrapper-level drop.

- **Gap 2 (dimensions vs L1_L5): PASS**
  Evidence: `evaluate_artwork(mock=True)` returned `dimensions` as a **flat `{L1: 0.85, L2: 0.80, ...}` dict of floats** — NOT the `{L1: {score: 0.8, ...}}` nested-dict shape that α initially expected. The skill body at §Phase 3 lines 253-257 says *"Map the 5 L scores out of the dimensions dict (keys are rubric names per tradition)"* which is ambiguous but compatible with flat floats. α's extractor handled both shapes defensively.
  **v0.17.8 candidate:** SKILL.md should pin the exact shape with an inline example, e.g. `# dimensions format: {"L1": 0.85, ...} when mock=True; {"L1": {"score":0.85, "rationale":...}} when live`. The JSONL row schema `"l_scores": {"L1":0.78,...}` (line 303) already expects flat floats — the extractor must therefore unwrap `.score` ONLY when nested.

- **Gap 3 (jsonl atomicity): PASS**
  Evidence: 3× `open(path,'a') + write(json.dumps(row)+"\n")` yielded a 3-line NDJSON file. Readback `[json.loads(l) for l in content.splitlines() if l.strip()]` recovered 3 dicts with `iter=[0,1,2]` monotonic. `json.dumps(..., ensure_ascii=True, separators=(",",":"))` emitted `\uXXXX` CJK escapes as specified. File on-disk is grep-safe, one row per line.

#### α summary
- **PASS count:** 1/1 case (P1-live 3-iter full positive flow).
- **Real latencies observed:** `per_gen_sec` = 10ms, 1ms, 1ms (mock provider). Total wall_time = 0.012s vs budgeted 10s → overage_pct = -99.88%. F ledger renders negative overage without truncation (cosmetic nit).
- **v0.17.8 clarity-gap candidates flagged:**
  1. **MCP `generate_image` `metadata` dropped** (load-bearing integration gap vs cosmetic; Gap 1 above).
  2. **`evaluate_artwork` dimensions shape** — lock flat-float vs nested-dict contract with inline example (Gap 2 above).
  3. **Slug path resolution** — skill assumes `docs/visual-specs/<slug>/` relative to cwd=vulca-root. Tmp/alternate-workspace users have no documented path (α worked around with absolute paths). Consider accepting absolute slug paths or a `--workspace` knob.
  4. **F.overage_pct formatting** — negative overages render as `-0.9988` unformatted; Phase 4 renderer could clamp display at `>= 0.0` or emit `"under budget"`.
  5. **Step 13 initial write vs Phase 2 redundancy** — Phase 1 step 13 *and* Phase 2 step 2 both `Write(plan.md, status=draft)`. Second write is redundant unless F-summary mutated state. Minor.

### Subagent β report (live) — 3 filesystem cases

#### Case β-lockfile — PASS
- Fixture steps executed: created `live-p3/` tmp workspace, wrote design.md (slug=live-p3, status=resolved), pre-created fresh lockfile with peer pid 99999 + `started_at_iso=now`, touched jsonl with recent mtime.
- Error raised: FileExistsError? **y** — `os.open(lock, O_CREAT|O_EXCL|O_WRONLY)` raised immediately.
- Err #11 verbatim byte-match: **PASS**. Rendered: `live-p3 currently running (pid: 99999, started: 2026-04-23T15:30:14Z). Abort the other session first, or wait and retry.` — matches SKILL.md §Error matrix row 11 template character-for-character.
- S5 discipline: no unlink attempted? **PASS** — lockfile.exists() remained True throughout; agent refused without mutating the peer's lock (S5 "fresh → Err #11 refuse, do not kill other pid").

#### Case β-stale-lock — PASS
- Fixture steps: `live-n7/` workspace, design.md written, lockfile with `started_at_iso` = `now - 400s` (pid 88888), jsonl pre-created and `os.utime`'d to `now - 350s`.
- Stale-detection branch fired: `lock_age > 300s AND jsonl_age > 300s` → True.
- `os.unlink(lock_path)` succeeded; post-unlink recreate via `O_CREAT|O_EXCL` also succeeded (proving the unlink was real and O_EXCL saw a clean path).
- Notes line written (not stderr): **PASS** — written to `plan.md ## Notes`: `[stale-lock-recovery] previous pid 88888 abandoned at 2026-04-23T15:23:34Z; reclaimed at 2026-04-23T15:30:14Z. Resuming from iter 0.` — byte-for-byte matches the SKILL.md §6 row 12 template (K=0 since no prior jsonl rows).
- Err #12 "no user prompt, NOT stderr" clause honored: **PASS** — nothing written to sys.stderr; no user prompt emitted; recovery was silent as §6 row 12 mandates.

#### Case β-drift — PASS
- design_hash before: `9db0a3fdaca83a9037b0454621cc9fbfa89c7fd1b2ad64e6bb17977c86b274f3`
- design_hash after:  `a332bb72faf29c03572d3569367ddbd8d71ecf7b649f4b55e6566e45d567665c`
- (drift bytes: `seed: 1337` → `seed: 9999`)
- Err #16 verbatim byte-match: **PASS**. Rendered at K=2 (iter 2 would have been next after 2 completed rows): `design.md mutated mid-session at iter 2; aborting. Re-run /visual-plan live-n16 to restart with new design.` — exact match to SKILL.md §Error matrix row 16.
- Status transition running → aborted (NOT partial): **PASS** — final plan.md on disk contains `status: aborted`; no `status: partial` substring present. Per §Phase 4 point 2 priority order, Err #16 sits in the `aborted` trigger list, above partial.
- Notes line written: **PASS** — `[design-drift] design.md sha256 changed between Phase 1 and iter 2; aborting.` written into `plan.md ## Notes` (also preserves prior `[resume-state]` line).
- jsonl preservation: the 2 completed rows (iter 0, iter 1) remain on disk untouched through the abort — confirming §6 row 16 "jsonl up through iter `<K-1>` preserved."

#### β summary
- PASS count: **3 / 3**
- v0.17.8 clarity-gap candidates:
  1. **Err #16 handoff-string K ambiguity.** §Handoff row 7 says `aborted by user at iter <K>`. For Err #16, is K the iter-that-would-have-run (2 in β's case) or the last-successful iter (1)? §6 row 16 uses `iter <K>` for the error print; §Phase 4 point 2 says "jsonl up through iter `<K-1>` preserved" — implying K is the aborted-iter (2). §Phase 3 pseudocode calls `_terminate_phase3(..., at_iter=iter_idx)` where `iter_idx` is the current loop index (2). All consistent — but user-facing handoff should make pre-run-K vs post-run-K-1 explicit.
  2. **Err #16 handoff variant selection underspecified.** §Handoff row 7 lumps "user interrupt / Err #13(b) / Err #16" into one variant `aborted by user at iter <K>`. But Err #16 is *not* a user action — it's a content-guard abort. Consider a dedicated 9th variant: `Plan /visual-plan/<slug> aborted at iter <K>. design.md mutated mid-session.` — lets downstream greppers distinguish drift-abort from user-interrupt.
  3. **Stale-lock K semantics when jsonl is empty.** §6 row 12 says "Resuming from iter `<K>`" — in β's case K=0 because jsonl had 0 rows. SKILL.md doesn't explicitly state K=len(completed_iters) when jsonl is empty-but-present. Harmless inference, but worth one line in §Phase 1 step 4 to lock it down.
- Skill-body wording deltas: **none observed**. Every verbatim string β rendered from SKILL.md §Error matrix templates produced byte-identical output to what a live agent would emit. Err #11, Err #12 notes line, and Err #16 all grep-contract-stable.

## Deltas (aggregated v0.17.8 candidates)

From v2 live ship-gate — 8 candidates total (5 from α + 3 from β). None blocking; ship `v0.17.7` with these in backlog for `v0.17.8` patch:

1. **MCP `generate_image` metadata dropped** (α Gap 1) — load-bearing for future agent features that want per-gen diagnostics; cosmetic now.
2. **`evaluate_artwork` dimensions shape** pin with example (α Gap 2).
3. **Slug path resolution** for non-repo-root workspaces (α).
4. **F.overage_pct negative formatting** Phase 4 render clamp (α).
5. **Phase 1 step 13 / Phase 2 step 2 redundant Write** — minor dedup opportunity (α).
6. **Err #16 handoff K pre/post ambiguity** — spec clarification (β).
7. **Err #16 handoff variant split** from user-interrupt variant (β).
8. **Stale-lock K=0 empty-jsonl rule** — one-line lock-down (β).

Plus the 5 carry-over candidates from v1 simulated (trace-leak guard, FIRST-violation precedence, Err #3+fresh-lock explicitness, Err #8 Write-suppression bolding, "compact form" definition) = **13 candidates total for v0.17.8 follow-up**.

## Conclusion

**Layer C live ship-gate v2: 6/6 gaps closed across 4/4 cases PASS.**

- Real MCP tool flow validated end-to-end: `generate_image(mock)` + `evaluate_artwork(mock=True)` via MCP produce canonical plan.md + jsonl + archive + handoff byte-identical.
- Real filesystem lockfile semantics validated (O_CREAT|O_EXCL collision refuse + stale auto-recover + Notes-not-stderr channel).
- Real Err #16 content-guard validated (sha256 drift detect + status=aborted + jsonl up-through-K-1 preserved).
- S1/S2/S4/S5/S6 invariants all hold under live execution.

**v1 simulated 14/14 + v2 live 4/4 = 18/18 cases total across non-pixel-heavy surface.** Pixel-heavy cases (live SDXL / ComfyUI / Gemini / OpenAI per-iter timing + cost tracking) deferred to post-ship user validation, consistent with /visual-spec v0.17.5 precedent.

**Layer C v2 verdict: GREEN. Advance to Task 10 v0.17.7 release chain** (PyPI + GH release + plugin sync PR #6).
