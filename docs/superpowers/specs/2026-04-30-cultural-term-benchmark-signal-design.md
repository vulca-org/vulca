# Cultural-Term Benchmark Signal Design

## Status

approved_for_implementation

## Context

The real-provider harness is now available, but the dry-run output showed weak experiment inputs: only `premium-tea-packaging` produced a selected direction card with a concrete culture term. `spiritual-editorial-poster` and `cultural-material-campaign` fell back to generic direction cards with empty `Culture terms:` text in condition D. Running real image generation on those inputs would under-test Vulca's product thesis around culture/taste analysis plus scheme construction.

## Goal

Make every cultural-term efficacy benchmark project produce a selected direction card with a non-empty culture term and concrete visual operations before any real-provider run.

## Non-Goals

- Do not run real providers.
- Do not add Gemini or ComfyUI execution.
- Do not build a broad cultural ontology.
- Do not change provider credentials, base URL handling, or generated artifact schema.

## Approach

- Keep `premium-tea-packaging` unchanged because it already extracts `reserved white space`.
- In the benchmark harness, when `infer_taste_profile()` cannot extract terms from a project, use that project's explicit `tradition_terms` as benchmark seed terms. This is scoped to the experiment harness, not a global profile inference behavior change.
- Add concrete visual-operation entries for benchmark-specific terms:
  - `sacred atmosphere`
  - `quiet symbolism`
  - `material culture`
  - `specific craft`
  - `local texture`
- Add tests proving all benchmark projects produce non-empty culture terms, non-empty D prompt `Culture terms`, negative prompts, and evaluation focus.

## Acceptance Criteria

- `select_direction_card()` returns a card with at least one culture term for all three benchmark projects.
- Condition B/C/D records carry at least one culture term for all three benchmark projects.
- Condition D prompt does not contain an empty `Culture terms:` block for any benchmark project.
- Spiritual and material benchmark projects no longer rely on the generic fallback visual operations for their selected cards.
- Existing dry-run and real-provider fail-closed behavior remains intact.
