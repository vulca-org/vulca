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
    "13-website-ppt-claim-spine.md",
    "14-release-readiness-evidence-gate.md",
]

REQUEST_TEMPLATE_CHECKS = [
    "This request does not mark blocked work as public-ready.",
    "This request does not turn AI-assisted synthesis into human evidence.",
    "This request cites source evidence.",
    "This request preserves `docs/review-context/LOCK.md`.",
]

RELEASE_READINESS_TEMPLATE_CHECKS = [
    "Public release remains blocked until every required gate below is passed and a human release owner records approval.",
    "Evidence Index",
    "Gate 1: Workspace Persistence",
    "Gate 2: Artifact Ingestion",
    "Gate 3: EvidencePack Rendering",
    "Gate 4: Human Release Workflow",
    "Gate 5: Public Example Quality",
    "Gate 6: Website/PPT Claim Review",
    "Human release owner",
    "Release Decision",
    "blocked / internal_only / preview_gated / internal_pilot / public_example / product_release",
]

BRIDGE_FIXTURE_ACCEPTANCE = {
    "asset_becomes_bridge_record": True,
    "bridge_projects_to_workspace_objects": True,
    "missing_evidence_visible": True,
}


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
    omit_release_gate_item: bool = False,
    omit_bridge_missing_evidence: bool = False,
) -> None:
    required_files = [
        "README.md",
        "LOCK.md",
        "GOVERNANCE.md",
        "CHANGELOG.md",
        "MANIFEST.json",
        "source-index.md",
        *CORE_HISTORY_FILES,
        "artifact-bridge/README.md",
        "artifact-bridge/m3-demo-bridge-fixture.json",
        "release-readiness/README.md",
        "release-readiness/TEMPLATE.md",
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
    missing_evidence = [] if omit_bridge_missing_evidence else ["durable storage evidence"]
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
        elif rel == "release-readiness/TEMPLATE.md":
            checks = (
                RELEASE_READINESS_TEMPLATE_CHECKS[:-1]
                if omit_release_gate_item
                else RELEASE_READINESS_TEMPLATE_CHECKS
            )
            path.write_text(
                "# Release Readiness Report\n\n"
                "Vault status: test.\n\n"
                + "\n".join(f"- {item}" for item in checks)
                + "\n\n## Sources\n\n- test source\n",
                encoding="utf-8",
            )
        elif rel == "artifact-bridge/m3-demo-bridge-fixture.json":
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "fixture_id": "m3-demo-bridge-fixture-v1",
                        "bridge_records": [
                            {
                                "bridge_record_id": "bridge-generate-key-visual-v1",
                                "source_operation": "generate_image",
                                "workspace_targets": {
                                    "visual_variant_id": "variant-key-visual-v1"
                                },
                                "operation": {"kind": "generate"},
                                "artifacts": {
                                    "primary_asset_path": "artifacts/key-visual.png"
                                },
                                "evidence": {"prompt_refs": ["prompt-ref"]},
                                "claim_state": {
                                    "status": "preview_gated",
                                    "public_ready": False,
                                },
                            }
                        ],
                        "workspace_projection": {
                            "brief": {"id": "brief-cultural-key-visual"},
                            "motif_branch": {"id": "motif-proof-spine"},
                            "visual_variant": {
                                "id": "variant-key-visual-v1",
                                "source_bridge_records": [
                                    "bridge-generate-key-visual-v1"
                                ],
                            },
                            "agent_runs": [
                                {
                                    "id": "agentrun-generate-key-visual-v1",
                                    "source_bridge_record": "bridge-generate-key-visual-v1",
                                }
                            ],
                            "evidence_pack": {
                                "id": "evidencepack-key-visual-v1",
                                "source_bridge_records": [
                                    "bridge-generate-key-visual-v1"
                                ],
                                "missing_evidence": missing_evidence,
                                "blockers": missing_evidence,
                                "visible_to_reviewers": True,
                            },
                            "review_request": {"id": "review-key-visual-v1"},
                            "release_gate": {
                                "id": "releasegate-key-visual-v1",
                                "publicReady": False,
                                "blockers": missing_evidence,
                                "human_owner_required": True,
                            },
                        },
                        "rr2_acceptance": BRIDGE_FIXTURE_ACCEPTANCE,
                    },
                    indent=2,
                ),
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
    module.RELEASE_READINESS_TEMPLATE_PATH = root / "release-readiness" / "TEMPLATE.md"
    module.BRIDGE_FIXTURE_PATH = root / "artifact-bridge" / "m3-demo-bridge-fixture.json"
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


def test_release_readiness_template_must_include_all_gate_controls(tmp_path: Path) -> None:
    module = load_validator()
    write_minimal_vault(tmp_path, omit_release_gate_item=True)

    with pytest.raises(SystemExit):
        run_validator_on(module, tmp_path)


def test_bridge_fixture_must_keep_missing_evidence_visible(tmp_path: Path) -> None:
    module = load_validator()
    write_minimal_vault(tmp_path, omit_bridge_missing_evidence=True)

    with pytest.raises(SystemExit):
        run_validator_on(module, tmp_path)
