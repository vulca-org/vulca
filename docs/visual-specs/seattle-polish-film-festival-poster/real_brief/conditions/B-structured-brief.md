# Condition B: Structured brief baseline

workflow_stage: structured-brief

purpose: Same brief normalized into structured client, deliverable, and constraint fields.

## Prompt

Create a direction from the structured brief below.

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

Success criteria:
- satisfy required deliverables
- respect every listed constraint
- identify the most production-relevant risk
