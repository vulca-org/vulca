# Prompt Engineering Experiment: SDXL Subject Fidelity Design

**Date:** 2026-04-11
**Status:** Revised after parallel review (codex + superpowers), ready for implementation plan
**Type:** Experimental spike (not a feature)

## Background

The v3 E2E gallery (`assets/demo/v3/gallery/`, generated 2026-04-11 with ComfyUI + SDXL base 1.0) surfaced a clear subject-fidelity regression on one of the 13 `TRADITION_PROMPTS` entries:

- **`chinese_gongbi`**: prompt `工笔牡丹，细腻勾线，三矾九染` ("gongbi peony, fine line work, three alum nine dyes"). Expected: close-up peony flower painting. Actual: **another misty mountain landscape with pagodas**. The word "牡丹" (peony) was completely ignored.

A visual review of all 13 gallery entries identified a failure gradient:

| Prompt language | Subject familiarity | Result |
|---|---|---|
| English | SDXL-center (Mughal miniature, English watercolor) | ✅ Excellent — subject + technique both correct |
| CJK | SDXL-center (Chinese ink landscape) | ✅ Acceptable — subject + technique both correct |
| CJK | Off-center (Kinkaku-ji, sumi-e) | ⚠️ Partial drift — culturally appropriate but lost the specific landmark and the monochrome constraint |
| CJK | Far off-center (gongbi peony) | ❌ Total fallback — landed on the statistical center (ink landscape) |

The failure pattern is consistent with **SDXL CLIP's weak CJK tokenization**: CJK glyphs produce noisy/meaningless tokens, the English suffix auto-appended by the provider (`, {tradition} style`) is the only real signal, and without a negative prompt the model slides back to its statistical prior. Codex review flagged that this auto-suffix is itself a **confounding signal**: for `chinese_gongbi` the runner appends `, chinese gongbi style`, which pulls toward generic Chinese-art priors (ink landscape) and competes with any new English positive prompt we inject. The experiment must suppress or override this suffix to be valid.

There are two candidate fixes for this category of failure:

1. **Prompt engineering** — rewrite prompts in English, add explicit negative prompts, token-weight the subject, and suppress the auto-suffix. Zero cost, zero download.
2. **Checkpoint swap** — replace SDXL base with a culturally fine-tuned checkpoint (e.g., GuoFeng XL). ~6 GB download + code plumbing.

Fix 1 is the cheaper hypothesis and must be ruled out before Fix 2 is justified. This spec covers Fix 1.

## Goals

1. **Verify or falsify** the hypothesis that English-first prompts + token-weighted subject + explicit negative prompts + suppressed auto-suffix can rescue subject fidelity on SDXL base, specifically for the `chinese_gongbi` failure.
2. **Preserve the baseline** gallery (`assets/demo/v3/gallery/`) untouched for before/after comparison.
3. **Extend the E2E runner** with minimal, **disposable scaffolding** (negative prompts + tradition filter + output subdir + multi-seed loop). Scaffolding is tracked as tech debt: if the experiment succeeds and we want to keep any of it, a follow-up will add regression tests. Not adding tests now is an intentional spike trade-off.
4. **Produce a go/no-go signal** for whether to proceed with the GuoFeng checkpoint experiment (separate spec), based on evidence from **multiple seeds**, not a single roll of the dice.

## Non-Goals

- Not fixing prompts for all 13 traditions. Only the three that exercise the hypothesis get new prompts.
- Not re-running Phase 3 (Evaluate). The gongbi baseline got L-scores of 0.83 mean **while painting the wrong subject** — Gemma 4 scored the wrong image as if it were right. The score is not a valid metric for "did we paint the requested subject". Visual inspection against a hand rubric is the metric.
- Not re-running Phase 8 (Tools). Unaffected by prompt changes.
- Not adding new tests. This is an experimental spike, not a feature. Existing local provider integration tests already cover the `negative_prompt` plumbing path. Flag tracked as disposable tech debt.
- Not changing `src/vulca/providers/comfyui.py`. The provider already accepts `negative_prompt` as a kwarg and wires it into `CLIPTextEncode` node 7. Auto-suffix suppression is done at the **caller** (by passing `tradition=""` when an experimental override applies), not the provider.
- Not changing `VULCA_VLM_MODEL`, `VULCA_IMAGE_BASE_URL`, `OLLAMA_API_BASE`, or any other env variable.
- **Not changing CFG, step count, sampler, or scheduler.** The provider currently pins `steps=20`, `cfg=7.0`, `sampler_name="euler"`, `scheduler="normal"` (see `providers/comfyui.py:43-47`). These are held constant vs baseline so **prompt is the only independent variable** in the experiment.
- Not designing a general "prompt library" system. If the experiment succeeds we can decide separately whether to backport the new prompts or build something more structured.

