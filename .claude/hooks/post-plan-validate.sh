#!/bin/bash
# Post-plan validation hook for VULCA project
# Runs comprehensive tests after Claude finishes a response
# to ensure code quality AND document consistency after plan execution.
#
# Exit codes:
#   0 = all checks passed
#   2 = critical failure, block and report to Claude

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/home/yhryzy/projects/website}"
BACKEND_DIR="$PROJECT_DIR/wenxin-backend"
FRONTEND_DIR="$PROJECT_DIR/wenxin-moyun"
DOCS_DIR="$FRONTEND_DIR/docs"
VENV="$BACKEND_DIR/venv/bin/python"
LOG_FILE="/tmp/vulca-post-plan-validate.log"

# Initialize
echo "$(date '+%Y-%m-%d %H:%M:%S') - Post-plan validation started" > "$LOG_FILE"
ERRORS=()
WARNINGS=()

# ============================================
# 1. Python syntax check on changed files
# ============================================
echo "=== Step 1: Python syntax check ===" >> "$LOG_FILE"
if [ -d "$BACKEND_DIR" ] && [ -f "$VENV" ]; then
    # Check recently modified Python files (last 5 minutes)
    CHANGED_PY=$(find "$BACKEND_DIR/app" -name "*.py" -mmin -5 2>/dev/null || true)
    if [ -n "$CHANGED_PY" ]; then
        while IFS= read -r pyfile; do
            if ! "$VENV" -m py_compile "$pyfile" 2>> "$LOG_FILE"; then
                ERRORS+=("Syntax error in: $pyfile")
            fi
        done <<< "$CHANGED_PY"
        echo "Checked $(echo "$CHANGED_PY" | wc -l) Python files" >> "$LOG_FILE"
    else
        echo "No recently changed Python files" >> "$LOG_FILE"
    fi
fi

# ============================================
# 2. Critical import chain verification
# ============================================
echo "=== Step 2: Import chain check ===" >> "$LOG_FILE"
if [ -f "$VENV" ]; then
    cd "$BACKEND_DIR"

    # Core imports that must always work
    IMPORTS=(
        "from app.core.config import settings"
        "from app.services.email import email_service"
        "from app.services.cache_service import cache_service"
    )

    for imp in "${IMPORTS[@]}"; do
        if ! "$VENV" -c "$imp" 2>> "$LOG_FILE"; then
            ERRORS+=("Import failed: $imp")
        fi
    done

    # VULCA-specific imports (if prototype exists)
    if [ -d "$BACKEND_DIR/app/prototype" ]; then
        if ! "$VENV" -c "import app.prototype" 2>> "$LOG_FILE"; then
            ERRORS+=("Import failed: app.prototype")
        fi
    fi

    # VULCA core adapter
    if ! "$VENV" -c "from app.vulca.core.vulca_core_adapter import VULCACoreAdapter" 2>> "$LOG_FILE"; then
        WARNINGS+=("VULCA adapter import failed (non-critical)")
    fi
fi

# ============================================
# 3. Dependency consistency check
# ============================================
echo "=== Step 3: Dependency consistency ===" >> "$LOG_FILE"
if [ -f "$BACKEND_DIR/constraints.txt" ] && [ -f "$BACKEND_DIR/requirements.render.txt" ]; then
    # Check bcrypt version consistency
    CONSTRAINTS_BCRYPT=$(grep -oP 'bcrypt==\K[0-9.]+' "$BACKEND_DIR/constraints.txt" 2>/dev/null || echo "")
    RENDER_BCRYPT=$(grep -oP 'bcrypt==\K[0-9.]+' "$BACKEND_DIR/requirements.render.txt" 2>/dev/null || echo "")

    if [ -n "$CONSTRAINTS_BCRYPT" ] && [ -n "$RENDER_BCRYPT" ] && [ "$CONSTRAINTS_BCRYPT" != "$RENDER_BCRYPT" ]; then
        ERRORS+=("bcrypt version mismatch: constraints=$CONSTRAINTS_BCRYPT, render=$RENDER_BCRYPT")
    fi

    # Verify passlib+bcrypt compatibility
    if [ -f "$VENV" ]; then
        if ! "$VENV" -c "from passlib.hash import bcrypt; bcrypt.hash('test')" 2>> "$LOG_FILE"; then
            ERRORS+=("passlib+bcrypt incompatible")
        fi
    fi
fi

