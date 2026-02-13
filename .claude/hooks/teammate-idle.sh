#!/bin/bash
# TeammateIdle Hook
# 当Agent即将变为idle时触发
# 用于自动检查Agent是否可以关闭

set -euo pipefail

# 接收环境变量
AGENT_NAME="${CLAUDE_TEAMMATE_NAME:-unknown}"
TEAM_NAME="${CLAUDE_TEAM_NAME:-unknown}"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

echo "🔔 [TeammateIdle Hook] Agent: $AGENT_NAME" >> "$PROJECT_ROOT/.claude/harness/hooks.log"

# 加载辅助函数
source "$PROJECT_ROOT/.claude/hooks/utils.sh"

# 检查Agent是否可以关闭
check_result=$(python3 "$PROJECT_ROOT/.claude/hooks/check_agent_completion.py" \
    --agent-name "$AGENT_NAME" \
    --project-root "$PROJECT_ROOT" 2>&1)

# 解析检查结果
if echo "$check_result" | grep -q "can_shutdown=true"; then
    # ✅ Agent可以关闭
    log_info "Agent $AGENT_NAME 可以自动关闭"

    # 清理Agent资源
    cleanup_agent_resources "$AGENT_NAME" "$PROJECT_ROOT"

    # 更新任务状态
    python3 "$PROJECT_ROOT/.claude/hooks/update_agent_status.py" \
        --agent-name "$AGENT_NAME" \
        --status "completed" \
        --project-root "$PROJECT_ROOT"

    # 返回0 - 允许Agent进入idle
    exit 0

elif echo "$check_result" | grep -q "can_shutdown=false"; then
    # ❌ Agent还不能关闭
    reason=$(echo "$check_result" | grep -oP 'reason=\K[^ ]+' || echo "未知原因")

    log_warning "Agent $AGENT_NAME 不能关闭: $reason"

    # 生成反馈消息
    feedback="⚠️ 你还有未完成的任务或质量检查未通过: $reason

请继续完成以下工作后再尝试关闭:
1. 检查所有分配的任务是否完成
2. 运行质量检查 (ruff/pyright/npm run lint等)
3. 确保测试覆盖率 >= 80%
4. E2E Agent需要所有测试通过"

    # 返回2 - 拒绝进入idle,保持Agent工作
    echo "$feedback"
    exit 2

else
    # 解析失败
    log_error "无法解析Agent完成度检查结果"
    exit 1
fi
