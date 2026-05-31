from __future__ import annotations

from typing import Any


PROMPT_STUDIO_WIDGET_URI = "ui://vulca/prompt-studio.html"


def _clean(value: str | None) -> str:
    return " ".join(str(value or "").split())


def build_followup_message(package: dict[str, Any]) -> str:
    negative_prompt = package["negative_prompt"] or "none"
    generation_notes = package["generation_notes"] or "none"
    rubric_summary = package["rubric_summary"] or "use Vulca's L1-L5 rubric"

    return (
        "Generate an image in ChatGPT using this Vulca prompt. "
        "Preserve the tradition, composition, negative constraints, and rubric "
        "priorities exactly.\n\n"
        f"Title: {package['prompt_title']}\n"
        f"Tradition: {package['tradition']}\n"
        f"Prompt: {package['final_prompt']}\n"
        f"Negative constraints: {negative_prompt}\n"
        f"Generation notes: {generation_notes}\n"
        f"Rubric priorities: {rubric_summary}"
    )


def build_prompt_studio_package(
    *,
    prompt_title: str = "",
    tradition: str = "",
    final_prompt: str,
    negative_prompt: str = "",
    generation_notes: str = "",
    rubric_summary: str = "",
) -> dict[str, Any]:
    final_prompt = _clean(final_prompt)
    if not final_prompt:
        raise ValueError("final_prompt is required for Prompt Studio")

    package: dict[str, Any] = {
        "prompt_title": _clean(prompt_title) or "Vulca image prompt",
        "tradition": _clean(tradition) or "unspecified",
        "final_prompt": final_prompt,
        "negative_prompt": _clean(negative_prompt),
        "generation_notes": _clean(generation_notes),
        "rubric_summary": _clean(rubric_summary),
        "widget_uri": PROMPT_STUDIO_WIDGET_URI,
    }
    package["followup_message"] = build_followup_message(package)
    return package
