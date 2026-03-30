"""Pipeline round checkpointing — save/load per-round state for resume and debugging."""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path
from typing import Any


class CheckpointStore:
    """Persist pipeline round state as JSONL + image files."""

    def __init__(self, data_dir: str = "") -> None:
        if not data_dir:
            data_dir = str(
                Path(os.environ.get("VULCA_DATA_DIR", "~/.vulca/data")).expanduser()
                / "checkpoints"
            )
        self._base = Path(data_dir)

    def save_metadata(self, session_id: str, metadata: dict[str, Any]) -> None:
        session_dir = self._base / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        meta = {"session_id": session_id, "created_at": int(time.time()), **metadata}
        (session_dir / "metadata.json").write_text(json.dumps(meta, indent=2))

    def save_round(self, session_id: str, round_num: int, ctx_data: dict[str, Any]) -> None:
        session_dir = self._base / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        record: dict[str, Any] = {"round_num": round_num, "timestamp": int(time.time())}

        image_b64 = ctx_data.pop("image_b64", None)
        if image_b64:
            img_filename = f"round{round_num}.png"
            img_path = session_dir / img_filename
            img_path.write_bytes(base64.b64decode(image_b64))
            record["image_ref"] = img_filename
        else:
            record["image_ref"] = ""

        for key in ("scores", "weighted_total", "candidate_id", "tradition", "eval_mode", "decision"):
            if key in ctx_data:
                record[key] = ctx_data[key]

        rounds_path = session_dir / "rounds.jsonl"
        with open(rounds_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")

    def load_checkpoint(self, session_id: str) -> dict[str, Any] | None:
        session_dir = self._base / session_id
        meta_path = session_dir / "metadata.json"
        if not meta_path.exists():
            return None
        metadata = json.loads(meta_path.read_text())
        rounds = self._load_rounds(session_dir)
        return {"metadata": metadata, "rounds": rounds}

    def get_round(self, session_id: str, round_num: int) -> dict[str, Any] | None:
        session_dir = self._base / session_id
        rounds = self._load_rounds(session_dir)
        for r in rounds:
            if r.get("round_num") == round_num:
                return r
        return None

    def list_sessions(self) -> list[str]:
        if not self._base.exists():
            return []
        return [d.name for d in self._base.iterdir() if d.is_dir() and (d / "metadata.json").exists()]

    def _load_rounds(self, session_dir: Path) -> list[dict[str, Any]]:
        rounds_path = session_dir / "rounds.jsonl"
        if not rounds_path.exists():
            return []
        rounds = []
        for line in rounds_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            image_ref = record.get("image_ref", "")
            if image_ref:
                img_path = session_dir / image_ref
                if img_path.exists():
                    record["image_b64"] = base64.b64encode(img_path.read_bytes()).decode()
            rounds.append(record)
        return rounds
