# Prompt Engineering Experiment: SDXL Subject Fidelity Design

**Date:** 2026-04-11
**Status:** Approved, ready for implementation plan
**Type:** Experimental spike (not a feature)

## Background

The v3 E2E gallery (`assets/demo/v3/gallery/`, generated 2026-04-11 with ComfyUI + SDXL base 1.0) surfaced a clear subject-fidelity regression on one of the 13 `TRADITION_PROMPTS` entries:

- **`chinese_gongbi`**: prompt `工笔牡丹，细腻勾线，三矾九染` ("gongbi peony, fine line work, three alum nine dyes"). Expected: close-up peony flower painting. Actual: **another misty mountain landscape with pagodas**. The word "牡丹" (peony) was completely ignored.

A visual review of all 13 gallery entries identified a failure gradient:

| Prompt language | Subject familiarity | Result |
|---|---|---|
| English | SDXL-center (Mughal miniature, English watercolor) | ✅ Excellent — subject + technique both correct |
| CJK | SDXL-center (Chinese ink landscape) | ✅ Acceptable — subject + technique both correct |
| CJK | Off-center (Kinkaku-ji, sumi-e) | ⚠️ Partial drift — culturally appropriate but lost the specific landmark and monochrome constraint |
| CJK | Far off-center (gongbi peony) | ❌ Total fallback — landed on the statistical center (ink landscape) |

The failure pattern is consistent with **SDXL CLIP's weak CJK tokenization**: CJK glyphs produce noisy/meaningless tokens, the English suffix auto-appended by the provider (`, chinese gongbi style`) is the only real signal, and without a negative prompt the model slides back to its statistical prior.

There are two candidate fixes for this category of failure:

1. **Prompt engineering** — rewrite prompts in English, add explicit negative prompts. Zero cost, zero download.
2. **Checkpoint swap** — replace SDXL base with a culturally fine-tuned checkpoint (e.g., GuoFeng XL). ~6 GB download + code plumbing.

Fix 1 is the cheaper hypothesis and must be ruled out before Fix 2 is justified. This spec covers Fix 1.

## Goals

1. **Verify or falsify** the hypothesis that English-first prompts + explicit negative prompts can rescue subject fidelity on SDXL base, specifically for the `chinese_gongbi` failure.
2. **Preserve the baseline** gallery (`assets/demo/v3/gallery/`) untouched for before/after comparison.
3. **Extend the E2E runner** with minimal plumbing (negative prompts + tradition filter + output subdir) in a way that's immediately reusable for future experiments, without introducing broken defaults.
4. **Produce a go/no-go signal** for whether to proceed with the GuoFeng checkpoint experiment (separate spec).

## Non-Goals

- Not fixing prompts for all 13 traditions. Only the three that exercise the hypothesis get new prompts.
- Not re-running Phase 3 (Evaluate). The gongbi baseline got L-scores of 0.83 mean **while painting the wrong subject** — Gemma 4 scored the wrong image as if it were right. The score is not a valid metric for "did we paint the requested subject". Visual inspection is the metric.
- Not re-running Phase 8 (Tools). Unaffected by prompt changes.
- Not adding new tests. This is an experimental spike, not a feature. Existing local provider integration tests already cover the `negative_prompt` plumbing path.
- Not changing `src/vulca/providers/comfyui.py`. The provider already accepts `negative_prompt` — only the caller does not pass it.
- Not changing `VLM_MODEL`, `IMAGE_BASE_URL`, or any other env variable.
- Not designing a general "prompt library" system. If the experiment succeeds we can decide separately whether to backport fixes into `TRADITION_PROMPTS` or build something more structured.

## Hypothesis

> Rewriting `chinese_gongbi` with an **English-first positive prompt** explicitly naming "peony", "close-up botanical study", and "flower-and-bird painting", combined with a **negative prompt** excluding "landscape, mountains, mist, pagodas, ink wash", will cause SDXL base to render an actual peony painting instead of falling back to a mountain landscape.

A secondary hypothesis: applying the same technique (English-first + negatives) to `chinese_xieyi` (which already works) will **not regress** its output quality, and applying it to `japanese_traditional` (which partially drifts) will produce a result closer to the requested Kinkaku-ji + sumi-e specification.

## Experimental Scope

Three traditions, selected as a minimal ABX test:

| Tradition | Role | Baseline | Target |
|---|---|---|---|
| `chinese_gongbi` | **Failure case** | Mountain landscape (wrong subject) | Peony close-up |
| `chinese_xieyi` | **Control** — must not regress | Acceptable ink landscape | Same or better ink landscape |
| `japanese_traditional` | **Partial drift** | Generic colored pagoda + snow | Kinkaku-ji sumi-e style |

