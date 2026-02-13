#!/bin/bash
# Hooks安装脚本
# 将hooks复制到正确的位置并设置权限

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "📦 安装Agent Teams Hooks..."

# 确保hooks目录存在
HOOKS_DIR="$PROJECT_ROOT/.claude/hooks"
mkdir -p "$HOOKS_DIR"

# 复制hooks文件
for hook in teammate-idle.sh task-completed.sh stop_gate.sh pre-tool-use.sh post-tool-use.sh utils.sh; do
    src="$SCRIPT_DIR/$hook"
    dst="$HOOKS_DIR/$hook"

    if [ -f "$src" ]; then
        cp "$src" "$dst"
        chmod +x "$dst"
        echo "✅ 已安装: $hook"
    else
        echo "⚠️ 文件不存在: $src"
    fi
done

# 复制Python脚本
for script in check_agent_completion.py get_task_info.py check_doc_sync.py update_agent_status.py; do
    src="$SCRIPT_DIR/$script"
    dst="$HOOK_DIR/$script"

    if [ -f "$src" ]; then
        cp "$src" "$dst"
        chmod +x "$dst"
        echo "✅ 已安装: $script"
    else
        echo "⚠️ 文件不存在: $src"
    fi
done

# 创建日志文件
LOG_FILE="$PROJECT_ROOT/.claude/harness/hooks.log"
touch "$LOG_FILE"
echo "📝 日志文件: $LOG_FILE"

echo ""
echo "✅ Hooks安装完成!"
echo ""
echo "下一步: 运行更新脚本配置hooks"
echo ""
echo "  python3 .claude/hooks/UPDATE_v2.py"
echo ""
echo "或者手动配置 ~/.claude/settings.json (使用新的数组格式):"
echo ""
cat <<'EOF'
{
  "hooks": {
    "TeammateIdle": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/绝对路径/.claude/hooks/teammate-idle.sh"
          }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/绝对路径/.claude/hooks/task-completed.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": {},
        "hooks": [
          {
            "type": "command",
            "command": "/绝对路径/.claude/hooks/stop_gate.sh"
          }
        ]
      }
    ]
  }
}
EOF
echo ""
echo "⚠️ 重要: Claude Code新版hooks需要使用数组格式!"
