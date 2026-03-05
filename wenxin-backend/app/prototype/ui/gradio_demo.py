#!/usr/bin/env python3
"""Gradio Web UI for the VULCA Prototype Pipeline — step-by-step visualization.

Shows each pipeline stage progressively using PipelineOrchestrator events:
  Stage 1: Scout — evidence gathering (terminology, taboo, samples)
  Stage 2: Draft — candidate image generation (gallery view)
  Stage 3: Critic — L1-L5 scoring per candidate
  Stage 4: Queen — accept / rerun / stop decision
  (If rerun → repeat Stage 2-4)

Supports mock (instant) and nb2 (real NB2 images) providers.

Usage::

    cd wenxin-backend
    python -m app.prototype.ui.gradio_demo
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.prototype.agents.critic_config import CriticConfig
from app.prototype.agents.draft_config import DraftConfig
from app.prototype.agents.queen_config import QueenConfig
from app.prototype.orchestrator.events import EventType
from app.prototype.orchestrator.orchestrator import PipelineOrchestrator
from app.prototype.pipeline.pipeline_types import PipelineInput

TRADITIONS = [
    "chinese_xieyi", "chinese_gongbi", "western_academic",
    "islamic_geometric", "watercolor", "african_traditional",
    "south_asian", "default",
]

_NO_IMAGES: list = []


def _build_scout_md(evidence: dict) -> str:
    """Format scout evidence as markdown."""
    lines = ["## Stage 1: Scout — Evidence Gathering\n"]
    samples = evidence.get("sample_matches", [])
    terms = evidence.get("terminology_hits", [])
    taboos = evidence.get("taboo_violations", [])

    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| Sample matches | **{len(samples)}** |")
    lines.append(f"| Terminology hits | **{len(terms)}** |")
    lines.append(f"| Taboo violations | **{len(taboos)}** |")

    if terms:
        lines.append("\n**Terminology:**")
        for t in terms[:5]:
            lines.append(f"- {t.get('term', '?')} ({t.get('tradition', '?')})")

    if taboos:
        lines.append("\n**⚠ Taboo Violations Detected:**")
        for v in taboos:
            lines.append(f"- **{v.get('term', '?')}** — {v.get('description', '')}")

    return "\n".join(lines)


def _build_critic_md(scored_candidates: list, best_id: str | None) -> str:
    """Format critic scoring as markdown table."""
    lines = ["## Stage 3: Critic — L1-L5 Scoring\n"]

    if not scored_candidates:
        lines.append("*No candidates to score.*")
        return "\n".join(lines)

    dims = [ds["dimension"] for ds in scored_candidates[0].get("dimension_scores", [])]
    dim_short = [d.replace("_", " ").title()[:12] for d in dims]

    lines.append(f"| Candidate | {' | '.join(dim_short)} | **Total** | Gate |")
    lines.append(f"|-----------|{'|'.join(['---'] * len(dims))}|------|------|")

    for sc in scored_candidates:
        cid = sc["candidate_id"].split("-")[-1]
        scores_str = " | ".join(
            f"{ds['score']:.2f}" for ds in sc.get("dimension_scores", [])
        )
        total = sc.get("weighted_total", 0)
        gate = "PASS" if sc.get("gate_passed") else "FAIL"
        best_mark = " **★**" if sc["candidate_id"] == best_id else ""
        lines.append(f"| #{cid}{best_mark} | {scores_str} | **{total:.3f}** | {gate} |")

    if best_id:
        lines.append(f"\n**Best candidate: {best_id}**")

    all_risks = set()
    for sc in scored_candidates:
        all_risks.update(sc.get("risk_tags", []))
    if all_risks:
        lines.append(f"\nRisk tags: {', '.join(sorted(all_risks))}")

    return "\n".join(lines)


def _build_queen_md(decision: str, reason: str, round_num: int) -> str:
    """Format queen decision as markdown."""
    icon = {"accept": "✅", "stop": "🛑", "rerun": "🔄", "downgrade": "⬇️"}.get(decision, "❓")
    lines = [
        f"## Stage 4: Queen — Decision (Round {round_num})\n",
        f"### {icon} {decision.upper()}\n",
        f"**Reason:** {reason}",
    ]
    if decision == "rerun":
        lines.append("\n*→ Returning to Draft stage for another round...*")
    return "\n".join(lines)


def run_pipeline_stepwise(
    subject: str,
    tradition: str,
    provider: str,
    n_candidates: int,
    max_rounds: int,
):
    """Generator that yields UI updates by consuming orchestrator events."""
    task_id = f"gradio-{int(time.time())}"

    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if provider == "nb2" and not api_key:
        yield (
            "**ERROR:** GOOGLE_API_KEY environment variable not set.\n\n"
            "Start with: `GOOGLE_API_KEY=... python -m app.prototype.ui.gradio_demo`",
            _NO_IMAGES, "", "", ""
        )
        return

    d_cfg = DraftConfig(
        provider=provider, api_key=api_key,
        n_candidates=int(n_candidates), seed_base=42,
    )
    cr_cfg = CriticConfig()
    q_cfg = QueenConfig(max_rounds=int(max_rounds))

    orchestrator = PipelineOrchestrator(
        draft_config=d_cfg,
        critic_config=cr_cfg,
        queen_config=q_cfg,
        enable_hitl=False,
        enable_archivist=True,
    )

    pipeline_input = PipelineInput(
        task_id=task_id, subject=subject, cultural_tradition=tradition,
    )

    progress_lines: list[str] = [f"**Task:** `{task_id}`\n**Provider:** {provider}\n"]
    all_images: list[tuple[str, str]] = []
    scout_md = ""
    critic_md = ""
    queen_md = ""

    for event in orchestrator.run_stream(pipeline_input):
        et = event.event_type
        payload = event.payload
        stage = event.stage
        rn = event.round_num

        if et == EventType.STAGE_STARTED:
            label = stage.capitalize()
            round_suffix = f" (Round {rn})" if rn > 0 and stage != "scout" else ""
            progress_lines.append(f"---\n### {label}{round_suffix}\n*Processing...*")
            yield "\n".join(progress_lines), all_images, scout_md, critic_md, queen_md

        elif et == EventType.STAGE_COMPLETED:
            ms = payload.get("latency_ms", 0)
            label = stage.capitalize()
            round_suffix = f" (Round {rn})" if rn > 0 and stage != "scout" else ""

            if stage == "scout":
                evidence = payload.get("evidence", {})
                scout_md = _build_scout_md(evidence)
                has_taboo = len(evidence.get("taboo_violations", [])) > 0
                progress_lines[-1] = f"### Scout — **done** ({ms}ms)"
                if has_taboo:
                    progress_lines.append("\n⚠ **Taboo content detected!** Pipeline will likely reject.\n")

            elif stage == "draft":
                candidates = payload.get("candidates", [])
                round_images: list[tuple[str, str]] = []
                for c in candidates:
                    img_path = c.get("image_path", "")
                    if img_path and Path(img_path).exists() and Path(img_path).stat().st_size > 100:
                        cid = c.get("candidate_id", "").split("-")[-1]
                        round_images.append((img_path, f"R{rn} #{cid}"))
                all_images = round_images
                n_real = len(round_images)
                progress_lines[-1] = (
                    f"### Draft{round_suffix} — **done** ({ms}ms)\n"
                    f"Generated {len(candidates)} candidates"
                    f"{f', {n_real} with real images' if n_real else ' (mock placeholders)'}"
                )

            elif stage == "critic":
                critique = payload.get("critique", {})
                scored = critique.get("scored_candidates", [])
                best_id = critique.get("best_candidate_id")
                critic_md = _build_critic_md(scored, best_id)
                progress_lines[-1] = f"### Critic{round_suffix} — **done** ({ms}ms)"

            elif stage == "archivist":
                success = payload.get("success", False)
                path = payload.get("evidence_chain_path", "")
                if success:
                    progress_lines.append(f"- Archive: `{path}`")
                else:
                    error = payload.get("error", "unknown")
                    progress_lines.append(f"- Archive failed: {error}")

            yield "\n".join(progress_lines), all_images, scout_md, critic_md, queen_md

        elif et == EventType.DECISION_MADE:
            action = payload.get("action", "?")
            reason = payload.get("reason", "")
            ms = payload.get("latency_ms", 0)
            queen_md = _build_queen_md(action, reason, rn)
            progress_lines[-1] = (
                f"### Queen (Round {rn}) — "
                f"**{action.upper()}** ({ms}ms)"
            )
            yield "\n".join(progress_lines), all_images, scout_md, critic_md, queen_md

        elif et == EventType.PIPELINE_COMPLETED:
            final = payload.get("final_decision", "?")
            best = payload.get("best_candidate_id", "N/A")
            rounds = payload.get("total_rounds", 0)
            cost = payload.get("total_cost_usd", 0.0)
            icon = {"accept": "✅", "stop": "🛑", "downgrade": "⬇️"}.get(final, "❓")
            progress_lines.append(
                f"\n---\n## Result: {icon} **{final.upper()}**\n"
                f"- Best candidate: `{best}`\n"
                f"- Total rounds: {rounds}\n"
                f"- Cost: ${cost:.4f}\n"
            )
            yield "\n".join(progress_lines), all_images, scout_md, critic_md, queen_md

        elif et == EventType.PIPELINE_FAILED:
            error = payload.get("error", "unknown")
            progress_lines.append(f"\n---\n## ❌ FAILED\n`{error}`")
            yield "\n".join(progress_lines), all_images, scout_md, critic_md, queen_md


def launch() -> None:
    """Launch the Gradio interface."""
    try:
        import gradio as gr
    except ImportError:
        print("ERROR: gradio not installed. Install with: pip install gradio")
        sys.exit(1)

    with gr.Blocks(title="VULCA Prototype Pipeline") as demo:
        gr.Markdown(
            "# VULCA Prototype Pipeline\n"
            "Multi-round evaluation: **Scout → Draft → Critic → Queen**. "
            "Watch each stage execute step by step."
        )

        with gr.Row():
            subject_input = gr.Textbox(
                label="Subject",
                placeholder="e.g., Dong Yuan landscape with hemp-fiber texture strokes",
                lines=2, scale=3,
            )
            tradition_input = gr.Dropdown(
                label="Cultural Tradition",
                choices=TRADITIONS, value="chinese_xieyi", scale=1,
            )

        with gr.Row():
            provider_input = gr.Radio(
                label="Provider",
                choices=["mock", "nb2"], value="mock",
                info="mock = instant placeholders, nb2 = real NB2 images ($0.067/img)",
            )
            n_candidates_input = gr.Slider(
                label="Candidates per round",
                minimum=1, maximum=8, value=4, step=1,
            )
            max_rounds_input = gr.Slider(
                label="Max Rounds",
                minimum=1, maximum=5, value=2, step=1,
            )

        run_btn = gr.Button("▶  Run Pipeline", variant="primary", size="lg")

        progress_output = gr.Markdown(label="Pipeline Progress", value="*Click Run to start...*")

        with gr.Row():
            gallery_output = gr.Gallery(
                label="Draft Candidates", columns=4, height=300, object_fit="contain",
            )

        with gr.Row():
            with gr.Column():
                scout_output = gr.Markdown(label="Scout Evidence", value="")
            with gr.Column():
                critic_output = gr.Markdown(label="Critic Scoring", value="")

        queen_output = gr.Markdown(label="Queen Decision", value="")

        run_btn.click(
            fn=run_pipeline_stepwise,
            inputs=[subject_input, tradition_input, provider_input,
                    n_candidates_input, max_rounds_input],
            outputs=[progress_output, gallery_output, scout_output,
                     critic_output, queen_output],
        )

    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    launch()
