"""Test that HITL interrupt saves checkpoint with image."""
import asyncio
import base64
from pathlib import Path

from vulca.pipeline.engine import execute
from vulca.pipeline.templates import DEFAULT
from vulca.pipeline.types import PipelineInput


class TestHITLCheckpointSavesImage:
    def test_interrupt_before_decide_saves_checkpoint(self):
        """When pipeline pauses for HITL, checkpoint with image must be saved."""
        inp = PipelineInput(
            subject="Test HITL checkpoint",
            intent="Test HITL checkpoint",
            tradition="default",
            provider="mock",
        )
        loop = asyncio.new_event_loop()
        output = loop.run_until_complete(
            execute(DEFAULT, inp, interrupt_before={"decide"})
        )
        loop.close()

        assert output.status == "waiting_human"
        assert output.interrupted_at == "decide"

        # Checkpoint should exist with image
        from vulca.pipeline.checkpoint import CheckpointStore
        store = CheckpointStore()
        checkpoint = store.load_checkpoint(output.session_id)
        assert checkpoint is not None, "Checkpoint should exist after HITL interrupt"
        assert len(checkpoint["rounds"]) >= 1, "At least one round should be saved"

        latest_round = checkpoint["rounds"][-1]
        assert latest_round.get("image_ref") or latest_round.get("image_b64"), \
            "HITL checkpoint must contain image data"

        # If image_ref exists, the actual file should exist
        if latest_round.get("image_ref"):
            session_dir = Path(store._base) / output.session_id
            img_path = session_dir / latest_round["image_ref"]
            assert img_path.exists(), f"Image file should exist at {img_path}"
            assert img_path.stat().st_size > 0, "Image file should not be empty"

    def test_interrupt_preserves_scores(self):
        """HITL checkpoint should contain scores from evaluation."""
        inp = PipelineInput(
            subject="Test scores",
            intent="Test scores in checkpoint",
            tradition="default",
            provider="mock",
        )
        loop = asyncio.new_event_loop()
        output = loop.run_until_complete(
            execute(DEFAULT, inp, interrupt_before={"decide"})
        )
        loop.close()

        from vulca.pipeline.checkpoint import CheckpointStore
        store = CheckpointStore()
        checkpoint = store.load_checkpoint(output.session_id)
        latest = checkpoint["rounds"][-1]
        assert latest.get("decision") == "waiting_human"
        # Scores should be saved (from EvaluateNode running before decide)
        scores = latest.get("scores", {})
        assert len(scores) > 0, "Scores should be saved in checkpoint"