## Hypothesis

> Rewriting `chinese_gongbi` with an **English-first positive prompt** that token-weights "peony" as the dominant subject, combined with a **negative prompt** excluding the exact failure modes we observed (landscape, mountains, mist, pagodas, temples, pine trees, architecture), AND **suppressing the provider's auto-appended `, chinese gongbi style` suffix**, will cause SDXL base to render a recognizable peony painting instead of falling back to a mountain landscape. We require this to hold across **at least 2 out of 3 random seeds** before declaring the hypothesis validated.

A secondary hypothesis: applying the same technique to `japanese_traditional` (which partially drifts) will produce a result closer to the requested Kinkaku-ji + sumi-e specification. `chinese_xieyi` is included as a **regression sentinel**, not a clean control — see next section.

## Experimental Scope

Stage 1 generates 5 images total:

| Tradition | Seeds | Role | Baseline | Target |
|---|---|---|---|---|
| `chinese_gongbi` | **3 (multi-seed)** | **Failure case to rescue** | Mountain landscape, no peony | Recognizable peony close-up in ≥2 of 3 seeds |
| `chinese_xieyi` | 1 | **Regression sentinel** (not a clean control — see below) | Acceptable ink landscape | Still an acceptable ink landscape (no catastrophic regression) |
| `japanese_traditional` | 1 | Partial-drift secondary test | Generic colored pagoda + snow | Kinkaku-ji architecture + monochrome/low-color palette |

The other 10 traditions are not regenerated — they either already produce strong results (English prompts: south_asian, watercolor, etc.) or are not part of the CJK failure mode.

**Why multi-seed for gongbi (codex review)**: SDXL base has high seed variance on culturally niche subjects. A single failed gongbi would not prove "SDXL cannot represent peonies no matter how we prompt it" — it could just be a bad seed. Three seeds with a ≥2/3 success bar makes the result robust to one unlucky roll. Wall-time cost is modest (~6 extra minutes for two additional gongbi images).

**Why xieyi is not a clean control (codex review)**: rewriting xieyi in English and adding a negative prompt at the same time confounds "did English help" with "did negatives help" with "was the baseline already robust enough". A rigorous factorial would require separate English-only and negative-only runs. This spec **explicitly does not do a factorial** — xieyi is kept only as a regression sentinel (detect catastrophic breakage, not attribute causation). If Stage 1 gongbi results are ambiguous (exactly 1 of 3 seeds pass), Stage 2 may add a factorial — see Decision Tree.

## Architecture

### Current State

`scripts/generate-e2e-demo.py`:

```python
TRADITION_PROMPTS: list[tuple[str, str]] = [
    ("chinese_xieyi", "水墨山水，雨后春山，松间茅屋"),
    ("chinese_gongbi", "工笔牡丹，细腻勾线，三矾九染"),
    # ... 11 more
]

result = await provider.generate(
    prompt,
    tradition=tradition,
    width=width,
    height=height,
)
```

No negative prompt is passed. No tradition filter. No seed control. Output goes to `assets/demo/v3/gallery/{tradition}.png`, overwriting prior baselines.

`src/vulca/providers/comfyui.py` — provider state relevant to the experiment:
- Already supports `negative_prompt` kwarg, wires it into `CLIPTextEncode` node 7 (line ~54).
- **Auto-appends `, {tradition} style` to the prompt when `tradition != ""` and `tradition != "default"`** (line ~38-39). The experiment must override this by passing `tradition=""` at the call site.
- **KSampler seed is randomized per call** via `secrets.randbelow(2**63)` (line ~44, commit `fb8d47b`). There is no deterministic seed path. Multi-seed runs are achieved by calling `generate()` multiple times and letting the provider draw independent seeds.
- Pins `steps=20`, `cfg=7.0`, `sampler_name="euler"`, `scheduler="normal"` — held constant (see Non-Goals).

