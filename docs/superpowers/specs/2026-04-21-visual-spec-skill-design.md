# `/visual-spec` Skill — Design Spec

**Date:** 2026-04-21
**Status:** Design locked after brainstorm session (6 clarifying Q's → Q1-Q6 with 1 Y-override + α artifact choice → 5 design sections all user-approved) + parallel review round (codex:codex-rescue + superpowers:code-reviewer — SP CONDITIONAL-APPROVE, 9 findings folded into this v2 locked spec).
**Parent sibling:** [`2026-04-21-visual-brainstorm-skill-design.md`](./2026-04-21-visual-brainstorm-skill-design.md) (shipped v0.17.4, 2026-04-21).
**Follow-up:** implementation plan at `docs/superpowers/plans/2026-04-21-visual-spec-skill.md` (next, via `superpowers:writing-plans`).

This spec is for the **shipped skill artifact** (`.claude/skills/visual-spec/SKILL.md`). Per the sibling spec's discipline, the skill file itself will contain zero "future / later / expand" phrasing — deployed artifact is not a roadmap. Y-future thinking lives only in this spec and the follow-up plan doc.

---

## 1. Purpose, scope, positioning

### 1.1 Purpose

`/visual-spec` is the **second member** of the 3-layer meta-skill architecture `brainstorm → spec → plan → execute`. It turns a reviewable `proposal.md` (produced by `/visual-brainstorm`) into a resolved `design.md` that a downstream `/visual-plan` can turn into concrete execution steps.

```
/visual-brainstorm  →  /visual-spec  →  /visual-plan  →  execute
  (intent)             (technical      (steps)          (pixel tools)
                        decisions)
```

### 1.2 Scope

**In-scope**: any `proposal.md` at `docs/visual-specs/<slug>/` with `frontmatter.status == ready` produced by `/visual-brainstorm` at v0.17.4 or later. The skill resolves 7 technical dimensions (A through F below) + optional spike execution when proposal explicitly flagged it in `## Open questions`.

**Out-of-scope** (hard reject):
- Any `proposal.md` with `status: draft` — run `/visual-brainstorm <slug>` to finalize first (Err #1).
- Proposals whose `frontmatter.tradition` is not in `list_traditions` registry AND is not literal YAML `null` — schema violation, fix at proposal (Err #4).
- Multi-proposal batch runs — one `/visual-spec` invocation, one slug. Parallel same-slug calls rejected (S5).

### 1.3 Positioning vs sibling skills

- vs `/visual-brainstorm` (sibling): brainstorm produces fuzzy→reviewable intent; `/visual-spec` produces reviewable→resolved technical plan. Different weight classes (see §11 weight-class table).
- vs `/visual-plan` (not yet designed): `/visual-spec` locks decisions; `/visual-plan` turns decisions into ordered execution steps. The Section 3 YAML schema here is a **proposal**, not a parser contract, until `/visual-plan` is designed (see Section 3 header disclaimer).

---

## 2. Input / output contracts

**Input** (required):
- `docs/visual-specs/<slug>/proposal.md` with `frontmatter.status == ready`

**Input** (optional — per-invocation flags):
- `--budget-per-gen <seconds>` — user-supplied value to skip F calibration
- `--dry-run` — run Phase 1-3, render draft to stdout, do NOT write to disk (review-only mode, never flips status)

**Output** (single artifact per α decision):
- `docs/visual-specs/<slug>/design.md` with `frontmatter.status == resolved` and 9 markdown sections (or 8 if no spike)

**Handoff**: on finalize, skill prints exactly:

```
Ready for /visual-plan. Run it with /visual-plan <slug>.
```

(String is verbatim per §Handoff convention; downstream tooling may grep.)

---

## 3. Architecture

```
USER: /visual-spec <slug>
  │
  ▼
Phase 1: Precondition gate
  - Read proposal.md; assert: status == ready, tradition ∈ registry ∨ null,
    domain ∈ 7-enum
  - Capture tradition (immutable per S4)
  - Check sketch readability (set sketch_available state per Err #9)
  - Errors: #1 (not-found / draft), #4 (schema violation)
  ↓
Phase 2: F calibration (pre-cap — does NOT count toward turn budget)
  - If user supplied --budget-per-gen: skip calibration
  - Else: run 1 × generate_image(provider="mock") to measure baseline
  - Multiply by provider-type factor (§6.5 table)
  - Propose F values; ONE user confirmation (pre-cap)
  ↓
Phase 3: Dimension derivation (pre-cap)
  - D1 (mechanical): copy from get_tradition_guide(tradition).weights
  - A / B / C / D2 (derived): agent reasoning from proposal + tradition guide
  - E (conditional): generate only if proposal.## Open questions flags a spike
  - All numeric fields in D2 / F carry {value, source, confidence} metadata
  ↓
Phase 4: Derive-then-review loop (hard cap 5 / "deep review" → +3, max 8)
  - Render full draft design.md with all 7 dims pre-filled
  - User: "accept all" / "change <dim>" per round
  - Overrides logged to ## Notes per S6
  ↓
Phase 5: Spike execution (conditional — only if E section active)
  - Whitelist lifts: generate_image (provider per A), evaluate_artwork
  - Run N spikes per proposal flag → results to E
  - MAY call unload_models after (memory hygiene)
  - Failures: Err #5 (provider down) / Err #6 (gen error) — continue
  ↓
Phase 6: Finalize + handoff
  - Triggers: finalize / done / ready / lock it / approve (superset of brainstorm)
  - status: draft → resolved
  - updated: today; created: unchanged (S2 / S4)
  - Write docs/visual-specs/<slug>/design.md
  - Print verbatim handoff string
  ↓
OUTPUT: docs/visual-specs/<slug>/design.md (status: resolved)
```

---

## 4. Components — per-phase tool whitelist + cap accounting

| # | Phase | Tool whitelist | Counts toward cap? | Primary enforce class |
|---|---|---|---|---|
| 1 | Precondition gate | `Read` (proposal.md, optional tradition-yaml) | No | helper |
| 2 | F calibration | `generate_image(provider="mock")` × 1 (if no `--budget-per-gen`); user Q to confirm F | No (explicitly excluded) | helper + prescription |
| 3 | Dimension derivation | `get_tradition_guide` / `list_traditions` / `search_traditions` / `view_image` (proposal sketch only — sketch-eval exemption) | No | helper + prescription |
| 4 | Derive-then-review loop | Same as Phase 3; no spike tools | **Yes** — each user-facing prompt = 1 turn | prescription |
| 5 | Spike execution *(conditional)* | Whitelist lifts: `generate_image(provider per A)`, `evaluate_artwork`, MAY `unload_models` after | No | prescription |
| 6 | Finalize + handoff | `Write` (design.md) | No | helper + prescription (verbatim handoff) |

**Hard cap**: 5 review turns. **Soft extension trigger**: user says `"deep review"` → +3, max 8. **Cap-hit behavior**: force-show full current draft + `"finalize or deep review? (deep review extends +3)"`.

**Forbidden across all phases** (S1 baseline): `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*`. These belong to `/visual-plan` execution layer, not spec layer.

---

## 5. The 7 dimensions

design.md has 9 sections = 7 dimensional sections + 2 supplementary (`## Open questions` + `## Notes`). When E is not triggered, design.md has 8 sections.

| Dim | Content | Derivation class | Data format |
|---|---|---|---|
| **A** | Provider + generation params (tool / seed / steps / cfg) | Derived from proposal + tradition + available providers | Flat YAML, `source: derived\|assumed`, confidence |
| **B** | Composition strategy (single / layer_decompose / series) | Derived from proposal "single vs series" answer | Flat YAML |
| **C** | Prompt composition (base / negative / tradition tokens / color tokens / sketch integration) | Derived from proposal intent + `get_tradition_guide` terminology | Flat YAML with string fields |
| **D1** | L1-L5 weights | **Mechanical** — `get_tradition_guide(tradition).weights` byte-for-byte copy | Flat YAML, no source/confidence (registry-authority asymmetry) |
| **D2** | Thresholds + batch + rollback | **Per-session judgment** — default proportional to D1; user MAY override | `{value, source, confidence}` triple per numeric field |
| **E** | Spike plan + results | **Conditional** — only if proposal `## Open questions` flags spike | Object YAML with `results[]` array |
| **F** | Cost budget (per-gen + total + fail-fast) | **Per-session calibration** — Phase 2 measurement × provider multiplier | `{value, source, confidence}` per numeric; `source: measured` requires Phase 2 ran |

Plus 2 supplementary sections:
- `## Open questions` — for `/visual-plan`; literal `none` if all resolved
- `## Notes` — free-form audit trail; override rationales per S6; Err #5 / #6 / #9 degrade logs

---

## 6. Data flow + fenced YAML schema (proposal — see disclaimer)

### 6.1 Schema disclaimer (finding 3)

> *Parser contract is NOT locked. The fenced YAML schema below is the current proposal; `/visual-plan` does not exist yet. Downstream tooling MUST NOT rely on key ordering or nesting until `/visual-plan` is designed and this Section 6 is confirmed against its parser needs. Schema MAY shift once the consumer is designed.*

### 6.2 Source + confidence semantics

| `source` | Meaning | `/visual-plan` treatment |
|---|---|---|
| `measured` | Actually ran a measurement this session (F calibration, evaluate_artwork on sketch, spike gen) | MAY treat as hard gate |
| `derived` | Mechanical formula from other measured/registry values (e.g., `total = per_gen × batch × margin`) | MAY treat as hard gate **with explicit rationale check** |
| `assumed` | Agent judgment, no measurement backing | **MUST NOT** treat as hard gate; starting point only |

| `confidence` | Implication |
|---|---|
| `high` | Calibrated or registry value; downstream trusts |
| `med` | Formula-derived from high-confidence inputs |
| `low` | Agent inference; downstream should verify |

### 6.3 Per-dim schema

**Common per-dim preamble rule**: every dim-level fenced block (A / B / C / D1 / D2 / E / F) MUST carry a `reviewed: true | false` key at the top, set by Phase 4 on user "accept" or "change <dim>" per round. This is the progress-tracking mechanism for Err #3 resume path (per codex round-2 finding 3 — D2's `override_rationale` is not a reliable progress signal since other dims have no such field).


```yaml
# ## A. Provider + generation params
provider: sdxl                     # source: derived, confidence: med
seed: 1337                         # source: assumed, confidence: low
steps: 30                          # source: derived, confidence: med
cfg_scale: 7.5                     # source: derived, confidence: med
```

```yaml
# ## B. Composition strategy
strategy: single                   # enum: single | layer_decompose | series
variation_axis: null               # MUST be non-null string (e.g., "zodiac_animal", "season") if strategy=series; MUST be null otherwise
variant_count: 1                   # MUST match proposal's declared count
```

```yaml
# ## C. Prompt composition
base_prompt: "..."
negative_prompt: "..."             # SDXL/ComfyUI only; "" for gemini/openai
tradition_tokens:                  # from get_tradition_guide.terminology (MECHANICAL copy)
  - "gongbi 工笔"
  - "xuan paper 宣纸"
color_constraint_tokens:
  - "cinnabar red 朱砂红"
sketch_integration: control        # enum: ignore | reference | control | composite
ref_integration: none              # enum: none | listed_in_notes
```

```yaml
# ## D1. L1-L5 weights (MECHANICAL — registry is authority; no source/confidence)
L1: 0.3
L2: 0.25
L3: 0.2
L4: 0.15
L5: 0.1
```

```yaml
# ## D2. Thresholds + batch + rollback (object form per finding 1)
L1_threshold:          {value: 0.7, source: assumed, confidence: low}
L2_threshold:          {value: 0.7, source: assumed, confidence: low}
L3_threshold:          {value: 0.6, source: assumed, confidence: low}
L4_threshold:          {value: 0.55, source: assumed, confidence: low}
L5_threshold:          {value: 0.5, source: assumed, confidence: low}
batch_size:            {value: 4, source: assumed, confidence: med}
rollback_trigger:      {value: "3 consecutive L3<0.5", source: assumed, confidence: low}
override_rationale: null           # MUST be non-null string if user overrode any above (S6)
```

```yaml
# ## E. Spike plan (only present if proposal.## Open questions flagged spike)
spike_requested: true
spike_count: 3
judgment_criterion: "pick seed where L3>=0.6 AND L2>=0.7; fallback: highest weighted sum"
results:                           # append-only; pre-spike: empty list
  - seed: 1337
    image_path: /tmp/.../spike_1.png
    L1_L5: {L1: 0.72, L2: 0.68, L3: 0.61, L4: 0.58, L5: 0.49}
    weighted_total: 0.644
    verdict: accept
status: pending | skipped | complete | failed
```

```yaml
# ## F. Cost budget
per_gen_sec:              {value: 80, source: measured, confidence: high}
total_session_sec:        {value: 480, source: derived, confidence: med}
fail_fast_consecutive:    {value: 2, source: assumed, confidence: low}
provider_used_for_calibration: mock
provider_multiplier_applied: 20
```

### 6.4 Data flow invariants

1. **D1 is byte-for-byte copy from registry** — if registry changes, re-running `/visual-spec` produces different D1. Not cached beyond this session.
2. **Spike results are append-only during Phase 5** — once a spike row is written + scored, it's immutable even on re-render during review. Audit trail preserved.
3. **`source: measured` requires witness** — if any YAML block claims `source: measured`, the skill body must show which tool call produced the number. Section 10 Testing enforces this.
4. **Section ordering is NOT contract** — downstream parser must locate sections by `##` heading match, not positional index.

### 6.5 F calibration — provider multiplier table

Phase 2 runs `generate_image(provider="mock")` once to get baseline `t_mock` (typically ~1ms on any machine). Then proposes per-gen budget by multiplier:

| A.provider (Phase 3 result) | Multiplier | Example per-gen (mock=1ms) |
|---|---|---|
| `mock` | 1× | 1 ms |
| `sdxl-mps` (Apple Silicon) | 20,000× | ~20 s (low-end MPS) |
| `sdxl-cuda` | 5,000× | ~5 s |
| `comfyui-mps` (full pipeline) | 80,000× | ~80 s (measured on M-series; see `docs/tools-readiness-matrix.md` §2.2) |
| `gemini` | 15,000× | ~15 s |
| `openai` | 10,000× | ~10 s |

Multipliers are **rough anchors derived from darwin/MPS/SDXL measurements recorded in `docs/tools-readiness-matrix.md` §2.2 (2026-04-21)**. They are NOT ground truth across hardware — users on different GPUs / cloud providers / CPU-only will see substantial drift. Per Y-override: user confirms proposed F in Phase 2; override logged to `## Notes` if deviated.

**Confidence tagging rules for F fields** (codifies portability per codex round-2 finding 6):

| Situation | F tags |
|---|---|
| Actual-provider calibration ran this session (non-mock `generate_image` measured real latency) | `source: measured, confidence: high` |
| Mock calibration + multiplier applied, **and host class matches the anchor set** (darwin/MPS for `sdxl-mps` / `comfyui-mps`, or user explicitly confirms provider class) | `source: derived, confidence: med` |
| Mock calibration + multiplier applied, **and host class differs from anchor set** OR provider class is unconfirmed | `source: derived, confidence: low` — **downgrade** per host-mismatch rule |

Treat the multiplier table as a platform-biased heuristic baseline, not general calibration. The calibration-user-confirm loop in Phase 2 IS the portability mechanism; the downgrade rule ensures the machine-readable `confidence` field reflects that honestly.

---

## 7. Invariants (skill bans S1-S6)

| # | Rule | Enforce class | Notes |
|---|---|---|---|
| **S1** | Pixel-tool ban baseline; exemptions: spike section + proposal sketch eval (Phase 3 `view_image`) | **prescription** | Agent self-discipline; no file lock |
| **S2** | `draft → resolved` only on explicit user trigger (finalize / done / ready / lock it / approve) | **prescription** | — |
| **S3** | Only consume proposal `status: ready`; reject draft | **helper** (frontmatter read) | Enforceable |
| **S4** | `design.frontmatter.tradition` copied from proposal and **immutable** | **helper** (Phase 6 write step) | Enforceable at write |
| **S5** | No parallel invocation on same slug | **prescription** (check `updated` timestamp vs now as heuristic) | Not truly atomic |
| **S6** | D1 from registry; D2 default proportional to D1; override MUST log rationale to `## Notes` | **prescription + helper** (registry call enforceable, rationale-logging is discipline) | Split-class |

Brainstorm's B1-B7 precedent is almost entirely prescription — `/visual-spec` inherits the same honest framing (per finding 4 — enforce annotations make the difference explicit, not eliminate it).

---

## 8. Error matrix (9 items)

| # | Signal | Response | Enforce |
|---|---|---|---|
| 1 | `proposal.md` not found OR `status != ready` | Print exactly: `proposal.md not found or status != ready at <path>. Run /visual-brainstorm <slug> first.` Terminate. | helper |
| 2 | Same-slug `design.md` exists `status: resolved` | Print exactly: `already finalized at <path>; branch with -v2 or pick new slug`. Terminate. **Do not overwrite.** | helper + prescription |
| 3 | Same-slug `design.md` exists `status: draft` | Resume path: re-enter Phase 4 review loop; skip dims whose fenced-block `reviewed: true` (per §6.3 preamble); prompt on remaining dims with `reviewed: false`. **Turn cap accumulates from draft's recorded count in `## Notes`; does NOT reset.** Implementation note: skill stores per-session turn count in `## Notes` as a `[resume-state] turns_used: <N>` line; plan doc decides storage exact format. | helper + prescription |
| 4 | Frontmatter schema violation: `tradition` not in registry OR `domain` not in 7-enum | Print exactly: `proposal.md frontmatter violation: <field> <value> invalid. Re-run /visual-brainstorm <slug> to fix.` Terminate. **Do not auto-retry.** | helper |
| 5 | Spike flagged but provider unreachable (ComfyUI down, missing API key) | In E section: `status: skipped`, `skip_reason: "<provider> unreachable: <err>"`. Log 1-line to `## Notes`. **Continue main flow** (D2/F unaffected). | helper |
| 6 | Spike `generate_image` returns error dict | In E section `results`: row with `verdict: failed`, `error: "<excerpt>"`. **Other spikes continue**; all-fail → `status: failed` (vs `skipped`). | helper |
| 7 | **Phase 5 only**: cost budget exceeded during spike (per-gen latency > `per_gen_sec.value × 2` for `fail_fast_consecutive` consecutive spike calls) | Print force-show of current draft + exactly: `cost budget exceeded during spike (<consecutive>×over). Abort, extend budget, or accept partial?` Three-option user pick. **Never auto-extend.** Phase 1-4 never trigger Err #7 (no pixel calls in those phases). | prescription |
| 8 | User requests pixel action outside spike (Phase 3/4) | Print exactly: `spec layer doesn't execute pixels outside spike. Spike plan is determined by proposal's ## Open questions; run /visual-plan after finalize to execute.` **Do not** call the requested tool. **Turn NOT charged.** | prescription (S1 parallel) |
| 9 | Sketch referenced by `proposal.## References` not readable at spec time (moved / symlink broken / permission denied) | Set phase state `sketch_available: false`. Proceed text-only. Log to `## Notes`: `sketch at <path> unreadable at spec time: <err>. Proceeding text-only; C.sketch_integration forced to "ignore".` **Do not abort.** | helper |

**Retry/overwrite classification**:
- **Do NOT auto-retry**: Errors #1, #4, #7
- **Do NOT overwrite**: Error #2
- **Degrade, continue**: Errors #5, #6, #9 (integration-path may-degrade principle)
- **Resume (special)**: Error #3 (accumulate state)
- **Decline without charge**: Error #8

---

## 9. Finalize vocabulary (finding 5 — brainstorm superset)

On Phase 6, the skill listens for any of **5 trigger words**, byte-compatible with brainstorm's 4-word set plus `approve` (new, aligned with derive-then-review semantics):

```
finalize | done | ready | lock it | approve
```

Cross-skill principle: `/visual-spec` is a superset of brainstorm's finalize vocabulary, not a different set. A user who just finalized a proposal with "done" can type "done" again here.

---

## 10. Testing — three-layer architecture

### 10.1 Layer A — pytest tripwires (durable)

```
tests/test_visual_spec_d1_registry_copy.py       # ~6 cases — registry→D1 byte-identity, no source/confidence on D1
tests/test_visual_spec_schema_invariants.py      # ~8 cases — 9-section (or 8) shape, triple-form on D2/F numerics, S1/S4/S6 statics, handoff literal grep
tests/test_visual_spec_source_confidence_matrix.py  # ~5 cases — per-dim source tag allowability, confidence enum
```

Total ~19 cases. Run time target < 5 s. No real providers.

### 10.2 Layer B — simulated ship-gate v1 (pre-ship)

After Step 6 writes SKILL.md, dispatch 4 parallel subagents covering 9 cases:

| # | Case | Expected outcome |
|---|---|---|
| P1 | Tradition-bearing proposal, no spike, full derive→review→finalize (mock-calibration path) | `status: resolved`, D1 from registry, D2 assumed/low, F **derived/med** (mock+multiplier per §6.5; only reaches `measured/high` if real provider ran in Phase 2) |
| P2 | Proposal Open questions flags spike → 3 spikes run | E section with `results[3]`, each has measured L1-L5 |
| P3 | Resume from `status: draft` + 1 un-reviewed dim | Turn accumulates (e.g., 3/5 → 4/5 on 1 review turn) |
| N1 | `proposal.status == draft` | Err #1 verbatim terminate |
| N2 | `proposal.tradition = "tang_court_mural"` (not in registry) | Err #4 schema violation verbatim |
| N3 | Mid-review user says "generate_image for me right now" | Err #8 decline, turn NOT charged |
| N4 | `proposal.## References: sketch.png` but file deleted | Err #9 degrade, text-only continue, `## Notes` logs |
| N5 | Same-slug design.md exists `status: resolved` | Err #2 refuse-overwrite verbatim |
| N6 | Spike provider (ComfyUI) unreachable | Err #5 spike.status=skipped, main flow completes |

Log: `docs/superpowers/plans/visual-spec-ship-gate-log.md` (to be written during plan).

### 10.3 Layer C — live ship-gate v2 (post-ship)

Runs after v1 GREEN + shipped, mirroring brainstorm's v2 pattern. Targets integration-path gaps:

| Gap | Live case |
|---|---|
| F calibration actually runs vs mock provider | Verify `per_gen_sec.source == measured` with witness |
| `get_tradition_guide` real data flowing into D1 | Byte-equality across session |
| Spike actually runs real ComfyUI when E active | End-to-end 1 spike × 1 image, bounded cost |
| `proposal.md` → `design.md` real file I/O + collision | Mirror brainstorm's Case C collision scenarios |
| `/visual-plan` actually consumes `design.md` | **Deferred** until `/visual-plan` ships — true parser-contract validation |

### 10.4 Testing discipline rules

1. **Layer A MUST pass before Layer B dispatches** — mechanical invariants cheap; catch before subagent spawn.
2. **`source: measured` claims require witness** (data-flow invariant #3). **Layer A only checks YAML/markdown structure and witness-reference SHAPE** (e.g., `## Notes` contains a calibration-tool-call reference line when F is tagged `measured`); it cannot verify the witness artifact actually exists. **Layer B simulates witnesses.** **Layer C is the only layer that fully verifies real witnesses via end-to-end tool runs.** Do NOT overstate Layer A coverage (per codex round-2 finding 4).
3. **Testing does NOT assert D2 correctness** — only that metadata is honest (`source: assumed, confidence: low`). Correctness of D2 thresholds is discovered through real use, not through testing (per finding 1 + Y-override).
4. **Cost gate**: ship-gate v2 live MUST default to `--max-images 1 --provider mock` for spike cases to avoid real-GPU burn during CI. Real-provider variant is manual invocation only.

---

## 11. Weight-class proportionality (vs brainstorm)

| Metric | `/visual-brainstorm` v0.17.4 | `/visual-spec` v1 | Ratio |
|---|---|---|---|
| Frontmatter fields (output) | 7 | 8 | 1.14× |
| Markdown sections (output) | 12 (2 conditional) | 9 (1 conditional) | 0.75× |
| Decision-tree nodes | 5 | 0 (pre-fill-then-review replaces tree) | — |
| Question-bank dimensions | 6 | 7 (= dimension count) | 1.17× |
| Turn cap (hard / soft) | 8 / 12 | 5 / 8 | 0.67× / 0.67× |
| Error matrix | 8 | 9 | 1.13× |
| Skill bans | 7 (B1-B7) | 6 (S1-S6) | 0.86× |

Proportional, not symmetric. Shorter turn cap because derive-then-review is legitimately lighter than interactive elicitation (superpowers reviewer verdict).

---

## 12. Deferred / not in scope (explicit)

- **`/visual-plan` parser contract lock** — Section 6 fenced YAML is proposal, not contract, until `/visual-plan` is designed. Disclaimer in Section 6.1.
- **Spike results feeding back into D2 threshold revision** — unidirectional (spike → E only) in v1. Revisit after real usage.
- **Pytest tripwires beyond the 3 files in §10.1** — additional invariants may surface during Layer B / C runs; file as follow-up.
- **Cross-session cost learning** — F uses per-session calibration; we do NOT persist calibration history to improve future estimates. YAGNI for v1.
- **Automatic provider fallback** — if Phase 3 picks `sdxl` and Phase 5 finds ComfyUI down, we Err #5 (skip spike) rather than fall back to another provider. Fallback logic would need another-decision dimension; keep spec focused.

---

## 13. Open questions (for Step 9 writing-plans)

These are implementation-level concerns for the follow-up plan doc:

- Exact turn count for "F calibration user confirm" — argued `not a turn` in §4 but the plan must specify the tool-call sequence that implements this non-counting.
- How the skill body detects "user said `deep review`" vs a false-positive in mid-sentence prose — brainstorm handles similar for `finalize / done / ready / lock it / approve` with loose substring match; `/visual-spec` adopts same pattern but plan should explicit-state.
- Whether pytest fixtures for Layer A should live under `tests/fixtures/visual-spec/` or inline — brainstorm's pytest is inline; Layer A may be more fixture-heavy due to schema checks. Plan decides.
- Release strategy: bundle with `/visual-plan` design (so 3 skills ship together as v0.18.0), or ship `/visual-spec` standalone as v0.17.5 patch and `/visual-plan` later. Current lean: ship standalone, mirror brainstorm's one-skill-at-a-time cadence. Plan to confirm.
- Section A flat-YAML-with-comment form vs D2/F triple-form (SP round-2 non-blocking): should A normalize to `{value, source, confidence}` triples on `seed` / `steps` / `cfg_scale` for parser uniformity once `/visual-plan` lands? Or keep flat because A fields are categorical-or-hyperparameter-not-judgment? Plan doc decides; either way, skill body writes a 1-line rationale.

---

## 14. References

- Sibling skill design: [`2026-04-21-visual-brainstorm-skill-design.md`](./2026-04-21-visual-brainstorm-skill-design.md)
- Shipped sibling skill body: `.claude/skills/visual-brainstorm/SKILL.md` (v0.17.4)
- Action-skill rigor baseline: `.claude/skills/decompose/SKILL.md`
- Tools matrix (F multiplier anchors): `docs/tools-readiness-matrix.md` §2.2
- Sibling live ship-gate log (Layer-C pattern reference): `docs/superpowers/plans/visual-brainstorm-live-ship-gate-log.md`
- Competitive landscape (moat context): [`2026-04-20-competitive-landscape.md`](./2026-04-20-competitive-landscape.md)
- Codex + superpowers review findings (9 items, all folded into this spec): `.scratch/visual-spec-draft-v2.md` §11
