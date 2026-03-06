#!/bin/bash
# Hook 2: Post-task documentation sync
# Detects when code files have changed but v2 core MD files haven't been updated.
# Returns additionalContext prompting Claude to sync all 6 core + 3 auxiliary documents.
#
# Trigger: Stop event (runs after each Claude response)
# Anti-loop: Uses /tmp/vulca-docs-sync-prompted-{date} lock file
#
# v2 核心文档体系（6 核心 + 3 辅助）:
#   1. vulca-prototype-plan-v2.md (59KB) — v2 总纲
#   2. vulca-prototype-plan-v2-compact.md (19KB) — v2 精简执行版
#   3. vulca-l1l5-dynamic-fusion-design.md (51KB) — 核心技术创新
#   4. agent-function-calling-architecture-2026-02-10.md (7KB) — Agent FC 架构
#   5. l1-l5-dynamic-fusion-design-2026-02-10.md (11KB) — 动态融合联网版
#   6. v2-plan-review-2026-02-10.md (4KB) — v2 审查报告
#   7. vulca-prototype-deep-audit-2026-02-10.md (7KB) — v1→v2 差距审计
#   8. vulca-analysis-review-roadmap-2026-02-10.md (8KB) — 路线复核结论
#   9. d2-executable-checklist.md (2KB) — v1 D2 Schema 清单
#
# Exit codes:
#   0 = no action needed, or additionalContext returned

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/home/yhryzy/projects/website}"
BACKEND_DIR="$PROJECT_DIR/wenxin-backend"
DOCS_DIR="$PROJECT_DIR/wenxin-moyun/docs"
STATE_DIR="/tmp/vulca-hook-state"
TODAY=$(date '+%Y-%m-%d')
LOCK_FILE="$STATE_DIR/docs-sync-prompted-$TODAY"
LOG_FILE="/tmp/vulca-post-task-sync-docs.log"

mkdir -p "$STATE_DIR"

# ============================================
# v2 核心文档（6 个核心 + MEMORY.md）
# ============================================
MEMORY_MD="$HOME/.claude/projects/-mnt-i-website/memory/MEMORY.md"
V2_FULL="$DOCS_DIR/vulca-prototype-plan-v2.md"
V2_COMPACT="$DOCS_DIR/vulca-prototype-plan-v2-compact.md"
V2_FUSION="$DOCS_DIR/vulca-l1l5-dynamic-fusion-design.md"
V2_FC="$DOCS_DIR/agent-function-calling-architecture-2026-02-10.md"
V2_FUSION_NET="$DOCS_DIR/l1-l5-dynamic-fusion-design-2026-02-10.md"
V2_REVIEW="$DOCS_DIR/v2-plan-review-2026-02-10.md"

# 辅助文档（3 个）
V2_AUDIT="$DOCS_DIR/vulca-prototype-deep-audit-2026-02-10.md"
V2_ROADMAP="$DOCS_DIR/vulca-analysis-review-roadmap-2026-02-10.md"
V2_D2="$DOCS_DIR/d2-executable-checklist.md"

# 执行报告目录
REPORTS_DIR="$BACKEND_DIR/app/prototype/reports"

# ============================================
# Check 1: Were code files recently modified?
# ============================================
CODE_CHANGED=0
CHANGED_FILES=""

# Check prototype Python files modified in last 5 minutes
if [ -d "$BACKEND_DIR/app/prototype" ]; then
    RECENT_PY=$(find "$BACKEND_DIR/app/prototype" -name "*.py" -mmin -5 2>/dev/null | wc -l)
    if [ "$RECENT_PY" -gt 0 ]; then
        CODE_CHANGED=1
        CHANGED_FILES=$(find "$BACKEND_DIR/app/prototype" -name "*.py" -mmin -5 -printf '%P\n' 2>/dev/null | head -10 | tr '\n' ', ')
    fi
fi

# Also check for new validation scripts or data files
if [ -d "$BACKEND_DIR/app/prototype/data" ]; then
    RECENT_DATA=$(find "$BACKEND_DIR/app/prototype/data" -name "*.json" -mmin -5 2>/dev/null | wc -l)
    if [ "$RECENT_DATA" -gt 0 ]; then
        CODE_CHANGED=1
    fi
fi

