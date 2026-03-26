"""Engram-inspired hash-indexed cultural knowledge retrieval.

Inspired by DeepSeek's Engram: O(1) lookup by tag instead of
full tradition dump into VLM prompt. Uses inverted index over
cultural fragments with dimension-aware scoring.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from vulca.cultural.types import TraditionConfig, TermEntry, TabooEntry


@dataclass
class CulturalFragment:
    """Minimal cultural knowledge unit (one Engram memory slot)."""
    fragment_id: str
    tradition: str
    category: str
    tags: list[str]
    content: str
    l_dimensions: list[str]
    weight: float = 0.5


@dataclass
class EngramQuery:
    """Retrieval query: structured Brief representation."""
    intent: str = ""
    tradition: str = ""
    tags: list[str] = field(default_factory=list)
    active_dimensions: list[str] = field(default_factory=list)


@dataclass
class EngramResult:
    """Retrieval result: ranked cultural fragments."""
    fragments: list[CulturalFragment] = field(default_factory=list)
    total_tokens_estimate: int = 0
    coverage: dict[str, float] = field(default_factory=dict)


_CHARS_PER_TOKEN = 3
_DIM_BONUS = 1.5


class CulturalEngram:
    """Engram-inspired hash-indexed cultural knowledge retrieval."""

    def __init__(self, max_fragments: int = 12, max_tokens: int = 800):
        self.max_fragments = max_fragments
        self.max_tokens = max_tokens
        self._tag_index: dict[str, list[CulturalFragment]] = {}
        self._tradition_fragments: dict[str, list[CulturalFragment]] = {}
        self._vocabulary: set[str] = set()

    def build_index(self, traditions: dict[str, TraditionConfig]) -> int:
        self._tag_index.clear()
        self._tradition_fragments.clear()
        self._vocabulary.clear()
        total = 0

        for name, config in traditions.items():
            fragments: list[CulturalFragment] = []

            for term in config.terminology:
                tags = [term.term]
                if term.term_zh and term.term_zh != term.term:
                    tags.append(term.term_zh)
                tags.extend(term.aliases)
                tags = [t.lower() for t in tags if t]

                frag_id = hashlib.md5(f"{name}:{term.term}:{term.definition}".encode()).hexdigest()[:12]
                content = (
                    f"{term.term}: {term.definition}"
                    if isinstance(term.definition, str)
                    else f"{term.term}: {next(iter(term.definition.values()), '')}"
                )

                frag = CulturalFragment(
                    fragment_id=frag_id,
                    tradition=name,
                    category="terminology",
                    tags=tags,
                    content=content,
                    l_dimensions=list(term.l_levels),
                    weight=0.7,
                )
                fragments.append(frag)
                self._vocabulary.update(tags)

            for taboo in config.taboos:
                tags = [p.lower() for p in taboo.trigger_patterns]
                tags.append(taboo.severity)
                frag_id = hashlib.md5(f"{name}:taboo:{taboo.rule}".encode()).hexdigest()[:12]

                frag = CulturalFragment(
                    fragment_id=frag_id,
                    tradition=name,
                    category="taboo",
                    tags=tags,
                    content=f"[TABOO] {taboo.rule}: {taboo.explanation}",
                    l_dimensions=list(taboo.l_levels),
                    weight=0.6,
                )
                fragments.append(frag)
                self._vocabulary.update(tags)

            self._tradition_fragments[name] = fragments
            total += len(fragments)

            for frag in fragments:
                for tag in frag.tags:
                    self._tag_index.setdefault(tag, []).append(frag)

        return total

    def query(self, q: EngramQuery) -> EngramResult:
        candidates: dict[str, tuple[CulturalFragment, float]] = {}

        if q.tags:
            for tag in q.tags:
                tag_lower = tag.lower()
                for frag in self._tag_index.get(tag_lower, []):
                    if q.tradition and frag.tradition != q.tradition:
                        continue
                    score = candidates.get(frag.fragment_id, (frag, 0.0))[1]
                    candidates[frag.fragment_id] = (frag, score + frag.weight)
        else:
            for frag in self._tradition_fragments.get(q.tradition, []):
                candidates[frag.fragment_id] = (frag, frag.weight)

        if q.active_dimensions:
            for fid, (frag, score) in list(candidates.items()):
                if any(d in frag.l_dimensions for d in q.active_dimensions):
                    candidates[fid] = (frag, score * _DIM_BONUS)

        sorted_candidates = sorted(candidates.values(), key=lambda x: x[1], reverse=True)

        result_fragments: list[CulturalFragment] = []
        total_chars = 0
        max_chars = self.max_tokens * _CHARS_PER_TOKEN

        for frag, _score in sorted_candidates:
            if len(result_fragments) >= self.max_fragments:
                break
            frag_chars = len(frag.content)
            if total_chars + frag_chars > max_chars and result_fragments:
                break
            result_fragments.append(frag)
            total_chars += frag_chars

        coverage: dict[str, float] = {}
        dims_requested = set(q.active_dimensions) if q.active_dimensions else {"L1", "L2", "L3", "L4", "L5"}
        for dim in dims_requested:
            matching = sum(1 for f in result_fragments if dim in f.l_dimensions)
            total_in_tradition = sum(
                1 for f in self._tradition_fragments.get(q.tradition, []) if dim in f.l_dimensions
            )
            coverage[dim] = matching / max(total_in_tradition, 1)

        return EngramResult(
            fragments=result_fragments,
            total_tokens_estimate=max(1, total_chars // _CHARS_PER_TOKEN),
            coverage=coverage,
        )

    def invalidate(self, tradition: str) -> None:
        fragments = self._tradition_fragments.pop(tradition, [])
        for frag in fragments:
            for tag in frag.tags:
                if tag in self._tag_index:
                    self._tag_index[tag] = [f for f in self._tag_index[tag] if f.tradition != tradition]

    def extract_tags(self, text: str) -> list[str]:
        found: list[str] = []
        text_lower = text.lower()
        sorted_vocab = sorted(self._vocabulary, key=len, reverse=True)
        for term in sorted_vocab:
            if term in text_lower:
                found.append(term)
        seen: set[str] = set()
        result: list[str] = []
        for tag in found:
            if tag not in seen:
                seen.add(tag)
                result.append(tag)
        return result
