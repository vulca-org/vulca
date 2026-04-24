"""OpenAI DALL-E image generation provider."""
from __future__ import annotations

import base64
import io
import os

from vulca.providers.base import ImageProvider, ImageResult
from vulca.providers.retry import with_retry


class OpenAIImageProvider:
    """Image generation via OpenAI DALL-E 3 API."""

    capabilities: frozenset[str] = frozenset({"raw_rgba"})

    def __init__(self, api_key: str = "", model: str = "gpt-image-1"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model

    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        seed: int | None = None,
        steps: int | None = None,
        cfg_scale: float | None = None,
        width: int = 1024,
        height: int = 1024,
        background: str = "auto",
        input_fidelity: str | None = None,
        quality: str | None = None,
        output_format: str | None = None,
        **kwargs,
    ) -> ImageResult:
        # OpenAI image endpoints (DALL-E 3 / gpt-image-1 / gpt-image-2) do not
        # expose seed, sampler steps, or CFG — accept for signature symmetry
        # and ignore.
        _ = (seed, steps, cfg_scale)

        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var "
                "or pass api_key to OpenAIImageProvider()."
            )

        import httpx

        full_prompt = prompt
        if not kwargs.get("raw_prompt", False):
            if tradition and tradition != "default":
                full_prompt = f"{prompt} (cultural tradition: {tradition.replace('_', ' ')})"
        if negative_prompt:
            full_prompt = f"{full_prompt} (avoid: {negative_prompt})"

        # Accepted sizes: DALL-E 3 uses 1024x1024, 1024x1792, 1792x1024.
        # gpt-image-1 / gpt-image-2 additionally accept 1024x1536 (portrait)
        # and 1536x1024 (landscape). Union both sets for simplicity; any
        # unsupported combo still falls back to 1024x1024.
        allowed_sizes = {
            (1024, 1024),
            (1024, 1792),
            (1792, 1024),
            (1024, 1536),
            (1536, 1024),
        }
        size = f"{width}x{height}" if (width, height) in allowed_sizes else "1024x1024"

        def _is_retryable(exc: Exception) -> bool:
            # httpx.HTTPStatusError carries a response with status_code
            response = getattr(exc, "response", None)
            if response is not None:
                status = getattr(response, "status_code", None)
                if status in (429, 500, 503):
                    return True
                return False
            # Our enriched 429 RuntimeError (normalized for readability) keeps
            # the rate-limit marker so retry logic still kicks in. Terminal
            # RuntimeErrors (403/402/400) do not carry this marker.
            if isinstance(exc, RuntimeError) and "rate limit hit" in str(exc).lower():
                return True
            # Network-level errors (timeout, connect) are retryable
            if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError)):
                return True
            return False

        # Only gpt-image-* supports reference-based editing without a mask.
        # dall-e-2 /edits requires a mask + square PNG + returns URLs by default,
        # none of which this provider currently handles.
        use_edits = bool(reference_image_b64)
        if use_edits and not self.model.startswith("gpt-image"):
            raise ValueError(
                f"OpenAI img2img (reference_image_b64) requires a gpt-image-* "
                f"model; current model={self.model!r} is not supported on /edits."
            )

        # Capture for closure
        model = self.model

        async def _call() -> ImageResult:
            async with httpx.AsyncClient(timeout=120) as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                if use_edits:
                    ref_bytes = base64.b64decode(reference_image_b64)
                    files = {
                        "image": ("ref.png", io.BytesIO(ref_bytes), "image/png"),
                    }
                    form = {
                        "model": model,
                        "prompt": full_prompt,
                        "n": "1",
                        "size": size,
                    }
                    # gpt-image-2 additions. input_fidelity is edits-only per
                    # OpenAI 2026-04-21 launch docs; quality + output_format
                    # apply to both endpoints.
                    if input_fidelity is not None:
                        form["input_fidelity"] = input_fidelity
                    if quality is not None:
                        form["quality"] = quality
                    if output_format is not None:
                        form["output_format"] = output_format
                    resp = await client.post(
                        "https://api.openai.com/v1/images/edits",
                        headers=headers, files=files, data=form,
                    )
                else:
                    payload: dict = {
                        "model": model,
                        "prompt": full_prompt,
                        "n": 1,
                        "size": size,
                    }
                    if model.startswith("gpt-image"):
                        payload["background"] = background
                        # Caller-supplied output_format wins; default stays png
                        # for backward-compat with gpt-image-1 callers.
                        payload["output_format"] = (
                            output_format if output_format is not None else "png"
                        )
                        if quality is not None:
                            payload["quality"] = quality
                    else:
                        payload["response_format"] = "b64_json"
                    resp = await client.post(
                        "https://api.openai.com/v1/images/generations",
                        headers=headers, json=payload,
                    )
                # Classify common user-facing failure modes with actionable
                # remediation hints BEFORE raise_for_status / retry logic
                # sees them (codex 2026-04-23 audit). Only 429 is retryable
                # downstream; 402/400/403 are terminal from the user's POV.
                body_text = ""
                try:
                    body_text = (resp.text or "")[:500]
                except Exception:
                    body_text = ""
                body_lower = body_text.lower()

                # 403 Org-verification (gpt-image-2 launch gates API access)
                if resp.status_code == 403:
                    if "organization must be verified" in body_lower:
                        raise RuntimeError(
                            f"OpenAI model {model!r} requires Org verification at "
                            "https://platform.openai.com/settings/organization/general. "
                            "Wait 15 min after verifying."
                        )
                # 402 billing / insufficient credits
                elif resp.status_code == 402:
                    raise RuntimeError(
                        "OpenAI billing blocked: insufficient credits or "
                        "payment failure. Visit "
                        "https://platform.openai.com/settings/organization/billing "
                        "to fix."
                    )
                # 400 content-policy / safety violation
                elif resp.status_code == 400 and (
                    "content_policy_violation" in body_lower
                    or "safety" in body_lower
                ):
                    raise RuntimeError(
                        "OpenAI content policy blocked the request. "
                        "Revise the prompt or negative_prompt to reduce "
                        "policy-triggering terms."
                    )
                # 429 rate limit — enrich the message. `_is_retryable`
                # recognizes this RuntimeError marker ("rate limit hit") so
                # with_retry still backs off and retries.
                elif resp.status_code == 429:
                    raise RuntimeError(
                        "OpenAI rate limit hit. "
                        "Retry in ~60s or reduce concurrency."
                    )
                resp.raise_for_status()
                data = resp.json()

            img_b64 = data["data"][0].get("b64_json") or data["data"][0].get("b64", "")
            return ImageResult(
                image_b64=img_b64,
                mime="image/png",
                metadata={"model": self.model,
                          "endpoint": "edits" if use_edits else "generations",
                          "revised_prompt": data["data"][0].get("revised_prompt", "")},
            )

        return await with_retry(
            _call,
            max_retries=3,
            base_delay_ms=500,
            max_delay_ms=16_000,
            retryable_check=_is_retryable,
        )
