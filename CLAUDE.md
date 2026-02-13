# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Sisyphus-X-Pro 是一款面向 QA 团队的企业级自动化测试管理平台,采用前后端分离架构,核心特色是 YAML 驱动的测试场景编排和可视化测试管理。

**技术栈**:
- 前端: React 18 + TypeScript 5.0 + Vite + TailwindCSS v4 + shadcn/ui + Monaco Editor
- 后端: FastAPI (Python 3.12+) + SQLAlchemy 2.0 (Mapped + DeclarativeBase) + asyncpg
- 核心执行器: pytest + sisyphus-api-engine (独立 CLI 工具)
- 中间件: PostgreSQL 15+ + MinIO + Redis

## 开发环境启动

### 前置依赖
```bash
# Docker 服务 (PostgreSQL/MinIO/Redis)
docker-compose up -d

# 检查服务状态
docker-compose ps
```

### 后端开发
```bash
cd backend

# 安装依赖 (使用 uv)
uv sync

# 环境配置
cp .env.example .env
# 编辑 .env 配置数据库连接、密钥等

# 初始化数据库
python -m app.init_db

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API 文档**: http://localhost:8000/docs

### 前端开发
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (默认端口 3000)
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint
```

**前端地址**: http://localhost:3000

### 核心执行器 (可选)
```bash
cd api-engine

# 安装依赖
uv sync

# 安装 CLI 工具
pip install -e .
```

## 架构要点

### 后端架构 (FastAPI)

**分层结构**:
```
backend/app/
├── main.py              # FastAPI 应用入口, lifespan 管理
├── config.py            # Pydantic Settings 环境配置
├── database.py          # SQLAlchemy async engine 和 Session
├── models/              # SQLAlchemy ORM 模型 (Mapped 模式)
│   └── base.py          # TimestampMixin (created_at/updated_at)
├── schemas/             # Pydantic 请求/响应模型
├── routers/             # API 路由 (依赖 services 层)
├── services/            # 业务逻辑层
├── middleware/          # 中间件 (认证/CORS)
└── utils/               # 工具函数
```

**关键模式**:
- 所有模型继承 `TimestampMixin` 获得时间戳字段
- 使用 `Mapped[]` 类型注解 (SQLAlchemy 2.0 Modern)
- 异步数据库操作 (asyncpg + AsyncSession)
- 路由依赖 services 层,不直接操作数据库
- JWT 认证 + OAuth (GitHub/Google) 支持

**开发模式免鉴权**:
- 设置 `APP_ENV=development` 可跳过 JWT 验证 (中间件自动检测)

### 前端架构 (React)

**目录结构**:
```
frontend/src/
├── main.tsx             # 应用入口
├── App.tsx              # 根组件
├── lib/
│   └── api.ts           # ApiClient 类 (统一 API 调用)
├── components/          # 通用组件
├── pages/               # 页面组件
├── contexts/            # React Context 全局状态
├── hooks/               # 自定义 Hooks
└── types/               # TypeScript 类型定义
```

**关键模式**:
- 使用 `@/` 路径别名 (vite.config.ts 配置)
- ApiClient 统一管理 API 请求和 Token
- localStorage 存储 JWT Token
- Vite 代理 `/api` → `http://localhost:8000`
- TailwindCSS v4 使用 `@theme` inline 模式

### 数据库模型关系

**核心表**:
1. `User` - 用户表 (邮箱密码 + OAuth)
2. `Project` - 项目表
3. `DatabaseConfig` - 数据库配置 (MySQL/PostgreSQL)
4. `Environment` - 环境表 (开发/测试/生产)
5. `EnvVariable` - 环境变量
6. `Interface` + `InterfaceFolder` - 接口定义 (树形结构)
7. `Keyword` - 关键字库 (内置 + 自定义)
8. `Scenario` + `ScenarioStep` - 测试场景
9. `TestPlan` + `PlanScenario` - 测试计划
10. `TestExecution` + `ExecutionStep` - 执行记录
11. `TestReport` - 测试报告
12. `GlobalVariable` - 全局变量
13. `GlobalParam` - 全局参数 (工具函数)
14. `Dataset` - 数据驱动测试数据集

## 常用命令

