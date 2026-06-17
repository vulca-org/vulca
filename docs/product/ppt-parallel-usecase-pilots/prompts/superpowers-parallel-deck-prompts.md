# Superpowers Parallel Deck Prompts

Status: prompt-design-ready-public-blocked

Use these prompts when dispatching parallel agents. The agents should produce
Markdown briefs and prompts only. Do not generate PPTX, do not update
`ppt-run-viewer.html`, and do not edit Run 2.92 or Run 2.93.

## Orchestrator Prompt

```text
You are coordinating three independent PPT usecase pilots in
/Users/yhryzy/.codex/worktrees/031a/vulca.

Use superpowers:dispatching-parallel-agents because the three decks are
independent:

1. Deck A: Brand-Safe AI Creative Production.
2. Deck B: Vulca Product Strategy.
3. Deck C: Vulca Workflow Demo.

Shared constraints:
- Create Markdown and prompt files only.
- Follow docs/product/ppt-parallel-usecase-pilots/output-templates.md exactly.
- Do not generate PPTX files.
- Do not update outputs/.../ppt-run-viewer.html.
- Do not edit Run 2.92 or Run 2.93 artifacts.
- Do not copy screenshots, logos, brand marks, source layouts, or long source
  prose from public references.
- Keep internal trace language out of audience-facing slide copy.
- Each deck must produce: research_brief.md, deck_brief.md, claim_spine.md,
  visual_brief.md, generation_prompt.md, qa_prompt.md.
- Each claim must map to source ids or internal_strategy_thesis.

After agents return:
- verify files exist;
- run source-boundary review;
- run gemini-agent research-brief or plan-critique on each deck;
- summarize which deck is ready for generation first.
```

## Deck A Subagent Prompt

```text
Build the Markdown input pack for Deck A: Brand-Safe AI Creative Production.

Workspace:
/Users/yhryzy/.codex/worktrees/031a/vulca

Output directory:
docs/product/ppt-parallel-usecase-pilots/deck-a-brand-safe-ai-creative-production/

Create exactly these files:
- research_brief.md
- deck_brief.md
- claim_spine.md
- visual_brief.md
- generation_prompt.md
- qa_prompt.md

Primary sources to inspect and cite as URLs:
- https://www.coca-colacompany.com/media-center/coca-cola-invites-digital-artists-to-create-real-magic-using-new-ai-platform
- https://business.adobe.com/products/firefly-business/firefly-creative-production.html
- https://business.adobe.com/products/firefly-business/firefly-creative-production/production-workflows.html
- https://helpx.adobe.com/firefly/web/work-with-enterprise-features/creative-production/creative-production-overview.html
- https://helpx.adobe.com/firefly/web/work-with-enterprise-features/creative-production/run-workflows.html

Deck goal:
Design a six-slide product deck for a brand-safe AI creative production
workflow. The product concept is a governed campaign workflow builder that turns
approved briefs, approved assets, channel requirements, and review rules into
editable creative variants and a presentation-ready review packet.

Hard boundaries:
- Do not imply Coca-Cola or Adobe endorse Vulca.
- Do not copy brand visuals, screenshots, logos, source layouts, or long source
  prose.
- Do not invent adoption numbers, revenue, performance, or customer outcomes.
- Keep internal terms such as primitive, run id, public blocked, renderer, and
  trace manifest out of audience-facing slide copy.

Required research_brief.md sections:
- Source table.
- Derived observations.
- Claims allowed by sources.
- Claims explicitly not allowed.
- Open questions.

Required deck_brief.md sections:
- Audience.
- Decision.
- Thesis.
- Product concept.
- Six-slide arc.
- Failure modes.

Required claim_spine.md:
- One thesis.
- Six slide claims.
- One proof object per slide.
- What not to include on each slide.

Required visual_brief.md:
- Visual mood.
- Layout families.
- Type hierarchy.
- Asset policy.
- Anti-patterns.

Required generation_prompt.md:
- A concise prompt for a later deck generator.
- Include source boundaries and public-copy ban list.

Required qa_prompt.md:
- Prompt for Gemini/human review.
- Ask whether the deck reads as a real commercial product, not an internal QA
  artifact.

Return:
- Files created.
- Template compliance.
- Key source facts.
- Claims omitted.
- Recommendation on whether to proceed to PPT generation.
```

## Deck B Subagent Prompt

```text
Build the Markdown input pack for Deck B: Vulca Product Strategy.

Workspace:
/Users/yhryzy/.codex/worktrees/031a/vulca

Output directory:
docs/product/ppt-parallel-usecase-pilots/deck-b-vulca-product-strategy/

Create exactly these files:
- research_brief.md
- deck_brief.md
- claim_spine.md
- visual_brief.md
- generation_prompt.md
- qa_prompt.md

Local sources to inspect:
- README.md
- docs/product/roadmap.md
- docs/product/ppt-run2-data-skill-quality/commercial_case.md
- docs/product/ppt-run2-data-skill-quality/generation_protocol.md
- docs/product/ppt-run2-data-skill-quality/results/run2_93_visual_quality_evaluation.md
- src/vulca/mcp_server.py

Deck goal:
Design a six-slide product strategy deck explaining what Vulca's main product
should become next. The deck should position Vulca as the agent-native visual
production control layer, not as a one-shot image generator or template deck
tool.

Hard boundaries:
- Do not make public-ready claims for current PPT outputs.
- Do not expose renderer ids, primitive ids, or internal run numbers in slide
  copy.
- Be honest about current gaps: web research to usecase pack is not yet a
  productized Vulca MCP tool.
- Keep the story external: product category, user problem, product loop,
  wedge, moat, next bet.

Required outputs follow the same six-file contract as Deck A and the shared
output template file.

Return:
- Files created.
- Template compliance.
- Product claims supported by repo files.
- Claims omitted or softened.
- Recommendation on whether to proceed to PPT generation.
```

## Deck C Subagent Prompt

```text
Build the Markdown input pack for Deck C: Vulca Workflow Demo.

Workspace:
/Users/yhryzy/.codex/worktrees/031a/vulca

Output directory:
docs/product/ppt-parallel-usecase-pilots/deck-c-vulca-workflow-demo/

Create exactly these files:
- research_brief.md
- deck_brief.md
- claim_spine.md
- visual_brief.md
- generation_prompt.md
- qa_prompt.md

Sources to inspect:
- docs/product/ppt-parallel-usecase-pilots/deck-briefs.md
- docs/product/ppt-run2-data-skill-quality/skill_workflow.json
- docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md
- docs/product/ppt-run2-data-skill-quality/generation_protocol.md
- docs/product/ppt-run2-data-skill-quality/results/run2_93_visual_quality_evaluation.md

Deck goal:
Design a six-slide workflow demo deck showing how Vulca turns a real usecase
into an editable, reviewable deck. This deck should make the workflow readable
as a product experience, not an internal trace manifest.

Hard boundaries:
- Do not show internal file ids as the main slide story.
- Do not claim a generated deck is public-ready.
- Do not reuse Run 2.92 copy.
- The workflow should be visible as clean product surfaces and review stages,
  not as debug labels.

Required outputs follow the same six-file contract as Deck A and the shared
output template file.

Return:
- Files created.
- Template compliance.
- Which Vulca capabilities are actually supported today.
- Which capabilities are aspirational or agent-side rather than Vulca MCP
  tools.
- Recommendation on whether to proceed to PPT generation.
```
