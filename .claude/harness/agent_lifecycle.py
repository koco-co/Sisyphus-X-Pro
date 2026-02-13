#!/usr/bin/env python3
"""
Agent生命周期管理脚本

用于管理无人值守开发模式中Agent的创建、分配任务、监控和关闭。
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class AgentLifecycleManager:
    """Agent生命周期管理器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.harness_dir = project_root / ".claude" / "harness"
        self.teams_dir = Path.home() / ".claude" / "teams"
        self.tasks_dir = Path.home() / ".claude" / "tasks"

    def save_agent_state(self, agent_name: str, state: dict[str, Any]) -> None:
        """保存Agent状态"""
        state_file = self.harness_dir / f"{agent_name}_state.json"
        with open(state_file, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "agent": agent_name,
                    "state": state,
                },
                f,
                indent=2,
            )
        print(f"💾 已保存Agent状态: {state_file}")

    def load_agent_state(self, agent_name: str) -> dict[str, Any] | None:
        """加载Agent状态"""
        state_file = self.harness_dir / f"{agent_name}_state.json"
        if state_file.exists():
            with open(state_file) as f:
                data = json.load(f)
                return data["state"]
        return None

    def create_shutdown_request(self, agent_name: str, reason: str) -> dict[str, Any]:
        """创建关闭请求"""
        return {
            "type": "shutdown_request",
            "agent": agent_name,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }

    def check_agent_completion(
        self, agent_name: str, task_ids: list[str]
    ) -> dict[str, Any]:
        """检查Agent任务完成度"""
        # 读取任务列表
        team_name = "autonomous-development"
        task_list_file = self.tasks_dir / team_name / "tasks.json"

        if not task_list_file.exists():
            return {"completed": False, "reason": "任务列表文件不存在"}

        with open(task_list_file) as f:
            tasks_data = json.load(f)

        # 检查指定任务的完成情况
        completed_tasks = []
        pending_tasks = []

        for task in tasks_data.get("tasks", []):
            if task["id"] in task_ids:
                if task.get("status") == "completed":
                    completed_tasks.append(task["id"])
                else:
                    pending_tasks.append(task["id"])

        completion_rate = len(completed_tasks) / len(task_ids) if task_ids else 0

        return {
            "completed": completion_rate == 1.0,
            "completion_rate": completion_rate,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
        }

    def run_quality_checks_for_agent(
        self, agent_name: str
    ) -> dict[str, Any]:
        """为Agent运行质量检查"""
        # 导入质量门禁脚本
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "quality_gates",
            self.harness_dir / "quality_gates.py",
        )
        quality_gates = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(quality_gates)

        # 根据Agent类型运行不同的检查
        if agent_name == "backend-agent":
            results = quality_gates.check_phase("backend")
        elif agent_name == "frontend-agent":
            results = quality_gates.check_phase("frontend")
        elif agent_name == "e2e-agent":
            results = quality_gates.check_phase("e2e")
        else:
            results = {}

        # 检查是否全部通过
        all_passed = all(result.get("passed", False) for result in results.values())

        return {
            "all_passed": all_passed,
            "results": results,
        }

    def can_agent_shutdown(
        self, agent_name: str, task_ids: list[str]
    ) -> dict[str, Any]:
        """检查Agent是否可以关闭"""
        # 1. 检查任务完成度
        completion = self.check_agent_completion(agent_name, task_ids)

        if not completion["completed"]:
            return {
                "can_shutdown": False,
                "reason": f"任务未完成 ({completion['completion_rate']:.1%})",
                "details": completion,
            }

        # 2. 运行质量检查
        quality = self.run_quality_checks_for_agent(agent_name)

        if not quality["all_passed"]:
            return {
                "can_shutdown": False,
                "reason": "质量检查未通过",
                "details": quality,
            }

        # 3. 可以关闭
        return {
            "can_shutdown": True,
            "reason": "所有任务完成,质量检查通过",
        }

    def request_agent_shutdown(self, agent_name: str, reason: str) -> None:
        """请求Agent关闭"""
        request = self.create_shutdown_request(agent_name, reason)

        # 保存关闭请求
        request_file = self.harness_dir / f"{agent_name}_shutdown_request.json"
        with open(request_file, "w") as f:
            json.dump(request, f, indent=2)

        print(f"📤 已发送关闭请求给 {agent_name}")
        print(f"   原因: {reason}")

    def handle_shutdown_response(
        self, agent_name: str, response: dict[str, Any]
    ) -> None:
        """处理Agent的关闭响应"""
        if response.get("approve"):
            print(f"✅ {agent_name} 已关闭")

            # 清理状态文件
            state_file = self.harness_dir / f"{agent_name}_state.json"
            if state_file.exists():
                state_file.unlink()

            request_file = self.harness_dir / f"{agent_name}_shutdown_request.json"
            if request_file.exists():
                request_file.unlink()

        else:
            print(f"⚠️ {agent_name} 拒绝关闭")
            print(f"   原因: {response.get('content', '未知')}")

            # 恢复任务状态
            # (需要通过TaskUpdate实现)

    def monitor_agent(self, agent_name: str, task_ids: list[str]) -> None:
        """监控Agent状态"""
        print(f"👀 监控Agent: {agent_name}")

        while True:
            # 检查是否可以关闭
            can_shutdown = self.can_agent_shutdown(agent_name, task_ids)

            if can_shutdown["can_shutdown"]:
                # 请求关闭
                self.request_agent_shutdown(agent_name, can_shutdown["reason"])
                break
            else:
                # 打印状态
                print(f"   状态: {can_shutdown['reason']}")
                # 等待一段时间后再检查
                import time

                time.sleep(30)

    def cleanup_agent_resources(self, agent_name: str) -> None:
        """清理Agent资源"""
        files_to_cleanup = [
            self.harness_dir / f"{agent_name}_state.json",
            self.harness_dir / f"{agent_name}_shutdown_request.json",
            self.harness_dir / f"{agent_name}_logs.txt",
        ]

        for file in files_to_cleanup:
            if file.exists():
                file.unlink()
                print(f"🗑️ 已清理: {file}")


def main():
    """命令行入口"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python agent_lifecycle.py <command> [args...]")
        print("命令:")
        print("  check <agent_name> <task_ids...>  - 检查Agent是否可以关闭")
        print("  request_shutdown <agent_name> <reason>  - 请求Agent关闭")
        print("  cleanup <agent_name>  - 清理Agent资源")
        sys.exit(1)

    command = sys.argv[1]
    project_root = Path.cwd()
    manager = AgentLifecycleManager(project_root)

    if command == "check":
        if len(sys.argv) < 4:
            print("用法: python agent_lifecycle.py check <agent_name> <task_ids...>")
            sys.exit(1)

        agent_name = sys.argv[2]
        task_ids = sys.argv[3:]

        result = manager.can_agent_shutdown(agent_name, task_ids)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        sys.exit(0 if result["can_shutdown"] else 1)

    elif command == "request_shutdown":
        if len(sys.argv) < 4:
            print("用法: python agent_lifecycle.py request_shutdown <agent_name> <reason>")
            sys.exit(1)

        agent_name = sys.argv[2]
        reason = " ".join(sys.argv[3:])

        manager.request_agent_shutdown(agent_name, reason)

    elif command == "cleanup":
        if len(sys.argv) < 3:
            print("用法: python agent_lifecycle.py cleanup <agent_name>")
            sys.exit(1)

        agent_name = sys.argv[2]
        manager.cleanup_agent_resources(agent_name)

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
