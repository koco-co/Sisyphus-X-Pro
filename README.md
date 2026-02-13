# Sisyphus-X-Pro

<div align="center">

**自动化测试管理平台**

让接口自动化测试的编排、执行、报告全流程可视化、可追溯

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 项目简介

Sisyphus-X-Pro 是一款面向 QA 团队与开发团队的**企业级自动化测试管理平台**。产品致力于让接口自动化测试的编排、执行、报告全流程可视化、可追溯,降低自动化测试门槛,提升交付效率。

### 品牌寓意

取名自希腊神话「西西弗斯」,寓意 **打破命运的循环** — 将重复、枯燥的回归测试交给自动化,让测试工程师从"推巨石"中解放出来。

### 核心价值

- **YAML 驱动**: 一个 YAML 文件 = 一个完整测试场景,可读性与版本控制兼顾
- **可视化编排**: 支持拖拽排序的测试步骤编排,降低学习成本
- **双报告体系**: 平台自定义报告 + Allure 报告,满足不同粒度的分析需求
- **数据驱动**: 支持 CSV 导入/平台创建数据集,一份用例覆盖 N 组数据
- **可扩展关键字**: 用户可自定义 Python 关键字函数,灵活扩展测试能力

---

## 功能概览

### 核心功能模块

#### FR-001 登录注册
- 邮箱注册/登录
- GitHub / Google OAuth 单点登录
- JWT Token 认证
- 开发模式免鉴权

#### FR-002 首页仪表盘
- 核心指标卡片 (项目/接口/场景/计划总数)
- 测试执行趋势图
- 项目覆盖率概览

#### FR-003 项目管理
- 项目 CRUD 操作
- 数据库配置管理 (MySQL/PostgreSQL)
- 连接状态自动检测
- 多数据源支持

#### FR-004 关键字配置
- 内置关键字库 (发送请求/断言/提取变量/数据库操作)
- 自定义关键字编辑器 (Monaco Editor)
- 关键字启用/禁用
- 关键字参数管理

#### FR-005 接口定义
- 接口目录树管理
- cURL 命令导入
- 环境管理 (多环境切换)
- 全局变量/环境变量管理
- MinIO 文件上传

#### FR-006 场景编排
- 可视化步骤编排
- 关键字联动 (类型 → 名称 → 参数)
- 前置/后置 SQL 支持
- 数据驱动测试 (CSV 导入)
- 场景调试 (Allure 报告)

#### FR-007 测试计划
- 测试场景编排
- 批量执行 (场景顺序执行,数据驱动并行执行)
- 实时进度监控
- 终止/暂停/恢复控制

#### FR-008 测试报告
- 历史报告列表
- 平台自定义报告模板
- Allure 报告集成
- 报告导出功能
- 30 天自动清理

#### FR-009 核心执行器
- YAML 文件解析
- 变量替换引擎
- 数据驱动执行
- 多格式报告 (文本/JSON/Allure/HTML)

#### FR-010 全局参数
- 工具函数库 (StringUtils/TimeUtils 等)
- Monaco Editor 代码编辑
- Docstring 自动解析
- 场景中通过 `{{函数名()}}` 引用

---

## 技术栈

### 前端
- **框架**: React 18 + TypeScript 5.0
- **构建工具**: Vite
- **UI 组件**: TailwindCSS + shadcn/ui
- **编辑器**: Monaco Editor
- **路由**: React Router
- **国际化**: i18n

### 后端
- **框架**: FastAPI (Python 3.12)
- **ORM**: SQLAlchemy 2.0 (Mapped + DeclarativeBase)
- **认证**: JWT + OAuth
- **工具链**: uv + ruff + pyright

### 核心执行器
- **引擎**: pytest
- **HTTP 库**: requests
- **报告**: allure-pytest
- **CLI**: sisyphus-api-engine

### 中间件
- **数据库**: PostgreSQL 15+
- **对象存储**: MinIO
- **缓存**: Redis

---

## 快速启动

### 前置要求

- Docker 和 Docker Compose
- Python 3.12+
- Node.js 18+
- uv (Python 包管理器)

### 一键启动中间件

```bash
# 启动 PostgreSQL, MinIO, Redis
docker-compose up -d

# 检查服务状态
docker-compose ps
```

### 后端启动

```bash
cd backend

# 安装依赖
uv sync

# 复制环境变量
cp .env.example .env

# 初始化数据库
python -m app.init_db

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档: http://localhost:8000/docs

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端访问地址: http://localhost:5173

### 核心执行器安装

```bash
cd api-engine