### Changes

All changes are in `scripts/generate-e2e-demo.py`. The existing 13-entry defaults are preserved so running the script with no new flags behaves identically to today.

**1. Evolve `TRADITION_PROMPTS` schema.**

From `list[tuple[str, str]]` to `list[dict]` with the shape:

```python
{
    "tradition": str,
    "prompt": str,          # existing positive prompt (preserved verbatim)
    "negative": str,        # defaults to "" for existing entries
}
```

Backfill all 13 existing entries with `"negative": ""`. Do not modify their `prompt` field. This preserves exact reproducibility of the baseline.

**2. Pass `negative_prompt` through `run_phase1_gallery`.**

`provider.generate(..., negative_prompt=entry["negative"])`. Provider already accepts this kwarg.

**3. Add `--traditions` CLI flag.**

```
--traditions chinese_gongbi,chinese_xieyi,japanese_traditional
```

Comma-separated list of tradition names. When set, Phase 1 only generates the listed subset. When unset, generates all 13 (existing behavior). Unknown names fail fast with a clear error listing valid names from `TRADITION_PROMPTS`.

**4. Add `--gallery-subdir` CLI flag.**

```
--gallery-subdir gallery-promptfix
```

When set, Phase 1 writes to `assets/demo/v3/<subdir>/` instead of the default `assets/demo/v3/gallery/`. The Phase 1 report is written to `assets/demo/v3/e2e-report-<subdir>.json` (with `e2e-report.json` preserved as the default-subdir filename for backwards compat). Report `path` fields reflect the chosen subdir. Phase 3 and Phase 8 continue to read from the default `gallery/` — they do not need to see the experimental subdir.

**5. Add `--seeds-per-tradition` CLI flag (new, codex-driven).**

```
--seeds-per-tradition chinese_gongbi:3
```

Semicolon or comma-separated `tradition:count` pairs. When set, the named traditions are regenerated `count` times each (each call produces an independent random seed since commit `fb8d47b`). Output filenames get a `_seedN` suffix: `chinese_gongbi_seed1.png`, `chinese_gongbi_seed2.png`, `chinese_gongbi_seed3.png`. Traditions not listed default to 1 image. When unset, all traditions produce 1 image (existing behavior).

Report entries gain an optional `seed_index` field when multi-seed is active.

**6. Override map for experimental prompts (with startup validation).**

Instead of editing the 13 defaults in-place, define a separate override map used only when `--traditions` is passed with a key that exists in the map. This keeps baseline defaults intact and the experiment fully isolated.

**Startup validation (moved out of Risks section per superpowers m5)**: at script startup, before any generation begins, iterate `EXPERIMENTAL_PROMPT_OVERRIDES` keys and verify each is a valid `TRADITION_PROMPTS` tradition name. If any key is not found, fail fast with a clear error. This guards against silent drift between the override map and the baseline list.

```python
# Experimental override prompts — only used when their tradition appears in
# --traditions. Each entry also suppresses the provider auto-suffix by causing
# the runner to pass tradition="" to provider.generate().
EXPERIMENTAL_PROMPT_OVERRIDES: dict[str, dict] = {
    "chinese_gongbi": {
        "prompt": (
            "(single large peony flower:1.4), close-up centered botanical "
            "portrait, Chinese gongbi meticulous brush painting, fine ink "
            "outlines, mineral pigments, peony blossom with green leaves, "
            "blank silk background, Chinese court flower-and-bird painting, "
            "museum quality botanical study"
        ),
        "negative": (
            "landscape, scenery, mountain, mountains, distant mountains, "
            "temple, pagoda, building, architecture, pine tree, river, lake, "
            "clouds, misty background, cottage, loose brushstrokes, xieyi, "
            "abstract, photography, impressionist"
        ),
        "suppress_tradition_suffix": True,
    },
    "chinese_xieyi": {
        "prompt": (
            "traditional Chinese xieyi freehand ink painting, misty mountains "
            "after spring rain, pine trees by a thatched cottage, sumi-e style, "
            "monochrome ink on rice paper, expressive loose brushwork, "
            "abundant reserved white space"
        ),
        "negative": (
            "photorealistic, saturated colors, western oil painting, gongbi, "
            "tight line work, peony, botanical portrait"
        ),
        "suppress_tradition_suffix": True,
    },
    "japanese_traditional": {
        "prompt": (
            "(Kinkaku-ji Golden Pavilion:1.3), Kyoto, winter snow, "
            "sumi-e monochrome ink painting, traditional Japanese ink wash "
            "suiboku-ga, minimal brushwork, atmospheric, gold temple "
            "reflecting on pond"
        ),
        "negative": (
            "saturated color, ukiyo-e print, anime, photography, western "
            "painting, cherry blossoms, red bridge, generic pagoda, "
            "snow on trees"
        ),
        "suppress_tradition_suffix": True,
    },
}
```

