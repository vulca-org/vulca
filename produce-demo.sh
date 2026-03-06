#!/bin/bash
# produce-demo.sh  ——  产制版 VULCA Demo（字幕 + 分段变速 + 结果卡片）
#
# 输入：
#   $1  原始 webm（默认自动找最新的）
#   $2  timestamps.json（默认 demo-timestamps.json）
# 输出：
#   ./vulca-demo-produced.mp4   (~55s)
#
# 用法：bash ./produce-demo.sh [raw.webm] [timestamps.json]
set -e

FF=/home/yhryzy/.local/bin/ffmpeg
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT=$PROJECT_ROOT
FONT_BOLD=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf

# ── 输入文件 ──────────────────────────────────────────────────────
RAW="${1:-$(ls -t $OUT/*.webm 2>/dev/null | head -1)}"
TS_FILE="${2:-$OUT/demo-timestamps.json}"

[ -z "$RAW" ] || [ ! -f "$RAW" ] && echo "❌ 找不到 webm" && exit 1
[ ! -f "$TS_FILE" ] && echo "❌ 找不到 $TS_FILE" && exit 1

echo "🎬 输入: $(basename $RAW)"

# ── 读取时间戳 ────────────────────────────────────────────────────
py() { python3 -c "$1"; }
ts() { py "import json; print(json.load(open('$TS_FILE'))['$1'])"; }

T_CLICK=$(ts click_run)
T_SCOUT=$(ts scout_appeared)
T_SCOUT_END=$(ts scout_linger_end)
T_DRAFT=$(ts draft_appeared)
T_COMPLETE=$(ts complete)
T_END=$(ts recording_end)
BUF=1.5

# ── 在原始视频坐标中定义各段 ──────────────────────────────────────
# Seg0: 表单填写  [0 → T_CLICK+3]   → 2x 加速
# Seg1: Scout    [T_SCOUT-BUF → T_SCOUT_END]  → 1x
# Seg2: Draft出现 [T_DRAFT-BUF → T_DRAFT+2.5]  → 1x
# Seg3: Critic   [T_DRAFT+2.5 → T_COMPLETE-2]  → 4x 加速
# Seg4: 结果滚屏  [T_COMPLETE-2 → T_END]  → 1x

SEG0_S=0
SEG0_E=$(py "print(round($T_CLICK + 3.0, 2))")

SEG1_S=$(py "print(round(max(0, $T_SCOUT - $BUF), 2))")
SEG1_E=$T_SCOUT_END

SEG2_S=$(py "print(round(max(0, $T_DRAFT - $BUF), 2))")
SEG2_E=$(py "print(round($T_DRAFT + 2.5, 2))")

SEG3_S=$(py "print(round($T_DRAFT + 2.5, 2))")
SEG3_E=$(py "print(round($T_COMPLETE - 2.0, 2))")

SEG4_S=$(py "print(round($T_COMPLETE - 2.0, 2))")
SEG4_E=$T_END

# ── 计算各段在最终视频中的时长 ────────────────────────────────────
# 注意：2x 加速 → 时长/2，4x → 时长/4
D0=$(py "print(round(($SEG0_E - $SEG0_S) / 2.0, 2))")     # 2x
D1=$(py "print(round($SEG1_E - $SEG1_S, 2))")              # 1x
D2=$(py "print(round($SEG2_E - $SEG2_S, 2))")              # 1x
D3=$(py "print(round(($SEG3_E - $SEG3_S) / 4.0, 2))")     # 4x
D4=$(py "print(round($SEG4_E - $SEG4_S, 2))")              # 1x

# ── 计算字幕在最终视频中的时间窗口（累计偏移）────────────────────
# 片头(3s) + D0 + D1 + D2 + D3 + D4
TITLE_DUR=3
END_CARD_DUR=7

