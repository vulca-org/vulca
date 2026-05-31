# PPT Run 1.5 Product Lab

Status: not-run.

This case pack defines a three-arm product-lab experiment for testing whether structured design evidence becomes design memory, changes code-generated PPT output, and exposes QA and public publishing gates.

## Arms

- prompt_only: baseline prompt-only deck generation with design memory and Vulca-specific inputs forbidden.
- full_vulca: full Vulca workflow using source analysis, tutorial notes, design memory, and the generation brief.
- bad_data: negative control using corrupted but structurally valid rules to test whether the workflow detects degraded design memory.

## Public Publishing

Public publishing blocked until generated outputs exist, render checks pass, asset provenance is complete, and human review approves release.

## Artifact Map

- `sources.json`: reference-analysis-only registry.
- `experiment_protocol.md` and `experiment_protocol.md.json`: arm definitions and blocking inputs.
- `design_memory.json`: strict Run 1.5 memory contract.
- `deck_outline.json` and `slide_patterns.json`: product-lab deck structure.
- `results/`: not-run result placeholders and delivery gate.
