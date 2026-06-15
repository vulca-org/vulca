#!/usr/bin/env python3
"""Validate the protected VULCA review-context vault."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "MANIFEST.json"
RELEASE_READINESS_TEMPLATE_PATH = ROOT / "release-readiness" / "TEMPLATE.md"


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


def main() -> int:
    manifest = load_manifest()
    check_required_files(manifest)
    check_vault_status_headers()
    check_sources()
    check_forbidden_claims(manifest)
    check_request_template()
    check_release_readiness_template()
    print("review-context gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