# ============================================
# 4. Frontend build check (if files changed)
# ============================================
echo "=== Step 4: Frontend check ===" >> "$LOG_FILE"
if [ -d "$FRONTEND_DIR" ]; then
    CHANGED_TS=$(find "$FRONTEND_DIR/src" -name "*.ts" -o -name "*.tsx" -mmin -5 2>/dev/null | head -5 || true)
    if [ -n "$CHANGED_TS" ]; then
        if [ -f "$FRONTEND_DIR/node_modules/.bin/tsc" ]; then
            cd "$FRONTEND_DIR"
            if ! npx tsc --noEmit --pretty false 2>> "$LOG_FILE"; then
                WARNINGS+=("TypeScript type errors detected (run npm run type-check)")
            fi
        fi
    fi
fi

# ============================================
# 5. Report generation check (prototype reports)
# ============================================
echo "=== Step 5: Report check ===" >> "$LOG_FILE"
REPORTS_DIR="$BACKEND_DIR/app/prototype/reports"
if [ -d "$REPORTS_DIR" ]; then
    REPORT_COUNT=$(find "$REPORTS_DIR" -name "*.md" -not -name "__init__.py" | wc -l)
    echo "Found $REPORT_COUNT report(s) in prototype/reports/" >> "$LOG_FILE"
fi

# ============================================
# 6. Prototype schema validation (D2 gate)
# ============================================
echo "=== Step 6: Prototype schema validation ===" >> "$LOG_FILE"
if [ -f "$BACKEND_DIR/app/prototype/validate_schema.py" ] && [ -f "$VENV" ]; then
    cd "$BACKEND_DIR"
    if ! SCHEMA_OUTPUT=$("$VENV" app/prototype/validate_schema.py 2>&1); then
        echo "$SCHEMA_OUTPUT" >> "$LOG_FILE"
        ERRORS+=("Prototype schema validation failed (validate_schema.py)")
    else
        echo "$SCHEMA_OUTPUT" >> "$LOG_FILE"
        if ! grep -q "ALL CHECKS PASSED" <<< "$SCHEMA_OUTPUT"; then
            ERRORS+=("Prototype schema validation output missing success marker")
        fi
    fi
fi

# ============================================
# 7. v2 核心文档一致性检查
# ============================================
echo "=== Step 7: v2 document consistency ===" >> "$LOG_FILE"

V2_FULL="$DOCS_DIR/vulca-prototype-plan-v2.md"
V2_COMPACT="$DOCS_DIR/vulca-prototype-plan-v2-compact.md"
V2_FC="$DOCS_DIR/agent-function-calling-architecture-2026-02-10.md"
V2_FUSION="$DOCS_DIR/vulca-l1l5-dynamic-fusion-design.md"
V2_FUSION_NET="$DOCS_DIR/l1-l5-dynamic-fusion-design-2026-02-10.md"
V2_REVIEW="$DOCS_DIR/v2-plan-review-2026-02-10.md"
STEP3_DESIGN="$REPORTS_DIR/step3-design-vs-implementation.md"

# Helper: safe grep count (avoids "0\n0" from grep -c + || echo)
safe_grep_count() {
    local count
    count=$(grep -c "$1" "$2" 2>/dev/null) || true
    echo "${count:-0}"
}

# --- 7a. Phase B FAISS status consistency ---
if [ -f "$V2_COMPACT" ] && [ -f "$V2_FULL" ]; then
    COMPACT_B=$(safe_grep_count "Phase B 已完成" "$V2_COMPACT")
    FULL_B_DONE=$(safe_grep_count "Scout FAISS.*✅" "$V2_FULL")
    FULL_B_NOT=$(safe_grep_count "Scout FAISS.*❌" "$V2_FULL")

    if [ "$COMPACT_B" -gt 0 ] && [ "$FULL_B_NOT" -gt 0 ] && [ "$FULL_B_DONE" -eq 0 ]; then
        WARNINGS+=("v2文档不一致: compact说Phase B已完成, 但总纲(v2.md)仍标记Scout FAISS为❌未实现 — 请同步总纲的观测同步表")
    fi
    echo "Phase B consistency: compact_done=$COMPACT_B, full_done=$FULL_B_DONE, full_not=$FULL_B_NOT" >> "$LOG_FILE"
fi

# --- 7b. Phase D Cultural Router consistency ---
if [ -f "$V2_COMPACT" ] && [ -f "$V2_FULL" ]; then
    COMPACT_D=$(safe_grep_count "Phase D 已完成" "$V2_COMPACT")
    FULL_D_NOT=$(safe_grep_count "文化路由.*❌" "$V2_FULL")

    if [ "$COMPACT_D" -gt 0 ] && [ "$FULL_D_NOT" -gt 0 ]; then
        WARNINGS+=("v2文档不一致: compact说Phase D已完成, 但总纲仍标记文化路由为❌ — 请同步总纲")
    fi
fi