T_FORM_IN=3
T_FORM_OUT=$(py "print(round($TITLE_DUR + $D0, 2))")
T_SCOUT_IN=$T_FORM_OUT
T_SCOUT_OUT=$(py "print(round($T_FORM_OUT + $D1, 2))")
T_DRAFT_IN=$T_SCOUT_OUT
T_DRAFT_OUT=$(py "print(round($T_SCOUT_OUT + $D2, 2))")
T_CRITIC_IN=$T_DRAFT_OUT
T_CRITIC_OUT=$(py "print(round($T_DRAFT_OUT + $D3, 2))")
T_RESULT_IN=$T_CRITIC_OUT
T_RESULT_OUT=$(py "print(round($T_CRITIC_OUT + $D4, 2))")
TOTAL=$(py "print(round($TITLE_DUR + $D0 + $D1 + $D2 + $D3 + $D4 + $END_CARD_DUR, 1))")

echo ""
echo "📐 最终视频结构:"
printf "   [%5.1f → %5.1f]  片头标题卡  (3s)\n" 0 $TITLE_DUR
printf "   [%5.1f → %5.1f]  表单填写 2x  (%.1fs)\n" $T_FORM_IN $T_FORM_OUT $D0
printf "   [%5.1f → %5.1f]  Scout 1x     (%.1fs)\n" $T_SCOUT_IN $T_SCOUT_OUT $D1
printf "   [%5.1f → %5.1f]  Draft 1x     (%.1fs)\n" $T_DRAFT_IN $T_DRAFT_OUT $D2
printf "   [%5.1f → %5.1f]  Critic 4x    (%.1fs)\n" $T_CRITIC_IN $T_CRITIC_OUT $D3
printf "   [%5.1f → %5.1f]  结果滚屏 1x  (%.1fs)\n" $T_RESULT_IN $T_RESULT_OUT $D4
printf "   [%5.1f → %5.1f]  结果对比卡片 (7s)\n" $T_RESULT_OUT $(py "print(round($T_RESULT_OUT + 7, 1))")
echo "   ─────────────────────────────"
echo "   总时长: ${TOTAL}s"
echo ""

# ── Step 1: 生成片头标题卡 (PNG) ──────────────────────────────────
echo "🎨 Step 1: 生成片头标题卡..."
python3 << PYEOF
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
img = Image.new('RGB', (W, H), (10, 10, 18))
draw = ImageDraw.Draw(img)

# 背景渐变感（简单处理：顶部深底部稍浅）
for y in range(H):
    c = int(10 + y * 8 / H)
    draw.line([(0, y), (W, y)], fill=(c, c, c+8))

font_big   = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 52)
font_med   = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)

