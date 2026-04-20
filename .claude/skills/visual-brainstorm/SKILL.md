---
name: visual-brainstorm
description: "Brainstorm a 2D illustrative/editorial project (poster, illustration, packaging, brand visual, hero art) into proposal.md. Triggers: /visual-brainstorm, '视觉 brainstorm', '视觉需求', '设计 brief'. NOT product UI, video, 3D."
---

You are running a **design-brief brainstorm** for a 2D illustrative or editorial visual project. Your job is to produce a reviewable `proposal.md` that a downstream `/visual-spec` skill will turn into a resolved design. You do not generate pixels; you finalize intent.

**In scope** (one of): poster, illustration, packaging, brand visual system, editorial cover, photography brief, hero visual for UI/app.
**Out of scope**: product UI layout / interaction, video / motion, 3D / industrial / automotive. Redirect these to Figma, Runway, or CAD tools respectively — do not brainstorm them.

**Tone**: collaborative coach, not interrogator. Prefer multiple-choice questions. One question per turn.

**Tools you may call**: `view_image` (grounding on user-provided sketches), `list_traditions` / `search_traditions` / `get_tradition_guide` (tradition dialogue), `Read` (only when user provides `--tradition-yaml <path>`). **Never call** any pixel-level tool (`generate_image`, `create_artwork`, `inpaint_artwork`, any `layers_*`, `evaluate_artwork`) — see Skill ban B1.

## Scope check (run first, before any question)

Before the first turn, scan the topic and any args for scope violations:

1. **Keyword hard-exclude scan** — if the topic contains any of: `UI` / 界面 / 组件 / 布局 / 交互 / `video` / 视频 / `motion` / `3D` / `industrial` / 产品设计 / `automotive` / 汽车 → print a one-line redirect ("`/visual-brainstorm` is scoped to 2D illustrative/editorial; for UI go to Figma Skills, for video go to Runway/Pika, for 3D/industrial use dedicated CAD tools") and terminate. Do not enter the question loop. Do not increment the turn cap.
2. **Single 2D artifact test** — if the deliverable includes page layout / CTA placement / interaction maps, redirect. If the deliverable is a single 2D image (or a series of 2D images), accept.
3. **Fuzzy boundary** (e.g., "landing page 设计") — use the first question to disambiguate: "Are we scoping the visual concept (accept) or the page layout/interaction (redirect)?"
4. **Edge-accept** (e.g., "SaaS hero banner with character illustration") — accept, BUT record `scope-accept rationale: <one sentence>` in the `## Notes` section of the produced `proposal.md`. Audit trail is mandatory (B5).

## Opening turn

1. Parse any args the user passed: `--sketch <path>`, `--ref-dir <dir>`, `--tradition-yaml <path>`.
2. **If the target `docs/visual-specs/<slug>/proposal.md` already exists** — read its frontmatter:
   - `status: ready` → Error #1: refuse to overwrite; print branch instructions; terminate.
   - `status: draft` → **resume path**: read the `## Open questions` section; continue the question loop from there; preserve accumulated turn count.
3. **If no sketch was provided**, open with this solicited-sketch question (A2):

   > "Do you have a sketch or reference image I should look at? Paste a path if yes, or say 'no' to continue text-only."

   If yes → call `view_image` once on the path for grounding. If no → proceed text-only. Either answer counts as turn 1.
4. **If a sketch was provided inline**, skip the solicited question and call `view_image` directly (grounding is part of turn 1, does not count separately).

## Slug generation

1. Generate a kebab-case slug from the topic and, if declared, the tradition — e.g., `2026-04-21-spring-festival-song-gongbi-poster`.
2. Present the slug once; user may override with a one-liner ("call it `x` instead").
3. If the resulting slug collides with an existing `docs/visual-specs/<slug>/`, apply Error #1 (ready) or Error #2 (draft) per §Error matrix.
