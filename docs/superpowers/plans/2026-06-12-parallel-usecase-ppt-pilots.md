# Parallel Usecase PPT Pilots Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create parallel Markdown briefs and prompt packs for three usecase-first PPT pilots without generating new PPT files.

**Architecture:** Add a standalone `docs/product/ppt-parallel-usecase-pilots/` package. The package separates shared policy, deck briefs, Superpowers prompts, and Gemini-agent prompts so each deck can be researched and designed independently.

**Tech Stack:** Markdown, existing repository documentation conventions, Superpowers process skills, `gemini-agent` review commands, official web sources captured as URLs.

---

## File Map

- Create: `docs/product/ppt-parallel-usecase-pilots/README.md`
- Create: `docs/product/ppt-parallel-usecase-pilots/deck-briefs.md`
- Create: `docs/product/ppt-parallel-usecase-pilots/output-templates.md`
- Create: `docs/product/ppt-parallel-usecase-pilots/prompts/superpowers-parallel-deck-prompts.md`
- Create: `docs/product/ppt-parallel-usecase-pilots/prompts/gemini-agent-prompt-pack.md`
- Create: `docs/superpowers/specs/2026-06-12-parallel-usecase-ppt-pilots-design.md`
- Create: `docs/superpowers/plans/2026-06-12-parallel-usecase-ppt-pilots.md`

Generated later, but not in this pass:

- `docs/product/ppt-parallel-usecase-pilots/deck-a-brand-safe-ai-creative-production/research_brief.md`
- `docs/product/ppt-parallel-usecase-pilots/deck-b-vulca-product-strategy/research_brief.md`
- `docs/product/ppt-parallel-usecase-pilots/deck-c-vulca-workflow-demo/research_brief.md`
- matching `deck_brief.md`, `claim_spine.md`, `visual_brief.md`, `generation_prompt.md`, and `qa_prompt.md` for each deck.

## Task 1: Add Shared Parallel Pilot Package

**Files:**
- Create: `docs/product/ppt-parallel-usecase-pilots/README.md`
- Create: `docs/product/ppt-parallel-usecase-pilots/deck-briefs.md`

- [ ] **Step 1: Create the shared README**

Write the README with:

```markdown
# PPT Parallel Usecase Pilots

Status: prompt-design-ready-public-blocked

This package defines three parallel PPT pilots. It does not generate PPTX files.
The purpose is to replace Run 2.92's internal trace-first story with concrete
usecase-first deck briefs.
```

- [ ] **Step 2: Create the three-deck brief file**

Write `deck-briefs.md` with Deck A, Deck B, and Deck C sections. Each section
must include audience, decision, thesis, six-slide arc, source policy, and copy
ban list.

- [ ] **Step 3: Verify file presence**

Run:

```bash
test -f docs/product/ppt-parallel-usecase-pilots/README.md
test -f docs/product/ppt-parallel-usecase-pilots/deck-briefs.md
test -f docs/product/ppt-parallel-usecase-pilots/output-templates.md
```

Expected: both commands exit `0`.

## Task 2: Add Superpowers Prompt Pack

**Files:**
- Create: `docs/product/ppt-parallel-usecase-pilots/prompts/superpowers-parallel-deck-prompts.md`

- [ ] **Step 1: Write the orchestrator prompt**

The prompt must tell the main agent to dispatch one subagent per deck, keep
deck outputs isolated, and prohibit PPT generation in the brief-building pass.

- [ ] **Step 2: Write deck-specific subagent prompts**

Include prompts for:

- Deck A research and brief subagent.
- Deck B Vulca product strategy subagent.
- Deck C workflow demo subagent.

Each subagent prompt must require `research_brief.md`, `deck_brief.md`,
`claim_spine.md`, `visual_brief.md`, `generation_prompt.md`, and `qa_prompt.md`.
Each prompt must also require compliance with `output-templates.md`.

- [ ] **Step 3: Verify prompt boundaries**

Run:

```bash
rg -n "Do not generate PPT|Do not update|do not copy|research_brief.md|claim_spine.md|output-templates.md" docs/product/ppt-parallel-usecase-pilots/prompts/superpowers-parallel-deck-prompts.md
```

Expected: matches for all required boundary phrases.

## Task 3: Add Gemini-Agent Prompt Pack

**Files:**
- Create: `docs/product/ppt-parallel-usecase-pilots/prompts/gemini-agent-prompt-pack.md`

- [ ] **Step 1: Write research review prompt**

The prompt must ask Gemini to flag unsupported commercial claims, missing
primary sources, and forbidden source-copy risks.

- [ ] **Step 2: Write plan critique prompt**

The prompt must ask Gemini to judge deck arc coherence, slide-level claim
strength, and whether the plan avoids internal trace language.

- [ ] **Step 3: Write artifact review prompt**

The prompt must ask Gemini to review later contact sheets for audience-facing
clarity, visual realism, text-image fusion, and public-readiness blockers.

- [ ] **Step 4: Verify command examples**

Run:

```bash
rg -n "gemini-agent research-brief|gemini-agent plan-critique|gemini-agent artifact-review|gemini-agent diff-review" docs/product/ppt-parallel-usecase-pilots/prompts/gemini-agent-prompt-pack.md
```

Expected: four command examples are present.

## Task 4: Run Local Verification And Gemini Review

**Files:**
- Review: all files created in this plan.

- [ ] **Step 1: Check Markdown and source URLs**

Run:

```bash
rg -n "https://|public blocked|primitive|Run 2.92|Coca-Cola|Adobe|output-templates.md" docs/product/ppt-parallel-usecase-pilots docs/superpowers/specs/2026-06-12-parallel-usecase-ppt-pilots-design.md
```

Expected: URLs and allowed internal references are visible only in design and
prompt-policy contexts.

- [ ] **Step 2: Run Gemini plan critique**

Run:

```bash
gemini-agent plan-critique --file docs/superpowers/specs/2026-06-12-parallel-usecase-ppt-pilots-design.md
```

Expected: Gemini returns no blocker that requires changing the prompt package.

- [ ] **Step 3: Run git diff check**

Run:

```bash
git diff --check
```

Expected: no whitespace errors.

- [ ] **Step 4: Commit**

Run:

```bash
git add docs/product/ppt-parallel-usecase-pilots docs/superpowers/specs/2026-06-12-parallel-usecase-ppt-pilots-design.md docs/superpowers/plans/2026-06-12-parallel-usecase-ppt-pilots.md
git commit -m "docs: add parallel usecase ppt pilot prompts"
```

Expected: commit succeeds.
