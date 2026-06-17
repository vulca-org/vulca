# PPT Parallel Usecase Pilots

Status: source-pack-handoff-ready-render-blocked

This package defines three parallel PPT pilots and the supporting handoff
materials needed for another contributor to continue the work directly.

The Markdown briefs, claim spines, visual briefs, generation prompts, QA
prompts, and generator harness are usable. The generated PPTX drafts remain
public-blocked and should not be treated as presentation candidates without a
new visual pass.

## Quick Start

Read this package in this order:

1. `deck-briefs.md` for the three deck concepts.
2. Each deck directory for source boundaries, claims, visual direction, and
   prompts.
3. `prompts/superpowers-parallel-deck-prompts.md` for parallel execution.
4. `prompts/gemini-agent-prompt-pack.md` for critique and review prompts.
5. `output-templates.md` for the required Markdown output shape.

Run the current generator harness locally with:

```bash
node --check scripts/generate_ppt_parallel_usecase_pilot_decks.mjs
node scripts/generate_ppt_parallel_usecase_pilot_decks.mjs --dry-run
node scripts/generate_ppt_parallel_usecase_pilot_decks.mjs
```

The generator writes local artifacts under:

```text
outputs/<THREAD_ID>/presentations/ppt-parallel-usecase-pilots/
```

Those local artifacts include PPTX files, slide previews, contact sheets, QA
notes, and an HTML viewer. They are generated outputs, not checked-in product
deliverables.

## Current Quality State

The content pack is useful as a source-grounded starting point. The current
PPTX rendering approach is not good enough:

- the three decks share too much of the same visual shell;
- proof objects read as schematic placeholders instead of persuasive business
  or product evidence;
- the scorecard is structural and should not be read as a human visual
  approval.

Recommended next step: keep this package as the source pack, then replace the
renderer with one usecase-specific deck pass. Deck C is the best candidate if
the goal is to demonstrate Vulca's workflow; Deck A is the best candidate if
the goal is a commercial AI-product case.

## Why This Exists

Run 2.92 improved text-to-object binding, but the slide story still feels
strange because the text and visuals describe internal renderer mechanics. The
next test should start from real usecases and audience-facing product stories.

## Decks

- **Deck A:** Brand-Safe AI Creative Production.
- **Deck B:** Vulca Product Strategy.
- **Deck C:** Vulca Workflow Demo.

Each deck contains the same six Markdown outputs before any PPT generation:

- `research_brief.md`
- `deck_brief.md`
- `claim_spine.md`
- `visual_brief.md`
- `generation_prompt.md`
- `qa_prompt.md`

## Shared Rules

- Use primary sources first.
- Store derived observations, not copied layouts, screenshots, brand marks, or
  long source prose.
- Keep internal trace language out of audience-facing slide copy.
- Treat public-ready as a gate, not a tone.
- Use Gemini-agent for critique and review, not direct editing.
- Keep each deck isolated so subagents can work in parallel.

## Related Files

- [Deck Briefs](deck-briefs.md)
- [Output Templates](output-templates.md)
- [Superpowers Prompt Pack](prompts/superpowers-parallel-deck-prompts.md)
- [Gemini-Agent Prompt Pack](prompts/gemini-agent-prompt-pack.md)
- [Design Spec](../../superpowers/specs/2026-06-12-parallel-usecase-ppt-pilots-design.md)
- [Implementation Plan](../../superpowers/plans/2026-06-12-parallel-usecase-ppt-pilots.md)