# Check frontend src changes
if [ -d "$PROJECT_DIR/wenxin-moyun/src" ]; then
    RECENT_TS=$(find "$PROJECT_DIR/wenxin-moyun/src" \( -name "*.ts" -o -name "*.tsx" \) -mmin -5 2>/dev/null | wc -l)
    if [ "$RECENT_TS" -gt 0 ]; then
        CODE_CHANGED=1
    fi
fi

# ============================================
# Check 2: Was MEMORY.md recently updated?
# ============================================
MEMORY_FRESH=0
if [ -f "$MEMORY_MD" ]; then
    MEMORY_AGE=$(find "$MEMORY_MD" -mmin -3 2>/dev/null | wc -l)
    if [ "$MEMORY_AGE" -gt 0 ]; then
        MEMORY_FRESH=1
    fi
fi

# ============================================
# Decision logic
# ============================================

# If no code changed, or memory was just updated, or already prompted today → skip
if [ "$CODE_CHANGED" -eq 0 ]; then
    echo '{"continue": true}'
    exit 0
fi

if [ "$MEMORY_FRESH" -eq 1 ]; then
    echo '{"continue": true}'
    exit 0
fi

if [ -f "$LOCK_FILE" ]; then
    LOCK_AGE=$(find "$LOCK_FILE" -mmin -10 2>/dev/null | wc -l)
    if [ "$LOCK_AGE" -gt 0 ]; then
        echo '{"continue": true}'
        exit 0
    fi
fi

# ============================================
# Gather staleness info for each v2 core doc
# ============================================
echo "$(date '+%Y-%m-%d %H:%M:%S') - Docs sync triggered (code changed, docs stale)" >> "$LOG_FILE"

DOC_STATUS=""
for doc_path in "$V2_FULL" "$V2_COMPACT" "$V2_FUSION" "$V2_FC" "$V2_FUSION_NET" "$V2_REVIEW" "$V2_AUDIT" "$V2_ROADMAP" "$V2_D2"; do
    if [ -f "$doc_path" ]; then
        doc_name=$(basename "$doc_path")
        doc_mtime=$(stat -c '%y' "$doc_path" 2>/dev/null | cut -d. -f1)
        DOC_STATUS="$DOC_STATUS\\n- $doc_name (最后更新: $doc_mtime)"
    fi
done

MEMORY_MTIME=""
if [ -f "$MEMORY_MD" ]; then
    MEMORY_MTIME=$(stat -c '%y' "$MEMORY_MD" 2>/dev/null | cut -d. -f1)
fi

# Create lock file
touch "$LOCK_FILE"

# ============================================
# Return additionalContext to prompt Claude
# ============================================
cat <<EOF
{
    "hookSpecificOutput": {
        "hookEventName": "Stop",
        "additionalContext": "## 自动文档同步提醒\n\n代码文件刚刚发生变更，但 v2 核心文档尚未更新。\n\n**变更文件**: ${CHANGED_FILES:-无新检测}\n**MEMORY.md 上次更新**: ${MEMORY_MTIME:-未知}\n\n### 需同步的 v2 核心文档（6 个核心 + 3 个辅助）\n\n**核心文档**（必须保持一致）：\n1. **v2 总纲** — vulca-prototype-plan-v2.md — 更新观测同步表(§-1)的 ✅/❌ 标记\n2. **v2 精简版** — vulca-prototype-plan-v2-compact.md — 更新观测同步表(§0)的当前状态\n3. **动态融合** — vulca-l1l5-dynamic-fusion-design.md — 更新实现状态同步块\n4. **FC 架构** — agent-function-calling-architecture-2026-02-10.md — 更新实现状态块\n5. **融合联网版** — l1-l5-dynamic-fusion-design-2026-02-10.md — 同步实现状态\n6. **v2 审查** — v2-plan-review-2026-02-10.md — 如有新发现追加\n\n**辅助文档**（按需更新）：\n7. deep-audit — 如有差距变化\n8. roadmap — 如有路线变化\n9. d2-checklist — 如有 Schema 变化\n\n**MEMORY.md** — 更新 Phase 完成状态、关键学习点\n\n### 各文档当前时间戳\n${DOC_STATUS}\n\n### 一致性规则\n- v2-compact 是唯一真实来源（source of truth）\n- v2 总纲的观测同步表必须与 compact 一致\n- FC 架构文档的实现状态块必须与 compact 一致\n- 动态融合文档的实现状态块必须与 compact 一致\n- 只更新实际发生变化的部分，不要重写整个文件\n- 保持 MEMORY.md 在 200 行以内"
    }
}
EOF
exit 0
