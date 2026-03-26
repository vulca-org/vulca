"""AttnRes-inspired selective aggregation across pipeline nodes.

Inspired by Kimi's Attention Residuals: instead of fixed residual
connections (flat ctx.data.update), each node's output is preserved
with provenance. Brief acts as a pseudo-query vector to compute
softmax attention weights over all node outputs.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field


@dataclass
class NodeSnapshot:
    """One node's complete output, preserved with provenance."""
    node_name: str
    round_num: int
    output: dict
    summary: str


@dataclass
class ResidualWeights:
    """Attention weights over node snapshots."""
    weights: dict[str, float]
    method: str = "keyword"


_TEMPERATURE = 0.5


def _tokenize(text: str) -> set[str]:
    """Split on non-alphanumeric, keep CJK chars individually + 2-grams."""
    tokens: set[str] = set()
    for word in re.findall(r"[a-zA-Z]+", text.lower()):
        if len(word) > 1:
            tokens.add(word)
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            tokens.add(ch)
    chars = [ch for ch in text if "\u4e00" <= ch <= "\u9fff"]
    for i in range(len(chars) - 1):
        tokens.add(chars[i] + chars[i + 1])
    return tokens


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class AgentResiduals:
    """AttnRes-inspired selective aggregation across pipeline nodes."""

    def __init__(self) -> None:
        self._history: list[NodeSnapshot] = []

    def record(self, node_name: str, round_num: int, output: dict) -> NodeSnapshot:
        summary = self._auto_summary(node_name, output)
        snap = NodeSnapshot(node_name=node_name, round_num=round_num, output=dict(output), summary=summary)
        self._history.append(snap)
        return snap

    def get_history(self) -> list[NodeSnapshot]:
        return list(self._history)

    def compute_weights(self, brief_text: str, snapshots: list[NodeSnapshot]) -> ResidualWeights:
        if not snapshots:
            return ResidualWeights(weights={}, method="keyword")

        brief_tokens = _tokenize(brief_text)
        raw_scores: dict[str, float] = {}
        for snap in snapshots:
            summary_tokens = _tokenize(snap.summary)
            raw_scores[snap.node_name] = _jaccard(brief_tokens, summary_tokens)

        max_score = max(raw_scores.values()) if raw_scores else 0.0
        exp_scores: dict[str, float] = {}
        for name, score in raw_scores.items():
            exp_scores[name] = math.exp((score - max_score) / _TEMPERATURE)

        total = sum(exp_scores.values()) or 1.0
        weights = {name: val / total for name, val in exp_scores.items()}
        return ResidualWeights(weights=weights, method="keyword")

    def aggregate(self, weights: ResidualWeights, snapshots: list[NodeSnapshot]) -> dict:
        node_contributions: dict[str, dict] = {}
        for snap in snapshots:
            node_contributions[snap.node_name] = dict(snap.output)
        dominant = max(weights.weights, key=weights.weights.get) if weights.weights else ""
        return {
            "node_contributions": node_contributions,
            "attention_weights": dict(weights.weights),
            "dominant_node": dominant,
        }

    @staticmethod
    def _auto_summary(node_name: str, output: dict) -> str:
        if node_name in ("scout",):
            guidance = output.get("cultural_guidance", "")
            return str(guidance)[:200] if guidance else node_name

        if node_name in ("generate", "draft"):
            parts = []
            if "subject" in output:
                parts.append(str(output["subject"]))
            if "candidate_id" in output:
                parts.append(f"candidate={output['candidate_id']}")
            if "improvement_focus" in output:
                parts.append(str(output["improvement_focus"])[:100])
            return " ".join(parts) if parts else "generated image"

        if node_name in ("evaluate", "critic"):
            parts = []
            scores = output.get("scores", {})
            if scores:
                parts.append(" ".join(f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}" for k, v in scores.items()))
            wt = output.get("weighted_total")
            if wt is not None:
                parts.append(f"total={wt:.2f}" if isinstance(wt, float) else f"total={wt}")
            return " ".join(parts) if parts else "evaluation scores"

        keys = list(output.keys())[:5]
        return " ".join(f"{k}={output[k]}" for k in keys) if keys else node_name
