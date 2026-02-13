"""Safe function execution utility for global parameter functions."""

import re
import ast
from typing import Any, Dict, List, Tuple
from datetime import datetime
import time
import random
import string


class FunctionExecutor:
    """Safe executor for global parameter functions.

    Provides sandboxed execution environment for user-defined functions.
    """

    # Built-in safe functions available to user code
    BUILTINS = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "filter": filter,
        "float": float,
        "int": int,
        "isinstance": isinstance,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "range": range,
        "reversed": reversed,
        "round": round,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
        "datetime": datetime,
        "time": time,
        "random": random,
        "string": string,
    }

    def __init__(self, functions: Dict[str, Any]):
        """Initialize function executor.

        Args:
            functions: Dictionary mapping function names to callable objects
        """
        self.functions = {**self.BUILTINS, **functions}

    def extract_function_calls(self, text: str) -> List[str]:
        """Extract all function calls from {{}} placeholders.

        Args:
            text: Text containing {{function()}} placeholders

        Returns:
            List of function call expressions
        """
        pattern = r"\{\{([^}]+)\}\}"
        matches = re.findall(pattern, text)
        return [m.strip() for m in matches]

    def validate_function_call(self, call_expr: str) -> bool:
        """Validate function call expression for safety.

        Args:
            call_expr: Function call expression (e.g., "current_time()")

        Returns:
            True if safe, False otherwise
        """
        try:
            # Parse the expression
            tree = ast.parse(call_expr, mode="eval")

            # Walk the AST and check for dangerous operations
            for node in ast.walk(tree):
                # Disallow imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    return False

                # Disallow attribute access on dangerous modules
                if isinstance(node, ast.Attribute):
                    if hasattr(node.value, "id"):
                        module_name = node.value.id
                        if module_name in ["os", "sys", "subprocess", "eval", "exec", "open"]:
                            return False

                # Only allow function calls and names
                if not isinstance(
                    node,
                    (
                        ast.Expression,
                        ast.Call,
                        ast.Name,
                        ast.Constant,
                        ast.Load,
                        ast.BinOp,
                        ast.UnaryOp,
                        ast.Compare,
                        ast.BoolOp,
                        ast.Num,
                        ast.Str,
                        ast.List,
                        ast.Tuple,
                        ast.Dict,
                    ),
                ):
                    continue

            return True

        except (SyntaxError, ValueError):
            return False

    def execute_function(self, call_expr: str, context: Dict[str, Any]) -> Any:
        """Execute a single function call.

        Args:
            call_expr: Function call expression (e.g., "current_time()")
            context: Execution context variables

        Returns:
            Function result

        Raises:
            ValueError: If function call is invalid or unsafe
        """
        # Validate safety
        if not self.validate_function_call(call_expr):
            raise ValueError(f"Unsafe or invalid function call: {call_expr}")

        try:
            # Execute in restricted environment
            exec_globals = {**self.functions, **context}
            result = eval(call_expr, exec_globals, {})
            return result

        except Exception as e:
            raise ValueError(f"Function execution failed: {call_expr}: {str(e)}") from e

    def parse_text(self, text: str, context: Dict[str, Any]) -> Tuple[str, List[str], bool, str]:
        """Parse text and replace {{function()}} with actual values.

        Supports nested function calls like {{outer(inner())}}.

        Args:
            text: Text containing function call placeholders
            context: Execution context variables

        Returns:
            Tuple of (parsed_text, functions_called, success, error_message)
        """
        pattern = r"\{\{([^}]+)\}\}"
        functions_called = []

        def replace_func(match):
            expr = match.group(1).strip()

            # Skip if already processed
            if expr in functions_called:
                return match.group(0)

            # Track function call
            functions_called.append(expr)

            try:
                # Execute function
                result = self.execute_function(expr, context)
                return str(result)
            except Exception as e:
                # On error, return original placeholder
                return match.group(0)

        try:
            # Apply replacement
            parsed_text = re.sub(pattern, replace_func, text)
            return parsed_text, functions_called, True, ""

        except Exception as e:
            return text, functions_called, False, str(e)


# Built-in utility functions
def to_uppercase(s: str) -> str:
    """Convert string to uppercase.

    Args:
        s: Input string

    Returns:
        Uppercase string
    """
    return s.upper()


def to_lowercase(s: str) -> str:
    """Convert string to lowercase.

    Args:
        s: Input string

    Returns:
        Lowercase string
    """
    return s.lower()


