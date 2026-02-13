#!/bin/bash
# Stop Hook - 会话结束时的最终检查
# 确保会话结束时代码库处于干净状态

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
LOG_FILE="$PROJECT_ROOT/.claude/harness/hooks.log"

echo "🔔 [Stop Hook] 会话结束检查" >> "$LOG_FILE"
echo "📅 时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

# 加载辅助函数
source "$PROJECT_ROOT/.claude/hooks/utils.sh"

log_info "开始会话结束检查..."

# 检查清单
issues=()

# 1. 检查Git状态
log_info "检查Git状态..."
cd "$PROJECT_ROOT"

if git status --porcelain | grep -q "^M"; then
    modified_files=$(git diff --name-only | head -5)
    issues+=("有未提交的修改: ${modified_files}")
    log_warning "发现未提交的修改"
else
    log_info "✅ Git状态干净"
fi

# 2. 检查console.log
log_info "检查console.log..."
if grep -r "console.log" "$PROJECT_ROOT/frontend/src" --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v "node_modules" | head -1; then
    issues+=("前端代码中有console.log")
    log_warning "发现console.log"
else
    log_info "✅ 无console.log"
fi

if grep -r "print(" "$PROJECT_ROOT/backend/app" --include="*.py" 2>/dev/null | head -1; then
    issues+=("后端代码中有print()")
    log_warning "发现print()"
else
    log_info "✅ 无print()"
fi

# 3. 检查临时文件
log_info "检查临时文件..."
temp_patterns=(
    "*.tmp"
    "*.bak"
    "*.swp"
    ".DS_Store"
    "Thumbs.db"
)

for pattern in "${temp_patterns[@]}"; do
    if find "$PROJECT_ROOT" -name "$pattern" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -1 | grep -q .; then
        issues+=("发现临时文件: $pattern")
        log_warning "发现临时文件: $pattern"
    fi
done

# 4. 检查Agent状态 (如果是无人值守模式)
if [ -f "$PROJECT_ROOT/.claude/harness/ralph_loop_state.json" ]; then
    log_info "检测到无人值守模式状态文件"

    # 检查是否有未完成的Agent
    if [ -d "$HOME/.claude/teams/autonomous-development" ]; then
        active_agents=$(jq -r '.members[] | select(.status != "completed") | .name' \
            "$HOME/.claude/teams/autonomous-development/config.json" 2>/dev/null || echo "")

        if [ -n "$active_agents" ]; then
            log_info "仍有活跃的Agent: $active_agents"
            # 这不是错误,只是记录
        fi
    fi
fi

# 5. 生成会话总结
log_info "生成本次会话总结..."

session_summary="$PROJECT_ROOT/.claude/harness/session_summary_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "# 会话总结"
    echo ""
    echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "**项目**: $PROJECT_ROOT"
    echo ""
    echo "## 检查结果"
    echo ""

    if [ ${#issues[@]} -eq 0 ]; then
        echo "✅ **所有检查通过** - 代码库处于干净状态"
    else
        echo "⚠️ **发现 ${#issues[@]} 个问题**"
        echo ""
        for issue in "${issues[@]}"; do
            echo "- $issue"
        done
    fi

    echo ""
    echo "## Git状态"
    echo ""
    git status --short 2>/dev/null || echo "无法获取Git状态"

    echo ""
    echo "## 最近的提交"
    echo ""
    git log --oneline -5 2>/dev/null || echo "无法获取提交历史"

} > "$session_summary"

log_info "会话总结已保存: $session_summary"

# 决定是否阻止会话结束
if [ ${#issues[@]} -gt 0 ]; then
    log_warning "会话结束检查发现问题"

    # 构建警告消息
    warning_msg="⚠️ 会话结束检查发现问题:

"

    for issue in "${issues[@]}"; do
        warning_msg+="  • $issue
"
    done

    warning_msg+="
建议:
1. 提交或回退未提交的修改
2. 移除console.log/print()调试代码
3. 清理临时文件
4. 查看完整报告: $session_summary

是否仍要结束会话?"

    # 输出警告但不阻止 (exit 0)
    # 如果要强制阻止,使用 exit 2
    echo "$warning_msg"
    exit 0
else
    log_info "✅ 会话结束检查全部通过"

    # 清理临时状态文件
    if [ -f "$PROJECT_ROOT/.claude/harness/temp_state.json" ]; then
        rm "$PROJECT_ROOT/.claude/harness/temp_state.json"
        log_info "已清理临时状态文件"
    fi

    exit 0
fi
