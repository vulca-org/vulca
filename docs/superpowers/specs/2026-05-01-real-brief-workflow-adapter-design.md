# Real Brief Workflow Adapter Design

**Date:** 2026-05-01
**Status:** Approved design for implementation planning
**Branch:** `codex/real-brief-workflow-adapter`
**Scope:** Phase 2 adapter that imports Phase 1 real-brief packages into the official Vulca visual workflow artifact tree.

## Decision

Build Phase 2 as an **artifact-first workflow adapter**.

The adapter consumes a Phase 1 real-brief dry-run package and writes official workflow entry artifacts under `docs/visual-specs/<slug>/`. It must make the real brief usable by the existing chain:

```text
/visual-discovery -> /visual-brainstorm -> /visual-spec -> /visual-plan -> /evaluate
```

It must not silently bypass the human gates already required by those skills. In Phase 2, the adapter prepares seeds, review context, and discovery artifacts. It does not auto-finalize `proposal.md`, `design.md`, or `plan.md`.

## Product Goal

The product direction is no longer "a visual-discovery tool only." The product direction is:

```text
real creative work -> structured intent -> direction discovery -> reviewable plan -> controlled generation -> evaluation
```

The Phase 1 benchmark proved that one-shot model output is hard to judge when briefs are vague. Phase 2 turns the benchmark into a reusable workflow so Vulca can show where it adds value:

- clarifying ambiguous client intent;
- turning cultural and taste language into concrete visual operations;
- preserving source constraints and production risks;
- giving the user direction cards before final pixels;
- making handoff packages reviewable by designers, directors, artists, and clients;
- preparing future review/studio surfaces without coupling them to a specific HTML prototype.

## Current Inputs

Phase 1 writes packages like:

```text
docs/product/experiments/real-brief-results/<date>-<slug>/
  source_brief.md
  structured_brief.json
  decision_package.md
  production_package.md
  workflow_handoff.json
  review_schema.json
  manifest.json
  conditions/
  prompts/
  images/
  evaluations/
  human_review.html
  summary.md
```

The Phase 2 adapter must treat these files as the source package. The required input files are:

- `manifest.json`
- `workflow_handoff.json`
- `structured_brief.json`
- `decision_package.md`
- `production_package.md`
- `review_schema.json`

Optional but preserved when present:

- `source_brief.md`
- `human_review.html`
- `conditions/*.md`
- `prompts/*.txt`
- `images/*`
- `evaluations/*`
- `summary.md`

## Output Artifact Tree

For a source package with `slug = seattle-polish-film-festival-poster`, the adapter writes:

```text
docs/visual-specs/seattle-polish-film-festival-poster/
  discovery/
    discovery.md
    taste_profile.json
    direction_cards.json
    sketch_prompts.json
  real_brief/
    adapter_manifest.json
    source_package_manifest.json
    structured_brief.json
    workflow_handoff.json
    decision_package.md
    production_package.md
    review_schema.json
    source_brief.md
    summary.md
    conditions/
    prompts/
    images/
    evaluations/
  workflow_seed.md
```

`discovery/` is the official upstream artifact location consumed by `/visual-discovery` and handed to `/visual-brainstorm`.

`real_brief/` is a lossless package copy with adapter metadata. It preserves benchmark and review context without polluting the canonical proposal/design/plan files.

`workflow_seed.md` is a human-readable handoff guide. It tells the user what the adapter imported and what to run next.

## Non-Goals

Phase 2 must not:

- generate or edit images;
- call real providers;
- call redraw, mask, decompose, or layer tools;
- finalize `proposal.md`;
- finalize `design.md`;
- finalize or execute `plan.md`;
- mutate Phase 1 result packages in place;
- depend on the redraw replacement branch;
- write provider keys, endpoints, or secrets into artifacts;
- submit or imply submission-readiness for AI-prohibited source briefs.

## Adapter Contract

### Input Validation

The adapter validates:

- source package path exists and is a directory;
- required files exist;
- `manifest.schema_version == "0.1"`;
- `manifest.experiment == "real-brief-benchmark"`;
- `manifest.provider_execution == "disabled"` for Phase 2 v1;
- `workflow_handoff.schema_version == "0.1"`;
- `workflow_handoff.human_gate_required is true`;
- `workflow_handoff.slug == structured_brief.slug == manifest.fixture.slug`;
- slug passes the same safe-slug rules used by `vulca.real_brief.types.safe_slug`;
- every copied path stays inside the source package and destination project directory;
- generated text contains no known secret markers.

If validation fails, no partial destination tree should be left behind. Use a temp directory plus atomic rename where practical.

### Collision Policy

The adapter must not overwrite an existing finalized workflow.

Rules:

- If `docs/visual-specs/<slug>/proposal.md` exists with `status: ready`, abort.
- If `docs/visual-specs/<slug>/design.md` exists with `status: resolved`, abort.
- If `docs/visual-specs/<slug>/plan.md` exists with terminal status, abort.
- If `discovery/` already exists, require `--force-discovery` to replace only adapter-owned discovery files.
- If `real_brief/` already exists, require `--force-real-brief` to replace only adapter-owned real-brief files.

