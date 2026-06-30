# 3D Vector Aesthetic Stage 02 - Central Object Reference Discovery

## Status

Discovery for user review. Do not implement yet.

The previous Stage 02 direction pushed too quickly into a text-poster canvas. The new target is a central visual element in the middle of the web page: one object, world, or device that changes through page or scroll states. Code is the final delivery layer, not the source of taste.

## What Changed

Stage 02 should stop asking "what canvas effect can we code?" and start asking "what is the subject?"

The subject should satisfy these gates:

- First frame works as a beautiful still image.
- The main element is not text.
- The element can hold 3 to 5 page or scroll states.
- Motion feels like state change, not cursor demo.
- The model or geometry can be sourced, generated, cleaned, and rendered as GLB/glTF.
- The result still belongs to 2025+ browser-native 3D/vector technical aesthetics.

## Reference Criteria

Use these fields when adding new cases to the learning DB:

```text
central_subject: micro_world | technical_device | living_system | spatial_sculpture | product_exploded_view
first_frame_strength: 0-3
scroll_state_count: integer
state_change_mechanism: grow | explode | assemble | scan | orbit | reveal | transform
asset_source: generated | modeled | procedural | reference_only | mixed
web_runtime_fit: model_viewer | three | r3f | spline_embed | webgpu
xhs_first_glance_fit: 0-3
do_not_copy: short rights and originality note
```

This should become a sparse module named `central_scroll_object` if we update the schema later.

## Best Reference Shortlist

### 1. Micro world or data garden

Primary direction to explore first.

External references:

- Codrops, "More Than a Portfolio: Building a Scroll-Driven 3D World with Something to Say"
  - URL: https://tympanus.net/codrops/2026/04/28/more-than-a-portfolio-building-a-scroll-driven-3d-world-with-something-to-say/
  - Why: clear proof that a page can behave like a composed 3D place, not a stack of sections.
  - Borrow: scroll-state world framing, camera path, scene polish, Blender to Three.js pipeline.
  - Do not copy: portfolio identity, religious/personal messaging, scene models.
- Weleda, The Open Garden
  - URL: https://www.awwwards.com/sites/weleda-the-open-garden
  - Studio case: https://www.makemepulse.com/case-study/weleda-the-open-garden
  - Why: the content itself is a garden, which is stronger than generic particles.
  - Borrow: meditative exploration, botanical subject matter, curated nature details.
  - Do not copy: Weleda brand language, plant assets, 360 environment specifics.

Existing DB anchors:

- `false-earth-webgpu-world`
- `matrix-sentinels-particle-trails-tsl`
- `phantom-land-interactive-grid`

Candidate VULCA subject:

```text
A floating evidence garden:
small terrain island, glass roots, luminous route veins, 3 to 5 data blossoms.
Scroll states: dormant -> scan -> bloom -> split layers -> archive constellation.
```

Why it is probably the best route:

- It gives us content, not just effect.
- It can use generated 3D assets but still be enhanced by procedural lines and particles.
- It supports future lessons: model generation, shader material, scroll timeline, particle field, and video capture.

Main risk:

- It can become fantasy/cute if the asset prompt is weak. Keep it mineral, botanical, precise, and technical.

### 2. Exploded technical object

External references:

- iyO, Interactive WebGL Exploded View
  - URL: https://www.awwwards.com/inspiration/interactive-webgl-exploded-view-iyo
  - Site listing: https://www.awwwards.com/sites/iyo
  - Why: a central object can carry scroll animation through exploded view, product exploration, and detail states.
  - Borrow: scroll-driven separation, component hierarchy, high-fidelity material read.
  - Do not copy: hardware form, product narrative, commercial configurator details.

Existing DB anchors:

- `spline-contemporary-3d-web`
- `webgpu-scanning-depth-maps`

Candidate VULCA subject:

```text
An evidence instrument:
a small orb/capsule device made of glass, metal, route-lines, and layered plates.
Scroll states: closed -> scan ring -> exploded layers -> annotated force field -> reassembled artifact.
```

Why it is useful:

- More technical and less whimsical than the garden route.
- Strong fit for 3D model generation and GLB cleanup.

Main risk:

- It may look like generic sci-fi product advertising if the form language is not distinctive.

### 3. Scroll navigation with 3D models

External references:

- Awwwards, Scroll Navigation with Animated 3D Models
  - URL: https://www.awwwards.com/inspiration/scroll-navigation-with-animated-3d-models
- Awwwards, 3D environment WebGL scroll navigation
  - URL: https://www.awwwards.com/inspiration/3d-environment-webgl-scroll-navigation
- Awwwards, Scroll Triggered Navigation With Animated 3D Models
  - URL: https://www.awwwards.com/inspiration/scroll-triggered-navigation-with-animated-3d-models

Borrow:

- Treat scroll as a state machine.
- Keep one persistent 3D subject while the page flips through moments.
- Use the camera and object transform as the primary transition.

Do not copy:

- Generic scroll-navigation UX, project-card layout, navigation chrome.

Candidate VULCA subject:

```text
One central artifact, four chapters.
The chapter content can stay outside the main object, but the object must visually change per chapter.
```

Main risk:

- This can become interaction design instead of visual content. Use it as motion grammar only.

### 4. Spatial sculpture and force field

External references:

- Awwwards WebGL collection
  - URL: https://www.awwwards.com/awwwards/collections/webgl/
- Codrops 3D tag
  - URL: https://tympanus.net/codrops/tag/3d/

Existing DB anchors:

- `makio-meshline`
- `codrops-threejs-meshline-family`
- `phantom-land-interactive-grid`

Candidate VULCA subject:

```text
A line-field sculpture:
one core object surrounded by route trails, scan sheets, and particles.
```

Why it is useful:

- Keeps the vector identity from Stage 01.

Main risk:

- This is closest to the old failure mode: pretty tech without a memorable subject.

## Asset And Tool Stack To Test

### Fast visual ideation

- Spline AI 3D Generation
  - URL: https://docs.spline.design/spline-ai/ai-3d-generation
  - Fit: quick text-to-3D and image-to-3D ideation inside a design tool.
  - Useful constraint from docs: focus on a single object; organic shapes usually work better than high-precision hard edges.
  - Use for: fast subject tests, not final technical lock-in.

### API asset generation

- Tripo API
  - URL: https://platform.tripo3d.ai/
  - Product page: https://www.tripo3d.ai/api
  - Fit: text/image/multiview to 3D, style generation, post-processing, export workflows.
  - Use for: batch generation of central object candidates.
- Meshy API
  - URL: https://www.meshy.ai/api
  - Image-to-3D docs: https://docs.meshy.ai/en/api/image-to-3d
  - Fit: text-to-3D, image-to-3D, remesh, AI texturing, rigging/animation, webhook support.
  - Use for: batch model attempts and GLB/FBX/OBJ output comparison.

### Local or open research track

- Hunyuan3D 2.x
  - URL: https://github.com/Tencent-Hunyuan/Hunyuan3D-2
  - Fit: open high-resolution textured asset generation research.
  - Use for: later local/open-source evaluation, not first visual spike.
- TRELLIS / TRELLIS.2
  - URL: https://github.com/microsoft/TRELLIS
  - Project: https://microsoft.github.io/TRELLIS.2/
  - Fit: image-to-3D research with mesh and richer 3D representations.
  - Use for: later comparison if hosted tools fail aesthetic gates.

### Web runtime and cleanup

- `<model-viewer>`
  - URL: https://modelviewer.dev/docs/
  - Fit: fastest smoke test for a single GLB in the center of a page.
  - Use for: first-pass visual review before building a Three.js system.
- React Three Fiber
  - URL: https://r3f.docs.pmnd.rs/getting-started/introduction
  - Fit: reusable stateful Three.js components.
  - Use for: final prototype if we need componentized scroll states.
- Three.js GLTF workflow
  - URL: https://threejs.org/docs/#manual/en/introduction/Loading-3D-models
  - Fit: direct GLB/glTF loading and custom shader control.
  - Use for: final creative-code control.
- GSAP ScrollTrigger
  - URL: https://gsap.com/docs/v3/Plugins/ScrollTrigger/
  - Fit: scroll progress as a stable timeline driver.
  - Use for: page-state animation, camera movement, model transforms, shader uniforms.
- glTF Transform
  - URL: https://gltf-transform.dev/cli
  - Fit: reproducible GLB inspection, Draco compression, WebP texture compression.
  - Use for: model optimization before web review.
- Blender glTF export
  - URL: https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html
  - Fit: manual cleanup, scale normalization, material and animation export.
  - Use for: final asset cleanup if generated output is promising.

## Recommended Spike

Do this before any new Stage 02 implementation:

1. Build a reference shortlist of 8 cases under the `central_scroll_object` lens.
2. Generate or source 6 central-object candidates:
   - 3 micro-world/data-garden prompts.
   - 3 exploded technical-device prompts.
3. Run the candidates through a smoke-test page:
   - first pass can use `<model-viewer>`;
   - second pass can use Three.js or R3F with a 4-state scroll timeline.
4. Score each candidate:
   - first-frame beauty;
   - silhouette strength;
   - material quality;
   - scroll-state potential;
   - web weight after optimization;
   - originality and rights safety.
5. Only then choose the final Stage 02 direction.

## Proposed Stage 02 Decision

Recommended path for now:

```text
D plus iyO mechanics:
Micro-world subject, exploded/scan state grammar.
```

This means:

- The content is a small evidence garden or data island.
- The motion borrows exploded-view clarity rather than random particles.
- The vector/technical identity comes from route veins, scan planes, and particle fields.
- 3D model generation is used to create the central subject, not to generate the whole page.

Definition of ready for implementation:

- At least one central subject looks good as a still.
- The subject has a recognizable silhouette at 1920x1080 and mobile crop.
- The subject can support 4 states without adding text as the main visual.
- The GLB can be optimized under a practical web budget.
- The reference notes identify what to borrow and what not to copy.
