"""Brief -- the living YAML document that drives Studio sessions."""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from vulca.studio.types import (
    BriefUpdate, Composition, Element, GenerationRound,
    Palette, Reference, StyleWeight,
)


@dataclass
class Brief:
    session_id: str = ""
    version: int = 1
    created_at: str = ""
    updated_at: str = ""

    intent: str = ""
    mood: str = ""
    style_mix: list[StyleWeight] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    user_sketch: str = ""

    concept_candidates: list[str] = field(default_factory=list)
    selected_concept: str = ""
    concept_notes: str = ""
    composition: Composition = field(default_factory=Composition)
    palette: Palette = field(default_factory=Palette)
    elements: list[Element] = field(default_factory=list)

    must_have: list[str] = field(default_factory=list)
    must_avoid: list[str] = field(default_factory=list)
    eval_criteria: dict[str, str] = field(default_factory=dict)

    generations: list[GenerationRound] = field(default_factory=list)
    updates: list[BriefUpdate] = field(default_factory=list)

    @classmethod
    def new(cls, intent: str, *, mood: str = "", style_mix: list[StyleWeight] | None = None,
            elements: list[Element] | None = None, must_have: list[str] | None = None,
            must_avoid: list[str] | None = None) -> Brief:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        return cls(session_id=uuid.uuid4().hex[:8], created_at=now, updated_at=now,
                   intent=intent, mood=mood, style_mix=style_mix or [],
                   elements=elements or [], must_have=must_have or [], must_avoid=must_avoid or [])

    def to_yaml(self) -> str:
        return yaml.dump(asdict(self), allow_unicode=True, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> Brief:
        return cls._from_dict(yaml.safe_load(yaml_str))

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> Brief:
        b = cls()
        for key in ("session_id", "version", "created_at", "updated_at", "intent", "mood",
                     "user_sketch", "selected_concept", "concept_notes", "concept_candidates",
                     "must_have", "must_avoid", "eval_criteria"):
            if key in data:
                setattr(b, key, data[key])
        if "style_mix" in data:
            b.style_mix = [StyleWeight(**s) for s in data["style_mix"]]
        if "references" in data:
            b.references = [Reference(**r) for r in data["references"]]
        if "elements" in data:
            b.elements = [Element(**e) for e in data["elements"]]
        if "generations" in data:
            b.generations = [GenerationRound(**g) for g in data["generations"]]
        if "updates" in data:
            b.updates = [BriefUpdate(**u) for u in data["updates"]]
        if "composition" in data and isinstance(data["composition"], dict):
            b.composition = Composition(**data["composition"])
        if "palette" in data and isinstance(data["palette"], dict):
            b.palette = Palette(**data["palette"])
        return b

    def save(self, project_dir: str | Path) -> Path:
        project_dir = Path(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
        filepath = project_dir / "brief.yaml"
        filepath.write_text(self.to_yaml(), encoding="utf-8")
        return filepath

    @classmethod
    def load(cls, project_dir: str | Path) -> Brief:
        return cls.from_yaml((Path(project_dir) / "brief.yaml").read_text(encoding="utf-8"))

    # Known Brief fields for validation
    _KNOWN_FIELDS = {
        "session_id", "version", "created_at", "updated_at",
        "intent", "mood", "style_mix", "references", "user_sketch",
        "concept_candidates", "selected_concept", "concept_notes",
        "composition", "palette", "elements",
        "must_have", "must_avoid", "eval_criteria",
        "generations", "updates",
    }

    def update_field(self, field_path: str, value: Any) -> None:
        """Update a field by dotted path. Validates field exists."""
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.updated_at = now
        parts = field_path.split(".")
        if parts[0] not in self._KNOWN_FIELDS:
            raise ValueError(f"Unknown Brief field: {parts[0]}")
        if len(parts) == 1:
            setattr(self, parts[0], value)
        elif len(parts) == 2:
            parent = getattr(self, parts[0])
            if not hasattr(parent, parts[1]):
                raise ValueError(f"Unknown nested field: {field_path}")
            setattr(parent, parts[1], value)
        self.updates.append(BriefUpdate(timestamp=now, instruction=f"set {field_path} = {value!r}",
                                        fields_changed=[field_path]))
