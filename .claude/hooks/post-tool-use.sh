#!/bin/bash
# PostToolUse Hook - 工具使用后的自动操作
# 自动格式化、检查等

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
LOG_FILE="$PROJECT_ROOT/.claude/harness/hooks.log"

# 接收环境变量
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"

# 只在特定工具后执行操作
case "$TOOL_NAME" in
    "Edit"|"Write")
        # 检查是否编辑了TypeScript文件
        # TOOL_PARAMETERS 在PostToolUse中包含修改后的文件路径
        if [ -n "${TOOL_PARAMETERS:-}" ]; then
            file_path=$(echo "$TOOL_PARAMETERS" | grep -oP 'filePath=\K[^,}]+' || echo "")

            if [[ "$file_path" =~ \.(ts|tsx|js|jsx)$ ]]; then
                echo "🔔 [PostToolUse Hook] 检测到TS/JS文件修改: $file_path" >> "$LOG_FILE"

                # 自动格式化 (如果配置了prettier)
                if [ -f "$PROJECT_ROOT/frontend/package.json" ] && command -v prettier &>/dev/null; then
                    echo "  → 运行prettier格式化" >> "$LOG_FILE"
                    cd "$PROJECT_ROOT/frontend"
                    prettier --write "$file_path" 2>/dev/null || true
                fi

                # 自动类型检查 (如果配置了)
                if [ -f "$PROJECT_ROOT/frontend/tsconfig.json" ] && command -v tsc &>/dev/null; then
                    echo "  → 运行tsc类型检查" >> "$LOG_FILE"
                    cd "$PROJECT_ROOT/frontend"
                    tsc --noEmit "$file_path" 2>/dev/null || true
                fi
            fi

            # 检查是否编辑了Python文件
            if [[ "$file_path" =~ \.py$ ]]; then
                echo "🔔 [PostToolUse Hook] 检测到Python文件修改: $file_path" >> "$LOG_FILE"

                # 自动格式化 (如果配置了ruff)
                if [ -f "$PROJECT_ROOT/backend/pyproject.toml" ] && command -v ruff &>/dev/null; then
                    echo "  → 运行ruff格式化" >> "$LOG_FILE"
                    cd "$PROJECT_ROOT/backend"
                    ruff check --fix "$file_path" 2>/dev/null || true
                fi
            fi
        fi
        ;;

    "Bash")
        # 检查是否运行了git相关命令
        if [ -n "${TOOL_PARAMETERS:-}" ]; then
            if echo "$TOOL_PARAMETERS" | grep -q "^git commit"; then
                echo "🔔 [PostToolUse Hook] 检测到git commit" >> "$LOG_FILE"

                # 提交后自动更新进度日志
                if [ -f "$PROJECT_ROOT/.claude/harness/claude-progress.txt" ]; then
                    {
                        echo ""
                        echo "### $(date '+%Y-%m-%d %H:%M:%S') - Git提交"
                        echo "提交信息: $(echo "$TOOL_PARAMETERS" | head -1)"
                    } >> "$PROJECT_ROOT/.claude/harness/claude-progress.txt"
                fi
            fi
        fi
        ;;
esac

# 默认允许
exit 0
