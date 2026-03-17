"""VLM Critic stub -- wraps vulca._vlm for backward compatibility.

The original 600-line VLMCritic was replaced by vulca/_vlm.py (50 lines).
This stub preserves the singleton API used by evaluate_routes and critic_rules.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class VLMCritic:
    """Lightweight VLM scoring singleton."""

    _instance: VLMCritic | None = None

    def __init__(self) -> None:
        self._api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get(
            "GOOGLE_API_KEY", ""
        )

    @classmethod
    def get(cls) -> VLMCritic:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def available(self) -> bool:
        return bool(self._api_key)

    def score_image(
        self,
        image_path: str | Path = "",
        subject: str = "",
        tradition: str = "default",
        **kwargs,
    ) -> dict[str, float | str]:
        """Score an image on L1-L5 (synchronous wrapper)."""
        img_b64, mime = self._load(image_path)

        try:
            from vulca._vlm import score_image

            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            if loop and loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor(1) as pool:
                    return pool.submit(
                        asyncio.run,
                        score_image(img_b64, mime, subject, tradition, self._api_key),
                    ).result()
            return asyncio.run(
                score_image(img_b64, mime, subject, tradition, self._api_key)
            )
        except Exception as exc:
            logger.error("VLMCritic.score_image failed: %s", exc)
            return {
                "L1": 0.0, "L2": 0.0, "L3": 0.0, "L4": 0.0, "L5": 0.0,
                "L1_rationale": f"Scoring failed: {exc}",
                "L2_rationale": "", "L3_rationale": "",
                "L4_rationale": "", "L5_rationale": "",
            }

    @staticmethod
    def _load(image_path: str | Path) -> tuple[str, str]:
        """Load image file to base64."""
        path = Path(image_path)
        if not path.exists():
            return "", "image/png"
        data = path.read_bytes()
        b64 = base64.b64encode(data).decode()
        suffix = path.suffix.lower()
        mime = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }.get(suffix, "image/png")
        return b64, mime
