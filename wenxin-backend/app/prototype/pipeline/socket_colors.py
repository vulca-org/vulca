"""Socket color mapping for DataType — Art Professional palette.

Maps each DataType to a hex color for visual socket identification
in the node editor (ComfyUI-style typed handles).
"""

from __future__ import annotations

from app.prototype.pipeline.port_contract import DataType

# Art Professional palette colors
SOCKET_COLORS: dict[DataType, str] = {
    # Core pipeline types
    DataType.PIPELINE_INPUT: "#334155",       # 墨石灰
    DataType.EVIDENCE: "#6B7B8D",             # 石板灰
    DataType.EVIDENCE_PACK: "#6B7B8D",        # 石板灰
    DataType.DRAFT_CANDIDATES: "#C87F4A",     # 暖铜棕
    DataType.CRITIQUE: "#B8923D",             # 琥珀金
    DataType.PLAN_STATE: "#8B7355",           # 古铜色
    DataType.QUEEN_DECISION: "#9B6A8C",       # 紫藤色
    DataType.PIPELINE_OUTPUT: "#334155",      # 墨石灰
    DataType.ARCHIVE: "#5F8A50",              # 鼠尾草绿
    DataType.SKILL_RESULTS: "#5F8A50",        # 鼠尾草绿

    # New extended types
    DataType.IMAGE: "#C87F4A",                # 暖铜棕
    DataType.TEXT: "#6B7B8D",                 # 石板灰
    DataType.SKETCH: "#B8923D",               # 琥珀金
    DataType.MASK: "#8B7355",                 # 古铜色
    DataType.AUDIO: "#9B6A8C",               # 紫藤色
    DataType.VIDEO: "#C65D4D",               # 珊瑚红
    DataType.MODEL_3D: "#6B8E7A",            # 青铜绿
    DataType.CONFIG: "#334155",              # 墨石灰
    DataType.STYLE: "#DDA574",               # 暖铜浅
    DataType.SCORES: "#C65D4D",              # 珊瑚红
    DataType.DECISION: "#9B6A8C",            # 紫藤色
}


def get_socket_color(data_type: DataType) -> str:
    """Get the hex color for a DataType socket."""
    return SOCKET_COLORS.get(data_type, "#6B7B8D")


def get_all_socket_colors() -> dict[str, str]:
    """Get all socket colors as {data_type_value: hex_color} for API response."""
    return {dt.value: color for dt, color in SOCKET_COLORS.items()}
