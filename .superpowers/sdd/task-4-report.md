# Task 4 Report: Static HTML Review Atlas

## What changed

- Added `write_review_html(review_json_path: Path, html_path: Path) -> Path` in `src/vulca/vector_aesthetics/review_html.py`.
- Rendered a static HTML review atlas with the required views and case cards.
- Escaped visible metadata, redacted secret-like strings in both visible HTML and embedded JSON, and resolved local capture links relative to the output HTML directory.
- Added the task-specific tests in `tests/test_vector_aesthetics_review_html.py`.

## Files changed

- `src/vulca/vector_aesthetics/review_html.py`
- `tests/test_vector_aesthetics_review_html.py`

## TDD evidence

### RED

Command:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_review_html.py -q
```

Result before implementation:

```text
FFFF
E       ModuleNotFoundError: No module named 'vulca.vector_aesthetics.review_html'
4 failed
```

### GREEN

Command:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_review_html.py -q
```

Result after implementation:

```text
4 passed
```

## Tests run

- `PYTHONPATH=src pytest tests/test_vector_aesthetics_review_html.py -q`

## Self-review

- The implementation stays narrow and matches the brief exactly.
- HTML escaping is applied to visible fields, and redaction runs before visible rendering and before JSON embedding.
- Capture links are resolved from `case_rel` plus the capture path, then normalized to a relative href from the output HTML directory.

## Concerns

- The renderer currently assumes the review JSON already follows the Task 3 schema shape used by the tests.
- Pytest still emits an existing `asyncio_mode` config warning and a couple of dependency deprecation warnings, but they do not affect the task result.

## Fix

Command:

```bash
PYTHONPATH=src pytest tests/test_vector_aesthetics_review_html.py -q
```

Output:

```text
......                                                                   [100%]
=============================== warnings summary ===============================
../../../../../../opt/homebrew/lib/python3.14/site-packages/_pytest/config/__init__.py:1434
  /opt/homebrew/lib/python3.14/site-packages/_pytest/config/__init__.py:1434: PytestConfigWarning: Unknown config option: asyncio_mode

tests/test_vector_aesthetics_review_html.py::test_write_review_html_renders_required_views
  <frozen importlib._bootstrap>:491: DeprecationWarning: builtin type SwigPyPacked has no __module__ attribute

tests/test_vector_aesthetics_review_html.py::test_write_review_html_renders_required_views
  <frozen importlib._bootstrap>:491: DeprecationWarning: builtin type SwigPyObject has no __module__ attribute

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
6 passed, 3 warnings in 2.76s
```
