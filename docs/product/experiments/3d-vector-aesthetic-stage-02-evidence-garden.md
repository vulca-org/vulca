# 3D Vector Aesthetic Stage 02 - Evidence Garden Direction

## Status

Selected working direction for Stage 02. This is still pre-implementation: generate or source the central 3D object before rebuilding the final page.

## Direction

Evidence Garden is now anchored on the Glass Root Specimen branch: a transparent technical specimen with a compact dark mineral garden core, internal glass roots, cyan signal veins, and tiny amber buds. It should feel like a quiet museum object, not fantasy terrain, dashboard UI, product perfume bottle, or text poster.

The direction is selected because it solves the current visual problem:

- It gives the page a memorable central subject.
- It is not text-led.
- It can support four page states without becoming a click demo.
- It keeps the 2025+ technical aesthetic through routes, scan planes, particles, and material polish.
- It can be produced by a 3D generation tool and then refined in a web runtime.

## Visual Structure

Central object:

- asymmetrical floating island, approximately oval from a three-quarter camera angle;
- dark graphite or basalt-like mineral base;
- translucent roots visible under and inside the island;
- thin cyan route veins crossing the top surface and descending into roots;
- three to five data blossoms, small and warm, not decorative flowers;
- no text, no logo, no character, no mascot.

Scene support:

- restrained dark background with negative space;
- one slow scan ring or scan sheet;
- sparse constellation particles only in the final state;
- no HUD panels, counters, fake dashboard labels, or explanatory typography as the main visual.

Palette:

```text
background: #050706
mineral_base: #1b241f
glass_root: #d8f4ee with low alpha
route_cyan: #6dd9cf
data_blossom: #d8955d
botanical_moss: #8da66f
warm_ink: #f1ead7
```

## Four Page States

1. Dormant Island
   - Object sits still in the center.
   - Roots are visible but dim.
   - Surface veins are barely lit.
   - Goal: first-frame beauty and silhouette.

2. Root Scan
   - A cyan scan plane passes through the island and root system.
   - Roots become legible.
   - Camera can move slightly lower, showing depth under the island.
   - Goal: explain structure without text.

3. Data Bloom
   - Route veins brighten.
   - Data blossoms lift or open slightly.
   - Warm amber becomes active but does not dominate.
   - Goal: give the piece emotional payoff without becoming cute.

4. Archive Constellation
   - Small particles and shards rise from blossoms.
   - The island connects to a sparse constellation field.
   - Camera pulls back a little.
   - Goal: end as technical memory/archive, not garden fantasy.

## Asset Generation Strategy

Generate the central object as GLB/glTF first. Do not generate the full web scene as an image or video. The web runtime should add scan rings, route highlights, particles, camera movement, and state transitions.

Preferred tool order:

1. Spline AI for fast visual ideation and rough object variants.
2. Tripo or Meshy for downloadable GLB candidates.
3. Blender cleanup if a generated model has the right silhouette but weak scale, materials, or topology.
4. `<model-viewer>` smoke test for first-frame review.
5. Three.js or React Three Fiber only after one GLB candidate passes visual gates.

## Prompt Strategy

Use `docs/product/experiments/3d-vector-aesthetic-stage-02-evidence-garden-prompts.json` as the working prompt pack.

Prompt rules:

- Always ask for a single centered 3D asset.
- Keep the subject as a specimen or object, not an environment.
- Use material words: mineral, graphite, translucent glass, ceramic, luminous veins.
- Avoid generic fantasy wording.
- Explicitly ban text, logos, characters, mascots, UI labels, and brand marks.
- Ask for GLB export where the tool supports it.

## Web Runtime Strategy

The first page should not depend on heavyweight app scaffolding.

Suggested sequence:

1. `stage-02-evidence-garden-model-smoke`
   - static page using `<model-viewer>`;
   - shows the GLB centered on a dark background;
   - includes a simple scoring panel and screenshot/video gate.
2. `stage-02-evidence-garden-scroll-prototype`
   - Three.js or R3F page;
   - one GLB, four scroll states, timeline-driven camera and shader overlays;
   - no final narration or MP4 until visual first frame is accepted.
3. `stage-02-evidence-garden-final`
   - polished visual page and optional horizontal capture pipeline.

## Acceptance Gates

Before final implementation:

- First frame reads as a central object in under one second.
- Silhouette remains recognizable at 1920x1080 and mobile crop.
- Object looks like a technical specimen, not a fantasy island or product bottle.
- The page can show four states without adding text as the main visual.
- GLB is small enough after optimization for local browser review.
- The model has no text, logos, brand marks, characters, or mascot elements.
- The route/scan/particle layers support the object instead of replacing it.

## Open Questions

- Should the first generated asset lean more botanical specimen or more glass archive object?
- Should the final motion be scroll-driven, page-button-driven, or both?
- Which tool will supply the first GLB: Spline, Tripo, Meshy, or manual Blender blockout?

## Current Recommendation

Use Evidence Garden as the Stage 02 working direction, and use Glass Root Specimen as the primary model candidate.

Generate candidates in this order:

1. glass root specimen: transparent vessel, compact mineral core, contained roots, tiny amber signal buds;
2. mineral root island: fallback if glass material fails or turns into a bottle;
3. technical data island: fallback if the branch needs to read more engineered and less botanical.

Pick the best silhouette first, but reject immediately if the glass form becomes a medicine vial, perfume bottle, terrarium, or generic product container. Materials and scan overlays can be repaired later, but weak shape logic will not recover.
