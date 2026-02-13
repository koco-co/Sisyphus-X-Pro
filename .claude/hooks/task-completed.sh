#!/bin/bash
# TaskCompleted Hook
# 当一个任务被标记为完成时触发
# 用于自动验证质量门禁

set -euo pipefail

# 接收环境变量
AGENT_NAME="${CLAUDE_TASK_AGENT_NAME:-unknown}"
TASK_ID="${CLAUDE_TASK_ID:-unknown}"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

echo "🔔 [TaskCompleted Hook] Agent: $AGENT_NAME, Task: $TASK_ID" >> "$PROJECT_ROOT/.claude/harness/hooks.log"

# 加载辅助函数
source "$PROJECT_ROOT/.claude/hooks/utils.sh"

# 读取任务信息
task_info=$(python3 "$PROJECT_ROOT/.claude/hooks/get_task_info.py" \
    --task-id "$TASK_ID" \
    --project-root "$PROJECT_ROOT")

# 提取Agent类型
agent_type=$(echo "$task_info" | grep -oP 'agent_type=\K[^ ]+' || echo "unknown")

# 根据Agent类型运行不同的质量检查
case "$agent_type" in
    "backend-agent")
        log_info "运行Backend质量检查..."
        check_result=$(python3 "$PROJECT_ROOT/.claude/harness/quality_gates.py" backend 2>&1)
        ;;

    "frontend-agent")
        log_info "运行Frontend质量检查..."
        check_result=$(python3 "$PROJECT_ROOT/.claude/harness/quality_gates.py" frontend 2>&1)
        ;;

    "e2e-agent")
        log_info "运行E2E质量检查..."
        check_result=$(python3 "$PROJECT_ROOT/.claude/harness/quality_gates.py" e2e 2>&1)
        ;;

    "doc-agent")
        log_info "运行文档同步检查..."
        check_result=$(python3 "$PROJECT_ROOT/.claude/hooks/check_doc_sync.py" 2>&1)
        ;;

    "qa-agent")
        log_info "跳过QA Agent的质量检查 (最终验收)"
        check_result="✅ QA Agent任务完成"
        ;;

    *)
        log_info "Agent类型 $agent_type 不需要质量检查"
        check_result="✅ 无需检查"
        ;;
esac

# 检查是否通过
if echo "$check_result" | grep -q "❌\|⛔\|FAIL"; then
    # 质量检查失败
    log_warning "任务 $TASK_ID 质量检查失败"

    feedback="❌ 质量门禁检查失败！

$check_result

请修复以下问题后重新提交任务:
1. 运行相应的质量检查命令
2. 修复所有错误和警告
3. 确保测试覆盖率 >= 80%
4. E2E Agent必须所有测试通过"

    # 返回2 - 阻止任务完成
    echo "$feedback"
    exit 2

else
    # 质量检查通过
    log_info "任务 $TASK_ID 质量检查通过"

    # 记录到进度日志
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "### [$timestamp] Task $TASK_ID by $AGENT_NAME - 完成 ✅" >> "$PROJECT_ROOT/.claude/harness/claude-progress.txt"

    # 返回0 - 允许任务完成
    exit 0
fi
