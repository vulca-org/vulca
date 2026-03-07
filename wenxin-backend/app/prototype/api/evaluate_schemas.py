"""Pydantic schemas for the B2B evaluate API (M4)."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class EvaluateRequest(BaseModel):
    """POST /api/v1/evaluate — cultural art evaluation request."""

    image_url: str | None = Field(default=None, description="HTTP(S) image URL")
    image_base64: str | None = Field(default=None, description="Base64-encoded image data")
    tradition: str = Field(default="default", description="Cultural tradition identifier")
    subject: str = Field(default="", description="Artwork subject description")
    include_evidence: bool = Field(default=False, description="Run Scout evidence gathering")
    intent: str | None = Field(default=None, description="Natural language evaluation intent")

    @model_validator(mode="after")
    def _require_image(self) -> EvaluateRequest:
        if not self.image_url and not self.image_base64:
            raise ValueError("Either image_url or image_base64 must be provided")
        return self


class DimensionDetail(BaseModel):
    """Single L1-L5 dimension score with rationale."""

    score: float
    rationale: str = ""


class EvaluateResponse(BaseModel):
    """POST /api/v1/evaluate — evaluation result."""

    scores: dict[str, float] = Field(description="L1-L5 scores, e.g. {'L1': 0.85, ...}")
    rationales: dict[str, str] = Field(description="Per-dimension rationale text")
    weighted_total: float
    tradition_used: str
    cultural_diagnosis: str = Field(default="", description="VLM综合诊断")
    recommendations: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list, description="Cultural taboo/risk flags")
    evidence_summary: dict | None = Field(default=None, description="Scout evidence if requested")
    intent_resolved: dict | None = Field(default=None, description="Resolved intent details")
    result_card: dict | None = Field(default=None, description="Formatted result card")
    latency_ms: int
    cost_usd: float = 0.0


class IdentifyTraditionRequest(BaseModel):
    """POST /api/v1/identify-tradition — auto-detect cultural tradition."""

    image_url: str | None = Field(default=None, description="HTTP(S) image URL")
    image_base64: str | None = Field(default=None, description="Base64-encoded image data")

    @model_validator(mode="after")
    def _require_image(self) -> IdentifyTraditionRequest:
        if not self.image_url and not self.image_base64:
            raise ValueError("Either image_url or image_base64 must be provided")
        return self


class TraditionAlternative(BaseModel):
    """Alternative tradition match."""

    tradition: str
    confidence: float


class IdentifyTraditionResponse(BaseModel):
    """POST /api/v1/identify-tradition — tradition identification result."""

    tradition: str
    confidence: float
    alternatives: list[TraditionAlternative] = Field(default_factory=list)
    recommended_weights: dict[str, float] = Field(
        default_factory=dict,
        description="Recommended L1-L5 weights for the identified tradition",
    )
    latency_ms: int


# ── Knowledge-base browse schemas ─────────────────────────────────


class TermItem(BaseModel):
    """A single cultural terminology entry."""

    id: str
    term_zh: str
    term_en: str
    definition: str
    category: str
    l_levels: list[str]
    aliases: list[str] = Field(default_factory=list)
    source: str = ""


class TabooRuleItem(BaseModel):
    """A single cultural taboo rule."""

    rule_id: str
    cultural_tradition: str = Field(description="Tradition id or '*' for universal")
    description: str
    severity: str
    trigger_patterns: list[str] = Field(default_factory=list)
    explanation: str = ""
    l_levels: list[str] = Field(default_factory=list)
    source: str = ""


class PipelineVariantInfo(BaseModel):
    """Pipeline variant summary for a tradition."""

    variant_name: str
    description: str
    scout_focus_layers: list[str] = Field(default_factory=list)
    allow_local_rerun: bool = True
    critic_stages: list[list[str]] = Field(default_factory=list)


class TraditionEntry(BaseModel):
    """Full knowledge-base entry for one cultural tradition."""

    tradition: str
    terms: list[TermItem] = Field(default_factory=list)
    taboo_rules: list[TabooRuleItem] = Field(default_factory=list)
    weights: dict[str, float] = Field(
        description="L1-L5 weights (dim_id → weight), sums to 1.0",
    )
    pipeline_variant: PipelineVariantInfo


class KnowledgeBaseSummary(BaseModel):
    """Aggregate statistics for the knowledge base."""

    total_traditions: int
    total_terms: int
    total_taboo_rules: int


class KnowledgeBaseResponse(BaseModel):
    """GET /api/v1/knowledge-base — full cultural knowledge-base browse response."""

    traditions: list[TraditionEntry]
    summary: KnowledgeBaseSummary
