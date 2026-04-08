"""A-path layered generation library.

Pure orchestration: plan → concurrent provider calls → keying → validate.
Decoupled from the pipeline so it can be called from CLI, MCP, SDK, or tests.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from vulca.layers.types import LayerInfo
from vulca.layers.validate import ValidationReport


@dataclass
class LayerOutcome:
    ok: bool
    info: LayerInfo
    rgba_path: str = ""
    cache_hit: bool = False
    attempts: int = 1
    validation: ValidationReport | None = None


@dataclass
class LayerFailure:
    layer_id: str
    role: str
    reason: str
    attempts: int = 1


@dataclass
class LayeredResult:
    layers: list[LayerOutcome] = field(default_factory=list)
    failed: list[LayerFailure] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return not self.failed

    @property
    def is_usable(self) -> bool:
        if not self.layers:
            return False
        has_subject = any(
            l.info.content_type in ("subject", "line_art", "color_block", "color_wash", "detail")
            for l in self.layers
        )
        return has_subject
