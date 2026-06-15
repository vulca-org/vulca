# Prompt Control Memory

Vault status: protected technical memory.

## Why Prompt Control Exists

VULCA does not treat prompt text as a single flat string. The project invested
in structured prompt control because visual failures often came from:

- weak CJK tokenization in local models
- provider-specific parameter drift
- missing negative prompts
- unclear style treatment
- global style wash when user wanted additive elements
- prompt/source mismatch across plan/spec/execution

## Core Artifacts

The visual workflow stabilizes prompt control through artifacts:

- `proposal.md`
- `design.md`
- `plan.md`
- frozen tradition tokens
- style treatment
- negative prompt
- provider request metadata
- prompt hashes in case records

## Visual Skill Chain

### `/visual-brainstorm`

Converts fuzzy intent into a proposal. It is scoped to 2D visual artifacts and
must preserve acceptance rubric and handoff boundaries.

### `/visual-spec`

Turns ready proposal into design. It validates schema and derives prompt
material from locked design decisions.

### `/visual-plan`

Reviews plan and executes only after explicit acceptance. It should not skip
review gates because real image calls can cost money and create artifacts that
look more final than they are.

## Provider Prompt Controls

Current prompt-related controls include:

- `seed`
- `steps`
- `cfg_scale`
- `negative_prompt`
- `quality`
- `output_format`
- model-aware provider capabilities
- `compose_prompt_from_design`

Boundary: public copy should say VULCA structures prompts and provider requests.
It should not claim prompt control guarantees model obedience.

## Important Historical Lesson

The prompt-engineering experiment showed that English-first prompt rewrites,
negative prompts, and suffix suppression can rescue some subject-fidelity
failures. It did not prove all cultural prompting works or that cultural terms
always improve generation.

Public claim must remain:

> VULCA creates structured, reviewable prompt artifacts and provider-specific
> constraints.

Not:

> VULCA guarantees culturally correct generation.

Sources:

- `docs/superpowers/specs/2026-04-11-prompt-engineering-experiment-design.md`
- `docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md`
- `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md`
- `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md`
- `tests/test_prompting.py`
