"""VULCA custom nodes for ComfyUI.

Provides cultural art evaluation and Brief-driven creative workflows
inside ComfyUI's visual pipeline editor.

Requires: pip install vulca
"""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
from pathlib import Path


def _get_project_dir() -> str:
    """Get or create a project directory for VULCA sessions."""
    d = os.environ.get("VULCA_PROJECT_DIR", "")
    if not d:
        d = os.path.join(tempfile.gettempdir(), "vulca-comfyui")
    Path(d).mkdir(parents=True, exist_ok=True)
    return d


class VULCABriefNode:
    """Create a VULCA Studio Brief from text intent."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "intent": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "mood": ("STRING", {"default": ""}),
                "tradition": ("STRING", {"default": ""}),
                "must_have": ("STRING", {"default": "", "multiline": True}),
                "must_avoid": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("brief_path",)
    FUNCTION = "create_brief"
    CATEGORY = "VULCA"

    def create_brief(self, intent, mood="", tradition="", must_have="", must_avoid=""):
        from vulca.studio.brief import Brief
        from vulca.studio.types import StyleWeight
        from vulca.studio.phases.intent import IntentPhase

        style_mix = []
        if tradition:
            style_mix = [StyleWeight(tradition=tradition, weight=1.0)]

        mh = [x.strip() for x in must_have.split(",") if x.strip()] if must_have else []
        ma = [x.strip() for x in must_avoid.split(",") if x.strip()] if must_avoid else []

        b = Brief.new(intent, mood=mood, style_mix=style_mix, must_have=mh, must_avoid=ma)

        # Auto-detect traditions from intent
        phase = IntentPhase()
        phase.parse_intent(b)

        project_dir = _get_project_dir()
        b.save(project_dir)
        return (project_dir,)


class VULCAConceptNode:
    """Generate concept designs from a VULCA Brief."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "brief_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "count": ("INT", {"default": 4, "min": 1, "max": 8}),
                "provider": ("STRING", {"default": "mock"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("concept_paths_json",)
    FUNCTION = "generate_concepts"
    CATEGORY = "VULCA"

    def generate_concepts(self, brief_path, count=4, provider="mock"):
        from vulca.studio.brief import Brief
        from vulca.studio.phases.concept import ConceptPhase

        b = Brief.load(brief_path)
        phase = ConceptPhase()

        loop = asyncio.new_event_loop()
        try:
            paths = loop.run_until_complete(
                phase.generate_concepts(b, count=count, provider=provider, project_dir=brief_path)
            )
        finally:
            loop.close()
        b.save(brief_path)

        return (json.dumps(paths),)


class VULCAEvaluateNode:
    """Evaluate an image against VULCA Brief or tradition."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "brief_path": ("STRING", {"default": ""}),
                "tradition": ("STRING", {"default": "chinese_xieyi"}),
                "mock": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "FLOAT", "FLOAT", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("scores_json", "L1", "L2", "L3", "L4", "L5")
    FUNCTION = "evaluate"
    CATEGORY = "VULCA"

    def evaluate(self, image_path, brief_path="", tradition="chinese_xieyi", mock=True):
        if brief_path:
            # Brief-based evaluation
            from vulca.studio.brief import Brief
            from vulca.studio.phases.evaluate import EvaluatePhase

            b = Brief.load(brief_path)
            phase = EvaluatePhase()

            loop = asyncio.new_event_loop()
            try:
                scores = loop.run_until_complete(
                    phase.evaluate(b, image_path=image_path, mock=mock)
                )
            finally:
                loop.close()
        else:
            # Tradition-based evaluation (existing API)
            import vulca
            result = vulca.evaluate(image_path, tradition=tradition, mock=mock)
            scores = result.dimensions

        scores_json = json.dumps(scores, ensure_ascii=False)
        return (
            scores_json,
            float(scores.get("L1", 0.0)),
            float(scores.get("L2", 0.0)),
            float(scores.get("L3", 0.0)),
            float(scores.get("L4", 0.0)),
            float(scores.get("L5", 0.0)),
        )


class VULCAGenerateNode:
    """Generate artwork from a VULCA Brief."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "brief_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "provider": ("STRING", {"default": "mock"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("image_path",)
    FUNCTION = "generate"
    CATEGORY = "VULCA"

    def generate(self, brief_path, provider="mock"):
        from vulca.studio.brief import Brief
        from vulca.studio.phases.generate import GeneratePhase

        b = Brief.load(brief_path)
        phase = GeneratePhase()

        loop = asyncio.new_event_loop()
        try:
            path = loop.run_until_complete(
                phase.generate(b, provider=provider, project_dir=brief_path)
            )
        finally:
            loop.close()
        b.save(brief_path)

        return (path,)


class VULCAUpdateNode:
    """Update a VULCA Brief with natural language instruction."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "brief_path": ("STRING", {"default": ""}),
                "instruction": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("brief_path", "rollback_phase")
    FUNCTION = "update_brief"
    CATEGORY = "VULCA"

    def update_brief(self, brief_path, instruction):
        from vulca.studio.brief import Brief
        from vulca.studio.nl_update import parse_nl_update, apply_update

        b = Brief.load(brief_path)
        result = parse_nl_update(instruction, b)
        apply_update(b, result)
        b.save(brief_path)

        return (brief_path, result.rollback_to.value)


# ComfyUI registration
NODE_CLASS_MAPPINGS = {
    "VULCABrief": VULCABriefNode,
    "VULCAConcept": VULCAConceptNode,
    "VULCAEvaluate": VULCAEvaluateNode,
    "VULCAGenerate": VULCAGenerateNode,
    "VULCAUpdate": VULCAUpdateNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VULCABrief": "VULCA Brief (Create)",
    "VULCAConcept": "VULCA Concept (Design)",
    "VULCAEvaluate": "VULCA Evaluate (L1-L5)",
    "VULCAGenerate": "VULCA Generate (Artwork)",
    "VULCAUpdate": "VULCA Update (NL)",
}
