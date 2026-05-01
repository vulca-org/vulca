# Condition A: One-shot model baseline

workflow_stage: one-shot

purpose: Raw real brief condensed into a single model ask.

## Prompt

Create the requested creative output for this real brief.

Client: Seattle Polish Film Festival
Context: Signature poster concept for the 34th festival edition.
Audience:
- festival attendees
- Polish cinema community
- Seattle arts audience
Required deliverables:
- poster concept (11 x 17 in vertical, print/digital)
- program cover adaptation (same key art, print)
Constraints:
- required festival text must be present
- dates, venues, website, and producer line must be accounted for
- bottom sponsor or patron logo band must remain available
- print output should anticipate CMYK and 300 dpi production
Budget: not specified by source
Timeline: source-specific contest deadline
Risks:
- broken generated text
- unsafe margins
- generic Polish national symbolism
- missing sponsor band
Avoid:
- illegible typography
- crowded logo area
- flag-only concept
AI policy: unspecified
Simulation only: True

Return a polished concept and any visual prompt needed to generate it.
