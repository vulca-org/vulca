"""Export VULCA Skills to Anthropic SKILL.md format.

SKILL.md is the emerging standard for portable AI skill definitions.
This exporter converts VULCA SkillDefs to SKILL.md format for
cross-platform compatibility (Codex, Manus, OpenClaw, etc.).

Reference: Anthropic SKILL.md specification
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from app.prototype.skills.types import SkillDef

__all__ = ["export_skill_md", "export_all_skills_md"]


def export_skill_md(skill: SkillDef) -> str:
    """Export a single SkillDef to SKILL.md format."""
    tags_str = ", ".join(skill.tags) if skill.tags else "general"
    inputs_str = ", ".join(skill.input_types) if skill.input_types else "any"

    # Build config section
    config_lines = ""
    if skill.config:
        config_items = []
        for k, v in skill.config.items():
            if isinstance(v, dict):
                config_items.append(f"- **{k}**:")
                for sk, sv in v.items():
                    config_items.append(f"  - {sk}: {sv}")
            else:
                config_items.append(f"- **{k}**: {v}")
        config_lines = "\n".join(config_items)

    md = textwrap.dedent(f"""\
    # {skill.name}

    > {skill.description}

    ## Metadata

    | Field | Value |
    |-------|-------|
    | Version | {skill.version} |
    | Author | {skill.author} |
    | Tags | {tags_str} |
    | Input Types | {inputs_str} |

    ## Skill Definition

    This skill evaluates content based on the following criteria:

    {config_lines or "_No additional configuration._"}

    ## Usage

    ```python
    from vulca import evaluate

    result = evaluate(
        image="path/to/image.png",
        skills=["{skill.name}"],
    )
    print(result.score, result.summary)
    ```

    ```bash
    vulca evaluate --skill {skill.name} my-image.png
    ```

    ```yaml
    # VULCA pipeline config
    skills:
      - name: {skill.name}
        version: "{skill.version}"
    ```
    """)

    return md


def export_all_skills_md(output_dir: str | Path) -> int:
    """Export all registered skills to SKILL.md files in output_dir.

    Returns the number of files written.
    """
    from app.prototype.skills import SkillRegistry

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    registry = SkillRegistry.get_instance()
    count = 0

    for skill in registry.list_all():
        md_content = export_skill_md(skill)
        filepath = output / f"{skill.name}.SKILL.md"
        filepath.write_text(md_content, encoding="utf-8")
        count += 1

    return count
