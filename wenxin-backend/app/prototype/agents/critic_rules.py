"""Rule-based L1-L5 scoring engine for the Critic Agent.

When a candidate has a valid image_path, CLIP-based image scores are
blended with rule scores so that scores vary across rounds — enabling
real self-correction in the Agent loop.
"""

from __future__ import annotations

import logging

from app.prototype.agents.critic_config import DIMENSIONS
from app.prototype.agents.critic_types import DimensionScore

__all__ = [
    "CriticRules",
    "ParallelDimensionScorer",
]

# Re-export for convenience
from app.prototype.agents.parallel_scorer import ParallelDimensionScorer  # noqa: E402, F401

logger = logging.getLogger(__name__)

# Cultural style keywords per tradition (subset of DraftAgent._STYLE_MAP keys)
_CULTURE_KEYWORDS: dict[str, list[str]] = {
    "chinese_xieyi": ["ink", "brush", "xieyi", "rice paper", "wash", "shanshui", "shan shui"],
    "chinese_gongbi": ["gongbi", "meticulous", "mineral", "fine lines"],
    "western_academic": ["oil", "chiaroscuro", "perspective", "classical", "academic", "realism"],
    "islamic_geometric": ["geometric", "tessellation", "arabesque", "islamic"],
    "watercolor": ["watercolor", "transparent", "washes", "wet"],
    "african_traditional": ["carved", "bold", "symbolic", "african"],
    "south_asian": ["miniature", "narrative", "south asian"],
    "default": ["art", "fine art", "museum"],
}

# How much to trust image-based CLIP score vs rule-based score per dimension.
# Higher = more image influence. L4 is 0 because taboo detection is metadata.
_IMAGE_BLEND_WEIGHTS: dict[str, float] = {
    "L1": 0.50,  # Visual perception: heavily image-dependent
    "L2": 0.20,  # Technical: mostly config-based, some image quality
    "L3": 0.40,  # Cultural context: visual cultural match
    "L5": 0.40,  # Aesthetic: visual aesthetic quality
}


def _clamp(v: float) -> float:
    """Clamp value to [0.0, 1.0]."""
    return max(0.0, min(1.0, v))


