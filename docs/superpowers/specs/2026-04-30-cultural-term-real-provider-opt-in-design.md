# Cultural-Term Real Provider Opt-In Design

## Status

approved_for_planning

## Context

The cultural-term efficacy harness now writes dry-run artifacts for A/B/C/D prompt conditions without provider execution. The next step is to allow a real provider run, but only when explicitly requested and only through local environment variables. The user has a NewAPI-style OpenAI-compatible gateway available. That credential is a secret and must never be written into this repository, generated artifacts, logs, PR bodies, or documentation.

Existing code facts:

- `scripts/visual_discovery_benchmark.py` already defines project fixtures, A/B/C/D conditions, dry-run result directories, `manifest.json`, `provider_costs.json`, and fail-closed `run_real_provider_experiment()`.
- `OpenAIImageProvider` can generate images with OpenAI image endpoints but currently hardcodes `https://api.openai.com/v1/images/...` and only reads `OPENAI_API_KEY`.
- `ImageResult` already carries `image_b64`, `mime`, and `metadata`, including provider-side cost/usage when available.
- The harness currently marks all providers as `not_run`.

## Goal

Add a real-provider opt-in path for the cultural-term efficacy harness that can run A/B/C/D prompt conditions through an OpenAI-compatible image endpoint, save output images, record provider metadata/costs, and still fail closed unless the caller explicitly enables provider execution.

## Non-Goals

- Do not store, echo, commit, log, or document any real API key.
- Do not add real Gemini or ComfyUI execution in this branch.
- Do not run `/evaluate` automatically; evaluation requires generated image artifacts first and will be a follow-up.
- Do not implement human ranking UI or scoring aggregation.
- Do not run real providers in tests or CI.
- Do not change v0.22 redraw, masks, layers, `/inpaint`, or `/redraw-layer`.

## Recommended Approach

Use the existing `OpenAIImageProvider`, but make its endpoint configurable:

- Add `base_url` to `OpenAIImageProvider.__init__`.
- Resolve it from `VULCA_OPENAI_BASE_URL`, then `OPENAI_BASE_URL`, then default to `https://api.openai.com`.
- Keep URL construction internal and normalize trailing `/v1`.
- Continue using `OPENAI_API_KEY` as the standard provider key path.

For the experiment harness, add a narrow real-provider path:

- CLI requires `--real-provider`.
- CLI requires `--provider openai`; any other provider fails with a clear unsupported-provider error.
- CLI requires credentials from environment:
  - `VULCA_REAL_PROVIDER_API_KEY`, falling back to `OPENAI_API_KEY`
  - `VULCA_REAL_PROVIDER_BASE_URL`, falling back to `VULCA_OPENAI_BASE_URL`, then `OPENAI_BASE_URL`
  - `VULCA_REAL_PROVIDER_MODEL`, defaulting to `gpt-image-2`
- The harness passes `api_key`, `base_url`, and `model` into `OpenAIImageProvider`.
- The harness writes image files and metadata but never writes the API key or authorization header.

This keeps the provider-specific change small and useful outside the experiment, while keeping the experiment path explicit and auditable.

## CLI Shape

Dry run remains unchanged:

```bash
PYTHONPATH=src python3 scripts/visual_discovery_benchmark.py --date 2026-04-30
```

Real provider run:

```bash
VULCA_REAL_PROVIDER_BASE_URL=https://example.openai-compatible-gateway.test \
VULCA_REAL_PROVIDER_API_KEY=... \
VULCA_REAL_PROVIDER_MODEL=gpt-image-2 \
PYTHONPATH=src python3 scripts/visual_discovery_benchmark.py \
  --real-provider \
  --provider openai \
  --slug premium-tea-packaging \
  --output-root /private/tmp/vulca-cultural-term-real-provider \
  --date 2026-04-30
```

The example intentionally uses a placeholder host and `...` for the key. Real credentials stay outside files.

## Artifact Contract

For a real run, the output directory remains:

```text
docs/product/experiments/results/<date>-<slug>/
  prompts/
    A.txt
    B.txt
    C.txt
    D.txt
  images/
    A.png
    B.png
    C.png
    D.png
    metadata.json
  evaluations/
    README.md
  human_ranking.json
  provider_costs.json
  summary.md
  manifest.json
```

`manifest.json` changes from:

```json
{
  "mode": "dry_run",
  "provider_execution": "disabled"
}
```

to:

```json
{
  "mode": "real_provider",
  "provider_execution": "enabled",
  "real_provider": {
    "provider": "openai",
    "model": "gpt-image-2",
    "base_url": "https://example.openai-compatible-gateway.test"
  }
}
```

`images/metadata.json` contains per-condition records:

```json
{
  "schema_version": "0.1",
  "provider": "openai",
  "model": "gpt-image-2",
  "conditions": [
    {
      "id": "A",
      "image_path": "images/A.png",
      "mime": "image/png",
      "metadata": {
        "endpoint": "generations",
        "cost_usd": 0.0
      }
    }
  ]
}
```

`provider_costs.json` changes from `"status": "not_collected"` to `"status": "collected"` when at least one generated result includes cost metadata. If no cost metadata is returned, it records `"status": "unavailable"` and does not invent costs.

## Safety Rules

- The API key must never appear in any artifact.
- The base URL may appear in metadata because it identifies the provider route, but it must be sanitized to remove path/query fragments and must not include credentials.
- Real provider execution must not happen unless `--real-provider` is present.
- Real provider execution must fail before any network call if the API key is missing.
- `mock` remains invalid for quality conclusions.
- Tests use mocked provider calls only.

## Error Handling

- Missing key: raise `RuntimeError` explaining which env vars are accepted.
- Unsupported provider: raise `ValueError` listing supported real providers.
- Provider failure after partial output: write whatever successful condition artifacts exist, then raise; do not write a success summary.
- Base URL normalization: accept `https://host`, `https://host/`, or `https://host/v1`; avoid `.../v1/v1`.

## Testing

- Provider tests verify `OpenAIImageProvider` sends requests to a custom base URL and never requires a real key in tests.
- Harness tests use a fake async provider function or monkeypatched `OpenAIImageProvider` to simulate generated b64 PNGs and metadata.
- Harness tests verify images, manifest, provider costs, and metadata are written.
- Harness tests verify missing credentials fail before provider construction.
- Docs truth tests verify real-provider examples use placeholders and do not contain credential-looking strings.

## Follow-Ups

- Add `/evaluate` batch scoring over generated real-provider images.
- Add Gemini and ComfyUI real-provider adapters once the OpenAI-compatible route is stable.
- Add human ranking collection and summary aggregation after the first real image batch exists.
