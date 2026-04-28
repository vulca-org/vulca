# IMG_6847 Direct iPad-Cartoon Showcase - Execution Log

Date: 2026-04-28

## Objective

Run one Scottish-style direct showcase attempt for the iPad roadside image: structured prompt planning first, then direct whole-image generation/edit. Do not use `decompose`, `layers_redraw`, or sparse-alpha compositing.

## Inputs

- Source: `source/IMG_6847.jpg`
- Proposal: `proposal.md`
- Design: `design.md`
- Plan: `plan.md`

## Superpowers Notes

- Used Superpowers process discipline requested by the user.
- `verification-before-completion` applies: do not claim the run completed until generated image files and metadata are checked.
- Existing v0.20.1 layered artifacts are intentionally preserved and not overwritten.

## Run Events

- Created direct-showcase artifact directory.
- Copied source image byte-for-byte from the prior iPad roadside slug.
- Prepared direct-edit execution path using a 1536x1024 reference PNG and full transparent edit mask.
- First sandboxed network attempt failed before reaching OpenAI due DNS/network restriction.
- Escalated network attempt was initially blocked by policy review because it would upload the local reference image to OpenAI.
- User explicitly approved the reference-image upload.
- Approved OpenAI edit attempt ran against `gpt-image-2`, then fallback `gpt-image-1.5`.
- Both provider calls returned HTTP 400.
- Follow-up response-body probe showed the real upstream reason: `Billing hard limit has been reached.` (`type: billing_limit_user_error`, `code: billing_hard_limit_reached`).
- Added A/B comparison plan: naive prompt vs Vulca structured prompt, same reference image, same full-edit mask, same provider/model contract.

## Result

blocked_billing_hard_limit_reached

## Next Unblocked Action

After OpenAI billing hard limit is raised or reset, run:

```bash
set -a; . /Users/yhryzy/dev/vulca/.env.local; set +a; python3 docs/visual-specs/2026-04-28-ipad-cartoon-roadside-direct-showcase/run_ab_experiment.py
```

Expected success writes:

- `iters/ab/naive_gpt_image_2.png`
- `iters/ab/vulca_structured_gpt_image_2.png`
- `iters/ab/results.json`
