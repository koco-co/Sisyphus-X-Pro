# Coding Agent 会话检查清单

每次会话开始和结束时使用此清单确保工作质量。

## 会话开始清单 ✅

- [ ] 运行 `pwd` 确认工作目录
- [ ] 运行 `source .claude/harness/init.sh` 启动开发环境
- [ ] 运行 `python .claude/harness/health_check.py` 验证服务正常
- [ ] 阅读 `cat .claude/harness/claude-progress.txt` 了解项目进展
- [ ] 阅读 `cat .claude/harness/feature_list.json` 查看待完成功能
- [ ] 运行 `git log --oneline -20` 查看最近的提交
- [ ] 运行 `git status` 查看当前分支状态
- [ ] 选择**一个**高优先级的待实现功能

## 功能实现清单 ✅

### 规划阶段
- [ ] 理解功能的完整需求
- [ ] 列出需要创建的文件
- [ ] 列出需要修改的文件
- [ ] 列出需要添加的依赖
- [ ] 制定测试计划

### TDD 开发阶段
- [ ] 编写单元测试 (pytest)
- [ ] 运行测试确认失败 (RED)
- [ ] 实现代码逻辑
- [ ] 运行测试确认通过 (GREEN)
- [ ] 代码重构优化 (IMPROVE)
- [ ] 验证测试覆盖率 ≥ 80%

### 端到端测试阶段
- [ ] 编写 Playwright E2E 测试
- [ ] 在浏览器中手动验证功能
- [ ] 验证所有测试步骤通过
- [ ] 截图保存测试证据 (可选)

### 代码质量检查
- [ ] 运行 `ruff check backend/ --fix` (后端代码风格)
- [ ] 运行 `pyright backend/` (后端类型检查)
- [ ] 运行 `npm run lint` (前端代码检查)
- [ ] 运行 `npm run type-check` (前端类型检查,如有配置)
- [ ] 所有检查通过

## 会话结束清单 ✅

- [ ] 功能完整实现且测试通过
- [ ] 更新 `feature_list.json` 中功能的 `passes` 字段为 `true`
- [ ] 运行 `git status` 和 `git diff` 查看所有变更
- [ ] 运行 `git add .` 暂存所有变更
- [ ] 创建 git commit (使用 Conventional Commits 格式)
- [ ] 推送到远程 `git push origin main`
- [ ] 更新 `claude-progress.txt` 添加本次会话记录
- [ ] 验证应用正常运行 (无破坏性变更)
- [ ] 运行 `python .claude/harness/health_check.py` 最后验证
- [ ] 确认代码库处于可提交状态

## 禁止事项 ❌

- [ ] 一次实现多个功能
- [ ] 跳过测试标记功能为完成
- [ ] 修改 `feature_list.json` 中的功能描述
- [ ] 留下半成品代码
- [ ] 引入破坏性变更
- [ ] 硬编码配置信息
- [ ] 提交不符合规范的代码

## 紧急情况处理

### 如果测试失败
1. 分析失败原因
2. 修复代码
3. 重新运行测试
4. **不要修改测试来通过代码**

### 如果环境问题
1. 重新运行 `init.sh`
2. 检查 Docker 服务
3. 查看日志文件 `logs/*.log`
4. 必要时重启服务

### 如果无法完成功能
1. 在 `claude-progress.txt` 中记录问题
2. 创建 git commit 保存当前进度
3. 详细说明阻碍因素
4. 为下次会话留下清晰上下文

## Git 提交模板

```bash
git commit -m "$(cat <<'EOF'
<type>: <简短描述>

详细说明本次实现的功能和变更点。

## 实现内容
- 创建了 XXX 模型/组件
- 实现了 XXX API/功能
- 添加了 XXX 测试

## 测试结果
- 单元测试: ✅ 全部通过 (X/Y)
- E2E 测试: ✅ 全部通过 (X/Y)
- 代码覆盖率: XX%

## 变更文件
- backend/app/models/xxx.py
- backend/app/routers/xxx.py
- frontend/src/pages/xxx.tsx

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

## 提交类型

- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 代码重构
- `test`: 添加或修改测试
- `docs`: 文档更新
- `chore`: 构建/工具配置

---

**记住**: 你的目标是保持代码库的干净和可工作状态,为下一个 Coding Agent 铺平道路。
