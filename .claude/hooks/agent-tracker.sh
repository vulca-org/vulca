#!/bin/bash
# VULCA Agent Tracker — 记录每次 Agent tool 调用
# 事件: PreToolUse (Agent)
# 追加记录到 .claude/agent-activations.jsonl

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/home/yhryzy/projects/website}"
LOG_FILE="$PROJECT_DIR/.claude/agent-activations.jsonl"
INPUT=$(cat)

TIMESTAMP=$(date -Is 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')

# 解析 agent 调用信息
python3 -c "
import json, sys

try:
    d = json.loads('''$INPUT''') if '''$INPUT'''.strip() else {}
except:
    try:
        d = json.load(sys.stdin)
    except:
        d = {}

ti = d.get('tool_input', {})
agent_type = ti.get('subagent_type', 'general-purpose')
description = ti.get('description', '')
prompt_preview = ti.get('prompt', '')[:100]
isolation = ti.get('isolation', 'none')
background = ti.get('run_in_background', False)

entry = {
    'ts': '$TIMESTAMP',
    'agent': agent_type,
    'description': description,
    'isolation': isolation,
    'background': background,
    'prompt_preview': prompt_preview
}

with open('$LOG_FILE', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
" 2>/dev/null || true

# 始终放行，不阻塞 agent 调用
exit 0
