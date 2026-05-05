# Layer Generate Case Design

Date: 2026-05-05
Status: approved-for-planning

## Purpose

`layer_generate_case` is the Learning Loop sibling schema for runs that start
from user intent, visual planning artifacts, and prompt stacks, then produce a
new multi-layer Vulca artifact. The record captures enough evidence for future
tiny models and tiny agents to learn failure classification, quality scoring,
generation route recommendation, and next-action policy without changing the
current runtime.

This design extends the Learning Loop v0 direction documented in
`docs/superpowers/specs/2026-05-05-vulca-learning-loop-v0-design.md`.
`src/vulca/layers/redraw_cases.py` is a precedent for versioned case records,
stable case IDs, enumerable review labels, and JSONL append behavior. It is not
the implementation template for this schema.

## Sibling Case Boundary

The three case types are separate causal records:

| Case type | Input | Output | Learning question |
| --- | --- | --- | --- |
| `redraw_case` | Existing layer or artifact plus edit instruction | Edited layer and pasteback preview | Did an edit improve an existing layer? |
| `decompose_case` | Existing image | Extracted semantic layers, masks, residuals, and manifest | Did extraction produce useful editable layers? |
| `layer_generate_case` | Intent, visual plan, layer plan, and prompt stack | Generated layered artifact with manifest, layers, composite, and preview | Did plan-to-layer generation create the intended layered artwork? |

`layer_generate_case` must not reuse `redraw_case` fields named `route`,
`geometry`, or `refinement`, because those fields describe editing an existing
layer. It must not embed decomposition extraction provenance such as detector
choice, segmentation mask confidence, residual extraction status, or source
image splitting decisions. If a generated layer is later edited, that later
operation is a separate `redraw_case`. If a generated composite is later split
from an image, that later operation is a separate `decompose_case`.

## Record Schema

Each record represents one attempt to generate a layered artifact from one
intent and prompt stack. Generated paths remain local path strings. Image bytes
are never embedded in the case record.

