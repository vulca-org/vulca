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

DURABLE_REVIEW_ACCEPTANCE = {
    "reload_preserves_review_item": True,
    "reload_preserves_evidence": True,
    "reload_preserves_blockers": True,
    "reload_preserves_decision_state": True,
    "agent_system_cannot_finalize_public_release": True,
    "human_decision_history_auditable": True,
}

PUBLIC_EXAMPLE_ACCEPTANCE = {
    "evidence_pack_exists": True,
    "visual_quality_reviewed": True,
    "release_owner_records_decision": True,
    "public_copy_example_specific": True,
}

WEBSITE_PPT_COPY_ACCEPTANCE = {
    "public_copy_uses_r_level_status": True,
    "proof_lab_remains_bounded": True,
    "translations_preserve_claim_level": True,
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
    omit_durable_decision_history: bool = False,
    omit_public_example_owner: bool = False,
    omit_translation_boundary: bool = False,
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
        "workspace-durable/README.md",
        "workspace-durable/m3-durable-review-fixture.json",
        "public-examples/README.md",
        "public-examples/m3-public-example-gate.json",
        "copy-gates/README.md",
        "copy-gates/website-ppt-copy-gate.json",
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
        elif rel == "workspace-durable/m3-durable-review-fixture.json":
            decision_history = (
                []
                if omit_durable_decision_history
                else [
                    {
                        "actor_role": "human_release_owner",
                        "action": "block_public_release",
                        "summary": "Durable review fixture keeps public release blocked.",
                        "timestamp": "2026-06-15T00:00:00Z",
                    }
                ]
            )
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "fixture_id": "m3-durable-review-fixture-v1",
                        "storage_boundary": {
                            "mode": "bounded_durable_demo_store",
                            "reload_supported": True,
                        },
                        "persisted_objects": {
                            "review_item": {
                                "id": "review-key-visual-v1",
                                "after_reload": True,
                            },
                            "evidence_pack": {
                                "id": "evidencepack-key-visual-v1",
                                "after_reload": True,
                                "source_bridge_records": [
                                    "bridge-generate-key-visual-v1"
                                ],
                            },
                            "release_gate": {
                                "id": "releasegate-key-visual-v1",
                                "after_reload": True,
                                "publicReady": False,
                                "blockers": ["human release decision missing"],
                            },
                        },
                        "decision_state": {
                            "before_reload": "blocked",
                            "after_reload": "blocked",
                        },
                        "permission_checks": {
                            "agent_can_set_public_ready": False,
                            "system_can_set_public_ready": False,
                            "human_release_owner_required": True,
                        },
                        "decision_history": decision_history,
                        "reload_assertions": [
                            {"name": "review item survives reload"},
                            {"name": "evidence pack survives reload"},
                            {"name": "release blockers survive reload"},
                            {"name": "decision state survives reload"},
                        ],
                        "rr3_acceptance": DURABLE_REVIEW_ACCEPTANCE,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        elif rel == "public-examples/m3-public-example-gate.json":
            release_owner = None if omit_public_example_owner else "release-owner-placeholder"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "gate_id": "m3-public-example-gate-v1",
                        "example_id": "public-example-key-visual-v1",
                        "release_level": "R4",
                        "scope": "example_specific",
                        "evidence_pack": {
                            "id": "evidencepack-key-visual-v1",
                            "status": "complete",
                        },
                        "visual_quality_review": {
                            "status": "pass",
                            "reviewer": "visual-reviewer-placeholder",
                        },
                        "evidence_review": {
                            "status": "pass",
                            "source_backed": True,
                        },
                        "release_decision": {
                            "status": "public_example_approved",
                            "release_owner": release_owner,
                            "decision_scope": "public-example-key-visual-v1",
                            "timestamp": "2026-06-15T00:00:00Z",
                        },
                        "public_copy": {
                            "claim_scope": "example_specific",
                            "product_level_claim": False,
                        },
                        "rr4_acceptance": PUBLIC_EXAMPLE_ACCEPTANCE,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        elif rel == "copy-gates/website-ppt-copy-gate.json":
            translation_level = "R5" if omit_translation_boundary else "R4"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "gate_id": "website-ppt-copy-gate-v1",
                        "website": {
                            "claim_level": "R4",
                            "status_language": "example-specific public example",
                            "blocked_claim_scope": "product-level release readiness",
                        },
                        "readme": {
                            "claim_level": "R4",
                            "status_language": "example-specific public example",
                            "blocked_claim_scope": "production Workspace readiness",
                        },
                        "ppt": {
                            "proof_lab_status": "public_blocked_unless_example_cleared",
                            "claim_level": "R2",
                        },
                        "translations": [
                            {
                                "locale": "zh-CN",
                                "source_surface": "website",
                                "claim_level": translation_level,
                                "matches_source_claim_level": not omit_translation_boundary,
                            }
                        ],
                        "forbidden_upgrade_checks": {
                            "copy_upgrades_missing_implementation": False,
                            "ppt_outputs_cleared_without_specific_gate": False,
                            "translation_upgrades_claim_level": False,
                            "example_generalized_to_product_level": False,
                        },
                        "rr5_acceptance": WEBSITE_PPT_COPY_ACCEPTANCE,
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
    module.DURABLE_REVIEW_FIXTURE_PATH = root / "workspace-durable" / "m3-durable-review-fixture.json"
    module.PUBLIC_EXAMPLE_GATE_PATH = root / "public-examples" / "m3-public-example-gate.json"
    module.WEBSITE_PPT_COPY_GATE_PATH = root / "copy-gates" / "website-ppt-copy-gate.json"
    return module.main()


def test_current_review_context_vault_passes() -> None:
    module = load_validator()

    assert module.main() == 0


def test_missing_required_file_fails(tmp_path: Path) -> None:
    module = load_validator()
    write_minimal_vault(tmp_path, missing_required_file="missing.md")

    with pytest.raises(SystemExit):
        run_validator_on(module, tmp_path)


def test_minimal_review_context_vault_fixture_passes(tmp_path: Path) -> None:
    module = load_validator()
    write_minimal_vault(tmp_path)

    assert run_validator_on(module, tmp_path) == 0


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


def test_durable_review_fixture_must_keep_human_decision_history(tmp_path: Path) -> None:
    module = load_validator()
    write_minimal_vault(tmp_path, omit_durable_decision_history=True)

    with pytest.raises(SystemExit):
        run_validator_on(module, tmp_path)


def test_public_example_gate_must_record_release_owner(tmp_path: Path) -> None:
    module = load_validator()
    write_minimal_vault(tmp_path, omit_public_example_owner=True)

    with pytest.raises(SystemExit):
        run_validator_on(module, tmp_path)


def test_website_ppt_copy_gate_must_preserve_translation_claim_level(tmp_path: Path) -> None:
    module = load_validator()
    write_minimal_vault(tmp_path, omit_translation_boundary=True)

    with pytest.raises(SystemExit):
        run_validator_on(module, tmp_path)
