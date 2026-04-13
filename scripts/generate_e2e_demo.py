"""Importable alias for generate-e2e-demo.py (hyphenated filename can't be imported directly)."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

_src = Path(__file__).resolve().parent / "generate-e2e-demo.py"
_spec = importlib.util.spec_from_file_location("scripts.generate_e2e_demo", _src)
_mod = importlib.util.module_from_spec(_spec)
sys.modules[__name__] = _mod  # replace this module in sys.modules
_spec.loader.exec_module(_mod)
