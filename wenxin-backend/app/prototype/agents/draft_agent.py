"""Draft Agent — generates low-resolution sketch candidates from Intent Card + Scout Evidence."""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from app.prototype.agents.draft_config import DraftConfig
from app.prototype.agents.draft_provider import (
    AbstractProvider,
    DiffusersProvider,
    MockProvider,
    TogetherFluxProvider,
)
from app.prototype.agents.nb2_provider import (
    NB2Provider,
    build_full_evidence_prompt,
)
from app.prototype.agents.draft_types import (
    DraftCandidate,
    DraftInput,
    DraftOutput,
)
from app.prototype.agents.inpaint_provider import (
    AbstractInpaintProvider,
    ControlNetInpaintProviderAdapter,
    DiffusersInpaintProvider,
    MaskGenerator,
    MockInpaintProvider,
)
from app.prototype.agents.layer_state import LocalRerunRequest
from app.prototype.checkpoints.draft_checkpoint import save_draft_checkpoint

__all__ = [
    "DraftAgent",
]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cultural tradition → style keyword mapping
# ---------------------------------------------------------------------------

_STYLE_MAP: dict[str, dict[str, str]] = {
    "chinese_xieyi": {
        "style": "Chinese xieyi ink wash painting, traditional brush strokes, rice paper texture",
        "negative": "photorealistic, 3D render",
    },
    "chinese_gongbi": {
        "style": "meticulous brushwork, mineral pigments, fine lines, gongbi",
        "negative": "rough texture, abstract",
    },
    "western_academic": {
        "style": "Western academic oil painting, realistic, classical composition, chiaroscuro, perspective",
        "negative": "flat, 2D, cartoon",
    },
    "islamic_geometric": {
        "style": "geometric patterns, tessellation, arabesque, Islamic art",
        "negative": "figurative, portraits",
    },
    "watercolor": {
        "style": "watercolor, wet-on-wet, transparent washes",
        "negative": "heavy impasto, digital",
    },
    "african_traditional": {
        "style": "carved forms, bold patterns, symbolic, African traditional art",
        "negative": "photorealistic, digital",
    },
    "south_asian": {
        "style": "miniature painting, detailed, narrative, South Asian art",
        "negative": "abstract, minimalist",
    },
    "default": {
        "style": "fine art, museum quality, detailed",
        "negative": "low quality, blurry",
    },
}




def _get_provider(name: str, config: DraftConfig | None = None) -> AbstractProvider:
    """Resolve a provider name to an AbstractProvider instance."""
    if name == "mock":
        return MockProvider()
    if name == "together_flux":
        cfg = config or DraftConfig()
        api_key = cfg.api_key or os.environ.get("TOGETHER_API_KEY", "")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY required for together_flux provider")
        model = cfg.provider_model or "black-forest-labs/FLUX.1-schnell"
        return TogetherFluxProvider(api_key=api_key, model=model, timeout=cfg.timeout_seconds)
    if name == "diffusers":
        cfg = config or DraftConfig()
        model_id = cfg.provider_model or "runwayml/stable-diffusion-v1-5"
        return DiffusersProvider(model_id=model_id)
    if name == "koala":
        from app.prototype.agents.koala_provider import KoalaProvider
        kp = KoalaProvider()
        # Wrap KoalaProvider in the AbstractProvider interface
        return _KoalaProviderAdapter(kp, config)
    if name == "nb2":
        from app.core.config import settings as _settings
        api_key = (
            (config.api_key if config else "")
            or os.environ.get("GOOGLE_API_KEY", "")
            or os.environ.get("GEMINI_API_KEY", "")
            or _settings.GOOGLE_API_KEY
            or _settings.GEMINI_API_KEY
        )
        if not api_key:
            raise ValueError("GOOGLE_API_KEY (or GEMINI_API_KEY) required for nb2 provider")
        return NB2Provider(api_key=api_key)
    raise ValueError(f"Unknown provider: {name!r} (available: mock, together_flux, diffusers, koala, nb2)")