**Prompt engineering notes (responding to codex review)**:

- `(...:1.4)` is A1111-style token weighting, supported natively by ComfyUI's `CLIPTextEncode` node. If it does not parse at runtime (older ComfyUI versions may differ), fall back to repetition + capitalization (e.g., `"PEONY peony peony"`) and re-run. Flagged as an implementation-time verification step.
- **Dropped** `ink wash` from the gongbi negative — codex noted it could suppress the adjacent `fine ink outlines` signal we want to keep. Replaced with `loose brushstrokes` which targets xieyi-style drift specifically.
- **Replaced** bare `color` with `saturated color` in the japanese negative — Kinkaku-ji is literally the **Gold** Pavilion, so a negative against all color would fight the subject itself.
- **Added** explicit architectural / landscape negatives for gongbi (temple, pagoda, building, architecture, pine tree, river, lake, clouds) targeting the exact failure modes observed in the baseline image.
- **Token-weighted** the primary subject in gongbi (`peony`) and japanese (`Kinkaku-ji Golden Pavilion`) to push them above generic filler tokens.
- **Removed** "silk scroll format" and "museum quality" as standalone tokens from gongbi — codex flagged these as fillers that compete with the subject without adding recognizable visual signal. "Museum quality botanical study" is kept as a phrase because "botanical study" reinforces the close-up framing.

**Override resolution rules** (explicit, per-tradition — superpowers M2 fix):

For each tradition listed in `--traditions`:
- If the tradition name is a key in `EXPERIMENTAL_PROMPT_OVERRIDES`, use the override's `prompt` + `negative` + `suppress_tradition_suffix` flag.
- Otherwise, use the original `TRADITION_PROMPTS` entry with empty `negative` and no suffix suppression.

Mixed invocations work correctly: `--traditions chinese_gongbi,south_asian` regenerates gongbi with the override and south_asian with its original prompt in the same run.

When `suppress_tradition_suffix=True`, the runner calls `provider.generate(positive, tradition="", ...)` instead of `provider.generate(positive, tradition=tradition, ...)`. The output filename still uses the loop-variable `tradition` name, so `chinese_gongbi_seed1.png` is still named correctly.

**Flag combinations** (table form to avoid ambiguity):

