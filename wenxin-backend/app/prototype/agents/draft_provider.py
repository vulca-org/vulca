"""Draft image providers — AbstractProvider + MockProvider + TogetherFluxProvider."""

from __future__ import annotations

import base64
import struct
import time
import zlib
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

__all__ = [
    "AbstractProvider",
    "AllProvidersFailedError",
    "DiffusersProvider",
    "FallbackProvider",
    "FaultInjectProvider",
    "MockProvider",
    "TogetherFluxProvider",
    "detect_image_format",
]


def detect_image_format(data: bytes) -> str:
    """Detect image format from magic bytes. Returns 'png', 'jpeg', or 'webp'."""
    if data[:4] == b"\x89PNG":
        return "png"
    if data[:2] == b"\xff\xd8":
        return "jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return "png"  # fallback


_FORMAT_EXT = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}


class AbstractProvider(ABC):
    """Base class for draft image generators."""

    @abstractmethod
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
        """Generate an image and write it to *output_path* (or corrected path).

        Returns the actual output path on success (extension may differ from input).
        """
        ...

    @property
    @abstractmethod
    def model_ref(self) -> str:
        """Human-readable model identifier."""
        ...


class MockProvider(AbstractProvider):
    """Generate deterministic placeholder PNGs using only stdlib.

    The image is an 8x8 pixel solid-colour PNG.  The colour is derived
    deterministically from *seed* so identical seeds always produce
    byte-identical files.
    """

    @property
    def model_ref(self) -> str:
        return "mock-v1"

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
        r, g, b = _seed_to_rgb(seed)
        png_bytes = _make_solid_png(8, 8, r, g, b)

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(png_bytes)
        return str(out)