class CriticRules:
    """Rule-based scorer with optional CLIP image blending."""

    def score(
        self,
        candidate: dict,
        evidence: dict,
        cultural_tradition: str,
        subject: str = "",
        use_vlm: bool = True,
    ) -> list[DimensionScore]:
        """Return L1-L5 DimensionScore list for a single candidate.

        If candidate has a valid image_path and CLIP is available,
        image-based scores are blended with rule-based scores.
        The ``subject`` parameter is used for L1 CLIP comparison.
        """
        prompt = candidate.get("prompt", "")
        prompt_lower = prompt.lower()
        steps = candidate.get("steps", 0)
        sampler = candidate.get("sampler", "")
        model_ref = candidate.get("model_ref", "")

        term_hits = evidence.get("terminology_hits", [])
        sample_matches = evidence.get("sample_matches", [])
        taboo_violations = evidence.get("taboo_violations", [])

        style_keywords = _CULTURE_KEYWORDS.get(
            cultural_tradition, _CULTURE_KEYWORDS["default"]
        )
        has_style = any(kw in prompt_lower for kw in style_keywords)
        has_terms = len(term_hits) > 0
        has_samples = len(sample_matches) > 0
        has_taboo_critical = any(
            v.get("severity") == "critical" for v in taboo_violations
        )
        has_taboo_high = any(
            v.get("severity") == "high" for v in taboo_violations
        )

        scores: list[DimensionScore] = []

        # --- L1: visual_perception ---
        l1 = 0.35
        rationale_parts_l1 = ["base=0.35"]
        if has_style:
            l1 += 0.2
            rationale_parts_l1.append("style_match=+0.2")
        if has_terms:
            l1 += 0.15
            rationale_parts_l1.append("terminology=+0.15")
        if len(prompt) > 50:
            l1 += 0.15
            rationale_parts_l1.append("prompt_length>50=+0.15")
        scores.append(DimensionScore(
            dimension=DIMENSIONS[0],
            score=_clamp(l1),
            rationale="; ".join(rationale_parts_l1),
        ))

        # --- L2: technical_analysis ---
        l2 = 0.35
        rationale_parts_l2 = ["base=0.35"]
        if steps >= 15:
            l2 += 0.2
            rationale_parts_l2.append("steps>=15=+0.2")
        if sampler:
            l2 += 0.15
            rationale_parts_l2.append("sampler_present=+0.15")
        if model_ref:
            l2 += 0.15
            rationale_parts_l2.append("model_ref_present=+0.15")
        scores.append(DimensionScore(
            dimension=DIMENSIONS[1],
            score=_clamp(l2),
            rationale="; ".join(rationale_parts_l2),
        ))

        # --- L3: cultural_context ---
        l3 = 0.3
        rationale_parts_l3 = ["base=0.3"]
        term_bonus = min(len(term_hits) * 0.15, 0.3)
        if term_bonus > 0:
            l3 += term_bonus
            rationale_parts_l3.append(f"term_hits({len(term_hits)})=+{term_bonus:.2f}")
        sample_bonus = min(len(sample_matches) * 0.1, 0.2)
        if sample_bonus > 0:
            l3 += sample_bonus
            rationale_parts_l3.append(f"sample_matches({len(sample_matches)})=+{sample_bonus:.2f}")
        if not taboo_violations:
            l3 += 0.2
            rationale_parts_l3.append("no_taboo=+0.2")
        scores.append(DimensionScore(
            dimension=DIMENSIONS[2],
            score=_clamp(l3),
            rationale="; ".join(rationale_parts_l3),
        ))

        # --- L4: critical_interpretation ---
        l4 = 0.6
        rationale_parts_l4 = ["base=0.6"]
        if has_taboo_critical:
            l4 = 0.0
            rationale_parts_l4 = ["taboo_critical → 0.0"]
        elif has_taboo_high:
            # Hard cap at 0.3 — no bonus stacking allowed (symmetric with taboo_critical)
            l4 = 0.3
            rationale_parts_l4 = ["taboo_high → 0.3"]
        else:
            if has_terms:
                l4 += 0.2
                rationale_parts_l4.append("terminology=+0.2")
            if has_samples:
                l4 += 0.2
                rationale_parts_l4.append("sample_evidence=+0.2")
        scores.append(DimensionScore(
            dimension=DIMENSIONS[3],
            score=_clamp(l4),
            rationale="; ".join(rationale_parts_l4),
        ))

        # --- L5: philosophical_aesthetic ---
        l5 = 0.4
        rationale_parts_l5 = ["base=0.4"]
        culture_kws = ["culture", "cultural", "philosophy", "aesthetic",
                       "meaning", "symbolism", "tradition", "heritage"]
        if any(kw in prompt_lower for kw in culture_kws):
            l5 += 0.2
            rationale_parts_l5.append("cultural_keywords=+0.2")
        if not taboo_violations:
            l5 += 0.2
            rationale_parts_l5.append("no_taboo=+0.2")
        if len(term_hits) >= 2:
            l5 += 0.2
            rationale_parts_l5.append("term_coverage>=2=+0.2")
        scores.append(DimensionScore(
            dimension=DIMENSIONS[4],
            score=_clamp(l5),
            rationale="; ".join(rationale_parts_l5),
        ))

        # --- Image-aware blending (VLM preferred, CLIP fallback) ---
        image_path = candidate.get("image_path", "")
        if image_path and subject:
            vlm_scores = None
            if use_vlm:
                vlm_scores = self._try_vlm_scoring(
                    image_path, subject, cultural_tradition,
                    prompt=prompt, evidence=evidence,
                )
            if vlm_scores is not None:
                scores = self._blend_vlm_scores(scores, vlm_scores)
            else:
                scores = self._blend_image_scores(
                    scores, image_path, subject, cultural_tradition,
                )

        return scores

    @staticmethod
    def _blend_image_scores(
        scores: list[DimensionScore],
        image_path: str,
        subject: str,
        cultural_tradition: str,
    ) -> list[DimensionScore]:
        """Blend rule-based scores with CLIP image scores."""
        try:
            from app.prototype.agents.image_scorer import ImageScorer

            scorer = ImageScorer.get()
            image_scores = scorer.score_image(image_path, subject, cultural_tradition)
        except Exception as e:
            logger.debug("Image scorer unavailable: %s", e)
            return scores

        if image_scores is None:
            return scores

        # Map dimension index -> (CLIP key, blend weight)
        blend_map: dict[int, tuple[str, float]] = {
            0: ("L1", _IMAGE_BLEND_WEIGHTS["L1"]),  # visual_perception
            1: ("L2", _IMAGE_BLEND_WEIGHTS["L2"]),  # technical_analysis
            2: ("L3", _IMAGE_BLEND_WEIGHTS["L3"]),  # cultural_context
            # 3: L4 — no image component (taboo is metadata)
            4: ("L5", _IMAGE_BLEND_WEIGHTS["L5"]),  # philosophical_aesthetic
        }

        blended = list(scores)
        for idx, (key, weight) in blend_map.items():
            if key not in image_scores:
                continue
            old = scores[idx].score
            img = image_scores[key]
            new = (1.0 - weight) * old + weight * img
            raw = image_scores.get(f"_{key}_raw", 0.0)

            blended[idx] = DimensionScore(
                dimension=scores[idx].dimension,
                score=_clamp(new),
                rationale=(
                    f"{scores[idx].rationale}; "
                    f"CLIP_{key}={raw:.3f}→{img:.2f}(w={weight})"
                ),
            )

        logger.info(
            "Image scoring applied: L1=%.3f L2=%.3f L3=%.3f L5=%.3f (raw CLIP)",
            image_scores.get("_L1_raw", 0),
            image_scores.get("_L2_raw", 0),
            image_scores.get("_L3_raw", 0),
            image_scores.get("_L5_raw", 0),
        )

        return blended

    # ------------------------------------------------------------------
    # VLM scoring (Line A: replaces CLIP)
    # ------------------------------------------------------------------

    @staticmethod
    def _try_vlm_scoring(
        image_path: str,
        subject: str,
        cultural_tradition: str,
        prompt: str = "",
        evidence: dict | None = None,
    ) -> dict[str, float] | None:
        """Try to score image using VLM. Returns None if unavailable."""
        try:
            from app.prototype.agents.vlm_critic import VLMCritic

            vlm = VLMCritic.get()
            if not vlm.available:
                return None
            return vlm.score_image(
                image_path=image_path,
                subject=subject,
                cultural_tradition=cultural_tradition,
                prompt=prompt,
                evidence=evidence or {},
            )
        except Exception as e:
            logger.debug("VLM scorer unavailable: %s", e)
            return None

    @staticmethod
    def _blend_vlm_scores(
        scores: list[DimensionScore],
        vlm_scores: dict[str, float],
    ) -> list[DimensionScore]:
        """Blend rule-based scores with VLM scores.

        VLM gets higher blend weights than CLIP because it actually
        understands the image content (not just cosine similarity).
        """
        # VLM blend weights — much higher than CLIP because VLM
        # provides meaningful visual evaluation
        vlm_weights: dict[str, float] = {
            "L1": 0.70,  # Visual perception: VLM excels here
            "L2": 0.50,  # Technical: VLM can assess quality
            "L3": 0.60,  # Cultural: VLM understands cultural context
            "L4": 0.30,  # Critical: mostly metadata, but VLM can detect issues
            "L5": 0.70,  # Aesthetic: VLM can judge artistic quality
        }

        # Map dimension name → (index in scores list, VLM key)
        dim_map: dict[int, str] = {
            0: "L1",  # visual_perception
            1: "L2",  # technical_analysis
            2: "L3",  # cultural_context
            3: "L4",  # critical_interpretation
            4: "L5",  # philosophical_aesthetic
        }

        blended = list(scores)
        for idx, key in dim_map.items():
            if key not in vlm_scores or idx >= len(scores):
                continue

            # Protect taboo hard overrides: if rule-based L4 ≤ 0.3,
            # VLM must not raise it (taboo_critical=0.0, taboo_high=0.3)
            old = scores[idx].score
            if key == "L4" and old <= 0.3:
                continue

            weight = vlm_weights.get(key, 0.5)
            vlm_val = vlm_scores[key]
            new = (1.0 - weight) * old + weight * vlm_val
            rationale_suffix = vlm_scores.get(f"{key}_rationale", "")
            raw = vlm_scores.get(f"_{key}_raw", vlm_val)

            blended[idx] = DimensionScore(
                dimension=scores[idx].dimension,
                score=_clamp(new),
                rationale=(
                    f"{scores[idx].rationale}; "
                    f"VLM_{key}={raw:.3f}→{vlm_val:.2f}(w={weight})"
                    + (f" [{rationale_suffix}]" if rationale_suffix else "")
                ),
            )

        logger.info(
            "VLM scoring applied: L1=%.3f L2=%.3f L3=%.3f L4=%.3f L5=%.3f",
            vlm_scores.get("L1", 0),
            vlm_scores.get("L2", 0),
            vlm_scores.get("L3", 0),
            vlm_scores.get("L4", 0),
            vlm_scores.get("L5", 0),
        )

        return blended
