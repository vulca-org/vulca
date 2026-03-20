#!/bin/bash
# VULCA protect-files hook
# 阻止编辑受保护文件: .env, constraints.txt, evolved_context.json
# 事件: PreToolUse (Edit)
# Exit 0=通过, Exit 2=阻塞(stderr 反馈给 Claude)

set -euo pipefail

# 从 stdin 读取 JSON 输入
INPUT=$(cat)

# 用 python3 解析 JSON（jq 未安装）
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    # Edit tool: file_path in tool_input
    ti = d.get('tool_input', {})
    print(ti.get('file_path', ''))
except:
    print('')
" 2>/dev/null || echo "")

# 如果无法解析文件路径，放行
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# 受保护文件列表
PROTECTED_PATTERNS=(
    ".env"
    ".env.local"
    ".env.production"
    "constraints.txt"
    "evolved_context.json"
    "settings.local.json"
)

BASENAME=$(basename "$FILE_PATH")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
    if [ "$BASENAME" = "$pattern" ]; then
        echo "BLOCKED: '$FILE_PATH' is a protected file. Reason: $BASENAME should not be edited directly by Claude." >&2
        echo "- .env files contain secrets" >&2
        echo "- constraints.txt controls critical dependency versions (bcrypt 4.0.x)" >&2
        echo "- evolved_context.json is auto-maintained by ContextEvolver" >&2
        echo "- settings.local.json contains local permissions" >&2
        exit 2
    fi
done

# 文件不在保护列表，放行
exit 0
