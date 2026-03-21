#!/bin/bash
# VULCA Stop hook — 分析本次工作并建议团队视角
# 事件: Stop (command 类型)
# 检测变更模式，输出建议（注入 Claude 上下文）

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/home/yhryzy/projects/website}"
cd "$PROJECT_DIR"

# 检测当前变更文件
python3 -c "
import subprocess, json, os

project = '$PROJECT_DIR'

# 收集变更文件
files = set()
for cmd in [
    ['git', 'diff', '--name-only'],
    ['git', 'diff', '--name-only', '--cached'],
    ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
]:
    try:
        out = subprocess.check_output(cmd, cwd=project, text=True, stderr=subprocess.DEVNULL).strip()
        if out:
            files.update(out.splitlines())
    except: pass

if not files:
    exit()

# 分类
frontend = [f for f in files if 'wenxin-moyun/' in f]
backend = [f for f in files if 'wenxin-backend/' in f]
sdk = [f for f in files if f.startswith('vulca/') and 'test' not in f]
tests = [f for f in files if 'test' in f.lower()]
config = [f for f in files if '.claude/' in f]
canvas = [f for f in files if 'canvas' in f.lower() or 'Canvas' in f]
hitl = [f for f in files if 'hitl' in f.lower() or 'Hitl' in f]

suggestions = []

# 大量前端变更 → 建议设计审查
if len(frontend) >= 3:
    suggestions.append('Multiple frontend files changed — consider design-reviewer audit')

# Canvas/HITL 变更 → 产品视角
if canvas or hitl:
    suggestions.append('Canvas/HITL changes detected — product-analyst: how does this affect user experience?')

# 新测试文件 → 内容机会
if len(tests) >= 2:
    suggestions.append('Test coverage improved — content-creator: worth a technical blog post?')

# 后端 API 变更 → 合约检查
if any('routes.py' in f or 'schemas.py' in f for f in backend):
    suggestions.append('API routes/schemas changed — contract-reviewer: check frontend sync')

# SDK 变更 → 确认测试
if sdk:
    suggestions.append('SDK core changed — run vulca tests to verify')

# 大量变更 → 里程碑检查
if len(files) >= 10:
    suggestions.append(f'{len(files)} files changed — milestone? Consider team quick review (Mode B)')

# 检查 agent 激活记录
activations = os.path.join(project, '.claude', 'agent-activations.jsonl')
agent_count = 0
if os.path.exists(activations):
    with open(activations) as f:
        agent_count = sum(1 for _ in f)

if agent_count == 0 and len(files) >= 5:
    suggestions.append('No agents spawned yet this project — team perspectives may add value')

if suggestions:
    print('Team suggestions: ' + ' | '.join(suggestions[:3]))
" 2>/dev/null || true

exit 0
