# Learning Loop And Case Records

Vault status: protected technical memory.

## Why This Exists

VULCA accumulated many redraw, decompose, layer-generation, and provider
experiments. The Learning Loop work creates a stable evidence substrate so those
experiments are not lost as screenshots, logs, or one-off branches.

The first goal is not model training. The first goal is reliable case records.

## Case Types

### `redraw_case`

Causal direction:

```text
existing layer or artifact + edit instruction -> edited layer + pasteback preview
```

Captures:

- source layer
- instruction
- provider/model
- route requested/chosen
- geometry
- quality gate state
- refinement
- artifacts
- sparse review labels

### `decompose_case`

Causal direction:

```text
existing image -> semantic layer split + manifest + residual
```

Captures:

- source image
- split mode
- target layer hints
- output manifest
- layers
- residual
- detection report
- quality metrics
- review labels

### `layer_generate_case`

Causal direction:

```text
intent + visual plan + prompt stack -> generated layered artifact
```

Captures:

- user intent
- tradition/style constraints
- layer plan
- prompt stack and hashes
- provider request
- decisions
- output layers
- composite and preview
- learning targets
- review labels

## Boundary

These case types must remain separate. Do not overload one schema with another
causal task.

Important distinctions:

- Decompose preserves source pixels under masks.
- Layer generation creates new layer assets from intent/prompt stack.
- Redraw edits an existing layer or artifact.

## Future Use

Case records can support:

- tiny failure classifiers
- route recommendation
- rerun/fallback policy
- benchmark seed sets
- review queues
- Workspace evidence packs

They cannot support public quality claims without human or gate confirmation.

Sources:

- `docs/superpowers/specs/2026-05-05-vulca-learning-loop-v0-design.md`
- `docs/superpowers/specs/2026-05-05-decompose-case-design.md`
- `docs/superpowers/specs/2026-05-05-layer-generate-case-design.md`
- `src/vulca/layers/redraw_cases.py`
- `src/vulca/layers/decompose_cases.py`
- `src/vulca/layers/layer_generate_cases.py`