```json
{
  "schema_version": 1,
  "case_type": "layer_generate_case",
  "case_id": "layer_generate_20260505T120000Z_...",
  "created_at": "2026-05-05T12:00:00Z",
  "inputs": {
    "user_intent": "Create a layered roadside botanical scene.",
    "tradition": "ipad_cartoon_showcase",
    "style_constraints": {
      "positive": ["clean readable layers", "consistent daylight"],
      "negative": ["flat single-image output", "merged flower and hedge detail"],
      "palette": ["blue sky", "green hedge", "white flowers", "yellow flowers"],
      "composition": ["roadside guardrail above flower bank"],
      "required_motifs": ["sky", "trees", "vehicles", "guardrail", "flower bank"],
      "prohibited_motifs": []
    },
    "layer_plan": {
      "source": "visual_plan",
      "desired_layer_count": 8,
      "layers": [
        {
          "semantic_path": "background.sky",
          "display_name": "Sky",
          "role": "background",
          "z_index": 0,
          "generation_prompt_ref": "prompts/layers/background.sky.txt",
          "alpha_strategy": "opaque_full_canvas",
          "required": true
        }
      ]
    },
    "prompt_stack": {
      "system_prompt_path": "prompts/system.txt",
      "plan_prompt_path": "prompts/plan.txt",
      "layer_prompt_refs": [
        {
          "semantic_path": "background.sky",
          "prompt_path": "prompts/layers/background.sky.txt",
          "prompt_text_hash": "sha256:..."
        }
      ],
      "negative_prompt_path": "prompts/negative.txt",
      "provider_request": {
        "size": "1024x1024",
        "quality": "high",
        "output_format": "png"
      }
    },
    "provider": "openai",
    "model": "gpt-image-2"
  },
  "decisions": {
    "layer_count": {
      "planned": 8,
      "generated": 8,
      "accepted": 7
    },
    "semantic_roles": [
      {
        "semantic_path": "background.sky",
        "role": "background",
        "required": true
      }
    ],
    "z_index": [
      {
        "semantic_path": "background.sky",
        "z_index": 0,
        "reason": "sky is the farthest full-canvas background"
      }
    ],
    "mask_alpha_strategy": {
      "canvas_mode": "full_canvas_rgba_layers",
      "composite_blend_order": "ascending_z_index",
      "per_layer": [
        {
          "semantic_path": "background.sky",
          "alpha_strategy": "opaque_full_canvas",
          "mask_source": "none"
        }
      ]
    },
    "fallback_decisions": [
      {
        "stage": "layer_generation",
        "affected_layers": ["foreground.flowers"],
        "reason": "provider returned merged hedge and flowers",
        "chosen_action": "split_layer"
      }
    ]
  },
  "outputs": {
    "artifact_dir": "runs/layered/roadside_001",
    "layer_manifest_path": "runs/layered/roadside_001/manifest.json",
    "layers": [
      {
        "semantic_path": "background.sky",
        "asset_path": "runs/layered/roadside_001/background.sky.png",
        "mask_path": "",
        "alpha_path": "",
        "visible": true,
        "locked": false,
        "status": "generated"
      }
    ],
    "composite_path": "runs/layered/roadside_001/composite.png",
    "preview_path": "runs/layered/roadside_001/preview.png"
  },
  "learning_targets": {
    "tiny_model": {
      "failure_classification": "",
      "quality_score": null,
      "route_recommendation": ""
    },
    "tiny_agent": {
      "next_action_policy": ""
    }
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

## Field Semantics

- `inputs.user_intent` is the user-facing goal before system decomposition into
  layers.
- `inputs.tradition` records the visual tradition, style family, or workflow
  tradition used by Vulca planning.
- `inputs.style_constraints` records positive and negative constraints that
  affect prompt construction.
- `inputs.layer_plan` records planned semantic layers before provider calls.
  `desired_layer_count` is the intended count, not the generated count.
- `inputs.prompt_stack` records prompt paths and text hashes. The case stores
  hashes and paths so training data can join to prompt text when the artifact
  bundle is available.
- `decisions.layer_count.generated` counts layers written by the generation
  run. `decisions.layer_count.accepted` counts layers accepted by automated or
  human review.
- `decisions.semantic_roles` records layer roles after planning, including
  required status.
- `decisions.z_index` records ordering decisions with concise reasons.
- `decisions.mask_alpha_strategy` records how transparent layers, full-canvas
  layers, blend order, alpha channels, and generated masks were handled.
- `decisions.fallback_decisions` records generation-time fallbacks such as
  `adjust_prompt`, `split_layer`, `merge_layers`, or `fallback_to_agent`.
- `outputs.layer_manifest_path` points to the Vulca manifest for the generated
  layered artifact.
- `outputs.layers[].asset_path` points to the generated layer asset for one
  semantic path.
- `outputs.composite_path` points to the generated full composite.
- `outputs.preview_path` points to the review-sized preview for humans or
  training review tooling.

## Review Labels

The review object is the authoritative human label surface:

- `human_accept`: `true`, `false`, or `null` when unlabeled.
- `failure_type`: empty string when unlabeled, otherwise one value from the
  generation failure taxonomy.
- `preferred_action`: empty string when unlabeled, otherwise one value from the
  generation action taxonomy.
- `reviewer`: stable reviewer identifier or empty string.
- `reviewed_at`: UTC timestamp or empty string.

`learning_targets.tiny_model` and `learning_targets.tiny_agent` are derived
training views over the same review evidence. They are included so dataset
builders can read target labels without inferring task intent from free-form
review fields.

## Failure And Action Taxonomy

Generation-specific `failure_type` values:

- `layer_mismatch`: generated layers do not match the requested layer plan.
- `missing_layer`: a required planned layer is absent.
- `wrong_semantic_role`: a layer exists but represents the wrong role.
- `z_order_error`: the manifest order or composite order is wrong.
- `style_drift`: output violates tradition or style constraints.
- `prompt_conflict`: prompts create contradictory layer instructions.
- `alpha_failure`: transparent/opaque boundaries make the layer unusable.
- `composite_mismatch`: individual layers are acceptable but composite quality
  is poor.
- `provider_failure`: provider failed, returned invalid assets, or returned
  incomplete assets.
- `uncertain`: reviewer cannot assign a more specific label.

Generation-specific `preferred_action` values:

- `accept`
- `rerun_layer`
- `adjust_prompt`
- `merge_layers`
- `split_layer`
- `adjust_alpha_strategy`
- `fallback_to_agent`
- `manual_review`

Redraw-only labels such as `pasteback_mismatch`, `mask_too_broad`, and
`large_white_component` are excluded from `layer_generate_case`. A future schema
revision must define an explicit mapping before any redraw-only label enters
the generation taxonomy.

## Learning Targets

Tiny model targets:

- `failure_classification`: predict the generation failure taxonomy value from
  inputs, decisions, and output summaries.
- `quality_score`: predict a scalar quality score for the generated layered
  artifact using review and acceptance data.
- `route_recommendation`: recommend a generation workflow route, such as direct
  generation, prompt adjustment, per-layer rerun, merge/split repair, alpha
  repair, or fallback to a larger agent.

Tiny agent target:

- `next_action_policy`: choose one action from the generation action taxonomy
  after seeing the case inputs, decisions, outputs, and validator summaries.

The large agent remains the teacher and reviewer for open-ended diagnosis. The
case record supplies compact evidence for narrow learners and small routing
policies.

## Data Rules

- `schema_version` is numeric `1`.
- `case_type` is exactly `layer_generate_case`.
- `case_id` starts with `layer_generate_` and uses a timestamp plus short hash
  over user intent, tradition, layer plan, prompt stack, provider, model, and
  manifest path.
- Paths are local strings. Base64 image data is not stored.
- Empty strings represent missing optional paths or unlabeled enum fields.
- `null` is used only for tri-state labels and numeric labels that are not
  reviewed yet.
- One record describes one generated layered artifact attempt. Repair attempts
  are separate cases or separate `redraw_case` records, depending on causal
  direction.

## Non-Goals

- This design does not implement `layer_generate_case` logging.
- This design does not modify `redraw_case`, `decompose_case`, provider code,
  CLI commands, MCP tools, or runtime generation behavior.
- This design does not add model training, review UI, JSON schema validators,
  benchmark manifests, or new dependencies.

## Success Criteria

The design is complete when an implementer can create a future
`layer_generate_case` builder without deciding the causal boundary, core record
shape, input/output fields, intermediate decision fields, review labels, tiny
model targets, tiny agent targets, or first failure/action taxonomy.
