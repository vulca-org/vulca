# Product Positioning README + Platform Plan Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reposition Vulca's public product story around the complete Discover -> Spec -> Generate -> Edit -> Evaluate workflow, while documenting platform/provider strategy and validation experiments.

**Architecture:** This is a docs-first product coherence pass. It must not touch redraw internals or provider runtime behavior. It creates stable product docs, rewrites README around the workflow, and adds tests that prevent stale public claims about model IDs, MCP tool counts, and implemented-vs-roadmap status.

**Tech Stack:** Markdown docs, pytest doc truth tests, existing Vulca skills/docs, current provider registry, current README.

---

## Source Inputs

- Product brief: `docs/product/2026-04-30-product-positioning-brief.md`
- Design spec: `docs/superpowers/specs/2026-04-30-product-positioning-platform-design.md`
- Existing README: `README.md`
- Visual discovery spec: `docs/superpowers/specs/2026-04-29-visual-discovery-design.md`
- Visual discovery skill: `.agents/skills/visual-discovery/SKILL.md`
- Competitive landscape: `docs/superpowers/specs/2026-04-20-competitive-landscape.md`
- Redraw plan, for boundaries only: `docs/superpowers/plans/2026-04-28-v0.21-redraw-recontract.md`

## File Structure

- Create: `docs/product/roadmap.md`
  - Public product roadmap: current, next, later, experiments.
- Create: `docs/product/provider-capabilities.md`
  - Provider/backend matrix for OpenAI, Gemini, ComfyUI, mock, and agent surfaces.
- Create: `docs/product/experiments/cultural-term-efficacy.md`
  - Benchmark protocol for testing whether culture/taste analysis improves generation.
- Modify: `README.md`
  - Reposition first viewport and capability matrix.
- Modify: `tests/test_visual_discovery_docs_truth.py`
  - Add public-doc truth tests for stale tool counts and implemented/roadmap phrasing.
- Optional Modify: `pyproject.toml`
  - Only if public package description still contradicts the new product thesis.

---

## Task 1: Product Roadmap Doc

**Files:**
- Create: `docs/product/roadmap.md`

- [ ] **Step 1: Write the roadmap doc**

Create `docs/product/roadmap.md` with:

```markdown
# Vulca Product Roadmap

**Status:** Public product roadmap
**Last updated:** 2026-04-30

Vulca is an agent-native visual control layer. The product turns fuzzy visual intent into controlled creative production through reviewable artifacts, provider-routed generation, semantic pixel editing, and cultural evaluation.

## Current

- `/decompose`: semantic layer extraction into transparent PNG artifacts.
- `/visual-discovery`: fuzzy intent -> taste profile -> direction cards -> discovery artifacts.
- `/visual-brainstorm`, `/visual-spec`, `/visual-plan`: proposal/design/plan workflow for controlled generation.
- Provider registry: `mock`, `gemini`, `nb2`, `openai`, `comfyui`.
- MCP tools for image generation, image viewing, evaluation, inpainting, layers, redraw, compositing, paste-back, and Tool Protocol analysis.
- 13 cultural traditions and L1-L5 evaluation framework.

## Next

- README repositioning around the full Discover -> Spec -> Generate -> Edit -> Evaluate workflow.
- `/evaluate` skill packaging on top of existing `evaluate_artwork`.
- Provider capability matrix for public docs.
- Cultural-term efficacy benchmark.

## In Parallel

- v0.22 target-aware mask refinement in `.worktrees/v0-22-mask-refinement`.
- This work owns redraw robustness and should land before `/inpaint` or `/redraw-layer` is marketed as a polished user-facing skill.

## Later

- `/inpaint` or `/redraw-layer` skill once redraw routes are robust.
- OpenAI/Codex and Gemini-facing usage guides.
- Lightweight Studio review UI for direction cards, sketch grids, layers, and evaluation reports.

## Non-Goals

- Hosting a foundation image/video model.
- Competing with one-click image models on raw generation quality.
- Building a general-purpose design app before artifact contracts stabilize.
```

- [ ] **Step 2: Verify no unfinished markers**

Run:

```bash
grep -nE "TB[D]|TO[D]O|coming soo[n]|lo[r]em" docs/product/roadmap.md
```

Expected: no matches.

- [ ] **Step 3: Commit**

```bash
git add docs/product/roadmap.md
git commit -m "docs(product): add vulca roadmap"
```

---

## Task 2: Provider Capability Doc

**Files:**
- Create: `docs/product/provider-capabilities.md`

