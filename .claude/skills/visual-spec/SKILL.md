---
name: visual-spec
description: Use when a proposal.md with status ready already exists and you need to derive a resolved design.md with technical decisions (provider, prompt, thresholds, cost budget) plus optional spike validation. You MUST use this before /visual-plan. Requires /visual-brainstorm finalized first.
---

## Triggers

- **Slash command**: `/visual-spec <slug>` (preferred explicit entry).
- **Chinese aliases**: `视觉 spec`, `设计 design`.
- **Intent auto-match**: any user request to derive / resolve / spec a visual project when `docs/visual-specs/<slug>/proposal.md` exists with `status: ready`. Auto-invoke on phrases like "把这个 brief 变成 design.md", "resolve the technical decisions", "decide provider + prompt + thresholds" — do NOT wait for the slash command.
- **Skip-condition**: no proposal.md exists (→ run /visual-brainstorm first per Err #1) or already a design.md with `status: resolved` (→ Err #2).


You are running `/visual-spec` — the second meta-skill in the `brainstorm → spec → plan → execute` pipeline. Your job: read a `proposal.md` at `docs/visual-specs/<slug>/` (produced by `/visual-brainstorm` with `status: ready`), derive 7 technical dimensions into a draft `design.md`, walk the user through review, and finalize on explicit approval.

**In scope:** any proposal with `status: ready` and `tradition` in the registry (or literal `null`).
**Out of scope:** producing pixels (the `/visual-plan` skill's job), multi-proposal batch runs, modifying `tradition` or `domain` (frozen from proposal per S4).

**Tone:** decisive derivation + collaborative review. You do the intellectual work pre-user; then you present the draft and let the user accept/override per dimension.

**Tools you may call** (phase-gated — see §Phase whitelist):
- Baseline (Phase 1-4, 6): `Read` (proposal.md + optional tradition-yaml), `list_traditions`, `search_traditions`, `get_tradition_guide`, `view_image` (proposal sketch only), `Write` (design.md — Phase 4 draft persistence + Phase 6 finalize)
- Phase 2 calibration only: `generate_image(provider="mock")` × 1
- Phase 5 spike only (if E section active): `generate_image(provider per A)`, `evaluate_artwork`, MAY `unload_models` after

**Never call** any pixel tool outside Phase 5 — see Skill ban S1.

## Phase 1 — Precondition gate

Run before anything else; no turn cap charged for this phase.

1. **Locate proposal.** `Read` `docs/visual-specs/<slug>/proposal.md`. If the file does not exist → Err #1. Do not create it; do not call `/visual-brainstorm` yourself.
2. **Check status.** Parse frontmatter. If `status != ready` (e.g., `draft`) → Err #1. Instruct the user to run `/visual-brainstorm <slug>` to finalize first.
3. **Check same-slug design collisions.** If `docs/visual-specs/<slug>/design.md` exists:
   - `status: resolved` → Err #2 (refuse overwrite; terminate).
   - `status: draft` → Err #3 (resume path: re-enter Phase 4, skip dims whose fenced block reads `reviewed: true`, accumulate turn count from the draft's `[resume-state] turns_used: <N>` line in `## Notes`).
4. **Validate tradition.** Call `list_traditions()`. Assert `frontmatter.tradition` is either a key in `list_traditions().traditions` OR the YAML literal `null`. Forbidden strings: `"N/A"`, `"none"`, `"null"`, `""`, `"unknown"` (brainstorm's B7 inheritance — these indicate upstream corruption). On violation → Err #4.
5. **Validate domain.** Assert `frontmatter.domain` is one of: `poster`, `illustration`, `packaging`, `brand_visual`, `editorial_cover`, `photography_brief`, `hero_visual_for_ui`. On violation → Err #4.
6. **Sketch readability probe.** If `## References` lists a local sketch path (not a URL), attempt `Read` on it once. If unreadable (FileNotFoundError, permission denied, broken symlink) → set internal state `sketch_available: false` and queue a `## Notes` entry per Err #9. Do NOT abort; proceed text-only with `C.sketch_integration` forced to `ignore`.
7. **Freeze tradition and domain.** Capture `tradition` and `domain` as session-level constants. They MUST NOT change between now and Phase 6 `Write` (S4).

Only when all gates pass: advance to Phase 2.

## Phase 2 — F calibration

Pre-cap. This phase produces the one user confirmation that is explicitly excluded from the 5-turn review budget.

**Resume behavior (Err #3).** On Err #3 resume, Phase 2 is skipped entirely — trust the draft's existing `F` block as-is. Do NOT re-invoke `generate_image(provider="mock")` nor re-apply the multiplier table. Rationale: the mock-calibration latency is a within-session noise measurement, not a repeatable physical constant; re-running it on resume adds jitter without new information, and re-prompting the user for F-confirm would silently inflate the turn count. If the draft's F block is malformed (missing keys, non-numeric values), that's a resume-corruption case — log `[resume-warning] F block malformed; re-enter Phase 2` to `## Notes` and re-run Phase 2 only then.

1. **Check `--budget-per-gen <seconds>` flag.**
   - If user passed a measurement (e.g., "I timed my last run at 42s") → use that value; mark `per_gen_sec.source: measured, confidence: high`. Skip the mock calibration.
   - If user passed a policy number (e.g., "budget me 60s per gen") with no measurement backing → use that value; mark `source: assumed, confidence: low`. Skip the mock calibration.
   - If the flag is absent → proceed to step 2.

   **Short-circuit when this path fires.** When `--budget-per-gen` was supplied (either measurement or policy number), you MUST skip steps 2-4 of Phase 2 (mock calibration, multiplier lookup, unknown-provider fallback, and the `t_mock × multiplier` F-value formula) entirely. Proceed directly to Phase 3 with the user-supplied value as the F baseline; tag F fields per step 1's source/confidence rules (not step 6's mock-path table). Set `provider_used_for_calibration: user-supplied` and `provider_multiplier_applied: null` in the F block. Step 5 (user confirm) and step 6 (confidence tagging) do not apply on this path — the user already committed the value by passing the flag.
2. **Run mock calibration.** Call `generate_image(provider="mock")` exactly once. Record the elapsed wall time as `t_mock` (seconds; typically ~0.001).
3. **Apply provider multiplier.** The multiplier depends on which provider Phase 3 will select for dim A. If A is not yet derived, make a provisional pick from `proposal.## Intent` + tradition hints, and revisit if Phase 3 diverges. Multiplier table:

   | A.provider | Multiplier | Example per-gen (mock = 1 ms) |
   |---|---|---|
   | `mock` | 1× | 1 ms |
   | `sdxl` (host-detect; aliases below) | — | see host-specific row |
   | `sdxl-mps` (Apple Silicon) | 20,000× | ~20 s |
   | `sdxl-cuda` | 5,000× | ~5 s |
   | `comfyui-mps` (full pipeline) | 80,000× | ~80 s |
   | `gemini` | 15,000× | ~15 s |
   | `openai` | 10,000× | ~10 s |

   **Bare `sdxl` resolution.** Proposals from `/visual-brainstorm` name `provider: sdxl` without a hardware qualifier (brainstorm has no reason to know the user's host). Before the multiplier lookup, normalize the provider name:
   - If `provider == "sdxl"` and `sys.platform == "darwin"` → treat as `sdxl-mps` for multiplier purposes.
   - If `provider == "sdxl"` on any other platform → treat as `sdxl-cuda`.
   - Record the resolved name in F as `provider_used_for_calibration`; keep the original `A.provider` value unchanged in the design.md `A` block.

   **Unknown-provider fallback.** If `A.provider` does not match any row in this table after the `sdxl` normalization above (new provider, typo, custom identifier): tag F fields with `source: assumed, confidence: low` and prompt the user verbatim: `Provider '<name>' not in multiplier table. Supply --budget-per-gen <seconds> to skip calibration.` Do NOT invent a multiplier; wait for the user's `--budget-per-gen` or provider correction before proceeding to step 4.

4. **Propose F values.**
   - `per_gen_sec.value = t_mock × multiplier`
   - `total_session_sec.value = per_gen_sec.value × D2.batch_size × 1.5` (margin)
   - `fail_fast_consecutive.value = 2`
5. **User confirm — one turn, NOT counted toward cap.** Prompt the user exactly:

   > `Calibration: per_gen ≈ <N>s (<source>). Session budget ~ <M>s. Accept or set --budget-per-gen?`

   Accept any affirmative reply (`ok`, `accept`, `yes`, `go`) or a `--budget-per-gen <seconds>` override. On override: re-apply step 1 rules for the supplied value.
6. **Confidence tagging rules (verbatim from spec §6.5).** Tag F fields by situation:

   | Situation | F tags |
   |---|---|
   | Actual-provider calibration ran this session (non-mock `generate_image` measured real latency) | `source: measured, confidence: high` |
   | Mock calibration + multiplier applied, **and host class matches the anchor set** (darwin/MPS for `sdxl-mps` / `comfyui-mps`, or user explicitly confirms provider class) | `source: derived, confidence: med` |
   | Mock calibration + multiplier applied, **and host class differs from anchor set** OR provider class is unconfirmed | `source: derived, confidence: low` — **downgrade** per host-mismatch rule |

   Derived fields (`total_session_sec`) inherit the parent confidence one notch lower, floored at `low`.

## Phase 3 — Dimension derivation

Pre-cap. Derive all 7 dimensions, each as a fenced YAML block with a `reviewed: false` preamble key. E is conditional — emit its block only if the proposal flags a spike (see below).

**Common preamble (every dim):** the first key in every dim's fenced YAML block is `reviewed: false`. Phase 4 flips this to `true` when the user accepts or completes a `change <dim>` sub-dialog on that dim.

### A — Provider + generation params

**Derivation class:** derived.

Reason from `proposal.## Intent` + `proposal.## Physical form` + `proposal.tradition` + local provider availability. The tradition guide's `pipeline_variant` field (e.g., `"sdxl-base"`, `"comfyui-full"`) is the nearest provider hint the registry exposes — use it when present, else apply agent judgment from the intent shape. (Note: no `recommended_providers` field exists on the guide; do not rely on one.) Pick seed as a stable integer (1337 is a safe default; steps and cfg_scale per tradition guide or provider default).

```yaml
# ## A. Provider + generation params
reviewed: false
provider: sdxl                     # source: derived, confidence: med
seed: 1337                         # source: assumed, confidence: low
steps: 30                          # source: derived, confidence: med
cfg_scale: 7.5                     # source: derived, confidence: med
```

### B — Composition strategy

**Derivation class:** derived (from proposal's single-vs-series answer).

If `proposal.## Series plan` exists → `strategy: series`, `variation_axis` MUST be a non-null string (e.g., `"zodiac_animal"`, `"season"`), `variant_count` MUST match the proposal's declared count. Else → `strategy: single`, `variation_axis: null`, `variant_count: 1`. `layer_decompose` is reserved for proposals whose intent explicitly requests editable layering (rare at spec time; usually a `/visual-plan` concern).

```yaml
# ## B. Composition strategy
reviewed: false
strategy: single                   # enum: single | layer_decompose | series
variation_axis: null               # MUST be non-null string if strategy=series; MUST be null otherwise
variant_count: 1                   # MUST match proposal's declared count
```

### C — Prompt composition

**Derivation class:** derived.

Compose `base_prompt` from `proposal.## Intent` + `proposal.## Physical form` + tradition tokens. Pull `tradition_tokens` MECHANICALLY from `get_tradition_guide(tradition).terminology` (no paraphrase).

**Real shape of `.terminology`.** The registry returns `list[dict]` — each entry has keys `term` (English), `term_zh` / `translation` (non-English), `definition` (`dict | str`), `aliases`, `category`. It is NOT a flat list of bilingual strings. Concat recipe to produce each `tradition_tokens` entry:

```
token = t.term
if t.translation or t.term_zh:
    token = f"{t.term} {t.translation or t.term_zh}"
```

Emit one `token` string per terminology entry (skip entries with empty `term`). The example below is the post-concat shape — do not copy it as the registry output.

Pull `color_constraint_tokens` from `proposal.## Color constraints` (one token per constraint; bilingual form where the guide supplies one). `negative_prompt` is used only on SDXL / ComfyUI providers; set `""` on `gemini` / `openai`. `sketch_integration` is forced to `ignore` if Phase 1 set `sketch_available: false`.

```yaml
# ## C. Prompt composition
reviewed: false
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

### D1 — L1-L5 weights (MECHANICAL)

**Derivation class:** mechanical — registry is the authority.

Call `get_tradition_guide(tradition).weights` and copy the 5 keys byte-for-byte. Do NOT paraphrase, round, or renormalize. If `tradition: null` → omit D1 entirely (no rubric; downstream treats as unweighted). D1 carries **no** `source` / `confidence` keys — registry-authority asymmetry.

```yaml
# ## D1. L1-L5 weights (MECHANICAL — registry is authority; no source/confidence)
# Values below are ILLUSTRATIVE only. Real weights vary per tradition — copy
# byte-for-byte from get_tradition_guide(tradition).weights. Do NOT paraphrase.
reviewed: false
L1: 0.3
L2: 0.25
L3: 0.2
L4: 0.15
L5: 0.1
```

### D2 — Thresholds + batch + rollback

**Derivation class:** per-session judgment, default proportional to D1.

Default rule: `L_N_threshold = 0.5 + D1.L_N` floored at 0.5, capped at 0.8. Batch size default 4 unless proposal indicates different scale. Rollback trigger default: `"3 consecutive L3<0.5"`. Every numeric field carries `{value, source, confidence}` triples. If the user overrides any default in Phase 4, set `override_rationale` to a non-null string (S6).

```yaml
# ## D2. Thresholds + batch + rollback
reviewed: false
L1_threshold:          {value: 0.7, source: assumed, confidence: low}
L2_threshold:          {value: 0.7, source: assumed, confidence: low}
L3_threshold:          {value: 0.6, source: assumed, confidence: low}
L4_threshold:          {value: 0.55, source: assumed, confidence: low}
L5_threshold:          {value: 0.5, source: assumed, confidence: low}
batch_size:            {value: 4, source: assumed, confidence: med}
rollback_trigger:      {value: "3 consecutive L3<0.5", source: assumed, confidence: low}
override_rationale: null           # MUST be non-null string if user overrode any above (S6)
```

### E — Spike plan (conditional)

**Derivation class:** conditional — only emit this block if `proposal.## Open questions` contains an item starting with `- spike:` OR matching the loose regex `spike[- ]?count\s*[=:]\s*\d+`. Be forgiving of user formatting (e.g., `- Spike: 3 seeds`, `- spike_count = 2`, `- spikecount: 4` all qualify).

If the trigger fires: set `spike_requested: true`, extract `spike_count` from the regex capture (default 3 if not numeric), derive `judgment_criterion` from `proposal.## Acceptance rubric` priorities + D2 thresholds. Pre-spike: `results: []`, `status: pending`.

If the trigger does not fire: **omit this section entirely** from design.md (yielding 8 markdown sections instead of 9).

**Null-tradition guard.** If `proposal.frontmatter.tradition == null`, skip the E section regardless of the spike trigger above. Rationale: D1 is omitted when `tradition: null` (registry-authority asymmetry), and Phase 5's `weighted_total = sum(L_N × D1.L_N)` + D2's "proportional to D1" default both require D1 values that do not exist. When this branch fires, append one line to `## Notes`: `[null-tradition] spike skipped — requires tradition-guide weights for judgment.`

```yaml
# ## E. Spike plan (only present if proposal.## Open questions flagged spike)
reviewed: false
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

### F — Cost budget

**Derivation class:** per-session calibration — Phase 2 measurement × provider multiplier.

Populate from Phase 2 results. `source: measured` requires a non-mock `generate_image` call actually ran this session; Phase 2's mock-only path MUST emit `source: derived` on `per_gen_sec` and downgrade per the §Phase 2 confidence table.

**Multiplier storage convention:** `provider_multiplier_applied` is the **raw factor from the Phase 2 multiplier table** (e.g., `20000` for `sdxl-mps`, `80000` for `comfyui-mps`), applied to `t_mock` (seconds) to compute `per_gen_sec`. The example below uses `comfyui-mps` (raw factor `80000`, producing ~80s/gen).

```yaml
# ## F. Cost budget
reviewed: false
per_gen_sec:              {value: 80, source: measured, confidence: high}
total_session_sec:        {value: 480, source: derived, confidence: med}
fail_fast_consecutive:    {value: 2, source: assumed, confidence: low}
provider_used_for_calibration: mock
provider_multiplier_applied: 80000
```

## Produced artifact — `design.md` schema

The Phase 4 draft and the Phase 6 finalized file share the same shape. Frontmatter is **9 fields, no extras, no inline YAML comments inside the `---` fence** (the 8 content fields below + `schema_version`). Sections: **9 when both D1 and E fire, 8 when either is omitted, 7 when both are omitted** (all `##` headings; downstream parsers locate by heading, not positional index — data-flow invariant 4). Specifically:

- **9 sections** (A B C D1 D2 E F + Open questions + Notes) — tradition is non-null AND proposal flagged a spike.
- **8 sections** — one of: (a) tradition non-null, no spike → omit E; (b) tradition null, spike flagged → but see null-tradition guard in §Phase 3.E which forces spike-skip → so case (b) collapses into (c); (c) tradition null, no spike → omit D1, E still absent.
- **7 sections** (A B C D2 F + Open questions + Notes) — tradition null AND no spike. This is the collapsed case. When this branch fires, `## Notes` MUST include the `[null-tradition] spike skipped` audit line per §Phase 3.E even though no spike was attempted.

### Template (copy and fill)

````markdown
---
slug: YYYY-MM-DD-<topic>            # copied from proposal, unchanged
status: draft                       # Phase 4: draft; Phase 6: resolved
schema_version: "0.1"               # design.md shape version; bump on breaking schema change; absent on legacy files means "0.1"
domain: <one of 7-enum>             # copied from proposal (S4 immutable)
tradition: <enum id OR YAML null>   # copied from proposal (S4 immutable)
generated_by: visual-spec@0.1.0
proposal_ref: docs/visual-specs/<slug>/proposal.md
created: YYYY-MM-DD                 # first draft write; unchanged on finalize
updated: YYYY-MM-DD                 # bumped on every write (draft + finalize)
---

# <human-readable title, mirror proposal>

## A. Provider + generation params
<fenced YAML per §Phase 3.A>

## B. Composition strategy
<fenced YAML per §Phase 3.B>

## C. Prompt composition
<fenced YAML per §Phase 3.C>

## D1. L1-L5 weights
<fenced YAML per §Phase 3.D1; OMITTED entirely if tradition: null>

## D2. Thresholds + batch + rollback
<fenced YAML per §Phase 3.D2>

## E. Spike plan
<ONLY present if proposal.## Open questions flagged spike per Phase 3.E trigger>
<fenced YAML per §Phase 3.E>

## F. Cost budget
<fenced YAML per §Phase 3.F>

## Open questions
<bullet list of items deferred to /visual-plan; literal `none` if all resolved>

## Notes
<free-form audit trail. MUST include (when relevant):
- [resume-state] turns_used: <N>              — progress counter (Err #3)
- [override] <dim>.<field>: <old> → <new>. Reason: <rationale>   — S6 override log
- sketch at <path> unreadable at spec time: <err>    — Err #9 degrade log
- <provider> unreachable: <err>                — Err #5 spike-skip log
- unload_models called after spike: <reason>   — Phase 5 memory-hygiene log>
````

**Empty-section rule** (mirrors brainstorm): when a non-conditional section has no content, write the literal `none` (not `TBD`, `N/A`, or blank). `## Open questions` and `## Notes` MUST NEVER be absent, even if empty.

## Phase 4 — Derive-then-review loop

Cap: **5 review turns** (hard). Each user-prompted reply increments the counter by 1. Soft extend: if user message contains the substring `deep review` (case-insensitive, loose — trigger also on `"let's do a deep review"`, `"DEEP REVIEW please"`) → raise cap to 8.

1. **Render draft.** Print the full in-flight `design.md` with all 7 dims filled in (E only if the Phase 3 conditional fired). Frontmatter `status: draft`, `updated: <today>`, `created: <today or resumed value>`. **Persist to disk:** immediately after the initial render, `Write` the draft to `docs/visual-specs/<slug>/design.md` with `status: draft`. This enables Err #3 resume. Each subsequent `change <dim>` acceptance MUST also re-`Write` the updated draft (same path, `status: draft`, bumped `updated:`) so the on-disk state matches the rendered state and the `[resume-state] turns_used: <N>` line stays current.
2. **Prompt exactly:**

   > `Draft design.md below. Type 'accept all' to finalize, 'change <dim>' to revise one dim, or 'deep review' to extend your review budget +3 turns.`

3. **Handle user replies:**
   - **`accept all`** → flip every dim's `reviewed: true`. Jump to Phase 6 (do not burn remaining cap; this is the happy path). **`accept all` does NOT require an intermediate draft-`Write` for the final `turns_used` bump** — Phase 6's finalize `Write` absorbs the +1 increment in the same transaction. Rationale: on this path, between the in-memory bump and the finalize `Write` no further turns can fire (the loop has already exited), so the single finalize `Write` is atomic for both status flip and counter state. This is the one exception to step 4's `Write`-pairs-with-every-`turns_used`-change rule.
   - **`change <dim>`** (e.g., `change A`, `change D2.batch_size`, `change C.base_prompt`) → open a sub-dialog scoped to that dim only. Rules:
     - Ask one targeted question per turn (e.g., `"D2.batch_size currently 4 (assumed, med). What value and why?"`).
     - When the user supplies a value, validate against the dim's schema (enum membership, positive integer, etc.). On invalid input: re-prompt once; a second invalid input counts as 1 turn and returns to the top prompt without changes.
     - When the user accepts the revision, flip that dim's `reviewed: true` in the fenced block. If the user overrode a default, append to `## Notes`: `[override] <dim>.<field>: <old> → <new>. Reason: <user rationale>.` (S6). If the user declines to give a rationale, write `Reason: none provided by user.` — the audit trail is the point, not blocking the user.
     - Sub-dialog turns count normally against the cap (1 turn per user reply).
   - **`deep review`** → cap: 5 → 8. Print one-liner: `Cap extended to 8 turns.` Do NOT advance to Phase 6. Only usable once per session (second invocation treated as invalid reply).
   - **Ambiguous reply** (`"looks good but"`, `"mostly fine"`) → re-prompt the main menu; count as 1 turn. Do not guess which dim the user means.
   - **Pixel action requests** (e.g., `just generate it`, `run the spike now` when E is not active) → Err #8. Decline; do NOT charge the turn.
4. **Per-turn housekeeping.** After each round, re-render the current draft (full block when any dim's YAML changed; compact `[unchanged dims: A, B, D1]` header otherwise) and update the `[resume-state] turns_used: <N>` line in `## Notes` (enables Err #3 resume). **Then re-`Write` `design.md` (with `status: draft`, `updated: <today>`) so the bumped counter is on disk. `Write` pairs with every `turns_used` change — no exceptions, even on ambiguous replies or invalid inputs that did not mutate any dim.** Otherwise a crash between the in-memory bump and the next `change <dim>` `Write` leaves the on-disk `turns_used` stale, and Err #3 resume undercounts the budget. If the user is hovering at cap−1, give one courtesy notice: `1 turn remaining. Last 'change <dim>' or 'deep review'?`.
5. **Cap-hit behavior.** When the counter reaches the current cap (5 or 8) without an `accept all`:
   - Force-show the current full draft.
   - Prompt exactly: `Turn cap reached. finalize or deep review?`
   - Do NOT auto-advance. Never flip `status` without explicit finalize (S2-equivalent).

## Phase 5 — Spike execution (conditional)

Runs only if Phase 3 emitted an E section with `spike_requested: true`. Not charged toward the review cap.

1. **Seed assignment.** Generate `spike_count` seeds deterministically: start from `A.seed` (the base), then `A.seed + 1`, `A.seed + 2`, ... One-off per-row override is permitted if the user specified it in the proposal's `## Open questions` (e.g., `- spike seeds: 1337, 42, 7`) — parse that list and prefer over the default walk.
2. **Iterate the spikes.** For each seed in the assignment list:
   - Call `generate_image(provider=<A.provider>, prompt=<C.base_prompt + C.tradition_tokens + C.color_constraint_tokens joined with commas>, negative_prompt=<C.negative_prompt>, seed=<this seed>, steps=<A.steps>, cfg_scale=<A.cfg_scale>)`.
   - Store the returned `image_path`.
   - On provider unreachable (connection refused, missing API key, timeout) → Err #5. Set E `status: skipped`, `skip_reason: "<provider> unreachable: <err>"`. Log a 1-liner to `## Notes`. **Break the spike loop; main flow continues.** D2 and F are unaffected.
   - On `generate_image` returning an error dict (validation, OOM, unsupported param) → Err #6. Append a `results[]` row with `verdict: failed, error: "<excerpt>"`. **Continue** to the next spike. If all spikes fail → E `status: failed` (distinct from `skipped`).
3. **Evaluate.** On each successful image: call `evaluate_artwork(image_path=<...>, tradition=<proposal.tradition>)`. Parse L1-L5 scores; compute `weighted_total = sum(L_N × D1.L_N)`. Pick `verdict` via the `judgment_criterion` string:
   - If the criterion is a thresholded predicate (e.g., `L3>=0.6 AND L2>=0.7`) → `accept` on pass, `reject` on fail.
   - Fallback: `accept` if `weighted_total >= max(D2.thresholds) × 0.9`, else `review`.
4. **Append results.** Each completed row: `{seed, image_path, L1_L5: {...}, weighted_total, verdict}` appended to E's `results[]`. **Append-only** during Phase 5 — do not rewrite earlier rows (data-flow invariant 2).
5. **Cost gate.** If any spike's measured per-gen latency exceeds `F.per_gen_sec.value × 2` and this happens on `F.fail_fast_consecutive` consecutive spike calls → Err #7. Force-show the current draft + prompt the three-option pick verbatim. **Never auto-extend.**
6. **Set E status.** After the loop: `status: complete` if all spikes scored; `status: failed` if all failed; `status: skipped` if Err #5 fired; `status: partial` if some but not all succeeded (log 1-liner to `## Notes`).
7. **Memory hygiene (optional).** After spikes complete, you MAY call `unload_models()` to free provider-side model weights. If you do, append a 1-line rationale to `## Notes`: `unload_models called after spike: freeing <provider> weights for subsequent session.`

## Phase 6 — Finalize + handoff

1. **Finalize triggers.** On user reply, do a case-insensitive substring match against the 5-word trigger set: `finalize`, `done`, `ready`, `lock it`, `approve`. Any hit → proceed. Ambiguous mid-sentence use (e.g., `"ready to keep reviewing"`) → prefer the later explicit prompt; if in doubt, ask `"Finalize now? (yes/no)"` and do NOT charge the turn.
2. **Flip status.** `frontmatter.status: draft → resolved`. `frontmatter.updated: <today in YYYY-MM-DD>`. `frontmatter.created:` unchanged from the draft / original write. **Ensure `frontmatter.schema_version` is present**: if absent on the draft (legacy file from pre-v0.17.6), set `"0.1"` on finalize; if present, leave as-is (downstream schema-version bumps are additive, not retro-written on older files).
3. **Write.** Call `Write` on `docs/visual-specs/<slug>/design.md`. Assert before writing: `frontmatter.tradition` and `frontmatter.domain` equal the values captured in Phase 1 (S4 write-time check). Assert `frontmatter.schema_version` is a non-empty string (defaults to `"0.1"` per step 2).
4. **Print the handoff string — exactly, verbatim, no variants:**

   ```
   Ready for /visual-plan. Run it with /visual-plan <slug>.
   ```

   Downstream tooling may grep this string; print exactly as shown (the trailing period closes the second sentence — keep it). Do not localize, do not paraphrase, do not add further punctuation.
5. **Do NOT auto-invoke `/visual-plan`.** The human-in-the-loop gate between spec and plan is preserved here.

### Date handling

`created` / `updated` use `YYYY-MM-DD` (ISO 8601 calendar date) in the session's local time zone. On resume (Err #3), `created` is copied from the existing draft and MUST NOT change; `updated` is set to today on every write (draft rewrite during Phase 4 housekeeping and Phase 6 finalize alike).

### Resume state line format

When Phase 4 housekeeping writes `## Notes`, the resume line is exactly:

```
[resume-state] turns_used: <N>
```

On Err #3 re-entry, grep this line out of the existing draft's `## Notes`; parse `<N>`; set the review-loop counter to `<N>` (not zero). If absent or unparseable, treat as `0` but log to `## Notes`: `[resume-warning] previous turns_used missing; counter reset to 0.`

## Phase whitelist

Copy of §4 from the design spec; the `Counts toward cap?` column header is grep-compatible with downstream tooling — do not rename.

| # | Phase | Tool whitelist | Counts toward cap? | Primary enforce class |
|---|---|---|---|---|
| 1 | Precondition gate | `Read` (proposal.md, optional tradition-yaml) | No | helper |
| 2 | F calibration | `generate_image(provider="mock")` × 1 (if no `--budget-per-gen`); user Q to confirm F | No (explicitly excluded) | helper + prescription |
| 3 | Dimension derivation | `get_tradition_guide` / `list_traditions` / `search_traditions` / `view_image` (proposal sketch only — sketch-eval exemption) | No | helper + prescription |
| 4 | Derive-then-review loop | Same as Phase 3; no spike tools; **plus `Write` (design.md, `status: draft`)** on initial render and after each accepted `change <dim>` | **Yes** — each user-facing prompt = 1 turn | prescription |
| 5 | Spike execution *(conditional)* | Whitelist lifts: `generate_image(provider per A)`, `evaluate_artwork`, MAY `unload_models` after | No | prescription |
| 6 | Finalize + handoff | `Write` (design.md) | No | helper + prescription (verbatim handoff) |

**Hard cap:** 5 review turns. **Soft extension trigger:** user says `deep review` → +3, max 8. **Cap-hit behavior:** force-show full current draft + `Turn cap reached. finalize or deep review?`.

**Forbidden across all phases** (S1 baseline): `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*`. Those belong to `/visual-plan` execution layer, not spec layer.

## Skill bans

Rules the agent running this skill MUST follow. Each ban is enforceable or prescription — labeled per column.

| # | Rule | Enforce class | Notes |
|---|---|---|---|
| **S1** | Pixel-tool ban baseline; exemptions: (a) Phase 5 spike execution authorizes ONLY `generate_image`, `evaluate_artwork`, and `unload_models` — no `create_artwork`, no `generate_concepts`, no `inpaint_artwork`, no `layers_*`; (b) Phase 3 `view_image` on proposal sketch for grounding. All other phases: zero pixel-tool calls. Forbidden across every phase (no exemption, ever): `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*`. | prescription | Agent self-discipline; no file lock. Violation → Err #8 if user requests; pure agent fault otherwise. |
| **S2** | Do not flip `frontmatter.status: draft → resolved` without an explicit finalize trigger (`finalize`/`done`/`ready`/`lock it`/`approve`). Turn-cap hit alone is NOT a trigger. | prescription | Vibe-spec anti-pattern; downstream burns tokens on misaligned decisions. |
| **S3** | Only consume `proposal.md` with `status: ready`. Reject `status: draft` via Err #1; run `/visual-brainstorm <slug>` to finalize first. | helper (frontmatter read) | Enforceable at Phase 1 gate. |
| **S4** | `design.frontmatter.tradition` and `design.frontmatter.domain` are copied from `proposal.md` and are **immutable** across the session. Phase 6 asserts equality before `Write`. | helper (Phase 6 write step) | Enforceable at write; violation is a code bug, not an agent choice. |
| **S5** | Do not dispatch two `/visual-spec` invocations on the same slug in parallel. Detect via `updated` timestamp vs wall-clock heuristic (if a same-slug `design.md` was updated <10 seconds ago, suspect concurrent run and abort). | prescription (not truly atomic) | File race corrupts state; resume broken. |
| **S6** | D1 is a byte-for-byte copy from `get_tradition_guide(tradition).weights`. D2 defaults proportional to D1. Any user override of a D2 / F numeric MUST log `[override] <dim>.<field>: <old> → <new>. Reason: <rationale>` to `## Notes`. | prescription + helper (registry call enforceable; rationale-logging is discipline) | Split-class. If user refuses to give a rationale, write `Reason: none provided by user` and continue — audit trail is the point, not correctness. |

## Error matrix

9-row table. Every `Print exactly:` string is in backticks for grep-compatibility. Do not paraphrase the printed strings.

| # | Signal | Response | Enforce |
|---|---|---|---|
| 1 | `proposal.md` not found OR `status != ready` | Print exactly: `proposal.md not found or status != ready at <path>. Run /visual-brainstorm <slug> first.` Terminate. | helper |
| 2 | Same-slug `design.md` exists `status: resolved` | Print exactly: `already finalized at <path>; branch with -v2 or pick new slug`. Terminate. **Do not overwrite.** | helper + prescription |
| 3 | Same-slug `design.md` exists `status: draft` | Resume path: re-enter Phase 4 review loop; skip dims whose fenced-block `reviewed: true` (per §Phase 3 preamble); prompt on remaining dims with `reviewed: false`. **Turn cap accumulates from draft's recorded count in `## Notes`** (`[resume-state] turns_used: <N>` line); does NOT reset. | helper + prescription |
| 4 | Frontmatter schema violation: `tradition` not in registry AND not YAML `null`, OR `domain` not in 7-enum | Print exactly: `proposal.md frontmatter violation: <field> <value> invalid. Re-run /visual-brainstorm <slug> to fix.` Terminate. **Do not auto-retry.** | helper |
| 5 | Spike flagged but **integration-layer** failure (provider unreachable / timeout / 401 / connection refused / missing API key). Classify by error-content semantic, not return shape — keyword list below. | In E section: `status: skipped`, `skip_reason: "<provider> unreachable: <err>"`. Log 1-line to `## Notes`. **Continue main flow** (D2/F unaffected); **break the spike loop**. | helper |
| 6 | Spike `generate_image` returns error dict due to **per-call** failure (validation error, OOM, malformed param, unsupported model error). Classify by error-content semantic — keyword list below. An ambiguous message that matches neither #5 nor #6 → default to #6 (continue-other-spikes is the safer degrade). | In E section `results`: row with `verdict: failed, error: "<excerpt>"`. **Other spikes continue**; all-fail → `status: failed` (distinct from `skipped`). | helper |

**Err #5 / #6 classifier (canonical regexes — case-insensitive).** Kept outside the table so alternation pipes are not escaped for Markdown; copy verbatim into any consumer:

```
Err #5 pattern:  (unreachable|timeout|connection refused|401|missing API key|rate.?limit)
Err #6 pattern:  (validation|OOM|malformed|unsupported|invalid param|model error)
```

Tiebreaker: on a message matching both patterns (e.g., `"OOM: fallback connection refused"`), prefer the diagnosis that is more actionable for the caller — integration-layer (#5) when the root cause is environmental, per-call (#6) when the root cause is input or model state. If unsure, the `default to #6` fallback in the matrix above applies (continue-other-spikes is the safer degrade).
| 7 | **Phase 5 only**: cost budget exceeded during spike (per-gen latency > `F.per_gen_sec.value × 2` for `F.fail_fast_consecutive` consecutive spike calls) | Print force-show of current draft + exactly: `cost budget exceeded during spike (<consecutive>×over). Abort, extend budget, or accept partial?` Three-option user pick. **Never auto-extend.** Phase 1-4 never trigger Err #7 (no pixel calls in those phases). | prescription |
| 8 | User requests pixel action outside spike (Phase 3 / Phase 4) | Print exactly: `spec layer doesn't execute pixels outside spike. Spike plan is determined by proposal's ## Open questions; run /visual-plan after finalize to execute.` **Do not** call the requested tool. **Turn NOT charged.** | prescription (S1 parallel) |
| 9 | Sketch referenced by `proposal.## References` not readable at spec time (moved / symlink broken / permission denied) | Set phase state `sketch_available: false`. Proceed text-only. Log to `## Notes`: `sketch at <path> unreadable at spec time: <err>. Proceeding text-only; C.sketch_integration forced to "ignore".` **Do not abort.** | helper |

**Retry/overwrite classification** (footer):

- **Do NOT auto-retry:** Errors #1, #4, #7.
- **Do NOT overwrite:** Error #2.
- **Degrade, continue:** Errors #5, #6, #9 (integration-path may-degrade principle).
- **Resume (special):** Error #3 (accumulate state).
- **Decline without charge:** Error #8.

## Finalize trigger vocabulary

On Phase 6, recognize any of **5 trigger words** (case-insensitive substring match):

`finalize` | `done` | `ready` | `lock it` | `approve`

This set is a superset of `/visual-brainstorm`'s 4-word set (brainstorm drops `approve`). A user who just finalized a proposal with "done" can type "done" again here — cross-skill vocabulary is intentionally monotonic.

## Handoff

On finalize (`status: draft → resolved`), print exactly:

> `Ready for /visual-plan. Run it with /visual-plan <slug>.`

Do NOT auto-invoke `/visual-plan`. The human-in-the-loop gate between `/visual-spec` and `/visual-plan` is preserved here.

## References

- Sibling skill: `.claude/skills/visual-brainstorm/SKILL.md` (v0.17.4; voice template)
- Design spec: `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md`
- Tools matrix (F multiplier anchors): `docs/tools-readiness-matrix.md` §2.2
- EMNLP 2025 Findings VULCA + VULCA-Bench L1-L5 anchors: same as brainstorm
