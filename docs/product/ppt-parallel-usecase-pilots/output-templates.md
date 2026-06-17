# Parallel Deck Output Templates

Status: prompt-design-ready-public-blocked

Every deck subagent must follow these exact Markdown section headings. The
templates are intentionally strict so Deck A, Deck B, and Deck C can be
compared without reading each subagent's private reasoning.

## Required Directory Shape

Each deck owns one directory:

```text
docs/product/ppt-parallel-usecase-pilots/<deck-slug>/
  research_brief.md
  deck_brief.md
  claim_spine.md
  visual_brief.md
  generation_prompt.md
  qa_prompt.md
```

## Audience-Facing Copy Ban

The following terms are banned from audience-facing slide titles, slide body
copy, claim text, proof captions, and generation prompts:

```text
primitive
Run 2.92
Run 2.93
public blocked
bound proof
trace manifest
renderer id
arm id
debug
QA artifact
```

Allowed locations:

- source-boundary notes;
- QA prompts;
- internal implementation notes;
- Superpowers plans;
- Gemini review instructions.

## Source Id Convention

Every source gets a short id:

```text
src_coca_cola_create_real_magic
src_adobe_firefly_creative_production
src_adobe_workflow_builder
src_vulca_readme
src_vulca_run2_93_eval
```

Every claim must list one or more source ids, or be marked:

```text
source_ids: internal_strategy_thesis
```

Use `internal_strategy_thesis` only for Vulca's own positioning ideas. Do not
use it for external market facts.

## `research_brief.md`

```markdown
# <Deck Name> Research Brief

Status: draft-public-blocked

## Research Question

<One sentence.>

## Source Table

| Source Id | URL Or Local Path | Source Type | Allowed Use | Do Not Use |
| --- | --- | --- | --- | --- |
| src_example | https://example.com | official page | derived observations | screenshots, logos, long prose |

## Derived Observations

| Observation Id | Source Ids | Observation | Deck Use |
| --- | --- | --- | --- |
| obs_01 | src_example | <Paraphrased observation.> | <How it can shape the deck.> |

## Allowed Claims

| Claim Id | Source Ids | Claim | Confidence |
| --- | --- | --- | --- |
| claim_01 | src_example | <Claim the deck may make.> | high |

## Forbidden Or Unproven Claims

| Claim | Reason |
| --- | --- |
| <Claim not allowed.> | <Why unsupported.> |

## Open Questions

- <Question that needs more research or human decision.>
```

## `deck_brief.md`

```markdown
# <Deck Name> Deck Brief

Status: draft-public-blocked

## Audience

<Who this deck is for.>

## Decision

<The decision the deck should help the audience make.>

## Thesis

<One sentence.>

## Product Or Workflow Concept

<Concrete product/workflow object.>

## Six-Slide Arc

| Slide | Role | Audience-Facing Claim | Proof Object | Source Or Basis |
| --- | --- | --- | --- | --- |
| 1 | cover | <Claim, not topic.> | <Object.> | <source ids or internal_strategy_thesis> |

## Failure Modes

- <How this deck can fail.>

## Copy Ban Applied

Confirm audience-facing copy avoids the banned internal terms.
```

## `claim_spine.md`

```markdown
# <Deck Name> Claim Spine

Status: draft-public-blocked

## Thesis

<One sentence.>

## Claims

| Slide | Claim Id | Claim | Source Ids | Proof Object | Omission Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | claim_slide_01 | <Claim.> | <source ids> | <Object.> | <What not to show.> |

## Appendix Candidates

- <Evidence that should not be on main slides.>
```

## `visual_brief.md`

```markdown
# <Deck Name> Visual Brief

Status: draft-public-blocked

## Visual Mood

<Editorial/product/strategy direction.>

## Layout Families

| Slide | Layout Family | Dominant Object | Typography Notes |
| --- | --- | --- | --- |
| 1 | <family> | <object> | <notes> |

## Asset Policy

- <What visual assets are allowed.>
- <What source assets are forbidden.>

## Anti-Patterns

- <Visual failure to avoid.>
```

## `generation_prompt.md`

```markdown
# <Deck Name> Generation Prompt

Status: draft-public-blocked

## Prompt

Create a six-slide editable PowerPoint deck for <audience>.

The deck decision is: <decision>.

Use this thesis: <thesis>.

Use this six-slide arc:
1. <claim + proof object>
2. <claim + proof object>
3. <claim + proof object>
4. <claim + proof object>
5. <claim + proof object>
6. <claim + proof object>

Constraints:
- Keep all core text editable.
- Use one dominant proof object per slide.
- Do not copy source visuals, logos, screenshots, layouts, or long prose.
- Do not invent metrics.
- Do not use banned internal trace words in slide copy.
- Keep public readiness blocked until render and human review pass.

## Source Boundary

<Summarize allowed and forbidden source usage.>
```

## `qa_prompt.md`

```markdown
# <Deck Name> QA Prompt

Status: draft-public-blocked

## Gemini Or Human Review Prompt

Review this deck as a public-facing product presentation.

Check:
- Does every slide have an audience-facing claim?
- Does every claim map to source ids or a clearly marked internal strategy thesis?
- Does the deck avoid banned internal trace terms in public copy?
- Does the deck show concrete business/product objects?
- Does the deck avoid copied source visuals and unsupported metrics?
- Does the deck have a visible climax and a clear decision handoff?

Return:
- verdict: proceed_to_generation, revise_brief, or block;
- strongest slide;
- weakest slide;
- unsupported claim risk;
- visual risk;
- next action.
```

## Verification Commands

Run these checks after each deck subagent finishes:

```bash
test -f docs/product/ppt-parallel-usecase-pilots/<deck-slug>/research_brief.md
test -f docs/product/ppt-parallel-usecase-pilots/<deck-slug>/deck_brief.md
test -f docs/product/ppt-parallel-usecase-pilots/<deck-slug>/claim_spine.md
test -f docs/product/ppt-parallel-usecase-pilots/<deck-slug>/visual_brief.md
test -f docs/product/ppt-parallel-usecase-pilots/<deck-slug>/generation_prompt.md
test -f docs/product/ppt-parallel-usecase-pilots/<deck-slug>/qa_prompt.md

rg -n "primitive|Run 2\\.92|Run 2\\.93|public blocked|bound proof|trace manifest|renderer id|arm id|debug|QA artifact" \
  docs/product/ppt-parallel-usecase-pilots/<deck-slug>/deck_brief.md \
  docs/product/ppt-parallel-usecase-pilots/<deck-slug>/claim_spine.md \
  docs/product/ppt-parallel-usecase-pilots/<deck-slug>/generation_prompt.md
```

The second command should return no matches for audience-facing files. If it
returns matches, rewrite those files before generation.
