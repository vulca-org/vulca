# Design Notes

## Narrative

Lead with the workflow problem: teams can now create slides quickly, but speed does not guarantee design reasoning, commercial fit, or editable structure. Introduce Vulca as the layer that turns reference-aware design knowledge into code-generated presentation systems.

## Hierarchy

Each slide should carry one claim, one proof object, and a small amount of supporting detail. A viewer should know the slide's point within five seconds. Long explanations should become diagrams, matrices, or labeled workflow stages.

## Rhythm

The deck should alternate between low-density claim slides, structured workflow diagrams, proof pages, and comparison pages. Repeating a single card-grid pattern across the whole deck would undercut the premise that Vulca understands presentation rhythm.

## Typography

Use a system-safe stack first. Establish hierarchy through size, weight, line length, and alignment instead of depending on fragile custom fonts. Display type should be reserved for cover, section, and closing moments.

## Color

Use a warm neutral base with black ink and a small set of signal colors. Avoid a one-hue purple or blue AI palette. Signal color should mark workflow transitions, proof objects, evaluation status, or a clear before/after contrast.

## Assets

Use editable SVG and native shapes for systems, diagrams, arrows, nodes, product metaphors, matrices, and evaluation marks. Use generated bitmap images only for atmosphere or illustrative backgrounds that do not carry essential text.

## Anti-Patterns

- Feature-card grids that could belong to any SaaS product.
- Rasterized screenshots containing important text.
- Copied brand marks, pseudo-logos, or reference layouts.
- Diagrams where arrows do not encode real relationships.
- Decorative image treatment that hides the commercial argument.
- Slide titles that label a topic instead of making a claim.
