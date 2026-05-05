# Vulca Learning Loop v0 Design

Date: 2026-05-05
Status: approved-for-planning

## Purpose

Vulca is already evolving along several parallel workstreams: redraw hardening, decomposition/layer quality, layered generation quality, provider SDK/MCP surfaces, and future specialist models. These should not be collapsed into one implementation branch or one model project. Learning Loop v0 creates a thin data layer underneath those workstreams so each redraw or layer-edit experiment can become training and evaluation evidence.

The first milestone is not model training. It is a stable `redraw_case` record, optional case logging, and a small benchmark seed set. This gives future tiny models and tiny agents a factual substrate without changing existing runtime behavior.

## Positioning

The system should be layered by responsibility and by maturity:

- Level 0: deterministic validators and contracts
- Level 1: tool execution and artifact generation
- Level 2: case logging and benchmark data
- Level 3: tiny specialist models for narrow judgments
- Level 4: tiny agents/state machines for routing and retries
- Level 5: large agent/VLM teacher for open-ended planning, labeling, and failure review

Current redraw, decomposition, and layered-generation branches can continue independently at Levels 0-1. Learning Loop v0 sits at Level 2 and observes their output. It must not block or rewrite those branches.

Decomposition and layered generation are separate workstreams. Decomposition starts from an existing image and splits it into semantic layers, masks, residuals, and manifest records. Layered generation starts from an intent or plan and creates multiple coordinated layers as the output. They share artifact vocabulary, but the causal direction is different. Learning Loop v0 should not blur those two tasks or use one schema for both.

## Scope

Learning Loop v0 adds:

- A versioned `redraw_case` JSON schema.
- A focused `src/vulca/layers/redraw_cases.py` module for case construction and JSONL append.
- Optional case logging from `layers_redraw`, disabled by default.
- CLI/MCP visibility for `case_id` and `case_log_path` when logging is enabled.
- A documented failure taxonomy and a small benchmark seed manifest.

Learning Loop v0 does not add:

- model training
- CLIP, DINO, SmolVLM, LightGBM, or other ML dependencies
- a UI review queue
- a rewrite of `redraw.py`
- agent calls in the redraw runtime loop
- changes to decomposition execution logic
- changes to layered generation execution logic

## Redraw Case Record

Each record should be self-contained enough to train or evaluate `Vulca-FD v0` later:

```json
{
  "schema_version": 1,
  "case_id": "redraw_...",
  "created_at": "2026-05-05T00:00:00Z",
  "artwork_dir": "...",
  "source_image": "...",
  "layer": {
    "id": "...",
    "name": "...",
    "description": "...",
    "semantic_path": "...",
    "quality_status": "...",
    "area_pct_manifest": 0.0
  },
  "instruction": "...",
  "provider": "openai",
  "model": "gpt-image-2",
  "route": {
    "requested": "auto",
    "chosen": "inpaint",
    "redraw_route": "sparse_bbox_crop",
    "geometry_redraw_route": "sparse_bbox_crop"
  },
  "geometry": {
    "area_pct": 0.0,
    "bbox_fill": 0.0,
    "component_count": 1,
    "sparse_detected": true
  },
  "quality": {
    "gate_passed": true,
    "failures": [],
    "metrics": {}
  },
  "refinement": {
    "applied": false,
    "reason": "no_target_profile",
    "strategy": "none",
    "child_count": 0,
    "mask_granularity_score": 0.0
  },
  "artifacts": {
    "source_layer_path": "...",
    "redrawn_layer_path": "...",
    "source_pasteback_path": "...",
    "debug_summary_path": ""
  },
  "review": {
    "human_accept": null,
    "failure_type": "",
    "preferred_action": "",
    "reviewer": "",
    "reviewed_at": ""
  }
}
```

Paths should remain local path strings, not embedded base64. A stable `case_id` can be derived from timestamp plus a short hash over source path, layer name, instruction, provider, model, and output path.

## Failure Taxonomy

The first taxonomy should stay small and redraw-focused:

- `color_drift`
- `shape_collapse`
- `wrong_subject`
- `missing_detail`
- `over_smoothing`
- `texture_leak`
- `alpha_expansion`
- `mask_too_broad`
- `background_bleed`
- `large_white_component`
- `pasteback_mismatch`
- `route_error`
- `over_split`
- `under_split`
- `uncertain`

The taxonomy is allowed to grow, but only through explicit schema updates. Free-form notes can be added later, but the model label should stay enumerable.

## Data Flow

```text
layers_redraw
  -> redraw result + redraw_advisory + source pasteback preview
  -> redraw_cases.build_redraw_case(...)
  -> optional append_jsonl(...)
  -> MCP/CLI returns case_id and case_log_path when enabled
```

The logger should be best-effort but not silent. If logging is explicitly enabled and writing fails, the caller should receive `case_log_error` in the result payload while the redraw result remains usable.

## Branch And Workstream Boundaries

Parallel redraw optimization branches should continue to modify route selection, mask refinement, quality gates, and provider behavior. Parallel decomposition branches should continue to improve semantic paths, bbox hints, masks, residuals, and manifest quality. Parallel layered-generation branches should continue to improve plan-to-layer generation, layer coordination, per-layer prompts, composites, and generation manifests.

Learning Loop v0 should avoid direct conflict with those branches by using a new module and reading existing outputs instead of moving logic. Its integration points should be narrow:

- read `LayerInfo` and manifest metadata
- read `redraw_advisory`
- read MCP pasteback result fields
- append JSONL only when enabled

This makes the logger a shared observation layer across experiments rather than another competing redraw implementation.

Future case types should be separate records, not overloads of `redraw_case`:

- `decompose_case`: existing image -> semantic layer split
- `layer_generate_case`: plan/intent -> generated layered artifact
- `redraw_case`: existing layer/artifact -> edited layer and pasteback preview

Learning Loop v0 implements only `redraw_case`, but the module and docs should leave room for sibling case schemas later.

## Tiny Model And Tiny Agent Roadmap

After enough cases exist, the next stages are:

1. `Vulca-FD v0`: predict `accept/reject/uncertain` and `failure_type`.
2. `Vulca-Route v0`: predict route or fallback action from geometry, instruction, and prior failures.
3. `Vulca-Ranker v0`: rank multiple redraw candidates.
4. Tiny agent/state machine: use model confidence plus validators to decide `accept`, `rerun`, `fallback_to_agent`, or `fallback_to_original`.

The large agent remains the teacher and reviewer. It should not be placed in the high-frequency redraw runtime loop.

## Error Handling

- Logging disabled: no behavior change and no new output fields.
- Logging enabled and succeeds: return `case_id` and `case_log_path`.
- Logging enabled and fails: return `case_log_error`; do not fail the redraw.
- Missing optional artifacts: record empty strings, not guessed paths.
- Unknown failure type during manual review: use `uncertain`.

## Testing

Tests should cover:

- schema construction from a minimal redraw payload
- JSONL append creates one valid line
- logging is disabled by default
- logging failure does not fail redraw
- MCP response includes `case_id` and `case_log_path` only when enabled
- quality failures and route advisory fields round-trip into the case record
- taxonomy rejects unsupported failure types in benchmark manifests

## Success Criteria

A successful implementation lets a caller run one redraw and, when logging is enabled, receive a valid JSONL case containing the source layer, redrawn output, pasteback preview, route geometry, quality gate state, provider/model metadata, and empty review labels. Existing redraw, decomposition, and provider behavior remain unchanged by default.
