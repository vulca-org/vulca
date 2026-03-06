#!/usr/bin/env bash
# finalize-demo-v3.sh
# VULCA Demo V3 — 双语字幕 + Logo 水印 + 数据标注
# 输出: vulca-demo-v3-final.mp4 (62.56s, 1280×720, h264+AAC)

set -euo pipefail

FF=/home/yhryzy/.local/bin/ffmpeg
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT=$PROJECT_ROOT

echo "╔══════════════════════════════════════════════╗"
echo "║   VULCA Demo V3 — Subtitle + Watermark        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ─── Step 1: Generate transparent logo overlay PNG ────────────────────────
echo "[1/3] Generating logo overlay PNG..."
python3 << PYEOF
from PIL import Image

logo = Image.open('${OUT}/wenxin-moyun/public/logo.png').convert('RGBA')

# 去白底（阈值 235）
data = logo.getdata()
new_data = []
for r, g, b, a in data:
    if r > 235 and g > 235 and b > 235:
        new_data.append((r, g, b, 0))
    else:
        new_data.append((r, g, b, a))
logo.putdata(new_data)

# 缩放到 180×54
logo = logo.resize((180, 54), Image.LANCZOS)

# 深色半透明圆角背景框 (200×66, alpha=140/255 ≈ 55%)
bg = Image.new('RGBA', (200, 66), (0, 0, 0, 140))
bg.paste(logo, (10, 6), logo)
bg.save('${OUT}/demo_logo_overlay.png')
print("  ✓ demo_logo_overlay.png saved (200×66 RGBA)")
PYEOF

# ─── Step 2: Generate bilingual ASS subtitles ─────────────────────────────
echo "[2/3] Generating demo_subtitles_v3.ass..."
python3 << PYEOF
# ASS 颜色格式: &HAABBGGRR (A=00 完全不透明, FF 完全透明)
# Alignment 键盘布局:
#   7 8 9
#   4 5 6
#   1 2 3
# White=&H00FFFFFF Gold(FFD700)=&H0000D7FF Orange(FF8C00)=&H00008CFF
# LightBlue(87CEEB)=&H00EBCE87 LightGreen(90EE90)=&H0090EE90

CJK_FONT = "WenQuanYi Zen Hei"

