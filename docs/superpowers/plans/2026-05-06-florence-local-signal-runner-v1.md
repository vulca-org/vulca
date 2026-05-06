# Florence Local Signal Runner v1

Status: implemented

## Goal

Add the first explicit local model runner behind the open-model signal adapter. The runner targets Florence-2 caption/OCR signals and keeps outputs as reviewable weak signals, not training labels.

## Runtime Boundary

- Default adapter behavior remains dry-run.
- Local Florence execution requires `--enable-local-runner florence_2`.
- Weight download is disabled unless `--allow-weight-download` is passed.
- Outputs remain `assistant_labeled` plus `needs_human_review`.
- Outputs are not added to `combined_case_source_manifest_v1`.
- Private source refs and missing images are skipped without leaking the original path.

## CLI Pilot

Cached-weights-only pilot:

```bash
PYTHONPATH=src python scripts/open_model_signal_adapter.py \
  --model florence_2 \
  --enable-local-runner florence_2 \
  --max-examples 3 \
  --output build/open_model_signal_adapter/florence_local_signals.jsonl \
  --report build/open_model_signal_adapter/florence_local_signal_report.json
```

Explicit download pilot:

```bash
PYTHONPATH=src python scripts/open_model_signal_adapter.py \
  --model florence_2 \
  --enable-local-runner florence_2 \
  --allow-weight-download \
  --max-examples 3
```

## Non-Goals

- Do not add SAM local execution in this branch.
- Do not train a model from Florence outputs.
- Do not treat captions or OCR as accepted labels.
- Do not call cloud providers.

## Verification

- `tests/test_florence_signal_runner.py` covers local runner normalization, private source skips, adapter enablement, and CLI flags.
