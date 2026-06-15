# Capability Map

Vault status: product capability map.

## User-Facing Capability Clusters

### Discover

Purpose: turn fuzzy visual intent into direction evidence.

Current assets:

- `/visual-discovery`
- taste profile
- cultural tendency analysis
- direction cards
- sketch prompt records

Boundary: real provider sketches require explicit opt-in; mock/dry records do
not prove visual quality.

### Direct

Purpose: convert chosen direction into structured artifacts.

Current assets:

- `/visual-brainstorm` -> `proposal.md`
- `/visual-spec` -> `design.md`
- `/visual-plan` -> `plan.md`
- `compose_prompt_from_design`
- tradition guides and L1-L5 acceptance rubrics

Boundary: design artifacts can define intent and gates; they do not guarantee
provider output quality.

### Generate

Purpose: route to image providers and generate candidates or layer assets.

Current assets:

- `generate_image`
- `create_artwork`
- provider registry
- optional `vulca[providers]`
- mock, OpenAI, Gemini/NB2, ComfyUI
- seed / steps / cfg / negative prompt metadata

Boundary: provider capability gates must stay in code. Public docs should avoid
claiming fixed model behavior.

### Decompose

Purpose: split an existing image into semantic RGBA layers.

Current assets:

- `/decompose`
- `layers_split`
- `layers_list`
- orchestrated DINO/SAM paths
- semantic paths
- residual layer
- manifest quality flags

Boundary: decompose preserves source pixels under masks. It is not the same as
generating a new clean layer stack.

### Edit / Redraw

Purpose: modify target regions or layers while preserving non-target pixels.

Current assets:

- `inpaint_artwork`
- `layers_redraw`
- `layers_edit`
- `layers_transform`
- `layers_paste_back`
- `layers_composite`
- mask-aware routing
- target-aware mask refinement
- quality advisory fields

Boundary: redraw is advanced. Public-facing claims must distinguish tested local
contracts from real-provider visual quality.

### Evaluate

Purpose: judge cultural and visual fit.

Current assets:

- `/evaluate`
- `evaluate_artwork`
- `layers_evaluate`
- 13 traditions
- L1-L5 framework
- rubric-only mode

Boundary: automated evaluation supports review. It does not replace human
creative, cultural, legal, or release judgment.

### Archive / Learn

Purpose: preserve artifacts and create future training/evaluation substrate.

Current assets:

- `archive_session`
- `redraw_case`
- `decompose_case`
- `layer_generate_case`
- benchmark manifests
- review labels

Boundary: case records are evidence substrate, not automatically human labels.

## Product Surface Mapping

| SDK / MCP capability | Workspace product object |
| --- | --- |
| visual discovery / brainstorm / spec / plan | `Brief`, `MotifBranch` |
| generate / layer generate | `VisualVariant`, `AgentRun` |
| decompose / layers | `VisualVariant`, `EvidencePack` |
| redraw / inpaint / pasteback | `VisualVariant`, `ReviewRequest`, `AgentRun` |
| evaluate / L1-L5 | `EvidencePack`, `ReleaseGate` |
| case logging | `AgentRun`, future training/evidence records |

## Sources

- `README.md`
- `docs/tools-readiness-matrix.md`
- `docs/product/provider-capabilities.md`
- `src/vulca/mcp_server.py`
- `src/vulca/layers/`
- `src/vulca/providers/`
- `tests/test_prompting.py`
- `tests/test_layers_redraw.py`
- `tests/test_visual_discovery_docs_truth.py`
