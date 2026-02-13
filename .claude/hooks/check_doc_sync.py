#!/usr/bin/env python3
"""
检查文档同步的脚本
由TaskCompleted Hook调用
"""
import subprocess
import sys
from pathlib import Path


def check_doc_sync(project_root: Path) -> dict:
    """检查文档是否同步更新"""
    # 获取Git变更
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1"],
        capture_output=True,
        text=True,
        cwd=project_root
    )

    if result.returncode != 0:
        return {
            "passed": False,
            "reason": "无法获取Git变更"
        }

    changed_files = result.stdout.strip().split("\n")

    # 检查必需的文档
    required_docs = ["README.md", "CLAUDE.md", "CHANGELOG.md"]
    updated_docs = [f for f in required_docs if f in changed_files]

    missing_docs = set(required_docs) - set(updated_docs)

    if missing_docs:
        return {
            "passed": False,
            "reason": f"文档未同步更新: 缺少 {', '.join(missing_docs)}",
            "missing_docs": list(missing_docs)
        }

    return {
        "passed": True,
        "reason": "所有必需文档已更新",
        "updated_docs": updated_docs
    }


def main():
    project_root = Path.cwd()

    result = check_doc_sync(project_root)

    if result["passed"]:
        print(f"✅ {result['reason']}")
        sys.exit(0)
    else:
        print(f"❌ {result['reason']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
