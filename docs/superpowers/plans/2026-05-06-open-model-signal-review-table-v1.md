# Open-Model Signal Review Table V1

## Goal

Turn completed open-model signal records into a human review worklist before
promotion. The table is an operator surface for deciding promote/reject/hold,
not an automatic training input.

## Scope

- Add `vulca.learning.open_model_signal_review_table`.
- Add `scripts/open_model_signal_review_table.py`.
- Export JSONL, CSV, Markdown, and a JSON report.
- Default to `completed` signals only. Skipped and dry-run signals stay out of
  the review table unless a caller explicitly includes those statuses.
- Include promote/reject/hold commands that call
  `scripts/open_model_signal_review.py review`.

## Safety Policy

- The table does not promote records by itself.
- The table only prepares human review decisions.
- Training still requires the separate promotion manifest from
  `open_model_signal_review.py promote`.
- Output rows only summarize safe signal fields: ids, model metadata, case
  metadata, caption/OCR previews, and mask summary metrics.

## Verification

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.11 -m pytest \
  tests/test_open_model_signal_review_table.py \
  tests/test_open_model_signal_review.py \
  tests/test_open_model_signal_adapter.py -q

/opt/homebrew/bin/python3.11 -m py_compile \
  src/vulca/learning/open_model_signal_review_table.py \
  scripts/open_model_signal_review_table.py

ruff check \
  src/vulca/learning/open_model_signal_review_table.py \
  scripts/open_model_signal_review_table.py \
  tests/test_open_model_signal_review_table.py

git diff --check
```
