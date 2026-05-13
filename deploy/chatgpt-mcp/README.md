# ChatGPT Remote MCP Deploy

This package builds the review-safe Vulca ChatGPT App MCP profile for a direct
public HTTPS deployment on Google Cloud Run. The image installs the published
PyPI package, pinned to `vulca[mcp]==0.23.1`.

The container runs `vulca-mcp-remote`, not the full local `vulca-mcp` server.
The exposed profile is restricted to:

- `list_traditions`
- `get_tradition_guide`
- `search_traditions`
- `compose_prompt_from_design`
- `evaluate_artwork`

The submitted profile is read-only, non-destructive, and not open-world. It does
not expose image generation, image upload, pixel reading, redraw, inpaint,
archive, sync, admin, or filesystem-writing tools.

## Local Build

Run from the repository root:

```bash
docker build -f deploy/chatgpt-mcp/Dockerfile -t vulca-chatgpt-mcp .
docker run --rm -p 8765:8765 \
  -e VULCA_REMOTE_MCP_PORT=8765 \
  -e VULCA_REMOTE_WORKSPACE_ROOT=/app/workspace \
  vulca-chatgpt-mcp
```

The MCP endpoint is:

```text
http://127.0.0.1:8765/mcp
```

Use this only for local validation. The submitted ChatGPT App should use the
direct Cloud Run service URL plus `/mcp`, for example
`https://vulca-chatgpt-mcp-<hash>.run.app/mcp`.

Do not depend on `https://vulcaart.art/mcp` for this resubmission. The website
is currently served by Firebase Hosting as a static SPA, and `/mcp` falls back
to the frontend unless Firebase Hosting is explicitly rewired to Cloud Run.

## Cloud Run

Set these values for Cloud Run:

```text
VULCA_REMOTE_MCP_TRANSPORT=streamable-http
VULCA_REMOTE_MCP_HOST=0.0.0.0
VULCA_REMOTE_MCP_PATH=/mcp
VULCA_REMOTE_WORKSPACE_ROOT=/app/workspace
```

Cloud Run provides `PORT`; the container maps it to
`VULCA_REMOTE_MCP_PORT`.

Example deploy shape:

```bash
PROJECT_ID=<gcp-project>
REGION=asia-east1
SERVICE_NAME=vulca-chatgpt-mcp
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:$(git rev-parse --short HEAD)"

gcloud builds submit \
  --config deploy/chatgpt-mcp/cloudbuild.yaml \
  --substitutions _IMAGE="$IMAGE" \
  .

gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 20 \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars "VULCA_REMOTE_MCP_TRANSPORT=streamable-http,VULCA_REMOTE_MCP_HOST=0.0.0.0,VULCA_REMOTE_MCP_PATH=/mcp,VULCA_REMOTE_WORKSPACE_ROOT=/app/workspace"
```

After deploy, use the Cloud Run service URL plus `/mcp` as the OpenAI Platform
MCP server URL.

Optional: set `VULCA_VERSION` at build time only after the new package has been
published and locally preflighted:

```bash
gcloud builds submit \
  --config deploy/chatgpt-mcp/cloudbuild.yaml \
  --substitutions _IMAGE="$IMAGE",_VULCA_VERSION=0.23.1 \
  .
```

## Preflight

Before submitting, run:

```bash
PYTHONPATH=src python scripts/chatgpt_app_preflight.py \
  --submission chatgpt-app-submission.json \
  --privacy-url https://vulcaart.art/chatgpt-app-privacy \
  --mcp-url https://<cloud-run-service-url>/mcp
```

Then capture fresh screenshots from the actual ChatGPT app experience, using
the production HTTPS MCP endpoint.
