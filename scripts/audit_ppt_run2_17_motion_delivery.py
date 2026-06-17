from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.validate_pptx_delivery import validate_delivery


DEFAULT_THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK_REL = Path("docs") / "product" / "ppt-run2-data-skill-quality"

RUN2_16_ARMS = [
    ("prompt_only", "ppt-run2-16-prompt-only", "Prompt only"),
    ("run1_5_skill", "ppt-run2-16-run1-5-skill", "Run 1.5 skill baseline"),
    ("run2_16_full_skill", "ppt-run2-16-full-vulca", "Run 2.16 full selector skill"),
    ("bad_selector_memory", "ppt-run2-16-bad-selector-memory", "Bad selector memory"),
]


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def audit_arm(repo_root: Path, presentations_dir: Path, arm_id: str, slug: str, label: str) -> dict[str, Any]:
    arm_dir = presentations_dir / slug
    pptx = arm_dir / "output" / f"{slug}.pptx"
    layout_dir = arm_dir / "layout" / "final"
    contact_sheet = arm_dir / "preview" / "contact-sheet.png"
    result = validate_delivery(
        pptx_path=pptx,
        layout_dir=layout_dir,
        contact_sheet_path=contact_sheet,
        label=label,
    )
    motion = result.checks.get("motion", {})
    return {
        "arm_id": arm_id,
        "label": label,
        "slug": slug,
        "pptx_path": rel(result.pptx_path, repo_root),
        "layout_dir": rel(result.layout_dir, repo_root),
        "contact_sheet_path": rel(result.contact_sheet_path, repo_root),
        "delivery_gate": result.delivery_gate,
        "slide_count": result.checks.get("slide_count", 0),
        "media_entry_count": len(result.checks.get("media_entries", [])),
        "motion": motion,
        "keynote_readout": (
            "motion_xml_present_native_review_required"
            if motion.get("has_motion_xml")
            else "static_editable_slides_only"
        ),
        "issue_codes": [issue.code for issue in result.issues],
    }


def build_audit(repo_root: Path, presentations_dir: Path) -> dict[str, Any]:
    arm_audits = [
        audit_arm(repo_root, presentations_dir, arm_id, slug, label)
        for arm_id, slug, label in RUN2_16_ARMS
    ]
    all_static = all(not arm["motion"].get("has_motion_xml") for arm in arm_audits)
    return {
        "schema_version": 1,
        "status": "motion_delivery_audit_public_blocked",
        "public_ready": False,
        "stage_policy": "repeat_same_five_layers_not_run3",
        "run_id": "2.17",
        "source_generated_run_id": "2.16",
        "delivery_truth": {
            "html_viewer_mode": "static_slide_preview_only",
            "pptx_editability_status": "editable_native_static_shapes",
            "native_ppt_animation_status": (
                "absent_in_current_pptx" if all_static else "motion_xml_present_native_review_required"
            ),
            "keynote_expected_behavior": "editable_static_slides_no_native_animation"
            if all_static
            else "native_review_required_before_animation_claim",
            "motion_xml_scan_scope": "tag_presence_only_not_playback_verification",
            "motion_storyboard_status": "static_sequence_design_contract_not_native_animation",
        },
        "arm_audits": arm_audits,
        "motion_renderer_gap": {
            "next_run_recommendation": "run2_17_motion_renderer_proof",
            "keep_static_ppt_as": "editable_product_output",
            "public_video_path": "separate_html_or_video_motion_renderer_until_pptx_animation_is_verified",
            "minimum_proof_slides": ["cover", "before_after", "climax"],
            "blocking_questions": [
                "Can artifact-tool export PowerPoint animation XML that Keynote preserves?",
                "If not, should public video use a separate HTML/video motion renderer?",
                "Which motion beats must stay editable in PPT versus only appear in the public video render?",
            ],
        },
        "qa_summary": {
            "pptx_motion_xml_scan": "passed: all Run 2.16 PPTX files inspected",
            "html_viewer_truthfulness": "passed: viewer remains static slide/contact-sheet preview",
            "keynote_claim_guard": "passed: current output is not claimed to contain native animation",
            "public_release_gate": "blocked pending renderer proof, native render inspection, human approval, and public-video-grade review",
        },
        "next_required_action": (
            "Build a minimal motion renderer proof for cover, before/after, and climax while keeping the "
            "current Run 2.16 PPT as the editable static product output; do not advance to Run 3.0."
        ),
    }


def write_markdown(audit: dict[str, Any], out_path: Path) -> None:
    lines = [
        "# Run 2.17 Motion Delivery Audit",
        "",
        "Status: motion delivery audit completed, public blocked.",
        "",
        "Run 2.17 does not generate a new four-arm PPT. It audits the Run 2.16 PPTX delivery layer so we do not confuse static storyboard rhythm with real Keynote or PowerPoint animation.",
        "",
        "## Delivery Truth",
        "",
        "- HTML viewer is static slide preview only.",
        "- Current PPTX files are editable native static slides.",
        "- Keynote will open the current decks as static editable slides, with no transition/timing/animation builds.",
        "- The motion XML scan detects tag presence only; it does not prove animation playback.",
        "- The existing motion/storyboard fields are sequence-design contracts, not native animation delivery.",
        "- Do not advance to Run 3.0.",
        "",
        "## Arm Audit",
        "",
        "| Arm | Slides | Media | Motion XML | Keynote readout |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for arm in audit["arm_audits"]:
        motion = arm["motion"]
        motion_label = (
            f"yes, slides {motion.get('slides_with_motion_xml', [])}; native review required"
            if motion.get("has_motion_xml")
            else "no transition/timing/animation"
        )
        lines.append(
            f"| `{arm['arm_id']}` | {arm['slide_count']} | {arm['media_entry_count']} | "
            f"{motion_label} | `{arm['keynote_readout']}` |"
        )
    lines.extend(
        [
            "",
            "## Renderer Gap",
            "",
            "Next run recommendation: `run2_17_motion_renderer_proof`.",
            "",
            "The static PPT remains the editable product output. Public video should use a separate HTML or video motion renderer until PPTX animation export is verified. The minimum proof should cover the cover, before/after, and climax slides.",
            "",
            "## QA Summary",
            "",
        ]
    )
    for key, value in audit["qa_summary"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", f"Next required action: {audit['next_required_action']}", ""])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Run 2.16 PPTX files for real motion/animation delivery.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--thread-id", default=DEFAULT_THREAD_ID)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    presentations_dir = repo_root / "outputs" / args.thread_id / "presentations"
    pack = repo_root / PACK_REL
    audit = build_audit(repo_root, presentations_dir)
    json_path = pack / "results" / "run2_17_motion_delivery_audit.json"
    md_path = pack / "results" / "run2_17_motion_delivery_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    write_markdown(audit, md_path)
    print(f"wrote {rel(json_path, repo_root)}")
    print(f"wrote {rel(md_path, repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
