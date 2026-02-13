# 前端组件使用指南

本文档介绍 Sisyphus-X-Pro 前端项目中可用的通用组件和使用方法。

## 目录

- [Context Providers](#context-providers)
- [布局组件](#布局组件)
- [通用 UI 组件](#通用-ui-组件)
- [API 客户端](#api-客户端)

---

## Context Providers

### ThemeProvider - 主题管理

管理应用的主题（深色/浅色模式）。

**使用方法**：

```tsx
import { ThemeProvider } from '@/contexts/ThemeContext'
import { useTheme } from '@/contexts/ThemeContext'

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="sisyphus-ui-theme">
      {/* Your app */}
    </ThemeProvider>
  )
}

function MyComponent() {
  const { theme, setTheme } = useTheme()

  return (
    <button onClick={() => setTheme('dark')}>
      切换到深色模式
    </button>
  )
}
```

**API**：
- `theme: 'light' | 'dark' | 'system'` - 当前主题
- `setTheme(theme)` - 设置主题

---

### AuthProvider - 认证管理

管理用户认证状态和登录/登出。

**使用方法**：

```tsx
import { AuthProvider } from '@/contexts/AuthContext'
import { useAuth } from '@/contexts/AuthContext'

function App() {
  return (
    <AuthProvider>
      {/* Your app */}
    </AuthProvider>
  )
}

function LoginPage() {
  const { login } = useAuth()

  const handleLogin = async () => {
    try {
      await login('user@example.com', 'password')
      // 登录成功，跳转到首页
    } catch (error) {
      // 处理错误
    }
  }

  return <button onClick={handleLogin}>登录</button>
}

function ProtectedPage() {
  const { user, isAuthenticated, logout } = useAuth()

  if (!isAuthenticated) {
    return <div>请先登录</div>
  }

  return (
    <div>
      <p>欢迎，{user?.email}</p>
      <button onClick={logout}>登出</button>
    </div>
  )
}
```

**API**：
- `user: User | null` - 当前用户信息
- `token: string | null` - JWT Token
- `isAuthenticated: boolean` - 是否已登录
- `login(email, password)` - 登录
- `logout()` - 登出

---

### ToastProvider - 消息通知

显示右上角消息通知，带进度条倒计时。

**使用方法**：

```tsx
import { ToastProvider } from '@/components/ui/toast'
import { useToast } from '@/components/ui/toast'

function App() {
  return (
    <ToastProvider>
      {/* Your app */}
    </ToastProvider>
  )
}

function MyComponent() {
  const { showSuccess, showError, showWarning, showInfo } = useToast()

  return (
    <>
      <button onClick={() => showSuccess('操作成功！')}>
        成功提示
      </button>
      <button onClick={() => showError('操作失败！')}>
        错误提示
      </button>
      <button onClick={() => showWarning('请注意！')}>
        警告提示
      </button>
      <button onClick={() => showInfo('提示信息')}>
        信息提示
      </button>
    </>
  )
}
```

**API**：
- `showSuccess(message)` - 显示成功消息
- `showError(message)` - 显示错误消息
- `showWarning(message)` - 显示警告消息
- `showInfo(message)` - 显示信息消息
- `showToast(message, type, duration)` - 自定义消息

---

### ConfirmProvider - 二次确认弹窗

显示二次确认对话框。

**使用方法**：

```tsx
import { ConfirmProvider } from '@/components/ui/confirm-dialog'
import { useConfirm } from '@/components/ui/confirm-dialog'

function App() {
  return (
    <ConfirmProvider>
      {/* Your app */}
    </ConfirmProvider>
  )
}

function DeleteButton() {
  const { confirm } = useConfirm()

  const handleDelete = async () => {
    const confirmed = await confirm({
      type: 'danger',
      title: '确认删除',
      description: '此操作无法撤销，确定要删除吗？',
      confirmText: '删除',
      cancelText: '取消',
    })

    if (confirmed) {
      // 执行删除操作
    }
  }

  return <button onClick={handleDelete}>删除</button>
}
```

**API**：
- `confirm(options)` - 显示确认对话框
  - `type?: 'danger' | 'warning' | 'info'` - 对话框类型
  - `title?: string` - 标题
  - `description?: string` - 描述
  - `confirmText?: string` - 确认按钮文本
  - `cancelText?: string` - 取消按钮文本

---

## 布局组件

### Sidebar - 侧边栏导航

可折叠的侧边栏，支持导航高亮。

**使用方法**：

```tsx
import { Sidebar } from '@/components/layout/Sidebar'

function MainLayout() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      {/* Main content */}
    </div>
  )
}
```

**特性**：
- ✅ 可折叠/展开
- ✅ 自动高亮当前路由
- ✅ 响应式设计
- ✅ 徽章支持

---

### Header - 顶部导航栏

包含用户菜单、主题切换、通知按钮。

**使用方法**：

```tsx
import { Header } from '@/components/layout/Header'

function MainLayout() {
  return (
    <div className="flex flex-col">
      <Header />
      {/* Main content */}
    </div>
  )
}
```

**特性**：
- ✅ 用户头像/菜单
- ✅ 主题切换按钮
- ✅ 通知按钮
- ✅ 下拉菜单

---

### MainLayout - 主布局

完整的页面布局（Sidebar + Header + 内容区）。

**使用方法**：

```tsx
import { MainLayout } from '@/components/layout/MainLayout'
import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="projects" element={<ProjectsPage />} />
      </Route>
    </Routes>
  )
}
```

---

## 通用 UI 组件

### Toast - 消息通知

（参见 ToastProvider）

---

### Pagination - 分页组件

分页组件，支持页码跳转和每页条数选择。

**使用方法**：

```tsx
import { Pagination } from '@/components/ui/pagination'

function UserList() {
  const [currentPage, setCurrentPage] = useState(1)
  const totalPages = 10
  const totalItems = 100

  return (
    <Pagination
      currentPage={currentPage}
      totalPages={totalPages}
      totalItems={totalItems}
      onPageChange={setCurrentPage}
      showSizeChanger
      pageSizeOptions={[10, 20, 50]}
      onPageSizeChange={(size) => console.log('Page size:', size)}
    />
  )
}
```

**Props**：
- `currentPage: number` - 当前页码
- `totalPages: number` - 总页数
- `totalItems?: number` - 总条数（可选，显示统计信息）
- `onPageChange: (page) => void` - 页码变化回调
- `showSizeChanger?: boolean` - 是否显示每页条数选择器
- `pageSizeOptions?: number[]` - 每页条数选项

---

### ConfirmDialog - 二次确认弹窗

（参见 ConfirmProvider）

---

### EmptyState - 空状态组件

空状态展示组件。

**使用方法**：

```tsx
import { EmptyState } from '@/components/ui/empty-state'

function ProjectList() {
  if (projects.length === 0) {
    return (
      <EmptyState
        type="empty"
        title="暂无项目"
        description="还没有任何项目，快去创建第一个项目吧！"
        actionText="创建项目"
        onAction={() => handleCreate()}
      />
    )
  }

  return <div>{/* 项目列表 */}</div>
}
```

**Props**：
- `type?: 'empty' | 'not-found' | 'error'` - 空状态类型
- `title?: string` - 标题
- `description?: string` - 描述
- `actionText?: string` - 操作按钮文本
- `onAction?: () => void` - 操作按钮回调

---

## API 客户端

### Axios 实例

预配置的 Axios 实例，自动注入 Token 和处理错误。

**使用方法**：

```tsx
import apiClient from '@/api/client'

// GET 请求
const users = await apiClient.get('/users')

// POST 请求
const newUser = await apiClient.post('/users', {
  name: 'John Doe',
  email: 'john@example.com',
})

// PUT 请求
const updatedUser = await apiClient.put(`/users/${id}`, {
  name: 'Jane Doe',
})

// DELETE 请求
await apiClient.delete(`/users/${id}`)

// 错误处理
try {
  const data = await apiClient.get('/users')
} catch (error) {
  // Token 过期会自动跳转到登录页
  // 其他错误已在拦截器中处理
  console.error('请求失败:', error)
}
```

**特性**：
- ✅ 自动注入 Authorization Token
- ✅ 401 自动跳转登录页
- ✅ 统一错误处理
- ✅ 请求超时配置（10s）

---

## 完整示例

```tsx
import { ThemeProvider } from '@/contexts/ThemeContext'
import { AuthProvider } from '@/contexts/AuthContext'
import { ToastProvider } from '@/components/ui/toast'
import { ConfirmProvider } from '@/components/ui/confirm-dialog'
import { MainLayout } from '@/components/layout/MainLayout'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider defaultTheme="system" storageKey="sisyphus-ui-theme">
        <AuthProvider>
          <ToastProvider>
            <ConfirmProvider>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/" element={<MainLayout />}>
                  <Route index element={<DashboardPage />} />
                  <Route path="projects" element={<ProjectsPage />} />
                </Route>
              </Routes>
            </ConfirmProvider>
          </ToastProvider>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  )
}
```

---

## 开发规范

1. **使用语义化颜色 Token**（Tailwind v4）：
   ```tsx
   // ✅ 正确
   <div className="bg-background text-foreground">

   // ❌ 错误
   <div className="bg-white text-gray-900">
   ```

2. **使用类型导入**：
   ```tsx
   // ✅ 正确
   import { type ReactNode } from 'react'

   // ❌ 错误
   import { ReactNode } from 'react'
   ```

3. **使用 cn() 工具函数合并类名**：
   ```tsx
   import { cn } from '@/lib/utils'

   <div className={cn('base-class', isActive && 'active-class')} />
   ```

---

## 相关文档

- [需求文档](../temp/01_需求文档.md)
- [README](../README.md)
- [Tailwind CSS v4 文档](https://tailwindcss.com/docs)
- [shadcn/ui 文档](https://ui.shadcn.com)
