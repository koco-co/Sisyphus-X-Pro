// 关键字类型定义

export interface Keyword {
  id: string
  project_id: string
  type: KeywordType
  name: string
  method_name: string
  code: string
  params?: ParamDescription[]
  enabled: boolean
  is_builtin: boolean
  created_at: string
  updated_at: string
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
}

// 内置关键字列表 (系统预置)
export const BUILTIN_KEYWORDS: Omit<Keyword, 'project_id' | 'created_at' | 'updated_at'>[] = [
  {
    id: 'builtin-http-request',
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
    enabled: true,
    is_builtin: true,
  },
]