The other 10 traditions are not regenerated. They either already produce strong results (English prompts: south_asian, watercolor, etc.) or are not part of the CJK failure mode.

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

No negative prompt is passed. No way to filter a subset. Output goes to `assets/demo/v3/gallery/{tradition}.png`, overwriting prior baselines.

`src/vulca/providers/comfyui.py` already supports `negative_prompt` as a kwarg and wires it into the `CLIPTextEncode` node #7. It requires zero changes.

### Changes

All changes are in `scripts/generate-e2e-demo.py`. The existing 13-entry defaults are preserved so running the script with no new flags behaves identically to today.

**1. Evolve `TRADITION_PROMPTS` schema.**

From `list[tuple[str, str]]` to `list[dict]` with the shape:

```python
{
    "tradition": str,
    "prompt": str,          # existing positive prompt (preserved verbatim for backwards compat)
    "negative": str,        # new, defaults to "" for existing entries
}
```

Backfill all 13 existing entries with `"negative": ""`. Do not modify their `prompt` field. This preserves exact reproducibility of the baseline.

**2. Pass `negative_prompt` through `run_phase1_gallery`.**

`provider.generate(..., negative_prompt=entry["negative"])`. Provider already accepts this kwarg.

**3. Add `--traditions` CLI flag.**

```
--traditions chinese_gongbi,chinese_xieyi,japanese_traditional
```

Comma-separated list of tradition names. When set, Phase 1 only generates the listed subset. When unset, generates all 13 (existing behavior). Unknown names fail fast with a clear error listing valid names.

**4. Add `--gallery-subdir` CLI flag.**

```
--gallery-subdir gallery-promptfix
```

When set, Phase 1 writes to `assets/demo/v3/<subdir>/` instead of the default `assets/demo/v3/gallery/`. The Phase 1 report's `path` fields reflect the chosen subdir. When unset, uses `gallery/` (existing behavior).

Phase 3 and Phase 8 continue to read from the default `gallery/` — they do not need to see the experimental subdir for this experiment.

**5. Override map for experimental prompts.**

Instead of editing the 13 defaults in-place, define a separate override list used only when `--traditions` is passed with the experimental subset. This keeps the baseline defaults intact and the experiment fully isolated.

```python
# Experimental override prompts — only used when their tradition appears in --traditions
EXPERIMENTAL_PROMPT_OVERRIDES: dict[str, dict] = {
    "chinese_gongbi": {
        "prompt": (
            "gongbi meticulous Chinese brush painting of peonies in full bloom, "
            "close-up botanical study, ultra-fine ink outlines, layered mineral "
            "pigments, silk scroll format, traditional Chinese flower-and-bird "
            "painting, museum quality"
        ),
        "negative": (
            "landscape, mountains, mist, pagodas, ink wash, impressionist, "
            "photography, loose brushstrokes, xieyi, abstract, cottage"
        ),
    },
    "chinese_xieyi": {
        "prompt": (
            "traditional Chinese xieyi freehand ink painting, misty mountains "
            "after spring rain, pine trees by a thatched cottage, sumi-e style, "
            "monochrome ink on rice paper, expressive loose brushwork, "
            "abundant reserved white space"
        ),
        "negative": (
            "photorealistic, colorful pigments, western oil painting, gongbi, "
            "tight line work, peony"
        ),
    },
    "japanese_traditional": {
        "prompt": (
            "sumi-e monochrome ink painting of Kinkaku-ji Golden Pavilion in "
            "winter snow, Kyoto, traditional Japanese ink wash suiboku-ga, "
            "minimal brushwork, atmospheric, gold temple reflecting on pond"
        ),
        "negative": (
            "color, ukiyo-e, anime, photography, western painting, cherry "
            "blossoms, red bridge, generic pagoda"
        ),
    },
}
```

**Override resolution rules** (explicit to avoid ambiguity):

- Override is applied **only when both** (a) `--traditions` is set, **and** (b) the tradition name appears as a key in `EXPERIMENTAL_PROMPT_OVERRIDES`.
- `--traditions` passed alone (no matching override key) runs the listed subset with **original** `TRADITION_PROMPTS` and empty `negative`. Useful for regenerating individual baselines.
- `--gallery-subdir` passed alone (no `--traditions`) runs **all 13** traditions with their original prompts into the subdir. Useful for full-gallery runs that should not overwrite the canonical baseline.
- Default invocation (neither flag set) behaves exactly as today: all 13, original prompts, into `gallery/`.
- Unknown tradition name in `--traditions` → fail fast at startup with a clear error listing valid names from `TRADITION_PROMPTS`.

