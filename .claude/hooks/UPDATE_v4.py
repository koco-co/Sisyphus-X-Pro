#!/usr/bin/env python3
"""
更新脚本 - 正确的hooks格式 (v4)
"""
import json
from pathlib import Path

def update_hooks():
    settings_file = Path.home() / ".claude" / "settings.json"
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    print(f"项目根目录: {project_root}")

    # 读取现有配置
    with open(settings_file) as f:
        settings = json.load(f)

    # 正确的hooks格式
    # TeammateIdle, TaskCompleted, Stop 不支持matcher - 省略matcher字段
    # PreToolUse, PostToolUse 需要matcher字符串 - 使用空字符串匹配所有

    hooks_config = {
        "TeammateIdle": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": f"bash {project_root / '.claude/hooks/teammate-idle.sh'}"
                    }
                ]
            }
        ],
        "TaskCompleted": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": f"bash {project_root / '.claude/hooks/task-completed.sh'}"
                    }
                ]
            }
        ],
        "Stop": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": f"bash {project_root / '.claude/hooks/stop_gate.sh'}"
                    }
                ]
            }
        ],
        # PreToolUse和PostToolUse使用matcher字符串,空字符串匹配所有工具
        "PreToolUse": [
            {
                "matcher": "",  # 空字符串匹配所有工具
                "hooks": [
                    {
                        "type": "command",
                        "command": f"bash {project_root / '.claude/hooks/pre-tool-use.sh'}"
                    }
                ]
            }
        ],
        "PostToolUse": [
            {
                "matcher": "",  # 空字符串匹配所有工具
                "hooks": [
                    {
                        "type": "command",
                        "command": f"bash {project_root / '.claude/hooks/post-tool-use.sh'}"
                    }
                ]
            }
        ]
    }

    # 更新hooks配置
    settings["hooks"] = hooks_config

    # 保存配置
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=2)

    print("✅ Hooks配置已更新 (正确格式v4)")
    print("\n已配置的hooks:")
    for hook_type, hook_configs in hooks_config.items():
        for hook_config in hook_configs:
            command = hook_config["hooks"][0]["command"]
            matcher = hook_config.get("matcher", "(无matcher)")
            print(f"  {hook_type}: matcher=\"{matcher}\", command={command}")

    print("\n✅ 完成! 请重启Claude Code使hooks生效")
    print("\n说明:")
    print("  - TeammateIdle, TaskCompleted, Stop: 不支持matcher,总是触发")
    print("  - PreToolUse, PostToolUse: matcher=\"\" 表示匹配所有工具")

if __name__ == "__main__":
    update_hooks()
