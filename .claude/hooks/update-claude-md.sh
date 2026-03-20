#!/bin/bash
# VULCA CLAUDE.md 自动更新 — 更新标记区内的状态信息
# 仅更新 <!-- AUTO-STATUS-START --> 和 <!-- AUTO-STATUS-END --> 之间的内容
# 在 Stop hook 中条件触发（每 10 次会话更新一次）

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/home/yhryzy/projects/website}"
cd "$PROJECT_DIR"

CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"
INSTINCTS="$PROJECT_DIR/.claude/instincts.jsonl"

# 检查 CLAUDE.md 是否有自动更新标记
if ! grep -q "AUTO-STATUS-START" "$CLAUDE_MD" 2>/dev/null; then
    exit 0
fi

# 节流：每 10 次 instinct 记录更新一次
if [ -f "$INSTINCTS" ]; then
    COUNT=$(wc -l < "$INSTINCTS")
    REMAINDER=$((COUNT % 10))
    if [ "$REMAINDER" -ne 0 ]; then
        exit 0
    fi
fi

# 生成状态内容
STATUS=$(python3 -c "
import json, os, glob
from datetime import datetime

project = '$PROJECT_DIR'
lines = []

# Git info
import subprocess
try:
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=project, text=True).strip()
    last_commit = subprocess.check_output(['git', 'log', '--oneline', '-1'], cwd=project, text=True).strip()
    lines.append(f'- **Branch**: {branch} | Last commit: {last_commit}')
except: pass

# Phase info
phase_dir = os.path.join(project, '.claude', 'phases')
if os.path.isdir(phase_dir):
    phases = glob.glob(os.path.join(phase_dir, 'phase-*.json'))
    if phases:
        for pf in phases:
            try:
                d = json.load(open(pf))
                lines.append(f\"- **Active Phase**: {d.get('name', '?')} — {d.get('description', '')}\")
            except: pass
    else:
        lines.append('- **Phase**: No active phase')

# Evolution info
evolved = os.path.join(project, 'wenxin-backend', 'app', 'prototype', 'data', 'evolved_context.json')
if os.path.exists(evolved):
    try:
        mtime = datetime.fromtimestamp(os.path.getmtime(evolved)).strftime('%Y-%m-%d')
        d = json.load(open(evolved))
        traditions = [k for k in d if isinstance(d[k], dict)]
        lines.append(f'- **Evolution**: {len(traditions)} traditions evolved (last: {mtime})')
    except: pass

# Instinct stats
instincts = os.path.join(project, '.claude', 'instincts.jsonl')
if os.path.exists(instincts):
    with open(instincts) as f:
        count = sum(1 for _ in f)
    lines.append(f'- **Sessions logged**: {count}')

# Config stats
agents = len(glob.glob(os.path.join(project, '.claude', 'agents', '*.md')))
skills = len(glob.glob(os.path.join(project, '.claude', 'skills', 'vulca-*', 'SKILL.md')))
rules = len(glob.glob(os.path.join(project, '.claude', 'rules', '*.md')))
lines.append(f'- **Config**: {agents} agents / {skills} skills / {rules} rules')
lines.append(f'- **Auto-updated**: {datetime.now().strftime(\"%Y-%m-%d %H:%M\")}')

print('\n'.join(lines))
" 2>/dev/null)

if [ -z "$STATUS" ]; then
    exit 0
fi

# 用 python3 替换标记区内容
python3 -c "
import re, sys

with open('$CLAUDE_MD', 'r') as f:
    content = f.read()

status = '''$STATUS'''
replacement = '<!-- AUTO-STATUS-START -->\n' + status + '\n<!-- AUTO-STATUS-END -->'

new_content = re.sub(
    r'<!-- AUTO-STATUS-START -->.*?<!-- AUTO-STATUS-END -->',
    replacement,
    content,
    flags=re.DOTALL
)

if new_content != content:
    with open('$CLAUDE_MD', 'w') as f:
        f.write(new_content)
" 2>/dev/null || true

exit 0
