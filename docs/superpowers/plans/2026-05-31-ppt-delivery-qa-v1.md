# PPT Delivery QA V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a narrow structural PPTX delivery QA primitive that tells us whether a generated deck is ready for internal demo review or blocked before public publishing.

**Architecture:** Add a Python stdlib validator that inspects a generated PPTX package, artifact-tool layout JSON directory, contact-sheet PNG, media dependencies, and local renderer availability. Renderer availability is only a heuristic; v1 does not prove native PowerPoint, Keynote, or Google Slides visual fidelity. Keep generated PPTX/contact-sheet/layout artifacts under `outputs/`; commit only tests, the validator, product docs, and Markdown reports that reference local evidence.

**Tech Stack:** Python stdlib (`argparse`, `zipfile`, `json`, `struct`, `shutil`, `xml.etree.ElementTree`), pytest, ruff, existing Run 1 output artifacts.

---

## File Map

- Create `scripts/validate_pptx_delivery.py`: CLI and importable validator for PPTX delivery checks.
- Create `tests/test_pptx_delivery_validator.py`: TDD coverage for package inspection, missing assets, media warnings, renderer gate, and report writing.
- Create `docs/product/ppt-delivery-qa-v1/README.md`: product primitive definition and scope.
- Create `docs/product/ppt-delivery-qa-v1/delivery_report.md`: Run 1 baseline and Vulca delivery QA report.
- Modify `docs/product/roadmap.md`: link the new delivery QA primitive to the PPT roadmap item if needed.

---

### Task 1: Add PPTX Delivery Validator

**Files:**
- Create: `tests/test_pptx_delivery_validator.py`
- Create: `scripts/validate_pptx_delivery.py`

- [ ] **Step 1: Write failing tests**

Create tests that build a tiny ZIP-based PPTX fixture, a minimal layout JSON directory, and a PNG header-only contact sheet. Cover:

- valid package plus layout plus contact sheet returns ok;
- missing contact sheet returns an error;
- embedded `ppt/media/*` entries create a warning and keep internal demo allowed;
- malformed PPTX ZIP input returns a clear error;
- missing layout JSON returns a clear error;
- renderer detection can be overridden in tests without relying on host OS tools;
- CLI writes a Markdown report containing `Delivery gate`.

- [ ] **Step 2: Run tests to verify RED**

```bash
python3 -m pytest tests/test_pptx_delivery_validator.py -q
```

Expected: fail because `scripts.validate_pptx_delivery` does not exist.

- [ ] **Step 3: Implement validator**

Create `scripts/validate_pptx_delivery.py` with:

- `DeliveryIssue`;
- `DeliveryResult`;
- `validate_delivery(...)`;
- `write_markdown_report(...)`;
- `main(...)`.

The CLI must accept:

```bash
python3 scripts/validate_pptx_delivery.py \
  --pptx <deck.pptx> \
  --layout-dir <layout/final> \
  --contact-sheet <contact-sheet.png> \
  --label <human-readable label> \
  --out <delivery_report.md>
```

- [ ] **Step 4: Run tests to verify GREEN**

```bash
python3 -m pytest tests/test_pptx_delivery_validator.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
ruff check scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py
ruff format --check scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py
git add scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py docs/superpowers/plans/2026-05-31-ppt-delivery-qa-v1.md
git commit -m "feat: add PPTX delivery QA validator"
```

---

### Task 2: Run Delivery QA on Run 1 Decks

**Files:**
- Create: `docs/product/ppt-delivery-qa-v1/README.md`
- Create: `docs/product/ppt-delivery-qa-v1/delivery_report.md`
- Modify: `docs/product/roadmap.md`

- [ ] **Step 1: Create product doc**

Create `docs/product/ppt-delivery-qa-v1/README.md` describing the primitive:

- input artifacts;
- checks;
- gate statuses;
- what it does not prove yet;
- why human review remains required.

- [ ] **Step 2: Run validator for baseline and Vulca**

Run the validator twice and combine the reports into `delivery_report.md`, once for:

- baseline deck under `outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline`;
- Vulca deck under `outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca`.

- [ ] **Step 3: Update roadmap**

Ensure `docs/product/roadmap.md` names PPT renderer/cross-platform QA as the next PPT primitive.

- [ ] **Step 4: Verify docs and tests**

```bash
python3 -m pytest tests/test_pptx_delivery_validator.py tests/test_ppt_run1_case_pack.py -q
python3 scripts/validate_pptx_delivery.py --help
ruff check scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py
ruff format --check scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py
```

- [ ] **Step 5: Commit**

```bash
git add docs/product/ppt-delivery-qa-v1 docs/product/roadmap.md
git commit -m "docs: record PPT delivery QA v1"
```

---

## Final Verification

```bash
python3 -m pytest tests/test_pptx_delivery_validator.py tests/test_ppt_case_pack_validator.py tests/test_ppt_run1_case_pack.py -q
python3 scripts/validate_pptx_delivery.py --help
ruff check scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py
ruff format --check scripts/validate_pptx_delivery.py tests/test_pptx_delivery_validator.py
git status --short
```

Expected: tests and lint pass; only `outputs/` remains untracked.

## Self-Review

- Spec coverage: The plan implements the selected Run 1 next primitive, renderer/cross-platform QA, without changing generation.
- Placeholder scan: No `TBD`, `TODO`, or unspecified implementation steps remain.
- Type consistency: The validator API and CLI names are consistent across tests, docs, and commands.