# 安装依赖
uv sync

# 安装 CLI 工具
pip install -e .
```

---

## 项目结构

```
Sisyphus-X-Pro/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── api/                # API 客户端
│   │   ├── components/         # 通用组件
│   │   ├── pages/              # 页面组件
│   │   ├── contexts/           # 全局状态
│   │   ├── hooks/              # 自定义 Hooks
│   │   ├── i18n/               # 国际化
│   │   ├── types/              # TypeScript 类型
│   │   └── utils/              # 工具函数
│   └── package.json
│
├── backend/                     # 后端项目
│   ├── app/
│   │   ├── models/             # SQLAlchemy 数据模型
│   │   ├── routers/            # API 路由
│   │   ├── services/           # 业务逻辑层
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── middleware/         # 中间件
│   │   ├── utils/              # 工具函数
│   │   └── tasks/              # 定时任务
│   └── pyproject.toml
│
├── api-engine/                  # 核心执行器
│   └── src/sisyphus_api_engine/
│       ├── cli.py              # CLI 入口
│       ├── yaml_parser.py      # YAML 解析器
│       ├── variable_manager.py # 变量管理器
│       ├── runner.py           # pytest Runner
│       └── reporters/          # 报告生成器
│
├── tests/                       # 测试项目
│   ├── backend/                # 白盒测试 (pytest)
│   └── e2e/                    # 黑盒测试 (Playwright)
│
├── temp/                        # 文档目录
│   ├── 01_需求文档.md
│   ├── 02_接口定义.md
│   ├── 03_数据库设计.md
│   └── 04_任务清单.md
│
├── docker-compose.yml           # 中间件部署
├── README.md                    # 项目说明
├── CHANGELOG.md                 # 变更日志
└── CLAUDE.md                    # 开发规范
```

---

## 开发规范

### 代码风格

#### 前端
- 遵循 ESLint + Prettier 配置
- 使用 TypeScript 严格模式
- 组件命名采用 PascalCase
- 文件命名采用 kebab-case

#### 后端
- 遵循 ruff + pyright 配置
- 使用 Google Python 风格指南
- 函数命名采用 snake_case
- 类命名采用 PascalCase
- 注释使用中文

### Git 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

[optional body]

[optional footer]
```

类型:
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 重构
- `docs`: 文档
- `test`: 测试
- `chore`: 构建/工具
- `perf`: 性能优化
- `ci`: CI 配置

示例:
```bash
feat: 添加场景调试功能
fix: 修复数据库连接状态检测问题
docs: 更新 README 安装指南
```

### 分支策略

- `main`: 主分支,保持稳定
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支
- `hotfix/*`: 紧急修复分支

### 测试要求

- **白盒测试**: 使用 pytest,覆盖率 ≥ 80%
- **黑盒测试**: 使用 Playwright,覆盖核心用户流程
- 遵循 TDD 开发流程: 红 → 绿 → 重构

---

## 开发路线图

### Phase 1: MVP (当前阶段)
- [x] 项目初始化
- [ ] 登录注册 (FR-001)
- [ ] 项目管理 (FR-003)
- [ ] 关键字配置 (FR-004)
- [ ] 接口定义 (FR-005)
- [ ] 场景编排 (FR-006)
- [ ] 测试计划 (FR-007)
- [ ] 测试报告 (FR-008)
- [ ] 全局参数 (FR-010)

### Phase 2: WEB 自动化
- 浏览器集群管理
- 元素定位器
- 页面对象模式
- 关键字扩展

### Phase 3: APP 自动化
- Appium 集成
- 设备管理
- 用例录制

### Phase 4: 消息通知
- 邮件通知
- 钉钉/企业微信集成
- Webhook 支持

---

## 文档

- [需求文档](./temp/01_需求文档.md)
- [接口定义](./temp/02_接口定义.md)
- [数据库设计](./temp/03_数据库设计.md)
- [任务清单](./temp/04_任务清单.md)
- [开发规范](./CLAUDE.md)
- [变更日志](./CHANGELOG.md)

---

## 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 联系方式

- 作者: poco
- 项目地址: [GitHub](https://github.com/poco/Sisyphus-X-Pro)

---

<div align="center">

**打破命运循环 · 解放测试生产力**

Made with ❤️ by Sisyphus Team

</div>
