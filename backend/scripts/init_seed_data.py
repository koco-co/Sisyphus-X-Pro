"""Seed data initialization script.

This script initializes the database with built-in keywords and global parameters.
Run this script after creating the database tables.
"""
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.global_param import GlobalParam
from app.models.keyword import Keyword


async def seed_keywords(session: AsyncSession) -> None:
    """Seed built-in keywords."""
    keywords = [
        Keyword(
            type="发送请求",
            name="HTTP 请求",
            method_name="http_request",
            code="# HTTP 请求关键字代码\nimport requests\n\ndef http_request(interface_id: int):\n    \"\"\"发送 HTTP 请求\"\"\"\n    # TODO: 实现 HTTP 请求逻辑\n    pass",
            params=[{"name": "interface_id", "description": "接口 ID"}],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="断言类型",
            name="JSON 断言",
            method_name="assert_json",
            code="# JSON 断言代码\n\ndef assert_json(jsonpath: str, operator: str, expected: str):\n    \"\"\"断言 JSON 响应字段\"\"\"\n    # TODO: 实现 JSON 断言逻辑\n    pass",
            params=[
                {"name": "jsonpath", "description": "JSON 路径表达式"},
                {"name": "operator", "description": "操作符 (eq, ne, gt, lt, contains)"},
                {"name": "expected", "description": "期望值"},
            ],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="断言类型",
            name="Header 断言",
            method_name="assert_header",
            code="# Header 断言代码\n\ndef assert_header(key: str, operator: str, expected: str):\n    \"\"\"断言响应头\"\"\"\n    # TODO: 实现 Header 断言逻辑\n    pass",
            params=[
                {"name": "key", "description": "Header 键"},
                {"name": "operator", "description": "操作符"},
                {"name": "expected", "description": "期望值"},
            ],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="断言类型",
            name="Cookie 断言",
            method_name="assert_cookie",
            code="# Cookie 断言代码\n\ndef assert_cookie(name: str, operator: str, expected: str):\n    \"\"\"断言响应 Cookie\"\"\"\n    # TODO: 实现 Cookie 断言逻辑\n    pass",
            params=[
                {"name": "name", "description": "Cookie 名称"},
                {"name": "operator", "description": "操作符"},
                {"name": "expected", "description": "期望值"},
            ],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="断言类型",
            name="状态码断言",
            method_name="assert_status_code",
            code="# 状态码断言代码\n\ndef assert_status_code(expected: int):\n    \"\"\"断言 HTTP 状态码\"\"\"\n    # TODO: 实现状态码断言逻辑\n    pass",
            params=[{"name": "expected", "description": "期望的状态码"}],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="断言类型",
            name="耗时断言",
            method_name="assert_elapsed",
            code="# 耗时断言代码\n\ndef assert_elapsed(max_ms: int):\n    \"\"\"断言请求耗时不超过指定值\"\"\"\n    # TODO: 实现耗时断言逻辑\n    pass",
            params=[{"name": "max_ms", "description": "最大耗时（毫秒）"}],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="提取变量",
            name="JSON 提取",
            method_name="extract_json",
            code="# JSON 提取代码\n\ndef extract_json(name: str, scope: str, jsonpath: str):\n    \"\"\"从 JSON 响应中提取变量\"\"\"\n    # TODO: 实现 JSON 提取逻辑\n    pass",
            params=[
                {"name": "name", "description": "变量名"},
                {"name": "scope", "description": "作用域 (scenario, global)"},
                {"name": "jsonpath", "description": "JSON 路径表达式"},
            ],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="提取变量",
            name="Header 提取",
            method_name="extract_header",
            code="# Header 提取代码\n\ndef extract_header(name: str, scope: str, key: str):\n    \"\"\"从响应头中提取变量\"\"\"\n    # TODO: 实现 Header 提取逻辑\n    pass",
            params=[
                {"name": "name", "description": "变量名"},
                {"name": "scope", "description": "作用域"},
                {"name": "key", "description": "Header 键"},
            ],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="提取变量",
            name="Cookie 提取",
            method_name="extract_cookie",
            code="# Cookie 提取代码\n\ndef extract_cookie(name: str, scope: str, cookie_name: str):\n    \"\"\"从响应 Cookie 中提取变量\"\"\"\n    # TODO: 实现 Cookie 提取逻辑\n    pass",
            params=[
                {"name": "name", "description": "变量名"},
                {"name": "scope", "description": "作用域"},
                {"name": "cookie_name", "description": "Cookie 名称"},
            ],
            is_builtin=True,
            is_enabled=True,
        ),
        Keyword(
            type="数据库操作",
            name="SQL 操作",
            method_name="sql_operation",
            code="# SQL 操作代码\n\ndef sql_operation(db_config_id: int, sql: str):\n    \"\"\"执行 SQL 操作\"\"\"\n    # TODO: 实现 SQL 操作逻辑\n    pass",
            params=[
                {"name": "db_config_id", "description": "数据库配置 ID"},
                {"name": "sql", "description": "SQL 语句"},
            ],
            is_builtin=True,
            is_enabled=True,
        ),
    ]

    for keyword in keywords:
        session.add(keyword)

    await session.commit()
    print(f"✅ Seeded {len(keywords)} built-in keywords")


async def seed_global_params(session: AsyncSession) -> None:
    """Seed built-in global parameters."""
    global_params = [
        GlobalParam(
            class_name="StringUtils",
            method_name="uuid",
            description="生成指定长度的 UUID 字符串",
            code="""class StringUtils:
    def uuid(self, length: int = 32) -> str:
        \"\"\"生成指定长度的 UUID 字符串

        Args:
            length: UUID 长度, 默认 32

        Returns:
            str: UUID 字符串
        \"\"\"
        import uuid
        return uuid.uuid4().hex[:length]""",
            params_in=[{"name": "length", "type": "int", "description": "UUID 长度, 默认 32"}],
            params_out=[{"type": "str", "description": "UUID 字符串"}],
            is_builtin=True,
        ),
        GlobalParam(
            class_name="StringUtils",
            method_name="random_string",
            description="生成随机字符串",
            code="""class StringUtils:
    def random_string(self, length: int = 8) -> str:
        \"\"\"生成随机字符串

        Args:
            length: 字符串长度, 默认 8

        Returns:
            str: 随机字符串
        \"\"\"
        import random, string
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))""",
            params_in=[{"name": "length", "type": "int", "description": "字符串长度, 默认 8"}],
            params_out=[{"type": "str", "description": "随机字符串"}],
            is_builtin=True,
        ),
        GlobalParam(
            class_name="TimeUtils",
            method_name="timestamp",
            description="获取当前时间戳",
            code="""class TimeUtils:
    def timestamp(self) -> int:
        \"\"\"获取当前时间戳

        Returns:
            int: Unix 时间戳
        \"\"\"
        import time
        return int(time.time())""",
            params_in=[],
            params_out=[{"type": "int", "description": "Unix 时间戳"}],
            is_builtin=True,
        ),
    ]

    for param in global_params:
        session.add(param)

    await session.commit()
    print(f"✅ Seeded {len(global_params)} built-in global parameters")


async def main() -> None:
    """Main seed function."""
    print("🌱 Starting seed data initialization...")
    print()

    async with async_session() as session:
        try:
            # Seed keywords
            await seed_keywords(session)
            print()

            # Seed global parameters
            await seed_global_params(session)
            print()

            print("✅ Seed data initialization completed successfully!")
        except Exception as e:
            print(f"❌ Error during seed data initialization: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