- [ ] **Step 1: Write the provider matrix**

Create `docs/product/provider-capabilities.md` with:

```markdown
# Vulca Provider and Platform Capability Matrix

**Status:** Public product guide
**Last updated:** 2026-04-30

Vulca separates agent surfaces from image providers.

## Agent Surfaces

| Surface | Role | Status |
|---|---|---|
| Claude Code | Primary agent surface for MCP tools and skills | Current |
| OpenAI Codex / ChatGPT developer surfaces | Future agent surface; OpenAI is already a provider backend | Planned |
| Gemini / Antigravity-like developer agents | Future agent surface for Google-native workflows | Planned |
| Python SDK / CLI | Power-user and test harness path | Current |
| Vulca Studio UI | Review surface for cards, sketches, layers, and evaluations | Later |

## Image Providers

| Provider | Current role | Use it for | Avoid using it for |
|---|---|---|---|
| `mock` | Cost-free artifact validation | tests, discovery sketch records, workflow dry-runs | quality claims |
| `openai` | High-quality generation/editing backend | final candidates, image edits, text-heavy visuals when model supports it | assuming every model supports every edit knob |
| `gemini` / `nb2` | Gemini image backend | sketching, reference-heavy exploration, alternative provider comparisons | treating marketing names as implementation IDs |
| `comfyui` | Local generation/editing backend | local-first workflows, inspectable pipelines, advanced users | assuming cloud-model prompt behavior |

## Documentation Rules

- Describe capability classes in public prose.
- Put model IDs in examples and matrices.
- Keep capability gates in code.
- Do not write fixed MCP tool counts in public docs.
- Treat real-provider discovery sketches as explicit opt-in.
```

- [ ] **Step 2: Verify current provider IDs**

Run:

```bash
PYTHONPATH=src python3 - <<'PY'
import vulca.providers as providers
providers._lazy_load_providers()
print(sorted(providers._IMAGE_PROVIDERS))
PY
```

Expected includes `comfyui`, `gemini`, `mock`, `nb2`, `openai`.

- [ ] **Step 3: Commit**

```bash
git add docs/product/provider-capabilities.md
git commit -m "docs(product): add provider capability matrix"
```

---

## Task 3: Cultural-Term Efficacy Benchmark Doc

**Files:**
- Create: `docs/product/experiments/cultural-term-efficacy.md`

- [ ] **Step 1: Write the experiment protocol**

Create `docs/product/experiments/cultural-term-efficacy.md` with:

```markdown
# Cultural-Term Efficacy Experiment

**Status:** Experiment protocol
**Last updated:** 2026-04-30

## Question

Do cultural and taste terms improve generated visual outputs, or do concrete visual operations and avoid lists carry most of the signal?

## Prompt Conditions

| Condition | Prompt shape |
|---|---|
| A | User prompt only |
| B | User prompt + cultural terms |
| C | User prompt + cultural terms + visual operations |
| D | Full direction-card prompt with avoid list and evaluation focus |

## Providers

- OpenAI GPT Image provider.
- Gemini image provider.
- ComfyUI local provider.

`mock` may validate artifact structure but must not be used for quality conclusions.

## Projects

Run at least three domains:

- premium tea packaging with xieyi restraint;
- editorial poster with spiritual but non-religious atmosphere;
- product campaign visual with culturally specific material references.

## Metrics

- Human preference.
- L1-L5 cultural/evaluation score.
- Cliche avoidance.
- Prompt adherence.
- Editability and layer separability.
- Cost and latency.
- Failure class.

## Output Artifacts

Each run writes:

```text
docs/product/experiments/results/<date>-<slug>/
  prompts/
  images/
  evaluations/
  human_ranking.json
  provider_costs.json
  summary.md
```

## Decision Rule

If condition D does not outperform A/B/C on at least two of three domains for human preference and cliche avoidance, product language must shift from "culture terms guide models" to "Vulca converts culture analysis into visual operations and evaluation criteria."
```

- [ ] **Step 2: Verify no quality claim without experiment**

Run:

```bash
grep -nE "proves|guarantees|always improves|best" docs/product/experiments/cultural-term-efficacy.md
```

Expected: no matches.

- [ ] **Step 3: Commit**

```bash
git add docs/product/experiments/cultural-term-efficacy.md
git commit -m "docs(product): define cultural term efficacy experiment"
```

---

## Task 4: README Repositioning

**Files:**
- Modify: `README.md`
- Test: `tests/test_visual_discovery_docs_truth.py`

- [ ] **Step 1: Add README truth tests**

