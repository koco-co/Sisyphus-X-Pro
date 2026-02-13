# 无人值守开发模式 - 完整指南

基于Anthropic的 **"Effective harnesses for long-running agents"** 研究成果,结合Claude Code的Agent Teams功能,打造的全自动无人值守开发流程。

## 📋 目录

- [核心原理](#核心原理)
- [快速开始](#快速开始)
- [工作流程](#工作流程)
- [Agent角色](#agent角色)
- [质量门禁](#质量门禁)
- [Ralph Loop](#ralph-loop)
- [配置选项](#配置选项)
- [故障处理](#故障处理)
- [最佳实践](#最佳实践)

## 核心原理

### 为什么需要无人值守模式?

传统AI Agent开发模式存在以下问题:

1. **测试敷衍** - Agent倾向于跳过或简化测试
2. **协调混乱** - 多Agent工作顺序混乱,依赖未明确
3. **文档落后** - 代码变更后文档不更新
4. **资源泄漏** - 完成的Agent不主动关闭
5. **上下文耗尽** - 长时间工作后上下文不足,只完成部分任务

### 解决方案

本方案通过以下机制解决上述问题:

| 问题 | 解决方案 |
|------|---------|
| 测试敷衍 | **强制E2E测试门禁** - 只有E2E测试全部通过才能进入下一阶段 |
| 协调混乱 | **严格依赖链管理** - Team Lead协调,每个阶段依赖前一阶段完成 |
| 文档落后 | **文档同步门禁** - 文档未更新不能标记完成 |
| 资源泄漏 | **自动生命周期管理** - Agent完成任务后自动申请关闭 |
| 上下文耗尽 | **Ralph Loop集成** - 自动保存状态,重启会话恢复工作 |

## 快速开始

### 前置条件

1. **启用Agent Teams**
```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

2. **安装依赖**
```bash
# 后端
cd backend
pip install ruff pyright pytest

# 前端
cd frontend
npm install

# E2E测试
npx playwright install
```

3. **初始化项目**
```bash
# 复制配置文件
cp .claude/harness/autonomous_config.json.example .claude/harness/autonomous_config.json

# 编辑配置 (可选)
vim .claude/harness/autonomous_config.json
```

### 启动无人值守模式

```bash
# 方式1: 使用斜杠命令 (推荐)
/autonomous

# 系统会提示您描述需求

# 方式2: 直接描述需求
我想实现用户可以重置密码的功能,请使用无人值守模式完成
```

### 恢复中断的会话

```bash
# Ralph Loop自动触发后,运行
/autonomous-resume

# 或手动运行重启脚本
source .claude/harness/ralph_loop_restart.sh
```

## 工作流程

### 完整流程图

```
用户需求
   ↓
[Phase 1] Product Agent (需求转化)
   ├─ 输出: temp/01_需求文档.md
   └─ 验证: 文档结构完整
   ↓
[Phase 2] Architect Agent (架构设计)
   ├─ 输出: temp/02_接口定义.md
   │        temp/03_数据库设计.md
   │        temp/04_任务清单.md
   │        CLAUDE.md (更新)
   └─ 验证: 设计可执行
   ↓
[Phase 3] Backend + Frontend Agent (开发实施) [并行]
   ├─ Backend: backend/app/ + backend/tests/
   └─ Frontend: frontend/src/ + 组件测试
   └─ 验证: 代码质量 + 单元测试 (覆盖率 >= 80%)
   ↓
[Phase 4] E2E Agent (端到端测试) ← 质量门禁 🔒
   ├─ 输出: frontend/e2e/ + reports/e2e/
   └─ 验证: **所有E2E测试通过** (强制)
   ↓ 如果失败 → 返回Phase 3修复
[Phase 5] Doc Agent (文档同步更新)
   ├─ 输出: README.md + CLAUDE.md + CHANGELOG.md + feature_list.json
   └─ 验证: 所有文档已同步更新
   ↓
[Phase 6] QA Agent (最终验收)
   ├─ 输出: reports/qa/YYYY-MM-DD.md
   └─ 验证: 功能 + 代码 + 文档 + 安全
   ↓ 如果失败 → 返回对应阶段修复
[Phase 7] Team Lead (交付确认)
   ├─ Git Commit (final)
   ├─ Git Push
   ├─ claude-progress.txt (更新)
   └─ 交付报告
```

### 批量模式

当需要实现多个功能时,自动触发Ralph Loop:

```
[Cycle 1]
├─ AUTH-001: 用户注册功能 ✅
├─ AUTH-002: 用户登录功能 ✅
└─ 触发 Ralph Loop (上下文: 85%)

↓ 自动保存状态并重启会话

[Cycle 2]
├─ AUTH-003: GitHub OAuth ✅
├─ AUTH-004: Google OAuth ✅
└─ 触发 Ralph Loop

↓ 继续直到所有功能完成
```

## Agent角色

### Team Lead (orchestrator)

**职责**: 协调所有Agent,管理依赖链,最终交付确认

**关键能力**:
- 创建和管理Agent Team
- 分配任务和设置依赖
- 验证每个阶段的完成度
- 处理Agent的关闭请求
- 触发Ralph Loop

**约束**: 不直接修改代码,只负责协调

### Product Agent

**职责**: 将碎片化需求转化为完整PRD文档

**输入**: 用户原始需求

**输出**: `temp/01_需求文档.md`

**技能**: tech-doc-enhancer

**验收标准**:
- 文档结构完整
- 功能描述清晰
- 用户场景明确

### Architect Agent

**职责**: 产出接口定义、数据库设计、任务清单

**输入**: PRD文档

**输出**:
- `temp/02_接口定义.md`
- `temp/03_数据库设计.md`
- `temp/04_任务清单.md`
- `CLAUDE.md` (更新)

**技能**: everything-claude-code:architect

**验收标准**:
- 接口定义完整
- 数据库设计合理
- 任务清单可执行
- CLAUDE.md已同步更新

### Backend Agent

**职责**: 后端开发 + 单元测试

**输入**: 任务清单中的后端任务

**输出**:
- `backend/app/` (代码实现)
- `backend/tests/` (单元测试)

**技能**: everything-claude-code:tdd-guide, everything-claude-code:python-reviewer

**验收标准** (强制):
- ✅ ruff check 通过
- ✅ pyright 通过
- ✅ 测试覆盖率 >= 80%
- ✅ 所有单元测试通过

### Frontend Agent

**职责**: 前端开发 + 组件测试

**输入**: 任务清单中的前端任务

**输出**:
- `frontend/src/` (代码实现)
- `frontend/src/components/__tests__/` (组件测试)

**技能**: everything-claude-code:tdd-guide, frontend-design:frontend-design

**验收标准** (强制):
- ✅ npm run lint 通过
- ✅ tsc -b 通过
- ✅ 组件测试通过

### E2E Agent (质量门禁)

**职责**: 端到端测试验证

**输入**: 完整的功能代码

**输出**:
- `frontend/e2e/` (E2E测试)
- `reports/e2e/` (测试报告 + 截图 + 视频)

**技能**: everything-claude-code:e2e-runner

**验收标准** (强制 - 最关键):
- ✅ **所有E2E测试用例通过**
- ✅ 截图证据完整
- ✅ 测试报告生成

**重要**: 如果有任何测试失败,**不能**进入下一阶段,必须返回开发阶段修复

### Doc Agent

**职责**: 文档同步更新

**输入**: 代码变更记录

**输出**:
- `README.md` (更新)
- `CLAUDE.md` (更新)
- `CHANGELOG.md` (更新)
- `feature_list.json` (更新passes字段)

**技能**: everything-claude-code:doc-updater

**验收标准** (强制):
- ✅ README.md 已更新
- ✅ CLAUDE.md 已更新
- ✅ CHANGELOG.md 已更新
- ✅ feature_list.json 已更新

### QA Agent

**职责**: 最终验收测试

**输入**: 完整的功能 + 文档

**输出**:
- `reports/qa/YYYY-MM-DD.md` (验收报告)
- `bug_list.md` (如果有Bug)

**技能**: feature-dev:code-reviewer, everything-claude-code:security-reviewer

**验收标准** (强制):
- ✅ 功能完整性验证通过
- ✅ 代码质量检查通过
- ✅ 文档完整性验证通过
- ✅ 安全性检查通过

## 质量门禁

### E2E测试门禁 (最关键)

```python
def check_e2e_gate():
    test_results = run_e2e_tests()

    if test_results.failed > 0:
        # 🔒 阻止继续
        block_progression(
            reason=f"E2E测试失败: {test_results.failed}个用例失败",
            action="返回开发阶段修复",
            assign_to="backend-agent或frontend-agent"
        )
        return False

    # ✅ 放行
    return True
```

### 代码覆盖率门禁

```python
def check_coverage_gate():
    backend_coverage = get_coverage("backend")

    if backend_coverage < 80:
        block_progression(
            reason=f"覆盖率不足: {backend_coverage}% < 80%",
            action="补充测试用例",
            assign_to="backend-agent"
        )
        return False

    return True
```

### 代码质量门禁

```python
def check_code_quality_gate():
    checks = {
        "backend": {
            "ruff": run_command("ruff check backend/"),
            "pyright": run_command("pyright backend/")
        },
        "frontend": {
            "eslint": run_command("npm run lint"),
            "tsc": run_command("tsc -b")
        }
    }

    failed = [name for name, result in checks.items() if not result.passed]

    if failed:
        block_progression(
            reason=f"代码检查失败: {', '.join(failed)}",
            action="修复代码质量问题",
            assign_to="对应agent"
        )
        return False

    return True
```

### 文档同步门禁

```python
def check_doc_sync_gate():
    changed_files = git_diff()
    doc_files = ["README.md", "CLAUDE.md", "CHANGELOG.md"]
    updated_docs = [f for f in doc_files if f in changed_files]

    if len(updated_docs) < len(doc_files):
        block_progression(
            reason=f"文档未同步更新: 缺少 {set(doc_files) - set(updated_docs)}",
            action="更新文档",
            assign_to="doc-agent"
        )
        return False

    return True
```

## Ralph Loop

### 原理

当上下文使用率达到阈值 (默认85%) 时:
1. 自动保存完整会话状态
2. 创建重启脚本
3. 显示恢复指南
4. 下次会话从状态文件恢复

### 状态保存

```python
state = {
    "session_id": "session-20250213-143022",
    "timestamp": "2025-02-13T14:30:22",
    "current_phase": "development",
    "completed_tasks": ["task-1", "task-2"],
    "pending_tasks": [...],
    "agent_status": {...}
}

save_to_file(".claude/harness/ralph_loop_state.json", state)
```

### 状态恢复

```bash
# 方式1: 使用命令
/autonomous-resume

# 方式2: 运行重启脚本
source .claude/harness/ralph_loop_restart.sh

# 方式3: 手动加载
请恢复会话状态,文件: .claude/harness/ralph_loop_state.json
```

### 批量任务模式

```
[检测到] 10个未完成功能
[预计] 需要3-5个会话周期

[Cycle 1] - 完成2个功能
↓ Ralph Loop触发

[Cycle 2] - 完成3个功能
↓ Ralph Loop触发

[Cycle 3] - 完成3个功能
↓ Ralph Loop触发

[Cycle 4] - 完成2个功能
↓ 全部完成,交付!
```

## 配置选项

### 全局配置

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "teammateMode": "auto",
  "autonomous": {
    "enabled": true,
    "context_threshold": 0.85,
    "e2e_required": true,
    "coverage_threshold": 80,
    "auto_commit": true,
    "auto_push": false,
    "ralph_loop_enabled": true,
    "max_retries": 3
  }
}
```

### 项目级配置

```json
// .claude/harness/autonomous_config.json
{
  "quality_gates": {
    "backend": {
      "min_coverage": 80
    },
    "e2e": {
      "blocking": true,
      "screenshots": true,
      "videos": true
    }
  },
  "agents": {
    "backend": {
      "timeout": 7200
    }
  }
}
```

## 故障处理

### Agent工作超时

```
1. 检测超时
2. 保存当前进度
3. 终止Agent
4. 重新启动Agent
5. 恢复任务
```

### 质量门禁失败

```
1. 阻止下一阶段
2. 分析失败原因
3. 决定返回哪个阶段
4. 分配给对应Agent修复
5. 最多重试3次
```

### 上下文耗尽

```
1. 触发Ralph Loop
2. 保存状态到文件
3. 创建重启脚本
4. 显示恢复指南
```

### Git冲突

```
1. 自动暂停
2. 通知用户解决
3. 解决后继续
```

## 最佳实践

### 1. 确保环境干净

```bash
# 启动前检查
git status  # 应该是干净的
docker-compose ps  # 所有服务运行
```

### 2. 明确需求描述

```
❌ 不好的描述: "优化登录功能"
✅ 好的描述: "实现用户可以通过GitHub OAuth登录,
           重定向到GitHub授权页面,授权后自动创建账户
           并跳转到首页,显示GitHub用户信息"
```

### 3. 合理拆分任务

```
❌ 一次性实现整个模块
✅ 拆分成多个小功能,逐个实现
```

### 4. 监控进度

```bash
# 查看实时进度
tail -f .claude/harness/claude-progress.txt

# 查看Agent状态
cat ~/.claude/teams/autonomous-development/config.json
```

### 5. 定期检查

```
建议每完成一个阶段后:
1. 检查代码质量
2. 运行测试
3. 查看文档
4. 确认进度
```

## 监控与日志

### 进度日志

```
.claude/harness/claude-progress.txt
```

### Agent日志

```
.claude/harness/agent_logs/
├── product-agent.log
├── architect-agent.log
├── backend-agent.log
├── frontend-agent.log
├── e2e-agent.log
├── doc-agent.log
└── qa-agent.log
```

### 测试报告

```
reports/
├── e2e/
│   ├── 2025-02-13.html
│   ├── screenshots/
│   └── videos/
├── qa/
│   └── 2025-02-13.md
└── delivery/
    └── 2025-02-13.md
```

## 相关文档

- [HARNESS_GUIDE.md](../../HARNESS_GUIDE.md) - 快速开始指南
- [.claude/harness/README.md](README.md) - 完整系统文档
- [.claude/harness/coding_agent_prompt.md](coding_agent_prompt.md) - Coding Agent指南
- [autonomous.md](../commands/autonomous.md) - 无人值守模式命令
- [Agent Teams 官方文档](https://code.claude.com/docs/en/agent-teams)
- [Anthropic研究论文](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

## 常见问题

### Q: 如何确认无人值守模式正在运行?

A: 查看Agent Team状态:
```bash
cat ~/.claude/teams/autonomous-development/config.json
```

### Q: Ralph Loop会丢失进度吗?

A: 不会。Ralph Loop会保存完整状态,包括任务列表、Agent状态、Git状态等。

### Q: 如何停止无人值守模式?

A: 按 Ctrl+C,当前进度会保存,下次可以继续。

### Q: 可以修改质量标准吗?

A: 可以。编辑 `.claude/harness/autonomous_config.json` 中的 `quality_gates` 部分。

### Q: E2E测试失败会怎样?

A: 质量门禁会阻止进入下一阶段,必须修复失败后重新测试。

### Q: 支持自定义Agent吗?

A: 支持。在 `.claude/agents/` 目录下创建自定义Agent的prompt文件。

## 贡献

欢迎反馈问题和改进建议!
