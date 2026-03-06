# VULCA Real-Mode Ablation Analysis Report

**Date**: 2026-02-17
**Author**: Yu Haorui + Claude Code
**Status**: Critical analysis — open questions remain

---

## 1. Experiment Setup

- **Mode**: Real (FLUX images via Together.ai + DeepSeek LLM)
- **Conditions**: C (FLUX+Rules+SingleRound) vs D (FLUX+LLM+MultiRound+Routing)
- **Tasks**: 30 (10 poetic + 10 cultural + 10 taboo)
- **Results**: 60/60 successful runs
- **Total cost**: $0.79
- **Results dir**: `blind_eval/results/ablation/run_20260217_142022/`

## 2. Raw Results

### Condition Summary

| Cond | Label | Avg Score | Avg Rounds | Accept% | Rerun% | Avg Latency | Cost |
|:----:|:------|:---------:|:----------:|:-------:|:------:|:-----------:|:----:|
| C | baseline-strong | 0.898 | 1.0 | 23% | 0% | 13.3s | $0.360 |
| D | agent-strong | 0.849 | 1.2 | 90% | 10% | 108.8s | $0.432 |

### L1-L5 Dimension Averages

| Cond | L1 Visual | L2 Technical | L3 Cultural | L4 Critical | L5 Aesthetic |
|:----:|:---------:|:------------:|:-----------:|:-----------:|:------------:|
| C | 0.850 | 0.850 | 0.987 | 0.933 | 0.833 |
| D | 0.850 | 0.850 | 0.951 | 0.943 | 0.647 |

### Statistical Tests (Paired Wilcoxon signed-rank)

| Metric | Wilcoxon stat | p-value | Cohen's d | Significance |
|--------|:------------:|:-------:|:---------:|:------------:|
| Overall weighted_total | 13.0 | 0.000006 | -1.381 | *** |
| L1 Visual | — | — | — | identical |
| L2 Technical | — | — | — | identical |
| L3 Cultural | 0.0 | 0.180 | -0.256 | ns |
| L4 Critical | 0.0 | 0.157 | +0.263 | ns |
| **L5 Aesthetic** | **19.0** | **0.000014** | **-1.396** | **\*\*\*** |

### Category Breakdown

| Category | C Score | D Score | Δ | D Rounds |
|----------|:-------:|:-------:|:-:|:--------:|
| Poetic | 0.911 | 0.863 | -0.048 | 1.0 |
| Cultural | 0.908 | 0.858 | -0.050 | 1.2 |
| Taboo | 0.873 | 0.826 | -0.047 | 1.4 |

### Multi-Round Tasks (D condition, 3/30 triggered)

| Task | Category | Tradition | R1 | R2 | R3 | Final | Latency |
|------|----------|-----------|:---:|:---:|:---:|:-----:|:-------:|
| vulca-bench-0020 | cultural | african_traditional | 0.736 | 0.735 | — | 0.733 | 226.6s |
| bench-010 | taboo | western_academic | 0.613 | 0.624 | 0.595 | 0.626 | 476.0s |
| bench-020 | taboo | islamic_geometric | 0.694 | 0.654 | — | 0.654 | 481.1s |

### Score Distributions

- **C**: Only 3 unique scores (0.618, 0.908, 0.948) — deterministic rule output
- **D**: 30 unique scores (0.626–0.917) — LLM introduces variance

### Image Output

