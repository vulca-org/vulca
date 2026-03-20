#!/bin/bash
# VULCA auto-format hook
# 在 Edit/Write 后自动格式化文件（如果工具可用）
# 事件: PostToolUse (Edit|Write)
# Exit 0=通过（格式化是 best-effort，不阻塞）

set -euo pipefail

# 从 stdin 读取 JSON 输入
INPUT=$(cat)

# 用 python3 解析 JSON
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', {})
    print(ti.get('file_path', ''))
except:
    print('')
" 2>/dev/null || echo "")

# 如果无法解析文件路径，跳过
if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

# 获取文件扩展名
EXT="${FILE_PATH##*.}"

case "$EXT" in
    py)
        # Python: 尝试 ruff format（如不存在则跳过）
        if command -v ruff &>/dev/null; then
            ruff format "$FILE_PATH" 2>/dev/null || true
            ruff check --fix "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
    ts|tsx|js|jsx|css|json)
        # Frontend: 尝试 prettier（如不存在则跳过）
        if command -v prettier &>/dev/null; then
            prettier --write "$FILE_PATH" 2>/dev/null || true
        elif [ -f "$(dirname "$FILE_PATH")/node_modules/.bin/prettier" ]; then
            "$(dirname "$FILE_PATH")/node_modules/.bin/prettier" --write "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
esac

# 格式化是 best-effort，始终放行
exit 0
