#!/bin/bash
# PreToolUse Hook - 工具使用前的验证
# 防止误操作和危险命令

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
LOG_FILE="$PROJECT_ROOT/.claude/harness/hooks.log"

# 接收环境变量
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
# TOOL_PARAMETERS 可能是复杂的多行内容,需要小心处理

echo "🔔 [PreToolUse Hook] 工具: $TOOL_NAME" >> "$LOG_FILE"

case "$TOOL_NAME" in
    "Bash")
        # 检查危险命令
        # TOOL_PARAMETERS 可能包含命令内容
        if [ -n "${TOOL_PARAMETERS:-}" ]; then
            # 检查是否有危险操作
            dangerous_patterns=(
                "rm -rf /"
                "rm -rf /*"
                "dd if=/dev/zero"
                "mkfs"
                ":(){ :|:& };:"  # fork bomb
                "chmod -R 777 /"
                "> /dev/sda"
            )

            for pattern in "${dangerous_patterns[@]}"; do
                if echo "$TOOL_PARAMETERS" | grep -q "$pattern"; then
                    echo "❌ 拒绝执行危险命令: $pattern" >> "$LOG_FILE"
                    echo "❌ 检测到危险操作,已被阻止"
                    exit 2
                fi
            done
        fi
        ;;

    "Edit")
        # 检查是否编辑了重要文件
        # TOOL_PARAMETERS 可能包含文件路径
        if [ -n "${TOOL_PARAMETERS:-}" ]; then
            # 防止编辑.git目录下的文件
            if echo "$TOOL_PARAMETERS" | grep -q "/\.git/"; then
                echo "❌ 拒绝编辑.git目录下的文件" >> "$LOG_FILE"
                echo "❌ 不允许编辑.git目录下的文件"
                exit 2
            fi

            # 防止编辑hooks脚本本身 (特殊情况下需要)
            # if echo "$TOOL_PARAMETERS" | grep -q "\.claude/hooks/"; then
            #     echo "⚠️ 尝试编辑hooks文件" >> "$LOG_FILE"
            # fi
        fi
        ;;

    "Write")
        # 检查是否写入敏感路径
        if [ -n "${TOOL_PARAMETERS:-}" ]; then
            # 防止覆盖.git目录
            if echo "$TOOL_PARAMETERS" | grep -q "/\.git/"; then
                echo "❌ 拒绝写入.git目录" >> "$LOG_FILE"
                echo "❌ 不允许写入.git目录"
                exit 2
            fi

            # 检查是否在项目根目录外写入
            if echo "$TOOL_PARAMETERS" | grep -q "^/[^/]" && ! echo "$TOOL_PARAMETERS" | grep -q "^$PROJECT_ROOT"; then
                echo "⚠️ 尝试在项目根目录外写入: $TOOL_PARAMETERS" >> "$LOG_FILE"
            fi
        fi
        ;;

esac

# 默认允许
exit 0
