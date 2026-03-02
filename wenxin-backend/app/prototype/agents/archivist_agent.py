"""Archivist Agent — generates auditable archive for each pipeline run.

Produces:
- evidence_chain.json: Full trace from Scout → Critic → Queen per round
- critique_card.md: Human-readable Markdown critique report
- params_snapshot.json: All configuration parameters snapshot
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from app.prototype.agents.archivist_types import ArchivistInput, ArchivistOutput

__all__ = [
    "ArchivistAgent",
]

_ARCHIVE_ROOT = Path(__file__).resolve().parent.parent / "checkpoints" / "archive"
_SAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")


class ArchivistAgent:
    """Generate a complete, auditable archive for a pipeline run."""

    def run(self, archivist_input: ArchivistInput) -> ArchivistOutput:
        task_id = archivist_input.task_id
        task_dir = _ARCHIVE_ROOT / _safe(task_id)
        task_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 1. Evidence chain
            chain = self._build_evidence_chain(archivist_input)
            chain_path = task_dir / "evidence_chain.json"
            chain_path.write_text(
                json.dumps(chain, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            # 2. Critique card
            card = self._build_critique_card(archivist_input, chain)
            card_path = task_dir / "critique_card.md"
            card_path.write_text(card, encoding="utf-8")

            # 3. Params snapshot
            params = {
                "draft_config": archivist_input.draft_config_dict,
                "critic_config": archivist_input.critic_config_dict,
                "queen_config": archivist_input.queen_config_dict,
                "archived_at": datetime.now(timezone.utc).isoformat(),
            }
            params_path = task_dir / "params_snapshot.json"
            params_path.write_text(
                json.dumps(params, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            return ArchivistOutput(
                task_id=task_id,
                evidence_chain_path=str(chain_path),
                critique_card_path=str(card_path),
                params_snapshot_path=str(params_path),
                success=True,
            )

        except Exception as exc:
            return ArchivistOutput(task_id=task_id, success=False, error=str(exc))

    def _build_evidence_chain(self, inp: ArchivistInput) -> dict:
        """Build the full evidence chain JSON."""
        rounds: list[dict] = []
        n_rounds = max(len(inp.critique_dicts), len(inp.queen_dicts))

        for i in range(n_rounds):
            round_data: dict = {"round": i + 1}

            # Scout evidence (same for all rounds)
            round_data["scout"] = {
                "sample_matches": inp.scout_evidence_dict.get("sample_matches", []),
                "terminology_hits": inp.scout_evidence_dict.get("terminology_hits", []),
                "taboo_violations": inp.scout_evidence_dict.get("taboo_violations", []),
            }

            # Critique for this round
            if i < len(inp.critique_dicts):
                crit = inp.critique_dicts[i]
                round_data["critic"] = {
                    "scored_candidates": crit.get("scored_candidates", []),
                    "best_candidate_id": crit.get("best_candidate_id"),
                    "rerun_hint": crit.get("rerun_hint", []),
                }

            # Queen decision for this round
            if i < len(inp.queen_dicts):
                q = inp.queen_dicts[i]
                decision = q.get("decision", {})
                round_data["queen"] = {
                    "action": decision.get("action", ""),
                    "reason": decision.get("reason", ""),
                    "rerun_dimensions": decision.get("rerun_dimensions", []),
                }

            rounds.append(round_data)

        pipeline = inp.pipeline_output_dict
        return {
            "task_id": inp.task_id,
            "subject": inp.subject,
            "cultural_tradition": inp.cultural_tradition,
            "rounds": rounds,
            "final_decision": pipeline.get("final_decision", ""),
            "best_candidate_id": pipeline.get("best_candidate_id"),
            "total_rounds": pipeline.get("total_rounds", 0),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _build_critique_card(self, inp: ArchivistInput, chain: dict) -> str:
        """Build a human-readable Markdown critique card."""
        lines: list[str] = []
        lines.append(f"# Critique Card: {inp.subject}")
        lines.append("")
        lines.append(f"## Cultural Tradition: {inp.cultural_tradition}")
        lines.append("")
        lines.append(f"## Final Decision: {chain.get('final_decision', 'N/A')}")
        lines.append(f"## Best Candidate: {chain.get('best_candidate_id', 'N/A')}")
        lines.append(f"## Total Rounds: {chain.get('total_rounds', 0)}")
        lines.append("")

        # L1-L5 scores from last critique round
        if inp.critique_dicts:
            last_crit = inp.critique_dicts[-1]
            scored = last_crit.get("scored_candidates", [])
            if scored:
                best_sc = scored[0]  # top scorer
                lines.append("## L1-L5 Scores")
                lines.append("")
                lines.append("| Dimension | Score | Rationale |")
                lines.append("|-----------|-------|-----------|")
                for ds in best_sc.get("dimension_scores", []):
                    dim = ds.get("dimension", "?")
                    score = ds.get("score", 0.0)
                    rationale = ds.get("rationale", "")
                    lines.append(f"| {dim} | {score:.2f} | {rationale} |")
                lines.append("")
                lines.append(f"**Weighted Total**: {best_sc.get('weighted_total', 0.0):.4f}")
                lines.append(f"**Gate Passed**: {best_sc.get('gate_passed', False)}")
                lines.append("")

                # Risk assessment
                risk_tags = best_sc.get("risk_tags", [])
                lines.append("## Risk Assessment")
                lines.append("")
                if risk_tags:
                    for tag in risk_tags:
                        lines.append(f"- {tag}")
                else:
                    lines.append("- No risk tags detected")
                lines.append("")

        # Evidence summary
        ev = inp.scout_evidence_dict
        lines.append("## Evidence Summary")
        lines.append("")
        lines.append(f"- Sample matches: {len(ev.get('sample_matches', []))}")
        lines.append(f"- Terminology hits: {len(ev.get('terminology_hits', []))}")
        lines.append(f"- Taboo violations: {len(ev.get('taboo_violations', []))}")
        lines.append("")

        # Decision history
        if len(chain.get("rounds", [])) > 1:
            lines.append("## Decision History")
            lines.append("")
            for r in chain.get("rounds", []):
                queen = r.get("queen", {})
                lines.append(f"- Round {r.get('round', '?')}: {queen.get('action', '?')} — {queen.get('reason', '')}")
            lines.append("")

        return "\n".join(lines)


def _safe(task_id: str) -> str:
    cleaned = _SAFE_RE.sub("_", task_id).strip("._")
    return cleaned or "task"
