"""v0.13.2 P2: LayerFailure.reason must be a Literal, not bare str."""
from __future__ import annotations

import sys
import typing

import vulca.layers.layered_generate as lg_mod
from vulca.layers.layered_generate import LayerFailure


def test_reason_annotation_is_literal():
    # Evaluate just the `reason` annotation against the module globals so we
    # don't depend on get_type_hints succeeding for the whole dataclass
    # (py3.9 chokes on PEP 604 `X | None` siblings under `from __future__
    # import annotations`).
    raw = LayerFailure.__annotations__["reason"]
    if isinstance(raw, str):
        reason_t = eval(raw, vars(lg_mod), {"typing": typing})
    else:
        reason_t = raw
    origin = typing.get_origin(reason_t)
    assert origin is typing.Literal, (
        f"LayerFailure.reason must be typing.Literal, got {reason_t!r}"
    )
    args = set(typing.get_args(reason_t))
    assert args == {"generation_failed", "validation_failed"}, args
