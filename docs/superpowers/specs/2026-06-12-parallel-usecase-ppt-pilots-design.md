# Parallel Usecase PPT Pilots Design

**Status:** approved for prompt and deck-brief artifact setup
**Date:** 2026-06-12
**Branch:** `codex/vulca-ppt-case-pack`
**Thread:** `codex://threads/019eb888-406f-7203-b211-d0a69f3c63f1`

## Decision

Stop treating Run 2.92 as the main object to polish. The latest generated deck
improved text-to-object binding, but the public-facing story still reads as an
internal renderer QA artifact. The next work should create parallel usecase
pilots with clean input briefs and separate prompts, then use those pilots to
judge whether Vulca can make a more natural presentation.

The parallel work should produce three independent deck briefs:

1. **Brand-Safe AI Creative Production**: a real-market usecase pilot based on
   public references such as Coca-Cola Create Real Magic and Adobe Firefly
   Creative Production.
2. **Vulca Product Strategy**: Vulca's own product narrative, focused on what
   the main product is and what it should do next.
3. **Vulca Workflow Demo**: a meta deck showing how a real usecase becomes an
   editable, reviewable deck through the Vulca workflow.

These decks must not inherit Run 2.92's public-copy failure. Internal trace
terms such as `primitive`, `run`, `public blocked`, `bound proof`, `native deck`,
and file ids belong in speaker notes, QA ledgers, or trace manifests. They do
not belong in audience-facing slide copy unless the deck is explicitly an
engineering appendix.

## Why This Change Is Needed

Run 2.92 has enough words, but not enough audience-facing meaning. The text is
mostly internal product-lab language: renderer ids, primitive ids, gate labels,
and proof labels. The images are also internal: abstract product surfaces,
outline boxes, connector residue, and small labels. Text and image are closer
on the canvas, but they still do not form a believable commercial object.

The next test should start from a concrete business usecase. A good product deck
should show a real user, a real workflow, a product action, an outcome, and a
decision. It should not ask the audience to understand the renderer.

## Primary Sources For The First Market Usecase

Use primary or official sources first. Secondary sources are allowed only to
find leads, not to support deck claims.

- Coca-Cola Create Real Magic official announcement:
  `https://www.coca-colacompany.com/media-center/coca-cola-invites-digital-artists-to-create-real-magic-using-new-ai-platform`
- Adobe Firefly Creative Production:
  `https://business.adobe.com/products/firefly-business/firefly-creative-production.html`
- Adobe Firefly Creative Production workflows:
  `https://business.adobe.com/products/firefly-business/firefly-creative-production/production-workflows.html`
- Adobe Creative Production overview:
  `https://helpx.adobe.com/firefly/web/work-with-enterprise-features/creative-production/creative-production-overview.html`
- Adobe workflow run/test/publish docs:
  `https://helpx.adobe.com/firefly/web/work-with-enterprise-features/creative-production/run-workflows.html`

Allowed derived observations:

- brand-safe AI creative production is moving from one-shot generation toward
  repeatable, governed workflows;
- campaign variant production, localization, approved inputs, review, and
  downstream delivery are credible workflow concepts;
- Coca-Cola's AI campaign proves that brand archives and generative tools can
  become a public creative participation surface;
- Adobe's enterprise materials prove that workflow builder, variants, brand
  governance, testing, publishing, and downstream systems are real product
  categories.

Forbidden use:

- do not copy brand visuals, logos, screenshots, layouts, or long source prose;
- do not make claims about adoption numbers, revenue, or performance unless an
  official source explicitly supports them;
- do not imply Coca-Cola or Adobe endorse Vulca.

## Deck Portfolio

### Deck A: Brand-Safe AI Creative Production

**Audience:** AI product builders, brand operations leaders, and creative
workflow owners.

**Decision:** Should a brand team use a governed AI creative workflow instead of
uncontrolled one-shot generation?

**Product concept:** A campaign workflow builder that turns an approved brand
brief, approved asset set, channel requirements, and review policy into editable
creative variants and a presentation-ready review packet.

**Six-slide arc:**

1. Campaign production has shifted from single hero assets to variant systems.
2. Real market signals show brand AI needs governance, not only generation.
3. The product workflow: brief -> approved assets -> workflow -> variants ->
   review -> delivery.
4. The control layer: brand rules, source boundaries, editable outputs, and
   review gates.
