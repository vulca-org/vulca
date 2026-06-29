# Task 1 Report: Schema And Case-Folder Validation

## What changed

Added the `vulca.vector_aesthetics` package with a schema validator for case folders and a review-dict serializer.

Implemented:
- `validate_case_folder(case_dir: Path) -> CaseRecord`
- `coverage_for_case(record: CaseRecord) -> dict[str, str]`
- `case_to_review_dict(record: CaseRecord) -> dict[str, object]`

Validation now covers:
- required metadata fields
- allowed source/currentness/review/module/capture values
- HTTPS canonical URL enforcement
- quality score range checks and total scoring
- local capture file existence checks
- capture failure handling that keeps coverage partial instead of complete
- broad secret redaction in review output

## Files changed

- `src/vulca/vector_aesthetics/__init__.py`
- `src/vulca/vector_aesthetics/schema.py`
- `tests/test_vector_aesthetics_schema.py`

## TDD evidence

### RED

Ran:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_schema.py -q
```

Observed failure before implementation:

```text
ModuleNotFoundError: No module named 'vulca.vector_aesthetics'
```

### GREEN

Ran the same focused test after implementation:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_schema.py -q
```

Result:

```text
8 passed
```

## Tests run

- `PYTHONPATH=src pytest tests/test_vector_aesthetics_schema.py -q`

## Self-review

The implementation stays within the task scope and only touches the requested package plus the focused schema test file.

I corrected the capture coverage logic so any `capture_failed` entry keeps the evidence bucket partial, which matches the stricter failure semantics in the brief.

## Concerns

Pytest still reports pre-existing warnings unrelated to this task, including:
- `PytestConfigWarning: Unknown config option: asyncio_mode`
- deprecation warnings from imported native types

Those warnings did not affect the focused schema gate.

## Fix

Implemented the review fixes for capture coverage and asset-manifest evidence:
- screenshot and video coverage now require explicit evidence and no longer pass through as `missing`
- `asset_manifest` coverage now comes from `assets/asset_manifest.json` or an `asset_manifest` evidence record
- validation now rejects case folders that lack screenshot or video coverage after coverage calculation

### Tests run

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_schema.py -q
```

### Result

```text
11 passed, 3 warnings in 4.11s
```

## Fix 2

Updated capture coverage precedence so a successful local capture wins over a capture-failure record for the same evidence type.

This specifically fixes screenshot coverage: `local_capture` now resolves to `complete` even when a `capture_failed` screenshot record also exists.

### Tests run

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_schema.py -q
```

### Result

```text
12 passed, 3 warnings in 2.79s
```
