"""Explicit local Florence-2 runner for open-model signal records.

The runner is opt-in and produces reviewable signals only. It does not turn
model output into training labels.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol

from PIL import Image


DEFAULT_FLORENCE_MODEL_ID = "microsoft/Florence-2-base"


class FlorenceSignalBackend(Protocol):
    def run(
        self,
        image_path: str | Path,
        *,
        case_record: Mapping[str, Any],
        model_spec: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Run Florence on a local image and return raw signal fields."""


@dataclass(frozen=True)
class ResolvedSourceImage:
    path: Path | None
    ref_kind: str


def build_florence2_signal_runner(
    *,
    repo_root: str | Path,
    backend: FlorenceSignalBackend | None = None,
    model_id: str = DEFAULT_FLORENCE_MODEL_ID,
    device: str = "auto",
    allow_weight_download: bool = False,
) -> Any:
    """Build a local Florence-2 signal runner.

    ``allow_weight_download`` defaults to False, so the real backend uses
    local cached weights unless the caller explicitly opts into downloads.
    """
    root = Path(repo_root)
    resolved_backend = backend or Florence2LocalBackend(
        model_id=model_id,
        device=device,
        local_files_only=not allow_weight_download,
    )

    def run(example: Mapping[str, Any], model_spec: Mapping[str, Any]) -> dict[str, Any]:
        case_record = _case_record_from_example(example)
        source = resolve_case_source_image_path(case_record, repo_root=root)
        if source.path is None:
            return {
                "status": "skipped",
                "skip_reason": "source_image_unavailable",
                "signal_source": "local_runner",
                "label_source": "assistant_labeled",
                "review_status": "needs_human_review",
                "source_image": {
                    "available": False,
                    "ref_kind": source.ref_kind,
                },
            }

        image_info = _image_info(source.path)
        backend_signals = dict(
            resolved_backend.run(
                source.path,
                case_record=case_record,
                model_spec=model_spec,
            )
        )
        normalized = _normalize_backend_signals(backend_signals)
        normalized.update(
            {
                "status": "completed",
                "signal_source": "local_runner",
                "label_source": "assistant_labeled",
                "review_status": "needs_human_review",
                "source_image": {
                    "available": True,
                    "ref_kind": source.ref_kind,
                    "width": image_info["width"],
                    "height": image_info["height"],
                },
            }
        )
        return normalized

    return run


def resolve_case_source_image_path(
    case_record: Mapping[str, Any],
    *,
    repo_root: str | Path,
) -> ResolvedSourceImage:
    """Resolve a case source image to a local path without leaking private refs."""
    ref = _source_image_ref(case_record)
    if not ref:
        return ResolvedSourceImage(path=None, ref_kind="missing")
    ref_kind = _ref_kind(ref)
    if ref_kind in {"private_uri", "remote_url"}:
        return ResolvedSourceImage(path=None, ref_kind=ref_kind)

    candidate = Path(ref)
    if not candidate.is_absolute():
        candidate = Path(repo_root) / candidate
    if not candidate.exists():
        return ResolvedSourceImage(path=None, ref_kind=ref_kind)
    return ResolvedSourceImage(path=candidate, ref_kind=ref_kind)