Extend `tests/test_visual_discovery_docs_truth.py` with:

```python
def test_readme_leads_with_full_visual_workflow():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    first_screen = readme[:2500].lower()

    assert "discover" in first_screen
    assert "generate" in first_screen
    assert "edit" in first_screen
    assert "evaluate" in first_screen
    assert "one-click" in first_screen or "one shot" in first_screen


def test_public_docs_do_not_overclaim_cultural_terms():
    public_text = "\n".join(
        [
            (ROOT / "README.md").read_text(encoding="utf-8"),
            (ROOT / "docs" / "product" / "roadmap.md").read_text(encoding="utf-8"),
            (ROOT / "docs" / "product" / "experiments" / "cultural-term-efficacy.md").read_text(encoding="utf-8"),
        ]
    ).lower()

    forbidden = [
        "culture terms guarantee",
        "cultural terms guarantee",
        "always improves generation",
        "proves cultural prompting",
    ]
    for phrase in forbidden:
        assert phrase not in public_text
```

- [ ] **Step 2: Run tests to verify they fail before README changes**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: FAIL on `test_readme_leads_with_full_visual_workflow`.

- [ ] **Step 3: Rewrite README first viewport**

Replace the current headline paragraph and early `/decompose`-first framing with:

```markdown
**Vulca turns fuzzy visual intent into controlled creative production.**

Discover the direction, compile the brief, route the model, edit the pixels,
and evaluate the result — as agent-native artifacts and MCP tools.

One-click models are getting stronger. Vulca does not try to beat them at raw
generation. Vulca sits around them: it helps agents clarify what should be made,
choose and constrain the right provider, preserve non-target pixels during edits,
and record why a result does or does not fit the cultural and visual brief.

```text
fuzzy intent
  -> /visual-discovery
  -> /visual-brainstorm
  -> /visual-spec
  -> /visual-plan
  -> generate / decompose / edit / evaluate
  -> archived artifacts
```
```

Keep the existing `/decompose` showcase, but move it below the product thesis and capability matrix.

- [ ] **Step 4: Add product capability matrix**

Add near the top:

```markdown
| Stage | What Vulca gives the agent | Status |
|---|---|---|
| Discover | Taste/culture profile, direction cards, sketch prompts | PR-ready |
| Specify | `proposal.md`, `design.md`, `plan.md` | Current |
| Generate | Provider-routed image calls across OpenAI, Gemini, ComfyUI, mock | Current |
| Edit | Semantic layers, masks, redraw, inpaint, composite, paste-back | Current + v0.22 hardening |
| Evaluate | L1-L5 cultural and visual scoring | Tool current, skill next |
| Archive | Prompts, masks, layers, evaluations, errors, user overrides | Current |
```

- [ ] **Step 5: Run README tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add README.md tests/test_visual_discovery_docs_truth.py
git commit -m "docs: reposition readme around visual control workflow"
```

---

## Task 5: Final Verification

**Files:**
- Verify all product docs and README tests.

- [ ] **Step 1: Run focused docs tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py tests/test_visual_discovery_skill_contract.py -q
```

Expected: all pass.

- [ ] **Step 2: Run unfinished-marker scan**

Run:

```bash
grep -RInE "TB[D]|TO[D]O|lo[r]em|coming soo[n]" docs/product docs/superpowers/specs/2026-04-30-product-positioning-platform-design.md docs/superpowers/plans/2026-04-30-product-positioning-readme-platform.md README.md
```

Expected: no matches. If there is a match, inspect and remove it unless it is historical context.

- [ ] **Step 3: Confirm no redraw internals changed**

Run:

```bash
git diff --name-only master...HEAD | grep -E '^src/vulca/layers|^tests/test_layers_redraw|^src/vulca/providers/openai_provider.py' || true
```

Expected: no matches from this branch's new commits. If matches appear only because this branch is stacked on `codex/visual-discovery`, note that in the PR body; do not edit redraw internals here.

- [ ] **Step 4: Open draft PR**

Run:

```bash
git push -u origin codex/product-positioning-plan
gh pr create --draft --base codex/visual-discovery --head codex/product-positioning-plan --title "[codex] reposition vulca product workflow" --body "Docs-first product positioning plan. Base is codex/visual-discovery because it depends on PR #21."
```

Expected: draft PR URL.

---

## Execution Options

Plan complete. Two execution options:

1. **Subagent-Driven (recommended)** - dispatch a fresh worker per task and review after each.
2. **Inline Execution** - execute docs tasks in this session with checkpoints.
