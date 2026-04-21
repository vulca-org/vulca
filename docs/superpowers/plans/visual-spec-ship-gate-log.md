# `/visual-spec` Ship-Gate Log (v1 — simulated)

**Date:** 2026-04-21
**Branch:** `master`
**Skill commit under test:** `ec709a34` (Task 1 final, 414 lines) + `72b8093f` (Task 2 pathlib fix)
**Spec reference:** `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md` §10.2
**Plan reference:** `docs/superpowers/plans/2026-04-21-visual-spec-skill.md` Task 4

## Protocol

Three parallel subagents act as "Claude Code sessions loading the skill" — each reads `.claude/skills/visual-spec/SKILL.md` verbatim and simulates both agent-following-skill and scripted user. Tool calls to `list_traditions` / `search_traditions` / `get_tradition_guide` / `view_image` / `evaluate_artwork` / `generate_image(mock)` are NOTED but not executed (subagents assume hypothetical success); pixel-level tools verified NOT called outside Phase 5 whitelist.

This is the mechanical-rule surface simulation. Integration-path regression (Layer C live ship-gate v2) is deferred to a later post-ship session.

## Case matrix

| # | Case | Subagent |
|---|---|---|
| P1 | Tradition-bearing proposal (chinese_gongbi), no spike, full derive→review→finalize | α |
| P2 | Proposal Open questions flags `spike count=3` → 3 spikes run (tools simulated) | α |
| P3 | Resume from `status: draft` + 1 un-reviewed dim | α |
| N1 | `proposal.status == draft` | β |
| N2 | `proposal.tradition = "tang_court_mural"` (not in registry) | β |
| N3 | Mid-review user says `"generate_image for me right now"` | β |
| N4 | `proposal.## References: sketch.png` but file deleted | γ |
| N5 | Same-slug design.md exists `status: resolved` | γ |
| N6 | Spike provider (ComfyUI) unreachable | γ |

## Results

<!-- Subagent reports plug in here when tasks complete. -->

### Subagent α — P1 + P2 + P3 (completed 2026-04-21)

**P1 — Tradition-bearing proposal, no spike, full derive→review→finalize: ✅ PASS**

- Phase 1: `Read(proposal.md)` → status:ready ✓, `list_traditions()` → chinese_gongbi in registry ✓, domain=poster in 7-enum ✓, no sketch.
- Phase 2: `generate_image(provider="mock")` × 1 → `t_mock=0.001s`; provider=sdxl → multiplier 20000 → `per_gen_sec=20`. User-confirm prompt printed (not cap-charged).
- Phase 3: `get_tradition_guide("chinese_gongbi")` → D1 byte-identical (0.3/0.25/0.2/0.15/0.1), no source/confidence keys on D1. E omitted (Open questions="none").
- Phase 4: 5 sub-dialog review turns, each writes draft with `turns_used:<N>` bump. No cap-hit.
- Phase 6: User "done" → `Write(design.md, status:resolved)`; handoff string printed byte-identical.
- Verified: 8 sections (A/B/C/D1/D2/F/Open questions/Notes), 8-field frontmatter, B1/S1 held (only Phase 2 mock pixel call), D1 registry-match, S4 immutable.

**P2 — Spike-flagged proposal (3 seeds): ✅ PASS**

- Phase 1-2 identical to P1. Open questions parses "- spike:" → E section emitted.
- Phase 3 E block: `spike_requested: true`, `spike_count: 3`, `judgment_criterion: "pick seed where L3>=0.6 AND L2>=0.65"`, `results: []`, `status: pending`.
- Phase 4: 5-turn review (all accept).
- Phase 5 (not cap-charged): seeds 1337/1338/1339 per default A.seed+N walk. Per seed: `generate_image(provider="sdxl", ...)` + `evaluate_artwork(tradition="chinese_gongbi")`. Fabricated L1-L5 scores: seed 1337 rejected (L3=0.55 fail), seed 1338 accepted (L3=0.62, L2=0.68), seed 1339 rejected (L3=0.58 fail). E.status=complete. `unload_models()` noted after.
- Phase 6: finalize.
- Verified: 9 sections (E present with 3 results rows), Phase 5 whitelist respected (only generate_image/evaluate_artwork/unload_models), zero pixel calls in Phase 1/3/4/6.

