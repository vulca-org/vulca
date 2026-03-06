"""VULCA HuggingFace Space — Gradio app for zero-install evaluation.

Launch locally:
    cd wenxin-backend
    python -m app.prototype.integrations.hf_space

Deploy to HF:
    Copy this file as app.py to a HuggingFace Space repo.
    Set env vars: VULCA_API_URL, VULCA_API_KEY
"""

from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path

VULCA_API_URL = os.environ.get("VULCA_API_URL", "http://localhost:8001")
VULCA_API_KEY = os.environ.get("VULCA_API_KEY", "")

# Tradition options for dropdown
TRADITIONS = [
    ("Auto-detect", "auto"),
    ("Chinese Freehand Ink (Xieyi)", "chinese_xieyi"),
    ("Chinese Meticulous (Gongbi)", "chinese_gongbi"),
    ("Western Academic", "western_academic"),
    ("Islamic Geometric", "islamic_geometric"),
    ("Japanese Traditional", "japanese_traditional"),
    ("Watercolor", "watercolor"),
    ("African Traditional", "african_traditional"),
    ("South Asian", "south_asian"),
    ("General / Cross-cultural", "default"),
]

# L-level display names
L_LABELS = {
    "L1": "L1 Visual Perception",
    "L2": "L2 Technical Analysis",
    "L3": "L3 Cultural Context",
    "L4": "L4 Critical Interpretation",
    "L5": "L5 Philosophical Aesthetic",
}


def _image_to_base64(image) -> str:
    """Convert PIL Image to base64 string."""
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _call_evaluate_api(image_b64: str, tradition: str) -> dict:
    """Call the VULCA evaluate API."""
    import httpx

    headers = {"Content-Type": "application/json"}
    if VULCA_API_KEY:
        headers["Authorization"] = f"Bearer {VULCA_API_KEY}"

    body = {"image_base64": image_b64}
    if tradition and tradition != "auto":
        body["tradition"] = tradition

    try:
        with httpx.Client(timeout=90) as client:
            resp = client.post(
                f"{VULCA_API_URL}/api/v1/evaluate",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"API error {e.response.status_code}: {e.response.text[:200]}"}
    except Exception as e:
        return {"error": f"Connection error: {e}"}


def _call_identify_api(image_b64: str) -> dict:
    """Call the VULCA identify-tradition API."""
    import httpx

    headers = {"Content-Type": "application/json"}
    if VULCA_API_KEY:
        headers["Authorization"] = f"Bearer {VULCA_API_KEY}"

    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{VULCA_API_URL}/api/v1/identify-tradition",
                json={"image_base64": image_b64},
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {"error": str(e)}


def _format_report(result: dict) -> str:
    """Format evaluation result as markdown."""
    if "error" in result:
        return f"**Error:** {result['error']}"

    scores = result.get("scores", {})
    total = result.get("weighted_total", 0)
    tradition = result.get("tradition_used", "unknown")
    diagnosis = result.get("cultural_diagnosis", "")
    recommendations = result.get("recommendations", [])
    risks = result.get("risk_flags", [])
    latency = result.get("latency_ms", 0)

    lines = [
        f"## Cultural Evaluation Report",
        f"",
        f"**Tradition:** {tradition} | **Score:** {total:.3f} | **Latency:** {latency}ms",
        f"",
        f"### L1-L5 Scores",
        f"| Dimension | Score |",
        f"|-----------|-------|",
    ]

    for key in ["L1", "L2", "L3", "L4", "L5"]:
        dim_key = key  # API returns L1-L5 keys
        score = scores.get(dim_key, 0)
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        lines.append(f"| {L_LABELS.get(key, key)} | {score:.3f} {bar} |")

    if diagnosis:
        lines += ["", f"### Cultural Diagnosis", f"{diagnosis}"]

    if recommendations:
        lines += ["", f"### Recommendations"]
        for r in recommendations:
            lines.append(f"- {r}")

    if risks:
        lines += ["", f"### Risk Flags"]
        for r in risks:
            lines.append(f"- ⚠️ {r}")

    lines += [
        "",
        "---",
        "*Powered by [VULCA](https://vulcaart.art) — Cultural AI Art Evaluation Framework*",
    ]
    return "\n".join(lines)


