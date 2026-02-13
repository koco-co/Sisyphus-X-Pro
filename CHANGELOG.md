# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- 项目初始化文档 (README.md, CLAUDE.md)
- 后端项目骨架 (FastAPI + SQLAlchemy 2.0)
- 前端项目骨架 (React + TypeScript + Vite)
- 数据库模型定义 (15 张表)
- 项目技术架构设计

### Changed
- 优化项目目录结构
- 统一代码风格规范 (ESLint + ruff)

### Fixed
- 修复 Python 类型注解兼容性问题 (使用 `Optional` 而非 `|` 语法)
- 修复模型文件导入路径错误

---

## [0.1.0] - TBD

### Added
- 初始项目结构
- 核心技术栈选型
  - 前端: React 18 + TypeScript 5.0 + Vite + TailwindCSS + shadcn/ui
  - 后端: FastAPI (Python 3.12) + SQLAlchemy 2.0 + JWT
  - 核心执行器: pytest + sisyphus-api-engine
  - 中间件: PostgreSQL + MinIO + Redis
- 需求文档 (temp/01_需求文档.md)
- 接口定义 (temp/02_接口定义.md)
- 数据库设计 (temp/03_数据库设计.md)
- 任务清单 (temp/04_任务清单.md)
- 开发规范文档 (CLAUDE.md)
- 项目说明文档 (README.md)

---

## 语义化版本规范 (Semantic Versioning)

本项目遵循 [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) 规范:

```
版本号格式: MAJOR.MINOR.PATCH

- MAJOR (主版本号): 不兼容的 API 变更
- MINOR (次版本号): 向下兼容的功能新增
- PATCH (修订号): 向下兼容的 Bug 修复
```

### 版本号示例

| 版本变更 | 说明 | 示例 |
|---------|------|------|
| `0.1.0` → `0.1.1` | Bug 修复 | 修复数据库连接错误 |
| `0.1.0` → `0.2.0` | 新增功能 | 添加用户认证模块 |
| `0.1.0` → `1.0.0` | 破坏性变更 | API 接口重构 |

### 变更类型说明

- **Added**: 新增功能
- **Changed**: 功能变更 (向下兼容)
- **Deprecated**: 即将废弃的功能
- **Removed**: 已删除的功能
- **Fixed**: Bug 修复
- **Security**: 安全漏洞修复

---

## 发布流程

### 1. 开发阶段

所有新功能开发和 Bug 修复都在 `[Unreleased]` 部分记录。

### 2. 发布准备

发布前执行以下检查:

```bash
# 运行测试
npm test                    # 前端测试
pytest tests/ --cov=app     # 后端测试 (覆盖率 ≥ 80%)

# 代码风格检查
npm run lint                # 前端 ESLint
ruff check app/             # 后端 ruff

# 类型检查
npm run type-check          # 前端 TypeScript
pyright app/                # 后端 pyright
```

### 3. 发布步骤

1. 更新 CHANGELOG.md:
   - 将 `[Unreleased]` 内容移至新版本号下
   - 添加发布日期 (YYYY-MM-DD)
   - 创建新的空 `[Unreleased]` 部分

2. 提交变更:
   ```bash
   git add CHANGELOG.md
   git commit -m "chore: release v0.1.0"
   git tag v0.1.0
   git push origin main --tags
   ```

### 4. 发布后

- 更新 README.md 中的版本号
- 生成 GitHub Release Notes
- 通知团队成员

---

## 变更日志模板

### 新功能发布

```markdown
## [1.0.0] - 2026-XX-XX

### Added
- 用户认证模块 (邮箱注册/登录 + OAuth)
- 项目管理功能
- 接口定义与管理
- 场景编排与调试
- 测试计划与执行
- 测试报告生成

### Changed
- 优化数据库查询性能
- 改进 API 响应格式

### Fixed
- 修复 JWT Token 刷新问题
- 修复数据库连接池泄漏
```

### Bug 修复发布

```markdown
## [0.1.1] - 2026-XX-XX

### Fixed
- 修复场景调试时的变量替换错误
- 修复 Allure 报告路径问题
- 修复前端 Monaco Editor 高度异常

### Security
- 修复 SQL 注入漏洞 (CVE-XXXX-XXXXX)
```

### 破坏性变更发布

```markdown
## [2.0.0] - 2026-XX-XX

### Added
- 全新的 UI 设计系统
- GraphQL API 支持

### Changed
- **BREAKING**: API 响应格式调整
  - 旧格式: `{ code: 200, data: {...} }`
  - 新格式: `{ success: true, data: {...} }`
  - 迁移指南: `docs/migration-v1-to-v2.md`

### Removed
- **BREAKING**: 移除旧版 API v1 端点
- **BREAKING**: 移除对 Python 3.11 的支持

### Deprecated
- REST API v1 将在 v3.0.0 中移除
```

---

## 版本号链接

```markdown
[Unreleased]: https://github.com/poco/Sisyphus-X-Pro/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/poco/Sisyphus-X-Pro/releases/tag/v0.1.0
```

---

> **维护者**: technical-writer (poco)
>
> **最后更新**: 2026-02-13
>
> **相关文档**:
> - [README.md](README.md) - 项目说明
> - [CLAUDE.md](CLAUDE.md) - 开发规范
> - [Keep a Changelog](https://keepachangelog.com/) - 格式规范
> - [Semantic Versioning](https://semver.org/) - 版本规范
