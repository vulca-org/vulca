# ChatGPT Prompt Studio Design

Date: 2026-05-31
Status: user-review

## Purpose

The ChatGPT App should make image creation feel direct without adding provider
cost, privacy review surface, or artifact ownership to the submitted remote
profile. The selected route is a Prompt Studio: Vulca prepares a high-quality
generation brief, final prompt, negative constraints, and evaluation rubric, then
hands the user back to ChatGPT's native image generation flow.

This design keeps Vulca as the creative director inside ChatGPT. It does not
turn the submitted app into an image provider.

## Product Decision

Build the A route from the visual companion:

- Use ChatGPT native image generation for the actual image.
- Use Vulca for tradition selection, prompt composition, rubric framing, and
  review guidance.
- Add a lightweight app UI that reduces the interaction from several tool calls
  to one visual prompt handoff.
- Keep provider-backed `generate_image`, inpaint, redraw, and artifact archive
  outside the public ChatGPT App profile for now.

The B route remains a later full-provider profile for workflows that require
Vulca to own generated image files and run automatic edit/evaluate/archive loops.

## Non-Goals

- Do not expose `generate_image` in the current ChatGPT remote-safe profile.
- Do not call OpenAI Image API, Responses API image generation, Gemini, ComfyUI,
  or any other provider from the submitted ChatGPT App.
- Do not promise that ChatGPT will return the generated image artifact to Vulca.
- Do not add upload, inpaint, redraw, layer editing, publishing, or archive
  actions in this first Prompt Studio pass.
- Do not change the currently submitted production MCP endpoint until review
  risk is acceptable.

## User Flow

1. User asks Vulca for an artwork, poster, character, scene, or visual concept.
2. ChatGPT calls Vulca's safe tools to select or inspect traditions and compose
   an image-generation prompt.
3. ChatGPT opens the Prompt Studio widget.
4. The widget displays:
   - selected tradition and short rationale,
   - final image prompt,
   - negative constraints,
   - optional size/style notes,
   - L1-L5 rubric points for judging the result.
5. User can copy the prompt or press `Generate in ChatGPT`.
6. The widget sends a follow-up message asking ChatGPT to generate the image
   using the prepared prompt.
7. ChatGPT handles native image generation outside Vulca.

## Architecture

Keep the existing remote-safe data tools and add one render-oriented tool in the
next app iteration:

| Unit | Responsibility |
| --- | --- |
| `compose_prompt_from_design` | Existing data tool that turns an approved design file into prompt material. |
| `open_prompt_studio` | New render tool that packages prompt material for the widget and returns the UI template metadata. |
| Prompt Studio widget | Static HTML/CSS/JS resource that shows the prompt package and calls the ChatGPT Apps bridge for follow-up messaging. |
| Remote profile policy | Keeps all provider and artifact tools denied. Marks the render tool read-only, idempotent, non-destructive, and closed-world. |

The app should use the decoupled Apps SDK pattern: data tools return reusable
structured content, and the render tool attaches the widget resource. This keeps
model-visible data separate from UI-only state.

## Tool Surface

The public ChatGPT profile remains prompt/rubric-first:

- `list_traditions`
- `search_traditions`
- `get_tradition_guide`
- `compose_prompt_from_design`
- `evaluate_artwork` in rubric-only mock mode
- `open_prompt_studio` as the only new render tool for the Prompt Studio UI

`open_prompt_studio` accepts structured prompt material rather than reading image
bytes or calling a provider. Its output includes:

- `prompt_title`
- `tradition`
- `final_prompt`
- `negative_prompt`
- `generation_notes`
- `rubric_summary`
- `followup_message`

The follow-up message is explicit model-facing text such as:

```text
Generate an image in ChatGPT using this Vulca prompt. Preserve the tradition,
composition, negative constraints, and rubric priorities exactly.

[final prompt and constraints]
```

## Widget Behavior

The widget should be compact and action-oriented:

- Show the final prompt in an editable text area.
- Show negative constraints and rubric as collapsible sections.
- Provide `Copy prompt` and `Generate in ChatGPT` actions.
- Use `window.openai.sendFollowUpMessage` when available.
- Fall back to copy-only behavior if the bridge is unavailable or the follow-up
  call is rejected.
- Store UI-only edits in widget state so the user can adjust wording before
  sending the follow-up.

The widget must not imply that Vulca generated the image or that Vulca can see
the generated result automatically.

## Privacy, Cost, And Review Boundary

Prompt Studio keeps the submitted app low risk:

- No Vulca-side image generation cost.
- No provider API keys required for the ChatGPT App.
- No generated image bytes sent to Vulca.
- No user image upload or pixel inspection in the first pass.
- Existing denied tools stay denied, especially `generate_image`,
  `create_artwork`, `inpaint_artwork`, `layers_redraw`, and `view_image`.

This is also why the first implementation should be developed behind a preview
profile or unreleased branch if the current submitted endpoint is still under
review.

## Error Handling

- If prompt material is missing, return a structured error that tells ChatGPT to
  call the relevant tradition and prompt composition tools first.
- If the widget bridge is unavailable, keep the prompt visible and enable copy.
- If `sendFollowUpMessage` fails, show a short inline failure state and keep the
  generated follow-up text copyable.
- If the user edits the prompt to an empty string, disable `Generate in ChatGPT`.
- If a denied provider action is requested, keep the existing remote policy
  response and steer back to Prompt Studio.

## Testing

Implementation should include focused tests before any code is accepted:

- Remote profile tests confirm `open_prompt_studio` is allowed and all provider
  tools remain denied.
- Tool handler tests confirm prompt packages include all required fields and no
  local filesystem paths leak into the public response.
- Widget tests or static checks confirm the bridge path, copy fallback, disabled
  empty-prompt state, and follow-up message format.
- ChatGPT preflight checks continue to pass with no forbidden provider keys or
  image-generation tools.
- Manual local app check verifies that pressing `Generate in ChatGPT` creates a
  follow-up message rather than invoking a Vulca provider.

## Rollout

1. Keep the submitted production MCP endpoint unchanged until the current review
   risk is clear.
2. Implement Prompt Studio in a preview branch/profile.
3. Validate with local ChatGPT App tooling and the existing preflight script.
4. Update submission copy only after the new UI is ready and the app still
   passes the prompt/rubric-only safety boundary.
5. Consider the B route later only if users need Vulca-owned artifacts,
   automatic evaluation, inpaint, redraw, or archive workflows.