- **240 real FLUX images** (120 per condition, 4 candidates × 30 tasks)
- Image size: 200-315KB each (JPEG, 512×512)
- Location: `checkpoints/draft/abl-{C|D}_{task_id}/`
- Windows path: `I:\website\wenxin-backend\app\prototype\checkpoints\draft\`

---

## 3. Critical Analysis — What Are We Actually Facing?

### 3.1 Experimental Design Problem — What Are We Measuring?

Current C vs D comparison confounds **three variables**:

1. **Different seeds** → different images (`_deterministic_seed()` includes condition name in hash)
2. **Different scoring** → rules vs LLM
3. **Different loop strategy** → 1 round vs max 3 rounds

The paper argues "Agent Loop improves cultural art generation", but:

- **D scores LOWER (0.849 < 0.898)**. We interpret this as "LLM is more stringent", but a reviewer will ask: **how do you prove lower = more accurate?** There is no ground truth. No human annotator has said "this image's L5 should be 0.38, not 0.83".
- Even if we fix seeds so images are identical, D will still score lower. But that only proves "LLM scoring differs from rules", not "LLM scoring is better".

### 3.2 Multi-Round Loop — Core Selling Point Fails

The paper title is "Self-Correction", but actual data:

```
bench-010:        R1=0.613 → R2=0.624 → R3=0.595  (no improvement)
bench-020:        R1=0.694 → R2=0.654              (got worse)
vulca-bench-0020: R1=0.736 → R2=0.735              (no change)
```

None of the 3 multi-round tasks showed self-correction. This is "self-retry with random seed", not "self-correction".

### 3.3 VLM Pathway Broken — "Hybrid" Is Hollow

We claim: hybrid scoring = rules (L1/L2) + LLM text (L3-L5) + VLM vision (L1/L2).

Reality:
- **L1/L2**: Always rules (0.850), VLM never called
- **L3/L4**: LLM has minor effect (Δ=-0.036 ns, +0.010 ns)
- **L5**: Only dimension with significant difference (Δ=-0.186 ***)

So "hybrid five-layer scoring" is actually "L5-only LLM scoring + 4 layers of rules". This undermines the architecture narrative.

### 3.4 Product Value Question

From a user's perspective:
- **C**: 13s, $0.012/run, score 0.898
- **D**: 109s, $0.014/run, score 0.849

D takes **8× longer**, gives **lower scores**, and multi-round doesn't improve results. Why would a user choose D?

"Stricter scoring" only has value when it **guides improvement**. If scoring is just lower without helping users generate better images, it's a slower, more expensive, worse experience.

### 3.5 Claims vs Evidence

| Claim | Evidence | Gap |
|-------|----------|-----|
| LLM provides more accurate cultural assessment | L5 scores lower, p<0.001 | No ground truth that "lower = more accurate" |
| Multi-agent loop enables self-correction | 3/30 triggered, scores didn't improve | Loop doesn't produce directional improvement |
| Hybrid five-layer scoring | Only L5 differs | L1-L4 LLM contribution ≈ 0 |
| Cultural routing improves quality | Routing on/off affects scores | C has no routing, D has it — another confound |
| FixItPlan enables targeted repair | Generated but scores unchanged | prompt_delta doesn't change rule-evaluated features |

---

## 4. Root Cause Diagnosis

### 4.1 The Workflow IS Working

Contrary to initial suspicion, the FixItPlan → prompt_delta → new prompt pathway **is closed**. Evidence from bench-010 Round 3 prompt:

```
A western academic artwork depicting: primitive art tribal art savage exotic,
strengthen interpretive depth with critical vocabulary,
ground interpretation in tradition evidence,
embed philosophical and aesthetic cultural keywords,
ensure cultural purity in philosophical expression,
broaden terminology coverage for deeper resonance,
Western academic oil painting, realistic, classical composition...
```

The "strengthen interpretive depth..." portion is the FixItPlan's prompt_delta, successfully consumed.

### 4.2 The Scoring Algorithm IS the Problem

The rule-based scoring system evaluates **prompt metadata, not the generated image**:

| Rule Check | What It Actually Evaluates | Looks at Image? |
|------------|---------------------------|:---------------:|
| L1: `has_style` | Does prompt contain style keywords? | No |
| L1: `has_terms` | Did Scout find terminology? | No |
| L1: `len(prompt) > 50` | Is prompt long enough? | No |
| L2: `steps >= 15` | Inference step count | No |
| L2: `sampler` | Is sampler name present? | No |
| L3: `len(term_hits)` | Number of terminology matches | No |
| L3: `taboo_violations` | Any taboo detected? | No |
| L5: `"culture" in prompt` | Does prompt mention culture? | No |

**Not a single line of rule scoring code looks at the generated image.**

Rules are **binary checklist** (has/doesn't have), not **quality gradient** (how well). Adding FixItPlan keywords to the prompt doesn't change whether the original checks pass — they already passed in Round 1.

This means: **rule scores are mathematically invariant across rounds** for the same task, regardless of image quality.

### 4.3 LLM Scoring Doesn't See Images Either

- DeepSeek (L3-L5): Text-only LLM, scores based on prompt text and evidence context
- Gemini VLM (L1-L2): Can see images, but **not invoked** in ablation (falls back to rules)
- Result: Even in condition D, only L5 gets LLM scoring, and that LLM can't see the generated image

### 4.4 Why Self-Correction Cannot Work Currently

```
Round N: Generate image → Score (rules check prompt, not image) → Low score
         ↓
         FixItPlan: "add aesthetic keywords to prompt"
         ↓
