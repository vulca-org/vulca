from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


SEED_CASES: list[dict[str, Any]] = [
    {
        "id": "makio-meshline",
        "title": "Makio MeshLine",
        "canonical_url": "https://meshline.makio.io/",
        "source_type": "demo",
        "year": 2025,
        "author_or_studio": "Makio64",
        "currentness": "still_current",
        "summary": "Modern Three.js/WebGPU-oriented wide-line reference for route-like vector forms.",
        "why_relevant": "Core learning source for thick 3D vector routes, animated trails, gradients, and dash behavior.",
        "visual_families": ["meshline", "data_tunnel"],
        "module_types": ["meshline", "shader_material", "performance_runtime", "vulca_translation"],
        "canonical_sources": ["https://meshline.makio.io/", "https://github.com/Makio64/makio-meshline"],
    },
    {
        "id": "codrops-threejs-meshline-family",
        "title": "Codrops Three.js MeshLines Demo Family",
        "canonical_url": "https://tympanus.net/codrops/hub/tag/three-js/",
        "source_type": "tutorial",
        "year": 2025,
        "author_or_studio": "Codrops / featured creative technologists",
        "currentness": "2025_plus",
        "summary": "2025+ Three.js demo family containing contemporary line-sculpture and WebGPU/TSL directions.",
        "why_relevant": "Useful as a source for selecting meshline sculpture and vector-space motion cases.",
        "visual_families": ["meshline", "wire_grid", "shader_material"],
        "module_types": ["meshline", "shader_material", "performance_runtime"],
        "canonical_sources": ["https://tympanus.net/codrops/hub/tag/three-js/"],
    },
    {
        "id": "interactive-text-destruction-webgpu-tsl",
        "title": "Interactive Text Destruction with Three.js, WebGPU and TSL",
        "canonical_url": "https://tympanus.net/codrops/2025/07/22/interactive-text-destruction-with-three-js-webgpu-and-tsl/",
        "source_type": "tutorial",
        "year": 2025,
        "author_or_studio": "Codrops",
        "currentness": "2025_plus",
        "summary": "Interactive 3D text destruction and reconstruction using Three.js, WebGPU, and TSL.",
        "why_relevant": "Maps directly to technical evidence labels exploding into fragments and rebuilding into readable state.",
        "visual_families": ["typography_3d", "particle_vector"],
        "module_types": ["typography_3d", "shader_material", "interaction_state", "vulca_translation"],
        "canonical_sources": ["https://tympanus.net/codrops/2025/07/22/interactive-text-destruction-with-three-js-webgpu-and-tsl/"],
    },
    {
        "id": "webgpu-gommage-msdf-dissolve",
        "title": "WebGPU Gommage Effect",
        "canonical_url": "https://tympanus.net/codrops/2026/01/28/webgpu-gommage-effect-dissolving-msdf-text-into-dust-and-petals-with-three-js-tsl/",
        "source_type": "tutorial",
        "year": 2026,
        "author_or_studio": "Codrops",
        "currentness": "2025_plus",
        "summary": "MSDF text dissolve into dust and petals using Three.js TSL and WebGPU-era rendering.",
        "why_relevant": "Strong teaching case for turning typography into particle-vector material states.",
        "visual_families": ["typography_3d", "particle_vector", "shader_material"],
        "module_types": ["typography_3d", "particle_vector", "shader_material", "asset_pipeline"],
        "canonical_sources": ["https://tympanus.net/codrops/2026/01/28/webgpu-gommage-effect-dissolving-msdf-text-into-dust-and-petals-with-three-js-tsl/"],
    },
    {
        "id": "webgpu-scanning-depth-maps",
        "title": "WebGPU Scanning Effect with Depth Maps",
        "canonical_url": "https://tympanus.net/codrops/2025/03/31/webgpu-scanning-effect-with-depth-maps/",
        "source_type": "tutorial",
        "year": 2025,
        "author_or_studio": "Codrops",
        "currentness": "2025_plus",
        "summary": "Depth-map driven scanning effect for technical reveal and inspection aesthetics.",
        "why_relevant": "Directly maps to VULCA review-gap inspection and scan-plane primitives.",
        "visual_families": ["scan_depth", "shader_material"],
        "module_types": ["scan_depth", "shader_material", "asset_pipeline", "vulca_translation"],
        "canonical_sources": ["https://tympanus.net/codrops/2025/03/31/webgpu-scanning-effect-with-depth-maps/"],
    },
    {
        "id": "matrix-sentinels-particle-trails-tsl",
        "title": "Matrix Sentinels Dynamic Particle Trails",
        "canonical_url": "https://tympanus.net/codrops/2025/05/05/matrix-sentinels-building-dynamic-particle-trails-with-tsl/",
        "source_type": "tutorial",
        "year": 2025,
        "author_or_studio": "Codrops",
        "currentness": "2025_plus",
        "summary": "TSL particle trails and dynamic motion structure in Three.js.",
        "why_relevant": "Useful for hybrid particle-vector trail behavior and uncertainty-state visualization.",
        "visual_families": ["particle_vector", "data_tunnel"],
        "module_types": ["particle_vector", "shader_material", "interaction_state", "performance_runtime"],
        "canonical_sources": ["https://tympanus.net/codrops/2025/05/05/matrix-sentinels-building-dynamic-particle-trails-with-tsl/"],
    },
    {
        "id": "countertype-three-text",
        "title": "Countertype three-text",
        "canonical_url": "https://countertype.com/",
        "source_type": "documentation",
        "year": 2025,
        "author_or_studio": "Countertype",
        "currentness": "still_current",
        "summary": "Modern Three.js text layout and 3D typography pipeline reference.",
        "why_relevant": "Provides technical baseline for treating words and labels as 3D vector material.",
        "visual_families": ["typography_3d"],
        "module_types": ["typography_3d", "asset_pipeline", "performance_runtime"],
        "canonical_sources": ["https://countertype.com/"],
    },
    {
        "id": "phantom-land-interactive-grid",
        "title": "Phantom.land Interactive Grid and 3D Face Particle System",
        "canonical_url": "https://tympanus.net/codrops/2025/06/30/invisible-forces-the-making-of-phantom-lands-interactive-grid-and-3d-face-particle-system/",
        "source_type": "case_study",
        "year": 2025,
        "author_or_studio": "Phantom.land / Codrops",
        "currentness": "2025_plus",
        "summary": "Interactive grid and 3D particle system case study with contemporary technical atmosphere.",
        "why_relevant": "Good reference for spatial technical surfaces and interactive distortion.",
        "visual_families": ["wire_grid", "particle_vector", "ui_sculpture"],
        "module_types": ["wire_grid", "particle_vector", "interaction_state", "vulca_translation"],
        "canonical_sources": ["https://tympanus.net/codrops/2025/06/30/invisible-forces-the-making-of-phantom-lands-interactive-grid-and-3d-face-particle-system/"],
    },
    {
        "id": "false-earth-webgpu-world",
        "title": "False Earth",
        "canonical_url": "https://tympanus.net/codrops/2026/04/21/false-earth-from-webgl-limits-to-a-webgpu-driven-world/",
        "source_type": "case_study",
        "year": 2026,
        "author_or_studio": "Codrops",
        "currentness": "2025_plus",
        "summary": "WebGPU-driven world logic and atmosphere case study.",
        "why_relevant": "Useful high-risk reference for world-scale technical space and WebGPU constraints.",
        "visual_families": ["ui_sculpture", "shader_material"],
        "module_types": ["shader_material", "performance_runtime", "asset_pipeline"],
        "canonical_sources": ["https://tympanus.net/codrops/2026/04/21/false-earth-from-webgl-limits-to-a-webgpu-driven-world/"],
    },
    {
        "id": "spline-contemporary-3d-web",
        "title": "Spline Contemporary 3D Web References",
        "canonical_url": "https://spline.design/",
        "source_type": "product_ref",
        "year": 2025,
        "author_or_studio": "Spline",
        "currentness": "still_current",
        "summary": "Contemporary 3D web design aesthetic reference for spatial UI sculpture.",
        "why_relevant": "Aesthetic reference only; implementation should remain code-native in this repo.",
        "visual_families": ["ui_sculpture"],
        "module_types": ["ui_sculpture", "interaction_state", "vulca_translation"],
        "canonical_sources": ["https://spline.design/"],
    },
    {
        "id": "threejs-webgpu-tsl-docs",
        "title": "Three.js WebGPURenderer and TSL Documentation",
        "canonical_url": "https://threejs.org/docs/pages/WebGPURenderer.html",
        "source_type": "documentation",
        "year": 2025,
        "author_or_studio": "Three.js",
        "currentness": "still_current",
        "summary": "Technical baseline for WebGPU renderer, TSL, and fallback risk.",
        "why_relevant": "Defines implementation constraints for 2025+ Three.js technical aesthetics.",
        "visual_families": ["shader_material"],
        "module_types": ["shader_material", "performance_runtime"],
        "canonical_sources": ["https://threejs.org/docs/pages/WebGPURenderer.html", "https://threejs.org/docs/pages/TSL.html"],
    },
    {
        "id": "maxime-heckel-tsl-webgpu-guide",
        "title": "Field Guide to TSL and WebGPU",
        "canonical_url": "https://blog.maximeheckel.com/posts/field-guide-to-tsl-and-webgpu/",
        "source_type": "tutorial",
        "year": 2025,
        "author_or_studio": "Maxime Heckel",
        "currentness": "still_current",
        "summary": "Teaching reference for TSL and WebGPU mental models.",
        "why_relevant": "Best seed for lesson-path explanations and implementation risk notes.",
        "visual_families": ["shader_material"],
        "module_types": ["shader_material", "performance_runtime"],
        "canonical_sources": ["https://blog.maximeheckel.com/posts/field-guide-to-tsl-and-webgpu/"],
    },
]


