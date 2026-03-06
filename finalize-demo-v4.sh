#!/usr/bin/env bash
# finalize-demo-v4.sh  (v5 — A+C 重构)
# Stage文字 → Progress dots；Narr → 研究背景解读；删Logo；DataTag不变
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
WORK=$PROJECT_ROOT
FF=/home/yhryzy/.local/bin/ffmpeg
INPUT="$WORK/vulca-demo-with-audio.mp4"
ASS="$WORK/demo_subtitles_v4.ass"
OUTPUT="$WORK/vulca-demo-v4-final.mp4"

echo "=== finalize-demo-v4.sh (v5 A+C) ==="
echo "Input : $INPUT"
echo "Output: $OUTPUT"
echo

[[ -f "$INPUT" ]] || { echo "ERROR: 源视频不存在"; exit 1; }
[[ -x "$FF"    ]] || { echo "ERROR: ffmpeg不存在: $FF"; exit 1; }
echo "[1/3] 前提检查 OK"

# ── 信息层设计 ──────────────────────────────────────────────────────────────
# DataTag  (\an6 右中)   数值弹出，琥珀黄，24pt，不变
#   → 屏幕上没有的关键数字（得分/成本/消融结果）
#
# Narr     (\an2 底中)   研究背景解读，奶油白，20pt，深色背景框
#   → 说观众不知道的：算法机制、框架设计、论文贡献
#   → 不重复原型UI已经显示的阶段名/操作描述
#
# Logo: 已删除（ffmpeg filter 简化）
#
# 颜色：
#   琥珀黄  #D4A84B → &H004BA8D4
#   深铜棕  #6B4E2C → &H002C4E6B
#   奶油白  #F5F0EB → &H00EBF0F5
#   半透黑  alpha=0x88 → &H88000000

cat > "$ASS" << 'ASSEOF'
[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
Timer: 100.0000
; v5 – DataTag (8 events) + Narr (8 events, stage-aligned) + No Logo

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: DataTag,Arial,24,&H004BA8D4,&H000000FF,&H002C4E6B,&H00000000,1,0,0,0,100,100,0,0,1,2,0,6,20,20,0,1
Style: Narr,WenQuanYi Zen Hei,20,&H00EBF0F5,&H000000FF,&H00000000,&H88000000,0,0,0,0,100,100,0,0,3,1,0,2,20,20,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

; ─── DataTag（不变，效果已验证）──────────────────────────────────────────────
Dialogue: 0,0:00:16.00,0:00:18.50,DataTag,,0,0,0,,{\an6\pos(1264,360)\fad(300,200)\t(0,200,\fscx112\fscy112)\t(200,400,\fscx100\fscy100)}3 Matches · 5 Terms · 0 Taboo
Dialogue: 0,0:00:20.50,0:00:22.50,DataTag,,0,0,0,,{\an6\pos(1264,360)\fad(300,200)\t(0,200,\fscx112\fscy112)\t(200,400,\fscx100\fscy100)}7,410 samples retrieved
Dialogue: 0,0:00:24.00,0:00:26.00,DataTag,,0,0,0,,{\an6\pos(1264,360)\fad(300,200)\t(0,200,\fscx112\fscy112)\t(200,400,\fscx100\fscy100)}2 candidates · NB2 generated
Dialogue: 0,0:00:40.00,0:00:43.00,DataTag,,0,0,0,,{\an6\pos(1264,360)\fad(300,200)\t(0,200,\fscx112\fscy112)\t(200,400,\fscx100\fscy100)}Score: 0.9517  ✓ ACCEPT
Dialogue: 0,0:00:43.00,0:00:46.00,DataTag,,0,0,0,,{\an6\pos(1264,360)\fad(300,200)\t(0,200,\fscx112\fscy112)\t(200,400,\fscx100\fscy100)}118.7s · $0.134 / run
Dialogue: 0,0:00:49.00,0:00:52.00,DataTag,,0,0,0,,{\an6\pos(1264,360)\fad(300,200)\t(0,200,\fscx112\fscy112)\t(200,400,\fscx100\fscy100)}Baseline: 0.810
Dialogue: 0,0:00:55.50,0:00:58.00,DataTag,,0,0,0,,{\an6\pos(1264,360)\fad(300,200)\t(0,200,\fscx112\fscy112)\t(200,400,\fscx100\fscy100)}G Full System: 0.915
Dialogue: 0,0:00:58.00,0:01:00.50,DataTag,,0,0,0,,{\an6\pos(1264,360)\fad(300,200)\t(0,200,\fscx112\fscy112)\t(200,400,\fscx100\fscy100)}+13.0%  ↑  480 runs verified

; ─── Narr（与实际阶段对齐，pos上移至y=672避开底部Stage bar）──────────────
; 每条内容严格匹配该时段的屏幕画面，\N硬换行
Dialogue: 0,0:00:00.00,0:00:02.50,Narr,,0,0,0,,{\an2\pos(640,672)\fad(150,100)}VULCA — 文化感知 AI 艺术生成评测系统\NVULCA: AI art evaluation with cultural intelligence
Dialogue: 0,0:00:02.50,0:00:13.00,Narr,,0,0,0,,{\an2\pos(640,672)\fad(150,100)}NB2：具备文化感知能力的多模态图像生成器\NNB2: culturally-aware multimodal image generator
Dialogue: 0,0:00:13.00,0:00:22.00,Narr,,0,0,0,,{\an2\pos(640,672)\fad(150,100)}VULCA-Bench：L1-L5 五层定义，7,410 人工标注样本\NVULCA-Bench: L1-L5 hierarchy · 7,410 labeled samples
Dialogue: 0,0:00:22.00,0:00:28.00,Narr,,0,0,0,,{\an2\pos(640,672)\fad(150,100)}种子多样性采样，保障候选图像风格覆盖度\NDiversity seeding ensures candidate style coverage
Dialogue: 0,0:00:28.00,0:00:32.00,Narr,,0,0,0,,{\an2\pos(640,672)\fad(150,100)}VLM 70% + 规则锚定 30%，L1-L5 五维加权评分\NVLM 70% + rule-based 30%: L1-L5 weighted scoring
Dialogue: 0,0:00:32.00,0:00:43.00,Narr,,0,0,0,,{\an2\pos(640,672)\fad(150,100)}Queen 决策：加权得分 ≥ 0.93 早停，接受最优候选\NQueen: weighted score ≥ 0.93 → early stop, accept best
Dialogue: 0,0:00:43.00,0:00:55.00,Narr,,0,0,0,,{\an2\pos(640,672)\fad(150,100)}端到端完成：118.7s · $0.134 / 次，Round 1 单轮接受\NEnd-to-end: 118.7s · $0.134 per run · accepted round 1
Dialogue: 0,0:00:55.00,0:01:00.76,Narr,,0,0,0,,{\an2\pos(640,672)\fad(200,150)}480 次验证：框架效应 73%，生成器效应 27%\N480 runs: framework 73% vs generator 27% of gain
ASSEOF

echo "[2/3] ASS字幕文件已生成 ($(wc -l < "$ASS") 行)"

# ── ffmpeg — 无Logo，仅ASS字幕叠加 ───────────────────────────────────────────
echo "[3/3] 开始 ffmpeg 渲染（无Logo overlay）..."

$FF -y \
  -i "$INPUT" \
  -vf "ass=${ASS}" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p \
  -c:a copy -t 60.76 -movflags +faststart \
  "$OUTPUT"

echo
echo "✅  完成！"
ls -lh "$OUTPUT"
$FF -i "$OUTPUT" 2>&1 | grep -E "Duration|Video:|Audio:" | sed 's/^/   /' || true
