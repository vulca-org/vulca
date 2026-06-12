# Vulca Workflow Demo Deck Brief

Status: draft-public-blocked

## Audience

Users, design partners, and product reviewers who need to understand Vulca's usecase-to-deck workflow without reading source code or implementation records.

## Decision

Should the team proceed to generate a six-slide workflow demo deck that shows Vulca converting a researched usecase into an editable, reviewable deck package?

## Thesis

Vulca's demo value is the governed path from researched usecase to editable review packet, not a one-click finished deck. source_ids: internal_strategy_thesis

## Product Or Workflow Concept

A source-to-deck product surface: usecase intake, source boundary ledger, claim spine board, visual plan, editable slide draft, review board, and handoff packet.

The proof objects are conceptual workflow-demo surfaces for explaining the product experience. They should not be presented as shipped application screens or as a fully automated one-click deck product.

## Six-Slide Arc

| Slide | Role | Audience-Facing Claim | Proof Object | Source Or Basis |
| --- | --- | --- | --- | --- |
| 1 | cover | A real usecase enters as a business decision, not a loose prompt. | Conceptual usecase intake surface with audience, decision, source packet, and desired output. | src_deck_c_brief, internal_strategy_thesis |
| 2 | research | The first product surface separates allowed observations from claims that stay out. | Conceptual source boundary ledger with allowed and blocked lanes. | src_output_templates, src_generation_protocol, src_vulca_ppt_skill |
| 3 | planning | The workflow turns evidence into a claim spine, visual brief, and generation prompt before slides are made. | Conceptual planning board with six slide slots, claim cards, visual direction, and prompt handoff. | src_output_templates, src_deck_c_brief, src_workflow_contract |
| 4 | generation | The deck draft should be built from editable slide objects, while orchestration stays separate from Vulca MCP capabilities. | Editable slide canvas showing native text, shapes, grouped diagrams, asset callouts, and an agent-side orchestration boundary. | src_vulca_ppt_skill, src_generation_protocol |
| 5 | evaluation | The generated deck is judged on editability, provenance, visual quality, and fit to the usecase before any release claim. | Conceptual review board with pass/repair lanes and a visual-quality note. | src_workflow_contract, src_generation_protocol, src_run2_93_eval |
| 6 | handoff | The useful output is a reviewable deck package plus a clear next repair decision. | Conceptual handoff packet with deck file, source ledger, review checklist, and decision state. | src_deck_c_brief, src_vulca_ppt_skill, src_generation_protocol, internal_strategy_thesis |

## Failure Modes

- The deck becomes a list of implementation ids instead of a readable product workflow.
- The story implies a public-ready or fully automated outcome before review gates pass.
- The proof objects become dense status grids instead of clean, dominant product surfaces.
- The deck treats prior visual evaluation as proof of polish instead of evidence for the repair loop.
- Current Vulca MCP capabilities are mixed together with agent-side deck orchestration.
- Conceptual product surfaces look like shipped UI screens without maturity or review-gate labels.

## Copy Ban Applied

Confirm audience-facing copy avoids the shared banned internal terms and does not use source ids, file paths, or implementation labels as the main slide story.