def _default_scores(case: dict[str, Any]) -> dict[str, int]:
    license_score = 2 if case["source_type"] in {"github", "documentation", "tutorial"} else 1
    return {
        "aesthetic_relevance": 3,
        "technical_learnability": 2,
        "multimodal_completeness": 0,
        "interaction_clarity": 1,
        "vulca_transfer_value": 2,
        "license_safety": license_score,
    }


def _module_payload(module_type: str) -> dict[str, Any]:
    return {"learning_primitive": f"{module_type} learning primitive", "seed_status": "metadata_only"}


def _metadata(case: dict[str, Any], captured_at: str) -> dict[str, Any]:
    return {
        "id": case["id"],
        "title": case["title"],
        "canonical_url": case["canonical_url"],
        "source_type": case["source_type"],
        "year": case["year"],
        "author_or_studio": case["author_or_studio"],
        "currentness": case["currentness"],
        "summary": case["summary"],
        "why_relevant": case["why_relevant"],
        "review_status": "candidate",
        "quality_scores": _default_scores(case),
        "visual_families": case["visual_families"],
        "canonical_sources": case["canonical_sources"],
        "modules": [
            {
                "module_type": module_type,
                "payload": _module_payload(module_type),
                "evidence_refs": [],
                "confidence": "low",
                "review_status": "partial",
                "review_notes": "Seed module; requires ingestion review.",
            }
            for module_type in case["module_types"]
        ],
        "captures": [
            {
                "id": "canonical-source",
                "evidence_type": "external_doc",
                "path_or_url": case["canonical_url"],
                "capture_method": "source_read",
                "viewport": "none",
                "interaction": "none",
                "captured_at": captured_at,
                "source_url": case["canonical_url"],
                "confidence": "high",
                "rights_status": "source_link_only",
                "notes": "Seed metadata record. Screenshots and motion captures are not complete yet.",
            },
            {
                "id": "screenshot-capture-failure",
                "evidence_type": "screenshot",
                "path_or_url": case["canonical_url"],
                "capture_method": "manual_browser",
                "viewport": "none",
                "interaction": "capture_failed",
                "captured_at": captured_at,
                "source_url": case["canonical_url"],
                "confidence": "medium",
                "rights_status": "source_link_only",
                "notes": "Seed requires visual capture. No local screenshot archived yet.",
            },
            {
                "id": "video-capture-failure",
                "evidence_type": "video",
                "path_or_url": case["canonical_url"],
                "capture_method": "manual_browser",
                "viewport": "none",
                "interaction": "capture_failed",
                "captured_at": captured_at,
                "source_url": case["canonical_url"],
                "confidence": "medium",
                "rights_status": "source_link_only",
                "notes": "Seed requires motion capture. No local interaction clip archived yet.",
            },
        ],
    }


