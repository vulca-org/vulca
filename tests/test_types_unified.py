"""Tests for unified type system -- scoring, pipeline, cultural, media types."""

from __future__ import annotations

import pytest


# -- Scoring Types ---------------------------------------------------------


class TestScoringTypes:
    def test_layer_id_enum(self):
        from vulca.scoring.types import LayerID
        assert LayerID.L1.value == "visual_perception"
        assert LayerID.L5.value == "philosophical_aesthetic"
        assert len(LayerID) == 5

    def test_dimensions_list(self):
        from vulca.scoring.types import DIMENSIONS
        assert len(DIMENSIONS) == 5
        assert "visual_perception" in DIMENSIONS
        assert "cultural_context" in DIMENSIONS

    def test_dimension_score(self):
        from vulca.scoring.types import DimensionScore
        ds = DimensionScore(layer_id="visual_perception", score=0.85, rationale="Good")
        assert ds.score == 0.85
        d = ds.to_dict()
        assert d["layer_id"] == "visual_perception"
        assert d["score"] == 0.85

    def test_critique_output(self):
        from vulca.scoring.types import CritiqueOutput
        co = CritiqueOutput(
            candidate_id="c1",
            dimension_scores={"visual_perception": 0.8, "cultural_context": 0.7},
            weighted_total=0.75,
            passed=True,
        )
        assert co.passed
        assert co.weighted_total == 0.75
        d = co.to_dict()
        assert d["candidate_id"] == "c1"
        assert d["passed"] is True

    def test_critic_config_defaults(self):
        from vulca.scoring.types import CriticConfig
        cc = CriticConfig()
        assert abs(sum(cc.weights.values()) - 1.0) < 0.01
        assert cc.pass_threshold == 0.4
        assert cc.min_dimension_score == 0.2
        assert cc.use_vlm is True

    def test_layer_state(self):
        from vulca.scoring.types import LayerState
        ls = LayerState(layer_id="visual_perception")
        assert ls.score == 0.0
        assert ls.confidence == 0.0

        ls.record_score(0.7)
        assert ls.score == 0.7

        ls.record_score(0.8)
        assert ls.score == 0.8
        assert ls.volatility > 0

    def test_layer_state_priority(self):
        from vulca.scoring.types import LayerState
        ls = LayerState(layer_id="L1", confidence=0.2)
        high_pri = ls.priority()

        ls2 = LayerState(layer_id="L2", confidence=0.9)
        low_pri = ls2.priority()

        assert high_pri > low_pri


# -- Pipeline Types --------------------------------------------------------


class TestPipelineTypes:
    def test_run_status_enum(self):
        from vulca.pipeline.types import RunStatus
        assert RunStatus.PENDING == "pending"
        assert RunStatus.COMPLETED == "completed"

    def test_event_type_enum(self):
        from vulca.pipeline.types import EventType
        assert EventType.STAGE_STARTED == "stage_started"
        assert EventType.PIPELINE_COMPLETED == "pipeline_completed"

    def test_pipeline_event(self):
        from vulca.pipeline.types import PipelineEvent, EventType
        ev = PipelineEvent(event_type=EventType.STAGE_STARTED, stage="scout", round_num=1)
        d = ev.to_dict()
        assert d["event_type"] == "stage_started"
        assert d["stage"] == "scout"

    def test_round_snapshot(self):
        from vulca.pipeline.types import RoundSnapshot
        rs = RoundSnapshot(round_num=1, weighted_total=0.75, decision="accept")
        assert rs.round_num == 1
        d = rs.to_dict()
        assert d["weighted_total"] == 0.75

    def test_pipeline_input(self):
        from vulca.pipeline.types import PipelineInput
        pi = PipelineInput(subject="ink wash mountain", tradition="chinese_xieyi")
        assert pi.subject == "ink wash mountain"
        assert pi.tradition == "chinese_xieyi"
        assert pi.max_rounds == 3
        assert pi.provider == "nb2"

    def test_pipeline_output(self):
        from vulca.pipeline.types import PipelineOutput, RoundSnapshot
        po = PipelineOutput(
            session_id="s1",
            tradition="chinese_xieyi",
            weighted_total=0.82,
            rounds=[RoundSnapshot(round_num=1, weighted_total=0.82, decision="accept")],
            total_rounds=1,
        )
        d = po.to_dict()
        assert d["session_id"] == "s1"
        assert len(d["rounds"]) == 1

    def test_pipeline_definition(self):
        from vulca.pipeline.types import PipelineDefinition
        pd = PipelineDefinition(name="default")
        assert pd.entry_point == "scout"
        assert "scout" in pd.nodes
        assert "queen" in pd.nodes
        d = pd.to_dict()
        assert d["name"] == "default"
        assert d["enable_loop"] is True

    def test_pipeline_definition_frozen(self):
        from vulca.pipeline.types import PipelineDefinition
        pd = PipelineDefinition(name="test")
        with pytest.raises(AttributeError):
            pd.name = "changed"

    def test_pipeline_definition_serializes(self):
        from vulca.pipeline.types import PipelineDefinition
        pd = PipelineDefinition(name="test")
        d = pd.to_dict()
        assert d["name"] == "test"
        assert "enable_loop" in d


# -- Cultural Types --------------------------------------------------------