Round N+1: Generate new image (with enriched prompt)
         → Score (rules check prompt... same features still pass)
         → Same score ± LLM random variance
```

The loop is structurally incapable of self-correction because the feedback signal (score) doesn't measure the output (image). It measures the input (prompt/config).

---

## 5. What the Data Actually Supports

### Can Claim (with evidence)

1. **FLUX generates culturally relevant high-quality images** — 240 real images across 8 traditions
2. **DeepSeek LLM provides statistically different L5 aesthetic scoring** — p=0.000014, Cohen's d=-1.40
3. **Cultural taboo scenarios trigger more scrutiny rounds** — taboo 1.4 rounds vs poetic 1.0
4. **LLM scoring produces individualized assessments** — 30 unique scores vs 3 from rules
5. **The multi-agent architecture technically supports multi-round loops** — 3/30 triggered, ran to completion

### Cannot Claim (insufficient evidence)

1. Multi-round loop improves generation quality
2. LLM scoring is more accurate than rules (no ground truth)
3. FixItPlan produces targeted image improvement
4. Hybrid five-layer scoring (only L5 is hybrid in practice)

---

## 6. Key Questions for Next Steps

### Q1: What is the paper's core contribution?

If self-correction doesn't work, the contribution may need repositioning:
- **Option A**: L1-L5 cultural evaluation framework itself (VULCA-Bench extends)
- **Option B**: LLM as a more discriminating scorer (L5 statistical evidence)
- **Option C**: Agent architecture design (contribution is the design, not the results)
- **Option D**: Fix the scoring to make self-correction work, then rerun

### Q2: What does it take to make self-correction actually work?

The scoring must evaluate the **generated image**, not just prompt metadata. Paths:
1. **Fix VLM pathway** — Make Gemini actually score L1/L2 by looking at images
2. **Add image-aware rules** — e.g., CLIP similarity between image and cultural reference
3. **Feed images to DeepSeek** — Use base64 image in LLM prompt (if supported)
4. **Use GalleryGPT/KOALA** — Already deployed, can provide image-level aesthetic scores

### Q3: How much does fixing seeds matter?

Same-seed experiment isolates scoring method difference from image quality difference. This is methodologically important but doesn't fix the fundamental scoring problem.

---

## 7. Files and Paths

| Item | Path |
|------|------|
| Raw results JSON | `blind_eval/results/ablation/run_20260217_142022/all_results.json` |
| Experiment config | `blind_eval/results/ablation/run_20260217_142022/experiment_config.json` |
| Auto-generated report | `blind_eval/results/ablation/run_20260217_142022/ablation_report.md` |
| FLUX images (Win) | `I:\website\wenxin-backend\app\prototype\checkpoints\draft\abl-{C\|D}_{task}\` |
| Critic checkpoints | `checkpoints/critique/abl-{C\|D}_{task}/run.json` |
| Queen checkpoints | `checkpoints/pipeline/abl-{C\|D}_{task}/stage_queen.json` |
| Rule scoring code | `agents/critic_rules.py` |
| Orchestrator | `orchestrator/orchestrator.py` |
| Browser screenshot | `prototype-llm-pipeline-complete.png` (project root) |

---

## 8. Session Deliverables (2026-02-17)

1. **3 Bug Fixes**: P0 rerun_local fallback + P1 best candidate prompt + P1 agent_mode SSE
2. **Frontend agent_mode visualization**: Green/yellow/gray badge + degradation warning
3. **First browser verification**: LLM pipeline 75.9s end-to-end in browser
4. **Real-mode ablation**: 60/60 FLUX runs, 240 real images, statistical tests
5. **Root cause diagnosis**: Scoring evaluates prompt, not image — structural blocker for self-correction
