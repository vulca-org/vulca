# PPT Parallel Usecase Pilots

Status: prompt-design-ready-public-blocked

This package defines three parallel PPT pilots. It does not generate PPTX
files, update the existing viewer, or change Run 2.92. The purpose is to replace
Run 2.92's internal trace-first story with concrete usecase-first deck briefs
and prompts.

## Why This Exists

Run 2.92 improved text-to-object binding, but the slide story still feels
strange because the text and visuals describe internal renderer mechanics. The
next test should start from real usecases and audience-facing product stories.

## Decks

- **Deck A:** Brand-Safe AI Creative Production.
- **Deck B:** Vulca Product Strategy.
- **Deck C:** Vulca Workflow Demo.

Each deck should produce the same six Markdown outputs before any PPT
generation:

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
