"""B2B Evaluate API — cultural art evaluation and tradition identification.

Public endpoints (prefix /api/v1):
- POST /evaluate           — score an image on L1-L5 cultural dimensions
- POST /identify-tradition — auto-detect cultural tradition from image
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.prototype.api.auth import verify_api_key
from app.prototype.api.evaluate_schemas import (
    EvaluateRequest,
    EvaluateResponse,
    IdentifyTraditionRequest,
    IdentifyTraditionResponse,
    KnowledgeBaseResponse,
    KnowledgeBaseSummary,
    PipelineVariantInfo,
    TabooRuleItem,
    TraditionAlternative,
    TraditionEntry,
    TermItem,
)
import httpx

from app.prototype.tools.image_utils import cleanup_temp_image, resolve_image_input

logger = logging.getLogger(__name__)

evaluate_router = APIRouter(prefix="/api/v1", tags=["evaluate"])

# ── Dimension label mapping ─────────────────────────────────────
_DIM_TO_LABEL: dict[str, str] = {
    "visual_perception": "L1",
    "technical_analysis": "L2",
    "cultural_context": "L3",
    "critical_interpretation": "L4",
    "philosophical_aesthetic": "L5",
}
_LABEL_TO_DIM = {v: k for k, v in _DIM_TO_LABEL.items()}

# 9 known traditions
_TRADITIONS = [
    "default", "chinese_xieyi", "chinese_gongbi", "western_academic",
    "islamic_geometric", "japanese_traditional", "watercolor",
    "african_traditional", "south_asian",
]


# ── GET /api/v1/knowledge-base ─────────────────────────────────

# Pre-load JSON data once at module level
_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "terminology"


def _load_terms_json() -> dict:
    """Load terms.v1.json, returning the 'traditions' mapping."""
    path = _DATA_DIR / "terms.v1.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("traditions", {})


def _load_taboo_json() -> list[dict]:
    """Load taboo_rules.v1.json, returning the 'rules' list."""
    path = _DATA_DIR / "taboo_rules.v1.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("rules", [])


@evaluate_router.get(
    "/knowledge-base",
    response_model=KnowledgeBaseResponse,
    summary="Browse cultural knowledge base",
    description=(
        "Returns the complete cultural knowledge base: terminology, taboo rules, "
        "L1-L5 weights, and pipeline variant info for all 9 traditions. "
        "Public read-only endpoint — no API key required."
    ),
)
async def get_knowledge_base() -> KnowledgeBaseResponse:
    """Assemble knowledge-base data from existing modules (no side effects)."""
    from app.prototype.cultural_pipelines.cultural_weights import get_all_weight_tables
    from app.prototype.cultural_pipelines.pipeline_router import (
        CulturalPipelineRouter,
        _TRADITION_TO_VARIANT,
        _VARIANTS,
    )

    # 1. Load raw data
    terms_by_tradition = _load_terms_json()
    taboo_rules_raw = _load_taboo_json()
    weight_tables = get_all_weight_tables()

    # 2. Index taboo rules by tradition
    taboo_by_tradition: dict[str, list[dict]] = {}
    for rule in taboo_rules_raw:
        trad = rule.get("cultural_tradition", "*")
        taboo_by_tradition.setdefault(trad, []).append(rule)

    # Universal rules (tradition == "*") apply to every tradition
    universal_taboos = taboo_by_tradition.get("*", [])

    # 3. Build per-tradition entries
    total_terms = 0
    total_taboos = 0
    tradition_entries: list[TraditionEntry] = []

    for tradition in _TRADITIONS:
        # Terms
        tradition_terms_raw = terms_by_tradition.get(tradition, {}).get("terms", [])
        term_items = [TermItem(**t) for t in tradition_terms_raw]
        total_terms += len(term_items)

        # Taboo rules: tradition-specific + universal
        tradition_taboos_raw = taboo_by_tradition.get(tradition, []) + universal_taboos
        taboo_items = [TabooRuleItem(**r) for r in tradition_taboos_raw]
        total_taboos += len(taboo_items)

        # Weights
        weights = weight_tables.get(tradition, weight_tables.get("default", {}))

        # Pipeline variant
        variant_name = _TRADITION_TO_VARIANT.get(tradition, "default")
        variant = _VARIANTS.get(variant_name, _VARIANTS["default"])
        pipeline_info = PipelineVariantInfo(
            variant_name=variant.name,
            description=variant.description,
            scout_focus_layers=variant.scout_focus_layers,
            allow_local_rerun=variant.allow_local_rerun,
            critic_stages=variant.critic_stages,
        )

        tradition_entries.append(
            TraditionEntry(
                tradition=tradition,
                terms=term_items,
                taboo_rules=taboo_items,
                weights=weights,
                pipeline_variant=pipeline_info,
            )
        )

    # Deduplicate universal taboos from total count (counted once per tradition)
    unique_taboo_count = len(taboo_rules_raw)

    summary = KnowledgeBaseSummary(
        total_traditions=len(_TRADITIONS),
        total_terms=total_terms,
        total_taboo_rules=unique_taboo_count,
    )

    return KnowledgeBaseResponse(traditions=tradition_entries, summary=summary)


# ── POST /api/v1/evaluate ───────────────────────────────────────

@evaluate_router.post(
    "/evaluate",
    response_model=EvaluateResponse,
    summary="Evaluate artwork on L1-L5 cultural dimensions",
    description="Score an image using VLM-based cultural critique with optional Scout evidence.",
)
async def evaluate_image(
    req: EvaluateRequest,
    api_key: str = Depends(verify_api_key),
) -> EvaluateResponse:
    t0 = time.monotonic()
    tmp_path: str | None = None

    try:
        # 1. Resolve image to temp file
        tmp_path = await resolve_image_input(req.image_url, req.image_base64)

        # Intent resolution (WU-01)
        intent_result = None
        tradition_override = req.tradition
        if req.intent and req.tradition == "default":
            try:
                from app.prototype.intent.intent_agent import IntentAgent
                agent = IntentAgent.get_instance()
                intent_result = await agent.resolve(req.intent)
                if intent_result and intent_result.tradition != "default":
                    tradition_override = intent_result.tradition
            except Exception:
                logger.warning("IntentAgent resolution failed, using default tradition")

        # 2. Route tradition → weights
        from app.prototype.cultural_pipelines.pipeline_router import CulturalPipelineRouter

        router = CulturalPipelineRouter()
        route = router.route(tradition_override)
        cfg = route.critic_config
        tradition_used = route.tradition

        # 3. Optional: Scout evidence
        evidence_dict: dict[str, Any] = {}
        evidence_summary: dict | None = None
        if req.include_evidence:
            from app.prototype.tools.scout_service import get_scout_service

            scout = get_scout_service()
            evidence = scout.gather_evidence(req.subject, tradition_used)
            evidence_dict = evidence.to_dict()
            evidence_summary = {
                "sample_matches": len(evidence.sample_matches),
                "terminology_hits": len(evidence.terminology_hits),
                "taboo_violations": len(evidence.taboo_violations),
            }

        # 4. VLM scoring
        from app.prototype.agents.vlm_critic import VLMCritic

        vlm = VLMCritic.get()
        if not vlm.available:
            raise HTTPException(status_code=503, detail="VLM service unavailable (no API key)")

        raw_scores = vlm.score_image(
            image_path=tmp_path,
            subject=req.subject,
            cultural_tradition=tradition_used,
            evidence=evidence_dict or None,
        )

        if raw_scores is None:
            raise HTTPException(status_code=502, detail="VLM scoring failed")

        # 5. Extract L1-L5 scores and rationales
        scores: dict[str, float] = {}
        rationales: dict[str, str] = {}
        for dim_id, label in _DIM_TO_LABEL.items():
            scores[label] = round(raw_scores.get(label, 0.0), 4)
            rationales[label] = raw_scores.get(f"{label}_rationale", "")

        # 6. Compute weighted total
        weighted_total = sum(
            cfg.weights.get(dim_id, 0.0) * raw_scores.get(label, 0.0)
            for dim_id, label in _DIM_TO_LABEL.items()
        )

        # 7. Risk flags from evidence taboo violations
        risk_flags: list[str] = []
        if evidence_dict:
            for tv in evidence_dict.get("taboo_violations", []):
                desc = tv.get("description", tv.get("rule_id", "unknown"))
                risk_flags.append(f"[{tv.get('severity', 'warn')}] {desc}")

        # 8. Build recommendations from low-scoring dimensions
        recommendations: list[str] = []
        for label, score_val in scores.items():
            if score_val < 0.6:
                dim_name = _LABEL_TO_DIM.get(label, label)
                recommendations.append(
                    f"{label} ({dim_name}): score {score_val:.2f} — consider strengthening this dimension"
                )

        # 9. Cultural diagnosis from rationales
        diagnosis_parts = [f"{k}: {v}" for k, v in rationales.items() if v]
        cultural_diagnosis = "; ".join(diagnosis_parts[:3]) if diagnosis_parts else ""

        elapsed_ms = int((time.monotonic() - t0) * 1000)

        # Build intent and result card dicts
        intent_resolved_dict = None
        if intent_result:
            intent_resolved_dict = {
                "tradition": intent_result.tradition,
                "context": intent_result.context,
                "confidence": intent_result.confidence,
            }

        result_card_dict = None
        try:
            from app.prototype.intent.result_formatter import ResultFormatter
            formatter = ResultFormatter()
            response_data = {
                "scores": scores,
                "weighted_total": round(weighted_total, 4),
                "tradition_used": tradition_used,
                "recommendations": recommendations,
                "risk_flags": risk_flags,
            }
            card = formatter.format(response_data, intent_result)
            result_card_dict = {
                "score": card.score,
                "summary": card.summary,
                "risk_level": card.risk_level,
            }
        except Exception:
            pass

        return EvaluateResponse(
            scores=scores,
            rationales=rationales,
            weighted_total=round(weighted_total, 4),
            tradition_used=tradition_used,
            cultural_diagnosis=cultural_diagnosis,
            recommendations=recommendations,
            risk_flags=risk_flags,
            evidence_summary=evidence_summary,
            intent_resolved=intent_resolved_dict,
            result_card=result_card_dict,
            latency_ms=elapsed_ms,
        )

    except HTTPException:
        raise
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=400, detail=f"Image download failed: {exc.response.status_code}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Evaluate API error")
        raise HTTPException(status_code=500, detail=f"Internal error: {type(exc).__name__}") from exc
    finally:
        if tmp_path:
            cleanup_temp_image(tmp_path)


# ── POST /api/v1/identify-tradition ─────────────────────────────

@evaluate_router.post(
    "/identify-tradition",
    response_model=IdentifyTraditionResponse,
    summary="Auto-detect cultural tradition from image",
    description="Analyze an image to identify its cultural art tradition and recommend L1-L5 weights.",
)
async def identify_tradition(
    req: IdentifyTraditionRequest,
    api_key: str = Depends(verify_api_key),
) -> IdentifyTraditionResponse:
    t0 = time.monotonic()
    tmp_path: str | None = None

    try:
        tmp_path = await resolve_image_input(req.image_url, req.image_base64)

        from app.prototype.agents.vlm_critic import VLMCritic

        vlm = VLMCritic.get()
        if not vlm.available:
            raise HTTPException(status_code=503, detail="VLM service unavailable")

        # Direct VLM call with tradition-identification prompt (not score_image)
        tradition_list = ", ".join(t for t in _TRADITIONS if t != "default")
        try:
            result_text = await _call_vlm_tradition(vlm, tmp_path, tradition_list)
        except Exception:
            logger.exception("VLM tradition identification call failed")
            result_text = ""

        # Parse VLM response
        tradition = "default"
        confidence = 0.5
        alternatives: list[TraditionAlternative] = []

        parsed = _try_parse_tradition_json(result_text)
        if parsed:
            tradition = parsed.get("tradition", "default")
            confidence = parsed.get("confidence", 0.5)
            for alt in parsed.get("alternatives", []):
                alternatives.append(
                    TraditionAlternative(
                        tradition=alt.get("tradition", ""),
                        confidence=alt.get("confidence", 0.0),
                    )
                )

        # Validate tradition is known
        if tradition not in _TRADITIONS:
            tradition_lower = tradition.lower().replace(" ", "_")
            for t in _TRADITIONS:
                if tradition_lower in t or t in tradition_lower:
                    tradition = t
                    break
            else:
                tradition = "default"

        # Get recommended weights
        from app.prototype.cultural_pipelines.cultural_weights import get_weights

        weights = get_weights(tradition)
        labeled_weights = {
            _DIM_TO_LABEL.get(dim, dim): w for dim, w in weights.items()
        }

        elapsed_ms = int((time.monotonic() - t0) * 1000)

        return IdentifyTraditionResponse(
            tradition=tradition,
            confidence=round(confidence, 2),
            alternatives=alternatives,
            recommended_weights=labeled_weights,
            latency_ms=elapsed_ms,
        )

    except HTTPException:
        raise
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=400, detail=f"Image download failed: {exc.response.status_code}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Identify-tradition API error")
        raise HTTPException(status_code=500, detail=f"Internal error: {type(exc).__name__}") from exc
    finally:
        if tmp_path:
            cleanup_temp_image(tmp_path)


def _try_parse_tradition_json(text: str) -> dict | None:
    """Attempt to extract JSON object from VLM rationale text."""
    if not text:
        return None
    # Try direct parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    # Try extracting JSON from markdown code block
    for marker in ["```json", "```"]:
        if marker in text:
            start = text.index(marker) + len(marker)
            end = text.index("```", start) if "```" in text[start:] else len(text)
            try:
                return json.loads(text[start:end].strip())
            except (json.JSONDecodeError, ValueError):
                pass
    # Try finding { ... } substring
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end > brace_start:
        try:
            return json.loads(text[brace_start : brace_end + 1])
        except (json.JSONDecodeError, ValueError):
            pass
    return None


async def _call_vlm_tradition(vlm: object, image_path: str, tradition_list: str) -> str:
    """Direct LiteLLM call for tradition identification (bypasses score_image)."""
    import base64
    from pathlib import Path

    import litellm

    from app.prototype.agents.model_router import MODELS

    spec = MODELS.get("gemini_direct")
    if spec is None:
        return ""

    # Encode image
    img_bytes = Path(image_path).read_bytes()
    img_b64 = base64.b64encode(img_bytes).decode()
    suffix = Path(image_path).suffix.lower()
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(
        suffix.lstrip("."), "image/png"
    )

    system_prompt = (
        "You are an expert art historian. Analyze the artwork in the image and identify "
        "its cultural art tradition. Output ONLY valid JSON, no other text."
    )
    user_prompt = (
        f"Identify the cultural art tradition of this artwork. "
        f"Choose the best match from: {tradition_list}. "
        f'Respond as JSON: {{"tradition": "exact_id_from_list", "confidence": 0.XX, '
        f'"alternatives": [{{"tradition": "...", "confidence": 0.XX}}], '
        f'"reasoning": "brief explanation"}}'
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                {"type": "text", "text": user_prompt},
            ],
        },
    ]

    extra: dict = {}
    api_base = spec.get_api_base()
    api_key = spec.get_api_key()
    if api_base:
        extra["api_base"] = api_base
    if api_key:
        extra["api_key"] = api_key

    response = await litellm.acompletion(
        model=spec.litellm_id,
        messages=messages,
        max_tokens=4096,
        temperature=0.1,
        timeout=55,
        **extra,
    )
    return response.choices[0].message.content or ""
