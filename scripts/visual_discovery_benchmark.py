"""Benchmark scaffolding for visual-discovery prompt guidance."""
from __future__ import annotations

from pathlib import Path

from vulca.discovery.prompting import compose_prompt_from_direction_card
from vulca.discovery.types import DirectionCard


PROVIDERS = [
    {
        "label": "OpenAI GPT Image 2",
        "provider": "openai",
        "model": "gpt-image-2",
    },
    {
        "label": "Gemini / Nano Banana",
        "provider": "gemini",
        "model": "gemini-3.1-flash-image-preview",
    },
    {"label": "ComfyUI", "provider": "comfyui", "model": ""},
]


def build_conditions(base_prompt: str, card: DirectionCard) -> list[dict[str, str]]:
    ops = card.visual_ops
    compiled = compose_prompt_from_direction_card(card, target="final")
    raw_terms = ", ".join(card.culture_terms)
    visual_ops = "; ".join(
        part
        for part in [
            ops.composition,
            ops.color,
            ops.texture,
            ops.symbol_strategy,
        ]
        if part
    )
    return [
        {
            "id": "A",
            "label": "Baseline user prompt",
            "prompt": base_prompt,
            "source_card_id": "",
        },
        {
            "id": "B",
            "label": "Baseline + raw cultural terms",
            "prompt": f"{base_prompt}. Raw cultural terms: {raw_terms}",
            "source_card_id": card.id,
        },
        {
            "id": "C",
            "label": "Baseline + visual operations",
            "prompt": f"{base_prompt}. Visual operations: {visual_ops}",
            "source_card_id": card.id,
        },
        {
            "id": "D",
            "label": "Raw terms + visual operations",
            "prompt": (
                f"{base_prompt}. Terms: {raw_terms}. "
                f"Visual operations: {visual_ops}"
            ),
            "source_card_id": card.id,
        },
        {
            "id": "E",
            "label": "Raw terms + visual operations + references",
            "prompt": (
                f"{base_prompt}. Terms: {raw_terms}. "
                f"Visual operations: {visual_ops}. "
                "Use provided references when available."
            ),
            "source_card_id": card.id,
        },
        {
            "id": "F",
            "label": "Visual-discovery card compiled prompt",
            "prompt": compiled.prompt,
            "source_card_id": card.id,
        },
    ]


def write_dry_run_report(path: str | Path) -> str:
    provider_lines = "\n".join(
        f"- {item['label']}: provider={item['provider']} "
        f"model={item['model'] or 'default'}"
        for item in PROVIDERS
    )
    report = f"""# Visual Discovery Benchmark Dry Run

## Providers
{provider_lines}

## Conditions
- A: baseline user prompt
- B: baseline + raw cultural/aesthetic terms
- C: baseline + visual operations only
- D: raw terms + visual operations
- E: raw terms + visual operations + reference images
- F: visual-discovery card compiled prompt
"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(report, encoding="utf-8")
    return report


if __name__ == "__main__":
    write_dry_run_report("docs/visual-discovery-benchmark-dry-run.md")
