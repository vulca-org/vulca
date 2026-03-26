"""TurboQuant-inspired zero-training session retrieval.

Uses deterministic character N-gram hashing for approximate semantic
search. Two-stage: N-gram accumulation (PolarQuant analogue) + sign
residual correction (QJL analogue). Zero external dependencies.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class SessionVector:
    """Compressed vector representation of a session."""
    session_id: str
    tradition: str
    intent_hash: int
    signature: list[float]
    scores: dict[str, float]
    user_feedback: str | None = None


@dataclass
class RetrievalResult:
    """A similar session found by retrieval."""
    session_id: str
    similarity: float
    tradition: str
    scores: dict[str, float]


_HASH_SEEDS = [0x9E3779B9, 0x517CC1B7, 0x6C62272E, 0x2E1B2138]
_SIGN_SCALE = 0.1


class QuantizedRetriever:
    """TurboQuant-inspired zero-training session retrieval."""

    def __init__(self, signature_dim: int = 32):
        self.signature_dim = signature_dim
        self._vectors: list[SessionVector] = []
        self._tradition_buckets: dict[str, list[int]] = {}

    def _compute_signature(self, text: str, dim: int | None = None) -> list[float]:
        dim = dim or self.signature_dim
        raw = [0.0] * dim

        for n in (2, 3):
            for i in range(max(0, len(text) - n + 1)):
                ngram = text[i:i + n]
                for seed in _HASH_SEEDS:
                    h = int(hashlib.md5(f"{seed}:{ngram}".encode("utf-8")).hexdigest(), 16)
                    idx = h % dim
                    sign = 1.0 if (h // dim) % 2 == 0 else -1.0
                    raw[idx] += sign

        norm = math.sqrt(sum(x * x for x in raw)) or 1.0
        normalized = [x / norm for x in raw]

        sign_residual = [1.0 if x >= 0 else -1.0 for x in normalized]
        final = [n + _SIGN_SCALE * s for n, s in zip(normalized, sign_residual)]

        norm2 = math.sqrt(sum(x * x for x in final)) or 1.0
        return [x / norm2 for x in final]

    @staticmethod
    def _inner_product(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def add(self, session_id: str, intent: str, tradition: str,
            scores: dict[str, float], feedback: str | None) -> SessionVector:
        sv = SessionVector(session_id=session_id, tradition=tradition, intent_hash=hash(intent),
                           signature=self._compute_signature(intent), scores=dict(scores), user_feedback=feedback)
        idx = len(self._vectors)
        self._vectors.append(sv)
        self._tradition_buckets.setdefault(tradition, []).append(idx)
        return sv

    def query(self, intent: str, tradition: str, top_k: int = 5, min_similarity: float = 0.3) -> list[RetrievalResult]:
        bucket = self._tradition_buckets.get(tradition, [])
        if not bucket:
            return []
        query_sig = self._compute_signature(intent)
        scored: list[tuple[float, SessionVector]] = []
        for idx in bucket:
            sv = self._vectors[idx]
            sim = self._inner_product(query_sig, sv.signature)
            if sim >= min_similarity:
                scored.append((sim, sv))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [RetrievalResult(session_id=sv.session_id, similarity=sim, tradition=sv.tradition, scores=sv.scores)
                for sim, sv in scored[:top_k]]

    def save(self, path: Path) -> None:
        data = [asdict(sv) for sv in self._vectors]
        Path(path).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def load(self, path: Path) -> int:
        self._vectors.clear()
        self._tradition_buckets.clear()
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        for item in raw:
            sv = SessionVector(**item)
            idx = len(self._vectors)
            self._vectors.append(sv)
            self._tradition_buckets.setdefault(sv.tradition, []).append(idx)
        return len(self._vectors)
