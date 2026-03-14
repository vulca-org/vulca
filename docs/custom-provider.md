# Adding a Custom Image Provider

This guide explains how to add a new image generation provider to the VULCA Canvas pipeline (e.g., ComfyUI, Midjourney, Stability AI, etc.).

## Overview

The provider system uses an abstract base class (`AbstractProvider`) with a simple contract: take a prompt and parameters, write an image file to disk, return the path. All providers are resolved by name through a factory function.

## Step 1: Create the Provider Class

Create a new file in `wenxin-backend/app/prototype/agents/` (e.g., `myapi_provider.py`):

```python
"""Custom provider via MyAPI."""

import os
import logging
import httpx
from pathlib import Path

from app.prototype.agents.draft_provider import AbstractProvider

logger = logging.getLogger(__name__)


class MyAPIProvider(AbstractProvider):
    """Generate images via MyAPI."""

    def __init__(self, api_key: str = "", endpoint: str = ""):
        self.api_key = api_key or os.environ.get("MYAPI_KEY", "")
        if not self.api_key:
            raise ValueError("MYAPI_KEY required for MyAPI provider")
        self.endpoint = endpoint or "https://api.myservice.com/v1/generate"

    @property
    def model_ref(self) -> str:
        """Human-readable model identifier shown in UI and logs."""
        return "myapi-v1"

    def generate(
        self,
        prompt: str,
        negative_prompt: str,
        seed: int,
        width: int,
        height: int,
        steps: int,
        sampler: str,
        output_path: str,
    ) -> str:
        """Generate an image and save it to output_path.

        Parameters
        ----------
        prompt : str
            The positive generation prompt (already enriched by Scout).
        negative_prompt : str
            Things to avoid in generation.
        seed : int
            Deterministic seed for reproducibility.
        width, height : int
            Target image dimensions (may need mapping to API-supported sizes).
        steps : int
            Number of inference steps.
        sampler : str
            Sampler name (e.g., "euler_a") — ignore if your API doesn't support it.
        output_path : str
            Where to write the output image file.

        Returns
        -------
        str
            The actual path where the image was written (may differ from output_path
            if the extension changed, e.g., .webp instead of .png).
        """
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height,
                    "steps": steps,
                    "seed": seed,
                },
            )
            resp.raise_for_status()

        # Write the image bytes to disk
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(resp.content)
        return str(out)
```

### Key requirements

- Subclass `AbstractProvider` from `app.prototype.agents.draft_provider`.
- Implement `generate()` with exactly the 8 parameters shown above.
- Implement the `model_ref` property (used in UI, logs, and checkpoints).
- Write the image to `output_path` and return the actual path.
- Handle errors by raising exceptions (the pipeline's `FallbackProvider` catches `TimeoutError`, `ConnectionError`, and `OSError` for retry logic).

## Step 2: Register in the Factory

Edit `wenxin-backend/app/prototype/agents/draft_agent.py` and add a new case to `_get_provider()`:

```python
def _get_provider(name: str, config: DraftConfig | None = None) -> AbstractProvider:
    # ... existing cases ...

    if name == "myapi":
        from app.prototype.agents.myapi_provider import MyAPIProvider
        key = (
            (config.api_key if config else "")
            or os.environ.get("MYAPI_KEY", "")
        )
        return MyAPIProvider(api_key=key)

    raise ValueError(f"Unknown provider: {name!r} (available: ...add myapi...)")
```

The lazy import ensures the provider module is only loaded when actually selected.

## Step 3: Add to the /capabilities Endpoint

Edit `wenxin-backend/app/prototype/api/routes.py` and add your provider to the `providers` list in `get_capabilities()`:

```python
providers = [
    # ... existing providers ...
    {"id": "myapi", "label": "MyAPI", "cost": 0.05, "available": bool(os.environ.get("MYAPI_KEY"))},
]
```

The frontend `ProviderQuickSwitch` component automatically fetches this list and shows only providers where `available` is `True`.

## Step 4: Set Environment Variables

Add your API key to the environment:

```bash
# Local development (.env file or shell)
export MYAPI_KEY="sk-your-api-key-here"

# Production (GCP Secret Manager)
gcloud secrets create MYAPI_KEY --data-file=-
```

For Cloud Run deployment, update `.github/workflows/deploy-gcp.yml` to inject the secret.

## Step 5: Test

### Verify Python syntax

```bash
python -c "import ast; ast.parse(open('wenxin-backend/app/prototype/agents/myapi_provider.py').read())"
```

### Verify the provider loads

```bash
cd wenxin-backend
python -c "
import os
os.environ['MYAPI_KEY'] = 'test-key'
from app.prototype.agents.myapi_provider import MyAPIProvider
p = MyAPIProvider(api_key='test-key')
print(f'Provider loaded: {p.model_ref}')
"
```

### Run via the pipeline

```bash
cd wenxin-backend
python -m uvicorn app.main:app --reload --port 8001

# In another terminal:
curl -X POST http://localhost:8001/api/v1/prototype/runs \
  -H "Content-Type: application/json" \
  -d '{"subject": "mountain landscape", "tradition": "chinese_xieyi", "provider": "myapi"}'
```

## Advanced: Fallback Chains

You can use `FallbackProvider` to create automatic failover:

```python
from app.prototype.agents.draft_provider import FallbackProvider, MockProvider
from app.prototype.agents.myapi_provider import MyAPIProvider

chain = FallbackProvider(
    providers=[
        MyAPIProvider(api_key="..."),
        MockProvider(),  # fallback if MyAPI fails
    ],
    max_retries_per_provider=2,
    backoff_base_ms=1000,
)
```

## Advanced: Local ComfyUI

For a local ComfyUI instance, the provider would POST a workflow JSON to `http://localhost:8188/prompt` and poll for results:

```python
class ComfyUIProvider(AbstractProvider):
    def __init__(self, endpoint: str = "http://localhost:8188"):
        self.endpoint = endpoint

    @property
    def model_ref(self) -> str:
        return "comfyui-local"

    def generate(self, prompt, negative_prompt, seed, width, height, steps, sampler, output_path) -> str:
        workflow = _build_workflow(prompt, negative_prompt, seed, width, height, steps)
        with httpx.Client(timeout=300) as client:
            resp = client.post(f"{self.endpoint}/prompt", json={"prompt": workflow})
            resp.raise_for_status()
            prompt_id = resp.json()["prompt_id"]

            # Poll for completion
            while True:
                history = client.get(f"{self.endpoint}/history/{prompt_id}").json()
                if prompt_id in history:
                    outputs = history[prompt_id]["outputs"]
                    # Download the output image
                    image_info = outputs["9"]["images"][0]  # node 9 = SaveImage
                    img_resp = client.get(
                        f"{self.endpoint}/view",
                        params={"filename": image_info["filename"], "subfolder": image_info.get("subfolder", "")},
                    )
                    out = Path(output_path)
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(img_resp.content)
                    return str(out)
                import time
                time.sleep(1)
```

## File Reference

| File | Purpose |
|------|---------|
| `wenxin-backend/app/prototype/agents/draft_provider.py` | `AbstractProvider` base class |
| `wenxin-backend/app/prototype/agents/replicate_provider.py` | FLUX.2 Pro / FLUX Schnell provider |
| `wenxin-backend/app/prototype/agents/draft_agent.py` | `_get_provider()` factory |
| `wenxin-backend/app/prototype/api/routes.py` | `/capabilities` endpoint |
| `wenxin-moyun/src/components/prototype/ProviderQuickSwitch.tsx` | Frontend provider selector |
