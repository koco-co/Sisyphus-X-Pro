import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import LoginPage from '@/pages/auth/LoginPage'
import OAuthCallback from '@/pages/auth/OAuthCallback'
import Dashboard from '@/pages/Dashboard'
import ProjectsPage from '@/pages/projects/ProjectsPage'
import DatabaseConfigPage from '@/pages/projects/DatabaseConfigPage'
import KeywordsPage from '@/pages/projects/KeywordsPage'
import { InterfacesPage } from '@/pages/projects/InterfacesPage'
import Header from '@/components/layout/Header'
import ScenariosPage from '@/pages/scenarios/ScenariosPage'
import TestPlansPage from '@/pages/test-plans/TestPlansPage'
import GlobalFunctions from '@/pages/GlobalFunctions'
import { apiClient } from '@/lib/api'
import { useEffect, useCallback } from 'react'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading, refreshAccessToken } = useAuth()

  // 设置 Token 刷新回调 - 使用 useCallback 避免重复创建
  const setupTokenRefresh = useCallback(async () => {
    try {
      await refreshAccessToken()
    } catch (error) {
      // Token 刷新失败,跳转登录页
      console.error('Token refresh failed:', error)
      window.location.href = '/login'
    }
  }, [refreshAccessToken])

  useEffect(() => {
    apiClient.setTokenRefreshCallback(setupTokenRefresh)
  }, [setupTokenRefresh])

  // 等待初始化完成
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">加载中...</div>
  }

  return isAuthenticated ? (
    <div className="min-h-screen bg-background">
      <Header />
      {children}
    </div>
  ) : <Navigate to="/login" replace />
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth()

  // 等待初始化完成
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">加载中...</div>
  }

  // 已登录用户访问公开路由时重定向到首页
  return isAuthenticated ? <Navigate to="/" replace /> : <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      {/* 公开路由 - 登录页 */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />

      {/* 公开路由 - OAuth 回调 (不需要包装在 PublicRoute 中,因为需要处理回调) */}
      <Route path="/auth/github/callback" element={<OAuthCallback />} />
      <Route path="/auth/google/callback" element={<OAuthCallback />} />

      {/* 受保护路由 - 首页 */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* 受保护路由 - 仪表盘 (重定向到首页) */}
      <Route
        path="/dashboard"
        element={<Navigate to="/" replace />}
      />

      {/* 受保护路由 - 项目管理 */}
      <Route
        path="/projects"
        element={
          <ProtectedRoute>
            <ProjectsPage />
          </ProtectedRoute>
        }
      />

      {/* 受保护路由 - 项目配置 */}
      <Route
        path="/projects/:projectId/database-config"
        element={
          <ProtectedRoute>
            <DatabaseConfigPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/:projectId/keywords"
        element={
          <ProtectedRoute>
            <KeywordsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/:projectId/interfaces"
        element={
          <ProtectedRoute>
            <InterfacesPage />
          </ProtectedRoute>
        }
      />

      {/* 受保护路由 - 场景编排 */}
      <Route
        path="/scenarios"
        element={
          <ProtectedRoute>
            <ScenariosPage />
          </ProtectedRoute>
        }
      />

      {/* 受保护路由 - 测试计划 */}
      <Route
        path="/test-plans"
        element={
          <ProtectedRoute>
            <TestPlansPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/test-plans/new"
        element={
          <ProtectedRoute>
            <TestPlansPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/test-plans/:id/edit"
        element={
          <ProtectedRoute>
            <TestPlansPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/test-plans/:id/executions"
        element={
          <ProtectedRoute>
            <TestPlansPage />
          </ProtectedRoute>
        }
      />

      {/* 受保护路由 - 全局函数 */}
      <Route
        path="/global-functions"
        element={
          <ProtectedRoute>
            <GlobalFunctions />
          </ProtectedRoute>
        }
      />

      {/* 404 - 所有未匹配的路由重定向到首页或登录页 */}
      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