5. The payoff: one campaign can become many channel-ready variants without
   losing brand governance.
6. Decision: production is ready only when workflow, brand, and review gates
   pass.

### Deck B: Vulca Product Strategy

**Audience:** product advisors, design partners, and early platform reviewers.

**Decision:** What should Vulca's main product become next?

**Core thesis:** Vulca should position as the agent-native visual production
control layer. It should not compete with image models as a one-shot generator.
It should help agents structure visual intent, choose providers, edit pixels,
evaluate output, and emit inspectable artifacts such as editable decks.

**Six-slide arc:**

1. The market has enough image generation; it lacks controlled visual workflow.
2. Vulca owns the control layer around generation.
3. The product loop: discover -> brief -> spec -> plan -> generate/edit ->
   evaluate -> package.
4. The wedge: usecase-first editable presentation generation.
5. The moat: workflow memory, cultural evaluation, provider routing, and layer
   editing combine into repeatable visual production.
6. Next product bet: build the usecase research-to-deck pipeline as the first
   public product surface.

### Deck C: Vulca Workflow Demo

**Audience:** people who need to understand how the system works without seeing
internal trace language on the slides.

**Decision:** Can Vulca turn a real researched usecase into an editable,
reviewable deck with visible product value?

**Six-slide arc:**

1. Start with a real commercial usecase, not a generic prompt.
2. Convert research into allowed observations and source boundaries.
3. Turn observations into a claim spine and visual plan.
4. Generate editable native slide structures and optional visual assets.
5. Evaluate against business specificity, editability, visual quality, and
   provenance.
6. Hand off a deck plus QA ledger, not a vibes-only output.

## Shared Output Format

Each deck must produce the following Markdown files before any PPT generation:

- `research_brief.md`: source list, derived observations, forbidden claims, and
  unresolved facts.
- `deck_brief.md`: audience, decision, product concept, six-slide arc, and
  public-copy ban list.
- `claim_spine.md`: one thesis, six slide claims, proof object per slide, and
  omission notes.
- `visual_brief.md`: layout families, image/asset policy, typography direction,
  and public-facing visual style.
- `generation_prompt.md`: prompt for the renderer or deck generator.
- `qa_prompt.md`: prompt for Gemini and human reviewers to judge the deck.

The file set is intentionally parallel. A Deck A subagent should be able to
work without reading Deck B or Deck C except for the shared policy.
All files must follow
`docs/product/ppt-parallel-usecase-pilots/output-templates.md`.

## Superpowers Integration

Use Superpowers as the work-management frame:

- **brainstorming:** already used to select the parallel-deck direction.
- **writing-plans:** use the companion implementation plan for task-by-task
  execution.
- **dispatching-parallel-agents:** dispatch one subagent per deck after the
  shared policy is written.
- **verification-before-completion:** verify file existence, no forbidden copy,
  and Markdown link/source integrity before committing.

Each subagent must return:

- files created or modified;
- source facts used;
- claims intentionally omitted;
- blockers;
- recommendation on whether to proceed to PPT generation.

## Gemini-Agent Integration

Use `gemini-agent` as an independent reviewer, not as an editor:

- `research-brief --file <research_brief.md>` checks whether the source brief is
  sufficiently grounded and whether claims overreach sources.
- `plan-critique --file <deck_brief.md>` checks whether the deck plan has a
  coherent commercial arc.
- `artifact-review --file <contact-sheet.png> --kind design --review-mode single`
  checks generated deck previews later.
- `diff-review --diff` reviews committed prompt/design changes before a commit
  when the diff is broad.

Gemini output is advisory. Codex owns source verification, file edits,
validation, commits, and final claims.

## Quality Gates

Before any deck moves to PPT generation, it must pass:

- every slide has an audience-facing claim;
- every slide has a business object or workflow object, not just a trace object;
- no slide headline contains internal renderer vocabulary;
- every claim maps to source ids or `internal_strategy_thesis`;
- the deck references primary sources for market facts;
- source visuals are not copied;
- output is allowed to remain public blocked until render and human review pass.

## Non-Goals

- Do not generate new PPTX files in this prompt-design pass.
- Do not update `ppt-run-viewer.html`.
- Do not rewrite Run 2.92 or Run 2.93.
- Do not create a fake public-ready claim.
- Do not invent metrics for Coca-Cola, Adobe, or Vulca.
