# Decompose Case Learning Schema Design

Date: 2026-05-05
Status: approved-for-implementation

## Purpose

`decompose_case` is the Learning Loop case type for one whole image split job:
an existing source image is decomposed into semantic RGBA layers, a manifest,
residual evidence, and debug artifacts. It captures whether the split is good
enough for editing and what a future tiny model or tiny agent should do next
when it is not.

This case type is a sibling of `redraw_case` and future `layer_generate_case`.
It must not be implemented by overloading `src/vulca/layers/redraw_cases.py`.
The future implementation should live in a separate decompose-focused
module/schema and only read existing split/decompose outputs.

## Boundary

`decompose_case` records `existing image -> semantic layer split`.

It is not a redraw case. It does not carry redraw instructions, edited layer
outputs, source pasteback previews, or per-layer redraw routes. The record is
about the quality of the split job as a whole, with per-layer evidence where
needed.

It is not layered generation. There is no intent-to-new-layer generation step.
`target_layer_hints` guide segmentation of the existing pixels; they are not
prompts to synthesize new layer imagery. Layer assets should preserve source
image pixels under alpha masks, with residual and composite artifacts used as
evidence for coverage and leakage.

## Case Record

Each record is a local-path JSON object. Paths are strings; images and masks
are never embedded as base64.

```json
{
  "schema_version": 1,
  "case_type": "decompose_case",
  "case_id": "decompose_20260505T120000Z_a1b2c3d4e5f6",
  "created_at": "2026-05-05T12:00:00Z",
  "input": {
    "source_image": "assets/showcase/originals/starry-night.jpg",
    "requested": {
      "mode": "orchestrated",
      "provider": "",
      "model": "",
      "tradition": "post_impressionist_painting"
    },
    "target_layer_hints": [
      {
        "name": "sky",
        "label": "swirling blue sky with yellow stars and moon",
        "semantic_path": "background.sky",
        "detector": "sam_bbox",
        "bbox_hint_pct": [0.0, 0.0, 1.0, 0.6],
        "multi_instance": false,
        "threshold": null
      }
    ]
  },
  "output": {
    "output_dir": "assets/showcase/layers_v2/starry-night",
    "manifest_path": "assets/showcase/layers_v2/starry-night/manifest.json",
    "manifest_version": 5,
    "split_mode": "claude_orchestrated",
    "status": "ok",
    "layers": [
      {
        "id": "layer_b4168030",
        "name": "sky",
        "semantic_path": "background.sky",
        "file": "assets/showcase/layers_v2/starry-night/sky.png",
        "z_index": 10,
        "quality_status": "detected",
        "area_pct": 51.55,
        "bbox": [0, 0, 1279, 608],
        "parent_layer_id": null
      }
    ],
    "residual_path": "assets/showcase/layers_v2/starry-night/residual.png",
    "composite_path": "",
    "detection_report": {
      "requested": 5,
      "detected": 5,
      "suspect": 0,
      "missed": 0,
      "success_rate": 1.0
    },
    "debug_artifacts": {
      "qa_contact_sheet_path": "assets/showcase/layers_v2/starry-night/qa_contact_sheet.jpg",
      "qa_prompt_path": "assets/showcase/layers_v2/starry-night/qa_prompt.md",
      "mask_overlay_paths": [],
      "log_path": ""
    }
  },
  "quality": {
    "quality_score": null,
    "layer_coverage": {
      "claimed_pct": 85.45,
      "residual_pct": 14.55,
      "missed_hint_count": 0,
      "suspect_hint_count": 0
    },
    "alpha_quality": {
      "mean_edge_softness": null,
      "hard_edge_ratio": null,
      "empty_layer_count": 0,
      "opaque_noise_ratio": null
    },
    "over_split": {
      "score": null,
      "evidence": []
    },
    "under_split": {
      "score": null,
      "evidence": []
    },
    "semantic_mismatch": {
      "score": null,
      "evidence": []
    },
    "residual_leakage": {
      "score": null,
      "residual_pct": 14.55,
      "evidence": []
    }
  },
  "review": {
    "human_accept": null,
    "failure_type": "",
    "preferred_action": "",
    "reviewer": "",
    "reviewed_at": "",
    "notes": ""
  }
}
```

