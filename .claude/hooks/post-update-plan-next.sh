#!/bin/bash
# Hook 3: Post-update planning trigger
# Detects when core MD files were freshly updated, then prompts Claude to
# re-read all v2 guidance files and design the next execution plan using
# parallel agent clusters.
#
# Trigger: Stop event (runs after each Claude response)
# Anti-loop: Uses /tmp/vulca-hook-state/planning-prompted-{date} lock file
#            Only fires when MEMORY.md was modified in last 3 min
#            AND code was also modified recently (not just a doc-only edit)
#
# v2 核心文档体系（6 核心 + 3 辅助）全部纳入扫描范围。
#
# Exit codes:
#   0 = no action needed, or additionalContext returned

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/home/yhryzy/projects/website}"
BACKEND_DIR="$PROJECT_DIR/wenxin-backend"
DOCS_DIR="$PROJECT_DIR/wenxin-moyun/docs"
STATE_DIR="/tmp/vulca-hook-state"
TODAY=$(date '+%Y-%m-%d')
LOCK_FILE="$STATE_DIR/planning-prompted-$TODAY"
LOG_FILE="/tmp/vulca-post-update-plan-next.log"

mkdir -p "$STATE_DIR"

# ============================================
# v2 核心文档体系（完整 9 个）
# ============================================
MEMORY_MD="$HOME/.claude/projects/-mnt-i-website/memory/MEMORY.md"

# 6 核心
V2_FULL="$DOCS_DIR/vulca-prototype-plan-v2.md"
V2_COMPACT="$DOCS_DIR/vulca-prototype-plan-v2-compact.md"
V2_FUSION="$DOCS_DIR/vulca-l1l5-dynamic-fusion-design.md"
V2_FC="$DOCS_DIR/agent-function-calling-architecture-2026-02-10.md"
V2_FUSION_NET="$DOCS_DIR/l1-l5-dynamic-fusion-design-2026-02-10.md"
V2_REVIEW="$DOCS_DIR/v2-plan-review-2026-02-10.md"

# 3 辅助
V2_AUDIT="$DOCS_DIR/vulca-prototype-deep-audit-2026-02-10.md"
V2_ROADMAP="$DOCS_DIR/vulca-analysis-review-roadmap-2026-02-10.md"
V2_D2="$DOCS_DIR/d2-executable-checklist.md"

# 执行报告
REPORTS_DIR="$BACKEND_DIR/app/prototype/reports"

# ============================================
# Check 1: Was MEMORY.md freshly updated? (within last 3 min)
# ============================================
MEMORY_FRESH=0
if [ -f "$MEMORY_MD" ]; then
    MEMORY_AGE=$(find "$MEMORY_MD" -mmin -3 2>/dev/null | wc -l)
    if [ "$MEMORY_AGE" -gt 0 ]; then
        MEMORY_FRESH=1
    fi
fi

if [ "$MEMORY_FRESH" -eq 0 ]; then
    echo '{"continue": true}'
    exit 0
fi

# ============================================
# Check 2: Was there also recent code activity? (prevents loop on doc-only edits)
# ============================================
CODE_ACTIVE=0
if [ -d "$BACKEND_DIR/app/prototype" ]; then
    RECENT_PY=$(find "$BACKEND_DIR/app/prototype" -name "*.py" -mmin -10 2>/dev/null | wc -l)
    if [ "$RECENT_PY" -gt 0 ]; then
        CODE_ACTIVE=1
    fi
fi

if [ "$CODE_ACTIVE" -eq 0 ]; then
    echo '{"continue": true}'
    exit 0
fi

# ============================================
# Check 3: Already prompted for planning this session?
# ============================================
if [ -f "$LOCK_FILE" ]; then
    LOCK_AGE=$(find "$LOCK_FILE" -mmin -30 2>/dev/null | wc -l)
    if [ "$LOCK_AGE" -gt 0 ]; then
        echo '{"continue": true}'
        exit 0
    fi
fi

# ============================================
# Gather current project state summary
# ============================================
echo "$(date '+%Y-%m-%d %H:%M:%S') - Planning trigger fired" >> "$LOG_FILE"

# Count completed phases from MEMORY.md
PHASES_DONE=0
if [ -f "$MEMORY_MD" ]; then
    PHASES_DONE=$(grep -c "COMPLETE" "$MEMORY_MD" 2>/dev/null || echo "0")
fi

# Count prototype reports
REPORT_COUNT=0
if [ -d "$REPORTS_DIR" ]; then
    REPORT_COUNT=$(find "$REPORTS_DIR" -name "*.md" | wc -l)
