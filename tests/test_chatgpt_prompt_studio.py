from __future__ import annotations

import pytest

from vulca.chatgpt_prompt_studio import (
    PROMPT_STUDIO_WIDGET_URI,
    build_prompt_studio_package,
)


def test_build_prompt_studio_package_normalizes_fields():
    package = build_prompt_studio_package(
        prompt_title="  Ink mountain study  ",
        tradition=" chinese_xieyi ",
        final_prompt="  misty mountain ink study with negative space  ",
        negative_prompt=" photorealistic, glossy  ",
        generation_notes=" square composition ",
        rubric_summary=" L5: qi resonance; L3: composition rhythm ",
    )

    assert package["prompt_title"] == "Ink mountain study"
    assert package["tradition"] == "chinese_xieyi"
    assert package["final_prompt"] == "misty mountain ink study with negative space"
    assert package["negative_prompt"] == "photorealistic, glossy"
    assert package["generation_notes"] == "square composition"
    assert package["rubric_summary"] == "L5: qi resonance; L3: composition rhythm"
    assert package["widget_uri"] == PROMPT_STUDIO_WIDGET_URI
    assert package["followup_message"].startswith(
        "Generate an image in ChatGPT using this Vulca prompt."
    )
    assert "Title: Ink mountain study" in package["followup_message"]
    assert "Tradition: chinese_xieyi" in package["followup_message"]
    assert (
        "Negative constraints: photorealistic, glossy"
        in package["followup_message"]
    )


def test_build_prompt_studio_package_uses_safe_defaults():
    package = build_prompt_studio_package(
        prompt_title="",
        tradition="",
        final_prompt="misty mountain",
    )

    assert package["prompt_title"] == "Vulca image prompt"
    assert package["tradition"] == "unspecified"
    assert package["negative_prompt"] == ""
    assert "Negative constraints: none" in package["followup_message"]


def test_build_prompt_studio_package_rejects_empty_final_prompt():
    with pytest.raises(ValueError, match="final_prompt is required"):
        build_prompt_studio_package(
            prompt_title="Ink mountain",
            tradition="chinese_xieyi",
            final_prompt="   ",
        )
