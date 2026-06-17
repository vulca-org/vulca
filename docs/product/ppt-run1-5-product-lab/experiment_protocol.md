# Experiment Protocol

Status: not-run.

Run 1.5 compares three blocking arms: prompt-only, full Vulca, and bad-data. The goal is to test whether evidence-backed design memory changes generated PPT structure, whether the output reads as a product lab rather than a generic explanatory deck, and whether corrupted but structurally valid rules expose QA gates.

## Arms

- prompt_only: generate from a baseline prompt only. This arm must not receive design memory, tutorial notes, Vulca generation brief, or Vulca PPT skill material.
- full_vulca: generate from the complete product-lab case pack, including sources, tutorial notes, design memory, deck outline, slide patterns, and the full Vulca generation brief.
- bad_data: generate from structurally valid corrupted rules as a negative control. This arm must not use invalid JSON, malformed PPTX packaging, or missing required files.

## Deferred Arms

The source-only and tutorial-only arms are deferred until the three blocking arms produce analyzable outputs.

## Gate

Public publishing remains blocked until comparison, ablation, render, provenance, and human review records exist.