fi

# Count validation scripts
VALIDATE_COUNT=0
if [ -d "$BACKEND_DIR/app/prototype/tools" ]; then
    VALIDATE_COUNT=$(find "$BACKEND_DIR/app/prototype/tools" -name "validate_*.py" | wc -l)
fi

# Get v2 plan status markers from compact (source of truth)
V2_STATUS=""
if [ -f "$V2_COMPACT" ]; then
    V2_STATUS=$(grep -E "✅|❌" "$V2_COMPACT" 2>/dev/null | head -15 | sed 's/|/;/g' | tr '\n' ' ')
fi

# Create lock file
touch "$LOCK_FILE"

# ============================================
# Build the file manifest for agent cluster
# ============================================
FILE_LIST=""

# Core docs (all 6)
for f in "$V2_FULL" "$V2_COMPACT" "$V2_FUSION" "$V2_FC" "$V2_FUSION_NET" "$V2_REVIEW"; do
    if [ -f "$f" ]; then
        fname=$(basename "$f")
        fsize=$(du -h "$f" 2>/dev/null | cut -f1)
        FILE_LIST="$FILE_LIST\n- [核心] $f ($fsize)"
    fi
done

# Auxiliary docs (all 3)
for f in "$V2_AUDIT" "$V2_ROADMAP" "$V2_D2"; do
    if [ -f "$f" ]; then
        fname=$(basename "$f")
        fsize=$(du -h "$f" 2>/dev/null | cut -f1)
        FILE_LIST="$FILE_LIST\n- [辅助] $f ($fsize)"
    fi
done

# MEMORY.md
if [ -f "$MEMORY_MD" ]; then
    FILE_LIST="$FILE_LIST\n- [记忆] $MEMORY_MD"
fi

# Add latest 3 reports
if [ -d "$REPORTS_DIR" ]; then
    RECENT_REPORTS=$(ls -t "$REPORTS_DIR"/*.md 2>/dev/null | head -3)
    for r in $RECENT_REPORTS; do
        FILE_LIST="$FILE_LIST\n- [报告] $r"
    done
fi

# ============================================
# Return additionalContext with planning directive
# ============================================
cat <<EOF
{
    "hookSpecificOutput": {
        "hookEventName": "Stop",
        "additionalContext": "## 自动规划触发：v2 文档已同步，请设计下一步计划\n\nv2 核心文档刚刚更新完成。现在请**完整重新阅读所有 v2 指导文件**，然后使用 **Agent 集群**（并行 Task 调用）设计下一步执行计划。\n\n### v2 核心文档体系（6 核心 + 3 辅助）\n${FILE_LIST}\n\n### 当前项目状态摘要\n- 已完成 Phase 数: ${PHASES_DONE}\n- 报告数: ${REPORT_COUNT}\n- 验证脚本数: ${VALIDATE_COUNT}\n- v2 进度快照: ${V2_STATUS:-未读取}\n\n### 文档关系（重要）\n- **v2-compact** 是唯一真实来源（source of truth）\n- **v2 总纲**是完整设计，与 compact 的观测同步表必须一致\n- **动态融合**(51KB)和**FC架构**(7KB)是总纲引用的核心技术文档\n- **融合联网版**(11KB)是动态融合的精简版\n- **审查报告**记录了文档层面的 P0/P1/P2 问题\n\n### 规划要求\n\n请使用以下 Agent 集群模式（**并行启动多个 Task**）：\n\n1. **Explore Agent**: 扫描 prototype/ 目录，列出所有已实现 vs 未实现的模块\n2. **Explore Agent**: 读取 v2-plan-compact.md 和 v2 总纲，提取下一阶段待办（关注 ❌ 标记项）\n3. **Explore Agent**: 扫描所有 validate_*.py 脚本，汇总当前 Gate 通过状态\n4. **Plan Agent**: 基于以上三个 Agent 的结果，输出结构化的下一步执行计划\n\n### 输出格式\n\n规划结果应包含：\n- **下一个目标**（从 v2 ❌ 项中选优先级最高的）\n- **具体步骤清单**（每步标注：新建/修改哪些文件、预期行数、依赖关系）\n- **Gate 验收标准**（对齐 v2 总纲中定义的 Gate 指标）\n- **需要同步更新的文档**（列出哪些核心文档需要改哪个 section）\n- **风险和 fallback 策略**\n\n请立即开始并行 Agent 集群扫描。"
    }
}
EOF
exit 0
