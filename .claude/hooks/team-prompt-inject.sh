#!/bin/bash
# VULCA UserPromptSubmit hook — 注入团队模式上下文
# 事件: UserPromptSubmit (prompt 类型)
# 每次用户发消息时，注入最近的 agent 激活记录和项目状态，
# 提醒 Claude 以团队协调者身份思考。

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/home/yhryzy/projects/website}"

# 构建注入上下文
python3 -c "
import json, os, glob
from datetime import datetime

project = '$PROJECT_DIR'
parts = []

# 1. 最近的 agent 激活记录
activations_file = os.path.join(project, '.claude', 'agent-activations.jsonl')
if os.path.exists(activations_file):
    with open(activations_file) as f:
        lines = f.readlines()
    recent = lines[-5:] if len(lines) >= 5 else lines
    if recent:
        parts.append('Recent agent activations:')
        for line in recent:
            try:
                d = json.loads(line.strip())
                parts.append(f'  {d[\"ts\"][:16]} {d.get(\"agent\",\"?\")} — {d.get(\"description\",\"\")}')
            except: pass
    else:
        parts.append('No agent activations yet — consider spawning agents for multi-perspective analysis.')
else:
    parts.append('No agent activations yet — consider spawning agents for multi-perspective analysis.')

# 2. 最近的 instinct 统计（有多少文件变更）
instincts_file = os.path.join(project, '.claude', 'instincts.jsonl')
if os.path.exists(instincts_file):
    with open(instincts_file) as f:
        lines = f.readlines()
    if lines:
        last = json.loads(lines[-1].strip())
        fc = last.get('file_count', 0)
        phase = last.get('phase') or 'none'
        parts.append(f'Last session: {fc} files touched, phase={phase}')

# 3. 是否有未读报告
reports = glob.glob(os.path.join(project, 'docs', 'reports', '*.md'))
reports = [r for r in reports if 'gitkeep' not in r]
if reports:
    parts.append(f'Reports available: {len(reports)}')

# 输出（控制 token 量）
print(' | '.join(parts[:4]))
" 2>/dev/null || true

exit 0