def ts(sec):
    """Convert seconds to ASS timestamp H:MM:SS.CC"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec % 1) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def dlg(start, end, style, text):
    return f"Dialogue: 0,{ts(start)},{ts(end)},{style},,0,0,0,,{text}"

L = []

# ── Script Info ──────────────────────────────────────────────────────────────
L += [
    "[Script Info]",
    "ScriptType: v4.00+",
    "PlayResX: 1280",
    "PlayResY: 720",
    "WrapStyle: 0",
    "ScaledBorderAndShadow: yes",
    "",
]

# ── Styles ───────────────────────────────────────────────────────────────────
L += [
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    # Stage EN: 白色 18pt bold, 半透明黑底框(BorderStyle=3), 左下(Align=1), MarginV=16
    "Style: Stage,Arial,18,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,3,0,1,1,20,20,16,1",
    # Stage ZH: 金黄色 16pt, 同底框, 左下(Align=1), MarginV=44 (EN 上方)
    f"Style: StageZh,{CJK_FONT},16,&H0000D7FF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,3,0,1,1,20,20,44,1",
    # DataTag: 橙色 22pt bold, 无底框(BorderStyle=1 outline only), 右中(Align=6)
    "Style: DataTag,Arial,22,&H00008CFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,6,20,20,0,1",
    # Narr EN: 浅蓝 14pt, 底中(Align=2), MarginV=8, 带轮廓阴影
    "Style: Narr,Arial,14,&H00EBCE87,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,1,2,20,20,8,1",
    # Narr ZH: 浅绿 14pt, 底中(Align=2), MarginV=32 (EN 上方)
    f"Style: NarrZh,{CJK_FONT},14,&H0090EE90,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,1,2,20,20,32,1",
    "",
]

# ── Events ───────────────────────────────────────────────────────────────────
L += [
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    "",
]

# ── Stage Labels (EN + ZH) ────────────────────────────────────────────────────
stages = [
    (3.0,  13.0,  "▶ STAGE 1/5 — FORM INPUT  |  NB2 (Gemini Image)",
                  "▶ 第一阶段 — 表单输入  |  NB2 (Gemini Image) 生成器"),
    (13.0, 21.2,  "▶ STAGE 2/5 — CULTURAL SCOUT  |  7,410 samples",
                  "▶ 第二阶段 — 文化侦察  |  检索 7,410 条标注样本"),
    (21.2, 25.2,  "▶ STAGE 3/5 — IMAGE GENERATION  |  NB2 candidates",
                  "▶ 第三阶段 — 图像生成  |  NB2 生成候选图像"),
    (25.2, 33.0,  "▶ STAGE 4/5 — VLM CRITIC  |  L1-L5 [4x speed]",
                  "▶ 第四阶段 — VLM 评测  |  L1-L5 维度 [4倍速]"),
    (33.0, 55.5,  "▶ STAGE 5/5 — L1-L5 COMPLETE  |  Queen Decision",
                  "▶ 第五阶段 — 综合评测完成  |  Queen 决策"),
]

for s, e, en, zh in stages:
    L.append(dlg(s, e, "Stage", en))
for s, e, en, zh in stages:
    L.append(dlg(s, e, "StageZh", zh))
L.append("")

# ── Data Tags (右侧中部浮现, \an6\pos 精确定位) ──────────────────────────────
# \an6 = mid-right anchor; \pos(1264,360) = 距右边缘16px，垂直居中
data_tags = [
    (20.5, 22.5, r"{\an6\pos(1264,360)}7,410 samples retrieved"),
    (32.0, 34.0, r"{\an6\pos(1264,360)}L1-L5 · 5 dimensions"),
    (55.5, 58.5, r"{\an6\pos(1264,360)}G: 0.915  ↑+13%"),
]
for s, e, text in data_tags:
    L.append(dlg(s, e, "DataTag", text))
L.append("")

# ── Narration Subtitles (EN 底部, ZH 在 EN 上方) ─────────────────────────────
narr_en = [
    (0.0,  6.7,  "Welcome to VULCA — AI art evaluation platform"),
    (6.7,  18.0, "Generating ink wash shrimp with NB2 (Gemini Image)"),
    (18.0, 28.0, "Cultural Scout retrieves 7,410 annotated samples"),
    (28.0, 34.0, "NB2 generates two high-quality candidate artworks"),
    (34.0, 47.0, "VLM Critic scores L1-L5 dimensions at 4x speed"),
    (47.0, 60.0, "Queen Decision: best artwork 0.915, +13% over baseline"),
    (60.0, 62.56, "VULCA: measurable, reproducible, explainable"),
]
narr_zh = [
    (0.0,  6.7,  "欢迎来到 VULCA — AI 艺术评测平台"),
    (6.7,  18.0, "使用 NB2 (Gemini Image) 生成水墨虾候选图像"),
    (18.0, 28.0, "文化侦察模块检索 7,410 条标注样本"),
    (28.0, 34.0, "NB2 生成两张高质量候选作品"),
    (34.0, 47.0, "VLM 评测模块对 L1-L5 维度打分，四倍速"),
    (47.0, 60.0, "Queen 决策选出最优，得分 0.915，高出基线 13%"),
    (60.0, 62.56, "VULCA：可量化、可复现、可解释"),
]

for s, e, text in narr_en:
    L.append(dlg(s, e, "Narr", text))
for s, e, text in narr_zh:
    L.append(dlg(s, e, "NarrZh", text))

with open('${OUT}/demo_subtitles_v3.ass', 'w', encoding='utf-8') as f:
    f.write('\n'.join(L) + '\n')

# 验证生成结果
with open('${OUT}/demo_subtitles_v3.ass', 'r', encoding='utf-8') as f:
    content = f.read()
dialogue_count = content.count('\nDialogue:')
print(f"  ✓ demo_subtitles_v3.ass saved ({dialogue_count} dialogue events)")
PYEOF

# ─── Step 3: ffmpeg single-pass render ────────────────────────────────────
echo "[3/3] ffmpeg rendering (estimate ~1-2 min)..."

FILTER="[0:v][1:v]overlay=W-w-16:16[v_logo];[v_logo]ass=${OUT}/demo_subtitles_v3.ass[vout]"

"$FF" -y \
  -i "${OUT}/vulca-demo-with-audio.mp4" \
  -loop 1 -i "${OUT}/demo_logo_overlay.png" \
  -filter_complex "${FILTER}" \
  -map "[vout]" \
  -map "0:a" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p \
  -c:a copy \
  -shortest \
  -movflags +faststart \
  "${OUT}/vulca-demo-v3-final.mp4"

# ─── Verification ──────────────────────────────────────────────────────────
echo ""
echo "─── Verification ───────────────────────────────"
ls -lh "${OUT}/vulca-demo-v3-final.mp4"
"$FF" -i "${OUT}/vulca-demo-v3-final.mp4" 2>&1 | grep -E "Duration|Video:|Audio:" || true
echo ""
echo "✅ Done!  vulca-demo-v3-final.mp4 is ready"
echo "📂 Windows path: I:\\website\\vulca-demo-v3-final.mp4"
