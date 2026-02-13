# /autonomous - 无人值守全流程开发模式

**启动无人值守AI开发流程**,从需求到交付的完整自动化。

## 使用方法

```bash
# 方式1: 通过斜杠命令 (推荐)
/autonomous

# 方式2: 直接描述需求
我想实现XXX功能,请使用无人值守模式完成
```

## 工作流程

### 第一阶段: 需求与设计 (Product + Architect)
```
用户需求 → Product Agent (需求转化) → 完整PRD文档
                                    ↓
                          Architect Agent (架构设计)
                                    ↓
    ┌───────────────────────────────────────────────────┐
    │  • 接口定义文档 (temp/02_接口定义.md)              │
    │  • 数据库设计文档 (temp/03_数据库设计.md)          │
    │  • 任务清单 (temp/04_任务清单.md)                  │
    │  • CLAUDE.md 更新 (项目级指引)                      │
    └───────────────────────────────────────────────────┘
```

### 第二阶段: 开发实施 (Backend + Frontend)
```
任务清单 → Backend Agent (后端开发 + 单元测试)
                    ↓ 前后端并行
         Frontend Agent (前端开发 + 组件测试)
                    ↓
    ┌───────────────────────────────────────┐
    │  代码质量检查 (ruff/pyright/ESLint)   │
    │  单元测试覆盖率 >= 80%                │
    │  Git Commit (draft状态)               │
    └───────────────────────────────────────┘
```

### 第三阶段: 质量验证 (E2E + Doc)
```
开发完成 → E2E Agent (端到端测试) ← 质量门禁
                  ↓ 如果通过
         Doc Agent (文档同步更新)
                  ↓
    ┌───────────────────────────────────────┐
    │  • 更新 README.md                     │
    │  • 更新 CLAUDE.md                     │
    │  • 更新 CHANGELOG.md                  │
    │  • 更新 feature_list.json             │
    └───────────────────────────────────────┘
```

### 第四阶段: 交付确认 (QA + Lead)
```
文档更新 → QA Agent (最终验收)
                  ↓ 通过
         Team Lead (交付确认)
                  ↓
    ┌───────────────────────────────────────┐
    │  • Git Commit (final状态)             │
    │  • Git Push                          │
    │  • 更新 claude-progress.txt           │
    │  • 生成交付报告                       │
    │  • 触发 Ralph Loop (可选)            │
    └───────────────────────────────────────┘
```

## 核心机制

### 1. 严格的依赖链管理
- **Product Agent** 必须先完成 → Architect Agent才能开始
- **Architect Agent** 必须先完成 → Backend/Frontend Agent才能开始
- **Backend + Frontend** 必须都完成 → E2E Agent才能开始
- **E2E Agent** 必须先通过 → Doc Agent才能开始
- **Doc Agent** 必须先完成 → QA Agent才能开始
- **QA Agent** 必须先通过 → Team Lead才能交付

### 2. 强制质量门禁
- ❌ E2E测试不通过 → **不能**进入下一阶段
- ❌ 代码覆盖率 < 80% → **不能**进入下一阶段
- ❌ 代码检查不通过 → **不能**进入下一阶段
- ❌ 文档未同步更新 → **不能**标记完成

### 3. 增量进度保存
每个Agent完成工作后:
1. 创建Git Commit (允许wip/draft前缀)
2. 更新 `.claude/harness/claude-progress.txt`
3. 更新任务状态
4. 记录当前上下文状态

### 4. 自动生命周期管理
- Agent完成工作后自动申请关闭
- Team Lead自动检查任务完成度
- 如果任务未完成,拒绝关闭请求
- 如果任务完成,批准关闭并清理资源

### 5. Ralph Loop 集成
当上下文过长时:
1. 自动触发Ralph Loop
2. 保存当前会话状态
3. 清空上下文
4. 从进度文件恢复状态
5. 继续下一批任务

## Agent角色定义

### Team Lead (orchestrator)
**职责**: 协调所有Agent,管理依赖链,最终交付确认
**工具**: TaskCreate, TaskUpdate, SendMessage, TeamCreate
**约束**: 不直接修改代码,只负责协调

### Product Agent
**职责**: 将碎片化需求转化为完整可交付的PRD文档
**输入**: 用户原始需求
**输出**: `temp/01_需求文档.md`
**技能**: tech-doc-enhancer

