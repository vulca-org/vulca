from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_THREAD_ID = "019e7d9c-532a-70b3-8892-fa3ae42baef2"
PACK_REL = Path("docs") / "product" / "ppt-run2-data-skill-quality"
LATEST_RUN_PAYLOAD_HINT = '"latestRunId": "2.62"'


@dataclass(frozen=True)
class ArmSpec:
    arm_id: str
    label: str
    slug: str
    role: str


@dataclass(frozen=True)
class RunSpec:
    run_id: str
    label: str
    four_arm_sheet: str
    arms: tuple[ArmSpec, ...]


RUN_SPECS: tuple[RunSpec, ...] = (
    RunSpec(
        "2.0",
        "Run 2.0",
        "run2-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-run1-5-skill", "baseline"),
            ArmSpec("run2_skill", "Run 2.0 full", "ppt-run2-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.1",
        "Run 2.1",
        "run2-1-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-1-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-1-run1-5-skill", "baseline"),
            ArmSpec("run2_1_full_skill", "Run 2.1 full", "ppt-run2-1-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-1-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.2",
        "Run 2.2",
        "run2-2-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-2-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-2-run1-5-skill", "baseline"),
            ArmSpec("run2_2_full_skill", "Run 2.2 full", "ppt-run2-2-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-2-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.3",
        "Run 2.3",
        "run2-3-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-3-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-3-run1-5-skill", "baseline"),
            ArmSpec("run2_3_full_skill", "Run 2.3 full", "ppt-run2-3-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-3-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.4",
        "Run 2.4",
        "run2-4-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-4-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-4-run1-5-skill", "baseline"),
            ArmSpec("run2_4_full_skill", "Run 2.4 full", "ppt-run2-4-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-4-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.5",
        "Run 2.5",
        "run2-5-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-5-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-5-run1-5-skill", "baseline"),
            ArmSpec("run2_5_full_skill", "Run 2.5 full", "ppt-run2-5-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-5-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.6",
        "Run 2.6",
        "run2-6-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-6-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-6-run1-5-skill", "baseline"),
            ArmSpec("run2_6_full_skill", "Run 2.6 full", "ppt-run2-6-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-6-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.6r",
        "Run 2.6R",
        "run2-6r-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-6r-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-6r-run1-5-skill", "baseline"),
            ArmSpec("run2_6r_visual_repair_full_skill", "Run 2.6R full", "ppt-run2-6r-full-vulca", "full"),
            ArmSpec("bad_aesthetic_memory", "Bad aesthetic memory", "ppt-run2-6r-bad-aesthetic-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.7",
        "Run 2.7",
        "run2-7-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-7-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-7-run1-5-skill", "baseline"),
            ArmSpec("run2_7_full_skill", "Run 2.7 full", "ppt-run2-7-full-vulca", "full"),
            ArmSpec("bad_workflow_memory", "Bad workflow memory", "ppt-run2-7-bad-workflow-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.8",
        "Run 2.8",
        "run2-8-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-8-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-8-run1-5-skill", "baseline"),
            ArmSpec("run2_8_full_skill", "Run 2.8 full", "ppt-run2-8-full-vulca", "full"),
            ArmSpec("bad_memory_schema", "Bad memory schema", "ppt-run2-8-bad-memory-schema", "negative"),
        ),
    ),
    RunSpec(
        "2.9",
        "Run 2.9",
        "run2-9-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-9-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-9-run1-5-skill", "baseline"),
            ArmSpec("run2_9_full_skill", "Run 2.9 full", "ppt-run2-9-full-vulca", "full"),
            ArmSpec("bad_visual_primitive_memory", "Bad visual primitive", "ppt-run2-9-bad-visual-primitive-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.10",
        "Run 2.10",
        "run2-10-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-10-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-10-run1-5-skill", "baseline"),
            ArmSpec("run2_10_full_skill", "Run 2.10 full", "ppt-run2-10-full-vulca", "full"),
            ArmSpec("bad_visual_system_memory", "Bad visual system", "ppt-run2-10-bad-visual-system-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.13",
        "Run 2.13",
        "run2-13-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-13-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-13-run1-5-skill", "baseline"),
            ArmSpec("run2_13_full_skill", "Run 2.13 full", "ppt-run2-13-full-vulca", "full"),
            ArmSpec("bad_thick_data_memory", "Bad thick data memory", "ppt-run2-13-bad-thick-data-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.14",
        "Run 2.14",
        "run2-14-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-14-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-14-run1-5-skill", "baseline"),
            ArmSpec("run2_14_full_skill", "Run 2.14 full", "ppt-run2-14-full-vulca", "full"),
            ArmSpec("bad_visible_workflow_memory", "Bad visible workflow", "ppt-run2-14-bad-visible-workflow-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.16",
        "Run 2.16",
        "run2-16-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-16-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-16-run1-5-skill", "baseline"),
            ArmSpec("run2_16_full_skill", "Run 2.16 full", "ppt-run2-16-full-vulca", "full"),
            ArmSpec("bad_selector_memory", "Bad selector memory", "ppt-run2-16-bad-selector-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.19",
        "Run 2.19",
        "run2-19-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-19-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-19-run1-5-skill", "baseline"),
            ArmSpec("run2_19_full_skill", "Run 2.19 full", "ppt-run2-19-full-vulca", "full"),
            ArmSpec("bad_thickness_memory", "Bad thickness memory", "ppt-run2-19-bad-thickness-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.22",
        "Run 2.22",
        "run2-22-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-22-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-22-run1-5-skill", "baseline"),
            ArmSpec("run2_22_full_selector_memory", "Run 2.22 full", "ppt-run2-22-full-vulca", "full"),
            ArmSpec("bad_selector_memory", "Bad selector memory", "ppt-run2-22-bad-selector-memory", "negative"),
        ),
    ),
    RunSpec(
        "2.25",
        "Run 2.25",
        "run2-25-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-25-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-25-run1-5-skill", "baseline"),
            ArmSpec("run2_25_full_single_usecase_content_visual", "Run 2.25 full", "ppt-run2-25-full-vulca", "full"),
            ArmSpec(
                "bad_content_visual_memory",
                "Bad content/visual memory",
                "ppt-run2-25-bad-content-visual-memory",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.27",
        "Run 2.27",
        "run2-27-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-27-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-27-run1-5-skill", "baseline"),
            ArmSpec("run2_27_full_content_surface_thickening", "Run 2.27 full", "ppt-run2-27-full-vulca", "full"),
            ArmSpec(
                "bad_surface_thickening_memory",
                "Bad surface-thickening memory",
                "ppt-run2-27-bad-surface-thickening-memory",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.28",
        "Run 2.28",
        "run2-28-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-28-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-28-run1-5-skill", "baseline"),
            ArmSpec("run2_28_full_evidence_chain", "Run 2.28 full", "ppt-run2-28-full-vulca", "full"),
            ArmSpec(
                "bad_evidence_chain_memory",
                "Bad evidence-chain memory",
                "ppt-run2-28-bad-evidence-chain-memory",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.29",
        "Run 2.29",
        "run2-29-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-29-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-29-run1-5-skill", "baseline"),
            ArmSpec("run2_29_full_presentation_synthesis", "Run 2.29 full", "ppt-run2-29-full-vulca", "full"),
            ArmSpec(
                "bad_presentation_synthesis_memory",
                "Bad presentation-synthesis memory",
                "ppt-run2-29-bad-presentation-synthesis-memory",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.31",
        "Run 2.31",
        "run2-31-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-31-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-31-run1-5-skill", "baseline"),
            ArmSpec("run2_31_full_spine_climax_repair", "Run 2.31 full", "ppt-run2-31-full-vulca", "full"),
            ArmSpec(
                "bad_spine_climax_repair_memory",
                "Bad spine/climax memory",
                "ppt-run2-31-bad-spine-climax-repair-memory",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.33",
        "Run 2.33",
        "run2-33-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-33-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-33-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_33_full_main_surface_visual_evidence",
                "Run 2.33 full",
                "ppt-run2-33-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_main_surface_visual_evidence_memory",
                "Bad main-surface visual-evidence",
                "ppt-run2-33-bad-main-surface-visual-evidence-memory",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.36",
        "Run 2.36",
        "run2-36-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-36-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-36-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_36_full_visual_evidence_realism",
                "Run 2.36 full",
                "ppt-run2-36-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_visual_evidence_realism_memory",
                "Bad visual-evidence realism",
                "ppt-run2-36-bad-visual-evidence-realism-memory",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.39",
        "Run 2.39",
        "run2-39-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-39-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-39-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_39_full_public_video_visual_direction",
                "Run 2.39 full",
                "ppt-run2-39-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_public_video_visual_direction_memory",
                "Bad public-video visual direction",
                "ppt-run2-39-bad-public-video-visual-direction-memory",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.40",
        "Run 2.40",
        "run2-40-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-40-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-40-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_40_full_visual_compiler",
                "Run 2.40 full",
                "ppt-run2-40-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_trace_visible_visual_compiler",
                "Bad trace-visible visual compiler",
                "ppt-run2-40-bad-trace-visible-visual-compiler",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.41",
        "Run 2.41",
        "run2-41-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-41-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-41-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_41_full_content_visual_asset_compiler",
                "Run 2.41 full",
                "ppt-run2-41-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_thin_content_visual_asset_compiler",
                "Bad thin content/visual asset",
                "ppt-run2-41-bad-thin-content-visual-asset-compiler",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.44",
        "Run 2.44",
        "run2-44-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-44-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-44-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_44_full_semantic_geometry_compiler",
                "Run 2.44 full",
                "ppt-run2-44-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_run2_43_name_only_geometry",
                "Bad Run 2.43 name-only geometry",
                "ppt-run2-44-bad-run2-43-name-only-geometry",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.47",
        "Run 2.47",
        "run2-47-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-47-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-47-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_47_full_composition_grammar_compiler",
                "Run 2.47 full",
                "ppt-run2-47-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_run2_46_missing_composition_grammar",
                "Bad missing composition grammar",
                "ppt-run2-47-bad-missing-composition-grammar",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.50",
        "Run 2.50",
        "run2-50-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-50-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-50-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_50_full_readability_density_renderer",
                "Run 2.50 full",
                "ppt-run2-50-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_run2_49_missing_repair_pack",
                "Bad missing Run 2.49 repair pack",
                "ppt-run2-50-bad-missing-run2-49-repair-pack",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.52",
        "Run 2.52",
        "run2-52-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-52-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-52-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_52_full_editorial_socket_renderer",
                "Run 2.52 full",
                "ppt-run2-52-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_run2_51_missing_editorial_socket_pack",
                "Bad missing socket pack",
                "ppt-run2-52-bad-missing-run2-51-editorial-socket-pack",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.54",
        "Run 2.54",
        "run2-54-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-54-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-54-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_54_full_product_surface_scene",
                "Run 2.54 full",
                "ppt-run2-54-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_run2_53_missing_product_surface_scene_pack",
                "Bad missing product surface scene pack",
                "ppt-run2-54-bad-missing-run2-53-product-surface-scene-pack",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.55",
        "Run 2.55",
        "run2-55-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-55-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-55-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_55_full_text_shape_integration",
                "Run 2.55 full",
                "ppt-run2-55-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_run2_54_without_text_shape_integration",
                "Bad missing text-shape integration",
                "ppt-run2-55-bad-without-text-shape-integration",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.56",
        "Run 2.56",
        "run2-56-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-56-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-56-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_56_full_role_renderer_split",
                "Run 2.56 full",
                "ppt-run2-56-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_run2_55_reused_single_template",
                "Bad reused Run 2.55 single template",
                "ppt-run2-56-bad-reused-single-template",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.58",
        "Run 2.58",
        "run2-58-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-58-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-58-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_58_full_product_content_contract",
                "Run 2.58 full",
                "ppt-run2-58-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_run2_56_without_product_capability_content",
                "Bad missing Run 2.57 content",
                "ppt-run2-58-bad-without-product-capability-content",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.60",
        "Run 2.60",
        "run2-60-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-60-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-60-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_60_full_content_aware_composition",
                "Run 2.60 full",
                "ppt-run2-60-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_run2_58_without_run2_59_composition_compiler",
                "Bad missing Run 2.59 compiler",
                "ppt-run2-60-bad-without-composition-compiler",
                "negative",
            ),
        ),
    ),
    RunSpec(
        "2.62",
        "Run 2.62",
        "run2-62-four-arm-contact-sheet.png",
        (
            ArmSpec("prompt_only", "Prompt only", "ppt-run2-62-prompt-only", "control"),
            ArmSpec("run1_5_skill", "Run 1.5 baseline", "ppt-run2-62-run1-5-skill", "baseline"),
            ArmSpec(
                "run2_62_full_narrative_proof",
                "Run 2.62 full",
                "ppt-run2-62-full-vulca",
                "full",
            ),
            ArmSpec(
                "bad_run2_60_without_run2_61_narrative_proof_dataset",
                "Bad missing Run 2.61 proof",
                "ppt-run2-62-bad-without-narrative-proof",
                "negative",
            ),
        ),
    ),
)


