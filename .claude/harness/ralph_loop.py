#!/usr/bin/env python3
"""
Ralph Loop集成脚本

用于在上下文耗尽时保存状态并触发会话恢复。
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class RalphLoopManager:
    """Ralph Loop管理器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.harness_dir = project_root / ".claude" / "harness"
        self.teams_dir = Path.home() / ".claude" / "teams"
        self.tasks_dir = Path.home() / ".claude" / "tasks"

    def estimate_context_usage(self) -> float:
        """估算当前上下文使用率 (伪实现)"""
        # 在实际使用中,这个值需要由Claude Code提供
        # 这里返回一个模拟值
        return 0.0

    def save_session_state(
        self,
        session_id: str,
        current_phase: str,
        completed_tasks: list[str],
        pending_tasks: list[dict[str, Any]],
        agent_status: dict[str, Any],
    ) -> None:
        """保存完整会话状态"""
        state = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "current_phase": current_phase,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "agent_status": agent_status,
        }

        # 保存状态文件
        state_file = self.harness_dir / "ralph_loop_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        print(f"💾 已保存会话状态: {state_file}")

        # 更新进度日志
        self._append_to_progress_log(
            f"[Ralph Loop] 保存会话状态 - Phase: {current_phase}, "
            f"已完成: {len(completed_tasks)}, 待完成: {len(pending_tasks)}"
        )

    def load_session_state(self) -> dict[str, Any] | None:
        """加载会话状态"""
        state_file = self.harness_dir / "ralph_loop_state.json"

        if not state_file.exists():
            print("⚠️ 未找到会话状态文件")
            return None

        with open(state_file) as f:
            state = json.load(f)

        print(f"📂 已加载会话状态: {state_file}")
        return state

    def _append_to_progress_log(self, message: str) -> None:
        """追加消息到进度日志"""
        progress_file = self.harness_dir / "claude-progress.txt"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n### {timestamp} - {message}\n"

        with open(progress_file, "a") as f:
            f.write(log_entry)

    def create_restart_script(self) -> Path:
        """创建重启脚本"""
        script_content = """#!/bin/bash
# Ralph Loop 重启脚本
# 自动生成于: {date}

echo "🔄 Ralph Loop: 准备恢复会话..."
echo ""

# 显示当前状态
echo "📊 当前会话状态:"
if [ -f ".claude/harness/ralph_loop_state.json" ]; then
    cat .claude/harness/ralph_loop_state.json | python3 -m json.tool
else
    echo "⚠️ 未找到状态文件"
fi

echo ""
echo "下一步:"
echo "1. 在Claude Code中说: 恢复无人值守模式"
echo "2. 或运行: /resume 并加载状态文件"
echo ""

# 检查Agent Teams状态
echo "🤖 Agent Teams状态:"
if [ -d ~/.claude/teams/autonomous-development ]; then
    echo "✅ Team配置存在"
    ls ~/.claude/teams/autonomous-development/
else
    echo "⚠️ Team配置不存在,需要重新创建"
fi
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        script_path = self.harness_dir / "ralph_loop_restart.sh"
        with open(script_path, "w") as f:
            f.write(script_content)

        # 添加执行权限
        script_path.chmod(0o755)

        print(f"📜 已创建重启脚本: {script_path}")
        return script_path

    def trigger_ralph_loop(
        self,
        session_id: str,
        current_phase: str,
        completed_tasks: list[str],
        pending_tasks: list[dict[str, Any]],
        agent_status: dict[str, Any],
    ) -> None:
        """触发Ralph Loop"""
        print("\n" + "=" * 60)
        print("🔄 Ralph Loop 触发")
        print("=" * 60)

        # 1. 保存完整状态
        self.save_session_state(
            session_id, current_phase, completed_tasks, pending_tasks, agent_status
        )

        # 2. 创建重启脚本
        restart_script = self.create_restart_script()

        # 3. 显示恢复指南
        print("\n" + "=" * 60)
        print("📋 会话恢复指南")
        print("=" * 60)
        print()
        print("当前上下文即将耗尽,已保存完整状态。")
        print()
        print("下一步操作:")
        print("  方式1 (推荐): 运行重启脚本")
        print(f"    {restart_script}")
        print()
        print("  方式2: 在Claude Code中说:")
        print("    恢复无人值守模式")
        print()
        print("  方式3: 使用 /resume 命令:")
        print("    /resume .claude/harness/ralph_loop_state.json")
        print()
        print("=" * 60)

    def resume_from_state(self, state_file: str | None = None) -> dict[str, Any] | None:
        """从状态文件恢复会话"""
        # 加载状态
        if state_file:
            state_path = Path(state_file)
        else:
            state_path = self.harness_dir / "ralph_loop_state.json"

        if not state_path.exists():
            print(f"⚠️ 状态文件不存在: {state_path}")
            return None

        with open(state_path) as f:
            state = json.load(f)

        print("\n" + "=" * 60)
        print("✅ 会话状态已恢复")
        print("=" * 60)
        print()
        print(f"会话ID: {state['session_id']}")
        print(f"保存时间: {state['timestamp']}")
        print(f"当前阶段: {state['current_phase']}")
        print(f"已完成任务: {len(state['completed_tasks'])}")
        print(f"待完成任务: {len(state['pending_tasks'])}")
        print()
        print("Agent状态:")
        for agent_name, agent_state in state["agent_status"].items():
            status_emoji = {
                "working": "🔄",
                "idle": "⏸️",
                "completed": "✅",
                "error": "❌",
            }.get(agent_state["status"], "❓")
            print(f"  {status_emoji} {agent_name}: {agent_state['status']}")
            if agent_state.get("current_task"):
                print(f"     任务: {agent_state['current_task']}")
        print()
        print("=" * 60)

        return state

    def create_resume_prompt(self) -> str:
        """创建恢复提示词"""
        state = self.load_session_state()

        if not state:
            return "无法加载会话状态,请手动恢复"

        prompt = f"""# 恢复无人值守开发模式

