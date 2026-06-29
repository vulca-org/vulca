# Task 5 Report: Capture Record Tooling

## What Changed

Implemented capture-record tooling for vector aesthetics case folders.

- Added `add_capture(case_dir: Path, capture: dict[str, str]) -> dict[str, object]` to load `metadata.json`, merge or replace a capture by id, validate the case folder, and restore the original metadata file if validation fails.
- Added `record_capture_failure(case_dir: Path, *, evidence_type: str, notes: str, source_url: str) -> dict[str, object]` to record an explicit failed capture entry.
- Added a CLI script, `scripts/vector_aesthetics_record_capture.py`, that records either a normal capture or a failure entry and prints a compact JSON status payload.
- Added tests covering:
  - failure capture recording updates coverage to partial,
  - missing local evidence files are rejected,
  - invalid updates restore `metadata.json` exactly.

## Tests Run

Command:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_captures.py -q
```

Result:

```text
3 passed, 3 warnings in 2.75s
```

Warnings observed were existing environment/config warnings from `pytest` and unrelated deprecation warnings during import.

## TDD Evidence

### RED

Initial run after adding the tests failed as expected because the module did not exist:

```text
ModuleNotFoundError: No module named 'vulca.vector_aesthetics.captures'
```

### GREEN

After implementing the module and CLI, the same test file passed:

```text
3 passed, 3 warnings in 2.75s
```

## Files Changed

- `src/vulca/vector_aesthetics/captures.py`
- `scripts/vector_aesthetics_record_capture.py`
- `tests/test_vector_aesthetics_captures.py`

## Self-Review

The metadata restoration path is explicit and file-local, so a validation failure does not leave a broken `metadata.json` behind. The CLI stays thin and delegates all state mutation to the shared helper.

## Fix

Addressed the review findings by centralizing local capture path resolution in `schema.py` and reusing it from `captures.py`.

- Absolute `path_or_url` values are rejected.
- `../` escapes are rejected if the resolved path leaves `case_dir`.
- Local evidence now requires `is_file()`, so directories do not satisfy validation.
- Added regressions for direct metadata edits plus CLI coverage for `--failure`, missing `--path-or-url`, and default id generation.

Test command:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_captures.py tests/test_vector_aesthetics_schema.py -q
```

Output:

```text
28 passed, 3 warnings in 2.92s
```

## Concerns

No functional blockers. The only residual noise is the pre-existing `pytest` config warning and import-time deprecation warnings in the environment.
