"""Per-artifact sidecar cache for layered generation.

Cache lives at <artifact_dir>/.layered_cache/<key>.png. No global cache,
no LRU, no eviction. Deletes when the artifact directory is deleted.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional


def build_cache_key(
    *,
    provider_id: str,
    model_id: str,
    prompt: str,
    canvas_color: str,
    canvas_tolerance: float,
    seed: int = 0,
    schema_version: str = "0.13",
    key_strategy: str = "",
    canvas_invert: bool = False,
    width: int = 0,
    height: int = 0,
) -> str:
    """Hash every input that can change the final RGBA bytes.

    Includes `key_strategy`, `canvas_invert` and `(width, height)` in addition
    to the original v0.13 inputs so that flipping any alpha-affecting knob or
    the raster dimensions invalidates the cached PNG.
    """
    h = hashlib.sha256()
    parts = [
        provider_id, model_id, prompt, canvas_color,
        f"{canvas_tolerance:.4f}", str(seed), schema_version,
        key_strategy, "1" if canvas_invert else "0",
        str(int(width)), str(int(height)),
    ]
    h.update("\x00".join(parts).encode("utf-8"))
    return h.hexdigest()


class LayerCache:
    def __init__(self, artifact_dir: Path | str | None, *, enabled: bool = True):
        self.enabled = enabled and artifact_dir is not None
        self.dir: Path | None = Path(artifact_dir) / ".layered_cache" if artifact_dir else None
        if self.enabled and self.dir is not None:
            self.dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[bytes]:
        if not self.enabled or self.dir is None:
            return None
        p = self.dir / f"{key}.png"
        if p.exists():
            return p.read_bytes()
        return None

    def put(self, key: str, data: bytes) -> None:
        if not self.enabled or self.dir is None:
            return
        (self.dir / f"{key}.png").write_bytes(data)
