#!/usr/bin/env python3
"""Validate the protected VULCA review-context vault."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "MANIFEST.json"
RELEASE_READINESS_TEMPLATE_PATH = ROOT / "release-readiness" / "TEMPLATE.md"
BRIDGE_FIXTURE_PATH = ROOT / "artifact-bridge" / "m3-demo-bridge-fixture.json"
DURABLE_REVIEW_FIXTURE_PATH = ROOT / "workspace-durable" / "m3-durable-review-fixture.json"
PUBLIC_EXAMPLE_GATE_PATH = ROOT / "public-examples" / "m3-public-example-gate.json"
WEBSITE_PPT_COPY_GATE_PATH = ROOT / "copy-gates" / "website-ppt-copy-gate.json"


FORBIDDEN_OUTSIDE_ALLOWLIST = [
    "public_ready=true",
    "guarantees cultural correctness",
    "guarantees commercial safety",
    "has solved presentation design",
    "fully autonomous approval",
    "replaces Figma",
    "replaces Canva",
    "replaces Adobe",
]

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

RELEASE_READINESS_TEMPLATE_REQUIRED_ITEMS = [
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

BRIDGE_FIXTURE_REQUIRED_WORKSPACE_OBJECTS = [
    "brief",
    "motif_branch",
    "visual_variant",
    "agent_runs",
    "evidence_pack",
    "review_request",
    "release_gate",
]

BRIDGE_FIXTURE_REQUIRED_ACCEPTANCE = [
    "asset_becomes_bridge_record",
    "bridge_projects_to_workspace_objects",
    "missing_evidence_visible",
]

DURABLE_REVIEW_REQUIRED_OBJECTS = [
    "review_item",
    "evidence_pack",
    "release_gate",
]

DURABLE_REVIEW_REQUIRED_ACCEPTANCE = [
    "reload_preserves_review_item",
    "reload_preserves_evidence",
    "reload_preserves_blockers",
    "reload_preserves_decision_state",
    "agent_system_cannot_finalize_public_release",
    "human_decision_history_auditable",
]

PUBLIC_EXAMPLE_REQUIRED_ACCEPTANCE = [
    "evidence_pack_exists",
    "visual_quality_reviewed",
    "release_owner_records_decision",
    "public_copy_example_specific",
]

WEBSITE_PPT_COPY_REQUIRED_ACCEPTANCE = [
    "public_copy_uses_r_level_status",
    "proof_lab_remains_bounded",
    "translations_preserve_claim_level",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        fail(f"missing manifest: {MANIFEST_PATH}")
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid MANIFEST.json: {exc}")


def check_required_files(manifest: dict) -> None:
    missing = []
    for rel in manifest.get("required_files", []):
        if not (ROOT / rel).exists():
            missing.append(rel)
    if missing:
        fail("missing required files: " + ", ".join(missing))


def check_vault_status_headers() -> None:
    for path in ROOT.rglob("*.md"):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if rel.startswith("requests/") and rel != "requests/README.md":
            continue
        if "Vault status:" not in text:
            fail(f"{rel} is missing 'Vault status:' metadata")


def check_sources() -> None:
    for rel in CORE_HISTORY_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "Sources:" not in text and "Source:" not in text and "## Sources" not in text and "## Source" not in text:
            fail(f"{rel} is missing a Sources/Source section")


def check_forbidden_claims(manifest: dict) -> None:
    allowlist = set(manifest.get("claim_boundary_allowlist", []))
    for path in ROOT.rglob("*.md"):
        rel = path.relative_to(ROOT).as_posix()
        if rel in allowlist:
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in FORBIDDEN_OUTSIDE_ALLOWLIST:
            if phrase.lower() in lowered:
                fail(f"forbidden phrase '{phrase}' appears in {rel}")


def check_request_template() -> None:
    template = (ROOT / "requests" / "TEMPLATE.md").read_text(encoding="utf-8")
    required = [
        "This request does not mark blocked work as public-ready.",
        "This request does not turn AI-assisted synthesis into human evidence.",
        "This request cites source evidence.",
        "This request preserves `docs/review-context/LOCK.md`.",
    ]
    for item in required:
        if item not in template:
            fail(f"request template missing checklist item: {item}")


def check_release_readiness_template() -> None:
    if not RELEASE_READINESS_TEMPLATE_PATH.exists():
        fail(f"missing release readiness template: {RELEASE_READINESS_TEMPLATE_PATH}")
    template = RELEASE_READINESS_TEMPLATE_PATH.read_text(encoding="utf-8")
    for item in RELEASE_READINESS_TEMPLATE_REQUIRED_ITEMS:
        if item not in template:
            fail(f"release readiness template missing item: {item}")


def load_json_file(path: Path, label: str) -> dict:
    if not path.exists():
        fail(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid {label}: {exc}")
    if not isinstance(value, dict):
        fail(f"{label} must be a JSON object")
    return value


def check_bridge_fixture() -> None:
    fixture = load_json_file(BRIDGE_FIXTURE_PATH, "bridge fixture")
    if fixture.get("schema_version") != 1:
        fail("bridge fixture schema_version must be 1")
    if not fixture.get("fixture_id"):
        fail("bridge fixture missing fixture_id")

    records = fixture.get("bridge_records")
    if not isinstance(records, list) or not records:
        fail("bridge fixture must include bridge_records")

    record_ids = set()
    asset_record_ids = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            fail(f"bridge fixture record {index} must be an object")
        record_id = record.get("bridge_record_id")
        if not record_id:
            fail(f"bridge fixture record {index} missing bridge_record_id")
        record_ids.add(record_id)
        if not record.get("source_operation"):
            fail(f"bridge fixture record {record_id} missing source_operation")
        if not isinstance(record.get("workspace_targets"), dict):
            fail(f"bridge fixture record {record_id} missing workspace_targets")
        operation = record.get("operation")
        if not isinstance(operation, dict) or not operation.get("kind"):
            fail(f"bridge fixture record {record_id} missing operation.kind")
        artifacts = record.get("artifacts")
        if not isinstance(artifacts, dict):
            fail(f"bridge fixture record {record_id} missing artifacts")
        claim_state = record.get("claim_state")
        if not isinstance(claim_state, dict) or claim_state.get("public_ready") is not False:
            fail(f"bridge fixture record {record_id} must keep public_ready false")

        if record.get("source_operation") in {"generate_image", "manual_upload_intake"}:
            if artifacts.get("primary_asset_path"):
                asset_record_ids.add(record_id)

    if not asset_record_ids:
        fail("bridge fixture must include generated or imported asset bridge record")

    projection = fixture.get("workspace_projection")
    if not isinstance(projection, dict):
        fail("bridge fixture missing workspace_projection")
    for key in BRIDGE_FIXTURE_REQUIRED_WORKSPACE_OBJECTS:
        if key not in projection:
            fail(f"bridge fixture missing workspace projection object: {key}")

    visual_variant = projection.get("visual_variant")
    if not isinstance(visual_variant, dict):
        fail("bridge fixture visual_variant must be an object")
    variant_sources = set(visual_variant.get("source_bridge_records") or [])
    if not asset_record_ids.intersection(variant_sources):
        fail("bridge fixture visual_variant must reference asset bridge record")

    agent_runs = projection.get("agent_runs")
    if not isinstance(agent_runs, list) or not agent_runs:
        fail("bridge fixture agent_runs must be a non-empty list")
    for index, run in enumerate(agent_runs):
        if not isinstance(run, dict):
            fail(f"bridge fixture agent_runs[{index}] must be an object")
        source_record = run.get("source_bridge_record")
        if source_record not in record_ids:
            fail(f"bridge fixture agent_runs[{index}] must reference a bridge record")

    evidence_pack = projection.get("evidence_pack")
    if not isinstance(evidence_pack, dict):
        fail("bridge fixture evidence_pack must be an object")
    pack_sources = evidence_pack.get("source_bridge_records")
    if not isinstance(pack_sources, list) or not set(pack_sources).issubset(record_ids):
        fail("bridge fixture evidence_pack must reference bridge records")
    missing_evidence = evidence_pack.get("missing_evidence")
    blockers = evidence_pack.get("blockers")
    if not isinstance(missing_evidence, list) or not missing_evidence:
        fail("bridge fixture evidence_pack must keep missing_evidence visible")
    if not isinstance(blockers, list) or not blockers:
        fail("bridge fixture evidence_pack must keep blockers visible")
    if evidence_pack.get("visible_to_reviewers") is not True:
        fail("bridge fixture evidence_pack must be visible_to_reviewers")

    release_gate = projection.get("release_gate")
    if not isinstance(release_gate, dict):
        fail("bridge fixture release_gate must be an object")
    if release_gate.get("publicReady") is not False:
        fail("bridge fixture release_gate must keep publicReady false")
    if not isinstance(release_gate.get("blockers"), list) or not release_gate.get("blockers"):
        fail("bridge fixture release_gate must keep blockers visible")
    if release_gate.get("human_owner_required") is not True:
        fail("bridge fixture release_gate must require human owner")

    acceptance = fixture.get("rr2_acceptance")
    if not isinstance(acceptance, dict):
        fail("bridge fixture missing rr2_acceptance")
    for key in BRIDGE_FIXTURE_REQUIRED_ACCEPTANCE:
        if acceptance.get(key) is not True:
            fail(f"bridge fixture rr2_acceptance.{key} must be true")


def check_durable_review_fixture() -> None:
    fixture = load_json_file(DURABLE_REVIEW_FIXTURE_PATH, "durable review fixture")
    if fixture.get("schema_version") != 1:
        fail("durable review fixture schema_version must be 1")
    if not fixture.get("fixture_id"):
        fail("durable review fixture missing fixture_id")

    storage = fixture.get("storage_boundary")
    if not isinstance(storage, dict):
        fail("durable review fixture missing storage_boundary")
    if storage.get("reload_supported") is not True:
        fail("durable review fixture must set storage_boundary.reload_supported true")

    persisted_objects = fixture.get("persisted_objects")
    if not isinstance(persisted_objects, dict):
        fail("durable review fixture missing persisted_objects")
    for key in DURABLE_REVIEW_REQUIRED_OBJECTS:
        obj = persisted_objects.get(key)
        if not isinstance(obj, dict):
            fail(f"durable review fixture missing persisted object: {key}")
        if obj.get("after_reload") is not True:
            fail(f"durable review fixture {key} must survive reload")

    evidence_pack = persisted_objects["evidence_pack"]
    if not evidence_pack.get("source_bridge_records"):
        fail("durable review fixture evidence_pack must preserve source bridge records")

    release_gate = persisted_objects["release_gate"]
    if release_gate.get("publicReady") is not False:
        fail("durable review fixture release_gate must keep publicReady false")
    blockers = release_gate.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        fail("durable review fixture release_gate must preserve blockers")

    decision_state = fixture.get("decision_state")
    if not isinstance(decision_state, dict):
        fail("durable review fixture missing decision_state")
    if not decision_state.get("before_reload") or not decision_state.get("after_reload"):
        fail("durable review fixture must record decision state before and after reload")
    if decision_state.get("before_reload") != decision_state.get("after_reload"):
        fail("durable review fixture decision state must survive reload unchanged")

    permissions = fixture.get("permission_checks")
    if not isinstance(permissions, dict):
        fail("durable review fixture missing permission_checks")
    if permissions.get("agent_can_set_public_ready") is not False:
        fail("durable review fixture must block agent public release finalization")
    if permissions.get("system_can_set_public_ready") is not False:
        fail("durable review fixture must block system public release finalization")
    if permissions.get("human_release_owner_required") is not True:
        fail("durable review fixture must require a human release owner")

    decision_history = fixture.get("decision_history")
    if not isinstance(decision_history, list) or not decision_history:
        fail("durable review fixture must include auditable human decision history")
    for index, event in enumerate(decision_history):
        if not isinstance(event, dict):
            fail(f"durable review decision_history[{index}] must be an object")
        if event.get("actor_role") != "human_release_owner":
            fail(f"durable review decision_history[{index}] must record human release owner")
        if not event.get("action") or not event.get("timestamp"):
            fail(f"durable review decision_history[{index}] missing action or timestamp")

    assertions = fixture.get("reload_assertions")
    if not isinstance(assertions, list) or len(assertions) < 4:
        fail("durable review fixture must include reload assertions")

    acceptance = fixture.get("rr3_acceptance")
    if not isinstance(acceptance, dict):
        fail("durable review fixture missing rr3_acceptance")
    for key in DURABLE_REVIEW_REQUIRED_ACCEPTANCE:
        if acceptance.get(key) is not True:
            fail(f"durable review fixture rr3_acceptance.{key} must be true")


def check_public_example_gate() -> None:
    gate = load_json_file(PUBLIC_EXAMPLE_GATE_PATH, "public example gate")
    if gate.get("schema_version") != 1:
        fail("public example gate schema_version must be 1")
    if not gate.get("gate_id") or not gate.get("example_id"):
        fail("public example gate missing gate_id or example_id")
    if gate.get("release_level") != "R4":
        fail("public example gate release_level must be R4")
    if gate.get("scope") != "example_specific":
        fail("public example gate scope must be example_specific")

    evidence_pack = gate.get("evidence_pack")
    if not isinstance(evidence_pack, dict):
        fail("public example gate missing evidence_pack")
    if evidence_pack.get("status") != "complete":
        fail("public example gate evidence_pack must be complete")
    if not evidence_pack.get("id"):
        fail("public example gate evidence_pack missing id")

    visual_review = gate.get("visual_quality_review")
    if not isinstance(visual_review, dict):
        fail("public example gate missing visual_quality_review")
    if visual_review.get("status") != "pass" or not visual_review.get("reviewer"):
        fail("public example gate visual quality review must pass with reviewer")

    evidence_review = gate.get("evidence_review")
    if not isinstance(evidence_review, dict):
        fail("public example gate missing evidence_review")
    if evidence_review.get("status") != "pass" or evidence_review.get("source_backed") is not True:
        fail("public example gate evidence review must pass and be source-backed")

    release_decision = gate.get("release_decision")
    if not isinstance(release_decision, dict):
        fail("public example gate missing release_decision")
    if release_decision.get("status") != "public_example_approved":
        fail("public example gate release decision must approve public example")
    if not release_decision.get("release_owner"):
        fail("public example gate release decision missing release owner")
    if release_decision.get("decision_scope") != gate.get("example_id"):
        fail("public example gate release decision must be scoped to the example")

    public_copy = gate.get("public_copy")
    if not isinstance(public_copy, dict):
        fail("public example gate missing public_copy")
    if public_copy.get("claim_scope") != "example_specific":
        fail("public example gate public copy must be example-specific")
    if public_copy.get("product_level_claim") is not False:
        fail("public example gate must not approve product-level claims")

    acceptance = gate.get("rr4_acceptance")
    if not isinstance(acceptance, dict):
        fail("public example gate missing rr4_acceptance")
    for key in PUBLIC_EXAMPLE_REQUIRED_ACCEPTANCE:
        if acceptance.get(key) is not True:
            fail(f"public example gate rr4_acceptance.{key} must be true")


def check_website_ppt_copy_gate() -> None:
    gate = load_json_file(WEBSITE_PPT_COPY_GATE_PATH, "website/PPT copy gate")
    if gate.get("schema_version") != 1:
        fail("website/PPT copy gate schema_version must be 1")
    if not gate.get("gate_id"):
        fail("website/PPT copy gate missing gate_id")

    for surface in ["website", "readme"]:
        value = gate.get(surface)
        if not isinstance(value, dict):
            fail(f"website/PPT copy gate missing {surface}")
        if not value.get("claim_level"):
            fail(f"website/PPT copy gate {surface} missing claim_level")
        if not value.get("status_language"):
            fail(f"website/PPT copy gate {surface} missing status_language")
        if value.get("blocked_claim_scope") in {"", None}:
            fail(f"website/PPT copy gate {surface} missing blocked_claim_scope")

    ppt = gate.get("ppt")
    if not isinstance(ppt, dict):
        fail("website/PPT copy gate missing ppt")
    if ppt.get("proof_lab_status") != "public_blocked_unless_example_cleared":
        fail("website/PPT copy gate must preserve PPT proof-lab boundary")
    if not ppt.get("claim_level"):
        fail("website/PPT copy gate ppt missing claim_level")

    translations = gate.get("translations")
    if not isinstance(translations, list) or not translations:
        fail("website/PPT copy gate must include translations")
    surface_levels = {
        "website": gate["website"].get("claim_level"),
        "readme": gate["readme"].get("claim_level"),
        "ppt": ppt.get("claim_level"),
    }
    for index, translation in enumerate(translations):
        if not isinstance(translation, dict):
            fail(f"website/PPT copy gate translations[{index}] must be an object")
        source_surface = translation.get("source_surface")
        if source_surface not in surface_levels:
            fail(f"website/PPT copy gate translations[{index}] has invalid source_surface")
        if translation.get("matches_source_claim_level") is not True:
            fail(f"website/PPT copy gate translations[{index}] must preserve claim level")
        if translation.get("claim_level") != surface_levels[source_surface]:
            fail(f"website/PPT copy gate translations[{index}] claim_level must match source")

    forbidden_upgrades = gate.get("forbidden_upgrade_checks")
    if not isinstance(forbidden_upgrades, dict):
        fail("website/PPT copy gate missing forbidden_upgrade_checks")
    for key, value in forbidden_upgrades.items():
        if value is not False:
            fail(f"website/PPT copy gate forbidden upgrade must remain false: {key}")

    acceptance = gate.get("rr5_acceptance")
    if not isinstance(acceptance, dict):
        fail("website/PPT copy gate missing rr5_acceptance")
    for key in WEBSITE_PPT_COPY_REQUIRED_ACCEPTANCE:
        if acceptance.get(key) is not True:
            fail(f"website/PPT copy gate rr5_acceptance.{key} must be true")


def main() -> int:
    manifest = load_manifest()
    check_required_files(manifest)
    check_vault_status_headers()
    check_sources()
    check_forbidden_claims(manifest)
    check_request_template()
    check_release_readiness_template()
    check_bridge_fixture()
    check_durable_review_fixture()
    check_public_example_gate()
    check_website_ppt_copy_gate()
    print("review-context gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
