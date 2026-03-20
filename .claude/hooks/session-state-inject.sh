#!/bin/bash
# VULCA SessionStart hook — 每次会话启动时注入项目快照
# 输出到 stdout，Claude 自动接收为上下文
# 控制在 ~300 token 以内

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/home/yhryzy/projects/website}"
cd "$PROJECT_DIR"

echo "## VULCA 项目快照 ($(date '+%Y-%m-%d %H:%M'))"

# Git 状态
echo "### Git"
echo "Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
git log --oneline -5 2>/dev/null || echo "(no commits)"
DIRTY=$(git status --porcelain 2>/dev/null | wc -l)
if [ "$DIRTY" -gt 0 ]; then
    echo "Working tree: ${DIRTY} uncommitted changes"
else
    echo "Working tree: clean"
fi

# 活跃 Phase
echo "### Phase"
PHASE_DIR="$PROJECT_DIR/.claude/phases"
if [ -d "$PHASE_DIR" ] && ls "$PHASE_DIR"/phase-*.json 1>/dev/null 2>&1; then
    for pf in "$PHASE_DIR"/phase-*.json; do
        python3 -c "
import json, sys
try:
    d = json.load(open('$pf'))
    name = d.get('name', '?')
    desc = d.get('description', '')
    cp = len(d.get('checkpoints', []))
    print(f'Active: {name} — {desc} ({cp} checkpoints)')
except: pass
" 2>/dev/null
    done
else
    echo "No active phase"
fi

# 进化权重快照
echo "### Evolution"
EVOLVED="$PROJECT_DIR/wenxin-backend/app/prototype/data/evolved_context.json"
if [ -f "$EVOLVED" ]; then
    python3 -c "
import json, os
from datetime import datetime
f = '$EVOLVED'
mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M')
d = json.load(open(f))
traditions = [k for k in d if isinstance(d[k], dict)]
print(f'Last updated: {mtime} | {len(traditions)} traditions evolved')
" 2>/dev/null || echo "Cannot read evolved_context.json"
else
    echo "No evolution data"
fi

# 最近报告
echo "### Reports"
REPORTS_DIR="$PROJECT_DIR/docs/reports"
if [ -d "$REPORTS_DIR" ]; then
    RECENT=$(ls -t "$REPORTS_DIR"/*.md 2>/dev/null | head -3)
    if [ -n "$RECENT" ]; then
        echo "$RECENT" | while read -r rf; do echo "- $(basename "$rf")"; done
    else
        echo "No reports yet"
    fi
else
    echo "No reports directory"
fi

# Instinct 统计
INSTINCTS="$PROJECT_DIR/.claude/instincts.jsonl"
if [ -f "$INSTINCTS" ]; then
    COUNT=$(wc -l < "$INSTINCTS")
    echo "### Instincts: ${COUNT} sessions logged"
fi

exit 0
