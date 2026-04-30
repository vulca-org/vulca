from __future__ import annotations


def _card():
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    return generate_direction_cards(profile, count=3)[0]


def test_openai_prompt_artifact_uses_gpt_image_2_hint():
    from vulca.discovery.prompting import compose_prompt_from_direction_card

    artifact = compose_prompt_from_direction_card(_card(), target="final")
    payload = artifact.to_dict()

    assert payload["provider"] == "openai"
    assert payload["model"] == "gpt-image-2"
    assert "large negative space" in payload["prompt"]
    assert "avoid:" not in payload["prompt"].lower()
    assert "generic minimalism unrelated to subject" in payload["negative_prompt"]


def test_gemini_prompt_artifact_uses_sketch_hint():
    from vulca.discovery.prompting import compose_prompt_from_direction_card

    artifact = compose_prompt_from_direction_card(_card(), target="sketch")

    assert artifact.provider == "gemini"
    assert artifact.model == "gemini-3.1-flash-image-preview"
    assert "exploratory thumbnail" in artifact.prompt


def test_unknown_target_rejected():
    import pytest

    from vulca.discovery.prompting import compose_prompt_from_direction_card

    with pytest.raises(ValueError, match="unknown provider target"):
        compose_prompt_from_direction_card(_card(), target="video")


def test_comfyui_prompt_artifact_is_clip_friendly():
    from vulca.discovery.prompting import compose_prompt_from_direction_card

    card = _card()
    final = compose_prompt_from_direction_card(card, target="final")
    local = compose_prompt_from_direction_card(card, target="local")

    assert local.provider == "comfyui"
    assert "CLIP-friendly" in local.prompt
    assert "high-fidelity commercial visual candidate" not in local.prompt
    assert len(local.prompt) < len(final.prompt)