class TogetherFluxProvider(AbstractProvider):
    """Together.ai FLUX image generation provider.

    Uses the Together.ai Images API with b64_json response format
    to avoid a second HTTP download.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "black-forest-labs/FLUX.1-schnell",
        timeout: int = 120,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._call_log: list[dict] = []

    @property
    def model_ref(self) -> str:
        return f"together:{self._model.split('/')[-1]}"

    @property
    def call_log(self) -> list[dict]:
        return list(self._call_log)

    def generate(
        self,
        prompt: str,
        negative_prompt: str,
        seed: int,
        width: int,
        height: int,
        steps: int,
        sampler: str,  # silently ignored — Together.ai doesn't support sampler
        output_path: str,
    ) -> str:
        import requests as _requests

        # FLUX.1-schnell supports 1-4 steps; clamp to avoid API errors
        clamped_steps = min(steps, 4) if "schnell" in self._model else steps

        payload: dict = {
            "model": self._model,
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": clamped_steps,
            "seed": seed,
            "n": 1,
            "response_format": "b64_json",
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        t0 = time.monotonic()
        resp = None
        try:
            resp = _requests.post(
                "https://api.together.xyz/v1/images/generations",
                json=payload,
                headers=headers,
                timeout=self._timeout,
            )
            resp.raise_for_status()
        except _requests.exceptions.Timeout as exc:
            self._log_call(payload, None, t0, str(exc))
            raise TimeoutError(f"Together.ai timeout: {exc}") from exc
        except _requests.exceptions.ConnectionError as exc:
            self._log_call(payload, None, t0, str(exc))
            raise ConnectionError(f"Together.ai connection: {exc}") from exc
        except _requests.exceptions.RequestException as exc:
            status = resp.status_code if resp is not None else None
            self._log_call(payload, status, t0, str(exc))
            raise OSError(f"Together.ai error ({status}): {exc}") from exc

        data = resp.json()
        b64_str = data["data"][0]["b64_json"]
        img_bytes = base64.b64decode(b64_str)

        # Detect actual format and correct extension
        fmt = detect_image_format(img_bytes)
        correct_ext = _FORMAT_EXT.get(fmt, ".png")
        out = Path(output_path)
        if out.suffix != correct_ext:
            out = out.with_suffix(correct_ext)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(img_bytes)

        self._log_call(payload, resp.status_code, t0, None)
        return str(out)

    def _log_call(
        self,
        payload: dict,
        status_code: int | None,
        t0: float,
        error: str | None,
    ) -> None:
        self._call_log.append({
            "model": payload.get("model"),
            "prompt_len": len(payload.get("prompt", "")),
            "width": payload.get("width"),
            "height": payload.get("height"),
            "steps": payload.get("steps"),
            "seed": payload.get("seed"),
            "status_code": status_code,
            "latency_ms": int((time.monotonic() - t0) * 1000),
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


class DiffusersProvider(AbstractProvider):
    """Local Stable Diffusion 1.5 txt2img via HuggingFace diffusers.

    Model is lazy-loaded on first generate() call to avoid import-time GPU allocation.
    Uses float16 on CUDA for ~3.5GB VRAM (fits RTX 2070 8GB with room for ControlNet).
    """

    def __init__(
        self,
        model_id: str = "runwayml/stable-diffusion-v1-5",
        device: str = "auto",
    ) -> None:
        self._model_id = model_id
        self._device = device
        self._pipe = None

    @property
    def model_ref(self) -> str:
        return f"diffusers:{self._model_id.split('/')[-1]}"

    def _load_pipeline(self):
        if self._pipe is not None:
            return
        import torch
        from diffusers import StableDiffusionPipeline

        device = self._device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        dtype = torch.float16 if device == "cuda" else torch.float32
        self._pipe = StableDiffusionPipeline.from_pretrained(
            self._model_id,
            torch_dtype=dtype,
            safety_checker=None,
            requires_safety_checker=False,
        ).to(device)
        # Enable memory-efficient attention if available
        if hasattr(self._pipe, "enable_attention_slicing"):
            self._pipe.enable_attention_slicing()

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
        import torch

        self._load_pipeline()
        generator = torch.Generator(device=self._pipe.device).manual_seed(seed)

        result = self._pipe(
            prompt=prompt,
            negative_prompt=negative_prompt or None,
            width=width,
            height=height,
            num_inference_steps=steps,
            generator=generator,
        )
        image = result.images[0]

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        image.save(str(out))
        return str(out)


class FaultInjectProvider(AbstractProvider):
    """Programmable fault injection for testing fallback chains.

    Parameters:
        fault_type: "timeout" | "connection" | "rate_limit" | "random"
        fail_count: Number of times to fail before succeeding (0 = always fail)
        fail_rate: For "random" type, probability of failure [0.0, 1.0]
    """

    def __init__(
        self,
        fault_type: str = "timeout",
        fail_count: int = 0,
        fail_rate: float = 0.5,
    ) -> None:
        self._fault_type = fault_type
        self._fail_count = fail_count
        self._fail_rate = fail_rate
        self._call_count = 0

    @property
    def model_ref(self) -> str:
        return f"fault-inject-{self._fault_type}"

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
        self._call_count += 1

        should_fail = False
        if self._fail_count == 0:
            should_fail = True  # Always fail
        elif self._call_count <= self._fail_count:
            should_fail = True

        if self._fault_type == "random":
            import random
            rng = random.Random(seed + self._call_count)
            should_fail = rng.random() < self._fail_rate

        if should_fail:
            if self._fault_type == "timeout":
                raise TimeoutError(f"FaultInject: timeout on call #{self._call_count}")
            elif self._fault_type == "connection":
                raise ConnectionError(f"FaultInject: connection refused on call #{self._call_count}")
            elif self._fault_type == "rate_limit":
                raise ConnectionError(f"FaultInject: 429 rate limited on call #{self._call_count}")
            elif self._fault_type == "random":
                raise ConnectionError(f"FaultInject: random failure on call #{self._call_count}")
            else:
                raise RuntimeError(f"FaultInject: unknown fault_type={self._fault_type}")

        # If we get here, succeed with mock
        return MockProvider().generate(
            prompt, negative_prompt, seed, width, height, steps, sampler, output_path
        )


class AllProvidersFailedError(Exception):
    """Raised when all providers in a fallback chain have failed."""
    pass


class FallbackProvider(AbstractProvider):
    """Multi-provider fallback chain with retry and exponential backoff.

    Tries providers in order. If a provider fails, moves to the next one.
    Each provider is retried up to max_retries times before moving on.
    """

    def __init__(
        self,
        providers: list[AbstractProvider],
        max_retries_per_provider: int = 2,
        backoff_base_ms: int = 0,  # 0 in mock mode (no real delay)
    ) -> None:
        self._providers = providers
        self._max_retries = max_retries_per_provider
        self._backoff_base_ms = backoff_base_ms
        self._route_log: list[dict] = []

    @property
    def model_ref(self) -> str:
        refs = [p.model_ref for p in self._providers]
        return f"fallback({','.join(refs)})"

    @property
    def route_log(self) -> list[dict]:
        """Access the routing log for testing/debugging."""
        return list(self._route_log)

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
        errors: list[str] = []

        for provider in self._providers:
            for attempt in range(1, self._max_retries + 1):
                try:
                    result = provider.generate(
                        prompt, negative_prompt, seed, width, height,
                        steps, sampler, output_path,
                    )
                    self._route_log.append({
                        "provider": provider.model_ref,
                        "attempt": attempt,
                        "status": "success",
                    })
                    return result
                except (TimeoutError, ConnectionError, OSError) as exc:
                    self._route_log.append({
                        "provider": provider.model_ref,
                        "attempt": attempt,
                        "status": f"failed: {exc}",
                    })
                    errors.append(f"{provider.model_ref} attempt {attempt}: {exc}")
                    # Exponential backoff between retries (skip on last attempt)
                    if self._backoff_base_ms > 0 and attempt < self._max_retries:
                        _MAX_BACKOFF_MS = 30_000  # 30 seconds cap
                        delay_ms = min(self._backoff_base_ms * (2 ** (attempt - 1)), _MAX_BACKOFF_MS)
                        time.sleep(delay_ms / 1000.0)

        raise AllProvidersFailedError(
            f"All providers failed after exhausting retries: {errors}"
        )


# ---------------------------------------------------------------------------
# Minimal PNG writer (stdlib only — struct + zlib)
# ---------------------------------------------------------------------------

def _seed_to_rgb(seed: int) -> tuple[int, int, int]:
    """Map a seed to a deterministic RGB triple."""
    r = (seed * 47) % 256
    g = (seed * 113) % 256
    b = (seed * 197) % 256
    return r, g, b


def _make_solid_png(w: int, h: int, r: int, g: int, b: int) -> bytes:
    """Create a minimal valid PNG file with a solid colour.

    Follows the PNG specification:
      Signature | IHDR | IDAT (deflated raw image data) | IEND
    """

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        length = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
        return length + chunk_type + data + crc

    # PNG signature
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR: width, height, bit depth 8, colour type 2 (RGB)
    ihdr_data = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)

    # Raw image data: each row is filter-byte (0) + RGB pixels
    row = bytes([0]) + bytes([r, g, b]) * w
    raw = row * h
    compressed = zlib.compress(raw)
    idat = _chunk(b"IDAT", compressed)

    # IEND
    iend = _chunk(b"IEND", b"")

    return signature + ihdr + idat + iend