# 主标题
title = "VULCA Pipeline"
bbox = draw.textbbox((0, 0), title, font=font_big)
tw = bbox[2] - bbox[0]
draw.text(((W-tw)//2, 210), title, font=font_big, fill=(255, 255, 255))

# 副标题
sub = "Modular Cultural Art Evaluation System"
bbox2 = draw.textbbox((0, 0), sub, font=font_med)
tw2 = bbox2[2] - bbox2[0]
draw.text(((W-tw2)//2, 285), sub, font=font_med, fill=(180, 200, 255))

# 分隔线
draw.rectangle([(W//2-160, 340), (W//2+160, 342)], fill=(80, 80, 120))

# 指标行
metrics = "480 evaluation runs   ·   16 conditions   ·   Peak score 0.917"
bbox3 = draw.textbbox((0, 0), metrics, font=font_small)
tw3 = bbox3[2] - bbox3[0]
draw.text(((W-tw3)//2, 365), metrics, font=font_small, fill=(140, 160, 200))

# 作者 / 会议
draw.text((W//2 - 140, 430), "ACM MM 2026 · Yu Haorui et al.", font=font_small, fill=(100, 120, 160))

img.save('${OUT}/demo_title_card.png')
print("   ✅ demo_title_card.png")
PYEOF

# ── Step 2: 生成结果对比卡片 (PNG) ────────────────────────────────
echo "🎨 Step 2: 生成结果对比卡片..."
python3 << PYEOF
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
img = Image.new('RGB', (W, H), (8, 10, 18))
draw = ImageDraw.Draw(img)

font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
font_head  = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
font_body  = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 21)
font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
font_bold  = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 21)

# 标题
draw.text((W//2 - 260, 60), "Ablation Study Results", font=font_title, fill=(230, 235, 255))
draw.text((W//2 - 170, 108), "480 runs · 16 conditions · 30 tasks (real mode)", font=font_small, fill=(120, 140, 180))

# 表头
draw.rectangle([(160, 155), (1120, 185)], fill=(30, 35, 60))
draw.text((175, 160), "Condition", font=font_head, fill=(180, 200, 255))
draw.text((480, 160), "Score", font=font_head, fill=(180, 200, 255))
draw.text((620, 160), "vs. Baseline", font=font_head, fill=(180, 200, 255))
draw.text((840, 160), "Description", font=font_head, fill=(180, 200, 255))

# 数据行
rows = [
    ("C  — Baseline",         "0.810", "—",        "(24, 160, 88)",  "Direct prompting, no framework"),
    ("H  — Framework",        "0.887", "+9.5%",     "(59, 130, 246)", "VULCA framework + FLUX generator"),
    ("G  — Full System",      "0.915", "+13.0% ✦",  "(234, 179, 8)",  "NB2 generator (this demo)"),
    ("G++ — Peak",            "0.917", "+13.2%",    "(168, 85, 247)", "Full system + Ghost Loop"),
]

y = 200
for i, (cond, score, delta, color_str, desc) in enumerate(rows):
    bg = (18, 22, 38) if i % 2 == 0 else (22, 26, 45)
    draw.rectangle([(160, y), (1120, y+52)], fill=bg)

    color = tuple(int(x.strip('() ')) for x in color_str.split(','))
    # 高亮当前演示行
    if "✦" in delta:
        draw.rectangle([(160, y), (163, y+52)], fill=color)

    draw.text((175, y+14), cond, font=font_bold if "✦" in delta else font_body,
              fill=(255,255,255) if "✦" in delta else (200, 210, 230))
    draw.text((480, y+14), score, font=font_bold if "✦" in delta else font_body,
              fill=color)
    draw.text((620, y+14), delta.replace(" ✦",""), font=font_bold if "✦" in delta else font_body,
              fill=(255, 220, 100) if "✦" in delta else (150, 200, 150))
    draw.text((840, y+14), desc, font=font_small, fill=(140, 155, 185))
    y += 54

# 底部注释
draw.text((175, y+20),
    "✦ = This demo  |  VULCA-Bench: 7,410 samples  |  L1-L5 five-layer evaluation",
    font=font_small, fill=(90, 110, 150))

img.save('${OUT}/demo_result_card.png')
print("   ✅ demo_result_card.png")
PYEOF

# ── Step 3: 提取并变速各段 ────────────────────────────────────────
echo "🎞️  Step 3: 提取并变速各段..."

extract() {
  local LABEL=$1 SS=$2 TO=$3 PTS=$4 OUT_F=$5
  # 用 trim 滤镜代替 -ss/-to：对 webm VP8 稀疏关键帧更可靠
  $FF -y -i "$RAW" \
    -vf "trim=start=${SS}:end=${TO},setpts=(PTS-STARTPTS)*${PTS}" \
    -r 25 -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p \
    "$OUT_F" 2>/dev/null
  echo "   ✅ $LABEL ($(python3 -c "print(round(($TO-$SS)*$PTS,1))")s)"
}

extract "seg0 表单2x"  $SEG0_S $SEG0_E  0.5  $OUT/ps0.mp4
extract "seg1 Scout1x" $SEG1_S $SEG1_E  1.0  $OUT/ps1.mp4
extract "seg2 Draft1x" $SEG2_S $SEG2_E  1.0  $OUT/ps2.mp4
extract "seg3 Critic4x" $SEG3_S $SEG3_E 0.25 $OUT/ps3.mp4
extract "seg4 结果1x"  $SEG4_S $SEG4_E  1.0  $OUT/ps4.mp4

# ── Step 4: 生成片头/尾静帧视频（3s/7s）──────────────────────────
echo "🎞️  Step 4: 生成片头/尾视频..."
$FF -y -loop 1 -t 3 -i $OUT/demo_title_card.png \
  -r 25 -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p $OUT/ps_title.mp4 2>/dev/null
echo "   ✅ 片头 (3s)"

$FF -y -loop 1 -t $END_CARD_DUR -i $OUT/demo_result_card.png \
  -r 25 -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p $OUT/ps_endcard.mp4 2>/dev/null
echo "   ✅ 结果卡片 (${END_CARD_DUR}s)"

# ── Step 5a: 生成 ASS 字幕文件 ────────────────────────────────────
echo "📝 Step 5a: 生成字幕文件..."
# 用 Python 生成 ASS 文件（bash 变量展开后传入）
python3 - ${T_FORM_IN} ${T_FORM_OUT} ${T_SCOUT_IN} ${T_SCOUT_OUT} \
           ${T_DRAFT_IN} ${T_DRAFT_OUT} ${T_CRITIC_IN} ${T_CRITIC_OUT} \
           ${T_RESULT_IN} ${T_RESULT_OUT} << PYEOF
import sys

args = [float(x) for x in sys.argv[1:]]
t_form_in,  t_form_out  = args[0], args[1]
t_scout_in, t_scout_out = args[2], args[3]
t_draft_in, t_draft_out = args[4], args[5]
t_critic_in,t_critic_out= args[6], args[7]
t_result_in,t_result_out= args[8], args[9]

def to_ass(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    cs = int(round((s % 1) * 100))
    return f"{h}:{m:02d}:{int(s):02d}.{cs:02d}"

subtitles = [
    (t_form_in,   t_form_out,   "\u25b6 STAGE 1/5 \u2014 FORM INPUT  |  NB2 (Gemini Image) provider selected"),
    (t_scout_in,  t_scout_out,  "\u25b6 STAGE 2/5 \u2014 CULTURAL SCOUT  |  Querying VULCA-Bench 7,410 samples"),
    (t_draft_in,  t_draft_out,  "\u25b6 STAGE 3/5 \u2014 IMAGE GENERATION  |  NB2 (Gemini Image) generating candidates"),
    (t_critic_in, t_critic_out, "\u25b6 STAGE 4/5 \u2014 VLM CRITIC  |  Gemini evaluating L1-L5 dimensions  [4x speed]"),
    (t_result_in, t_result_out, "\u25b6 STAGE 5/5 \u2014 L1-L5 EVALUATION COMPLETE  |  Queen Decision"),
]

# ASS Style: Alignment=1 (bottom-left), half-transparent black box via BackColour
header = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Stage,Arial,18,&H00FFFFFF,&H000000FF,&H00000000,&H99000000,1,0,0,0,100,100,0,0,3,0,1,1,20,20,16,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

lines = [header]
for (s, e, text) in subtitles:
    lines.append(f"Dialogue: 0,{to_ass(s)},{to_ass(e)},Stage,,0,0,0,,{text}")

with open('${OUT}/demo_subtitles.ass', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print("   ✅ demo_subtitles.ass")
PYEOF

# ── Step 5b: 拼接 + ASS 字幕叠加 ──────────────────────────────────
echo "🔗 Step 5b: 拼接 + 字幕..."

$FF -y \
  -i $OUT/ps_title.mp4 \
  -i $OUT/ps0.mp4 \
  -i $OUT/ps1.mp4 \
  -i $OUT/ps2.mp4 \
  -i $OUT/ps3.mp4 \
  -i $OUT/ps4.mp4 \
  -i $OUT/ps_endcard.mp4 \
  -filter_complex \
    "[0:v][1:v][2:v][3:v][4:v][5:v][6:v]concat=n=7:v=1:a=0[base];[base]ass=${OUT}/demo_subtitles.ass[vout]" \
  -map "[vout]" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -movflags +faststart \
  $OUT/vulca-demo-produced.mp4 2>&1 | grep -E "frame=.*fps|Lsize|error" | tail -3

echo ""
echo "✅ 完成！"
$FF -i $OUT/vulca-demo-produced.mp4 2>&1 | grep -E "Duration|Video:"
ls -lh $OUT/vulca-demo-produced.mp4

# 清理临时文件
rm -f $OUT/ps{0,1,2,3,4}.mp4 $OUT/ps_title.mp4 $OUT/ps_endcard.mp4

echo ""
echo "📂 Windows: I:\\website\\vulca-demo-produced.mp4"
echo "📂 字幕卡片留存: demo_title_card.png / demo_result_card.png"
