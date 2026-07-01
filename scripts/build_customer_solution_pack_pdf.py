#!/usr/bin/env python3
"""Build the public-example VULCA Solution Pack customer sample PDF."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence
from xml.sax.saxutils import escape

try:
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Paragraph
except ModuleNotFoundError as exc:
    bundled_python = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
    if exc.name == "reportlab" and bundled_python.exists() and Path(sys.executable) != bundled_python:
        os.execv(str(bundled_python), [str(bundled_python), *sys.argv])
    raise SystemExit("reportlab is required. Use a Python environment with reportlab installed.") from exc


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output/pdf/vulca-solution-pack-v1-customer-sample-public-examples.pdf"
ASSET_ROOT = ROOT / "assets/research/vulca-evidence-packs/2026-06-20"

CREATIFY_CARD = ASSET_ROOT / "creatify-deep-proof-v1/source-safe/creatify-source-safe-workflow-card-v1.png"
PROYA_CARD = ASSET_ROOT / "proya-deep-proof-v1/vision-banana/proya-source-safe-distilled-card-v1.png"
SEEDREAM_CARD = ASSET_ROOT / (
    "seedream-byteplus-deep-proof-v1/source-safe/"
    "seedream-byteplus-source-safe-distilled-card-v1.png"
)


PAGE_W, PAGE_H = landscape((11.25 * inch, 20 * inch))
CARD_R = 7

COLORS = {
    "bg": HexColor("#edf4f0"),
    "paper": HexColor("#fbfcfa"),
    "ink": HexColor("#16211d"),
    "muted": HexColor("#62716b"),
    "teal": HexColor("#007f73"),
    "teal_dark": HexColor("#00695f"),
    "green_bg": HexColor("#dff1ec"),
    "green_border": HexColor("#007f73"),
    "blue_bg": HexColor("#e4f4f8"),
    "blue_border": HexColor("#0d6f91"),
    "amber_bg": HexColor("#fff1d2"),
    "amber_border": HexColor("#9a6700"),
    "red_bg": HexColor("#f8e0dc"),
    "red_border": HexColor("#b63a31"),
    "panel": HexColor("#f7f6f1"),
    "line": HexColor("#c8d0cc"),
}


def style(size: int = 18, color: str = "ink", leading: int | None = None, bold: bool = False) -> ParagraphStyle:
    return ParagraphStyle(
        name=f"s-{size}-{color}-{bold}",
        fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size,
        leading=leading or int(size * 1.28),
        textColor=COLORS[color],
        spaceAfter=0,
    )


def para(c: canvas.Canvas, text: str, x: float, y: float, w: float, h: float, *, size: int = 18,
         color: str = "ink", bold: bool = False, leading: int | None = None) -> None:
    p = Paragraph(escape(text).replace("\n", "<br/>"), style(size, color, leading, bold))
    _aw, ah = p.wrap(w, h)
    p.drawOn(c, x, y + h - ah)


def shell(c: canvas.Canvas, title: str, page: int, *, kicker: str = "VULCA SOLUTION PACK V1") -> None:
    c.setFillColor(COLORS["bg"])
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(COLORS["paper"])
    c.roundRect(36, 30, PAGE_W - 72, PAGE_H - 60, CARD_R, stroke=0, fill=1)
    c.setFillColor(COLORS["teal"])
    c.rect(36, PAGE_H - 70, PAGE_W - 72, 10, stroke=0, fill=1)
    c.setFont("Helvetica", 16)
    c.setFillColor(COLORS["muted"])
    c.drawString(72, PAGE_H - 115, kicker)
    c.drawRightString(PAGE_W - 72, PAGE_H - 115, f"Public example sample / Page {page}")
    c.setFont("Helvetica", 40)
    c.setFillColor(COLORS["ink"])
    c.drawString(72, PAGE_H - 165, title)


def pill(c: canvas.Canvas, x: float, y: float, text: str, fill: str, stroke: str, width: float | None = None) -> None:
    w = width or max(92, len(text) * 7.8 + 24)
    c.setFillColor(COLORS[fill])
    c.setStrokeColor(COLORS[stroke])
    c.setLineWidth(1)
    c.roundRect(x, y, w, 24, 12, stroke=1, fill=1)
    c.setFillColor(COLORS[stroke])
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x + w / 2, y + 8, text)


def box(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    title: str,
    body: str,
    fill: str = "green_bg",
    stroke: str = "green_border",
    title_size: int = 17,
    body_size: int = 16,
) -> None:
    c.setFillColor(COLORS[fill])
    c.setStrokeColor(COLORS["line"])
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, CARD_R, stroke=1, fill=1)
    c.setFillColor(COLORS[stroke])
    c.rect(x, y + h - 10, w, 10, stroke=0, fill=1)
    para(c, title, x + 22, y + h - 58, w - 44, 36, size=title_size, color=stroke, bold=True)
    para(c, body, x + 22, y + 24, w - 44, h - 90, size=body_size, leading=int(body_size * 1.35))


def draw_image_fit(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float) -> None:
    c.drawImage(str(path), x, y, width=w, height=h, preserveAspectRatio=True, anchor="c", mask="auto")


def evidence_field(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, body: str,
                   *, fill: str, stroke: str) -> None:
    c.setFillColor(COLORS[fill])
    c.setStrokeColor(COLORS[stroke])
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, 6, stroke=1, fill=1)
    para(c, title, x + 16, y + h - 38, w - 32, 24, size=14, color=stroke, bold=True)
    para(c, body, x + 16, y + 12, w - 32, h - 48, size=12, color="ink", leading=15)


def source_anchor(c: canvas.Canvas, x: float, y: float, w: float, h: float, *, title: str, body: str,
                  proof: str) -> None:
    c.setFillColor(COLORS["green_bg"])
    c.setStrokeColor(COLORS["line"])
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, CARD_R, stroke=1, fill=1)
    c.setFillColor(COLORS["teal"])
    c.rect(x, y + h - 10, w, 10, stroke=0, fill=1)
    para(c, title, x + 22, y + h - 62, w - 44, 38, size=18, color="teal", bold=True)
    para(c, body, x + 22, y + h - 160, w - 44, 82, size=14, leading=20)
    c.setFillColor(COLORS["paper"])
    c.setStrokeColor(COLORS["teal"])
    c.roundRect(x + 22, y + 28, w - 44, 74, 6, stroke=1, fill=1)
    para(c, proof, x + 42, y + 42, w - 84, 48, size=13, color="teal", bold=True, leading=17)


def page_1(c: canvas.Canvas) -> None:
    shell(c, "VULCA Solution Pack v1", 1)
    para(
        c,
        "Release-evidence packets for AI-assisted visual assets.",
        72,
        PAGE_H - 225,
        980,
        34,
        size=17,
        color="teal",
    )
    para(
        c,
        "AI-assisted visual production is scaling across commerce, campaign, generated media, "
        "and ad workflows. The bottleneck is no longer only making an asset. The bottleneck is "
        "explaining what it came from, what it represents, what still needs review, and who owns "
        "the release decision.",
        72,
        PAGE_H - 345,
        760,
        110,
        size=17,
        leading=25,
    )
    pill(c, 72, 160, "public examples only", "green_bg", "teal_dark")
    pill(c, 205, 160, "source-backed", "green_bg", "teal_dark")
    pill(c, 330, 160, "human-reviewed", "amber_bg", "amber_border")
    para(
        c,
        "Named companies are workflow examples only. They do not imply a relationship, endorsement, "
        "authorization source, or finding.",
        72,
        104,
        1100,
        40,
        size=11,
        color="muted",
    )
    c.showPage()


def page_2(c: canvas.Canvas) -> None:
    shell(c, "What VULCA Produces", 2)
    para(
        c,
        "A compact packet that connects source context, visual or generated-output fields, "
        "review questions, owner route, and a bounded human review gate.",
        72,
        PAGE_H - 222,
        1150,
        46,
        size=16,
        color="muted",
    )
    lane_w = 360
    box(
        c,
        90,
        420,
        lane_w,
        190,
        title="Lane A / Product-truth",
        body=(
            "Existing commercial material and product claims become source-backed evidence cards: "
            "visible claim, product representation, source context, channel role, and release owner."
        ),
        fill="green_bg",
        stroke="teal_dark",
        body_size=14,
    )
    box(
        c,
        535,
        420,
        lane_w,
        190,
        title="Lane B / AI publishability",
        body=(
            "Generated assets are paired with input or reference context, model or workflow context, "
            "output state, label posture, unresolved fields, and owner route."
        ),
        fill="amber_bg",
        stroke="amber_border",
        body_size=14,
    )
    box(
        c,
        980,
        420,
        lane_w,
        190,
        title="Lane C / AI ad workflow",
        body=(
            "Product URL, listing, or brief-to-ad workflows become handoff packets: source input, "
            "generated candidate, review anatomy, export state, and campaign owner."
        ),
        fill="red_bg",
        stroke="red_border",
        body_size=14,
    )
    para(
        c,
        "Default reading order for this sample: Lane C is the main before/after workflow story. "
        "Lane A and Lane B show that the same source-backed method also works for product claims "
        "and generated assets.",
        90,
        285,
        1180,
        80,
        size=16,
        leading=24,
    )
    c.showPage()


def page_3(c: canvas.Canvas) -> None:
    shell(c, "Before / After: AI Ad Workflow Handoff", 3)
    box(
        c,
        75,
        410,
        455,
        215,
        title="Before VULCA",
        body=(
            "A product URL, listing, image, or brief can quickly become multiple campaign candidates. "
            "Source input, review anatomy, export state, missing fields, and release owner often sit "
            "in different places."
        ),
        fill="red_bg",
        stroke="red_border",
        title_size=22,
        body_size=17,
    )
    box(
        c,
        75,
        145,
        455,
        220,
        title="After VULCA",
        body=(
            "The same flow becomes a release-evidence packet: source input -> generated candidate -> "
            "hook/body/CTA review -> export state -> missing-field list -> owner route -> human "
            "review gate."
        ),
        fill="green_bg",
        stroke="teal",
        title_size=22,
        body_size=17,
    )
    draw_image_fit(c, CREATIFY_CARD, 650, 185, 650, 448)
    para(
        c,
        "Public workflow example. This page uses a source-safe evidence card, not vendor proof or "
        "performance prediction.",
        560,
        92,
        820,
        30,
        size=11,
        color="muted",
    )
    c.showPage()


def page_4(c: canvas.Canvas) -> None:
    shell(c, "Supporting Proof A: Product-Truth Evidence", 4)
    para(
        c,
        "A public product or campaign surface can be translated into reviewable fields before reuse.",
        72,
        PAGE_H - 218,
        850,
        38,
        size=16,
        color="muted",
    )
    c.setFillColor(COLORS["panel"])
    c.roundRect(72, 80, 840, 480, 8, stroke=0, fill=1)
    para(c, "Readable evidence-card view", 96, 518, 520, 32, size=18, color="ink", bold=True)
    evidence_field(
        c,
        96,
        396,
        244,
        98,
        "1. Public source surface",
        "Public commercial material, product representation, offer cue, and channel context are preserved.",
        fill="blue_bg",
        stroke="blue_border",
    )
    evidence_field(
        c,
        368,
        396,
        244,
        98,
        "2. VULCA field read",
        "Claim text, representation surface, reuse context, and owner route are separated into explicit fields.",
        fill="green_bg",
        stroke="green_border",
    )
    evidence_field(
        c,
        640,
        396,
        244,
        98,
        "3. Review output",
        "A product-truth packet shows what is known, what is missing, and who should decide release.",
        fill="amber_bg",
        stroke="amber_border",
    )
    evidence_field(
        c,
        96,
        270,
        244,
        98,
        "Source context",
        "The example name can remain visible only as a public example label.",
        fill="blue_bg",
        stroke="blue_border",
    )
    evidence_field(
        c,
        368,
        270,
        244,
        98,
        "Representation check",
        "The packet asks whether the visual surface and product claim are connected enough for reuse.",
        fill="green_bg",
        stroke="green_border",
    )
    evidence_field(
        c,
        640,
        270,
        244,
        98,
        "Owner route",
        "The output routes unresolved questions to a human owner instead of implying automatic approval.",
        fill="amber_bg",
        stroke="amber_border",
    )
    box(
        c,
        96,
        112,
        376,
        120,
        title="What this proves",
        body=(
            "VULCA can make a public commercial surface inspectable as source, representation, "
            "review question, and owner route."
        ),
        fill="green_bg",
        stroke="teal",
        title_size=16,
        body_size=13,
    )
    box(
        c,
        508,
        112,
        376,
        120,
        title="Boundary",
        body=(
            "This is a public example for workflow discussion. It does not make a legal, rights, "
            "platform, release-readiness, or relationship claim."
        ),
        fill="amber_bg",
        stroke="amber_border",
        title_size=16,
        body_size=13,
    )
    source_anchor(
        c,
        970,
        212,
        320,
        260,
        title="Source-safe anchor",
        body=(
            "The public example name can be visible, but the customer view shows only structured "
            "fields and review boundaries."
        ),
        proof="Customer-visible use: check whether these fields match the team's review workflow.",
    )
    c.showPage()


def page_5(c: canvas.Canvas) -> None:
    shell(c, "Supporting Proof B: AI Publishability Context", 5)
    para(
        c,
        "Generated media should not be reviewed as a file alone. The review packet needs source or "
        "reference context, model or workflow context, output state, label posture, and owner route.",
        72,
        PAGE_H - 235,
        1080,
        60,
        size=16,
        color="muted",
    )
    c.setFillColor(COLORS["panel"])
    c.roundRect(72, 80, 840, 480, 8, stroke=0, fill=1)
    para(c, "Readable evidence-card view", 96, 518, 520, 32, size=18, color="ink", bold=True)
    evidence_field(
        c,
        96,
        396,
        244,
        98,
        "1. Public records",
        "Official model or tool pages and tutorial context become source records.",
        fill="blue_bg",
        stroke="blue_border",
    )
    evidence_field(
        c,
        368,
        396,
        244,
        98,
        "2. Normalized fields",
        "Model context, input reference, output state, label posture, and reuse owner are split out.",
        fill="green_bg",
        stroke="green_border",
    )
    evidence_field(
        c,
        640,
        396,
        244,
        98,
        "3. Review packet",
        "The output states what is reviewable, missing, source-backed, and not yet approved.",
        fill="amber_bg",
        stroke="amber_border",
    )
    evidence_field(
        c,
        96,
        270,
        244,
        98,
        "Prompt/reference posture",
        "The packet keeps source and generated-output context together for review.",
        fill="blue_bg",
        stroke="blue_border",
    )
    evidence_field(
        c,
        368,
        270,
        244,
        98,
        "Label posture",
        "AI-assisted status and reuse limitations are made explicit before publication.",
        fill="green_bg",
        stroke="green_border",
    )
    evidence_field(
        c,
        640,
        270,
        244,
        98,
        "Missing fields",
        "The packet lists unresolved fields for a qualified human decision maker.",
        fill="amber_bg",
        stroke="amber_border",
    )
    box(
        c,
        96,
        92,
        376,
        132,
        title="What this proves",
        body=(
            "VULCA can structure public AI-model or tool context into a publishability packet for "
            "human review."
        ),
        fill="green_bg",
        stroke="teal",
        title_size=16,
        body_size=13,
    )
    box(
        c,
        508,
        92,
        376,
        132,
        title="Boundary",
        body=(
            "This is not model quality scoring, model-safety certification, copyright clearance, "
            "policy approval, or benchmark comparison."
        ),
        fill="amber_bg",
        stroke="amber_border",
        title_size=16,
        body_size=13,
    )
    source_anchor(
        c,
        970,
        212,
        320,
        260,
        title="Source-safe anchor",
        body=(
            "The customer view does not expose untreated screenshots or dense production notes. "
            "It keeps the review fields readable."
        ),
        proof="Customer-visible use: check whether these fields match AI publishability review.",
    )
    c.showPage()


def page_6(c: canvas.Canvas) -> None:
    shell(c, "A Bounded Pilot Shape", 6)
    para(
        c,
        "The first useful step is small: public examples or sanitized assets, one review lane, "
        "a short readout, and a clear owner route.",
        72,
        PAGE_H - 225,
        1120,
        44,
        size=16,
        color="muted",
    )
    steps = [
        ("1. Intake", "Public example, sanitized asset, product URL, listing, brief, or generated candidate."),
        ("2. Field Read", "Source context, visible claim or output context, review anatomy, output state, and missing fields."),
        ("3. Evidence Card", "A compact review object that a human owner can inspect and route."),
        ("4. Readout", "What is ready to discuss, what is missing, who owns the next decision, and what should wait."),
    ]
    positions = [(90, 470), (735, 470), (90, 265), (735, 265)]
    fills = ["green_bg", "green_bg", "amber_bg", "amber_bg"]
    strokes = ["teal", "teal", "amber_border", "amber_border"]
    for (title, body), (x, y), fill, stroke in zip(steps, positions, fills, strokes, strict=True):
        box(c, x, y, 555, 130, title=title, body=body, fill=fill, stroke=stroke, title_size=16, body_size=14)
    para(
        c,
        "Pilot output is not final approval. It is a source-backed packet for a qualified human decision maker.",
        90,
        145,
        1150,
        42,
        size=16,
        color="ink",
    )
    c.showPage()


def page_7(c: canvas.Canvas) -> None:
    shell(c, "Review Ask", 7)
    para(
        c,
        "We would value practical feedback on whether this release-evidence workflow maps to a real "
        "bottleneck in ecommerce, campaign, or AI creative workflows.",
        72,
        520,
        1180,
        108,
        size=23,
        leading=33,
    )
    box(
        c,
        72,
        360,
        600,
        135,
        title="Useful feedback",
        body=(
            "Which fields are useful? Which fields are missing? Where would source context, label posture, "
            "output state, and owner routing fit in your current review process?"
        ),
        fill="green_bg",
        stroke="teal",
        title_size=20,
        body_size=15,
    )
    box(
        c,
        740,
        360,
        600,
        135,
        title="What this sample is not",
        body=(
            "It is not legal advice, a compliance certification, platform approval, model-safety "
            "certification, campaign-performance measurement, or automatic release approval."
        ),
        fill="red_bg",
        stroke="red_border",
        title_size=20,
        body_size=15,
    )
    box(
        c,
        72,
        150,
        600,
        135,
        title="Possible next step",
        body=(
            "If relevant, discuss a bounded pilot using public examples or sanitized assets: one lane, "
            "a small set of visual materials, and a short readout."
        ),
        fill="amber_bg",
        stroke="amber_border",
        title_size=20,
        body_size=15,
    )
    box(
        c,
        740,
        150,
        600,
        135,
        title="Boundary",
        body=(
            "Named companies are public examples for workflow discussion only. Human owners make release "
            "decisions."
        ),
        fill="green_bg",
        stroke="teal",
        title_size=20,
        body_size=15,
    )
    para(
        c,
        "Prepared as a public-example sample. No private assets are required for an initial review.",
        72,
        78,
        1180,
        30,
        size=14,
        color="muted",
    )
    c.showPage()


def build(output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    missing = [path for path in (CREATIFY_CARD, PROYA_CARD, SEEDREAM_CARD) if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing source-safe cards: " + ", ".join(str(path) for path in missing))

    c = canvas.Canvas(str(output), pagesize=(PAGE_W, PAGE_H))
    c.setTitle("VULCA Solution Pack v1 - Public Example Sample")
    c.setAuthor("VULCA")
    c.setSubject("Source-backed evidence packets for AI-assisted visual assets")

    for page in (page_1, page_2, page_3, page_4, page_5, page_6, page_7):
        page(c)
    c.save()
    return output


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--approval-recorded",
        action="store_true",
        help="Confirm that explicit main-review approval exists for generating this customer sample.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT,
        help="PDF output path. Defaults to the canonical customer sample PDF.",
    )
    args = parser.parse_args(argv)
    if not args.approval_recorded:
        parser.error("explicit user approval is required; rerun with --approval-recorded after approval")
    print(build(args.output.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