### Data Flow

```
CLI:  python scripts/generate-e2e-demo.py \
        --phases 1 \
        --provider comfyui \
        --traditions chinese_gongbi,chinese_xieyi,japanese_traditional \
        --gallery-subdir gallery-promptfix

→ filter TRADITION_PROMPTS by --traditions
→ for each entry, look up override in EXPERIMENTAL_PROMPT_OVERRIDES
→ call provider.generate(positive, negative_prompt=negative, ...)
→ write to assets/demo/v3/gallery-promptfix/{tradition}.png
→ write report to assets/demo/v3/e2e-report-<subdir>.json
  (when --gallery-subdir=gallery-promptfix, filename is
   e2e-report-gallery-promptfix.json). Default subdir uses the
   existing e2e-report.json filename for backwards compat.
```

## Success Metrics

Visual inspection only. No quantitative metric is meaningful here (the existing VLM score is known to be insensitive to subject correctness).

**Primary** (must): `assets/demo/v3/gallery-promptfix/chinese_gongbi.png` contains a recognizable peony flower painting, not a mountain landscape.

**Secondary** (should): `assets/demo/v3/gallery-promptfix/chinese_xieyi.png` is subjectively as good or better than the baseline — it still shows a misty ink landscape with pines.

**Tertiary** (nice): `assets/demo/v3/gallery-promptfix/japanese_traditional.png` more closely matches the Kinkaku-ji + sumi-e request (specific golden pavilion architecture, monochrome or low-color palette).

## Decision Tree After Results

- **Primary + Secondary pass**: prompt engineering is confirmed sufficient. Stop the GuoFeng experiment. Open a follow-up to decide whether to backport the three new prompts into `TRADITION_PROMPTS` proper or build a more structured prompt library.
- **Primary fails** (gongbi still a landscape): strong evidence that SDXL base cannot represent the gongbi subject no matter how we prompt it. Proceed with the GuoFeng checkpoint experiment (separate spec).
- **Primary passes, Secondary fails** (gongbi fixed, xieyi regressed): the new xieyi prompt is over-specified or the negative prompt is too aggressive. Rebalance and re-run just xieyi. Still counts as a win — the core hypothesis is validated.
- **Mixed/unclear**: document in the spike report and escalate to user before deciding.

## Risk & Rollback

**Risk: experimental outputs contaminate baseline.**
Mitigated by `--gallery-subdir gallery-promptfix`. Baseline `gallery/` is never touched. Rollback = delete the `gallery-promptfix/` directory.

**Risk: the override map diverges from `TRADITION_PROMPTS` silently.**
Mitigated by the override map being explicit and keyed by tradition name. If an override references a tradition that is not in `TRADITION_PROMPTS`, fail fast at startup with a clear error.

**Risk: ComfyUI is not running.**
Mitigated by human-in-loop. The user must start ComfyUI before the runner is invoked. The runner does not start ComfyUI itself.

**Risk: the new prompts produce artistically mediocre results despite being subject-correct.**
This is the *point* of the experiment — to find out. A subject-correct but aesthetically mediocre gongbi is still strong evidence that prompt engineering is viable and the remaining gap is a quality-tuning problem (LoRAs, CFG, step count), not a fundamental model limitation.

## Pre-requisites

- ComfyUI must be running at `http://localhost:8188` with `sd_xl_base_1.0.safetensors` loaded.
- `VULCA_IMAGE_BASE_URL=http://localhost:8188` must be set in the environment the runner is invoked from.
- No new model downloads. No new dependencies.

## Estimated Wall Time

~6 minutes generation wall time (3 images × ~2 min each at SDXL MPS rate on this hardware, matching the baseline run's ~105-130s per image). The code changes and report writing are negligible.

## Deliverables

1. Updated `scripts/generate-e2e-demo.py` with the four code changes above.
2. `assets/demo/v3/gallery-promptfix/chinese_gongbi.png`
3. `assets/demo/v3/gallery-promptfix/chinese_xieyi.png`
4. `assets/demo/v3/gallery-promptfix/japanese_traditional.png`
5. `assets/demo/v3/e2e-report-gallery-promptfix.json`
6. A short written comparison summary delivered back to the user (not committed).
7. Go/no-go decision for the GuoFeng checkpoint experiment, derived from the comparison.

All artifacts committed to git in a single experimental commit (the code changes are permanently useful; the images document the experiment outcome).
