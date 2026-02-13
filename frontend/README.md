# Sisyphus-X-Pro Frontend

## 技术栈

- **框架**: React 19 + TypeScript
- **构建工具**: Vite
- **样式**: TailwindCSS v4 + shadcn/ui
- **路由**: React Router v7
- **HTTP 客户端**: Axios
- **图标**: Lucide React

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器 (http://localhost:3000)
npm run dev

# 构建
npm run build
```

## 项目结构

```
src/
├── components/
│   ├── layout/           # 布局组件
│   └── ui/               # 通用 UI 组件
├── contexts/             # React Context
├── pages/                # 页面组件
├── api/                  # API 客户端
├── lib/                  # 工具函数
├── App.tsx               # 路由配置
└── main.tsx              # 应用入口
```

## 可用组件

### Context Providers
- **ThemeProvider** - 深色/浅色主题切换
- **AuthProvider** - 用户认证管理
- **ToastProvider** - 消息通知（右上角，带进度条）
- **ConfirmProvider** - 二次确认弹窗

### 布局组件
- **Sidebar** - 可折叠侧边栏
- **Header** - 顶部导航栏（用户菜单 + 主题切换）
- **MainLayout** - 完整布局

### 通用 UI 组件
- **Toast** - 消息通知
- **Pagination** - 分页组件
- **ConfirmDialog** - 二次确认弹窗
- **EmptyState** - 空状态组件

详细使用方法请参考 [COMPONENTS.md](./COMPONENTS.md)

## 文档

- [组件使用指南](./COMPONENTS.md)
- [需求文档](../temp/01_需求文档.md)
- [项目 README](../README.md)
