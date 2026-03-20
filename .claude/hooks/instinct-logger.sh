#!/bin/bash
# VULCA Instinct Logger — Stop hook 记录每次会话操作
# 追加一行 JSON 到 .claude/instincts.jsonl
# 用于积累操作模式，后续分析进化配置

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/home/yhryzy/projects/website}"
cd "$PROJECT_DIR"

INSTINCTS_FILE="$PROJECT_DIR/.claude/instincts.jsonl"

# 收集数据
TIMESTAMP=$(date -Is 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# 变更文件列表（最近 5 分钟内修改的文件）
CHANGED_FILES=$(find "$PROJECT_DIR" -maxdepth 4 \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/venv/*" \
    -not -path "*/.venv/*" \
    -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.md" \
    2>/dev/null | xargs -r find 2>/dev/null -maxdepth 0 -mmin -5 2>/dev/null | head -20 || true)

# 活跃 phase
ACTIVE_PHASE=""
PHASE_DIR="$PROJECT_DIR/.claude/phases"
if [ -d "$PHASE_DIR" ]; then
    for pf in "$PHASE_DIR"/phase-*.json; do
        [ -f "$pf" ] && ACTIVE_PHASE=$(python3 -c "import json; print(json.load(open('$pf')).get('name',''))" 2>/dev/null || true)
    done
fi

# 用 python3 生成 JSON（避免 shell 转义问题）
python3 -c "
import json, sys

files = '''$CHANGED_FILES'''.strip().split('\n') if '''$CHANGED_FILES'''.strip() else []
# 转为相对路径
import os
base = '$PROJECT_DIR'
files = [os.path.relpath(f, base) for f in files if f]

entry = {
    'ts': '$TIMESTAMP',
    'branch': '$BRANCH',
    'phase': '$ACTIVE_PHASE' or None,
    'files_touched': files[:20],
    'file_count': len(files)
}
print(json.dumps(entry, ensure_ascii=False))
" >> "$INSTINCTS_FILE" 2>/dev/null || true

exit 0
