#!/usr/bin/env python3
"""Generate qualitative comparison figure: 6 conditions × 3 tasks.

Shows progression across 4 experimental phases:
  v1 (SD1.5): A — baseline
  v1 (FLUX):  C — FLUX baseline, D — full v1 pipeline
  v3 (VLM):   H — best FLUX + VLM scoring
  v4 (NB2):   G — NB2 baseline, G++ — NB2 multi-round (peak 0.917)
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

CHECKPOINT_ROOT = Path("/mnt/i/website/wenxin-backend/app/prototype/checkpoints/draft")
ABLATION_DATA = Path("/mnt/i/website/wenxin-backend/app/prototype/blind_eval/results/ablation/unified_ablation_results.json")
OUTPUT = Path(__file__).resolve().parent / "qualitative.pdf"

# 3 representative tasks
TASK_IDS = ["bench-020", "bench-017", "vulca-bench-0020"]
TASK_LABELS = ["Taboo (bench-020)", "Poetic (bench-017)", "Cultural (vb-0020)"]

# 6 key conditions across 4 phases
CONDITIONS = [
    {"cond": "A",   "label": "(A) SD1.5 Baseline",          "phase": "v1\n(SD1.5)", "phase_idx": 0},
    {"cond": "C",   "label": "(C) FLUX Baseline",           "phase": "v1\n(FLUX)",  "phase_idx": 1},
    {"cond": "D",   "label": "(D) FLUX + Rule/LLM + Loop",  "phase": "",            "phase_idx": 1},
    {"cond": "H",   "label": "(H) FLUX + VLM Scoring",      "phase": "v3\n(VLM)",   "phase_idx": 2},
    {"cond": "G",   "label": "(G) NB2 + VLM",               "phase": "v4\n(NB2)",   "phase_idx": 3},
    {"cond": "Gpp", "label": "(G++) NB2 + VLM + Loop",      "phase": "",            "phase_idx": 3},
]

# Layout constants
CELL_W, CELL_H = 360, 360
PAD = 12
LABEL_H = 48          # below-image score label area
PHASE_LABEL_W = 60    # left margin for phase labels
ROW_LABEL_W = 210     # condition label width
HEADER_H = 44
COL_GAP = PAD
ROW_GAP = PAD

N_ROWS = len(CONDITIONS)
N_COLS = len(TASK_IDS)

TOTAL_W = PHASE_LABEL_W + ROW_LABEL_W + N_COLS * CELL_W + (N_COLS - 1) * COL_GAP + PAD * 2
TOTAL_H = HEADER_H + N_ROWS * (CELL_H + LABEL_H) + (N_ROWS - 1) * ROW_GAP + PAD * 2

# Phase colors
PHASE_COLORS = {
    0: (100, 100, 100),  # v1 SD1.5 — gray
    1: (16, 185, 129),   # v1 FLUX — green
    2: (245, 158, 11),   # v3 VLM — amber
    3: (139, 92, 246),   # v4 NB2 — purple
}


def get_font(size, bold=True):
    names = (
        ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"] if bold
        else ["DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    for prefix in ["/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/truetype/liberation/"]:
        for name in names:
            try:
                return ImageFont.truetype(prefix + name, size)
            except OSError:
                pass
    return ImageFont.load_default()


def load_scores():
    """Load scores from unified ablation results."""
    with open(ABLATION_DATA) as f:
        data = json.load(f)
    scores = {}
    for entry in data:
        key = (entry["condition"], entry["task_id"])
        scores[key] = {
            "score": entry["score"],
            "l5": entry["dim_scores"].get("L5", 0) if entry.get("dim_scores") else 0,
            "rounds": entry.get("rounds", 1),
        }
    return scores


def load_image(task_id, condition):
    """Load candidate image for a given task/condition."""
    base = CHECKPOINT_ROOT / f"abl-{condition}_{task_id}"
    for ext in [".jpg", ".png"]:
        p = base / f"draft-abl-{condition}_{task_id}-0{ext}"
        if p.exists():
            return Image.open(p).convert("RGB").resize((CELL_W, CELL_H), Image.LANCZOS)
    # Fallback: try any image in the directory
    if base.exists():
        for f in sorted(base.iterdir()):
            if f.suffix.lower() in (".jpg", ".jpeg", ".png"):
                return Image.open(f).convert("RGB").resize((CELL_W, CELL_H), Image.LANCZOS)
    print(f"MISSING: {base}", file=sys.stderr)
    img = Image.new("RGB", (CELL_W, CELL_H), (220, 220, 220))
    d = ImageDraw.Draw(img)
    d.text((CELL_W // 2, CELL_H // 2), "N/A", anchor="mm", fill=(150, 150, 150), font=get_font(24))
    return img


def main():
    scores = load_scores()

    # Baseline condition for delta computation
    baseline_cond = "C"

    canvas = Image.new("RGB", (TOTAL_W, TOTAL_H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    font_header = get_font(20)
    font_cond = get_font(15)
    font_score = get_font(12, bold=False)
    font_delta = get_font(11, bold=True)
    font_phase = get_font(14)

    x_start = PHASE_LABEL_W + ROW_LABEL_W + PAD

    # Column headers
    for j, label in enumerate(TASK_LABELS):
        cx = x_start + j * (CELL_W + COL_GAP) + CELL_W // 2
        draw.text((cx, HEADER_H // 2 + 2), label, anchor="mm", fill=(30, 30, 30), font=font_header)

    # Draw rows
    prev_phase_idx = -1
    for i, cinfo in enumerate(CONDITIONS):
        cond = cinfo["cond"]
        y_top = HEADER_H + PAD + i * (CELL_H + LABEL_H + ROW_GAP)
        row_mid_y = y_top + (CELL_H + LABEL_H) // 2

        # Phase label (only on first row of each phase)
        if cinfo["phase"] and cinfo["phase_idx"] != prev_phase_idx:
            color = PHASE_COLORS[cinfo["phase_idx"]]

            # Calculate phase span (how many rows in this phase)
            phase_rows = sum(1 for c in CONDITIONS if c["phase_idx"] == cinfo["phase_idx"])
            phase_height = phase_rows * (CELL_H + LABEL_H) + (phase_rows - 1) * ROW_GAP
            phase_mid_y = y_top + phase_height // 2

            # Draw phase bracket
            bx = PHASE_LABEL_W - 10
            draw.line([(bx, y_top), (bx, y_top + phase_height)], fill=color, width=2)
            draw.line([(bx, y_top), (bx + 6, y_top)], fill=color, width=2)
            draw.line([(bx, y_top + phase_height), (bx + 6, y_top + phase_height)], fill=color, width=2)

            # Phase text
            for li, line in enumerate(cinfo["phase"].split("\n")):
                draw.text(
                    (PHASE_LABEL_W // 2, phase_mid_y - 10 + li * 18),
                    line, anchor="mm", fill=color, font=font_phase,
                )
            prev_phase_idx = cinfo["phase_idx"]

        # Row label (condition description)
        draw.text(
            (PHASE_LABEL_W + 8, row_mid_y),
            cinfo["label"], anchor="lm",
            fill=PHASE_COLORS[cinfo["phase_idx"]], font=font_cond,
        )

        # Images + scores
        for j, task_id in enumerate(TASK_IDS):
            x = x_start + j * (CELL_W + COL_GAP)
            img = load_image(task_id, cond)
            canvas.paste(img, (x, y_top))

            # Border
            border_color = PHASE_COLORS[cinfo["phase_idx"]]
            draw.rectangle(
                [x - 1, y_top - 1, x + CELL_W, y_top + CELL_H],
                outline=(*border_color, 128), width=1,
            )

            # Score label
            s = scores.get((cond, task_id))
            if s:
                score_text = f"Score: {s['score']:.3f}  |  L5: {s['l5']:.3f}"
                if s["rounds"] > 1:
                    score_text += f"  ({s['rounds']}R)"
                draw.text(
                    (x + CELL_W // 2, y_top + CELL_H + 4),
                    score_text, anchor="mt", fill=(50, 50, 50), font=font_score,
                )

                # Delta vs C baseline
                baseline = scores.get((baseline_cond, task_id))
                if baseline and cond != baseline_cond:
                    ds = s["score"] - baseline["score"]
                    dl5 = s["l5"] - baseline["l5"]
                    sign_s = "+" if ds >= 0 else ""
                    sign_l5 = "+" if dl5 >= 0 else ""
                    delta_text = f"\u0394: {sign_s}{ds:.3f} / L5 {sign_l5}{dl5:.3f}"
                    delta_color = (0, 128, 0) if ds >= 0 else (200, 0, 0)
                    draw.text(
                        (x + CELL_W // 2, y_top + CELL_H + 22),
                        delta_text, anchor="mt", fill=delta_color, font=font_delta,
                    )

    # Horizontal separator lines between phases
    drawn_phases = set()
    for i, cinfo in enumerate(CONDITIONS):
        if cinfo["phase_idx"] not in drawn_phases and i > 0:
            prev_phase = CONDITIONS[i - 1]["phase_idx"]
            if cinfo["phase_idx"] != prev_phase:
                y_sep = HEADER_H + PAD + i * (CELL_H + LABEL_H + ROW_GAP) - ROW_GAP // 2
                draw.line(
                    [(PHASE_LABEL_W, y_sep), (TOTAL_W - PAD, y_sep)],
                    fill=(200, 200, 200), width=1,
                )
        drawn_phases.add(cinfo["phase_idx"])

    canvas.save(str(OUTPUT), "PDF", resolution=150)
    print(f"Saved: {OUTPUT} ({TOTAL_W}x{TOTAL_H})")


if __name__ == "__main__":
    main()