class TestCulturalTypes:
    def test_term_entry(self):
        from vulca.cultural.types import TermEntry
        te = TermEntry(term="xieyi", term_zh="\u5199\u610f", category="style")
        assert te.term == "xieyi"
        d = te.to_dict()
        assert d["term_zh"] == "\u5199\u610f"

    def test_taboo_entry(self):
        from vulca.cultural.types import TabooEntry
        tb = TabooEntry(rule="No figural representation", severity="high")
        assert tb.severity == "high"

    def test_tradition_config(self):
        from vulca.cultural.types import TraditionConfig
        tc = TraditionConfig(
            name="chinese_xieyi",
            display_name={"en": "Xieyi", "zh": "\u5199\u610f"},
            weights_l={"L1": 0.10, "L2": 0.15, "L3": 0.25, "L4": 0.20, "L5": 0.30},
        )
        assert tc.name == "chinese_xieyi"
        assert abs(sum(tc.weights_l.values()) - 1.0) < 0.01

    def test_tradition_config_weights_dim(self):
        from vulca.cultural.types import TraditionConfig
        tc = TraditionConfig(
            name="default",
            weights_l={"L1": 0.15, "L2": 0.20, "L3": 0.25, "L4": 0.20, "L5": 0.20},
        )
        wd = tc.weights_dim
        assert "visual_perception" in wd
        assert wd["cultural_context"] == 0.25

    def test_tradition_config_to_dict(self):
        from vulca.cultural.types import TraditionConfig, TermEntry
        tc = TraditionConfig(
            name="test",
            terminology=[TermEntry(term="test_term")],
        )
        d = tc.to_dict()
        assert d["name"] == "test"
        assert len(d["terminology"]) == 1

    def test_pipeline_config(self):
        from vulca.cultural.types import PipelineConfig
        pc = PipelineConfig(variant="fast_draft", overrides={"max_rounds": 1})
        assert pc.variant == "fast_draft"


# -- Media Types -----------------------------------------------------------


class TestMediaTypes:
    def test_media_type_enum(self):
        from vulca.media.types import MediaType
        assert MediaType.IMAGE == "image"
        assert MediaType.VIDEO == "video"
        assert MediaType.MODEL_3D == "3d_model"
        assert MediaType.SOUND == "sound"

    def test_sub_stage_def(self):
        from vulca.media.types import SubStageDef
        ssd = SubStageDef(
            name="mood_palette",
            display_name="Mood Palette",
            description="Generate color palette",
            order=1,
        )
        assert ssd.name == "mood_palette"
        d = ssd.to_dict()
        assert d["order"] == 1

    def test_sub_stage_def_frozen(self):
        from vulca.media.types import SubStageDef
        ssd = SubStageDef(name="x", display_name="X", description="X", order=0)
        with pytest.raises(AttributeError):
            ssd.name = "changed"

    def test_sub_stage_artifact(self):
        from vulca.media.types import SubStageArtifact
        a = SubStageArtifact(stage_name="sketch", artifact_type="image", image_path="/tmp/s.png")
        d = a.to_dict()
        assert d["image_path"] == "/tmp/s.png"

    def test_sub_stage_result(self):
        from vulca.media.types import SubStageResult
        r = SubStageResult(stage_name="final_render", status="completed", duration_ms=8000)
        d = r.to_dict()
        assert d["status"] == "completed"

    def test_creation_recipe(self):
        from vulca.media.types import CreationRecipe, MediaType, SubStageDef
        recipe = CreationRecipe(
            media_type=MediaType.IMAGE,
            name="image_standard",
            display_name="Standard Image Pipeline",
            sub_stages=(
                SubStageDef(name="sketch", display_name="Sketch", description="Rough sketch", order=1),
                SubStageDef(name="render", display_name="Render", description="Final render", order=2),
            ),
        )
        assert recipe.media_type == MediaType.IMAGE
        assert len(recipe.stage_names()) == 2
        assert recipe.get_stage_by_name("sketch") is not None
        assert recipe.get_stage_by_name("nonexistent") is None

    def test_creation_recipe_validates_order(self):
        from vulca.media.types import CreationRecipe, MediaType, SubStageDef
        with pytest.raises(ValueError, match="ascending order"):
            CreationRecipe(
                media_type=MediaType.IMAGE,
                name="bad",
                display_name="Bad",
                sub_stages=(
                    SubStageDef(name="b", display_name="B", description="B", order=2),
                    SubStageDef(name="a", display_name="A", description="A", order=1),
                ),
            )

    def test_creation_recipe_validates_unique_names(self):
        from vulca.media.types import CreationRecipe, MediaType, SubStageDef
        with pytest.raises(ValueError, match="unique"):
            CreationRecipe(
                media_type=MediaType.IMAGE,
                name="dup",
                display_name="Dup",
                sub_stages=(
                    SubStageDef(name="same", display_name="A", description="A", order=1),
                    SubStageDef(name="same", display_name="B", description="B", order=2),
                ),
            )

    def test_creation_recipe_frozen(self):
        from vulca.media.types import CreationRecipe, MediaType, SubStageDef
        recipe = CreationRecipe(
            media_type=MediaType.IMAGE,
            name="test",
            display_name="Test",
            sub_stages=(
                SubStageDef(name="s1", display_name="S1", description="S1", order=1),
            ),
        )
        with pytest.raises(AttributeError):
            recipe.name = "changed"
