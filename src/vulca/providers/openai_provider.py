"""OpenAI DALL-E image generation provider."""
from __future__ import annotations

import base64
import io
import logging
import os

from vulca.providers.base import ImageProvider, ImageResult
from vulca.providers.retry import with_retry


logger = logging.getLogger("vulca.openai")

MODEL_CAPABILITIES: dict[str, dict[str, bool]] = {
    "dall-e-2": {
        "input_fidelity": False,
        "quality": False,
        "output_format": False,
    },
    "dall-e-3": {
        "input_fidelity": False,
        "quality": True,
        "output_format": False,
    },
    "gpt-image-1": {
        "input_fidelity": False,
        "quality": True,
        "output_format": True,
    },
    "gpt-image-1.5": {
        "input_fidelity": True,
        "quality": True,
        "output_format": True,
    },
    "gpt-image-2": {
        "input_fidelity": False,
        "quality": True,
        "output_format": True,
    },
}

MODEL_TOKEN_PRICING_PER_MILLION: dict[str, dict[str, float]] = {
    "gpt-image-1": {"input": 10.0, "output": 40.0},
    "gpt-image-1.5": {"input": 8.0, "output": 32.0},
    "gpt-image-2": {"input": 8.0, "output": 30.0},
}

MODEL_STATIC_IMAGE_PRICING: dict[str, dict[str, dict[str, float]]] = {
    "dall-e-2": {
        "standard": {
            "1024x1024": 0.020,
            "1024x1536": 0.018,
            "1536x1024": 0.020,
        },
    },
    "dall-e-3": {
        "standard": {
            "1024x1024": 0.040,
            "1024x1792": 0.080,
            "1792x1024": 0.080,
        },
        "hd": {
            "1024x1024": 0.080,
            "1024x1792": 0.120,
            "1792x1024": 0.120,
        },
    },
}


def _drop_unsupported_params(model: str, values: dict[str, str | None]) -> dict[str, str]:
    capabilities = MODEL_CAPABILITIES.get(
        model,
        {"input_fidelity": True, "quality": True, "output_format": True},
    )
    kept: dict[str, str] = {}
    for param, value in values.items():
        if value is None:
            continue
        if capabilities.get(param, True):
            kept[param] = value
            continue
        logger.info("[param-dropped] model=%s param=%s — not supported", model, param)
    return kept


def _extract_cost_usd(
    *,
    model: str,
    data: dict,
    size: str,
    quality: str | None,
) -> float | None:
    usage = data.get("usage") or {}
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")

    if isinstance(input_tokens, (int, float)) or isinstance(output_tokens, (int, float)):
        pricing = MODEL_TOKEN_PRICING_PER_MILLION.get(model)
        if pricing is not None:
            total = (
                (float(input_tokens or 0) * pricing["input"])
                + (float(output_tokens or 0) * pricing["output"])
            ) / 1_000_000
            return round(total, 6)

    static_pricing = MODEL_STATIC_IMAGE_PRICING.get(model)
    if static_pricing is None:
        return None

    quality_key = "standard"
    if model == "dall-e-3" and (quality or "").lower() in {"high", "hd"}:
        quality_key = "hd"
    by_size = static_pricing.get(quality_key, {})
    return by_size.get(size) or by_size.get("1024x1024")


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
        filtered_params = _drop_unsupported_params(
            model,
            {
                "input_fidelity": input_fidelity,
                "quality": quality,
                "output_format": output_format,
            },
        )

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
                    form.update(filtered_params)
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
                            filtered_params.get("output_format", "png")
                        )
                        if "quality" in filtered_params:
                            payload["quality"] = filtered_params["quality"]
                    else:
                        payload["response_format"] = "b64_json"
                        if "quality" in filtered_params:
                            payload["quality"] = filtered_params["quality"]
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
            metadata = {
                "model": self.model,
                "endpoint": "edits" if use_edits else "generations",
                "revised_prompt": data["data"][0].get("revised_prompt", ""),
            }
            cost_usd = _extract_cost_usd(
                model=model,
                data=data,
                size=size,
                quality=filtered_params.get("quality", quality),
            )
            if cost_usd is not None:
                metadata["cost_usd"] = cost_usd
            if data.get("usage"):
                metadata["usage"] = data["usage"]
            return ImageResult(
                image_b64=img_b64,
                mime="image/png",
                metadata=metadata,
            )

        return await with_retry(
            _call,
            max_retries=3,
            base_delay_ms=500,
            max_delay_ms=16_000,
            retryable_check=_is_retryable,
        )
