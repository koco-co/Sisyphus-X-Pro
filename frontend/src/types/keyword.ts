// 关键字类型定义

export interface Keyword {
  id: number
  type: KeywordType
  name: string
  method_name: string
  code: string
  params: ParamDescription[]
  is_enabled: boolean
  is_builtin: boolean
  created_at: string
}

export type KeywordType =
  | 'http_request'
  | 'assertion'
  | 'extract'
  | 'database'
  | 'custom'

export interface ParamDescription {
  name: string
  description: string
  type?: string
  default?: string | null
}

// 内置关键字列表 (系统预置)
export const BUILTIN_KEYWORDS: Keyword[] = [
  {
    id: 0, // Placeholder ID
    type: 'http_request',
    name: 'HTTP 请求',
    method_name: 'http_request',
    type: 'http_request',
    name: 'HTTP 请求',
    method_name: 'http_request',
    code: `def http_request(
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
        headers: 请求头
        params: URL 参数
        json: JSON 请求体
        data: 表单数据
        **kwargs: 其他 requests 库参数

    Returns:
        响应对象 (包含 status_code, headers, text, json 等属性)
    """
    import requests

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json,
        data=data,
        **kwargs
    )

    return {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "text": response.text,
        "json": response.json() if response.headers.get("content-type", "").startswith("application/json") else None,
        "response": response
    }`,
    params: [
      { name: 'url', description: '请求 URL' },
      { name: 'method', description: '请求方法' },
      { name: 'headers', description: '请求头' },
      { name: 'json', description: 'JSON 请求体' },
    ],
    is_enabled: true,
    is_builtin: true,
    created_at: new Date().toISOString(),
  },
  {
    id: 1, // Placeholder ID
    type: 'assertion',
    name: '断言响应',
    method_name: 'assert_response',
    code: `def assert_response(response, expected_status=200, expected_json_contains=None, json_path_exists=None):
    """断言HTTP响应"""
    errors = []
    if response.get('status_code') != expected_status:
        errors.append(f"状态码不匹配: 期望 {expected_status}, 实际 {response.get('status_code')}")
    if errors:
        raise AssertionError('; '.join(errors))
    return True`,
    params: [
      { name: 'response', description: 'HTTP 响应对象' },
      { name: 'expected_status', description: '期望的 HTTP 状态码' },
      { name: 'expected_json_contains', description: '期望 JSON 包含的键值对' },
    ],
    is_enabled: true,
    is_builtin: true,
    created_at: new Date().toISOString(),
  },
  {
    id: 2, // Placeholder ID
    type: 'extract',
    name: '提取变量',
    method_name: 'extract_variable',
    code: `def extract_variable(response, json_path=None, header_name=None, regex_pattern=None):
    """从HTTP响应中提取变量"""
    if json_path:
        keys = json_path.split('.')
        current = response.get('json') or {}
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                raise ValueError(f"JSON路径不存在: {json_path}")
            current = current[key]
        return current
    return None`,
    params: [
      { name: 'response', description: 'HTTP 响应对象' },
      { name: 'json_path', description: 'JSON 路径 (如: data.user.id)' },
      { name: 'header_name', description: '响应头名称' },
    ],
    is_enabled: true,
    is_builtin: true,
    created_at: new Date().toISOString(),
  },
  {
    id: 3, // Placeholder ID
    type: 'database',
    name: '数据库查询',
    method_name: 'db_query',
    code: `def db_query(db_connection, sql, params=None, fetch_one=False):
    """执行数据库查询"""
    cursor = db_connection.cursor()
    cursor.execute(sql, params or ())
    return cursor.fetchone() if fetch_one else cursor.fetchall()`,
    params: [
      { name: 'db_connection', description: '数据库连接对象' },
      { name: 'sql', description: 'SQL 查询语句' },
      { name: 'params', description: 'SQL 参数' },
    ],
    is_enabled: true,
    is_builtin: true,
    created_at: new Date().toISOString(),
  },
  {
    id: 4, // Placeholder ID
    type: 'database',
    name: '数据库更新',
    method_name: 'db_update',
    code: `def db_update(db_connection, sql, params=None, commit=True):
    """执行数据库更新 (INSERT/UPDATE/DELETE)"""
    cursor = db_connection.cursor()
    cursor.execute(sql, params or ())
    affected = cursor.rowcount
    if commit:
        db_connection.commit()
    return affected`,
    params: [
      { name: 'db_connection', description: '数据库连接对象' },
      { name: 'sql', description: 'SQL 语句' },
      { name: 'params', description: 'SQL 参数' },
    ],
    is_enabled: true,
    is_builtin: true,
    created_at: new Date().toISOString(),
  },
]
