# Brand-Safe AI Creative Production QA Prompt

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
- Does the deck avoid implying that Coca-Cola or Adobe endorses Vulca?
- Does the deck avoid using Coca-Cola visuals, Adobe visuals, source screenshots, source layouts, or long source prose?
- Search slide copy, claim text, proof captions, and generation text for these banned terms: `primitive`, `Run 2.92`, `Run 2.93`, `public blocked`, `bound proof`, `trace manifest`, `renderer id`, `arm id`, `debug`, `QA artifact`.

Return:
- verdict: proceed_to_generation, revise_brief, or block;
- strongest slide;
- weakest slide;
- unsupported claim risk;
- visual risk;
- next action.
