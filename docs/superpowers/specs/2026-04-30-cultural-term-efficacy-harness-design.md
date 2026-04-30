# Cultural-Term Efficacy Harness Design

## Status

approved_for_planning

## Context

Vulca now positions itself as an agent-native visual control layer, not a foundation image model. The current roadmap names two product evidence gaps: provider/platform capability clarity and a cultural-term efficacy benchmark. The provider capability matrix already exists as `docs/product/provider-capabilities.md`, so this work should first make the roadmap consistent, then turn `docs/product/experiments/cultural-term-efficacy.md` from protocol-only into a repeatable dry-run harness.

The product question is specific: do cultural and taste terms directly improve generated outputs, or does Vulca create value by translating cultural analysis into concrete visual operations, avoid lists, and evaluation criteria? The harness must support that decision without making unproven quality claims.

## Goals

- Provide a default no-cost experiment harness for the cultural-term efficacy protocol.
- Generate deterministic A/B/C/D prompt conditions for the three project domains in the protocol.
- Write the expected result directory skeleton under `docs/product/experiments/results/<date>-<slug>/`.
- Keep real provider generation behind an explicit opt-in flag.
- Prevent public docs from claiming that cultural terms are proven or guaranteed to improve outputs.
- Move the provider capability matrix out of roadmap "Next" because it already exists.

## Non-Goals

- Do not call OpenAI, Gemini, ComfyUI, or any other real image provider by default.
- Do not run image generation, evaluation, or human ranking in this first harness.
- Do not change provider APIs, MCP tools, `/visual-discovery`, `/visual-plan`, `/evaluate`, redraw, layers, or v0.22 mask refinement.
- Do not market `/inpaint` or `/redraw-layer` as polished user-facing skills.

## Recommended Approach

Extend the existing `scripts/visual_discovery_benchmark.py` into a product experiment harness. This is intentionally conservative: the script already imports the visual discovery prompt machinery and has tests. The first version should make the experiment reproducible and artifact-backed without introducing a new runtime package or provider execution path.

The script will expose library functions that tests can call directly and keep its command-line behavior as a dry-run artifact writer. Later, if the experiment needs real provider execution, a separate follow-up can add an explicit `--real-provider` path after credentials, costs, output normalization, and evaluation policy are settled.

## Experiment Conditions

The harness uses the protocol's four conditions:

| ID | Meaning | Prompt contents |
|---|---|---|
| A | User prompt only | The project's raw user prompt. |
| B | User prompt + cultural terms | Raw prompt plus the selected card's `culture_terms`. |
| C | User prompt + cultural terms + visual operations | Raw prompt plus `culture_terms` and concrete `visual_ops`. |
| D | Full direction-card prompt | `compose_prompt_from_direction_card(..., target="final")`, plus avoid list and L1-L5 evaluation focus metadata. |

This deliberately removes the older E/F conditions from `scripts/visual_discovery_benchmark.py`; those were useful scaffolding, but they no longer match the public protocol.

## Project Fixtures

The harness defines exactly three built-in projects:

- `premium-tea-packaging`: premium tea packaging with xieyi restraint.
- `spiritual-editorial-poster`: editorial poster with spiritual but non-religious atmosphere.
- `cultural-material-campaign`: product campaign visual with culturally specific material references.

Each fixture includes a slug, user prompt, expected domain, seed tradition hints, and enough input text for `infer_taste_profile()` and `generate_direction_cards()` to create a deterministic selected card.

## Artifact Contract

For each dry run, the harness writes:

```text
docs/product/experiments/results/<date>-<slug>/
  prompts/
    A.txt
    B.txt
    C.txt
    D.txt
  images/
    README.md
  evaluations/
    README.md
  human_ranking.json
  provider_costs.json
  summary.md
  manifest.json
```

`manifest.json` contains:

```json
{
  "schema_version": "0.1",
  "experiment": "cultural-term-efficacy",
  "mode": "dry_run",
  "provider_execution": "disabled",
  "project": {
    "slug": "premium-tea-packaging",
    "prompt": "..."
  },
  "conditions": [
    {
      "id": "A",
      "label": "User prompt only",
      "prompt_path": "prompts/A.txt",
      "source_card_id": ""
    }
  ],
  "providers": [
    {
      "provider": "openai",
      "model": "gpt-image-2",
      "execution": "not_run"
    }
  ]
}
```

`human_ranking.json` and `provider_costs.json` are placeholders only in the data sense: they are valid empty result records with `"status": "not_collected"` and must not contain prose placeholders.

## Safety and Product Claims

- `mock` may be used only to validate artifact structure.
- Dry-run artifacts must say that provider execution is disabled.
- Summary text must not claim that any condition improves image quality.
- Public docs must continue to avoid phrases such as "culture terms guarantee", "cultural terms guarantee", "always improves generation", and "proves cultural prompting".
- Real providers require a future explicit opt-in interface. The first harness should fail closed if asked to run real providers.

## Files

- Modify `scripts/visual_discovery_benchmark.py` to define fixtures, A-D conditions, artifact writers, and a dry-run CLI.
- Modify `tests/test_visual_discovery_benchmark.py` to expect A-D only and validate dry-run outputs.
- Modify `tests/test_visual_discovery_docs_truth.py` to lock the roadmap consistency and safety claims.
- Modify `docs/product/roadmap.md` to move the provider capability matrix into Current.
- Modify `docs/product/experiments/cultural-term-efficacy.md` to point readers at the dry-run harness and clarify explicit opt-in for real provider runs.

## Testing

- Focused benchmark tests verify prompt conditions, project fixtures, artifact tree, manifest schema, and dry-run safety.
- Docs truth tests verify roadmap consistency and public-claim boundaries.
- Existing visual discovery prompt/artifact tests remain in scope because the harness reuses direction-card generation and prompt composition.

## Open Decisions Deferred

- The scoring methodology for human rankings is deferred until there are real generated images.
- Provider-specific generation adapters are deferred until costs, credentials, and output normalization are agreed.
- `/evaluate` integration is deferred until the harness has real image artifacts.
