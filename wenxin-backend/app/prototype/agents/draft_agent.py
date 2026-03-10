"""Draft Agent — generates low-resolution sketch candidates from Intent Card + Scout Evidence."""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from app.prototype.agents.draft_config import DraftConfig
from app.prototype.agents.draft_provider import (
    AbstractProvider,
    DiffusersProvider,
    MockProvider,
)
from app.prototype.agents.model_router import MODEL_FAST
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

_LEGACY_STYLE_MAP: dict[str, dict[str, str]] = {
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

# ---------------------------------------------------------------------------
# Dynamic style lookup with 3-tier fallback: YAML → LLM → Legacy
# ---------------------------------------------------------------------------

_llm_style_cache: dict[str, dict[str, str]] = {}

_SAFE_TASK_ID_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _get_style_for_tradition(tradition: str, intent: str = "") -> dict[str, str]:
    """Dynamic style lookup with 3-tier fallback: YAML → LLM → Legacy."""
    # Tier 1: YAML tradition config
    try:
        from app.prototype.cultural_pipelines.tradition_loader import get_tradition
        tc = get_tradition(tradition)
        if tc and tc.terminology:
            style_parts: list[str] = []
            negative_parts: list[str] = []
            for term in tc.terminology:
                if term.category in ("technique", "material", "color"):
                    style_parts.append(term.term)
                    if isinstance(term.definition, str) and term.definition:
                        style_parts.append(term.definition[:80])
            for taboo in tc.taboos:
                negative_parts.append(taboo.rule)
            if style_parts:
                return {
                    "style": ", ".join(style_parts[:8]),
                    "negative": ", ".join(negative_parts[:4]) if negative_parts else "low quality, blurry",
                }
    except Exception:
        pass

    # Tier 2: LLM (with cache)
    if tradition in _llm_style_cache:
        return _llm_style_cache[tradition]
    try:
        import litellm
        response = litellm.completion(
            model=MODEL_FAST,
            messages=[{
                "role": "user",
                "content": (
                    f"For the art tradition '{tradition}', provide style keywords for image generation. "
                    f"Return ONLY a JSON object: {{\"style\": \"comma-separated style keywords\", \"negative\": \"things to avoid\"}}"
                ),
            }],
            max_tokens=200,
            temperature=0.1,
            timeout=10,
        )
        import json
        text = response.choices[0].message.content or ""
        # Try to parse JSON
        for marker in ["```json", "```"]:
            if marker in text:
                start = text.index(marker) + len(marker)
                end = text.find("```", start)
                text = text[start:end].strip() if end != -1 else text[start:].strip()
                break
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end > brace_start:
            text = text[brace_start:brace_end + 1]
        parsed = json.loads(text)
        result = {"style": str(parsed.get("style", "")), "negative": str(parsed.get("negative", "low quality, blurry"))}
        if not result["style"].strip():
            raise ValueError("empty style from LLM")
        _llm_style_cache[tradition] = result
        return result
    except Exception:
        logger.debug("LLM style generation failed for %s, using legacy", tradition)

    # Tier 3: Legacy fallback
    return _LEGACY_STYLE_MAP.get(tradition, _LEGACY_STYLE_MAP["default"])



def _get_provider(name: str, config: DraftConfig | None = None) -> AbstractProvider:
    """Resolve a provider name to an AbstractProvider instance."""
    if name == "mock":
        return MockProvider()
    if name == "diffusers":
        cfg = config or DraftConfig()
        model_id = cfg.provider_model or "runwayml/stable-diffusion-v1-5"
        return DiffusersProvider(model_id=model_id)
    if name == "koala":
        from app.prototype.agents.koala_provider import KoalaProvider
        kp = KoalaProvider()
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
    raise ValueError(f"Unknown provider: {name!r} (available: mock, nb2, diffusers, koala)")


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


def _inject_evolved_context(prompt_parts: list[str], tradition: str) -> None:
    """Inject evolved context archetypes into Draft prompt parts.

    Reads successful patterns from evolved_context.json and adds them
    as style hints to the generation prompt. Zero regression on failure.
    """
    try:
        from app.prototype.cultural_pipelines.cultural_weights import get_prompt_archetypes

        archetypes = get_prompt_archetypes(tradition, top_n=3)
        for arch in archetypes:
            pattern = arch.get("pattern", "")
            if pattern and len(pattern) > 2:
                prompt_parts.append(pattern)
            # Add draft-specific insight from agent_insights
            insights = arch.get("insights", "")
            if insights:
                # Extract key phrases (first sentence, capped at 60 chars)
                first_sentence = insights.split(".")[0].strip()
                if first_sentence and len(first_sentence) <= 60:
                    prompt_parts.append(first_sentence)
    except Exception:
        pass  # Zero regression


def _get_evolved_anti_patterns(tradition: str) -> list[str]:
    """Get evolved anti-patterns for negative prompt injection."""
    try:
        from app.prototype.cultural_pipelines.cultural_weights import get_prompt_archetypes

        anti: list[str] = []
        for arch in get_prompt_archetypes(tradition, top_n=3):
            for ap in arch.get("anti_patterns", [])[:2]:
                if ap and len(ap) <= 80:
                    anti.append(ap)
        return anti[:5]
    except Exception:
        return []


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

        # Sub-stage path: when enabled, delegate to SubStageExecutor
        if config.enable_sub_stages:
            return self._run_with_sub_stages(draft_input, config, t0)

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

        def _generate_one(i: int) -> DraftCandidate | None:
            """Generate a single candidate (thread-safe)."""
            seed = config.seed_base + i
            candidate_id = f"draft-{safe_task_id}-{i}"
            img_path = self._image_path(safe_task_id, candidate_id)

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
                        output_path=img_path,
                    )
                    return DraftCandidate(
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
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{candidate_id} attempt {attempt}: {exc}")
            return None

        # Parallel generation: each candidate is an independent HTTP call
        max_workers = min(config.n_candidates, 4)
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_generate_one, i): i for i in range(config.n_candidates)}
            results: dict[int, DraftCandidate | None] = {}
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()

        # Collect in deterministic order (by candidate index)
        for i in range(config.n_candidates):
            cand = results.get(i)
            if cand is not None:
                candidates.append(cand)

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
    # Sub-stage pipeline execution
    # ------------------------------------------------------------------

    def _run_with_sub_stages(
        self,
        draft_input: DraftInput,
        config: DraftConfig,
        t0: float,
    ) -> DraftOutput:
        """Run the draft pipeline via SubStageExecutor.

        Uses the recipe specified in config.recipe_name (or the default
        for the media type) and executes all sub-stages in order.
        """
        from app.prototype.media.recipes import get_default_recipe, get_recipe
        from app.prototype.media.sub_stage_executor import SubStageExecutor
        from app.prototype.media.types import MediaType

        # Resolve recipe
        recipe = None
        if config.recipe_name:
            recipe = get_recipe(config.recipe_name)
        if recipe is None:
            try:
                mt = MediaType(draft_input.media_type)
            except ValueError:
                mt = MediaType.IMAGE
            recipe = get_default_recipe(mt)

        # Resolve handlers based on media type
        handlers: dict = {}
        if recipe.media_type == MediaType.IMAGE:
            from app.prototype.media.image_handlers import get_image_handlers
            handlers = get_image_handlers()

        executor = SubStageExecutor(recipe=recipe, handlers=handlers)

        initial_context = {
            "task_id": draft_input.task_id,
            "subject": draft_input.subject,
            "cultural_tradition": draft_input.cultural_tradition,
            "evidence": draft_input.evidence,
        }

        # Run async executor in sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    results = pool.submit(
                        lambda: asyncio.run(executor.execute(initial_context))
                    ).result()
            else:
                results = loop.run_until_complete(executor.execute(initial_context))
        except RuntimeError:
            results = asyncio.run(executor.execute(initial_context))

        elapsed_ms = int((time.monotonic() - t0) * 1000)

        # Convert sub-stage results to serializable dicts
        sub_stage_dicts = [r.to_dict() for r in results]

        # Check if all required stages completed
        all_ok = all(
            r.status in ("completed", "skipped")
            for r in results
        )

        output = DraftOutput(
            task_id=draft_input.task_id,
            candidates=[],  # Sub-stage mode doesn't produce DraftCandidates
            created_at=datetime.now(timezone.utc).isoformat(),
            latency_ms=elapsed_ms,
            model_ref=f"sub_stage:{recipe.name}",
            success=all_ok,
            error=None if all_ok else "; ".join(
                f"{r.stage_name}: {r.error}" for r in results if r.error
            ),
            sub_stage_results=sub_stage_dicts,
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
        style_entry = _get_style_for_tradition("default")
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
        Injects evolved context (archetypes, insights, anti-patterns).
        """
        style_entry = _get_style_for_tradition(tradition)
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

        # Evolved context injection (MemRL: archetypes + insights)
        _inject_evolved_context(prompt_parts, tradition)

        prompt = ", ".join(prompt_parts)

        # Negative prompt: base + taboos + evolved anti-patterns
        neg_parts = [base_neg]
        neg_parts.extend(pack.get_negative_prompt_additions())
        neg_parts.extend(_get_evolved_anti_patterns(tradition))
        negative_prompt = ", ".join(neg_parts)

        return prompt, negative_prompt

    def _build_prompt(
        self,
        subject: str,
        tradition: str,
        evidence: dict,
    ) -> tuple[str, str]:
        """Assemble generation prompt from subject, tradition, and evidence."""
        style_entry = _get_style_for_tradition(tradition)
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

        # Evolved context injection (MemRL: archetypes + insights)
        _inject_evolved_context(prompt_parts, tradition)

        prompt = ", ".join(prompt_parts)

        # Negative prompt: base + taboo descriptions + evolved anti-patterns
        neg_parts = [base_neg]
        for violation in evidence.get("taboo_violations", []):
            desc = violation.get("description", "")
            if desc:
                neg_parts.append(desc)
        neg_parts.extend(_get_evolved_anti_patterns(tradition))

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
    if name in ("flux_fill", "flux_fill_dev", "flux_fill_pro"):
        # M0: FLUX Fill removed; NB2 doesn't support inpaint → mock fallback
        logger.warning("flux_fill inpaint deprecated (M0 Gemini migration), using mock")
        return MockInpaintProvider()
    if name == "nb2_regenerate":
        # NB2 doesn't support inpaint; caller should use full regeneration instead.
        # Return mock as a safe fallback for the inpaint interface.
        return MockInpaintProvider()
    if name in ("controlnet_canny", "controlnet_depth"):
        cn_type = name.split("_", 1)[1]  # "canny" or "depth"
        return ControlNetInpaintProviderAdapter(cn_type)
    return MockInpaintProvider()  # safe fallback


def _sanitize_task_id(task_id: str) -> str:
    """Convert task_id into a filesystem-safe path segment."""
    from app.prototype.checkpoints.utils import safe_task_id
    return safe_task_id(task_id)
