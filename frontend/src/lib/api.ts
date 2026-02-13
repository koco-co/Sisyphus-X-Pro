// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// API 响应类型
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
}

// 认证相关类型
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  nickname: string
}

export interface AuthResponse {
  access_token: string
  refresh_token?: string
  user: {
    id: string
    email: string
    nickname?: string
    avatar?: string
  }
}

// Token 刷新回调类型
type TokenRefreshCallback = () => Promise<void>

// API 客户端
export class ApiClient {
  baseUrl: string
  token: string | null = null
  tokenRefreshCallback: TokenRefreshCallback | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token')
    }
  }

  setToken(token: string | null) {
    this.token = token
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    }
  }

  setTokenRefreshCallback(callback: TokenRefreshCallback) {
    this.tokenRefreshCallback = callback
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    let response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    })

    // 处理 401 未授权响应
    if (response.status === 401 && this.tokenRefreshCallback) {
      try {
        // 尝试刷新 token
        await this.tokenRefreshCallback()

        // 重新设置 token
        if (this.token) {
          headers['Authorization'] = `Bearer ${this.token}`

          // 重试原请求
          response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers,
          })
        }
      } catch (error) {
        // Token 刷新失败,抛出原始错误
        console.error('Token refresh failed:', error)
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: '请求失败' }))
      throw new Error(error.message || error.detail || '请求失败')
    }

    return response.json()
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  async patch<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }
}

// Dashboard 相关 API 方法
export interface CoreStats {
  total_projects: number
  total_interfaces: number
  total_scenarios: number
  total_plans: number
}

export interface TrendDataPoint {
  date: string
  count: number
}

export interface TrendData {
  trend: TrendDataPoint[]
}

export interface CoverageData {
  tested_projects: number
  untested_projects: number
  coverage_percentage: number
}

export class DashboardAPI {
  client: ApiClient

  constructor(client: ApiClient) {
    this.client = client
  }

  async getCoreStats(): Promise<CoreStats> {
    return this.client.get<CoreStats>('/dashboard/stats')
  }

  async getExecutionTrend(days: number = 30): Promise<TrendData> {
    return this.client.get<TrendData>(`/dashboard/trend?days=${days}`)
  }

  async getProjectCoverage(): Promise<CoverageData> {
    return this.client.get<CoverageData>('/dashboard/coverage')
  }
}

// 全局参数相关 API 方法
export interface ParamIn {
  name: string
  type: string
  description: string
}

export interface ParamOut {
  type: string
  description: string
}

export interface GlobalParam {
  id: number
  class_name: string
  method_name: string
  description: string
  code: string
  params_in: ParamIn[]
  params_out: ParamOut[]
  is_builtin: boolean
  created_at: string
}

export interface GlobalParamListResponse {
  items: GlobalParam[]
  total: number
  page: number
  pageSize: number
}

export interface GlobalParamGroupedResponse {
  params: Record<string, GlobalParam[]>
}

export interface FunctionParseRequest {
  text: string
  context: Record<string, string>
}

export interface FunctionParseResponse {
  original_text: string
  parsed_text: string
  functions_called: string[]
  success: boolean
  error?: string
}

export interface CreateGlobalParamRequest {
  class_name: string
  method_name: string
  description: string
  code: string
  params_in: ParamIn[]
  params_out: ParamOut[]
}

export interface UpdateGlobalParamRequest {
  class_name?: string
  method_name?: string
  description?: string
  code?: string
  params_in?: ParamIn[]
  params_out?: ParamOut[]
}

export class GlobalParamAPI {
  client: ApiClient

  constructor(client: ApiClient) {
    this.client = client
  }

