"""Helpers for deriving structured prompts from visual design artifacts."""
from __future__ import annotations

import re
from pathlib import Path

from vulca.cultural.loader import get_tradition_guide


_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def _parse_yaml_block(raw: str) -> dict:
    import yaml

    parsed = yaml.safe_load(raw) or {}
    if not isinstance(parsed, dict):
        raise ValueError("Expected YAML mapping block")
    return parsed


def _parse_frontmatter(text: str) -> dict:
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        raise ValueError("design.md is missing YAML frontmatter")
    return _parse_yaml_block(match.group(1))


def _extract_section_yaml(text: str, heading: str) -> dict:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\n\n```yaml\n(.*?)\n```",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if match is None:
        raise ValueError(f"design.md is missing section {heading!r}")
    return _parse_yaml_block(match.group(1))


def _format_tradition_tokens(guide: dict) -> list[str]:
    tokens: list[str] = []
    for entry in guide.get("terminology", []):
        if not isinstance(entry, dict):
            continue
        term = str(entry.get("term", "")).strip()
        translation = str(entry.get("translation", "")).strip()
        token = f"{term} {translation}".strip()
        if token:
            tokens.append(token)
    return tokens


def compose_prompt_from_design(design_path: str) -> dict:
    """Compose the execution prompt from a resolved visual-spec design.md."""
    path = Path(design_path)
    text = path.read_text(encoding="utf-8")

    frontmatter = _parse_frontmatter(text)
    _a_block = _extract_section_yaml(text, "A. Provider + generation params")
    c_block = _extract_section_yaml(text, "C. Prompt composition")

    tradition = str(frontmatter.get("tradition", "")).strip()
    if not tradition:
        raise ValueError("design.md frontmatter is missing tradition")

    guide = get_tradition_guide(tradition)
    if guide is None:
        raise ValueError(f"Unknown tradition in design.md: {tradition!r}")

    base_prompt = str(c_block.get("base_prompt", "")).strip()
    negative_prompt = str(c_block.get("negative_prompt", ""))
    tradition_tokens = _format_tradition_tokens(guide)
    color_tokens = [str(token) for token in (c_block.get("color_constraint_tokens") or [])]
    composed_parts = [part for part in [base_prompt, ", ".join(tradition_tokens), ", ".join(color_tokens)] if part]
    composed_prompt = ", ".join(composed_parts)

    return {
        "composed_prompt": composed_prompt,
        "negative_prompt": negative_prompt,
        "tradition_tokens": tradition_tokens,
        "color_tokens": color_tokens,
        "style_treatment": str(c_block.get("style_treatment", "")),
        "source_design_path": design_path,
    }
