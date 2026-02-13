#!/usr/bin/env python3
"""
检查Agent任务完成度的脚本
由TeammateIdle Hook调用
"""
import argparse
import json
import sys
from pathlib import Path


def check_agent_completion(agent_name: str, project_root: Path) -> dict:
    """检查Agent是否可以关闭"""
    teams_dir = Path.home() / ".claude" / "teams"
    tasks_dir = Path.home() / ".claude" / "tasks"

    # 读取team配置
    team_name = "autonomous-development"
    team_config_file = teams_dir / team_name / "config.json"

    if not team_config_file.exists():
        return {
            "can_shutdown": False,
            "reason": "Team配置文件不存在"
        }

    with open(team_config_file) as f:
        team_config = json.load(f)

    # 读取任务列表
    tasks_file = tasks_dir / team_name / "tasks.json"

    if not tasks_file.exists():
        return {
            "can_shutdown": True,
            "reason": "任务列表不存在,允许关闭"
        }

    with open(tasks_file) as f:
        tasks_data = json.load(f)

    # 找出分配给该Agent的任务
    agent_tasks = [
        task for task in tasks_data.get("tasks", [])
        if task.get("owner") == agent_name
    ]

    if not agent_tasks:
        # 该Agent没有任务,可以关闭
        return {
            "can_shutdown": True,
            "reason": "没有分配任务"
        }

    # 检查任务状态
    completed_tasks = [t for t in agent_tasks if t.get("status") == "completed"]
    pending_tasks = [t for t in agent_tasks if t.get("status") != "completed"]

    if pending_tasks:
        # 还有未完成任务
        return {
            "can_shutdown": False,
            "reason": f"还有{len(pending_tasks)}个未完成任务",
            "pending_tasks": [t["id"] for t in pending_tasks],
            "completed_tasks": len(completed_tasks),
            "total_tasks": len(agent_tasks)
        }

    # 所有任务完成,检查是否是特殊Agent (E2E, QA等)
    if agent_name in ["e2e-agent", "qa-agent"]:
        # 这些Agent需要额外的质量检查
        # (由TaskCompleted Hook处理)
        return {
            "can_shutdown": True,
            "reason": "所有任务完成,质量检查已在TaskCompleted Hook中通过"
        }

    # 普通Agent,所有任务完成,可以关闭
    return {
        "can_shutdown": True,
        "reason": f"所有{len(agent_tasks)}个任务已完成",
        "completed_tasks": len(completed_tasks),
        "total_tasks": len(agent_tasks)
    }


def main():
    parser = argparse.ArgumentParser(description="检查Agent完成度")
    parser.add_argument("--agent-name", required=True, help="Agent名称")
    parser.add_argument("--project-root", default=Path.cwd(), help="项目根目录")

    args = parser.parse_args()
    project_root = Path(args.project_root)

    result = check_agent_completion(args.agent_name, project_root)

    # 输出结果
    print(f"can_shutdown={result['can_shutdown']}")
    print(f"reason={result['reason']}")

    if "pending_tasks" in result:
        print(f"pending_tasks={','.join(result['pending_tasks'])}")

    # 返回退出码
    sys.exit(0 if result["can_shutdown"] else 1)


if __name__ == "__main__":
    main()
