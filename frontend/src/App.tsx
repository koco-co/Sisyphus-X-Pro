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
import { apiClient } from '@/lib/api'
import { useEffect } from 'react'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, refreshAccessToken } = useAuth()

  // 设置 Token 刷新回调
  useEffect(() => {
    apiClient.setTokenRefreshCallback(async () => {
      try {
        await refreshAccessToken()
      } catch (error) {
        // Token 刷新失败,跳转登录页
        console.error('Token refresh failed:', error)
        window.location.href = '/login'
      }
    })
  }, [refreshAccessToken])

  return isAuthenticated ? (
    <div className="min-h-screen bg-background">
      <Header />
      {children}
    </div>
  ) : <Navigate to="/login" replace />
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <Navigate to="/" replace /> : <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      {/* OAuth 回调路由 (公开) */}
      <Route path="/auth/github/callback" element={<OAuthCallback />} />
      <Route path="/auth/google/callback" element={<OAuthCallback />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects"
        element={
          <ProtectedRoute>
            <ProjectsPage />
          </ProtectedRoute>
        }
      />
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
