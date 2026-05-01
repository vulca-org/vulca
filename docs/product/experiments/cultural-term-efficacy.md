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

## Harness

Run the no-cost dry-run harness with:

```bash
PYTHONPATH=src python3 scripts/visual_discovery_benchmark.py --date 2026-04-30
```

The default harness writes prompts, manifests, empty result records, and summaries. It does not call OpenAI, Gemini, ComfyUI, or `mock` for quality evidence.

Real provider execution requires explicit opt-in:

```bash
VULCA_REAL_PROVIDER_BASE_URL=https://example.openai-compatible-gateway.test \
VULCA_REAL_PROVIDER_API_KEY=... \
VULCA_REAL_PROVIDER_MODEL=gpt-image-2 \
PYTHONPATH=src python3 scripts/visual_discovery_benchmark.py \
  --real-provider \
  --provider openai \
  --slug premium-tea-packaging \
  --output-root /private/tmp/vulca-cultural-term-real-provider \
  --date 2026-04-30
```

Never put live API keys in repository files, generated artifacts, PR bodies, or documentation. Use local environment variables or a secret manager.

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

## Successor: Real-Brief Benchmark

The cultural-term prompt signal test is useful for isolating whether cultural
terms alone move model output, but it is weaker than real briefs as product
evidence. Real briefs include client context, deliverables, constraints,
timelines, risks, and approval questions, so they better test whether Vulca
turns messy creative inputs into reviewable decision and production packages.

Use `scripts/real_brief_benchmark.py` for the successor dry-run harness:

```bash
PYTHONPATH=src python3 scripts/real_brief_benchmark.py --date 2026-05-01
```
