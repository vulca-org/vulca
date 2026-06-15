from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "docs" / "review-context" / "gates" / "validate_review_context.py"

CORE_HISTORY_FILES = [
    "00-project-overview.md",
    "01-development-history.md",
    "02-capability-map.md",
    "03-layering-and-decompose.md",
    "04-prompt-control.md",
    "05-layer-redraw-and-mask-gates.md",
    "06-learning-loop-and-case-records.md",
    "07-workspace-product-model.md",
    "08-website-and-ppt-boundaries.md",
    "09-claim-boundaries.md",
    "10-integration-spine.md",
    "11-artifact-bridge-spec.md",
    "12-complete-demo-path.md",
]

REQUEST_TEMPLATE_CHECKS = [
    "This request does not mark blocked work as public-ready.",
    "This request does not turn AI-assisted synthesis into human evidence.",
    "This request cites source evidence.",
    "This request preserves `docs/review-context/LOCK.md`.",
]


def load_validator():
    spec = importlib.util.spec_from_file_location("review_context_validator", VALIDATOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_minimal_vault(
    root: Path,
    *,
    missing_required_file: str | None = None,
    forbidden_claim_file: str | None = None,
    omit_request_lock_item: bool = False,
) -> None:
    required_files = [
        "README.md",
        "LOCK.md",
        "GOVERNANCE.md",
        "CHANGELOG.md",
        "MANIFEST.json",
        "source-index.md",
        *CORE_HISTORY_FILES,
        "requests/README.md",
        "requests/TEMPLATE.md",
        "gates/validate-review-context.md",
        "gates/validate_review_context.py",
    ]
    if missing_required_file is not None:
        required_files.append(missing_required_file)

    manifest = {
        "required_files": required_files,
        "claim_boundary_allowlist": [
            "09-claim-boundaries.md",
            "GOVERNANCE.md",
            "LOCK.md",
            "requests/TEMPLATE.md",
        ],
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")

    standard_text = "# Test\n\nVault status: test.\n\n## Sources\n\n- test source\n"
    for rel in required_files:
        if rel == "MANIFEST.json" or rel == missing_required_file:
            continue
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel == "requests/TEMPLATE.md":
            checks = REQUEST_TEMPLATE_CHECKS[:-1] if omit_request_lock_item else REQUEST_TEMPLATE_CHECKS
            path.write_text(
                "# Request\n\n" + "\n".join(f"- [ ] {item}" for item in checks) + "\n",
                encoding="utf-8",
            )
        elif path.suffix == ".md":
            text = standard_text
            if rel == forbidden_claim_file:
                text += "\npublic_ready=true\n"
            path.write_text(text, encoding="utf-8")
        else:
            path.write_text("# placeholder\n", encoding="utf-8")


def run_validator_on(module, root: Path) -> int:
    module.ROOT = root
    module.MANIFEST_PATH = root / "MANIFEST.json"
    return module.main()


def test_current_review_context_vault_passes() -> None:
    module = load_validator()

    assert module.main() == 0


def test_missing_required_file_fails(tmp_path: Path) -> None:
    module = load_validator()
    write_minimal_vault(tmp_path, missing_required_file="missing.md")

    with pytest.raises(SystemExit):
        run_validator_on(module, tmp_path)


def test_forbidden_claim_outside_allowlist_fails(tmp_path: Path) -> None:
    module = load_validator()
    write_minimal_vault(tmp_path, forbidden_claim_file="00-project-overview.md")

    with pytest.raises(SystemExit):
        run_validator_on(module, tmp_path)


def test_request_template_must_preserve_lock_checklist(tmp_path: Path) -> None:
    module = load_validator()
    write_minimal_vault(tmp_path, omit_request_lock_item=True)

    with pytest.raises(SystemExit):
        run_validator_on(module, tmp_path)