| `--traditions` | `--gallery-subdir` | `--seeds-per-tradition` | Behavior |
|---|---|---|---|
| unset | unset | unset | All 13 traditions, original prompts, 1 seed each, `gallery/` (today's behavior) |
| set | unset | unset | Listed subset, 1 seed each, **writes to `gallery/`** (overwrites baseline — use with caution) |
| unset | set | unset | All 13 traditions, original prompts, 1 seed each, subdir |
| set | set | unset | Listed subset, 1 seed each, subdir (safe experimental default minus multi-seed) |
| set | set | set | **Full experimental invocation** — subset + multi-seed + isolated subdir |

Unknown tradition name in `--traditions` → fail fast at startup with a clear error listing valid names from `TRADITION_PROMPTS`.

### Data Flow

```
CLI:  python scripts/generate-e2e-demo.py \
        --phases 1 \
        --provider comfyui \
        --traditions chinese_gongbi,chinese_xieyi,japanese_traditional \
        --gallery-subdir gallery-promptfix \
        --seeds-per-tradition chinese_gongbi:3

→ startup: validate EXPERIMENTAL_PROMPT_OVERRIDES keys ⊆ TRADITION_PROMPTS names
→ filter TRADITION_PROMPTS by --traditions
→ for each entry:
    override = EXPERIMENTAL_PROMPT_OVERRIDES.get(entry["tradition"])
    (positive, negative, suppress_suffix) = override or (entry["prompt"], "", False)
    tradition_arg = "" if suppress_suffix else entry["tradition"]
    seed_count = parsed_seeds.get(entry["tradition"], 1)
    for seed_idx in range(1, seed_count + 1):
        result = await provider.generate(
            positive,
            tradition=tradition_arg,
            negative_prompt=negative,
            width=1024, height=1024,
        )
        filename = f"{entry['tradition']}.png" if seed_count == 1 \
                   else f"{entry['tradition']}_seed{seed_idx}.png"
        write to assets/demo/v3/gallery-promptfix/{filename}
→ write report to assets/demo/v3/e2e-report-gallery-promptfix.json
```

## Evaluation Rubric

Visual inspection, hand-scored against a fixed rubric defined **before** the images are generated. This prevents post-hoc aesthetic drift from deciding the result (codex minor finding 5). The rubric is deliberately simple and binary — no CLIP similarity, no separate classifier, no Gemma 4 re-scoring (Gemma 4 already demonstrated it cannot judge subject correctness for this exact class of image).

### Per-image rubric (4 binary criteria)

For each generated image, score 0/1 on:

1. **Subject present** — the requested primary subject appears somewhere in the image at all.
   - gongbi: peony flower(s) visible
   - xieyi: misty mountain landscape visible
   - japanese: a gold temple / pavilion visible
2. **Subject dominant** — the requested subject occupies the visual center of gravity, not a background detail.
   - gongbi: peony is the main subject (not a decorative edge flower in a landscape)
   - xieyi: landscape is the main subject
   - japanese: the gold temple is the main subject
3. **No wrong-genre dominance** — the image is not dominated by a genre other than the one requested.
   - gongbi: no mountain landscape, no temple architecture dominance
   - xieyi: no photorealism, no saturated Western oil-painting palette
   - japanese: no red bridge / cherry blossom ukiyo-e fallback
4. **Style roughly matches requested technique** — the brushwork / color palette / composition broadly fits the named tradition. This is the most subjective criterion and is scored conservatively — when in doubt, score 0.
   - gongbi: fine outlines + layered flat pigment, not loose ink wash
   - xieyi: monochrome ink, loose expressive brushwork
   - japanese: monochrome or low-saturation palette, ink-wash brushwork

Each image gets a score out of 4. "Pass" = score ≥ 3 **AND** criterion 1 (subject present) = 1. An image with subject absent is an automatic fail regardless of the other criteria.

### Success thresholds

- **Primary** (must): gongbi passes in **at least 2 of 3 seeds**. This is the stronger, multi-seed version of "recognizable peony flower painting, not a mountain landscape".
- **Secondary** (should): xieyi passes. Regression sentinel — detect catastrophic breakage from the new prompt + negative.
- **Tertiary** (nice): japanese passes. Evidence that the technique generalizes to a second off-center CJK subject.

## Decision Tree After Results

Outcome space is Primary × Secondary (tertiary is advisory only):

| Primary (gongbi ≥2/3) | Secondary (xieyi passes) | Decision |
|---|---|---|
| **Pass** | **Pass** | **Prompt engineering confirmed sufficient.** Close the GuoFeng spec as not-needed. Open a follow-up to decide backport strategy (hand-patch `TRADITION_PROMPTS` vs design a prompt library). |
| **Pass** | **Fail** | **Core hypothesis validated, xieyi prompt over-specified.** Rebalance the xieyi override (weaken negative, restore loose brushwork language) and re-run xieyi only — 1 seed, ~2 min. Still a win overall. |
| **Fail** (0/3) | Pass | **Bounded reformulation, not immediate escalation** (codex + superpowers M3). Run exactly **one** additional gongbi Stage 2 with a reformulated prompt: stronger token weight (1.6 instead of 1.4), different subject phrasing (e.g., `"(peony blossom botanical illustration:1.6)"`), all 3 seeds. If Stage 2 still 0/3 → proceed to GuoFeng spec. If Stage 2 ≥2/3 → primary pass. Budget: **exactly one reformulation iteration**, not unlimited. |
| **Fail** (0/3) | Fail | Same as above (single reformulation iteration for gongbi). Xieyi-fail under this branch is secondary evidence the baseline is itself fragile, which only strengthens the case to either reformulate or escalate. |
| **Ambiguous** (1/3 seeds pass) | (any) | **Run Stage 2 factorial for gongbi**: 3 seeds of English-prompt-only (no negative), 3 seeds of original-CJK-prompt-with-negative. This disentangles whether English or negative is carrying the signal. Report all 9 images + factorial analysis. Then re-enter this decision tree with the better condition as the Stage 1 result. |

**Explicit budget**: at most one Stage 2 iteration per gongbi branch (reformulation OR factorial, not both in sequence). This guards against unbounded prompt tweaking.

**`Primary pass, Secondary fail` cases for other traditions** (e.g., japanese fails): informational only. Does not block a primary-pass go/no-go decision. Record in the comparison summary but do not trigger stage 2 on its own.

## Reproducibility

This experiment's artifacts are visual and seed-dependent. For a future session to reproduce or even interpret the results, the spec pins the following and the final commit message records them:

- **Commit SHA** (at time of run): recorded in the comparison summary deliverable and in the commit message of the experimental commit.
- **ComfyUI repo commit** at `~/dev/ComfyUI/`: record `git rev-parse HEAD` of that repo in the comparison summary.
- **`sd_xl_base_1.0.safetensors` SHA-256 checksum**: `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b` (measured 2026-04-11). Recompute with `shasum -a 256 ~/dev/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors` before running the experiment; if the hash differs, the local copy was re-downloaded or corrupted and the results cannot be compared against the baseline gallery.
- **Machine**: Apple Silicon, macOS Darwin 25.4.0, MPS backend, fp32. (This is the only machine this repo has been run on locally; if that changes, the record should be updated.)
- **Random seed disclosure**: KSampler seed is drawn via `secrets.randbelow(2**63)` on every `provider.generate` call. **The committed PNGs are the only reproducible artifact** — running this spec's commands again will produce different images. This is accepted: the experiment answers a "does it work at all" question, not a "what exactly does seed 42 produce" question. The ≥2/3 threshold is the robustness guard against seed unluckiness.
- **Sampler settings** (held constant vs baseline): `steps=20`, `cfg=7.0`, `sampler_name="euler"`, `scheduler="normal"`, `denoise=1.0`, `width=1024`, `height=1024`. Codified at `providers/comfyui.py:43-47` and not modified by this spec.

If the experiment succeeds and is worth locking in, a follow-up could add seed-pinning to `comfyui.py` via an optional `seed` kwarg — but that's out of scope here.

## Risk & Rollback

**Risk: experimental outputs contaminate baseline.**
Mitigated by `--gallery-subdir gallery-promptfix`. Baseline `gallery/` is never touched. Rollback = delete the `gallery-promptfix/` directory.

**Risk: ComfyUI is not running.**
Mitigated by human-in-loop. The user must start ComfyUI before the runner is invoked. The runner does not start ComfyUI itself. Validated by a connection check at Phase 1 startup (existing behavior — failures surface immediately).

**Risk: A1111 token weighting `(peony:1.4)` does not parse in our ComfyUI version.**
Mitigated by fallback plan: if the first gongbi image shows no subject-weighting effect, switch to `PEONY PEONY peony` repetition + uppercase. Flagged as an implementation-time verification step.

**Risk: The new prompts produce subject-correct but aesthetically mediocre results.**
This is the *point* of the experiment — to find out. A subject-correct but ugly gongbi is still strong evidence that prompt engineering is viable; the remaining gap is a quality-tuning problem (LoRAs, CFG, step count), not a fundamental model limitation. Recorded in the comparison summary as "subject win, quality follow-up needed".

**Risk: Multi-seed wall time exceeds expectations.**
Stage 1 has 5 images total (gongbi ×3 + xieyi + japanese). At ~110s/image that's ~9 minutes, not 6. Stage 2 (if triggered) adds another 3–6 images (~6–11 minutes). Worst-case wall time is ~20 minutes. Still acceptable for a spike.

## Pre-requisites

- ComfyUI must be running at `http://localhost:8188` with `sd_xl_base_1.0.safetensors` loaded.
- `VULCA_IMAGE_BASE_URL=http://localhost:8188` must be set in the environment the runner is invoked from.
- No new model downloads. No new dependencies.

## Test Plan

**No new automated tests.** Rationale:
- The `negative_prompt` plumbing in `providers/comfyui.py` is already covered by existing integration tests in `tests/test_local_provider_e2e.py`.
- The CLI flag surface (`--traditions`, `--gallery-subdir`, `--seeds-per-tradition`) is disposable scaffolding per Goal 3. If the experiment succeeds and we keep any of these flags, a follow-up ticket will add smoke tests — this is tracked as intentional spike debt, not oversight.
- The experiment itself is a one-shot visual comparison, not a repeatable test fixture.
- Startup validation of `EXPERIMENTAL_PROMPT_OVERRIDES` keys is a self-check at every invocation, which is stricter than a one-time test.

**Manual verification at implementation time:**
1. Run the script with `--traditions chinese_gongbi --gallery-subdir /tmp/smoke` (no `--seeds-per-tradition`) and verify a single gongbi image lands in `/tmp/smoke/` with the override applied.
2. Run with `--seeds-per-tradition chinese_gongbi:2` and verify `chinese_gongbi_seed1.png` and `chinese_gongbi_seed2.png` both exist and are byte-different.
3. Run with an intentionally invalid `--traditions foo` and verify fail-fast error message lists valid names.
4. Run with `EXPERIMENTAL_PROMPT_OVERRIDES` temporarily pointing to a non-existent tradition and verify startup validation catches it.

After all four pass, run the full Stage 1 invocation (the CLI in Data Flow above).

## Estimated Wall Time

- **Stage 1**: 5 images total — gongbi ×3 + xieyi ×1 + japanese ×1 — at ~110s/image on SDXL + MPS ≈ **9 minutes** of generation. Code changes + reporting negligible.
- **Stage 2** (if triggered): one reformulation round for gongbi = 3 more images ≈ **5 minutes**. Or the factorial branch = 6 more images ≈ **11 minutes**.
- **Worst case**: Stage 1 + Stage 2 factorial ≈ **20 minutes** total ComfyUI time.

## Deliverables

1. Updated `scripts/generate-e2e-demo.py` with the five code changes listed in Architecture.
2. `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed1.png`
3. `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed2.png`
4. `assets/demo/v3/gallery-promptfix/chinese_gongbi_seed3.png`
5. `assets/demo/v3/gallery-promptfix/chinese_xieyi.png`
6. `assets/demo/v3/gallery-promptfix/japanese_traditional.png`
7. `assets/demo/v3/e2e-report-gallery-promptfix.json`
8. **Comparison summary** (not committed, posted back to the user) using the template below.
9. Go/no-go decision for the GuoFeng checkpoint experiment, derived from applying the Decision Tree to the rubric scores.

### Comparison summary template (superpowers m2 fix)

```
## Prompt Engineering Experiment Results

**Run commit**: <SHA of the experimental commit>
**ComfyUI commit**: <SHA of ~/dev/ComfyUI HEAD>
**Model SHA-256**: <sd_xl_base_1.0.safetensors hash>
**Total wall time**: <minutes>
**Stage 2 triggered**: yes / no (which branch)

### Per-image rubric scores

| Image | Subject present | Subject dominant | No wrong-genre | Style match | Total | Pass? |
|---|---|---|---|---|---|---|
| chinese_gongbi_seed1 | 0/1 | 0/1 | 0/1 | 0/1 | N/4 | yes/no |
| chinese_gongbi_seed2 | 0/1 | 0/1 | 0/1 | 0/1 | N/4 | yes/no |
| chinese_gongbi_seed3 | 0/1 | 0/1 | 0/1 | 0/1 | N/4 | yes/no |
| chinese_xieyi | 0/1 | 0/1 | 0/1 | 0/1 | N/4 | yes/no |
| japanese_traditional | 0/1 | 0/1 | 0/1 | 0/1 | N/4 | yes/no |

### Aggregate
- Primary (gongbi ≥2/3 pass): **PASS / FAIL** (<N>/3)
- Secondary (xieyi pass): **PASS / FAIL**
- Tertiary (japanese pass): **PASS / FAIL**

### Decision
**<Branch taken from the Decision Tree>** → **<Next action>**

### One-sentence rationale per image
- gongbi seed1: ...
- gongbi seed2: ...
- gongbi seed3: ...
- xieyi: ...
- japanese: ...
```

All artifacts (code + images + report) committed to git in a single experimental commit. The comparison summary lives in the chat / in-session output, not in the repo (superpowers-convention for spike reports).
