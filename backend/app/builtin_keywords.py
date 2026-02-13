"""Built-in keywords data definition."""

BUILTIN_KEYWORDS = [
    {
        "type": "http_request",
        "name": "HTTP 请求",
        "method_name": "http_request",
        "code": '''def http_request(
    url: str,
    method: str = "GET",
    headers: dict = None,
    params: dict = None,
    json: dict = None,
    data: dict = None,
    **kwargs
) -> dict:
    """
    发送 HTTP 请求

    Args:
        url: 请求 URL
        method: 请求方法 (GET/POST/PUT/DELETE/PATCH 等)
        headers: 请求头字典
        params: URL 查询参数
        json: JSON 请求体
        data: 表单数据
        **kwargs: 其他 requests 库参数 (timeout, verify 等)

    Returns:
        包含响应信息的字典:
        - status_code: HTTP 状态码
        - headers: 响应头
        - text: 响应文本
        - json: JSON 数据 (如果 Content-Type 是 application/json)
        - response: 原始响应对象
    """
    import requests

    if headers is None:
        headers = {}
    if params is None:
        params = {}

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json,
        data=data,
        **kwargs
    )

    result = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "text": response.text,
        "response": response
    }

    # 尝试解析 JSON
    try:
        if response.headers.get("content-type", "").startswith("application/json"):
            result["json"] = response.json()
    except Exception:
        result["json"] = None

    return result
''',
        "params": [
            {"name": "url", "description": "请求 URL"},
            {"name": "method", "description": "请求方法 (默认: GET)"},
            {"name": "headers", "description": "请求头字典"},
            {"name": "params", "description": "URL 查询参数"},
            {"name": "json", "description": "JSON 请求体"},
        ],
    },
    {
        "type": "assertion",
        "name": "断言响应",
        "method_name": "assert_response",
        "code": '''def assert_response(
    response: dict,
    expected_status: int = 200,
    expected_json_contains: dict = None,
    expected_text_contains: str = None,
    json_path_exists: str = None,
) -> bool:
    """
    断言 HTTP 响应是否符合预期

    Args:
        response: HTTP 响应对象 (http_request 返回值)
        expected_status: 期望的 HTTP 状态码
        expected_json_contains: 期望 JSON 响应包含的键值对
        expected_text_contains: 期望响应文本包含的字符串
        json_path_exists: 期望存在的 JSON 路径 (如: data.user.id)

    Returns:
        True 如果所有断言通过

    Raises:
        AssertionError: 如果任何断言失败
    """
    errors = []

    # 断言状态码
    if response.get("status_code") != expected_status:
        errors.append(
            f"状态码不匹配: 期望 {expected_status}, 实际 {response.get('status_code')}"
        )

    # 断言 JSON 包含
    if expected_json_contains:
        response_json = response.get("json") or {}
        for key, value in expected_json_contains.items():
            if key not in response_json:
                errors.append(f"JSON 缺少字段: {key}")
            elif response_json[key] != value:
                errors.append(
                    f"JSON 字段 {key} 不匹配: 期望 {value}, "
                    f"实际 {response_json.get(key)}"
                )

    # 断言文本包含
    if expected_text_contains:
        if expected_text_contains not in response.get("text", ""):
            errors.append(f"响应文本不包含: {expected_text_contains}")

    # 断言 JSON 路径存在
    if json_path_exists:
        keys = json_path_exists.split(".")
        current = response.get("json") or {}
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                errors.append(f"JSON 路径不存在: {json_path_exists}")
                break
            current = current[key]

    if errors:
        raise AssertionError("; ".join(errors))

    return True
''',
        "params": [
            {"name": "response", "description": "HTTP 响应对象"},
            {"name": "expected_status", "description": "期望的 HTTP 状态码"},
            {"name": "expected_json_contains", "description": "期望 JSON 包含的键值对"},
            {"name": "json_path_exists", "description": "期望存在的 JSON 路径"},
        ],
    },
    {
        "type": "extract",
        "name": "提取变量",
        "method_name": "extract_variable",
        "code": '''def extract_variable(
    response: dict,
    json_path: str = None,
    header_name: str = None,
    regex_pattern: str = None,
) -> any:
    """
    从 HTTP 响应中提取变量

    Args:
        response: HTTP 响应对象
        json_path: JSON 路径 (如: data.user.id)
        header_name: 响应头名称
        regex_pattern: 正则表达式 (从响应文本中提取)

    Returns:
        提取的值

    Raises:
        ValueError: 如果无法提取值或参数冲突
    """
    provided = sum([
        json_path is not None,
        header_name is not None,
        regex_pattern is not None,
    ])

    if provided == 0:
        raise ValueError("必须提供 json_path, header_name, 或 regex_path 之一")
    if provided > 1:
        raise ValueError("只能提供一个提取方式")

    # 从 JSON 提取
    if json_path:
        keys = json_path.split(".")
        current = response.get("json") or {}
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                raise ValueError(f"JSON 路径不存在: {json_path}")
            current = current[key]
        return current

    # 从响应头提取
    if header_name:
        headers = response.get("headers") or {}
        if header_name not in headers:
            raise ValueError(f"响应头不存在: {header_name}")
        return headers[header_name]

    # 使用正则提取
    if regex_pattern:
        import re
        text = response.get("text") or ""
        match = re.search(regex_pattern, text)
        if not match:
            raise ValueError(f"正则表达式未匹配: {regex_pattern}")
        return match.group(1) if match.groups() else match.group(0)

    return None
''',
        "params": [
            {"name": "response", "description": "HTTP 响应对象"},
            {"name": "json_path", "description": "JSON 路径 (如: data.user.id)"},
            {"name": "header_name", "description": "响应头名称"},
            {"name": "regex_pattern", "description": "正则表达式"},
        ],
    },
    {
        "type": "database",
        "name": "数据库查询",
        "method_name": "db_query",
        "code": '''def db_query(
    db_connection,
    sql: str,
    params: tuple = None,
    fetch_one: bool = False,
) -> list[dict] | dict | None:
    """
    执行数据库查询

    Args:
        db_connection: 数据库连接对象
        sql: SQL 查询语句
        params: SQL 参数 (用于参数化查询)
        fetch_one: 是否只获取一条记录

    Returns:
        如果 fetch_one=True: 单条记录 (dict) 或 None
        如果 fetch_one=False: 记录列表 (list[dict])

    Raises:
        Exception: 数据库执行错误
    """
    cursor = None
    try:
        cursor = db_connection.cursor(dictionary=True)

        cursor.execute(sql, params or ())

        if fetch_one:
            return cursor.fetchone()
        else:
            return cursor.fetchall()

    except Exception as e:
        raise Exception(f"数据库查询失败: {str(e)}") from e
    finally:
        if cursor:
            cursor.close()
''',
        "params": [
            {"name": "db_connection", "description": "数据库连接对象"},
            {"name": "sql", "description": "SQL 查询语句"},
            {"name": "params", "description": "SQL 参数"},
            {"name": "fetch_one", "description": "是否只获取一条记录"},
        ],
    },
    {
        "type": "database",
        "name": "数据库更新",
        "method_name": "db_update",
        "code": '''def db_update(
    db_connection,
    sql: str,
    params: tuple = None,
    commit: bool = True,
) -> int:
    """
    执行数据库更新 (INSERT/UPDATE/DELETE)

    Args:
        db_connection: 数据库连接对象
        sql: SQL 语句
        params: SQL 参数
        commit: 是否自动提交

    Returns:
        影响的行数

    Raises:
        Exception: 数据库执行错误
    """
    cursor = None
    try:
        cursor = db_connection.cursor()

        cursor.execute(sql, params or ())
        affected_rows = cursor.rowcount

        if commit:
            db_connection.commit()

        return affected_rows

    except Exception as e:
        if commit:
            db_connection.rollback()
        raise Exception(f"数据库更新失败: {str(e)}") from e
    finally:
        if cursor:
            cursor.close()
''',
        "params": [
            {"name": "db_connection", "description": "数据库连接对象"},
            {"name": "sql", "description": "SQL 语句"},
            {"name": "params", "description": "SQL 参数"},
            {"name": "commit", "description": "是否自动提交"},
        ],
    },
]