TECHNICAL_ANATOMY_CASE_IDS = {
    "makio-meshline",
    "interactive-text-destruction-webgpu-tsl",
    "webgpu-gommage-msdf-dissolve",
    "webgpu-scanning-depth-maps",
    "matrix-sentinels-particle-trails-tsl",
    "phantom-land-interactive-grid",
}

REBUILD_EXERCISE_CASE_IDS = {
    "makio-meshline",
    "interactive-text-destruction-webgpu-tsl",
    "webgpu-scanning-depth-maps",
}


def _anatomy_text(case: dict[str, Any]) -> str:
    if case["id"] not in TECHNICAL_ANATOMY_CASE_IDS:
        return (
            f"# Anatomy: {case['title']}\n\n"
            f"Primitive: {case['visual_families'][0]} reference primitive.\n\n"
            "Technique: seed-level public-source review; deeper implementation anatomy is pending.\n"
        )
    return (
        f"# Anatomy: {case['title']}\n\n"
        f"Primitive: {case['visual_families'][0]} technical form.\n\n"
        "Technique: map the public reference into one reusable browser-native 3D vector construction.\n\n"
        "Moment: idle state plus one interaction or motion transition must be reviewed before shortlist promotion.\n"
    )


def _lesson_text(case: dict[str, Any]) -> str:
    if case["id"] not in REBUILD_EXERCISE_CASE_IDS:
        return (
            f"# Lesson: {case['title']}\n\n"
            f"minimal_rebuild_exercise: Describe a small {case['visual_families'][0]} rebuild using generated placeholders before shortlist promotion.\n"
        )
    return (
        f"# Lesson: {case['title']}\n\n"
        "lesson_goal: Rebuild the core primitive without copying brand, assets, or proprietary shader code.\n\n"
        f"minimal_rebuild_exercise: Build a small {case['visual_families'][0]} study using generated geometry and placeholder labels.\n\n"
        "runtime_target: local_vite_three\n"
        "verified_status: described\n"
        "verification_command: none\n"
    )


