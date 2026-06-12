# Gemini-Agent Prompt Pack

Status: prompt-design-ready-public-blocked

Use these prompts after a deck subagent creates its Markdown input pack.
Gemini-agent is an advisory reviewer only. Codex owns edits, verification,
commits, and final claims.

## Research Brief Review

Command:

```bash
gemini-agent research-brief --file docs/product/ppt-parallel-usecase-pilots/deck-a-brand-safe-ai-creative-production/research_brief.md
```

Prompt intent:

```text
Review this research brief for source grounding and unsafe commercial claims.

Check:
- Are all business claims supported by primary or official sources?
- Are any source facts overstated?
- Are any adoption, revenue, performance, or customer-outcome claims invented?
- Are source boundaries clear enough to avoid copied visuals, layouts, brand
  marks, screenshots, long source prose, or implied endorsement?
- What claims should be removed, softened, or moved to open questions?

Return:
- verdict: pass, caution, or block;
- top source risks;
- unsupported claims;
- missing primary sources;
- suggested changes.
```

## Deck Plan Critique

Command:

```bash
gemini-agent plan-critique --file docs/product/ppt-parallel-usecase-pilots/deck-a-brand-safe-ai-creative-production/deck_brief.md
```

Prompt intent:

```text
Critique this six-slide deck brief as a commercial presentation plan.

Check:
- Does the deck have a clear audience and decision?
- Does the deck follow `docs/product/ppt-parallel-usecase-pilots/output-templates.md`?
- Does each slide have a claim instead of a topic label?
- Does the sequence move from pressure to proof to decision?
- Does the plan avoid internal trace language such as primitive, run id,
  renderer, public blocked, bound proof, or trace manifest?
- Does the deck have enough concrete business objects to avoid looking like an
  internal QA artifact?
- Which slide is most likely to fail visually?

Return:
- verdict: pass, caution, or block;
- weakest slide;
- missing proof object;
- wording to remove;
- recommended next change before generation.
```

## Generation Prompt Precheck

Command:

```bash
gemini-agent patch-precheck --file docs/product/ppt-parallel-usecase-pilots/deck-a-brand-safe-ai-creative-production/generation_prompt.md
```

Prompt intent:

```text
Precheck this generation prompt before a deck renderer uses it.

Check:
- Does the prompt provide enough source, audience, and slide structure?
- Does every slide claim map to a source id or internal_strategy_thesis?
- Does it forbid copying source visuals and brand marks?
- Does it keep all core slide text editable?
- Does it ask for one dominant proof object per slide?
- Does it avoid asking for a dashboard, report grid, or internal trace surface?
- Does it include enough constraints to prevent hallucinated metrics?

Return:
- verdict: pass, caution, or block;
- likely failure mode;
- missing constraint;
- one recommended prompt rewrite.
```

## Contact Sheet Artifact Review

Command:

```bash
gemini-agent artifact-review \
  --file outputs/<thread-id>/presentations/<deck-slug>/preview/contact-sheet.png \
  --kind design \
  --review-mode single \
  --review-depth standard
```

Prompt intent:

```text
Review this contact sheet as a public-facing product presentation.

Check:
- Does the deck read as a real commercial product story?
- Are text and visual objects semantically fused, not merely co-located?
- Does each slide have enough audience-facing content?
- Do the main visuals look like believable business/product objects?
- Does the deck avoid internal QA labels and renderer language?
- Are any slides too sparse, wireframe-like, or diagrammatic?
- Is there a visible climax?

Return:
- verdict: public_candidate, internal_only, or block;
- strongest slide;
- weakest slide;
- top visual blocker;
- top content blocker;
- whether to rerun or revise the brief first.
```

## Diff Review Before Commit

Command:

```bash
gemini-agent diff-review --diff
```

Prompt intent:

```text
Review the staged or working diff for prompt/design risks.

Check:
- Are the new files scoped to Markdown and prompt design?
- Do the generated deck files follow the shared output templates?
- Do they accidentally authorize PPT generation or viewer updates?
- Do they overstate source facts?
- Do they copy source prose?
- Do they create conflicting instructions for Superpowers or Gemini-agent?
- Are public-ready claims blocked until render and human review?

Return:
- verdict: pass, caution, or block;
- blockers;
- confusing instructions;
- suggested changes.
```
