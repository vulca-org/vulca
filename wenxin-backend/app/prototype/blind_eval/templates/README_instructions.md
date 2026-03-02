# VULCA Blind Evaluation — Annotation Instructions

## Overview

You will evaluate AI-generated artworks (E1) and art critiques (E2) in a blinded study.
Each task shows two outputs labeled **A** and **B**. You do NOT know which system produced which.

## E1: Image Preference

For each task in `e1/annotation.csv`:

1. Open `e1/images/{task_id}/A.png` and `B.png` side by side
2. **preference**: Which image better represents the cultural subject? Enter `A`, `B`, or `TIE`
3. **cultural_fit_A** / **cultural_fit_B**: Rate each image's cultural appropriateness (1-5 Likert, see SCORING_RUBRIC.md)

## E2: Critique Text Quality

For each task in `e2/annotation.csv`:

1. Open `e2/critiques/{task_id}/A.md` and `B.md`
2. Rate each critique on three dimensions (1-5 Likert):
   - **evidence_chain**: Does the critique cite specific visual evidence?
   - **cross_cultural**: Does it demonstrate cross-cultural awareness?
   - **self_consistency**: Is the argument internally consistent?
3. **preference**: Which critique is better overall? Enter `A`, `B`, or `TIE`

## Important Notes

- Fill in your **rater_id** (e.g., `rater1`) on every row
- Use integer scores only (1, 2, 3, 4, 5)
- Leave `notes` blank unless you want to add a comment
- Do NOT look at filenames or metadata for clues about which system produced which output
- See `example/filled_example.csv` for a completed example row