The first implementation should keep this conservative. Re-import and merge behavior is explicitly out of scope for Phase 2.

### Domain Mapping

The adapter maps `structured_brief.domain` to the existing visual workflow domain enum when possible:

| source domain | visual workflow domain | status |
|---|---|---|
| `poster` | `poster` | supported |
| `packaging` | `packaging` | supported |
| `brand_visual` | `brand_visual` | supported |
| `illustration` | `illustration` | supported |
| `editorial_cover` | `editorial_cover` | supported |
| `photography_brief` | `photography_brief` | supported |
| `hero_visual_for_ui` | `hero_visual_for_ui` | supported |
| `public_art` | none | unsupported for visual chain v1 |
| `video_treatment` | none | unsupported for visual chain v1 |
| other video or treatment-only domains | none | unsupported for visual chain v1 |

The existing `erie-botanical-gardens-public-art` and `music-video-treatment-low-budget` fixtures remain useful for Phase 1 benchmarking, but Phase 2 v1 must not force them into the static 2D visual chain. They should produce real-brief import packages and mark:

```json
{
  "workflow_status": "unsupported_for_visual_chain",
  "reason": "source domain is outside /visual-brainstorm static 2D scope"
}
```

## Discovery Artifact Generation

For supported static 2D briefs, the adapter uses existing discovery internals rather than inventing a second artifact shape:

- `vulca.discovery.profile.infer_taste_profile`
- `vulca.discovery.cards.generate_direction_cards`
- `vulca.discovery.prompting.compose_prompt_from_direction_card`
- `vulca.discovery.artifacts.write_discovery_artifacts`

Input intent should combine:

- `workflow_handoff.visual_discovery_seed.initial_intent`;
- source client/context/audience from `structured_brief.json`;
- constraints, risks, and avoid lists;
- selected direction/card data already present in Phase 1 condition C/D when available.

The output `discovery.md` must end in `ready_for_brainstorm`, not `proposal_ready` or `ready_for_spec`. `/visual-brainstorm` remains the next human gate.

## Workflow Seed

`workflow_seed.md` is a concise operator-facing handoff:

```markdown
# Real Brief Workflow Seed: <title>

## Status
ready_for_visual_brainstorm

## Source Package
<relative path>

## Imported Artifacts
- discovery/discovery.md
- discovery/taste_profile.json
- discovery/direction_cards.json
- real_brief/structured_brief.json
- real_brief/decision_package.md
- real_brief/production_package.md

## Recommended Next Step
Run /visual-brainstorm <slug> using the discovery handoff below.

## Discovery Handoff
<handoff string from discovery artifacts>

## Human Gates Preserved
- /visual-brainstorm must finalize proposal.md
- /visual-spec must resolve design.md
- /visual-plan must review plan.md before generation

## Unsupported Or Deferred Items
<none or reason>
```

This file is not a substitute for `proposal.md`. It is a bridge for humans and agents.

## Adapter Manifest

`real_brief/adapter_manifest.json` is the machine contract for future Review Surface / Studio work:

```json
{
  "schema_version": "0.1",
  "adapter": "real-brief-workflow-adapter",
  "source_experiment": "real-brief-benchmark",
  "source_package_path": "docs/product/experiments/real-brief-results/2026-05-01-seattle-polish-film-festival-poster",
  "slug": "seattle-polish-film-festival-poster",
  "workflow_status": "ready_for_visual_brainstorm",
  "human_gate_required": true,
  "simulation_only": true,
  "ai_policy": "unspecified",
  "domain": "poster",
  "visual_workflow_domain": "poster",
  "created": "2026-05-01",
  "source_files": {
    "manifest": "source_package_manifest.json",
    "structured_brief": "structured_brief.json",
    "workflow_handoff": "workflow_handoff.json",
    "decision_package": "decision_package.md",
    "production_package": "production_package.md",
    "review_schema": "review_schema.json"
  },
  "workflow_artifacts": {
    "discovery_md": "../discovery/discovery.md",
    "taste_profile_json": "../discovery/taste_profile.json",
    "direction_cards_json": "../discovery/direction_cards.json",
    "workflow_seed_md": "../workflow_seed.md"
  },
  "next_steps": [
    "/visual-brainstorm seattle-polish-film-festival-poster",
    "/visual-spec seattle-polish-film-festival-poster",
    "/visual-plan seattle-polish-film-festival-poster",
    "/evaluate seattle-polish-film-festival-poster"
  ]
}
```

The manifest should store relative paths from `real_brief/` where possible, so review tools can move or archive packages without rewriting absolute paths.

## CLI

Add a new script instead of overloading Phase 1:

```bash
PYTHONPATH=src python3 scripts/real_brief_workflow_adapter.py \
  --source-package docs/product/experiments/real-brief-results/2026-05-01-seattle-polish-film-festival-poster \
  --root . \
  --date 2026-05-01
```

Flags:

