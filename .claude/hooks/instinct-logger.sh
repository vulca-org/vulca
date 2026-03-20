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

# 活跃 phase
ACTIVE_PHASE=""
PHASE_DIR="$PROJECT_DIR/.claude/phases"
if [ -d "$PHASE_DIR" ]; then
    for pf in "$PHASE_DIR"/phase-*.json; do
        [ -f "$pf" ] && ACTIVE_PHASE=$(python3 -c "import json; print(json.load(open('$pf')).get('name',''))" 2>/dev/null || true)
    done
fi

# 用 python3 一次性收集 git 变更 + 生成 JSON（避免 shell 转义问题）
python3 -c "
import json, subprocess, os

project = '$PROJECT_DIR'

# 用 git 检测变更文件（比 find -mmin 更可靠）
files = set()

# 未暂存的修改
try:
    out = subprocess.check_output(
        ['git', 'diff', '--name-only'],
        cwd=project, text=True, stderr=subprocess.DEVNULL
    ).strip()
    if out:
        files.update(out.splitlines())
except: pass

# 已暂存的修改
try:
    out = subprocess.check_output(
        ['git', 'diff', '--name-only', '--cached'],
        cwd=project, text=True, stderr=subprocess.DEVNULL
    ).strip()
    if out:
        files.update(out.splitlines())
except: pass

# 未跟踪的新文件（排除常见临时目录）
try:
    out = subprocess.check_output(
        ['git', 'ls-files', '--others', '--exclude-standard'],
        cwd=project, text=True, stderr=subprocess.DEVNULL
    ).strip()
    if out:
        for f in out.splitlines():
            if not any(f.startswith(p) for p in ['node_modules/', 'venv/', '.venv/', '__pycache__/', 'demo_output/']):
                files.add(f)
except: pass

# 最近一次 commit 的变更（如果是刚提交的）
try:
    out = subprocess.check_output(
        ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
        cwd=project, text=True, stderr=subprocess.DEVNULL
    ).strip()
    if out:
        files.update(out.splitlines())
except: pass

files = sorted(files)[:30]

phase = '$ACTIVE_PHASE' if '$ACTIVE_PHASE' else None

entry = {
    'ts': '$TIMESTAMP',
    'branch': '$BRANCH',
    'phase': phase,
    'files_touched': files,
    'file_count': len(files)
}
print(json.dumps(entry, ensure_ascii=False))
" >> "$INSTINCTS_FILE" 2>/dev/null || true

exit 0
