#!/bin/bash
# make-video.sh
# 将 4 张 fullPage 截图合成为竖向平移 + xfade 过渡的演示视频
# 用法: bash ./make-video.sh
#
# 输出: ./vulca-demo-final.mp4 (1280×720, ~32s)
set -e

FF=/home/yhryzy/.local/bin/ffmpeg
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT=$PROJECT_ROOT
W=1280
H=720
FPS=30

# ── 检查依赖 ─────────────────────────────────────────────────────
echo "🔍 检查 ffmpeg ..."
$FF -version 2>&1 | head -1

echo "🔍 检查截图文件 ..."
for f in stage-0-form stage-1-scout stage-2-draft stage-3-complete; do
  FILE="$OUT/${f}.png"
  if [ ! -f "$FILE" ]; then
    echo "❌ 缺少 $FILE，请先运行 capture-stages.js"
    exit 1
  fi
  SIZE=$(identify -format "%wx%h" "$FILE" 2>/dev/null || echo "unknown")
  echo "   ✅ ${f}.png  ($SIZE)"
done

# ── 函数：单张截图 → 竖向平移 clip ───────────────────────────────
# pan_clip <input> <output> <duration_s>
# 原理：
#   - scale 保持宽度 W 不变（截图已是 1280px），高度按比例不压缩
#   - crop W×H 裁剪窗口，y 坐标随时间 t 从 0 线性增至 (in_h - H)
#   - 效果：摄像机从页面顶部平滑向下移动到底部，1:1 像素，无压缩
#
# 变量说明（ffmpeg crop 表达式内置）：
#   in_h / ih  = 输入图片实际高度（如 3671）
#   out_h / oh = 裁剪输出高度 = H = 720
#   t          = 当前帧的时间戳（秒，0 → DUR）
pan_clip() {
  local IN="$1"
  local OUT_F="$2"
  local DUR=$3

  echo "🎞️  生成 $(basename $OUT_F) (${DUR}s) ..."

  # -loop 1 -t DUR：把单帧 PNG 循环成 DUR 秒的输入流
  # crop y 公式：(in_h-out_h)*t/DUR，从顶滑到底
  $FF -y -loop 1 -t ${DUR} -i "$IN" \
    -vf "scale=${W}:-2,crop=${W}:${H}:0:'(in_h-out_h)*t/${DUR}'" \
    -r ${FPS} \
    -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p \
    "$OUT_F"
}

# 各阶段时长（秒）
DUR0=4   # stage-0 表单    (~1200px  → 4s)
DUR1=5   # stage-1 scout   (~1800px  → 5s)
DUR2=7   # stage-2 draft   (~2600px  → 7s)
DUR3=10  # stage-3 complete(~4008px  → 10s)

pan_clip "$OUT/stage-0-form.png"     "$OUT/clip0.mp4" $DUR0
pan_clip "$OUT/stage-1-scout.png"    "$OUT/clip1.mp4" $DUR1
pan_clip "$OUT/stage-2-draft.png"    "$OUT/clip2.mp4" $DUR2
pan_clip "$OUT/stage-3-complete.png" "$OUT/clip3.mp4" $DUR3

# ── xfade 拼接（各段间 0.5s crossfade）──────────────────────────
# xfade offset = 累计时长 - 0.5s * (段序号)
# offset01: clip0 结束前 0.5s → 4 - 0.5 = 3.5
# offset12: clip0+clip1 累计 - 已消耗 crossfade → (4+5) - 1×0.5 = 8.5  → 等价于 offset01 + (DUR1-0.5) = 3.5+4.5 = 8.0
# offset23: 3.5 + 4.5 + 6.5 = 14.5
FADE_DUR=0.5
OFFSET01=$(echo "$DUR0 - $FADE_DUR" | bc)            # 3.5
OFFSET12=$(echo "$OFFSET01 + $DUR1 - $FADE_DUR" | bc) # 8.0
OFFSET23=$(echo "$OFFSET12 + $DUR2 - $FADE_DUR" | bc) # 14.5

echo ""
echo "🔗 xfade 拼接: offset01=${OFFSET01}s  offset12=${OFFSET12}s  offset23=${OFFSET23}s"

$FF -y \
  -i "$OUT/clip0.mp4" \
  -i "$OUT/clip1.mp4" \
  -i "$OUT/clip2.mp4" \
  -i "$OUT/clip3.mp4" \
  -filter_complex "
    [0][1]xfade=transition=fade:duration=${FADE_DUR}:offset=${OFFSET01}[v01];
    [v01][2]xfade=transition=fade:duration=${FADE_DUR}:offset=${OFFSET12}[v012];
    [v012][3]xfade=transition=fade:duration=${FADE_DUR}:offset=${OFFSET23}[vout]
  " \
  -map "[vout]" \
  -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -movflags +faststart \
  "$OUT/vulca-demo-final.mp4"

echo ""
echo "✅ 完成！"
ls -lh "$OUT/vulca-demo-final.mp4"

# 用 ffprobe 验证时长和分辨率
echo ""
echo "📊 视频信息:"
$FF -i "$OUT/vulca-demo-final.mp4" 2>&1 | grep -E "Duration|Video:|Stream" | head -5

echo ""
echo "📂 Windows 路径: I:\\website\\vulca-demo-final.mp4"
