"""VULCA Digestion V2 — 4-layer session learning system.

Layer 0: Pre-session intelligence (preloader)
Layer 1: Real-time in-session preferences
Layer 2: Session completion trajectory analysis
Layer 3: Cross-session evolution
"""
from vulca.digestion.archiver import LocalArchiver
from vulca.digestion.artifact_analysis import ArtifactAnalysis
from vulca.digestion.evolver import detect_patterns, evolve_weights
from vulca.digestion.preferences import SessionPreferences
from vulca.digestion.preloader import preload_intelligence
from vulca.digestion.signals import accumulate_preferences, extract_action_signal
from vulca.digestion.storage import JsonlStudioStorage
from vulca.digestion.trajectory import build_session_digest

__all__ = [
    "JsonlStudioStorage",
    "ArtifactAnalysis",
    "SessionPreferences",
    "LocalArchiver",
    "extract_action_signal",
    "accumulate_preferences",
    "preload_intelligence",
    "detect_patterns",
    "evolve_weights",
    "build_session_digest",
]