def rel(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_arm(base: Path, out: Path, spec: ArmSpec) -> dict[str, Any] | None:
    arm_dir = base / spec.slug
    preview = arm_dir / "preview"
    if not preview.exists():
        return None
    slides = [preview / f"slide-{index:02d}.png" for index in range(1, 7)]
    slides = [path for path in slides if path.exists()]
    if not slides:
        return None
    trace = read_json(arm_dir / "trace_manifest.json")
    return {
        "id": spec.arm_id,
        "label": spec.label,
        "role": spec.role,
        "slug": spec.slug,
        "contactSheet": rel(preview / "contact-sheet.png", out.parent) if (preview / "contact-sheet.png").exists() else "",
        "traceManifest": rel(arm_dir / "trace_manifest.json", out.parent) if (arm_dir / "trace_manifest.json").exists() else "",
        "deliveryGate": trace.get("release_decision") or trace.get("delivery_gate") or "internal-demo-ok-public-blocked",
        "slides": [rel(path, out.parent) for path in slides],
    }


def local_output_href(result: dict[str, Any], key: str, repo_root: Path, out: Path) -> str:
    raw = str((result.get("local_outputs") or {}).get(key) or "")
    if not raw:
        return ""
    path = (repo_root / raw).resolve()
    return rel(path, out.parent) if path.exists() else raw


def build_reference_data(repo_root: Path, presentations_dir: Path, out: Path) -> dict[str, Any]:
    pack = repo_root / PACK_REL
    sources = read_json(pack / "sources.json")
    decomposition = read_json(pack / "run2_8_tutorial_decomposition.json")
    memory = read_json(pack / "run2_8_executable_design_memory.json")
    gate_matrix = read_json(pack / "run2_8_workflow_gate_matrix.json")
    run29_repair = read_json(pack / "run2_9_visual_primitive_repair.json")
    run29_modules = read_json(pack / "run2_9_executable_visual_modules.json")
    run29_gate_matrix = read_json(pack / "run2_9_visual_gate_matrix.json")
    run210_sources = read_json(pack / "run2_10_visual_system_sources.json")
    run210_memory = read_json(pack / "run2_10_visual_system_memory.json")
    run210_gate_matrix = read_json(pack / "run2_10_visual_system_gate_matrix.json")
    run212_evidence = read_json(pack / "run2_12_thick_multimodal_evidence.json")
    run212_memory = read_json(pack / "run2_12_design_memory_seed.json")
    run212_gate_seed = read_json(pack / "run2_12_workflow_gate_seed.json")
    run215_sources = read_json(pack / "run2_15_layout_selector_sources.json")
    run215_memory = read_json(pack / "run2_15_layout_module_memory.json")
    run215_gate_matrix = read_json(pack / "run2_15_layout_selector_gate_matrix.json")
    run217_motion_audit = read_json(pack / "results" / "run2_17_motion_delivery_audit.json")
    run217_motion_proof = read_json(pack / "results" / "run2_17_motion_renderer_proof_result.json")
    run218_evidence = read_json(pack / "run2_18_multimodal_evidence_expansion.json")
    run218_memory = read_json(pack / "run2_18_design_memory_expansion.json")
    run218_gates = read_json(pack / "run2_18_workflow_gate_expansion.json")
    run218_result = read_json(pack / "results" / "run2_18_thickness_result.json")
    run219_result = read_json(pack / "results" / "run2_19_thickness_rerun_result.json")
    run220_trace_audit = read_json(pack / "results" / "run2_20_trace_effectiveness_audit.json")
    run221_decision_memory = read_json(pack / "run2_21_visual_decision_memory.json")
    run221_selector_gates = read_json(pack / "run2_21_per_role_selector_gates.json")
    run221_rejection_matrix = read_json(pack / "run2_21_evidence_rejection_matrix.json")
    run221_result = read_json(pack / "results" / "run2_21_visual_decision_memory_result.json")
    run222_result = read_json(pack / "results" / "run2_22_selector_rerun_result.json")
    run223_selector_audit = read_json(pack / "results" / "run2_23_selector_effectiveness_audit.json")
    run224_content_memory = read_json(pack / "run2_24_single_usecase_content_memory.json")
    run224_visual_assets = read_json(pack / "run2_24_visual_evidence_asset_memory.json")
    run224_workflow_gates = read_json(pack / "run2_24_content_visual_workflow_gates.json")
    run224_result = read_json(pack / "results" / "run2_24_single_usecase_thickening_result.json")
    run225_result = read_json(pack / "results" / "run2_25_single_usecase_rerun_result.json")
    run226_visual_module_audit = read_json(pack / "results" / "run2_26_visual_module_quality_audit.json")
    run227_result = read_json(pack / "results" / "run2_27_content_surface_thickening_rerun_result.json")
    run228_evidence_chain = read_json(pack / "run2_28_evidence_chain_view_model.json")
    run228_result = read_json(pack / "results" / "run2_28_evidence_chain_rerun_result.json")
    run229_synthesis_memory = read_json(pack / "run2_29_presentation_synthesis_memory.json")
    run229_result = read_json(pack / "results" / "run2_29_presentation_synthesis_rerun_result.json")
    run230_audit = read_json(pack / "results" / "run2_30_presentation_synthesis_audit.json")
    run231_result = read_json(pack / "results" / "run2_31_spine_climax_repair_rerun_result.json")
    run232_audit = read_json(pack / "results" / "run2_32_spine_climax_repair_audit.json")
    run233_result = read_json(pack / "results" / "run2_33_main_surface_visual_evidence_rerun_result.json")
    run234_audit = read_json(pack / "results" / "run2_34_main_surface_visual_evidence_audit.json")
    run235_realism_memory = read_json(pack / "run2_35_visual_evidence_asset_realism_memory.json")
    run235_composition_memory = read_json(pack / "run2_35_editorial_composition_memory.json")
    run235_workflow_gates = read_json(pack / "run2_35_visual_evidence_workflow_gates.json")
    run235_result = read_json(pack / "results" / "run2_35_visual_evidence_realism_workflow_result.json")
    run236_result = read_json(pack / "results" / "run2_36_visual_evidence_realism_rerun_result.json")
    run237_audit = read_json(pack / "results" / "run2_37_visual_quality_audit.json")
    run238_direction_memory = read_json(pack / "run2_38_public_video_slide_direction_memory.json")
    run238_recipe_memory = read_json(pack / "run2_38_per_slide_visual_recipe_memory.json")
    run238_workflow_gates = read_json(pack / "run2_38_public_video_workflow_gates.json")
    run238_result = read_json(pack / "results" / "run2_38_public_video_visual_direction_workflow_result.json")
    run239_result = read_json(pack / "results" / "run2_39_public_video_visual_direction_rerun_result.json")
    run240_result = read_json(pack / "results" / "run2_40_visual_compiler_rerun_result.json")
    run241_result = read_json(pack / "results" / "run2_41_content_visual_asset_compiler_rerun_result.json")
    run242_audit = read_json(pack / "results" / "run2_42_content_visual_asset_quality_audit.json")
    run243_semantic_memory = read_json(pack / "run2_43_semantic_visual_asset_memory.json")
    run243_editorial_typography_memory = read_json(pack / "run2_43_editorial_composition_typography_memory.json")
    run243_workflow_gates = read_json(pack / "run2_43_visual_asset_semantics_workflow_gates.json")
    run243_result = read_json(pack / "results" / "run2_43_visual_asset_semantics_workflow_result.json")
    run244_dataflow_audit = read_json(pack / "results" / "run2_44_dataflow_readiness_audit.json")
    run244_result = read_json(pack / "results" / "run2_44_semantic_geometry_rerun_result.json")
    run245_audit = read_json(pack / "results" / "run2_45_semantic_geometry_effectiveness_audit.json")
    run246_decomposition = read_json(pack / "run2_46_multimodal_composition_decomposition.json")
    run246_grammar = read_json(pack / "run2_46_visual_object_grammar_memory.json")
    run246_gates = read_json(pack / "run2_46_composition_workflow_gates.json")
    run246_result = read_json(pack / "results" / "run2_46_multimodal_composition_memory_result.json")
    run247_result = read_json(pack / "results" / "run2_47_composition_grammar_rerun_result.json")
    run248_audit = read_json(pack / "results" / "run2_48_composition_grammar_effectiveness_audit.json")
    run249_readability = read_json(pack / "run2_49_readability_memory.json")
    run249_density = read_json(pack / "run2_49_content_evidence_density_memory.json")
    run249_gates = read_json(pack / "run2_49_editorial_renderer_workflow_gates.json")
    run249_result = read_json(
        pack / "results" / "run2_49_readability_content_density_renderer_repair_result.json"
    )
    run250_result = read_json(pack / "results" / "run2_50_readability_density_renderer_rerun_result.json")
    run251_copy_memory = read_json(pack / "run2_51_editorial_copy_memory.json")
    run251_socket_memory = read_json(pack / "run2_51_shape_text_socket_memory.json")
    run251_gates = read_json(pack / "run2_51_renderer_archetype_workflow_gates.json")
    run251_result = read_json(pack / "results" / "run2_51_editorial_shape_text_repair_result.json")
    run252_result = read_json(pack / "results" / "run2_52_editorial_socket_renderer_rerun_result.json")
    run253_scene_memory = read_json(pack / "run2_53_product_surface_scene_memory.json")
    run253_evidence_memory = read_json(pack / "run2_53_business_visual_evidence_memory.json")
    run253_gates = read_json(pack / "run2_53_scene_renderer_workflow_gates.json")
    run253_result = read_json(pack / "results" / "run2_53_product_surface_scene_repair_result.json")
    run254_result = read_json(pack / "results" / "run2_54_product_surface_scene_rerun_result.json")
    run255_result = read_json(pack / "results" / "run2_55_text_shape_integration_rerun_result.json")
    run256_result = read_json(pack / "results" / "run2_56_role_renderer_split_rerun_result.json")
    run257_capability_memory = read_json(pack / "run2_57_product_capability_memory.json")
    run257_message_contracts = read_json(pack / "run2_57_slide_message_contracts.json")
    run257_workflow_gates = read_json(pack / "run2_57_content_workflow_gates.json")
    run257_result = read_json(pack / "results" / "run2_57_product_capability_content_result.json")
    run258_result = read_json(pack / "results" / "run2_58_product_content_contract_rerun_result.json")
    run258_open_source_research = read_json(pack / "run2_58_open_source_slide_code_research.json")
    run259_contracts = read_json(pack / "run2_59_content_composition_contracts.json")
    run259_capacity = read_json(pack / "run2_59_layout_capacity_model.json")
    run259_selector = read_json(pack / "run2_59_content_to_layout_selector.json")
    run259_trace_policy = read_json(pack / "run2_59_public_surface_trace_policy.json")
    run259_gates = read_json(pack / "run2_59_composition_workflow_gates.json")
    run259_result = read_json(pack / "results" / "run2_59_content_aware_composition_compiler_result.json")
    run260_result = read_json(pack / "results" / "run2_60_content_aware_composition_rerun_result.json")
    run261_narrative = read_json(pack / "run2_61_narrative_proof_dataset.json")
    run261_selector = read_json(pack / "run2_61_story_to_visual_carrier_selector.json")
    run261_fusion = read_json(pack / "run2_61_text_socket_fusion_contracts.json")
    run261_source_policy = read_json(pack / "run2_61_source_to_public_proof_policy.json")
    run261_gates = read_json(pack / "run2_61_narrative_workflow_gates.json")
    run261_result = read_json(pack / "results" / "run2_61_narrative_proof_dataset_result.json")
    run262_result = read_json(pack / "results" / "run2_62_narrative_proof_rerun_result.json")
    run211_audit = read_json(pack / "results" / "run2_11_data_workflow_audit.json")
    workflow = read_json(pack / "skill_workflow.json")
    source_records = read_json(pack / "run2_7_multimodal_source_records.json")
    skill_markdown = read_text(pack / "vulca_ppt_skill.md")

    return {
        "packPath": PACK_REL.as_posix(),
        "diagnosis": [
            {
                "label": "2.8 visual verdict",
                "body": "The data and workflow are executable, but the code bindings still render mostly type ladders, spacing zones, before/after panels, gates, and one hero object.",
            },
            {
                "label": "Why it still feels boxy",
                "body": "Tutorial learning has been translated into native PPT rectangles and text modules, so it proves traceable execution more than high-end editorial composition.",
            },
            {
                "label": "Next design problem",
                "body": "The next rerun must upgrade visual primitives: product-surface composition, asymmetry, depth, editorial spread, motion beats, and a non-dashboard climax.",
            },
            {
                "label": "2.13 thick-data rerun guard",
                "body": "Run 2.13 must prove the Run 2.12 evidence, memory seeds, and workflow gate seeds changed the native PPT generation path; evidence-only negative control should remain weaker.",
            },
            {
                "label": "2.15 layout module selector",
                "body": "Run 2.15 is data/workflow-only: it adds selector sources, layout module memory, and selector gates before the next four-arm rerun.",
            },
            {
                "label": "2.18 data/workflow thickness",
                "body": "Run 2.18 is not a new PPT. It expands derived evidence, executable memory, and workflow gates that Run 2.19 consumes before native code generation.",
            },
            {
                "label": "2.19 generated thickness rerun",
                "body": "Run 2.19 is the generated four-arm proof that the Run 2.18 thickness pack is selected in trace before native PPT code writes the slides.",
            },
            {
                "label": "2.17 delivery truth",
                "body": "Run 2.17 is audit-only: HTML viewer is static, current PPTX files have no native animation XML, and Keynote readout is static editable slides until a renderer proof exists.",
            },
        ],
        "sources": sources.get("sources", []),
        "sourceRecords": source_records.get("records", []),
        "decompositionStatus": decomposition.get("status", ""),
        "decompositionUnits": decomposition.get("units", []),
        "memoryStatus": memory.get("status", ""),
        "memoryBindings": memory.get("bindings", []),
        "gateStatus": gate_matrix.get("status", ""),
        "workflowGates": gate_matrix.get("gates", []),
        "run29RepairStatus": run29_repair.get("status", ""),
        "run29PrimitiveRepairs": run29_repair.get("primitive_repairs", []),
        "run29ModuleStatus": run29_modules.get("status", ""),
        "run29VisualModules": run29_modules.get("modules", []),
        "run29GateStatus": run29_gate_matrix.get("status", ""),
        "run29VisualGates": run29_gate_matrix.get("gates", []),
        "run210SourceStatus": run210_sources.get("status", ""),
        "run210VisualSystemSources": run210_sources.get("sources", []),
        "run210MemoryStatus": run210_memory.get("status", ""),
        "run210VisualSystems": run210_memory.get("visual_systems", []),
        "run210GateStatus": run210_gate_matrix.get("status", ""),
        "run210VisualGates": run210_gate_matrix.get("gates", []),
        "run212EvidenceStatus": run212_evidence.get("status", ""),
        "run212ThickEvidenceRecords": run212_evidence.get("records", []),
        "run212MemoryStatus": run212_memory.get("status", ""),
        "run212MemorySeeds": run212_memory.get("memory_seeds", []),
        "run212GateStatus": run212_gate_seed.get("status", ""),
        "run212WorkflowGateSeeds": run212_gate_seed.get("gates", []),
        "run215SelectorSourceStatus": run215_sources.get("status", ""),
        "run215SelectorSources": run215_sources.get("records", []),
        "run215SelectorMemoryStatus": run215_memory.get("status", ""),
        "run215SelectorModules": run215_memory.get("modules", []),
        "run215SelectorGateStatus": run215_gate_matrix.get("status", ""),
        "run215SelectorGates": run215_gate_matrix.get("gates", []),
        "run217MotionAuditStatus": run217_motion_audit.get("status", ""),
        "run217MotionAudit": run217_motion_audit,
        "run217MotionProofStatus": run217_motion_proof.get("status", ""),
        "run217MotionProof": run217_motion_proof,
        "run217MotionProofHtmlHref": local_output_href(run217_motion_proof, "html", repo_root, out),
        "run217MotionProofManifestHref": local_output_href(run217_motion_proof, "manifest", repo_root, out),
        "run218EvidenceStatus": run218_evidence.get("status", ""),
        "run218EvidenceRecords": run218_evidence.get("records", []),
        "run218MemoryStatus": run218_memory.get("status", ""),
        "run218MemoryExpansions": run218_memory.get("memory_expansions", []),
        "run218GateStatus": run218_gates.get("status", ""),
        "run218WorkflowGates": run218_gates.get("gates", []),
        "run218ResultStatus": run218_result.get("status", ""),
        "run218Result": run218_result,
        "run219ResultStatus": run219_result.get("status", ""),
        "run219Result": run219_result,
        "run220TraceAuditStatus": run220_trace_audit.get("status", ""),
        "run220TraceAudit": run220_trace_audit,
        "run221DecisionMemoryStatus": run221_decision_memory.get("status", ""),
        "run221DecisionMemory": run221_decision_memory.get("visual_decision_memory", []),
        "run221SelectorGateStatus": run221_selector_gates.get("status", ""),
        "run221SelectorGates": run221_selector_gates.get("gates", []),
        "run221RejectionMatrixStatus": run221_rejection_matrix.get("status", ""),
        "run221RejectionRecords": run221_rejection_matrix.get("role_records", []),
        "run221ResultStatus": run221_result.get("status", ""),
        "run221Result": run221_result,
        "run222ResultStatus": run222_result.get("status", ""),
        "run222Result": run222_result,
        "run223SelectorAuditStatus": run223_selector_audit.get("status", ""),
        "run223SelectorAudit": run223_selector_audit,
        "run224ContentMemoryStatus": run224_content_memory.get("status", ""),
        "run224ContentMemory": run224_content_memory.get("slide_content_memory", []),
        "run224SelectedUsecase": run224_content_memory.get("selected_usecase", {}),
        "run224StoryPolicy": run224_content_memory.get("story_policy", {}),
        "run224VisualAssetStatus": run224_visual_assets.get("status", ""),
        "run224VisualAssets": run224_visual_assets.get("visual_evidence_assets", []),
        "run224WorkflowGateStatus": run224_workflow_gates.get("status", ""),
        "run224WorkflowGates": run224_workflow_gates.get("gates", []),
        "run224ResultStatus": run224_result.get("status", ""),
        "run224Result": run224_result,
        "run225ResultStatus": run225_result.get("status", ""),
        "run225Result": run225_result,
        "run226VisualModuleAuditStatus": run226_visual_module_audit.get("status", ""),
        "run226VisualModuleAudit": run226_visual_module_audit,
        "run227ResultStatus": run227_result.get("status", ""),
        "run227Result": run227_result,
        "run228EvidenceChainStatus": run228_evidence_chain.get("status", ""),
        "run228EvidenceChain": run228_evidence_chain,
        "run228ResultStatus": run228_result.get("status", ""),
        "run228Result": run228_result,
        "run229SynthesisMemoryStatus": run229_synthesis_memory.get("status", ""),
        "run229SynthesisMemory": run229_synthesis_memory,
        "run229ResultStatus": run229_result.get("status", ""),
        "run229Result": run229_result,
        "run230AuditStatus": run230_audit.get("status", ""),
        "run230Audit": run230_audit,
        "run231ResultStatus": run231_result.get("status", ""),
        "run231Result": run231_result,
        "run232AuditStatus": run232_audit.get("status", ""),
        "run232Audit": run232_audit,
        "run233ResultStatus": run233_result.get("status", ""),
        "run233Result": run233_result,
        "run234AuditStatus": run234_audit.get("status", ""),
        "run234Audit": run234_audit,
        "run235RealismMemoryStatus": run235_realism_memory.get("status", ""),
        "run235RealismMemory": run235_realism_memory.get("visual_evidence_asset_realism_records", []),
        "run235CompositionMemoryStatus": run235_composition_memory.get("status", ""),
        "run235CompositionMemory": run235_composition_memory.get("editorial_composition_records", []),
        "run235WorkflowGateStatus": run235_workflow_gates.get("status", ""),
        "run235WorkflowGates": run235_workflow_gates.get("gates", []),
        "run235ResultStatus": run235_result.get("status", ""),
        "run235Result": run235_result,
        "run236ResultStatus": run236_result.get("status", ""),
        "run236Result": run236_result,
        "run237AuditStatus": run237_audit.get("status", ""),
        "run237Audit": run237_audit,
        "run238DirectionMemoryStatus": run238_direction_memory.get("status", ""),
        "run238DirectionMemory": run238_direction_memory.get("public_video_slide_direction_records", []),
        "run238RecipeMemoryStatus": run238_recipe_memory.get("status", ""),
        "run238RecipeMemory": run238_recipe_memory.get("per_slide_visual_recipe_records", []),
        "run238WorkflowGateStatus": run238_workflow_gates.get("status", ""),
        "run238WorkflowGates": run238_workflow_gates.get("gates", []),
        "run238WorkflowGateContract": run238_workflow_gates.get("visual_rhythm_diversity_contract", {}),
        "run238ResultStatus": run238_result.get("status", ""),
        "run238Result": run238_result,
        "run239ResultStatus": run239_result.get("status", ""),
        "run239Result": run239_result,
        "run240ResultStatus": run240_result.get("status", ""),
        "run240Result": run240_result,
        "run241ResultStatus": run241_result.get("status", ""),
        "run241Result": run241_result,
        "run242AuditStatus": run242_audit.get("status", ""),
        "run242Audit": run242_audit,
        "run243SemanticAssetMemoryStatus": run243_semantic_memory.get("status", ""),
        "run243SemanticVisualAssets": run243_semantic_memory.get("semantic_visual_asset_records", []),
        "run243SourceBoundary": run243_semantic_memory.get("source_boundary", {}),
        "run243EditorialTypographyMemoryStatus": run243_editorial_typography_memory.get("status", ""),
        "run243EditorialTypographyMemory": run243_editorial_typography_memory.get(
            "editorial_composition_typography_records", []
        ),
        "run243WorkflowGateStatus": run243_workflow_gates.get("status", ""),
        "run243VisualAssetSemanticsWorkflowGates": run243_workflow_gates.get(
            "visual_asset_semantics_workflow_gates", []
        ),
        "run243NextRerunContract": run243_workflow_gates.get("next_rerun_contract", ""),
        "run243ResultStatus": run243_result.get("status", ""),
        "run243Result": run243_result,
        "run244DataflowAuditStatus": run244_dataflow_audit.get("status", ""),
        "run244DataflowAudit": run244_dataflow_audit,
        "run244ResultStatus": run244_result.get("status", ""),
        "run244Result": run244_result,
        "run245AuditStatus": run245_audit.get("status", ""),
        "run245Audit": run245_audit,
        "run246DecompositionStatus": run246_decomposition.get("status", ""),
        "run246CompositionDecomposition": run246_decomposition.get(
            "multimodal_composition_decomposition_records", []
        ),
        "run246GrammarStatus": run246_grammar.get("status", ""),
        "run246VisualObjectGrammar": run246_grammar.get("visual_object_grammar_records", []),
        "run246GateStatus": run246_gates.get("status", ""),
        "run246CompositionWorkflowGates": run246_gates.get("composition_workflow_gates", []),
        "run246ResultStatus": run246_result.get("status", ""),
        "run246Result": run246_result,
        "run247ResultStatus": run247_result.get("status", ""),
        "run247Result": run247_result,
        "run247ResultPath": "run2_47_composition_grammar_rerun_result.json",
        "run247TargetLayer": (run247_result.get("quality_delta") or {}).get(
            "target_layer", "composition_grammar_binding"
        ),
        "run247SourceDataStatus": (run247_result.get("quality_delta") or {}).get(
            "source_data_status", "run2_46_composition_grammar_consumed_before_native_ppt_drawing"
        ),
        "run248AuditStatus": run248_audit.get("status", ""),
        "run248Audit": run248_audit,
        "run248AuditPath": "run2_48_composition_grammar_effectiveness_audit.json",
        "run249ReadabilityStatus": run249_readability.get("status", ""),
        "run249ReadabilityRecords": run249_readability.get("readability_records", []),
        "run249DensityStatus": run249_density.get("status", ""),
        "run249DensityRecords": run249_density.get("content_evidence_density_records", []),
        "run249GateStatus": run249_gates.get("status", ""),
        "run249Gates": run249_gates.get("editorial_renderer_workflow_gates", []),
        "run249ResultStatus": run249_result.get("status", ""),
        "run249Result": run249_result,
        "run250ResultStatus": run250_result.get("status", ""),
        "run250Result": run250_result,
        "run250ResultPath": "run2_50_readability_density_renderer_rerun_result.json",
        "run250TargetLayer": (run250_result.get("quality_delta") or {}).get(
            "target_layer", "readability_content_density_and_editorial_renderer_binding"
        ),
        "run251CopyMemoryStatus": run251_copy_memory.get("status", ""),
        "run251CopyRecords": run251_copy_memory.get("editorial_copy_records", []),
        "run251SocketMemoryStatus": run251_socket_memory.get("status", ""),
        "run251SocketRecords": run251_socket_memory.get("shape_text_socket_records", []),
        "run251GateStatus": run251_gates.get("status", ""),
        "run251Gates": run251_gates.get("renderer_archetype_workflow_gates", []),
        "run251ResultStatus": run251_result.get("status", ""),
        "run251Result": run251_result,
        "run251ResultPath": "run2_51_editorial_shape_text_repair_result.json",
        "run252ResultStatus": run252_result.get("status", ""),
        "run252Result": run252_result,
        "run252ResultPath": "run2_52_editorial_socket_renderer_rerun_result.json",
        "run252TargetLayer": (run252_result.get("quality_delta") or {}).get(
            "target_layer", "editorial_copy_shape_text_socket_and_renderer_archetype_binding"
        ),
        "run252SourceDataStatus": (run252_result.get("quality_delta") or {}).get(
            "source_data_status", "run2_51_editorial_socket_pack_consumed_before_native_ppt_drawing"
        ),
        "run253ProductSurfaceSceneStatus": run253_scene_memory.get("status", ""),
        "run253ProductSurfaceScenes": run253_scene_memory.get("product_surface_scene_records", []),
        "run253BusinessVisualEvidenceStatus": run253_evidence_memory.get("status", ""),
        "run253BusinessVisualEvidence": run253_evidence_memory.get("business_visual_evidence_records", []),
        "run253SceneRendererGateStatus": run253_gates.get("status", ""),
        "run253SceneRendererGates": run253_gates.get("scene_renderer_workflow_gates", []),
        "run253ResultStatus": run253_result.get("status", ""),
        "run253Result": run253_result,
        "run253ResultPath": "run2_53_product_surface_scene_repair_result.json",
        "run254ResultStatus": run254_result.get("status", ""),
        "run254Result": run254_result,
        "run254ResultPath": "run2_54_product_surface_scene_rerun_result.json",
        "run254TargetLayer": (run254_result.get("quality_delta") or {}).get(
            "target_layer", "product_surface_scene_and_business_visual_evidence_binding"
        ),
        "run254SourceDataStatus": (run254_result.get("quality_delta") or {}).get(
            "source_data_status", "run2_53_product_surface_scene_pack_consumed_before_native_ppt_drawing"
        ),
        "run255ResultStatus": run255_result.get("status", ""),
        "run255Result": run255_result,
        "run255ResultPath": "run2_55_text_shape_integration_rerun_result.json",
        "run255TargetLayer": (run255_result.get("quality_delta") or {}).get(
            "target_layer", "text_shape_integration_and_shape_vocabulary_repair"
        ),
        "run255SourceDataStatus": (run255_result.get("quality_delta") or {}).get(
            "source_data_status", "run2_54_product_surface_scene_rerun_consumed_before_text_shape_redraw"
        ),
        "run256ResultStatus": run256_result.get("status", ""),
        "run256Result": run256_result,
        "run256ResultPath": "run2_56_role_renderer_split_rerun_result.json",
        "run256TargetLayer": (run256_result.get("quality_delta") or {}).get(
            "target_layer", "role_specific_renderer_variation_and_layout_qa"
        ),
        "run256SourceDataStatus": (run256_result.get("quality_delta") or {}).get(
            "source_data_status", "run2_55_text_shape_integration_consumed_before_role_renderer_redraw"
        ),
        "run257ProductCapabilityStatus": run257_capability_memory.get("status", ""),
        "run257ProductCapabilities": run257_capability_memory.get("product_capability_records", []),
        "run257ProductLogicRelations": run257_capability_memory.get("product_logic_relation_records", []),
        "run257CompetitorBoundaries": run257_capability_memory.get("competitor_boundary_records", []),
        "run257SlideMessageContractStatus": run257_message_contracts.get("status", ""),
        "run257SlideMessageContracts": run257_message_contracts.get("slide_message_contracts", []),
        "run257ContentWorkflowGateStatus": run257_workflow_gates.get("status", ""),
        "run257ContentWorkflowGates": run257_workflow_gates.get("content_workflow_gates", []),
        "run257NextGeneratedRunContract": run257_workflow_gates.get("next_generated_run_contract", {}),
        "run257ResultStatus": run257_result.get("status", ""),
        "run257Result": run257_result,
        "run257ResultPath": "run2_57_product_capability_content_result.json",
        "run257ProductCapabilityPath": "run2_57_product_capability_memory.json",
        "run257SlideMessageContractsPath": "run2_57_slide_message_contracts.json",
        "run257ContentWorkflowGatesPath": "run2_57_content_workflow_gates.json",
        "run257TargetLayer": (run257_result.get("quality_delta") or {}).get(
            "target_layer", "product_capability_narrative_and_content_specificity"
        ),
        "run257SourceDataStatus": (run257_result.get("quality_delta") or {}).get(
            "source_data_status", "run2_56_role_renderer_split_rerun_public_blocked"
        ),
        "run258ResultStatus": run258_result.get("status", ""),
        "run258Result": run258_result,
        "run258ResultPath": "run2_58_product_content_contract_rerun_result.json",
        "run258TargetLayer": (run258_result.get("quality_delta") or {}).get(
            "target_layer", "product_capability_content_contract_binding"
        ),
        "run258SourceDataStatus": (run258_result.get("quality_delta") or {}).get(
            "source_data_status", "run2_57_product_capability_content_consumed_before_native_ppt_drawing"
        ),
        "run258OpenSourceResearchStatus": run258_open_source_research.get("status", ""),
        "run258OpenSourceResearch": run258_open_source_research,
        "run258OpenSourceReferences": run258_open_source_research.get("open_source_reference_records", []),
        "run258OpenSourceUsePolicy": run258_open_source_research.get("usage_boundary", {}),
        "run258OpenSourceResearchPath": "run2_58_open_source_slide_code_research.json",
        "run258GeneratorPath": "scripts/generate_ppt_run2_58_product_content_contract_arms.mjs",
        "run258FullTracePath": "ppt-run2-58-full-vulca/trace_manifest.json",
        "run258BadTracePath": "ppt-run2-58-bad-without-product-capability-content/trace_manifest.json",
        "run258FullDeckSourcePath": "ppt-run2-58-full-vulca/slides/deck-source.mjs",
        "run258FourArmSheetPath": "run2-58-four-arm-contact-sheet.png",
        "run259ResultStatus": run259_result.get("status", ""),
        "run259Result": run259_result,
        "run259ResultPath": "run2_59_content_aware_composition_compiler_result.json",
        "run259ContentCompositionStatus": run259_contracts.get("status", ""),
        "run259ContentContracts": run259_contracts.get("content_composition_contracts", []),
        "run259ContentContractsPath": "run2_59_content_composition_contracts.json",
        "run259LayoutCapacityStatus": run259_capacity.get("status", ""),
        "run259LayoutCapacityRecords": run259_capacity.get("layout_capacity_records", []),
        "run259LayoutCapacityPath": "run2_59_layout_capacity_model.json",
        "run259ContentSelectorStatus": run259_selector.get("status", ""),
        "run259SelectorRecords": run259_selector.get("content_to_layout_selection_records", []),
        "run259ContentSelectorPath": "run2_59_content_to_layout_selector.json",
        "run259TracePolicyStatus": run259_trace_policy.get("status", ""),
        "run259PublicTracePolicy": run259_trace_policy,
        "run259TracePolicyPath": "run2_59_public_surface_trace_policy.json",
        "run259WorkflowGateStatus": run259_gates.get("status", ""),
        "run259WorkflowGates": run259_gates.get("composition_workflow_gates", []),
        "run259WorkflowGatesPath": "run2_59_composition_workflow_gates.json",
        "run259NextGeneratedRunContract": run259_gates.get("next_generated_run_contract", {}),
        "run259TargetLayer": (run259_result.get("quality_delta") or {}).get(
            "target_layer", "content_aware_composition_compiler"
        ),
        "run259FailureMode": (run259_result.get("quality_delta") or {}).get(
            "fixes_failure_mode",
            "content_thickness_and_layout_module_memory_not_bound_before_native_ppt_drawing",
        ),
        "run260ResultStatus": run260_result.get("status", ""),
        "run260Result": run260_result,
        "run260ResultPath": "run2_60_content_aware_composition_rerun_result.json",
        "run260TargetLayer": (run260_result.get("quality_delta") or {}).get(
            "target_layer", "content_aware_composition_compiler_consumed"
        ),
        "run260SourceDataStatus": (run260_result.get("quality_delta") or {}).get(
            "source_data_status", "run2_59_composition_compiler_consumed_before_native_ppt_drawing"
        ),
        "run260GeneratorPath": "scripts/generate_ppt_run2_60_content_aware_composition_arms.mjs",
        "run260FullTracePath": "ppt-run2-60-full-vulca/trace_manifest.json",
        "run260BadTracePath": "ppt-run2-60-bad-without-composition-compiler/trace_manifest.json",
        "run260FourArmSheetPath": "run2-60-four-arm-contact-sheet.png",
        "run261ResultStatus": run261_result.get("status", ""),
        "run261Result": run261_result,
        "run261ResultPath": "run2_61_narrative_proof_dataset_result.json",
        "run261NarrativeStatus": run261_narrative.get("status", ""),
        "run261NarrativeRecords": run261_narrative.get("narrative_proof_records", []),
        "run261NarrativePath": "run2_61_narrative_proof_dataset.json",
        "run261SelectorStatus": run261_selector.get("status", ""),
        "run261SelectorRecords": run261_selector.get("story_to_visual_carrier_records", []),
        "run261SelectorPath": "run2_61_story_to_visual_carrier_selector.json",
        "run261FusionStatus": run261_fusion.get("status", ""),
        "run261FusionRecords": run261_fusion.get("text_socket_fusion_contracts", []),
        "run261FusionPath": "run2_61_text_socket_fusion_contracts.json",
        "run261SourcePolicyStatus": run261_source_policy.get("status", ""),
        "run261SourcePolicy": run261_source_policy,
        "run261SourcePolicyPath": "run2_61_source_to_public_proof_policy.json",
        "run261WorkflowGateStatus": run261_gates.get("status", ""),
        "run261WorkflowGates": run261_gates.get("narrative_workflow_gates", []),
        "run261WorkflowGatesPath": "run2_61_narrative_workflow_gates.json",
        "run261NextGeneratedRunContract": run261_gates.get("next_generated_run_contract", {}),
        "run262ResultStatus": run262_result.get("status", ""),
        "run262Result": run262_result,
        "run262ResultPath": "run2_62_narrative_proof_rerun_result.json",
        "run262TargetLayer": (run262_result.get("quality_delta") or {}).get(
            "target_layer", "run2_61_narrative_proof_dataset_consumed"
        ),
        "run262SourceDataStatus": (run262_result.get("quality_delta") or {}).get(
            "source_data_status", "run2_61_narrative_proof_dataset_consumed_before_native_ppt_drawing"
        ),
        "run262GeneratorPath": "scripts/generate_ppt_run2_62_narrative_proof_arms.mjs",
        "run262FullTracePath": "ppt-run2-62-full-vulca/trace_manifest.json",
        "run262BadTracePath": "ppt-run2-62-bad-without-narrative-proof/trace_manifest.json",
        "run262FourArmSheetPath": "run2-62-four-arm-contact-sheet.png",
        "selectorLayer": {
            "label": "Run 2.15 selector",
            "summary": "layout module selector before the next four-arm rerun",
            "sources": run215_sources,
            "memory": run215_memory,
            "gateMatrix": run215_gate_matrix,
        },
        "run211Audit": run211_audit,
        "workflowStatus": workflow.get("status", ""),
        "workflowStages": workflow.get("stages", []),
        "skillMarkdown": skill_markdown,
    }


def build_data(presentations_dir: Path, out: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    runs: list[dict[str, Any]] = []
    for run in RUN_SPECS:
        arms = [arm for arm_spec in run.arms if (arm := build_arm(presentations_dir, out, arm_spec))]
        if not arms:
            continue
        full_arm = next((arm for arm in arms if arm["role"] == "full"), arms[0])
        four_arm_sheet = presentations_dir / run.four_arm_sheet
        runs.append(
            {
                "id": run.run_id,
                "label": run.label,
                "fourArmSheet": rel(four_arm_sheet, out.parent) if four_arm_sheet.exists() else "",
                "arms": arms,
                "fullArm": full_arm,
            }
        )
    return {
        "title": "PPT run viewer",
        "status": "internal-demo-ok-public-blocked",
        "runs": runs,
        "latestRunId": runs[-1]["id"] if runs else "",
        "generatedFrom": "scripts/build_ppt_run_html_viewer.py",
        "references": build_reference_data(repo_root, presentations_dir, out),
    }


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def build_html(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=True, indent=2)
    latest = esc(str(data.get("latestRunId") or ""))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>PPT Run Viewer</title>
  <style>
    :root {{
      --bg: #f5f3ee;
      --panel: #ffffff;
      --ink: #17181c;
      --muted: #5d6670;
      --line: #d0cbc1;
      --dark: #15171c;
      --accent: #e24d30;
      --blue: #2a63da;
      --green: #0d8d68;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; min-height: 100%; background: var(--bg); color: var(--ink); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ overflow: hidden; }}
    button, input {{ font: inherit; }}
    .app {{ display: grid; grid-template-rows: auto auto 1fr; height: 100vh; }}
    .topbar {{ display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 18px 22px 14px; border-bottom: 1px solid var(--line); background: rgba(245, 243, 238, 0.96); }}
    .brand {{ display: flex; flex-direction: column; gap: 3px; min-width: 220px; }}
    .brand h1 {{ margin: 0; font-size: 22px; line-height: 1.1; }}
    .brand .meta {{ color: var(--muted); font-size: 12px; }}
    .statusbar {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    .pill {{ display: inline-flex; align-items: center; height: 28px; padding: 0 10px; border-radius: 999px; background: var(--panel); border: 1px solid var(--line); font-size: 12px; color: var(--muted); white-space: nowrap; }}
    .pill.strong {{ background: var(--dark); border-color: var(--dark); color: #fff; }}
    .toolbar {{ display: flex; align-items: center; gap: 18px; padding: 12px 22px; border-bottom: 1px solid var(--line); background: #fbfaf7; overflow: hidden; }}
    .versionRail, .viewRail {{ display: flex; gap: 8px; align-items: center; }}
    .versionRail {{ flex: 1 1 auto; min-width: 0; overflow-x: auto; padding-bottom: 2px; }}
    .viewRail {{ flex: 0 0 auto; }}
    .railLabel {{ font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; }}
    .seg {{ height: 34px; border: 1px solid var(--line); background: #fff; color: var(--ink); border-radius: 6px; padding: 0 12px; cursor: pointer; white-space: nowrap; }}
    .seg.active {{ background: var(--dark); color: #fff; border-color: var(--dark); }}
    .seg[data-role="full"].active {{ background: var(--accent); border-color: var(--accent); }}
    .content {{ min-height: 0; overflow: auto; padding: 18px 22px 26px; }}
    .sectionHeader {{ display: flex; align-items: end; justify-content: space-between; gap: 18px; margin-bottom: 14px; }}
    .sectionHeader h2 {{ margin: 0; font-size: 20px; }}
    .sectionHeader .summary {{ color: var(--muted); font-size: 13px; }}
    .fourGrid {{ display: grid; grid-template-columns: repeat(4, minmax(340px, 1fr)); gap: 16px; min-width: 1400px; }}
    .seriesGrid {{ display: flex; gap: 16px; align-items: flex-start; min-width: max-content; }}
    .armCard, .seriesCard {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; box-shadow: 0 1px 0 rgba(0,0,0,0.04); }}
    .armHead, .seriesHead {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; background: var(--dark); color: #fff; padding: 11px 12px; }}
    .armHead h3, .seriesHead h3 {{ margin: 0; font-size: 14px; }}
    .armHead .tag, .seriesHead .tag {{ font-size: 10px; color: #d9dde2; text-transform: uppercase; }}
    .slidesGrid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; padding: 10px; }}
    .seriesCard {{ width: 360px; }}
    .seriesCard .slidesGrid {{ grid-template-columns: repeat(2, 1fr); }}
    .slideTile {{ position: relative; border: 1px solid #d8dce0; background: #fff; cursor: zoom-in; overflow: hidden; }}
    .slideTile img {{ display: block; width: 100%; height: auto; aspect-ratio: 16 / 9; object-fit: contain; background: #fff; }}
    .slideNo {{ position: absolute; left: 6px; bottom: 5px; height: 18px; min-width: 34px; padding: 2px 6px; background: rgba(21,23,28,0.82); color: #fff; font-size: 10px; border-radius: 3px; }}
    .contactRow {{ display: flex; gap: 8px; padding: 0 10px 10px; }}
    .contactRow button {{ height: 30px; border: 1px solid var(--line); background: #f8f8f5; border-radius: 6px; padding: 0 10px; cursor: zoom-in; color: var(--muted); }}
    .sheetPanel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 12px; min-width: 1120px; }}
    .sheetPanel img {{ display: block; width: 100%; height: auto; border: 1px solid #c8c4b8; background: #fff; cursor: zoom-in; }}
    .dataStack {{ display: grid; gap: 16px; max-width: 1480px; }}
    .dataBand {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    .dataBandHead {{ display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; padding: 14px 16px; border-bottom: 1px solid var(--line); background: #fbfaf7; }}
    .dataBandHead > div {{ flex: 1; min-width: 0; }}
    .dataBandHead .pill {{ max-width: min(460px, 42vw); overflow: hidden; text-overflow: ellipsis; }}
    .dataBandHead h3 {{ margin: 0; font-size: 16px; }}
    .dataBandHead p {{ margin: 4px 0 0; color: var(--muted); font-size: 12px; line-height: 1.45; }}
    .dataBandSubhead {{ padding: 14px 16px 0; border-top: 1px solid #e6e0d7; }}
    .dataBandSubhead h4 {{ margin: 0; font-size: 13px; }}
    .dataBandSubhead p {{ margin: 4px 0 0; color: var(--muted); font-size: 12px; line-height: 1.45; }}
    .dataGrid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; padding: 14px; }}
    .dataCard {{ border: 1px solid #d8d5ce; border-radius: 8px; background: #fff; padding: 12px; display: grid; gap: 9px; align-content: start; min-width: 0; }}
    .dataCard h4 {{ margin: 0; font-size: 14px; line-height: 1.25; overflow-wrap: anywhere; }}
    .dataCard p {{ margin: 0; color: var(--muted); font-size: 12px; line-height: 1.45; overflow-wrap: anywhere; }}
    .dataCard a {{ color: var(--blue); text-decoration: none; overflow-wrap: anywhere; }}
    .dataCard a:hover {{ text-decoration: underline; }}
    .expandedGrid {{ grid-template-columns: repeat(auto-fit, minmax(440px, 1fr)); }}
    .run261Contract {{ gap: 12px; }}
    .contractHeader {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; border-bottom: 1px solid #e8e4dc; padding-bottom: 8px; }}
    .contractHeader h4 {{ font-size: 15px; }}
    .contractHeader .roleTag {{ flex: 0 0 auto; border: 1px solid #ddd6ca; border-radius: 999px; padding: 4px 8px; background: #f7f4ec; color: var(--muted); font-size: 10px; font-weight: 800; text-transform: uppercase; }}
    .contractRoute {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; }}
    .routeStep {{ border: 1px solid #e0d9cf; border-radius: 7px; padding: 8px; background: #fbfaf7; }}
    .routeStep b {{ display: block; margin-bottom: 3px; font-size: 11px; }}
    .routeStep span {{ display: block; color: var(--muted); font-size: 11px; line-height: 1.35; overflow-wrap: anywhere; }}
    .socketPlan {{ margin: 0; padding: 0; list-style: none; display: grid; gap: 6px; }}
    .socketPlan li {{ border: 1px solid #e0d9cf; border-radius: 7px; padding: 7px; background: #fffdf8; color: var(--muted); font-size: 11px; line-height: 1.35; overflow-wrap: anywhere; }}
    .socketPlan strong {{ color: var(--ink); }}
    .traceGate {{ border-left: 3px solid var(--accent); padding-left: 9px; }}
    .dataLabel {{ color: var(--muted); font-size: 10px; font-weight: 800; letter-spacing: 0; text-transform: uppercase; }}
    .chipRow {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .chip {{ display: inline-flex; align-items: center; min-height: 22px; padding: 2px 7px; border: 1px solid #d8d5ce; border-radius: 999px; background: #f7f6f1; color: #343841; font-size: 11px; overflow-wrap: anywhere; }}
    .dataList {{ margin: 0; padding-left: 18px; color: var(--muted); font-size: 12px; line-height: 1.45; }}
    .dataPre {{ margin: 0; max-height: 420px; overflow: auto; white-space: pre-wrap; color: #2a2e35; font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; padding: 14px; }}
    .auditGrid {{ display: grid; grid-template-columns: minmax(320px, 0.8fr) minmax(560px, 1.4fr); gap: 16px; max-width: 1480px; }}
    .auditTable {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    .auditTable th, .auditTable td {{ border-top: 1px solid #ddd8cf; padding: 8px; text-align: left; vertical-align: top; }}
    .auditTable th {{ color: var(--muted); font-size: 10px; text-transform: uppercase; }}
    .statusPass {{ color: var(--green); font-weight: 800; }}
    .statusWeak {{ color: #a16600; font-weight: 800; }}
    .statusMissing, .statusBlocked {{ color: var(--accent); font-weight: 800; }}
    .empty {{ padding: 40px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; color: var(--muted); }}
    .modal {{ position: fixed; inset: 0; z-index: 20; display: none; align-items: center; justify-content: center; background: rgba(12, 14, 17, 0.86); padding: 22px; }}
    .modal.open {{ display: flex; }}
    .modalFrame {{ max-width: min(96vw, 1560px); max-height: 94vh; background: #111; border: 1px solid #3a3e46; border-radius: 10px; overflow: hidden; box-shadow: 0 18px 48px rgba(0,0,0,0.34); }}
    .modalBar {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; color: #fff; padding: 10px 12px; background: #15171c; }}
    .modalBar button {{ height: 30px; border: 1px solid #4b515a; background: #242832; color: #fff; border-radius: 6px; cursor: pointer; }}
    .modal img {{ display: block; max-width: 96vw; max-height: calc(94vh - 52px); width: auto; height: auto; background: #fff; }}
    @media (max-width: 900px) {{
      body {{ overflow: auto; }}
      .app {{ height: auto; min-height: 100vh; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .statusbar {{ justify-content: flex-start; }}
      .fourGrid {{ grid-template-columns: minmax(340px, 1fr); min-width: 0; }}
      .seriesGrid {{ min-width: 0; flex-direction: column; }}
      .seriesCard {{ width: 100%; }}
      .sheetPanel {{ min-width: 0; }}
      .auditGrid {{ grid-template-columns: minmax(0, 1fr); }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <header class="topbar">
      <div class="brand">
        <h1>PPT Run Viewer</h1>
        <div class="meta">latest {latest} / generated native PPT outputs</div>
      </div>
      <div class="statusbar">
        <span class="pill strong">internal demo</span>
        <span class="pill">public blocked</span>
        <span class="pill" id="runCount"></span>
      </div>
    </header>
    <nav class="toolbar">
      <div class="versionRail" id="versionRail"><span class="railLabel">Version</span></div>
      <div class="viewRail" id="viewRail">
        <span class="railLabel">View</span>
        <button class="seg active" data-view="four">Four arms</button>
        <button class="seg" data-view="series">Full series</button>
        <button class="seg" data-view="sheet">Sheets</button>
        <button class="seg" data-view="data">Data / Skill</button>
        <button class="seg" data-view="audit">Data/Workflow Audit</button>
      </div>
    </nav>
    <main class="content" id="content"></main>
  </div>
  <div class="modal" id="modal" aria-hidden="true">
    <div class="modalFrame">
      <div class="modalBar">
        <div id="modalTitle"></div>
        <button id="modalClose">Close</button>
      </div>
      <img id="modalImage" alt="">
    </div>
  </div>
  <script>
    const DATA = {payload};
    let selectedRunId = DATA.latestRunId;
    let selectedView = "four";

    const byId = (id) => document.getElementById(id);
    const content = byId("content");
    const versionRail = byId("versionRail");
    const modal = byId("modal");
    const modalImage = byId("modalImage");
    const modalTitle = byId("modalTitle");

    byId("runCount").textContent = `${{DATA.runs.length}} versions`;

    function activeRun() {{
      return DATA.runs.find((run) => run.id === selectedRunId) || DATA.runs[DATA.runs.length - 1];
    }}

    function button(label, className, attrs = "") {{
      return `<button class="${{className}}" ${{attrs}}>${{label}}</button>`;
    }}

    function safe(value) {{
      return value === undefined || value === null ? "" : String(value);
    }}

    function escapeHtml(value) {{
      const map = {{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      }};
      return safe(value).replace(/[&<>"']/g, (char) => map[char]);
    }}

    function safeHref(value) {{
      const url = safe(value).trim();
      return /^https?:\\/\\//i.test(url) ? url : "";
    }}

    function chipList(items) {{
      const values = Array.isArray(items) ? items : [];
      if (!values.length) return "";
      return `<div class="chipRow">${{values.map((item) => `<span class="chip">${{escapeHtml(item)}}</span>`).join("")}}</div>`;
    }}

    function listBlock(items) {{
      const values = Array.isArray(items) ? items : [];
      if (!values.length) return "";
      return `<ul class="dataList">${{values.map((item) => `<li>${{escapeHtml(item)}}</li>`).join("")}}</ul>`;
    }}

    function detailBlock(label, value) {{
      if (value === undefined || value === null || value === "") return "";
      if (Array.isArray(value) && !value.length) return "";
      if (typeof value === "object" && !Array.isArray(value)) {{
        return `<div><div class="dataLabel">${{escapeHtml(label)}}</div><pre class="dataPre">${{escapeHtml(JSON.stringify(value, null, 2))}}</pre></div>`;
      }}
      if (Array.isArray(value)) {{
        return `<div><div class="dataLabel">${{escapeHtml(label)}}</div>${{listBlock(value)}}</div>`;
      }}
      return `<div><div class="dataLabel">${{escapeHtml(label)}}</div><p>${{escapeHtml(value)}}</p></div>`;
    }}

    function slideTile(src, title, index) {{
      return `<button class="slideTile" data-src="${{src}}" data-title="${{title}} / slide ${{index + 1}}">
        <img src="${{src}}" loading="lazy" alt="${{title}} slide ${{index + 1}}">
        <span class="slideNo">S${{String(index + 1).padStart(2, "0")}}</span>
      </button>`;
    }}

    function renderVersionRail() {{
      const buttons = DATA.runs.map((run) => {{
        const active = run.id === selectedRunId ? " active" : "";
        return `<button class="seg${{active}}" data-run="${{run.id}}">${{run.label}}</button>`;
      }}).join("");
      versionRail.innerHTML = `<span class="railLabel">Version</span>${{buttons}}`;
    }}

    function renderFour() {{
      const run = activeRun();
      if (!run) {{
        content.innerHTML = `<div class="empty">No generated runs found.</div>`;
        return;
      }}
      const arms = run.arms.map((arm) => {{
        const slides = arm.slides.map((src, index) => slideTile(src, `${{run.label}} / ${{arm.label}}`, index)).join("");
        const contact = arm.contactSheet
          ? `<button data-src="${{arm.contactSheet}}" data-title="${{run.label}} / ${{arm.label}} contact sheet">Contact sheet</button>`
          : "";
        return `<section class="armCard">
          <div class="armHead"><h3>${{arm.label}}</h3><span class="tag">${{arm.role}}</span></div>
          <div class="slidesGrid">${{slides}}</div>
          <div class="contactRow">${{contact}}</div>
        </section>`;
      }}).join("");
      content.innerHTML = `<div class="sectionHeader">
        <div><h2>${{run.label}} four-arm comparison</h2><div class="summary">${{run.arms.length}} arms / six editable native-PPT slide previews per arm</div></div>
        <span class="pill">${{DATA.status}}</span>
      </div><div class="fourGrid">${{arms}}</div>`;
    }}

    function renderSeries() {{
      const cards = DATA.runs.map((run) => {{
        const arm = run.fullArm;
        const slides = arm.slides.map((src, index) => slideTile(src, `${{run.label}} / ${{arm.label}}`, index)).join("");
        return `<section class="seriesCard">
          <div class="seriesHead"><h3>${{run.label}}</h3><span class="tag">${{arm.id}}</span></div>
          <div class="slidesGrid">${{slides}}</div>
        </section>`;
      }}).join("");
      content.innerHTML = `<div class="sectionHeader">
        <div><h2>Full skill series</h2><div class="summary">Run 2.0 through latest full arm, kept as individual slide previews</div></div>
        <span class="pill">${{DATA.runs.length}} versions</span>
      </div><div class="seriesGrid">${{cards}}</div>`;
    }}

    function renderSheets() {{
      const run = activeRun();
      const four = run?.fourArmSheet
        ? `<section class="sheetPanel"><img src="${{run.fourArmSheet}}" data-src="${{run.fourArmSheet}}" data-title="${{run.label}} four-arm sheet" alt="${{run.label}} four-arm sheet"></section>`
        : `<div class="empty">No four-arm sheet for ${{run?.label || "selected run"}}.</div>`;
      const seriesSheet = "run2-full-skill-series-horizontal.png";
      content.innerHTML = `<div class="sectionHeader">
        <div><h2>Comparison sheets</h2><div class="summary">${{run.label}} four-arm sheet plus the current full-series sheet</div></div>
      </div>
      <div style="display:grid; gap:16px;">
        ${{four}}
        <section class="sheetPanel"><img src="${{seriesSheet}}" data-src="${{seriesSheet}}" data-title="Full skill series sheet" alt="Full skill series sheet"></section>
      </div>`;
    }}

    function sourceCard(source) {{
      const href = safeHref(source.url);
      const url = href
        ? `<a href="${{escapeHtml(href)}}" target="_blank" rel="noreferrer">${{escapeHtml(source.url)}}</a>`
        : detailBlock("URL", source.url);
      return `<article class="dataCard">
        <h4>${{escapeHtml(source.title || source.id)}}</h4>
        ${{chipList([source.role, source.allowed_use].filter(Boolean))}}
        <p><strong>${{escapeHtml(source.id)}}</strong></p>
        ${{url}}
        ${{detailBlock("Accessed", source.accessed_on)}}
      </article>`;
    }}

    function sourceRecordCard(record) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(record.id)}}</h4>
        ${{chipList(record.modalities)}}
        ${{detailBlock("Source", record.source_id)}}
        ${{detailBlock("Observation", record.visual_observation)}}
        ${{detailBlock("Derived rule", record.extracted_design_rule)}}
        ${{detailBlock("Native implication", record.native_ppt_implication)}}
      </article>`;
    }}

    function decompositionCard(unit) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(unit.id)}}</h4>
        ${{chipList(unit.modality_mix)}}
        ${{detailBlock("Source ids", unit.source_ids)}}
        ${{detailBlock("Tutorial method", unit.tutorial_anchor)}}
        ${{detailBlock("Observed move", unit.observed_design_move)}}
        ${{detailBlock("Derived rule", unit.derived_rule)}}
        ${{detailBlock("Code binding", unit.code_generation_binding)}}
        ${{detailBlock("Native obligation", unit.native_ppt_obligation)}}
        ${{detailBlock("Failure probe", unit.failure_probe)}}
      </article>`;
    }}

    function bindingCard(binding) {{
      const code = binding.code_binding || {{}};
      return `<article class="dataCard">
        <h4>${{escapeHtml(binding.id)}}</h4>
        ${{chipList(binding.applies_to_slide_roles)}}
        ${{detailBlock("Function", code.function_name)}}
        ${{detailBlock("Params", code.params)}}
        ${{detailBlock("Composition constraints", binding.composition_constraints)}}
        ${{detailBlock("Typography constraints", binding.typography_constraints)}}
        ${{detailBlock("Spacing constraints", binding.spacing_constraints)}}
        ${{detailBlock("Negative-control failure", binding.negative_control_failure)}}
      </article>`;
    }}

    function gateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.id)}}</h4>
        ${{chipList([gate.slide_role])}}
        ${{detailBlock("Required code bindings", gate.required_code_bindings)}}
        ${{detailBlock("Layout budget", gate.layout_budget)}}
        ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
        ${{detailBlock("Trace fields", gate.trace_fields)}}
      </article>`;
    }}

    function run29PrimitiveCard(primitive) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(primitive.id)}}</h4>
        ${{chipList(primitive.target_slide_roles)}}
        ${{detailBlock("Source ids", primitive.source_ids)}}
        ${{detailBlock("Visual problem", primitive.visual_problem)}}
        ${{detailBlock("Reference method", primitive.reference_method)}}
        ${{detailBlock("Visual primitive", primitive.extracted_visual_primitive)}}
        ${{detailBlock("Native PPT translation", primitive.native_ppt_translation)}}
        ${{detailBlock("Code obligation", primitive.code_module_obligation)}}
        ${{detailBlock("Forbidden box patterns", primitive.forbidden_box_patterns)}}
        ${{detailBlock("Boxiness probe", primitive.boxiness_failure_probe)}}
      </article>`;
    }}

    function run29ModuleCard(module) {{
      const code = module.code_binding || {{}};
      return `<article class="dataCard">
        <h4>${{escapeHtml(module.id)}}</h4>
        ${{chipList(module.applies_to_slide_roles)}}
        ${{detailBlock("Function", code.function_name)}}
        ${{detailBlock("Params", code.params)}}
        ${{detailBlock("Composition contract", module.composition_contract)}}
        ${{detailBlock("Native primitives", module.native_ppt_primitives)}}
        ${{detailBlock("Negative control", module.negative_control_failure)}}
        ${{detailBlock("QA probe", module.qa_probe)}}
      </article>`;
    }}

    function run29VisualGateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.id)}}</h4>
        ${{chipList([gate.slide_role])}}
        ${{detailBlock("Visual primitive ids", gate.visual_primitive_ids)}}
        ${{detailBlock("Visual module ids", gate.visual_module_ids)}}
        ${{detailBlock("Required code modules", gate.required_code_modules)}}
        ${{detailBlock("Boxiness probe", gate.boxiness_failure_probe)}}
        ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
        ${{detailBlock("Trace fields", gate.trace_fields)}}
      </article>`;
    }}

    function run210SourceCard(source) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(source.id)}}</h4>
        ${{chipList([source.visual_system_direction, source.reference_type].filter(Boolean))}}
        ${{detailBlock("Source ids", source.source_ids)}}
        ${{detailBlock("Typography", source.typography_observation)}}
        ${{detailBlock("Composition", source.spatial_composition_observation)}}
        ${{detailBlock("Asset strategy", source.asset_strategy_observation)}}
        ${{detailBlock("Sequence", source.motion_or_sequence_observation)}}
        ${{detailBlock("Native implication", source.native_ppt_implication)}}
        ${{detailBlock("Probe", source.public_demo_probe)}}
      </article>`;
    }}

    function run210VisualSystemCard(system) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(system.visual_system_id)}}</h4>
        ${{chipList(system.applicable_slide_roles)}}
        ${{detailBlock("Source records", system.source_record_ids)}}
        ${{detailBlock("Typography contract", system.typography_contract)}}
        ${{detailBlock("Composition contract", system.composition_contract)}}
        ${{detailBlock("Asset strategy", system.asset_strategy_contract)}}
        ${{detailBlock("Motion sequence", system.motion_sequence_contract)}}
        ${{detailBlock("Native module implications", system.native_ppt_module_implications)}}
        ${{detailBlock("Forbidden sameness", system.forbidden_sameness_patterns)}}
      </article>`;
    }}

    function run210VisualGateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.id)}}</h4>
        ${{chipList([gate.slide_role])}}
        ${{detailBlock("Visual system source ids", gate.visual_system_source_ids)}}
        ${{detailBlock("Visual system memory ids", gate.visual_system_memory_ids)}}
        ${{detailBlock("Required code modules", gate.required_code_modules)}}
        ${{detailBlock("Delta from 2.9", gate.visual_delta_from_run2_9)}}
        ${{detailBlock("Sameness probe", gate.sameness_failure_probe)}}
        ${{detailBlock("Shape budget", gate.shape_count_budget)}}
        ${{detailBlock("Asymmetry and whitespace", gate.asymmetry_whitespace_rule)}}
        ${{detailBlock("Trace fields", gate.trace_fields)}}
      </article>`;
    }}

    function run212EvidenceCard(record) {{
      const urls = (record.source_urls || []).map((item) => item.url).filter(Boolean);
      return `<article class="dataCard">
        <h4>${{escapeHtml(record.id)}}</h4>
        ${{chipList(record.modality_mix)}}
        ${{detailBlock("Source role", record.source_role)}}
        ${{detailBlock("Source ids", record.source_ids)}}
        ${{detailBlock("Source URLs", urls)}}
        ${{detailBlock("Segment locator", record.segment_locator)}}
        ${{detailBlock("Derived design method", record.derived_design_method)}}
        ${{detailBlock("Native PPT obligations", record.native_ppt_code_obligations)}}
        ${{detailBlock("Workflow gate obligations", record.workflow_gate_obligations)}}
        ${{detailBlock("Memory targets", record.memory_seed_targets)}}
        ${{detailBlock("Anti-copy boundary", record.anti_copy_boundary)}}
      </article>`;
    }}

    function run212MemorySeedCard(seed) {{
      const contract = seed.native_ppt_contract || {{}};
      return `<article class="dataCard">
        <h4>${{escapeHtml(seed.id)}}</h4>
        ${{chipList(seed.applies_to_slide_roles)}}
        ${{detailBlock("Evidence records", seed.evidence_record_ids)}}
        ${{detailBlock("Memory type", seed.memory_type)}}
        ${{detailBlock("Design constraints", seed.design_constraints)}}
        ${{detailBlock("Code binding hint", contract.code_binding_hint)}}
        ${{detailBlock("Required before render", contract.required_before_render)}}
        ${{detailBlock("Required trace fields", seed.required_trace_fields)}}
        ${{detailBlock("Failure probe", seed.failure_probe)}}
      </article>`;
    }}

    function run212WorkflowGateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.id)}}</h4>
        ${{chipList([gate.gate_type, gate.required_before_next_rerun ? "required before rerun" : ""].filter(Boolean))}}
        ${{detailBlock("Slide roles", gate.slide_roles)}}
        ${{detailBlock("Evidence records", gate.evidence_record_ids)}}
        ${{detailBlock("Memory seeds", gate.memory_seed_ids)}}
        ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
        ${{detailBlock("Trace fields", gate.trace_fields)}}
        ${{detailBlock("Release boundary", gate.release_boundary)}}
      </article>`;
    }}

    function run215SelectorSourceCard(record) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(record.record_id)}}</h4>
        ${{chipList([record.source_family, ...(record.derived_from_run_ids || [])])}}
        ${{detailBlock("Commercial need", record.commercial_need)}}
        ${{detailBlock("Design observation", record.design_observation)}}
        ${{detailBlock("Selector obligation", record.layout_selector_obligation)}}
        ${{detailBlock("Typography", record.typography_obligation)}}
        ${{detailBlock("Spacing", record.spacing_obligation)}}
        ${{detailBlock("Product theater", record.product_theater_obligation)}}
        ${{detailBlock("Trace visibility", record.trace_visibility_obligation)}}
        ${{detailBlock("Anti-copy boundary", record.anti_copy_boundary)}}
      </article>`;
    }}

    function run215SelectorModuleCard(module) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(module.module_id)}}</h4>
        ${{chipList([module.module_family, ...(module.slide_roles || [])])}}
        ${{detailBlock("Source records", module.source_record_ids)}}
        ${{detailBlock("Selection trigger", module.selection_trigger)}}
        ${{detailBlock("Composition", module.composition_contract)}}
        ${{detailBlock("Typography", module.typography_contract)}}
        ${{detailBlock("Spacing", module.spacing_contract)}}
        ${{detailBlock("Trace visibility", module.trace_visibility_contract)}}
        ${{detailBlock("Fallback", module.fallback_contract)}}
        ${{detailBlock("Native obligations", module.native_ppt_obligations)}}
        ${{detailBlock("Forbidden patterns", module.forbidden_patterns)}}
      </article>`;
    }}

    function run215SelectorGateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.gate_id)}}</h4>
        ${{chipList([gate.slide_role])}}
        ${{detailBlock("Candidate modules", gate.candidate_module_ids)}}
        ${{detailBlock("Required inputs", gate.required_selector_inputs)}}
        ${{detailBlock("Selection rules", gate.selection_rules)}}
        ${{detailBlock("Rejection rules", gate.rejection_rules)}}
        ${{detailBlock("Trace fields", gate.trace_fields)}}
        ${{detailBlock("Layout budget", gate.layout_budget)}}
        ${{detailBlock("Text resilience probe", gate.text_resilience_probe)}}
        ${{detailBlock("Product surface probe", gate.product_surface_probe)}}
        ${{detailBlock("Bad control probe", gate.bad_control_probe)}}
      </article>`;
    }}

    function run218EvidenceCard(record) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(record.record_id)}}</h4>
        ${{chipList([record.source_family, ...(record.modality_mix || [])])}}
        ${{detailBlock("Commercial usecases", record.commercial_usecase_ids)}}
        ${{detailBlock("Source ids", record.source_ids)}}
        ${{detailBlock("Source locator", record.source_locator)}}
        ${{detailBlock("Observed method", record.observed_design_method)}}
        ${{detailBlock("Business requirement", record.business_requirement)}}
        ${{detailBlock("Generation constraint", record.derived_generation_constraint)}}
        ${{detailBlock("Memory targets", record.memory_targets)}}
        ${{detailBlock("Workflow targets", record.workflow_gate_targets)}}
        ${{detailBlock("Bad control probe", record.bad_control_probe)}}
        ${{detailBlock("Anti-copy boundary", record.anti_copy_boundary)}}
      </article>`;
    }}

    function run218MemoryCard(memory) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(memory.memory_id)}}</h4>
        ${{chipList([memory.memory_family, ...(memory.slide_roles || [])])}}
        ${{detailBlock("Evidence records", memory.evidence_record_ids)}}
        ${{detailBlock("Composition", memory.composition_contract)}}
        ${{detailBlock("Typography", memory.typography_contract)}}
        ${{detailBlock("Spacing", memory.spacing_contract)}}
        ${{detailBlock("Motion/sequence", memory.motion_or_sequence_contract)}}
        ${{detailBlock("Proof object", memory.proof_object_contract)}}
        ${{detailBlock("Code binding", memory.code_generation_binding)}}
        ${{detailBlock("Trace fields", memory.trace_fields_required)}}
        ${{detailBlock("Negative control", memory.negative_control_failure)}}
      </article>`;
    }}

    function run218GateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.gate_id)}}</h4>
        ${{chipList([gate.required_before_next_rerun ? "required before rerun" : "optional"])}}
        ${{detailBlock("Evidence records", gate.evidence_record_ids)}}
        ${{detailBlock("Memory ids", gate.memory_ids)}}
        ${{detailBlock("Selection rules", gate.selection_rules)}}
        ${{detailBlock("Rejection rules", gate.rejection_rules)}}
        ${{detailBlock("Trace fields", gate.trace_fields)}}
        ${{detailBlock("QA probe", gate.qa_probe)}}
        ${{detailBlock("Bad control probe", gate.bad_control_probe)}}
        ${{detailBlock("Release boundary", gate.release_boundary)}}
      </article>`;
    }}

    function run221DecisionMemoryCard(record) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(record.decision_id)}}</h4>
        ${{chipList([record.role, record.primary_evidence_id].filter(Boolean))}}
        ${{detailBlock("Secondary evidence", record.secondary_evidence_ids)}}
        ${{detailBlock("Selected memory", record.selected_memory_ids)}}
        ${{detailBlock("Selected gates", record.selected_gate_ids)}}
        ${{detailBlock("Typography decision", record.typography_decision)}}
        ${{detailBlock("Spacing decision", record.spacing_decision)}}
        ${{detailBlock("Composition decision", record.composition_decision)}}
        ${{detailBlock("Proof object", record.proof_object_decision)}}
        ${{detailBlock("Code obligation", record.code_generation_obligation)}}
        ${{detailBlock("Risk", record.visual_quality_risk)}}
      </article>`;
    }}

    function run221SelectorGateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.gate_id)}}</h4>
        ${{chipList([gate.role, gate.required_visual_decision_memory_id].filter(Boolean))}}
        ${{detailBlock("Primary evidence count", gate.required_primary_evidence_count)}}
        ${{detailBlock("Max secondary evidence", gate.max_secondary_evidence_count)}}
        ${{detailBlock("Required code modules", gate.required_code_module_ids)}}
        ${{detailBlock("Trace fields", gate.required_trace_fields)}}
        ${{detailBlock("Public surface", gate.public_surface_policy)}}
        ${{detailBlock("Pass/fail", gate.pass_fail_checks)}}
        ${{detailBlock("Release boundary", gate.release_boundary)}}
      </article>`;
    }}

    function run221RejectionRecordCard(record) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}}</h4>
        ${{chipList([record.visual_decision_memory_id, record.primary_evidence_id].filter(Boolean))}}
        ${{detailBlock("Secondary evidence", record.secondary_evidence_ids)}}
        ${{detailBlock("Rejected evidence", (record.rejected_evidence || []).map((item) => `${{item.evidence_id}}: ${{item.reason}}`))}}
        ${{detailBlock("All evidence accounted for", record.all_evidence_accounted_for)}}
      </article>`;
    }}

    function run224ContentMemoryCard(record) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(record.content_memory_id)}}</h4>
        ${{chipList([record.role, record.selected_usecase_id].filter(Boolean))}}
        ${{detailBlock("Headline", record.headline)}}
        ${{detailBlock("Support line", record.support_line)}}
        ${{detailBlock("Business proof points", record.business_proof_points)}}
        ${{detailBlock("Visual evidence slots", record.visual_evidence_slot_ids)}}
        ${{detailBlock("Density contract", record.content_density_contract)}}
        ${{detailBlock("Trace fields", record.trace_fields_required)}}
        ${{detailBlock("Forbidden materials", record.forbidden_source_materials)}}
      </article>`;
    }}

    function run224VisualAssetCard(asset) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(asset.asset_id)}}</h4>
        ${{chipList([asset.role, asset.asset_type].filter(Boolean))}}
        ${{detailBlock("Content payload", asset.content_payload)}}
        ${{detailBlock("Native PPT strategy", asset.native_ppt_strategy)}}
        ${{detailBlock("Visual density role", asset.visual_density_role)}}
        ${{detailBlock("Source boundary", asset.source_boundary)}}
        ${{detailBlock("QA probe", asset.qa_probe)}}
      </article>`;
    }}

    function run224WorkflowGateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.gate_id)}}</h4>
        ${{chipList([gate.role, gate.selected_usecase_id, gate.public_release_gate].filter(Boolean))}}
        ${{detailBlock("Content memory", gate.required_content_memory_id)}}
        ${{detailBlock("Min business proof points", gate.min_business_proof_points)}}
        ${{detailBlock("Min visual evidence slots", gate.min_visual_evidence_slots)}}
        ${{detailBlock("Forbid cross-case story", gate.forbid_cross_case_primary_story)}}
        ${{detailBlock("Trace fields", gate.required_trace_fields)}}
        ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
        ${{detailBlock("Bad control probe", gate.bad_control_probe)}}
      </article>`;
    }}

    function run235RealismMemoryCard(record) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(record.realism_memory_id)}}</h4>
        ${{chipList([record.role, record.selected_usecase_id].filter(Boolean))}}
        ${{detailBlock("Product evidence object", record.usecase_specific_visual_evidence_object)}}
        ${{detailBlock("Observable product state", record.observable_product_state)}}
        ${{detailBlock("Business caption", record.business_context_caption)}}
        ${{detailBlock("Audience question", record.audience_question_answered)}}
        ${{detailBlock("Native PPT realism strategy", record.native_ppt_realism_strategy)}}
        ${{detailBlock("Anti-schematic constraints", record.anti_schematic_constraints)}}
        ${{detailBlock("Source boundary", record.source_boundary)}}
      </article>`;
    }}

    function run235CompositionMemoryCard(record) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(record.composition_memory_id)}}</h4>
        ${{chipList([record.role, record.repairs_run2_34_weak_editorial_anchor ? "repairs weak anchor" : "preserves anchor"].filter(Boolean))}}
        ${{detailBlock("Editorial anchor object", record.editorial_anchor_object)}}
        ${{detailBlock("Hero canvas share target", record.hero_canvas_share_target)}}
        ${{detailBlock("Composition obligations", record.composition_obligations)}}
        ${{detailBlock("Typography obligations", record.typography_obligations)}}
        ${{detailBlock("Spacing obligations", record.spacing_obligations)}}
        ${{detailBlock("Forbidden patterns", record.forbidden_patterns)}}
        ${{detailBlock("QA probe", record.qa_probe)}}
      </article>`;
    }}

    function run235WorkflowGateCard(gate) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(gate.gate_id)}}</h4>
        ${{chipList([gate.role, gate.next_rerun_contract, gate.public_release_gate].filter(Boolean))}}
        ${{detailBlock("Required realism memory", gate.required_realism_memory_ids)}}
        ${{detailBlock("Required composition memory", gate.required_editorial_composition_memory_id)}}
        ${{detailBlock("Min realistic visual evidence objects", gate.min_realistic_visual_evidence_objects)}}
        ${{detailBlock("Forbid generic block diagrams", gate.forbid_generic_block_diagrams)}}
        ${{detailBlock("Trace fields", gate.required_trace_fields)}}
        ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
        ${{detailBlock("Bad control probe", gate.bad_control_probe)}}
      </article>`;
    }}

    function run217ArmAuditCard(arm) {{
      const motion = arm.motion || {{}};
      return `<article class="dataCard">
        <h4>${{escapeHtml(arm.arm_id || arm.slug)}}</h4>
        ${{chipList([arm.delivery_gate, arm.keynote_readout].filter(Boolean))}}
        ${{detailBlock("PPTX", arm.pptx_path)}}
        ${{detailBlock("Slides", arm.slide_count)}}
        ${{detailBlock("Media entries", arm.media_entry_count)}}
        ${{detailBlock("Motion XML present", motion.has_motion_xml)}}
        ${{detailBlock("Slides with motion XML", motion.slides_with_motion_xml)}}
        ${{detailBlock("Transition tags", motion.transition_tags)}}
        ${{detailBlock("Timing tags", motion.timing_tags)}}
        ${{detailBlock("Animation tags", motion.animation_tags)}}
        ${{detailBlock("Keynote readout", arm.keynote_readout)}}
      </article>`;
    }}

    function run217ProofSceneCard(scene) {{
      return `<article class="dataCard">
        <h4>${{escapeHtml(scene.scene_id)}}</h4>
        ${{chipList([scene.role, scene.public_release_gate].filter(Boolean))}}
        ${{detailBlock("Source motion contracts", scene.source_motion_contract_ids)}}
        ${{detailBlock("Animation steps", scene.animation_steps)}}
        ${{detailBlock("Reduced motion fallback", scene.reduced_motion_fallback)}}
      </article>`;
    }}

    function stageCard(stage) {{
      return `<article class="dataCard">
        <h4>${{String(stage.order || "").padStart(2, "0")}} / ${{escapeHtml(stage.id)}}</h4>
        ${{detailBlock("Inputs", stage.inputs || stage.input_files || stage.input_ids)}}
        ${{detailBlock("Outputs", stage.outputs || stage.output_files || stage.output_ids)}}
        ${{detailBlock("Gate", stage.pass_fail_gate || stage.gate || stage.qa_gate)}}
        ${{detailBlock("Repair", stage.repair_recommendation)}}
      </article>`;
    }}

    function auditStatusClass(status) {{
      const value = safe(status).toLowerCase();
      if (value.includes("pass")) return "statusPass";
      if (value.includes("weak")) return "statusWeak";
      if (value.includes("missing")) return "statusMissing";
      if (value.includes("blocked")) return "statusBlocked";
      return "";
    }}

    function auditInventoryCard(title, value, note) {{
      const rows = value && typeof value === "object" && !Array.isArray(value)
        ? Object.entries(value).map(([key, count]) => `<p><strong>${{escapeHtml(key)}}</strong>: ${{escapeHtml(count)}}</p>`).join("")
        : `<p>${{escapeHtml(value || "No inventory recorded.")}}</p>`;
      return `<article class="dataCard">
        <h4>${{escapeHtml(title)}}</h4>
        ${{rows}}
        ${{note ? `<p>${{escapeHtml(note)}}</p>` : ""}}
      </article>`;
    }}

    function renderAudit() {{
      const refs = DATA.references || {{}};
      const audit = (refs.run223SelectorAudit && refs.run223SelectorAudit.status)
        ? refs.run223SelectorAudit
        : (refs.run220TraceAudit && refs.run220TraceAudit.status)
          ? refs.run220TraceAudit
          : (refs.run211Audit || {{}});
      if (!audit.status) {{
        content.innerHTML = `<div class="empty">No Data/Workflow Audit is embedded in this viewer.</div>`;
        return;
      }}
      const roleTraceRecords = (((audit.trace_effectiveness || {{}}).full_arm || {{}}).role_records || []).map((role) => ({{
        chain_id: `${{role.role}}_run2_20_trace_effectiveness`,
        run_id: "2.20",
        slide_roles: [role.role],
        required_code_module_ids: role.code_module_ids || [],
        actual_code_module_ids: role.code_module_ids || [],
        status: role.layout_budget_passed ? "pass" : "blocked",
        reason: `evidence=${{role.evidence_count}}, memory=${{role.memory_count}}, gates=${{role.workflow_gate_count}}; ${{role.visual_delta_from_run2_16 || "no visual delta recorded"}}`,
        next_fix: role.layout_budget_passed ? "thicken_visual_decision_memory" : "repair_layout_budget",
      }}));
      const chains = (audit.chain_records && audit.chain_records.length) ? audit.chain_records : roleTraceRecords;
      const sourceInventory = audit.source_inventory || ((audit.trace_effectiveness || {{}}).inventory || {{}});
      const workflowInventory = audit.workflow_inventory || (((audit.trace_effectiveness || {{}}).full_arm || {{}}));
      const auditTitle = audit.run_id === "2.23"
        ? "Run 2.23 selector effectiveness audit (audit-only layer)"
        : audit.run_id === "2.20"
          ? "Run 2.20 trace effectiveness audit (audit-only layer)"
          : "Data/Workflow Audit";
      const chainRows = (chains || []).map((chain) => `<tr>
        <td>${{escapeHtml(chain.chain_id)}}</td>
        <td>${{escapeHtml(chain.run_id)}}</td>
        <td>${{chipList(chain.slide_roles)}}</td>
        <td>${{listBlock(chain.required_code_module_ids)}}</td>
        <td>${{listBlock(chain.actual_code_module_ids)}}</td>
        <td><span class="${{auditStatusClass(chain.status)}}">${{escapeHtml(chain.status)}}</span>${{detailBlock("Reason", chain.reason)}}</td>
        <td>${{escapeHtml(chain.next_fix)}}</td>
      </tr>`).join("");
      const controlChecks = (audit.negative_control_checks && audit.negative_control_checks.length)
        ? audit.negative_control_checks
        : Object.entries(audit.control_boundary || {{}}).map(([arm, boundary]) => ({{
            arm_role: arm,
            forbidden_fields: [
              boundary.forbids_run2_18_thickness_pack ? "run2_18_thickness_pack" : "",
              boundary.uses_evidence_only ? "run2_18_design_memory_and_workflow_gates" : "",
            ].filter(Boolean),
            observed_boundary: JSON.stringify(boundary),
            status: boundary.uses_evidence_only || boundary.forbids_run2_18_thickness_pack ? "pass" : "weak",
          }}));
      const controlRows = (controlChecks || []).map((check) => `<tr>
        <td>${{escapeHtml(check.arm_role)}}</td>
        <td>${{listBlock(check.forbidden_fields)}}</td>
        <td>${{escapeHtml(check.observed_boundary)}}</td>
        <td><span class="${{auditStatusClass(check.status)}}">${{escapeHtml(check.status)}}</span></td>
      </tr>`).join("");
      const gate = audit.gate_summary || {{}};
      const proven = gate.proven || gate.trace_grounded_pass_chains || gate.data_workflow_chain_gate || "";
      const weak = gate.weak || gate.weaknesses || gate.summary || "";
      const blocked = gate.blocked || gate.public_release_gate || "";
      content.innerHTML = `<div class="sectionHeader">
        <div><h2>${{auditTitle}}</h2><div class="summary">${{escapeHtml(audit.stage_policy || "same-stage audit")}}</div></div>
        <span class="pill ${{auditStatusClass(audit.status)}}">${{escapeHtml(audit.status)}}</span>
      </div>
      <div class="dataStack">
        <section class="auditGrid">
          <div class="dataBand">
            <div class="dataBandHead"><div><h3>Inventories</h3><p>Counts of source, memory, workflow, and gate material checked by the audit.</p></div></div>
            <div class="dataGrid">
              ${{auditInventoryCard("Source inventory", sourceInventory, "Data artifacts checked by this audit.")}}
              ${{auditInventoryCard("Workflow inventory", workflowInventory, "Trace, module, and gate material checked by this audit.")}}
            </div>
          </div>
          <div class="dataBand">
            <div class="dataBandHead"><div><h3>Gaps Before Next Rerun</h3><p>${{escapeHtml(gate.summary || "")}}</p></div></div>
            <div class="dataGrid">
              <article class="dataCard"><h4>Proven</h4><p>${{escapeHtml(proven || "No proven gate summary recorded.")}}</p></article>
              <article class="dataCard"><h4>Weak</h4><p>${{escapeHtml(weak || "No weak gate summary recorded.")}}</p></article>
              <article class="dataCard"><h4>Blocked</h4><p>${{escapeHtml(blocked || "No blocked gate summary recorded.")}}</p></article>
              <article class="dataCard"><h4>Next required action</h4><p>${{escapeHtml(audit.next_required_action || "No next action recorded.")}}</p></article>
            </div>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Source-to-slide chains</h3><p>Trace-grounded path from data records and gates to actual code module evidence.</p></div><span class="pill">${{(chains || []).length}} chains</span></div>
          <table class="auditTable">
            <thead><tr><th>Chain</th><th>Run</th><th>Slide roles</th><th>Required modules</th><th>Actual modules</th><th>Status / reason</th><th>Next fix</th></tr></thead>
            <tbody>${{chainRows}}</tbody>
          </table>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Control boundaries</h3><p>Negative-control checks that keep prompt-only and non-skill arms from claiming data or workflow evidence.</p></div><span class="pill">${{(audit.negative_control_checks || []).length}} checks</span></div>
          <table class="auditTable">
            <thead><tr><th>Arm</th><th>Forbidden fields</th><th>Observed boundary</th><th>Status</th></tr></thead>
            <tbody>${{controlRows}}</tbody>
          </table>
        </section>
      </div>`;
    }}

    function renderData() {{
      const refs = DATA.references || {{}};
      const diagnosis = (refs.diagnosis || []).map((item) => `<article class="dataCard"><h4>${{escapeHtml(item.label)}}</h4><p>${{escapeHtml(item.body)}}</p></article>`).join("");
      const sources = (refs.sources || []).map(sourceCard).join("");
      const records = (refs.sourceRecords || []).map(sourceRecordCard).join("");
      const units = (refs.decompositionUnits || []).map(decompositionCard).join("");
      const bindings = (refs.memoryBindings || []).map(bindingCard).join("");
      const gates = (refs.workflowGates || []).map(gateCard).join("");
      const run29Primitives = (refs.run29PrimitiveRepairs || []).map(run29PrimitiveCard).join("");
      const run29Modules = (refs.run29VisualModules || []).map(run29ModuleCard).join("");
      const run29Gates = (refs.run29VisualGates || []).map(run29VisualGateCard).join("");
      const run210Sources = (refs.run210VisualSystemSources || []).map(run210SourceCard).join("");
      const run210Systems = (refs.run210VisualSystems || []).map(run210VisualSystemCard).join("");
      const run210Gates = (refs.run210VisualGates || []).map(run210VisualGateCard).join("");
      const run212Evidence = (refs.run212ThickEvidenceRecords || []).map(run212EvidenceCard).join("");
      const run212MemorySeeds = (refs.run212MemorySeeds || []).map(run212MemorySeedCard).join("");
      const run212WorkflowGates = (refs.run212WorkflowGateSeeds || []).map(run212WorkflowGateCard).join("");
      const run215SelectorSources = (refs.run215SelectorSources || []).map(run215SelectorSourceCard).join("");
      const run215SelectorModules = (refs.run215SelectorModules || []).map(run215SelectorModuleCard).join("");
      const run215SelectorGates = (refs.run215SelectorGates || []).map(run215SelectorGateCard).join("");
      const run218Evidence = (refs.run218EvidenceRecords || []).map(run218EvidenceCard).join("");
      const run218Memory = (refs.run218MemoryExpansions || []).map(run218MemoryCard).join("");
      const run218Gates = (refs.run218WorkflowGates || []).map(run218GateCard).join("");
      const run218Result = refs.run218Result || {{}};
      const run219Result = refs.run219Result || {{}};
      const run219Rerun = run219Result.rerun || {{}};
      const run219Inputs = run219Result.input_chain || {{}};
      const run219Control = run219Result.control_boundary || {{}};
      const run221Result = refs.run221Result || {{}};
      const run221DecisionMemory = (refs.run221DecisionMemory || []).map(run221DecisionMemoryCard).join("");
      const run221SelectorGates = (refs.run221SelectorGates || []).map(run221SelectorGateCard).join("");
      const run221RejectionRecords = (refs.run221RejectionRecords || []).map(run221RejectionRecordCard).join("");
      const run222Result = refs.run222Result || {{}};
      const run222Rerun = run222Result.rerun || {{}};
      const run222Inputs = run222Result.input_chain || {{}};
      const run222Control = run222Result.control_boundary || {{}};
      const run224Result = refs.run224Result || {{}};
      const run224OutputChain = run224Result.output_chain || {{}};
      const run224SelectedUsecase = refs.run224SelectedUsecase || {{}};
      const run224StoryPolicy = refs.run224StoryPolicy || {{}};
      const run224ContentMemory = (refs.run224ContentMemory || []).map(run224ContentMemoryCard).join("");
      const run224VisualAssets = (refs.run224VisualAssets || []).map(run224VisualAssetCard).join("");
      const run224WorkflowGates = (refs.run224WorkflowGates || []).map(run224WorkflowGateCard).join("");
      const run225Result = refs.run225Result || {{}};
      const run225Rerun = run225Result.rerun || {{}};
      const run225Inputs = run225Result.input_chain || {{}};
      const run225Control = run225Result.control_boundary || {{}};
      const run226Audit = refs.run226VisualModuleAudit || {{}};
      const run226Summary = run226Audit.quality_summary || {{}};
      const run226NoNewDeckProof = run226Audit.no_new_deck_proof || {{}};
      const run226RoleRecords = (run226Audit.role_records || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}}</h4>
        ${{chipList([record.status, ...((record.issue_categories || []))].filter(Boolean))}}
        ${{detailBlock("Module ids", record.module_ids)}}
        ${{detailBlock("Geometry", record.geometry)}}
        ${{detailBlock("Content density", record.content_density)}}
        ${{detailBlock("Visual evidence visibility", record.visual_evidence_visibility)}}
        ${{detailBlock("Composition hierarchy", record.composition_hierarchy)}}
        ${{detailBlock("Recommended next action", record.recommended_next_action)}}
      </article>`).join("");
      const run226Recommendations = (run226Audit.module_recommendations || []).map((item) => `<article class="dataCard">
        <h4>${{escapeHtml(item.module_id)}}</h4>
        ${{detailBlock("Priority", item.priority)}}
        ${{detailBlock("Issue categories", item.issue_categories)}}
        ${{detailBlock("Why", item.why)}}
        ${{detailBlock("Next contract", item.next_contract)}}
      </article>`).join("");
      const run227Result = refs.run227Result || {{}};
      const run227Rerun = run227Result.rerun || {{}};
      const run227Inputs = run227Result.input_chain || {{}};
      const run227Delta = run227Result.quality_delta || {{}};
      const run227Control = run227Result.control_boundary || {{}};
      const run228EvidenceChain = refs.run228EvidenceChain || {{}};
      const run228Chains = run228EvidenceChain.slide_evidence_chains || [];
      const run228Result = refs.run228Result || {{}};
      const run228Rerun = run228Result.rerun || {{}};
      const run228Inputs = run228Result.input_chain || {{}};
      const run228Delta = run228Result.evidence_chain_delta || {{}};
      const run228Control = run228Result.control_boundary || {{}};
      const run228ChainCards = run228Chains.map((chain) => `<article class="dataCard">
        <h4>${{escapeHtml(chain.slide_index)}}. ${{escapeHtml(chain.role)}}</h4>
        ${{detailBlock("source evidence", chain.source_evidence_summary)}}
        ${{detailBlock("extracted design rule", chain.extracted_design_rule)}}
        ${{detailBlock("workflow decision", chain.workflow_decision)}}
        ${{detailBlock("generated slide surface", chain.generated_slide_surface)}}
        ${{detailBlock("native module", chain.native_surface_module_id)}}
      </article>`).join("");
      const run229SynthesisMemory = refs.run229SynthesisMemory || {{}};
      const run229Records = run229SynthesisMemory.slide_synthesis_records || [];
      const run229Result = refs.run229Result || {{}};
      const run229Rerun = run229Result.rerun || {{}};
      const run229Inputs = run229Result.input_chain || {{}};
      const run229Delta = run229Result.presentation_synthesis_delta || {{}};
      const run229Control = run229Result.control_boundary || {{}};
      const run229Policy = run229SynthesisMemory.surface_policy || {{}};
      const run229RecordCards = run229Records.map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / ${{escapeHtml(record.presentation_module_id)}}</h4>
        ${{detailBlock("Evidence chain id", record.evidence_chain_id)}}
        ${{detailBlock("Public surface mode", record.public_surface_mode)}}
        ${{detailBlock("Trace surface mode", record.trace_surface_mode || "manifest_and_html_viewer_full_chain_visible")}}
        ${{detailBlock("Primary contract", record.primary_slide_surface_contract)}}
        ${{detailBlock("Compressed evidence spine", record.visible_on_slide_evidence_spine_steps)}}
        ${{detailBlock("Chain compression policy", record.chain_compression_policy)}}
      </article>`).join("");
      const run230Audit = refs.run230Audit || {{}};
      const run230Summary = run230Audit.quality_summary || {{}};
      const run230Trace = run230Audit.trace_closure || {{}};
      const run230TraceFull = run230Trace.full_arm || {{}};
      const run230TraceBad = run230Trace.bad_control || {{}};
      const run230Comparison = run230Audit.comparison_to_run2_28 || {{}};
      const run230NoNewDeck = run230Audit.no_new_deck_proof || {{}};
      const run230RoleCards = (run230Audit.role_records || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / ${{escapeHtml(record.run2_29_presentation_module_id)}}</h4>
        ${{detailBlock("Run 2.28 source module", record.run2_28_native_surface_module_id)}}
        ${{detailBlock("Presentation-first surface", (record.presentation_first_surface || {{}}).status)}}
        ${{detailBlock("Compressed evidence spine called", (record.evidence_spine || {{}}).compressed_spine_module_called)}}
        ${{detailBlock("Min spine font size", (record.evidence_spine || {{}}).min_spine_font_size)}}
        ${{detailBlock("Run 2.28 chain preserved", (record.trace_closure || {{}}).run2_28_chain_preserved)}}
        ${{detailBlock("Issue categories", record.issue_categories)}}
        ${{detailBlock("Recommended next action", record.recommended_next_action)}}
      </article>`).join("");
      const run231Result = refs.run231Result || {{}};
      const run231Rerun = run231Result.rerun || {{}};
      const run231Inputs = run231Result.input_chain || {{}};
      const run231Delta = run231Result.quality_delta || {{}};
      const run231Control = run231Result.control_boundary || {{}};
      const run232Audit = refs.run232Audit || {{}};
      const run232Trace = run232Audit.trace_closure || {{}};
      const run232TraceFull = run232Trace.full_arm || {{}};
      const run232TraceBad = run232Trace.bad_control || {{}};
      const run232Repair = run232Audit.repair_verification || {{}};
      const run232Summary = run232Audit.quality_summary || {{}};
      const run232Inputs = run232Audit.input_chain || {{}};
      const run232RoleCards = (run232Audit.role_records || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / ${{escapeHtml(record.run2_31_presentation_module_id)}}</h4>
        ${{detailBlock("Run 2.30 audit status present", (record.repair_trace_closure || {{}}).run2_30_audit_status_present)}}
        ${{detailBlock("Spine module called", (record.spine_repair || {{}}).readable_spine_module_called)}}
        ${{detailBlock("Spine min target", (record.spine_repair || {{}}).spine_min_font_size_target)}}
        ${{detailBlock("Measured min spine", (record.spine_repair || {{}}).measured_min_spine_font_size)}}
        ${{detailBlock("Climax policy", (record.climax_repair || {{}}).climax_style_policy)}}
        ${{detailBlock("Visual evidence objects", (record.main_surface_density || {{}}).visual_evidence_objects)}}
        ${{detailBlock("Issue categories", record.issue_categories)}}
        ${{detailBlock("Recommended next action", record.recommended_next_action)}}
      </article>`).join("");
      const run233Result = refs.run233Result || {{}};
      const run233Rerun = run233Result.rerun || {{}};
      const run233Inputs = run233Result.input_chain || {{}};
      const run233Delta = run233Result.quality_delta || {{}};
      const run233Control = run233Result.control_boundary || {{}};
      const run234Audit = refs.run234Audit || {{}};
      const run234Inputs = run234Audit.input_chain || {{}};
      const run234Trace = run234Audit.trace_closure || {{}};
      const run234TraceFull = run234Trace.full_arm || {{}};
      const run234TraceBad = run234Trace.bad_control || {{}};
      const run234Verification = run234Audit.main_surface_verification || {{}};
      const run234Summary = run234Audit.quality_summary || {{}};
      const run234RoleCards = (run234Audit.role_records || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / ${{escapeHtml(record.run2_33_presentation_module_id)}}</h4>
        ${{detailBlock("Run 2.32 audit status present", (record.main_surface_trace_closure || {{}}).run2_32_audit_status_present)}}
        ${{detailBlock("Execution status present", (record.main_surface_trace_closure || {{}}).execution_status_present)}}
        ${{detailBlock("Main surface layer called", (record.main_surface_modules || {{}}).main_surface_evidence_layer_called)}}
        ${{detailBlock("Storyboard called", (record.main_surface_modules || {{}}).visual_evidence_storyboard_called)}}
        ${{detailBlock("Visual evidence objects", (record.main_surface_density || {{}}).visual_evidence_objects)}}
        ${{detailBlock("Schematic visual evidence", (record.visual_evidence_realism || {{}}).schematic_visual_evidence)}}
        ${{detailBlock("Hero object share", (record.editorial_composition || {{}}).hero_object_canvas_share)}}
        ${{detailBlock("Issue categories", record.issue_categories)}}
        ${{detailBlock("Recommended next action", record.recommended_next_action)}}
      </article>`).join("");
      const run235Result = refs.run235Result || {{}};
      const run235Inputs = run235Result.input_chain || {{}};
      const run235Output = run235Result.output_chain || {{}};
      const run235Quality = run235Result.quality_contract || {{}};
      const run235RealismMemory = (refs.run235RealismMemory || []).map(run235RealismMemoryCard).join("");
      const run235CompositionMemory = (refs.run235CompositionMemory || []).map(run235CompositionMemoryCard).join("");
      const run235WorkflowGates = (refs.run235WorkflowGates || []).map(run235WorkflowGateCard).join("");
      const run236Result = refs.run236Result || {{}};
      const run236Rerun = run236Result.rerun || {{}};
      const run236Inputs = run236Result.input_chain || {{}};
      const run236Delta = run236Result.quality_delta || {{}};
      const run236Control = run236Result.control_boundary || {{}};
      const run237Audit = refs.run237Audit || {{}};
      const run237Inputs = run237Audit.input_chain || {{}};
      const run237Trace = run237Audit.trace_closure || {{}};
      const run237TraceFull = run237Trace.full_arm || {{}};
      const run237TraceBad = run237Trace.bad_control || {{}};
      const run237Assessment = run237Audit.visual_quality_assessment || {{}};
      const run237Delivery = run237Audit.delivery_check || {{}};
      const run237RoleCards = (run237Audit.role_records || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / visual quality</h4>
        ${{detailBlock("Layout signature", record.layout_signature)}}
        ${{detailBlock("Run 2.36 data consumed", record.run2_36_data_consumed)}}
        ${{detailBlock("Workflow gate exposed", record.workflow_gate_exposed)}}
        ${{detailBlock("Public video grade", record.public_video_grade)}}
        ${{detailBlock("Hero object share", record.hero_object_canvas_share)}}
        ${{detailBlock("Visual evidence objects", record.realistic_visual_evidence_objects)}}
        ${{detailBlock("Failure reasons", record.aesthetic_failure_reasons)}}
        ${{detailBlock("Recommended next action", record.recommended_next_action)}}
      </article>`).join("");
      const run238Result = refs.run238Result || {{}};
      const run238Inputs = run238Result.input_chain || {{}};
      const run238Output = run238Result.output_chain || {{}};
      const run238Counts = run238Result.artifact_counts || {{}};
      const run238Contract = refs.run238WorkflowGateContract || {{}};
      const run238DirectionCards = (refs.run238DirectionMemory || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / ${{escapeHtml(record.visual_rhythm_id)}}</h4>
        ${{detailBlock("Scene type", record.public_video_scene_type)}}
        ${{detailBlock("First-read object", record.first_read_object)}}
        ${{detailBlock("Specific business object", (record.commercial_story_payload || {{}}).specific_business_object)}}
        ${{detailBlock("Viewer takeaway", (record.commercial_story_payload || {{}}).viewer_takeaway)}}
        ${{detailBlock("Required code modules", record.required_code_modules)}}
        ${{detailBlock("Forbidden patterns", record.forbidden_visible_patterns)}}
      </article>`).join("");
      const run238RecipeCards = (refs.run238RecipeMemory || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / recipe</h4>
        ${{detailBlock("Layout signature target", record.layout_signature_target)}}
        ${{detailBlock("Forbid Run 2.36 signature", record.forbid_run2_36_dominant_layout_signature)}}
        ${{detailBlock("Public gate ribbon", record.show_workflow_gate_as_public_ribbon)}}
        ${{detailBlock("Primary visual weight target", record.primary_visual_weight_target)}}
        ${{detailBlock("Typography recipe", record.typography_recipe)}}
        ${{detailBlock("Spacing recipe", record.spacing_recipe)}}
        ${{detailBlock("Motion beat", record.motion_beat_recipe)}}
      </article>`).join("");
      const run238GateCards = (refs.run238WorkflowGates || []).map((gate) => `<article class="dataCard">
        <h4>${{escapeHtml(gate.role)}} / ${{escapeHtml(gate.gate_id)}}</h4>
        ${{detailBlock("Direction memory", gate.required_public_video_slide_direction_memory_id)}}
        ${{detailBlock("Recipe memory", gate.required_per_slide_visual_recipe_memory_id)}}
        ${{detailBlock("Visual rhythm", gate.required_visual_rhythm_id)}}
        ${{detailBlock("Layout signature target", gate.required_layout_signature_target)}}
        ${{detailBlock("Next rerun contract", gate.next_rerun_contract)}}
        ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
      </article>`).join("");
      const run239Result = refs.run239Result || {{}};
      const run239Rerun = run239Result.rerun || {{}};
      const run239Inputs = run239Result.input_chain || {{}};
      const run239Delta = run239Result.quality_delta || {{}};
      const run239Control = run239Result.control_boundary || {{}};
      const run240Result = refs.run240Result || {{}};
      const run240Rerun = run240Result.rerun || {{}};
      const run240Inputs = run240Result.input_chain || {{}};
      const run240Delta = run240Result.quality_delta || {{}};
      const run240Control = run240Result.control_boundary || {{}};
      const run241Result = refs.run241Result || {{}};
      const run241Rerun = run241Result.rerun || {{}};
      const run241Inputs = run241Result.input_chain || {{}};
      const run241Delta = run241Result.quality_delta || {{}};
      const run241Control = run241Result.control_boundary || {{}};
      const run242Audit = refs.run242Audit || {{}};
      const run242Inputs = run242Audit.input_chain || {{}};
      const run242Trace = run242Audit.trace_closure || {{}};
      const run242Assessment = run242Audit.visual_quality_assessment || {{}};
      const run243Result = refs.run243Result || {{}};
      const run243Inputs = run243Result.input_chain || {{}};
      const run243Outputs = run243Result.output_chain || {{}};
      const run243Counts = run243Result.artifact_counts || {{}};
      const run244Audit = refs.run244DataflowAudit || {{}};
      const run244Inputs = run244Audit.input_chain || {{}};
      const run244Findings = run244Audit.dataflow_findings || {{}};
      const run244NextGate = run244Audit.next_rerun_gate || {{}};
      const run244Result = refs.run244Result || {{}};
      const run244Rerun = run244Result.rerun || {{}};
      const run244RerunInputs = run244Result.input_chain || {{}};
      const run244Delta = run244Result.quality_delta || {{}};
      const run244Control = run244Result.control_boundary || {{}};
      const run245Audit = refs.run245Audit || {{}};
      const run245Inputs = run245Audit.input_chain || {{}};
      const run245Trace = run245Audit.semantic_geometry_trace_effectiveness || {{}};
      const run245Full = run245Trace.full_arm || {{}};
      const run245Bad = run245Trace.bad_control || {{}};
      const run245Visual = run245Audit.visual_effectiveness_assessment || {{}};
      const run245Gate = run245Audit.gate_summary || {{}};
      const run246Result = refs.run246Result || {{}};
      const run246Inputs = run246Result.input_chain || {{}};
      const run246Outputs = run246Result.output_chain || {{}};
      const run246Counts = run246Result.artifact_counts || {{}};
      const run246DecompositionCards = (refs.run246CompositionDecomposition || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / ${{escapeHtml(record.composition_move)}}</h4>
        ${{detailBlock("Decomposition id", record.decomposition_id)}}
        ${{detailBlock("Multimodal sources", record.multimodal_source_record_ids)}}
        ${{detailBlock("Modalities", record.modalities)}}
        ${{detailBlock("Slot failure", record.slot_based_failure_mode)}}
        ${{detailBlock("Native PPT implications", record.native_ppt_composition_implications)}}
        ${{detailBlock("Source boundary", record.source_boundary_rules)}}
      </article>`).join("");
      const run246GrammarCards = (refs.run246VisualObjectGrammar || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / visual object grammar</h4>
        ${{detailBlock("Grammar id", record.visual_object_grammar_id)}}
        ${{detailBlock("Required decomposition", record.required_decomposition_id)}}
        ${{detailBlock("Required semantic assets", record.required_run2_43_semantic_visual_asset_ids)}}
        ${{detailBlock("Replaces Run 2.44 slot geometry", record.replaces_run2_44_slot_based_geometry)}}
        ${{detailBlock("Visual object grammar", record.visual_object_grammar)}}
        ${{detailBlock("Composition quality checks", record.composition_quality_checks)}}
      </article>`).join("");
      const run246GateCards = (refs.run246CompositionWorkflowGates || []).map((gate) => `<article class="dataCard">
        <h4>${{escapeHtml(gate.role)}} / ${{escapeHtml(gate.gate_id)}}</h4>
        ${{detailBlock("Required grammar", gate.required_visual_object_grammar_id)}}
        ${{detailBlock("Required decomposition", gate.required_multimodal_composition_decomposition_id)}}
        ${{detailBlock("Forbid slot-based primary surface", gate.forbid_slot_based_geometry_as_primary_surface)}}
        ${{detailBlock("Require multimodal decomposition", gate.require_multimodal_composition_decomposition)}}
        ${{detailBlock("Required trace fields", gate.required_trace_fields)}}
        ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
      </article>`).join("");
      const run247Result = refs.run247Result || {{}};
      const run247Rerun = run247Result.rerun || {{}};
      const run247Inputs = run247Result.input_chain || {{}};
      const run247Delta = run247Result.quality_delta || {{}};
      const run247Control = run247Result.control_boundary || {{}};
      const run248Audit = refs.run248Audit || {{}};
      const run248Inputs = run248Audit.input_chain || {{}};
      const run248Trace = run248Audit.composition_grammar_trace_effectiveness || {{}};
      const run248Full = run248Trace.full_arm || {{}};
      const run248Bad = run248Trace.bad_control || {{}};
      const run248Prior = run248Trace.prior_run2_44 || {{}};
      const run248Visual = run248Audit.visual_effectiveness_assessment || {{}};
      const run248Content = run248Visual.content_density_diagnosis || {{}};
      const run248Gate = run248Audit.gate_summary || {{}};
      const run249Result = refs.run249Result || {{}};
      const run249Inputs = run249Result.input_chain || {{}};
      const run249Outputs = run249Result.output_chain || {{}};
      const run249Counts = run249Result.artifact_counts || {{}};
      const run249RepairContract = run249Result.repair_contract || {{}};
      const run250Result = refs.run250Result || {{}};
      const run250Inputs = run250Result.input_chain || {{}};
      const run250Rerun = run250Result.rerun || {{}};
      const run250Quality = run250Result.quality_delta || {{}};
      const run251Result = refs.run251Result || {{}};
      const run252Result = refs.run252Result || {{}};
      const run252Inputs = run252Result.input_chain || {{}};
      const run252Rerun = run252Result.rerun || {{}};
      const run252Quality = run252Result.quality_delta || {{}};
      const run252Control = run252Result.control_boundary || {{}};
      const run253Result = refs.run253Result || {{}};
      const run253Outputs = run253Result.output_chain || {{}};
      const run253Counts = run253Result.artifact_counts || {{}};
      const run253RepairContract = run253Result.repair_contract || {{}};
      const run254Result = refs.run254Result || {{}};
      const run254Inputs = run254Result.input_chain || {{}};
      const run254Rerun = run254Result.rerun || {{}};
      const run254Quality = run254Result.quality_delta || {{}};
      const run254Control = run254Result.control_boundary || {{}};
      const run255Result = refs.run255Result || {{}};
      const run255Inputs = run255Result.input_chain || {{}};
      const run255Rerun = run255Result.rerun || {{}};
      const run255Quality = run255Result.quality_delta || {{}};
      const run255Control = run255Result.control_boundary || {{}};
      const run256Result = refs.run256Result || {{}};
      const run256Inputs = run256Result.input_chain || {{}};
      const run256Rerun = run256Result.rerun || {{}};
      const run256Quality = run256Result.quality_delta || {{}};
      const run256Control = run256Result.control_boundary || {{}};
      const run257Result = refs.run257Result || {{}};
      const run257Inputs = run257Result.input_chain || {{}};
      const run257Outputs = run257Result.output_chain || {{}};
      const run257Counts = run257Result.artifact_counts || {{}};
      const run257Quality = run257Result.quality_delta || {{}};
      const run257GenerationBoundary = run257Result.generation_boundary || {{}};
      const run257RepairContract = run257Result.repair_contract || {{}};
      const run257NextGeneratedRunContract = refs.run257NextGeneratedRunContract || {{}};
      const run258Result = refs.run258Result || {{}};
      const run258Inputs = run258Result.input_chain || {{}};
      const run258Rerun = run258Result.rerun || {{}};
      const run258Quality = run258Result.quality_delta || {{}};
      const run258Control = run258Result.control_boundary || {{}};
      const run258OpenSourceUsePolicy = refs.run258OpenSourceUsePolicy || {{}};
      const run258OpenSourceCards = (refs.run258OpenSourceReferences || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.label)}} code reference</h4>
          <p><a href="${{escapeHtml(record.source_url || "#")}}" target="_blank" rel="noreferrer">${{escapeHtml(record.source_url || "source missing")}}</a></p>
          ${{detailBlock("Source type", record.source_type)}}
          ${{detailBlock("What to learn", record.what_to_learn)}}
          ${{detailBlock("Learnable code patterns", record.learnable_code_patterns)}}
          ${{detailBlock("Product relevance", record.product_relevance)}}
          ${{detailBlock("Integration boundary", record.integration_boundary)}}
          ${{detailBlock("License / usage note", record.license_or_usage_note)}}
          ${{detailBlock("do not copy source assets", record.do_not_copy_source_assets)}}
        </article>`).join("");
      const run260Result = refs.run260Result || {{}};
      const run260Inputs = run260Result.input_chain || {{}};
      const run260Rerun = run260Result.rerun || {{}};
      const run260Quality = run260Result.quality_delta || {{}};
      const run260Control = run260Result.control_boundary || {{}};
      const run261Result = refs.run261Result || {{}};
      const run261Quality = run261Result.quality_delta || {{}};
      const run261Boundary = run261Result.generation_boundary || {{}};
      const run261Policy = refs.run261SourcePolicy || {{}};
      const run261Next = refs.run261NextGeneratedRunContract || {{}};
      const run262Result = refs.run262Result || {{}};
      const run262Inputs = run262Result.input_chain || {{}};
      const run262Rerun = run262Result.rerun || {{}};
      const run262Quality = run262Result.quality_delta || {{}};
      const run262Control = run262Result.control_boundary || {{}};
      const run261SelectorByRole = Object.fromEntries((refs.run261SelectorRecords || []).map((record) => [record.role, record]));
      const run261FusionByRole = Object.fromEntries((refs.run261FusionRecords || []).map((record) => [record.role, record]));
      const run261GateByRole = Object.fromEntries((refs.run261WorkflowGates || []).map((gate) => [gate.role, gate]));
      const run261ExpandedRoleCards = (refs.run261NarrativeRecords || []).map((record) => {{
        const selector = run261SelectorByRole[record.role] || {{}};
        const fusion = run261FusionByRole[record.role] || {{}};
        const gate = run261GateByRole[record.role] || {{}};
        const proof = record.proof_payload || {{}};
        const copy = record.copy_units || {{}};
        const replacement = record.public_proof_replacement || {{}};
        const density = record.density_budget || {{}};
        const sockets = (fusion.socket_bindings || []).map((socket) => `
          <li>
            <strong>${{escapeHtml(socket.copy_unit_key || "")}}</strong>
            <span> -> ${{escapeHtml(socket.owning_shape_role || "")}} / ${{escapeHtml(socket.socket_id || "")}}</span><br>
            <span>${{escapeHtml(socket.character_budget || "")}} chars, ${{escapeHtml(socket.max_lines || "")}} lines, min ${{escapeHtml(socket.minimum_font_size || "")}}px. ${{escapeHtml(socket.placement_rule || "")}}</span>
          </li>`).join("");
        const socketPlan = sockets
          ? `<div><div class="dataLabel">Socket plan</div><ul class="socketPlan">${{sockets}}</ul></div>`
          : "";
        return `<article class="dataCard run261Contract">
          <div class="contractHeader">
            <h4>${{escapeHtml(record.role || "")}} / 2.61 consumption contract</h4>
            <span class="roleTag">${{escapeHtml(record.source_generated_run_id || "2.60")}} -> 2.62</span>
          </div>
          <div class="contractRoute">
            <div class="routeStep"><b>Question</b><span>${{escapeHtml(record.reader_question || "")}}</span></div>
            <div class="routeStep"><b>Answer</b><span>${{escapeHtml(record.required_answer || "")}}</span></div>
            <div class="routeStep"><b>Business action</b><span>${{escapeHtml(record.business_action || "")}}</span></div>
            <div class="routeStep"><b>Visual carrier</b><span>${{escapeHtml(selector.visual_carrier_type || "")}} / ${{escapeHtml(selector.selected_layout_module_id || "")}}</span></div>
          </div>
          ${{detailBlock("Narrative proof id", record.narrative_proof_id)}}
          ${{detailBlock("Public headline", copy.headline)}}
          ${{detailBlock("Public subhead", copy.subhead)}}
          ${{detailBlock("Proof badges", copy.proof_badges)}}
          ${{detailBlock("Primary evidence object", proof.primary_evidence_object)}}
          ${{detailBlock("Secondary evidence objects", proof.secondary_evidence_objects)}}
          ${{detailBlock("Product mechanism", proof.product_mechanism)}}
          ${{detailBlock("Business consequence", proof.business_consequence)}}
          ${{detailBlock("Before / after", [proof.before_state, proof.after_state].filter(Boolean))}}
          ${{detailBlock("Viewer notice", proof.what_the_viewer_should_notice)}}
          ${{detailBlock("Public proof replacement", `${{replacement.replacement_type || ""}}: ${{replacement.replacement_rule || ""}}`)}}
          ${{detailBlock("Visual weight requirement", selector.visual_weight_requirement)}}
          ${{detailBlock("Text socket requirement", selector.text_socket_requirement)}}
          ${{socketPlan}}
          ${{detailBlock("maximum_public_visible_words", density.maximum_public_visible_words)}}
          ${{detailBlock("minimum_public_proof_objects", density.minimum_public_proof_objects)}}
          ${{detailBlock("minimum_socket_bound_copy_units", density.minimum_socket_bound_copy_units)}}
          <div class="traceGate">
            ${{detailBlock("Trace gate", gate.gate_id)}}
            ${{detailBlock("Required checks", gate.required_checks)}}
            ${{detailBlock("Next trace fields", gate.next_run_required_trace_fields)}}
            ${{detailBlock("Bad control probe", gate.bad_control_probe)}}
          </div>
          ${{detailBlock("Source refs", (record.source_refs || []).map((source) => `${{source.source_id}} / ${{source.source_record_id}}`))}}
        </article>`;
      }}).join("");
      const run261NarrativeCards = (refs.run261NarrativeRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.role || "")}} narrative proof</h4>
          ${{detailBlock("Reader question", record.reader_question)}}
          ${{detailBlock("Required answer", record.required_answer)}}
          ${{detailBlock("Business action", record.business_action)}}
          ${{detailBlock("Primary proof", (record.proof_payload || {{}}).primary_evidence_object)}}
          ${{detailBlock("Public replacement", (record.public_proof_replacement || {{}}).replacement_type)}}
        </article>`).join("");
      const run261SelectorCards = (refs.run261SelectorRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.role || "")}} visual carrier</h4>
          ${{detailBlock("Carrier", record.visual_carrier_type)}}
          ${{detailBlock("Layout module", record.selected_layout_module_id)}}
          ${{detailBlock("Socket memory", record.selected_socket_memory_id)}}
          ${{detailBlock("Reason", record.carrier_reason)}}
        </article>`).join("");
      const run261FusionCards = (refs.run261FusionRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.role || "")}} text socket fusion</h4>
          ${{detailBlock("Fusion contract", record.fusion_contract_id)}}
          ${{detailBlock("Source socket memory", record.source_socket_memory_id)}}
          ${{detailBlock("Socket count", (record.socket_bindings || []).length)}}
          ${{detailBlock("Overflow", record.overflow_behavior)}}
        </article>`).join("");
      const run259Result = refs.run259Result || {{}};
      const run259Quality = run259Result.quality_delta || {{}};
      const run259GenerationBoundary = run259Result.generation_boundary || {{}};
      const run259Next = refs.run259NextGeneratedRunContract || {{}};
      const run259TracePolicy = refs.run259PublicTracePolicy || {{}};
      const run259PublicSurface = run259TracePolicy.public_slide_surface || {{}};
      const run259TraceSurface = run259TracePolicy.trace_viewer_surface || {{}};
      const run259ContractCards = (refs.run259ContentContracts || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.role)}} content contract</h4>
          ${{detailBlock("Contract id", record.content_contract_id)}}
          ${{detailBlock("Source message contract", record.source_message_contract_id)}}
          ${{detailBlock("Public claim", record.public_claim)}}
          ${{detailBlock("Primary proof object", record.primary_proof_object)}}
          ${{detailBlock("Evidence chips", record.evidence_chips)}}
          ${{detailBlock("Trace-only details", record.trace_only_details)}}
          ${{detailBlock("Max public visible words", record.max_public_visible_words)}}
        </article>`).join("");
      const run259CapacityCards = (refs.run259LayoutCapacityRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.module_family)}} capacity</h4>
          ${{detailBlock("Layout module", record.layout_module_id)}}
          ${{detailBlock("Source memory", record.source_layout_module_memory)}}
          ${{detailBlock("Max title lines", record.max_title_lines)}}
          ${{detailBlock("Max visible words", record.max_visible_words)}}
          ${{detailBlock("Max evidence chips", record.max_evidence_chips)}}
          ${{detailBlock("Primary object area min pct", record.primary_object_area_min_pct)}}
          ${{detailBlock("Spacing rule", record.spacing_rule)}}
          ${{detailBlock("Forbidden patterns", record.forbidden_patterns)}}
        </article>`).join("");
      const run259SelectorCards = (refs.run259SelectorRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.role)}} layout selection</h4>
          ${{detailBlock("Content contract", record.content_contract_id)}}
          ${{detailBlock("Selected layout module", record.selected_layout_module_id)}}
          ${{detailBlock("Content burden", record.content_burden_level)}}
          ${{detailBlock("Proof object type", record.proof_object_type)}}
          ${{detailBlock("Public visible word budget", record.public_visible_word_budget)}}
          ${{detailBlock("Capacity fit status", record.capacity_fit_status)}}
          ${{detailBlock("Selection reason", record.selection_reason)}}
          ${{detailBlock("Fallback route", record.fallback_route)}}
        </article>`).join("");
      const run259GateCards = (refs.run259WorkflowGates || []).map((gate) => `
        <article class="dataCard">
          <h4>${{escapeHtml(gate.role)}} composition gate</h4>
          ${{detailBlock("Gate id", gate.gate_id)}}
          ${{detailBlock("Content contract", gate.content_contract_id)}}
          ${{detailBlock("Selected layout module", gate.selected_layout_module_id)}}
          ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
          ${{detailBlock("Bad control probe", gate.bad_control_probe)}}
          ${{detailBlock("Required trace fields", gate.required_trace_fields)}}
        </article>`).join("");
      const run257CapabilityCards = (refs.run257ProductCapabilities || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.capability_layer)}} capability</h4>
          ${{detailBlock("Capability id", record.id)}}
          ${{detailBlock("Claim", record.plain_language_claim)}}
          ${{detailBlock("Visible PPT obligation", record.visible_ppt_obligation)}}
          ${{detailBlock("Trace obligation", record.trace_obligation)}}
          ${{detailBlock("Why it matters", record.why_it_matters)}}
        </article>`).join("");
      const run257LogicCards = (refs.run257ProductLogicRelations || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.relation_type)}} relation</h4>
          ${{detailBlock("Relation id", record.id)}}
          ${{detailBlock("From", record.from_capability_id)}}
          ${{detailBlock("To", record.to_capability_id)}}
          ${{detailBlock("Must be visible as", record.must_be_visible_as)}}
        </article>`).join("");
      const run257CompetitorCards = (refs.run257CompetitorBoundaries || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.competitor_boundary_id)}} boundary</h4>
          ${{detailBlock("Competitor pattern", record.competitor_pattern)}}
          ${{detailBlock("Vulca difference", record.vulca_difference)}}
          ${{detailBlock("Slide obligation", record.slide_obligation)}}
        </article>`).join("");
      const run257MessageCards = (refs.run257SlideMessageContracts || []).map((contract) => `
        <article class="dataCard">
          <h4>${{escapeHtml(contract.role)}} message contract</h4>
          ${{detailBlock("Contract id", contract.contract_id)}}
          ${{detailBlock("Reader question", contract.reader_question)}}
          ${{detailBlock("Required answer", contract.required_answer)}}
          ${{detailBlock("Visible product object", contract.visible_product_object)}}
          ${{detailBlock("Required product terms", contract.required_product_terms)}}
          ${{detailBlock("Minimum specific units", contract.minimum_specific_content_units)}}
        </article>`).join("");
      const run257GateCards = (refs.run257ContentWorkflowGates || []).map((gate) => `
        <article class="dataCard">
          <h4>${{escapeHtml(gate.gate_id)}} gate</h4>
          ${{detailBlock("Type", gate.gate_type)}}
          ${{detailBlock("Purpose", gate.purpose)}}
          ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
          ${{detailBlock("Bad control probe", gate.bad_control_probe)}}
          ${{detailBlock("Next generated run", gate.consumer_contract?.next_generated_run)}}
          ${{detailBlock("Trace fields", gate.required_trace_fields)}}
        </article>`).join("");
      const run253SceneCards = (refs.run253ProductSurfaceScenes || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.role)}} product surface scene</h4>
          ${{detailBlock("Scene id", record.id)}}
          ${{detailBlock("Object", record.primary_product_or_business_object)}}
          ${{detailBlock("Surface slots", record.surface_slots)}}
          ${{detailBlock("Forbidden patterns", record.forbidden_patterns)}}
          ${{detailBlock("Next rerun", record.next_rerun_obligation)}}
        </article>`).join("");
      const run253EvidenceCards = (refs.run253BusinessVisualEvidence || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.role)}} business visual evidence</h4>
          ${{detailBlock("Evidence id", record.id)}}
          ${{detailBlock("Required scene", record.required_product_surface_scene_id)}}
          ${{detailBlock("Observable business object", record.observable_business_object)}}
          ${{detailBlock("Reader question", record.reader_question_answered)}}
          ${{detailBlock("Specificity checks", record.minimum_visual_specificity_checks)}}
        </article>`).join("");
      const run253GateCards = (refs.run253SceneRendererGates || []).map((gate) => `
        <article class="dataCard">
          <h4>${{escapeHtml(gate.role)}} scene renderer gate</h4>
          ${{detailBlock("Gate", gate.id)}}
          ${{detailBlock("Required scene", gate.required_product_surface_scene_id)}}
          ${{detailBlock("Required evidence", gate.required_business_visual_evidence_id)}}
          ${{detailBlock("Next generated run", gate.consumer_contract?.next_generated_run)}}
          ${{detailBlock("Trace fields", gate.required_trace_fields)}}
        </article>`).join("");
      const run251CopyCards = (refs.run251CopyRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.role)}} editorial copy</h4>
          ${{detailBlock("Headline", record.public_surface_copy_bundle?.headline)}}
          ${{detailBlock("Subline", record.public_surface_copy_bundle?.subline)}}
          ${{detailBlock("Proof nuggets", record.public_surface_copy_bundle?.proof_nuggets)}}
          ${{detailBlock("Business claim", record.business_claim_preservation_check)}}
          ${{detailBlock("Next rerun", record.next_rerun_obligation)}}
        </article>`).join("");
      const run251SocketCards = (refs.run251SocketRecords || []).map((record) => `
        <article class="dataCard">
          <h4>${{escapeHtml(record.role)}} sockets</h4>
          ${{detailBlock("Archetype", record.primary_archetype)}}
          ${{detailBlock("Shape primitives", record.shape_primitives)}}
          ${{detailBlock("Socket count", (record.socket_contracts || []).length)}}
          ${{detailBlock("Geometry constraints", record.geometry_constraints)}}
        </article>`).join("");
      const run251GateCards = (refs.run251Gates || []).map((gate) => `
        <article class="dataCard">
          <h4>${{escapeHtml(gate.role)}} archetype gate</h4>
          ${{detailBlock("Gate", gate.gate_id)}}
          ${{detailBlock("Primary archetype", gate.primary_archetype)}}
          ${{detailBlock("Trace fields", gate.required_trace_fields)}}
          ${{detailBlock("Bad control", gate.bad_control_probe)}}
        </article>`).join("");
      const run249ReadabilityCards = (refs.run249ReadabilityRecords || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / readability</h4>
        ${{detailBlock("Readability memory id", record.readability_memory_id)}}
        ${{detailBlock("Gate id", record.readability_gate_id)}}
        ${{detailBlock("Goal", record.readability_goal)}}
        ${{detailBlock("Min contact-sheet title px", record.min_contact_sheet_title_px)}}
        ${{detailBlock("Max headline words", record.max_headline_words)}}
        ${{detailBlock("Forbid title clipping", record.forbid_title_clipping)}}
        ${{detailBlock("Checks", record.required_readability_checks)}}
      </article>`).join("");
      const run249DensityCards = (refs.run249DensityRecords || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / content evidence density</h4>
        ${{detailBlock("Density memory id", record.content_evidence_density_memory_id)}}
        ${{detailBlock("Required readability", record.required_readability_memory_id)}}
        ${{detailBlock("Min specific business evidence objects", record.min_specific_business_evidence_objects)}}
        ${{detailBlock("Min inspectable proof objects", record.min_inspectable_visual_proof_objects)}}
        ${{detailBlock("Evidence object contract", record.evidence_object_contract)}}
        ${{detailBlock("Inspectable proof objects", record.inspectable_visual_proof_object_contract)}}
        ${{detailBlock("Forbidden substitutes", record.forbidden_evidence_substitutes)}}
      </article>`).join("");
      const run249GateCards = (refs.run249Gates || []).map((gate) => `<article class="dataCard">
        <h4>${{escapeHtml(gate.role)}} / editorial renderer</h4>
        ${{detailBlock("Gate id", gate.gate_id)}}
        ${{detailBlock("Renderer contract id", gate.renderer_contract_id)}}
        ${{detailBlock("Surface contract", gate.surface_contract)}}
        ${{detailBlock("Forbid square block grid", gate.forbid_square_block_grid_as_primary_surface)}}
        ${{detailBlock("Non-square ratio variants", gate.min_non_square_surface_ratio_variants)}}
        ${{detailBlock("Require contact-sheet readability", gate.require_contact_sheet_readability)}}
        ${{detailBlock("Require inspectable business evidence", gate.require_inspectable_business_evidence)}}
        ${{detailBlock("Next rerun contract", gate.next_rerun_contract)}}
        ${{detailBlock("Trace fields", gate.required_trace_fields)}}
      </article>`).join("");
      const run243SemanticAssetCards = (refs.run243SemanticVisualAssets || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / ${{escapeHtml(record.source_run2_41_surface_type)}}</h4>
        ${{detailBlock("Semantic asset id", record.semantic_asset_id)}}
        ${{detailBlock("Usecase object", record.usecase_specific_semantic_object)}}
        ${{detailBlock("Observable scene evidence", record.observable_scene_evidence)}}
        ${{detailBlock("Allowed native PPT representation", record.allowed_native_ppt_representation)}}
        ${{detailBlock("Forbidden substitutes", record.forbidden_schematic_substitutes)}}
        ${{detailBlock("Source boundary", record.source_boundary_note)}}
      </article>`).join("");
      const run243EditorialCards = (refs.run243EditorialTypographyMemory || []).map((record) => `<article class="dataCard">
        <h4>${{escapeHtml(record.role)}} / editorial typography</h4>
        ${{detailBlock("Memory id", record.editorial_typography_memory_id)}}
        ${{detailBlock("Semantic assets", record.required_semantic_asset_ids)}}
        ${{detailBlock("First-read scene object", record.first_read_scene_object)}}
        ${{detailBlock("Layout signature target", record.layout_signature_target)}}
        ${{detailBlock("Primary visual weight", record.primary_visual_weight_target)}}
        ${{detailBlock("Typography hierarchy", record.typography_hierarchy_rules)}}
        ${{detailBlock("Editorial composition", record.editorial_composition_rules)}}
        ${{detailBlock("Scene depth rule", record.climax_or_scene_depth_rule)}}
      </article>`).join("");
      const run243GateCards = (refs.run243VisualAssetSemanticsWorkflowGates || []).map((gate) => `<article class="dataCard">
        <h4>${{escapeHtml(gate.role)}} / ${{escapeHtml(gate.gate_id)}}</h4>
        ${{detailBlock("Semantic assets", gate.required_semantic_asset_ids)}}
        ${{detailBlock("Editorial typography memory", gate.required_editorial_typography_memory_id)}}
        ${{detailBlock("Min semantic visual assets", gate.min_semantic_visual_assets)}}
        ${{detailBlock("Forbid generic placeholders", gate.forbid_generic_placeholder_assets)}}
        ${{detailBlock("Forbid schematic shape-only surface", gate.forbid_schematic_native_shape_only_surface)}}
        ${{detailBlock("Next rerun contract", gate.next_rerun_contract)}}
        ${{detailBlock("Pass/fail checks", gate.pass_fail_checks)}}
      </article>`).join("");
      const run217Audit = refs.run217MotionAudit || {{}};
      const run217DeliveryTruth = run217Audit.delivery_truth || {{}};
      const run217RendererGap = run217Audit.motion_renderer_gap || {{}};
      const run217ArmAudits = (run217Audit.arm_audits || []).map(run217ArmAuditCard).join("");
      const run217Proof = refs.run217MotionProof || {{}};
      const run217ProofBoundary = run217Proof.delivery_boundary || {{}};
      const run217ProofScenes = (run217Proof.scenes || []).map(run217ProofSceneCard).join("");
      const proofHtmlLink = refs.run217MotionProofHtmlHref
        ? `<a href="${{escapeHtml(refs.run217MotionProofHtmlHref)}}" target="_blank" rel="noreferrer">run2-17-motion-renderer-proof.html</a>`
        : "";
      const proofManifestLink = refs.run217MotionProofManifestHref
        ? `<a href="${{escapeHtml(refs.run217MotionProofManifestHref)}}" target="_blank" rel="noreferrer">run2-17-motion-renderer-proof-manifest.json</a>`
        : "";
      const stages = (refs.workflowStages || []).map(stageCard).join("");
      const skill = escapeHtml(refs.skillMarkdown || "Missing vulca_ppt_skill.md");

      content.innerHTML = `<div class="sectionHeader">
        <div><h2>Reference data and skill workflow</h2><div class="summary">Shows the allowed derived evidence behind the case pack, not copied tutorial media or source layouts.</div></div>
        <span class="pill">${{escapeHtml(refs.packPath || "case pack")}}</span>
      </div>
      <div class="dataStack">
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.62 generated narrative proof consumption</h3><p>Run 2.62 is the current generated proof: the full arm consumes Run 2.61 narrative proof records, visual carrier selectors, text socket fusion contracts, public proof replacements, and workflow gates before native PPT drawing.</p></div><span class="pill" title="${{escapeHtml(refs.run262ResultStatus || "missing")}}">${{escapeHtml(refs.run262ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run 2.62 generated result</h4>
              ${{detailBlock("Result", refs.run262ResultPath || "run2_62_narrative_proof_rerun_result.json")}}
              ${{detailBlock("Best arm", run262Rerun.best_internal_arm || "run2_62_full_narrative_proof")}}
              ${{detailBlock("Target layer", run262Quality.target_layer || refs.run262TargetLayer)}}
              ${{detailBlock("Source data status", run262Quality.source_data_status || refs.run262SourceDataStatus)}}
              ${{detailBlock("Contact sheet", run262Rerun.combined_contact_sheet || "run2-62-four-arm-contact-sheet.png")}}
            </article>
            <article class="dataCard">
              <h4>Run 2.61 consumed by generator</h4>
              ${{detailBlock("Narrative proof dataset", run262Inputs.run2_61_narrative_proof_dataset || "run2_61_narrative_proof_dataset.json")}}
              ${{detailBlock("Visual carrier selector", run262Inputs.run2_61_visual_carrier_selector || "run2_61_story_to_visual_carrier_selector.json")}}
              ${{detailBlock("Text socket fusion", run262Inputs.run2_61_text_socket_fusion || "run2_61_text_socket_fusion_contracts.json")}}
              ${{detailBlock("Source policy", run262Inputs.run2_61_source_policy || "run2_61_source_to_public_proof_policy.json")}}
              ${{detailBlock("Narrative workflow gates", run262Inputs.run2_61_workflow_gates || "run2_61_narrative_workflow_gates.json")}}
            </article>
            <article class="dataCard">
              <h4>Consumption trace metrics</h4>
              ${{detailBlock("Slides with 2.61 contracts", run262Quality.full_slides_with_run2_61_contracts)}}
              ${{detailBlock("Slides with socket bindings", run262Quality.full_slides_with_socket_bindings)}}
              ${{detailBlock("Slides with public proof replacement", run262Quality.full_slides_with_public_proof_replacements)}}
              ${{detailBlock("Required answers visible", run262Quality.full_slides_with_required_answers_visible)}}
              ${{detailBlock("Bad-control failures", run262Quality.bad_control_slides_without_run2_61_contracts)}}
            </article>
            <article class="dataCard">
              <h4>2.62 trace surfaces</h4>
              ${{detailBlock("Generator", refs.run262GeneratorPath || "scripts/generate_ppt_run2_62_narrative_proof_arms.mjs")}}
              ${{detailBlock("Full trace", refs.run262FullTracePath || "ppt-run2-62-full-vulca/trace_manifest.json")}}
              ${{detailBlock("Bad trace", refs.run262BadTracePath || "ppt-run2-62-bad-without-narrative-proof/trace_manifest.json")}}
              ${{detailBlock("Four-arm sheet", refs.run262FourArmSheetPath || "run2-62-four-arm-contact-sheet.png")}}
              ${{detailBlock("Negative boundary", run262Control.bad_run2_60_without_run2_61_narrative_proof_dataset)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Previous generated repair proof</h3><p>Run 2.60 consumes Run 2.59 before native PPT drawing, so the content-aware composition compiler consumed status is visible in both slide trace and result metadata.</p></div><span class="pill" title="${{escapeHtml(refs.run260ResultStatus || "missing")}}">${{escapeHtml(refs.run260ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run 2.60 generated result</h4>
              ${{detailBlock("Result", refs.run260ResultPath || "run2_60_content_aware_composition_rerun_result.json")}}
              ${{detailBlock("Best arm", run260Rerun.best_internal_arm || "run2_60_full_content_aware_composition")}}
              ${{detailBlock("Target layer", run260Quality.target_layer || refs.run260TargetLayer)}}
              ${{detailBlock("Source data status", run260Quality.source_data_status || refs.run260SourceDataStatus)}}
              ${{detailBlock("Contact sheet", run260Rerun.combined_contact_sheet || "run2-60-four-arm-contact-sheet.png")}}
            </article>
            <article class="dataCard">
              <h4>Run 2.59 consumed by generator</h4>
              ${{detailBlock("Content contracts", run260Inputs.run2_59_content_contracts || "run2_59_content_composition_contracts.json")}}
              ${{detailBlock("Layout capacity model", run260Inputs.run2_59_layout_capacity_model || "run2_59_layout_capacity_model.json")}}
              ${{detailBlock("Content-to-layout selector", run260Inputs.run2_59_content_to_layout_selector || "run2_59_content_to_layout_selector.json")}}
              ${{detailBlock("Public slide / trace viewer split", run260Inputs.run2_59_public_surface_trace_policy || "run2_59_public_surface_trace_policy.json")}}
              ${{detailBlock("Composition workflow gates", run260Inputs.run2_59_composition_workflow_gates || "run2_59_composition_workflow_gates.json")}}
            </article>
            <article class="dataCard">
              <h4>Consumption trace metrics</h4>
              ${{detailBlock("Content contracts bound", run260Quality.full_slides_with_run2_59_content_contracts)}}
              ${{detailBlock("Layout capacity fit", run260Quality.full_slides_with_layout_capacity_fit)}}
              ${{detailBlock("Public/trace split", run260Quality.full_slides_with_public_trace_split)}}
              ${{detailBlock("No layout collision", run260Quality.full_slides_without_layout_collision)}}
              ${{detailBlock("Bad-control failures", run260Quality.bad_control_slides_without_run2_59_compiler)}}
            </article>
            <article class="dataCard">
              <h4>2.60 trace surfaces</h4>
              ${{detailBlock("Generator", refs.run260GeneratorPath || "scripts/generate_ppt_run2_60_content_aware_composition_arms.mjs")}}
              ${{detailBlock("Full trace", refs.run260FullTracePath || "ppt-run2-60-full-vulca/trace_manifest.json")}}
              ${{detailBlock("Bad trace", refs.run260BadTracePath || "ppt-run2-60-bad-without-composition-compiler/trace_manifest.json")}}
              ${{detailBlock("Four-arm sheet", refs.run260FourArmSheetPath || "run2-60-four-arm-contact-sheet.png")}}
              ${{detailBlock("Negative boundary", run260Control.bad_run2_58_without_run2_59_composition_compiler)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.61 narrative proof dataset</h3><p>Why 2.60 felt thin: the generated deck consumed compressed claims, but did not directly bind thick source data, text sockets, visual carriers, and public proof replacements. Run 2.61 repairs that data/workflow layer before any Run 2.62 deck generation.</p></div><span class="pill" title="${{escapeHtml(refs.run261ResultStatus || "missing")}}">${{escapeHtml(refs.run261ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Layer boundary</h4>
              ${{detailBlock("Result", refs.run261ResultPath || "run2_61_narrative_proof_dataset_result.json")}}
              ${{detailBlock("Creates new PPT deck", run261Boundary.creates_new_ppt_deck)}}
              ${{detailBlock("Latest generated run", run261Boundary.latest_generated_run_id || "2.60")}}
              ${{detailBlock("Target layer", run261Quality.target_layer)}}
              ${{detailBlock("Next action", run261Result.next_required_action || "run2_62_generate_four_arm_ppt_consuming_run2_61_narrative_proof_dataset")}}
            </article>
            <article class="dataCard">
              <h4>Artifacts</h4>
              ${{detailBlock("Narrative proof", refs.run261NarrativePath || "run2_61_narrative_proof_dataset.json")}}
              ${{detailBlock("Visual carrier selector", refs.run261SelectorPath || "run2_61_story_to_visual_carrier_selector.json")}}
              ${{detailBlock("Text socket fusion", refs.run261FusionPath || "run2_61_text_socket_fusion_contracts.json")}}
              ${{detailBlock("Source policy", refs.run261SourcePolicyPath || "run2_61_source_to_public_proof_policy.json")}}
              ${{detailBlock("Workflow gates", refs.run261WorkflowGatesPath || "run2_61_narrative_workflow_gates.json")}}
            </article>
            <article class="dataCard">
              <h4>Public proof replacement</h4>
              ${{detailBlock("Policy id", run261Policy.policy_id)}}
              ${{detailBlock("Allowed abstractions", run261Policy.allowed_source_abstraction_types)}}
              ${{detailBlock("Forbidden copying", run261Policy.forbidden_source_copying_behaviors)}}
            </article>
            <article class="dataCard">
              <h4>Next Run 2.62 contract</h4>
              ${{detailBlock("Run", run261Next.run_id || "2.62")}}
              ${{detailBlock("Required trace fields", run261Next.required_trace_fields)}}
              ${{detailBlock("Bad control", run261Next.bad_control_arm || "bad_run2_60_without_run2_61_narrative_proof_dataset")}}
              ${{detailBlock("Full pass status", run261Next.full_arm_pass_status || "run2_61_narrative_proof_dataset_consumed_before_native_ppt_drawing")}}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Run 2.61 expanded role contracts</h4><p>One card per slide role, joining narrative proof, visual carrier selector, socket fusion, density budget, public-proof replacement, source refs, and the trace gate that Run 2.62 must consume.</p></div>
          <div class="dataGrid expandedGrid">${{run261ExpandedRoleCards}}</div>
          <div class="dataBandSubhead"><h4>Per-slide narrative proof table</h4><p>${{escapeHtml(refs.run261NarrativeStatus)}}. Each role now carries reader question, required answer, business action, proof payload, copy units, source refs, and public proof replacement.</p></div>
          <div class="dataGrid">${{run261NarrativeCards}}</div>
          <div class="dataBandSubhead"><h4>Visual carrier selector</h4><p>${{escapeHtml(refs.run261SelectorStatus)}}. Each role selects a visual carrier from business action, proof payload, Run 2.15 layout memory, and Run 2.51 socket availability.</p></div>
          <div class="dataGrid">${{run261SelectorCards}}</div>
          <div class="dataBandSubhead"><h4>Text socket fusion</h4><p>${{escapeHtml(refs.run261FusionStatus)}}. Required copy units must bind to sockets before Run 2.62 native PPT drawing.</p></div>
          <div class="dataGrid">${{run261FusionCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.58 product-content proof</h3><p>Run 2.58 remains the previous generated product-content proof: it consumes the Run 2.57 product capability content layer, keeps the Run 2.56 role-renderer pass, and forces every slide to answer a concrete product reader question.</p></div><span class="pill" title="${{escapeHtml(refs.run258ResultStatus || "missing")}}">${{escapeHtml(refs.run258ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run 2.58 generated result</h4>
              ${{detailBlock("Result", refs.run258ResultPath || "run2_58_product_content_contract_rerun_result.json")}}
              ${{detailBlock("Best arm", run258Rerun.best_internal_arm || "run2_58_full_product_content_contract")}}
              ${{detailBlock("Target layer", run258Quality.target_layer || refs.run258TargetLayer)}}
              ${{detailBlock("Source data status", run258Quality.source_data_status || refs.run258SourceDataStatus)}}
              ${{detailBlock("Contact sheet", run258Rerun.combined_contact_sheet || "run2-58-four-arm-contact-sheet.png")}}
            </article>
            <article class="dataCard">
              <h4>Product-content binding metrics</h4>
              ${{detailBlock("Capability ids", run258Quality.full_slides_with_run2_57_capability_ids)}}
              ${{detailBlock("Message contracts", run258Quality.full_slides_with_message_contracts)}}
              ${{detailBlock("Workflow gates", run258Quality.full_slides_with_content_workflow_gates)}}
              ${{detailBlock("Reader question pass", run258Quality.full_slides_with_reader_question_answered)}}
              ${{detailBlock("Zero generic claims", run258Quality.full_slides_with_zero_generic_claims)}}
            </article>
            <article class="dataCard">
              <h4>Consumed 2.57 content chain</h4>
              ${{detailBlock("Run 2.57 result", run258Inputs.run2_57_result || "run2_57_product_capability_content_result.json")}}
              ${{detailBlock("Product capability memory", run258Inputs.run2_57_product_capability_memory || "run2_57_product_capability_memory.json")}}
              ${{detailBlock("Slide message contracts", run258Inputs.run2_57_slide_message_contracts || "run2_57_slide_message_contracts.json")}}
              ${{detailBlock("Content workflow gates", run258Inputs.run2_57_content_workflow_gates || "run2_57_content_workflow_gates.json")}}
              ${{detailBlock("Run 2.56 full trace", run258Inputs.run2_56_full_trace || "ppt-run2-56-full-vulca/trace_manifest.json")}}
            </article>
            <article class="dataCard">
              <h4>2.58 negative control</h4>
              ${{detailBlock("Bad arm", "bad_run2_56_without_product_capability_content")}}
              ${{detailBlock("Missing-content slides", run258Quality.bad_control_slides_without_run2_57_content)}}
              ${{detailBlock("Boundary", run258Control.bad_run2_56_without_product_capability_content || "Bad control may see Run 2.56 visual proof, but cannot use Run 2.57 product capability content contracts.")}}
            </article>
            <article class="dataCard">
              <h4>Run 2.56 generated result</h4>
              ${{detailBlock("Result", refs.run256ResultPath || "run2_56_role_renderer_split_rerun_result.json")}}
              ${{detailBlock("Best arm", run256Rerun.best_internal_arm || "run2_56_full_role_renderer_split")}}
              ${{detailBlock("Target layer", run256Quality.target_layer || refs.run256TargetLayer)}}
              ${{detailBlock("Source data status", run256Quality.source_data_status || refs.run256SourceDataStatus)}}
              ${{detailBlock("Contact sheet", run256Rerun.combined_contact_sheet || "run2-56-four-arm-contact-sheet.png")}}
            </article>
            <article class="dataCard">
              <h4>Role-renderer split metrics</h4>
              ${{detailBlock("Unique renderer ids", run256Quality.full_slides_with_unique_role_renderer)}}
              ${{detailBlock("Unique layout signatures", run256Quality.full_slides_with_unique_layout_signature)}}
              ${{detailBlock("Archetype binding pass", run256Quality.full_slides_with_role_archetype_binding)}}
              ${{detailBlock("No text collision risk", run256Quality.full_slides_without_text_collision_risk)}}
              ${{detailBlock("No overflow risk", run256Quality.full_slides_without_text_overflow_risk)}}
            </article>
            <article class="dataCard">
              <h4>Consumed input chain</h4>
              ${{detailBlock("Run 2.55 result", run256Inputs.run2_55_result || "run2_55_text_shape_integration_rerun_result.json")}}
              ${{detailBlock("Run 2.55 full trace", run256Inputs.run2_55_full_trace || "ppt-run2-55-full-vulca/trace_manifest.json")}}
              ${{detailBlock("Run 2.51 copy memory", run256Inputs.run2_51_editorial_copy_memory || "run2_51_editorial_copy_memory.json")}}
              ${{detailBlock("Run 2.51 socket memory", run256Inputs.run2_51_shape_text_socket_memory || "run2_51_shape_text_socket_memory.json")}}
              ${{detailBlock("Run 2.53 scene gates", run256Inputs.run2_53_scene_renderer_workflow_gates || "run2_53_scene_renderer_workflow_gates.json")}}
            </article>
            <article class="dataCard">
              <h4>Negative control</h4>
              ${{detailBlock("Bad arm", "bad_run2_55_reused_single_template")}}
              ${{detailBlock("Reused-template slides", run256Quality.bad_control_slides_with_reused_run2_55_template)}}
              ${{detailBlock("Boundary", run256Control.bad_run2_55_reused_single_template || "Bad control may reuse Run 2.55 trace, but cannot use Run 2.56 role renderer modules.")}}
            </article>
            <article class="dataCard">
              <h4>Run 2.55 generated result</h4>
              ${{detailBlock("Result", refs.run255ResultPath || "run2_55_text_shape_integration_rerun_result.json")}}
              ${{detailBlock("Best arm", run255Rerun.best_internal_arm || "run2_55_full_text_shape_integration")}}
              ${{detailBlock("Target layer", run255Quality.target_layer || refs.run255TargetLayer)}}
              ${{detailBlock("Source data status", run255Quality.source_data_status || refs.run255SourceDataStatus)}}
              ${{detailBlock("Contact sheet", run255Rerun.combined_contact_sheet || "run2-55-four-arm-contact-sheet.png")}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.58 experiment lab</h3><p>This is the current product experiment surface: inspect the generated result, the code generator, the full/bad traces, and the open-source slide-code learning map in one place.</p></div><span class="pill" title="${{escapeHtml(refs.run258OpenSourceResearchStatus || "missing")}}">${{escapeHtml(refs.run258OpenSourceResearchStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Generated proof to inspect</h4>
              ${{detailBlock("Generated result", refs.run258ResultPath || "run2_58_product_content_contract_rerun_result.json")}}
              ${{detailBlock("Generator source", refs.run258GeneratorPath || "scripts/generate_ppt_run2_58_product_content_contract_arms.mjs")}}
              ${{detailBlock("Full arm trace", refs.run258FullTracePath || "ppt-run2-58-full-vulca/trace_manifest.json")}}
              ${{detailBlock("Bad control trace", refs.run258BadTracePath || "ppt-run2-58-bad-without-product-capability-content/trace_manifest.json")}}
              ${{detailBlock("Full deck source", refs.run258FullDeckSourcePath || "ppt-run2-58-full-vulca/slides/deck-source.mjs")}}
              ${{detailBlock("Four-arm contact sheet", refs.run258FourArmSheetPath || "run2-58-four-arm-contact-sheet.png")}}
            </article>
            <article class="dataCard">
              <h4>What this experiment proves</h4>
              ${{detailBlock("Code-generated editable PPT", "Run 2.58 still generates editable PPTX with native code, not flat images.")}}
              ${{detailBlock("Data consumed", run258Quality.source_data_status || refs.run258SourceDataStatus)}}
              ${{detailBlock("Reader-question slides", run258Quality.full_slides_with_reader_question_answered)}}
              ${{detailBlock("Product terms visible", run258Quality.full_slides_with_code_generated_ppt_claim)}}
              ${{detailBlock("Bad control failure", run258Quality.bad_control_slides_without_run2_57_content)}}
            </article>
            <article class="dataCard">
              <h4>Open-source slide-code learning map</h4>
              ${{detailBlock("Research file", refs.run258OpenSourceResearchPath || "run2_58_open_source_slide_code_research.json")}}
              ${{detailBlock("Learning mode", run258OpenSourceUsePolicy.learning_mode || "runtime_learning_only")}}
              ${{detailBlock("do not copy source assets", run258OpenSourceUsePolicy.do_not_copy_source_assets)}}
              ${{detailBlock("Do not copy brand/template layouts", run258OpenSourceUsePolicy.do_not_copy_brand_or_template_layouts)}}
              ${{detailBlock("Rewrite boundary", run258OpenSourceUsePolicy.rewrite_as_vulca_native_artifact_tool_modules)}}
              ${{detailBlock("Reason", run258OpenSourceUsePolicy.reason)}}
            </article>
            <article class="dataCard">
              <h4>How to use GitHub code</h4>
              ${{detailBlock("Learn", "APIs, object models, theme/component boundaries, export paths, runtime motion boundaries, and RAG-to-layout planning.")}}
              ${{detailBlock("Do not copy", "source assets, demo decks, visual identity, brand marks, or template layouts.")}}
              ${{detailBlock("Vulca translation", "Convert learnings into design memory and native artifact-tool modules before code-generated editable PPT rendering.")}}
              ${{detailBlock("Next workflow", "Run 2.59 should prove each slide role used at least one concrete code-pattern memory record.")}}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Open-source references</h4><p>PptxGenJS, Slidev, Marp, reveal.js, and SlideCoder are references for code patterns and workflow structure. Use them to learn implementation patterns; do not copy source assets, demo decks, or template layouts.</p></div>
          <div class="dataGrid">${{run258OpenSourceCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Next data/workflow repair: Run 2.59 content-aware composition compiler</h3><p>Run 2.59 fixes the current failure mode: content_thickness_and_layout_module_memory_not_bound_before_native_ppt_drawing. It does not create a new PPT deck; it defines how content burden, layout capacity, and the public slide / trace viewer split must be compiled before Run 2.60 native drawing.</p></div><span class="pill" title="${{escapeHtml(refs.run259ResultStatus || "missing")}}">${{escapeHtml(refs.run259ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run 2.59 compiler result</h4>
              ${{detailBlock("Result", refs.run259ResultPath || "run2_59_content_aware_composition_compiler_result.json")}}
              ${{detailBlock("Target layer", run259Quality.target_layer || refs.run259TargetLayer)}}
              ${{detailBlock("Failure mode fixed", run259Quality.fixes_failure_mode || refs.run259FailureMode)}}
              ${{detailBlock("Creates new PPT deck", run259GenerationBoundary.creates_new_ppt_deck)}}
              ${{detailBlock("Latest generated run", run259GenerationBoundary.latest_generated_run_id || "2.58")}}
              ${{detailBlock("Next required action", run259Result.next_required_action || "run2_60_generate_four_arm_ppt_consuming_run2_59_composition_compiler")}}
            </article>
            <article class="dataCard">
              <h4>Compiler artifacts</h4>
              ${{detailBlock("Content contracts", refs.run259ContentContractsPath || "run2_59_content_composition_contracts.json")}}
              ${{detailBlock("Layout capacity model", refs.run259LayoutCapacityPath || "run2_59_layout_capacity_model.json")}}
              ${{detailBlock("Content to layout selector", refs.run259ContentSelectorPath || "run2_59_content_to_layout_selector.json")}}
              ${{detailBlock("Public surface trace policy", refs.run259TracePolicyPath || "run2_59_public_surface_trace_policy.json")}}
              ${{detailBlock("Composition workflow gates", refs.run259WorkflowGatesPath || "run2_59_composition_workflow_gates.json")}}
            </article>
            <article class="dataCard">
              <h4>public slide / trace viewer split</h4>
              ${{detailBlock("Policy id", run259TracePolicy.policy_id)}}
              ${{detailBlock("Public allowed", run259PublicSurface.allowed_content)}}
              ${{detailBlock("Public forbidden", run259PublicSurface.forbidden_content)}}
              ${{detailBlock("Viewer allowed", run259TraceSurface.allowed_content)}}
              ${{detailBlock("Visual requirement", run259PublicSurface.visual_requirement)}}
            </article>
            <article class="dataCard">
              <h4>Run 2.60 consumer contract</h4>
              ${{detailBlock("Run", run259Next.run_id || "2.60")}}
              ${{detailBlock("Required trace fields", run259Next.required_trace_fields)}}
              ${{detailBlock("Bad control arm", run259Next.bad_control_arm || "bad_run2_58_without_run2_59_composition_compiler")}}
              ${{detailBlock("Full arm pass status", run259Next.full_arm_pass_status || "run2_59_composition_compiler_consumed_before_native_ppt_drawing")}}
              ${{detailBlock("Next action", run259Result.next_required_action || "run2_60_generate_four_arm_ppt_consuming_run2_59_composition_compiler")}}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Content composition contracts</h4><p>${{escapeHtml(refs.run259ContentCompositionStatus)}}. Each role now separates public claim, proof object, evidence chips, trace-only details, speaker note, and visible word budget.</p></div>
          <div class="dataGrid">${{run259ContractCards}}</div>
          <div class="dataBandSubhead"><h4>Layout capacity model</h4><p>${{escapeHtml(refs.run259LayoutCapacityStatus)}}. Run 2.15 layout modules now have max title lines, visible word budgets, evidence chip limits, primary object area requirements, and forbidden patterns.</p></div>
          <div class="dataGrid">${{run259CapacityCards}}</div>
          <div class="dataBandSubhead"><h4>Content-to-layout selector</h4><p>${{escapeHtml(refs.run259ContentSelectorStatus)}}. Run 2.60 must select layout from role, content burden, proof object type, and rhythm position before native PPT drawing.</p></div>
          <div class="dataGrid">${{run259SelectorCards}}</div>
          <div class="dataBandSubhead"><h4>Composition workflow gates</h4><p>${{escapeHtml(refs.run259WorkflowGateStatus)}}. Bad controls must fail if they reuse Run 2.58 renderers without the 2.59 compiler trace fields.</p></div>
          <div class="dataGrid">${{run259GateCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Latest data/workflow repair: Run 2.57 product capability content layer</h3><p>Run 2.57 is data/workflow-only. It adds product capability memory, slide message contracts, and content workflow gates. Next generated run 2.58 must consume this layer so it can explain the product instead of only varying the visual surface.</p></div><span class="pill" title="${{escapeHtml(refs.run257ResultStatus || "missing")}}">${{escapeHtml(refs.run257ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run 2.57 result</h4>
              ${{detailBlock("Result", refs.run257ResultPath || "run2_57_product_capability_content_result.json")}}
              ${{detailBlock("Target layer", run257Quality.target_layer || refs.run257TargetLayer)}}
              ${{detailBlock("Source data status", run257Quality.source_data_status || refs.run257SourceDataStatus)}}
              ${{detailBlock("Generated PPT", "No PPT deck generated in Run 2.57")}}
              ${{detailBlock("Boundary", run257GenerationBoundary.reason || "Data/workflow-only, no new PPT deck")}}
              ${{detailBlock("Latest generated run", run257GenerationBoundary.latest_generated_run_id || "2.56")}}
              ${{detailBlock("Next generated run", run257NextGeneratedRunContract.run_id || "2.58")}}
            </article>
            <article class="dataCard">
              <h4>Content artifacts</h4>
              ${{detailBlock("Product capability memory", refs.run257ProductCapabilityPath || "run2_57_product_capability_memory.json")}}
              ${{detailBlock("Slide message contracts", refs.run257SlideMessageContractsPath || "run2_57_slide_message_contracts.json")}}
              ${{detailBlock("Content workflow gates", refs.run257ContentWorkflowGatesPath || "run2_57_content_workflow_gates.json")}}
              ${{detailBlock("Output chain", run257Outputs)}}
            </article>
            <article class="dataCard">
              <h4>What it fixes</h4>
              ${{detailBlock("Product capability", run257RepairContract["product capability"])}}
              ${{detailBlock("Slide message contracts", run257RepairContract["slide message contracts"])}}
              ${{detailBlock("Content workflow gates", run257RepairContract["content workflow gates"])}}
              ${{detailBlock("Counts", run257Counts)}}
            </article>
            <article class="dataCard">
              <h4>Next generated proof</h4>
              ${{detailBlock("Run", run257NextGeneratedRunContract.run_id || "2.58")}}
              ${{detailBlock("Must consume", run257NextGeneratedRunContract.must_consume)}}
              ${{detailBlock("Bad control", run257NextGeneratedRunContract.bad_control_arm || "bad_run2_56_without_product_capability_content")}}
              ${{detailBlock("Required trace fields", run257NextGeneratedRunContract.required_trace_fields)}}
              ${{detailBlock("Full arm status", run257NextGeneratedRunContract.full_arm_pass_status)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.56 result", run257Inputs.run2_56_result || "run2_56_role_renderer_split_rerun_result.json")}}
              ${{detailBlock("Run 2.56 full trace", run257Inputs.run2_56_full_trace || "ppt-run2-56-full-vulca/trace_manifest.json")}}
              ${{detailBlock("Usecase bank", run257Inputs.commercial_usecase_bank || "commercial_usecase_bank.json")}}
              ${{detailBlock("Sources", run257Inputs.sources || "sources.json")}}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Product capability memory</h4><p>${{escapeHtml(refs.run257ProductCapabilityStatus)}}. These records explain the actual product: input, understanding, code-generated editable PPT generation, comparison, verification, output, and repair loop.</p></div>
          <div class="dataGrid">${{run257CapabilityCards}}</div>
          <div class="dataBandSubhead"><h4>Product logic relations</h4><p>These relations make the product mechanism visible instead of leaving it as a generic design claim.</p></div>
          <div class="dataGrid">${{run257LogicCards}}</div>
          <div class="dataBandSubhead"><h4>Competitor boundaries</h4><p>These records force the next deck to explain how Vulca differs from prompt-only generation, image generation, templates, design editors, and office-native copilots.</p></div>
          <div class="dataGrid">${{run257CompetitorCards}}</div>
          <div class="dataBandSubhead"><h4>Slide message contracts</h4><p>${{escapeHtml(refs.run257SlideMessageContractStatus)}}. Every role must answer a reader question with concrete product terms and a visible product object.</p></div>
          <div class="dataGrid">${{run257MessageCards}}</div>
          <div class="dataBandSubhead"><h4>Content workflow gates</h4><p>${{escapeHtml(refs.run257ContentWorkflowGateStatus)}}. Generic claims, wrong output claims, and missing 2.57-to-2.58 handoff must fail before renderer execution.</p></div>
          <div class="dataGrid">${{run257GateCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Prior product-surface data/workflow repair</h3><p>Run 2.53 product-surface scene repair is data/workflow-only: it adds product surface scene memory, business visual evidence memory, and scene renderer workflow gates. It creates no PPT deck; Run 2.54 consumes this pack before native drawing.</p></div><span class="pill" title="${{escapeHtml(refs.run253ResultStatus || "missing")}}">${{escapeHtml(refs.run253ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run 2.53 repair pack</h4>
              ${{detailBlock("Result", refs.run253ResultPath || "run2_53_product_surface_scene_repair_result.json")}}
              ${{detailBlock("Product surface scenes", run253Outputs.product_surface_scene_memory || "run2_53_product_surface_scene_memory.json")}}
              ${{detailBlock("Business visual evidence", run253Outputs.business_visual_evidence_memory || "run2_53_business_visual_evidence_memory.json")}}
              ${{detailBlock("Scene renderer workflow gates", run253Outputs.scene_renderer_workflow_gates || "run2_53_scene_renderer_workflow_gates.json")}}
              ${{detailBlock("Boundary", "Data/workflow-only, no new PPT deck")}}
              ${{detailBlock("Target layer", run253Result.target_layer || "product_surface_scene_and_business_visual_evidence_repair")}}
              ${{detailBlock("Next required action", run253Result.next_required_action || "consume_run2_53_before_run2_54_four_arm_rerun")}}
            </article>
            <article class="dataCard">
              <h4>What it fixes</h4>
              ${{detailBlock("Product surface scene", run253RepairContract["product surface scene"])}}
              ${{detailBlock("Business visual evidence", run253RepairContract["business visual evidence"])}}
              ${{detailBlock("Scene renderer gates", run253RepairContract["scene renderer gates"])}}
              ${{detailBlock("Records", run253Counts)}}
              ${{detailBlock("Visual validation", "Deferred to Run 2.54 generated rerun")}}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Product surface scene memory</h4><p>${{escapeHtml(refs.run253ProductSurfaceSceneStatus)}}. Each slide role must render an inspectable product or business object, not a generic geometric diagram.</p></div>
          <div class="dataGrid">${{run253SceneCards}}</div>
          <div class="dataBandSubhead"><h4>Business visual evidence memory</h4><p>${{escapeHtml(refs.run253BusinessVisualEvidenceStatus)}}. Each record names the observable business object and the reader question the visual must answer.</p></div>
          <div class="dataGrid">${{run253EvidenceCards}}</div>
          <div class="dataBandSubhead"><h4>Scene renderer workflow gates</h4><p>${{escapeHtml(refs.run253SceneRendererGateStatus)}}. The next generated full arm must bind these gates before native drawing; the bad control must fail without them.</p></div>
          <div class="dataGrid">${{run253GateCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Prior data/workflow repair</h3><p>Run 2.51 remains the prior data/workflow repair layer. Run 2.51 is data/workflow-only: it prepares editorial public copy, semantic shape text sockets, and renderer archetype workflow gates. It creates no PPT deck; visual validation waits for the next generated rerun that consumes it.</p></div><span class="pill" title="${{escapeHtml(refs.run251ResultStatus || "missing")}}">${{escapeHtml(refs.run251ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run 2.51 repair pack</h4>
              ${{detailBlock("Result", refs.run251ResultPath || "run2_51_editorial_shape_text_repair_result.json")}}
              ${{detailBlock("Editorial copy", "run2_51_editorial_copy_memory.json")}}
              ${{detailBlock("Shape text sockets", "run2_51_shape_text_socket_memory.json")}}
              ${{detailBlock("Renderer archetype workflow gates", "run2_51_renderer_archetype_workflow_gates.json")}}
              ${{detailBlock("Boundary", "Data/workflow-only, no new PPT deck")}}
              ${{detailBlock("Target layer", run251Result.target_layer || "editorial_copy_and_shape_text_socket_repair")}}
              ${{detailBlock("Next required action", run251Result.next_required_action || "consume_run2_51_before_run2_52_four_arm_rerun")}}
            </article>
            <article class="dataCard">
              <h4>What it fixes</h4>
              ${{detailBlock("Editorial copy", run251Result.repair_contract?.["editorial copy"])}}
              ${{detailBlock("Shape text sockets", run251Result.repair_contract?.["shape text sockets"])}}
              ${{detailBlock("Renderer archetypes", run251Result.repair_contract?.["renderer archetypes"])}}
              ${{detailBlock("Visual validation", "Deferred to generated rerun")}}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Editorial copy memory</h4><p>${{escapeHtml(refs.run251CopyMemoryStatus)}}. Raw evidence is rewritten into short public-facing display copy with word and character budgets.</p></div>
          <div class="dataGrid">${{run251CopyCards}}</div>
          <div class="dataBandSubhead"><h4>Shape text socket memory</h4><p>${{escapeHtml(refs.run251SocketMemoryStatus)}}. Each role has a dominant archetype, semantic primitives, and text sockets before generation.</p></div>
          <div class="dataGrid">${{run251SocketCards}}</div>
          <div class="dataBandSubhead"><h4>Renderer archetype workflow gates</h4><p>${{escapeHtml(refs.run251GateStatus)}}. The next generated full arm must bind these gates, while the bad control must fail without them.</p></div>
          <div class="dataGrid">${{run251GateCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.49 readability/content density repair</h3><p>Run 2.49 remains the earlier readability/content density/editorial renderer repair pack; Run 2.50 is the generated proof that consumes it and exposes the consumption in trace.</p></div><span class="pill" title="${{escapeHtml(refs.run249ResultStatus || "missing")}}">${{escapeHtml(refs.run249ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run 2.49 repair pack</h4>
              ${{detailBlock("Run", "Run 2.49 readability/content density/editorial renderer repair")}}
              ${{detailBlock("Boundary", "Data-only, no new PPT deck")}}
              ${{detailBlock("Target layer", run249Result.target_layer || "readability_content_density_and_editorial_renderer_repair")}}
              ${{detailBlock("Next required action", run249Result.next_required_action || "consume_run2_49_before_run2_50_four_arm_rerun")}}
            </article>
            <article class="dataCard">
              <h4>What it fixes</h4>
              ${{detailBlock("Readability", run249RepairContract.readability)}}
              ${{detailBlock("Content evidence density", run249RepairContract["content evidence density"])}}
              ${{detailBlock("Editorial renderer", run249RepairContract["editorial renderer"])}}
              ${{detailBlock("Release boundary", run249Result.release_boundary)}}
            </article>
            <article class="dataCard">
              <h4>Artifacts to inspect</h4>
              ${{detailBlock("Readability memory", run249Outputs.readability_memory || "run2_49_readability_memory.json")}}
              ${{detailBlock("Content evidence density memory", run249Outputs.content_evidence_density_memory || "run2_49_content_evidence_density_memory.json")}}
              ${{detailBlock("Editorial renderer workflow gates", run249Outputs.editorial_renderer_workflow_gates || "run2_49_editorial_renderer_workflow_gates.json")}}
            </article>
            <article class="dataCard">
              <h4>Visual/data split</h4>
              ${{detailBlock("Latest generated proof", "Run 2.56")}}
              ${{detailBlock("Source generated baseline", "Run 2.55")}}
              ${{detailBlock("Reason", "Run 2.51 and Run 2.53 are data-workflow layers; Run 2.55 proved text-shape integration; Run 2.56 tests whether each role gets a distinct renderer instead of a reused template.")}}
              ${{detailBlock("Proof result", "Run 2.56 binds Run 2.55 generated trace before native role-renderer redraw.")}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Why 2.8 still looks close to 2.7</h3><p>The current bottleneck is visual primitive quality, not trace plumbing.</p></div></div>
          <div class="dataGrid">${{diagnosis}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.24 single-usecase content + visual evidence</h3><p>Data/workflow-only layer: locks one commercial story and adds visible business content plus native visual evidence slots before the next generated rerun. It does not create a PPT deck or advance to Run 3.0.</p></div><span class="pill">${{escapeHtml(refs.run224ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Selected usecase</h4>
              ${{detailBlock("Usecase id", run224SelectedUsecase.id)}}
              ${{detailBlock("Audience", run224SelectedUsecase.audience)}}
              ${{detailBlock("Business decision", run224SelectedUsecase.business_decision)}}
              ${{detailBlock("Deck mission", run224SelectedUsecase.deck_mission)}}
              ${{detailBlock("QA probe", run224SelectedUsecase.qa_probe)}}
            </article>
            <article class="dataCard">
              <h4>Story policy</h4>
              ${{detailBlock("Single primary usecase", run224StoryPolicy.single_primary_usecase)}}
              ${{detailBlock("Supporting references only", run224StoryPolicy.supporting_references_only)}}
              ${{detailBlock("Forbid cross-case primary story", run224StoryPolicy.forbid_cross_case_primary_story)}}
              ${{detailBlock("Reason", run224StoryPolicy.reason)}}
            </article>
            <article class="dataCard">
              <h4>Run boundary</h4>
              ${{detailBlock("Creates new PPT deck", run224Result.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run224Result.public_ready)}}
              ${{detailBlock("Artifact counts", run224Result.artifact_counts)}}
              ${{detailBlock("Output chain", run224OutputChain)}}
              ${{detailBlock("Next action", run224Result.next_required_action)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.24 content memory</h3><p>${{escapeHtml(refs.run224ContentMemoryStatus)}}. Each slide role now has concrete headline, supporting line, business proof points, visual evidence slot ids, and content density gates.</p></div><span class="pill">${{(refs.run224ContentMemory || []).length}} records</span></div>
          <div class="dataGrid">${{run224ContentMemory}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.24 visual evidence asset memory</h3><p>${{escapeHtml(refs.run224VisualAssetStatus)}}. These are native-PPT visual evidence instructions, not copied screenshots, video frames, source layouts, or brand marks.</p></div><span class="pill">${{(refs.run224VisualAssets || []).length}} assets</span></div>
          <div class="dataGrid">${{run224VisualAssets}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.24 content/visual workflow gates</h3><p>${{escapeHtml(refs.run224WorkflowGateStatus)}}. These gates must be consumed before the next native PPT generation pass.</p></div><span class="pill">${{(refs.run224WorkflowGates || []).length}} gates</span></div>
          <div class="dataGrid">${{run224WorkflowGates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.25 single-usecase generated rerun</h3><p>Generated four-arm rerun that consumes Run 2.24 content memory, visual evidence asset memory, and workflow gates before native PPT code generation. It stays in the same five-layer loop and does not advance to Run 3.0.</p></div><span class="pill">${{escapeHtml(refs.run225ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Selected usecase", run225Result.selected_usecase_id)}}
              ${{detailBlock("Best internal arm", run225Rerun.best_internal_arm)}}
              ${{detailBlock("Verdict", run225Rerun.best_internal_arm_verdict)}}
              ${{detailBlock("Four-arm sheet", run225Rerun.combined_contact_sheet)}}
              ${{detailBlock("Full-skill series", run225Rerun.full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Content memory", run225Inputs.content_memory)}}
              ${{detailBlock("Visual evidence asset memory", run225Inputs.visual_evidence_asset_memory)}}
              ${{detailBlock("Content/visual workflow gates", run225Inputs.content_visual_workflow_gates)}}
              ${{detailBlock("Stage policy", run225Result.stage_policy)}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Negative control", run225Control.bad_content_visual_memory)}}
              ${{detailBlock("Prompt only", run225Control.prompt_only)}}
              ${{detailBlock("Run 1.5", run225Control.run1_5_skill)}}
              ${{detailBlock("Public ready", run225Result.public_ready)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.26 visual module quality audit</h3><p>Audit-only layer over Run 2.25 full skill output. It checks layout_geometry, content_density, visual_evidence_visibility, composition_hierarchy, and climax_impact before deciding what to thicken next.</p></div><span class="pill">${{escapeHtml(refs.run226VisualModuleAuditStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Quality summary</h4>
              ${{detailBlock("Module quality gate", run226Summary.module_quality_gate)}}
              ${{detailBlock("Public release gate", run226Summary.public_release_gate)}}
              ${{detailBlock("roles_with_visible_layout_defects", run226Summary.roles_with_visible_layout_defects)}}
              ${{detailBlock("roles_with_compressed_proof_surface", run226Summary.roles_with_compressed_proof_surface)}}
              ${{detailBlock("Top next module", run226Summary.top_next_module_to_thicken || "drawRun225ContentEvidenceSurface")}}
              ${{detailBlock("Reason", run226Summary.reason)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Source generated run", run226Audit.source_generated_run)}}
              ${{detailBlock("Trace manifest", (run226Audit.input_chain || {{}}).full_arm_trace_manifest)}}
              ${{detailBlock("Layout directory", (run226Audit.input_chain || {{}}).full_arm_layout_dir)}}
              ${{detailBlock("no_new_deck_proof", run226NoNewDeckProof)}}
              ${{detailBlock("Stage policy", run226Audit.stage_policy)}}
              ${{detailBlock("Creates new PPT deck", run226Audit.creates_new_ppt_deck)}}
              ${{detailBlock("Next required action", run226Audit.next_required_action)}}
            </article>
          </div>
          <div class="dataGrid">${{run226Recommendations}}</div>
          <div class="dataGrid">${{run226RoleRecords}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.27 content surface thickening rerun</h3><p>Generated four-arm rerun that consumes the Run 2.26 audit target before native PPT code generation. The visual delta is narrow: replace drawRun225ContentEvidenceSurface with drawRun227ContentEvidenceSurface so setup, contrast, and close can show three proof rows without compressed proof-surface carryover.</p></div><span class="pill">${{escapeHtml(refs.run227ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Source audit run", run227Result.source_audit_run_id)}}
              ${{detailBlock("Best internal arm", run227Rerun.best_internal_arm)}}
              ${{detailBlock("Verdict", run227Rerun.best_internal_arm_verdict)}}
              ${{detailBlock("Four-arm sheet", run227Rerun.combined_contact_sheet)}}
              ${{detailBlock("Full-skill series", run227Rerun.full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Content memory", run227Inputs.content_memory)}}
              ${{detailBlock("Visual evidence asset memory", run227Inputs.visual_evidence_asset_memory)}}
              ${{detailBlock("Content/visual workflow gates", run227Inputs.content_visual_workflow_gates)}}
              ${{detailBlock("Visual module quality audit", run227Inputs.visual_module_quality_audit)}}
              ${{detailBlock("Stage policy", run227Result.stage_policy)}}
            </article>
            <article class="dataCard">
              <h4>Quality delta</h4>
              ${{detailBlock("Target module", run227Delta.target_module)}}
              ${{detailBlock("Replacement module", run227Delta.replacement_module || "drawRun227ContentEvidenceSurface")}}
              ${{detailBlock("Roles compressed before", run227Delta.roles_with_compressed_proof_surface_before)}}
              ${{detailBlock("Roles compressed after", run227Delta.roles_with_compressed_proof_surface_after)}}
              ${{detailBlock("Required visible proof rows", run227Delta.required_visible_proof_points_per_target_role)}}
              ${{detailBlock("Visual quality boundary", run227Result.visual_quality_boundary)}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Negative control", run227Control.bad_surface_thickening_memory)}}
              ${{detailBlock("Prompt only", run227Control.prompt_only)}}
              ${{detailBlock("Run 1.5", run227Control.run1_5_skill)}}
              ${{detailBlock("Public ready", run227Result.public_ready)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.28 evidence-chain rerun</h3><p>Generated four-arm rerun that consumes the Run 2.28 evidence-chain view model before native PPT code generation. This makes the data learning path visible: source evidence -> extracted design rule -> workflow decision -> generated slide surface.</p></div><span class="pill">${{escapeHtml(refs.run228ResultStatus || refs.run228EvidenceChainStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Evidence chain status", refs.run228EvidenceChainStatus)}}
              ${{detailBlock("Best internal arm", run228Rerun.best_internal_arm)}}
              ${{detailBlock("Verdict", run228Rerun.best_internal_arm_verdict)}}
              ${{detailBlock("Four-arm sheet", run228Rerun.combined_contact_sheet)}}
              ${{detailBlock("Full-skill series", run228Rerun.full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Evidence chain view model", run228Inputs.evidence_chain_view_model || "run2_28_evidence_chain_view_model.json")}}
              ${{detailBlock("Content memory", run228Inputs.content_memory)}}
              ${{detailBlock("Visual evidence asset memory", run228Inputs.visual_evidence_asset_memory)}}
              ${{detailBlock("Content/visual workflow gates", run228Inputs.content_visual_workflow_gates)}}
              ${{detailBlock("Prior rerun result", run228Inputs.prior_rerun_result)}}
            </article>
            <article class="dataCard">
              <h4>Evidence-chain delta</h4>
              ${{detailBlock("Chain order", run228Delta.chain_order || ["source evidence", "extracted design rule", "workflow decision", "generated slide surface"])}}
              ${{detailBlock("Replacement focus", run228Delta.replacement_focus)}}
              ${{detailBlock("Visible chain steps", run228Delta.required_visible_chain_steps_per_full_slide)}}
              ${{detailBlock("Public ready", run228Result.public_ready)}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Negative control", run228Control.bad_evidence_chain_memory)}}
              ${{detailBlock("Prompt only", run228Control.prompt_only)}}
              ${{detailBlock("Run 1.5", run228Control.run1_5_skill)}}
              ${{detailBlock("Stage policy", run228Result.stage_policy || run228EvidenceChain.stage_policy)}}
            </article>
          </div>
          <div class="dataGrid">${{run228ChainCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.29 presentation-synthesis rerun</h3><p>Generated four-arm rerun that consumes Run 2.29 presentation synthesis memory, the Run 2.28 evidence-chain view model, Run 2.24 content/visual/workflow memory, and the Run 2.28 rerun result before native PPT code generation. This changes the public slide surface from a four-column audit table into a presentation-first surface with a compressed evidence spine.</p></div><span class="pill">${{escapeHtml(refs.run229ResultStatus || refs.run229SynthesisMemoryStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Synthesis memory status", refs.run229SynthesisMemoryStatus)}}
              ${{detailBlock("Best internal arm", run229Rerun.best_internal_arm)}}
              ${{detailBlock("Verdict", run229Rerun.best_internal_arm_verdict)}}
              ${{detailBlock("Four-arm sheet", run229Rerun.combined_contact_sheet)}}
              ${{detailBlock("Full-skill series", run229Rerun.full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Presentation synthesis memory", run229Inputs.presentation_synthesis_memory || "run2_29_presentation_synthesis_memory.json")}}
              ${{detailBlock("Evidence chain view model", run229Inputs.evidence_chain_view_model || "run2_28_evidence_chain_view_model.json")}}
              ${{detailBlock("Content memory", run229Inputs.content_memory)}}
              ${{detailBlock("Visual evidence asset memory", run229Inputs.visual_evidence_asset_memory)}}
              ${{detailBlock("Content/visual workflow gates", run229Inputs.content_visual_workflow_gates)}}
              ${{detailBlock("Prior rerun result", run229Inputs.prior_rerun_result || "run2_28_evidence_chain_rerun_result.json")}}
            </article>
            <article class="dataCard">
              <h4>Surface policy</h4>
              ${{detailBlock("Primary reader experience", run229Policy.primary_reader_experience || "presentation-first surface")}}
              ${{detailBlock("Secondary reviewer experience", run229Policy.secondary_reviewer_experience || "compressed evidence spine")}}
              ${{detailBlock("Forbidden primary surface", run229Policy.forbidden_primary_surface || "four-column audit table")}}
              ${{detailBlock("Trace mode", (run229SynthesisMemory.viewer_contract || {{}}).trace_surface_mode || "manifest_and_html_viewer_full_chain_visible")}}
            </article>
            <article class="dataCard">
              <h4>Presentation-synthesis delta</h4>
              ${{detailBlock("Replacement focus", run229Delta.replacement_focus)}}
              ${{detailBlock("Primary surface mode", run229Delta.primary_surface_mode || "presentation-first surface")}}
              ${{detailBlock("Secondary surface mode", run229Delta.secondary_surface_mode || "compressed evidence spine")}}
              ${{detailBlock("Forbidden primary surface", run229Delta.forbidden_primary_surface || "four-column audit table")}}
              ${{detailBlock("Visible chain steps", run229Delta.required_visible_chain_steps_per_full_slide)}}
              ${{detailBlock("Public ready", run229Result.public_ready)}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Negative control", run229Control.bad_presentation_synthesis_memory)}}
              ${{detailBlock("Prompt only", run229Control.prompt_only)}}
              ${{detailBlock("Run 1.5", run229Control.run1_5_skill)}}
              ${{detailBlock("Stage policy", run229Result.stage_policy || run229SynthesisMemory.stage_policy)}}
            </article>
          </div>
          <div class="dataGrid">${{run229RecordCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.30 presentation synthesis audit</h3><p>Audit-only layer over Run 2.29. It creates no new PPT deck; it checks whether the Run 2.28 four-column audit table was demoted into a secondary compressed evidence spine, whether the full chain stayed preserved in trace, and which layer should be thickened before Run 2.31.</p></div><span class="pill">${{escapeHtml(refs.run230AuditStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Audit boundary</h4>
              ${{detailBlock("Source generated run", run230Audit.source_generated_run)}}
              ${{detailBlock("Comparison baseline run", run230Audit.comparison_baseline_run)}}
              ${{detailBlock("Creates new PPT deck", run230Audit.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run230Audit.public_ready)}}
              ${{detailBlock("No-new-deck status", run230NoNewDeck.status)}}
            </article>
            <article class="dataCard">
              <h4>Trace closure</h4>
              ${{detailBlock("Full arm", run230TraceFull.arm_id)}}
              ${{detailBlock("Synthesis records selected", run230TraceFull.presentation_synthesis_records_selected)}}
              ${{detailBlock("Compressed spine modules called", run230TraceFull.compressed_evidence_spine_modules_called)}}
              ${{detailBlock("Run 2.28 chain fields preserved", run230TraceFull.run2_28_chain_fields_preserved)}}
              ${{detailBlock("Bad-control leaks", run230TraceBad.presentation_synthesis_fields_leaked)}}
            </article>
            <article class="dataCard">
              <h4>2.28 -> 2.29 comparison</h4>
              ${{detailBlock("audit_table_demoted_to_secondary_spine", run230Comparison.audit_table_demoted_to_secondary_spine)}}
              ${{detailBlock("full_chain_preserved_in_trace", run230Comparison.full_chain_preserved_in_trace)}}
              ${{detailBlock("Primary surface delta", run230Comparison.primary_surface_delta)}}
              ${{detailBlock("Baseline full arm", run230Comparison.baseline_full_arm_id)}}
              ${{detailBlock("Current full arm", run230Comparison.current_full_arm_id)}}
            </article>
            <article class="dataCard">
              <h4>Quality summary</h4>
              ${{detailBlock("presentation_synthesis_gate", run230Summary.presentation_synthesis_gate)}}
              ${{detailBlock("Public release gate", run230Summary.public_release_gate)}}
              ${{detailBlock("Top next layer", run230Summary.top_next_layer_to_thicken || "spine_readability_and_climax_consistency")}}
              ${{detailBlock("Dense spine roles", run230Summary.roles_with_dense_spine_text)}}
              ${{detailBlock("Climax style-shift roles", run230Summary.roles_with_climax_style_shift)}}
            </article>
          </div>
          <div class="dataGrid">${{run230RoleCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.31 spine/climax repair rerun</h3><p>Generated four-arm rerun that consumes the Run 2.30 presentation synthesis audit before native PPT code generation. The repair is narrow: drawRun231ReadableEvidenceSpine raises the evidence-spine readability target, and drawRun231HeroProofScene normalizes the climax into a shared light editorial frame.</p></div><span class="pill">${{escapeHtml(refs.run231ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Source audit run", run231Result.source_audit_run_id)}}
              ${{detailBlock("Best internal arm", run231Rerun.best_internal_arm)}}
              ${{detailBlock("Verdict", run231Rerun.best_internal_arm_verdict)}}
              ${{detailBlock("Four-arm sheet", run231Rerun.combined_contact_sheet)}}
              ${{detailBlock("Full-skill series", run231Rerun.full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Presentation synthesis audit", run231Inputs.presentation_synthesis_audit || "run2_30_presentation_synthesis_audit.json")}}
              ${{detailBlock("Presentation synthesis memory", run231Inputs.presentation_synthesis_memory || "run2_29_presentation_synthesis_memory.json")}}
              ${{detailBlock("Evidence chain view model", run231Inputs.evidence_chain_view_model || "run2_28_evidence_chain_view_model.json")}}
              ${{detailBlock("Content memory", run231Inputs.content_memory)}}
              ${{detailBlock("Visual evidence asset memory", run231Inputs.visual_evidence_asset_memory)}}
              ${{detailBlock("Content/visual workflow gates", run231Inputs.content_visual_workflow_gates)}}
              ${{detailBlock("Prior rerun result", run231Inputs.prior_rerun_result || "run2_29_presentation_synthesis_rerun_result.json")}}
            </article>
            <article class="dataCard">
              <h4>Quality delta</h4>
              ${{detailBlock("Target layer", run231Delta.target_layer || "spine_readability_and_climax_consistency")}}
              ${{detailBlock("Repair modules", run231Delta.repair_modules || ["drawRun231ReadableEvidenceSpine", "drawRun231HeroProofScene"])}}
              ${{detailBlock("Spine min font target", run231Delta.spine_min_font_size_target)}}
              ${{detailBlock("Climax style policy", run231Delta.climax_style_policy || "high_contrast_climax_with_shared_light_editorial_frame")}}
              ${{detailBlock("Replacement focus", run231Delta.replacement_focus)}}
              ${{detailBlock("Public ready", run231Result.public_ready)}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Negative control", run231Control.bad_spine_climax_repair_memory)}}
              ${{detailBlock("Prompt only", run231Control.prompt_only)}}
              ${{detailBlock("Run 1.5", run231Control.run1_5_skill)}}
              ${{detailBlock("Stage policy", run231Result.stage_policy)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.32 spine/climax repair audit</h3><p>Audit-only layer over Run 2.31. It creates no new PPT deck; it checks whether the Run 2.30 spine_readability_and_climax_consistency target is closed, then moves the next thickness target to main_surface_information_density_and_visual_evidence_realism.</p></div><span class="pill">${{escapeHtml(refs.run232AuditStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Audit boundary</h4>
              ${{detailBlock("Source generated run", run232Audit.source_generated_run)}}
              ${{detailBlock("Source audit run", run232Audit.source_audit_run)}}
              ${{detailBlock("Creates new PPT deck", run232Audit.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run232Audit.public_ready)}}
              ${{detailBlock("Stage policy", run232Audit.stage_policy)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.30 audit", run232Inputs.run2_30_presentation_synthesis_audit || "run2_30_presentation_synthesis_audit.json")}}
              ${{detailBlock("Run 2.31 result", run232Inputs.run2_31_spine_climax_repair_rerun_result || "run2_31_spine_climax_repair_rerun_result.json")}}
              ${{detailBlock("Full trace manifest", run232Inputs.run2_31_full_trace_manifest)}}
              ${{detailBlock("Bad trace manifest", run232Inputs.run2_31_bad_trace_manifest)}}
              ${{detailBlock("Full contact sheet", run232Inputs.run2_31_full_contact_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Repair verification</h4>
              ${{detailBlock("repair_target_closed", run232Repair.repair_target_closed)}}
              ${{detailBlock("Spine min target", run232Repair.spine_min_font_size_target)}}
              ${{detailBlock("Measured min spine", run232Repair.measured_min_spine_font_size)}}
              ${{detailBlock("Climax policy enforced", run232Repair.climax_style_policy_enforced)}}
              ${{detailBlock("Climax hero share", run232Repair.climax_hero_object_canvas_share)}}
            </article>
            <article class="dataCard">
              <h4>Trace closure</h4>
              ${{detailBlock("Full arm", run232TraceFull.arm_id)}}
              ${{detailBlock("Run 2.30 audit consumed slides", run232TraceFull.run2_30_audit_consumed_slides)}}
              ${{detailBlock("Repair execution status slides", run232TraceFull.repair_execution_status_slides)}}
              ${{detailBlock("Readable spine modules called", run232TraceFull.readable_evidence_spine_modules_called)}}
              ${{detailBlock("Bad-control repair leaks", run232TraceBad.repair_fields_leaked)}}
            </article>
            <article class="dataCard">
              <h4>Quality summary</h4>
              ${{detailBlock("Repair gate", run232Summary.repair_gate)}}
              ${{detailBlock("Public release gate", run232Summary.public_release_gate)}}
              ${{detailBlock("Closed target layers", run232Summary.closed_target_layers)}}
              ${{detailBlock("roles_with_low_visual_evidence_density", run232Summary.roles_with_low_visual_evidence_density)}}
              ${{detailBlock("Top next layer", run232Summary.top_next_layer_to_thicken || "main_surface_information_density_and_visual_evidence_realism")}}
            </article>
          </div>
          <div class="dataGrid">${{run232RoleCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.33 main-surface visual-evidence rerun</h3><p>Generated four-arm rerun that consumes the Run 2.32 spine/climax repair audit before native PPT code generation. The target layer is main_surface_information_density_and_visual_evidence_realism, implemented through drawRun233MainSurfaceEvidenceLayer and drawRun233VisualEvidenceStoryboard.</p></div><span class="pill">${{escapeHtml(refs.run233ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Source audit run", run233Result.source_audit_run_id)}}
              ${{detailBlock("Best internal arm", run233Rerun.best_internal_arm)}}
              ${{detailBlock("Verdict", run233Rerun.best_internal_arm_verdict)}}
              ${{detailBlock("Four-arm sheet", run233Rerun.combined_contact_sheet)}}
              ${{detailBlock("Full-skill series", run233Rerun.full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.32 spine/climax repair audit", run233Inputs.spine_climax_repair_audit || "run2_32_spine_climax_repair_audit.json")}}
              ${{detailBlock("Run 2.31 repair rerun", run233Inputs.spine_climax_repair_rerun_result || "run2_31_spine_climax_repair_rerun_result.json")}}
              ${{detailBlock("Run 2.30 presentation synthesis audit", run233Inputs.presentation_synthesis_audit || "run2_30_presentation_synthesis_audit.json")}}
              ${{detailBlock("Run 2.29 presentation synthesis memory", run233Inputs.presentation_synthesis_memory || "run2_29_presentation_synthesis_memory.json")}}
              ${{detailBlock("Evidence chain view model", run233Inputs.evidence_chain_view_model || "run2_28_evidence_chain_view_model.json")}}
              ${{detailBlock("Content memory", run233Inputs.content_memory)}}
              ${{detailBlock("Visual evidence asset memory", run233Inputs.visual_evidence_asset_memory)}}
              ${{detailBlock("Content/visual workflow gates", run233Inputs.content_visual_workflow_gates)}}
            </article>
            <article class="dataCard">
              <h4>Quality delta</h4>
              ${{detailBlock("Target layer", run233Delta.target_layer || "main_surface_information_density_and_visual_evidence_realism")}}
              ${{detailBlock("Repair modules", run233Delta.repair_modules || ["drawRun233MainSurfaceEvidenceLayer", "drawRun233VisualEvidenceStoryboard"])}}
              ${{detailBlock("Preserved modules", run233Delta.preserved_modules)}}
              ${{detailBlock("Visual evidence min target", run233Delta.visual_evidence_object_min_target)}}
              ${{detailBlock("Source repair target closed", run233Delta.source_repair_target_closed)}}
              ${{detailBlock("Replacement focus", run233Delta.replacement_focus)}}
              ${{detailBlock("Public ready", run233Result.public_ready)}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Negative control", run233Control.bad_main_surface_visual_evidence_memory)}}
              ${{detailBlock("Prompt only", run233Control.prompt_only)}}
              ${{detailBlock("Run 1.5", run233Control.run1_5_skill)}}
              ${{detailBlock("Stage policy", run233Result.stage_policy)}}
              ${{detailBlock("Release boundary", run233Result.release_boundary)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.34 main-surface visual-evidence audit</h3><p>Audit-only layer over Run 2.33. It creates no new PPT deck; it checks whether main_surface_visual_evidence_gate passes internally, then sends the next thickness target to usecase_specific_visual_evidence_asset_realism_and_editorial_composition in Run 2.35 data/workflow.</p></div><span class="pill">${{escapeHtml(refs.run234AuditStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Audit boundary</h4>
              ${{detailBlock("Source generated run", run234Audit.source_generated_run)}}
              ${{detailBlock("Source audit run", run234Audit.source_audit_run)}}
              ${{detailBlock("Creates new PPT deck", run234Audit.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run234Audit.public_ready)}}
              ${{detailBlock("Stage policy", run234Audit.stage_policy)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.33 result", run234Inputs.run2_33_rerun_result || "run2_33_main_surface_visual_evidence_rerun_result.json")}}
              ${{detailBlock("Run 2.32 audit", run234Inputs.run2_32_spine_climax_repair_audit || "run2_32_spine_climax_repair_audit.json")}}
              ${{detailBlock("Full trace manifest", run234Inputs.run2_33_full_trace_manifest)}}
              ${{detailBlock("Bad trace manifest", run234Inputs.run2_33_bad_trace_manifest)}}
              ${{detailBlock("Full contact sheet", run234Inputs.run2_33_full_contact_sheet)}}
              ${{detailBlock("Delivery validation", run234Inputs.run2_33_delivery_validation)}}
            </article>
            <article class="dataCard">
              <h4>Main-surface verification</h4>
              ${{detailBlock("source_audit_target", run234Verification.source_audit_target)}}
              ${{detailBlock("source_rerun_verdict", run234Verification.source_rerun_verdict)}}
              ${{detailBlock("visual_evidence_object_target_met", run234Verification.visual_evidence_object_target_met)}}
              ${{detailBlock("main_surface_modules_called_by_contract", run234Verification.main_surface_modules_called_by_contract)}}
              ${{detailBlock("delivery_gate", run234Verification.delivery_gate)}}
              ${{detailBlock("static_no_animation", run234Verification.static_no_animation)}}
              ${{detailBlock("human_review_required", run234Verification.human_review_required)}}
            </article>
            <article class="dataCard">
              <h4>Trace closure</h4>
              ${{detailBlock("Full arm", run234TraceFull.arm_id)}}
              ${{detailBlock("Run 2.32 audit consumed slides", run234TraceFull.run2_32_audit_consumed_slides)}}
              ${{detailBlock("Main-surface execution status slides", run234TraceFull.main_surface_execution_status_slides)}}
              ${{detailBlock("Main-surface layer modules called", run234TraceFull.main_surface_evidence_layer_modules_called)}}
              ${{detailBlock("Storyboard modules called", run234TraceFull.visual_evidence_storyboard_modules_called)}}
              ${{detailBlock("Bad-control main-surface leaks", run234TraceBad.main_surface_fields_leaked)}}
            </article>
            <article class="dataCard">
              <h4>Quality summary</h4>
              ${{detailBlock("main_surface_visual_evidence_gate", run234Summary.main_surface_visual_evidence_gate)}}
              ${{detailBlock("Public release gate", run234Summary.public_release_gate)}}
              ${{detailBlock("Closed target layers", run234Summary.closed_target_layers)}}
              ${{detailBlock("roles_with_weak_editorial_anchor", run234Summary.roles_with_weak_editorial_anchor)}}
              ${{detailBlock("roles_with_schematic_visual_evidence", run234Summary.roles_with_schematic_visual_evidence)}}
              ${{detailBlock("Top next layer", run234Summary.top_next_layer_to_thicken || "usecase_specific_visual_evidence_asset_realism_and_editorial_composition")}}
              ${{detailBlock("Next required action", run234Audit.next_required_action || "Run 2.35 data/workflow")}}
            </article>
          </div>
          <div class="dataGrid">${{run234RoleCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.35 visual evidence realism workflow</h3><p>Data/workflow-only layer after Run 2.34. It creates no new PPT deck; it converts the target usecase_specific_visual_evidence_asset_realism_and_editorial_composition into required realism memory, editorial composition memory, and workflow gates that Run 2.36 must consume before any native PPT rerun.</p></div><span class="pill">${{escapeHtml(refs.run235ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run boundary</h4>
              ${{detailBlock("Target layer", run235Result.target_layer || "usecase_specific_visual_evidence_asset_realism_and_editorial_composition")}}
              ${{detailBlock("Creates new PPT deck", run235Result.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run235Result.public_ready)}}
              ${{detailBlock("Public release gate", run235Result.public_release_gate)}}
              ${{detailBlock("Artifact counts", run235Result.artifact_counts)}}
              ${{detailBlock("Next action", run235Result.next_required_action || "consume_run2_35_visual_evidence_realism_workflow_before_run2_36_rerun")}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.34 audit", run235Inputs.main_surface_visual_evidence_audit || "run2_34_main_surface_visual_evidence_audit.json")}}
              ${{detailBlock("Content memory", run235Inputs.content_memory)}}
              ${{detailBlock("Visual evidence asset memory", run235Inputs.visual_evidence_asset_memory)}}
              ${{detailBlock("Sources", run235Inputs.sources)}}
              ${{detailBlock("Commercial usecase bank", run235Inputs.commercial_usecase_bank)}}
            </article>
            <article class="dataCard">
              <h4>Output chain</h4>
              ${{detailBlock("Visual evidence asset realism memory", run235Output.visual_evidence_asset_realism_memory || "run2_35_visual_evidence_asset_realism_memory.json")}}
              ${{detailBlock("Editorial composition memory", run235Output.editorial_composition_memory || "run2_35_editorial_composition_memory.json")}}
              ${{detailBlock("Visual evidence workflow gates", run235Output.visual_evidence_workflow_gates || "run2_35_visual_evidence_workflow_gates.json")}}
              ${{detailBlock("Result", "run2_35_visual_evidence_realism_workflow_result.json")}}
            </article>
            <article class="dataCard">
              <h4>Run 2.36 contract</h4>
              ${{detailBlock("Must consume before rerun", ["run2_35_visual_evidence_asset_realism_memory.json", "run2_35_editorial_composition_memory.json", "run2_35_visual_evidence_workflow_gates.json"])}}
              ${{detailBlock("Negative control rule", "bad arm may receive the usecase label, but not Run 2.35 memory ids, composition memory, or gate ids")}}
              ${{detailBlock("Quality contract", run235Quality)}}
              ${{detailBlock("Release boundary", run235Result.release_boundary)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.35 visual evidence asset realism memory</h3><p>${{escapeHtml(refs.run235RealismMemoryStatus)}}. Each Run 2.24 visual slot becomes a usecase-specific product or business state, not a generic block diagram or evidence token.</p></div><span class="pill">${{(refs.run235RealismMemory || []).length}} records</span></div>
          <div class="dataGrid">${{run235RealismMemory}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.35 editorial composition memory</h3><p>${{escapeHtml(refs.run235CompositionMemoryStatus)}}. Each role gets a first-read anchor object, hero canvas share target, typography/spacing obligations, and explicit forbidden schematic patterns.</p></div><span class="pill">${{(refs.run235CompositionMemory || []).length}} records</span></div>
          <div class="dataGrid">${{run235CompositionMemory}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.35 visual evidence workflow gates</h3><p>${{escapeHtml(refs.run235WorkflowGateStatus)}}. These are required-before-rerun gates for Run 2.36, including trace fields and negative-control probes.</p></div><span class="pill">${{(refs.run235WorkflowGates || []).length}} gates</span></div>
          <div class="dataGrid">${{run235WorkflowGates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.36 visual evidence realism rerun</h3><p>Generated four-arm rerun that consumes Run 2.35 visual evidence realism workflow before native PPT code generation. Target: usecase_specific_visual_evidence_asset_realism_and_editorial_composition.</p></div><span class="pill">${{escapeHtml(refs.run236ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Result", "run2_36_visual_evidence_realism_rerun_result.json")}}
              ${{detailBlock("Best internal arm", run236Rerun.best_internal_arm || "run2_36_full_visual_evidence_realism")}}
              ${{detailBlock("Verdict", run236Rerun.best_internal_arm_verdict || "usecase_specific_visual_evidence_asset_realism_and_editorial_composition_consumed_before_native_ppt_generation")}}
              ${{detailBlock("Four-arm sheet", run236Rerun.combined_contact_sheet || "run2-36-four-arm-contact-sheet.png")}}
              ${{detailBlock("Full-skill series", run236Rerun.full_skill_series_sheet || "run2-full-skill-series-horizontal.png")}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.34 audit", run236Inputs.main_surface_visual_evidence_audit || "run2_34_main_surface_visual_evidence_audit.json")}}
              ${{detailBlock("Run 2.33 prior rerun", run236Inputs.prior_main_surface_visual_evidence_rerun || "run2_33_main_surface_visual_evidence_rerun_result.json")}}
              ${{detailBlock("Run 2.35 workflow result", run236Inputs.visual_evidence_realism_workflow_result || "run2_35_visual_evidence_realism_workflow_result.json")}}
              ${{detailBlock("Run 2.35 realism memory", run236Inputs.visual_evidence_asset_realism_memory || "run2_35_visual_evidence_asset_realism_memory.json")}}
              ${{detailBlock("Run 2.35 composition memory", run236Inputs.editorial_composition_memory || "run2_35_editorial_composition_memory.json")}}
              ${{detailBlock("Run 2.35 workflow gates", run236Inputs.visual_evidence_workflow_gates || "run2_35_visual_evidence_workflow_gates.json")}}
            </article>
            <article class="dataCard">
              <h4>Quality delta</h4>
              ${{detailBlock("Target layer", run236Delta.target_layer || "usecase_specific_visual_evidence_asset_realism_and_editorial_composition")}}
              ${{detailBlock("Required modules", run236Delta.required_modules || ["drawRun236RealisticProductState", "drawRun236EditorialAnchorObject", "drawRun236RealismGateRibbon"])}}
              ${{detailBlock("Realism records", run236Delta.visual_evidence_asset_realism_records)}}
              ${{detailBlock("Composition records", run236Delta.editorial_composition_records)}}
              ${{detailBlock("Workflow gates", run236Delta.workflow_gates)}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Prompt-only arm", "ppt-run2-36-prompt-only")}}
              ${{detailBlock("Run 1.5 arm", "ppt-run2-36-run1-5-skill")}}
              ${{detailBlock("Full arm", "ppt-run2-36-full-vulca")}}
              ${{detailBlock("Bad memory arm", "ppt-run2-36-bad-visual-evidence-realism-memory")}}
              ${{detailBlock("Negative-control rule", run236Control.negative_control_rule || "bad arm may receive the usecase label, but not Run 2.35 realism ids, composition ids, gate ids, or execution status")}}
              ${{detailBlock("Release boundary", run236Result.release_boundary || "Do not advance to Run 3.0 before Run 2.36 is audited")}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.37 visual quality audit</h3><p>Audit-only layer over Run 2.36. It creates no new PPT deck; it explains why data consumption passes but design quality is still blocked. Root cause: visual_module_language_too_repetitive_and_card_like.</p></div><span class="pill">${{escapeHtml(refs.run237AuditStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Audit boundary</h4>
              ${{detailBlock("Result", "run2_37_visual_quality_audit.json")}}
              ${{detailBlock("Source generated run", run237Audit.source_generated_run)}}
              ${{detailBlock("Source data/workflow run", run237Audit.source_data_workflow_run)}}
              ${{detailBlock("Creates new PPT deck", run237Audit.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run237Audit.public_ready)}}
              ${{detailBlock("Stage policy", run237Audit.stage_policy)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.36 result", run237Inputs.run2_36_rerun_result || "run2_36_visual_evidence_realism_rerun_result.json")}}
              ${{detailBlock("Run 2.35 workflow result", run237Inputs.run2_35_visual_evidence_realism_workflow_result || "run2_35_visual_evidence_realism_workflow_result.json")}}
              ${{detailBlock("Full trace manifest", run237Inputs.run2_36_full_trace_manifest)}}
              ${{detailBlock("Bad trace manifest", run237Inputs.run2_36_bad_trace_manifest)}}
              ${{detailBlock("Four-arm contact sheet", run237Inputs.run2_36_four_arm_contact_sheet)}}
              ${{detailBlock("Full-skill series", run237Inputs.run2_full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Trace closure</h4>
              ${{detailBlock("Full arm", run237TraceFull.arm_id)}}
              ${{detailBlock("Run 2.35 consumed slides", run237TraceFull.run2_35_workflow_consumed_slides)}}
              ${{detailBlock("Realism ids bound slides", run237TraceFull.realism_ids_bound_slides)}}
              ${{detailBlock("Required Run 2.36 modules called", run237TraceFull.required_run236_modules_called_slides)}}
              ${{detailBlock("Bad-control Run 2.35 leaks", run237TraceBad.visual_evidence_realism_fields_leaked)}}
            </article>
            <article class="dataCard">
              <h4>Visual quality assessment</h4>
              ${{detailBlock("Data consumption gate", run237Assessment.data_consumption_gate)}}
              ${{detailBlock("Workflow proof gate", run237Assessment.workflow_proof_gate)}}
              ${{detailBlock("Design quality gate", run237Assessment.design_quality_gate)}}
              ${{detailBlock("Public video readiness", run237Assessment.public_video_readiness)}}
              ${{detailBlock("Root cause", run237Assessment.root_cause_primary || "visual_module_language_too_repetitive_and_card_like")}}
              ${{detailBlock("Repeated layout signature count", run237Assessment.repeated_layout_signature_count)}}
              ${{detailBlock("Unique layout signature count", run237Assessment.unique_layout_signature_count)}}
            </article>
            <article class="dataCard">
              <h4>Next data/workflow target</h4>
              ${{detailBlock("Top next layer", run237Assessment.top_next_layer_to_thicken || "public_video_grade_slide_direction_and_per_slide_visual_recipe")}}
              ${{detailBlock("roles_with_repetitive_card_layout", run237Assessment.roles_with_repetitive_card_layout)}}
              ${{detailBlock("roles_with_insufficient_public_aesthetic", run237Assessment.roles_with_insufficient_public_aesthetic)}}
              ${{detailBlock("Run 2.38 data/workflow", run237Audit.next_required_action || "build_run2_38_public_video_grade_visual_direction_memory_and_workflow_gates")}}
              ${{detailBlock("Delivery gate", run237Delivery.delivery_gate)}}
              ${{detailBlock("Static/no animation", run237Delivery.static_no_animation)}}
            </article>
          </div>
          <div class="dataGrid">${{run237RoleCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.38 public-video visual direction workflow</h3><p>Data/workflow-only layer after Run 2.37. It creates no new PPT deck; it turns public_video_grade_slide_direction_and_per_slide_visual_recipe into direction memory, per-slide recipes, and workflow gates that must_be_consumed_before_run2_39_four_arm_rerun.</p></div><span class="pill">${{escapeHtml(refs.run238ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run boundary</h4>
              ${{detailBlock("Result", "run2_38_public_video_visual_direction_workflow_result.json")}}
              ${{detailBlock("Source audit run", run238Result.source_audit_run)}}
              ${{detailBlock("Source generated run", run238Result.source_generated_run)}}
              ${{detailBlock("Target layer", run238Result.target_layer || "public_video_grade_slide_direction_and_per_slide_visual_recipe")}}
              ${{detailBlock("Creates new PPT deck", run238Result.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run238Result.public_ready)}}
              ${{detailBlock("Next action", run238Result.next_required_action || "Run 2.39 four-arm rerun")}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.37 audit", run238Inputs.visual_quality_audit || "run2_37_visual_quality_audit.json")}}
              ${{detailBlock("Run 2.36 result", run238Inputs.visual_evidence_realism_rerun_result || "run2_36_visual_evidence_realism_rerun_result.json")}}
              ${{detailBlock("Run 2.35 workflow", run238Inputs.visual_evidence_realism_workflow_result || "run2_35_visual_evidence_realism_workflow_result.json")}}
              ${{detailBlock("Commercial usecase bank", run238Inputs.commercial_usecase_bank)}}
              ${{detailBlock("Sources", run238Inputs.sources)}}
            </article>
            <article class="dataCard">
              <h4>Output chain</h4>
              ${{detailBlock("Direction memory", run238Output.public_video_slide_direction_memory || "run2_38_public_video_slide_direction_memory.json")}}
              ${{detailBlock("Recipe memory", run238Output.per_slide_visual_recipe_memory || "run2_38_per_slide_visual_recipe_memory.json")}}
              ${{detailBlock("Workflow gates", run238Output.public_video_workflow_gates || "run2_38_public_video_workflow_gates.json")}}
              ${{detailBlock("Artifact counts", run238Counts)}}
            </article>
            <article class="dataCard">
              <h4>visual_rhythm_diversity_contract</h4>
              ${{detailBlock("Min unique visual rhythms", run238Contract.min_unique_visual_rhythms)}}
              ${{detailBlock("Max repeated layout signature allowed", run238Contract.max_repeated_layout_signature_allowed)}}
              ${{detailBlock("Forbidden dominant layout signature", run238Contract.forbidden_dominant_layout_signature)}}
              ${{detailBlock("Required by", "Run 2.39 four-arm rerun")}}
            </article>
          </div>
          <div class="dataGrid">${{run238DirectionCards}}</div>
          <div class="dataGrid">${{run238RecipeCards}}</div>
          <div class="dataGrid">${{run238GateCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.39 public-video visual direction rerun</h3><p>Generated four-arm rerun that consumes the Run 2.38 public-video visual direction workflow before native PPT code generation. Target: public_video_grade_slide_direction_and_per_slide_visual_recipe.</p></div><span class="pill">${{escapeHtml(refs.run239ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Result", "run2_39_public_video_visual_direction_rerun_result.json")}}
              ${{detailBlock("Best internal arm", run239Rerun.best_internal_arm || "run2_39_full_public_video_visual_direction")}}
              ${{detailBlock("Verdict", run239Rerun.best_internal_arm_verdict || "public_video_grade_slide_direction_and_per_slide_visual_recipe_consumed_before_native_ppt_generation")}}
              ${{detailBlock("Four-arm sheet", run239Rerun.combined_contact_sheet || "run2-39-four-arm-contact-sheet.png")}}
              ${{detailBlock("Full-skill series", run239Rerun.full_skill_series_sheet || "run2-full-skill-series-horizontal.png")}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.37 audit", run239Inputs.visual_quality_audit || "run2_37_visual_quality_audit.json")}}
              ${{detailBlock("Run 2.36 result", run239Inputs.visual_evidence_realism_rerun_result || "run2_36_visual_evidence_realism_rerun_result.json")}}
              ${{detailBlock("Run 2.38 workflow", run239Inputs.public_video_visual_direction_workflow_result || "run2_38_public_video_visual_direction_workflow_result.json")}}
              ${{detailBlock("Direction memory", run239Inputs.public_video_slide_direction_memory || "run2_38_public_video_slide_direction_memory.json")}}
              ${{detailBlock("Recipe memory", run239Inputs.per_slide_visual_recipe_memory || "run2_38_per_slide_visual_recipe_memory.json")}}
              ${{detailBlock("Workflow gates", run239Inputs.public_video_workflow_gates || "run2_38_public_video_workflow_gates.json")}}
            </article>
            <article class="dataCard">
              <h4>Quality delta</h4>
              ${{detailBlock("Target layer", run239Delta.target_layer || "public_video_grade_slide_direction_and_per_slide_visual_recipe")}}
              ${{detailBlock("Run 2.38 direction records consumed", run239Delta.run2_38_direction_records_consumed)}}
              ${{detailBlock("Run 2.38 recipe records consumed", run239Delta.run2_38_recipe_records_consumed)}}
              ${{detailBlock("Run 2.38 workflow gates consumed", run239Delta.run2_38_workflow_gates_consumed)}}
              ${{detailBlock("Unique visual rhythms", run239Delta.unique_visual_rhythms)}}
              ${{detailBlock("Required modules", run239Delta.repair_modules || ["drawRun239LaunchPosterStage", "drawRun239FailurePathScene", "drawRun239AsymmetricBeforeAfterState", "drawRun239ProductWorkflowSurface", "drawRun239CinematicClimaxObject", "drawRun239DecisionHandoffPath"])}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Prompt-only arm", "ppt-run2-39-prompt-only")}}
              ${{detailBlock("Run 1.5 arm", "ppt-run2-39-run1-5-skill")}}
              ${{detailBlock("Full arm", "ppt-run2-39-full-vulca")}}
              ${{detailBlock("Bad memory arm", "ppt-run2-39-bad-public-video-visual-direction-memory")}}
              ${{detailBlock("Bad control rule", run239Control.bad_public_video_visual_direction_memory || "selected usecase label only, no Run 2.38 public-video direction memory")}}
              ${{detailBlock("Release boundary", run239Result.release_boundary || "Do not advance to Run 3.0 before Run 2.39 is audited")}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.40 same-data visual compiler rerun</h3><p>Generated four-arm rerun that uses the same Run 2.38 and Run 2.39 data with no database expansion. Target: visual_compiler_hidden_trace_public_composition.</p></div><span class="pill">${{escapeHtml(refs.run240ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Result", "run2_40_visual_compiler_rerun_result.json")}}
              ${{detailBlock("Best internal arm", run240Rerun.best_internal_arm || "run2_40_full_visual_compiler")}}
              ${{detailBlock("Verdict", run240Rerun.best_internal_arm_verdict || "same_run2_38_run2_39_data_no_database_expansion_visual_compiler_improves_public_surface")}}
              ${{detailBlock("Four-arm sheet", run240Rerun.combined_contact_sheet || "run2-40-four-arm-contact-sheet.png")}}
              ${{detailBlock("Full-skill series", run240Rerun.full_skill_series_sheet || "run2-full-skill-series-horizontal.png")}}
            </article>
            <article class="dataCard">
              <h4>Same-data inputs</h4>
              ${{detailBlock("Run 2.39 result", run240Inputs.run2_39_rerun_result || "run2_39_public_video_visual_direction_rerun_result.json")}}
              ${{detailBlock("Direction memory", run240Inputs.public_video_slide_direction_memory || "run2_38_public_video_slide_direction_memory.json")}}
              ${{detailBlock("Recipe memory", run240Inputs.per_slide_visual_recipe_memory || "run2_38_per_slide_visual_recipe_memory.json")}}
              ${{detailBlock("Workflow gates", run240Inputs.public_video_workflow_gates || "run2_38_public_video_workflow_gates.json")}}
              ${{detailBlock("Database expansion", run240Result.database_expansion)}}
              ${{detailBlock("Source data status", run240Delta.source_data_status || "same_run2_38_run2_39_data_no_database_expansion")}}
            </article>
            <article class="dataCard">
              <h4>Visual compiler</h4>
              ${{detailBlock("Target layer", run240Delta.target_layer || "visual_compiler_hidden_trace_public_composition")}}
              ${{detailBlock("Policy", run240Delta.visual_compiler_policy || "trace_to_hidden_constraints_public_surface_composition")}}
              ${{detailBlock("New database records", run240Delta.new_database_records_added)}}
              ${{detailBlock("Hidden machinery slides", run240Delta.public_surface_machinery_hidden_slides)}}
              ${{detailBlock("Required modules", run240Delta.repair_modules || ["drawRun240EditorialPoster", "drawRun240UsecaseScene", "drawRun240TransformationSpread", "drawRun240ProductMoment", "drawRun240CinematicResult", "drawRun240DecisionScene"])}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Prompt-only arm", "ppt-run2-40-prompt-only")}}
              ${{detailBlock("Run 1.5 arm", "ppt-run2-40-run1-5-skill")}}
              ${{detailBlock("Full arm", "ppt-run2-40-full-vulca")}}
              ${{detailBlock("Bad same-data arm", "ppt-run2-40-bad-trace-visible-visual-compiler")}}
              ${{detailBlock("Bad same-data rule", run240Control.bad_trace_visible_visual_compiler || "same data, but trace/gate/memory/module terms stay visible")}}
              ${{detailBlock("Release boundary", run240Result.release_boundary || "Do not advance to Run 3.0 before Run 2.40 is audited")}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.41 content visual asset compiler rerun</h3><p>Generated four-arm rerun that uses the same database and no workflow expansion after Run 2.40. Target: content_visual_asset_composition_thickness.</p></div><span class="pill">${{escapeHtml(refs.run241ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Result", "run2_41_content_visual_asset_compiler_rerun_result.json")}}
              ${{detailBlock("Best internal arm", run241Rerun.best_internal_arm || "run2_41_full_content_visual_asset_compiler")}}
              ${{detailBlock("Verdict", run241Rerun.best_internal_arm_verdict || "content_visual_asset_compiler_thickens_public_surface_without_database_or_workflow_expansion")}}
              ${{detailBlock("Four-arm sheet", run241Rerun.combined_contact_sheet || "run2-41-four-arm-contact-sheet.png")}}
              ${{detailBlock("Full-skill series", run241Rerun.full_skill_series_sheet || "run2-full-skill-series-horizontal.png")}}
            </article>
            <article class="dataCard">
              <h4>Same database inputs</h4>
              ${{detailBlock("Run 2.40 result", run241Inputs.run2_40_rerun_result || "run2_40_visual_compiler_rerun_result.json")}}
              ${{detailBlock("Run 2.39 result", run241Inputs.run2_39_rerun_result || "run2_39_public_video_visual_direction_rerun_result.json")}}
              ${{detailBlock("Direction memory", run241Inputs.public_video_slide_direction_memory || "run2_38_public_video_slide_direction_memory.json")}}
              ${{detailBlock("Recipe memory", run241Inputs.per_slide_visual_recipe_memory || "run2_38_per_slide_visual_recipe_memory.json")}}
              ${{detailBlock("Workflow gates", run241Inputs.public_video_workflow_gates || "run2_38_public_video_workflow_gates.json")}}
              ${{detailBlock("Commercial usecase bank", run241Inputs.commercial_usecase_bank || "commercial_usecase_bank.json")}}
              ${{detailBlock("Sources", run241Inputs.sources || "sources.json")}}
            </article>
            <article class="dataCard">
              <h4>Content/visual asset compiler</h4>
              ${{detailBlock("Target layer", run241Delta.target_layer || "content_visual_asset_composition_thickness")}}
              ${{detailBlock("Source data status", run241Delta.source_data_status || "same_database_no_workflow_expansion_content_visual_asset_compiler")}}
              ${{detailBlock("Compiler policy", run241Delta.content_visual_asset_compiler_policy || "visual_asset_surface_from_existing_sources_not_copied_media")}}
              ${{detailBlock("New database records", run241Delta.new_database_records_added)}}
              ${{detailBlock("New workflow gates", run241Delta.new_workflow_gates_added)}}
              ${{detailBlock("Slides with >=5 business details", run241Delta.full_slides_with_visible_business_detail_count_min_5)}}
              ${{detailBlock("Slides with >=3 visual asset surfaces", run241Delta.full_slides_with_visual_asset_surface_count_min_3)}}
              ${{detailBlock("Required modules", run241Delta.repair_modules || ["drawRun241MarketScenePoster", "drawRun241FailureStoryboard", "drawRun241BeforeAfterBusinessCase", "drawRun241ProductUiEvidenceScene", "drawRun241CinematicLaunchMoment", "drawRun241ReviewDecisionRoom"])}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Prompt-only arm", "ppt-run2-41-prompt-only")}}
              ${{detailBlock("Run 1.5 arm", "ppt-run2-41-run1-5-skill")}}
              ${{detailBlock("Full arm", "ppt-run2-41-full-vulca")}}
              ${{detailBlock("Bad thin arm", "ppt-run2-41-bad-thin-content-visual-asset-compiler")}}
              ${{detailBlock("Bad thin rule", run241Control.bad_thin_content_visual_asset_compiler || "same database, hidden machinery, but thin business details and visual asset surfaces")}}
              ${{detailBlock("Release boundary", run241Result.release_boundary || "Do not advance to Run 3.0 before Run 2.41 is audited")}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.42 content visual asset quality audit</h3><p>Audit-only layer over Run 2.41. It creates no new PPT deck; it verifies that content/visual asset thickness improved while design quality remains blocked by schematic visual assets.</p></div><span class="pill">${{escapeHtml(refs.run242AuditStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Audit boundary</h4>
              ${{detailBlock("Result", "run2_42_content_visual_asset_quality_audit.json")}}
              ${{detailBlock("Source generated run", run242Audit.source_generated_run)}}
              ${{detailBlock("Source prior generated run", run242Audit.source_prior_generated_run)}}
              ${{detailBlock("Creates new PPT deck", run242Audit.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run242Audit.public_ready)}}
              ${{detailBlock("Next required action", run242Audit.next_required_action || "build_run2_43_visual_asset_semantics_editorial_composition_workflow")}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.41 full trace", run242Inputs.run2_41_full_trace_manifest)}}
              ${{detailBlock("Run 2.41 bad trace", run242Inputs.run2_41_bad_trace_manifest)}}
              ${{detailBlock("Run 2.41 result", run242Inputs.run2_41_rerun_result)}}
              ${{detailBlock("Run 2.40 result", run242Inputs.run2_40_rerun_result)}}
              ${{detailBlock("Run 2.41 four-arm sheet", run242Inputs.run2_41_four_arm_contact_sheet)}}
              ${{detailBlock("Full skill series", run242Inputs.run2_full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Trace closure</h4>
              ${{detailBlock("Full arm", (run242Trace.full_arm || {{}}).arm_id)}}
              ${{detailBlock("Compiler applied slides", (run242Trace.full_arm || {{}}).content_visual_asset_compiler_applied_slides)}}
              ${{detailBlock(">=5 business detail slides", (run242Trace.full_arm || {{}}).visible_business_detail_min5_slides)}}
              ${{detailBlock(">=3 visual asset surface slides", (run242Trace.full_arm || {{}}).visual_asset_surface_min3_slides)}}
              ${{detailBlock("Bad thin control slides", (run242Trace.bad_control || {{}}).thin_content_control_slides)}}
              ${{detailBlock("Bad machinery leaks", (run242Trace.bad_control || {{}}).machinery_leak_slides)}}
            </article>
            <article class="dataCard">
              <h4>Quality assessment</h4>
              ${{detailBlock("Content visual asset gate", run242Assessment.content_visual_asset_gate)}}
              ${{detailBlock("Delta from bad control", run242Assessment.content_visual_asset_thickness_delta_from_bad_control)}}
              ${{detailBlock("Design quality gate", run242Assessment.design_quality_gate)}}
              ${{detailBlock("Root cause", run242Assessment.root_cause_primary || "visual_asset_surfaces_are_still_schematic_native_shapes_not_true_product_or_scene_assets")}}
              ${{detailBlock("Next layer", run242Assessment.top_next_layer_to_thicken || "usecase_specific_visual_asset_semantics_editorial_composition_and_typography_hierarchy")}}
              ${{detailBlock("Why still simple", run242Assessment.why_user_still_sees_simple_design)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.43 visual asset semantics workflow</h3><p>Data/workflow-only layer over Run 2.42. It creates no new PPT deck; it turns Run 2.41's named visual asset surfaces into semantic visual assets, editorial composition, typography hierarchy, and next-rerun gates.</p></div><span class="pill">${{escapeHtml(refs.run243ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Workflow boundary</h4>
              ${{detailBlock("Result", "run2_43_visual_asset_semantics_workflow_result.json")}}
              ${{detailBlock("Source audit run", run243Result.source_audit_run)}}
              ${{detailBlock("Source generated run", run243Result.source_generated_run)}}
              ${{detailBlock("Creates new PPT deck", run243Result.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run243Result.public_ready)}}
              ${{detailBlock("Target layer", run243Result.target_layer || "usecase_specific_visual_asset_semantics_editorial_composition_and_typography_hierarchy")}}
              ${{detailBlock("Next required action", run243Result.next_required_action || "consume_run2_43_visual_asset_semantics_workflow_before_run2_44_rerun")}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.42 audit", run243Inputs.content_visual_asset_quality_audit)}}
              ${{detailBlock("Run 2.41 full trace", run243Inputs.run2_41_full_trace_manifest)}}
              ${{detailBlock("Run 2.41 result", run243Inputs.run2_41_rerun_result)}}
              ${{detailBlock("Run 2.40 result", run243Inputs.run2_40_rerun_result)}}
              ${{detailBlock("Commercial usecase bank", run243Inputs.commercial_usecase_bank)}}
            </article>
            <article class="dataCard">
              <h4>Output chain</h4>
              ${{detailBlock("Semantic visual asset memory", run243Outputs.semantic_visual_asset_memory || "run2_43_semantic_visual_asset_memory.json")}}
              ${{detailBlock("Editorial composition typography memory", run243Outputs.editorial_composition_typography_memory || "run2_43_editorial_composition_typography_memory.json")}}
              ${{detailBlock("Visual asset semantics workflow gates", run243Outputs.visual_asset_semantics_workflow_gates || "run2_43_visual_asset_semantics_workflow_gates.json")}}
              ${{detailBlock("Semantic asset records", run243Counts.semantic_visual_asset_records)}}
              ${{detailBlock("Editorial typography records", run243Counts.editorial_composition_typography_records)}}
              ${{detailBlock("Workflow gates", run243Counts.workflow_gates)}}
            </article>
            <article class="dataCard">
              <h4>Storage/source boundary</h4>
              ${{detailBlock("Allowed storage", (refs.run243SourceBoundary || {{}}).allowed_storage)}}
              ${{detailBlock("Copied screenshots", (refs.run243SourceBoundary || {{}}).copied_screenshots)}}
              ${{detailBlock("Raw tutorial or video media", (refs.run243SourceBoundary || {{}}).raw_tutorial_or_video_media)}}
              ${{detailBlock("Source layouts", (refs.run243SourceBoundary || {{}}).source_layouts)}}
              ${{detailBlock("Brand marks", (refs.run243SourceBoundary || {{}}).brand_marks)}}
              ${{detailBlock("Next rerun contract", refs.run243NextRerunContract || "must_be_consumed_before_run2_44_four_arm_rerun")}}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Semantic visual assets</h4><p>Each Run 2.41 named surface becomes a concrete usecase-specific object that native PPT code must render without copied media.</p></div>
          <div class="dataGrid">${{run243SemanticAssetCards}}</div>
          <div class="dataBandSubhead"><h4>Editorial composition + typography memory</h4><p>Each role gets first-read object, hierarchy, spacing, and scene-depth obligations before code generation.</p></div>
          <div class="dataGrid">${{run243EditorialCards}}</div>
          <div class="dataBandSubhead"><h4>Workflow gates</h4><p>Run 2.44 must bind these ids in trace before native PPT drawing; bad control can reuse names but not this memory.</p></div>
          <div class="dataGrid">${{run243GateCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.44 dataflow readiness audit</h3><p>Preflight audit for the suspected bug: current visible slides do not consume the latest workflow, and current data use affects text/trace more than visual geometry.</p></div><span class="pill">${{escapeHtml(refs.run244DataflowAuditStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Bug classification</h4>
              ${{detailBlock("Result", "run2_44_dataflow_readiness_audit.json")}}
              ${{detailBlock("Bug confirmed", run244Audit.bug_confirmed)}}
              ${{detailBlock("Not a generated Run 2.44 output", run244Audit.not_a_run2_44_output)}}
              ${{detailBlock("Risk priority", run244Audit.risk_priority)}}
              ${{detailBlock("Latest visible PPT run", run244Audit.latest_visible_ppt_run)}}
              ${{detailBlock("Latest workflow run", run244Audit.latest_workflow_run)}}
              ${{detailBlock("Root cause", run244Audit.root_cause_primary || "latest_visible_ppt_does_not_consume_latest_run2_43_workflow")}}
              ${{detailBlock("Classification", run244Audit.classification)}}
            </article>
            <article class="dataCard">
              <h4>Dataflow findings</h4>
              ${{detailBlock("Run 2.43 consumed by latest visible PPT", run244Findings.run2_43_consumed_by_latest_visible_ppt)}}
              ${{detailBlock("Run 2.41 reads Run 2.38 data", run244Findings.run2_41_generator_reads_run2_38_data)}}
              ${{detailBlock("Run 2.41 reads Run 2.43 data", run244Findings.run2_41_generator_reads_run2_43_data)}}
              ${{detailBlock("Run 2.41 visual geometry is hardcoded", run244Findings.run2_41_visual_geometry_is_hardcoded)}}
              ${{detailBlock("Run 2.43 reads multimodal source records", run244Findings.run2_43_builder_reads_multimodal_source_records)}}
            </article>
            <article class="dataCard">
              <h4>Input chain checked</h4>
              ${{detailBlock("Run 2.41 generator", run244Inputs.run2_41_generator)}}
              ${{detailBlock("Run 2.41 trace", run244Inputs.run2_41_full_trace_manifest)}}
              ${{detailBlock("Run 2.43 workflow result", run244Inputs.run2_43_workflow_result)}}
              ${{detailBlock("Run 2.43 semantic memory", run244Inputs.run2_43_semantic_visual_asset_memory)}}
              ${{detailBlock("Run 2.43 gates", run244Inputs.run2_43_visual_asset_semantics_workflow_gates)}}
            </article>
            <article class="dataCard">
              <h4>Next rerun gate</h4>
              ${{detailBlock("Required before Run 2.44 generator", run244NextGate.required_before_run2_44_generator)}}
              ${{detailBlock("Generator must fail if Run 2.43 not consumed", run244NextGate.generator_must_fail_if_run2_43_not_consumed)}}
              ${{detailBlock("Visual geometry must be data-bound", run244NextGate.visual_geometry_must_be_data_bound)}}
              ${{detailBlock("Required trace fields", run244NextGate.required_trace_fields)}}
              ${{detailBlock("Next required action", run244Audit.next_required_action || "build_run2_44_generator_that_consumes_run2_43_memory_for_visual_geometry_before_render")}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.44 semantic geometry rerun</h3><p>Generated four-arm rerun that consumes Run 2.43 before drawing native PPT geometry. Target: semantic_visual_asset_geometry_binding.</p></div><span class="pill">${{escapeHtml(refs.run244ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Result", "run2_44_semantic_geometry_rerun_result.json")}}
              ${{detailBlock("Best internal arm", run244Rerun.best_internal_arm || "run2_44_full_semantic_geometry_compiler")}}
              ${{detailBlock("Verdict", run244Rerun.best_internal_arm_verdict || "Run 2.43 semantic workflow now drives native PPT geometry before drawing")}}
              ${{detailBlock("Four-arm sheet", run244Rerun.combined_contact_sheet || "run2-44-four-arm-contact-sheet.png")}}
              ${{detailBlock("Full-skill series", run244Rerun.full_skill_series_sheet || "run2-full-skill-series-horizontal.png")}}
            </article>
            <article class="dataCard">
              <h4>Consumed input chain</h4>
              ${{detailBlock("Run 2.43 workflow result", run244RerunInputs.run2_43_workflow_result || "run2_43_visual_asset_semantics_workflow_result.json")}}
              ${{detailBlock("Semantic visual asset memory", run244RerunInputs.semantic_visual_asset_memory || "run2_43_semantic_visual_asset_memory.json")}}
              ${{detailBlock("Editorial composition typography memory", run244RerunInputs.editorial_composition_typography_memory || "run2_43_editorial_composition_typography_memory.json")}}
              ${{detailBlock("Visual asset semantics workflow gates", run244RerunInputs.visual_asset_semantics_workflow_gates || "run2_43_visual_asset_semantics_workflow_gates.json")}}
              ${{detailBlock("Preflight audit", run244RerunInputs.run2_44_dataflow_readiness_audit || "run2_44_dataflow_readiness_audit.json")}}
            </article>
            <article class="dataCard">
              <h4>Geometry binding result</h4>
              ${{detailBlock("Target layer", run244Delta.target_layer || "semantic_visual_asset_geometry_binding")}}
              ${{detailBlock("Source data status", run244Delta.source_data_status || "run2_43_workflow_consumed_for_data_bound_geometry")}}
              ${{detailBlock("Geometry source", run244Delta.run2_44_geometry_source || "run2_43_semantic_visual_asset_memory+run2_43_editorial_composition_typography_memory+run2_43_visual_asset_semantics_workflow_gates")}}
              ${{detailBlock("Slides with semantic asset ids", run244Delta.full_slides_with_run2_43_semantic_asset_ids)}}
              ${{detailBlock("Slides with data-bound geometry", run244Delta.full_slides_with_data_bound_geometry)}}
              ${{detailBlock("Required modules", run244Delta.repair_modules || ["drawRun244CoverSemanticGeometry", "drawRun244SetupSemanticGeometry", "drawRun244ContrastSemanticGeometry", "drawRun244ProofSemanticGeometry", "drawRun244ClimaxSemanticGeometry", "drawRun244CloseSemanticGeometry"])}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Prompt-only arm", "ppt-run2-44-prompt-only")}}
              ${{detailBlock("Run 1.5 arm", "ppt-run2-44-run1-5-skill")}}
              ${{detailBlock("Full arm", "ppt-run2-44-full-vulca")}}
              ${{detailBlock("Bad name-only arm", "ppt-run2-44-bad-run2-43-name-only-geometry")}}
              ${{detailBlock("Bad name-only rule", run244Control.bad_run2_43_name_only_geometry || "surface names only, no semantic asset ids, no gate id, no data-bound geometry")}}
              ${{detailBlock("Release boundary", run244Result.release_boundary || "Do not advance to Run 3.0 before Run 2.44 is audited")}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.45 semantic geometry effectiveness audit</h3><p>Audit-only layer over Run 2.44. It confirms the dataflow bug is fixed, then blocks visual quality because the compiler remains slot_based_semantic_geometry.</p></div><span class="pill">${{escapeHtml(refs.run245AuditStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Audit boundary</h4>
              ${{detailBlock("Result", "run2_45_semantic_geometry_effectiveness_audit.json")}}
              ${{detailBlock("Source generated run", run245Audit.source_generated_run)}}
              ${{detailBlock("Source workflow run", run245Audit.source_workflow_run)}}
              ${{detailBlock("Creates new PPT deck", run245Audit.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run245Audit.public_ready)}}
              ${{detailBlock("Next required action", run245Audit.next_required_action || "build_run2_46_multimodal_composition_memory_and_workflow_thickening")}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.44 full trace", run245Inputs.run2_44_full_trace_manifest)}}
              ${{detailBlock("Run 2.44 bad trace", run245Inputs.run2_44_bad_trace_manifest)}}
              ${{detailBlock("Run 2.44 result", run245Inputs.run2_44_rerun_result)}}
              ${{detailBlock("Run 2.43 semantic memory", run245Inputs.run2_43_semantic_visual_asset_memory)}}
              ${{detailBlock("Run 2.43 gates", run245Inputs.run2_43_visual_asset_semantics_workflow_gates)}}
              ${{detailBlock("Run 2.44 four-arm sheet", run245Inputs.run2_44_four_arm_contact_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Trace effectiveness</h4>
              ${{detailBlock("Dataflow bug fixed", run245Trace.dataflow_bug_fixed)}}
              ${{detailBlock("Full arm", run245Full.arm_id)}}
              ${{detailBlock("Slides with semantic asset ids", run245Full.slides_with_run2_43_semantic_asset_ids)}}
              ${{detailBlock("Slides with data-bound geometry", run245Full.slides_with_data_bound_geometry)}}
              ${{detailBlock("All slides have ids/memory/gate/geometry", run245Full.all_slides_have_semantic_ids_memory_gate_and_geometry)}}
              ${{detailBlock("Bad control name-only boundary", run245Bad.name_only_boundary_passed)}}
            </article>
            <article class="dataCard">
              <h4>Visual effectiveness</h4>
              ${{detailBlock("Composition compiler kind", run245Visual.composition_compiler_kind || "slot_based_semantic_geometry")}}
              ${{detailBlock("Slot-based geometry slides", run245Visual.slot_based_geometry_slides)}}
              ${{detailBlock("Visual delta from bad control", run245Visual.dataflow_fix_visual_delta_from_bad_control)}}
              ${{detailBlock("Visual quality gate", run245Visual.visual_quality_gate)}}
              ${{detailBlock("Root cause", run245Visual.root_cause_primary || "run2_44_dataflow_fixed_but_composition_compiler_still_slot_based")}}
              ${{detailBlock("Next layer", run245Visual.top_next_layer_to_thicken || "multimodal_composition_memory_and_visual_object_grammar")}}
              ${{detailBlock("Gate summary", run245Gate.summary)}}
            </article>
          </div>
        </section>
        <!-- Run 2.46 is data/workflow-only; generated proof advances through Run 2.47 and Run 2.50. -->
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.46 multimodal composition memory</h3><p>Data/workflow-only layer over Run 2.45. It turns slot-based failure into multimodal composition decomposition, visual object grammar, and composition gates that must be consumed before Run 2.47.</p></div><span class="pill">${{escapeHtml(refs.run246ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Workflow boundary</h4>
              ${{detailBlock("Result", "run2_46_multimodal_composition_memory_result.json")}}
              ${{detailBlock("Creates new PPT deck", run246Result.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run246Result.public_ready)}}
              ${{detailBlock("Target layer", run246Result.target_layer || "multimodal_composition_memory_and_visual_object_grammar")}}
              ${{detailBlock("Next required action", run246Result.next_required_action || "consume_run2_46_multimodal_composition_memory_before_run2_47_rerun")}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.45 audit", run246Inputs.semantic_geometry_effectiveness_audit)}}
              ${{detailBlock("Multimodal source records", run246Inputs.multimodal_source_records)}}
              ${{detailBlock("Run 2.43 semantic memory", run246Inputs.semantic_visual_asset_memory)}}
              ${{detailBlock("Run 2.43 typography memory", run246Inputs.editorial_composition_typography_memory)}}
              ${{detailBlock("Run 2.43 gates", run246Inputs.visual_asset_semantics_workflow_gates)}}
            </article>
            <article class="dataCard">
              <h4>Output chain</h4>
              ${{detailBlock("Multimodal composition decomposition", run246Outputs.multimodal_composition_decomposition || "run2_46_multimodal_composition_decomposition.json")}}
              ${{detailBlock("Visual object grammar memory", run246Outputs.visual_object_grammar_memory || "run2_46_visual_object_grammar_memory.json")}}
              ${{detailBlock("Composition workflow gates", run246Outputs.composition_workflow_gates || "run2_46_composition_workflow_gates.json")}}
              ${{detailBlock("Decomposition records", run246Counts.multimodal_composition_decomposition_records)}}
              ${{detailBlock("Grammar records", run246Counts.visual_object_grammar_records)}}
              ${{detailBlock("Workflow gates", run246Counts.composition_workflow_gates)}}
            </article>
            <article class="dataCard">
              <h4>Gate purpose</h4>
              ${{detailBlock("Decomposition status", refs.run246DecompositionStatus)}}
              ${{detailBlock("Grammar status", refs.run246GrammarStatus)}}
              ${{detailBlock("Gate status", refs.run246GateStatus)}}
              ${{detailBlock("Release boundary", run246Result.release_boundary)}}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Multimodal composition decomposition</h4><p>Role-level composition moves derived from source-safe tutorial/video/case records, not copied layouts or media.</p></div>
          <div class="dataGrid">${{run246DecompositionCards}}</div>
          <div class="dataBandSubhead"><h4>Visual object grammar</h4><p>Per-role grammar that replaces Run 2.44 slot geometry with composed object scenes.</p></div>
          <div class="dataGrid">${{run246GrammarCards}}</div>
          <div class="dataBandSubhead"><h4>Composition workflow gates</h4><p>Run 2.47 must bind these gate ids before native PPT drawing; slot-based geometry alone should fail.</p></div>
          <div class="dataGrid">${{run246GateCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.47 composition grammar rerun</h3><p>Generated four-arm rerun that consumes Run 2.46 visual object grammar before native PPT code generation. It proves the full arm leaves slot-based geometry while the bad control falls back to Run 2.44 slots.</p></div><span class="pill">${{escapeHtml(refs.run247ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Result", refs.run247ResultPath || "run2_47_composition_grammar_rerun_result.json")}}
              ${{detailBlock("Best internal arm", run247Rerun.best_internal_arm || "run2_47_full_composition_grammar_compiler")}}
              ${{detailBlock("Target layer", run247Delta.target_layer || "composition_grammar_binding")}}
              ${{detailBlock("Source data status", run247Delta.source_data_status || "run2_46_composition_grammar_consumed_before_native_ppt_drawing")}}
              ${{detailBlock("Four-arm sheet", run247Rerun.combined_contact_sheet || "run2-47-four-arm-contact-sheet.png")}}
              ${{detailBlock("Full-skill series", run247Rerun.full_skill_series_sheet || "run2-full-skill-series-horizontal.png")}}
            </article>
            <article class="dataCard">
              <h4>Consumed input chain</h4>
              ${{detailBlock("Composition decomposition", run247Inputs.multimodal_composition_decomposition || "run2_46_multimodal_composition_decomposition.json")}}
              ${{detailBlock("Visual object grammar", run247Inputs.visual_object_grammar_memory || "run2_46_visual_object_grammar_memory.json")}}
              ${{detailBlock("Composition workflow gates", run247Inputs.composition_workflow_gates || "run2_46_composition_workflow_gates.json")}}
              ${{detailBlock("Run 2.46 result", run247Inputs.run2_46_result || "run2_46_multimodal_composition_memory_result.json")}}
            </article>
            <article class="dataCard">
              <h4>Trace delta</h4>
              ${{detailBlock("Full slides with grammar ids", run247Delta.full_slides_with_run2_46_visual_object_grammar_id)}}
              ${{detailBlock("Full slides with slot-based geometry replaced", run247Delta.full_slides_with_slot_based_geometry_replaced)}}
              ${{detailBlock("Full slides without Run 2.44 slots", run247Delta.full_slides_without_run2_44_geometry_slots)}}
              ${{detailBlock("Bad control without grammar", run247Delta.bad_control_slides_without_run2_46_grammar)}}
              ${{detailBlock("Bad control with Run 2.44 slots", run247Delta.bad_control_slides_with_run2_44_geometry_slots)}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Bad missing grammar", run247Control.bad_run2_46_missing_composition_grammar)}}
              ${{detailBlock("Prompt-only", run247Control.prompt_only)}}
              ${{detailBlock("Run 1.5", run247Control.run1_5_skill)}}
              ${{detailBlock("Next required action", run247Result.next_required_action || "audit_run2_47_composition_grammar_against_visual_quality_then_continue_data_workflow_thickening_or_renderer_repair")}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.48 composition grammar effectiveness audit</h3><p>Audit-only layer over Run 2.47. It confirms visual object grammar consumption, compares against Run 2.44 slots and the bad control, then blocks public-video-grade release until readability and editorial renderer repair. No Run 2.48 PPTX/download is created; the next generated proof layer is Run 2.50.</p></div><span class="pill">${{escapeHtml(refs.run248AuditStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Audit boundary</h4>
              ${{detailBlock("Result", refs.run248AuditPath || "run2_48_composition_grammar_effectiveness_audit.json")}}
              ${{detailBlock("Source generated run", run248Audit.source_generated_run)}}
              ${{detailBlock("Source composition memory run", run248Audit.source_composition_memory_run)}}
              ${{detailBlock("Comparison prior generated run", run248Audit.comparison_prior_generated_run)}}
              ${{detailBlock("Creates new PPT deck", run248Audit.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run248Audit.public_ready)}}
            </article>
            <article class="dataCard">
              <h4>Input chain checked</h4>
              ${{detailBlock("Run 2.47 full trace", run248Inputs.run2_47_full_trace_manifest)}}
              ${{detailBlock("Run 2.47 bad trace", run248Inputs.run2_47_bad_trace_manifest)}}
              ${{detailBlock("Run 2.47 result", run248Inputs.run2_47_rerun_result)}}
              ${{detailBlock("Run 2.46 grammar", run248Inputs.run2_46_visual_object_grammar_memory)}}
              ${{detailBlock("Run 2.44 prior trace", run248Inputs.run2_44_full_trace_manifest)}}
            </article>
            <article class="dataCard">
              <h4>Trace effectiveness</h4>
              ${{detailBlock("Composition grammar consumed", run248Trace.composition_grammar_consumed)}}
              ${{detailBlock("Full slides with grammar ids", run248Full.slides_with_run2_46_visual_object_grammar_id)}}
              ${{detailBlock("Full slides with scene objects", run248Full.slides_with_run2_47_scene_objects)}}
              ${{detailBlock("Full slides without Run 2.44 slots", run248Full.slides_without_run2_44_slots)}}
              ${{detailBlock("Bad control without grammar", run248Bad.slides_without_run2_46_grammar)}}
              ${{detailBlock("Bad control with Run 2.44 slots", run248Bad.slides_with_run2_44_slots)}}
              ${{detailBlock("Prior Run 2.44 slots", run248Prior.slides_with_run2_44_slots)}}
            </article>
            <article class="dataCard">
              <h4>Visual effectiveness gate</h4>
              ${{detailBlock("Compiler kind", run248Visual.composition_compiler_kind || "visual_object_grammar_composed_object_scene")}}
              ${{detailBlock("Delta from Run 2.44", run248Visual.composition_grammar_delta_from_run2_44)}}
              ${{detailBlock("Visual quality gate", run248Visual.visual_quality_gate)}}
              ${{detailBlock("Public-video-grade", run248Visual.public_video_grade_visual_quality)}}
              ${{detailBlock("Root cause", run248Visual.root_cause_primary)}}
              ${{detailBlock("Next layer", run248Visual.top_next_layer_to_thicken || "readability_content_density_and_editorial_renderer_repair")}}
            </article>
            <article class="dataCard">
              <h4>Content density diagnosis</h4>
              ${{detailBlock("Average visible words", run248Content.average_visible_words_per_slide)}}
              ${{detailBlock("Average text boxes", run248Content.average_text_boxes_per_slide)}}
              ${{detailBlock("Rich-density slides", run248Content.slides_with_rich_text_density)}}
              ${{detailBlock("Interpretation", run248Content.interpretation)}}
            </article>
            <article class="dataCard">
              <h4>Release gate</h4>
              ${{detailBlock("Grammar consumption gate", run248Gate.grammar_consumption_gate)}}
              ${{detailBlock("Bad control gate", run248Gate.bad_control_gate)}}
              ${{detailBlock("Visual effectiveness gate", run248Gate.visual_effectiveness_gate)}}
              ${{detailBlock("Public release gate", run248Gate.public_release_gate)}}
              ${{detailBlock("Next required action", run248Audit.next_required_action || "build_run2_49_readability_content_density_and_editorial_renderer_repair_before_rerun")}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.49 readability/content density/editorial renderer repair</h3><p>Data-only Run over Run 2.48. It creates readability memory, content evidence density memory, and editorial renderer workflow gates, then blocks any new visual-quality claim until Run 2.50 consumes them in a generated four-arm rerun.</p></div><span class="pill">${{escapeHtml(refs.run249ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Data-only Run boundary</h4>
              ${{detailBlock("Result", "run2_49_readability_content_density_renderer_repair_result.json")}}
              ${{detailBlock("Creates new PPT deck", run249Result.creates_new_ppt_deck)}}
              ${{detailBlock("Public ready", run249Result.public_ready)}}
              ${{detailBlock("Target layer", run249Result.target_layer || "readability_content_density_and_editorial_renderer_repair")}}
              ${{detailBlock("Next required action", run249Result.next_required_action || "consume_run2_49_before_run2_50_four_arm_rerun")}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.48 audit", run249Inputs.composition_grammar_effectiveness_audit || "run2_48_composition_grammar_effectiveness_audit.json")}}
              ${{detailBlock("Run 2.46 visual object grammar", run249Inputs.visual_object_grammar_memory || "run2_46_visual_object_grammar_memory.json")}}
              ${{detailBlock("Run 2.46 composition gates", run249Inputs.composition_workflow_gates || "run2_46_composition_workflow_gates.json")}}
              ${{detailBlock("Run 2.24 single-usecase content", run249Inputs.single_usecase_content_memory || "run2_24_single_usecase_content_memory.json")}}
            </article>
            <article class="dataCard">
              <h4>Output chain</h4>
              ${{detailBlock("Readability memory", run249Outputs.readability_memory || "run2_49_readability_memory.json")}}
              ${{detailBlock("Content evidence density memory", run249Outputs.content_evidence_density_memory || "run2_49_content_evidence_density_memory.json")}}
              ${{detailBlock("Editorial renderer workflow gates", run249Outputs.editorial_renderer_workflow_gates || "run2_49_editorial_renderer_workflow_gates.json")}}
              ${{detailBlock("Readability records", run249Counts.readability_records)}}
              ${{detailBlock("Content evidence density records", run249Counts.content_evidence_density_records)}}
              ${{detailBlock("Editorial renderer workflow gates", run249Counts.editorial_renderer_workflow_gates)}}
            </article>
            <article class="dataCard">
              <h4>Repair contract</h4>
              ${{detailBlock("Readability", run249RepairContract.readability)}}
              ${{detailBlock("Content evidence density", run249RepairContract["content evidence density"])}}
              ${{detailBlock("Editorial renderer", run249RepairContract["editorial renderer"])}}
              ${{detailBlock("Release boundary", run249Result.release_boundary)}}
            </article>
          </div>
          <div class="dataBandSubhead"><h4>Readability memory</h4><p>${{escapeHtml(refs.run249ReadabilityStatus)}}. These gates turn the previous vague readability complaint into title size, headline length, clipping, contrast, and contact-sheet checks.</p></div>
          <div class="dataGrid">${{run249ReadabilityCards}}</div>
          <div class="dataBandSubhead"><h4>Content evidence density memory</h4><p>${{escapeHtml(refs.run249DensityStatus)}}. These records require concrete business evidence objects and inspectable proof objects instead of generic abstract proof.</p></div>
          <div class="dataGrid">${{run249DensityCards}}</div>
          <div class="dataBandSubhead"><h4>Editorial renderer workflow gates</h4><p>${{escapeHtml(refs.run249GateStatus)}}. Run 2.50 must bind these renderer contracts before native PPT drawing, including non-square surfaces and no square block grid as the primary visual surface.</p></div>
          <div class="dataGrid">${{run249GateCards}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.50 readability density renderer rerun</h3><p>Generated four-arm rerun over Run 2.49. The full arm binds readability ids, content evidence density ids, and renderer gate ids before native PPT drawing; the bad control intentionally lacks the repair pack.</p></div><span class="pill">${{escapeHtml(refs.run250ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Run 2.49 result", run250Inputs.run2_49_result || "run2_49_readability_content_density_renderer_repair_result.json")}}
              ${{detailBlock("Readability memory", run250Inputs.run2_49_readability_memory || "run2_49_readability_memory.json")}}
              ${{detailBlock("Content evidence density", run250Inputs.run2_49_content_evidence_density_memory || "run2_49_content_evidence_density_memory.json")}}
              ${{detailBlock("Renderer gates", run250Inputs.run2_49_editorial_renderer_workflow_gates || "run2_49_editorial_renderer_workflow_gates.json")}}
            </article>
            <article class="dataCard">
              <h4>Generated proof</h4>
              ${{detailBlock("Best arm", run250Rerun.best_internal_arm)}}
              ${{detailBlock("Verdict", run250Rerun.best_internal_arm_verdict)}}
              ${{detailBlock("Four-arm sheet", run250Rerun.combined_contact_sheet)}}
              ${{detailBlock("Full-series sheet", run250Rerun.full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Trace delta</h4>
              ${{detailBlock("Readability ids", run250Quality.full_slides_with_run2_49_readability_memory_id)}}
              ${{detailBlock("Density ids", run250Quality.full_slides_with_run2_49_content_evidence_density_memory_id)}}
              ${{detailBlock("Renderer gate ids", run250Quality.full_slides_with_run2_49_editorial_renderer_gate_id)}}
              ${{detailBlock("Non-square surfaces", run250Quality.full_slides_with_non_square_renderer_surface)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.22 selector-memory rerun result</h3><p>Generated four-arm rerun that consumes Run 2.21 visual-decision memory, selector gates, and rejection matrix before native PPT code generation. It stays in the same five-layer loop and does not advance to Run 3.0.</p></div><span class="pill">${{escapeHtml(refs.run222ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Best internal arm", run222Rerun.best_internal_arm)}}
              ${{detailBlock("Verdict", run222Rerun.best_internal_arm_verdict)}}
              ${{detailBlock("Four-arm sheet", run222Rerun.combined_contact_sheet)}}
              ${{detailBlock("Full-skill series", run222Rerun.full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Visual decision memory", run222Inputs.visual_decision_memory)}}
              ${{detailBlock("Selector gates", run222Inputs.selector_gates)}}
              ${{detailBlock("Rejection matrix", run222Inputs.rejection_matrix)}}
              ${{detailBlock("Stage policy", run222Result.stage_policy)}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Control arm", "bad_selector_memory")}}
              ${{detailBlock("Negative control", run222Control.bad_selector_memory)}}
              ${{detailBlock("Public ready", run222Result.public_ready)}}
              ${{detailBlock("Release boundary", run222Result.release_boundary)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.21 visual-decision memory</h3><p>Data-only layer: turns Run 2.20 trace effectiveness into per-role primary evidence, secondary evidence, and explicit rejection reasons before another generated rerun.</p></div><span class="pill">${{escapeHtml(refs.run221ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run boundary</h4>
              ${{detailBlock("Status", run221Result.status)}}
              ${{detailBlock("Creates new PPT deck", run221Result.creates_new_ppt_deck)}}
              ${{detailBlock("Source audit run", run221Result.source_audit_run)}}
              ${{detailBlock("Artifact counts", run221Result.artifact_counts)}}
              ${{detailBlock("Next action", run221Result.next_required_action)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.21 visual decision memory records</h3><p>${{escapeHtml(refs.run221DecisionMemoryStatus)}}. Each role has one primary evidence id, limited secondary evidence, and concrete typography, spacing, composition, proof-object, and code obligations.</p></div><span class="pill">${{(refs.run221DecisionMemory || []).length}} records</span></div>
          <div class="dataGrid">${{run221DecisionMemory}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.21 per-role selector gates</h3><p>${{escapeHtml(refs.run221SelectorGateStatus)}}. These gates must be consumed before the next native PPT generation pass.</p></div><span class="pill">${{(refs.run221SelectorGates || []).length}} gates</span></div>
          <div class="dataGrid">${{run221SelectorGates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.21 evidence rejection matrix</h3><p>${{escapeHtml(refs.run221RejectionMatrixStatus)}}. Every Run 2.18 evidence id is primary, secondary, or explicitly rejected for each slide role.</p></div><span class="pill">${{(refs.run221RejectionRecords || []).length}} roles</span></div>
          <div class="dataGrid">${{run221RejectionRecords}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.19 thickness rerun result</h3><p>Generated four-arm rerun that consumes the Run 2.18 thickness pack before native PPT code generation. It stays in the same five-layer loop and does not advance to Run 3.0.</p></div><span class="pill">${{escapeHtml(refs.run219ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Rerun proof</h4>
              ${{detailBlock("Best internal arm", run219Rerun.best_internal_arm)}}
              ${{detailBlock("Verdict", run219Rerun.best_internal_arm_verdict)}}
              ${{detailBlock("Four-arm sheet", run219Rerun.combined_contact_sheet)}}
              ${{detailBlock("Full-skill series", run219Rerun.full_skill_series_sheet)}}
            </article>
            <article class="dataCard">
              <h4>Input chain</h4>
              ${{detailBlock("Evidence", run219Inputs.evidence)}}
              ${{detailBlock("Memory", run219Inputs.memory)}}
              ${{detailBlock("Workflow gates", run219Inputs.workflow_gates)}}
              ${{detailBlock("Stage policy", run219Result.stage_policy)}}
            </article>
            <article class="dataCard">
              <h4>Control boundary</h4>
              ${{detailBlock("Control arm", "bad_thickness_memory")}}
              ${{detailBlock("Negative control", run219Control.bad_thickness_memory)}}
              ${{detailBlock("Public ready", run219Result.public_ready)}}
              ${{detailBlock("Release boundary", run219Result.release_boundary)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.18 thickness pack</h3><p>Latest data/workflow thickness layer: not a new PPT, but the required evidence, memory, and gate inputs for the next four-arm rerun.</p></div><span class="pill">${{escapeHtml(refs.run218ResultStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Run boundary</h4>
              ${{detailBlock("Status", run218Result.status)}}
              ${{detailBlock("Latest generated PPT", run218Result.latest_generated_ppt_run || "2.16")}}
              ${{detailBlock("Creates new PPT deck", run218Result.creates_new_ppt_deck)}}
              ${{detailBlock("Next action", run218Result.next_required_action)}}
              ${{detailBlock("Artifact counts", run218Result.artifact_counts)}}
            </article>
          </div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.18 multimodal evidence expansion</h3><p>${{escapeHtml(refs.run218EvidenceStatus)}}. Derived commercial usecase, tutorial, video, audio, transcript, image-reference, and interaction observations; raw media stays forbidden.</p></div><span class="pill">${{(refs.run218EvidenceRecords || []).length}} records</span></div>
          <div class="dataGrid">${{run218Evidence}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.18 design memory expansion</h3><p>${{escapeHtml(refs.run218MemoryStatus)}}. Converts thick evidence into composition, typography, spacing, sequence, proof-object, code, and trace contracts.</p></div><span class="pill">${{(refs.run218MemoryExpansions || []).length}} memories</span></div>
          <div class="dataGrid">${{run218Memory}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.18 workflow gate expansion</h3><p>${{escapeHtml(refs.run218GateStatus)}}. Required-before-rerun gates bind evidence, memory, selection rules, rejection rules, QA probes, and bad-control failure probes.</p></div><span class="pill">${{(refs.run218WorkflowGates || []).length}} gates</span></div>
          <div class="dataGrid">${{run218Gates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.17 motion delivery audit</h3><p>HTML viewer is static. This section separates static editable PPT delivery from real Keynote or public-video motion rendering.</p></div><span class="pill">${{escapeHtml(refs.run217MotionAuditStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Delivery truth</h4>
              ${{detailBlock("HTML viewer mode", run217DeliveryTruth.html_viewer_mode || "static_slide_preview_only")}}
              ${{detailBlock("PPTX editability", run217DeliveryTruth.pptx_editability_status)}}
              ${{detailBlock("Native PPT animation", run217DeliveryTruth.native_ppt_animation_status)}}
              ${{detailBlock("Keynote expected behavior", run217DeliveryTruth.keynote_expected_behavior)}}
              ${{detailBlock("Storyboard status", run217DeliveryTruth.motion_storyboard_status)}}
            </article>
            <article class="dataCard">
              <h4>Renderer gap</h4>
              ${{detailBlock("Next run", run217RendererGap.next_run_recommendation)}}
              ${{detailBlock("Static PPT role", run217RendererGap.keep_static_ppt_as)}}
              ${{detailBlock("Public video path", run217RendererGap.public_video_path)}}
              ${{detailBlock("Minimum proof slides", run217RendererGap.minimum_proof_slides)}}
              ${{detailBlock("Blocking questions", run217RendererGap.blocking_questions)}}
            </article>
          </div>
          <div class="dataGrid">${{run217ArmAudits}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.17 motion renderer proof</h3><p>A separate HTML motion renderer proof for cover, before/after, and climax. It is not Keynote animation and it does not replace the editable static PPT.</p></div><span class="pill">${{escapeHtml(refs.run217MotionProofStatus || "missing")}}</span></div>
          <div class="dataGrid">
            <article class="dataCard">
              <h4>Proof output</h4>
              ${{detailBlock("Motion proof role", run217ProofBoundary.motion_proof_role || "separate_html_motion_renderer")}}
              ${{detailBlock("Static PPT role", run217ProofBoundary.static_ppt_role)}}
              ${{detailBlock("Native animation claim", run217ProofBoundary.native_pptx_animation_claim || "not_claimed")}}
              ${{detailBlock("Keynote animation claim", run217ProofBoundary.keynote_animation_claim || "not_claimed")}}
              <p>${{proofHtmlLink}}</p>
              <p>${{proofManifestLink}}</p>
            </article>
          </div>
          <div class="dataGrid">${{run217ProofScenes}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Source URLs</h3><p>Reference identities stored in sources.json. These links are for inspection; copied media, layouts, transcripts, and brand marks remain forbidden.</p></div><span class="pill">${{(refs.sources || []).length}} sources</span></div>
          <div class="dataGrid">${{sources}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.7 multimodal records</h3><p>Derived source observations feeding the later Run 2.8 decomposition.</p></div><span class="pill">${{(refs.sourceRecords || []).length}} records</span></div>
          <div class="dataGrid">${{records}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.8 tutorial decomposition</h3><p>${{escapeHtml(refs.decompositionStatus)}}. This is where tutorial/video methods become generator rules.</p></div><span class="pill">${{(refs.decompositionUnits || []).length}} units</span></div>
          <div class="dataGrid">${{units}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Executable design memory</h3><p>${{escapeHtml(refs.memoryStatus)}}. These bindings explain why the output still depends on a small set of native PPT modules.</p></div><span class="pill">${{(refs.memoryBindings || []).length}} bindings</span></div>
          <div class="dataGrid">${{bindings}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Workflow gate matrix</h3><p>${{escapeHtml(refs.gateStatus)}}. Per-slide role gates connect data selection to required code calls and trace fields.</p></div><span class="pill">${{(refs.workflowGates || []).length}} gates</span></div>
          <div class="dataGrid">${{gates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.9 visual primitive repair</h3><p>${{escapeHtml(refs.run29RepairStatus)}}. Converts the Run 2.8 boxiness diagnosis into native editable visual primitives.</p></div><span class="pill">${{(refs.run29PrimitiveRepairs || []).length}} primitives</span></div>
          <div class="dataGrid">${{run29Primitives}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.9 executable visual modules</h3><p>${{escapeHtml(refs.run29ModuleStatus)}}. Function-level contracts for editorial spread, product depth, storyboard, climax stage, and typographic field modules.</p></div><span class="pill">${{(refs.run29VisualModules || []).length}} modules</span></div>
          <div class="dataGrid">${{run29Modules}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.9 visual gate matrix</h3><p>${{escapeHtml(refs.run29GateStatus)}}. Per-role gates require visual delta from Run 2.8 and explicit boxiness failure probes.</p></div><span class="pill">${{(refs.run29VisualGates || []).length}} gates</span></div>
          <div class="dataGrid">${{run29Gates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.10 visual-system sources</h3><p>${{escapeHtml(refs.run210SourceStatus)}}. Derived observations for editorial cinema, product theater, typographic launch fields, kinetic sequence, and non-rectangular proof paths.</p></div><span class="pill">${{(refs.run210VisualSystemSources || []).length}} sources</span></div>
          <div class="dataGrid">${{run210Sources}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.10 visual-system memory</h3><p>${{escapeHtml(refs.run210MemoryStatus)}}. Executable contracts that force structural asymmetry, whitespace, and visual-system differentiation before code generation.</p></div><span class="pill">${{(refs.run210VisualSystems || []).length}} systems</span></div>
          <div class="dataGrid">${{run210Systems}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.10 visual-system gate matrix</h3><p>${{escapeHtml(refs.run210GateStatus)}}. Per-role gates require actual drawRun210 module calls, shape budgets, and sameness failure probes against Run 2.9.</p></div><span class="pill">${{(refs.run210VisualGates || []).length}} gates</span></div>
          <div class="dataGrid">${{run210Gates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.12 thick multimodal evidence</h3><p>${{escapeHtml(refs.run212EvidenceStatus)}}. This is the real usecase/tutorial/video/audio-derived evidence layer used by Run 2.13; raw media and copied source visuals remain forbidden.</p></div><span class="pill">${{(refs.run212ThickEvidenceRecords || []).length}} records</span></div>
          <div class="dataGrid">${{run212Evidence}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.12 design memory seeds</h3><p>${{escapeHtml(refs.run212MemoryStatus)}}. These memory seeds translate thick evidence into native PPT contracts and code binding hints.</p></div><span class="pill">${{(refs.run212MemorySeeds || []).length}} seeds</span></div>
          <div class="dataGrid">${{run212MemorySeeds}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.12 workflow gate seeds</h3><p>${{escapeHtml(refs.run212GateStatus)}}. These are required before the Run 2.13 four-arm rerun and define what trace fields and failure probes must appear.</p></div><span class="pill">${{(refs.run212WorkflowGateSeeds || []).length}} gates</span></div>
          <div class="dataGrid">${{run212WorkflowGates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.15 selector sources</h3><p>${{escapeHtml(refs.run215SelectorSourceStatus)}}. These derived records convert the Run 2.14 aesthetic recovery into layout module selector obligations.</p></div><span class="pill">${{(refs.run215SelectorSources || []).length}} sources</span></div>
          <div class="dataGrid">${{run215SelectorSources}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.15 layout module memory</h3><p>${{escapeHtml(refs.run215SelectorMemoryStatus)}}. This is the layout module selector target layer: editorial cover, product theater, before/after route, metric reveal, quiet handoff, and dense evidence compression.</p></div><span class="pill">${{(refs.run215SelectorModules || []).length}} modules</span></div>
          <div class="dataGrid">${{run215SelectorModules}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Run 2.15 selector gate matrix</h3><p>${{escapeHtml(refs.run215SelectorGateStatus)}}. These gates require text resilience, hidden trace, product theater realism, and bad-control boundaries before the next four-arm rerun.</p></div><span class="pill">${{(refs.run215SelectorGates || []).length}} gates</span></div>
          <div class="dataGrid">${{run215SelectorGates}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Skill workflow stages</h3><p>${{escapeHtml(refs.workflowStatus)}}. This is the ordered product loop, not a one-off prompt.</p></div><span class="pill">${{(refs.workflowStages || []).length}} stages</span></div>
          <div class="dataGrid">${{stages}}</div>
        </section>
        <section class="dataBand">
          <div class="dataBandHead"><div><h3>Vulca PPT Skill</h3><p>The persistent skill contract used to decide what data, memory, code, QA, and release gates mean.</p></div></div>
          <pre class="dataPre">${{skill}}</pre>
        </section>
      </div>`;
    }}

    function render() {{
      renderVersionRail();
      document.querySelectorAll("#viewRail .seg").forEach((item) => {{
        item.classList.toggle("active", item.dataset.view === selectedView);
      }});
      if (selectedView === "series") renderSeries();
      else if (selectedView === "sheet") renderSheets();
      else if (selectedView === "data") renderData();
      else if (selectedView === "audit") renderAudit();
      else renderFour();
      content.scrollTop = 0;
      content.scrollLeft = 0;
    }}

    function openModal(src, title) {{
      modalImage.src = src;
      modalImage.alt = title;
      modalTitle.textContent = title;
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
    }}

    versionRail.addEventListener("click", (event) => {{
      const target = event.target.closest("[data-run]");
      if (!target) return;
      selectedRunId = target.dataset.run;
      selectedView = selectedView || "four";
      render();
    }});

    byId("viewRail").addEventListener("click", (event) => {{
      const target = event.target.closest("[data-view]");
      if (!target) return;
      selectedView = target.dataset.view;
      render();
    }});

    content.addEventListener("click", (event) => {{
      const target = event.target.closest("[data-src]");
      if (!target) return;
      openModal(target.dataset.src, target.dataset.title || target.getAttribute("alt") || "preview");
    }});

    byId("modalClose").addEventListener("click", () => {{
      modal.classList.remove("open");
      modal.setAttribute("aria-hidden", "true");
      modalImage.removeAttribute("src");
    }});
    modal.addEventListener("click", (event) => {{
      if (event.target === modal) byId("modalClose").click();
    }});
    document.addEventListener("keydown", (event) => {{
      if (event.key === "Escape") byId("modalClose").click();
    }});

    render();
  </script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an HTML viewer for PPT run outputs.")
    parser.add_argument(
        "--presentations-dir",
        type=Path,
        default=None,
    )
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    default_presentations_dir = repo_root / "outputs" / DEFAULT_THREAD_ID / "presentations"
    presentations_dir = (args.presentations_dir or default_presentations_dir).resolve()
    out = args.out.resolve() if args.out else presentations_dir / "ppt-run-viewer.html"
    data = build_data(presentations_dir, out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(data), encoding="utf-8")
    print(json.dumps({"html": str(out), "runs": len(data["runs"]), "latest": data["latestRunId"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