**P3 — Resume from `status: draft` + 1 reviewed dim: ✅ PASS**

- Phase 1: same-slug design.md status=draft detected → Err #3 resume.
- `Read(design.md)` → `[resume-state] turns_used: 2`; D2.reviewed=true, others false. Counter initialized to 2.
- Phase 2 re-runs mock calibration (no resume-skip rule; acceptable per skill).
- Phase 3 idempotent D1 re-derivation; D2 preserved with reviewed=true.
- Phase 4: 5 dims to review (A/B/C/D1/F). Turns 3-5 accept A/B/C. At turn 5 cap-hit → force-show + prompt "Turn cap reached. finalize or deep review?". User "deep review" → cap 5→8. Turns 6-7 accept D1/F. User "finalize" at turn 8.
- Phase 6: finalize; `created:` preserved from original draft; `updated: 2026-04-21`; handoff printed.
- Verified: turn counter accumulated (not reset), cap-hit at 5 (per skill, not at 3 per brief math), deep-review extension to 8, S2 held (no auto-advance).

---

### Subagent β — N1 + N2 + N3 (completed 2026-04-21)

**N1 — proposal.status == draft → Err #1 terminate: ✅ PASS**

- Phase 1 step 2 assertion fires; verbatim Err #1 printed: `proposal.md not found or status != ready at <path>. Run /visual-brainstorm <slug> first.` (SKILL.md:375)
- Only `Read(proposal.md)` before terminate; no list_traditions, no Write.
- "Do NOT auto-retry" footer honored.

**N2 — Unknown tradition `tang_court_mural` → Err #4 schema violation: ✅ PASS**

- `list_traditions()` called for registry check. Tradition not in keys, not YAML null, not forbidden-string.
- Verbatim Err #4 printed: `proposal.md frontmatter violation: tradition tang_court_mural invalid. Re-run /visual-brainstorm <slug> to fix.` (SKILL.md:378)
- Terminate; no auto-retry; no fuzzy search via search_traditions.

**N3 — Mid-review pixel action request → Err #8 decline, turn NOT charged: ✅ PASS**

