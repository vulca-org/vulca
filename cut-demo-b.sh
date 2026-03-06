#!/bin/bash
# cut-demo-b.sh  ——  读取 demo-timestamps.json，精确剪掉 spinner，输出成品视频
#
# 用法：bash ./cut-demo-b.sh [raw.webm]
#       (不传参数则自动找最新 .webm)
#
# 输出：./vulca-demo-final.mp4
#
# 切段逻辑（3 段保留，2 段剪掉）：
#   Seg0: [0 → click_run + 3s]              ← 表单填写 + 点击 + 短暂 spinner
#   ✂  剪掉: [click_run+3s → scout-BUFFER]  ← spinner 1（~30s）
#   Seg1: [scout-BUFFER → scout_linger_end] ← Scout Evidence（停留 5s）
#   ✂  剪掉: [scout_linger_end → draft-BUF] ← spinner 2（~40s NB2 生图）
#   Seg2: [draft-BUFFER → recording_end]    ← Draft + Critic + Queen + Complete

set -e

FF=/home/yhryzy/.local/bin/ffmpeg
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT=$PROJECT_ROOT
TS_FILE="$OUT/demo-timestamps.json"
BUFFER=1.5   # 切点前后各留 1.5s 缓冲，避免硬切

# ── 检查输入 ─────────────────────────────────────────────────────
RAW="${1:-}"
if [ -z "$RAW" ]; then
  RAW=$(ls -t "$OUT"/*.webm 2>/dev/null | head -1)
fi

if [ -z "$RAW" ] || [ ! -f "$RAW" ]; then
  echo "❌ 找不到 webm 文件"
  echo "   用法: bash cut-demo-b.sh <raw.webm>"
  exit 1
fi

if [ ! -f "$TS_FILE" ]; then
  echo "❌ 找不到 $TS_FILE"
  echo "   请先运行 node record-demo-b.js"
  exit 1
fi

echo "🎬 输入: $(basename $RAW)"
echo "📊 读取时间戳..."

# ── Python helper：从 JSON 取一个字段的浮点值 ────────────────────
ts() { python3 -c "import json; print(json.load(open('$TS_FILE'))['$1'])"; }
calc() { python3 -c "print(round($1, 3))"; }

T_CLICK=$(ts click_run)
T_SCOUT=$(ts scout_appeared)
T_SCOUT_END=$(ts scout_linger_end)
T_DRAFT=$(ts draft_appeared)
T_END=$(ts recording_end)

printf "   %-22s %6ss\n" "click_run:"         "$T_CLICK"
printf "   %-22s %6ss\n" "scout_appeared:"    "$T_SCOUT"
printf "   %-22s %6ss\n" "scout_linger_end:"  "$T_SCOUT_END"
printf "   %-22s %6ss\n" "draft_appeared:"    "$T_DRAFT"
printf "   %-22s %6ss\n" "recording_end:"     "$T_END"

# ── 计算三段时间范围 ──────────────────────────────────────────────
SEG0_START=0
SEG0_END=$(calc "$T_CLICK + 3.0")

SEG1_START=$(calc "max(0.0, $T_SCOUT - $BUFFER)")
SEG1_END=$T_SCOUT_END

SEG2_START=$(calc "max(0.0, $T_DRAFT - $BUFFER)")
SEG2_END=$T_END

# 统计节省时长
CUT1=$(calc "round($T_SCOUT - $BUFFER - ($T_CLICK + 3.0), 1)")
CUT2=$(calc "round($T_DRAFT - $BUFFER - $T_SCOUT_END, 1)")
TOTAL_CUT=$(calc "round(float('$CUT1') + float('$CUT2'), 1)")
SEG_LEN=$(calc "round(float('$SEG0_END') + (float('$SEG1_END') - float('$SEG1_START')) + (float('$SEG2_END') - float('$SEG2_START')), 1)")

echo ""
echo "✂  切段方案:"
echo "   Seg0  [${SEG0_START}s → ${SEG0_END}s]     表单 + 点击"
echo "   ✗ cut [${SEG0_END}s → ${SEG1_START}s]    spinner 1 (~${CUT1}s)"
echo "   Seg1  [${SEG1_START}s → ${SEG1_END}s]  Scout Evidence"
echo "   ✗ cut [${SEG1_END}s → ${SEG2_START}s]   spinner 2 (~${CUT2}s)"
echo "   Seg2  [${SEG2_START}s → ${SEG2_END}s]   Draft + Critic + Queen + Complete"
echo ""
echo "   📐 总计剪掉: ${TOTAL_CUT}s → 剩余: ${SEG_LEN}s"
echo ""

# ── ffmpeg 一次 pass：trim + concat ──────────────────────────────
# 注意：SEG2 不指定 end（取到视频结尾）
echo "🎞️  剪辑中..."

$FF -y -i "$RAW" \
  -filter_complex "
    [0:v]trim=start=${SEG0_START}:end=${SEG0_END},setpts=PTS-STARTPTS[v0];
    [0:v]trim=start=${SEG1_START}:end=${SEG1_END},setpts=PTS-STARTPTS[v1];
    [0:v]trim=start=${SEG2_START}:end=${SEG2_END},setpts=PTS-STARTPTS[v2];
    [v0][v1][v2]concat=n=3:v=1:a=0[vout]
  " \
  -map "[vout]" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -movflags +faststart \
  "$OUT/vulca-demo-final.mp4" 2>&1 | grep -E "frame=|Lsize|error|Error" | tail -4

echo ""
echo "✅ 完成！"
$FF -i "$OUT/vulca-demo-final.mp4" 2>&1 | grep -E "Duration|Video:"
ls -lh "$OUT/vulca-demo-final.mp4"
echo ""
echo "📂 Windows: I:\\website\\vulca-demo-final.mp4"