class _KoalaProviderAdapter(AbstractProvider):
    """Adapter wrapping KoalaProvider to fit AbstractProvider interface."""

    def __init__(self, koala, config=None):
        self._koala = koala
        self._config = config

    @property
    def model_ref(self) -> str:
        return self._koala.model_ref

    def generate(self, prompt, negative_prompt, seed, width, height, steps, sampler, output_path) -> str:
        return self._koala.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            width=width,
            height=height,
            steps=steps,
            output_path=output_path,
        )


class DraftAgent:
    """Generate 4-6 traceable low-res sketch candidates."""

    def __init__(self, config: DraftConfig | None = None) -> None:
        self._default_config = config or DraftConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, draft_input: DraftInput, evidence_pack=None) -> DraftOutput:
        """Execute the draft generation pipeline.

        Parameters
        ----------
        draft_input : DraftInput
            Standard draft input with subject, tradition, evidence dict.
        evidence_pack : EvidencePack | None
            Layer 1a structured evidence pack. If provided, uses enriched
            prompt construction; otherwise falls back to legacy path.
        """
        t0 = time.monotonic()
        config = draft_input.config or self._default_config
        provider = _get_provider(config.provider, config)
        safe_task_id = _sanitize_task_id(draft_input.task_id)

        # Layer 1a: prefer EvidencePack-based prompt if available
        if evidence_pack is not None and config.enable_full_evidence_injection:
            # NB2 full-context mode: inject complete EvidencePack into 32K context.
            # Unlike FLUX (T5, 512 tokens), NB2's Gemini encoder handles the full text.
            prompt, negative_prompt = build_full_evidence_prompt(
                subject=draft_input.subject,
                tradition=draft_input.cultural_tradition,
                evidence_pack=evidence_pack,
            )
            logger.info(
                "NB2 full-evidence prompt: %d chars for task %s",
                len(prompt), draft_input.task_id,
            )
        elif evidence_pack is not None:
            prompt, negative_prompt = self._build_prompt_from_pack(
                subject=draft_input.subject,
                tradition=draft_input.cultural_tradition,
                pack=evidence_pack,
            )
        else:
            prompt, negative_prompt = self._build_prompt(
                subject=draft_input.subject,
                tradition=draft_input.cultural_tradition,
                evidence=draft_input.evidence,
            )

        candidates: list[DraftCandidate] = []
        errors: list[str] = []

        for i in range(config.n_candidates):
            seed = config.seed_base + i
            candidate_id = f"draft-{safe_task_id}-{i}"
            image_path = self._image_path(safe_task_id, candidate_id)

            ok = False
            actual_path = image_path
            for attempt in range(1 + config.max_retries):
                try:
                    actual_path = provider.generate(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        seed=seed,
                        width=config.width,
                        height=config.height,
                        steps=config.steps,
                        sampler=config.sampler,
                        output_path=image_path,
                    )
                    ok = True
                    break
                except Exception as exc:  # noqa: BLE001
                    errors.append(
                        f"{candidate_id} attempt {attempt}: {exc}"
                    )

            if ok:
                candidates.append(
                    DraftCandidate(
                        candidate_id=candidate_id,
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        seed=seed,
                        width=config.width,
                        height=config.height,
                        steps=config.steps,
                        sampler=config.sampler,
                        model_ref=provider.model_ref,
                        image_path=actual_path,
                    )
                )

        elapsed_ms = int((time.monotonic() - t0) * 1000)
        success = len(candidates) == config.n_candidates

        output = DraftOutput(
            task_id=draft_input.task_id,
            candidates=candidates,
            created_at=datetime.now(timezone.utc).isoformat(),
            latency_ms=elapsed_ms,
            model_ref=provider.model_ref,
            success=success,
            error="; ".join(errors) if errors else None,
        )

        save_draft_checkpoint(output)
        return output

    # ------------------------------------------------------------------
    # Local rerun (inpainting)
    # ------------------------------------------------------------------

    def refine_candidate(
        self,
        local_rerun_request: LocalRerunRequest,
        base_image_path: str,
        inpaint_provider_name: str = "mock_inpaint",
    ) -> DraftCandidate:
        """Refine a candidate via targeted inpainting based on LocalRerunRequest.

        Parameters
        ----------
        local_rerun_request : LocalRerunRequest
            Specifies target layers, preserve layers, mask specs, and prompt delta.
        base_image_path : str
            Path to the base image to refine.
        inpaint_provider_name : str
            Which inpaint provider to use ("mock_inpaint" or "diffusers_inpaint").

        Returns
        -------
        DraftCandidate
            A new candidate with the refined image.
        """
        config = self._default_config
        provider = _get_inpaint_provider(inpaint_provider_name)
        mask_gen = MaskGenerator()

        # 1. Generate mask from target layers
        mask = mask_gen.generate(
            target_layers=local_rerun_request.target_layers,
            image_width=config.width,
            image_height=config.height,
            mask_specs=local_rerun_request.mask_specs or None,
            preserve_layers=getattr(local_rerun_request, "preserve_layers", None) or None,
        )

        # 2. Build prompt delta
        prompt = local_rerun_request.prompt_delta or "refine artistic details"
        negative = local_rerun_request.negative_delta or ""

        # 3. Determine output path
        safe_base_id = _SAFE_TASK_ID_RE.sub("_", local_rerun_request.base_candidate_id)
        candidate_id = f"{safe_base_id}-refined"
        output_path = str(
            Path(__file__).resolve().parent.parent
            / "checkpoints" / "draft" / "refined" / f"{candidate_id}.png"
        )

        # 4. Run inpainting
        seed = config.seed_base
        strength = 0.75  # default denoising strength

        # Override from structure_constraints if provided
        if local_rerun_request.structure_constraints:
            strength = local_rerun_request.structure_constraints.get("strength", strength)

        actual_path = provider.inpaint(
            base_image_path=base_image_path,
            mask_image=mask,
            prompt=prompt,
            negative_prompt=negative,
            seed=seed,
            strength=strength,
            steps=config.steps,
            output_path=output_path,
        )

        return DraftCandidate(
            candidate_id=candidate_id,
            prompt=prompt,
            negative_prompt=negative,
            seed=seed,
            width=config.width,
            height=config.height,
            steps=config.steps,
            sampler="inpaint",
            model_ref=provider.model_ref,
            image_path=actual_path,
        )

    # ------------------------------------------------------------------
    # Style transfer (IP-Adapter)
    # ------------------------------------------------------------------

    def style_transfer(
        self,
        image_path: str,
        reference_image_path: str,
        prompt: str,
        scale: float = 0.6,
        seed: int = 42,
        output_path: str = "",
    ) -> DraftCandidate:
        """Apply style transfer using IP-Adapter.

        Parameters
        ----------
        image_path : str
            Path to the source content image.
        reference_image_path : str
            Path to the style reference image.
        prompt : str
            Text prompt guiding the transfer.
        scale : float
            IP-Adapter influence scale.
        output_path : str
            Where to save the result.

        Returns
        -------
        DraftCandidate
            A new candidate with the style-transferred image.
        """
        from PIL import Image as PILImage
        from app.prototype.agents.ip_adapter_provider import IPAdapterProvider

        config = self._default_config
        provider = IPAdapterProvider()

        image = PILImage.open(image_path).convert("RGB")
        reference = PILImage.open(reference_image_path).convert("RGB")

        if not output_path:
            safe_id = _SAFE_TASK_ID_RE.sub("_", Path(image_path).stem)
            output_path = str(
                Path(__file__).resolve().parent.parent
                / "checkpoints" / "draft" / "style_transfer" / f"{safe_id}_styled.png"
            )

        actual_path = provider.transfer_style(
            image=image,
            reference_image=reference,
            prompt=prompt,
            scale=scale,
            seed=seed,
            width=config.width,
            height=config.height,
            output_path=output_path,
        )

        return DraftCandidate(
            candidate_id=f"{Path(image_path).stem}-styled",
            prompt=prompt,
            negative_prompt="",
            seed=seed,
            width=config.width,
            height=config.height,
            steps=config.steps,
            sampler="ip_adapter",
            model_ref=provider.model_ref,
            image_path=actual_path,
        )

    # ------------------------------------------------------------------
    # Layer 1b: Rerun with FixItPlan
    # ------------------------------------------------------------------

    def rerun_with_fix(
        self,
        original_prompt: str,
        fix_plan: "FixItPlan",
        evidence_pack=None,
        base_image_path: str = "",
        inpaint_provider_name: str = "mock_inpaint",
        preserve_layers: list[str] | None = None,
    ) -> DraftCandidate:
        """Rerun generation using a targeted FixItPlan from Critic.

        Enhances the original prompt with fix_plan.to_prompt_delta()
        and uses mask hints for targeted inpainting when a base image
        is available.
        """
        config = self._default_config

        # Build enhanced prompt
        prompt_delta = fix_plan.to_prompt_delta()
        enhanced_prompt = original_prompt
        if prompt_delta:
            enhanced_prompt = f"{original_prompt}, {prompt_delta}"

        negative_additions = fix_plan.get_negative_additions()

        # If we have a base image, use inpainting
        if base_image_path:
            provider = _get_inpaint_provider(inpaint_provider_name)
            mask_gen = MaskGenerator()

            # Build per-item mask specs (each FixItem has its own mask_region_hint)
            target_layers = []
            mask_specs_list = []
            if not fix_plan.items:
                logger.warning("FixItPlan.items is empty (Critic produced no fix items)")
            for item in fix_plan.items:
                if item.target_layer:
                    target_layers.append(item.target_layer)
                    if item.mask_region_hint:
                        mask_specs_list.append({
                            "layer": item.target_layer,
                            "region": item.mask_region_hint,
                            "strength": item.strength,
                        })
            if not target_layers:
                logger.warning(
                    "FixItPlan items have no target_layers, defaulting to ['L2'] blind inpaint"
                )
                target_layers = ["L2"]  # default
            if not mask_specs_list:
                mask_specs_list = None

            mask = mask_gen.generate(
                target_layers=target_layers,
                image_width=config.width,
                image_height=config.height,
                mask_specs=mask_specs_list,
                preserve_layers=preserve_layers,
            )

            negative = ", ".join(negative_additions) if negative_additions else ""
            candidate_id = f"fix-{int(time.time())}"
            output_path = str(
                Path(__file__).resolve().parent.parent
                / "checkpoints" / "draft" / "refined" / f"{candidate_id}.png"
            )

            actual_path = provider.inpaint(
                base_image_path=base_image_path,
                mask_image=mask,
                prompt=enhanced_prompt,
                negative_prompt=negative,
                seed=config.seed_base,
                strength=0.75,
                steps=config.steps,
                output_path=output_path,
            )

            return DraftCandidate(
                candidate_id=candidate_id,
                prompt=enhanced_prompt,
                negative_prompt=negative,
                seed=config.seed_base,
                width=config.width,
                height=config.height,
                steps=config.steps,
                sampler="fix_it_inpaint",
                model_ref=provider.model_ref,
                image_path=actual_path,
            )

        # No base image — full regeneration with enhanced prompt
        provider = _get_provider(config.provider, config)
        style_entry = _STYLE_MAP["default"]
        negative = style_entry["negative"]
        if negative_additions:
            negative = f"{negative}, {', '.join(negative_additions)}"

        candidate_id = f"fix-{int(time.time())}"
        image_path = str(
            Path(__file__).resolve().parent.parent
            / "checkpoints" / "draft" / f"fix_{candidate_id}.png"
        )

        actual_path = provider.generate(
            prompt=enhanced_prompt,
            negative_prompt=negative,
            seed=config.seed_base,
            width=config.width,
            height=config.height,
            steps=config.steps,
            sampler=config.sampler,
            output_path=image_path,
        )

        return DraftCandidate(
            candidate_id=candidate_id,
            prompt=enhanced_prompt,
            negative_prompt=negative,
            seed=config.seed_base,
            width=config.width,
            height=config.height,
            steps=config.steps,
            sampler=config.sampler,
            model_ref=provider.model_ref,
            image_path=actual_path,
        )

    # ------------------------------------------------------------------
    # Prompt assembly
    # ------------------------------------------------------------------

    def _build_prompt_from_pack(
        self,
        subject: str,
        tradition: str,
        pack: "EvidencePack",
    ) -> tuple[str, str]:
        """Build prompt from a structured EvidencePack (Layer 1a).

        Uses terminology anchors with usage hints, composition fragments,
        style constraints, and taboo constraints for negative prompt.
        """
        style_entry = _STYLE_MAP.get(tradition, _STYLE_MAP["default"])
        style_kw = style_entry["style"]
        base_neg = style_entry["negative"]

        # Base prompt
        prompt_parts = [
            f"A {tradition.replace('_', ' ')} artwork depicting: {subject}",
            style_kw,
        ]

        # Terminology anchors with usage hints
        for anchor in pack.anchors:
            if anchor.usage_hint:
                prompt_parts.append(f"{anchor.term} ({anchor.usage_hint})")
            else:
                prompt_parts.append(anchor.term)

        # Composition fragments
        for comp in pack.compositions:
            if comp.example_prompt_fragment:
                prompt_parts.append(comp.example_prompt_fragment)

        # Style constraints
        for style in pack.styles:
            prompt_parts.append(f"{style.attribute}: {style.value}")

        prompt = ", ".join(prompt_parts)

        # Negative prompt: base + taboos
        neg_parts = [base_neg]
        neg_parts.extend(pack.get_negative_prompt_additions())
        negative_prompt = ", ".join(neg_parts)

        return prompt, negative_prompt

    def _build_prompt(
        self,
        subject: str,
        tradition: str,
        evidence: dict,
    ) -> tuple[str, str]:
        """Assemble generation prompt from subject, tradition, and evidence."""
        style_entry = _STYLE_MAP.get(tradition, _STYLE_MAP["default"])
        style_kw = style_entry["style"]
        base_neg = style_entry["negative"]

        # Base prompt
        prompt_parts = [
            f"A {tradition.replace('_', ' ')} artwork depicting: {subject}",
            style_kw,
        ]

        # Evidence enrichment: add matched terminology terms
        for hit in evidence.get("terminology_hits", []):
            term = hit.get("term", "")
            if term:
                prompt_parts.append(term)

        prompt = ", ".join(prompt_parts)

        # Negative prompt: base + taboo descriptions
        neg_parts = [base_neg]
        for violation in evidence.get("taboo_violations", []):
            desc = violation.get("description", "")
            if desc:
                neg_parts.append(desc)

        negative_prompt = ", ".join(neg_parts)

        return prompt, negative_prompt

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------

    @staticmethod
    def _image_path(task_id: str, candidate_id: str) -> str:
        """Return the output path for a candidate image."""
        base = Path(__file__).resolve().parent.parent / "checkpoints" / "draft"
        return str(base / task_id / f"{candidate_id}.png")


def _get_inpaint_provider(name: str) -> AbstractInpaintProvider:
    """Resolve an inpaint provider name to an instance."""
    if name in ("mock", "mock_inpaint"):
        return MockInpaintProvider()
    if name in ("diffusers", "diffusers_inpaint"):
        return DiffusersInpaintProvider()
    if name in ("flux_fill", "flux_fill_dev"):
        from app.prototype.agents.flux_fill_provider import FluxFillProvider
        return FluxFillProvider(use_pro=False)
    if name == "flux_fill_pro":
        from app.prototype.agents.flux_fill_provider import FluxFillProvider
        return FluxFillProvider(use_pro=True)
    if name in ("controlnet_canny", "controlnet_depth"):
        cn_type = name.split("_", 1)[1]  # "canny" or "depth"
        return ControlNetInpaintProviderAdapter(cn_type)
    return MockInpaintProvider()  # safe fallback


def _sanitize_task_id(task_id: str) -> str:
    """Convert task_id into a filesystem-safe path segment."""
    from app.prototype.checkpoints.utils import safe_task_id
    return safe_task_id(task_id)
