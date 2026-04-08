"""CompositeNode — blend layers into composite + write Artifact V3."""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from vulca.pipeline.node import PipelineNode, NodeContext
from vulca.layers.types import LayerResult
from vulca.layers.composite import composite_layers
from vulca.layers.artifact import write_artifact_v3
from vulca.layers.manifest import write_manifest


class CompositeNode(PipelineNode):
    """Blend all layers → composite image + Artifact V3 document."""

    name = "composite"

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        layer_results: list[LayerResult] = ctx.get("layer_results", [])
        import tempfile
        output_dir = ctx.get("output_dir", tempfile.mkdtemp(prefix="vulca_composite_"))
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        size = ctx.get("size", "1024x1024")
        w, h = _parse_size(size)

        valid = [r for r in layer_results if r.image_path and Path(r.image_path).exists()]
        failed = [r for r in layer_results if not r.image_path or not Path(r.image_path).exists()]

        composite_path = str(Path(output_dir) / "composite.png")
        if valid:
            composite_layers(valid, width=w, height=h, output_path=composite_path)
        else:
            from PIL import Image
            Image.new("RGBA", (w, h), (0, 0, 0, 0)).save(composite_path)

        with open(composite_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        # Build cultural context from pipeline data
        cultural_context = ctx.get("cultural_context")
        if not cultural_context:
            tradition_order = ctx.get("tradition_layer_order", [])
            cultural_context = {}
            if tradition_order:
                cultural_context["tradition_layer_order"] = tradition_order

        # Build rounds history
        rounds_history = ctx.get("rounds_history", [])
        if not rounds_history:
            rounds_history = [{
                "round": ctx.round_num or 1,
                "layers_generated": [r.info.name for r in layer_results if r.image_path],
                "layers_kept": [],
                "decision": "pending",
            }]

        # Collect per-layer scores
        layer_scores = {r.info.name: r.scores for r in layer_results if r.scores}

        artifact_path = write_artifact_v3(
            layers=[r.info for r in layer_results],
            output_dir=output_dir,
            width=w, height=h,
            intent=ctx.intent or ctx.subject,
            tradition=ctx.tradition,
            composite_file="composite.png",
            composite_scores=ctx.get("composite_scores"),
            cultural_context=cultural_context,
            rounds=rounds_history,
            session_id=ctx.get("session_id", ""),
            layer_scores=layer_scores,
        )

        # v0.13: write manifest.json with layered metadata.
        # generation_path is "a" (native library) when layered_result is present,
        # otherwise "b" (legacy VLM-mask split path).
        layered_result = ctx.get("layered_result")
        try:
            from vulca.cultural.loader import get_tradition
            trad = get_tradition(ctx.tradition or "default")
            layerability = getattr(trad, "layerability", "") or ""
        except Exception:
            layerability = ""

        def _validation_dict(v):
            warn_dicts = [
                {"kind": w.kind, "message": w.message, "detail": w.detail}
                for w in v.warnings
            ]
            return {
                "ok": v.ok,
                "warnings": warn_dicts,
                "coverage_actual": v.coverage_actual,
                "position_iou": v.position_iou,
            }, warn_dicts

        warnings: list[str] = []
        layer_extras: dict[str, dict] = {}
        # P0.1 #3: always record canvas_color + key_strategy on A-path extras.
        trad_canvas_color = ""
        trad_key_strategy = ""
        if layered_result is not None:
            try:
                from vulca.cultural.loader import get_tradition as _gt
                _t = _gt(ctx.tradition or "default")
                trad_canvas_color = getattr(_t, "canvas_color", "") or ""
                trad_key_strategy = getattr(_t, "key_strategy", "") or ""
            except Exception:
                pass
        if layered_result is not None:
            for o in layered_result.layers:
                extra: dict = {
                    "source": "a",
                    "status": "ok",
                    "cache_hit": bool(o.cache_hit),
                    "attempts": o.attempts,
                    "canvas_color": trad_canvas_color,
                    "key_strategy": trad_key_strategy,
                }
                if o.validation is not None:
                    vd, warn_dicts = _validation_dict(o.validation)
                    extra["validation"] = vd
                    warnings.extend(w["message"] for w in warn_dicts)
                layer_extras[o.info.id] = extra

            # P0 #2: also write extras for failed layers so retry can find them
            # and so the manifest records the validation report that explains why.
            for f in layered_result.failed:
                extra = {
                    "source": "a",
                    "status": "failed",
                    "reason": f.reason,
                    "attempts": f.attempts,
                    "canvas_color": trad_canvas_color,
                    "key_strategy": trad_key_strategy,
                }
                if f.validation is not None:
                    vd, warn_dicts = _validation_dict(f.validation)
                    extra["validation"] = vd
                    warnings.extend(w["message"] for w in warn_dicts)
                layer_extras[f.layer_id] = extra

        write_manifest(
            [r.info for r in layer_results],
            output_dir=output_dir,
            width=w, height=h,
            generation_path=("a" if layered_result is not None else "b"),
            layerability=layerability,
            partial=(not layered_result.is_complete) if layered_result is not None else bool(failed),
            warnings=warnings,
            layer_extras=layer_extras,
            # P0.1: persist tradition so `layers retry` can recover the
            # correct anchor/canvas/keying without operator guesswork.
            tradition=ctx.tradition or "",
        )

        return {
            "image_b64": image_b64,
            "composite_path": composite_path,
            "artifact_path": artifact_path,
            "failed_layers": [r.info.name for r in failed],
        }


def _parse_size(size: str) -> tuple[int, int]:
    if "x" in size:
        parts = size.split("x")
        return int(parts[0]), int(parts[1])
    s = int(size)
    return s, s
