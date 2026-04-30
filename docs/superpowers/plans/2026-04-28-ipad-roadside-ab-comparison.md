# iPad Roadside A/B Comparison Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a fair A/B experiment comparing a plain prompt against the Vulca structured prompt-planning path on the same roadside source image.

**Architecture:** The experiment lives inside `docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/`. It uses one shared source image, one shared prepared reference image, one shared full-edit mask, the same provider/model/size for both arms, and separate output files for baseline and Vulca-mediated results. If the provider is blocked, the run records the exact upstream failure and stops without pretending the comparison completed.

**Tech Stack:** Vulca markdown artifacts, Python 3, PIL, httpx/OpenAI Images `/v1/images/edits`, Superpowers verification-before-completion discipline.

---

### Task 1: Record The A/B Experiment Contract

**Files:**
- Create: `docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/prompts/naive_prompt.txt`
- Create: `docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/prompts/vulca_structured_prompt.txt`
- Modify: `docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/plan.md`
- Modify: `docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/execution_log.md`

- [ ] **Step 1: Create the naive prompt**

Write this exact text to `prompts/naive_prompt.txt`:

```text
Turn this roadside photo into an iPad Procreate-style cartoon illustration. Make it colorful, playful, clean, and polished.
```

- [ ] **Step 2: Create the Vulca structured prompt**

Write this exact text to `prompts/vulca_structured_prompt.txt`:

```text
Transform the provided roadside photo into a polished iPad Procreate cartoon illustration.
Keep the same camera angle, road layout, guardrail placement, roadside hedge, trees,
sky, yellow maintenance truck, red car, and small white wildflowers as recognizable
scene anchors. Redraw the whole image as one coherent illustration, not as separate
pasted layer cutouts.

Visual style: vibrant pastel iPad illustration, soft rounded outlines, clean flat
shading, simple readable shapes, cheerful roadside atmosphere, crisp but gentle linework,
no photorealistic texture.

Critical constraints:
- no large white or cream blank blocks
- no mask-shaped halos
- no pasted stickers
- no muddy green/brown color drift on flower regions
- no global low-contrast wash
- keep the roadside scene composition legible
```

- [ ] **Step 3: Update plan.md with A/B arms**

Add an `## A/B Comparison Contract` section containing:

```markdown
## A/B Comparison Contract

| arm | prompt file | provider/model | reference | mask | output |
|---|---|---|---|---|---|
| A naive | `prompts/naive_prompt.txt` | `openai/gpt-image-2` | `source/reference_1536x1024.png` | `source/full_edit_mask_1536x1024.png` | `iters/ab/naive_gpt_image_2.png` |
| B Vulca structured | `prompts/vulca_structured_prompt.txt` | `openai/gpt-image-2` | `source/reference_1536x1024.png` | `source/full_edit_mask_1536x1024.png` | `iters/ab/vulca_structured_gpt_image_2.png` |

Fairness rules:
- same source-derived reference image
- same full-edit mask
- same model, endpoint, size, output format, quality where supported
- no decompose, no layers_redraw, no manual retouching
- if provider billing blocks either arm, mark the whole experiment blocked
```

- [ ] **Step 4: Verify files exist**

Run:

```bash
test -f docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/prompts/naive_prompt.txt
test -f docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/prompts/vulca_structured_prompt.txt
rg -n "A/B Comparison Contract|naive_gpt_image_2|vulca_structured_gpt_image_2" docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/plan.md
```

Expected: exit 0 and three `rg` matches.

### Task 2: Make The Experiment Runner Reproducible

**Files:**
- Create: `docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/run_ab_experiment.py`

- [ ] **Step 1: Create the runner**

Write a Python runner that:
- reads `.env.local` before execution through shell `set -a; . .env.local; set +a`
- uses the existing `source/reference_1536x1024.png`
- uses the existing `source/full_edit_mask_1536x1024.png`
- calls `/v1/images/edits`
- writes `iters/ab/naive_gpt_image_2.png`
- writes `iters/ab/vulca_structured_gpt_image_2.png`
- writes `iters/ab/results.json`
- if OpenAI returns billing hard limit, writes `verdict: blocked_billing_hard_limit_reached`

The runner should use `httpx` directly instead of `OpenAIImageProvider` so 400 response bodies are preserved.

- [ ] **Step 2: Verify runner imports**

Run:

```bash
python3 -m py_compile docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/run_ab_experiment.py
```

Expected: exit 0.

### Task 3: Execute Or Block With Evidence

**Files:**
- Modify: `docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/execution_log.md`
- Create or modify: `docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/iters/ab/results.json`

- [ ] **Step 1: Run the experiment only after upload approval**

Run:

```bash
set -a; . /Users/yhryzy/dev/vulca/.env.local; set +a; python3 docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/run_ab_experiment.py
```

Expected success: both image files exist and `results.json` has `verdict: completed`.

Expected provider-blocked result: `results.json` has `verdict: blocked_billing_hard_limit_reached` and includes the OpenAI response body showing `Billing hard limit has been reached.`

- [ ] **Step 2: Update execution log**

Append a run event with the actual verdict from `results.json`. If blocked, record that no image comparison can be produced until OpenAI billing hard limit is lifted or another provider is explicitly approved.

### Task 4: Verify Before Reporting

**Files:**
- Read: `docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/iters/ab/results.json`
- Read: generated image files if `verdict: completed`

- [ ] **Step 1: Verify blocked or completed state**

Run:

```bash
python3 - <<'PY'
import json
from pathlib import Path
root = Path("docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase")
result = json.loads((root / "iters/ab/results.json").read_text())
print(result["verdict"])
if result["verdict"] == "completed":
    for path in [
        root / "iters/ab/naive_gpt_image_2.png",
        root / "iters/ab/vulca_structured_gpt_image_2.png",
    ]:
        print(path, path.exists(), path.stat().st_size if path.exists() else 0)
else:
    print(result.get("blocked_reason", ""))
PY
```

Expected: either `completed` with both images present and non-empty, or `blocked_billing_hard_limit_reached` with provider evidence.

- [ ] **Step 2: Report only verified facts**

If completed, show both image paths and summarize the visible difference. If blocked, report the exact blocker and the files already prepared.
