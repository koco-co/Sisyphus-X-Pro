import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import type { ReactNode } from 'react'
import { authService } from '@/lib/auth'
import { apiClient } from '@/lib/api'

interface User {
  id: string
  email: string
  nickname?: string
  avatar?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  refreshToken: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, nickname: string) => Promise<void>
  logout: () => void
  refreshAccessToken: () => Promise<void>
  isAuthenticated: boolean
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // 初始化时从 localStorage 恢复登录状态
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedRefreshToken = localStorage.getItem('refreshToken')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      setToken(storedToken)
      setRefreshToken(storedRefreshToken)
      setUser(JSON.parse(storedUser))
      apiClient.setToken(storedToken)
    }

    setLoading(false)
  }, [])

  // 登录
  const login = useCallback(async (email: string, password: string) => {
    const data = await authService.login(email, password)
    const { access_token: newToken, refresh_token: newRefreshToken, user: newUser } = data

    setToken(newToken)
    setRefreshToken(newRefreshToken || null)
    setUser(newUser)
    apiClient.setToken(newToken)

    localStorage.setItem('token', newToken)
    if (newRefreshToken) {
      localStorage.setItem('refreshToken', newRefreshToken)
    }
    localStorage.setItem('user', JSON.stringify(newUser))
  }, [])

  // 注册
  const register = useCallback(async (email: string, password: string, nickname: string) => {
    const data = await authService.register(email, password, nickname)
    const { access_token: newToken, refresh_token: newRefreshToken, user: newUser } = data

    setToken(newToken)
    setRefreshToken(newRefreshToken || null)
    setUser(newUser)
    apiClient.setToken(newToken)

    localStorage.setItem('token', newToken)
    if (newRefreshToken) {
      localStorage.setItem('refreshToken', newRefreshToken)
    }
    localStorage.setItem('user', JSON.stringify(newUser))
  }, [])

  // 刷新 token
  const refreshAccessToken = useCallback(async () => {
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const data = await authService.refreshToken(refreshToken)
    const { access_token: newToken, refresh_token: newRefreshToken, user: newUser } = data

    setToken(newToken)
    setRefreshToken(newRefreshToken || refreshToken)
    setUser(newUser)
    apiClient.setToken(newToken)

    localStorage.setItem('token', newToken)
    if (newRefreshToken) {
      localStorage.setItem('refreshToken', newRefreshToken)
    }
    localStorage.setItem('user', JSON.stringify(newUser))
  }, [refreshToken])

  // 退出登录
  const logout = useCallback(() => {
    setUser(null)
    setToken(null)
    setRefreshToken(null)
    apiClient.setToken(null)
    authService.logout()
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        refreshToken,
        login,
        register,
        logout,
        refreshAccessToken,
        isAuthenticated: !!user,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
