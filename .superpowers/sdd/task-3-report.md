# Task 3 Report: Compile Case Folders To SQLite And Review JSON

## What changed

Implemented `compile_database(root: Path, sqlite_path: Path) -> list[CaseRecord]` and `export_review_json(records: list[CaseRecord], output_path: Path) -> Path` in `src/vulca/vector_aesthetics/compiler.py`.

The compiler:
- walks `root/cases` in deterministic sorted order,
- validates each case with `validate_case_folder`,
- writes SQLite through a temporary sibling file and atomically replaces the target only after successful completion,
- stores `cases`, `module_payloads`, and `captures` rows,
- exports review JSON with `case_to_review_dict`, sorted by case id, with stable key ordering.

I also added focused compiler tests in `tests/test_vector_aesthetics_compiler.py` covering:
- SQLite row counts,
- bounded/sorted review JSON,
- determinism across repeated compiles,
- preservation of the existing SQLite file when validation fails.

## TDD evidence

### RED

Initial focused run before implementation failed as expected with:

```text
ModuleNotFoundError: No module named 'vulca.vector_aesthetics.compiler'
```

Command:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_compiler.py -q
```

Result:
- 4 failed
- failure mode matched the missing compiler module

### GREEN

After implementation, the same test command passed:

```text
4 passed, 3 warnings in 2.94s
```

## Tests run

- `PYTHONPATH=src pytest tests/test_vector_aesthetics_compiler.py -q`

Observed output:
- first run: 4 failed, `ModuleNotFoundError` for missing compiler module
- second run: 4 passed

## Files changed

- `src/vulca/vector_aesthetics/compiler.py`
- `tests/test_vector_aesthetics_compiler.py`

## Self-review

The implementation stays within the task boundary and does not touch generated artifacts. The SQLite write path is atomic at the file-replacement level, and validation happens before any replacement attempt, so a failed recompile leaves the previous database intact.

The review JSON is deterministic because case order is sorted by id and serialization uses sorted keys.

## Concerns

- Pytest emitted unrelated environment warnings about `asyncio_mode` and SWIG types. They did not affect the compiler tests.
- I did not generate or commit SQLite/JSON outputs; the test run only produced temporary artifacts under pytest-managed temp directories.

## Fix

Addressed the review findings by:
- raising `ValueError` when `root/cases` is missing or contains no case folders, so an empty compile cannot overwrite an existing SQLite file,
- storing a per-case `review_json` payload in SQLite and exporting review JSON from the compiled index,
- tightening the module row-count assertion to the current seed total of 40.

Verification:

```text
PYTHONPATH=src pytest tests/test_vector_aesthetics_compiler.py -q
```

Expected result after the fix:

```text
5 passed
```
