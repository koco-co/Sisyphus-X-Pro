#!/usr/bin/env python3
"""
端到端测试辅助工具
为 Coding Agent 提供 Playwright 测试模板和工具函数
"""

import json
import subprocess
from pathlib import Path
from typing import Optional


class E2ETestHelper:
    """E2E 测试辅助类"""

    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.api_base_url = "http://localhost:8000/api/v1"
        self.feature_list_path = Path(__file__).parent / "feature_list.json"

    def load_feature_list(self) -> dict:
        """加载功能清单"""
        with open(self.feature_list_path) as f:
            return json.load(f)

    def get_pending_features(self, category: Optional[str] = None) -> list[dict]:
        """获取待实现的功能"""
        data = self.load_feature_list()
        pending = []

        for cat_name, cat_data in data["categories"].items():
            if category and cat_name != category:
                continue
            for feature in cat_data["features"]:
                if not feature.get("passes", False):
                    pending.append(feature)

        # 按优先级排序
        priority_order = {
            "authentication": 1,
            "dashboard": 2,
            "project_management": 3,
            "keyword_management": 4,
            "interface_management": 5,
            "scenario_orchestration": 6,
            "test_plan": 7,
            "test_report": 8,
            "global_params": 9,
        }
        pending.sort(key=lambda f: priority_order.get(
            self._get_feature_category(f["id"]),
            999
        ))
        pending.sort(key=lambda f: f["id"])
        return pending

    def _get_feature_category(self, feature_id: str) -> str:
        """根据功能 ID 获取分类"""
        data = self.load_feature_list()
        for cat_name, cat_data in data["categories"].items():
            for feature in cat_data["features"]:
                if feature["id"] == feature_id:
                    return cat_name
        return ""

    def generate_playwright_test(self, feature: dict) -> str:
        """生成 Playwright 测试代码"""
        test_id = feature["id"]
        description = feature["description"]
        steps = feature.get("steps", [])

        # 将测试步骤转换为 Playwright 代码
        test_code = f'''import {{ test, expect }} from "@playwright/test";

test("{description} ({test_id})", async ({{ page }}) => {{
'''
        for i, step in enumerate(steps, 1):
            test_code += f"  // 步骤 {i}: {step}\n"
            test_code += self._step_to_code(step)
            test_code += "\n"

        test_code += "}});\n"
        return test_code

    def _step_to_code(self, step: str) -> str:
        """将测试步骤转换为代码"""
        step_lower = step.lower()

        if "导航到" in step or "navigate" in step_lower:
            return '  await page.goto("http://localhost:3000/相应的页面");'

        elif "输入" in step and "邮箱" in step:
            return '  await page.fill("[name=\\"email\\"]", "test@example.com");'

        elif "输入" in step and "密码" in step:
            return '  await page.fill("[name=\\"password\\"]", "password123");'

        elif "点击" in step or "click" in step_lower:
            button_desc = step.split("点击")[-1].strip() if "点击" in step else "按钮"
            return f'  await page.click(\'[type="submit"], [role="button"]\');  // {button_desc}'

        elif "验证" in step or "verify" in step_lower:
            if "跳转" in step or "redirect" in step_lower:
                return '  await expect(page).toHaveURL(/dashboard/);'
            elif "显示" in step or "visible" in step_lower:
                return '  await expect(page.locator("body")).toContainText("期望的文本");'

        return f'  // TODO: 实现步骤: {step}'

    def run_playwright_test(self, test_file: Path) -> tuple[bool, str]:
        """运行 Playwright 测试"""
        try:
            result = subprocess.run(
                ["npx", "playwright", "test", str(test_file)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            success = result.returncode == 0
            return success, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "测试超时"
        except Exception as e:
            return False, str(e)


def print_status():
    """打印当前状态"""
    helper = E2ETestHelper()
    data = helper.load_feature_list()

    total = data["metadata"]["total_features"]
    completed = data["metadata"]["completed_features"]
    rate = data["metadata"]["completion_rate"]

    print("\n📊 功能完成状态:")
    print("=" * 50)
    print(f"总计: {total} 个功能")
    print(f"已完成: {completed} 个")
    print(f"完成率: {rate:.1f}%")
    print()

    # 按分类显示
    for cat_name, cat_data in data["categories"].items():
        cat_features = cat_data["features"]
        completed_count = sum(1 for f in cat_features if f.get("passes", False))
        total_count = len(cat_features)
        cat_name_cn = cat_data["name"]
        status = "✅" if completed_count == total_count else "🔄"
        print(f"{status} {cat_name_cn}: {completed_count}/{total_count}")

    print()

    # 显示待完成的高优先级功能
    pending = helper.get_pending_features()
    if pending:
        print("📋 下一个待实现功能:")
        next_feature = pending[0]
        print(f"  - {next_feature['id']}: {next_feature['description']}")
        print()


if __name__ == "__main__":
    print_status()