## 会话信息
- 会话ID: {state['session_id']}
- 保存时间: {state['timestamp']}
- 当前阶段: {state['current_phase']}

## 任务状态
- 已完成: {len(state['completed_tasks'])} 个任务
- 待完成: {len(state['pending_tasks'])} 个任务

## 待完成任务清单
"""

        for i, task in enumerate(state["pending_tasks"], 1):
            prompt += f"{i}. {task.get('subject', task.get('id', 'Unknown'))}\n"
            if task.get("description"):
                prompt += f"   {task['description']}\n"

        prompt += f"""
## Agent状态
"""

        for agent_name, agent_state in state["agent_status"].items():
            prompt += f"- **{agent_name}**: {agent_state['status']}\n"
            if agent_state.get("current_task"):
                prompt += f"  当前任务: {agent_state['current_task']}\n"

        prompt += """
## 下一步行动
请继续执行待完成任务,从当前阶段 `{current_phase}` 开始。
"""

        return prompt


def main():
    """命令行入口"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python ralph_loop.py <command> [args...]")
        print("命令:")
        print("  trigger <session_id> <phase>  - 触发Ralph Loop")
        print("  resume [state_file]  - 从状态文件恢复会话")
        print("  prompt  - 生成恢复提示词")
        print("  status  - 显示当前状态")
        sys.exit(1)

    command = sys.argv[1]
    project_root = Path.cwd()
    manager = RalphLoopManager(project_root)

    if command == "trigger":
        if len(sys.argv) < 4:
            print("用法: python ralph_loop.py trigger <session_id> <phase>")
            sys.exit(1)

        session_id = sys.argv[2]
        current_phase = sys.argv[3]

        # 模拟数据 - 实际使用时应该从真实环境获取
        manager.trigger_ralph_loop(
            session_id=session_id,
            current_phase=current_phase,
            completed_tasks=[],
            pending_tasks=[],
            agent_status={},
        )

    elif command == "resume":
        state_file = sys.argv[2] if len(sys.argv) > 2 else None
        manager.resume_from_state(state_file)

    elif command == "prompt":
        prompt = manager.create_resume_prompt()
        print(prompt)

    elif command == "status":
        state = manager.load_session_state()
        if state:
            print(json.dumps(state, indent=2, ensure_ascii=False))
        else:
            print("未找到会话状态")

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
