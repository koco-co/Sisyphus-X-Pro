# 无人值守 AI 开发流程 - 实施总结

## 📌 概述

基于 Anthropic 的研究成果,我们为 **Sisyphus-X-Pro** 项目构建了一个完整的无人值守 AI 开发流程。这个流程解决了长时间运行 AI Agent 在多个上下文窗口中持续工作的核心挑战。

## 🎯 解决的问题

### 核心挑战
1. **上下文窗口限制**: 每个 Agent 会话都是全新的,没有记忆
2. **功能过早完成**: Agent 倾向于过早声明项目完成
3. **环境状态混乱**: Agent 留下半成品代码和 Bug
4. **测试验证不足**: Agent 缺少端到端验证,导致功能不完整

### 解决方案
- **两阶段 Agent 设计**: Initializer Agent (初始化) + Coding Agent (编码)
- **功能清单系统**: 详细的 JSON 格式功能列表,每个功能都有明确的测试步骤
- **进度追踪**: 清晰的日志系统,记录每个会话的进展
- **健康检查**: 每次会话开始时验证基础功能正常
- **端到端测试**: 强制要求使用 Playwright 进行完整的功能验证

## 🏗️ 系统架构

### 文件结构

```
.claude/harness/
├── feature_list.json              # 🎯 核心文件: 54 个功能的详细清单
├── init.sh                        # 🚀 环境初始化脚本
├── stop.sh                        # 🛑 停止服务脚本
├── health_check.py                # 🏥 健康检查脚本
├── test_helper.py                 # 🧪 测试辅助工具
├── claude-progress.txt            # 📝 进度追踪日志
├── initializer_agent_prompt.md    # 🤖 Initializer Agent 提示词
├── coding_agent_prompt.md         # 💻 Coding Agent 提示词
├── session_checklist.md           # ✅ 会话检查清单
├── quickstart.sh                  # ⚡ 快速启动脚本
├── README.md                      # 📖 使用文档
└── SUMMARY.md                     # 📊 本文件
```

### 两个 Agent 的职责

#### Initializer Agent (初始化代理)
**运行时机**: 项目第一次启动

**任务清单**:
- ✅ 创建完整的项目结构
- ✅ 配置前后端开发框架
- ✅ 创建 15 张数据库表
- ✅ 配置 Docker Compose 服务
- ✅ 创建功能清单 (54 个功能)
- ✅ 编写初始化脚本
- ✅ 编写健康检查脚本
- ✅ 配置代码检查工具
- ✅ 编写项目文档

**产出**: 完整、可工作的开发环境

#### Coding Agent (编码代理)
**运行时机**: 每次新的开发会话

**会话工作流程**:
1. **启动阶段** (5 分钟)
   - 运行 `init.sh` 启动服务
   - 运行 `health_check.py` 验证环境
   - 阅读 `claude-progress.txt` 了解进度
   - 阅读 `feature_list.json` 选择功能
   - 查看最近的 git 提交

2. **实现阶段** (30-60 分钟)
   - 选择一个高优先级的未完成功能
   - 制定实现计划
   - TDD 开发: 测试先行
   - 编写单元测试 (pytest)
   - 实现代码逻辑
   - 编写 E2E 测试 (Playwright)
   - 验证所有测试通过

3. **收尾阶段** (10 分钟)
   - 运行代码检查 (ruff/pyright/ESLint)
   - 更新 `feature_list.json` 标记功能完成
   - 创建 git commit 并推送
   - 更新 `claude-progress.txt` 记录进展
   - 验证代码库处于干净状态

**产出**: 一个完整的功能 + 清晰的进展记录

## 📊 功能清单设计

### 功能分类 (9 个模块,54 个功能)

| 模块 | ID 前缀 | 功能数 | 优先级 |
|------|---------|--------|--------|
| 用户认证 | AUTH-*** | 8 | 1 (最高) |
| 首页仪表盘 | DASH-*** | 3 | 2 |
| 项目管理 | PROJ-*** | 6 | 3 |
| 关键字配置 | KEYW-*** | 5 | 4 |
| 接口定义 | INTF-*** | 6 | 5 |
| 场景编排 | SCEN-*** | 7 | 6 |
| 测试计划 | PLAN-*** | 6 | 7 |
| 测试报告 | REPT-*** | 5 | 8 |
| 全局参数 | GPAR-*** | 4 | 9 |

### 功能结构

