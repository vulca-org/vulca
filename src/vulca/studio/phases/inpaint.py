"""InpaintPhase -- partial region redraw with Gemini blend."""
from __future__ import annotations

import re


def is_coordinate_string(region: str) -> bool:
    """Check if region string looks like coordinates (4 comma-separated numbers)."""
    parts = [p.strip() for p in region.split(",")]
    if len(parts) != 4:
        return False
    return all(p.lstrip("-").isdigit() for p in parts)


def parse_region_coordinates(region: str) -> dict:
    """Parse 'x,y,w,h' coordinate string to bbox dict. All values 0-100, w/h >= 5."""
    parts = [int(p.strip()) for p in region.split(",")]
    if len(parts) != 4:
        raise ValueError(f"Expected 4 values (x,y,w,h), got {len(parts)}")

    x, y, w, h = parts
    for name, val in [("x", x), ("y", y), ("w", w), ("h", h)]:
        if val < 0 or val > 100:
            raise ValueError(f"{name}={val} out of range 0-100")
    if w < 5 or h < 5:
        raise ValueError(f"Region too small: w={w}, h={h} (minimum 5%)")

    return {"x": x, "y": y, "w": w, "h": h}
