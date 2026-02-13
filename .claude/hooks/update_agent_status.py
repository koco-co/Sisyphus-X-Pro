#!/usr/bin/env python3
"""
更新Agent状态的脚本
"""
import argparse
import json
from datetime import datetime
from pathlib import Path


def update_agent_status(agent_name: str, status: str, project_root: Path):
    """更新Agent状态"""
    teams_dir = Path.home() / ".claude" / "teams"
    team_name = "autonomous-development"
    team_config_file = teams_dir / team_name / "config.json"

    if not team_config_file.exists():
        print(f"⚠️ Team配置文件不存在: {team_config_file}")
        return

    with open(team_config_file) as f:
        team_config = json.load(f)

    # 更新Agent状态
    for member in team_config.get("members", []):
        if member.get("name") == agent_name:
            member["status"] = status
            member["status_updated_at"] = datetime.now().isoformat()
            break

    # 保存配置
    with open(team_config_file, "w") as f:
        json.dump(team_config, f, indent=2)

    print(f"✅ 已更新Agent状态: {agent_name} -> {status}")


def main():
    parser = argparse.ArgumentParser(description="更新Agent状态")
    parser.add_argument("--agent-name", required=True, help="Agent名称")
    parser.add_argument("--status", required=True, help="新状态")
    parser.add_argument("--project-root", default=Path.cwd(), help="项目根目录")

    args = parser.parse_args()
    project_root = Path(args.project_root)

    update_agent_status(args.agent_name, args.status, project_root)


if __name__ == "__main__":
    main()