class Florence2LocalBackend:
    """Lazy Florence-2 backend using transformers when explicitly enabled."""

    def __init__(
        self,
        *,
        model_id: str = DEFAULT_FLORENCE_MODEL_ID,
        device: str = "auto",
        local_files_only: bool = True,
        max_new_tokens: int = 256,
        num_beams: int = 3,
    ) -> None:
        self.model_id = model_id
        self.device = device
        self.local_files_only = local_files_only
        self.max_new_tokens = max_new_tokens
        self.num_beams = num_beams
        self._processor = None
        self._model = None
        self._torch = None

    def run(
        self,
        image_path: str | Path,
        *,
        case_record: Mapping[str, Any],
        model_spec: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        processor, model, torch, device = self._load()
        image = Image.open(image_path).convert("RGB")
        caption = self._run_task(
            "<CAPTION>",
            image=image,
            processor=processor,
            model=model,
            torch=torch,
            device=device,
        )
        ocr = self._run_task(
            "<OCR>",
            image=image,
            processor=processor,
            model=model,
            torch=torch,
            device=device,
        )
        return {
            "caption_candidates": _as_text_list(caption),
            "ocr_text": _as_text_list(ocr),
            "dense_region_descriptions": [],
        }

    def _load(self):
        if self._processor is not None and self._model is not None:
            return self._processor, self._model, self._torch, self._resolved_device()

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoProcessor
        except ImportError as exc:
            raise RuntimeError(
                "Florence-2 local runner requires transformers and torch. "
                "Install vulca[layers-full] or the equivalent optional deps."
            ) from exc

        device = self._resolved_device(torch)
        self._processor = AutoProcessor.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            local_files_only=self.local_files_only,
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            local_files_only=self.local_files_only,
            torch_dtype=torch.float32,
        ).to(device).eval()
        self._torch = torch
        return self._processor, self._model, self._torch, device

    def _resolved_device(self, torch_module=None) -> str:
        torch = torch_module or self._torch
        if self.device != "auto":
            return self.device
        if torch is None:
            return "cpu"
        if (
            getattr(torch.backends, "mps", None) is not None
            and torch.backends.mps.is_available()
        ):
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _run_task(
        self,
        task: str,
        *,
        image: Image.Image,
        processor,
        model,
        torch,
        device: str,
    ) -> Any:
        inputs = processor(text=task, images=image, return_tensors="pt")
        inputs = {
            key: value.to(device) if hasattr(value, "to") else value
            for key, value in inputs.items()
        }
        with torch.no_grad():
            generated = model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=self.max_new_tokens,
                num_beams=self.num_beams,
                do_sample=False,
            )
        decoded = processor.batch_decode(generated, skip_special_tokens=False)[0]
        parsed = processor.post_process_generation(
            decoded,
            task=task,
            image_size=image.size,
        )
        if isinstance(parsed, Mapping):
            return parsed.get(task, parsed)
        return parsed


def _case_record_from_example(example: Mapping[str, Any]) -> Mapping[str, Any]:
    input_block = example.get("input")
    if isinstance(input_block, Mapping):
        case_record = input_block.get("case_record")
        if isinstance(case_record, Mapping):
            return case_record
    return {}


def _source_image_ref(case_record: Mapping[str, Any]) -> str:
    direct = str(case_record.get("source_image") or "")
    if direct:
        return direct
    for key in ("input", "inputs"):
        nested = case_record.get(key)
        if isinstance(nested, Mapping):
            value = str(nested.get("source_image") or "")
            if value:
                return value
    return ""


def _ref_kind(ref: str) -> str:
    if not ref:
        return "missing"
    if ref.startswith("private://"):
        return "private_uri"
    if ref.startswith("http://") or ref.startswith("https://"):
        return "remote_url"
    if Path(ref).is_absolute():
        return "absolute_path"
    return "repo_relative"


def _image_info(path: Path) -> dict[str, int]:
    with Image.open(path) as image:
        return {"width": int(image.width), "height": int(image.height)}


def _normalize_backend_signals(signals: Mapping[str, Any]) -> dict[str, Any]:
    caption_candidates = _as_text_list(signals.get("caption_candidates"))
    ocr_text = _as_text_list(signals.get("ocr_text"))
    dense_region_descriptions = _as_text_list(signals.get("dense_region_descriptions"))
    return {
        "caption_candidates": caption_candidates,
        "ocr_text": ocr_text,
        "ocr_text_count": len(ocr_text),
        "dense_region_descriptions": dense_region_descriptions,
    }


def _as_text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Mapping):
        texts: list[str] = []
        for child in value.values():
            texts.extend(_as_text_list(child))
        return texts
    if isinstance(value, (list, tuple)):
        texts = []
        for item in value:
            texts.extend(_as_text_list(item))
        return texts
    return [str(value)]
