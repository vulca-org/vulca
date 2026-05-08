from __future__ import annotations

from vulca.content_lock import (
    apply_content_fidelity_gate,
    build_content_fidelity_prompt,
    build_content_lock_prompt,
    extract_content_lock,
)


def test_extracts_required_subjects_and_attributes_from_caption():
    lock = extract_content_lock(
        "Ink and wash painting of delicate bamboo and orchid grasses beside "
        "vertical Chinese calligraphy and red seals on aged paper, with sparse "
        "brushwork and a calm scholarly composition."
    )

    assert lock.required_subjects == ["bamboo", "orchid grasses"]
    assert lock.required_text_elements == ["vertical Chinese calligraphy", "red seals"]
    assert lock.required_surface == ["aged paper"]
    assert "sparse brushwork" in lock.required_style_attributes
    assert "calm scholarly composition" in lock.required_mood


def test_extracts_generic_required_subjects_from_caption():
    lock = extract_content_lock(
        "Editorial illustration of a silver astronaut, cracked moon rover, and "
        "orange emergency flare under a black sky."
    )

    assert lock.required_subjects == [
        "silver astronaut",
        "cracked moon rover",
        "orange emergency flare",
    ]


def test_extracts_declarative_graph_paper_branching_caption():
    lock = extract_content_lock(
        "Abstract hand-drawn branching lines fill a rectangular frame on graph "
        "paper, forming a dense tree-like network with a small heart and "
        "geometric marks in monochrome pencil style."
    )

    assert "hand-drawn branching lines" in lock.required_subjects
    assert "dense tree-like network" in lock.required_subjects
    assert "small heart" in lock.required_subjects
    assert "geometric marks" in lock.required_subjects
    assert lock.required_surface == ["graph paper"]
    assert "rectangular frame" in lock.required_style_attributes
    assert "monochrome pencil style" in lock.required_style_attributes


def test_extracts_gongbi_album_leaf_subjects_and_format():
    lock = extract_content_lock(
        "Gongbi album leaf with a small bird perched beside sparse branches, "
        "a circular calligraphy panel, and an ornate pale patterned border."
    )

    assert "small bird" in lock.required_subjects
    assert "sparse branches" in lock.required_subjects
    assert "circular calligraphy panel" in lock.required_text_elements
    assert "ornate pale patterned border" in lock.required_surface
    assert "Gongbi album leaf" in lock.required_style_attributes


def test_content_lock_prompt_makes_subjects_non_negotiable():
    lock = extract_content_lock(
        "Ink and wash painting of delicate bamboo and orchid grasses beside "
        "vertical Chinese calligraphy and red seals on aged paper."
    )

    prompt = build_content_lock_prompt(lock)

    assert "NON-NEGOTIABLE CONTENT REQUIREMENTS" in prompt
    assert "bamboo" in prompt
    assert "orchid grasses" in prompt
    assert "vertical Chinese calligraphy" in prompt
    assert "red seals" in prompt
    assert (
        "Do not replace these subjects with mountains, generic landscapes, "
        "or unrelated tradition prototypes."
    ) in prompt


def test_content_lock_prompt_bans_visible_ids_and_gallery_artifacts():
    lock = extract_content_lock(
        "Abstract hand-drawn branching lines fill a rectangular frame on graph "
        "paper in monochrome pencil style."
    )

    prompt = build_content_lock_prompt(lock)

    assert "sample IDs" in prompt
    assert "gallery" in prompt.lower()
    assert "large labels" in prompt


def test_content_fidelity_prompt_requests_missing_elements():
    lock = extract_content_lock(
        "Ink and wash painting of bamboo beside vertical Chinese calligraphy."
    )

    prompt = build_content_fidelity_prompt(lock)

    assert "CONTENT FIDELITY CHECK" in prompt
    assert "missing_required_subjects" in prompt
    assert "missing_required_text_elements" in prompt
    assert "bamboo" in prompt
    assert "vertical Chinese calligraphy" in prompt
    assert "forbidden_visual_artifacts" in prompt


