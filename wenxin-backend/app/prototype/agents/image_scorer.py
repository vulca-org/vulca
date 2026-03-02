"""Image-aware scoring using CLIP for L1-L5 cultural art evaluation.

Uses CLIP ViT-B/32 to compute image-text similarity as a quality signal
that varies with each generated image — enabling real self-correction.

Key design:
- Singleton model loading (CLIP loads once, reused across calls)
- Batch encoding: 1 image encode + 1 batch text encode per candidate
- Graceful fallback: returns None when CLIP unavailable
- CLIP raw scores normalized from [0.15, 0.35] -> [0.0, 1.0]
- Tradition-specific reference texts for cultural context scoring
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = [
    "ImageScorer",
]

# CLIP cosine similarity typically ranges [0.15, 0.35] for art images.
# (Validated empirically in Route C sensitivity test, 2026-02-17)
_CLIP_LOW = 0.15   # maps to 0.0
_CLIP_HIGH = 0.35  # maps to 1.0

# Tradition-specific reference texts for CLIP scoring.
# English descriptions capturing visual essence (CLIP trained on EN image-text pairs).
_TRADITION_REFERENCES: dict[str, dict[str, str]] = {
    "chinese_xieyi": {
        "L1": "Chinese ink wash painting with mountains mist and pine trees",
        "L3": "traditional Chinese shanshui landscape art with calligraphy seal",
        "L5": "ethereal Asian ink painting with vast empty space and spiritual harmony",
    },
    "chinese_gongbi": {
        "L1": "detailed Chinese painting of birds and flowers on silk",
        "L3": "traditional Chinese court painting with precise fine brushwork",
        "L5": "refined meticulous Asian art with delicate mineral colors and precise lines",
    },
    "western_academic": {
        "L1": "classical European oil painting with realistic perspective",
        "L3": "Western academic art with classical composition and realist technique",
        "L5": "sublime romantic painting with dramatic light and emotional depth",
    },
    "islamic_geometric": {
        "L1": "Islamic geometric pattern with tessellation and arabesques",
        "L3": "Islamic art with intricate mathematical geometric patterns and gold",
        "L5": "sacred geometric art with infinite symmetry and spiritual precision",
    },
    "watercolor": {
        "L1": "watercolor painting with transparent washes and soft edges",
        "L3": "fine art watercolor with skilled wet-on-wet technique",
        "L5": "impressionist watercolor capturing light and atmosphere",
    },
    "african_traditional": {
        "L1": "African traditional art with bold geometric patterns and symbols",
        "L3": "African Kente cloth textile with symbolic motifs and ceremonial elements",
        "L5": "African art with deep symbolic meaning and cultural storytelling",
    },
    "south_asian": {
        "L1": "South Asian miniature painting with detailed narrative scenes",
        "L3": "Indian miniature art with narrative composition and vibrant colors",
        "L5": "South Asian art with mythological symbolism and spiritual depth",
    },
    "default": {
        "L1": "fine art painting with skilled composition and technique",
        "L3": "cultural artwork with meaningful traditional elements",
        "L5": "artwork with aesthetic depth and philosophical resonance",
    },
}

# Quality reference text for L2 technical assessment
_QUALITY_REF = "high quality detailed professional artwork, sharp clear well-composed"


def _normalize_clip(raw: float) -> float:
    """Normalize CLIP similarity from typical range to [0, 1]."""
    return max(0.0, min(1.0, (raw - _CLIP_LOW) / (_CLIP_HIGH - _CLIP_LOW)))


class ImageScorer:
    """CLIP-based image scorer for L1-L5 dimensions.

    Singleton pattern: model loaded once, shared across all scoring calls.
    """

    _instance: ImageScorer | None = None

    @classmethod
    def get(cls) -> ImageScorer:
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self._model = None
        self._available: bool | None = None

    @property
    def available(self) -> bool:
        """Check if CLIP model can be loaded."""
        if self._available is not None:
            return self._available
        try:
            from sentence_transformers import SentenceTransformer  # noqa: F401
            from PIL import Image  # noqa: F401
            import numpy as np  # noqa: F401

            self._available = True
        except ImportError:
            self._available = False
        return self._available

    def _load_model(self) -> None:
        if self._model is not None:
            return
        from sentence_transformers import SentenceTransformer

        logger.info("Loading CLIP ViT-B/32 for image scoring...")
        self._model = SentenceTransformer("clip-ViT-B-32")
        logger.info("CLIP ViT-B/32 loaded for image scoring")

    def score_image(
        self,
        image_path: str,
        subject: str,  # kept for API compat; L1 now uses tradition refs (R3-D1)
        cultural_tradition: str,
    ) -> dict[str, float] | None:
        """Score image on L1, L2, L3, L5 using CLIP similarity.

        Returns dict with normalized [0, 1] scores and raw similarities,
        or None if image scoring unavailable.

        Keys: "L1", "L2", "L3", "L5" (normalized)
              "_L1_raw", "_L2_raw", "_L3_raw", "_L5_raw" (raw CLIP cosine)
        """
        if not self.available:
            return None

        path = Path(image_path)
        if not path.exists():
            logger.debug("Image not found for scoring: %s", image_path)
            return None

        refs = _TRADITION_REFERENCES.get(
            cultural_tradition, _TRADITION_REFERENCES["default"]
        )

        try:
            from PIL import Image
            import numpy as np

            self._load_model()

            # Encode image ONCE
            img = Image.open(path).convert("RGB")
            img_emb = self._model.encode(img, convert_to_numpy=True)
            img_norm = np.linalg.norm(img_emb)
            if img_norm < 1e-8:
                return None

            # Batch encode all reference texts at once (4 texts)
            texts = [refs["L1"], _QUALITY_REF, refs["L3"], refs["L5"]]
            txt_embs = self._model.encode(texts, convert_to_numpy=True)

            # Compute cosine similarities
            sims = []
            for txt_emb in txt_embs:
                txt_norm = np.linalg.norm(txt_emb)
                if txt_norm < 1e-8:
                    sims.append(0.0)
                else:
                    sims.append(float(np.dot(img_emb, txt_emb) / (img_norm * txt_norm)))

            l1_raw, l2_raw, l3_raw, l5_raw = sims

            return {
                "L1": _normalize_clip(l1_raw),
                "L2": _normalize_clip(l2_raw),
                "L3": _normalize_clip(l3_raw),
                "L5": _normalize_clip(l5_raw),
                "_L1_raw": round(l1_raw, 4),
                "_L2_raw": round(l2_raw, 4),
                "_L3_raw": round(l3_raw, 4),
                "_L5_raw": round(l5_raw, 4),
            }

        except Exception as e:
            logger.warning("Image scoring failed for %s: %s", image_path, e)
            return None
