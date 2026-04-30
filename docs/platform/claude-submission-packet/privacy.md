# Claude Submission Privacy Notes

Vulca is local-first by default. It reads local project files and image paths when the user asks it to inspect, decompose, or evaluate local artifacts.

Provider-backed actions can send prompts, images, masks, or metadata to the configured provider. These actions must remain explicit opt-in and should show provider/model/cost metadata when available.

The first public submission should not enable remote upload, generation, redraw, inpaint, or VLM evaluation without user approval.
