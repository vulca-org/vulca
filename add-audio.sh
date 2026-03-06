#!/bin/bash
# add-audio.sh  ——  为 vulca-demo-produced.mp4 添加 TTS 配音 + BGM
#
# 输出：./vulca-demo-with-audio.mp4
#
# 安全说明：
#   - TTS 文本硬编码在 Python 字符串中，不接受外部输入
#   - BGM URL 硬编码，下载后验证 MP3 magic bytes 再传 ffmpeg
#   - ffmpeg 不执行任何动态构建的 shell 命令
#
set -e

FF=/home/yhryzy/.local/bin/ffmpeg
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT=$PROJECT_ROOT
VIDEO=$OUT/vulca-demo-produced.mp4
VOICE_MP3=$OUT/demo_voice.mp3
BGM_MP3=$OUT/demo_bgm.mp3
FINAL=$OUT/vulca-demo-with-audio.mp4

[ ! -f "$VIDEO" ] && echo "❌ 找不到 $VIDEO，请先运行 produce-demo.sh" && exit 1

# ── 获取视频时长（秒）────────────────────────────────────────────
VID_DUR=$(python3 -c "
import subprocess, re
r = subprocess.run(['$FF', '-i', '$VIDEO'], capture_output=True)
out = r.stderr.decode()
m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', out)
if m:
    print(round(int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3)), 2))
")
echo "📐 视频时长: ${VID_DUR}s"

# ─────────────────────────────────────────────────────────────────
# Step 1: 生成 TTS 配音
# ─────────────────────────────────────────────────────────────────
echo ""
echo "🎙️  Step 1: 生成 TTS 配音（en-US-BrianNeural）..."

python3 << PYEOF
import asyncio, edge_tts, sys

# 叙事脚本（约 165 词，-5% rate 下约 60s）
# 注意：NB2 / VLM / L1 等缩写用空格分开以确保正确发音
SCRIPT = """\
Welcome to VULCA — a modular pipeline for evaluating A I-generated cultural art.

In this demonstration, we generate ink wash paintings in the style of Qi Baishi's \
xieyi shrimp, using N B 2 — powered by Google Gemini Image generation — \
with two candidate images requested.

First, the Cultural Scout retrieves evidence from VULCA-Bench — \
a dataset of seven thousand, four hundred and ten human-annotated cultural samples — \
identifying key visual attributes and historical context for this motif.

Next, the Image Generation stage invokes N B 2, \
producing two high-quality candidate artworks.

The V L M Critic module — powered by Gemini Vision — \
then scores each candidate across five dimensions: \
semantic grounding, technical execution, cultural context, innovation, \
and cultural resonance. This stage is shown here at four times speed.

The Queen Decision module selects the best candidate \
and outputs a full L 1 through L 5 evaluation profile.

In our ablation study — four hundred eighty real evaluation runs \
across sixteen experimental conditions — \
the complete VULCA system with N B 2 achieves a score of zero point nine one five. \
That is a thirteen percent improvement over the direct prompting baseline, \
and the highest result across all conditions tested.

VULCA: making cultural art generation measurable, reproducible, and interpretable.
"""

async def generate():
    communicate = edge_tts.Communicate(
        SCRIPT,
        voice="en-US-BrianNeural",
        rate="-5%",
        volume="+0%",
        pitch="-2Hz",
    )
    await communicate.save("${OUT}/demo_voice.mp3")

asyncio.run(generate())
print("   ✅ demo_voice.mp3 已生成")
PYEOF

# 获取 TTS 时长
VOICE_DUR=$($FF -i $VOICE_MP3 2>&1 | grep Duration | grep -oP '(\d+):(\d+):(\d+\.\d+)' | python3 -c "
import sys
t = sys.stdin.read().strip().split(':')
print(round(int(t[0])*3600 + int(t[1])*60 + float(t[2]), 1))")
echo "   🎙️  TTS 时长: ${VOICE_DUR}s（视频 ${VID_DUR}s）"

# ─────────────────────────────────────────────────────────────────
# Step 2: 下载 Kevin MacLeod — Aitech (CC BY 3.0)
# 来源：Internet Archive，Incompetech 官方备份
# ─────────────────────────────────────────────────────────────────
echo ""
echo "🎵 Step 2: 获取 BGM（Kevin MacLeod — Aitech）..."

BGM_URL="https://archive.org/download/Incompetech/mp3-royaltyfree/Aitech.mp3"

if [ -f "$BGM_MP3" ] && [ $(stat -c%s "$BGM_MP3") -gt 100000 ]; then
  echo "   ✅ 已有 demo_bgm.mp3，跳过下载"
else
  echo "   📥 从 archive.org 下载..."
  wget -q --timeout=30 --tries=2 -O "$BGM_MP3" "$BGM_URL" 2>&1
  if [ $? -ne 0 ] || [ $(stat -c%s "$BGM_MP3") -lt 100000 ]; then
    echo "   ⚠  Aitech 下载失败，尝试备用曲目 Arcane..."
    BGM_URL2="https://archive.org/download/Incompetech/mp3-royaltyfree/Arcane.mp3"
    wget -q --timeout=30 --tries=2 -O "$BGM_MP3" "$BGM_URL2" 2>&1
  fi

  # 安全验证：检查 MP3 magic bytes（ID3 tag = 0x49443300 或 frame sync = 0xFF 0xFB）
  MAGIC=$(python3 -c "
with open('$BGM_MP3', 'rb') as f:
    b = f.read(3)
if b[:3] == b'ID3' or (len(b)>=2 and b[0]==0xFF and b[1] in (0xFB,0xF3,0xF2,0xFA)):
    print('ok')
else:
    print('invalid')
")
  if [ "$MAGIC" != "ok" ]; then
    echo "❌ 下载的文件不是有效 MP3，已中止（可能被替换）"
    rm -f "$BGM_MP3"
    exit 1
  fi
  echo "   ✅ demo_bgm.mp3（验证通过）"
fi

# ─────────────────────────────────────────────────────────────────
# Step 3: 混音合成
# 策略：
#   - voice(0dB) 作为主音轨
#   - bgm(-20dB, 循环, 与视频等长) 作为背景
#   - 两路混合后加到视频
# ─────────────────────────────────────────────────────────────────
echo ""
echo "🔊 Step 3: 混音合成..."

$FF -y \
  -i "$VIDEO" \
  -i "$VOICE_MP3" \
  -stream_loop -1 -i "$BGM_MP3" \
  -filter_complex \
    "[1:a]atempo=1.2,volume=1.0,atrim=duration=${VID_DUR},asetpts=PTS-STARTPTS[voice];[2:a]volume=0.18,atrim=duration=${VID_DUR},asetpts=PTS-STARTPTS[bgm];[voice][bgm]amix=inputs=2:duration=shortest[aout]" \
  -map "0:v" -map "[aout]" \
  -c:v copy \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  "$FINAL" 2>&1 | grep -E "frame=.*fps|Lsize|error|Error" | tail -4

echo ""
echo "✅ 完成！"
$FF -i "$FINAL" 2>&1 | grep -E "Duration|Video:|Audio:"
ls -lh "$FINAL"
echo ""
echo "📂 Windows: I:\\website\\vulca-demo-with-audio.mp4"
echo ""
echo "📜 BGM 版权：Kevin MacLeod (incompetech.com)"
echo "   Licensed under Creative Commons: By Attribution 4.0 License"
echo "   http://creativecommons.org/licenses/by/4.0/"
