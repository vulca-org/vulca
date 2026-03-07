"""AdminAgent - Orchestrates EvolutionAgent and QualityAgent, generates weekly reports.

On each cycle:
1. Runs EvolutionAgent and QualityAgent
2. Collects their results
3. Generates a weekly ecosystem report (markdown)
4. Saves report to data/reports/weekly_YYYY-MM-DD.md
5. Returns status summary
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from app.prototype.evolution.base_agent import BaseAgent
from app.prototype.evolution.evolution_agent import EvolutionAgent
from app.prototype.evolution.quality_agent import QualityAgent

logger = logging.getLogger(__name__)

_REPORTS_DIR = Path(__file__).parent.parent / "data" / "reports"


@dataclass
class AdminAgent(BaseAgent):
    """Orchestrates sub-agents and produces weekly ecosystem reports."""

    name: str = "admin"
    evolution_agent: EvolutionAgent = field(default_factory=EvolutionAgent)
    quality_agent: QualityAgent = field(default_factory=QualityAgent)

    async def run_cycle(self) -> dict:
        """Execute one admin cycle.

        Returns
        -------
        dict with keys:
          - report_path: str
          - status: "healthy" | "warning" | "critical"
        """
        self.log_action("cycle_start")

        # 1. Run sub-agents
        evolution_result = await self.evolution_agent.run_cycle()
        self.log_action("evolution_complete", evolution_result)

        quality_result = await self.quality_agent.run_cycle()
        self.log_action("quality_complete", quality_result)

        # 2. Determine ecosystem status
        status = self._determine_status(evolution_result, quality_result)

        # 3. Generate weekly report
        report_path = self._generate_report(evolution_result, quality_result, status)

        result = {
            "report_path": str(report_path),
            "status": status,
        }
        self.log_action("cycle_complete", result)
        return result

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _determine_status(
        self,
        evolution_result: dict[str, Any],
        quality_result: dict[str, Any],
    ) -> str:
        """Determine overall ecosystem health status."""
        anomalies = quality_result.get("anomalies", 0)
        drift = quality_result.get("drift_detected", False)

        if drift and anomalies > 5:
            return "critical"
        if drift or anomalies > 2:
            return "warning"
        return "healthy"

    def _generate_report(
        self,
        evolution_result: dict[str, Any],
        quality_result: dict[str, Any],
        status: str,
    ) -> Path:
        """Generate a weekly ecosystem report in markdown."""
        now = datetime.utcnow()
        date_str = now.strftime("%Y-%m-%d")
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")

        status_emoji_map = {
            "healthy": "OK",
            "warning": "WARN",
            "critical": "CRIT",
        }
        status_label = status_emoji_map.get(status, status)

        # Build markdown content
        lines = [
            f"# VULCA Ecosystem Weekly Report",
            f"",
            f"**Date**: {timestamp}",
            f"**Status**: {status_label} ({status})",
            f"",
            f"---",
            f"",
            f"## Evolution Agent Summary",
            f"",
            f"- **Principles distilled**: {evolution_result.get('principles', 0)}",
            f"- **Weight adjustments**: {len(evolution_result.get('adjustments', {}))} traditions affected",
            f"",
        ]

        adjustments = evolution_result.get("adjustments", {})
        if adjustments:
            lines.append("### Weight Adjustments")
            lines.append("")
            lines.append("| Tradition | Delta |")
            lines.append("|-----------|-------|")
            for tradition, delta in sorted(adjustments.items()):
                sign = "+" if delta >= 0 else ""
                lines.append(f"| {tradition} | {sign}{delta:.4f} |")
            lines.append("")

        lines.extend([
            f"## Quality Agent Summary",
            f"",
            f"- **Average score**: {quality_result.get('avg_score', 'N/A')}",
            f"- **Drift detected**: {'Yes' if quality_result.get('drift_detected') else 'No'}",
            f"- **Anomalies flagged**: {quality_result.get('anomalies', 0)}",
            f"",
            f"---",
            f"",
            f"## Recommendations",
            f"",
        ])

        if status == "critical":
            lines.append("1. **Immediate action required**: Significant quality drift and anomalies detected.")
            lines.append("2. Review recent evaluation pipeline changes.")
            lines.append("3. Consider rolling back to previous evolved context.")
        elif status == "warning":
            lines.append("1. Monitor quality metrics closely over the next cycle.")
            lines.append("2. Investigate flagged anomalies for root cause.")
        else:
            lines.append("1. System operating within normal parameters.")
            lines.append("2. Continue regular monitoring cycles.")

        lines.append("")
        lines.append(f"*Generated by AdminAgent at {timestamp}*")
        lines.append("")

        # Write report
        _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = _REPORTS_DIR / f"weekly_{date_str}.md"
        report_path.write_text("\n".join(lines), encoding="utf-8")

        logger.info("Weekly report saved to %s", report_path)
        return report_path