def test_content_fidelity_prompt_requests_missing_style_attributes():
    lock = extract_content_lock(
        "Abstract hand-drawn branching lines fill a rectangular frame on graph "
        "paper in monochrome pencil style."
    )

    prompt = build_content_fidelity_prompt(lock)

    assert "missing_required_style_attributes" in prompt
    assert "rectangular frame" in prompt
    assert "monochrome pencil style" in prompt


def test_missing_required_subject_caps_high_score():
    result = {
        "scores": {"L1": 0.95, "L2": 0.92, "L3": 1.0, "L4": 1.0, "L5": 0.94},
        "weighted_total": 0.965,
        "rationales": {},
    }
    gate = {
        "required_subjects": ["bamboo", "orchid grasses"],
        "missing_required_subjects": ["bamboo", "orchid grasses"],
    }

    gated = apply_content_fidelity_gate(result, gate)

    assert gated["weighted_total"] == 0.25
    assert gated["scores"]["L3"] <= 0.25
    assert "content_fidelity_failed" in gated["risk_flags"]
    assert (
        "Missing required subjects: bamboo, orchid grasses"
        in gated["rationales"]["content_fidelity"]
    )


def test_missing_required_text_element_caps_high_score():
    result = {
        "scores": {"L1": 0.95, "L2": 0.92, "L3": 1.0, "L4": 1.0, "L5": 0.94},
        "weighted_total": 0.965,
        "rationales": {},
    }
    gate = {
        "required_text_elements": ["vertical Chinese calligraphy"],
        "missing_required_text_elements": ["vertical Chinese calligraphy"],
    }

    gated = apply_content_fidelity_gate(result, gate)

    assert gated["weighted_total"] == 0.25
    assert "content_fidelity_failed" in gated["risk_flags"]
    assert "Missing required text elements" in gated["rationales"]["content_fidelity"]


def test_missing_required_style_attribute_caps_high_score():
    result = {
        "scores": {"L1": 0.95, "L2": 0.92, "L3": 1.0, "L4": 1.0, "L5": 0.94},
        "weighted_total": 0.965,
        "rationales": {},
    }
    gate = {
        "required_style_attributes": ["monochrome pencil style"],
        "missing_required_style_attributes": ["monochrome pencil style"],
    }

    gated = apply_content_fidelity_gate(result, gate)

    assert gated["weighted_total"] == 0.25
    assert "content_fidelity_failed" in gated["risk_flags"]
    assert "Missing required style attributes" in gated["rationales"]["content_fidelity"]


def test_forbidden_visual_artifact_caps_high_score():
    result = {
        "scores": {"L1": 0.95, "L2": 0.92, "L3": 1.0, "L4": 1.0, "L5": 0.94},
        "weighted_total": 0.965,
        "rationales": {},
    }
    gate = {
        "forbidden_visual_artifacts": ["visible sample ID", "gallery photo mockup"],
    }

    gated = apply_content_fidelity_gate(result, gate)

    assert gated["weighted_total"] == 0.25
    assert "content_fidelity_failed" in gated["risk_flags"]
    assert "Forbidden visual artifacts" in gated["rationales"]["content_fidelity"]


def test_present_required_subjects_do_not_cap_score():
    result = {
        "scores": {"L1": 0.95, "L2": 0.92, "L3": 1.0, "L4": 1.0, "L5": 0.94},
        "weighted_total": 0.965,
        "rationales": {},
    }
    gate = {
        "required_subjects": ["bamboo", "orchid grasses"],
        "missing_required_subjects": [],
    }

    gated = apply_content_fidelity_gate(result, gate)

    assert gated["weighted_total"] == 0.965
    assert gated["scores"]["L3"] == 1.0
    assert gated.get("risk_flags", []) == []