  async getGlobalParams(
    page: number = 1,
    pageSize: number = 10,
    class_name?: string,
    is_builtin?: boolean
  ): Promise<GlobalParamListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      pageSize: pageSize.toString(),
    })

    if (class_name) params.append('class_name', class_name)
    if (is_builtin !== undefined) params.append('is_builtin', is_builtin.toString())

    return this.client.get<GlobalParamListResponse>(`/global-params?${params}`)
  }

  async getGlobalParamsGrouped(): Promise<GlobalParamGroupedResponse> {
    return this.client.get<GlobalParamGroupedResponse>('/global-params/grouped')
  }

  async getGlobalParam(id: number): Promise<GlobalParam> {
    return this.client.get<GlobalParam>(`/global-params/${id}`)
  }

  async createGlobalParam(data: CreateGlobalParamRequest): Promise<GlobalParam> {
    return this.client.post<GlobalParam>('/global-params', data)
  }

  async updateGlobalParam(
    id: number,
    data: UpdateGlobalParamRequest
  ): Promise<GlobalParam> {
    return this.client.put<GlobalParam>(`/global-params/${id}`, data)
  }

  async deleteGlobalParam(id: number): Promise<void> {
    return this.client.delete<void>(`/global-params/${id}`)
  }

  async parseFunctionCalls(
    request: FunctionParseRequest
  ): Promise<FunctionParseResponse> {
    return this.client.post<FunctionParseResponse>('/global-params/parse', request)
  }
}

// Report 相关类型和 API
export interface TestReport {
  id: number
  execution_id: string
  plan_id: number
  status: string
  total_scenarios: number
  passed: number
  failed: number
  skipped: number
  duration_seconds: number | null
  executor_id: number
  environment_name: string
  started_at: string
  finished_at: string | null
  allure_path: string | null
  created_at: string
  updated_at: string | null
}

export interface ReportListResponse {
  reports: TestReport[]
  total: number
  page: number
  limit: number
}

export interface ReportStatistics {
  total_reports: number
  total_scenarios: number
  total_passed: number
  total_failed: number
  total_skipped: number
  pass_rate: number
  average_duration: number | null
}

export interface ReportExportRequest {
  format: 'pdf' | 'excel' | 'html'
  include_details: boolean
}

export interface AllureReportResponse {
  url: string
  expires_at: string | null
}

export class ReportAPI {
  client: ApiClient

  constructor(client: ApiClient) {
    this.client = client
  }

  async getReports(params: {
    page?: number
    limit?: number
    plan_id?: number
    status?: string
  } = {}): Promise<ReportListResponse> {
    const queryParams = new URLSearchParams()
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.limit) queryParams.append('limit', params.limit.toString())
    if (params.plan_id) queryParams.append('plan_id', params.plan_id.toString())
    if (params.status) queryParams.append('status', params.status)

    const queryString = queryParams.toString()
    return this.client.get<ReportListResponse>(`/reports${queryString ? `?${queryString}` : ''}`)
  }

  async getReport(reportId: number): Promise<TestReport> {
    return this.client.get<TestReport>(`/reports/${reportId}`)
  }

  async getStatistics(): Promise<ReportStatistics> {
    return this.client.get<ReportStatistics>('/reports/statistics')
  }

  async getAllureReport(reportId: number): Promise<AllureReportResponse> {
    return this.client.get<AllureReportResponse>(`/reports/${reportId}/allure`)
  }

  async deleteReport(reportId: number): Promise<void> {
    return this.client.delete<void>(`/reports/${reportId}`)
  }

  async exportReport(reportId: number, request: ReportExportRequest): Promise<Blob> {
    const response = await fetch(`${this.client.baseUrl}/reports/${reportId}/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.client.token && { Authorization: `Bearer ${this.client.token}` }),
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error('导出报告失败')
    }

    return response.blob()
  }
}

// 创建全局 API 客户端实例
export const apiClient = new ApiClient()

// 创建 Dashboard API 实例
export const dashboardAPI = new DashboardAPI(apiClient)

// 创建 GlobalParam API 实例
export const globalParamAPI = new GlobalParamAPI(apiClient)

// 创建 Report API 实例
export const reportAPI = new ReportAPI(apiClient)
