import asyncio
import json
import sys
import types
from pathlib import Path


def _run(coro):
    return asyncio.run(coro)


class _FastMCPStub:
    def __init__(self, *args, **kwargs):
        pass

    def tool(self, *args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

    def run(self):
        pass


def _install_fastmcp_stub(monkeypatch):
    module = types.ModuleType("fastmcp")
    module.FastMCP = _FastMCPStub
    monkeypatch.setitem(sys.modules, "fastmcp", module)


class _FakePipelineResult:
    def __init__(self, output_dir: Path, manifest_path: Path):
        self.status = "partial"
        self.manifest_path = manifest_path
        self.output_dir = output_dir
        self.reason = None
        self.detection_report = {
            "requested": 1,
            "detected": 0,
            "suspect": 0,
            "missed": 1,
            "success_rate": 0.0,
        }
        self.stage_timings = [{"stage": "total", "seconds": 0.01}]
        self.layers = [
            {
                "id": "layer_residual",
                "name": "residual",
                "semantic_path": "residual",
                "file": "residual.png",
                "z_index": 1,
                "content_type": "residual",
                "blend_mode": "normal",
                "quality_status": "residual",
                "area_pct": 100.0,
                "bbox": [0, 0, 20, 20],
                "parent_layer_id": None,
            }
        ]


def test_layers_split_orchestrated_appends_decompose_case(tmp_path, monkeypatch):
    _install_fastmcp_stub(monkeypatch)

    import vulca.pipeline.segment as segment_mod
    from vulca.mcp_server import layers_split

    source = tmp_path / "source.png"
    source.write_bytes(b"not-read-by-stub")
    out_dir = tmp_path / "layers"
    case_log = tmp_path / "decompose_cases.jsonl"
    plan = {
        "slug": "case-test",
        "domain": "news_photograph",
        "entities": [
            {
                "name": "subject",
                "label": "main subject",
                "semantic_path": "subject.main",
                "detector": "sam_bbox",
                "bbox_hint_pct": [0.1, 0.1, 0.9, 0.9],
            }
        ],
    }

    def _fake_run(plan_obj, image_path, output_dir, force=True):  # noqa: ARG001
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "residual.png").write_bytes(b"fake")
        (output_dir / "qa_prompt.md").write_text("review prompt")
        manifest_path = output_dir / "manifest.json"
        manifest = {
            "version": 5,
            "split_mode": "claude_orchestrated",
            "status": "partial",
            "layers": [
                {
                    "id": "layer_residual",
                    "name": "residual",
                    "semantic_path": "residual",
                    "file": "residual.png",
                    "z_index": 1,
                    "quality_status": "residual",
                    "area_pct": 100.0,
                    "bbox": [0, 0, 20, 20],
                    "parent_layer_id": None,
                }
            ],
            "detection_report": {
                "requested": 1,
                "detected": 0,
                "suspect": 0,
                "missed": 1,
                "success_rate": 0.0,
            },
        }
        manifest_path.write_text(json.dumps(manifest))
        return _FakePipelineResult(output_dir, manifest_path)

    monkeypatch.setattr(segment_mod, "run", _fake_run)

    result = _run(
        layers_split(
            image_path=str(source),
            output_dir=str(out_dir),
            mode="orchestrated",
            plan=json.dumps(plan),
            case_log_path=str(case_log),
        )
    )

    assert result["case_log_path"] == str(case_log)
    assert result["case_id"].startswith("decompose_")
    assert result["split_mode"] == "orchestrated"
    lines = case_log.read_text().splitlines()
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["case_id"] == result["case_id"]
    assert record["case_type"] == "decompose_case"
    assert record["input"]["source_image"] == str(source.resolve())
    assert record["input"]["requested"]["mode"] == "orchestrated"
    assert record["input"]["requested"]["tradition"] == "news_photograph"
    assert record["input"]["target_layer_hints"][0]["semantic_path"] == "subject.main"
    assert record["output"]["manifest_path"] == str(out_dir / "manifest.json")
    assert record["output"]["residual_path"] == str(out_dir / "residual.png")
    assert record["output"]["debug_artifacts"]["qa_prompt_path"] == str(
        out_dir / "qa_prompt.md"
    )
    assert record["quality"]["layer_coverage"]["residual_pct"] == 100.0
    assert record["review"]["preferred_action"] == ""
