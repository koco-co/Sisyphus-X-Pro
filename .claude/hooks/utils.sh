#!/bin/bash
# Hooks辅助函数

# 日志级别
LOG_INFO=0
LOG_WARNING=1
LOG_ERROR=2

# 颜色输出
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

# 日志函数
log_info() {
    echo -e "${COLOR_GREEN}[INFO]${COLOR_RESET} $*" | tee -a "${LOG_FILE:-/dev/stderr}"
}

log_warning() {
    echo -e "${COLOR_YELLOW}[WARNING]${COLOR_RESET} $*" | tee -a "${LOG_FILE:-/dev/stderr}"
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $*" | tee -a "${LOG_FILE:-/dev/stderr}"
}

# 清理Agent资源
cleanup_agent_resources() {
    local agent_name=$1
    local project_root=$2

    log_info "清理Agent资源: $agent_name"

    # 删除状态文件
    local state_file="$project_root/.claude/harness/${agent_name}_state.json"
    if [ -f "$state_file" ]; then
        rm "$state_file"
        log_info "已删除: $state_file"
    fi

    # 删除关闭请求文件
    local request_file="$project_root/.claude/harness/${agent_name}_shutdown_request.json"
    if [ -f "$request_file" ]; then
        rm "$request_file"
        log_info "已删除: $request_file"
    fi

    # 删除日志文件
    local log_file="$project_root/.claude/harness/agent_logs/${agent_name}.log"
    if [ -f "$log_file" ]; then
        # 保留最后100行
        tail -n 100 "$log_file" > "${log_file}.tmp"
        mv "${log_file}.tmp" "$log_file"
        log_info "已压缩日志: $log_file"
    fi
}

# 检查Agent任务完成度
check_agent_task_completion() {
    local agent_name=$1
    local project_root=$2

    # 使用Python脚本检查
    python3 "$project_root/.claude/hooks/check_agent_completion.py" \
        --agent-name "$agent_name" \
        --project-root "$project_root"
}

# 获取Agent类型
get_agent_type() {
    local agent_name=$1

    case "$agent_name" in
        "product-agent")
            echo "requirement"
            ;;
        "architect-agent")
            echo "architecture"
            ;;
        "backend-agent")
            echo "development"
            ;;
        "frontend-agent")
            echo "development"
            ;;
        "e2e-agent")
            echo "e2e_testing"
            ;;
        "doc-agent")
            echo "documentation"
            ;;
        "qa-agent")
            echo "qa"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# 更新进度文件
update_progress_file() {
    local agent_name=$1
    local status=$2
    local project_root=$3

    local progress_file="$project_root/.claude/harness/claude-progress.txt"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "### [$timestamp] Agent: $agent_name - 状态: $status" >> "$progress_file"
}

# 发送通知 (可选)
send_notification() {
    local title=$1
    local message=$2

    # macOS通知
    if command -v terminal-notifier &> /dev/null; then
        terminal-notifier -title "$title" -message "$message"
    fi

    # Linux通知
    if command -v notify-send &> /dev/null; then
        notify-send "$title" "$message"
    fi
}
