# 前端项目快速启动指南

## 🚀 快速开始

### 1. 安装依赖
```bash
cd frontend
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```
访问 http://localhost:3000

### 3. 构建生产版本
```bash
npm run build
```

## 📦 技术栈

- **React 19.2.0** + **TypeScript 5.9**
- **Vite 7.3** - 构建工具
- **TailwindCSS v4.1.18** - 样式框架
- **shadcn/ui** - UI 组件库
- **React Router DOM 7.13** - 路由
- **Axios** - HTTP 客户端
- **Monaco Editor** - 代码编辑器

## 🔧 配置说明

### API 代理
开发环境下，所有 `/api` 请求会自动代理到 `http://localhost:8000`

### 路径别名
使用 `@` 作为 `src` 目录的别名：
```typescript
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
```

### 环境变量
在 `.env` 文件中配置：
- `VITE_API_URL` - 后端 API 地址
- `VITE_APP_TITLE` - 应用标题
- `VITE_APP_VERSION` - 应用版本

## 🎨 添加 shadcn/ui 组件

```bash
# 添加单个组件
npx shadcn@latest add button

# 添加多个组件
npx shadcn@latest add button dialog dropdown-menu input
```

## 📁 项目结构

```
src/
├── components/
│   ├── ui/              # shadcn/ui 组件
│   └── layout/          # 布局组件
├── pages/               # 页面组件
├── contexts/            # React Context
├── hooks/               # 自定义 Hooks
├── api/                 # API 客户端
├── utils/               # 工具函数
├── types/               # TypeScript 类型
├── i18n/                # 国际化
├── App.tsx              # 根组件
├── main.tsx             # 入口文件
└── index.css            # 全局样式
```

## ✅ 已完成的配置

- ✅ Vite + React + TypeScript
- ✅ TailwindCSS v4 (CSS-first 配置)
- ✅ shadcn/ui 集成准备
- ✅ 路径别名 (@/*)
- ✅ API 代理配置
- ✅ TypeScript 严格模式
- ✅ ESLint 配置
- ✅ 环境变量类型定义
- ✅ 构建优化配置

## 🚀 下一步

1. 使用 shadcn CLI 添加基础 UI 组件
2. 创建布局组件（Header, Sidebar, MainLayout）
3. 实现路由和页面结构
4. 集成 API 客户端
5. 实现认证逻辑
