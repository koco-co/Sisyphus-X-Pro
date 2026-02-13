import type { AuthResponse } from './api'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export interface User {
  id: string
  email: string
  nickname?: string
  avatar?: string
}

/**
 * 认证服务类
 * 处理登录、注册、OAuth 等认证相关操作
 */
export class AuthService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * 邮箱密码登录
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/login/json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: '登录失败' }))
      throw new Error(error.detail || '登录失败')
    }

    return response.json()
  }

  /**
   * 用户注册
   */
  async register(email: string, password: string, nickname: string): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, nickname }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: '注册失败' }))
      throw new Error(error.detail || '注册失败')
    }

    return response.json()
  }

  /**
   * 刷新 access token
   */
  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshToken}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: '刷新 Token 失败' }))
      throw new Error(error.detail || '刷新 Token 失败')
    }

    return response.json()
  }

  /**
   * GitHub OAuth 登录
   * 获取 GitHub 授权 URL
   */
  async getGitHubAuthUrl(): Promise<string> {
    const response = await fetch(`${this.baseUrl}/auth/github`)
    if (!response.ok) {
      throw new Error('获取 GitHub 授权链接失败')
    }

    const data = await response.json()
    return data.authorization_url
  }

  /**
   * Google OAuth 登录
   * 获取 Google 授权 URL
   */
  async getGoogleAuthUrl(): Promise<string> {
    const response = await fetch(`${this.baseUrl}/auth/google`)
    if (!response.ok) {
      throw new Error('获取 Google 授权链接失败')
    }

    const data = await response.json()
    return data.authorization_url
  }

  /**
   * 处理 OAuth 回调
   * 适用于 GitHub 和 Google
   */
  async handleOAuthCallback(provider: 'github' | 'google', code: string, state: string): Promise<AuthResponse> {
    const response = await fetch(
      `${this.baseUrl}/auth/${provider}/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`
    )

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'OAuth 登录失败' }))
      throw new Error(error.detail || 'OAuth 登录失败')
    }

    return response.json()
  }

  /**
   * 退出登录
   * 客户端清除 token 即可
   */
  logout(): void {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  }
}

// 创建全局认证服务实例
export const authService = new AuthService()