```json
{
  "id": "AUTH-001",
  "category": "functional",
  "description": "用户可以通过邮箱和密码注册新账户",
  "steps": [
    "导航到注册页面",
    "输入有效邮箱地址",
    "输入密码 (至少8位)",
    "确认密码",
    "点击注册按钮",
    "验证收到验证邮件",
    "点击邮件中的验证链接",
    "验证自动登录到系统"
  ],
  "passes": false,
  "verification_method": "e2e_browser_test"
}
```

**关键设计**:
- `steps` 字段包含详细的测试步骤,可直接转换为 E2E 测试
- `passes` 字段唯一可修改,用于标记功能完成状态
- `verification_method` 指定验证方法 (E2E 测试/API 测试/数据库检查)

## 🔄 工作流程详解

### 第一次运行 (Initializer Agent)

```bash
# 1. Initializer Agent 创建项目结构
# 2. 运行初始化脚本
source .claude/harness/init.sh

# 3. 验证环境
python .claude/harness/health_check.py

# ✅ 输出: 所有服务运行正常,可以开始开发
```

### 每次会话 (Coding Agent)

```bash
# 1. 快速启动
source .claude/harness/quickstart.sh

# 2. 查看状态
python .claude/harness/test_helper.py
# 输出: 功能总数: 54, 已完成: 5, 完成率: 9.3%

# 3. 选择功能
cat .claude/harness/feature_list.json
# 选择下一个高优先级功能: AUTH-002

# 4. 实现功能 (遵循 TDD)
# - 编写测试
# - 实现代码
# - 验证测试
# - E2E 测试

# 5. 提交并更新
git add .
git commit -m "feat: 实现用户登录功能 (AUTH-002)"
git push

# 6. 更新功能清单
# 编辑 feature_list.json: AUTH-002 的 passes 改为 true

# 7. 更新进度日志
# 编辑 claude-progress.txt 添加会话记录
```

## 🛡️ 质量保证机制

### 1. 健康检查 (每次会话开始)
```python
health_check.py 检查:
✓ 后端服务响应
✓ 数据库连接
✓ API 文档访问
✓ 前端服务响应
✓ 功能清单文件
```

### 2. 代码检查 (每次提交前)
```bash
# 后端
ruff check backend/ --fix      # 代码风格
pyright backend/               # 类型检查
pytest backend/tests/ -v       # 单元测试

# 前端
npm run lint                   # 代码检查
npx playwright test            # E2E 测试
```

### 3. 端到端验证 (功能完成)
```typescript
// 使用 Playwright
test("用户可以通过邮箱和密码登录", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.fill('[name="email"]', "test@example.com");
  await page.fill('[name="password"]', "password123");
  await page.click('[type="submit"]');
  await expect(page).toHaveURL("http://localhost:3000/dashboard");
});
```

### 4. Git 提交规范
```
feat: 实现用户登录功能 (AUTH-002)

- 添加登录 API 端点
- 创建登录页面组件
- 实现 JWT token 验证
- 编写单元测试和 E2E 测试

测试结果:
- 单元测试: ✅ 全部通过 (15/15)
- E2E 测试: ✅ 全部通过 (5/5)
- 代码覆盖率: 92%

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## 📈 进度追踪

### 功能完成率
- 初始状态: 0/54 (0%)
- 目标状态: 54/54 (100%)
- 当前状态: 实时更新

### 会话历史
每次会话记录包含:
- 实现的功能 ID 和描述
- 创建/修改的文件
- 测试结果 (单元测试 + E2E 测试)
- 代码覆盖率
- Git 提交哈希
- 已知问题
- 下一步行动

### 可视化追踪
```bash
python .claude/harness/test_helper.py
```

输出:
```
📊 功能完成状态:
==================================================
总计: 54 个功能
已完成: 12 个
完成率: 22.2%

✅ 用户认证模块 (FR-001): 8/8
🔄 首页仪表盘 (FR-002): 3/3
🔄 项目管理 (FR-003): 1/6

📋 下一个待实现功能:
  - PROJ-002: 用户可以编辑项目信息
