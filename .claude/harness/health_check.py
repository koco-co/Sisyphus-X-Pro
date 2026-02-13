#!/usr/bin/env python3
"""
Sisyphus-X-Pro 基础健康检查脚本
在每次 Coding Agent 会话开始时运行,验证核心功能正常
"""

import sys
import json
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

try:
    import requests
    from app.database import engine
    from app.models import User, Project
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)


class HealthCheck:
    """基础健康检查"""

    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.frontend_url = "http://localhost:3000"
        self.passed_checks = []
        self.failed_checks = []

    def check_backend_health(self):
        """检查后端健康状态"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.passed_checks.append("后端健康检查")
                return True
            else:
                self.failed_checks.append(f"后端健康检查: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.failed_checks.append(f"后端健康检查: {str(e)}")
            return False

    def check_database_connection(self):
        """检查数据库连接"""
        try:
            import asyncio

            async def test_connection():
                async with engine.connect() as conn:
                    await conn.execute("SELECT 1")

            asyncio.run(test_connection())
            self.passed_checks.append("数据库连接")
            return True
        except Exception as e:
            self.failed_checks.append(f"数据库连接: {str(e)}")
            return False

    def check_api_docs_accessible(self):
        """检查 API 文档可访问"""
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                self.passed_checks.append("API 文档访问")
                return True
            else:
                self.failed_checks.append(f"API 文档访问: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.failed_checks.append(f"API 文档访问: {str(e)}")
            return False

    def check_frontend_running(self):
        """检查前端服务运行"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.passed_checks.append("前端服务")
                return True
            else:
                self.failed_checks.append(f"前端服务: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.failed_checks.append(f"前端服务: {str(e)}")
            return False

    def check_feature_list_exists(self):
        """检查功能清单文件存在"""
        feature_list_path = Path(__file__).parent / "feature_list.json"
        if feature_list_path.exists():
            try:
                with open(feature_list_path) as f:
                    data = json.load(f)
                total = data.get("metadata", {}).get("total_features", 0)
                completed = data.get("metadata", {}).get("completed_features", 0)
                self.passed_checks.append(f"功能清单 ({completed}/{total} 完成)")
                return True
            except Exception as e:
                self.failed_checks.append(f"功能清单: {str(e)}")
                return False
        else:
            self.failed_checks.append("功能清单: 文件不存在")
            return False

    def run_all_checks(self):
        """运行所有检查"""
        print("🔍 运行基础健康检查...")
        print("=" * 50)

        checks = [
            ("后端健康", self.check_backend_health),
            ("数据库连接", self.check_database_connection),
            ("API 文档", self.check_api_docs_accessible),
            ("前端服务", self.check_frontend_running),
            ("功能清单", self.check_feature_list_exists),
        ]

        for name, check_func in checks:
            print(f"\n检查: {name}...")
            check_func()
            time.sleep(0.5)

        self.print_summary()

    def print_summary(self):
        """打印检查摘要"""
        print("\n" + "=" * 50)
        print("📊 检查摘要:")
        print("=" * 50)

        if self.passed_checks:
            print("\n✅ 通过的检查:")
            for check in self.passed_checks:
                print(f"   ✓ {check}")

        if self.failed_checks:
            print("\n❌ 失败的检查:")
            for check in self.failed_checks:
                print(f"   ✗ {check}")

        total = len(self.passed_checks) + len(self.failed_checks)
        passed = len(self.passed_checks)
        print(f"\n总计: {passed}/{total} 检查通过")

        if self.failed_checks:
            print("\n⚠️  部分检查失败,请修复后再继续开发")
            return False
        else:
            print("\n✅ 所有检查通过,可以开始开发!")
            return True


if __name__ == "__main__":
    checker = HealthCheck()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