def current_time() -> str:
    """Get current time in YYYY-MM-DD HH:mm:ss format.

    Returns:
        Current time formatted string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def current_timestamp() -> int:
    """Get current Unix timestamp (seconds since epoch).

    Returns:
        Current timestamp
    """
    return int(time.time())


def timestamp_to_date(ts: int) -> str:
    """Convert Unix timestamp to date string.

    Args:
        ts: Unix timestamp

    Returns:
        Formatted date string
    """
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def random_string(length: int = 10) -> str:
    """Generate random alphanumeric string.

    Args:
        length: String length (default: 10)

    Returns:
        Random string
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_number(min_val: int = 0, max_val: int = 100) -> int:
    """Generate random integer in range.

    Args:
        min_val: Minimum value (inclusive, default: 0)
        max_val: Maximum value (inclusive, default: 100)

    Returns:
        Random integer
    """
    return random.randint(min_val, max_val)


# Built-in functions registry
BUILTIN_FUNCTIONS = {
    # StringUtils
    "to_uppercase": to_uppercase,
    "to_lowercase": to_lowercase,
    # TimeUtils
    "current_time": current_time,
    "current_timestamp": current_timestamp,
    "timestamp_to_date": timestamp_to_date,
    # RandomUtils
    "random_string": random_string,
    "random_number": random_number,
}

# Built-in function metadata for initialization
BUILTIN_PARAMS_DATA = [
    # StringUtils
    {
        "class_name": "StringUtils",
        "method_name": "to_uppercase",
        "description": "转换字符串为大写",
        "code": '''def to_uppercase(s: str) -> str:
    """Convert string to uppercase.

    Args:
        s: Input string

    Returns:
        Uppercase string
    """
    return s.upper()
''',
        "params_in": [
            {"name": "s", "type": "str", "description": "输入字符串"}
        ],
        "params_out": [
            {"type": "str", "description": "大写字符串"}
        ],
        "is_builtin": True,
    },
    {
        "class_name": "StringUtils",
        "method_name": "to_lowercase",
        "description": "转换字符串为小写",
        "code": '''def to_lowercase(s: str) -> str:
    """Convert string to lowercase.

    Args:
        s: Input string

    Returns:
        Lowercase string
    """
    return s.lower()
''',
        "params_in": [
            {"name": "s", "type": "str", "description": "输入字符串"}
        ],
        "params_out": [
            {"type": "str", "description": "小写字符串"}
        ],
        "is_builtin": True,
    },
    # TimeUtils
    {
        "class_name": "TimeUtils",
        "method_name": "current_time",
        "description": "获取当前时间 (YYYY-MM-DD HH:mm:ss)",
        "code": '''def current_time() -> str:
    """Get current time in YYYY-MM-DD HH:mm:ss format.

    Returns:
        Current time formatted string
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
''',
        "params_in": [],
        "params_out": [
            {"type": "str", "description": "当前时间字符串"}
        ],
        "is_builtin": True,
    },
    {
        "class_name": "TimeUtils",
        "method_name": "current_timestamp",
        "description": "获取当前时间戳(秒)",
        "code": '''def current_timestamp() -> int:
    """Get current Unix timestamp (seconds since epoch).

    Returns:
        Current timestamp
    """
    import time
    return int(time.time())
''',
        "params_in": [],
        "params_out": [
            {"type": "int", "description": "当前时间戳"}
        ],
        "is_builtin": True,
    },
    {
        "class_name": "TimeUtils",
        "method_name": "timestamp_to_date",
        "description": "时间戳转日期字符串",
        "code": '''def timestamp_to_date(ts: int) -> str:
    """Convert Unix timestamp to date string.

    Args:
        ts: Unix timestamp

    Returns:
        Formatted date string
    """
    from datetime import datetime
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
''',
        "params_in": [
            {"name": "ts", "type": "int", "description": "Unix时间戳"}
        ],
        "params_out": [
            {"type": "str", "description": "日期字符串"}
        ],
        "is_builtin": True,
    },
    # RandomUtils
    {
        "class_name": "RandomUtils",
        "method_name": "random_string",
        "description": "生成随机字符串",
        "code": '''def random_string(length: int = 10) -> str:
    """Generate random alphanumeric string.

    Args:
        length: String length (default: 10)

    Returns:
        Random string
    """
    import random
    import string
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
''',
        "params_in": [
            {"name": "length", "type": "int", "description": "字符串长度(默认10)"}
        ],
        "params_out": [
            {"type": "str", "description": "随机字符串"}
        ],
        "is_builtin": True,
    },
    {
        "class_name": "RandomUtils",
        "method_name": "random_number",
        "description": "生成随机数字",
        "code": '''def random_number(min_val: int = 0, max_val: int = 100) -> int:
    """Generate random integer in range.

    Args:
        min_val: Minimum value (inclusive, default: 0)
        max_val: Maximum value (inclusive, default: 100)

    Returns:
        Random integer
    """
    import random
    return random.randint(min_val, max_val)
''',
        "params_in": [
            {"name": "min_val", "type": "int", "description": "最小值(包含,默认0)"},
            {"name": "max_val", "type": "int", "description": "最大值(包含,默认100)"}
        ],
        "params_out": [
            {"type": "int", "description": "随机整数"}
        ],
        "is_builtin": True,
    },
]
