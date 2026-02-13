import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import LoginPage from '@/pages/auth/LoginPage'
import ProjectsPage from '@/pages/projects/ProjectsPage'
import DatabaseConfigPage from '@/pages/projects/DatabaseConfigPage'
import KeywordsPage from '@/pages/projects/KeywordsPage'
import { InterfacesPage } from '@/pages/projects/InterfacesPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
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
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <ProjectsPage />
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