def write_seed_cases(root: Path, *, captured_at: str | None = None) -> list[Path]:
    cases_root = root / "cases"
    cases_root.mkdir(parents=True, exist_ok=True)
    capture_date = captured_at or date.today().isoformat()
    written: list[Path] = []
    for case in SEED_CASES:
        case_dir = cases_root / str(case["id"])
        case_dir.mkdir(parents=True, exist_ok=True)
        for child in ["screenshots", "videos", "traces", "code", "assets"]:
            (case_dir / child).mkdir(exist_ok=True)
        (case_dir / "metadata.json").write_text(
            json.dumps(_metadata(case, capture_date), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (case_dir / "anatomy.md").write_text(_anatomy_text(case), encoding="utf-8")
        (case_dir / "lesson.md").write_text(_lesson_text(case), encoding="utf-8")
        (case_dir / "vulca_translation.md").write_text(
            f"# VULCA Translation: {case['title']}\n\nSeed translation. Review must map this case to source trail, evidence layer, review gap, route decision, or uncertainty.\n",
            encoding="utf-8",
        )
        (case_dir / "assets" / "asset_manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "case_id": case["id"],
                    "assets": [],
                    "rights_status": "source_link_only",
                    "notes": "No local assets archived in seed state.",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(case_dir)
    return written