- User "Just generate_image for me right now" at turn 3.
- Verbatim Err #8 printed: `spec layer doesn't execute pixels outside spike. Spike plan is determined by proposal's ## Open questions; run /visual-plan after finalize to execute.` (SKILL.md:382)
- B1/S1 held: no generate_image called.
- Turn counter stays at 3 (Err #8 "Turn NOT charged" footer).
- Review loop continues on next user message.

---

### Subagent γ — N4 + N5 + N6 (completed 2026-04-21)

**N4 — Sketch unreadable at spec time → Err #9 degrade + continue: ✅ PASS**

- Phase 1 step 6 Read(sketch) fails. Err #9 fires; sets internal `sketch_available: false`.
- Notes queued for Phase 4 draft render: `sketch at <path> unreadable at spec time: <err>. Proceeding text-only; C.sketch_integration forced to "ignore".` (SKILL.md:383)
- Phase 2/3/4/6 all run; C.sketch_integration value = `ignore` in final design.md.
- No abort.

**N5 — Same-slug resolved design.md → Err #2 refuse-overwrite: ✅ PASS**

- Phase 1 step 3 detects collision. Verbatim Err #2: `already finalized at <path>; branch with -v2 or pick new slug` (SKILL.md:376) with `<path>` substituted.
- File mtime unchanged (no Write fires).
- S2 + S4 held trivially (no write = no possible mutation).

**N6 — Spike provider unreachable → Err #5 skip + continue: ✅ PASS**

- Phase 5 loop catches unreachable for `{"error": "ComfyUI not reachable at http://localhost:8188"}` → Err #5 (not Err #6).
- E.status: skipped (not failed); skip_reason captured. 1-liner logged to ## Notes.
- Main flow continues to Phase 6 finalize; D2/F unaffected.
- Final design.md: 9 sections (E present with status:skipped).

---

## Deltas + invariants

**Three real skill-body drifts surfaced (non-blocking; noted for future patch)**:

1. **Err #9 wording drift** — Error matrix row 383 says `"unreadable at spec time"`; Notes template bullet at SKILL.md:261 says `"unreachable at spec time"`. Agents copying from the Notes template may write a slightly different string than Err #9 prescribes. Recommend normalizing to `"unreadable"` (matches FileNotFoundError/permission-denied semantics; "unreachable" implies network).

2. **Err #5 vs #6 judge-by-shape gap** — Both matrix rows treat "error dict" as their trigger. A strict dict-shape reader could mis-route an unreachable-phrased error dict to #6. Recommend tightening: classify by error content semantics (unreachable / timeout / 401 → #5; validation / OOM / malformed param → #6), not by return shape.

3. **P1 provider bare `sdxl` vs multiplier table** — skill multiplier table lists `sdxl-mps` / `sdxl-cuda`, not bare `sdxl`. Strictly this triggers the unknown-provider fallback rule (SKILL.md:56). For proposals generated by brainstorm that name `provider: sdxl` without qualifier, the fallback fires on every invocation. Not a correctness issue (fallback is correct degrade); just a UX papercut.

**Brief-side note (not a skill issue):** my subagent brief for β contained a paraphrase of Err #8 (`"Spec execution is determined by..."`) that diverged from skill's verbatim (`"Spike plan is determined by..."`). Subagent correctly followed skill as authoritative. No skill change needed.

**Invariants verified across all 9 cases**:
- **B1/S1** — zero pixel-tool calls outside Phase 2 mock + Phase 5 spike whitelist. No `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*` called anywhere.
- **S2** — no status auto-flip. P3 cap-hit correctly prompts rather than auto-finalizing.
- **S4** — tradition immutable across all cases; write-time assert holds.
- **Handoff string** — byte-identical `Ready for /visual-plan. Run it with /visual-plan <slug>.` in all positive cases (P1/P2/P3).
- **Err matrix grep-compatibility** — all verbatim strings backtick-wrapped and byte-identical per SKILL.md §Error matrix row contract.
- **Do-not-auto-retry** footer honored for Err #1 (N1), Err #4 (N2), Err #7 (not triggered but documented).
- **Decline-without-charge** footer honored for Err #8 (N3).
- **Degrade-and-continue** footer honored for Err #5 (N6), Err #6 (not triggered but documented), Err #9 (N4).

## Conclusion

**Ship-gate v1 GREEN.** Skill body at commit `ec709a34` (Task 1 final) + `72b8093f` (Task 2 pathlib fix) is spec-compliant across 9/9 mechanical-rule surface cases. 3 real wording-drift items logged for future clarity patch (non-blocking). Brief-side paraphrase (Err #8) did NOT manifest in skill; skill is authoritative.

Proceeding to Task 5 (release chain) + Task 6 (plugin mirror). Layer C live ship-gate v2 deferred post-ship per spec §10.3.

## Subagent transcripts (session-local)

- α (P1+P2+P3): `/private/tmp/claude-501/-Users-yhryzy-dev-vulca/c6312a8d-2d94-418e-8ead-797850871982/tasks/a346181b0761d2b7d.output`
- β (N1+N2+N3): `/private/tmp/claude-501/-Users-yhryzy-dev-vulca/c6312a8d-2d94-418e-8ead-797850871982/tasks/aefb362d1b01d2a92.output`
- γ (N4+N5+N6): `/private/tmp/claude-501/-Users-yhryzy-dev-vulca/c6312a8d-2d94-418e-8ead-797850871982/tasks/a74610078591feac3.output`

Paths are session-local; summary above is the durable record.