# --- 7c. FC architecture doc vs compact ---
if [ -f "$V2_FC" ] && [ -f "$V2_COMPACT" ]; then
    FC_FAISS_NOT=$(safe_grep_count "FAISS.*未实现\|Phase B 待启动" "$V2_FC")
    COMPACT_B=$(safe_grep_count "Phase B 已完成" "$V2_COMPACT")

    if [ "$FC_FAISS_NOT" -gt 0 ] && [ "$COMPACT_B" -gt 0 ]; then
        WARNINGS+=("v2文档不一致: FC架构文档仍标记FAISS为未实现/Phase B待启动, 但compact已标记完成 — 请同步FC架构文档")
    fi
fi

# --- 7d. Fusion design doc vs compact ---
if [ -f "$V2_FUSION" ] && [ -f "$V2_COMPACT" ]; then
    FUSION_PHASE_B_PENDING=$(safe_grep_count "Phase B.*先完成\|Phase B FAISS 先完成" "$V2_FUSION")
    COMPACT_B=$(safe_grep_count "Phase B 已完成" "$V2_COMPACT")

    if [ "$FUSION_PHASE_B_PENDING" -gt 0 ] && [ "$COMPACT_B" -gt 0 ]; then
        WARNINGS+=("v2文档不一致: 动态融合设计文档仍引用'需Phase B先完成', 但Phase B已完成 — 请同步融合设计文档")
    fi
fi

# --- 7e. step3-design-vs-implementation consistency ---
if [ -f "$STEP3_DESIGN" ]; then
    # Exclude strikethrough lines (~~text~~) which indicate already-fixed items
    STEP3_B_PENDING=$(grep -v '~~' "$STEP3_DESIGN" 2>/dev/null | grep -c "Phase B 待启动\|Scout 仍用 Jaccard" 2>/dev/null) || true
    STEP3_B_PENDING="${STEP3_B_PENDING:-0}"
    if [ "$STEP3_B_PENDING" -gt 0 ]; then
        WARNINGS+=("step3文档过时: step3-design-vs-implementation.md仍包含'Phase B待启动'或'Scout仍用Jaccard' — 请更新")
    fi
fi

# --- 7f. Cross-doc ✅/❌ marker count sanity ---
if [ -f "$V2_COMPACT" ] && [ -f "$V2_FULL" ]; then
    COMPACT_DONE=$(safe_grep_count "✅.*Phase [A-D].*完成\|Phase [A-D].*✅" "$V2_COMPACT")
    FULL_DONE=$(safe_grep_count "✅.*Phase [A-D]\|Phase [A-D].*✅" "$V2_FULL")
    echo "Phase completion markers: compact=$COMPACT_DONE, full=$FULL_DONE" >> "$LOG_FILE"

    if [ "$COMPACT_DONE" -gt 0 ] && [ "$FULL_DONE" -eq 0 ]; then
        WARNINGS+=("v2文档不一致: compact有${COMPACT_DONE}个Phase完成标记, 但总纲没有 — 总纲可能需要更新")
    fi
fi

echo "Step 7 completed: $(echo "${WARNINGS[@]}" | grep -c "v2文档" 2>/dev/null || echo 0) doc inconsistencies found" >> "$LOG_FILE"

# ============================================
# Results
# ============================================
echo "" >> "$LOG_FILE"
echo "=== Results ===" >> "$LOG_FILE"
echo "Errors: ${#ERRORS[@]}" >> "$LOG_FILE"
echo "Warnings: ${#WARNINGS[@]}" >> "$LOG_FILE"

# Output JSON result
if [ ${#ERRORS[@]} -gt 0 ]; then
    ERROR_MSG=$(printf '%s; ' "${ERRORS[@]}")
    WARNING_MSG=""
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        WARNING_MSG=$(printf '%s; ' "${WARNINGS[@]}")
    fi

    echo "ERRORS: $ERROR_MSG" >> "$LOG_FILE"
    echo "CRITICAL VALIDATION FAILED: $ERROR_MSG" >&2

    # Return structured feedback to Claude
    cat <<EOF
{
    "decision": "block",
    "reason": "Post-plan validation failed. Errors: ${ERROR_MSG}${WARNING_MSG:+ Warnings: $WARNING_MSG} Fix these issues before proceeding."
}
EOF
    exit 2
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
    WARNING_MSG=$(printf '%s; ' "${WARNINGS[@]}")
    echo "WARNINGS: $WARNING_MSG" >> "$LOG_FILE"

    cat <<EOF
{
    "hookSpecificOutput": {
        "hookEventName": "Stop",
        "additionalContext": "Post-plan validation warnings: ${WARNING_MSG}"
    }
}
EOF
    exit 0
fi

echo "All checks passed" >> "$LOG_FILE"
echo '{"continue": true}'
exit 0
