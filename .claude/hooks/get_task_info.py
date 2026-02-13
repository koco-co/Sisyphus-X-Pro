#!/usr/bin/env python3
"""
获取任务信息的脚本
由TaskCompleted Hook调用
"""
import argparse
import json
import sys
from pathlib import Path


def get_task_info(task_id: str, project_root: Path) -> dict:
    """获取任务信息"""
    tasks_dir = Path.home() / ".claude" / "tasks"
    team_name = "autonomous-development"
    tasks_file = tasks_dir / team_name / "tasks.json"

    if not tasks_file.exists():
        return {
            "task_id": task_id,
            "error": "任务列表文件不存在"
        }

    with open(tasks_file) as f:
        tasks_data = json.load(f)

    # 查找任务
    task = next(
        (t for t in tasks_data.get("tasks", []) if t["id"] == task_id),
        None
    )

    if not task:
        return {
            "task_id": task_id,
            "error": "任务不存在"
        }

    # 提取Agent类型
    owner = task.get("owner", "unknown")
    subject = task.get("subject", "")
    description = task.get("description", "")

    return {
        "task_id": task_id,
        "agent_type": owner,
        "subject": subject,
        "description": description,
        "status": task.get("status", "unknown")
    }


def main():
    parser = argparse.ArgumentParser(description="获取任务信息")
    parser.add_argument("--task-id", required=True, help="任务ID")
    parser.add_argument("--project-root", default=Path.cwd(), help="项目根目录")

    args = parser.parse_args()
    project_root = Path(args.project_root)

    result = get_task_info(args.task_id, project_root)

    # 输出结果
    print(f"task_id={result['task_id']}")
    print(f"agent_type={result.get('agent_type', 'unknown')}")

    if "error" in result:
        print(f"error={result['error']}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
