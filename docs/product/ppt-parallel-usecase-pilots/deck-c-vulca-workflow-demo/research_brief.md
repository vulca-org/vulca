# Vulca Workflow Demo Research Brief

Status: draft-public-blocked

## Research Question

How can a six-slide workflow demo show Vulca turning a real researched usecase into an editable, reviewable deck without overclaiming automation or public readiness?

## Source Table

| Source Id | URL Or Local Path | Source Type | Allowed Use | Do Not Use |
| --- | --- | --- | --- | --- |
| src_output_templates | docs/product/ppt-parallel-usecase-pilots/output-templates.md | local template | required six-file contract, source-id rules, copy boundaries, QA prompt shape | external market evidence, source visuals |
| src_deck_c_brief | docs/product/ppt-parallel-usecase-pilots/deck-briefs.md | local deck brief | Deck C audience, decision, thesis, six-slide arc, proof objects, risk | finished public slide copy, evidence of shipped automation |
| src_workflow_contract | docs/product/ppt-run2-data-skill-quality/skill_workflow.json | local declarative workflow contract | staged workflow order, inputs, outputs, gates, repair and release boundaries | audience-facing internal ids, proof of one-click product availability |
| src_vulca_ppt_skill | docs/product/ppt-run2-data-skill-quality/vulca_ppt_skill.md | local skill protocol | editable-native PPT requirements, source boundaries, QA and release gate constraints | public-ready claim, copied source media, raw implementation labels as the story |
| src_generation_protocol | docs/product/ppt-run2-data-skill-quality/generation_protocol.md | local generation protocol | runtime isolation, native PPT QA, layout QA, scoring and motion boundaries | claim that animation/video output or public release is already proven |
| src_run2_93_eval | docs/product/ppt-run2-data-skill-quality/results/run2_93_visual_quality_evaluation.md | local evaluation result | evidence that prior visual output still needed polish, legibility, and surface realism repair | reusable audience-facing copy, public-ready claim |
| src_vulca_readme | README.md | local product README | current MCP and agent-skill capabilities for visual discovery, generation, edit, evaluation, and archive workflows | claim that the deck workflow is a dedicated Vulca MCP tool |

## Derived Observations

| Observation Id | Source Ids | Observation | Deck Use |
| --- | --- | --- | --- |
| obs_01 | src_deck_c_brief | Deck C is meant for users who need to understand the Vulca workflow without reading source code or internal implementation records. | Keep the main story as product surfaces and review stages. |
| obs_02 | src_deck_c_brief | The requested arc is usecase, research, planning, generation, evaluation, and handoff. | Use six slides that read like a workflow demo rather than a status report. |
| obs_03 | src_output_templates | Every deck output must include the same six Markdown files and every claim must map to source ids or internal_strategy_thesis. | Make the pack generation-ready and comparable with sibling decks. |
| obs_04 | src_workflow_contract, src_vulca_ppt_skill | The workflow contract records staged inputs, outputs, gates, module selections, QA, repair recommendations, and release decisions. | Convert internal stages into a clean visible product journey. |
| obs_05 | src_vulca_ppt_skill, src_generation_protocol | Core deck text, claims, labels, charts, diagrams, and proof annotations should be editable native PowerPoint objects rather than flattened images. | Make editability a visible slide-4 claim and proof object. |
| obs_06 | src_vulca_ppt_skill, src_generation_protocol | Source material must be used as derived observations only; copied source prose, screenshots, frames, layouts, logos, and brand marks are forbidden. | Make slide 2 a source-boundary ledger with allowed and blocked lanes. |
| obs_07 | src_generation_protocol | Motion grammar is a metadata and native-object sequencing boundary until native PPT objects, static layout quality, render checks, and approvals pass. | Avoid claiming finished animation or public video capability. |
| obs_08 | src_workflow_contract, src_generation_protocol | Structural QA, layout checks, visual validation, Gemini or human review, and human approval are gates before release language can advance. | Make slide 5 a review board and slide 6 a repair decision handoff. |
| obs_09 | src_run2_93_eval | The prior evaluation found improved text-object binding but blocked public-quality design due to polish, legibility, and surface realism gaps. | Show evaluation as a repair loop, not a victory lap. |
| obs_10 | src_vulca_readme | Vulca currently exposes MCP tools and agent skills for visual intent workflows including discovery, specification, generation, editing, evaluation, and archiving. | State current capabilities separately from the deck-specific agent workflow. |

## Allowed Claims

| Claim Id | Source Ids | Claim | Confidence |
| --- | --- | --- | --- |
| claim_01 | src_deck_c_brief, internal_strategy_thesis | Vulca's demo value can be framed as the governed path from real usecase to reviewable visual artifact. | high |
| claim_02 | src_output_templates, src_generation_protocol, src_vulca_ppt_skill | A usable deck workflow starts by separating allowed observations from blocked claims and forbidden source reuse. | high |
| claim_03 | src_output_templates, src_deck_c_brief, src_workflow_contract | The planning layer can be presented as a claim spine, visual brief, generation prompt, and QA prompt before deck generation. | high |
| claim_04 | src_vulca_ppt_skill, src_generation_protocol | The generated deck should keep core text and proof structures editable as native PowerPoint objects. | high |
| claim_05 | src_workflow_contract, src_generation_protocol, src_run2_93_eval | A generated deck should be evaluated for editability, provenance, visual quality, and repair needs before any public-ready claim. | high |
| claim_06 | src_vulca_readme | Current Vulca MCP capabilities cover image creation, prompt composition, visual evaluation, layer operations, inpainting, image viewing, session archiving, and tradition lookup. | high |
| claim_07 | src_vulca_readme, src_vulca_ppt_skill, src_generation_protocol | The usecase-to-deck workflow is currently best described as an agent-side workflow using documented deck inputs and generation rules, not as a dedicated Vulca MCP deck-generation tool. | medium |
| claim_08 | src_run2_93_eval | Prior generated deck work showed useful binding improvements but still required visual polish, legibility, and surface realism repair. | high |

## Forbidden Or Unproven Claims

| Claim | Reason |
| --- | --- |
| Vulca can automatically turn any researched usecase into a public-ready deck. | The sources require render, provenance, QA, and human approval gates before public-ready language. |
| Vulca exposes a dedicated MCP tool that generates complete PowerPoint decks from research briefs. | The inspected MCP surface covers visual creation, editing, evaluation, layers, image viewing, concepts, and archiving; deck assembly is documented as an agent-side workflow. |
| The prior generated deck is public-quality evidence. | The visual quality evaluation says the prior output still needed polish, legibility, and surface realism repair. |
| The demo may copy source screenshots, logos, layouts, video frames, or long prose. | The generation and skill protocols allow derived observations only and forbid copied source media or source prose. |
| Motion grammar proves finished animation or public video output. | The generation protocol treats motion grammar as metadata and native-object sequencing until further checks pass. |
| Repair recommendations can be accepted automatically. | The workflow contract says repair remains recommendation-only until accepted. |

## Open Questions

- Which real usecase should the first generated demo use if Deck A and Deck B packs are not yet available?
- Should source ids appear only in speaker notes and QA materials, or also in a hidden appendix?
- Which generator, renderer, and review owner will be responsible for the first PPT generation attempt?
- What threshold should a human reviewer use to move from reviewable demo candidate to public-ready release?
