# Open-Model Signal Review Promotion V1

## Goal

Add a human review gate between open-model signal generation and tiny training
data use. Florence/SAM/GroundingDINO-style local or injected runners can produce
weak visual signals, but those records must not become training features unless
a reviewer explicitly promotes them.

## Scope

- Add `vulca.learning.open_model_signal_review` for reviewing one signal record
  and writing a promoted-only signal pack plus a promotion manifest.
- Add `scripts/open_model_signal_review.py` with `review` and `promote`
  subcommands.
- Add an explicit `auxiliary_signal_manifest_path` input to tiny dataset export
  and the tiny training/eval gate.
- Add low-weight sparse features for reviewed auxiliary signals in
  `tiny_action_model_v1`.

## Safety Policy

- Open-model signals remain excluded from default training input.
- Dry-run and skipped signal records cannot be promoted; promotion requires a
  completed local/injected signal.
- Promotion writes a separate JSONL pack and manifest; the manifest declares
  `requires_explicit_dataset_flag: true`.
- Dataset export only attaches auxiliary signals when the promotion manifest is
  passed explicitly.
- Auxiliary signals are features only, not replacement labels. Human review
  labels in source case logs remain the target source of truth.

## Verification

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest \
  tests/test_open_model_signal_review.py \
  tests/test_open_model_signal_adapter.py \
  tests/test_tiny_dataset_export.py \
  tests/test_tiny_action_model.py \
  tests/test_tiny_training_eval_gate.py -q

/opt/homebrew/bin/python3.11 -m py_compile \
  src/vulca/learning/open_model_signal_review.py \
  src/vulca/learning/tiny_dataset.py \
  src/vulca/learning/tiny_action_model.py \
  src/vulca/learning/tiny_training_eval.py \
  scripts/open_model_signal_review.py \
  scripts/tiny_training_eval_gate.py

ruff check \
  src/vulca/learning/open_model_signal_review.py \
  src/vulca/learning/tiny_dataset.py \
  src/vulca/learning/tiny_action_model.py \
  src/vulca/learning/tiny_training_eval.py \
  scripts/open_model_signal_review.py \
  scripts/tiny_training_eval_gate.py \
  tests/test_open_model_signal_review.py
```
