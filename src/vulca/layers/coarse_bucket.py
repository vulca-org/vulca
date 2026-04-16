"""Coarse bucket extraction for multi-layer content_type values.

Multi-layer schema uses dot-notation (subject.face.eyes) and indexed
namespaces (person[0].hair). Call sites that branch on bucket membership
must use coarse_bucket_of() so they don't break when the layer name
gains hierarchy.

Design note: buckets are identified by prefix match on the segment before
the first '.' or '['. Non-matching prefixes are returned verbatim so
callers can decide what to do (rather than hiding unknowns behind a
fallback bucket).
"""
from __future__ import annotations

import logging

_logger = logging.getLogger("vulca.layers.coarse_bucket")
_SEEN_UNKNOWN: set[str] = set()


def _warn_unknown_bucket(head: str) -> None:
    if head in _SEEN_UNKNOWN:
        return
    _SEEN_UNKNOWN.add(head)
    _logger.warning("coarse_bucket: unknown head %r (not in _KNOWN_BUCKETS)", head)


_KNOWN_BUCKETS = frozenset({
    "background",
    "subject",
    "foreground",
    "midground",
    "detail",
    "atmosphere",
    "effect",
    "text",
    "line_art",
    "color_wash",
    "color_block",
    "decoration",
})

_PREFIX_ALIASES = {
    "person": "subject",
}


def coarse_bucket_of(content_type: str) -> str:
    """Extract the coarse bucket from a possibly-dotted content_type.

    >>> coarse_bucket_of("background.catch_all")
    'background'
    >>> coarse_bucket_of("subject.face.eyes")
    'subject'
    >>> coarse_bucket_of("person[0].hair")
    'subject'
    >>> coarse_bucket_of("background_noise")
    'background_noise'
    >>> coarse_bucket_of("")
    'background'
    """
    if not content_type:
        return "background"

    first_dot = content_type.find(".")
    first_bracket = content_type.find("[")
    if first_dot == -1 and first_bracket == -1:
        head = content_type
    else:
        cut = min(p for p in (first_dot, first_bracket) if p != -1)
        head = content_type[:cut]

    if head in _PREFIX_ALIASES:
        return _PREFIX_ALIASES[head]
    if head not in _KNOWN_BUCKETS:
        _warn_unknown_bucket(head)
    return head


def is_background(content_type: str) -> bool:
    """True if the content_type belongs to the background bucket.

    Use this at every call site that currently checks
    `info.content_type == "background"`.
    """
    return coarse_bucket_of(content_type) == "background"