`case_id` should be stable enough for logs but not globally meaningful. The
recommended form is timestamp plus a short hash over source image, requested
mode/provider/model, tradition, target hints, manifest path, and output dir.

## Inputs

- `source_image`: original flat image used for decomposition. This is required
  and is the causal source of all layer assets.
- `requested.mode`: split/decompose route requested by the caller, such as
  `extract`, `vlm`, `sam3`, or `orchestrated`.
- `requested.provider`: provider requested for modes that need one. Empty
  string is valid for detector/SAM-based paths that do not call an image
  provider.
- `requested.model`: provider or segmentation model identifier when known.
  Empty string means unavailable, not guessed.
- `requested.tradition`: tradition/domain context used to plan or interpret
  the split. This may come from the caller, manifest, or decompose plan.
- `target_layer_hints`: normalized hints that describe what should be split
  from the existing image. For orchestrated plans this maps from plan entities:
  `name`, `label`, `semantic_path`, `detector`, `bbox_hint_pct`,
  `multi_instance`, `threshold`, `order`, and related split thresholds.

## Outputs

- `manifest_path`, `output_dir`, `manifest_version`, `split_mode`, and `status`
  identify the concrete decomposition output.
- `layers` records the produced layer assets and enough manifest metadata for
  later learning: `id`, `name`, `semantic_path`, `file`, `z_index`,
  `quality_status`, `area_pct`, `bbox`, and `parent_layer_id`.
- `residual_path` records the residual layer when present. Residual is an
  honesty artifact for pixels not explained by named hints; it is not a normal
  target layer.
- `composite_path` is optional. It should point to a recomposed output only
  when the pipeline produced one or a caller generated one as quality evidence.
- `detection_report` preserves existing detector/SAM/plan observability:
  requested/detected/suspect/missed counts, per-entity statuses, quality flags,
  scores, bbox fill, inside ratio, and success rate when available.
- `debug_artifacts` preserves review aids such as QA contact sheets, QA prompts,
  mask overlays, sidecar logs, or provider/debug summaries.

## Quality Metrics

Quality metrics should be numeric when deterministic evidence exists and `null`
when the implementation does not yet compute a metric. Do not invent values.

- `layer_coverage`: measures whether target hints and output layers explain the
  source image. Existing signals include `area_pct`, residual percentage,
  `detection_report.detected`, `suspect`, `missed`, and per-entity status.
- `alpha_quality`: measures whether layer alpha is useful for editing. Evidence
  may include empty masks, hard-edge ratios, edge softness, noisy opaque pixels,
  excessive holes, or alpha artifacts from VLM/SAM/keying paths.
- `over_split`: measures redundant or overly fine fragments, such as many
  sibling layers that should be merged, duplicate multi-instance masks, or face
  parts that create no useful editing control.
- `under_split`: measures coarse or missing decomposition, such as a whole
  person captured as one layer when face/hair/clothing are expected, or a large
  residual holding recognizable target concepts.
- `semantic_mismatch`: measures whether a layer captures the wrong concept,
  wrong instance, wrong region, or semantically unrelated source pixels.
- `residual_leakage`: measures source pixels that should belong to named layers
  but remain in residual, plus named layer pixels that leak into residual-like
  catch-all/background regions.

The first bounded `quality_score` should be a 0.0-1.0 reviewer/model target:
`1.0` means editable, semantically correct, and low residual leakage; `0.0`
means unusable split output. It is a learning label, not a hard runtime gate.

## Review Labels

Review labels are sparse at case creation and filled by a human reviewer,
large-agent teacher, or later review queue.

- `human_accept`: `true`, `false`, or `null`.
- `failure_type`: one decompose-specific label or empty string before review.
- `preferred_action`: one decompose-specific next action or empty string before
  review.
- `reviewer`, `reviewed_at`, `notes`: optional provenance and short rationale.

Initial `failure_type` enum:

- `over_split`
- `under_split`
- `semantic_mismatch`
- `alpha_bad`
- `residual_leakage`
- `missed_concept`
- `wrong_instance`
- `empty_layer`
- `duplicate_layer`
- `debug_artifact_missing`
- `route_error`
- `uncertain`

Initial `preferred_action` enum:

- `rerun_split`
- `adjust_hints`
- `merge_layers`
- `split_layer_further`
- `fallback_to_manual`
- `fallback_to_agent`
- `accept`

## Tiny Model Targets

The tiny model should learn narrow judgments from the case record, not perform
open-ended planning.

1. Predict `failure_type` from source/hint/output/quality evidence.
2. Predict a bounded `quality_score` in `[0.0, 1.0]`.
3. Optionally predict binary accept/reject/uncertain from `quality_score`,
   confidence, and failure evidence.

Training features should prioritize compact evidence already available in the
case: requested route, provider/model, tradition, hint count, semantic paths,
detector choices, bbox hints, layer count, residual percentage, detection
statuses, per-layer area percentages, alpha metrics, and review labels.

## Tiny Agent Targets

The tiny agent should learn the next action for split repair:

- `rerun_split`: use when the route is plausible but stochastic/provider/model
  output is weak, debug artifacts exist, and hints do not obviously need edits.
- `adjust_hints`: use when concepts are missed, residual is high, bbox hints
  are loose/wrong, thresholds are poor, or detector choice is wrong.
- `merge_layers`: use when over-split fragments duplicate each other or create
  more layers than useful editing control.
- `split_layer_further`: use when a coarse layer contains multiple editable
  concepts that should be independently addressable.
- `fallback_to_manual`: use when masks need human-grade precision or repeated
  exact-mask failures make automatic recovery inefficient.
- `fallback_to_agent`: use when the plan/hints need semantic reasoning,
  tradition-aware judgment, or visual inspection beyond deterministic routing.

Action rubric:

| Evidence | Preferred action |
|---|---|
| High residual percentage with recognizable missed concepts | `adjust_hints` |
| `detection_report.missed > 0` or many suspect entities | `adjust_hints` |
| Many tiny sibling layers with overlapping/duplicated semantics | `merge_layers` |
| One large subject layer hides expected subparts | `split_layer_further` |
| Repeated route failure with stable hints | `rerun_split` once, then `fallback_to_agent` |
| Alpha edges unusable despite correct semantics | `fallback_to_manual` or `fallback_to_agent` |
| Missing contact sheet/debug evidence for review | `fallback_to_agent` |

## Data Flow

```text
layers_split / decompose workflow
  -> source image + requested mode/provider/tradition + target hints
  -> manifest.json + layer PNGs + residual/composite/debug artifacts
  -> decompose_cases.build_decompose_case(...)
  -> optional JSONL append when logging is explicitly enabled
  -> later review fills human_accept, failure_type, preferred_action
```

The logger should be observational and best-effort, mirroring the Learning Loop
v0 principle used for redraw logging. Missing optional artifacts should be
stored as empty strings or empty arrays. Unknown review labels should use
`uncertain`, not ad hoc free-form taxonomy values.

## Testing For Future Implementation

Future implementation should add tests for:

- minimal schema construction from an orchestrated manifest and plan
- path-only artifact recording with no embedded base64
- residual, manifest, layer assets, detection report, and debug artifacts
  round-tripping into the case
- empty optional `composite_path` and debug artifacts represented explicitly
- rejection of unsupported `failure_type` and `preferred_action`
- proof that `decompose_case` cannot be written through redraw-case builders
- logging disabled by default and enabled only through an explicit decompose
  case log path or decompose-specific environment variable

## Success Criteria

A successful `decompose_case` implementation will let Vulca record one
decomposition run as training/evaluation evidence for split quality without
changing split behavior by default. The record must show what existing image was
split, what hints guided the split, which artifacts were produced, how coverage
and alpha quality look, what the reviewer accepted or rejected, and what the
next repair action should be. It must remain separate from redraw and layered
generation schemas.
