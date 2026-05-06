# SAM Local Signal Runner v1

Status: implemented

## Goal

Add an explicit local SAM signal runner behind the open-model signal adapter. The runner produces reviewable mask proposal signals for redraw and decompose cases: mask count, coverage candidates, total coverage, and lightweight boundary complexity.

## Runtime Boundary

- Default adapter behavior remains dry-run.
- Local SAM execution requires `--enable-local-runner segment_anything_sam_vit`.
- The real backend never downloads weights.
- Real SAM execution requires `--sam-checkpoint`.
- Outputs remain `assistant_labeled` plus `needs_human_review`.
- Outputs are not added to `combined_case_source_manifest_v1`.
- Private or missing source refs are skipped without leaking original refs.

## CLI Pilot

Dry-run smoke:

```bash
PYTHONPATH=src python scripts/open_model_signal_adapter.py \
  --model segment_anything_sam_vit \
  --max-examples 3
```

Explicit local SAM pilot:

```bash
PYTHONPATH=src python scripts/open_model_signal_adapter.py \
  --model segment_anything_sam_vit \
  --enable-local-runner segment_anything_sam_vit \
  --sam-checkpoint /path/to/sam_vit_b.pth \
  --sam-model-type vit_b \
  --sam-points-per-side 16 \
  --max-examples 3
```

## Non-Goals

- Do not convert masks into accepted labels.
- Do not train a model from SAM outputs.
- Do not add SAM outputs to the combined training manifest.
- Do not call cloud providers.
- Do not auto-download checkpoints.

## Verification

- `tests/test_sam_signal_runner.py` covers mask normalization, private source skips, adapter enablement, and CLI flags.