```

## 🚀 快速开始指南

### 对于 AI Agent (Claude Code)

**每次新会话开始时**:
```bash
# 一键启动
source .claude/harness/quickstart.sh
```

**然后按照提示**:
1. 阅读进度日志
2. 查看功能清单
3. 选择一个功能
4. 开始实现

**会话结束时**:
1. 运行所有检查
2. 更新功能清单
3. 提交代码
4. 更新进度日志

### 对于人类开发者

**启动开发环境**:
```bash
source .claude/harness/init.sh
```

**查看进度**:
```bash
python .claude/harness/test_helper.py
```

**手动实现功能**:
- 参考 `session_checklist.md`
- 遵循 TDD 开发流程
- 使用 E2E 测试验证

## 🎓 最佳实践

### ✅ 推荐做法
1. **一次一个功能**: 每次会话只实现一个功能
2. **测试先行**: TDD 开发流程 (红 → 绿 → 重构)
3. **端到端验证**: 必须通过 Playwright 测试
4. **清晰提交**: 使用 Conventional Commits 格式
5. **记录进展**: 每次会话都更新日志

### ❌ 避免做法
1. **一次多个功能**: 贪多嚼不烂
2. **跳过测试**: 未测试的代码不能提交
3. **修改测试**: 不能修改测试来适应代码
4. **硬编码配置**: 所有配置通过环境变量
5. **留下半成品**: 会话结束必须代码干净

## 🔧 技术栈

### 后端
- **框架**: FastAPI (Python 3.12+)
- **ORM**: SQLAlchemy 2.0 (Mapped + DeclarativeBase)
- **数据库**: PostgreSQL 15+ (asyncpg)
- **认证**: JWT + OAuth
- **测试**: pytest + pytest-asyncio

### 前端
- **框架**: React 18 + TypeScript 5.0
- **构建**: Vite
- **UI**: TailwindCSS v4 + shadcn/ui
- **测试**: Playwright

### 基础设施
- **容器**: Docker + Docker Compose
- **数据库**: PostgreSQL (Docker)
- **存储**: MinIO (Docker)
- **缓存**: Redis (Docker)

### 工具链
- **代码检查**: ruff (Python) + ESLint (TypeScript)
- **类型检查**: pyright (Python) + TypeScript (JS)
- **包管理**: uv (Python) + npm (Node.js)
- **版本控制**: Git

## 📚 参考资料

1. **Anthropic 的研究论文**: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
2. **Conventional Commits**: [https://www.conventionalcommits.org/](https://www.conventionalcommits.org/)
3. **Keep a Changelog**: [https://keepachangelog.com/](https://keepachangelog.com/)
4. **Playwright 文档**: [https://playwright.dev/](https://playwright.dev/)
5. **FastAPI 文档**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)

## 🎯 预期成果

### Initializer Agent 完成后
- ✅ 完整的项目结构
- ✅ 可运行的开发环境
- ✅ 54 个功能的详细清单
- ✅ 完善的开发文档
- ✅ 自动化测试框架

### Coding Agent 多次会话后
- ✅ 所有 54 个功能实现完成
- ✅ 代码覆盖率达到 80%+
- ✅ 所有 E2E 测试通过
- ✅ 代码符合规范要求
- ✅ 完整的 commit 历史

### 项目质量
- ✅ 生产级代码质量
- ✅ 完整的测试覆盖
- ✅ 清晰的文档
- ✅ 可维护的架构
- ✅ 可追溯的开发历史

## 🔮 未来改进

### 短期 (1-2 周)
- [ ] 添加 CI/CD 集成
- [ ] 实现自动化测试报告
- [ ] 添加性能测试
- [ ] 实现自动化部署

### 中期 (1-2 月)
- [ ] 多 Agent 架构 (测试 Agent、QA Agent、重构 Agent)
- [ ] 自动化代码审查
- [ ] 智能功能推荐
- [ ] 自动化文档生成

### 长期 (3-6 月)
- [ ] 自适应优先级调整
- [ ] 跨项目知识迁移
- [ ] 多模态测试 (视觉、音频)
- [ ] AI 辅助重构

## 📝 总结

这个无人值守 AI 开发流程是基于 Anthropic 最新研究成果的实战应用,通过以下核心机制实现了长时间运行的 AI 开发:

1. **两阶段 Agent 设计**: Initializer + Coding
2. **详细的功能清单**: 54 个功能,每个都有测试步骤
3. **清晰的进度追踪**: 进度日志 + Git 历史
4. **严格的质量保证**: 健康检查 + 代码检查 + E2E 测试
5. **完整的工作流程**: 从启动到提交的标准化流程

这个流程不仅适用于 Sisyphus-X-Pro 项目,也可以适配到其他类似的全栈开发项目,是一个可复用的 AI 开发框架。

---

**作者**: poco
**创建日期**: 2026-02-13
**版本**: 1.0.0
**基于**: Anthropic Engineering Blog - "Effective harnesses for long-running agents"