- `--source-package <path>` required unless `--source-root --slug --date` is supplied.
- `--source-root <path>` optional convenience root for Phase 1 results.
- `--slug <slug>` optional when resolving from `--source-root`.
- `--date YYYY-MM-DD` required for deterministic metadata in tests.
- `--root <repo-root>` default `.`.
- `--force-discovery` opt-in replacement for adapter-owned `discovery/` files.
- `--force-real-brief` opt-in replacement for adapter-owned `real_brief/` files.
- `--dry-run` validate and print planned writes without writing files.

Default execution writes artifacts. It never calls a provider.

## Python API

Add a focused module:

```text
src/vulca/real_brief/workflow_adapter.py
```

Public API:

```python
def adapt_real_brief_package(
    *,
    source_package: str | Path,
    root: str | Path,
    date: str,
    force_discovery: bool = False,
    force_real_brief: bool = False,
    dry_run: bool = False,
) -> dict[str, str]:
    ...
```

Return shape:

```json
{
  "slug": "seattle-polish-film-festival-poster",
  "status": "ready_for_visual_brainstorm",
  "project_dir": "docs/visual-specs/seattle-polish-film-festival-poster",
  "workflow_seed_md": ".../workflow_seed.md",
  "adapter_manifest_json": ".../real_brief/adapter_manifest.json",
  "discovery_md": ".../discovery/discovery.md"
}
```

For unsupported visual-chain inputs:

```json
{
  "slug": "music-video-treatment-low-budget",
  "status": "unsupported_for_visual_chain",
  "project_dir": "docs/visual-specs/music-video-treatment-low-budget",
  "adapter_manifest_json": ".../real_brief/adapter_manifest.json"
}
```

## Error Handling

Use clear `ValueError` or `RuntimeError` messages for:

- unknown or unsafe slug;
- missing required source package files;
- schema version mismatch;
- source package not created by real-brief benchmark;
- `human_gate_required` false;
- slug mismatch across files;
- destination collision with finalized proposal/design/plan;
- unsupported domain for visual workflow;
- unsafe copy path;
- secret-like content in generated adapter files.

Unsupported static workflow domain is not a crash if the source package is otherwise valid. It writes a real-brief import package and adapter manifest, but it does not write discovery artifacts that claim `/visual-brainstorm` readiness.

## Review Surface Readiness

Phase 3 Review Surface / Studio should be able to load:

- `real_brief/adapter_manifest.json`;
- `real_brief/source_package_manifest.json`;
- `real_brief/structured_brief.json`;
- `real_brief/workflow_handoff.json`;
- `real_brief/review_schema.json`;
- `discovery/direction_cards.json`;
- future `proposal.md`, `design.md`, `plan.md`, and `evaluation.json`.

That means Phase 2 must preserve source metadata and not flatten the benchmark package into prose only.

## Tests

Add focused tests in `tests/test_real_brief_workflow_adapter.py`:

- fixture-generated Phase 1 package adapts into `docs/visual-specs/<slug>/`;
- adapter writes `discovery/discovery.md`, `taste_profile.json`, and `direction_cards.json`;
- adapter writes `real_brief/adapter_manifest.json` with correct next steps and relative paths;
- adapter copies required source files without modifying the Phase 1 source package;
- adapter writes `workflow_seed.md` and preserves human gate language;
- unsafe slugs and path traversal are rejected;
- missing required files fail before partial writes;
- existing ready `proposal.md` collision aborts;
- `erie-botanical-gardens-public-art` and `music-video-treatment-low-budget` are marked unsupported for visual chain instead of forced into `/visual-brainstorm`;
- generated artifacts contain no provider keys, live endpoints, or secret-like markers;
- CLI `--dry-run` reports planned writes and writes nothing;
- CLI normal mode writes the same files as the Python API.

Keep these existing tests green:

- `tests/test_real_brief_benchmark.py`
- `tests/test_visual_discovery_artifacts.py`
- `tests/test_visual_discovery_benchmark.py`
- `tests/test_visual_discovery_cards.py`
- `tests/test_visual_discovery_types.py`

## Implementation Boundaries

Files expected in Phase 2 implementation:

- Create `src/vulca/real_brief/workflow_adapter.py`
- Create `scripts/real_brief_workflow_adapter.py`
- Create `tests/test_real_brief_workflow_adapter.py`
- Modify `src/vulca/real_brief/__init__.py` to lazy-export `adapt_real_brief_package`
- Optionally update `docs/product/experiments/cultural-term-efficacy.md` with a short Phase 2 link

Do not modify:

- redraw, mask, decompose, or layer internals;
- provider implementations;
- MCP tool registration;
- existing `/visual-*` skill contracts unless a failing test proves the adapter cannot use them as written.

## Open Questions For Later Phases

- Whether `/visual-brainstorm` should eventually accept `--from-real-brief <path>` and prefill `proposal.md` as `draft`.
- Whether Review Surface should render `workflow_seed.md` or read only `adapter_manifest.json`.
- Whether video/director-treatment briefs should get a separate `/video-treatment` workflow instead of remaining benchmark-only.
- Whether Phase 3 should compare adapter-seeded discovery against manual `/visual-discovery` sessions.

These are intentionally deferred. Phase 2 should only make real briefs enter the existing visual workflow safely and repeatably.