def _make_radar_chart(scores: dict):
    """Create a radar chart from L1-L5 scores."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    labels = list(L_LABELS.values())
    values = [scores.get(f"L{i+1}", 0) for i in range(5)]
    values.append(values[0])  # close the polygon

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles.append(angles[0])

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, values, "o-", linewidth=2, color="#007AFF")
    ax.fill(angles, values, alpha=0.2, color="#007AFF")
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=8)
    ax.set_ylim(0, 1)
    ax.set_rticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=7)
    ax.set_title("L1-L5 Cultural Scores", pad=20, fontsize=12, fontweight="bold")
    plt.tight_layout()
    return fig


def evaluate(image, tradition_choice: str) -> tuple:
    """Main evaluation function for Gradio interface."""
    if image is None:
        return None, "**Please upload an image.**"

    image_b64 = _image_to_base64(image)

    # Map dropdown value
    tradition = tradition_choice
    for label, val in TRADITIONS:
        if label == tradition_choice:
            tradition = val
            break

    result = _call_evaluate_api(image_b64, tradition)

    # Build outputs
    report = _format_report(result)

    scores = result.get("scores", {})
    radar = _make_radar_chart(scores) if scores else None

    return radar, report


def identify(image) -> str:
    """Identify the cultural tradition of an image."""
    if image is None:
        return "**Please upload an image.**"

    image_b64 = _image_to_base64(image)
    result = _call_identify_api(image_b64)

    if "error" in result:
        return f"**Error:** {result['error']}"

    tradition = result.get("tradition", "unknown")
    confidence = result.get("confidence", 0)
    alternatives = result.get("alternatives", [])
    weights = result.get("recommended_weights", {})

    lines = [
        f"## Tradition Identification",
        f"",
        f"**Detected:** {tradition} (confidence: {confidence:.0%})",
        f"",
    ]

    if alternatives:
        lines += ["### Alternatives"]
        for alt in alternatives[:3]:
            lines.append(f"- {alt.get('tradition', '?')}: {alt.get('confidence', 0):.0%}")

    if weights:
        lines += ["", "### Recommended Weights"]
        for k, v in sorted(weights.items()):
            lines.append(f"- {k}: {v:.2f}")

    return "\n".join(lines)


def build_app():
    """Build and return the Gradio app."""
    try:
        import gradio as gr
    except ImportError:
        raise ImportError("Install gradio: pip install gradio")

    tradition_labels = [label for label, _ in TRADITIONS]

    with gr.Blocks(
        title="VULCA Cultural Art Evaluator",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown(
            """
            # 🎨 VULCA — Cultural Art Evaluator
            Upload an image to evaluate its cultural authenticity across 5 dimensions (L1-L5).

            **[Full Platform](https://vulcaart.art)** | **[GitHub](https://github.com/yha9806/website)** | **[Paper (EMNLP 2025)](https://arxiv.org/abs/2601.07986)**
            """
        )

        with gr.Tabs():
            with gr.TabItem("Evaluate"):
                with gr.Row():
                    with gr.Column(scale=1):
                        eval_image = gr.Image(type="pil", label="Upload Image")
                        eval_tradition = gr.Dropdown(
                            choices=tradition_labels,
                            value="Auto-detect",
                            label="Cultural Tradition",
                        )
                        eval_btn = gr.Button("Evaluate", variant="primary")

                    with gr.Column(scale=1):
                        eval_radar = gr.Plot(label="L1-L5 Radar Chart")
                        eval_report = gr.Markdown(label="Evaluation Report")

                eval_btn.click(
                    fn=evaluate,
                    inputs=[eval_image, eval_tradition],
                    outputs=[eval_radar, eval_report],
                )

            with gr.TabItem("Identify Tradition"):
                with gr.Row():
                    with gr.Column(scale=1):
                        id_image = gr.Image(type="pil", label="Upload Image")
                        id_btn = gr.Button("Identify", variant="primary")

                    with gr.Column(scale=1):
                        id_result = gr.Markdown(label="Identification Result")

                id_btn.click(
                    fn=identify,
                    inputs=[id_image],
                    outputs=[id_result],
                )

        gr.Markdown(
            """
            ---
            *VULCA: Visual Understanding and Linguistic Cultural Assessment*
            *L1-L5 evaluation framework published at EMNLP 2025 Findings*
            """
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860)
