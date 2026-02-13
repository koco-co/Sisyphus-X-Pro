#!/usr/bin/env python3
"""
质量门禁检查脚本

用于在无人值守开发模式中检查各个阶段的质量标准。
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import Literal, TypedDict


class CheckResult(TypedDict):
    """检查结果类型"""
    passed: bool
    message: str
    details: dict | None


class QualityGates:
    """质量门禁检查器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_dir = project_root / "backend"
        self.frontend_dir = project_root / "frontend"

    def run_all_checks(self) -> dict[str, CheckResult]:
        """运行所有质量检查"""
        results = {
            "backend_lint": self.check_backend_lint(),
            "backend_types": self.check_backend_types(),
            "backend_coverage": self.check_backend_coverage(),
            "backend_tests": self.check_backend_tests(),
            "frontend_lint": self.check_frontend_lint(),
            "frontend_types": self.check_frontend_types(),
            "frontend_tests": self.check_frontend_tests(),
            "e2e_tests": self.check_e2e_tests(),
        }

        return results

    def check_backend_lint(self) -> CheckResult:
        """检查后端代码风格 (ruff)"""
        print("🔍 检查后端代码风格 (ruff)...")

        try:
            result = subprocess.run(
                ["ruff", "check", str(self.backend_dir), "--fix"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return {
                    "passed": True,
                    "message": "✅ ruff check 通过",
                    "details": {"output": result.stdout},
                }
            else:
                return {
                    "passed": False,
                    "message": f"❌ ruff check 失败\n{result.stdout}",
                    "details": {"exit_code": result.returncode, "output": result.stdout},
                }
        except FileNotFoundError:
            return {
                "passed": False,
                "message": "⚠️ ruff 未安装",
                "details": None,
            }

    def check_backend_types(self) -> CheckResult:
        """检查后端类型 (pyright)"""
        print("🔍 检查后端类型注解 (pyright)...")

        try:
            result = subprocess.run(
                ["pyright", str(self.backend_dir)],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return {
                    "passed": True,
                    "message": "✅ pyright 通过",
                    "details": {"output": result.stdout},
                }
            else:
                return {
                    "passed": False,
                    "message": f"❌ pyright 失败\n{result.stdout}",
                    "details": {"exit_code": result.returncode, "output": result.stdout},
                }
        except FileNotFoundError:
            return {
                "passed": False,
                "message": "⚠️ pyright 未安装",
                "details": None,
            }

    def check_backend_coverage(self) -> CheckResult:
        """检查后端测试覆盖率"""
        print("🔍 检查后端测试覆盖率...")

        try:
            result = subprocess.run(
                [
                    "pytest",
                    str(self.backend_dir / "tests"),
                    "--cov=app",
                    "--cov-report=json",
                    "--cov-report=term",
                ],
                capture_output=True,
                text=True,
                cwd=self.backend_dir,
            )

            # 读取覆盖率报告
            coverage_file = self.backend_dir / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    total_coverage = coverage_data["totals"]["percent_covered"]

                if total_coverage >= 80:
                    return {
                        "passed": True,
                        "message": f"✅ 测试覆盖率: {total_coverage:.1f}%",
                        "details": {"coverage": total_coverage},
                    }
                else:
                    return {
                        "passed": False,
                        "message": f"❌ 测试覆盖率不足: {total_coverage:.1f}% < 80%",
                        "details": {"coverage": total_coverage},
                    }
            else:
                return {
                    "passed": False,
                    "message": "❌ 无法读取覆盖率报告",
                    "details": {"exit_code": result.returncode, "output": result.stdout},
                }
        except FileNotFoundError:
            return {
                "passed": False,
                "message": "⚠️ pytest 未安装",
                "details": None,
            }

    def check_backend_tests(self) -> CheckResult:
        """检查后端单元测试"""
        print("🔍 运行后端单元测试...")

        try:
            result = subprocess.run(
                ["pytest", str(self.backend_dir / "tests"), "-v"],
                capture_output=True,
                text=True,
                cwd=self.backend_dir,
            )

            if result.returncode == 0:
                return {
                    "passed": True,
                    "message": "✅ 后端单元测试全部通过",
                    "details": {"output": result.stdout},
                }
            else:
                # 统计失败数量
                failed_count = result.stdout.count("FAILED")
                return {
                    "passed": False,
                    "message": f"❌ {failed_count} 个后端测试失败",
                    "details": {"exit_code": result.returncode, "output": result.stdout},
                }
        except FileNotFoundError:
            return {
                "passed": False,
                "message": "⚠️ pytest 未安装",
                "details": None,
            }

    def check_frontend_lint(self) -> CheckResult:
        """检查前端代码风格 (ESLint)"""
        print("🔍 检查前端代码风格 (ESLint)...")

        try:
            result = subprocess.run(
                ["npm", "run", "lint"],
                capture_output=True,
                text=True,
                cwd=self.frontend_dir,
            )

            if result.returncode == 0:
                return {
                    "passed": True,
                    "message": "✅ ESLint 通过",
                    "details": {"output": result.stdout},
                }
            else:
                return {
                    "passed": False,
                    "message": f"❌ ESLint 失败\n{result.stdout}",
                    "details": {"exit_code": result.returncode, "output": result.stdout},
                }
        except FileNotFoundError:
            return {
                "passed": False,
                "message": "⚠️ npm 未安装",
                "details": None,
            }

    def check_frontend_types(self) -> CheckResult:
        """检查前端类型 (TypeScript)"""
        print("🔍 检查前端类型 (TypeScript)...")

        try:
            result = subprocess.run(
                ["tsc", "-b"],
                capture_output=True,
                text=True,
                cwd=self.frontend_dir,
            )

            if result.returncode == 0:
                return {
                    "passed": True,
                    "message": "✅ TypeScript 检查通过",
                    "details": {"output": result.stdout},
                }
            else:
                return {
                    "passed": False,
                    "message": f"❌ TypeScript 检查失败\n{result.stdout}",
                    "details": {"exit_code": result.returncode, "output": result.stdout},
                }
        except FileNotFoundError:
            return {
                "passed": False,
                "message": "⚠️ tsc 未安装",
                "details": None,
            }

    def check_frontend_tests(self) -> CheckResult:
        """检查前端组件测试"""
        print("🔍 运行前端组件测试...")

        try:
            result = subprocess.run(
                ["npm", "test", "--", "--run"],
                capture_output=True,
                text=True,
                cwd=self.frontend_dir,
            )

            if result.returncode == 0:
                return {
                    "passed": True,
                    "message": "✅ 前端组件测试全部通过",
                    "details": {"output": result.stdout},
                }
            else:
                return {
                    "passed": False,
                    "message": f"❌ 前端测试失败\n{result.stdout}",
                    "details": {"exit_code": result.returncode, "output": result.stdout},
                }
        except FileNotFoundError:
            return {
                "passed": False,
                "message": "⚠️ npm 未安装",
                "details": None,
            }

    def check_e2e_tests(self) -> CheckResult:
        """检查端到端测试"""
        print("🔍 运行端到端测试 (Playwright)...")

        try:
            result = subprocess.run(
                ["npx", "playwright", "test"],
                capture_output=True,
                text=True,
                cwd=self.frontend_dir,
            )

            if result.returncode == 0:
                return {
                    "passed": True,
                    "message": "✅ E2E测试全部通过",
                    "details": {"output": result.stdout},
                }
            else:
                # 统计失败数量
                failed_count = result.stdout.count("failed")
                return {
                    "passed": False,
                    "message": f"❌ {failed_count} 个E2E测试失败",
                    "details": {"exit_code": result.returncode, "output": result.stdout},
                }
        except FileNotFoundError:
            return {
                "passed": False,
                "message": "⚠️ Playwright 未安装",
                "details": None,
            }


def check_phase(phase: Literal["backend", "frontend", "e2e", "all"]) -> dict[str, CheckResult]:
    """检查指定阶段的质量门禁"""
    project_root = Path.cwd()
    gates = QualityGates(project_root)

    if phase == "backend":
        return {
            "lint": gates.check_backend_lint(),
            "types": gates.check_backend_types(),
            "coverage": gates.check_backend_coverage(),
            "tests": gates.check_backend_tests(),
        }
    elif phase == "frontend":
        return {
            "lint": gates.check_frontend_lint(),
            "types": gates.check_frontend_types(),
            "tests": gates.check_frontend_tests(),
        }
    elif phase == "e2e":
        return {
            "e2e": gates.check_e2e_tests(),
        }
    else:  # all
        return gates.run_all_checks()


def print_results(results: dict[str, CheckResult]) -> bool:
    """打印检查结果并返回是否全部通过"""
    print("\n" + "=" * 60)
    print("📊 质量门禁检查结果")
    print("=" * 60)

    all_passed = True
    for name, result in results.items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} - {name}")
        print(f"    {result['message']}")

        if not result["passed"]:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 所有质量门禁检查通过!")
        return True
    else:
        print("\n⛔ 质量门禁检查失败,请修复后重试")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python quality_gates.py <phase>")
        print("phase: backend | frontend | e2e | all")
        sys.exit(1)

    phase = sys.argv[1]
    results = check_phase(phase)  # type: ignore
    all_passed = print_results(results)

    sys.exit(0 if all_passed else 1)