### 后端
```bash
# 代码风格检查
ruff check app/

# 自动修复
ruff check --fix app/

# 类型检查
pyright app/

# 运行测试
pytest tests/backend/ -v --cov=app --cov-report=html

# 单个测试
pytest tests/backend/test_auth.py::test_login -v
```

### 前端
```bash
# 开发服务器
npm run dev

# 类型检查
tsc -b

# 代码检查
npm run lint

# 预览构建
npm run preview
```

### Docker 服务
```bash
# 启动所有中间件
docker-compose up -d

# 查看日志
docker-compose logs -f postgres

# 停止服务
docker-compose down

# 重启特定服务
docker-compose restart postgres
```

## 开发注意事项

### 后端开发
- 使用 `Mapped[类型] = mapped_column(...)` 定义模型字段
- 所有数据库操作必须使用 `async/await`
- 路由函数签名使用 `async def`
- 使用 `Depends()` 依赖注入获取 Session
- Pydantic schemas 用于请求验证和响应序列化

### 前端开发
- 组件文件使用 PascalCase (如 `UserList.tsx`)
- 工具文件使用 kebab-case (如 `api-client.ts`)
- 使用 `ApiClient` 类调用 API,避免直接 fetch
- 所有 API 调用使用 `try/catch` 错误处理
- 使用 `@/` 路径别名引用 src 目录下的文件

### Git 提交规范
遵循 Conventional Commits:
- `feat:` 新功能
- `fix:` Bug 修复
- `refactor:` 重构
- `docs:` 文档
- `test:` 测试
- `chore:` 构建/工具

示例:
```bash
feat: 添加场景调试功能
fix: 修复数据库连接状态检测问题
docs: 更新 README 安装指南
```

### 分支策略
- `main` - 主分支 (稳定)
- `develop` - 开发分支
- `feature/*` - 功能分支
- `bugfix/*` - 修复分支

## 环境变量配置

**关键配置** (`.env` 文件):
- `DATABASE_URL` - PostgreSQL 连接字符串
- `MINIO_ENDPOINT/ACCESS_KEY/SECRET_KEY` - MinIO 对象存储
- `REDIS_URL` - Redis 缓存
- `JWT_SECRET_KEY` - JWT 签名密钥
- `APP_ENV` - 运行环境 (development/production)
- `GITHUB_CLIENT_ID/SECRET` - GitHub OAuth
- `GOOGLE_CLIENT_ID/SECRET` - Google OAuth

**开发模式**: 设置 `APP_ENV=development` 可跳过 JWT 验证

## 核心功能模块

### FR-001 登录注册
- 邮箱注册/登录 (bcrypt 密码哈希)
- GitHub/Google OAuth 单点登录
- JWT Token 认证 (7 天有效期)
- 开发模式免鉴权

### FR-003 项目管理
- 项目 CRUD 操作
- 多数据库配置 (MySQL/PostgreSQL)
- 连接状态自动检测

### FR-004 关键字配置
- 内置关键字库 (发送请求/断言/提取变量/数据库操作)
- 自定义关键字编辑器 (Monaco Editor)
- 关键字参数管理

### FR-005 接口定义
- 接口目录树管理
- cURL 命令导入
- 环境管理 (多环境切换)
- 全局变量/环境变量管理

### FR-006 场景编排
- 可视化步骤编排 (@dnd-kit 拖拽)
- 关键字联动 (类型 → 名称 → 参数)
- 前置/后置 SQL 支持
- 数据驱动测试 (CSV 导入)
- 场景调试 (Allure 报告)

### FR-007 测试计划
- 测试场景编排
- 批量执行 (场景顺序执行,数据驱动并行执行)
- 实时进度监控
- 终止/暂停/恢复控制

### FR-008 测试报告
- 平台自定义报告模板
- Allure 报告集成
- 报告导出功能
- 30 天自动清理

## 测试要求

- **白盒测试**: 使用 pytest,覆盖率 ≥ 80%
- **黑盒测试**: 使用 Playwright,覆盖核心用户流程
- 遵循 TDD 开发流程: 红 → 绿 → 重构

## 相关文档

- [需求文档](./temp/01_需求文档.md)
- [接口定义](./temp/02_接口定义.md)
- [数据库设计](./temp/03_数据库设计.md)
- [任务清单](./temp/04_任务清单.md)
- [变更日志](./CHANGELOG.md)