### Architect Agent
**职责**: 产出接口定义、数据库设计、架构设计
**输入**: PRD文档
**输出**:
- `temp/02_接口定义.md`
- `temp/03_数据库设计.md`
- `temp/04_任务清单.md`
- 更新 `CLAUDE.md`
**技能**: everything-claude-code:architect

### Backend Agent
**职责**: 后端开发 + 单元测试
**输入**: 任务清单中的后端任务
**输出**:
- 后端代码实现
- 单元测试 (覆盖率 >= 80%)
- API文档更新
**技能**: everything-claude-code:tdd-guide, everything-claude-code:python-reviewer

### Frontend Agent
**职责**: 前端开发 + 组件测试
**输入**: 任务清单中的前端任务
**输出**:
- 前端代码实现
- 组件测试
- UI交互测试
**技能**: everything-claude-code:tdd-guide, frontend-design:frontend-design

### E2E Agent
**职责**: 端到端测试 (质量门禁)
**输入**: 完整的功能代码
**输出**:
- Playwright E2E测试
- 测试报告
- 截图/视频证据
**技能**: everything-claude-code:e2e-runner
**约束**: 只有E2E测试全部通过才能标记任务完成

### Doc Agent
**职责**: 文档同步更新
**输入**: 代码变更记录
**输出**:
- 更新 README.md
- 更新 CLAUDE.md
- 更新 CHANGELOG.md
- 更新 feature_list.json
**技能**: everything-claude-code:doc-updater

### QA Agent
**职责**: 最终验收测试
**输入**: 完整的功能 + 文档
**输出**:
- 验收测试报告
- Bug清单 (如果有)
- 交付确认
**技能**: feature-dev:code-reviewer

## 质量标准

### 代码质量
- [ ] 后端: ruff check --fix 通过
- [ ] 后端: pyright 通过
- [ ] 前端: npm run lint 通过
- [ ] 前端: tsc -b 通过

### 测试覆盖率
- [ ] 单元测试覆盖率 >= 80%
- [ ] E2E测试覆盖核心用户流程
- [ ] 所有测试用例通过

### 文档完整性
- [ ] README.md 已更新
- [ ] CLAUDE.md 已更新
- [ ] CHANGELOG.md 已更新
- [ ] API文档已更新 (如有接口变更)

### Git提交规范
- [ ] Commit message遵循 Conventional Commits
- [ ] 包含详细的commit body
- [ ] 包含测试结果说明
- [ ] 代码库处于可提交状态

## 自动关闭机制

每个Agent完成工作后,自动执行以下流程:

```python
# 伪代码
async def agent_complete_work(agent):
    # 1. 检查任务完成度
    completion_rate = check_task_completion(agent.tasks)

    if completion_rate < 100:
        # 任务未完成,不能关闭
        await agent.send_message_to_lead(
            f"任务未完成 ({completion_rate}%),继续工作"
        )
        return False

    # 2. 运行质量检查
    quality_checks = run_quality_checks(agent.work)

    if not quality_checks.all_passed:
        # 质量检查未通过,不能关闭
        await agent.send_message_to_lead(
            f"质量检查未通过: {quality_checks.failures}"
        )
        return False

    # 3. 创建Git Commit
    await agent.create_git_commit()

    # 4. 更新进度文件
    await agent.update_progress_file()

    # 5. 向Team Lead申请关闭
    await agent.send_shutdown_request(
        reason="所有任务完成,质量检查通过"
    )

    return True
```

## Ralph Loop 集成

当上下文达到阈值时,自动触发Ralph Loop:

```python
# 伪代码
async def check_context_and_ralph_loop():
    context_usage = get_context_usage()

    if context_usage > CONTEXT_THRESHOLD:
        # 1. 保存当前会话状态
        state = {
            "current_phase": current_phase,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "agent_status": agent_status,
        }
        save_state_to_file(state)

        # 2. 触发Ralph Loop
        await trigger_ralph_loop(
            next_action="continue_from_state",
            state_file="current_session_state.json"
        )

        # 3. Ralph Loop会:
        #    - 清空上下文
        #    - 从状态文件恢复
        #    - 继续下一批任务
```

## 使用示例

