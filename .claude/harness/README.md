# Sisyphus-X-Pro 无人值守 AI 开发流程

基于 Anthropic 的 [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 设计,用于实现跨多个上下文窗口的长时间运行 AI 开发。

## 📋 概述

这个 harness 系统解决了长时间运行 AI Agent 的核心问题:
- **上下文窗口限制**: 每个 Agent 会话都有记忆空白
- **功能过早完成**: Agent 倾向于过早声明项目完成
- **环境状态混乱**: Agent 留下半成品和 Bug
- **测试不足**: Agent 缺少端到端验证

## 🏗️ 架构组件

### 1. Initializer Agent (初始化代理)
**职责**: 设置初始开发环境
- 创建完整的项目结构
- 配置开发工具链
- 创建功能清单 (feature_list.json)
- 编写初始化脚本 (init.sh)
- 设置进度追踪系统

**运行时机**: 项目第一次启动时

### 2. Coding Agent (编码代理)
**职责**: 每次会话实现一个功能
- 阅读进度和功能清单
- 运行基础健康检查
- 选择并实现一个功能
- 通过端到端测试验证
- 更新进度并提交代码

**运行时机**: 每次新的开发会话

### 3. 核心文件

```
.claude/harness/
├── feature_list.json           # 功能清单 (54 个功能)
├── init.sh                     # 环境初始化脚本
├── stop.sh                     # 停止服务脚本
├── health_check.py             # 健康检查脚本
├── test_helper.py              # 测试辅助工具
├── claude-progress.txt         # 进度日志
├── initializer_agent_prompt.md # Initializer Agent 提示词
├── coding_agent_prompt.md      # Coding Agent 提示词
├── session_checklist.md        # 会话检查清单
└── README.md                   # 本文件
```

## 🚀 快速开始

### 第一次运行 (Initializer Agent)

1. **创建新项目并设置环境**:
```bash
# 克隆或创建项目
cd Sisyphus-X-Pro

# 确保 Docker 运行
docker --version
docker-compose --version

# 运行初始化
source .claude/harness/init.sh
```

2. **验证环境**:
```bash
# 检查服务状态
python .claude/harness/health_check.py

# 访问前端
open http://localhost:3000

# 访问 API 文档
open http://localhost:8000/docs
```

3. **查看功能清单**:
```bash
cat .claude/harness/feature_list.json | python -m json.tool
```

### 每次开发会话 (Coding Agent)

1. **启动会话**:
```bash
# 进入项目目录
cd Sisyphus-X-Pro

# 启动开发环境
source .claude/harness/init.sh

# 验证服务正常
python .claude/harness/health_check.py
```

2. **了解当前状态**:
```bash
# 阅读进度日志
cat .claude/harness/claude-progress.txt

# 查看功能完成情况
python .claude/harness/test_helper.py

# 查看最近提交
git log --oneline -20

# 查看当前状态
git status
```

3. **选择并实现功能**:
- 阅读 `feature_list.json`
- 选择一个 `passes: false` 的功能
- 按照 TDD 流程实现
- 使用 Playwright 进行端到端测试
- 更新 `feature_list.json` 中的 `passes` 为 `true`

4. **提交并结束会话**:
```bash
# 运行代码检查
ruff check backend/ --fix
pyright backend/
cd frontend && npm run lint && cd ..

# 提交变更
git add .
git commit -m "feat: 实现 XXX 功能"

# 推送到远程
git push origin main

# 更新进度日志 (手动编辑)
vim .claude/harness/claude-progress.txt

# 停止服务 (可选)
source .claude/harness/stop.sh
```

## 📊 功能清单结构

`feature_list.json` 包含 54 个功能,分为 9 个模块:

```json
{
  "categories": {
    "authentication": {
      "name": "用户认证模块 (FR-001)",
      "priority": 1,
      "features": [
        {
          "id": "AUTH-001",
          "category": "functional",
          "description": "用户可以通过邮箱和密码注册新账户",
          "steps": ["详细测试步骤..."],
          "passes": false,
          "verification_method": "e2e_browser_test"
        }
      ]
    }
  },
  "metadata": {
    "total_features": 54,
    "completed_features": 0,
    "completion_rate": 0.0
  }
}
```

### 功能优先级

1. **authentication** (AUTH-***): 用户认证 - 最高优先级
2. **dashboard** (DASH-***): 首页仪表盘
3. **project_management** (PROJ-***): 项目管理
4. **keyword_management** (KEYW-***): 关键字配置
5. **interface_management** (INTF-***): 接口定义
6. **scenario_orchestration** (SCEN-***): 场景编排
7. **test_plan** (PLAN-***): 测试计划
8. **test_report** (REPT-***): 测试报告
9. **global_params** (GPAR-***): 全局参数

## ✅ 质量保证

### 代码检查

**后端**:
```bash
# 代码风格
ruff check backend/ --fix

# 类型检查
pyright backend/

# 测试
pytest backend/tests/ -v --cov=app --cov-report=html
```

**前端**:
```bash
# 代码检查
npm run lint

# 类型检查
npm run type-check  # 如果有配置

# E2E 测试
npx playwright test
```

### 健康检查

```bash
# 运行基础健康检查
python .claude/harness/health_check.py

# 检查项:
# - 后端服务 (http://localhost:8000/health)
# - 数据库连接
# - API 文档访问
# - 前端服务 (http://localhost:3000)
# - 功能清单文件
```

## 🎯 成功标准

### Initializer Agent
- [ ] 项目结构完整
- [ ] 开发环境可正常启动
- [ ] 功能清单包含所有 54 个功能
- [ ] 健康检查全部通过
- [ ] 文档完整清晰

### Coding Agent
- [ ] 每次会话实现一个完整功能
- [ ] 所有测试通过 (单元 + E2E)
- [ ] 代码符合规范 (ruff/pyright/ESLint)
- [ ] 功能清单已更新
- [ ] 代码已提交
- [ ] 进度日志已更新
- [ ] 代码库处于可提交状态

## 🚨 常见问题

### Q: 如何处理环境问题?
A: 重新运行 `init.sh`,检查 Docker 服务,查看日志文件。

### Q: 测试失败怎么办?
A: 分析失败原因,修复代码,重新运行测试。**不要修改测试**。

### Q: 可以一次实现多个功能吗?
A: **不可以**。每次会话只实现一个功能,确保质量。

### Q: 如何验证功能完成?
A: 必须通过端到端测试 (Playwright),不能只依赖单元测试。

### Q: 忘记提交代码怎么办?
A: 立即提交,并在下次会话开始时检查状态。

## 📚 参考资料

- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Playwright Documentation](https://playwright.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 贡献

这个 harness 系统是为 Sisyphus-X-Pro 项目定制的,但可以适配到其他项目。主要需要修改:

1. `feature_list.json` - 功能清单
2. `init.sh` - 初始化脚本
3. `health_check.py` - 健康检查
4. 项目特定的测试配置

## 📄 许可证

MIT License - 与 Sisyphus-X-Pro 项目一致

---

**维护者**: poco
**最后更新**: 2026-02-13
**版本**: 1.0.0