### 示例1: 实现一个新功能
```
用户: /autonomous

系统: 请描述您要实现的功能:

用户: 我想要实现用户可以重置密码的功能

系统: [启动无人值守模式]
       [Phase 1] Product Agent 正在工作...
       [Phase 1] Architect Agent 正在工作...
       [Phase 2] Backend Agent 正在工作...
       [Phase 2] Frontend Agent 正在工作...
       [Phase 3] E2E Agent 正在进行质量验证...
       [Phase 3] Doc Agent 正在更新文档...
       [Phase 4] QA Agent 正在进行最终验收...
       [完成] 功能已交付,查看报告:
       - Git Commit: abc1234
       - 测试报告: reports/e2e/password-reset.html
       - 交付报告: reports/delivery/2025-02-13.md
```

### 示例2: 批量实现功能
```
用户: /autonomous
       请实现feature_list.json中所有未完成的功能

系统: [批量模式]
       检测到 10 个未完成功能
       预计需要 3-5 个会话周期

       [Cycle 1]
       - AUTH-001: 用户注册功能 ✅
       - AUTH-002: 用户登录功能 ✅

       [Ralph Loop 触发] 保存状态,重启会话...

       [Cycle 2]
       - AUTH-003: GitHub OAuth ✅
       - AUTH-004: Google OAuth ✅
       ...

       [最终报告]
       完成功能: 10/10
       测试覆盖率: 87%
       E2E测试: 全部通过
       代码质量: 全部检查通过
```

## 配置选项

在 `.claude/settings.json` 中添加:

```json
{
  "autonomous": {
    "enabled": true,
    "context_threshold": 0.8,
    "e2e_required": true,
    "coverage_threshold": 80,
    "auto_commit": true,
    "auto_push": false,
    "ralph_loop_enabled": true,
    "quality_gates": {
      "lint": true,
      "type_check": true,
      "unit_tests": true,
      "e2e_tests": true,
      "doc_update": true
    },
    "agent_timeout": 3600,
    "max_retries": 3
  }
}
```

## 故障处理

### Agent工作超时
- 自动终止超时Agent
- 保存当前进度
- 重新启动Agent继续工作

### 质量门禁失败
- 阻止进入下一阶段
- 返回上一阶段Agent修复
- 最多重试3次

### 上下文耗尽
- 触发Ralph Loop
- 保存状态到文件
- 重启会话并恢复

### Git冲突
- 自动暂停
- 通知用户解决
- 解决后继续

## 监控与日志

所有Agent的工作都会记录在:
- `.claude/harness/claude-progress.txt` - 进度日志
- `.claude/harness/agent_logs/` - Agent详细日志
- `.claude/harness/reports/` - 测试报告和交付报告

## 注意事项

1. **首次使用前**,确保已安装所有依赖和工具
2. **确保环境干净**,无未提交的更改
3. **首次运行会自动初始化** Agent Teams
4. **可以随时中断**,使用 Ctrl+C,当前进度会保存
5. **支持断点续传**,下次运行会从上次进度继续

## 高级功能

### 自定义Agent配置
可以在项目级覆盖Agent行为:

```markdown
<!-- .claude/agents/backend.md -->
# Backend Agent 自定义配置

## 覆盖的技能
- 使用项目的 backend-patterns skill
- 使用项目的 python-testing skill

## 额外的约束
- 所有API必须包含错误处理
- 所有数据库操作必须使用异步
- 所有外部调用必须包含超时设置

## 测试要求
- 每个函数至少有2个测试用例
- 边界条件必须测试
- 异常情况必须测试
```

### 自定义质量门禁
可以在项目级添加额外的检查:

```markdown
<!-- .claude/quality_gates.md -->
# 自定义质量门禁

## 后端额外检查
- [ ] 安全审查通过 (使用 security-reviewer)
- [ ] 性能测试通过 (响应时间 < 200ms)
- [ ] 数据库查询优化通过 (无N+1查询)

## 前端额外检查
- [ ] 可访问性检查通过 (WCAG 2.1 AA)
- [ ] SEO检查通过 (Lighthouse Score > 90)
- [ ] 性能检查通过 (FCP < 1.8s)
```

---

**相关文档**:
- [HARNESS_GUIDE.md](../../HARNESS_GUIDE.md) - 快速开始指南
- [.claude/harness/README.md](README.md) - 完整系统文档
- [Agent Teams 官方文档](https://code.claude.com/docs/en/agent-teams)
